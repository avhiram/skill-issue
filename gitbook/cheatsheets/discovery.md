# Active Directory — Énumération LDAP

## Objectif

Inventorier les objets du domaine Active Directory, comprendre leur rôle et préparer une cartographie des relations d'administration.

## Référence des filtres LDAP

| Objet | Filtre LDAP |
| --- | --- |
| Comptes utilisateurs | `(samAccountType=805306368)` |
| Comptes ordinateurs | `(samAccountType=805306369)` |
| Groupes | `(samAccountType=268435456)` |
| Domaines | `(objectClass=domain)` |
| Unités d'organisation | `(objectClass=organizationalUnit)` |
| Stratégies de groupe | `(objectClass=groupPolicyContainer)` |
| Relations d'approbation | `(objectClass=trustedDomain)` |
| Filtres WMI | `(objectClass=msWMI-Som)` |

> Un compte ordinateur possède également la classe LDAP `user`. Utiliser `samAccountType` pour distinguer correctement les types de comptes.

## Commandes d'inventaire

### Identifier le domaine et le contrôleur de domaine

```powershell
Get-ADDomain
Get-ADDomainController -Discover
```

Ces commandes nécessitent le module **ActiveDirectory** et les autorisations appropriées.

### Lister les ordinateurs du domaine

```powershell
Get-ADComputer -Filter * -Properties DNSHostName,OperatingSystem |
  Select-Object Name,DNSHostName,OperatingSystem
```

### Lister les utilisateurs et leurs groupes

```powershell
Get-ADUser -Filter * -Properties MemberOf |
  Select-Object SamAccountName,MemberOf
```

### Lister les GPO

```powershell
Get-GPO -All | Select-Object DisplayName,Id,GpoStatus
```

### Inventorier les relations d'approbation

```powershell
Get-ADTrust -Filter * | Select-Object Name,Direction,TrustType
```

## Analyse et journalisation

Limiter les attributs demandés, respecter les règles de l'environnement et éviter les requêtes non bornées sur de très grands annuaires. Les résultats d'inventaire ne suffisent pas à démontrer l'existence d'un chemin d'attaque.

**Source de structuration :** [Discovery — CRTO-Study-Notes](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/cheatsheets/discovery.md). Les commandes PowerShell ci-dessus sont des alternatives d'administration à la méthode BOF présentée dans la source.


## LDAP — Commandes natives de la fiche CRTO

Les commandes ci-dessous reprennent la syntaxe `ldapsearch` du guide source. Elles supposent que le module BOF LDAP est disponible dans le laboratoire autorisé.

### Énumérer les objets du domaine et les GPO

```text
ldapsearch (|(objectClass=domain)(objectClass=organizationalUnit)(objectClass=groupPolicyContainer)) --attributes name,distinguishedName,gPCFileSysPath
```

**Utilité :** identifier les domaines, les unités d'organisation et les chemins SYSVOL des stratégies de groupe.

### Énumérer les comptes utilisateurs

```text
ldapsearch (samAccountType=805306368) --attributes samaccountname,memberof,admincount,description,useraccountcontrol
```

**Utilité :** examiner les comptes, leur appartenance aux groupes et leurs indicateurs d'administration.

### Énumérer les comptes ordinateurs

```text
ldapsearch (samAccountType=805306369) --attributes dnshostname,operatingsystem
```

**Utilité :** inventorier les hôtes et systèmes d'exploitation déclarés dans l'annuaire.

### Énumérer les groupes et leurs membres

```text
ldapsearch (samAccountType=268435456) --attributes samaccountname,member,admincount
```

**Utilité :** identifier les groupes de sécurité et leurs membres.

### Rechercher les comptes protégés

```text
ldapsearch (&(samAccountType=805306368)(adminCount=1)) --attributes samaccountname,memberof
```

**Utilité :** identifier les objets portant l'attribut `adminCount=1`. Cet attribut n'est pas une preuve d'appartenance actuelle à un groupe privilégié.

### Relations de confiance

```text
ldapsearch (objectClass=trustedDomain) --attributes name,trustDirection,trustType
```

**Utilité :** relever les relations d'approbation entre domaines.

### Filtres WMI

```text
ldapsearch (objectClass=msWMI-Som) --attributes msWMI-Name,msWMI-Parm2
```

**Utilité :** vérifier les conditions WMI qui peuvent restreindre l'application des GPO.

## BloodHound CE — Requêtes Cypher

### Afficher les objets GPO

```cypher
MATCH (n:GPO) RETURN n
```

### Examiner les relations d'administration locale

```cypher
MATCH p=(n:User)-[r:AdminTo]->(m:Computer) RETURN p
```

### Examiner les chemins d'accès privilégiés

```cypher
MATCH p=(n)-[:DCSync|AllExtendedRights|GenericAll]->(m:Domain) RETURN p
```

**Lecture :** ces requêtes interrogent des données déjà importées. Leur résultat dépend de la collecte et ne confirme pas à lui seul la possibilité d'exploiter une relation.

## BOFHound — Traitement des journaux

```bash
bofhound -i logs
```

Transforme des journaux de collecte compatibles en fichiers JSON destinés à BloodHound CE. Le dossier `logs` doit contenir des données issues d'un environnement autorisé.

## Filtres LDAP — Opérateurs utiles

| Filtre | Signification |
| --- | --- |
| `(&(...)(...))` | ET logique |
| `(\|(...)(...))` | OU logique |
| `(!(attr=value))` | Négation |
| `(attr=*)` | Attribut présent |
| `1.2.840.113556.1.4.803` | Comparaison bit à bit AND |
| `1.2.840.113556.1.4.1941` | Résolution récursive d'appartenance à des groupes |

**Référence :** [Discovery — notes CRTO originales](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/cheatsheets/discovery.md).

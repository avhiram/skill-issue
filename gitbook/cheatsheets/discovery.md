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

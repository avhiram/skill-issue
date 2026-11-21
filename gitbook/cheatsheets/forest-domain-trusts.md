# Active Directory — Forest & Domain Trusts

> **Périmètre :** inventaire des relations de confiance et des objets d'annuaire. Les procédures de falsification de tickets du dépôt source ne sont pas reproduites ici.

## Typologie

| Relation | Description |
| --- | --- |
| Parent / Child | Confiance hiérarchique au sein d'une même forêt |
| Inbound Trust | Relation entrante du point de vue du domaine examiné |
| Outbound Trust | Relation sortante du point de vue du domaine examiné |
| Inter-Realm Ticket | Ticket Kerberos utilisé entre domaines ou royaumes |

## Trusted Domain Objects (TDO)

### Inventorier les relations de confiance

```text
ldapsearch (objectClass=trustedDomain)
```

### Identifier les comptes de confiance

```text
ldapsearch (samAccountType=805306370) --attributes samAccountName
```

### Examiner le SID du domaine parent

```text
ldapsearch (objectClass=domain) --attributes objectSid --hostname lon-dc-1.contoso.com --dn DC=contoso,DC=com
```

Ces exemples conservent la syntaxe de la fiche source. Les noms d'hôtes et de domaines sont des valeurs de laboratoire.

## Vérifications PowerShell

### Énumérer les relations de confiance

```powershell
Get-ADTrust -Filter * | Select-Object Name,Direction,TrustType,ForestTransitive
```

### Consulter le domaine actuel

```powershell
Get-ADDomain | Select-Object DNSRoot,DomainSID,ParentDomain,ChildDomains
```

### Identifier la forêt

```powershell
Get-ADForest | Select-Object Name,Domains,RootDomain
```

**Source :** [Forest & Domain Trusts — CRTO-Study-Notes](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/cheatsheets/forest-domain-trusts.md).

# AD Enumeration

Inventaire du domaine, des objets, des stratégies de groupe et des relations d'approbation. Les exemples supposent un environnement AD de laboratoire ou administré avec autorisation.

## Modules PowerShell

Les notes distinguent le module ActiveDirectory, PowerView, SharpView et BloodHound. Le module ActiveDirectory est fourni par Microsoft ; PowerView constitue une alternative pour interroger les objets du domaine.

### Domaine actuel

```powershell
Get-ADDomain
```

Affiche les propriétés du domaine courant.

### SID du domaine

```powershell
(Get-ADDomain).DomainSID
```

Affiche l'identifiant de sécurité du domaine.

### Contrôleurs de domaine

```powershell
Get-ADDomainController
```

Identifie un contrôleur de domaine.

## Utilisateurs et ordinateurs

### Utilisateurs

```powershell
Get-ADUser -Filter *
```

Liste les utilisateurs AD.

### Ordinateurs

```powershell
Get-ADComputer -Filter * | Select-Object Name
```

Liste les objets ordinateurs.

### Groupes

```powershell
Get-ADGroup -Filter * | Select-Object Name
```

Affiche les groupes du domaine.

### Appartenances d'un utilisateur

```powershell
Get-ADPrincipalGroupMembership -Identity student1
```

Affiche les groupes associés au compte de laboratoire student1.

## GPO et OU

### Unités organisationnelles

```powershell
Get-ADOrganizationalUnit -Filter * -Properties *
```

Inventorie les OU et leurs propriétés.

Les notes abordent les GPO liées aux ordinateurs et aux OU, ainsi que les appartenances aux groupes locaux définies par les stratégies.

## ACL

Les ACL définissent les droits d'accès aux objets. Les droits GenericAll, GenericWrite, WriteDacl et WriteOwner méritent une revue dans le cadre d'un audit de délégation.

## Trusts et forêts

### Forêt courante

```powershell
Get-ADForest
```

Affiche les propriétés de la forêt.

### Relations d'approbation

```powershell
Get-ADTrust -Filter *
```

Inventorie les relations d'approbation visibles.

### Catalogues globaux

```powershell
Get-ADForest | Select-Object -ExpandProperty GlobalCatalogs
```

Liste les catalogues globaux.

## User Hunting et BloodHound

Le chapitre source traite des sessions utilisateurs, des partages, des relations de groupes et des chemins d'administration. BloodHound représente les relations sous forme de graphe ; les données collectées doivent rester limitées au périmètre autorisé.

## Ressources

- [ADModule](https://github.com/samratashok/ADModule)
- [BloodHound](https://github.com/BloodHoundAD/BloodHound)
- [SharpView](https://github.com/tevora-threat/SharpView/)

---
title: Cheatsheet AD
aside: false
---

# Cheatsheet AD

Ouvre PowerShell sur un poste du domaine équipé du module **ActiveDirectory**. Saisis le nom demandé quand tu exécutes un exemple.

[Périmètre](#perimetre) · [Comptes et groupes](#comptes) · [Postes et stratégies](#postes) · [Droits et approbations](#droits) · [Session Windows](#poste-windows)

## Dans quel domaine suis-je ? {#perimetre}

```powershell
Import-Module ActiveDirectory
(Get-ADDomain).DNSRoot
```

Le résultat est le nom DNS du domaine interrogé, par exemple `formation.example`.

::: details Afficher les domaines de la forêt
Une forêt peut regrouper plusieurs domaines. Affiche leurs noms DNS.

```powershell
(Get-ADForest).Domains
```
:::

::: details Lire les propriétés d’une zone DNS
Avec le module DnsServer, indique le serveur qui héberge la zone et son nom DNS. ZoneType précise son type et IsDsIntegrated indique si elle est intégrée à Active Directory.

```powershell
$serveur = Read-Host "Serveur DNS"
$zone = Read-Host "Nom de la zone"
Get-DnsServerZone -ComputerName $serveur -Name $zone |
    Select-Object ZoneName, ZoneType, IsDsIntegrated, IsReverseLookupZone
```
:::

## Qui fait partie d’un groupe ? {#comptes}

::: details Lire les membres directs
Saisis le nom du groupe. La colonne ObjectClass distingue les utilisateurs, les ordinateurs et les groupes imbriqués.

```powershell
$groupe = Read-Host "Nom du groupe"
Get-ADGroupMember -Identity $groupe | Select-Object Name, ObjectClass
```
:::

::: details Consulter un compte utilisateur
Saisis son identifiant de connexion. Enabled indique si le compte est activé.

```powershell
$compte = Read-Host "Identifiant du compte"
Get-ADUser -Identity $compte | Select-Object Name, SamAccountName, Enabled
```
:::

::: details Lire la description d’un groupe
La description peut préciser le rôle prévu pour ce groupe.

```powershell
$groupe = Read-Host "Nom du groupe"
Get-ADGroup -Identity $groupe -Properties Description | Select-Object Name, Description
```
:::

::: details Identifier un compte de service géré
La classe msDS-GroupManagedServiceAccount identifie un gMSA.

```powershell
$service = Read-Host "Nom du compte de service"
Get-ADServiceAccount -Identity $service | Select-Object Name, ObjectClass, Enabled
```
:::

::: details Inventorier les comptes et les ordinateurs
Afficher les identifiants des utilisateurs du domaine.

```powershell
Get-ADUser -Filter * | Select-Object -ExpandProperty SamAccountName
```

Afficher les noms des ordinateurs enregistrés.

```powershell
Get-ADComputer -Filter * | Select-Object -ExpandProperty Name
```

Lister les comptes de service gérés.

```powershell
Get-ADServiceAccount -Filter * | Select-Object Name, ObjectClass
```

Rechercher les anciens comptes de connecteur dont le nom commence par MSOL_.

```powershell
Get-ADUser -Filter "SamAccountName -like 'MSOL_*'" -Properties Description | Select-Object SamAccountName, Description
```
:::

::: details Vérifier les groupes d’administration
Lire les propriétés du groupe Administrateurs du domaine. Son SID se termine par 512, quelle que soit la langue du domaine.

```powershell
$sid = (Get-ADDomain).DomainSID.Value + '-512'
Get-ADGroup -Identity $sid -Properties *
```

Lister ses membres directs.

```powershell
Get-ADGroupMember -Identity ((Get-ADDomain).DomainSID.Value + '-512')
```

Afficher les membres du groupe Administrateurs de l’entreprise dans le domaine racine de la forêt.

```powershell
$racine = (Get-ADForest).RootDomain
$sid = (Get-ADDomain -Server $racine).DomainSID.Value + '-519'
Get-ADGroupMember -Identity $sid -Server $racine
```
:::

::: details Lire un groupe avec PowerView
Avec PowerView chargé, indique le nom du groupe. Chaque ligne correspond à un membre direct.

```powershell
Get-DomainGroupMember -Identity (Read-Host "Nom du groupe") |
    Select-Object GroupName, MemberName, MemberObjectClass
```
:::

## Quels postes et stratégies trouve-t-on dans une OU ? {#postes}

Une unité d’organisation (OU) regroupe des objets du domaine. Commence par retrouver son chemin, puis copie-le dans la commande qui t’intéresse.

::: details Retrouver le chemin d’une OU
Copie la valeur DistinguishedName de l’OU recherchée.

```powershell
Get-ADOrganizationalUnit -Filter * | Select-Object Name, DistinguishedName
```
:::

::: details Lister les postes placés directement dans l’OU
OneLevel limite la recherche aux objets placés juste sous cette OU.

```powershell
$ou = Read-Host "Chemin de l’OU"
Get-ADComputer -Filter * -SearchBase $ou -SearchScope OneLevel | Select-Object Name
```
:::

::: details Voir les stratégies liées directement à l’OU
Cette commande utilise le module GroupPolicy. GpoLinks affiche les liens directs. Le champ Enabled indique si le lien est actif.

```powershell
$ou = Read-Host "Chemin de l’OU"
(Get-GPInheritance -Target $ou).GpoLinks | Select-Object DisplayName, Enabled, Enforced
```
:::

::: details Consulter les OU et les stratégies avec PowerView
Dans une session où PowerView est chargé, afficher les unités d’organisation.

```powershell
Get-DomainOU | Select-Object Name, DistinguishedName
```

Afficher les GPO du domaine.

```powershell
Get-DomainGPO | Select-Object DisplayName, Name
```

Lire les liens GPO d’une OU.

```powershell
(Get-DomainOU -Identity (Read-Host 'Nom de l’OU')).gplink
```

Retrouver une GPO à partir de son GUID.

```powershell
Get-DomainGPO -Identity (Read-Host 'GUID de la GPO')
```

Consulter les paramètres de groupes locaux définis par les GPO.

```powershell
Get-DomainGPOLocalGroup
```

Lire la stratégie Kerberos renvoyée par PowerView.

```powershell
(Get-DomainPolicy).KerberosPolicy
```
:::

::: details Lister les postes d’une OU et de ses sous-OU
Copie le chemin de l’OU. Subtree inclut les unités imbriquées dans la recherche.

```powershell
$ou = Read-Host "Chemin de l’OU"
Get-ADComputer -Filter * -SearchBase $ou -SearchScope Subtree | Select-Object Name
```
:::

::: details Lire les ordinateurs d’une OU avec PowerView
Utilise le chemin complet de l’OU pour distinguer deux unités portant le même nom.

```powershell
$ou = Read-Host "Chemin de l’OU"
Get-DomainComputer -SearchBase $ou | Select-Object Name, DistinguishedName
```
:::

## Quels droits et relations vérifier ? {#droits}

::: details Lire les permissions sur un groupe
Chaque ligne indique à qui s’applique la règle, les droits concernés et son éventuel héritage.

```powershell
$groupe = Get-ADGroup -Identity (Read-Host "Nom du groupe")
(Get-Acl -Path ("AD:\" + $groupe.DistinguishedName)).Access |
    Select-Object IdentityReference, ActiveDirectoryRights, AccessControlType, IsInherited
```
:::

::: details Lire les relations d’approbation du domaine
Lis ensemble Source, Target et Direction pour interpréter le sens de chaque relation.

```powershell
Get-ADTrust -Filter * | Select-Object Source, Target, Direction, IntraForest
```
:::

::: details Examiner les relations d’un domaine précis
Interroger le domaine DNS indiqué.

```powershell
Get-ADTrust -Filter * -Server (Read-Host 'Domaine DNS')
```

Afficher les relations du domaine racine avec des domaines extérieurs à la forêt.

```powershell
Get-ADTrust -Filter 'IntraForest -eq $False' -Server (Get-ADForest).RootDomain
```

Lister les objets qui représentent des identités externes dans le domaine choisi.

```powershell
Get-ADObject -LDAPFilter '(objectClass=foreignSecurityPrincipal)' -Server (Read-Host 'Domaine DNS') | Select-Object Name, DistinguishedName
```

Avec PowerView chargé, lire les relations de la forêt indiquée.

```powershell
Get-ForestTrust -Forest (Read-Host 'Nom DNS de la forêt')
```
:::

::: details Lire les approbations et les permissions avec PowerView
Afficher les relations d’approbation de la forêt courante.

```powershell
Get-ForestTrust
```

Lire les entrées de contrôle d’accès du groupe indiqué. ResolveGUIDs traduit les identifiants de types d’objets lorsque PowerView peut les résoudre.

```powershell
Get-DomainObjectAcl -Identity (Read-Host "Nom du groupe") -ResolveGUIDs |
    Select-Object SecurityIdentifier, ActiveDirectoryRights, ObjectAceType, IsInherited
```
:::

::: details Identifier un compte externe par son SID
Si le SID désigne un utilisateur et que son domaine d’origine est connu, interroge ce domaine pour retrouver le compte correspondant.

```powershell
$domaine = Read-Host "Domaine DNS d’origine"
$sid = Read-Host "SID du compte"
Get-ADUser -Identity $sid -Server $domaine | Select-Object Name, SamAccountName, SID
```
:::

::: details PAM · lire les shadow principals
Dans une forêt de gestion PAM, cette requête affiche les objets du conteneur Shadow Principal Configuration, leurs membres et le SID représenté. Elle suppose que le conteneur existe dans la forêt interrogée.

```powershell
$configuration = (Get-ADRootDSE).configurationNamingContext
$base = "CN=Shadow Principal Configuration,CN=Services,$configuration"
Get-ADObject -SearchBase $base -SearchScope OneLevel -LDAPFilter '(objectClass=msDS-ShadowPrincipal)' -Properties member, msDS-ShadowPrincipalSid |
    Select-Object Name, member, msDS-ShadowPrincipalSid
```
:::

## Que vérifier sur le poste Windows ? {#poste-windows}

::: details Lire la session et les tickets Kerberos
Afficher les groupes présents dans le jeton de la session Windows.

```powershell
whoami /groups
```

Consulter les tickets Kerberos en cache pour la session courante.

```powershell
klist
```

Afficher le mode de langage de la session PowerShell.

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Lire la version de Windows du poste courant avec CIM.

```powershell
Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber
```
:::

::: details Vérifier AppLocker et Device Guard
Dans Windows PowerShell avec le module AppLocker, afficher les collections de règles de la stratégie effective.

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections
```

Lire la clé locale de stratégie AppLocker, si elle existe.

```powershell
reg query HKLM\Software\Policies\Microsoft\Windows\SRPV2
```

Afficher les états déclarés par Device Guard.

```powershell
Get-CimInstance -Namespace root\Microsoft\Windows\DeviceGuard -ClassName Win32_DeviceGuard | Select-Object VirtualizationBasedSecurityStatus, SecurityServicesConfigured, SecurityServicesRunning
```
:::

::: details SQL Server · lire les serveurs liés à une instance
Avec PowerUpSQL chargé, saisis le nom de l’instance que tu administres. La commande lit la liste des serveurs liés visible avec ton compte.

```powershell
Get-SQLServerLink -Instance (Read-Host "Instance SQL Server")
```
:::

[Accueil CRTP](./index) · [Module ActiveDirectory](https://learn.microsoft.com/fr-fr/powershell/module/activedirectory/) · [Get-GPInheritance](https://learn.microsoft.com/fr-fr/powershell/module/grouppolicy/get-gpinheritance)

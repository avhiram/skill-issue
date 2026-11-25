---
title: Cheatsheet AD
aside: false
---

# Cheatsheet AD

Ouvre PowerShell sur un poste du domaine équipé du module **ActiveDirectory**. Saisis le nom demandé quand tu exécutes un exemple.

[Périmètre](#perimetre) · [Comptes et groupes](#comptes) · [Postes et stratégies](#postes) · [Droits et approbations](#droits)

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

[Accueil CRTP](./index) · [Module ActiveDirectory](https://learn.microsoft.com/fr-fr/powershell/module/activedirectory/) · [Get-GPInheritance](https://learn.microsoft.com/fr-fr/powershell/module/grouppolicy/get-gpinheritance)

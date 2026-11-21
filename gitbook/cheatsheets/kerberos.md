# Kerberos — Authentification et délégation

## Principes

Kerberos utilise des tickets pour authentifier les identités et accéder aux services d'un domaine Active Directory.

| Élément | Rôle |
| --- | --- |
| KDC | Centre de distribution des clés |
| TGT | Ticket initial d'authentification |
| TGS | Ticket d'accès à un service |
| SPN | Identifiant du service |
| S4U | Extensions de délégation de service |
| RBCD | Délégation contrainte basée sur les ressources |

## Commandes de diagnostic

### Afficher les tickets Kerberos de la session

```powershell
klist
```

### Afficher les paramètres Kerberos du domaine

```powershell
Get-ADDomain | Select-Object DNSRoot,DomainMode,PDCEmulator
```

### Inventorier les comptes configurés pour une délégation

```powershell
Get-ADUser -Filter * -Properties TrustedForDelegation,TrustedToAuthForDelegation |
  Where-Object { $_.TrustedForDelegation -or $_.TrustedToAuthForDelegation } |
  Select-Object SamAccountName,TrustedForDelegation,TrustedToAuthForDelegation
```

### Consulter les SPN d'un compte de service

```powershell
Get-ADUser -Identity 'service-account' -Properties ServicePrincipalName |
  Select-Object -ExpandProperty ServicePrincipalName
```

Remplacer `service-account` par un compte autorisé.

## Points d'analyse

La délégation **non contrainte**, **contrainte** et **RBCD** repose sur des mécanismes distincts. Documenter la configuration, les comptes de service et les droits avant de conclure à une exposition.

**Source :** [Kerberos — CRTO-Study-Notes](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/cheatsheets/kerberos.md).

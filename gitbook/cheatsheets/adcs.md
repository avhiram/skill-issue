# AD CS — Audit des services de certificats

## Objectif

Identifier les autorités de certification, les modèles de certificats et les paramètres d'inscription pouvant affecter la sécurité de l'authentification Active Directory.

## Concepts essentiels

| Paramètre | Vérification |
| --- | --- |
| `ENROLLEE_SUPPLIES_SUBJECT` | Le demandeur peut-il renseigner l'identité dans la requête ? |
| EKU Client Authentication | Le certificat est-il destiné à l'authentification ? |
| Manager Approval | Une validation humaine est-elle exigée ? |
| Authorized Signatures | Des signatures supplémentaires sont-elles requises ? |
| Enrollment Permissions | Quels comptes peuvent demander le certificat ? |
| Web Enrollment | Quels services HTTP(S) sont exposés ? |

## Commandes de diagnostic

### Lister les autorités de certification

```powershell
certutil -config - -ping
```

### Afficher les modèles de certificats connus

```powershell
certutil -template
```

### Examiner la configuration de l'autorité

```powershell
certutil -getreg CA
```

À exécuter dans un contexte autorisé ; la disponibilité des commandes dépend des composants Windows installés et des droits.

## Familles de mauvaises configurations

- **ESC1 :** modèle permettant de fournir un sujet, associé à des droits d'inscription et à des usages d'authentification inadaptés.
- **ESC8 :** exposition des services d'inscription web à des risques liés à l'authentification NTLM et aux protections de canal.

Une anomalie de configuration ne constitue pas, à elle seule, la preuve d'une exploitation possible.

**Source :** [AD CS — CRTO-Study-Notes](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/cheatsheets/adcs.md).

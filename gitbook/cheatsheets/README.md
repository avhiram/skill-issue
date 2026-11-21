# CRTO — Référentiel technique

Bienvenue dans la section **Certified Red Team Operator**. Chaque fiche est accessible depuis le menu latéral et présente une technique, ses prérequis et des blocs de commandes avec coloration syntaxique et copie intégrée à GitBook.

## Active Directory

{% content-ref url="discovery.md" %}
[discovery.md](discovery.md)
{% endcontent-ref %}

**Énumération LDAP** — Inventaire des utilisateurs, groupes, ordinateurs, GPO et relations d'approbation.

## Contrôles Windows

{% content-ref url="applocker.md" %}
[applocker.md](applocker.md)
{% endcontent-ref %}

**AppLocker** — Stratégies effectives, collections de règles et diagnostic des restrictions.

## Authentification et PKI

{% content-ref url="kerberos.md" %}
[kerberos.md](kerberos.md)
{% endcontent-ref %}

**Kerberos** — Tickets, SPN et configuration de la délégation.

{% content-ref url="adcs.md" %}
[adcs.md](adcs.md)
{% endcontent-ref %}

**AD CS** — Autorités de certification, modèles de certificats et paramètres d'inscription.

---

## Organisation prévue du référentiel

| Domaine | Chapitres de la source |
| --- | --- |
| C2 et environnement | Cobalt Strike Primer |
| Défense et restrictions | AppLocker, Defense Evasion, OPSEC |
| Accès et identités | Initial Access, Credential Access, User Impersonation |
| Déplacements et réseau | Lateral Movement, Pivoting |
| Active Directory | Discovery, Kerberos, Domain Dominance, Forest & Domain Trusts |
| Services | Microsoft SQL Server, AD CS |
| Élévation et maintien d'accès | Privilege Escalation, Persistence, Elevated Persistence |
| Pratique | Laboratoires, examen et bibliothèque de commandes |

> **État réel :** seules les quatre fiches liées ci-dessus sont rédigées. Ce référentiel n'est pas encore une reproduction complète du dépôt source.

**Source de référence :** [CRTO-Study-Notes](https://github.com/botesjuan/CRTO-Study-Notes).

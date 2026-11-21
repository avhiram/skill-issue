---
title: "OSCP · Active Directory : fondamentaux"
description: "Comprendre les objets AD et les mécanismes d'authentification."
---

# Active Directory : fondamentaux

Les concepts essentiels avant de commencer l'énumération du domaine.

## Domaine et contrôleur de domaine

Le domaine rassemble comptes, ordinateurs, groupes et droits. Le contrôleur de domaine (DC) fournit notamment les services LDAP et Kerberos.

Exemple de domaine : domain.com.

## Authentification

- Kerberos : le client demande un ticket initial (TGT), puis des tickets de service (TGS).
- NTLM : protocole d'authentification par défi-réponse.
- SPN : nom associant un service à un compte Active Directory.

## Valeurs à connaître

- DONT_REQ_PREAUTH : indicateur d'un compte pouvant ne pas exiger la préauthentification Kerberos.
- DS-Replication-Get-Changes : droit utilisé dans les mécanismes de réplication de l'annuaire.

Ces éléments sont des noms d'attributs et de droits, pas des commandes.

## Passer à la pratique

- [Énumération Active Directory](ad-enumeration.md)
- [Techniques Active Directory](ad-techniques.md)
- [Mouvement latéral](ad-lateral.md)

Source : [Notes OSCP Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

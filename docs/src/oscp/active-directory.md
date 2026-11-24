---
title: "OSCP · Active Directory"
description: "Parcours de révision Active Directory, inventaire des notions et commandes de vérification."
---

# Active Directory

Parcours de révision à utiliser dans un laboratoire autorisé. Les rubriques suivent un ordre d’apprentissage, pas une chaîne d’exploitation automatique.

## Fondamentaux

Avant de lire les résultats, identifier le domaine, les contrôleurs de domaine, les utilisateurs, les groupes, les ordinateurs, les OU, les GPO et les relations entre domaines. Comprendre la différence entre LDAP, SMB, DNS, NTLM et Kerberos.

[Théorie Active Directory](ad-theorie.md)

## Découverte du domaine

### Identifier le contrôleur de domaine par DNS

Depuis un poste qui utilise le DNS du laboratoire, remplacer `example.test` par le domaine étudié. Les enregistrements SRV indiquent les serveurs qui publient le service LDAP des contrôleurs de domaine.

```bash
nslookup -type=SRV _ldap._tcp.dc._msdcs.example.test
```

### Afficher les paramètres réseau sous Linux

Remplacer `eth0` par l’interface du laboratoire. Vérifier notamment l’adresse et le DNS configuré. La commande nécessite NetworkManager.

```bash
nmcli dev show eth0
```

### Interroger les métadonnées LDAP

Lecture de la RootDSE sans modification de l’annuaire. Adapter le nom du serveur au laboratoire.

```bash
ldapsearch -x -H ldap://dc.example.test -s base
```

À connaître dans la mind map : découverte des services, DNS et transferts de zone, accès SMB invité ou anonyme, LDAP anonyme, visibilité des comptes, PXE, TimeRoasting, poisoning et coercition. Ces derniers sujets sont des risques à étudier dans leur contexte.

[Énumération Active Directory](ad-enumeration.md)

## Comptes et authentification

Distinguer un identifiant connu, un compte authentifié, les droits locaux et les droits du domaine. Un identifiant valide n’implique pas de privilège administratif.

### Lire la politique de mot de passe du domaine

Depuis PowerShell avec le module ActiveDirectory (RSAT), afficher les règles par défaut : longueur, historique et seuil de verrouillage notamment.

```powershell
Get-ADDefaultDomainPasswordPolicy
```

### Lire les politiques de mot de passe affinées

Afficher les politiques distinctes de la politique par défaut, lorsqu’elles existent.

```powershell
Get-ADFineGrainedPasswordPolicy -Filter *
```

La mind map distingue notamment les formats LM, NT, NTLMv1, NTLMv2, Kerberos TGS et AS-REP, MSCache 2, PXE et Timeroast. Elle traite aussi le password spraying, l’AS-REP Roasting, le Kerberoasting, les relais NTLM/Kerberos et les risques d’interception. Un hash, un ticket et un mot de passe en clair ne sont pas interchangeables.

## Objets, permissions et délégations

Étudier les ACL/ACE des utilisateurs, groupes, ordinateurs et OU, les GPO, les comptes gMSA, LAPS et DNS Admins. Comprendre la portée des droits de réplication, DCSync et des modifications de `msDS-KeyCredentialLink`.

Délégations Kerberos : distinguer unconstrained delegation, constrained delegation, resource-based constrained delegation et S4U2self. Examiner les relations d’autorisation sans confondre un droit sur un objet et une permission administrative générale.

## Services et configurations sensibles

### AD CS

Distinguer les modèles de certificat, l’autorité de certification (CA), les permissions sur les objets PKI, le Web Enrollment, les ACL et le certificate mapping. Un certificat d’authentification ne doit pas être confondu avec un simple certificat TLS.

### SCCM

Identifier les rôles du site, les clients, la base de données, les permissions d’administration et les paramètres de déploiement. Les catégories de la mind map comprennent les risques liés aux identifiants, à l’élévation, à la prise de contrôle du site et au nettoyage.

### Services et vulnérabilités

La mind map couvre Exchange, GLPI, Veeam, MSSQL, Java RMI, désérialisation Java, Log4Shell, Tomcat/JBoss et les services exposés. Elle cite notamment MS17-010, Zerologon (signalé comme dangereux), MS14-025, MS14-068, PrivExchange, noPac, PrintNightmare, Certifried et ProxyNotShell. Vérifier l’applicabilité de chaque CVE, la version, les correctifs et les règles du laboratoire avant toute validation.

## Privilèges locaux et accès distants

Distinguer les comptes de service, SeImpersonatePrivilege, UAC, AppLocker, les configurations WebDAV et les informations présentes dans les fichiers. Étudier les risques liés à LSASS, SAM, LSA et DPAPI, sans assimiler un accès local à un droit sur l’ensemble du domaine.

Pour les accès distants, distinguer les protocoles, le compte et le contexte d’authentification : mot de passe, NT hash, ticket Kerberos, certificat PFX, MSSQL et SOCKS. Les droits de connexion varient selon le service et la machine.

- [Privilèges Windows](privileges-windows.md)
- [Techniques Active Directory](ad-techniques.md)
- [Mouvement latéral Active Directory](ad-lateral.md)

## Relations d’approbation

### Lire les relations d’approbation Windows

Depuis un poste Windows joint au domaine, afficher les domaines approuvés visibles par le poste.

```cmd
nltest.exe /trusted_domains
```

La mind map distingue les trusts parent/enfant, les trusts externes et les liens MSSQL. Étudier les SID de domaine, le sens de la relation, sa transitivité et les frontières d’autorisation.

## Risques liés aux privilèges de domaine et à la persistance

La mind map présente les risques concernant NTDS.dit, les clés de sauvegarde, les droits de réplication, les modifications d’ACL, DCShadow, les comptes administrateurs et DSRM. Elle recense aussi Golden/Silver/Diamond/Sapphire Ticket, Golden Certificate, Skeleton Key et Custom SSP. Ces notions sont à comprendre en termes d’impact, de détection et de remédiation. Elles ne constituent pas un objectif systématique d’un examen OSCP.

## Rapport et révision

Documenter le périmètre, le contexte du compte utilisé, les observations, les preuves, les limites de la validation et les remédiations. Consulter les règles OffSec en vigueur avant l’examen.

[Rédaction de rapports](rapport.md) · [Références](references.md)

## Mind map complète

[Active Directory Mindmap v2025.03 - Orange Cyberdefense](https://orange-cyberdefense.github.io/ocd-mindmaps/img/mindmap_ad_dark_classic_2025.03.excalidraw.svg)

Cette fiche est une synthèse de révision en français. La mind map originale contient l’intégralité des notes, exemples et commandes dans leur contexte. Les exemples de vérification ci-dessus en sont adaptés ; ils n’ont pas été exécutés ici.

Projet original : [ocd-mindmaps](https://github.com/Orange-Cyberdefense/ocd-mindmaps) · Mayfly et contributeurs · GPL-3.0.

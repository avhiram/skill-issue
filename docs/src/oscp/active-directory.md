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

### Reconnaissance réseau

Les exemples utilisent les adresses réservées à la documentation `192.0.2.0/24` et le domaine `example.test`. Remplacer ces valeurs uniquement par celles du laboratoire autorisé.

#### Découvrir les hôtes actifs

<p class="oscp-command-note">Repérer les machines joignables sur le réseau du laboratoire sans scanner leurs ports. La notation `-sP -p` de la mind map est remplacée par `-sn`, qui correspond à la découverte d’hôtes.</p>

```bash
nmap -sn 192.0.2.0/28
```

#### Identifier les ports TCP les plus courants

<p class="oscp-command-note">Effectuer un premier inventaire des 50 ports les plus fréquents et des versions des services ouverts.</p>

```bash
nmap -Pn -sV --top-ports 50 --open 192.0.2.10
```

#### Examiner les ports TCP courants

<p class="oscp-command-note">Identifier les services sur les ports TCP par défaut et enregistrer les résultats dans les trois formats Nmap. Les scripts par défaut ne sont à utiliser que dans le périmètre autorisé.</p>

```bash
nmap -Pn -sC -sV -oA ad-tcp 192.0.2.10
```

#### Examiner tous les ports TCP

<p class="oscp-command-note">Étendre l’inventaire aux 65 535 ports TCP lorsque le premier contrôle ne suffit pas.</p>

```bash
nmap -Pn -sC -sV -p- -oA ad-tcp-complet 192.0.2.10
```

#### Examiner les services UDP

<p class="oscp-command-note">Compléter le relevé TCP par un inventaire UDP. Ce contrôle peut être plus lent et nécessiter des privilèges élevés.</p>

```bash
nmap -sU -sC -sV -oA ad-udp 192.0.2.10
```

#### Identifier les services SMB

<p class="oscp-command-note">Recenser les machines qui répondent sur SMB avec NetExec, sans fournir d’identifiants.</p>

```bash
nxc smb 192.0.2.0/28
```

#### Vérifier les versions du protocole SMB

<p class="oscp-command-note">La mind map propose des scripts de vulnérabilité SMB génériques. Pour ce premier contrôle, utiliser un script ciblé de lecture des protocoles pris en charge ; SMBv1 est notamment une configuration à examiner.</p>

```bash
nmap -p 139,445 --script smb-protocols 192.0.2.10
```

### Identification du contrôleur de domaine

#### Afficher la configuration réseau Linux

<p class="oscp-command-note">Vérifier l’adresse IP, la passerelle et les serveurs DNS de l’interface. Remplacer eth0 par l’interface réelle. NetworkManager doit être présent.</p>

```bash
nmcli dev show eth0
```

#### Localiser les contrôleurs de domaine par DNS

<p class="oscp-command-note">Interroger les enregistrements SRV LDAP du domaine. Utiliser le serveur DNS du laboratoire et remplacer example.test par le domaine étudié.</p>

```bash
nslookup -type=SRV _ldap._tcp.dc._msdcs.example.test
```

#### Identifier les serveurs Kerberos

<p class="oscp-command-note">Rechercher les hôtes du laboratoire qui exposent le port TCP 88. Un port 88 ouvert est un indice, pas une preuve qu’un hôte est un contrôleur de domaine.</p>

```bash
nmap -p 88 --open 192.0.2.0/28
```

### Vérification DNS

#### Contrôler les transferts de zone DNS

<p class="oscp-command-note">Vérifier sur le serveur DNS du laboratoire si un transfert AXFR est autorisé. Un refus peut être normal ; un transfert réussi doit être comparé à la politique d’autorisation des serveurs secondaires.</p>

```bash
dig @192.0.2.10 example.test AXFR
```

### Accès SMB anonymes et invités

#### Vérifier une session SMB anonyme

<p class="oscp-command-note">Tester une connexion sans nom d’utilisateur ni mot de passe. Une session acceptée ne signifie pas que tous les partages sont accessibles.</p>

```bash
nxc smb 192.0.2.10 -u '' -p ''
```

#### Vérifier le mappage vers le compte Guest

<p class="oscp-command-note">La mind map utilise un nom arbitraire et un mot de passe vide pour vérifier le mappage invité. Choisir un nom de test inexistant dans le laboratoire. Selon la version de NetExec, activer check_guest_account dans ~/.nxc/nxc.conf pour identifier explicitement Guest.</p>

```bash
nxc smb 192.0.2.10 -u 'a' -p ''
```

#### Lister les partages visibles avec Samba

<p class="oscp-command-note">Demander la liste des partages avec une identité vide. La notation % sépare le nom du mot de passe ; aucun des deux n’est renseigné. La liste ne prouve pas les droits de lecture ou d’écriture.</p>

```bash
smbclient -U '%' -L //192.0.2.10
```

#### Vérifier les informations SMB accessibles sans compte

<p class="oscp-command-note">La mind map utilise -a ; dans enum4linux-ng, l’option documentée est -A. Elle regroupe plusieurs contrôles d’énumération. Les informations disponibles dépendent des permissions et de la configuration du serveur.</p>

```bash
enum4linux-ng -A -u '' -p '' 192.0.2.10
```

### Informations LDAP accessibles

#### Interroger les métadonnées LDAP

<p class="oscp-command-note">Lire la RootDSE pour identifier les contextes de nommage, notamment defaultNamingContext. La portée base limite la recherche à l’objet racine ; -x utilise l’authentification simple, ici sans identifiants.</p>

```bash
ldapsearch -x -H ldap://dc.example.test -s base -b ''
```

#### Vérifier la RootDSE avec Nmap

<p class="oscp-command-note">Alternative à ldapsearch. La mind map utilise un ensemble générique de scripts LDAP ; ici le script ldap-rootdse est sélectionné explicitement pour lire les métadonnées, sans lancer les autres scripts.</p>

```bash
nmap -n -sV -p 389 --script ldap-rootdse 192.0.2.10
```

### Énumération des utilisateurs du domaine

Avec un compte de test autorisé, comparer les utilisateurs visibles aux informations de l’annuaire. Les exemples utilisent le domaine de laboratoire `EXAMPLE`, le contrôleur `dc.example.test` et le compte `audit`.

#### Net RPC - lister les membres du groupe Domain Users

<p class="oscp-command-note">Afficher les membres du groupe Domain Users avec Samba. L’option -W indique le domaine, -S le serveur et -U le compte de test. Le mot de passe est demandé interactivement. Le nom du groupe peut être localisé selon la langue du domaine.</p>

```bash
net rpc group members 'Domain Users' -W EXAMPLE -S dc.example.test -U audit
```

#### NetExec - lister les utilisateurs du domaine

<p class="oscp-command-note">Afficher les utilisateurs accessibles au compte de test via SMB. Remplacer la valeur illustrative du mot de passe par celle du laboratoire ; ne pas conserver de secrets réels dans les notes. Le résultat dépend des droits et de la configuration du contrôleur.</p>

```bash
nxc smb 192.0.2.10 -d example.test -u audit -p 'MOT_DE_PASSE_LAB' --users
```

#### Risques de divulgation des noms de comptes

La mind map distingue trois autres méthodes : recherche de comptes par identifiant relatif (RID), énumération Kerberos avec le script NSE krb5-enum-users et Kerbrute userenum. Ces méthodes peuvent révéler l’existence de comptes et générer un volume important de requêtes. Pour la revue de configuration, privilégier un inventaire authentifié et vérifier les restrictions de visibilité et la journalisation. Les trois méthodes sont recensées ici au niveau conceptuel, sans procédures de brute force.

### Poisoning réseau

Le poisoning consiste à fausser les réponses réseau utilisées par une machine. Cette branche est étudiée au niveau conceptuel ; les commandes ci-dessous sont des vérifications locales en lecture seule, complémentaires aux exemples de la mind map. Utiliser PowerShell sur un poste Windows autorisé.

#### LLMNR, NBT-NS et mDNS

Ces mécanismes de résolution de noms peuvent accepter des réponses non fiables selon le réseau et la configuration. Vérifier les politiques de résolution de noms et distinguer LLMNR, NetBIOS Name Service et mDNS : désactiver l’un ne désactive pas nécessairement les autres.

#### PowerShell - vérifier la politique LLMNR

<p class="oscp-command-note">Lire la valeur EnableMulticast de la politique DNS Client. Une valeur de 0 correspond à la désactivation de LLMNR par cette politique. Une valeur absente ne permet pas de conclure à sa désactivation.</p>

```powershell
Get-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient' -Name EnableMulticast
```

#### PowerShell - vérifier NetBIOS sur TCP/IP

<p class="oscp-command-note">Afficher le réglage NetBIOS des interfaces IP actives. Les valeurs 0, 1 et 2 correspondent respectivement au réglage DHCP, à l’activation et à la désactivation.</p>

```powershell
Get-CimInstance -ClassName Win32_NetworkAdapterConfiguration -Filter 'IPEnabled = TRUE' | Select-Object Description, TcpipNetbiosOptions
```

#### DHCPv6

Un serveur DHCPv6 non autorisé peut modifier les paramètres réseau reçus par un client. La préférence IPv6 dépend de la politique de sélection des adresses et du contexte réseau. Contrôler la provenance des paramètres DNS et IPv6 ; ne pas désactiver IPv6 systématiquement.

#### PowerShell - lire la configuration IP et DNS

<p class="oscp-command-note">Afficher les adresses IPv4 et IPv6, les passerelles et les serveurs DNS des interfaces. Comparer les valeurs aux paramètres attendus du laboratoire.</p>

```powershell
Get-NetIPConfiguration
```

#### ARP poisoning

Une association IP/MAC falsifiée peut détourner des échanges sur un segment IPv4. La mind map mentionne aussi le risque d’exposition de données d’authentification Kerberos AS-REQ lors d’une interception. Une observation du cache ARP ne suffit pas à démontrer une attaque.

#### PowerShell - consulter le cache ARP

<p class="oscp-command-note">Afficher les entrées IPv4 du cache de voisinage et comparer les adresses MAC à un inventaire de référence. Ce contrôle est passif et ne modifie pas les associations.</p>

```powershell
Get-NetNeighbor -AddressFamily IPv4
```

### Coercition d’authentification SMB

La coercition d’authentification désigne le fait de provoquer une authentification réseau non sollicitée. La mind map cite PetitPotam et CVE-2022-26925, une vulnérabilité Windows LSA associée aux risques de relais NTLM. Distinguer la coercition, qui déclenche une authentification, du relay, qui tente de réutiliser celle-ci auprès d’un autre service.

Cette technique est documentée au niveau conceptuel. Les commandes suivantes sont des contrôles complémentaires en lecture seule, à exécuter sur les postes et serveurs Windows autorisés avec le module SmbShare et les permissions nécessaires. Vérifier également les mises à jour de sécurité, les restrictions NTLM et l’Extended Protection for Authentication (EPA) des services concernés. La signature SMB ne protège pas à elle seule les autres protocoles.

#### PowerShell - vérifier la signature SMB côté client

<p class="oscp-command-note">Afficher si la signature SMB est exigée pour les connexions sortantes. True indique une signature obligatoire ; False signifie qu’elle n’est pas imposée par ce réglage.</p>

```powershell
Get-SmbClientConfiguration | Select-Object RequireSecuritySignature
```

#### PowerShell - vérifier la signature SMB côté serveur

<p class="oscp-command-note">Afficher si la signature SMB est exigée pour les connexions entrantes. Ce réglage est distinct de celui du client et doit être contrôlé sur le serveur concerné. Le résultat ne confirme pas à lui seul la présence ou l’absence de CVE-2022-26925.</p>

```powershell
Get-SmbServerConfiguration | Select-Object RequireSecuritySignature
```

### PXE - déploiement réseau

PXE (Preboot Execution Environment) permet de démarrer un poste depuis le réseau afin de déployer un système d’exploitation. Distinguer Windows Deployment Services (WDS) du PXE responder de Configuration Manager (SCCM), qui peut fonctionner sans WDS.

#### PXE sans mot de passe

La mind map signale le risque d’exposition du Network Access Account (NAA) dans certaines configurations de déploiement. Le NAA sert à accéder au contenu lorsque le compte ordinateur ne peut pas le faire. Il ne constitue pas le compte d’exécution de la Task Sequence. Vérifier le besoin réel du NAA et limiter ses permissions.

#### PXE protégé par mot de passe

La protection par mot de passe ajoute une barrière d’accès au démarrage PXE, mais ne garantit pas à elle seule la sécurité des secrets associés au déploiement. La mind map mentionne également le risque portant sur les données de vérification du mot de passe PXE. Contrôler les restrictions de déploiement, la segmentation réseau et les comptes utilisés dans les Task Sequences.

Les quatre commandes de la branche PXE sont traitées au niveau conceptuel. Les contrôles administratifs suivants sont complémentaires et en lecture seule.

#### PowerShell - vérifier le rôle WDS

<p class="oscp-command-note">Afficher l’état d’installation du rôle Windows Deployment Services sur le serveur local. Exécuter depuis Windows Server avec le module ServerManager. L’absence de WDS n’exclut pas un PXE responder SCCM autonome.</p>

```powershell
Get-WindowsFeature -Name WDS
```

#### WDSUtil - consulter la configuration WDS

<p class="oscp-command-note">Afficher la configuration du serveur WDS local sans la modifier. Utiliser une console CMD avec les outils WDS et les droits administratifs nécessaires. Ce contrôle ne remplace pas la revue des paramètres PXE dans Configuration Manager.</p>

```cmd
wdsutil /Get-Server /Show:Config
```

La branche TimeRoasting reste à examiner séparément.

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

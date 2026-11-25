---
title: "4 - Offensive .NET"
---

# Offensive .NET

## Outils .NET

Les outils développés en C# peuvent interagir avec Windows, Active Directory et les mécanismes d'authentification. Leur exécution peut prendre la forme d'un binaire .NET ou d'un chargement en mémoire.

## Détection antivirus

Les notes d'origine présentent plusieurs méthodes qui modifient la forme d'un binaire : obfuscation, modification de chaînes, compression et intégration de contenu dans un programme.

Ces modifications peuvent changer les indicateurs statiques d'un fichier. Elles ne changent pas nécessairement son comportement à l'exécution.

### DefenderCheck

DefenderCheck sert à identifier les parties d'un binaire susceptibles de déclencher une détection Windows Defender. Dans un audit défensif, ces résultats aident à comprendre les éléments signalés par l'antivirus.

### SharpKatz

SharpKatz est un outil .NET qui reprend certaines fonctionnalités de Mimikatz. Les usages présentés dans les notes concernent des données d'authentification Windows.

### SafetyKatz

SafetyKatz associe des fonctionnalités de Mimikatz à un mécanisme de chargement en mémoire. Les notes d'origine décrivent également l'utilisation d'un contenu compressé.

### BetterSafetyKatz

Les notes présentent une variante qui intègre le contenu d'une archive directement dans le programme. Cette méthode modifie le mode de stockage et de chargement du binaire.

### Rubeus

Rubeus est un outil orienté Kerberos. Les notes d'origine mentionnent l'obfuscation de son binaire et la modification de métadonnées d'assembly.

## Payload Delivery

Les notes présentent NetLoader et AssemblyLoad comme des outils de chargement de binaires depuis un chemin local ou une URL.

NetLoader est également associé à des modifications d'AMSI et d'ETW. Ces mécanismes sont sensibles, car ils peuvent réduire la visibilité des outils de sécurité sur l'exécution PowerShell et .NET.

### Indicateurs à surveiller

- Chargement inattendu d'assemblies .NET en mémoire.
- Exécution de binaires depuis des répertoires inhabituels ou des URL distantes.
- Modifications inattendues des mécanismes AMSI et ETW.
- Connexions réseau initiées par un processus qui n'en a pas habituellement besoin.

## Chemins de compromission du laboratoire

Les deux scénarios ci-dessous sont décrits au niveau des mécanismes et des traces à rechercher. Les commandes de contournement, de chargement furtif et d'extraction d'identifiants ne sont pas reproduites.

### Scénario 1 - dcorp-ci

Le scénario associe l'administration distante via WinRM, le transfert d'un binaire, une redirection de port locale et l'accès à des données d'authentification. Il se termine par l'utilisation de matériel Kerberos associé à un compte privilégié.

**Points de surveillance**

- Sessions WinRM inattendues et commandes distantes inhabituelles.
- Copie de binaires vers des partages administratifs.
- Modification de la configuration portproxy.
- Accès anormal au processus LSASS.
- Activité Kerberos inhabituelle liée à des comptes privilégiés.

### Scénario 2 - Droits administrateur locaux indirects

Ce scénario part d'un compte disposant de droits administrateur locaux sur une machine. Il examine ensuite les possibilités d'administration distante, les restrictions du langage PowerShell et les règles AppLocker.

La présence de droits administrateur locaux sur une machine ne donne pas automatiquement des privilèges sur le domaine. Le risque apparaît lorsque ces droits permettent d'accéder à une autre machine ou à une session contenant des données d'authentification sensibles.

**Points de surveillance**

- Utilisation inhabituelle de PowerShell Remoting.
- Restrictions Constrained Language et règles AppLocker modifiées ou contournées.
- Copie de scripts ou d'outils d'administration vers des machines distantes.
- Accès à LSASS et utilisation de tickets Kerberos depuis une session inattendue.

## Contrôles défensifs

- Limiter les comptes disposant de droits administrateur locaux.
- Restreindre et journaliser l'administration distante.
- Appliquer les règles AppLocker et contrôler leur modification.
- Surveiller les accès à LSASS et les chargements .NET inhabituels.
- Contrôler les modifications d'AMSI, d'ETW et de la configuration réseau.
- Corréler les événements PowerShell, WinRM, Defender et Kerberos.

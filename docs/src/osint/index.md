---
title: OSINT
description: Méthode, ressources et commandes de recherche en sources ouvertes.
aside: false
prev: false
next: false
---

# OSINT

Une bibliothèque pratique pour la recherche en sources ouvertes. Les outils sont classés selon la **question à résoudre**, pas selon leur popularité.

**[Cheatsheet OSINT - commandes à copier](./cheatsheet.md)**

Choisis un point de départ : **pseudonyme**, **e-mail**, **nom**, **domaine**, **image** ou **infrastructure**. Les résultats se recoupent avant toute conclusion.

## Recherche Web et dorks

- **[Google](https://www.google.com/)** - Requêtes avancées avec `site:`, `filetype:` et expressions exactes.
- **[Bing](https://www.bing.com/)** - Autre index pour comparer les résultats.
- **[Brave Search](https://search.brave.com/)** - Moteur complémentaire pour élargir la recherche.
- **[Qwant](https://www.qwant.com/)** - Moteur de recherche alternatif.
- **[Google Hacking Database](https://www.exploit-db.com/google-hacking-database)** - Exemples d'opérateurs pour une reconnaissance autorisée.

## Pseudonymes et profils publics

- **[Sherlock](https://github.com/sherlock-project/sherlock)** - Rechercher les comptes liés à un pseudonyme.
- **[Maigret](https://github.com/soxoj/maigret)** - Croiser les profils publics et produire un rapport.
- **[WhatsMyName](https://github.com/WebBreacher/WhatsMyName)** - Vérifier des pseudonymes sur des plateformes.
- **[Social Analyzer](https://github.com/qeeqbox/social-analyzer)** - Compléter l'analyse des profils sociaux publics.
- **[Reddit Search](https://www.reddit.com/search/)** - Retrouver des publications et commentaires publics.
- **[X - Recherche avancée](https://x.com/search-advanced)** - Combiner mots-clés, comptes et périodes lorsque la recherche est disponible.

## E-mails et exposition

- **[Holehe](https://github.com/megadose/holehe)** - Rechercher des indices d'inscription à partir d'un e-mail.
- **[Have I Been Pwned](https://haveibeenpwned.com/)** - Vérifier l'apparition d'un e-mail dans des incidents documentés.
- **[EmailRep](https://emailrep.io/)** - Consulter des indicateurs de réputation d'une adresse.
- **[Hunter](https://hunter.io/)** - Rechercher des adresses et formats d'e-mails professionnels publics.

## Domaines, DNS et sous-domaines

- **[theHarvester](https://github.com/laramies/theHarvester)** - Collecter sous-domaines, e-mails, URL et indices publics.
- **[crt.sh](https://crt.sh/)** - Explorer les noms figurant dans les certificats publics.
- **[Subfinder](https://github.com/projectdiscovery/subfinder)** - Rassembler des sous-domaines à partir de sources passives.
- **[Amass](https://github.com/owasp-amass/amass)** - Cartographier la surface d'exposition d'un domaine.
- **[SecurityTrails](https://securitytrails.com/dns-trails)** - Consulter des données DNS et leurs évolutions.
- **[BGP.tools](https://bgp.tools/)** - Identifier les annonces BGP et les réseaux associés.
- **[ICANN Lookup](https://lookup.icann.org/)** - Consulter les informations d'enregistrement disponibles.

## Infrastructure et cybermenaces

- **[Shodan](https://www.shodan.io/)** - Rechercher les services Internet indexés.
- **[Censys](https://search.censys.io/)** - Explorer les hôtes, certificats et services connus.
- **[VirusTotal](https://www.virustotal.com/)** - Recouper IP, domaines, URL et empreintes de fichiers.
- **[urlscan.io](https://urlscan.io/)** - Examiner les observations publiques de pages et URL.
- **[AbuseIPDB](https://www.abuseipdb.com/)** - Consulter les signalements associés à une adresse IP.
- **[AlienVault OTX](https://otx.alienvault.com/)** - Recouper des indicateurs de compromission.
- **[URLhaus](https://urlhaus.abuse.ch/)** - Rechercher des URL associées à la diffusion de malware.
- **[ThreatFox](https://threatfox.abuse.ch/)** - Examiner les indicateurs publics de menace.

## Archives et publications

- **[Wayback Machine](https://web.archive.org/)** - Voir les versions conservées d'une page Web.
- **[Internet Archive](https://archive.org/)** - Rechercher des pages, documents et contenus archivés.
- **[DocumentCloud](https://www.documentcloud.org/)** - Explorer des documents publics et leurs annotations.
- **[Google Dataset Search](https://datasetsearch.research.google.com/)** - Retrouver des jeux de données publics.
- **[GitHub Search](https://github.com/search)** - Retrouver projets, dépôts et discussions indexés.

## Images, vidéos et géolocalisation

- **[Google Lens](https://lens.google.com/)** - Retrouver des images ressemblantes et éléments visuels.
- **[TinEye](https://tineye.com/)** - Rechercher les copies publiques d'une image.
- **[ExifTool](https://exiftool.org/)** - Lire les métadonnées d'images et de documents.
- **[Bellingcat Toolkit](https://bellingcat.gitbook.io/toolkit)** - Recouper lieux, médias et informations publiques.
- **[Google Earth](https://earth.google.com/web/)** - Comparer des vues de terrain et des repères géographiques.
- **[OpenStreetMap](https://www.openstreetmap.org/)** - Comparer rues, bâtiments et points d'intérêt.

## Entreprises et registres

- **[Annuaire des entreprises](https://annuaire-entreprises.data.gouv.fr/)** - Vérifier les données des sociétés et établissements français.
- **[OpenCorporates](https://opencorporates.com/)** - Explorer les registres d'entreprises de plusieurs pays.
- **[Pappers](https://www.pappers.fr/)** - Consulter les informations légales publiques d'entreprises françaises.

## Méthodes, rapports et référentiels

- **[Awesome OSINT](https://github.com/jivoi/awesome-osint)** - Trouver une ressource complémentaire par domaine d'investigation.
- **[OSINT Cheat Sheet](https://github.com/Jieyab89/OSINT-Cheat-sheet)** - Répertoire étendu de méthodes et d'outils.
- **[OSINT Framework](https://osintframework.com/)** - Choisir un outil selon le type de renseignement.
- **[CyberChef](https://gchq.github.io/CyberChef/)** - Convertir et décoder des données.
- **[MITRE ATT&CK](https://attack.mitre.org/)** - Relier des indices cyber aux techniques documentées.

## Méthode de recherche

1. **Définir** la question, la cible et le périmètre.
2. **Collecter** les informations publiques avec deux sources différentes.
3. **Recouper** les identifiants, dates, domaines et relations sans conclure sur un seul indice.
4. **Conserver** les URL, les dates UTC et les captures nécessaires au compte rendu.

La disponibilité et les fonctionnalités de certains services varient selon leur formule. Une correspondance de pseudonyme ou de nom n'est pas une preuve d'identité.

**[Consulter les commandes OSINT](./cheatsheet.md)**

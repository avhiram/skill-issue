---
title: OSINT - Cheatsheet
description: OSINT, commandes et installations pour une enquête chronologique.
aside: false
prev: false
next: false
---

# Cheatsheet OSINT

Tu commences avec **une information**. Voici où démarrer, puis quelles commandes utiliser.

| Tu disposes de | D'abord | Ensuite |
| --- | --- | --- |
| Pseudonyme | Recherche exacte Google | Réseaux sociaux, Sherlock, Maigret, Blackbird |
| E-mail | Recherche exacte Google | Documents publics, Holehe, Blackbird |
| Prénom et nom | Nom exact + organisation | Réseaux, documents publics et publications |
| Domaine | Google `site:`, WHOIS | DNS, certificats, theHarvester, Subfinder |
| URL ou site | HTTP et redirections | Archives, Photon |
| Photo ou PDF | ExifTool, `pdfinfo` | Recouper avec les résultats Web |

Remplace directement `pseudo_exemple`, `exemple@example.com`, `Camille Exemple` ou `example.com` dans les exemples. Les dorks sont des requêtes à coller dans Google.

[Outils et ressources OSINT](./index.md)

## Méthode - cycle du renseignement

1. **Cadrage et orientation** - définir la question et le périmètre de recherche.
2. **Collecte** - recueillir les informations accessibles dans les sources retenues.
3. **Traitement et exploitation** - classer les éléments et extraire les données utiles.
4. **Analyse et production** - recouper les informations et distinguer les faits des hypothèses.
5. **Diffusion et intégration** - présenter les résultats de façon claire et traçable.

## Installer les outils

Sur Kali Linux. À exécuter une fois selon les outils que tu souhaites utiliser. Les moteurs de recherche et sites Web n'ont rien à installer.

### Utilitaires de base

Installer les outils de recherche, de métadonnées et de rapports.

```bash
sudo apt update && sudo apt install -y file coreutils grep git curl jq whois dnsutils openssl pipx python3-venv libimage-exiftool-perl poppler-utils xdg-utils
```

### FFprobe et MediaInfo

Installer les outils complémentaires pour analyser les vidéos.

```bash
sudo apt install -y ffmpeg mediainfo
```

### Préparer les applications Python

Ajouter au PATH les programmes installés par pipx.

```bash
pipx ensurepath
```

### Sherlock

Installer l'outil de recherche de pseudonymes.

```bash
pipx install sherlock-project
```

### Maigret

Installer Maigret et ses fonctions d'export.

```bash
pipx install maigret
```

### Holehe

Installer Holehe dans un environnement séparé.

```bash
python3 -m venv "$HOME/.venvs/holehe"
"$HOME/.venvs/holehe/bin/pip" install holehe
```

### uv

Installer le gestionnaire utilisé par theHarvester actuel.

```bash
pipx install uv
```

### theHarvester

Installer la version du dépôt ; uv choisit ses dépendances et son Python.

```bash
mkdir -p "$HOME/outils"
git clone https://github.com/laramies/theHarvester.git "$HOME/outils/theHarvester"
(cd "$HOME/outils/theHarvester" && uv sync)
```

### Subfinder - version Go (alternative)

Nécessite une version de Go compatible avec la version téléchargée. Sur Kali, utilise plutôt le paquet ci-dessous.

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

### Subfinder - Kali

Installation via les dépôts de Kali Linux.

```bash
sudo apt install -y subfinder
```

### Blackbird

Installation dans un environnement Python séparé.

```bash
mkdir -p "$HOME/outils"
git clone https://github.com/antoniaci/blackbird.git "$HOME/outils/blackbird"
python3 -m venv "$HOME/.venvs/blackbird"
"$HOME/.venvs/blackbird/bin/pip" install -r "$HOME/outils/blackbird/requirements.txt"
```

### Photon

Installation dans un environnement Python séparé.

```bash
mkdir -p "$HOME/outils"
git clone https://github.com/s0md3v/Photon.git "$HOME/outils/Photon"
python3 -m venv "$HOME/.venvs/photon"
"$HOME/.venvs/photon/bin/pip" install -r "$HOME/outils/Photon/requirements.txt"
```

### dnstwist - Kali

Installe l'outil de recherche de domaines ressemblants.

```bash
sudo apt install -y dnstwist
```

### Fierce - Kali

Installe l'outil de reconnaissance DNS.

```bash
sudo apt install -y fierce
```

### WhatWeb

Installer l'outil de fingerprinting des technologies Web.

```bash
sudo apt install -y whatweb
```

### Amass - Kali

Installe l'outil de découverte de domaines.

```bash
sudo apt install -y amass
```

### Recon-ng - Kali

Installe le framework de reconnaissance.

```bash
sudo apt install -y recon-ng
```

### SpiderFoot - Kali

Installe l'outil de collecte OSINT.

```bash
sudo apt install -y spiderfoot
```

## Démarrer l'enquête

Crée le dossier de travail, puis lance les recherches à partir des éléments disponibles.

### Préparer un dossier

Créer une structure simple pour les fichiers de travail.

```bash
mkdir -p dossier_osint/{notes,captures,rapports,documents}
```

### Heure d'observation

Afficher l'heure UTC au format ISO 8601.

```bash
date -u '+%Y-%m-%dT%H:%M:%SZ'
```

## Première recherche - partir de l'information connue

Commence par le pseudo, l'e-mail, le nom ou le domaine que tu possèdes. Ces requêtes sont à coller directement dans Google.

### Occurrences exactes

Retrouver les pages publiques qui contiennent le pseudo.

```text
"pseudo_exemple"
```

### Profils GitHub

Rechercher ce pseudo sur GitHub indexé.

```text
"pseudo_exemple" site:github.com
```

### Discussions Reddit

Rechercher les mentions du pseudo sur Reddit.

```text
"pseudo_exemple" site:reddit.com
```

### Profils LinkedIn

Chercher un profil public portant le même identifiant.

```text
"pseudo_exemple" site:linkedin.com/in/
```

### Forums et communautés

Retrouver des messages associés au pseudo.

```text
"pseudo_exemple" (forum OR discussion OR communauté)
```

### Occurrences exactes d'un e-mail

Chercher l'adresse exacte dans les pages indexées.

```text
"exemple@example.com"
```

### E-mail dans les PDF

Rechercher les documents publics où l'adresse apparaît.

```text
"exemple@example.com" filetype:pdf
```

### E-mail sur les plateformes de code

Rechercher les pages de code indexées contenant l'adresse.

```text
"exemple@example.com" (site:github.com OR site:gitlab.com)
```

### Nom exact

Rechercher le nom complet avec des guillemets.

```text
"Camille Exemple"
```

### PDF avec le nom

Repérer des documents publics associés au nom.

```text
"Camille Exemple" filetype:pdf
```

### Profils professionnels

Chercher des profils LinkedIn indexés au même nom.

```text
"Camille Exemple" site:linkedin.com/in/
```

### Presse et interviews

Repérer des publications qui mentionnent le nom.

```text
"Camille Exemple" (interview OR conférence OR article)
```

### Nom et organisation

Recouper le nom avec une organisation déclarée.

```text
"Camille Exemple" "Organisation Exemple"
```

### Pages indexées

Lister les pages publiques d'un domaine.

```text
site:example.com
```

### Termes présents dans le contenu

Rechercher un mot ou une expression dans le texte des pages.

```text
intext:"rapport annuel"
```

### Termes présents dans le titre

Rechercher les pages dont le titre contient une expression.

```text
intitle:"rapport annuel"
```

### PDF du domaine

Trouver les documents PDF publics du domaine.

```text
site:example.com filetype:pdf
```

### Documents bureautiques

Trouver les feuilles de calcul publiquement indexées.

```text
site:example.com filetype:xlsx
```

### Pages de contact

Rechercher les pages contact ou à propos.

```text
site:example.com (inurl:contact OR inurl:about)
```

### Sous-domaines indexés

Repérer certaines pages hors du sous-domaine www ; résultat non exhaustif.

```text
site:example.com -site:www.example.com
```

### Mentions externes d'une organisation

Identifier des pages extérieures au site principal.

```text
"Organisation Exemple" -site:example.com
```

### Mentions récentes

Filtrer les publications selon une date de début à adapter.

```text
"Organisation Exemple" after:2026-01-01
```

## Réseaux sociaux - rechercher les profils

Recherches Google sur les **profils et publications publics**. Pour les résultats non indexés, consulte aussi la recherche interne de chaque réseau.

### Facebook - nom

Profils ou publications publiques portant ce nom.

```text
"Camille Exemple" site:facebook.com
```

### Facebook - pseudo

Mentions et profils publics associés au pseudo.

```text
"pseudo_exemple" site:facebook.com
```

### Instagram - pseudo

Profils et publications Instagram indexés.

```text
"pseudo_exemple" site:instagram.com
```

### Instagram - nom

Publications et mentions du nom.

```text
"Camille Exemple" site:instagram.com
```

### Snapchat - pseudo

Profils Snapchat publics accessibles via l'URL d'ajout.

```text
"pseudo_exemple" site:snapchat.com/add
```

### Snapchat - nom

Mentions publiques sur le site Snapchat.

```text
"Camille Exemple" site:snapchat.com
```

### X - pseudo

Retrouver les profils et publications publiques sur X.

```text
"pseudo_exemple" site:x.com
```

### X - anciens liens Twitter

Compléter avec les anciennes URL twitter.com indexées.

```text
"pseudo_exemple" site:twitter.com
```

### X - nom

Chercher les mentions du nom sur X.

```text
"Camille Exemple" site:x.com
```

### X - publications d'un compte

Requête pour la recherche interne X (à coller sur X).

```text
from:pseudo_exemple
```

### LinkedIn - nom

Profils professionnels publics au nom recherché.

```text
"Camille Exemple" site:linkedin.com/in/
```

### LinkedIn - pseudo

Mentions du pseudo dans les profils publics.

```text
"pseudo_exemple" site:linkedin.com
```

### TikTok - pseudo

Profils et vidéos indexés.

```text
"pseudo_exemple" site:tiktok.com/@
```

### TikTok - nom

Mentions publiques d'un nom sur TikTok.

```text
"Camille Exemple" site:tiktok.com
```

### YouTube - nom

Chaînes, vidéos et descriptions publiques.

```text
"Camille Exemple" site:youtube.com
```

### YouTube - pseudo

Rechercher les chaînes utilisant ce nom public.

```text
"pseudo_exemple" site:youtube.com/@
```

### Reddit - pseudo

Comptes, posts et discussions publics.

```text
"pseudo_exemple" site:reddit.com/user/
```

### Reddit - nom

Mentions publiques dans les fils et commentaires indexés.

```text
"Camille Exemple" site:reddit.com
```

### Threads - pseudo

Profils et publications indexés.

```text
"pseudo_exemple" site:threads.net
```

### Bluesky - pseudo

Profils et posts publics indexés.

```text
"pseudo_exemple" site:bsky.app
```

### Mastodon - pseudo

Rechercher des profils publics sur une instance connue.

```text
"pseudo_exemple" site:mastodon.social
```

### Telegram - pseudo

Comptes ou canaux publics mentionnant ce pseudo.

```text
"pseudo_exemple" site:t.me
```

### Telegram - nom

Mentions publiques dans les canaux indexés.

```text
"Camille Exemple" site:t.me
```

### Twitch - pseudo

Chaînes et profils Twitch publics.

```text
"pseudo_exemple" site:twitch.tv
```

### Pinterest - pseudo

Profils et tableaux Pinterest publics.

```text
"pseudo_exemple" site:pinterest.com
```

### GitHub - pseudo

Comptes, dépôts et pages publiques.

```text
"pseudo_exemple" site:github.com
```

### GitLab - pseudo

Dépôts et profils techniques publics.

```text
"pseudo_exemple" site:gitlab.com
```

### Steam - pseudo

Profils Steam Community publics indexés.

```text
"pseudo_exemple" site:steamcommunity.com
```

### SoundCloud - pseudo

Profils et contenus audio publics.

```text
"pseudo_exemple" site:soundcloud.com
```

### VK - pseudo

Profils et mentions publiques du réseau VK.

```text
"pseudo_exemple" site:vk.com
```

## Identité publique - nom, surnom et recoupements

Recherches à partir des noms connus, variations d'écriture et éléments biographiques **publiquement mentionnés**.

### Nom + ville

Rechercher une personne avec le lieu connu.

```text
"Camille Exemple" "Paris"
```

### Prénom + nom + surnom

Chercher les mentions qui associent le nom au surnom.

```text
"Camille Exemple" "pseudo_exemple"
```

### Pseudo + e-mail

Chercher les pages publiant les deux identifiants.

```text
"pseudo_exemple" "exemple@example.com"
```

### Pseudo + autre pseudo

Trouver des mentions reliant deux identifiants.

```text
"pseudo_exemple" "autre_pseudo"
```

### Nom - autre graphie

Rechercher une variante orthographique ou un ancien nom publiquement employé.

```text
"Camille AutreNom"
```

### Nom + année

Rechercher les publications citant un nom à une période donnée.

```text
"Camille Exemple" "2024"
```

### Nom + date de naissance

Mentions explicites d'une date de naissance dans des sources publiques.

```text
"Camille Exemple" "date de naissance"
```

### Nom + né/née le

Rechercher les notices biographiques ouvertes.

```text
"Camille Exemple" ("né le" OR "née le")
```

### Nom + anniversaire

Rechercher des mentions publiques d'anniversaire.

```text
"Camille Exemple" "anniversaire"
```

### Nom + ancien pseudo

Rechercher les annonces publiques d'un changement d'identifiant.

```text
"Camille Exemple" "ancien pseudo"
```

### Nom + entreprise

Rechercher le nom dans le contexte d'un employeur ou projet.

```text
"Camille Exemple" "Organisation Exemple"
```

### Nom + association

Chercher des publications associatives publiques.

```text
"Camille Exemple" association
```

### Nom + conférence

Rechercher conférences, interventions et événements publics.

```text
"Camille Exemple" (conférence OR présentation OR interview)
```

## Documents publics - PDF, CV, registres et publications

Cherche les documents **indexés et accessibles publiquement** ; adapte le nom et, si besoin, le site ou le domaine.

### CV PDF

Chercher les curriculum vitae rendus publics.

```text
"Camille Exemple" (CV OR "curriculum vitae") filetype:pdf
```

### Documents Word

Chercher le nom dans des fichiers Word indexés.

```text
"Camille Exemple" filetype:docx
```

### Présentations PowerPoint

Retrouver des présentations publiques mentionnant le nom.

```text
"Camille Exemple" filetype:pptx
```

### Tableurs publics

Repérer les tableurs indexés mentionnant le nom.

```text
"Camille Exemple" filetype:xlsx
```

### Rapports publics PDF

Rechercher le nom dans les rapports publics.

```text
"Camille Exemple" rapport filetype:pdf
```

### Communiqués et bulletins

Retrouver les bulletins publics mentionnant le nom.

```text
"Camille Exemple" (communiqué OR bulletin) filetype:pdf
```

### E-mail dans les documents Word

Rechercher l'adresse dans des documents publics indexés.

```text
"exemple@example.com" filetype:docx
```

### Pseudo dans les PDF

Chercher un identifiant cité dans un document public.

```text
"pseudo_exemple" filetype:pdf
```

### Nom dans un site ciblé

Concentrer la recherche sur un site connu.

```text
"Camille Exemple" site:example.com
```

### Rapports sur un site

Trouver les PDF publics du site qui citent le nom.

```text
"Camille Exemple" site:example.com filetype:pdf
```

### Publications scientifiques HAL

Rechercher les publications et affiliations ouvertes.

```text
"Camille Exemple" site:hal.science
```

### Identifiants ORCID

Retrouver un profil de recherche public.

```text
"Camille Exemple" site:orcid.org
```

### Registre des entreprises

Retrouver les mentions publiques associées à une entreprise.

```text
"Camille Exemple" site:annuaire-entreprises.data.gouv.fr
```

### Registres d'entreprise

Rechercher les sociétés mentionnant publiquement ce nom.

```text
"Camille Exemple" site:pappers.fr
```

### Presse locale et archives

Retrouver les articles publics associés à un nom et un lieu.

```text
"Camille Exemple" "Paris" (article OR presse)
```

## Pseudonyme - rechercher les comptes

Après les premières occurrences, vérifie les profils sur plusieurs plateformes et exporte les résultats.

### Sherlock - recherche simple

Recherche sur les plateformes connues de Sherlock.

```bash
sherlock pseudo_exemple
```

### Sherlock - résultats trouvés

Masquer les sites où aucun profil n'a été signalé.

```bash
sherlock pseudo_exemple --print-found
```

### Sherlock - une plateforme

Limiter les requêtes à GitHub.

```bash
sherlock pseudo_exemple --site GitHub --print-found
```

### Sherlock - enregistrer en texte

Conserver un rapport des résultats.

```bash
sherlock pseudo_exemple --output sherlock-pseudo_exemple.txt
```

### Sherlock - CSV

Produire un tableau des résultats.

```bash
sherlock pseudo_exemple --csv
```

### Sherlock - comparer plusieurs pseudos

Vérifier plusieurs variantes sans générer de noms au hasard.

```bash
sherlock pseudo_exemple pseudo_variante --print-found
```

### Maigret - recherche rapide

Chercher les comptes correspondant à un identifiant.

```bash
maigret pseudo_exemple
```

### Maigret - sites principaux

Limiter la recherche à un ensemble de sites mieux classés.

```bash
maigret pseudo_exemple --top-sites 100
```

### Maigret - catégories

Restreindre à des plateformes liées à la photo.

```bash
maigret pseudo_exemple --tags photo
```

### Maigret - HTML

Générer un rapport navigable.

```bash
maigret pseudo_exemple --html
```

### Maigret - CSV

Exporter les résultats au format tableur.

```bash
maigret pseudo_exemple --csv
```

### Maigret - JSON

Exporter les résultats au format structuré.

```bash
maigret pseudo_exemple --json simple
```

### Maigret - fichier de pseudos

Rechercher les identifiants listés un par ligne.

```bash
maigret --input-file pseudos.txt --html
```

### Blackbird - pseudonyme

Cherche les comptes publics correspondant au pseudo.

```bash
"$HOME/.venvs/blackbird/bin/python" "$HOME/outils/blackbird/blackbird.py" --username pseudo_exemple
```

### Blackbird - export JSON

Enregistre les profils trouvés au format JSON.

```bash
"$HOME/.venvs/blackbird/bin/python" "$HOME/outils/blackbird/blackbird.py" --username pseudo_exemple --json
```

## E-mail - rechercher les comptes

Vérifie les traces d'un e-mail déjà trouvé dans une publication ou un profil.

### Holehe - recherche par e-mail

Tester une adresse de démonstration ou appartenant au périmètre autorisé.

```bash
"$HOME/.venvs/holehe/bin/holehe" exemple@example.com
```

### Holehe - vérifier la version

Lire les options présentes sur l'installation locale.

```bash
"$HOME/.venvs/holehe/bin/holehe" --help
```

### Blackbird - e-mail

Cherche les profils publics associés à une adresse.

```bash
"$HOME/.venvs/blackbird/bin/python" "$HOME/outils/blackbird/blackbird.py" --email exemple@example.com
```

## Téléphonie - annuaires publics

Consulte les informations publiques disponibles sur un numéro. Les résultats d'un annuaire sont des indices à recouper, pas une preuve d'identité.

- [Truecaller](https://www.truecaller.com/) - informations et signalements associés à un numéro.
- [Infobel](https://www.infobel.com/) - annuaires téléphoniques et professionnels.

## Domaine - commencer par le DNS

Quand tu obtiens un domaine, vérifie ses enregistrements publics avant d'aller plus loin.

### WHOIS

Afficher les informations d'enregistrement disponibles.

```bash
whois example.com
```

### IPv4

Afficher les enregistrements A.

```bash
dig example.com A +short
```

### IPv6

Afficher les enregistrements AAAA.

```bash
dig example.com AAAA +short
```

### Serveurs de messagerie

Identifier les MX déclarés.

```bash
dig example.com MX +short
```

### Serveurs de noms

Identifier les NS déclarés.

```bash
dig example.com NS +short
```

### TXT et SPF

Lire les politiques et autres TXT publiés.

```bash
dig example.com TXT +short
```

### DMARC

Lire la politique de messagerie DMARC.

```bash
dig _dmarc.example.com TXT +short
```

### CAA

Voir les autorités de certification déclarées.

```bash
dig example.com CAA +short
```

### DNS inverse

Trouver le PTR éventuellement déclaré pour une IP.

```bash
dig -x 8.8.8.8 +short
```

### Certificat TLS

Afficher sujet, émetteur et dates du certificat présenté.

```bash
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```

### SOA - zone DNS

Affiche les informations de gestion de zone publiées.

```bash
dig example.com SOA +short
```

## Domaine - trouver les sous-domaines

Croise les certificats, les sources passives et les domaines ressemblants. Certaines sources nécessitent une clé API.

### theHarvester - certificats publics

Utiliser crt.sh et CertSpotter.

```bash
(cd "$HOME/outils/theHarvester" && uv run theHarvester -d example.com -b crtsh,certspotter)
```

### theHarvester - plusieurs sources

Comparer certificats et Common Crawl.

```bash
(cd "$HOME/outils/theHarvester" && uv run theHarvester -d example.com -b crtsh,certspotter,commoncrawl)
```

### theHarvester - rechercher les e-mails

Chercher les adresses publiques et les URL associées.

```bash
(cd "$HOME/outils/theHarvester" && uv run theHarvester -d example.com -b emails,urls,certspotter)
```

### theHarvester - exporter

Sauvegarder les rapports locaux selon les formats du projet.

```bash
(cd "$HOME/outils/theHarvester" && uv run theHarvester -d example.com -b crtsh,certspotter -f example.com-rapport)
```

### Subfinder - sous-domaines passifs

Collecter les noms publics, sans scan de ports.

```bash
"$HOME/go/bin/subfinder" -d example.com -silent -o sous-domaines.txt
```

### crt.sh - certificats en JSON

Extraire les noms des certificats ; le service peut limiter les requêtes.

```bash
curl -fsSG --data-urlencode "q=%.example.com" --data-urlencode "output=json" https://crt.sh/ | jq -r '.[].name_value' | sort -u
```

### Amass - passif

Recherche des sous-domaines en mode passif et enregistre le résultat.

```bash
amass enum -passive -d example.com -o amass-resultats.txt
```

### dnstwist - domaines similaires

Vérifie les domaines ressemblants déjà enregistrés.

```bash
dnstwist --registered example.com
```

### dnstwist - exporter

Exporte les domaines ressemblants au format CSV.

```bash
dnstwist --format csv example.com > domaines-similaires.csv
```

### Fierce - DNS

Recherche des noms d'hôtes par requêtes DNS dans le périmètre autorisé.

```bash
fierce --domain example.com --subdomains mail
```

### Recon-ng - espace de travail

Ouvre un espace de travail Recon-ng pour regrouper les recherches.

```bash
recon-ng -w enquete-exemple
```

### SpiderFoot - collecte passive

Exécute une collecte OSINT passive et affiche le résultat en CSV.

```bash
spiderfoot -s example.com -u passive -o csv
```

## Site Web et archives - retrouver les versions précédentes

Quand tu as une URL, regarde sa réponse HTTP, ses archives et les services indexés.

### Wayback Machine - ouvrir les archives

Ouvrir les versions disponibles d'un domaine dans le navigateur.

```bash
xdg-open 'https://web.archive.org/web/*/example.com'
```

### En-têtes HTTP

Examiner les en-têtes d'une URL publique.

```bash
curl -sSI --max-time 15 https://example.com/
```

### Redirection HTTP

Voir le code final et l'URL obtenue.

```bash
curl -sSL -o /dev/null -w '%{http_code} %{url_effective}\n' https://example.com/
```

### Enregistrer le HTML d'une page

Conserver une copie locale du HTML public.

```bash
curl -sSL --max-time 20 https://example.com/ -o page.html
```

### Rechercher un terme dans le HTML

Filtrer un fichier sauvegardé par mots-clés.

```bash
grep -inF contact page.html
```

### WhatWeb - identifier les technologies d'un site

Repérer les technologies visibles d'un site Web. Limiter l'usage aux domaines du périmètre autorisé.

```bash
whatweb https://example.com
```

### Shodan - rechercher un domaine

Ouvrir une requête ciblée dans le moteur Shodan.

```bash
xdg-open 'https://www.shodan.io/search?query=hostname%3Aexample.com'
```

### urlscan.io - domaine

Ouvrir une recherche d'observations associées au domaine.

```bash
xdg-open 'https://urlscan.io/search/#domain%3Aexample.com'
```

### Photon - explorer un site

Explore un niveau de pages publiques sur un site dont l'exploration est autorisée.

```bash
"$HOME/.venvs/photon/bin/python" "$HOME/outils/Photon/photon.py" -u https://example.com/ -l 1
```

## Images et documents - exploiter les fichiers

Examiner les métadonnées des fichiers trouvés au cours de l'enquête.

### Type réel du fichier

Identifier le format reconnu par l'outil file.

```bash
file photo.jpg
```

### Métadonnées de l'image

Afficher toutes les métadonnées lisibles d'un fichier.

```bash
exiftool photo.jpg
```

### Métadonnées par groupe

Voir les groupes de tags et leurs noms techniques.

```bash
exiftool -G1 -a -s photo.jpg
```

### Champs GPS

Afficher les champs GPS présents dans le fichier.

```bash
exiftool -GPS:all photo.jpg
```

### Exporter les métadonnées

Créer un export JSON local.

```bash
exiftool -json photo.jpg > metadonnees.json
```

### Informations d'un PDF

Lire le producteur et les autres champs PDF disponibles.

```bash
pdfinfo document.pdf
```

### Texte d'un PDF

Extraire le texte d'un PDF textuel ; n'effectue pas d'OCR.

```bash
pdftotext -layout document.pdf document.txt
```

### Dates EXIF

Affiche les champs de dates disponibles dans une image.

```bash
exiftool -time:all -G1 -s photo.jpg
```

### Métadonnées d'un dossier

Exporte les métadonnées de plusieurs images au format CSV.

```bash
exiftool -csv -r dossier_images/ > images-metadonnees.csv
```

## Photos et vidéos - analyser un fichier

ExifTool lit les métadonnées disponibles dans les photos et vidéos.

### Photo - toutes les métadonnées

Lire les champs disponibles, avec leur groupe et les doublons.

```bash
exiftool -a -G1 -s "photo.jpg"
```

### Vidéo - toutes les métadonnées

Lire les champs présents dans la vidéo et son conteneur.

```bash
exiftool -a -G1 -s "video.mp4"
```

### Photo - GPS

Afficher les coordonnées GPS présentes, si elles existent.

```bash
exiftool -a -G1 -s -GPS:all "photo.jpg"
```

### Vidéo - GPS

Afficher les éventuelles métadonnées de localisation.

```bash
exiftool -a -G1 -s -GPS:all "video.mp4"
```

### Photo - date et appareil

Afficher les champs de date et le modèle de l’appareil.

```bash
exiftool -a -G1 -s -time:all -Make -Model -Software "photo.jpg"
```

### Vidéo - dates

Afficher les dates et le logiciel déclarés dans les métadonnées.

```bash
exiftool -a -G1 -s -time:all -Software "video.mp4"
```

### Vidéo - FFprobe en JSON

Extraire les pistes, codecs, résolution, durée et informations de conteneur.

```bash
ffprobe -v error -show_format -show_streams -of json "video.mp4" > video-ffprobe.json
```

### Vidéo - MediaInfo en JSON

Exporter les informations techniques des pistes vidéo et audio.

```bash
mediainfo --Output=JSON "video.mp4" > video-mediainfo.json
```

## Dossiers complets - analyse récursive

Remplace uniquement `/chemin/du/dossier` par le chemin réel. L'option `-r` parcourt également les sous-dossiers. Ces commandes ne modifient pas les fichiers d'origine.

### Analyser tous les fichiers

Lire les métadonnées des fichiers reconnus, sous-dossiers compris.

```bash
exiftool -r -a -G1 -s "/chemin/du/dossier/"
```

### Rapport texte complet

Enregistrer les métadonnées dans un fichier texte.

```bash
exiftool -r -a -G1 -s "/chemin/du/dossier/" > rapport-metadonnees.txt
```

### Rapport JSON complet

Exporter les métadonnées dans un fichier JSON.

```bash
exiftool -r -j -G1 "/chemin/du/dossier/" > rapport-metadonnees.json
```

### Rapport CSV complet

Créer un tableau de métadonnées de tous les fichiers reconnus.

```bash
exiftool -r -csv "/chemin/du/dossier/" > rapport-metadonnees.csv
```

### Photos et vidéos uniquement

Limiter le rapport CSV aux formats photo et vidéo indiqués.

```bash
exiftool -r -csv -ext jpg -ext jpeg -ext png -ext heic -ext webp -ext gif -ext tif -ext mp4 -ext mov -ext avi -ext mkv -ext webm "/chemin/du/dossier/" > rapport-medias.csv
```

### GPS de tout le dossier

Extraire les coordonnées et autres champs GPS disponibles.

```bash
exiftool -r -a -G1 -s -GPS:all "/chemin/du/dossier/" > rapport-gps.txt
```

### Dates de tout le dossier

Extraire les dates renseignées dans les métadonnées.

```bash
exiftool -r -a -G1 -s -time:all "/chemin/du/dossier/" > rapport-dates.txt
```

### Vidéos - rapport MediaInfo

Analyser toutes les vidéos prises en charge dans les sous-dossiers.

```bash
find "/chemin/du/dossier/" -type f \( -iname '*.mp4' -o -iname '*.mov' -o -iname '*.mkv' -o -iname '*.avi' -o -iname '*.webm' \) -exec mediainfo '{}' \; > rapport-videos-mediainfo.txt
```

### Vidéos - rapport FFprobe

Extraire les pistes et informations des fichiers vidéo trouvés.

```bash
find "/chemin/du/dossier/" -type f \( -iname '*.mp4' -o -iname '*.mov' -o -iname '*.mkv' -o -iname '*.avi' -o -iname '*.webm' \) -exec ffprobe -v error -show_format -show_streams '{}' \; > rapport-videos-ffprobe.txt
```

### Empreintes SHA-256 du dossier

Créer un inventaire des empreintes sans modifier les fichiers.

```bash
find "/chemin/du/dossier/" -type f -print0 | sort -z | xargs -0 -r sha256sum > rapport-sha256.txt
```

## Réseaux sans fil - observations publiques

[WiGLE](https://wigle.net/) permet de consulter des observations géolocalisées de réseaux Wi-Fi et Bluetooth. Une observation peut être ancienne et ne prouve pas qu'un réseau se trouve toujours au même endroit.

## Exporter les résultats

Enregistrer les résultats au fur et à mesure des recherches.

### Sauver une recherche Sherlock

Afficher et enregistrer simultanément la sortie standard.

```bash
sherlock pseudo_exemple --print-found | tee rapport-sherlock.txt
```

### Empreinte SHA-256

Conserver l'empreinte d'un fichier de travail.

```bash
sha256sum capture.png > capture.png.sha256
```

### Vérifier l'empreinte

Vérifier qu'un fichier est identique à la version enregistrée.

```bash
sha256sum -c capture.png.sha256
```

### Dédoublonner une liste

Trier les résultats en supprimant les lignes identiques.

```bash
sort -u sous-domaines.txt > liste-unique.txt
```

### Chercher un terme dans les notes

Afficher les lignes et numéros où apparaît le mot.

```bash
grep -inF domaine notes.txt
```

### Inventaire des fichiers

Liste les fichiers enregistrés pour l'enquête.

```bash
find dossier_osint -type f | sort
```

### Exporter les MX

Enregistre les serveurs de messagerie dans le dossier de rapports.

```bash
dig example.com MX +short | tee dossier_osint/rapports/dns-mx.txt
```


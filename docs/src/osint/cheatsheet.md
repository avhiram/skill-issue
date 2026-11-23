---
title: OSINT - Cheatsheet
description: Commandes OSINT prêtes à copier pour la recherche en sources ouvertes.
aside: false
prev: false
next: false
---

# Cheatsheet OSINT

Remplace `PSEUDO`, `EMAIL`, `PRENOM`, `NOM`, `DOMAINE`, `URL` ou `FICHIER`, puis copie la commande. Les dorks ouvrent Google dans ton navigateur.

[Revenir à la bibliothèque OSINT](./index.md)

## Installer les outils

Installation sous Kali, Debian ou Ubuntu. À exécuter une fois. Les exemples utilisent ensuite les mêmes chemins.

### Utilitaires de base

```bash
# Installer les outils de recherche, de métadonnées et de rapports.
sudo apt update && sudo apt install -y git curl jq whois dnsutils openssl pipx python3-venv libimage-exiftool-perl poppler-utils
```

### Préparer les applications Python

```bash
# Ajouter au PATH les programmes installés par pipx.
pipx ensurepath
```

### Sherlock

```bash
# Installer l'outil de recherche de pseudonymes.
pipx install sherlock-project
```

### Maigret

```bash
# Installer Maigret et ses fonctions d'export.
pipx install maigret
```

### Holehe

```bash
# Installer Holehe dans un environnement séparé.
python3 -m venv "$HOME/.venvs/holehe"
"$HOME/.venvs/holehe/bin/pip" install holehe
```

### uv

```bash
# Installer le gestionnaire utilisé par theHarvester actuel.
pipx install uv
```

### theHarvester

```bash
# Installer la version du dépôt ; uv choisit ses dépendances et son Python.
mkdir -p "$HOME/outils"
git clone https://github.com/laramies/theHarvester.git "$HOME/outils/theHarvester"
(cd "$HOME/outils/theHarvester" && uv sync)
```

### Subfinder - facultatif

```bash
# Installer avec Go déjà présent sur le poste.
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
export PATH="$PATH:$HOME/go/bin"
```

## Dorks - pseudonyme

Chaque bloc ouvre une recherche Google. Remplace seulement la valeur de PSEUDO.

### Occurrences exactes

```bash
# Retrouver les pages publiques qui contiennent le pseudo.
PSEUDO="pseudo_exemple"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$PSEUDO\""
```

### Profils GitHub

```bash
# Rechercher ce pseudo sur GitHub indexé.
PSEUDO="pseudo_exemple"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$PSEUDO\" site:github.com"
```

### Discussions Reddit

```bash
# Rechercher les mentions du pseudo sur Reddit.
PSEUDO="pseudo_exemple"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$PSEUDO\" site:reddit.com"
```

### Profils LinkedIn

```bash
# Chercher un profil public portant le même identifiant.
PSEUDO="pseudo_exemple"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$PSEUDO\" site:linkedin.com/in/"
```

### Forums et communautés

```bash
# Retrouver des messages associés au pseudo.
PSEUDO="pseudo_exemple"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$PSEUDO\" (forum OR discussion OR communauté)"
```

## Dorks - adresse e-mail

Recherche d'occurrences publiques. Remplace EMAIL ; les résultats n'établissent pas à eux seuls qui détient le compte.

### Occurrences exactes d'un e-mail

```bash
# Chercher l'adresse exacte dans les pages indexées.
EMAIL="exemple@example.com"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$EMAIL\""
```

### E-mail dans les PDF

```bash
# Rechercher les documents publics où l'adresse apparaît.
EMAIL="exemple@example.com"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$EMAIL\" filetype:pdf"
```

### E-mail sur les plateformes de code

```bash
# Rechercher les pages de code indexées contenant l'adresse.
EMAIL="exemple@example.com"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$EMAIL\" (site:github.com OR site:gitlab.com)"
```

## Dorks - prénom et nom

Deux champs à remplacer : PRENOM et NOM. Les homonymes imposent un recoupement.

### Nom exact

```bash
# Rechercher le nom complet avec des guillemets.
PRENOM="Camille"
NOM="Exemple"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$PRENOM $NOM\""
```

### Documents PDF

```bash
# Repérer des documents publics associés au nom.
PRENOM="Camille"
NOM="Exemple"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$PRENOM $NOM\" filetype:pdf"
```

### Profils professionnels

```bash
# Chercher des profils LinkedIn indexés au même nom.
PRENOM="Camille"
NOM="Exemple"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$PRENOM $NOM\" site:linkedin.com/in/"
```

### Presse et interviews

```bash
# Repérer des publications qui mentionnent le nom.
PRENOM="Camille"
NOM="Exemple"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$PRENOM $NOM\" (interview OR conférence OR article)"
```

### Nom et organisation

```bash
# Recouper le nom avec une organisation déclarée.
PRENOM="Camille"
NOM="Exemple"
ORGANISATION="Organisation Exemple"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$PRENOM $NOM\" \"$ORGANISATION\""
```

## Dorks - domaine et organisation

Remplace DOMAINE ou ORGANISATION par la valeur recherchée.

### Pages indexées

```bash
# Lister les pages publiques d'un domaine.
DOMAINE="example.com"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "site:$DOMAINE"
```

### Documents PDF

```bash
# Trouver les documents PDF publics du domaine.
DOMAINE="example.com"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "site:$DOMAINE filetype:pdf"
```

### Documents bureautiques

```bash
# Trouver les feuilles de calcul publiquement indexées.
DOMAINE="example.com"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "site:$DOMAINE filetype:xlsx"
```

### Pages de contact

```bash
# Rechercher les pages contact ou à propos.
DOMAINE="example.com"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "site:$DOMAINE (inurl:contact OR inurl:about)"
```

### Sous-domaines indexés

```bash
# Repérer certaines pages hors du sous-domaine www ; résultat non exhaustif.
DOMAINE="example.com"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "site:$DOMAINE -site:www.$DOMAINE"
```

### Mentions externes d'une organisation

```bash
# Identifier des pages extérieures au site principal.
ORGANISATION="Organisation Exemple"
DOMAINE="example.com"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$ORGANISATION\" -site:$DOMAINE"
```

### Mentions récentes

```bash
# Filtrer les publications selon une date de début à adapter.
ORGANISATION="Organisation Exemple"
python3 -c 'import sys, urllib.parse as u, webbrowser; webbrowser.open("https://www.google.com/search?q=" + u.quote(sys.argv[1]))' "\"$ORGANISATION\" after:2026-01-01"
```

## Pseudonymes - Sherlock et Maigret

Recherche de profils publics et exports.

### Sherlock - recherche simple

```bash
# Recherche sur les plateformes connues de Sherlock.
PSEUDO="pseudo_exemple"
sherlock "$PSEUDO"
```

### Sherlock - résultats trouvés

```bash
# Masquer les sites où aucun profil n'a été signalé.
PSEUDO="pseudo_exemple"
sherlock "$PSEUDO" --print-found
```

### Sherlock - une plateforme

```bash
# Limiter les requêtes à GitHub.
PSEUDO="pseudo_exemple"
sherlock "$PSEUDO" --site GitHub --print-found
```

### Sherlock - enregistrer en texte

```bash
# Conserver un rapport des résultats.
PSEUDO="pseudo_exemple"
sherlock "$PSEUDO" --output "sherlock-$PSEUDO.txt"
```

### Sherlock - CSV

```bash
# Produire un tableau des résultats.
PSEUDO="pseudo_exemple"
sherlock "$PSEUDO" --csv
```

### Sherlock - comparer plusieurs pseudos

```bash
# Vérifier plusieurs variantes sans générer de noms au hasard.
PSEUDO1="pseudo_exemple"
PSEUDO2="pseudo_variante"
sherlock "$PSEUDO1" "$PSEUDO2" --print-found
```

### Maigret - recherche rapide

```bash
# Chercher les comptes correspondant à un identifiant.
PSEUDO="pseudo_exemple"
maigret "$PSEUDO"
```

### Maigret - sites principaux

```bash
# Limiter la recherche à un ensemble de sites mieux classés.
PSEUDO="pseudo_exemple"
maigret "$PSEUDO" --top-sites 100
```

### Maigret - catégories

```bash
# Restreindre à des plateformes liées à la photo.
PSEUDO="pseudo_exemple"
maigret "$PSEUDO" --tags photo
```

### Maigret - HTML

```bash
# Générer un rapport navigable.
PSEUDO="pseudo_exemple"
maigret "$PSEUDO" --html
```

### Maigret - CSV

```bash
# Exporter les résultats au format tableur.
PSEUDO="pseudo_exemple"
maigret "$PSEUDO" --csv
```

### Maigret - JSON

```bash
# Exporter les résultats au format structuré.
PSEUDO="pseudo_exemple"
maigret "$PSEUDO" --json simple
```

### Maigret - fichier de pseudos

```bash
# Rechercher les identifiants listés un par ligne.
FICHIER="pseudos.txt"
maigret --input-file "$FICHIER" --html
```

## Adresse e-mail - Holehe

Recherche d'inscriptions associées à un e-mail.

### Holehe - recherche par e-mail

```bash
# Tester une adresse de démonstration ou appartenant au périmètre autorisé.
EMAIL="exemple@example.com"
"$HOME/.venvs/holehe/bin/holehe" "$EMAIL"
```

### Holehe - vérifier la version

```bash
# Lire les options présentes sur l'installation locale.
"$HOME/.venvs/holehe/bin/holehe" --help
```

## Domaines - theHarvester et Subfinder

Choisir d'abord les sources passives. Les requêtes vont aux fournisseurs de données, pas nécessairement à la cible.

### theHarvester - certificats publics

```bash
# Utiliser crt.sh et CertSpotter.
DOMAINE="example.com"
(cd "$HOME/outils/theHarvester" && uv run theHarvester -d "$DOMAINE" -b crtsh,certspotter)
```

### theHarvester - plusieurs sources

```bash
# Comparer certificats et Common Crawl.
DOMAINE="example.com"
(cd "$HOME/outils/theHarvester" && uv run theHarvester -d "$DOMAINE" -b crtsh,certspotter,commoncrawl)
```

### theHarvester - rechercher les e-mails

```bash
# Chercher les adresses publiques et les URL associées.
DOMAINE="example.com"
(cd "$HOME/outils/theHarvester" && uv run theHarvester -d "$DOMAINE" -b emails,urls,certspotter)
```

### theHarvester - exporter

```bash
# Sauvegarder les rapports locaux selon les formats du projet.
DOMAINE="example.com"
(cd "$HOME/outils/theHarvester" && uv run theHarvester -d "$DOMAINE" -b crtsh,certspotter -f "$DOMAINE-rapport")
```

### Subfinder - sous-domaines passifs

```bash
# Collecter les noms publics, sans scan de ports.
DOMAINE="example.com"
subfinder -d "$DOMAINE" -silent -o sous-domaines.txt
```

### crt.sh - certificats en JSON

```bash
# Extraire les noms des certificats ; le service peut limiter les requêtes.
DOMAINE="example.com"
curl -fsSG --data-urlencode "q=%.$DOMAINE" --data-urlencode "output=json" https://crt.sh/ | jq -r '.[].name_value' | sort -u
```

## Domaines - DNS, WHOIS et TLS

Commandes système simples pour comprendre les informations d'un domaine.

### WHOIS

```bash
# Afficher les informations d'enregistrement disponibles.
DOMAINE="example.com"
whois "$DOMAINE"
```

### IPv4

```bash
# Afficher les enregistrements A.
DOMAINE="example.com"
dig "$DOMAINE" A +short
```

### IPv6

```bash
# Afficher les enregistrements AAAA.
DOMAINE="example.com"
dig "$DOMAINE" AAAA +short
```

### Serveurs de messagerie

```bash
# Identifier les MX déclarés.
DOMAINE="example.com"
dig "$DOMAINE" MX +short
```

### Serveurs de noms

```bash
# Identifier les NS déclarés.
DOMAINE="example.com"
dig "$DOMAINE" NS +short
```

### TXT et SPF

```bash
# Lire les politiques et autres TXT publiés.
DOMAINE="example.com"
dig "$DOMAINE" TXT +short
```

### DMARC

```bash
# Lire la politique de messagerie DMARC.
DOMAINE="example.com"
dig "_dmarc.$DOMAINE" TXT +short
```

### CAA

```bash
# Voir les autorités de certification déclarées.
DOMAINE="example.com"
dig "$DOMAINE" CAA +short
```

### DNS inverse

```bash
# Trouver le PTR éventuellement déclaré pour une IP.
IP="8.8.8.8"
dig -x "$IP" +short
```

### Certificat TLS

```bash
# Afficher sujet, émetteur et dates du certificat présenté.
DOMAINE="example.com"
openssl s_client -connect "$DOMAINE:443" -servername "$DOMAINE" </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```

## Archives, sites Web et données publiques

Pour les pages Web, conserver l'URL et la date ; les réponses HTTP peuvent changer.

### Wayback Machine - ouvrir les archives

```bash
# Ouvrir les versions disponibles d'un domaine dans le navigateur.
DOMAINE="example.com"
python3 -c 'import sys,webbrowser;webbrowser.open("https://web.archive.org/web/*/"+sys.argv[1])' "$DOMAINE"
```

### En-têtes HTTP

```bash
# Examiner les en-têtes d'une URL publique.
URL="https://example.com/"
curl -sSI --max-time 15 "$URL"
```

### Redirection HTTP

```bash
# Voir le code final et l'URL obtenue.
URL="https://example.com/"
curl -sSL -o /dev/null -w '%{http_code} %{url_effective}\n' "$URL"
```

### Enregistrer le HTML d'une page

```bash
# Conserver une copie locale du HTML public.
URL="https://example.com/"
curl -sSL --max-time 20 "$URL" -o page.html
```

### Rechercher un terme dans le HTML

```bash
# Filtrer un fichier sauvegardé par mots-clés.
MOT="contact"
grep -inF "$MOT" page.html
```

### Shodan - rechercher un domaine

```bash
# Ouvrir une requête ciblée dans le moteur Shodan.
DOMAINE="example.com"
python3 -c 'import sys,urllib.parse as u,webbrowser;webbrowser.open("https://www.shodan.io/search?query="+u.quote("hostname:"+sys.argv[1]))' "$DOMAINE"
```

### urlscan.io - domaine

```bash
# Ouvrir une recherche d'observations associées au domaine.
DOMAINE="example.com"
python3 -c 'import sys,urllib.parse as u,webbrowser;webbrowser.open("https://urlscan.io/search/#"+u.quote("domain:"+sys.argv[1]))' "$DOMAINE"
```

## Images et documents

Examiner la copie locale de l'image ou du document. Les métadonnées peuvent être absentes ou modifiées.

### Type réel du fichier

```bash
# Identifier le format reconnu par l'outil file.
FICHIER="photo.jpg"
file "$FICHIER"
```

### Métadonnées de l'image

```bash
# Afficher toutes les métadonnées lisibles d'un fichier.
FICHIER="photo.jpg"
exiftool "$FICHIER"
```

### Métadonnées par groupe

```bash
# Voir les groupes de tags et leurs noms techniques.
FICHIER="photo.jpg"
exiftool -G1 -a -s "$FICHIER"
```

### Champs GPS

```bash
# Afficher les champs GPS présents dans le fichier.
FICHIER="photo.jpg"
exiftool -GPS:all "$FICHIER"
```

### Exporter les métadonnées

```bash
# Créer un export JSON local.
FICHIER="photo.jpg"
exiftool -json "$FICHIER" > metadonnees.json
```

### Informations d'un PDF

```bash
# Lire le producteur et les autres champs PDF disponibles.
FICHIER="document.pdf"
pdfinfo "$FICHIER"
```

### Texte d'un PDF

```bash
# Extraire le texte d'un PDF textuel ; n'effectue pas d'OCR.
FICHIER="document.pdf"
pdftotext -layout "$FICHIER" document.txt
```

## Fichiers et exports

### Préparer un dossier

```bash
# Créer une structure simple pour les fichiers de travail.
mkdir -p dossier_osint/{notes,captures,rapports,documents}
```

### Heure d'observation

```bash
# Afficher l'heure UTC au format ISO 8601.
date -u '+%Y-%m-%dT%H:%M:%SZ'
```

### Sauver une recherche Sherlock

```bash
# Afficher et enregistrer simultanément la sortie standard.
PSEUDO="pseudo_exemple"
sherlock "$PSEUDO" --print-found | tee rapport-sherlock.txt
```

### Empreinte SHA-256

```bash
# Conserver l'empreinte d'un fichier de travail.
FICHIER="capture.png"
sha256sum "$FICHIER" > "$FICHIER.sha256"
```

### Vérifier l'empreinte

```bash
# Vérifier qu'un fichier est identique à la version enregistrée.
EMPREINTE="capture.png.sha256"
sha256sum -c "$EMPREINTE"
```

### Dédoublonner une liste

```bash
# Trier les résultats en supprimant les lignes identiques.
FICHIER="sous-domaines.txt"
sort -u "$FICHIER" > liste-unique.txt
```

### Chercher un terme dans les notes

```bash
# Afficher les lignes et numéros où apparaît le mot.
MOT="domaine"
grep -inF "$MOT" notes.txt
```

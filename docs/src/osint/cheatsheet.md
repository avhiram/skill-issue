---
title: OSINT - Cheatsheet
description: Commandes OSINT prêtes à copier pour la recherche en sources ouvertes.
aside: false
prev: false
next: false
---

# Cheatsheet OSINT

Remplace directement le pseudo, l’e-mail, le nom ou le domaine dans la commande. Pour les dorks, colle la requête dans Google.

[Revenir à la bibliothèque OSINT](./index.md)

## Installer les outils

Installation sous Kali, Debian ou Ubuntu. À exécuter une fois. Les exemples utilisent ensuite les mêmes chemins.

### Utilitaires de base

Installer les outils de recherche, de métadonnées et de rapports.

```bash
sudo apt update && sudo apt install -y git curl jq whois dnsutils openssl pipx python3-venv libimage-exiftool-perl poppler-utils
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

### Subfinder - facultatif

Installer avec Go déjà présent sur le poste.

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

## Dorks - pseudonyme

Chaque bloc ouvre une recherche Google. Remplace seulement la valeur de PSEUDO.

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

## Dorks - adresse e-mail

Recherche d'occurrences publiques. Remplace EMAIL ; les résultats n'établissent pas à eux seuls qui détient le compte.

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

## Dorks - prénom et nom

Deux champs à remplacer : PRENOM et NOM. Les homonymes imposent un recoupement.

### Nom exact

Rechercher le nom complet avec des guillemets.

```text
"Camille Exemple"
```

### Documents PDF

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

## Dorks - domaine et organisation

Remplace DOMAINE ou ORGANISATION par la valeur recherchée.

### Pages indexées

Lister les pages publiques d'un domaine.

```text
site:example.com
```

### Documents PDF

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

## Pseudonymes - Sherlock et Maigret

Recherche de profils publics et exports.

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

## Adresse e-mail - Holehe

Recherche d'inscriptions associées à un e-mail.

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

## Domaines - theHarvester et Subfinder

Choisir d'abord les sources passives. Les requêtes vont aux fournisseurs de données, pas nécessairement à la cible.

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

## Domaines - DNS, WHOIS et TLS

Commandes système simples pour comprendre les informations d'un domaine.

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

## Archives, sites Web et données publiques

Pour les pages Web, conserver l'URL et la date ; les réponses HTTP peuvent changer.

### Wayback Machine - ouvrir les archives

Ouvrir les versions disponibles d'un domaine dans le navigateur.

```bash
python3 -c 'import sys,webbrowser;webbrowser.open("https://web.archive.org/web/*/"+sys.argv[1])' example.com
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

### Shodan - rechercher un domaine

Ouvrir une requête ciblée dans le moteur Shodan.

```bash
python3 -c 'import sys,urllib.parse as u,webbrowser;webbrowser.open("https://www.shodan.io/search?query="+u.quote("hostname:"+sys.argv[1]))' example.com
```

### urlscan.io - domaine

Ouvrir une recherche d'observations associées au domaine.

```bash
python3 -c 'import sys,urllib.parse as u,webbrowser;webbrowser.open("https://urlscan.io/search/#"+u.quote("domain:"+sys.argv[1]))' example.com
```

## Images et documents

Examiner la copie locale de l'image ou du document. Les métadonnées peuvent être absentes ou modifiées.

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

## Fichiers et exports

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

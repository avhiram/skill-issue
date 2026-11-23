---
title: OSINT - Cheatsheet
description: Commandes essentielles de reconnaissance OSINT, expliquées en français.
aside: false
prev: false
next: false
---

# Cheatsheet OSINT

Une sélection de commandes pour la **recherche de comptes**, la **reconnaissance de domaines** et la **conservation de résultats**.

[Retour aux outils](./index.md) · [Générateur de dorks](./index.md#générateur-de-dorks)

Les exemples utilisent des identifiants fictifs et le domaine `example.com`.

## Installer les outils

Sous Kali, Debian ou Ubuntu. Les commandes d'installation ne sont à exécuter qu'une fois.

### Installer les utilitaires système

~~~bash
sudo apt update && sudo apt install -y git pipx python3-venv whois dnsutils curl jq libimage-exiftool-perl poppler-utils
# Installe Git, les outils DNS, WHOIS, JSON, métadonnées et PDF.
~~~

### Activer les commandes pipx

~~~bash
pipx ensurepath
# Ajoute les commandes des applications Python installées par pipx au PATH (rouvrir le terminal si nécessaire).
~~~

### Installer Sherlock

~~~bash
pipx install sherlock-project
# Installe Sherlock dans un environnement Python isolé.
~~~

### Installer Maigret

~~~bash
pipx install maigret
# Installe Maigret dans un environnement Python isolé.
~~~

### Créer un environnement pour Holehe

~~~bash
python3 -m venv ~/.venvs/holehe
# Prépare un environnement Python dédié à Holehe.
~~~

### Installer Holehe

~~~bash
~/.venvs/holehe/bin/pip install holehe
# Installe Holehe dans l'environnement dédié.
~~~

### Récupérer theHarvester

~~~bash
git clone https://github.com/laramies/theHarvester.git
# Récupère les sources officielles de theHarvester.
~~~

**Installer uv**

~~~bash
pipx install uv
# Installe uv pour lancer la version actuelle de theHarvester.
~~~

### Installer les dépendances theHarvester

Dans le dossier du dépôt cloné, uv utilise la version Python et les dépendances définies par le projet.

~~~bash
cd theHarvester && uv sync
# Installe les dépendances depuis le dépôt ; nécessite uv et la version Python demandée par le projet.
~~~

## Rechercher un pseudonyme

Sherlock et Maigret recherchent des profils publics ; Holehe fournit des indices d'inscription liés à une adresse e-mail. **Un résultat ne prouve pas une identité.**

### Rechercher un pseudonyme

~~~bash
sherlock pseudo_exemple
# Cherche les comptes publics correspondant au pseudonyme.
~~~

### Afficher uniquement les résultats positifs

~~~bash
sherlock pseudo_exemple --print-found
# Affiche les sites où Sherlock signale un compte.
~~~

### Enregistrer un rapport texte

~~~bash
sherlock pseudo_exemple --output sherlock-resultats.txt
# Enregistre les profils identifiés dans un fichier.
~~~

### Rechercher un identifiant

~~~bash
maigret pseudo_exemple
# Recherche les comptes publics associés à un pseudonyme.
~~~

### Lire une liste d'identifiants

~~~bash
maigret --input-file pseudos.txt
# Recherche les identifiants figurant dans un fichier, un par ligne.
~~~

### Exporter un rapport HTML

~~~bash
maigret pseudo_exemple --html
# Produit un rapport HTML lisible dans un navigateur.
~~~

### Exporter un rapport JSON

~~~bash
maigret pseudo_exemple --json simple
# Génère un rapport JSON simplifié.
~~~

### Rechercher des inscriptions

Utiliser une adresse e-mail de démonstration ou examinée dans un cadre autorisé.

~~~bash
~/.venvs/holehe/bin/holehe exemple@example.com
# Interroge les indices d'inscription liés à l'adresse indiquée.
~~~

## Domaine et reconnaissance passive

Avec theHarvester, se placer dans son dossier cloné. Les sources passives interrogent des fournisseurs tiers ; la résolution DNS implique des requêtes supplémentaires.

### Interroger deux sources passives

~~~bash
uv run theHarvester -d example.com -b crtsh,certspotter
# Recherche les données publiques de certificats liées au domaine.
~~~

### Rechercher les e-mails et URL publics

~~~bash
uv run theHarvester -d example.com -b emails,urls,certspotter
# Collecte les adresses et les URL accessibles dans les sources choisies.
~~~

### Exporter les résultats

~~~bash
uv run theHarvester -d example.com -b crtsh,certspotter -f rapport
# Enregistre des rapports locaux JSONL, JSON et XML.
~~~

### Consulter WHOIS

~~~bash
whois example.com
# Affiche les informations publiques disponibles dans le service WHOIS.
~~~

### Lire l'adresse IPv4

~~~bash
dig example.com A +short
# Affiche les adresses IPv4 publiées pour le domaine.
~~~

### Trouver les serveurs de messagerie

~~~bash
dig example.com MX +short
# Affiche les serveurs de courrier déclarés.
~~~

### Lire les serveurs DNS

~~~bash
dig example.com NS +short
# Affiche les serveurs de noms du domaine.
~~~

### Lire les enregistrements TXT

~~~bash
dig example.com TXT +short
# Affiche les informations TXT, dont d'éventuelles politiques de messagerie.
~~~

### Lire les informations TLS

~~~bash
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates
# Affiche le sujet, l'émetteur et les dates du certificat présenté par le serveur.
~~~

## Pages et archives

### Examiner les en-têtes HTTP

~~~bash
curl -sSI --max-time 15 https://example.com/
# Affiche les en-têtes de réponse HTTP, sans le corps de page.
~~~

### Voir une redirection

~~~bash
curl -sSL -o /dev/null -w '%{http_code} %{url_effective}\n' https://example.com/
# Affiche le statut final et l'adresse obtenue après redirection.
~~~

### Récupérer une page pour analyse locale

~~~bash
curl -sSL --max-time 20 https://example.com/ -o page.html
# Enregistre le HTML public d'une page dans un fichier.
~~~

## Images et documents

Les métadonnées peuvent être absentes ou modifiées.

### Identifier le type d'un fichier

~~~bash
file document.pdf
# Affiche le type détecté à partir du contenu du fichier.
~~~

### Lire les métadonnées d'une image

~~~bash
exiftool photo.jpg
# Affiche les informations EXIF et autres métadonnées disponibles.
~~~

### Lire les données GPS

~~~bash
exiftool -GPS:all photo.jpg
# Affiche les champs GPS présents, sans déduire qu'ils sont authentiques.
~~~

### Exporter les métadonnées en JSON

~~~bash
exiftool -json photo.jpg > photo-metadata.json
# Enregistre les métadonnées de l'image au format JSON.
~~~

### Lire les informations d'un PDF

~~~bash
pdfinfo document.pdf
# Affiche les métadonnées courantes et les propriétés du PDF.
~~~

## Conserver les preuves

### Créer un dossier de travail

~~~bash
mkdir -p dossier_osint/{captures,rapports,notes,donnees}
# Prépare une arborescence pour les éléments collectés.
~~~

### Noter la date UTC

~~~bash
date -u '+%Y-%m-%dT%H:%M:%SZ'
# Affiche l'heure UTC de l'observation.
~~~

### Calculer une empreinte SHA-256

~~~bash
sha256sum capture.png > capture.png.sha256
# Enregistre l'empreinte SHA-256 d'une capture locale.
~~~

### Contrôler l'intégrité d'une capture

~~~bash
sha256sum -c capture.png.sha256
# Vérifie que la capture correspond à l'empreinte enregistrée.
~~~

## Dorks utiles

Utilise le [générateur de recherches](./index.md#générateur-de-dorks) pour construire directement les liens Google.

| Recherche | Dork | Utilité |
| --- | --- | --- |
| Pseudonyme | `"pseudo_exemple"` | Mentions exactes d'un identifiant. |
| Profils techniques | `"pseudo_exemple" site:github.com` | Profils ou discussions indexés. |
| E-mail | `"exemple@domaine.fr"` | Occurrences exactes de l'adresse. |
| Nom complet | `"Prénom Nom" filetype:pdf` | Documents publics qui mentionnent le nom. |
| Domaine | `site:example.com` | Pages indexées sur un domaine. |
| Documents | `site:example.com filetype:pdf` | PDF publics d'un domaine. |
| Pages de contact | `site:example.com inurl:contact` | Pages de contact indexées. |

Les opérateurs essentiels : `site:` (domaine), `filetype:` (format), `inurl:` (URL), guillemets (expression exacte) et `-` (exclusion).

## Vérifier les résultats

- **Source** - Noter l'URL exacte et la date d'observation.
- **Contexte** - Confirmer le résultat dans la page d'origine et dans une seconde source.
- **Identité** - Ne pas assimiler deux profils à une même personne sur la seule base d'un pseudo.
- **Traçabilité** - Conserver les sorties ou captures utiles à l'analyse.


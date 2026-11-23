---
title: OSINT - Cheatsheet
description: Commandes OSINT vérifiées dans les documentations des outils, expliquées en français.
aside: false
prev: false
next: false
---

# Cheatsheet OSINT

Commandes de recherche en sources ouvertes, regroupées par objectif. Exemples avec des identifiants fictifs et des domaines de démonstration.

[Retour aux ressources OSINT](./index.md)

Les exemples sont adaptés à **Sherlock**, **Maigret**, **Holehe** et **theHarvester**, ainsi qu'aux utilitaires courants sous Linux. La syntaxe des outils évolue : consulter leur aide après mise à jour.

## Préparer l'environnement

Commandes pour Kali, Debian ou Ubuntu. Exécuter les installations une fois avant d'utiliser les outils.

**Installer les utilitaires système**

~~~bash
sudo apt update && sudo apt install -y git pipx python3-venv whois dnsutils curl jq libimage-exiftool-perl poppler-utils
# Installe Git, les outils DNS, WHOIS, JSON, métadonnées et PDF.
~~~

**Activer les commandes pipx**

~~~bash
pipx ensurepath
# Ajoute les commandes des applications Python installées par pipx au PATH (rouvrir le terminal si nécessaire).
~~~

**Installer Sherlock**

~~~bash
pipx install sherlock-project
# Installe Sherlock dans un environnement Python isolé.
~~~

**Installer Maigret**

~~~bash
pipx install maigret
# Installe Maigret dans un environnement Python isolé.
~~~

**Créer un environnement pour Holehe**

~~~bash
python3 -m venv ~/.venvs/holehe
# Prépare un environnement Python dédié à Holehe.
~~~

**Installer Holehe**

~~~bash
~/.venvs/holehe/bin/pip install holehe
# Installe Holehe dans l'environnement dédié.
~~~

**Récupérer theHarvester**

~~~bash
git clone https://github.com/laramies/theHarvester.git
# Récupère les sources officielles de theHarvester.
~~~

**Installer les dépendances theHarvester**

~~~bash
cd theHarvester && uv sync
# Installe les dépendances depuis le dépôt ; nécessite uv et la version Python demandée par le projet.
~~~

**Afficher l'aide d'un outil**

~~~bash
sherlock --help
# Vérifie les options disponibles dans la version installée.
~~~

## Sherlock - rechercher des pseudonymes

Dépôt : <https://github.com/sherlock-project/sherlock>. Les profils trouvés doivent être vérifiés manuellement.

**Rechercher un pseudonyme**

~~~bash
sherlock pseudo_exemple
# Cherche les comptes publics correspondant au pseudonyme.
~~~

**Afficher uniquement les résultats positifs**

~~~bash
sherlock pseudo_exemple --print-found
# Affiche les sites où Sherlock signale un compte.
~~~

**Comparer plusieurs pseudonymes**

~~~bash
sherlock pseudo_a pseudo_b pseudo_c
# Lance une recherche pour plusieurs identifiants.
~~~

**Limiter à un service**

~~~bash
sherlock pseudo_exemple --site GitHub
# Cible un seul service de la base Sherlock.
~~~

**Limiter à deux services**

~~~bash
sherlock pseudo_exemple --site GitHub --site Reddit
# Vérifie deux plateformes précises.
~~~

**Enregistrer un rapport texte**

~~~bash
sherlock pseudo_exemple --output sherlock-resultats.txt
# Enregistre les profils identifiés dans un fichier.
~~~

**Exporter au format CSV**

~~~bash
sherlock pseudo_exemple --csv
# Crée un export CSV exploitable dans un tableur.
~~~

**Enregistrer plusieurs résultats dans un dossier**

~~~bash
sherlock pseudo_a pseudo_b --folderoutput rapports_sherlock
# Range les résultats des pseudonymes dans un dossier dédié.
~~~

**Limiter le délai réseau**

~~~bash
sherlock pseudo_exemple --timeout 20
# Fixe le délai maximal d'attente réseau à 20 secondes.
~~~

**Afficher la version**

~~~bash
sherlock --version
# Affiche la version installée pour documenter l'environnement.
~~~

## Maigret - approfondir les recherches de comptes

Dépôt : <https://github.com/soxoj/maigret>. Maigret privilégie les comptes accessibles publiquement et propose plusieurs formats de rapports.

**Rechercher un identifiant**

~~~bash
maigret pseudo_exemple
# Recherche les comptes publics associés à un pseudonyme.
~~~

**Limiter le nombre de sites**

~~~bash
maigret pseudo_exemple --top-sites 100
# Limite la recherche aux 100 sites classés en tête.
~~~

**Explorer tous les sites disponibles**

~~~bash
maigret pseudo_exemple -a
# Explore toute la base ; l'opération peut être longue.
~~~

**Rechercher plusieurs identifiants**

~~~bash
maigret pseudo_a pseudo_b
# Recherche plusieurs pseudonymes dans une même exécution.
~~~

**Lire une liste d'identifiants**

~~~bash
maigret --input-file pseudos.txt
# Recherche les identifiants figurant dans un fichier, un par ligne.
~~~

**Filtrer par catégorie de sites**

~~~bash
maigret pseudo_exemple --tags photo
# Recherche sur les sites portant le tag photo.
~~~

**Limiter les connexions simultanées**

~~~bash
maigret pseudo_exemple -n 10
# Limite le nombre de connexions pour modérer le volume de requêtes.
~~~

**Exporter un rapport HTML**

~~~bash
maigret pseudo_exemple --html
# Produit un rapport HTML lisible dans un navigateur.
~~~

**Exporter un rapport CSV**

~~~bash
maigret pseudo_exemple --csv
# Produit un rapport CSV exploitable dans un tableur.
~~~

**Exporter un rapport JSON**

~~~bash
maigret pseudo_exemple --json simple
# Génère un rapport JSON simplifié.
~~~

**Exporter un graphe de résultats**

~~~bash
maigret pseudo_exemple --graph
# Génère un graphe de relations au format HTML.
~~~

**Définir un délai réseau**

~~~bash
maigret pseudo_exemple --timeout 15
# Fixe le délai d'attente des requêtes à 15 secondes.
~~~

**Consulter les options**

~~~bash
maigret --help
# Affiche les options prises en charge par la version installée.
~~~

## Holehe - rechercher à partir d'un e-mail

Dépôt : <https://github.com/megadose/holehe>. Utiliser une adresse de test ou une adresse examinée dans un cadre autorisé. Les réponses des services ne prouvent pas l'identité du titulaire.

**Rechercher des inscriptions**

~~~bash
~/.venvs/holehe/bin/holehe exemple@example.com
# Interroge les indices d'inscription liés à l'adresse indiquée.
~~~

**Afficher les options disponibles**

~~~bash
~/.venvs/holehe/bin/holehe --help
# Affiche les options effectivement fournies par la version installée.
~~~

## theHarvester - recherche passive sur un domaine

Dépôt : <https://github.com/laramies/theHarvester>. Les commandes suivantes utilisent le dépôt cloné et uv. Se placer dans le dossier theHarvester avant exécution.

**Lister les sources et options**

~~~bash
uv run theHarvester -h
# Affiche les sources et les paramètres disponibles.
~~~

**Interroger deux sources passives**

~~~bash
uv run theHarvester -d example.com -b crtsh,certspotter
# Recherche les données publiques de certificats liées au domaine.
~~~

**Ajouter Common Crawl**

~~~bash
uv run theHarvester -d example.com -b crtsh,certspotter,commoncrawl
# Croise les certificats et les données de Common Crawl.
~~~

**Chercher des sous-domaines**

~~~bash
uv run theHarvester -d example.com -b subdomains
# Utilise les sources du catalogue capables de fournir des sous-domaines.
~~~

**Rechercher les e-mails et URL publics**

~~~bash
uv run theHarvester -d example.com -b emails,urls,certspotter
# Collecte les adresses et les URL accessibles dans les sources choisies.
~~~

**Exporter les résultats**

~~~bash
uv run theHarvester -d example.com -b crtsh,certspotter -f rapport
# Enregistre des rapports locaux JSONL, JSON et XML.
~~~

**Conserver les résultats non liés aux hôtes**

~~~bash
uv run theHarvester -d example.com -b emails,ips,urls --no-hosts -f rapport_sans_hotes
# Ignore les noms d'hôtes dans les résultats tout en conservant les autres éléments.
~~~

**Résoudre les hôtes découverts**

~~~bash
uv run theHarvester -d example.com -b crtsh,certspotter -r
# Effectue aussi des requêtes DNS ; l'utiliser seulement dans un périmètre autorisé.
~~~

**Utiliser une installation système**

~~~bash
theHarvester -d example.com -b crtsh,certspotter
# Exécute la version installée par la distribution, sans uv.
~~~

## DNS, domaines et infrastructures

Le domaine example.com est utilisé comme exemple. Les résultats DNS ne prouvent pas à eux seuls la propriété d'un service.

**Consulter WHOIS**

~~~bash
whois example.com
# Affiche les informations publiques disponibles dans le service WHOIS.
~~~

**Lire l'adresse IPv4**

~~~bash
dig example.com A +short
# Affiche les adresses IPv4 publiées pour le domaine.
~~~

**Lire l'adresse IPv6**

~~~bash
dig example.com AAAA +short
# Affiche les adresses IPv6 publiées pour le domaine.
~~~

**Trouver les serveurs de messagerie**

~~~bash
dig example.com MX +short
# Affiche les serveurs de courrier déclarés.
~~~

**Lire les serveurs DNS**

~~~bash
dig example.com NS +short
# Affiche les serveurs de noms du domaine.
~~~

**Lire les enregistrements TXT**

~~~bash
dig example.com TXT +short
# Affiche les informations TXT, dont d'éventuelles politiques de messagerie.
~~~

**Lire le certificat d'autorité DNS**

~~~bash
dig example.com CAA +short
# Affiche les autorités autorisées à émettre des certificats, si déclarées.
~~~

**Interroger un résolveur précis**

~~~bash
dig @1.1.1.1 example.com A +short
# Interroge explicitement le résolveur DNS indiqué.
~~~

**Faire une recherche DNS inverse**

~~~bash
dig -x 8.8.8.8 +short
# Recherche le nom PTR éventuellement associé à une adresse IP.
~~~

**Consulter un nom précis**

~~~bash
host www.example.com
# Affiche les enregistrements DNS trouvés pour le nom fourni.
~~~

**Lire les informations TLS**

~~~bash
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates
# Affiche le sujet, l'émetteur et les dates du certificat présenté par le serveur.
~~~

## Web, archives et vérification de pages

Ces commandes interrogent le site indiqué. Pour les archives, utiliser aussi <https://web.archive.org/>.

**Examiner les en-têtes HTTP**

~~~bash
curl -sSI --max-time 15 https://example.com/
# Affiche les en-têtes de réponse HTTP, sans le corps de page.
~~~

**Voir une redirection**

~~~bash
curl -sSL -o /dev/null -w '%{http_code} %{url_effective}\n' https://example.com/
# Affiche le statut final et l'adresse obtenue après redirection.
~~~

**Récupérer une page pour analyse locale**

~~~bash
curl -sSL --max-time 20 https://example.com/ -o page.html
# Enregistre le HTML public d'une page dans un fichier.
~~~

**Afficher le titre HTML enregistré**

~~~bash
grep -iEo '<title>[^<]*</title>' page.html
# Extrait une balise titre simple du HTML local, si elle existe.
~~~

**Extraire les liens HTML visibles**

~~~bash
grep -oE 'href="[^"]+"' page.html
# Liste les attributs href au format à guillemets doubles du fichier HTML local.
~~~

**Rechercher un terme dans des notes**

~~~bash
grep -inE 'domaine|organisation' notes.txt
# Cherche les lignes contenant l'un des termes et affiche leurs numéros.
~~~

**Conserver les URL présentes dans un fichier**

~~~bash
grep -Eo 'https?://[^[:space:]"<>]+' notes.txt | sort -u
# Extrait les URL explicites et supprime les doublons ; vérifier les caractères de fin.
~~~

## Métadonnées et fichiers

Les métadonnées peuvent être absentes, modifiées ou supprimées. Ne jamais déduire une localisation ou une identité d'un seul champ.

**Identifier le type d'un fichier**

~~~bash
file document.pdf
# Affiche le type détecté à partir du contenu du fichier.
~~~

**Lire les métadonnées d'une image**

~~~bash
exiftool photo.jpg
# Affiche les informations EXIF et autres métadonnées disponibles.
~~~

**Afficher les champs et leurs groupes**

~~~bash
exiftool -G1 -a -s photo.jpg
# Présente les tags avec leur groupe et leurs noms techniques.
~~~

**Lire les données GPS**

~~~bash
exiftool -GPS:all photo.jpg
# Affiche les champs GPS présents, sans déduire qu'ils sont authentiques.
~~~

**Exporter les métadonnées en JSON**

~~~bash
exiftool -json photo.jpg > photo-metadata.json
# Enregistre les métadonnées de l'image au format JSON.
~~~

**Lire les informations d'un PDF**

~~~bash
pdfinfo document.pdf
# Affiche les métadonnées courantes et les propriétés du PDF.
~~~

**Rechercher du texte dans un PDF**

~~~bash
pdftotext -layout document.pdf document.txt
# Extrait le texte disponible dans le PDF vers un fichier texte.
~~~

**Lire les informations d'un fichier**

~~~bash
stat document.pdf
# Affiche les informations du système de fichiers, dont les horodatages locaux.
~~~

**Rechercher des fichiers PDF dans un dossier**

~~~bash
find dossier_osint -type f -iname '*.pdf'
# Liste les PDF présents dans les sous-dossiers.
~~~

## Organiser et conserver les résultats

Distinguer observation, interprétation et résultat non confirmé.

**Créer un dossier de travail**

~~~bash
mkdir -p dossier_osint/{captures,rapports,notes,donnees}
# Prépare une arborescence pour les éléments collectés.
~~~

**Noter la date UTC**

~~~bash
date -u '+%Y-%m-%dT%H:%M:%SZ'
# Affiche l'heure UTC de l'observation.
~~~

**Calculer une empreinte SHA-256**

~~~bash
sha256sum capture.png > capture.png.sha256
# Enregistre l'empreinte SHA-256 d'une capture locale.
~~~

**Contrôler l'intégrité d'une capture**

~~~bash
sha256sum -c capture.png.sha256
# Vérifie que la capture correspond à l'empreinte enregistrée.
~~~

**Conserver la sortie d'une recherche**

~~~bash
sherlock pseudo_exemple --print-found | tee sherlock-console.txt
# Affiche et enregistre simultanément la sortie standard.
~~~

**Extraire une valeur JSON**

~~~bash
jq -r '.[] | .FileName // empty' photo-metadata.json
# Lit le nom de fichier dans l'export JSON d'ExifTool.
~~~

**Lister les fichiers du dossier**

~~~bash
find dossier_osint -type f -print | sort
# Produit un inventaire simple des fichiers collectés.
~~~

## Requêtes pour moteurs de recherche

Ces expressions se saisissent directement dans Google ou un moteur compatible. Elles ne sont pas des commandes de terminal.

**Limiter à un domaine**

~~~text
site:example.com
~~~

Ne montre que les pages indexées sous le domaine indiqué.

**Rechercher des documents PDF**

~~~text
site:example.com filetype:pdf
~~~

Cherche les PDF indexés pour le domaine.

**Rechercher une expression exacte**

~~~text
"rapport annuel" "example.com"
~~~

Recherche les pages qui contiennent les deux expressions.

**Exclure un terme**

~~~text
"organisation" -recrutement
~~~

Retire les pages comprenant le terme exclu, selon le moteur.

**Rechercher dans une URL**

~~~text
site:example.com inurl:publications
~~~

Cherche les URL contenant publications sur le domaine.

**Rechercher dans un titre**

~~~text
site:example.com intitle:rapport
~~~

Cherche les pages dont le titre contient rapport.

**Chercher une ancienne page**

~~~text
"nom de projet" site:example.com
~~~

Retrouve les occurrences indexées du nom de projet.

**Rechercher une présentation**

~~~text
site:example.com filetype:pptx
~~~

Cherche les présentations publiques indexées pour le domaine.

## Points de contrôle

- **Pseudonyme** : un compte trouvé ne démontre pas que deux profils appartiennent à la même personne.
- **E-mail** : une réponse de service peut être inexacte ou bloquée ; ne pas assimiler un indicateur d'inscription à une confirmation d'identité.
- **Domaine** : distinguer source passive, requête DNS et connexion directe à une machine.
- **Preuve** : conserver l'URL d'origine, la date UTC, le contexte et une copie du résultat si cela est nécessaire et autorisé.

## Documentation des outils

- [Sherlock](https://github.com/sherlock-project/sherlock) - Recherche de pseudonymes.
- [Maigret](https://github.com/soxoj/maigret) - Recherche de comptes et rapports.
- [Holehe](https://github.com/megadose/holehe) - Indices d'inscription par e-mail.
- [theHarvester](https://github.com/laramies/theHarvester) - Collecte de données de domaines.
- [Awesome OSINT](https://github.com/jivoi/awesome-osint) - Répertoire de ressources complémentaires.

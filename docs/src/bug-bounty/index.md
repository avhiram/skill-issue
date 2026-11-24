---
title: Bug Bounty
description: Parcours chronologique, de la sélection du programme au rapport et à la prime.
aside: true
prev: false
next: false
---

# Bug Bounty

Méthodologie de travail et cheatsheet, de la sélection d'un programme au suivi du rapport. Les commandes sont classées dans l'étape où elles sont utiles, avec une explication en français.

Les exemples utilisent des domaines génériques ou des laboratoires. Les commandes historiques et leurs options ne sont pas toutes vérifiées. Ne tester que les ressources expressément autorisées par le programme ; certaines techniques, même sur un domaine du scope, peuvent être interdites.

[Outils et extensions](./ressources.md) · [Archive Lostsec](https://web.archive.org/web/20250828093634/https://lostsec.xyz/)

## Cheatsheet

Suivre les étapes dans l'ordre. Les commandes de chaque rubrique sont des alternatives ou des exemples indépendants, sauf lorsqu'un enchaînement et ses fichiers sont explicitement décrits.

## Programme et préparation

Objectif : choisir un programme, comprendre les règles et préparer son environnement avant toute requête.

### Préparation

- Lire le scope, les exclusions, les limites de débit et les règles de divulgation du programme.
- Distinguer les domaines autorisés des noms simplement découverts. Un certificat, un ASN ou une archive ne prouve pas qu'un service est dans le scope.
- Préparer un dossier de travail et conserver les résultats intermédiaires.

### Choisir un programme

- Identifier un programme ouvert aux signalements et vérifier s'il prévoit une prime.
- Lire les actifs inclus et exclus, les catégories éligibles, les restrictions sur l'automatisation et les consignes de signalement.
- Conserver une copie datée du scope et des règles. Un VDP n'est pas nécessairement rémunéré.
- Séparer chaque programme dans un dossier de travail et utiliser des comptes de test dédiés.

### Dossier de travail

```bash
mkdir -p bug-bounty/{scope,recon,requests,preuves,rapports}
cd bug-bounty
```

Prépare les dossiers locaux pour conserver le périmètre, les inventaires, les requêtes, les preuves et les rapports. Adaptation pratique du classement proposé dans l'article Claude Code.

### Préparer les outils

Consulter [Security Tools et Browser Extensions](./ressources.md). Vérifier les versions installées, les dépendances et les permissions des extensions avant utilisation.

### Vérifier la disponibilité des outils

```bash
command -v subfinder httpx katana gau nmap nuclei ffuf
```

Vérifie quels exécutables sont présents dans le PATH. Attention : httpx désigne ici l'outil ProjectDiscovery, pas le client Python. Ajout de préparation local.

## Reconnaissance passive

Objectif : recenser les actifs connus, vérifier leur appartenance au programme et préparer un inventaire exploitable.

### Énumération des sous-domaines

#### Découverte des sous-domaines

```bash
subfinder -d example.com -all -recursive > subexample.com.txt
```

Effectue une recherche récursive avec Subfinder et enregistre les résultats.

#### Amass - découverte passive

```bash
amass enum -passive -d example.com -o amass_passive_subs.txt
```

Collecte les sous-domaines depuis des sources publiques.

#### Assetfinder - sous-domaines

```bash
assetfinder --subs-only example.com > assetfinder_subs.txt
```

Collecte les noms de sous-domaines connus.

#### Findomain - sous-domaines

```bash
findomain -t example.com -q > findomain_subs.txt
```

Collecte les sous-domaines et écrit les résultats dans un fichier.

#### Chaos - données publiques

```bash
chaos -d example.com -silent > chaos_subs.txt
```

Interroge le catalogue Chaos de ProjectDiscovery ; vérifier les prérequis d'accès.

#### CRT.sh - certificats publics

```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json" |
jq -r '.[].name_value' |
sed 's/\*\.//g' |
anew crtsh_subs.txt
```

Extrait les noms des certificats publics avec jq et retire le préfixe wildcard.

#### Fusion des résultats passifs

```bash
cat *_subs.txt | sort -u > all_subs.txt
```

Fusionne les fichiers de résultats en supprimant les doublons. Exécuter dans le dossier contenant uniquement les fichiers concernés.

### Sources publiques complémentaires

#### HackerTarget - DNS passif

```bash
curl -fsS 'https://api.hackertarget.com/hostsearch/?q=example.com' | cut -d ',' -f1 | sort -u > hackertarget_subs.txt
```

Récupère les noms connus dans la base HackerTarget. Variante corrigée du pipeline de l'article, qui se terminait par un pipe vide.

#### URLScan - domaines observés

```bash
curl -fsS 'https://urlscan.io/api/v1/search/?q=domain:example.com' | jq -r '.results[]?.page?.domain // empty' | sort -u > urlscan_subs.txt
```

Extrait les domaines observés dans les résultats historiques de URLScan.

#### Common Crawl - index historique

```bash
curl -fsS 'https://index.commoncrawl.org/CC-MAIN-2023-50-index?url=*.example.com&output=json' | jq -r '.url' | sed -E 's#^https?://##; s#/.*##' | sort -u > commoncrawl_subs.txt
```

Extrait les hôtes de l'index 2023-50 indiqué dans l'article. Il s'agit d'un index historique, pas d'un inventaire actuel.

#### Wayback CDX - URL historiques

```bash
curl -fsS 'https://web.archive.org/cdx/search/cdx?url=*.example.com/*&output=text&fl=original&collapse=urlkey' | sort -u > wayback_cdx.txt
```

Récupère les URL indexées. Le double suffixe .com du document a été corrigé.

#### URLScan - adresses IP observées

```bash
curl -fsS 'https://urlscan.io/api/v1/search/?q=domain:example.com' | jq -r '.results[]?.page?.ip // empty' | sort -u > observed_ips.txt
```

Récupère les IP historiques présentes dans les résultats. Une IP observée n'est pas une preuve d'appartenance au scope.

#### AlienVault OTX - adresses IP observées

```bash
curl -fsS 'https://otx.alienvault.com/api/v1/indicators/hostname/example.com/url_list?limit=500&page=1' | jq -r '.url_list[]?.result?.urlworker?.ip // empty' | sort -u > otx_ips.txt
```

Extrait les IP observées dans les données publiques OTX. Cette requête ne traite que la première page.

#### Fusion des résultats de collecte

```bash
sort -u amass_passive_subs.txt assetfinder_subs.txt findomain_subs.txt chaos_subs.txt crtsh_subs.txt hackertarget_subs.txt urlscan_subs.txt commoncrawl_subs.txt > inventory_subs.txt
```

Fusionne explicitement les fichiers produits par les différentes sources, lorsqu'ils existent. Évite de mélanger tous les fichiers TXT du dossier.

Les exemples de sources publiques sont adaptés du document Recon to Master. Les réponses d'API, quotas, disponibilité et options n'ont pas été testés.

### Shodan

#### Recherche par certificat TLS

```text
Ssl.cert.subject.CN:"example.com" 200
```

Requête Shodan historique fondée sur le nom commun d'un certificat.

### Advanced Google Dorks Methodology

La fiche archivée ne contient pas de commandes supplémentaires.

#### Bonnes pratiques

- Remplacer example.com par le domaine autorisé.
- Utiliser la notation [.] lors de la documentation pour éviter la création automatique de liens.
- Combiner les opérateurs de recherche et utiliser les guillemets pour les expressions exactes.
- Exclure les résultats non pertinents avec `-site:` et utiliser les filtres de date.
- Surveiller les nouvelles expositions dans le périmètre autorisé.
- Documenter et vérifier chaque observation avant le signalement.

Voir également [Exposition de données](#exposition-de-donnees) pour les requêtes déjà présentes.

### Waybackurls - noms de domaine

```bash
waybackurls example.com | unfurl -u domains > wayback_domains.txt
```

Extrait les noms de domaine des URL historiques. Commande issue de l'article IIS ; Unfurl doit être installé. Les domaines découverts ne sont pas automatiquement autorisés.

## Cartographie et scan réseau

Objectif : identifier les services réellement présents, les ports autorisés et les technologies, sans confondre un CDN ou un hébergement partagé avec le périmètre.

### Validation DNS et HTTP

Vérifier l'appartenance des noms collectés au scope avant les requêtes actives. Les exemples de fichiers historiques utilisent plusieurs noms ; sélectionner explicitement les fichiers de la méthode choisie.

#### DNSX - validation DNS

```bash
dnsx -l all_subs.txt -silent -o resolved_subs.txt
```

Identifie les noms qui répondent aux requêtes DNS.

#### DNSX - résolution inverse

```bash
dnsx -ptr -l resolved_subs.txt -resp-only -o reverse_dns.txt
```

Interroge les enregistrements PTR ; utiliser une liste d'adresses IP pour une résolution inverse pertinente, plutôt qu'une liste de noms.

#### HTTPX - métadonnées des services

```bash
httpx -l resolved_subs.txt -p 80,443,8080,8443 -silent -title -sc -ip -o live_websites.txt
```

Identifie les services HTTP répondants et collecte titres, codes et adresses IP. Utiliser HTTPX de ProjectDiscovery.

#### Filtrage des sous-domaines actifs

```bash
cat subexample.com.txt | httpx-toolkit -ports 80,443,8080,8000,8888 -threads 200 > subexample.coms_alive.txt
```

Vérifie les réponses HTTP sur plusieurs ports et enregistre les hôtes répondants.

> La commande emploie une concurrence élevée. Respecter les limites du programme.

#### Httprobe - services Web

```bash
cat resolved_subs.txt | httprobe > live_websites.txt
```

Alternative de détection des services HTTP et HTTPS. Le fichier de sortie est écrasé.

### Scan réseau

#### Inventaire des ports avec Naabu

```bash
naabu -list ip.txt -c 50 -nmap-cli 'nmap -sV -SC' -o naabu-full.txt
```

Associe Naabu et Nmap pour identifier des ports et services.

#### Scan complet avec Nmap

```bash
nmap -p- --min-rate 1000 -T4 -A example.com -oA fullscan
```

Analyse l'ensemble des ports TCP et collecte des informations sur les services.

> Débit et options intrusives à vérifier selon les règles du programme.

#### Scan avec Masscan

```bash
masscan -p0-65535 example.com --rate 100000 -oG masscan-results.txt
```

Exemple historique de scan de ports à débit très élevé.

> Débit extrêmement élevé dans l'original ; ne pas exécuter sur des systèmes tiers.

### Reconnaissance visuelle

#### Aquatone - captures des services Web

```bash
cat hosts.txt | aquatone
```

Génère des captures et un rapport visuel à partir d'une liste de services Web autorisés. Préparer `hosts.txt` avec les hôtes validés et vérifier les dépendances du logiciel. Aquatone est un outil historique ; sa compatibilité actuelle n'a pas été testée.

#### Cartographie ASN et IP

Identifier les réseaux et les systèmes autonomes associés à une organisation, puis comparer les résultats avec le périmètre explicitement autorisé. Une association ASN, DNS ou IP ne suffit pas à établir qu'un actif peut être testé. Cette étape complète l'énumération des sous-domaines sans répéter les commandes existantes.

#### Checklist de reconnaissance

- [ ] Collecte passive et déduplication des sous-domaines.
- [ ] Validation DNS et contrôle du scope.
- [ ] Inventaire HTTP et identification des technologies.
- [ ] Cartographie ASN/IP et reconnaissance visuelle.
- [ ] Collecte des URL, paramètres et références JavaScript.
- [ ] Inventaire des interfaces API et des fonctionnalités.
- [ ] Vérification manuelle des observations et préparation du rapport.

### Nmap - rapport XML local

```bash
nmap -sV -p 8000,8080 -oX nmap_out.xml 127.0.0.1
```

Produit un inventaire XML des deux ports du laboratoire local. Adaptation pour alimenter le parseur Nmap présenté dans le workflow de scanning.

### Workflow de scanning et fuzzing

L'article organise le travail en six étapes. Les commandes déjà documentées dans la cheatsheet ne sont pas répétées.

1. **Chaos** : collecte des sous-domaines.
2. **HTTPX** : validation HTTP et inventaire, déduplication des résultats.
3. **Naabu** : inventaire des ports expressément autorisés.
4. **Nmap** : identification des services et production de résultats XML.
5. **Nuclei** : contrôle des configurations et vulnérabilités connues dans le périmètre de test.
6. **FFUF** : découverte de contenu dans un laboratoire autorisé.

Ne pas assimiler une adresse IP partagée, un CDN ou un service tiers à un actif autorisé. Vérifier le scope avant tout scan. Comparer les codes HTTP, la taille des réponses et le nombre de mots pour distinguer les réponses génériques des résultats pertinents ; un 403 doit être respecté.

#### Nmap - conversion XML en HTML

```bash
./nmap-parse-output nmap_out.xml html > scan.html
```

Convertit un rapport Nmap XML déjà produit en document HTML, sans effectuer de nouvelle requête. Adapter le chemin au fichier local. La syntaxe est reprise de l'article avec un chemin générique.

[Script nmap-parse-output](https://github.com/ernw/nmap-parse-output)

## Cartographie Web et API

Objectif : inventorier les URL, routes, formulaires, paramètres, scripts et interfaces API dans le périmètre.

### Collecte des URL

#### Collecte passive avec Katana

```bash
katana -u subexample.coms_alive.txt -d 5 -ps -pss waybackarchive,commoncrawl,alienvault -kf -jc -fx -ef woff,css,png,svg,jpg,woff2,jpeg,gif,svg -o allurls.txt
```

Collecte des URL depuis des archives et d'autres sources, en excluant certaines extensions.

#### Collecte avancée avec Katana

```bash
echo example.com | katana -d 5 -ps -pss waybackarchive,commoncrawl,alienvault -f qurl | urldedupe > output.txt
katana -u https://example.com -d 5 | grep '=' | urldedupe | anew output.txt
cat output.txt | sed 's/=.*/=/' > final.txt
```

Bloc de collecte et de déduplication des URL paramétrées.

> Séparation des lignes rétablie grâce aux notes complémentaires ; options et compatibilité à vérifier. La normalisation supprime tout ce qui suit le premier signe égal.

#### Collecte avec GAU

```bash
echo example.com | gau --mc 200 | urldedupe > urls.txt
grep -E '\.php|\.asp|\.aspx|\.jspx|\.jsp' urls.txt | grep '=' | sort -u > output.txt
cat output.txt | sed 's/=.*/=/' > final.txt
```

Bloc de collecte et de filtrage des URL par extension et paramètres.

> Séparation des lignes rétablie grâce aux notes complémentaires ; options et compatibilité à vérifier. La normalisation supprime tout ce qui suit le premier signe égal.

#### Waybackurls - archives Web

```bash
waybackurls example.com > wayback_urls.txt
```

Collecte les URL connues dans les archives.

#### Katana - crawling des services Web

```bash
katana -list live_websites.txt -jc -o katana_urls.txt
```

Explore les services Web autorisés et les références JavaScript. Vérifier le format d'entrée.

#### Gospider - exploration Web

```bash
gospider -S live_websites.txt -d 2 -o gospider_output/
```

Explore les sites de la liste à une profondeur de deux niveaux.

#### AlienVault OTX - collecte historique

```bash
./alienvault.sh example.com
```

Interroge les données publiques d'AlienVault OTX pour recenser les URL associées au domaine autorisé. Le script doit être récupéré et examiné avant exécution ; vérifier son comportement et ses dépendances.

[Script alienvault.sh](https://github.com/coffinxp/scripts/blob/main/alienvault.sh)

#### URLScan.io - collecte passive

```bash
python urlscan.py -d example.com --mode urls
python urlscan.py -d example.com --mode subdomains
```

Les deux modes présentés dans l'article récupèrent respectivement les URL et les sous-domaines connus de URLScan.io. Les résultats historiques ne prouvent ni que les ressources sont encore disponibles, ni qu'elles font partie du scope.

[Script urlscan.py](https://github.com/coffinxp/scripts/blob/main/urlscan.py)

#### Wayback - filtrage des archives

```bash
./wayback.sh example.com -sc 200,302,403
./wayback.sh example.com -scx 404,500
```

Le premier exemple sélectionne les codes indiqués ; le second les exclut. Les options proviennent de l'article et n'ont pas été testées. Un code HTTP archivé ne garantit pas le statut actuel de la page.

[Script wayback.sh](https://github.com/coffinxp/scripts/blob/main/wayback.sh)

#### Gospider - sitemap

```bash
gospider -s https://example.com --sitemap -d 2
```

Explore les URL du sitemap et les liens à une profondeur de deux niveaux. Limiter les requêtes au périmètre autorisé.

#### Gospider - proxy HTTP local

```bash
gospider -s https://example.com -p http://127.0.0.1:8080
```

Fait transiter les requêtes par un proxy HTTP local, par exemple Burp Suite, pour observer le trafic du laboratoire. Le proxy doit être démarré et configuré.

[Gospider - dépôt GitHub](https://github.com/jaeles-project/gospider)

#### Fusion des URL archivées

```bash
cat archived_urls.txt wayback_urls.txt | sort -u > all_archived_urls.txt
```

Regroupe les résultats de GAU et Waybackurls ; les deux fichiers doivent exister.

#### Extraction des URL avec paramètres

```bash
grep '=' all_archived_urls.txt > parameters.txt
```

Isole les URL contenant un signe égal, puis vérifier manuellement qu'il s'agit de paramètres.

#### Repérage des pages de connexion

```bash
grep -Ei 'login|admin|signin|dashboard' live_websites.txt | tee login_endpoints.txt
```

Repère les services ou titres contenant ces termes ; cela ne constitue pas une preuve de vulnérabilité.

### GAU - collecte des archives

```bash
gau --subs example.com > archived_urls.txt
```

Alimente le fichier archived_urls.txt utilisé par la fusion des archives. Exemple du document Full Bug Bounty Reconnaissance ; vérifier que les sous-domaines sont dans le scope.

### URLfinder - collecte passive

```bash
urlfinder -d example.com | sort -u > urlfinder_urls.txt
```

Collecte et déduplique les URL connues. Variante issue de Recon to Master avec un domaine générique.

### Crawling complémentaire et nettoyage

#### Hakrawler - exploration locale

```bash
printf '%s\n' 'http://127.0.0.1:8000/' | hakrawler -u > hakrawler_urls.txt
```

Explore un site de laboratoire déjà démarré sur le port 8000. L'option -u est reprise du document ; vérifier sa prise en charge dans la version installée.

#### GAU - liste de domaines

```bash
gau < scope/domains.txt | sort -u > gau_urls.txt
```

Collecte les URL historiques des domaines listés dans le fichier préparé au préalable.

#### URL avec paramètres

```bash
grep -E '\?[^=]+=.+$' allurls.txt | sort -u > urls_with_params.txt
```

Filtre les URL contenant un paramètre avec une valeur non vide, sans envoyer de requête.

#### Gospider et Katana - références JavaScript locales

```bash
grep -E '\.js([?#].*)?$' allurls.txt | sort -u > js_inventory.txt
```

Filtre une liste locale d'URL déjà obtenues. L'expression tient aussi compte des paramètres et fragments après l'extension.

#### Analyse DOM locale - sources et sinks

```bash
grep -nE 'document\.(location|URL|cookie|domain|referrer)|innerHTML|outerHTML|eval\(|\.write\(' javascript/*.js
```

Repère des sources et sinks JavaScript dans les fichiers locaux autorisés. Un résultat ne constitue pas une preuve de XSS. Adaptation en lecture locale de la commande DOM de l'article.

#### Inventaire des paramètres avec GF

```bash
gf sqli < allurls.txt > sqli_candidates.txt
```

Classe les URL déjà collectées selon un pattern GF installé. Aucun test réseau ni exploitation n'est effectué ; les correspondances sont des hypothèses.


### Découverte de paramètres

#### Recherche passive avec Arjun

```bash
arjun -u https://example.com/endpoint.php -oT arjun_output.txt -t 10 --rate-limit 10 --passive -m GET,POST --headers "User-Agent: Mozilla/5.0"
```

Recherche des paramètres HTTP avec le mode passif d'Arjun.

#### Recherche avec une wordlist Arjun

```bash
arjun -u https://example.com/endpoint.php -oT arjun_output.txt -m GET,POST -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt -t 10 --rate-limit 10 --headers "User-Agent: Mozilla/5.0"
```

Teste des noms de paramètres provenant d'une liste de mots.

#### Arjun - export JSON

```bash
arjun -u https://example.com -m GET,POST --stable -oJ params.json
```

Recherche des paramètres dans un environnement autorisé et exporte les résultats en JSON. L'option de sortie a été adaptée au format JSON ; vérifier la version installée.

### Analyse JavaScript

#### Collecte et analyse des fichiers JS

```bash
echo example.com | katana -d 5 | grep -E "\.js$" | nuclei -t /path/to/nuclei-templates/http/exposures/ -c 30
```

Collecte des URL JavaScript et applique des modèles d'exposition Nuclei.

#### Analyse d'une liste de fichiers JS

```bash
cat alljs.txt | nuclei -t /path/to/nuclei-templates/http/exposures/
```

Applique des modèles Nuclei à une liste de fichiers JavaScript collectés.

#### Collecte passive des scripts

```bash
gau --subs example.com | grep '\.js$' > js_passive.txt
```

Sélectionne les URL archivées se terminant par .js.

#### Collecte active des scripts

```bash
katana -list live_websites.txt -jc -silent | grep '\.js$' > js_active.txt
```

Recense les références JavaScript dans les applications autorisées.

#### Fusion des URL JavaScript

```bash
cat js_passive.txt js_active.txt | sort -u > js_all.txt
```

Crée une liste unique de scripts à examiner.

### Filtrage des types de contenu

#### Filtrage du contenu HTML

```bash
echo example.com | gau | grep -Eo '(\/[^\/]+)\.(php|asp|aspx|jsp|jsf|cfm|pl|perl|cgi|htm|html)$' | httpx -status-code -mc 200 -content-type | grep -E 'text/html|application/xhtml+xml'
```

Bloc historique de recherche d'extensions de pages et de filtrage du type MIME.

> Le filtrage extrait des chemins au lieu d'URL complètes ; le fonctionnement n'est pas garanti.

#### Filtrage du contenu JavaScript

```bash
echo example.com | gau | grep '\.js-php-jsp-other extens$' | httpx -status-code -mc 200 -content-type | grep 'application/javascript'
```

Bloc historique de filtrage du type MIME JavaScript.

> Expression de filtrage manifestement incomplète dans la source ; non exécutable comme méthode fiable.

### Advanced Recon Methodology

La fiche Lostsec fournie en complément reprend une grande partie des commandes de la cheatsheet. Pour éviter les doublons, suivre les rubriques existantes dans l'ordre suivant :

1. [Énumération des sous-domaines](#enumeration-des-sous-domaines) : Subfinder et filtrage HTTP.
2. [Collecte des URL](#collecte-des-url) : Katana, GAU et normalisation des résultats.
3. [Exposition de données](#exposition-de-donnees) : inspection des références et documents indexés.
4. [Découverte de paramètres](#decouverte-de-parametres) : Arjun.
5. [Cross-Origin Resource Sharing (CORS)](#cross-origin-resource-sharing-cors) : lecture des en-têtes.
6. [WordPress](#wordpress) et [analyse JavaScript](#analyse-javascript) : vérification des configurations et ressources.
7. Vérifier les résultats dans le périmètre autorisé et documenter les observations.

#### Lecture ciblée des en-têtes CORS

```bash
curl -H 'Origin: http://example.com' -I https://example.com/wp-json/ | grep -i -e 'access-control-allow-origin' -e 'access-control-allow-methods' -e 'access-control-allow-credentials'
```

Affiche les trois en-têtes CORS pertinents. Le domaine tiers figurant dans la fiche a été remplacé par un domaine d'exemple. Un en-tête seul ne suffit pas à établir l'impact.

#### Découverte de contenu

Dirsearch et FFUF permettent de cartographier les chemins dans un laboratoire ou un périmètre explicitement autorisé. La fiche contient des variantes récursives ; adapter les limites de débit, les extensions et la wordlist aux règles du programme. Les en-têtes de contournement figurant dans la variante FFUF ne sont pas nécessaires à un inventaire ordinaire.

### Workflow de reconnaissance rapide

L'article [My 5-Minute Workflow to Find Bugs on Any Website](https://infosecwriteups.com/my-5-minute-workflow-to-find-bugs-on-any-website-c20075320c96) (27 septembre 2025, mis à jour le 26 novembre 2025) décrit trois axes : inventaire des expositions CVE, inspection du DOM et collecte automatisée des URL.

- **Shodan et Nuclei** : comparer les informations sur les produits et versions avec l'inventaire des actifs autorisés et les avis de sécurité. L'article présente aussi des scans massifs ; ces procédures ne sont pas reproduites ici.
- **Inspection du DOM** : relever les champs désactivés, en lecture seule ou masqués et les références présentes dans le HTML. Les restrictions côté navigateur ne remplacent pas les contrôles d'autorisation côté serveur. Les bookmarklets modifiant ces restrictions ne sont pas reproduits.
- **Collecte d'URL** : compléter les sources passives avec AlienVault OTX, URLScan.io et les archives Web, puis dédupliquer les résultats et vérifier le scope.
- **Analyse JavaScript** : inventorier les références et endpoints des scripts autorisés. Si une donnée sensible apparaît, la protéger et la signaler sans tenter de réutiliser un identifiant ou un secret.

Les nouvelles commandes de collecte et de crawling sont classées dans [Collecte des URL](#collecte-des-url), sans répéter les commandes existantes. Les scripts de collecte de secrets et les chaînes de scan offensif en masse n'ont pas été ajoutés. Le délai de cinq minutes est une affirmation de l'auteur, pas une garantie de découverte.

### Inventaire API

Relever les routes et méthodes HTTP dans la documentation, les requêtes du navigateur et les captures Burp. Classer les paramètres, les types de réponses et les fonctions nécessitant une authentification.

### Inventaire des champs JSON locaux

```bash
jq 'keys' response.json
```

Affiche les clés d'un objet JSON déjà enregistré, sans contacter un service. Exemple local ajouté pour faciliter l'analyse des réponses API.

## Tests de vulnérabilités

Objectif : choisir les contrôles adaptés aux fonctionnalités identifiées et distinguer les indices des vulnérabilités confirmées.

### Subdomain Takeover

#### Vérification du risque de Subdomain Takeover

```bash
subzy run --targets subexample.coms.txt --concurrency 100 --hide_fails --verify_ssl
```

Recherche des configurations potentiellement vulnérables avec Subzy.

> Le fichier d'entrée est une liste de sous-domaines autorisés à préparer ; son nom diffère des sorties Subfinder précédentes.


### Exposition de données

#### Repérage de fichiers sensibles

```bash
cat allurls.txt | grep -E "\.xls|\.xml|\.xlsx|\.json|\.pdf|\.sql|\.doc|\.docx|\.pptx|\.txt|\.zip|\.tar\.gz|\.tgz|\.bak|\.7z|\.rar|\.log|\.cache|\.secret|\.db|\.backup|\.yml|\.gz|\.config|\.csv|\.yaml|\.md|\.md5"
```

Filtre une liste d'URL selon des extensions pouvant indiquer des fichiers exposés.

#### Recherche de documents indexés

```text
site:*.example.com (ext:doc OR ext:docx OR ext:odt OR ext:pdf OR ext:rtf OR ext:ppt OR ext:pptx OR ext:csv OR ext:xls OR ext:xlsx OR ext:txt OR ext:xml OR ext:json OR ext:zip OR ext:rar OR ext:md OR ext:log OR ext:bak OR ext:conf OR ext:sql)
```

Requête de moteur de recherche filtrant les extensions de documents dans le périmètre autorisé.

#### Détection de dépôts Git exposés

```bash
cat example.coms.txt | grep "SUCCESS" | gf urls | httpx-toolkit -sc -server -cl -path "/.git/" -mc 200 -location -ms "Index of" -probe
```

Vérifie des réponses HTTP pouvant révéler un répertoire Git.

#### Filtrage étendu des extensions sensibles

```bash
echo https://example.com | gau | grep -E "\.(xls|xml|xlsx|json|pdf|sql|doc|docx|pptx|txt|zip|tar\.gz|tgz|bak|7z|rar|log|cache|secret|db|backup|yml|gz|config|csv|yaml|md|md5|tar|xz|7zip|p12|pem|key|crt|csr|sh|pl|py|java|class|jar|war|ear|sqlitedb|sqlite3|dbf|db3|accdb|mdb|sqlcipher|gitignore|env|ini|conf|properties|plist|cfg)$"
```

Recherche des extensions de fichiers potentiellement sensibles dans les URL collectées.

#### Recherche de buckets AWS S3

```bash
s3scanner scan -d example.com
```

Recherche des buckets associés au domaine indiqué.

#### Recherche de secrets dans des fichiers JavaScript

```bash
cat allurls.txt | grep -E "\.js$" | httpx-toolkit -mc 200 -content-type | grep -E "application/javascript|text/javascript" | cut -d' ' -f1 | xargs -I% curl -s % | grep -E "(API_KEY|api_key|apikey|secret|token|password)"
```

Bloc historique recherchant des marqueurs de secrets dans les fichiers JavaScript. Traiter les résultats comme des indices, sans utiliser les secrets trouvés.

#### Google API Keys et Gemini

L'exposition d'une clé Google API n'implique pas systématiquement une vulnérabilité. Le risque dépend des API activées, des restrictions de la clé, des quotas et des permissions associées au projet.

##### Inspection du code source local

```bash
git grep -l 'GEMINI_API_KEY'
```

Liste les fichiers suivis par Git contenant le nom de la variable, sans afficher sa valeur. À utiliser dans un dépôt dont on est propriétaire ou dont l'audit est autorisé. Un résultat peut correspondre à une simple référence à une variable d'environnement et ne confirme pas une fuite.

##### Points de contrôle

- Examiner les fichiers de configuration, les bundles JavaScript et les commits autorisés pour déterminer si une clé a été intégrée au code.
- Distinguer les clés destinées à un usage client des identifiants donnant accès à des services sensibles ou facturables.
- Vérifier les restrictions et les API activées depuis la console du projet, avec l'accord de son propriétaire.
- Ne pas assimiler un code HTTP 400 ou 403 à une preuve de révocation : plusieurs causes sont possibles.

##### Impact potentiel

| Risque | Conséquence possible |
| --- | --- |
| Quotas | Indisponibilité du service légitime |
| Facturation | Consommation non autorisée de ressources payantes |
| File API et Corpora | Exposition ou modification de données, selon les permissions |
| Autres services Google | Accès non prévu à des API activées sur le projet |

L'article cite également Maps, Firebase, Vision, Translate et YouTube Data. L'accès à un service ne prouve pas que les autres sont accessibles.

##### Rapport Bug Bounty

- Indiquer le fichier, l'URL ou le commit d'origine et le contexte de découverte.
- Masquer la valeur de la clé dans le rapport et les captures.
- Distinguer les capacités confirmées avec une autorisation explicite des hypothèses.
- Estimer le risque financier à partir des tarifs officiels, sans générer de dépenses sur un compte tiers.
- Recommander la révocation ou la rotation de la clé exposée, des restrictions adaptées aux API et applications, ainsi que la surveillance des quotas et de la facturation.

##### Documentation

- [Tarifs Gemini API](https://ai.google.dev/gemini-api/docs/pricing).
- [Google API Keys et Gemini - Truffle Security](https://trufflesecurity.com/blog/google-api-keys-werent-secrets-but-then-gemini-changed-the-rules).

Synthèse de l'article fourni, publié le 23 mai 2026. Les procédures de collecte massive, de réutilisation de clés tierces, de contournement des restrictions et de consommation de ressources ne sont pas reproduites. Une clé littérale présente dans le document d'origine n'a pas été publiée.

### Cross-Site Scripting (XSS)

#### Collecte de candidats XSS

```bash
echo https://example.com/ | gau | gf xss | uro | Gxss | kxss | tee xss_output.txt
```

Chaîne d'outils pour repérer des paramètres candidats à une vérification XSS.

#### Analyse XSS avec Dalfox

```bash
cat xss_params.txt | dalfox pipe --blind https://your-collaborator-url --waf-bypass --silence
```

Commande Dalfox historique pour tester des paramètres dans un lab.

> Les options et l'autorisation de tester doivent être vérifiées ; l'archive ne démontre pas la validité de la commande.

#### Recherche de candidats XSS persistants

```bash
cat urls.txt | grep -E "(login|signup|register|forgot|password|reset)" | httpx -silent | nuclei -t nuclei-templates/vulnerabilities/xss/ -severity critical,high
```

Filtre des URL de formulaires et lance des modèles de détection XSS.

> Ce filtrage ne démontre pas qu'une XSS est persistante.

#### Recherche de candidats DOM XSS

```bash
cat js_files.txt | Gxss -c 100 | sort -u | dalfox pipe -o dom_xss_results.txt
```

Combine Gxss et Dalfox sur une liste de fichiers JavaScript.

> Le résultat n'établit pas à lui seul une DOM XSS.

### XSS WAF Bypass Methodology

La fiche archivée ne contient aucun bloc de commandes.

#### Bonnes pratiques

La fiche traite des différences de comportement des filtres WAF selon leur version, les encodages, les attributs HTML et le contexte JavaScript. Pour une évaluation en laboratoire, relever la version et la configuration du filtre, documenter les résultats et vérifier le comportement réel du navigateur. Une réflexion de chaîne ne démontre pas à elle seule une exécution JavaScript. Corriger la cause de la XSS plutôt que de compter uniquement sur le WAF.

### SQL Injection Methodology

La fiche Lostsec fournie contient 22 exemples portant sur la reconnaissance, les tests automatisés, les en-têtes HTTP et les différences entre moteurs SQL. Les exemples historiques ne sont pas tous syntaxiquement valides et n'ont pas été exécutés.

#### Reconnaissance

- Identifier les technologies des services Web autorisés.
- Recenser les URL paramétrées avec les méthodes GAU et Katana déjà présentes dans [Collecte des URL](#collecte-des-url).
- Une extension PHP, ASP ou JSP ne démontre pas une injection SQL.
- Inventorier les paramètres, cookies et en-têtes traités par l'application.

#### Validation en laboratoire

- Distinguer les comportements MySQL, PostgreSQL, Oracle et Microsoft SQL Server.
- La fiche présente notamment les injections aveugles temporelles : une variation de latence doit être comparée à des mesures de référence pour écarter les faux positifs.
- Limiter les tests à des données fictives et ne pas extraire de bases de données réelles.
- Consigner la configuration, les mesures, les observations et les limites du test.
- Recommander les requêtes paramétrées et la réduction des privilèges du compte de base de données.

La fiche comporte aussi des chaînes de tests automatisés en masse et des variantes de contournement de filtres. Elles ne sont pas reproduites dans cette synthèse. Les exemples de reconnaissance déjà présents dans la cheatsheet ne sont pas dupliqués.

#### SQLmap et Ghauri

Les deux outils automatisent des vérifications d'injection SQL. SQLmap couvre plusieurs moteurs et techniques ; Ghauri met notamment l'accent sur les injections aveugles booléennes et temporelles. Le document présente les requêtes GET, POST, JSON et les requêtes HTTP enregistrées depuis Burp Suite.

```bash
sqlmap -hh
```

Affiche l'aide détaillée de la version installée de SQLmap, sans contacter une cible.

Pour une validation en laboratoire, examiner les paramètres transmis, utiliser des comptes de test, conserver les échanges HTTP et respecter les limites de requêtes. Les techniques de contournement de WAF, d'extraction de données et de prise de contrôle du serveur détaillées par l'article ne sont pas reproduites.

[SQLmap et Ghauri - article de référence](https://infosecwriteups.com/mastering-sqlmap-and-ghauri-a-practical-guide-to-waf-bypass-techniques-1aaa9eee9d32) (15 janvier 2026).

#### Ressources de pratique

- [PortSwigger - SQL injection](https://portswigger.net/web-security/sql-injection) : cours et laboratoires dédiés aux injections SQL.
- [PortSwigger - Cross-site scripting](https://portswigger.net/web-security/cross-site-scripting) : cours et laboratoires dédiés aux XSS.

### Local File Inclusion (LFI)

#### Recherche de LFI

```bash
echo "https://example.com/" | gau | gf lfi | uro | sed 's/=.*/=/' | qsreplace "FUZZ" | sort -u | xargs -I{} ffuf -u {} -w payloads/lfi.txt -c -mr "root:(x|\*|\$[^\:]*):0:0:" -v
```

Bloc historique de test LFI avec une liste de charges de test et FFUF.

### Server-Side Request Forgery (SSRF)

Une SSRF survient lorsqu'une application effectue une requête côté serveur vers une destination contrôlée par un utilisateur sans appliquer les restrictions nécessaires. Elle peut exposer des ressources normalement inaccessibles depuis Internet.

#### Types de SSRF

| Type | Observation |
| --- | --- |
| In-band | Le contenu de la réponse distante est renvoyé par l'application. |
| Blind | La requête est effectuée sans restitution directe de son contenu. |
| Semi-blind | Des différences de latence, de statut ou d'erreur fournissent des indices indirects. |

Une interaction DNS isolée ou une variation de temps ne démontre pas à elle seule un accès à une ressource interne.

#### Points d'entrée

- Prévisualisation de liens, import de fichiers distants et webhooks.
- Conversion PDF, traitement d'images SVG et de vidéos.
- Parseurs XML et flux RSS/Atom.
- Mutations GraphQL acceptant des URL et proxys WebSocket.
- En-têtes HTTP interprétés par les composants backend.

Examiner les fonctionnalités qui récupèrent une ressource distante. Les paramètres dont le nom évoque une URL ne constituent pas, à eux seuls, une preuve de SSRF.

#### Serveur HTTP de démonstration locale

```bash
mkdir -p ssrf-lab
printf 'SSRF-LAB-TEST\n' > ssrf-lab/test.txt
python3 -m http.server 8080 --bind 127.0.0.1 --directory ssrf-lab
```

Démarre un serveur de test accessible uniquement depuis la machine locale, avec un fichier témoin fictif. Ne pas exposer un dossier contenant des données personnelles ou des secrets.

#### Validation in-band dans un laboratoire local

```bash
curl -s -i --get 'http://127.0.0.1:8000/api/preview' \
  --data-urlencode 'url=http://127.0.0.1:8080/test.txt'
```

Adaptation de l'exemple de l'article pour un laboratoire local : suppose qu'une application de test déjà disponible sur le port 8000 possède cette route et accepte le paramètre url. Observer si le marqueur SSRF-LAB-TEST apparaît dans la réponse et comparer avec le comportement attendu. Le test ne nécessite pas de consulter des données réelles.

#### Blind SSRF et interactions OOB

L'article présente les outils suivants pour observer les interactions DNS ou HTTP dans un environnement explicitement autorisé :

- [Interactsh](https://github.com/projectdiscovery/interactsh)
- [Burp Collaborator](https://portswigger.net/burp/documentation/collaborator)
- [Webhook.site](https://webhook.site/)
- [RequestRepo](https://requestrepo.com/requests)

Distinguer les interactions provenant du navigateur, du serveur de test et d'intermédiaires. Ne pas transférer de données sensibles vers des services de callback externes.

#### Validation des URL et risques de contournement

L'article décrit les différences de représentation des adresses IP, les divergences entre parseurs d'URL, les protocoles alternatifs, le DNS rebinding et les redirections HTTP. Ces situations justifient des contrôles de destination robustes et cohérents au moment de la connexion, plutôt qu'un simple filtre textuel.

#### Impact potentiel

- Accès involontaire aux services et interfaces internes.
- Exposition de fichiers ou de métadonnées cloud.
- Accès à des identifiants selon la configuration des services concernés.
- Exécution de code à distance dans certaines chaînes de vulnérabilités.

La gravité dépend des capacités réellement démontrées. Ne pas extraire de secrets, cartographier les réseaux privés ou modifier les services d'un tiers pour augmenter artificiellement l'impact du rapport.

#### Remédiation

- Autoriser uniquement les protocoles et destinations nécessaires à la fonctionnalité.
- Normaliser les URL et vérifier les adresses IPv4 et IPv6 obtenues après résolution DNS.
- Bloquer les destinations privées, loopback et link-local lorsqu'elles ne sont pas nécessaires.
- Désactiver les redirections automatiques ou vérifier chaque nouvelle destination.
- Restreindre le trafic sortant du serveur et isoler les composants de conversion.
- Appliquer le principe du moindre privilège aux identités cloud.

#### Rapport Bug Bounty

Documenter la fonctionnalité concernée, le comportement attendu, la requête de test, les observations et les limites de la preuve. Distinguer l'impact confirmé des scénarios possibles. Les montants de primes ne peuvent pas être déduits du type de SSRF seul.

#### Références

- [The Ultimate Guide to SSRF](https://lostsec.medium.com/the-ultimate-guide-to-ssrf-hunting-bypassing-and-exploiting-in-modern-bug-bounty-a43fa34ba324), publié le 24 octobre 2026.
- [PortSwigger - SSRF](https://portswigger.net/web-security/ssrf).

Synthèse de l'article fourni avec adaptation locale des exemples de validation. Les charges de contournement, de collecte d'identifiants cloud, de lecture de fichiers sensibles et de prise de contrôle de services ne sont pas reproduites. Les exemples de laboratoire n'ont pas été exécutés.

### Cross-Origin Resource Sharing (CORS)

#### Vérification des en-têtes CORS

```bash
curl -H "Origin: http://example.com" -I https://example.com/wp-json/
```

Observe les en-têtes renvoyés pour une requête contenant Origin.

#### Analyse avec CORScanner

```bash
python3 CORScanner.py -u https://example.com -d -t 10
```

Recherche des configurations CORS potentiellement incorrectes.

#### Détection CORS avec Nuclei

```bash
cat example.coms.txt | httpx -silent | nuclei -t nuclei-templates/vulnerabilities/cors/ -o cors_results.txt
```

Applique des modèles de détection CORS à des hôtes répondants.

#### Vérification de la réflexion d'Origin

```bash
curl -H "Origin: https://evil.com" -I https://example.com/api/data | grep -i "access-control-allow-origin: https://evil.com"
```

Vérifie si un en-tête de réponse reflète l'origine envoyée.

> La réflexion seule ne suffit pas à démontrer une vulnérabilité exploitable.

### WordPress

#### Analyse WordPress avec WPScan

```bash
wpscan --url https://example.com --disable-tls-checks --api-token YOUR_TOKEN -e at -e ap -e u --enumerate ap --plugins-detection aggressive --force
```

Commande historique d'énumération WordPress et de recherche de vulnérabilités.

> Mode agressif et vérification TLS désactivée dans l'original. Ne pas utiliser tel quel hors d'un lab adapté.

### Microsoft IIS et ASP.NET

#### Identification via HTTP

```bash
curl -I https://example.com
```

Affiche les en-têtes HTTP. Rechercher notamment Server et X-Powered-By ; ces en-têtes peuvent être absents ou modifiés et ne prouvent pas à eux seuls la version réellement installée.

#### Points de contrôle

- **IIS 6 et 7.x** : fonctionnalités héritées, WebDAV, TLS, paramètres ASP.NET et noms courts NTFS (8.3).
- **IIS 8.x** : configuration des handlers, validation des fichiers, anciens composants et messages d'erreur.
- **IIS 10.x** : configuration applicative, contrôle d'accès, diagnostic et dépendances .NET.

Ces points reprennent les axes proposés dans l'article. Ils ne signifient pas que toutes les installations d'une version sont vulnérables.

#### Analyse des composants .NET

[dotPeek](https://www.jetbrains.com/decompiler/) permet d'examiner les assemblies .NET obtenus légitimement, notamment leurs classes et méthodes.

#### ViewState et configuration

Contrôler la protection d'intégrité du ViewState, la gestion des clés, les paramètres de diagnostic, les autorisations WebDAV et les règles de filtrage dans les configurations dont on dispose. L'encodage Base64 ne constitue pas un chiffrement. Vérifier également que les décisions d'accès sont appliquées côté serveur.

[Inventaire des CVE IIS - OpenCVE](https://app.opencve.io/cve/?vendor=microsoft&product=internet_information_services)

Les procédures de contournement d'authentification, de WAF et de génération de charges de désérialisation ne sont pas reproduites.

### React2Shell - CVE-2025-55182

#### Comprendre la vulnérabilité

L'article décrit une désérialisation non sécurisée des données du protocole Flight de React Server Components (RSC), susceptible de permettre une exécution de code à distance sans authentification. Le risque concerne les applications utilisant les composants serveur affectés, notamment certaines configurations Next.js avec App Router. Une détection de React ou Next.js ne démontre pas que l'application est vulnérable.

#### Inventaire et validation

- Identifier les applications et dépendances RSC de son périmètre.
- Comparer les versions installées à l'avis de sécurité officiel ; la liste précise des versions n'est pas lisible dans l'export de l'article.
- Valider la correction dans un environnement de test et conserver les preuves.
- En cas d'exposition confirmée, rechercher les traces d'activité anormale et appliquer les mesures de remédiation appropriées.

#### Ressources

- [Avis de sécurité React](https://github.com/facebook/react/security/advisories/GHSA-fv66-9v8q-g76r).
- [TryHackMe - React2Shell](https://tryhackme.com/room/react2shellcve202555182) : laboratoire présenté dans l'article ; conditions d'accès non vérifiées.

Les procédures de recherche de cibles à grande échelle, d'exécution de commandes, d'exfiltration et de contournement de protections ne sont pas reprises.

### FFUF avec fichier de requête

#### Test LFI à partir d'une requête

```bash
ffuf -request lfi -request-proto https -w /root/wordlists/offensive\ payloads/LFI\ payload.txt -c -mr "root:"
```

Charge une requête HTTP enregistrée et applique une liste de tests LFI.

#### Test XSS à partir d'une requête

```bash
ffuf -request xss -request-proto https -w /root/wordlists/xss-payloads.txt -c -mr "<script>alert('XSS')</script>"
```

Charge une requête HTTP enregistrée et applique une liste de tests XSS.

### Techniques avancées

#### Tests d'en-têtes XSS / SSRF

```bash
cat example.coms.txt | assetfinder --subs-only| httprobe | while read url; do xss1=$(curl -s -L $url -H 'X-Forwarded-For: xss.yourburpcollabrotor'|grep xss) xss2=$(curl -s -L $url -H 'X-Forwarded-Host: xss.yourburpcollabrotor'|grep xss) xss3=$(curl -s -L $url -H 'Host: xss.yourburpcollabrotor'|grep xss) xss4=$(curl -s -L $url --request-target http://burpcollaborator/ --max-time 2); echo -e "\e[1;32m$url\e[0m""\n""Method[1] X-Forwarded-For: xss+ssrf => $xss1""\n""Method[2] X-Forwarded-Host: xss+ssrf ==> $xss2""\n""Method[3] Host: xss+ssrf ==> $xss3""\n""Method[4] GET http://xss.yourburpcollabrotor HTTP/1.1 ""\n";done
```

Bloc historique combinant des requêtes et des vérifications d'en-têtes. Réservé aux environnements de test contrôlés.

> Bloc non vérifié, avec un nom Collaborator mal orthographié et des hypothèses non démontrées.

## Validation et preuves

Objectif : confirmer manuellement les observations, documenter le résultat et démontrer uniquement l'impact nécessaire.

### Analyse et validation

- Examiner les comportements communs, puis les différences entre applications et fonctionnalités.
- Contrôler manuellement les résultats automatisés ; une réponse HTTP 200 ou une chaîne réfléchie ne suffit pas à démontrer une vulnérabilité.
- Utiliser des comptes de test et des données fictives ; ne pas réutiliser de secrets découverts.
- Démontrer uniquement l'impact nécessaire, sans accéder à des données réelles non nécessaires.

### Proof of Concept (PoC)

- Documenter le contexte, les prérequis et les étapes reproductibles.
- Joindre les requêtes et réponses pertinentes, captures ou vidéo de démonstration.
- Masquer les secrets et données personnelles.

### Empreinte des fichiers de preuve

```bash
sha256sum preuves/* > preuves.sha256
```

Calcule les empreintes des fichiers de preuve locaux pour documenter leur intégrité. Ne conserver que des preuves expurgées ; ajout de documentation locale.

## IA et Bug Bounty

L'IA intervient dans l'organisation des résultats, la revue des captures et du code, la préparation de validations manuelles et la rédaction. Les exemples ci-dessous sont adaptés de The Best Claude Code Setup for Bug Bounty Hunting. Conserver une validation humaine des actions réseau.

### Configuration Claude Code et Burp Suite MCP

- Installer l'extension MCP officielle dans Burp Suite : [PortSwigger MCP Server](https://github.com/PortSwigger/mcp-server).
- Vérifier que le serveur SSE écoute localement et que le port correspond à la configuration de l'extension.
- Définir le scope dans Burp Suite avant de connecter le client. Ne pas activer l'approbation automatique globale.

#### Ajouter le serveur MCP Burp

```bash
claude mcp add burp --transport sse http://127.0.0.1:9876
```

Enregistre le serveur MCP SSE local dans Claude Code. Commande de l'article ; nécessite Claude Code installé et un serveur MCP Burp déjà démarré sur ce port. Syntaxe et connexion non testées.

#### Organisation des fichiers du projet

```text
project/
  recon/
    subdomains.txt
    alive.txt
    urls.txt
  requests/
    login.txt
    profile.txt
    api.txt
  javascript/
    app.js
    dashboard.js
    auth.js
  source/
  notes/
```

Structure de travail adaptée des deux arborescences de l'article. Stocker uniquement des copies autorisées et expurgées.

### Prompts d'analyse

#### Historique HTTP Burp

```text
Analyse les requêtes HTTP exportées de Burp et fournies pour le périmètre autorisé.
Liste les méthodes, URL, statuts et paramètres.
Résume les fonctionnalités et distingue login, recherche, panier, paiement et API.
Signale les catégories de données sensibles sans reproduire les valeurs.
N'envoie aucune requête et ne modifie aucun fichier.
```

Transforme l'historique HTTP fourni en inventaire structuré. Adaptation du prompt Proxy History.

#### Cartographie applicative

```text
À partir des captures autorisées, classe les routes par fonctionnalité.
Identifie les paramètres, les identifiants d'objets, les formulaires, les interfaces d'administration et les API.
Indique les contrôles de sécurité attendus et les informations manquantes.
Ne teste pas les routes et n'accède pas à d'autres comptes.
```

Adaptation du prompt Attack Surface pour examiner les observations et définir les contrôles à vérifier manuellement.

#### Analyse JavaScript

```text
Analyse les fichiers JavaScript locaux fournis.
Inventorie les routes API, méthodes, paramètres, logique de session, fonctions d'autorisation, uploads, téléchargements et intégrations tierces.
Repère les sources et sinks DOM, flags de fonctionnalités et références à des secrets sans afficher leur valeur.
Déduplique les routes et cite les fichiers et lignes.
Distingue observations, hypothèses et constats démontrés.
```

Regroupe les trois prompts JavaScript de l'article : fichier individuel, revue du code fourni et analyse d'un dossier.

#### Revue IDOR et BOLA

```text
Analyse la requête de laboratoire fournie et les réponses de mes deux comptes de test.
Identifie le paramètre d'objet et la frontière d'autorisation attendue.
Explique si les preuves démontrent une violation de cette frontière.
Propose des contrôles manuels avec des objets de test uniquement.
Ne conclus pas à une vulnérabilité sans preuve et n'effectue aucune requête.
```

Adaptation du prompt IDOR/BOLA pour des preuves obtenues avec des comptes et objets de test autorisés.

#### Revue du code source

```text
Examine le code source local autorisé.
Évalue authentification, autorisation, validation des entrées, injections, gestion des fichiers, sessions et logique métier.
Pour chaque constat étayé, indique la cause, la ligne concernée, l'impact, la correction et une vérification manuelle en laboratoire.
Ne présente pas une hypothèse comme un fait.
```

Adaptation du prompt Source Code Review.

#### Corrélation des résultats

```text
Corrèle les fichiers locaux de reconnaissance, captures HTTP, JavaScript et code source.
Construis un inventaire des routes, paramètres, contrôles d'accès et fonctionnalités.
Déduplique les observations et classe les vérifications manuelles selon les preuves disponibles.
Sépare les constats confirmés et les hypothèses.
Produis un rapport sans lancer de test actif.
```

Adaptation du prompt de corrélation multi-sources.

#### Rapport de vulnérabilité

```text
À partir des constats validés et des preuves expurgées, rédige un rapport.
Inclure le titre, le composant, la sévérité justifiée, les étapes de reproduction documentées, les preuves, l'impact et la remédiation.
Séparer les observations des vulnérabilités confirmées.
Ne rien inventer.
```

Adaptation du prompt de reporting de l'article.

### Skills Claude Code

#### Créer une skill de revue

```text
À partir de ma méthodologie de revue autorisée, crée une skill Claude Code de lecture seule.
Définis le nom, la description, SKILL.md, les fichiers d'entrée, les étapes d'inventaire et d'analyse, les critères de validation et le format du rapport.
Précise que les hypothèses doivent être séparées des preuves et qu'aucune action réseau ou modification ne doit être lancée automatiquement.
Ne propose pas de technique absente de mes notes.
```

Adaptation des trois prompts de création de skills pour organiser l'analyse, la revue des résultats XSS et Open Redirect et le reporting.

### Provenance

[The Best Claude Code Setup for Bug Bounty Hunting](https://lostsec.medium.com/the-best-claude-code-setup-for-bug-bounty-hunting-a16a0a50e811), 27 août 2026. Les prompts sont reformulés pour l'analyse de données fournies et la validation manuelle ; les workflows de test autonome, les chaînes d'exploitation et les instructions de contournement ne sont pas reproduits. Les exemples HTTP contenant des identifiants de démonstration ne sont pas republiés.

## Rapport et signalement

Objectif : produire un rapport reproductible et transmettre les preuves via le canal prévu par le programme.

### Rapport de vulnérabilité

```markdown
# Titre de la vulnérabilité

## Résumé
Périmètre, fonctionnalité concernée et description.

## Sévérité
Niveau de risque et justification.

## Étapes de reproduction
1. Prérequis et environnement.
2. Étapes et comportement observé.
3. Résultat attendu.

## Impact
Conséquences techniques et métier démontrées.

## Preuves
Captures, requêtes et réponses expurgées.

## Recommandations
Correction et contrôles de vérification.
```

### Avant envoi

- Vérifier l'éligibilité du constat et le périmètre de l'actif.
- Présenter un titre précis, le comportement attendu, le comportement observé et l'impact démontré.
- Joindre les éléments nécessaires en masquant les données personnelles et secrets.
- Respecter les règles de confidentialité et ne pas publier le rapport sans autorisation.

## Suivi et prime

Objectif : accompagner le traitement jusqu'à la clôture du rapport. Une prime n'est jamais garantie.

### Triage

Suivre les demandes de précision, répondre avec les preuves existantes et effectuer de nouveaux tests seulement dans le cadre permis. Le programme peut accepter, refuser, classer comme doublon ou demander des informations supplémentaires.

### Validation de la correction

Si le programme demande un retest, vérifier la correction avec les mêmes conditions de laboratoire ou de test autorisé et communiquer le résultat.

### Récompense

Lorsqu'une prime est attribuée, suivre les instructions de la plateforme concernant les coordonnées de paiement, les éventuelles vérifications d'identité et les délais. Le montant et le versement dépendent du programme et de ses règles. Tenir un suivi des rapports soumis, des réponses et des paiements, sans y enregistrer de secrets.

## Références et compléments

Les ressources sont séparées du parcours pour éviter de confondre un catalogue d'outils avec une étape de travail.

### Références pédagogiques

- Full Bug Bounty Reconnaissance Methodology, Alham Rizvi : reconnaissance, validation DNS, collecte Web et inventaire des API.
- Bug Bounty Hunting Methodology 2025, AmrSec : méthodologie et rapports ; document portant la mention All Rights Reserved. Synthèse originale, pas de republication intégrale.
- Bug Bounty Methodologies : notes de reconnaissance et de tests Web.
- Bug Bounty Hunting Process, HTB Academy : présentation du module et importance du respect du processus de signalement.

### Méthodologies complémentaires

Quatre fiches restent identifiables par leur titre seulement. La fin de la fiche Advanced Recon est également tronquée dans le texte fourni.

- Gather assets through API
- SSTI Payloads
- CRLF Injection
- SQL Injection XOR WAF Bypass


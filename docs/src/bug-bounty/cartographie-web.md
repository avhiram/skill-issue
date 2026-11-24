---
title: Cartographie Web et API
aside: true
prev: false
next: false
---

# Cartographie Web et API

[Retour au parcours](./index.md)

<BountyTarget />

Objectif : inventorier les URL, routes, formulaires, paramètres, scripts et interfaces API dans le périmètre.

## Collecte des URL

### Collecte passive avec Katana

```bash
katana -u subexample.coms_alive.txt -d 5 -ps -pss waybackarchive,commoncrawl,alienvault -kf -jc -fx -ef woff,css,png,svg,jpg,woff2,jpeg,gif,svg -o katana_archive_urls.txt
```

Variante historique. Entrée : `subexample.coms_alive.txt` (filtrage HTTP du chapitre précédent). Sortie : `katana_archive_urls.txt`.

### Collecte avancée avec Katana

```bash
echo example.com | katana -d 5 -ps -pss waybackarchive,commoncrawl,alienvault -f qurl | urldedupe > katana_parameters_raw.txt
katana -u https://example.com -d 5 | grep '=' | urldedupe | anew katana_parameters_raw.txt
cat katana_parameters_raw.txt | sed 's/=.*/=/' > katana_parameters_normalized.txt
```

Enchaînement volontaire : les deux collectes Katana alimentent `katana_parameters_raw.txt`. `anew` ajoute les nouvelles URL sans répéter celles déjà enregistrées. La normalisation produit un fichier distinct.

> Séparation des lignes rétablie grâce aux notes complémentaires ; options et compatibilité à vérifier. La normalisation supprime tout ce qui suit le premier signe égal.

### Collecte avec GAU

```bash
echo example.com | gau --mc 200 | urldedupe > urls.txt
grep -E '\.php|\.asp|\.aspx|\.jspx|\.jsp' urls.txt | grep '=' | sort -u > gau_parameters_raw.txt
cat gau_parameters_raw.txt | sed 's/=.*/=/' > gau_parameters_normalized.txt
```

Enchaînement : GAU produit `urls.txt`, le filtre sélectionne les URL paramétrées dans `gau_parameters_raw.txt`, puis la normalisation crée `gau_parameters_normalized.txt`.

> Séparation des lignes rétablie grâce aux notes complémentaires ; options et compatibilité à vérifier. La normalisation supprime tout ce qui suit le premier signe égal.

### Waybackurls - archives Web

<BountyCommand :source="&quot;waybackurls __BOUNTY_DOMAIN__ &gt; wayback_urls.txt&quot;" language="bash" />

Collecte les URL connues dans les archives.

### Katana - crawling des services Web

```bash
katana -list live_websites.txt -jc -o katana_urls.txt
```

Explore les services Web autorisés et les références JavaScript. Vérifier le format d'entrée.

### Gospider - exploration Web

```bash
gospider -S live_websites.txt -d 2 -o gospider_output/
```

Explore les sites de la liste à une profondeur de deux niveaux.

### AlienVault OTX - collecte historique

```bash
./alienvault.sh example.com
```

Interroge les données publiques d'AlienVault OTX pour recenser les URL associées au domaine autorisé. Le script doit être récupéré et examiné avant exécution ; vérifier son comportement et ses dépendances.

[Script alienvault.sh](https://github.com/coffinxp/scripts/blob/main/alienvault.sh)

### URLScan.io - collecte passive

```bash
python urlscan.py -d example.com --mode urls
python urlscan.py -d example.com --mode subdomains
```

Les deux modes présentés dans l'article récupèrent respectivement les URL et les sous-domaines connus de URLScan.io. Les résultats historiques ne prouvent ni que les ressources sont encore disponibles, ni qu'elles font partie du scope.

[Script urlscan.py](https://github.com/coffinxp/scripts/blob/main/urlscan.py)

### Wayback - filtrage des archives

```bash
./wayback.sh example.com -sc 200,302,403
./wayback.sh example.com -scx 404,500
```

Le premier exemple sélectionne les codes indiqués ; le second les exclut. Les options proviennent de l'article et n'ont pas été testées. Un code HTTP archivé ne garantit pas le statut actuel de la page.

[Script wayback.sh](https://github.com/coffinxp/scripts/blob/main/wayback.sh)

### Gospider - sitemap

```bash
gospider -s https://example.com --sitemap -d 2
```

Explore les URL du sitemap et les liens à une profondeur de deux niveaux. Limiter les requêtes au périmètre autorisé.

### Gospider - proxy HTTP local

```bash
gospider -s https://example.com -p http://127.0.0.1:8080
```

Fait transiter les requêtes par un proxy HTTP local, par exemple Burp Suite, pour observer le trafic du laboratoire. Le proxy doit être démarré et configuré.

[Gospider - dépôt GitHub](https://github.com/jaeles-project/gospider)

### GAU - collecte des archives

<BountyCommand :source="&quot;gau --subs __BOUNTY_DOMAIN__ &gt; archived_urls.txt&quot;" language="bash" />

Alimente le fichier archived_urls.txt utilisé par la fusion des archives. Exemple du document Full Bug Bounty Reconnaissance ; vérifier que les sous-domaines sont dans le scope.

### URLfinder - collecte passive

<BountyCommand :source="&quot;urlfinder -d __BOUNTY_DOMAIN__ | sort -u &gt; urlfinder_urls.txt&quot;" language="bash" />

Collecte et déduplique les URL connues. Variante issue de Recon to Master avec un domaine générique.

### Fusion des URL archivées

```bash
for f in archived_urls.txt wayback_urls.txt urlfinder_urls.txt wayback_cdx.txt; do
  if [ -f "$f" ]; then cat "$f"; fi
done | sort -u > all_archived_urls.txt
```

Fusion volontaire des URL collectées par GAU, Waybackurls, URLfinder et Wayback CDX (chapitre Reconnaissance passive). Les fichiers absents sont ignorés ; vérifier le scope des URL obtenues.

### Extraction des URL avec paramètres

```bash
grep '=' all_archived_urls.txt > parameters.txt
```

Isole les URL contenant un signe égal, puis vérifier manuellement qu'il s'agit de paramètres.

### Repérage des pages de connexion

```bash
grep -Ei 'login|admin|signin|dashboard' all_archived_urls.txt | tee login_endpoints.txt
```

Repère les chemins archivés contenant ces termes ; vérifier leur pertinence et leur périmètre manuellement.

## Crawling complémentaire et nettoyage

### Hakrawler - exploration locale

```bash
printf '%s\n' 'http://127.0.0.1:8000/' | hakrawler -u > hakrawler_urls.txt
```

Explore un site de laboratoire déjà démarré sur le port 8000. L'option -u est reprise du document ; vérifier sa prise en charge dans la version installée.

### GAU - liste de domaines

```bash
gau < scope/domains.txt | sort -u > gau_urls.txt
```

Collecte les URL historiques des domaines listés dans `scope/domains.txt`, fichier à préparer à partir du périmètre du programme.

### Préparer l'inventaire Web

Réunir les résultats bruts pertinents des collectes passives et actives (`all_archived_urls.txt`, `katana_urls.txt`, `katana_archive_urls.txt`, `gau_urls.txt`, etc.). Dédupliquer puis enregistrer uniquement les URL autorisées dans `allurls.txt`, une par ligne. Ne pas mélanger les URL normalisées sans valeurs, les métadonnées HTTP ou les URL du laboratoire local.

### URL avec paramètres

```bash
grep -E '\?[^=]+=.+$' allurls.txt | sort -u > urls_with_params.txt
```

Filtre les URL contenant un paramètre avec une valeur non vide, sans envoyer de requête.

### Inventaire des scripts JavaScript

```bash
grep -Ei '\.js([?#].*)?$' allurls.txt | sort -u > js_inventory.txt
```

Filtre une liste locale d'URL déjà obtenues. L'expression tient aussi compte des paramètres et fragments après l'extension.

### Analyse DOM locale - sources et sinks

```bash
grep -nE 'document\.(location|URL|cookie|domain|referrer)|innerHTML|outerHTML|eval\(|\.write\(' javascript/*.js
```

Repère des sources et sinks JavaScript dans les fichiers locaux autorisés. Un résultat ne constitue pas une preuve de XSS. Adaptation en lecture locale de la commande DOM de l'article.

### Open Redirect - classement des URL

```bash
gf redirect < allurls.txt | sort -u > redirect_candidates.txt
```

Classe les URL locales selon le pattern GF installé. Une correspondance reste un indice à vérifier manuellement.

### Classement SQL Injection avec GF

```bash
gf sqli < allurls.txt > sqli_candidates.txt
```

Classe les URL déjà collectées selon un pattern GF installé. Aucun test réseau ni exploitation n'est effectué ; les correspondances sont des hypothèses.


## Découverte de paramètres

### Recherche passive avec Arjun

```bash
arjun -u https://example.com/endpoint.php -oT arjun_passive.txt -t 10 --rate-limit 10 --passive -m GET,POST --headers "User-Agent: Mozilla/5.0"
```

Recherche des paramètres HTTP avec le mode passif d'Arjun.

### Recherche avec une wordlist Arjun

```bash
arjun -u https://example.com/endpoint.php -oT arjun_wordlist.txt -m GET,POST -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt -t 10 --rate-limit 10 --headers "User-Agent: Mozilla/5.0"
```

Teste des noms de paramètres provenant d'une liste de mots.

### Arjun - export JSON

```bash
arjun -u https://example.com -m GET,POST --stable -oJ params.json
```

Recherche des paramètres dans un environnement autorisé et exporte les résultats en JSON. L'option de sortie a été adaptée au format JSON ; vérifier la version installée.

## JS Recon - méthode manuelle

Dans le navigateur, ouvrir les outils de développement (F12), puis les onglets Network et Sources. Filtrer les ressources JavaScript, relever les chemins et examiner les fichiers dont l'audit est autorisé. LazyEgg et EndPointer peuvent faciliter l'inventaire des références ; voir [Extensions](./ressources.md#browser-extensions).

## Analyse JavaScript

### Collecte et analyse des fichiers JS

```bash
echo example.com | katana -d 5 | grep -E "\.js$" | nuclei -t /path/to/nuclei-templates/http/exposures/ -c 30
```

Collecte des URL JavaScript et applique des modèles d'exposition Nuclei.

### Analyse d'une liste de fichiers JS

```bash
cat alljs.txt | nuclei -t /path/to/nuclei-templates/http/exposures/
```

Prérequis : préparer manuellement `alljs.txt` avec les URL autorisées à tester et vérifier les modèles. Cette variante historique est indépendante du parcours principal.

### Collecte passive des scripts

<BountyCommand :source="&quot;gau --subs __BOUNTY_DOMAIN__ | grep '\\.js$' &gt; js_passive.txt&quot;" language="bash" />

Sélectionne les URL archivées se terminant par .js.

### Collecte active des scripts

```bash
katana -list live_websites.txt -jc -silent | grep '\.js$' > js_active.txt
```

Recense les références JavaScript dans les applications autorisées.

### Fusion des URL JavaScript

```bash
cat js_passive.txt js_active.txt | sort -u > js_all.txt
```

Fusion volontaire des collectes JavaScript passive et active : les deux listes alimentent `js_all.txt`. Si une seule collecte a été effectuée, ne fusionner que le fichier disponible. Les URL restent à vérifier par rapport au scope.

### Validation HTTP des fichiers JavaScript

```bash
httpx -l js_all.txt -mc 200 -o js_live.txt
```

Vérifie les URL de fichiers JavaScript autorisées qui répondent avec un statut HTTP 200. Le fichier `js_all.txt` est issu de la fusion des listes passive et active. Adaptation de l'article JS-Recon ; utiliser HTTPX de ProjectDiscovery.

### Revue de JavaScript local - fichiers à examiner

```bash
grep -rilE 'api[_-]?key|token|password|jwt|secret' javascript/
```

Prérequis : placer les scripts autorisés à examiner dans le dossier javascript/. Liste uniquement les noms des fichiers locaux contenant des termes à examiner, sans afficher les valeurs. Utiliser un dossier de code dont l'audit est autorisé. La présence d'un mot-clé ne démontre pas une fuite.

### Analyse des résultats

Les outils cités dans l'article comprennent JSLeak et LazyEgg, ainsi que Nuclei. Les commandes de collecte Katana et GAU sont déjà présentes ci-dessus. Examiner les références d'API, les routes et les configurations ; masquer les secrets éventuels et ne pas les réutiliser. Les commandes d'extraction automatisée d'identifiants ne sont pas reprises.

## Filtrage des types de contenu

### Pages HTML - extensions

```bash
grep -Ei '\.(php|asp|aspx|jsp|jsf|cfm|pl|perl|cgi|htm|html)([?#].*)?$' allurls.txt | sort -u > html_candidates.txt
```

Conserve les URL complètes de l'inventaire local. L'extension ne garantit pas le type MIME.

### Vérification du type MIME

```bash
grep -i '^content-type:' requests/headers.txt
```

Lit le type MIME dans les en-têtes HTTP enregistrés dans `requests/headers.txt`. `text/html` et `application/xhtml+xml` indiquent du HTML ; `text/javascript` et `application/javascript` indiquent du JavaScript.

Pour les URL JavaScript, réutiliser [Inventaire des scripts JavaScript](#inventaire-des-scripts-javascript), sans refaire une collecte.

## Vérifications complémentaires

La fiche Lostsec fournie en complément reprend une grande partie des commandes de la cheatsheet. Pour éviter les doublons, suivre les rubriques existantes dans l'ordre suivant :

1. [Énumération des sous-domaines](./reconnaissance.md#enumeration-des-sous-domaines) : Subfinder et filtrage HTTP.
2. [Collecte des URL](./cartographie-web.md#collecte-des-url) : Katana, GAU et normalisation des résultats.
3. [Exposition de données](./vulnerabilites.md#exposition-de-donnees) : inspection des références et documents indexés.
4. [Découverte de paramètres](./cartographie-web.md#decouverte-de-parametres) : Arjun.
5. [Cross-Origin Resource Sharing (CORS)](./vulnerabilites.md#cross-origin-resource-sharing-cors) : lecture des en-têtes.
6. [WordPress](./vulnerabilites.md#wordpress) et [analyse JavaScript](./cartographie-web.md#analyse-javascript) : vérification des configurations et ressources.
7. Vérifier les résultats dans le périmètre autorisé et documenter les observations.

### Lecture ciblée des en-têtes CORS

```bash
curl -H 'Origin: http://example.com' -I https://example.com/wp-json/ | grep -i -e 'access-control-allow-origin' -e 'access-control-allow-methods' -e 'access-control-allow-credentials'
```

Affiche les trois en-têtes CORS pertinents. Le domaine tiers figurant dans la fiche a été remplacé par un domaine d'exemple. Un en-tête seul ne suffit pas à établir l'impact.

### Découverte de contenu

Dirsearch et FFUF permettent de cartographier les chemins dans un laboratoire ou un périmètre explicitement autorisé. La fiche contient des variantes récursives ; adapter les limites de débit, les extensions et la wordlist aux règles du programme. Les en-têtes de contournement figurant dans la variante FFUF ne sont pas nécessaires à un inventaire ordinaire.

## Workflow de reconnaissance rapide

L'article [My 5-Minute Workflow to Find Bugs on Any Website](https://infosecwriteups.com/my-5-minute-workflow-to-find-bugs-on-any-website-c20075320c96) (27 septembre 2025, mis à jour le 26 novembre 2025) décrit trois axes : inventaire des expositions CVE, inspection du DOM et collecte automatisée des URL.

- **Shodan et Nuclei** : comparer les informations sur les produits et versions avec l'inventaire des actifs autorisés et les avis de sécurité. L'article présente aussi des scans massifs ; ces procédures ne sont pas reproduites ici.
- **Inspection du DOM** : relever les champs désactivés, en lecture seule ou masqués et les références présentes dans le HTML. Les restrictions côté navigateur ne remplacent pas les contrôles d'autorisation côté serveur. Les bookmarklets modifiant ces restrictions ne sont pas reproduits.
- **Collecte d'URL** : compléter les sources passives avec AlienVault OTX, URLScan.io et les archives Web, puis dédupliquer les résultats et vérifier le scope.
- **Analyse JavaScript** : inventorier les références et endpoints des scripts autorisés. Si une donnée sensible apparaît, la protéger et la signaler sans tenter de réutiliser un identifiant ou un secret.

Les nouvelles commandes de collecte et de crawling sont classées dans [Collecte des URL](./cartographie-web.md#collecte-des-url), sans répéter les commandes existantes. Les scripts de collecte de secrets et les chaînes de scan offensif en masse n'ont pas été ajoutés. Le délai de cinq minutes est une affirmation de l'auteur, pas une garantie de découverte.

## Inventaire API

Relever les routes et méthodes HTTP dans la documentation, les requêtes du navigateur et les captures Burp. Classer les paramètres, les types de réponses et les fonctions nécessitant une authentification.

## Inventaire des champs JSON locaux

```bash
jq 'keys' requests/response.json
```

Prérequis : enregistrer une réponse API de test dans `requests/response.json`. Affiche les clés d'un objet JSON déjà enregistré, sans contacter un service. Exemple local ajouté pour faciliter l'analyse des réponses API.

## Fichiers du chapitre

- `katana_parameters_raw.txt` et `gau_parameters_raw.txt` : résultats distincts des variantes historiques.
- `katana_parameters_normalized.txt` et `gau_parameters_normalized.txt` : paramètres normalisés ; les valeurs originales restent dans les fichiers bruts.
- `arjun_passive.txt`, `arjun_wordlist.txt` et `params.json` : sorties indépendantes.

- `live_websites.txt` : inventaire HTTP à préparer lors de la reconnaissance active.
- `all_archived_urls.txt` : fusion des archives.
- `allurls.txt` : liste d'URL à examiner. Vérifier le scope et réunir les résultats pertinents avant les filtres locaux.
- `parameters.txt` : URL paramétrées issues des archives.
- `js_inventory.txt`, `js_all.txt` : inventaires JavaScript ; ne pas confondre les URL et les fichiers téléchargés.
- `js_live.txt` : résultat de la vérification HTTP des scripts.

Les fichiers de requêtes, scripts externes et wordlists sont des prérequis à préparer séparément. Conserver les ajouts volontaires au même fichier (`anew`, `>>`) et les fusions prévues. Séparer seulement les résultats incompatibles ou les variantes qui risquent de s'écraser.

## Avant de poursuivre

<BountyChecklist storage-key="checkpoint-cartographie-web" :items='["Inventaire des fonctionnalités, URL, paramètres et API.","Résultats enregistrés et observations à vérifier identifiées."]' />

---

[Précédent : Reconnaissance active](./scan-reseau.md) · [Parcours](./index.md) · [Suivant : Tests de vulnérabilités](./vulnerabilites.md)

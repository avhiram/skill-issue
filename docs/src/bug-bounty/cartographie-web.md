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

### Katana - ancien mode passif (historique)

```bash
katana -u subexample.coms_alive.txt -d 5 -ps -pss waybackarchive,commoncrawl,alienvault -kf -jc -fx -ef woff,css,png,svg,jpg,woff2,jpeg,gif,svg -o katana_archive_urls.txt
```

Exemple obsolète : ProjectDiscovery a retiré le mode passif de Katana à partir de la version 1.1.1. Ne pas exécuter ce bloc avec une version actuelle. Utiliser les sections GAU, Waybackurls ou URLfinder déjà présentes pour les archives. Sortie historique : `katana_archive_urls.txt`.

### Katana - ancien workflow de paramètres (historique)

```bash
echo example.com | katana -d 5 -ps -pss waybackarchive,commoncrawl,alienvault -f qurl | urldedupe > katana_parameters_raw.txt
katana -u https://example.com -d 5 | grep '=' | urldedupe | anew katana_parameters_raw.txt
cat katana_parameters_raw.txt | sed 's/=.*/=/' > katana_parameters_normalized.txt
```

Enchaînement historique : les deux collectes alimentent `katana_parameters_raw.txt` ; `anew` ajoute les nouvelles lignes. La première commande utilise le mode passif retiré de Katana. Ce bloc n'est pas une procédure exécutable avec les versions actuelles.

> La normalisation est destructive pour la structure des paramètres : elle supprime tout après le premier `=`. Conserver les URL brutes pour l'analyse.

### Collecte avec GAU

```bash
echo example.com | gau --mc 200 | urldedupe > urls.txt
grep -E '\.php|\.asp|\.aspx|\.jspx|\.jsp' urls.txt | grep '=' | sort -u > gau_parameters_raw.txt
cat gau_parameters_raw.txt | sed 's/=.*/=/' > gau_parameters_normalized.txt
```

GAU produit `urls.txt` à partir des archives (`--mc` filtre les codes enregistrés, pas les réponses actuelles). Le pipeline nécessite `urldedupe`. Les fichiers bruts et normalisés restent distincts.

> Les filtres recherchent des chaînes dans l'URL entière ; ils ne prouvent ni le type de page ni la présence d'un paramètre exploitable. La normalisation supprime aussi les paramètres suivants.

### Waybackurls - archives Web

<BountyCommand :source="&quot;waybackurls __BOUNTY_DOMAIN__ &gt; wayback_urls.txt&quot;" language="bash" />

Collecte les URL historiques dans `wayback_urls.txt`. Leur disponibilité actuelle et leur autorisation ne sont pas établies.

### Katana - crawling des services Web

```bash
katana -list live_websites.txt -jc -o katana_urls.txt
```

Crawling actif. `live_websites.txt` doit contenir une URL autorisée par ligne, sans métadonnées. `-jc` active l'analyse des références JavaScript.

### Gospider - exploration Web

```bash
gospider -S live_websites.txt -d 2 -o gospider_output/
```

Crawling actif à profondeur maximale de deux niveaux. Gospider écrit ses résultats dans `gospider_output/` ; ne pas assimiler ses lignes annotées à une liste d'URL.

### AlienVault OTX - collecte historique

```bash
./alienvault.sh example.com
```

Exemple de script tiers à examiner avant toute exécution. Sa version, ses dépendances et son format de sortie n'ont pas été confirmés ; il ne fait pas partie de la chaîne principale.

[Script alienvault.sh](https://github.com/coffinxp/scripts/blob/main/alienvault.sh)

### URLScan.io - collecte passive

```bash
python urlscan.py -d example.com --mode urls
python urlscan.py -d example.com --mode subdomains
```

Les deux modes sont issus de l'article. Vérifier la version du script, son interpréteur Python et ses dépendances ; les options et sorties n'ont pas été confirmées ici.

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

Active le traitement du sitemap et limite la profondeur de crawling. Les liens découverts ne deviennent pas automatiquement autorisés.

### Gospider - proxy HTTP local

```bash
gospider -s https://example.com -p http://127.0.0.1:8080
```

Configure un proxy HTTP local. Burp doit écouter sur le port indiqué ; vérifier le comportement du proxy et la configuration TLS en laboratoire.

[Gospider - dépôt GitHub](https://github.com/jaeles-project/gospider)

### GAU - collecte des archives

<BountyCommand :source="&quot;gau --subs __BOUNTY_DOMAIN__ &gt; archived_urls.txt&quot;" language="bash" />

Alimente `archived_urls.txt` pour la fusion des archives. `--subs` inclut les sous-domaines dans la recherche ; les URL obtenues doivent être validées avant tout test actif.

### URLfinder - collecte passive

<BountyCommand :source="&quot;urlfinder -d __BOUNTY_DOMAIN__ | sort -u &gt; urlfinder_urls.txt&quot;" language="bash" />

Collecte les URL passives dans `urlfinder_urls.txt`. URLfinder remplace l'ancien mode passif de Katana.

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

Isole les lignes contenant `=`. Ce caractère peut aussi se trouver dans un chemin ou un fragment ; ce filtre ne parse pas les paramètres.

### Repérage des pages de connexion

```bash
grep -Ei 'login|admin|signin|dashboard' all_archived_urls.txt | tee login_endpoints.txt
```

Repère les URL contenant ces termes, y compris dans le domaine ou la query string. Les résultats ne démontrent pas la présence d'une page de connexion.

## Crawling complémentaire et nettoyage

### Hakrawler - exploration locale

```bash
printf '%s\n' 'http://127.0.0.1:8000/' | hakrawler -u > hakrawler_urls.txt
```

Explore un site de laboratoire démarré sur le port 8000. `-u` demande des URL uniques selon la documentation Hakrawler.

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

Heuristique locale : conserve les lignes contenant `?` puis `=` et au moins un caractère. Ne garantit pas que chaque paramètre possède une valeur non vide.

### Inventaire des scripts JavaScript

```bash
grep -Ei '\.js([?#].*)?$' allurls.txt | sort -u > js_inventory.txt
```

Filtre une liste locale d'URL déjà obtenues. L'expression tient aussi compte des paramètres et fragments après l'extension.

### Analyse DOM locale - sources et sinks

```bash
grep -nE 'document\.(location|URL|cookie|domain|referrer)|innerHTML|outerHTML|eval\(|\.write\(' javascript/*.js
```

Repère des références textuelles à des sources et sinks dans les fichiers `.js` directement sous `javascript/`. Ne suit pas les flux de données et ne constitue pas une preuve de XSS.

### Open Redirect - classement des URL

```bash
gf redirect < allurls.txt | sort -u > redirect_candidates.txt
```

Classe les URL locales selon un pattern `redirect` à installer et vérifier séparément dans la configuration GF. Une correspondance reste un indice.

### Classement SQL Injection avec GF

```bash
gf sqli < allurls.txt > sqli_candidates.txt
```

Classe les URL locales selon un pattern `sqli` à installer et vérifier séparément. Aucun test réseau ; une correspondance n'établit pas une injection.


## Découverte de paramètres

### Arjun - sources passives et validation active (historique)

```bash
arjun -u https://example.com/endpoint.php -oT arjun_passive.txt -t 10 --rate-limit 10 --passive -m GET,POST --headers "User-Agent: Mozilla/5.0"
```

Exemple historique non validé. `--passive` enrichit les noms de paramètres à partir de sources publiques, mais Arjun effectue ensuite des requêtes actives. `-m GET,POST` ne correspond pas à une méthode documentée. Ne pas exécuter tel quel.

### Recherche avec une wordlist Arjun

```bash
arjun -u https://example.com/endpoint.php -oT arjun_wordlist.txt -m GET,POST -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt -t 10 --rate-limit 10 --headers "User-Agent: Mozilla/5.0"
```

Exemple historique non validé : le chemin de la wordlist doit être vérifié et `-m GET,POST` n'est pas une méthode documentée. Réserver l'étude de ce bloc au laboratoire.

### Arjun - export JSON

```bash
arjun -u https://example.com -m GET,POST --stable -oJ params.json
```

Exemple historique non validé : `-oJ` désigne l'export JSON et `--stable` privilégie la stabilité. `-m GET,POST` n'est pas une méthode documentée. Ne pas exécuter tel quel.

## JS Recon - méthode manuelle

Dans le navigateur, ouvrir les outils de développement (F12), puis les onglets Network et Sources. Filtrer les ressources JavaScript, relever les chemins et examiner les fichiers dont l'audit est autorisé. LazyEgg et EndPointer peuvent faciliter l'inventaire des références ; voir [Extensions](./ressources.md#browser-extensions).

## Analyse JavaScript

### Collecte et analyse des fichiers JS

```bash
echo example.com | katana -d 5 | grep -E "\.js$" | nuclei -t /path/to/nuclei-templates/http/exposures/ -c 30
```

Variante historique de tests actifs, indépendante du parcours. Le chemin des modèles est un exemple ; les modèles et options n'ont pas été validés.

### Analyse d'une liste de fichiers JS

```bash
cat alljs.txt | nuclei -t /path/to/nuclei-templates/http/exposures/
```

Prérequis : préparer manuellement `alljs.txt` avec les URL autorisées à tester et vérifier les modèles. Cette variante historique est indépendante du parcours principal.

### Collecte passive des scripts

<BountyCommand :source="&quot;gau --subs __BOUNTY_DOMAIN__ | grep '\\.js$' &gt; js_passive.txt&quot;" language="bash" />

Sélectionne uniquement les URL archivées se terminant exactement par `.js`. Les URL avec query string ou fragment sont exclues par ce filtre historique.

### Collecte active des scripts

```bash
katana -list live_websites.txt -jc -silent | grep '\.js$' > js_active.txt
```

Collecte active de références JavaScript ; le filtre historique exclut les URL avec query string ou fragment.

### Fusion des URL JavaScript

```bash
cat js_passive.txt js_active.txt | sort -u > js_all.txt
```

Fusion volontaire des collectes JavaScript passive et active : les deux listes alimentent `js_all.txt`. Si une seule collecte a été effectuée, ne fusionner que le fichier disponible. Les URL restent à vérifier par rapport au scope.

### Validation HTTP des fichiers JavaScript

```bash
httpx -l js_all.txt -mc 200 -o js_live.txt
```

Vérifie les réponses HTTP 200 des URL de scripts autorisées. Ce statut ne garantit pas que la réponse contient du JavaScript. Le fichier `js_all.txt` est issu de la fusion des listes passive et active. Adaptation de l'article JS-Recon ; utiliser HTTPX de ProjectDiscovery.

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

Exemple HTTP HEAD historique. Affiche certains en-têtes CORS ; la requête n'est pas un preflight OPTIONS et ne démontre pas une vulnérabilité.

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

Prérequis : enregistrer une réponse API de test dans `requests/response.json`. Affiche les clés d'un objet JSON déjà enregistré, ou les indices d'un tableau. Requiert un JSON valide ; aucun service n'est contacté. Exemple local ajouté pour faciliter l'analyse des réponses API.

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

## Documentation des outils

- [Katana](https://github.com/projectdiscovery/katana) · [Retrait du mode passif](https://github.com/projectdiscovery/katana/discussions/1114) · [GAU](https://github.com/lc/gau)
- [Gospider](https://github.com/jaeles-project/gospider) · [Hakrawler](https://github.com/hakluke/hakrawler) · [Arjun](https://github.com/s0md3v/Arjun/wiki/Usage) · [GF](https://github.com/tomnomnom/gf)

## Avant de poursuivre

<BountyChecklist storage-key="checkpoint-cartographie-web" :items='["Inventaire des fonctionnalités, URL, paramètres et API.","Résultats enregistrés et observations à vérifier identifiées."]' />

---

[Précédent : Reconnaissance active](./scan-reseau.md) · [Parcours](./index.md) · [Suivant : Tests de vulnérabilités](./vulnerabilites.md)

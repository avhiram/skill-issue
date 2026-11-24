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
katana -u subexample.coms_alive.txt -d 5 -ps -pss waybackarchive,commoncrawl,alienvault -kf -jc -fx -ef woff,css,png,svg,jpg,woff2,jpeg,gif,svg -o allurls.txt
```

Collecte des URL depuis des archives et d'autres sources, en excluant certaines extensions.

### Collecte avancée avec Katana

```bash
echo example.com | katana -d 5 -ps -pss waybackarchive,commoncrawl,alienvault -f qurl | urldedupe > output.txt
katana -u https://example.com -d 5 | grep '=' | urldedupe | anew output.txt
cat output.txt | sed 's/=.*/=/' > final.txt
```

Bloc de collecte et de déduplication des URL paramétrées.

> Séparation des lignes rétablie grâce aux notes complémentaires ; options et compatibilité à vérifier. La normalisation supprime tout ce qui suit le premier signe égal.

### Collecte avec GAU

```bash
echo example.com | gau --mc 200 | urldedupe > urls.txt
grep -E '\.php|\.asp|\.aspx|\.jspx|\.jsp' urls.txt | grep '=' | sort -u > output.txt
cat output.txt | sed 's/=.*/=/' > final.txt
```

Bloc de collecte et de filtrage des URL par extension et paramètres.

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

### Fusion des URL archivées

```bash
cat archived_urls.txt wayback_urls.txt | sort -u > all_archived_urls.txt
```

Regroupe les résultats de GAU et Waybackurls ; les deux fichiers doivent exister.

### Extraction des URL avec paramètres

```bash
grep '=' all_archived_urls.txt > parameters.txt
```

Isole les URL contenant un signe égal, puis vérifier manuellement qu'il s'agit de paramètres.

### Repérage des pages de connexion

```bash
grep -Ei 'login|admin|signin|dashboard' live_websites.txt | tee login_endpoints.txt
```

Repère les services ou titres contenant ces termes ; cela ne constitue pas une preuve de vulnérabilité.

## GAU - collecte des archives

<BountyCommand :source="&quot;gau --subs __BOUNTY_DOMAIN__ &gt; archived_urls.txt&quot;" language="bash" />

Alimente le fichier archived_urls.txt utilisé par la fusion des archives. Exemple du document Full Bug Bounty Reconnaissance ; vérifier que les sous-domaines sont dans le scope.

## URLfinder - collecte passive

<BountyCommand :source="&quot;urlfinder -d __BOUNTY_DOMAIN__ | sort -u &gt; urlfinder_urls.txt&quot;" language="bash" />

Collecte et déduplique les URL connues. Variante issue de Recon to Master avec un domaine générique.

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

Collecte les URL historiques des domaines listés dans le fichier préparé au préalable.

### URL avec paramètres

```bash
grep -E '\?[^=]+=.+$' allurls.txt | sort -u > urls_with_params.txt
```

Filtre les URL contenant un paramètre avec une valeur non vide, sans envoyer de requête.

### Inventaire des scripts JavaScript

```bash
grep -Ei '\.js([?#].*)?### Analyse DOM locale - sources et sinks

```bash
grep -nE 'document\.(location|URL|cookie|domain|referrer)|innerHTML|outerHTML|eval\(|\.write\(' javascript/*.js
```

Repère des sources et sinks JavaScript dans les fichiers locaux autorisés. Un résultat ne constitue pas une preuve de XSS. Adaptation en lecture locale de la commande DOM de l'article.

### Open Redirect - classement des URL

```bash
gf redirect < allurls.txt | sort -u > redirect_candidates.txt
```

Classe les URL locales selon le pattern GF installé. Une correspondance reste un indice à vérifier manuellement.

### Inventaire des paramètres avec GF

```bash
gf sqli < allurls.txt > sqli_candidates.txt
```

Classe les URL déjà collectées selon un pattern GF installé. Aucun test réseau ni exploitation n'est effectué ; les correspondances sont des hypothèses.


## Découverte de paramètres

### Recherche passive avec Arjun

```bash
arjun -u https://example.com/endpoint.php -oT arjun_output.txt -t 10 --rate-limit 10 --passive -m GET,POST --headers "User-Agent: Mozilla/5.0"
```

Recherche des paramètres HTTP avec le mode passif d'Arjun.

### Recherche avec une wordlist Arjun

```bash
arjun -u https://example.com/endpoint.php -oT arjun_output.txt -m GET,POST -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt -t 10 --rate-limit 10 --headers "User-Agent: Mozilla/5.0"
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

Applique des modèles Nuclei à une liste de fichiers JavaScript collectés.

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

Crée une liste unique de scripts à examiner.

### Validation HTTP des fichiers JavaScript

```bash
httpx -l js_all.txt -mc 200 -o js_live.txt
```

Vérifie les URL de fichiers JavaScript autorisées qui répondent avec un statut HTTP 200. Le fichier js_all.txt est issu de la fusion des listes passive et active. Adaptation de l'article JS-Recon ; utiliser HTTPX de ProjectDiscovery.

### Revue de JavaScript local - fichiers à examiner

```bash
grep -rilE 'api[_-]?key|token|password|jwt|secret' javascript/
```

Liste uniquement les noms des fichiers locaux contenant des termes à examiner, sans afficher les valeurs. Utiliser un dossier de code dont l'audit est autorisé. La présence d'un mot-clé ne démontre pas une fuite.

### Analyse des résultats

Les outils cités dans l'article comprennent JSLeak et LazyEgg, ainsi que Nuclei. Les commandes de collecte Katana et GAU sont déjà présentes ci-dessus. Examiner les références d'API, les routes et les configurations ; masquer les secrets éventuels et ne pas les réutiliser. Les commandes d'extraction automatisée d'identifiants ne sont pas reprises.

## Filtrage des types de contenu

### Filtrage du contenu HTML

```bash
echo example.com | gau | grep -Eo '(\/[^\/]+)\.(php|asp|aspx|jsp|jsf|cfm|pl|perl|cgi|htm|html)$' | httpx -status-code -mc 200 -content-type | grep -E 'text/html|application/xhtml+xml'
```

Bloc historique de recherche d'extensions de pages et de filtrage du type MIME.

> Le filtrage extrait des chemins au lieu d'URL complètes ; le fonctionnement n'est pas garanti.

### Filtrage du contenu JavaScript

```bash
echo example.com | gau | grep '\.js-php-jsp-other extens$' | httpx -status-code -mc 200 -content-type | grep 'application/javascript'
```

Bloc historique de filtrage du type MIME JavaScript.

> Expression de filtrage manifestement incomplète dans la source ; non exécutable comme méthode fiable.

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
jq 'keys' response.json
```

Affiche les clés d'un objet JSON déjà enregistré, sans contacter un service. Exemple local ajouté pour faciliter l'analyse des réponses API.

## Avant de poursuivre

- Inventaire des fonctionnalités, URL, paramètres et API.
- Résultats enregistrés et observations à vérifier identifiées.

---

[Précédent : Reconnaissance active](./scan-reseau.md) · [Parcours](./index.md) · [Suivant : Tests de vulnérabilités](./vulnerabilites.md)
 allurls.txt | sort -u > js_inventory.txt
```

Filtre les URL JavaScript de l'inventaire local et supprime les doublons.

### Analyse DOM locale - sources et sinks

```bash
grep -nE 'document\.(location|URL|cookie|domain|referrer)|innerHTML|outerHTML|eval\(|\.write\(' javascript/*.js
```

Repère des sources et sinks JavaScript dans les fichiers locaux autorisés. Un résultat ne constitue pas une preuve de XSS. Adaptation en lecture locale de la commande DOM de l'article.

### Inventaire des paramètres avec GF

```bash
gf sqli < allurls.txt > sqli_candidates.txt
```

Classe les URL déjà collectées selon un pattern GF installé. Aucun test réseau ni exploitation n'est effectué ; les correspondances sont des hypothèses.


## Découverte de paramètres

### Recherche passive avec Arjun

```bash
arjun -u https://example.com/endpoint.php -oT arjun_output.txt -t 10 --rate-limit 10 --passive -m GET,POST --headers "User-Agent: Mozilla/5.0"
```

Recherche des paramètres HTTP avec le mode passif d'Arjun.

### Recherche avec une wordlist Arjun

```bash
arjun -u https://example.com/endpoint.php -oT arjun_output.txt -m GET,POST -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt -t 10 --rate-limit 10 --headers "User-Agent: Mozilla/5.0"
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

Applique des modèles Nuclei à une liste de fichiers JavaScript collectés.

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

Crée une liste unique de scripts à examiner.

### Validation HTTP des fichiers JavaScript

```bash
httpx -l js_all.txt -mc 200 -o js_live.txt
```

Vérifie les URL de fichiers JavaScript autorisées qui répondent avec un statut HTTP 200. Le fichier js_all.txt est issu de la fusion des listes passive et active. Adaptation de l'article JS-Recon ; utiliser HTTPX de ProjectDiscovery.

### Revue de JavaScript local - fichiers à examiner

```bash
grep -rilE 'api[_-]?key|token|password|jwt|secret' javascript/
```

Liste uniquement les noms des fichiers locaux contenant des termes à examiner, sans afficher les valeurs. Utiliser un dossier de code dont l'audit est autorisé. La présence d'un mot-clé ne démontre pas une fuite.

### Analyse des résultats

Les outils cités dans l'article comprennent JSLeak et LazyEgg, ainsi que Nuclei. Les commandes de collecte Katana et GAU sont déjà présentes ci-dessus. Examiner les références d'API, les routes et les configurations ; masquer les secrets éventuels et ne pas les réutiliser. Les commandes d'extraction automatisée d'identifiants ne sont pas reprises.

## Filtrage des types de contenu

### Filtrage du contenu HTML

```bash
echo example.com | gau | grep -Eo '(\/[^\/]+)\.(php|asp|aspx|jsp|jsf|cfm|pl|perl|cgi|htm|html)$' | httpx -status-code -mc 200 -content-type | grep -E 'text/html|application/xhtml+xml'
```

Bloc historique de recherche d'extensions de pages et de filtrage du type MIME.

> Le filtrage extrait des chemins au lieu d'URL complètes ; le fonctionnement n'est pas garanti.

### Filtrage du contenu JavaScript

```bash
echo example.com | gau | grep '\.js-php-jsp-other extens$' | httpx -status-code -mc 200 -content-type | grep 'application/javascript'
```

Bloc historique de filtrage du type MIME JavaScript.

> Expression de filtrage manifestement incomplète dans la source ; non exécutable comme méthode fiable.

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
jq 'keys' response.json
```

Affiche les clés d'un objet JSON déjà enregistré, sans contacter un service. Exemple local ajouté pour faciliter l'analyse des réponses API.

## Avant de poursuivre

- Inventaire des fonctionnalités, URL, paramètres et API.
- Résultats enregistrés et observations à vérifier identifiées.

---

[Précédent : Reconnaissance active](./scan-reseau.md) · [Parcours](./index.md) · [Suivant : Tests de vulnérabilités](./vulnerabilites.md)

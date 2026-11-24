---
title: Bug Bounty
description: Cheatsheet Bug Bounty issue du toolkit archivé Lostsec.
aside: true
prev: false
next: false
---

# Bug Bounty

Cheatsheet et méthodologie classées par sujet, à partir du toolkit Lostsec (28 août 2025) et de quatre documents complémentaires.

[Lostsec - archive originale](https://web.archive.org/web/20250828093634/https://lostsec.xyz/)

Les commandes reproduisent les exemples historiques de la capture ; leur fonctionnement et leur compatibilité avec les versions actuelles des outils n'ont pas été validés. Les blocs manifestement incomplets sont signalés. Utilisation uniquement dans un laboratoire ou dans le périmètre explicitement autorisé d'un programme Bug Bounty. Vérifier les limites de débit, les permissions et les fichiers nécessaires avant tout test.

**[Outils, extensions et writeups](./ressources.md)**

## Cheatsheet

## Énumération des sous-domaines

### Découverte des sous-domaines

```bash
subfinder -d example.com -all -recursive > subexample.com.txt
```

Effectue une recherche récursive avec Subfinder et enregistre les résultats.

### Filtrage des sous-domaines actifs

```bash
cat subexample.com.txt | httpx-toolkit -ports 80,443,8080,8000,8888 -threads 200 > subexample.coms_alive.txt
```

Vérifie les réponses HTTP sur plusieurs ports et enregistre les hôtes répondants.

> La commande emploie une concurrence élevée. Respecter les limites du programme.

### Vérification du risque de Subdomain Takeover

```bash
subzy run --targets subexample.coms.txt --concurrency 100 --hide_fails --verify_ssl
```

Recherche des configurations potentiellement vulnérables avec Subzy.

> Le fichier d'entrée ne porte pas le même nom que celui créé par Subfinder dans le bloc précédent.

### Amass - découverte passive

```bash
amass enum -passive -d example.com -o amass_passive_subs.txt
```

Collecte les sous-domaines depuis des sources publiques.

### Assetfinder - sous-domaines

```bash
assetfinder --subs-only example.com > assetfinder_subs.txt
```

Collecte les noms de sous-domaines connus.

### Findomain - sous-domaines

```bash
findomain -t example.com -q > findomain_subs.txt
```

Collecte les sous-domaines et écrit les résultats dans un fichier.

### Chaos - données publiques

```bash
chaos -d example.com -silent > chaos_subs.txt
```

Interroge le catalogue Chaos de ProjectDiscovery ; vérifier les prérequis d'accès.

### CRT.sh - certificats publics

```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json" |
jq -r '.[].name_value' |
sed 's/\*\.//g' |
anew crtsh_subs.txt
```

Extrait les noms des certificats publics avec jq et retire le préfixe wildcard.

### Fusion des résultats passifs

```bash
cat *_subs.txt | sort -u > all_subs.txt
```

Fusionne les fichiers de résultats en supprimant les doublons. Exécuter dans le dossier contenant uniquement les fichiers concernés.

### DNSX - validation DNS

```bash
dnsx -l all_subs.txt -silent -o resolved_subs.txt
```

Identifie les noms qui répondent aux requêtes DNS.

### DNSX - résolution inverse

```bash
dnsx -ptr -l resolved_subs.txt -resp-only -o reverse_dns.txt
```

Interroge les enregistrements PTR ; utiliser une liste d'adresses IP pour une résolution inverse pertinente, plutôt qu'une liste de noms.

### HTTPX - métadonnées des services

```bash
httpx -l resolved_subs.txt -p 80,443,8080,8443 -silent -title -sc -ip -o live_websites.txt
```

Identifie les services HTTP répondants et collecte titres, codes et adresses IP. Utiliser HTTPX de ProjectDiscovery.

### Httprobe - services Web

```bash
cat resolved_subs.txt | httprobe > live_websites.txt
```

Alternative de détection des services HTTP et HTTPS. Le fichier de sortie est écrasé.

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

```bash
waybackurls example.com > wayback_urls.txt
```

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

## Exposition de données

### Repérage de fichiers sensibles

```bash
cat allurls.txt | grep -E "\.xls|\.xml|\.xlsx|\.json|\.pdf|\.sql|\.doc|\.docx|\.pptx|\.txt|\.zip|\.tar\.gz|\.tgz|\.bak|\.7z|\.rar|\.log|\.cache|\.secret|\.db|\.backup|\.yml|\.gz|\.config|\.csv|\.yaml|\.md|\.md5"
```

Filtre une liste d'URL selon des extensions pouvant indiquer des fichiers exposés.

### Recherche de documents indexés

```text
site:*.example.com (ext:doc OR ext:docx OR ext:odt OR ext:pdf OR ext:rtf OR ext:ppt OR ext:pptx OR ext:csv OR ext:xls OR ext:xlsx OR ext:txt OR ext:xml OR ext:json OR ext:zip OR ext:rar OR ext:md OR ext:log OR ext:bak OR ext:conf OR ext:sql)
```

Requête de moteur de recherche filtrant les extensions de documents dans le périmètre autorisé.

### Détection de dépôts Git exposés

```bash
cat example.coms.txt | grep "SUCCESS" | gf urls | httpx-toolkit -sc -server -cl -path "/.git/" -mc 200 -location -ms "Index of" -probe
```

Vérifie des réponses HTTP pouvant révéler un répertoire Git.

### Filtrage étendu des extensions sensibles

```bash
echo https://example.com | gau | grep -E "\.(xls|xml|xlsx|json|pdf|sql|doc|docx|pptx|txt|zip|tar\.gz|tgz|bak|7z|rar|log|cache|secret|db|backup|yml|gz|config|csv|yaml|md|md5|tar|xz|7zip|p12|pem|key|crt|csr|sh|pl|py|java|class|jar|war|ear|sqlitedb|sqlite3|dbf|db3|accdb|mdb|sqlcipher|gitignore|env|ini|conf|properties|plist|cfg)$"
```

Recherche des extensions de fichiers potentiellement sensibles dans les URL collectées.

### Recherche de buckets AWS S3

```bash
s3scanner scan -d example.com
```

Recherche des buckets associés au domaine indiqué.

### Recherche de secrets dans des fichiers JavaScript

```bash
cat allurls.txt | grep -E "\.js$" | httpx-toolkit -mc 200 -content-type | grep -E "application/javascript|text/javascript" | cut -d' ' -f1 | xargs -I% curl -s % | grep -E "(API_KEY|api_key|apikey|secret|token|password)"
```

Bloc historique recherchant des marqueurs de secrets dans les fichiers JavaScript. Traiter les résultats comme des indices, sans utiliser les secrets trouvés.

## Cross-Site Scripting (XSS)

### Collecte de candidats XSS

```bash
echo https://example.com/ | gau | gf xss | uro | Gxss | kxss | tee xss_output.txt
```

Chaîne d'outils pour repérer des paramètres candidats à une vérification XSS.

### Analyse XSS avec Dalfox

```bash
cat xss_params.txt | dalfox pipe --blind https://your-collaborator-url --waf-bypass --silence
```

Commande Dalfox historique pour tester des paramètres dans un lab.

> Les options et l'autorisation de tester doivent être vérifiées ; l'archive ne démontre pas la validité de la commande.

### Recherche de candidats XSS persistants

```bash
cat urls.txt | grep -E "(login|signup|register|forgot|password|reset)" | httpx -silent | nuclei -t nuclei-templates/vulnerabilities/xss/ -severity critical,high
```

Filtre des URL de formulaires et lance des modèles de détection XSS.

> Ce filtrage ne démontre pas qu'une XSS est persistante.

### Recherche de candidats DOM XSS

```bash
cat js_files.txt | Gxss -c 100 | sort -u | dalfox pipe -o dom_xss_results.txt
```

Combine Gxss et Dalfox sur une liste de fichiers JavaScript.

> Le résultat n'établit pas à lui seul une DOM XSS.

## Local File Inclusion (LFI)

### Recherche de LFI

```bash
echo "https://example.com/" | gau | gf lfi | uro | sed 's/=.*/=/' | qsreplace "FUZZ" | sort -u | xargs -I{} ffuf -u {} -w payloads/lfi.txt -c -mr "root:(x|\*|\$[^\:]*):0:0:" -v
```

Bloc historique de test LFI avec une liste de charges de test et FFUF.

## Cross-Origin Resource Sharing (CORS)

### Vérification des en-têtes CORS

```bash
curl -H "Origin: http://example.com" -I https://example.com/wp-json/
```

Observe les en-têtes renvoyés pour une requête contenant Origin.

### Analyse avec CORScanner

```bash
python3 CORScanner.py -u https://example.com -d -t 10
```

Recherche des configurations CORS potentiellement incorrectes.

### Détection CORS avec Nuclei

```bash
cat example.coms.txt | httpx -silent | nuclei -t nuclei-templates/vulnerabilities/cors/ -o cors_results.txt
```

Applique des modèles de détection CORS à des hôtes répondants.

### Vérification de la réflexion d'Origin

```bash
curl -H "Origin: https://evil.com" -I https://example.com/api/data | grep -i "access-control-allow-origin: https://evil.com"
```

Vérifie si un en-tête de réponse reflète l'origine envoyée.

> La réflexion seule ne suffit pas à démontrer une vulnérabilité exploitable.

## WordPress

### Analyse WordPress avec WPScan

```bash
wpscan --url https://example.com --disable-tls-checks --api-token YOUR_TOKEN -e at -e ap -e u --enumerate ap --plugins-detection aggressive --force
```

Commande historique d'énumération WordPress et de recherche de vulnérabilités.

> Mode agressif et vérification TLS désactivée dans l'original. Ne pas utiliser tel quel hors d'un lab adapté.

## Scan réseau

### Inventaire des ports avec Naabu

```bash
naabu -list ip.txt -c 50 -nmap-cli 'nmap -sV -SC' -o naabu-full.txt
```

Associe Naabu et Nmap pour identifier des ports et services.

### Scan complet avec Nmap

```bash
nmap -p- --min-rate 1000 -T4 -A example.com -oA fullscan
```

Analyse l'ensemble des ports TCP et collecte des informations sur les services.

> Débit et options intrusives à vérifier selon les règles du programme.

### Scan avec Masscan

```bash
masscan -p0-65535 example.com --rate 100000 -oG masscan-results.txt
```

Exemple historique de scan de ports à débit très élevé.

> Débit extrêmement élevé dans l'original ; ne pas exécuter sur des systèmes tiers.

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

```bash
gau --subs example.com | grep '\.js$' > js_passive.txt
```

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

## Shodan

### Recherche par certificat TLS

```text
Ssl.cert.subject.CN:"example.com" 200
```

Requête Shodan historique fondée sur le nom commun d'un certificat.

## FFUF avec fichier de requête

### Test LFI à partir d'une requête

```bash
ffuf -request lfi -request-proto https -w /root/wordlists/offensive\ payloads/LFI\ payload.txt -c -mr "root:"
```

Charge une requête HTTP enregistrée et applique une liste de tests LFI.

### Test XSS à partir d'une requête

```bash
ffuf -request xss -request-proto https -w /root/wordlists/xss-payloads.txt -c -mr "<script>alert('XSS')</script>"
```

Charge une requête HTTP enregistrée et applique une liste de tests XSS.

## Techniques avancées

### Tests d'en-têtes XSS / SSRF

```bash
cat example.coms.txt | assetfinder --subs-only| httprobe | while read url; do xss1=$(curl -s -L $url -H 'X-Forwarded-For: xss.yourburpcollabrotor'|grep xss) xss2=$(curl -s -L $url -H 'X-Forwarded-Host: xss.yourburpcollabrotor'|grep xss) xss3=$(curl -s -L $url -H 'Host: xss.yourburpcollabrotor'|grep xss) xss4=$(curl -s -L $url --request-target http://burpcollaborator/ --max-time 2); echo -e "\e[1;32m$url\e[0m""\n""Method[1] X-Forwarded-For: xss+ssrf => $xss1""\n""Method[2] X-Forwarded-Host: xss+ssrf ==> $xss2""\n""Method[3] Host: xss+ssrf ==> $xss3""\n""Method[4] GET http://xss.yourburpcollabrotor HTTP/1.1 ""\n";done
```

Bloc historique combinant des requêtes et des vérifications d'en-têtes. Réservé aux environnements de test contrôlés.

> Bloc non vérifié, avec un nom Collaborator mal orthographié et des hypothèses non démontrées.


## Méthodologie de Bug Bounty

### Préparation

- Lire le scope, les exclusions, les limites de débit et les règles de divulgation du programme.
- Distinguer les domaines autorisés des noms simplement découverts. Un certificat, un ASN ou une archive ne prouve pas qu'un service est dans le scope.
- Préparer un dossier de travail et conserver les résultats intermédiaires.

### Reconnaissance et cartographie

- Commencer par la collecte passive, puis dédupliquer les sous-domaines.
- Résoudre les noms autorisés, identifier les services Web et inventorier les technologies.
- Regrouper les URL archivées, les URL découvertes par crawling, les paramètres et les références JavaScript.
- Identifier les API, les interfaces d'administration et les ressources cloud pertinentes. Vérifier l'autorisation avant toute requête active.
- Privilégier la qualité des résultats à la multiplication des outils.

### Analyse et validation

- Examiner les comportements communs, puis les différences entre applications et fonctionnalités.
- Contrôler manuellement les résultats automatisés ; une réponse HTTP 200 ou une chaîne réfléchie ne suffit pas à démontrer une vulnérabilité.
- Utiliser des comptes de test et des données fictives ; ne pas réutiliser de secrets découverts.
- Démontrer uniquement l'impact nécessaire, sans accéder à des données réelles non nécessaires.

### Proof of Concept (PoC)

- Documenter le contexte, les prérequis et les étapes reproductibles.
- Joindre les requêtes et réponses pertinentes, captures ou vidéo de démonstration.
- Masquer les secrets et données personnelles.

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

## Références pédagogiques

- Full Bug Bounty Reconnaissance Methodology, Alham Rizvi : reconnaissance, validation DNS, collecte Web et inventaire des API.
- Bug Bounty Hunting Methodology 2025, AmrSec : méthodologie et rapports ; document portant la mention All Rights Reserved. Synthèse originale, pas de republication intégrale.
- Bug Bounty Methodologies : notes de reconnaissance et de tests Web.
- Bug Bounty Hunting Process, HTB Academy : présentation du module et importance du respect du processus de signalement.

## Advanced Recon Methodology

La fiche Lostsec fournie en complément reprend une grande partie des commandes de la cheatsheet. Pour éviter les doublons, suivre les rubriques existantes dans l'ordre suivant :

1. [Énumération des sous-domaines](#enumeration-des-sous-domaines) : Subfinder et filtrage HTTP.
2. [Collecte des URL](#collecte-des-url) : Katana, GAU et normalisation des résultats.
3. [Exposition de données](#exposition-de-donnees) : inspection des références et documents indexés.
4. [Découverte de paramètres](#decouverte-de-parametres) : Arjun.
5. [Cross-Origin Resource Sharing (CORS)](#cross-origin-resource-sharing-cors) : lecture des en-têtes.
6. [WordPress](#wordpress) et [analyse JavaScript](#analyse-javascript) : vérification des configurations et ressources.
7. Vérifier les résultats dans le périmètre autorisé et documenter les observations.

### Lecture ciblée des en-têtes CORS

```bash
curl -H 'Origin: http://example.com' -I https://example.com/wp-json/ | grep -i -e 'access-control-allow-origin' -e 'access-control-allow-methods' -e 'access-control-allow-credentials'
```

Affiche les trois en-têtes CORS pertinents. Le domaine tiers figurant dans la fiche a été remplacé par un domaine d'exemple. Un en-tête seul ne suffit pas à établir l'impact.

### Découverte de contenu

Dirsearch et FFUF permettent de cartographier les chemins dans un laboratoire ou un périmètre explicitement autorisé. La fiche contient des variantes récursives ; adapter les limites de débit, les extensions et la wordlist aux règles du programme. Les en-têtes de contournement figurant dans la variante FFUF ne sont pas nécessaires à un inventaire ordinaire.

## Advanced Google Dorks Methodology

La fiche archivée ne contient pas de commandes supplémentaires.

### Bonnes pratiques

- Remplacer example.com par le domaine autorisé.
- Utiliser la notation [.] lors de la documentation pour éviter la création automatique de liens.
- Combiner les opérateurs de recherche et utiliser les guillemets pour les expressions exactes.
- Exclure les résultats non pertinents avec `-site:` et utiliser les filtres de date.
- Surveiller les nouvelles expositions dans le périmètre autorisé.
- Documenter et vérifier chaque observation avant le signalement.

Voir également [Exposition de données](#exposition-de-donnees) pour les requêtes déjà présentes.

## XSS WAF Bypass Methodology

La fiche archivée ne contient aucun bloc de commandes.

### Bonnes pratiques

La fiche traite des différences de comportement des filtres WAF selon leur version, les encodages, les attributs HTML et le contexte JavaScript. Pour une évaluation en laboratoire, relever la version et la configuration du filtre, documenter les résultats et vérifier le comportement réel du navigateur. Une réflexion de chaîne ne démontre pas à elle seule une exécution JavaScript. Corriger la cause de la XSS plutôt que de compter uniquement sur le WAF.

## SQL Injection Methodology

La fiche Lostsec fournie contient 22 exemples portant sur la reconnaissance, les tests automatisés, les en-têtes HTTP et les différences entre moteurs SQL. Les exemples historiques ne sont pas tous syntaxiquement valides et n'ont pas été exécutés.

### Reconnaissance

- Identifier les technologies des services Web autorisés.
- Recenser les URL paramétrées avec les méthodes GAU et Katana déjà présentes dans [Collecte des URL](#collecte-des-url).
- Une extension PHP, ASP ou JSP ne démontre pas une injection SQL.
- Inventorier les paramètres, cookies et en-têtes traités par l'application.

### Validation en laboratoire

- Distinguer les comportements MySQL, PostgreSQL, Oracle et Microsoft SQL Server.
- La fiche présente notamment les injections aveugles temporelles : une variation de latence doit être comparée à des mesures de référence pour écarter les faux positifs.
- Limiter les tests à des données fictives et ne pas extraire de bases de données réelles.
- Consigner la configuration, les mesures, les observations et les limites du test.
- Recommander les requêtes paramétrées et la réduction des privilèges du compte de base de données.

La fiche comporte aussi des chaînes de tests automatisés en masse et des variantes de contournement de filtres. Elles ne sont pas reproduites dans cette synthèse. Les exemples de reconnaissance déjà présents dans la cheatsheet ne sont pas dupliqués.

### Ressources de pratique

- [PortSwigger - SQL injection](https://portswigger.net/web-security/sql-injection) : cours et laboratoires dédiés aux injections SQL.
- [PortSwigger - Cross-site scripting](https://portswigger.net/web-security/cross-site-scripting) : cours et laboratoires dédiés aux XSS.

## Méthodologies complémentaires

Quatre fiches restent identifiables par leur titre seulement. La fin de la fiche Advanced Recon est également tronquée dans le texte fourni.

- Gather assets through API
- SSTI Payloads
- CRLF Injection
- SQL Injection XOR WAF Bypass

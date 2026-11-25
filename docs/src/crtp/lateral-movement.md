# Lateral Movement

Étude des mécanismes d'administration distante Windows et des risques liés à la réutilisation des identités.

## PowerShell Remoting

WinRM implémente WS-Management. Les ports habituels sont TCP 5985 pour HTTP et 5986 pour HTTPS.

### Sessions interactives et persistantes

New-PSSession crée une session persistante ; Enter-PSSession permet une interaction avec une session. Invoke-Command permet notamment l'administration de plusieurs systèmes. Les notes distinguent les sessions stateful des exécutions ponctuelles.

### Processus PowerShell

```powershell
Get-PSHostProcessInfo
```

Inventorie les processus hébergeant PowerShell.

### Session interactive

```powershell
Enter-PSSession -ComputerName Server1
```

Ouvre une session PowerShell interactive sur le serveur de laboratoire Server1, avec les droits de l'identité authentifiée.

### Créer une session persistante

```powershell
$machine = New-PSSession -ComputerName Server1
```

Crée une session distante réutilisable et conserve son objet dans la variable $machine.

### Inventaire des processus sur plusieurs serveurs

```powershell
Invoke-Command -ScriptBlock { Get-Process } -ComputerName (Get-Content C:\scripts\servers.txt)
```

Interroge les processus des serveurs administrés dont les noms figurent dans le fichier servers.txt. Le chemin remplace le placeholder du document original.

### Conserver un état entre deux appels

```powershell
$Sess = New-PSSession -ComputerName Server1
Invoke-Command -Session $Sess -ScriptBlock { $Proc = Get-Process }
Invoke-Command -Session $Sess -ScriptBlock { $Proc.Name }
```

Crée une session distante, y conserve les objets processus et affiche leurs noms lors d'un second appel.

## Administration distante

Le document cite également WinRS et les interfaces WSMan. Contrôler l'autorisation des connexions, les identités utilisées et la journalisation des sessions.

## Credential Access

Mimikatz, SafetyKatz, SharpKatz, Dumpert, pypykatz et les mécanismes de dump de processus sont présentés dans la source. Ils illustrent le risque d'exposition des éléments d'authentification en mémoire.

## Over-Pass-The-Hash

Les notes décrivent la réutilisation de clés ou d'empreintes d'authentification pour obtenir un contexte Kerberos. Il convient de distinguer le risque de réutilisation NTLM et celui de réutilisation de tickets Kerberos.

## DCSync

DCSync détourne les droits de réplication AD. La revue doit porter sur les comptes autorisés à répliquer les données et sur les opérations de réplication inhabituelles.

Voir [AD Defense](./defense.md) pour les contrôles et la détection.

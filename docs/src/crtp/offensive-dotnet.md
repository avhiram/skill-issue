# Offensive .NET

Le chapitre source étudie les outils C#/.NET utilisés dans les exercices CRTP, les mécanismes de détection et la livraison d'assemblies.

## Détection par signature

Les notes présentent DefenderCheck, SharpKatz, SafetyKatz, BetterSafetyKatz et Rubeus dans le contexte de la détection de signatures. L'obfuscation et la manipulation de chaînes compliquent certaines détections statiques ; elles ne garantissent pas l'absence de détection comportementale.

## Chargement d'assemblies

Le document aborde NetLoader et AssemblyLoad, ainsi que les mécanismes AMSI, ETW et la journalisation. Ces sujets sont étudiés ici sous l'angle des surfaces d'exécution et des contrôles de sécurité.

## Constrained Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Affiche le mode de langage PowerShell de la session courante.

## AppLocker

### Politique effective

```powershell
Get-AppLockerPolicy -Effective | Select-Object -ExpandProperty RuleCollections
```

Affiche les collections de règles de la politique effective.

### Configuration du registre

```cmd
reg query HKLM\Software\Policies\Microsoft\Windows\SRPV2
```

Consulte la configuration AppLocker accessible dans le registre.

## Identification de la session

Les deux commandes suivantes sont extraites des exemples de diagnostic du document de 2023 et présentées séparément.

### Identifier la machine

```cmd
hostname
```

Affiche le nom de la machine sur laquelle la commande est exécutée.

### Identifier le compte courant

```cmd
whoami
```

Affiche l'identité Windows de la session courante.

## Compléments d'audit

Ces vérifications de configuration et de journalisation complètent les notes originales ; elles ne figurent pas dans le document de 2023.

### État de Microsoft Defender

```powershell
Get-MpComputerStatus | Select-Object AntivirusEnabled,RealTimeProtectionEnabled,AntivirusSignatureLastUpdated
```

Consulte l'état de l'antivirus, de la protection en temps réel et la date de mise à jour des signatures. Nécessite le module Defender.

### Journal AppLocker

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-AppLocker/EXE and DLL' -MaxEvents 20
```

Consulte les vingt événements les plus récents du journal AppLocker EXE and DLL, si le journal est disponible et accessible.

### Journal PowerShell

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -MaxEvents 20
```

Consulte les vingt événements opérationnels PowerShell les plus récents. Les événements disponibles dépendent de la configuration de journalisation.

## Points de contrôle

- Politique de contrôle des applications.
- Restrictions PowerShell.
- Journalisation des scripts.
- Contrôle des assemblies et des binaires.
- Analyse des chemins d'administration privilégiée.

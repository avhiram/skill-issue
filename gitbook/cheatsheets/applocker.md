# Windows AppLocker — Audit des règles d'exécution

## Fonctionnement

AppLocker contrôle l'exécution d'applications selon des règles **Allow / Deny**. Les conditions peuvent reposer sur l'éditeur, le chemin ou l'empreinte du fichier.

## Collections de règles

| Collection | Type de fichier |
| --- | --- |
| Exe | Exécutables |
| Script | Scripts |
| Msi | Installateurs |
| Appx | Applications empaquetées |
| Dll | Bibliothèques |

## Commandes de diagnostic

### Afficher la stratégie effective

```powershell
Get-AppLockerPolicy -Effective -Xml
```

Permet d'inspecter la politique effectivement appliquée sur la machine.

### Examiner les collections de règles

```powershell
$policy = Get-AppLockerPolicy -Effective
$policy.RuleCollections
```

### Examiner les clés de configuration

```powershell
Get-ChildItem 'HKLM:\Software\Policies\Microsoft\Windows\SrpV2'
```

### Vérifier le mode de langage PowerShell

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Le mode de langage constitue un indicateur du contexte de restriction, mais ne prouve pas à lui seul qu'AppLocker est actif.

### Tester une politique sans exécuter de programme

```powershell
Test-AppLockerPolicy -PolicyObject $policy -Path 'C:\Windows\System32\notepad.exe' -User 'Everyone'
```

Adapter le compte et le chemin au contexte réel.

## Points de contrôle

- Identifier les règles héritées des GPO et les règles locales.
- Vérifier les collections réellement appliquées.
- Examiner les permissions des répertoires visés par les règles de chemin.
- Contrôler les journaux **Microsoft-Windows-AppLocker**.

**Source :** [AppLocker — CRTO-Study-Notes](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/cheatsheets/applocker.md). Cette fiche couvre l'audit et la validation, sans les procédures de contournement.

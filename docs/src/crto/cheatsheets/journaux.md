# Journaux et stratégie Windows

## Lire les décisions AppLocker

Sur un poste Windows qui journalise les décisions AppLocker, cette requête PowerShell affiche les vingt derniers événements concernant les exécutables et les DLL.

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Microsoft-Windows-AppLocker/EXE and DLL'
    Id = 8002, 8003, 8004
} -MaxEvents 20 | Select-Object TimeCreated, Id, Message
```

## Lire les demandes de tickets Kerberos

Sur une copie du journal Security d’un contrôleur de domaine, saisissez le chemin du fichier EVTX. PowerShell affiche les demandes de TGT et de tickets de service présentes dans cette copie.

```powershell
$journal = Read-Host 'Chemin complet du fichier Security.evtx'
Get-WinEvent -FilterHashtable @{
    Path = $journal
    Id = 4768, 4769
} -MaxEvents 30 | Select-Object TimeCreated, Id, Message
```

## Vérifier l’empreinte d’un export

Saisissez le chemin d’un fichier exporté. Comparez le SHA-256 obtenu à l’empreinte relevée lors de la collecte.

```powershell
$fichier = Read-Host 'Chemin complet du fichier exporté'
Get-FileHash -LiteralPath $fichier -Algorithm SHA256
```

## Afficher les Group Policies de l’utilisateur

Depuis la session Windows concernée, affichez le résumé des stratégies appliquées à l’utilisateur. Le résultat dépend des données de stratégie disponibles sur ce poste.

```bat
gpresult /scope user /r
```

## Vérifier les langues et méthodes de saisie

Dans Windows PowerShell, le module International affiche les langues configurées pour l’utilisateur et leurs méthodes de saisie. Cette liste aide à expliquer une différence de clavier dans un lab.

```powershell
Get-WinUserLanguageList | Select-Object LanguageTag, InputMethodTips
```

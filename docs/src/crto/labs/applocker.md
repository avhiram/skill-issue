# Interpréter une décision AppLocker

## Objectif et prérequis

Distinguer une autorisation, un blocage simulé et un blocage appliqué. Utilisez un poste Windows de laboratoire avec AppLocker et un compte autorisé à lire le journal. L’exercice porte sur la collection EXE et DLL.

## Lire les décisions récentes

Cette commande PowerShell affiche jusqu’à vingt décisions du journal local, avec l’heure et le message associé au fichier.

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Microsoft-Windows-AppLocker/EXE and DLL'
    Id = 8002, 8003, 8004
} -MaxEvents 20 | Select-Object TimeCreated, Id, Message
```

## Interpréter le résultat

| Événement | Conclusion pour le fichier concerné |
|---|---|
| 8002 | AppLocker a autorisé son exécution. |
| 8003 | AppLocker l’a autorisé en mode audit. La règle l’aurait bloqué en mode appliqué. |
| 8004 | AppLocker a bloqué son exécution. |

## Vérification et dépannage

Relevez le chemin et le compte dans le message. Si le journal contient un 8003, un rapport qui annonce un blocage effectif est incorrect. Si la recherche ne renvoie aucune entrée, vérifier le poste, la collection et les droits de lecture. Un journal vide ne suffit pas à établir qu’un fichier a été autorisé.

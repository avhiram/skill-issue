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

## Points de contrôle

- Politique de contrôle des applications.
- Restrictions PowerShell.
- Journalisation des scripts.
- Contrôle des assemblies et des binaires.
- Analyse des chemins d'administration privilégiée.

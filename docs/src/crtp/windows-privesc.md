# Windows PrivEsc

Revue des configurations Windows susceptibles d'entraîner une élévation locale de privilèges.

## Points de contrôle

- Correctifs manquants.
- Déploiement automatisé et AutoLogon.
- AlwaysInstallElevated.
- Services mal configurés.
- DLL Hijacking.
- NTLM Relaying.

## Services et PowerUp

Les trois vérifications ci-dessous proviennent du chapitre source et nécessitent PowerUp dans un laboratoire autorisé.

### Chemins de services non quotés

```powershell
Get-ServiceUnquoted -Verbose
```

Identifie des chemins de service non entourés de guillemets.

### Fichiers de services modifiables

```powershell
Get-ModifiableServiceFile -Verbose
```

Recense les fichiers de services modifiables par l'identité courante.

### Configuration de services modifiable

```powershell
Get-ModifiableService -Verbose
```

Identifie les services dont la configuration est modifiable.

## Inventaire des administrateurs locaux

```cmd
net localgroup Administrators
```

Affiche les membres du groupe Administrators sur une installation anglophone.

## Audit automatisé

Le document présente PowerUp, Privesc et winPEAS comme outils complémentaires. Examiner leurs résultats et confirmer manuellement les configurations avant toute conclusion.

## Jenkins

Les notes illustrent le risque des droits d'administration ou de modification de tâches de build : les consoles et étapes de compilation peuvent exécuter du code dans le contexte du service. Vérifier les permissions et l'isolation des agents.

## Ressources

- [PowerSploit - Privesc](https://github.com/PowerShellMafia/PowerSploit/tree/master/Privesc)
- [Privesc](https://github.com/enjoiz/Privesc)
- [winPEAS](https://github.com/carlospolop/PEASS-ng/tree/master/winPEAS)

# Cobalt Strike — Interface et commandes de base

## Beacon Interact

La console Cobalt Strike utilise une fenêtre **Interact** :

- **Volet supérieur :** résultats des commandes.
- **Volet inférieur :** saisie des commandes.
- **Autocomplétion :** disponible sur de nombreuses commandes.

## Référence de navigation

### Identifier le contexte utilisateur

```text
getuid
```

### Afficher le répertoire courant

```text
pwd
```

### Lister les fichiers

```text
ls
```

### Changer de répertoire

```text
cd C:\Windows\Temp
```

### Afficher les variables d'environnement

```text
env
```

### Consulter la configuration réseau

```text
ipconfig
```

### Examiner les connexions réseau

```text
netstat
```

## Gestion de l'environnement

La source distingue les commandes par niveaux **SAFE**, **CAUTION** et **UNSAFE**. Ces catégories correspondent à son contexte de laboratoire : elles ne constituent **pas une garantie d'absence de télémétrie ou de détection**.

| Catégorie | Signification |
| --- | --- |
| SAFE | Activité considérée comme relativement discrète dans le scénario de la source |
| CAUTION | Activité susceptible de produire des traces significatives |
| UNSAFE | Activité particulièrement visible ou risquée dans ce scénario |

Les commandes d'injection, de manipulation de jetons et de déploiement furtif sont exclues de cette fiche d'introduction.

**Source :** [Cobalt Strike Primer — CRTO-Study-Notes](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/cheatsheets/cobalt-strike-primer.md).

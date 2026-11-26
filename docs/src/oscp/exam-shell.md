---
title: "OSCP · Shell interactif"
description: "Stabilisation du terminal Linux dans un laboratoire autorisé."
prev: false
next: false
---

# Shell interactif (TTY)

À partir d’un shell Linux déjà ouvert dans le laboratoire. Cette procédure améliore l’interactivité, sans modifier les privilèges du compte.

## Vérifier Python

**Shell distant (ex. `www-data`)**

```bash
command -v python3 python
```

## Ouvrir un pseudo-terminal

**Shell distant · Python 3**

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

**Si seul Python est disponible**

```bash
python -c 'import pty; pty.spawn("/bin/bash")'
```

Utiliser une seule des deux commandes.

## Mettre la session en arrière-plan

Appuyer sur **Ctrl + Z** pour revenir au terminal Kali.

## Relever les dimensions

**Kali**

```bash
echo $TERM
stty size
```

Exemple de résultat :

```text
xterm-256color
40 120
```

`40` = lignes (hauteur), `120` = colonnes (largeur). Noter les valeurs réellement affichées.

## Reprendre la session

**Kali**

```bash
stty raw -echo; fg
```

Dans le shell distant, saisir `reset` puis Entrée. Si le type de terminal est demandé, renseigner la valeur obtenue avec `echo $TERM`.

## Régler le terminal distant

**Shell distant**

```bash
export TERM=xterm-256color
export SHELL=/bin/bash
stty rows 40 columns 120
```

Remplacer `xterm-256color`, `40` et `120` par les valeurs relevées sur Kali. La dernière commande adapte la hauteur et la largeur du pseudo-terminal distant à celles de la fenêtre locale.

## Dépannage

Si le terminal Kali reste inutilisable après la fermeture de la connexion :

```bash
stty sane
reset
```

::: details Notes
- Bash et Python doivent être disponibles sur le système distant.
- Un pseudo-terminal ne garantit pas la stabilité de la connexion réseau.
- `Ctrl + Z` et `fg` nécessitent un shell local avec gestion des tâches. Bash n’est pas obligatoire si le shell local le permet.
:::

[Référence complète : terminaux interactifs](./utilitaires.md#améliorer-les-shells-interactifs)

[Retour à Exam Mode](./exam.md)

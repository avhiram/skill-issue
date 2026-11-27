---
title: Cheatsheet eJPT
prev: false
next: false
---

# Cheatsheet

Première fiche de révision des fondamentaux, à utiliser sur tes propres machines et laboratoires autorisés.

## Réseau

::: details Adresses IP
### Linux

Afficher les interfaces et adresses IP.

```bash
ip a
ip -br -c a
```

### Windows

```powershell
ipconfig /all
```
:::

::: details Routage
### Linux

Afficher la table de routage.

```bash
ip route
```

### Windows

```powershell
route print
```
:::

::: details Voisins réseau
### Linux

```bash
ip neighbour
```

### Windows

```powershell
arp -a
```
:::

::: details Ports locaux
### Linux

Afficher les sockets TCP en écoute.

```bash
ss -tnl
```

### Windows

Afficher les connexions et processus associés.

```powershell
netstat -ano
```
:::

## Notes originales

- [Cheatsheet eJPT originale](https://github.com/e-hakson/eJPT/blob/7e20a68c70b4a9fe086e9174138e0468eb375886/ejpt-cheatsheet.md)
- [Version sans liens](https://github.com/e-hakson/eJPT/blob/7e20a68c70b4a9fe086e9174138e0468eb375886/cheatsheet-files/ejpt-cheatsheet_nolinks.md)

::: info En construction
Cette première fiche ne couvre que les fondamentaux. Le fichier supplémentaire fourni et les autres thèmes seront traités séparément.
:::

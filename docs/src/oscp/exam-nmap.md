---
title: "OSCP · Exam Mode · Nmap"
description: "Quatre scans Nmap en laboratoire autorisé : découverte, inventaire TCP, analyse des services et UDP indépendant."
prev: false
next: false
---

# Scan Nmap

<LabVariables />

## Découverte des hôtes

<LabCommand source='sudo nmap -sn -n "$SUBNET"' />

## TCP · Tous les ports

<LabCommand source='sudo nmap -sS -p- --min-rate 1000 -T4 -n -Pn "$IP"' />

## TCP · Services détectés

Renseigner les ports ouverts.

<LabCommand source='sudo nmap -A -p "$TCP_PORTS" -n -Pn "$IP"' />

## UDP · Tous les ports

Dans un second terminal.

<LabCommand source='sudo nmap -sU -p- -n -Pn "$IP"' />

::: details Points de vigilance
- La découverte ne garantit pas que tous les hôtes répondent. Utiliser `-Pn` uniquement sur les machines connues et autorisées.
- `--min-rate 1000` est un débit minimal demandé, pas une limite maximale. Réduire le débit et confirmer les résultats si des pertes sont suspectées.
- Un scan UDP intégral peut durer plusieurs heures. Aucun débit minimal forcé pour UDP.
- Les ports UDP `open|filtered` nécessitent une vérification ciblée ; le scan UDP d’inventaire ne garantit pas l’identification de leurs versions.
- Vérifier les règles de l’épreuve et le comportement des scripts NSE. Aucun scan ne garantit de détecter tous les services.
:::

[**Services par port →**](./exam-ports.md)

::: details Références
[Notes Nmap complètes](./reconnaissance.md#nmap) · [Documentation Nmap](https://nmap.org/book/man-port-specification.html)
:::

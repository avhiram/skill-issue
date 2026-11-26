---
title: "OSCP · Exam Mode · Nmap"
description: "Quatre scans Nmap en laboratoire autorisé : découverte, inventaire TCP, analyse des services et UDP indépendant."
prev: false
next: false
---

# Nmap · Exam Mode

[← Exam Mode](./exam.md) · [Référence Nmap complète](./reconnaissance.md#nmap)

<LabVariables />

## 1. Découverte des hôtes

Identifier les machines actives du réseau autorisé.

<LabCommand source='sudo nmap -sn -n "$SUBNET"' />

## 2. Scan TCP rapide

Examiner les 65 535 ports TCP.

<LabCommand source='sudo nmap -sS -p- --min-rate 1000 -T4 -n -Pn "$IP" -oN tcp.txt' />

## 3. Analyse approfondie TCP

Renseigner les ports TCP ouverts dans le configurateur. Analyser uniquement ces ports.

<LabCommand source='sudo nmap -A -p "$TCP_PORTS" -n -Pn "$IP" -oN services.txt' />

## 4. Scan UDP indépendant

Lancer dans un deuxième terminal, sans attendre la fin de l’analyse TCP. Examiner les 65 535 ports UDP.

<LabCommand source='sudo nmap -sU -p- -n -Pn "$IP" -oN udp.txt' />

::: details Points de vigilance
- La découverte ne garantit pas que tous les hôtes répondent. Utiliser `-Pn` uniquement sur les machines connues et autorisées.
- `--min-rate 1000` est un débit minimal demandé, pas une limite maximale. Réduire le débit et confirmer les résultats si des pertes sont suspectées.
- Un scan UDP intégral peut durer plusieurs heures. Aucun débit minimal forcé pour UDP.
- Les ports UDP `open|filtered` nécessitent une vérification ciblée ; le scan UDP d’inventaire ne garantit pas l’identification de leurs versions.
- Vérifier les règles de l’épreuve et le comportement des scripts NSE. Aucun scan ne garantit de détecter tous les services.
:::

[Services par port](./reconnaissance.md#services-par-port) · [Documentation Nmap TCP/UDP](https://nmap.org/book/man-port-specification.html)

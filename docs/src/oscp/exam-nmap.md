---
title: "OSCP · Exam Mode · Nmap"
description: "Trois scans Nmap en laboratoire autorisé : découverte, inventaire TCP et UDP, identification des services."
prev: false
next: false
---

# Nmap · Exam Mode

[← Exam Mode](./exam.md) · [Référence Nmap complète](./reconnaissance.md#nmap)

`$SUBNET` : réseau autorisé en CIDR · `$IP` : machine du laboratoire · `$TCP_PORTS` et `$UDP_PORTS` : listes de ports séparés par des virgules.

## 1. Découverte des hôtes

Identifier les machines qui répondent sur le réseau de laboratoire.

```bash
sudo nmap -sn -n "$SUBNET"
```

## 2. Scan complet TCP et UDP

Examiner les ports 1 à 65 535 de chaque protocole. Conserver les résultats bruts.

```bash
sudo nmap -sS -sU -p- -T4 -n -Pn "$IP" -oN rapport_ports.txt
```

## 3. Analyse des services

Renseigner les ports TCP ouverts et les ports UDP ouverts ou `open|filtered` identifiés précédemment. Analyser uniquement ces ports.

```bash
sudo nmap -sS -sU -A -p "T:$TCP_PORTS,U:$UDP_PORTS" -n -Pn "$IP" -oN rapport_services.txt
```

Si un protocole ne présente aucun port à vérifier, retirer son indicateur de scan (`-sS` ou `-sU`) et sa partie dans `-p`.

::: details Points de vigilance
- Un hôte peut ne pas répondre à la découverte. Utiliser `-Pn` uniquement sur les machines connues et autorisées.
- Un scan UDP intégral peut durer plusieurs heures. Aucun débit minimal forcé : les pertes et la limitation des réponses ICMP peuvent rendre le résultat incertain.
- Les états `open|filtered` ne prouvent pas qu’un port est ouvert. La détection des versions peut aider à les distinguer.
- Si des résultats sont incohérents, confirmer à un débit adapté. Aucun scan ne garantit la découverte de tous les services.
- Contrôler les règles de l’épreuve et le comportement des scripts NSE avant leur utilisation.
:::

[Services par port](./reconnaissance.md#services-par-port) · [Documentation Nmap TCP/UDP](https://nmap.org/book/man-port-specification.html)

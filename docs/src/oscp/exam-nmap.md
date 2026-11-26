---
title: "OSCP · Exam Mode · Nmap"
description: "Trois scans Nmap dans un laboratoire autorisé : découverte, inventaire TCP et identification des services."
prev: false
next: false
---

# Nmap · Exam Mode

[← Exam Mode](./exam.md) · [Référence Nmap complète](./reconnaissance.md#nmap)

`$SUBNET` : réseau autorisé en CIDR · `$IP` : machine du laboratoire · `$PORTS` : ports TCP ouverts, séparés par des virgules.

## 1. Découverte des hôtes

Identifier les machines qui répondent sur le réseau de laboratoire.

```bash
sudo nmap -sn -n "$SUBNET"
```

## 2. Scan TCP complet

Examiner les 65 535 ports TCP de la machine autorisée et enregistrer les résultats.

```bash
sudo nmap -sS -p- -T4 --min-rate 1000 -n -Pn "$IP" -oN rapport_ports.txt
```

## 3. Analyse des ports ouverts

Renseigner `$PORTS` avec les ports ouverts trouvés à l’étape précédente. Détecter les versions, l’OS, les scripts NSE par défaut et le chemin réseau, sur ces ports uniquement.

```bash
sudo nmap -A -p "$PORTS" -n -Pn "$IP" -oN rapport_services.txt
```

::: details Points de vigilance
- Un hôte peut ne pas répondre à la découverte. `-Pn` s’utilise sur les machines connues et autorisées.
- Un débit trop élevé peut faire manquer des ports : réduire le débit et confirmer si nécessaire.
- Le scan TCP ne couvre pas UDP. Vérifier UDP si le contexte l’exige.
- Contrôler les règles de l’épreuve et le comportement des scripts NSE avant leur utilisation.
:::

[Services par port](./reconnaissance.md#services-par-port)

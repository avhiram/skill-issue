---
title: Bug Bounty
description: Parcours Bug Bounty, du programme à la prime.
aside: true
prev: false
next: false
---

# Bug Bounty

Un parcours chronologique et une cheatsheet en français. Chaque étape contient ses méthodes, commandes et explications. Commencer par le programme et suivre les chapitres dans l'ordre.

## Parcours

### [Programme et préparation](./preparation.md)

Choisir un programme, définir le scope et préparer son espace de travail.

### [Reconnaissance passive](./reconnaissance.md)

Recenser les domaines et les actifs connus à partir des sources publiques.

### [Cartographie et scan réseau](./scan-reseau.md)

Valider le périmètre, les services et les technologies.

### [Cartographie Web et API](./cartographie-web.md)

Collecter les URL, paramètres, fichiers JavaScript et routes API.

### [Tests de vulnérabilités](./vulnerabilites.md)

Retrouver les techniques par famille de vulnérabilités.

### [Validation et preuves](./validation.md)

Confirmer les observations et préparer les preuves.

### [Rapport et signalement](./rapport.md)

Rédiger et transmettre un rapport reproductible.

### [Suivi et prime](./suivi.md)

Suivre le triage, le retest et la récompense.

## Accès rapide

- [JavaScript et endpoints](./cartographie-web.md#analyse-javascript)
- [Exposition de données](./vulnerabilites.md#exposition-de-donnees)
- [XSS](./vulnerabilites.md#cross-site-scripting-xss)
- [SQL Injection](./vulnerabilites.md#sql-injection-sqli)
- [SSRF](./vulnerabilites.md#server-side-request-forgery-ssrf)
- [LFI](./vulnerabilites.md#local-file-inclusion-lfi)
- [CORS](./vulnerabilites.md#cross-origin-resource-sharing-cors)
- [Microsoft IIS](./vulnerabilites.md#microsoft-iis-et-asp-net)

## Espaces complémentaires

- [IA & Bug Bounty](./ia.md)
- [Security Tools](./ressources.md#security-tools)
- [Browser Extensions](./ressources.md#browser-extensions)

Les exemples historiques et leurs options ne sont pas tous vérifiés. Les fichiers de sortie des différentes variantes peuvent différer : vérifier les prérequis et sélectionner les commandes adaptées au périmètre autorisé. Les articles transmis alimentent les fiches ; l'intégration de leurs commandes reste partielle.

Les ressources sont séparées du parcours pour éviter de confondre un catalogue d'outils avec une étape de travail.

### Références pédagogiques

- Full Bug Bounty Reconnaissance Methodology, Alham Rizvi : reconnaissance, validation DNS, collecte Web et inventaire des API.
- Bug Bounty Hunting Methodology 2025, AmrSec : méthodologie et rapports ; document portant la mention All Rights Reserved. Synthèse originale, pas de republication intégrale.
- Bug Bounty Methodologies : notes de reconnaissance et de tests Web.
- Bug Bounty Hunting Process, HTB Academy : présentation du module et importance du respect du processus de signalement.

### Méthodologies complémentaires

Quatre fiches restent identifiables par leur titre seulement. La fin de la fiche Advanced Recon est également tronquée dans le texte fourni.

- Gather assets through API
- SSTI Payloads
- CRLF Injection
- SQL Injection XOR WAF Bypass

---
title: "OSCP · Rapports de pentest"
description: "Documenter les constats et les preuves techniques."
---

# OSCP · Rapports de pentest

Documenter les constats et les preuves techniques.


## Prise de notes et rapports

Structurer les notes, les constats et les preuves techniques.


## Captures d'écran

Conserver des captures lisibles pour appuyer les constats.


### Windows

Capturer les écrans utiles depuis Windows.


### Kali Linux

Réaliser les captures depuis Kali Linux.


**Paramètres et repères :**
`gnome-screenshot`  


### Bonnes pratiques pour les captures d’écran

Conserver le contexte nécessaire à la compréhension de chaque preuve.


**Paramètres et repères :**
`sql_injection_vuln_example.png`  


## Éléments essentiels d’un rapport

Présenter le périmètre, les constats, les preuves et les recommandations.


## Mise en forme du rapport

Organiser le rapport pour faciliter la lecture des résultats.


## Rapport de conformité (facultatif)

Relier les constats aux exigences applicables lorsque cela est demandé.



## Conserver des preuves vérifiables

Une preuve doit préserver son contexte : système, compte de test, date, cible et commande exécutée. Le rapport distingue observation, impact et recommandations.

### Empreinte SHA-256 sous Linux

Calculer l'empreinte d'un fichier de preuve pour contrôler son intégrité sans divulguer son contenu.

<p class="oscp-command-note">Calculer l’empreinte d’un fichier sous Linux.</p>

```bash
sha256sum <FICHIER_PREUVE>
```

### Empreinte SHA-256 sous Windows

Associer une empreinte à chaque capture conservée dans le dossier du rapport.

<p class="oscp-command-note">Calculer l’empreinte d’une capture avec PowerShell.</p>

```powershell
Get-FileHash -Algorithm SHA256 -Path '<CAPTURE>.png'
```

Pour structurer les constats, consulter le [guide de rapports OffSec avec SysReptor](https://docs.sysreptor.com/offsec-reporting-with-sysreptor/). Éviter d'exécuter un script d'installation distant sans en examiner le contenu.

**Référence complémentaire :** [krovs/oscp-notes](https://github.com/krovs/oscp-notes/blob/main/README.md).

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->

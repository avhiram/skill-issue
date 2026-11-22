---
title: "OSCP · Rapport d’audit"
description: "Préparer les captures, vérifier leur intégrité et rédiger un constat."
---

# Rapport d’audit

## Garder le contexte d’une preuve

Pour chaque constat, note la machine, le compte utilisé, la commande exacte et sa sortie. Conserve une capture lisible qui montre le résultat et permet d’identifier le système concerné.

| Élément | À consigner |
| --- | --- |
| Périmètre | Machine et service concernés. |
| Observation | Action réalisée, résultat obtenu et nom de la capture. |
| Impact | Conséquence effectivement observée pendant le test. |
| Correction | Mesure proposée et résultat attendu après correction. |

Pour l’examen, vérifie les consignes de capture et de remise du rapport dans le [guide officiel OffSec](https://help.offsec.com/hc/en-us/articles/360040165632-OSCP-Exam-Guide).

## Capturer une fenêtre

### Sous Windows

Appuie sur **Windows + Maj + S**, sélectionne la zone utile et enregistre l’image sous `capture.png`.

### Sous Kali avec GNOME Screenshot

Si `gnome-screenshot` est installé, sélectionne la zone à enregistrer dans le dossier courant.

```bash
gnome-screenshot -a -f ./capture.png
```

## Contrôler l’intégrité d’une capture

Exécute la commande depuis le dossier contenant `capture.png`. Conserve l’empreinte avec les notes pour la comparer à celle d’une copie ultérieure.

### SHA-256 sous Linux

```bash
sha256sum -- ./capture.png
```

### SHA-256 sous Windows avec PowerShell

```powershell
Get-FileHash -LiteralPath '.\capture.png' -Algorithm SHA256
```

## Rédiger le rapport

Relie chaque constat à sa preuve et à une correction. Si le mandat prévoit une analyse de conformité, cite l’exigence concernée et la pièce qui permet de la vérifier.

[Consignes de rapport OffSec](https://help.offsec.com/hc/en-us/articles/360046787731-OSCP-Reporting-Requirements) · [Modèle OffSec pour SysReptor](https://docs.sysreptor.com/offsec-reporting-with-sysreptor/) · [GNU Coreutils](https://www.gnu.org/software/coreutils/manual/coreutils.html) · [Get-FileHash](https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/get-filehash).

Sources d’origine : [notes de krovs](https://github.com/krovs/oscp-notes/blob/main/README.md) et [guide d’Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- notes-krovs-2026 -->
<!-- refined-oscp -->

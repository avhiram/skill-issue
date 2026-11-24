---
title: Validation et preuves
aside: true
prev: false
next: false
---

# Validation et preuves

[Retour au parcours](./index.md)

Objectif : confirmer manuellement les observations, documenter le résultat et démontrer uniquement l'impact nécessaire.

## Analyse et validation

- Examiner les comportements communs, puis les différences entre applications et fonctionnalités.
- Contrôler manuellement les résultats automatisés ; une réponse HTTP 200 ou une chaîne réfléchie ne suffit pas à démontrer une vulnérabilité.
- Utiliser des comptes de test et des données fictives ; ne pas réutiliser de secrets découverts.
- Démontrer uniquement l'impact nécessaire, sans accéder à des données réelles non nécessaires.

## Proof of Concept (PoC)

- Documenter le contexte, les prérequis et les étapes reproductibles.
- Joindre les requêtes et réponses pertinentes, captures ou vidéo de démonstration.
- Masquer les secrets et données personnelles.

## Empreinte des fichiers de preuve

```bash
(
  set -o pipefail
  find preuves -type f -print0 | sort -z | xargs -0 -r sha256sum > preuves.sha256
) && test -s preuves.sha256 && sha256sum -c preuves.sha256
```

Calcule puis vérifie les empreintes SHA-256 des preuves, y compris dans les sous-dossiers (Bash et GNU/Linux). Le contrôle échoue si le manifeste est vide. Exécuter depuis la racine du programme, après avoir enregistré les preuves expurgées dans `preuves/`.

## Avant de poursuivre

<BountyChecklist storage-key="checkpoint-validation" :items='["Impact démontré et étapes de reproduction documentées.","Preuves expurgées et enregistrées."]' />

---

[Précédent : Tests de vulnérabilités](./vulnerabilites.md) · [Parcours](./index.md) · [Suivant : Rapport et signalement](./rapport.md)

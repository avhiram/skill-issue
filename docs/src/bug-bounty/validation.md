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
sha256sum preuves/* > preuves.sha256
```

Calcule les empreintes des fichiers de preuve locaux pour documenter leur intégrité. Ne conserver que des preuves expurgées ; ajout de documentation locale.

---

[Précédent : Tests de vulnérabilités](./vulnerabilites.md) · [Parcours](./index.md) · [Suivant : Rapport et signalement](./rapport.md)

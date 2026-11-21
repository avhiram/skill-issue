# CRTO — Examen et préparation opérationnelle

> **Source :** [notes d'examen du dépôt CRTO-Study-Notes](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/notes/Exam-Instructions.md). Ces indications sont issues de notes communautaires : **vérifie toujours les règles et délais dans ton espace de formation officiel**, qui fait foi.

## Déroulement de l'épreuve

Le scénario décrit dans les notes est de type **assume-breach** : un point d'appui dans le réseau interne est fourni. Les objectifs, les restrictions et les systèmes hors périmètre figurent dans le panneau d'instructions de l'épreuve.

- Ouvrir le module **Red Team Operator Exam** dans la plateforme de formation.
- Garder la page de l'examen ouverte pendant la session ; consulter le cours dans un autre onglet.
- Relever le **Lab ID** indiqué dans les instructions, notamment pour toute demande au support.
- Lire intégralement les **Rules of Engagement (RoE)** avant toute interaction avec l'environnement.

## Barème indiqué par les notes

| Critère | Points |
| --- | ---: |
| Objectif opérationnel | 50 |
| Discipline OPSEC | 50 |
| Seuil de réussite annoncé | **85 / 100** |

La réussite de l'objectif technique ne suffit donc pas, selon cette source, si le score OPSEC est insuffisant.

## Périmètre et sécurité

> **Hôtes hors périmètre :** les notes signalent qu'une alerte générée sur un hôte interdit peut entraîner l'échec de l'épreuve.

Avant toute action, documenter les systèmes autorisés et les exclusions. Ne pas supposer qu'un hôte visible sur le réseau fait partie du périmètre.

Les notes soulignent également l'importance de ne pas désactiver les protections Windows Defender ou le pare-feu pendant l'épreuve.

## Durées rapportées par les notes

| Élément | Durée |
| --- | --- |
| Temps de laboratoire cumulé | 24 heures |
| Fenêtre calendaire | 7 jours |
| Délai entre tentatives | 7 jours |
| Temps d'activité avant disponibilité de la sauvegarde | 15 à 20 minutes |

**Attention :** ces valeurs ne sont pas vérifiées auprès de l'organisme certificateur pour la session actuelle.

## Sauvegarder sans terminer l'épreuve

| Action | Effet décrit |
| --- | --- |
| **Exit Lab → Save Progress And Exit** | Enregistre l'état de l'environnement et suspend la session |
| **Exit Lab → End Lab** | Termine définitivement la tentative |

Ne pas confondre ces deux actions. La sauvegarde de l'environnement ne garantit pas le maintien de toutes les sessions réseau actives.

## Soumettre les résultats

Selon les notes :

1. Utiliser **Submit** lorsque le travail est terminé.
2. Ne pas quitter la page pendant l'évaluation.
3. Utiliser **Update & Close** après le calcul du score afin d'enregistrer le résultat dans la plateforme.

## Checklist de préparation

- [ ] Lire les consignes officielles de la session.
- [ ] Identifier les hôtes autorisés et exclus.
- [ ] Noter le Lab ID.
- [ ] Préparer un journal horodaté des actions et observations.
- [ ] Vérifier les paramètres et la connectivité de l'environnement de laboratoire.
- [ ] Contrôler le temps restant avant toute interruption.
- [ ] Distinguer clairement sauvegarde, fin de session et soumission définitive.
- [ ] Conserver les preuves demandées par les consignes officielles.

## Références

- [Exam Instructions — CRTO-Study-Notes](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/notes/Exam-Instructions.md)
- [Bibliothèque de commandes — dépôt source](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/crto-command-library.md)

La bibliothèque de commandes sera organisée dans des fiches distinctes afin de conserver une navigation lisible.

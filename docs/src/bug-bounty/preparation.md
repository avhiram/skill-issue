---
title: Programme et préparation
aside: true
prev: false
next: false
---

# Programme et préparation

[Retour au parcours](./index.md)

Objectif : choisir un programme, comprendre les règles et préparer son environnement avant toute requête.

## Préparation

- Lire le scope, les exclusions, les limites de débit et les règles de divulgation du programme.
- Distinguer les domaines autorisés des noms simplement découverts. Un certificat, un ASN ou une archive ne prouve pas qu'un service est dans le scope.
- Préparer un dossier de travail et conserver les résultats intermédiaires.

## Choisir un programme

- Identifier un programme ouvert aux signalements et vérifier s'il prévoit une prime.
- Lire les actifs inclus et exclus, les catégories éligibles, les restrictions sur l'automatisation et les consignes de signalement.
- Conserver une copie datée du scope et des règles. Un VDP n'est pas nécessairement rémunéré.
- Séparer chaque programme dans un dossier de travail et utiliser des comptes de test dédiés.

## Dossier de travail

```bash
mkdir -p bug-bounty/{scope,recon,requests,preuves,rapports}
cd bug-bounty
```

Prépare les dossiers locaux pour conserver le périmètre, les inventaires, les requêtes, les preuves et les rapports. Adaptation pratique du classement proposé dans l'article Claude Code.

## Préparer les outils

Consulter [Security Tools et Browser Extensions](./ressources.md). Vérifier les versions installées, les dépendances et les permissions des extensions avant utilisation.

## Vérifier la disponibilité des outils

```bash
command -v subfinder httpx katana gau nmap nuclei ffuf
```

Vérifie quels exécutables sont présents dans le PATH. Attention : httpx désigne ici l'outil ProjectDiscovery, pas le client Python. Ajout de préparation local.

---

[Parcours](./index.md) · [Suivant : Reconnaissance passive](./reconnaissance.md)

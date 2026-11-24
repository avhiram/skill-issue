---
title: Programme et préparation
aside: true
prev: false
next: false
---

# Programme et préparation

[Retour au parcours](./index.md)

Objectif : choisir un programme, comprendre les règles et préparer son environnement avant toute requête.

## Choisir un programme

- Identifier un programme ouvert aux signalements et vérifier s'il prévoit une prime.
- Lire les actifs inclus et exclus, les catégories éligibles, les restrictions sur l'automatisation et les consignes de signalement.
- Conserver une copie datée du scope et des règles. Un VDP n'est pas nécessairement rémunéré.
- Séparer chaque programme dans un dossier de travail et utiliser des comptes de test dédiés.

## Dossier de travail

```bash
mkdir -p bug-bounty/{scope,recon,requests,preuves,rapports,javascript}
cd bug-bounty
```

Crée les dossiers du programme pour classer le scope, les résultats, les requêtes, les preuves et les rapports. Conserver le même répertoire de travail entre les chapitres : les exemples utilisent des chemins relatifs. Les fichiers de scope, requêtes et wordlists doivent être préparés séparément. Enregistrer les domaines autorisés dans `scope/domains.txt`, à raison d'un nom par ligne. Les inventaires TXT des exemples sont stockés à la racine du dossier du programme ; `javascript/` accueille les scripts obtenus dans le cadre autorisé.

## Préparer les outils

Consulter [Security Tools et Browser Extensions](./ressources.md). Vérifier les versions installées, les dépendances et les permissions des extensions avant utilisation.

## Vérifier la disponibilité des outils

```bash
command -v subfinder httpx katana gau nmap nuclei ffuf
```

Vérifie quels exécutables sont présents dans le PATH. Attention : httpx désigne ici l'outil ProjectDiscovery, pas le client Python.

## Avant de poursuivre

- Scope et exclusions enregistrés.
- Règles du programme vérifiées.
- Dossier de travail et comptes de test prêts.

---

[Parcours](./index.md) · [Suivant : Reconnaissance passive](./reconnaissance.md)

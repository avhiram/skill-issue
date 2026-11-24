---
title: IA et Bug Bounty
aside: true
prev: false
next: false
---

# IA et Bug Bounty

[Retour au parcours](./index.md)

Analyse, organisation et rédaction avec l'IA. Exemples adaptés de The Best Claude Code Setup for Bug Bounty Hunting. Validation humaine des actions réseau.

## Configuration Claude Code et Burp Suite MCP

- Installer l'extension MCP officielle dans Burp Suite : [PortSwigger MCP Server](https://github.com/PortSwigger/mcp-server).
- Vérifier que le serveur SSE écoute localement et que le port correspond à la configuration de l'extension.
- Définir le scope dans Burp Suite avant de connecter le client. Ne pas activer l'approbation automatique globale.

### Ajouter le serveur MCP Burp

```bash
claude mcp add burp --transport sse http://127.0.0.1:9876
```

Enregistre le serveur MCP SSE local dans Claude Code. Commande de l'article ; nécessite Claude Code installé et un serveur MCP Burp déjà démarré sur ce port. Syntaxe et connexion non testées.

### Organisation des fichiers du projet

```text
project/
  recon/
    subdomains.txt
    alive.txt
    urls.txt
  requests/
    login.txt
    profile.txt
    api.txt
  javascript/
    app.js
    dashboard.js
    auth.js
  source/
  notes/
```

Structure de travail adaptée des deux arborescences de l'article. Stocker uniquement des copies autorisées et expurgées.

## Prompts d'analyse

### Historique HTTP Burp

```text
Analyse les requêtes HTTP exportées de Burp et fournies pour le périmètre autorisé.
Liste les méthodes, URL, statuts et paramètres.
Résume les fonctionnalités et distingue login, recherche, panier, paiement et API.
Signale les catégories de données sensibles sans reproduire les valeurs.
N'envoie aucune requête et ne modifie aucun fichier.
```

Transforme l'historique HTTP fourni en inventaire structuré. Adaptation du prompt Proxy History.

### Cartographie applicative

```text
À partir des captures autorisées, classe les routes par fonctionnalité.
Identifie les paramètres, les identifiants d'objets, les formulaires, les interfaces d'administration et les API.
Indique les contrôles de sécurité attendus et les informations manquantes.
Ne teste pas les routes et n'accède pas à d'autres comptes.
```

Adaptation du prompt Attack Surface pour examiner les observations et définir les contrôles à vérifier manuellement.

### Analyse JavaScript

```text
Analyse les fichiers JavaScript locaux fournis.
Inventorie les routes API, méthodes, paramètres, logique de session, fonctions d'autorisation, uploads, téléchargements et intégrations tierces.
Repère les sources et sinks DOM, flags de fonctionnalités et références à des secrets sans afficher leur valeur.
Déduplique les routes et cite les fichiers et lignes.
Distingue observations, hypothèses et constats démontrés.
```

Regroupe les trois prompts JavaScript de l'article : fichier individuel, revue du code fourni et analyse d'un dossier.

### Revue IDOR et BOLA

```text
Analyse la requête de laboratoire fournie et les réponses de mes deux comptes de test.
Identifie le paramètre d'objet et la frontière d'autorisation attendue.
Explique si les preuves démontrent une violation de cette frontière.
Propose des contrôles manuels avec des objets de test uniquement.
Ne conclus pas à une vulnérabilité sans preuve et n'effectue aucune requête.
```

Adaptation du prompt IDOR/BOLA pour des preuves obtenues avec des comptes et objets de test autorisés.

### Revue du code source

```text
Examine le code source local autorisé.
Évalue authentification, autorisation, validation des entrées, injections, gestion des fichiers, sessions et logique métier.
Pour chaque constat étayé, indique la cause, la ligne concernée, l'impact, la correction et une vérification manuelle en laboratoire.
Ne présente pas une hypothèse comme un fait.
```

Adaptation du prompt Source Code Review.

### Corrélation des résultats

```text
Corrèle les fichiers locaux de reconnaissance, captures HTTP, JavaScript et code source.
Construis un inventaire des routes, paramètres, contrôles d'accès et fonctionnalités.
Déduplique les observations et classe les vérifications manuelles selon les preuves disponibles.
Sépare les constats confirmés et les hypothèses.
Produis un rapport sans lancer de test actif.
```

Adaptation du prompt de corrélation multi-sources.

### Rapport de vulnérabilité

```text
À partir des constats validés et des preuves expurgées, rédige un rapport.
Inclure le titre, le composant, la sévérité justifiée, les étapes de reproduction documentées, les preuves, l'impact et la remédiation.
Séparer les observations des vulnérabilités confirmées.
Ne rien inventer.
```

Adaptation du prompt de reporting de l'article.

## Skills Claude Code

### Créer une skill de revue

```text
À partir de ma méthodologie de revue autorisée, crée une skill Claude Code de lecture seule.
Définis le nom, la description, SKILL.md, les fichiers d'entrée, les étapes d'inventaire et d'analyse, les critères de validation et le format du rapport.
Précise que les hypothèses doivent être séparées des preuves et qu'aucune action réseau ou modification ne doit être lancée automatiquement.
Ne propose pas de technique absente de mes notes.
```

Adaptation des trois prompts de création de skills pour organiser l'analyse, la revue des résultats XSS et Open Redirect et le reporting.

## Provenance

[The Best Claude Code Setup for Bug Bounty Hunting](https://lostsec.medium.com/the-best-claude-code-setup-for-bug-bounty-hunting-a16a0a50e811), 27 août 2026. Les prompts sont reformulés pour l'analyse de données fournies et la validation manuelle ; les workflows de test autonome, les chaînes d'exploitation et les instructions de contournement ne sont pas reproduits. Les exemples HTTP contenant des identifiants de démonstration ne sont pas republiés.

[Retour au parcours](./index.md)

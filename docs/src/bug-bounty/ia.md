---
title: IA et Bug Bounty
aside: true
prev: false
next: false
---

# IA et Bug Bounty

[Retour au parcours](./index.md)

Claude Code permet de centraliser la reconnaissance, l'analyse HTTP, la revue JavaScript, la validation des vulnérabilités et la rédaction de rapports. MCP et les Skills permettent de réutiliser cette méthodologie dans un environnement de test autorisé.

## Claude Code

Claude Code est un assistant accessible depuis le terminal. Il peut travailler avec les fichiers d'un projet, les commandes et les outils connectés.

```text
target/
├── javascript/
├── requests/
├── urls.txt
├── endpoints.txt
└── notes/
```

Organiser les artefacts dans un dossier dédié permet à Claude de les analyser sans copier chaque fichier dans une interface de conversation.

## Model Context Protocol (MCP)

MCP permet de connecter un assistant IA à des outils externes. Le serveur MCP de Burp Suite expose notamment des fonctionnalités liées à l'historique HTTP et à l'analyse du trafic.

## Configuration de Burp Suite MCP

### Installation

1. Ouvrir Burp Suite et accéder au BApp Store.
2. Rechercher MCP et vérifier l'auteur ainsi que les fonctionnalités de l'extension.
3. Installer l'extension officielle : [PortSwigger MCP Server](https://github.com/PortSwigger/mcp-server).
4. Dans l'onglet MCP, vérifier la configuration du serveur et les autorisations HTTP. Limiter les autorisations aux hôtes du laboratoire et conserver une validation des actions actives.
5. Pour Claude Desktop, utiliser l'installation proposée par l'extension. Pour une installation manuelle, récupérer le JAR compilé ou suivre les instructions de compilation du dépôt.
6. Si nécessaire, charger le JAR dans Extensions et vérifier l'adresse locale et le port.

### Connexion à Claude Code

```bash
claude mcp add --transport sse burp http://127.0.0.1:9876
```

Ajoute le serveur MCP Burp à Claude Code. Adapter le port à la configuration réelle. Consulter les outils exposés dans la section MCP de Claude. Le transport SSE est celui utilisé dans cet exemple.

Documentation : [Claude Code MCP](https://code.claude.com/docs/en/mcp).

## Collecte du trafic et reconnaissance

1. Ajouter l'application autorisée au scope dans Target.
2. Dans Proxy > HTTP history, activer Show only in-scope items.
3. Parcourir les fonctionnalités : formulaires, recherche, connexion, déconnexion, panier et API.
4. Si les règles du laboratoire le permettent, utiliser Engagement Tools > Discover Content pour compléter l'inventaire.
5. Arrêter la découverte, puis utiliser Show only parameterized requests pour isoler les requêtes paramétrées.

## Workflow Bug Bounty

### Phase 1 — Analyse de l'historique HTTP

```text
Analyse l'historique HTTP de Burp pour le périmètre autorisé du laboratoire.

1. Liste les requêtes avec méthode, URL et statut HTTP.
2. Résume l'application et ses fonctionnalités principales.
3. Regroupe les routes de connexion, recherche, panier, paiement et API.
4. Construis un tableau des endpoints API avec méthode, chemin et paramètres.
5. Repère les catégories de données sensibles : mots de passe, tokens, clés API, emails et données personnelles. Masque les valeurs.
6. Déduplique les résultats et résume les points à examiner.
```

Transforme les captures HTTP en inventaire exploitable.

### Phase 2 — Cartographie de la surface d'attaque

```text
Analyse les captures HTTP et les fichiers JavaScript disponibles pour le laboratoire.

1. Identifie les paramètres search et q.
2. Inventorie les identifiants numériques, références d'objets et commandes.
3. Classe les endpoints admin, profile, user, account, upload et API.
4. Examine les fichiers JavaScript fournis : routes API, logique applicative et références à des secrets.
5. Sélectionne six points prioritaires à examiner manuellement, par catégorie : SQLi, XSS, IDOR et authentification.

Distingue les hypothèses des vulnérabilités démontrées.
```

Organise les surfaces applicatives et les contrôles de sécurité à examiner.

### Phase 3 — Tests de vulnérabilités

Les tests actifs sont réalisés dans le laboratoire avec des comptes et des données de démonstration. Examiner les résultats de chaque famille avant de poursuivre.

```text
À partir de la cartographie et des résultats des tests manuels du laboratoire, examine dans cet ordre :

1. SQL injection : comportement des entrées de recherche et traitement côté serveur.
2. XSS réfléchie : réflexion des entrées et encodage selon le contexte.
3. IDOR : isolation des objets appartenant aux deux comptes de test.
4. Identifiants faibles ou par défaut : résultats des vérifications autorisées sur les comptes de démonstration.
5. Énumération utilisateur : différences entre les réponses de connexion des comptes de test.
6. Rate limiting : résultats des contrôles de limitation et de verrouillage.
7. Broken Access Control : respect des permissions sur les interfaces administratives et API.
8. Logique métier : application des règles de remise et du panier.

Pour chaque catégorie, résume le résultat, les preuves, l'endpoint, la sévérité justifiée et les limites de validation.
Ne confirme aucune vulnérabilité sans preuve.
```

Claude Code permet également de consulter le détail de ses opérations avec Ctrl+O selon la version utilisée.

### Phase 4 — Rapport final

```text
Rédige un rapport de pentest à partir des résultats validés du laboratoire.

Pour chaque vulnérabilité :
- Titre.
- Sévérité : Critical, High, Medium ou Low.
- Endpoint affecté.
- Étapes de reproduction déjà validées.
- Preuve : requête et réponse HTTP.
- Impact.
- Remédiation.

Termine par une liste de corrections classées par priorité.
Identifie les requêtes à conserver dans Burp Organizer.
```

Centralise les preuves et distingue les constats confirmés des observations.

## Prompt global — One-Shot

Ce prompt rassemble les six phases d'une évaluation assistée par IA, à partir des artefacts du laboratoire et des tests validés par l'opérateur.

```text
RÔLE
Tu assistes un analyste dans l'évaluation autorisée d'une application e-commerce de laboratoire.

PÉRIMÈTRE
- Utilise uniquement les captures, fichiers et résultats fournis pour le laboratoire.
- Appuie-toi sur les artefacts Burp : historique, Repeater, Organizer et résultats Collaborator disponibles.
- Distingue les observations des hypothèses et des constats confirmés.
- Ne lance pas de test actif sans validation de l'opérateur.

PHASE 1 — INVENTAIRE ET MODÉLISATION
1. Inventorie les hôtes, pages, endpoints, méthodes et paramètres.
2. Examine les en-têtes serveur, signatures de frameworks, cookies, JWT, bibliothèques JS et indices CDN/WAF.
3. Analyse les bundles JavaScript fournis : routes API, secrets masqués et logique applicative.
4. Cartographie connexion, cycle de vie des tokens, réinitialisation de mot de passe, inscription, rôles et sessions.
5. Classe les paramètres id, search, q et les routes admin, user, profile, upload.
6. Produis une cartographie des surfaces et des classes de vulnérabilité pertinentes.

PHASE 2 — HYPOTHÈSES ET PRIORISATION
- Classe les hypothèses selon impact, vraisemblance et effort.
- Examine en priorité la logique métier et les contrôles d'accès.
- Formule cinq à huit hypothèses vérifiables.
- Définis la preuve nécessaire pour confirmer ou infirmer chacune.

PHASE 3 — REVUE DES TESTS
Examine les résultats de tests manuels pour les catégories suivantes :
1. Logique métier : prix, quantités, devises, remises, transitions du paiement.
2. IDOR/BOLA : isolation des objets et autorisations des comptes de test.
3. Authentification et sessions : credentials faibles, énumération, limitation, fixation, invalidation, tokens.
4. Contrôles d'accès : séparation des rôles et permissions des API.
5. Injections : SQLi, XSS réfléchie, stockée et DOM, SSTI et injection de commandes.
6. Out-of-band : interprétation des preuves SSRF, XXE et interactions DNS/HTTP de laboratoire.
7. Uploads et divulgation : validation des fichiers, types MIME, origine, source maps, debug, sauvegardes et erreurs.

PHASE 4 — CORRÉLATION ET IMPACT
- Identifie les relations entre les constats déjà démontrés.
- Évalue les conséquences sur les comptes, sessions, données, permissions et opérations métier.
- Décris les dépendances entre constats et les contrôles qui limitent leur impact.
- Repère les composants susceptibles de partager la même cause racine.
- Ne présente pas une chaîne hypothétique comme une chaîne validée.

PHASE 5 — VALIDATION
- Examine les reproductions minimales réalisées dans Repeater.
- Vérifie que les preuves démontrent un impact réel.
- Écarte les constats non reproductibles ou insuffisamment étayés.
- Référence les preuves conservées dans Organizer.

PHASE 6 — RAPPORT
1. Résumé exécutif.
2. Constats confirmés : titre, sévérité, vecteur et score CVSS 3.1 si justifiés, endpoint, catégorie, reproduction, preuve, impact, remédiation.
3. Relations entre constats démontrés.
4. Tableau de synthèse par sévérité.
5. Annexe des références Organizer.

En l'absence de vulnérabilité confirmée, indique-le et propose trois priorités de durcissement étayées.
```

## Analyse sans Burp MCP

Claude Code peut également travailler directement sur des requêtes HTTP, des fichiers JavaScript et du code source.

### Analyser une requête HTTP brute

Exporter une requête Burp dans un fichier texte. Exemple fictif d'inscription :

```http
POST /api/v1/auth/signup HTTP/2
Host: demo.local
Cookie: session=eyJhbGciOiJIUzI1NiJ9.demo.session
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/139.0.0.0 Safari/537.36
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.9
Content-Type: application/json
Origin: https://demo.local
Referer: https://demo.local/register
X-CSRF-Token: demo-csrf-token
X-Forwarded-For: 127.0.0.1
Connection: keep-alive

{
  "username": "john.doe",
  "email": "john@example.com",
  "password": "Password123!",
  "confirmPassword": "Password123!",
  "role": "user",
  "inviteCode": "",
  "referrer": "newsletter"
}
```

```text
Analyse cette requête HTTP.

Identifie :
1. Les entrées contrôlées par l'utilisateur.
2. Les mécanismes d'authentification et d'autorisation.
3. Les références d'objets et identifiants.
4. Les candidats IDOR/BOLA.
5. Les points d'injection potentiels.
6. Les paramètres de logique métier.
7. Les en-têtes et cookies pertinents.
8. Les comportements inhabituels à examiner.

Explique l'intérêt de chaque point, les contrôles manuels nécessaires et les preuves attendues.
Sépare observations et hypothèses. Ne conclus pas sans preuve.
```

### Analyser un fichier JavaScript

```text
Analyse le fichier JavaScript fourni.

Extrais et classe :
1. Endpoints API et chemins URL.
2. Méthodes HTTP.
3. Paramètres.
4. Logique d'authentification et d'autorisation.
5. Références à des secrets, tokens ou clés API, avec valeurs masquées.
6. Endpoints administratifs et internes.
7. Upload et téléchargement.
8. Debug et développement.
9. Fonctionnalités cachées et feature flags.
10. Sources et sinks DOM.
11. Intégrations tierces.

Pour chaque observation, indique le fichier, les lignes pertinentes et l'intérêt de la revue.
Ne confirme pas une vulnérabilité sans preuve.
```

### Analyser un JavaScript depuis une URL

```text
Analyse le fichier JavaScript accessible à cette URL autorisée :
<JS_URL>

Recherche les routes API, paramètres, contrôles d'authentification et d'autorisation, références à des secrets, fonctionnalités internes et administratives, endpoints de debug et problèmes côté client.

Pour chaque observation, explique son intérêt et référence le code concerné.
Limite la collecte au fichier autorisé et masque les valeurs sensibles.
```

### Analyser plusieurs fichiers JavaScript

```text
Analyse tous les fichiers JavaScript du dossier.

Construis une cartographie consolidée :
1. Endpoints API.
2. Méthodes HTTP.
3. Paramètres.
4. Authentification.
5. Autorisation.
6. Fonctions administratives.
7. Upload et download.
8. Endpoints WebSocket.
9. Intégrations tierces.
10. Références à des secrets et identifiants, valeurs masquées.
11. Sinks côté client.
12. Fonctionnalités cachées ou non documentées.

Déduplique les endpoints et regroupe les fonctionnalités.
Classe les dix observations prioritaires pour une revue manuelle.
Sépare les fonctionnalités observées des hypothèses de vulnérabilité.
```

### Examiner une vulnérabilité spécifique — IDOR/BOLA

```text
Analyse la requête et les réponses des deux comptes de test pour une éventuelle IDOR/BOLA.

1. Explique pourquoi la requête mérite une revue.
2. Identifie le paramètre de référence d'objet.
3. Décris la frontière d'autorisation attendue.
4. Indique les différences de réponse qui démontreraient une violation.
5. Précise les contrôles manuels à réaliser avec les objets de démonstration.

Distingue les observations des hypothèses et indique les preuves nécessaires.
```

### Revue du code source

```text
Effectue une revue de sécurité du code source fourni.

Examine :
1. Authentification.
2. Autorisation et contrôles d'accès.
3. Validation des entrées.
4. Risques d'injection.
5. Exposition de données sensibles.
6. Gestion des fichiers.
7. Gestion des sessions.
8. Logique métier.

Pour chaque constat étayé : cause racine, code concerné, impact, correction et méthode de validation en laboratoire.

Distingue les vulnérabilités confirmées, observations et hypothèses.
Classe les constats selon leur sévérité et leur impact pratique.
```

### Générer un rapport Bug Bounty

```text
À partir des requêtes HTTP, analyses JavaScript, résultats de reconnaissance et notes de test, rédige un rapport professionnel.

Pour chaque constat confirmé :
- Titre
- Sévérité
- Endpoint affecté
- Classe de vulnérabilité
- Étapes de reproduction validées
- Preuves
- Impact
- Remédiation

Sépare :
1. Vulnérabilités confirmées.
2. Observations de sécurité.
3. Hypothèses nécessitant une validation supplémentaire.

Classe les constats par sévérité et impact réel. Ne transforme pas une hypothèse en fait.
```

## Corrélation des résultats

### Structure du projet

```text
project/
├── recon/
│   ├── subdomains.txt
│   ├── alive.txt
│   └── urls.txt
├── requests/
│   ├── login.txt
│   ├── profile.txt
│   └── api.txt
├── javascript/
│   ├── app.js
│   ├── dashboard.js
│   └── auth.js
└── source/
    └── application-code/
```

### Prompt de corrélation

```text
Analyse les fichiers du projet d'évaluation autorisée et corrèle les résultats de reconnaissance, les captures HTTP, JavaScript et le code source.

Construis :
1. Une cartographie applicative.
2. Un inventaire des API.
3. Une cartographie de l'authentification et de l'autorisation.
4. Une liste des paramètres et identifiants d'objets.
5. Les fonctionnalités non documentées découvertes dans le code.
6. Les hypothèses de vulnérabilité.
7. Un plan de validation manuelle priorisé.
8. Les constats confirmés par les preuves fournies.
9. Un rapport professionnel.

Pour chaque constat, référence les preuves et indique la validation restante.
```

Cette approche constitue une alternative à MCP pour l'analyse d'artefacts déjà collectés.

## Skills Claude Code

Une Skill formalise une méthodologie réutilisable : description, ressources, étapes, critères de validation et format des résultats. Elle évite de répéter les mêmes instructions à chaque revue.

### Ressources communautaires

[Skills.sh](https://skills.sh/) propose un catalogue de Skills pour agents IA. Examiner le code, la licence, les permissions et les dépendances avant installation.

### Skills personnalisées

Une Skill peut être construite à partir de notes de recherche, d'une méthodologie de test, de fichiers de référence et de procédures de validation existantes. Le fichier principal SKILL.md définit son rôle et son workflow ; les ressources associées apportent le contexte nécessaire.

### Skill Open Redirect

```text
Crée une Skill Claude Code de revue Open Redirect à partir de ma méthodologie :

[COLLER LA MÉTHODOLOGIE OPEN REDIRECT]

Inclure :
- Nom et description.
- Méthodologie de détection.
- Organisation des paramètres et routes de redirection.
- Analyse des tests documentés et des mécanismes de validation.
- Outils de revue.
- Critères de confirmation et faux positifs.
- Format du rapport.

Reste fidèle à la méthodologie fournie. Réserve les tests actifs à une validation manuelle dans le laboratoire.
```

### Skill XSS

```text
Crée une Skill de revue XSS à partir des notes suivantes :

[COLLER LES NOTES XSS]

Organise :
- Reconnaissance et découverte des entrées.
- Analyse de la réflexion.
- Inventaire des paramètres et endpoints.
- Identification des contextes.
- Analyse des cas de test déjà documentés.
- Revue des filtres et de l'encodage.
- Critères de validation.
- Outils de revue.
- Faux positifs.
- Documentation et reporting.

Préserve la méthodologie et distingue analyse, hypothèses et résultats confirmés.
```

### Skill à partir d'une méthodologie complète

```text
Transforme ma méthodologie en Skill Claude Code réutilisable :

[COLLER LA MÉTHODOLOGIE]

Crée :
1. Nom.
2. Description.
3. SKILL.md.
4. Liste des outils.
5. Workflow d'analyse et de revue.
6. Cas de test documentés et critères attendus.
7. Scripts auxiliaires de traitement des artefacts si nécessaire.
8. Méthodologie de validation.
9. Format de rapport.
10. Fichiers de référence.

Outils installés :
[COLLER LES CHEMINS DES OUTILS]

Utilise les ressources existantes et ne déclenche pas d'installation ou d'action réseau sans validation.
```

Relire le SKILL.md et ses ressources avant de les intégrer au répertoire de Skills.

[Retour au parcours](./index.md)

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

![Architecture MCP](https://miro.medium.com/v2/resize:fit:1400/1*pTli88BeDE_GNI9j4PHXNg.png)


## Configuration de Burp Suite MCP

### Installation

1. Ouvrir Burp Suite et accéder au BApp Store.
2. Rechercher MCP et vérifier l'auteur ainsi que les fonctionnalités de l'extension.
3. Installer l'extension officielle : [PortSwigger MCP Server](https://github.com/PortSwigger/mcp-server).

![Installation de l'extension MCP](https://miro.medium.com/v2/resize:fit:1400/1*nSGuFsFeBJqQzQqVDZbNRw.png)

4. Dans l'onglet MCP, vérifier la configuration du serveur et les autorisations HTTP. Limiter les autorisations aux hôtes du laboratoire et conserver une validation des actions actives.

![Configuration des cibles HTTP](https://miro.medium.com/v2/resize:fit:1400/1*vxRSoZ7l2P5-33YfeoVEEg.png)

5. Pour Claude Desktop, utiliser l'installation proposée par l'extension. Pour une installation manuelle, récupérer le JAR compilé ou suivre les instructions de compilation du dépôt.

![Installation Claude Desktop](https://miro.medium.com/v2/resize:fit:1400/1*8YOLSkDrdFQhdIgzRAuEiw.png)

6. Si nécessaire, charger le JAR dans Extensions et vérifier l'adresse locale et le port.

![Configuration du serveur local](https://miro.medium.com/v2/resize:fit:1400/1*Eu0I4XcTSDBqYwTn72Yvug.png)


### Connexion à Claude Code

```bash
claude mcp add burp --transport sse http://127.0.0.1:9876
```

Ajoute le serveur MCP Burp à Claude Code. Adapter le port à la configuration réelle. La variante de syntaxe utilisée dans la documentation est `claude mcp add --transport sse burp http://127.0.0.1:9876`. Consulter les outils exposés dans la section MCP de Claude. Le transport SSE est celui utilisé dans cet exemple.

Documentation : [Claude Code MCP](https://code.claude.com/docs/en/mcp).

![Serveur Burp dans Claude Code](https://miro.medium.com/v2/resize:fit:1400/1*oXo-BKj4aDFTXVw9JCn1TQ.png)


## Collecte du trafic et reconnaissance

1. Ajouter l'application autorisée au scope dans Target.
2. Dans Proxy > HTTP history, activer Show only in-scope items.
3. Parcourir les fonctionnalités : formulaires, recherche, connexion, déconnexion, panier et API.
4. Si les règles du laboratoire le permettent, utiliser Engagement Tools > Discover Content pour compléter l'inventaire.
5. Arrêter la découverte, puis utiliser Show only parameterized requests pour isoler les requêtes paramétrées.

## Workflow Bug Bounty

Les exemples de prompts utilisent le domaine de démonstration `ginandjuice.shop`. Les prompts d'origine sont conservés en anglais pour les sections d'analyse et de reporting.

### Phase 1 — Analyse de l'historique HTTP

```text
  List the requests in my Burp proxy history, showing method, URL, and status code for each. Then do all of this in order:
  1) Summarize what this application is and its main features.
  2) Filter history to only ginandjuice.shop requests and highlight the most interesting ones (login, search, cart, checkout, APIs).
  3) List all API endpoints in a table with method, path, and parameters.
  4) Scan history for sensitive data — passwords, tokens, API keys, emails, personal info.
  5) Give me a final summary of what this app does and which endpoints are worth testing.
```

Transforme les captures HTTP en inventaire exploitable.

![Analyse de l'historique HTTP](https://miro.medium.com/v2/resize:fit:1400/1*kp_wvHtJeM9ZSUE8FYcJAQ.png)


### Phase 2 — Cartographie de la surface d'attaque

```text
Analyze my Burp proxy history for ginandjuice.shop and identify the attack surface. In order:
  1) Find all requests with search or q parameters — injection candidates.
  2) Find all requests with numeric ID parameters (like id=1, /api/xxx/1, order numbers) — IDOR candidates.
  3) Find admin, profile, user, account, upload, and API endpoints.
  4) Find any JavaScript files in history and fetch the interesting ones, looking for hardcoded secrets, API paths, or clues.
  5) Output a clean prioritized list: the top 6 endpoints to test for bugs, grouped by bug type (SQLi, XSS, IDOR, auth).
```

Organise les surfaces applicatives et les contrôles de sécurité à examiner.

![Cartographie applicative](https://miro.medium.com/v2/resize:fit:1400/1*zi9X-ZEL8B9OvlbL2_6c5g.png)


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

![Résultats de l'analyse](https://miro.medium.com/v2/resize:fit:1400/1*zaoccEruIK8FJBOPEuBsag.png)


### Phase 4 — Rapport final

```text
Write a professional pentest-style summary report of everything we found on ginandjuice.shop. For each finding include: vulnerability name, severity
(Critical/High/Medium/Low), affected endpoint, how it was exploited, and the proof (request + response). End with a prioritized fix list, most critical first. Also save
 the interesting requests to Burp Organizer for evidence.
```

Centralise les preuves et distingue les constats confirmés des observations.

![Rapport final](https://miro.medium.com/v2/resize:fit:1400/1*P839XfMuiuLfvd2m2yCLQg.png)


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

![Workflow global](https://miro.medium.com/v2/resize:fit:1400/1*MD-U_vtWLmmTapcpGPB5sQ.png)


![Résultats du workflow](https://miro.medium.com/v2/resize:fit:1400/1*cw-wq_wwynUMQDnI7YBvXQ.png)


![Synthèse du workflow](https://miro.medium.com/v2/resize:fit:1400/1*5FfJVbQPCZTMnK5M178nWw.png)

## Analyse sans Burp MCP

Claude Code peut également travailler directement sur des requêtes HTTP, des fichiers JavaScript et du code source.

### Analyser une requête HTTP brute

Exporter une requête Burp dans un fichier texte. Exemple fictif d'inscription :

```text
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
Identify:
1. All user-controlled inputs and parameters.
2. Authentication and authorization mechanisms.
3. Interesting IDs and object references.
4. Potential IDOR/BOLA candidates.
5. Injection points.
6. Business-logic parameters.
7. Security-relevant headers and cookies.
8. Any unusual behavior that deserves further testing.

Rank each issue by severity. For each interesting point, explain why it is worth investigating and suggest manual testing steps.
Do not assume a vulnerability exists.
Separate observations from hypotheses.
```

### Analyser un fichier JavaScript

```text
Analyze this JavaScript file from a bug bounty perspective.

Extract and categorize:
1. API endpoints and URL paths.
2. HTTP methods.
3. Parameters and parameter names.
4. Authentication and authorization logic.
5. Hardcoded secrets, tokens, or API keys.
6. Administrative or internal endpoints.
7. Upload and download functionality.
8. Debug or development endpoints.
9. Hidden functionality and feature flags.
10. Interesting DOM sources and sinks.
11. Third-party integrations.

For every interesting discovery, explain why it deserves further investigation.
Do not report something as a vulnerability unless there is enough evidence to support it.
```

### Analyser un JavaScript depuis une URL

```text
Analyze this JavaScript file for security-relevant information:
<JS_URL>
Look for:
1. API endpoints and hidden routes
2. Interesting parameters
3. Authentication or authorization logic
4. Hardcoded secrets or sensitive information
5. Internal or administrative functionality
6. Debug or development endpoints
7. Client-side security issues
8. Anything else that could be useful for authorized security testing
For each finding, explain why it is interesting and provide the relevant code or URL as evidence.
```

### Analyser plusieurs fichiers JavaScript

```text
Analyze every JavaScript file in this directory.
Build a consolidated attack-surface map containing:

1. API endpoints
2. HTTP methods
3. Parameters
4. Authentication functionality
5. Authorization logic
6. Administrative functionality
7. Upload/download features
8. WebSocket endpoints
9. Third-party integrations
10. Hardcoded secrets or credentials
11. Interesting client-side sinks
12. Hidden or undocumented functionality

Deduplicate identical endpoints and group related functionality together.

For each discovery, include relevant details and explain why it is interesting from a security-testing perspective.

At the end, rank the top 10 discoveries that deserve manual security testing and explain why each one is interesting.

Do not assume a vulnerability exists. Clearly separate observed functionality from security hypotheses.
```

### Examiner une vulnérabilité spécifique — IDOR/BOLA

```text
Analyze this request for a possible IDOR/BOLA vulnerability.

Explain:
1. Why this request could be interesting.
2. Which parameter controls the object being accessed.
3. What needs to change to test the authorization boundary.
4. What response differences would confirm the issue.
5. How I should manually validate the finding.

Do not assume the vulnerability exists.
Clearly distinguish observations from hypotheses.
Explain what evidence would be required to confirm the issue.
```

### Revue du code source

```text
Review this source code from a security perspective.

Identify:
1. Authentication weaknesses.
2. Authorization and access-control issues.
3. Input validation problems.
4. Injection risks.
5. Sensitive information exposure.
6. Insecure file handling.
7. Session-management issues.
8. Business-logic flaws.

For every confirmed or evidence-supported issue:
- Explain the root cause.
- Point to the relevant code.
- Explain the security impact.
- Suggest a secure fix.
- Explain how the issue could be manually validated in an authorized environment.

Do not report theoretical issues without explaining the evidence.
Clearly distinguish confirmed issues, security-relevant observations, and hypotheses.
Prioritize findings by severity and practical exploitability.
```

### Générer un rapport Bug Bounty

```text
Based on the provided HTTP requests, JavaScript analysis, recon results, and testing notes, create a professional bug bounty report.

For each confirmed finding, include:
- Title
- Severity
- Affected endpoint
- Vulnerability class
- Steps to reproduce
- Evidence
- Security impact
- Remediation

Structure the report clearly and professionally.

Separate:
1. Confirmed vulnerabilities
2. Security-relevant observations
3. Potential issues requiring further validation

Do not include speculative findings as confirmed vulnerabilities.
Only classify an issue as a confirmed vulnerability when the provided evidence demonstrates an actual security impact.
Clearly distinguish observed behavior from security conclusions.
Rank confirmed findings by severity and practical impact.
```

## Corrélation des résultats

### Structure du projet

```text
project/
├── recon/
│   ├── subdomains.txt
│   ├── alive.txt
│   └── urls.txt
│
├── requests/
│   ├── login.txt
│   ├── profile.txt
│   └── api.txt
│
├── javascript/
│   ├── app.js
│   ├── dashboard.js
│   └── auth.js
│
└── source/
    └── application-code/
```

### Prompt de corrélation

```text
You are assisting with an authorized security assessment.
Analyze the files in this project and correlate the information across recon, HTTP requests, JavaScript, and source code.

Build:

1. An attack-surface map.
2. An API inventory.
3. An authentication and authorization map.
4. A list of interesting parameters and object IDs.
5. Hidden functionality discovered in JavaScript or source code.
6. Potential vulnerability hypotheses.
7. A prioritized manual testing plan.
8. Confirmed findings supported by the provided evidence.
9. A professional security report.

Do not treat suspicious patterns as confirmed vulnerabilities.

For every finding, clearly explain the evidence that supports it and what additional validation is required.
```

Cette approche constitue une alternative à MCP pour l'analyse d'artefacts déjà collectés.

[Vidéo — Analyse des artefacts avec Claude Code](https://www.youtube.com/watch?v=Vr-NEWVLN9Y)


## Skills Claude Code

Une Skill formalise une méthodologie réutilisable : description, ressources, étapes, critères de validation et format des résultats. Elle évite de répéter les mêmes instructions à chaque revue.

### Ressources communautaires

[Skills.sh](https://skills.sh/) propose un catalogue de Skills pour agents IA. Examiner le code, la licence, les permissions et les dépendances avant installation.

![Catalogue des Skills](https://miro.medium.com/v2/resize:fit:1400/1*Ts9JbWP72mEbc7FxFXYSAQ.png)


### Dépôts de Skills

- Claude-Red — SnailSploit
- Claude-BugHunter — elementalsouls
- Agentic-Bug-Hunter — Awarexone

![Collections de Skills](https://miro.medium.com/v2/resize:fit:1400/1*nEEBjvOwGRIxrDnJS7zXuw.png)

### Skills personnalisées

Une Skill peut être construite à partir de notes de recherche, d'une méthodologie de test, de fichiers de référence et de procédures de validation existantes. Le fichier principal SKILL.md définit son rôle et son workflow ; les ressources associées apportent le contexte nécessaire.

![Structure d'une Skill](https://miro.medium.com/v2/resize:fit:1400/1*GxiOymmzy7yuOchJ5bHERg.png)


![Format SKILL.md](https://miro.medium.com/v2/resize:fit:1400/1*CDvK8ZpiMF6cfeylT1vWag.png)


![Organisation des ressources](https://miro.medium.com/v2/resize:fit:1400/1*vXLXk943Mb_OtI0eb1C3pA.png)


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

[Vidéo — Création d'une Skill personnalisée](https://www.youtube.com/watch?v=yTmfDSkr8sI)


[Retour au parcours](./index.md)

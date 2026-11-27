---
title: IA et Bug Bounty
aside: true
prev: false
next: false
---

# La meilleure configuration de Claude Code pour le Bug Bounty

*Transformez Claude Code en un puissant assistant de Bug Bounty grâce à MCP, aux Skills personnalisées, aux agents, aux outils et aux workflows de sécurité automatisés.*

*Publié le 27 août 2026 · Gratuit : non*

### Introduction

**Le Bug Bounty** ne consiste pas uniquement à trouver des vulnérabilités. Il implique également la reconnaissance, l’analyse du JavaScript et des requêtes HTTP, la cartographie de la surface d’attaque, les tests et la rédaction de rapports. Une grande partie de ce travail est répétitive, et c’est là que Claude Code et MCP interviennent. Dans ce guide, je vais vous montrer comment tout configurer depuis zéro, automatiser certaines parties du workflow et connecter Claude Code directement à Burp Suite via MCP.

### Qu’est-ce que Claude Code ?

Claude Code est un assistant de programmation agentique d’Anthropic qui fonctionne dans le terminal. Au lieu d’interagir avec une IA uniquement via un navigateur, vous pouvez l’exécuter directement dans votre terminal et lui permettre de travailler avec des fichiers, des commandes et d’autres outils. Cela le rend particulièrement intéressant pour la recherche en sécurité, car une grande partie du workflow de Bug Bounty se déroule déjà dans le terminal.

Par exemple, vous pourriez avoir un répertoire contenant :

```typescript
target/
├── javascript/
├── requests/
├── urls.txt
├── endpoints.txt
└── notes/
```

Claude Code peut travailler avec le contexte de ce projet sans vous obliger à tout copier manuellement dans une interface de conversation.

### Qu’est-ce que MCP ?

MCP signifie **Model Context Protocol**. En termes simples, il permet aux modèles d’IA comme Claude de se connecter à des outils externes et d’interagir réellement avec eux. Imaginez Claude comme le cerveau et MCP comme le pont. Sans MCP, Claude peut comprendre vos instructions et analyser les informations que vous lui fournissez, mais il ne peut pas interagir directement avec des outils comme Burp Suite. Une fois le serveur MCP de Burp Suite connecté, Claude peut accéder à votre historique HTTP de Burp et utiliser les outils proposés par Burp MCP pour analyser le trafic capturé et interagir avec celui-ci.

![Architecture MCP](https://miro.medium.com/v2/resize:fit:1400/1*pTli88BeDE_GNI9j4PHXNg.png)

### Étape 1 : Configuration du serveur MCP de Burp Suite

Commençons par tout configurer. Pour cette démonstration, j’utilise un site web de test dédié afin de pouvoir expérimenter en toute sécurité sans affecter de cibles réelles.

1. **Installer l’extension :** ouvrez Burp Suite, accédez au **BApp Store** et recherchez « MCP ». Vérifiez les fonctionnalités et l’auteur de l’extension, puis cliquez sur **Install**. Une fois installée, elle devrait s’ouvrir dans un nouvel onglet.

![Installation de l'extension MCP](https://miro.medium.com/v2/resize:fit:1400/1*nSGuFsFeBJqQzQqVDZbNRw.png)

**2. Configurer les cibles automatiquement approuvées :** dans le nouvel onglet MCP, activez les options nécessaires. Vous verrez un paramètre nommé Auto-Approved HTTP Targets. Ajoutez votre domaine cible, ses sous-domaines ou utilisez un caractère générique (par exemple, *.test-target.com). Remarque : cette étape est cruciale. Elle évite à Claude de s’interrompre pour demander une autorisation à chaque interaction avec cet hôte.

![Configuration des cibles HTTP](https://miro.medium.com/v2/resize:fit:1400/1*vxRSoZ7l2P5-33YfeoVEEg.png)

**3. Récupérer le fichier JAR :**

- Si vous utilisez Claude Desktop, vous pouvez généralement utiliser le bouton d’installation intégré.

![Installation Claude Desktop](https://miro.medium.com/v2/resize:fit:1400/1*8YOLSkDrdFQhdIgzRAuEiw.png)

- Si vous exécutez Claude depuis votre terminal, vous avez besoin du fichier JAR compilé. Vous pouvez l’extraire de l’extension ou le générer en suivant les instructions de compilation du dépôt GitHub officiel du projet.

[**GitHub - PortSwigger/mcp-server : serveur MCP pour Burp**](https://github.com/PortSwigger/mcp-server)
*Serveur MCP pour Burp. Contribuez au développement de PortSwigger/mcp-server en créant un compte GitHub.*

4. **Charger l’extension :** accédez à l’onglet Extensions de Burp Suite et chargez le fichier JAR de MCP. Une fois chargé, vérifiez que le serveur MCP fonctionne sur localhost avec le port qui lui a été attribué.

![Configuration du serveur local](https://miro.medium.com/v2/resize:fit:1400/1*Eu0I4XcTSDBqYwTn72Yvug.png)

5. **Connecter Claude :** ouvrez enfin votre terminal et saisissez la commande de connexion fournie par l’extension pour relier Claude à votre serveur Burp MCP local.

```csharp
claude mcp add burp --transport sse http://127.0.0.1:9876
```

![Serveur Burp dans Claude Code](https://miro.medium.com/v2/resize:fit:1400/1*oXo-BKj4aDFTXVw9JCn1TQ.png)

Si vous accédez à la section MCP de Claude, votre serveur Burp MCP devrait désormais apparaître dans la liste. En cliquant sur **View Tools**, vous découvrirez toutes les fonctionnalités de Burp auxquelles Claude a maintenant accès.

### Étape 2 : Collecte du trafic et reconnaissance

Avant de commencer les tests avec l’IA, nous devons lui fournir suffisamment de données pour comprendre la cible et sa surface d’attaque.

1. **Définir le périmètre :** ouvrez le site web cible, assurez-vous que le Proxy de Burp est activé et ajoutez votre cible au périmètre dans l’onglet **Target**.
2. **Filtrer l’historique :** accédez au filtre de l’historique HTTP et sélectionnez « **Show only in-scope items.** » Cela élimine le bruit et garantit que Burp ne suit que le trafic pertinent.
3. **Exploration manuelle :** parcourez l’application cible comme un utilisateur ordinaire. Cliquez sur les boutons, remplissez les formulaires, testez les champs de recherche, connectez-vous, déconnectez-vous et interagissez avec autant de fonctionnalités que possible. L’objectif est d’alimenter votre historique HTTP avec un ensemble riche d’URL, d’endpoints d’API et de paramètres.
4. **Découverte automatisée (facultative mais recommandée) :** pour approfondir la recherche, accédez à l’onglet Target, ouvrez **Engagement Tools** et sélectionnez **Discover Content**. Laissez Burp explorer l’application pour trouver des répertoires et endpoints cachés.
5. **Affiner l’affichage :** une fois que vous avez suffisamment de trafic, arrêtez l’exploration. Retournez dans le filtre de l’historique HTTP et cochez « **Show only parameterized requests.** » Vous visualisez maintenant les requêtes les plus pertinentes pour les tests de sécurité.

### Étape 3 : Workflow de recherche de vulnérabilités avec l’IA

Voici la partie intéressante. Nous allons utiliser Claude Code pour analyser les données que nous venons de collecter.

#### Phase 1 : Analyse et organisation du trafic

Au lieu de parcourir des centaines de requêtes brutes, nous utilisons notre premier prompt pour demander à Claude :

**Prompt 1 — Lister et comprendre l’historique**

```sql
  List the requests in my Burp proxy history, showing method, URL, and status code for each. Then do all of this in order:
  1) Summarize what this application is and its main features.
  2) Filter history to only ginandjuice.shop requests and highlight the most interesting ones (login, search, cart, checkout, APIs).
  3) List all API endpoints in a table with method, path, and parameters.
  4) Scan history for sensitive data — passwords, tokens, API keys, emails, personal info.
  5) Give me a final summary of what this app does and which endpoints are worth testing.
```

![Analyse de l'historique HTTP](https://miro.medium.com/v2/resize:fit:1400/1*kp_wvHtJeM9ZSUE8FYcJAQ.png)

Claude analysera les données, supprimera les doublons et vous fournira une vue d’ensemble claire de l’application. Il identifiera les endpoints d’API, les paramètres intéressants et toute information sensible exposée dans le trafic.

### Phase 2 : Cartographie de la surface d’attaque

Ensuite, nous demanderons à Claude de rechercher les zones susceptibles de contenir des vulnérabilités :

**Prompt 2 — Sélectionner la surface d’attaque**

```sql
Analyze my Burp proxy history for ginandjuice.shop and identify the attack surface. In order:
  1) Find all requests with search or q parameters — injection candidates.
  2) Find all requests with numeric ID parameters (like id=1, /api/xxx/1, order numbers) — IDOR candidates.
  3) Find admin, profile, user, account, upload, and API endpoints.
  4) Find any JavaScript files in history and fetch the interesting ones, looking for hardcoded secrets, API paths, or clues.
  5) Output a clean prioritized list: the top 6 endpoints to test for bugs, grouped by bug type (SQLi, XSS, IDOR, auth).
```

![Cartographie applicative](https://miro.medium.com/v2/resize:fit:1400/1*zi9X-ZEL8B9OvlbL2_6c5g.png)

Claude transforme la liste brute d’URL en une cartographie claire de la surface d’attaque, en indiquant quelles requêtes méritent d’être examinées pour chaque type de vulnérabilité.

### Phase 3 : Tests actifs de vulnérabilités

C’est ici que nous passons aux **véritables tests de sécurité**. Nous demanderons à Claude de tester les endpoints et les types de vulnérabilités pertinents identifiés lors de la phase précédente.

**Prompt 3 — Tester les vulnérabilités (la partie principale)**

```sql
Using the endpoints from the attack surface list, test ginandjuice.shop for vulnerabilities, one bug class at a time. Do them in this order and report a one-line result
  after each test:
  1) SQL injection — test the search endpoint with a single quote, OR  and UNION SELECT payloads.
  2) Reflected XSS — inject <script>alert(1)</script> into search and product parameters, check if it's reflected unencoded.
  3) IDOR — take order/profile requests and swap the ID for neighboring numbers (1, 2, 3); compare response lengths to confirm access to other users' data.
  4) Weak/default credentials — test login with common combos like admin/admin, admin@ginandjuice.shop:admin123, and note the exact error messages (user enumeration).
  5) User enumeration — compare login responses for a fake email vs an existing email.
  6) Rate limiting — send the login request 10 times fast; is there any lockout or rate limit?
  7) Broken access control — try hitting admin-only API endpoints (like /api/Users or /api/Products) unauthenticated.
  8) Business logic — try common coupon codes like GIN or JUICE and check if the discount can be reused.
  At the end, list every confirmed or suspected finding with severity, the endpoint, and which request proved it.
```

Cette phase peut prendre un certain temps. Pendant l’exécution de Claude, appuyez sur **Ctrl+O** pour afficher ses processus en arrière-plan. Vous pourrez observer Claude envoyer des requêtes via Burp Suite en utilisant la connexion MCP, tester différents paramètres et analyser les réponses HTTP obtenues.

![Résultats de l'analyse](https://miro.medium.com/v2/resize:fit:1400/1*zaoccEruIK8FJBOPEuBsag.png)

Une fois les tests terminés, Claude fournira une liste des vulnérabilités testées en distinguant les résultats confirmés des problèmes suspectés. Il inclura également les requêtes HTTP pertinentes et les éléments de preuve associés à chaque constat.

### Phase 4 : Génération du rapport final

Enfin, nous transformons les résultats validés en un **rapport de sécurité clair et professionnel**, comprenant les endpoints affectés, les preuves techniques, l’impact, la sévérité et les mesures correctives recommandées.

**Prompt 4 — Finaliser comme un professionnel**

```vbnet
Write a professional pentest-style summary report of everything we found on ginandjuice.shop. For each finding include: vulnerability name, severity
(Critical/High/Medium/Low), affected endpoint, how it was exploited, and the proof (request + response). End with a prioritized fix list, most critical first. Also save
 the interesting requests to Burp Organizer for evidence.
```

![Rapport final](https://miro.medium.com/v2/resize:fit:1400/1*P839XfMuiuLfvd2m2yCLQg.png)

En quelques secondes, Claude génère un rapport clair et bien organisé, prêt à être soumis à un programme de Bug Bounty.

### Le prompt One-Shot

Si l’exécution séparée des quatre phases vous semble trop chronophage, vous pouvez les combiner dans un seul prompt « **One-Shot** ». Celui-ci demande à Claude de gérer l’intégralité du workflow en une seule fois, depuis l’analyse des données et la cartographie de la surface d’attaque jusqu’aux tests de vulnérabilités, à la validation des résultats et à la génération du rapport final.

```sql
ROLE
  You are a senior bug bounty hunter running a structured engagement against a live demo e-commerce target. You work methodically, you validate everything with real PoCs,
  and you never inflate severity. Every phase below builds on the previous one — do not skip ahead.

  SCOPE & RULES
  - Target: https://ginandjuice.shop/ only. Ignore every other host in Burp history.
  - Primary toolkit: Burp MCP (proxy history, regex filtering, Repeater, Collaborator, encoding). Direct HTTP calls only as a fallback.
  - Time-box each attempt: two clean exploitation tries per bug class, then move on. Dead ends are normal — log the negative result and continue.
  - Evidence-first: no finding enters the report without a reproducible request/response pair.

  PHASE 1 — PRE-ENGAGEMENT INTEL & SURFACE MODELING
  1. Build the operational picture from proxy history: inventory every host, page, endpoint, and API route; note methods and parameters.
  2. Fingerprint the stack: server headers, framework signatures, cookies (JWT? session cookie flags?), JS libraries, CDN/WAF presence.
  3. Mine the client side: fetch the JavaScript bundles in history and extract API paths, hardcoded secrets, and app logic clues (this is where hidden endpoints live).
  4. Map the auth model: login flow, token lifecycle, password reset behavior, registration, role structure, and any session-related headers.
  5. Regex-scan history for high-value signals: id=, search/q, admin|user|profile|upload paths, token/secret patterns, and sensitive data leakage.
  6. Produce an attack surface model: a scored list of endpoints with the bug classes most likely to succeed on each. No findings yet — this is intel only.

  PHASE 2 — ATTACK HYPOTHESES & PRIORITIZATION
  - Rank the attack surface by (impact × likelihood) ÷ effort. E-commerce priority: business logic and access control before generic injection.
  - Write 5-8 concrete attack hypotheses, e.g.: "the coupon endpoint accepts replay of a consumed code", "order IDs are sequential and unauthenticated reads leak customer
  data", "the search endpoint reflects input into the page without encoding".
  - State your expected evidence for each hypothesis before testing — a clean test needs a falsifiable claim.

  PHASE 3 — EXPLOITATION (in this order)
  1. Business logic: cart/price manipulation (negative quantities, tampered price fields, currency swaps), coupon logic (reuse, self-referral, rate), checkout state
  manipulation (skipping steps, reordering the flow).
  2. IDOR / broken object-level access: enumerate neighboring IDs on orders, profiles, and API objects; verify with response-content comparison, not just status codes.
  3. Authentication & session: default/weak creds, user enumeration, missing rate limiting, session fixation/invalidation gaps, token weaknesses.
  4. Access control: unauthenticated calls to user/admin APIs, privilege escalation via role or flag tampering, forced browsing.
  5. Injection: SQLi (classic, UNION, and blind via timing/boolean) on search and parameters; XSS (reflected in search, stored in reviews/profile fields, DOM sinks in
  JS); SSTI and command injection on file/export/convert features.
  6. Out-of-band: inject Collaborator payloads into any URL/fetch/image/import parameters for blind SSRF and XXE; poll for DNS/HTTP interactions.
  7. File upload & misc: extension/filter bypasses, content-type spoofing, same-origin serving, plus info disclosure (source maps, debug endpoints, backup files, verbose
  errors).

  PHASE 4 — CHAINING & IMPACT AMPLIFICATION (the part that makes findings severe)
  - For every confirmed primitive, map what it unlocks: can an IDOR pivot into account takeover? Can stored XSS capture an admin session? Can the coupon bug chain with
  registration into unlimited free orders? Can a leaked API key from JS escalate to admin API access?
  - Follow each chain to its maximum impact and document the full kill chain — a chain of two Mediums often reports as High/Critical.
  - Sweep for variant coverage: same bug class on other endpoints/parameters — one pattern, many surfaces.

  PHASE 5 — VALIDATION GATE (before anything enters the report)
  - Replay every finding with a clean, minimal request in Repeater; it must reproduce deterministically, twice.
  - Prove impact in the response: leaked data, executed code, state change, privileged action — no theoretical impact statements.
  - Kill any finding you can't stand behind. A report with 3 confirmed issues beats 12 speculative ones.
  - Store all PoC requests in Burp Organizer for the evidence appendix.

  PHASE 6 — PROFESSIONAL REPORT (triager-ready)
  Structure the final output exactly like a production submission:
  1. Executive summary — 3-4 lines: what the app is, what you found, overall risk posture.
  2. Findings — one entry per confirmed issue: Title / Severity (CVSS 3.1 vector + score) / Affected endpoint / Vulnerability class / Steps to reproduce (numbered,
  copy-pasteable) / Evidence (request + response excerpts) / Business impact (what an attacker actually gains) / Remediation (specific fix, not generic advice).
  3. Chained findings — for each chain, the component bugs and the escalation path.
  4. Summary table — all findings ranked by severity with a one-line fix each.
  5. Appendix — the Organizer request IDs as raw evidence.
  If the engagement produced no confirmed vulnerabilities, say exactly that, and close with the top 3 residual risks you observed with recommended hardening — a clean
  report is a credible report.
```

![Workflow global](https://miro.medium.com/v2/resize:fit:1400/1*MD-U_vtWLmmTapcpGPB5sQ.png)

![Résultats du workflow](https://miro.medium.com/v2/resize:fit:1400/1*cw-wq_wwynUMQDnI7YBvXQ.png)

![Synthèse du workflow](https://miro.medium.com/v2/resize:fit:1400/1*5FfJVbQPCZTMnK5M178nWw.png)

Comme le prompt One-Shot exécute l’intégralité du workflow en un seul processus, cela peut prendre un certain temps, notamment lorsqu’une grande quantité d’historique HTTP doit être analysée. Laissez Claude parcourir chaque phase. Une fois terminé, vous disposerez d’un rapport de sécurité complet, avec des résultats validés et des chaînes de vulnérabilités potentielles.

### Bonus : Recherche de vulnérabilités sans Burp MCP

Dans ma précédente vidéo, j’ai montré comment Claude Code peut travailler directement avec des artefacts de sécurité individuels, tels que des fichiers de requêtes brutes Burp et des **fichiers** JavaScript. Cette approche est beaucoup plus simple lorsque vous souhaitez uniquement examiner une requête précise, un fichier source ou un élément issu de la reconnaissance.

Ainsi, si vous ne souhaitez pas configurer **Burp MCP**, vous pouvez tout de même construire un workflow puissant en fournissant à Claude Code les données exactes que vous souhaitez analyser.

Voici quelques-uns des raccourcis les plus utiles :

#### 1. Analyser une requête brute Burp

Enregistrez toute requête Burp intéressante dans un fichier .txt, puis transmettez-le à Claude pour qu’il analyse la requête.

Voici un exemple réaliste de **requête brute Burp Suite** que vous pouvez utiliser pour la démonstration.

```makefile
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

Cela est utile lorsque vous disposez d’une requête particulièrement intéressante et souhaitez que Claude se concentre uniquement sur cette requête plutôt que sur l’intégralité de votre historique Burp.

#### 2. Analyser un fichier JavaScript

L’analyse JavaScript constitue un autre raccourci utile. Au lieu de connecter Claude à Burp, vous pouvez simplement lui fournir un fichier JavaScript et le laisser analyser directement le code.

```markdown
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

#### 3. Tester un fichier JavaScript directement depuis une URL

Vous n’avez pas toujours besoin de télécharger manuellement un fichier JavaScript. Si vous trouvez un fichier .js pendant la reconnaissance, vous pouvez transmettre directement son URL à Claude et lui demander de l’analyser.

Cela est utile lorsque vous trouvez un bundle JavaScript intéressant et souhaitez identifier rapidement des endpoints d’API, des routes cachées, des informations sensibles et d’autres indices pertinents pour la sécurité.

**Utilisez un prompt comme celui-ci :**

```markdown
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

#### 4. Analyser plusieurs fichiers JS

Si vous avez déjà collecté des fichiers JavaScript pendant la reconnaissance, placez-les dans un même répertoire et laissez Claude les analyser ensemble.

```markdown
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

Cela est particulièrement utile pour les grandes applications, dans lesquelles parcourir de nombreux fichiers JavaScript peut prendre beaucoup de temps.

#### 5. Demander à Claude d’examiner une vulnérabilité précise

Vous pouvez également utiliser Claude pour obtenir un second avis lorsque vous disposez déjà d’une requête suspecte.

**Par exemple :**

```vbnet
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

Cette approche fonctionne bien lorsque vous avez déjà découvert quelque chose manuellement et souhaitez que Claude vous aide à structurer l’investigation.

#### 6. Auditer le code source

Si le code source est disponible, Claude Code peut aller au-delà de la reconnaissance et contribuer à un audit de sécurité plus approfondi du code lui-même.

```markdown
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

Vous disposez ainsi d’un autre workflow qui ne nécessite pas du tout Burp.

#### 7. Transformer l’ensemble des résultats en rapport de Bug Bounty

Une fois votre investigation terminée, vous pouvez fournir les preuves à Claude et le laisser les organiser dans un rapport clair.

```vbnet
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

### Le raccourci complet

Le véritable avantage apparaît lorsque vous combinez ces approches.

**Vous pouvez fournir à Claude Code :**

```bash
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

**Demandez ensuite à Claude de faire le lien entre les éléments et de tout corréler :**

```markdown
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

Vous disposez ainsi d’une alternative légère au workflow MCP.

MCP est utile lorsque vous souhaitez que Claude interagisse directement avec Burp et travaille en continu avec le trafic en direct. Toutefois, si vous souhaitez uniquement que Claude analyse des artefacts précis, ces raccourcis peuvent être beaucoup plus rapides et plus faciles à mettre en place.

**Vous pouvez également regarder cette vidéo dans laquelle j’ai présenté la démonstration pratique complète de cette méthode :**

<!-- iframe: 854x480 -->
[Contenu intégré](https://cdn.embedly.com/widgets/media.html?src=https%3A%2F%2Fwww.youtube.com%2Fembed%2FVr-NEWVLN9Y%3Ffeature%3Doembed&display_name=YouTube&url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DVr-NEWVLN9Y&image=https%3A%2F%2Fi.ytimg.com%2Fvi%2FVr-NEWVLN9Y%2Fhqdefault.jpg&type=text%2Fhtml&schema=youtube)

### Les Skills de Claude Code pour la recherche de vulnérabilités

Les Skills de Claude Code permettent de transformer une méthodologie de recherche de vulnérabilités en un workflow réutilisable. Au lieu de donner à Claude les mêmes prompts et instructions à chaque fois, vous pouvez définir la méthodologie, les outils, le workflow, les payloads et les références dans une Skill et la réutiliser chaque fois que nécessaire.

Imaginez une Skill comme un template Nuclei, mais pour Claude. Au lieu de définir un test de vulnérabilité, une Skill définit la méthodologie que Claude doit suivre pour une tâche précise.

Les Skills sont particulièrement utiles pour les workflows répétitifs de recherche de vulnérabilités, car vous pouvez définir le processus une seule fois, puis le réutiliser sur différentes cibles autorisées.

#### Utiliser des Skills open source pour la recherche de vulnérabilités

Vous n’avez pas toujours besoin de créer chaque Skill vous-même. Il existe déjà des Skills open source créées par la communauté que vous pouvez installer et utiliser avec Claude Code.

![Catalogue des Skills](https://miro.medium.com/v2/resize:fit:1400/1*Ts9JbWP72mEbc7FxFXYSAQ.png)

[**L’annuaire des Skills pour agents**](https://www.skills.sh/)
*Découvrez et installez des Skills pour les agents d’IA.*

Vous pouvez consulter **skill.sh** pour parcourir les Skills disponibles et rechercher le type de workflow dont vous avez besoin. Vous trouverez différentes collections couvrant des domaines tels que l’OSINT, la recherche de vulnérabilités et la sécurité offensive.

#### Ajouter des Skills de recherche de vulnérabilités hébergées sur GitHub

En dehors de skill.sh, vous pouvez également trouver des Skills utiles pour la recherche de vulnérabilités directement sur GitHub. De nombreux chercheurs en sécurité publient leurs propres Skills et des collections complètes que vous pouvez ajouter à Claude Code.

![Collections de Skills](https://miro.medium.com/v2/resize:fit:1400/1*nEEBjvOwGRIxrDnJS7zXuw.png)

[**Claude-Red/Skills/web sur la branche main · SnailSploit/Claude-Red**](https://github.com/SnailSploit/Claude-Red/tree/main/Skills/web)
*claude-red est une bibliothèque sélectionnée de Skills de sécurité offensive conçues pour le système de Skills de Claude. Chaque Skill est une…*

[**GitHub - elementalsouls/Claude-BugHunter : un ensemble de Skills Claude Code pour la recherche de vulnérabilités et les…**](https://github.com/elementalsouls/Claude-BugHunter)
*Un ensemble de Skills Claude Code pour la recherche de vulnérabilités et les opérations Red Team externes : 82 Skills, 15 commandes slash, 681…*

[**GitHub - Awarexone/Agentic-Bug-Hunter : boîte à outils de Bug Bounty propulsée par l’IA, fonctionnant avec ou…**](https://github.com/Awarexone/Agentic-Bug-Hunter)
*Boîte à outils de Bug Bounty propulsée par l’IA, fonctionnant avec ou sans abonnement. - Awarexone/Agentic-Bug-Hunter*

Ces dépôts peuvent contenir des Skills pour des tâches précises, telles que la reconnaissance, la découverte de vulnérabilités, l’analyse des endpoints, les tests d’authentification, les tests d’API et d’autres parties du workflow de Bug Bounty.

### Créer vos propres Skills personnalisées pour la recherche de vulnérabilités

L’option la plus intéressante consiste à créer vos propres Skills à partir des méthodologies que vous utilisez déjà.

Vous pouvez prendre une méthodologie existante de recherche de vulnérabilités, comme un article de recherche, vos propres notes, un workflow de test ou une collection de techniques, et la convertir en une Skill réutilisable.

#### Structure et format d’une Skill Claude

![Structure d'une Skill](https://miro.medium.com/v2/resize:fit:1400/1*GxiOymmzy7yuOchJ5bHERg.png)

![Format SKILL.md](https://miro.medium.com/v2/resize:fit:1400/1*CDvK8ZpiMF6cfeylT1vWag.png)

Une Skill peut contenir le titre, la description, la méthodologie, les outils, les workflows, les payloads, les scripts et d’autres ressources que Claude peut utiliser pendant l’exécution de la tâche.

![Organisation des ressources](https://miro.medium.com/v2/resize:fit:1400/1*vXLXk943Mb_OtI0eb1C3pA.png)

Ensuite, au lieu de fournir un long prompt à chaque fois, vous pouvez simplement indiquer le nom de la Skill et les informations relatives à la cible. Claude peut suivre le workflow défini dans la Skill et générer les résultats dans un format cohérent.

#### Exemples de prompts pour créer des Skills personnalisées de recherche de vulnérabilités

Voici quelques exemples de prompts que vous pouvez utiliser pour transformer vos méthodologies existantes en Skills réutilisables.

#### **Skill de redirection ouverte (Open Redirect)**

```diff
Create a Claude Code Skill for finding and validating open redirect vulnerabilities.

Use the methodology below as the source material:

[PASTE YOUR OPEN REDIRECT METHODOLOGY HERE]

Convert this methodology into a complete reusable Skill. Include:
- Skill name and description
- Detection methodology
- Testing workflow
- Common parameters to test
- Payloads and bypass techniques
- Validation steps
- Useful CLI tools
- Expected findings and false positives
- Reporting workflow

Organize everything into a practical workflow Claude can follow during an authorized bug bounty assessment.

Do not invent techniques that are not supported by the methodology. Keep the Skill focused on open redirect testing.
```

#### **Skill XSS**

```diff
Create a Claude Code Skill for XSS hunting based on the methodology below:

[PASTE YOUR XSS RESEARCH OR NOTES HERE]

Turn this into a structured Skill that Claude can use during authorized security testing.

Include:
- Reconnaissance and input discovery
- Reflection detection
- Parameter and endpoint testing
- Context identification
- Payload selection
- Filter and encoding analysis
- Safe validation techniques
- Useful tools and commands
- False-positive handling
- Finding documentation and reporting

Preserve the methodology from my research and organize it into a repeatable workflow.
```

#### **Méthodologie personnalisée → Skill**

Vous pouvez également fournir à Claude une méthodologie complète et le laisser structurer la Skill pour vous :

```markdown
I have developed the following bug hunting methodology:

[PASTE YOUR COMPLETE METHODOLOGY HERE]

Convert this into a production-ready Claude Code Skill.

First understand the methodology and break it into logical phases.

Then create:
1. Skill name
2. Description
3. SKILL.md
4. Required tools
5. Testing workflow
6. Payloads or test cases
7. Helper scripts if required
8. Validation methodology
9. Reporting format
10. Any supporting resource files

Keep the workflow faithful to my original methodology.

The Skill will be used only for authorized security testing and bug bounty programs.

My locally installed security tools are available at:

[PASTE YOUR TOOL PATHS HERE]

Use these existing binaries when appropriate instead of attempting to install alternative versions.
```

Vous pouvez ensuite récupérer la Skill générée, examiner le fichier SKILL.md et les éventuels fichiers complémentaires, apporter des ajustements et placer le tout dans votre répertoire de Skills Claude.

C’est là que les Skills personnalisées deviennent particulièrement utiles. Au lieu d’expliquer votre méthodologie à Claude à plusieurs reprises, vous transformez votre expérience en un workflow réutilisable que vous pouvez continuellement améliorer.

**Vous pouvez également regarder cette vidéo dans laquelle j’ai présenté la démonstration pratique complète de cette méthode :**

<!-- iframe: 854x480 -->
[Contenu intégré](https://cdn.embedly.com/widgets/media.html?src=https%3A%2F%2Fwww.youtube.com%2Fembed%2FyTmfDSkr8sI%3Ffeature%3Doembed&display_name=YouTube&url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DyTmfDSkr8sI&image=https%3A%2F%2Fi.ytimg.com%2Fvi%2FyTmfDSkr8sI%2Fhqdefault.jpg&type=text%2Fhtml&schema=youtube)

### Conclusion

Ce workflow peut faire gagner des heures de travail répétitif lors de l’analyse du trafic, de la cartographie de la surface d’attaque, des tests et de la rédaction de rapports. Grâce aux Skills, vous pouvez également transformer vos propres méthodologies de recherche de vulnérabilités en workflows réutilisables et utiliser les Skills open source de la communauté. La véritable puissance réside dans la combinaison de MCP, des Skills, de prompts efficaces et de votre propre méthodologie, tout en continuant à valider manuellement les résultats.

### Avertissement

> _Le contenu fourni dans cet article est destiné uniquement à des fins éducatives et informatives. Assurez-vous toujours de disposer des autorisations nécessaires avant de réaliser des évaluations de sécurité. Utilisez ces informations de manière responsable._
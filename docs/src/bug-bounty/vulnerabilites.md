---
title: Tests de vulnérabilités
aside: true
prev: false
next: false
---

# Tests de vulnérabilités

[Retour au parcours](./index.md)

Objectif : choisir les contrôles adaptés aux fonctionnalités identifiées et distinguer les indices des vulnérabilités confirmées.

## Préparer les fichiers

Les inventaires du chapitre précédent ne sont pas des résultats de vulnérabilité. Les exemples historiques ci-dessous qui nécessitent leurs propres listes, captures ou wordlists sont indépendants : ne pas les exécuter comme une suite automatique.

| Fichier | Origine |
|---|---|
| `allurls.txt` | Inventaire Web validé au chapitre précédent |
| `js_inventory.txt` | Liste d'URL JavaScript, pas de scripts locaux |
| `headers.txt` | En-têtes d'une réponse HTTP de test, enregistrés manuellement |
| `reponse-compte-a.txt`, `reponse-compte-b.txt` | Réponses de deux comptes de test, exportées séparément |
| `jwt-test.txt` | Jeton de test enregistré localement |
| `openapi.json` | Spécification OpenAPI JSON obtenue légitimement |

## Subdomain Takeover

### Vérification du risque de Subdomain Takeover

```bash
subzy run --targets subexample.coms.txt --concurrency 100 --hide_fails --verify_ssl
```

Recherche des configurations potentiellement vulnérables avec Subzy.

> Exemple historique indépendant : `subexample.coms.txt` doit être préparé manuellement pour ce test. Il n'est pas créé par les étapes précédentes.


## Exposition de données

### Repérage de fichiers sensibles

```bash
cat allurls.txt | grep -E "\.xls|\.xml|\.xlsx|\.json|\.pdf|\.sql|\.doc|\.docx|\.pptx|\.txt|\.zip|\.tar\.gz|\.tgz|\.bak|\.7z|\.rar|\.log|\.cache|\.secret|\.db|\.backup|\.yml|\.gz|\.config|\.csv|\.yaml|\.md|\.md5"
```

Filtre une liste d'URL selon des extensions pouvant indiquer des fichiers exposés.

### Recherche de documents indexés

```text
site:*.example.com (ext:doc OR ext:docx OR ext:odt OR ext:pdf OR ext:rtf OR ext:ppt OR ext:pptx OR ext:csv OR ext:xls OR ext:xlsx OR ext:txt OR ext:xml OR ext:json OR ext:zip OR ext:rar OR ext:md OR ext:log OR ext:bak OR ext:conf OR ext:sql)
```

Requête de moteur de recherche filtrant les extensions de documents dans le périmètre autorisé.

### Détection de dépôts Git exposés

```bash
cat example.coms.txt | grep "SUCCESS" | gf urls | httpx-toolkit -sc -server -cl -path "/.git/" -mc 200 -location -ms "Index of" -probe
```

Exemple historique indépendant : `example.coms.txt` et son format avec le marqueur SUCCESS ne sont pas produits par le parcours. La chaîne n'a pas été validée.

### Filtrage étendu des extensions sensibles

```bash
echo https://example.com | gau | grep -E "\.(xls|xml|xlsx|json|pdf|sql|doc|docx|pptx|txt|zip|tar\.gz|tgz|bak|7z|rar|log|cache|secret|db|backup|yml|gz|config|csv|yaml|md|md5|tar|xz|7zip|p12|pem|key|crt|csr|sh|pl|py|java|class|jar|war|ear|sqlitedb|sqlite3|dbf|db3|accdb|mdb|sqlcipher|gitignore|env|ini|conf|properties|plist|cfg)$"
```

Recherche des extensions de fichiers potentiellement sensibles dans les URL collectées.

### Recherche de buckets AWS S3

```bash
s3scanner scan -d example.com
```

Recherche des buckets associés au domaine indiqué.

### Recherche de secrets dans des fichiers JavaScript

```bash
cat allurls.txt | grep -E "\.js$" | httpx-toolkit -mc 200 -content-type | grep -E "application/javascript|text/javascript" | cut -d' ' -f1 | xargs -I% curl -s % | grep -E "(API_KEY|api_key|apikey|secret|token|password)"
```

Bloc historique recherchant des marqueurs de secrets dans les fichiers JavaScript. Traiter les résultats comme des indices, sans utiliser les secrets trouvés.

### Google API Keys et Gemini

L'exposition d'une clé Google API n'implique pas systématiquement une vulnérabilité. Le risque dépend des API activées, des restrictions de la clé, des quotas et des permissions associées au projet.

##### Inspection du code source local

```bash
git grep -l 'GEMINI_API_KEY'
```

Liste les fichiers suivis par Git contenant le nom de la variable, sans afficher sa valeur. À utiliser dans un dépôt dont on est propriétaire ou dont l'audit est autorisé. Un résultat peut correspondre à une simple référence à une variable d'environnement et ne confirme pas une fuite.

##### Points de contrôle

- Examiner les fichiers de configuration, les bundles JavaScript et les commits autorisés pour déterminer si une clé a été intégrée au code.
- Distinguer les clés destinées à un usage client des identifiants donnant accès à des services sensibles ou facturables.
- Vérifier les restrictions et les API activées depuis la console du projet, avec l'accord de son propriétaire.
- Ne pas assimiler un code HTTP 400 ou 403 à une preuve de révocation : plusieurs causes sont possibles.

##### Impact potentiel

| Risque | Conséquence possible |
| --- | --- |
| Quotas | Indisponibilité du service légitime |
| Facturation | Consommation non autorisée de ressources payantes |
| File API et Corpora | Exposition ou modification de données, selon les permissions |
| Autres services Google | Accès non prévu à des API activées sur le projet |

L'article cite également Maps, Firebase, Vision, Translate et YouTube Data. L'accès à un service ne prouve pas que les autres sont accessibles.

##### Rapport Bug Bounty

- Indiquer le fichier, l'URL ou le commit d'origine et le contexte de découverte.
- Masquer la valeur de la clé dans le rapport et les captures.
- Distinguer les capacités confirmées avec une autorisation explicite des hypothèses.
- Estimer le risque financier à partir des tarifs officiels, sans générer de dépenses sur un compte tiers.
- Recommander la révocation ou la rotation de la clé exposée, des restrictions adaptées aux API et applications, ainsi que la surveillance des quotas et de la facturation.

##### Documentation

- [Tarifs Gemini API](https://ai.google.dev/gemini-api/docs/pricing).
- [Google API Keys et Gemini - Truffle Security](https://trufflesecurity.com/blog/google-api-keys-werent-secrets-but-then-gemini-changed-the-rules).

Synthèse de l'article fourni, publié le 23 mai 2026. Les procédures de collecte massive, de réutilisation de clés tierces, de contournement des restrictions et de consommation de ressources ne sont pas reproduites. Une clé littérale présente dans le document d'origine n'a pas été publiée.

## Cross-Site Scripting (XSS)

### Collecte de candidats XSS

```bash
echo https://example.com/ | gau | gf xss | uro | Gxss | kxss | tee xss_output.txt
```

Chaîne d'outils pour repérer des paramètres candidats à une vérification XSS.

### Analyse XSS avec Dalfox

```bash
cat xss_params.txt | dalfox pipe --blind https://your-collaborator-url --waf-bypass --silence
```

Exemple historique indépendant de la collecte précédente : `xss_params.txt` n'est pas créé par le parcours. Ne pas confondre ce fichier avec `xss_output.txt` ou `xss_candidates.txt`.

> Les options et l'autorisation de tester doivent être vérifiées ; l'archive ne démontre pas la validité de la commande.

### Recherche de candidats XSS persistants

```bash
cat urls.txt | grep -E "(login|signup|register|forgot|password|reset)" | httpx -silent | nuclei -t nuclei-templates/vulnerabilities/xss/ -severity critical,high
```

Variante historique indépendante : le fichier `urls.txt` correspond à la variante GAU du chapitre Web, pas à l'inventaire principal validé.

> Ce filtrage ne démontre pas qu'une XSS est persistante.

### Recherche de candidats DOM XSS

```bash
cat js_files.txt | Gxss -c 100 | sort -u | dalfox pipe -o dom_xss_results.txt
```

Exemple historique indépendant : `js_files.txt` n'est pas produit par le parcours et le format attendu n'a pas été confirmé. Ne pas confondre des URL de scripts avec des fichiers JavaScript locaux.

> Le résultat n'établit pas à lui seul une DOM XSS.

### XSS - extraction des URL depuis un résultat local

```bash
grep -oP '^URL: \K\S+' xss_output.txt | sort -u > xss_candidates.txt
```

Extrait et déduplique les URL d'un résultat déjà enregistré au format URL: ... ; vérifier le format réel de la sortie. Contrairement à l'exemple source, conserve les valeurs des paramètres pour éviter de perdre les paramètres suivants. Une réflexion ne constitue pas une preuve de XSS.

### Méthode de validation

L'article XSS propose la collecte d'URL, le filtrage GF/URO, l'analyse de réflexion, le filtrage des types de contenu et la validation. Les commandes déjà présentes ne sont pas dupliquées. Examiner le contexte HTML ou JavaScript dans un laboratoire ; distinguer réflexion, DOM XSS et XSS stockée. Les variantes d'exploitation automatisée et de contournement WAF ne sont pas reproduites.

## XSS - protections et limites

La fiche archivée ne contient aucun bloc de commandes.

### Bonnes pratiques

La fiche traite des différences de comportement des filtres WAF selon leur version, les encodages, les attributs HTML et le contexte JavaScript. Pour une évaluation en laboratoire, relever la version et la configuration du filtre, documenter les résultats et vérifier le comportement réel du navigateur. Une réflexion de chaîne ne démontre pas à elle seule une exécution JavaScript. Corriger la cause de la XSS plutôt que de compter uniquement sur le WAF.

## SQL Injection (SQLi)

La fiche Lostsec fournie contient 22 exemples portant sur la reconnaissance, les tests automatisés, les en-têtes HTTP et les différences entre moteurs SQL. Les exemples historiques ne sont pas tous syntaxiquement valides et n'ont pas été exécutés.

### Reconnaissance

- Identifier les technologies des services Web autorisés.
- Recenser les URL paramétrées avec les méthodes GAU et Katana déjà présentes dans [Collecte des URL](./cartographie-web.md#collecte-des-url).
- Une extension PHP, ASP ou JSP ne démontre pas une injection SQL.
- Inventorier les paramètres, cookies et en-têtes traités par l'application.

### Validation en laboratoire

- Distinguer les comportements MySQL, PostgreSQL, Oracle et Microsoft SQL Server.
- La fiche présente notamment les injections aveugles temporelles : une variation de latence doit être comparée à des mesures de référence pour écarter les faux positifs.
- Limiter les tests à des données fictives et ne pas extraire de bases de données réelles.
- Consigner la configuration, les mesures, les observations et les limites du test.
- Recommander les requêtes paramétrées et la réduction des privilèges du compte de base de données.

La fiche comporte aussi des chaînes de tests automatisés en masse et des variantes de contournement de filtres. Elles ne sont pas reproduites dans cette synthèse. Les exemples de reconnaissance déjà présents dans la cheatsheet ne sont pas dupliqués.

### SQLmap et Ghauri

Les deux outils automatisent des vérifications d'injection SQL. SQLmap couvre plusieurs moteurs et techniques ; Ghauri met notamment l'accent sur les injections aveugles booléennes et temporelles. Le document présente les requêtes GET, POST, JSON et les requêtes HTTP enregistrées depuis Burp Suite.

```bash
sqlmap -hh
```

Affiche l'aide détaillée de la version installée de SQLmap, sans contacter une cible.

Pour une validation en laboratoire, examiner les paramètres transmis, utiliser des comptes de test, conserver les échanges HTTP et respecter les limites de requêtes. Les techniques de contournement de WAF, d'extraction de données et de prise de contrôle du serveur détaillées par l'article ne sont pas reproduites.

[SQLmap et Ghauri - article de référence](https://infosecwriteups.com/mastering-sqlmap-and-ghauri-a-practical-guide-to-waf-bypass-techniques-1aaa9eee9d32) (15 janvier 2026).

### Ressources de pratique

- [PortSwigger - SQL injection](https://portswigger.net/web-security/sql-injection) : cours et laboratoires dédiés aux injections SQL.
- [PortSwigger - Cross-site scripting](https://portswigger.net/web-security/cross-site-scripting) : cours et laboratoires dédiés aux XSS.

## Local File Inclusion (LFI)

### Recherche de LFI

```bash
echo "https://example.com/" | gau | gf lfi | uro | sed 's/=.*/=/' | qsreplace "FUZZ" | sort -u | xargs -I{} ffuf -u {} -w payloads/lfi.txt -c -mr "root:(x|\*|\$[^\:]*):0:0:" -v
```

Bloc historique de test LFI avec une liste de charges de test et FFUF.

## Server-Side Request Forgery (SSRF)

Une SSRF survient lorsqu'une application effectue une requête côté serveur vers une destination contrôlée par un utilisateur sans appliquer les restrictions nécessaires. Elle peut exposer des ressources normalement inaccessibles depuis Internet.

### Types de SSRF

| Type | Observation |
| --- | --- |
| In-band | Le contenu de la réponse distante est renvoyé par l'application. |
| Blind | La requête est effectuée sans restitution directe de son contenu. |
| Semi-blind | Des différences de latence, de statut ou d'erreur fournissent des indices indirects. |

Une interaction DNS isolée ou une variation de temps ne démontre pas à elle seule un accès à une ressource interne.

### Points d'entrée

- Prévisualisation de liens, import de fichiers distants et webhooks.
- Conversion PDF, traitement d'images SVG et de vidéos.
- Parseurs XML et flux RSS/Atom.
- Mutations GraphQL acceptant des URL et proxys WebSocket.
- En-têtes HTTP interprétés par les composants backend.

Examiner les fonctionnalités qui récupèrent une ressource distante. Les paramètres dont le nom évoque une URL ne constituent pas, à eux seuls, une preuve de SSRF.

### Serveur HTTP de démonstration locale

```bash
mkdir -p ssrf-lab
printf 'SSRF-LAB-TEST\n' > ssrf-lab/test.txt
python3 -m http.server 8080 --bind 127.0.0.1 --directory ssrf-lab
```

Démarre un serveur de test accessible uniquement depuis la machine locale, avec un fichier témoin fictif. Ne pas exposer un dossier contenant des données personnelles ou des secrets.

### Validation in-band dans un laboratoire local

```bash
curl -s -i --get 'http://127.0.0.1:8000/api/preview' \
  --data-urlencode 'url=http://127.0.0.1:8080/test.txt'
```

Adaptation de l'exemple de l'article pour un laboratoire local : suppose qu'une application de test déjà disponible sur le port 8000 possède cette route et accepte le paramètre url. Observer si le marqueur SSRF-LAB-TEST apparaît dans la réponse et comparer avec le comportement attendu. Le test ne nécessite pas de consulter des données réelles.

### Blind SSRF et interactions OOB

L'article présente les outils suivants pour observer les interactions DNS ou HTTP dans un environnement explicitement autorisé :

- [Interactsh](https://github.com/projectdiscovery/interactsh)
- [Burp Collaborator](https://portswigger.net/burp/documentation/collaborator)
- [Webhook.site](https://webhook.site/)
- [RequestRepo](https://requestrepo.com/requests)

Distinguer les interactions provenant du navigateur, du serveur de test et d'intermédiaires. Ne pas transférer de données sensibles vers des services de callback externes.

### Validation des URL et risques de contournement

L'article décrit les différences de représentation des adresses IP, les divergences entre parseurs d'URL, les protocoles alternatifs, le DNS rebinding et les redirections HTTP. Ces situations justifient des contrôles de destination robustes et cohérents au moment de la connexion, plutôt qu'un simple filtre textuel.

### Impact potentiel

- Accès involontaire aux services et interfaces internes.
- Exposition de fichiers ou de métadonnées cloud.
- Accès à des identifiants selon la configuration des services concernés.
- Exécution de code à distance dans certaines chaînes de vulnérabilités.

La gravité dépend des capacités réellement démontrées. Ne pas extraire de secrets, cartographier les réseaux privés ou modifier les services d'un tiers pour augmenter artificiellement l'impact du rapport.

### Remédiation

- Autoriser uniquement les protocoles et destinations nécessaires à la fonctionnalité.
- Normaliser les URL et vérifier les adresses IPv4 et IPv6 obtenues après résolution DNS.
- Bloquer les destinations privées, loopback et link-local lorsqu'elles ne sont pas nécessaires.
- Désactiver les redirections automatiques ou vérifier chaque nouvelle destination.
- Restreindre le trafic sortant du serveur et isoler les composants de conversion.
- Appliquer le principe du moindre privilège aux identités cloud.

### Rapport Bug Bounty

Documenter la fonctionnalité concernée, le comportement attendu, la requête de test, les observations et les limites de la preuve. Distinguer l'impact confirmé des scénarios possibles. Les montants de primes ne peuvent pas être déduits du type de SSRF seul.

### Références

- [The Ultimate Guide to SSRF](https://lostsec.medium.com/the-ultimate-guide-to-ssrf-hunting-bypassing-and-exploiting-in-modern-bug-bounty-a43fa34ba324), publié le 24 octobre 2026.
- [PortSwigger - SSRF](https://portswigger.net/web-security/ssrf).

Synthèse de l'article fourni avec adaptation locale des exemples de validation. Les charges de contournement, de collecte d'identifiants cloud, de lecture de fichiers sensibles et de prise de contrôle de services ne sont pas reproduites. Les exemples de laboratoire n'ont pas été exécutés.

## Cross-Origin Resource Sharing (CORS)

### Vérification des en-têtes CORS

```bash
curl -H "Origin: http://example.com" -I https://example.com/wp-json/
```

Observe les en-têtes renvoyés pour une requête contenant Origin.

### Analyse avec CORScanner

```bash
python3 CORScanner.py -u https://example.com -d -t 10
```

Recherche des configurations CORS potentiellement incorrectes.

### Détection CORS avec Nuclei

```bash
cat example.coms.txt | httpx -silent | nuclei -t nuclei-templates/vulnerabilities/cors/ -o cors_results.txt
```

Exemple historique indépendant : `example.coms.txt` n'est pas produit par le parcours. Les modèles et la chaîne n'ont pas été validés.

### Vérification de la réflexion d'Origin

```bash
curl -H "Origin: https://evil.com" -I https://example.com/api/data | grep -i "access-control-allow-origin: https://evil.com"
```

Vérifie si un en-tête de réponse reflète l'origine envoyée.

> La réflexion seule ne suffit pas à démontrer une vulnérabilité exploitable.

## WordPress

### Analyse WordPress avec WPScan

```bash
wpscan --url https://example.com --disable-tls-checks --api-token YOUR_TOKEN -e at -e ap -e u --enumerate ap --plugins-detection aggressive --force
```

Commande historique d'énumération WordPress et de recherche de vulnérabilités.

> Mode agressif et vérification TLS désactivée dans l'original. Ne pas utiliser tel quel hors d'un lab adapté.

## Microsoft IIS et ASP.NET

### Identification via HTTP

```bash
curl -I https://example.com
```

Affiche les en-têtes HTTP. Rechercher notamment Server et X-Powered-By ; ces en-têtes peuvent être absents ou modifiés et ne prouvent pas à eux seuls la version réellement installée.

### Points de contrôle

- **IIS 6 et 7.x** : fonctionnalités héritées, WebDAV, TLS, paramètres ASP.NET et noms courts NTFS (8.3).
- **IIS 8.x** : configuration des handlers, validation des fichiers, anciens composants et messages d'erreur.
- **IIS 10.x** : configuration applicative, contrôle d'accès, diagnostic et dépendances .NET.

Ces points reprennent les axes proposés dans l'article. Ils ne signifient pas que toutes les installations d'une version sont vulnérables.

### Analyse des composants .NET

[dotPeek](https://www.jetbrains.com/decompiler/) permet d'examiner les assemblies .NET obtenus légitimement, notamment leurs classes et méthodes.

### ViewState et configuration

Contrôler la protection d'intégrité du ViewState, la gestion des clés, les paramètres de diagnostic, les autorisations WebDAV et les règles de filtrage dans les configurations dont on dispose. L'encodage Base64 ne constitue pas un chiffrement. Vérifier également que les décisions d'accès sont appliquées côté serveur.

[Inventaire des CVE IIS - OpenCVE](https://app.opencve.io/cve/?vendor=microsoft&product=internet_information_services)

Les procédures de contournement d'authentification, de WAF et de génération de charges de désérialisation ne sont pas reproduites.

## React2Shell - CVE-2025-55182

### Comprendre la vulnérabilité

L'article décrit une désérialisation non sécurisée des données du protocole Flight de React Server Components (RSC), susceptible de permettre une exécution de code à distance sans authentification. Le risque concerne les applications utilisant les composants serveur affectés, notamment certaines configurations Next.js avec App Router. Une détection de React ou Next.js ne démontre pas que l'application est vulnérable.

### Inventaire et validation

- Identifier les applications et dépendances RSC de son périmètre.
- Comparer les versions installées à l'avis de sécurité officiel ; la liste précise des versions n'est pas lisible dans l'export de l'article.
- Valider la correction dans un environnement de test et conserver les preuves.
- En cas d'exposition confirmée, rechercher les traces d'activité anormale et appliquer les mesures de remédiation appropriées.

### Ressources

- [Avis de sécurité React](https://github.com/facebook/react/security/advisories/GHSA-fv66-9v8q-g76r).
- [TryHackMe - React2Shell](https://tryhackme.com/room/react2shellcve202555182) : laboratoire présenté dans l'article ; conditions d'accès non vérifiées.

Les procédures de recherche de cibles à grande échelle, d'exécution de commandes, d'exfiltration et de contournement de protections ne sont pas reprises.

## FFUF avec fichier de requête

### Test LFI à partir d'une requête

```bash
ffuf -request lfi -request-proto https -w /root/wordlists/offensive\ payloads/LFI\ payload.txt -c -mr "root:"
```

Prérequis indépendant : une requête de laboratoire enregistrée dans `lfi` et la wordlist indiquée. Ces fichiers ne sont pas générés par les chapitres précédents.

### Test XSS à partir d'une requête

```bash
ffuf -request xss -request-proto https -w /root/wordlists/xss-payloads.txt -c -mr "<script>alert('XSS')</script>"
```

Prérequis indépendant : une requête de laboratoire enregistrée dans `xss` et la wordlist indiquée. Ces fichiers ne sont pas générés par les chapitres précédents.

## Techniques avancées

### Tests d'en-têtes XSS / SSRF

```bash
cat example.coms.txt | assetfinder --subs-only| httprobe | while read url; do xss1=$(curl -s -L $url -H 'X-Forwarded-For: xss.yourburpcollabrotor'|grep xss) xss2=$(curl -s -L $url -H 'X-Forwarded-Host: xss.yourburpcollabrotor'|grep xss) xss3=$(curl -s -L $url -H 'Host: xss.yourburpcollabrotor'|grep xss) xss4=$(curl -s -L $url --request-target http://burpcollaborator/ --max-time 2); echo -e "\e[1;32m$url\e[0m""\n""Method[1] X-Forwarded-For: xss+ssrf => $xss1""\n""Method[2] X-Forwarded-Host: xss+ssrf ==> $xss2""\n""Method[3] Host: xss+ssrf ==> $xss3""\n""Method[4] GET http://xss.yourburpcollabrotor HTTP/1.1 ""\n";done
```

Bloc historique combinant des requêtes et des vérifications d'en-têtes. Réservé aux environnements de test contrôlés.

> Bloc non vérifié, avec un nom Collaborator mal orthographié et des hypothèses non démontrées.

## Authentification et contrôle d'accès

### Access Control (IDOR / BOLA)

Vérifier les permissions horizontales (entre comptes de même rôle), verticales (entre rôles) et liées à l'état d'une opération. Utiliser uniquement des comptes et objets de test.

Comparer deux réponses HTTP de test enregistrées localement :

```bash
diff -u reponse-compte-a.txt reponse-compte-b.txt
```

Distinguer les différences normales liées aux comptes d'un accès réellement non autorisé.

### Authentication

Examiner la connexion, la réinitialisation du mot de passe, la MFA, la durée des sessions et la déconnexion. Vérifier la cohérence des messages d'erreur et des protections entre les différents parcours.

### JWT

Examiner le header, les claims, l'expiration et la validation de signature. Le décodage d'un JWS ne vérifie pas sa signature.

```bash
python3 - <<'PY'
import base64, json
from pathlib import Path

parts = Path("jwt-test.txt").read_text().strip().split(".")
if len(parts) != 3:
    raise SystemExit("Un JWS compact à trois segments est attendu")
for label, part in zip(("Header", "Payload"), parts[:2]):
    raw = base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))
    print(label, json.dumps(json.loads(raw), indent=2))
PY
```

Décode localement un jeton de test enregistré dans `jwt-test.txt`, sans le transmettre à un service externe.

### OAuth / OpenID Connect

Identifier le fournisseur d'identité, le client, les redirections, les paramètres state et nonce, ainsi que les permissions accordées. Examiner la correspondance entre l'identité authentifiée et la session obtenue.

### Business Logic

Cartographier les étapes d'une opération et ses règles métier : états autorisés, contrôles serveur, limites et invariants. Utiliser des transactions fictives dans un environnement prévu pour les tests.

### Race Conditions

Identifier les opérations qui modifient un état partagé, consomment un crédit ou appliquent une limite. Examiner les garanties d'atomicité et les résultats de tests contrôlés sur des objets de test.

## Contrôles côté serveur

### API Testing

Recenser les méthodes HTTP, les paramètres requis et facultatifs, les types de contenu, les autorisations et la documentation API. Voir aussi [Cartographie Web et API](./cartographie-web.md#inventaire-api).

```bash
jq -r '.paths | keys[]' openapi.json
```

Liste les chemins décrits dans une spécification OpenAPI JSON déjà récupérée légalement.

### GraphQL

Distinguer queries, mutations et subscriptions. Examiner les champs exposés et les contrôles d'accès appliqués à chaque objet.

```graphql
query myGetProductQuery {
  product(id: "123") {
    name
    description
  }
}
```

Exemple de lecture d'un produit fictif repris du cours GraphQL. Le schéma et l'identifiant doivent correspondre au lab.

### NoSQL Injection

Identifier les entrées transmises aux requêtes NoSQL et les différences de types entre chaînes, nombres et objets. Examiner la validation et les messages d'erreur sur des données fictives.

### OS Command Injection

Repérer les fonctionnalités qui appellent des programmes système. Vérifier dans un laboratoire comment les entrées sont transmises aux processus et si elles sont séparées des arguments de commande.

### File Upload

Examiner les formats autorisés, la taille maximale, le stockage, les droits d'accès et le traitement des fichiers. Préparer un fichier de test inoffensif.

```bash
printf 'bug-bounty-test\n' > upload-test.txt
file --mime-type upload-test.txt
sha256sum upload-test.txt
```

Crée un fichier texte local et identifie son type réel et son empreinte.

### XXE

Identifier les fonctionnalités qui analysent du XML, notamment les imports et les API. Vérifier en laboratoire la configuration du parseur et la désactivation des entités externes.

### SSTI

Repérer les champs intégrés dans un template serveur. Distinguer les données affichées littéralement des expressions interprétées par un moteur de templates dans un lab.

### Insecure Deserialization

Identifier les formats sérialisés présents dans les cookies et les données applicatives. Examiner les types d'objets autorisés et les contrôles d'intégrité, sans désérialiser un objet inconnu dans un environnement sensible.

## Contrôles côté client

### CSRF

Identifier les opérations qui changent un état. Examiner les tokens anti-CSRF, les cookies SameSite et les contrôles d'origine.

### Clickjacking

Examiner les protections contre l'intégration d'une page dans une iframe : X-Frame-Options et Content-Security-Policy frame-ancestors.

```bash
grep -Ei '^(x-frame-options|content-security-policy):' headers.txt
```

Recherche les protections dans des en-têtes HTTP déjà enregistrés localement.

### DOM-based vulnerabilities

Relever les sources de données contrôlables et les sinks JavaScript. Examiner le traitement des URL, fragments, messages et attributs DOM. Voir aussi [Analyse JavaScript](./cartographie-web.md#analyse-javascript).

### WebSockets

Recenser les connexions WebSocket dans Burp Suite. Examiner le handshake, l'origine, l'authentification et les permissions associées aux messages de test.

### Prototype Pollution

Examiner la fusion d'objets JavaScript, les propriétés héritées et la validation des clés. Étudier séparément les cas client et serveur dans les labs.

## HTTP, cache et IA

### HTTP Host Header

Examiner la validation du nom d'hôte, la construction des URL absolues et les dépendances aux en-têtes de proxy. Utiliser les labs dédiés pour les scénarios de réinitialisation de mot de passe.

### HTTP Request Smuggling

Comprendre les différences d'interprétation des limites de requête entre proxies et serveurs. Réserver les tests susceptibles de perturber des connexions partagées aux environnements isolés prévus à cet effet.

### Web Cache Poisoning

Identifier les caches et leur politique de clé. Examiner les variations de réponse et les en-têtes de cache sur des ressources de test isolées.

### Web Cache Deception

Vérifier que les réponses privées ne sont pas stockées dans un cache partagé. Distinguer une fuite de données mises en cache d'une modification du contenu servi par le cache.

```bash
grep -Ei '^(cache-control|vary|age|x-cache|expires|set-cookie):' headers.txt
```

Extrait les indicateurs de cache et de session d'une capture HTTP locale. Un en-tête seul ne prouve pas une vulnérabilité.

### Web LLM Attacks

Identifier les entrées de confiance, les outils accessibles au modèle, les données connectées et les autorisations des actions. Examiner les risques d'injection de prompt et d'agence excessive avec des données fictives.

## Pratique PortSwigger

- [Web Security Academy](https://portswigger.net/web-security) - cours et labs par niveau.
- Essential Skills : analyser les structures de données non standard et sélectionner les fonctionnalités à examiner.
- Les contrôles ci-dessus sont des synthèses des thèmes du dossier PortSwigger Full Lab Writeups. Les exemples shell d'analyse locale sont des compléments, non des commandes extraites des solutions.

## Avant de poursuivre

- Observations pertinentes classées par type de vulnérabilité.
- Résultats à confirmer manuellement identifiés.

---

[Précédent : Cartographie Web et API](./cartographie-web.md) · [Parcours](./index.md) · [Suivant : Validation et preuves](./validation.md)

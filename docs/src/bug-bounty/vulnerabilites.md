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
| `requests/headers.txt` | En-têtes d'une réponse HTTP de test, enregistrés manuellement |
| `requests/reponse-compte-a.txt`, `requests/reponse-compte-b.txt` | Réponses de deux comptes de test, exportées séparément |
| `requests/jwt-test.txt` | Jeton de test enregistré localement |
| `requests/openapi.json` | Spécification OpenAPI JSON obtenue légitimement |

## Subdomain Takeover

### Vérification du risque de Subdomain Takeover

```bash
subzy run --targets subexample.coms.txt --concurrency 100 --hide_fails --verify_ssl
```

Exemple historique de détection de configurations potentiellement vulnérables. Une empreinte de service ou une erreur DNS ne démontre pas qu'une ressource peut être revendiquée ; concurrence élevée dans cet exemple.

> Exemple historique indépendant : `subexample.coms.txt` doit être préparé manuellement pour ce test. Il n'est pas créé par les étapes précédentes.


## Exposition de données

### Repérage de fichiers sensibles

```bash
cat allurls.txt | grep -E "\.xls|\.xml|\.xlsx|\.json|\.pdf|\.sql|\.doc|\.docx|\.pptx|\.txt|\.zip|\.tar\.gz|\.tgz|\.bak|\.7z|\.rar|\.log|\.cache|\.secret|\.db|\.backup|\.yml|\.gz|\.config|\.csv|\.yaml|\.md|\.md5"
```

Filtre l'inventaire local `allurls.txt` selon des chaînes d'extensions. Le filtre n'est pas limité à la fin du chemin et peut produire des faux positifs ; une extension ne démontre ni l'accès ni la sensibilité du contenu.

### Recherche de documents indexés

```text
site:*.example.com (ext:doc OR ext:docx OR ext:odt OR ext:pdf OR ext:rtf OR ext:ppt OR ext:pptx OR ext:csv OR ext:xls OR ext:xlsx OR ext:txt OR ext:xml OR ext:json OR ext:zip OR ext:rar OR ext:md OR ext:log OR ext:bak OR ext:conf OR ext:sql)
```

Exemple à saisir dans un moteur de recherche, pas dans Bash. Les opérateurs et la couverture de l'index dépendent du moteur.

### Détection de dépôts Git exposés

```bash
cat example.coms.txt | grep "SUCCESS" | gf urls | httpx-toolkit -sc -server -cl -path "/.git/" -mc 200 -location -ms "Index of" -probe
```

Exemple historique indépendant : `example.coms.txt` et son format avec le marqueur SUCCESS ne sont pas produits par le parcours. La chaîne n'a pas été validée ; elle dépend aussi du pattern GF `urls` et d'HTTPX Toolkit. Un statut 200 ou un titre générique ne prouve pas l'exposition d'un dépôt.

### Filtrage étendu des extensions sensibles

```bash
echo https://example.com | gau | grep -E "\.(xls|xml|xlsx|json|pdf|sql|doc|docx|pptx|txt|zip|tar\.gz|tgz|bak|7z|rar|log|cache|secret|db|backup|yml|gz|config|csv|yaml|md|md5|tar|xz|7zip|p12|pem|key|crt|csr|sh|pl|py|java|class|jar|war|ear|sqlitedb|sqlite3|dbf|db3|accdb|mdb|sqlcipher|gitignore|env|ini|conf|properties|plist|cfg)$"
```

Variante historique GAU : recherche des suffixes littéraux dans les URL archivées. Les URL comportant une query string après l'extension peuvent être ignorées. Le résultat ne prouve pas l'exposition.

### Recherche de buckets AWS S3

```bash
s3scanner scan -d example.com
```

Exemple obsolète ou destiné à une autre version : cette syntaxe `scan -d` n'est pas documentée dans la version actuelle de [S3Scanner](https://github.com/sa7mon/S3Scanner). Ne pas exécuter tel quel. Un nom de bucket ressemblant au domaine ne prouve pas son appartenance au programme.

### Recherche de secrets dans des fichiers JavaScript

```bash
cat allurls.txt | grep -E "\.js$" | httpx-toolkit -mc 200 -content-type | grep -E "application/javascript|text/javascript" | cut -d' ' -f1 | xargs -I% curl -s % | grep -E "(API_KEY|api_key|apikey|secret|token|password)"
```

Exemple historique de collecte active qui peut afficher des secrets en clair. Ne pas utiliser tel quel. Préférer la revue locale des fichiers autorisés décrite dans [Analyse JavaScript](./cartographie-web.md#analyse-javascript), qui ne liste que les noms de fichiers.

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

Exemple historique non validé : dépend des outils et du pattern GF `xss`. La sortie de chaque outil doit correspondre au format attendu par le suivant. Une réflexion n'est pas une preuve d'exécution JavaScript.

### Analyse XSS avec Dalfox

```bash
cat xss_params.txt | dalfox pipe --blind https://your-collaborator-url --waf-bypass --silence
```

Exemple historique indépendant de la collecte précédente : `xss_params.txt` n'est pas créé par le parcours. Ne pas confondre ce fichier avec `xss_output.txt` ou `xss_candidates.txt`.

> Exemple historique non validé ; ne pas exécuter tel quel. Les options, le service de callback et le format d'entrée dépendent de la version installée.

### Recherche de candidats XSS - variante historique

```bash
cat urls.txt | grep -E "(login|signup|register|forgot|password|reset)" | httpx -silent | nuclei -t nuclei-templates/vulnerabilities/xss/ -severity critical,high
```

Variante historique indépendante : le fichier `urls.txt` correspond à la variante GAU du chapitre Web, pas à l'inventaire principal validé.

> Ce filtrage ne démontre pas qu'une XSS est persistante.

### Réflexion et XSS - variante historique

```bash
cat js_files.txt | Gxss -c 100 | sort -u | dalfox pipe -o dom_xss_results.txt
```

Exemple historique indépendant : `js_files.txt` n'est pas produit par le parcours et le format attendu n'a pas été confirmé. Ne pas confondre des URL de scripts avec des fichiers JavaScript locaux.

> Cette chaîne n'analyse pas les flux de données dans le DOM et ne démontre pas une DOM XSS.

### XSS - extraction des URL depuis un résultat local

```bash
grep -oP '^URL: \K\S+' xss_output.txt | sort -u > xss_candidates.txt
```

Extrait et déduplique les URL d'un résultat local dont les lignes commencent par `URL: `. Requiert GNU grep avec prise en charge PCRE (`-P`). Le format réel de `xss_output.txt` reste à vérifier. Contrairement à l'exemple source, conserve les valeurs des paramètres pour éviter de perdre les paramètres suivants. Une réflexion ne constitue pas une preuve de XSS.

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

Affiche l'aide détaillée de SQLmap, sans contacter de cible. SQLmap doit être installé ; cette commande n'effectue aucun test d'injection.

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

Exemple historique non validé, réservé à l'étude en laboratoire. Dépend de GAU, GF et de son pattern `lfi`, URO, qsreplace, FFUF et de la wordlist locale `payloads/lfi.txt`. La normalisation perd des paramètres et la correspondance textuelle ne démontre pas à elle seule une LFI.

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

Démarre un serveur de fichiers sur l'interface loopback IPv4, avec un fichier témoin fictif. Requiert Python 3 et un port 8080 libre ; le serveur occupe le terminal jusqu'à son arrêt. Ne pas exposer un dossier contenant des données personnelles ou des secrets.

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

Effectue une requête HEAD avec un en-tête Origin. Ce n'est pas un preflight OPTIONS et les en-têtes obtenus ne démontrent pas le comportement du navigateur.

### Analyse avec CORScanner

```bash
python3 CORScanner.py -u https://example.com -d -t 10
```

Exemple historique nécessitant une copie examinée de CORScanner.py et ses dépendances Python. Les options et la compatibilité de cette version ne sont pas confirmées.

### Détection CORS avec Nuclei

```bash
cat example.coms.txt | httpx -silent | nuclei -t nuclei-templates/vulnerabilities/cors/ -o cors_results.txt
```

Exemple historique indépendant : `example.coms.txt` n'est pas produit par le parcours. Les modèles et la chaîne n'ont pas été validés. Cet exemple ne fait pas partie du parcours principal.

### Vérification de la réflexion d'Origin

```bash
curl -H "Origin: https://evil.com" -I https://example.com/api/data | grep -i "access-control-allow-origin: https://evil.com"
```

Recherche une valeur textuelle dans les en-têtes de la réponse HEAD ; vérifier le contexte et les en-têtes complets avant toute conclusion.

> La réflexion seule ne suffit pas à démontrer une vulnérabilité exploitable.

## WordPress

### Analyse WordPress avec WPScan

```bash
wpscan --url https://example.com --disable-tls-checks --api-token YOUR_TOKEN -e at -e ap -e u --enumerate ap --plugins-detection aggressive --force
```

Exemple historique d'énumération WordPress. La répétition des options d'énumération rend l'intention ambiguë ; leur interprétation dépend de la version. La base de vulnérabilités WPScan nécessite un jeton API valide.

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

Prérequis indépendant : une requête de laboratoire enregistrée dans `lfi` (à la racine du dossier, pour cette variante historique) et la wordlist indiquée. Ces fichiers ne sont pas générés par les chapitres précédents ; les chemins absolus et le format de la requête doivent être vérifiés dans le laboratoire. Une correspondance de réponse n'est pas une preuve suffisante.

### Test XSS à partir d'une requête

```bash
ffuf -request xss -request-proto https -w /root/wordlists/xss-payloads.txt -c -mr "<script>alert('XSS')</script>"
```

Prérequis indépendant : une requête de laboratoire enregistrée dans `xss` (à la racine du dossier, pour cette variante historique) et la wordlist indiquée. Ces fichiers ne sont pas générés par les chapitres précédents ; les chemins absolus et le format de la requête doivent être vérifiés dans le laboratoire. Une correspondance de réponse n'est pas une preuve suffisante.

## Techniques avancées

### Tests d'en-têtes XSS / SSRF

```bash
cat example.coms.txt | assetfinder --subs-only| httprobe | while read url; do xss1=$(curl -s -L $url -H 'X-Forwarded-For: xss.yourburpcollabrotor'|grep xss) xss2=$(curl -s -L $url -H 'X-Forwarded-Host: xss.yourburpcollabrotor'|grep xss) xss3=$(curl -s -L $url -H 'Host: xss.yourburpcollabrotor'|grep xss) xss4=$(curl -s -L $url --request-target http://burpcollaborator/ --max-time 2); echo -e "\e[1;32m$url\e[0m""\n""Method[1] X-Forwarded-For: xss+ssrf => $xss1""\n""Method[2] X-Forwarded-Host: xss+ssrf ==> $xss2""\n""Method[3] Host: xss+ssrf ==> $xss3""\n""Method[4] GET http://xss.yourburpcollabrotor HTTP/1.1 ""\n";done
```

Bloc historique combinant des requêtes et des vérifications d'en-têtes. Réservé aux environnements de test contrôlés.

> Bloc historique non validé, à ne pas exécuter tel quel. Les fichiers et formats d'entrée ne sont pas définis et les résultats ne démontrent ni XSS ni SSRF.

## Authentification et contrôle d'accès

### Access Control (IDOR / BOLA)

Vérifier les permissions horizontales (entre comptes de même rôle), verticales (entre rôles) et liées à l'état d'une opération. Utiliser uniquement des comptes et objets de test.

Comparer deux réponses HTTP de test enregistrées localement :

```bash
diff -u requests/reponse-compte-a.txt requests/reponse-compte-b.txt
```

Compare deux fichiers de réponse locaux. `diff` renvoie 0 s'ils sont identiques, 1 s'ils diffèrent et une valeur supérieure en cas d'erreur. Une différence peut être normale ; elle ne prouve pas un défaut de contrôle d'accès.

### Authentication

Examiner la connexion, la réinitialisation du mot de passe, la MFA, la durée des sessions et la déconnexion. Vérifier la cohérence des messages d'erreur et des protections entre les différents parcours.

### JWT

Examiner le header, les claims, l'expiration et la validation de signature. Le décodage d'un JWS ne vérifie pas sa signature.

```bash
python3 - <<'PY'
import base64, json
from pathlib import Path

parts = Path("requests/jwt-test.txt").read_text().strip().split(".")
if len(parts) != 3:
    raise SystemExit("Un JWS compact à trois segments est attendu")
for label, part in zip(("Header", "Payload"), parts[:2]):
    raw = base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))
    print(label, json.dumps(json.loads(raw), indent=2))
PY
```

Décode localement les deux segments JSON d'un JWS compact de test. Requiert Python 3 ; une entrée invalide peut provoquer une erreur de décodage. Le script ne vérifie ni la signature, ni la validité des claims.

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
jq -r '.paths | keys[]' requests/openapi.json
```

Liste les clés de l'objet `paths` d'une spécification OpenAPI JSON locale. Requiert jq et un objet `paths` valide ; ne vérifie pas la disponibilité des routes.

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

Exemple de requête GraphQL pour un produit fictif, à saisir dans le client du laboratoire. Le schéma doit définir le champ `product`, son argument et les champs demandés.

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

Crée un fichier texte fictif (écrase un fichier du même nom), affiche son type MIME estimé avec `file` puis son empreinte SHA-256. Ne transfère aucun fichier.

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
grep -Ei '^(x-frame-options|content-security-policy):' requests/headers.txt
```

Extrait les en-têtes X-Frame-Options et Content-Security-Policy d'une capture locale. Vérifier notamment la directive `frame-ancestors` : la simple présence d'une CSP ne suffit pas.

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
grep -Ei '^(cache-control|vary|age|x-cache|expires|set-cookie):' requests/headers.txt
```

Extrait des indicateurs de cache et de session d'une capture HTTP locale. La sortie peut contenir des cookies : masquer leur valeur avant partage. Aucun en-tête seul ne prouve une vulnérabilité.

### Web LLM Attacks

Identifier les entrées de confiance, les outils accessibles au modèle, les données connectées et les autorisations des actions. Examiner les risques d'injection de prompt et d'agence excessive avec des données fictives.

## Pratique PortSwigger

- [Web Security Academy](https://portswigger.net/web-security) - cours et labs par niveau.
- Essential Skills : analyser les structures de données non standard et sélectionner les fonctionnalités à examiner.
- Les contrôles ci-dessus sont des synthèses des thèmes du dossier PortSwigger Full Lab Writeups. Les exemples shell d'analyse locale sont des compléments, non des commandes extraites des solutions.

## Avant de poursuivre

<BountyChecklist storage-key="checkpoint-vulnerabilites" :items='["Observations pertinentes classées par type de vulnérabilité.","Résultats à confirmer manuellement identifiés."]' />

---

[Précédent : Cartographie Web et API](./cartographie-web.md) · [Parcours](./index.md) · [Suivant : Validation et preuves](./validation.md)

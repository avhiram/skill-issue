---
title: Outils et ressources Bug Bounty
aside: true
prev: false
next: false
---

# Outils et ressources

Catalogue issu de la [capture Lostsec du 28 août 2025](https://web.archive.org/web/20250828093634/https://lostsec.xyz/). Les liens proviennent de l'archive ; leur disponibilité actuelle et la maintenance des projets ne sont pas garanties. Les extensions doivent être évaluées avant installation, notamment leurs permissions.

## Security Tools

### Reconnaissance et collecte

- **[Subfinder](https://github.com/projectdiscovery/subfinder)** - Collecte de sous-domaines.
- **[Amass](https://github.com/OWASP/Amass)** - Cartographie DNS et OSINT.
- **[Assetfinder](https://github.com/tomnomnom/assetfinder)** - Découverte de domaines associés.
- **[GAU](https://github.com/lc/gau)** - Collecte d'URL archivées.
- **[URLfinder](https://github.com/projectdiscovery/urlfinder)** - Découverte passive d'URL.
- **[Waybackurls](https://github.com/tomnomnom/waybackurls)** - Collecte d'URL depuis la Wayback Machine.
- **[Katana](https://github.com/projectdiscovery/katana)** - Crawling Web.
- **[Hakrawler](https://github.com/hakluke/hakrawler)** - Exploration d'endpoints Web.
- **[HTTPX](https://github.com/projectdiscovery/httpx)** - Inventaire des services HTTP.
- **[Masscan](https://github.com/robertdavidgraham/masscan)** - Scanner de ports TCP.
- **[LinkFinder](https://github.com/GerbenJavado/LinkFinder)** - Identification de références et endpoints JavaScript.
- **[GF](https://github.com/tomnomnom/gf)** - Filtres grep réutilisables.
- **[Go-Dork](https://github.com/dwisiswant0/go-dork)** - Recherche par opérateurs de moteur de recherche.

### Analyse Web et paramètres

- **[FFUF](https://github.com/ffuf/ffuf)** - Fuzzing Web en laboratoire.
- **[x8](https://github.com/Sh1Yo/x8)** - Découverte de paramètres HTTP.
- **[Gxss](https://github.com/KathanP19/Gxss)** - Repérage de paramètres réfléchis.
- **[KXSS](https://github.com/Emoe/kxss)** - Analyse de réflexion des paramètres.
- **[Recx](https://github.com/1hehaq/recx)** - Analyse de paramètres réfléchis.

### Audit et tests en laboratoire

- **[Nuclei](https://github.com/projectdiscovery/nuclei)** - Scanner à modèles.
- **[WPScan](https://github.com/wpscanteam/wpscan)** - Audit WordPress.
- **[S3Scanner](https://github.com/sa7mon/S3Scanner)** - Audit de configuration S3.
- **[LOXS](https://github.com/coffinxp/loxs)** - Scanner de vulnérabilités Web.
- **[OTY](https://github.com/1hehaq/oty)** - Automatisation de workflows avec YAML.
- **[SQLmap](https://github.com/sqlmapproject/sqlmap)** - Évaluation des injections SQL en laboratoire.
- **[CustomBsqli](https://github.com/coffinxp/customBsqli)** - Tests d'injection SQL aveugle en laboratoire.
- **[Ghauri](https://github.com/r0oth3x49/ghauri)** - Évaluation des injections SQL.
- **[SSRFmap](https://github.com/swisskyrepo/SSRFmap)** - Tests SSRF en environnement autorisé.
- **[Commix](https://github.com/commixproject/commix)** - Évaluation des injections de commandes en laboratoire.
- **[DotDotPwn](https://github.com/wireghoul/dotdotpwn)** - Tests de traversée de répertoires.
- **[LFISuite](https://github.com/D35m0nd142/LFISuite)** - Outil historique de tests LFI en laboratoire.
- **[SSTImap](https://github.com/vladko312/SSTImap)** - Tests d'injection dans les moteurs de templates.

## Browser Extensions

Extensions classées par usage. Les liens Chrome proviennent du document [Best Browser Extensions for Bug Hunting and Cybersecurity](https://infosecwriteups.com/best-browser-extensions-for-bug-hunting-and-cybersecurity-77faf6bd8188), mis à jour le 23 avril 2026. Les liens Firefox et GitHub sont conservés. La disponibilité, la compatibilité et l'identité des éditeurs n'ont pas été vérifiées individuellement. Examiner les permissions et utiliser un profil de navigateur dédié aux tests ; éviter d'accorder l'accès à des sessions ou à des données sensibles. Les extensions similaires mais distinctes restent séparées.

### Reconnaissance et OSINT

- **Wappalyzer** - Identification des technologies Web. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/wappalyzer/) · [Chrome](https://chromewebstore.google.com/detail/wappalyzer-technology-pro/gppongmhjkpfnbhagpmjfkannfbllamg)
- **Hunter.io** - Recherche d'adresses e-mail professionnelles. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/hunterio/) · [Chrome](https://chromewebstore.google.com/detail/hunter-email-finder-exten/hgmhmanijnjhaffoampdlllchpolkdnj)
- **Link Gopher** - Extraction des liens. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/link-gopher/) · [Chrome](https://chromewebstore.google.com/detail/link-gopher/bpjdkodgnbfalgghnbeggfbfjpcfamkf)
- **WaybackURLs** - Consultation des URL archivées. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/waybackurl/)
- **Shodan** - Informations publiques sur les services Internet. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/shodan-addon/) · [Chrome](https://chromewebstore.google.com/detail/shodan/jjalcfnidlmpjhdfepjhjbhnhkbgleap)
- **EXIF Viewer Pro** - Lecture des métadonnées EXIF des images. [Chrome](https://chromewebstore.google.com/detail/exif-viewer-pro/mmbhfeiddhndihdjeganjggkmjapkffm)
- **Wayback Machine** - Extension de l'Internet Archive pour consulter les versions archivées. [Chrome](https://chromewebstore.google.com/detail/wayback-machine/fpnmgdkabkmnadcjpehmlllkndpkmiak)
- **YesWeHack VDP Finder** - Identifie les programmes de divulgation de vulnérabilités associés aux sites visités. [Chrome](https://chromewebstore.google.com/detail/yeswehack-vdp-finder/jnknjejacdkpnaacfgolbmdohkhpphjb)
- **Mitaka** - Recherche d'indicateurs IP, domaines, URL et hashes dans des services de renseignement. [Chrome](https://chromewebstore.google.com/detail/mitaka/bfjbejmeoibbdpfdbmbacmefcbannnbg)
- **Vortimo** - Organisation des observations OSINT et captures de pages. [Chrome](https://chromewebstore.google.com/detail/vortimo-osint-tool/mnakbpdnkedaegeiaoakkjafhoidklnf)
- **IP Address and Domain Information** - Consultation des informations IP, ASN, WHOIS et hébergement. [Chrome](https://chromewebstore.google.com/detail/ip-address-and-domain-inf/lhgkegeccnckoiliokondpaaalbhafoa)

### Analyse Web

- **TruffleHog** - Détection de secrets potentiellement exposés. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/trufflehog/) · [Chrome](https://chromewebstore.google.com/detail/trufflehog/bafhdnhjnlcdbjcdcnafhdcphhnfnhjc)
- **FindSomething** - Inspection des références et paramètres. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/findsomething/) · [Chrome](https://chromewebstore.google.com/detail/findsomething/kfhniponecokdefffkpagipffdefeldb)
- **DotGit** - Détection de dépôts Git exposés. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/dotgit/) · [Chrome](https://chromewebstore.google.com/detail/dotgit/pampamgoihgcedonnphgehgondkhikel)
- **Retire.js** - Détection de bibliothèques JavaScript vulnérables. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/retire-js/)
- **EndPointer** - Extraction et organisation des endpoints. [Chrome](https://chromewebstore.google.com/detail/endpointer/ppliilneafplhagjhhphcjmjdmbjagcp)
- **S3BucketList** - Repère les références à des buckets Amazon S3 dans les requêtes du navigateur. [Chrome](https://chromewebstore.google.com/detail/s3bucketlist/anngjobjhcbancaaogmlcffohpmcniki)
- **JSON Formatter** - Mise en forme des réponses JSON. [Chrome](https://chromewebstore.google.com/detail/json-formatter/bcjindcccaagfpajjjmafapmmgkkhgoa)
- **Code Formatter** - Mise en forme de JSON, CSS et JavaScript. [Chrome](https://chromewebstore.google.com/detail/code-formatter-json-css-j/bhimnoepicmcjfkbmhckamllnibadfal)

### Tests manuels et HTTP

- **Greb** - Inspection de paramètres et formulaires. [GitHub](https://github.com/1hehaq/greb.git)
- **FoxyProxy** - Gestion des proxys. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/foxyproxy-standard/) · [Chrome](https://chromewebstore.google.com/detail/foxyproxy/gcknhkkoolaabfmlnjonogaaifnjlfnp)
- **HackTools** - Aide-mémoire de tests Web. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/hacktools/) · [Chrome](https://chromewebstore.google.com/detail/hack-tools/cmbndhnoonmghfofefkcccljbkdpamhi)
- **Cookie Editor** - Inspection et gestion des cookies. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/edit-cookie/)
- **User-Agent Switcher** - Modification du User-Agent pour tests de compatibilité. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/uaswitcher/) · [Chrome](https://chromewebstore.google.com/detail/user-agent-switcher-and-m/bhchdcejhohfmigjafbampogmaanbfkg)
- **EditThisCookie** - Inspection et gestion des cookies ; vérifier la provenance et les permissions avant installation. [Chrome](https://chromewebstore.google.com/detail/editthiscookie-v3/ojfebgpkimhlhcblbalbfjblapadhbol)
- **d3coder** - Encodage, décodage et conversions de formats. [Chrome](https://chromewebstore.google.com/detail/d3coder/gncnbkghencmkfgeepfaonmegemakcol)
- **Toggle JavaScript** - Active ou désactive JavaScript pour comparer le comportement d'une page. [Chrome](https://chromewebstore.google.com/detail/toggle-javascript/cidlcjdalomndpeagkjpnefhljffbnlo)
- **HackBar** - Manipulation manuelle des paramètres et encodage dans un laboratoire. [Chrome](https://chromewebstore.google.com/detail/hackbar/ginpbkfigcoaokgflihfhhmglmbchinc)
- **Fake Filler** - Remplit des formulaires de test avec des données fictives. [Chrome](https://chromewebstore.google.com/detail/fake-filler/bnjjngeaknajbdcgpfkgnonkmififhfo)

### Confort et productivité

- **Temp Mail** - Adresses e-mail temporaires. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/temp-mail/) · [Chrome](https://chromewebstore.google.com/detail/temp-mail-disposable-temp/inojafojbhdpnehkhhfjalgjjobnhomj)
- **WebRTC Disable** - Gestion de WebRTC. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/happy-bonobo-disable-webrtc/)
- **Open Multiple URLs** - Ouverture de plusieurs URL. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/open-multiple-urls/) · [Chrome](https://chromewebstore.google.com/detail/open-multiple-urls/oifijhaokejakekmnjmphonojcfkpbbh)
- **uBlock Origin** - Blocage des publicités et traceurs. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/) · [Chrome](https://chromewebstore.google.com/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm)
- **Dark Reader** - Thème sombre. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/darkreader/) · [Chrome](https://chromewebstore.google.com/detail/dark-reader/eimadpbcbfnmbkopoojfekhnkhdbieeh)
- **Page Translator** - Traduction de pages. [Firefox](https://addons.mozilla.org/en-US/firefox/addon/traduzir-paginas-web/)
- **WebRTC Protect** - Configuration du routage WebRTC pour limiter certaines fuites d'adresse IP. [Chrome](https://chromewebstore.google.com/detail/webrtc-protect-protect-ip/bkmmlbllpjdpgcgdohbaghfaecnddhni)
- **Google Translate** - Traduction de pages Web. [Chrome](https://chromewebstore.google.com/detail/google-translate/aapbdbdomjkkjkaonfhkkikfgjllcleb)
- **SponsorBlock** - Ignore les segments sponsorisés dans les vidéos de formation. [Chrome](https://chromewebstore.google.com/detail/sponsorblock-for-youtube/mnjggcdmjocbbbhaepdhchncahnbgone)

## Writeups

Références historiques de l'archive pour la veille et l'analyse en environnement autorisé. Les articles n'ont pas été validés individuellement ; certaines pages peuvent être payantes ou indisponibles.

- **[WAF Bypass Using SQLMap, Proxychains & Tamper Scripts](https://infosecwriteups.com/waf-bypass-masterclass-using-sqlmap-with-proxychains-and-tamper-scripts-against-cloudflare-9d46b36bae94)**
- **[Next.js - CVE-2025-29927](https://infosecwriteups.com/how-hackers-exploit-cve-2025-29927-in-next-js-like-a-pro-9997f48ed7ce)**
- **[XML-RPC - risques de brute force et DDoS](https://infosecwriteups.com/how-hackers-abuse-xml-rpc-to-launch-bruteforce-and-ddos-attacks-40be5b310960)**
- **[Configuration WSL et Burp Suite](https://infosecwriteups.com/how-to-route-traffic-from-wsl-to-burp-suite-on-windows-a-step-by-step-guide-38d58f65b21a)**
- **[Open Redirect](https://infosecwriteups.com/from-zero-to-hero-hunting-high-paying-open-redirect-bugs-in-web-apps-fdb80286236e)**
- **[LostFuzzer - URL Fuzzing et Nuclei DAST](https://infosecwriteups.com/lostfuzzer-passive-url-fuzzing-nuclei-dast-for-bug-hunters-a33501b9563b)**
- **[S3 Bucket Recon](https://infosecwriteups.com/s3-bucket-recon-finding-exposed-aws-buckets-like-a-pro-106be5ab9e1d)**
- **[Extensions navigateur Bug Bounty](https://infosecwriteups.com/best-browser-extensions-for-bug-hunting-and-cybersecurity-77faf6bd8188)**
- **[FFUF Mastery](https://osintteam.blog/ffuf-mastery-the-ultimate-web-fuzzing-guide-f7755c396b92)**
- **[Collection de templates Nuclei](https://medium.com/meetcyber/my-private-nuclei-template-collection-for-easy-bounties-ba704073d065)**
- **[Wayback Machine pour le Bug Bounty](https://infosecwriteups.com/unlock-the-full-potential-of-the-wayback-machine-for-bug-bounty-8b6f57e2637d)**
- **[SQL Injection - retour d'expérience](https://infosecwriteups.com/sql-injection-in-largest-electricity-board-of-sri-lanka-1a55c12104bd)**
- **[PDF.js - CVE-2024-4367](https://infosecwriteups.com/pdf-js-arbitrary-javascript-code-execution-cve-2024-4367-be4a64f877df)**
- **[Origin IP et WAF](https://infosecwriteups.com/how-to-find-origin-ip-of-any-website-behind-a-waf-c85095156ef7)**
- **[Recherche XSS](https://osintteam.blog/find-xss-vulnerabilities-in-just-2-minutes-d14b63d000b1)**
- **[JSRecon - données sensibles dans JavaScript](https://osintteam.blog/how-to-identify-sensitive-data-in-javascript-files-jsrecon-306b8a2e6462)**

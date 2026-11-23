// Une seule progression de zéro au projet final. Tous les liens importés ont un niveau unique.
// Ajouter des ressources dans les deux catalogues existants reste possible ; les nouveaux liens non classés
// apparaîtront au niveau Veille en attendant leur classement éditorial.
export const academyLevels = [
  {
    "id": "environment",
    "title": "Prendre en main son environnement",
    "phase": "Fondamentaux",
    "intro": "Partir de zéro : ordinateur, fichiers, outils et machines virtuelles.",
    "learn": [
      "Comprendre matériel, système d'exploitation et fichiers.",
      "Installer un éditeur, un terminal et une VM isolée."
    ],
    "exercise": "Créer un dossier de travail, installer VirtualBox et documenter une première VM.",
    "ready": "Tu sais organiser tes fichiers, accéder au terminal et expliquer une VM.",
    "featured": [
      "https://cs50.harvard.edu/x/",
      "https://www.virtualbox.org/"
    ]
  },
  {
    "id": "network-basics",
    "title": "Réseau : IP, DNS et sous-réseaux",
    "phase": "Fondamentaux",
    "intro": "Comprendre comment les machines communiquent avant de les analyser.",
    "learn": [
      "IP, masque, routeur, DNS, NAT et ports.",
      "Différences entre TCP, UDP, HTTP et HTTPS."
    ],
    "exercise": "Dessiner ton réseau local et calculer deux sous-réseaux fictifs.",
    "ready": "Tu peux expliquer une résolution DNS et une connexion TCP.",
    "featured": [
      "https://www.practicalnetworking.net/"
    ]
  },
  {
    "id": "network-practice",
    "title": "Réseau : captures et protocoles",
    "phase": "Fondamentaux",
    "intro": "Observer les communications dans une capture, pas seulement en théorie.",
    "learn": [
      "Lire des PCAP avec Wireshark et tcpdump.",
      "Reconnaître DNS, TCP, TLS et les échanges réseau."
    ],
    "exercise": "Ouvrir un PCAP public, retrouver une requête DNS et suivre un flux TCP.",
    "ready": "Tu identifies les adresses, ports et protocoles d'un échange.",
    "featured": [
      "https://wiki.wireshark.org/SampleCaptures",
      "https://www.wireshark.org/"
    ]
  },
  {
    "id": "linux-basics",
    "title": "Linux : commandes essentielles",
    "phase": "Fondamentaux",
    "intro": "Se repérer et travailler efficacement dans un terminal Linux.",
    "learn": [
      "pwd, ls, cd, cat, grep, find et redirections.",
      "Fichiers, arborescence et aide des commandes."
    ],
    "exercise": "Résoudre Bandit 0 à 10 sur OverTheWire.",
    "ready": "Tu navigues et retrouves un fichier sans tutoriel.",
    "featured": [
      "https://overthewire.org/wargames/bandit/",
      "https://linuxjourney.com/"
    ]
  },
  {
    "id": "linux-admin",
    "title": "Linux : utilisateurs et administration",
    "phase": "Fondamentaux",
    "intro": "Comprendre les permissions, services et communications entre machines.",
    "learn": [
      "Permissions, sudo, utilisateurs, groupes, processus.",
      "SSH, services, journaux et Bash."
    ],
    "exercise": "Configurer deux comptes et une connexion SSH entre deux VM isolées.",
    "ready": "Tu sais administrer un système Linux de lab.",
    "featured": [
      "https://pwn.college/linux-luminarium/"
    ]
  },
  {
    "id": "windows-basics",
    "title": "Windows : système et commandes",
    "phase": "Fondamentaux",
    "intro": "Prendre les mêmes repères sur Windows.",
    "learn": [
      "CMD, fichiers, processus et services.",
      "Comptes locaux, groupes, permissions et journaux."
    ],
    "exercise": "Lister comptes, processus et services d'une VM Windows.",
    "ready": "Tu retrouves les principaux éléments système sans interface graphique.",
    "featured": [
      "https://learn.microsoft.com/fr-fr/windows-server/administration/windows-commands/windows-commands"
    ]
  },
  {
    "id": "powershell",
    "title": "Windows : PowerShell et sécurité",
    "phase": "Fondamentaux",
    "intro": "Automatiser les tâches simples et lire les traces Windows.",
    "learn": [
      "Pipeline, cmdlets, scripts et droits.",
      "Event Viewer, Sysinternals et Sysmon."
    ],
    "exercise": "Créer un script d'inventaire de ta VM Windows.",
    "ready": "Tu sais exécuter un script simple et interpréter un événement.",
    "featured": [
      "https://learn.microsoft.com/en-us/powershell/",
      "https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon"
    ]
  },
  {
    "id": "python-basics",
    "title": "Python : bases et automatisation",
    "phase": "Développement",
    "intro": "Apprendre à écrire du code utile au quotidien.",
    "learn": [
      "Variables, conditions, boucles et fonctions.",
      "Fichiers, chaînes et exceptions."
    ],
    "exercise": "Écrire un script qui extrait les adresses IP d'un fichier de test.",
    "ready": "Tu sais modifier, exécuter et corriger ton script.",
    "featured": [
      "https://cs50.harvard.edu/python/",
      "https://automatetheboringstuff.com/"
    ]
  },
  {
    "id": "scripting",
    "title": "Bash, JavaScript et Git",
    "phase": "Développement",
    "intro": "Passer des commandes isolées à de petits projets reproductibles.",
    "learn": [
      "Shell, Git, dépendances et gestion de versions.",
      "Bases de JavaScript et automatisation."
    ],
    "exercise": "Créer un mini-répertoire Git contenant deux scripts documentés.",
    "ready": "Tu sais sauvegarder et relire un projet simple.",
    "featured": [
      "https://skills.github.com/",
      "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/"
    ]
  },
  {
    "id": "web-basics",
    "title": "Web : HTML, HTTP et navigateur",
    "phase": "Développement",
    "intro": "Comprendre ce qui se passe lorsqu'une page se charge.",
    "learn": [
      "HTML, CSS, DOM, URL et formulaires.",
      "Requêtes, réponses, en-têtes, cookies et sessions."
    ],
    "exercise": "Observer les requêtes de ton navigateur puis résoudre Natas 0 à 4.",
    "ready": "Tu distingues clairement requête, réponse et session.",
    "featured": [
      "https://developer.mozilla.org/fr/docs/Learn_web_development",
      "https://overthewire.org/wargames/natas/"
    ]
  },
  {
    "id": "web-api",
    "title": "Web : applications et API",
    "phase": "Développement",
    "intro": "Comprendre l'architecture des services que tu analyseras.",
    "learn": [
      "REST, JSON, authentification et API.",
      "SQL, bases de données, erreurs et journalisation."
    ],
    "exercise": "Créer une API locale minimale puis l'interroger.",
    "ready": "Tu expliques un appel API et la circulation de ses données.",
    "featured": [
      "https://owasp.org/www-project-api-security/"
    ]
  },
  {
    "id": "security-basics",
    "title": "Sécurité : principes et risques",
    "phase": "Sécurité",
    "intro": "Construire une méthode et un vocabulaire précis.",
    "learn": [
      "Confidentialité, intégrité, disponibilité et risque.",
      "Vulnérabilités, authentification et moindre privilège."
    ],
    "exercise": "Décrire trois risques d'une application fictive et proposer une correction.",
    "ready": "Tu sais expliquer cause, impact et mesure de protection.",
    "featured": [
      "https://www.nist.gov/cyberframework",
      "https://attack.mitre.org/"
    ]
  },
  {
    "id": "crypto",
    "title": "Cryptographie, hash et encodage",
    "phase": "Sécurité",
    "intro": "Différencier les mécanismes souvent confondus.",
    "learn": [
      "Encodage, hachage, chiffrement symétrique et asymétrique.",
      "TLS, certificats, mots de passe et bonnes pratiques."
    ],
    "exercise": "Résoudre trois exercices introductifs CryptoHack.",
    "ready": "Tu sais choisir et expliquer un mécanisme adapté.",
    "featured": [
      "https://cryptohack.org/",
      "https://gchq.github.io/CyberChef/"
    ]
  },
  {
    "id": "osint-recon",
    "title": "OSINT et reconnaissance",
    "phase": "Sécurité",
    "intro": "Apprendre à rechercher puis vérifier des informations publiques.",
    "learn": [
      "Sources ouvertes, recoupement et documentation.",
      "Domaines, sous-domaines et exposition publique."
    ],
    "exercise": "Réaliser une fiche OSINT sur un domaine de démonstration autorisé.",
    "ready": "Tu documentes des faits sans confondre hypothèse et preuve.",
    "featured": [
      "https://osintframework.com/"
    ]
  },
  {
    "id": "scanning",
    "title": "Nmap et diagnostic technique",
    "phase": "Pentest",
    "intro": "Passer de la théorie réseau à une reconnaissance maîtrisée.",
    "learn": [
      "Services, versions, ports et bannières.",
      "Wireshark, Nmap, Curl et diagnostic."
    ],
    "exercise": "Scanner deux VM de lab et expliquer chaque port relevé.",
    "ready": "Tu sais distinguer découverte et interprétation.",
    "featured": [
      "https://nmap.org/"
    ]
  },
  {
    "id": "web-security",
    "title": "Web Security : vulnérabilités",
    "phase": "Pentest",
    "intro": "Découvrir les failles Web avec un cadre de test clair.",
    "learn": [
      "OWASP Top 10, injections, contrôle d'accès et XSS.",
      "Interception et analyse de requêtes dans un lab."
    ],
    "exercise": "Résoudre une première série de labs PortSwigger.",
    "ready": "Tu expliques pour chaque faille son principe et sa correction.",
    "featured": [
      "https://portswigger.net/web-security/",
      "https://owasp.org/www-project-top-ten/"
    ]
  },
  {
    "id": "web-labs",
    "title": "Web Security : labs et API",
    "phase": "Pentest",
    "intro": "Mettre en pratique sur des applications volontairement vulnérables.",
    "learn": [
      "DVWA, Juice Shop, WebGoat et crAPI.",
      "Vérification, documentation et remédiation."
    ],
    "exercise": "Installer Juice Shop en local et terminer cinq défis.",
    "ready": "Tu documentes des observations reproductibles sur ton lab.",
    "featured": [
      "https://github.com/juice-shop/juice-shop",
      "https://github.com/OWASP/crAPI"
    ]
  },
  {
    "id": "ctf-beginner",
    "title": "CTF : premiers challenges",
    "phase": "Pentest",
    "intro": "Commencer par des exercices guidés, sans perdre le fil.",
    "learn": [
      "Lire un énoncé, choisir un outil, noter les étapes.",
      "Challenges réseau, Linux, Web et cryptographie."
    ],
    "exercise": "Terminer trois défis faciles sur Root-Me ou picoCTF.",
    "ready": "Tu peux expliquer la résolution sans copier un write-up.",
    "featured": [
      "https://www.root-me.org/",
      "https://picoctf.org/"
    ]
  },
  {
    "id": "ctf-intermediate",
    "title": "CTF : machines et scénarios",
    "phase": "Pentest",
    "intro": "Assembler plusieurs compétences dans un exercice complet.",
    "learn": [
      "Énumération, hypothèses et validation.",
      "Compte rendu et retour sur les erreurs."
    ],
    "exercise": "Terminer deux machines guidées TryHackMe ou VulnHub.",
    "ready": "Tu peux reproduire ton cheminement.",
    "featured": [
      "https://tryhackme.com/free-rooms",
      "https://www.vulnhub.com/"
    ]
  },
  {
    "id": "pentest-system",
    "title": "Pentest Linux et Windows",
    "phase": "Pentest",
    "intro": "Comprendre les erreurs de configuration dans un lab.",
    "learn": [
      "Services exposés, permissions et comptes.",
      "Énumération et correction des faiblesses système."
    ],
    "exercise": "Analyser une VM volontairement vulnérable et produire un rapport.",
    "ready": "Tu présentes les constats, preuves et mesures correctives.",
    "featured": [
      "https://book.hacktricks.wiki/",
      "https://github.com/rapid7/metasploitable3"
    ]
  },
  {
    "id": "ad-intro",
    "title": "Active Directory : DNS et Kerberos",
    "phase": "Active Directory",
    "intro": "Comprendre le fonctionnement d'un domaine Windows.",
    "learn": [
      "Domaines, contrôleurs, OU, groupes et GPO.",
      "DNS, LDAP, Kerberos et authentification."
    ],
    "exercise": "Dessiner une architecture AD simple et expliquer ses flux.",
    "ready": "Tu sais identifier les rôles principaux d'un domaine.",
    "featured": [
      "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview"
    ]
  },
  {
    "id": "ad-minilab",
    "title": "GOAD : MINILAB",
    "phase": "Active Directory",
    "intro": "Première mise en pratique Active Directory dans un petit environnement.",
    "learn": [
      "Déployer et isoler les machines.",
      "Observer comptes, groupes et services AD."
    ],
    "exercise": "Installer MINILAB et réaliser l'inventaire du domaine.",
    "ready": "Tu sais retrouver les composants et conserver les traces.",
    "featured": [
      "https://orange-cyberdefense.github.io/GOAD/labs/MINILAB/"
    ]
  },
  {
    "id": "ad-light",
    "title": "GOAD : Light",
    "phase": "Active Directory",
    "intro": "Passer à un environnement plus complet sans changer de méthode.",
    "learn": [
      "Analyse des relations et configurations AD.",
      "Énumération, hypothèses et documentation."
    ],
    "exercise": "Déployer GOAD-Light puis comparer sa topologie à MINILAB.",
    "ready": "Tu comprends ce qui change entre les deux labs.",
    "featured": [
      "https://orange-cyberdefense.github.io/GOAD/labs/GOAD-Light/"
    ]
  },
  {
    "id": "ad-full",
    "title": "GOAD : complet",
    "phase": "Active Directory",
    "intro": "Approfondir plusieurs domaines et relations dans un lab isolé.",
    "learn": [
      "Trusts, Kerberos et chemins de privilèges.",
      "Méthodologie de test et rédaction AD."
    ],
    "exercise": "Documenter la topologie, les rôles et constats de GOAD.",
    "ready": "Tu peux présenter une analyse structurée d'un domaine complexe.",
    "featured": [
      "https://github.com/Orange-Cyberdefense/GOAD"
    ]
  },
  {
    "id": "c2",
    "title": "Command & Control : Cobalt Strike et C2 open source",
    "phase": "Red Team",
    "intro": "Comprendre le rôle d'un C2 et apprendre à l'observer dans un lab autorisé.",
    "learn": [
      "Architecture C2, agent, serveur, flux et télémétrie.",
      "Documentation Cobalt Strike, Sliver, Mythic et CALDERA."
    ],
    "exercise": "Créer un lab virtuel sans exposition Internet, suivre un atelier Sliver ou CALDERA sur VM de test, puis observer et journaliser les flux.",
    "ready": "Tu expliques l'architecture C2 et sais documenter son trafic.",
    "featured": [
      "https://www.cobaltstrike.com/support/user-manuals",
      "https://github.com/BishopFox/sliver",
      "https://github.com/apache/caldera",
      "https://github.com/its-a-feature/Mythic"
    ]
  },
  {
    "id": "red-advanced",
    "title": "Red Team : simulation et méthodologie",
    "phase": "Red Team",
    "intro": "Préparer un scénario de simulation et l'évaluer avec la défense.",
    "learn": [
      "Cartographier des comportements sur MITRE ATT&CK.",
      "Définir des objectifs, règles d'engagement et preuves."
    ],
    "exercise": "Préparer un scénario ATT&CK fictif, puis relever les détections dans ton lab.",
    "ready": "Tu sais décrire un exercice reproductible et son périmètre.",
    "featured": [
      "https://attack.mitre.org/",
      "https://github.com/redcanaryco/atomic-red-team"
    ]
  },
  {
    "id": "blue-logs",
    "title": "Blue Team : logs et événements",
    "phase": "Défense",
    "intro": "Savoir où regarder lorsqu'une activité doit être expliquée.",
    "learn": [
      "Logs Windows, Linux, réseau et horodatages.",
      "Collecte, normalisation et indicateurs."
    ],
    "exercise": "Comparer des journaux Windows et Linux sur un scénario de test.",
    "ready": "Tu retrouves la chronologie d'une activité locale.",
    "featured": [
      "https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon"
    ]
  },
  {
    "id": "blue-siem",
    "title": "Blue Team : SIEM, règles et alertes",
    "phase": "Défense",
    "intro": "Passer des traces aux alertes utiles.",
    "learn": [
      "SIEM, requêtes, corrélation, Sigma et YARA.",
      "IDS, EDR et validation des alertes."
    ],
    "exercise": "Installer ou utiliser un lab Wazuh, puis analyser trois alertes d'exemple.",
    "ready": "Tu sais expliquer pourquoi une alerte a été déclenchée.",
    "featured": [
      "https://wazuh.com/",
      "https://github.com/SigmaHQ/sigma"
    ]
  },
  {
    "id": "blue-threat",
    "title": "Blue Team : Threat Hunting et réponse",
    "phase": "Défense",
    "intro": "Approfondir la détection et l'analyse des comportements.",
    "learn": [
      "MITRE ATT&CK, threat intelligence et IoC.",
      "Investigation, escalade et mesures de réponse."
    ],
    "exercise": "Faire un challenge CyberDefenders et produire une chronologie.",
    "ready": "Tu sais distinguer indicateurs, hypothèses et constats.",
    "featured": [
      "https://cyberdefenders.org/blue-team-labs/"
    ]
  },
  {
    "id": "dfir-network",
    "title": "DFIR : réseau et chronologie",
    "phase": "Investigation",
    "intro": "Reconstituer une activité à partir des données réseau.",
    "learn": [
      "PCAP, DNS, HTTP et chronologie.",
      "Préservation des données et chaîne de preuve."
    ],
    "exercise": "Analyser un PCAP de lab et rédiger une chronologie.",
    "ready": "Tu peux relier les événements sans supposer les faits.",
    "featured": [
      "https://wiki.wireshark.org/SampleCaptures"
    ]
  },
  {
    "id": "dfir-host",
    "title": "DFIR : mémoire et disques",
    "phase": "Investigation",
    "intro": "Étudier les artefacts d'un poste ou d'une VM.",
    "learn": [
      "Artefacts Windows, images disque et mémoire.",
      "Autopsy, Volatility et rapport d'analyse."
    ],
    "exercise": "Résoudre un challenge forensic fourni avec une image de test.",
    "ready": "Tu justifies tes conclusions avec des artefacts précis.",
    "featured": [
      "https://github.com/volatilityfoundation/volatility3"
    ]
  },
  {
    "id": "reverse",
    "title": "Reverse Engineering : fondamentaux",
    "phase": "Recherche technique",
    "intro": "Lire le fonctionnement d'un programme dans un environnement de test.",
    "learn": [
      "Assembleur, exécutables, strings et débogage.",
      "Analyse statique avec Ghidra."
    ],
    "exercise": "Analyser un petit binaire pédagogique et en documenter les fonctions.",
    "ready": "Tu identifies les grands blocs d'un programme.",
    "featured": [
      "https://ghidra-sre.org/"
    ]
  },
  {
    "id": "malware",
    "title": "Malware Analysis : environnement et détection",
    "phase": "Recherche technique",
    "intro": "Observer des programmes de test dans un environnement confiné.",
    "learn": [
      "Analyse statique et dynamique en bac à sable.",
      "Artefacts, comportements et rapport."
    ],
    "exercise": "Analyser un exemple éducatif non dangereux et relever ses artefacts.",
    "ready": "Tu sais expliquer un comportement observé sans exposer une machine réelle.",
    "featured": [
      "https://remnux.org/",
      "https://www.malware-traffic-analysis.net/"
    ]
  },
  {
    "id": "cloud-foundations",
    "title": "Cloud : AWS, Azure et IAM",
    "phase": "Cloud et infrastructures",
    "intro": "Comprendre les identités, services et responsabilités.",
    "learn": [
      "IAM, rôles, stockage et réseaux cloud.",
      "Modèle de responsabilité partagée."
    ],
    "exercise": "Dessiner une architecture cloud minimale avec IAM et réseau.",
    "ready": "Tu sais expliquer les principaux composants.",
    "featured": [
      "https://learn.microsoft.com/en-us/training/azure/"
    ]
  },
  {
    "id": "cloud-security",
    "title": "Cloud Security : erreurs de configuration",
    "phase": "Cloud et infrastructures",
    "intro": "Identifier les risques cloud dans des environnements pédagogiques.",
    "learn": [
      "Identités trop permissives et secrets exposés.",
      "Contrôles, journalisation et configuration sécurisée."
    ],
    "exercise": "Utiliser CloudGoat dans un environnement autorisé et documenter un risque.",
    "ready": "Tu peux proposer une mesure corrective à un scénario cloud.",
    "featured": [
      "https://github.com/RhinoSecurityLabs/cloudgoat"
    ]
  },
  {
    "id": "containers",
    "title": "Docker, Kubernetes et DevSecOps",
    "phase": "Cloud et infrastructures",
    "intro": "Appliquer les principes de sécurité aux applications déployées.",
    "learn": [
      "Images, conteneurs, registres et secrets.",
      "RBAC, clusters, manifests et contrôles Kubernetes."
    ],
    "exercise": "Installer un petit lab conteneurisé puis corriger deux mauvaises configurations.",
    "ready": "Tu sais expliquer la frontière entre hôte et conteneur.",
    "featured": [
      "https://kubernetes.io/docs/concepts/security/",
      "https://github.com/madhuakula/kubernetes-goat"
    ]
  },
  {
    "id": "mobile",
    "title": "Sécurité mobile : Android et iOS",
    "phase": "Domaines avancés",
    "intro": "Comprendre les applications mobiles et leurs composants.",
    "learn": [
      "APK, permissions, stockage et communications.",
      "Analyse statique d'une application de test."
    ],
    "exercise": "Analyser un APK d'exemple avec Jadx ou MobSF.",
    "ready": "Tu identifies les permissions et points d'entrée d'une app.",
    "featured": [
      "https://mas.owasp.org/"
    ]
  },
  {
    "id": "iot",
    "title": "IoT : firmware et équipements",
    "phase": "Domaines avancés",
    "intro": "Étudier les particularités des objets connectés.",
    "learn": [
      "Firmware, interfaces et mise à jour.",
      "Méthodes d'analyse de systèmes embarqués."
    ],
    "exercise": "Explorer le firmware pédagogique OWASP IoTGoat dans une VM.",
    "ready": "Tu sais expliquer les surfaces d'un système embarqué.",
    "featured": [
      "https://github.com/OWASP/IoTGoat"
    ]
  },
  {
    "id": "ot",
    "title": "OT / ICS : réseaux industriels",
    "phase": "Domaines avancés",
    "intro": "Découvrir les contraintes des environnements industriels.",
    "learn": [
      "PLC, SCADA et protocoles industriels.",
      "Disponibilité, segmentation et sécurité OT."
    ],
    "exercise": "Faire une étude de réseau OT fictif et proposer une segmentation.",
    "ready": "Tu comprends pourquoi la sécurité OT diffère d'un système IT.",
    "featured": [
      "https://csrc.nist.gov/pubs/sp/800/82/r3/final"
    ]
  },
  {
    "id": "grc",
    "title": "GRC : risques, normes et conformité",
    "phase": "Domaines avancés",
    "intro": "Relier les exercices techniques aux exigences de sécurité.",
    "learn": [
      "Analyse de risques, politiques et audit.",
      "ISO 27001, NIST, RGPD et mesures."
    ],
    "exercise": "Rédiger une mini-analyse de risques pour ton lab.",
    "ready": "Tu peux relier un risque à un contrôle vérifiable.",
    "featured": [
      "https://www.iso.org/standard/27001"
    ]
  },
  {
    "id": "ctf-advanced",
    "title": "CTF : challenges avancés et Hackropole",
    "phase": "Validation",
    "intro": "Reprendre l'ensemble des domaines sans se limiter aux exercices guidés.",
    "learn": [
      "Résolution autonome, pistes de recherche et rédaction.",
      "Web, reverse, crypto, réseau et forensic."
    ],
    "exercise": "Résoudre deux épreuves Hackropole de domaines différents.",
    "ready": "Tu peux justifier ta méthode et tes résultats.",
    "featured": [
      "https://hackropole.fr/fr/challenges/",
      "https://www.root-me.org/"
    ]
  },
  {
    "id": "certifications",
    "title": "Certifications et plans de révision",
    "phase": "Validation",
    "intro": "Choisir un examen selon les compétences déjà travaillées.",
    "learn": [
      "Comparer objectifs et prérequis sans confondre diplôme et pratique.",
      "Organiser révisions, labs et fiches."
    ],
    "exercise": "Créer une matrice des compétences déjà maîtrisées et à renforcer.",
    "ready": "Tu peux définir un programme de révision réalisable.",
    "featured": [
      "https://www.offsec.com/",
      "https://training.zeropointsecurity.co.uk/"
    ]
  },
  {
    "id": "community",
    "title": "Communautés, événements et entraide",
    "phase": "Validation",
    "intro": "Partager et apprendre dans un cadre professionnel.",
    "learn": [
      "Communautés, conférences et retour d'expérience.",
      "Rédaction, contribution et veille collaborative."
    ],
    "exercise": "Rédiger un court retour d'expérience technique anonymisé.",
    "ready": "Tu sais partager une méthode sans exposer de données sensibles.",
    "featured": [
      "https://www.defcon.org/"
    ]
  },
  {
    "id": "research",
    "title": "Veille, CVE et recherche",
    "phase": "Validation",
    "intro": "Garder sa méthode à jour une fois les bases acquises.",
    "learn": [
      "Avis de sécurité, CVE et bulletins fournisseurs.",
      "Sources primaires, vérification et traçabilité."
    ],
    "exercise": "Suivre trois CVE et noter description, produit affecté et correctif.",
    "ready": "Tu sais vérifier une information technique à sa source.",
    "featured": [
      "https://nvd.nist.gov/",
      "https://cve.mitre.org/"
    ]
  },
  {
    "id": "final-project",
    "title": "Projet final : audit et restitution",
    "phase": "Validation",
    "intro": "Rassembler apprentissage offensif, défensif et restitution.",
    "learn": [
      "Cadrer un environnement isolé et autorisé.",
      "Tester, observer, corriger et documenter."
    ],
    "exercise": "Créer un lab multi-VM, mener un audit limité, relever les alertes et rédiger un rapport de corrections.",
    "ready": "Tu possèdes un compte rendu clair, reproductible et vérifiable.",
    "featured": [
      "https://github.com/juice-shop/juice-shop",
      "https://github.com/Orange-Cyberdefense/GOAD"
    ]
  }
] as const

export const academyExtraResources = [
  {
    "id": "added-001",
    "title": "GitHub Skills - premiers pas",
    "url": "https://skills.github.com/",
    "category": "additional",
    "routeLevel": "scripting",
    "access": "Gratuit"
  },
  {
    "id": "added-002",
    "title": "Documentation PowerShell",
    "url": "https://learn.microsoft.com/en-us/powershell/",
    "category": "additional",
    "routeLevel": "powershell",
    "access": "Gratuit"
  },
  {
    "id": "added-003",
    "title": "Microsoft Sysmon",
    "url": "https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon",
    "category": "additional",
    "routeLevel": "blue-logs",
    "access": "Gratuit"
  },
  {
    "id": "added-004",
    "title": "OWASP API Security",
    "url": "https://owasp.org/www-project-api-security/",
    "category": "additional",
    "routeLevel": "web-api",
    "access": "Gratuit"
  },
  {
    "id": "added-005",
    "title": "OWASP Top 10",
    "url": "https://owasp.org/www-project-top-ten/",
    "category": "additional",
    "routeLevel": "web-security",
    "access": "Gratuit"
  },
  {
    "id": "added-006",
    "title": "OSINT Framework",
    "url": "https://osintframework.com/",
    "category": "additional",
    "routeLevel": "osint-recon",
    "access": "Gratuit"
  },
  {
    "id": "added-007",
    "title": "Microsoft - Active Directory Domain Services",
    "url": "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview",
    "category": "additional",
    "routeLevel": "ad-intro",
    "access": "Gratuit"
  },
  {
    "id": "added-008",
    "title": "GOAD - environnement AD",
    "url": "https://github.com/Orange-Cyberdefense/GOAD",
    "category": "additional",
    "routeLevel": "ad-full",
    "access": "Open source"
  },
  {
    "id": "added-009",
    "title": "Cobalt Strike - manuel officiel",
    "url": "https://www.cobaltstrike.com/support/user-manuals",
    "category": "additional",
    "routeLevel": "c2",
    "access": "Documentation gratuite, produit sous licence"
  },
  {
    "id": "added-010",
    "title": "Cobalt Strike - formations officielles",
    "url": "https://www.cobaltstrike.com/support/training",
    "category": "additional",
    "routeLevel": "c2",
    "access": "Formations à conditions variables"
  },
  {
    "id": "added-011",
    "title": "Cobalt Strike - projets GitHub publics",
    "url": "https://github.com/Cobalt-Strike",
    "category": "additional",
    "routeLevel": "c2",
    "access": "Gratuit"
  },
  {
    "id": "added-012",
    "title": "Sliver - framework C2 open source",
    "url": "https://github.com/BishopFox/sliver",
    "category": "additional",
    "routeLevel": "c2",
    "access": "Open source"
  },
  {
    "id": "added-013",
    "title": "Sliver - documentation et ateliers",
    "url": "https://sliver.sh/",
    "category": "additional",
    "routeLevel": "c2",
    "access": "Gratuit"
  },
  {
    "id": "added-014",
    "title": "Mythic - framework C2 open source",
    "url": "https://github.com/its-a-feature/Mythic",
    "category": "additional",
    "routeLevel": "c2",
    "access": "Open source"
  },
  {
    "id": "added-015",
    "title": "Mythic - documentation",
    "url": "https://docs.mythic-c2.net/",
    "category": "additional",
    "routeLevel": "c2",
    "access": "Gratuit"
  },
  {
    "id": "added-016",
    "title": "CALDERA - émulation et lab C2",
    "url": "https://github.com/apache/caldera",
    "category": "additional",
    "routeLevel": "c2",
    "access": "Open source"
  },
  {
    "id": "added-017",
    "title": "CALDERA - documentation et entraînement",
    "url": "https://caldera.readthedocs.io/en/stable/index.html",
    "category": "additional",
    "routeLevel": "c2",
    "access": "Gratuit"
  },
  {
    "id": "added-018",
    "title": "MITRE ATT&CK - Command and Control",
    "url": "https://attack.mitre.org/tactics/TA0011/",
    "category": "additional",
    "routeLevel": "c2",
    "access": "Gratuit"
  },
  {
    "id": "added-019",
    "title": "Atomic Red Team - tests ATT&CK",
    "url": "https://github.com/redcanaryco/atomic-red-team",
    "category": "additional",
    "routeLevel": "red-advanced",
    "access": "Open source"
  },
  {
    "id": "added-020",
    "title": "Ligolo-ng - tunnels dans un lab",
    "url": "https://github.com/nicocha30/ligolo-ng",
    "category": "additional",
    "routeLevel": "red-advanced",
    "access": "Open source"
  },
  {
    "id": "added-021",
    "title": "Sigma - détection",
    "url": "https://github.com/SigmaHQ/sigma",
    "category": "additional",
    "routeLevel": "blue-siem",
    "access": "Open source"
  },
  {
    "id": "added-022",
    "title": "Wazuh - SIEM open source",
    "url": "https://wazuh.com/",
    "category": "additional",
    "routeLevel": "blue-siem",
    "access": "Open source"
  },
  {
    "id": "added-023",
    "title": "DetectionLab - laboratoire de journalisation",
    "url": "https://github.com/clong/DetectionLab",
    "category": "additional",
    "routeLevel": "blue-siem",
    "access": "Open source, projet ancien"
  },
  {
    "id": "added-024",
    "title": "Malware Traffic Analysis - PCAP pédagogiques",
    "url": "https://www.malware-traffic-analysis.net/",
    "category": "additional",
    "routeLevel": "malware",
    "access": "Gratuit"
  },
  {
    "id": "added-025",
    "title": "Volatility 3 - analyse mémoire",
    "url": "https://github.com/volatilityfoundation/volatility3",
    "category": "additional",
    "routeLevel": "dfir-host",
    "access": "Open source"
  },
  {
    "id": "added-026",
    "title": "REMnux - analyse de malware",
    "url": "https://remnux.org/",
    "category": "additional",
    "routeLevel": "malware",
    "access": "Open source"
  },
  {
    "id": "added-027",
    "title": "Microsoft Learn - Azure",
    "url": "https://learn.microsoft.com/en-us/training/azure/",
    "category": "additional",
    "routeLevel": "cloud-foundations",
    "access": "Gratuit"
  },
  {
    "id": "added-028",
    "title": "CloudGoat - labs cloud",
    "url": "https://github.com/RhinoSecurityLabs/cloudgoat",
    "category": "additional",
    "routeLevel": "cloud-security",
    "access": "Open source"
  },
  {
    "id": "added-029",
    "title": "Kubernetes - documentation sécurité",
    "url": "https://kubernetes.io/docs/concepts/security/",
    "category": "additional",
    "routeLevel": "containers",
    "access": "Gratuit"
  },
  {
    "id": "added-030",
    "title": "Kubernetes Goat - lab",
    "url": "https://github.com/madhuakula/kubernetes-goat",
    "category": "additional",
    "routeLevel": "containers",
    "access": "Open source"
  },
  {
    "id": "added-031",
    "title": "OWASP Mobile Application Security",
    "url": "https://mas.owasp.org/",
    "category": "additional",
    "routeLevel": "mobile",
    "access": "Gratuit"
  },
  {
    "id": "added-032",
    "title": "OWASP IoTGoat - lab firmware",
    "url": "https://github.com/OWASP/IoTGoat",
    "category": "additional",
    "routeLevel": "iot",
    "access": "Open source"
  },
  {
    "id": "added-033",
    "title": "NIST SP 800-82 - sécurité OT",
    "url": "https://csrc.nist.gov/pubs/sp/800/82/r3/final",
    "category": "additional",
    "routeLevel": "ot",
    "access": "Gratuit"
  },
  {
    "id": "added-034",
    "title": "ISO/IEC 27001 - présentation",
    "url": "https://www.iso.org/standard/27001",
    "category": "additional",
    "routeLevel": "grc",
    "access": "Norme complète potentiellement payante"
  },
  {
    "id": "added-035",
    "title": "Hackropole - challenges ANSSI",
    "url": "https://hackropole.fr/fr/challenges/",
    "category": "additional",
    "routeLevel": "ctf-advanced",
    "access": "Gratuit"
  },
  {
    "id": "added-036",
    "title": "OffSec - certifications et formations",
    "url": "https://www.offsec.com/",
    "category": "additional",
    "routeLevel": "certifications",
    "access": "Formations à conditions variables"
  },
  {
    "id": "added-037",
    "title": "Zero-Point Security - formations",
    "url": "https://training.zeropointsecurity.co.uk/",
    "category": "additional",
    "routeLevel": "certifications",
    "access": "Formations à conditions variables"
  },
  {
    "id": "added-038",
    "title": "DEF CON",
    "url": "https://www.defcon.org/",
    "category": "additional",
    "routeLevel": "community",
    "access": "Gratuit pour les informations"
  },
  {
    "id": "added-039",
    "title": "NVD - vulnérabilités",
    "url": "https://nvd.nist.gov/",
    "category": "additional",
    "routeLevel": "research",
    "access": "Gratuit"
  },
  {
    "id": "added-040",
    "title": "CVE Program",
    "url": "https://cve.mitre.org/",
    "category": "additional",
    "routeLevel": "research",
    "access": "Gratuit"
  },
  {
    "id": "added-041",
    "title": "OWASP crAPI - lab API",
    "url": "https://github.com/OWASP/crAPI",
    "category": "additional",
    "routeLevel": "web-labs",
    "access": "Open source"
  },
  {
    "id": "added-042",
    "title": "Ghidra - reverse engineering",
    "url": "https://ghidra-sre.org/",
    "category": "additional",
    "routeLevel": "reverse",
    "access": "Gratuit"
  },
  {
    "id": "added-043",
    "title": "pwn.college",
    "url": "https://pwn.college/",
    "category": "additional",
    "routeLevel": "ctf-intermediate",
    "access": ""
  }
] as const

export const academyAssignments: Record<string,string> = {
  "task-l0-1": "linux-basics",
  "task-l0-2": "linux-basics",
  "task-l1-2": "network-practice",
  "task-l2-1": "python-basics",
  "task-l2-2": "web-labs",
  "task-l2-3": "crypto",
  "task-l3-1": "web-labs",
  "task-l3-2": "web-api",
  "task-l3-3": "web-labs",
  "task-l4-1": "web-labs",
  "task-l4-2": "ctf-beginner",
  "task-l4-3": "ctf-beginner",
  "lab-owasp-webgoat": "web-labs",
  "lab-owasp-crapi": "web-labs",
  "lab-vulhub": "ctf-intermediate",
  "lab-metasploitable3": "pentest-system",
  "lab-goad-minilab": "ad-minilab",
  "lab-goad-light": "ad-light",
  "lab-goad-complet": "ad-full",
  "lab-owasp-wrongsecrets": "cloud-security",
  "lab-kubernetes-goat": "containers",
  "lab-cloudgoat": "cloud-security",
  "off-002": "environment",
  "off-004": "network-basics",
  "off-005": "network-practice",
  "off-007": "windows-basics",
  "off-008": "linux-basics",
  "off-009": "python-basics",
  "off-010": "python-basics",
  "off-011": "scripting",
  "off-012": "environment",
  "off-014": "security-basics",
  "off-016": "ctf-beginner",
  "off-018": "ctf-beginner",
  "off-019": "ctf-advanced",
  "off-021": "web-security",
  "off-022": "web-labs",
  "off-023": "web-labs",
  "off-024": "web-security",
  "off-025": "ctf-intermediate",
  "off-026": "ctf-intermediate",
  "off-027": "blue-siem",
  "off-028": "blue-logs",
  "off-029": "blue-threat",
  "off-030": "dfir-host",
  "off-031": "dfir-host",
  "off-033": "cloud-foundations",
  "off-034": "cloud-foundations",
  "off-035": "cloud-foundations",
  "off-036": "reverse",
  "off-037": "malware",
  "off-038": "malware",
  "off-040": "ot",
  "online-web-PortSwig": "web-labs",
  "cu-001": "network-practice",
  "cu-002": "security-basics",
  "cu-003": "ctf-intermediate",
  "cu-004": "linux-basics",
  "cu-005": "linux-basics",
  "cu-006": "linux-basics",
  "cu-007": "ctf-intermediate",
  "cu-008": "security-basics",
  "cu-009": "red-advanced",
  "cu-010": "ctf-intermediate",
  "cu-011": "linux-basics",
  "cu-012": "linux-basics",
  "cu-013": "osint-recon",
  "cu-014": "osint-recon",
  "cu-015": "osint-recon",
  "cu-016": "linux-admin",
  "cu-017": "network-practice",
  "cu-018": "scanning",
  "cu-019": "osint-recon",
  "cu-020": "pentest-system",
  "cu-021": "pentest-system",
  "cu-022": "pentest-system",
  "cu-023": "red-advanced",
  "cu-024": "osint-recon",
  "cu-025": "network-practice",
  "cu-026": "ctf-intermediate",
  "cu-027": "ctf-intermediate",
  "cu-028": "ctf-beginner",
  "cu-029": "ctf-intermediate",
  "cu-030": "crypto",
  "cu-031": "ctf-intermediate",
  "cu-032": "ctf-intermediate",
  "cu-033": "ctf-intermediate",
  "cu-034": "ctf-intermediate",
  "cu-035": "ctf-beginner",
  "cu-036": "pentest-system",
  "cu-037": "web-security",
  "cu-038": "web-labs",
  "cu-039": "web-security",
  "cu-040": "web-labs",
  "cu-041": "ctf-intermediate",
  "cu-042": "ctf-intermediate",
  "cu-043": "ctf-intermediate",
  "cu-044": "ctf-intermediate",
  "cu-045": "ctf-intermediate",
  "cu-046": "reverse",
  "cu-047": "reverse",
  "cu-048": "reverse",
  "cu-049": "reverse",
  "cu-050": "reverse",
  "cu-051": "reverse",
  "cu-052": "reverse",
  "cu-053": "pentest-system",
  "cu-054": "pentest-system",
  "cu-055": "pentest-system",
  "cu-056": "pentest-system",
  "cu-057": "pentest-system",
  "cu-058": "pentest-system",
  "cu-059": "ctf-advanced",
  "cu-060": "ctf-advanced",
  "cu-061": "ctf-advanced",
  "cu-062": "ctf-advanced",
  "cu-063": "ctf-advanced",
  "cu-064": "dfir-host",
  "cu-065": "windows-basics",
  "cu-066": "blue-siem",
  "cu-067": "blue-threat",
  "cu-068": "blue-siem",
  "cu-069": "blue-siem",
  "cu-070": "blue-siem",
  "cu-071": "blue-siem",
  "cu-072": "dfir-host",
  "cu-073": "dfir-host",
  "cu-074": "dfir-host",
  "cu-075": "blue-threat",
  "cu-076": "blue-logs",
  "cu-077": "blue-logs",
  "cu-078": "dfir-host",
  "cu-079": "blue-siem",
  "cu-080": "blue-siem",
  "cu-081": "blue-siem",
  "cu-082": "blue-threat",
  "cu-083": "blue-threat",
  "cu-084": "blue-threat",
  "cu-085": "dfir-host",
  "cu-086": "dfir-host",
  "cu-087": "dfir-network",
  "cu-088": "dfir-network",
  "cu-089": "dfir-network",
  "cu-090": "dfir-host",
  "cu-091": "dfir-host",
  "cu-092": "dfir-host",
  "cu-093": "dfir-host",
  "cu-094": "dfir-host",
  "cu-095": "dfir-host",
  "cu-097": "dfir-host",
  "cu-098": "dfir-host",
  "cu-099": "dfir-host",
  "cu-100": "dfir-host",
  "cu-101": "dfir-host",
  "cu-102": "dfir-host",
  "cu-103": "dfir-network",
  "cu-104": "malware",
  "cu-105": "malware",
  "cu-106": "malware",
  "cu-107": "reverse",
  "cu-109": "reverse",
  "cu-110": "dfir-host",
  "cu-113": "pentest-system",
  "cu-114": "ctf-advanced",
  "cu-115": "ctf-advanced",
  "cu-116": "ctf-advanced",
  "cu-117": "ctf-advanced",
  "cu-118": "ctf-advanced",
  "cu-119": "containers",
  "cu-120": "containers",
  "cu-121": "web-labs",
  "cu-122": "web-labs",
  "cu-123": "ctf-advanced",
  "cu-124": "ad-intro",
  "cu-125": "ctf-advanced",
  "cu-126": "ctf-advanced",
  "cu-127": "ctf-advanced",
  "cu-128": "ctf-advanced",
  "cu-129": "ctf-advanced",
  "cu-130": "ctf-advanced",
  "cu-131": "ctf-advanced",
  "cu-132": "ctf-advanced",
  "cu-133": "ctf-advanced",
  "cu-134": "ctf-advanced",
  "cu-135": "ctf-advanced",
  "cu-136": "ctf-advanced",
  "cu-137": "ctf-advanced",
  "cu-138": "ctf-advanced",
  "cu-139": "ctf-advanced",
  "cu-140": "ctf-advanced",
  "hm-001": "environment",
  "hm-002": "environment",
  "hm-003": "environment",
  "hm-004": "environment",
  "hm-005": "linux-basics",
  "hm-006": "environment",
  "hm-007": "environment",
  "hm-008": "network-basics",
  "hm-009": "network-basics",
  "hm-010": "network-basics",
  "hm-011": "network-practice",
  "hm-013": "network-practice",
  "hm-014": "network-practice",
  "hm-015": "network-basics",
  "hm-016": "python-basics",
  "hm-017": "python-basics",
  "hm-018": "python-basics",
  "hm-019": "scripting",
  "hm-020": "scripting",
  "hm-021": "scripting",
  "hm-022": "python-basics",
  "hm-023": "scripting",
  "hm-024": "scripting",
  "hm-025": "scripting",
  "hm-026": "scripting",
  "hm-027": "linux-basics",
  "hm-028": "linux-basics",
  "hm-029": "linux-basics",
  "hm-030": "linux-admin",
  "hm-031": "environment",
  "hm-032": "environment",
  "hm-033": "environment",
  "hm-034": "security-basics",
  "hm-035": "environment",
  "hm-036": "security-basics",
  "hm-037": "crypto",
  "hm-038": "crypto",
  "hm-039": "crypto",
  "hm-040": "crypto",
  "hm-041": "crypto",
  "hm-042": "crypto",
  "hm-043": "crypto",
  "hm-044": "crypto",
  "hm-045": "grc",
  "hm-046": "grc",
  "hm-047": "grc",
  "hm-048": "grc",
  "hm-049": "pentest-system",
  "hm-050": "pentest-system",
  "hm-051": "pentest-system",
  "hm-052": "pentest-system",
  "hm-053": "pentest-system",
  "hm-054": "scanning",
  "hm-055": "scanning",
  "hm-056": "scanning",
  "hm-057": "web-security",
  "hm-058": "scanning",
  "hm-059": "pentest-system",
  "hm-060": "pentest-system",
  "hm-061": "network-basics",
  "hm-062": "scanning",
  "hm-063": "network-basics",
  "hm-064": "network-practice",
  "hm-065": "network-practice",
  "hm-066": "blue-siem",
  "hm-067": "ctf-beginner",
  "hm-068": "blue-siem",
  "hm-070": "blue-siem",
  "hm-071": "blue-siem",
  "hm-072": "blue-siem",
  "hm-073": "network-practice",
  "hm-074": "network-practice",
  "hm-076": "network-practice",
  "hm-077": "network-practice",
  "hm-078": "network-practice",
  "hm-079": "network-basics",
  "hm-080": "powershell",
  "hm-081": "linux-admin",
  "hm-082": "linux-admin",
  "hm-083": "powershell",
  "hm-084": "windows-basics",
  "hm-085": "linux-basics",
  "hm-086": "linux-basics",
  "hm-087": "powershell",
  "hm-088": "blue-logs",
  "hm-089": "blue-siem",
  "hm-090": "blue-siem",
  "hm-091": "blue-siem",
  "hm-092": "blue-logs",
  "hm-093": "blue-logs",
  "hm-094": "blue-siem",
  "hm-095": "linux-basics",
  "hm-096": "linux-basics",
  "hm-097": "linux-basics",
  "hm-098": "linux-basics",
  "hm-099": "web-security",
  "hm-100": "web-security",
  "hm-101": "web-basics",
  "hm-102": "web-security",
  "hm-103": "web-security",
  "hm-104": "web-security",
  "hm-105": "web-api",
  "hm-106": "web-labs",
  "hm-107": "web-labs",
  "hm-108": "ctf-intermediate",
  "hm-109": "web-labs",
  "hm-110": "web-basics",
  "hm-111": "web-basics",
  "hm-112": "scripting",
  "hm-113": "web-labs",
  "hm-114": "web-security",
  "hm-115": "web-basics",
  "hm-116": "web-basics",
  "hm-117": "web-basics",
  "hm-118": "web-security",
  "hm-119": "web-basics",
  "hm-120": "web-basics",
  "hm-121": "web-basics",
  "hm-122": "ctf-beginner",
  "hm-123": "ctf-intermediate",
  "hm-124": "pentest-system",
  "hm-125": "pentest-system",
  "hm-126": "pentest-system",
  "hm-127": "c2",
  "hm-128": "pentest-system",
  "hm-129": "pentest-system",
  "hm-130": "pentest-system",
  "hm-131": "pentest-system",
  "hm-132": "pentest-system",
  "hm-133": "pentest-system",
  "hm-134": "pentest-system",
  "hm-135": "pentest-system",
  "hm-136": "reverse",
  "hm-137": "pentest-system",
  "hm-138": "pentest-system",
  "hm-139": "pentest-system",
  "hm-140": "pentest-system",
  "hm-141": "pentest-system",
  "hm-142": "pentest-system",
  "hm-143": "blue-siem",
  "hm-144": "blue-logs",
  "hm-145": "blue-logs",
  "hm-146": "blue-logs",
  "hm-147": "blue-siem",
  "hm-148": "blue-logs",
  "hm-149": "blue-logs",
  "hm-150": "blue-logs",
  "hm-151": "blue-threat",
  "hm-152": "dfir-host",
  "hm-153": "blue-threat",
  "hm-154": "blue-threat",
  "hm-155": "blue-logs",
  "hm-156": "blue-logs",
  "hm-157": "dfir-host",
  "hm-158": "dfir-host",
  "hm-159": "dfir-host",
  "hm-160": "dfir-host",
  "hm-161": "dfir-host",
  "hm-162": "dfir-host",
  "hm-163": "dfir-host",
  "hm-164": "dfir-host",
  "hm-165": "cloud-foundations",
  "hm-166": "cloud-foundations",
  "hm-167": "cloud-foundations",
  "hm-168": "cloud-foundations",
  "hm-169": "cloud-foundations",
  "hm-170": "cloud-security",
  "hm-171": "cloud-security",
  "hm-172": "cloud-security",
  "hm-173": "containers",
  "hm-174": "cloud-foundations",
  "hm-175": "cloud-foundations",
  "hm-176": "cloud-foundations",
  "hm-177": "cloud-foundations",
  "hm-178": "cloud-foundations",
  "hm-179": "cloud-foundations",
  "hm-180": "cloud-foundations",
  "hm-181": "containers",
  "hm-182": "containers",
  "hm-183": "web-security",
  "hm-184": "containers",
  "hm-185": "containers",
  "hm-186": "containers",
  "hm-187": "containers",
  "hm-188": "containers",
  "hm-189": "malware",
  "hm-190": "malware",
  "hm-191": "malware",
  "hm-192": "reverse",
  "hm-193": "malware",
  "hm-194": "malware",
  "hm-195": "blue-threat",
  "hm-196": "blue-threat",
  "hm-197": "blue-threat",
  "hm-198": "blue-threat",
  "hm-199": "blue-logs",
  "hm-200": "blue-logs",
  "hm-201": "blue-logs",
  "hm-202": "blue-threat",
  "hm-203": "blue-threat",
  "hm-204": "blue-threat",
  "hm-205": "blue-threat",
  "hm-206": "blue-siem",
  "hm-207": "blue-siem",
  "hm-208": "web-security",
  "hm-209": "iot",
  "hm-210": "iot",
  "hm-211": "iot",
  "hm-212": "osint-recon",
  "hm-213": "iot",
  "hm-214": "iot",
  "hm-215": "web-security",
  "hm-216": "web-security",
  "hm-217": "mobile",
  "hm-218": "mobile",
  "hm-219": "mobile",
  "hm-220": "mobile",
  "hm-221": "mobile",
  "hm-222": "mobile",
  "hm-223": "ot",
  "hm-224": "ot",
  "hm-225": "ot",
  "hm-226": "ot",
  "hm-227": "ot",
  "hm-228": "ot",
  "hm-229": "certifications",
  "hm-230": "certifications",
  "hm-231": "certifications",
  "hm-232": "certifications",
  "hm-233": "certifications",
  "hm-234": "certifications",
  "hm-235": "certifications",
  "hm-236": "research",
  "hm-237": "community",
  "hm-238": "web-security",
  "hm-239": "community",
  "hm-240": "community",
  "hm-241": "community",
  "hm-242": "research",
  "hm-243": "research",
  "hm-244": "research",
  "hm-245": "research",
  "hm-246": "research",
  "hm-247": "research",
  "hm-248": "research",
  "hm-249": "ctf-intermediate",
  "hm-250": "ctf-intermediate",
  "hm-251": "ctf-intermediate",
  "hm-252": "certifications",
  "hm-253": "certifications",
  "hm-254": "certifications",
  "hm-255": "certifications",
  "hm-256": "certifications",
  "hm-257": "certifications",
  "hm-258": "ctf-intermediate",
  "hm-259": "certifications",
  "hm-260": "certifications",
  "hm-261": "web-labs",
  "hm-262": "ctf-beginner",
  "hm-263": "ctf-intermediate",
  "hm-264": "crypto",
  "hm-265": "ctf-intermediate",
  "hm-266": "community",
  "hm-267": "community",
  "hm-268": "community",
  "hm-269": "community",
  "hm-270": "community",
  "hm-271": "community",
  "hm-272": "community",
  "hm-273": "community",
  "hm-274": "community",
  "hm-275": "community",
  "hm-276": "community",
  "hm-277": "community",
  "hm-278": "certifications",
  "hm-279": "osint-recon",
  "hm-280": "osint-recon",
  "hm-281": "osint-recon",
  "hm-282": "osint-recon",
  "hm-283": "web-security",
  "hm-284": "osint-recon",
  "hm-285": "web-security",
  "hm-286": "pentest-system",
  "hm-287": "pentest-system",
  "hm-288": "pentest-system",
  "hm-289": "scanning",
  "hm-290": "web-security",
  "hm-291": "web-security",
  "hm-292": "web-security",
  "hm-293": "pentest-system",
  "hm-294": "pentest-system",
  "hm-295": "pentest-system",
  "hm-296": "c2",
  "hm-297": "pentest-system",
  "hm-298": "pentest-system",
  "hm-299": "red-advanced",
  "hm-300": "pentest-system",
  "hm-301": "pentest-system",
  "hm-302": "pentest-system",
  "hm-303": "pentest-system",
  "hm-304": "pentest-system",
  "hm-305": "dfir-host",
  "hm-306": "dfir-host",
  "hm-307": "dfir-host",
  "hm-308": "dfir-host",
  "hm-309": "blue-logs",
  "hm-310": "cloud-security",
  "hm-311": "cloud-security",
  "hm-312": "cloud-security",
  "hm-313": "cloud-security",
  "hm-314": "cloud-security",
  "hm-315": "ad-intro",
  "hm-316": "cloud-security",
  "hm-317": "containers",
  "hm-318": "mobile",
  "hm-319": "mobile",
  "hm-320": "mobile",
  "hm-321": "mobile",
  "hm-322": "mobile",
  "hm-323": "osint-recon",
  "hm-324": "osint-recon",
  "hm-325": "osint-recon",
  "hm-326": "osint-recon",
  "hm-327": "certifications",
  "hm-328": "certifications",
  "hm-329": "certifications",
  "hm-330": "certifications",
  "hm-331": "certifications",
  "hm-332": "certifications",
  "hm-333": "certifications",
  "hm-334": "certifications",
  "hm-335": "certifications",
  "hm-336": "certifications",
  "hm-337": "certifications",
  "hm-338": "certifications",
  "hm-339": "certifications",
  "hm-340": "certifications",
  "hm-341": "community",
  "hm-342": "community",
  "hm-343": "community",
  "hm-344": "community",
  "hm-345": "web-security",
  "hm-346": "ctf-intermediate",
  "hm-347": "ctf-intermediate",
  "hm-348": "community",
  "hm-349": "community",
  "hm-350": "community",
  "hm-351": "community",
  "hm-352": "community",
  "hm-353": "community",
  "hm-354": "community",
  "hm-355": "community",
  "hm-356": "community",
  "hm-357": "community",
  "hm-358": "community",
  "hm-359": "community",
  "hm-360": "community",
  "hm-361": "community",
  "hm-362": "community",
  "hm-363": "community",
  "hm-364": "community",
  "hm-365": "community",
  "hm-366": "community",
  "hm-367": "ctf-beginner",
  "hm-368": "ctf-intermediate",
  "hm-369": "ctf-intermediate",
  "hm-370": "ctf-intermediate",
  "hm-371": "ctf-beginner",
  "hm-372": "ctf-intermediate",
  "hm-373": "ctf-intermediate",
  "hm-374": "ctf-intermediate",
  "hm-375": "ctf-intermediate",
  "hm-376": "ctf-intermediate",
  "hm-377": "ctf-intermediate",
  "hm-378": "ctf-intermediate",
  "hm-379": "ctf-intermediate",
  "hm-380": "ctf-intermediate",
  "hm-381": "ctf-intermediate",
  "hm-382": "ctf-intermediate",
  "hm-383": "ctf-intermediate",
  "hm-384": "ctf-intermediate",
  "hm-385": "ctf-intermediate",
  "hm-386": "ctf-intermediate",
  "hm-387": "environment",
  "hm-388": "environment",
  "hm-389": "environment",
  "hm-390": "environment",
  "hm-391": "environment",
  "hm-392": "environment",
  "hm-393": "environment",
  "hm-394": "environment",
  "hm-395": "environment",
  "hm-396": "ctf-intermediate",
  "hm-397": "environment",
  "hm-398": "environment",
  "hm-399": "ad-intro",
  "hm-400": "environment",
  "hm-401": "research",
  "hm-402": "research",
  "hm-403": "research",
  "hm-404": "research",
  "hm-405": "research",
  "hm-406": "research",
  "hm-407": "research",
  "hm-408": "research",
  "hm-409": "research",
  "hm-410": "research",
  "hm-411": "research",
  "hm-412": "research",
  "hm-413": "research",
  "hm-414": "research",
  "hm-415": "research",
  "hm-416": "research",
  "hm-417": "research",
  "hm-418": "research",
  "hm-419": "research",
  "hm-420": "research",
  "hm-421": "research",
  "hm-422": "research",
  "hm-423": "research",
  "hm-424": "research",
  "hm-425": "research",
  "hm-426": "osint-recon",
  "hm-427": "malware",
  "hm-428": "malware",
  "hm-429": "malware",
  "hm-430": "web-security"
}

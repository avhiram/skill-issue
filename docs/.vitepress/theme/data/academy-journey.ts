// Parcours progressif original SKILL-ISSUE. Les URL mènent vers les pages officielles des ressources.
export const journey = [
  {
    "id": "environment",
    "title": "Environnement",
    "intro": "Prends tes repères sur ton ordinateur et installe un espace de travail pour t'entraîner.",
    "learn": [
      "Fichiers, dossiers, téléchargements et logiciels.",
      "Navigateur, terminal et machine virtuelle.",
      "Créer un dossier et conserver ses notes."
    ],
    "exercise": "Créer un dossier pour tes labs, lancer un terminal et ouvrir ton premier exercice interactif.",
    "ready": "Tu retrouves tes fichiers, sais utiliser un terminal et comprends le rôle d'une VM.",
    "links": [
      {
        "title": "pwn.college - Linux Luminarium",
        "url": "https://pwn.college/linux-luminarium/"
      },
      {
        "title": "VirtualBox",
        "url": "https://www.virtualbox.org/"
      },
      {
        "title": "CS50 - Introduction à l'informatique",
        "url": "https://cs50.harvard.edu/x/"
      }
    ]
  },
  {
    "id": "network",
    "title": "Réseaux",
    "intro": "Avant la cybersécurité, comprends comment communiquent les machines.",
    "learn": [
      "Adresse IP, routeur, DNS et sous-réseau.",
      "Ports, TCP/UDP, HTTP et HTTPS.",
      "Lire une capture de trafic dans Wireshark."
    ],
    "exercise": "Ouvrir un PCAP, repérer une requête DNS et une connexion TCP, puis identifier les adresses et ports.",
    "ready": "Tu sais expliquer une IP, un port et le chemin d'une requête Web.",
    "links": [
      {
        "title": "Practical Networking",
        "url": "https://www.practicalnetworking.net/"
      },
      {
        "title": "Wireshark - captures d'exemple",
        "url": "https://wiki.wireshark.org/SampleCaptures"
      },
      {
        "title": "Cisco Packet Tracer",
        "url": "https://www.netacad.com/courses/packet-tracer"
      }
    ]
  },
  {
    "id": "linux",
    "title": "Linux",
    "intro": "Apprends les commandes que tu utiliseras tout au long du parcours.",
    "learn": [
      "Se déplacer avec pwd, ls et cd.",
      "Lire, chercher et modifier un fichier.",
      "Utilisateurs, permissions, processus et SSH."
    ],
    "exercise": "Résoudre OverTheWire Bandit 0 à 10 sans copier de solution.",
    "ready": "Tu peux chercher un fichier, identifier ses permissions et te connecter en SSH.",
    "links": [
      {
        "title": "OverTheWire - Bandit",
        "url": "https://overthewire.org/wargames/bandit/"
      },
      {
        "title": "pwn.college - Linux Luminarium",
        "url": "https://pwn.college/linux-luminarium/"
      },
      {
        "title": "Ubuntu - Terminal pour débutants",
        "url": "https://ubuntu.com/tutorials/command-line-for-beginners#1-overview"
      }
    ]
  },
  {
    "id": "windows",
    "title": "Windows",
    "intro": "Comprends les comptes, les services et les commandes d'un système Windows.",
    "learn": [
      "CMD et PowerShell : commandes de base.",
      "Comptes locaux, groupes et droits.",
      "Processus, services et journaux d'événements."
    ],
    "exercise": "Dans ton Windows ou une VM, relever l'IP, les comptes et les processus actifs avec les outils système.",
    "ready": "Tu peux retrouver utilisateurs, services et informations réseau sans guide.",
    "links": [
      {
        "title": "Microsoft - Commandes Windows",
        "url": "https://learn.microsoft.com/fr-fr/windows-server/administration/windows-commands/windows-commands"
      },
      {
        "title": "Microsoft - Sysinternals",
        "url": "https://docs.microsoft.com/en-us/sysinternals/"
      },
      {
        "title": "TryHackMe - Windows Fundamentals",
        "url": "https://tryhackme.com/room/windowsfundamentals1xbx"
      }
    ]
  },
  {
    "id": "web",
    "title": "Web & HTTP",
    "intro": "Comprends ce qui se passe entre le navigateur et un serveur.",
    "learn": [
      "HTML, URL, paramètres et formulaires.",
      "Méthodes et codes HTTP, cookies et sessions.",
      "Outils développeur et interception de requêtes."
    ],
    "exercise": "Observer une requête dans le navigateur, puis résoudre OverTheWire Natas 0 à 4.",
    "ready": "Tu sais distinguer une requête, une réponse et un paramètre Web.",
    "links": [
      {
        "title": "MDN - Apprendre le Web",
        "url": "https://developer.mozilla.org/fr/docs/Learn_web_development"
      },
      {
        "title": "OverTheWire - Natas",
        "url": "https://overthewire.org/wargames/natas/"
      },
      {
        "title": "PortSwigger - Web Security Academy",
        "url": "https://portswigger.net/web-security/"
      }
    ]
  },
  {
    "id": "scripting",
    "title": "Python & scripting",
    "intro": "Automatise les petites tâches avant de passer aux outils complexes.",
    "learn": [
      "Variables, conditions, boucles et fonctions.",
      "Lire un fichier et manipuler du texte.",
      "Exécuter et corriger un script Python."
    ],
    "exercise": "Écrire un script Python qui compte les lignes d'un fichier et affiche le résultat.",
    "ready": "Tu peux modifier et exécuter un script simple sans recopier aveuglément.",
    "links": [
      {
        "title": "CS50P - Python",
        "url": "https://cs50.harvard.edu/python/"
      },
      {
        "title": "freeCodeCamp - Exercices Python",
        "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/"
      },
      {
        "title": "Automate the Boring Stuff with Python",
        "url": "https://automatetheboringstuff.com/"
      }
    ]
  },
  {
    "id": "security",
    "title": "Sécurité",
    "intro": "Découvre les vulnérabilités, l'authentification et les bases de la protection.",
    "learn": [
      "Différence entre vulnérabilité, risque et exploitation.",
      "Identifiants, droits, chiffrement et hash.",
      "Noter la cause d'une faille et une correction possible."
    ],
    "exercise": "Résoudre un premier lab PortSwigger puis expliquer en quelques phrases ce que tu as observé.",
    "ready": "Tu peux décrire une faille simple, son impact et comment la limiter.",
    "links": [
      {
        "title": "PortSwigger - Lab Path Traversal",
        "url": "https://portswigger.net/web-security/file-path-traversal/lab-simple"
      },
      {
        "title": "CryptoHack - Introduction",
        "url": "https://cryptohack.org/courses/intro/course_details/"
      },
      {
        "title": "CyberChef",
        "url": "https://gchq.github.io/CyberChef/"
      }
    ]
  },
  {
    "id": "tools",
    "title": "Outils de sécurité",
    "intro": "Utilise les outils de base dans ton propre lab, pas sur des systèmes tiers.",
    "learn": [
      "Découverte de services avec Nmap.",
      "Analyse réseau avec Wireshark.",
      "Inspection de requêtes HTTP avec un proxy."
    ],
    "exercise": "Sur deux machines virtuelles isolées, identifier les services de la VM cible et relever leurs ports.",
    "ready": "Tu sais identifier les services d'un lab et prendre des notes propres.",
    "links": [
      {
        "title": "Nmap",
        "url": "https://nmap.org/"
      },
      {
        "title": "Wireshark",
        "url": "https://www.wireshark.org/"
      },
      {
        "title": "OWASP ZAP - Démarrage",
        "url": "https://www.zaproxy.org/getting-started/"
      }
    ]
  },
  {
    "id": "challenges",
    "title": "Labs & CTF",
    "intro": "Mets ensemble réseau, Linux, Web et scripting dans des exercices guidés.",
    "learn": [
      "Lire un énoncé et choisir un outil.",
      "Résoudre un challenge sans solution immédiate.",
      "Reprendre les commandes et expliquer leur utilité."
    ],
    "exercise": "Résoudre trois challenges différents sur picoCTF ou Root-Me et une room gratuite TryHackMe.",
    "ready": "Tu sais retrouver et expliquer les étapes d'une résolution simple.",
    "links": [
      {
        "title": "Root-Me",
        "url": "https://www.root-me.org/"
      },
      {
        "title": "picoCTF",
        "url": "https://picoctf.org/"
      },
      {
        "title": "TryHackMe - Free Rooms",
        "url": "https://tryhackme.com/free-rooms"
      },
      {
        "title": "PortSwigger - Tous les labs",
        "url": "https://portswigger.net/web-security/all-labs"
      }
    ]
  },
  {
    "id": "local-lab",
    "title": "Lab local",
    "intro": "Installe une application volontairement vulnérable dans un environnement isolé.",
    "learn": [
      "Virtualisation ou Docker : démarrage et arrêt.",
      "Comprendre les services d'une application Web.",
      "Tracer tes tests et rédiger les résultats."
    ],
    "exercise": "Installer DVWA, Juice Shop ou WebGoat localement et terminer cinq challenges simples.",
    "ready": "Tu sais installer, utiliser puis arrêter un lab sans l'exposer à Internet.",
    "links": [
      {
        "title": "DVWA",
        "url": "https://github.com/digininja/DVWA"
      },
      {
        "title": "OWASP Juice Shop",
        "url": "https://github.com/juice-shop/juice-shop"
      },
      {
        "title": "OWASP WebGoat",
        "url": "https://github.com/WebGoat/WebGoat"
      }
    ]
  },
  {
    "id": "project",
    "title": "Projet final",
    "intro": "Valide les fondamentaux sur un mini-projet complet avant de choisir ta spécialité.",
    "learn": [
      "Définir le périmètre d'un lab autorisé.",
      "Observer, tester, documenter et reproduire.",
      "Rédiger un court rapport structuré."
    ],
    "exercise": "Choisir un lab déjà installé et produire un compte rendu : contexte, étapes réalisées, résultat et pistes de correction.",
    "ready": "Tu as un premier compte rendu reproductible, avec captures et commandes utiles.",
    "links": [
      {
        "title": "OWASP Juice Shop - Lab local",
        "url": "https://github.com/juice-shop/juice-shop"
      },
      {
        "title": "PortSwigger - Labs",
        "url": "https://portswigger.net/web-security/all-labs"
      },
      {
        "title": "picoCTF - Practice",
        "url": "https://picoctf.org/"
      }
    ]
  }
];
export const branches = [
  {
    "id": "pentest",
    "title": "Pentest / Red Team",
    "desc": "Tester des machines et des réseaux autorisés.",
    "sections": [
      {
        "title": "Reconnaissance",
        "goal": "Identifier hôtes, services et surfaces d'attaque sur une machine de lab.",
        "links": [
          {
            "title": "Nmap",
            "url": "https://nmap.org/"
          },
          {
            "title": "HackTricks",
            "url": "https://book.hacktricks.wiki/"
          }
        ]
      },
      {
        "title": "Premières machines",
        "goal": "Résoudre une machine de lab et expliquer chaque étape.",
        "links": [
          {
            "title": "TryHackMe - Free Rooms",
            "url": "https://tryhackme.com/free-rooms"
          },
          {
            "title": "Vulhub",
            "url": "https://github.com/vulhub/vulhub"
          }
        ]
      },
      {
        "title": "Windows et Linux",
        "goal": "Étudier permissions et mauvaises configurations sur un environnement contrôlé.",
        "links": [
          {
            "title": "Metasploitable3",
            "url": "https://github.com/rapid7/metasploitable3"
          },
          {
            "title": "pwn.college",
            "url": "https://pwn.college/"
          }
        ]
      },
      {
        "title": "Rapport et méthode",
        "goal": "Terminer un lab de bout en bout et rendre un rapport reproductible.",
        "links": [
          {
            "title": "Root-Me",
            "url": "https://www.root-me.org/"
          },
          {
            "title": "PortSwigger",
            "url": "https://portswigger.net/web-security/"
          }
        ]
      }
    ]
  },
  {
    "id": "web",
    "title": "Web Security",
    "desc": "Rechercher et comprendre les failles des applications Web et API.",
    "sections": [
      {
        "title": "HTTP & proxy",
        "goal": "Intercepter des requêtes et comprendre paramètres, cookies et sessions.",
        "links": [
          {
            "title": "PortSwigger - Web Security Academy",
            "url": "https://portswigger.net/web-security/"
          }
        ]
      },
      {
        "title": "Premières vulnérabilités",
        "goal": "Résoudre des labs injection, XSS et contrôle d'accès.",
        "links": [
          {
            "title": "PortSwigger - Tous les labs",
            "url": "https://portswigger.net/web-security/all-labs"
          },
          {
            "title": "DVWA",
            "url": "https://github.com/digininja/DVWA"
          }
        ]
      },
      {
        "title": "API Security",
        "goal": "Comprendre les API et pratiquer sur un environnement vulnérable.",
        "links": [
          {
            "title": "OWASP crAPI",
            "url": "https://github.com/OWASP/crAPI"
          }
        ]
      },
      {
        "title": "Projet complet",
        "goal": "Terminer plusieurs défis et préparer un rapport.",
        "links": [
          {
            "title": "OWASP Juice Shop",
            "url": "https://github.com/juice-shop/juice-shop"
          },
          {
            "title": "OWASP WebGoat",
            "url": "https://github.com/WebGoat/WebGoat"
          }
        ]
      }
    ]
  },
  {
    "id": "blue",
    "title": "Blue Team / SOC",
    "desc": "Détecter, examiner et comprendre les incidents.",
    "sections": [
      {
        "title": "Logs et événements",
        "goal": "Identifier les événements importants d'un système.",
        "links": [
          {
            "title": "Microsoft - Sysinternals",
            "url": "https://docs.microsoft.com/en-us/sysinternals/"
          },
          {
            "title": "MITRE ATT&CK",
            "url": "https://attack.mitre.org/"
          }
        ]
      },
      {
        "title": "Premières alertes",
        "goal": "Trier une alerte et reconstituer un scénario d'incident.",
        "links": [
          {
            "title": "LetsDefend",
            "url": "https://app.letsdefend.io/challenge"
          },
          {
            "title": "Blue Team Labs Online",
            "url": "https://blueteamlabs.online/"
          }
        ]
      },
      {
        "title": "SIEM et détection",
        "goal": "Explorer les journaux et comprendre une règle de détection.",
        "links": [
          {
            "title": "Wazuh",
            "url": "https://wazuh.com/"
          },
          {
            "title": "CyberDefenders",
            "url": "https://cyberdefenders.org/blue-team-labs/"
          }
        ]
      },
      {
        "title": "Investigation",
        "goal": "Écrire une chronologie de l'incident et ses indicateurs.",
        "links": [
          {
            "title": "CyberDefenders - Labs",
            "url": "https://cyberdefenders.org/blue-team-labs/"
          }
        ]
      }
    ]
  },
  {
    "id": "dfir",
    "title": "DFIR / Forensic",
    "desc": "Analyser les traces d'une activité et reconstituer les faits.",
    "sections": [
      {
        "title": "Fichiers et artefacts",
        "goal": "Lire les métadonnées et identifier les fichiers utiles.",
        "links": [
          {
            "title": "picoCTF",
            "url": "https://picoctf.org/"
          }
        ]
      },
      {
        "title": "Réseau",
        "goal": "Étudier une capture PCAP pour retrouver les événements.",
        "links": [
          {
            "title": "Wireshark - Samples",
            "url": "https://wiki.wireshark.org/SampleCaptures"
          }
        ]
      },
      {
        "title": "Disques et mémoire",
        "goal": "Pratiquer sur des images fournies par des labs.",
        "links": [
          {
            "title": "CyberDefenders",
            "url": "https://cyberdefenders.org/blue-team-labs/"
          }
        ]
      },
      {
        "title": "Rapport",
        "goal": "Établir une chronologie vérifiable et un rapport d'investigation.",
        "links": [
          {
            "title": "CyberDefenders - Labs",
            "url": "https://cyberdefenders.org/blue-team-labs/"
          }
        ]
      }
    ]
  },
  {
    "id": "ad",
    "title": "Active Directory",
    "desc": "Comprendre les domaines Windows et s'entraîner sur GOAD.",
    "sections": [
      {
        "title": "Bases AD",
        "goal": "Utilisateurs, groupes, domaines, DNS et Kerberos.",
        "links": [
          {
            "title": "Microsoft Learn - Commandes Windows",
            "url": "https://learn.microsoft.com/fr-fr/windows-server/administration/windows-commands/windows-commands"
          }
        ]
      },
      {
        "title": "MINILAB",
        "goal": "Commencer avec le plus petit environnement GOAD isolé.",
        "links": [
          {
            "title": "GOAD MINILAB",
            "url": "https://orange-cyberdefense.github.io/GOAD/labs/MINILAB/"
          }
        ]
      },
      {
        "title": "GOAD-Light",
        "goal": "Étudier les mauvaises configurations dans un lab plus complet.",
        "links": [
          {
            "title": "GOAD-Light",
            "url": "https://orange-cyberdefense.github.io/GOAD/labs/GOAD-Light/"
          }
        ]
      },
      {
        "title": "GOAD complet",
        "goal": "Documenter les domaines, trusts et constats dans le lab complet.",
        "links": [
          {
            "title": "GOAD",
            "url": "https://github.com/Orange-Cyberdefense/GOAD"
          }
        ]
      }
    ]
  },
  {
    "id": "cloud",
    "title": "Cloud / Conteneurs",
    "desc": "Étudier les identités, les environnements cloud et Kubernetes.",
    "sections": [
      {
        "title": "Cloud & IAM",
        "goal": "Comprendre les comptes, rôles et permissions.",
        "links": [
          {
            "title": "Microsoft Learn",
            "url": "https://learn.microsoft.com/training/topics/sci"
          }
        ]
      },
      {
        "title": "Docker & secrets",
        "goal": "Déployer un petit lab de gestion de secrets.",
        "links": [
          {
            "title": "OWASP WrongSecrets",
            "url": "https://github.com/OWASP/wrongsecrets"
          }
        ]
      },
      {
        "title": "Kubernetes",
        "goal": "Examiner des mauvaises configurations sur un lab local.",
        "links": [
          {
            "title": "Kubernetes Goat",
            "url": "https://github.com/madhuakula/kubernetes-goat"
          }
        ]
      },
      {
        "title": "Scénarios avancés",
        "goal": "Explorer les scénarios CloudGoat après avoir étudié leurs coûts.",
        "links": [
          {
            "title": "CloudGoat",
            "url": "https://github.com/RhinoSecurityLabs/cloudgoat"
          }
        ]
      }
    ]
  },
  {
    "id": "reverse",
    "title": "Reverse Engineering",
    "desc": "Comprendre et analyser le fonctionnement des programmes.",
    "sections": [
      {
        "title": "Bases machine",
        "goal": "Apprendre les registres, instructions et exécutables.",
        "links": [
          {
            "title": "OpenSecurityTraining2",
            "url": "https://opensecuritytraining.info/"
          }
        ]
      },
      {
        "title": "Reverse débutant",
        "goal": "Inspecter le comportement d'un binaire simple.",
        "links": [
          {
            "title": "Malware Unicorn RE101",
            "url": "https://malwareunicorn.org/workshops/re101"
          }
        ]
      },
      {
        "title": "Analyse avancée",
        "goal": "Approfondir l'analyse et les outils de reverse.",
        "links": [
          {
            "title": "Malware Unicorn RE102",
            "url": "https://malwareunicorn.org/workshops/re102"
          }
        ]
      },
      {
        "title": "Étude complète",
        "goal": "Documenter ce que fait un programme de laboratoire.",
        "links": [
          {
            "title": "OpenSecurityTraining2",
            "url": "https://opensecuritytraining.info/"
          }
        ]
      }
    ]
  },
  {
    "id": "crypto",
    "title": "Cryptographie",
    "desc": "Comprendre chiffrement, hash et protocoles par la pratique.",
    "sections": [
      {
        "title": "Encodages",
        "goal": "Distinguer encodage, chiffrement et empreinte.",
        "links": [
          {
            "title": "CyberChef",
            "url": "https://gchq.github.io/CyberChef/"
          }
        ]
      },
      {
        "title": "Challenges",
        "goal": "Résoudre les exercices du parcours d'introduction.",
        "links": [
          {
            "title": "CryptoHack",
            "url": "https://cryptohack.org/courses/intro/course_details/"
          }
        ]
      },
      {
        "title": "Cryptographie pratique",
        "goal": "Établir les propriétés d'un chiffrement à partir de problèmes.",
        "links": [
          {
            "title": "Cryptopals",
            "url": "https://cryptopals.com/"
          }
        ]
      },
      {
        "title": "Projet",
        "goal": "Présenter et expliquer un ensemble de challenges.",
        "links": [
          {
            "title": "CryptoHack",
            "url": "https://cryptohack.org/"
          }
        ]
      }
    ]
  },
  {
    "id": "ot",
    "title": "OT / ICS",
    "desc": "Découvrir les systèmes industriels et les enjeux de sécurité.",
    "sections": [
      {
        "title": "Architecture OT",
        "goal": "Identifier les composants d'une installation industrielle.",
        "links": [
          {
            "title": "CISA ICS",
            "url": "https://www.cisa.gov/topics/industrial-control-systems"
          }
        ]
      },
      {
        "title": "Réseaux et protocoles",
        "goal": "Comprendre les différences entre réseau IT et réseau industriel.",
        "links": [
          {
            "title": "CISA ICS",
            "url": "https://www.cisa.gov/topics/industrial-control-systems"
          }
        ]
      },
      {
        "title": "Sécurité industrielle",
        "goal": "Explorer les mécanismes de segmentation et de surveillance.",
        "links": [
          {
            "title": "CISA ICS",
            "url": "https://www.cisa.gov/topics/industrial-control-systems"
          }
        ]
      },
      {
        "title": "Étude de cas",
        "goal": "Documenter une architecture simulée, jamais une installation réelle.",
        "links": [
          {
            "title": "CISA ICS",
            "url": "https://www.cisa.gov/topics/industrial-control-systems"
          }
        ]
      }
    ]
  }
];

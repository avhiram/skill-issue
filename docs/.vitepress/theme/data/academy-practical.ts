// Academy - roadmap orientée pratique. Les labs vulnérables doivent rester isolés.
export const academyLevels = [
  {
    "id": 0,
    "title": "Prendre en main le terminal",
    "desc": "Savoir manipuler des fichiers, se déplacer dans Linux et utiliser SSH.",
    "validate": "Tu peux naviguer, lire un fichier et te connecter à un serveur SSH sans suivre un corrigé.",
    "required": 2,
    "tasks": [
      {
        "id": "l0-1",
        "name": "Linux Luminarium",
        "provider": "pwn.college",
        "url": "https://pwn.college/linux-luminarium/",
        "work": "Effectuer les premiers exercices sur le terminal, les répertoires et les fichiers.",
        "access": "Gratuit"
      },
      {
        "id": "l0-2",
        "name": "Bandit - niveaux 0 à 5",
        "provider": "OverTheWire",
        "url": "https://overthewire.org/wargames/bandit/",
        "work": "Passer les niveaux 0 à 5 en SSH avec les commandes Linux.",
        "access": "Gratuit"
      }
    ]
  },
  {
    "id": 1,
    "title": "Linux et réseaux",
    "desc": "Comprendre permissions, services, IP, DNS, TCP et captures réseau.",
    "validate": "Tu sais retrouver un service dans un PCAP, manipuler des permissions et utiliser grep/find.",
    "required": 2,
    "tasks": [
      {
        "id": "l1-1",
        "name": "Bandit - niveaux 6 à 15",
        "provider": "OverTheWire",
        "url": "https://overthewire.org/wargames/bandit/",
        "work": "Résoudre les niveaux suivants avec grep, find, permissions et encodages.",
        "access": "Gratuit"
      },
      {
        "id": "l1-2",
        "name": "Wireshark - exemples PCAP",
        "provider": "Wireshark",
        "url": "https://wiki.wireshark.org/SampleCaptures",
        "work": "Ouvrir une capture et identifier des échanges DNS et TCP avec des filtres.",
        "access": "Gratuit"
      },
      {
        "id": "l1-3",
        "name": "Linux Luminarium - processus",
        "provider": "pwn.college",
        "url": "https://pwn.college/linux-luminarium/",
        "work": "Pratiquer les modules sur les processus, permissions et variables d'environnement.",
        "access": "Gratuit"
      }
    ]
  },
  {
    "id": 2,
    "title": "Python, Web et CTF",
    "desc": "Écrire du code simple, comprendre HTTP et résoudre des défis de découverte.",
    "validate": "Tu as écrit un petit script Python, identifié les éléments d'une requête Web et résolu plusieurs défis.",
    "required": 2,
    "tasks": [
      {
        "id": "l2-1",
        "name": "Python - exercices pratiques",
        "provider": "freeCodeCamp",
        "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
        "work": "Coder plusieurs exercices et terminer un mini-projet Python.",
        "access": "Gratuit"
      },
      {
        "id": "l2-2",
        "name": "Natas - niveaux 0 à 4",
        "provider": "OverTheWire",
        "url": "https://overthewire.org/wargames/natas/",
        "work": "Résoudre les cinq premiers niveaux en inspectant les pages Web.",
        "access": "Gratuit"
      },
      {
        "id": "l2-3",
        "name": "CryptoHack - Introduction",
        "provider": "CryptoHack",
        "url": "https://cryptohack.org/courses/intro/course_details/",
        "work": "Réaliser les défis d'encodage et de décodage proposés.",
        "access": "Gratuit"
      }
    ]
  },
  {
    "id": 3,
    "title": "Vulnérabilités et premiers labs",
    "desc": "Observer de vraies requêtes, reconnaître des failles et tester dans des labs dédiés.",
    "validate": "Tu as terminé deux labs Web et tu peux expliquer ce que tu as modifié dans les requêtes.",
    "required": 2,
    "tasks": [
      {
        "id": "l3-1",
        "name": "Path Traversal - lab débutant",
        "provider": "PortSwigger",
        "url": "https://portswigger.net/web-security/file-path-traversal/lab-simple",
        "work": "Résoudre le lab Apprentice en observant les paramètres et réponses HTTP.",
        "access": "Gratuit"
      },
      {
        "id": "l3-2",
        "name": "SQL Injection - lab débutant",
        "provider": "PortSwigger",
        "url": "https://portswigger.net/web-security/sql-injection/lab-retrieve-hidden-data",
        "work": "Résoudre le lab Apprentice et noter la cause de la vulnérabilité.",
        "access": "Gratuit"
      },
      {
        "id": "l3-3",
        "name": "DVWA - premiers défis",
        "provider": "DVWA",
        "url": "https://github.com/digininja/DVWA",
        "work": "Installer le lab localement et pratiquer trois catégories de vulnérabilités.",
        "access": "Open source"
      }
    ]
  },
  {
    "id": 4,
    "title": "Autonomie et premier projet",
    "desc": "Choisir un lab complet, tenir des notes et expliquer ce qui a fonctionné.",
    "validate": "Tu as terminé au moins un défi en autonomie et rédigé un compte rendu court : objectif, méthode et résultat.",
    "required": 1,
    "tasks": [
      {
        "id": "l4-1",
        "name": "OWASP Juice Shop",
        "provider": "OWASP",
        "url": "https://github.com/juice-shop/juice-shop",
        "work": "Déployer localement l'application et résoudre au moins cinq challenges.",
        "access": "Open source"
      },
      {
        "id": "l4-2",
        "name": "picoCTF / CyLab",
        "provider": "Carnegie Mellon",
        "url": "https://picoctf.org/",
        "work": "Résoudre trois CTF dans trois domaines différents et documenter les résultats.",
        "access": "Gratuit"
      },
      {
        "id": "l4-3",
        "name": "TryHackMe - Free Rooms",
        "provider": "TryHackMe",
        "url": "https://tryhackme.com/free-rooms",
        "work": "Choisir une room gratuite pratique et la terminer sans guide complet.",
        "access": "Freemium",
        "note": "Utiliser exclusivement les rooms gratuites."
      }
    ]
  }
];
export const academyOpenSource = [
  {
    "title": "DVWA",
    "category": "web",
    "difficulty": "Débutant",
    "where": "Local",
    "cost": "Code gratuit",
    "url": "https://github.com/digininja/DVWA",
    "desc": "Application Web vulnérable en PHP. SQLi, XSS et authentification.",
    "task": "Installer puis terminer trois exercices en difficulté Low.",
    "prereq": "Docker ou pile PHP/MySQL"
  },
  {
    "title": "OWASP Juice Shop",
    "category": "web",
    "difficulty": "Débutant",
    "where": "Local",
    "cost": "Code gratuit",
    "url": "https://github.com/juice-shop/juice-shop",
    "desc": "Fausse boutique contenant de nombreuses failles Web et API.",
    "task": "Déployer et terminer cinq challenges faciles.",
    "prereq": "Docker ou Node.js"
  },
  {
    "title": "OWASP WebGoat",
    "category": "web",
    "difficulty": "Débutant",
    "where": "Local",
    "cost": "Code gratuit",
    "url": "https://github.com/WebGoat/WebGoat",
    "desc": "Leçons interactives sur les vulnérabilités des applications.",
    "task": "Terminer une leçon injection et une leçon authentification.",
    "prereq": "Docker ou Java"
  },
  {
    "title": "OWASP crAPI",
    "category": "web",
    "difficulty": "Intermédiaire",
    "where": "Local",
    "cost": "Code gratuit",
    "url": "https://github.com/OWASP/crAPI",
    "desc": "API volontairement vulnérable pour pratiquer l'OWASP API Security.",
    "task": "Installer la stack, intercepter les appels API et résoudre un challenge.",
    "prereq": "Docker Compose, HTTP et JSON"
  },
  {
    "title": "Vulhub",
    "category": "infra",
    "difficulty": "Intermédiaire",
    "where": "Local",
    "cost": "Code gratuit",
    "url": "https://github.com/vulhub/vulhub",
    "desc": "Bibliothèque de services volontairement vulnérables sous Docker.",
    "task": "Choisir un environnement et analyser le service et sa vulnérabilité.",
    "prereq": "Docker Compose et réseau"
  },
  {
    "title": "Metasploitable3",
    "category": "infra",
    "difficulty": "Intermédiaire",
    "where": "Local",
    "cost": "Code gratuit",
    "url": "https://github.com/rapid7/metasploitable3",
    "desc": "Machine virtuelle vulnérable pour pratiquer reconnaissance et pentest.",
    "task": "Déployer une VM isolée et inventorier les services exposés.",
    "prereq": "Virtualisation et machine suffisamment puissante"
  },
  {
    "title": "GOAD - MINILAB",
    "category": "ad",
    "difficulty": "Intermédiaire",
    "where": "Local",
    "cost": "Code gratuit",
    "url": "https://orange-cyberdefense.github.io/GOAD/labs/MINILAB/",
    "desc": "Introduction pratique à un domaine Active Directory avec deux VM.",
    "task": "Déployer MINILAB puis identifier domaine, utilisateurs et services.",
    "prereq": "Windows AD, réseau et virtualisation",
    "note": "Commencer ici avant GOAD-Light."
  },
  {
    "title": "GOAD-Light",
    "category": "ad",
    "difficulty": "Avancé",
    "where": "Local",
    "cost": "Code gratuit",
    "url": "https://orange-cyberdefense.github.io/GOAD/labs/GOAD-Light/",
    "desc": "Environnement AD réduit pour progresser vers un lab plus complet.",
    "task": "Déployer le lab et documenter l'architecture et les mauvaises configurations.",
    "prereq": "AD, Kerberos, Windows Server, virtualisation"
  },
  {
    "title": "GOAD - complet",
    "category": "ad",
    "difficulty": "Avancé",
    "where": "Local",
    "cost": "Code gratuit",
    "url": "https://github.com/Orange-Cyberdefense/GOAD",
    "desc": "Plusieurs domaines et forêts AD vulnérables conçus pour le pentest.",
    "task": "Déployer le lab complet et produire une cartographie des domaines et trusts.",
    "prereq": "AD, virtualisation, RAM importante",
    "note": "Ne pas exposer les VM vulnérables à Internet."
  },
  {
    "title": "OWASP WrongSecrets",
    "category": "cloud",
    "difficulty": "Intermédiaire",
    "where": "Local",
    "cost": "Code gratuit",
    "url": "https://github.com/OWASP/wrongsecrets",
    "desc": "Exercices sur les secrets et leur exposition dans les applications.",
    "task": "Déployer le lab et identifier les secrets de plusieurs scénarios.",
    "prereq": "Docker et notions de secrets applicatifs"
  },
  {
    "title": "Kubernetes Goat",
    "category": "cloud",
    "difficulty": "Avancé",
    "where": "Local",
    "cost": "Code gratuit",
    "url": "https://github.com/madhuakula/kubernetes-goat",
    "desc": "Environnements Kubernetes volontairement vulnérables.",
    "task": "Déployer un cluster local et étudier une configuration vulnérable.",
    "prereq": "Docker, Kubernetes et ressources locales"
  },
  {
    "title": "CloudGoat",
    "category": "cloud",
    "difficulty": "Avancé",
    "where": "AWS",
    "cost": "Cloud payant possible",
    "url": "https://github.com/RhinoSecurityLabs/cloudgoat",
    "desc": "Scénarios AWS volontairement vulnérables à déployer dans son propre compte.",
    "task": "Examiner un scénario et son coût avant toute mise en place.",
    "prereq": "Compte AWS, IAM, Terraform et maîtrise des coûts",
    "note": "Le code est ouvert, mais les ressources AWS peuvent être facturées."
  }
];
export const academyOnlineLabs = [
  {
    "title": "PortSwigger - labs Web",
    "url": "https://portswigger.net/web-security/all-labs",
    "info": "Gratuit - labs directement dans le navigateur"
  },
  {
    "title": "TryHackMe - Free Rooms",
    "url": "https://tryhackme.com/free-rooms",
    "info": "Freemium - sélectionner les rooms gratuites"
  },
  {
    "title": "Hack The Box - débuter",
    "url": "https://www.hackthebox.com/hacker/htb-for-beginners",
    "info": "Freemium - modules gratuits et limites de crédits"
  },
  {
    "title": "Root-Me - challenges",
    "url": "https://www.root-me.org/",
    "info": "Challenges publics, conditions à vérifier par défi"
  },
  {
    "title": "LetsDefend - challenges",
    "url": "https://app.letsdefend.io/challenge",
    "info": "Freemium - choisir les challenges étiquetés Free"
  },
  {
    "title": "Blue Team Labs Online",
    "url": "https://blueteamlabs.online/",
    "info": "Freemium - temps de lab gratuit limité"
  }
];

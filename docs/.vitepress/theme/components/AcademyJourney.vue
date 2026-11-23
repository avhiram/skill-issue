<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { resources } from '../data/academy-organized'
import { masteryResources } from '../data/academy-mastery'
import { academyLevels, academyExtraResources, academyAssignments } from '../data/academy-unified'

type Resource = {
  id: string
  title: string
  url: string
  category?: string
  type?: string
  description?: string
  access?: string
  level?: number | null
  routeLevel?: string
}
type AssignedResource = Resource & { routeLevel: string }
type Level = {
  id: string
  title: string
  intro: string
  learn: readonly string[]
  exercise: string
  ready: string
}

const sections = [
  {
    "id": "premiers-pas",
    "title": "Fondamentaux informatiques",
    "summary": "Comprendre son ordinateur, le réseau et les premiers outils.",
    "levels": [
      "environment",
      "network-basics",
      "network-practice"
    ]
  },
  {
    "id": "linux-windows",
    "title": "Sécurité des systèmes",
    "summary": "Apprendre les commandes, les fichiers, les comptes et les permissions.",
    "levels": [
      "linux-basics",
      "linux-admin",
      "windows-basics",
      "powershell"
    ]
  },
  {
    "id": "code-et-web",
    "title": "Programmation et Web",
    "summary": "Écrire ses premiers scripts et comprendre les applications Web.",
    "levels": [
      "python-basics",
      "scripting",
      "web-basics",
      "web-api"
    ]
  },
  {
    "id": "notions-securite",
    "title": "Principes de sécurité de l'information",
    "summary": "Acquérir les réflexes de sécurité, découvrir la cryptographie et pratiquer l'OSINT.",
    "levels": [
      "security-basics",
      "crypto",
      "osint-recon",
      "osint-practice"
    ]
  },
  {
    "id": "premiers-labs",
    "title": "Sécurité des applications Web",
    "summary": "Découvrir les outils, les failles Web et les premiers labs autorisés.",
    "levels": [
      "scanning",
      "web-security",
      "web-labs",
      "local-labs",
      "bug-bounty",
      "ctf-beginner",
      "ctf-intermediate",
      "pentest-system"
    ]
  },
  {
    "id": "bonus-windows",
    "title": "Protection des postes Windows",
    "summary": "Consolider ses bases sur des environnements Windows dédiés à la pratique.",
    "levels": [
      "bonus-windows-labs"
    ]
  },
  {
    "id": "active-directory-red-team",
    "title": "Sécurité offensive",
    "summary": "Passer des domaines Windows aux labs GOAD, puis aux environnements Red Team.",
    "levels": [
      "ad-intro",
      "ad-minilab",
      "ad-light",
      "ad-full",
      "c2",
      "red-advanced"
    ]
  },
  {
    "id": "blue-team",
    "title": "Sécurité défensive",
    "summary": "Comprendre les journaux, la détection et l'analyse d'incidents.",
    "levels": [
      "blue-logs",
      "blue-siem",
      "blue-threat"
    ]
  },
  {
    "id": "forensic-reverse",
    "title": "Digital Forensics et analyse de malware",
    "summary": "Étudier les captures réseau, la mémoire, les binaires et les traces.",
    "levels": [
      "dfir-network",
      "dfir-host",
      "reverse",
      "malware"
    ]
  },
  {
    "id": "cloud-et-specialites",
    "title": "Cloud Security et domaines spécialisés",
    "summary": "Explorer le Cloud, les conteneurs, le mobile, l'IoT, l'OT et la conformité.",
    "levels": [
      "cloud-foundations",
      "cloud-security",
      "containers",
      "mobile",
      "iot",
      "ot",
      "grc"
    ]
  },
  {
    "id": "challenges-avances",
    "title": "Capture The Flag (CTF)",
    "summary": "Appliquer sa méthode sur des défis complexes, jusqu'aux rooms très difficiles.",
    "levels": [
      "ctf-advanced",
      "extremely-hard-rooms"
    ]
  },
  {
    "id": "veilles-certifications",
    "title": "Développement professionnel",
    "summary": "Suivre les vulnérabilités, préparer ses examens et rejoindre les communautés.",
    "levels": [
      "research",
      "certifications",
      "community"
    ]
  },
  {
    "id": "projet-final",
    "title": "Projet final",
    "summary": "Rassembler ses acquis dans un lab complet et rédiger son rapport.",
    "levels": [
      "final-project"
    ]
  }
] as const

const supplementary: Level[] = [
  {
    id: 'bonus-windows-labs',
    title: "Windows : s'entraîner sur des machines",
    intro: 'Applique les fondamentaux Windows, Active Directory et pentest sur des rooms dédiées.',
    learn: ['Analyse les services Windows, les permissions et les configurations du lab.'],
    exercise: 'Résoudre deux rooms Windows puis consigner les commandes, résultats et corrections.',
    ready: 'Tu peux expliquer le cheminement d’une room Windows sans solution préremplie.'
  },
  {
    id: 'extremely-hard-rooms',
    title: 'CTF : réussir des rooms très difficiles',
    intro: 'Consolide les acquis sur des environnements complexes, après les labs précédents.',
    learn: ['Prépare une méthodologie, une prise de notes et un rapport reproductible.'],
    exercise: 'Résoudre une room difficile sans write-up, dans le cadre du lab proposé.',
    ready: 'Tu sais justifier chaque étape et documenter une résolution complète.'
  }
]

const allLevels: Level[] = [...academyLevels, ...supplementary]
const byId = new Map(allLevels.map(level => [level.id, level]))
const orderedLevels: Level[] = sections.flatMap(section => section.levels.map(id => byId.get(id)!).filter(Boolean))
const indexOf = new Map(orderedLevels.map((level, i) => [level.id, i + 1]))
const normalizeUrl = (value: string) => value.trim().replace(/^http:/i, 'https:').replace(/^https:\/\/www\./i, 'https://').replace(/\/+$/, '').toLowerCase()
const simplify = (value: string) => value.toLocaleLowerCase('fr').normalize('NFD').replace(/[\u0300-\u036f]/g, '')

const windowsRooms = new Set(['retro', 'blue print', 'anthem', 'relevant'])
const hardRooms = new Set([
  'ra', 'cct2019', 'theseus', 'ironcorp', 'carpe diem 1', 'borderlands',
  'jeff', 'year of the owl', 'anonymous playground', 'enterprize',
  'racetrack bank', 'python playground'
])
const bonusLabs = new Set(['smag grotto', 'dogcat', 'break out the cage', 'lian yu'])
const routeAdjustments: Record<string, string> = {
  'insecure kubernetes': 'containers',
  'the great escape (docker)': 'containers',
  'solr exploiting log4j': 'web-labs',
  'spring4shell': 'web-labs',
  'most recent threats': 'research',
  'post exploitation basics': 'red-advanced',
  'buffer overflow prep': 'ctf-advanced'
}
const localLabUrls = new Set([
  'https://github.com/digininja/DVWA',
  'https://github.com/juice-shop/juice-shop',
  'https://owasp.org/www-project-juice-shop/',
  'https://github.com/WebGoat/WebGoat',
  'https://owasp.org/www-project-webgoat/',
  'https://www.vulnhub.com/',
  'https://github.com/rapid7/metasploitable3'
].map(normalizeUrl))
const osintToolUrls = new Set([
  'https://github.com/sherlock-project/sherlock',
  'https://github.com/laramies/theHarvester',
  'https://github.com/soxoj/maigret',
  'https://github.com/megadose/holehe',
  'https://github.com/jivoi/awesome-osint'
].map(normalizeUrl))
const sourceItems: Resource[] = [...resources, ...masteryResources, ...academyExtraResources] as Resource[]
const resourceMap = new Map<string, AssignedResource>()
for (const item of sourceItems) {
  // Retirer les ressources Cisco, NetAcad et Packet Tracer, pas les cours réseau neutres.
  if (/cisco|netacad|packet.?tracer/i.test(item.title + ' ' + item.url)) continue
  const key = normalizeUrl(item.url)
  if (resourceMap.has(key)) continue
  const title = simplify(item.title.trim())
  let routeLevel = item.routeLevel || academyAssignments[item.id] || 'research'
  if (osintToolUrls.has(key)) routeLevel = 'osint-recon'
  if (localLabUrls.has(key)) routeLevel = 'local-labs'
  else if (key === normalizeUrl('https://tryhackme.com/free-rooms')) routeLevel = 'ctf-intermediate'
  else if (windowsRooms.has(title)) routeLevel = 'bonus-windows-labs'
  else if (hardRooms.has(title)) routeLevel = 'extremely-hard-rooms'
  else if (bonusLabs.has(title)) routeLevel = 'ctf-intermediate'
  else if (routeAdjustments[title]) routeLevel = routeAdjustments[title]
  if (!byId.has(routeLevel)) routeLevel = 'research'
  resourceMap.set(key, { ...item, routeLevel })
}
const catalog = [...resourceMap.values()]
const linksByLevel = new Map<string, AssignedResource[]>()
for (const level of orderedLevels) linksByLevel.set(level.id, [])
for (const item of catalog) linksByLevel.get(item.routeLevel)?.push(item)
// Mettre les ressources choisies pour démarrer avant les références longues et les outils.
const featuredByLevel = new Map(academyLevels.map(level => [
  level.id, level.featured.map(normalizeUrl)
]))
for (const [id, links] of linksByLevel) {
  const featured = featuredByLevel.get(id) || []
  links.sort((a, b) => {
    const aOrder = featured.indexOf(normalizeUrl(a.url))
    const bOrder = featured.indexOf(normalizeUrl(b.url))
    if (aOrder !== -1 && bOrder !== -1) return aOrder - bOrder
    if (aOrder !== -1) return -1
    if (bOrder !== -1) return 1
    const aIntro = /intro|début|beginner|fundamental|basics|premier|getting started/i.test(a.title)
    const bIntro = /intro|début|beginner|fundamental|basics|premier|getting started/i.test(b.title)
    if (aIntro !== bIntro) return aIntro ? -1 : 1
    return 0
  })
}

const manualDescriptions: Record<string, string> = {
  'sherlock': 'Recherche de comptes publics à partir d’un pseudonyme.',
  'theharvester': 'Collecte de sous-domaines et d’informations publiques sur un domaine.',
  'maigret - recherche de profils': 'Recherche de profils publics avec rapports.',
  'holehe - recherche par e-mail': 'Recherche d’indices d’inscription liés à une adresse e-mail.',
  'awesome osint - repertoire d’outils': 'Catalogue d’outils et ressources OSINT.',
  'threat intelligence 101': 'Introduction au renseignement sur les cybermenaces.',
  'threat intelligence tools': 'Découverte des outils d’OSINT et de Threat Intelligence.',
  'martryohka doll': 'Challenge d’analyse de fichiers pour débuter.',
  'the glory of the garden': 'Challenge débutant d’analyse d’image.',
  'packets primer': 'Première analyse de paquets réseau.',
  'wireshark doo doo doo': 'Challenge débutant d’analyse de paquets.',
  'wireshark two two two': 'Challenge débutant d’analyse réseau.',
  'trivial flag transfer protocol': 'Challenge d’analyse de trafic réseau.',
  'what lies within': 'Challenge de décodage et d’analyse.',
  'illumination': 'Challenge forensic de difficulté intermédiaire.',
  'emo': 'Challenge forensic de difficulté intermédiaire.',
  'obsecure': 'Challenge forensic de difficulté intermédiaire.',
  'intel101 challenge': 'Challenge de Threat Intelligence intermédiaire.',
  'sleuthkit intro': 'Premiers exercices d’analyse forensique de disque.',
  'reminiscent': 'Challenge forensique sur une image disque.',
  'hunter - windows disk image forensics': 'Analyse forensique d’une image disque Windows.',
  'spotlight - mac disk image forensics': 'Analyse forensique d’une image disque macOS.',
  'ulysses - linux disk image forensics': 'Analyse forensique d’une image disque Linux.',
  'banking troubles - windows memory image forensics': 'Analyse forensique de mémoire Windows.',
  'detect log4j': 'Investigation sur la vulnérabilité Log4j.',
  'nmap,curl and netcat': 'Prise en main des outils de diagnostic réseau.',
  'linux fundamentals 1': 'Premières commandes Linux dans un terminal interactif.',
  'linux fundamentals 2': 'Poursuite des fondamentaux Linux.',
  'linux fundamentals 3': 'Approfondissement des commandes Linux.',
  'red team engagements': 'Introduction à la préparation d’un engagement Red Team.',
  'cobalt strike - manuel officiel': 'Documentation officielle du logiciel Cobalt Strike.',
  'sliver - framework c2 open source': 'Framework C2 open source pour un environnement de lab.',
  'caldera - émulation et lab c2': 'Plateforme open source d’émulation adversaire.',
  'letsdefend - challenges gratuits': 'Challenges de SOC, avec une sélection accessible gratuitement. Le catalogue migre vers Hack The Box.',
  'dvwa - premiers défis': 'Application Web vulnérable pour pratiquer localement les failles courantes.',
  'owasp juice shop': 'Application Web volontairement vulnérable, adaptée aux exercices locaux.',
  'owasp webgoat': 'Environnement Web pédagogique à installer dans un lab isolé.',
  'vulnhub': 'Machines virtuelles vulnérables téléchargeables pour un lab personnel.',
  'cryptopals': 'Défis progressifs de cryptographie qui nécessitent de savoir coder.',
  'root-me - challenges': 'Challenges de sécurité organisés par domaine et difficulté.'
}
const topicLabels: Record<string, string> = {
  fondamentaux: 'bases informatiques',
  systemes: 'Linux et Windows',
  reseau: 'réseau et protocoles',
  programmation: 'programmation et scripting',
  web: 'sécurité Web et API',
  crypto: 'cryptographie',
  osint: 'recherche OSINT',
  red: 'pentest et Red Team',
  ad: 'Active Directory',
  ctf: 'CTF et challenges',
  blue: 'Blue Team et SOC',
  dfir: 'investigation forensic',
  reverse: 'reverse engineering',
  cloud: 'sécurité cloud',
  mobile: 'sécurité mobile',
  iot: 'sécurité IoT',
  ot: 'sécurité OT/ICS',
  grc: 'gestion des risques et conformité',
  veille: 'veille cybersécurité',
  carriere: 'formations et certifications',
  communaute: 'communautés cybersécurité',
  formations: 'ressources de formation',
  outils: 'outils de sécurité'
}
const minimalTitles: Record<string, string> = {
  "letsdefend - conditions et migration hack the box": "LetsDefend - évolution des labs",
  "ine security - offres et acces": "INE Security - offres",
  "offsec - acces aux labs gratuits": "OffSec - labs gratuits",
  "offsec - pen-103 kali linux revealed (acces gratuit)": "OffSec - PEN-103 Kali Linux Revealed"
}
function displayTitle(item: AssignedResource) { return minimalTitles[simplify(item.title.trim())] || item.title }
const minimalDescriptions: Record<string, string> = {
  "root-me - web serveur": "Challenges Web sur la sécurité côté serveur.",
  "root-me - web client": "Challenges Web sur la sécurité côté navigateur.",
  "bugcrowd - liste des programmes publics": "Répertoire de programmes publics de Bug Bounty.",
  "osint-fr - challenges ctf": "Challenges OSINT proposés par la communauté OSINT-FR.",
  "letsdefend - environnement soc": "Labs et alertes pour s'entraîner à l'analyse SOC.",
  "letsdefend - conditions et migration hack the box": "Informations sur l'évolution des labs LetsDefend.",
  "hack the box - sherlocks (investigation)": "Challenges d'enquête et d'analyse d'incident.",
  "ine security - catalogue complet des cours cyber": "Catalogue de formations en offensive, SOC, Cloud, DFIR et GRC.",
  "ine security - offres et acces": "Présentation des offres de formation INE.",
  "open source security testing methodology manual": "Méthodologie de test et d'audit de sécurité.",
  "google skills - parcours cloud": "Formations et exercices sur Google Cloud.",
  "offsec - acces aux labs gratuits": "Présentation des labs Proving Grounds Play et du cours PEN-103."
}
function describe(item: AssignedResource) {
  const concise = minimalDescriptions[simplify(item.title.trim())]
  if (concise) return concise
  const known = manualDescriptions[simplify(item.title.trim())]
  if (known) return known
  if (item.description?.trim()) return item.description.trim()
  const url = item.url.toLowerCase()
  if (/tryhackme\.com\/room\//.test(url)) return 'Room pratique TryHackMe.'
  if (/root-me\.org/.test(url)) return 'Challenges pratiques Root-Me.'
  if (/picoctf\.org/.test(url)) return 'Challenges pratiques picoCTF.'
  if (/hackthebox\.com|hackthebox\.eu/.test(url)) return 'Labs et exercices Hack The Box.'
  if (/portswigger\.net\/web-security/.test(url)) return 'Cours et labs pratiques sur la sécurité Web.'
  if (/github\.com\//.test(url)) return 'Dépôt GitHub avec documentation ou outils techniques.'
  if (/learn\.microsoft\.com/.test(url)) return 'Documentation technique Microsoft.'
  if (/youtube\.com|youtu\.be/.test(url)) return 'Vidéo ou formation technique.'
  if (/sans\.org/.test(url)) return 'Présentation d’une formation SANS.'
  if (item.type?.trim()) return item.type.trim() + ' - ' + (topicLabels[item.category || ''] || 'cybersécurité') + '.'
  return 'Ressource sur ' + (topicLabels[item.category || ''] || 'la cybersécurité') + '.'
}
function levelLinks(id: string): AssignedResource[] { return linksByLevel.get(id) || [] }
function levelsIn(section: typeof sections[number]) {
  return section.levels.map(id => byId.get(id)!).filter(Boolean)
}
function numberFor(id: string) { return indexOf.get(id) || 0 }

// Intitulés courts repris des thèmes du README Cybersecurity Mastery Roadmap.
const levelTitles: Record<string, string> = {
  "environment": "Systèmes d'exploitation",
  "network-basics": "Bases des réseaux",
  "network-practice": "Protocoles réseau",
  "linux-basics": "Fondamentaux Linux",
  "linux-admin": "Sécurité Linux",
  "windows-basics": "Fondamentaux Windows",
  "powershell": "PowerShell",
  "python-basics": "Python",
  "scripting": "Scripting",
  "web-basics": "Fondamentaux du Web",
  "web-api": "Sécurité des API",
  "security-basics": "Principes de sécurité",
  "crypto": "Cryptographie",
  "osint-recon": "Reconnaissance et OSINT",
  "osint-practice": "Pratique OSINT",
  "scanning": "Scan de vulnérabilités",
  "web-security": "OWASP Top 10",
  "web-labs": "Pentest Web",
  "local-labs": "Labs et environnements pratiques",
  "bug-bounty": "Bug Bounty",
  "ctf-beginner": "CTF débutant",
  "ctf-intermediate": "CTF intermédiaire",
  "pentest-system": "Méthodologie de pentest",
  "bonus-windows-labs": "Labs Windows",
  "ad-intro": "Active Directory",
  "ad-minilab": "GOAD - MINILAB",
  "ad-light": "GOAD - GOAD-Light",
  "ad-full": "GOAD",
  "c2": "Frameworks C2",
  "red-advanced": "Red Team",
  "blue-logs": "Security Operations Center (SOC)",
  "blue-siem": "SIEM et détection",
  "blue-threat": "Réponse à incident",
  "dfir-network": "Forensic réseau",
  "dfir-host": "Forensic système",
  "reverse": "Reverse Engineering",
  "malware": "Analyse de malware",
  "cloud-foundations": "Fondamentaux Cloud",
  "cloud-security": "Architecture et sécurité Cloud",
  "containers": "Sécurité des conteneurs",
  "mobile": "Sécurité mobile",
  "iot": "Sécurité IoT",
  "ot": "Sécurité OT / ICS",
  "grc": "Politiques et conformité",
  "ctf-advanced": "CTF avancés",
  "extremely-hard-rooms": "CTF très difficiles",
  "research": "Recherche en sécurité",
  "certifications": "Certifications",
  "community": "Communautés",
  "final-project": "Projet final"
}
function titleFor(id: string, fallback: string) { return levelTitles[id] || fallback }


// Une seule roadmap, avec une sélection de ressources sans achat pour chaque niveau.
// Les offres freemium ou les certifications payantes restent dans la vue complète.
const freeSelections: Record<string, readonly string[]> = {
  "environment": [
    "https://cs50.harvard.edu/x/",
    "https://www.virtualbox.org/"
  ],
  "network-basics": [
    "https://www.cloudflare.com/learning/network-layer/what-is-a-computer-network/",
    "https://www.practicalnetworking.net/"
  ],
  "network-practice": [
    "https://wiki.wireshark.org/SampleCaptures",
    "https://www.wireshark.org/"
  ],
  "linux-basics": [
    "https://overthewire.org/wargames/bandit/",
    "https://linuxjourney.com/"
  ],
  "linux-admin": [
    "https://ubuntu.com/server/docs/",
    "https://help.offsec.com/hc/en-us/articles/360044925031-How-to-get-access-to-free-content-in-the-OffSec-Learning-Library"
  ],
  "windows-basics": [
    "https://learn.microsoft.com/fr-fr/windows-server/administration/windows-commands/windows-commands"
  ],
  "powershell": [
    "https://learn.microsoft.com/en-us/powershell/"
  ],
  "python-basics": [
    "https://cs50.harvard.edu/python/",
    "https://www.freecodecamp.org/learn/scientific-computing-with-python/"
  ],
  "scripting": [
    "https://skills.github.com/",
    "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/"
  ],
  "web-basics": [
    "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview"
  ],
  "web-api": [
    "https://owasp.org/www-project-api-security/"
  ],
  "security-basics": [
    "https://www.nist.gov/cyberframework",
    "https://learn.microsoft.com/en/security"
  ],
  "crypto": [
    "https://cryptohack.org/",
    "https://cryptopals.com/"
  ],
  "osint-recon": [
    "https://osintframework.com/",
    "https://github.com/sherlock-project/sherlock",
    "https://github.com/soxoj/maigret",
    "https://github.com/megadose/holehe",
    "https://github.com/laramies/theHarvester",
    "https://github.com/jivoi/awesome-osint"
  ],
  "osint-practice": [
    "https://bellingcat.gitbook.io/toolkit"
  ],
  "scanning": [
    "https://nmap.org/"
  ],
  "web-security": [
    "https://portswigger.net/web-security/",
    "https://portswigger.net/web-security/learning-paths",
    "https://owasp.org/www-project-top-ten/"
  ],
  "web-labs": [
    "https://portswigger.net/web-security/all-labs",
    "https://www.root-me.org/fr/Challenges/Web-Serveur/",
    "https://www.root-me.org/fr/Challenges/Web-Client/",
    "https://overthewire.org/wargames/natas/"
  ],
  "local-labs": [
    "https://github.com/digininja/DVWA",
    "https://github.com/juice-shop/juice-shop",
    "https://github.com/WebGoat/WebGoat"
  ],
  "bug-bounty": [
    "https://www.hackerone.com/hackers/how-to-start-hacking",
    "https://docs.bugcrowd.com/researchers/participating-in-program/finding-program/"
  ],
  "ctf-beginner": [
    "https://picoctf.org/",
    "https://www.root-me.org/",
    "https://blog.root-me.org/posts/how-to-start/"
  ],
  "ctf-intermediate": [
    "https://help.offsec.com/hc/en-us/articles/360048318472-Getting-Started-with-PG-Play-and-Practice",
    "https://tryhackme.com/free-rooms"
  ],
  "pentest-system": [
    "https://github.com/peass-ng/PEASS-ng"
  ],
  "bonus-windows-labs": [
    "https://learn.microsoft.com/en-us/windows/security/"
  ],
  "ad-intro": [
    "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview"
  ],
  "ad-minilab": [
    "https://orange-cyberdefense.github.io/GOAD/labs/MINILAB/"
  ],
  "ad-light": [
    "https://orange-cyberdefense.github.io/GOAD/labs/GOAD-Light/"
  ],
  "ad-full": [
    "https://github.com/Orange-Cyberdefense/GOAD"
  ],
  "c2": [
    "https://github.com/BishopFox/sliver",
    "https://github.com/apache/caldera",
    "https://github.com/its-a-feature/Mythic"
  ],
  "red-advanced": [
    "https://github.com/redcanaryco/atomic-red-team"
  ],
  "blue-logs": [
    "https://docs.suricata.io/en/latest/quickstart.html"
  ],
  "blue-siem": [
    "https://wazuh.com/",
    "https://github.com/SigmaHQ/sigma"
  ],
  "blue-threat": [
    "https://attack.mitre.org/"
  ],
  "dfir-network": [
    "https://play.picoctf.org/practice/challenge/286?category=4&page=2&solved=0"
  ],
  "dfir-host": [
    "https://github.com/volatilityfoundation/volatility3",
    "https://cloud.google.com/learn/security/mandiant-academy-courses/free-cyber-defense-training"
  ],
  "reverse": [
    "https://opensecuritytraining.info/",
    "https://ghidra-sre.org/"
  ],
  "malware": [
    "https://remnux.org/",
    "https://www.malware-traffic-analysis.net/"
  ],
  "cloud-foundations": [
    "https://learn.microsoft.com/en-us/training/azure/"
  ],
  "cloud-security": [
    "https://github.com/OWASP/wrongsecrets"
  ],
  "containers": [
    "https://kubernetes.io/docs/concepts/security/",
    "https://github.com/madhuakula/kubernetes-goat"
  ],
  "mobile": [
    "https://mas.owasp.org/"
  ],
  "iot": [
    "https://github.com/OWASP/IoTGoat"
  ],
  "ot": [
    "https://csrc.nist.gov/pubs/sp/800/82/r3/final"
  ],
  "grc": [
    "https://csrc.nist.gov/publications/sp"
  ],
  "ctf-advanced": [
    "https://hackropole.fr/fr/challenges/"
  ],
  "extremely-hard-rooms": [
    "https://pwn.college/program-security/"
  ],
  "certifications": [
    "https://pauljerimy.com/security-certification-roadmap/"
  ],
  "community": [
    "https://www.defcon.org/"
  ],
  "research": [
    "https://nvd.nist.gov/"
  ],
  "final-project": [
    "https://owasp.org/projects/web-security-testing-guide"
  ]
}
const freeSets = new Map(Object.entries(freeSelections).map(([id, urls]) => [
  id, new Set(urls.map(normalizeUrl))
]))

function freeLinks(id: string): AssignedResource[] {
  const selected = freeSets.get(id)
  return selected ? levelLinks(id).filter(item => selected.has(normalizeUrl(item.url))) : []
}
function otherLinks(id: string): AssignedResource[] {
  const selected = freeSets.get(id)
  return levelLinks(id).filter(item => !selected?.has(normalizeUrl(item.url)))
}

// La vue complète reste identique. La vue gratuite affiche uniquement la sélection sans achat.
const freeOnly = ref(false)
async function toggleFreePath() {
  freeOnly.value = !freeOnly.value
  await nextTick()
  document.getElementById('premiers-pas')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<template>
  <div class="academy-syllabus">
    <header id="academy-top" class="academy-intro">
      <p class="academy-kicker">SKILL-ISSUE / ACADEMY</p>
      <h1>Cyber University</h1>
      <p class="academy-description">Apprendre la cybersécurité de zéro, étape par étape. Une roadmap complète avec des cours, des exercices et des labs, y compris sans budget.</p>
      <button class="academy-start" type="button" :aria-pressed="freeOnly" @click="toggleFreePath">{{ freeOnly ? 'Voir toutes les ressources' : 'Commencer gratuitement' }}</button>
    </header>

    <nav class="academy-contents" aria-label="Chapitres de la roadmap">
      <p>Parcours</p>
      <ul>
        <li v-for="section in sections" :key="section.id">
          <a :href="'#' + section.id">{{ section.title }}</a>
        </li>
      </ul>
    </nav>

    <p class="academy-legend" aria-live="polite">
      <strong>{{ freeOnly ? 'Parcours gratuit' : 'Parcours complet' }}</strong>
      - {{ freeOnly ? 'Les ressources sélectionnées sans achat.' : 'Toutes les ressources, gratuites et payantes.' }}
    </p>
    <p v-if="freeOnly" class="academy-free-picks">
      <strong>Labs pour commencer :</strong>
      <a href="https://www.root-me.org/" target="_blank" rel="noopener noreferrer">Root-Me</a>
      <span aria-hidden="true"> · </span>
      <a href="https://portswigger.net/web-security" target="_blank" rel="noopener noreferrer">PortSwigger Academy</a>
    </p>

    <main class="academy-chapters">
      <section v-for="section in sections" :id="section.id" :key="section.id" class="academy-chapter">
        <h2>{{ section.title }}</h2>
        <div v-for="level in levelsIn(section)" :id="'level-' + level.id" :key="level.id" class="academy-level">
          <h3>Level {{ numberFor(level.id) }} - {{ titleFor(level.id, level.title) }}</h3>

          <ul class="academy-links">
            <li v-for="item in freeLinks(level.id)" :key="item.id + item.url">
              <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ displayTitle(item) }}</a>
              <span class="academy-explanation"> - {{ describe(item) }}</span>
              <small v-if="!freeOnly" class="academy-free" title="Sélection sans achat">Gratuit</small>
            </li>
            <li v-for="item in freeOnly ? [] : otherLinks(level.id)" :key="item.id + item.url">
              <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ displayTitle(item) }}</a>
              <span class="academy-explanation"> - {{ describe(item) }}</span>
            </li>
          </ul>
        </div>
      </section>
    </main>

    <footer class="academy-footer">
      <a href="#academy-top">Retour au début</a>
    </footer>
  </div>
</template>
<style scoped>
/*
 * Une seule longue page, sans cartes, accordéons ni changement de vue.
 * Hiérarchie : chapitre > niveau > lien et courte description.
 */
.academy-syllabus {
  max-width: 1000px;
  margin: 0 auto;
  padding: 10px 0 54px;
  color: #d6d0dc;
  font-family: inherit;
}
.academy-syllabus * { box-sizing: border-box; }
:global(.academy-page),
:global(.academy-page .VPContent),
:global(.academy-page .VPDoc) { background: #151119; }
:global(.academy-page .VPDoc .container),
:global(.academy-page .VPDoc .content),
:global(.academy-page .VPDoc .content-container) {
  max-width: 1070px !important;
}
.academy-intro {
  padding: 24px 0 27px;
}
.academy-kicker {
  margin: 0 0 13px !important;
  color: #a999bc !important;
  font-size: .69rem !important;
  letter-spacing: .13em;
  font-weight: 650;
}
.academy-intro h1 {
  padding: 0 !important;
  margin: 0 0 12px !important;
  border: 0 !important;
  color: #f4eef7 !important;
  font-size: clamp(2.05rem, 4.4vw, 2.7rem) !important;
  line-height: 1.17;
  letter-spacing: -.035em;
  font-weight: 590;
}
.academy-description {
  max-width: 710px;
  margin: 0 0 20px !important;
  color: #bfb7c8 !important;
  font-size: .95rem;
  line-height: 1.65;
}
.academy-start {
  display: inline-block;
  padding: 9px 16px;
  color: #ead8f7 !important;
  border: 1px solid #735884;
  border-radius: 4px;
  background: #31233e;
  font-size: .83rem;
  font-weight: 590;
  text-decoration: none !important;
}
.academy-start:hover { background: #3e2b50; color: #fff !important; }
.academy-start { font-family: inherit; cursor: pointer; }
.academy-start:focus-visible { outline: 2px solid #bd92dd; outline-offset: 3px; }
.academy-contents {
  padding: 22px 0 23px;
  border-top: 1px solid #30273a;
  border-bottom: 1px solid #30273a;
}
.academy-contents p {
  margin: 0 0 11px !important;
  font-size: .83rem;
  font-weight: 620;
  color: #e2d3e9 !important;
}
.academy-contents ul {
  display: grid;
  grid-template-columns: repeat(2,minmax(0,1fr));
  column-gap: 21px;
  row-gap: 5px;
  padding: 0 !important;
  margin: 0 !important;
  list-style: none !important;
}
.academy-contents li { padding: 0 !important; margin: 0 !important; }
.academy-contents a {
  color: #bca9ca !important;
  font-size: .83rem;
  line-height: 1.45;
  text-decoration: none !important;
}
.academy-contents a:hover { color: #f0d7ff !important; text-decoration: underline !important; }
.academy-legend {
  padding: 0;
  margin: 25px 0 0 !important;
  max-width: 820px;
  color: #a99fb0 !important;
  font-size: .82rem;
  line-height: 1.65;
}
.academy-legend strong { color: #d7bfea; font-weight: 630; }
.academy-free-picks { margin: 8px 0 0 !important; font-size: .83rem; color: #b3a4c0 !important; line-height: 1.7; }
.academy-free-picks strong { color: #d8c2e6; font-weight: 600; }
.academy-free-picks a { color: #d4abf1 !important; text-decoration: none !important; }
.academy-free-picks a:hover { text-decoration: underline !important; }
.academy-chapter {
  padding: 32px 0 4px;
  scroll-margin-top: 90px;
}
.academy-chapter h2 {
  padding: 0 !important;
  margin: 0 0 20px !important;
  border: 0 !important;
  color: #eee8f1 !important;
  font-size: clamp(1.7rem, 3.1vw, 2.05rem) !important;
  line-height: 1.3;
  font-weight: 480;
  letter-spacing: -.012em;
}
.academy-level {
  margin: 0 0 29px;
  scroll-margin-top: 85px;
}
.academy-level h3 {
  margin: 0 0 12px !important;
  padding: 0 !important;
  border: 0 !important;
  color: #bdb7c4 !important;
  font-size: clamp(1.11rem, 2.1vw, 1.24rem) !important;
  font-weight: 460;
  line-height: 1.4;
  letter-spacing: 0;
}
.academy-links {
  list-style: none !important;
  padding: 0 0 0 35px !important;
  margin: 0 !important;
}
.academy-links li {
  position: relative;
  margin: 0 0 4px !important;
  padding: 0 !important;
  font-size: .98rem;
  line-height: 1.58;
  color: #d0c9d3;
  overflow-wrap: break-word;
  word-break: normal;
}
.academy-links li::before {
  content: "»";
  position: absolute;
  top: 0;
  left: -25px;
  font-weight: 560;
  font-size: 1.13rem;
  line-height: 1.39;
  color: #9f93a7;
}
.academy-links a {
  color: #cfa6f1 !important;
  font-weight: 540;
  text-decoration: none !important;
  text-underline-offset: 3px;
}
.academy-links a:hover { color: #edcfff !important; text-decoration: underline !important; }
.academy-explanation { color: #d0c9d3; }
.academy-free {
  display: inline;
  margin-left: 7px;
  color: #ad92be;
  font-size: .74rem;
  font-weight: 500;
  white-space: normal;
}
.academy-free { color: #b2a1bf; }
.academy-footer {
  margin: 40px 0 0;
  padding: 18px 0 0;
  border-top: 1px solid #33283e;
}
.academy-footer a { color: #bea2d3 !important; font-size: .82rem; text-decoration: none !important; }
.academy-footer a:hover { text-decoration: underline !important; }
.academy-syllabus a:focus-visible { outline: 2px solid #bd92dd; outline-offset: 3px; }
@media (max-width: 650px) {
  .academy-syllabus { padding: 3px 0 40px; }
  .academy-intro { padding: 20px 0 23px; }
  .academy-intro h1 { font-size: 2.15rem !important; }
  .academy-description { font-size: .9rem; }
  .academy-contents { padding: 17px 0 18px; }
  .academy-contents ul { grid-template-columns: 1fr; row-gap: 4px; }
  .academy-chapter { padding-top: 30px; }
  .academy-chapter h2 { font-size: 1.63rem !important; margin-bottom: 17px !important; }
  .academy-level { margin-bottom: 27px; }
  .academy-level h3 { font-size: 1.14rem !important; margin-bottom: 10px !important; }
  .academy-links { padding-left: 34px !important; }
  .academy-links li { font-size: .96rem; line-height: 1.6; margin-bottom: 4px !important; }
  .academy-links li::before { left: -24px; }
}
</style>

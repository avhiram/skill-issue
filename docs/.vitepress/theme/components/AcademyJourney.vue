<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { resources } from '../data/academy-organized'
import { masteryResources } from '../data/academy-mastery'
import { academyLevels, academyExtraResources, academyAssignments } from '../data/academy-unified'
import { tryHackMeRooms } from '../data/academy-tryhackme'

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
// Écarter uniquement les liens qui ne constituent ni un cours exploitable, ni un lab,
// ni une référence technique utile : offres commerciales, pages de prix,
// forums, newsletters, chaînes généralistes et fiches de certification.
// Les entrées restent dans les catalogues sources pour être réintroduites si nécessaire.
const academyNoiseIds = new Set([
  'hm-049',
  'hm-050',
  'hm-062',
  'hm-083',
  'hm-101',
  'hm-124',
  'hm-139',
  'hm-145',
  'hm-152',
  'hm-157',
  'hm-190',
  'hm-196',
  'hm-224',
  'hm-229',
  'hm-230',
  'hm-231',
  'hm-232',
  'hm-234',
  'hm-235',
  'hm-241',
  'hm-242',
  'hm-243',
  'hm-245',
  'hm-257',
  'hm-260',
  'hm-266',
  'hm-267',
  'hm-268',
  'hm-269',
  'hm-270',
  'hm-271',
  'hm-272',
  'hm-273',
  'hm-274',
  'hm-275',
  'hm-276',
  'hm-277',
  'hm-278',
  'hm-382',
  'hm-327',
  'hm-328',
  'hm-329',
  'hm-330',
  'hm-331',
  'hm-332',
  'hm-334',
  'hm-336',
  'hm-337',
  'hm-338',
  'hm-341',
  'hm-342',
  'hm-343',
  'hm-345',
  'hm-346',
  'hm-347',
  'hm-349',
  'hm-366',
  'hm-411',
  'added-036',
  'added-057',
  'added-092',
  'added-097',
  'added-098',
  'added-099',
  'added-100',
  'added-110',
  'added-111',
  'added-112',
  'added-113',
  // Pages vitrines, doublons thématiques et catalogues sans support direct.
  'hm-013',
  'hm-014',
  'hm-015',
  'hm-021',
  'hm-022',
  'hm-023',
  'hm-024',
  'hm-031',
  'hm-042',
  'hm-053',
  'hm-055',
  'hm-056',
  'hm-058',
  'hm-064',
  'hm-065',
  'hm-068',
  'hm-070',
  'hm-071',
  'hm-072',
  'hm-077',
  'hm-078',
  'hm-079',
  'hm-080',
  'hm-084',
  'hm-086',
  'hm-091',
  'hm-092',
  'hm-093',
  'hm-094',
  'hm-095',
  'hm-097',
  'hm-098',
  'hm-103',
  'hm-104',
  'hm-105',
  'hm-107',
  'hm-108',
  'hm-117',
  'hm-119',
  'hm-120',
  'hm-121',
  'hm-125',
  'hm-127',
  'hm-135',
  'hm-136',
  'hm-137',
  'hm-140',
  'hm-142',
  'hm-144',
  'hm-147',
  'hm-148',
  'hm-149',
  'hm-153',
  'hm-154',
  'hm-155',
  'hm-161',
  'hm-162',
  'hm-163',
  'hm-164',
  'hm-165',
  'hm-167',
  'hm-168',
  'hm-170',
  'hm-171',
  'hm-172',
  'hm-178',
  'hm-179',
  'hm-180',
  'hm-187',
  'hm-188',
  'hm-189',
  'hm-192',
  'hm-193',
  'hm-194',
  'hm-198',
  'hm-199',
  'hm-200',
  'hm-201',
  'hm-209',
  'hm-212',
  'hm-220',
  'hm-237',
  'hm-240',
  'hm-250',
  'hm-252',
  'hm-255',
  'hm-256',
  'hm-258',
  'hm-262',
  'hm-281',
  'hm-286',
  'hm-287',
  'hm-292',
  'hm-299',
  'hm-303',
  'hm-305',
  'hm-306',
  'hm-308',
  'hm-312',
  'hm-321',
  'hm-324',
  'hm-333',
  'hm-339',
  'hm-340',
  'hm-344',
  'hm-348',
  'hm-350',
  'hm-351',
  'hm-352',
  'hm-353',
  'hm-354',
  'hm-355',
  'hm-356',
  'hm-357',
  'hm-359',
  'hm-360',
  'hm-361',
  'hm-362',
  'hm-363',
  'hm-364',
  'hm-365',
  'hm-374',
  'hm-375',
  'hm-376',
  'hm-377',
  'hm-378',
  'hm-379',
  'hm-386',
  'hm-387',
  'hm-388',
  'hm-390',
  'hm-391',
  'hm-393',
  'hm-394',
  'hm-412',
  'hm-414',
  'hm-426',
  'hm-428',
  'hm-430',
  'hm-261',
  'added-011',
  'added-038',
  'added-058',
  'added-065',
  'added-066',
  'added-068',
  'added-072',
  'added-079',
  'added-082',
  'added-091',
  'added-101',
  'off-025',
  'off-022',
  'off-023',
  'hm-358'
])
// Favoriser les pages contenant directement un cours ou une documentation exploitable.
const academyResourceEdits: Record<string, Partial<Resource>> = {
  "hm-006": {
    "title": "QEMU - documentation",
    "url": "https://www.qemu.org/docs/master/",
    "type": "Documentation",
    "description": "Comprendre l’émulation et la configuration des machines virtuelles."
  },
  "hm-007": {
    "title": "VirtualBox - créer une machine virtuelle",
    "url": "https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/create-vm.html",
    "type": "Tutoriel",
    "description": "Créer une VM, choisir son système et configurer ses ressources."
  },
  "hm-032": {
    "title": "Kali Linux - documentation",
    "url": "https://www.kali.org/docs/",
    "type": "Documentation",
    "description": "Installer Kali Linux et configurer son environnement de travail."
  },
  "off-005": {
    "title": "Wireshark - guide utilisateur",
    "url": "https://www.wireshark.org/docs/wsug_html_chunked/",
    "type": "Documentation",
    "description": "Apprendre à capturer, filtrer et analyser le trafic réseau."
  },
  "hm-054": {
    "title": "Nmap - documentation officielle",
    "url": "https://nmap.org/docs.html",
    "type": "Documentation",
    "description": "Comprendre les options de scan et consulter des exemples d’utilisation."
  },
  "hm-073": {
    "title": "OpenVPN - guide de configuration",
    "url": "https://openvpn.net/community-docs/how-to/",
    "type": "Cours",
    "description": "Installer et configurer un VPN client-serveur, puis tester la connexion."
  },
  "hm-074": {
    "title": "WireGuard - tutoriel de configuration",
    "type": "Cours",
    "description": "Configurer un tunnel VPN et comprendre les clés et les interfaces."
  },
  "hm-076": {
    "title": "SSL/TLS - comprendre le protocole",
    "url": "https://www.cloudflare.com/fr-fr/learning/ssl/transport-layer-security-tls/",
    "type": "Cours",
    "description": "Comprendre le chiffrement TLS, les certificats et la protection des échanges HTTPS."
  },
  "added-022": {
    "title": "Wazuh - prise en main",
    "url": "https://documentation.wazuh.com/current/getting-started/index.html",
    "type": "Documentation",
    "description": "Comprendre les composants du SIEM, la collecte de logs et les cas de détection."
  },
  "added-026": {
    "title": "REMnux - documentation",
    "url": "https://docs.remnux.org/",
    "type": "Documentation",
    "description": "Installer et utiliser un environnement d’analyse de malware."
  },
  "added-042": {
    "title": "Ghidra - dépôt et documentation",
    "url": "https://github.com/NationalSecurityAgency/ghidra",
    "type": "Documentation",
    "description": "Accéder au projet officiel, à ses instructions et à sa documentation."
  }
}
const sourceItems: Resource[] = ([...tryHackMeRooms, ...resources, ...masteryResources, ...academyExtraResources] as Resource[])
  .filter(item => !academyNoiseIds.has(item.id))
  .map(item => ({ ...item, ...academyResourceEdits[item.id] }))
const resourceMap = new Map<string, AssignedResource>()
for (const item of sourceItems) {
  // Retirer les ressources Cisco, NetAcad et Packet Tracer, pas les cours réseau neutres.
  if (/cisco|netacad|packet.?tracer/i.test(item.title + ' ' + item.url)) continue
  const key = normalizeUrl(item.url)
  if (resourceMap.has(key)) continue
  const title = simplify(item.title.trim())
  let routeLevel = item.routeLevel || academyAssignments[item.id] || 'research'
  if (!item.id.startsWith('thm-')) {
    if (osintToolUrls.has(key)) routeLevel = 'osint-recon'
    if (localLabUrls.has(key)) routeLevel = 'local-labs'
    else if (key === normalizeUrl('https://tryhackme.com/free-rooms')) routeLevel = 'ctf-intermediate'
    else if (windowsRooms.has(title)) routeLevel = 'bonus-windows-labs'
    else if (hardRooms.has(title)) routeLevel = 'extremely-hard-rooms'
    else if (bonusLabs.has(title)) routeLevel = 'ctf-intermediate'
    else if (routeAdjustments[title]) routeLevel = routeAdjustments[title]
  }
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

// Distinguer les cours/labs (parcours) des logiciels et documentations (références).
const toolNames = /(?:^|[\s:–-])(virtualbox|qemu|wireshark|tcpdump|nmap|rustscan|masscan|burp suite|metasploit|hydra|john the ripper|hashcat|ghidra|radare2|autopsy|volatility|cyberchef|sherlock|maigret|holehe|theharvester|subfinder|amass|recon-ng|photon|ffuf|gobuster|nikto|sqlmap|dirsearch|shodan|censys|openvas|nessus|zap|sysmon|sysinternals|splunk|wazuh|suricata|zeek|snort|yara|velociraptor|osquery|docker|kubernetes|terraform|ansible|git|vscode|visual studio code|pycharm|jupyter|postman|insomnia|gns3|bloodhound|impacket|responder|netcat|mitmproxy|bettercap|aircrack|binwalk|exiftool|foremost)(?:$|[\s:–-])/i
const toolDomains = /(?:virtualbox\.org|qemu\.org|wireshark\.org|nmap\.org|tcpdump\.org|ghidra-sre\.org|portswigger\.net\/burp|gchq\.github\.io\/CyberChef|osintframework\.com|shodan\.io|censys\.io|docker\.com|kubernetes\.io|github\.com\/(?:sherlock-project|soxoj\/maigret|megadose\/holehe|laramies\/theHarvester))/i
function isToolOrReference(item: AssignedResource): boolean {
  if (item.id.startsWith('thm-')) return false
  const masteryToolId = /^hm-(\d+)$/.exec(item.id)
  if (masteryToolId && Number(masteryToolId[1]) >= 279 && Number(masteryToolId[1]) <= 326 && item.id !== 'hm-314') return true
  const type = (item.type || '').toLowerCase()
  if (/cours|exercice|lab|ctf|challenge|formation/.test(type)) return false
  if (/référence|reference|outil|documentation/.test(type)) return true
  if (/cours|formation|tutoriel|tutorial|introduction|guide pratique|exercices|lab|challenges|academy|training|bootcamp|learn|fondamentaux|basics/i.test(item.title)) return false
  return item.category === 'outils' || toolNames.test(' ' + item.title + ' ') || toolDomains.test(item.url)
}
const selectedCourses = (id: string) => freeLinks(id).filter(item => !isToolOrReference(item))
const otherCourses = (id: string) => otherLinks(id).filter(item => !isToolOrReference(item))
function sectionTools(section: typeof sections[number]): AssignedResource[] {
  const levels = new Set<string>(section.levels)
  const items = catalog.filter(item => levels.has(item.routeLevel) && isToolOrReference(item))
  return freeOnly.value ? items.filter(item => freeSets.get(item.routeLevel)?.has(normalizeUrl(item.url))) : items
}

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
    "https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/create-vm.html"
  ],
  "network-basics": [
    "https://www.cloudflare.com/learning/network-layer/what-is-a-computer-network/",
    "https://www.practicalnetworking.net/"
  ],
  "network-practice": [
    "https://wiki.wireshark.org/SampleCaptures",
    "https://www.wireshark.org/docs/wsug_html_chunked/",
    "https://openvpn.net/community-docs/how-to/",
    "https://www.wireguard.com/quickstart/",
    "https://www.cloudflare.com/fr-fr/learning/ssl/transport-layer-security-tls/"
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
    "https://nmap.org/docs.html"
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
    "https://documentation.wazuh.com/current/getting-started/index.html",
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
    "https://github.com/NationalSecurityAgency/ghidra"
  ],
  "malware": [
    "https://docs.remnux.org/",
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
// Importer aussi les salles du README dans le parcours gratuit, sans doublon.
for (const room of tryHackMeRooms) {
  const existing = freeSets.get(room.routeLevel) || new Set<string>()
  existing.add(normalizeUrl(room.url))
  freeSets.set(room.routeLevel, existing)
}
// Le nouveau README indique explicitement que ces salles ne sont plus gratuites.
// Elles restent consultables dans le parcours complet si elles figurent déjà au catalogue.
const roomsNotFree = [
  'probe', 'cauldron', 'bppenguin', 'greprtp', 'snappedphishingline',
  'lookback', 'confidential', 'linuxfundamentalspart2',
  'linuxfundamentalspart3', 'introtolan'
]
for (const slug of roomsNotFree) {
  const url = normalizeUrl('https://tryhackme.com/room/' + slug)
  for (const selected of freeSets.values()) selected.delete(url)
}

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
async function selectPath(showFreeOnly: boolean) {
  freeOnly.value = showFreeOnly
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
      <div class="academy-actions" role="group" aria-label="Choisir le parcours">
        <button class="academy-start" :class="{ 'academy-start-active': freeOnly }" type="button" :aria-pressed="freeOnly" @click="selectPath(true)">Parcours gratuit</button>
        <button class="academy-start" :class="{ 'academy-start-active': !freeOnly }" type="button" :aria-pressed="!freeOnly" @click="selectPath(false)">Parcours complet</button>
      </div>
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
      - {{ freeOnly ? 'Cours et labs sélectionnés sans achat.' : 'Cours et labs, gratuits et payants.' }}
    </p>
    <p v-if="freeOnly" class="academy-free-picks">
      <strong>Labs pour commencer :</strong>
      <a href="https://www.root-me.org/" target="_blank" rel="noopener noreferrer">Root-Me</a>
      <span aria-hidden="true"> · </span>
      <a href="https://portswigger.net/web-security" target="_blank" rel="noopener noreferrer">PortSwigger Academy</a>
    </p>

    <p class="academy-learning-note">Suis les cours et les labs dans l’ordre. Les logiciels et références sont regroupés dans la <a href="#academy-tools">boîte à outils</a>, à la fin.</p>

    <main class="academy-chapters">
      <section v-for="section in sections" :id="section.id" :key="section.id" class="academy-chapter">
        <h2>{{ section.title }}</h2>
        <div v-for="level in levelsIn(section)" :id="'level-' + level.id" :key="level.id" class="academy-level">
          <h3>Level {{ numberFor(level.id) }} - {{ titleFor(level.id, level.title) }}</h3>

          <ul class="academy-links">
            <li v-for="item in selectedCourses(level.id)" :key="item.id + item.url">
              <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ displayTitle(item) }}</a>
              <span class="academy-explanation"> - {{ describe(item) }}</span>
              <small v-if="!freeOnly" class="academy-free" title="Sélection sans achat">Gratuit</small>
            </li>
            <li v-for="item in freeOnly ? [] : otherCourses(level.id)" :key="item.id + item.url">
              <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ displayTitle(item) }}</a>
              <span class="academy-explanation"> - {{ describe(item) }}</span>
            </li>
          </ul>
        </div>
      </section>
    </main>

    <section id="academy-tools" class="academy-chapter academy-toolbox" aria-label="Boîte à outils">
      <h2>Outils et références</h2>
      <p class="academy-learning-note">Ces liens servent pendant les exercices. Ils ne constituent pas des étapes à apprendre dans l’ordre.</p>
      <template v-for="section in sections" :key="'tools-' + section.id">
        <div v-if="sectionTools(section).length" class="academy-level">
          <h3>{{ section.title }}</h3>
          <ul class="academy-links">
            <li v-for="item in sectionTools(section)" :key="'tool-' + item.id + item.url">
              <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ displayTitle(item) }}</a>
              <span class="academy-explanation"> - {{ describe(item) }}</span>
            </li>
          </ul>
        </div>
      </template>
    </section>

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
.academy-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
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
.academy-start-active { background: #31233e !important; border-color: #735884 !important; color: #ead8f7 !important; }
.academy-start:not(.academy-start-active) { background: transparent; border-color: #4a3c55; color: #c9bfd0 !important; }
.academy-start:hover { background: #3e2b50; color: #fff !important; }
.academy-start { font-family: inherit; cursor: pointer; }
.academy-start:focus-visible { outline: 2px solid #bd92dd; outline-offset: 3px; }
.academy-learning-note { margin: 16px 0 24px !important; color: #bdb3c5 !important; font-size: .88rem; line-height: 1.7; }
.academy-learning-note a { color: #c7a8e4 !important; }
.academy-toolbox { margin-top: 38px; padding-top: 26px; border-top: 1px solid #30273a; }
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

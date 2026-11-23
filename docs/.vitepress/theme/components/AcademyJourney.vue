<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
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
    id: 'premiers-pas',
    title: "Bien démarrer",
    summary: "Comprendre son ordinateur, préparer ses outils et apprendre les réseaux avant de passer aux systèmes.",
    levels: ["environment","network-basics","network-practice"]
  },
  {
    id: 'linux-windows',
    title: "Comprendre Linux et Windows",
    summary: "Se repérer dans les deux systèmes, utiliser les commandes et identifier les permissions.",
    levels: ["linux-basics","linux-admin","windows-basics","powershell"]
  },
  {
    id: 'code-et-web',
    title: "Apprendre à coder et comprendre le Web",
    summary: "Écrire ses premiers scripts, puis comprendre les échanges entre navigateur, serveur et API.",
    levels: ["python-basics","scripting","web-basics","web-api"]
  },
  {
    id: 'notions-securite',
    title: "Comprendre les bases de la sécurité",
    summary: "Apprendre les notions de sécurité, la cryptographie et l'OSINT, puis les pratiquer sur des challenges.",
    levels: ["security-basics","crypto","osint-recon","osint-practice"]
  },
  {
    id: 'premiers-labs',
    title: "Premiers outils, pentest et CTF",
    summary: "Découvrir Nmap, installer ses labs locaux, apprendre le Bug Bounty puis résoudre des CTF autorisés.",
    levels: ["scanning","web-security","web-labs","local-labs","bug-bounty","ctf-beginner","ctf-intermediate","pentest-system","bonus-windows-labs"]
  },
  {
    id: 'active-directory-red-team',
    title: "Active Directory et Red Team",
    summary: "Commencer par les domaines Windows, suivre GOAD dans l'ordre, puis explorer les labs C2.",
    levels: ["ad-intro","ad-minilab","ad-light","ad-full","c2","red-advanced"]
  },
  {
    id: 'blue-team',
    title: "Blue Team : détection et réponse",
    summary: "Apprendre à lire des traces, comprendre un SIEM et enquêter sur une activité.",
    levels: ["blue-logs","blue-siem","blue-threat"]
  },
  {
    id: 'forensic-reverse',
    title: "Forensic, reverse et analyse de malware",
    summary: "Analyser le réseau, la mémoire et les programmes avant de reconstituer les faits.",
    levels: ["dfir-network","dfir-host","reverse","malware"]
  },
  {
    id: 'cloud-et-specialites',
    title: "Cloud et autres domaines de sécurité",
    summary: "Aborder le Cloud, les conteneurs, les applications mobiles, l'IoT, l'OT et les risques.",
    levels: ["cloud-foundations","cloud-security","containers","mobile","iot","ot","grc"]
  },
  {
    id: 'challenges-avances',
    title: "Challenges avancés",
    summary: "Réutiliser les compétences acquises sur des CTF de difficulté supérieure.",
    levels: ["ctf-advanced","extremely-hard-rooms"]
  },
  {
    id: 'veilles-certifications',
    title: "Veille, certifications et communautés",
    summary: "Identifier des sources fiables, préparer un examen et continuer à progresser.",
    levels: ["research","certifications","community"]
  },
  {
    id: 'projet-final',
    title: "Projet final",
    summary: "Mettre toute la méthode en pratique et rédiger un rapport clair sur un lab.",
    levels: ["final-project"]
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
const sourceItems: Resource[] = [...resources, ...masteryResources, ...academyExtraResources] as Resource[]
const resourceMap = new Map<string, AssignedResource>()
for (const item of sourceItems) {
  // Retirer les ressources Cisco, NetAcad et Packet Tracer, pas les cours réseau neutres.
  if (/cisco|netacad|packet.?tracer/i.test(item.title + ' ' + item.url)) continue
  const key = normalizeUrl(item.url)
  if (resourceMap.has(key)) continue
  const title = simplify(item.title.trim())
  let routeLevel = item.routeLevel || academyAssignments[item.id] || 'research'
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
function describe(item: AssignedResource) {
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
    "https://osintframework.com/"
  ],
  "osint-practice": [
    "https://bellingcat.gitbook.io/toolkit"
  ],
  "scanning": [
    "https://nmap.org/"
  ],
  "web-security": [
    "https://portswigger.net/web-security/",
    "https://owasp.org/www-project-top-ten/"
  ],
  "web-labs": [
    "https://portswigger.net/web-security/all-labs",
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
    "https://www.root-me.org/"
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
const storageKey = 'skill-issue-academy-single-route-v1'
const resourceView = ref<'free' | 'all'>('free')
const completed = ref<string[]>([])
const search = ref('')
const showUrls = ref(false)
const doneCount = computed(() => orderedLevels.filter(l => completed.value.includes(l.id)).length)
const progress = computed(() => Math.round((doneCount.value / orderedLevels.length) * 100))
const query = computed(() => simplify(search.value.trim()))
// Toutes les URL restent visibles, sans onglets ni filtre qui raccourcit la page.
function visibleLinks(id: string): AssignedResource[] {
  const base = levelLinks(id)
  if (!query.value) return base
  const level = byId.get(id)
  if (level && simplify(level.title + ' ' + level.intro).includes(query.value)) return base
  return base.filter(item => simplify(item.title + ' ' + item.url + ' ' + (item.description || '')).includes(query.value))
}
function freeLinks(id: string): AssignedResource[] {
  const free = freeSets.get(id)
  return free ? visibleLinks(id).filter(item => free.has(normalizeUrl(item.url))) : []
}
function otherLinks(id: string): AssignedResource[] {
  const free = freeSets.get(id)
  return visibleLinks(id).filter(item => !free?.has(normalizeUrl(item.url)))
}
function visibleLevels(section: typeof sections[number]) {
  if (!query.value) return levelsIn(section)
  return levelsIn(section).filter(level =>
    (resourceView.value === 'free' ? freeLinks(level.id) : visibleLinks(level.id)).length > 0
  )
}
const searchCount = computed(() => orderedLevels.reduce((n, l) =>
  n + (resourceView.value === 'free' ? freeLinks(l.id) : visibleLinks(l.id)).length, 0
))
const freeCount = orderedLevels.reduce((n, l) => {
  const free = freeSets.get(l.id)
  return n + levelLinks(l.id).filter(item => free?.has(normalizeUrl(item.url))).length
}, 0)

function persist() {
  try { localStorage.setItem(storageKey, JSON.stringify(completed.value)) } catch {}
}
function toggle(id: string, checked: boolean) {
  completed.value = checked ? [...new Set([...completed.value, id])] : completed.value.filter(x => x !== id)
  persist()
}
onMounted(() => {
  try {
    const stored = JSON.parse(localStorage.getItem(storageKey) || '[]')
    if (Array.isArray(stored)) completed.value = stored.filter((x: unknown): x is string => typeof x === 'string' && byId.has(x))
  } catch { completed.value = [] }
})
</script>

<template>
  <div class="academy-roadmap">
    <header id="about" class="intro">
      <p class="eyebrow">SKILL-ISSUE / ACADEMY</p>
      <h1>Roadmap cybersécurité</h1>
      <p class="lead">Un parcours chronologique, de zéro aux labs avancés. Choisis les ressources sans achat ou affiche tout le catalogue, niveau par niveau, sur cette même page.</p>
      <div class="figures">
        <span><strong>{{ orderedLevels.length }}</strong> niveaux dans l'ordre</span>
        <span><strong>{{ freeCount }}</strong> liens sélectionnés sans achat</span>
        <span><strong>{{ catalog.length }}</strong> ressources au total</span>
      </div>
      <div class="progress-heading">
        <span>Progression personnelle</span>
        <strong>{{ doneCount }} / {{ orderedLevels.length }} niveaux terminés</strong>
      </div>
      <div class="progress-track" role="progressbar" aria-label="Niveaux terminés" :aria-valuenow="doneCount" :aria-valuemin="0" :aria-valuemax="orderedLevels.length">
        <span :style="{ width: progress + '%' }"></span>
      </div>
      <p class="progress-help">Les niveaux cochés restent enregistrés sur cet appareil.</p>

      <div class="route-choice">
        <p class="choice-label">Choisir son parcours</p>
        <div class="choice-buttons" role="group" aria-label="Afficher les ressources">
          <button type="button" :class="{ active: resourceView === 'free' }" :aria-pressed="resourceView === 'free'" @click="resourceView = 'free'">Sans budget</button>
          <button type="button" :class="{ active: resourceView === 'all' }" :aria-pressed="resourceView === 'all'" @click="resourceView = 'all'">Toutes les ressources</button>
        </div>
        <p class="choice-help">Les mêmes niveaux, dans le même ordre. Les ressources complémentaires sont facultatives : aucun achat de cours n'est nécessaire pour suivre la sélection gratuite.</p>
      </div>

      <nav class="roadmap-index" aria-label="Sommaire">
        <p class="index-label">Sur cette page</p>
        <a href="#parcours-gratuit">Le parcours - du début au projet final</a>
        <div class="index-subitems">
          <a v-for="section in sections" :key="section.id" :href="'#' + section.id">{{ section.title }}</a>
        </div>
      </nav>
      <div class="search-controls">
        <label for="academy-query">Rechercher dans la roadmap</label>
        <input id="academy-query" v-model="search" type="search" placeholder="Python, Linux, Cobalt Strike, GOAD, Bug Bounty..." autocomplete="off">
        <label class="show-urls"><input v-model="showUrls" type="checkbox"> Afficher les URL complètes</label>
        <p v-if="query" class="search-note">{{ searchCount }} ressources correspondant à ta recherche</p>
      </div>
    </header>

    <main>
      <section id="parcours-gratuit" class="free-path" aria-labelledby="free-title">
        <div class="major-heading">
          <p class="eyebrow">DU PREMIER NIVEAU AU PROJET FINAL</p>
          <h2 id="free-title">Le parcours</h2>
          <p>Avance dans l'ordre. « Pour commencer » rassemble les ressources sélectionnées sans achat. « Pour approfondir » apparaît si tu choisis « Toutes les ressources ».</p>
          <p class="small-disclaimer">Un compte gratuit, un ordinateur ou une installation locale peuvent être nécessaires. Les abonnements, les examens et certains usages du Cloud ne sont pas inclus.</p>
        </div>

        <section v-for="section in sections" :id="section.id" :key="section.id" class="course-section">
          <header class="course-section-heading">
            <h3>{{ section.title }}</h3>
            <p>{{ section.summary }}</p>
          </header>

          <article v-for="level in visibleLevels(section)" :id="'level-' + level.id" :key="level.id" class="course-level">
            <div class="course-level-heading">
              <h4><span class="level-label">Niveau {{ numberFor(level.id) }}</span> - {{ level.title }}</h4>
              <label class="done-toggle">
                <input type="checkbox" :checked="completed.includes(level.id)" @change="toggle(level.id, !completed.includes(level.id))">
                <span>Terminé</span>
              </label>
            </div>
            <p class="level-description">{{ level.intro }}</p>
            <p v-if="freeLinks(level.id).length" class="resource-group-title">Pour commencer <span>- sans achat</span></p>
            <ul v-if="freeLinks(level.id).length" class="resource-list">
              <li v-for="item in freeLinks(level.id)" :key="item.id + item.url">
                <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ item.title }}</a>
                <span class="resource-description"> - {{ describe(item) }}</span>
                <small v-if="showUrls" class="raw-url">{{ item.url }}</small>
              </li>
            </ul>
            <p v-else-if="!query" class="empty-message">Exercice de synthèse avec les ressources déjà étudiées.</p>
            <div v-if="resourceView === 'all' && otherLinks(level.id).length" class="extra-resources">
              <p class="resource-group-title">Pour approfondir <span>- facultatif, accès parfois payant</span></p>
              <ul class="resource-list">
                <li v-for="item in otherLinks(level.id)" :key="item.id + item.url">
                  <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ item.title }}</a>
                  <span class="resource-description"> - {{ describe(item) }}</span>
                  <small v-if="item.access" class="resource-access">{{ item.access }}</small>
                  <small v-if="showUrls" class="raw-url">{{ item.url }}</small>
                </li>
              </ul>
            </div>
            <details v-if="!query" class="exercise">
              <summary>Exercice pratique et validation</summary>
              <p><strong>À faire :</strong> {{ level.exercise }}</p>
              <p><strong>Tu peux continuer quand :</strong> {{ level.ready }}</p>
            </details>
          </article>
          <p v-if="query && !visibleLevels(section).length" class="empty-message">Aucun résultat dans cette partie.</p>
          <a class="return-link" href="#about">Retour au début ↑</a>
        </section>
      </section>

    </main>
    <p class="closing">Entraîne-toi uniquement sur des environnements autorisés. « Sans budget » signifie sans achat de cours pour les liens sélectionnés, pas une garantie de gratuité du matériel, des crédits Cloud ou des certifications. Les conditions d'accès des plateformes peuvent évoluer.</p>
  </div>
</template>

<style scoped>
.academy-roadmap {
  --page-bg:#0c0912;
  --page-panel:#130d1c;
  --line:#342742;
  --purple:#b892ee;
  --purple-soft:#e1ccff;
  --text:#e7e0ee;
  --muted:#b0a4bd;
  max-width:1010px;
  margin:0 auto;
  padding:16px 2px 38px;
  color:var(--text);
  font-family:inherit;
}
.academy-roadmap * { box-sizing:border-box; }
:global(.Layout.academy-page),
:global(.academy-page .VPContent) { background:#0c0912; }
.intro { scroll-margin-top:88px; padding:9px 0 28px; border-bottom:1px solid var(--line); }
.eyebrow { margin:0 0 12px!important; color:var(--purple)!important; font-size:.69rem!important; letter-spacing:.14em; font-weight:750; }
.intro h1 { color:#f9f2ff!important; border:0!important; padding:0!important; margin:0 0 12px!important; font-size:clamp(1.8rem,4vw,2.55rem)!important; letter-spacing:-.035em; line-height:1.2; }
.lead { color:#c8bcd3!important; font-size:.91rem; line-height:1.8; max-width:790px; margin:0 0 20px!important; }
.figures { display:flex; flex-wrap:wrap; gap:8px 24px; margin-bottom:25px; color:#bcaece; font-size:.78rem; }
.figures strong { color:#e7d0ff; font-size:1rem; padding-right:4px; }
.progress-heading { display:flex; align-items:center; justify-content:space-between; gap:8px; color:#ae9ebb; font-size:.75rem; margin-bottom:8px; }
.progress-heading strong { font-weight:620; color:#dcc3f5; }
.progress-track { height:6px; max-width:790px; background:#2a2033; border-radius:10px; overflow:hidden; }
.progress-track span { display:block; height:100%; background:linear-gradient(90deg,#7650aa,#c79bea); transition:width .2s; }
.progress-help { color:#9789a5!important; font-size:.7rem; margin:8px 0 22px!important; }
.route-choice { margin:20px 0 26px; }
.choice-label { color:#ddc5f2!important; font-size:.8rem!important; font-weight:670; margin:0 0 10px!important; }
.choice-buttons { display:flex; flex-wrap:wrap; gap:8px; }
.choice-buttons button { border:1px solid #50385f; background:transparent; border-radius:5px; color:#bdaecb; padding:9px 15px; font:inherit; font-size:.8rem; cursor:pointer; }
.choice-buttons button.active { border-color:#ad81d1; color:#f3e8ff; background:#241630; }
.choice-buttons button:hover { border-color:#a176c4; color:#f3e8ff; }
.choice-buttons button:focus-visible { outline:2px solid #d1a0f2; outline-offset:2px; }
.choice-help { margin:9px 0 0!important; max-width:750px; color:#a99ab6!important; font-size:.73rem; line-height:1.7; }
.roadmap-index { border-left:2px solid #674782; padding:1px 0 1px 19px; margin:25px 0; display:flex; flex-direction:column; gap:8px; }
.index-label { color:#d4b5f1!important; font-size:.77rem; font-weight:680; margin:0 0 5px!important; }
.roadmap-index a { display:block; width:fit-content; color:#d5c1e9!important; text-decoration:none!important; font-size:.82rem; line-height:1.45; }
.roadmap-index a:hover { color:#fff1ff!important; text-decoration:underline!important; }
.index-subitems { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); column-gap:20px; row-gap:6px; margin-left:13px; padding:3px 0 6px; }
.index-subitems a { color:#ada0be!important; font-size:.75rem; }
.search-controls { max-width:780px; display:flex; gap:8px; flex-direction:column; margin-top:18px; }
.search-controls>label:first-child { font-size:.75rem; color:#c6b0dd; font-weight:650; }
.search-controls input[type=search] { width:100%; padding:11px 12px; border-radius:5px; border:1px solid #59426c; background:#17101f; color:#eee5f5; font:inherit; font-size:.86rem; }
.search-controls input[type=search]:focus { outline:2px solid #9e74c9; outline-offset:1px; }
.show-urls { width:fit-content; color:#a99bb4; font-size:.73rem; display:flex; align-items:center; gap:7px; cursor:pointer; }
.show-urls input { accent-color:#a879d8; }
.search-note { margin:2px 0!important; color:#c5b1d8!important; font-size:.74rem; }
.major-heading { border-bottom:1px solid #4a355b; padding:26px 0 23px; margin-bottom:16px; scroll-margin-top:86px; }
.major-heading h2 { color:#f0e1ff!important; padding:0!important; border:0!important; font-size:clamp(1.55rem,3vw,2rem)!important; font-weight:680; letter-spacing:-.022em; margin:0 0 9px!important; }
.major-heading p:not(.eyebrow) { color:#c7b9d2!important; font-size:.87rem; line-height:1.7; max-width:830px; margin:0 0 8px!important; }
.major-heading .small-disclaimer { color:#94869e!important; font-size:.74rem!important; }
.course-section { padding:22px 0 8px; scroll-margin-top:90px; }
.course-section-heading { padding:0 0 15px; margin-bottom:18px; border-bottom:1px solid #32253f; }
.course-section-heading h3 { color:#d1aaed!important; font-size:clamp(1.18rem,2.6vw,1.46rem)!important; padding:0!important; margin:0 0 7px!important; border:0!important; font-weight:660; }
.course-section-heading p { color:#ada0bd!important; font-size:.82rem; line-height:1.7; margin:0!important; }
.course-level { margin:0 0 23px 8px; padding:0 0 20px 20px; border-left:2px solid #49305c; position:relative; scroll-margin-top:90px; }
.course-level:before { content:''; position:absolute; top:8px; left:-6px; width:10px; height:10px; background:#130d1c; border:2px solid #a580ca; border-radius:50%; }
.course-level:has(.done-toggle input:checked):before { background:#b38be0; }
.course-level-heading { display:flex; align-items:flex-start; justify-content:space-between; gap:10px; }
.course-level h4 { color:#e7dbf0!important; font-size:1rem!important; font-weight:670!important; line-height:1.55; padding:0!important; margin:0 0 5px!important; border:0!important; }
.level-label { color:#c2a2e7; font-weight:710; }
.done-toggle { flex-shrink:0; display:flex; align-items:center; gap:6px; cursor:pointer; color:#a99db3; font-size:.73rem; padding-top:4px; }
.done-toggle input { width:15px; height:15px; accent-color:#9970c3; }
.level-description { margin:0 0 12px!important; color:#a99db3!important; font-size:.8rem; line-height:1.75; }
.resource-group-title { margin:12px 0 7px!important; color:#d4adef!important; font-size:.78rem!important; font-weight:680; }
.resource-group-title span { color:#9e8bad; font-weight:450; }
.extra-resources { margin:17px 0 12px; padding:3px 0 1px 13px; border-left:1px solid #382645; }
.resource-access { display:inline; margin-left:6px; color:#9c8cac; font-size:.7rem; }
.resource-list { margin:0 0 12px 15px!important; padding:0!important; list-style:none!important; }
.resource-list li { position:relative; margin:4px 0!important; padding:0!important; color:#bfb1c7; font-size:.82rem; line-height:1.65; overflow-wrap:anywhere; }
.resource-list li:before { content:'›'; position:absolute; left:-16px; color:#ad80cf; font-weight:800; }
.resource-list a { color:#d8b2f3!important; font-size:inherit; font-weight:615; text-decoration:none!important; }
.resource-list a:hover { color:#fff0ff!important; text-decoration:underline!important; }
.resource-description { color:#b6abbf; }
.raw-url { display:block; margin:2px 0 6px; color:#9485a3; font-size:.69rem; overflow-wrap:anywhere; }
.exercise { margin:8px 0 0 15px; color:#aca0b9; font-size:.77rem; }
.exercise summary { width:fit-content; color:#b89bcf; cursor:pointer; font-size:.77rem; }
.exercise summary:hover { color:#f0dcff; }
.exercise p { margin:6px 0!important; color:#b9adbf!important; font-size:.77rem; line-height:1.6; }
.exercise strong { color:#dec6f0; }
.empty-message { color:#9a8baa!important; font-size:.78rem; margin:5px 0!important; }
.return-link { display:inline-block; margin:6px 0 12px; font-size:.72rem; color:#a68dbd!important; text-decoration:none!important; }
.return-link:hover { color:#e9d2ff!important; }
.closing { color:#8e809c!important; font-size:.73rem; margin:23px 0 0!important; line-height:1.7; }
@media(max-width:650px) {
  .academy-roadmap { padding:9px 0 30px; }
  .index-subitems { grid-template-columns:1fr; gap:5px; }
  .figures { gap:9px 14px; font-size:.73rem; }
  .course-level { margin-left:4px; padding-left:14px; }
  .course-level-heading h4 { font-size:.93rem!important; }
  .done-toggle span { display:none; }
  .resource-list li { font-size:.79rem; }
  .major-heading { padding-top:19px; }
}
@media(prefers-reduced-motion:reduce) { .progress-track span { transition:none; } }
</style>
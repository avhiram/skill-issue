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
const completed = ref<string[]>([])
const viewMode = ref<'free' | 'all'>('free')
const search = ref('')
const showUrls = ref(false)
const doneCount = computed(() => orderedLevels.filter(l => completed.value.includes(l.id)).length)
const progress = computed(() => Math.round((doneCount.value / orderedLevels.length) * 100))
const query = computed(() => simplify(search.value.trim()))
function modeLinks(id: string): AssignedResource[] {
  const list = levelLinks(id)
  if (viewMode.value === 'all') return list
  const free = freeSets.get(id)
  return free ? list.filter(item => free.has(normalizeUrl(item.url))) : []
}
function visibleLinks(id: string) {
  const base = modeLinks(id)
  if (!query.value) return base
  const level = byId.get(id)
  if (level && simplify(level.title + ' ' + level.intro).includes(query.value)) return base
  return base.filter(item => simplify(item.title + ' ' + item.url + ' ' + (item.description || '')).includes(query.value))
}
function visibleLevels(section: typeof sections[number]) {
  if (!query.value) return levelsIn(section)
  return levelsIn(section).filter(level => visibleLinks(level.id).length > 0)
}
const searchCount = computed(() => orderedLevels.reduce((n, l) => n + visibleLinks(l.id).length, 0))
const filteredCount = computed(() => orderedLevels.reduce((n, l) => n + modeLinks(l.id).length, 0))
const freeComplete = computed(() => orderedLevels.every(l => modeLinks(l.id).length > 0))
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
    <header id="about" class="about">
      <p class="academy-eyebrow">SKILL-ISSUE / ACADEMY</p>
      <h1>Roadmap cybersécurité</h1>
      <h2>Commence ici</h2>
      <p>Du réseau à Linux, au pentest, au SOC, au forensic, au Cloud et aux certifications : une seule progression pour explorer tous les domaines. Avance à ton rythme, avec ou sans budget.</p>
      <div class="progress-wrap">
        <div class="progress-head"><span>Progression</span><strong>{{ doneCount }} / {{ orderedLevels.length }} niveaux terminés</strong></div>
        <div class="progress-track" role="progressbar" aria-label="Progression de la roadmap" :aria-valuenow="doneCount" :aria-valuemin="0" :aria-valuemax="orderedLevels.length"><span :style="{width: progress + '%'}"></span></div>
        <span class="progress-note">{{ catalog.length }} liens uniques dans la vue « Toutes les ressources ». Progression enregistrée sur cet appareil.</span>
      </div>
      <div class="mode-panel">
        <div class="mode-switch" role="group" aria-label="Choisir les ressources à afficher">
          <button type="button" :class="{active: viewMode === 'free'}" :aria-pressed="viewMode === 'free'" @click="viewMode = 'free'">100 % gratuit</button>
          <button type="button" :class="{active: viewMode === 'all'}" :aria-pressed="viewMode === 'all'" @click="viewMode = 'all'">Toutes les ressources</button>
        </div>
        <p v-if="viewMode === 'free'" class="mode-explainer">
          {{ filteredCount }} ressources sélectionnées sans achat de cours, réparties dans les {{ orderedLevels.length }} niveaux.
          Certains labs nécessitent un compte gratuit, une machine personnelle ou des ressources système. Les certificats eux-mêmes peuvent être payants.
        </p>
        <p v-else class="mode-explainer">
          {{ catalog.length }} ressources : cours gratuits, freemium, open source et formations payantes (OffSec, INE, etc.).
          Vérifie les conditions d'accès avant toute inscription.
        </p>
      </div>
      <nav class="contents" aria-label="Sommaire de la roadmap">
        <a v-for="(section, i) in sections" :key="section.id" :href="'#' + section.id"><span class="contents-number">{{ i + 1 }}</span>{{ section.title }}</a>
      </nav>
      <div class="tools-line">
        <label for="academy-query">Rechercher un cours, une room ou un outil</label>
        <input id="academy-query" v-model="search" type="search" placeholder="Ex. Wireshark, Cobalt Strike, GOAD, Root-Me..." autocomplete="off">
        <label class="urls-checkbox"><input v-model="showUrls" type="checkbox"><span>Afficher les URL complètes</span></label>
        <p v-if="query" class="search-note">{{ searchCount }} lien{{ searchCount > 1 ? 's' : '' }} trouvé{{ searchCount > 1 ? 's' : '' }}</p>
      </div>
    </header>

    <section v-for="(section, groupIndex) in sections" :id="section.id" :key="section.id" class="curriculum-section">
      <header class="section-header">
        <span class="section-step">PARTIE {{ groupIndex + 1 }} / {{ sections.length }}</span>
        <h2>{{ section.title }}</h2>
        <p>{{ section.summary }}</p>
      </header>

      <article v-for="level in visibleLevels(section)" :id="'level-' + level.id" :key="level.id" class="level">
        <div class="level-head">
          <h3><span class="level-prefix">Niveau {{ numberFor(level.id) }}</span> <span class="dash">-</span> {{ level.title }}</h3>
          <div class="level-meta"><span class="level-count">{{ modeLinks(level.id).length }} liens</span><label class="done-toggle"><input type="checkbox" :checked="completed.includes(level.id)" @change="toggle(level.id, !completed.includes(level.id))"><span>Terminé</span></label></div>
        </div>
        <p class="level-info">{{ level.intro }}</p>
        <ul class="link-list">
          <template v-for="(item, resourceIndex) in visibleLinks(level.id)" :key="item.id + item.url">
            <li v-if="!query && resourceIndex === 0" class="resource-group-title">Pour commencer</li>
            <li v-if="!query && resourceIndex === 3" class="resource-group-title further">Pour approfondir</li>
            <li :class="{ 'key-resource': !query && resourceIndex < 3 }">
              <span class="arrow" aria-hidden="true">»</span>
              <div class="resource-line">
                <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ item.title }}</a>
                <span class="description"> - {{ describe(item) }}</span>
                <small v-if="showUrls" class="raw-url">{{ item.url }}</small>
              </div>
            </li>
          </template>
        </ul>
        <div v-if="!query && !modeLinks(level.id).length" class="no-resource">
          Exercice final : réutilise les ressources des niveaux précédents.
        </div>
        <details v-if="!query" class="level-exercise">
          <summary>Exercice pratique et objectif à atteindre</summary>
          <p><strong>À pratiquer :</strong> {{ level.exercise }}</p>
          <p><strong>Pour valider :</strong> {{ level.ready }}</p>
        </details>
      </article>
      <p v-if="query && !visibleLevels(section).length" class="no-result">Aucun résultat dans cette partie.</p>
      <a class="back-top" href="#about">↑ Retour au début</a>
    </section>

    <p class="footer-note">Le filtre gratuit sélectionne des supports accessibles sans abonnement ou achat de cours connu. Il ne garantit pas la gratuité du matériel, de l'hébergement Cloud ou des examens. Certaines plateformes limitent les heures ou demandent un compte. Les conditions changent : vérifie-les à chaque inscription. N'utilise que des labs et environnements explicitement autorisés.</p>
  </div>
</template>

<style scoped>
.academy-roadmap { color:#e4e1e9; max-width:980px; padding:3px 4px 24px; margin:auto; font-family:inherit; }
.academy-roadmap * { box-sizing:border-box; }
.about { scroll-margin-top:88px; padding:11px 0 25px; border-bottom:1px solid #37303c; }
.academy-eyebrow { font-size:.73rem!important; letter-spacing:.15em; font-weight:680; color:#b3a1d1!important; margin:0 0 13px!important; }
.about h1 { font-size:clamp(1.9rem,4vw,2.65rem)!important; letter-spacing:-.025em; color:#f6effd!important; line-height:1.17; border:0!important; margin:0 0 25px!important; padding:0!important; }
.about h2 { color:#ebe6f0!important; margin:0 0 8px!important; padding:0!important; border:0!important; font-size:1.35rem!important; }
.about>p:not(.academy-eyebrow) { color:#b9b3c1!important; max-width:770px; font-size:.9rem; line-height:1.75; margin:0 0 20px!important; }
.progress-wrap { margin:20px 0 22px; max-width:720px; }
.progress-head { display:flex; align-items:center; justify-content:space-between; gap:14px; margin:0 0 7px; font-size:.75rem; color:#b3a8bf; }
.progress-head strong { color:#d6c4e7; font-weight:650; }
.progress-track { height:5px; background:#34303a; border-radius:6px; overflow:hidden; }
.progress-track span { display:block; height:100%; background:#a783cb; transition:width .2s; }
.progress-note { display:block; font-size:.73rem; color:#98909e; margin-top:8px; }
.contents { display:flex; flex-direction:column; gap:7px; margin:25px 0 21px; border-left:2px solid #534260; padding-left:18px; max-width:720px; }
.contents a { color:#ccc5d2; text-decoration:none!important; font-size:.88rem; line-height:1.5; width:fit-content; }
.contents a:hover { color:#f0c95c; text-decoration:underline!important; }
.tools-line { display:grid; grid-template-columns:minmax(0,1fr) auto; align-items:end; gap:8px 16px; max-width:800px; margin:18px 0 0; }
.tools-line>label:first-child { grid-column:1 / -1; font-size:.76rem; color:#b7aaba; }
.tools-line input[type=search] { border:1px solid #51445d; border-radius:5px; padding:11px 12px; background:#19151e; color:#e8e2ee; font:inherit; font-size:.84rem; width:100%; min-width:0; }
.tools-line input[type=search]:focus { outline:2px solid #9d79c1; }
.urls-checkbox { display:flex; align-items:center; gap:7px; white-space:nowrap; font-size:.77rem; color:#afa4b7; cursor:pointer; padding-bottom:9px; }
.urls-checkbox input { accent-color:#ab87d4; }
.search-note { grid-column:1 / -1; font-size:.76rem; color:#b3a9ba!important; margin:3px 0!important; }
.curriculum-section { padding:22px 0 7px; border-bottom:1px solid #37303c; scroll-margin-top:82px; }
.section-header { margin:0 0 23px; }
.section-header h2 { font-size:clamp(1.35rem,3vw,1.7rem)!important; font-weight:580; color:#e4e1e7!important; letter-spacing:-.01em; border:0!important; padding:0!important; margin:0 0 7px!important; }
.section-header p { font-size:.85rem; color:#aaa3af!important; line-height:1.65; margin:0!important; }
.level { padding:0 0 28px 0; margin-bottom:25px; border-bottom:1px solid #29252f; scroll-margin-top:88px; }
.level:last-of-type { border:0; margin-bottom:0; }
.level-head { display:flex; align-items:baseline; justify-content:space-between; gap:12px; }
.level h3 { margin:0 0 5px!important; font-weight:520!important; font-size:1.07rem!important; line-height:1.55; padding:0!important; border:0!important; color:#d7d4dc!important; }
.level-prefix { color:#c8b5df; white-space:nowrap; font-weight:650; }
.dash { color:#807589; }
.done-toggle { flex-shrink:0; display:flex; gap:6px; align-items:center; color:#9c93a4; font-size:.74rem; cursor:pointer; }
.done-toggle input { width:14px; height:14px; accent-color:#9a75c3; }
.level-info { font-size:.8rem!important; color:#9e97a4!important; line-height:1.65; margin:0 0 11px!important; max-width:820px; }
.link-list { padding:0!important; margin:10px 0 0 21px!important; list-style:none!important; }
.link-list li { display:flex; align-items:flex-start; gap:9px; margin:0 0 3px!important; padding:0; line-height:1.62; font-size:.845rem; }
.arrow { flex:0 0 11px; font-weight:700; color:#b9acc9; line-height:1.55; }
.resource-line { flex:1; min-width:0; overflow-wrap:anywhere; }
.resource-line>a { color:#f1c953!important; font-size:inherit; text-decoration:none!important; font-weight:550; }
.resource-line>a:hover { color:#ffe18a!important; text-decoration:underline!important; }
.description { color:#c9c2cf; font-weight:400; }
.raw-url { display:block; font-size:.7rem; line-height:1.6; color:#8d8594; overflow-wrap:anywhere; }
.level-exercise { margin:13px 0 0 40px; font-size:.77rem; line-height:1.65; color:#aaa2b0; }
.level-exercise summary { width:fit-content; cursor:pointer; color:#bca9d1; }
.level-exercise summary:hover { color:#ead3fb; }
.level-exercise p { font-size:.77rem; color:#b8aabf!important; line-height:1.65; margin:8px 0!important; }
.level-exercise strong { color:#dbc6e9; font-weight:650; }
.no-resource { margin:7px 0 0 40px; color:#a69baf; font-size:.79rem; }
.no-result { font-size:.82rem; color:#a69faf!important; margin:0 0 18px!important; }
.back-top { display:inline-block; margin:8px 0 23px; font-size:.75rem; color:#a99ab7!important; text-decoration:none!important; }
.back-top:hover { color:#f1c953!important; }
.footer-note { margin:25px 0 0!important; font-size:.74rem; line-height:1.8; color:#9d93a6!important; }
@media(max-width:640px) { .academy-roadmap { padding:2px 0 20px; } .tools-line { display:flex; flex-direction:column; align-items:stretch; } .urls-checkbox { padding:4px 0; } .level-head { align-items:flex-start; } .done-toggle span { display:none; } .section-header { margin-bottom:21px; } .level { margin-bottom:23px; padding-bottom:25px; } .link-list { margin-left:5px!important; } .link-list li { font-size:.8rem; gap:7px; line-height:1.6; } .level-exercise { margin-left:21px; } .about h1 { margin-bottom:21px!important; } }
@media(prefers-reduced-motion:reduce) { .progress-track span { transition:none; } }

/* Academy - noir profond et violet, sans cartes superflues. */
:global(.Layout.academy-page) {
  --vp-c-bg: #0e0a15;
  --vp-c-bg-soft: #17101f;
  --vp-c-bg-alt: #130e1b;
  --vp-c-border: #34263f;
  background-color:#0e0a15;
}
:global(.academy-page .VPContent) { background:#0e0a15; }
.academy-roadmap { color:#e9e3f1; max-width:1040px; padding:14px 8px 38px; }
.about { border-bottom-color:#3e2c51; padding-bottom:31px; }
.academy-eyebrow { color:#b892e7!important; }
.about h1 { color:#faf5ff!important; font-weight:650!important; letter-spacing:-.035em; }
.about h2 { color:#d7b9ff!important; }
.about>p:not(.academy-eyebrow) { color:#c9bed4!important; }
.progress-wrap { border:1px solid #392848; border-radius:9px; padding:15px 18px; background:linear-gradient(110deg,#160f20,#110c1a); max-width:100%; }
.progress-track { background:#362742; height:6px; }
.progress-track span { background:linear-gradient(90deg,#7955b1,#c297fa); }
.progress-note { color:#aa9aba; }
.contents { max-width:none; display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:7px 15px; border:0; padding:0; margin:23px 0; }
.contents a { display:flex; align-items:baseline; gap:11px; width:auto; border:1px solid #33263e; border-radius:6px; background:#140e1c; padding:10px 13px; color:#dfd3ea!important; font-size:.79rem; }
.contents a:hover { border-color:#8160ad; background:#1c1328; color:#dfbfff!important; text-decoration:none!important; }
.contents-number { font-size:.71rem; font-weight:740; color:#bc96e7; min-width:17px; }
.tools-line { max-width:100%; border-top:1px solid #32243d; padding-top:17px; }
.tools-line input[type=search] { background:#1a1225; border-color:#5a4272; }
.tools-line input[type=search]:focus { outline-color:#aa83d3; }
.tools-line>label:first-child { color:#c7b8d8; }
.curriculum-section { border-bottom:1px solid #3a2b49; padding-top:37px; scroll-margin-top:80px; }
.section-header { margin-bottom:27px; }
.section-step { display:block; font-size:.7rem; color:#c09bfa; font-weight:730; letter-spacing:.095em; margin:0 0 7px; }
.section-header h2 { color:#f1e8ff!important; font-weight:650!important; font-size:clamp(1.35rem,2.6vw,1.75rem)!important; }
.section-header p { color:#bbaeC7!important; max-width:780px; }
.level { position:relative; border-bottom:0; border-left:2px solid #49335e; padding:0 0 25px 23px; margin-left:8px; margin-bottom:2px; }
.level:last-of-type { margin-bottom:0; border-left-color:transparent; }
.level:before { content:''; position:absolute; top:9px; left:-6px; width:10px; height:10px; background:#160e20; border:2px solid #9b74ca; border-radius:50%; }
.level:has(.done-toggle input:checked):before { background:#ba8be9; border-color:#ba8be9; }
.level-head { align-items:center; }
.level h3 { color:#f1e7fb!important; font-size:1.02rem!important; font-weight:670!important; }
.level-prefix { color:#c49aed; font-weight:740; }
.dash { color:#a48bb8; }
.level-meta { display:flex; gap:15px; align-items:center; }
.level-count { white-space:nowrap; font-size:.72rem; color:#a593b5; }
.done-toggle { color:#b8a9c4; }
.level-info { color:#bdb1c9!important; line-height:1.75; margin:3px 0 9px!important; }
.link-list { margin-left:0!important; }
.link-list li { color:#c8bfcc; font-size:.825rem; margin-bottom:4px!important; }
.link-list li.resource-group-title { margin:15px 0 8px!important; color:#cba7f6; font-size:.74rem; font-weight:740; letter-spacing:.035em; list-style:none; }
.link-list li.resource-group-title:first-child { margin-top:9px!important; }
.link-list li.resource-group-title.further { padding-top:8px; border-top:1px solid #32243e; color:#a999b8; }
.link-list .arrow { color:#a27ac8; }
.link-list .key-resource .arrow { color:#c7a2f3; }
.link-list .resource-line>a { color:#d9b6ff!important; font-weight:650; }
.link-list .key-resource .resource-line>a { color:#ead6ff!important; }
.link-list .resource-line>a:hover { color:#fff1ff!important; text-decoration:underline!important; }
.link-list .description { color:#bcb0c6; }
.raw-url { color:#9f90ae; }
.level-exercise summary { color:#bfa2dc; font-weight:560; }
.level-exercise summary:hover { color:#ead6ff; }
.level-exercise p { color:#bdb0c9!important; }
.level-exercise strong { color:#dfc8fa; }
.back-top { color:#a99bc0!important; }
.back-top:hover { color:#ead4ff!important; }
@media(max-width:700px) {
  .academy-roadmap { padding:8px 0 26px; }
  .contents { grid-template-columns:1fr; gap:5px; }
  .progress-wrap { padding:12px; }
  .level { padding-left:15px; margin-left:6px; }
  .level-meta { flex-direction:column; gap:5px; align-items:flex-end; }
  .level-count { font-size:.67rem; }
  .level h3 { font-size:.96rem!important; }
  .level-head { align-items:flex-start; }
  .link-list { margin-left:0!important; }
  .link-list li { font-size:.8rem; }
}

.mode-panel { background:#160f20; border:1px solid #493354; border-radius:9px; padding:13px 15px; margin:19px 0 22px; }
.mode-switch { display:flex; gap:8px; flex-wrap:wrap; }
.mode-switch button { background:#22182e; border:1px solid #5a4071; border-radius:6px; padding:11px 16px; color:#cbbbd9; font:inherit; font-size:.85rem; font-weight:650; cursor:pointer; }
.mode-switch button:hover { border-color:#b690e1; color:#f4e5ff; }
.mode-switch button.active { background:#604381; color:#fff; border-color:#b38cde; }
.mode-explainer { margin:11px 0 0!important; color:#c3b2d0!important; font-size:.78rem; line-height:1.7; max-width:820px; }
@media(max-width:460px){ .mode-switch button { flex:1; padding:11px 9px; font-size:.8rem; } }
</style>
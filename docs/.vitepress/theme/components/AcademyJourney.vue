<script setup lang="ts">
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
    "title": "Introduction et pré-sécurité",
    "summary": "Comprendre son ordinateur, le réseau et les premiers outils.",
    "levels": [
      "environment",
      "network-basics",
      "network-practice"
    ]
  },
  {
    "id": "linux-windows",
    "title": "Linux et Windows",
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
    "title": "Fondamentaux de la cybersécurité",
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
    "title": "Red Team - parcours débutant",
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
    "title": "Bonus Windows",
    "summary": "Consolider ses bases sur des environnements Windows dédiés à la pratique.",
    "levels": [
      "bonus-windows-labs"
    ]
  },
  {
    "id": "active-directory-red-team",
    "title": "Active Directory et Red Team",
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
    "title": "Blue Team - parcours débutant",
    "summary": "Comprendre les journaux, la détection et l'analyse d'incidents.",
    "levels": [
      "blue-logs",
      "blue-siem",
      "blue-threat"
    ]
  },
  {
    "id": "forensic-reverse",
    "title": "Forensic, reverse et malware",
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
    "title": "Cloud et domaines spécialisés",
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
    "title": "CTF et challenges avancés",
    "summary": "Appliquer sa méthode sur des défis complexes, jusqu'aux rooms très difficiles.",
    "levels": [
      "ctf-advanced",
      "extremely-hard-rooms"
    ]
  },
  {
    "id": "veilles-certifications",
    "title": "Veille, CVE et certifications",
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

function freeLinks(id: string): AssignedResource[] {
  const selected = freeSets.get(id)
  return selected ? levelLinks(id).filter(item => selected.has(normalizeUrl(item.url))) : []
}
function otherLinks(id: string): AssignedResource[] {
  const selected = freeSets.get(id)
  return levelLinks(id).filter(item => !selected?.has(normalizeUrl(item.url)))
}
</script>

<template>
  <div class="academy-longpage">
    <header id="academy-top" class="academy-hero">
      <p class="eyebrow">SKILL-ISSUE / ACADEMY</p>
      <h1>Cyber University</h1>
      <p class="hero-lead">Une roadmap chronologique pour apprendre la cybersécurité, des premières bases aux labs avancés. Un chemin gratuit est proposé à chaque niveau.</p>
      <a class="start-button" href="#premiers-pas">Commencer gratuitement <span aria-hidden="true">→</span></a>
      <p class="hero-meta">{{ orderedLevels.length }} niveaux · {{ catalog.length }} ressources · Une seule page</p>
    </header>

    <nav class="academy-index" aria-label="Sommaire">
      <h2>Les chapitres</h2>
      <ul>
        <li v-for="section in sections" :key="section.id">
          <a :href="'#' + section.id">{{ section.title }}</a>
        </li>
      </ul>
    </nav>

    <main>
      <div class="reading-note">
        <p><strong>Sans budget ?</strong> Suis les liens « Pour commencer » à chaque niveau. Les ressources « Pour approfondir » sont facultatives, et restent visibles juste après.</p>
        <p>Certains sites demandent un compte gratuit. Le matériel, les crédits Cloud et les examens peuvent entraîner des frais.</p>
      </div>

      <section v-for="section in sections" :id="section.id" :key="section.id" class="chapter">
        <header class="chapter-heading">
          <h2>{{ section.title }}</h2>
          <p>{{ section.summary }}</p>
        </header>

        <article v-for="level in levelsIn(section)" :id="'level-' + level.id" :key="level.id" class="level">
          <h3><span>Level {{ numberFor(level.id) }}</span> - {{ level.title }}</h3>
          <p class="level-intro">{{ level.intro }}</p>

          <div v-if="freeLinks(level.id).length" class="resource-group">
            <h4>Pour commencer <span>· sans achat</span></h4>
            <ul class="resource-links">
              <li v-for="item in freeLinks(level.id)" :key="item.id + item.url">
                <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ item.title }}</a>
                <span> - {{ describe(item) }}</span>
              </li>
            </ul>
          </div>

          <div v-if="otherLinks(level.id).length" class="resource-group more">
            <h4>Pour approfondir <span>· facultatif</span></h4>
            <ul class="resource-links">
              <li v-for="item in otherLinks(level.id)" :key="item.id + item.url">
                <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ item.title }}</a>
                <span> - {{ describe(item) }}</span>
                <small v-if="item.access && item.access !== 'Gratuit' && item.access !== 'Open source'"> ({{ item.access }})</small>
              </li>
            </ul>
          </div>

          <p class="practice"><strong>À pratiquer :</strong> {{ level.exercise }}</p>
        </article>
      </section>
    </main>

    <footer class="academy-footer">
      <p>Vérifie les conditions d'accès avant de t'inscrire. Pratique uniquement sur des systèmes et labs autorisés.</p>
      <a href="#academy-top">Retour en haut ↑</a>
    </footer>
  </div>
</template>

<style scoped>
.academy-longpage {
  --line: #30243c;
  --violet: #c7a0eb;
  --body: #c7bbd0;
  max-width: 980px; margin: 0 auto; padding: 12px 5px 55px;
  color: #e9e0ee; font-family: inherit;
}
.academy-longpage * { box-sizing: border-box; }
:global(.academy-page), :global(.academy-page .VPContent), :global(.academy-page .VPDoc) { background: #0c0912; }
:global(.academy-page .VPDoc .container), :global(.academy-page .VPDoc .content), :global(.academy-page .VPDoc .content-container) { max-width: 1050px !important; }
.academy-hero { padding: 30px 0 42px; border-bottom: 1px solid var(--line); }
.eyebrow { margin: 0 0 14px !important; color: #a88ac8 !important; font-size: .7rem !important; font-weight: 730; letter-spacing: .14em; }
.academy-hero h1 { margin: 0 0 15px !important; padding: 0 !important; border: 0 !important; color: #f7efff !important; font-size: clamp(2.3rem, 5.2vw, 3.35rem) !important; line-height: 1.14; letter-spacing: -.04em; font-weight: 740; }
.hero-lead { max-width: 690px; margin: 0 0 24px !important; color: #cfc2da !important; font-size: 1rem; line-height: 1.72; }
.start-button { display: inline-flex; align-items: center; gap: 12px; padding: 11px 19px; border-radius: 5px; border: 1px solid #c5a0eb; background: #ac86d0; color: #160f21 !important; font-size: .9rem; font-weight: 730; text-decoration: none !important; }
.start-button:hover { background: #caa6e8; }
.hero-meta { margin: 17px 0 0 !important; color: #9183a0 !important; font-size: .74rem; }
.academy-index { padding: 25px 0 27px; border-bottom: 1px solid var(--line); }
.academy-index h2 { margin: 0 0 14px !important; padding: 0 !important; border: 0 !important; font-size: .89rem !important; color: #ded1ea !important; }
.academy-index ul { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 7px 22px; list-style: none !important; padding: 0 !important; margin: 0 !important; }
.academy-index li { margin: 0 !important; padding: 0 !important; }
.academy-index a { font-size: .86rem; color: #bfa8d2 !important; text-decoration: none !important; line-height: 1.6; }
.academy-index a:hover { color: #f1dfff !important; text-decoration: underline !important; }
.reading-note { padding: 24px 0 0; }
.reading-note p { margin: 0 0 7px !important; max-width: 850px; color: #ab9eb7 !important; font-size: .82rem; line-height: 1.65; }
.reading-note strong { color: #ddbeef; }
.chapter { padding-top: 52px; scroll-margin-top: 96px; }
.chapter-heading { border-bottom: 1px solid #483551; padding: 0 0 14px; margin-bottom: 26px; }
.chapter-heading h2 { margin: 0 0 7px !important; padding: 0 !important; border: 0 !important; color: #e1c5f8 !important; font-size: clamp(1.45rem, 3vw, 1.95rem) !important; font-weight: 710; line-height: 1.32; letter-spacing: -.02em; }
.chapter-heading p { margin: 0 !important; color: #b0a3bc !important; font-size: .88rem; line-height: 1.64; }
.level { margin-bottom: 39px; scroll-margin-top: 96px; }
.level h3 { margin: 0 0 7px !important; padding: 0 !important; border: 0 !important; color: #f1e9f7 !important; font-size: clamp(1.075rem, 2.2vw, 1.24rem) !important; line-height: 1.5; font-weight: 680; overflow-wrap: break-word; }
.level h3 span { color: #c5a0ee; }
.level-intro { margin: 0 0 15px !important; color: #b2a4bc !important; font-size: .87rem; line-height: 1.68; }
.resource-group { margin: 13px 0 15px; }
.resource-group h4 { margin: 0 0 9px !important; padding: 0 !important; border: 0 !important; color: #dcbff4 !important; font-size: .84rem !important; line-height: 1.4; font-weight: 680; }
.resource-group h4 span { color: #9b8ba8; font-weight: 430; }
.resource-group.more h4 { color: #bfaecc !important; }
.resource-links { list-style: none !important; margin: 0 !important; padding: 0 0 0 22px !important; }
.resource-links li { position: relative; margin: 0 0 7px !important; padding: 0 !important; color: var(--body); font-size: .93rem; line-height: 1.68; overflow-wrap: anywhere; }
.resource-links li::before { content: "»"; position: absolute; left: -22px; color: #a47bce; font-weight: 750; }
.resource-links a { color: #d9b6fa !important; text-decoration: none !important; font-weight: 640; }
.resource-links a:hover { color: #f7eaff !important; text-decoration: underline !important; text-underline-offset: 3px; }
.resource-links small { color: #9a8aac; font-size: .74rem; }
.practice { margin: 19px 0 0 !important; padding-top: 10px; border-top: 1px solid #231a2d; font-size: .8rem; color: #9b8da9 !important; line-height: 1.65; }
.practice strong { color: #b7a0c7; font-weight: 640; }
.academy-footer { border-top: 1px solid var(--line); margin-top: 54px; padding-top: 22px; }
.academy-footer p { margin: 0 0 13px !important; font-size: .77rem; color: #978ba3 !important; line-height: 1.7; }
.academy-footer a { color: #d0b0ed !important; font-size: .84rem; text-decoration: none !important; }
.academy-footer a:hover { text-decoration: underline !important; }
.start-button:focus-visible, .academy-index a:focus-visible, .resource-links a:focus-visible, .academy-footer a:focus-visible { outline: 2px solid #dab4fd; outline-offset: 3px; }
@media (max-width: 650px) {
  .academy-longpage { padding: 5px 0 43px; }
  .academy-hero { padding: 20px 0 31px; }
  .academy-hero h1 { font-size: clamp(2.15rem, 10vw, 2.9rem) !important; }
  .hero-lead { font-size: .96rem; }
  .academy-index ul { grid-template-columns: 1fr; }
  .chapter { padding-top: 36px; }
  .chapter-heading { margin-bottom: 22px; }
  .level { margin-bottom: 34px; }
  .level h3 { font-size: 1.1rem !important; }
  .resource-links li { font-size: .92rem; line-height: 1.65; margin-bottom: 9px !important; }
  .resource-links { padding-left: 20px !important; }
  .resource-links li::before { left: -20px; }
}
@media (prefers-reduced-motion: reduce) { .start-button { transition: none; } }
</style>

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
    id: 'introduction-and-pre-security',
    title: 'Introduction and Pre-Security',
    summary: 'Les bases indispensables avant les premiers challenges.',
    levels: ['environment', 'linux-basics', 'linux-admin', 'network-basics', 'network-practice', 'windows-basics', 'powershell', 'python-basics', 'scripting', 'web-basics', 'web-api', 'security-basics', 'crypto']
  },
  {
    id: 'free-beginner-red-team-path',
    title: 'Free Beginner Red Team Path',
    summary: 'Reconnaissance, outils, Web, pentest, Active Directory et C2.',
    levels: ['osint-recon', 'scanning', 'web-security', 'web-labs', 'ctf-beginner', 'pentest-system', 'ad-intro', 'ad-minilab', 'ad-light', 'ad-full', 'c2', 'red-advanced']
  },
  {
    id: 'free-beginner-blue-team-path',
    title: 'Free Beginner Blue Team Path',
    summary: 'Détection, investigation, forensic, analyse de malware et autres environnements.',
    levels: ['blue-logs', 'blue-siem', 'blue-threat', 'dfir-network', 'dfir-host', 'reverse', 'malware', 'cloud-foundations', 'cloud-security', 'containers', 'mobile', 'iot', 'ot', 'grc']
  },
  {
    id: 'bonus-ctf-practice-and-latest-cves',
    title: 'Bonus CTF practice and Latest CVEs',
    summary: 'Challenges supplémentaires, CVE, veille et ressources pour aller plus loin.',
    levels: ['ctf-intermediate', 'research', 'certifications', 'community']
  },
  {
    id: 'bonus-windows',
    title: 'Bonus Windows',
    summary: 'Machines et challenges Windows complémentaires.',
    levels: ['bonus-windows-labs']
  },
  {
    id: 'extremely-hard-rooms-to-do',
    title: 'Extremely Hard Rooms to do',
    summary: 'Challenges exigeants et projet de synthèse.',
    levels: ['ctf-advanced', 'extremely-hard-rooms', 'final-project']
  }
] as const

const supplementary: Level[] = [
  {
    id: 'bonus-windows-labs',
    title: 'Windows - challenges complémentaires',
    intro: 'Applique les fondamentaux Windows, Active Directory et pentest sur des rooms dédiées.',
    learn: ['Analyse les services Windows, les permissions et les configurations du lab.'],
    exercise: 'Résoudre deux rooms Windows puis consigner les commandes, résultats et corrections.',
    ready: 'Tu peux expliquer le cheminement d’une room Windows sans solution préremplie.'
  },
  {
    id: 'extremely-hard-rooms',
    title: 'Rooms très difficiles',
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

const windowsRooms = new Set(['attacktive directory', 'retro', 'blue print', 'anthem', 'relevant'])
const hardRooms = new Set([
  'ra', 'cct2019', 'theseus', 'ironcorp', 'carpe diem 1', 'borderlands',
  'jeff', 'year of the owl', 'anonymous playground', 'enterprize',
  'racetrack bank', 'python playground'
])
const bonusLabs = new Set([
  'smag grotto', 'dogcat', 'buffer overflow prep', 'break out the cage',
  'lian yu', 'insecure kubernetes', 'the great escape (docker)',
  'solr exploiting log4j', 'spring4shell', 'most recent threats',
  'post exploitation basics', 'bandit', 'natas'
])
const sourceItems: Resource[] = [...resources, ...masteryResources, ...academyExtraResources] as Resource[]
const resourceMap = new Map<string, AssignedResource>()
for (const item of sourceItems) {
  // Retirer les ressources Cisco, NetAcad et Packet Tracer, pas les cours réseau neutres.
  if (/cisco|netacad|packet.?tracer/i.test(item.title + ' ' + item.url)) continue
  const key = normalizeUrl(item.url)
  if (resourceMap.has(key)) continue
  const title = simplify(item.title.trim())
  let routeLevel = item.routeLevel || academyAssignments[item.id] || 'research'
  if (windowsRooms.has(title)) routeLevel = 'bonus-windows-labs'
  else if (hardRooms.has(title)) routeLevel = 'extremely-hard-rooms'
  else if (bonusLabs.has(title)) routeLevel = 'ctf-intermediate'
  if (!byId.has(routeLevel)) routeLevel = 'research'
  resourceMap.set(key, { ...item, routeLevel })
}
const catalog = [...resourceMap.values()]
const linksByLevel = new Map<string, AssignedResource[]>()
for (const level of orderedLevels) linksByLevel.set(level.id, [])
for (const item of catalog) linksByLevel.get(item.routeLevel)?.push(item)

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
  'caldera - émulation et lab c2': 'Plateforme open source d’émulation adversaire.'
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

const storageKey = 'skill-issue-academy-single-route-v1'
const completed = ref<string[]>([])
const search = ref('')
const showUrls = ref(false)
const doneCount = computed(() => orderedLevels.filter(l => completed.value.includes(l.id)).length)
const progress = computed(() => Math.round((doneCount.value / orderedLevels.length) * 100))
const query = computed(() => simplify(search.value.trim()))
function visibleLinks(id: string) {
  const base = levelLinks(id)
  if (!query.value) return base
  const level = byId.get(id)
  if (level && simplify(level.title + ' ' + level.intro).includes(query.value)) return base
  return base.filter(item => simplify(item.title + ' ' + item.url + ' ' + (item.description || '')).includes(query.value))
}
function visibleLevels(section: typeof sections[number]) {
  if (!query.value) return levelsIn(section)
  return levelsIn(section).filter(level => visibleLinks(level.id).length > 0)
}
const searchCount = computed(() => query.value ? orderedLevels.reduce((n, l) => n + visibleLinks(l.id).length, 0) : catalog.length)
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
      <h1>Cybersecurity Roadmap</h1>
      <h2>About</h2>
      <p>Une seule route, du premier terminal aux labs avancés. Les niveaux se suivent dans l’ordre. Les ressources sont directement accessibles sous chaque niveau, avec une courte explication.</p>
      <div class="progress-wrap">
        <div class="progress-head"><span>Progression</span><strong>{{ doneCount }} / {{ orderedLevels.length }} niveaux terminés</strong></div>
        <div class="progress-track" role="progressbar" aria-label="Progression de la roadmap" :aria-valuenow="doneCount" :aria-valuemin="0" :aria-valuemax="orderedLevels.length"><span :style="{width: progress + '%'}"></span></div>
        <span class="progress-note">{{ catalog.length }} liens uniques, classés dans une seule roadmap. Progression enregistrée sur cet appareil.</span>
      </div>
      <nav class="contents" aria-label="Sommaire de la roadmap">
        <a href="#about">About</a>
        <a v-for="section in sections" :key="section.id" :href="'#' + section.id">{{ section.title }}</a>
      </nav>
      <div class="tools-line">
        <label for="academy-query">Rechercher un cours, une room ou un outil</label>
        <input id="academy-query" v-model="search" type="search" placeholder="Ex. Wireshark, Cobalt Strike, GOAD, Root-Me..." autocomplete="off">
        <label class="urls-checkbox"><input v-model="showUrls" type="checkbox"><span>Afficher les URL complètes</span></label>
        <p v-if="query" class="search-note">{{ searchCount }} lien{{ searchCount > 1 ? 's' : '' }} trouvé{{ searchCount > 1 ? 's' : '' }}</p>
      </div>
    </header>

    <section v-for="section in sections" :id="section.id" :key="section.id" class="curriculum-section">
      <header class="section-header">
        <h2>{{ section.title }}</h2>
        <p>{{ section.summary }}</p>
      </header>

      <article v-for="level in visibleLevels(section)" :id="'level-' + level.id" :key="level.id" class="level">
        <div class="level-head">
          <h3><span class="level-prefix">Level {{ numberFor(level.id) }}</span> <span class="dash">-</span> {{ level.title }}</h3>
          <label class="done-toggle"><input type="checkbox" :checked="completed.includes(level.id)" @change="toggle(level.id, !completed.includes(level.id))"><span>Terminé</span></label>
        </div>
        <p class="level-info">{{ level.intro }}</p>
        <ul class="link-list">
          <li v-for="item in visibleLinks(level.id)" :key="item.id + item.url">
            <span class="arrow" aria-hidden="true">»</span>
            <div class="resource-line">
              <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ item.title }}</a>
              <span class="description"> - {{ describe(item) }}</span>
              <small v-if="showUrls" class="raw-url">{{ item.url }}</small>
            </div>
          </li>
        </ul>
        <div v-if="!query && !levelLinks(level.id).length" class="no-resource">
          Exercice final : réutilise les ressources des niveaux précédents.
        </div>
        <details v-if="!query" class="level-exercise">
          <summary>Exercice et validation</summary>
          <p><strong>À pratiquer :</strong> {{ level.exercise }}</p>
          <p><strong>Pour valider :</strong> {{ level.ready }}</p>
        </details>
      </article>
      <p v-if="query && !visibleLevels(section).length" class="no-result">Aucun résultat dans cette partie.</p>
      <a class="back-top" href="#about">↑ Retour au sommaire</a>
    </section>

    <p class="footer-note">Les liens externes peuvent évoluer ou nécessiter un compte ou un abonnement. Vérifie les conditions d’accès avant de commencer. Utilise uniquement des labs ou environnements pour lesquels tu disposes d’une autorisation.</p>
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
</style>
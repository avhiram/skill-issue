<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { resources } from '../data/academy-organized'
import { masteryResources } from '../data/academy-mastery'
import { academyLevels, academyExtraResources, academyAssignments } from '../data/academy-unified'

type Resource = { id: string; title: string; url: string; category?: string; access?: string; description?: string; featured?: boolean; routeLevel?: string }
type RouteResource = Resource & { routeLevel: string }

const storageKey = 'skill-issue-academy-single-route-v1'
const oldStorageKey = 'skill-issue-academy-path-v1'
const activeIndex = ref(0)
const completed = ref<string[]>([])
const search = ref('')
const openPhase = ref('')
const showAll = ref(false)
const normUrl = (s: string) => s.trim().replace(/^http:/i, 'https:').replace(/^https:\/\/www\./i, 'https://').replace(/\/+$/, '').toLowerCase()
const norm = (s: string) => s.toLocaleLowerCase('fr').normalize('NFD').replace(/[\u0300-\u036f]/g, '')
const levelIds = new Set<string>(academyLevels.map(x => x.id))
const levelNumbers = new Map<string, number>(academyLevels.map((x, i) => [x.id, i]))
const catalogMap = new Map<string, RouteResource>()

// Une URL ne figure qu'une fois dans la route. Les liens des deux catalogues d'origine sont tous importés.
for (const item of [...resources, ...masteryResources, ...academyExtraResources] as Resource[]) {
  const key = normUrl(item.url)
  if (catalogMap.has(key)) continue
  const selectedLevel = item.routeLevel || academyAssignments[item.id] || 'research'
  catalogMap.set(key, { ...item, routeLevel: levelIds.has(selectedLevel) ? selectedLevel : 'research' })
}
const catalog = [...catalogMap.values()]
const groups = (() => {
  const result: Array<{ name: string; items: Array<{ id: string; title: string }> }> = []
  for (const level of academyLevels) {
    let group = result.find(g => g.name === level.phase)
    if (!group) {
      group = { name: level.phase, items: [] }
      result.push(group)
    }
    group.items.push(level)
  }
  return result
})()
const phaseOf = (index: number) => academyLevels[index].phase
const doneCount = computed(() => completed.value.filter(id => levelIds.has(id)).length)
const progress = computed(() => Math.round(doneCount.value / academyLevels.length * 100))
const active = computed(() => academyLevels[activeIndex.value])
const activeLinks = computed(() => {
  const top = active.value.featured.map(x => normUrl(x))
  return catalog.filter(x => x.routeLevel === active.value.id).sort((a, b) => {
    const ia = top.indexOf(normUrl(a.url))
    const ib = top.indexOf(normUrl(b.url))
    if (ia !== -1 && ib !== -1) return ia - ib
    if (ia !== -1) return -1
    if (ib !== -1) return 1
    if (a.featured && !b.featured) return -1
    if (!a.featured && b.featured) return 1
    return a.title.localeCompare(b.title, 'fr')
  })
})
const priorityLinks = computed(() => activeLinks.value.slice(0, 4))
const otherLinks = computed(() => activeLinks.value.slice(4))
const byLevel = (id: string) => catalog.filter(x => x.routeLevel === id).length
const completedInPhase = (items: Array<{ id: string }>) => items.filter(x => completed.value.includes(x.id)).length
const matches = computed(() => {
  const query = norm(search.value.trim())
  if (!query) return []
  return catalog.filter(x => {
    const i = levelNumbers.get(x.routeLevel) ?? 0
    const level = academyLevels[i]
    return norm([x.title, x.url, x.category || '', level.title, level.phase].join(' ')).includes(query)
  })
})
const shownMatches = computed(() => matches.value.slice(0, 60))
watch(activeIndex, () => { showAll.value = false; openPhase.value = phaseOf(activeIndex.value) })

function save() {
  try { localStorage.setItem(storageKey, JSON.stringify(completed.value)) } catch {}
}
function choose(index: number, scroll = true) {
  if (index < 0 || index >= academyLevels.length) return
  activeIndex.value = index
  openPhase.value = phaseOf(index)
  if (typeof window !== 'undefined') {
    window.history.replaceState(null, '', '#level-' + academyLevels[index].id)
    if (scroll) nextTick(() => document.getElementById('academy-level-detail')?.scrollIntoView({
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      block: 'start'
    }))
  }
}
function finish() {
  const id = active.value.id
  if (!completed.value.includes(id)) completed.value = [...completed.value, id]
  save()
  if (activeIndex.value < academyLevels.length - 1) choose(activeIndex.value + 1)
}
function toggleDone(id: string) {
  completed.value = completed.value.includes(id) ? completed.value.filter(x => x !== id) : [...completed.value, id]
  save()
}
function goToResource(item: RouteResource) {
  const index = levelNumbers.get(item.routeLevel)
  if (typeof index === 'number') choose(index)
  search.value = ''
}

onMounted(() => {
  try {
    const raw = JSON.parse(localStorage.getItem(storageKey) || '[]')
    if (Array.isArray(raw)) completed.value = raw.filter((x: unknown): x is string => typeof x === 'string' && levelIds.has(x))
    else completed.value = []
  } catch { completed.value = [] }
  if (!completed.value.length) {
    // Conserver les niveaux déjà validés dans l'ancienne Academy.
    const oldToNew: Record<string, string> = {
      environment: 'environment', network: 'network-basics', linux: 'linux-basics',
      windows: 'windows-basics', web: 'web-basics', scripting: 'python-basics',
      security: 'security-basics', tools: 'scanning', challenges: 'ctf-beginner',
      'local-lab': 'web-labs', project: 'final-project'
    }
    try {
      const old = JSON.parse(localStorage.getItem(oldStorageKey) || '[]')
      if (Array.isArray(old)) {
        completed.value = [...new Set(old.filter((x: unknown): x is string => typeof x === 'string' && x.startsWith('core-'))
          .map(x => oldToNew[x.slice(5)]).filter((x): x is string => !!x))]
        if (completed.value.length) save()
      }
    } catch {}
  }
  let index = academyLevels.findIndex(level => !completed.value.includes(level.id))
  const hash = decodeURIComponent(window.location.hash.slice(1))
  if (hash.startsWith('level-')) {
    const found = academyLevels.findIndex(level => level.id === hash.slice(6))
    if (found >= 0) index = found
  }
  activeIndex.value = index >= 0 ? index : academyLevels.length - 1
  openPhase.value = phaseOf(activeIndex.value)
})
</script>

<template>
  <div class="academy">
    <header class="intro">
      <div class="eyebrow"><span class="pulse"></span> ACADEMY / CYBERSECURITY</div>
      <h1>Une seule roadmap.<br><span>Du premier terminal aux labs avancés.</span></h1>
      <p class="intro-copy">Suis les niveaux dans l'ordre. Chaque étape contient les notions à apprendre, un exercice et ses ressources. Toutes les thématiques font partie du même parcours.</p>
      <div class="top-stats">
        <div><strong>{{ academyLevels.length }}</strong><span>Niveaux</span></div>
        <div><strong>{{ catalog.length }}</strong><span>Ressources classées</span></div>
        <div><strong>{{ progress }} %</strong><span>Progression</span></div>
      </div>
      <div class="progress-line" role="progressbar" aria-label="Avancement du parcours" :aria-valuenow="doneCount" :aria-valuemin="0" :aria-valuemax="academyLevels.length">
        <span :style="{ width: progress + '%' }"></span>
      </div>
      <div class="progress-caption"><span>{{ doneCount }} / {{ academyLevels.length }} niveaux terminés</span><span>Enregistré sur cet appareil</span></div>
    </header>

    <section class="search-panel" aria-label="Trouver une ressource">
      <label for="academy-search">Rechercher dans toute la roadmap</label>
      <div class="search-wrap">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.7"/><path d="m16 16 5 5"/></svg>
        <input id="academy-search" v-model="search" type="search" autocomplete="off" placeholder="Cobalt Strike, Root-Me, GOAD, Python, Wireshark...">
      </div>
      <div v-if="search.trim()" class="search-results">
        <p>{{ matches.length }} résultat{{ matches.length > 1 ? 's' : '' }} dans le parcours <span v-if="matches.length > shownMatches.length">- 60 premiers affichés</span></p>
        <div v-for="item in shownMatches" :key="item.id + item.url" class="search-hit">
          <button type="button" @click="goToResource(item)">
            <small>NIVEAU {{ String((levelNumbers.get(item.routeLevel) ?? 0) + 1).padStart(2, '0') }}</small>
            <strong>{{ item.title }}</strong>
          </button>
          <a :href="item.url" target="_blank" rel="noopener noreferrer" :aria-label="'Ouvrir '+item.title">↗</a>
        </div>
        <p v-if="!matches.length">Aucune ressource trouvée.</p>
      </div>
    </section>

    <div class="workspace">
      <nav class="path" aria-label="Roadmap chronologique">
        <div class="path-heading"><span>LE PARCOURS</span><strong>{{ academyLevels.length }} étapes</strong></div>
        <section v-for="(group, gi) in groups" :key="group.name" class="phase">
          <button type="button" class="phase-button" :aria-expanded="openPhase === group.name"
            @click="openPhase = openPhase === group.name ? '' : group.name">
            <span class="phase-dot" :class="{ visited: completedInPhase(group.items) === group.items.length }"></span>
            <span class="phase-name">{{ group.name }}</span>
            <span class="phase-progress">{{ completedInPhase(group.items) }}/{{ group.items.length }}</span>
            <span class="chevron" :class="{ expanded: openPhase === group.name }">⌄</span>
          </button>
          <div v-if="openPhase === group.name" class="phase-items">
            <button v-for="entry in group.items" :key="entry.id" type="button" class="path-entry"
              :class="{ selected: active.id === entry.id, finished: completed.includes(entry.id) }"
              :aria-current="active.id === entry.id ? 'step' : undefined"
              @click="choose(levelNumbers.get(entry.id) ?? 0)">
              <span class="level-number">{{ String((levelNumbers.get(entry.id) ?? 0) + 1).padStart(2, '0') }}</span>
              <span class="level-label">{{ entry.title }}</span>
              <span v-if="completed.includes(entry.id)" class="checkmark" aria-label="Terminé">✓</span>
            </button>
          </div>
        </section>
      </nav>

      <main id="academy-level-detail" class="level-card">
        <div class="level-meta">
          <span class="level-chip">NIVEAU {{ String(activeIndex + 1).padStart(2, '0') }} / {{ academyLevels.length }}</span>
          <span class="phase-tag">{{ active.phase }}</span>
        </div>
        <h2>{{ active.title }}</h2>
        <p class="level-intro">{{ active.intro }}</p>
        <div class="section-divider"></div>
        <section class="lesson-section">
          <h3><span class="section-index">01</span> Ce que tu vas apprendre</h3>
          <ul class="learn-list"><li v-for="l in active.learn" :key="l">{{ l }}</li></ul>
        </section>
        <section class="lesson-section">
          <h3><span class="section-index">02</span> Exercice pratique</h3>
          <p class="exercise">{{ active.exercise }}</p>
        </section>
        <section class="lesson-section">
          <div class="resource-title">
            <h3><span class="section-index">03</span> Ressources du niveau</h3>
            <span class="count">{{ activeLinks.length }} liens</span>
          </div>
          <p class="subline">Commence par ces ressources. Les autres liens sont juste en dessous, dans ce même niveau.</p>
          <div class="resource-grid">
            <a v-for="r in priorityLinks" :key="r.url" :href="r.url" target="_blank" rel="noopener noreferrer" class="resource primary-resource">
              <span class="resource-kind">Ressource recommandée</span>
              <span class="resource-name">{{ r.title }} <span aria-hidden="true">↗</span></span>
              <small>{{ r.url }}</small>
            </a>
          </div>
          <div v-if="otherLinks.length" class="extra-links">
            <button type="button" class="show-more" :aria-expanded="showAll" @click="showAll = !showAll">
              <span>{{ showAll ? 'Masquer les ressources complémentaires' : 'Afficher les '+otherLinks.length+' autres ressources du niveau' }}</span>
              <span>{{ showAll ? '−' : '+' }}</span>
            </button>
            <div v-if="showAll" class="extra-resource-list">
              <a v-for="r in otherLinks" :key="r.url" :href="r.url" target="_blank" rel="noopener noreferrer" class="extra-resource">
                <span>{{ r.title }}</span>
                <small>{{ r.url }}</small>
                <span class="open-symbol" aria-hidden="true">↗</span>
              </a>
            </div>
          </div>
          <p v-if="!activeLinks.length" class="empty-links">Projet de synthèse : réutilise les ressources des niveaux précédents et rédige ton propre rapport.</p>
        </section>
        <section class="check-section">
          <div><span class="check-label">POUR VALIDER CE NIVEAU</span><p>{{ active.ready }}</p></div>
          <label class="manual-done"><input type="checkbox" :checked="completed.includes(active.id)" @change="toggleDone(active.id)"><span>Validé</span></label>
        </section>
        <footer class="actions">
          <button type="button" class="secondary-btn" :disabled="activeIndex === 0" @click="choose(activeIndex - 1)">← Précédent</button>
          <button type="button" class="next-btn" @click="finish">{{ activeIndex === academyLevels.length - 1 ? 'Terminer le parcours ✓' : 'Valider et continuer →' }}</button>
        </footer>
        <p class="last-note">Les ressources sont classées par thème et par progression. Certaines nécessitent un compte, sont payantes ou peuvent avoir changé d'adresse. Les labs doivent rester isolés et autorisés.</p>
      </main>
    </div>
  </div>
</template>

<style scoped>
.academy { --bg:#100d17; --surface:#171120; --border:#362945; --ink:#f0e9f7; --muted:#b1a4be; --accent:#c1a4ed; width:100%; max-width:1180px; margin:0 auto; color:var(--ink); font-family:inherit; }
.academy * { box-sizing:border-box; }
.intro { border:1px solid var(--border); border-radius:14px; padding:28px 30px 23px; background:radial-gradient(ellipse at top right,rgba(125,79,175,.19),transparent 55%),#110e19; }
.eyebrow { font-size:.72rem; font-weight:750; letter-spacing:.13em; color:#bda4d9; display:flex; align-items:center; gap:9px; margin-bottom:13px; }
.pulse { width:7px; height:7px; border-radius:50%; background:#c19bf5; box-shadow:0 0 0 4px #38254e; }
.intro h1 { font-size:clamp(1.55rem,3vw,2.35rem)!important; line-height:1.22; margin:0 0 12px!important; color:#f6efff!important; letter-spacing:-.035em; border:0!important; padding:0!important; }
.intro h1 span { color:#be9fea; }
.intro-copy { max-width:720px; font-size:.92rem; line-height:1.65; color:#c0b4cf!important; margin:0 0 25px!important; }
.top-stats { display:flex; gap:0; margin:0 0 14px; }
.top-stats>div { display:flex; flex-direction:column; min-width:150px; gap:3px; padding:0 21px; border-left:1px solid #423252; }
.top-stats>div:first-child { padding-left:0; border-left:0; }
.top-stats strong { font-size:1.5rem; font-weight:750; color:#ecdefa; }
.top-stats span { font-size:.75rem; color:#a99aba; }
.progress-line { height:7px; background:#31263c; border-radius:30px; overflow:hidden; }
.progress-line span { background:linear-gradient(90deg,#8e61c5,#c8a4f3); display:block; height:100%; transition:width .22s ease; }
.progress-caption { display:flex; justify-content:space-between; gap:10px; font-size:.72rem; color:#9e90af; margin-top:9px; }
.search-panel { margin:17px 0 20px; border:1px solid var(--border); border-radius:11px; padding:14px 16px; background:#120e1b; }
.search-panel>label { display:block; margin-bottom:8px; font-size:.77rem; font-weight:680; color:#c5b3dd; }
.search-wrap { display:flex; align-items:center; gap:11px; padding:10px 12px; border-radius:7px; border:1px solid #48365b; background:#1b1426; color:#a990c7; }
.search-wrap:focus-within { outline:2px solid #9470b9; outline-offset:1px; }
.search-wrap input { flex:1; min-width:0; background:transparent; border:0; outline:0; color:#f5ecff; font:inherit; font-size:.87rem; }
.search-wrap input::placeholder { color:#9a88ae; }
.search-results { border-top:1px solid #3c2d4b; margin-top:13px; padding-top:8px; max-height:400px; overflow-y:auto; }
.search-results>p { margin:3px 0 10px!important; color:#ad9cbe!important; font-size:.76rem; }
.search-hit { display:flex; align-items:center; border-bottom:1px solid #30253d; }
.search-hit button { text-align:left; display:flex; gap:9px; flex:1; align-items:center; padding:10px 4px; color:#dfcef1; border:0; background:transparent; cursor:pointer; font:inherit; }
.search-hit button:hover strong { text-decoration:underline; }
.search-hit small { font-size:.69rem; flex-shrink:0; color:#b399d0; font-weight:680; }
.search-hit strong { font-size:.81rem; font-weight:590; }
.search-hit a { color:#bda3db; padding:8px 10px; text-decoration:none!important; }
.workspace { display:grid; grid-template-columns:minmax(245px,320px) minmax(0,1fr); gap:18px; align-items:start; }
.path { border:1px solid var(--border); border-radius:12px; background:#100d17; padding:9px; position:sticky; top:76px; max-height:calc(100vh - 90px); overflow-y:auto; scrollbar-width:thin; }
.path-heading { padding:12px 11px 14px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #32263f; }
.path-heading span { font-size:.73rem; letter-spacing:.1em; font-weight:750; color:#c3a9e2; }
.path-heading strong { font-size:.71rem; color:#9e8db1; font-weight:600; }
.phase { position:relative; border-bottom:1px solid #2c2235; padding:3px 0; }
.phase:last-child { border-bottom:0; }
.phase-button { display:flex; width:100%; align-items:center; gap:10px; padding:13px 8px; color:#ded0ed; background:transparent; border:0; border-radius:7px; font:inherit; text-align:left; cursor:pointer; }
.phase-button:hover { background:#1b1524; }
.phase-dot { flex:0 0 9px; width:9px; height:9px; border:2px solid #9871b6; border-radius:50%; }
.phase-dot.visited { background:#b79ae0; }
.phase-name { font-size:.84rem; font-weight:700; flex:1; }
.phase-progress { color:#aa98be; font-size:.72rem; }
.chevron { color:#ab97c0; font-size:1.1rem; transition:transform .15s; }
.chevron.expanded { transform:rotate(180deg); }
.phase-items { margin-left:12px; padding:2px 0 11px 12px; border-left:1px solid #443050; }
.path-entry { display:flex; align-items:center; gap:10px; padding:10px 9px; width:100%; background:transparent; color:#afa1bf; border:1px solid transparent; border-radius:7px; cursor:pointer; text-align:left; font:inherit; transition:background .14s; }
.path-entry:hover { background:#21182c; color:#ece0f6; }
.path-entry.selected { background:#2e1e40; border-color:#8055a6; color:#f4eaff; box-shadow:inset 3px 0 #b58bde; }
.path-entry.finished:not(.selected) { color:#d3c0e9; }
.level-number { font-size:.71rem; font-weight:760; color:#ad91d0; flex:0 0 19px; }
.level-label { flex:1; font-size:.79rem; font-weight:570; line-height:1.37; }
.checkmark { color:#c5aae9; font-size:.83rem; font-weight:700; }
.level-card { min-width:0; scroll-margin-top:82px; padding:27px 28px 22px; background:#15101d; border:1px solid #49355c; border-radius:13px; box-shadow:0 8px 30px #00000015; }
.level-meta { display:flex; justify-content:space-between; flex-wrap:wrap; align-items:center; gap:8px; }
.level-chip { color:#cbaaf1; background:#2a1b3a; border:1px solid #63487f; border-radius:5px; padding:6px 9px; font-size:.69rem; font-weight:760; letter-spacing:.055em; }
.phase-tag { color:#a89ab5; font-size:.73rem; }
.level-card h2 { font-size:clamp(1.25rem,2.5vw,1.8rem)!important; margin:18px 0 8px!important; padding:0!important; border:0!important; color:#f5ecff!important; line-height:1.24; letter-spacing:-.018em; }
.level-intro { color:#bdafcb!important; font-size:.88rem; line-height:1.7; margin:0!important; }
.section-divider { height:1px; background:#382943; margin:22px 0 20px; }
.lesson-section { margin-bottom:23px; }
.lesson-section h3 { display:flex; align-items:center; gap:12px; margin:0 0 12px!important; color:#eee0fb!important; font-size:.99rem!important; font-weight:700; border:0!important; padding:0!important; }
.section-index { font-size:.71rem; font-weight:750; color:#b899d9; flex:0 0 21px; }
.learn-list { padding-left:23px!important; margin:0!important; color:#c7b9d2; font-size:.84rem; line-height:1.8; }
.learn-list li { padding-left:5px; margin:4px 0; }
.exercise { background:#20172b; border-left:2px solid #a47bcb; border-radius:0 7px 7px 0; padding:12px 15px; margin:0!important; font-size:.83rem; line-height:1.7; color:#dfd1eb!important; }
.resource-title { display:flex; align-items:center; justify-content:space-between; gap:10px; }
.resource-title h3 { margin-bottom:6px!important; }
.count { font-size:.72rem; color:#b69ccc; white-space:nowrap; }
.subline { font-size:.77rem; line-height:1.55; color:#a99bb6!important; margin:0 0 13px!important; }
.resource-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:9px; }
.resource { display:flex; flex-direction:column; gap:8px; background:#211729; border:1px solid #4d385e; border-radius:8px; padding:12px 13px; min-width:0; text-decoration:none!important; transition:border-color .16s,background .16s; }
.resource:hover { background:#2a1e36; border-color:#b78cdd; }
.resource-kind { font-size:.68rem; color:#aa91c7; }
.resource-name { font-size:.83rem; line-height:1.45; font-weight:680; color:#f0e3ff; }
.resource-name>span { color:#b8a0d4; }
.resource small { font-size:.68rem; line-height:1.4; color:#a89ab7; overflow-wrap:anywhere; }
.extra-links { margin-top:10px; }
.show-more { width:100%; display:flex; justify-content:space-between; align-items:center; gap:15px; border:1px solid #473453; background:#1c1425; border-radius:8px; padding:11px 12px; text-align:left; font:inherit; color:#d6bdec; font-size:.82rem; cursor:pointer; }
.show-more:hover { border-color:#8b69ae; background:#23182e; }
.extra-resource-list { margin-top:7px; border:1px solid #352942; border-radius:8px; overflow:hidden; }
.extra-resource { display:grid; grid-template-columns:1fr auto; gap:3px 10px; border-bottom:1px solid #30253b; padding:11px 12px; text-decoration:none!important; }
.extra-resource:last-child { border-bottom:0; }
.extra-resource:hover { background:#201729; }
.extra-resource>span:first-child { color:#dccced; font-size:.79rem; font-weight:610; grid-column:1; }
.extra-resource small { grid-column:1; color:#9586a5; font-size:.67rem; overflow-wrap:anywhere; }
.extra-resource .open-symbol { grid-column:2; grid-row:1 / span 2; align-self:center; color:#b79ad5; }
.empty-links { padding:15px; background:#20182b; border-radius:7px; color:#baacc8!important; font-size:.82rem; line-height:1.65; }
.check-section { border:1px solid #58406d; border-radius:9px; background:#24182f; display:flex; align-items:center; gap:12px; justify-content:space-between; padding:14px 16px; }
.check-label { font-size:.67rem; color:#c4a2e8; letter-spacing:.075em; font-weight:740; }
.check-section p { color:#d5c7e2!important; font-size:.8rem; line-height:1.6; margin:5px 0 0!important; }
.manual-done { display:flex; gap:7px; align-items:center; flex-shrink:0; color:#e3c9f7; font-size:.77rem; cursor:pointer; }
.manual-done input { width:16px; height:16px; accent-color:#9970ca; }
.actions { display:flex; justify-content:space-between; gap:10px; margin-top:18px; }
.actions button { padding:12px 15px; border-radius:8px; font-size:.82rem; font-weight:680; font-family:inherit; cursor:pointer; }
.secondary-btn { color:#d3bde5; background:transparent; border:1px solid #6a507e; }
.secondary-btn:disabled { opacity:.4; cursor:not-allowed; }
.next-btn { color:#fff7ff; background:#6a468d; border:1px solid #906bb1; }
.next-btn:hover { background:#79549c; }
.last-note { font-size:.71rem; color:#9689a5!important; line-height:1.65; margin:16px 0 0!important; }
@media(max-width:960px) { .workspace { grid-template-columns:minmax(210px,270px) minmax(0,1fr); gap:12px; } .level-card { padding:22px 20px; } .intro { padding:23px; } }
@media(max-width:760px) { .workspace { grid-template-columns:1fr; } .path { position:static; max-height:300px; } .top-stats>div { min-width:0; flex:1; padding:0 12px; } .top-stats strong { font-size:1.2rem; } .path-heading { position:sticky; top:0; background:#100d17; z-index:2; } .resource-grid { grid-template-columns:1fr; } .level-card { padding:20px 17px; } .intro { padding:20px 17px; } .intro-copy { font-size:.85rem; } .progress-caption { flex-wrap:wrap; } .phase-items { padding-bottom:7px; } }
@media(max-width:400px) { .check-section { flex-direction:column; align-items:flex-start; } .actions button { padding:11px 10px; } }
@media(prefers-reduced-motion:reduce) { .progress-line span, .resource, .phase-button, .path-entry { transition:none; } }
</style>
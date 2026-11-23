<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { journey, branches } from '../data/academy-journey'
import { resources, categories } from '../data/academy-organized'
import { masteryResources } from '../data/academy-mastery'

type ResourceLink = { id: string; title: string; url: string; category: string }
const storageKey = 'skill-issue-academy-path-v1'
const levelIndex = ref(0)
const selectedBranchId = ref('pentest')
const completed = ref<string[]>([])
const query = ref('')
const filterCategory = ref('reseau')

const classNames: Record<string,string> = {
  fondamentaux: 'Bases',
  reseau: 'Réseau',
  systemes: 'Linux & Windows',
  programmation: 'Python & Scripting',
  web: 'Web & API',
  red: 'Pentest / Red Team',
  ad: 'Active Directory',
  blue: 'Blue Team / SOC',
  dfir: 'DFIR / Forensic',
  cloud: 'Cloud',
  reverse: 'Reverse Engineering',
  crypto: 'Cryptographie',
  ot: 'OT / ICS',
  ctf: 'CTF & Labs',
  mobile: 'Mobile',
  iot: 'IoT',
  osint: 'OSINT',
  grc: 'GRC',
  carriere: 'Carrière',
  veille: 'Veille',
  communaute: 'Communautés',
  formations: 'Formations',
  outils: 'Outils'
}
const subjectGroups = [
  { label: 'Bases', ids: ['fondamentaux', 'reseau', 'systemes', 'programmation'] },
  { label: 'Pratique', ids: ['ctf', 'web', 'red', 'ad'] },
  { label: 'Défense', ids: ['blue', 'dfir', 'grc'] },
  { label: 'Autres domaines', ids: ['cloud', 'reverse', 'crypto', 'ot', 'iot', 'mobile', 'osint', 'outils', 'formations', 'veille', 'communaute', 'carriere'] }
]
const canon = (s: string) => s.trim().replace(/^http:/i, 'https:').replace(/^https:\/\/www\./i, 'https://').replace(/\/+$/, '').toLowerCase()
const catalog: ResourceLink[] = (() => {
  const m = new Map<string, ResourceLink>()
  for (const r of [...resources, ...masteryResources]) {
    const key = canon(r.url)
    if (!m.has(key)) m.set(key, { id: r.id, title: r.title, url: r.url, category: r.category })
  }
  return [...m.values()]
})()
const step = computed(() => journey[levelIndex.value])
const selectedBranch = computed(() => branches.find(b => b.id === selectedBranchId.value) || branches[0])
const doneCount = computed(() => journey.filter(s => completed.value.includes('core-' + s.id)).length)
const branchCount = (id: string) => {
  const b = branches.find(x => x.id === id)
  return b?.sections.filter((_:unknown,i:number) => completed.value.includes('branch-' + id + '-' + i)).length || 0
}
const norm = (s:string) => s.toLocaleLowerCase('fr').normalize('NFD').replace(/[\u0300-\u036f]/g,'')
const results = computed(() => {
  const needle = norm(query.value.trim())
  return catalog.filter(r =>
    (filterCategory.value === 'all' || r.category === filterCategory.value) &&
    (!needle || norm([r.title, r.url, classNames[r.category] || r.category].join(' ')).includes(needle))
  ).sort((a,b) => (classNames[a.category] || a.category).localeCompare(classNames[b.category] || b.category,'fr') || a.title.localeCompare(b.title,'fr'))
})
const categoryCount = (id:string) => catalog.filter(r => r.category === id).length

onMounted(() => {
  try {
    const raw = JSON.parse(localStorage.getItem(storageKey) || '[]')
    if (Array.isArray(raw)) completed.value = raw.filter((x:unknown):x is string => typeof x === 'string')
  } catch { completed.value = [] }
  const hash = decodeURIComponent(window.location.hash.substring(1))
  if (hash.startsWith('level-')) {
    const found = journey.findIndex(s => s.id === hash.substring(6))
    if (found !== -1) levelIndex.value = found
  } else {
    const first = journey.findIndex(s => !completed.value.includes('core-' + s.id))
    if (first !== -1) levelIndex.value = first
  }
  if (hash.startsWith('specialite-')) {
    const v = hash.substring('specialite-'.length)
    if (branches.some(b => b.id === v)) selectedBranchId.value = v
  }
})
function persist() {
  try { localStorage.setItem(storageKey, JSON.stringify(completed.value)) } catch {}
}
function selectLevel(i:number,scroll=true) {
  if (i < 0 || i >= journey.length) return
  levelIndex.value = i
  if (typeof window !== 'undefined') {
    window.history.replaceState(null, '', '#level-' + journey[i].id)
    if (scroll) nextTick(() => document.getElementById('rm-detail')?.scrollIntoView({
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',
      block:'start'
    }))
  }
}
function finishLevel() {
  const key = 'core-' + step.value.id
  if (!completed.value.includes(key)) completed.value.push(key)
  persist()
  if (levelIndex.value < journey.length - 1) selectLevel(levelIndex.value + 1)
  else if (typeof window !== 'undefined') document.getElementById('specialisations')?.scrollIntoView({ behavior:'smooth', block:'start' })
}
function selectBranch(id:string) {
  if (!branches.some(b => b.id === id)) return
  selectedBranchId.value = id
  if (typeof window !== 'undefined') {
    window.history.replaceState(null, '', '#specialite-' + id)
    nextTick(() => document.getElementById('rm-branch-detail')?.scrollIntoView({ behavior:'smooth',block:'start' }))
  }
}
function toggleBranch(i:number) {
  const key = 'branch-' + selectedBranch.value.id + '-' + i
  completed.value = completed.value.includes(key) ? completed.value.filter(x=>x!==key) : [...completed.value, key]
  persist()
}
</script>

<template>
<div class="rm">
  <div class="rm-intro">
    <p class="rm-intro-main">Un parcours de zéro à la pratique. Chaque niveau prépare le suivant.</p>
    <div class="rm-progress-head"><span>Ton avancement</span><strong>{{ doneCount }} / {{ journey.length }} niveaux</strong></div>
    <div class="rm-progress-track" role="progressbar" aria-label="Progression" :aria-valuemin="0" :aria-valuemax="journey.length" :aria-valuenow="doneCount"><span :style="{width:doneCount/journey.length*100+'%'}"></span></div>
    <span class="rm-progress-note">Progression conservée sur cet appareil.</span>
  </div>

  <section id="parcours" class="rm-section">
    <div class="rm-section-title"><h2>Roadmap</h2><p>Commence au Level 0 et avance dans l'ordre.</p></div>
    <div class="rm-columns">
      <nav class="rm-levels" aria-label="Les niveaux du parcours">
        <button v-for="(s,i) in journey" :key="s.id" type="button" class="rm-level"
          :class="{active:i===levelIndex,done:completed.includes('core-'+s.id)}"
          :aria-current="i===levelIndex?'step':undefined" @click="selectLevel(i)">
          <span class="rm-level-num">{{String(i).padStart(2,'0')}}</span>
          <span class="rm-level-name">{{s.title}}</span>
          <span v-if="completed.includes('core-'+s.id)" class="rm-done-symbol" aria-label="Terminé">✓</span>
        </button>
      </nav>
      <article id="rm-detail" class="rm-detail">
        <div class="rm-detail-head">
          <span class="rm-kicker">LEVEL {{ levelIndex }}</span>
          <h3>{{step.title}}</h3>
          <p>{{step.intro}}</p>
        </div>
        <div class="rm-detail-section">
          <h4>À apprendre</h4>
          <ul><li v-for="v in step.learn" :key="v">{{v}}</li></ul>
        </div>
        <div class="rm-detail-section">
          <h4>Exercice pratique</h4>
          <p>{{step.exercise}}</p>
        </div>
        <div class="rm-detail-section">
          <h4>Ressources</h4>
          <div class="rm-resources">
            <a v-for="r in step.links" :key="r.url" :href="r.url" target="_blank" rel="noopener noreferrer">
              <strong>{{r.title}} <span aria-hidden="true">↗</span></strong>
              <small>{{r.url}}</small>
            </a>
          </div>
        </div>
        <p class="rm-ready"><strong>Pour passer à la suite :</strong> {{step.ready}}</p>
        <div class="rm-actions">
          <button type="button" class="rm-primary" @click="finishLevel">
            {{ levelIndex===journey.length-1 ? 'Terminer le parcours de base' : 'Terminer et continuer' }}
          </button>
          <button v-if="levelIndex<journey.length-1" type="button" class="rm-secondary" @click="selectLevel(levelIndex+1)">Suivant</button>
        </div>
      </article>
    </div>
  </section>

  <section id="specialisations" class="rm-section">
    <div class="rm-section-title"><h2>Choisir une spécialisation</h2><p>Après les bases, choisis un domaine et suis ses quatre étapes.</p></div>
    <div class="rm-branches">
      <button v-for="b in branches" :key="b.id" type="button" class="rm-branch"
        :class="{active:selectedBranchId===b.id}" :aria-pressed="selectedBranchId===b.id"
        @click="selectBranch(b.id)">
        <span class="rm-branch-title">{{b.title}}</span><span class="rm-branch-desc">{{b.desc}}</span>
        <span class="rm-branch-count">{{branchCount(b.id)}} / {{b.sections.length}} étapes</span>
      </button>
    </div>
    <div id="rm-branch-detail" class="rm-branch-detail">
      <h3>{{selectedBranch.title}}</h3>
      <p>{{selectedBranch.desc}}</p>
      <div v-for="(s,i) in selectedBranch.sections" :key="selectedBranch.id+'-'+i" class="rm-branch-step">
        <div class="rm-branch-step-header">
          <span class="rm-branch-index">{{String(i+1).padStart(2,'0')}}</span>
          <div><h4>{{s.title}}</h4><p>{{s.goal}}</p></div>
          <label class="rm-check">
            <input type="checkbox" :checked="completed.includes('branch-'+selectedBranch.id+'-'+i)"
              :aria-label="'Étape terminée : '+s.title" @change="toggleBranch(i)">
            <span>Terminé</span>
          </label>
        </div>
        <div class="rm-branch-step-links">
          <a v-for="r in s.links" :key="r.url" :href="r.url" target="_blank" rel="noopener noreferrer">
            <strong>{{r.title}} <span aria-hidden="true">↗</span></strong>
            <small>{{r.url}}</small>
          </a>
        </div>
      </div>
    </div>
  </section>

  <section id="annuaire" class="rm-section">
    <details class="rm-directory">
      <summary><span><strong>Bibliothèque complète</strong><small>{{catalog.length}} liens classés et recherchables</small></span><span class="rm-expand" aria-hidden="true">⌄</span></summary>
      <div class="rm-directory-body">
        <p>Tous les cours, labs, outils et références sont rangés ici, sans doublons.</p>
        <div class="rm-search-controls">
          <label><span>Rechercher</span><input v-model="query" type="search" placeholder="Root-Me, GOAD, Wireshark, OSINT..." autocomplete="off"></label>
          <label><span>Catégorie</span><select v-model="filterCategory">
            <option value="all">Toutes les catégories</option>
            <optgroup v-for="group in subjectGroups" :key="group.label" :label="group.label">
              <option v-for="id in group.ids" :key="id" :value="id">{{classNames[id] || id}} ({{categoryCount(id)}})</option>
            </optgroup>
          </select></label>
        </div>
        <p class="rm-result-count" aria-live="polite">{{results.length}} liens</p>
        <div class="rm-directory-rows">
          <a v-for="r in results" :key="r.id+'-'+r.url" :href="r.url" target="_blank" rel="noopener noreferrer" class="rm-directory-row">
            <span>{{r.title}} <span aria-hidden="true">↗</span></span><small>{{r.url}}</small>
          </a>
          <p v-if="!results.length" class="rm-no-result">Aucun résultat. Modifie les filtres.</p>
        </div>
        <p class="rm-foot">Certains liens de l'annuaire peuvent nécessiter un compte, un abonnement ou une infrastructure payante. Les labs vulnérables doivent rester dans un environnement isolé et autorisé.</p>
      </div>
    </details>
  </section>
</div>
</template>

<style scoped>
.rm{color:#eee8f7;width:100%;max-width:1000px}
.rm-intro{background:#120e19;border:1px solid #372a46;border-radius:11px;padding:19px 20px;margin:15px 0 31px}
.rm-intro-main{font-size:1.02rem!important;color:#e4dcee!important;margin:0 0 16px!important;line-height:1.6}
.rm-progress-head{display:flex;justify-content:space-between;gap:10px;color:#b5a9c1;font-size:.8rem}
.rm-progress-head strong{color:#dfcafd}
.rm-progress-track{height:6px;background:#30253f;border-radius:8px;overflow:hidden;margin:10px 0 6px}
.rm-progress-track>span{display:block;height:100%;background:#aa8cdb;transition:width .2s}
.rm-progress-note{color:#988ca6;font-size:.73rem}
.rm-section{margin:32px 0 37px;scroll-margin-top:78px}
.rm-section-title{margin-bottom:18px}
.rm-section-title h2{font-size:1.37rem!important;margin:0 0 6px!important;padding:0!important;border:0!important;color:#ecdefd!important}
.rm-section-title p{font-size:.85rem;color:#b1a5c1!important;margin:0!important}
.rm-columns{display:grid;grid-template-columns:minmax(200px,280px) minmax(0,1fr);gap:16px;align-items:start}
.rm-levels{display:flex;flex-direction:column;gap:5px;border:1px solid #34283f;border-radius:10px;background:#100d17;padding:9px}
.rm-level{display:flex;gap:12px;align-items:center;text-align:left;width:100%;padding:10px 11px;background:transparent;border:1px solid transparent;color:#c6bace;cursor:pointer;border-radius:7px;font-size:.85rem}
.rm-level:hover{background:#1b1427}
.rm-level.active{background:#261a37;border-color:#765595;color:#f1e7ff}
.rm-level-num{font-size:.77rem;font-weight:720;color:#a78ec9;flex:0 0 21px}
.rm-level-name{flex:1;font-weight:610}
.rm-done-symbol{color:#b79ee2;font-weight:700}
.rm-detail{scroll-margin-top:87px;border:1px solid #443155;border-radius:11px;background:#120e1a;padding:22px 23px;min-width:0}
.rm-detail-head{padding-bottom:13px;border-bottom:1px solid #382a49}
.rm-kicker{color:#c6a8ec;font-size:.7rem;font-weight:740;letter-spacing:.1em}
.rm-detail h3{margin:5px 0 7px!important;font-size:1.35rem!important;color:#f0e5ff!important}
.rm-detail-head p{margin:0!important;color:#bfb1ce!important;line-height:1.6;font-size:.91rem}
.rm-detail-section{margin-top:18px}
.rm-detail-section h4{margin:0 0 9px!important;font-size:.88rem!important;font-weight:710;color:#e1cbfb!important}
.rm-detail-section ul{margin:0!important;padding-left:19px!important;color:#c2b7cd;font-size:.86rem;line-height:1.7}
.rm-detail-section li{margin:4px 0}
.rm-detail-section>p{font-size:.87rem;color:#c1b4ce!important;line-height:1.6;margin:0!important}
.rm-resources{display:grid;gap:7px}
.rm-resources a,.rm-branch-step-links a{display:flex;flex-direction:column;gap:3px;text-decoration:none!important;color:#ded0f6!important;padding:9px 11px;border:1px solid #3b2b4d;background:#1c1527;border-radius:7px;min-width:0}
.rm-resources a:hover,.rm-branch-step-links a:hover{border-color:#956fbc;background:#251a35}
.rm-resources strong,.rm-branch-step-links strong{font-weight:650;font-size:.84rem}
.rm-resources small,.rm-branch-step-links small{font-size:.7rem;color:#9e91ad;overflow-wrap:anywhere;line-height:1.4}
.rm-ready{margin:19px 0 0!important;font-size:.82rem;line-height:1.6;color:#c5b7d4!important;border-left:2px solid #8060a5;padding-left:11px}
.rm-actions{display:flex;flex-wrap:wrap;gap:9px;margin-top:18px}
.rm-actions button{cursor:pointer;font:inherit;font-size:.83rem;font-weight:620;padding:10px 14px;border-radius:7px;border:1px solid #6c4d8d}
.rm-primary{background:#47315f;color:#f8efff}
.rm-primary:hover{background:#594074}
.rm-secondary{background:transparent;color:#c7aedf}
.rm-secondary:hover{background:#21162e}
.rm-branches{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}
.rm-branch{display:flex;flex-direction:column;gap:7px;text-align:left;min-height:100px;padding:14px;cursor:pointer;border:1px solid #372944;background:#120e1b;border-radius:9px}
.rm-branch.active{border-color:#9771bd;background:#1e152b}
.rm-branch:hover{border-color:#74578d}
.rm-branch-title{font-size:.91rem;font-weight:710;color:#eee4f9}
.rm-branch-desc{font-size:.78rem;line-height:1.43;color:#ab9eb9;flex:1}
.rm-branch-count{font-size:.72rem;color:#bba5d3}
.rm-branch-detail{scroll-margin-top:86px;border:1px solid #3b2c4c;border-radius:11px;background:#110d19;padding:19px;margin:14px 0 0}
.rm-branch-detail>h3{margin:0 0 5px!important;font-size:1.1rem!important;color:#eadbf9!important}
.rm-branch-detail>p{margin:0 0 18px!important;font-size:.85rem;color:#aea3bb!important}
.rm-branch-step{padding:14px 0;border-top:1px solid #33263f}
.rm-branch-step-header{display:flex;gap:12px;align-items:flex-start}
.rm-branch-index{font-size:.78rem;font-weight:740;color:#b99dd8;flex:0 0 22px}
.rm-branch-step-header>div{flex:1;min-width:0}
.rm-branch-step h4{margin:0 0 4px!important;font-size:.9rem!important;font-weight:700;color:#dfcafa!important}
.rm-branch-step p{margin:0!important;font-size:.82rem;color:#b6a9c2!important;line-height:1.5}
.rm-check{display:flex;align-items:center;gap:6px;font-size:.72rem;color:#afa1be;cursor:pointer}
.rm-check input{width:15px;height:15px;accent-color:#9873c5}
.rm-branch-step-links{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin:10px 0 0 34px}
.rm-directory{border:1px solid #392a49;background:#100d17;border-radius:10px;overflow:hidden}
.rm-directory summary{display:flex;align-items:center;justify-content:space-between;gap:10px;cursor:pointer;list-style:none;padding:17px 19px}
.rm-directory summary::-webkit-details-marker{display:none}
.rm-directory summary>span:first-child{display:flex;flex-direction:column;gap:5px}
.rm-directory summary strong{font-size:.98rem;color:#e9ddf8}
.rm-directory summary small{font-size:.78rem;color:#9f91ae}
.rm-expand{color:#b99ed5}
.rm-directory[open] .rm-expand{transform:rotate(180deg)}
.rm-directory-body{padding:0 19px 19px;border-top:1px solid #34263f}
.rm-directory-body>p{color:#ada0bb!important;font-size:.81rem;margin:14px 0!important}
.rm-search-controls{display:grid;grid-template-columns:1.3fr 1fr;gap:10px;margin:14px 0}
.rm-search-controls label{display:flex;flex-direction:column;gap:6px;font-size:.79rem;color:#b9a9c8}
.rm-search-controls input,.rm-search-controls select{border:1px solid #4b375d;background:#181120;color:#eadff9;border-radius:7px;padding:10px 11px;font:inherit;font-size:.85rem;box-sizing:border-box;width:100%;min-width:0}
.rm-search-controls :is(input,select):focus{outline:2px solid #9b7ac1;outline-offset:1px}
.rm-result-count{font-size:.77rem!important;margin:8px 0!important;color:#b5a6c3!important}
.rm-directory-rows{border-top:1px solid #352841}
.rm-directory-row{padding:10px 3px;border-bottom:1px solid #2c2235;display:flex;flex-direction:column;gap:4px;text-decoration:none!important}
.rm-directory-row span{font-size:.85rem;color:#e1d2f6}
.rm-directory-row:hover span{text-decoration:underline}
.rm-directory-row small{font-size:.7rem;color:#a498af;overflow-wrap:anywhere}
.rm-foot{font-size:.73rem!important;color:#998fa6!important;line-height:1.55}
.rm-no-result{font-size:.82rem;color:#ad9abf;padding:10px}
@media(max-width:820px){.rm-columns{grid-template-columns:minmax(180px,230px) minmax(0,1fr)}.rm-branches{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:640px){.rm-intro{padding:15px}.rm-columns{grid-template-columns:1fr}.rm-levels{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:5px}.rm-level{padding:9px 7px;gap:6px;min-height:45px;font-size:.77rem}.rm-level-num{flex:0 0 18px}.rm-detail{padding:17px}.rm-branches{grid-template-columns:1fr}.rm-branch{min-height:72px}.rm-branch-step-links{grid-template-columns:1fr}.rm-search-controls{grid-template-columns:1fr}.rm-branch-detail{padding:15px}.rm-check span{display:none}}
@media(prefers-reduced-motion:reduce){.rm-progress-track>span{transition:none}}
</style>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { withBase } from 'vitepress'
import { examGroups as groups } from '../examNavigation'

type Link = { label: string; path: string }
type Task = { id: string; text: string }
type Stage = { id: string; title: string; tasks: Task[]; links: Link[] }
const stages: Stage[] = [
  { id:'prep', title:'Préparation', tasks:[
    {id:'rules',text:'Lire les consignes officielles et les restrictions applicables.'},
    {id:'workspace',text:'Préparer un espace de travail et vérifier la connexion au laboratoire.'},
    {id:'scope',text:'Noter le périmètre autorisé et les objectifs de l’exercice.'}
  ],links:[{label:'Consignes officielles',path:'/oscp/references'},{label:'Utilitaires',path:'/oscp/utilitaires'},{label:'PimpMyKali · Préparer une VM Kali',path:'https://github.com/Dewalt-arch/pimpmykali'}]},
  { id:'inventory',title:'Inventaire et résultats',tasks:[
    {id:'hosts',text:'Consigner les machines du périmètre et les services identifiés.'},
    {id:'results',text:'Conserver les résultats bruts et les observations.'}
  ],links:[{label:'Reconnaissance',path:'/oscp/reconnaissance'},{label:'Nmap · Exam Mode',path:'/oscp/exam-nmap'},{label:'Référence Nmap complète',path:'/oscp/reconnaissance#nmap'},{label:'Services par port',path:'/oscp/reconnaissance#services-par-port'}]},
  { id:'analysis',title:'Analyse et références',tasks:[
    {id:'observations',text:'Classer les observations par machine et par technologie.'},
    {id:'validation',text:'Distinguer les hypothèses, les vérifications et les résultats confirmés.'}
  ],links:[{label:'Méthodologie OSCP',path:'/oscp/methodologie'},{label:'Applications Web',path:'/oscp/applications-web'},{label:'Mindmaps',path:'/oscp/mindmaps'}]},
  { id:'systems',title:'Documentation des systèmes',tasks:[
    {id:'system-context',text:'Consigner le contexte système, les comptes et les permissions observés.'}
  ],links:[{label:'Références Windows',path:'/oscp/privileges-windows'},{label:'Références Linux',path:'/oscp/privileges-linux'},{label:'Transferts de fichiers',path:'/oscp/transferts'}]},
  { id:'ad',title:'Active Directory',tasks:[
    {id:'domain-context',text:'Documenter les machines, le domaine et les observations pertinentes si cet environnement est présent.'}
  ],links:[{label:'Active Directory',path:'/oscp/active-directory'},{label:'Théorie Active Directory',path:'/oscp/ad-theorie'},{label:'Mindmap AD',path:'/oscp/mindmap-ad'}]},
  { id:'evidence',title:'Preuves et rapport',tasks:[
    {id:'evidence-context',text:'Associer chaque preuve à la machine et au constat correspondant.'},
    {id:'report',text:'Vérifier les captures, le rapport et les critères de remise.'}
  ],links:[{label:'Rédaction du rapport',path:'/oscp/rapport'},{label:'Critères officiels',path:'/oscp/references'}]}
]
const preparation=stages.find(stage=>stage.id==='prep')!
const key = 'skill-issue:exam-oscp:v1'
const completed = ref<string[]>([])
const expanded = ref<string[]>([])
const confirmingReset = ref(false)
const total = stages.reduce((sum,s)=>sum+s.tasks.length,0)
const valid = new Set(stages.flatMap(s=>s.tasks.map(t=>t.id)))
const percent = computed(()=>Math.round(completed.value.length / total * 100))
function completedCount(stage: Stage) { return stage.tasks.filter(t=>completed.value.includes(t.id)).length }
function persist() { try { localStorage.setItem(key,JSON.stringify(completed.value)) } catch {} }
function toggleTask(id:string) {
  if (!valid.has(id)) return
  completed.value=completed.value.includes(id)?completed.value.filter(x=>x!==id):[...completed.value,id]
  persist()
}
function toggleStage(id:string) { expanded.value=expanded.value.includes(id)?[]:[id] }
function reset() { completed.value=[]; expanded.value=[]; confirmingReset.value=false; persist() }
onMounted(()=>{
  try {
    const data=JSON.parse(localStorage.getItem(key)||'[]')
    if(Array.isArray(data)) completed.value=[...new Set(data.filter(x=>typeof x==='string'&&valid.has(x)))] as string[]
  } catch {}
  expanded.value=[]
})
</script>

<template>
  <div class="exam-workspace">
    <details class="exam-fold">
      <summary>Avant l’examen <span aria-hidden="true">⌄</span></summary>
      <div class="exam-fold-body">
        <div class="exam-links">
          <a v-for="link in preparation.links" :key="link.path" :href="link.path.startsWith('https://') ? link.path : withBase(link.path)" :target="link.path.startsWith('https://') ? '_blank' : undefined" :rel="link.path.startsWith('https://') ? 'noopener noreferrer' : undefined">{{ link.label }} <span aria-hidden="true">›</span></a>
        </div>
        <p class="exam-local-note">PimpMyKali : facultatif, sur une VM Kali compatible, avant l’épreuve. Créer un snapshot, lire le script et vérifier les outils après installation.</p>
      </div>
    </details>
    <nav class="exam-quick" aria-label="Parcours de travail">
      <section v-for="group in groups" :key="group.title" class="exam-group">
        <h2 class="exam-group-title">{{ group.title }}</h2>
        <a v-for="link in group.links" :key="link.path" :href="withBase(link.path)">
          <span>{{ link.label }}</span>
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>
        </a>
      </section>
    </nav>
    <details class="exam-fold">
      <summary>Checklist <span class="exam-count">{{ completed.length }}/{{ total }} <span aria-hidden="true">⌄</span></span></summary>
      <div class="exam-fold-body">
        <div class="exam-progress" aria-label="Progression locale de la checklist">
          <progress :value="completed.length" :max="total" :aria-label="'Progression : '+percent+' %'" />
          <span>{{ percent }} %</span>
        </div>
        <section v-for="stage in stages" :key="stage.id" class="exam-stage">
          <button type="button" class="exam-stage-title" :aria-expanded="expanded.includes(stage.id)" :aria-controls="'exam-body-'+stage.id" @click="toggleStage(stage.id)">
            <span>{{ stage.title }}</span>
            <small>{{ completedCount(stage) }}/{{ stage.tasks.length }}</small>
            <span class="exam-chevron" :class="{'is-open':expanded.includes(stage.id)}" aria-hidden="true">›</span>
          </button>
          <div v-show="expanded.includes(stage.id)" :id="'exam-body-'+stage.id" class="exam-stage-body">
            <label v-for="task in stage.tasks" :key="task.id" class="exam-task">
              <input type="checkbox" :checked="completed.includes(task.id)" @change="toggleTask(task.id)">
              <span>{{ task.text }}</span>
            </label>
            <div v-if="stage.id!=='prep'" class="exam-links">
              <a v-for="link in stage.links" :key="link.path" :href="withBase(link.path)">{{ link.label }} <span aria-hidden="true">›</span></a>
            </div>
          </div>
        </section>
        <div class="exam-footer"><small>Progression locale</small><button type="button" @click="confirmingReset=true">Réinitialiser</button></div>
        <div v-if="confirmingReset" class="exam-confirm">
          <span>Effacer la progression ?</span>
          <button type="button" @click="reset">Confirmer</button>
          <button type="button" @click="confirmingReset=false">Annuler</button>
        </div>
      </div>
    </details>
  </div>
</template>
<style scoped>
.exam-workspace { display:grid; gap:12px; margin-top:12px; color:var(--vp-c-text-1); min-width:0; }
.exam-quick { display:grid; gap:14px; }
.exam-group { min-width:0; }
.exam-workspace .exam-group-title { margin:0 0 2px !important; padding:0 0 4px !important; border:0 !important; color:#b39aff; font-size:12px; font-weight:650; line-height:1.5; letter-spacing:0; }
.exam-quick a,.exam-links a { display:flex; align-items:center; justify-content:space-between; gap:8px; color:#e6d9f6; text-decoration:none; font-size:14px; font-weight:550; line-height:1.35; min-width:0; }
.exam-quick a { min-height:44px; padding:9px 4px; border-bottom:1px solid #29213a; }
.exam-quick a svg { flex:none; color:#b39aff; }
.exam-quick a:hover,.exam-links a:hover { color:#f0e4ff; background:#1b1425; }
.exam-quick a:active,.exam-links a:active { background:#302043; }
.exam-quick a:focus-visible,.exam-fold summary:focus-visible { outline:2px solid #b39aff; outline-offset:2px; }
.exam-workspace .exam-fold { margin:0; padding:0; border:1px solid #3f304e; border-radius:9px; background:#15101e; }
.exam-workspace .exam-fold > summary { display:flex; align-items:center; justify-content:space-between; gap:8px; min-height:48px; margin:0; padding:10px 12px; cursor:pointer; list-style:none; color:#cdbbe4; font-size:13px; font-weight:600; }
.exam-fold > summary::-webkit-details-marker { display:none; }
.exam-fold > summary > span { color:#ad98c7; }
.exam-fold[open] > summary > span:last-child:not(.exam-count) { transform:rotate(180deg); }
.exam-count { font-variant-numeric:tabular-nums; display:inline-flex; gap:9px; align-items:center; white-space:nowrap; }
.exam-fold-body { display:grid; gap:8px; padding:10px 12px; border-top:1px solid #3f304e; }
.exam-progress { display:flex; align-items:center; gap:10px; font-size:12px; color:#bfa5e5; }
.exam-progress progress { width:100%; min-width:0; height:6px; accent-color:#b39aff; }
.exam-progress > span { white-space:nowrap; }
.exam-stage { border-bottom:1px solid #36283f; }
.exam-stage-title { width:100%; min-height:44px; display:flex; align-items:center; gap:8px; text-align:left; font-size:13px; font-weight:600; color:#e4d6f1; }
.exam-stage-title > span:first-child { flex:1; }
.exam-stage-title small { font-size:11px; color:#b39fc6; white-space:nowrap; }
.exam-chevron { color:#b39aff; font-size:20px; }
.exam-chevron.is-open { transform:rotate(90deg); }
.exam-stage-body { display:grid; gap:4px; padding:4px 0 12px; }
.exam-task { display:flex; gap:9px; align-items:flex-start; min-height:44px; padding:8px 0; color:#ded3ea; font-size:13px; line-height:1.45; cursor:pointer; }
.exam-task input { width:18px; height:18px; flex:none; margin-top:2px; accent-color:#b39aff; }
.exam-links { display:flex; flex-wrap:wrap; gap:6px; }
.exam-links a { min-height:44px; font-size:12px; padding:8px 10px; border:1px solid #40304f; border-radius:7px; background:#191320; }
.exam-local-note { color:#b5a5c6; font-size:12px; margin:0 !important; line-height:1.5; }
.exam-footer,.exam-confirm { display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:8px; color:#b5a5c6; font-size:12px; }
.exam-footer button,.exam-confirm button { min-height:44px; padding:6px 8px; color:#dcc7f7; font-size:12px; }
.exam-confirm button { border:1px solid #4d3a64; border-radius:6px; }
@media(max-width:420px) { .exam-quick { gap:12px; } .exam-quick a { font-size:14px; padding:8px 4px; } }
</style>

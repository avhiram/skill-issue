<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { withBase } from 'vitepress'

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
const key = 'skill-issue:exam-oscp:v1'
const completed = ref<string[]>([])
const expanded = ref<string[]>(['prep'])
const confirmingReset = ref(false)
const total = stages.reduce((sum,s)=>sum+s.tasks.length,0)
const valid = new Set(stages.flatMap(s=>s.tasks.map(t=>t.id)))
const percent = computed(()=>Math.round(completed.value.length / total * 100))
const nextStage = computed(()=>stages.find(s=>s.tasks.some(t=>!completed.value.includes(t.id))))
function completedCount(stage: Stage) { return stage.tasks.filter(t=>completed.value.includes(t.id)).length }
function persist() { try { localStorage.setItem(key,JSON.stringify(completed.value)) } catch {} }
function toggleTask(id:string) {
  if (!valid.has(id)) return
  completed.value=completed.value.includes(id)?completed.value.filter(x=>x!==id):[...completed.value,id]
  persist()
}
function toggleStage(id:string) { expanded.value=expanded.value.includes(id)?expanded.value.filter(x=>x!==id):[...expanded.value,id] }
function reset() { completed.value=[]; expanded.value=['prep']; confirmingReset.value=false; persist() }
function openNext() {
  const stage=nextStage.value
  if (!stage) return
  if (!expanded.value.includes(stage.id)) expanded.value=[...expanded.value,stage.id]
  document.getElementById('exam-stage-'+stage.id)?.scrollIntoView({block:'start',behavior:'auto'})
}
onMounted(()=>{
  try {
    const data=JSON.parse(localStorage.getItem(key)||'[]')
    if(Array.isArray(data)) completed.value=[...new Set(data.filter(x=>typeof x==='string'&&valid.has(x)))] as string[]
  } catch {}
  expanded.value=nextStage.value?[nextStage.value.id]:[]
})
</script>

<template>
  <div class="exam-workspace">
    <div class="exam-quick">
      <a :href="withBase('/oscp/methodologie')">Méthodologie <span aria-hidden="true">›</span></a>
      <a :href="withBase('/oscp/exam-nmap')">Nmap <span aria-hidden="true">›</span></a>
      <a :href="withBase('/oscp/reconnaissance#services-par-port')">Ports &amp; services <span aria-hidden="true">›</span></a>
      <a :href="withBase('/oscp/references')">Règles d’examen <span aria-hidden="true">›</span></a>
    </div>
    <section class="exam-progress" aria-label="Progression locale de la checklist">
      <div class="exam-progress-head"><strong>Progression</strong><span>{{ completed.length }} / {{ total }} · {{ percent }} %</span></div>
      <progress :value="completed.length" :max="total" />
      <div class="exam-progress-actions">
        <button v-if="nextStage" type="button" class="exam-primary" @click="openNext">Reprendre · {{ nextStage.title }}</button>
        <span v-else class="exam-complete">Checklist terminée</span>
        <button type="button" class="exam-subtle" @click="confirmingReset=true">Réinitialiser</button>
      </div>
      <div v-if="confirmingReset" class="exam-confirm">
        <span>Effacer la progression de cette checklist ?</span>
        <button type="button" @click="reset">Confirmer</button>
        <button type="button" @click="confirmingReset=false">Annuler</button>
      </div>
    </section>
    <div class="exam-actions">
      <strong>Checklist</strong>
      <div><button type="button" @click="expanded=stages.map(s=>s.id)">Tout déplier</button><button type="button" @click="expanded=[]">Tout replier</button></div>
    </div>
    <section v-for="(stage,i) in stages" :id="'exam-stage-'+stage.id" :key="stage.id" class="exam-stage">
      <h2 class="exam-stage-title">
        <button type="button" :aria-expanded="expanded.includes(stage.id)" :aria-controls="'exam-body-'+stage.id" @click="toggleStage(stage.id)">
          <span class="exam-stage-number" :class="{'is-complete':completedCount(stage)===stage.tasks.length}">{{ completedCount(stage)===stage.tasks.length?'✓':i+1 }}</span>
          <span class="exam-stage-label">{{ stage.title }}</span>
          <small>{{ completedCount(stage) }}/{{ stage.tasks.length }}</small>
          <span class="exam-chevron" :class="{'is-open':expanded.includes(stage.id)}" aria-hidden="true">›</span>
        </button>
      </h2>
      <div v-show="expanded.includes(stage.id)" :id="'exam-body-'+stage.id" class="exam-stage-body">
        <label v-for="task in stage.tasks" :key="task.id" class="exam-task">
          <input type="checkbox" :checked="completed.includes(task.id)" @change="toggleTask(task.id)">
          <span>{{ task.text }}</span>
        </label>
        <p v-if="stage.id==='prep'" class="exam-local-note">PimpMyKali : facultatif, sur une VM Kali compatible, avant l’épreuve. Créer un snapshot, lire le script et vérifier les outils après installation.</p>
        <div class="exam-links">
          <a v-for="link in stage.links" :key="link.path" :href="link.path.startsWith('https://') ? link.path : withBase(link.path)" :target="link.path.startsWith('https://') ? '_blank' : undefined" :rel="link.path.startsWith('https://') ? 'noopener noreferrer' : undefined">{{ link.label }} <span aria-hidden="true">›</span></a>
        </div>
      </div>
    </section>
    <p class="exam-local-note">Progression enregistrée dans ce navigateur. Vérifier les règles de l’épreuve avant toute utilisation.</p>
  </div>
</template>
<style scoped>
.exam-workspace { display:grid; gap:12px; margin-top:20px; color:var(--vp-c-text-1); }
.exam-quick { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }
.exam-quick a,.exam-links a { display:flex; align-items:center; justify-content:space-between; gap:6px; background:#191320; color:#cfb4f5; border:1px solid #40304f; border-radius:8px; padding:10px 12px; text-decoration:none; font-size:13px; min-height:44px; }
.exam-quick a:hover,.exam-links a:hover { background:#261a36; border-color:#8966b6; }
.exam-progress { background:#191320; border:1px solid #40304f; border-radius:12px; padding:14px; display:grid; gap:12px; }
.exam-progress-head,.exam-progress-actions,.exam-actions { display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:8px; }
.exam-progress-head span { font-size:13px; color:#c4a7ec; }
.exam-progress progress { display:block; width:100%; height:7px; accent-color:#b39aff; }
.exam-primary,.exam-subtle,.exam-actions button,.exam-confirm button { min-height:40px; border:1px solid #4d3a64; border-radius:7px; padding:6px 10px; color:#dcc7f7; background:#21182c; font-size:12px; }
.exam-primary { background:#37234f; border-color:#7958a6; }
.exam-confirm { display:flex; flex-wrap:wrap; align-items:center; gap:8px; color:#cdbddd; font-size:12px; }
.exam-complete { color:#d2b9f3; font-size:13px; }
.exam-actions { margin-top:10px; color:#cdbddd; font-size:13px; }
.exam-actions > div { display:flex; gap:6px; }
.exam-stage { border:1px solid #3f304e; border-radius:10px; background:#191320; scroll-margin-top:90px; overflow:hidden; }
.exam-stage-title { margin:0 !important; padding:0 !important; border:0 !important; }
.exam-stage-title button { width:100%; min-height:62px; display:flex; align-items:center; gap:10px; text-align:left; padding:12px; }
.exam-stage-number { display:grid; place-items:center; flex:none; width:32px; height:32px; border-radius:8px; background:#2a1c3d; color:#c7a9f4; font-size:14px; }
.exam-stage-number.is-complete { background:#382653; color:#e6d4ff; }
.exam-stage-label { flex:1; font-size:15px; font-weight:650; color:#e4d6f1; line-height:1.4; }
.exam-stage-title small { font-size:12px; color:#b39fc6; white-space:nowrap; }
.exam-chevron { color:#b39aff; font-size:23px; }
.exam-chevron.is-open { transform:rotate(90deg); }
.exam-stage-body { display:grid; gap:8px; border-top:1px solid #3f304e; padding:10px 12px 12px; }
.exam-task { display:flex; gap:10px; align-items:flex-start; padding:8px 0; color:#ded3ea; font-size:14px; line-height:1.5; cursor:pointer; }
.exam-task input { width:19px; height:19px; flex:none; margin-top:2px; accent-color:#b39aff; }
.exam-links { display:flex; flex-wrap:wrap; gap:6px; padding-top:4px; }
.exam-links a { min-height:36px; padding:7px 10px; font-size:12px; }
.exam-local-note { color:#a798bb; font-size:12px; margin:0 !important; line-height:1.6; }
@media(max-width:640px) { .exam-quick { gap:6px; } .exam-quick a { padding:10px; font-size:12px; } .exam-stage-title button { gap:8px; padding:10px; } .exam-stage-label { font-size:14px; } .exam-links a { min-height:44px; } }
</style>

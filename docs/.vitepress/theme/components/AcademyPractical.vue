<script setup lang="ts">
import {computed,onMounted,ref} from 'vue'
import {academyLevels,academyOpenSource,academyOnlineLabs} from '../data/academy-practical'

const storageKey='skill-issue-academy-levels-v3'
const checked=ref<string[]>([])
const activeCategory=ref('all')
const search=ref('')
const showAll=ref(false)
const completed=(level:typeof academyLevels[number])=>level.tasks.filter(t=>checked.value.includes(t.id)).length>=level.required
const doneCount=computed(()=>academyLevels.filter(completed).length)
const labFilter=computed(()=>{
 const query=search.value.trim().toLowerCase()
 return academyOpenSource.filter(l=>(activeCategory.value==='all'||activeCategory.value===l.category)&&(!query||[l.title,l.desc,l.task,l.prereq,l.difficulty].join(' ').toLowerCase().includes(query)))
})
const shownLabs=computed(()=>showAll.value?labFilter.value:labFilter.value.slice(0,6))
onMounted(()=>{
 try{const saved=JSON.parse(localStorage.getItem(storageKey)||'[]'); const valid=new Set(academyLevels.flatMap(l=>l.tasks.map(t=>t.id)));checked.value=Array.isArray(saved)?saved.filter((v:unknown):v is string=>typeof v==='string'&&valid.has(v)):[]}catch{checked.value=[]}
})
function toggle(id:string){checked.value=checked.value.includes(id)?checked.value.filter(x=>x!==id):[...checked.value,id];try{localStorage.setItem(storageKey,JSON.stringify(checked.value))}catch{}}
</script>

<template>
<div class="a-root">
  <div class="a-intro">
    <p class="a-overline">ROADMAP CYBERSÉCURITÉ</p>
    <p class="a-lead">De zéro aux premiers labs. Chaque level correspond à des compétences pratiques et des exercices à terminer. Pas de parcours uniquement basés sur des QCM.</p>
    <div class="a-progress-head"><span>Progression</span><strong>{{doneCount}} / 5 levels</strong></div>
    <div class="a-progress" role="progressbar" :aria-valuenow="doneCount" aria-valuemin="0" aria-valuemax="5" aria-label="Niveaux terminés"><span :style="{width:doneCount*20+'%'}"></span></div>
    <small>Les cases cochées sont mémorisées sur cet appareil.</small>
  </div>
  <div class="a-links"><a href="#academy-levels">Les levels</a><a href="#academy-open-source">Labs open source</a><a href="#academy-online">Labs en ligne</a></div>

  <h2 id="academy-levels">Roadmap - Level 0 à Level 4</h2>
  <p class="a-description">Commence au Level 0. Ouvre un niveau pour voir les exercices, puis coche ce que tu as réellement terminé.</p>
  <div class="a-levels">
    <details v-for="(level,index) in academyLevels" :key="level.id" :id="'academy-level-'+level.id" class="a-level" :open="index===0">
      <summary>
        <span class="a-number">{{level.id}}</span>
        <span class="a-level-label"><strong>Level {{level.id}} <span>- {{level.title}}</span></strong><small>{{level.desc}}</small></span>
        <span class="a-level-completion">{{completed(level)?'Terminé':level.tasks.filter(t=>checked.includes(t.id)).length+'/'+level.required}}</span>
        <span class="a-caret" aria-hidden="true">⌄</span>
      </summary>
      <div class="a-content">
        <p class="a-subhead">{{level.id===4?'Choisis au moins un projet à terminer':'Exercices pratiques'}}</p>
        <div class="a-exercises">
          <div v-for="task in level.tasks" :key="task.id" class="a-exercise">
            <label class="a-check"><input type="checkbox" :checked="checked.includes(task.id)" :aria-label="'Exercice terminé : '+task.name" @change="toggle(task.id)"></label>
            <div class="a-exercise-body">
              <div class="a-mini"><span>{{task.provider}}</span><span>{{task.access}}</span></div>
              <a :href="task.url" target="_blank" rel="noopener noreferrer">{{task.name}} <span aria-hidden="true">↗</span></a>
              <p><b>À faire :</b> {{task.work}}</p>
              <p v-if="task.note" class="a-note">{{task.note}}</p>
            </div>
          </div>
        </div>
        <p class="a-validation"><b>Tu peux passer à la suite si :</b> {{level.validate}}</p>
      </div>
    </details>
  </div>

  <section id="academy-open-source" class="a-section">
    <h2>Labs open source</h2>
    <p class="a-description">De vraies applications et machines vulnérables à installer pour pratiquer. GOAD est classé en trois étapes : MINILAB, GOAD-Light, puis GOAD complet. Les environnements doivent rester isolés de ton réseau de production et d'Internet.</p>
    <div class="a-controls">
      <label><span>Domaine</span><select v-model="activeCategory"><option value="all">Tous les domaines</option><option value="web">Web / API</option><option value="infra">Machines / services</option><option value="ad">Active Directory</option><option value="cloud">Cloud / conteneurs</option></select></label>
      <label><span>Rechercher</span><input v-model="search" type="search" placeholder="GOAD, Docker, API..."></label>
    </div>
    <p class="a-counter">{{labFilter.length}} labs trouvés</p>
    <div class="a-grid">
      <article v-for="lab in shownLabs" :key="lab.title" class="a-lab">
        <div class="a-meta"><span>{{lab.difficulty}} · {{lab.where}}</span><span>{{lab.cost}}</span></div>
        <h3>{{lab.title}}</h3>
        <p>{{lab.desc}}</p>
        <p class="a-task"><b>Pratique :</b> {{lab.task}}</p>
        <p class="a-prereq"><b>Prérequis :</b> {{lab.prereq}}</p>
        <p v-if="lab.note" class="a-note">{{lab.note}}</p>
        <a :href="lab.url" target="_blank" rel="noopener noreferrer">Voir le projet <span aria-hidden="true">↗</span></a>
      </article>
    </div>
    <button v-if="labFilter.length>6" type="button" class="a-more" @click="showAll=!showAll">{{showAll?'Afficher moins':'Voir les '+labFilter.length+' labs'}}</button>
  </section>

  <section id="academy-online" class="a-section">
    <h2>Labs en ligne</h2>
    <p class="a-description">Pour pratiquer sans installer de machines virtuelles. Les offres freemium ne donnent pas accès à tous les labs.</p>
    <div class="a-online">
      <a v-for="lab in academyOnlineLabs" :key="lab.title" :href="lab.url" target="_blank" rel="noopener noreferrer"><strong>{{lab.title}} <span aria-hidden="true">↗</span></strong><small>{{lab.info}}</small></a>
    </div>
  </section>
  <p class="a-foot">Les niveaux sont un guide d'apprentissage, pas des certifications. Les projets restent la propriété de leurs auteurs. Certains environnements sont gratuits à télécharger mais nécessitent du matériel ; les ressources AWS de CloudGoat peuvent engendrer des frais. Les liens et descriptions sont issus des sites officiels, sans test individuel de chaque déploiement.</p>
</div>
</template>

<style scoped>
.a-root{color:#eae4f4;max-width:970px}
.a-intro{background:#120e19;border:1px solid #3a2c49;border-radius:13px;padding:22px;margin:20px 0 16px}
.a-overline{color:#b7a0de!important;font-size:.72rem;letter-spacing:.14em;font-weight:750;margin:0 0 10px!important}
.a-lead{font-size:1.03rem;line-height:1.7;color:#ded5ea!important;margin:0 0 18px!important}
.a-progress-head{display:flex;justify-content:space-between;font-size:.8rem;color:#b7abc8;gap:10px}
.a-progress-head strong{color:#e2d3fd}
.a-progress{height:6px;background:#332640;overflow:hidden;border-radius:6px;margin:8px 0}
.a-progress span{display:block;background:#a586de;height:100%}
.a-intro small,.a-foot{font-size:.78rem;color:#a29aaf}
.a-links{display:flex;gap:9px;flex-wrap:wrap;margin-bottom:26px}
.a-links a{display:inline-flex;padding:7px 12px;border:1px solid #3c2e4e;border-radius:100px;background:#17111f;color:#d5c3f2!important;font-size:.82rem;text-decoration:none!important}
.a-links a:hover{border-color:#8b70b1}
.a-description{color:#b0a6bd!important;font-size:.92rem;line-height:1.65;margin:0 0 18px!important}
.a-levels{display:grid;gap:10px}
.a-level{border:1px solid #372947;background:#110d19;border-radius:11px;overflow:hidden;scroll-margin-top:85px}
.a-level[open]{border-color:#674b89}
.a-level summary{display:flex;align-items:center;gap:13px;cursor:pointer;list-style:none;padding:15px 16px}
.a-level summary::-webkit-details-marker{display:none}
.a-number{width:38px;height:38px;flex:0 0 38px;display:flex;align-items:center;justify-content:center;background:#2c1e41;color:#dec9ff;border:1px solid #60437e;border-radius:9px;font-weight:800;font-size:1.1rem}
.a-level-label{min-width:0;flex:1}
.a-level-label strong{display:block;color:#f0e8fd;font-size:1rem}
.a-level-label strong span{color:#d5c6e5}
.a-level-label small{display:block;color:#a79bb6;line-height:1.4;margin-top:4px}
.a-level-completion{color:#bda6d8;flex:0 0 auto;font-size:.76rem}
.a-caret{color:#a68dbb;font-size:1.1rem}
.a-level[open] .a-caret{transform:rotate(180deg)}
.a-content{padding:0 16px 17px 67px}
.a-subhead{font-size:.76rem!important;color:#ad98c9!important;text-transform:uppercase;letter-spacing:.08em;font-weight:700}
.a-exercises{display:grid;gap:9px}
.a-exercise{display:flex;gap:12px;border:1px solid #32243f;background:#171120;border-radius:9px;padding:13px}
.a-check input{width:17px;height:17px;accent-color:#ac8add;cursor:pointer;margin-top:4px}
.a-exercise-body{min-width:0;flex:1}
.a-mini{display:flex;gap:10px;justify-content:space-between;flex-wrap:wrap;color:#a99dba;font-size:.73rem;margin-bottom:4px}
.a-exercise-body>a{font-weight:720;font-size:.94rem;color:#dbc6fc;text-decoration:none!important}
.a-exercise-body>a:hover{text-decoration:underline!important}
.a-exercise-body p{font-size:.84rem;color:#c0b6cd!important;margin:5px 0 0!important;line-height:1.5}
.a-note{font-size:.78rem!important;color:#a69ab7!important}
.a-validation{font-size:.85rem!important;color:#d1c3de!important;margin:16px 0 0!important}
.a-section{margin-top:39px;scroll-margin-top:80px}
.a-controls{display:grid;grid-template-columns:1fr 1.5fr;gap:10px;margin-bottom:14px}
.a-controls label{display:grid;gap:5px;color:#b5a8c6;font-size:.8rem}
.a-controls select,.a-controls input{width:100%;box-sizing:border-box;border:1px solid #544064;background:#171020;color:#f0eafb;border-radius:8px;padding:10px;font-size:.88rem}
.a-controls :is(input,select):focus{outline:2px solid #a083d9;outline-offset:1px}
.a-counter{color:#a79fb3!important;font-size:.8rem!important;margin:0 0 10px!important}
.a-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.a-lab{border:1px solid #332641;background:#120e1a;padding:17px;border-radius:10px;display:flex;flex-direction:column}
.a-meta{display:flex;flex-wrap:wrap;justify-content:space-between;gap:6px;color:#b49bcc;font-size:.73rem}
.a-lab h3{font-size:1.05rem!important;margin:10px 0 4px!important;color:#efe5fd!important;border:0!important}
.a-lab p{color:#bbb0c6!important;font-size:.84rem;line-height:1.5;margin:5px 0!important}
.a-lab .a-task{color:#d1c5de!important}
.a-lab>a{margin-top:auto;padding-top:10px;color:#d9c2fa;text-decoration:none!important;font-size:.83rem;font-weight:680}
.a-lab>a:hover{text-decoration:underline!important}
.a-more{display:block;margin:19px auto 0;border:1px solid #654886;border-radius:8px;padding:10px 20px;background:#23172f;color:#eadbfa;cursor:pointer}
.a-more:hover{background:#312143}
.a-online{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.a-online a{display:grid;gap:4px;border:1px solid #382845;border-radius:9px;background:#140f1d;padding:13px;text-decoration:none!important}
.a-online strong{color:#dac7f5}
.a-online small{color:#afa4be;line-height:1.4}
.a-foot{margin-top:30px!important;line-height:1.6}
@media(max-width:680px){
.a-intro{padding:17px}.a-level summary{padding:12px 10px;gap:9px}
.a-level-label strong{font-size:.9rem}.a-level-label small{font-size:.74rem}
.a-number{width:30px;height:30px;flex-basis:30px;font-size:.9rem}
.a-level-completion{font-size:.7rem}.a-content{padding:0 10px 13px}
.a-grid,.a-online,.a-controls{grid-template-columns:1fr}
}
</style>

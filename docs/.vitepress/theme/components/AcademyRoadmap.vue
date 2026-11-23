<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { academyStages, academyTracks, academyResources } from '../data/academy'

const completed = ref<string[]>([])
const search = ref('')
const area = ref('all')
const access = ref('all')
const limit = ref(24)
const statusLabels: Record<string, string> = {
  gratuit: 'Gratuit',
  'gratuit-partiel': 'Gratuit en partie',
  'gratuit-limite': 'Gratuit limité',
  freemium: 'Freemium',
  'a-verifier': 'Accès à confirmer'
}

const progress = computed(() => academyStages.filter(s => completed.value.includes(s.id)).length)
const percent = computed(() => Math.round(progress.value * 100 / academyStages.length))
const normalized = (value: string) => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
const found = computed(() => {
  const q = normalized(search.value.trim())
  return academyResources.filter(r => {
    const matchesArea = area.value === 'all' || r.stage === area.value || r.track === area.value
    const matchesAccess = access.value === 'all' || (access.value === 'confirme' ? r.access !== 'a-verifier' : r.access === access.value)
    const matchesQuery = !q || normalized([r.title, r.detail, r.kind, r.level, r.stage || '', r.track || ''].join(' ')).includes(q)
    return matchesArea && matchesAccess && matchesQuery
  }).sort((a, b) => Number(b.featured) - Number(a.featured) || a.title.localeCompare(b.title, 'fr'))
})
const visible = computed(() => found.value.slice(0, limit.value))
const recommended = (id: string, key: 'stage' | 'track') => academyResources.filter(r => r.featured && r[key] === id).slice(0, 4)
const verifiedCount = academyResources.filter(r => r.access !== 'a-verifier').length
watch([search, area, access], () => { limit.value = 24 })

onMounted(() => {
  try {
    const value = JSON.parse(localStorage.getItem('skill-issue-academy-progress-v1') || '[]')
    completed.value = Array.isArray(value) ? value.filter((id: unknown) => typeof id === 'string' && academyStages.some(s => s.id === id)) : []
  } catch { completed.value = [] }
})
function toggle(id: string) {
  completed.value = completed.value.includes(id) ? completed.value.filter(x => x !== id) : [...completed.value, id]
  try { localStorage.setItem('skill-issue-academy-progress-v1', JSON.stringify(completed.value)) } catch {}
}
function jumpToCatalog(id: string) {
  area.value = id
  access.value = 'all'
  search.value = ''
  const element = document.getElementById('catalogue')
  if (element) element.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<template>
  <div class="academy-roadmap">
    <div class="academy-overview" aria-label="Présentation de la roadmap">
      <div>
        <p class="academy-kicker">APPRENDRE - PRATIQUER - PROGRESSER</p>
        <p class="academy-lead">Commence par les fondamentaux, avance à ton rythme, puis choisis une spécialisation. Les ressources sont accessibles depuis leur site officiel.</p>
      </div>
      <div class="academy-progress">
        <div class="academy-progress-top"><span>Ton parcours</span><strong>{{ progress }} / {{ academyStages.length }} étapes</strong></div>
        <div class="academy-progress-rail" role="progressbar" :aria-valuenow="progress" :aria-valuemin="0" :aria-valuemax="academyStages.length" :aria-label="'Progression : ' + percent + ' %'"><span :style="{width: percent + '%'}"></span></div>
        <small>Enregistré uniquement sur cet appareil.</small>
      </div>
    </div>

    <nav class="academy-quicknav" aria-label="Navigation Academy">
      <a href="#parcours">Roadmap débutant</a>
      <a href="#specialisations">Spécialisations</a>
      <a href="#catalogue">Toutes les ressources</a>
    </nav>

    <h2 id="parcours">Roadmap débutant</h2>
    <p class="academy-muted">Suis les étapes dans l'ordre. Une étape est terminée lorsque tu sais réaliser l'objectif indiqué, pas simplement après avoir ouvert les liens.</p>
    <ol class="academy-stage-list">
      <li v-for="(step, index) in academyStages" :key="step.id" class="academy-stage" :class="{ 'is-complete': completed.includes(step.id) }">
        <div class="academy-stage-no" aria-hidden="true">{{ String(index + 1).padStart(2, '0') }}</div>
        <div class="academy-stage-body">
          <div class="academy-stage-heading"><h3>{{ step.title }}</h3><span class="academy-stage-label">{{ completed.includes(step.id) ? 'Terminée' : 'À apprendre' }}</span></div>
          <p>{{ step.summary }}</p>
          <p class="academy-goal"><strong>Objectif :</strong> {{ step.goal }}</p>
          <div class="academy-resource-links">
            <a v-for="resource in recommended(step.id, 'stage')" :key="resource.id" :href="resource.url" target="_blank" rel="noopener noreferrer" :title="resource.note || resource.detail">
              <span>{{ resource.title }}</span><span class="academy-out" aria-hidden="true">↗</span>
            </a>
          </div>
          <div class="academy-stage-actions">
            <button type="button" class="academy-done" :aria-pressed="completed.includes(step.id)" @click="toggle(step.id)">{{ completed.includes(step.id) ? '✓ Étape terminée' : 'Marquer comme terminée' }}</button>
            <button type="button" class="academy-more" @click="jumpToCatalog(step.id)">Voir toutes les ressources</button>
          </div>
        </div>
      </li>
    </ol>

    <h2 id="specialisations">Choisir une spécialisation</h2>
    <p class="academy-muted">Après les bases, sélectionne un domaine. Ces branches sont indépendantes : tu n'as pas besoin de toutes les terminer.</p>
    <div class="academy-tracks">
      <article v-for="track in academyTracks" :key="track.id" class="academy-track">
        <h3>{{ track.title }}</h3>
        <p>{{ track.summary }}</p>
        <div class="academy-track-links">
          <a v-for="resource in recommended(track.id, 'track').slice(0, 2)" :key="resource.id" :href="resource.url" target="_blank" rel="noopener noreferrer">{{ resource.title }} <span aria-hidden="true">↗</span></a>
        </div>
        <button type="button" @click="jumpToCatalog(track.id)">Explorer cette spécialité <span aria-hidden="true">→</span></button>
      </article>
    </div>

    <section class="academy-catalog" aria-labelledby="catalogue">
      <h2 id="catalogue">Toutes les ressources</h2>
      <p class="academy-muted">{{ academyResources.length }} liens classés, dont {{ verifiedCount }} ressources documentées par leurs fournisseurs. Les anciens liens communautaires conservent la mention « Accès à confirmer » tant que leur gratuité n'a pas été revérifiée.</p>
      <div class="academy-filters">
        <label class="academy-search">
          <span>Recherche</span>
          <input v-model="search" type="search" placeholder="Linux, Python, SOC, Nmap..." autocomplete="off">
        </label>
        <label>
          <span>Domaine</span>
          <select v-model="area">
            <option value="all">Tous les domaines</option>
            <optgroup label="Fondamentaux">
              <option v-for="step in academyStages" :key="step.id" :value="step.id">{{ step.title }}</option>
            </optgroup>
            <optgroup label="Spécialisations">
              <option v-for="track in academyTracks" :key="track.id" :value="track.id">{{ track.title }}</option>
            </optgroup>
          </select>
        </label>
        <label>
          <span>Accès</span>
          <select v-model="access">
            <option value="all">Tous les accès</option>
            <option value="confirme">Conditions documentées</option>
            <option value="gratuit">Gratuit</option>
            <option value="freemium">Freemium</option>
            <option value="gratuit-partiel">Partiellement gratuit</option>
            <option value="gratuit-limite">Gratuit limité</option>
            <option value="a-verifier">Accès à confirmer</option>
          </select>
        </label>
      </div>
      <p class="academy-count" aria-live="polite">{{ found.length }} résultat{{ found.length > 1 ? 's' : '' }}</p>
      <div class="academy-results">
        <article v-for="resource in visible" :key="resource.id" class="academy-result">
          <div class="academy-result-top">
            <span class="academy-status" :class="{ unverified: resource.access === 'a-verifier' }">{{ statusLabels[resource.access] }}</span>
            <span>{{ resource.level }} · {{ resource.kind }}</span>
          </div>
          <h3><a :href="resource.url" target="_blank" rel="noopener noreferrer">{{ resource.title }} <span aria-hidden="true">↗</span></a></h3>
          <p>{{ resource.detail }}</p>
          <p v-if="resource.note" class="academy-result-note">{{ resource.note }}</p>

        </article>
      </div>
      <p v-if="!found.length" class="academy-empty">Aucune ressource trouvée. Essaie un autre domaine ou efface les filtres.</p>
      <button v-if="found.length > visible.length" type="button" class="academy-show-more" @click="limit += 24">Afficher 24 ressources supplémentaires ({{ found.length - visible.length }} restantes)</button>
      <p class="academy-note">Les ressources freemium disposent d'une partie gratuite, mais pas d'un accès intégral. La date indiquée correspond à la consultation documentaire, pas à un test de connexion individuel. Les liens « Accès à confirmer » ne sont pas garantis gratuits aujourd'hui. Les exercices doivent être réalisés uniquement sur les plateformes et laboratoires autorisés.</p>
    </section>
  </div>
</template>

<style scoped>
.academy-roadmap{max-width:1040px;color:#eeeaf7}
.academy-overview{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(230px,1fr);gap:22px;align-items:center;border:1px solid #352848;border-radius:14px;background:linear-gradient(125deg,#171121,#0d0a12);padding:24px;margin:22px 0}
.academy-kicker{letter-spacing:.16em;font-size:.69rem;font-weight:750;color:#b398ef!important;margin:0 0 12px!important}
.academy-lead{font-size:1.04rem;line-height:1.7;margin:0!important;color:#e3ddec!important}
.academy-progress{padding:17px;background:#110e19;border:1px solid #31243f;border-radius:12px}
.academy-progress-top{display:flex;justify-content:space-between;gap:8px;font-size:.82rem;color:#bdb1cb}
.academy-progress-top strong{color:#decafa}
.academy-progress-rail{height:6px;border-radius:6px;background:#332840;overflow:hidden;margin:13px 0 9px}
.academy-progress-rail span{display:block;height:100%;background:#a38ae8;transition:width .25s}
.academy-progress small,.academy-result small{font-size:.73rem;color:#9187a0}
.academy-quicknav{display:flex;flex-wrap:wrap;gap:9px;margin:0 0 27px}
.academy-quicknav a{padding:7px 13px;text-decoration:none!important;border:1px solid #3b2d4d;border-radius:30px;font-size:.84rem;color:#d8c9ed;background:#15101d}
.academy-quicknav a:hover{border-color:#9275c5}
.academy-muted{color:#aba2b8!important;margin:0 0 21px!important;line-height:1.65}
.academy-stage-list{list-style:none!important;margin:0 0 36px!important;padding:0!important;position:relative}
.academy-stage{list-style:none!important;margin:0!important;padding:0 0 15px!important;display:grid;grid-template-columns:44px minmax(0,1fr);gap:15px;position:relative}
.academy-stage:before{content:"";position:absolute;left:21px;top:44px;bottom:-4px;width:1px;background:#4a365f}
.academy-stage:last-child:before{display:none}
.academy-stage-no{display:flex;align-items:center;justify-content:center;width:44px;height:44px;border:1px solid #6d5092;border-radius:11px;color:#d1bfff;background:#1a1326;font-size:.85rem;font-weight:750}
.academy-stage.is-complete .academy-stage-no{background:#332348;border-color:#b396df}
.academy-stage-body{padding:18px;border-radius:12px;border:1px solid #342741;background:#100c18}
.academy-stage-heading{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap}
.academy-stage-heading h3,.academy-track h3,.academy-result h3{margin:0!important;padding:0!important;border:0!important;font-size:1.03rem!important;line-height:1.4;color:#efe7fc!important}
.academy-stage-label{font-size:.72rem;color:#ac92cc}
.academy-stage-body>p,.academy-track p,.academy-result p{margin:9px 0!important;line-height:1.55;color:#b9b0c6}
.academy-goal{font-size:.85rem}
.academy-resource-links{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin-top:13px}
.academy-resource-links a{display:flex;justify-content:space-between;gap:8px;padding:10px;text-decoration:none!important;background:#1c1527;border:1px solid #352746;border-radius:7px;color:#d8caed;font-size:.82rem;overflow-wrap:anywhere}
.academy-resource-links a:hover{border-color:#9e7cd4;background:#261b35}
.academy-out{flex-shrink:0;color:#a58bc7}
.academy-stage-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.academy-stage-actions button,.academy-track button,.academy-show-more{cursor:pointer;font-size:.83rem;border-radius:8px;padding:9px 13px;border:1px solid #504064;background:#231a30;color:#e4d7fc}
.academy-stage-actions button:hover,.academy-track button:hover,.academy-show-more:hover{border-color:#a887d4}
.academy-stage-actions .academy-done[aria-pressed=true]{border-color:#8e70ba;color:#efdcff;background:#312445}
.academy-stage-actions .academy-more{border-color:transparent;background:none;color:#b7a3d1}
.academy-tracks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px;margin:0 0 36px}
.academy-track{padding:18px;border-radius:12px;border:1px solid #342741;background:#120e1b;min-width:0}
.academy-track-links{display:flex;flex-direction:column;gap:7px;margin:11px 0}
.academy-track-links a{color:#c6afeb;font-size:.79rem;text-decoration:none!important}
.academy-track-links a:hover{text-decoration:underline!important}
.academy-track button{padding:8px 0;border:0;background:transparent;color:#cfb7f4}
.academy-filters{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:10px;margin-top:20px}
.academy-filters label{display:flex;flex-direction:column;gap:6px;font-size:.79rem;color:#c1b4d3}
.academy-filters input,.academy-filters select{box-sizing:border-box;width:100%;min-width:0;background:#16101e;border:1px solid #4a365e;border-radius:8px;padding:11px 12px;color:#eee6fc;font:inherit;font-size:.86rem}
.academy-filters input:focus,.academy-filters select:focus{outline:2px solid #9071c7;outline-offset:1px}
.academy-count{font-size:.8rem;color:#b7acc3!important;margin:17px 0 11px!important}
.academy-results{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.academy-result{border:1px solid #322640;border-radius:11px;background:#110d19;padding:15px;min-width:0}
.academy-result-top{display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap;color:#9d91af;font-size:.71rem;margin-bottom:10px}
.academy-status{padding:3px 8px;border:1px solid #5f447e;border-radius:6px;color:#d5b9f8;background:#261a38}
.academy-status.unverified{color:#bbb2c6;border-color:#494150;background:#211d27}
.academy-result h3 a{color:#ece3fc;text-decoration:none!important}
.academy-result h3 a:hover{color:#bda2ee}
.academy-result-note{font-size:.78rem;color:#aaa0b5!important}
.academy-empty{padding:18px;border:1px dashed #44334f;border-radius:9px}
.academy-show-more{display:block;margin:20px auto}
.academy-note{font-size:.78rem;line-height:1.65;color:#9c91aa!important;margin-top:18px!important}
@media(max-width:700px){
  .academy-overview{grid-template-columns:1fr;padding:17px;gap:15px}
  .academy-stage{grid-template-columns:34px minmax(0,1fr);gap:10px}
  .academy-stage-no{width:34px;height:34px;font-size:.74rem}
  .academy-stage:before{left:16px;top:36px}
  .academy-stage-body{padding:13px}
  .academy-resource-links,.academy-tracks,.academy-results{grid-template-columns:1fr}
  .academy-filters{grid-template-columns:1fr}
  .academy-stage-heading h3{font-size:.96rem!important}
}
@media(prefers-reduced-motion:reduce){.academy-progress-rail span{transition:none}}
</style>

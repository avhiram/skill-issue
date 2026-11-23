<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { categories, resources } from '../data/academy-organized'

const groups = ['Bases', 'Offensif', 'Défensif', 'Spécialités', 'Pratique']
const current = ref('fondamentaux')
const search = ref('')
const level = ref('all')
const limit = ref(15)
const category = computed(() => categories.find(c => c.id === current.value) || categories[0])
const isSearching = computed(() => search.value.trim().length > 0)
const simplify = (v: string) => v.toLocaleLowerCase('fr').normalize('NFD').replace(/[\u0300-\u036f]/g, '')

const matches = computed(() => {
  const needle = simplify(search.value.trim())
  return resources.filter(r => {
    if (!needle && r.category !== current.value) return false
    if (level.value !== 'all' && String(r.level) !== level.value) return false
    if (!needle) return true
    return simplify([r.title, r.provider, r.category, r.type, r.description].join(' ')).includes(needle)
  }).sort((a, b) => a.level - b.level
    || Number(b.featured) - Number(a.featured)
    || Number(b.handsOn) - Number(a.handsOn)
    || a.title.localeCompare(b.title, 'fr'))
})
const visible = computed(() => matches.value.slice(0, limit.value))
const levelGroups = computed(() => [0, 1, 2, 3, 4]
  .map(n => ({ n, items: visible.value.filter(r => r.level === n) }))
  .filter(g => g.items.length))
const categoryCount = (id: string) => resources.filter(r => r.category === id).length

watch([current, search, level], () => { limit.value = 15 })
onMounted(() => {
  const hash = decodeURIComponent(window.location.hash.slice(1))
  if (categories.some(c => c.id === hash)) current.value = hash
})
function openCategory(id: string) {
  current.value = id
  search.value = ''
  level.value = 'all'
  if (typeof window !== 'undefined') {
    window.history.replaceState(null, '', '#' + id)
    nextTick(() => document.getElementById('academy-content')?.scrollIntoView({
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      block: 'start'
    }))
  }
}
function clearSearch() {
  search.value = ''
  level.value = 'all'
}
</script>

<template>
  <div class="academy-categories">
    <label class="ac-search">
      <span class="ac-search-label">Rechercher une ressource</span>
      <span class="ac-search-wrap">
        <svg aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="10.8" cy="10.8" r="6.5"/><path d="m16 16 5 5"/></svg>
        <input v-model="search" type="search" placeholder="Nmap, Wireshark, GOAD, forensic..." autocomplete="off" aria-label="Rechercher dans toutes les catégories">
      </span>
    </label>

    <div class="ac-start">
      <span>Ordre conseillé pour débuter</span>
      <div class="ac-start-links">
        <button type="button" @click="openCategory('fondamentaux')">Fondamentaux</button>
        <span>→</span>
        <button type="button" @click="openCategory('reseau')">Réseau</button>
        <span>→</span>
        <button type="button" @click="openCategory('systemes')">Linux / Windows</button>
        <span>→</span>
        <button type="button" @click="openCategory('ctf')">Premiers labs</button>
        <span>→</span>
        <span>Spécialisation</span>
      </div>
    </div>

    <section id="categories" class="ac-sections" aria-label="Catégories de cybersécurité">
      <div v-for="group in groups" :key="group" class="ac-section">
        <h2>{{ group }}</h2>
        <div class="ac-category-grid">
          <button v-for="cat in categories.filter(c => c.group === group)" :key="cat.id"
            type="button" class="ac-category"
            :class="{ 'is-selected': !isSearching && cat.id === current }"
            :aria-pressed="!isSearching && cat.id === current"
            @click="openCategory(cat.id)">
            <span class="ac-category-top">
              <strong>{{ cat.name }}</strong>
              <span class="ac-category-count">{{ categoryCount(cat.id) }}</span>
            </span>
            <span class="ac-category-summary">{{ cat.summary }}</span>
          </button>
        </div>
      </div>
    </section>

    <section id="academy-content" class="ac-results" aria-live="polite">
      <div class="ac-results-head">
        <div class="ac-results-title">
          <p class="ac-kicker">{{ isSearching ? 'RECHERCHE GLOBALE' : category.group }}</p>
          <h2>{{ isSearching ? 'Résultats de recherche' : category.name }}</h2>
          <p v-if="!isSearching" class="ac-order"><strong>À suivre :</strong> {{ category.order }}</p>
          <p v-else class="ac-order">Recherche dans toutes les catégories.</p>
        </div>
        <label class="ac-level-control">
          <span>Niveau</span>
          <select v-model="level">
            <option value="all">Tous les niveaux</option>
            <option v-for="n in 5" :key="n" :value="String(n-1)">Level {{ n-1 }}</option>
          </select>
        </label>
      </div>
      <div class="ac-results-bar">
        <span>{{ matches.length }} ressource{{ matches.length > 1 ? 's' : '' }}</span>
        <button v-if="isSearching" type="button" @click="clearSearch">Effacer la recherche</button>
      </div>

      <div v-if="levelGroups.length" class="ac-list">
        <section v-for="g in levelGroups" :key="g.n" class="ac-level-group" :aria-label="'Level '+g.n">
          <div class="ac-level-heading">
            <span>Level {{ g.n }}</span>
            <span>{{ g.n === 0 ? 'Débuter' : g.n === 1 ? 'Bases' : g.n === 2 ? 'Pratiquer' : g.n === 3 ? 'Approfondir' : 'Avancé' }}</span>
          </div>
          <div class="ac-rows">
            <a v-for="r in g.items" :key="r.id" class="ac-resource" :href="r.url" target="_blank" rel="noopener noreferrer">
              <div class="ac-resource-main">
                <span class="ac-resource-name">
                  {{ r.title }}
                  <span aria-hidden="true" class="ac-out">↗</span>
                </span>
                <span class="ac-resource-url">{{ r.url }}</span>
                <span v-if="isSearching" class="ac-resource-category">{{ categories.find(c => c.id === r.category)?.name }}</span>
              </div>
            </a>
          </div>
        </section>
      </div>
      <p v-else class="ac-empty">Aucun résultat pour cette sélection. Essaie un autre niveau ou une autre recherche.</p>
      <button v-if="matches.length > visible.length" class="ac-show-more" type="button" @click="limit += 15">
        Afficher 15 ressources supplémentaires ({{ matches.length - visible.length }} restantes)
      </button>

    </section>
  </div>
</template>

<style scoped>
.academy-categories{width:100%;color:#efeaf6}
.ac-search{display:block;margin:16px 0 16px}
.ac-search-label{display:block;color:#aa9eb8;font-size:.78rem;font-weight:650;margin-bottom:8px}
.ac-search-wrap{display:flex;align-items:center;gap:12px;border:1px solid #433450;background:#15101d;border-radius:9px;padding:0 14px;color:#a698b7}
.ac-search-wrap:focus-within{border-color:#9d82c4;outline:1px solid #795c9b}
.ac-search input{width:100%;padding:13px 0;background:transparent;border:0;outline:none;color:#f0eaf9;font:inherit;font-size:.91rem}
.ac-search input::placeholder{color:#857991}
.ac-start{margin:0 0 34px;border-bottom:1px solid #2c2239;padding-bottom:22px;color:#b4a5c3;font-size:.81rem}
.ac-start>span{display:block;margin-bottom:9px;font-weight:600}
.ac-start-links{display:flex;flex-wrap:wrap;gap:8px;align-items:center;color:#8f7fa4}
.ac-start-links button{border:0;background:none;padding:0;cursor:pointer;font:inherit;color:#d5c3ed}
.ac-start-links button:hover{text-decoration:underline}
.ac-sections{display:grid;gap:24px}
.ac-section h2{font-size:.91rem!important;color:#b39dc9!important;letter-spacing:.025em;margin:0 0 10px!important;padding:0!important;border:none!important;font-weight:670}
.ac-category-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.ac-category{width:100%;min-height:88px;box-sizing:border-box;text-align:left;display:flex;flex-direction:column;align-items:stretch;gap:7px;border-radius:9px;border:1px solid #34283f;background:#110d18;padding:14px 16px;cursor:pointer;transition:border-color .15s,background .15s}
.ac-category:hover{border-color:#71548a;background:#191225}
.ac-category.is-selected{border-color:#9576be;background:#1b1428}
.ac-category-top{display:flex;align-items:center;justify-content:space-between;gap:10px}
.ac-category-top strong{color:#f1e9fa;font-size:.93rem;line-height:1.3;font-weight:680}
.ac-category-count{font-size:.73rem;color:#ac97c4;background:#251b32;border-radius:6px;padding:3px 7px;flex:0 0 auto}
.ac-category-summary{font-size:.78rem;line-height:1.4;color:#a9a0b4}
.ac-results{margin:34px 0 0;scroll-margin-top:88px;border-top:1px solid #3b2e49;padding-top:24px}
.ac-results-head{display:flex;justify-content:space-between;align-items:end;gap:15px;flex-wrap:wrap}
.ac-kicker{font-size:.71rem!important;color:#aa92c5!important;letter-spacing:.1em;margin:0 0 4px!important;font-weight:650}
.ac-results-title h2{margin:0!important;padding:0!important;border:0!important;font-size:1.45rem!important;color:#f1e8fa!important}
.ac-order{margin:7px 0 0!important;color:#b8aac4!important;font-size:.83rem!important}
.ac-order strong{font-weight:650;color:#d5c1e8!important}
.ac-level-control{display:flex;align-items:center;gap:8px;font-size:.79rem;color:#ac9bbb}
.ac-level-control select{padding:8px 10px;border:1px solid #433450;border-radius:7px;background:#171020;color:#e8def3;font:inherit;max-width:184px}
.ac-results-bar{display:flex;justify-content:space-between;align-items:center;margin:17px 0 6px;min-height:22px;gap:10px;color:#a598b2;font-size:.77rem}
.ac-results-bar button{border:0;background:transparent;color:#d3bce9;cursor:pointer;font:inherit}
.ac-level-group{margin:0 0 17px}
.ac-level-heading{display:flex;align-items:center;justify-content:space-between;gap:8px;border-bottom:1px solid #44314f;padding:8px 0;color:#d7bdf3;font-size:.78rem;font-weight:700}
.ac-level-heading span:last-child{color:#9386a5;font-weight:500}
.ac-rows{display:grid}
.ac-resource{display:flex;align-items:center;justify-content:space-between;gap:15px;padding:12px 5px;border-bottom:1px solid #282030;text-decoration:none!important}
.ac-resource:hover .ac-resource-name{text-decoration:underline}
.ac-resource:hover{background:#14101b}
.ac-resource-main{display:flex;flex-direction:column;gap:3px;min-width:0;flex:1}
.ac-resource-name{font-size:.9rem;font-weight:620;line-height:1.4;color:#eee3fa}
.ac-out{font-size:.75rem;color:#a489bf}
.ac-resource-url{font-size:.77rem;color:#a79aac;overflow-wrap:anywhere;line-height:1.35}
.ac-resource-category{font-size:.72rem;color:#8d80a0}





.ac-empty{font-size:.88rem;color:#ab9db9;padding:18px 0}
.ac-show-more{display:block;margin:15px auto 0;padding:9px 15px;border-radius:7px;border:1px solid #58416c;background:#251b31;color:#decaf2;cursor:pointer;font-size:.81rem}
.ac-show-more:hover{border-color:#9170ba}



@media(min-width:980px){.ac-category-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:590px){.ac-category-grid{grid-template-columns:1fr}.ac-category{min-height:72px;padding:12px 14px}.ac-results-head{align-items:flex-start}.ac-resource{gap:8px;align-items:flex-start}.ac-start-links{gap:6px}.ac-category-summary{font-size:.78rem}}
@media(prefers-reduced-motion:reduce){.ac-category{transition:none}}
</style>

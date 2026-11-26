<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, shallowRef, watch } from 'vue'
import { useData, useRoute } from 'vitepress'
import { revealFoldTarget } from '../sectionFolds'

const props = defineProps<{ mode: 'desktop' | 'mobile' }>()
const route = useRoute()
const { frontmatter, theme } = useData()

type Entry = {
  id: string
  label: string
  level: number
  depth: number
  parents: string[]
  children: number
}
const entries = shallowRef<Entry[]>([])
const elements = new Map<string, HTMLElement>()
const expanded = ref<Set<string>>(new Set())
const active = ref('')
const query = ref('')
const mobileOpen = ref(false)
const list = ref<HTMLElement | null>(null)
const search = ref<HTMLInputElement | null>(null)
let frame = 0
let refreshFrame = 0
let observer: MutationObserver | undefined

const enabled = computed(() => frontmatter.value.outline !== false && (frontmatter.value.aside !== false || props.mode === 'mobile') && !(props.mode==='mobile'&&/\/(academy|osint|bug-bounty|oscp|crto|crtp)(?:\/|$)/.test(route.path)))
const normalize = (s: string) => s.toLocaleLowerCase('fr').normalize('NFD').replace(/\p{Diacritic}/gu, '').trim()
const terms = computed(() => normalize(query.value).split(/\s+/).filter(Boolean))
const filtering = computed(() => terms.value.length > 0)
const groups = computed(() => entries.value.filter(x => x.children > 0).map(x => x.id))
const byId = computed(() => new Map(entries.value.map(x => [x.id, x])))
const matchingIds = computed(() => new Set(entries.value.filter(x => {
  const label = normalize(x.label)
  return terms.value.every(t => label.includes(t))
}).map(x => x.id)))
const visibleRows = computed(() => {
  if (filtering.value) {
    const visible = new Set<string>()
    for (const id of matchingIds.value) {
      visible.add(id)
      for (const p of byId.value.get(id)?.parents || []) visible.add(p)
    }
    return entries.value.filter(x => visible.has(x.id))
  }
  return entries.value.filter(x => x.parents.every(p => expanded.value.has(p)))
})
const allExpanded = computed(() => groups.value.length > 0 && groups.value.every(id => expanded.value.has(id)))
const matchCount = computed(() => filtering.value ? matchingIds.value.size : entries.value.length)
const panelId = computed(() => 'skill-outline-panel-' + props.mode)
const searchId = computed(() => 'skill-outline-search-' + props.mode)

function toggle(id: string) {
  const next = new Set(expanded.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  expanded.value = next
}
function toggleAll() {
  expanded.value = new Set(allExpanded.value ? [] : groups.value)
}
function clearSearch() {
  query.value = ''
  search.value?.focus()
}

function levels(): [number, number] {
  let option = frontmatter.value.outline ?? theme.value.outline ?? [2, 4]
  if (typeof option === 'object' && !Array.isArray(option) && option !== null) option = option.level
  if (option === 'deep') return [2, 6]
  if (typeof option === 'number') return [option, option]
  if (Array.isArray(option) && option.length === 2) return [Number(option[0]), Number(option[1])]
  return [2, 4]
}

function collect() {
  if (!enabled.value) {
    entries.value = []
    elements.clear()
    return
  }
  const doc = document.querySelector<HTMLElement>('.VPDoc .vp-doc')
  if (!doc) {
    entries.value = []
    return
  }
  const [min, max] = levels()
  const academy = /\/academy\//.test(route.path)
  const result: Entry[] = []
  const stack: Entry[] = []
  elements.clear()
  for (const heading of Array.from(doc.querySelectorAll<HTMLElement>(academy ? '.academy-chapter[id],.academy-level[id]' : 'h2[id],h3[id],h4[id],h5[id],h6[id]'))) {
    const level = academy ? (heading.classList.contains('academy-chapter') ? 2 : 3) : Number(heading.tagName.slice(1))
    if (level < min || level > max || heading.closest('.ignore-header, [data-outline-ignore]')) continue
    const labelElement = academy ? heading.querySelector(':scope > h2, :scope > h3, :scope > summary > h2, :scope > summary > h3, :scope > summary > .academy-chapter-label > h2') : heading
    if (!labelElement) continue
    const clone = labelElement.cloneNode(true) as HTMLElement
    clone.querySelectorAll('.header-anchor, .ignore-header, .VPBadge, .skill-fold-toggle').forEach(node => node.remove())
    const label = (clone.textContent || '').replace(/\u200b/g, '').replace(/\s+/g, ' ').trim()
    if (!label || elements.has(heading.id)) continue
    while (stack.length && stack[stack.length - 1].level >= level) stack.pop()
    const entry: Entry = { id: heading.id, label, level, depth: stack.length, parents: stack.map(p => p.id), children: 0 }
    if (stack.length) stack[stack.length - 1].children++
    result.push(entry)
    stack.push(entry)
    elements.set(entry.id, heading)
  }
  entries.value = result
  expanded.value = new Set([...expanded.value].filter(id => result.some(x => x.id === id && x.children)))
  updateActive()
}

function updateActive() {
  if (!entries.value.length) { active.value = ''; return }
  const marker = 112
  let current = ''
  let closest = -Infinity
  let firstVisible = ''
  for (const entry of entries.value) {
    const heading = elements.get(entry.id)
    if (!heading || !heading.getClientRects().length) continue
    if (!firstVisible) firstVisible = entry.id
    const top = heading.getBoundingClientRect().top
    if (top <= marker && top >= closest) { current = entry.id; closest = top }
  }
  active.value = current || firstVisible
}
function onScroll() {
  if (frame) return
  frame = requestAnimationFrame(() => { frame = 0; updateActive() })
}
function scheduleCollect() {
  if (refreshFrame) cancelAnimationFrame(refreshFrame)
  refreshFrame = requestAnimationFrame(() => { refreshFrame = 0; collect() })
}
function observe() {
  observer?.disconnect()
  const doc = document.querySelector<HTMLElement>('.VPDoc .vp-doc')
  if (!doc) return
  observer = new MutationObserver(scheduleCollect)
  observer.observe(doc, { childList: true, subtree: true })
}

function openAncestors(entry: Entry) {
  if (!entry.parents.length) return
  const next = new Set(expanded.value)
  for (const parent of entry.parents) next.add(parent)
  expanded.value = next
}
function navigate(entry: Entry) {
  // Open folded Markdown sections before the existing VitePress anchor navigation.
  let parent = elements.get(entry.id)
  revealFoldTarget(parent)
  while (parent) {
    if (parent instanceof HTMLDetailsElement) parent.open = true
    if (parent.classList.contains('vp-doc')) break
    parent = parent.parentElement
  }
  openAncestors(entry)
  active.value = entry.id
  if (props.mode === 'mobile') mobileOpen.value = false
  query.value = ''
  onScroll()
}

watch(active, id => {
  const entry = byId.value.get(id)
  if (entry && !filtering.value) openAncestors(entry)
  if (props.mode !== 'desktop' || filtering.value) return
  nextTick(() => {
    const pane = list.value
    const row = pane?.querySelector<HTMLElement>('[aria-current="location"]')
    if (!pane || !row) return
    const p = pane.getBoundingClientRect(), r = row.getBoundingClientRect()
    if (r.top < p.top + 4) pane.scrollTop += r.top - p.top - 8
    else if (r.bottom > p.bottom - 4) pane.scrollTop += r.bottom - p.bottom + 8
  })
})
watch(() => route.path, async () => {
  query.value = ''
  mobileOpen.value = false
  expanded.value = new Set()
  active.value = ''
  entries.value = []
  observer?.disconnect()
  await nextTick()
  scheduleCollect()
  observe()
}, { flush: 'post' })

function closeMobile() { mobileOpen.value = false }
function openMobile() {
  if (props.mode === 'mobile' && enabled.value && entries.value.length) mobileOpen.value = true
}
function onEscape(event: KeyboardEvent) {
  if (event.key === 'Escape' && mobileOpen.value) closeMobile()
}

onMounted(async () => {
  await nextTick()
  collect()
  observe()
  window.addEventListener('skill-reading-mode', onScroll)
  if (props.mode === 'mobile') {
    window.addEventListener('skill-outline-open', openMobile)
    window.addEventListener('skill-outline-close', closeMobile)
    window.addEventListener('keydown', onEscape)
  }
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', onScroll, { passive: true })
  document.addEventListener('toggle', onScroll, true)
})
onUnmounted(() => {
  observer?.disconnect()
  cancelAnimationFrame(frame)
  cancelAnimationFrame(refreshFrame)
  window.removeEventListener('skill-reading-mode', onScroll)
  window.removeEventListener('skill-outline-open', openMobile)
  window.removeEventListener('skill-outline-close', closeMobile)
  window.removeEventListener('keydown', onEscape)
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('resize', onScroll)
  document.removeEventListener('toggle', onScroll, true)
})
</script>

<template>
  <nav v-if="enabled && entries.length" class="skill-outline" :class="'skill-outline--' + mode" aria-label="Sommaire de la page">
    <button v-if="mode === 'mobile'" class="skill-outline-mobile-toggle" type="button" :aria-expanded="mobileOpen" :aria-controls="panelId" @click="mobileOpen = !mobileOpen">
      <span><span class="skill-outline-icon" aria-hidden="true">≡</span> Sur cette page</span>
      <span class="skill-outline-mobile-meta">{{ entries.length }} rubriques <span aria-hidden="true">{{ mobileOpen ? '⌄' : '›' }}</span></span>
    </button>
    <button v-if="mode === 'mobile' && mobileOpen" class="skill-outline-backdrop" type="button" aria-label="Fermer le sommaire" @click="closeMobile" />
    <div v-show="mode === 'desktop' || mobileOpen" :id="panelId" class="skill-outline-panel" :class="{ 'is-mobile-open': mode === 'mobile' && mobileOpen }">
      <div v-if="mode === 'mobile'" class="skill-outline-mobile-header"><strong>Sommaire</strong><button type="button" aria-label="Fermer le sommaire" @click="closeMobile">×</button></div>
      <div v-if="mode === 'desktop'" class="skill-outline-header">
        <span class="skill-outline-heading">Sur cette page</span>
        <span class="skill-outline-count">{{ entries.length }}</span>
      </div>
      <div class="skill-outline-search">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></svg>
        <input :id="searchId" ref="search" v-model="query" type="search" placeholder="Filtrer les rubriques..." aria-label="Filtrer les rubriques de cette page" @keydown.esc.prevent="clearSearch">
        <button v-if="query" type="button" class="skill-outline-clear" aria-label="Effacer la recherche" @click="clearSearch">×</button>
      </div>
      <div class="skill-outline-tools">
        <span v-if="filtering" aria-live="polite">{{ matchCount }} résultat{{ matchCount !== 1 ? 's' : '' }}</span>
        <span v-else>{{ groups.length ? 'Navigation par rubrique' : matchCount + ' rubriques' }}</span>
        <button v-if="groups.length && !filtering" type="button" @click="toggleAll">{{ allExpanded ? 'Tout replier' : 'Tout déplier' }}</button>
      </div>
      <div ref="list" class="skill-outline-list">
        <div v-if="!visibleRows.length" class="skill-outline-empty">Aucune rubrique trouvée.</div>
        <div v-for="entry in visibleRows" :key="entry.id" class="skill-outline-row" :class="[{ 'is-root': entry.depth === 0, 'is-active': active === entry.id, 'is-match': filtering && matchingIds.has(entry.id) }]" :style="{ '--outline-depth': Math.min(entry.depth, 4) }">
          <div class="skill-outline-row-inner">
            <button v-if="entry.children && !filtering" class="skill-outline-caret" type="button" :aria-expanded="expanded.has(entry.id)" :aria-label="(expanded.has(entry.id) ? 'Replier ' : 'Déplier ') + entry.label" @click="toggle(entry.id)">
              <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" :class="{ 'is-open': expanded.has(entry.id) }"><path d="m6 3 5 5-5 5"/></svg>
            </button>
            <span v-else class="skill-outline-dot" aria-hidden="true"></span>
            <a :href="'#' + entry.id" :aria-current="active === entry.id ? 'location' : undefined" @click="navigate(entry)">{{ entry.label }}</a>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style>
/* Keep the native outline as a fallback until the enhanced outline is populated. */
.VPDocAside:has(.skill-outline--desktop) .VPDocAsideOutline { display: none; }
.VPDocAsideOutline .outline-link, .VPLocalNav .outline-link {
  white-space: normal; overflow-wrap: anywhere; text-overflow: clip; line-height: 1.4;
}
.skill-outline { color: #bdb3d0; font-size: 12px; min-width: 0; }
.skill-outline--desktop { margin-bottom: 12px; }
.skill-outline--mobile { display: none; }
.skill-outline-panel { min-width: 0; }
.skill-outline-header { display: flex; justify-content: space-between; align-items: center; gap: 6px; padding: 0 2px 11px; }
.skill-outline-heading { font-size: 13px; font-weight: 730; color: #eee6ff; }
.skill-outline-count { font-variant-numeric: tabular-nums; font-size: 10px; color: #b5a0d9; background: #221930; border-radius: 5px; padding: 1px 6px; }
.skill-outline-search { display: flex; align-items: center; gap: 7px; padding: 8px; color: #b19acb; background: #17111f; border: 1px solid #3d2d51; border-radius: 7px; }
.skill-outline-search:focus-within { border-color: #aa84e4; }
.skill-outline-search input { display: block; flex: 1; width: 0; min-width: 0; color: #f0e8fc; font-size: 11px; background: transparent; outline: none; }
.skill-outline-search input::placeholder { color: #a195b6; }
.skill-outline-search input::-webkit-search-cancel-button { display: none; }
.skill-outline-clear { padding: 0 3px; font-size: 17px; color: #cbb0f2; line-height: 1; }
.skill-outline-tools { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 4px; margin: 10px 2px 8px; color: #a99aba; font-size: 10px; line-height: 1.5; }
.skill-outline-tools button { color: #cfb6f9; font-weight: 620; }
.skill-outline-tools button:hover { color: #fff; }
.skill-outline-list { max-height: max(180px, calc(100dvh - 230px)); overflow-y: auto; overscroll-behavior: contain; scrollbar-width: thin; scrollbar-color: #4b385f transparent; padding-right: 4px; }
.skill-outline-row { padding-left: calc(var(--outline-depth, 0) * 9px); }
.skill-outline-row.is-root { margin: 5px 0 2px; }
.skill-outline-row-inner { display: flex; align-items: flex-start; gap: 3px; border-radius: 6px; border-left: 2px solid transparent; min-width: 0; }
.skill-outline-row.is-root > .skill-outline-row-inner { background: #181220; }
.skill-outline-row-inner:hover { background: #21172c; }
.skill-outline-row.is-active > .skill-outline-row-inner { background: #2a1d39; border-left-color: #b795ef; }
.skill-outline-row a { display: block; flex: 1; min-width: 0; padding: 7px 4px 7px 1px; color: #bdb2ce; text-decoration: none; line-height: 1.4; overflow-wrap: anywhere; white-space: normal; }
.skill-outline-row.is-root a { color: #e3d7f4; font-weight: 650; }
.skill-outline-row.is-active a, .skill-outline-row.is-match a { color: #dec6ff; font-weight: 620; }
.skill-outline-row a:hover { color: #f7edff; }
.skill-outline-caret, .skill-outline-dot { flex: 0 0 19px; height: 29px; display: grid; place-items: center; color: #b59cd6; }
.skill-outline-caret { border-radius: 5px; }
.skill-outline-caret:hover { background: rgba(183,149,239,.14); color: #f1e7ff; }
.skill-outline-caret svg { transition: transform .18s ease; }
.skill-outline-caret svg.is-open { transform: rotate(90deg); }
.skill-outline-dot::before { content: ''; width: 4px; height: 4px; border-radius: 50%; background: #6f5b8c; }
.skill-outline-empty { padding: 12px 5px; color: #b4a3c5; line-height: 1.5; }
@media (max-width: 1279px) {
  .skill-outline--mobile { display: block; margin: 0 0 18px; border: 1px solid #3a2b4b; border-radius: 9px; background: #15101e; }
  .skill-outline-mobile-toggle { display: flex; align-items: center; justify-content: space-between; gap: 8px; width: 100%; text-align: left; padding: 12px; font-size: 13px; font-weight: 650; color: #e4d7f6; }
  .skill-outline-icon { color: #c4a4f4; margin-right: 5px; }
  .skill-outline-mobile-meta { color: #ad9ac7; font-size: 11px; font-weight: 500; }
  .skill-outline--mobile .skill-outline-panel { padding: 0 12px 12px; }
  .skill-outline--mobile .skill-outline-list { max-height: 55vh; }
  .skill-outline--mobile .skill-outline-search input { font-size: 14px; }
  .skill-outline--mobile .skill-outline-row a { font-size: 13px; padding-block: 9px; }
  .skill-outline--mobile .skill-outline-caret, .skill-outline--mobile .skill-outline-dot { height: 35px; flex-basis: 25px; }
}
@media (prefers-reduced-motion: reduce) { .skill-outline-caret svg { transition: none; } }
.skill-outline-backdrop, .skill-outline-mobile-header { display: none; }
@media (max-width: 767px) {
  .skill-outline--mobile .skill-outline-backdrop {
    display: block; position: fixed; inset: 0; z-index: 36; background: rgba(8,5,13,.64);
  }
  .skill-outline--mobile .skill-outline-panel.is-mobile-open {
    position: fixed; inset: auto 0 0; z-index: 37; padding: 14px 16px calc(18px + env(safe-area-inset-bottom, 0px));
    background: #15101e; border: 1px solid #4a355e; border-radius: 16px 16px 0 0;
    box-shadow: 0 -12px 36px rgba(0,0,0,.35);
  }
  .skill-outline-mobile-header { display: flex; align-items: center; justify-content: space-between; color: #eee6ff; margin-bottom: 8px; font-size: 15px; }
  .skill-outline-mobile-header button { width: 44px; height: 44px; font-size: 24px; color: #cbb0f2; }
  .skill-outline--mobile .skill-outline-list { max-height: 56dvh; }
  .skill-outline--mobile .skill-outline-row-inner { align-items: center; }
  .skill-outline--mobile .skill-outline-row a { display:flex; align-items:center; }
  .skill-outline--mobile .skill-outline-row a:active { color:#f0e2ff; }
  .skill-outline--mobile .skill-outline-row a { min-height: 44px; padding-block: 11px; }
  .skill-outline--mobile .skill-outline-caret { height: 44px; flex-basis: 38px; }
  .skill-outline--mobile .skill-outline-search input { font-size: 16px; }
}
</style>

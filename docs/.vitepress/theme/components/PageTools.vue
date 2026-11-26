<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useData, useRoute, onContentUpdated, withBase } from 'vitepress'
import PageFind from './PageFind.vue'
import Breadcrumbs from './Breadcrumbs.vue'
import ExamChapterTree from './ExamChapterTree.vue'
import LibraryChapterTree from './LibraryChapterTree.vue'
import ExamSectionIndex from './ExamSectionIndex.vue'
import { data as siteHeadings } from '../examHeadings.data'

const route = useRoute()
const { frontmatter } = useData()
const mode = ref<'read' | 'quick'>('read')
const hasCode = ref(false)
const hasOutline = ref(false)
const wrapCode = ref(false)
const readingSize = ref<'small'|'normal'|'large'|'xl'>('normal')
const sizeKey = 'skill-issue:text-size:v1'
function changeReadingSize() {
  writeLocal(sizeKey, readingSize.value)
  if (currentDoc) currentDoc.dataset.skillTextSize = readingSize.value
}
function findInPage() { showFull(); closePanels(); window.dispatchEvent(new Event('skill-outline-close')); window.dispatchEvent(new Event('skill-page-find')) }
const ready = ref(false)
const menuOpen = ref(false)
const examOpen = ref(false)
const section= computed(()=>route.path.match(/\/(academy|osint|bug-bounty|oscp|crto|crtp)(?:\/|$)/)?.[1]||'')
const onLibrary=computed(()=>!!section.value)
const inExam=computed(()=>/\/oscp\/exam(?:-|\/|\.html|$)/.test(route.path))
const sourcePath=computed(()=>{const m=route.path.match(/\/(academy|osint|bug-bounty|oscp|crto|crtp)(?:\/.*)?$/);return (m?.[0]||'').replace(/\.html$/,'').replace(/\/index$/,'/').replace(/\/+$/,'')})
const indexAvailable=computed(()=>onLibrary.value&&section.value!=='academy'&&sourcePath.value.split('/').length>2&&!inExam.value&&!/\/(mindmap[^/]*|preparation)$/.test(sourcePath.value)&&frontmatter.value.outline!==false&&(siteHeadings[sourcePath.value]||[]).some(h=>h.level>=2))
const indexView=ref(false)
const showIndex=computed(()=>ready.value&&indexAvailable.value&&indexView.value)
const sectionTitle=computed(()=>section.value==='bug-bounty'?'Bug Bounty':section.value==='academy'?'Academy':section.value.toUpperCase())
function applyIndex(){currentDoc?.classList.toggle('skill-library-index-hidden',showIndex.value)}
function showFull(){indexView.value=false;applyIndex()}
function showRubrics(){indexView.value=true;applyIndex();window.scrollTo({top:0,behavior:'auto'})}
function jumpLibrary(id:string){showFull();pendingExamAnchor=id;history.replaceState(history.state,'',window.location.pathname+window.location.search+'#'+encodeURIComponent(id));nextTick(jumpExamAnchor)}

let pendingExamAnchor = ''
function jumpExamAnchor() {
  if (!pendingExamAnchor) {
    try {
      const raw=sessionStorage.getItem('skill-issue:exam-jump:v1')
      if(raw){
        const item=JSON.parse(raw)
        const clean=(s:string)=>s.replace(/\.html$/,'').replace(/\/+$/,'')
        if(typeof item.path==='string'&&typeof item.id==='string'&&clean(item.path)===clean(route.path)){
          pendingExamAnchor=item.id
          sessionStorage.removeItem('skill-issue:exam-jump:v1')
        }
      }
    } catch {}
  }
  if (!pendingExamAnchor) return
  showFull()
  const el = document.getElementById(pendingExamAnchor)
  if (!el) return
  pendingExamAnchor = ''
  for (let node: HTMLElement | null = el; node; node = node.parentElement) {
    if (node instanceof HTMLDetailsElement) node.open = true
  }
  requestAnimationFrame(() => el.scrollIntoView({block:'start',behavior:'auto'}))
}
function navigateExam(path:string,event:MouseEvent) {
  if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||event.button!==0)return
  const [target,hash] = path.split('#')
  closePanels()
  if(!hash)return
  try { pendingExamAnchor = decodeURIComponent(hash) } catch { pendingExamAnchor=hash }
  const normalize=(s:string)=>s.replace(/\.html$/,'').replace(/\/+$/,'')
  if(normalize(withBase(target))===normalize(route.path)){
    event.preventDefault()
    history.replaceState(history.state,'',withBase(path))
    jumpExamAnchor()
  } else {
    try{sessionStorage.setItem('skill-issue:exam-jump:v1',JSON.stringify({path:withBase(target),id:pendingExamAnchor}))}catch{}
  }
}
function openExam() {
  closePanels()
  window.dispatchEvent(new Event('skill-outline-close'))
  examOpen.value = true
}
const searchScope = ref('all')
type Bookmark = { path: string; title: string; hash?: string }
type ReadingPosition = Bookmark & { y: number; progress: number; offset?: number }
const lastRead = ref<ReadingPosition | null>(null)
const currentBookmark = ref<Bookmark | null>(null)
let saveTimer: ReturnType<typeof setTimeout> | undefined
let restoreFrame = 0
const progressKey = 'skill-issue:last-read:v1'
const resumeKey = 'skill-issue:resume:v1'
const wrapKey = 'skill-issue:wrap-code:v1'
const sections = [
  { title: 'Accueil', path: '/' },
  { title: 'Academy', path: '/academy/' },
  { title: 'Exam Mode · OSCP', path: '/oscp/exam' },
  { title: 'OSINT', path: '/osint/' },
  { title: 'Bug Bounty', path: '/bug-bounty/' },
  { title: 'OSCP', path: '/oscp/' },
  { title: 'CRTO', path: '/crto/' },
  { title: 'CRTP', path: '/crtp/' }
]
function readLocal<T>(key: string, fallback: T): T {
  try { const value = localStorage.getItem(key); return value ? JSON.parse(value) as T : fallback } catch { return fallback }
}
function writeLocal(key: string, value: unknown) {
  try { localStorage.setItem(key, JSON.stringify(value)) } catch { /* Storage can be disabled. */ }
}
function safePath(path: unknown): path is string {
  return typeof path === 'string' && path.startsWith(withBase('/')) && !path.startsWith('//')
}
function closePanels() {
  menuOpen.value = false
  examOpen.value = false
}
function onEscape(event: KeyboardEvent) { if (event.key === 'Escape') closePanels() }
function currentHeading() {
  return Array.from(currentDoc?.querySelectorAll<HTMLElement>('h1[id],h2[id],h3[id],h4[id],.academy-chapter[id],.academy-level[id]') ?? [])
    .filter(el => el.getClientRects().length && el.getBoundingClientRect().top <= 125).pop()
}
function saveReading() {
  if (!currentBookmark.value || !currentDoc || window.scrollY < 120 || !/\/(oscp|crto|crtp|osint|bug-bounty|academy)\//.test(currentBookmark.value.path)) return
  const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight)
  const heading = currentHeading()
  const position = { ...currentBookmark.value, y: window.scrollY, progress: Math.min(100, Math.round(window.scrollY / max * 100)), hash: heading?.id, offset: heading?.getBoundingClientRect().top }
  lastRead.value = position
  writeLocal(progressKey, position)
}
function queueReading() {
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(saveReading, 350)
}
function restorePosition(position: ReadingPosition) {
  showFull()
  closePanels()
  const el = position.hash ? document.getElementById(position.hash) : null
  if (el) {
    for (let node: HTMLElement | null = el; node; node = node.parentElement) {
      if (node instanceof HTMLDetailsElement) node.open = true
      if (node === currentDoc) break
    }
    const y = window.scrollY + el.getBoundingClientRect().top - (position.offset ?? 100)
    window.scrollTo({ top: Math.max(0, y), behavior: 'instant' as ScrollBehavior })
  } else window.scrollTo({ top: position.y, behavior: 'instant' as ScrollBehavior })
}
function resumeReading() {
  const item = lastRead.value
  if (!item || !safePath(item.path)) return
  if (window.location.pathname === item.path) restorePosition(item)
  else {
    try { sessionStorage.setItem(resumeKey, JSON.stringify(item)) } catch { /* fallback to anchor */ }
    window.location.assign(item.path + (item.hash ? '#' + encodeURIComponent(item.hash) : ''))
  }
}
function maybeRestore() {
  try {
    const raw = sessionStorage.getItem(resumeKey)
    if (!raw) return
    const item = JSON.parse(raw) as ReadingPosition
    if (!safePath(item.path) || item.path !== window.location.pathname) return
    sessionStorage.removeItem(resumeKey)
    restoreFrame = requestAnimationFrame(() => restorePosition(item))
  } catch { /* no stored position */ }
}
function toggleWrap() {
  wrapCode.value = !wrapCode.value
  writeLocal(wrapKey, wrapCode.value)
  currentDoc?.classList.toggle('skill-wrap-code', wrapCode.value && hasCode.value)
}
let currentDoc: HTMLElement | null = null
const storageKey = 'skill-issue:reading-mode'
const protectedContent = 'pre,code,table,img,svg,video,iframe,button,input,select,textarea,a,details,[id],[role],.custom-block,.bounty-command'

function clearDoc() {
  if (!currentDoc) return
  currentDoc.classList.remove('skill-cheatsheet-mode', 'skill-wrap-code', 'skill-library-index-hidden')
  delete currentDoc.dataset.skillTextSize
  currentDoc.querySelectorAll('[data-skill-reading-prose]').forEach(el => el.removeAttribute('data-skill-reading-prose'))
  currentDoc = null
}

function markProse(container: Element) {
  for (const child of Array.from(container.children)) {
    if (child.matches('p,ul,ol') && !child.matches('[id],[role],[class]') && !child.querySelector(protectedContent)) {
      child.setAttribute('data-skill-reading-prose', '')
    } else if (child.matches('details.custom-block, details:not([class]), div:not([class]):not([id]):not([role])')) {
      // Only traverse known Markdown wrappers. Do not alter custom widgets, warnings or command blocks.
      markProse(child)
    }
  }
}

function applyMode() {
  currentDoc?.classList.toggle('skill-cheatsheet-mode', hasCode.value && mode.value === 'quick')
  window.dispatchEvent(new Event('skill-reading-mode'))
}

function refresh() {
  const doc = document.querySelector<HTMLElement>('.VPDoc .vp-doc')
  if (doc !== currentDoc) clearDoc()
  currentDoc = doc
  if (doc) doc.dataset.skillTextSize = readingSize.value
  const technical = /\/(oscp|crto|crtp|osint|bug-bounty)\//.test(route.path)
  hasCode.value = !!(technical && doc?.querySelector('pre, .bounty-command'))
  const academy = /\/academy\//.test(route.path)
  hasOutline.value = !!(doc && frontmatter.value.outline !== false &&
    doc.querySelector('h2[id],h3[id],h4[id],h5[id],h6[id],.academy-chapter[id]'))
  const path = window.location.pathname
  const title = doc?.querySelector('h1')?.textContent?.replace(/\u200b/g, '').trim() || document.title.split('|')[0].trim()
  currentBookmark.value = safePath(path) && (technical || academy) ? { path, title } : null
  doc?.classList.toggle('skill-wrap-code', wrapCode.value && hasCode.value)
  if (doc && hasCode.value) {
    doc.querySelectorAll('[data-skill-reading-prose]').forEach(el => el.removeAttribute('data-skill-reading-prose'))
    markProse(doc)
  }
  applyMode()
  applyIndex()
  jumpExamAnchor()
}

async function setMode(value: 'read' | 'quick') {
  if (mode.value === value) return
  const visibleHeadings = Array.from(currentDoc?.querySelectorAll<HTMLElement>('h1[id],h2[id],h3[id],h4[id]') ?? [])
    .filter(el => el.getClientRects().length)
  const anchor = window.scrollY > 160 ? visibleHeadings.filter(el => el.getBoundingClientRect().top <= 120).pop() : undefined
  const previousTop = anchor?.getBoundingClientRect().top
  mode.value = value
  try { localStorage.setItem(storageKey, value) } catch { /* optional browser storage */ }
  applyMode()
  await nextTick()
  if (anchor && previousTop !== undefined) window.scrollBy(0, anchor.getBoundingClientRect().top - previousTop)
}

function openMenu() {
  window.dispatchEvent(new Event('skill-outline-close'))
  examOpen.value = false
  menuOpen.value = !menuOpen.value
}
function openChapterMenu() {
  closePanels()
  document.querySelector<HTMLButtonElement>('.VPLocalNav button.menu')?.click()
}
let scopeObserver: MutationObserver | undefined
let scopeTimeout: ReturnType<typeof setTimeout> | undefined
function clearSearchScope() {
  delete document.documentElement.dataset.skillSearchScope
  scopeObserver?.disconnect()
  scopeObserver = undefined
  if (scopeTimeout) clearTimeout(scopeTimeout)
}
function launchSearch(scope = 'all') {
  closePanels()
  window.dispatchEvent(new Event('skill-outline-close'))
  clearSearchScope()
  const button = document.querySelector<HTMLButtonElement>('#local-search button, .VPNavBarSearch button')
  if (!button) return
  if (scope !== 'all') {
    document.documentElement.dataset.skillSearchScope = scope
    let appeared = false
    scopeObserver = new MutationObserver(() => {
      const modal = document.querySelector('.VPLocalSearchBox')
      if (modal) {
        appeared = true
        if (scopeTimeout) clearTimeout(scopeTimeout)
      } else if (appeared) clearSearchScope()
    })
    scopeObserver.observe(document.body, { childList: true, subtree: true })
    scopeTimeout = setTimeout(() => { if (!appeared) clearSearchScope() }, 8000)
  }
  button.click()
}
function openSearch() { launchSearch() }
function searchInScope() { launchSearch(searchScope.value) }
function openOutline() { closePanels(); window.dispatchEvent(new Event('skill-outline-open')) }
function goTop() {
  closePanels()
  window.dispatchEvent(new Event('skill-outline-close'))
  window.scrollTo({ top: 0, behavior: 'auto' })
}

onMounted(async () => {
  try { if (localStorage.getItem(storageKey) === 'quick') mode.value = 'quick' } catch { /* optional browser storage */ }
  wrapCode.value = readLocal(wrapKey, false) === true
  const size = readLocal(sizeKey, 'normal')
  if (size === 'small' || size === 'normal' || size === 'large' || size === 'xl') readingSize.value = size
  const last = readLocal<ReadingPosition | null>(progressKey, null)
  lastRead.value = last && safePath(last.path) && Number.isFinite(last.y) ? last : null
  await nextTick()
  indexView.value=!window.location.hash
  refresh()
  ready.value = true
  applyIndex()
  document.documentElement.classList.add('skill-mobile-nav-ready')
  window.addEventListener('scroll', queueReading, { passive: true })
  window.addEventListener('pagehide', saveReading)
  window.addEventListener('keydown', onEscape)
  maybeRestore()
})
onContentUpdated(() => nextTick(refresh))
watch(() => route.path, () => {
  if (saveTimer) clearTimeout(saveTimer)
  closePanels()
  indexView.value=!window.location.hash
  nextTick(refresh)
}, { flush: 'post' })
onUnmounted(() => {
  if (saveTimer) clearTimeout(saveTimer)
  cancelAnimationFrame(restoreFrame)
  window.removeEventListener('scroll', queueReading)
  window.removeEventListener('pagehide', saveReading)
  window.removeEventListener('keydown', onEscape)
  clearSearchScope()
  document.documentElement.classList.remove('skill-mobile-nav-ready')
  clearDoc()
})
</script>

<template>
  <div class="skill-page-tools">
    <Breadcrumbs />
    <div v-if="showIndex" class="skill-inline-index"><h1>{{siteHeadings[sourcePath]?.find(h=>h.level===1)?.label || currentBookmark?.title || sectionTitle}}</h1><ExamSectionIndex :key="sourcePath" :source="sourcePath" inline @jump="jumpLibrary" @full="showFull" /></div>
    <button v-else-if="ready&&indexAvailable" type="button" class="skill-return-index" @click="showRubrics">‹ Rubriques</button>
    <div v-if="hasCode&&!showIndex" class="skill-reading-toolbar">
      <div class="skill-reading-label">Mode d’affichage</div>
      <div class="skill-reading-switch" role="group" aria-label="Mode d’affichage">
        <button type="button" :aria-pressed="mode === 'read'" @click="setMode('read')">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 6c-3-2-6-2-9-1v14c3-1 6-1 9 1 3-2 6-2 9-1V5c-3-1-6-1-9 1v14"/></svg> Lecture
        </button>
        <button type="button" :aria-pressed="mode === 'quick'" @click="setMode('quick')">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 6 6 6-6 6m9 0h7"/></svg> Cheatsheet
        </button>
      </div>
    </div>
    <PageFind />
    <div v-if="ready&&!showIndex" class="skill-library-toolbar">
      <label class="skill-size-control">Texte <select v-model="readingSize" @change="changeReadingSize" aria-label="Taille du texte"><option value="small">A−</option><option value="normal">A</option><option value="large">A+</option><option value="xl">A++</option></select></label>
      <button type="button" @click="findInPage">Rechercher dans la page</button>
      <button v-if="hasCode" type="button" :aria-pressed="wrapCode" @click="toggleWrap">{{ wrapCode ? 'Retour à la ligne' : 'Lignes originales' }}</button>
      <button v-if="lastRead" type="button" class="skill-library-desktop" @click="resumeReading">Reprendre ma lecture</button>
    </div>
    <div v-if="ready&&!onLibrary" class="skill-scoped-search-desktop">
      <div class="skill-search-scope">
        <label for="skill-search-scope">Rechercher dans</label>
        <select id="skill-search-scope" v-model="searchScope">
          <option value="all">Tout le site</option>
          <option value="academy">Academy</option>
          <option value="osint">OSINT</option>
          <option value="bug-bounty">Bug Bounty</option>
          <option value="oscp">OSCP</option>
          <option value="crto">CRTO</option>
          <option value="crtp">CRTP</option>
        </select>
        <button type="button" @click="searchInScope">Rechercher</button>
      </div>
    </div>
    <Teleport to="body" :disabled="!ready">
      <div v-if="menuOpen" class="skill-tools-overlay">
        <button type="button" class="skill-tools-backdrop" aria-label="Fermer" @click="closePanels" />
        <section class="skill-tools-panel" role="dialog" aria-label="Navigation">
          <header><strong>Navigation</strong><button type="button" aria-label="Fermer" @click="closePanels">×</button></header>
            <div v-if="lastRead" class="skill-resume">
              <small>Reprendre ma lecture</small>
              <button type="button" @click="resumeReading">{{ lastRead.title }} · {{ lastRead.progress }} %</button>
              <progress :value="lastRead.progress" max="100" />
            </div>
            <button v-if="!onLibrary && currentBookmark && !currentBookmark.path.includes('/academy/')" class="skill-tools-chapter" type="button" @click="openChapterMenu">Rubriques de la section ›</button>
            <a v-for="section in sections" :key="section.path" :href="withBase(section.path)" @click="closePanels">{{ section.title }} <span>›</span></a>
            <div class="skill-search-scope">
              <label for="skill-search-scope-mobile">Rechercher dans</label>
              <select id="skill-search-scope-mobile" v-model="searchScope">
                <option value="all">Tout le site</option>
                <option value="academy">Academy</option>
                <option value="osint">OSINT</option>
                <option value="bug-bounty">Bug Bounty</option>
                <option value="oscp">OSCP</option>
                <option value="crto">CRTO</option>
                <option value="crtp">CRTP</option>
              </select>
              <button type="button" @click="searchInScope">Rechercher</button>
            </div>
            <button v-if="onLibrary" type="button" @click="goTop">Retour en haut <span>↑</span></button>
            <details class="skill-menu-settings">
              <summary>Réglages d’affichage</summary>
              <div class="skill-menu-settings-body">
                <label class="skill-size-control">Taille du texte <select v-model="readingSize" @change="changeReadingSize" aria-label="Taille du texte"><option value="small">A−</option><option value="normal">A</option><option value="large">A+</option><option value="xl">A++</option></select></label>
                <label v-if="hasCode" class="skill-wrap-setting"><input type="checkbox" :checked="wrapCode" @change="toggleWrap"> Retour à la ligne des commandes</label>
              </div>
            </details>
        </section>
      </div>
      <div v-if="examOpen" class="skill-tools-overlay">
        <button type="button" class="skill-tools-backdrop" aria-label="Fermer" @click="closePanels" />
        <section class="skill-tools-panel skill-exam-panel" role="dialog" aria-modal="true" aria-label="Chapitres">
          <header><strong>Chapitres · {{sectionTitle}}</strong><button type="button" aria-label="Fermer" @click="closePanels">×</button></header>
          <ExamChapterTree v-if="inExam" :current-path="route.path" @navigate="navigateExam" @find="findInPage" />
          <LibraryChapterTree v-else :key="section" :section="section" :current-path="route.path" @navigate="navigateExam" @find="findInPage" />
        </section>
      </div>
    </Teleport>
    <nav v-if="ready" class="skill-mobile-tools" :style="{ '--skill-nav-count': onLibrary ? 3 + Number(hasCode) : 4 + Number(hasOutline) + Number(hasCode) }" aria-label="Accès rapides sur mobile">
      <button type="button" @click="openMenu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg><span>Menu</span></button>
      <button v-if="!onLibrary" type="button" aria-label="Recherche globale" @click="openSearch"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></svg><span>Chercher</span></button>
      <button v-if="!onLibrary && hasOutline" type="button" aria-label="Sommaire de la page" @click="openOutline"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5h11M9 12h11M9 19h11M4 5h.01M4 12h.01M4 19h.01"/></svg><span>Plan</span></button>
      <button v-if="onLibrary" type="button" aria-label="Chapitres et sous-chapitres" :aria-expanded="examOpen" @click="openExam"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 4v16m3-11h5m-5 5h5"/></svg><span>Chapitres</span></button>
      <button v-if="hasCode" type="button" :aria-pressed="mode === 'quick'" aria-label="Basculer entre Lecture et Cheatsheet" @click="showFull();setMode(mode === 'read' ? 'quick' : 'read')"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 6 6 6-6 6m9 0h7"/></svg><span>{{ mode === 'quick' ? 'Fiche' : 'Lecture' }}</span></button>
      <button v-if="!onLibrary" type="button" @click="findInPage" aria-label="Rechercher dans cette page"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 3H5v18h7M13 3v5h5v3M13 3l5 5"/><circle cx="17" cy="16" r="3.5"/><path d="m19.5 18.5 2.5 2.5"/></svg><span>Page</span></button>
      <button v-if="onLibrary" type="button" aria-label="Recherche dans la section" @click="launchSearch(section)"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></svg><span>Recherche</span></button>
      <button v-else type="button" @click="goTop"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20V4m-7 7 7-7 7 7"/></svg><span>Haut</span></button>
    </nav>
  </div>
</template>

<style>
.vp-doc.skill-library-index-hidden{display:none!important}
.skill-inline-index{margin:20px 0 28px;min-width:0}
.skill-inline-index h1{font-size:clamp(23px,4vw,32px);font-weight:700;line-height:1.25;margin:0 0 16px;color:var(--vp-c-text-1)}
.skill-return-index{color:#b39aff;min-height:44px;font-size:13px;text-align:left}
.skill-page-tools:has(.skill-inline-index) + .skill-outline--mobile{display:none!important}
.skill-cheatsheet-mode [data-skill-reading-prose] { display: none !important; }
.skill-reading-toolbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin: 0 0 18px; }
.skill-reading-label { color: #a99aba; font-size: 12px; font-weight: 600; }
.skill-reading-switch { display: inline-flex; gap: 3px; padding: 3px; border: 1px solid #3a2b4b; border-radius: 9px; background: #15101e; }
.skill-reading-switch button { display: flex; align-items: center; gap: 6px; color: #bdb2ce; font-size: 12px; font-weight: 600; padding: 8px 12px; border-radius: 6px; }
.skill-reading-switch button[aria-pressed="true"] { color: #e9d6ff; background: #35234f; }
.skill-reading-switch button:hover { color: #fff; }
.skill-reading-switch svg, .skill-mobile-tools svg { width: 17px; height: 17px; fill: none; stroke: currentColor; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
.skill-page-tools button:focus-visible, .skill-outline-mobile-header button:focus-visible { outline: 2px solid #b39aff; outline-offset: 2px; }
.skill-mobile-tools { display: none; }
@media (max-width: 767px) {
  .skill-page-tools .skill-reading-toolbar { display: none; }
  .skill-mobile-tools { display: grid; grid-template-columns: repeat(var(--skill-nav-count, 6), minmax(0, 1fr)); align-items: stretch; gap: 2px; position: fixed; z-index: 29; inset: auto 0 0; padding: 5px max(5px, env(safe-area-inset-right, 0px)) calc(5px + env(safe-area-inset-bottom, 0px)) max(5px, env(safe-area-inset-left, 0px)); background: #15101e; border-top: 1px solid #3a2b4b; box-shadow: 0 -4px 18px rgba(0,0,0,.28); }
  .skill-mobile-tools button { min-width: 0; height: 56px; padding: 4px 1px; display: grid; grid-template-rows: 23px 14px; align-content: center; justify-items: center; gap: 4px; color: #c7bed5; font-size: clamp(9px, 2.65vw, 11px); font-weight: 550; line-height: 14px; border-radius: 9px; box-sizing: border-box; transition: background-color .15s ease, color .15s ease; -webkit-tap-highlight-color: transparent; }
  .skill-mobile-tools button span { display: block; white-space: nowrap; text-align: center; max-width: 100%; overflow: hidden; text-overflow: ellipsis; }
  .skill-mobile-tools button:active { background: #302341; }
  .skill-mobile-tools button:focus-visible { outline-offset: -2px; }
  @media (prefers-reduced-motion: reduce) { .skill-mobile-tools button { transition: none; } }
  .skill-mobile-tools button svg { align-self: center; }
  .skill-mobile-tools button[aria-pressed="true"] { color: #e4caff; background: #2a1d39; }
  .skill-mobile-tools svg { width: 21px; height: 21px; color: #c4a4f4; }
  .skill-mobile-tools button[aria-pressed="true"] svg { color: #e2ccff; }
  .VPDoc:has(.skill-mobile-tools) { padding-bottom: max(100px, calc(85px + env(safe-area-inset-bottom, 0px))); }
}
/* Visual wrapping only: the DOM text and original copy handlers remain unchanged. */
.vp-doc.skill-wrap-code div[class*="language-"] pre,
.vp-doc.skill-wrap-code .bounty-command pre,
.vp-doc.skill-wrap-code .lab-command pre,
.vp-doc.skill-wrap-code pre.vp-code { white-space: pre-wrap !important; overflow-wrap: anywhere; }
.vp-doc.skill-wrap-code pre code, .vp-doc.skill-wrap-code pre code .line { white-space: inherit !important; overflow-wrap: inherit; }
.skill-library-toolbar { display:flex; flex-wrap:wrap; align-items:center; gap:7px; margin: 0 0 16px; }
.skill-library-toolbar button { font-size:12px; color:#d4c4e8; border:1px solid #3a2b4b; background:#15101e; border-radius:7px; padding:7px 10px; }
.skill-library-toolbar button[aria-pressed="true"] { background:#35234f; color:#f0e2ff; border-color:#71529a; }
.skill-tools-overlay { position:fixed; inset:0; z-index:80; display:flex; justify-content:center; align-items:center; }
.skill-tools-backdrop { position:absolute; inset:0; background:rgba(8,5,13,.7); }
.skill-tools-panel { position:relative; width:min(440px,calc(100% - 24px)); max-height:75dvh; overflow:auto; overscroll-behavior:contain; background:#15101e; border:1px solid #4a355e; border-radius:14px; padding:16px; color:#e5d8f4; box-shadow:0 10px 35px #0005; }
.skill-tools-panel header { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
.skill-tools-panel header button { flex:none; width:44px; min-height:44px; font-size:21px; }
.skill-tools-panel > a,.skill-tools-panel > button,.skill-resume button { display:flex; justify-content:space-between; align-items:center; text-align:left; width:100%; min-height:44px; padding:9px; border-bottom:1px solid #30243e; color:#d8c4f4; }
.skill-tools-panel .skill-tools-chapter { color:#e6d3ff; background:#2a1d39; border-radius:7px; margin-bottom:7px; }
.skill-tools-panel small { display:block; font-size:12px; color:#ab98c1; margin:12px 0 5px; }
 .skill-menu-settings { margin-top:12px; border:1px solid #3a2b4b; border-radius:8px; }
.skill-menu-settings summary { cursor:pointer; padding:12px; color:#dac6f5; font-size:13px; font-weight:600; }
.skill-menu-settings-body { display:grid; gap:10px; padding:0 12px 12px; }
.skill-menu-settings-body .skill-size-control { justify-content:space-between; }
.skill-wrap-setting { display:flex; align-items:center; gap:8px; min-height:40px; font-size:13px; color:#d8c4f4; cursor:pointer; }
.skill-wrap-setting input { width:18px; height:18px; flex:none; accent-color:#b39aff; }
.skill-exam-panel .skill-exam-home { background:#21172e; border-radius:7px; font-weight:650; }
.skill-exam-group { padding:8px 0 2px; }
.skill-exam-panel .skill-exam-group small { color:#b39aff; margin:4px 8px; font-size:12px; font-weight:650; }
.skill-exam-group a { display:flex; align-items:center; justify-content:space-between; gap:8px; min-height:44px; padding:8px; border-bottom:1px solid #30243e; color:#e6d9f6; font-size:14px; text-decoration:none; }
.skill-exam-group a[aria-current="page"] { background:#2a1d39; border-radius:6px; color:#ead9ff; }
.skill-exam-group a:hover,.skill-exam-group a:active { background:#261a35; }
.skill-resume { border:1px solid #3a2b4b; border-radius:8px; padding:9px; margin-bottom:8px; }
.skill-resume progress { width:100%; height:6px; accent-color:#b39aff; }
@media(max-width:767px) {
  .skill-page-tools .skill-library-toolbar { display:none; }
  .skill-library-desktop { display:none; }
  .skill-tools-overlay { align-items:flex-end; }
  .skill-tools-panel { width:100%; max-height:82dvh; border-radius:18px 18px 0 0; padding:12px 16px calc(16px + env(safe-area-inset-bottom,0px)); }
  .skill-tools-panel header { position:sticky; top:-12px; z-index:1; background:#15101e; padding:4px 0; margin-bottom:8px; border-bottom:1px solid #30243e; }
  .skill-tools-panel > a,.skill-tools-panel > button { min-height:48px; border-radius:6px; }
  .skill-tools-panel > a:active,.skill-tools-panel > button:active { background:#261a35; }
}
.skill-scoped-search-desktop { margin:0 0 16px; }
.skill-search-scope { display:flex; flex-wrap:wrap; align-items:center; gap:8px; padding:8px 0; }
.skill-search-scope label { font-size:12px; color:#b6aec5; }
.skill-search-scope select,.skill-search-scope button { min-height:34px; padding:5px 9px; border:1px solid #3a2b4b; border-radius:7px; background:#15101e; color:#d8c4f4; font-size:12px; }
.skill-search-scope button { background:#2a1d39; }
@media(max-width:767px) {
  .skill-scoped-search-desktop { display:none; }
  .skill-search-scope select,.skill-search-scope button { min-height:44px; }
}
.skill-size-control { display:inline-flex; align-items:center; gap:6px; font-size:12px; color:#c9b7e2; }
.skill-size-control select { min-height:34px; padding:5px 9px; border:1px solid #3a2b4b; background:#15101e; color:#e0caff; border-radius:6px; }
.vp-doc[data-skill-text-size="small"] { --skill-prose-size:14px; --skill-code-size:12px; }
.vp-doc[data-skill-text-size="large"] { --skill-prose-size:18px; --skill-code-size:15px; }
.vp-doc[data-skill-text-size="xl"] { --skill-prose-size:21px; --skill-code-size:17px; }
.vp-doc[data-skill-text-size]:not([data-skill-text-size="normal"]) :is(p,li,blockquote,td,th,.academy-resource-content>a,.academy-explanation) { font-size:var(--skill-prose-size) !important; }
.vp-doc[data-skill-text-size]:not([data-skill-text-size="normal"]) :is(pre,pre code,pre code .line,code,.bounty-command pre) { font-size:var(--skill-code-size) !important; }
</style>

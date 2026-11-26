<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useData, useRoute, onContentUpdated } from 'vitepress'

const route = useRoute()
const { frontmatter } = useData()
const mode = ref<'read' | 'quick'>('read')
const hasCode = ref(false)
const hasOutline = ref(false)
let currentDoc: HTMLElement | null = null
const storageKey = 'skill-issue:reading-mode'
const protectedContent = 'pre,code,table,img,svg,video,iframe,button,input,select,textarea,a,details,[id],[role],.custom-block,.bounty-command'

function clearDoc() {
  if (!currentDoc) return
  currentDoc.classList.remove('skill-cheatsheet-mode')
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
  const technical = /\/(oscp|crto|crtp|osint|bug-bounty)\//.test(route.path)
  hasCode.value = !!(technical && doc?.querySelector('pre, .bounty-command'))
  hasOutline.value = !!(doc && frontmatter.value.outline !== false &&
    (frontmatter.value.aside !== false || technical) &&
    doc.querySelector('h2[id],h3[id],h4[id],h5[id],h6[id]'))
  if (doc && hasCode.value) {
    doc.querySelectorAll('[data-skill-reading-prose]').forEach(el => el.removeAttribute('data-skill-reading-prose'))
    markProse(doc)
  }
  applyMode()
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
  const local = document.querySelector<HTMLButtonElement>('.VPLocalNav button.menu')
  const global = document.querySelector<HTMLButtonElement>('.VPNavBarHamburger')
  ;(local && local.getClientRects().length ? local : global)?.click()
}
function openSearch() {
  window.dispatchEvent(new Event('skill-outline-close'))
  const button = document.querySelector<HTMLButtonElement>('#local-search button, .VPNavBarSearch button')
  if (button) button.click()
}
function openOutline() { window.dispatchEvent(new Event('skill-outline-open')) }
function goTop() {
  window.dispatchEvent(new Event('skill-outline-close'))
  window.scrollTo({ top: 0, behavior: 'auto' })
}

onMounted(async () => {
  try { if (localStorage.getItem(storageKey) === 'quick') mode.value = 'quick' } catch { /* optional browser storage */ }
  await nextTick()
  refresh()
})
onContentUpdated(() => nextTick(refresh))
watch(() => route.path, () => nextTick(refresh), { flush: 'post' })
onUnmounted(clearDoc)
</script>

<template>
  <div class="skill-page-tools">
    <div v-if="hasCode" class="skill-reading-toolbar">
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
    <nav class="skill-mobile-tools" aria-label="Accès rapides sur mobile">
      <button type="button" @click="openMenu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg><span>Menu</span></button>
      <button type="button" @click="openSearch"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></svg><span>Recherche</span></button>
      <button v-if="hasOutline" type="button" @click="openOutline"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5h11M9 12h11M9 19h11M4 5h.01M4 12h.01M4 19h.01"/></svg><span>Sommaire</span></button>
      <button v-if="hasCode" type="button" :aria-pressed="mode === 'quick'" aria-label="Basculer entre Lecture et Cheatsheet" @click="setMode(mode === 'read' ? 'quick' : 'read')"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 6 6 6-6 6m9 0h7"/></svg><span>{{ mode === 'quick' ? 'Lecture' : 'Cheatsheet' }}</span></button>
      <button type="button" @click="goTop"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20V4m-7 7 7-7 7 7"/></svg><span>Haut</span></button>
    </nav>
  </div>
</template>

<style>
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
  .skill-reading-toolbar { margin-bottom: 14px; }
  .skill-reading-label { font-size: 11px; }
  .skill-reading-switch button { min-height: 44px; padding: 8px 10px; }
  .skill-mobile-tools { display: flex; position: fixed; z-index: 29; inset: auto 0 0; padding: 5px max(5px, env(safe-area-inset-right, 0px)) calc(5px + env(safe-area-inset-bottom, 0px)) max(5px, env(safe-area-inset-left, 0px)); background: #15101e; border-top: 1px solid #3a2b4b; box-shadow: 0 -6px 20px rgba(0,0,0,.22); }
  .skill-mobile-tools button { flex: 1 1 0; min-width: 0; min-height: 49px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; color: #bdb2ce; font-size: 10px; line-height: 1.2; border-radius: 6px; }
  .skill-mobile-tools button[aria-pressed="true"] { color: #e4caff; background: #2a1d39; }
  .skill-mobile-tools svg { width: 19px; height: 19px; color: #c4a4f4; }
  .VPDoc:has(.skill-mobile-tools) { padding-bottom: max(100px, calc(85px + env(safe-area-inset-bottom, 0px))); }
}
</style>

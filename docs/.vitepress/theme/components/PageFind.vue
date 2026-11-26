<script setup lang="ts">
import { ref, nextTick, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vitepress'
const route = useRoute()
const opened = ref(false), ready = ref(false), query = ref(''), count = ref(0), index = ref(0)
const field = ref<HTMLInputElement | null>(null)
let hits: Range[] = []
let active: HTMLElement | null = null
let timeout: ReturnType<typeof setTimeout> | undefined
function highlightSet(name: string, ranges: Range[]) {
  const api = (window.CSS as any)?.highlights
  const Ctor = (window as any).Highlight
  if (api && Ctor) api.set(name, new Ctor(...ranges))
}
function clearHighlights() {
  const api = (window.CSS as any)?.highlights
  api?.delete('skill-page-find-all'); api?.delete('skill-page-find-current')
  active?.classList.remove('skill-page-find-target')
  active = null
}
function close() {
  opened.value = false
  if (timeout) clearTimeout(timeout)
  clearHighlights()
  hits = []; count.value = 0; query.value = ''
}
async function open() {
  if (opened.value) { field.value?.focus(); return }
  opened.value = true
  await nextTick(); field.value?.focus()
}
function collect() {
  clearHighlights(); hits = []; index.value = 0
  const term = query.value.trim().toLocaleLowerCase()
  const doc = document.querySelector('.VPDoc .vp-doc')
  if (!term || !doc) { count.value = 0; return }
  // Match complete code lines across syntax-highlight spans, without modifying any source text.
  const blocks = doc.querySelectorAll<HTMLElement>('pre, p, li, h1, h2, h3, h4, h5, h6, td, th, summary, .academy-resource-content, .inspector-selectable')
  for (const block of blocks) {
    if (block.closest('.skill-cheatsheet-mode [data-skill-reading-prose], [hidden], .academy-explanation[style*="display: none"]')) continue
    if (block.querySelector('pre,p,li,h1,h2,h3,h4,h5,h6,td,th,.academy-resource-content')) continue
    const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT, { acceptNode(node) {
      return node.parentElement?.closest('button,script,style,.header-anchor,[aria-hidden="true"],[hidden],.academy-explanation[style*="display: none"]') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT
    } })
    const nodes: { node: Text; start: number; end: number }[] = []
    let text = '', n: Node | null
    while ((n = walker.nextNode())) {
      const value = n.nodeValue || ''
      nodes.push({ node:n as Text, start:text.length, end:text.length+value.length }); text+=value
    }
    const normalized = text.toLocaleLowerCase()
    // Lowercase may change the length of uncommon Unicode characters; skip those blocks rather than create invalid ranges.
    if (normalized.length !== text.length) continue
    for (let pos = normalized.indexOf(term); pos !== -1; pos = normalized.indexOf(term,pos+term.length)) {
      const first = nodes.find(x => x.start <= pos && x.end > pos)
      const last = nodes.find(x => x.start < pos+term.length && x.end >= pos+term.length)
      if (first && last) {
        const range = document.createRange()
        range.setStart(first.node,pos-first.start); range.setEnd(last.node,pos+term.length-last.start)
        hits.push(range)
      }
      if (hits.length >= 3000) break
    }
    if (hits.length >= 3000) break
  }
  count.value = hits.length
  highlightSet('skill-page-find-all',hits)
  if (hits.length) go(0)
}
function go(delta: number) {
  if (!hits.length) return
  index.value = (index.value + delta + hits.length) % hits.length
  const range = hits[index.value]
  const el = range.startContainer.parentElement
  if (!el || !el.isConnected) { collect(); return }
  for (let p: HTMLElement | null = el; p; p=p.parentElement) {
    if (p instanceof HTMLDetailsElement) p.open = true
    if (p.classList.contains('vp-doc')) break
  }
  active?.classList.remove('skill-page-find-target')
  active = el.closest('pre,p,li,h1,h2,h3,h4,h5,h6,td,th,summary,.academy-resource-content') as HTMLElement || el
  active.classList.add('skill-page-find-target')
  highlightSet('skill-page-find-current',[range])
  nextTick(() => {
    const r = range.getBoundingClientRect()
    if (r.height) {
      const y = window.scrollY + r.top - window.innerHeight * .35
      window.scrollTo({ top:Math.max(0,y),behavior:'auto' })
      const pre = el.closest('pre')
      if (pre) { const box = pre.getBoundingClientRect(); if (r.right > box.right || r.left < box.left) pre.scrollLeft += r.left-box.left-20 }
    } else active?.scrollIntoView({ block:'center' })
  })
}
function onInput() { if (timeout) clearTimeout(timeout); timeout=setTimeout(collect,120) }
function key(event: KeyboardEvent) {
  if (event.key === 'Escape' && opened.value) close()
}
onMounted(() => { ready.value=true; window.addEventListener('skill-page-find',open); window.addEventListener('keydown',key) })
watch(() => route.path,close)
onBeforeUnmount(() => { window.removeEventListener('skill-page-find',open); window.removeEventListener('keydown',key); close() })
</script>
<template>
  <Teleport to="body" :disabled="!ready">
    <section v-if="opened" class="skill-find-bar" role="search" aria-label="Rechercher dans cette page">
      <input ref="field" v-model="query" type="search" placeholder="Texte, commande, outil…" aria-label="Rechercher dans la page" @input="onInput" @keydown.enter.prevent="go($event.shiftKey ? -1 : 1)">
      <span aria-live="polite">{{ count ? (index+1)+' / '+count+(count===3000?'+':'') : query.trim() ? '0 résultat' : '' }}</span>
      <button type="button" :disabled="!count" aria-label="Résultat précédent" @click="go(-1)">↑</button>
      <button type="button" :disabled="!count" aria-label="Résultat suivant" @click="go(1)">↓</button>
      <button type="button" aria-label="Fermer la recherche" @click="close">×</button>
    </section>
  </Teleport>
</template>
<style>
.skill-find-bar { position:fixed; z-index:85; top:12px; right:12px; display:flex; align-items:center; gap:5px; max-width:calc(100% - 24px); background:#191320; border:1px solid #654a86; border-radius:10px; padding:8px; box-shadow:0 8px 30px #0006; color:#e4d3f4; }
.skill-find-bar input { flex:1; min-width:0; width:230px; padding:8px; border:1px solid #49345d; border-radius:6px; font-size:16px; color:#e6d5f8; background:#100d17; }
.skill-find-bar span { min-width:28px; font-size:11px; white-space:nowrap; }
.skill-find-bar button { min-width:35px; height:40px; font-size:19px; color:#d7bdf8; border-radius:5px; }
.skill-find-bar button:disabled { opacity:.35; }
.skill-page-find-target { outline:1px solid #b39aff !important; outline-offset:2px; }
::highlight(skill-page-find-all) { color:#f4eaff; background:#62458b; }
::highlight(skill-page-find-current) { color:#120b1a; background:#e0b9ff; }
@media(max-width:767px) { .skill-find-bar { top:8px; left:8px; right:8px; max-width:none; } .skill-find-bar input { width:100%; } .skill-find-bar button { min-width:35px; } }
</style>

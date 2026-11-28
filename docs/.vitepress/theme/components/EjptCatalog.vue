<script setup lang="ts">
import { computed, ref } from 'vue'
import { withBase } from 'vitepress'
import { groups, sheets } from '../data/ejpt-catalog'
const props = defineProps<{mode:'course'|'cheatsheet'}>()
const query = ref('')
const normalize = (value:string) => value.normalize('NFD').replace(/\p{M}/gu,'').toLowerCase()
const terms = computed(() => normalize(query.value).trim().split(/\s+/).filter(Boolean))
const visible = computed(() => groups.map(g => ({
  ...g,
  children:g.children.filter(c => {
    const label = normalize(g.title+' '+c.title)
    return terms.value.every(term => label.includes(term))
  })
})).filter(g=>g.children.length))
const count = computed(() => groups.reduce((n,g)=>n+g.children.length,0))
const visibleCount = computed(() => visible.value.reduce((n,g)=>n+g.children.length,0))
const href = (path:string) => withBase('/ejpt/original/'+path)
function open(event:MouseEvent,path:string){
  event.stopPropagation()
  if(event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey) return
  event.preventDefault()
  window.location.assign(href(path))
}
</script>

<template>
  <div class="ejpt-catalog">
    <div v-if="mode==='course'" class="ejpt-toolbar">
      <span aria-live="polite">{{terms.length ? visibleCount + ' / ' + count + ' pages' : groups.length + ' modules · ' + count + ' pages'}}</span>
      <input v-model="query" type="search" placeholder="Rechercher un chapitre…" aria-label="Rechercher un chapitre" />
    </div>
    <template v-if="mode==='course'">
      <a class="ejpt-intro" :href="href('README.html')" @click="open($event,'README.html')">
        <span><strong>Introduction au parcours</strong><small>Vue d’ensemble et préparation</small></span><span aria-hidden="true">›</span>
      </a>
      <details v-for="group in visible" :key="group.id" :id="group.id" class="ejpt-module" :open="terms.length ? true : undefined">
        <summary><span class="ejpt-number">{{group.number}}</span><span class="ejpt-title"><strong>{{group.title}}</strong><small>{{group.description}}</small></span><span class="ejpt-count">{{group.children.length}}</span><span class="ejpt-chevron" aria-hidden="true">⌄</span></summary>
        <div class="ejpt-chapters">
          <a v-for="chapter in group.children" :key="chapter.path" :href="href(chapter.path)" @click="open($event,chapter.path)" :style="{paddingInlineStart:Math.min(chapter.depth,3)*16+12+'px'}"><span>{{chapter.title}}</span><span aria-hidden="true">›</span></a>
        </div>
      </details>
      <p v-if="!visible.length" class="ejpt-empty">Aucun chapitre trouvé.</p>
    </template>
    <template v-else>
      <div class="ejpt-sheet-grid">
        <a v-for="sheet in sheets" :key="sheet.path" :href="href(sheet.path)" @click="open($event,sheet.path)" class="ejpt-sheet">
          <span><strong>{{sheet.title}}</strong><small>{{sheet.description}}</small></span><span aria-hidden="true">›</span>
        </a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.ejpt-catalog{display:grid;gap:12px;margin:24px 0}
.ejpt-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;color:var(--vp-c-text-2);font-size:13px;flex-wrap:wrap}
.ejpt-toolbar input{min-width:0;width:min(100%,290px);padding:10px 12px;border:1px solid var(--vp-c-divider);border-radius:8px;background:var(--vp-c-bg-soft);color:var(--vp-c-text-1)}
.ejpt-toolbar input:focus{outline:2px solid var(--vp-c-brand-1)}
.ejpt-module{margin:0;border:1px solid #392e49;border-radius:10px;background:var(--vp-c-bg-soft);overflow:hidden;scroll-margin-top:90px}
.ejpt-module summary{display:flex;align-items:center;gap:12px;cursor:pointer;padding:15px;list-style:none}
.ejpt-module summary::-webkit-details-marker{display:none}
.ejpt-module summary:hover,.ejpt-intro:hover,.ejpt-sheet:hover{background:#21182c}
.ejpt-number{flex:none;font-size:12px;font-weight:700;color:var(--vp-c-brand-1);border:1px solid #4f3c68;border-radius:6px;padding:4px 8px}
.ejpt-title,.ejpt-intro>span:first-child,.ejpt-sheet>span:first-child{flex:1;min-width:0;display:grid;gap:3px}
.ejpt-title strong,.ejpt-intro strong,.ejpt-sheet strong{font-size:15px;color:var(--vp-c-text-1);font-weight:650;line-height:1.45}
.ejpt-title small,.ejpt-intro small,.ejpt-sheet small{color:var(--vp-c-text-2);font-size:12px;line-height:1.4}
.ejpt-count{font-size:12px;color:var(--vp-c-text-2)}
.ejpt-chevron{font-size:20px;color:var(--vp-c-brand-1);transition:transform .15s}
.ejpt-module[open] .ejpt-chevron{transform:rotate(180deg)}
.ejpt-chapters{border-top:1px solid #392e49;padding:6px}
.ejpt-chapters a,.ejpt-intro,.ejpt-sheet{display:flex;align-items:center;justify-content:space-between;gap:10px;text-decoration:none!important}
.ejpt-chapters a{padding:9px 12px;border-radius:6px;color:var(--vp-c-text-2);font-size:14px;line-height:1.5}
.ejpt-chapters a>span:first-child{min-width:0;overflow-wrap:anywhere}
.ejpt-chapters a>span:last-child{flex:none}
.ejpt-chapters a:focus-visible,.ejpt-intro:focus-visible,.ejpt-sheet:focus-visible,.ejpt-module summary:focus-visible{outline:2px solid var(--vp-c-brand-1);outline-offset:-2px}
.ejpt-chapters a:hover{color:var(--vp-c-brand-1);background:var(--vp-c-bg)}
.ejpt-intro,.ejpt-sheet{padding:15px;border:1px solid #392e49;border-radius:10px;background:var(--vp-c-bg-soft);color:var(--vp-c-brand-1)}
.ejpt-sheet-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.ejpt-empty{color:var(--vp-c-text-2)}
@media(max-width:640px){.ejpt-sheet-grid{grid-template-columns:1fr}.ejpt-module summary{padding:12px;gap:8px}.ejpt-count{display:none}}
</style>

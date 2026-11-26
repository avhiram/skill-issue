<script setup lang="ts">
import { computed, ref } from 'vue'
import { withBase } from 'vitepress'
import { data as headings } from '../examHeadings.data'
const props=defineProps<{source:string; inline?:boolean}>()
const emit=defineEmits<{(e:'jump',id:string):void;(e:'full'):void}>()
type Entry={label:string;id:string;level:number;parents:Entry[]}
const sourcePath=computed(()=>props.source.split('#')[0])
const entries=computed(()=>{
  let items=(headings[sourcePath.value]||[]).filter(h=>h.level>=2)
  const hash=props.source.split('#')[1]
  if(hash){
    const start=items.findIndex(x=>x.id===hash)
    if(start<0)return []
    const level=items[start].level
    let end=start+1
    while(end<items.length&&items[end].level>level)end++
    items=items.slice(start,end)
  }
  const stack:Entry[]=[]
  return items.map(item=>{
    while(stack.length&&stack[stack.length-1].level>=item.level)stack.pop()
    const entry={...item,parents:[...stack]}
    stack.push(entry)
    return entry
  })
})
const query=ref('')
const expanded=ref(new Set<string>())
const norm=(s:string)=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim()
const terms=computed(()=>norm(query.value).split(/\s+/).filter(Boolean))
const filtering=computed(()=>terms.value.length>0)
const visible=computed(()=>entries.value.filter(item=>{
  if(filtering.value){
    const text=norm([...item.parents.map(p=>p.label),item.label].join(' '))
    return terms.value.every(t=>text.includes(t))
  }
  return item.parents.every(parent=>expanded.value.has(parent.id))
}))
const parentIds=computed(()=>new Set(entries.value.flatMap(item=>item.parents.map(parent=>parent.id))))
const allExpanded=computed(()=>parentIds.value.size>0&&[...parentIds.value].every(id=>expanded.value.has(id)))
function toggleAll(){expanded.value=new Set(allExpanded.value?[]:parentIds.value)}
function toggle(id:string){
 const next=new Set(expanded.value)
 if(next.has(id))next.delete(id);else next.add(id)
 expanded.value=next
}
function href(entry:Entry){return withBase(sourcePath.value+'#'+encodeURIComponent(entry.id))}
function remember(entry:Entry,event:MouseEvent){
 if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||event.button!==0)return
 if(props.inline){event.preventDefault();emit('jump',entry.id);return}
 try{sessionStorage.setItem('skill-issue:exam-context:v1',withBase(sourcePath.value));sessionStorage.setItem('skill-issue:exam-jump:v1',JSON.stringify({path:withBase(sourcePath.value),id:entry.id}))}catch{}
}
function rememberFull(event:MouseEvent){if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||event.button!==0)return;try{sessionStorage.setItem('skill-issue:exam-context:v1',withBase(sourcePath.value))}catch{}}
</script>
<template>
  <div class="exam-index">
    <div v-if="entries.length" class="exam-index-search">
      <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></svg>
      <input v-model="query" type="search" placeholder="Rechercher une rubrique…" aria-label="Rechercher une rubrique" autocomplete="off" spellcheck="false">
      <button v-if="query" type="button" aria-label="Effacer" @click="query=''">×</button>
    </div>
    <div v-if="entries.length" class="skill-rubric-meta"><span aria-live="polite">{{ filtering ? visible.length : entries.length }} rubrique{{ (filtering ? visible.length : entries.length) > 1 ? 's' : '' }}</span><button v-if="!filtering&&parentIds.size" type="button" @click="toggleAll">{{ allExpanded ? 'Tout replier' : 'Tout déplier' }}</button></div>
    <nav v-if="entries.length" class="exam-index-list" aria-label="Sous-rubriques">
      <div v-for="entry in visible" :key="entry.id" class="exam-index-row" :style="{paddingInlineStart:filtering?'0px':Math.min(entry.parents.length,4)*12+'px'}">
        <a :href="href(entry)" @click="remember(entry,$event)">
          <small v-if="filtering&&entry.parents.length">{{ entry.parents.map(p=>p.label).join(' › ') }}</small>
          <span>{{entry.label}}</span>
        </a>
        <button v-if="!filtering&&parentIds.has(entry.id)" type="button" :aria-label="'Sous-rubriques : '+entry.label" :aria-expanded="expanded.has(entry.id)" @click="toggle(entry.id)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" :style="{transform:expanded.has(entry.id)?'rotate(90deg)':'none'}" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>
        </button>
        <svg v-else class="exam-index-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>
      </div>
      <p v-if="!visible.length" role="status">Aucun résultat.</p>
    </nav>
    <button v-if="inline" class="exam-index-full" type="button" @click="emit('full')">Ouvrir la fiche complète <span aria-hidden="true">›</span></button>
    <a v-else class="exam-index-full" :href="withBase(source)" @click="rememberFull">Ouvrir la fiche complète <span aria-hidden="true">›</span></a>
  </div>
</template>
<style scoped>
.skill-rubric-meta{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#a99aba;font-size:12px}.skill-rubric-meta button{min-height:36px;color:#c4a4f4;padding:0 4px}
.exam-index{display:grid;gap:10px;margin-top:14px;min-width:0}
.exam-index-search{display:flex;align-items:center;gap:8px;min-height:48px;padding:0 12px;border:1px solid #49345e;border-radius:9px;background:#15101e;color:#b39aff}
.exam-index-search:focus-within{border-color:#b39aff}
.exam-index-search input{flex:1;min-width:0;width:100%;height:46px;background:transparent;color:#f0edf8;outline:none;font-size:16px}
.exam-index-search input::placeholder{color:#a99aba}
.exam-index-search input::-webkit-search-cancel-button{display:none}
.exam-index-search button{width:36px;height:44px;font-size:22px;flex:none}
.exam-index-list{display:grid}
.exam-index-row{display:flex;align-items:center;gap:8px;min-height:45px;border-bottom:1px solid #29213a}
.exam-index-row>a{flex:1;min-width:0;display:grid;gap:3px;align-content:center;min-height:45px;padding:8px 4px;color:#e6d9f6;font-size:14px;font-weight:550;line-height:1.4;text-decoration:none;overflow-wrap:anywhere}
.exam-index-row>a:hover,.exam-index-row>a:active{background:#20162c;color:#f1e5ff}
.exam-index-row>a small{color:#a99aba;font-size:11px;font-weight:400}
.exam-index-row button{display:grid;place-items:center;min-height:44px;width:44px;flex:none;color:#b39aff}
.exam-index-arrow{margin-right:14px;color:#a68cc7;flex:none;pointer-events:none}
.exam-index-list p{font-size:13px;color:#b6aec5}
.exam-index-full{text-align:left;display:flex;justify-content:space-between;align-items:center;min-height:44px;color:#b39aff;font-size:13px;text-decoration:none}
</style>

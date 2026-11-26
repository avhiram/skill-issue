<script setup lang="ts">
import { computed, ref } from 'vue'
import { useData, withBase } from 'vitepress'
import { data as headings } from '../examHeadings.data'
const props=defineProps<{section:string;currentPath:string}>()
const emit=defineEmits<{(e:'navigate',path:string,event:MouseEvent):void;(e:'find'):void}>()
const {theme}=useData()
type Node={key:string;label:string;path?:string;children:Node[]}
type SidebarItem={text?:string;link?:string;items?:SidebarItem[]}
const normalize=(s:string)=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim()
const clean=(s:string)=>s.split('#')[0].split('?')[0].replace(/\.html$/,'').replace(/\/index$/,'').replace(/\/+$/,'')
const prefix='/'+props.section
const current=(path:string)=>clean(withBase(path))===clean(props.currentPath)
const used=new Set<string>()
function headingNodes(path:string):Node[]{
 const stack:{level:number;node:Node}[]=[]
 const roots:Node[]=[]
 for(const h of (headings[path]||[]).filter(h=>h.level>=2)){
  const node:Node={key:path+'#'+h.id,label:h.label,path:path+'#'+encodeURIComponent(h.id),children:[]}
  while(stack.length&&stack[stack.length-1].level>=h.level)stack.pop()
  if(stack.length)stack[stack.length-1].node.children.push(node);else roots.push(node)
  stack.push({level:h.level,node})
 }
 return roots
}
function sidebarPath(link:string){
 let raw=link
 if(/^https?:\/\//.test(raw)){try{raw=new URL(raw).pathname}catch{return ''}}
 const i=raw.indexOf(prefix+'/')
 if(i>=0)raw=raw.slice(i)
 return clean(raw)
}
function convert(items:SidebarItem[],parent:string):Node[]{
 return items.flatMap((item,i)=>{
  const key=parent+':'+i
  const raw=item.link?sidebarPath(item.link):''
  const nested=convert(item.items||[],key)
  if(raw===prefix)return nested
  if(raw&&raw.startsWith(prefix+'/')&&headings[raw]&&!used.has(raw)&&!item.link?.includes('#')){
    used.add(raw)
    return [{key,label:item.text||raw,path:raw,children:headingNodes(raw)}]
  }
  return nested.length?[{key,label:item.text||'Rubriques',children:nested}]:[]
 })
}
const config=theme.value.sidebar
const sidebar=Array.isArray(config)?config:config?.[prefix+'/']
const roots=convert(Array.isArray(sidebar)?sidebar:sidebar?.items||[],'sidebar')
const extra=Object.keys(headings).filter(p=>p.startsWith(prefix+'/')&&!used.has(p)&&!p.startsWith('/oscp/exam-')&&p!=='/oscp/exam').sort().map(path=>({key:path,label:headings[path].find(h=>h.level===1)?.label||path.split('/').pop()!,path,children:headingNodes(path)}))
if(extra.length)roots.push({key:'other',label:roots.length?'Autres fiches':'Rubriques',children:extra})
const expanded=ref(new Set<string>())
function activate(nodes:Node[],parents:string[]=[]){
 for(const node of nodes){
  if(node.path&&current(node.path))parents.forEach(k=>expanded.value.add(k))
  activate(node.children,[...parents,node.key])
 }
}
activate(roots)
const query=ref('')
const terms=computed(()=>normalize(query.value).split(/\s+/).filter(Boolean))
const filtering=computed(()=>terms.value.length>0)
function prune(node:Node):Node|null{
 const children=node.children.map(prune).filter((x):x is Node=>x!==null)
 return terms.value.every(t=>normalize(node.label).includes(t))||children.length?{...node,children}:null
}
const rows=computed(()=>{
 const out:{node:Node;depth:number}[]=[]
 const walk=(node:Node,depth:number)=>{out.push({node,depth});if(filtering.value||expanded.value.has(node.key))node.children.forEach(x=>walk(x,depth+1))}
 const visible=filtering.value?roots.map(prune).filter((x):x is Node=>x!==null):roots
 visible.forEach(n=>walk(n,0))
 return out
})
function toggle(k:string){const next=new Set(expanded.value);if(next.has(k))next.delete(k);else next.add(k);expanded.value=next}
</script>
<template>
 <div class="library-tree">
  <div class="library-search">
   <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></svg>
   <input v-model="query" type="search" placeholder="Chapitre ou sous-rubrique…" aria-label="Rechercher dans la section" autocomplete="off">
   <button v-if="query" type="button" aria-label="Effacer" @click="query=''">×</button>
  </div>
  <a class="library-home" :href="withBase(prefix+'/')" @click="emit('navigate',prefix+'/',$event)">Accueil de la section <span>›</span></a>
  <a v-if="section==='oscp'" class="library-home" :href="withBase('/oscp/exam')" @click="emit('navigate','/oscp/exam',$event)">Exam Mode <span>›</span></a>
  <div v-for="row in rows" :key="row.node.key" class="library-row" :class="{'is-group':!row.node.path,'is-current':row.node.path&&!row.node.path.includes('#')&&current(row.node.path)}" :style="{paddingInlineStart:Math.min(row.depth,5)*12+'px'}">
    <a v-if="row.node.path" :href="withBase(row.node.path)" @click="emit('navigate',row.node.path,$event)">{{row.node.label}}</a>
    <button v-else class="library-label" type="button" :aria-expanded="filtering||expanded.has(row.node.key)" @click="toggle(row.node.key)">{{row.node.label}}</button>
    <button v-if="row.node.children.length" class="library-toggle" type="button" :aria-label="'Sous-rubriques : '+row.node.label" :aria-expanded="filtering||expanded.has(row.node.key)" @click="toggle(row.node.key)"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" :style="{transform:filtering||expanded.has(row.node.key)?'rotate(90deg)':'none'}" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg></button>
  </div>
  <p v-if="!rows.length" class="library-empty">Aucune rubrique trouvée.</p>
  <button class="library-home" type="button" @click="emit('find')">Rechercher dans la page actuelle <span>›</span></button>
 </div>
</template>
<style scoped>
.library-tree{display:grid;min-width:0}
.library-search{display:flex;align-items:center;gap:8px;min-height:48px;border:1px solid #49345e;border-radius:8px;color:#b39aff;padding:0 10px;margin-bottom:8px}
.library-search input{min-width:0;flex:1;height:46px;font-size:16px;outline:none;background:transparent;color:#f1e7ff}
.library-search input::placeholder{color:#a99aba;font-size:13px}
.library-search button{width:36px;height:44px;flex:none;font-size:21px}
.library-home{display:flex;align-items:center;justify-content:space-between;min-height:44px;color:#b39aff;font-size:13px;text-align:left;border-bottom:1px solid #30243e}
.library-row{display:flex;align-items:center;min-height:44px;border-bottom:1px solid #29213a;min-width:0}
.library-row>a,.library-label{flex:1;min-width:0;text-align:left;padding:10px 5px;min-height:44px;line-height:1.4;font-size:13px;color:#e6d9f6;overflow-wrap:anywhere}
.library-label{font-weight:650;color:#cfb4f7;font-size:14px}
.library-row.is-current{background:#291e38;border-radius:6px}
.library-toggle{width:44px;min-height:44px;display:grid;place-items:center;flex:none;color:#b39aff}
.library-empty{padding:12px 0;color:#b6aec5;font-size:13px}
</style>

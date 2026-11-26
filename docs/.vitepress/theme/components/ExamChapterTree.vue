<script setup lang="ts">
import { computed, ref } from 'vue'
import { withBase } from 'vitepress'
import { examGroups, examIndexPath } from '../examNavigation'
import { portEntries } from '../portNavigation'
import { data as headings } from '../examHeadings.data'
const props=defineProps<{ currentPath:string }>()
const emit=defineEmits<{ (e:'navigate',path:string,event:MouseEvent):void; (e:'find'):void }>()
type Node={key:string;label:string;path?:string;children:Node[];meta?:string}
const query=ref('')
const expanded=ref(new Set<string>())
const normalize=(s:string)=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim()
const pagePath=(s:string)=>s.split('#')[0].replace(/\.html$/,'').replace(/\/+$/,'')
const current=(path:string)=>pagePath(withBase(path))===pagePath(props.currentPath)
function headingNodes(path:string):Node[]{
  const base=pagePath(path)
  const stack:{level:number;node:Node}[]=[]
  const roots:Node[]=[]
  for(const heading of headings[base]||[]){
    const node={key:base+'#'+heading.id,label:heading.label,path:base+'#'+encodeURIComponent(heading.id),children:[] as Node[]}
    while(stack.length&&stack[stack.length-1].level>=heading.level)stack.pop()
    if(stack.length)stack[stack.length-1].node.children.push(node);else roots.push(node)
    stack.push({level:heading.level,node})
  }
  return roots
}
const groups:Node[]=examGroups.map(group=>({key:'group:'+group.title,label:group.title,children:group.links.map(link=>{
  const children=link.path==='/oscp/exam-ports' ? portEntries.map(port=>({key:'port:'+port.path,label:port.label,meta:port.ports,path:port.path,children:[] as Node[]})) : headingNodes(link.path)
  return {key:link.path,label:link.label,path:examIndexPath(link.path),children}
})}))
for(const group of groups){
  const active=group.children.find(node=>node.path&&(current(node.path)||Object.entries(examGroups.flatMap(g=>g.links)).some(([,link])=>examIndexPath(link.path)===node.path&&current(link.path))))
  if(active){expanded.value.add(group.key)}
}
function toggle(key:string){const next=new Set(expanded.value);if(next.has(key))next.delete(key);else next.add(key);expanded.value=next}
const terms=computed(()=>normalize(query.value).split(/\s+/).filter(Boolean))
const filtering=computed(()=>terms.value.length>0)
function matches(node:Node){const value=normalize(node.label+' '+(node.meta||''));return terms.value.every(term=>/^\d+$/.test(term)&&node.meta?node.meta.split(',').some(port=>port.trim()===term):value.includes(term))}
function prune(node:Node):Node|null {
 const children=node.children.map(prune).filter((x):x is Node=>x!==null)
 if(matches(node))return {...node,children}
 return children.length?{...node,children}:null
}
const visibleGroups=computed(()=>filtering.value?groups.map(prune).filter((x):x is Node=>x!==null):groups)
type Row={node:Node;depth:number}
const rows=computed(()=>{
 const output:Row[]=[]
 function walk(node:Node,depth:number){output.push({node,depth});if(filtering.value||expanded.value.has(node.key))node.children.forEach(child=>walk(child,depth+1))}
 visibleGroups.value.forEach(node=>walk(node,0))
 return output
})
</script>
<template>
  <div class="exam-tree">
    <div class="exam-tree-search">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></svg>
      <input v-model="query" type="search" placeholder="Chapitre, sous-chapitre, port…" aria-label="Rechercher dans les chapitres OSCP" autocomplete="off" spellcheck="false">
      <button v-if="query" type="button" aria-label="Effacer" @click="query=''">×</button>
    </div>
    <a class="exam-tree-home" :href="withBase('/oscp/exam')" @click="emit('navigate','/oscp/exam',$event)">Accueil de l’examen <span>›</span></a>
    <div v-for="row in rows" :key="row.node.key" class="exam-tree-row" :class="{'is-group':row.depth===0,'is-current':row.depth===1&&row.node.path&&current(row.node.path)}" :style="{paddingInlineStart:Math.min(row.depth,5)*12+'px'}">
      <a v-if="row.node.path" :href="withBase(row.node.path)" @click="emit('navigate',row.node.path,$event)">
        <span v-if="row.node.meta" class="exam-tree-port">{{row.node.meta}}</span>{{row.node.label}}
      </a>
      <button v-else class="exam-tree-group-label" type="button" :aria-expanded="filtering||expanded.has(row.node.key)" @click="toggle(row.node.key)">{{row.node.label}}</button>
      <button v-if="row.node.children.length" class="exam-tree-toggle" type="button" :aria-label="'Sous-chapitres : '+row.node.label" :aria-expanded="filtering||expanded.has(row.node.key)" @click="toggle(row.node.key)"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" :style="{transform:filtering||expanded.has(row.node.key)?'rotate(90deg)':'none'}" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg></button>
    </div>
    <p v-if="!rows.length" class="exam-tree-empty">Aucun titre correspondant.</p>
    <button class="exam-tree-find" type="button" @click="emit('find')">Rechercher dans le texte de la page actuelle</button>
  </div>
</template>
<style scoped>
.exam-tree{display:grid;gap:0;min-width:0}
.exam-tree-search{display:flex;align-items:center;gap:8px;min-height:48px;padding:0 10px;border:1px solid #49345e;border-radius:8px;color:#b39aff;margin-bottom:8px}
.exam-tree-search input{width:100%;min-width:0;flex:1;height:46px;font-size:16px;outline:none;color:#f1e7ff;background:transparent}
.exam-tree-search input::placeholder{color:#a99aba;font-size:13px}
.exam-tree-search button{width:36px;height:44px;font-size:21px;flex:none}
.exam-tree-home{display:flex;justify-content:space-between;align-items:center;min-height:44px;color:#b39aff;font-size:13px;border-bottom:1px solid #30243e}
.exam-tree-row{display:flex;align-items:center;min-height:44px;gap:2px;border-bottom:1px solid #29213a;min-width:0}
.exam-tree-row.is-group{color:#cfb4f7;font-weight:650}
.exam-tree-row.is-current{background:#291e38;border-radius:6px}
.exam-tree-row>a,.exam-tree-group-label{flex:1;min-width:0;text-align:left;padding:10px 5px;min-height:44px;line-height:1.4;font-size:13px;color:#e6d9f6;overflow-wrap:anywhere}
.exam-tree-group-label{color:#cfb4f7;font-size:14px}
.exam-tree-toggle{width:44px;min-height:44px;display:grid;place-items:center;flex:none;color:#b39aff}
.exam-tree-port{color:#b39aff;font-size:12px;font-variant-numeric:tabular-nums;margin-right:8px}
.exam-tree-empty{padding:12px 0;color:#b6aec5;font-size:13px}
.exam-tree-find{min-height:44px;text-align:left;color:#b9a7d0;font-size:12px;margin-top:10px}
</style>

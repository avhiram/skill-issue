<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useData, withBase } from 'vitepress'

type Item = { text?: string; link?: string; items?: Item[] }
const { page, theme, frontmatter } = useData()
const openGroup = ref(-1)
function normalize(value: string) {
  return value.replace(/^https?:\/\/avhiram\.github\.io\/skill-issue(?=\/)/i, '')
    .replace(/^\/skill-issue(?=\/)/, '').split(/[?#]/)[0]
    .replace(/\.(html|md)$/i,'').replace(/\/index$/i,'').replace(/\/+$/,'') || '/'
}
const path = computed(() => normalize('/' + page.value.relativePath))
const section = computed(() => path.value.split('/')[1] || '')
const sectionTitles: Record<string,string> = { oscp:'OSCP',crto:'CRTO',crtp:'CRTP',osint:'OSINT','bug-bounty':'Bug Bounty',academy:'Academy' }
function find(items: Item[], target: string, trail: Item[] = []): Item[] | undefined {
  for (const item of items) {
    const next = [...trail,item]
    if (item.link && !item.link.includes('#') && normalize(item.link) === target) return next
    const child = find(item.items || [], target, next)
    if (child) return child
  }
}
function links(items: Item[]): Item[] {
  return items.flatMap(item => item.link && item.text ? [item] : links(item.items || []))
}
function href(link: string) {
  return /^https?:\/\//i.test(link) ? link : withBase(link)
}
const crumbs = computed(() => {
  const s = section.value
  if (!sectionTitles[s]) return []
  const root = '/' + s
  if (path.value === root) return [{text:sectionTitles[s],current:true} as Item & {current:boolean}]
  const sidebar = theme.value.sidebar as Record<string,Item[]> | Item[] | undefined
  const items = Array.isArray(sidebar) ? sidebar : sidebar?.[root+'/'] || sidebar?.['/'] || []
  const trail = find(items,path.value) || []
  const prefix: Item[] = [{text:sectionTitles[s],link:root+'/'}]
  if (trail.length) {
    const filtered = trail.filter(item => !(item.link && normalize(item.link)===root))
    // Groups with no route are presented as actual navigable child-link menus.
    prefix.push(...filtered)
  } else {
    if (s==='oscp' && /\/mindmap-/.test(path.value)) prefix.push({text:'Mindmaps',link:'/oscp/mindmaps'})
    prefix.push({text:frontmatter.value.title || page.value.title || path.value.split('/').pop() || ''})
  }
  return prefix.map((item,i) => ({...item,current:i===prefix.length-1}))
})
watch(path,()=>{openGroup.value=-1})
</script>
<template>
  <nav v-if="crumbs.length" class="skill-breadcrumbs" aria-label="Fil d’Ariane">
    <a class="skill-crumb-home" :href="withBase('/')" aria-label="Accueil"><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 10 9-7 9 7v10h-6v-6H9v6H3z"/></svg></a>
    <template v-for="(item,i) in crumbs" :key="i">
      <span class="skill-crumb-separator" aria-hidden="true">›</span>
      <span v-if="item.current" class="skill-crumb-current" aria-current="page">{{ item.text }}</span>
      <a v-else-if="item.link" :href="href(item.link)">{{ item.text }}</a>
      <span v-else-if="item.items?.length" class="skill-crumb-group" @keydown.esc="openGroup=-1">
        <button type="button" :aria-expanded="openGroup===i" @click="openGroup=openGroup===i?-1:i">{{ item.text }} <span aria-hidden="true">⌄</span></button>
        <span v-if="openGroup===i" class="skill-crumb-dropdown">
          <a v-for="child in links(item.items)" :key="child.link" :href="href(child.link!)" @click="openGroup=-1">{{ child.text }}</a>
        </span>
      </span>
      <span v-else>{{ item.text }}</span>
    </template>
  </nav>
</template>
<style scoped>
.skill-breadcrumbs { display:flex; align-items:center; flex-wrap:wrap; gap:5px 8px; margin:0 0 18px; font-size:12px; line-height:1.6; color:#ae9dc4; }
.skill-breadcrumbs a,.skill-breadcrumbs button { color:#bba0ec; text-decoration:none; }
.skill-breadcrumbs a:hover,.skill-breadcrumbs button:hover { color:#f1e3ff; text-decoration:underline; }
.skill-crumb-home { display:inline-flex; align-items:center; }
.skill-crumb-separator { color:#746284; font-size:16px; }
.skill-crumb-current { color:#ded0ef; overflow-wrap:anywhere; }
.skill-crumb-group { position:relative; }
.skill-crumb-dropdown { position:absolute; left:0; top:calc(100% + 6px); z-index:45; display:flex; flex-direction:column; width:max-content; max-width:min(260px,75vw); max-height:50vh; overflow:auto; padding:6px; background:#1b1426; border:1px solid #503b6b; border-radius:8px; box-shadow:0 8px 24px #0006; }
.skill-crumb-dropdown a { padding:8px 10px; border-radius:5px; white-space:normal; }
.skill-crumb-dropdown a:hover { background:#2a1d39; }
@media(max-width:767px) { .skill-breadcrumbs { font-size:12px; gap:3px 6px; margin:0 0 12px; line-height:1.45; } .skill-crumb-dropdown a { min-height:44px; } .skill-crumb-current { font-weight:600; } }
</style>

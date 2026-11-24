<script setup>
import { computed, ref, shallowRef, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { withBase } from 'vitepress'

const data = shallowRef(null)
const error = ref('')
const svg = ref(null)
const root = ref(null)
const expanded = ref(false)
const selected = ref(null)
const query = ref('')
const matchIndex = ref(0)
const view = ref({ x: 0, y: 0, k: 1 })
const dragging = ref(false)
const pointers = new Map()
let clickCandidate = null
let moved = false
let observer
const palette = { '1': '#fb7185', '2': '#f59e0b', '3': '#facc15', '4': '#4ade80', '5': '#22d3ee', '6': '#a78bfa' }
const color = (c, fallback = '#76658c') => palette[c] || (/^#[0-9a-f]{6}$/i.test(c || '') ? c : fallback)
const groups = computed(() => data.value?.nodes.filter(n => n.type === 'group') || [])
const nodes = computed(() => data.value?.nodes.filter(n => n.type === 'text') || [])
const byId = computed(() => new Map((data.value?.nodes || []).map(n => [n.id, n])))
const bounds = computed(() => {
  const a = data.value?.nodes || []
  return a.length ? { x: Math.min(...a.map(n => n.x)), y: Math.min(...a.map(n => n.y)), right: Math.max(...a.map(n => n.x + n.width)), bottom: Math.max(...a.map(n => n.y + n.height)) } : { x: 0, y: 0, right: 100, bottom: 100 }
})
const matches = computed(() => {
  const q = query.value.trim().toLowerCase()
  return q ? [...groups.value, ...nodes.value].filter(n => (n.label || n.text || '').toLowerCase().includes(q)) : []
})
const matchIds = computed(() => new Set(matches.value.map(n => n.id)))
const transform = computed(() => 'translate(' + view.value.x + ' ' + view.value.y + ') scale(' + view.value.k + ')')
const percent = computed(() => Math.round(view.value.k * 100))
function point(n, side) {
  if (side === 'top') return [n.x + n.width / 2, n.y, 0, -1]
  if (side === 'bottom') return [n.x + n.width / 2, n.y + n.height, 0, 1]
  if (side === 'left') return [n.x, n.y + n.height / 2, -1, 0]
  return [n.x + n.width, n.y + n.height / 2, 1, 0]
}
const edges = computed(() => (data.value?.edges || []).flatMap(e => {
  const a = byId.value.get(e.fromNode), b = byId.value.get(e.toNode)
  if (!a || !b) return []
  const [x1,y1,dx1,dy1] = point(a, e.fromSide)
  const [x2,y2,dx2,dy2] = point(b, e.toSide)
  const d = Math.max(40, Math.min(600, Math.hypot(x2-x1,y2-y1)*0.35))
  return [{ ...e, path: 'M '+x1+' '+y1+' C '+(x1+dx1*d)+' '+(y1+dy1*d)+', '+(x2+dx2*d)+' '+(y2+dy2*d)+', '+x2+' '+y2, mx:(x1+x2)/2, my:(y1+y2)/2 }]
}))
function viewport() { return { w: svg.value?.clientWidth || 800, h: svg.value?.clientHeight || 600 } }
function frame(box) {
  const { w,h } = viewport()
  const k = Math.max(0.015, Math.min(2.5, (w-60)/Math.max(1,box.width), (h-60)/Math.max(1,box.height)))
  view.value = { k, x: w/2-(box.x+box.width/2)*k, y: h/2-(box.y+box.height/2)*k }
}
function fit() { const b=bounds.value; frame({ x:b.x,y:b.y,width:b.right-b.x,height:b.bottom-b.y }) }
function focus(n) { if (!n) return; selected.value = n.type === 'text' ? n : null; frame({ x:n.x-50,y:n.y-50,width:n.width+100,height:n.height+100 }) }
function jumpGroup(event) { const n=byId.value.get(event.target.value); if(n) focus(n); event.target.value='' }
function searchStep(step = 0) { if(!matches.value.length) return; matchIndex.value=(matchIndex.value+step+matches.value.length)%matches.value.length; focus(matches.value[matchIndex.value]) }
function searchChanged() { matchIndex.value=0 }
function zoomAt(f, px, py) {
  const v=view.value, k=Math.max(0.015,Math.min(3,v.k*f)), ratio=k/v.k
  view.value={ k, x:px-(px-v.x)*ratio, y:py-(py-v.y)*ratio }
}
function zoom(f) { const { w,h }=viewport(); zoomAt(f,w/2,h/2) }
function position(e) { const r=svg.value.getBoundingClientRect(); return { x:e.clientX-r.left,y:e.clientY-r.top } }
function wheel(e) { const p=position(e); zoomAt(Math.exp(-e.deltaY*0.0015),p.x,p.y) }
function down(e) {
  if(e.pointerType==='mouse' && e.button!==0) return
  if(!pointers.size) { moved=false; clickCandidate=e.target.closest?.('[data-node]')?.getAttribute('data-node') || null }
  else { moved=true; clickCandidate=null }
  pointers.set(e.pointerId,position(e))
  svg.value.setPointerCapture?.(e.pointerId)
  dragging.value=true
}
function move(e) {
  if(!pointers.has(e.pointerId)) return
  const prev=[...pointers.values()], p=position(e), old=pointers.get(e.pointerId)
  pointers.set(e.pointerId,p)
  const curr=[...pointers.values()]
  if(Math.hypot(p.x-old.x,p.y-old.y)>1) moved=true
  if(curr.length===2) {
    const a=prev[0],b=prev[1],c=curr[0],d=curr[1], dist=Math.hypot(a.x-b.x,a.y-b.y), next=Math.hypot(c.x-d.x,c.y-d.y)
    const cx=(a.x+b.x)/2,cy=(a.y+b.y)/2
    if(dist>0) zoomAt(next/dist,cx,cy)
    view.value={...view.value,x:view.value.x+(c.x+d.x)/2-cx,y:view.value.y+(c.y+d.y)/2-cy}
  } else if(curr.length===1) view.value={...view.value,x:view.value.x+p.x-old.x,y:view.value.y+p.y-old.y}
}
function up(e) {
  if(!pointers.has(e.pointerId)) return
  pointers.delete(e.pointerId)
  if(!pointers.size) {
    dragging.value=false
    if(!moved && clickCandidate && e.type==='pointerup') {
      const n=byId.value.get(clickCandidate)
      if(n?.type==='text') selected.value=n
      else if(n) focus(n)
    }
    clickCandidate=null
  }
}
function toggleExpanded() { expanded.value=!expanded.value; nextTick(fit) }
function onKey(e) { if(e.key==='Escape'){ if(expanded.value) toggleExpanded(); else selected.value=null } }
const isCode = n => (n.text || '').includes('```')
function cardText(n) { return (n.text || '').replace(/^\s*```[^\n]*$/gm, '').trim() }
onMounted(async () => {
  window.addEventListener('keydown',onKey)
  try {
    const response=await fetch(withBase('/mindmap-ad.canvas.json'))
    if(!response.ok) throw Error('HTTP '+response.status)
    const canvas=await response.json()
    if(!Array.isArray(canvas.nodes)||!Array.isArray(canvas.edges)) throw Error('Format Canvas invalide')
    data.value=canvas
    await nextTick(); fit()
    observer=new ResizeObserver(() => { if(!dragging.value && !selected.value) fit() })
    if(svg.value) observer.observe(svg.value)
  } catch(e){ error.value='Impossible de charger le Canvas : '+e.message }
})
onBeforeUnmount(() => { observer?.disconnect(); window.removeEventListener('keydown',onKey) })
</script>

<template>
  <section ref="root" class="ad-mindmap" :class="{ expanded }">
    <div class="map-bar">
      <div class="map-heading"><span class="map-dot"></span><strong>Active Directory</strong><small v-if="data">{{ data.nodes.length }} éléments · {{ data.edges.length }} liens</small></div>
      <div class="map-controls">
        <button type="button" @click="zoom(1/1.25)" title="Dézoomer" aria-label="Dézoomer">−</button>
        <span class="zoom-readout">{{ percent }} %</span>
        <button type="button" @click="zoom(1.25)" title="Zoomer" aria-label="Zoomer">+</button>
        <button type="button" @click="fit">Vue globale</button>
        <button type="button" @click="toggleExpanded">{{ expanded ? 'Quitter plein écran' : 'Plein écran' }}</button>
      </div>
    </div>
    <div class="map-filters">
      <div class="map-search">
        <input v-model="query" type="search" placeholder="Rechercher dans la mind map…" aria-label="Rechercher dans la mind map" @input="searchChanged" @keydown.enter.prevent="searchStep(0)">
        <button type="button" @click="searchStep(0)" :disabled="!matches.length">Rechercher</button>
        <button type="button" @click="searchStep(-1)" :disabled="!matches.length" aria-label="Résultat précédent">‹</button>
        <button type="button" @click="searchStep(1)" :disabled="!matches.length" aria-label="Résultat suivant">›</button>
        <small v-if="query.trim()">{{ matches.length ? (matchIndex+1)+' / '+matches.length : 'Aucun résultat' }}</small>
      </div>
      <select aria-label="Aller à une branche" @change="jumpGroup"><option value="">Aller à une branche</option><option v-for="g in groups" :key="g.id" :value="g.id">{{ g.label }}</option></select>
    </div>
    <div v-if="error" class="map-message" role="alert">{{ error }}</div>
    <div v-else-if="!data" class="map-message">Chargement du Canvas…</div>
    <div v-else class="map-stage">
      <svg ref="svg" class="map-svg" :class="{ dragging }" aria-label="Canvas Active Directory interactif" @wheel.prevent="wheel" @pointerdown="down" @pointermove="move" @pointerup="up" @pointercancel="up" @lostpointercapture="up">
        <defs><marker id="ad-map-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M 0 0 L 8 4 L 0 8 z" fill="#9a84b8"/></marker></defs>
        <g :transform="transform">
          <g v-for="g in groups" :key="g.id">
            <rect :x="g.x" :y="g.y" :width="g.width" :height="g.height" rx="20" :fill="color(g.color)" fill-opacity=".075" :stroke="color(g.color)" stroke-opacity=".8" stroke-width="5" pointer-events="none"/>
            <foreignObject :x="g.x+12" :y="g.y-44" :width="Math.max(g.width,300)" height="44" :data-node="g.id">
              <div xmlns="http://www.w3.org/1999/xhtml" class="map-group-label" :style="{ color: color(g.color,'#c4a6f5') }" v-text="g.label"></div>
            </foreignObject>
          </g>
          <g v-for="e in edges" :key="e.id" pointer-events="none">
            <path :d="e.path" fill="none" :stroke="color(e.color,'#86769b')" stroke-width="3" stroke-opacity=".72" marker-end="url(#ad-map-arrow)"/>
            <text v-if="e.label" :x="e.mx" :y="e.my-8" class="map-edge-label" text-anchor="middle">{{ e.label }}</text>
          </g>
          <g v-for="n in nodes" :key="n.id" :data-node="n.id">
            <rect :x="n.x" :y="n.y" :width="n.width" :height="n.height" rx="9" fill="#181320" :stroke="matchIds.has(n.id) ? '#e6caff' : color(n.color,'#4d3c63')" :stroke-width="selected?.id===n.id || matchIds.has(n.id) ? 5 : 2.5"/>
            <foreignObject :x="n.x+5" :y="n.y+3" :width="Math.max(1,n.width-10)" :height="Math.max(1,n.height-6)">
              <div xmlns="http://www.w3.org/1999/xhtml" class="map-node-text" :class="{ 'map-code': isCode(n) }" :style="{ color: n.color ? color(n.color,'#f1eafc') : '#e8def4' }" v-text="cardText(n)"></div>
            </foreignObject>
          </g>
        </g>
      </svg>
      <div v-if="selected" class="map-inspector" @pointerdown.stop>
        <div class="inspector-header"><strong>Carte sélectionnée</strong><button type="button" @click="selected=null" aria-label="Fermer la carte">×</button></div>
        <pre v-text="selected.text"></pre>
      </div>
      <span class="map-hint">Glisser pour naviguer · Molette / pincement pour zoomer · Toucher une carte pour la lire</span>
    </div>
  </section>
</template>

<style scoped>
:global(.VPDoc:has(.ad-mindmap) .content-container){max-width:none!important}
:global(.VPDoc:has(.ad-mindmap) .container){max-width:none!important}
.ad-mindmap{--map-bg:#100d17;--map-panel:#1b1426;--map-border:#3e2c56;--map-fg:#f1eafa;border:1px solid var(--map-border);border-radius:12px;overflow:hidden;background:var(--map-bg);color:var(--map-fg);margin:24px 0;display:flex;flex-direction:column;min-width:0}
.ad-mindmap.expanded{position:fixed;inset:0;z-index:9999;margin:0;border:0;border-radius:0}
.map-bar,.map-filters{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;padding:11px 13px;background:var(--map-panel);border-bottom:1px solid var(--map-border)}
.map-heading,.map-controls,.map-search{display:flex;align-items:center;flex-wrap:wrap;gap:8px}
.map-heading strong{font-size:14px}.map-heading small,.map-search small,.zoom-readout{font-size:11px;color:#b8a7cf}
.map-dot{width:8px;height:8px;border-radius:50%;background:#a78bfa;box-shadow:0 0 12px #a78bfa}
.ad-mindmap button,.ad-mindmap input,.ad-mindmap select{font:inherit;font-size:12px;line-height:1.3;color:#eee5f9;background:#211831;border:1px solid #503b6b;border-radius:6px;padding:7px 10px}
.ad-mindmap button{cursor:pointer}.ad-mindmap button:hover{border-color:#a78bfa;background:#352348}.ad-mindmap button:disabled{opacity:.4;cursor:default}
.ad-mindmap input{width:min(240px,100%)}.ad-mindmap select{max-width:100%}
.map-stage{position:relative;height:clamp(460px,70vh,900px);min-height:0;overflow:hidden;flex:1}
.expanded .map-stage{height:auto;flex:1}.map-svg{display:block;width:100%;height:100%;touch-action:none;cursor:grab;background-color:#100d17;background-image:radial-gradient(#2b2238 1px,transparent 1px);background-size:20px 20px;user-select:none}
.map-svg.dragging{cursor:grabbing}
.map-group-label{font:600 28px/1.2 system-ui,sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;pointer-events:auto}
.map-node-text{width:100%;height:100%;box-sizing:border-box;display:flex;align-items:center;justify-content:center;padding:4px;white-space:pre-wrap;overflow-wrap:anywhere;overflow:hidden;text-align:center;font:500 18px/1.18 system-ui,sans-serif}
.map-node-text.map-code{display:block;text-align:left;font:400 15px/1.15 ui-monospace,SFMono-Regular,Consolas,monospace;padding:5px}
.map-edge-label{font:500 16px system-ui,sans-serif;fill:#c4b4d7}
.map-hint{position:absolute;bottom:10px;left:10px;right:10px;font-size:10px;color:#b8a7cf;pointer-events:none;text-shadow:0 1px 3px #000}
.map-inspector{position:absolute;right:12px;top:12px;width:min(400px,calc(100% - 24px));max-height:calc(100% - 55px);overflow:auto;border:1px solid #594077;border-radius:10px;background:#1b1426;box-shadow:0 8px 32px #0008;color:#eee5f9}
.inspector-header{display:flex;align-items:center;justify-content:space-between;padding:10px 12px;border-bottom:1px solid #3e2c56;font-size:12px}
.map-inspector pre{font:12px/1.6 ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere;margin:0;padding:14px;color:#eee5f9;background:transparent}
.map-message{padding:30px;color:#c7b5dd;font-size:13px}
@media(max-width:640px){.map-controls{gap:4px}.map-bar,.map-filters{padding:8px}.map-search{gap:5px}.ad-mindmap input{width:160px}.map-stage{height:65vh;min-height:350px}.map-inspector{width:calc(100% - 24px);max-height:45%;top:auto;bottom:28px}}
</style>

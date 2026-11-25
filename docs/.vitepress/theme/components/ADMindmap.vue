<script setup>
import { computed, ref, shallowRef, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { withBase } from 'vitepress'

const props = defineProps({ src: { type: String, default: '/mindmap-ad.canvas.json' }, title: { type: String, default: 'Active Directory' } })
const data = shallowRef(null)
const error = ref('')
const svg = ref(null)
const root = ref(null)
const expanded = ref(false)
const selected = ref(null)
const copyState = ref('')
function selectBlock(field) {
  if(!field)return
  field.focus({preventScroll:true})
  field.setSelectionRange(0,field.value.length)
}
watch(selected, () => { copyState.value = '' })
function splitCard(raw) {
  const parts = []
  let lines = [], language = '', inCode = false
  function flush() {
    const value = lines.join('\n')
    if (value.trim()) parts.push({ type: inCode ? 'code' : 'text', language, value: inCode ? value : value.trim() })
    lines = []
  }
  for (const line of String(raw || '').replace(/\r\n/g, '\n').split('\n')) {
    const fence = line.match(/^\s*`{3,}\s*([^\s`]*)\s*$/)
    if (fence && (!inCode || !fence[1])) {
      flush()
      inCode = !inCode
      language = inCode ? fence[1] : ''
    } else lines.push(line)
  }
  flush()
  return parts
}
const cardParts = computed(() => splitCard([selected.value?.text || selected.value?.file || '', selected.value?.description || ''].filter(Boolean).join('\n\n')))
const allCopyText = computed(() => {
  const codes = cardParts.value.filter(p => p.type === 'code')
  return (codes.length ? codes : cardParts.value).map(p => p.value).join('\n\n')
})
async function copyCard(value, key) {
  if (!value) return
  const original = selected.value?.id
  let ok = false
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(value)
      ok = true
    }
  } catch {}
  if (!ok) {
    const previousFocus = document.activeElement
    const field = document.createElement('textarea')
    field.value = value
    field.readOnly = true
    field.style.cssText = 'position:fixed;left:0;top:0;opacity:0;pointer-events:none;font-size:16px'
    document.body.appendChild(field)
    try {
      field.focus()
      field.select()
      field.setSelectionRange(0, field.value.length)
      ok = document.execCommand('copy')
    } catch {} finally {
      field.remove()
      previousFocus?.focus?.({ preventScroll: true })
    }
  }
  if (selected.value?.id === original) copyState.value = ok ? key : 'failed'
}
const query = ref('')
const matchIndex = ref(0)
const view = ref({ x: 0, y: 0, k: 1 })
const dragging = ref(false)
const pointers = new Map()
let clickCandidate = null
let moved = false
let pressOrigin = null
let observer
const palette = { '1': '#fb7185', '2': '#f59e0b', '3': '#facc15', '4': '#4ade80', '5': '#22d3ee', '6': '#a78bfa' }
const color = (c, fallback = '#76658c') => palette[c] || (/^#[0-9a-f]{6}$/i.test(c || '') ? c : fallback)
const groups = computed(() => data.value?.nodes.filter(n => n.type === 'group') || [])
const nodes = computed(() => data.value?.nodes.filter(n => n.type !== 'group') || [])
const byId = computed(() => new Map((data.value?.nodes || []).map(n => [n.id, n])))
const bounds = computed(() => {
  const a = data.value?.nodes || []
  return a.length ? { x: Math.min(...a.map(n => n.x)), y: Math.min(...a.map(n => n.y)), right: Math.max(...a.map(n => n.x + n.width)), bottom: Math.max(...a.map(n => n.y + n.height)) } : { x: 0, y: 0, right: 100, bottom: 100 }
})
const matches = computed(() => {
  const q = query.value.trim().toLowerCase()
  return q ? [...groups.value, ...nodes.value].filter(n => (n.label || n.text || n.file || '').toLowerCase().includes(q)) : []
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
function focus(n) { if (!n) return; selected.value = n.type !== 'group' ? n : null; frame({ x:n.x-50,y:n.y-50,width:n.width+100,height:n.height+100 }) }
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
function nodeAt(e) {
  const p=position(e), v=view.value
  const x=(p.x-v.x)/v.k, y=(p.y-v.y)/v.k
  // The complete rectangle is a touch target, including its blank margins.
  const target=e.target.closest?.('[data-node]')?.getAttribute('data-node')
  if(target)return target
  return [...nodes.value].reverse().find(n=>x>=n.x&&x<=n.x+n.width&&y>=n.y&&y<=n.y+n.height)?.id || null
}
function down(e) {
  if(e.pointerType==='mouse' && e.button!==0) return
  e.preventDefault()
  if(!pointers.size) { moved=false; pressOrigin=position(e); clickCandidate=nodeAt(e) }
  else { moved=true; clickCandidate=null }
  pointers.set(e.pointerId,position(e))
  try { svg.value.setPointerCapture?.(e.pointerId) } catch {}
  dragging.value=true
}
function move(e) {
  if(!pointers.has(e.pointerId)) return
  const prev=[...pointers.values()], p=position(e), old=pointers.get(e.pointerId)
  pointers.set(e.pointerId,p)
  const curr=[...pointers.values()]
  if(pressOrigin && Math.hypot(p.x-pressOrigin.x,p.y-pressOrigin.y)>7) moved=true
  if(curr.length===2) {
    const a=prev[0],b=prev[1],c=curr[0],d=curr[1], dist=Math.hypot(a.x-b.x,a.y-b.y), next=Math.hypot(c.x-d.x,c.y-d.y)
    const cx=(a.x+b.x)/2,cy=(a.y+b.y)/2
    if(dist>0) zoomAt(next/dist,cx,cy)
    view.value={...view.value,x:view.value.x+(c.x+d.x)/2-cx,y:view.value.y+(c.y+d.y)/2-cy}
  } else if(curr.length===1 && moved) view.value={...view.value,x:view.value.x+p.x-old.x,y:view.value.y+p.y-old.y}
}
function up(e) {
  if(!pointers.has(e.pointerId)) return
  pointers.delete(e.pointerId)
  if(!pointers.size) {
    dragging.value=false
    if(!moved && clickCandidate && e.type==='pointerup') {
      const n=byId.value.get(clickCandidate)
      if(n && n.type!=='group') { selected.value=n; copyState.value='' }
      else if(n) focus(n)
    }
    clickCandidate=null
  }
}
function toggleExpanded() { expanded.value=!expanded.value; nextTick(fit) }
function onKey(e) { if(e.key==='Escape'){ if(expanded.value) toggleExpanded(); else selected.value=null } }
const isCode = n => (n.text || '').includes('```')
function cardText(n) { return (n.text || n.file || '').replace(/^\s*```[^\n]*$/gm, '').trim() }
onMounted(async () => {
  window.addEventListener('keydown',onKey)
  try {
    const response=await fetch(withBase(props.src))
    if(!response.ok) throw Error('HTTP '+response.status)
    let canvas
    if (props.src.endsWith('.gz')) {
      if (typeof DecompressionStream === 'undefined' || !response.body) throw Error('Ce navigateur ne prend pas en charge le chargement compressé.')
      const stream = response.body.pipeThrough(new DecompressionStream('gzip'))
      canvas = await new Response(stream).json()
    } else {
      canvas = await response.json()
    }
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
      <div class="map-heading"><span class="map-dot"></span><strong>{{ props.title }}</strong><small v-if="data">{{ data.nodes.length }} éléments · {{ data.edges.length }} liens</small></div>
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
      <select v-if="groups.length" aria-label="Aller à une branche" @change="jumpGroup"><option value="">Aller à une branche</option><option v-for="g in groups" :key="g.id" :value="g.id">{{ g.label }}</option></select>
    </div>
    <div v-if="error" class="map-message" role="alert">{{ error }}</div>
    <div v-else-if="!data" class="map-message">Chargement du Canvas…</div>
    <div v-else class="map-stage">
      <svg ref="svg" class="map-svg" :class="{ dragging }" aria-label="Mindmap interactive" @wheel.prevent="wheel" @contextmenu.prevent @pointerdown="down" @pointermove="move" @pointerup="up" @pointercancel="up" @lostpointercapture="up">
        <defs><marker id="ad-map-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M 0 0 L 8 4 L 0 8 z" fill="#9a84b8"/></marker><marker id="ad-map-arrow-start" markerWidth="8" markerHeight="8" refX="1" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M 8 0 L 0 4 L 8 8 z" fill="#9a84b8"/></marker></defs>
        <g :transform="transform">
          <g v-for="g in groups" :key="g.id">
            <rect :x="g.x" :y="g.y" :width="g.width" :height="g.height" rx="20" :fill="color(g.color)" fill-opacity=".075" :stroke="color(g.color)" stroke-opacity=".8" stroke-width="5" pointer-events="none"/>
            <foreignObject :x="g.x+12" :y="g.y-44" :width="Math.max(g.width,300)" height="62" :data-node="g.id">
              <div xmlns="http://www.w3.org/1999/xhtml" class="map-group-heading">
                <div class="map-group-label" :style="{ color: color(g.color,'#c4a6f5') }" v-text="g.label"></div>
                <div v-if="g.description" class="map-group-description" v-text="g.description"></div>
              </div>
            </foreignObject>
          </g>
          <g v-for="e in edges" :key="e.id" pointer-events="none">
            <path :d="e.path" fill="none" :stroke="color(e.color,'#86769b')" stroke-width="3" stroke-opacity=".72" :marker-end="e.toEnd === 'none' ? undefined : 'url(#ad-map-arrow)'" :marker-start="e.fromEnd === 'arrow' ? 'url(#ad-map-arrow-start)' : undefined"/>
            <text v-if="e.label" :x="e.mx" :y="e.my-8" class="map-edge-label" text-anchor="middle">{{ e.label }}</text>
          </g>
          <g v-for="n in nodes" :key="n.id" :data-node="n.id">
            <rect :x="n.x" :y="n.y" :width="n.width" :height="n.height" rx="9" pointer-events="all" fill="#181320" :stroke="selected?.id===n.id ? '#c4a7ff' : matchIds.has(n.id) ? '#e6caff' : color(n.color,'#4d3c63')" :stroke-width="selected?.id===n.id || matchIds.has(n.id) ? 5 : 2.5"/>
            <foreignObject :x="n.x+5" :y="n.y+3" :width="Math.max(1,n.width-10)" :height="Math.max(1,n.height-6)">
              <div xmlns="http://www.w3.org/1999/xhtml" class="map-node-text" :class="{ 'map-code': isCode(n) }" :style="{ color: n.color ? color(n.color,'#f1eafc') : '#e8def4' }" v-text="cardText(n)"></div>
            </foreignObject>
          </g>
        </g>
      </svg>
      <div v-if="selected" class="map-inspector" @pointerdown.stop>
        <div class="inspector-header">
          <strong>Carte sélectionnée</strong>
          <div class="inspector-actions">
            <button type="button" class="copy-primary" :disabled="!allCopyText" @click="copyCard(allCopyText, 'all')">{{ copyState === 'all' ? '✓ Copié' : 'Copier' }}</button>
            <button type="button" @click="selected=null" aria-label="Fermer la carte">×</button>
          </div>
        </div>
        <div class="inspector-content">
          <template v-for="(part, i) in cardParts" :key="i">
            <div v-if="part.type === 'code'" class="inspector-code" @click="selectBlock($event.currentTarget.querySelector('textarea'))">
              <div class="inspector-code-bar">
                <span>{{ part.language || 'Code' }}</span>
                <button type="button" @click.stop="copyCard(part.value, 'part-'+i)">{{ copyState === 'part-'+i ? '✓ Copié' : 'Copier' }}</button>
              </div>
              <textarea class="inspector-selectable" :value="part.value" readonly spellcheck="false" :rows="Math.min(14,Math.max(3,part.value.split('\n').length+1))" aria-label="Code sélectionnable" @click.stop="selectBlock($event.currentTarget)" @contextmenu.stop></textarea>
            </div>
            <textarea v-else class="inspector-selectable inspector-prose" :value="part.value" readonly spellcheck="false" :rows="Math.min(12,Math.max(2,part.value.split('\n').length+1))" aria-label="Texte sélectionnable" @click="selectBlock($event.currentTarget)"></textarea>
          </template>
          <div v-if="selected.url || selected.sourceUrl || selected.internalUrl" class="inspector-links">
            <a v-if="selected.url" :href="selected.url" target="_blank" rel="noopener noreferrer">Ouvrir la ressource</a>
            <a v-if="selected.sourceUrl && selected.sourceUrl !== selected.url" :href="selected.sourceUrl" target="_blank" rel="noopener noreferrer">URL d’origine</a>
            <a v-if="selected.internalUrl" :href="withBase(selected.internalUrl)">Voir dans le parcours</a>
          </div>
          <p v-if="selected.statusNote" class="inspector-note">{{ selected.statusNote }}</p>
          <p v-if="copyState === 'failed'" class="copy-feedback" role="status">Copie indisponible. Touche le bloc de texte pour le sélectionner entièrement.</p>
          <span v-else-if="copyState" class="copy-feedback" role="status">Copié dans le presse-papiers.</span>
        </div><a v-if="selected.type === 'file' && selected.file?.endsWith('PowerView Enumeration.canvas')" class="map-file-link" :href="withBase('/oscp/mindmap-powerview.html')">Ouvrir PowerView Enumeration</a>
      </div>
      <span v-if="!selected" class="map-hint">Glisser pour naviguer · Molette / pincement pour zoomer · Toucher un bloc pour sélectionner son texte</span>
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
.map-stage{position:relative;height:clamp(460px,70vh,900px);min-height:460px;overflow:hidden;flex:0 0 auto}
.expanded .map-stage{height:auto;min-height:0;flex:1 1 0}.map-svg{position:absolute;inset:0;display:block;width:100%;height:100%;touch-action:none;cursor:grab;background-color:#100d17;background-image:radial-gradient(#2b2238 1px,transparent 1px);background-size:20px 20px;user-select:none;-webkit-user-select:none;-webkit-touch-callout:none}
.map-svg.dragging{cursor:grabbing}
.map-svg [data-node],.map-svg [data-node] *{user-select:none;-webkit-user-select:none;-webkit-touch-callout:none}
.map-svg .map-node-text{pointer-events:none}
.map-group-heading{display:flex;flex-direction:column;gap:2px;pointer-events:auto}.map-group-label{font:600 23px/1.08 system-ui,sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.map-group-description{font:400 12px/1.15 system-ui,sans-serif;color:#c3b4d3;white-space:normal;max-width:100%;overflow:hidden}
.map-node-text{width:100%;height:100%;box-sizing:border-box;display:flex;align-items:center;justify-content:center;padding:4px;white-space:pre-wrap;overflow-wrap:anywhere;overflow:hidden;text-align:center;font:500 18px/1.18 system-ui,sans-serif}
.map-node-text.map-code{display:block;text-align:left;font:400 15px/1.15 ui-monospace,SFMono-Regular,Consolas,monospace;padding:5px}
.map-edge-label{font:500 16px system-ui,sans-serif;fill:#c4b4d7}
.map-hint{position:absolute;bottom:10px;left:10px;right:10px;font-size:10px;color:#b8a7cf;pointer-events:none;text-shadow:0 1px 3px #000}
.map-inspector{position:absolute;right:12px;top:12px;width:min(400px,calc(100% - 24px));max-height:calc(100% - 55px);overflow:auto;border:1px solid #594077;border-radius:10px;background:#1b1426;box-shadow:0 8px 32px #0008;color:#eee5f9}
.inspector-header{position:sticky;top:0;z-index:1;display:flex;align-items:center;justify-content:space-between;gap:8px;padding:10px 12px;border-bottom:1px solid #3e2c56;font-size:12px;background:#1b1426}
.inspector-actions{display:flex;align-items:center;gap:6px}
.ad-mindmap .copy-primary{background:#62409a;border-color:#a78bfa;font-weight:600;min-height:44px;padding:8px 14px}
.ad-mindmap .copy-primary:hover{background:#7550b6}
.inspector-content{padding:10px;user-select:text;-webkit-user-select:text;touch-action:pan-y}.inspector-links{display:flex;flex-wrap:wrap;gap:8px;padding:0 10px 10px}.inspector-links a{display:inline-flex;align-items:center;border:1px solid #594077;border-radius:6px;padding:7px 10px;color:#d8c5f5;background:#241a32;font-size:11px;text-decoration:none}.inspector-links a:hover{border-color:#a78bfa;background:#352348}.inspector-note{margin:0 10px 12px;padding:8px 10px;border-left:2px solid #a78bfa;color:#c8b9d8;background:#211831;font-size:11px;line-height:1.45}
.inspector-code{cursor:pointer;border:1px solid #4d3967;border-radius:7px;overflow:hidden;background:#100d17;margin:0 0 8px}
.inspector-code-bar{display:flex;justify-content:space-between;align-items:center;min-height:26px;padding:4px 9px;color:#bca8d9;font-size:11px;background:#231a30}
.inspector-code-bar button{padding:8px 12px;min-height:44px;background:#62409a;border-color:#a78bfa}
.inspector-prose{font-size:13px;line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere;padding:5px 4px 10px}
.copy-feedback{display:block;color:#c4b5fd;font-size:11px;margin:4px 0}
.map-inspector .inspector-selectable{display:block;width:100%;box-sizing:border-box;resize:vertical;border:0;outline:none;min-height:54px;max-height:45vh;font:13px/1.6 ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere;margin:0;padding:12px;color:#eee5f9;background:transparent;user-select:text;-webkit-user-select:text;cursor:text}
.map-file-link{display:block;padding:0 14px 14px;color:#c4a6f5}.map-message{padding:30px;color:#c7b5dd;font-size:13px}
@media(max-width:640px){.map-controls{gap:4px}.map-bar,.map-filters{padding:8px}.map-search{gap:5px}.ad-mindmap input{width:160px}.map-stage{height:65vh;min-height:350px}.map-inspector{width:calc(100% - 24px);max-height:85%;top:auto;bottom:8px;max-height:48%}}
/* Keep the desktop viewport independent of SVG intrinsic sizing. */
@media(min-width:641px){
  .map-bar,.map-filters{flex:0 0 auto}
  .map-search{flex:1 1 auto;min-width:0}
  .map-filters select{flex:0 1 260px;min-width:0}
  .map-inspector{max-height:calc(100% - 24px);box-sizing:border-box;overscroll-behavior:contain}
}
@media(max-width:640px){.ad-mindmap:not(.expanded) .map-stage{min-height:350px}.ad-mindmap.expanded .map-stage{min-height:0;height:auto;flex:1 1 0}}
</style>

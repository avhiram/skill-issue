<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
const src = 'https://orange-cyberdefense.github.io/ocd-mindmaps/img/mindmap_ad_dark_classic_2025.03.excalidraw.svg'
const root = ref(null), stage = ref(null), image = ref(null)
const frame = ref(null), textMode = ref(false), loadingText = ref(false), frameDoc = ref(''), selectedText = ref(''), textMessage = ref(''), copied = ref(false)
let frameCleanup = () => {}
const copyField = ref(null)
function selectText(){if(copyField.value){copyField.value.focus({preventScroll:true});copyField.value.select();copyField.value.setSelectionRange(0,copyField.value.value.length)}}
const size = ref({ w: 0, h: 0 }), zoom = ref(1), expanded = ref(false), error = ref(false), dragging = ref(false)
let pendingScroll = null
let scrollRevision = 0
const ready = computed(() => size.value.w > 0 && !error.value)
const scaled = computed(() => ({ width: Math.max(1, Math.round(size.value.w * zoom.value)) + 'px', height: Math.max(1, Math.round(size.value.h * zoom.value)) + 'px' }))
function fit() {
  if (!stage.value || !size.value.w) return
  zoom.value = Math.min(1, Math.max(.001, Math.min((stage.value.clientWidth-16)/size.value.w, (stage.value.clientHeight-16)/size.value.h)))
  queueScroll(0,0)
}
function loaded() {
  if (!image.value?.naturalWidth || !image.value?.naturalHeight) { error.value = true; return }
  size.value = { w: image.value.naturalWidth, h: image.value.naturalHeight }
  fit()
  if (!textMode.value && !loadingText.value) toggleTextMode()
}
// Keep the same map point under the centre of a pinch, even inside the iframe.
function scrollPosition() {
  return pendingScroll || {left:stage.value?.scrollLeft||0,top:stage.value?.scrollTop||0}
}
function queueScroll(left,top) {
  const el=stage.value
  if(!el)return
  const revision=++scrollRevision
  pendingScroll={left:Math.max(0,Math.min(left,Math.max(0,Math.round(size.value.w*zoom.value)-el.clientWidth))),top:Math.max(0,Math.min(top,Math.max(0,Math.round(size.value.h*zoom.value)-el.clientHeight)))}
  nextTick(()=>{
    if(revision!==scrollRevision||stage.value!==el)return
    el.scrollLeft=pendingScroll.left;el.scrollTop=pendingScroll.top
    pendingScroll=null
  })
}
function scale(factor,event) {
  if(!ready.value||!stage.value)return
  const el=stage.value,rect=el.getBoundingClientRect(),pos=scrollPosition()
  const px=event?event.clientX-rect.left:el.clientWidth/2,py=event?event.clientY-rect.top:el.clientHeight/2
  const x=(pos.left+px)/zoom.value,y=(pos.top+py)/zoom.value
  zoom.value=Math.max(.001,Math.min(4,zoom.value*factor))
  queueScroll(x*zoom.value-px,y*zoom.value-py)
}
function makeGestures(getPoint,onTap,captureElement) {
  const pointers=new Map()
  let origin=null,pinch=null,candidate=null,moved=false
  const reset=()=>{
    const p=[...pointers.values()]
    const pos=scrollPosition()
    if(p.length>=2){
      const [a,b]=p,mid={x:(a.x+b.x)/2,y:(a.y+b.y)/2}
      pinch={distance:Math.max(1,Math.hypot(a.x-b.x,a.y-b.y)),zoom:zoom.value,x:(pos.left+mid.x)/zoom.value,y:(pos.top+mid.y)/zoom.value}
      origin=null
    }else{
      pinch=null
      origin=p.length?{...p[0],...pos}:null
    }
  }
  const down=e=>{
    if(!ready.value||!stage.value||(e.pointerType==='mouse'&&e.button!==0))return
    e.preventDefault()
    if(!pointers.size){moved=false;candidate=e.target}
    else{moved=true;candidate=null}
    pointers.set(e.pointerId,getPoint(e))
    reset()
    dragging.value=true
    try{captureElement()?.setPointerCapture?.(e.pointerId)}catch{}
  }
  const move=e=>{
    if(!pointers.has(e.pointerId))return
    e.preventDefault()
    const p=getPoint(e)
    pointers.set(e.pointerId,p)
    if(pointers.size>=2&&pinch){
      const [a,b]=[...pointers.values()],mid={x:(a.x+b.x)/2,y:(a.y+b.y)/2}
      moved=true
      zoom.value=Math.max(.001,Math.min(4,pinch.zoom*Math.max(1,Math.hypot(a.x-b.x,a.y-b.y))/pinch.distance))
      queueScroll(pinch.x*zoom.value-mid.x,pinch.y*zoom.value-mid.y)
    }else if(origin){
      const dx=p.x-origin.x,dy=p.y-origin.y
      if(Math.hypot(dx,dy)>7)moved=true
      if(moved)queueScroll(origin.left-dx,origin.top-dy)
    }
  }
  const up=e=>{
    if(!pointers.has(e.pointerId))return
    pointers.delete(e.pointerId)
    if(pointers.size){moved=true;candidate=null;reset();return}
    if(!moved&&candidate&&e.type==='pointerup')onTap?.(candidate,e)
    origin=null;pinch=null;candidate=null;dragging.value=false
  }
  const clear=()=>{pointers.clear();origin=null;pinch=null;candidate=null;dragging.value=false}
  return {down,move,up,clear}
}
const stagePoint=e=>{const r=stage.value.getBoundingClientRect();return {x:e.clientX-r.left,y:e.clientY-r.top}}
const stageGestures=makeGestures(stagePoint,null,()=>stage.value)
async function toggleTextMode() {
  if (textMode.value) {
    frameCleanup(); stageGestures.clear(); textMode.value=false; selectedText.value=''; copied.value=false
    return
  }
  if (loadingText.value) return
  loadingText.value=true; textMessage.value=''; copied.value=false; selectedText.value=''
  try {
    if (!frameDoc.value) {
      let xml=''
      for (const url of [src, 'https://raw.githubusercontent.com/Orange-Cyberdefense/ocd-mindmaps/main/img/mindmap_ad_dark_classic_2025.03.excalidraw.svg']) {
        try { const r=await fetch(url,{credentials:'omit'}); if(r.ok){xml=await r.text();break} } catch {}
      }
      if (!xml) throw Error('Le SVG ne peut pas être lu depuis ce navigateur.')
      const doc=new DOMParser().parseFromString(xml,'image/svg+xml')
      const svg=doc.documentElement
      if(svg.localName!=='svg'||doc.querySelector('parsererror')) throw Error('Le fichier SVG est invalide.')
      if(!svg.querySelector('text')) throw Error('Aucun texte sélectionnable dans ce SVG.')
      svg.querySelectorAll('script,foreignObject,iframe,object,embed,animate,animateTransform,set').forEach(el=>el.remove())
      for(const el of [svg,...svg.querySelectorAll('*')]) for(const a of [...el.attributes]) {
        if(/^on/i.test(a.name)||(/^(?:xlink:)?href$/i.test(a.name)&&!a.value.startsWith('#')&&!/^data:image\/(?:png|jpeg|webp);base64,/i.test(a.value))) el.removeAttribute(a.name)
      }
      svg.removeAttribute('width'); svg.removeAttribute('height')
      svg.setAttribute('width','100%'); svg.setAttribute('height','100%')
      const markup=new XMLSerializer().serializeToString(svg)
      frameDoc.value='<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data:; font-src data:"><style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#100d17}svg{display:block;width:100%;height:100%;}svg{touch-action:none;user-select:none;-webkit-user-select:none;-webkit-touch-callout:none}svg text,svg tspan{user-select:none!important;-webkit-user-select:none!important;cursor:pointer!important;pointer-events:all!important}</style></head><body>'+markup+'</body></html>'
    }
    stageGestures.clear(); textMode.value=true
  } catch(e) {textMessage.value=e.message+' Le lecteur original reste disponible.'}
  finally {loadingText.value=false}
}
function bindTextFrame() {
  frameCleanup()
  const doc=frame.value?.contentDocument
  if(!doc) {textMessage.value='Sélection indisponible dans ce navigateur.';textMode.value=false;return}
  const textOf = el => {
    const spans=[...el.querySelectorAll(':scope > tspan')]
    if(spans.length>1 && spans.slice(1).some(t=>t.hasAttribute('y')||t.hasAttribute('dy'))) return spans.map(t=>t.textContent||'').join('\n')
    return el.textContent||''
  }
  const textGroups=new Map()
  const svgRoot=doc.querySelector('svg')
  let activeHighlight=null
  // Work in SVG coordinates so hit areas remain correct at every zoom level.
  const inverse=svgRoot.getScreenCTM()?.inverse()
  if(!inverse)return
  const boundsOf=el=>{
    try {
      const b=el.getBBox(), m=inverse.multiply(el.getScreenCTM())
      const pts=[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(m))
      const x=Math.min(...pts.map(p=>p.x)),y=Math.min(...pts.map(p=>p.y))
      return {x,y,w:Math.max(...pts.map(p=>p.x))-x,h:Math.max(...pts.map(p=>p.y))-y}
    }catch{return null}
  }
  const contains=(outer,inner,pad=2)=>inner.x>=outer.x-pad&&inner.y>=outer.y-pad&&inner.x+inner.w<=outer.x+outer.w+pad&&inner.y+inner.h<=outer.y+outer.h+pad
  const area=b=>b.w*b.h
  for(const el of svgRoot.querySelectorAll('text')) {
    const owner=el.parentElement?.localName==='g'?el.parentElement:el
    if(!textGroups.has(owner))textGroups.set(owner,[])
    textGroups.get(owner).push(el)
  }
  const groups=[]
  for(const [owner,lines] of textGroups) {
    const boxes=lines.map(boundsOf).filter(Boolean)
    if(!boxes.length)continue
    const x=Math.min(...boxes.map(b=>b.x)),y=Math.min(...boxes.map(b=>b.y))
    const box={x,y,w:Math.max(...boxes.map(b=>b.x+b.w))-x,h:Math.max(...boxes.map(b=>b.y+b.h))-y}
    if(box.w>0&&box.h>0)groups.push({owner,lines,box})
  }
  // Excalidraw draws borders separately from the text. Match compact
  // containing shapes rather than relying on a touch hitting a letter.
  const shapes=[...svgRoot.querySelectorAll('rect,path,polygon')].map(boundsOf).filter(b=>b&&b.w>8&&b.h>8)
  const blocks=new Map()
  for(const group of groups) {
    const b=group.box
    const shape=shapes.filter(r=>contains(r,b)&&r.w<=b.w+160&&r.h<=b.h+100&&area(r)<=area(b)*12).sort((a,b)=>area(a)-area(b))[0]
    const key=shape||group
    if(!blocks.has(key))blocks.set(key,{box:shape||b,groups:[]})
    blocks.get(key).groups.push(group)
  }
  const entries=[...blocks.values()]
  const byText=new Map()
  for(const block of entries)for(const group of block.groups)for(const line of group.lines)byText.set(line,block)
  const pick=async (target,clientX,clientY)=>{
    const matrix=svgRoot.getScreenCTM()
    if(!matrix)return
    const pt=new DOMPoint(clientX,clientY).matrixTransform(matrix.inverse())
    let block=byText.get(target.closest?.('text'))
    if(!block)block=entries.filter(({box:b})=>pt.x>=b.x-3&&pt.x<=b.x+b.w+3&&pt.y>=b.y-3&&pt.y<=b.y+b.h+3).sort((a,b)=>area(a.box)-area(b.box))[0]
    if(!block)return
    selectedText.value=block.groups.flatMap(g=>g.lines).map(textOf).join('\n')
    copied.value=false
    activeHighlight?.remove()
    const b=block.box
    activeHighlight=doc.createElementNS('http://www.w3.org/2000/svg','rect')
    for(const [k,v] of Object.entries({x:b.x-2,y:b.y-2,width:b.w+4,height:b.h+4,rx:2,fill:'none',stroke:'#c4a7ff','stroke-width':2,'vector-effect':'non-scaling-stroke','pointer-events':'none'}))activeHighlight.setAttribute(k,String(v))
    svgRoot.appendChild(activeHighlight)
    await nextTick()
  }
  const framePoint=e=>{
    const f=frame.value.getBoundingClientRect(),r=stage.value.getBoundingClientRect()
    return {x:f.left+e.clientX-r.left,y:f.top+e.clientY-r.top}
  }
  const gestures=makeGestures(framePoint,(target,e)=>pick(target,e.clientX,e.clientY),()=>svgRoot)
  const {down,move,up}=gestures
  const wheel=e=>{
    e.preventDefault()
    if(e.deltaY){const f=frame.value.getBoundingClientRect();scale(Math.exp(-e.deltaY*.0015),{clientX:f.left+e.clientX,clientY:f.top+e.clientY})}
    else if(e.deltaX){const p=scrollPosition();queueScroll(p.left+e.deltaX,p.top)}
  }
  const context=e=>e.preventDefault()
  const listeners=[['contextmenu',context],['pointerdown',down],['pointermove',move],['pointerup',up],['pointercancel',up],['lostpointercapture',up],['wheel',wheel]]
  for(const [name,fn] of listeners)doc.addEventListener(name,fn,{passive:false})
  frameCleanup=()=>{for(const [name,fn] of listeners)doc.removeEventListener(name,fn);gestures.clear();activeHighlight?.remove()}
}
async function copyText() {
  if(!selectedText.value)return
  try { await navigator.clipboard.writeText(selectedText.value);copied.value=true; textMessage.value='' }
  catch { selectText();try{copied.value=document.execCommand('copy')}catch{} if(!copied.value)textMessage.value='Utilise Copier dans le menu de sélection.' }
}
function wheel(e){e.preventDefault();if(e.deltaY)scale(Math.exp(-e.deltaY*.0015),e);else if(e.deltaX){const p=scrollPosition();queueScroll(p.left+e.deltaX,p.top)}}
function down(e){if(!textMode.value)stageGestures.down(e)}
function move(e){if(!textMode.value)stageGestures.move(e)}
function up(e){stageGestures.up(e)}
function toggle(){expanded.value=!expanded.value;nextTick(fit)}
function key(e){if(e.key==='Escape'&&expanded.value)toggle()}
onMounted(()=>window.addEventListener('keydown',key))
onBeforeUnmount(()=>{frameCleanup();stageGestures.clear();window.removeEventListener('keydown',key)})
</script>

<template>
  <section ref="root" class="ocd-viewer" :class="{expanded}">
    <div class="ocd-toolbar">
      <strong>AD · Mars 2025</strong>
      <div class="ocd-controls">
        <button type="button" :disabled="!ready" aria-label="Dézoomer" @click="scale(1/1.5)">−</button>
        <span>{{ (zoom*100).toFixed(zoom<.1?1:0) }} %</span>
        <button type="button" :disabled="!ready" aria-label="Zoomer" @click="scale(1.5)">+</button>
        <button type="button" :disabled="!ready" @click="fit">Vue globale</button>
        <button type="button" @click="toggle">{{ expanded?'Quitter plein écran':'Plein écran' }}</button>
        <button type="button" :disabled="!ready||loadingText" @click="toggleTextMode">{{ loadingText ? 'Chargement…' : textMode ? 'Vue SVG' : 'Texte interactif' }}</button>
        <a :href="src" target="_blank" rel="noopener noreferrer">SVG original</a>
      </div>
    </div>
    <div v-if="error" class="ocd-status">Le SVG distant n'a pas pu être chargé. <a :href="src" target="_blank" rel="noopener noreferrer">Ouvrir le fichier officiel</a>.</div>
    <div v-else ref="stage" class="ocd-stage" :class="{dragging}" @wheel="wheel" @pointerdown="down" @pointermove="move" @pointerup="up" @pointercancel="up" @lostpointercapture="up">
      <p v-if="!ready" class="ocd-status">Chargement du SVG officiel…</p>
      <iframe v-if="textMode" ref="frame" :srcdoc="frameDoc" :style="scaled" sandbox="allow-same-origin" class="ocd-text-frame" title="SVG avec texte sélectionnable" @load="bindTextFrame"></iframe>
      <img v-show="!textMode" ref="image" :src="src" alt="Mind map Active Directory Orange Cyberdefense, mars 2025" :style="ready ? scaled : {width:'1px',height:'1px',opacity:0}" draggable="false" @load="loaded" @error="error=true">
    </div>
    <div v-if="textMode && selectedText" class="ocd-copy">
      <div class="ocd-copy-header"><button type="button" @click="selectText">Tout sélectionner</button><button type="button" class="ocd-copy-main" @click="copyText">{{ copied ? '✓ Copié' : 'Copier' }}</button><button type="button" aria-label="Fermer" @click="selectedText='';copied=false">×</button></div>
      <textarea ref="copyField" :value="selectedText" readonly spellcheck="false" :rows="Math.min(8,Math.max(3,selectedText.split('\n').length+1))" aria-label="Texte sélectionné" @click="selectText"></textarea>
    </div>
    <div v-if="textMessage" class="ocd-status" role="status">{{ textMessage }}</div>
    <div class="ocd-hint">{{ textMode ? 'Touche un bloc pour sélectionner son texte · Molette ou pincement pour zoomer' : 'Glisser pour naviguer · Molette ou boutons + et − pour zoomer · Pincement sur écran tactile' }}</div>
  </section>
</template>

<style scoped>
:global(.VPDoc:has(.ocd-viewer) .content-container){max-width:none!important}
.ocd-viewer{display:flex;flex-direction:column;border:1px solid #503b6b;border-radius:12px;overflow:hidden;background:#100d17;color:#eee5f9;margin:24px 0}
.ocd-viewer.expanded{position:fixed;inset:0;z-index:9999;margin:0;border-radius:0}
.ocd-toolbar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:12px;background:#1b1426;border-bottom:1px solid #503b6b}
.ocd-controls{display:flex;gap:7px;flex-wrap:wrap;align-items:center;font-size:12px}
.ocd-controls button,.ocd-controls a{border:1px solid #503b6b;border-radius:6px;padding:8px 10px;background:#211831;color:#eee5f9;font:inherit;cursor:pointer;text-decoration:none}
.ocd-controls button:disabled{opacity:.45;cursor:default}
.ocd-controls button:hover,.ocd-controls a:hover{border-color:#a78bfa}
.ocd-stage{height:clamp(420px,70vh,900px);overflow:auto;overscroll-behavior:contain;cursor:grab;touch-action:none;min-height:0}
.expanded .ocd-stage{flex:1;height:auto}
.ocd-stage.dragging{cursor:grabbing}
.ocd-stage img{display:block;max-width:none!important;max-height:none!important;margin:0!important;user-select:none;pointer-events:none}
.ocd-text-frame{display:block;border:0;max-width:none!important;background:#100d17;touch-action:none}
.ocd-copy{position:sticky;bottom:0;z-index:3;flex-shrink:0;padding:10px 12px;border-top:1px solid #503b6b;background:#1b1426}
.ocd-copy-header{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:12px}
.ocd-copy-header button{background:#62409a;border:1px solid #a78bfa;color:#fff;border-radius:6px;padding:8px 14px;cursor:pointer}
.ocd-copy-header .ocd-copy-main{flex:1;min-height:44px;font-weight:600}.ocd-copy-header button:disabled{opacity:.4;cursor:default}
.ocd-copy textarea{display:block;width:100%;resize:vertical;min-height:65px;max-height:30vh;margin-top:8px;padding:8px;border:1px solid #503b6b;border-radius:6px;background:#100d17;color:#eee5f9;font:13px/1.5 ui-monospace,monospace;user-select:text}
.ocd-status,.ocd-hint{padding:10px 12px;color:#c4b5d9;font-size:12px}
@media(max-width:640px){.ocd-stage{height:65vh;min-height:350px}.ocd-toolbar{padding:8px}}
</style>

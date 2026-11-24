<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
const src = 'https://orange-cyberdefense.github.io/ocd-mindmaps/img/mindmap_ad_dark_classic_2025.03.excalidraw.svg'
const root = ref(null), stage = ref(null), image = ref(null)
const frame = ref(null), textMode = ref(false), loadingText = ref(false), frameDoc = ref(''), selectedText = ref(''), textMessage = ref(''), copied = ref(false)
let frameCleanup = () => {}
const copyField = ref(null)
function selectText(){if(copyField.value){copyField.value.focus({preventScroll:true});copyField.value.select();copyField.value.setSelectionRange(0,copyField.value.value.length)}}
const size = ref({ w: 0, h: 0 }), zoom = ref(1), expanded = ref(false), error = ref(false), dragging = ref(false)
let drag = null
const ready = computed(() => size.value.w > 0 && !error.value)
const scaled = computed(() => ({ width: Math.max(1, Math.round(size.value.w * zoom.value)) + 'px', height: Math.max(1, Math.round(size.value.h * zoom.value)) + 'px' }))
function fit() {
  if (!stage.value || !size.value.w) return
  zoom.value = Math.min(1, Math.max(.001, Math.min((stage.value.clientWidth-16)/size.value.w, (stage.value.clientHeight-16)/size.value.h)))
  nextTick(() => { if(stage.value) {stage.value.scrollLeft=0;stage.value.scrollTop=0} })
}
function loaded() {
  if (!image.value?.naturalWidth || !image.value?.naturalHeight) { error.value = true; return }
  size.value = { w: image.value.naturalWidth, h: image.value.naturalHeight }
  fit()
  if (!textMode.value && !loadingText.value) toggleTextMode()
}
function scale(factor, event) {
  if (!ready.value || !stage.value) return
  const el=stage.value, rect=el.getBoundingClientRect()
  const px=event ? event.clientX-rect.left : el.clientWidth/2, py=event ? event.clientY-rect.top : el.clientHeight/2
  const x=(el.scrollLeft+px)/zoom.value, y=(el.scrollTop+py)/zoom.value
  zoom.value=Math.max(.001,Math.min(4,zoom.value*factor))
  nextTick(()=>{if(stage.value){el.scrollLeft=x*zoom.value-px;el.scrollTop=y*zoom.value-py}})
}
async function toggleTextMode() {
  if (textMode.value) {
    frameCleanup(); textMode.value=false; selectedText.value=''; copied.value=false
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
      frameDoc.value='<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data:; font-src data:"><style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#100d17}svg{display:block;width:100%;height:100%;}svg{touch-action:none}svg text,svg tspan{user-select:none!important;-webkit-user-select:none!important;cursor:pointer!important;pointer-events:all!important}</style></head><body>'+markup+'</body></html>'
    }
    textMode.value=true
  } catch(e) {textMessage.value=e.message+' Le lecteur original reste disponible.'}
  finally {loadingText.value=false}
}
function bindTextFrame() {
  frameCleanup()
  const doc=frame.value?.contentDocument
  if(!doc) {textMessage.value='Sélection indisponible dans ce navigateur.';textMode.value=false;return}
  let gesture=null
  const textOf = el => {
    const spans=[...el.querySelectorAll(':scope > tspan')]
    if(spans.length>1 && spans.slice(1).some(t=>t.hasAttribute('y')||t.hasAttribute('dy'))) return spans.map(t=>t.textContent||'').join('\n')
    return el.textContent||''
  }
  const hitGroups=new Map()
  const textGroups=new Map()
  const svgRoot=doc.querySelector('svg')
  // Use the original SVG's text groups as the selection unit.
  for(const el of svgRoot?.querySelectorAll('text') || []) {
    const group=el.parentElement
    const owner=group?.localName==='g'?group:el
    if(!textGroups.has(owner))textGroups.set(owner,[])
    textGroups.get(owner).push(el)
  }
  for(const [owner,lines] of textGroups) {
    if(owner.localName!=='g')continue
    try {
      const bounds=lines.map(el=>el.getBBox())
      const left=Math.min(...bounds.map(b=>b.x)),top=Math.min(...bounds.map(b=>b.y))
      const right=Math.max(...bounds.map(b=>b.x+b.width)),bottom=Math.max(...bounds.map(b=>b.y+b.height))
      if(![left,top,right,bottom].every(Number.isFinite)||right<=left||bottom<=top)continue
      const hit=doc.createElementNS('http://www.w3.org/2000/svg','rect')
      const pad=3
      hit.setAttribute('x',String(left-pad));hit.setAttribute('y',String(top-pad))
      hit.setAttribute('width',String(right-left+2*pad));hit.setAttribute('height',String(bottom-top+2*pad))
      hit.setAttribute('fill','transparent');hit.setAttribute('pointer-events','all');hit.setAttribute('style','cursor:pointer')
      owner.insertBefore(hit,owner.firstChild)
      hitGroups.set(hit,owner)
    }catch{}
  }
  const pick = async target => {
    if(!target)return
    const el=target.closest?.('text')
    const owner=hitGroups.get(target)||(el?.parentElement?.localName==='g'?el.parentElement:el)
    const lines=textGroups.get(owner)
    if(!lines?.length)return
    selectedText.value=lines.map(textOf).join('\n')
    copied.value=false
    await nextTick()
    selectText()
  }
  const down=e=>{
    if(e.button!==0&&e.pointerType==='mouse')return
    gesture={id:e.pointerId,x:e.clientX,y:e.clientY,screenX:e.screenX,screenY:e.screenY,left:stage.value.scrollLeft,top:stage.value.scrollTop,target:e.target,moved:false}
    e.target.setPointerCapture?.(e.pointerId)
  }
  const move=e=>{
    if(!gesture||gesture.id!==e.pointerId)return
    const dx=e.screenX-gesture.screenX,dy=e.screenY-gesture.screenY
    if(Math.hypot(dx,dy)>7)gesture.moved=true
    if(gesture.moved){stage.value.scrollLeft=gesture.left-dx;stage.value.scrollTop=gesture.top-dy}
  }
  const up=e=>{
    if(!gesture||gesture.id!==e.pointerId)return
    if(!gesture.moved&&e.type==='pointerup')pick(gesture.target)
    gesture=null
  }
  const wheel=e=>{
    e.preventDefault()
    if(e.ctrlKey||e.metaKey)scale(Math.exp(-e.deltaY*.003))
    else {stage.value.scrollLeft+=e.deltaX;stage.value.scrollTop+=e.deltaY}
  }
  const listeners=[['pointerdown',down],['pointermove',move],['pointerup',up],['pointercancel',up],['wheel',wheel]]
  for(const [name,fn] of listeners)doc.addEventListener(name,fn,{passive:false})
  frameCleanup=()=>{for(const [name,fn] of listeners)doc.removeEventListener(name,fn);for(const hit of hitGroups.keys())hit.remove()}
}
async function copyText() {
  if(!selectedText.value)return
  try { await navigator.clipboard.writeText(selectedText.value);copied.value=true; textMessage.value='' }
  catch { selectText();try{copied.value=document.execCommand('copy')}catch{} if(!copied.value)textMessage.value='Utilise Copier dans le menu de sélection.' }
}
function wheel(e){if(e.ctrlKey || e.metaKey){e.preventDefault();scale(Math.exp(-e.deltaY*.003),e)}}
function down(e){if(textMode.value||e.pointerType!=='mouse'||e.button!==0)return;drag={x:e.clientX,y:e.clientY,left:stage.value.scrollLeft,top:stage.value.scrollTop};dragging.value=true;stage.value.setPointerCapture?.(e.pointerId)}
function move(e){if(!drag)return;stage.value.scrollLeft=drag.left-(e.clientX-drag.x);stage.value.scrollTop=drag.top-(e.clientY-drag.y)}
function up(){drag=null;dragging.value=false}
function toggle(){expanded.value=!expanded.value;nextTick(fit)}
function key(e){if(e.key==='Escape'&&expanded.value)toggle()}
onMounted(()=>window.addEventListener('keydown',key))
onBeforeUnmount(()=>{frameCleanup();window.removeEventListener('keydown',key)})
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
      <textarea ref="copyField" :value="selectedText" readonly spellcheck="false" :rows="Math.min(8,Math.max(3,selectedText.split('\n').length+1))" aria-label="Texte sélectionné" @click="selectText" @focus="selectText"></textarea>
    </div>
    <div v-if="textMessage" class="ocd-status" role="status">{{ textMessage }}</div>
    <div class="ocd-hint">{{ textMode ? 'Touche un texte pour le copier.' : 'Glisser pour naviguer · Boutons + et − pour zoomer · Ctrl + molette sur ordinateur' }}</div>
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
.ocd-stage{height:clamp(420px,70vh,900px);overflow:auto;overscroll-behavior:contain;cursor:grab;touch-action:pan-x pan-y;min-height:0}
.expanded .ocd-stage{flex:1;height:auto}
.ocd-stage.dragging{cursor:grabbing}
.ocd-stage img{display:block;max-width:none!important;max-height:none!important;margin:0!important;user-select:none;pointer-events:none}
.ocd-text-frame{display:block;border:0;max-width:none!important;background:#100d17}
.ocd-copy{flex-shrink:0;padding:10px 12px;border-top:1px solid #503b6b;background:#1b1426}
.ocd-copy-header{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:12px}
.ocd-copy-header button{background:#62409a;border:1px solid #a78bfa;color:#fff;border-radius:6px;padding:8px 14px;cursor:pointer}
.ocd-copy-header .ocd-copy-main{flex:1;min-height:44px;font-weight:600}.ocd-copy-header button:disabled{opacity:.4;cursor:default}
.ocd-copy textarea{display:block;width:100%;resize:vertical;min-height:65px;max-height:30vh;margin-top:8px;padding:8px;border:1px solid #503b6b;border-radius:6px;background:#100d17;color:#eee5f9;font:13px/1.5 ui-monospace,monospace;user-select:text}
.ocd-status,.ocd-hint{padding:10px 12px;color:#c4b5d9;font-size:12px}
@media(max-width:640px){.ocd-stage{height:65vh;min-height:350px}.ocd-toolbar{padding:8px}}
</style>

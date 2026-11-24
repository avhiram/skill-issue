<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
const src = 'https://orange-cyberdefense.github.io/ocd-mindmaps/img/mindmap_ad_dark_classic_2025.03.excalidraw.svg'
const root = ref(null), stage = ref(null), image = ref(null)
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
}
function scale(factor, event) {
  if (!ready.value || !stage.value) return
  const el=stage.value, rect=el.getBoundingClientRect()
  const px=event ? event.clientX-rect.left : el.clientWidth/2, py=event ? event.clientY-rect.top : el.clientHeight/2
  const x=(el.scrollLeft+px)/zoom.value, y=(el.scrollTop+py)/zoom.value
  zoom.value=Math.max(.001,Math.min(4,zoom.value*factor))
  nextTick(()=>{if(stage.value){el.scrollLeft=x*zoom.value-px;el.scrollTop=y*zoom.value-py}})
}
function wheel(e){if(e.ctrlKey || e.metaKey){e.preventDefault();scale(Math.exp(-e.deltaY*.003),e)}}
function down(e){if(e.pointerType!=='mouse'||e.button!==0)return;drag={x:e.clientX,y:e.clientY,left:stage.value.scrollLeft,top:stage.value.scrollTop};dragging.value=true;stage.value.setPointerCapture?.(e.pointerId)}
function move(e){if(!drag)return;stage.value.scrollLeft=drag.left-(e.clientX-drag.x);stage.value.scrollTop=drag.top-(e.clientY-drag.y)}
function up(){drag=null;dragging.value=false}
function toggle(){expanded.value=!expanded.value;nextTick(fit)}
function key(e){if(e.key==='Escape'&&expanded.value)toggle()}
onMounted(()=>window.addEventListener('keydown',key))
onBeforeUnmount(()=>window.removeEventListener('keydown',key))
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
        <a :href="src" target="_blank" rel="noopener noreferrer">SVG original</a>
      </div>
    </div>
    <div v-if="error" class="ocd-status">Le SVG distant n'a pas pu être chargé. <a :href="src" target="_blank" rel="noopener noreferrer">Ouvrir le fichier officiel</a>.</div>
    <div v-else ref="stage" class="ocd-stage" :class="{dragging}" @wheel="wheel" @pointerdown="down" @pointermove="move" @pointerup="up" @pointercancel="up" @lostpointercapture="up">
      <p v-if="!ready" class="ocd-status">Chargement du SVG officiel…</p>
      <img ref="image" :src="src" alt="Mind map Active Directory Orange Cyberdefense, mars 2025" :style="ready ? scaled : {width:'1px',height:'1px',opacity:0}" draggable="false" @load="loaded" @error="error=true">
    </div>
    <div class="ocd-hint">Glisser pour naviguer · Boutons + et − pour zoomer · Ctrl + molette sur ordinateur</div>
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
.ocd-status,.ocd-hint{padding:10px 12px;color:#c4b5d9;font-size:12px}
@media(max-width:640px){.ocd-stage{height:65vh;min-height:350px}.ocd-toolbar{padding:8px}}
</style>

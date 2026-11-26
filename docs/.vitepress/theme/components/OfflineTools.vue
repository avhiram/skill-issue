<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { withBase } from 'vitepress'
const supported=ref(false),busy=ref(false),message=ref(''),done=ref(0),total=ref(0)
const key='skill-issue-offline-v1'
const revision=ref('')
onMounted(()=>{
  supported.value=!!(window.isSecureContext&&'serviceWorker' in navigator&&'caches' in window)
  revision.value=document.querySelector<HTMLMetaElement>('meta[name="skill-issue-build"]')?.content.slice(0,8)||''
})
async function save(){
  if(busy.value||!supported.value)return
  busy.value=true;done.value=0;total.value=0;message.value='Préparation…'
  try{
    await navigator.serviceWorker.register(withBase('/offline-sw.js'),{scope:withBase('/'),updateViaCache:'none'})
    await navigator.serviceWorker.ready
    const response=await fetch(withBase('/offline-index.json'),{cache:'no-store'})
    if(!response.ok)throw Error('index')
    const manifest=await response.json() as {revision:string;files:string[]}
    if(!Array.isArray(manifest.files)||!manifest.files.length)throw Error('empty')
    const base=new URL(withBase('/'),window.location.origin)
    const cache=await caches.open(key)
    total.value=manifest.files.length
    let next=0,failed=0
    async function download(){
      while(next<manifest.files.length){
        const file=manifest.files[next++]
        try{
          const url=new URL(file,base)
          if(url.origin!==base.origin||!url.pathname.startsWith(base.pathname))throw Error('path')
          const r=await fetch(url.href,{cache:'reload'})
          if(!r.ok)throw Error('fetch')
          if(file.endsWith('.html')&&manifest.revision!=='local'){
            const html=await r.clone().text()
            if(!html.includes('content="'+manifest.revision+'"'))throw Error('stale')
          }
          await cache.put(url.href,r)
        }catch{failed++}
        done.value++
      }
    }
    await Promise.all(Array.from({length:4},download))
    message.value=failed?('Copie partielle : '+failed+' fichier(s) indisponible(s). Relancer pour compléter.'):('Documentation enregistrée · '+manifest.revision.slice(0,8))
  }catch{message.value='Téléchargement indisponible. Réessaie avec une connexion Internet.'}
  finally{busy.value=false}
}
async function clear(){
  if(busy.value)return
  try{const reg=await navigator.serviceWorker.getRegistration(withBase('/'));if(reg?.scope===new URL(withBase('/'),location.origin).href&&reg.active?.scriptURL===new URL(withBase('/offline-sw.js'),location.origin).href)await reg.unregister();await caches.delete(key);message.value='Copie locale supprimée. Ferme puis rouvre le site.'}
  catch{message.value='Impossible de supprimer la copie locale.'}
}
</script>
<template>
  <details class="skill-offline">
    <summary>Hors ligne <small v-if="revision">· {{ revision }}</small></summary>
    <div class="skill-offline-body">
      <p>Enregistre les fiches et la recherche sur cet appareil. Les vidéos, images lourdes et sites externes peuvent rester indisponibles.</p>
      <button type="button" :disabled="busy||!supported" @click="save">{{busy?'Téléchargement…':'Télécharger / actualiser'}}</button>
      <progress v-if="busy&&total" :value="done" :max="total" />
      <small v-if="busy&&total">{{done}} / {{total}}</small>
      <small v-if="message" role="status">{{message}}</small>
      <small v-if="!supported">Indisponible dans ce navigateur.</small>
      <button type="button" :disabled="busy||!supported" @click="clear">Supprimer la copie locale</button>
    </div>
  </details>
</template>
<style scoped>
.skill-offline{border:1px solid #3a2b4b;border-radius:8px;margin:10px 0;color:#dac6f5;font-size:13px}
.skill-offline summary{cursor:pointer;padding:11px;font-weight:600}
.skill-offline-body{display:grid;gap:8px;padding:0 11px 11px}
.skill-offline-body p{font-size:12px;line-height:1.5;color:#b6aec5;margin:0}
.skill-offline-body button{border:1px solid #49345e;border-radius:7px;background:#21172e;color:#e2d2f4;min-height:44px;padding:6px}
.skill-offline-body button:disabled{opacity:.55;cursor:not-allowed}
.skill-offline-body small{margin:0;color:#c9b5df;overflow-wrap:anywhere}
.skill-offline-body progress{width:100%;height:8px;accent-color:#b39aff}
</style>

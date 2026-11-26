<script setup lang="ts">
import {computed,ref,watch} from 'vue'
import {useLabVariables,type LabKey} from '../labVariables'
const props=defineProps<{source:string}>()
const {validated}=useLabVariables()
const required=computed(()=>[...new Set([...props.source.matchAll(/\$(TCP_PORTS|UDP_PORTS|SUBNET|IP)\b/g)].map(m=>m[1] as LabKey))])
const complete=computed(()=>required.value.every(k=>!!validated.value[k]))
const command=computed(()=>props.source.replace(/\$(TCP_PORTS|UDP_PORTS|SUBNET|IP)\b/g,(original,key:LabKey)=>validated.value[key]||original))
const status=ref('')
watch(command,()=>status.value='')
async function copy(){
  try {await navigator.clipboard.writeText(complete.value?command.value:props.source);status.value='Copié'}
  catch {status.value='Sélectionner le texte pour copier'}
}
</script>
<template>
  <div class="lab-command">
    <div class="lab-command-bar"><span>Bash</span><button type="button" @click="copy">{{ status || (complete ? 'Copier' : 'Copier le modèle') }}</button></div>
    <pre><code>{{ command }}</code></pre>
  </div>
</template>
<style scoped>
.lab-command{background:var(--vp-code-block-bg);border-radius:8px;margin:16px 0;overflow:hidden}
.lab-command-bar{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:7px 12px;color:var(--vp-c-text-2);font-size:12px}
.lab-command-bar button{border:1px solid #4a385f;border-radius:6px;padding:6px 10px;color:#dfcaf9;min-height:40px}
.lab-command pre{margin:0;padding:12px 16px 16px;overflow-x:auto;white-space:pre}
.lab-command pre code{background:transparent;padding:0;font-family:var(--vp-font-family-mono);font-size:var(--vp-code-font-size);color:var(--vp-c-text-1);white-space:inherit}
</style>

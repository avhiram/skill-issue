<script setup lang="ts">
import { useLabVariables, type LabKey } from '../labVariables'
const {values,validated,automaticSubnet,set,reset}=useLabVariables()
const prefixes=Array.from({length:33},(_,i)=>32-i)
const fields: {key:LabKey;label:string;placeholder:string}[] = [
  {key:'TCP_PORTS',label:'Ports TCP',placeholder:'22,80,445'},
  {key:'UDP_PORTS',label:'Ports UDP',placeholder:'53,161'}
]
</script>
<template>
  <details class="lab-vars">
    <summary>Variables du laboratoire <span>{{ Object.values(validated).filter(Boolean).length }}/4</span></summary>
    <div class="lab-vars-body">
      <label>
        <span>IP de la machine</span>
        <input type="text" :value="values.IP" placeholder="192.168.1.10" autocomplete="off" spellcheck="false" :aria-invalid="!!values.IP.trim() && !validated.IP" @input="set('IP',($event.target as HTMLInputElement).value)">
        <small v-if="values.IP.trim() && !validated.IP">IPv4 invalide</small>
      </label>
      <label>
        <span>Masque réseau (CIDR)</span>
        <select :value="values.PREFIX" @change="set('PREFIX',($event.target as HTMLSelectElement).value)">
          <option value="">Choisir le préfixe</option>
          <option v-for="prefix in prefixes" :key="prefix" :value="String(prefix)">/{{ prefix }}</option>
        </select>
        <small v-if="!values.PREFIX">Choisir le masque réel du laboratoire.</small>
      </label>
      <label class="lab-subnet">
        <span>Réseau CIDR <small v-if="automaticSubnet && !values.SUBNET.trim()">· Calcul automatique</small></span>
        <input type="text" :value="values.SUBNET" :placeholder="automaticSubnet || '192.168.1.0/24'" autocomplete="off" spellcheck="false" :aria-invalid="!!values.SUBNET.trim() && !validated.SUBNET" @input="set('SUBNET',($event.target as HTMLInputElement).value)">
        <small v-if="values.SUBNET.trim() && !validated.SUBNET">CIDR invalide</small>
        <small v-else-if="validated.SUBNET">Réseau utilisé : {{ validated.SUBNET }}</small>
        <small v-else>Saisir le réseau ou choisir le masque de l’IP.</small>
        <button v-if="values.SUBNET.trim()" type="button" class="lab-auto" @click="set('SUBNET','')">Utiliser le calcul automatique</button>
      </label>
      <label v-for="field in fields" :key="field.key">
        <span>{{ field.label }}</span>
        <input type="text" :value="values[field.key]" :placeholder="field.placeholder" autocomplete="off" spellcheck="false" :aria-invalid="!!values[field.key].trim() && !validated[field.key]" @input="set(field.key,($event.target as HTMLInputElement).value)">
        <small v-if="values[field.key].trim() && !validated[field.key]">Format invalide</small>
      </label>
      <div class="lab-vars-footer"><small>Valeurs conservées dans cet onglet.</small><button type="button" @click="reset">Réinitialiser</button></div>
    </div>
  </details>
</template>
<style scoped>
.lab-vars{border:1px solid #433251;border-radius:9px;background:#191320;margin:16px 0;padding:0}
.lab-vars summary{cursor:pointer;list-style:none;display:flex;align-items:center;justify-content:space-between;gap:8px;padding:12px 14px;color:#dac5f8;font-weight:650;font-size:14px;min-height:44px}
.lab-vars summary::-webkit-details-marker{display:none}
.lab-vars summary span{font-size:12px;color:#ab95c8}
.lab-vars-body{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;padding:12px;border-top:1px solid #433251}
.lab-vars label{display:grid;gap:4px;color:#cbb9df;font-size:12px;min-width:0}
.lab-vars input,.lab-vars select{min-height:40px;width:100%;min-width:0;border:1px solid #4a385f;border-radius:6px;padding:8px;background:#100d17;color:#eee4fb;font-size:16px}
.lab-vars input[aria-invalid=true]{border-color:#e3a095}
.lab-vars small{color:#b7a7cb;font-size:11px}
.lab-subnet{grid-column:1/-1}
.lab-auto{justify-self:start;color:#d5bcff;font-size:12px;padding:6px 0;min-height:36px}
.lab-vars-footer{grid-column:1/-1;display:flex;align-items:center;justify-content:space-between;gap:8px}
.lab-vars-footer button{color:#d5bcff;font-size:12px;padding:8px;min-height:40px}
@media(max-width:420px){.lab-vars-body{grid-template-columns:1fr}}
</style>

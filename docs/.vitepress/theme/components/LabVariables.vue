<script setup lang="ts">
import { computed } from 'vue'
import { useLabVariables, type LabKey } from '../labVariables'
const {values,validated,automaticSubnet,set,reset}=useLabVariables()
const props=withDefaults(defineProps<{ad?:boolean}>(),{ad:false})
const activeKeys=computed<LabKey[]>(()=>props.ad?['DC_IP','DOMAIN','DC_HOST','BASE_DN']:['IP','SUBNET','TCP_PORTS','UDP_PORTS'])
const adFields: {key:LabKey;label:string;example:string;help:string}[]=[
 {key:'DC_IP',label:'IP du contrôleur de domaine (DC)',example:'192.168.1.10',help:'Adresse IPv4 du DC, pas celle du poste client.'},
 {key:'DOMAIN',label:'Domaine DNS',example:'corp.local',help:'Nom DNS complet du domaine.'},
 {key:'DC_HOST',label:'Nom complet du DC (FQDN)',example:'dc01.corp.local',help:'Nom de la machine suivi du domaine DNS.'},
 {key:'BASE_DN',label:'Base LDAP (DN)',example:'DC=corp,DC=local',help:'Calculée depuis le domaine, ou saisie manuellement.'}
]
const prefixes=Array.from({length:33},(_,i)=>32-i)
const fields: {key:LabKey;label:string;placeholder:string}[] = [
  {key:'TCP_PORTS',label:'Ports TCP',placeholder:'22,80,445'},
  {key:'UDP_PORTS',label:'Ports UDP',placeholder:'53,161'}
]
</script>
<template>
  <details class="lab-vars">
    <summary>{{ ad ? "Variables Active Directory" : "Variables du laboratoire" }} <span>{{ activeKeys.filter(key=>validated[key]).length }}/{{ activeKeys.length }}</span></summary>
    <div class="lab-vars-body">
      <template v-if="!ad">
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
      </template>
      <template v-else>
        <label v-for="field in adFields" :key="field.key">
          <span>{{ field.label }}</span>
          <input type="text" :value="values[field.key]" :placeholder="field.key==='BASE_DN' && validated.BASE_DN ? validated.BASE_DN : field.example" autocomplete="off" spellcheck="false" :aria-invalid="!!values[field.key].trim() && !validated[field.key]" @input="set(field.key,($event.target as HTMLInputElement).value)">
          <small>{{ field.help }}</small>
          <small>Exemple : <code>{{ field.example }}</code></small>
          <small v-if="values[field.key].trim() && !validated[field.key]">Format invalide</small>
          <small v-else-if="field.key==='BASE_DN' && validated.BASE_DN && !values.BASE_DN.trim()">Calcul automatique : {{ validated.BASE_DN }}</small>
          <button v-if="field.key==='BASE_DN' && values.BASE_DN.trim()" type="button" class="lab-auto" @click="set('BASE_DN','')">Utiliser le calcul automatique</button>
        </label>
      </template>
      <div class="lab-vars-footer"><small>Valeurs conservées dans cet onglet.</small><button type="button" @click="ad ? activeKeys.forEach(key=>set(key,'')) : reset()">Réinitialiser</button></div>
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

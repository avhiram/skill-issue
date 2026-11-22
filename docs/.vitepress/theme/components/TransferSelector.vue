<script setup lang="ts">
import { computed, ref } from 'vue'
type OS = 'Linux' | 'Windows'
const source = ref<OS>('Linux')
const target = ref<OS>('Windows')
const methods = {
  'Linux-Linux': [
    { name: 'SCP (SSH)', condition: 'SSH sur la destination', steps: [{host:'Sur Linux source',lang:'bash',code:'scp ./rapport.txt etudiant@10.10.10.20:/tmp/'},{host:'Récupérer depuis Linux local',lang:'bash',code:'scp etudiant@10.10.10.20:/tmp/rapport.txt ./' }] },
    { name: 'SFTP', condition: 'SSH sur la destination', steps:[{host:'Sur Linux source',lang:'bash',code:'sftp etudiant@10.10.10.20\nput rapport.txt\nget autre_fichier.txt\nbye'}] },
    { name:'rsync',condition:'SSH et rsync disponibles',steps:[{host:'Sur Linux source',lang:'bash',code:'rsync -avP ./dossier/ etudiant@10.10.10.20:/tmp/dossier/'}]},
    { name:'HTTP (téléchargement)',condition:'Le destinataire atteint le port 8000 de la source',steps:[{host:'Sur Linux source (laisser ouvert)',lang:'bash',code:'python3 -m http.server 8000 --bind 0.0.0.0'},{host:'Sur Linux destination',lang:'bash',code:'curl -fLO http://10.10.14.10:8000/rapport.txt'}]},
    { name:'Netcat (laboratoire isolé)',condition:'Port 9001 autorisé ; non chiffré',steps:[{host:'Sur Linux destination (en premier)',lang:'bash',code:'nc -lvnp 9001 > rapport.txt'},{host:'Sur Linux source',lang:'bash',code:'nc 10.10.10.20 9001 < rapport.txt'}]}
  ],
  'Linux-Windows': [
    {name:'HTTP + PowerShell',condition:'Windows atteint le port 8000 de Kali',steps:[{host:'Sur Kali (laisser ouvert)',lang:'bash',code:'python3 -m http.server 8000 --bind 0.0.0.0'},{host:'Sur Windows (PowerShell)',lang:'powershell',code:"Invoke-WebRequest -Uri 'http://10.10.14.10:8000/outil.exe' -OutFile 'C:\\Users\\Public\\outil.exe'"}]},
    {name:'HTTP + curl.exe',condition:'Windows atteint le port 8000 de Kali',steps:[{host:'Sur Kali',lang:'bash',code:'python3 -m http.server 8000 --bind 0.0.0.0'},{host:'Sur Windows',lang:'powershell',code:"curl.exe -fL 'http://10.10.14.10:8000/outil.exe' -o 'C:\\Users\\Public\\outil.exe'"}]},
    {name:'SCP',condition:'OpenSSH Server actif sur Windows',steps:[{host:'Sur Linux source',lang:'bash',code:'scp ./rapport.txt etudiant@10.10.10.30:C:/Users/Public/rapport.txt'}]},
    {name:'SMB (partage Windows)',condition:'Partage Depot accessible en écriture',steps:[{host:'Sur Linux source',lang:'bash',code:"smbclient //10.10.10.30/Depot -U 'LAB\\etudiant' -c 'put rapport.txt rapport.txt'"}]}
  ],
  'Windows-Linux': [
    {name:'SMB sur Kali',condition:'Windows atteint le port 445 de Kali ; permissions d’écriture',steps:[{host:'Sur Kali (laisser ouvert)',lang:'bash',code:"mkdir -p ./reception\nsudo impacket-smbserver -smb2support -username audit -password 'MotDePasseTest' partage ./reception"},{host:'Sur Windows (PowerShell)',lang:'powershell',code:"net use \\\\10.10.14.10\\partage /user:audit MotDePasseTest\nCopy-Item 'C:\\Users\\Public\\rapport.txt' '\\\\10.10.14.10\\partage\\rapport.txt'\nnet use \\\\10.10.14.10\\partage /delete"}]},
    {name:'SCP',condition:'OpenSSH Client sur Windows et serveur SSH sur Kali',steps:[{host:'Sur Windows',lang:'powershell',code:"scp 'C:\\Users\\Public\\rapport.txt' kali@10.10.14.10:/tmp/rapport.txt"}]},
    {name:'WebDAV (PUT)',condition:'WsgiDAV installé sur Kali ; port 8080 accessible',steps:[{host:'Sur Kali (laisser ouvert)',lang:'bash',code:'mkdir -p ./reception\nwsgidav -H 0.0.0.0 -p 8080 -r ./reception --auth anonymous'},{host:'Sur Windows',lang:'powershell',code:"curl.exe -T 'C:\\Users\\Public\\rapport.txt' 'http://10.10.14.10:8080/rapport.txt'"}]}
  ],
  'Windows-Windows': [
    {name:'SMB (partage existant)',condition:'Partage Depot accessible en écriture',steps:[{host:'Sur Windows source',lang:'powershell',code:"Copy-Item 'C:\\Users\\Public\\rapport.txt' '\\\\10.10.10.30\\Depot\\rapport.txt'"}]},
    {name:'SCP',condition:'OpenSSH Server actif sur Windows destination',steps:[{host:'Sur Windows source',lang:'powershell',code:"scp 'C:\\Users\\Public\\rapport.txt' etudiant@10.10.10.30:C:/Users/Public/rapport.txt"}]}
  ]
}
const key = computed(() => `${source.value}-${target.value}` as keyof typeof methods)
const choices = computed(() => methods[key.value])
const selected = ref(0)
const current = computed(() => choices.value[Math.min(selected.value,choices.value.length-1)])
function chooseSource(v:Event){source.value=(v.target as HTMLSelectElement).value as OS;selected.value=0}
function chooseTarget(v:Event){target.value=(v.target as HTMLSelectElement).value as OS;selected.value=0}
</script>

<template>
  <div class="transfer-selector">
    <div class="transfer-fields">
      <label>Fichier sur <select :value="source" @change="chooseSource"><option>Linux</option><option>Windows</option></select></label>
      <label>Envoyer vers <select :value="target" @change="chooseTarget"><option>Linux</option><option>Windows</option></select></label>
    </div>
    <label class="transfer-method">Méthode <select v-model.number="selected"><option v-for="(m,i) in choices" :key="m.name" :value="i">{{ m.name }}</option></select></label>
    <p><strong>Prérequis :</strong> {{ current.condition }}</p>
    <div v-for="(step,i) in current.steps" :key="i">
      <strong>{{ i+1 }}. {{ step.host }}</strong>
      <div class="transfer-code"><button type="button" @click="navigatorClipboard(step.code)" aria-label="Copier la commande">Copier</button><pre><code>{{ step.code }}</code></pre></div>
    </div>
    <p class="transfer-help">IP de laboratoire : Kali 10.10.14.10 · Linux 10.10.10.20 · Windows 10.10.10.30. Adapter les comptes, chemins et ports. Voir les explications détaillées plus bas.</p>
  </div>
</template>

<script lang="ts">
export default {
  methods: {
    async navigatorClipboard(value:string) {
      if (typeof navigator !== 'undefined' && navigator.clipboard) await navigator.clipboard.writeText(value)
    }
  }
}
</script>

<style scoped>
.transfer-selector{border:1px solid #48345d;border-radius:12px;padding:16px;background:#15101e;margin:18px 0}
.transfer-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.transfer-selector label{display:flex;flex-direction:column;gap:7px;font-weight:650;color:#dacbfa}
.transfer-selector select{width:100%;min-width:0;padding:10px;border:1px solid #59436e;border-radius:7px;background:#241a30;color:#f2ecff;font-size:15px}
.transfer-method{margin-top:14px}
.transfer-selector p{font-size:14px}
.transfer-code{position:relative;background:#0b0910;border:1px solid #30243f;border-radius:8px;margin:8px 0 16px}
.transfer-code pre{overflow-x:auto;padding:36px 12px 12px;margin:0;white-space:pre-wrap;overflow-wrap:anywhere;color:#e4d8f5;font-size:13px}
.transfer-code button{position:absolute;right:7px;top:6px;background:#3d2b54;border:1px solid #66507d;color:white;border-radius:5px;padding:4px 10px;cursor:pointer}
.transfer-help{color:#b6aec5}
@media(max-width:420px){.transfer-fields{grid-template-columns:1fr}}
</style>

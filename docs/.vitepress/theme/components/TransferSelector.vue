<script setup lang="ts">
import { computed, ref } from 'vue'

type System = 'Linux' | 'Windows'
type Method = { name: string, anchor: string }

const source = ref<System>('Linux')
const destination = ref<System>('Windows')
const methods: Record<System, Record<System, Method[]>> = {
  Linux: {
    Linux: [
      { name: 'SCP depuis la source', anchor: 'll-scp' },
      { name: 'SCP depuis la destination', anchor: 'll-scp-reception' },
      { name: 'Dossier par SCP', anchor: 'll-scp-dossier' },
      { name: 'rsync', anchor: 'll-rsync' },
      { name: 'SFTP', anchor: 'll-sftp' },
      { name: 'HTTP', anchor: 'll-http' },
      { name: 'HTTPS', anchor: 'https-linux' },
      { name: 'FTP', anchor: 'ftp' },
      { name: 'Netcat', anchor: 'll-netcat' }
    ],
    Windows: [
      { name: 'HTTP avec PowerShell', anchor: 'lw-http-ps' },
      { name: 'SCP', anchor: 'lw-scp' },
      { name: 'Partage SMB sur Kali', anchor: 'lw-smb-kali' },
      { name: 'Partage SMB sur Windows', anchor: 'lw-smb-windows' },
      { name: 'HTTPS avec PowerShell', anchor: 'https-windows' },
      { name: 'HTTP avec curl.exe', anchor: 'lw-http-curl' },
      { name: 'Dossier partagé par RDP', anchor: 'rdp' },
      { name: 'Base64', anchor: 'base64-linux' }
    ]
  },
  Windows: {
    Linux: [
      { name: 'SCP', anchor: 'wl-scp' },
      { name: 'Partage SMB sur Kali', anchor: 'wl-smb-kali' },
      { name: 'Partage SMB sur Windows', anchor: 'wl-smb-windows' },
      { name: 'HTTPS', anchor: 'https-linux' },
      { name: 'WebDAV', anchor: 'wl-webdav' },
      { name: 'Copie vers Kali par RDP', anchor: 'rdp-retour' },
      { name: 'Base64', anchor: 'base64-windows' }
    ],
    Windows: [
      { name: 'Partage SMB existant', anchor: 'ww-smb' },
      { name: 'SCP', anchor: 'ww-scp' },
      { name: 'Créer le partage SMB', anchor: 'ww-creer' },
      { name: 'HTTPS avec PowerShell', anchor: 'https-windows' }
    ]
  }
}

const available = computed(() => methods[source.value][destination.value])
</script>

<template>
  <nav class="transfer-selector" aria-label="Choisir un transfert de fichiers">
    <div class="transfer-fields">
      <label>Machine source
        <select v-model="source"><option value="Linux">Linux (dont Kali)</option><option value="Windows">Windows</option></select>
      </label>
      <label>Machine de destination
        <select v-model="destination"><option value="Linux">Linux (dont Kali)</option><option value="Windows">Windows</option></select>
      </label>
    </div>
    <ul :aria-label="`Méthodes de ${source} vers ${destination}`">
      <li v-for="method in available" :key="method.anchor">
        <a :href="'#' + method.anchor">{{ method.name }}</a>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.transfer-selector {
  margin: 1.25rem 0;
  padding: 1rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  background: var(--vp-c-bg-soft);
}
.transfer-fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 11rem), 1fr));
  gap: .75rem;
}
.transfer-selector label {
  display: grid;
  gap: .35rem;
  font-weight: 600;
}
.transfer-selector select {
  appearance: auto;
  width: 100%;
  min-height: 44px;
  padding: .4rem .65rem;
  border: 1px solid var(--vp-c-text-3);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 1rem;
}
.transfer-selector ul {
  display: flex;
  flex-wrap: wrap;
  gap: .15rem 1.15rem;
  padding: 0;
  margin: .75rem 0 0;
  list-style: none;
}
.transfer-selector li { margin: 0; }
.transfer-selector a { display: inline-block; padding: .35rem 0; }
</style>

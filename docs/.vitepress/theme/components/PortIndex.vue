<script setup lang="ts">
import { computed, ref } from 'vue'
import { withBase } from 'vitepress'
const entries = [
  {
    "ports": "21",
    "label": "FTP",
    "path": "/oscp/reconnaissance#port-ftp"
  },
  {
    "ports": "22",
    "label": "SSH",
    "path": "/oscp/reconnaissance#port-ssh"
  },
  {
    "ports": "23",
    "label": "Telnet",
    "path": "/oscp/reconnaissance#port-telnet"
  },
  {
    "ports": "25",
    "label": "SMTP",
    "path": "/oscp/reconnaissance#port-smtp"
  },
  {
    "ports": "53",
    "label": "DNS",
    "path": "/oscp/reconnaissance#port-dns"
  },
  {
    "ports": "69",
    "label": "TFTP",
    "path": "/oscp/reconnaissance#port-tftp"
  },
  {
    "ports": "80, 443, 8080, 8443",
    "label": "HTTP / HTTPS",
    "path": "/oscp/applications-web"
  },
  {
    "ports": "88",
    "label": "Kerberos",
    "path": "/oscp/reconnaissance#port-kerberos"
  },
  {
    "ports": "110",
    "label": "POP3",
    "path": "/oscp/reconnaissance#port-pop3"
  },
  {
    "ports": "111",
    "label": "RPC / rpcbind",
    "path": "/oscp/reconnaissance#port-rpc"
  },
  {
    "ports": "135, 593",
    "label": "MSRPC",
    "path": "/oscp/reconnaissance#port-msrpc"
  },
  {
    "ports": "139, 445",
    "label": "SMB",
    "path": "/oscp/reconnaissance#port-smb"
  },
  {
    "ports": "143, 993",
    "label": "IMAP",
    "path": "/oscp/reconnaissance#port-imap"
  },
  {
    "ports": "161",
    "label": "SNMP (UDP)",
    "path": "/oscp/reconnaissance#port-snmp"
  },
  {
    "ports": "389, 636, 3268, 3269",
    "label": "LDAP / LDAPS",
    "path": "/oscp/reconnaissance#port-ldap"
  },
  {
    "ports": "1433",
    "label": "MSSQL",
    "path": "/oscp/reconnaissance#port-mssql"
  },
  {
    "ports": "2049",
    "label": "NFS",
    "path": "/oscp/reconnaissance#port-nfs"
  },
  {
    "ports": "3003",
    "label": "Service à identifier",
    "path": "/oscp/reconnaissance#port-3003"
  },
  {
    "ports": "3306",
    "label": "MySQL / MariaDB",
    "path": "/oscp/reconnaissance#port-mysql"
  },
  {
    "ports": "3389",
    "label": "RDP",
    "path": "/oscp/reconnaissance#port-rdp"
  },
  {
    "ports": "5432, 5433",
    "label": "PostgreSQL",
    "path": "/oscp/reconnaissance#port-postgresql"
  },
  {
    "ports": "5900",
    "label": "VNC",
    "path": "/oscp/reconnaissance#port-vnc"
  },
  {
    "ports": "5985, 5986",
    "label": "WinRM",
    "path": "/oscp/reconnaissance#port-winrm"
  },
  {
    "ports": "6379",
    "label": "Redis",
    "path": "/oscp/reconnaissance#port-redis"
  },
  {
    "ports": "",
    "label": "Port inconnu",
    "path": "/oscp/reconnaissance#port-unknown"
  }
]
const query=ref('')
const normalize=(value:string)=>value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim()
const filtered=computed(()=>{
 const q=normalize(query.value)
 if(!q)return entries
 if(/^\d+$/.test(q)){
   const exact=entries.filter(item=>item.ports.split(',').map(p=>p.trim()).includes(q))
   return exact.length?exact:entries.filter(item=>item.ports.split(',').some(p=>p.trim().startsWith(q)))
 }
 return entries.filter(item=>normalize(item.label+' '+item.ports).includes(q))
})
</script>
<template>
  <div class="port-index">
    <div class="port-search">
      <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></svg>
      <input v-model="query" type="search" aria-label="Port ou service" placeholder="Port ou service : 445, SMB…" autocomplete="off" spellcheck="false">
      <button v-if="query" type="button" aria-label="Effacer la recherche" @click="query=''">×</button>
    </div>
    <nav aria-label="Index des ports et services" class="port-list">
      <a v-for="item in filtered" :key="item.path" :href="withBase(item.path)">
        <span class="port-number">{{ item.ports || '—' }}</span>
        <span class="port-service">{{ item.label }}</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>
      </a>
      <p v-if="!filtered.length" role="status">Aucun service correspondant. <a :href="withBase('/oscp/reconnaissance#port-unknown')">Port inconnu</a></p>
    </nav>
  </div>
</template>
<style scoped>
.port-index{display:grid;gap:10px;margin-top:14px;min-width:0}
.port-search{display:flex;align-items:center;gap:8px;border:1px solid #49345e;border-radius:9px;background:#15101e;padding:0 12px;color:#b39aff;min-height:48px}
.port-search:focus-within{border-color:#b39aff}
.port-search input{flex:1;min-width:0;width:100%;height:46px;outline:none;background:transparent;color:#f0edf8;font-size:16px}
.port-search input::placeholder{color:#a99aba}
.port-search input::-webkit-search-cancel-button{display:none}
.port-search button{width:36px;height:44px;font-size:22px;flex:none}
.port-list{display:grid;gap:0}
.port-list>a{display:grid;grid-template-columns:minmax(90px,32%) minmax(0,1fr) 16px;align-items:center;gap:10px;min-height:45px;padding:9px 4px;border-bottom:1px solid #29213a;color:#e6d9f6;text-decoration:none;line-height:1.4}
.port-list>a:hover,.port-list>a:active{background:#20162c;color:#f1e5ff}
.port-number{font-size:12px;color:#b39aff;font-variant-numeric:tabular-nums;font-weight:600;overflow-wrap:anywhere}
.port-service{font-size:14px;font-weight:550}
.port-list>a svg{color:#a68cc7}
.port-list p{font-size:13px;color:#b6aec5}
</style>

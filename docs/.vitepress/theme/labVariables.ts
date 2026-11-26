import { computed, onMounted, onBeforeUnmount, ref } from 'vue'

type Values = { IP: string; SUBNET: string; TCP_PORTS: string; UDP_PORTS: string; DC_IP: string; DOMAIN: string; DC_HOST: string; BASE_DN: string }
type Settings = Values & { PREFIX: string }
export type LabKey = keyof Values
const keys: LabKey[] = ['IP','SUBNET','TCP_PORTS','UDP_PORTS','DC_IP','DOMAIN','DC_HOST','BASE_DN']
const settingsKeys: (keyof Settings)[] = [...keys,'PREFIX']
const storageKey = 'skill-issue:lab-variables:v1'
const eventName = 'skill-lab-variables'
const blank = (): Settings => ({IP:'',SUBNET:'',TCP_PORTS:'',UDP_PORTS:'',DC_IP:'',DOMAIN:'',DC_HOST:'',BASE_DN:'',PREFIX:''})
function ip(value: string) {
  const parts = value.split('.')
  return parts.length === 4 && parts.every(part => /^(0|[1-9]\d{0,2})$/.test(part) && Number(part)<=255)
}
export function networkCidr(address: string, prefix: string): string {
  if (!ip(address) || !/^(0|[1-9]|[12]\d|3[012])$/.test(prefix)) return ''
  const bits=Number(prefix)
  const n=address.split('.').reduce((acc,octet)=>acc*256+Number(octet),0)
  const size=2**(32-bits)
  const network=Math.floor(n/size)*size
  const octets=[24,16,8,0].map(shift=>Math.floor(network/2**shift)%256)
  return octets.join('.')+'/'+bits
}
function ports(value: string) {
  return /^\d{1,5}(,\d{1,5})*$/.test(value) && value.split(',').every(p=>Number(p)>=1 && Number(p)<=65535)
}
export function validValue(key: LabKey, raw: string) {
  const v=raw.trim()
  if (!v) return ''
  if (key==='IP' || key==='DC_IP') return ip(v)?v:''
  if (key==='DOMAIN' || key==='DC_HOST') {
    return v.length<=253 && v.includes('.') && v.split('.').every(label=>/^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/i.test(label)) ? v.toLowerCase() : ''
  }
  if (key==='BASE_DN') return /^(?:DC=[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:,DC=[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$/i.test(v)?v:''
  if (key==='SUBNET') {
    const parts=v.split('/')
    return parts.length===2 && ip(parts[0]) && /^(0|[1-9]|[12]\d|3[012])$/.test(parts[1])?v:''
  }
  const p=v.replace(/\s+/g,'')
  return ports(p)?p:''
}
export function useLabVariables() {
  const values=ref<Settings>(blank())
  const automaticSubnet=computed(()=>networkCidr(validValue('IP',values.value.IP),values.value.PREFIX))
  const validated=computed(()=>{
    const result=Object.fromEntries(keys.map(k=>[k,validValue(k,values.value[k])])) as Values
    if (!values.value.SUBNET.trim()) result.SUBNET=automaticSubnet.value
    if (!values.value.BASE_DN.trim() && result.DOMAIN) result.BASE_DN=result.DOMAIN.split('.').map(label=>'DC='+label).join(',')
    return result
  })
  function sync(event?: Event) {
    let data: Partial<Settings> = {}
    try {
      if(event instanceof CustomEvent) data=event.detail||{}
      else data=JSON.parse(sessionStorage.getItem(storageKey)||'{}')
    } catch {}
    const next=blank()
    for(const k of settingsKeys) if(typeof data?.[k]==='string') next[k]=data[k]!.slice(0,2048)
    values.value=next
  }
  function publish(next: Settings) {
    values.value=next
    try { sessionStorage.setItem(storageKey,JSON.stringify(next)) } catch {}
    window.dispatchEvent(new CustomEvent(eventName,{detail:next}))
  }
  function set(key:keyof Settings,value:string) { publish({...values.value,[key]:value.slice(0,2048)}) }
  function reset() { publish(blank()); try { sessionStorage.removeItem(storageKey) } catch {} }
  onMounted(()=>{sync();window.addEventListener(eventName,sync)})
  onBeforeUnmount(()=>window.removeEventListener(eventName,sync))
  return {values,validated,automaticSubnet,set,reset}
}

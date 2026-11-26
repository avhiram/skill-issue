import { computed, onMounted, onBeforeUnmount, ref } from 'vue'

type Values = { IP: string; SUBNET: string; TCP_PORTS: string; UDP_PORTS: string }
export type LabKey = keyof Values
const keys: LabKey[] = ['IP','SUBNET','TCP_PORTS','UDP_PORTS']
const storageKey = 'skill-issue:lab-variables:v1'
const eventName = 'skill-lab-variables'
const blank = (): Values => ({IP:'',SUBNET:'',TCP_PORTS:'',UDP_PORTS:''})
function ip(value: string) {
  const parts = value.split('.')
  return parts.length === 4 && parts.every(part => /^(0|[1-9]\d{0,2})$/.test(part) && Number(part)<=255)
}
function ports(value: string) {
  return /^\d{1,5}(,\d{1,5})*$/.test(value) && value.split(',').every(p=>Number(p)>=1 && Number(p)<=65535)
}
export function validValue(key: LabKey, raw: string) {
  const v=raw.trim()
  if (!v) return ''
  if (key==='IP') return ip(v)?v:''
  if (key==='SUBNET') {
    const parts=v.split('/')
    return parts.length===2 && ip(parts[0]) && /^(0|[1-9]|[12]\d|3[012])$/.test(parts[1])?v:''
  }
  const p=v.replace(/\s+/g,'')
  return ports(p)?p:''
}
export function useLabVariables() {
  const values=ref<Values>(blank())
  const validated=computed(()=>Object.fromEntries(keys.map(k=>[k,validValue(k,values.value[k])])) as Values)
  function sync(event?: Event) {
    let data: Partial<Values> = {}
    try {
      if(event instanceof CustomEvent) data=event.detail||{}
      else data=JSON.parse(sessionStorage.getItem(storageKey)||'{}')
    } catch {}
    const next=blank()
    for(const k of keys) if(typeof data?.[k]==='string') next[k]=data[k]!.slice(0,2048)
    values.value=next
  }
  function publish(next: Values) {
    values.value=next
    try { sessionStorage.setItem(storageKey,JSON.stringify(next)) } catch {}
    window.dispatchEvent(new CustomEvent(eventName,{detail:next}))
  }
  function set(key:LabKey,value:string) { publish({...values.value,[key]:value.slice(0,2048)}) }
  function reset() { publish(blank()); try { sessionStorage.removeItem(storageKey) } catch {} }
  onMounted(()=>{sync();window.addEventListener(eventName,sync)})
  onBeforeUnmount(()=>window.removeEventListener(eventName,sync))
  return {values,validated,set,reset}
}

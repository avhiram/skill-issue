import { computed, onMounted, ref } from 'vue'

const STORAGE_KEY = 'skill-issue:bug-bounty:target:v1'
const value = ref('')
let loaded = false

export function useBountyTarget() {
  onMounted(() => {
    if (loaded) return
    loaded = true
    try { value.value = localStorage.getItem(STORAGE_KEY) || '' } catch {}
  })

  const target = computed(() => {
    const raw = value.value.trim()
    if (!raw) return null
    if (!/^[a-zA-Z0-9.:/\-]+$/.test(raw)) return null
    try {
      const url = new URL(/^https?:\/\//i.test(raw) ? raw : 'https://' + raw)
      if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) return null
      if (url.pathname !== '/' || url.search || url.hash) return null
      const domain = url.hostname.toLowerCase()
      const labels = domain.split('.')
      if (domain.length > 253 || labels.length < 2 || !labels.every(label => /^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(label))) return null
      return { domain, origin: url.origin }
    } catch { return null }
  })

  function setTarget(next: string) {
    value.value = next
    try { localStorage.setItem(STORAGE_KEY, next) } catch {}
  }

  return { value, target, setTarget }
}

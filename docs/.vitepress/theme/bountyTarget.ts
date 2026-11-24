import { computed, onMounted, ref } from 'vue'

const STORAGE_KEY = 'skill-issue:bug-bounty:target:v1'
const value = ref('')
const PROGRAM_KEY = 'skill-issue:bug-bounty:program:v1'
const program = ref('')
const HISTORY_KEY = 'skill-issue:bug-bounty:programs:v1'
type SavedProgram = { workspace: string; target: string; name: string }
const history = ref<SavedProgram[]>([])
let loaded = false

export function useBountyTarget() {
  onMounted(() => {
    if (loaded) return
    loaded = true
    try {
      value.value = localStorage.getItem(STORAGE_KEY) || ''
      program.value = localStorage.getItem(PROGRAM_KEY) || ''
      const saved: unknown = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]')
      if (Array.isArray(saved)) history.value = saved.filter((entry): entry is SavedProgram => !!entry && typeof entry.workspace === 'string' && typeof entry.target === 'string' && typeof entry.name === 'string').slice(0, 100)
    } catch {}
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
      return { domain, origin: url.origin, port: url.port }
    } catch { return null }
  })

  const workspace = computed(() => {
    if (!target.value) return null
    const name = program.value.trim().toLowerCase()
    if (name && !/^[a-z0-9][a-z0-9_-]{0,63}$/.test(name)) return null
    const host = target.value.domain + (target.value.port ? '_port_' + target.value.port : '')
    const folder = host + (name ? '__' + name : '')
    return folder.length <= 255 ? folder : null
  })

  function setProgram(next: string) {
    program.value = next
    try { localStorage.setItem(PROGRAM_KEY, next) } catch {}
  }

  function setTarget(next: string) {
    value.value = next
    try { localStorage.setItem(STORAGE_KEY, next) } catch {}
  }

  function saveProgram() {
    if (!workspace.value || !target.value) return false
    const entry = { workspace: workspace.value, target: target.value.origin, name: program.value.trim() }
    history.value = [entry, ...history.value.filter(item => item.workspace !== entry.workspace)].slice(0, 100)
    try { localStorage.setItem(HISTORY_KEY, JSON.stringify(history.value)); return true } catch { return false }
  }

  function selectProgram(folder: string) {
    const entry = history.value.find(item => item.workspace === folder)
    if (!entry) return
    setTarget(entry.target)
    setProgram(entry.name)
  }

  return { value, target, setTarget, program, setProgram, workspace, history, saveProgram, selectProgram }
}

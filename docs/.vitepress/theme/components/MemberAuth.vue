<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { withBase } from 'vitepress'
import { createClient, type SupabaseClient, type Session } from '@supabase/supabase-js'

const email = ref('')
const password = ref('')
const mode = ref<'login' | 'register' | 'reset' | 'recover'>('login')
const session = ref<Session | null>(null)
const ready = ref(false)
const busy = ref(false)
const message = ref('')
const failed = ref(false)
const grants = ref<{ section: string; source: string; starts_at: string; expires_at: string | null; revoked_at: string | null }[]>([])
const grantError = ref(false)
let client: SupabaseClient | undefined
let unsubscribe: (() => void) | undefined
let mounted = false
let generation = 0
const redirect = 'https://avhiram.github.io/skill-issue/membres/'
const active = computed(() => grants.value.filter(g => !g.revoked_at && Date.parse(g.starts_at) <= Date.now() && (!g.expires_at || Date.parse(g.expires_at) > Date.now())))

const memberSections = [
  { id: 'oscp', title: 'OSCP', path: '/oscp/' },
  { id: 'crto', title: 'CRTO', path: '/crto/' },
  { id: 'crtp', title: 'CRTP', path: '/crtp/' },
  { id: 'bug-bounty', title: 'Bug Bounty', path: '/bug-bounty/' }
]
function hasGrant(id: string) {
  return active.value.some(g => g.section === '*' || g.section.trim().toLowerCase().replace(/[_\s]+/g, '-') === id)
}

async function refresh() {
  const request = ++generation
  grants.value = []
  grantError.value = false
  if (!client || !session.value) return
  const { data, error } = await client.from('member_access').select('section,source,starts_at,expires_at,revoked_at')
  if (!mounted || request !== generation) return
  grantError.value = !!error
  grants.value = error ? [] : data || []
}

onMounted(async () => {
  mounted = true
  try {
    client = createClient('https://kqnvvwyygqivkpqkpdgb.supabase.co', 'sb_publishable_Y-tMgaUOXkFAYUNwr_Xqjg_hjh01ZBX', {
      auth: { storage: window.sessionStorage, persistSession: true, autoRefreshToken: true, detectSessionInUrl: true }
    })
    const { data } = client.auth.onAuthStateChange((event, next) => {
      if (!mounted) return
      session.value = next
      if (event === 'PASSWORD_RECOVERY') mode.value = 'recover'
      if (!next) { grants.value = []; generation++ }
      window.setTimeout(() => { if (mounted) void refresh() }, 0)
    })
    unsubscribe = () => data.subscription.unsubscribe()
    const { data: initial, error } = await client.auth.getSession()
    if (!mounted) return
    if (error) throw error
    session.value = initial.session
    await refresh()
  } catch {
    failed.value = true
    message.value = 'Connexion au service indisponible. Réessaie après avoir actualisé la page.'
  } finally { ready.value = true }
})
onUnmounted(() => { mounted = false; generation++; unsubscribe?.() })

function changeMode(next: 'login' | 'register' | 'reset') {
  mode.value = next
  password.value = ''
  message.value = ''
  failed.value = false
}
async function submit() {
  if (!client || busy.value) return
  busy.value = true
  message.value = ''
  failed.value = false
  try {
    if (mode.value === 'register') {
      const { error } = await client.auth.signUp({ email: email.value.trim(), password: password.value, options: { emailRedirectTo: redirect } })
      if (error) throw error
      message.value = 'Si nécessaire, confirme ton inscription via le lien reçu par email.'
    } else if (mode.value === 'reset') {
      const { error } = await client.auth.resetPasswordForEmail(email.value.trim(), { redirectTo: redirect })
      if (error) throw error
      message.value = 'Si un compte correspond à cette adresse, un lien de réinitialisation pourra être envoyé.'
    } else if (mode.value === 'recover') {
      const { error } = await client.auth.updateUser({ password: password.value })
      if (error) throw error
      mode.value = 'login'
      message.value = 'Mot de passe mis à jour.'
    } else {
      const { error } = await client.auth.signInWithPassword({ email: email.value.trim(), password: password.value })
      if (error) throw error
    }
  } catch {
    failed.value = true
    message.value = 'La demande a échoué. Vérifie les informations ou réessaie dans quelques instants.'
  } finally { password.value = ''; busy.value = false }
}
async function logout() {
  if (!client || busy.value) return
  busy.value = true
  try {
    const { error } = await client.auth.signOut({ scope: 'local' })
    if (error) throw error
    changeMode('login')
  } catch {
    failed.value = true
    message.value = 'La déconnexion a échoué. Réessaie.'
  } finally { busy.value = false }
}
</script>

<template>
  <section class="member-panel">
    <p v-if="!ready" role="status">Chargement…</p>
    <template v-else-if="session && mode !== 'recover'">
      <h2>Mon compte</h2>
      <p class="member-muted">{{ session.user.email }}</p>
      <p v-if="grantError" role="alert">Impossible de vérifier les accès actuellement.</p>
      <template v-else>
        <p v-if="active.length === 0">Compte gratuit · Aucun accès privé actif.</p>
        <template v-else>
          <p>Autorisations actives</p>
          <ul><li v-for="grant in active" :key="grant.section + grant.source">{{ grant.section === '*' ? 'Toutes les rubriques membres' : grant.section }} · {{ grant.source === 'admin' ? 'Administrateur' : grant.source === 'manual' ? 'Sur autorisation' : 'Abonnement' }}</li></ul>
        </template>
      </template>
      <div v-if="!grantError" class="member-paths">
        <p v-for="section in memberSections" :key="section.id">
          <strong>{{ section.title }}</strong>
          <a v-if="hasGrant(section.id)" :href="withBase(section.path)">Ouvrir la rubrique</a>
          <span v-else>Autorisation requise</span>
        </p>
      </div>
      <button class="member-secondary" :disabled="busy" @click="refresh">Actualiser mes accès</button>
      <button class="member-secondary" :disabled="busy" @click="logout">Se déconnecter</button>
    </template>
    <template v-else>
      <h2>{{ mode === 'register' ? 'Créer un compte' : mode === 'reset' ? 'Mot de passe oublié' : mode === 'recover' ? 'Nouveau mot de passe' : 'Connexion' }}</h2>
      <div class="member-paths">
        <p><strong>Accès gratuit</strong><span>Pour ceux qui veulent apprendre, même sans budget.</span></p>
        <p><strong>Accès membre</strong><span>Pour ceux qui veulent aller plus loin et développer leurs compétences.</span></p>
      </div>
      <form @submit.prevent="submit">
        <label v-if="mode !== 'recover'">Adresse email<input v-model="email" type="email" autocomplete="email" required :disabled="busy"></label>
        <label v-if="mode !== 'reset'">Mot de passe<input v-model="password" type="password" :autocomplete="mode === 'login' ? 'current-password' : 'new-password'" :minlength="mode === 'login' ? undefined : 12" required :disabled="busy"></label>
        <button class="member-primary" type="submit" :disabled="busy || !client">{{ busy ? 'En cours…' : mode === 'register' ? 'S’inscrire' : mode === 'reset' ? 'Envoyer le lien' : mode === 'recover' ? 'Modifier le mot de passe' : 'Se connecter' }}</button>
      </form>
      <div v-if="mode !== 'recover'" class="member-links">
        <button v-if="mode !== 'login'" :disabled="busy" @click="changeMode('login')">Connexion</button>
        <button v-if="mode !== 'register'" :disabled="busy" @click="changeMode('register')">Créer un compte</button>
        <button v-if="mode !== 'reset'" :disabled="busy" @click="changeMode('reset')">Mot de passe oublié ?</button>
      </div>
    </template>
    <p v-if="message" :role="failed ? 'alert' : 'status'" class="member-message">{{ message }}</p>
  </section>
</template>

<style scoped>
.member-panel { max-width: 460px; margin: 28px auto; padding: 28px; border: 1px solid var(--vp-c-divider); border-radius: 14px; background: var(--vp-c-bg-soft); }
.member-panel h2 { border: 0; margin: 0 0 12px; padding: 0; }
.member-muted { color: var(--vp-c-text-2); font-size: 14px; overflow-wrap: anywhere; }
.member-panel label { display: grid; gap: 6px; margin: 16px 0; font-size: 14px; }
.member-panel input { width: 100%; padding: 11px 12px; border: 1px solid var(--vp-c-divider); border-radius: 8px; background: var(--vp-c-bg); color: var(--vp-c-text-1); }
.member-panel input:focus-visible, .member-panel button:focus-visible { outline: 2px solid var(--vp-c-brand-1); outline-offset: 3px; }
.member-primary, .member-secondary { border-radius: 8px; padding: 10px 14px; font-weight: 600; }
.member-primary { width: 100%; background: var(--vp-button-brand-bg); color: var(--vp-button-brand-text); }
.member-secondary { border: 1px solid var(--vp-c-divider); margin: 8px 8px 0 0; }
.member-panel button:disabled { opacity: .5; cursor: not-allowed; }
.member-links { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 16px; }
.member-links button { color: var(--vp-c-brand-1); font-size: 13px; text-decoration: underline; }
.member-message { font-size: 14px; overflow-wrap: anywhere; }
.member-paths { display: grid; gap: 12px; margin: 18px 0 24px; }
.member-paths p { margin: 0; padding: 0 0 0 12px; border-left: 2px solid var(--vp-c-divider); font-size: 13px; line-height: 1.6; }
.member-paths p + p { border-left-color: var(--vp-c-brand-1); }
.member-paths strong, .member-paths span { display: block; }
.member-paths strong { color: var(--vp-c-text-1); font-size: 14px; }
.member-paths span { color: var(--vp-c-text-2); }
</style>

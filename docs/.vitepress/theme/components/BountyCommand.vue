<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useBountyTarget } from '../bountyTarget'
const props = withDefaults(defineProps<{ source: string; language?: string }>(), { language: 'bash' })
const { target } = useBountyTarget()
const command = computed(() => props.source
  .split('__BOUNTY_DOMAIN__').join(target.value?.domain || 'example.com')
  .split('__BOUNTY_ORIGIN__').join(target.value?.origin || 'https://example.com'))
const copied = ref(false)
const error = ref(false)
watch(command, () => { copied.value = false; error.value = false })
async function copyCommand() {
  try {
    await navigator.clipboard.writeText(command.value)
    copied.value = true
    error.value = false
  } catch {
    copied.value = false
    error.value = true
  }
}
</script>

<template>
  <div class="bounty-command">
    <div class="command-bar">
      <span>{{ language }}</span>
      <button type="button" @click="copyCommand">{{ copied ? 'Copié' : 'Copier' }}</button>
    </div>
    <pre><code>{{ command }}</code></pre>
    <span v-if="error" class="copy-error" role="status">Copie indisponible : sélectionner le texte manuellement.</span>
  </div>
</template>

<style scoped>
.bounty-command { position: relative; margin: 16px 0; border-radius: 8px; background: var(--vp-code-block-bg); overflow: hidden; }
.command-bar { display: flex; justify-content: flex-end; align-items: center; gap: 12px; padding: 8px 12px 0; color: var(--vp-c-text-2); font-size: 12px; }
.command-bar button { border: 1px solid var(--vp-c-divider); border-radius: 5px; padding: 5px 10px; color: var(--vp-c-text-1); }
.command-bar button:focus-visible { outline: 2px solid var(--vp-c-brand-1); }
.bounty-command pre { margin: 0; padding: 12px 16px 16px; overflow-x: auto; white-space: pre; }
.bounty-command code { color: var(--vp-c-text-1); background: transparent; font-family: var(--vp-font-family-mono); font-size: var(--vp-code-font-size); padding: 0; }
.copy-error { display: block; color: var(--vp-c-text-2); padding: 0 16px 10px; font-size: 12px; }
</style>

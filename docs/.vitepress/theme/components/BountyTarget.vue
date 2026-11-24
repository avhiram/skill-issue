<script setup lang="ts">
import { useBountyTarget } from '../bountyTarget'
const { value, target, setTarget } = useBountyTarget()
function update(event: Event) {
  setTarget((event.target as HTMLInputElement).value)
}
</script>

<template>
  <div class="bounty-target">
    <label>
      <span>Cible du programme</span>
      <input type="text" :value="value" placeholder="example.com ou https://example.com" autocomplete="off" spellcheck="false" @input="update">
    </label>
    <div class="target-meta">
      <span v-if="value && !target" role="status">Saisir un domaine ou une URL HTTP(S) sans chemin.</span>
      <span v-else-if="target" role="status">{{ target.domain }} · enregistré sur cet appareil</span>
      <span v-else>Adapte les commandes compatibles. Scope autorisé uniquement.</span>
      <button type="button" v-if="value" @click="setTarget('')">Effacer</button>
    </div>
  </div>
</template>

<style scoped>
.bounty-target { margin: 20px 0 24px; }
.bounty-target label { display: grid; gap: 8px; font-size: 14px; font-weight: 600; }
.bounty-target input { width: 100%; min-width: 0; padding: 11px 12px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg-soft); color: var(--vp-c-text-1); font: inherit; }
.bounty-target input:focus { outline: 1px solid var(--vp-c-brand-1); }
.target-meta { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-top: 8px; color: var(--vp-c-text-2); font-size: 12px; }
.target-meta span { overflow-wrap: anywhere; }
.target-meta button { color: var(--vp-c-brand-1); flex-shrink: 0; }
</style>

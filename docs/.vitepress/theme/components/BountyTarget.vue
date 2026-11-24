<script setup lang="ts">
import { ref, watch } from 'vue'
import { useBountyTarget } from '../bountyTarget'
const { value, target, setTarget, program, setProgram, workspace, history, saveProgram, selectProgram } = useBountyTarget()
const feedback = ref('')
watch([value, program], () => { feedback.value = '' })
function saveCurrent() { feedback.value = saveProgram() ? 'Programme enregistré.' : 'Sauvegarde locale indisponible.' }
function choose(event: Event) {
  const folder = (event.target as HTMLSelectElement).value
  if (folder) selectProgram(folder)
}
function update(event: Event) {
  setTarget((event.target as HTMLInputElement).value)
}
function updateProgram(event: Event) {
  setProgram((event.target as HTMLInputElement).value)
}
</script>

<template>
  <div class="bounty-target">
    <label v-if="history.length" class="saved-programs">
      <span>Programmes enregistrés</span>
      <select :value="history.some(item => item.workspace === workspace) ? workspace : ''" @change="choose">
        <option value="">Choisir un programme</option>
        <option v-for="item in history" :key="item.workspace" :value="item.workspace">{{ item.workspace }}</option>
      </select>
    </label>
    <label>
      <span>Cible du programme</span>
      <input type="text" :value="value" placeholder="example.com ou https://example.com" autocomplete="off" spellcheck="false" @input="update">
    </label>
    <label class="program-name">
      <span>Nom du programme (facultatif)</span>
      <input type="text" :value="program" placeholder="ex. programme-2026" autocomplete="off" spellcheck="false" @input="updateProgram">
    </label>
    <div class="target-meta">
      <span v-if="value && !target" role="status">Saisir un domaine ou une URL HTTP(S) sans chemin.</span>
      <span v-else-if="target && !workspace" role="status">Nom invalide ou dossier trop long (64 caractères pour le nom, 255 pour le dossier).</span>
      <span v-else-if="workspace" role="status">Dossier : ./{{ workspace }}</span>
      <span v-else>Adapte les commandes compatibles. Scope autorisé uniquement.</span>
      <div class="target-actions">
        <button type="button" :disabled="!workspace" @click="saveCurrent">Enregistrer</button>
        <button type="button" v-if="value || program" @click="setTarget(''); setProgram('')">Nouveau</button>
      </div>
    </div>
    <p v-if="feedback" class="workspace-note" role="status">{{ feedback }}</p>
    <p v-if="workspace" class="workspace-note">Terminal : lancer la préparation depuis le dossier parent souhaité.</p>
  </div>
</template>

<style scoped>
.bounty-target { margin: 20px 0 24px; }
.bounty-target label { display: grid; gap: 8px; font-size: 14px; font-weight: 600; }
.program-name { margin-top: 12px; }
.saved-programs { margin-bottom: 12px; }
.bounty-target input, .bounty-target select { width: 100%; min-width: 0; padding: 11px 12px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg-soft); color: var(--vp-c-text-1); font: inherit; }
.bounty-target input:focus, .bounty-target select:focus { outline: 1px solid var(--vp-c-brand-1); }
.target-meta { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-top: 8px; color: var(--vp-c-text-2); font-size: 12px; }
.target-meta span { overflow-wrap: anywhere; }
.target-actions { display: flex; flex-wrap: wrap; gap: 10px; }
.target-meta button { color: var(--vp-c-brand-1); flex-shrink: 0; }
.target-meta button:disabled { opacity: .45; cursor: not-allowed; }
.workspace-note { margin: 6px 0 0; font-size: 12px; color: var(--vp-c-text-2); }
</style>

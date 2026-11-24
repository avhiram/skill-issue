<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

const props = defineProps<{ storageKey: string; items: string[] }>()
const checked = ref<boolean[]>(props.items.map(() => false))
const ready = ref(false)
const key = computed(() => 'skill-issue:bug-bounty:checklist:v1:' + props.storageKey)
const count = computed(() => checked.value.filter(Boolean).length)

onMounted(() => {
  try {
    const saved = JSON.parse(localStorage.getItem(key.value) || 'null')
    if (Array.isArray(saved)) {
      const selected = new Set(saved.filter((item) => typeof item === 'string'))
      checked.value = props.items.map((item) => selected.has(item))
    }
  } catch {
    // The checklist still works if local storage is unavailable.
  }
  ready.value = true
})

function save() {
  if (!ready.value) return
  try {
    localStorage.setItem(key.value, JSON.stringify(props.items.filter((_, i) => checked.value[i])))
  } catch {
    // Keep the current selection in memory.
  }
}

function reset() {
  checked.value = props.items.map(() => false)
  save()
}
</script>

<template>
  <div class="bounty-checklist">
    <div class="checklist-meta">
      <span aria-live="polite">{{ count }} / {{ items.length }}</span>
      <button type="button" :disabled="count === 0" @click="reset">Réinitialiser</button>
    </div>
    <ul>
      <li v-for="(item, i) in items" :key="item">
        <label>
          <input v-model="checked[i]" type="checkbox" @change="save">
          <span :class="{ completed: checked[i] }">{{ item }}</span>
        </label>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.bounty-checklist { margin: 16px 0 24px; }
.checklist-meta { display: flex; justify-content: space-between; align-items: center; gap: 12px; color: var(--vp-c-text-2); font-size: 13px; }
.checklist-meta button { color: var(--vp-c-brand-1); padding: 8px 0 8px 12px; font-size: 13px; }
.checklist-meta button:disabled { opacity: .45; cursor: default; }
.bounty-checklist ul { list-style: none; padding: 0; margin: 6px 0; }
.bounty-checklist li { margin: 0; }
.bounty-checklist label { display: flex; align-items: flex-start; gap: 12px; min-height: 44px; padding: 9px 0; cursor: pointer; }
.bounty-checklist input { appearance: auto; flex: 0 0 20px; width: 20px; height: 20px; margin: 3px 0 0; accent-color: var(--vp-c-brand-1); cursor: pointer; }
.completed { text-decoration: line-through; color: var(--vp-c-text-2); }
.bounty-checklist input:focus-visible, .checklist-meta button:focus-visible { outline: 2px solid var(--vp-c-brand-1); outline-offset: 3px; }
</style>

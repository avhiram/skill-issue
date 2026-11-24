---
title: "WiFi Mindmap"
description: Canvas interactif de cybersécurité
aside: false
---

<script setup>
import ADMindmap from '../../.vitepress/theme/components/ADMindmap.vue'
</script>

# WiFi Mindmap

[Toutes les mindmaps](mindmaps.md)

<ClientOnly>
  <ADMindmap src="/mindmaps/wifi.canvas.json" title="WiFi Mindmap" />
  <template #fallback>Chargement de la mindmap…</template>
</ClientOnly>

---
title: Mindmap AD
description: Canvas interactif Active Directory
aside: false
---

<script setup>
import ADMindmap from '../../.vitepress/theme/components/ADMindmap.vue'
</script>

# Mindmap AD

Explore le Canvas Active Directory. Déplace la carte, zoome sur les branches ou recherche un élément.

<ClientOnly>
  <ADMindmap />
  <template #fallback>
    Chargement de la mind map…
  </template>
</ClientOnly>

<small>Canvas fourni par l’utilisateur. Version et provenance exactes non vérifiées. Les cartes reproduisent le contenu original, sans validation individuelle des commandes. À consulter dans un cadre de formation et de laboratoire autorisé.</small>

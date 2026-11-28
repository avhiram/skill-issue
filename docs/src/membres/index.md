---
title: Espace membre
aside: false
sidebar: false
prev: false
next: false
---

<script setup>
import MemberAuth from '../../.vitepress/theme/components/MemberAuth.vue'
</script>

# Espace membre

Retrouve les quatre parcours de l’espace membre. Connecte-toi pour consulter les autorisations de ton compte.

<div class="access-overview">
  <div class="access-card access-card-member" id="oscp"><strong>OSCP</strong><span>Préparation et méthodologie pentest.</span></div>
  <div class="access-card access-card-member" id="crto"><strong>CRTO</strong><span>Red Team et opérations en laboratoire.</span></div>
  <div class="access-card access-card-member" id="crtp"><strong>CRTP</strong><span>Active Directory et préparation à la certification.</span></div>
  <div class="access-card access-card-member" id="bug-bounty"><strong>Bug Bounty</strong><span>Méthodologie, outils et ressources.</span></div>
</div>

<ClientOnly>
  <MemberAuth />
</ClientOnly>

<script setup lang="ts">
import { computed, ref } from 'vue'

type Recherche = 'pseudo' | 'email' | 'personne' | 'domaine'
type Requete = { titre: string; recherche: string; detail: string }

const categorie = ref<Recherche>('pseudo')
const valeur = ref('')
const prenom = ref('')
const nom = ref('')

const texte = (s: string) => s.replace(/["\\]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 160)
const expression = (s: string) => '"' + texte(s) + '"'
const domaine = computed(() => valeur.value.trim().replace(/^https?:\/\//i, '').replace(/\/.*$/, '').replace(/:\d+$/, '').toLowerCase())
const domaineValide = computed(() => /^(?:[a-z0-9-]+\.)+[a-z]{2,}$/i.test(domaine.value) && domaine.value.length <= 253)

const recherches = computed<Requete[]>(() => {
  if (categorie.value === 'personne') {
    const a = texte(prenom.value)
    const b = texte(nom.value)
    if (!a || !b) return []
    const n = expression(a + ' ' + b)
    return [
      { titre: 'Mentions exactes', recherche: n, detail: 'Retrouver les pages où figure le nom complet.' },
      { titre: 'Documents publics', recherche: n + ' filetype:pdf', detail: 'Rechercher les PDF indexés contenant ce nom.' },
      { titre: 'Profils professionnels', recherche: n + ' site:linkedin.com/in/', detail: 'Rechercher les profils professionnels publics.' },
      { titre: 'Presse et publications', recherche: n + ' (article OR interview OR conférence)', detail: 'Rechercher des mentions dans des articles ou événements.' }
    ]
  }

  const v = texte(valeur.value)
  if (!v) return []
  if (categorie.value === 'email') {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return []
    const e = expression(v)
    return [
      { titre: 'Occurrences exactes', recherche: e, detail: "Retrouver les pages où l'adresse apparaît." },
      { titre: 'Documents indexés', recherche: e + ' filetype:pdf', detail: "Rechercher l'adresse dans des PDF publics." },
      { titre: 'Code et documentation', recherche: e + ' (site:github.com OR site:gitlab.com)', detail: 'Rechercher des mentions dans les pages indexées des plateformes de code.' }
    ]
  }
  if (categorie.value === 'domaine') {
    if (!domaineValide.value) return []
    const d = domaine.value
    return [
      { titre: 'Pages du domaine', recherche: 'site:' + d, detail: 'Lister les pages publiques indexées.' },
      { titre: 'Documents PDF', recherche: 'site:' + d + ' filetype:pdf', detail: 'Rechercher les PDF indexés.' },
      { titre: 'Sous-domaines visibles', recherche: 'site:' + d + ' -site:www.' + d, detail: 'Repérer certaines pages hors du sous-domaine www.' },
      { titre: 'Pages de contact', recherche: 'site:' + d + ' (inurl:contact OR inurl:about)', detail: 'Trouver les pages de contact ou de présentation.' }
    ]
  }
  const p = expression(v)
  return [
    { titre: 'Mentions du pseudonyme', recherche: p, detail: 'Retrouver les occurrences exactes du pseudo.' },
    { titre: 'Profils techniques', recherche: p + ' (site:github.com OR site:reddit.com)', detail: 'Rechercher des profils et échanges publics.' },
    { titre: 'Profils professionnels', recherche: p + ' site:linkedin.com/in/', detail: 'Rechercher les profils LinkedIn indexés.' },
    { titre: 'Forums et discussions', recherche: p + ' (forum OR discussion)', detail: 'Retrouver des messages et échanges publics.' }
  ]
})

const urlGoogle = (r: string) => 'https://www.google.com/search?q=' + encodeURIComponent(r)
function changerCategorie() {
  valeur.value = ''
  prenom.value = ''
  nom.value = ''
}
</script>

<template>
  <div class="osint-search">
    <div class="search-controls">
      <label class="osint-field">
        <span>Type de recherche</span>
        <select v-model="categorie" @change="changerCategorie">
          <option value="pseudo">Pseudonyme</option>
          <option value="email">E-mail</option>
          <option value="personne">Prénom et nom</option>
          <option value="domaine">Domaine</option>
        </select>
      </label>

      <template v-if="categorie === 'personne'">
        <label class="osint-field">
          <span>Prénom</span>
          <input v-model="prenom" type="text" placeholder="Prénom" autocomplete="off" maxlength="100">
        </label>
        <label class="osint-field">
          <span>Nom</span>
          <input v-model="nom" type="text" placeholder="Nom" autocomplete="off" maxlength="100">
        </label>
      </template>

      <label v-else class="osint-field osint-value">
        <span>{{ categorie === 'pseudo' ? 'Pseudonyme' : categorie === 'email' ? 'E-mail' : 'Domaine' }}</span>
        <input
          v-model="valeur"
          :type="categorie === 'email' ? 'email' : 'text'"
          :placeholder="categorie === 'pseudo' ? 'pseudo_exemple' : categorie === 'email' ? 'exemple@domaine.fr' : 'exemple.fr'"
          autocomplete="off"
          maxlength="220"
        >
      </label>
    </div>

    <p v-if="valeur.trim() && categorie === 'domaine' && !domaineValide" class="search-tip">Entre un domaine comme exemple.fr.</p>
    <p v-else-if="valeur.trim() && categorie === 'email' && recherches.length === 0" class="search-tip">Entre une adresse e-mail complète.</p>
    <p v-else-if="!recherches.length" class="search-tip">Renseigne la recherche pour obtenir les requêtes prêtes à ouvrir.</p>

    <div v-else class="search-results">
      <div v-for="item in recherches" :key="item.titre" class="search-result">
        <div class="search-result-text">
          <strong>{{ item.titre }}</strong>
          <code>{{ item.recherche }}</code>
          <span>{{ item.detail }}</span>
        </div>
        <a :href="urlGoogle(item.recherche)" target="_blank" rel="noopener noreferrer" :aria-label="'Ouvrir dans Google : ' + item.titre">Rechercher ↗</a>
      </div>
    </div>

    <p class="search-privacy">La requête est préparée dans ton navigateur. Elle n'est envoyée à Google que lorsque tu ouvres une recherche.</p>
  </div>
</template>

<style scoped>
.osint-search {
  border-top: 1px solid #382c42;
  border-bottom: 1px solid #382c42;
  margin: 14px 0 24px;
  padding: 19px 0 20px;
}
.search-controls { display: grid; grid-template-columns: 190px 1fr 1fr; gap: 12px; align-items: end; }
.osint-field { display: flex; flex-direction: column; min-width: 0; gap: 7px; }
.osint-field span { font-size: .79rem; font-weight: 600; color: #c8b8d2; }
.osint-field select, .osint-field input {
  width: 100%;
  min-width: 0;
  height: 41px;
  margin: 0;
  padding: 7px 11px;
  font: inherit;
  font-size: .91rem;
  color: #ebe2f2;
  border: 1px solid #53445c;
  border-radius: 5px;
  background: #201827;
}
.osint-field select:focus-visible, .osint-field input:focus-visible, .search-result a:focus-visible {
  outline: 2px solid #b58fce;
  outline-offset: 2px;
}
.osint-value { grid-column: span 2; }
.search-tip, .search-privacy { color: #a99aaf !important; font-size: .79rem; line-height: 1.6; }
.search-tip { margin: 14px 0 2px !important; }
.search-privacy { margin: 12px 0 0 !important; font-size: .73rem; }
.search-results { margin: 16px 0 0; display: flex; flex-direction: column; }
.search-result { display: flex; justify-content: space-between; align-items: center; gap: 18px; padding: 12px 0; border-top: 1px solid #302538; }
.search-result-text { min-width: 0; display: flex; flex-direction: column; align-items: start; gap: 4px; }
.search-result-text strong { font-weight: 630; font-size: .9rem; color: #e4d8ed; }
.search-result-text code { font-size: .78rem; line-height: 1.7; word-break: break-word; white-space: normal; color: #d6b2ef; }
.search-result-text span { color: #a99daf; font-size: .79rem; line-height: 1.55; }
.search-result a { color: #d6b5ef !important; font-size: .82rem; white-space: nowrap; text-decoration: none !important; }
.search-result a:hover { text-decoration: underline !important; }
@media (max-width: 700px) {
  .search-controls { grid-template-columns: 1fr 1fr; }
  .search-controls .osint-field:first-child { grid-column: span 2; }
  .osint-value { grid-column: span 2; }
  .search-result { align-items: start; flex-direction: column; gap: 5px; }
}
</style>

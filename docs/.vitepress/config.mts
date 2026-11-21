import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'SKILL-ISSUE',
  description: 'Documentation cybersécurité en français',
  lang: 'fr-FR',
  base: '/skill-issue/',
  srcDir: './src',
  outDir: './.vitepress/dist',
  cleanUrls: true,
  appearance: 'force-dark',
  lastUpdated: false,
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/skill-issue/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#09070E' }]
  ],
  markdown: {
    theme: { dark: 'github-dark' }
  },
  themeConfig: {
    logo: '/logo.svg',
    siteTitle: 'SKILL-ISSUE',
    nav: [
      { text: 'Accueil', link: '/' },
      { text: 'CRTO', link: '/crto/' }
    ],
    sidebar: [
      { text: 'SKILL-ISSUE', link: '/' },
      {
        text: 'Certifications',
        collapsed: false,
        items: [{ text: 'CRTO', link: '/crto/' }]
      }
    ],
    search: { provider: 'local' },
    outline: { level: [2, 3], label: 'Sur cette page' },
    docFooter: { prev: 'Précédent', next: 'Suivant' },
    returnToTopLabel: 'Retour en haut',
    sidebarMenuLabel: 'Menu'
  }
})

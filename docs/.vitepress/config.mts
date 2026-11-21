import { defineConfig } from 'vitepress'
import { tabsMarkdownPlugin } from 'vitepress-plugin-tabs'
import githubAlertsPlugin from './plugins/githubAlertsPlugin'
import youtubeEmbedPlugin from './plugins/youtubeEmbedPlugin'
import lineNumberPlugin from './plugins/lineNumbers'

export default defineConfig({
  title: 'SKILL-ISSUE',
  description: 'Documentation cybersécurité en français',
  lang: 'fr-FR',
  base: '/skill-issue/',
  srcDir: 'src',
  cleanUrls: true,
  lastUpdated: false,
  appearance: 'force-dark',
  srcExclude: [
    'ad/**', 'web/**', 'infra/**', 'evasion/**', 'physical/**',
    'phishing/**', 'intelligence-gathering/**', 'radio/**',
    'mobile-apps/**', 'policies/**', 'contributing/**'
  ],
  head: [
    ['meta', { name: 'theme-color', content: '#09070E' }],
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/skill-issue/logo.svg' }]
  ],
  themeConfig: {
    logo: '/logo.svg',
    siteTitle: 'SKILL-ISSUE',
    nav: [
      { text: 'OSCP', link: '/oscp/' },
      { text: 'CRTO', link: '/crto/' }
    ],
    sidebar: [
      {
        text: 'OSCP',
        link: '/oscp/',
        collapsed: false,
        items: [
          { text: '01. Collecte d’informations', link: '/oscp/reconnaissance' },
          { text: '02. Analyse de vulnérabilités', link: '/oscp/vulnerabilites' },
          { text: '03. Applications web', link: '/oscp/applications-web' },
          { text: '04. Attaques côté client', link: '/oscp/attaques-client' },
          { text: '05. Évasion antivirus et Metasploit', link: '/oscp/antivirus-metasploit' },
          { text: '06. Attaques par mots de passe', link: '/oscp/mots-de-passe' },
          { text: '07. Élévation de privilèges Windows', link: '/oscp/privileges-windows' },
          { text: '08. Élévation de privilèges Linux', link: '/oscp/privileges-linux' },
          { text: '09. Redirection de ports et tunnels manuels', link: '/oscp/redirection-ports' },
          { text: '10. Tunnels avec des outils', link: '/oscp/tunneling' },
          { text: '11. Théorie Active Directory', link: '/oscp/ad-theorie' },
          { text: '12. Énumération Active Directory', link: '/oscp/ad-enumeration' },
          { text: '13. Attaques Active Directory', link: '/oscp/ad-techniques' },
          { text: '14. Mouvement latéral Active Directory', link: '/oscp/ad-lateral' },
          { text: '15. Infrastructures cloud', link: '/oscp/cloud' },
          { text: '16. Rédaction de rapports', link: '/oscp/rapport' },
          { text: '17. Transferts de fichiers', link: '/oscp/transferts' },
          { text: '18. Utilitaires', link: '/oscp/utilitaires' },
          { text: '19. Méthodologie', link: '/oscp/methodologie' },
          { text: '20. Références', link: '/oscp/references' }
        ]
      },
      { text: 'CRTO', link: '/crto/', collapsed: true }
    ],
    search: { provider: 'local' },
    outline: { level: [2, 4], label: 'Sur cette page' },
    docFooter: { prev: 'Précédent', next: 'Suivant' },
    sidebarMenuLabel: 'Menu',
    returnToTopLabel: 'Retour en haut',
    socialLinks: [],
    editLink: false
  },
  markdown: {
    config(md) {
      md.use(tabsMarkdownPlugin)
      md.use(githubAlertsPlugin)
      md.use(youtubeEmbedPlugin)
      md.use(lineNumberPlugin)
    }
  }
})

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
    'mobile-apps/**', 'policies/**', 'contributing/**',
    'oscp/cloud.md', 'oscp/references.md'
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
          {
            text: 'Reconnaissance',
            collapsed: true,
            items: [
              { text: 'Information Gathering', link: '/oscp/reconnaissance' },
              { text: 'Analyse de vulnérabilités', link: '/oscp/vulnerabilites' }
            ]
          },
          {
            text: 'Applications et accès',
            collapsed: true,
            items: [
              { text: 'Applications web', link: '/oscp/applications-web' },
              { text: 'Attaques côté client', link: '/oscp/attaques-client' },
              { text: 'Antivirus et Metasploit', link: '/oscp/antivirus-metasploit' },
              { text: 'Mots de passe', link: '/oscp/mots-de-passe' }
            ]
          },
          {
            text: 'Systèmes et réseau',
            collapsed: true,
            items: [
              { text: 'Windows', link: '/oscp/privileges-windows' },
              { text: 'Linux', link: '/oscp/privileges-linux' },
              { text: 'Redirection de ports', link: '/oscp/redirection-ports' },
              { text: 'Tunneling', link: '/oscp/tunneling' },
              { text: 'Transfert de fichiers', link: '/oscp/transferts' }
            ]
          },
          {
            text: 'Active Directory',
            collapsed: true,
            items: [
              { text: 'Fondamentaux', link: '/oscp/ad-theorie' },
              { text: 'Énumération', link: '/oscp/ad-enumeration' },
              { text: 'Techniques', link: '/oscp/ad-techniques' },
              { text: 'Mouvement latéral', link: '/oscp/ad-lateral' }
            ]
          },
          {
            text: 'Outils et méthodologie',
            collapsed: true,
            items: [
              { text: 'Rapports', link: '/oscp/rapport' },
              { text: 'Utilitaires', link: '/oscp/utilitaires' },
              { text: 'Méthodologie OSCP', link: '/oscp/methodologie' }
            ]
          }
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

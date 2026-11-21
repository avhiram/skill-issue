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
          { text: "Reconnaissance", link: '/oscp/reconnaissance' },
          { text: "Analyse de vulnérabilités", link: '/oscp/vulnerabilites' },
          { text: "Applications web", link: '/oscp/applications-web' },
          { text: "Attaques côté client", link: '/oscp/attaques-client' },
          { text: "Antivirus et Metasploit", link: '/oscp/antivirus-metasploit' },
          { text: "Mots de passe et authentification", link: '/oscp/mots-de-passe' },
          { text: "Élévation de privilèges Windows", link: '/oscp/privileges-windows' },
          { text: "Élévation de privilèges Linux", link: '/oscp/privileges-linux' },
          { text: "Redirection de ports", link: '/oscp/redirection-ports' },
          { text: "Tunneling", link: '/oscp/tunneling' },
          { text: "Active Directory : fondamentaux", link: '/oscp/ad-theorie' },
          { text: "Active Directory : énumération", link: '/oscp/ad-enumeration' },
          { text: "Active Directory : techniques", link: '/oscp/ad-techniques' },
          { text: "Active Directory : mouvement latéral", link: '/oscp/ad-lateral' },
          { text: "Infrastructures cloud", link: '/oscp/cloud' },
          { text: "Rapports de pentest", link: '/oscp/rapport' },
          { text: "Transfert de fichiers", link: '/oscp/transferts' },
          { text: "Utilitaires", link: '/oscp/utilitaires' },
          { text: "Méthodologie OSCP", link: '/oscp/methodologie' }
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

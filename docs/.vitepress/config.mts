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
          { text: 'Collecte d’informations', link: '/oscp/reconnaissance' },
          { text: 'Analyse de vulnérabilités', link: '/oscp/vulnerabilites' },
          { text: 'Applications web', link: '/oscp/applications-web' },
          { text: 'Attaques côté client', link: '/oscp/attaques-client' },
          { text: 'Évasion antivirus et Metasploit', link: '/oscp/antivirus-metasploit' },
          { text: 'Attaques par mots de passe', link: '/oscp/mots-de-passe' },
          { text: 'Élévation de privilèges Windows', link: '/oscp/privileges-windows' },
          { text: 'Élévation de privilèges Linux', link: '/oscp/privileges-linux' },
          { text: 'Redirections SSH, Socat et netsh', link: '/oscp/redirection-ports' },
          { text: 'Ligolo-ng, Chisel et pivot', link: '/oscp/tunneling' },
          { text: 'Théorie Active Directory', link: '/oscp/ad-theorie' },
          { text: 'Énumération Active Directory', link: '/oscp/ad-enumeration' },
          { text: 'Attaques Active Directory', link: '/oscp/ad-techniques' },
          { text: 'Mouvement latéral Active Directory', link: '/oscp/ad-lateral' },
          { text: 'Infrastructures cloud', link: '/oscp/cloud' },
          { text: 'Rédaction de rapports', link: '/oscp/rapport' },
          { text: 'Transferts Linux et Windows', link: '/oscp/transferts' },
          { text: 'Utilitaires', link: '/oscp/utilitaires' },
          { text: 'Méthodologie', link: '/oscp/methodologie' },
          { text: 'Références', link: '/oscp/references' }
        ]
      },
      {
        text: 'CRTO', link: '/crto/', collapsed: true,
        items: [
          { text: 'Notes', items: [
            { text: 'Windows et contexte de sécurité', link: '/crto/notes/windows' },
            { text: 'Kerberos et Active Directory', link: '/crto/notes/kerberos' },
            { text: 'Cobalt Strike et opérations réseau', link: '/crto/notes/cobalt-strike' },
            { text: 'Identités dans SQL Server', link: '/crto/notes/sql-server' },
            { text: 'Discovery dans Active Directory', link: '/crto/notes/discovery' },
            { text: 'Services Windows et Persistence', link: '/crto/notes/services-persistence' },
            { text: 'Credential Access et User Impersonation', link: '/crto/notes/credential-access' },
            { text: 'Process Injection et Defence Evasion', link: '/crto/notes/processus' },
            { text: 'Active Directory Certificate Services', link: '/crto/notes/adcs' },
            { text: 'Domain Trusts et Forest Trusts', link: '/crto/notes/trusts' }
          ] },
          { text: 'Labs', items: [
            { text: 'Session Windows', link: '/crto/labs/session-windows' },
            { text: 'Session SQL', link: '/crto/labs/session-sql' },
            { text: 'Scénario de délégation', link: '/crto/labs/delegation' },
            { text: 'Interpréter une décision AppLocker', link: '/crto/labs/applocker' },
            { text: 'Relire une demande de certificat', link: '/crto/labs/certificat' }
          ] },
          { text: 'Cheatsheets', items: [
            { text: 'Commandes Windows et SQL', link: '/crto/cheatsheets/identites' },
            { text: 'Journaux et stratégie Windows', link: '/crto/cheatsheets/journaux' }
          ] }
        ]
      }
    ],
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: 'Rechercher', buttonAriaLabel: 'Rechercher dans le guide' },
          modal: {
            noResultsText: 'Aucun résultat pour',
            resetButtonTitle: 'Effacer la recherche',
            backButtonTitle: 'Fermer la recherche',
            displayDetails: 'Afficher les détails',
            footer: {
              selectText: 'pour sélectionner', selectKeyAriaLabel: 'Entrée',
              navigateText: 'pour parcourir', navigateUpKeyAriaLabel: 'Flèche haut',
              navigateDownKeyAriaLabel: 'Flèche bas',
              closeText: 'pour fermer', closeKeyAriaLabel: 'Échap'
            }
          }
        }
      }
    },
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

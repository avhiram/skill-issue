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
      { text: 'Academy', link: 'https://avhiram.github.io/skill-issue/academy/index.html', target: '_self' },
      { text: 'OSINT', link: '/osint/' },
      { text: 'Bug Bounty', link: '/bug-bounty/' },
      { text: 'OSCP', link: '/oscp/' },
      { text: 'CRTO', link: '/crto/' }
    ],
    sidebar: {
      '/academy/': [],
      '/bug-bounty/': [
        { text: 'Parcours Bug Bounty', link: '/bug-bounty/', items: [
          { text: 'Programme et préparation', link: '/bug-bounty/#programme-et-preparation' },
          { text: 'Reconnaissance passive', link: '/bug-bounty/#reconnaissance-passive' },
          { text: 'Cartographie et scan réseau', link: '/bug-bounty/#cartographie-et-scan-reseau' },
          { text: 'Cartographie Web et API', link: '/bug-bounty/#cartographie-web-et-api' },
          { text: 'Tests de vulnérabilités', link: '/bug-bounty/#tests-de-vulnerabilites' },
          { text: 'Validation et preuves', link: '/bug-bounty/#validation-et-preuves' },
          { text: 'IA & Bug Bounty', link: '/bug-bounty/#ia-et-bug-bounty' },
          { text: 'Rapport et signalement', link: '/bug-bounty/#rapport-et-signalement' },
          { text: 'Suivi et prime', link: '/bug-bounty/#suivi-et-prime' }
        ] },
        { text: 'Ressources', items: [
          { text: 'Security Tools', link: '/bug-bounty/ressources#security-tools' },
          { text: 'Browser Extensions', link: '/bug-bounty/ressources#browser-extensions' }
        ] }
      ],
      '/osint/': [
        { text: 'OSINT', link: '/osint/', items: [
          { text: 'Ressources', link: '/osint/' },
          { text: 'Cheatsheet', link: '/osint/cheatsheet' }
        ] }
      ],
      '/': [
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
        text: 'CRTO',
        link: '/crto/',
        collapsed: false,
        items: [
          { text: 'Notes générales', link: '/crto/liham/README' },
          { text: 'Bibliothèque de commandes', link: '/crto/liham/crto-command-library' },
          { text: 'Cobalt Strike · Introduction', link: '/crto/liham/cheatsheets/cobalt-strike-primer' },
          { text: 'Initial Access', link: '/crto/liham/cheatsheets/initial-access' },
          { text: 'Discovery', link: '/crto/liham/cheatsheets/discovery' },
          { text: 'User Impersonation', link: '/crto/liham/cheatsheets/user-impersonation' },
          { text: 'Credential Access', link: '/crto/liham/cheatsheets/credential-access' },
          { text: 'Lateral Movement', link: '/crto/liham/cheatsheets/lateral-movement' },
          { text: 'Defense Evasion', link: '/crto/liham/cheatsheets/defense-evasion' },
          { text: 'AppLocker', link: '/crto/liham/cheatsheets/applocker' },
          { text: 'Privilege Escalation', link: '/crto/liham/cheatsheets/privilege-escalation' },
          { text: 'Post-Exploitation', link: '/crto/liham/cheatsheets/post-exploitation' },
          { text: 'Énumération Post-Exploitation', link: '/crto/liham/cheatsheets/Post-Exploitation-Privilege-Escalation-Enumeration' },
          { text: 'Persistence', link: '/crto/liham/cheatsheets/persistence' },
          { text: 'Elevated Persistence', link: '/crto/liham/cheatsheets/elevated-persistence' },
          { text: 'Pivoting', link: '/crto/liham/cheatsheets/pivoting' },
          { text: 'Kerberos', link: '/crto/liham/cheatsheets/kerberos' },
          { text: 'Domain Dominance', link: '/crto/liham/cheatsheets/domain-dominance' },
          { text: 'Forest & Domain Trusts', link: '/crto/liham/cheatsheets/forest-domain-trusts' },
          { text: 'AD CS', link: '/crto/liham/cheatsheets/adcs' },
          { text: 'Microsoft SQL Server', link: '/crto/liham/cheatsheets/ms-sql-server' },
          {
            text: 'Labs · Opérations',
            collapsed: true,
            items: [
              { text: 'Cobalt Strike · Configuration', link: '/crto/liham/labs/2-Cobalt-Strike-Primer' },
              { text: 'Initial Access', link: '/crto/liham/labs/Initial-Access-lab' },
              { text: 'Defense Evasion · Malleable C2', link: '/crto/liham/labs/defence-evasion-lab-Malleable' },
              { text: 'AppLocker · Challenge', link: '/crto/liham/labs/applocker-challenge' },
              { text: 'Discovery', link: '/crto/liham/labs/Discovery-lab' },
              { text: 'User Impersonation', link: '/crto/liham/labs/User-Impersonation-lab' },
              { text: 'Lateral Movement', link: '/crto/liham/labs/Lateral-Movement-lab' },
              { text: 'Credential Access · Challenge', link: '/crto/liham/labs/credential-access-challenge-commands' },
              { text: 'Privilege Escalation', link: '/crto/liham/labs/Privilege-Escalation-lab' },
              { text: 'Persistence', link: '/crto/liham/labs/Persistence-lab' },
              { text: 'Elevated Persistence', link: '/crto/liham/labs/Elevated-Persistence-lab' },
              { text: 'Pivoting · SOCKS', link: '/crto/liham/labs/pivoting-SOCKS-lab' }
            ]
          },
          {
            text: 'Labs · Active Directory',
            collapsed: true,
            items: [
              { text: 'Kerberos · Challenge', link: '/crto/liham/labs/kerberos-challenge' },
              { text: 'Constrained Delegation', link: '/crto/liham/labs/Constrained-Delegation-kerberos-lab' },
              { text: 'Unconstrained Delegation', link: '/crto/liham/labs/Unconstrained-Delegation-Kerberos-lab' },
              { text: 'Service Name Substitution', link: '/crto/liham/labs/Service-Name-Substitution-Kerberos-lab' },
              { text: 'RBCD', link: '/crto/liham/labs/RBCD-lab' },
              { text: 'S4U2self', link: '/crto/liham/labs/S4U2self-lab' },
              { text: 'Inbound Trusts', link: '/crto/liham/labs/Inbound-Trusts-lab' },
              { text: 'Outbound Trusts', link: '/crto/liham/labs/Outbound-Trusts-lab' },
              { text: 'Parent-Child Trusts', link: '/crto/liham/labs/Parent-Child-Trusts' }
            ]
          },
          {
            text: 'Labs · AD CS & SQL',
            collapsed: true,
            items: [
              { text: 'SQL Servers', link: '/crto/liham/labs/SQL-Servers-lab' },
              { text: 'AD CS · ESC1', link: '/crto/liham/labs/esc1' },
              { text: 'AD CS · ESC8', link: '/crto/liham/labs/esc8' },
              { text: 'Golden Certificates · DPERSIST1', link: '/crto/liham/labs/dpersist1' }
            ]
          },
          { text: 'Consignes de l’examen', link: '/crto/liham/notes/Exam-Instructions' },
          { text: 'Shadow Credentials · Étude de cas', link: '/crto/liham/notes/shadow-credential-to-ransomware-storytime' }
        ]
      }
    ]
    },
    search: {
      provider: 'local',
      options: {
        miniSearch: {
          options: {
            processTerm: (term) => term.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '')
          },
          searchOptions: { boost: { title: 4, titles: 3, text: 1 } }
        },
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
    skipToContentLabel: 'Aller au contenu',
    sidebarMenuLabel: 'Menu',
    returnToTopLabel: 'Retour en haut',
    socialLinks: [],
    editLink: false
  },
  markdown: {
    codeCopyButtonTitle: 'Copier le code',
    theme: { light: 'github-light', dark: 'github-dark-default' },
    config(md) {
      md.use(tabsMarkdownPlugin)
      md.use(githubAlertsPlugin)
      md.use(youtubeEmbedPlugin)
      md.use(lineNumberPlugin)
    }
  }
})

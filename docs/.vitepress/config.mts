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
  transformPageData(pageData) {
    if (pageData.relativePath.startsWith('bug-bounty/')) {
      pageData.frontmatter.buildRevision = process.env.GITHUB_SHA?.slice(0, 12) || 'local'
    }
  },
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
      { text: 'Academy', link: 'https://avhiram.github.io/skill-issue/academy/index.html', target: '_self', activeMatch: '^/academy/' },
      { text: 'OSINT', link: '/osint/' },
      { text: 'Bug Bounty', link: `https://avhiram.github.io/skill-issue/bug-bounty/index.html?v=${process.env.GITHUB_SHA?.slice(0, 12) || 'local'}`, target: '_self', activeMatch: '^/bug-bounty/' },
      { text: 'OSCP', link: '/oscp/' },
      { text: 'CRTO', link: '/crto/' },
      { text: 'CRTP', link: '/crtp/' }
    ],
    sidebar: {
      '/crtp/': [
        { text: 'CRTP', link: '/crtp/', collapsed: true, items: [
          { text: 'Cheatsheet AD', link: '/crtp/cheatsheet' },
          { text: 'Fondamentaux & progression', collapsed: true, items: [
            { text: 'AD Enumeration', link: '/crtp/enumeration' },
            { text: 'Windows PrivEsc', link: '/crtp/windows-privesc' },
            { text: 'Lateral Movement', link: '/crtp/lateral-movement' },
            { text: 'Offensive .NET', link: '/crtp/offensive-dotnet' }
          ] },
          { text: 'Active Directory', collapsed: true, items: [
            { text: 'AD Persistence', link: '/crtp/ad-persistence' },
            { text: 'AD PrivEsc', link: '/crtp/ad-privesc' },
            { text: 'AD Defense', link: '/crtp/defense' }
          ] },
        ] }
      ],
      '/academy/': [],
      '/bug-bounty/': [
        { text: 'Bug Bounty', link: '/bug-bounty/index.html', collapsed: true, items: [
          { text: 'Programme et préparation', link: `https://avhiram.github.io/skill-issue/bug-bounty/preparation.html?v=${process.env.GITHUB_SHA?.slice(0, 12) || 'local'}`, target: '_self' },
          { text: 'Reconnaissance passive', link: '/bug-bounty/reconnaissance' },
          { text: 'Reconnaissance active', link: '/bug-bounty/scan-reseau' },
          { text: 'Cartographie Web et API', link: '/bug-bounty/cartographie-web' },
          { text: 'Mindmap Bug Bounty', link: '/bug-bounty/mindmap-web' },
          { text: 'Tests de vulnérabilités', link: '/bug-bounty/vulnerabilites', collapsed: true, items: [
            { text: 'Subdomain Takeover', link: '/bug-bounty/vulnerabilites#subdomain-takeover' },
            { text: 'Exposition de données', link: '/bug-bounty/vulnerabilites#exposition-de-donnees' },
            { text: 'XSS', link: '/bug-bounty/vulnerabilites#cross-site-scripting-xss' },
            { text: 'SQL Injection', link: '/bug-bounty/vulnerabilites#sql-injection-sqli' },
            { text: 'LFI', link: '/bug-bounty/vulnerabilites#local-file-inclusion-lfi' },
            { text: 'SSRF', link: '/bug-bounty/vulnerabilites#server-side-request-forgery-ssrf' },
            { text: 'CORS', link: '/bug-bounty/vulnerabilites#cross-origin-resource-sharing-cors' },
            { text: 'WordPress', link: '/bug-bounty/vulnerabilites#wordpress' },
            { text: 'Microsoft IIS', link: '/bug-bounty/vulnerabilites#microsoft-iis-et-asp-net' },
            { text: 'React2Shell', link: '/bug-bounty/vulnerabilites#react2shell-cve-2025-55182' },
            { text: 'Authentification et Access Control', link: '/bug-bounty/vulnerabilites#authentification-et-controle-d-acces' },
            { text: 'Contrôles côté serveur', link: '/bug-bounty/vulnerabilites#controles-cote-serveur' },
            { text: 'Contrôles côté client', link: '/bug-bounty/vulnerabilites#controles-cote-client' },
            { text: 'HTTP, cache et IA', link: '/bug-bounty/vulnerabilites#http-cache-et-ia' },
            { text: 'Pratique PortSwigger', link: '/bug-bounty/vulnerabilites#pratique-portswigger' }
          ] },
          { text: 'Validation et preuves', link: '/bug-bounty/validation' },
          { text: 'Rapport et signalement', link: '/bug-bounty/rapport' },
          { text: 'Suivi et prime', link: '/bug-bounty/suivi' }
        ] },
        { text: 'Espaces complémentaires', collapsed: true, items: [
          { text: 'IA & Bug Bounty', link: '/bug-bounty/ia' },
          { text: 'Security Tools', link: '/bug-bounty/ressources#security-tools' },
          { text: 'Browser Extensions', link: '/bug-bounty/ressources#browser-extensions' }
        ] }
      ],
      '/osint/': [
        { text: 'OSINT', link: '/osint/', collapsed: true, items: [
          { text: 'Ressources', link: '/osint/' },
          { text: 'Cheatsheet', link: '/osint/cheatsheet' }
        ] }
      ],
      '/': [
      {
        text: 'OSCP',
        link: '/oscp/',
        collapsed: true,
        items: [
          { text: 'Reconnaissance', collapsed: true, items: [
            { text: 'Collecte d’informations', link: '/oscp/reconnaissance' },
            { text: 'Analyse de vulnérabilités', link: '/oscp/vulnerabilites' }
          ] },
          { text: 'Exploitation', collapsed: true, items: [
            { text: 'Applications web', link: '/oscp/applications-web' },
            { text: 'Attaques côté client', link: '/oscp/attaques-client' },
            { text: 'Évasion antivirus et Metasploit', link: '/oscp/antivirus-metasploit' },
            { text: 'Attaques par mots de passe', link: '/oscp/mots-de-passe' }
          ] },
          { text: 'Élévation de privilèges', collapsed: true, items: [
            { text: 'Élévation de privilèges Windows', link: '/oscp/privileges-windows' },
            { text: 'Élévation de privilèges Linux', link: '/oscp/privileges-linux' }
          ] },
          { text: 'Pivoting & transferts', collapsed: true, items: [
            { text: 'Redirections SSH, Socat et netsh', link: '/oscp/redirection-ports' },
            { text: 'Ligolo-ng, Chisel et pivot', link: '/oscp/tunneling' },
            { text: 'Transferts Linux et Windows', link: '/oscp/transferts' }
          ] },
          { text: 'Active Directory', collapsed: true, items: [
            { text: 'Active Directory', link: '/oscp/active-directory' },
            { text: 'Théorie Active Directory', link: '/oscp/ad-theorie' },
            { text: 'Énumération Active Directory', link: '/oscp/ad-enumeration' },
            { text: 'Attaques Active Directory', link: '/oscp/ad-techniques' },
            { text: 'Mouvement latéral Active Directory', link: '/oscp/ad-lateral' },
            { text: 'Mindmap AD', link: '/oscp/mindmap-ad' }
          ] },
          { text: 'Ressources', collapsed: true, items: [
            { text: 'Infrastructures cloud', link: '/oscp/cloud' },
            { text: 'Utilitaires', link: '/oscp/utilitaires' },
            { text: 'Méthodologie', link: '/oscp/methodologie' },
            { text: 'Rédaction de rapports', link: '/oscp/rapport' },
            { text: 'Références', link: '/oscp/references' },
            { text: 'Mindmaps', link: '/oscp/mindmaps' }
          ] },
        ]
      },
      {
        text: 'CRTO',
        link: '/crto/',
        collapsed: true,
        items: [
          { text: 'Accès rapide', collapsed: true, items: [
            { text: 'Notes générales', link: '/crto/liham/README' },
            { text: 'Bibliothèque de commandes', link: '/crto/liham/crto-command-library' }
          ] },
          { text: 'Opérations · fondamentaux', collapsed: true, items: [
            { text: 'Cobalt Strike · Introduction', link: '/crto/liham/cheatsheets/cobalt-strike-primer' },
            { text: 'Initial Access', link: '/crto/liham/cheatsheets/initial-access' },
            { text: 'Discovery', link: '/crto/liham/cheatsheets/discovery' },
            { text: 'User Impersonation', link: '/crto/liham/cheatsheets/user-impersonation' },
            { text: 'Credential Access', link: '/crto/liham/cheatsheets/credential-access' }
          ] },
          { text: 'Opérations · progression', collapsed: true, items: [
            { text: 'Lateral Movement', link: '/crto/liham/cheatsheets/lateral-movement' },
            { text: 'Defense Evasion', link: '/crto/liham/cheatsheets/defense-evasion' },
            { text: 'AppLocker', link: '/crto/liham/cheatsheets/applocker' },
            { text: 'Privilege Escalation', link: '/crto/liham/cheatsheets/privilege-escalation' },
            { text: 'Post-Exploitation', link: '/crto/liham/cheatsheets/post-exploitation' },
            { text: 'Énumération Post-Exploitation', link: '/crto/liham/cheatsheets/Post-Exploitation-Privilege-Escalation-Enumeration' },
            { text: 'Persistence', link: '/crto/liham/cheatsheets/persistence' },
            { text: 'Elevated Persistence', link: '/crto/liham/cheatsheets/elevated-persistence' },
            { text: 'Pivoting', link: '/crto/liham/cheatsheets/pivoting' }
          ] },
          { text: 'Active Directory & SQL', collapsed: true, items: [
            { text: 'Kerberos', link: '/crto/liham/cheatsheets/kerberos' },
            { text: 'Domain Dominance', link: '/crto/liham/cheatsheets/domain-dominance' },
            { text: 'Forest & Domain Trusts', link: '/crto/liham/cheatsheets/forest-domain-trusts' },
            { text: 'AD CS', link: '/crto/liham/cheatsheets/adcs' },
            { text: 'Microsoft SQL Server', link: '/crto/liham/cheatsheets/ms-sql-server' }
          ] },
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
          { text: 'Examen & études de cas', collapsed: true, items: [
            { text: 'Consignes de l’examen', link: '/crto/liham/notes/Exam-Instructions' },
            { text: 'Shadow Credentials · Étude de cas', link: '/crto/liham/notes/shadow-credential-to-ransomware-storytime' }
          ] }
        ]
      }
    ]
    },
    search: {
      provider: 'local',
      options: {
        miniSearch: {
          options: {
            processTerm: (term) => {
              const value = term.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '')
              const equivalents: Record<string, string> = {
                privesc: 'privilege', privileges: 'privilege', privilege: 'privilege',
                elevation: 'privilege', escalation: 'privilege',
                enum: 'enumeration', enumeration: 'enumeration',
                reconnaissance: 'reconnaissance', recon: 'reconnaissance',
                tunnelling: 'tunneling', tunneling: 'tunneling',
                lateral: 'lateral', lateraux: 'lateral', laterale: 'lateral',
                movements: 'movement', mouvement: 'movement', mouvements: 'movement',
                vulnerabilites: 'vulnerability', vulnerabilite: 'vulnerability', vulnerabilities: 'vulnerability',
                transferts: 'transfer', transfert: 'transfer', transfers: 'transfer'
              }
              return equivalents[value] || value
            }
          },
          searchOptions: { prefix: true, fuzzy: 0.15, boost: { title: 5, titles: 3, text: 2 } }
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

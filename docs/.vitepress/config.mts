import { defineConfig } from 'vitepress'
import { copyFile, readdir, writeFile } from 'node:fs/promises'
import { join } from 'node:path'
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
  async buildEnd(site) {
    // Only documentation and its local runtime, not personal documents or large media.
    const paths: string[] = []
    async function walk(dir: string, prefix = '') {
      for (const entry of await readdir(dir, { withFileTypes: true })) {
        const rel = prefix + entry.name
        if (entry.isDirectory()) {
          if (!/^(credentials|institutions|justificatifs|audit|images|database|membres)$/.test(entry.name)) await walk(join(dir, entry.name), rel + '/')
        } else if (/\.(html|js|css|json|woff2?|svg)$/i.test(rel) && !/^(offline-sw\.js|offline-index\.json)$/.test(rel)) {
          paths.push(rel)
        }
      }
    }
    await copyFile(join(site.srcDir, 'public', 'offline-sw.js'), join(site.outDir, 'offline-sw.js'))
    await walk(site.outDir)
    if (paths.some(path => /^crto\/liham\/|^assets\/crto_liham_/i.test(path))) {
      throw new Error('CRTO: contenu privé détecté dans le build public.')
    }
    await writeFile(join(site.outDir, 'offline-index.json'), JSON.stringify({ revision: process.env.GITHUB_SHA || 'local', files: paths.sort() }))
  },
  appearance: 'force-dark',
  // Les notes CRTO restent dans les sources, hors du site public.
  srcExclude: [
    'crto/liham/**',
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
      {
        text: 'Accès gratuit',
        items: [
          { text: 'Academy', link: 'https://avhiram.github.io/skill-issue/academy/index.html', target: '_self' },
          { text: 'eJPT', link: '/ejpt/' },
          { text: 'OSINT', link: '/osint/' },
          { text: 'Bug Bounty', link: `https://avhiram.github.io/skill-issue/bug-bounty/index.html?v=${process.env.GITHUB_SHA?.slice(0, 12) || 'local'}`, target: '_self' },
          { text: 'OSCP', link: '/oscp/' },
          { text: 'CRTP', link: '/crtp/' }
        ]
      },
      {
        text: 'Accès membre',
        items: [
          { text: 'Espace membre', link: '/membres/' },
          { text: 'CRTO · Accès réservé', link: '/crto/' }
        ]
      }
    ],
    sidebar: {
      '/ejpt/': [
        { text: 'Junior Penetration Tester', link: '/ejpt/' },
        { text: 'Cours', link: '/ejpt/cours', collapsed: true, items: [
          { text: 'Prérequis du pentest', link: '/ejpt/cours#penetration-testing-prerequisites' },
          { text: 'Méthodologie et audit', link: '/ejpt/cours#assessment-methodologies' },
          { text: 'Pentest système et réseau', link: '/ejpt/cours#hostnetwork-penetration-testing' },
          { text: 'Pentest Web', link: '/ejpt/cours#webapp-penetration-testing' },
          { text: 'Labs et préparation', link: '/ejpt/cours#exam-preparation-labs' }
        ] },
        { text: 'Cheatsheet', link: '/ejpt/cheatsheet' }
      ],
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
      '/': [],
      '/oscp/': [
      {
        text: 'OSCP',
        link: '/oscp/',
        collapsed: false,
        items: [
          { text: 'Exam Mode', link: '/oscp/exam', collapsed: true, items: [{ text: 'Nmap', link: '/oscp/exam-nmap' }] },
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
      }
      ],
      '/crto/': []
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
                transferts: 'transfer', transfert: 'transfer', transfers: 'transfer', transfer: 'transfer',
                permissions: 'permission', permission: 'permission', droits: 'permission', rights: 'permission',
                fichiers: 'file', fichier: 'file', files: 'file', file: 'file',
                dossiers: 'directory', dossier: 'directory', directories: 'directory', directory: 'directory',
                supprimer: 'delete', suppression: 'delete', effacer: 'delete', delete: 'delete',
                copier: 'copy', copie: 'copy', copy: 'copy',
                telecharger: 'download', telechargement: 'download', download: 'download',
                rechercher: 'search', recherche: 'search', search: 'search',
                utilisateurs: 'user', utilisateur: 'user', users: 'user', user: 'user'
              }
              return Object.prototype.hasOwnProperty.call(equivalents, value) ? equivalents[value] : value
            }
          },
          searchOptions: {
            prefix: true, fuzzy: 0.15, boost: { title: 5, titles: 3, text: 2 },
            filter: (result) => {
              if (typeof document === 'undefined') return true
              const path = String(result.id).split('#')[0].replace(/^\/skill-issue\//, '/')
              if (/^\/?crto(?:\/|$)/i.test(path)) return false
              const scope = document.documentElement.dataset.skillSearchScope
              if (!scope || !/^(academy|osint|bug-bounty|oscp|crtp)$/.test(scope)) return true
              return path.startsWith('/' + scope + '/') || path.startsWith(scope + '/') ||
                path === '/' + scope || path === scope
            }
          }
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

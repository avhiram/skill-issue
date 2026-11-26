// Configuration originale, conservée pour le futur espace privé.
export default {
      '/crto/': [
      {
        text: 'CRTO',
        link: '/crto/',
        collapsed: false,
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
}

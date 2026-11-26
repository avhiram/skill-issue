type Link = { label: string; path: string }
export const examGroups: {title:string; links:Link[]}[] = [
  {
    "title": "Reconnaissance",
    "links": [
      {
        "label": "Nmap",
        "path": "/oscp/exam-nmap"
      },
      {
        "label": "Ports et services",
        "path": "/oscp/exam-ports"
      },
      {
        "label": "Collecte d’informations",
        "path": "/oscp/reconnaissance"
      },
      {
        "label": "Analyse de vulnérabilités (NSE)",
        "path": "/oscp/vulnerabilites#nmap-nse"
      }
    ]
  },
  {
    "title": "Analyse selon la cible",
    "links": [
      {
        "label": "Méthodologie",
        "path": "/oscp/methodologie"
      },
      {
        "label": "Web",
        "path": "/oscp/applications-web"
      },
      {
        "label": "Mots de passe",
        "path": "/oscp/mots-de-passe"
      },
      {
        "label": "Côté client",
        "path": "/oscp/attaques-client"
      }
    ]
  },
  {
    "title": "Active Directory",
    "links": [
      {
        "label": "Énumération",
        "path": "/oscp/ad-enumeration"
      },
      {
        "label": "Techniques AD",
        "path": "/oscp/ad-techniques"
      },
      {
        "label": "Mouvement latéral",
        "path": "/oscp/ad-lateral"
      },
      {
        "label": "Fondamentaux AD",
        "path": "/oscp/ad-theorie"
      }
    ]
  },
  {
    "title": "Shell et systèmes",
    "links": [
      {
        "label": "Shell interactif (TTY)",
        "path": "/oscp/exam-shell"
      },
      {
        "label": "Linux",
        "path": "/oscp/privileges-linux"
      },
      {
        "label": "Windows",
        "path": "/oscp/privileges-windows"
      },
      {
        "label": "Transferts",
        "path": "/oscp/transferts"
      }
    ]
  },
  {
    "title": "Réseau",
    "links": [
      {
        "label": "Ligolo-ng et pivot",
        "path": "/oscp/tunneling"
      },
      {
        "label": "Redirections de ports",
        "path": "/oscp/redirection-ports"
      }
    ]
  },
  {
    "title": "Preuves et rapport",
    "links": [
      {
        "label": "Rapport",
        "path": "/oscp/rapport"
      },
      {
        "label": "Consignes OffSec",
        "path": "/oscp/references"
      }
    ]
  },
  {
    "title": "Références complémentaires",
    "links": [
      {
        "label": "Utilitaires",
        "path": "/oscp/utilitaires"
      },
      {
        "label": "Mindmaps",
        "path": "/oscp/mindmaps"
      },
      {
        "label": "Mindmap AD",
        "path": "/oscp/mindmap-ad"
      }
    ]
  }
]

type Link = { label: string; path: string }
export const examGroups: {title:string; links:Link[]}[] = [
  {
    "title": "Reconnaissance",
    "links": [
      {
        "label": "Scan Nmap",
        "path": "/oscp/exam-nmap"
      },
      {
        "label": "Services par port",
        "path": "/oscp/exam-ports"
      },
      {
        "label": "Web",
        "path": "/oscp/applications-web"
      },
      {
        "label": "Mots de passe",
        "path": "/oscp/mots-de-passe"
      }
    ]
  },
  {
    "title": "Systèmes",
    "links": [
      {
        "label": "Shell interactif",
        "path": "/oscp/exam-shell"
      },
      {
        "label": "Transferts",
        "path": "/oscp/transferts"
      },
      {
        "label": "Linux",
        "path": "/oscp/privileges-linux"
      },
      {
        "label": "Windows",
        "path": "/oscp/privileges-windows"
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
      }
    ]
  },
  {
    "title": "Réseau",
    "links": [
      {
        "label": "Ligolo-ng",
        "path": "/oscp/tunneling"
      },
      {
        "label": "Redirections",
        "path": "/oscp/redirection-ports"
      }
    ]
  },
  {
    "title": "Rapport",
    "links": [
      {
        "label": "Preuves et rapport",
        "path": "/oscp/rapport"
      }
    ]
  },
  {
    "title": "Références",
    "links": [
      {
        "label": "Consignes OffSec",
        "path": "/oscp/references"
      },
      {
        "label": "Méthodologie complète",
        "path": "/oscp/methodologie"
      },
      {
        "label": "Collecte d’informations",
        "path": "/oscp/reconnaissance"
      },
      {
        "label": "NSE",
        "path": "/oscp/vulnerabilites#nmap-nse"
      },
      {
        "label": "Côté client",
        "path": "/oscp/attaques-client"
      },
      {
        "label": "Fondamentaux AD",
        "path": "/oscp/ad-theorie"
      },
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

// Keep the original content routes available for heading indexing.
export const examIndexes: Record<string,string> = {
  "/oscp/applications-web": "/oscp/exam-applications-web",
  "/oscp/mots-de-passe": "/oscp/exam-mots-de-passe",
  "/oscp/transferts": "/oscp/exam-transferts",
  "/oscp/privileges-linux": "/oscp/exam-privileges-linux",
  "/oscp/privileges-windows": "/oscp/exam-privileges-windows",
  "/oscp/ad-enumeration": "/oscp/exam-ad-enumeration",
  "/oscp/ad-techniques": "/oscp/exam-ad-techniques",
  "/oscp/ad-lateral": "/oscp/exam-ad-lateral",
  "/oscp/tunneling": "/oscp/exam-tunneling",
  "/oscp/redirection-ports": "/oscp/exam-redirection-ports",
  "/oscp/rapport": "/oscp/exam-rapport",
  "/oscp/references": "/oscp/exam-references",
  "/oscp/methodologie": "/oscp/exam-methodologie",
  "/oscp/reconnaissance": "/oscp/exam-reconnaissance",
  "/oscp/vulnerabilites#nmap-nse": "/oscp/exam-vulnerabilites",
  "/oscp/attaques-client": "/oscp/exam-attaques-client",
  "/oscp/ad-theorie": "/oscp/exam-ad-theorie",
  "/oscp/utilitaires": "/oscp/exam-utilitaires",
  "/oscp/mindmaps": "/oscp/exam-mindmaps",
  "/oscp/mindmap-ad": "/oscp/exam-mindmap-ad"
}
export const examIndexPath = (path:string) => examIndexes[path] ?? path

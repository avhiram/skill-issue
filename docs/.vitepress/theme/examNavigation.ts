type Link = { label: string; path: string }
export const examGroups: {title:string; links:Link[]}[] = [
  {title:'Reconnaissance',links:[
    {label:'Nmap',path:'/oscp/exam-nmap'},
    {label:'Ports et services',path:'/oscp/reconnaissance#services-par-port'}
  ]},
  {title:'Analyse selon la cible',links:[
    {label:'Méthodologie',path:'/oscp/methodologie'},
    {label:'Web',path:'/oscp/applications-web'}
  ]},
  {title:'Active Directory',links:[
    {label:'Énumération',path:'/oscp/ad-enumeration'},
    {label:'Techniques AD',path:'/oscp/ad-techniques'},
    {label:'Mouvement latéral',path:'/oscp/ad-lateral'}
  ]},
  {title:'Systèmes',links:[
    {label:'Linux',path:'/oscp/privileges-linux'},
    {label:'Windows',path:'/oscp/privileges-windows'},
    {label:'Transferts',path:'/oscp/transferts'}
  ]},
  {title:'Rapport',links:[
    {label:'Preuves et rapport',path:'/oscp/rapport'}
  ]}
]

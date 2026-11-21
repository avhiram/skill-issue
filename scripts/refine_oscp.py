#!/usr/bin/env python3
"""Format OSCP notes for fast reading while retaining executable source snippets."""
from pathlib import Path
import re
import json

D=Path("docs/src/oscp")
B=chr(96)
F=B*3
GENERIC="Commandes, paramètres et exemples associés à cette technique."
NAMES={
 "Overview":"Vue d'ensemble","Authentication":"Authentification",
 "Credential Storage & Hash Dumping":"Identifiants et empreintes",
 "Common Attack Vectors":"Vecteurs d'attaque courants","Lateral Movement":"Mouvement latéral",
 "Persistence":"Persistance","Run Category of Scripts":"Catégories des scripts NSE",
 "PowerShell Functions":"Fonctions PowerShell","FingerPrinting":"Identification des technologies",
 "Directory Discovery":"Recherche de répertoires","File Discovery":"Recherche de fichiers",
 "Git Exposed":"Dépôt Git exposé","Send Emails":"Envoi de courriels",
 "Normal Email":"Courriel simple","Email with Authentication":"Courriel avec authentification",
 "Brute-Force":"Essais de mots de passe","Spraying Credentials":"Password spraying",
 "Crack Files":"Analyse des empreintes","Office Files":"Fichiers Office","PDF Files":"Fichiers PDF",
 "ZIP Files":"Archives ZIP","HTTP POST Login Form":"Connexion HTTP POST",
 "HTTP GET (Basic Authentication)":"Authentification HTTP Basic",
 "Calculate cracking time":"Estimer le temps de calcul",
 "Hashcat Formats for Cracking":"Modes de hachage Hashcat",
 "Password Managers":"Gestionnaires de mots de passe",
 "SSH Passphrases":"Phrases secrètes SSH","Linux Users Hashes":"Empreintes Linux",
 "Mimikatz Commands":"Commandes Mimikatz","Do Not Require Credentials":"Sans identifiants",
 "Require Credentials":"Avec identifiants","PowerShell Goldmine (Logs)":"Journaux PowerShell",
 "Abusing Privileges":"Risques liés aux privilèges",
 "Check Assigned Privileges":"Vérifier les privilèges",
 "Token Privileges Table":"Tableau des privilèges",
 "Service Binary Hijacking":"Binaire de service vulnérable",
 "Service DLL Hijacking":"Chargement de DLL par un service",
 "Unquoted Service Paths":"Chemins de services sans guillemets",
 "Basic and Main Checks":"Vérifications principales",
 "Additional Optional Checks":"Vérifications complémentaires",
 "Internal Services":"Services internes",
 "Display Active Network Connections":"Connexions réseau actives",
 "Inspecting Service Footprints":"Examiner les services",
 "Setuid Binaries and Capabilities":"Binaires SUID et capacités",
 "Setuid Binaries":"Binaires SUID",
 "Table of Capabilities":"Capacités Linux",
 "Abusing SUDO":"Risques liés à sudo",
 "Kernel Exploitations":"Vulnérabilités du noyau",
 "Wildcard Basics":"Fonctionnement des caractères génériques",
 "Initial Recon with Nmap":"Reconnaissance avec Nmap",
 "Kerberos Énumération (Port 88)":"Énumération Kerberos (port 88)",
 "LDAP Énumération (Port 389/636)":"Énumération LDAP (ports 389 et 636)",
 "SMB/NetBIOS Énumération (Port 445)":"Énumération SMB (port 445)",
 "WinRM Énumération and Access (Port 5985)":"Énumération WinRM (port 5985)",
 "Extracting and Cracking Password Hashes":"Analyse des empreintes de mots de passe",
 "Common SPNs for Service Accounts":"SPN des comptes de service",
 "Silver Tickets":"Tickets Silver","Golden Tickets":"Tickets Golden",
 "Cached AD Credentials":"Identifiants AD en cache",
 "NTLM Authentication":"Authentification NTLM",
 "Kerberos Authentication":"Authentification Kerberos",
 "Running the Script":"Exécuter le script",
 "Source Code of the Script":"Code source du script",
 "From Kali":"Depuis Kali","From Windows":"Depuis Windows",
 "Port Redirection with Socat":"Redirection avec Socat",
 "SSH Local Redirection de ports":"Redirection SSH locale",
 "SSH Dynamic Redirection de ports":"Redirection SSH dynamique",
 "SSH Remote Redirection de ports":"Redirection SSH distante",
 "Forward Dynamic SOCKS Proxy":"Proxy SOCKS dynamique",
 "Reverse Dynamic SOCKS Proxy":"Proxy SOCKS inverse",
 "Tools for Note-Taking and Report Writing":"Prise de notes et rapports",
 "Recommended Tools":"Outils recommandés",
 "Best Practices":"Bonnes pratiques",
 "Capturing Screenshots":"Captures d'écran",
 "Proof of Concept (PoC)":"Preuve de concept (PoC)",
 "Common Mistakes to Avoid":"Erreurs à éviter",
 "RDP shared folder":"Dossier partagé RDP",
 "HTTP Requests":"Requêtes HTTP","Send a File":"Envoyer un fichier",
 "Reverse Shells":"Shells inversés",
 "Upgrade Shells":"Améliorer le shell interactif",
 "General Methodology":"Méthodologie générale",
 "Specific Services Strategy":"Vérifications par service"
}
PHRASES=[
 ("Information Gathering","Reconnaissance"),("Vulnerability Scanning","Analyse de vulnérabilités"),
 ("Directory Enumeration","Énumération des répertoires"),
 ("User Enumeration","Énumération des utilisateurs"),
 ("Groups Enumeration","Énumération des groupes"),
 ("Privilege Escalation","Élévation de privilèges"),
 ("Password Attacks","Attaques sur les mots de passe"),
 ("Port Forwarding","Redirection de ports"),
 ("File Transfers","Transferts de fichiers"),
 ("Command Execution","Exécution de commandes"),
 ("Authentication","Authentification"),
 ("Enumeration","Énumération"),("Discovery","Découverte"),
 ("Commands","Commandes"),("Basic","De base"),("Advanced","Avancé"),
 ("Additional","Complémentaire"),("Scanning","Scan")
]
NSE={"auth":"authentification","broadcast":"diffusion","brute":"essais de mots de passe",
 "default":"scripts par défaut","discovery":"découverte","exploit":"tests d'exploitation",
 "fuzzer":"fuzzing","malware":"malwares","safe":"non intrusifs selon NSE",
 "version":"versions","vuln":"vulnérabilités"}
SWITCH={"-sU":"scan UDP","-sT":"TCP connect","-sS":"SYN",
 "-sn":"découverte d'hôtes","-sV":"versions de service",
 "-O":"détection du système","-oN":"sortie texte",
 "-oG":"sortie grepable","--local-auth":"authentification locale",
 "--max-retries":"limite des tentatives","--delay":"délai"}
MODES={"0":"MD5","100":"SHA-1","1000":"NTLM","5500":"NetNTLMv1","5600":"NetNTLMv2",
 "3200":"bcrypt","13100":"Kerberos TGS-REP","18200":"Kerberos AS-REP"}
TOOLS=set("nc crackmapexec enum4linux kerbrute ldapsearch strings hashcat john "
 "impacket-GetNPUsers GetNPUsers.py creds office2john ligolo Ligolo-ng proxychains "
 "xfreerdp plink.exe".split())
ONE_WORD_COMMAND=set("whoami hostname systeminfo id pwd mount lsblk lsmod ipconfig "
 "ifconfig netstat uname groups env uptime ps df free".split())
REF_DESC={"ssh-rsa":"clé SSH RSA ancienne","diffie-hellman-group1-sha1":"échange de clés SSH ancien",
 "domain.com":"exemple de domaine","DONT_REQ_PREAUTH":"indicateur Kerberos",
 "DC-Replication-Get-Changes":"droit de réplication AD",".git":"métadonnées Git"}
COMMENTS={"# Specify a different whois server":"# Utiliser un serveur WHOIS précis",
 "# UDP instead of TCP":"# Utiliser UDP plutôt que TCP",
 "# Listen for an incoming connection rather than initiate connection":"# Attendre une connexion entrante",
 "# Continue listening for connections after first client has disconnected":"# Rester en écoute après la première connexion",
 "# Basic SSH Service Scan":"# Examiner le service SSH",
 "# Enumerate SSH Version":"# Identifier la version SSH",
 "# Detect Weak SSH Encryption Algorithms":"# Examiner les algorithmes SSH anciens",
 "# List domain users":"# Énumérer les utilisateurs du domaine",
 "# List domain groups":"# Énumérer les groupes du domaine",
 "# Get Naming Contexts":"# Afficher les contextes de nommage LDAP",
 "# Download a Single File":"# Télécharger un fichier",
 "# Download Multiple Files":"# Télécharger plusieurs fichiers"}
def fr(s):
 if s in NAMES: return NAMES[s]
 for en,fr in sorted(PHRASES,key=lambda x:-len(x[0])):
  s=re.sub(r"\b"+re.escape(en)+r"\b",fr,s,flags=re.I)
 return s
def is_ref(code):
 x=code.strip()
 if not x or "\n" in x or len(x)>110 or x in ONE_WORD_COMMAND: return False
 return bool(re.fullmatch(r"-{1,2}\w[\w.-]*",x)
   or re.fullmatch(r"[A-Za-z0-9._/+:-]{1,50}",x)
   or re.match(r"^(site:|intitle:|filetype:|ext:)",x,re.I))
def purpose(code,subject):
 lines=[z.strip() for z in code.splitlines() if z.strip() and not z.strip().startswith(("#","//")) and z.strip()!="or"]
 s=(lines[0] if lines else code.strip()).removeprefix("sudo ").lower()
 if s.startswith("nmap "):
  if "--script-help" in s:return "Consulter la documentation du script Nmap."
  if "--script" in s:return "Examiner le service avec les scripts NSE sélectionnés."
  if "-su" in s:return "Examiner les ports UDP."
  if "-sv" in s:return "Identifier les versions des services."
  if "-sn" in s:return "Identifier les hôtes actifs."
  if "-p-" in s:return "Scanner l'ensemble des ports."
  return "Examiner les ports et les services avec Nmap."
 if s.startswith(("host ","dig ","nslookup ","dnsrecon ","dnsenum ")):return "Interroger les enregistrements DNS."
 if s.startswith("whois "):return "Consulter les informations d'enregistrement du domaine."
 if s.startswith("ssh "):
  if "kexalgorithms" in s or "hostkeyalgorithms" in s:return "Tester des algorithmes SSH anciens."
  if " -i " in s:return "Se connecter avec une clé SSH privée."
  if "'whoami'" in s or '"whoami"' in s:return "Exécuter une commande distante via SSH."
  return "Ouvrir une connexion SSH avec les paramètres indiqués."
 if s.startswith(("scp ","sftp ","rsync ")):return "Transférer des fichiers via SSH."
 if s.startswith(("nc ","netcat ")):
  if " -l" in s:return "Ouvrir un port d'écoute avec Netcat."
  return "Tester ou établir une connexion réseau avec Netcat."
 if s.startswith("rustscan "):return "Identifier rapidement les ports accessibles."
 if s.startswith(("curl ","wget ")):return "Récupérer une ressource distante ou une réponse HTTP."
 if s.startswith(("ffuf ","gobuster ","feroxbuster ","dirsearch ","dirb ","wfuzz ")):return "Rechercher des chemins ou paramètres web."
 if s.startswith("ldapsearch "):return "Interroger les objets de l'annuaire LDAP."
 if s.startswith(("get-ad","get-net","resolve-dnsname","test-netconnection")):return "Examiner les informations AD ou réseau en PowerShell."
 if s.startswith(("crackmapexec ","netexec ")):return "Examiner le service distant avec les paramètres fournis."
 if s.startswith(("rpcclient ","enum4linux ","smbclient ","smbmap ")):return "Énumérer les informations SMB ou RPC."
 if s.startswith(("hydra ","medusa ")):return "Vérifier des identifiants dans un environnement autorisé."
 if s.startswith(("hashcat ","john ")):return "Analyser une empreinte avec le mode indiqué."
 if s.startswith(("ssh2john ","zip2john ","office2john ","pdf2john ")):return "Préparer une empreinte pour John the Ripper."
 if s.startswith(("find ","grep ","awk ","sed ")):return "Rechercher ou filtrer des données."
 if s.startswith(("whoami","systeminfo","ipconfig","get-local")):return "Afficher des informations de la session ou du système."
 if s.startswith(("ping ","traceroute ","tracert ")):return "Vérifier la connectivité réseau."
 match=re.match(r"^[./\w-]+",s)
 if match and len(match.group(0))<30:return "Commande "+B+match.group(0)+B+" pour la rubrique « "+subject+" »."
 return "Exemple technique pour la rubrique « "+subject+" »."
def fmtrefs(values,subject):
 keep=list(dict.fromkeys(x for x in values if x not in TOOLS))
 if not keep:return []
 parts=[]
 for x in keep:
  desc=NSE.get(x) or SWITCH.get(x) or (MODES.get(x) if "hash" in subject.lower() or "mots" in subject.lower() else None) or REF_DESC.get(x)
  parts.append(B+x.replace(B,"")+B+(" ("+desc+")" if desc else ""))
 label="Catégories NSE" if sum(x in NSE for x in keep)>=4 else "Paramètres et repères"
 lines=["", "**"+label+" :**"]
 for n in range(0,len(parts),4):lines.append(" · ".join(parts[n:n+4])+"  ")
 return lines+[""]
def process(source,slug):
 if "<!-- refined-oscp -->" in source:return source,{}
 lines=source.splitlines();output=[];refs=[];title=slug.replace("-"," ");bold=None
 before=after=0;replaced=0
 def flush():
  nonlocal replaced
  if refs:
   replaced+=len(refs)
   output.extend(fmtrefs(refs,title));refs.clear()
 i=0
 while i<len(lines):
  line=lines[i];s=line.strip()
  m=re.match(r"^(#{2,5})\s+(.+)$",s)
  if m:
   flush()
   if bold:output.extend(["","**"+fr(bold)+"**",""]);bold=None
   title=fr(m.group(2));output.extend(["",m.group(1)+" "+title,""])
   i+=1;continue
  if s==GENERIC:i+=1;continue
  if re.fullmatch(r"\*\*[^*]{2,145}\*\*",s):
   flush()
   if bold:output.extend(["","**"+fr(bold)+"**",""])
   bold=s[2:-2];i+=1;continue
  if s.startswith(F):
   end=i+1
   while end<len(lines) and lines[end].strip()!=F:end+=1
   if end==len(lines):output.append(line);i+=1;continue
   code="\n".join(lines[i+1:end]);lang=s[3:];before+=1;i=end+1
   if is_ref(code):
    refs.append(code.strip());continue
   flush()
   if not code.strip():continue
   if bold:output.extend(["","**"+fr(bold)+"**",""]);bold=None
   output.extend(["",purpose(code,title),""])
   if lang=="text" and re.match(r"^(?:sudo |nmap |nc |ssh |scp |curl |wget |ldapsearch |ftp |dig |nslookup |hashcat |john |python3? |impacket-|hydra |crackmapexec |rustscan )",code.strip(),re.I):lang="bash"
   if lang=="text" and re.match(r"^(?:Get-|Set-|Invoke-|New-|Test-|Resolve-DnsName)",code.strip(),re.I):lang="powershell"
   for en,frtext in COMMENTS.items():code=code.replace(en,frtext)
   code=re.sub(r"(?m)^\s*or\s*$","# Autre possibilité",code)
   output.extend([F+lang,code,F,""]);after+=1;continue
  if s:
   flush()
   if bold:output.extend(["","**"+fr(bold)+"**",""]);bold=None
   output.append(line)
  elif not output or output[-1]!="":output.append("")
  i+=1
 flush()
 if bold:output.extend(["","**"+fr(bold)+"**",""])
 result="\n".join(output)
 result=re.sub(r"\n{4,}","\n\n\n",result)
 result=re.sub(r"(?m)^#{2,5}\s+[^\n]+\n(?:\s*\n)*(?=^#{2,5}\s+|^---\s*$|\Z)","",result)
 return result+"\n\n<!-- refined-oscp -->\n",{"source_blocks":before,"remaining_blocks":after,"compact_fragments":replaced}
def main():
 audit={}
 for f in sorted(D.glob("*.md")):
  if f.stem in ("index","cloud","references","ad-theorie"):continue
  src=f.read_text(encoding="utf-8");new,stat=process(src,f.stem)
  f.write_text(new,encoding="utf-8");audit[f.stem]=stat
 theory=D/"ad-theorie.md"
 theory.write_text("""---
title: "OSCP · Active Directory : fondamentaux"
description: "Comprendre les objets AD et les mécanismes d'authentification."
---

# Active Directory : fondamentaux

Les concepts essentiels avant de commencer l'énumération du domaine.

## Domaine et contrôleur de domaine

Le domaine rassemble comptes, ordinateurs, groupes et droits. Le contrôleur de domaine (DC) fournit notamment les services LDAP et Kerberos.

Exemple de domaine : domain.com.

## Authentification

- Kerberos : le client demande un ticket initial (TGT), puis des tickets de service (TGS).
- NTLM : protocole d'authentification par défi-réponse.
- SPN : nom associant un service à un compte Active Directory.

## Valeurs à connaître

- DONT_REQ_PREAUTH : indicateur d'un compte pouvant ne pas exiger la préauthentification Kerberos.
- DS-Replication-Get-Changes : droit utilisé dans les mécanismes de réplication de l'annuaire.

Ces éléments sont des noms d'attributs et de droits, pas des commandes.

## Passer à la pratique

- [Énumération Active Directory](ad-enumeration.md)
- [Techniques Active Directory](ad-techniques.md)
- [Mouvement latéral](ad-lateral.md)

Source : [Notes OSCP Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).
""",encoding="utf-8")
 cssf=Path("docs/.vitepress/theme/custom.css")
 css=cssf.read_text(encoding="utf-8")
 if "/* OSCP exam compact styling */" not in css:
  css+="""
/* OSCP exam compact styling */
.vp-doc h2 { margin-top: 1.7rem; margin-bottom: .65rem; }
.vp-doc h3 { margin-top: 1.25rem; margin-bottom: .5rem; }
.vp-doc h4 { margin-top: 1rem; margin-bottom: .4rem; }
.vp-doc p { margin: .5rem 0 .75rem; line-height: 1.6; }
.vp-doc div[class*="language-"] { margin: .55rem 0 1rem; border-color: #30243F; box-shadow: none; }
.vp-doc div[class*="language-"] pre { padding-top: 12px; padding-bottom: 12px; }
.vp-doc div[class*="language-"] code { line-height: 1.55; }
.vp-doc strong { color: #DCCFFF; font-weight: 600; }
.vp-doc table td, .vp-doc table th { padding: 7px 11px; }
"""
  cssf.write_text(css,encoding="utf-8")
 index=D/"index.md"
 s=index.read_text(encoding="utf-8")
 if "Ctrl + K" not in s:s=s.replace("# OSCP","# OSCP\n\n**Recherche rapide :** Ctrl + K pour trouver une commande ou une technique.",1)
 index.write_text(s,encoding="utf-8")
 totals={k:sum(p.get(k,0) for p in audit.values()) for k in ("source_blocks","remaining_blocks","compact_fragments")}
 Path("oscp-refinement-audit.json").write_text(json.dumps({"total":totals,"pages":audit},ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps(totals,ensure_ascii=False))
 assert totals["source_blocks"]>1500
 assert totals["remaining_blocks"]>900
 assert totals["compact_fragments"]>200
if __name__=="__main__":main()

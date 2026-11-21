#!/usr/bin/env python3
"""Precise French titles for OSCP snippets, without changing executable commands."""
from __future__ import annotations
from pathlib import Path
import collections
import html
import json
import re

ROOT=Path("docs/src/oscp")
CSS=Path("docs/.vitepress/theme/custom.css")
B=chr(96)
F=B*3
NOTE=re.compile(r'<p class="oscp-command-note">([\s\S]*?)</p>(\s*)('+F+r'([^\n]*)\n([\s\S]*?)\n'+F+')')
GENERIC=re.compile(r"^(?:Exemple (?:avec|technique|et paramètres)|Commande .+ pour la rubrique)",re.I)
BOLD={
"Username and Hostname":"Utilisateur et nom de la machine",
"Existing Users":"Utilisateurs locaux","Existing Groups":"Groupes locaux",
"Operating System, Version, and Architecture":"Système, version et architecture",
"Network Information":"Configuration réseau","Installed Applications":"Logiciels installés",
"Running Processes":"Processus actifs","Service Accounts":"Comptes de service",
"Local Administrator Group Members":"Membres du groupe Administrateurs",
"System Drives and Mounted Volumes":"Lecteurs et volumes",
"PowerShell Version":"Version de PowerShell",
"Common Commands":"Commandes courantes","Basic Enumeration":"Énumération de base",
"Overview":"Vue d'ensemble","General Methodology":"Méthodologie générale",
"Theory":"Principes","Command Methods":"Méthodes d'exécution",
"FTP (with Null Session)":"FTP sans authentification",
"RPC (with Null Session)":"RPC sans authentification",
"SMB (with Null Session)":"SMB sans authentification",
"LDAP (with Null Session)":"LDAP sans authentification",
"Redis (with Null Session)":"Redis sans authentification",
"Rsync (with Null Session)":"Rsync sans authentification",
"Password Policy":"Politique de mots de passe",
"File Permissions":"Permissions des fichiers",
}
TOOLS={
"whoami":"Afficher le compte utilisateur courant",
"id":"Afficher l'identité Unix et les groupes","hostname":"Afficher le nom de la machine",
"uname":"Afficher le système et la version du noyau","pwd":"Afficher le répertoire courant",
"systeminfo":"Afficher la version et la configuration de Windows",
"ipconfig":"Afficher la configuration réseau Windows","ifconfig":"Afficher les interfaces réseau",
"netstat":"Examiner les ports et connexions réseau","ip":"Examiner les interfaces et routes réseau",
"route":"Afficher ou modifier les routes réseau","ps":"Afficher les processus actifs",
"ls":"Lister les fichiers du répertoire","dir":"Lister les fichiers du répertoire",
"cat":"Lire un fichier","chmod":"Modifier les permissions d'un fichier",
"rm":"Supprimer les fichiers indiqués","cp":"Copier les fichiers indiqués",
"mkdir":"Créer un répertoire","cd":"Changer de répertoire",
"find":"Rechercher des fichiers selon un filtre","grep":"Rechercher un motif textuel",
"sed":"Transformer le texte avec une expression","awk":"Filtrer ou formater des données",
"echo":"Afficher ou écrire une valeur","git":"Examiner les fichiers et l'historique Git",
"whatweb":"Identifier les technologies du site web","wappalyzer":"Identifier les technologies web",
"builtwith":"Identifier les technologies du site","nikto":"Examiner la configuration du serveur web",
"ffuf":"Rechercher des chemins ou paramètres web avec FFUF",
"dirb":"Rechercher des répertoires web avec DIRB",
"dirsearch":"Rechercher des chemins web avec dirsearch",
"gobuster":"Énumérer les répertoires ou sous-domaines avec Gobuster",
"feroxbuster":"Énumérer les chemins web avec Feroxbuster",
"wfuzz":"Tester les paramètres web avec Wfuzz","wpscan":"Examiner un site WordPress",
"sqlmap":"Examiner les paramètres SQL de l'application",
"curl":"Interroger le serveur avec une requête HTTP",
"wget":"Télécharger une ressource distante",
"whois":"Consulter les données publiques d'enregistrement du domaine",
"host":"Interroger les enregistrements DNS","nslookup":"Interroger les enregistrements DNS",
"dig":"Interroger les enregistrements DNS",
"nmap":"Scanner les ports et services avec Nmap",
"rustscan":"Rechercher rapidement les ports accessibles",
"nc":"Établir ou tester une connexion avec Netcat",
"ncat":"Établir ou tester une connexion avec Ncat",
"ssh":"Ouvrir une connexion SSH","scp":"Transférer des fichiers via SSH",
"sftp":"Transférer des fichiers en SFTP","telnet":"Tester la connexion à un port TCP",
"proxychains":"Utiliser une commande au travers d'un proxy",
"socat":"Configurer une connexion ou une redirection réseau",
"chisel":"Configurer un tunnel réseau avec Chisel",
"xfreerdp":"Ouvrir une session RDP","rdesktop":"Ouvrir une session RDP",
"evil-winrm":"Ouvrir une session distante WinRM",
"ldapsearch":"Interroger les objets de l'annuaire LDAP",
"rpcclient":"Examiner les objets exposés par RPC",
"enum4linux":"Examiner les informations SMB et du domaine",
"smbclient":"Parcourir un partage SMB","smbmap":"Lister les partages SMB et leurs permissions",
"crackmapexec":"Examiner un service Windows avec CrackMapExec",
"netexec":"Examiner un service Windows avec NetExec",
"nxc":"Examiner un service Windows avec NetExec",
"kerbrute":"Examiner les comptes Kerberos du domaine",
"impacket-getnpusers":"Examiner les comptes sans préauthentification Kerberos",
"getnpusers.py":"Examiner les comptes sans préauthentification Kerberos",
"impacket-getuserspns":"Énumérer les SPN des comptes de service",
"getuserspns.py":"Énumérer les SPN des comptes de service",
"impacket-gettgt":"Demander un ticket Kerberos TGT",
"impacket-secretsdump":"Examiner les données d'authentification avec SecretsDump",
"secretsdump.py":"Examiner les données d'authentification avec SecretsDump",
"impacket-psexec":"Exécuter une commande distante via SMB",
"psexec.py":"Exécuter une commande distante via SMB",
"impacket-wmiexec":"Exécuter une commande distante via WMI",
"wmiexec.py":"Exécuter une commande distante via WMI",
"rubeus.exe":"Examiner les tickets et paramètres Kerberos",
"mimikatz":"Examiner les données d'authentification avec Mimikatz",
"mimikatz.exe":"Examiner les données d'authentification avec Mimikatz",
"get-aduser":"Énumérer les utilisateurs du domaine",
"get-adcomputer":"Énumérer les ordinateurs du domaine",
"get-adgroup":"Énumérer les groupes du domaine",
"get-localuser":"Lister les comptes locaux",
"get-localgroup":"Lister les groupes locaux",
"get-localgroupmember":"Afficher les membres d'un groupe local",
"get-itemproperty":"Lire une clé du Registre Windows",
"get-childitem":"Rechercher des fichiers avec PowerShell",
"get-ciminstance":"Examiner les propriétés CIM du système",
"get-wmiobject":"Examiner les informations système WMI",
"get-scheduledtask":"Lister les tâches planifiées Windows",
"get-psdrive":"Lister les lecteurs PowerShell",
"select-object":"Sélectionner les propriétés de la sortie PowerShell",
"resolve-dnsname":"Résoudre un nom DNS avec PowerShell",
"test-netconnection":"Tester une connexion réseau avec PowerShell",
"iwr":"Interroger une URL avec PowerShell",
"invoke-webrequest":"Interroger une URL avec PowerShell",
"import-module":"Charger un module PowerShell",
"net":"Examiner les comptes ou ressources Windows",
"reg":"Consulter ou modifier une clé de Registre",
"wmic":"Interroger les informations système via WMI",
"icacls":"Vérifier les permissions NTFS",
"schtasks":"Examiner les tâches planifiées Windows",
"sc":"Examiner les services Windows",
"netsh":"Examiner les paramètres réseau Windows",
"msfvenom":"Créer un fichier de sortie avec msfvenom",
"msfconsole":"Ouvrir la console Metasploit",
"hashcat":"Analyser des empreintes avec Hashcat",
"john":"Analyser des empreintes avec John",
"hydra":"Vérifier des identifiants sur un service autorisé",
"medusa":"Vérifier des identifiants sur un service autorisé",
"pdfcrack":"Vérifier le mot de passe d'un document PDF",
"fcrackzip":"Vérifier le mot de passe d'une archive ZIP",
"ssh2john":"Préparer une empreinte de clé SSH pour John",
"zip2john":"Préparer une empreinte ZIP pour John",
"office2john":"Préparer une empreinte Office pour John",
"exiftool":"Afficher les métadonnées d'un fichier",
"binwalk":"Examiner la structure d'un fichier",
"strings":"Rechercher les chaînes de caractères lisibles",
"certutil":"Examiner les paramètres des certificats Windows",
"certutil.exe":"Examiner les paramètres des certificats Windows",
"systemctl":"Examiner l'état des services Linux",
"apt":"Gérer les paquets Debian/Ubuntu",
"dpkg":"Examiner ou gérer les paquets installés",
"pip3":"Gérer les modules Python",
"python":"Exécuter un script Python","python3":"Exécuter un script Python",
"bash":"Exécuter un script shell","powershell":"Exécuter un script PowerShell",
"powershell.exe":"Exécuter un script PowerShell",
"mysql":"Interroger une base de données MySQL",
"redis-cli":"Interroger un serveur Redis",
"openssl":"Examiner une connexion TLS ou un certificat",
"searchsploit":"Rechercher des références de vulnérabilités connues",
"snmpwalk":"Interroger les paramètres SNMP",
"swaks":"Examiner la configuration SMTP",
"showmount":"Lister les exports NFS",
"chisel":"Configurer un tunnel réseau",
"responder":"Observer les requêtes de résolution de noms"
}
def first_line(code):
    for raw in code.splitlines():
        line=raw.strip()
        if line and not line.startswith(("#","//","-- ",";","/*","#!")):
            return line
    return code.strip().splitlines()[0] if code.strip() else ""

def tool_key(line):
    s=re.sub(r"^\$\s+|^sudo\s+","",line.strip(),flags=re.I)
    token=s.split()[0] if s.split() else ""
    return token.lstrip("./").split("/")[-1].split("\\")[-1].casefold()

def describe(code,language,heading):
    line=first_line(code)
    low=line.lower()
    name=tool_key(line)
    if language=="sql" and low.startswith("select-object"):
        return "Sélectionner les propriétés de la sortie PowerShell."
    if language=="sql" or re.match(r"^(select|insert|update|delete|create|alter)\s",low):
        if "select" in code.lower():return "Lire les résultats d'une requête SQL."
        if "create" in code.lower():return "Définir un objet ou une configuration SQL."
        return "Instruction SQL dans la rubrique « "+heading+" »."
    if language in ("html","xml","php","javascript"):
        return "Extrait "+{"html":"HTML","xml":"XML","php":"PHP","javascript":"JavaScript"}[language]+" lié à « "+heading+" »."
    if language=="python" or low.startswith(("import ","from ")) and language=="python":
        return "Script Python lié à « "+heading+" »."
    if low.startswith(("<?php","<%")):return "Extrait de code serveur lié à « "+heading+" »."
    if low.startswith(("<script","<img ","<form ","<iframe")):return "Exemple de balise HTML lié à « "+heading+" »."
    if low.startswith("nmap "):
        if "--script-help" in low:return "Afficher l'aide d'un script Nmap NSE."
        if "--script" in low:return "Examiner les services avec les scripts NSE sélectionnés."
        if "-su" in low:return "Examiner les ports UDP."
        if "-sv" in low:return "Identifier les versions des services."
        if "-sn" in low:return "Identifier les hôtes actifs."
        if "-p-" in low:return "Scanner tous les ports."
    if low.startswith(("nc ","ncat ")):
        if re.search(r"\s-[a-z]*l",low):return "Ouvrir un port d'écoute Netcat."
        if re.search(r"\s-[a-z]*z",low):return "Tester l'accessibilité de ports avec Netcat."
    if low.startswith("ssh "):
        if "kexalgorithms" in low or "hostkeyalgorithms" in low:
            return "Tester les algorithmes SSH anciens."
        if " -i " in low:return "Se connecter avec une clé SSH privée."
        if re.search(r"\s-[lrd]\s",low):return "Configurer une redirection SSH."
    if low.startswith("get-itemproperty") and "uninstall" in low:
        return "Lister les logiciels installés depuis le Registre."
    if low.startswith("net localgroup"):
        return "Lister les groupes locaux Windows."
    if low.startswith("net user"):
        return "Examiner les comptes utilisateurs Windows."
    if low.startswith("reg query"):
        return "Consulter la valeur d'une clé du Registre."
    if low.startswith("curl "):
        if " -x options" in low:return "Afficher les méthodes HTTP disponibles."
        if " -x post" in low:return "Envoyer une requête HTTP POST."
        if re.search(r"\s-I(?:\s|$)",line):return "Afficher les en-têtes de la réponse HTTP."
    if name in TOOLS:return TOOLS[name]+"."
    if name.startswith("impacket-"):
        return "Commande Impacket dans la rubrique « "+heading+" »."
    if language=="powershell" and len(code.splitlines())>=3:
        return "Script PowerShell dans la rubrique « "+heading+" »."
    if language=="bash" and len(code.splitlines())>=4:
        return "Script shell dans la rubrique « "+heading+" »."
    return None

def data_snippet(code,lang):
    value=code.strip()
    if value=="version + github + exploit search":
        return ("Rappel","Rechercher une vulnérabilité connue à partir de la version détectée.")
    if value=="HYDRA SMTP ENUM":
        return ("Rappel","Vérifier le service SMTP ; la note d'origine ne fournit pas une syntaxe complète.")
    if re.fullmatch(r"\[(?:boxname|appname)\]:(?:admin|password|\[appName\])",value,re.I):
        return ("Identifiant de laboratoire",value)
    if re.fullmatch(r"(?:admin|root):(?:no pass|admin|root|password)",value,re.I):
        return ("Identifiant de laboratoire",value)
    if value.lower().startswith("pass, passwd, pwd, user, usr, username, secret,"):
        return ("Champs de formulaire",value)
    if lang=="text" and len(value.splitlines())==1:
        if re.fullmatch(r"(?:[a-z]:\\[^\n]+|/(?:etc|var|home|tmp|root)/[^\n]+)",value,re.I):
            return ("Chemin à vérifier",value)
        if re.fullmatch(r"\.[\w.]+(?:\s*,\s*\.[\w.]+)*",value):
            return ("Extensions de fichier",value)
    return None

def method_credential_group(text):
    start=text.find("**Paramètres et repères :**\n"+B+"admin:admin")
    end=text.find("**Paramètres et repères :**\n"+B+"sa",start)
    if start==-1 or end==-1:return text,False
    summary="""#### Exemples d'identifiants et de champs à vérifier

**Couples utilisateur / mot de passe (laboratoire) :** §admin:admin§, §admin:password§, §root:admin§, §root:password§, §root:root§, §[boxname]:admin§, §[boxname]:password§, §[appName]:[appName]§.

**Variantes sans mot de passe :** §admin:no pass§, §root:no pass§. Ce sont des valeurs, pas des commandes.

**Noms de champs fréquents :** §pass§, §passwd§, §pwd§, §user§, §usr§, §username§, §secret§, §cred§, §credential§, §auth§.

""".replace("§",B)
    return text[:start]+summary+text[end:],True

def improve(text,slug):
    if slug=="methodologie":
        text, grouped=method_credential_group(text)
    else: grouped=False
    translated=0
    for orig,new in BOLD.items():
        n=text.count("**"+orig+"**")
        if n: text=text.replace("**"+orig+"**","**"+new+"**");translated+=n
    heading=slug.replace("-"," ")
    previous_title=None
    previous_end=0
    stats=collections.Counter()
    if grouped:stats["identifiers_grouped"]=1
    stats["translated_titles"]=translated
    def subst(m):
        nonlocal heading,previous_end,previous_title
        between=text[previous_end:m.start()]
        previous_end=m.end()
        found=re.findall(r"^#{2,5}\s+(.+)$",between,re.M)
        if found:heading=found[-1];previous_title=None
        old=html.unescape(m.group(1))
        code=m.group(5)
        lang=m.group(4).strip()
        spacing=m.group(2)
        fence=m.group(3)
        generic=bool(GENERIC.match(old))
        if generic:stats["generic_before"]+=1
        data=data_snippet(code,lang)
        if data:
            label,value=data
            if label=="Rappel":
                result='<p class="oscp-inline-ref"><strong>Rappel :</strong> '+html.escape(value)+'</p>'
            else:
                result='<p class="oscp-inline-ref"><strong>'+html.escape(label)+' :</strong> <code>'+html.escape(value)+'</code></p>'
            stats["noncommands_fixed"]+=1
            return result
        title=describe(code,lang,heading)
        if not title and not generic:title=old
        if not title:
            stats["unknown_titles_omitted"]+=1
            return spacing+fence
        if title==previous_title:
            stats["repeated_titles_removed"]+=1
            return spacing+fence
        previous_title=title
        stats["titles_written"]+=1
        return '<p class="oscp-command-note">'+html.escape(title)+'</p>'+spacing+fence
    result=NOTE.sub(subst,text)
    stats["generic_after"]=len(re.findall(r'<p class="oscp-command-note">(?:Exemple (?:avec|technique)|Commande .+ pour la rubrique)',result,re.I))
    stats["code_blocks_before"]=len(re.findall(r"^"+F,text,re.M))//2
    stats["code_blocks_after"]=len(re.findall(r"^"+F,result,re.M))//2
    return result,dict(stats)

def main():
    audit={}
    for file in sorted(ROOT.glob("*.md")):
        if file.stem in ("index","ad-theorie","cloud","references"):continue
        old=file.read_text(encoding="utf-8")
        updated,stats=improve(old,file.stem)
        file.write_text(updated,encoding="utf-8")
        audit[file.stem]=stats
    css=CSS.read_text(encoding="utf-8")
    if "/* Precise OSCP labels */" not in css:
        css+="""
/* Precise OSCP labels */
.vp-doc .oscp-command-note { font-size: .84rem; color:#B7A6D9; font-weight:500;
    border-left:2px solid #694C9A; padding-left:10px; margin:.45rem 0; }
.vp-doc .oscp-inline-ref { font-size:.84rem; color:#ACA1C0; line-height:1.55; margin:.35rem 0 .6rem; }
.vp-doc .oscp-inline-ref strong { color:#CDB8F3; }
.vp-doc .oscp-inline-ref code { color:#DDCFFF; }
"""
        CSS.write_text(css,encoding="utf-8")
    totals={key:sum(page.get(key,0) for page in audit.values()) for key in (
        "generic_before","generic_after","titles_written","unknown_titles_omitted",
        "repeated_titles_removed","noncommands_fixed","identifiers_grouped",
        "translated_titles","code_blocks_before","code_blocks_after")}
    REPORT=Path("oscp-command-title-audit.json")
    REPORT.write_text(json.dumps({"pages":audit,"totals":totals},ensure_ascii=False,indent=2),encoding="utf-8")
    assert totals["generic_before"]>800,totals
    assert totals["generic_after"]==0,totals
    assert totals["identifiers_grouped"]==1,totals
    assert totals["code_blocks_before"]-totals["code_blocks_after"]<=30,totals
    method=(ROOT/"methodologie.md").read_text(encoding="utf-8")
    assert "#### Exemples d'identifiants et de champs à vérifier" in method
    assert "Exemple technique pour la rubrique" not in method
    print(json.dumps(totals,ensure_ascii=False,indent=2))

if __name__=="__main__":main()

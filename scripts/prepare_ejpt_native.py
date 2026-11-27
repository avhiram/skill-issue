#!/usr/bin/env python3
"""Integrate existing sanitized eJPT documents with the site's native theme."""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from bs4 import BeautifulSoup
src=Path(sys.argv[1])
docs=Path("docs/src")
target=docs/"ejpt/original"
assets=docs/"public/ejpt/original"
report=json.loads((src/"import-report.json").read_text(encoding="utf-8"))
titles=json.loads(Path("imports/ejpt/display-titles.json").read_text(encoding="utf-8"))
assert len(report["pages"])==len(titles)==80
if target.exists() or assets.exists():
    raise RuntimeError("Generated directories already exist; refusing to overwrite sources")
target.mkdir(parents=True)
assets.mkdir(parents=True)
count=0
for p in src.rglob("*"):
    if not p.is_file():
        continue
    rel=p.relative_to(src)
    if rel.as_posix() in report["pages"] or rel.as_posix() in {"index.html","reader.css","reader.js"}:
        continue
    dest=assets/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(p,dest)
    if hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(dest.read_bytes()).digest():
        raise RuntimeError("Asset copy mismatch: "+str(rel))
    if p.suffix.lower() in {".png",".gif"}:
        count+=1
assert count==report["images"]
# Consolidate the existing sheets at render time. The original source files
# remain byte-verified and unchanged. Deduplicate only identical rendered
# code blocks, including whitespace; no command is rewritten.
canonical = "ejpt-cheatsheet.html"
aliases = {
    "cheatsheet-files/ejpt-cheatsheet_nolinks.html",
    "cheatsheet-additional.html",
}
canonical_url = "/skill-issue/ejpt/original/" + canonical
def load_article(page):
    doc = BeautifulSoup((src/page).read_text(encoding="utf-8"),"html.parser")
    result = doc.find("article")
    if result is None:
        raise RuntimeError("Missing sheet article: "+page)
    return result
sheet_sources = [canonical, "cheatsheet-files/ejpt-cheatsheet_nolinks.html", "cheatsheet-additional.html"]
source_blocks = {
    p: [c.get_text() for c in load_article(p).select("pre code")]
    for p in sheet_sources
}
expected_blocks = set().union(*(set(v) for v in source_blocks.values()))
if set(source_blocks[sheet_sources[1]]) != set(source_blocks[canonical]):
    raise RuntimeError("The no-links variant has different blocks; review before consolidation")
def consolidate_sheets(soup, article):
    seen = {}
    def dedup(part):
        for pre in list(part.find_all("pre")):
            code = pre.find("code",recursive=False)
            if code is None:
                continue
            key = code.get_text()
            if key in seen:
                note = soup.new_tag("p",attrs={"class":"ejpt-duplicate-note"})
                link = soup.new_tag("a",href="#"+seen[key])
                link.string = "Bloc identique — voir la commande"
                note.append(link)
                pre.replace_with(note)
            else:
                ident = "ejpt-code-"+str(len(seen)+1)
                pre["id"] = ident
                seen[key] = ident
    dedup(article)
    supplement = load_article("cheatsheet-additional.html")
    # Keep the original headings, explanations, images and context for
    # non-identical material, inside the same canonical sheet.
    for node in supplement.select("[id]"):
        node["id"] = "complement-"+node["id"]
    for link in supplement.select('a[href^="#"]'):
        if len(link["href"])>1:
            link["href"] = "#complement-"+link["href"][1:]
    dedup(supplement)
    # Use the same heading hierarchy as the rest of the site's native sheets.
    # This is presentation only: retain all existing prose, images and code.
    extra = soup.new_tag("h2", id="complements-de-revision")
    extra.string = "Compléments de révision"
    article.append(extra)
    for heading in supplement.find_all(re.compile(r"^h[2-6]$")):
        heading.name = "h"+str(min(int(heading.name[1])+1,6))
    for child in list(supplement.contents):
        if getattr(child,"name",None) == "h1":
            child.extract()
            continue
        article.append(child.extract())
    actual = [c.get_text() for c in article.select("pre code")]
    if set(actual) != expected_blocks or len(actual) != len(expected_blocks):
        raise RuntimeError("Consolidation lost or duplicated a source code block")
    print("Unified eJPT cheatsheet:",len(actual),"distinct original rendered code blocks")
    return article

# Display labels only; preserve the original IDs and course references.
sheet_labels = {
    "Networking": "Fondamentaux réseau",
    "Information Gathering": "Collecte d’informations",
    "Footprinting & Scanning": "Footprinting et scanning",
    "Enumeration": "Énumération",
    "Vulnerability Assessment": "Évaluation des vulnérabilités",
    "Host Based Attacks": "Pentest système",
    "Network Based Attacks": "Pentest réseau",
    "Metasploit": "Metasploit",
    "Exploitation": "Exploitation",
    "Post-Exploitation": "Post-exploitation",
    "Social Engineering": "Social Engineering",
    "Web Application Penetration Testing": "Pentest Web",
}
def format_sheet(soup, article):
    # Do not expose the obsolete download variants in the unified web sheet.
    for link in list(article.find_all("a",href=True)):
        href=link["href"].split("#",1)[0].split("?",1)[0]
        if re.search(r"/cheatsheet-files/ejpt-cheatsheet_nolinks\.(?:md|pdf|html|docx)$",href,re.I):
            parent=link.parent
            if parent.name=="li" and parent.get_text(strip=True)==link.get_text(strip=True):
                parent.decompose()
            else:
                link.replace_with(link.get_text())
    for ul in list(article.find_all(["ul","ol"])):
        if not ul.find("li"):
            ul.decompose()
    for heading in article.find_all(re.compile(r"^h[23]$")):
        label=heading.get_text(" ",strip=True)
        if label not in sheet_labels:
            continue
        if heading.get("id","").startswith("complement-"):
            heading.string=sheet_labels[label]
            continue
        link=heading.find("a",href=True)
        href=link["href"] if link else None
        heading.clear()
        heading.append(sheet_labels[label])
        if href:
            p=soup.new_tag("p",attrs={"class":"ejpt-course-link"})
            a=soup.new_tag("a",href=href)
            a.string="Voir le cours"
            p.append(a)
            heading.insert_after(p)


# Separate the basic networking commands by purpose and operating system.
# Only presentation labels and comments are moved; every command line is
# checked against the original before generating the displayed blocks.
network_labels = {
    "# Routing": ("Table de routage", "Afficher les routes utilisées par le système."),
    "# IP": ("Adresses IP et interfaces", "Identifier les interfaces réseau et leurs adresses IP."),
    "# ARP": ("Table ARP et voisins réseau", "Consulter les associations d’adresses IP et MAC connues du système."),
    "# PORTS": ("Ports et connexions locales", "Afficher les ports et les connexions réseau du système."),
    "# Connect": ("Tester une connexion réseau", "Vérifier une connexion TCP ou TLS vers un service autorisé."),
}
platform_labels = {
    "# Linux": ("Linux", "bash"),
    "# Windows": ("Windows", "bat"),
    "# Mac OS X / Linux": ("macOS / Linux", "bash"),
}
def format_network_basics(soup, article):
    network = article.find("h2", id="networking")
    if network is None:
        network = next((h for h in article.find_all("h2") if h.get_text(strip=True)=="Fondamentaux réseau"), None)
    if network is None:
        raise RuntimeError("Missing networking section")
    candidates = []
    for sibling in network.next_siblings:
        if getattr(sibling,"name",None)=="h2":
            break
        if getattr(sibling,"name",None)=="pre":
            candidates.append(sibling)
    changed = set()
    for pre in candidates:
        code = pre.find("code",recursive=False)
        if code is None:
            continue
        lines = code.get_text().splitlines()
        if not lines or lines[0] not in network_labels:
            continue
        marker = lines[0]
        if marker in changed:
            raise RuntimeError("Duplicate networking source section")
        changed.add(marker)
        name, description = network_labels[marker]
        base = "reseau-"+{"# Routing":"routage","# IP":"ip","# ARP":"arp","# PORTS":"ports","# Connect":"connexion"}[marker]
        ident = pre.get("id",base)
        heading = soup.new_tag("h3",id=ident)
        heading.string = name
        pre.insert_before(heading)
        desc = soup.new_tag("p")
        desc.string = description
        pre.insert_before(desc)
        parts = []
        if marker != "# Connect":
            current = None
            for line in lines[1:]:
                if line in platform_labels:
                    current = [*platform_labels[line],[]]
                    parts.append(current)
                elif current is not None:
                    current[2].append(line)
                elif line.strip():
                    raise RuntimeError("Unexpected content before platform heading")
            if len(parts)!=3:
                raise RuntimeError("Unexpected networking platform count")
            removed = set(platform_labels) | {marker}
        else:
            # The existing block contains three groups separated by blank lines.
            raw = "\n".join(lines[1:]).strip()
            chunks = [c for c in re.split(r"\n[ \t]*\n",raw) if c.strip()]
            if len(chunks)!=3 or not chunks[2].startswith("# Scan port\n"):
                raise RuntimeError("Unexpected connection block structure")
            parts = [
                ["Connexion TCP avec Netcat","bash",chunks[0].splitlines()],
                ["Connexion TLS avec OpenSSL","bash",chunks[1].splitlines()],
                ["Vérification d’un port avec Netcat","bash",chunks[2].splitlines()[1:]],
            ]
            removed = {marker,"# Scan port"}
        original = [line for line in lines if line.strip() and line not in removed]
        displayed = []
        for i,(label,language,commands) in enumerate(parts,1):
            while commands and not commands[0].strip():
                commands.pop(0)
            while commands and not commands[-1].strip():
                commands.pop()
            if not commands:
                raise RuntimeError("Empty networking block")
            displayed.extend(line for line in commands if line.strip())
            sub = soup.new_tag("h4",id=base+"-"+str(i))
            sub.string = label
            pre.insert_before(sub)
            block = soup.new_tag("pre")
            newcode = soup.new_tag("code",attrs={"class":"language-"+language})
            newcode.string = "\n".join(commands)+"\n"
            block.append(newcode)
            pre.insert_before(block)
        if displayed != original:
            raise RuntimeError("Networking formatting changed command lines")
        pre.decompose()
    if changed != set(network_labels):
        raise RuntimeError("Networking layout incomplete")
    print("Network presentation verified: 5 source blocks split into 15, every command line retained")


# Presentation metadata for the existing information-gathering notes.
# Do not change commands or add procedures; split only known source blocks.
info_labels = {
    "host": ("Résolution DNS", "Consulter les informations DNS associées à un nom d’hôte."),
    "whatweb": ("Technologies Web", "Identifier les technologies visibles sur une application Web autorisée."),
    "whois": ("Informations WHOIS", "Consulter les informations publiques d’enregistrement d’un domaine ou d’une adresse IP."),
    "dnsrecon": ("Informations DNS avec DNSRecon", "Consulter les informations DNS dans le périmètre autorisé."),
    "wafw00f": ("Identification du WAF", "Identifier la présence éventuelle d’un pare-feu applicatif sur un site de test."),
    "sublist3r": ("Sous-domaines", "Recenser les sous-domaines du périmètre autorisé."),
    "theHarvester": ("Informations publiques", "Consulter les informations publiques associées au domaine de test."),
    "sudo": ("Fichier hosts local", "Consulter ou modifier la résolution locale des noms sur sa machine de laboratoire."),
    "dnsenum": ("DNS avec DNSenum", "Examiner les informations DNS du domaine de test."),
    "dig": ("Requêtes DNS avec Dig", "Interroger le DNS dans le cadre du laboratoire autorisé."),
    "fierce": ("Inventaire DNS avec Fierce", "Consulter les informations DNS dans le périmètre défini."),
    "dorks": ("Opérateurs de recherche", "Repères de syntaxe des moteurs de recherche. Rester dans le périmètre autorisé."),
    "## Ping scan": ("Découverte des hôtes", "Identifier les hôtes visibles sur le réseau de laboratoire."),
    "## ARP scan": ("Découverte ARP", "Consulter les hôtes visibles sur le réseau local de test."),
    "# NMAP PORT SCAN": ("Scan de ports", "Identifier les ports accessibles sur un hôte autorisé."),
    "## Skip ping": ("Scan sans découverte préalable", "Repère sur le comportement de la phase de découverte Nmap."),
    "## Host discovery + saving into file": ("Enregistrer les résultats de découverte", "Conserver les résultats du laboratoire dans un fichier."),
    "## Scan all ports": ("Ensemble des ports TCP", "Repère sur le périmètre de ports examiné."),
    "## Open ports scan + saving into file": ("Enregistrer les résultats du scan", "Conserver les résultats du scan de laboratoire."),
    "## Port 80 only scan": ("Port HTTP", "Examiner le port indiqué dans le périmètre de test."),
    "## Custom list of ports scan": ("Liste de ports", "Définir les ports à examiner."),
    "## Custom ports range scan": ("Plage de ports", "Définir un intervalle de ports à examiner."),
    "## Fast mode & verbose scan": ("Mode rapide et affichage détaillé", "Repère sur les options de scan et d’affichage."),
    "## UDP scan": ("Ports UDP", "Examiner les ports utilisant le protocole UDP."),
    "## Service scan": ("Identification des services", "Identifier les services et leurs versions."),
    "## Service + O.S. detection scan": ("Services et système", "Consulter les informations de détection des services et du système."),
    "## Default Scripts scan": ("Scripts Nmap par défaut", "Repère sur les scripts proposés par Nmap dans un laboratoire autorisé."),
    "## Aggressive scan": ("Mode de détection étendu", "Repère sur les options de détection combinées ; respecter les règles d’engagement."),
    "## Timing (T0=slow ... T5=insanely fast) scan": ("Temporisation du scan", "Repère sur les profils de temporisation ; adapter les tests aux règles d’engagement."),
    "## Output scan": ("Formats de sortie", "Conserver les résultats sous forme de fichiers."),
    "## Output to all formats": ("Export des résultats", "Conserver les résultats dans les formats de sortie prévus."),
}
def format_information_gathering(soup, article):
    seen = {}
    counts = [0,0]
    def format_block(pre,kind,depth):
        code=pre.find("code",recursive=False)
        if code is None:
            raise RuntimeError("Missing source code in information gathering")
        lines=code.get_text().splitlines()
        removed=set()
        parts=[]
        current=None
        def add(key):
            nonlocal current
            if key not in info_labels:
                raise RuntimeError("Unknown information gathering label: "+key)
            current=[key,[]]
            parts.append(current)
        if kind=="dorks":
            add("dorks")
        for line in lines:
            if line in {"# Passive","# Google Dorks","# DNS","# HOST DISCOVERY"}:
                removed.add(line)
                continue
            if kind=="scan" and line in info_labels and line.startswith("#"):
                removed.add(line)
                add(line)
                continue
            if kind in {"passive","dns"} and line.strip() and not line.startswith("#"):
                key=line.split()[0]
                if key not in info_labels:
                    raise RuntimeError("Unexpected information gathering source group")
                if current is None or current[0]!=key:
                    add(key)
            if current is not None:
                current[1].append(line)
            elif line.strip():
                raise RuntimeError("Unclassified information gathering source line")
        original=[line for line in lines if line.strip() and line not in removed]
        reconstructed=[]
        source_id=pre.get("id","info-source-"+str(counts[0]+1))
        anchor=soup.new_tag("span",id=source_id)
        pre.insert_before(anchor)
        duplicate_targets=[]
        for i,(key,group) in enumerate(parts,1):
            while group and not group[0].strip():
                group.pop(0)
            while group and not group[-1].strip():
                group.pop()
            if not group:
                continue
            reconstructed.extend(x for x in group if x.strip())
            content="\n".join(group)+"\n"
            if content in seen:
                duplicate_targets.append(seen[content])
                continue
            title,desc=info_labels[key]
            ident="info-"+str(counts[0]+1)+"-"+str(i)
            heading=soup.new_tag("h"+str(depth),id=ident,attrs={"class":"ejpt-action-heading"})
            heading.string=title
            pre.insert_before(heading)
            para=soup.new_tag("p",attrs={"class":"ejpt-action-description"})
            para.string=desc
            pre.insert_before(para)
            block=soup.new_tag("pre")
            newcode=soup.new_tag("code",attrs={"class":"language-text" if kind=="dorks" else "language-bash"})
            newcode.string=content
            block.append(newcode)
            pre.insert_before(block)
            seen[content]=ident
            counts[1]+=1
        if original!=reconstructed:
            raise RuntimeError("Information gathering formatting changed original command lines")
        if duplicate_targets:
            p=soup.new_tag("p",attrs={"class":"ejpt-duplicate-note"})
            p.append("Blocs déjà présentés : ")
            for i,ident in enumerate(dict.fromkeys(duplicate_targets)):
                if i:
                    p.append(" · ")
                a=soup.new_tag("a",href="#"+ident)
                target=article.find(id=ident)
                a.string=target.get_text(strip=True)
                p.append(a)
            pre.insert_before(p)
        counts[0]+=1
        pre.decompose()

    def section(heading,level,depth):
        if heading is None:
            raise RuntimeError("Information gathering section missing")
        candidates=[]
        for sibling in heading.next_siblings:
            tag=getattr(sibling,"name",None)
            if tag and re.fullmatch(r"h[1-6]",tag) and int(tag[1])<=level:
                break
            if tag=="pre":
                candidates.append(sibling)
        for pre in candidates:
            first=next((x for x in pre.get_text().splitlines() if x.strip()),"")
            if first.startswith("# Passive") or first.startswith("host "):
                kind="passive"
            elif first.startswith("# Google Dorks") or first=="site:":
                kind="dorks"
            elif first=="# DNS" or first.startswith("sudo nano "):
                kind="dns"
            elif first in {"# HOST DISCOVERY","## Ping scan"}:
                kind="scan"
            else:
                raise RuntimeError("Unexpected original block in information gathering")
            format_block(pre,kind,depth)
    section(next((h for h in article.find_all("h2") if h.get_text(strip=True)=="Collecte d’informations"),None),2,3)
    section(next((h for h in article.find_all("h3") if h.get("id","").startswith("complement-") and h.get_text(strip=True)=="Collecte d’informations"),None),3,5)
    if counts[0] < 4:
        raise RuntimeError("Information gathering presentation incomplete")
    print("Information gathering presentation verified:",counts[0],"source blocks,",counts[1],"distinct displayed blocks")



# Presentation-only pass over the remaining source sections.
# Existing headings and comments are the basis for labels; code remains intact.
section_context = {
    "Footprinting et scanning": "Inventaire des équipements et observation du réseau dans un laboratoire autorisé.",
    "Énumération": "Identification des services et lecture des informations disponibles pour documenter leur configuration.",
    "Évaluation des vulnérabilités": "Repères pour comprendre les vulnérabilités et distinguer un résultat de scan d'une preuve confirmée.",
    "Pentest système": "Notes de laboratoire sur les configurations et les risques de sécurité des systèmes.",
    "Pentest réseau": "Notes sur les protocoles, le trafic réseau et les risques associés.",
    "Metasploit": "Référence des notions et des outils étudiés dans le cours, à utiliser en laboratoire autorisé.",
    "Exploitation": "Notes de laboratoire sur la validation des vulnérabilités et de leurs impacts.",
    "Post-exploitation": "Notes de cours sur les impacts d'une compromission et les mesures de défense associées.",
    "Social Engineering": "Étude des risques liés à la manipulation humaine et à la sensibilisation.",
    "Pentest Web": "Référence aux notions de sécurité des applications et des protocoles Web.",
    "Compléments de révision": "Notes complémentaires issues de la seconde fiche, regroupées avec les références originales.",
    "Wordpress": "Notions de sécurité et de configuration du CMS WordPress.",
    "Drupal": "Notions de sécurité et de configuration du CMS Drupal.",
    "Discovery": "Notes de découverte issues du complément de révision.",
}
display_labels = {
    "NETWORK DISCOVERY": "Découverte réseau",
    "NMAP": "Nmap",
    "SMBMAP": "SMBMap",
    "ENUM4LINUX": "Enum4linux",
    "METASPLOIT": "Metasploit",
    "NETCAT": "Netcat",
    "MYSQL": "MySQL",
    "SMB Connection": "Connexion SMB",
    "MSF Install": "Installation de Metasploit",
    "NESSUS Results Import": "Import des résultats Nessus",
    "Tools": "Outils",
    "Enumeration & Scanning": "Énumération et scanning",
    "Vulnerability Scanning": "Scan de vulnérabilités",
    "Info Gathering & Enumeration": "Collecte d’informations et énumération",
    "Network Discovery": "Découverte réseau",
    "Transferring Files": "Transfert de fichiers",
    "Win Local Enumeration": "Énumération locale Windows",
    "Linux Local Enumeration": "Énumération locale Linux",
    "Win Privilege Escalation": "Privilege Escalation Windows",
    "Linux Privilege Escalation": "Privilege Escalation Linux",
    "Cron Jobs": "Tâches Cron",
    "Wordpress": "WordPress",
}
def format_remaining_sections(soup, article):
    from collections import Counter
    before = [c.get_text() for c in article.select("pre code")]
    titles = Counter()
    stack = []
    main = ""
    complement = ""
    index = 0
    annotated = 0
    contexts = set()
    # Snapshot nodes so new headings are not processed recursively.
    for node in list(article.find_all(re.compile(r"^(?:h[1-6]|pre)$"))):
        if node.name != "pre":
            level = int(node.name[1])
            label = node.get_text(" ",strip=True)
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level,label))
            if level == 2:
                main = label
                complement = ""
            if main == "Compléments de révision" and level == 3:
                complement = label
            if label in section_context and level in (2,3) and label not in contexts:
                p = soup.new_tag("p",attrs={"class":"ejpt-section-description"})
                p.string = section_context[label]
                node.insert_after(p)
                contexts.add(label)
            continue
        if main in ("Fondamentaux réseau","Collecte d’informations"):
            continue
        if main == "Compléments de révision" and complement in ("Fondamentaux réseau","Networking","Collecte d’informations"):
            continue
        code = node.find("code",recursive=False)
        if code is None:
            continue
        index += 1
        context = stack[-1][1] if stack else "Notes de révision"
        label = display_labels.get(context,context)
        # Reuse an existing short comment as a display heading, not a command.
        first = next((line.strip() for line in code.get_text().splitlines() if line.strip()),"")
        comment = re.fullmatch(r"#{1,3}\s+([\w][\w .&()/+-]{0,62})",first)
        if comment:
            original = comment.group(1).strip()
            label = display_labels.get(original,original)
        if not label:
            label = "Notes de laboratoire"
        key = (main,complement,context,label)
        titles[key] += 1
        if titles[key] > 1:
            label += " · " + str(titles[key])
        # Do not introduce nested fold levels beyond HTML's heading range.
        depth = min((stack[-1][0]+1) if stack else 3,6)
        heading = soup.new_tag("h"+str(depth),id="ejpt-note-"+str(index),attrs={"class":"ejpt-action-heading ejpt-existing-note-heading"})
        heading.string = label
        node.insert_before(heading)
        annotated += 1
    assert before == [c.get_text() for c in article.select("pre code")], "Presentation changed original blocks"
    if annotated < 100:
        raise RuntimeError("Remaining cheatsheet layout incomplete")
    print("Remaining cheatsheet presentation:",annotated,"code block headings;",len(contexts),"section descriptions")
    return annotated



# Presentation only: preserve the existing network-inventory examples.
def format_footprinting(soup, article):
    candidates = []
    for pre in article.find_all("pre"):
        code = pre.find("code", recursive=False)
        if code is None:
            continue
        lines = code.get_text().splitlines()
        if '## fping with no "Host Unreachable errors"' in lines and any(line.startswith("sudo arp-scan ") for line in lines):
            candidates.append((pre, lines))
    if len(candidates) != 2:
        raise RuntimeError("Unexpected number of original footprinting blocks")
    seen = {}
    count = 0
    labels = {
        "arp": ("Découverte ARP", "Identifier les équipements visibles sur le réseau local de laboratoire."),
        "ping": ("Test de connectivité ICMP", "Vérifier si un équipement répond aux requêtes ICMP."),
        "nmap": ("Inventaire des hôtes", "Consulter les résultats de découverte des hôtes."),
        "tracert": ("Chemin réseau sous Windows", "Observer le trajet réseau vers une destination."),
        "traceroute": ("Chemin réseau sous Linux", "Observer le trajet réseau vers une destination."),
        "fping": ("Découverte avec fping", "Consulter les réponses ICMP dans le périmètre de test."),
        "fping-note": ("Variante fping des notes originales", "Attention : la ligne source semble concaténer deux commandes. Elle est conservée à l’identique et doit être vérifiée avant utilisation."),
    }
    for source_index, (pre, lines) in enumerate(candidates, 1):
        parent_heading = pre.find_previous_sibling(re.compile(r"^h[1-6]$"))
        if parent_heading is None or "ejpt-existing-note-heading" not in parent_heading.get("class", []):
            raise RuntimeError("Missing footprinting heading")
        parent_heading.string = "Découverte réseau" if source_index == 1 else "Compléments de découverte réseau"
        level = min(int(parent_heading.name[1])+1, 6)
        marker = None
        removed = []
        groups = []
        for line in lines:
            if line in ('# NETWORK DISCOVERY', '## fping', '## fping with no "Host Unreachable errors"'):
                removed.append(line)
                if line.startswith("## fping"):
                    marker = "fping-note" if "Host Unreachable" in line else "fping"
                continue
            if not line.strip():
                continue
            if line.startswith("sudo arp-scan "):
                key = "arp"
            elif line.startswith("ping "):
                key = "ping"
            elif line.startswith("sudo nmap "):
                key = "nmap"
            elif line.startswith("tracert "):
                key = "tracert"
            elif line.startswith("traceroute "):
                key = "traceroute"
            elif line.startswith("fping ") and marker in ("fping", "fping-note"):
                key = marker
            else:
                raise RuntimeError("Unknown footprinting source line")
            groups.append((key,line))
        original = [line for line in lines if line.strip() and line not in removed]
        if original != [line for _,line in groups]:
            raise RuntimeError("Footprinting formatting changed original lines")
        if pre.get("id"):
            pre.insert_before(soup.new_tag("span",id=pre["id"]))
        for key,line in groups:
            if line in seen:
                p = soup.new_tag("p",attrs={"class":"ejpt-duplicate-note"})
                link = soup.new_tag("a",href="#"+seen[line])
                link.string = labels[key][0]
                p.append(link)
                pre.insert_before(p)
                continue
            count += 1
            ident = "ejpt-footprint-"+str(count)
            title,desc = labels[key]
            h = soup.new_tag("h"+str(level),id=ident,attrs={"class":"ejpt-footprint-heading"})
            h.string = title
            pre.insert_before(h)
            p = soup.new_tag("p",attrs={"class":"ejpt-action-description"})
            p.string = desc
            pre.insert_before(p)
            block = soup.new_tag("pre")
            code = soup.new_tag("code",attrs={"class":"language-bat" if key=="tracert" else "language-bash"})
            code.string = line+"\n"
            block.append(code)
            pre.insert_before(block)
            seen[line] = ident
        pre.decompose()
    if count != 7:
        raise RuntimeError("Unexpected footprinting display count")
    print("Footprinting presentation verified: 2 original blocks, 7 distinct action blocks")
    return count



# French presentation metadata for existing source topics.
# These are conceptual labels, not additional commands or procedures.
note_topics = [
    (r"\b(?:IIS|WebDAV)\b", "IIS et WebDAV", "IIS est un serveur Web Windows. WebDAV étend HTTP pour la gestion de ressources distantes."),
    (r"\b(?:SMB|SMBMap|SMBClient|Enum4linux|RPCClient|Nmblookup|Samba)\b", "SMB et Samba", "SMB est un protocole de partage de ressources. Samba en fournit une implémentation pour les systèmes Unix."),
    (r"\b(?:FTP|VSFTPD|FTPD)\b", "FTP", "FTP est un protocole de transfert de fichiers. Les droits d’accès et la protection des échanges constituent des points de vigilance."),
    (r"\b(?:SSH|OpenSSH)\b", "SSH", "SSH fournit un canal d’administration distante chiffré. La configuration et l’authentification déterminent la sécurité du service."),
    (r"\b(?:SMTP|mail)\b", "SMTP", "SMTP est le protocole de transport des messages électroniques."),
    (r"\b(?:MySQL|MSSQL|SQL)\b", "Bases de données SQL", "Les bases SQL stockent des données structurées. La gestion des permissions et des entrées utilisateur est essentielle."),
    (r"\bRDP\b", "RDP", "RDP permet l’accès à une session graphique distante sous Windows."),
    (r"\bWinRM\b", "WinRM", "WinRM fournit un mécanisme d’administration distante des systèmes Windows."),
    (r"\b(?:HTTP|HTTPS|HFS|Tomcat|Apache)\b", "Services Web", "Les serveurs Web traitent des requêtes HTTP ou HTTPS. Leur configuration et leur version influencent leur surface d’exposition."),
    (r"\b(?:Nmap|port scan|UDP scan|service enumeration)\b", "Inventaire réseau", "Les résultats d’inventaire décrivent les hôtes, les ports et les services observés dans un périmètre autorisé."),
    (r"\b(?:Wireshark|TShark|ARP)\b", "Trafic réseau", "L’analyse de paquets permet de comprendre les échanges réseau. ARP associe des adresses IP et MAC sur un réseau local."),
    (r"\b(?:Heartbleed|Eternalblue|Bluekeep|Log4j|CVE|Shellshock|vulnerability scanning|vulnérabilités)\b", "Vulnérabilités", "Une vulnérabilité décrit une faiblesse de sécurité. Un indice de scan ne constitue pas à lui seul une confirmation."),
    (r"\b(?:Nessus|WMAP)\b", "Résultats d’audit", "Les outils d’évaluation produisent des résultats qui nécessitent une interprétation et une validation."),
    (r"\b(?:kernel|noyau)\b", "Noyau du système", "Le noyau gère les ressources du système et constitue une frontière importante de sécurité."),
    (r"\bUAC\b", "UAC", "User Account Control contrôle les demandes d’élévation de privilèges sous Windows."),
    (r"\b(?:token|access token)\b", "Access Token", "Un jeton d’accès représente l’identité et les droits associés à un processus Windows."),
    (r"\b(?:SUID)\b", "Permissions SUID", "Le bit SUID modifie l’identité effective d’exécution d’un programme Unix ; il nécessite une gestion rigoureuse."),
    (r"\b(?:cron)\b", "Tâches Cron", "Cron planifie des tâches sur les systèmes Unix. Le propriétaire et les permissions des fichiers associés sont importants."),
    (r"\b(?:credentials?|hashes|hash|hydra|cracking|brute|keylogging|password)\b", "Authentification et identifiants", "Les identifiants et les données d’authentification sont des informations sensibles. Leur exposition constitue un risque de sécurité."),
    (r"\b(?:payloads?|msfvenom|meterpreter|metasploit|msfconsole|armitage)\b", "Environnement Metasploit", "Cette partie concerne le vocabulaire et les composants de l’environnement de laboratoire Metasploit."),
    (r"\b(?:persistence|persistance|backdoored)\b", "Persistance", "La persistance désigne la capacité d’un accès non autorisé à subsister ; sa détection et sa suppression sont des objectifs de défense."),
    (r"\b(?:pivoting|pivot)\b", "Segmentation réseau", "La segmentation limite les communications entre zones et réduit la propagation d’une compromission."),
    (r"\b(?:clearing|obfuscation|shellter|empire)\b", "Visibilité et sécurité", "Cette notion concerne les risques liés à la dissimulation et l’importance de la journalisation et de la détection."),
    (r"\b(?:shells?|TTY|bash|python|perl|netcat)\b", "Interfaces de commande", "Un shell est une interface d’interaction avec un système. Un terminal fournit son environnement d’affichage et de saisie."),
    (r"\b(?:files|folders|fichiers|tmux|transferring)\b", "Fichiers et sessions", "Cette partie concerne la gestion des fichiers et des sessions dans un environnement de laboratoire."),
    (r"\b(?:privilege escalation|privesc)\b", "Privilèges", "Une élévation de privilèges correspond à un changement de niveau d’accès. Le principe du moindre privilège vise à limiter ce risque."),
    (r"\b(?:enumeration|énumération|discovery)\b", "Inventaire", "L’inventaire consiste à relever les informations disponibles sur les éléments du périmètre de test."),
    (r"\b(?:WordPress|WPScan|plugins|themes)\b", "WordPress", "WordPress est un CMS dont le noyau, les extensions et les thèmes constituent des composants distincts."),
    (r"\b(?:Drupal|modules)\b", "Drupal", "Drupal est un CMS modulaire. Les versions, les modules et leurs permissions doivent être suivis."),
    (r"\bXSS\b", "Cross-Site Scripting", "Une XSS est une vulnérabilité liée à l’interprétation de données non fiables dans le navigateur."),
    (r"\b(?:injection|SQLMap)\b", "Injection SQL", "Une injection SQL survient lorsque des données non fiables modifient la structure d’une requête SQL."),
    (r"\b(?:gophish|social engineering)\b", "Social Engineering", "Le social engineering exploite des facteurs humains. La sensibilisation et les mécanismes de vérification contribuent à la prévention."),
    (r"\b(?:windows|win)\b", "Environnement Windows", "Exemple issu des notes sur les caractéristiques et la sécurité de Windows."),
    (r"\b(?:linux|unix)\b", "Environnement Linux", "Exemple issu des notes sur les caractéristiques et la sécurité des systèmes Unix."),
]
def add_note_explanations(soup, article):
    before = [c.get_text() for c in article.select("pre code")]
    stack = []
    previous_heading = None
    count = 0
    contextual = 0
    generic = 0
    for node in list(article.find_all(re.compile(r"^(?:h[1-6]|pre)$"))):
        if node.name != "pre":
            level = int(node.name[1])
            label = node.get_text(" ",strip=True)
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level,label))
            previous_heading = node
            continue
        if node.find("code",recursive=False) is None:
            continue
        # The three already reviewed sections have explicit action descriptions.
        previous = node.find_previous_sibling()
        if previous is not None and "ejpt-action-description" in previous.get("class",[]):
            continue
        if previous is not None and previous.name=="p" and previous.get("data-ejpt-note-description")=="true":
            continue
        source_labels = [label for _,label in stack]
        # Prefer specific original labels; then the nearest source topic.
        match = None
        for label in reversed(source_labels):
            for pattern, topic, desc in note_topics:
                if re.search(pattern,label,re.I):
                    match = (topic,desc)
                    break
            if match:
                break
        if match:
            topic,desc = match
            contextual += 1
        else:
            topic = source_labels[-1] if source_labels else "Notes de laboratoire"
            desc = next((section_context[x] for x in reversed(source_labels) if x in section_context),
                        "Exemple original du cours. À replacer dans le contexte du laboratoire autorisé.")
            generic += 1
        # Guarantee a nearby title without rewriting source code or changing
        # heading IDs that existing internal links reference.
        if previous is None or not re.fullmatch(r"h[1-6]",previous.name or ""):
            count += 1
            label = topic
            h = soup.new_tag("h"+str(min((stack[-1][0]+1) if stack else 3,6)),
                             id="ejpt-context-"+str(count),attrs={"class":"ejpt-context-heading"})
            h.string = label
            node.insert_before(h)
        p = soup.new_tag("p",attrs={"class":"ejpt-action-description","data-ejpt-note-description":"true"})
        p.string = desc
        node.insert_before(p)
    after = [c.get_text() for c in article.select("pre code")]
    if before != after:
        raise RuntimeError("Explanatory presentation changed existing code blocks")
    print("Cheatsheet context:",contextual,"topic descriptions,",generic,"general descriptions")
    return {"topic":contextual,"general":generic,"extra_headings":count}




# Editorial pass over the six existing service-enumeration sections.
# Descriptions identify the tools and concepts; the source examples remain intact.
enumeration_topics = {
    "nmap": ("Inventaire du service avec Nmap", "Nmap présente les ports et les informations disponibles sur les services réseau."),
    "nmblookup": ("Informations NetBIOS", "NetBIOS fournit notamment des mécanismes de nommage utilisés sur certains réseaux."),
    "smbmap": ("Partages réseau et permissions", "SMBMap présente les ressources partagées et les droits associés."),
    "smbclient": ("Client SMB et RPC", "SMBClient et RPCClient sont des interfaces clientes pour les ressources et services Windows."),
    "rpcclient": ("Interface RPC", "RPCClient est un client pour les services RPC Windows."),
    "enum4linux": ("Informations sur les ressources Windows", "Enum4linux présente des informations relatives aux services Windows et Samba."),
    "hydra": ("Authentification — notes Hydra", "Cette partie concerne les risques liés aux mots de passe et les contrôles d’authentification."),
    "metasploit": ("Modules Metasploit du cours", "Extraits originaux du cours associés à ce service. Les exemples sont réservés au laboratoire autorisé."),
    "ftp": ("Client FTP", "Un client FTP permet d’interagir avec le service de transfert de fichiers selon les droits accordés."),
    "ssh": ("Client SSH", "SSH fournit un canal chiffré pour les sessions distantes."),
    "netcat": ("Informations du service avec Netcat", "Netcat est un utilitaire réseau qui interagit avec des connexions TCP ou UDP."),
    "http": ("Outils et clients HTTP", "Ces outils présentent différents aspects des échanges et technologies HTTP."),
    "mysql": ("Client MySQL", "MySQL utilise des sessions SQL pour accéder aux bases de données selon les permissions accordées."),
    "smtp": ("Dialogue SMTP", "Le protocole SMTP définit les échanges entre clients et serveurs de messagerie."),
    "smtp-user-enum": ("Identités et service SMTP", "Cette partie traite de la visibilité des identités par les services de messagerie et des risques associés."),
}
def refine_enumeration(soup, article):
    from collections import Counter
    before = [c.get_text() for c in article.select("pre code")]
    headings = list(article.find_all(re.compile(r"^h[1-6]$")))
    primary = next((h for h in headings if h.name=="h2" and h.get_text(strip=True)=="Énumération"),None)
    complementary = next((h for h in headings if h.name=="h3" and h.get_text(strip=True)=="Énumération" and h.get("id","").startswith("complement-")),None)
    if primary is None or complementary is None:
        raise RuntimeError("Missing original enumeration sections")
    counts = Counter()
    seen_titles = Counter()
    for root in (primary,complementary):
        root_level = int(root.name[1])
        service = None
        duplicate_source_headings = []
        for node in list(root.next_siblings):
            if not getattr(node,"name",None):
                continue
            if re.fullmatch(r"h[1-6]",node.name):
                level = int(node.name[1])
                if level <= root_level:
                    break
                label = node.get_text(" ",strip=True)
                if "ejpt-existing-note-heading" not in node.get("class",[]) and "ejpt-context-heading" not in node.get("class",[]):
                    if level==root_level+1 and label in {"SMB","FTP","SSH","HTTP","SQL","SMTP"}:
                        service = label
                    elif service and label.casefold()==service.casefold():
                        duplicate_source_headings.append(node)
                continue
            if node.name != "pre":
                continue
            code = node.find("code",recursive=False)
            if code is None or service is None:
                continue
            lines = code.get_text().splitlines()
            first = next((line.strip() for line in lines if line.strip()),"")
            first_command = next((line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")),"")
            # Classification is based on the original lead comment/tool only.
            lead = first.casefold()
            command = first_command.casefold()
            if "metasploit" in lead or re.match(r"^(?:msfconsole|use |setg |service postgresql)",command):
                kind = "metasploit"
            elif "hydra" in lead or re.match(r"^(?:hydra|gzip)\b",command):
                kind = "hydra"
            elif "smbmap" in lead or command.startswith("smbmap "):
                kind = "smbmap"
            elif "smb connection" in lead or command.startswith("smbclient "):
                kind = "smbclient"
            elif "rpcclient" in lead or command.startswith("rpcclient "):
                kind = "rpcclient"
            elif "enum4linux" in lead or "null sessions" in lead or command.startswith("enum4linux "):
                kind = "enum4linux"
            elif "nmblookup" in lead or re.match(r"^(?:sudo\s+)?nmblookup\b",command):
                kind = "nmblookup"
            elif "nmap" in lead or re.match(r"^(?:sudo\s+)?nmap\b",command):
                kind = "nmap"
            elif "netcat" in lead or (service=="SSH" and command.startswith("nc ")):
                kind = "netcat"
            elif service=="FTP" and command.startswith("ftp "):
                kind = "ftp"
            elif service=="SSH" and command.startswith("ssh "):
                kind = "ssh"
            elif service=="HTTP" and re.match(r"^(?:whatweb|http|curl|wget|browsh|dirb|lynx)\b",command):
                kind = "http"
            elif service=="SQL" and ("mysql" in lead or command.startswith("mysql ")):
                kind = "mysql"
            elif service=="SMTP" and command.startswith("smtp-user-enum "):
                kind = "smtp-user-enum"
            elif service=="SMTP" and re.match(r"^(?:nc|telnet)\b",command):
                kind = "smtp"
            else:
                # Some source examples are indented or contain prompt markers.
                # Use the nearest original heading for presentation only.
                source_heading = node.find_previous_sibling(lambda el: bool(
                    getattr(el,"name",None) and re.fullmatch(r"h[1-6]",el.name)
                    and "ejpt-existing-note-heading" not in el.get("class",[])
                    and "ejpt-context-heading" not in el.get("class",[])))
                source_label = source_heading.get_text(" ",strip=True).casefold() if source_heading else ""
                kind = {"nmblookup":"nmblookup","nmap":"nmap","smbmap":"smbmap",
                        "smb connection":"smbclient","rpcclient":"rpcclient",
                        "enum4linux":"enum4linux","hydra":"hydra","metasploit":"metasploit",
                        "ftp client":"ftp","netcat":"netcat","ssh":"ssh",
                        "alternative":"http"}.get(source_label)
                if kind is None:
                    # Do not guess what an unmatched block does.
                    kind = "source-"+service.casefold()
                    enumeration_topics[kind] = ("Notes originales — "+service,
                        "Extrait original de cette rubrique, conservé sans interprétation technique.")
                    print("Enumeration label to review:",service,source_label)

            title,desc = enumeration_topics[kind]
            key = (service,kind)
            seen_titles[key] += 1
            if seen_titles[key] > 1:
                title += " — complément "+str(seen_titles[key]-1)
            previous = node.find_previous_sibling()
            if previous is None or previous.name!="p" or "ejpt-action-description" not in previous.get("class",[]):
                raise RuntimeError("Missing enumeration description")
            heading = previous.find_previous_sibling()
            if heading is None or not re.fullmatch(r"h[1-6]",heading.name or ""):
                raise RuntimeError("Missing enumeration label")
            heading.clear()
            heading.append(title)
            heading["class"] = heading.get("class",[]) + ["ejpt-reviewed-enum-title"]
            previous.string = desc
            previous["class"] = previous.get("class",[]) + ["ejpt-reviewed-enum-description"]
            counts[service] += 1
        for heading in duplicate_source_headings:
            # Keep the original fragment identifier without a repeated menu.
            heading.clear()
            heading.name = "span"
            heading["aria-hidden"] = "true"
            heading["class"] = heading.get("class",[]) + ["ejpt-repeated-service-anchor"]
    assert before == [c.get_text() for c in article.select("pre code")], "Enumeration changed original code"
    if set(counts) != {"SMB","FTP","SSH","HTTP","SQL","SMTP"}:
        raise RuntimeError("Enumeration service coverage incomplete")
    print("Enumeration editorial check:",dict(counts))
    return dict(counts)



# Editorial presentation of the existing vulnerability-assessment notes.
# Definitions give context without introducing additional procedures.
def refine_vulnerability_assessment(soup, article):
    before = [c.get_text() for c in article.select("pre code")]
    root = next((h for h in article.find_all("h2") if h.get_text(strip=True)=="Évaluation des vulnérabilités"),None)
    if root is None:
        raise RuntimeError("Missing vulnerability assessment section")
    candidates = []
    for node in root.next_siblings:
        if not getattr(node,"name",None):
            continue
        if node.name=="h2":
            break
        if node.name=="pre":
            candidates.append(node)
    if len(candidates)!=2:
        raise RuntimeError("Unexpected vulnerability assessment source block count")
    descriptions = {
        "# HEARTBLEED": ("Heartbleed", "Vulnérabilité de la gestion des messages Heartbeat dans certaines versions d’OpenSSL, susceptible d’exposer des données en mémoire."),
        "# ETERNALBLUE": ("EternalBlue", "Nom associé à l’exploitation d’une vulnérabilité du protocole SMBv1 sous Windows."),
        "# BLUEKEEP": ("BlueKeep", "Vulnérabilité affectant les services Bureau à distance de certaines versions de Windows."),
        "# LOG4J": ("Log4j", "Bibliothèque de journalisation Java ; certaines versions ont été affectées par la vulnérabilité Log4Shell."),
    }
    combined, reference = candidates
    code=combined.find("code",recursive=False)
    if code is None:
        raise RuntimeError("Missing original vulnerability assessment code")
    old=code.get_text()
    groups=[]
    for line in old.splitlines(keepends=True):
        if line.rstrip("\r\n") in descriptions:
            groups.append((line.rstrip("\r\n"),[line]))
        elif groups:
            groups[-1][1].append(line)
        else:
            raise RuntimeError("Unexpected text before first vulnerability heading")
    if [key for key,_ in groups]!=list(descriptions):
        raise RuntimeError("Vulnerability assessment source headings changed")
    if "".join("".join(lines) for _,lines in groups)!=old:
        raise RuntimeError("Source block reconstruction failed")
    desc=combined.find_previous_sibling()
    heading=desc.find_previous_sibling() if desc else None
    if desc is None or heading is None or "ejpt-action-description" not in desc.get("class",[]) or "ejpt-existing-note-heading" not in heading.get("class",[]):
        raise RuntimeError("Missing original assessment presentation")
    # Keep anchor IDs and the validation marker on the existing heading.
    heading.clear()
    heading.append("Vulnérabilités étudiées")
    desc.string="Les exemples originaux portent sur quatre sujets de sécurité distincts."
    for i,(key,lines) in enumerate(groups,1):
        title,explanation=descriptions[key]
        label=soup.new_tag("p",id="ejpt-va-"+str(i),attrs={"class":"ejpt-va-title"})
        strong=soup.new_tag("strong")
        strong.string=title
        label.append(strong)
        combined.insert_before(label)
        para=soup.new_tag("p",attrs={"class":"ejpt-action-description ejpt-va-description"})
        para.string=explanation
        combined.insert_before(para)
        block=soup.new_tag("pre")
        inner=soup.new_tag("code",attrs={"class":code.get("class",[])})
        inner.string="".join(lines)
        block.append(inner)
        combined.insert_before(block)
    if combined.get("id"):
        combined.insert_before(soup.new_tag("span",id=combined["id"]))
    combined.decompose()
    previous=reference.find_previous_sibling()
    label=previous.find_previous_sibling() if previous else None
    if previous is None or label is None or "ejpt-action-description" not in previous.get("class",[]):
        raise RuntimeError("Missing SearchSploit presentation")
    label.clear()
    label.append("Référence SearchSploit")
    label["class"]=label.get("class",[])+["ejpt-va-title"]
    previous.string="SearchSploit est un outil de consultation de références publiques issues d’Exploit-DB."
    previous["class"]=previous.get("class",[])+["ejpt-va-description"]
    expected=list(before)
    position=expected.index(old)
    expected[position:position+1]=["".join(lines) for _,lines in groups]
    if expected != [c.get_text() for c in article.select("pre code")]:
        raise RuntimeError("Assessment presentation changed original code")
    print("Vulnerability assessment editorial check: 5 labels, original code reconstructed exactly")
    return 5



# Clarify the existing Windows/Linux section hierarchy, without changing code.
system_section_labels = {
    "Windows Exploitation": "Windows — services et vulnérabilités",
    "Linux Exploitation": "Linux — services et vulnérabilités",
    "Windows Privilege Escalation": "Windows — privilèges",
    "Linux Privilege Escalation": "Linux — privilèges",
    "Windows Credential Dumping": "Windows — protection des identifiants",
    "Linux Credential Dumping": "Linux — protection des identifiants",
    "IIS WEBDAV": "IIS et WebDAV",
    "WINRM": "WinRM",
    "SAMBA": "Samba",
    "Kernel": "Noyau du système",
    "Access Token": "Jetons d’accès Windows",
    "Cron Jobs": "Tâches Cron",
    "SUID": "Permissions SUID",
    "UAC": "User Account Control (UAC)",
}
system_section_descriptions = {
    "Windows Exploitation": "Services Windows et vulnérabilités étudiés dans le cours.",
    "Linux Exploitation": "Services Linux et vulnérabilités étudiés dans le cours.",
    "Windows Privilege Escalation": "Modèle de permissions Windows et risques associés aux privilèges.",
    "Linux Privilege Escalation": "Modèle de permissions Unix et risques associés aux privilèges.",
    "Windows Credential Dumping": "Notions relatives à la protection des informations d’authentification Windows.",
    "Linux Credential Dumping": "Notions relatives à la protection des informations d’authentification Linux.",
}
def refine_system_layout(soup, article):
    before = [c.get_text() for c in article.select("pre code")]
    roots = [h for h in article.find_all(["h2","h3"]) if h.get_text(strip=True)=="Pentest système"]
    if len(roots)!=2:
        raise RuntimeError("Missing original system sections")
    counts=[]
    for root in roots:
        changed=0
        described=0
        root_level=int(root.name[1])
        for node in list(root.next_siblings):
            if not getattr(node,"name",None) or not re.fullmatch(r"h[1-6]",node.name):
                continue
            if int(node.name[1])<=root_level:
                break
            if any(c in node.get("class",[]) for c in ("ejpt-existing-note-heading","ejpt-context-heading")):
                continue
            label=node.get_text(" ",strip=True)
            if label not in system_section_labels:
                continue
            # Preserve anchors and any embedded links.
            if node.find("a",href=True):
                continue
            node.clear()
            node.append(system_section_labels[label])
            node["class"]=node.get("class",[])+["ejpt-system-reviewed-heading"]
            changed+=1
            if label in system_section_descriptions:
                p=soup.new_tag("p",attrs={"class":"ejpt-system-section-context"})
                p.string=system_section_descriptions[label]
                node.insert_after(p)
                described+=1
        counts.append({"headings":changed,"descriptions":described})
    if any(c["headings"]<6 or c["descriptions"]<3 for c in counts):
        raise RuntimeError("System heading review incomplete")
    if before!=[c.get_text() for c in article.select("pre code")]:
        raise RuntimeError("System presentation changed original code")
    print("System presentation review:",counts)
    return counts


def simplify_note_titles(soup, article):
    """Keep actual sections collapsible; display leaf labels as plain text."""
    before = [c.get_text() for c in article.select("pre code")]
    stack = []
    simplified = 0
    redundant = 0
    def normal(label):
        return re.sub(r"[\W_]+", "", label.casefold())
    for node in list(article.find_all(re.compile(r"^h[1-6]$"))):
        level = int(node.name[1])
        label = node.get_text(" ",strip=True)
        while stack and stack[-1][0] >= level:
            stack.pop()
        classes = node.get("class",[])
        # These headings were created solely to label a code block.
        # The source sections and the three individually reviewed sections
        # retain their existing accordion controls.
        if ("ejpt-existing-note-heading" in classes or
                "ejpt-context-heading" in classes):
            # Footprinting uses its generated heading as a real parent.
            next_heading = node.find_next_sibling(re.compile(r"^h[1-6]$"))
            if next_heading is not None and "ejpt-footprint-heading" in next_heading.get("class",[]) and int(next_heading.name[1]) > level:
                stack.append((level,label))
                continue
            duplicate = any(normal(label) == normal(parent) for _,parent in stack)
            node.clear()
            if duplicate:
                node.name = "span"
                node["class"] = classes + ["ejpt-redundant-title"]
                node["aria-hidden"] = "true"
                redundant += 1
            else:
                node.name = "p"
                node["class"] = classes + ["ejpt-leaf-title"]
                strong = soup.new_tag("strong")
                strong.string = label
                node.append(strong)
                simplified += 1
        else:
            stack.append((level,label))
    assert before == [c.get_text() for c in article.select("pre code")], "Title formatting changed existing code"
    assert not article.select("h2.ejpt-leaf-title,h3.ejpt-leaf-title,h4.ejpt-leaf-title,h5.ejpt-leaf-title,h6.ejpt-leaf-title")
    print("Cheatsheet leaf labels:",simplified,"plain titles;",redundant,"redundant titles suppressed")
    return {"plain_titles":simplified,"redundant_titles":redundant}


for page in report["pages"]:
    soup=BeautifulSoup((src/page).read_text(encoding="utf-8"),"html.parser")
    article=soup.find("article")
    if article is None:
        raise RuntimeError("Missing article: "+page)
    if page in aliases:
        article.clear()
        article["class"]="ejpt-native-content"
        heading=soup.new_tag("h1")
        heading.string="Cheatsheet eJPTv2"
        article.append(heading)
        paragraph=soup.new_tag("p")
        link=soup.new_tag("a",href=canonical_url)
        link.string="Ouvrir la Cheatsheet eJPTv2"
        paragraph.append(link)
        article.append(paragraph)
    elif page==canonical:
        article=consolidate_sheets(soup,article)
        format_sheet(soup,article)
        format_network_basics(soup,article)
        format_information_gathering(soup,article)
        report["cheatsheet_remaining_headings"]=format_remaining_sections(soup,article)
        report["cheatsheet_footprinting_actions"]=format_footprinting(soup,article)
        report["cheatsheet_context"]=add_note_explanations(soup,article)
        report["cheatsheet_enumeration"]=refine_enumeration(soup,article)
        report["cheatsheet_vulnerability_assessment"]=refine_vulnerability_assessment(soup,article)
        report["cheatsheet_system_layout"]=refine_system_layout(soup,article)
        report["cheatsheet_leaf_titles"]=simplify_note_titles(soup,article)
        report["cheatsheet_display_blocks"]=len(article.select("pre code"))
    before=[x.get_text() for x in article.select("pre code")]
    # Use existing VitePress code styling and native copy interaction.
    for pre in list(article.find_all("pre")):
        code=pre.find("code",recursive=False)
        if code is None:
            continue
        lang=next((x[9:] for x in code.get("class",[]) if x.startswith("language-")),"text")
        if not re.fullmatch(r"[a-zA-Z0-9_+#.-]+",lang):
            lang="text"
        box=soup.new_tag("div",attrs={"class":"language-"+lang+" vp-adaptive-theme"})
        button=soup.new_tag("button",attrs={"class":"copy","title":"Copier le code","aria-label":"Copier le code","type":"button"})
        label=soup.new_tag("span",attrs={"class":"lang"})
        label.string=lang
        pre.wrap(box)
        box.insert(0,button)
        box.insert(1,label)
        pre["class"]=["shiki","shiki-themes","github-dark","vp-code"]
    assert before==[x.get_text() for x in article.select("pre code")],page
    # Raw precompiled HTML is inert, not interpreted as Vue expressions.
    # Encode literal braces so user-provided examples cannot become template expressions.
    # v-pre protects all markup from Vue evaluation.
    article["class"]="ejpt-native-content ejpt-cheatsheet-content" if page==canonical else "ejpt-native-content"
    article["v-pre"]=""
    article["data-ejpt-native"]="true"
    for img in article.find_all("img"):
        img["loading"]="lazy"
        img["decoding"]="async"
        if img.get("src","").endswith("/assets/eJPT-small.png"):
            img["src"]="/skill-issue/ejpt-logo.png"
            img["width"]="100"
            img["height"]="132"
            img["style"]="object-fit:contain"

    title="Cheatsheet eJPTv2" if page in aliases else titles[page[:-5]+".md"]
    heading=article.find("h1")
    if heading is not None and not heading.find(["img","code"]):
        heading.clear()
        heading.append(title)
    # Keep sanitized content as data rather than compiling upstream HTML as
    # a Vue template. This prevents asset import rewriting and interpolation.
    article.attrs.pop("v-pre",None)
    body=str(article)
    parsed=BeautifulSoup(body,"html.parser")
    assert before==[x.get_text() for x in parsed.select("pre code")],page
    dest=target/Path(page).with_suffix(".md")
    dest.parent.mkdir(parents=True,exist_ok=True)
    data_file=dest.with_suffix(".content.json")
    data_file.write_text(json.dumps(body,ensure_ascii=False),encoding="utf-8")
    import_path="./"+data_file.name
    redirect_script = (
        "import { onMounted } from 'vue'\n"
        "onMounted(() => window.location.replace("+json.dumps(canonical_url)+"))\n"
        if page in aliases else ""
    )
    dest.write_text(
        "---\ntitle: "+json.dumps(title,ensure_ascii=False)+"\noutline: deep\n---\n\n"
        "<script setup>\nimport chapterHtml from "+json.dumps(import_path)+"\n"+redirect_script+"</script>\n\n"
        '<div class="ejpt-native-page" data-ejpt-native="true" v-html="chapterHtml"></div>\n',
        encoding="utf-8"
    )
assert len(list(target.rglob("*.md")))==80
(assets/"import-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("Native eJPT pages: 80; verified original images:",count)

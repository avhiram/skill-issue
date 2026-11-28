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
    # Mark source chapter boundaries before the editorial passes rename headings.
    def mark_chapters(part, role):
        seen = set()
        for heading in part.find_all("h2"):
            label = heading.get_text(" ", strip=True)
            if label in sheet_labels and label not in seen:
                heading["data-ejpt-source-chapter"] = label
                heading["data-ejpt-source-role"] = role
                seen.add(label)
        if seen != set(sheet_labels):
            raise RuntimeError("Missing source chapters (" + role + "): " + str(sorted(set(sheet_labels) - seen)))
    mark_chapters(article, "primary")
    mark_chapters(supplement, "supplement")
    # Record original direct subsection identities before translating labels.
    for part, role in ((article, "primary"), (supplement, "supplement")):
        chapter = None
        for heading in part.find_all(["h2", "h3"]):
            if heading.name == "h2":
                chapter = heading.get("data-ejpt-source-chapter")
            elif chapter:
                heading["data-ejpt-source-subsection"] = heading.get_text(" ", strip=True)
                heading["data-ejpt-subsection-chapter"] = chapter
                heading["data-ejpt-subsection-role"] = role
    # All original level-two supplement headings mark boundaries, including CMS.
    for heading in supplement.find_all("h2"):
        heading["data-ejpt-source-boundary"] = "true"
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



# Make long capture-analysis examples easier to read without changing their text.
def refine_network_layout(soup, article):
    before=[c.get_text() for c in article.select("pre code")]
    # Use broad topics already explicitly present in the original notes.
    wireshark={
        "# Filter by ip": ("Adresses IP", "Les filtres d’affichage distinguent les paquets selon les adresses IP."),
        "# Filter by dest ip": ("Adresse IP de destination", "Filtrer les paquets selon leur adresse IP de destination."),
        "# Filter by source ip": ("Adresse IP source", "Filtrer les paquets selon leur adresse IP source."),
        "# Filter by ip addr and port": ("Adresse IP et port", "Combiner les critères d’adresse et de port."),
        "# Filter by tcp port": ("Ports TCP", "Les ports identifient les points de communication des services."),
        "# Filter SYN flag": ("Indicateur SYN", "Repérer les paquets TCP qui portent le flag SYN."),
        "# Broadcast filter": ("Diffusion réseau", "Le broadcast désigne les trames destinées à l’ensemble d’un domaine de diffusion."),
    }
    tshark={
        "# First 100 packets": ("Lecture de la capture", "TShark permet de consulter des captures réseau en ligne de commande."),
        "# Protocl hierarchy statistics": ("Statistiques de protocoles", "La hiérarchie des protocoles résume la composition d’une capture."),
        "# HTTP traffic": ("Trafic HTTP", "Les messages HTTP sont structurés en requêtes et réponses."),
        "# Check session ID": ("Identifiant de session", "Repérer les informations de session présentes dans la capture."),
        "# Check OS/User Agent type": ("Système et User-Agent", "Consulter les informations de système et de navigateur exposées dans les échanges."),
        "# WiFi traffic filter": ("Trafic Wi-Fi", "Filtrer les trames liées aux communications sans fil."),
        "# Only deauthentication packets": ("Trames de désauthentification", "Isoler les trames de désauthentification dans la capture."),
        "# Only WPA handshake packets": ("Handshake WPA", "Repérer les paquets associés à un échange WPA."),
        "# Onyl SSID/BSSID": ("SSID et BSSID", "Consulter les identifiants du réseau et du point d’accès."),
        "# WiFi Channel": ("Canal Wi-Fi", "Identifier le canal utilisé par le réseau sans fil."),
        "# Vendor & model": ("Constructeur et modèle", "Consulter les informations de fabricant et de modèle visibles dans la capture."),
    }
    count=0
    sources=0
    replacement=[]
    for node in list(article.find_all("pre")):
            if not getattr(node,"name",None):
                continue
            if node.name!="pre":
                continue
            code=node.find("code",recursive=False)
            if code is None:
                continue
            old=code.get_text()
            markers=wireshark if "# Filter by ip\n" in old else tshark if "# First 100 packets" in old else None
            if markers is None:
                continue
            groups=[]
            current=["Ouverture et lecture de la capture","Extrait original consacré à l’analyse réseau.",[]]
            for line in old.splitlines(keepends=True):
                key=line.rstrip("\r\n")
                if key in markers:
                    if current[2]:
                        groups.append(current)
                    current=[*markers[key],[]]
                current[2].append(line)
            if current[2]:
                groups.append(current)
            if len(groups)<3 or "".join("".join(g[2]) for g in groups)!=old:
                raise RuntimeError("Network block reconstruction failed")
            sources+=1
            previous=node.find_previous_sibling()
            label=previous.find_previous_sibling() if previous else None
            if previous is not None and label is not None and "ejpt-action-description" in previous.get("class",[]) and "ejpt-existing-note-heading" in label.get("class",[]):
                label.clear()
                label.append("Wireshark" if markers is wireshark else "TShark")
                previous.string="Notes originales sur l’analyse de captures réseau."
            for title,desc,lines in groups:
                count+=1
                h=soup.new_tag("p",id="ejpt-network-note-"+str(count),attrs={"class":"ejpt-network-reviewed-title"})
                b=soup.new_tag("strong")
                b.string=title
                h.append(b)
                node.insert_before(h)
                p=soup.new_tag("p",attrs={"class":"ejpt-action-description ejpt-network-reviewed-description"})
                p.string=desc
                node.insert_before(p)
                block=soup.new_tag("pre")
                inner=soup.new_tag("code",attrs={"class":code.get("class",[])})
                inner.string="".join(lines)
                block.append(inner)
                node.insert_before(block)
            if node.get("id"):
                node.insert_before(soup.new_tag("span",id=node["id"]))
            replacement.append((old,["".join(g[2]) for g in groups]))
            node.decompose()
    expected=list(before)
    for old,new in replacement:
        pos=expected.index(old)
        expected[pos:pos+1]=new
    if expected!=[c.get_text() for c in article.select("pre code")]:
        raise RuntimeError("Network presentation changed original code")
    if sources!=3 or count<9:
        raise RuntimeError("Network capture review incomplete")
    print("Network capture review:",sources,"source blocks;",count,"display groups")
    return {"sources":sources,"groups":count}



# Review the existing Metasploit chapter headings only. Existing examples
# remain in their original order and are not rewritten or expanded.
def refine_framework_layout(soup, article):
    before=[c.get_text() for c in article.select("pre code")]
    roots=[h for h in article.find_all(["h2","h3"]) if h.get_text(" ",strip=True)=="Metasploit"
           and (h.name=="h2" or h.get("id","").startswith("complement-"))]
    if len(roots)!=2:
        raise RuntimeError("Missing original framework sections")
    labels={
        "Info Gathering & Enumeration":"Collecte d’informations et énumération",
        "Vulnerability Scanning":"Évaluation des vulnérabilités",
        "Win Exploitation":"Windows — notes du cours",
        "Linux Exploitation":"Linux — notes du cours",
        "Default MSF Start":"Environnement Metasploit",
        "Post-Exploitation Fundamentals":"Notions de post-exploitation",
        "Win Post-Exploitation":"Post-exploitation — Windows",
        "Linux Post-Exploitation":"Post-exploitation — Linux",
        "WINRM":"WinRM",
        "TOMCAT":"Tomcat",
        "SAMBA":"Samba",
    }
    context={
        "Meterpreter":"Composant de l’environnement Metasploit étudié dans le cours.",
        "Vulnerability Scanning":"Les résultats de scan constituent des indices à vérifier.",
        "Armitage":"Interface graphique historique associée à Metasploit.",
    }
    counts=[]
    for root in roots:
        changed=0
        described=0
        for node in list(root.next_siblings):
            if not getattr(node,"name",None) or not re.fullmatch(r"h[1-6]",node.name):
                continue
            if int(node.name[1])<=int(root.name[1]):
                break
            if any(c in node.get("class",[]) for c in ("ejpt-existing-note-heading","ejpt-context-heading")):
                continue
            label=node.get_text(" ",strip=True)
            if label in labels and not node.find("a",href=True):
                node.clear()
                node.append(labels[label])
                node["class"]=node.get("class",[])+["ejpt-framework-reviewed-heading"]
                changed+=1
            if label in context:
                p=soup.new_tag("p",attrs={"class":"ejpt-framework-context"})
                p.string=context[label]
                node.insert_after(p)
                described+=1
        counts.append({"headings":changed,"descriptions":described})
    if any(c["headings"]<4 or c["descriptions"]<2 for c in counts):
        raise RuntimeError("Framework heading review incomplete")
    if before!=[c.get_text() for c in article.select("pre code")]:
        raise RuntimeError("Framework presentation changed source code")
    print("Framework presentation review:",counts)
    return counts

# Record large existing blocks for subsequent manual presentation review.
# This inventory does not alter any code, command, argument or sequence.
def audit_cheatsheet_block_sizes(article):
    sizes={}
    section="Introduction"
    extra=None
    for node in article.find_all(re.compile(r"^(?:h[23]|pre)$")):
        if node.name=="h2":
            section=node.get_text(" ",strip=True)
            extra=None
        elif node.name=="h3" and section=="Compléments de révision":
            extra=node.get_text(" ",strip=True)
        elif node.name=="pre":
            code=node.find("code",recursive=False)
            if code is None:
                continue
            name=extra or section
            n=sum(bool(line.strip()) for line in code.get_text().splitlines())
            row=sizes.setdefault(name,{"blocks":0,"long":0,"max_lines":0})
            row["blocks"]+=1
            row["long"]+=int(n>=15)
            row["max_lines"]=max(row["max_lines"],n)
    print("Cheatsheet block size review:",sum(x["blocks"] for x in sizes.values()),"blocks;",
          sum(x["long"] for x in sizes.values()),"blocks of 15+ nonempty lines")
    return sizes



# Editorial pass over existing chapter headings, with no changes to examples.
def refine_later_chapters(soup, article):
    before=[c.get_text() for c in article.select("pre code")]
    chapters={
        "Exploitation": {
            "Vulnerability Scanning": "Évaluation des vulnérabilités",
            "Exploits": "Notions d’exploitation",
            "Shells": "Shells",
            "Frameworks": "Frameworks",
            "Win Exploitation": "Windows — notes du cours",
            "Linux Exploitation": "Linux — notes du cours",
            "OPENSSH": "OpenSSH",
            "MYSQL": "MySQL",
            "VSFTPD": "vsftpd",
            "Obfuscation": "Obfuscation — notes du cours",
        },
        "Post-exploitation": {
            "Win Local Enumeration": "Énumération locale Windows",
            "Linux Local Enumeration": "Énumération locale Linux",
            "Transferring Files": "Transfert de fichiers",
            "Shells": "Shells",
            "TTY Shells": "Terminaux TTY",
            "Win Privilege Escalation": "Privilèges Windows",
            "Linux Privilege Escalation": "Privilèges Linux",
            "Win Persistence": "Persistance Windows",
            "Linux Persistence": "Persistance Linux",
            "Dumping & Cracking": "Identifiants — notes du cours",
            "Pivoting": "Pivoting",
            "Clearing Tracks": "Traces et journalisation",
        },
    }
    context={
        "Vulnerability Scanning": "Les résultats d’une analyse doivent être interprétés et vérifiés.",
        "Frameworks": "Les frameworks regroupent différents outils et composants.",
        "Shells": "Un shell est une interface d’interaction avec un système.",
        "Win Local Enumeration": "Inventaire des informations propres à un système Windows.",
        "Linux Local Enumeration": "Inventaire des informations propres à un système Linux.",
        "TTY Shells": "Un terminal TTY fournit une interface de saisie et d’affichage.",
        "Clearing Tracks": "La journalisation et la conservation des traces sont essentielles à l’investigation.",
    }
    result={}
    for chapter,labels in chapters.items():
        roots=[h for h in article.find_all(["h2","h3"])
               if h.get_text(" ",strip=True).casefold()==chapter.casefold()
               and (h.name=="h2" or h.get("id","").startswith("complement-"))]
        if len(roots)!=2:
            raise RuntimeError("Missing original chapter: "+chapter)
        counts=[]
        for root in roots:
            changed=0
            described=0
            for node in list(root.next_siblings):
                if not getattr(node,"name",None) or not re.fullmatch(r"h[1-6]",node.name):
                    continue
                if int(node.name[1])<=int(root.name[1]):
                    break
                if any(c in node.get("class",[]) for c in ("ejpt-existing-note-heading","ejpt-context-heading")):
                    continue
                label=node.get_text(" ",strip=True)
                if label in labels and not node.find("a",href=True):
                    if labels[label]!=label:
                        node.clear()
                        node.append(labels[label])
                        node["class"]=node.get("class",[])+["ejpt-later-reviewed-heading"]
                        changed+=1
                if label in context:
                    p=soup.new_tag("p",attrs={"class":"ejpt-later-section-context"})
                    p.string=context[label]
                    node.insert_after(p)
                    described+=1
            counts.append({"headings":changed,"descriptions":described})
        if any(c["headings"]<4 or c["descriptions"]<2 for c in counts):
            raise RuntimeError("Chapter heading review incomplete: "+chapter)
        result[chapter]=counts
    if before!=[c.get_text() for c in article.select("pre code")]:
        raise RuntimeError("Chapter presentation changed original code")
    print("Later chapter presentation review:",result)
    return result



# Editorial review of the final headings and conceptual descriptions.
# Preserve every original code block, source link and fragment identifier.
def refine_final_chapters(soup, article):
    before=[c.get_text() for c in article.select("pre code")]
    links=[a.get("href") for a in article.find_all("a",href=True)]
    counts={"social":0,"web":0,"cms":0,"titles":0}
    def set_title(node,title):
        if node.get_text(" ",strip=True)==title or node.find("a",href=True):
            return
        node.clear()
        node.append(title)
        node["class"]=node.get("class",[])+["ejpt-final-reviewed-heading"]
        counts["titles"]+=1
    def set_context(node,description,kind):
        following=node.find_next_sibling()
        if following is not None and following.name=="p" and "ejpt-section-description" in following.get("class",[]):
            p=following
        else:
            p=soup.new_tag("p")
            node.insert_after(p)
        p.string=description
        p["class"]=p.get("class",[])+["ejpt-final-context","ejpt-final-"+kind]
        counts[kind]+=1
    def is_generated(node):
        return any(c in node.get("class",[]) for c in ("ejpt-existing-note-heading","ejpt-context-heading"))
    roots=[h for h in article.find_all(["h2","h3"]) if not is_generated(h)]
    for root in roots:
        label=root.get_text(" ",strip=True)
        if label=="Social Engineering":
            set_context(root,"Le social engineering concerne les risques liés à la manipulation humaine, à la confiance et à la sensibilisation.","social")
        elif label=="Pentest Web":
            set_context(root,"Notions de sécurité des applications Web, des services HTTP et des composants applicatifs.","web")
            labels={"Tools":"Outils","Enumeration & Scanning":"Énumération et scanning",
                    "Attacks":"Vulnérabilités Web"}
            for node in list(root.next_siblings):
                if not getattr(node,"name",None) or not re.fullmatch(r"h[1-6]",node.name):
                    continue
                if int(node.name[1])<=int(root.name[1]):
                    break
                if is_generated(node):
                    continue
                name=node.get_text(" ",strip=True)
                if name in labels:
                    set_title(node,labels[name])
    complement=next((h for h in roots if h.get("id")=="complements-de-revision"),None)
    if complement is None:
        raise RuntimeError("Missing complement chapter")
    cms=None
    wp_labels={
        "Basic Information":"Informations générales",
        "Main WordPress Files":"Fichiers WordPress",
        "Users Permissions":"Utilisateurs et permissions",
        "Passive Enumeration":"Énumération passive",
        "Get WordPress version":"Version WordPress",
        "Get Plugins":"Extensions",
        "Get Themes":"Thèmes",
        "Extract versions in general":"Versions des composants",
        "Active enumeration":"Énumération active",
        "Plugins and Themes":"Extensions et thèmes",
        "Users":"Utilisateurs",
    }
    drupal_labels={
        "Version":"Version du CMS",
        "Hidden pages":"Pages et ressources",
        "Installed modules info":"Modules installés",
        "References (tranks to all):":"Références",
    }
    for node in list(complement.next_siblings):
        if not getattr(node,"name",None) or not re.fullmatch(r"h[1-6]",node.name):
            continue
        if int(node.name[1])<=2:
            break
        if is_generated(node):
            continue
        label=node.get_text(" ",strip=True)
        if node.name=="h3":
            if label.casefold()=="wordpress":
                cms="wp"
                set_title(node,"WordPress")
                set_context(node,"CMS organisé autour d’un noyau, de thèmes, d’extensions et de rôles utilisateurs.","cms")
                continue
            if label.casefold()=="drupal":
                cms="drupal"
                set_context(node,"CMS modulaire dont la sécurité dépend notamment des versions, des modules et des permissions.","cms")
                continue
            if cms=="drupal" and label in ("Discovery","Énumération","Enumeration"):
                set_title(node,"Drupal — découverte" if label=="Discovery" else "Drupal — énumération")
                continue
            cms=None
        if cms=="wp" and label in wp_labels:
            set_title(node,wp_labels[label])
        elif cms=="drupal" and label in drupal_labels:
            set_title(node,drupal_labels[label])
    if counts["social"]!=2 or counts["web"]!=2 or counts["cms"]!=2 or counts["titles"]<4:
        raise RuntimeError("Final chapter heading coverage incomplete: "+str(counts))
    if before!=[c.get_text() for c in article.select("pre code")]:
        raise RuntimeError("Final chapter presentation changed original code")
    if links!=[a.get("href") for a in article.find_all("a",href=True)]:
        raise RuntimeError("Final chapter presentation changed source links")
    print("Final chapter presentation review:",counts)
    return counts


def refine_long_blocks(soup, article):
    """Split long source blocks at existing section markers without changing their text."""
    before = [c.get_text() for c in article.select("pre code")]
    original_pres = list(article.find_all("pre"))
    expected = list(before)
    position = 0
    reviewed = 0
    split_count = 0
    created_blocks = 0
    retained = 0

    label_map = {
        "msf meterpreter": "Session Meterpreter",
        "linux shell - run 'shell' in meterpreter": "Shell Linux",
        "system": "Informations système",
        "users": "Utilisateurs",
        "network": "Réseau",
        "services": "Services",
        "metasploit": "Metasploit",
        "linenum - automatic enumeration": "Énumération automatique avec LinEnum",
        "win cmd - run 'shell' in meterpreter": "Invite de commandes Windows",
        "jaws - automatic local enumeration - powershell": "Énumération automatique avec JAWS",
        "exploitation": "Exploitation",
        "on target system": "Exécution sur le système cible",
        "run payload.exe": "Lancement du payload",
        "metasploit - meterpreter": "Session Meterpreter",
        "creds dumping - meterpreter": "Collecte des identifiants",
        "mimikatz": "Mimikatz",
        "pass the hash": "Pass the Hash",
        "service enumeration": "Énumération des services",
        "ftp": "FTP",
        "smb": "SMB",
        "http": "HTTP",
        "mysql": "MySQL",
        "ssh": "SSH",
        "smtp": "SMTP",
        "msfconsole": "Console Metasploit",
        "switch between sessions ids with": "Gestion des sessions",
        "rename sessions": "Renommer une session",
        "run a meterpreter command on the session given with -i": "Commande sur une session",
        "terminate a specific session": "Fermer une session",
        "terminate all sessions": "Fermer toutes les sessions",
        "upgrade a shell session to a meterpreter session": "Conversion en Meterpreter",
        "workspaces - db_status must be connected": "Workspaces",
        "dirbuster": "Dirbuster",
        "curl": "Requêtes HTTP avec cURL",
        "gobuster": "Gobuster",
        "ffuf": "Ffuf",
        "directory discovery:": "Découverte de répertoires",
        "file discovery:": "Découverte de fichiers",
        "output of responses with status code:": "Filtrage par code HTTP",
        "the -maxtime flag offers to end the ongoing fuzzing after the specified time in seconds:": "Durée maximale du fuzzing",
        "number of threads:": "Nombre de threads",
        "nikto": "Nikto",
        "wpscan": "WPScan",
        "targeting smb": "Analyse SMB",
        "brute-force smb": "Authentification SMB",
        "enumeration": "Énumération",
        "smb login with <user>": "Connexion SMB avec identifiants",
        "without <user>:<pw>, exploit a vulnerability, e.g. eternalblue": "Vulnérabilité SMB",
        "targeting vsftpd": "Analyse vsftpd",
        "try anonymous:anonymous": "Accès anonyme",
        "exploit vsftpd": "Référence vsftpd",
        "enumerate smtp - msfconsole": "Énumération SMTP",
        "brute-force ftp": "Authentification FTP",
        "modify the shell via ftp": "Transfert du fichier",
        "change the $ip & $port variable to the attacker's ip & port": "Paramètres du fichier",
        "attacker listener": "Listener Netcat",
        "metasploit mysql": "Modules MySQL",
        "ms sql": "Microsoft SQL Server",
        "global set": "Paramètres globaux",
        "set options depends on the selected module": "Options du module",
        "meterpreter - 'root' user": "Session Meterpreter privilégiée",
        "local machine enumeration": "Énumération locale",
        "targeting mysql (wordpress)": "Analyse MySQL",
        "brute-force mysql - msfconsole": "Authentification MySQL",
        "mysql login with <user>": "Connexion MySQL",
        "attacker's machine - find target ip": "Préparation de la machine de test",
        "port scanning - 1000 common ports or more advanced scans": "Scan des ports",
        "banner grabbing": "Bannières des services",
        "exploitable vulnerabilities modules": "Modules de vulnérabilités",
        "msfconsole meterpreter privesc": "Vérification des privilèges",
        "uac - uacme": "UACMe",
        "metasploit - listening": "Configuration du handler",
        "meterpreter (unprivileged session)": "Session non privilégiée",
        "elevated meterpreter received on the listening session": "Session élevée",
        "persistence": "Persistance",
        "meterpreter - manual": "Session Meterpreter",
        "ssh key": "Clé SSH",
        "persistence test": "Vérification de la persistance",
        "exit all the msfconsole sessions and close it": "Fermeture des sessions",
        "searchsploit - install": "Installation de SearchSploit",
        "update": "Mise à jour",
        "copy an exploit to the current working dir": "Copier un exploit",
        "case sensitive search": "Recherche sensible à la casse",
        "search just the exploit title": "Recherche par titre",
        "exact search on title": "Recherche exacte",
        "filters search": "Recherche filtrée",
        "list online links": "Liens en ligne",
        "targeting openssh": "Analyse SSH",
        "brute-force ssh": "Authentification SSH",
        "ssh login with <user>": "Connexion SSH",
        "win": "Commandes Windows",
        "ctrl+z to background": "Mettre la session en arrière-plan",
        "targeting iis/ftp": "Analyse IIS et FTP",
        "generate an .asp reverse shell payload": "Génération du fichier ASP",
        "ftp login with <user>": "Connexion FTP",
        "open http://<target_ip>/shell.aspx . a reverse shell may be received.": "Accès au fichier transféré",
        "nmap": "Nmap",
        "microsoft sql": "Microsoft SQL Server",
        "port scan example": "Scan des ports",
        "pivoting to target2 through target1": "Pivoting",
        "winrm": "WinRM",
        "brute force winrm login": "Authentification WinRM",
        "launch command": "Exécution de commande",
        "sqlmap": "SQLMap",
        "list databases": "Lister les bases de données",
        "xsser": "XSSer",
        "authenticated xsser": "Tests authentifiés",
        "hydra - basic auth attacks (brute-force)": "Authentification HTTP",
        "null sessions": "Null Sessions",
        "enumerate wordpress using wpscan": "Énumération WordPress",
        "upload reverse shell to wordpress": "Fichier de thème WordPress",
        "upload using metasploit": "Modules Metasploit",
        "manual exploit - autoblue": "AutoBlue",
        "access token impersonation": "Access Token Impersonation",
        "metasploit - meterpreter (unprivileged session)": "Session Meterpreter non privilégiée",
        "automation": "Automatisation",
        "create a handler resource": "Créer un fichier resource",
        "insert the following lines": "Configuration du handler",
        "save it and exit": "Enregistrer le fichier",
        "export inserted msfconsole commands into a resource script": "Exporter les commandes",
        "kiwi - meterpreter": "Kiwi",
        "mimikatz - meterpreter": "Mimikatz",
        "port forwarding": "Port Forwarding",
        "target2 exploitation": "Test de la cible secondaire",
        "targeting php": "Analyse PHP",
        "browse": "Navigation",
        "manual exploitation php cgi": "PHP CGI",
        "if it executes, modify the .py script": "Vérification du résultat",
        "php reverse shell": "PHP Reverse Shell",
        "attacker listener in another tab": "Listener Netcat",
        "launch the exploit": "Lancement du test",
        "gobuster - install": "Installation de Gobuster",
        "dirbuster - install": "Installation de Dirbuster",
        "nikto - install": "Installation de Nikto",
        "burpsuite - install": "Installation de Burp Suite",
        "sqlmap - install": "Installation de SQLMap",
        "xsser - install": "Installation de XSSer",
        "wpscan - install": "Installation de WPScan",
        "hydra - install": "Installation de Hydra",
        "spawn shells": "Spawn Shells",
        "smb connection": "Connexion SMB",
        "smbclient": "Client SMB",
        "rpcclient": "Client RPC",
        "bypass uac": "UAC Bypass",
        "administrative privileges required!": "Privilèges administrateur",
        "rdp - meterpreter": "RDP",
        "regain access": "Reprise de session",
        "enabling rdp": "Activation de RDP",
        "netcat - install": "Installation de Netcat",
        "nc listener": "Listener Netcat",
        "transfer files": "Transfert de fichiers",
        "download the 'id_rsa' file": "Téléchargement de la clé SSH",
        "cron jobs": "Tâches Cron",
        "setup a 'nc' listener and wait for the bash reverse shell": "Listener Netcat",
        "windows c:\\temp - metasploit e.g.": "Nettoyage Windows",
        "cleanup meterpreter rc file:": "Nettoyage des fichiers RC",
        "linux /tmp": "Nettoyage Linux",
        "johnthe ripper": "John the Ripper",
        "checking routes": "Vérification des routes",
        "adding manual routes": "Routes statiques",
        "meterpreter on target1": "Session sur la cible intermédiaire",
        "meterpreterport forwarding": "Port Forwarding",
        "filter by ip": "Adresses IP",
        "filter by dest ip": "Adresse IP de destination",
        "filter by source ip": "Adresse IP source",
        "filter by ip addr and port": "Adresse IP et port",
        "filter by tcp port": "Ports TCP",
        "filter syn flag": "Indicateur SYN",
        "broadcast filter": "Diffusion réseau",
        "first 100 packets": "Lecture de la capture",
        "protocl hierarchy statistics": "Statistiques de protocoles",
        "http traffic": "Trafic HTTP",
        "check session id": "Identifiant de session",
        "check os/user agent type": "Système et User-Agent",
        "wifi traffic filter": "Trafic Wi-Fi",
        "only deauthentication packets": "Trames de désauthentification",
        "only wpa handshake packets": "Handshake WPA",
        "onyl ssid/bssid": "SSID et BSSID",
        "wifi channel": "Canal Wi-Fi",
        "vendor & model": "Constructeur et modèle",
    }

    description_map = {
        "Informations système": "Consulter les informations du système et sa configuration.",
        "Utilisateurs": "Consulter les comptes, groupes et sessions utilisateurs.",
        "Réseau": "Consulter les interfaces, routes et connexions réseau.",
        "Services": "Repérer les processus et services actifs.",
        "Session Meterpreter": "Commandes et informations issues d’une session Meterpreter.",
        "Shell Linux": "Commandes exécutées dans un shell Linux.",
        "Invite de commandes Windows": "Commandes exécutées dans l’invite de commandes Windows.",
        "Énumération automatique avec LinEnum": "Repères sur l’outil d’inventaire Linux LinEnum.",
        "Énumération automatique avec JAWS": "Repères sur l’outil d’inventaire Windows JAWS.",
        "Énumération des services": "Regrouper les modules par service réseau.",
        "Paramètres globaux": "Définir les paramètres réutilisés par les modules.",
        "Options du module": "Renseigner les options propres au module sélectionné.",
        "Scan des ports": "Identifier les ports et services visibles dans le périmètre de test.",
        "Bannières des services": "Lire les informations de bannière exposées par un service.",
        "Collecte des identifiants": "Repères sur les informations d’authentification présentes sur le système.",
        "Pass the Hash": "Notions liées à l’utilisation d’un hash comme élément d’authentification.",
        "Trafic HTTP": "Les messages HTTP sont structurés en requêtes et réponses.",
        "Trafic Wi-Fi": "Filtrer les trames liées aux communications sans fil.",
        "Handshake WPA": "Repérer les paquets associés à un échange WPA.",
        "SSID et BSSID": "Consulter les identifiants du réseau et du point d’accès.",
        "Canal Wi-Fi": "Identifier le canal utilisé par le réseau sans fil.",
        "Constructeur et modèle": "Consulter les informations de fabricant et de modèle visibles dans la capture.",
        "Découverte de répertoires": "Rechercher les chemins Web présents dans le périmètre de test.",
        "Filtrage par code HTTP": "Limiter les résultats aux codes de réponse HTTP pertinents.",
        "Durée maximale du fuzzing": "Limiter la durée d’une recherche automatisée.",
        "Nombre de threads": "Régler le nombre de tâches concurrentes.",
        "Authentification SMB": "Repères sur les mécanismes d’authentification SMB.",
        "Authentification FTP": "Repères sur les mécanismes d’authentification FTP.",
        "Authentification SSH": "Repères sur les mécanismes d’authentification SSH.",
        "Authentification WinRM": "Repères sur les mécanismes d’authentification WinRM.",
        "Installation de Burp Suite": "Installation de l’outil d’analyse Web Burp Suite.",
        "Installation de Netcat": "Installation de l’utilitaire réseau Netcat.",
        "Transfert de fichiers": "Échanges de fichiers dans le laboratoire.",
        "Tâches Cron": "Tâches planifiées sur les systèmes Unix.",
        "Nettoyage Windows": "Extrait original relatif aux fichiers temporaires Windows.",
        "Nettoyage Linux": "Extrait original relatif aux fichiers temporaires Linux.",
    }

    def count_lines(lines):
        return sum(bool(line.strip()) for line in lines)

    def is_marker(line):
        match = re.match(r"^\s*#{1,3}\s+(.+?)\s*$", line)
        if not match:
            return False
        label = match.group(1).strip()
        if re.match(r"^(?:LHOST|LPORT|[1-5]\s*[-.)]|and devices\b|or upload\b|this is another way\b)", label, re.I):
            return False
        return True

    def merge_short(groups):
        groups = [g for g in groups if g]
        i = 0
        while i < len(groups) and len(groups) > 1:
            if count_lines(groups[i]) < 2:
                if i + 1 < len(groups):
                    groups[i + 1] = groups[i] + groups[i + 1]
                    groups.pop(i)
                else:
                    groups[i - 1].extend(groups[i])
                    groups.pop(i)
                continue
            i += 1
        return groups

    def split_markers(lines):
        groups = []
        current = []
        for line in lines:
            if is_marker(line) and current and count_lines(current) >= 2:
                groups.append(current)
                current = []
            current.append(line)
        if current:
            groups.append(current)
        return merge_short(groups)

    def split_blank_lines(lines):
        groups = []
        current = []
        pending = []
        for line in lines:
            if not line.strip():
                pending.append(line)
                continue
            if pending and count_lines(current) >= 3:
                current.extend(pending)
                groups.append(current)
                current = [line]
            else:
                current.extend(pending)
                current.append(line)
            pending = []
        current.extend(pending)
        if current:
            groups.append(current)
        return merge_short(groups)

    def manual_groups(lines):
        first = next((line.strip() for line in lines if line.strip()), "")
        if first == "# Spawn shells":
            one = next((i for i,line in enumerate(lines) if line.strip().startswith("import socket,subprocess,os;")), None)
            two = next((i for i,line in enumerate(lines) if line.strip().startswith("/usr/bin/script -qc /bin/bash /dev/null")), None)
            if one is not None and two is not None and one < two:
                return [
                    (lines[:one+1], "Python", "Exemples originaux de création de shell avec Python."),
                    (lines[one+1:two+1], "Shells et PHP", "Autres exemples originaux de shell et d’interpréteur."),
                    (lines[two+1:], "Perl, Ruby, Lua et outils", "Variantes utilisant différents interpréteurs et utilitaires."),
                ]
        if first == "# meterpreter > <command>":
            one = next((i for i,line in enumerate(lines) if line.strip() == "getenv PATH"), None)
            two = next((i for i,line in enumerate(lines) if i > (one if one is not None else -1) and line.strip() == "ifconfig"), None)
            if one is not None and two is not None:
                return [
                    (lines[:one+1], "Commandes générales Meterpreter", "Commandes courantes de navigation et d’environnement."),
                    (lines[one+1:two+1], "Identité et réseau", "Informations sur l’identité, les privilèges et le réseau."),
                    (lines[two+1:], "Fichiers et processus", "Commandes de gestion des fichiers, processus et sessions."),
                ]
        return None

    def split_block(lines):
        manual = manual_groups(lines)
        if manual:
            return manual
        groups = split_markers(lines)
        if len(groups) == 1:
            groups = split_blank_lines(lines)
        else:
            refined = []
            for group in groups:
                if count_lines(group) >= 15:
                    refined.extend(split_blank_lines(group))
                else:
                    refined.append(group)
            groups = merge_short(refined)
        return [(group, None, None) for group in groups]

    def title_and_description(group, title_override=None, description_override=None):
        first = next((line.strip() for line in group if line.strip()), "")
        if title_override:
            title = title_override
        elif is_marker(first):
            raw = re.sub(r"^\s*#{1,3}\s*", "", first).strip()
            key = re.sub(r"\s+", " ", raw).casefold()
            title = label_map.get(key, raw)
            if len(title) > 68:
                title = title[:65].rstrip() + "…"
        else:
            command = first.split(None, 1)[0].casefold() if first else ""
            inferred = {
                "nmap": "Nmap",
                "smbclient": "Client SMB",
                "smbmap": "SMBMap",
                "enum4linux": "Enum4linux",
                "rpcclient": "Client RPC",
                "hydra": "Hydra",
                "curl": "cURL",
                "gobuster": "Gobuster",
                "ffuf": "Ffuf",
                "nikto": "Nikto",
                "wpscan": "WPScan",
                "sqlmap": "SQLMap",
                "nc": "Netcat",
                "msfconsole": "Console Metasploit",
                "use": "Modules Metasploit",
                "mysql": "Client MySQL",
                "ftp": "Client FTP",
                "ssh": "Client SSH",
            }
            title = inferred.get(command, "Commandes complémentaires")
        description = description_override or description_map.get(
            title, "Extrait original de cette sous-partie, conservé dans son ordre initial."
        )
        return title, description

    for pre in original_pres:
        code = pre.find("code")
        if code is None:
            continue
        old = code.get_text()
        lines = old.splitlines(keepends=True)
        if count_lines(lines) < 15:
            position += 1
            continue
        reviewed += 1
        groups = split_block(lines)
        contents = ["".join(group) for group,_,_ in groups]
        if len(contents) < 2 or "".join(contents) != old:
            retained += 1
            position += 1
            continue
        if pre.get("id"):
            pre.insert_before(soup.new_tag("span", id=pre["id"]))
        for group,title_override,description_override in groups:
            title,description = title_and_description(group,title_override,description_override)
            label = soup.new_tag("p", attrs={"class":"ejpt-long-block-title"})
            strong = soup.new_tag("strong")
            strong.string = title
            label.append(strong)
            pre.insert_before(label)
            para = soup.new_tag("p", attrs={"class":"ejpt-action-description"})
            para.string = description
            pre.insert_before(para)
            new_pre = soup.new_tag("pre", attrs={k:v for k,v in pre.attrs.items() if k != "id"})
            new_code = soup.new_tag("code", attrs=dict(code.attrs))
            new_code.string = "".join(group)
            new_pre.append(new_code)
            pre.insert_before(new_pre)
        pre.decompose()
        expected[position:position+1] = contents
        position += len(contents)
        split_count += 1
        created_blocks += len(contents) - 1

    actual = [c.get_text() for c in article.select("pre code")]
    if expected != actual:
        raise RuntimeError("Long-block presentation changed original code or order")
    remaining = []
    for pre in article.find_all("pre"):
        code = pre.find("code")
        if code is None:
            continue
        lines = code.get_text().splitlines()
        count = count_lines(lines)
        if count >= 15:
            first = next((line.strip() for line in lines if line.strip()), "")
            remaining.append({"lines":count,"first_line":first})
    after_long = len(remaining)
    print("Long-block review:", reviewed, "candidates;", split_count, "split;", created_blocks,
          "additional blocks;", retained, "kept intact;", after_long, "still at 15+ lines")
    if remaining:
        for item in remaining:
            print("Remaining long block:", item["lines"], "lines;", item["first_line"])
    return {
        "reviewed":reviewed,
        "split":split_count,
        "created_blocks":created_blocks,
        "retained":retained,
        "before_long":reviewed,
        "after_long":after_long,
        "remaining":remaining,
        "preserved":True,
    }


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


EJPT_TEXT_TRANSLATIONS = json.loads(r'''{"⬇️ Feel free to download the version of your choice and kindly mention my blog when utilizing it":"Téléchargez la version de votre choix et pensez à mentionner mon blog lorsque vous l’utilisez.","Routing":"Routage","Connect and Scan":"Connexion et scan","Passive":"Reconnaissance passive","Host Discovery":"Découverte d’hôtes","Network Discovery":"Découverte réseau","SMB Connection":"Connexion SMB","Ftp Client":"Client FTP","Alternative":"Autres outils","Vulnerability Assessment":"Évaluation des vulnérabilités","Host Based Attacks":"Attaques sur les systèmes","Windows Exploitation":"Exploitation Windows","Windows Privilege Escalation":"Élévation de privilèges Windows","Kernel":"Noyau","Windows Credential Dumping":"Extraction d’identifiants Windows","Linux Exploitation":"Exploitation Linux","Linux Privilege Escalation":"Élévation de privilèges Linux","Cron Jobs":"Tâches Cron","Linux Credential Dumping":"Extraction d’identifiants Linux","Network Based Attacks":"Attaques réseau","Info Gathering & Enumeration":"Collecte d’informations et énumération","Vulnerability Scanning":"Scan de vulnérabilités","MSFVenom shells":"Shells avec MSFVenom","MSF Staged and Non Staged Payload":"Payloads staged et non-staged","Win Exploitation":"Exploitation Windows","Default MSF Start":"Démarrage de Metasploit","Post-Exploitation Fundamentals":"Bases de la post-exploitation","Win Post-Exploitation":"Post-exploitation Windows","To search for files and Folders":"Rechercher des fichiers et des dossiers","Win Local Enumeration":"Énumération locale Windows","Linux Local Enumeration":"Énumération locale Linux","Transferring Files":"Transfert de fichiers","Win Privilege Escalation":"Élévation de privilèges Windows","Win Persistence":"Persistance Windows","Linux Persistence":"Persistance Linux","Dumping & Cracking":"Extraction et cracking","Clearing Tracks":"Effacement des traces","Web Application Penetration Testing":"Pentest Web","Tools":"Outils","Enumeration & Scanning":"Énumération et scan","Attacks":"Attaques","Check if injection exists":"Vérifier la présence d’une injection","Get database if injection Exists":"Extraire la base de données en cas d’injection","Get Tables in a Database":"Lister les tables d’une base de données","Get data in a Database tables":"Extraire les données des tables d’une base de données","Get OS-Shell":"Obtenir un OS shell","Check an example:":"Exemple :","Hijack cookie through xss":"Détournement de cookie via XSS","Wordpress":"WordPress","Basic Information":"Informations générales","Main WordPress Files":"Fichiers principaux de WordPress","Users Permissions":"Rôles et permissions","Passive Enumeration":"Énumération passive","Get WordPress version":"Identifier la version de WordPress","Get Plugins":"Identifier les plugins","Get Themes":"Identifier les thèmes","Extract versions in general":"Identifier les versions","Active enumeration":"Énumération active","Plugins and Themes":"Plugins et thèmes","Users":"Utilisateurs","ID Brute":"Énumération des utilisateurs par ID","Login username enumeration":"Énumération des noms d’utilisateur à la connexion","Discovery":"Découverte","Username enumeration":"Énumération des noms d’utilisateur","Register":"Inscription","Request new password":"Demander un nouveau mot de passe","Get number of users":"Nombre d’utilisateurs","Hidden pages":"Pages cachées","Installed modules info":"Informations sur les modules installés","Automatic":"Automatique","With PHP Filter Module":"Avec le module PHP Filter","Install PHP Filter Module":"Installer le module PHP Filter","Backdoored Module":"Module avec backdoor","Post Exploitation":"Post-exploitation","Post exploitation":"Post-exploitation","Read settings.php":"Lire le fichier settings.php","Dump users from DB":"Extraire les utilisateurs de la base de données","References (tranks to all):":"Références :","Info":"Information","Warning":"Avertissement","We can use a wordlist generator tools (how ":"Il est possible d’utiliser un générateur de wordlists (par exemple, ","), to create custom wordlists.":") pour créer des wordlists personnalisées.","there are four components as follows:":"Cette méthode repose sur quatre éléments :","attacker client pc":"poste client de l’attaquant","attacker logging server":"serveur de journalisation de l’attaquant","vulnerable server":"serveur vulnérable","victim client pc":"poste client de la victime","attacker: first finds a vulnerable server and its breach point.":"Attaquant : repérer d’abord un serveur vulnérable et son point d’entrée exploitable.","attacker: enter the following snippet in order to hijack the cookie kepts by victim client pc (p.s.: the ip address, 192.168.99.102, belongs to attacker logging server in this example):":"Attaquant : saisir l’extrait suivant pour intercepter le cookie conservé par le navigateur de la victime. (Remarque : l’adresse IP 192.168.99.102 correspond ici au serveur de journalisation de l’attaquant) :","attacker: log into attacker logging server (P.S.: it is 192.168.99.102 in this example), and execute the following command:":"Attaquant : se connecter au serveur de journalisation (192.168.99.102 dans cet exemple), puis exécuter la commande suivante :","attacker: when victim client pc browses the vulnerable server, check the output of the command above.":"Attaquant : lorsque le poste de la victime consulte le serveur vulnérable, vérifier le résultat de la commande précédente.","attacker: after obtaining the victim’s cookie, utilize a firefox’s add-on called Cookie Quick Manager to change to the victim’s cookie in an effort to hijack the victim’s privilege.":"Attaquant : après avoir obtenu le cookie de la victime, utiliser l’extension Firefox Cookie Quick Manager pour remplacer le cookie du navigateur par celui de la victime et reprendre sa session.","Uploaded":"Les fichiers téléversés"," files go to: ":" sont enregistrés dans : ","Themes files can be found in /wp-content/themes/,":"Les fichiers des thèmes se trouvent dans /wp-content/themes/,"," so if you change some php of the theme to get RCE you probably will use that path. For example: Using ":" si vous modifiez un fichier PHP du thème pour obtenir une RCE, ce chemin pourra être utilisé. Par exemple, avec le thème "," you can ":" vous pouvez ","access":"accéder à"," the ":" "," file in: ":" : ","Another useful url could be:":"Autre URL utile :","In ":"Dans "," you can find the root password of the database.":" vous pouvez retrouver le mot de passe root de la base de données.","Default login paths to check: ":"Chemins de connexion par défaut : "," contains useful information such as the version WordPress installed.":" contient des informations utiles, notamment la version de WordPress installée."," is used for the email activation process when setting up a new WordPress site.":" sert à l’activation par e-mail lors de la création d’un site WordPress.","Login folders (may be renamed to hide it):\n":"Répertoires de connexion (ils peuvent être renommés pour les masquer) :\n"," is a file that represents a feature of WordPress that enables data to be transmitted with HTTP acting as the transport mechanism and XML as the encoding mechanism. This type of communication has been replaced by the WordPress ":" est un fichier correspondant à une fonctionnalité de WordPress qui permet de transmettre des données via HTTP, avec XML comme format d’encodage. Cette communication a été remplacée par la "," folder is the main directory where plugins and themes are stored.":" contient les plugins et les thèmes."," Is the directory where any files uploaded to the platform are stored.":" contient les fichiers téléversés sur la plateforme."," This is the directory where core files are stored, such as certificates, fonts, JavaScript files, and widgets.":" contient les fichiers du cœur de WordPress, notamment les certificats, les polices, les fichiers JavaScript et les widgets."," file contains information required by WordPress to connect to the database such as the database name, database host, username and password, authentication keys and salts, and the database table prefix. This configuration file can also be used to activate DEBUG mode, which can useful in troubleshooting.":" contient les informations nécessaires à WordPress pour se connecter à la base de données : nom de la base, hôte, identifiant et mot de passe, clés et salts d’authentification, ainsi que préfixe des tables. Ce fichier permet également d’activer le mode DEBUG, utile pour le dépannage.",": Publish and manages his and others posts":": peut publier et gérer ses propres articles ainsi que ceux des autres.",": Publish and manage his own posts":": peut publier et gérer ses propres articles.",": Write and manage his posts but cannot publish them":": peut rédiger et gérer ses articles, mais ne peut pas les publier.",": Browser posts and edit their profile":": peut consulter les articles et modifier son profil.","Check if you can find the files ":"Vérifier la présence des fichiers "," or ":" ou ","Inside the ":"Dans le ","source code":"code source"," of the page (example from ":" de la page (exemple : ","Meta name":"Balise meta","CSS link files":"Fichiers CSS référencés","JavaScript files":"Fichiers JavaScript","You probably won't be able to find all the Plugins and Themes passible. In order to discover all of them, you will need to ":"Il est peu probable de trouver tous les plugins et thèmes uniquement par observation. Pour les découvrir, il faudra ","actively Brute Force a list of Plugins and Themes":"tester activement une liste de plugins et de thèmes par brute force"," (hopefully for us there are automated tools that contains this lists).":" (des outils automatisés peuvent fournir ces listes).","You get valid users from a WordPress site by Brute Forcing users IDs:":"Il est possible d’identifier des utilisateurs WordPress en testant une série d’IDs :","If the responses are ":"Si les réponses sont ",", that means that the id is ":", cela signifie que l’ID est ",". If the the response is ":". Si la réponse est ",", then the id is ":", l’ID est alors ","You can also try to get information about the users by querying:":"Il est également possible de récupérer des informations sur les utilisateurs en interrogeant :","Only information about the users that has this feature enable will be provided":"Seules les informations des utilisateurs pour lesquels cette fonctionnalité est activée seront renvoyées.","Also note that ":"À noter également : "," could leak IP addresses.":" peut exposer des adresses IP.","When login in ":"Lors de la connexion à "," is ":" varie "," is the indicated ":" ","username exists or not":"nom d’utilisateur existe ou non","Check ":"Vérifier ","meta":"meta","Node":"Nœud",": Drupal ":": Drupal ","indexes its content using nodes":"organise son contenu à l’aide de nœuds",". A node can ":". Un nœud peut ","hold anything":"contenir tout type de contenu"," such as a blog post, poll, article, etc. The page URIs are usually of the form ":" comme un billet de blog, un sondage ou un article. Les URI des pages suivent généralement le format ","Drupal supports ":"Drupal propose ","three types of users":"trois types d’utilisateurs"," by default:":" par défaut :",": This user has complete control over the Drupal website.":": cet utilisateur dispose d’un contrôle complet sur le site Drupal.",": These users can log in to the website and perform operations such as adding and editing articles based on their permissions.":": ces utilisateurs peuvent se connecter au site et effectuer des opérations comme ajouter ou modifier des articles, selon leurs permissions.",": All website visitors are designated as anonymous. By default, these users are only allowed to read posts.":": tous les visiteurs du site sont considérés comme anonymes. Par défaut, ils peuvent uniquement lire les publications.","Newer installs of Drupal by default block access to the ":"Les installations récentes de Drupal bloquent par défaut l’accès aux fichiers "," and ":" et "," files.":"."," just try to create a username and if the name is already taken it will be notified:":" essayez simplement de créer un nom d’utilisateur ; si celui-ci est déjà utilisé, le site vous l’indiquera :","If you request a new password for an existing username:":"Si vous demandez un nouveau mot de passe pour un nom d’utilisateur existant :","If you request a new password for a non-existent username:":"Si vous demandez un nouveau mot de passe pour un nom d’utilisateur inexistant :","Accessing ":"En accédant à "," you can see the number of existing users, in this case is 2 as ":" vous pouvez connaître le nombre d’utilisateurs existants. Dans cet exemple, il est égal à 2, car "," returns a not found error:":" renvoie une erreur 404 :","Fuzz ":"Effectuer un fuzzing sur "," where ":" où "," is a number":" correspond à un nombre"," (from 1 to 500 for example).":" (par exemple, de 1 à 500).","\nYou could find ":"\nCela peut permettre de découvrir des ","hidden pages":"pages cachées"," (test, dev) which are not referenced by the search engines.":" (test, dev) qui ne sont pas référencées par les moteurs de recherche.","In older versions of Drupal ":"Dans les anciennes versions de Drupal ","(before version 8)":"(antérieures à la version 8)",", it was possible to log in as an admin and ":", il était possible de se connecter avec un compte administrateur et d’","enable the ":"activer le module ",", which \"Allows embedded PHP code/snippets to be evaluated.\"":", qui permet d’exécuter du code ou des extraits PHP intégrés.","You need the ":"Le module ","plugin php to be installed":"PHP doit être installé"," (check it accessing to ":" (vérifiez sa présence en accédant à "," and if it returns a ":" ; s’il renvoie un code "," then, ":", cela signifie qu’il ","exists":"existe",", if ":" ; si ","not found":"n’est pas trouvé",", then the ":", alors le ","plugin php isn't installed":"module PHP n’est pas installé","Go to ":"Aller dans "," -> (":" → (","Check":"Cocher",") ":") "," -> ":" → ","Save configuration":"Enregistrer la configuration","Then click on ":"Cliquez ensuite sur ","Add content":"Ajouter du contenu"," -> Select ":" → sélectionnez ","Basic Page":"Page de base","Article -":"Article –","> Write ":" → saisissez ","php shellcode on the body":"le shellcode PHP dans le contenu"," in ":" dans ","Text format":"Format de texte","Preview":"Aperçu","Finally just access the newly created node:":"Accédez enfin au nœud créé :","From version ":"À partir de la version ","8 onwards, the":"8, le","module is not installed by default":"module n’est pas installé par défaut",". To leverage this functionality, we would have to ":". Pour utiliser cette fonctionnalité, il faut ","install the module ourselves":"installer le module manuellement","Download the most recent version of the module from the Drupal website.\n":"Télécharger la version la plus récente du module depuis le site officiel de Drupal.\n","Once downloaded go to ":"Une fois le fichier téléchargé, aller dans ","Click on ":"Cliquer sur "," select the file from the directory we downloaded it to, and then click ":" sélectionner le fichier dans le répertoire de téléchargement, puis cliquer sur ","Once the module is installed, we can click on ":"Une fois le module installé, cliquer sur ","create a new basic page":"créer une nouvelle page de base",", similar to how we did in the Drupal 7 example. Again, be sure to ":", comme dans l’exemple avec Drupal 7. Veillez également à ","select ":"sélectionner "," from the ":" dans le menu "," dropdown":" déroulant","A backdoored module can be created by ":"Un module peut être modifié pour intégrer une backdoor en ","adding a shell to an existing module":"ajoutant un shell à un module existant",". Modules can be found on the drupal.org website. Let's pick a module such as ":". Les modules sont disponibles sur drupal.org. Prenons l’exemple d’un module comme ",". Scroll down and copy the link for the tar.gz ":". Faites défiler la page et copiez le lien de l’archive tar.gz ","Download the archive and extract its contents.":"Télécharger l’archive et en extraire le contenu.","Create a ":"Créer un "," with the contents:":" contenant :","Next, we need to create a ":"Ensuite, créer un fichier "," file to give ourselves access to the folder. This is necessary as Drupal denies direct access to the ":" pour accéder au répertoire. Cette étape est nécessaire, car Drupal bloque l’accès direct au répertoire "," folder.":".","The configuration above will apply rules for the / folder when we request a file in /modules. Copy both of these files to the captcha folder and create an archive.":"La configuration ci-dessus applique les règles au répertoire / lorsqu’un fichier est demandé dans /modules. Copiez ces deux fichiers dans le répertoire captcha, puis créez une archive.","Assuming we have ":"Si nous disposons d’un ","administrative access":"accès administrateur"," to the website, click on ":" au site, ouvrir "," and then ":" puis "," on the sidebar. Next, click on the ":" dans le menu latéral. Cliquer ensuite sur le bouton "," button, and we will be taken to the install page, such as ":" pour accéder à la page d’installation, par exemple "," Browse to the backdoored Captcha archive and click ":" Sélectionner l’archive CAPTCHA modifiée, puis cliquer sur ","Once the installation succeeds, browse to ":"Une fois l’installation terminée, accéder à "," to execute commands.":" pour exécuter des commandes.","In late March 2018, a critical vulnerability was uncovered in Drupal CMS. ":"Fin mars 2018, une vulnérabilité critique a été découverte dans le CMS Drupal. "," versions were affected by this vulnerability.":" étaient concernées par cette vulnérabilité.","It allows remote attackers to execute arbitrary code because of an issue affecting multiple subsystems with default or standard module configurations.":"Elle permet à un attaquant distant d’exécuter du code arbitraire en raison d’un problème touchant plusieurs sous-systèmes dans leur configuration par défaut ou standard.","A lot of PoC is available to exploit this vulnerability.":"De nombreuses PoC sont disponibles pour exploiter cette vulnérabilité.","Drupal before 7.58, 8.x before 8.3.9, 8.4.x before 8.4.6, and 8.5.x before 8.5.1":"Les versions de Drupal antérieures à 7.58, 8.x antérieures à 8.3.9, 8.4.x antérieures à 8.4.6 et 8.5.x antérieures à 8.5.1","Get database if injection Exists · 2":"Extraire la base de données en cas d’injection · 2","Get database if injection Exists · 3":"Extraire la base de données en cas d’injection · 3","Inject into Portable Executables":"Injection dans des exécutables portables","Manual SHELL TO METERPRETER":"Conversion manuelle d’un shell en Meterpreter","Meterpreter on Target1":"Meterpreter sur la cible 1","PASS THE HASH - PSExec":"Pass the Hash avec PsExec","Run a Meterpreter Command on the session given with `-i`":"Exécuter une commande Meterpreter sur la session indiquée avec `-i`","Some shell enumeration":"Quelques commandes d’énumération du shell","The ":"Le ","Upload the payload on the target and try it with MSFconsole":"Transférer le payload sur la cible, puis le tester avec MSFconsole","Use more encoding iterations":"Augmenter le nombre d’itérations d’encodage","WMAP in msfconsole":"WMAP dans msfconsole","for example:":"par exemple :","⬇ Feel free to download the version of your choice and kindly mention my blog when utilizing it":"Téléchargez la version de votre choix et pensez à mentionner mon blog lorsque vous l’utilisez.","message":"message","different":"selon que le"}''')
EJPT_ENGLISH_KEEP = {"Pass the Hash"}
EJPT_ENGLISH_MARKERS = re.compile(
    r"\b(?:the|and|you|your|we|our|if|when|where|which|that|this|these|those|are|is|was|were|can|could|will|would|should|from|with|for|by|on|in|to|of|as|such|there|it|they|their|not|then|also|only|after|before|during|over|under|into|about|be|has|have|had|do|does|did|than|more|most|any|all|some|one|two|three)\b",
    re.I,
)
def translate_ejpt_cheatsheet(article):
    before = [c.get_text() for c in article.select("pre code")]
    inline_before = [c.get_text() for c in article.select("code, kbd")]
    links_before = [a.get("href") for a in article.find_all("a", href=True)]
    translated = 0
    translated_keys = set()
    preserved_technical = 0
    remaining = set()
    reviewed = 0
    for node in list(article.find_all(string=True)):
        if node.find_parent(["pre", "code", "kbd", "script", "style"]):
            continue
        value = str(node)
        if not value.strip():
            continue
        reviewed += 1
        if value in EJPT_TEXT_TRANSLATIONS:
            replacement = EJPT_TEXT_TRANSLATIONS[value]
            # Resolve short ambiguous text fragments from their inline context.
            following = node.next_sibling
            inline = following.get_text(strip=True) if getattr(following, "name", None) else ""
            if value == "The " and inline == "wp-content":
                replacement = "Le répertoire "
            elif value == "The " and inline == "wp-config.php":
                replacement = "Le fichier "
            elif value == "In " and inline == "/user/register":
                replacement = "Sur "
            elif value == "When login in ":
                replacement = "Lors de la connexion à "
            elif value == " the " and node.parent.get_text(" ", strip=True).startswith(("When login", "Lors de la connexion")):
                replacement = ", le "
            node.replace_with(replacement)
            translated += 1
            translated_keys.add(value)
        elif value in EJPT_ENGLISH_KEEP:
            preserved_technical += 1
        elif EJPT_ENGLISH_MARKERS.search(value):
            remaining.add(value)
    after = [c.get_text() for c in article.select("pre code")]
    if before != after:
        raise RuntimeError("eJPT translation modified an original command block")
    assert inline_before == [c.get_text() for c in article.select("code, kbd")], "Translation changed inline code"
    assert links_before == [a.get("href") for a in article.find_all("a", href=True)], "Translation changed a source link"
    total = len(translated_keys) + len(remaining)
    progress = 100 if total == 0 else round(100 * len(translated_keys) / total)
    result = {
        "reviewed_nodes": reviewed,
        "translated_nodes": translated,
        "translated_unique_fragments": len(translated_keys),
        "preserved_technical_nodes": preserved_technical,
        "translation_dictionary_size": len(EJPT_TEXT_TRANSLATIONS),
        "untranslated_prose": len(remaining),
        "progress_percent": progress,
        "untranslated_samples": sorted(remaining),
        "commands_preserved": True,
    }
    print("eJPT French translation:", json.dumps(result, ensure_ascii=False))
    return result


def simplify_generated_descriptions(article):
    """Hide repetitive editorial text, never original notes, commands or headings."""
    before = [c.get_text() for c in article.select("pre code")]
    images = [i.get("src") for i in article.find_all("img")]
    links = [a.get("href") for a in article.find_all("a", href=True)]
    seen = set()
    section = ""
    hidden = 0
    boilerplate = {
        "Notes complémentaires issues de la seconde fiche, regroupées avec les références originales.",
        "Notes de découverte issues du complément de révision.",
        "Exemple original du cours. À replacer dans le contexte du laboratoire autorisé.",
        "Extrait original de cette sous-partie, conservé dans son ordre initial.",
    }
    # Keep generated metadata for the existing structural audit. Hide only
    # generated descriptions, and keep the first useful occurrence per chapter.
    for node in article.find_all(["h2", "h3", "p"]):
        if node.name == "h2":
            section = node.get("id") or node.get_text(" ", strip=True)
            continue
        if node.name != "p" or node.find(["a", "img", "code", "kbd"]):
            continue
        classes = set(node.get("class", []))
        if not (node.get("data-ejpt-note-description") == "true" or
                classes.intersection({"ejpt-action-description", "ejpt-section-description"})):
            continue
        value = " ".join(node.get_text(" ", strip=True).split())
        key = (section, value)
        if value in boilerplate or key in seen:
            node["hidden"] = ""
            node["style"] = (node.get("style", "").rstrip(";") + ";display:none!important").lstrip(";")
            node["data-ejpt-repetitive-description"] = "true"
            hidden += 1
        else:
            seen.add(key)
    assert before == [c.get_text() for c in article.select("pre code")]
    assert images == [i.get("src") for i in article.find_all("img")]
    assert links == [a.get("href") for a in article.find_all("a", href=True)]
    assert not any(" ".join(p.get_text(" ", strip=True).split()) in boilerplate
                   for p in article.select("p.ejpt-action-description:not([hidden]), p.ejpt-section-description:not([hidden])"))
    print("eJPT editorial cleanup:", hidden, "repetitive generated descriptions hidden; original content intact")
    return {"hidden_descriptions": hidden, "commands_preserved": True}


def merge_common_chapters(soup, article):
    """Move existing complementary sections into the matching main chapters."""
    from collections import Counter
    code_before = Counter(c.get_text() for c in article.select("pre code"))
    images_before = Counter(str(i) for i in article.find_all("img"))
    links_before = Counter(a.get("href") for a in article.find_all("a", href=True))
    ids_before = Counter(n["id"] for n in article.select("[id]"))
    root = article.find("h2", id="complements-de-revision")
    if root is None:
        raise RuntimeError("Missing complementary chapter")
    main = {h["data-ejpt-source-chapter"]: h for h in article.select('[data-ejpt-source-role="primary"]')}
    roots = list(article.select('[data-ejpt-source-role="supplement"]'))
    if len(roots) != len(sheet_labels) or set(main) != set(sheet_labels):
        raise RuntimeError("Source chapter markers incomplete")
    moved = []
    anchors = []
    for h in roots:
        key = h["data-ejpt-source-chapter"]
        dest = main[key]
        anchors.append(h["id"])
        nodes = [h]
        for n in h.next_siblings:
            tag = getattr(n, "name", None)
            if tag == "h2" or (tag and n.get("data-ejpt-source-boundary") == "true"):
                break
            nodes.append(n)
        # Keep the original fragment ID without creating a repeated accordion.
        h.name = "span"
        h["class"] = h.get("class", []) + ["ejpt-merged-chapter-anchor"]
        h.clear()
        h["aria-hidden"] = "true"
        h["style"] = "display:block;height:0;scroll-margin-top:100px"
        # Promote genuine nested headings by one level so they remain within
        # the corresponding chapter. Keep platform headings and code unchanged.
        for n in nodes[1:]:
            tag = getattr(n, "name", None)
            if tag and re.fullmatch(r"h[4-6]", tag):
                n.name = "h" + str(int(tag[1]) - 1)
        # Place the existing content at the end of the matching main chapter.
        stop = dest.find_next_sibling("h2")
        if stop is None:
            raise RuntimeError("Missing main chapter boundary")
        for n in nodes:
            stop.insert_before(n.extract())
        moved.append(sheet_labels[key])
    assert len(moved) == len(sheet_labels)
    assert code_before == Counter(c.get_text() for c in article.select("pre code"))
    assert images_before == Counter(str(i) for i in article.find_all("img"))
    assert links_before == Counter(a.get("href") for a in article.find_all("a", href=True))
    assert ids_before == Counter(n["id"] for n in article.select("[id]"))
    assert all(article.find(id=ident).name == "span" for ident in anchors)
    print("eJPT chapter merge:", len(moved), "common chapters merged; all blocks, images, links and IDs preserved")
    return {"merged":len(moved), "chapters":moved, "content_preserved":True}


def clean_generated_titles(article):
    """Remove generated numbering and repeated consecutive leaf labels."""
    before = [c.get_text() for c in article.select("pre code")]
    ids = [n["id"] for n in article.select("[id]")]
    links = [a.get("href") for a in article.find_all("a", href=True)]
    renamed = 0
    hidden = 0
    previous = None
    for node in article.find_all(re.compile(r"^(?:h[1-6]|p)$")):
        classes = set(node.get("class", []))
        generated = bool(classes.intersection({
            "ejpt-existing-note-heading", "ejpt-context-heading",
            "ejpt-reviewed-enum-title", "ejpt-leaf-title",
            "ejpt-long-block-title",
        }))
        if not generated:
            if node.name.startswith("h"):
                previous = None
            continue
        if node.find(["a", "img", "code", "kbd"]):
            previous = None
            continue
        old = node.get_text(" ", strip=True)
        if not old:
            continue
        new = re.sub(r"\s+(?:·\s*\d+|—\s*complément\s+\d+)$", "", old)
        if new != old:
            # Keep the existing element, ID, and emphasis styling.
            target = node.find("strong") or node
            if len(list(target.children)) == 1 and target.string is not None:
                target.string.replace_with(new)
                renamed += 1
        key = " ".join(new.casefold().split())
        if node.name == "p" and key == previous:
            node["hidden"] = ""
            node["style"] = (node.get("style", "").rstrip(";") + ";display:none!important").lstrip(";")
            node["data-ejpt-repetitive-title"] = "true"
            hidden += 1
        previous = key
    assert before == [c.get_text() for c in article.select("pre code")]
    assert ids == [n["id"] for n in article.select("[id]")]
    assert links == [a.get("href") for a in article.find_all("a", href=True)]
    print("eJPT title cleanup:", renamed, "numbered labels simplified;", hidden, "consecutive duplicates hidden")
    return {"renamed":renamed, "hidden":hidden, "content_preserved":True}


def merge_matching_subsections(soup, article):
    """Combine exact matching original subsection headings within each chapter."""
    from collections import Counter, defaultdict
    code_before = Counter(c.get_text() for c in article.select("pre code"))
    images_before = Counter(str(i) for i in article.find_all("img"))
    links_before = Counter(a.get("href") for a in article.find_all("a", href=True))
    ids_before = Counter(n["id"] for n in article.select("[id]"))
    groups = defaultdict(lambda: {"primary": [], "supplement": []})
    for heading in article.select("[data-ejpt-source-subsection]"):
        key = (heading["data-ejpt-subsection-chapter"],
               heading["data-ejpt-source-subsection"])
        groups[key][heading["data-ejpt-subsection-role"]].append(heading)
    def boundary(node):
        return bool(getattr(node, "name", None) and
                    (node.name == "h2" or
                     node.get("data-ejpt-source-chapter") or
                     node.get("data-ejpt-source-boundary") or
                     node.get("data-ejpt-source-subsection")))
    def chapter_for(node):
        return next((h for h in node.previous_siblings
                     if getattr(h, "name", None) == "h2"), None)
    merged = []
    skipped = 0
    for (chapter, label), pair in groups.items():
        if not pair["primary"] or not pair["supplement"]:
            continue
        if len(pair["primary"]) != 1 or len(pair["supplement"]) != 1:
            skipped += 1
            continue
        target, source = pair["primary"][0], pair["supplement"][0]
        if (target.name != "h3" or source.name != "h3" or
            target.parent is not article or source.parent is not article or
            chapter_for(target) is not chapter_for(source) or
            source.find(["a", "img", "code", "kbd"])):
            skipped += 1
            continue
        source_nodes = [source]
        for n in source.next_siblings:
            if boundary(n):
                break
            source_nodes.append(n)
        if not any(getattr(n, "name", None) for n in source_nodes[1:]):
            skipped += 1
            continue
        stop = next((n for n in target.next_siblings if boundary(n)), None)
        if stop is None or any(stop is n for n in source_nodes):
            skipped += 1
            continue
        # The duplicate title becomes an anchor; the original body is moved intact.
        source["data-ejpt-original-label"] = source.get_text(" ", strip=True)
        source.name = "span"
        source.clear()
        source["class"] = source.get("class", []) + ["ejpt-merged-subsection-anchor"]
        source["aria-hidden"] = "true"
        source["style"] = "display:block;height:0;scroll-margin-top:100px"
        for n in source_nodes:
            stop.insert_before(n.extract())
        merged.append([chapter, label])
    assert code_before == Counter(c.get_text() for c in article.select("pre code"))
    assert images_before == Counter(str(i) for i in article.find_all("img"))
    assert links_before == Counter(a.get("href") for a in article.find_all("a", href=True))
    assert ids_before == Counter(n["id"] for n in article.select("[id]"))
    print("eJPT subsection merge:", len(merged), "exact matching subsections merged;", skipped,
          "ambiguous or incompatible matches kept intact")
    return {"merged":len(merged), "skipped":skipped, "subsections":merged, "content_preserved":True}


def remove_em_dashes(article):
    """Use natural punctuation in displayed prose, leaving technical literals intact."""
    from bs4 import Comment
    code_before = [c.get_text() for c in article.select("pre, code, kbd, samp")]
    links_before = [a["href"] for a in article.find_all("a", href=True)]
    images_before = [str(img) for img in article.find_all("img")]
    ids_before = [n["id"] for n in article.select("[id]")]
    def prose(node):
        return not isinstance(node, Comment) and not node.find_parent(
            ["pre", "code", "kbd", "samp", "script", "style", "textarea"])
    count = 0
    for node in list(article.find_all(string=True)):
        if not prose(node) or "\u2014" not in str(node):
            continue
        value = str(node)
        count += value.count("\u2014")
        title = node.find_parent(re.compile(r"^h[1-6]$")) or node.find_parent(
            class_=re.compile(r"ejpt-(?:leaf-title|long-block-title|context-heading|reviewed-enum-title)"))
        separator = " : " if title else ", "
        replacement = re.sub(r"[ \t]*\u2014[ \t]*", separator, value)
        replacement = re.sub(r"^[:,][ \t]+", "", replacement)
        node.replace_with(replacement)
    assert not any("\u2014" in str(n) for n in article.find_all(string=True) if prose(n))
    assert code_before == [c.get_text() for c in article.select("pre, code, kbd, samp")]
    assert links_before == [a["href"] for a in article.find_all("a", href=True)]
    assert images_before == [str(img) for img in article.find_all("img")]
    assert ids_before == [n["id"] for n in article.select("[id]")]
    print("eJPT punctuation:", count, "em dashes removed from prose; technical content unchanged")
    return {"removed":count, "remaining_in_prose":0, "content_preserved":True}


# First course module: translate the navigation labels from the original headings.
# Do not alter technical examples, links, images, or the source lesson text.
PREREQUISITE_HEADINGS = {
    "Topics": "Thèmes abordés",
    "Sections": "Chapitres",
    "The Information Security Field": "La sécurité informatique",
    "InfoSec Culture": "Culture InfoSec",
    "Career Opportunities": "Débouchés professionnels",
    "Information Security Terms": "Terminologie de la sécurité informatique",
    "Cryptography Protocols & VPNs": "Protocoles cryptographiques et VPN",
    "Clear-text Protocols": "Protocoles en clair",
    "Cryptographic Protocols": "Protocoles cryptographiques",
    "Virtual Private Networks (VPN)": "Réseaux privés virtuels (VPN)",
    "Binary Arithmetic Basics": "Bases de l’arithmétique binaire",
    "Binary and Decimal Bases": "Bases binaire et décimale",
    "Bitwise operations": "Opérations bit à bit",
    "Hexadecimal arithmetic": "Arithmétique hexadécimale",
    "Protocols": "Protocoles",
    "Packets": "Paquets",
    "Protocol Layers": "Couches protocolaires",
    "Routing": "Routage",
    "Routing table": "Table de routage",
    "IP/Mask": "Adresse IP et masque",
    "Link Layer Devices & Protocols": "Équipements et protocoles de la couche liaison",
    "MAC Addresses": "Adresses MAC",
    "IP and MAC Address usage": "Utilisation des adresses IP et MAC",
    "Hubs": "Hubs",
    "Switches": "Switches",
    "CAM / Forwarding Table": "Table CAM",
    "TCP & UDP": "TCP et UDP",
    "TCP 3-Way Handshake": "TCP 3-Way Handshake",
    "Firewall & Defense": "Pare-feu et défense",
    "Packet Filtering Firewalls": "Pare-feu à filtrage de paquets",
    "Application Layer Firewalls": "Pare-feu applicatifs",
    "Spot an obstacle": "Identifier un obstacle réseau",
    "NAT and IP Masquerading": "NAT et IP Masquerading",
    "DNS Structure/Hierarchy": "Structure et hiérarchie DNS",
    "DNS Names Resolution": "Résolution des noms DNS",
    "Reverse DNS Resolution": "Résolution DNS inverse",
    "Capturing": "Capture",
    "Filtering": "Filtrage",
    "HTTP Protocol Basics": "Fondamentaux du protocole HTTP",
    "HTTP Requests": "Requêtes HTTP",
    "HTTP Responses": "Réponses HTTP",
    "HTTPS Protocol Basics": "Fondamentaux du protocole HTTPS",
    "Command Line / GUI Tools": "Outils en ligne de commande et interface graphique",
    "HTTP Cookies": "Cookies HTTP",
    "Cookies Format": "Format des cookies",
    "Cookies Domain & Path": "Domaine et chemin des cookies",
    "Other Attributes": "Autres attributs",
    "Session Cookies": "Cookies de session",
    "Burp Suite Tool": "Burp Suite",
    "Burp Suite - Tools": "Outils de Burp Suite",
}
PREREQUISITE_INTRO = {
    "These notes are from the first version of the PTS1 Learning Path on INE.": "Ces notes proviennent de la première version du parcours PTS1 sur INE.",
    "Information Security": "Sécurité informatique",
    "Foundational and technical skills on:": "Fondamentaux et compétences techniques :",
    "Computer networks": "Réseaux informatiques",
    "Protocols": "Protocoles",
    "Web applications": "Applications Web",
    "Theoretical + Hands on sessions (Labs)": "Théorie et sessions pratiques (Labs)",
    "Introduction": "Introduction",
    "Networking": "Réseaux",
    "Web Applications": "Applications Web",
}
def format_prerequisite_headings(article, page):
    before = [c.get_text() for c in article.select("pre, code, kbd, samp")]
    links = [a["href"] for a in article.find_all("a", href=True)]
    images = [str(i) for i in article.find_all("img")]
    ids = [n["id"] for n in article.select("[id]")]
    renamed = 0
    for heading in article.find_all(re.compile(r"^h[2-6]$")):
        old = heading.get_text(" ", strip=True)
        if old in PREREQUISITE_HEADINGS and heading.string is not None and not heading.find(["a","code","img","kbd"]):
            new = PREREQUISITE_HEADINGS[old]
            if new != old:
                heading.string.replace_with(new)
                renamed += 1
    overview = 0
    if page.endswith("/README.html"):
        for node in list(article.find_all(string=True)):
            if node.find_parent(["pre","code","kbd","samp","script","style"]):
                continue
            value = str(node)
            old = value.strip()
            if old in PREREQUISITE_INTRO and old != PREREQUISITE_INTRO[old]:
                node.replace_with(value.replace(old, PREREQUISITE_INTRO[old], 1))
                overview += 1
    assert before == [c.get_text() for c in article.select("pre, code, kbd, samp")]
    assert links == [a["href"] for a in article.find_all("a", href=True)]
    assert images == [str(i) for i in article.find_all("img")]
    assert ids == [n["id"] for n in article.select("[id]")]
    print("eJPT prerequisite navigation:", page, renamed, "headings;", overview, "overview fragments")
    return {"headings_renamed":renamed, "overview_fragments":overview, "content_preserved":True}


ASSESSMENT_HEADINGS = {
    "Topics": "Thèmes abordés",
    "Disclaimer": "Avertissement",
    "Passive Information Gathering Introduction": "Introduction à la collecte passive",
    "What passive information?": "Informations collectées passivement",
    "Active Information Gathering Introduction": "Introduction à la collecte active",
    "What active information?": "Informations collectées activement",
    "Code of conduct": "Code de conduite",
    "Passive Information Gathering": "Collecte passive d’informations",
    "Active Information Gathering": "Collecte active d’informations",
    "Website Reconnaissance & Footprinting": "Reconnaissance Web et footprinting",
    "Whois Enumeration": "Énumération WHOIS",
    "Website Footprinting with Netcraft": "Footprinting Web avec Netcraft",
    "DNS Reconnaissance": "Reconnaissance DNS",
    "Mapping a Network": "Cartographie réseau",
    "Purpose": "Objectif",
    "Process": "Processus",
    "Tools": "Outils",
    "Operating System": "Système d’exploitation",
    "Services": "Services",
    "Port Scanning": "Scan de ports",
    "Vulnerabilities": "Vulnérabilités",
    "Case Studies": "Études de cas",
    "Vulnerable Lab": "Laboratoire vulnérable",
    "Cybersecurity Basics": "Fondamentaux de la cybersécurité",
    "CIA Triad": "Triade CIA",
    "Defense in Depth": "Défense en profondeur",
    "Compliance": "Conformité",
    "Frameworks and Maturity": "Référentiels et maturité",
    "Auditing": "Audit",
    "Asset Management": "Gestion des actifs",
}
ASSESSMENT_OVERVIEW = {
    "Information Gathering": "Collecte d’informations",
    "Footprinting & Scanning": "Footprinting et scanning",
    "Enumeration": "Énumération",
    "Vulnerability Assessment": "Évaluation des vulnérabilités",
    "Auditing Fundamentals": "Fondamentaux de l’audit",
    "Never use tools and techniques on real IP addresses, hosts or networks without proper authorization!": "Ne jamais utiliser ces outils et techniques sur des adresses IP, des hôtes ou des réseaux réels sans autorisation préalable !",
}
def format_assessment_navigation(article, page):
    before = [c.get_text() for c in article.select("pre, code, kbd, samp")]
    links = [a["href"] for a in article.find_all("a", href=True)]
    images = [str(i) for i in article.find_all("img")]
    ids = [n["id"] for n in article.select("[id]")]
    renamed = 0
    overview = 0
    for heading in article.find_all(re.compile(r"^h[2-6]$")):
        old = heading.get_text(" ", strip=True)
        if old in ASSESSMENT_HEADINGS and heading.string is not None and not heading.find(["a","code","img","kbd"]):
            new = ASSESSMENT_HEADINGS[old]
            if new != old:
                heading.string.replace_with(new)
                renamed += 1
    if page.endswith("/README.html"):
        for node in list(article.find_all(string=True)):
            if node.find_parent(["pre","code","kbd","samp","script","style"]):
                continue
            value = str(node)
            old = value.strip()
            if old in ASSESSMENT_OVERVIEW and old != ASSESSMENT_OVERVIEW[old]:
                node.replace_with(value.replace(old, ASSESSMENT_OVERVIEW[old], 1))
                overview += 1
    assert before == [c.get_text() for c in article.select("pre, code, kbd, samp")]
    assert links == [a["href"] for a in article.find_all("a", href=True)]
    assert images == [str(i) for i in article.find_all("img")]
    assert ids == [n["id"] for n in article.select("[id]")]
    print("eJPT assessment navigation:", page, renamed, "headings;", overview, "overview fragments")
    return {"headings_renamed":renamed, "overview_fragments":overview, "content_preserved":True}


# Editorial navigation only, without modifying technical lessons.
HOST_NETWORK_OVERVIEW_PAGES = {
    "README.html", "1-system-attack.html",
    "1-system-attack/linux-attacks.html", "1-system-attack/windows-attacks.html",
    "2-network-attack.html", "3-metasploit.html", "4-exploitation.html",
    "5-post-exploit.html", "6-social-engineer.html",
}
HOST_NETWORK_GENERAL_HEADINGS = {
    "Topics": "Thèmes abordés",
    "Disclaimer": "Avertissement",
    "Linux Vulnerabilities": "Vulnérabilités Linux",
    "Windows Vulnerabilities": "Vulnérabilités Windows",
    "Vulns Types": "Types de vulnérabilités",
    "Tools": "Outils",
    "MSF Introduction": "Introduction à Metasploit",
    "Terminology": "Terminologie",
    "Interfaces": "Interfaces",
    "Metasploit Fundamentals": "Fondamentaux de Metasploit",
    "Module Variables": "Variables des modules",
    "Case Studies": "Études de cas",
    "Penetration Testing": "Tests d’intrusion",
    "Methodology": "Méthodologie",
    "System Information": "Informations système",
    "Users & Groups": "Utilisateurs et groupes",
    "Network information & Services": "Informations réseau et services",
    "File System - Alternate Data Streams": "Système de fichiers : Alternate Data Streams",
}
HOST_NETWORK_OVERVIEW = {
    "System/Host Based Attacks": "Sécurité des systèmes",
    "Network Based Attacks": "Sécurité réseau",
    "The Metasploit Framework (MSF)": "Framework Metasploit (MSF)",
    "Post-Exploitation": "Post-exploitation",
    "Never use tools and techniques on real IP addresses, hosts or networks without proper authorization!": "Ne jamais utiliser ces outils et techniques sur des adresses IP, des hôtes ou des réseaux réels sans autorisation préalable !",
}
def format_host_network_navigation(article, page):
    before = [c.get_text() for c in article.select("pre, code, kbd, samp")]
    links = [a["href"] for a in article.find_all("a", href=True)]
    images = [str(i) for i in article.find_all("img")]
    ids = [n["id"] for n in article.select("[id]")]
    renamed = 0
    overview = 0
    for heading in article.find_all(re.compile(r"^h[2-6]$")):
        old = heading.get_text(" ", strip=True)
        if old in HOST_NETWORK_GENERAL_HEADINGS and heading.string is not None and not heading.find(["a","code","img","kbd"]):
            new = HOST_NETWORK_GENERAL_HEADINGS[old]
            if new != old:
                heading.string.replace_with(new)
                renamed += 1
    if page.endswith("/README.html"):
        for node in list(article.find_all(string=True)):
            if node.find_parent(["pre","code","kbd","samp","script","style"]):
                continue
            value = str(node)
            old = value.strip()
            if old in HOST_NETWORK_OVERVIEW and old != HOST_NETWORK_OVERVIEW[old]:
                node.replace_with(value.replace(old, HOST_NETWORK_OVERVIEW[old], 1))
                overview += 1
    assert before == [c.get_text() for c in article.select("pre, code, kbd, samp")]
    assert links == [a["href"] for a in article.find_all("a", href=True)]
    assert images == [str(i) for i in article.find_all("img")]
    assert ids == [n["id"] for n in article.select("[id]")]
    print("eJPT host-network navigation:", page, renamed, "headings;", overview, "overview fragments")
    return {"headings_renamed":renamed, "overview_fragments":overview, "content_preserved":True}


WEB_LABS_GENERAL_PAGES = {
    "webapp-penetration-testing/README.html",
    "webapp-penetration-testing/1-webapp-http.html",
    "webapp-penetration-testing/1-webapp-http/webapp-scan.html",
    "exam-preparation-labs/README.html",
    "exam-preparation-labs/p.t.-prerequisites-labs/README.html",
    "exam-preparation-labs/p.t.-prerequisites-labs/http-s-traffic-sniffing.html",
    "exam-preparation-labs/pts2-labs.html",
}
WEB_LABS_LABELS = {
    "Topics": "Thèmes abordés",
    "Disclaimer": "Avertissement",
    "Request Methods": "Méthodes HTTP",
    "Response Status Codes": "Codes de statut HTTP",
    "INE - PTSv2 Course": "Parcours PTSv2 sur INE",
}
def format_web_labs_navigation(article, page):
    before = [c.get_text() for c in article.select("pre, code, kbd, samp")]
    links = [a["href"] for a in article.find_all("a", href=True)]
    images = [str(i) for i in article.find_all("img")]
    ids = [n["id"] for n in article.select("[id]")]
    renamed = 0
    overview = 0
    for heading in article.find_all(re.compile(r"^h[2-6]$")):
        old = heading.get_text(" ", strip=True)
        if old in WEB_LABS_LABELS and not heading.find(["code","img","kbd"]):
            strings = [n for n in heading.find_all(string=True) if str(n).strip()]
            if len(strings) == 1 and str(strings[0]).strip() == old:
                strings[0].replace_with(str(strings[0]).replace(old, WEB_LABS_LABELS[old], 1))
                renamed += 1
    if page.endswith("/README.html"):
        translations = {
            "Intro to Web App Pentesting": "Introduction au pentest Web",
            "Never use tools and techniques on real IP addresses, hosts or networks without proper authorization!": "Ne jamais utiliser ces outils et techniques sur des adresses IP, des hôtes ou des réseaux réels sans autorisation préalable !",
        }
        for node in list(article.find_all(string=True)):
            if node.find_parent(["pre","code","kbd","samp","script","style"]):
                continue
            value = str(node)
            old = value.strip()
            if old in translations:
                node.replace_with(value.replace(old, translations[old], 1))
                overview += 1
    assert before == [c.get_text() for c in article.select("pre, code, kbd, samp")]
    assert links == [a["href"] for a in article.find_all("a", href=True)]
    assert images == [str(i) for i in article.find_all("img")]
    assert ids == [n["id"] for n in article.select("[id]")]
    print("eJPT web/labs navigation:", page, renamed, "headings;", overview, "overview fragments")
    return {"headings_renamed":renamed, "overview_fragments":overview, "content_preserved":True}


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
        report["cheatsheet_network_layout"]=refine_network_layout(soup,article)
        report["cheatsheet_framework_layout"]=refine_framework_layout(soup,article)
        report["cheatsheet_later_layout"]=refine_later_chapters(soup,article)
        report["cheatsheet_final_layout"]=refine_final_chapters(soup,article)
        report["cheatsheet_long_block_review"]=refine_long_blocks(soup,article)
        report["cheatsheet_leaf_titles"]=simplify_note_titles(soup,article)
        report["cheatsheet_translation"]=translate_ejpt_cheatsheet(article)
        report["cheatsheet_chapter_merge"]=merge_common_chapters(soup,article)
        report["cheatsheet_subsection_merge"]=merge_matching_subsections(soup,article)
        report["cheatsheet_editorial_cleanup"]=simplify_generated_descriptions(article)
        report["cheatsheet_title_cleanup"]=clean_generated_titles(article)
        report["cheatsheet_punctuation"]=remove_em_dashes(article)
        report["cheatsheet_block_sizes"]=audit_cheatsheet_block_sizes(article)
        report["cheatsheet_display_blocks"]=len(article.select("pre code"))
    elif page.startswith("penetration-testing-prerequisites/"):
        report.setdefault("prerequisite_navigation", {})[page] = format_prerequisite_headings(article, page)
    elif page.startswith("assessment-methodologies/"):
        report.setdefault("assessment_navigation", {})[page] = format_assessment_navigation(article, page)
    elif page.startswith("hostnetwork-penetration-testing/") and page.split("/", 1)[1] in HOST_NETWORK_OVERVIEW_PAGES:
        report.setdefault("host_network_navigation", {})[page] = format_host_network_navigation(article, page)
    elif page in WEB_LABS_GENERAL_PAGES:
        report.setdefault("web_labs_navigation", {})[page] = format_web_labs_navigation(article, page)
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

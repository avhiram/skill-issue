#!/usr/bin/env python3
"""Import OSCP commands from Emmanuel Solis into the SKILL-ISSUE VitePress structure.

This creates a French navigation and preserves every source <pre> block plus
every <code> element outside a <pre>. Original explanatory prose is not copied.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

SOURCE = "https://www.emmanuelsolis.com/oscp.html"
ROOT = Path("docs/src")
OUT = ROOT / "oscp"

TOPICS = {
    1: ("reconnaissance", "Reconnaissance", "Identifier les hôtes, les ports et les services accessibles."),
    2: ("vulnerabilites", "Analyse de vulnérabilités", "Évaluer les services exposés et rechercher des faiblesses connues."),
    3: ("applications-web", "Applications web", "Examiner les fonctionnalités, entrées et configurations des applications web."),
    4: ("attaques-client", "Attaques côté client", "Comprendre les vecteurs d'interaction avec les postes utilisateurs."),
    5: ("antivirus-metasploit", "Antivirus et Metasploit", "Références sur les protections, charges utiles et outils de laboratoire."),
    6: ("mots-de-passe", "Mots de passe et authentification", "Analyser les mécanismes d'authentification et les formats de hachage."),
    7: ("privileges-windows", "Élévation de privilèges Windows", "Auditer les services, jetons et configurations d'un poste Windows."),
    8: ("privileges-linux", "Élévation de privilèges Linux", "Examiner les permissions, processus et configurations d'un système Linux."),
    9: ("redirection-ports", "Redirection de ports", "Documenter les redirections locales, distantes et dynamiques."),
    10: ("tunneling", "Tunneling", "Référence des outils de tunnel et des modes de transport réseau."),
    11: ("ad-theorie", "Active Directory : fondamentaux", "Comprendre les objets, protocoles et mécanismes d'un domaine."),
    12: ("ad-enumeration", "Active Directory : énumération", "Identifier les utilisateurs, groupes, services et relations du domaine."),
    13: ("ad-techniques", "Active Directory : techniques", "Étudier les mécanismes d'authentification et les techniques AD."),
    14: ("ad-lateral", "Active Directory : mouvement latéral", "Référence des accès distants et protocoles entre hôtes Windows."),
    15: ("cloud", "Infrastructures cloud", "Repères sur l'évaluation des environnements cloud."),
    16: ("rapport", "Rapports de pentest", "Documenter les constats et les preuves techniques."),
    17: ("transferts", "Transfert de fichiers", "Envoyer, récupérer et encoder des fichiers dans un laboratoire."),
    18: ("utilitaires", "Utilitaires", "Commandes courantes et outils complémentaires."),
    19: ("methodologie", "Méthodologie OSCP", "Organiser les vérifications et la collecte des résultats."),
    20: ("references", "Références", "Bibliographie et outils cités dans la source.")
}
TRANSLATIONS = {
    "Information Gathering": "Reconnaissance",
    "Passive Information Gathering": "Collecte passive d'informations",
    "DNS Enumeration": "Énumération DNS",
    "Port Scanning": "Scan de ports",
    "Specific Port Services": "Services par port",
    "Vulnerability Scanning": "Analyse de vulnérabilités",
    "Web Applications": "Applications web",
    "Client-Side Attacks": "Attaques côté client",
    "Antivirus Evasion & Metasploit": "Antivirus et Metasploit",
    "Password Attacks": "Attaques sur les mots de passe",
    "Windows Privilege Escalation": "Élévation de privilèges Windows",
    "Linux Privilege Escalation": "Élévation de privilèges Linux",
    "Port Redirection and Manual Tunneling": "Redirection de ports et tunneling manuel",
    "Tunneling Through Tools": "Tunnels avec des outils",
    "Active Directory Theory": "Fondamentaux Active Directory",
    "Active Directory Enumeration": "Énumération Active Directory",
    "Active Directory Attacking": "Techniques Active Directory",
    "Active Directory Lateral Movement": "Mouvement latéral Active Directory",
    "Cloud Infrastructures": "Infrastructures cloud",
    "Reports Writing": "Rédaction de rapports",
    "File Transfers": "Transfert de fichiers",
    "Utilities": "Utilitaires",
    "Methodology": "Méthodologie",
    "References": "Références",
    "Enumeration": "Énumération",
    "Scanning": "Analyse",
    "Nmap Scripting Scan": "Scripts Nmap",
    "Nmap Scripting Engine (NSE)": "Scripts Nmap (NSE)",
    "Personal Methodology": "Méthode personnelle",
    "Scan Types": "Types de scan",
    "Detection and Scanning": "Détection et scan",
    "Saving Results": "Enregistrement des résultats",
    "Basic Enumeration": "Énumération de base",
    "Network Sweeping": "Découverte réseau",
    "User Enumeration": "Énumération des utilisateurs",
    "Groups Enumeration": "Énumération des groupes",
    "Initial Connection": "Connexion initiale",
    "Common Queries": "Requêtes courantes",
    "Commands Execution": "Exécution de commandes",
    "Command Execution": "Exécution de commandes",
    "Useful Tools": "Outils utiles",
    "Scripts": "Scripts",
    "Common Commands": "Commandes courantes",
    "Basic Commands": "Commandes de base",
    "Finding Files in Directories": "Recherche de fichiers",
    "Privilege Escalation": "Élévation de privilèges",
    "Password Files": "Fichiers de mots de passe",
    "Password Policy": "Politique de mots de passe",
    "Scheduled Tasks": "Tâches planifiées",
    "Cron Jobs": "Tâches cron",
    "File Upload Vulnerabilities": "Vulnérabilités de téléversement",
    "Local File Inclusion (LFI)": "Inclusion de fichiers locaux (LFI)",
    "Remote File Inclusion (RFI)": "Inclusion de fichiers distants (RFI)",
    "SQL Attacks": "Attaques SQL",
    "SQL Injection": "Injection SQL",
    "XXE (XML External Entity) Injection": "Injection XXE",
    "Command Injections": "Injections de commandes",
    "Web Services": "Services web",
    "Wordlists": "Listes de mots",
    "Port Forwarding": "Redirection de ports",
    "Reverse Port Forwarding": "Redirection inversée de ports",
    "Source Code": "Code source",
    "Additional Commands": "Commandes complémentaires",
    "Additional Notes": "Notes complémentaires",
    "Normal Tunneling": "Tunnel simple",
    "Double Tunneling": "Double tunnel",
    "Techniques and Preparation": "Techniques et préparation",
    "Domain Shares Enumeration": "Énumération des partages du domaine",
    "Object Permissions Enumeration": "Énumération des permissions d'objets",
    "General Enumeration": "Énumération générale",
    "Linux Targets": "Cibles Linux",
    "Windows Targets": "Cibles Windows",
    "Scanning for LFI": "Détection de LFI",
    "Common Linux Files": "Fichiers Linux courants",
    "Common Windows Files": "Fichiers Windows courants",
    "Checking for Vulnerability": "Vérification de la vulnérabilité",
    "User Inputs": "Entrées utilisateur",
    "Network Enumeration": "Énumération réseau",
    "Service Discovery": "Identification des services",
    "Initial Scanning": "Scan initial",
    "General Methodology": "Méthodologie générale",
    "FTP": "FTP",
    "SSH": "SSH",
    "SMB": "SMB",
    "LDAP": "LDAP",
    "Kerberos": "Kerberos",
    "Active Directory": "Active Directory",
    "WinRM": "WinRM",
    "BloodHound": "BloodHound",
}
PHRASES = sorted(TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True)


def translate_heading(raw: str) -> str:
    name = re.sub(r"^\s*\d+(?:\.\d+)*\.?\s+", "", raw.strip())
    name = "".join(c for c in name if unicodedata.category(c) not in ("So", "Sk"))
    name = re.sub(r"\s+", " ", name).strip("- • \t\n")
    for english, french in PHRASES:
        if name.casefold() == english.casefold():
            return french
    for english, french in PHRASES:
        name = re.sub(r"\b" + re.escape(english) + r"\b", french, name, flags=re.I)
    return name.replace("\n", " ").strip()


def heading_note(topic: str) -> str:
    n = topic.casefold()
    checks = [
        (("dns",), "Interroger les enregistrements DNS et identifier les services associés."),
        (("nmap", "rustscan", "netcat", "port", "scan"), "Vérifier les ports et les services de la cible autorisée."),
        (("ldap", "kerberos", "domain", "active directory", "gpo", "spn", "bloodhound", "smb"),
         "Examiner les objets, les droits et les services du domaine."),
        (("password", "mot de passe", "credential", "hash", "hachage", "authentification"),
         "Vérifier les comptes, les secrets et les mécanismes d'authentification."),
        (("sql", "mysql", "mssql"), "Examiner les connexions, la configuration et les requêtes de la base de données."),
        (("web", "http", "xss", "file inclusion", "inclusion", "upload", "injection", "php", "cms"),
         "Examiner les entrées et les réponses de l'application web."),
        (("windows", "powershell", "winrm", "registre", "registry"),
         "Observer les permissions et la configuration de Windows."),
        (("linux", "sudo", "cron", "suid"),
         "Examiner les permissions et la configuration de Linux."),
        (("transfer", "transfert", "scp", "ftp", "tftp"),
         "Transférer ou récupérer des fichiers dans le laboratoire."),
        (("tunnel", "proxy", "forward", "redirection"),
         "Configurer et comprendre les chemins de communication réseau."),
        (("report", "rapport", "screenshot"),
         "Préparer et conserver des preuves exploitables dans un rapport."),
    ]
    for needles, note in checks:
        if any(needle in n for needle in needles):
            return note
    return "Commandes, paramètres et exemples associés à cette technique."


def lang_for(code: str, cls: list[str] | None = None) -> str:
    classes = " ".join(cls or []).lower()
    for lang in ("powershell", "bash", "python", "sql", "json", "xml", "javascript", "php", "html", "csharp", "ruby"):
        if lang in classes:
            return lang
    s = code.strip()
    if re.search(r"(?im)^\s*(get-|set-|new-|invoke-|test-|import-module|resolve-dnsname|\$[a-z_][\w-]*\s*=)", s):
        return "powershell"
    if re.search(r"(?im)^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE TABLE|EXEC(?:UTE)?\s+sp_)", s):
        return "sql"
    if re.search(r"(?m)^\s*(from [\w.]+ import |import \w+|def \w+\(|#!/usr/bin/env python)", s):
        return "python"
    if s.startswith("<?php"):
        return "php"
    if s.startswith("<") and re.match(r"<(?:html|script|svg|div|form)", s, re.I):
        return "html"
    if s.startswith("{") and s.rstrip().endswith("}"):
        return "json"
    if re.search(r"(?m)^\s*(nmap|sudo|curl|wget|whois|nc |host |nslookup|dig |ssh |scp |ftp |msfvenom|gobuster|ffuf|hydra|find |grep |python3? |cat |ls |chmod|echo |bash|socat|rustscan)\b", s):
        return "bash"
    return "text"


def fenced(value: str, classes: list[str] | None = None) -> str:
    # Prevent a command that contains backticks from closing its fence.
    n = max([len(x) for x in re.findall(r"`+", value)] or [0]) + 1
    fence = "`" * max(3, n)
    return "\n" + fence + lang_for(value, classes) + "\n" + value.rstrip("\n") + "\n" + fence + "\n"


def sanitize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().replace("[", "\\[").replace("]", "\\]")


def download() -> BeautifulSoup:
    response = requests.get(SOURCE, timeout=120, headers={"User-Agent": "Mozilla/5.0 (compatible; SKILL-ISSUE documentation import)"})
    response.raise_for_status()
    response.encoding = "utf-8"
    assert len(response.content) > 300_000, "Unexpectedly short OSCP source"
    return BeautifulSoup(response.text, "lxml")


def write_config(page_links: list[tuple[int, str, str]]) -> None:
    items = ",\n".join(
        "          { text: " + json.dumps(label, ensure_ascii=False)
        + ", link: '/oscp/" + slug + "' }"
        for n, slug, label in page_links if n < 20
    )
    config = """import { defineConfig } from 'vitepress'
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
      { text: 'OSCP', link: '/oscp/' },
      { text: 'CRTO', link: '/crto/' }
    ],
    sidebar: [
      {
        text: 'OSCP',
        link: '/oscp/',
        collapsed: false,
        items: [
""" + items + """
        ]
      },
      { text: 'CRTO', link: '/crto/', collapsed: true }
    ],
    search: { provider: 'local' },
    outline: { level: [2, 4], label: 'Sur cette page' },
    docFooter: { prev: 'Précédent', next: 'Suivant' },
    sidebarMenuLabel: 'Menu',
    returnToTopLabel: 'Retour en haut',
    socialLinks: [],
    editLink: false
  },
  markdown: {
    config(md) {
      md.use(tabsMarkdownPlugin)
      md.use(githubAlertsPlugin)
      md.use(youtubeEmbedPlugin)
      md.use(lineNumberPlugin)
    }
  }
})
"""
    Path("docs/.vitepress/config.mts").write_text(config, encoding="utf-8")


def main() -> None:
    soup = download()
    bodies = soup.select(".cheatsheet-content")
    assert bodies, "OSCP content container not found"
    body = max(bodies, key=lambda el: len(el.find_all("pre")))
    source_pre = list(body.find_all("pre"))
    source_inline = [x for x in body.find_all("code") if x.find_parent("pre") is None]
    assert len(source_pre) >= 1000, f"Source only contains {len(source_pre)} preformatted command blocks"
    assert len(source_inline) >= 500, f"Source only contains {len(source_inline)} inline code elements"

    OUT.mkdir(parents=True, exist_ok=True)
    imported_pre = set()
    imported_inline = set()
    page_items: list[tuple[int, str, str]] = []
    section_counts = {}
    current = None
    section_index = None
    section_lines = []

    def add_pre(pre: Tag) -> None:
        content = pre.get_text("\n", strip=False).replace("\r\n", "\n").replace("\r", "\n")
        if content.strip():
            code_tag = pre.find("code")
            cls = (code_tag.get("class", []) if code_tag else []) or pre.get("class", [])
            section_lines.append(fenced(content, cls))
        imported_pre.add(id(pre))

    def add_code(code: Tag) -> None:
        value = code.get_text("\n", strip=False).replace("\r\n", "\n")
        if value.strip():
            section_lines.append(fenced(value, code.get("class", [])))
        imported_inline.add(id(code))

    def flush() -> None:
        if section_index is None or current is None:
            return
        slug, french, description = TOPICS[section_index]
        title = f"OSCP · {french}"
        header = [
            "---",
            "title: " + json.dumps(title, ensure_ascii=False),
            "description: " + json.dumps(description, ensure_ascii=False),
            "---",
            "",
            "# " + title,
            "",
            description,
            "",
        ]
        footer = [
            "",
            "---",
            "",
            "Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](" + SOURCE + ").",
            "",
        ]
        (OUT / f"{slug}.md").write_text(
            "\n".join(header + section_lines + footer), encoding="utf-8"
        )

    for element in body.descendants:
        if not isinstance(element, Tag):
            continue
        tag = element.name
        if tag == "h2":
            heading = element.get_text(" ", strip=True)
            hit = re.match(r"^\s*(\d{1,2})\.\s+", heading)
            if not hit:
                continue
            number = int(hit.group(1))
            if number not in TOPICS:
                continue
            flush()
            section_index = number
            current = TOPICS[number][0]
            page_items.append((number, *TOPICS[number][:2]))
            section_lines = []
            section_counts[str(number)] = {"pre": 0, "inline": 0, "images": 0}
            continue

        if current is None:
            continue

        if tag in ("h3", "h4", "h5", "h6"):
            original = element.get_text(" ", strip=True)
            label = translate_heading(original)
            if not label:
                continue
            depth = min(5, int(tag[-1]) - 1)
            section_lines.extend(["", "#" * depth + " " + sanitize(label), "", heading_note(label), ""])
            continue

        if tag == "table":
            for tr in element.find_all("tr"):
                cells = tr.find_all(["th", "td"], recursive=False)
                if not cells or all(x.name == "th" for x in cells):
                    continue
                label = cells[0].get_text(" ", strip=True)
                label = translate_heading(label)
                if label and len(label) < 130:
                    section_lines.extend(["", "**" + sanitize(label) + "**", ""])
                for pre in tr.find_all("pre"):
                    if id(pre) not in imported_pre:
                        add_pre(pre)
                        section_counts[str(section_index)]["pre"] += 1
                for code in tr.find_all("code"):
                    if code.find_parent("pre") is None and id(code) not in imported_inline:
                        add_code(code)
                        section_counts[str(section_index)]["inline"] += 1
                if not tr.find("code") and not tr.find("pre") and len(cells) > 1:
                    value = " · ".join(x.get_text(" ", strip=True) for x in cells[1:])
                    if value and len(value) < 160:
                        section_lines.append(sanitize(value) + "\n")
            continue

        if tag == "pre":
            if element.find_parent("table") is not None or id(element) in imported_pre:
                continue
            add_pre(element)
            section_counts[str(section_index)]["pre"] += 1
            continue

        if tag == "code":
            if element.find_parent(["pre", "table", "h2", "h3", "h4", "h5", "h6"]) is not None:
                continue
            if id(element) in imported_inline:
                continue
            add_code(element)
            section_counts[str(section_index)]["inline"] += 1
            continue

        if tag == "img" and element.find_parent("table") is None:
            src = element.get("src", "").strip()
            if src and not src.startswith("data:"):
                absolute = urljoin(SOURCE, src)
                alt = sanitize(element.get("alt") or "Illustration")
                section_lines.append("\n![" + alt + "](" + absolute + ")\n")
                section_counts[str(section_index)]["images"] += 1

    flush()
    page_items.sort(key=lambda x: x[0])
    assert len(page_items) >= 19, f"Missing OSCP sections: {page_items}"

    index_lines = [
        "---", "title: OSCP", "description: Aide-mémoire OSCP en français",
        "---", "", "# OSCP", "",
        "**Offensive Security Certified Professional**", "",
        "Fiches par technique avec des explications courtes et les commandes originales dans des blocs copiables.", "",
        "## Sommaire", ""
    ]
    for number, slug, label in page_items:
        if number == 20:
            continue
        index_lines.append(f"- [{label}]({slug}.md) : {TOPICS[number][2]}")
    index_lines += [
        "", "Les commandes sont présentées telles qu'elles figurent dans la source, avec ses paramètres et ses exemples de laboratoire.",
        "",
        "Les commentaires intégrés aux commandes restent dans leur langue d'origine pour éviter d'altérer leur syntaxe.",
        "",
        "Source : [Emmanuel Solis, OSCP+ Cheatsheet](" + SOURCE + ").", ""
    ]
    (OUT / "index.md").write_text("\n".join(index_lines), encoding="utf-8")

    (ROOT / "crto").mkdir(parents=True, exist_ok=True)
    (ROOT / "crto" / "index.md").write_text(
        "---\ntitle: CRTO\ndescription: Certified Red Team Operator\n---\n\n# CRTO\n\n"
        "La rubrique CRTO sera alimentée après l'intégration OSCP. "
        "Les notes non encore intégrées ne sont pas présentées comme terminées.\n",
        encoding="utf-8"
    )
    (ROOT / "index.md").write_text(
        "---\ntitle: SKILL-ISSUE\ndescription: Documentation cybersécurité en français\n"
        "next: false\n---\n\n# SKILL-ISSUE\n\n"
        "**Notes techniques · Commandes copiables · Français**\n\n"
        "## Certifications\n\n"
        "### [OSCP](/oscp/)\n\n"
        "Commandes organisées par technique, avec une courte explication et un bloc copiable.\n\n"
        "### [CRTO](/crto/)\n\n"
        "Espace dédié aux notes Certified Red Team Operator.\n",
        encoding="utf-8"
    )
    write_config(page_items)

    # A few inline commands can sit outside numbered sections in the source.
    # Keep those as an appendix rather than silently discarding them.
    extra_inline = [
        c for c in source_inline
        if id(c) not in imported_inline
        and c.find_parent(["h2", "h3", "h4", "h5", "h6"]) is None
    ]
    extra_examples = [c.get_text(" ", strip=True)[:150] for c in extra_inline]
    if extra_inline:
        extra_path = OUT / "reconnaissance.md"
        with extra_path.open("a", encoding="utf-8") as appendix:
            appendix.write("\n## Syntaxes complémentaires de la source\n\n")
            appendix.write("Exemples présents hors des rubriques principales de la page d'origine.\n\n")
            for c in extra_inline:
                value = c.get_text("\n", strip=False)
                appendix.write(fenced(value, c.get("class", [])))
                imported_inline.add(id(c))

    skipped_pre = [p.get_text(" ",strip=True)[:80] for p in source_pre if id(p) not in imported_pre]
    skipped_inline = [c.get_text(" ",strip=True)[:80] for c in source_inline
                      if id(c) not in imported_inline
                      and c.find_parent(["h2", "h3", "h4", "h5", "h6"]) is None]
    report = {
        "source": SOURCE, "source_pre": len(source_pre),
        "source_inline_code": len(source_inline),
        "imported_pre": len(imported_pre),
        "imported_inline_code": len(imported_inline),
        "extra_inline_examples": extra_examples,\n        "skipped_pre": len(skipped_pre),
        "skipped_inline_code_outside_headings": len(skipped_inline),
        "skipped_pre_examples": skipped_pre[:20],
        "skipped_inline_examples": skipped_inline[:20],
        "sections": section_counts,
        "generated_pages": [x[1] + ".md" for x in page_items],
    }
    Path("oscp-import-audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in report.items() if not k.startswith("skipped_")}, ensure_ascii=False, indent=2))
    assert not skipped_pre, f"{len(skipped_pre)} source pre blocks were lost"
    assert not skipped_inline, f"{len(skipped_inline)} source inline code elements were lost"


if __name__ == "__main__":
    main()

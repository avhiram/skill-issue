#!/usr/bin/env python3
"""Readable, compact OSCP layout without changing the substantive command syntax."""
from pathlib import Path
import html
import re
import json

ROOT = Path("docs/src/oscp")
CSS = Path("docs/.vitepress/theme/custom.css")
FENCE = chr(96) * 3
LABEL = re.compile(r"^Commande [\x60]([^\x60]+)[\x60] pour la rubrique « ([^»]+) »\.$")

def inline_html(s: str) -> str:
    safe = html.escape(s)
    return re.sub(r"\x60([^\x60]+)\x60", r"<code>\1</code>", safe)

def compact_dns(src: str) -> tuple[str, bool]:
    start = src.find("## Énumération DNS\n")
    end = src.find("## Scan de ports\n", start)
    if start < 0 or end < 0:
        return src, False
    original = src[start:end]
    blocks = re.findall(r"\x60{3}(?:bash|text|powershell)\n([\s\S]*?)\n\x60{3}", original)
    if len(blocks) != 5:
        return src, False
    # Keep original commands byte-for-byte, but group them by purpose.
    comments = [
        "Résolution du domaine",
        "Enregistrement TXT du domaine",
        "Résolution d'un sous-domaine",
        "Requête TXT avec un serveur DNS spécifique",
        "Résolution en boucle depuis une liste",
    ]
    command_lines = []
    for comment, block in zip(comments, blocks):
        command_lines.extend(["# " + comment, block.strip(), ""])
    replacement = (
        "## Énumération DNS\n\n"
        "Interroger les enregistrements DNS et identifier les services associés.\n\n"
        "<p class=\"oscp-command-note\">Résolution classique, recherche TXT et vérification de sous-domaines.</p>\n\n"
        + FENCE + "bash\n" + "\n".join(command_lines).rstrip() + "\n" + FENCE + "\n\n\n"
    )
    return src[:start] + replacement + src[end:], True

def fix_versions(src: str) -> tuple[str,int]:
    # These are observations, not executable commands.
    pattern = (
        r"Commande [\x60]apache[\x60] pour la rubrique « Scan initial »\.\s*"
        r"\x60{3}text\nApache 2\.4\.49\n\x60{3}"
    )
    result, count = re.subn(
        pattern,
        "**Version du serveur dans l'exemple :** \x60Apache 2.4.49\x60.",
        src,
    )
    return result, count

def note_sentence(line: str) -> str:
    m = LABEL.fullmatch(line)
    if m:
        program, subject = m.groups()
        program_low = program.lower()
        if program_low == "telnet":
            return "Tester une connexion au port indiqué avec Telnet."
        if program_low == "for":
            return "Exécuter la boucle de vérification des hôtes."
        if program_low == "apache":
            return "Identifier la version du serveur Apache."
        if program_low == "ftp":
            return "Ouvrir une session FTP sur le serveur cible."
        if program_low == "nc":
            return "Tester une connexion TCP ou UDP avec Netcat."
        if program_low == "gobuster":
            return "Rechercher des noms ou chemins avec Gobuster."
        if program_low == "curl":
            return "Examiner la réponse HTTP avec Curl."
        return "Exemple avec l'outil " + program + "."
    return line

def format_notes(src: str) -> tuple[str,int,int]:
    lines = src.splitlines()
    result = []
    in_code = False
    last_description = None
    after_code = False
    styled = duplicates = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(FENCE):
            in_code = not in_code
            result.append(line)
            if not in_code:
                after_code = True
            continue
        if in_code:
            result.append(line)
            continue
        if re.match(r"^#{1,6} ", stripped):
            last_description = None
            after_code = False
            result.append(line)
            continue
        if not stripped:
            result.append(line)
            continue

        # Only turn a one-line explanation into a muted visual note when
        # a code fence is directly beneath it.
        next_nonempty = ""
        for candidate in lines[i+1:]:
            if candidate.strip():
                next_nonempty = candidate.strip()
                break
        description = (
            next_nonempty.startswith(FENCE)
            and not stripped.startswith(("-", "* ", "**", "|", ">", "<", FENCE, "---", "["))
            and not re.match(r"^\d+[.)] ", stripped)
            and len(stripped) <= 220
        )
        if description:
            sentence = note_sentence(stripped)
            if sentence == last_description and after_code:
                # The exact same label has already been shown for this group.
                duplicates += 1
                continue
            result.append('<p class="oscp-command-note">' + inline_html(sentence) + '</p>')
            last_description = sentence
            after_code = False
            styled += 1
        else:
            result.append(line)
            # Do not treat unrelated paragraphs as part of the same command group.
            last_description = None
            after_code = False
    rendered = "\n".join(result)
    rendered = re.sub(r"\n{4,}", "\n\n\n", rendered).rstrip() + "\n"
    return rendered, styled, duplicates

def main() -> None:
    changes = {}
    for path in sorted(ROOT.glob("*.md")):
        if path.stem in ("index", "ad-theorie", "cloud", "references"):
            continue
        original = path.read_text(encoding="utf-8")
        working, dns = compact_dns(original) if path.stem == "reconnaissance" else (original,False)
        working, versions = fix_versions(working)
        working, notes, duplicates = format_notes(working)
        if working != original:
            path.write_text(working, encoding="utf-8")
        changes[path.stem] = {
            "styled_explanations": notes,
            "repeated_labels_removed": duplicates,
            "dns_command_blocks_grouped": bool(dns),
            "noncommand_version_blocks_fixed": versions,
        }

    css = CSS.read_text(encoding="utf-8")
    marker = "/* SKILL-ISSUE OSCP visual hierarchy v2 */"
    if marker not in css:
        css += """
/* SKILL-ISSUE OSCP visual hierarchy v2 */
/* Headings are clearly distinct from short notes and executable examples. */
.vp-doc h1 { color: #F2ECFF; }
.vp-doc h2 {
  color: #DACBFA;
  font-weight: 740;
  border-color: #382844;
  margin-top: 1.85rem;
}
.vp-doc h3 { color: #BCA4F3; font-weight: 700; }
.vp-doc h4 { color: #A99BC2; font-weight: 650; }
.vp-doc .oscp-command-note {
  color: #ACA2BF;
  font-size: .86rem;
  line-height: 1.55;
  border-left: 2px solid #725397;
  padding-left: 11px;
  margin: .6rem 0 .55rem;
}
.vp-doc .oscp-command-note code {
  color: #CDB8F9;
  background: #221930;
  border: 1px solid #352445;
  border-radius: 4px;
  padding: 1px 4px;
}
.vp-doc .oscp-command-note + div[class*="language-"] {
  margin-top: .45rem;
}
.vp-doc div[class*="language-"] {
  background: #17121F;
  border-color: #30273F;
  margin-top: .4rem;
  margin-bottom: .85rem;
}
.vp-doc div[class*="language-"] pre {
  padding-top: 12px;
  padding-bottom: 12px;
}
"""
        CSS.write_text(css, encoding="utf-8")

    report = {
        "pages_processed": len(changes),
        "notes_styled": sum(x["styled_explanations"] for x in changes.values()),
        "duplicated_notes_removed": sum(x["repeated_labels_removed"] for x in changes.values()),
        "dns_grouped": any(x["dns_command_blocks_grouped"] for x in changes.values()),
        "misidentified_versions_fixed": sum(x["noncommand_version_blocks_fixed"] for x in changes.values()),
        "per_page": changes,
    }
    Path("oscp-visual-cleanup-audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    assert report["pages_processed"] >= 17
    assert report["notes_styled"] >= 200
    assert report["duplicated_notes_removed"] >= 10
    assert report["dns_grouped"]
    assert report["misidentified_versions_fixed"] >= 1
    recon = (ROOT / "reconnaissance.md").read_text(encoding="utf-8")
    dns_section = recon.split("## Énumération DNS", 1)[1].split("## Scan de ports", 1)[0]
    assert dns_section.count(FENCE) == 2
    assert "Interroger les enregistrements DNS." not in dns_section
    assert "# Enregistrement TXT du domaine" in recon
    assert "host -t txt [domain]" in recon
    print(json.dumps({k:v for k,v in report.items() if k!="per_page"}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

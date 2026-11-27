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
print("Native eJPT pages: 80; verified original images:",count)

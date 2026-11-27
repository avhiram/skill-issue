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
for page in report["pages"]:
    soup=BeautifulSoup((src/page).read_text(encoding="utf-8"),"html.parser")
    article=soup.find("article")
    if article is None:
        raise RuntimeError("Missing article: "+page)
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
    article["class"]="ejpt-native-content"
    article["v-pre"]=""
    article["data-ejpt-native"]="true"
    for img in article.find_all("img"):
        img["loading"]="lazy"
        img["decoding"]="async"
    title=titles[page[:-5]+".md"]
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
    dest.write_text(
        "---\ntitle: "+json.dumps(title,ensure_ascii=False)+"\noutline: deep\n---\n\n"
        "<script setup>\nimport chapterHtml from "+json.dumps(import_path)+"\n</script>\n\n"
        '<div class="ejpt-native-page" data-ejpt-native="true" v-html="chapterHtml"></div>\n',
        encoding="utf-8"
    )
assert len(list(target.rglob("*.md")))==80
print("Native eJPT pages: 80; verified original images:",count)

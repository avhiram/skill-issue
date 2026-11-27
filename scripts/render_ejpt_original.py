#!/usr/bin/env python3
"""Render the user-supplied eJPT archive without changing its source files."""
import collections
import hashlib
import html
import io
import json
import posixpath
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt

REVISION = "7e20a68c70b4a9fe086e9174138e0468eb375886"
MANIFEST = "f1026f3a3ab5978f0fcd322ac0c1f7bc3695a76797e66f3294fdc1bdc7e04fc1"
EXTRA = "fcdfa6446d243de1bc2be38bdb0fae902c28ac86c98b77d6e5bef45885cee1d5"
OUT = Path(sys.argv[1] if len(sys.argv)>1 else "docs/.vitepress/dist/ejpt/original")
BASE = "/skill-issue/ejpt/original/"
ARCHIVE = Path(sys.argv[2]) if len(sys.argv)>2 else None
SUPPLEMENT = Path(sys.argv[3]) if len(sys.argv)>3 else Path("imports/ejpt/cheatsheet-additional.md")

def digest(data):
    return hashlib.sha256(data).hexdigest()

if ARCHIVE:
    archive = ARCHIVE.read_bytes()
else:
    url = "https://codeload.github.com/e-hakson/eJPT/zip/" + REVISION
    with urllib.request.urlopen(url, timeout=120) as r:
        archive = r.read(150 * 1024 * 1024 + 1)
    if len(archive) > 150 * 1024 * 1024:
        raise RuntimeError("Archive too large")

files = {}
with zipfile.ZipFile(io.BytesIO(archive)) as z:
    for item in z.infolist():
        if item.is_dir():
            continue
        name = item.filename.split("/", 1)[1]
        if name.startswith("/") or ".." in PurePosixPath(name).parts or name in files:
            raise RuntimeError("Unsafe or duplicate archive path")
        files[name] = z.read(item)
manifest = "".join(digest(data) + "  " + name + "\n" for name, data in sorted(files.items()))
if len(files) != 826 or digest(manifest.encode()) != MANIFEST:
    raise RuntimeError("Archive differs from supplied original")
extra = SUPPLEMENT.read_bytes()
if digest(extra) != EXTRA:
    raise RuntimeError("Supplementary cheatsheet differs from supplied original")
files["cheatsheet-additional.md"] = extra
notes = sorted(n for n in files if n.endswith(".md"))
assert len(notes) == 80
assets = [n for n in files if n.lower().endswith((".png", ".gif"))]
assert len(assets) == 744
OUT.mkdir(parents=True, exist_ok=True)
def write(name, data):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))

def destination(n):
    if n.endswith(".md"):
        return n[:-3] + ".html"
    if n.endswith((".docx", ".pdf", ".html")):
        return "downloads/" + n
    return n

for n, data in files.items():
    if not n.endswith(".md"):
        write(destination(n), data)

md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")
def content(n):
    s = files[n].decode("utf-8-sig")
    return re.sub(r"\A---[ \t]*\r?\n[\s\S]*?\r?\n---[ \t]*\r?\n", "", s, count=1)
def title(n):
    m = re.search(r"^#\s+(.+)$", content(n), re.M)
    return m.group(1).strip() if m else PurePosixPath(n).stem
# Display titles are separate from the byte-verified source archive.
titles = json.loads(Path("imports/ejpt/display-titles.json").read_text(encoding="utf-8"))
if set(titles) != set(notes):
    raise RuntimeError("Display titles must cover all 80 original notes")
normalized_titles = [re.sub(r"\s+", " ", label).strip().casefold() for label in titles.values()]
if len(set(normalized_titles)) != len(notes):
    raise RuntimeError("Duplicate eJPT page titles")
emoji = re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0E\uFE0F\u200D\u20E3]")
def clean_heading(text):
    return re.sub(r"\s+", " ", emoji.sub("", text)).strip()

byname = collections.defaultdict(list)
for n in files:
    byname[PurePosixPath(n).name].append(n)
missing = []
repaired = []
def esc(s):
    return html.escape(str(s), quote=True)
def url(n):
    return BASE + urllib.parse.quote(destination(n), safe="/")
def slug(s):
    return re.sub(r"[^\w-]", "", re.sub(r"\s+", "-", s.lower().strip()))
groups = [
    ("Prérequis du pentest", "penetration-testing-prerequisites/"),
    ("Méthodologie et audit", "assessment-methodologies/"),
    ("Pentest système et réseau", "hostnetwork-penetration-testing/"),
    ("Pentest Web", "webapp-penetration-testing/"),
    ("Labs et préparation", "exam-preparation-labs/"),
    ("Cheatsheets et références", "")
]
def navigation(current):
    out = ['<a class="home" href="/skill-issue/ejpt/">eJPT · Accueil</a>',
           '<a href="'+url("README.md")+'">Cours original</a>']
    for label, prefix in groups:
        ns = [n for n in notes if (n.startswith(prefix) if prefix else "/" not in n or n.startswith("cheatsheet-files/")) and n!="README.md"]
        if not ns:
            continue
        ns.sort(key=lambda n:(not n.endswith("/README.md"),n))
        out.append('<details'+(' open' if current in ns else '')+'><summary>'+esc(label)+'</summary>')
        for n in ns:
            depth = max(0,len(PurePosixPath(n).parts)-2)
            out.append('<a class="'+('active' if n==current else '')+'" style="padding-left:'+str(10+depth*10)+'px" href="'+url(n)+'">'+esc(titles[n])+'</a>')
        out.append('</details>')
    return "".join(out)
allowed = set("a p img pre code li ul ol strong em s del blockquote h1 h2 h3 h4 h5 h6 hr details summary td tr th table thead tbody br kbd sup sub span div figure figcaption".split())
attrs = {"a":{"href","title","id","name"},"img":{"src","alt","title","width","height"},"code":{"class"},"ol":{"start"},"details":{"open"},"th":{"style"},"td":{"style"}}
def render(n):
    soup = BeautifulSoup(md.render(content(n)), "html.parser")
    for tag in list(soup.find_all(True)):
        if tag.name is None:
            continue
        if tag.name in {"script","iframe","object","embed","style","form","input","link","meta","base"}:
            tag.decompose()
            continue
        if tag.name not in allowed:
            tag.unwrap()
            continue
        for key in list(tag.attrs):
            if key not in attrs.get(tag.name,set()):
                del tag.attrs[key]
        if "style" in tag.attrs and not re.fullmatch(r"text-align:\s*(left|right|center);?",str(tag["style"])):
            del tag.attrs["style"]
        if tag.name not in {"a","img"}:
            continue
        key = "href" if tag.name=="a" else "src"
        u = tag.get(key)
        if not u:
            continue
        try:
            p = urllib.parse.urlsplit(u)
        except ValueError:
            del tag.attrs[key]
            continue
        if p.scheme or p.netloc:
            if p.scheme.lower() not in {"http","https","mailto"} or (tag.name=="img" and p.scheme.lower() not in {"http","https"}):
                del tag.attrs[key]
            elif tag.name=="a":
                tag["rel"]="noopener noreferrer"
            continue
        if not p.path:
            continue
        q = posixpath.normpath(posixpath.join(posixpath.dirname(n),urllib.parse.unquote(p.path)))
        if q not in files and q+"/README.md" in files:
            q += "/README.md"
        if q not in files:
            candidates=byname.get(PurePosixPath(q).name,[])
            if len(candidates)==1:
                repaired.append([n,u,candidates[0]])
                q=candidates[0]
        if q in files:
            tag[key]=url(q)+("?" + p.query if p.query else "")+("#"+p.fragment if p.fragment else "")
        else:
            missing.append([n,tag.name,u])
            if tag.name=="img":
                note=soup.new_tag("span",attrs={"class":"missing-image"})
                note.string="Image absente de l’archive originale : "+(tag.get("alt") or u)
                tag.replace_with(note)
    used=collections.Counter()
    for heading in soup.find_all(re.compile(r"^h[1-6]$")):
        base=slug(heading.get_text(" ",strip=True)) or "section"
        count=used[base]
        used[base]+=1
        heading["id"]=base+("-"+str(count) if count else "")
        # Keep original fragment identifiers and inline code intact.
        for node in list(heading.find_all(string=True)):
            if node.find_parent("code") is None:
                node.replace_with(emoji.sub("", str(node)))
    for node in list(soup.find_all(string=True)):
        if node.find_parent(["pre", "code", "kbd"]) is None:
            node.replace_with(emoji.sub("", str(node)))
    first = soup.find("h1")
    if first is None:
        first = soup.new_tag("h1")
        first.string = titles[n]
        soup.insert(0, first)
    elif not first.find(["img", "code"]):
        first.clear()
        first.append(titles[n])
    return str(soup)

CSS = """
:root{color-scheme:dark;--bg:#09070e;--panel:#15111d;--line:#382c48;--text:#f0edf8;--muted:#b6aec5;--brand:#b39aff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.65 system-ui,-apple-system,sans-serif}
a{color:var(--brand);text-underline-offset:3px}header{position:sticky;top:0;z-index:5;display:flex;align-items:center;gap:22px;padding:13px 24px;border-bottom:1px solid var(--line);background:var(--bg);flex-wrap:wrap}
header a{text-decoration:none}header strong{letter-spacing:.06em;color:var(--text)}.layout{max-width:1600px;margin:auto;display:grid;grid-template-columns:280px minmax(0,1fr)}
aside{position:sticky;top:58px;max-height:calc(100vh - 58px);overflow:auto;border-right:1px solid var(--line);padding:16px;background:#0d0a13}aside a{display:block;color:var(--muted);text-decoration:none;padding:6px 10px;font-size:13px;overflow-wrap:anywhere}aside a.active,aside a:hover{color:var(--brand);background:var(--panel)}aside summary{cursor:pointer;padding:9px 5px;font-weight:650;font-size:13px}
main{width:100%;max-width:1000px;padding:32px 38px 80px;margin:auto;align-self:start;min-width:0}h1,h2,h3,h4{color:#dacbfa;line-height:1.3;scroll-margin-top:90px}h1{font-size:2rem}h2{font-size:1.45rem;border-bottom:1px solid var(--line);padding-bottom:10px;margin-top:35px}h3{font-size:1.14rem}
img{max-width:100%;height:auto;display:block;margin:16px auto;border-radius:6px}pre{position:relative;background:#17121f;border:1px solid var(--line);border-radius:8px;padding:42px 14px 14px;overflow:auto;line-height:1.55}code{font:13px/1.55 ui-monospace,SFMono-Regular,Consolas,monospace;color:#cfbbff}p code,li code{background:#21182c;padding:2px 4px;border-radius:4px}pre code{color:inherit;background:none;padding:0}
button.copy{position:absolute;top:7px;right:8px;background:#22182e;color:#e5d8f4;border:1px solid #56416d;border-radius:5px;padding:5px 10px;cursor:pointer}blockquote{border-left:3px solid #7953be;padding:4px 12px;color:var(--muted);margin:15px 0}
table{display:block;max-width:100%;overflow:auto;border-collapse:collapse}td,th{border:1px solid var(--line);padding:8px 11px}article details{padding:10px 14px;border:1px solid var(--line);border-radius:8px;margin:12px 0}article summary{cursor:pointer}.source,.missing-image{color:var(--muted);font-size:12px}.source{border-top:1px solid var(--line);padding-top:12px;margin-top:32px}.missing-image{display:block;padding:10px;background:var(--panel);border:1px dashed var(--line)}
.mobile{display:none}@media(max-width:780px){.layout{display:block}aside{position:static;max-height:50vh;border-right:0;border-bottom:1px solid var(--line);display:none}aside.open{display:block}.mobile{display:inline-block}main{padding:20px 16px 70px}header{padding:12px;gap:14px}h1{font-size:1.6rem}}
"""
JS = """
document.querySelector('.mobile')?.addEventListener('click',()=>{const a=document.querySelector('aside');const open=a.classList.toggle('open');document.querySelector('.mobile').setAttribute('aria-expanded',String(open))});
for(const pre of document.querySelectorAll('pre')){const c=pre.querySelector('code');if(!c)continue;const b=document.createElement('button');b.type='button';b.className='copy';b.textContent='Copier';b.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(c.textContent);b.textContent='Copié';setTimeout(()=>b.textContent='Copier',1200)}catch{b.textContent='Sélectionner le texte'}});pre.append(b)}
"""
write("reader.css",CSS)
write("reader.js",JS)
for n in notes:
    body=render(n)
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(titles[n])+' | SKILL-ISSUE</title><link rel="stylesheet" href="'+BASE+'reader.css"></head><body><header><a href="/skill-issue/"><strong>SKILL-ISSUE</strong></a><a href="'+url("README.md")+'">Cours</a><a href="'+url("ejpt-cheatsheet.md")+'">Cheatsheet</a><a href="'+url("cheatsheet-additional.md")+'">Cheatsheet 2</a><button type="button" class="mobile" aria-expanded="false">Chapitres</button></header><div class="layout"><aside aria-label="Chapitres">'+navigation(n)+'</aside><main><article>'+body+'</article></main></div><script src="'+BASE+'reader.js" defer></script></body></html>'
    write(destination(n),page)
write("index.html",'<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=README.html"><title>eJPT</title></head><body><a href="README.html">Cours original</a></body></html>')
write("import-report.json",json.dumps({"revision":REVISION,"source_files":826,"markdown_pages":len(notes),"pages":[destination(n) for n in notes],"images":len(assets),"repaired_links":repaired,"missing_links":missing},ensure_ascii=False,indent=2))
assert all((OUT/destination(n)).is_file() for n in files)
assert all(digest((OUT/destination(n)).read_bytes())==digest(files[n]) for n in assets)
print(f"Verified: {len(notes)} original Markdown pages rendered, {len(assets)} unchanged images, {len(missing)} unresolved source references, {len(repaired)} repaired references")

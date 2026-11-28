#!/usr/bin/env python3
"""Lossless pinned TCM notes import; the reader is a separate presentation."""
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

manifest = json.loads(Path("imports/tcm/source-manifest.json").read_text(encoding="utf-8"))
revision = manifest["revision"]
repository = manifest["repository"]
expected = {entry["path"]: entry for entry in manifest["files"]}
out = Path(sys.argv[1])
if out.exists():
    raise RuntimeError("Refusing to overwrite an existing TCM output")
out.mkdir(parents=True)
base = "/skill-issue/tcm/original/"
archive_url = "https://codeload.github.com/" + repository + "/zip/" + revision
with urllib.request.urlopen(archive_url, timeout=120) as response:
    archive = response.read(150 * 1024 * 1024 + 1)
if len(archive) > 150 * 1024 * 1024:
    raise RuntimeError("Archive too large")
files = {}
with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
    for entry in bundle.infolist():
        if entry.is_dir():
            continue
        name = entry.filename.split("/", 1)[1]
        if not name or name.startswith("/") or ".." in PurePosixPath(name).parts or name in files:
            raise RuntimeError("Unsafe or duplicate path: " + name)
        files[name] = bundle.read(entry)
if set(files) != set(expected):
    raise RuntimeError("Archive inventory differs from pinned Git tree")
for name, data in files.items():
    record = expected[name]
    blob = hashlib.sha1(("blob " + str(len(data))).encode() + b"\0" + data).hexdigest()
    if len(data) != record["size"] or blob != record["sha"]:
        raise RuntimeError("Source file integrity mismatch: " + name)
# Keep the verified archive in memory only; never publish the ZIP.
(out / "LICENSE.txt").write_bytes(files["LICENSE"])
courses = manifest["courses"]
notes = [name for name in files if name.endswith(".md") and name.split("/")[0] in courses]
image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico"}
images = [name for name in files if PurePosixPath(name).suffix.lower() in image_extensions]
def write(name, data):
    dest = out / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))

def media(name):
    # Avoid hidden directories in deployed Pages assets; raw archive remains unchanged.
    return "media/" + "/".join("gitbook" if p == ".gitbook" else p for p in name.split("/"))

def page(name):
    return name[:-3] + ".html"

def url(name):
    return base + urllib.parse.quote(name, safe="/")

for name in images:
    write(media(name), files[name])
    assert (out / media(name)).read_bytes() == files[name]

md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")
missing = []
resolved_examples = []
code_counts = {}
summary = files["SUMMARY.md"].decode("utf-8")
ordered = [p for p in re.findall(r"\]\(([^)]+\.md)\)", summary) if p in notes]
ordered = list(dict.fromkeys(ordered + sorted(notes)))
titles = {}
def strip_frontmatter(text):
    return re.sub(r"\A---[ \t]*\r?\n[\s\S]*?\r?\n---[ \t]*\r?\n", "", text, count=1)

translation_dir = Path("imports/tcm/course-fr")
translations = {p.relative_to(translation_dir).as_posix(): p.read_text(encoding="utf-8") for p in translation_dir.rglob("*.md")}
if not set(translations).issubset(notes):
    raise RuntimeError("Unknown TCM translation path")

def source_text(name):
    return strip_frontmatter(translations.get(name, files[name].decode("utf-8-sig")))

def protected_content(markup):
    parsed = BeautifulSoup(md.render(markup), "html.parser")
    return {
        "code": [tag.get_text() for tag in parsed.select("code")],
        "links": [tag.get("href") for tag in parsed.select("a[href]")],
        "images": [(tag.get("src"), tag.get("alt")) for tag in parsed.select("img")],
    }

for name, translated in translations.items():
    if protected_content(strip_frontmatter(files[name].decode("utf-8-sig"))) != protected_content(strip_frontmatter(translated)):
        raise RuntimeError("Translation changed protected code, links or images: " + name)

for name in notes:
    match = re.search(r"^#\s+(.+)$", source_text(name), re.M)
    titles[name] = re.sub(r"[*_]", "", match.group(1)).strip() if match else PurePosixPath(name).stem

def render(name):
    source = source_text(name)
    soup = BeautifulSoup(md.render(source), "html.parser")
    original_blocks = [block.get_text() for block in soup.select("pre code")]
    original_images = len(soup.select("img"))
    # Render source examples as inert text; never execute embedded source scripts.
    for tag in list(soup.find_all(True)):
        if tag.name is None:
            continue
        if tag.name in {"script", "iframe", "object", "embed", "style", "form", "input", "link", "meta", "base", "svg"}:
            tag.decompose()
            continue
        for key in list(tag.attrs):
            if key.lower().startswith("on") or key.lower() in {"srcdoc", "srcset", "formaction", "style"}:
                del tag.attrs[key]
        if tag.name not in {"a", "img"}:
            continue
        key = "href" if tag.name == "a" else "src"
        value = tag.get(key)
        if not value:
            continue
        try:
            parts = urllib.parse.urlsplit(value)
        except ValueError:
            del tag.attrs[key]
            continue
        if parts.scheme or parts.netloc:
            if parts.scheme.lower() not in {"https", "http", "mailto"}:
                del tag.attrs[key]
            elif tag.name == "a":
                tag["rel"] = "noopener noreferrer"
            continue
        if not parts.path:
            continue
        # This source label is an address in a lab example, not a local document.
        if name == "peh/3-eth-hack/capstone.md" and tag.name == "a" and value == "192.168.31.128":
            tag.unwrap()
            resolved_examples.append({"page":name,"reference":value,"rendering":"plain source text"})
            continue
        target = posixpath.normpath(posixpath.join(posixpath.dirname(name), urllib.parse.unquote(parts.path)))
        if target not in files and target + "/README.md" in files:
            target += "/README.md"
        if target in notes:
            dest = url(page(target))
        elif target in images:
            dest = url(media(target))
        elif target in files:
            # Other source material remains available at its original location.
            dest = "https://github.com/" + repository + "/blob/" + revision + "/" + urllib.parse.quote(target, safe="/")
        else:
            missing.append({"page":name,"kind":tag.name,"reference":value})
            # Keep source text, avoid guessing a substitute.
            continue
        tag[key] = dest + ("?" + parts.query if parts.query else "") + ("#" + parts.fragment if parts.fragment else "")
    if original_blocks != [block.get_text() for block in soup.select("pre code")]:
        raise RuntimeError("Rendered code differs from source: " + name)
    code_counts[name] = len(original_blocks)
    if len(soup.select("img")) != original_images:
        raise RuntimeError("Rendered images differ from source: " + name)
    # Move explicit instructor credits from the course introductions to the
    # consolidated legal page. The source archive and original Markdown stay intact.
    relocated = {
        "mapt/README.md": "Instructor: Aaron Wilson",
        "peh/README.md": "Instructor: Heath Adams - The Cyber Mentor",
    }
    if name in relocated:
        matches = [p for p in soup.find_all("p") if p.get_text(" ", strip=True) == relocated[name]]
        if len(matches) != 1:
            raise RuntimeError("Unexpected instructor attribution: " + name)
        matches[0].decompose()
    # UI only: add stable heading anchors and copy buttons outside original code.
    ids = set(tag.get("id") for tag in soup.find_all(id=True))
    for i, heading in enumerate(soup.select("h2, h3, h4"), 1):
        if not heading.get("id"):
            ident = "section-" + str(i)
            while ident in ids:
                ident += "-a"
            heading["id"] = ident
            ids.add(ident)
    for block in list(soup.select("pre")):
        if not block.find("code"):
            continue
        wrapper = soup.new_tag("div", attrs={"class":"code-panel"})
        block.wrap(wrapper)
        code = block.find("code")
        language = next((x[9:] for x in code.get("class", []) if x.startswith("language-")), "")
        toolbar = soup.new_tag("div", attrs={"class":"code-toolbar"})
        label = soup.new_tag("span")
        label.string = language.upper() if language else "CODE"
        toolbar.append(label)
        button = soup.new_tag("button", attrs={"type":"button","class":"copy-code","aria-label":"Copier le bloc"})
        button.string = "Copier"
        toolbar.append(button)
        block.insert_before(toolbar)
    if original_blocks != [block.get_text() for block in soup.select("pre code")]:
        raise RuntimeError("UI changed source commands: " + name)
    return str(soup)

css = """
:root{color-scheme:dark;--bg:#09070e;--panel:#17121f;--line:#3a2b4b;--text:#efeaf7;--muted:#b6aec5;--brand:#b39aff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,sans-serif}
a{color:var(--brand);text-underline-offset:3px}header{padding:18px 24px;border-bottom:1px solid var(--line);display:flex;gap:22px;flex-wrap:wrap}
header a{text-decoration:none}header strong{letter-spacing:.04em}
.layout{display:grid;grid-template-columns:280px minmax(0,1fr);max-width:1450px;margin:auto}
aside{padding:20px;border-right:1px solid var(--line);position:sticky;top:0;max-height:100vh;overflow:auto}
aside a{display:block;padding:6px 10px;font-size:14px;overflow-wrap:anywhere;border-radius:6px;text-decoration:none}aside a:hover,aside a[aria-current="page"]{background:var(--panel);color:var(--text)}aside summary{cursor:pointer;color:var(--text);margin:10px 0}aside .module{margin:6px 0 6px 8px;padding-left:9px;border-left:1px solid var(--line)}aside .module summary{font-size:14px;font-weight:600}aside .module a{padding-left:12px}aside .course-home{font-weight:600}
main{width:100%;max-width:1050px;margin:auto;padding:28px 36px 80px;min-width:0;align-self:start}
h1,h2,h3,h4{color:#e2d4fb;line-height:1.35}h2{border-bottom:1px solid var(--line);padding-bottom:10px;margin-top:35px}
img{max-width:100%;height:auto;display:block;margin:16px auto}pre{background:var(--panel);border:1px solid var(--line);padding:16px;border-radius:8px;overflow:auto}
code{font:14px/1.55 ui-monospace,monospace;color:#d9c6fa}pre code{color:inherit}blockquote{border-left:3px solid var(--brand);margin:12px 0;padding:4px 14px;color:var(--muted)}
table{display:block;max-width:100%;overflow:auto;border-collapse:collapse}td,th{border:1px solid var(--line);padding:8px}footer{margin-top:42px;border-top:1px solid var(--line);padding-top:16px;color:var(--muted);font-size:13px}
@media(max-width:780px){.layout{display:block}aside{position:static;max-height:none;border:0;border-bottom:1px solid var(--line);padding:14px 20px}main{padding:20px 16px 70px}header{padding:14px 16px}}
"""
css += """
header{position:sticky;top:0;z-index:10;background:var(--bg);align-items:center}
header .nav-toggle,header .reading-toggle,.copy-code{font:inherit;font-size:12px;border:1px solid var(--line);border-radius:7px;background:var(--panel);color:var(--text);padding:6px 12px;cursor:pointer}
header .reading-toggle{margin-left:auto}header .nav-toggle{display:none}
aside{top:65px;max-height:calc(100vh - 65px)}main{max-width:980px}
.breadcrumb{display:flex;flex-wrap:wrap;gap:8px;color:var(--muted);font-size:13px;margin:0 0 24px}
.breadcrumb a{text-decoration:none}.breadcrumb span{overflow-wrap:anywhere}
article h1,article h2,article h3,article h4{scroll-margin-top:90px}
article h1{font-size:clamp(25px,4vw,36px);margin:0 0 25px}
article h2{font-size:22px}article h3{font-size:18px}article p,article ul,article ol{margin:12px 0}
.code-panel{margin:16px 0;border:1px solid var(--line);border-radius:9px;overflow:hidden;background:var(--panel)}
.code-toolbar{display:flex;justify-content:space-between;align-items:center;padding:7px 12px;border-bottom:1px solid var(--line);color:var(--muted);font-size:11px;letter-spacing:.04em}
.code-panel pre{margin:0;border:0;border-radius:0;padding:16px;max-width:100%}.copy-code{letter-spacing:0}
.page-nav{display:flex;justify-content:space-between;gap:12px;margin:42px 0 0}
.page-nav a{border:1px solid var(--line);border-radius:9px;padding:12px 16px;text-decoration:none;flex:1;min-width:0;overflow-wrap:anywhere}
.page-nav a:last-child{text-align:right}.page-nav small{display:block;color:var(--muted)}
.reading-mode .layout{display:block}.reading-mode aside{display:none}
@media(max-width:780px){header .nav-toggle{display:inline-block}aside{display:none;position:static;max-height:none}aside.open{display:block}main{padding-top:22px}.page-nav a{padding:10px;font-size:13px}header{gap:12px}.reading-mode aside.open{display:block}}
"""
write("reader.css", css)
write("reader.js", """document.addEventListener('click', async (event) => {
  const button = event.target.closest('button');
  if (!button) return;
  if (button.classList.contains('nav-toggle')) {
    const nav = document.querySelector('aside');
    const open = nav.classList.toggle('open');
    button.setAttribute('aria-expanded', String(open));
  }
  if (button.classList.contains('reading-toggle')) {
    const enabled = document.body.classList.toggle('reading-mode');
    button.setAttribute('aria-pressed', String(enabled));
  }
  if (!button.classList.contains('copy-code')) return;
  const code = button.closest('.code-panel').querySelector('pre code');
  try {
    await navigator.clipboard.writeText(code.textContent);
    button.textContent = 'Copié';
  } catch {
    const selection = window.getSelection(), range = document.createRange();
    range.selectNodeContents(code); selection.removeAllRanges(); selection.addRange(range);
    button.textContent = 'Sélectionné';
  }
  window.setTimeout(() => {button.textContent = 'Copier'}, 1800);
});
""")
escape = html.escape
for name in ordered:
    current = name.split("/")[0]
    nav = []
    def nav_link(item, label=None, extra_class=""):
        return ('<a href="' + url(page(item)) + '"' +
            (' aria-current="page"' if item == name else '') +
            (' class="' + extra_class + '"' if extra_class else '') +
            '>' + escape(label or titles[item]) + '</a>')
    for course in courses:
        home = course + "/README.md"
        nav.append('<details' + (' open' if course == current else '') + '><summary>' + escape(titles[home]) + '</summary>')
        nav.append(nav_link(home, "Accueil du parcours", "course-home"))
        members = [item for item in ordered if item.startswith(course+"/") and item != home]
        chapters = list(dict.fromkeys(item.split("/")[1] for item in members if len(item.split("/")) > 2))
        for chapter in chapters:
            prefix = course + "/" + chapter + "/"
            module_pages = [item for item in members if item.startswith(prefix)]
            module_home = prefix + "README.md"
            module_title = titles.get(module_home, chapter)
            if len(module_pages) == 1:
                nav.append(nav_link(module_pages[0], module_title))
                continue
            nav.append('<details class="module"' + (' open' if name.startswith(prefix) else '') + '><summary>' + escape(module_title) + '</summary>')
            for item in module_pages:
                nav.append(nav_link(item, "Plan du chapitre" if item == module_home else None))
            nav.append("</details>")
        for item in members:
            if len(item.split("/")) == 2:
                nav.append(nav_link(item))
        nav.append("</details>")
    body = render(name)
    course_home = current + "/README.md"
    course_pages = [item for item in ordered if item.startswith(current+"/")]
    index = course_pages.index(name)
    breadcrumb = '<nav class="breadcrumb" aria-label="Fil d’Ariane"><a href="/skill-issue/">Accueil</a><span>›</span><a href="/skill-issue/tcm/">TCM</a><span>›</span>'
    if name != course_home:
        breadcrumb += '<a href="' + url(page(course_home)) + '">' + escape(titles[course_home]) + '</a><span>›</span>'
    breadcrumb += '<span aria-current="page">' + escape(titles[name]) + '</span></nav>'
    adjacent = '<nav class="page-nav" aria-label="Navigation du cours">'
    if index:
        previous = course_pages[index-1]
        adjacent += '<a href="' + url(page(previous)) + '"><small>Précédent</small>' + escape(titles[previous]) + '</a>'
    if index+1 < len(course_pages):
        following = course_pages[index+1]
        adjacent += '<a href="' + url(page(following)) + '"><small>Suivant</small>' + escape(titles[following]) + '</a>'
    adjacent += '</nav>'
    document = ('<!doctype html><html lang="' + ("fr" if name in translations else "en") + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>' + escape(titles[name]) + ' | SKILL-ISSUE</title><link rel="stylesheet" href="' + url("reader.css") + '">'
        '<script src="' + url("reader.js") + '" defer></script></head><body><header><a href="/skill-issue/"><strong>SKILL-ISSUE</strong></a><a href="/skill-issue/tcm/">TCM</a>'
        '<button type="button" class="nav-toggle" aria-expanded="false">Chapitres</button><button type="button" class="reading-toggle" aria-pressed="false">Lecture</button></header>'
        '<div class="layout"><aside aria-label="Chapitres">' + "".join(nav) + '</aside><main>' + breadcrumb + '<article>' + body + '</article>' + adjacent +
        '</main></div></body></html>')
    write(page(name), document)

report = {"repository":repository,"revision":revision,"files_verified":len(files),"archive_sha256":hashlib.sha256(archive).hexdigest(),"images_verified":len(images),"courses":{course:sum(n.startswith(course+"/") for n in notes) for course in courses},"rendered_pages":len(notes),"unresolved_source_references":missing,"resolved_lab_examples":resolved_examples,"code_blocks_verified":sum(code_counts.values()),"code_pages_verified":len(code_counts),"translated_pages":sorted(translations),"translated_course_counts":{course:sum(n.startswith(course+"/") for n in translations) for course in courses}}
write("import-report.json", json.dumps(report, ensure_ascii=False, indent=2))
assert all((out / page(n)).is_file() for n in notes)
assert not (out / "source.zip").exists() and not (out / "markdown").exists(), "Raw course archive must not be published"
print(json.dumps(report, ensure_ascii=False))
if missing:
    raise RuntimeError("Unresolved TCM references: " + json.dumps(missing, ensure_ascii=False))

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
(out / "source.zip").write_bytes(archive)
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
for name in notes:
    write("markdown/" + name, files[name])

md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")
missing = []
resolved_examples = []
code_counts = {}
summary = files["SUMMARY.md"].decode("utf-8")
ordered = [p for p in re.findall(r"\]\(([^)]+\.md)\)", summary) if p in notes]
ordered = list(dict.fromkeys(ordered + sorted(notes)))
titles = {}
def source_text(name):
    return re.sub(r"\A---[ \t]*\r?\n[\s\S]*?\r?\n---[ \t]*\r?\n", "", files[name].decode("utf-8-sig"), count=1)
for name in notes:
    match = re.search(r"^#\s+(.+)$", source_text(name), re.M)
    titles[name] = re.sub(r"[*_]", "", match.group(1)).strip() if match else PurePosixPath(name).stem

def render(name):
    source = source_text(name)
    soup = BeautifulSoup(md.render(source), "html.parser")
    original_blocks = [block.get_text() for block in soup.select("pre code")]
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
            # Other source material remains available in the complete archive.
            dest = "https://github.com/" + repository + "/blob/" + revision + "/" + urllib.parse.quote(target, safe="/")
        else:
            missing.append({"page":name,"kind":tag.name,"reference":value})
            # Keep source text, avoid guessing a substitute.
            continue
        tag[key] = dest + ("?" + parts.query if parts.query else "") + ("#" + parts.fragment if parts.fragment else "")
    if original_blocks != [block.get_text() for block in soup.select("pre code")]:
        raise RuntimeError("Rendered code differs from source: " + name)
    code_counts[name] = len(original_blocks)
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
write("reader.css", css)
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
    document = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>' + escape(titles[name]) + ' | SKILL-ISSUE</title><link rel="stylesheet" href="' + url("reader.css") + '">'
        '</head><body><header><a href="/skill-issue/"><strong>SKILL-ISSUE</strong></a><a href="/skill-issue/tcm/">TCM</a></header>'
        '<div class="layout"><aside aria-label="Courses">' + "".join(nav) + '</aside><main><article>' + body + '</article>'
        '<footer>Source: <a href="https://github.com/' + repository + '/tree/' + revision + '">syselement/tcm-sec-notes</a> · '
        '<a href="' + url("LICENSE.txt") + '">CC BY-SA 4.0</a> · '
        '<a href="' + url("markdown/"+name) + '">Original Markdown</a> · '
        '<a href="' + url("source.zip") + '">Complete source archive</a>. '
        'Original credits and third-party notices remain applicable. Presentation adapted for SKILL-ISSUE.</footer></main></div></body></html>')
    write(page(name), document)

report = {"repository":repository,"revision":revision,"files_verified":len(files),"archive_sha256":hashlib.sha256(archive).hexdigest(),"images_verified":len(images),"courses":{course:sum(n.startswith(course+"/") for n in notes) for course in courses},"rendered_pages":len(notes),"unresolved_source_references":missing,"resolved_lab_examples":resolved_examples,"code_blocks_verified":sum(code_counts.values()),"code_pages_verified":len(code_counts)}
write("import-report.json", json.dumps(report, ensure_ascii=False, indent=2))
assert all((out / page(n)).is_file() and (out / ("markdown/"+n)).read_bytes() == files[n] for n in notes)
print(json.dumps(report, ensure_ascii=False))
if missing:
    raise RuntimeError("Unresolved TCM references: " + json.dumps(missing, ensure_ascii=False))

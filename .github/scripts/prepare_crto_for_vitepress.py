#!/usr/bin/env python3
"""Escape documentation placeholders for VitePress rendering only.

Original upstream Git blobs remain untouched in Git history. The publishing workflow
restores the working copies after VitePress has rendered the site.
"""
from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path("docs/src/crto/botesjuan")
ALLOWED_HTML = {
    "a", "abbr", "b", "blockquote", "br", "caption", "center", "code",
    "col", "colgroup", "dd", "del", "details", "div", "dl", "dt",
    "em", "figure", "figcaption", "font", "h1", "h2", "h3", "h4",
    "h5", "h6", "hr", "i", "iframe", "img", "input", "kbd",
    "li", "mark", "ol", "p", "pre", "s", "small", "span", "strong",
    "sub", "summary", "sup", "table", "tbody", "td", "th", "thead",
    "tr", "u", "ul",
}
TAGS = re.compile(r"<(/?)([A-Za-z][A-Za-z0-9:-]*)([^<>]*)>")
INLINE_CODE = re.compile(r"(`+[^`]*`+)")


def escape_placeholders(fragment: str) -> str:
    def replace(match: re.Match) -> str:
        name = match.group(2).lower()
        raw = match.group(0)
        if name in ALLOWED_HTML or name.startswith(("http:", "https:", "mailto:")):
            return raw
        return raw.replace("<", "&lt;").replace(">", "&gt;")

    return TAGS.sub(replace, fragment)


for path in ROOT.rglob("*.md"):
    original = path.read_text(encoding="utf-8")
    output = []
    fence = None
    for line in original.splitlines(keepends=True):
        stripped = line.lstrip()
        marker = re.match(r"^(`{3,}|~{3,})", stripped)
        if marker:
            sig = marker.group(1)
            if fence is None:
                fence = sig[0]
            elif fence == sig[0]:
                fence = None
            output.append(line)
            continue
        if fence:
            output.append(line)
            continue
        pieces = INLINE_CODE.split(line)
        output.append("".join(
            chunk if i % 2 else escape_placeholders(chunk)
            for i, chunk in enumerate(pieces)
        ))
    rendered = "".join(output)
    # Root-relative paths in the upstream repository assume the website is
    # hosted at /. GitHub Pages uses /skill-issue/, so rewrite links only in
    # this temporary build-time working copy, leaving Git blobs unchanged.
    relative_root = "../" * len(path.relative_to(ROOT).parts[:-1]) or "./"
    for folder in ("images", "labs", "cheatsheets", "notes"):
        rendered = rendered.replace(f'="/{folder}/', f'="{relative_root}{folder}/')
        rendered = rendered.replace(f"='/{folder}/", f"='{relative_root}{folder}/")
        rendered = rendered.replace(f'](/{folder}/', f']({relative_root}{folder}/')
    rendered = rendered.replace("](/crto-command-library.md", f"]({relative_root}crto-command-library.md")
    # Some upstream notes reference images absent from their own repository.
    # Render an explicit message for missing assets, while leaving source untouched.
    def missing_asset(url: str) -> bool:
        if url.startswith(("https://", "http://", "data:", "#")):
            return False
        local = unquote(url.split("#", 1)[0].split("?", 1)[0])
        return not (path.parent / local).is_file()

    def check_markdown_image(match: re.Match) -> str:
        alt, url = match.group(1), match.group(2)
        if not missing_asset(url):
            return match.group(0)
        return ""

    rendered = re.sub(r"!\[([^\]]*)\]\(([^\s)]+)\)", check_markdown_image, rendered)

    def check_html_image(match: re.Match) -> str:
        url = match.group(2)
        if not missing_asset(url):
            return match.group(0)
        return ""

    rendered = re.sub(r"<img\b[^>]*?\bsrc\s*=\s*([\"'])([^\"']+)\1[^>]*>", check_html_image, rendered, flags=re.IGNORECASE)
    if path.relative_to(ROOT).as_posix() == "labs/defence-evasion-lab-Malleable.md":
        rendered = rendered.replace("](Exam-Instructions.md)", "](../notes/Exam-Instructions.md)")
    if rendered != original:
        path.write_text(rendered, encoding="utf-8")

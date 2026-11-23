#!/usr/bin/env python3
"""Audit VitePress HTML for Markdown fences accidentally rendered as text."""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re

FENCE = re.compile(r'(?<!`)`{3,}[A-Za-z0-9_+#.-]*')
SUPPRESSED = {'pre', 'code', 'script', 'style', 'textarea', 'svg'}


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = {tag: 0 for tag in SUPPRESSED}
        self.hits = []

    def handle_starttag(self, tag, attrs):
        if tag in SUPPRESSED:
            self.depth[tag] += 1

    def handle_endtag(self, tag):
        if tag in SUPPRESSED:
            self.depth[tag] = max(0, self.depth[tag] - 1)

    def handle_data(self, data):
        if any(self.depth.values()):
            return
        for match in FENCE.finditer(data):
            left = max(0, match.start() - 65)
            right = min(len(data), match.end() + 90)
            self.hits.append(' '.join(data[left:right].split()))


def audit(root):
    files = sorted(root.rglob('*.html'))
    issues = []
    for html_file in files:
        parser = VisibleText()
        parser.feed(html_file.read_text(encoding='utf-8'))
        if parser.hits:
            issues.append({
                'file': str(html_file.relative_to(root)),
                'visible_markdown_fences': len(parser.hits),
                'examples': parser.hits[:8],
            })
    return {
        'checked_html_pages': len(files),
        'affected_pages': len(issues),
        'total_visible_fences': sum(i['visible_markdown_fences'] for i in issues),
        'issues': issues,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('site_dir', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    result = audit(args.site_dir)
    report = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + '\n', encoding='utf-8')
    print(f"Pages vérifiées : {result['checked_html_pages']}; "
          f"pages suspectes : {result['affected_pages']}; "
          f"balises visibles : {result['total_visible_fences']}")
    for issue in result['issues']:
        print('Rendu Markdown suspect :', issue['file'])
    if args.strict and result['affected_pages']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()

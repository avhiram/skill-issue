#!/usr/bin/env python3
"""Use a simple hyphen in published site prose without changing code examples."""

from pathlib import Path
import re

ROOT = Path('docs/src')
FENCE = re.compile(r'^\s*(?:>\s*)?(`{3,}|~{3,})')
INLINE_CODE = re.compile(r'(`+[^`\r\n]*`+)')


def normalize_markdown(markdown: str) -> str:
    fence = None
    result = []
    for line in markdown.splitlines(keepends=True):
        match = FENCE.match(line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1]:
                fence = None
            result.append(line)
            continue
        if fence is not None:
            result.append(line)
            continue
        parts = INLINE_CODE.split(line)
        result.append(''.join(
            part if index % 2 else part.replace('\u2014', '-')
            for index, part in enumerate(parts)
        ))
    return ''.join(result)


def main() -> None:
    paths = [ROOT / 'index.md']
    paths.extend(sorted((ROOT / 'oscp').rglob('*.md')))
    paths.extend(sorted((ROOT / 'crto').rglob('*.md')))
    changed = 0
    replaced = 0
    for path in paths:
        if not path.is_file():
            continue
        before = path.read_text(encoding='utf-8')
        after = normalize_markdown(before)
        if after == before:
            continue
        changed += 1
        replaced += before.count('\u2014') - after.count('\u2014')
        path.write_text(after, encoding='utf-8')
    print(f'Tirets longs remplacés dans le texte : {replaced} sur {changed} pages Markdown.')


if __name__ == '__main__':
    main()

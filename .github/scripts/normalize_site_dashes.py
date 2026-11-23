#!/usr/bin/env python3
"""Use a simple ASCII hyphen in all published Markdown site content."""

from pathlib import Path

ROOT = Path('docs/src')


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
        after = before.replace('\u2014', '-')
        if after == before:
            continue
        changed += 1
        replaced += before.count('\u2014')
        path.write_text(after, encoding='utf-8')
    print(f'Tirets longs remplacés : {replaced} sur {changed} pages Markdown.')


if __name__ == '__main__':
    main()

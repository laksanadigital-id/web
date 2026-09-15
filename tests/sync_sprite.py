"""Regenerate the inlined icon sprite block in every page from assets/icons.svg.

The pages inline the symbols (instead of referencing assets/icons.svg) so that
<use> keeps working when a page is opened directly from disk, where external
sprite references are blocked. Run this after editing assets/icons.svg:
    python tests/sync_sprite.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ('index.html', 'apotek.html')
BLOCK = re.compile(
    r'  <!-- Icon sprite.*?\n  <svg class="hidden".*?\n  </svg>\n',
    re.S,
)

sprite = (ROOT / 'assets/icons.svg').read_text(encoding='utf-8')
inner = sprite[sprite.index('>', sprite.index('<svg')) + 1:sprite.rindex('</svg>')]
symbols = re.findall(r'<symbol .*?</symbol>', inner, re.S)

replacement = '\n'.join([
    '  <!-- Icon sprite, inlined so <use> works for both http:// and file:// pages. Generated from assets/icons.svg by tests/sync_sprite.py. -->',
    '  <svg class="hidden" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">',
    *[f'    {symbol}' for symbol in symbols],
    '  </svg>',
]) + '\n'

for name in PAGES:
    path = ROOT / name
    source = path.read_text(encoding='utf-8')
    updated, count = BLOCK.subn(lambda _: replacement, source, count=1)
    assert count == 1, f'{name}: inline sprite block not found'
    path.write_text(updated, encoding='utf-8')
    print(f'{name}: {len(symbols)} symbols inlined')

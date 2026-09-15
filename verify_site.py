#!/usr/bin/env python3
"""Structural verification for Laksana Digital static Tailwind pages."""
import re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent
PAGES=(ROOT/'index.html',ROOT/'apotek.html')
class Parser(HTMLParser):
 def __init__(self): super().__init__(); self.images=[]; self.styles=0; self.inline=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='img' and a.get('src'): self.images.append(a['src'])
  if tag=='style': self.styles+=1
  if 'style' in a:self.inline.append(a['style'])
def check(path):
 s=path.read_text(encoding='utf8'); p=Parser();p.feed(s); bad=[]
 checks={
 'Tailwind CDN/config missing': 'cdn.tailwindcss.com' in s and 'tailwind.config' in s,
 'Inter-only setup missing': 'family=Inter' in s and "fontFamily:{sans:['Inter','sans-serif']}" in s and 'Bricolage' not in s,
 'blue accent/light base missing': 'bg-white' in s and 'blue-' in s,
 'dark theme toggle missing': all(x in s for x in ('dark:','data-theme-toggle','localStorage','prefers-color-scheme')),
 'responsive mobile menu missing': all(x in s for x in ('id="nav-links"','id="hamburger"','aria-expanded','aria-controls','md:hidden')),
 'reduced motion missing': 'prefers-reduced-motion' in s and 'motion-reduce:' in s,
 'reveals missing': 'fade-up' in s and 'IntersectionObserver' in s,
 'FAQ semantics missing': '<details' in s and '<summary' in s,
 }
 bad += [f'{path.name}: {msg}' for msg,ok in checks.items() if not ok]
 if p.styles or re.search(r'<style\b',s,re.I):bad.append(f'{path.name}: forbidden <style> found')
 if p.inline or re.search(r'\sstyle\s*=',s,re.I):bad.append(f'{path.name}: forbidden style= found')
 for src in p.images:
  u=urlsplit(src)
  if not u.scheme and not src.startswith(('//','data:')) and not (path.parent/u.path).is_file():bad.append(f'{path.name}: missing image {src}')
 return bad
bad=[]
for p in PAGES: bad += check(p) if p.is_file() else [f'missing {p.name}']
i=PAGES[0].read_text(encoding='utf8'); a=PAGES[1].read_text(encoding='utf8')
if not all(x in i for x in ('Lynk.id','WhatsApp')):bad.append('index purchase wording incomplete')
checks={'download':'href="apotek-demo.exe"' in a,'buy links':'lynk.id/nor1c/45w2ryrdxn3p' in a and 'wa.me/' in a,'dialog':'role="dialog"' in a and 'aria-modal="true"' in a,'focus management':'lastFocus' in a and '.focus()' in a,'keyboard':'Escape' in a and 'ArrowLeft' in a and 'ArrowRight' in a and "e.key==='Tab'" in a,'triggers':'data-index' in a and 'openLightbox' in a}
bad += [f'apotek: {k} missing' for k,v in checks.items() if not v]
if bad:
 print(f'FAIL: {len(bad)} issue(s)');print('\n'.join(' - '+x for x in bad));sys.exit(1)
print('PASS: checked 2 pages; Tailwind-only, Inter, blue palette, responsive light/dark theme, motion, menus, reveals, FAQ')
print('PASS: local images resolve; Apotek download, purchase links, accessible lightbox keyboard/focus hooks found')
print('PASS: no <style> blocks or style= attributes')

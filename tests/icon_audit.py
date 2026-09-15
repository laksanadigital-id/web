"""Icon audit: visible sprite icons must draw a real box, and brand icons must
use the real brand colours.

Checks http:// (server) and file:// (opened from disk), because external sprite
references are blocked over file://. Run: python tests/icon_audit.py
"""
import functools
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = ('index.html', 'apotek.html')
# Official brand colours for the marks that inherit currentColor.
BRAND_COLORS = {
    'whatsapp': 'rgb(37, 211, 102)',
    'youtube': 'rgb(255, 0, 0)',
    'facebook': 'rgb(24, 119, 242)',
}

CHECK = """
() => [...document.querySelectorAll('svg')]
  .filter(svg => svg.querySelector('use'))
  .map(svg => {
    const box = svg.getBBox();
    return {
      href: (svg.querySelector('use').getAttribute('href') || '').replace('#', ''),
      visible: svg.checkVisibility(),
      blank: box.width === 0 || box.height === 0,
      color: getComputedStyle(svg).color,
    };
  })
"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}'
failures = []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for scheme in ('http', 'file'):
            for name in PAGES:
                url = f'{base}/{name}' if scheme == 'http' else (ROOT / name).as_uri()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000})
                page.goto(url)
                page.wait_for_load_state('load')
                page.wait_for_timeout(400)
                icons = page.evaluate(CHECK)
                visible = [icon for icon in icons if icon['visible']]
                blank = [icon['href'] for icon in visible if icon['blank']]
                wrong = [
                    f"{icon['href']}={icon['color']}"
                    for icon in visible
                    if icon['href'] in BRAND_COLORS and icon['color'] != BRAND_COLORS[icon['href']]
                ]
                marks = sorted({icon['href'] for icon in visible} & set(BRAND_COLORS))
                print(f"{scheme}://{name}: {len(visible)} visible icons, brand marks {marks}")
                if blank:
                    failures.append((scheme, name, 'blank', blank))
                if wrong:
                    failures.append((scheme, name, 'colour', wrong))
                if not marks:
                    failures.append((scheme, name, 'brand icons missing', []))
                page.close()
        browser.close()
finally:
    server.shutdown()
    server.server_close()

if failures:
    for failure in failures:
        print('FAILED', failure)
else:
    print('\nAll icons render over http:// and file://; brand marks use brand colours')
raise SystemExit(1 if failures else 0)

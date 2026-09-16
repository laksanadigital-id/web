"""Browser regression checks. Requires an already-installed Playwright + Chromium.

Run: python tests/browser_smoke.py
Screenshots and JSON results are written to ignored test-results/.
"""
import functools
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'test-results'
OUTPUT.mkdir(exist_ok=True)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{server.server_port}'
results = []


def record(name):
    print(f'PASS: {name}')
    results.append(name)


try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        for filename in ('index.html', 'apotek.html'):
            page.goto(f'{BASE}/{filename}')
            page.wait_for_load_state('networkidle')
            assert page.locator('body').evaluate('(el) => getComputedStyle(el).fontFamily').startswith('Inter')
            # Inter is the only typeface: every role, from headline to footer copy, renders in it.
            page_fonts = page.evaluate("""(filename) => {
                const font = selector => {
                    const element = document.querySelector(selector);
                    return element ? getComputedStyle(element).fontFamily : '';
                };
                const catalog = filename === 'index.html';
                return {
                    hero: font('h1'),
                    appHeadline: catalog ? font('#katalog h3') : font('h1'),
                    supporting: font(catalog ? 'footer h2' : '#features-title'),
                    paragraph: font('main p'),
                    displayLoaded: document.fonts.check('900 40px Inter'),
                    bodyLoaded: document.fonts.check('400 16px Inter'),
                };
            }""", filename)
            for role in ('hero', 'appHeadline', 'supporting', 'paragraph'):
                assert page_fonts[role].startswith('Inter'), (filename, role, page_fonts[role])
            assert page_fonts['displayLoaded'] and page_fonts['bodyLoaded'], (filename, page_fonts)
            record(f'{filename}: every text role renders in Inter')
            for dark in (False, True):
                # Set the motion preference before switching themes so the read below never lands
                # mid-transition (reduced motion disables the theme colour transition).
                page.emulate_media(reduced_motion='reduce')
                page.evaluate('(dark) => document.documentElement.classList.toggle("dark", dark)', dark)
                page.locator('body').evaluate('(el) => el.getAnimations().forEach(animation => animation.finish())')
                contrast = page.evaluate((ROOT / 'tests/contrast.js').read_text(encoding='utf-8'))
                assert not contrast, (filename, dark, contrast)
                record(f'{filename}: {"dark" if dark else "light"} text contrast')
                page.emulate_media(reduced_motion='no-preference')
                for width, height in ((375, 812), (768, 1024), (1024, 768), (1440, 1000), (1920, 1080), (812, 375)):
                    page.set_viewport_size({'width': width, 'height': height})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (filename, width, dark, 'horizontal overflow')
                    assert page.locator('h1').is_visible()
                    assert page.locator('[data-theme-toggle]').is_visible()
                    assert page.locator('img').evaluate_all('(els) => els.filter(el => !el.closest("dialog") && el.loading !== "lazy").every(el => el.complete && el.naturalWidth > 0)')
                    record(f'{filename}: {width}x{height}, {"dark" if dark else "light"}, no overflow')
                page.set_viewport_size({'width': 1440, 'height': 1000})
                page.screenshot(path=str(OUTPUT / f'{filename[:-5]}-{"dark" if dark else "light"}.png'), full_page=True)
            page.set_viewport_size({'width': 1440, 'height': 1000})
            blank_icons = page.evaluate("""() => [...document.querySelectorAll('svg')]
                .filter(svg => svg.querySelector('use') && svg.checkVisibility())
                .filter(svg => { const box = svg.getBBox(); return box.width === 0 || box.height === 0; })
                .map(svg => svg.querySelector('use').getAttribute('href'))""")
            assert not blank_icons, (filename, 'blank icons', blank_icons)
            record(f'{filename}: inline sprite icons render')
            page.set_viewport_size({'width': 375, 'height': 812})
            page.evaluate('document.documentElement.classList.remove("dark")')
            page.screenshot(path=str(OUTPUT / f'{filename[:-5]}-mobile.png'), full_page=True)
            if filename != 'apotek.html':
                continue
            assert not page.locator('#nav-links').is_visible()
            page.set_viewport_size({'width': 1440, 'height': 1000})
            assert page.locator('#nav-links').is_visible()
            for anchor in ('#tampilan', '#fitur', '#spesifikasi', '#informasi'):
                page.locator(f'#nav-links a[href="{anchor}"]').click()
                assert page.url.endswith(anchor), (anchor, page.url)
            record(f'{filename}: section navigation resolves')

        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.goto(f'{BASE}/index.html')
        page.goto(f'{BASE}/index.html')
        cards = page.locator('#katalog > li')
        assert cards.count() >= 1, 'Catalog grid has no product cards'
        assert page.locator('#katalog').is_visible()
        # The catalog page stays a plain grid: no product blocks, no per-app feature list.
        assert page.locator('#katalog li ul').count() == 0, 'Catalog card lists per-app features'
        assert page.locator('[class*="animate-marquee"], #kpi, #peran').count() == 0, 'Catalog page shows product blocks'
        card_link = cards.first.locator('a[href="apotek.html"]').first
        assert card_link.is_visible()
        card_link.click()
        page.wait_for_load_state('networkidle')
        assert page.url.endswith('apotek.html')
        record('Catalog grid lists products and links to the product page')

        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.goto(f'{BASE}/apotek.html')
        page.locator('[data-theme-toggle]').click()
        assert page.locator('html').get_attribute('class').find('dark') >= 0
        page.reload()
        assert page.evaluate('document.documentElement.classList.contains("dark")')
        page.goto(f'{BASE}/index.html')
        assert page.evaluate('document.documentElement.classList.contains("dark")')
        page.locator('[data-theme-toggle]').click()
        record('Theme persists across reloads and pages; accessible toggle')

        page.goto(f'{BASE}/apotek.html')
        categories = page.locator('#fitur section')
        assert categories.count() == 8
        for index in range(8):
            assert categories.nth(index).is_visible()
            assert categories.nth(index).locator('ul li').count() >= 2
        assert page.locator('#spesifikasi dl div').count() == 6
        # Info penting tampil sebagai FAQ yang bisa dibuka-tutup tanpa JavaScript.
        faq = page.locator('#informasi details')
        assert faq.count() == 6
        assert page.locator('#informasi details[open]').count() == 0
        faq.first.locator('summary').click()
        assert faq.first.get_attribute('open') is not None
        faq.first.locator('summary').click()
        assert faq.first.get_attribute('open') is None
        assert page.locator('[data-theme-toggle]').count() == 1
        # Thumbnail tangkapan layar membuka pratinjau di <dialog>; legend di bawah gambar menavigasi
        # ke gambar sebelumnya/berikutnya, dan Esc serta tombol tutup menutup pratinjau.
        shots = page.locator('#tampilan [data-shot-open]')
        assert shots.count() == 8
        modal = page.locator('[data-shot-modal]')
        legend = modal.locator('[data-shot-legend]')
        assert modal.get_attribute('open') is None
        shots.nth(2).click()
        assert modal.get_attribute('open') is not None
        assert modal.locator('img').get_attribute('src').endswith('3.png')
        assert legend.inner_text() == '3 dari 8'
        modal.locator('[data-shot-next]').click()
        assert modal.locator('img').get_attribute('src').endswith('4.png')
        assert legend.inner_text() == '4 dari 8'
        page.keyboard.press('ArrowLeft')
        assert modal.locator('img').get_attribute('src').endswith('3.png')
        assert legend.inner_text() == '3 dari 8'
        page.keyboard.press('Escape')
        assert modal.get_attribute('open') is None
        shots.first.click()
        assert modal.locator('img').get_attribute('src').endswith('1.png')
        modal.locator('[data-shot-prev]').click()
        assert modal.locator('img').get_attribute('src').endswith('8.png')
        assert legend.inner_text() == '8 dari 8'
        page.locator('[data-shot-close]').click()
        assert modal.get_attribute('open') is None
        record('Product details render as feature groups, specs, an expandable FAQ and a shot modal')

        # Creative-level motion and artwork: counters finish, art draws geometry; tanpa fade-in masuk.
        # Harga statis dan tanpa kartu KPI, jadi tidak ada counter di kedua halaman.
        for page_name, expected_counters, expected_marquee in (('index.html', 0, 0), ('apotek.html', 0, 1)):
            page.goto(f'{BASE}/{page_name}')
            page.wait_for_load_state('networkidle')
            page.set_viewport_size({'width': 1440, 'height': 1000})
            assert page.locator('[data-cursor-glow]').is_visible()
            assert page.locator('[class*="animate-marquee"]').count() == expected_marquee
            counters = page.locator('[data-counter]')
            assert counters.count() == expected_counters
            # Both pages stay illustration-free: no mascot, avatar or doodle symbols survive.
            art = page.evaluate("""() => [...document.querySelectorAll('svg use')]
                .map(use => use.getAttribute('href') || '')
                .filter(href => /#(doodle|mascot|avatar)-/.test(href))""")
            assert not art, (page_name, 'character artwork is back', art)
            # Tanpa fade-in masuk: tidak ada hook reveal maupun animasi masuk di kedua halaman.
            assert page.locator('[data-reveal]').count() == 0
            assert page.locator('[class*="animate-rise"]').count() == 0
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_function("""() => [...document.querySelectorAll('[data-counter]')]
                .every(el => Number(el.textContent.replace(/[^0-9]/g, '')) === Number(el.dataset.counter))""")
            record(f'{page_name}: no character artwork, no entrance fade, counters finish')

        page.set_viewport_size({'width': 375, 'height': 812})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.set_viewport_size({'width': 320, 'height': 812})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        record('Product details reflow at 375px and 320px')

        reduced = browser.new_context(reduced_motion='reduce')
        reduced_page = reduced.new_page()
        reduced_page.goto(BASE)
        assert reduced_page.locator('html').evaluate('(el) => getComputedStyle(el).scrollBehavior') == 'auto'
        assert reduced_page.locator('[data-theme-toggle]').evaluate('(el) => getComputedStyle(el).transitionProperty') == 'none'
        record('Reduced-motion scrolling and transitions')
        reduced.close()

        restricted = browser.new_context()
        restricted.add_init_script("Object.defineProperty(window, 'localStorage', {get() { throw new Error('blocked'); }});")
        restricted_page = restricted.new_page()
        restricted_page.goto(BASE)
        restricted_page.locator('[data-theme-toggle]').click()
        assert restricted_page.evaluate('document.documentElement.classList.contains("dark")')
        record('Theme remains usable when localStorage is blocked')
        restricted.close()

        no_js = browser.new_context(java_script_enabled=False, viewport={'width': 375, 'height': 812})
        no_js_page = no_js.new_page()
        no_js_page.goto(f'{BASE}/apotek.html')
        assert no_js_page.locator('#fitur').is_visible()
        assert no_js_page.locator('#spesifikasi').is_visible()
        assert no_js_page.locator('#informasi').is_visible()
        assert no_js_page.locator('#fitur section').count() == 8
        assert 'Rp 450.000' in no_js_page.locator('main').inner_text()
        record('No-JavaScript fallback keeps headline, product list and details')
        no_js.close()
        assert not errors, errors
        record('No uncaught browser JavaScript errors')
        context.close()
        browser.close()
finally:
    server.shutdown()
    server.server_close()
    (OUTPUT / 'browser-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')

print(f'\n{len(results)} checks passed. Artifacts: {OUTPUT}')

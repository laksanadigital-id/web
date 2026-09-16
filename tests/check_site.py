"""Dependency-free structural checks for the static site."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class SiteStructure(unittest.TestCase):
    # Both pages stay list-based: a headline, a product list, and the product details.
    PAGES = ('index.html', 'apotek.html')

    def test_pages(self):
        for filename in self.PAGES:
            with self.subTest(page=filename):
                source = (ROOT / filename).read_text(encoding='utf-8')
                document = Document(source)
                ids = [a['id'] for _, a in document.tags if 'id' in a]
                self.assertEqual(len(ids), len(set(ids)), 'Duplicate IDs')
                self.assertEqual(sum(tag == 'h1' for tag, _ in document.tags), 1)
                self.assertEqual(sum(tag == 'main' for tag, _ in document.tags), 1)
                # Tabel dan panel interaktif tetap di luar: info penting memakai
                # <details>/<summary> dan pratinjau gambar memakai <dialog>, keduanya
                # elemen bawaan browser, bukan akordeon atau lightbox berbasis JavaScript.
                for removed in ('<table', 'data-faq', 'data-feature-panel',
                                'data-gallery-thumb', 'data-lightbox', 'data-demo-download', 'role="tablist"'):
                    self.assertNotIn(removed, source, f'{filename} still ships {removed}')
                self.assertIn('assets/site.css', source)
                self.assertIn('assets/theme.js', source)
                self.assertIn('data-theme-toggle', source)
                self.assertIn('dark:', source)
                self.assertIn('motion-reduce:', source)
                self.assertNotIn('youtube....playlist', source)
                self.assertNotRegex(source, r'\b(?:rounded-[23]xl|text-[3-9]xl|transition-all)\b')
                # Hover tetap datar: hanya warna dan bayangan, tanpa naik atau membesar.
                self.assertNotRegex(source, r'(?<![-\w])hover:(?:-translate-y-[\d.]+|scale-\[[\d.]+\])')
                for tag, attrs in document.tags:
                    self.assertNotIn(tag, ('style', 'select', 'option'))
                    self.assertNotIn('style', attrs)
                    self.assertFalse(any(key.startswith('on') for key in attrs), 'Inline event handler')
                    if tag == 'img':
                        self.assertIn('alt', attrs)
                        self.assertIn('width', attrs)
                        self.assertIn('height', attrs)
                    if attrs.get('target') == '_blank':
                        self.assertIn('noopener', attrs.get('rel', ''))
                    for key in ('aria-controls', 'aria-labelledby', 'aria-describedby'):
                        for target in attrs.get(key, '').split():
                            self.assertIn(target, ids, f'Missing ARIA target {target}')
                    classes = attrs.get('class', '')
                    if 'hover:' in classes:
                        self.assertIn('transition-', classes)
                        self.assertRegex(classes, r'duration-(300|500)')
                    for key in ('src', 'href'):
                        ref = attrs.get(key)
                        if not ref:
                            continue
                        url = urlsplit(ref)
                        if url.scheme or url.netloc:
                            continue
                        if url.path == 'apotek-demo.exe':
                            self.assertIn('data-demo-download', attrs)
                            continue  # Deployment-supplied file has an explicit runtime fallback.
                        target = ROOT / unquote(url.path or filename)
                        self.assertTrue(target.is_file(), f'Missing local asset: {ref}')
                        if url.fragment and target.suffix == '.html':
                            other = Document(target.read_text(encoding='utf-8'))
                            target_ids = [a.get('id') for _, a in other.tags]
                            self.assertIn(url.fragment, target_ids, f'Broken anchor: {ref}')

    def test_catalog_grid(self):
        source = (ROOT / 'index.html').read_text(encoding='utf-8')
        document = Document(source)
        self.assertIn('id="katalog"', source, 'Catalog grid container is missing')
        product_links = {
            a['href'] for tag, a in document.tags
            if tag == 'a' and a.get('href', '').endswith('.html') and '#' not in a['href'] and a['href'] != 'index.html'
        }
        self.assertTrue(product_links, 'Catalog must link to at least one product page')
        for href in product_links:
            self.assertTrue((ROOT / href).is_file(), f'Missing product page: {href}')
        # The catalog card stays a one-liner: no nested list, no per-app feature breakdown.
        card = source[source.index('id="katalog"'):source.index('</ul>', source.index('id="katalog"'))]
        self.assertNotIn('<ul', card, 'Catalog card must not enumerate per-app features')
        # Every card opens with a preview image; without it the grid is just text again.
        cards = re.findall(r'<li\b[^>]*>.*?</li>', card, re.S)
        self.assertTrue(cards, 'Catalog grid has no product cards')
        for item in cards:
            self.assertRegex(item, r'<img\b[^>]*src="images/[^"]+"',
                             'Every catalog card needs an app preview image')
        for detail in ('FEFO', 'FIFO', 'Import/Export', 'Stok opname', 'Cetak struk', 'Point of Sales',
                       'laba rugi', 'arus kas', 'Backup otomatis', 'Fitur dalam aplikasi',
                       'Kelompok fitur', 'Offline penuh', 'Akses jaringan lokal', 'dukungan teknis 30 hari'):
            self.assertNotIn(detail, source, f'Home page leaks per-app detail: {detail}')
        # Product marketing blocks (capability marquee, KPI strip, role cards) belong to the product
        # page; the catalog page stays headline + grid + footer.
        for product_block in ('animate-marquee', 'kpi-title', 'roles-title'):
            self.assertNotIn(product_block, source, f'Home page still ships {product_block}')
        self.assertFalse([name for name in re.findall(r'<use href="#(avatar-[a-z]+)"', source)])
        # Harga tampil sebagai teks statis (tanpa counter-up) dan halaman katalog tetap
        # memakai hook gerak kreatifnya.
        self.assertNotIn('data-counter', source, 'Harga di halaman katalog harus statis')
        # Creative motion hooks that stay on the catalog page (tanpa fade-in masuk).
        for hook in ('data-parallax', 'data-cursor-glow',
                     'animate-gradient-pan', 'animate-pulse-soft'):
            self.assertIn(hook, source)
        # Legacy landing-page sections stay removed: no comparison table, no purchase-funnel block.
        for removed in ('id="perbandingan"', 'id="cara-beli"', 'id="benefit-title"', 'id="stats-title"'):
            self.assertNotIn(removed, source)

    def test_price_is_static(self):
        # Harga ditulis apa adanya: tanpa hitungan naik (counter-up) di kedua halaman.
        for filename in self.PAGES:
            with self.subTest(page=filename):
                source = (ROOT / filename).read_text(encoding='utf-8')
                self.assertIn('Rp 450.000', source)
                self.assertNotIn('data-counter-prefix', source)
                self.assertNotRegex(source, r'<span data-counter="450000"')

    def test_local_tailwind_build(self):
        source = (ROOT / 'assets/tailwind.css').read_text(encoding='utf-8')
        self.assertIn('@import "tailwindcss"', source)
        self.assertIn('@custom-variant dark', source)
        self.assertIn('--font-sans: "Inter"', source)
        self.assertGreater((ROOT / 'assets/site.css').stat().st_size, 5000)

    def test_preserved_product_contract(self):
        source = (ROOT / 'apotek.html').read_text(encoding='utf-8')
        for expected in ('Rp 450.000', 'Windows 10', '4 GB', '100 GB', '30 hari',
                         'FEFO', 'FIFO', 'Import/Export Excel',
                         'lynk.id/nor1c/45w2ryrdxn3p', 'wa.me/',
                         'Backup &amp; restore database'):
            self.assertIn(expected, source)
        # The product page keeps its three plain sections: features, specs, key notes.
        for anchor in ('id="fitur"', 'id="spesifikasi"', 'id="informasi"'):
            self.assertIn(anchor, source)
        # Hero (dengan blok harga di bawah headline), strip marquee, grid tangkapan layar,
        # perincian fitur (8 kelompok modul), spesifikasi, kartu peran, dan FAQ
        # (detail/summary) tetap section biasa.
        self.assertEqual(source.count('<section'), 15)

    def test_no_character_artwork(self):
        # Both pages stay illustration-free: no mascots, role avatars or doodle ornaments.
        for filename in self.PAGES:
            with self.subTest(page=filename):
                source = (ROOT / filename).read_text(encoding='utf-8')
                for removed in ('#doodle-', '#mascot-', '#avatar-', 'animate-spin-slow',
                                'animate-sparkle', 'id="doodle-', 'id="mascot-', 'id="avatar-'):
                    self.assertNotIn(removed, source, f'{filename} still ships {removed}')
                # Whatever still animates keeps a reduced-motion escape hatch.
                for classes in re.findall(r'class="([^"]*\banimate-[^"]*)"', source):
                    moving = [token for token in re.findall(r'[\w:-]*animate-[\w-]+', classes)
                              if not token.startswith('motion-reduce:')]
                    if moving:
                        self.assertIn('motion-reduce:animate-none', classes,
                                      f'{filename}: {moving} without a reduced-motion escape')

    def test_typography_roles(self):
        # Inter is the only typeface on both pages: nothing else is loaded, requested or referenced.
        for filename in self.PAGES:
            with self.subTest(page=filename):
                source = (ROOT / filename).read_text(encoding='utf-8')
                body = re.search(r'<body class="([^"]*)"', source)
                self.assertIn('font-sans', body.group(1), f'{filename}: body must use Inter')
                self.assertNotIn('Fredoka', source, f'{filename}: a second family is still loaded')
                self.assertNotIn('font-display', source, f'{filename}: display-font utility remains')
                self.assertTrue(re.findall(r'<(h[1-4])\b', source), f'{filename}: no headings found')
                link = re.search(r'fonts\.googleapis\.com/css2\?([^"]+)', source)
                self.assertTrue(link, f'{filename}: no webfont request found')
                self.assertEqual(set(re.findall(r'family=([A-Za-z0-9+]+)', link.group(1))), {'Inter'},
                                 f'{filename}: only Inter may be requested')
        theme = (ROOT / 'assets/tailwind.css').read_text(encoding='utf-8')
        self.assertIn('--font-sans: "Inter"', theme)
        self.assertNotIn('--font-display', theme, 'the theme must not define a second family')

    def test_no_entrance_fade_effects(self):
        # Fade-in masuk sudah dihapus di semua halaman: tanpa hook reveal, tanpa animasi rise/pop.
        for filename in self.PAGES:
            with self.subTest(page=filename):
                source = (ROOT / filename).read_text(encoding='utf-8')
                for removed in ('data-reveal', 'animate-rise', 'animate-pop', '[animation-delay:'):
                    self.assertNotIn(removed, source, f'{filename} still ships {removed}')
        theme = (ROOT / 'assets/tailwind.css').read_text(encoding='utf-8')
        for removed in ('--animate-rise', '--animate-pop', '@keyframes rise', '@keyframes pop'):
            self.assertNotIn(removed, theme, f'build theme still ships {removed}')

    def test_shared_script_is_minimal(self):
        script = (ROOT / 'assets/site.js').read_text(encoding='utf-8')
        self.assertIn('nori-theme', script)
        # Counters, parallax, the cursor glow and the screenshot modal stay dependency-free.
        for hook in ('IntersectionObserver', 'data-counter', 'data-shot-modal', 'prefers-reduced-motion'):
            self.assertIn(hook, script)
        self.assertNotIn('data-reveal', script, 'site.js masih memasang reveal fade-in')
        for removed in ('fetch(', 'tabpanel', 'localStorage.setItem("nori-theme", dark'):
            self.assertNotIn(removed, script, f'site.js still ships {removed}')


if __name__ == '__main__':
    unittest.main(verbosity=2)

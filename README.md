# Laksana Digital

Website statis berbahasa Indonesia dengan dua halaman sederhana.

- `index.html`: hanya headline lalu katalog (`#katalog`): satu kartu per aplikasi berisi pratinjau aplikasi (gambar di dalam bingkai jendela, dari `images/<produk>/cover.png`), nama, satu baris deskripsi, harga dengan penanda "sekali bayar", dan satu tombol perincian selebar kartu. Home page tidak memuat apa pun yang spesifik ke satu produk (tidak ada daftar fitur, marquee kemampuan, strip KPI, atau kartu peran); semua itu hanya ada di halaman produk. Dijaga oleh `test_catalog_grid` dan pemeriksaan grid di `tests/browser_smoke.py`. Navigasi header halaman katalog hanya memuat tautan Katalog, tombol konsultasi, dan pemilih tema; tautan ke halaman produk cukup lewat kartu katalog. Tautan "Katalog" dan tombol hero diarahkan ke `#katalog-heading` (pembungkus judul) supaya judul "Katalog aplikasi" tetap terlihat setelah digulir, bukan ke `#katalog` yang menandai grid.
- `apotek.html`: halaman produk Laksana Apotek tanpa breadcrumb: headline dan badge platform, harga, grid 8 tangkapan layar, perincian fitur per bagian kerja, spesifikasi, kartu peran (ikon garis, bukan ilustrasi), dan FAQ "Info penting".

Halaman detail tanpa tab, pencarian, atau lightbox pihak ketiga. Tangkapan layar tampil sebagai grid rapat (2 kolom di ponsel, 3 di tablet, 4 di desktop; semua gambar memakai `loading="lazy"`) dan tiap thumbnail adalah tautan ke berkas gambarnya; dengan JavaScript tautan itu membuka pratinjau ukuran penuh di `<dialog data-shot-modal>` bawaan browser, lengkap dengan legend di bawah gambar (posisi "4 dari 8" plus tombol Sebelumnya/Berikutnya, tombol panah kiri/kanan juga jalan, urutannya memutar); Esc, klik backdrop, atau tombol tutup menutup pratinjau dan fokus balik ke thumbnail. Tanpa JavaScript tautan tersebut membuka gambarnya langsung. Perincian fitur dan spesifikasi tampil sebagai daftar biasa, dan "Info penting" memakai `<details>`/`<summary>` sehingga tetap bisa dibuka-tutup tanpa JavaScript.

Menambah produk baru berarti menambah satu `<li>` di dalam `<ul id="katalog">` pada `index.html`; grid mengatur sendiri jumlah kolomnya (1 kolom di ponsel, 2 di tablet, 3 di desktop).

## Menjalankan lokal

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Buka `http://127.0.0.1:8000`. Gunakan HTTP, bukan `file://`, agar sprite ikon SVG tampil.

CSS hasil build (`assets/site.css`) disertakan. Node.js tidak dibutuhkan untuk melayani website.

## Mengubah tampilan

```sh
npm ci
npm run build
# atau kompilasi otomatis selama pengembangan:
npm run watch
```

- Utility Tailwind langsung di HTML; token font dan varian dark ada di `assets/tailwind.css`.
- Level desain: **frontend level creative** (aturan level normal tetap berlaku sebagai dasar). Satu skema warna aksen: **blue**; netral `slate`. Hal yang wajib dipertahankan saat menyunting:
  - Hero memakai display font Fredoka (`font-display`, bukan Inter) dengan gradient text dan stagger `animate-rise`; teks hero lainnya (paragraf, tombol) tetap Inter.
  - Tanpa ilustrasi karakter: tidak ada maskot, avatar bergaya ilustrasi, atau ornamen doodle di kedua halaman. Ikon hanya diambil dari `assets/icons.svg` (ikon garis fungsional dan logo merek), diwarnai lewat class teks. Dijaga oleh `test_no_character_artwork`.
  - Animasi idle: `animate-float-slow` dan `animate-pulse-soft` untuk latar hero, `animate-gradient-pan` untuk gradien hero, `animate-marquee` hanya di halaman produk. Gerakan masuk section dari hook `data-reveal` (stagger lewat `[transition-delay:...]`), angka dari hook `data-counter` (hook-nya tetap ada di `site.js` untuk dipakai ulang, tetapi saat ini tidak ada elemen yang memakainya setelah kartu ringkasan halaman produk dihapus; harga selalu teks statis, tanpa counter-up), kedalaman dari `data-parallax` dan `data-cursor-glow`.
  - Marquee kemampuan aplikasi (hanya di halaman produk) berhenti saat hover dan saat `prefers-reduced-motion`. Setiap elemen beranimasi wajib punya `motion-reduce:animate-none`.
- JavaScript bersama di `assets/site.js` hanya berisi pemilih tema, efek header saat digulir, reveal `data-reveal`, counter `data-counter`, modal zoom `data-shot-open`/`data-shot-modal`, parallax, dan cursor glow. Inisialisasi tema sebelum render ada di `assets/theme.js`. Tanpa JavaScript semua konten tetap tampil pada nilai akhirnya, dan thumbnail tetap berupa tautan ke berkas gambarnya.
- Tipografi: **Inter untuk semua teks** (`--font-sans`, dipasang di `<body>`). Fredoka (`--font-display`, class `font-display`) hanya dipakai di tiga tempat: headline hero "Beli sekali, PAKAI selamanya", judul "Katalog aplikasi" di halaman katalog, dan headline aplikasi (h1 halaman produk serta h3 nama aplikasi di kartu katalog). Semua heading lain (judul section halaman produk, judul kartu fitur, judul kolom footer) dan `<p>`, `<li>`, `<dd>`, `<dt>` wajib Inter tanpa `font-display`. Harga dan angka statistik memakai Inter dengan `tabular-nums` agar sejajar. Keduanya dimuat dari Google Fonts (Fredoka 500-700, Inter 400-700); `font-black` pada hero di-clamp ke 700 karena sumbu Fredoka berhenti di 700. Dijaga oleh `test_typography_roles` dan pemeriksaan font di `tests/browser_smoke.py`.
- Skala ukuran memakai skala creative (hero sampai `clamp(2.6rem,7vw,4.5rem)`, body 16-18px) karena aturan level creative menggantikan batas skala compact level normal untuk hero dan body.
- Ikon berasal dari `assets/icons.svg` dan diwarnai lewat class teks (mis. `text-[#25d366]` untuk WhatsApp). Logo merek (WhatsApp, Lynk.id, YouTube, TikTok, Facebook) memakai path logo aslinya, bukan ikon garis generik.
- Salinan simbolnya di-inline di awal `<body>` setiap halaman (blok komentar "Icon sprite") supaya `<use>` tetap tampil walau file dibuka langsung lewat `file://`; setelah mengubah `assets/icons.svg`, jalankan `python tests/sync_sprite.py` untuk menyegarkan salinannya.
- Aset merek di `images/`. Logo metode pembayaran ada di `images/payments/` (QRIS, GoPay, BCA dari Wikimedia Commons, public domain; DANA dan ShopeePay dari ikon aplikasi resmi di App Store). Kelimanya tampil sebagai baris chip di section "Pembayaran" pada footer kedua halaman, di atas baris hak cipta.
- Tema awal terang. Pilihan pengguna disimpan sebagai `nori-theme`; tetap berfungsi bila storage browser diblokir.
- Seluruh konten dan navigasi antar-bagian tetap tersedia tanpa JavaScript. Menu bagian header (Tampilan, Fitur, Spesifikasi, Info penting) hanya tampil pada layar sedang ke atas.

## Verifikasi

```sh
npm test
node --check assets/site.js
node --check assets/theme.js
python tests/icon_audit.py
```

Pengujian browser opsional memakai instalasi Python Playwright dan Chromium yang sudah tersedia:

```sh
python tests/browser_smoke.py
```

Pengujian membuka server lokal di port acak dan menutupnya setelah selesai. Screenshot serta hasil JSON ada di `test-results/` (diabaikan Git). Cakupannya: mobile-desktop, light/dark, kontras teks (termasuk teks di atas gradient), overflow horizontal, navigasi antar-bagian, grid katalog yang tetap satu baris tanpa rincian fitur, tema yang bertahan setelah reload, reveal yang bersih, FAQ yang bisa dibuka-tutup, modal zoom tangkapan layar (buka, legend sebelumnya/berikutnya, tombol panah, Esc, tombol tutup), ikon sprite yang tergambar, storage diblokir, fallback tanpa JavaScript, dan tidak ada error JavaScript.

`verify_site.py` yang sudah ada sebelum redesign dibiarkan tanpa perubahan. Skrip tersebut mengecek token implementasi lama seperti CDN Tailwind dan JavaScript inline; gunakan `npm test` untuk arsitektur CSS lokal saat ini.

## Sebelum publikasi

- Kontak WhatsApp mengikuti konten awal: footer dan tombol konsultasi memakai `6281234567890`, sedangkan tombol "Order via WhatsApp" pada halaman apotek memakai `6282112710702`. Kontak footer diberi keterangan "chat saja, tidak menerima telepon", dan kontak email sudah dihapus. Konfirmasikan nomor resmi sebelum publikasi.
- Tautan eksternal (Lynk.id, YouTube, TikTok, Facebook) belum diverifikasi secara live.
- Website memuat Inter (body) dan Fredoka (display) dari Google Fonts. CSS dan JavaScript website dilayani lokal.

Tidak ada perubahan backend, publikasi, atau deployment dalam penyederhanaan ini.

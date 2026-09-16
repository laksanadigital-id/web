# Peta Modul dan Fitur Apotera

Dokumen ini memetakan menu navigasi, route halaman, fitur di dalam halaman, serta fitur lintas aplikasi yang ditemukan pada source code saat dokumentasi dibuat.

## 1. Ringkasan aplikasi

Apotera adalah sistem manajemen apotek berbasis React + Express dengan dukungan desktop Electron dan akses browser LAN. Area fungsional utamanya:

- Dashboard operasional dan ringkasan bisnis.
- Master data obat, satuan, kategori, lokasi/rak, supplier, dokter, pelanggan, karyawan.
- Transaksi penjualan/POS, pembelian, hutang pembelian, retur.
- Persediaan, batch, kartu stok, stok opname, pengingat kadaluarsa.
- Keuangan dan laporan.
- Absensi, shift, dan riwayat uang kasir.
- Manajemen pengguna, role, hak akses, dan multi-apotek.
- Pengaturan tampilan, operasional, nota/cetak, backup/restore, jaringan, dan lisensi.

Semua data bisnis dirancang terisolasi berdasarkan `pharmacy_id` pada backend.

## 2. Aturan akses dan visibilitas

### 2.1 Lapisan akses

- Seluruh area aplikasi setelah login dilindungi autentikasi pengguna.
- Pada mode multi-apotek, pengguna harus melewati login apotek terlebih dahulu.
- Route menggunakan `PermRoute`; pengguna tanpa permission diarahkan kembali ke Dashboard.
- Administrator dikenali melalui permission `all` dan melewati pemeriksaan permission modul.
- Beberapa item menu memakai feature flag, terutama `attendance_feature_enabled`.
- Pengguna non-admin pada Pengaturan hanya melihat tab `Tampilan & Tema`.

### 2.2 Permission utama

| Permission | Cakupan umum |
|---|---|
| `sales` | POS, penjualan, dokter, pelanggan |
| `purchases` | pembelian, supplier, hutang, retur pembelian |
| `medicines` | obat, kategori, satuan, lokasi, pengingat kadaluarsa |
| `stock_opname` | stok opname |
| `cashflow` | transaksi arus kas |
| `attendance` | absensi dan riwayat uang kasir |
| `admin` / `all` | manajemen pengguna, role, karyawan, shift, multi-apotek, pengaturan admin |
| `report_sales` | laporan penjualan dan breakdown penjualan |
| `report_best_seller` | laporan obat paling laris |
| `report_per_medicine` | laporan penjualan per obat |
| `report_low_performance` | laporan obat performa rendah |
| `report_stock_movement` | laporan pergerakan stok dan expired |
| `report_lost_items` | laporan barang hilang |
| `report_profit_loss` | laporan laba rugi |
| `report_revenue` | rekap omzet dan tren pemasukan/pengeluaran |
| `report_hutang` | laporan hutang/cicilan |
| `report_cashflow` | laporan arus kas pada Finance Hub |
| `report_cash_history` | laporan riwayat uang kasir |
| `report_fraud` | laporan deteksi kecurangan |
| `purchase_returns` | route/backend retur pembelian dan tampilan terkait |
| `hutang` | pembayaran hutang pembelian |

Hak `view`, `create`, `delete`, `cancel`, dan `import` diterapkan lebih rinci pada endpoint backend sesuai modul.

## 3. Struktur menu navigasi utama

Menu berikut berasal dari `client/src/config/menuConfig.js`. Item anak dapat disembunyikan berdasarkan permission dan feature flag.

### 3.1 Dashboard

- **Dashboard** — `/`
  - Ringkasan metrik dan grafik bisnis.
  - Ringkasan tren transaksi/pendapatan.
  - Peringatan stok menipis, stok habis, kadaluarsa, dan hutang yang mendekati jatuh tempo.
  - Shortcut menuju data master yang belum lengkap, khususnya supplier dan lokasi/rak.
  - Catatan dashboard yang tersimpan otomatis.
  - Clock-in dan clock-out absensi pengguna.
  - Pemilihan shift aktif bila tersedia.
  - Clock-out dengan nominal uang kas.
  - Pengajuan forgot clock-out dengan tanggal, waktu, alasan, dan bukti.
  - Tautan cepat ke modul transaksi, laporan, dan master sesuai permission.

### 3.2 Transaksi

Grup menu: **Transaksi**.

#### Kasir / POS — `/pos`

- Pencarian obat aktif untuk dimasukkan ke keranjang, mendukung pencarian cepat/hotkey.
- Pengelolaan item keranjang dan kuantitas.
- Pemilihan batch manual atau dispensing otomatis sesuai pengaturan FEFO.
- Pemilihan satuan dan konversi satuan obat.
- Pemilihan pelanggan dan dokter.
- Dukungan transaksi resep dokter.
- Catatan transaksi/pasien.
- Diskon per item dan diskon transaksi dalam mode persentase atau nominal.
- Pajak dengan pilihan tarif dan auto-apply berdasarkan pengaturan.
- Metode pembayaran, nominal tunai, preset uang, dan perhitungan kembalian.
- Validasi stok tidak mencukupi.
- Menahan transaksi untuk dilanjutkan kemudian.
- Membuka, memilih, dan menghapus transaksi tertahan.
- Konfirmasi aksi berisiko, termasuk mengosongkan keranjang.
- Penyelesaian transaksi dan pembuatan struk.
- Cetak struk thermal dengan pilihan ukuran kertas.
- Dukungan fokus pencarian dan shortcut keyboard seperti F2, F6, F7, Ctrl+Enter, dan Ctrl+Delete.

#### Data Penjualan — `/sales`

- Daftar penjualan dengan pencarian, pagination, sorting, dan filter.
- Tab penjualan selesai dan penjualan dibatalkan.
- Ringkasan penjualan berdasarkan filter aktif.
- Detail invoice/nota dan detail item.
- Salin nomor nota/invoice.
- Cetak transaksi/struk melalui detail.
- Pembatalan penjualan dengan alasan, waktu pembatalan, dan nama pelanggan.
- Konfirmasi pembatalan.
- Dukungan pembukaan detail dari laporan dan kartu stok.

#### Data Pembelian — `/purchases`

- Daftar pembelian dengan status, pencarian, filter, sorting, pagination, dan ringkasan.
- Pencatatan pembelian supplier.
- Penambahan item obat dan batch.
- Pemeriksaan duplikasi/keberadaan nomor batch.
- Penerimaan stok pembelian.
- Pembayaran pembelian tunai atau kredit.
- Draft, finalisasi, pembatalan, dan penghapusan pembelian sesuai status.
- Rencana pembelian otomatis berdasarkan kebutuhan stok.
- Detail pembelian dan rincian batch.
- Riwayat penjualan per batch dari detail pembelian.
- Cetak transaksi pembelian dan surat pesanan.
- Salin nomor faktur.

#### Hutang Pembelian — `/hutang`

- Daftar hutang/cicilan pembelian.
- Tab berdasarkan status pembayaran, termasuk aktif dan lunas.
- Indikator hutang jatuh tempo/dekat jatuh tempo.
- Pencarian dan filter supplier, obat, tanggal, status, dan metode pembayaran.
- Detail hutang dan riwayat pembayaran.
- Pencatatan pembayaran hutang sebagian maupun penuh.
- Nominal pembayaran, metode, nomor referensi/bukti, dan catatan.
- Cetak transaksi terkait.

#### Retur Pembelian — `/retur/pembelian`

- Daftar retur pembelian dengan tab status dan jumlah per status.
- Pencarian retur/faktur.
- Pemilihan transaksi pembelian dan item yang dapat diretur.
- Pembuatan retur supplier dengan alasan dan item.
- Pengubahan nominal bila diperlukan.
- Finalisasi, persetujuan, penolakan, pembatalan/penghapusan sesuai status.
- Detail retur.
- Cetak surat retur supplier.
- Salin nomor retur dan nomor faktur.

> **Catatan route:** Backend juga menyediakan retur penjualan, tetapi menu transaksi saat ini hanya menampilkan Retur Pembelian.

### 3.3 Data dan persediaan

Grup menu: **Data**.

#### Data Obat / Produk — `/medicines`

- Daftar obat/produk dengan pencarian, sorting, pagination, dan filter lanjutan.
- Filter kategori, satuan, lokasi/rak, supplier, status aktif, stok, stok jual, harga beli, dan harga jual.
- Tambah, edit, hapus, dan lihat detail obat.
- Data identitas obat, produsen, kategori, lokasi, supplier, satuan, harga, stok, minimum stok, dan status.
- Penanda obat resep dan catatan resep.
- Pengelolaan banyak satuan dan konversi satuan per obat.
- Pengelolaan batch, tanggal kadaluarsa, stok batch, dan harga batch.
- Detail penjualan per batch.
- Kartu stok dengan rentang tanggal.
- Detail transaksi penjualan dan retur yang terkait obat.
- Mode pengurangan stok batch.
- Salin kode dan nama obat.
- Import massal dari Excel dengan panduan, preview, validasi, konfirmasi, dan hasil import.
- Export daftar obat ke Excel.
- Cetak daftar obat.
- Pengaturan kolom cetak.
- Cetak label QR/barcode massal.
- Modal informasi konversi satuan.
- Tambah cepat kategori, lokasi, supplier, dan satuan dari form obat.

#### Stok Opname — `/stock-opname`

- Daftar stok opname dengan pencarian, filter, sorting, dan pagination.
- Pembuatan opname untuk satu atau banyak obat.
- Pencarian obat dan pengisian stok fisik.
- Perhitungan selisih stok sistem dan stok fisik.
- Detail opname.
- Simpan draft dan finalisasi opname.
- Konfirmasi sebelum menyimpan/finalisasi.
- Kartu stok obat dari konteks opname.
- Detail obat dan QR/barcode obat.
- Cetak laporan opname/kartu stok.

#### Pengingat Kadaluarsa — `/expiry-reminder`

- Daftar obat/batch yang akan kadaluarsa atau sudah kadaluarsa.
- Filter rentang waktu kadaluarsa.
- Ringkasan berdasarkan tingkat kedekatan kadaluarsa.
- Detail obat dan batch terkait.
- Cetak daftar pengingat kadaluarsa.

### 3.4 Laporan

Grup menu: **Laporan**. Akses tiap laporan memakai permission laporan masing-masing.

#### Lap. Penjualan — `/reports/sales`

- Laporan penjualan berdasarkan periode.
- Ringkasan dan grafik penjualan.
- Subtab `Utama`.
- Subtab `By Metode Pembayaran`.
- Subtab `By Kategori Obat`.
- Subtab `By Supplier`.
- Subtab `By Hari`.
- Detail invoice dari laporan.
- Filter periode dan filter terkait penjualan.
- Export Excel dan cetak.

#### Lap. Obat Paling Laris — `/reports/best-seller`

- Ranking obat berdasarkan performa penjualan.
- Filter periode.
- Ringkasan/grafik dan detail obat.
- Export dan cetak.

#### Lap. Per Obat — `/reports/sales-by-medicine`

- Analisis penjualan untuk obat tertentu.
- Pencarian/pemilihan obat.
- Kuantitas, omzet, dan rincian transaksi obat.
- Filter periode.
- Detail invoice dan export/cetak.

#### Lap. Obat Performa Rendah — `/reports/low-performance`

- Identifikasi obat dengan performa penjualan rendah.
- Quick filter/periode analisis.
- Detail penjualan obat terpilih.
- Pagination detail penjualan.
- Export dan cetak.

#### Lap. Pergerakan Stok — `/reports/stock-movement`

- Pergerakan stok masuk dan keluar.
- Filter periode dan obat.
- Detail per obat.
- Drill-down ke pembelian, penjualan, dan opname.
- Detail batch dan kuantitas satuan dasar.
- Cetak transaksi pembelian/surat pesanan dari drill-down.
- Export dan cetak laporan.

#### Lap. Barang Hilang — `/reports/lost-items`

- Daftar barang/obat yang terindikasi hilang atau berkurang tidak sesuai.
- Filter tanggal.
- Pagination dan detail terkait.
- Export dan cetak.

#### Lap. Laba & Rugi — `/reports/profit-loss`

- Ringkasan pendapatan, biaya, laba, dan rugi.
- Subtab `Ringkasan`.
- Subtab `Per Transaksi`.
- Filter/navigasi periode bulanan.
- Tren pemasukan vs pengeluaran.
- Rincian transaksi pendapatan dan pengeluaran.
- Link menuju pengelolaan cashflow.
- Detail invoice.
- Export dan cetak.

#### Lap. Rekap Omzet — `/reports/revenue-recap`

- Rekap omzet berdasarkan periode.
- Pengelompokan data berdasarkan pilihan grouping.
- Grafik omzet.
- Ringkasan dan detail.
- Export dan cetak.

#### Lap. Hutang/Cicilan — `/reports/hutang`

- Ringkasan hutang dan cicilan pembelian.
- Filter periode/status sesuai laporan.
- Detail invoice/hutang dan export/cetak.

#### Lap. Deteksi Kecurangan — `/fraud-detection`

- Analisis temuan transaksi/aktivitas yang berpotensi tidak wajar.
- Pengelompokan temuan berdasarkan kategori.
- Jumlah temuan per bagian.
- Filter periode.
- Detail temuan.
- Export/cetak laporan.

### 3.5 Master Data

Grup menu: **Master Data**.

#### Kategori — `/categories`

- CRUD kategori obat.
- Pencarian, sorting, pagination, dan validasi relasi sebelum penghapusan.

#### Satuan — `/units`

- CRUD satuan obat.
- Pencarian, sorting, pagination, dan pemeriksaan pemakaian data.

#### Lokasi / Rak — `/locations`

- CRUD lokasi/rak penyimpanan.
- Pencarian, sorting, pagination, dan pemeriksaan pemakaian data.

#### Supplier — `/suppliers`

- CRUD supplier.
- Data kontak/alamat dan status sesuai field form.
- Pencarian, sorting, pagination, dan pemeriksaan relasi.

#### Dokter — `/doctors`

- CRUD dokter.
- Data nama, spesialisasi, kontak, dan informasi pendukung.
- Pencarian, sorting, pagination, dan pemeriksaan relasi.

#### Pelanggan — `/customers`

- CRUD pelanggan.
- Data identitas, kontak, alamat, NIK, nomor keanggotaan, dokter utama, status, dan catatan.
- Detail pelanggan.
- Riwayat transaksi terakhir.
- Profil medis: alergi, kondisi kronis, obat yang sedang dikonsumsi, golongan darah, dan catatan medis.
- Profil kesehatan terakhir: tekanan darah, gula darah, denyut jantung, suhu, berat, tinggi, BMI, waktu pengukuran, metrik tambahan, dan catatan.
- Riwayat resep.
- Tambah/edit resep dan item resep.
- Relasi obat dan dokter pada resep.
- Pencarian, pagination, edit inline pada detail, dan penghapusan.

### 3.6 Manajemen User

Grup menu: **Manajemen User**. Hanya admin.

#### Manajemen Pengguna — `/users`

- CRUD pengguna.
- Username, nama, role, status aktif, dan data pengguna terkait.
- Reset password pengguna.
- Pengaturan tanggal bergabung.
- Penghapusan pengguna dengan konfirmasi.

#### Manajemen Role — `/roles`

- CRUD role.
- Pengaturan nama/deskripsi role.
- Hak akses granular per modul dan aksi.
- Permission `all` untuk administrator.
- Tampilan ringkas permission dan konfirmasi penghapusan.

#### Data Karyawan — `/employees`

- CRUD data karyawan.
- Data identitas, jabatan, tanggal bergabung, status aktif, dan relasi pengguna.
- Menonaktifkan karyawan.
- Penghapusan dengan konfirmasi.

#### Manajemen Shift — `/shifts`

- CRUD shift.
- Nama shift, jam mulai, jam selesai, dan konfigurasi terkait.
- Tampilan visual dan tampilan tabel.
- Manajemen penugasan shift pada route `/shifts/assignments`.
- CRUD assignment karyawan ke shift.
- Penghapusan assignment dengan konfirmasi.

### 3.7 Pengaturan

Menu: **Pengaturan** — `/settings`.

#### Identitas Apotek

- Nama, kode, alamat, telepon, email, dan identitas apotek.
- Logo apotek dan edit logo.

#### Prefix dan Nota

- Prefix/format nomor transaksi.
- Format nota/invoice.
- Pengaturan isi dan identitas pada nota.

#### Cetak

- Ukuran kertas dan parameter cetak.
- Konfigurasi printer/nota sesuai pengaturan yang dipakai POS, transaksi, dan laporan.

#### Tampilan & Tema

- Tema light, dark, dan sepia.
- Warna utama/palette.
- Font dan skala UI.
- Posisi menu.
- Kepadatan tabel.
- Radius sudut komponen.
- Bayangan kartu.
- Jumlah baris per halaman.
- Preview/penerapan tampilan.

#### Operasional

- Zona waktu dan pengaturan tanggal/waktu aplikasi.
- Pengaturan absensi dan attendance feature.
- Kewajiban uang kas saat clock-out.
- Prompt forgot clock-out.
- Metode dispensing stok batch.
- Pengaturan pajak: feature, tarif, dan auto-apply penjualan.
- Pengaturan operasional lain yang digunakan POS, dashboard, dan transaksi.
- Generate data simulasi/dummy dengan verifikasi password admin.

#### Backup & Data

- Melihat lokasi database.
- Download/export backup database.
- Import database dari backup.
- Peringatan dan konfirmasi sebelum import.
- Reset data awal aplikasi.
- Hapus semua data obat.
- Hapus semua data transaksi.
- Verifikasi password admin untuk operasi destruktif.

#### Jaringan

- Informasi akses jaringan lokal.
- URL akses LAN untuk perangkat lain.
- Salin URL jaringan.
- Konfigurasi/penjelasan penggunaan server LAN.

#### Lisensi

- Informasi lisensi.
- Cek koneksi internet.
- Verifikasi status lisensi.
- Aktivasi license key.
- Lepas/revoke lisensi dengan konfirmasi.
- Informasi status perangkat/licensing.
- Tab lisensi ditampilkan sesuai mode demo dan hak admin.

## 4. Route dan komponen yang tersedia tetapi tidak seluruhnya muncul di menu

### 4.1 Retur Penjualan — komponen tersedia, route aplikasi belum terpasang

File `client/src/pages/ReturPenjualanPage.js` mengimplementasikan:

- Daftar retur penjualan.
- Pencarian nomor retur, invoice, dan pelanggan.
- Detail retur dan item penjualan.
- Pembuatan retur berdasarkan transaksi penjualan.
- Pengisian nama pelanggan dan alasan retur.
- Konfirmasi proses retur.
- Pemulihan stok seluruh item transaksi.
- Pengubahan status penjualan menjadi `Diretur` tanpa menghapus data penjualan.

Backend juga memiliki endpoint `/returns/sale`. Namun pada `client/src/App.js` komponen ini belum di-import dan belum memiliki route `retur/penjualan`; item tersebut juga belum ada di `menuConfig.js`. Dengan kondisi source saat ini, fitur ini belum dapat diakses melalui navigasi/route React standar.

### 4.2 Data Karyawan — route tersedia, menu belum tercantum

`/employees` terdaftar di `App.js` dan dilindungi admin, tetapi belum menjadi child pada grup `Manajemen User` di `menuConfig.js`. Fitur tetap tersedia melalui route langsung atau bila ditautkan dari area lain.

### 4.3 Pharmacy Selector — komponen tersedia, route belum terpasang

`client/src/pages/PharmacySelectorPage.js` ada di source, tetapi tidak ditemukan pada konfigurasi route `App.js`. Mode multi-apotek saat ini menggunakan `PharmacyLoginPage` dan `PharmaciesPage`.

### 4.4 Route laporan generik

`/reports` dan `/reports/:tabSection` tersedia sebagai route generik. Tab yang valid ditentukan oleh `ReportsPage` berdasarkan permission. `/reports/finance-hub` mengarah ke halaman Finance Hub khusus.

## 5. Fitur lintas aplikasi

### Autentikasi dan sesi

- Login pengguna dengan username/password.
- Logout.
- Verifikasi password untuk operasi sensitif.
- Token JWT dan pemeriksaan pengguna aktif.
- Preferensi pengguna.
- Login apotek pada mode multi-apotek.
- Redirect otomatis saat sesi tidak valid atau permission tidak cukup.

### Setup awal apotek

- Health/startup check.
- Setup wizard untuk apotek baru.
- Pemeriksaan status konfigurasi awal.
- Peringatan bila master supplier/lokasi belum tersedia.
- Pembuatan data awal dan opsi penambahan data awal.

### Desktop dan startup

- Electron wrapper.
- Server backend sebagai child process.
- Pemeriksaan kesehatan server sebelum membuka aplikasi.
- Splash/loading screen opsional.
- Error boundary React.
- Error log modal yang dapat dibuka melalui shortcut Electron F3.
- Auto-restart server Electron ketika child process berhenti.

### UI/UX umum

- Tema light/dark/sepia.
- Layout responsif desktop dan mobile.
- Sidebar/top navigation/bottom navigation.
- Modal, dialog konfirmasi, toast, badge, tabel responsif, pagination, filter modal, dan date input.
- Sorting, pencarian, filter aktif, refresh, dan pagination pada banyak halaman.
- Salin nomor invoice/kode/nama melalui clipboard.
- Format mata uang IDR dan tanggal Indonesia.

### Cetak dan export

- Cetak thermal receipt.
- Cetak dokumen transaksi.
- Cetak surat pesanan dan surat retur.
- Cetak kartu stok, stok opname, laporan, dan label QR/barcode.
- Pengaturan ukuran kertas dan layout cetak.
- Export Excel pada obat, cashflow, laporan, dan area yang mendukungnya.

### Demo dan lisensi

- Demo mode dengan pembatasan jumlah record.
- Modal pemberitahuan batas demo.
- Konfigurasi kredensial demo pada mode debug.
- Aktivasi, verifikasi, status, dan revoke lisensi.
- Pemeriksaan ketidaksesuaian perangkat lisensi.

## 6. Daftar route React saat ini

| Route | Komponen | Akses/ketentuan |
|---|---|---|
| `/pharmacy-login` | `PharmacyLoginPage` | Login apotek multi-apotek |
| `/login` | `LoginPage` | Login pengguna setelah guard apotek |
| `/` | `Dashboard` | Pengguna terautentikasi |
| `/medicines` | `MedicinesPage` | permission `medicines` |
| `/categories` | `CategoriesPage` | permission `medicines` |
| `/units` | `UnitsPage` | permission `medicines` |
| `/locations` | `RacksPage` | permission `medicines` |
| `/suppliers` | `SuppliersPage` | permission `purchases` |
| `/doctors` | `DoctorsPage` | permission `sales` |
| `/customers` | `CustomersPage` | permission `sales` |
| `/employees` | `EmployeesPage` | admin |
| `/sales` | `SalesPage` | permission `sales` |
| `/pos` | `POSPage` | permission `sales` |
| `/purchases` | `PurchasesPage` | permission `purchases` |
| `/hutang` | `HutangPage` | permission `purchases` |
| `/retur/pembelian` | `ReturPembelianPage` | permission `purchases` pada route |
| `/stock-opname` | `StockOpnamePage` | permission `stock_opname` |
| `/expiry-reminder` | `ExpiryReminderPage` | permission `medicines` |
| `/cashflow` | `CashflowPage` | permission `cashflow` |
| `/reports` | `ReportsPage` | tab laporan ditentukan permission |
| `/reports/finance-hub` | `FinanceHubPage` | tab laporan ditentukan permission |
| `/reports/:tabSection` | `ReportsPage` | tab laporan ditentukan permission |
| `/attendance` | `AttendancePage` | permission `attendance` dan feature flag |
| `/cash-history` | `CashHistoryPage` | route memakai permission `attendance` |
| `/fraud-detection` | `FraudDetectionPage` | halaman route tersedia; tab menu memakai `report_fraud` |
| `/shifts` | `ShiftsPage` | admin dan feature flag pada menu |
| `/shifts/assignments` | `ShiftsPage` | admin dan feature flag pada menu |
| `/settings` | `SettingsPage` | pengguna login; tab admin dibatasi |
| `/users` | `UsersPage` | admin |
| `/roles` | `RolesPage` | admin |
| `/pharmacies` | `PharmaciesPage` | admin |

## 7. Catatan pemeliharaan dokumentasi

- Sumber utama menu: `client/src/config/menuConfig.js`.
- Sumber utama route: `client/src/App.js`.
- Detail perilaku UI: masing-masing file `client/src/pages/*.js`.
- Detail kontrak API/backend: `server/src/routes/*.js`.
- Saat menambah menu atau route baru, perbarui bagian struktur menu, daftar route, permission, dan fitur internal pada dokumen ini.
- Item yang sengaja tidak terlihat di menu sebaiknya diberi keterangan seperti bagian 4 agar tidak disalahartikan sebagai fitur yang tidak ada.

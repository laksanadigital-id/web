#!/usr/bin/env node
// Salin berkas statis ke public/ supaya Vercel punya direktori output yang eksplisit.
// Sumbernya tetap di root repo, sesuai layout yang dipakai tests/ dan server lokal.
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const output = path.join(root, 'public');
const pages = fs.readdirSync(root).filter(name => name.endsWith('.html'));
const directories = ['assets', 'images'];
const entries = [...pages, ...directories];

if (!pages.length) {
  console.error('build-public: tidak ada berkas .html di root repo');
  process.exit(1);
}

fs.rmSync(output, { recursive: true, force: true });
fs.mkdirSync(output, { recursive: true });

for (const entry of entries) {
  const source = path.join(root, entry);
  if (!fs.existsSync(source)) {
    console.error(`build-public: ${entry} tidak ditemukan di ${root}`);
    process.exit(1);
  }
  fs.cpSync(source, path.join(output, entry), { recursive: true });
}

console.log(`build-public: ${pages.join(', ')} dan ${directories.join(', ')} disalin ke public/`);

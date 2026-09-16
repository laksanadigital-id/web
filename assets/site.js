(() => {
  'use strict';

  const root = document.documentElement;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const wideViewport = window.matchMedia('(min-width: 768px)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');

  const themeButtons = document.querySelectorAll('[data-theme-toggle]');
  function updateThemeButtons() {
    const dark = root.classList.contains('dark');
    themeButtons.forEach(button => {
      button.setAttribute('aria-pressed', String(dark));
      button.setAttribute('aria-label', dark ? 'Aktifkan tema terang' : 'Aktifkan tema gelap');
      button.title = dark ? 'Tema terang' : 'Tema gelap';
    });
  }
  themeButtons.forEach(button => button.addEventListener('click', () => {
    const dark = root.classList.toggle('dark');
    try {
      localStorage.setItem('nori-theme', dark ? 'dark' : 'light');
    } catch {
      // The current theme still works when browser storage is unavailable.
    }
    updateThemeButtons();
  }));
  window.addEventListener('storage', event => {
    if (event.key !== 'nori-theme' && event.key !== null) return;
    root.classList.toggle('dark', event.newValue === 'dark');
    updateThemeButtons();
  });
  updateThemeButtons();

  // Header turns from transparent glass into a stronger, shadowed surface after scrolling.
  const header = document.querySelector('[data-header]');
  if (header) {
    let headerFrame = false;
    function syncHeader() {
      headerFrame = false;
      header.toggleAttribute('data-scrolled', window.scrollY > 8);
    }
    syncHeader();
    window.addEventListener('scroll', () => {
      if (headerFrame) return;
      headerFrame = true;
      window.requestAnimationFrame(syncHeader);
    }, { passive: true });
  }

  // Figures in the markup are final; JavaScript only replays them from zero for storytelling.
  const counterFormat = new Intl.NumberFormat('id-ID');
  document.querySelectorAll('[data-counter]').forEach(counter => {
    const target = Number(counter.dataset.counter);
    if (!Number.isFinite(target)) return;
    const prefix = counter.dataset.counterPrefix || '';
    const suffix = counter.dataset.counterSuffix || '';
    function render(value) {
      counter.textContent = `${prefix}${counterFormat.format(Math.round(value))}${suffix}`;
    }
    function count() {
      const start = performance.now();
      const duration = 2200;
      function step(now) {
        const progress = Math.min((now - start) / duration, 1);
        render(target * (1 - (1 - progress) ** 4));
        if (progress < 1) window.requestAnimationFrame(step);
      }
      window.requestAnimationFrame(step);
    }
    if (reduceMotion.matches) {
      render(target);
    } else if ('IntersectionObserver' in window) {
      const counterObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          count();
          observer.unobserve(entry.target);
        });
      }, { threshold: 0.4 });
      counterObserver.observe(counter);
    } else {
      count();
    }
  });

  // Zoom tangkapan layar: setiap thumbnail tetap tautan ke berkas gambarnya, jadi tanpa JavaScript
  // gambarnya tetap bisa dibuka. Dengan JavaScript, <dialog> bawaan browser yang membuka pratinjau:
  // Esc, focus trap, dan backdrop gratis dari elemennya. Script hanya menyambung buka, tutup, dan
  // navigasi antar gambar (tombol di legend maupun tombol panah kiri/kanan).
  const shotModal = document.querySelector('[data-shot-modal]');
  if (shotModal) {
    const shotView = shotModal.querySelector('img');
    const shotLegend = shotModal.querySelector('[data-shot-legend]');
    const shots = [...document.querySelectorAll('[data-shot-open]')];
    let shotIndex = 0;
    function showShot(index) {
      if (!shots.length) return;
      shotIndex = (index + shots.length) % shots.length;
      const thumbnail = shots[shotIndex].querySelector('img');
      if (!thumbnail) return;
      shotView.src = thumbnail.currentSrc || thumbnail.src;
      shotView.alt = thumbnail.alt;
      if (shotLegend) shotLegend.textContent = `${shotIndex + 1} dari ${shots.length}`;
    }
    function closeShotModal() {
      shotModal.close();
    }
    shots.forEach((trigger, index) => trigger.addEventListener('click', event => {
      event.preventDefault();
      showShot(index);
      shotModal.showModal();
    }));
    const shotPrev = shotModal.querySelector('[data-shot-prev]');
    const shotNext = shotModal.querySelector('[data-shot-next]');
    const shotClose = shotModal.querySelector('[data-shot-close]');
    if (shotPrev) shotPrev.addEventListener('click', () => showShot(shotIndex - 1));
    if (shotNext) shotNext.addEventListener('click', () => showShot(shotIndex + 1));
    if (shotClose) shotClose.addEventListener('click', closeShotModal);
    shotModal.addEventListener('keydown', event => {
      if (event.key === 'ArrowLeft') showShot(shotIndex - 1);
      else if (event.key === 'ArrowRight') showShot(shotIndex + 1);
      else return;
      event.preventDefault();
    });
    // Klik di luar kotak gambar menutup pratinjau; klik pada gambar tidak.
    shotModal.addEventListener('click', event => {
      const box = shotModal.getBoundingClientRect();
      const outside = event.clientX < box.left || event.clientX > box.right
        || event.clientY < box.top || event.clientY > box.bottom;
      if (outside) closeShotModal();
    });
  }

  if (reduceMotion.matches) return;

  // Parallax and cursor glow: the runtime only feeds scroll/pointer values into custom properties,
  // while every visual rule stays in the Tailwind classes.
  const parallax = [...document.querySelectorAll('[data-parallax]')];
  const cursorGlow = document.querySelector('[data-cursor-glow]');
  if (parallax.length && wideViewport.matches) {
    let scrollFrame = false;
    function applyScroll() {
      scrollFrame = false;
      root.style.setProperty('--scroll', String(Math.round(window.scrollY)));
    }
    applyScroll();
    window.addEventListener('scroll', () => {
      if (scrollFrame) return;
      scrollFrame = true;
      window.requestAnimationFrame(applyScroll);
    }, { passive: true });
    window.addEventListener('resize', applyScroll, { passive: true });
  }
  if (cursorGlow && finePointer.matches && wideViewport.matches) {
    let pointerFrame = false;
    let pointerX = 0;
    let pointerY = 0;
    window.addEventListener('pointermove', event => {
      pointerX = event.clientX;
      pointerY = event.clientY;
      if (pointerFrame) return;
      pointerFrame = true;
      window.requestAnimationFrame(() => {
        pointerFrame = false;
        root.style.setProperty('--cx', `${pointerX}px`);
        root.style.setProperty('--cy', `${pointerY}px`);
      });
    }, { passive: true });
  }
})();

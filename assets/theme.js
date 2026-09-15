(() => {
  let theme = 'light';
  try {
    theme = localStorage.getItem('nori-theme') === 'dark' ? 'dark' : 'light';
  } catch {
    // Storage may be unavailable in private or restricted browsing contexts.
  }
  document.documentElement.classList.toggle('dark', theme === 'dark');
})();

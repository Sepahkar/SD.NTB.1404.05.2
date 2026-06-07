'use strict';

(function () {
  const STORAGE_KEY = 'ay-admin-theme';
  const DEFAULT = 'dark';

  function getTheme() {
    try {
      const v = localStorage.getItem(STORAGE_KEY);
      if (v === 'light' || v === 'dark') return v;
    } catch (e) { /* ignore */ }
    return DEFAULT;
  }

  function applyTheme(theme) {
    const mode = theme === 'light' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', mode);
    try {
      localStorage.setItem(STORAGE_KEY, mode);
      localStorage.setItem('theme', mode);
    } catch (e) { /* ignore */ }
    document.querySelectorAll('[data-ay-theme-toggle]').forEach((btn) => {
      const label = btn.querySelector('.ay-theme-toggle__text');
      const icon = btn.querySelector('.ay-theme-toggle__icon');
      if (label) label.textContent = mode === 'dark' ? 'تم روشن' : 'تم تیره';
      if (icon) icon.textContent = mode === 'dark' ? '☀' : '☽';
      btn.setAttribute('aria-label', mode === 'dark' ? 'تغییر به تم روشن' : 'تغییر به تم تیره');
    });
  }

  function toggle() {
    const cur = document.documentElement.getAttribute('data-theme') || getTheme();
    applyTheme(cur === 'dark' ? 'light' : 'dark');
  }

  applyTheme(getTheme());

  function bind() {
    document.querySelectorAll('[data-ay-theme-toggle]').forEach((btn) => {
      btn.addEventListener('click', toggle);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();

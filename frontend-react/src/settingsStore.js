const THEME_KEY = 'arm_theme';

export function loadTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  return stored === 'dark' ? 'dark' : 'light';
}

export function saveTheme(theme) {
  const next = theme === 'dark' ? 'dark' : 'light';
  localStorage.setItem(THEME_KEY, next);
  return next;
}

export function applyTheme(theme) {
  const next = theme === 'dark' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
}

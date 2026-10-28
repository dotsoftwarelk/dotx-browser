/* Optional preference: no tracking and no dependency on remote resources. */
(() => {
  const picker = document.getElementById('theme-picker');
  if (!picker) return;
  let saved = 'system';
  try { saved = localStorage.getItem('dotx-theme') || 'system'; } catch (_) { /* private storage unavailable */ }
  if (!['system', 'light', 'dark'].includes(saved)) saved = 'system';
  const apply = (value) => {
    if (value === 'system') delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = value;
    picker.value = value;
  };
  apply(saved);
  picker.parentElement.hidden = false;
  picker.addEventListener('change', () => {
    const value = ['system', 'light', 'dark'].includes(picker.value) ? picker.value : 'system';
    apply(value);
    try { localStorage.setItem('dotx-theme', value); } catch (_) { /* selection remains for this page */ }
  });
})();

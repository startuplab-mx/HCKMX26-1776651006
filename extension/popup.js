// Popup: read hit count from chrome.storage and offer a reset.
const hitsEl = document.getElementById('hits');
const statusEl = document.getElementById('status');

function render(hits) {
  if (hitsEl) hitsEl.textContent = String(Number(hits) || 0);
  if (statusEl) statusEl.textContent = 'Activo';
}

if (chrome?.storage?.local) {
  chrome.storage.local.get(['hits'], ({ hits }) => render(hits));
  chrome.storage.onChanged?.addListener((changes, area) => {
    if (area === 'local' && 'hits' in changes) render(changes.hits.newValue);
  });
} else {
  render(0);
}

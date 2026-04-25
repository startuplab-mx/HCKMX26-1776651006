// Popup logic — reads chrome.storage.local for hits, last detection,
// and the global pause flag. All updates live-render via storage events.

const BOT_PHONE = '5218445387404';

const els = {
  hits:   document.getElementById('hits'),
  status: document.getElementById('status'),
  last:   document.getElementById('last-block'),
  phase:  document.getElementById('last-phase'),
  when:   document.getElementById('last-when'),
  snip:   document.getElementById('last-snip'),
  toggle: document.getElementById('toggle'),
  reset:  document.getElementById('reset'),
  openBot: document.getElementById('open-bot'),
};

function timeAgo(ts) {
  if (!ts) return '—';
  const s = Math.floor((Date.now() - Number(ts)) / 1000);
  if (s < 60) return `hace ${s}s`;
  if (s < 3600) return `hace ${Math.floor(s / 60)} min`;
  if (s < 86400) return `hace ${Math.floor(s / 3600)} h`;
  return new Date(Number(ts)).toLocaleString();
}

function render(state) {
  const hits = Number(state.hits) || 0;
  const paused = !!state.paused;
  const last = state.lastHit || null;

  if (els.hits) els.hits.textContent = String(hits);
  if (els.status) els.status.textContent = paused ? 'Pausado' : 'Activo';
  if (els.toggle) {
    els.toggle.classList.toggle('on', paused);
    els.toggle.setAttribute('aria-checked', String(paused));
  }
  if (els.last) {
    if (last && last.phase) {
      els.last.style.display = 'block';
      els.phase.textContent = last.phase === 'coercion' ? 'Coerción' : 'Explotación';
      els.when.textContent  = timeAgo(last.at);
      els.snip.textContent  = (last.snippet || '').slice(0, 110) + ((last.snippet || '').length > 110 ? '…' : '');
    } else {
      els.last.style.display = 'none';
    }
  }
  // Reflect badge on the icon for at-a-glance.
  if (chrome?.action?.setBadgeText) {
    chrome.action.setBadgeText({ text: hits ? String(hits) : '' });
    chrome.action.setBadgeBackgroundColor({ color: paused ? '#666' : '#EF4444' });
  }
}

function loadAndRender() {
  if (!chrome?.storage?.local) return render({ hits: 0 });
  chrome.storage.local.get(['hits', 'paused', 'lastHit', 'lastHitAt'], (s) => render(s || {}));
}

loadAndRender();
chrome.storage?.onChanged?.addListener((_changes, area) => {
  if (area === 'local') loadAndRender();
});

// ------- Controls -------

if (els.toggle) {
  const flip = () => {
    chrome.storage.local.get(['paused'], ({ paused }) => {
      chrome.storage.local.set({ paused: !paused });
    });
  };
  els.toggle.addEventListener('click', flip);
  els.toggle.addEventListener('keydown', (e) => {
    if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); flip(); }
  });
}

if (els.reset) {
  els.reset.addEventListener('click', () => {
    chrome.storage.local.set({ hits: 0, lastHit: null, lastHitAt: null });
  });
}

if (els.openBot) {
  els.openBot.addEventListener('click', () => {
    const url = `https://wa.me/${BOT_PHONE}?text=${encodeURIComponent('Hola Nahual, quiero analizar un mensaje sospechoso.')}`;
    chrome.tabs?.create?.({ url });
  });
}

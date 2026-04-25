// Nahual Shield — content script.
// Local zero-trust detection: mini-regex over DOM mutations. When a Phase 3 or
// Phase 4 pattern fires, show a single overlay and persist the hit count to
// chrome.storage so the popup can read it. No network I/O.

const PHASE3_REGEX = [
  /si intentas escapar te (descuartizo|matamos)/i,
  /sabemos d(o|ó)nde vives/i,
  /ya estás (adentro|marcado)/i,
  /(levant(o|ó)n|tronar|dar piso|darte piso)/i,
  /si te vas te (matamos|tronamos|damos piso)/i,
];

const PHASE4_REGEX = [
  /(manda|env(í|i)a) (fotos|videos|nudes|pack)/i,
  /(deposita|transfiere) \$?\s?\d+/i,
  /si no pagas (las|tus) (fotos|nudes|videos)/i,
  /(las|tus) (fotos|nudes) (van|las mando) a/i,
  /no traigas celular/i,
];

const COOLDOWN_MS = 5 * 60 * 1000;
const SEEN_NODES = new WeakSet();
const seenHashes = new Map();
let overlayOpen = false;

function flagText(text) {
  for (const r of PHASE3_REGEX) if (r.test(text)) return 'coercion';
  for (const r of PHASE4_REGEX) if (r.test(text)) return 'explotacion';
  return null;
}

function hash32(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h + str.charCodeAt(i)) | 0;
  }
  return h.toString(16);
}

function alreadySeenRecently(text) {
  const key = hash32(text.slice(0, 200));
  const now = Date.now();
  const last = seenHashes.get(key);
  if (last && now - last < COOLDOWN_MS) return true;
  seenHashes.set(key, now);
  return false;
}

function bumpHits() {
  if (!chrome?.storage?.local) return;
  chrome.storage.local.get(['hits'], ({ hits }) => {
    const n = (Number(hits) || 0) + 1;
    chrome.storage.local.set({ hits: n, lastHitAt: Date.now() });
  });
}

function showOverlay(phase, snippet) {
  if (overlayOpen) return;
  overlayOpen = true;
  const overlay = document.createElement('div');
  overlay.id = 'nahual-overlay';
  overlay.innerHTML = `
    <div class="nahual-card" role="dialog" aria-label="Alerta Nahual">
      <div class="nahual-header">🛡️ Nahual Shield</div>
      <div class="nahual-body">
        <p><strong>Detectamos un patrón de ${phase === 'coercion' ? 'COERCIÓN' : 'EXPLOTACIÓN'}.</strong></p>
        <p>Esto puede ser reclutamiento criminal o sextorsión. No estás solo/a.</p>
        <p class="nahual-snippet">"${snippet.slice(0, 140)}…"</p>
      </div>
      <div class="nahual-actions">
        <a class="nahual-btn primary" href="https://wa.me/?text=${encodeURIComponent('Hola Nahual, recibí un mensaje sospechoso')}" target="_blank" rel="noopener">Reportar al bot</a>
        <button class="nahual-btn secondary" id="nahual-close">Cerrar</button>
      </div>
      <div class="nahual-footer">Policía Cibernética: <strong>088</strong> · SIPINNA</div>
    </div>
  `;
  document.body.appendChild(overlay);
  document.getElementById('nahual-close').addEventListener('click', () => {
    overlay.remove();
    overlayOpen = false;
  });
  bumpHits();
}

function scanNode(node) {
  if (!node || SEEN_NODES.has(node)) return;
  if (node.nodeType === Node.TEXT_NODE) {
    SEEN_NODES.add(node);
    const text = (node.textContent || '').trim();
    if (text.length < 8) return;
    const phase = flagText(text);
    if (phase && !alreadySeenRecently(text)) showOverlay(phase, text);
  } else if (node.nodeType === Node.ELEMENT_NODE) {
    SEEN_NODES.add(node);
    for (const child of node.childNodes) scanNode(child);
  }
}

const observer = new MutationObserver((mutations) => {
  for (const m of mutations) {
    for (const node of m.addedNodes) scanNode(node);
  }
});

observer.observe(document.body, { childList: true, subtree: true });
// Initial sweep so patterns already visible on load are caught too.
for (const child of document.body.childNodes) scanNode(child);

console.log('[Nahual Shield] active on', location.hostname);

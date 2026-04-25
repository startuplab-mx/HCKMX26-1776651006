// Nahual Shield — content script.
// Local zero-trust detection: mini-regex over DOM mutations. When a Phase 3 or
// Phase 4 pattern fires, show a single overlay and persist the hit count to
// chrome.storage so the popup can read it. No network I/O.

// Per-platform DOM hints. The MutationObserver below scans the whole body
// regardless, but the platform config is exposed so popups / future code
// can know which site is active and adjust UX (e.g. a "Roblox detected"
// banner). Keeping it data-only keeps the runtime trivial.
const PLATFORMS = [
  {
    name: 'whatsapp',
    matches: (host) => host.includes('whatsapp'),
    chatSelector: '#main .copyable-text',
    messageSelector: '.message-in .copyable-text span',
    containerSelector: '#main',
  },
  {
    name: 'instagram',
    matches: (host) => host.includes('instagram'),
    chatSelector: '[role="main"]',
    messageSelector: 'div[dir="auto"]',
    containerSelector: '[role="main"]',
  },
  {
    name: 'discord',
    matches: (host) => host.includes('discord'),
    chatSelector: '[class*="chatContent"]',
    messageSelector: '[id^="message-content"]',
    containerSelector: '[class*="chatContent"]',
  },
  {
    name: 'roblox',
    matches: (host) => host.includes('roblox'),
    chatSelector: '.chat-container, [class*="ChatWindow"], [class*="chat-window"]',
    messageSelector: '.chat-message-content, [class*="message-content"]',
    containerSelector: '.chat-container, [class*="ChatWindow"], [class*="chat-window"]',
  },
];

function detectPlatform() {
  const host = window.location.hostname;
  return PLATFORMS.find((p) => p.matches(host)) || null;
}

const ACTIVE_PLATFORM = detectPlatform();

// Phase 3 (Coerción) — direct threats received. The extension scans messages
// the user is *receiving* in chat, so both aggressor-speech ("te voy a
// matar") and 1st-person reception ("me van a matar") need coverage in
// case the user pastes/quotes the threat in a screenshot description.
const PHASE3_REGEX = [
  // Aggressor speech (typical incoming WhatsApp/Insta/Discord DM)
  /te (voy|vamos) a (matar|tronar|levantar|desaparecer|dar piso)/i,
  /si intentas escapar te (descuartizo|matamos)/i,
  /si te (vas|rajas) te (matamos|tronamos|damos piso|encontramos)/i,
  /sabemos d(o|ó)nde (vives|estudias|trabajas)/i,
  /ya estás (adentro|marcado|en la lista)/i,
  /(levant(o|ó)n|te tronamos|te damos piso|te ponemos en bolsa)/i,
  /(última|ultima) oportunidad/i,
  /ya sabes demasiado/i,
  /te va a pesar/i,
  // Reception (user pasted/forwarded the threat into chat)
  /me (van|iban) a (matar|tronar|levantar|desaparecer|dar piso|chingar)/i,
  /me amenaz(aron|an) (de muerte|con matarme)/i,
  /si no (respondo|contesto|voy|pago) me van a/i,
];

// Phase 4 (Explotación) — operative orders, sextortion, money requests.
const PHASE4_REGEX = [
  // Sextortion classics
  /(manda|env(í|i)a|m(á|a)ndame) (fotos|videos|nudes|pack)/i,
  /(deposita|transfiere|p(á|a)same) \$?\s?\d+/i,
  /si no pagas (las|tus) (fotos|nudes|videos)/i,
  /(las|tus) (fotos|nudes) (van|las mando) a/i,
  // Narco-recruitment operative orders
  /no traigas celular/i,
  /(ve|venga|trae) armado/i,
  /tienes que (levantar|ejecutar|cargar piedra)/i,
  /trae (la coca|la mota|las grapitas|la merca|la mercanc(í|i)a)/i,
  /vas a (vender en el punto|halconear)/i,
  /tienes que (dar piso|tronar)/i,
  // Platform-pivot + grooming traps (Roblox / Discord / IG)
  /(gift\s?card|tarjeta de regalo|robux gratis)/i,
  /(p(á|a)sate a|pasamos a|m(é|e)tete a) (discord|wpp|whatsapp|telegram|signal)/i,
  /(p(á|a)same|d(á|a)me) tu (user(name)?|cuenta|tag)/i,
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

// Defensive HTML escape — the snippet may come from any DOM node on the
// host page (potentially an attacker-controlled chat message). The
// overlay used to inline the raw text via template literal, which would
// execute markup. Escaping the five XSS-relevant characters keeps the
// overlay rendering as plain text.
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  })[c]);
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

function bumpHits(phase, snippet) {
  if (!chrome?.storage?.local) return;
  chrome.storage.local.get(['hits'], ({ hits }) => {
    const n = (Number(hits) || 0) + 1;
    const lastHit = {
      phase,
      snippet: String(snippet || '').slice(0, 200),
      at: Date.now(),
      host: location.hostname,
    };
    chrome.storage.local.set({ hits: n, lastHit, lastHitAt: lastHit.at });
  });
}

// Pause flag: when popup toggles `paused`, content scripts stop showing
// overlays. We cache the value in memory + listen for changes.
let PAUSED = false;
if (chrome?.storage?.local) {
  chrome.storage.local.get(['paused'], ({ paused }) => { PAUSED = !!paused; });
  chrome.storage.onChanged?.addListener((c, area) => {
    if (area === 'local' && 'paused' in c) PAUSED = !!c.paused.newValue;
  });
}

// Bot phone number — used to build the wa.me deep link so the "Reportar al
// bot" button opens a chat directly with the Nahual bot instead of an empty
// WhatsApp dialog. Format: country code + national number, no '+', no spaces.
// 5218445387404 = +52 1 844 538 7404 (Mexican mobile JID).
const BOT_PHONE = '5218445387404';

function showOverlay(phase, snippet) {
  if (overlayOpen || PAUSED) return;
  overlayOpen = true;
  const overlay = document.createElement('div');
  overlay.id = 'nahual-overlay';
  const greeting =
    phase === 'coercion'
      ? 'Hola Nahual, recibí un mensaje con señales de coerción/amenaza. ¿Me ayudas?'
      : 'Hola Nahual, recibí un mensaje con señales de explotación/sextorsión. ¿Me ayudas?';
  const waLink = `https://wa.me/${BOT_PHONE}?text=${encodeURIComponent(greeting)}`;
  overlay.innerHTML = `
    <div class="nahual-card" role="dialog" aria-label="Alerta Nahual">
      <div class="nahual-header">🛡️ Nahual Shield</div>
      <div class="nahual-body">
        <p><strong>Detectamos un patrón de ${phase === 'coercion' ? 'COERCIÓN' : 'EXPLOTACIÓN'}.</strong></p>
        <p>Esto puede ser reclutamiento criminal o sextorsión. No estás solo/a.</p>
        <p class="nahual-snippet">"${escapeHtml(snippet.slice(0, 140))}…"</p>
      </div>
      <div class="nahual-actions">
        <a class="nahual-btn primary" href="${waLink}" target="_blank" rel="noopener">Reportar al bot</a>
        <button class="nahual-btn secondary" id="nahual-close">Cerrar</button>
      </div>
      <div class="nahual-footer">Policía Cibernética: <strong>088</strong> · SIPINNA</div>
    </div>
  `;
  document.body.appendChild(overlay);
  const closeOverlay = () => {
    if (!overlay.isConnected) return;
    overlay.remove();
    overlayOpen = false;
    document.removeEventListener('keydown', onKeydown);
  };
  const onKeydown = (e) => { if (e.key === 'Escape') closeOverlay(); };
  document.getElementById('nahual-close').addEventListener('click', closeOverlay);
  document.addEventListener('keydown', onKeydown);
  // Auto-dismiss after 30s so the overlay never sticks forever if the user
  // walks away. Still less aggressive than a typical toast (8s) because the
  // user might be reading the snippet carefully.
  setTimeout(closeOverlay, 30000);
  bumpHits(phase, snippet);
}

// Tags whose textContent is never user-visible chat — we MUST skip them or
// the scanner ends up reading Instagram's React/GraphQL JSON payloads,
// stylesheets, etc. and showing those as "the snippet" in the overlay.
// (Caught live during testing on instagram.com/direct.)
const SKIP_TAGS = new Set([
  'SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE',
  'META', 'LINK', 'TITLE', 'HEAD',
  'IFRAME', 'OBJECT', 'EMBED',
  'CODE', 'PRE', // dev tools / docs / paste-inspect surfaces
]);

function scanNode(node) {
  if (!node || SEEN_NODES.has(node)) return;
  if (node.nodeType === Node.TEXT_NODE) {
    SEEN_NODES.add(node);
    // Climb to the parent element to check the host tag — text nodes inside
    // <script> tags will silently match patterns from JSON payloads otherwise.
    const parent = node.parentNode;
    if (parent && parent.nodeType === Node.ELEMENT_NODE && SKIP_TAGS.has(parent.tagName)) {
      return;
    }
    const text = (node.textContent || '').trim();
    if (text.length < 8 || text.length > 2000) return; // skip empty + huge JSON blobs
    const phase = flagText(text);
    if (phase && !alreadySeenRecently(text)) showOverlay(phase, text);
  } else if (node.nodeType === Node.ELEMENT_NODE) {
    SEEN_NODES.add(node);
    if (SKIP_TAGS.has(node.tagName)) return; // bail before recursing into <script>
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

// Privacy by design: no console output that reveals the extension is running.
// (Earlier versions logged the active platform, which let host pages detect
// the shield via console.* hooks. The popup UI is the only signal now.)

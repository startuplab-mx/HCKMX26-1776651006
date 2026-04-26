// Nahual Shield — content script.
// Local zero-trust detection: mini-regex over DOM mutations. When a Phase 3 or
// Phase 4 pattern fires, show a single overlay and persist the hit count to
// chrome.storage so the popup can read it. No network I/O.

// Per-platform DOM hints. The MutationObserver below scans the whole body
// regardless, but the platform config is exposed so popups / future code
// can know which site is active and adjust UX (e.g. a "Roblox detected"
// banner). Keeping it data-only keeps the runtime trivial.
// Platform configs informed by the user's existing extractors at
// C:\Users\arma2\Codigo\{discord,wa,ig}-chat-extractor — selectors verified
// to point at actual chat content (vs page chrome / store pages / nav menus).
const PLATFORMS = [
  {
    name: 'whatsapp',
    matches: (host) => host.includes('whatsapp'),
    // The chat panel's main container in WA Web. Only scan here.
    containerSelectors: ['#main', '[data-testid="conversation-panel-messages"]'],
    // We want only inbound messages; WA marks them with .message-in.
    messageSelectors: ['.message-in', '.copyable-text'],
    // URLs that should NEVER fire (settings, help, etc).
    urlBlocklist: [/\/help\//, /\/about\//],
  },
  {
    name: 'instagram',
    matches: (host) => host.includes('instagram'),
    // /direct/ is the only place chat lives on IG.
    urlAllowlist: [/\/direct\//],
    containerSelectors: ['[role="main"] section[role="dialog"]', '[role="main"]'],
    messageSelectors: ['div[role="row"]', 'div[dir="auto"]'],
  },
  {
    name: 'discord',
    matches: (host) => host.includes('discord'),
    // Verified against Codigo/discord-chat-extractor: messages live inside
    // ol[class*="scrollerInner"] and individual messages are
    // li[id^="chat-messages-"]. The text node we want is
    // [id^="message-content-"].
    containerSelectors: ['ol[class*="scrollerInner"]'],
    messageSelectors: ['li[id^="chat-messages-"]', '[id^="message-content-"]'],
    // Only fire on actual channel paths, not friends/library/settings/store.
    urlAllowlist: [/\/channels\//],
    urlBlocklist: [
      /\/store\b/, /\/library\b/, /\/discovery\b/, /\/shop\b/, /\/settings\b/,
    ],
  },
  {
    name: 'roblox',
    matches: (host) => host.includes('roblox'),
    // Roblox chat selectors. Avoiding the catalog/store text body which
    // contains words like "Gift Card" in product titles (false positive
    // surfaced by Armando Apr 25).
    containerSelectors: [
      '.chat-window', '[class*="ChatWindow"]', '[class*="chat-window"]',
      '.message-row', '[data-testid="chat"]',
    ],
    messageSelectors: ['.message-row', '[class*="MessageContainer"]'],
    // These paths are pure store/marketplace/profile and should NEVER
    // trigger the shield even if they have phrases like "gift card".
    urlBlocklist: [
      /\/catalog\b/, /\/marketplace\b/, /\/upgrades?\b/, /\/redeem\b/,
      /\/giftcards?\b/, /\/charity\b/, /\/users?\/\d+\b/, /\/develop\b/,
      /\/communities\b/, /\/groups\b/, /\/games\/\d+\b/,  // game pages, not in-game chat
      /\/home\b/, /\/discover\b/, /\/avatar\b/,
    ],
  },
];

function detectPlatform() {
  const host = window.location.hostname;
  return PLATFORMS.find((p) => p.matches(host)) || null;
}

function urlMatchesAny(patterns) {
  if (!patterns || !patterns.length) return false;
  const path = window.location.pathname;
  return patterns.some((re) => re.test(path));
}

function platformActive(platform) {
  if (!platform) return false;
  if (urlMatchesAny(platform.urlBlocklist)) return false;
  if (platform.urlAllowlist && !urlMatchesAny(platform.urlAllowlist)) return false;
  return true;
}

function findChatContainers(platform) {
  if (!platform || !platform.containerSelectors) return [];
  const found = [];
  for (const sel of platform.containerSelectors) {
    document.querySelectorAll(sel).forEach((el) => found.push(el));
  }
  return found;
}

function nodeIsInsideChat(node, containers) {
  if (!containers.length) return false;
  for (const c of containers) {
    if (c.contains(node)) return true;
  }
  return false;
}

const ACTIVE_PLATFORM = detectPlatform();
// Re-evaluated on every scan because SPA navigation (React Router) doesn't
// re-inject content scripts. Without this, navigating from /channels to
// /store on Discord, or from a game chat to /giftcards on Roblox, kept
// the scanner active in the wrong context (Armando caught the Roblox
// gift-card-store false positive Apr 25 ~15:17).
function platformIsActive() {
  return platformActive(ACTIVE_PLATFORM);
}

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
  // Platform-pivot + grooming traps (Roblox / Discord / IG).
  // CRITICAL: these patterns require a VERB OF PROPOSITION before the
  // grooming term, otherwise the Roblox catalog page text "Buy Giftcards"
  // / "Robux Gift Card" matches as a false positive (caught Apr 25 by
  // Armando in the catalog page).
  /(te\s+(paso|regalo|doy|mando|env[ií]o)|tengo|consigues?)\s+(\$\d+|\d+\s*robux|robux|gift\s?card|tarjeta\s+de\s+regalo)/i,
  /(robux\s+gratis|robux\s+free)\s+(si|por|a\s+cambio)/i,
  /(p(á|a)sate a|pasamos a|m(é|e)tete a|vamos a)\s+(discord|wpp|whatsapp|telegram|signal|snapchat)/i,
  /(p(á|a)same|d(á|a)me)\s+tu\s+(user(name)?|cuenta|tag|@|user|n[uú]mero)/i,
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
  // Build the snippet block with explicit truncation hint when the
  // original is longer than 140 chars — otherwise users may dismiss
  // a real threat thinking the visible text is the whole message.
  const snippetTrimmed = snippet.slice(0, 140);
  const snippetHtml = snippet.length > 140
    ? `<p class="nahual-snippet">"${escapeHtml(snippetTrimmed)}<strong>…</strong>"</p>
       <p class="nahual-snippet-note">Primeros 140 de ${snippet.length} caracteres.</p>`
    : `<p class="nahual-snippet">"${escapeHtml(snippetTrimmed)}"</p>`;

  overlay.innerHTML = `
    <div class="nahual-card" role="dialog" aria-label="Alerta Nahual">
      <div class="nahual-header">🛡️ Nahual Shield</div>
      <div class="nahual-body">
        <p><strong>Detectamos un patrón de ${phase === 'coercion' ? 'COERCIÓN' : 'EXPLOTACIÓN'}.</strong></p>
        <p>Esto puede ser reclutamiento criminal o sextorsión. No estás solo/a.</p>
        ${snippetHtml}
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

// Whitelist patterns: phrases that look risky out of context but are
// legitimate UI / store / catalog text. If text contains ANY of these, skip.
const WHITELIST_REGEX = [
  // Roblox / gift card store UX text
  /(comprar|buy)\s+(gift\s?card|tarjeta\s+de\s+regalo)/i,
  /robux\s+(gift\s?card|tarjeta\s+de\s+regalo|membership|membres[ií]a)/i,
  /(canjear|redeem)\s+(gift\s?card|tarjeta|c[oó]digo)/i,
  /tarjeta\s+de\s+regalo\s+de\s+\$?\d/i,
  // Generic UI chrome
  /(cookies|t[eé]rminos|condiciones|pol[ií]tica\s+de\s+privacidad)/i,
  /(iniciar\s+sesi[oó]n|crear\s+cuenta|sign\s+up|log\s+in)\s*$/i,
  // Discord store / nitro upsell
  /(discord\s+nitro|boost\s+this\s+server|server\s+boost)/i,
  // News / educational mentions of crime ("noticia: matan a..." in news feed)
  /(noticias?|nota|reportaje|art[ií]culo)[:\s]/i,
];

function isWhitelisted(text) {
  for (const r of WHITELIST_REGEX) if (r.test(text)) return true;
  return false;
}

// Containers cache — refreshed lazily because chat panels mount/unmount.
let CHAT_CONTAINERS = [];
let CONTAINERS_LAST_REFRESH = 0;
function getChatContainers() {
  const now = Date.now();
  if (now - CONTAINERS_LAST_REFRESH > 1500) {
    CHAT_CONTAINERS = findChatContainers(ACTIVE_PLATFORM);
    CONTAINERS_LAST_REFRESH = now;
  }
  return CHAT_CONTAINERS;
}

function scanNode(node) {
  if (!platformIsActive()) return; // whole site is on the URL blocklist
  if (!node || SEEN_NODES.has(node)) return;
  if (node.nodeType === Node.TEXT_NODE) {
    SEEN_NODES.add(node);
    // Climb to the parent element to check the host tag — text nodes inside
    // <script> tags will silently match patterns from JSON payloads otherwise.
    const parent = node.parentNode;
    if (parent && parent.nodeType === Node.ELEMENT_NODE && SKIP_TAGS.has(parent.tagName)) {
      return;
    }
    // Scope: only fire if this text node lives inside a known chat container.
    // Falls back to "scan everything" only when no container has mounted yet
    // — necessary for WhatsApp Web where chat is the entire viewport.
    const containers = getChatContainers();
    if (containers.length && parent && !nodeIsInsideChat(parent, containers)) {
      return;
    }
    const text = (node.textContent || '').trim();
    if (text.length < 8 || text.length > 2000) return;
    if (isWhitelisted(text)) return;
    const phase = flagText(text);
    if (phase && !alreadySeenRecently(text)) showOverlay(phase, text);
  } else if (node.nodeType === Node.ELEMENT_NODE) {
    SEEN_NODES.add(node);
    if (SKIP_TAGS.has(node.tagName)) return;
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

// React-heavy chat clients (Discord, IG) mount the conversation pane AFTER
// our content script runs, AND swap it on URL navigation without reloading.
// We keep watching forever (cheap querySelector) so chat re-renders are
// always covered. If the page is on a non-chat URL, platformIsActive()
// gates the actual overlay — the watcher just keeps the container cache
// fresh.
let _lastUrl = location.href;
setInterval(() => {
  // SPA URL change: clear container cache so the next scanNode re-detects.
  if (location.href !== _lastUrl) {
    _lastUrl = location.href;
    CHAT_CONTAINERS = [];
    CONTAINERS_LAST_REFRESH = 0;
  }
  if (!platformIsActive()) return;
  const containers = findChatContainers(ACTIVE_PLATFORM);
  if (containers.length) {
    const newOnes = containers.filter((c) => !CHAT_CONTAINERS.includes(c));
    CHAT_CONTAINERS = containers;
    CONTAINERS_LAST_REFRESH = Date.now();
    // Sweep only newly-mounted containers — avoids re-scanning everything
    // every second.
    newOnes.forEach((c) => {
      for (const child of c.childNodes) scanNode(child);
    });
  }
}, 1500);

// Privacy by design: no console output that reveals the extension is running.
// (Earlier versions logged the active platform, which let host pages detect
// the shield via console.* hooks. The popup UI is the only signal now.)

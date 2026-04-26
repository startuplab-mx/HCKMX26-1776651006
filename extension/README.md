# 🛡️ Nahual Shield (Chrome Extension)

Extensión Chrome **Manifest V3 v1.3.0** que monitorea WhatsApp Web,
Instagram, Discord y Roblox para detectar señales de Coerción o
Explotación en tiempo real.

## Cómo funciona

```
DOM mutations → MutationObserver → scanNode (text nodes)
  ↓
  • urlAllowlist / urlBlocklist (per platform)
  • container scope (solo dentro del chat container)
  • SKIP_TAGS (script, style, noscript, etc.)
  • WHITELIST_REGEX (UI / store / catalog)
  ↓
  flagText() → PHASE3_REGEX (12) | PHASE4_REGEX (14)
  ↓
  showOverlay()
    ├── snippet (escapeHtml)
    ├── botón "Reportar al bot" → wa.me/5218445387404
    ├── botón "Cerrar" (+ ESC + auto-dismiss 30s)
    └── bumpHits() → chrome.storage.local
```

## Plataformas soportadas

| Plataforma | URL allow | URL block (FP) |
|---|---|---|
| **WhatsApp Web** | `web.whatsapp.com/*` | — |
| **Instagram** | `/direct/*` | — |
| **Discord** | `/channels/*` | `/store`, `/library`, `/discovery`, `/shop`, `/settings` |
| **Roblox** | (todo excepto store) | `/catalog`, `/marketplace`, `/upgrades`, `/redeem`, `/giftcards`, `/charity`, `/avatar`, `/games/<id>`, `/home`, `/discover` |

## Instalación

1. `chrome://extensions/`
2. Activá **Modo de desarrollador** (toggle arriba derecha)
3. **Cargar descomprimida** → seleccionar `extension/`
4. Anclar el ícono con el alfiler 📌

## Pruebas

### Manual
1. Abre WhatsApp Web (o web.whatsapp.com directo, sin escanear QR)
2. F12 → Console
3. ```js
   const el = document.createElement('div');
   el.textContent = 'te voy a matar si te rajas, sabemos donde vives';
   document.body.appendChild(el);
   ```
4. El overlay rojo aparece al instante.

### Patrones que disparan

| Phase 3 — Coerción | Phase 4 — Explotación |
|---|---|
| `te voy/vamos a matar/tronar/levantar/dar piso` | `manda fotos/nudes/pack` |
| `me van a matar` (víctima) | `deposita $XXX` |
| `me amenazaron de muerte` | `si no pagas las fotos van a tu escuela` |
| `si te rajas te matamos` | `ve armado` |
| `sabemos dónde vives/estudias` | `tienes que levantar a alguien` |
| `ya estás adentro/marcado` | `trae la coca/mota/grapitas` |
| `ya sabes demasiado` | `vas a halconear` |
| `última oportunidad` | `gift card / robux gratis` (con verbo de propuesta) |
| `te va a pesar` | `pásate a Discord/Telegram, pásame tu user` |

26 regex en total. Whitelist de 5 frases UI/store que NO disparan
("Buy Roblox Gift Cards", cookies, terms, news headlines).

## Popup (v1.2)

- **Estado:** Activo / Pausado (toggle)
- **Detecciones esta sesión:** contador
- **Plataformas:** WA · IG · Discord · Roblox
- **Última detección:** fase + tiempo relativo + snippet (truncado)
- **Botón "Abrir bot":** wa.me deeplink con saludo pre-rellenado
- **Botón "Resetear contador":** zeros + lastHit
- **Badge en ícono:** count rojo (activo) / gris (paused)

## Privacy by design

- **NO envía nada al backend** hasta que el usuario haga click en
  "Reportar al bot"
- Los hits se almacenan en `chrome.storage.local` (no nubes)
- ESC + auto-dismiss 30s (overlay no se queda fijo)
- Toda la detección es local, sin red

## Configuración

`content.js`:
- `BOT_PHONE = "5218445387404"` (formato JID México sin +)
- `COOLDOWN_MS = 5 * 60 * 1000` (5 min entre overlays del mismo texto)

## Hardening reciente

- **SPA navigation:** `platformIsActive()` re-evalúa la URL en cada scan
  (Roblox/Discord cambian de página sin re-inyectar content script)
- **Mount watcher:** corre indefinidamente, detecta cambio de `location.href`
- **Container scope:** solo escanea dentro del `containerSelectors` —
  evita el bug del JSON de React de Instagram que mostraba data raw en
  el overlay
- **Verb-of-proposition** en Phase 4: `te paso 5 mil robux si` fira;
  `Buy Roblox Gift Cards` (catálogo) no
- **HTTPS only:** matches usan `https://` (no `*://`) tras audit de
  seguridad

## Source

`extension/content.js` — todo en un solo archivo con MutationObserver
+ regexes + overlay UI. ~250 líneas.

Ver [README.md raíz](../README.md) para arquitectura completa.

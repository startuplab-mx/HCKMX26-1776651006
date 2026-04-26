# 📋 NAHUAL — CHANGELOG

Cronología de la sesión de hardening + deploy a producción
(25 abril 2026, ~12:00 → 18:00 CST).

## [v1.4.0] — Apr 25 evening · "4-layer cognitive classifier"

Después del cierre de v1.3 surgió un análisis estructural que reveló
3 gaps fundamentales: dataset perspectiva-agresor, LLM solo en zona
gris, sin normalización chat MX. Se implementaron 7 capas de
corrección + un clasificador Bayesiano completo.

### Highlights v1.4

* **CAPA A — LLM activation extendida** (`pipeline.py`): además de la
  zona gris (0.3-0.6), el LLM ahora activa cuando score=0 + texto>30
  chars, o cuando score<0.3 + keywords de dinero/trabajo/amenaza.
  Cuando heur=0 y LLM activa, peso 100% LLM (no merge con 0).
* **CAPA C — `_normalize_advanced`** (`heuristic.py`): chat MX
  abbreviations (x→por, q→que, pa→para, toy→estoy, xq→porque),
  números escritos (quince mil → 15000), formato dinero
  (15 mil → 15000, $15.000 → $15000), typos (ofresieron → ofrecieron).
* **CAPAS B+D+E — +102 patrones**:
  - phase1: +34 (victim offers, money no-$, social DM hooks)
  - phase2: +17 (PII pulls recibidos, cambio canal, secrecía)
  - phase3: +31 (received threats, conditional, distress, vigilancia)
  - phase4: +20 (forced ops, sextortion victim, deepfake CSAM, recruit-pares)
  - 5 universal money regexes for $-less formats
* **CAPA F — Whitelist expandida**: trabajo legítimo, dinero casual,
  videojuegos, series, noticias, memes, escuela. +33 entradas/fase.
* **CAPA G — `_contextual_boost`**: 1.30× para 3+ categorías distintas,
  1.50× para danger combos (`{oferta_economica, perfilamiento}`,
  `{amenaza, orden_directa}`, `{sextorsion_recibida, sextorsion_chantaje}`).
* **CAPA 1.5 — Bayesiano** (`bayesian.py`): Naive Bayes incremental
  con n-gramas (1,2,3), Laplace smoothing, persistencia JSON atómica,
  RLock thread-safe. 911 docs entrenados (836 patrones + 75 safe),
  vocab 5701. 0 dependencias nuevas. Aprende de cada feedback.
  - Endpoints: `GET /bayesian/stats`, `POST /bayesian/predict`
  - Auto-feed: `confirm` → train(fase), `deny` → train("seguro")
  - 9 tests nuevos en `test_bayesian.py` (cold start, train, predict,
    persist, endpoints, pipeline integration)

### Resultados v1.4

* **Dataset**: 768 → 870 patrones (+102, 460 high-confidence)
* **Pytest**: 147 → 156 tests (+9 bayesian)
* **Score comparison** structural verification suite (sin LLM):
  - Antes: 16/20 (80%)
  - Después: **20/20 (100%)** ← bayesiano rescata 4 falsos negativos
* **Self-feed**: 192 frases candidatas curadas de Infobae/Proceso/etc;
  91 testeadas en producción; 8 false negatives PRE-deploy ahora son
  ATENCION/PELIGRO post-deploy.

### Commits v1.4

```
d5eb140  TRACK 1 + TRACK 2 deliverables: self-feed CSV + bayesian deployed
20b5607  polish: bootstrap safe phrases + score_comparison harness
a8da2bb  feat(bayesian): Capa 1.5 — Naive Bayes incremental classifier
60eae46  structural-fix: 7-layer classifier overhaul (CAPAS A-G)
```

---

## [v1.3.0] — Apr 25, 2026 · "production-hardened"

Sistema desplegado en producción (`159.223.187.6`), 768 patrones, 21 commits
de polish, 147 tests pytest verde, todos los endpoints públicos verificados
end-to-end.

### Estado live al cierre

```
Backend   active   FastAPI + uvicorn :8000
Bot       active   Baileys WhatsApp +52 844 538 7404
Nginx     active   reverse proxy + panel + rate limit + security headers
Health    all_ok   DB ✓ Anthropic 4.5 ✓ Groq Whisper ✓
Dataset   768 patrones, 433 high-conf, 14 emojis
Tests     147/147
```

---

## Highlights por capa

### 🤖 Bot WhatsApp (Baileys)

- **`fetchLatestBaileysVersion()`** al boot — Baileys 6.7.21 cacheaba una
  versión de protocolo deprecada por WhatsApp; el handshake fallaba en
  loop. (`430b1d0`)
- **QR persistente como PNG** en `/opt/nahual/panel/bot-qr.png` —
  escanear desde un browser en lugar de leer el journal por SSH;
  auto-borra cuando `connection === 'open'`. (`16e6d04`)
- **X-API-Key header en axios** — sin esto `/sessions/*` retornaba 403
  silenciosamente y el FSM perdía estado entre restarts. (`c5b8ca8`)
- **JID normalization para México** — `+52 844 538 7404` debe convertirse
  a `5218445387404` (`52` + `1` mobile + 10 dígitos), no `528445387404`
  como el código original hacía. Más `sock.onWhatsApp()` para verificar
  existencia antes de enviar. PDF se adjunta al guardián, no solo texto.
  (`11eaec8`)
- **Reconnect con exponential backoff** — antes era recursión sin throttle
  (riesgo de ban WhatsApp por flood). 0.5s × 2^n, max 60s, ±25% jitter,
  con cleanup de listeners viejos. (`7acabee`)
- **SIGTERM/SIGINT handler** — antes systemd esperaba 90s en cada restart;
  ahora cierra en 1.5s. (`7acabee`)
- **Per-JID rate limit** (5 alertas / 60s sliding window) y **session
  TTL eviction** (drop entries idle > 7d). (`1561400`)
- **Comandos universales**: `menu`, `ayuda`, `privacidad`, `estado`,
  `reset`, `reporte` — funcionan en cualquier estado del FSM. (`2933897`)
- **Cierres conversacionales** — `gracias`, `ok`, `bye`, `no`, `no gracias`,
  `estoy bien`, `nada más`... → respuesta empática + reset, sin /analyze.
  Tres variantes de respuesta random. (`8ba2046`, `ee89db2`)
- **Distress detection** — `tengo miedo`, `necesito ayuda`, `me quiero
  morir` → empatía + Línea de la Vida + 088, sin interrogar. (`d8b4f2f`)
- **Mensaje al guardián reescrito** — empático, 4 pasos accionables,
  recursos, "no respondas, soy bot". (`cbb690b`)
- **Validación de región** — rechaza preguntas/garbage como "Hola cuantos
  años tienes?" que se había colado en `by_region`. (`1d5ed2d`)
- **No re-greeting bug** — bot reenviaba bienvenida cada vez que el FSM
  volvía a `inicio`; ahora solo greeting explícito o primer turno.
  (`8ba2046`)

### 🔌 Extensión Chrome (Manifest V3 v1.3.0)

- **Selectores corregidos** — basados en los extractores reales del
  usuario en `C:\Users\arma2\Codigo\{discord,wa,ig}-chat-extractor`.
  Discord ahora usa `ol[class*="scrollerInner"]` + `li[id^="chat-messages-"]`.
  WhatsApp `#main`. IG `section[role="dialog"]`. (`ee89db2`)
- **`https://discord.com/*` agregado al manifest** — antes solo
  `*.discord.com` que no incluye el apex. (`ee89db2`)
- **Per-platform URL allow/block lists** — Roblox bloquea `/catalog`,
  `/giftcards`, `/marketplace`, `/upgrades`, `/charity`, `/redeem`,
  `/avatar`, `/games/<id>`. Discord allow `/channels/`. (`8ba2046`)
- **SPA navigation handling** — `platformIsActive()` se re-evalúa en cada
  scan; mount watcher track `location.href` y limpia container cache
  cuando cambia. Sin esto, navegar de chat a `/giftcards` mantenía el
  scanner activo. (`ee89db2`)
- **Whitelist regex** — frases que se ven sospechosas fuera de contexto
  (gift cards en catálogo, news headlines, terms of service) NO
  disparan overlay. (`8ba2046`)
- **Phase 4 regex requiere verbo-de-propuesta** — `te paso 10000 robux si`
  fira; `Buy Roblox Gift Cards` (catálogo) NO. (`ee89db2`)
- **Skip `<script>/<style>/<noscript>`** — el observer matcheaba JSON de
  React de Instagram, mostrando JSON crudo en el snippet del overlay.
  (`afef156`)
- **Deep link al bot** — el botón "Reportar al bot" ahora apunta a
  `wa.me/5218445387404?text=...` con saludo pre-rellenado. Antes era
  `wa.me/?text=...` (sin teléfono → diálogo vacío). (`21f11f2`)
- **popup.html v1.2** — última detección visible (fase + tiempo +
  snippet), toggle pause, "Abrir bot", "Resetear contador". (`2933897`)
- **Badge counter** en el ícono (rojo activo / gris paused). (`2933897`)
- **ESC cierra overlay** + auto-dismiss 30s. (`2933897`)

### 🐍 Backend (FastAPI)

- **Modelo Anthropic actualizado** — `claude-sonnet-4-20250514` (deprecado)
  → `claude-sonnet-4-5-20250929`. Sin esto OCR retornaba 502 y la zona
  gris LLM no funcionaba. (`8ba2046`)
- **MIME normalization** — `audio/ogg; codecs=opus` y `image/jpeg;charset=binary`
  ahora se aceptan; antes el set check estricto retornaba 415.
  Ampliada `ALLOWED_AUDIO_MIME` (aac/flac) e `ALLOWED_IMAGE_MIME`
  (heic/heif iPhone). (`8ba2046`)
- **`/admin/version`** — git commit + branch + commit_at + python (lee
  `.git/` directo, sin shellear). (`2933897`)
- **`/admin/dataset-info`** — counts per fase + histograma de pesos +
  emoji count + tuner overlay size. Lee del clasificador en memoria. (`2933897`)
- **`/admin/metrics`** — middleware `@app.middleware("http")` que cuenta
  requests por endpoint. (`2933897`)
- **`/admin/healthcheck-deep`** — pings live a DB + Anthropic + Groq con
  timeout per-check. (`913356f`)
- **`/alerts.csv`** — export Excel UTF-8-BOM con 14 columnas. (`e4a5106`)
- **SQLite retry on lock** — `_LockedConn._execute_with_retry` con
  5 intentos + backoff (0.05/0.1/0.2/0.4/0.8s) en `OperationalError("locked")`. (`7acabee`)
- **Webhook retry budget** — 3 intentos con backoff (1s/2s/4s) en
  5xx/network. 4xx never retries. (`913356f`)
- **Error logging visible** — `pipeline.classify` ya no swallow silencioso
  en feedback save. (`913356f`)
- **Dataset expandido** — 643 → 768 patrones via `scripts/add_audit_patterns.py`:
  - +106 audit-round-1 (sextorsión, Roblox grooming, jerga lana/billete/feria,
    cartel jerga halcón/puchador/punto/estaca, recepción víctima)
    (`7acabee`)
  - +19 final critical sextortion/distress (`fe77ae2`)
  - +76 reception perspective + money-without-$ (`32c7c21`)
- **6 tests nuevos** en `tests/test_admin.py`. Total: 141 → 147. (`e4a5106`)

### 🎨 Panel web

- **🧪 Probar el clasificador en vivo** — textarea + 4 botones de ejemplo,
  Cmd/Ctrl+Enter shortcut. Llama POST /analyze sin persistir. (`2933897`)
- **🔬 Deep check** — botón en header que pinguea LLM/STT/DB. (`e4f0fa8`)
- **🚨 PELIGRO toast** — slide-in bottom-right + 880Hz beep + 8s auto-dismiss.
  Solo dispara para alertas con `id > last_seen_high_water_mark`. (`2933897`)
- **⏸ Pause/resume** del auto-refresh. (`2933897`)
- **Connection state pill** (ok / reconectando / desconectado) — antes
  mostraba data stale silenciosamente. (`2933897`)
- **Banner de validación n=129** (92.3% / 19.2% / 73.1%) — encuesta
  pre-MVP. (`4060d1c`)
- **Survey-banner**, **dataset stats en header**, **empty state row**,
  **mobile responsive <640px**. (`2933897`, `1d5ed2d`)
- **Fix `window.NAHUAL_API_URL = ""` falsy fallback** — empty string
  caía al default `localhost:8000` desde browsers remotos. (`6e186f1`)

### 🌐 Nginx (en droplet)

- **Server name extendido** — `nahualshield.com` + `nahualsec.com` +
  `api.` / `panel.` / `www.` subdominios.
- **Per-IP rate limiting**:
  - `/analyze` 20/min, burst 10
  - `/alert` 15/min, burst 5
  - `/transcribe + /ocr` 8/min, burst 3 (cost guard Groq/Anthropic)
  - General API 120/min, burst 40
- **Security headers globales**: `X-Content-Type-Options nosniff`,
  `X-Frame-Options SAMEORIGIN`, `Referrer-Policy`, `X-XSS-Protection`,
  `Permissions-Policy locks geolocation/mic/camera`.
- **Cache-Control** no-cache en `.html/.js` para que los updates del
  panel se vean al recargar.
- **HSTS preparado** (comentado hasta certbot).

### 📚 Setup local

- **`start_all.bat`** + **`start_all.sh`** — banner, dependency checks,
  seed idempotente, multi-window backend+panel, browser auto-open.
  (`4060d1c`)
- **conftest.py** que limpia env vars al inicio de pytest así `.env`
  con `NAHUAL_API_KEY=nahual-hackathon-2026` no contamina los tests. (`4060d1c`)

---

## Bugs encontrados en testing en vivo (Marco + Armando)

| Cuándo | Bug | Fix commit |
|---|---|---|
| 13:37 | `15,000 pesos a la semana` → SEGURO 0% (dataset solo tenía `$15,000 semanales`) | `32c7c21` |
| 13:37 | `me van a matar` → SEGURO 0% (dataset solo tenía `te voy a matar` perspectiva agresor) | `32c7c21` |
| 13:51 | Panel "desconectado" en producción | `6e186f1` |
| 13:51 | PDF no llegaba al guardián (JID mal formado) | `11eaec8` |
| 14:19 | Snippet del overlay mostraba JSON de React de Instagram | `afef156` |
| 14:58 | Audio devolvía 415 (`audio/ogg; codecs=opus` no en set check) | `8ba2046` |
| 14:58 | OCR devolvía 502 (modelo Anthropic deprecado) | `8ba2046` |
| 14:58 | Bot no paraba con `gracias`/`bye` | `8ba2046` |
| 14:58 | Roblox extension detectaba página de catálogo de gift cards | `8ba2046` |
| 14:58 | Discord extension no detectaba | `8ba2046` |
| 15:17 | Bot ejecutaba /analyze("No") al final del flujo | `ee89db2` |
| 15:17 | Roblox catálogo seguía disparando overlay tras navegar | `ee89db2` |

Cada uno detectado en producción y corregido + deployed dentro de la misma sesión.

---

## Estructura de versiones

- **v1.0** — MVP entregable Hackathon (placeholder dataset, 47 patrones)
- **v1.1** — Panel + extension v1.1 + Phase 4 features
- **v1.2** — ETL real dataset (563 patrones) + admin endpoints
- **v1.3** — Production-hardened (768 patrones, deployed, all bugs fixed)

---

## Siguiente milestone (post-hackathon)

- HTTPS via certbot cuando el DNS apunte a `nahualshield.com`
- Postgres + connection pool (vs SQLite single-file)
- OAuth real (vs API key estática)
- Sentry + Datadog (vs print logs)
- Backup automático SQL de la DB
- Tests E2E con Playwright para el panel
- Ampliación regional del dataset (variantes norteño / sureste / Bajío)
- Sextortion benchmark dataset comparado con baseline humano

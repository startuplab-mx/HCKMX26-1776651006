# NAHUAL — Claude Code Project Context

## WHAT IS THIS PROJECT
Nahual is a criminal recruitment detection system for minors in Mexico. It detects digital recruitment patterns used by cartels (narcoculture, fake job offers, threats, sextortion) across 4 phases: Captación, Enganche, Coerción, Explotación.

Built for Hackathon 404: Threat Not Found (April 24-26, 2026) — organized by the U.S. Embassy (INL) and StartupLab MX. Prize: $25,000 USD.

## TEAM
- **Armando (Lead Dev):** Sole developer. Experienced with WhatsApp bots (Baileys), Python, FastAPI. Runs AUCTORUM (commercial WhatsApp AI agency).
- **Marco (Clinical/UX):** Medical student. Owns: bot language, legal protocols, pitch, validation. NOT a programmer.

## ARCHITECTURE — 5 MODULES

```
D:\nahual\
├── CLAUDE.md                      ← YOU ARE HERE
├── README.md
├── LICENSE (MIT)
├── .env.example
├── .gitignore
│
├── bot/                           ← Module 1: WhatsApp Bot (Node.js + Baileys)
│   ├── package.json
│   ├── index.js                   ← Entry point
│   ├── handlers/
│   │   ├── messageHandler.js      ← Process incoming messages
│   │   ├── flowController.js      ← State machine (FSM)
│   │   └── alertDispatcher.js     ← Send alerts to backend + guardian
│   ├── config/
│   │   └── messages.js            ← ALL bot messages (Marco edits this)
│   └── utils/
│       ├── textExtractor.js       ← Extract text from any WA message type
│       └── sessionManager.js      ← Per-user state management
│
├── backend/                       ← Module 2: API + Classifier (Python + FastAPI)
│   ├── requirements.txt
│   ├── main.py                    ← FastAPI app + all endpoints
│   ├── classifier/
│   │   ├── __init__.py
│   │   ├── heuristic.py           ← Layer 1: regex + keyword scoring
│   │   ├── llm_layer.py           ← Layer 2: Claude API (grey zone only)
│   │   ├── pipeline.py            ← Orchestrates both layers + OVERRIDE logic
│   │   └── keywords/              ← JSON files per phase (PENDING - Marco working on it)
│   │       ├── phase1_captacion.json
│   │       ├── phase2_enganche.json
│   │       ├── phase3_coercion.json
│   │       ├── phase4_explotacion.json
│   │       └── emojis_narco.json
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── db.py                  ← SQLite connection + CRUD
│   ├── reports/
│   │   ├── __init__.py
│   │   └── pdf_generator.py       ← ReportLab PDF generation
│   └── tests/
│       └── test_classifier.py
│
├── extension/                     ← Module 3: Nahual Shield (Chrome Extension)
│   ├── manifest.json              ← Manifest V3
│   ├── content.js                 ← MutationObserver + mini-regex + overlay UI
│   ├── popup.html                 ← Extension popup
│   ├── popup.js
│   └── styles.css                 ← Overlay styling (Carbón #2F353A + Cobre #C16A4C)
│
├── panel/                         ← Module 4: Web Dashboard
│   ├── index.html                 ← Single-file dashboard (HTML + Tailwind CDN + vanilla JS)
│   └── js/
│       └── app.js                 ← API calls + DOM rendering + auto-refresh
│
├── docs/                          ← Documentation + design materials
│   ├── arquitectura.png
│   ├── flujo-bot.png
│   ├── wireframes/
│   ├── protocolo-legal.md
│   └── investigacion/
│       ├── NAHUAL1.md
│       └── NAHUAL2.md
│
└── scripts/
    ├── seed_test_data.py          ← Populate DB with demo data
    └── demo_scenario.py           ← Automated demo script
```

## TECH STACK

| Component | Technology | Notes |
|-----------|-----------|-------|
| Bot WhatsApp | Node.js 18+ + @whiskeysockets/baileys | WebSocket, QR auth, ES Modules |
| Backend API | Python 3.11+ + FastAPI + Uvicorn | Auto Swagger at /docs |
| Classifier | Python regex + keyword scoring | No GPU, no ML libraries needed |
| LLM Layer | Anthropic Claude API (claude-sonnet-4-20250514) | Only for grey zone (0.3-0.6) |
| Database | SQLite3 (built-in Python) | Zero config |
| PDF Reports | Python ReportLab | Template-based |
| Extension | Chrome Manifest V3 | MutationObserver + content scripts |
| Panel Web | HTML + Tailwind CDN + vanilla JS | Single file, no build step |
| Tunnel | ngrok | Expose bot for demo |

## CRITICAL DESIGN RULES

### Classifier Override Logic
If Phase 3 (Coerción) OR Phase 4 (Explotación) individual score >= 0.80, SKIP weighted average and set risk_score = 1.0 (PELIGRO INMINENTE). This is non-negotiable.

### Scoring Formula (Normal Path)
```
risk_score = phase1 * 0.15 + phase2 * 0.25 + phase3 * 0.35 + phase4 * 0.25
```
Levels: SEGURO (0-0.29), ATENCIÓN (0.3-0.69), PELIGRO (0.7-1.0)

### Bot UX Rules
- Send "Recibido. Dame unos segundos... 🔍" immediately when analyzing
- 5-second timeout for LLM layer — fallback to heuristic if exceeded
- Reject audio/images/stickers with: "Aún estoy entrenando mis ojos y oídos 🙈. Por ahora, envíame texto."
- NEVER store original message text — only SHA-256 hash + anonymized summary
- All messages in Mexican Spanish, informal tuteo, empathetic, non-judgmental

### Privacy by Design
- No full messages stored, only hashes
- Alert to guardian contains risk level + platform ONLY, never content
- Compliant with Art. 16 CPEUM (no interception of private communications)
- Bot only analyzes data self-reported by the user

### Colors (Brand)
- Carbón: #2F353A
- Cobre Terracota: #C16A4C
- White: #FFFFFF
- Semáforo: Green #22C55E, Yellow #EAB308, Red #EF4444

## DATABASE SCHEMA

```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    platform TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'bot',
    risk_score REAL NOT NULL,
    risk_level TEXT NOT NULL,
    phase_detected TEXT,
    categories TEXT,
    summary TEXT,
    original_text_hash TEXT,
    contact_phone TEXT,
    report_generated INTEGER DEFAULT 0,
    report_path TEXT,
    llm_used INTEGER DEFAULT 0,
    override_triggered INTEGER DEFAULT 0,
    session_id TEXT
);

CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    current_step TEXT NOT NULL DEFAULT 'inicio',
    data TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## API ENDPOINTS (33 total)

### Public (no auth)
| Method | Route | Description |
|--------|-------|-------------|
| POST | /analyze | Classify text → risk_score, phases, categories, why, escalation, legal |
| POST | /alert | Register alert from bot/extension (also classifies + persists) |
| POST | /transcribe | Audio → text (Groq Whisper) |
| POST | /ocr | Image → text (Claude Vision) |
| GET | /stats | Aggregated stats (totals, by phase, by platform, by status) |
| GET | /stats/timeseries | Hourly/daily buckets for the panel chart |
| GET | /health | LLM/STT enabled flags + auth_enforced |
| POST | /report/{id} | Download PDF report (no auth — IDs already gated by /alerts) |
| GET | /profile/{id} | Cumulative risk profile of a session (pitch demo + extension) |
| POST | /feedback | User feedback for the auto-tuner (bot/panel/extension) |
| POST | /contribute | Anonymous research metadata |
| GET | /contributions/stats | Aggregate from contributed-research dataset |
| GET | /docs | Swagger UI (automatic) |

### Admin / observability (read-only, public, PII-free)
| Method | Route | Description |
|--------|-------|-------------|
| GET | /admin/version | commit SHA + branch + commit_at + python version + env |
| GET | /admin/dataset-info | per-phase pattern counts + weight histogram + emojis |
| GET | /admin/metrics | requests/analyze/alert/transcribe/ocr counters since boot |
| GET | /admin/healthcheck-deep | live ping to DB + Anthropic + Groq |

### Protected (X-API-Key header, default `nahual-hackathon-2026`)
| Method | Route | Description |
|--------|-------|-------------|
| GET | /alerts | List + filter (status, risk_level, limit, offset) |
| GET | /alerts.csv | Excel-friendly UTF-8-BOM export |
| GET/PATCH | /alerts/{id} | Detail / update status / notes / reviewer |
| POST | /alerts/{id}/escalate | Escalate to 088 / SIPINNA / Fiscalía |
| GET | /alerts/{id}/why | Reconstruct human explanations from pattern_ids |
| GET | /alerts/{id}/legal | Recompute legal block from stored alert |
| GET/PUT/DELETE | /sessions/{id} | Bot session state (used to survive restarts) |
| GET/DELETE | /risk-history/{id} | Cronological scores for a session |
| GET/POST | /precision/* | Auto-tuner diagnostics + state + manual tune |

## BOT STATE MACHINE

```
INICIO → BIENVENIDA → RECIBIR_MSG → ANALIZANDO → RESULT_SAFE/ATTENTION/DANGER
                                                        │
                                            (if DANGER) ▼
                                         ASK_CONTACT → NOTIFY → GEN_REPORT
```

## KEYWORDS — STATUS

**Dataset is COMPLETE and in production.** 900 patterns total, 487 high-confidence (weight ≥ 0.8), 14 emojis.

```
phase1_captacion.json   299 patterns (high=132)  Captación
phase2_enganche.json    192 patterns (high= 71)  Enganche
phase3_coercion.json    236 patterns (high=187)  Coerción ← override-prone
phase4_explotacion.json 173 patterns (high= 89)  Explotación
emojis_narco.json        14 emojis
```

Patterns include both **aggressor speech** ("te voy a matar") and **victim
reception** ("me van a matar", "me amenazan con publicar mis fotos") —
critical because users paste mensajes recibidos OR describe what happened.

Sources: Marco's curated patterns (374 originales) + alta-confidence subset
of CSV expansion (189) + audit additions (sextortion, Roblox grooming,
Mexican slang lana/billete/feria, cartel jerga halcón/puchador/punto) +
structural audit (perspectiva-víctima, distress, money sin $) +
selffeed (cartel slogans testeados contra producción).

ETL: `scripts/etl_dataset.py`, `scripts/add_audit_patterns.py`,
`scripts/add_structural_patterns.py` (all idempotent).

## BAYESIAN LAYER (Capa 1.5)

**`backend/classifier/bayesian.py`** — Naive Bayes incremental with
n-grams (1, 2, 3), Laplace smoothing, atomic JSON persistence,
RLock-protected. 0 deps beyond stdlib.

```
total_training_examples: 911
vocabulary_size:         5701
class_distribution:
  seguro          75   (50 base + 25 casual money/spending)
  captacion      264
  enganche       189
  coercion       222
  explotacion    161
```

Bootstrap: `scripts/bootstrap_bayesian.py` reads all 4 phaseN_*.json
plus 75 hand-picked safe phrases. Persists to
`backend/classifier/bayesian_model.json`.

Auto-feed from `/feedback`:
* `confirm` → `train_one(surrogate_text, alert.phase_detected)`
* `deny` / `operator_fp` → `train_one(surrogate_text, "seguro")`

`surrogate_text` is built from the alert's anonymized summary +
reconstructed why-list — original text never leaves the wire.

Pipeline merge math:
* heur=0, no Bayes data            → LLM 100%
* heur=0, Bayes ready              → Bayes 30% + LLM 70%
* heur>0, Bayes ready, LLM fired   → Heur 50% + Bayes 20% + LLM 30%
* heur>0, Bayes ready, no LLM      → Heur 70% + Bayes 30%
* Bayes insufficient_data          → unchanged from before

Endpoints:
* `GET /bayesian/stats` — counts, top features per class
* `POST /bayesian/predict` — pure Bayesian (debug/comparison)

Score-comparison vs heurístico-only on the structural verification suite:
**16/20 (80%) → 20/20 (100%)** without needing the LLM.

## DEPLOYMENT — PRODUCTION

**Live at**: `159.223.187.6` (DigitalOcean Ubuntu 24.04, 1 vCPU / 1 GB)

```
Backend      systemd: nahual-backend.service  → uvicorn :8000
Bot WhatsApp systemd: nahual-bot.service      → +52 844 538 7404
Panel        Nginx static at /opt/nahual/panel + reverse proxy
HTTP only    HTTPS pending DNS for nahualshield.com / nahualsec.com
```

**Production resilience (already shipped)**:
- Baileys reconnect with exponential backoff + listener cleanup + SIGTERM
- SQLite WAL + retry-on-lock (5 attempts, exp backoff)
- Bot per-JID rate limit (5 alerts / 60s sliding window)
- Session TTL eviction (drop entries idle > 7d)
- Webhook retry (3 attempts on 5xx/network, 4xx never retries)
- Nginx rate limits per IP + security headers (X-Frame-Options, CSP, HSTS-ready)
- Anthropic model: `claude-sonnet-4-5-20250929`
- MIME normalization for `audio/ogg; codecs=opus` & `image/jpeg;charset=binary`

## BOT BEHAVIORAL RULES

**Universal commands** (any state, slash optional):
`menu`, `ayuda`, `privacidad`, `estado`, `reset`, `reporte`

**Conversational closers** (don't trigger /analyze):
`gracias`, `ok`, `bye`, `listo`, `chido`, `sale`, `fin`, `ya`, `cuídate`,
`no`, `no gracias`, `estoy bien`, `nada más`, `ya no`...

**Distress / SOS** (empathy first, no analysis):
`tengo miedo`, `necesito ayuda`, `me quiero morir`, `estoy asustado/a`
→ Línea de la Vida (800-911-2000) + 088 + invites the suspicious message.

**Greeting handling** (don't double-welcome):
Bot greets only on EXPLICIT greeting OR first-ever turn — Marco surfaced
the double-welcome bug Apr 25.

## CHROME EXTENSION — RULES

`extension/` is **v1.3.0**. Manifest matches `https://discord.com/*`,
`https://*.discord.com/*`, `https://web.whatsapp.com/*`,
`https://www.instagram.com/*`, Roblox.

**Detection scope** (critical to avoid false positives):
- Per-platform `urlAllowlist` / `urlBlocklist` (Roblox blocks `/catalog`,
  `/giftcards`, `/marketplace`, `/upgrades`, `/charity`, `/redeem`,
  `/avatar`, `/games/<id>`, `/home`, `/discover`)
- Per-platform `containerSelectors` verified against the user's existing
  extractors at `C:\Users\arma2\Codigo\{discord,wa,ig}-chat-extractor`
  (Discord: `ol[class*="scrollerInner"]` + `li[id^="chat-messages-"]`)
- `WHITELIST_REGEX` for UI/store phrases that look risky out of context
- `nodeIsInsideChat()` — only fire if matched text is INSIDE a chat
  container; avoids matching JSON payloads in `<script>` tags
- SPA navigation handling: `platformIsActive()` re-evaluates on every
  scan + mount watcher tracks `location.href` changes

**Phase 4 regex requires verb-of-proposition** — "te paso 10000 robux si"
fires; "Buy Roblox Gift Cards" (catalog) does NOT.

## IMPORTANT NOTES FOR FUTURE WORK

- This was a HACKATHON project. Speed > perfection. Working demo > clean code.
- Sole developer: Armando. All bot/backend/panel/extension code lives in `D:\nahual` (Windows D: drive).
- Existing chat extractors at `C:\Users\arma2\Codigo\` were the reference for extension DOM selectors.
- All commits must have descriptive messages with conventional prefixes: `feat:`, `fix:`, `docs:`, `polish:`, `round-N`, `hotfix:`.
- Privacy by design is non-negotiable — never store original message text, only SHA-256 + anonymized summary.
- Override rule (Phase 3 or Phase 4 individual ≥ 0.80 → risk_score = 1.0) is the cornerstone of detection. Don't relax it.
- 147 pytest tests must remain green. New endpoints get tests in `tests/test_admin.py` style.

See `CHANGELOG.md` for the post-deploy commit history.

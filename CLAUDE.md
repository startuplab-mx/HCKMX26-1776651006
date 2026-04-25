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

## API ENDPOINTS

| Method | Route | Description |
|--------|-------|-------------|
| POST | /analyze | Analyze text → risk_score, risk_level, phases, categories |
| POST | /alert | Register alert from bot (internal webhook) |
| GET | /alerts | List all alerts (desc by date) |
| GET | /alerts/{id} | Single alert detail |
| GET | /stats | Aggregated stats (totals, by phase, by platform) |
| POST | /report/{id} | Generate PDF report for an alert |
| GET | /health | Health check |
| GET | /docs | Swagger UI (automatic) |

## BOT STATE MACHINE

```
INICIO → BIENVENIDA → RECIBIR_MSG → ANALIZANDO → RESULT_SAFE/ATTENTION/DANGER
                                                        │
                                            (if DANGER) ▼
                                         ASK_CONTACT → NOTIFY → GEN_REPORT
```

## KEYWORDS — STATUS
The keyword JSON files in backend/classifier/keywords/ are PENDING. Marco is working on them.
For now, create the classifier with a PLACEHOLDER dataset that has 5-10 patterns per phase so the pipeline works end-to-end. We'll swap in the real dataset when Marco delivers.

### Placeholder patterns to use:
Phase 1 (Captación): "quiero jale", "$X,000 semanales", "guardia de seguridad", "te pago el viaje", narco emojis
Phase 2 (Enganche): "dónde vives", "pásate a telegram", "no le digas a nadie", "envía tu ubicación"
Phase 3 (Coerción): "ya sabes demasiado", "te vamos a buscar", "última oportunidad", "te va a pesar"
Phase 4 (Explotación): "ve al punto", "deposita $X", "manda fotos", "trae a tus compas", "gift card"

## WHAT TO BUILD NOW (IN ORDER)

### Phase 1: Foundation (BUILD FIRST)
1. Initialize repo structure (all folders, package.json, requirements.txt, .gitignore, LICENSE, .env.example)
2. Backend: FastAPI app with /health, /analyze, /alerts, /stats, /report/{id} endpoints
3. Classifier: heuristic.py with 4-phase regex scoring + override logic + pipeline.py
4. Database: SQLite init + CRUD operations

### Phase 2: Bot
5. Bot: Baileys connection with QR auth
6. Bot: Message handler + text extractor
7. Bot: State machine (flowController.js) with all states
8. Bot: messages.js with all bot messages
9. Bot: Integration with backend (/analyze endpoint via axios)
10. Bot: Alert dispatcher (webhook to backend + message to guardian)

### Phase 3: Panel + PDF
11. Panel: HTML dashboard with stats cards + alerts table + semaphore colors + auto-refresh
12. PDF: ReportLab template with incident data + legal protocols + contacts

### Phase 4: Extension
13. Extension: manifest.json + content.js with MutationObserver
14. Extension: Mini-regex local detection (Phase 3/4 patterns only)
15. Extension: Overlay UI + deep link to WhatsApp bot

### Phase 5: Polish
16. LLM Layer: Claude API integration with 5s timeout
17. seed_test_data.py: Demo data for panel
18. Testing: End-to-end flow
19. README.md: Complete documentation

## IMPORTANT NOTES
- This is a HACKATHON project. Speed > perfection. Working demo > clean code.
- The extension content scripts for Instagram, WhatsApp Web, and Discord DOM extraction already exist in Armando's other projects. He will integrate them manually.
- All commits must have descriptive messages with conventional prefixes: feat:, fix:, docs:, polish:
- The project runs on Windows (D: drive). Use appropriate path separators.

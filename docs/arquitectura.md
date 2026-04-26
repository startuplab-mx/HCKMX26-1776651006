# Arquitectura — Nahual

## Vista general

```mermaid
flowchart TB
    subgraph CANALES[Canales de entrada]
        Bot["🤖 Bot WhatsApp<br/>+52 844 538 7404<br/>(Reactivo · Baileys 6.7)"]
        Ext["🛡️ Nahual Shield v1.3<br/>WA · IG · Discord · Roblox<br/>(Proactivo · Manifest V3)"]
        API["🌐 API pública<br/>POST /analyze<br/>+ /admin/* observabilidad"]
    end

    subgraph BACKEND[Backend Core · FastAPI :8000]
        direction TB
        Pipe[Pipeline]
        H[Layer 1<br/>Heuristic 900 patrones<br/>(F1 299 · F2 192 · F3 236 · F4 173)]
        L[Layer 2<br/>claude-sonnet-4-5<br/>5s timeout · zona gris 0.3-0.6]
        STT[Layer Audio<br/>Groq Whisper-large-v3]
        OCR_L[Layer Imagen<br/>Claude Vision]
        OV{{"Override Fase 3/4 ≥ 0.80<br/>→ risk_score = 1.0"}}
        DB[(SQLite + WAL<br/>retry on lock<br/>alerts + sessions + risk_history)]
        PDF[ReportLab<br/>folio NAH-2026-XXXX<br/>marco legal MX]
        WH[Webhooks outbound<br/>retry 3× backoff]
    end

    subgraph INFRA[Infra · DigitalOcean 159.223.187.6]
        Nginx[Nginx :80<br/>rate limit + security headers<br/>+ static panel]
        SystemD[systemd<br/>nahual-backend + nahual-bot]
    end

    Panel["📊 Panel Web<br/>http://159.223.187.6/<br/>auto-refresh 5s · Tailwind + Chart.js<br/>+ 🧪 manual test + 🔬 deep check"]

    Bot -->|/alert con X-API-Key| Nginx
    Ext -.deep-link wa.me.-> Bot
    API --> Nginx
    Nginx --> Pipe
    Pipe --> H
    H --> OV
    OV -- 'no override · grey zone 0.3-0.6' --> L
    L --> DB
    OV -- 'override' --> DB
    H -- 'normal weighted' --> DB
    DB --> Panel
    DB --> PDF
    PDF -.PDF.-> Bot
    Panel -.descarga PDF.-> PDF
    Bot --> STT
    Bot --> OCR_L
    DB --> WH
    WH -.alert.escalated.-> External[088 / SIPINNA / Fiscalía]
    SystemD --> Bot
    SystemD --> BACKEND
```

## Flujo del Bot

```mermaid
stateDiagram-v2
    [*] --> inicio
    inicio --> recibir_msg: greeting<br/>(hola, ola, qué pex...)
    inicio --> analizando: substantive text
    inicio --> [*]: closer<br/>(gracias, ok, no, bye)
    inicio --> recibir_msg: distress<br/>(tengo miedo, ayuda)

    recibir_msg --> analizando: paste message
    recibir_msg --> confirm_transcription: audio/imagen<br/>(STT/OCR)
    confirm_transcription --> analizando: SÍ
    confirm_transcription --> recibir_msg: NO

    analizando --> result: SEGURO / ATENCION
    analizando --> notify: PELIGRO

    notify --> ask_contribute: phone enviado<br/>(+ aviso + PDF al guardián)
    notify --> recibir_msg: deny / falso positivo

    result --> ask_contribute: post-análisis
    ask_contribute --> ask_region: SÍ
    ask_contribute --> [*]: NO

    ask_region --> [*]: región o "paso"

    %% Universal commands intercept ALL states:
    note right of inicio
        En cualquier estado el usuario puede:
        menu · ayuda · privacidad · estado
        reset · reporte
    end note
```

## Lógica del clasificador (4 capas cognitivas — v1.4)

```mermaid
flowchart LR
    T[texto] --> N[normalize_advanced<br/>chat MX + números + typos]
    N --> P1[Fase 1<br/>Captación]
    N --> P2[Fase 2<br/>Enganche]
    N --> P3[Fase 3<br/>Coerción]
    N --> P4[Fase 4<br/>Explotación]
    N --> EM[Emojis narco<br/>boost por afinidad]
    N --> BAY[Capa 1.5<br/>Naive Bayes<br/>n-gramas 1-3<br/>911 docs]
    EM --> P1
    EM --> P2
    EM --> P3
    EM --> P4
    P3 --> OV{phase3/4 ≥ 0.80?}
    P4 --> OV
    OV -- sí --> R1[risk_score = 1.0<br/>PELIGRO + override]
    OV -- no --> CB[contextual_boost<br/>1.3× ó 1.5× si danger combo]
    P1 --> CB
    P2 --> CB
    CB --> W[weighted avg<br/>+ saturation floor]
    W --> ACT{Activación LLM:<br/>grey zone OR<br/>score=0+texto>30 OR<br/>score<0.3+keywords}
    ACT -- sí --> LLM[Claude Sonnet 4.5<br/>5s timeout]
    ACT -- no --> MERGE[Merge 3-vías:<br/>heur 50% + bayes 20% + LLM 30%]
    BAY --> MERGE
    LLM --> MERGE
    MERGE --> R2[risk_level<br/>SEGURO/ATENCION/PELIGRO]
```

**Activación LLM** — la Capa 2 ya no espera solo la zona gris (0.3-0.6).
Activa en 3 condiciones:
- Zona gris clásica
- score=0 con texto sustantivo (>30 chars) — Marco gap
- score<0.3 con keywords de money/work/threat/sextorsion

**Merge 3-vías** depende de qué capas se activaron:
- Solo heurístico → score = heur
- Heur + Bayes → 70% heur + 30% bayes
- Heur + LLM (sin Bayes) → 50% heur + 50% LLM
- Heur + Bayes + LLM → 50% heur + 20% bayes + 30% LLM
- heur=0 + LLM → 100% LLM (no merge con 0)
- heur=0 + Bayes + LLM → 30% bayes + 70% LLM

## Datos persistidos

| Campo | Almacenado | Notas |
|-------|-----------|-------|
| Texto original | ❌ | Nunca persistido (privacidad) |
| `original_text_hash` | ✅ SHA-256 | Permite detección de repeticiones sin exponer contenido |
| `summary` | ✅ Anonimizado | "Mensaje de N chars · señales: X, Y" |
| `categories` | ✅ JSON | Fases activadas + emojis detectados |
| `risk_score`, `risk_level` | ✅ | Score [0,1] + label SEGURO/ATENCION/PELIGRO |
| `override_triggered` | ✅ Bool | Marca si la regla de cortocircuito disparó |
| `contact_phone` | ⚠️ Opcional | Sólo si el menor lo provee voluntariamente |

## Cumplimiento

- **Art. 16 CPEUM** — sólo se analizan datos autoinformados; no se interceptan comunicaciones.
- **LGDNNA Art. 47** — protección integral de NNA contra reclutamiento.
- **LFPDPPP** — sin PII innecesaria; hash + summary.
- **Ley Olimpia** — protocolo activado en sextorsión (Fase 4).

## Hardening de producción

```mermaid
flowchart LR
    subgraph PROTECCIONES
        direction TB
        RL[Rate Limit<br/>Nginx per-IP<br/>+ Bot per-JID]
        BO[Baileys backoff<br/>exp + jitter<br/>+ listener cleanup]
        SQL[SQLite retry<br/>5× exp backoff<br/>WAL + lock detection]
        WHK[Webhook retry<br/>3× backoff<br/>5xx only]
        SES[Session TTL<br/>evict idle > 7d]
        SIG[SIGTERM/SIGINT<br/>graceful shutdown]
    end

    subgraph SEGURIDAD
        direction TB
        AUTH[X-API-Key opt-in<br/>NAHUAL_API_KEY]
        SH[Security headers<br/>X-Frame-Options<br/>Permissions-Policy<br/>Referrer-Policy]
        CORS[CORS allowlist<br/>nahualshield + nahualsec]
    end

    subgraph PRIVACIDAD
        direction TB
        NOTEXT[Texto NUNCA persiste<br/>solo SHA-256]
        ANON[Resumen anonimizado<br/>+ pattern_ids]
        WL[Whitelist + scope a chat<br/>en extensión]
    end
```

## Endpoints de observabilidad (`/admin/*`)

Todos públicos, read-only, sin PII:

| Endpoint | Output |
|----------|--------|
| `/admin/version` | commit SHA + branch + commit_at + python + env |
| `/admin/dataset-info` | per-fase pattern counts + weight histogram + emojis + tuner overlay size |
| `/admin/metrics` | requests/analyze/alert/transcribe/ocr counters + uptime + alerts_in_db |
| `/admin/healthcheck-deep` | ping live a DB + Anthropic + Groq con timeouts per-check |

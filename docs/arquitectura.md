# Arquitectura — Nahual

## Vista general

```mermaid
flowchart TB
    subgraph CANALES[Canales de entrada]
        Bot["🤖 Bot WhatsApp<br/>(Reactivo · Baileys)"]
        Ext["🛡️ Nahual Shield<br/>(Proactivo · Manifest V3)"]
        API["🌐 API pública<br/>POST /analyze"]
    end

    subgraph BACKEND[Backend Core · FastAPI :8000]
        direction TB
        Pipe[Pipeline]
        H[Layer 1<br/>Heuristic regex+keywords]
        L[Layer 2<br/>Claude API · 5s timeout]
        OV{{"Override Fase 3/4 ≥ 0.80<br/>→ risk_score = 1.0"}}
        DB[(SQLite<br/>alerts + sessions)]
        PDF[ReportLab<br/>folio NAH-2026-XXXX]
    end

    Panel["📊 Panel Web :3000<br/>auto-refresh 5s · Tailwind"]

    Bot -->|/alert| Pipe
    Ext -.deep-link.-> Bot
    API --> Pipe
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
```

## Flujo del Bot

```mermaid
stateDiagram-v2
    [*] --> inicio
    inicio --> recibir_msg: greeting
    inicio --> analizando: substantive text
    recibir_msg --> analizando: paste message
    analizando --> result: SEGURO / ATENCION
    analizando --> notify: PELIGRO
    notify --> result: phone enviado
    result --> analizando: nuevo mensaje
    result --> [*]: "reporte" → PDF
    notify --> [*]: "reporte" → PDF
```

## Lógica del clasificador

```mermaid
flowchart LR
    T[texto] --> N[normalize<br/>lowercase + sin diacríticos]
    N --> P1[Fase 1<br/>Captación]
    N --> P2[Fase 2<br/>Enganche]
    N --> P3[Fase 3<br/>Coerción]
    N --> P4[Fase 4<br/>Explotación]
    N --> EM[Emojis narco<br/>boost por afinidad]
    EM --> P1
    EM --> P2
    EM --> P3
    EM --> P4
    P3 --> OV{phase3 ≥ 0.80?}
    P4 --> OV
    OV -- sí --> R1[risk_score = 1.0<br/>PELIGRO + override]
    OV -- no --> W[weighted avg<br/>+ saturation floor]
    P1 --> W
    P2 --> W
    W --> GZ{0.3 ≤ score ≤ 0.6?}
    GZ -- sí --> LLM[Claude API<br/>5s timeout]
    GZ -- no --> R2[risk_level<br/>SEGURO/ATENCION/PELIGRO]
    LLM --> R2
```

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

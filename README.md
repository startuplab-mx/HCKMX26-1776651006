# 🛡️ NAHUAL

**Sistema de detección de reclutamiento criminal digital de menores en México.**

> "Nahual detecta manipulación digital antes de que escale a daño real"

Construido para **Hackathon 404: Threat Not Found** (24-26 abril 2026) — U.S. Embassy (INL) + StartupLab MX.

---

## ¿Qué hace?

Nahual analiza mensajes que un menor recibe en redes sociales (WhatsApp, Instagram, Discord) y detecta las **4 fases del reclutamiento criminal**:

1. **Captación** — ofertas falsas de trabajo, narcocultura aspiracional
2. **Enganche** — aislamiento, secrecía, traslado a canales privados
3. **Coerción** — amenazas, presión, "ya sabes demasiado"
4. **Explotación** — sextorsión, instrucciones operativas, depósitos

El sistema asigna un `risk_score` (0.0–1.0) y un `risk_level` (`SEGURO` / `ATENCIÓN` / `PELIGRO`).

### Regla de Override (Cortocircuito Crítico)

Si Fase 3 o Fase 4 obtienen score individual ≥ 0.80, el sistema ignora el promedio ponderado y eleva `risk_score` a 1.0 (**PELIGRO INMINENTE**). El reclutamiento NO es lineal: un agresor puede saltar directo a la amenaza.

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│  CANALES DE ENTRADA                                      │
│  • Bot WhatsApp (Baileys, REACTIVO)                      │
│  • Nahual Shield (Extensión Chrome, PROACTIVO)           │
│  • API pública POST /analyze                             │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│  BACKEND CORE (FastAPI :8000)                            │
│  • Capa 1: Heurístico (regex + keywords + emojis)        │
│  • Capa 2: Claude API (zona gris 0.3–0.6, timeout 5s)    │
│  • Override: Fase 3/4 ≥ 0.80 → risk_score = 1.0          │
│  • SQLite + PDF (ReportLab) + Webhooks                   │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│  PANEL WEB (:3000)                                       │
│  Dashboard alertas + semáforo + descarga PDF             │
└─────────────────────────────────────────────────────────┘
```

---

## Stack

| Componente | Tecnología |
|------------|-----------|
| Bot WhatsApp | Node.js 18+ + `@whiskeysockets/baileys` |
| Backend API | Python 3.11+ + FastAPI + Uvicorn |
| Clasificador | Regex + keyword scoring (sin GPU) |
| LLM Layer | Anthropic Claude API (sólo zona gris) |
| Database | SQLite3 |
| PDF | ReportLab |
| Extensión | Chrome Manifest V3 |
| Panel | HTML + Tailwind CDN + vanilla JS |

---

## Setup Rápido

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp ../.env.example ../.env  # editar y llenar ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000
```

Swagger UI automática: <http://localhost:8000/docs>

### 2. Bot WhatsApp

```bash
cd bot
npm install
node index.js
# Escanea el QR con WhatsApp → Dispositivos vinculados
```

### 3. Panel Web

```bash
cd panel
# Sirvelo con cualquier server estático:
python -m http.server 3000
```

### 4. Extensión Nahual Shield

1. Abre `chrome://extensions/`
2. Activa **Modo desarrollador**
3. Click **Cargar descomprimida** → selecciona `extension/`

---

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|------------|
| `POST` | `/analyze` | Analiza texto → risk_score, fases, categorías |
| `POST` | `/alert` | Registra alerta (webhook bot) |
| `GET` | `/alerts` | Lista todas las alertas |
| `GET` | `/alerts/{id}` | Detalle de alerta |
| `GET` | `/stats` | Estadísticas agregadas |
| `POST` | `/report/{id}` | Genera PDF |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |

### Ejemplo

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "yo quiero jale, pago $15,000 semanales 🍕"}'
```

```json
{
  "risk_score": 0.78,
  "risk_level": "PELIGRO",
  "phase_detected": "captacion",
  "phase_scores": {"phase1": 0.85, "phase2": 0.0, "phase3": 0.0, "phase4": 0.0},
  "categories": ["narco_emoji_sinaloa", "oferta_economica"],
  "override_triggered": false,
  "llm_used": false
}
```

---

## Privacy by Design

- **No se almacenan mensajes completos**, solo SHA-256 + resumen anonimizado
- **Alerta a tutor** contiene SOLO nivel de riesgo + plataforma, NUNCA el contenido
- **Cumplimiento Art. 16 CPEUM** — no intercepta comunicaciones, sólo analiza datos autoinformados por el usuario
- **LFPDPPP** — protección de datos personales de menores
- **Ley Olimpia** — protocolo en casos de sextorsión

---

## Marco Legal

- Art. 47 LGDNNA — protección contra reclutamiento de menores
- Art. 16 CPEUM — inviolabilidad de comunicaciones (cumple)
- Código Penal Federal (reforma 2026) — hasta 18 años por reclutamiento
- Ley Olimpia — sextorsión

**Reportar:** Policía Cibernética **088** | SIPINNA <https://sipinna.gob.mx> | Línea de la Vida **800-911-2000**

---

## Documentación de IA

- **Claude Code** — asistente de programación para boilerplate. Todo el código revisado e integrado por el equipo.
- **Claude API** — Capa 2 del clasificador (zona gris 0.3–0.6, timeout 5 s). Componente funcional opcional. El sistema funciona sin ella.

El clasificador heurístico (Capa 1) y los datasets fueron investigados y construidos por el equipo basándose en fuentes verificadas (Colmex, El País, FinCEN, CSIS, REDIM, ONC).

Declaración detallada: [docs/ai_usage.md](docs/ai_usage.md).

---

## Troubleshooting

**El backend no arranca con `ModuleNotFoundError`.**
Activa el virtualenv e instala deps: `cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt`.

**En Windows, el seed falla con `UnicodeEncodeError` al imprimir emojis.**
Usa `set PYTHONIOENCODING=utf-8` (cmd) o `$env:PYTHONIOENCODING='utf-8'` (PowerShell) antes de ejecutar scripts que imprimen caracteres no-ASCII.

**`node` no se encuentra en la terminal.**
Verifica que `C:\Program Files\nodejs` o la ruta de NVM esté en tu PATH. Con NVM Windows: `nvm use 22`.

**El bot muestra QR cada vez que arranca.**
La primera sesión guarda credenciales en `bot/auth_info_baileys/`. No borres esa carpeta entre ejecuciones.

**La extensión no inyecta el overlay.**
Revisa `chrome://extensions/` → errores. Asegúrate de cargar la carpeta `extension/` completa (con `icons/`). Cambia `matches` en `manifest.json` si estás probando un subdominio distinto.

**`POST /report/{id}` devuelve 404.**
La alerta no existe. Crea una primero con `POST /alert` o corre `python scripts/seed_test_data.py`.

**CORS bloquea el panel.**
Revisa `.env`: con `CORS_ORIGINS=*` las credenciales se desactivan automáticamente. Si necesitas credenciales, enumera orígenes explícitos.

**El LLM siempre está desactivado (`llm_enabled: false`).**
Pon una `ANTHROPIC_API_KEY` real en `.env` (no el placeholder `sk-ant-xxxxx`).

---

## Equipo Vanguard

- **Armando Flores** — Lead Dev (AUCTORUM, bots WhatsApp, FastAPI)
- **Marco Espinosa** — Clinical/UX/Legal/Pitch (Medicina)

---

## Licencia

MIT — ver [LICENSE](LICENSE).

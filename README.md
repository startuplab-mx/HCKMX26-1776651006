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

Soporta **WhatsApp Web · Instagram · Discord · Roblox**.

1. Abre `chrome://extensions/`
2. Activa **Modo desarrollador**
3. Click **Cargar descomprimida** → selecciona `extension/`

---

## API Endpoints

### Análisis
| Método | Ruta | Descripción |
|--------|------|------------|
| `POST` | `/analyze` | Analiza texto → risk_score, fases, categorías, pattern_ids, **why**, **escalation**, **legal** |
| `POST` | `/transcribe` | 🎙️ Audio → texto (Groq Whisper) |
| `POST` | `/ocr` | 📸 Imagen → texto (Claude Vision) |

### Alertas + Triage
| Método | Ruta | Descripción |
|--------|------|------------|
| `POST` | `/alert` | Registra alerta (webhook bot/extensión) — incluye `why` + `escalation` + `legal` |
| `GET` | `/alerts` | Lista (filtrable por status / risk_level) |
| `GET` | `/alerts/{id}` | Detalle |
| `PATCH` | `/alerts/{id}` | Actualiza status / notes / reviewer |
| `POST` | `/alerts/{id}/escalate` | Escala a 088 / SIPINNA / Fiscalía |
| `GET` | `/alerts/{id}/history` | Audit trail |
| `GET` | `/alerts/{id}/legal` | Marco legal aplicable (recomputado desde DB) |
| `GET` | `/alerts/{id}/why` | 🧠 Reconstruye explicaciones humanas desde pattern_ids persistidos |
| `POST` | `/report/{id}` | Genera PDF dinámico con marco legal |

### Investigación anónima
| Método | Ruta | Descripción |
|--------|------|------------|
| `POST` | `/contribute` | Aporta metadata anónima (sin PII, `extra="forbid"`) |
| `GET` | `/contributions/stats` | Stats agregados (top patterns, regiones) |

### Escalamiento + perfil de riesgo (Phase 4)
| Método | Ruta | Descripción |
|--------|------|------------|
| `GET` | `/profile/{session_id}` | Perfil acumulativo: trend, avg, max, dominant phase, score timeline |
| `GET` | `/risk-history/{session_id}` | Historial cronológico de scores |
| `DELETE` | `/risk-history/{session_id}` | Reset (usado por demo_live.py) |

### Stats + sesiones + sistema
| Método | Ruta | Descripción |
|--------|------|------------|
| `GET` | `/stats` | by_level, by_phase, by_platform, by_status |
| `GET` | `/stats/timeseries` | Buckets por hora/día para gráfica del panel |
| `GET/PUT/DELETE` | `/sessions/{id}` | Persistencia de sesión del bot |
| `GET` | `/health` | Health check (LLM + STT enabled flags) |
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

## Diferenciadores clave (Phase 4)

Lo que ningún otro detector hace:

### 📈 Detección de escalamiento
Cada análisis con `session_id` se persiste en `risk_history`. El `EscalationDetector` calcula tendencia (creciente/estable/decreciente), velocidad (Δ promedio entre mensajes), y progresión de fase (captación → enganche → coerción). Cuando ATENCION + historial ≥ 3 + (velocity ≥ 0.20 OR progresión de fase) → **trayectory override** automático que sube a PELIGRO antes de que el menor sea captado.

### 🧠 Explicabilidad humana ("¿Por qué?")
Cada patrón en los JSON de keywords incluye campo `explanation` en español natural. La API surface el `why[]` array en `/analyze` y `/alert`, y `/alerts/{id}/why` lo reconstruye desde los `pattern_ids` persistidos — sin necesidad de re-clasificar (lo que sería imposible porque nunca se guarda el texto). El bot manda 🧠 *¿Por qué?* después del veredicto y el panel lo muestra al expandir cada alerta.

### 🛡️ Marco legal programático
Cada fase / categoría se mapea a artículos mexicanos (CPEUM 4 & 16, LGDNNA 47-VII / 48 / 101 Bis 2, **CPF 209 Sextus *propuesto*** — reclutamiento forzado pendiente de DOF, marzo 2026, CPF 282 / 199 Octies-Decies, LGAMVLV 20 Quáter, LGPSEDMTP 10, LFPDPPP 5-8) + autoridades (088, FEVIMTRA, Comisión de Búsqueda, etc.) + acciones recomendadas + derechos de la víctima. Surface en API, PDF dinámico, bot WhatsApp y panel.

### 🎬 Demo en vivo
`scripts/demo_live.py` proyecta en terminal una secuencia de 5 mensajes (contacto → captación → enganche → coerción → explotación) con barras de progreso ANSI, why list, trayectoria visual, y diferenciación entre override estático y override por trayectoria. Press ENTER para avanzar.

## Capacidades multimedia (Phase 3)

El bot acepta tres tipos de entrada:

| Tipo | Cómo funciona | Servicio |
|------|--------------|----------|
| 📝 **Texto** | Pegar el mensaje sospechoso. Análisis directo. | Heurístico + Claude (zona gris) |
| 🎙️ **Audio** | El bot transcribe con Whisper, muestra el texto al usuario para confirmar, después analiza. | Groq Whisper (`GROQ_API_KEY`) |
| 📸 **Captura** | OCR vía Claude Vision, confirmación, después análisis. Funciona con WhatsApp, Instagram, TikTok, Discord, **Roblox**, etc. | Claude Vision (`ANTHROPIC_API_KEY`) |

**Privacidad:** los bytes del audio/imagen se reenvían al proveedor para extracción y NO se persisten en Nahual. Sólo el texto extraído (tras confirmación del usuario) entra al pipeline normal — y de ahí únicamente se guarda el SHA-256.

## Investigación abierta (Phase 3)

Después de cada análisis el bot pregunta: *"¿quieres compartir los datos de este análisis de forma anónima?"*. Si el usuario acepta, se persiste en `contributions`:

- platform, risk_level, risk_score, phase_detected
- categories, pattern_ids (cuáles regex dispararon)
- source_type (text/audio/image), region (opcional)
- llm_used, override_triggered

**Lo que NO se guarda jamás:** texto, teléfono, identidad, hash, session_id. El modelo Pydantic tiene `extra="forbid"` que rechaza cualquier campo desconocido con HTTP 422 — defensa en profundidad contra leakage accidental.

El endpoint público `GET /contributions/stats` expone agregados (top patrones, distribución por región/plataforma). Esto convierte a Nahual en el primer dataset abierto sobre patrones de reclutamiento criminal digital en México.

## Privacy by Design

- **No se almacenan mensajes completos**, solo SHA-256 + resumen anonimizado
- **Alerta a tutor** contiene SOLO nivel de riesgo + plataforma, NUNCA el contenido
- **Audio/imagen** se procesan y se descartan — sólo el texto extraído entra al pipeline (después de confirmación explícita)
- **Contribuciones anónimas** rechazan campos desconocidos a nivel modelo (Pydantic `extra="forbid"`)
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

## Limitaciones conocidas

Nahual es un MVP de hackathon construido en 48 horas. Lo enviamos con una lectura honesta de lo que **no** hace todavía:

1. **No reemplaza a un profesional.** Nahual orienta, no diagnostica. PELIGRO siempre debe escalarse a Policía Cibernética 088, SIPINNA o un adulto de confianza. El bot lo dice explícitamente en cada mensaje crítico.
2. **Cobertura idiomática limitada.** El dataset (563 patrones) está calibrado para español mexicano informal. Variantes regionales (norteño, sureste) y otros países hispanohablantes tienen menor recall hasta enriquecer el dataset.
3. **Texto > multimedia.** STT (Whisper-large-v3) y OCR (Claude Vision) están integrados pero requieren confirmación explícita del usuario antes del análisis. El tunado fino para audios cortos con ruido o capturas borrosas queda fuera de alcance.
4. **Sin detección de deepfakes ni perfiles falsos.** Solo analizamos texto recibido. Verificación de identidad del emisor (cuentas falsas, suplantación) no es parte del pipeline.
5. **Falsos positivos posibles.** El score heurístico se basa en patrones léxicos. Mensajes irónicos, citas literarias, lirismo narcocultural sin intención real pueden disparar ATENCIÓN. Por eso el panel permite marcar "descartar" y eso retro-alimenta al auto-tuner.
6. **Falsos negativos posibles.** Lenguaje codificado nuevo (jerga emergente, emojis no catalogados) puede pasar inadvertido hasta que un operador lo reporte vía `/feedback`. La capa LLM mitiga esto en zona gris (0.3–0.6) pero no es infalible.
7. **Privacidad first, telemetría limitada.** No almacenamos mensajes originales, solo SHA-256 + resumen anonimizado. Esto significa que NO podemos auditar retroactivamente el texto que disparó una alerta — solo los pattern_ids que matchearon.
8. **Demo local, no producción.** El backend corre en SQLite (un archivo) y `uvicorn` sin reverse proxy. Para piloto real haría falta Postgres, autenticación OAuth (no API key estática), rate limiting por IP, y observabilidad (Sentry/Datadog).

Si encuentras un caso donde Nahual falla, abre un issue con el patrón redactado (sin PII) y lo agregamos al backlog del dataset.

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

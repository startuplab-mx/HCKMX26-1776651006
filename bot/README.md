# 🤖 Nahual Bot WhatsApp

Bot reactivo de WhatsApp construido con Baileys que actúa como **canal de
triage** para mensajes sospechosos de reclutamiento criminal o sextorsión.

## Estado en producción
- **Número:** `+52 844 538 7404`
- **Servicio systemd:** `nahual-bot.service`
- **Backend:** `http://localhost:8000` (FastAPI · misma máquina)

## Arquitectura

```
WhatsApp → Baileys (WebSocket) → messageHandler.js
                                  ├── audio  → /transcribe (Groq Whisper)
                                  ├── image  → /ocr (Claude Vision)
                                  └── text   → flowController.js (FSM)
                                               └── /alert (clasifica + persiste)
```

## State machine (`flowController.js`)

```
inicio → recibir_msg → analizando → result_safe / result_attention / notify
                                                                       ↓ (PELIGRO)
                                                               ask_contact → ask_contribute → ask_region → done
```

## Comandos universales (cualquier estado)

| Comando | Función |
|---|---|
| `menu` / `comandos` | Lista comandos |
| `ayuda` / `help` | Cómo funciona |
| `privacidad` / `datos` | Qué guarda y qué no |
| `estado` / `status` | Paso actual del flujo |
| `reset` / `reiniciar` | Empezar de cero |
| `reporte` / `pdf` | Descargar PDF último análisis |

## Cierres conversacionales (no dispara /analyze)

`gracias`, `ok`, `bye`, `listo`, `chido`, `sale`, `fin`, `ya`, `cuídate`,
`no`, `no gracias`, `estoy bien`, `nada más`, `ya no`, ... → respuesta
empática + `resetSession()`.

## Distress detection (empatía primero, análisis después)

`tengo miedo`, `estoy asustado/a`, `necesito ayuda`, `me quiero morir`
→ MENSAJES.distress (Línea de la Vida 800-911-2000 + 088 + invitación a
analizar).

## Privacy by design

- Texto original **NUNCA** persiste — solo SHA-256 hash + categorías
- Notificación al guardián: solo nivel de riesgo + plataforma + PDF
  oficial (sin contenido)
- Audios y capturas se procesan + descartan al instante (los bytes
  originales no llegan a SQLite)

## Setup local

```bash
cd bot
npm install
cp .env.example .env  # editar con BOT_BACKEND_URL + NAHUAL_API_KEY
node index.js
# Escanea el QR con WhatsApp → Dispositivos vinculados
```

## Variables de entorno

```
BOT_BACKEND_URL=http://localhost:8000
NAHUAL_API_KEY=nahual-hackathon-2026
LOG_LEVEL=info
BOT_SESSION_DIR=./auth_info_baileys
BOT_QR_FILE=./bot-qr.png  # opcional — QR como PNG
```

## Hardening

- **Reconnect con exponential backoff** (0.5s × 2^n, max 60s, ±25% jitter)
- **Cleanup de listeners viejos** antes de re-conectar (sin memory leak)
- **SIGTERM/SIGINT graceful shutdown** (1.5s en lugar de 90s default)
- **Per-JID rate limit** (5 alertas / 60s sliding window)
- **Session TTL eviction** (drop entries idle > 7d)
- **`fetchLatestBaileysVersion()`** al boot — Baileys 6.7.21 cacheaba
  versión deprecada del protocolo WhatsApp
- **`onWhatsApp()`** check antes de enviar al guardián (evita black-hole
  silencioso)

## Mensajes que edita Marco

`config/messages.js` — todo el texto user-facing en mexicano informal,
empático, no juicioso. Marco tiene priority sobre cualquier change a
ese archivo.

Ver el [README.md raíz](../README.md) para arquitectura completa.

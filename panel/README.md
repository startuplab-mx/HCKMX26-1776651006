# 📊 Nahual Panel Web

Single-file dashboard HTML + Tailwind CDN + Chart.js + vanilla JS.
Auto-refresh cada 5s. Hosted en producción en `http://159.223.187.6/`.

## Features

- **🧪 Probar el clasificador en vivo:** textarea + 4 botones de ejemplo
  (uno por fase) + Cmd/Ctrl+Enter shortcut. POST `/analyze` sin escribir
  a DB.
- **🔬 Deep healthcheck:** botón en header → modal con DB + Anthropic + Groq
  status (live ping, ~6s).
- **🚨 PELIGRO toast:** slide-in bottom-right + 880Hz audio cue + 8s
  auto-dismiss. Solo dispara para alertas con `id > last_seen_high_water_mark`.
- **📈 Risk timeline:** últimas 30 alertas con barras de color (verde
  <30%, amarillo <70%, rojo ≥70%).
- **📊 Stats cards:** Total / PELIGRO / ATENCIÓN / SEGURO / Pendientes /
  Escaladas con Chart.js timeseries (hour/day buckets).
- **⏸ Pause/resume:** toggle del auto-refresh para triagar sin clobber.
- **🛡️ Survey banner:** validación n=129 (92.3% / 19.2% / 73.1%).
- **📋 Tabla de alertas:** folio, fecha, plataforma, nivel, score, fase,
  override, status. Botones por fila: ✓ Revisar / ⚠️ Escalar / ✗ Descartar /
  🧠 ¿Por qué? / 📜 Legal / 🕑 Historial / 📄 PDF.
- **Mobile responsive:** overrides a partir de 640px.
- **Empty state:** mensaje cuando filtros sin match.
- **Connection state pill:** ok / reconectando / desconectado.

## Endpoints consumidos

```
GET  /health
GET  /stats
GET  /stats/timeseries
GET  /alerts                          (con X-API-Key)
GET  /alerts/{id}/history             (X-API-Key)
GET  /alerts/{id}/why                 (X-API-Key)
GET  /alerts/{id}/legal               (X-API-Key)
PATCH /alerts/{id}                    (X-API-Key)
POST /alerts/{id}/escalate            (X-API-Key)
GET  /admin/dataset-info              (público)
GET  /admin/healthcheck-deep          (público)
GET  /bayesian/stats                  (público)
GET  /contributions/stats             (público)
POST /analyze                         (manual analyze textbox)
```

## API base config (auto-detect)

A partir de `7970804` (Apr 26 2026) el panel **ya no necesita configuración
explícita** para distinguir local vs producción:

```js
// js/app.js
function _resolveApiBase() {
  if (typeof window.NAHUAL_API_URL === 'string') return window.NAHUAL_API_URL;
  const host = location.hostname;
  if (host === 'localhost' || host === '127.0.0.1' || host === '') {
    return 'http://localhost:8000';   // dev
  }
  return '';                          // prod → same-origin via Nginx
}
```

| Cómo se sirve el panel | API base resultante |
|---|---|
| `python -m http.server 3000` (local) | `http://localhost:8000` |
| Abrir `index.html` desde el filesystem | `http://localhost:8000` |
| Detrás de Nginx en `159.223.187.6` | `""` (relative → same-origin) |
| Override explícito | `<script>window.NAHUAL_API_URL = "https://api.example.com";</script>` |

> **Bug fix Apr 26:** versiones anteriores defaulteaban a `http://localhost:8000`
> incluso desde un browser remoto, lo que hacía que el panel **nunca se
> actualizara** en producción (cada `fetch()` pegaba al localhost del propio
> usuario). El boot banner en consola muestra qué base resolvió:
> `[nahual-panel] API base="(same-origin)" · refresh=5000ms · key=present`.

Override de la API key (endpoints protegidos `/alerts*`, `/sessions/*`, etc.):
- `<script>window.NAHUAL_API_KEY = '...'</script>` antes de `js/app.js`
- `localStorage.setItem('nahual_api_key', '...')` desde DevTools

## Setup local

```bash
cd panel
python -m http.server 3000
# o cualquier servidor estático: live-server, npx serve, etc.
```

Para que apunte a un backend remoto:
```html
<script>window.NAHUAL_API_URL = "http://159.223.187.6";</script>
```

## Filosofía de diseño

- **Single-file HTML** (`index.html`) + un archivo `js/app.js` + zero
  build step. Tailwind via CDN, Chart.js via jsDelivr.
- **Privacy first:** no logging analytics, no third-party scripts más
  allá de Tailwind/Chart.js, no PII renderizada (solo folios + scores +
  metadata).
- **Operability:** todo el panel funciona sin JS pesado — funciona en
  laptop modesta + conexión 3G. La sección manual-analyze + deep-check
  son las únicas que requieren respuesta del backend.

## Source

- `index.html` — markup + Tailwind classes inline + survey banner
- `js/app.js` — fetch logic + render + auto-refresh + manual analyze +
  deep check modal + PELIGRO toast + pause control

Ver [README.md raíz](../README.md) para arquitectura completa.

# 🛡️ NAHUAL — BIBLIA OPERATIVA DEFINITIVA
## Documento Integral: Arquitectura + Investigación + Operaciones + Criterios
### Hackathon 404: Threat Not Found | 24-26 Abril 2026
### Equipo Vanguard | Armando Flores (Dev) + Marco Espinosa (Clinical/UX/Legal/Pitch)

---

> **"Nahual detecta manipulación digital antes de que escale a daño real"**

---

# ÍNDICE

1. Decisiones de Arquitectura (Actualizadas)
2. Identidad Visual
3. Arquitectura del Sistema (Con Extensión)
4. Clasificador de Reclutamiento Criminal (4 Fases + Override)
5. Dataset Completo de Keywords (NAHUAL2 Integrado)
6. Bot de WhatsApp (Flujo + UX + Manejo Multimedia)
7. Nahual Shield — Extensión de Navegador
8. Panel Web
9. API REST
10. Reporte PDF
11. Investigación de Respaldo (NAHUAL1 Integrado)
12. Marco Legal y Protocolos
13. Plan Operativo de Marco (Completo)
14. Roadmap Hora por Hora (Ambos)
15. Estrategia de Validación (Encuestas + Mentorías)
16. Pitch — Script Completo
17. Mapping: Criterios de Convocatoria vs. Nahual
18. Estrategia de Commits
19. Documentación de IA
20. Checklist Final de Entregables

---

# 1. DECISIONES DE ARQUITECTURA (ACTUALIZADAS)

| # | Decisión | Elección |
|---|----------|----------|
| 1 | **Enfoque del Sistema** | **HÍBRIDO PROACTIVO:** Bot WA (reactivo) + Extensión navegador Nahual Shield (proactivo) + API pública. La extensión ES componente crítico, no bonus — Armando ya tiene los extractores de DOM para Instagram, WhatsApp Web y Discord. |
| 2 | Canal principal | WhatsApp (Baileys) |
| 3 | Clasificador | Heurístico (Capa 1) + Claude API (Capa 2 zona gris) + **Override Fase 3/4** |
| 4 | Dataset | Híbrido: investigación NAHUAL2 + validación Marco + jerga real MX |
| 5 | Rol Marco | **DUEÑO de:** Lenguaje + Validación + Narrativa + Legal + Presentación |
| 6 | Base de código | Repo limpio. Sprint pre-desarrollo completado. |
| 7 | Demo | Video pregrabado + demo en vivo corriendo de fondo + IA apoya en edición |

---

# 2. IDENTIDAD VISUAL

**Logotipo Nahual Nodal:** Glifo abstracto mesoamericano estilizado — red de nodos y líneas de datos geométricos formando la silueta de un jaguar.

**Cromática:**
- **Carbón Profundo (#2F353A):** Seguridad, sobriedad técnica
- **Cobre Terracota (#C16A4C):** Alerta, acción, raíz cultural mexicana
- **Blanco (#FFFFFF):** Texto sobre fondos oscuros
- **Verde Semáforo (#22C55E):** Estado seguro
- **Amarillo Semáforo (#EAB308):** Estado atención
- **Rojo Semáforo (#EF4444):** Estado peligro

Aplicar en: panel web, PDF de reporte, slides si se necesitan, README header.

---

# 3. ARQUITECTURA DEL SISTEMA

```
┌────────────────────────────────────────────────────────────────────┐
│                      CANALES DE ENTRADA                            │
│                                                                    │
│  ┌──────────────┐  ┌────────────────────┐  ┌───────────────────┐  │
│  │  Bot WhatsApp │  │  Nahual Shield     │  │  API Directa      │  │
│  │  (REACTIVO)   │  │  Extensión Chrome  │  │  POST /analyze    │  │
│  │  Node.js +    │  │  (PROACTIVO)       │  │  [Público]        │  │
│  │  Baileys      │  │  MutationObserver  │  │                   │  │
│  │               │  │  + Mini-Regex      │  │                   │  │
│  └──────┬───────┘  └────────┬───────────┘  └────────┬──────────┘  │
│         │                   │                       │             │
│         └───────────────────┼───────────────────────┘             │
│                             │                                     │
│                    HTTP POST /analyze                              │
└─────────────────────────────┼─────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     BACKEND CORE (FastAPI :8000)                  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              PIPELINE DE ANÁLISIS                          │  │
│  │                                                            │  │
│  │  Texto → Preprocesamiento → Capa 1: Heurístico            │  │
│  │                                  │                         │  │
│  │                          Score ≥ 0.8 en Fase 3/4?          │  │
│  │                            │            │                  │  │
│  │                           SÍ           NO                  │  │
│  │                            │            │                  │  │
│  │                            ▼            ▼                  │  │
│  │                     OVERRIDE →    Zona gris (0.3-0.6)?     │  │
│  │                     Score = 1.0      │         │           │  │
│  │                     PELIGRO         SÍ        NO           │  │
│  │                     INMINENTE        │         │           │  │
│  │                                      ▼         ▼           │  │
│  │                              Capa 2: Claude  Retornar      │  │
│  │                              API (5s timeout) resultado    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [SQLite DB]  [PDF Engine]  [Webhook Engine]  [Swagger /docs]    │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     PANEL WEB (:3000)                             │
│  Dashboard alertas + Stats + Semáforo + Descarga PDF             │
└──────────────────────────────────────────────────────────────────┘
```

## Estructura del Repositorio

```
nahual/
├── README.md
├── LICENSE (MIT)
├── .env.example
├── docs/
│   ├── arquitectura.png
│   ├── flujo-bot.png
│   ├── wireframes/
│   ├── protocolo-legal.md
│   └── investigacion/
│       ├── NAHUAL1-investigacion-completa.md
│       └── NAHUAL2-dataset-keywords.md
├── bot/
│   ├── package.json
│   ├── index.js
│   ├── handlers/
│   │   ├── messageHandler.js
│   │   ├── flowController.js
│   │   └── alertDispatcher.js
│   ├── config/
│   │   └── messages.js          ← MARCO EDITA ESTO
│   └── utils/
│       ├── textExtractor.js
│       └── sessionManager.js
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   ├── classifier/
│   │   ├── heuristic.py
│   │   ├── llm_layer.py
│   │   ├── pipeline.py          ← Incluye lógica Override
│   │   └── keywords/
│   │       ├── phase1_captacion.json
│   │       ├── phase2_enganche.json
│   │       ├── phase3_coercion.json
│   │       ├── phase4_explotacion.json
│   │       └── emojis_narco.json
│   ├── database/
│   ├── reports/
│   └── tests/
├── extension/                   ← NAHUAL SHIELD
│   ├── manifest.json
│   ├── content.js               ← MutationObserver + mini-regex
│   ├── popup.html
│   ├── popup.js
│   └── styles.css
├── panel/
│   ├── index.html
│   └── js/
└── scripts/
    ├── seed_test_data.py
    └── demo_scenario.py
```

---

# 4. CLASIFICADOR — REGLA DE OVERRIDE

## Lógica de Override (Cortocircuito Crítico)

Cuando el clasificador detecta un score individual ≥ 0.80 en Fase 3 (Coerción) o Fase 4 (Explotación), el sistema ignora el promedio ponderado estándar y eleva automáticamente el risk_score global a 1.00 (PELIGRO INMINENTE).

**Justificación:** El reclutamiento criminal NO es lineal. Un agresor puede saltar directamente a la amenaza ("ya sabes dónde vives tu familia") sin pasar por captación ni enganche. El promedio ponderado subestima estos casos. El override los atrapa.

```python
# En pipeline.py
def classify(self, text):
    scores = self.heuristic.classify(text)
    
    # OVERRIDE: Fase 3 o 4 con score ≥ 0.80 → PELIGRO INMINENTE
    if scores['phase3'] >= 0.80 or scores['phase4'] >= 0.80:
        return {
            'risk_score': 1.0,
            'risk_level': 'PELIGRO',
            'override': True,
            'dominant_phase': 'coercion' if scores['phase3'] >= 0.80 else 'explotacion',
            ...
        }
    
    # Scoring normal ponderado
    total = scores['phase1']*0.15 + scores['phase2']*0.25 + scores['phase3']*0.35 + scores['phase4']*0.25
    ...
```

---

# 5. DATASET COMPLETO DE KEYWORDS (NAHUAL2 INTEGRADO)

## Fuentes Verificadas

Todos los patrones provienen de fuentes documentadas:
- **Colmex (Dr. Rodrigo Peña):** 100 cuentas TikTok analizadas, emojis codificados (🍕=Chapiza/Sinaloa, 🐓=CJNG/Mencho)
- **El País México (sep 2025):** Testimonios del Rancho Izaguirre/La Vega, ofertas de "corte de agave", "guardia de seguridad", "te pago el viaje"
- **FinCEN (sep 2025):** Red flags de sextorsión financiera
- **Swissinfo/EFE (mar 2026):** Lenguaje digital de cárteles, "yo quiero jale"
- **CSIS (may 2025):** Uso de algoritmos de TikTok para reclutamiento

## Emojis Codificados por Cártel

| Emoji | Significado | Fuente | Confianza |
|-------|------------|--------|-----------|
| 🍕 | Cartel de Sinaloa ("Chapiza") | Colmex/Swissinfo | Confirmado |
| 🐓 | CJNG (Nemecio "Mencho") | Colmex/Swissinfo | Confirmado |
| 🔫💰💎 | Narcocultura genérica | CSIS/Infobae | Alto |
| 🤑💀🖤 | Glorificación violencia/dinero | Derivado | Medio |
| 🦅⚡🏴‍☠️ | Identidad criminal | Derivado | Medio |
| 🤝🔒 | Acuerdo/secreto | Sintético | Bajo (evaluar en contexto) |

## Keywords por Fase (Selección del NAHUAL2)

### Fase 1 — Captación
- "Yo quiero jale" (peso 0.9, Swissinfo/Colmex)
- "trabajo cortando agave" (0.7, El País 2025)
- "guardia de seguridad" (0.7, El País 2025)
- "te pago el viaje" / "boleto de autobús incluido" (0.8, El País 2025)
- "instalar cámaras de vigilancia" (0.6, El País 2025)
- "$X,000 semanales/diarios" (0.7, Colmex)
- "el jale", "la chamba", "el movimiento" (0.6)
- Corridos tumbados como aspiración (0.4)

### Fase 2 — Enganche
- "dónde vives", "qué colonia", "de dónde eres" (0.5)
- "pásate a Signal/Telegram/privado" (0.6)
- "no le digas a nadie", "manténlo en secreto" (0.6)
- "confía en mí", "yo te cuido" (0.3)
- "necesitas dinero/lana/feria" (0.4)
- "peleas con la familia", "no tengo dinero" (0.4, sintético)
- "envía tu ubicación" (0.7)

### Fase 3 — Coerción
- "vas a ser sicario" (0.9, El País 2025)
- "si intentas escapar te descuartizo" (1.0, El País 2025)
- "ya sabes demasiado" / "ya estás adentro" (0.7)
- "te vamos a buscar" / "sabemos dónde vives" (0.9)
- "levantón", "tronar", "dar piso" (0.8)
- "última oportunidad" (0.5)

### Fase 4 — Explotación
- "ve al punto", "recoge esto", "echa aguas" (0.6)
- "trae a tus compas" (reclutamiento secundario, 0.7)
- "manda fotos/videos/nudes" (sextorsión, 0.7)
- "deposita $X", "gift card", "SPEI" (0.6-0.7)
- "no traigas celular", "te van a recoger" (0.7)

### Heurísticas Anti-Falsos Positivos (NAHUAL2)
- Un solo patrón de bajo peso NO dispara alerta
- Verificar contexto cruzado: "trabajo" sola no basta, necesita indicadores fuertes
- Listas blancas de frases inocuas ("estoy trabajando ahora" ≠ "quiero jale")
- Mensajes de contactos confiables bajan score
- Regex con variantes leet: t[rk][a4]b[aj]0 para "trabajo"

---

# 6. BOT DE WHATSAPP — ACTUALIZADO

## Optimización de Latencia (Modificación Marco)

- **Mensaje instantáneo de confirmación:** Al recibir texto para análisis, el bot envía inmediatamente: "Recibido. Esto requiere un análisis detallado, dame unos segundos... 🔍"
- **Timeout de 5 segundos** para Capa 2 (Claude API). Si excede, corta y entrega resultado Capa 1.
- **Fallback garantizado:** En NINGÚN caso el bot se queda sin respuesta.

## Manejo de Contenido Multimedia

El bot rechaza audio, imágenes y stickers con mensaje empático:

> "Aún estoy entrenando mis ojos y oídos 🙈. Por ahora, por favor envíame tu reporte en texto o cópiame lo que te escribieron para poder ayudarte."

## Máquina de Estados (Sin cambios — ver doc anterior)

INICIO → BIENVENIDA → RECIBIR_MSG → ANALIZANDO → RESULT_* → (ASK_CONTACT → NOTIFY →) GEN_REPORT → INICIO

---

# 7. NAHUAL SHIELD — EXTENSIÓN DE NAVEGADOR

## Decisión Actualizada

La extensión es COMPONENTE CRÍTICO, no roadmap. Armando ya tiene extractores de DOM funcionales para Instagram, WhatsApp Web y Discord.

## Mecanismo

1. **MutationObserver** monitorea el DOM de plataformas específicas
2. **Procesamiento Local (Zero-Trust):** Mini-base de regex local con patrones de mayor riesgo (Fases 3 y 4)
3. **Al detectar coincidencia:**
   - **Overlay UI:** Panel de alerta recomendando atención inmediata
   - **Deep Link:** Botón que abre WhatsApp con el número del bot pre-cargado con reporte inicial
4. **Cumplimiento legal:** No intercepta comunicaciones (Art. 16 CPEUM). Solo analiza lo visible en pantalla del usuario que instaló la extensión.

## Plataformas Soportadas

| Plataforma | DOM Extractor | Estado |
|------------|--------------|--------|
| WhatsApp Web | ✅ Existente | Integrar |
| Instagram Web | ✅ Existente | Integrar |
| Discord Web | ✅ Existente | Integrar |
| TikTok Web | ❌ Pendiente | Roadmap post-hackathon |

## Manifest V3

```json
{
  "manifest_version": 3,
  "name": "Nahual Shield",
  "version": "1.0.0",
  "description": "Detección proactiva de reclutamiento criminal digital",
  "permissions": ["activeTab"],
  "content_scripts": [{
    "matches": [
      "*://web.whatsapp.com/*",
      "*://www.instagram.com/*",
      "*://*.discord.com/*"
    ],
    "js": ["content.js"],
    "css": ["styles.css"]
  }],
  "action": {
    "default_popup": "popup.html"
  }
}
```

---

# 8-10. PANEL WEB + API REST + REPORTE PDF

(Sin cambios respecto al documento anterior — ver Nahual_Arquitectura_Roadmap_Completo.docx Partes V, VI, VII)

Panel: HTML + Tailwind + auto-refresh 5s. Colores: Carbón #2F353A + Cobre #C16A4C.

API: POST /analyze, POST /alert, GET /alerts, GET /stats, POST /report/{id}, GET /health, GET /docs.

PDF: Folio NAH-2026-XXXX, datos del incidente, análisis, recomendaciones, marco legal, contactos 088.

---

# 11. INVESTIGACIÓN DE RESPALDO (NAHUAL1 INTEGRADO)

## Datos Clave para Pitch y README

**México:**
- En 2024, entre 388 y 460 mil menores fueron reclutados por el crimen organizado (REDIM)
- 46,000 menores reportaron ser obligados a unirse a pandillas (ONC 2015)
- En 2026, Cámara de Diputados reformó Código Penal: hasta 18 años de pena por reclutamiento de menores
- La ONU activó mecanismo excepcional por desapariciones vinculadas a captación digital

**Digital:**
- 50% de videos de reclutamiento en TikTok se publicaron DESPUÉS del descubrimiento del Rancho Izaguirre (Colmex)
- Los cárteles ofrecen hasta $15,000 pesos semanales vs. salario mínimo de $315/día
- 27% de menores en pandillas de Ecuador fueron reclutados vía redes sociales (2025)
- Las plataformas (Meta, TikTok) redujeron sus equipos de moderación de contenido en 2025

**Legal (México):**
- Art. 16 CPEUM: Comunicaciones privadas son inviolables sin orden judicial
- Nahual solo analiza datos AUTOINFORMADOS por el usuario
- LGDNNA (Ley General de Derechos de NNA): Protección integral
- LFPDPPP: Protección de datos personales
- Ley Olimpia: En casos de sextorsión

**Fuentes verificadas:** REDIM, CNDH, ONC, Colmex, UNICEF México, Swissinfo/EFE, El País, CSIS, FinCEN, Infobae, Proceso, Milenio.

---

# 12. MARCO LEGAL Y PROTOCOLOS

## A Quién Denunciar

| Autoridad | Contacto | Cuándo |
|-----------|----------|--------|
| Policía Cibernética | 088 | Cualquier riesgo digital |
| Fiscalía General | Local según estado | Delitos graves / amenazas |
| SIPINNA | sipinna.gob.mx | Vulneración de derechos de NNA |
| DIF | Local según estado | Menores en situación de riesgo |
| Línea de la Vida | 800-911-2000 | Crisis emocional |

## Artículos de Ley Aplicables

- **Art. 47 LGDNNA:** Protección contra reclutamiento de menores
- **Art. 16 CPEUM:** Inviolabilidad de comunicaciones (Nahual cumple: solo analiza datos autoinformados)
- **Código Penal Federal (reforma 2026):** Hasta 18 años por reclutamiento de menores
- **Ley Olimpia:** Difusión no consentida de material íntimo (en casos de sextorsión)
- **LFPDPPP:** Protección de datos personales de menores

---

# 13. PLAN OPERATIVO DE MARCO (COMPLETO)

## Principio Operativo

**Marco NO es apoyo. Marco es DUEÑO de: Lenguaje + Validación + Narrativa + Legal + Presentación.**

Cada bloque de trabajo debe producir: algo visible, algo medible, algo usable en pitch/demo. Si no cumple eso → es pérdida de tiempo.

## Pre-Hackathon — Entregables Obligatorios

| # | Entregable | Formato | Estado |
|---|-----------|---------|--------|
| 1 | messages.js COMPLETO | Archivo JS con todos los mensajes del bot | |
| 2 | Dataset humano inicial | Frases reales, emojis, variantes, falsos positivos | |
| 3 | Protocolo legal | protocolo-legal.md con SIPINNA, 088, Ley Olimpia | |
| 4 | Encuesta Google Form | Anónima, lista para enviar | ✅ Enviada |
| 5 | Guion pitch v1 | Hook + problema + solución + cierre | |
| 6 | Wireframe extensión | Flujo visual simple | |

## Viernes — Observar y Ajustar

**Objetivo: No construir. Entender.**

| Tarea | Output |
|-------|--------|
| Tomar datos de CADA charla (cifras exactas, nombres, artículos) | Lista de datos para pitch |
| Detectar lenguaje clave que usa el jurado | Ajustes de vocabulario |
| Probar bot como usuario (5+ mensajes variados) | Lista de mejoras en lenguaje |
| Ajustar messages.js en tiempo real | Versión 2 de mensajes |

## Sábado — Día Crítico

| Bloque | Hora | Tarea | Output |
|--------|------|-------|--------|
| 1 | 08:15-09:30 | Validar keywords del clasificador con jerga real | Dataset refinado |
| 2 | 10:00-12:00 | Testing: 10+ mensajes simulados, anotar falsos +/- | Bug report + ajustes |
| 3 | 11:00-11:45 | MENTORÍA #1 (ciberseguridad) — tomar notas | Feedback documentado |
| 4 | 13:30-15:00 | Encuestas: recolectar + análisis preliminar con IA | Métricas de validación |
| 5 | 15:00-17:00 | Contenido legal final para PDF + testing final bot | PDF content + mensajes v3 |
| 6 | 16:30-17:15 | MENTORÍA #2 (impacto social) — tomar notas | Feedback #2 documentado |

**Output del día:** Dataset refinado, mensajes pulidos, insights reales, 2 feedbacks documentados, métricas de encuesta.

## Domingo — Cierre

| Bloque | Hora | Tarea | Output |
|--------|------|-------|--------|
| 1 | 08:00-09:00 | Script FINAL del pitch | Guion cronometrado |
| 2 | 09:15-10:00 | Narración del video demo (Marco narra o actúa como "menor") | Audio/participación en video |
| 3 | 10:00-10:45 | README no técnico: secciones de problema, impacto, legal | Secciones del README |
| 4 | 10:45-11:30 | Diagramas + wireframes finales al repo | Archivos en docs/ |
| 5 | 13:00-14:00 | Ensayo pitch x3 CRONOMETRADO | Pitch dominado |

## Responsabilidad en Pitch

| Quién | Cuándo | Qué |
|-------|--------|-----|
| **Marco ABRE** | 0:00-1:00 | Hook emocional + problema cuantificado |
| **Armando** | 1:00-4:00 | Demo en vivo + explicación técnica |
| **Marco CIERRA** | 4:00-5:00 | Impacto social + conexión institucional + cierre |

## Validación — Lo que Marco DEBE entregar

| Métrica | Fuente | Para qué |
|---------|--------|---------|
| % de jóvenes expuestos a mensajes sospechosos | Encuesta | Pitch: "X% de adolescentes en Saltillo han recibido..." |
| % que no identifican riesgo | Encuesta | Pitch: "Solo X% reconoce señales de reclutamiento" |
| % que usarían Nahual | Encuesta | Pitch: "X% dijo que usaría una herramienta como esta" |
| Feedback de 2 mentores | Mentorías evento | Criterio Validación del jurado |

## Reglas para Marco

**NO hacer:** código complejo, tareas técnicas pesadas, cosas que no producen output visible.

**SÍ hacer:** mejorar lenguaje, validar con usuarios, fortalecer narrativa, documentar todo.

**Backup tasks (si termina todo):** refinar mensajes, mejorar dataset, consolidar encuestas, mejorar pitch, crear visuales.

---

# 14. ROADMAP HORA POR HORA (AMBOS)

## DÍA 1 — Viernes 24 (15:00-20:00)

| Hora | Armando | Marco |
|------|---------|-------|
| 15:00-16:00 | Registro + kit | Registro + kit |
| 16:00-17:30 | Escuchar charlas. Tomar notas técnicas. | Tomar CADA dato, cifra, nombre. Detectar vocabulario del jurado. |
| 17:30-18:15 | Refinar propuesta si hay insights nuevos | Networking. Identificar mentores potenciales. |
| 18:15-19:00 | **HACK:** Verificar bot+backend en venue. Primer commit. | Probar bot como usuario. 5+ mensajes. Anotar mejoras. |
| 19:00-19:45 | **HACK:** Integrar flujo conversacional completo | Ajustar messages.js en tiempo real según feedback |
| 19:45-20:00 | Commit #1, #2 | Documentar avance en README |

## DÍA 2 — Sábado 25 (08:00-20:00)

| Hora | Armando | Marco |
|------|---------|-------|
| 08:00-08:15 | Check-in avance | Presentar avance |
| 08:15-09:30 | **HACK:** Clasificador 4 fases + Override | Validar keywords: ¿suenan naturales? ¿Falta jerga? |
| 09:30-10:00 | Commit #3 | Ajustar dataset |
| 10:00-11:00 | **HACK:** Capa 2 LLM + timeout 5s + fallback | Preparar preguntas mentoría ciberseg |
| 11:00-11:45 | **MENTORÍA #1** ciberseguridad | **MENTORÍA #1** — acompañar, tomar notas |
| 11:45-12:00 | Commit #4 | Registrar feedback |
| 12:00-13:00 | **HACK:** Panel web — stats + tabla + semáforo (colores Nahual) | Testing: 10+ mensajes variados |
| 13:00-13:30 | Almuerzo | Almuerzo |
| 13:30-14:30 | **HACK:** Extensión Nahual Shield — integrar extractores DOM | Encuestas: recolectar + análisis preliminar |
| 14:30-15:00 | Commit #5 | Consolidar métricas encuesta |
| 15:00-16:00 | **HACK:** PDF generator + webhook alerta silenciosa | Contenido legal final del PDF |
| 16:00-16:30 | **HACK:** Extensión — overlay UI + deep link a WhatsApp bot | Preparar preguntas mentoría impacto social |
| 16:30-17:15 | **MENTORÍA #2** impacto social | **MENTORÍA #2** — presentar flujo, pedir feedback |
| 17:15-17:30 | Commit #6 | Registrar feedback #2 |
| 17:30-18:30 | Checkpoint + **HACK:** API docs, /stats, edge cases | README secciones no-técnicas |
| 18:30-19:30 | **HACK:** Extensión — testing en las 3 plataformas | Testing final bot como usuario |
| 19:30-20:00 | Testing end-to-end. Fix bugs. Commit #7. | Pitch v2 con datos de encuestas + mentorías |

## DÍA 3 — Domingo 26 (08:00-17:30)

| Hora | Armando | Marco |
|------|---------|-------|
| 08:00-09:15 | Fix bugs. Pulir UI. Seed data demo. | Script FINAL pitch. Ensayar solo. |
| 09:15-10:00 | Extensión: últimos fixes + testing | Diagramas arquitectura (Figma/papel) |
| 10:00-10:45 | Grabar video demo (2 min) | Marco narra / actúa como "menor" en demo |
| 10:45-11:30 | README final. Verificar repo cloneable. | Subir wireframes, protocolo legal, diagramas |
| 11:30-12:00 | **SUBIR TODO A GITHUB.** | Verificar video subido y linkado |
| 12:00-13:00 | Taller pitch | Taller pitch |
| 13:00-14:00 | Ensayar pitch x3 CRONOMETRADO | Marco abre + cierra. Armando demo. |
| 14:00-16:30 | **EVALUACIÓN EN MESA + DEMODAY** | Demo corriendo de fondo. Marco: hook + impacto. |
| 16:30-17:30 | Premiación + networking | Intercambiar contactos mentores y jurados |

---

# 15. ESTRATEGIA DE VALIDACIÓN

## Encuestas (Ya Lanzadas)

- **Plataforma:** Google Form
- **Target:** Estudiantes de secundaria y prepa en Saltillo/Monterrey
- **Objetivo:** 400+ respuestas
- **Preguntas clave:**
  - ¿Has recibido mensajes de desconocidos ofreciéndote trabajo o dinero en redes sociales?
  - ¿Sabrías identificar si alguien te está intentando reclutar?
  - ¿Usarías una herramienta que analice mensajes sospechosos por ti?
- **Análisis:** Marco + IA consolidan resultados para incluir en pitch

## Mentorías (Criterio de Validación del Jurado)

La convocatoria pregunta explícitamente: "¿El equipo comprobó su solución con partes interesadas durante el evento?"

- **Mentoría #1 (Sábado AM):** Mentor de ciberseguridad. Preguntar sobre la arquitectura, la privacidad, los patrones de detección.
- **Mentoría #2 (Sábado PM):** Mentor de impacto social/legal. Preguntar sobre el flujo del bot, el lenguaje, la conexión con protocolos reales.
- **Documentar AMBAS** con: nombre del mentor, feedback recibido, cambios implementados.
- En el pitch mencionar: "Validamos nuestra solución con X mentores durante el evento y ajustamos Y basándonos en su feedback."

---

# 16. PITCH — SCRIPT COMPLETO (5 MINUTOS)

## MARCO (0:00 – 1:00) — Hook + Problema

"En marzo de 2025 se descubrió el Rancho Izaguirre en Jalisco. Un campo de adiestramiento del CJNG donde jóvenes reclutados por TikTok eran entrenados a la fuerza. Los que no aprobaban, eran asesinados.

El Colegio de México analizó 100 cuentas de TikTok y descubrió que los cárteles han construido un lenguaje digital completo: emojis, corridos tumbados, ofertas de $15,000 semanales.

[DATO DE ENCUESTA] X% de los adolescentes que encuestamos en Saltillo han recibido mensajes de desconocidos ofreciéndoles trabajo o dinero. Solo Y% reconoce las señales de reclutamiento.

El reclutamiento ya no ocurre en la esquina. Ocurre en el teléfono de tu hijo. Y hoy, no existe una sola herramienta en México que detecte estas señales."

## ARMANDO (1:00 – 4:00) — Solución + Demo

"Nahual es un sistema de detección de reclutamiento criminal digital. Tiene dos modos:

REACTIVO: [DEMO] Un adolescente pega un mensaje sospechoso en nuestro bot de WhatsApp. El clasificador detecta las 4 fases del reclutamiento. Si hay peligro, activa una alerta silenciosa al adulto y genera un reporte para la Policía Cibernética.

PROACTIVO: [DEMO EXTENSIÓN] Nahual Shield, nuestra extensión de navegador, monitorea chats de WhatsApp Web, Instagram y Discord en tiempo real. Cuando detecta patrones de riesgo, muestra una alerta y ofrece reportar directamente al bot.

Los patrones están basados en el estudio del Colegio de México sobre reclutamiento en TikTok, testimonios judiciales del Rancho Izaguirre, y red flags de FinCEN.

La API es pública, documentada con Swagger, y open source. Cualquier plataforma puede integrar la detección."

## MARCO (4:00 – 5:00) — Impacto + Cierre

"Como estudiante de Medicina, validé cada mensaje que Nahual envía. Un adolescente asustado no necesita un manual. Necesita que alguien le diga: no estás solo.

El reporte incluye los artículos de ley, los protocolos de SIPINNA, y el número de la Policía Cibernética. No es un prototipo académico — es algo que un maestro de secundaria puede usar mañana.

Validamos con [X] mentores durante el evento y encuestamos a [N] adolescentes. Los datos confirman que el problema es real y la herramienta es necesaria.

Nahual no es otra IA genérica. Es el primer sistema en México diseñado para detectar reclutamiento criminal digital antes de que el menor desaparezca.

Gracias."

---

# 17. MAPPING: CRITERIOS DE CONVOCATORIA vs. NAHUAL

## Fase 1: Criterios de Selección (Para entrar a los 20)

| Criterio | Score esperado | Cómo lo cubrimos |
|----------|---------------|------------------|
| Equipo (1-5) | 4/5 | Armando: bots WA en producción (AUCTORUM). Marco: Medicina + validación clínica. Debilidad: solo 2 personas. |
| Originalidad (1-5) | 5/5 | Único proyecto enfocado en reclutamiento criminal digital (no grooming genérico). Extensión proactiva. Basado en estudio Colmex. |
| Claridad (1-5) | 5/5 | 3 capas definidas: bot reactivo + extensión proactiva + API. En 60 segundos se entiende. |
| Factibilidad (1-5) | 5/5 | Stack que Armando domina. Clasificador heurístico sin GPU. Extensión con extractores existentes. |
| Registro completo (1-5) | 5/5 | Datos completos de ambos integrantes. |

## Fase 2: Criterios de Evaluación Final (Para ganar)

| Criterio | Pregunta del jurado | Cómo lo cubrimos | Responsable |
|----------|-------------------|------------------|-------------|
| Problema | ¿Aborda directamente la problemática? | Reclutamiento criminal digital = tema central del hackathon + Q&A. Datos del Colmex, REDIM, ONU. | Marco (pitch) |
| Ejecución | ¿Prototipo funcional demostrable? | Bot + extensión + panel + PDF funcionando en demo en vivo. | Armando (demo) |
| Viabilidad | ¿Usuarios/clientes potenciales reales? | Encuesta con N adolescentes. Padres, escuelas (250,000 en MX), plataformas via API. | Marco (encuesta) |
| **Validación** | ¿Comprobó con partes interesadas DURANTE evento? | 2 mentorías documentadas + encuesta + testing con usuarios simulados. | Marco (mentorías) |
| Presentación | ¿Clara, precisa, convincente? | Script de 5 min ensayado 3+ veces. Marco abre/cierra. Demo en vivo. | Ambos |
| Factibilidad | ¿Implementable a escala? | API pública MIT. Extensión distribuible via Chrome Web Store. Bot replicable. | Armando (técnica) |

## Entregables Requeridos vs. Estado

| Entregable | Requerido | Quién | Estado |
|-----------|-----------|-------|--------|
| Código fuente en repo | ✅ Obligatorio | Armando | Pendiente (durante evento) |
| README documentado | ✅ Obligatorio | Ambos | Pendiente |
| Video demo ≤ 2 min | ✅ Obligatorio | Ambos | Pendiente |
| Materiales de diseño (wireframes, mockups, diagramas) | ✅ Obligatorio | Marco + Armando | Wireframes en progreso |
| Documentación IA usada | ✅ Obligatorio | Armando | Template listo |
| Historial de commits | ✅ Verificado por comité integridad | Armando | Estrategia definida |

## Normas Técnicas — Cumplimiento

| Norma | Cumple | Notas |
|-------|--------|-------|
| Todo desarrollo durante el evento (o especificar qué existía antes) | ✅ | README documenta: "Pre-desarrollo: estructura, dependencias, dataset. Todo el código funcional durante el evento." |
| Tecnología libre | ✅ | Node.js, Python, HTML, Chrome Extension — todo libre |
| Documentar IA usada | ✅ | Sección dedicada en README |
| Apps web en navegadores principales | ✅ | Panel web + extensión Chrome/Edge |
| No contenido prohibido | ✅ | |
| Licencia MIT en repo | ✅ | LICENSE file incluido |

---

# 18. ESTRATEGIA DE COMMITS

| Día | Hora | Commit |
|-----|------|--------|
| Vie | 18:30 | "Initial setup: bot connection + API health" |
| Vie | 19:45 | "feat: conversational flow with state machine" |
| Sáb | 09:30 | "feat: 4-phase classifier with override logic" |
| Sáb | 11:45 | "feat: Claude API layer with 5s timeout" |
| Sáb | 14:30 | "feat: web dashboard + Nahual Shield extension v1" |
| Sáb | 17:15 | "feat: PDF reports + silent alert system" |
| Sáb | 20:00 | "fix: edge cases + extension testing on 3 platforms" |
| Dom | 09:15 | "polish: UI + demo data + extension overlay" |
| Dom | 10:45 | "docs: video demo + architecture diagrams" |
| Dom | 11:30 | "docs: README complete + AI disclosure + legal protocols" |
| Dom | 11:55 | "final: last review before deadline" |

---

# 19. DOCUMENTACIÓN DE IA

(Para el README — sección obligatoria)

**Claude Code:** Asistente de programación para boilerplate. Todo el código revisado e integrado manualmente. La lógica del clasificador (patrones, keywords, fases) fue investigada y definida por el equipo basándose en fuentes verificadas.

**Claude API:** Capa 2 del clasificador para análisis contextual en zona gris. Componente funcional del producto. El sistema funciona sin esta capa.

**Principio:** El clasificador heurístico (Capa 1) funciona sin IA. La Capa 2 es opcional. El sistema es fundamentalmente creado por el equipo; la IA es un componente, no el producto.

---

# 20. CHECKLIST FINAL

| # | Entregable | Quién | ✓ |
|---|-----------|-------|---|
| 1 | Código fuente en repo hackathon | Armando | |
| 2 | README.md completo | Ambos | |
| 3 | LICENSE (MIT) | Armando | |
| 4 | Video demo ≤ 2 min | Ambos | |
| 5 | Wireframes extensión | Marco | |
| 6 | Diagrama arquitectura | Marco | |
| 7 | Screenshots panel | Marco | |
| 8 | 11+ commits descriptivos | Armando | |
| 9 | Documentación IA | Armando | |
| 10 | PDF de ejemplo | Armando | |
| 11 | API /docs (Swagger) | Armando (auto) | |
| 12 | Dataset keywords en /keywords/ | Marco + Armando | |
| 13 | protocolo-legal.md | Marco | |
| 14 | Pitch ensayado 3+ veces | Ambos | |
| 15 | Encuesta resultados | Marco | |
| 16 | Feedback mentores documentado | Marco | |
| 17 | Extensión Nahual Shield | Armando | |
| 18 | Investigación NAHUAL1 + NAHUAL2 en docs/ | Marco | |

---

> **A COOKEAR. CON TODO. 🛡️🔥**

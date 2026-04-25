# Documentación de uso de IA — Nahual

> Requisito obligatorio de la convocatoria Hackathon 404 y Biblia Operativa §19.
> Este documento declara con precisión qué IA usamos, para qué, y qué NO fue generado por IA.

---

## 1. Resumen ejecutivo

Nahual usa IA como **componente auxiliar**, no como el producto. Hay dos usos distinguibles:

1. **Claude Code** — asistente de programación durante el desarrollo. Todo el código producido fue revisado, probado e integrado por el equipo humano.
2. **Claude API** — componente funcional en runtime (Capa 2 del clasificador, zona gris 0.3–0.6, timeout 5 s). **El sistema funciona sin esta capa**: la Capa 1 heurística devuelve siempre un resultado.

El clasificador heurístico (Capa 1), los datasets de keywords, la lógica de override, la UX del bot, el marco legal y la presentación fueron definidos por el equipo con base en fuentes verificadas.

---

## 2. Uso en tiempo de desarrollo

### 2.1 Claude Code (Anthropic)
- **Para qué:** generar boilerplate (estructura de directorios, scaffolding de FastAPI, plumbing de Baileys), redactar docstrings en español, primera versión de regex de keywords, auto-generar tests.
- **Qué NO hizo:** definir la arquitectura de 4 fases, elegir los umbrales de override, redactar el pitch, validar con usuarios, elegir el marco legal, decidir las keywords reales (Marco).
- **Verificación humana:** cada cambio pasa por pytest local, simulación del bot, revisión manual de diffs.

### 2.2 Herramientas de edición
- Editor de texto y terminal (VS Code, IntelliJ).
- Git para control de versiones.
- No se usó IA generativa para wireframes, diagramas finales ni copy del pitch.

---

## 3. Uso en tiempo de ejecución (componente del producto)

### 3.1 Claude API — Capa 2 del clasificador
- **Cuándo se invoca:** sólo cuando la Capa 1 heurística da un score ponderado en `[0.3, 0.6]` (zona gris) Y la Fase 3/4 no disparó override.
- **Qué hace:** analiza el mensaje en español y devuelve `{risk_score, phase, rationale}` en JSON.
- **Modelo:** `claude-sonnet-4-20250514`.
- **Timeout duro:** 5 segundos. Si se excede, falla silenciosamente y el bot responde con el resultado de la Capa 1.
- **Privacidad:** el mensaje se envía a la API de Anthropic. No se almacena en Anthropic más allá de la retención estándar del servicio. La BD local de Nahual sólo guarda hash SHA-256 + resumen anonimizado.

### 3.2 Fallback garantizado
- Si `ANTHROPIC_API_KEY` está vacía o inválida, la Capa 2 se deshabilita automáticamente.
- Todos los tests unitarios e integración corren con la Capa 2 deshabilitada, comprobando que el sistema es funcional sin IA.

---

## 4. Qué NO fue generado por IA

| Componente | Autor | Evidencia |
|------------|-------|-----------|
| Arquitectura de 4 fases + override | Equipo Vanguard | [Biblia operativa §4](investigacion/NAHUAL_BIBLIA_OPERATIVA.md) |
| Dataset real de keywords | Marco Espinosa | `backend/classifier/keywords/*.json` con atributo `source` por patrón |
| Pitch (script 5 min) | Marco Espinosa | Biblia §16 |
| Mensajes del bot (tono, empatía) | Marco Espinosa | `bot/config/messages.js` |
| Protocolo legal | Marco Espinosa | [`docs/protocolo-legal.md`](protocolo-legal.md) |
| Encuesta y validación con usuarios | Marco Espinosa | Resultados en Google Form |
| Mentorías en el evento | Equipo Vanguard | Documentación del sábado |
| Reforma Código Penal 2026 · Rancho Izaguirre · cifras REDIM | Investigación humana | Biblia §11 (fuentes verificadas) |

---

## 5. Principio

> **La IA es un componente, no el producto.** El clasificador heurístico (Capa 1) funciona sin IA y cubre el 100% de los mensajes con un resultado útil. La Capa 2 añade precisión en casos ambiguos pero es opcional y fallable.

Este principio se aplica también al desarrollo: el equipo entiende cada línea de código que entra al repositorio y puede defender cualquier decisión técnica frente al jurado.

---

## 6. Fuentes humanas verificadas (no-IA)

- **Colegio de México (Dr. Rodrigo Peña):** análisis de 100 cuentas TikTok, catálogo de emojis codificados.
- **El País México (sep 2025):** testimonios del Rancho Izaguirre.
- **FinCEN (sep 2025):** red flags de sextorsión financiera.
- **Swissinfo/EFE (mar 2026):** lenguaje digital de cárteles.
- **CSIS (may 2025):** uso de algoritmos de TikTok para reclutamiento.
- **REDIM / ONC / CNDH / UNICEF México:** cifras de menores reclutados.

Ver [`investigacion/NAHUAL_BIBLIA_OPERATIVA.md`](investigacion/NAHUAL_BIBLIA_OPERATIVA.md) para el set completo con citas.

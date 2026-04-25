# Protocolo Legal — Nahual

> Documento operativo para enrutar incidentes detectados por Nahual hacia las autoridades correctas. **Marco mantiene este archivo durante el hackathon.**

---

## 1. Marco normativo aplicable

| Norma | Aplicación |
|-------|-----------|
| **Art. 16 CPEUM** | Inviolabilidad de comunicaciones privadas. **Nahual cumple:** sólo analiza datos AUTOINFORMADOS por el usuario; no intercepta. |
| **Art. 47 LGDNNA** | Protección integral de NNA contra reclutamiento. |
| **Código Penal Federal (reforma 2026)** | Hasta **18 años** de pena por reclutamiento de menores. |
| **Ley Olimpia** | Difusión no consentida de material íntimo (sextorsión). |
| **LFPDPPP** | Datos personales de menores: Nahual sólo guarda hashes y resúmenes anonimizados. |

---

## 2. Ruta de denuncia por nivel de riesgo

### SEGURO
- No requiere acción institucional.
- El bot recomienda hablar con un adulto si algo incomoda.

### ATENCIÓN
- Bot ofrece preparar reporte para Policía Cibernética (088).
- Sugiere conversación con tutor de confianza.
- Registra alerta en panel para seguimiento.

### PELIGRO (incluye override Fase 3/4)
1. **Inmediato:** alerta silenciosa al adulto designado (sólo nivel + plataforma, NUNCA contenido).
2. Generar PDF folio NAH-2026-XXXX con marco legal y contactos.
3. Recomendar **088 Policía Cibernética** y SIPINNA.
4. Si hay sextorsión → activar protocolo Ley Olimpia.

---

## 3. Contactos

| Autoridad | Contacto | Cuándo |
|-----------|----------|--------|
| Policía Cibernética | **088** | Cualquier riesgo digital |
| SIPINNA | https://sipinna.gob.mx | Vulneración de derechos NNA |
| Línea de la Vida | **800-911-2000** | Crisis emocional |
| Fiscalía General | Local según estado | Delitos graves / amenazas |
| DIF | Local según estado | Menores en situación de riesgo |

---

## 4. Privacidad por diseño

- **Mensajes originales:** nunca se almacenan. Sólo hash SHA-256 + resumen anonimizado.
- **Reporte PDF:** incluye categorías y fase, NO el texto literal.
- **Alerta a tutor:** sólo nivel + plataforma. NUNCA el contenido.
- **API pública** documentada con Swagger; el clasificador es transparente.

---

## 5. Cuándo Nahual NO actúa

- Mensajes recibidos por canales que no son del usuario (ej. interceptar a otra persona) → fuera de scope, viola Art. 16.
- Reporte sin consentimiento del menor → Nahual sólo analiza lo que el usuario pega voluntariamente.
- Diagnóstico clínico → Nahual detecta patrones de riesgo, no diagnostica trastornos.

---

*Última actualización: 2026-04-24 · Equipo Vanguard*

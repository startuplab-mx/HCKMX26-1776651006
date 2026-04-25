# NAHUAL — MARCO JURÍDICO, LEGAL Y DE PRIVACIDAD
## Documento Exhaustivo de Cumplimiento Normativo
### Equipo Vanguard | Hackathon 404: Threat Not Found | Abril 2026

---

> Este documento analiza la totalidad del marco jurídico mexicano aplicable al sistema Nahual, artículo por artículo, ley por ley, con el texto legal exacto y su aplicación concreta al diseño técnico del sistema.

---

# ÍNDICE

1. Constitución Política de los Estados Unidos Mexicanos (CPEUM)
2. Ley General de los Derechos de Niñas, Niños y Adolescentes (LGDNNA)
3. Código Penal Federal — Reclutamiento Ilícito (Art. 209 Quáter)
4. Ley Olimpia — Violación a la Intimidad Sexual (Arts. 199 Octies-Decies CPF)
5. Ley General de Acceso de las Mujeres a una Vida Libre de Violencia (LGAMVLV)
6. Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP)
7. Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados (LGPDPPSO)
8. Ley General para Prevenir, Sancionar y Erradicar los Delitos en Materia de Trata de Personas (LGPSEDMTP)
9. SIPINNA — Sistema Nacional de Protección Integral
10. Tratados Internacionales Aplicables
11. Análisis de Cumplimiento: Nahual vs. Marco Legal
12. Aviso de Privacidad (Template)
13. Protocolo de Denuncia para Usuarios

---

# 1. CONSTITUCIÓN POLÍTICA (CPEUM)

## Artículo 1 — Derechos Humanos

Todas las personas gozarán de los derechos humanos reconocidos en la Constitución y en los tratados internacionales, así como de las garantías para su protección. Todas las autoridades, en el ámbito de sus competencias, tienen la obligación de promover, respetar, proteger y garantizar los derechos humanos de conformidad con los principios de universalidad, interdependencia, indivisibilidad y progresividad.

**Aplicación a Nahual:** El sistema opera bajo el principio de protección progresiva de derechos de menores. La detección de reclutamiento criminal es una herramienta que coadyuva con el Estado en su obligación de proteger a NNA (niñas, niños y adolescentes).

## Artículo 4, Párrafo Noveno — Interés Superior de la Niñez

"En todas las decisiones y actuaciones del Estado se velará y cumplirá con el principio del interés superior de la niñez, garantizando de manera plena sus derechos. Los niños y las niñas tienen derecho a la satisfacción de sus necesidades de alimentación, salud, educación y sano esparcimiento para su desarrollo integral. Este principio deberá guiar el diseño, ejecución, seguimiento y evaluación de las políticas públicas dirigidas a la niñez."

**Aplicación a Nahual:** Nahual está diseñado con el interés superior de la niñez como principio rector. Cada decisión de diseño (privacidad por defecto, no almacenar texto original, lenguaje empático, consentimiento explícito para contribución de datos) prioriza la protección del menor sobre cualquier otra consideración.

## Artículo 16 — Inviolabilidad de las Comunicaciones Privadas

### Texto constitucional exacto (párrafos relevantes):

**Párrafo primero:** "Nadie puede ser molestado en su persona, familia, domicilio, papeles o posesiones, sino en virtud de mandamiento escrito de la autoridad competente, que funde y motive la causa legal del procedimiento."

**Párrafo segundo:** "Toda persona tiene derecho a la protección de sus datos personales, al acceso, rectificación y cancelación de los mismos, así como a manifestar su oposición, en los términos que fije la ley, la cual establecerá los supuestos de excepción a los principios que rijan el tratamiento de datos, por razones de seguridad nacional, disposiciones de orden público, seguridad y salud públicas o para proteger los derechos de terceros."

**Párrafo decimosegundo:** "Las comunicaciones privadas son inviolables. La ley sancionará penalmente cualquier acto que atente contra la libertad y privacía de las mismas, excepto cuando sean aportadas de forma voluntaria por alguno de los particulares que participen en ellas."

**Párrafo decimotercero:** "Exclusivamente la autoridad judicial federal, a petición de la autoridad federal que faculte la ley o del titular del Ministerio Público de la entidad federativa correspondiente, podrá autorizar la intervención de cualquier comunicación privada."

### Análisis de cumplimiento de Nahual:

**¿Nahual intercepta comunicaciones privadas?** NO. El sistema opera bajo dos modelos, ambos legalmente lícitos:

**Modelo reactivo (bot):** El menor aporta voluntariamente el contenido de una comunicación en la que participó. La CPEUM establece explícitamente la excepción: las comunicaciones "cuando sean aportadas de forma voluntaria por alguno de los particulares que participen en ellas." El menor es participante de la comunicación y la aporta voluntariamente. No hay interceptación.

**Modelo proactivo (extensión):** Nahual Shield es una extensión que el usuario instala voluntariamente en su propio navegador. La extensión analiza el contenido visible en la pantalla del usuario — contenido al que el usuario ya tiene acceso legítimo. No intercepta comunicaciones de terceros; analiza lo que el usuario ya está viendo. La jurisprudencia de la SCJN (Tesis 1a. CLIV/2011) establece que el derecho a la inviolabilidad de las comunicaciones "se impone solo frente a terceros ajenos a la comunicación." El usuario de la extensión es participante de la comunicación.

**Modelo de contribución anónima:** El usuario consiente explícitamente aportar datos anonimizados. No se almacena texto original ni datos de identificación. Solo metadata estadística (plataforma, fase detectada, categorías de patrones). Esto constituye un tratamiento de datos anonimizados, no de datos personales.

---

# 2. LEY GENERAL DE LOS DERECHOS DE NIÑAS, NIÑOS Y ADOLESCENTES (LGDNNA)

## Artículo 5 — Definiciones de Edad

"Son niñas y niños los menores de doce años, y adolescentes las personas de entre doce años cumplidos y menos de dieciocho años de edad."

**Aplicación:** Nahual protege a todo menor de 18 años. El lenguaje del bot está calibrado para adolescentes (12-17), que son el grupo principal de riesgo de reclutamiento digital.

## Artículo 47 — Obligación de Prevenir

Las autoridades federales, estatales y municipales, en el ámbito de sus respectivas competencias, están obligadas a tomar las medidas necesarias para prevenir, atender y sancionar los casos en que niñas, niños o adolescentes se vean afectados por:

**Fracción VII:** "La incitación o coacción para que participen en la comisión de delitos o en asociaciones delictuosas, en conflictos armados o en cualquier otra condición que impida su desarrollo integral."

**Fracción reformada (2022, DOF):** Incluye explícitamente la protección contra el reclutamiento para actividades delictivas.

**Aplicación a Nahual:** El artículo 47 fracción VII es el fundamento legal directo de la existencia de Nahual. El sistema es una herramienta tecnológica que coadyuva en la prevención del reclutamiento criminal de menores — exactamente lo que este artículo ordena. Esto debe citarse en el pitch y en el README.

## Artículo 47 Bis (Iniciativa en proceso legislativo, septiembre 2025)

Propuesta de adición que ordena a las autoridades "establecer protocolos y programas integrales de prevención del reclutamiento, captación o utilización de niñas, niños y adolescentes por parte de organizaciones delictivas." Incluye: diagnóstico territorial, protocolos escolares de detección temprana, y campañas de sensibilización.

**Aplicación:** Aunque esta iniciativa está en proceso legislativo, su existencia demuestra la voluntad del Estado mexicano de crear herramientas como Nahual. Si se aprueba, Nahual sería una implementación directa de lo que el artículo 47 Bis ordena.

## Artículo 48 — Medidas de Protección Especial

Las autoridades deben adoptar medidas especiales de protección para NNA que sean víctimas de delitos, incluyendo asistencia jurídica, psicológica, y mecanismos de denuncia accesibles.

**Aplicación:** El reporte PDF de Nahual y la conexión con la Policía Cibernética (088) son mecanismos que facilitan el acceso a protección especial.

---

# 3. CÓDIGO PENAL FEDERAL — RECLUTAMIENTO ILÍCITO

## Artículo 209 Quáter (Propuesta de adición)

"Comete el delito de reclutamiento ilícito, el que enliste, reclute u obligue a participar directa o indirectamente en las hostilidades o en acciones armadas, a personas menores de dieciocho años de edad. Por tal delito se impondrán de nueve a dieciocho años de prisión y de mil a dos mil quinientos días de multa."

**Estado legislativo:** Esta tipificación ha sido propuesta en múltiples iniciativas (2021, 2022, 2025). La Cámara de Diputados reformó el Código Penal en 2026 para incluir penas de hasta 18 años por reclutamiento de menores.

**Aplicación a Nahual:** Los reportes PDF generados por el sistema incluyen la referencia a esta tipificación. Cuando un menor genera un reporte de riesgo nivel PELIGRO con fase de coerción o explotación, el documento cita los artículos aplicables para que la Fiscalía pueda iniciar la investigación correspondiente.

---

# 4. LEY OLIMPIA — VIOLACIÓN A LA INTIMIDAD SEXUAL

La "Ley Olimpia" no es una ley unitaria sino un conjunto de reformas al Código Penal Federal y a la Ley General de Acceso de las Mujeres a una Vida Libre de Violencia. Las disposiciones relevantes son:

## Artículo 199 Octies del Código Penal Federal

"Comete el delito de violación a la intimidad sexual, aquella persona que divulgue, comparta, distribuya o publique imágenes, videos o audios de contenido íntimo sexual de una persona que tenga la mayoría de edad, sin su consentimiento, su aprobación o su autorización."

"Así como quien videograbe, audiograbe, fotografíe, imprima o elabore, imágenes, audios o videos con contenido íntimo sexual de una persona sin su consentimiento, sin su aprobación, o sin su autorización."

Pena: 3 a 6 años de prisión + 500 a 1,000 UMA de multa.

## Artículo 199 Nonies

Extiende la misma pena cuando las imágenes, videos o audios "no correspondan con la persona que es señalada o identificada en los mismos" — es decir, cubre deepfakes y material generado por IA.

## Artículo 199 Decies — Agravantes

La pena se aumenta hasta en una mitad (4.5 a 9 años) cuando:
- I. Sea cometido por cónyuge, concubino, o persona con relación sentimental
- II. Sea cometido por servidor público
- III. Se cometa contra persona que no pueda comprender el hecho
- IV. Se obtenga beneficio no lucrativo
- V. Se haga con fines lucrativos
- VI. Cuando la víctima atente contra su integridad o su propia vida como consecuencia

**Aplicación a Nahual:** La Fase 4 del clasificador (Explotación) incluye detección de patrones de sextorsión: solicitud de material íntimo + amenaza de difusión + demanda de pago. Cuando estos patrones se detectan, el reporte PDF incluye referencia a los artículos 199 Octies-Decies del CPF. Esto es particularmente relevante porque la sextorsión de menores combina reclutamiento criminal con violencia digital.

---

# 5. LEY GENERAL DE ACCESO DE LAS MUJERES A UNA VIDA LIBRE DE VIOLENCIA (LGAMVLV)

## Artículo 20 Quáter — Violencia Digital

Define violencia digital como "aquellas acciones en las que se expongan, distribuyan, difundan, exhiban, transmitan, comercialicen, oferten, intercambien o compartan imágenes, audios o videos reales o simulados de contenido íntimo sexual de una persona sin su consentimiento, sin su aprobación o sin su autorización y que le cause daño psicológico, emocional, en cualquier ámbito de su vida privada o en su imagen propia."

También incluye: "aquellos actos dolosos que causen daño a la intimidad, privacidad y/o dignidad de las mujeres, que se cometan por medio de las tecnologías de la información y la comunicación."

**Aplicación:** Los patrones de sextorsión en el clasificador de Nahual están alineados con esta definición. La detección temprana de estos patrones previene la consumación de la violencia digital descrita en este artículo.

---

# 6. LEY FEDERAL DE PROTECCIÓN DE DATOS PERSONALES (LFPDPPP)

## NOTA IMPORTANTE: Nueva LFPDPPP (Marzo 2025)

La LFPDPPP fue reformada sustancialmente y publicada en el DOF el 20 de marzo de 2025. Las funciones del extinto INAI fueron transferidas a la Secretaría de Anticorrupción y Buen Gobierno. Los cambios relevantes para Nahual:

## Artículo 5 — Principios Rectores

"El responsable deberá observar los principios de licitud, finalidad, lealtad, consentimiento, calidad, proporcionalidad, información y responsabilidad en el tratamiento de datos personales."

**Cumplimiento de Nahual por principio:**

- **Licitud:** Nahual trata datos conforme a la ley. No intercepta comunicaciones (Art. 16 CPEUM). Los datos son aportados voluntariamente.
- **Finalidad:** Los datos se usan exclusivamente para detección de riesgo de reclutamiento criminal. No hay finalidad secundaria no declarada.
- **Lealtad:** No se obtienen datos de forma engañosa ni fraudulenta. El bot declara su propósito desde el mensaje de bienvenida.
- **Consentimiento:** El menor consiente al interactuar con el bot. La contribución de datos anónimos requiere consentimiento explícito adicional.
- **Calidad:** Solo se almacenan datos necesarios y exactos.
- **Proporcionalidad:** Se almacena el mínimo necesario. Nunca el texto original.
- **Información:** El usuario sabe qué hace el sistema (vía mensajes del bot y aviso de privacidad).
- **Responsabilidad:** El responsable (equipo Nahual) implementa medidas de seguridad.

## Artículo 7 — Consentimiento

"Todo tratamiento de datos personales estará sujeto al consentimiento de la persona titular."

**Cumplimiento:** El menor consiente al enviar un mensaje al bot voluntariamente. La contribución anónima tiene un segundo momento de consentimiento explícito ("¿Quieres compartir los datos de forma anónima? Responde SÍ o NO").

## Artículo 8 — Datos Sensibles

"Tratándose de datos personales sensibles, el responsable deberá obtener el consentimiento expreso y por escrito."

**Cumplimiento:** Nahual NO almacena datos personales sensibles. No almacena texto original, no almacena números de teléfono de terceros (solo el hash del JID para gestión de sesión), no almacena contenido de las conversaciones. Los datos que almacena (risk_score, fase detectada, plataforma, categorías de patrones) no son datos personales ni sensibles — son metadata estadística anonimizada.

## Artículo 19 — Vulneraciones de Seguridad

"Las vulneraciones de seguridad ocurridas en cualquier fase del tratamiento que afecten de forma significativa los derechos patrimoniales o morales serán informadas de forma inmediata al titular."

**Cumplimiento:** Dado que Nahual no almacena datos personales identificables, una vulneración de la base de datos no expondría información personal. Sin embargo, como medida adicional, la base de datos usa WAL (Write-Ahead Logging) y los hashes SHA-256 son irreversibles.

## Artículo 14 — Menores de Edad

La LGPDPPSO (para sujetos obligados) establece en su artículo 7: "En el tratamiento de datos personales de menores de edad se deberá privilegiar el interés superior de la niña, el niño y el adolescente."

Y en artículo 14: "En la obtención del consentimiento de personas menores de edad se estará a lo dispuesto en las reglas de representación previstas en la legislación civil."

**Análisis:** Nahual opera en el sector privado (no es sujeto obligado del Estado), por lo que se rige por la LFPDPPP, no la LGPDPPSO. Sin embargo, adopta voluntariamente el estándar más protector: privilegiar el interés superior del menor en todo tratamiento.

**Nota sobre la nueva LFPDPPP:** La reforma de marzo 2025 eliminó la referencia explícita al tratamiento de datos de menores que existía en la versión anterior. Sin embargo, las reglas generales de consentimiento y los principios siguen aplicando, y el interés superior del menor (Art. 4 CPEUM, Art. 2 LGDNNA) tiene rango constitucional superior.

---

# 7. LEY GENERAL PARA PREVENIR LA TRATA DE PERSONAS (LGPSEDMTP)

## Artículo 10 — Explotación

Define como forma de explotación: "la esclavitud, la condición de siervo, la prostitución ajena u otras formas de explotación sexual, la explotación laboral, el trabajo o servicios forzados, la mendicidad forzosa, la utilización de personas menores de dieciocho años en actividades delictivas, la adopción ilegal de persona menor de dieciocho años, el matrimonio forzoso o servil, tráfico de órganos, tejidos y células de seres humanos vivos, y experimentación biomédica ilícita en seres humanos."

**Aplicación:** El reclutamiento criminal digital de menores (el target de Nahual) está explícitamente incluido en la definición de trata de personas: "la utilización de personas menores de dieciocho años en actividades delictivas." Esto eleva la gravedad jurídica del problema que Nahual detecta.

---

# 8. SIPINNA — SISTEMA NACIONAL DE PROTECCIÓN INTEGRAL

El SIPINNA es el mecanismo de coordinación interinstitucional creado por la LGDNNA para garantizar los derechos de NNA. Opera a nivel federal, estatal y municipal.

**Funciones relevantes:**
- Coordinar políticas públicas de protección de NNA
- Establecer protocolos de atención a víctimas menores
- Generar datos y estadísticas sobre situación de NNA
- Articular respuestas institucionales

**Aplicación a Nahual:**
- Los reportes PDF generados incluyen referencia a SIPINNA como instancia de canalización
- La API pública de Nahual (/contributions/stats) genera datos agregados que podrían alimentar los diagnósticos de SIPINNA
- El sistema es una herramienta de detección temprana que se alinea con los protocolos de prevención de SIPINNA

---

# 9. TRATADOS INTERNACIONALES

## Convención sobre los Derechos del Niño (CDN, 1989)

Ratificada por México. Artículo 3: "En todas las medidas concernientes a los niños, el interés superior del niño será una consideración primordial."

## Protocolo Facultativo de la CDN relativo a la Participación de Niños en Conflictos Armados (2002)

Prohíbe el reclutamiento de menores de 18 años en hostilidades. Aunque está diseñado para conflictos armados, la jurisprudencia interamericana ha extendido su aplicación al reclutamiento por organizaciones criminales.

## Protocolo de Palermo (2000)

Protocolo de las Naciones Unidas para Prevenir, Reprimir y Sancionar la Trata de Personas. Define la captación, transporte, traslado, acogida o recepción de personas con fines de explotación como trata. El reclutamiento digital de menores encaja en esta definición.

## Jurisprudencia Interamericana

**Villagrán Morales y otros vs. Guatemala (1999):** La Corte IDH estableció el deber reforzado de protección de menores frente a su utilización en contextos de violencia estructural.

**Aplicación:** Estos instrumentos internacionales refuerzan la legitimidad de Nahual como herramienta de prevención. En el pitch ante INL (Embajada de EE.UU.), citar el Protocolo de Palermo y la CDN conecta directamente con la agenda de cooperación bilateral.

---

# 10. ANÁLISIS DE CUMPLIMIENTO: NAHUAL vs. MARCO LEGAL

## Tabla de Cumplimiento Artículo por Artículo

| Norma | Artículo | Requisito | ¿Nahual cumple? | Cómo |
|-------|----------|-----------|-----------------|------|
| CPEUM | Art. 16 párr. 12 | No interceptar comunicaciones privadas | ✅ SÍ | Bot: datos aportados voluntariamente por participante. Extensión: analiza DOM visible del usuario que la instaló. |
| CPEUM | Art. 16 párr. 2 | Protección de datos personales | ✅ SÍ | No almacena texto original. Solo SHA-256 hash + metadata anonimizada. |
| CPEUM | Art. 4 párr. 9 | Interés superior de la niñez | ✅ SÍ | Principio rector de diseño. Privacidad por defecto. Lenguaje empático. |
| LGDNNA | Art. 47 fr. VII | Prevenir reclutamiento de NNA | ✅ SÍ | Es literalmente el propósito del sistema. |
| CPF | Art. 199 Octies | Tipificación de violencia digital | ✅ REFERENCIA | Citado en reportes PDF cuando se detecta sextorsión. |
| LFPDPPP | Art. 5 | Principios de tratamiento | ✅ SÍ | Licitud, finalidad, lealtad, consentimiento, calidad, proporcionalidad, información, responsabilidad — todos cumplidos. |
| LFPDPPP | Art. 7 | Consentimiento del titular | ✅ SÍ | Consentimiento implícito al interactuar + consentimiento explícito para contribución. |
| LFPDPPP | Art. 8 | Consentimiento expreso para datos sensibles | ✅ N/A | Nahual no trata datos personales sensibles. |
| LFPDPPP | Art. 19 | Notificación de vulneraciones | ✅ MITIGADO | No hay datos personales expuestos en caso de brecha. |
| LGPSEDMTP | Art. 10 | Prevención de trata (utilización de menores en delitos) | ✅ ALINEADO | Detección de las fases previas a la explotación. |
| CDN | Art. 3 | Interés superior del niño | ✅ SÍ | Principio rector. |
| Protocolo de Palermo | General | Prevención de trata | ✅ ALINEADO | Herramienta de detección temprana de captación. |

## Análisis de Riesgos Legales

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|-----------|
| Acusación de interceptación de comunicaciones (Art. 16 CPEUM) | BAJA | El usuario aporta voluntariamente. La extensión analiza su propia pantalla. Documentar en ToS. |
| Demanda por tratamiento indebido de datos de menores | BAJA | No se almacenan datos personales. Solo metadata anonimizada. Documentar en aviso de privacidad. |
| Responsabilidad por falso positivo que cause daño al menor | MEDIA | Disclaimers claros: "Este análisis es orientativo y no constituye un diagnóstico." El reporte recomienda acudir a autoridades. |
| Uso del sistema para acosar o monitorear ilegalmente a un menor | MEDIA | La extensión solo funciona en el navegador del usuario que la instala. El bot solo analiza lo que el usuario le envía. No hay monitoreo remoto. |

---

# 11. AVISO DE PRIVACIDAD (Template para Nahual)

```
AVISO DE PRIVACIDAD INTEGRAL — NAHUAL

Identidad del responsable: Equipo Vanguard (Nahual)
Contacto: [correo del equipo]
Fecha: Abril 2026

I. DATOS QUE RECOPILAMOS
Nahual NO recopila datos personales identificables. Específicamente:
- NO almacenamos el contenido de los mensajes que analizas
- NO almacenamos tu número de teléfono de forma permanente
- NO almacenamos tu nombre, ubicación ni datos de contacto

Lo que SÍ almacenamos (exclusivamente para funcionamiento del sistema):
- Un identificador de sesión temporal (hash criptográfico)
- El resultado del análisis: nivel de riesgo, fase detectada, categorías
- La plataforma de origen del mensaje (ej: "WhatsApp", "TikTok")
- El tipo de entrada (texto, audio, imagen)

II. FINALIDAD
Los datos se utilizan exclusivamente para:
- Proporcionarte el resultado del análisis de riesgo
- Generar reportes PDF para presentar ante autoridades
- Si lo autorizas explícitamente: contribuir datos anónimos
  para investigación sobre reclutamiento criminal digital

III. CONTRIBUCIÓN ANÓNIMA (OPCIONAL)
Si decides contribuir datos de forma anónima:
- Solo se almacenan categorías de patrones detectados y
  nivel de riesgo. NUNCA el contenido del mensaje.
- Estos datos no pueden vincularse a tu identidad.
- Puedes negarte sin ninguna consecuencia.

IV. TRANSFERENCIAS
No transferimos datos personales a terceros.
Los datos anónimos de contribución son públicos en
formato agregado (estadísticas, no casos individuales).

V. DERECHOS ARCO
Dado que Nahual no almacena datos personales 
identificables, los derechos de Acceso, Rectificación,
Cancelación y Oposición se ejercen de facto:
no hay datos personales que acceder, rectificar,
cancelar ni a los cuales oponerse.

VI. SEGURIDAD
- Encriptación SHA-256 para hashes
- Base de datos SQLite con WAL
- No se almacena texto original
- Código abierto bajo licencia MIT para auditoría

VII. BASE LEGAL
Art. 16 CPEUM (datos aportados voluntariamente)
Art. 4 CPEUM (interés superior de la niñez)
Art. 47 LGDNNA (prevención de reclutamiento)
LFPDPPP Arts. 5, 7, 8, 19 (principios de tratamiento)
```

---

# 12. PROTOCOLO DE DENUNCIA PARA USUARIOS

## ¿A dónde acudir según el tipo de riesgo?

| Tipo de riesgo detectado | Autoridad competente | Contacto | Fundamento legal |
|--------------------------|---------------------|----------|-----------------|
| Reclutamiento criminal (cualquier fase) | Policía Cibernética | 088 (24/7) | Art. 47 fr. VII LGDNNA |
| Amenazas de muerte o violencia | Fiscalía General / Ministerio Público | Fiscalía local | CPF Art. 282 (amenazas) |
| Sextorsión / material íntimo | Policía Cibernética + Fiscalía | 088 + Fiscalía local | CPF Arts. 199 Octies-Decies |
| Trata de personas / explotación | Fiscalía Especial FEVIMTRA | 800-00-854-00 | LGPSEDMTP Art. 10 |
| Desaparición de menor | Comisión Nacional de Búsqueda | 800-800-2835 | Ley General de Desaparición |
| Cualquier vulneración de derechos de NNA | DIF / SIPINNA | DIF local | Art. 47 LGDNNA |
| Crisis emocional del menor | Línea de la Vida | 800-911-2000 (24/7) | — |

## Información que debe contener la denuncia

Basado en los requisitos del Ministerio Público para iniciar carpeta de investigación:
1. Narración de hechos (qué pasó, cuándo, dónde)
2. Plataforma digital donde ocurrió
3. Capturas de pantalla (si las tiene — NO borrar conversaciones)
4. Datos del presunto responsable (username, número, perfil)
5. Cualquier dato que permita identificar al agresor

**El reporte PDF de Nahual incluye:** Folio único, fecha, plataforma, nivel de riesgo, fase detectada, análisis del sistema, y los artículos de ley aplicables. Este reporte está diseñado para ser presentado directamente ante el Ministerio Público como complemento de la denuncia.

---

# 13. REFERENCIAS LEGISLATIVAS COMPLETAS

| Norma | Publicación DOF | URL oficial |
|-------|----------------|-------------|
| CPEUM | Última reforma 2024 | diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf |
| LGDNNA | DOF 04-12-2014, última reforma 2024 | diputados.gob.mx/LeyesBiblio/pdf/LGDNNA.pdf |
| CPF (Ley Olimpia) | DOF 01-06-2021 | Arts. 199 Octies-Decies |
| LFPDPPP | DOF 20-03-2025 (nueva) | diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf |
| LGPDPPSO | DOF 26-01-2017 | diputados.gob.mx/LeyesBiblio/pdf/LGPDPPSO.pdf |
| LGAMVLV | DOF 01-02-2007, reforma 2021 | diputados.gob.mx/LeyesBiblio/pdf/LGAMVLV.pdf |
| LGPSEDMTP | DOF 14-06-2012 | diputados.gob.mx/LeyesBiblio/pdf/LGPSEDMTP.pdf |
| CDN | Ratificada por México 1990 | ohchr.org |
| Protocolo de Palermo | 2000 | unodc.org |

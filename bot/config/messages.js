// ============================================================
// Nahual Bot — Mensajes (PROPIEDAD DE MARCO)
// Marco edita este archivo durante el hackathon. Tono: español
// mexicano informal (tuteo), empático, no-juicioso.
// ============================================================

export const MESSAGES = {
  bienvenida: [
    '🛡️ Hola, soy Nahual.',
    'Estoy aquí para ayudarte a entender si un mensaje que recibiste es seguro o sospechoso.',
    '',
    'Puedes mandarme:',
    '• 📝 Texto (pega el mensaje)',
    '• 🎙️ Un audio (lo transcribo y analizo)',
    '• 📸 Una captura de pantalla (extraigo el texto)',
    '',
    '🔒 No guardo el mensaje original, sólo un resumen anónimo. Tu privacidad es prioridad.',
  ].join('\n'),

  recibido: 'Recibido. Esto requiere un análisis detallado, dame unos segundos... 🔍',

  // Multimedia ----------------------------------------------------------
  audioRecibido: '🎙️ Recibí tu audio. Transcribiendo… esto puede tardar unos segundos.',
  audioVacio: 'No pude entender el audio. ¿Puedes enviarlo como texto?',
  audioNoConfigurado:
    'Por ahora no puedo procesar audios (falta configurar el servicio de transcripción). Mándame el texto, por favor.',
  audioError:
    'No pude procesar el audio en este momento. Por favor, envíame el mensaje como texto.',

  imagenRecibida: '📸 Recibí tu imagen. Extrayendo el texto…',
  imagenSinTexto:
    'No pude leer texto en la imagen. ¿Puedes copiarlo y pegarlo como texto?',
  imagenNoConfigurada:
    'Por ahora no puedo procesar imágenes (falta configurar el servicio de OCR). Cópiame el texto, por favor.',
  imagenError:
    'No pude procesar la imagen. Intenta enviarme el texto copiado directamente.',

  rechazoMultimedia:
    'Por ahora sólo puedo analizar texto, audios y capturas. Stickers y videos los estoy aprendiendo todavía 🙈.',

  confirmarTranscripcion: (text) => {
    const preview = text.length > 500 ? `${text.slice(0, 500)}…` : text;
    return [
      '📝 *Esto fue lo que entendí:*',
      '',
      `"${preview}"`,
      '',
      '¿Quieres que analice este texto? Responde *SÍ* o *NO*.',
    ].join('\n');
  },

  transcripcionRechazada:
    'OK, no analicé ese mensaje. Mándame texto o intenta de nuevo cuando quieras.',

  // Resultados ---------------------------------------------------------
  resultadoSeguro: (score) =>
    [
      '✅ *Mensaje SEGURO*',
      `Riesgo: ${(score * 100).toFixed(0)}%`,
      '',
      'No detecté señales claras de reclutamiento. Aun así, si algo te incomoda, confía en tu instinto y platícalo con alguien de confianza.',
    ].join('\n'),

  resultadoAtencion: (score, fase) =>
    [
      '⚠️ *Atención — señales sospechosas*',
      `Riesgo: ${(score * 100).toFixed(0)}%`,
      `Fase detectada: ${fase}`,
      '',
      'Vi patrones que pueden ser intentos de manipulación. No tienes que decidir solo/a.',
      '',
      '¿Quieres que te ayude a preparar un reporte para la Policía Cibernética (088)?',
    ].join('\n'),

  resultadoPeligro: (score, fase) =>
    [
      '🚨 *PELIGRO — actúa ahora*',
      `Riesgo: ${(score * 100).toFixed(0)}%`,
      `Fase: ${fase}`,
      '',
      'Lo que recibiste tiene señales claras de reclutamiento criminal o amenaza directa.',
      '',
      'No estás solo/a. Voy a ayudarte:',
      '1️⃣ Avisar a un adulto de confianza',
      '2️⃣ Generar un reporte para la Policía Cibernética',
      '3️⃣ Bloquear al contacto que te escribió',
      '',
      '¿Me das el WhatsApp de un adulto de confianza para avisarle de inmediato? (sólo nivel de alerta, NO el mensaje)',
    ].join('\n'),

  pedirContacto:
    'Mándame el número del adulto de confianza con el formato +52XXXXXXXXXX (10 dígitos con clave país).',

  notificacionTutor: (nivel, plataforma) =>
    [
      '🛡️ *Aviso Nahual*',
      '',
      `Un menor está usando Nahual y detectamos un mensaje con nivel: *${nivel}* en ${plataforma}.`,
      '',
      'Por privacidad NO incluimos el contenido. Recomendamos:',
      '• Buscar al menor con calma, sin juicio',
      '• Marcar 088 (Policía Cibernética)',
      '• SIPINNA: https://sipinna.gob.mx',
      '',
      'Línea de la Vida (crisis): 800-911-2000',
    ].join('\n'),

  reporteListo: (folio) =>
    `📄 Tu reporte fue generado con folio *${folio}*. Puedes descargarlo desde el panel o pedirlo aquí.`,

  // Legal context (Phase 4) -------------------------------------------
  // The bot keeps WhatsApp messages short. We cap actions at 5 and
  // authorities at 3 — the full list goes to the PDF report.
  guiaLegal: (legal) => {
    if (!legal) return null;
    const urgencyLabel = {
      inmediata: '🔴 URGENCIA INMEDIATA',
      prioritaria: '🟡 ATENCIÓN PRIORITARIA',
      preventiva: '🟢 ACCIÓN PREVENTIVA',
    }[legal.urgency] || legal.urgency;

    const actions = (legal.recommended_actions || [])
      .slice(0, 5)
      .map((a, i) => `${i + 1}. ${a}`)
      .join('\n');

    const authorities = (legal.authorities || [])
      .slice(0, 3)
      .map((a) => `• ${a.name}: *${a.phone}* (${a.hours})`)
      .join('\n');

    const articleHint = (legal.articles || [])
      .filter((a) => a.law !== 'CPEUM' && a.law !== 'LFPDPPP')
      .slice(0, 3)
      .map((a) => `• ${a.law} ${a.article} — ${a.title}`)
      .join('\n');

    const blocks = [`🛡️ *Guía legal · ${urgencyLabel}*`, ''];
    if (actions) blocks.push('*Qué hacer ahora:*', actions, '');
    if (authorities) blocks.push('*Contactos:*', authorities, '');
    if (articleHint)
      blocks.push('*Marco legal aplicable (extracto):*', articleHint, '');
    blocks.push(
      '_El reporte PDF incluye la lista completa de artículos, autoridades y derechos de la víctima._',
    );
    return blocks.join('\n');
  },

  // Contribuciones (Phase 3) -------------------------------------------
  preguntarContribuir: [
    '🔬 *Última pregunta*',
    '',
    '¿Te gustaría compartir los datos de este análisis de forma completamente anónima?',
    '',
    'No se guarda tu número, nombre, ni el contenido del mensaje — sólo el tipo de riesgo detectado y la plataforma. Esto ayuda a entender mejor cómo operan los reclutadores y a proteger a más jóvenes.',
    '',
    'Responde *SÍ* para contribuir o *NO* para terminar.',
  ].join('\n'),

  preguntarRegion: [
    'Gracias 🙏. Si te animas, ¿de qué estado o región eres? Nos ayuda a saber dónde están ocurriendo más casos.',
    '',
    'Ejemplo: "Coahuila", "CDMX", "Nuevo León". O escribe *paso* para omitir.',
  ].join('\n'),

  contribucionGracias: [
    '🙏 *Gracias.*',
    '',
    'Tu aportación anónima ayuda a construir el primer mapa de reclutamiento criminal digital en México. Cada dato cuenta.',
    '',
    '¿Hay algo más que quieras analizar?',
  ].join('\n'),

  contribucionRechazada:
    'Sin problema. Tu privacidad es lo primero. Cuando quieras analizar otro mensaje, sólo escríbeme. 🛡️',

  contribucionError:
    'No pude registrar la contribución, pero tu análisis sigue en pie. Intenta más tarde si quieres aportar.',

  errorBackend:
    'Tuve un problema al analizar tu mensaje. Inténtalo de nuevo en un momento. Si urge: 088 (Policía Cibernética).',

  despedida: 'Gracias por confiar en Nahual. Cuídate. 🛡️',
};

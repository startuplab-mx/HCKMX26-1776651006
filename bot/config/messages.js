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
    'Pégame el mensaje que te llegó (sólo texto, por ahora) y lo analizo en segundos.',
    '',
    '🔒 No guardo el mensaje original, sólo un resumen anónimo. Tu privacidad es prioridad.',
  ].join('\n'),

  recibido: 'Recibido. Esto requiere un análisis detallado, dame unos segundos... 🔍',

  rechazoMultimedia:
    'Aún estoy entrenando mis ojos y oídos 🙈. Por ahora, por favor envíame tu reporte en texto o cópiame lo que te escribieron para poder ayudarte.',

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

  errorBackend:
    'Tuve un problema al analizar tu mensaje. Inténtalo de nuevo en un momento. Si urge: 088 (Policía Cibernética).',

  despedida: 'Gracias por confiar en Nahual. Cuídate. 🛡️',
};

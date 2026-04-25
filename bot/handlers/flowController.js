// State machine:
//   inicio → bienvenida → recibir_msg → (analizando) → result_*
//                                                   ↓ (PELIGRO)
//                                                notify → (gen_report on demand)
//
// One call per turn: /alert classifies + persists + returns the analysis.
// Last alert id is stored in session so the user can ask for the PDF
// afterwards by typing "reporte".
import { MESSAGES } from '../config/messages.js';
import {
  ensureLoaded,
  getSession,
  setStep,
  setSessionData,
  getSessionData,
} from '../utils/sessionManager.js';
import { registerAlert, fetchReportBytes } from './alertDispatcher.js';

const PHASE_LABEL = {
  captacion: 'Captación',
  enganche: 'Enganche',
  coercion: 'Coerción',
  explotacion: 'Explotación',
  ninguna: 'Sin fase dominante',
};

const GREETING_RE =
  /^(hola|hey|hi|buenas|qué onda|que onda|buenos dias|buenas tardes|buenas noches|holi|wenas|saludos|menu)[\s!.,?¿¡]*$/i;
const REPORT_RE = /^\s*(reporte|report|pdf|descargar)\s*$/i;

function looksLikeGreeting(text) {
  return text.length < 30 && GREETING_RE.test(text.trim());
}

async function sendReport(sock, jid) {
  const lastAlertId = getSessionData(jid, 'lastAlertId');
  if (!lastAlertId) {
    await sock.sendMessage(jid, {
      text: 'Aún no tengo un reporte listo para ti. Envíame primero el mensaje sospechoso.',
    });
    return;
  }
  try {
    const buf = await fetchReportBytes(lastAlertId);
    const folio = `NAH-2026-${String(lastAlertId).padStart(4, '0')}`;
    await sock.sendMessage(jid, {
      document: buf,
      mimetype: 'application/pdf',
      fileName: `${folio}.pdf`,
      caption: MESSAGES.reporteListo(folio),
    });
  } catch (err) {
    await sock.sendMessage(jid, {
      text: `No pude generar el reporte (${err.message}). Intenta de nuevo en un momento.`,
    });
  }
}

async function analyzeAndReply(sock, jid, text) {
  await sock.sendMessage(jid, { text: MESSAGES.recibido });
  setStep(jid, 'analizando');
  try {
    const result = await registerAlert({
      text,
      platform: 'whatsapp',
      source: 'bot',
      session_id: jid,
    });
    setSessionData(jid, { lastAlertId: result.id });
    const fase = PHASE_LABEL[result.phase_detected] || 'Sin fase dominante';
    let reply;
    if (result.risk_level === 'PELIGRO') {
      reply = MESSAGES.resultadoPeligro(result.risk_score, fase);
      setStep(jid, 'notify');
    } else if (result.risk_level === 'ATENCION') {
      reply = MESSAGES.resultadoAtencion(result.risk_score, fase);
      setStep(jid, 'result');
    } else {
      reply = MESSAGES.resultadoSeguro(result.risk_score);
      setStep(jid, 'result');
    }
    await sock.sendMessage(jid, { text: reply });
  } catch (err) {
    await sock.sendMessage(jid, { text: MESSAGES.errorBackend });
    setStep(jid, 'recibir_msg');
  }
}

export async function advance(sock, jid, text) {
  // Hydrate from backend so a restarted bot picks up where each user left off.
  await ensureLoaded(jid);
  // "reporte" is recognized in any post-analysis state.
  const session = getSession(jid);
  if (REPORT_RE.test(text) && ['result', 'notify', 'inicio'].includes(session.current_step)) {
    await sendReport(sock, jid);
    return;
  }

  switch (session.current_step) {
    case 'inicio': {
      await sock.sendMessage(jid, { text: MESSAGES.bienvenida });
      if (looksLikeGreeting(text)) {
        setStep(jid, 'recibir_msg');
        return;
      }
      await analyzeAndReply(sock, jid, text);
      return;
    }

    case 'recibir_msg':
    case 'result':
      await analyzeAndReply(sock, jid, text);
      return;

    case 'notify': {
      const phone = text.replace(/[^\d]/g, '');
      if (phone.length < 10) {
        await sock.sendMessage(jid, {
          text: 'Número no válido. Mándame +52 con 10 dígitos, o escribe "reporte" para descargar el PDF.',
        });
        return;
      }
      const guardianJid = `${phone}@s.whatsapp.net`;
      const guardianText = MESSAGES.notificacionTutor('PELIGRO', 'WhatsApp');
      try {
        await sock.sendMessage(guardianJid, { text: guardianText });
        await sock.sendMessage(jid, {
          text: '✅ Aviso enviado al adulto de confianza (sin contenido del mensaje). Si necesitas el reporte PDF, escribe "reporte".',
        });
      } catch (err) {
        await sock.sendMessage(jid, {
          text: `No pude enviar el aviso (${err.message}). Llama 088 directamente.`,
        });
      }
      setStep(jid, 'result');
      return;
    }

    default:
      setStep(jid, 'inicio');
      await sock.sendMessage(jid, { text: MESSAGES.bienvenida });
  }
}

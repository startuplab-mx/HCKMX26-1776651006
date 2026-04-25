// State machine:
//   inicio → bienvenida → recibir_msg → (analizando) → result_*
//                                                   ↓ (PELIGRO)
//                                                notify → ask_contribute
//                                                              ↓ sí
//                                                       ask_region → done → inicio
//
//   audio/image → confirm_transcription → (sí) analyzeAndReply / (no) recibir_msg
//
// One call per turn for text: /alert classifies + persists + returns the
// analysis. Last alert id + analysis kept in session for the "reporte"
// command and for ASK_CONTRIBUTE.
import { MESSAGES } from '../config/messages.js';
import {
  ensureLoaded,
  getSession,
  setStep,
  setSessionData,
  getSessionData,
} from '../utils/sessionManager.js';
import {
  registerAlert,
  fetchReportBytes,
  submitContribution,
  submitFeedback,
} from './alertDispatcher.js';

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
const YES_RE = /^\s*(s[ií]|si|sí|yes|y|confirmar|confirmo|ok|dale|adelante)\s*[!.]?\s*$/i;
const NO_RE = /^\s*(no|nop|nope|nah|cancelar|nel)\s*[!.]?\s*$/i;
const SKIP_RE = /^\s*(skip|saltar|omitir|n\/?a|prefiero no|paso)\s*$/i;
// Explicit denial of the alert verdict — distinct from "no quiero contribuir".
// When the user says "no es" / "me equivoqué" / "falso" while we're waiting
// for the guardian phone, treat it as an alert-level deny and feed the
// auto-tuner accordingly.
const DENY_ALERT_RE =
  /^\s*(no\s+es|no\s+es\s+cierto|me\s+equivoqu[eé]|fals[oa]|no\s+(es\s+)?peligro|esto\s+no\s+es|exager(o|aste)|fui\s+yo)\s*[!.]?\s*$/i;

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

async function analyzeAndReply(sock, jid, text, sourceType = 'text') {
  await sock.sendMessage(jid, { text: MESSAGES.recibido });
  setStep(jid, 'analizando');
  try {
    const result = await registerAlert({
      text,
      platform: 'whatsapp',
      source: 'bot',
      session_id: jid,
      source_type: sourceType,
    });
    // Stash the metadata we need later for ASK_CONTRIBUTE — never the raw text.
    setSessionData(jid, {
      lastAlertId: result.id,
      lastAnalysis: {
        platform: 'whatsapp',
        risk_level: result.risk_level,
        risk_score: result.risk_score,
        phase_detected: result.phase_detected,
        categories: result.categories || [],
        pattern_ids: result.pattern_ids || [],
        source_type: sourceType,
        llm_used: !!result.llm_used,
        override_triggered: !!result.override_triggered,
      },
    });
    const fase = PHASE_LABEL[result.phase_detected] || 'Sin fase dominante';
    let reply;
    if (result.risk_level === 'PELIGRO') {
      reply = MESSAGES.resultadoPeligro(result.risk_score, fase);
      setStep(jid, 'notify');
    } else if (result.risk_level === 'ATENCION') {
      reply = MESSAGES.resultadoAtencion(result.risk_score, fase);
      setStep(jid, 'ask_contribute');
    } else {
      reply = MESSAGES.resultadoSeguro(result.risk_score);
      setStep(jid, 'ask_contribute');
    }
    await sock.sendMessage(jid, { text: reply });

    // ── Phase 4: explainability + escalation banners ──
    if (result.risk_level !== 'SEGURO') {
      const why = MESSAGES.porQue(result.why || []);
      if (why) await sock.sendMessage(jid, { text: why });
      const esc = MESSAGES.escalamientoDetectado(result.escalation);
      if (esc) await sock.sendMessage(jid, { text: esc });
    }

    // Legal guide: send only when risk_level is not SEGURO and the API
    // returned a populated `legal` block. Capped to 5 actions / 3 authorities
    // to keep the WA message readable; the PDF carries the full list.
    if (result.risk_level !== 'SEGURO' && result.legal) {
      const guia = MESSAGES.guiaLegal(result.legal);
      if (guia) await sock.sendMessage(jid, { text: guia });
    }

    if (result.risk_level !== 'PELIGRO') {
      // For SAFE / ATTENTION we go straight to the contribute prompt; for
      // DANGER we ask after the guardian-notify flow completes.
      await sock.sendMessage(jid, { text: MESSAGES.preguntarContribuir });
    }
  } catch (err) {
    await sock.sendMessage(jid, { text: MESSAGES.errorBackend });
    setStep(jid, 'recibir_msg');
  }
}

async function handleConfirmTranscription(sock, jid, text) {
  const pending = getSessionData(jid, 'pendingTranscription');
  const sourceType = getSessionData(jid, 'pendingSourceType') || 'text';
  if (YES_RE.test(text)) {
    setSessionData(jid, { pendingTranscription: null, pendingSourceType: null });
    await analyzeAndReply(sock, jid, pending, sourceType);
    return;
  }
  if (NO_RE.test(text)) {
    setSessionData(jid, { pendingTranscription: null, pendingSourceType: null });
    await sock.sendMessage(jid, { text: MESSAGES.transcripcionRechazada });
    setStep(jid, 'recibir_msg');
    return;
  }
  await sock.sendMessage(jid, {
    text: 'Responde *sí* para que lo analice o *no* para descartarlo.',
  });
}

async function fireContribution(sock, jid, region = null) {
  const analysis = getSessionData(jid, 'lastAnalysis');
  if (!analysis) {
    await sock.sendMessage(jid, { text: MESSAGES.contribucionGracias });
    setStep(jid, 'inicio');
    return;
  }
  try {
    await submitContribution({ ...analysis, region });
    await sock.sendMessage(jid, { text: MESSAGES.contribucionGracias });
  } catch (err) {
    await sock.sendMessage(jid, { text: MESSAGES.contribucionError });
  } finally {
    setSessionData(jid, { lastAnalysis: null });
    setStep(jid, 'inicio');
  }
}

export async function advance(sock, jid, text) {
  await ensureLoaded(jid);
  const session = getSession(jid);

  // "reporte" works in any post-analysis state.
  if (
    REPORT_RE.test(text) &&
    ['result', 'notify', 'ask_contribute', 'inicio'].includes(session.current_step)
  ) {
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

    case 'confirm_transcription':
      await handleConfirmTranscription(sock, jid, text);
      return;

    case 'notify': {
      // Explicit denial → feed the auto-tuner as a possible false positive
      // and exit the flow gracefully, no guardian notify, no contribute.
      if (DENY_ALERT_RE.test(text)) {
        const lastAlertId = getSessionData(jid, 'lastAlertId');
        const lastAnalysis = getSessionData(jid, 'lastAnalysis') || {};
        await submitFeedback({
          feedback_type: 'deny',
          alert_id: lastAlertId,
          session_id: jid,
          pattern_ids: lastAnalysis.pattern_ids || [],
          heuristic_score: lastAnalysis.risk_score,
          final_score: lastAnalysis.risk_score,
        });
        await sock.sendMessage(jid, { text: MESSAGES.falsoPositivoReconocido });
        setSessionData(jid, { lastAnalysis: null });
        setStep(jid, 'inicio');
        return;
      }

      const phone = text.replace(/[^\d]/g, '');
      if (phone.length < 10) {
        await sock.sendMessage(jid, {
          text: 'Número no válido. Mándame +52 con 10 dígitos, escribe "no" si te equivocaste, o "reporte" para el PDF.',
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
      // Implicit confirm: the user acted on the PELIGRO verdict by handing
      // over the guardian phone. Feed it to the auto-tuner so the patterns
      // that fired keep their weight (or move up).
      const lastAlertId = getSessionData(jid, 'lastAlertId');
      const lastAnalysis = getSessionData(jid, 'lastAnalysis') || {};
      await submitFeedback({
        feedback_type: 'confirm',
        alert_id: lastAlertId,
        session_id: jid,
        pattern_ids: lastAnalysis.pattern_ids || [],
        heuristic_score: lastAnalysis.risk_score,
        final_score: lastAnalysis.risk_score,
      });
      setStep(jid, 'ask_contribute');
      await sock.sendMessage(jid, { text: MESSAGES.preguntarContribuir });
      return;
    }

    case 'ask_contribute':
      if (YES_RE.test(text)) {
        setStep(jid, 'ask_region');
        await sock.sendMessage(jid, { text: MESSAGES.preguntarRegion });
        return;
      }
      if (NO_RE.test(text)) {
        await sock.sendMessage(jid, { text: MESSAGES.contribucionRechazada });
        setSessionData(jid, { lastAnalysis: null });
        setStep(jid, 'inicio');
        return;
      }
      await sock.sendMessage(jid, {
        text: 'Responde *sí* para contribuir anónimamente o *no* para terminar.',
      });
      return;

    case 'ask_region': {
      const region = SKIP_RE.test(text) ? null : text.trim().slice(0, 80) || null;
      await fireContribution(sock, jid, region);
      return;
    }

    default:
      setStep(jid, 'inicio');
      await sock.sendMessage(jid, { text: MESSAGES.bienvenida });
  }
}

// Entry point used by audio/image handlers in messageHandler.js. They
// stash the transcription on the session and bounce the user into the
// confirm_transcription state so they always see the text before analysis.
export async function startTranscriptionConfirmation(sock, jid, text, sourceType) {
  setSessionData(jid, {
    pendingTranscription: text,
    pendingSourceType: sourceType,
  });
  setStep(jid, 'confirm_transcription');
  await sock.sendMessage(jid, { text: MESSAGES.confirmarTranscripcion(text) });
}

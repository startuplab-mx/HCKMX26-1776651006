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
  resetSession,
  checkRateLimit,
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
  /^(hola|hey|hi|buenas|qué onda|que onda|qué pex|que pex|qu[eé] tal|buenos dias|buenas tardes|buenas noches|holi|wenas|saludos|ola|holiwis|holuli|hi5|hu|aki|aqui|hello)[\s!.,?¿¡]*$/i;

// Emotional/distress states — fire empathy first, analysis second.
// User typing "tengo miedo" / "no se que hacer" before sending the message
// is reaching out for help. The bot acknowledges before asking for content.
const DISTRESS_RE =
  /\b(tengo\s+miedo|estoy\s+(asustad[oa]|nervios[oa]|preocupad[oa]|amenazad[oa])|no\s+s[eé]\s+(qu[eé]|que)\s+hacer|me\s+siento\s+(mal|terrible|horrible|atrapad[oa])|necesito\s+ayuda|ay[uú]dame|please\s+help|estoy\s+en\s+peligro|me\s+quiero\s+morir)\b/i;

// "Solo quería platicar" / "quiero hablar con alguien" — emotional support
// not analysis. Acknowledge and offer to either listen or analyze.
const SUPPORT_RE =
  /\b(quiero\s+(hablar|platicar|desahogarme)|necesito\s+platicar|me\s+puedes\s+escuchar|alguien\s+me\s+escucha)\b/i;
const REPORT_RE = /^\s*\/?\s*(reporte|report|pdf|descargar)\s*$/i;
const YES_RE = /^\s*(s[ií]|si|sí|yes|y|confirmar|confirmo|ok|dale|adelante)\s*[!.]?\s*$/i;
const NO_RE = /^\s*(no|nop|nope|nah|cancelar|nel)\s*[!.]?\s*$/i;
const SKIP_RE = /^\s*(skip|saltar|omitir|n\/?a|prefiero no|paso)\s*$/i;

// Universal slash-style commands. Match in ANY state — they short-circuit
// before the FSM dispatch so the user always has an escape hatch.
const MENU_RE   = /^\s*\/?\s*(menu|men[uú]|comandos|opciones)\s*$/i;
const HELP_RE   = /^\s*\/?\s*(ayuda|help|info|que\s+haces|qu[eé]\s+haces|c[oó]mo\s+funciona)\s*$/i;
const RESET_RE  = /^\s*\/?\s*(reset|reiniciar|empezar(\s+de)?\s*nuevo|cancelar\s*todo|salir)\s*$/i;
const STATUS_RE = /^\s*\/?\s*(estado|status|d(o|ó)nde\s+voy)\s*$/i;
const PRIVACY_RE = /^\s*\/?\s*(privacidad|datos|qu[eé]\s+guardas|borra\s*mis\s*datos)\s*$/i;

// Conversational closers — "gracias", "ok", "bye", "listo", "fin". When any
// of these arrive, we acknowledge with a friendly close and reset to inicio
// WITHOUT triggering /analyze. Without this, the bot was re-classifying
// every "gracias" as a fresh message (Marco surfaced this Apr 25).
//
// Includes "no" / "ya no" / "no gracias" / "estoy bien" — caught Apr 25
// 15:17: after the contribution flow (¿Hay algo más que quieras analizar?)
// the user typed "No" and the bot ran /analyze on the literal "No",
// returning SEGURO 0% AND re-prompting for contribution. Now closes cleanly.
const CLOSE_RE = /^\s*(no|nop|nope|nel|nada|nada\s+m[aá]s|ya\s+no|nada\s+m[aá]s\s+por\s+hoy|gracias|grax|thx|thanks|no\s+gracias|estoy\s+bien|todo\s+bien|todo\s+bien\s+gracias|ok|okay|listo|chido|sale|sale\s+pues|bye|adi[oó]s|hasta\s+luego|fin|ya|ya\s+est[áa]|nos\s+vemos|cu[ií]date|cu[ií]dale)\s*[!.\s😊🙏👍]*\s*$/i;
// Affirmation-as-command — "si", "claro", "obvio" without context — also
// shouldn't trigger /analyze in inicio state. We treat them as friendly
// acknowledgements and prompt the user for what they actually want.
const AFFIRM_NO_CONTEXT_RE = /^\s*(s[ií]|claro|obvio|por\s+supuesto|dale|seguro)\s*[!.]?\s*$/i;
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
  // Per-JID rate limit: 5 /alert per 60s. Without this a malicious user
  // (or buggy WA client retry loop) could burn LLM budget rapidly.
  const rl = checkRateLimit(jid);
  if (!rl.ok) {
    await sock.sendMessage(jid, {
      text: `⏳ Estás mandando muchos análisis muy seguido. Espera ${rl.retryAfterSec}s y mándame el siguiente. Si urge: *088* (Policía Cibernética).`,
    });
    return;
  }
  await sock.sendMessage(jid, { text: MESSAGES.recibidoRandom() });
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

  // ---------- Universal commands (short-circuit before FSM dispatch) ----------
  // These let the user always escape the current state without re-greeting.

  if (MENU_RE.test(text)) {
    await sock.sendMessage(jid, { text: MESSAGES.menu });
    return;
  }
  if (HELP_RE.test(text)) {
    await sock.sendMessage(jid, { text: MESSAGES.ayuda });
    return;
  }
  if (PRIVACY_RE.test(text)) {
    await sock.sendMessage(jid, { text: MESSAGES.privacidad });
    return;
  }
  if (STATUS_RE.test(text)) {
    const stepLabel = MESSAGES.estadoLabels?.[session.current_step] || session.current_step;
    await sock.sendMessage(jid, {
      text: `📍 Estado actual: *${stepLabel}*\n\nEscribe "menu" para ver tus opciones, o "reset" para empezar de cero.`,
    });
    return;
  }
  if (RESET_RE.test(text)) {
    resetSession(jid);
    await sock.sendMessage(jid, {
      text: '🔄 Reinicié la conversación. Mándame el mensaje sospechoso cuando quieras.',
    });
    return;
  }

  // Conversational close: "gracias", "ok", "bye"… acknowledge + reset.
  // Only trigger when we're past an analysis (i.e. there's no in-progress
  // multi-step state). Otherwise let the FSM handle the literal token —
  // e.g. "ok" inside ask_contribute is a different signal.
  if (CLOSE_RE.test(text) && ['inicio', 'recibir_msg', 'result'].includes(session.current_step)) {
    const variants = [
      '🙏 Gracias por confiar en Nahual. Cuando lo necesites, aquí estoy. Cuídate. 🛡️',
      '🛡️ Aquí estoy si vuelves a necesitar ayuda. Cuídate mucho.',
      '👍 Listo. Si recibes otro mensaje sospechoso, mándamelo. Cuídate.',
    ];
    const reply = variants[Math.floor(Math.random() * variants.length)];
    await sock.sendMessage(jid, { text: reply });
    resetSession(jid);
    return;
  }

  // Bare affirmation in initial states with no question pending → prompt.
  // Without this, "si" by itself ran through analyze and came back SEGURO.
  if (AFFIRM_NO_CONTEXT_RE.test(text) && session.current_step === 'inicio') {
    await sock.sendMessage(jid, {
      text: '¿"Sí" a qué? 🙂  Mándame el mensaje sospechoso (texto, audio o captura) y lo analizo. O escribe *menu* para ver opciones.',
    });
    return;
  }

  // Distress / SOS — empathy first, then offer a path.
  if (DISTRESS_RE.test(text) && ['inicio', 'recibir_msg'].includes(session.current_step)) {
    await sock.sendMessage(jid, { text: MESSAGES.distress });
    setStep(jid, 'recibir_msg'); // ready for the actual sus message
    return;
  }
  // "Quiero platicar / desahogarme" — acknowledge + offer.
  if (SUPPORT_RE.test(text) && session.current_step === 'inicio') {
    await sock.sendMessage(jid, { text: MESSAGES.soporte });
    setStep(jid, 'recibir_msg');
    return;
  }

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
      // Only show the welcome banner if the user actually greeted ("hola",
      // "buenas", "menu"…) or if this is their first interaction (no
      // session.lastAnalysis yet). Otherwise the bot becomes annoyingly
      // chatty — it greeted on every reset back to 'inicio', which Marco
      // surfaced during field testing on Apr 25.
      if (looksLikeGreeting(text)) {
        await sock.sendMessage(jid, { text: MESSAGES.bienvenida });
        setStep(jid, 'recibir_msg');
        return;
      }
      const seenAlready = !!getSessionData(jid, 'lastAlertId');
      if (!seenAlready) {
        await sock.sendMessage(jid, { text: MESSAGES.bienvenida });
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

      const digits = text.replace(/[^\d]/g, '');
      if (digits.length < 10) {
        await sock.sendMessage(jid, {
          text: 'Número no válido. Mándame +52 con 10 dígitos, escribe "no" si te equivocaste, o "reporte" para el PDF.',
        });
        return;
      }
      // WhatsApp JID normalisation for Mexican numbers.
      // Accepted inputs:
      //   • 10 digits             → 521XXXXXXXXXX (mobile, with legacy '1')
      //   • 12 digits, starts 52  → 521XXXXXXXXXX (insert mobile prefix)
      //   • 13 digits, starts 521 → use as-is
      //   • Anything else with country code (US, Argentina…) → use raw digits
      let normalized;
      if (digits.length === 10) normalized = `521${digits}`;
      else if (digits.length === 12 && digits.startsWith('52')) normalized = `521${digits.slice(2)}`;
      else if (digits.length === 13 && digits.startsWith('521')) normalized = digits;
      else normalized = digits; // foreign number — let WA decide

      const guardianJid = `${normalized}@s.whatsapp.net`;

      // Verify the guardian number actually exists on WhatsApp before
      // pretending we delivered the alert. Baileys answers with `exists:true`
      // and a fixed-up JID when the number is registered. This avoids the
      // silent black-hole case where sendMessage queues to a non-existent
      // JID and the operator never finds out.
      let resolvedJid = guardianJid;
      try {
        const lookup = await sock.onWhatsApp(guardianJid);
        const hit = Array.isArray(lookup) ? lookup[0] : null;
        if (!hit || !hit.exists) {
          await sock.sendMessage(jid, {
            text: 'Ese número no parece estar en WhatsApp. Verifícalo y envíame uno donde sí pueda contactar al adulto de confianza.',
          });
          return;
        }
        // WA returns the canonical JID (sometimes adds/removes the legacy '1').
        if (hit.jid) resolvedJid = hit.jid;
      } catch (lookupErr) {
        console.warn(`[guardian] onWhatsApp lookup failed: ${lookupErr.message}`);
        // Continue with the best-effort JID — better to try than to drop.
      }

      const guardianText = MESSAGES.notificacionTutor('PELIGRO', 'WhatsApp');
      const lastAlertId = getSessionData(jid, 'lastAlertId');
      try {
        await sock.sendMessage(resolvedJid, { text: guardianText });

        // Also push the PDF — the guardian needs the full evidence package
        // (folio + legal block + categories), not just a one-line alert.
        let pdfDelivered = false;
        if (lastAlertId) {
          try {
            const buf = await fetchReportBytes(lastAlertId);
            const folio = `NAH-2026-${String(lastAlertId).padStart(4, '0')}`;
            await sock.sendMessage(resolvedJid, {
              document: buf,
              mimetype: 'application/pdf',
              fileName: `${folio}.pdf`,
              caption: `📄 Reporte oficial Nahual · ${folio}\n\nEste reporte contiene categorías detectadas, marco legal aplicable y autoridades. NO incluye el contenido original del mensaje.`,
            });
            pdfDelivered = true;
          } catch (pdfErr) {
            // Don't block the user notification on a PDF failure.
            console.warn(`[guardian] PDF send failed for alert ${lastAlertId}: ${pdfErr.message}`);
          }
        }

        await sock.sendMessage(jid, {
          text: pdfDelivered
            ? '✅ Aviso + reporte PDF enviados al adulto de confianza (sin contenido del mensaje original).'
            : '✅ Aviso enviado al adulto de confianza. El PDF no se pudo adjuntar — escribe "reporte" para que te lo mande aquí y reenvíalo manualmente.',
        });
      } catch (err) {
        await sock.sendMessage(jid, {
          text: `No pude enviar el aviso (${err.message}). Llama al 088 directamente o escribe "reporte" para descargar el PDF y reenviarlo manualmente.`,
        });
      }
      // Implicit confirm: the user acted on the PELIGRO verdict by handing
      // over the guardian phone. Feed it to the auto-tuner so the patterns
      // that fired keep their weight (or move up). `lastAlertId` was already
      // captured above for the PDF dispatch — reuse it here.
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
      // Validate the region input. Real Mexican states/cities are 3-40
      // chars, mostly letters + spaces + a few accents. Reject obvious
      // garbage (questions, sentences with verbs, very long noise) so the
      // research dataset stays clean — we caught noise like
      // "Hola cuantos años tienes?" leaking into by_region.
      let region = null;
      if (!SKIP_RE.test(text)) {
        const cleaned = text.trim().replace(/\s+/g, ' ');
        const looksLikeQuestion = /\?|¿/.test(cleaned);
        const looksLikeSentence = cleaned.split(' ').length > 6;
        const validShape = /^[A-Za-zÁÉÍÓÚáéíóúÑñ ,.\-]{2,40}$/.test(cleaned);
        if (validShape && !looksLikeQuestion && !looksLikeSentence) {
          // Title-case for consistency in the panel ("saltillo" → "Saltillo").
          region = cleaned
            .toLowerCase()
            .replace(/(^|\s)\S/g, (c) => c.toUpperCase())
            .slice(0, 60);
        } else {
          await sock.sendMessage(jid, {
            text: 'No reconocí la región. Mándame sólo el nombre (ej. "Coahuila", "CDMX") o escribe *paso* para omitir.',
          });
          return; // stay in ask_region
        }
      }
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

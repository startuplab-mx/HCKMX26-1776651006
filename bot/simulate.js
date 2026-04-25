// Offline bot simulation — exercises the FSM end-to-end without WhatsApp.
// Pre-req: backend running (uvicorn main:app --reload --port 8000).
//
// Usage: BOT_BACKEND_URL=http://localhost:8000 node simulate.js
//
// Phase 3 additions: drives audio + image flows by injecting transcribed
// text directly into the FSM (we don't need real audio bytes for the
// offline path). The contribution flow is exercised at the end.
import 'dotenv/config';
import { advance, startTranscriptionConfirmation } from './handlers/flowController.js';
import { resetSession } from './utils/sessionManager.js';

const FAKE_JID = 'demo-user@s.whatsapp.net';

const fakeSocket = {
  async sendMessage(jid, payload) {
    const target = jid === FAKE_JID ? 'BOT→USER' : `BOT→GUARDIAN(${jid})`;
    if (payload.document) {
      console.log(
        `\n[${target}] [DOCUMENT ${payload.fileName} · ${payload.mimetype} · ${payload.document.length} bytes]`,
      );
      if (payload.caption) console.log(`  caption: ${payload.caption}`);
      return;
    }
    const text = payload.text || JSON.stringify(payload);
    console.log(`\n[${target}]`);
    console.log(text.split('\n').map((l) => `  ${l}`).join('\n'));
  },
};

async function userSays(text) {
  console.log(`\n[USER→BOT] ${text}`);
  await advance(fakeSocket, FAKE_JID, text);
}

async function userSendsAudio(transcribedText) {
  console.log(`\n[USER→BOT] [audio] (transcribed: "${transcribedText}")`);
  await startTranscriptionConfirmation(fakeSocket, FAKE_JID, transcribedText, 'audio');
}

async function userSendsImage(extractedText) {
  console.log(`\n[USER→BOT] [image] (OCR: "${extractedText}")`);
  await startTranscriptionConfirmation(fakeSocket, FAKE_JID, extractedText, 'image');
}

async function main() {
  resetSession(FAKE_JID);
  console.log('🛡️  NAHUAL BOT — OFFLINE SIMULATION (Phase 3)\n');

  // ── Scenario A: text + DANGER + guardian + report + contribute ───────
  console.log('\n=== A. Text → PELIGRO → notify → reporte → contribute ===');
  await userSays('hola');
  await userSays('si intentas escapar te descuartizo, sabemos donde vives');
  await userSays('+525512345678'); // guardian
  await userSays('reporte');       // PDF
  await userSays('sí');            // contribute? yes
  await userSays('Coahuila');      // region

  // ── Scenario B: audio with captacion → confirm → analyze ─────────────
  console.log('\n\n=== B. Audio → confirm → ATENCION captación → contribute (no) ===');
  resetSession(FAKE_JID);
  await userSendsAudio('yo quiero jale, te pago el viaje, $15,000 semanales 🍕');
  await userSays('sí');           // confirm transcription
  await userSays('no');           // contribute? no

  // ── Scenario C: image with sextortion → confirm → DANGER ─────────────
  console.log('\n\n=== C. Image OCR → DANGER override → guardian → skip contribute ===');
  resetSession(FAKE_JID);
  await userSendsImage('si no pagas las fotos van a tu escuela. deposita 500 spei');
  await userSays('sí');                 // confirm transcription
  await userSays('+525587654321');      // guardian
  await userSays('sí');                 // contribute
  await userSays('paso');               // skip region

  // ── Scenario D: user rejects transcription → returns to recibir_msg ──
  console.log('\n\n=== D. Audio rejected → bot waits for text ===');
  resetSession(FAKE_JID);
  await userSendsAudio('mañana hay examen de bio');
  await userSays('no');           // reject
  await userSays('vienes al cumple el sabado'); // safe text

  console.log('\n✅ Simulación completa.');
}

main().catch((err) => {
  console.error('❌ simulate failed:', err.message);
  process.exit(1);
});

// Offline bot simulation — exercises the FSM end-to-end without WhatsApp.
// Pre-req: backend running (uvicorn main:app --reload --port 8000).
//
// Usage: BOT_BACKEND_URL=http://localhost:8000 node simulate.js
import 'dotenv/config';
import { advance } from './handlers/flowController.js';
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

async function main() {
  resetSession(FAKE_JID);
  console.log('🛡️  NAHUAL BOT — OFFLINE SIMULATION\n');

  // 1. First contact: greeting → only welcome
  await userSays('hola');

  // 2. Coercion message → triggers PELIGRO + override
  await userSays('si intentas escapar te descuartizo, sabemos donde vives');

  // 3. User sends guardian phone → bot notifies (no content)
  await userSays('+525512345678');

  // 4. User asks for the PDF report → bot sends WhatsApp document
  await userSays('reporte');

  // 5. Substantive first paste in fresh session → analyzed inline
  resetSession(FAKE_JID);
  await userSays('yo quiero jale, te pago el viaje, $15,000 semanales 🍕');

  console.log('\n✅ Simulación completa.');
}

main().catch((err) => {
  console.error('❌ simulate failed:', err.message);
  process.exit(1);
});

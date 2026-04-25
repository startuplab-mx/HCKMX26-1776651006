// Nahual WhatsApp Bot — entry point
// Phase 2 (bot wiring) builds on top of this. For Phase 1 this is a working
// scaffold: connects to WhatsApp, prints QR, and routes messages through
// messageHandler. State machine + flow controller live in handlers/.

import 'dotenv/config';
import { makeWASocket, useMultiFileAuthState, DisconnectReason } from '@whiskeysockets/baileys';
import qrcode from 'qrcode-terminal';
import pino from 'pino';
import { handleIncomingMessage } from './handlers/messageHandler.js';

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

const SESSION_DIR = process.env.BOT_SESSION_DIR || './auth_info_baileys';

async function start() {
  const { state, saveCreds } = await useMultiFileAuthState(SESSION_DIR);

  const sock = makeWASocket({
    auth: state,
    logger: pino({ level: 'silent' }),
    printQRInTerminal: false,
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', (update) => {
    const { connection, lastDisconnect, qr } = update;
    if (qr) {
      console.log('\n🛡️  Escanea este QR con WhatsApp → Dispositivos vinculados:\n');
      qrcode.generate(qr, { small: true });
    }
    if (connection === 'close') {
      const shouldReconnect =
        lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
      logger.warn({ reason: lastDisconnect?.error?.message }, 'connection closed');
      if (shouldReconnect) start();
    } else if (connection === 'open') {
      logger.info('✅ Nahual bot conectado a WhatsApp');
    }
  });

  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify') return;
    for (const msg of messages) {
      try {
        await handleIncomingMessage(sock, msg);
      } catch (err) {
        logger.error({ err: err.message }, 'message handler crashed');
      }
    }
  });
}

start().catch((err) => {
  logger.error({ err: err.message }, 'fatal startup error');
  process.exit(1);
});

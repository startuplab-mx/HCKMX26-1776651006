// Nahual WhatsApp Bot — entry point
// Phase 2 (bot wiring) builds on top of this. For Phase 1 this is a working
// scaffold: connects to WhatsApp, prints QR, and routes messages through
// messageHandler. State machine + flow controller live in handlers/.

import 'dotenv/config';
import {
  makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
} from '@whiskeysockets/baileys';
import qrcode from 'qrcode-terminal';
import QRCode from 'qrcode';
import fs from 'node:fs';
import path from 'node:path';
import pino from 'pino';
import { handleIncomingMessage } from './handlers/messageHandler.js';

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

const SESSION_DIR = process.env.BOT_SESSION_DIR || './auth_info_baileys';

// Reconnect bookkeeping. Without this `start()` recursed without backoff and
// kept stale socket listeners alive — both real risks the resilience audit
// flagged. Backoff: 0.5s × 2^n, capped at 60s, jittered ±25%.
let RECONNECT_ATTEMPTS = 0;
let CURRENT_SOCK = null;

function scheduleReconnect() {
  RECONNECT_ATTEMPTS += 1;
  const base = Math.min(60000, 500 * Math.pow(2, RECONNECT_ATTEMPTS));
  const jitter = base * 0.25 * (Math.random() * 2 - 1);
  const delay = Math.max(500, Math.floor(base + jitter));
  // Tear down the old socket FIRST so its listeners do not double-fire.
  if (CURRENT_SOCK) {
    try { CURRENT_SOCK.ev.removeAllListeners(); } catch {}
    try { CURRENT_SOCK.end?.(); } catch {}
    CURRENT_SOCK = null;
  }
  logger.warn({ attempt: RECONNECT_ATTEMPTS, delay }, 'reconnecting after backoff');
  setTimeout(() => start().catch((e) => logger.error({ err: e.message }, 'reconnect failed')), delay);
}

async function start() {
  const { state, saveCreds } = await useMultiFileAuthState(SESSION_DIR);

  // Without this WhatsApp rejects the handshake on any baked-in WA version
  // older than the current server-side protocol — even on a fresh install.
  // fetchLatestBaileysVersion() pulls the active version from a CDN; falls
  // back to the bundled version if the lookup fails (which is fine on dev).
  let waVersion;
  try {
    const v = await fetchLatestBaileysVersion();
    waVersion = v.version;
    logger.info({ version: waVersion, isLatest: v.isLatest }, 'WA version negotiated');
  } catch (err) {
    logger.warn({ err: err.message }, 'fetchLatestBaileysVersion failed, using bundled');
  }

  const sock = makeWASocket({
    auth: state,
    version: waVersion,
    logger: pino({ level: 'silent' }),
    browser: ['Nahual', 'Chrome', '20.0.0'],
  });
  CURRENT_SOCK = sock;

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', (update) => {
    const { connection, lastDisconnect, qr } = update;
    if (qr) {
      console.log('\n🛡️  Escanea este QR con WhatsApp → Dispositivos vinculados:\n');
      qrcode.generate(qr, { small: true });
      // Also persist a PNG to a well-known path so the operator can scan it
      // from a browser (handy for headless deploys where reading the journal
      // is awkward). Path is overridable via BOT_QR_FILE.
      const qrPath = process.env.BOT_QR_FILE || '/opt/nahual/panel/bot-qr.png';
      QRCode.toFile(qrPath, qr, { width: 400, margin: 2 })
        .then(() => logger.info({ qrPath }, 'QR written to disk'))
        .catch((err) => logger.warn({ err: err.message }, 'failed to persist QR'));
    }
    if (connection === 'close') {
      const shouldReconnect =
        lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
      logger.warn({ reason: lastDisconnect?.error?.message, attempts: RECONNECT_ATTEMPTS }, 'connection closed');
      if (shouldReconnect) {
        scheduleReconnect();
      } else {
        logger.error('logged out — manual QR re-scan required');
      }
    } else if (connection === 'open') {
      RECONNECT_ATTEMPTS = 0; // success resets backoff
      logger.info('✅ Nahual bot conectado a WhatsApp');
      // Wipe the QR PNG once paired so a stale image can't trick a third
      // party into linking the wrong device.
      const qrPath = process.env.BOT_QR_FILE || '/opt/nahual/panel/bot-qr.png';
      try { fs.existsSync(qrPath) && fs.unlinkSync(qrPath); } catch {}
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

// Graceful shutdown for systemd. Without this, systemd waits ~90s on the
// default TimeoutStopSec before SIGKILL; with it, we close the socket
// cleanly and exit fast on `systemctl restart nahual-bot`.
let SHUTTING_DOWN = false;
function gracefulShutdown(signal) {
  if (SHUTTING_DOWN) return;
  SHUTTING_DOWN = true;
  logger.info({ signal }, 'shutting down gracefully');
  try { CURRENT_SOCK?.ev?.removeAllListeners?.(); } catch {}
  try { CURRENT_SOCK?.end?.(); } catch {}
  // Give Baileys a moment to flush pending sends, then exit.
  setTimeout(() => process.exit(0), 1500);
}
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT',  () => gracefulShutdown('SIGINT'));

start().catch((err) => {
  logger.error({ err: err.message }, 'fatal startup error');
  process.exit(1);
});

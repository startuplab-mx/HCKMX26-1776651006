// Receives Baileys messages, extracts text, routes to flow controller.
import { extractText, isSupportedTextMessage, isMultimedia } from '../utils/textExtractor.js';
import { advance } from './flowController.js';
import { MESSAGES } from '../config/messages.js';

export async function handleIncomingMessage(sock, msg) {
  if (!msg.message || msg.key.fromMe) return;
  const jid = msg.key.remoteJid;
  if (!jid || jid.endsWith('@g.us')) return; // skip groups

  if (isMultimedia(msg) && !isSupportedTextMessage(msg)) {
    await sock.sendMessage(jid, { text: MESSAGES.rechazoMultimedia });
    return;
  }

  const text = extractText(msg);
  if (!text) return;

  await advance(sock, jid, text);
}

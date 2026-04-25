// Receives Baileys messages, routes by media type. Audio → /transcribe,
// image → /ocr, text → flowController.advance directly. Sticker / video /
// document still get a polite rejection because OCR on video frames is
// out of scope for the hackathon.
import { downloadMediaMessage } from '@whiskeysockets/baileys';

import { advance, startTranscriptionConfirmation } from './flowController.js';
import { transcribeAudio, ocrImage } from './alertDispatcher.js';
import { extractText } from '../utils/textExtractor.js';
import { MESSAGES } from '../config/messages.js';

const AUDIO_MIME_DEFAULT = 'audio/ogg';
const IMAGE_MIME_DEFAULT = 'image/png';

async function downloadBuffer(msg) {
  return downloadMediaMessage(msg, 'buffer', {});
}

async function handleAudioMessage(sock, jid, msg) {
  await sock.sendMessage(jid, { text: MESSAGES.audioRecibido });
  try {
    const buffer = await downloadBuffer(msg);
    const audio = msg.message?.audioMessage || msg.message?.pttMessage || {};
    const mime = audio.mimetype || AUDIO_MIME_DEFAULT;
    const { text } = await transcribeAudio(buffer, 'audio.ogg', mime);
    if (!text || text.trim().length === 0) {
      await sock.sendMessage(jid, { text: MESSAGES.audioVacio });
      return;
    }
    await startTranscriptionConfirmation(sock, jid, text, 'audio');
  } catch (err) {
    const status = err.response?.status;
    if (status === 503) {
      await sock.sendMessage(jid, { text: MESSAGES.audioNoConfigurado });
    } else {
      console.error('[audio]', err.message);
      await sock.sendMessage(jid, { text: MESSAGES.audioError });
    }
  }
}

async function handleImageMessage(sock, jid, msg) {
  await sock.sendMessage(jid, { text: MESSAGES.imagenRecibida });
  try {
    const buffer = await downloadBuffer(msg);
    const image = msg.message?.imageMessage || {};
    const mime = image.mimetype || IMAGE_MIME_DEFAULT;
    const { text } = await ocrImage(buffer, 'screenshot.png', mime);
    if (!text || text.trim().length === 0) {
      await sock.sendMessage(jid, { text: MESSAGES.imagenSinTexto });
      return;
    }
    await startTranscriptionConfirmation(sock, jid, text, 'image');
  } catch (err) {
    const status = err.response?.status;
    if (status === 503) {
      await sock.sendMessage(jid, { text: MESSAGES.imagenNoConfigurada });
    } else {
      console.error('[image]', err.message);
      await sock.sendMessage(jid, { text: MESSAGES.imagenError });
    }
  }
}

export async function handleIncomingMessage(sock, msg) {
  if (!msg.message || msg.key.fromMe) return;
  const jid = msg.key.remoteJid;
  if (!jid || jid.endsWith('@g.us')) return; // skip groups

  const m = msg.message;

  if (m.audioMessage || m.pttMessage) {
    return handleAudioMessage(sock, jid, msg);
  }
  if (m.imageMessage) {
    return handleImageMessage(sock, jid, msg);
  }
  if (m.stickerMessage || m.videoMessage || m.documentMessage) {
    await sock.sendMessage(jid, { text: MESSAGES.rechazoMultimedia });
    return;
  }

  const text = extractText(msg);
  if (!text) return;
  await advance(sock, jid, text);
}

// Extract plain text from any Baileys message shape we care about.
export function extractText(msg) {
  const m = msg.message;
  if (!m) return '';
  return (
    m.conversation ||
    m.extendedTextMessage?.text ||
    m.imageMessage?.caption ||
    m.videoMessage?.caption ||
    m.buttonsResponseMessage?.selectedDisplayText ||
    m.listResponseMessage?.title ||
    ''
  ).trim();
}

export function isMultimedia(msg) {
  const m = msg.message || {};
  return Boolean(
    m.audioMessage || m.imageMessage || m.videoMessage || m.stickerMessage || m.documentMessage,
  );
}

export function isSupportedTextMessage(msg) {
  return Boolean(extractText(msg));
}

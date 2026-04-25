// Backend client. Single source of truth for /alert (classify+persist),
// /transcribe (audio→text), /ocr (image→text), /contribute (anonymous
// research metadata), and the PDF download for the "reporte" command.
import axios from 'axios';
import FormData from 'form-data';

const BASE_URL = (process.env.BOT_BACKEND_URL || 'http://localhost:8000').replace(/\/$/, '');
const TIMEOUT_MS = 8000;
const MEDIA_TIMEOUT_MS = 25000; // Groq + Claude Vision can take several seconds

// API key auth: when set, every backend call carries the X-API-Key header so
// even protected endpoints (/sessions/*, /alerts/*) work in production where
// the backend enforces auth. Public endpoints just ignore the extra header.
const API_KEY = (process.env.NAHUAL_API_KEY || '').trim();
const authHeader = API_KEY ? { 'X-API-Key': API_KEY } : {};

export async function registerAlert(payload) {
  const { data } = await axios.post(`${BASE_URL}/alert`, payload, {
    timeout: TIMEOUT_MS,
    headers: { ...authHeader },
  });
  return data;
}

export async function fetchReportBytes(alertId) {
  const { data } = await axios.post(
    `${BASE_URL}/report/${alertId}`,
    null,
    {
      timeout: TIMEOUT_MS,
      responseType: 'arraybuffer',
      headers: { ...authHeader },
    },
  );
  return Buffer.from(data);
}

export async function transcribeAudio(buffer, filename = 'audio.ogg', mimetype = 'audio/ogg') {
  const form = new FormData();
  form.append('file', buffer, { filename, contentType: mimetype });
  const { data } = await axios.post(`${BASE_URL}/transcribe`, form, {
    headers: { ...form.getHeaders(), ...authHeader },
    timeout: MEDIA_TIMEOUT_MS,
    maxBodyLength: Infinity,
    maxContentLength: Infinity,
  });
  return data; // { text, source }
}

export async function ocrImage(buffer, filename = 'screenshot.png', mimetype = 'image/png') {
  const form = new FormData();
  form.append('file', buffer, { filename, contentType: mimetype });
  const { data } = await axios.post(`${BASE_URL}/ocr`, form, {
    headers: { ...form.getHeaders(), ...authHeader },
    timeout: MEDIA_TIMEOUT_MS,
    maxBodyLength: Infinity,
    maxContentLength: Infinity,
  });
  return data;
}

export async function submitContribution(payload) {
  const { data } = await axios.post(`${BASE_URL}/contribute`, payload, {
    timeout: TIMEOUT_MS,
    headers: { ...authHeader },
  });
  return data;
}

export async function submitFeedback(payload) {
  // Best-effort: failures must NOT bubble up into the bot flow.
  try {
    await axios.post(`${BASE_URL}/feedback`, payload, {
      timeout: TIMEOUT_MS,
      headers: { ...authHeader },
    });
  } catch (err) {
    const code = err.response ? err.response.status : err.code || err.message;
    console.warn(`[feedback] sync failed: ${code}`);
  }
}

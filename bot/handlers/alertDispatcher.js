// Backend client. Single source of truth for /alert (classify+persist),
// /transcribe (audio→text), /ocr (image→text), /contribute (anonymous
// research metadata), and the PDF download for the "reporte" command.
import axios from 'axios';
import FormData from 'form-data';

const BASE_URL = (process.env.BOT_BACKEND_URL || 'http://localhost:8000').replace(/\/$/, '');
const TIMEOUT_MS = 8000;
const MEDIA_TIMEOUT_MS = 25000; // Groq + Claude Vision can take several seconds

export async function registerAlert(payload) {
  const { data } = await axios.post(`${BASE_URL}/alert`, payload, { timeout: TIMEOUT_MS });
  return data;
}

export async function fetchReportBytes(alertId) {
  const { data } = await axios.post(
    `${BASE_URL}/report/${alertId}`,
    null,
    { timeout: TIMEOUT_MS, responseType: 'arraybuffer' },
  );
  return Buffer.from(data);
}

export async function transcribeAudio(buffer, filename = 'audio.ogg', mimetype = 'audio/ogg') {
  const form = new FormData();
  form.append('file', buffer, { filename, contentType: mimetype });
  const { data } = await axios.post(`${BASE_URL}/transcribe`, form, {
    headers: form.getHeaders(),
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
    headers: form.getHeaders(),
    timeout: MEDIA_TIMEOUT_MS,
    maxBodyLength: Infinity,
    maxContentLength: Infinity,
  });
  return data;
}

export async function submitContribution(payload) {
  const { data } = await axios.post(`${BASE_URL}/contribute`, payload, { timeout: TIMEOUT_MS });
  return data;
}

// Backend client. Single source of truth: /alert classifies + persists +
// returns the full analysis. /analyze is exposed for the public API but the
// bot doesn't need it.
import axios from 'axios';

const BASE_URL = (process.env.BOT_BACKEND_URL || 'http://localhost:8000').replace(/\/$/, '');
const TIMEOUT_MS = 8000;

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

// Session store with persistence to backend /sessions endpoints.
//
// Strategy: in-memory cache as the source of truth for hot reads, with
// every mutation synced to the backend via fire-and-forget PUT. On a fresh
// session (cache miss), we attempt a lazy GET so the bot survives restarts.
// All HTTP calls fail-soft — if the backend is unreachable, we degrade to
// in-memory only and log a warning.
import axios from 'axios';

const BASE_URL = (process.env.BOT_BACKEND_URL || 'http://localhost:8000').replace(/\/$/, '');
const TIMEOUT_MS = 3000;
// /sessions/* is a protected endpoint in production. Read NAHUAL_API_KEY from
// the bot's env so persistence works behind the auth wall. When unset, the
// header is empty and dev backends ignore it.
const API_KEY = (process.env.NAHUAL_API_KEY || '').trim();
const authHeader = API_KEY ? { 'X-API-Key': API_KEY } : {};

const SESSIONS = new Map();
const HYDRATING = new Map(); // jid -> Promise to dedupe concurrent hydrations
// Per-JID rate limit: drop bursts of /alert from a single user. The bot
// flow only emits /alert during analyzeAndReply — limiting that protects
// the LLM/Groq spend AND the SQLite write throughput. 5 alerts per 60s
// is generous (real users send <1 alert/min).
const RATE_LIMIT_WINDOW_MS = 60_000;
const RATE_LIMIT_MAX = 5;
const RATE_LIMIT_HITS = new Map(); // jid -> [timestamps]
// Session TTL eviction: stale sessions sit in memory forever otherwise.
// Sweep hourly, drop entries idle > 7 days (sessions older than 7 days
// almost certainly belong to users who won't return).
const SESSION_IDLE_MS = 7 * 24 * 60 * 60 * 1000;
const SESSION_LAST_TOUCH = new Map();

function touchSession(jid) {
  SESSION_LAST_TOUCH.set(jid, Date.now());
}

function evictStaleSessions() {
  const cutoff = Date.now() - SESSION_IDLE_MS;
  let evicted = 0;
  for (const [jid, ts] of SESSION_LAST_TOUCH) {
    if (ts < cutoff) {
      SESSIONS.delete(jid);
      SESSION_LAST_TOUCH.delete(jid);
      evicted += 1;
    }
  }
  if (evicted) console.warn(`[sessionManager] evicted ${evicted} stale sessions`);
}
setInterval(evictStaleSessions, 60 * 60 * 1000); // hourly

export function checkRateLimit(jid) {
  const now = Date.now();
  const hits = (RATE_LIMIT_HITS.get(jid) || []).filter(
    (t) => now - t < RATE_LIMIT_WINDOW_MS,
  );
  if (hits.length >= RATE_LIMIT_MAX) {
    return { ok: false, retryAfterSec: Math.ceil((RATE_LIMIT_WINDOW_MS - (now - hits[0])) / 1000) };
  }
  hits.push(now);
  RATE_LIMIT_HITS.set(jid, hits);
  return { ok: true };
}

function makeDefault() {
  return { current_step: 'inicio', data: {} };
}

async function hydrate(jid) {
  if (HYDRATING.has(jid)) return HYDRATING.get(jid);
  const promise = (async () => {
    try {
      const { data } = await axios.get(`${BASE_URL}/sessions/${encodeURIComponent(jid)}`, {
        timeout: TIMEOUT_MS,
        headers: { ...authHeader },
      });
      SESSIONS.set(jid, { current_step: data.current_step, data: data.data || {} });
    } catch (err) {
      if (err.response && err.response.status === 404) {
        SESSIONS.set(jid, makeDefault());
      } else {
        // Backend unreachable: start fresh in memory; sync will retry on next mutation.
        if (!SESSIONS.has(jid)) SESSIONS.set(jid, makeDefault());
      }
    } finally {
      HYDRATING.delete(jid);
    }
    return SESSIONS.get(jid);
  })();
  HYDRATING.set(jid, promise);
  return promise;
}

export async function ensureLoaded(jid) {
  if (SESSIONS.has(jid)) return SESSIONS.get(jid);
  return hydrate(jid);
}

export function getSession(jid) {
  // Synchronous accessor: returns cached state, defaulting to inicio if missing.
  // Callers should `await ensureLoaded(jid)` once per turn before this.
  if (!SESSIONS.has(jid)) {
    SESSIONS.set(jid, makeDefault());
  }
  touchSession(jid);
  return SESSIONS.get(jid);
}

function syncToBackend(jid) {
  const s = SESSIONS.get(jid);
  if (!s) return;
  axios
    .put(
      `${BASE_URL}/sessions/${encodeURIComponent(jid)}`,
      { current_step: s.current_step, data: s.data },
      { timeout: TIMEOUT_MS, headers: { ...authHeader } },
    )
    .catch((err) => {
      // Fire-and-forget: log and move on. Next mutation retries.
      const code = err.response ? err.response.status : err.code || err.message;
      console.warn(`[sessionManager] sync failed for ${jid}: ${code}`);
    });
}

export function setStep(jid, step) {
  const s = getSession(jid);
  s.current_step = step;
  syncToBackend(jid);
}

export function setSessionData(jid, patch) {
  const s = getSession(jid);
  s.data = { ...s.data, ...patch };
  syncToBackend(jid);
}

export function getSessionData(jid, key) {
  return getSession(jid).data[key];
}

export function resetSession(jid) {
  SESSIONS.delete(jid);
  axios
    .delete(`${BASE_URL}/sessions/${encodeURIComponent(jid)}`, {
      timeout: TIMEOUT_MS,
      headers: { ...authHeader },
    })
    .catch(() => {});
}

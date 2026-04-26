// Resolution rules for the backend base URL:
//   1. Explicit override via `<script>window.NAHUAL_API_URL = "..."</script>`
//      injected before this file (used for cross-origin staging environments).
//   2. Auto-detect: if the panel is being served from localhost / 127.0.0.1 /
//      file://, target the dev backend on :8000. Otherwise return "" so all
//      requests stay same-origin and Nginx (or whatever proxy) routes them.
//   This avoids the 26 Apr 2026 prod regression where the deployed panel
//   defaulted to http://localhost:8000 — every fetch from a remote browser
//   hit *its own* localhost (which has no backend) and the table never
//   refreshed.
function _resolveApiBase() {
  if (typeof window.NAHUAL_API_URL === 'string') return window.NAHUAL_API_URL;
  const host = (typeof location !== 'undefined' && location.hostname) || '';
  if (host === 'localhost' || host === '127.0.0.1' || host === '') {
    return 'http://localhost:8000';
  }
  return ''; // same-origin → /alerts, /stats, etc. proxied by Nginx
}
const API = _resolveApiBase().replace(/\/$/, '');
const REFRESH_MS = 5000;
// API key for protected endpoints (/alerts, /sessions, /precision, /risk-history).
// Override at deploy time with `<script>window.NAHUAL_API_KEY = '...'</script>`
// before this file loads, or via localStorage.setItem('nahual_api_key', '...').
const API_KEY = (
  window.NAHUAL_API_KEY ||
  (window.localStorage && window.localStorage.getItem('nahual_api_key')) ||
  'nahual-hackathon-2026'
);

function authHeaders(extra) {
  const h = Object.assign({}, extra || {});
  if (API_KEY) h['X-API-Key'] = API_KEY;
  return h;
}

const state = {
  filterStatus: '',
  expanded: new Set(),
  history: new Map(),
  legalExpanded: new Set(),
  legal: new Map(),
  whyExpanded: new Set(),
  why: new Map(),
  tsRange: { interval: 'hour', hours: 24 },
  chart: null,
};

async function jget(path) {
  const r = await fetch(`${API}${path}`, { headers: authHeaders() });
  if (!r.ok) throw new Error(`${path} → ${r.status}`);
  return r.json();
}

async function jsend(path, method, body) {
  const r = await fetch(`${API}${path}`, {
    method,
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error(`${path} → ${r.status}`);
  return r.json();
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function pill(level) {
  return `<span class="px-2 py-1 rounded text-xs font-bold pill-${level}">${level}</span>`;
}

function statusPill(status) {
  const label = {
    pending: 'Pendiente',
    reviewed: 'Revisada',
    dismissed: 'Descartada',
    escalated: 'Escalada',
  }[status] || status;
  return `<span class="px-2 py-1 rounded text-xs font-semibold status-${status}">${label}</span>`;
}

function esc(s) {
  return String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

function row(a) {
  const folio = `NAH-2026-${String(a.id).padStart(4, '0')}`;
  const score = (a.risk_score * 100).toFixed(0) + '%';
  const phase = a.phase_detected || '—';
  const ovr = a.override_triggered
    ? '<span class="accent font-bold">SÍ</span>'
    : '<span class="text-white/40">no</span>';
  const isExpanded = state.expanded.has(a.id);
  const hist = isExpanded ? state.history.get(a.id) || [] : [];

  const isLegalExpanded = state.legalExpanded.has(a.id);
  const isWhyExpanded = state.whyExpanded.has(a.id);
  const actions = `
    <div class="flex gap-1 justify-end flex-wrap">
      <button class="btn-sm" data-act="reviewed" data-id="${a.id}">✓ Revisar</button>
      <button class="btn-sm" data-act="escalate" data-id="${a.id}">⚠️ Escalar</button>
      <button class="btn-sm" data-act="dismissed" data-id="${a.id}">✗ Descartar</button>
      <button class="btn-sm" data-act="why" data-id="${a.id}">🧠 ${isWhyExpanded ? 'Ocultar por qué' : '¿Por qué?'}</button>
      <button class="btn-sm" data-act="legal" data-id="${a.id}">📜 ${isLegalExpanded ? 'Ocultar legal' : 'Legal'}</button>
      <button class="btn-sm" data-act="history" data-id="${a.id}">🕑 ${isExpanded ? 'Ocultar' : 'Historial'}</button>
      <a class="btn-sm primary" href="${API}/report/${a.id}" target="_blank" rel="noopener">PDF</a>
    </div>`;

  const mainRow = `
    <tr class="hover:bg-white/5">
      <td class="px-4 py-3 font-mono text-xs">${folio}</td>
      <td class="px-4 py-3 text-xs text-white/70">${a.created_at}</td>
      <td class="px-4 py-3">${esc(a.platform)}</td>
      <td class="px-4 py-3">${pill(a.risk_level)}</td>
      <td class="px-4 py-3 font-semibold">${score}</td>
      <td class="px-4 py-3 capitalize">${esc(phase)}</td>
      <td class="px-4 py-3">${ovr}</td>
      <td class="px-4 py-3">${statusPill(a.status || 'pending')}</td>
      <td class="px-4 py-3">${actions}</td>
    </tr>`;

  let extraRows = '';

  if (isExpanded) {
    extraRows += hist.length === 0
      ? '<tr class="history-row"><td colspan="9" class="px-8 py-2 text-white/50 italic">Sin acciones aún.</td></tr>'
      : hist
          .map(
            (h) => `
        <tr class="history-row">
          <td colspan="9" class="px-8 py-2">
            <span class="text-white/50">${h.created_at}</span>
            · <span class="accent font-semibold">${h.action}</span>
            ${h.from_value ? `· ${h.from_value} → ${h.to_value}` : ''}
            ${h.reviewer ? `· <em>${esc(h.reviewer)}</em>` : ''}
            ${h.notes ? `· ${esc(h.notes)}` : ''}
          </td>
        </tr>`,
          )
          .join('');
  }

  if (isLegalExpanded) {
    const legal = state.legal.get(a.id);
    if (!legal) {
      extraRows += '<tr class="history-row"><td colspan="9" class="px-8 py-2 text-white/50 italic">Cargando marco legal…</td></tr>';
    } else {
      extraRows += renderLegalRow(legal);
    }
  }

  if (isWhyExpanded) {
    const why = state.why.get(a.id);
    if (!why) {
      extraRows += '<tr class="history-row"><td colspan="9" class="px-8 py-2 text-white/50 italic">Reconstruyendo explicaciones…</td></tr>';
    } else {
      extraRows += renderWhyRow(why);
    }
  }

  return mainRow + extraRows;
}

function renderWhyRow(payload) {
  const lines = (payload.why || []);
  const body = lines.length === 0
    ? '<div class="text-white/40 italic">Sin patrones específicos registrados (alerta seguro o histórica anterior a Phase 3).</div>'
    : `<ol class="list-decimal list-inside space-y-1">${lines.map((w) => `<li>${esc(w)}</li>`).join('')}</ol>`;
  const ids = (payload.pattern_ids || []).map((p) => `<code class="text-white/50">${esc(p)}</code>`).join(' ') || '<span class="text-white/40 italic">ninguno</span>';
  return `
    <tr class="history-row">
      <td colspan="9" class="px-8 py-3 text-xs">
        <div class="font-semibold accent mb-2">🧠 ¿Por qué se levantó la alerta?</div>
        ${body}
        <div class="text-white/40 mt-3">Pattern IDs: ${ids}</div>
      </td>
    </tr>`;
}

function renderLegalRow(legal) {
  const urgencyColor = {
    inmediata: 'text-red-400',
    prioritaria: 'text-yellow-400',
    preventiva: 'text-green-400',
  }[legal.urgency] || 'text-white';

  const articlesHtml = (legal.articles || [])
    .map(
      (a) => `<tr>
        <td class="pr-4 align-top text-white/60">${esc(a.law)}</td>
        <td class="pr-4 align-top font-mono text-xs">${esc(a.article)}</td>
        <td class="pr-4 align-top">${esc(a.title)}</td>
        <td class="align-top text-white/70">${esc(a.penalty || '—')}</td>
      </tr>`,
    )
    .join('');

  const authoritiesHtml = (legal.authorities || [])
    .map(
      (au) => `<div class="py-0.5"><strong>${esc(au.name)}</strong> · <span class="accent">${esc(au.phone)}</span> <span class="text-white/40">· ${esc(au.hours)}</span></div>`,
    )
    .join('');

  const actionsHtml = (legal.recommended_actions || [])
    .map((act, i) => `<li>${esc(act)}</li>`)
    .join('');

  const rightsHtml = (legal.victim_rights || [])
    .map((r) => `<li>${esc(r)}</li>`)
    .join('');

  return `
    <tr class="history-row">
      <td colspan="9" class="px-8 py-3 text-xs">
        <div class="font-semibold ${urgencyColor} mb-2">📜 Marco legal · urgencia: ${esc(legal.urgency)}</div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div class="text-white/60 mb-1">Artículos aplicables</div>
            <table class="w-full text-xs"><tbody>${articlesHtml || '<tr><td class="text-white/40 italic">Sin artículos</td></tr>'}</tbody></table>
          </div>
          <div>
            <div class="text-white/60 mb-1">Autoridades competentes</div>
            ${authoritiesHtml || '<div class="text-white/40 italic">Ninguna autoridad recomendada.</div>'}
            ${actionsHtml ? `<div class="text-white/60 mt-3 mb-1">Acciones recomendadas</div><ol class="list-decimal list-inside space-y-0.5">${actionsHtml}</ol>` : ''}
            ${rightsHtml ? `<div class="text-white/60 mt-3 mb-1">Derechos de la víctima</div><ul class="list-disc list-inside space-y-0.5">${rightsHtml}</ul>` : ''}
          </div>
        </div>
      </td>
    </tr>`;
}

// Tiny toast for non-PELIGRO actions (status updates, errors, etc).
// Lighter than showPeligroToast() — no audio, 4s auto-dismiss.
function showToast(text, kind = 'info') {
  const stack = document.getElementById('toast-stack');
  if (!stack) return;
  const t = document.createElement('div');
  t.className = 'toast';
  const color = kind === 'error' ? '#EF4444' : kind === 'success' ? '#22C55E' : '#C16A4C';
  t.style.borderColor = color;
  t.style.borderLeftColor = color;
  t.innerHTML = `<div class="toast-body">${esc(text)}</div>`;
  t.addEventListener('click', () => t.remove());
  stack.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

const STATUS_VERBS = {
  reviewed: 'marcada como Revisada',
  dismissed: 'Descartada',
  escalated: 'Escalada',
  pending: 'movida a Pendiente',
};

async function patchStatus(id, status) {
  try {
    await jsend(`/alerts/${id}`, 'PATCH', {
      status,
      reviewer: localStorage.getItem('nahual_reviewer') || 'panel',
    });
    const folio = `NAH-2026-${String(id).padStart(4, '0')}`;
    showToast(`✓ ${folio} ${STATUS_VERBS[status] || status}`, 'success');
  } catch (e) {
    showToast(`Error al actualizar: ${e.message}`, 'error');
  }
}

async function escalate(id) {
  const destination = window.prompt('Destino de escalación (088, SIPINNA, Fiscalía…)', '088');
  if (!destination) return;
  const reason = window.prompt('Motivo (opcional):', '') || null;
  await jsend(`/alerts/${id}/escalate`, 'POST', {
    destination,
    reason,
    reviewer: localStorage.getItem('nahual_reviewer') || 'panel',
  });
}

async function toggleLegal(id) {
  if (state.legalExpanded.has(id)) {
    state.legalExpanded.delete(id);
    state.legal.delete(id);
  } else {
    state.legalExpanded.add(id);
    state.legal.set(id, await jget(`/alerts/${id}/legal`));
  }
  await refresh();
}

async function toggleWhy(id) {
  if (state.whyExpanded.has(id)) {
    state.whyExpanded.delete(id);
    state.why.delete(id);
  } else {
    state.whyExpanded.add(id);
    state.why.set(id, await jget(`/alerts/${id}/why`));
  }
  await refresh();
}

async function toggleHistory(id) {
  if (state.expanded.has(id)) {
    state.expanded.delete(id);
    state.history.delete(id);
  } else {
    state.expanded.add(id);
    state.history.set(id, await jget(`/alerts/${id}/history`));
  }
  await refresh();
}

function fillBuckets(rows, interval, hours) {
  // Generate every bucket key in [now-hours, now] and merge with the server rows
  // so the line chart has a continuous time axis even when most buckets are empty.
  const stepMs = interval === 'day' ? 24 * 3600 * 1000 : 3600 * 1000;
  const fmt = (d) => {
    const pad = (n) => String(n).padStart(2, '0');
    const Y = d.getUTCFullYear();
    const M = pad(d.getUTCMonth() + 1);
    const D = pad(d.getUTCDate());
    if (interval === 'day') return `${Y}-${M}-${D}`;
    return `${Y}-${M}-${D} ${pad(d.getUTCHours())}:00`;
  };
  const now = new Date();
  // Round down to the bucket boundary in UTC.
  if (interval === 'hour') now.setUTCMinutes(0, 0, 0);
  else now.setUTCHours(0, 0, 0, 0);
  const buckets = [];
  for (let i = hours - (interval === 'day' ? hours - Math.floor(hours / 24) * 24 : 1); i >= 0; i--) {
    buckets.push(fmt(new Date(now.getTime() - i * stepMs)));
  }
  // Simpler regeneration: start from earliest, step forward.
  buckets.length = 0;
  const totalSteps = interval === 'day' ? Math.max(1, Math.floor(hours / 24)) : hours;
  for (let i = totalSteps - 1; i >= 0; i--) {
    buckets.push(fmt(new Date(now.getTime() - i * stepMs)));
  }
  const byBucket = new Map(rows.map((r) => [r.bucket, r]));
  return buckets.map((b) => byBucket.get(b) || {
    bucket: b,
    total: 0,
    by_level: { PELIGRO: 0, ATENCION: 0, SEGURO: 0 },
    overrides: 0,
    escalated: 0,
  });
}

async function refreshChart() {
  const { interval, hours } = state.tsRange;
  let rows;
  try {
    rows = await jget(`/stats/timeseries?interval=${interval}&hours=${hours}`);
  } catch (err) {
    console.error('timeseries fetch failed', err);
    return;
  }
  const filled = fillBuckets(rows, interval, hours);
  const labels = filled.map((b) => b.bucket);
  const peligro = filled.map((b) => b.by_level.PELIGRO);
  const atencion = filled.map((b) => b.by_level.ATENCION);
  const seguro = filled.map((b) => b.by_level.SEGURO);

  const ctx = document.getElementById('ts-chart').getContext('2d');
  if (state.chart) {
    state.chart.data.labels = labels;
    state.chart.data.datasets[0].data = peligro;
    state.chart.data.datasets[1].data = atencion;
    state.chart.data.datasets[2].data = seguro;
    state.chart.update('none');
    return;
  }
  state.chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'PELIGRO', data: peligro, borderColor: '#EF4444', backgroundColor: 'rgba(239,68,68,0.25)', tension: 0.3, fill: true, pointRadius: 2 },
        { label: 'ATENCIÓN', data: atencion, borderColor: '#EAB308', backgroundColor: 'rgba(234,179,8,0.20)', tension: 0.3, fill: true, pointRadius: 2 },
        { label: 'SEGURO', data: seguro, borderColor: '#22C55E', backgroundColor: 'rgba(34,197,94,0.18)', tension: 0.3, fill: true, pointRadius: 2 },
      ],
    },
    options: {
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: { ticks: { color: 'rgba(255,255,255,0.55)', maxRotation: 0, autoSkipPadding: 16 }, grid: { color: 'rgba(255,255,255,0.05)' } },
        y: { beginAtZero: true, ticks: { color: 'rgba(255,255,255,0.55)', precision: 0 }, grid: { color: 'rgba(255,255,255,0.05)' } },
      },
      plugins: {
        legend: { labels: { color: 'rgba(255,255,255,0.8)', boxWidth: 12, font: { size: 11 } } },
        tooltip: { backgroundColor: '#1f2326', borderColor: '#C16A4C', borderWidth: 1 },
      },
    },
  });
}

function bindActions() {
  document.getElementById('alerts-body').addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-act]');
    if (!btn) return;
    const id = Number(btn.dataset.id);
    const act = btn.dataset.act;
    try {
      if (act === 'history') await toggleHistory(id);
      else if (act === 'legal') await toggleLegal(id);
      else if (act === 'why') await toggleWhy(id);
      else if (act === 'escalate') {
        await escalate(id);
        await refresh();
      } else {
        await patchStatus(id, act);
        await refresh();
      }
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  });

  document.querySelectorAll('.filter-chip').forEach((chip) => {
    chip.addEventListener('click', async () => {
      document.querySelectorAll('.filter-chip').forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      state.filterStatus = chip.dataset.status;
      await refresh();
    });
  });

  const tsSelect = document.getElementById('ts-range');
  if (tsSelect) {
    tsSelect.addEventListener('change', async () => {
      const [interval, hours] = tsSelect.value.split(':');
      state.tsRange = { interval, hours: Number(hours) };
      // Force chart rebuild so axis labels regenerate cleanly.
      if (state.chart) {
        state.chart.destroy();
        state.chart = null;
      }
      await refreshChart();
    });
  }
}

function renderKvList(elId, obj, formatter = (k, v) => `${k}: <strong>${v}</strong>`) {
  const el = document.getElementById(elId);
  if (!el) return;
  const entries = Object.entries(obj || {}).sort((a, b) => b[1] - a[1]);
  if (entries.length === 0) {
    el.innerHTML = '<span class="text-white/40 italic">sin datos</span>';
    return;
  }
  el.innerHTML = entries.map(([k, v]) => formatter(esc(k), v)).join('<br/>');
}

async function refreshContributions() {
  try {
    const stats = await jget('/contributions/stats');
    setText('contrib-total', stats.total_contributions);
    setText('contribBannerNumber', stats.total_contributions);
    renderKvList('contrib-by-level', stats.by_level);
    renderKvList('contrib-by-platform', stats.by_platform);
    renderKvList('contrib-by-source', stats.by_source);
    renderKvList('contrib-by-region', stats.by_region);
    const top = (stats.top_patterns || [])
      .map((r) => `<code>${esc(r.pattern_id)}</code>: <strong>${r.count}</strong>`)
      .join('<br/>') || '<span class="text-white/40 italic">aún no hay contribuciones</span>';
    const el = document.getElementById('contrib-top-patterns');
    if (el) el.innerHTML = top;
  } catch (err) {
    console.error('contributions refresh failed', err);
  }
}

function colorForScore(s) {
  if (s >= 0.7) return '#EF4444';
  if (s >= 0.3) return '#EAB308';
  return '#22C55E';
}

function renderRiskTimeline(alerts) {
  const chart = document.getElementById('riskChart');
  if (!chart) return;
  const recent = (alerts || []).slice(0, 30).reverse();
  if (recent.length === 0) {
    chart.innerHTML = '<div class="text-xs text-white/40 italic m-auto">Aún no hay alertas registradas.</div>';
    return;
  }
  chart.innerHTML = recent
    .map((a) => {
      const score = Number(a.risk_score) || 0;
      const heightPct = Math.max(score * 100, 4);
      const color = colorForScore(score);
      const folio = `NAH-2026-${String(a.id).padStart(4, '0')}`;
      const tip = `${folio} · ${a.risk_level} ${(score * 100).toFixed(0)}% · ${a.platform}`;
      return `<div class="timeline-bar" style="height:${heightPct}%;background:${color};" title="${tip}"></div>`;
    })
    .join('');
}

// Track last seen PELIGRO alert id so the toast only fires for genuinely
// new high-risk events (not for the 15 we already had on first load).
let LAST_PELIGRO_ID = null;
let CONSEC_FAILS = 0;
let PAUSED = false;
let TIMER_HANDLE = null;

function setHealthPill(state, label) {
  const el = document.getElementById('health');
  if (!el) return;
  el.textContent = label;
  el.classList.remove('ok', 'degraded', 'down');
  el.classList.add(state);
}

function showPeligroToast(alert) {
  const stack = document.getElementById('toast-stack');
  if (!stack) return;
  const folio = `NAH-2026-${String(alert.id).padStart(4, '0')}`;
  const t = document.createElement('div');
  t.className = 'toast';
  t.innerHTML = `
    <div class="toast-title">🚨 PELIGRO · ${esc(folio)}</div>
    <div class="toast-body">${esc(alert.platform || '?')} · score ${(Number(alert.risk_score) * 100).toFixed(0)}% · fase ${esc(alert.phase_detected || 'ninguna')}${alert.override_triggered ? ' · OVERRIDE' : ''}</div>
  `;
  // Audio cue (optional, may be blocked by browser autoplay policy).
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator(); const g = ctx.createGain();
    o.connect(g); g.connect(ctx.destination);
    o.frequency.value = 880; g.gain.value = 0.04;
    o.start(); o.stop(ctx.currentTime + 0.18);
  } catch {}
  t.addEventListener('click', () => t.remove());
  stack.appendChild(t);
  // PELIGRO toast lives 15s (was 8s) — operator may be on another tab
  // when a critical alert lands; 8s wasn't enough.
  setTimeout(() => t.remove(), 15000);
}

async function refresh() {
  try {
    const health = await jget('/health');
    setHealthPill(
      'ok',
      `OK · LLM ${health.llm_enabled ? 'on' : 'off'} · STT ${health.groq_enabled ? 'on' : 'off'}`,
    );
    CONSEC_FAILS = 0;
    const stats = await jget('/stats');
    setText('stat-total', stats.total_alerts);
    setText('stat-peligro', stats.by_level.PELIGRO || 0);
    setText('stat-atencion', stats.by_level.ATENCION || 0);
    setText('stat-seguro', stats.by_level.SEGURO || 0);
    setText('stat-pending', stats.by_status.pending || 0);
    setText('stat-escalated', stats.by_status.escalated || 0);

    const qs = state.filterStatus ? `?limit=100&status=${state.filterStatus}` : '?limit=100';
    const alerts = await jget(`/alerts${qs}`);
    // Mini risk-timeline (always shows the freshest 30 alerts unfiltered)
    const allAlerts = state.filterStatus ? await jget('/alerts?limit=30') : alerts;
    renderRiskTimeline(allAlerts);

    // Toast for any newly-arrived PELIGRO above the last seen id.
    const peligros = allAlerts.filter((a) => a.risk_level === 'PELIGRO');
    if (peligros.length) {
      const newest = peligros[0];
      if (LAST_PELIGRO_ID !== null && newest.id > LAST_PELIGRO_ID) {
        showPeligroToast(newest);
      }
      // Initialise high-water mark on first successful refresh — without
      // this, every page load would fire a toast for the most recent
      // historical PELIGRO, which is annoying.
      if (LAST_PELIGRO_ID === null || newest.id > LAST_PELIGRO_ID) {
        LAST_PELIGRO_ID = newest.id;
      }
    }

    // Refresh open history in place.
    await Promise.all(
      [...state.expanded].map(async (id) => {
        state.history.set(id, await jget(`/alerts/${id}/history`).catch(() => []));
      }),
    );
    const body = document.getElementById('alerts-body');
    if (!alerts.length) {
      const filterLabel = state.filterStatus
        ? `con estado "${state.filterStatus}"`
        : 'aún';
      body.innerHTML = `
        <tr><td colspan="9" class="px-4 py-10 text-center text-white/45 text-sm">
          🛡️  No hay alertas ${filterLabel}.<br/>
          <span class="text-xs">Las alertas aparecen aquí en cuanto el bot, la extensión o el endpoint /alert reciban un mensaje sospechoso.</span>
        </td></tr>`;
    } else {
      body.innerHTML = alerts.map(row).join('');
    }
  } catch (err) {
    CONSEC_FAILS += 1;
    if (CONSEC_FAILS === 1) setHealthPill('degraded', 'reconectando…');
    else setHealthPill('down', 'desconectado');
    // Surface the backend outage in the alerts table so the operator sees
    // a clear ⚠️ instead of a silent stale view. Otherwise an empty table
    // looks identical to "no alerts" — dangerous during a real incident.
    const body = document.getElementById('alerts-body');
    if (body && CONSEC_FAILS >= 2) {
      body.innerHTML = `
        <tr><td colspan="9" class="px-4 py-10 text-center text-sm" style="color:#EF4444">
          ⚠️ Backend desconectado · datos no actualizados<br/>
          <span class="text-xs" style="color:rgba(255,255,255,0.5)">El panel sigue intentando reconectar cada ${REFRESH_MS / 1000}s.</span>
        </td></tr>`;
    }
    console.error(err);
  }
}

async function refreshDatasetStats() {
  try {
    const info = await jget('/admin/dataset-info');
    const el = document.getElementById('dataset-stats');
    if (el) {
      el.innerHTML =
        `<span class="accent font-semibold">${info.total_patterns}</span> patrones · ` +
        `<span class="accent font-semibold">${info.high_confidence_patterns}</span> alta-conf`;
      // Tooltip: per-phase counts + bayesian summary if available.
      let tooltipBits = Object.entries(info.phases).map(
        ([k, v]) => `${v.name}: ${v.patterns}`,
      );
      tooltipBits.push(`override≥${info.override_threshold}`);
      // Pull bayesian stats lazily — non-fatal if missing.
      try {
        const bay = await jget('/bayesian/stats');
        if (bay && bay.available !== false) {
          tooltipBits.push(
            `bayesian: ${bay.total_training_examples} docs · vocab ${bay.vocabulary_size}`,
          );
        }
      } catch {}
      el.title = tooltipBits.join('  ·  ');
    }
  } catch {
    // Non-critical; the panel still works without dataset stats.
  }
}

// ---------------- Manual analyze (test box) ----------------

async function runTestAnalysis() {
  const ta = document.getElementById('test-input');
  const out = document.getElementById('test-result');
  if (!ta || !out) return;
  const text = ta.value.trim();
  if (!text) {
    out.className = 'test-result error';
    out.textContent = 'Escribe algo en el textarea primero.';
    return;
  }
  out.className = 'test-result';
  out.textContent = 'Analizando…';
  try {
    const r = await fetch(`${API}/analyze`, {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ text, use_llm: true }),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const a = await r.json();
    out.className = `test-result ${a.risk_level}`;
    const pct = (Number(a.risk_score) * 100).toFixed(0);
    const phases = a.phase_scores
      ? Object.entries(a.phase_scores)
          .map(([k, v]) => `${k.replace('phase', 'F')}=${(v * 100).toFixed(0)}%`)
          .join(' · ')
      : '';
    const ids = (a.pattern_ids || []).slice(0, 6).join(', ') || '—';
    const cats = (a.categories || []).join(', ') || '—';
    const why = (a.why || []).slice(0, 4).map((w) => `   • ${w}`).join('\n') || '   —';
    // Show which layers contributed — the judge can see at a glance
    // whether this verdict came from the heuristic alone or whether the
    // LLM/Bayesian rescued it from a false negative.
    const bay = a.bayesian
      ? `🧠 Bayesiano: ${a.bayesian.predicted_class} (${(a.bayesian.risk_score * 100).toFixed(0)}%, conf ${(a.bayesian.confidence * 100).toFixed(0)}%)`
      : '🧠 Bayesiano: insufficient_data';
    const llm = a.llm_used ? '🤖 LLM (Sonnet 4.5): ACTIVADO' : '⚡ Heurístico solo';
    out.textContent =
      `${a.risk_level}   ${pct}%   ${a.override_triggered ? 'OVERRIDE' : ''}\n` +
      `Fase dominante: ${a.phase_detected || '—'}\n` +
      `Phases:  ${phases}\n` +
      `Categorías: ${cats}\n` +
      `Pattern IDs: ${ids}\n` +
      `${llm}\n${bay}\n` +
      `Por qué:\n${why}`;
  } catch (err) {
    out.className = 'test-result error';
    out.textContent = `Error: ${err.message}`;
  }
}

function bindTestBox() {
  const btn = document.getElementById('test-run');
  const ta = document.getElementById('test-input');
  if (btn) btn.addEventListener('click', runTestAnalysis);
  if (ta) {
    ta.addEventListener('keydown', (e) => {
      // Cmd/Ctrl + Enter sends the analysis.
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        runTestAnalysis();
      }
    });
  }
  document.querySelectorAll('[data-fill]').forEach((b) => {
    b.addEventListener('click', () => {
      const t = document.getElementById('test-input');
      if (t) {
        t.value = b.getAttribute('data-fill') || '';
        runTestAnalysis();
      }
    });
  });
}

// ---------------- Pause toggle ----------------

function showDeepCheckModal(info, errMsg) {
  // Remove previous modal if any.
  document.getElementById('deep-modal')?.remove();
  const modal = document.createElement('div');
  modal.id = 'deep-modal';
  modal.style.cssText = `
    position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 10000;
    display: flex; align-items: center; justify-content: center; padding: 20px;
    backdrop-filter: blur(4px);
  `;
  let body = '';
  if (errMsg) {
    body = `<div style="color:#EF4444">⚠️ ${esc(errMsg)}</div>`;
  } else {
    const checks = Object.entries(info.checks || {})
      .map(([k, v]) => {
        const ok = v.ok;
        const icon = ok ? '✓' : '✗';
        const color = ok ? '#22C55E' : '#EF4444';
        const detail =
          v.error || v.reason || (v.status ? `status=${v.status}` : 'ok');
        return `<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.06);"><span><span style="color:${color};font-weight:bold">${icon}</span> <strong>${esc(k)}</strong></span><span style="color:rgba(255,255,255,0.6);font-family:ui-monospace,Menlo,monospace;font-size:12px">${esc(String(detail))}</span></div>`;
      })
      .join('');
    const summary = info.all_ok
      ? '<div style="color:#22C55E;margin-top:14px;font-weight:bold">✅ Todos los servicios responden.</div>'
      : '<div style="color:#EAB308;margin-top:14px;font-weight:bold">⚠️ Algún servicio falló.</div>';
    body = `${checks}${summary}`;
  }
  modal.innerHTML = `
    <div style="background:#2F353A;border:1px solid #C16A4C;border-radius:12px;padding:24px;min-width:380px;max-width:560px;color:#fff;box-shadow:0 20px 60px rgba(0,0,0,0.6)">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
        <h3 style="margin:0;font-size:16px;color:#C16A4C">🔬 Deep Healthcheck</h3>
        <button id="deep-modal-close" tabindex="0" aria-label="Cerrar" style="background:transparent;border:1px solid rgba(255,255,255,0.12);color:#fff;border-radius:999px;width:32px;height:32px;cursor:pointer;font-size:16px">×</button>
      </div>
      ${body}
      <div style="margin-top:18px;font-size:11px;color:rgba(255,255,255,0.4)">DB · Anthropic · Groq · live ping</div>
    </div>
  `;
  modal.addEventListener('click', (e) => {
    if (e.target === modal || (e.target instanceof Element && e.target.id === 'deep-modal-close')) {
      modal.remove();
    }
  });
  document.body.appendChild(modal);
  // ESC closes too
  const onEsc = (e) => {
    if (e.key === 'Escape') {
      modal.remove();
      document.removeEventListener('keydown', onEsc);
    }
  };
  document.addEventListener('keydown', onEsc);
}

async function runDeepHealthcheck() {
  const btn = document.getElementById('deep-check');
  if (!btn) return;
  btn.disabled = true;
  btn.textContent = '🔬 Probando…';
  try {
    const info = await jget('/admin/healthcheck-deep');
    showDeepCheckModal(info);
  } catch (e) {
    showDeepCheckModal(null, e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '🔬 Deep check';
  }
}

function bindDeepCheck() {
  const btn = document.getElementById('deep-check');
  if (btn) btn.addEventListener('click', runDeepHealthcheck);
}

function bindPauseToggle() {
  const btn = document.getElementById('pause-toggle');
  if (!btn) return;
  btn.addEventListener('click', () => {
    PAUSED = !PAUSED;
    btn.textContent = PAUSED ? '▶ Reanudar' : '⏸ Pausar';
    btn.classList.toggle('paused', PAUSED);
    const lbl = document.getElementById('refresh-label');
    if (lbl) lbl.textContent = PAUSED ? 'pausado · click ▶ para reanudar' : 'auto-refresh cada 5 s';
  });
}

async function tick() {
  if (PAUSED) return;
  await Promise.all([refresh(), refreshChart(), refreshContributions()]);
}

// Tiny boot banner so any future "panel doesn't update" regression is
// debuggable from the browser DevTools without source-mapping the bundle.
console.log(
  `[nahual-panel] API base="${API || '(same-origin)'}" · refresh=${REFRESH_MS}ms` +
  ` · key=${API_KEY ? 'present' : 'absent'}`,
);

bindActions();
bindTestBox();
bindPauseToggle();
bindDeepCheck();
refreshDatasetStats(); // one-shot; dataset is immutable at runtime
tick();
TIMER_HANDLE = setInterval(tick, REFRESH_MS);

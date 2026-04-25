const API = (window.NAHUAL_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const REFRESH_MS = 5000;

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
  const r = await fetch(`${API}${path}`);
  if (!r.ok) throw new Error(`${path} → ${r.status}`);
  return r.json();
}

async function jsend(path, method, body) {
  const r = await fetch(`${API}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
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

async function patchStatus(id, status) {
  await jsend(`/alerts/${id}`, 'PATCH', {
    status,
    reviewer: localStorage.getItem('nahual_reviewer') || 'panel',
  });
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

async function refresh() {
  try {
    const health = await jget('/health');
    setText(
      'health',
      `OK · LLM ${health.llm_enabled ? 'on' : 'off'} · STT ${health.groq_enabled ? 'on' : 'off'}`,
    );
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
    // Refresh open history in place.
    await Promise.all(
      [...state.expanded].map(async (id) => {
        state.history.set(id, await jget(`/alerts/${id}/history`).catch(() => []));
      }),
    );
    document.getElementById('alerts-body').innerHTML = alerts.map(row).join('');
  } catch (err) {
    setText('health', 'desconectado');
    console.error(err);
  }
}

async function tick() {
  await Promise.all([refresh(), refreshChart(), refreshContributions()]);
}

bindActions();
tick();
setInterval(tick, REFRESH_MS);

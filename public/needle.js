const $ = selector => document.querySelector(selector);
const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const time = value => value ? new Date(value).toLocaleString() : 'Not available';
const number = value => typeof value === 'number' ? Math.round(value).toLocaleString() : 'Unknown';
const percent = value => typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : '—';
const safeUrl = value => {
  if (typeof value !== 'string' || !value.trim()) return '';
  try { const url = new URL(value, location.origin); return ['http:', 'https:'].includes(url.protocol) ? escape(url.href) : ''; } catch { return ''; }
};
let catalog = [], saved = new Map(), errors = new Set(), running = false;
async function get(path) { const response = await fetch(path); if (!response.ok) throw new Error('Saved forecast unavailable'); return response.json(); }

function dial(needle) {
  const ready = needle.status === 'ready' && needle.probabilities;
  const angle = ready ? (needle.probabilities.R - needle.probabilities.D) * 85 : 0;
  const label = ready ? `Democratic caucus ${percent(needle.probabilities.D)}, Republican caucus ${percent(needle.probabilities.R)}` : 'Forecast unavailable';
  return `<svg class="needle-dial" viewBox="0 0 280 165" role="img" aria-label="${escape(label)}"><path class="needle-track needle-blue" d="M30 140 A110 110 0 0 1 140 30"/><path class="needle-track needle-red" d="M140 30 A110 110 0 0 1 250 140"/>${ready ? `<line class="needle-hand" x1="140" y1="140" x2="140" y2="45" transform="rotate(${angle} 140 140)"/><circle cx="140" cy="140" r="7" fill="currentColor"/>` : '<text x="140" y="120" text-anchor="middle" fill="currentColor" font-size="30">—</text>'}</svg>`;
}

function card(entry) {
  const data = { ...(saved.get(entry.id) ?? { ...entry, status: 'loading' }) };
  const age = Date.now() - Date.parse(data.forecastTimestamp ?? '');
  if (data.status === 'ready' && (!Number.isFinite(age) || age < -60_000 || age > 15 * 60_000)) {
    data.status = 'stale'; data.reason = 'Forecast run is stale.';
  }
  const odds = data.status === 'ready' ? data.probabilities : null;
  const completion = data.completion;
  const labels = { ready: 'Win probability', uncalibrated: 'Awaiting calibrated forecast', unavailable: 'Forecast unavailable', stale: 'Forecast stale', loading: 'Loading forecast…' };
  const details = data.kind === 'chamber'
    ? `<p>${number(data.totalSeats)} voting seats · D threshold ${number(data.thresholds?.D)} · R threshold ${number(data.thresholds?.R)}.</p><p>${number(data.contributingRaceIds?.length)} forecast races, ${number(data.fixedSeats?.length)} fixed seats, ${number(data.missingSeats)} missing seats.</p>${data.seatInterval ? `<p>90% seat intervals: D ${data.seatInterval.D.map(number).join('–')}, R ${data.seatInterval.R.map(number).join('–')}.</p>` : ''}${data.senateTieBreaker ? `<p>Senate tie-breaking caucus: ${escape(data.senateTieBreaker)}.</p>` : ''}<p>${escape(data.method)}</p>`
    : `<p>${number(data.observed?.totalVotes)} reported votes · ${escape(data.observed?.status ?? 'Unavailable')}.</p>${data.observed?.candidates?.length ? `<table><thead><tr><th>Candidate</th><th>Votes</th></tr></thead><tbody>${data.observed.candidates.map(c => `<tr><td>${escape(c.name)} (${escape(c.party)})</td><td>${number(c.votes)}</td></tr>`).join('')}</tbody></table>` : ''}${completion ? `<p>${completion.percentCounted === null ? 'Unknown share' : `${escape(completion.percentCounted)}%`} of expected vote counted · ${escape(completion.status)}.</p><p>${completion.estimatedRemainingVotes === null ? "Remaining contest votes unknown" : `Approximately ${number(completion.estimatedRemainingVotes)} contest votes remaining`} (${escape(completion.sourceName)} estimate; supplier counted ${number(completion.supplierVotes)}).</p><p class="muted">${escape(completion.uncertainty)}</p>${safeUrl(completion.sourceUrl) ? `<a href="${safeUrl(completion.sourceUrl)}" target="_blank" rel="noopener noreferrer">Completion source</a>` : ''}<p class="needle-foot">Supplier updated ${escape(time(completion.sourceUpdated))}; verified ${escape(time(completion.checkedAt))}.</p>` : ''}${data.marginInterval ? `<p>Projected D−R margin ${data.projectedMargin.toFixed(1)} points · 90% interval ${data.marginInterval.map(v => v.toFixed(1)).join(' to ')}.</p>` : ''}`;
  return `<article class="needle-card" id="${escape(entry.id)}"><p class="eyebrow">${escape(entry.chamber)}${data.kind === 'chamber' ? ' / CONTROL' : ''}</p><h3>${escape(entry.name)}</h3>${dial(data)}<div class="needle-odds"><span class="dem">D ${percent(odds?.D)}</span><span class="rep">R ${percent(odds?.R)}</span></div><p class="needle-state">${escape(labels[data.status] ?? data.status)}</p>${odds?.other ? `<p>Other or unresolved: ${percent(odds.other)}.</p>` : ''}${errors.has(entry.id) ? '<p class="needle-error">Refresh failed. Retained data may be out of date.</p>' : ''}${data.reason ? `<p class="muted">${escape(data.reason)}</p>` : ''}<details><summary>Counts, sources &amp; assumptions</summary>${details}${data.assumptions?.length ? `<ul>${data.assumptions.map(a => `<li>${escape(a)}</li>`).join('')}</ul>` : ''}${safeUrl(data.calibrationUrl) ? `<p><a href="${safeUrl(data.calibrationUrl)}">Calibration report</a></p>` : ''}<p class="needle-foot">Forecast ${escape(time(data.forecastTimestamp))} · model ${escape(data.modelVersion ?? 'not published')} · version ${data.version ?? 0}.</p><a href="${escape(entry.apiUrl)}">Individual JSON API</a></details></article>`;
}

function render() {
  const open = new Set([...document.querySelectorAll('.needle-card details[open]')].map(d => d.closest('article').id));
  $('#chamber-needles').innerHTML = catalog.filter(n => n.id.endsWith('-control')).map(card).join('');
  const query = $('#needle-search').value.trim().toLowerCase(), chamber = $('#needle-chamber').value;
  const races = catalog.filter(n => !n.id.endsWith('-control'));
  const filtered = races.filter(n => (!chamber || n.chamber === chamber) && `${n.name} ${n.id}`.toLowerCase().includes(query));
  $('#race-needles').innerHTML = filtered.length ? filtered.map(card).join('') : '<p>No matching races.</p>';
  $('#needle-count').textContent = `${filtered.length} of ${races.length} races`;
  for (const id of open) { const detail = document.getElementById(id)?.querySelector('details'); if (detail) detail.open = true; }
}

async function refresh() {
  if (running || document.hidden) return;
  running = true;
  try {
    const next = await get('/api/needle'); catalog = next.needles;
    render();
    let index = 0;
    await Promise.all(Array.from({ length: Math.min(6, catalog.length) }, async () => {
      while (index < catalog.length) {
        const entry = catalog[index++];
        try {
          const value = await get(entry.apiUrl);
          // Do not mix a newly published run with the catalog's previous run.
          if (value.version !== next.version) throw new Error('Forecast changed during refresh');
          saved.set(entry.id, value); errors.delete(entry.id);
        } catch { errors.add(entry.id); }
      }
    }));
    render();
    $('#needle-status').textContent = `${errors.size ? `${errors.size} forecasts could not refresh. ` : ''}Saved data checked ${new Date().toLocaleTimeString()}. Updates every 30 seconds while visible.`;
  } catch { render(); $('#needle-status').textContent = 'Forecasts could not refresh. Retrying in 30 seconds.'; }
  finally { running = false; }
}
$('#needle-search').addEventListener('input', render);
$('#needle-chamber').addEventListener('change', render);
document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
setInterval(refresh, 30_000);
refresh();

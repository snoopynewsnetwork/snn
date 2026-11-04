import { miCountyModel, twoPartyMargin } from './mi-sen-model.js';

const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const num = v => v === null || v === undefined ? '—' : Math.round(v).toLocaleString('en-US');
const pct = v => v === null || v === undefined ? '—' : `${v.toFixed(1)}%`;
const signed = (v, decimals = 1) => v === null ? '—' : `${v >= 0 ? '+' : '−'}${Math.abs(v).toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`;
const margin = v => v === null ? 'No votes' : `${v >= 0 ? 'D' : 'R'} +${Math.abs(v).toFixed(1)}`;
const color = v => v === null || Math.abs(v) < .05 ? '' : v > 0 ? 'county-blue' : 'county-red';
const time = v => v && Number.isFinite(Date.parse(v)) ? new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' }).format(new Date(v)) : 'Not verified';
const updates = new WeakMap();
export const updateMiSen = root => updates.get(root)?.();
let baselineRequest;

export function renderMiSummary(model, result, baseline) {
  if (!model) return `<p role="status">Waiting for a verified 83-county snapshot. ${esc(result?.message || '')}</p>`;
  const m = model;
  const largest = [...m.rows].sort((a, b) => (b.remaining ?? b.baselineTotal) - (a.remaining ?? a.baselineTotal)).slice(0, 8);
  const max = Math.max(...largest.map(c => c.remaining ?? 0), 1);
  const missingWeight = m.missing.reduce((sum, c) => sum + c.baselineTotal, 0) / m.baselineTotal * 100;
  const missing = [...m.missing].sort((a, b) => b.baselineTotal - a.baselineTotal).slice(0, 6);
  return `<section class="county-outstanding"><div class="county-live-heading"><strong>${m.fresh ? 'LIVE COUNTY SNAPSHOT · UNOFFICIAL' : 'LAST VERIFIED COUNTY SNAPSHOT · STALE'}</strong><span>Verified ${esc(time(result.lastSuccessAt))} · automatic checks every minute</span></div>
    ${!m.fresh ? '<p class="error">The county source is stale or unavailable. Saved counts remain visible; current remaining-vote estimates are suspended.</p>' : ''}
    <div class="county-stats"><article><span>Reported county two-party margin</span><strong class="${color(m.margin)}">${margin(m.margin)}</strong><small>D ${num(m.d)} · R ${num(m.r)} · other ${num(m.other)}</small></article><article><span>Change vs. 2024 · matched county mix</span><strong class="${color(m.matchedSwing)}">${signed(m.matchedSwing)} margin points</strong><small>2024 statewide Senate baseline: ${margin(twoPartyMargin(baseline.totals.d, baseline.totals.r))}. Partial returns can differ by precinct and voting method.</small></article><article><span>Modeled additional D+R votes</span><strong>${num(m.remaining)}</strong><small>Conditional on the applied turnout model. Actual uncounted ballots are unknown.</small></article></div>
    <p><strong>${m.missing.length} counties have no published votes</strong>, representing ${pct(missingWeight)} of 2024 two-party Senate votes.${missing.length ? ` Largest: ${missing.map(c => `${esc(c.name)} (${margin(c.margin24)})`).join('; ')}.` : ''} Reporting counties can also have votes left.</p>
    ${m.fresh ? `<div class="county-live-comparison"><strong>Conditional final two-party result: <span class="${color(m.finalMargin)}">${margin(m.finalMargin)}</span></strong><p>D ${num(m.finalD)} / R ${num(m.finalR)} · modeled volume ${pct(m.impliedTurnout)} of 2024 D+R.${m.requiredDToTie !== null ? ` Democrats would need ${pct(m.requiredDToTie)} of the modeled additional votes to tie.` : ''} This is an uncalibrated scenario, without a win probability or race call.</p></div>
    <h4>Largest modeled pools still to report</h4><ol class="mi-remaining-bars">${largest.map(c => `<li><div><strong>${esc(c.name)}</strong><span>${num(c.remaining)} additional D+R · net D ${signed(c.remainingNet, 0)}</span></div><svg class="mi-remaining-track" viewBox="0 0 100 5" preserveAspectRatio="none" role="img" aria-label="${esc(c.name)} modeled remaining: D ${num(c.remainingD)}, R ${num(c.remainingR)}"><rect class="county-track" width="100" height="5"/><rect class="county-fill-d" width="${100 * c.remainingD / max}" height="5"/><rect class="county-fill-r" x="${100 * c.remainingD / max}" width="${100 * c.remainingR / max}" height="5"/></svg><small>${esc(c.volumeSource)} · 2024 ${margin(c.margin24)}</small></li>`).join('')}</ol><p class="muted">Blue = modeled D votes; red = modeled R votes. Bar lengths share one scale. Counties at CNN’s 100% can still be revised.</p>` : ''}
    <p><a href="${esc(result.sourceUrl)}" target="_blank" rel="noopener noreferrer">CNN county feed ↗</a>${(result.sourceSnapshots || []).filter(s => s.url).map(s => ` · <a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">Saved county response</a>`).join('')} · provider clock ${esc(result.sourceUpdated)} (timezone as supplied)</p>
  </section>`;
}

export function miCsv(model, options, result, baseline) {
  const fields = ['county','fips','2024_D','2024_R','2024_other','2024_two_party_margin_pp','2026_D','2026_R','2026_other','2026_two_party_margin_pp','margin_change_pp','D_net_change_at_same_reported_volume','reported_D_R_pct_of_2024','supplier_expected_vote_pct','assumed_D_R_total','signed_headroom_to_assumption','modeled_additional_D_R','modeled_additional_D','modeled_additional_R','modeled_final_D','modeled_final_R','volume_source','volume_mode','fallback_turnout_pct','apply_matched_swing','snapshot_status','verified_at','source_url','baseline_source'];
  const rows = model.rows.map(c => [c.name,c.fips,c.d,c.r,c.other,c.margin24,c.d26,c.r26,c.other26,c.margin26,c.swing,c.netChange,c.observedPct24,c.supplierPercent,c.assumedTotal,c.headroom,c.remaining,c.remainingD,c.remainingR,c.finalD,c.finalR,c.volumeSource,options.volume,options.turnout,options.swing,model.fresh ? 'current' : 'stale',result.lastSuccessAt,result.sourceUrl,baseline.source.url]);
  return [fields,...rows].map(row => row.map(cell => `"${String(cell ?? '').replaceAll('"','""')}"`).join(',')).join('\r\n') + '\r\n';
}

export async function mountMiSen(root, getLive) {
  root.innerHTML = '<p role="status">Loading Michigan’s 83-county Senate comparison…</p>';
  try {
    baselineRequest ??= fetch('/mi-sen-counties.json').then(r => { if (!r.ok) throw new Error('Baseline unavailable'); return r.json(); }).catch(e => { baselineRequest = undefined; throw e; });
    const baseline = await baselineRequest;
    if (!root.isConnected) return;
    root.innerHTML = `<section class="county-tracker"><p class="eyebrow">MI-SEN · 2024 → 2026</p><h3>Where the vote is left. What has changed.</h3>
      <p>All 83 counties, comparing 2026 Senate returns with Slotkin (D) / Rogers (R) in 2024. Margins and turnout volumes below use D+R; other candidates stay separate.</p>
      <form class="county-controls mi-controls"><label>Turnout model<select name="volume"><option value="supplier">CNN county estimates; historical fallback</option><option value="historical">Scale every county from 2024</option></select></label><label>2024 turnout scale / fallback (%)<input name="turnout" type="number" min="10" max="150" step="any" required value="80"><small>80% is an illustrative midterm assumption, not a turnout forecast.</small></label><label class="mi-swing-control"><input name="swing" type="checkbox" checked>Apply observed matched-county share change to additional votes</label><button type="submit" class="button">Apply model</button></form>
      <p class="error" data-mi-error role="alert"></p><div data-mi-summary aria-live="polite"></div>
      <div class="county-table-heading"><h4>County by county · reported change and modeled votes left</h4><label>Find county<input type="search" data-mi-search placeholder="County name"></label><label>Sort<select data-mi-sort><option value="remaining">Modeled votes left</option><option value="volume">2024 vote volume</option><option value="swing">Swing toward Democrats</option><option value="net">D net improvement at observed volume</option><option value="name">County name</option></select></label><button class="button quiet" type="button" data-mi-csv>Download all counties CSV</button></div>
      <div class="table-wrap county-table-scroll" tabindex="0" role="region" aria-label="Michigan county turnout model"><table class="county-table mi-county-table"><caption>Observed turnout is votes published so far divided by final 2024 D+R votes, not percent counted. Swing is the change in D−R margin points. Model columns depend on the applied controls.</caption><thead><tr><th rowspan="2" scope="col">County</th><th colspan="3" scope="colgroup">2024 Senate · final</th><th colspan="6" scope="colgroup">2026 Senate · published so far</th><th colspan="4" scope="colgroup">Remaining-vote model · conditional</th></tr><tr><th>D</th><th>R</th><th>Margin</th><th>D</th><th>R</th><th>Other</th><th>D+R / 2024</th><th>Margin</th><th>Swing pp</th><th>Additional D+R</th><th>Net additional D−R</th><th>Final D+R / 2024</th><th>Volume basis</th></tr></thead><tbody data-mi-rows></tbody><tfoot data-mi-total></tfoot></table></div><p data-mi-row-count class="muted"></p>
      <details><summary>Sources, denominators and assumptions</summary><p><a href="${esc(baseline.source.url)}" target="_blank" rel="noopener noreferrer">Pinned MEDSL 2024 Senate county returns ↗</a> · <a href="${esc(baseline.source.primaryUrl)}" target="_blank" rel="noopener noreferrer">Official House Clerk statewide totals ↗</a> · <a href="/mi-sen-counties.json">Baseline data</a>. D ${num(baseline.totals.d)}, R ${num(baseline.totals.r)}, other ${num(baseline.totals.other)}. The county source is a secondary transcription of official returns; statewide candidate sums reconcile, but county allocations have not been independently checked against original certificates.</p><p>The collector checks all 83 county identities and every candidate, and sums the county snapshot independently. CNN’s 43 Wayne municipality rows overlap Wayne and are excluded. County and statewide snapshots may differ in time; their difference is never assigned to a county. Zero published votes means no returns in this snapshot.</p><p>Matched-county swing reweights each 2024 county share by its published 2026 D+R volume. It controls which counties have reported, but cannot control voting-method or precinct mix within a county. County swings compare partial 2026 with final 2024; they are descriptive, not final swings.</p><p>With CNN estimates selected, a reporting county’s expected D+R volume equals its published D+R divided by CNN’s expected-vote fraction. This assumes remaining votes have the same major-party participation rate. Counties without a usable positive estimate use their 2024 D+R times the turnout scale. Historical mode uses that scale everywhere. The model holds reported votes fixed; † marks an assumed total already exceeded, whose signed shortfall stays in the CSV while additional votes are bounded at zero.</p><p>Additional votes follow the county’s 2024 D share, plus half the pooled observed margin change if selected, bounded at 0–100%. This is one conditional path. Candidate changes, voting methods and precinct order can invalidate that extrapolation. Supplier estimates including 100% can be revised. Stale sources suppress modeled remaining votes. Actual outstanding ballots and final turnout are unknown.</p></details></section>`;
    const form = root.querySelector('form');
    let options = { turnout: 80, volume: 'supplier', swing: true }, model;
    function renderRows() {
      const body = root.querySelector('[data-mi-rows]'), foot = root.querySelector('[data-mi-total]');
      if (!model) { body.innerHTML = ''; foot.innerHTML = ''; return; }
      const sort = root.querySelector('[data-mi-sort]').value, query = root.querySelector('[data-mi-search]').value.trim().toLowerCase();
      const value = c => sort === 'volume' ? c.baselineTotal : sort === 'swing' ? c.swing ?? -Infinity : sort === 'net' ? c.netChange : c.remaining ?? c.baselineTotal;
      const rows = model.rows.filter(c => c.name.toLowerCase().includes(query)).sort((a, b) => sort === 'name' ? a.name.localeCompare(b.name) : value(b) - value(a) || a.name.localeCompare(b.name));
      body.innerHTML = rows.map(c => `<tr><th scope="row">${esc(c.name)}${!c.published ? '<small>No votes published</small>' : ''}</th><td>${num(c.d)}</td><td>${num(c.r)}</td><td class="${color(c.margin24)}">${margin(c.margin24)}</td><td class="county-blue">${num(c.d26)}</td><td class="county-red">${num(c.r26)}</td><td>${num(c.other26)}</td><td>${pct(c.observedPct24)}</td><td class="${color(c.margin26)}">${margin(c.margin26)}</td><td class="${color(c.swing)}">${signed(c.swing)}</td><td>${num(c.remaining)}${c.exceeded ? ' †' : ''}</td><td class="${color(c.remainingNet)}">${signed(c.remainingNet, 0)}</td><td>${model.fresh ? pct(100 * (c.counted + c.remaining) / c.baselineTotal) : '—'}</td><td>${esc(c.volumeSource)}${c.volumeSource.startsWith('CNN') ? ` (${pct(c.supplierPercent)})` : ''}</td></tr>`).join('');
      foot.innerHTML = `<tr><th scope="row">Michigan · all 83</th><td>${num(baseline.totals.d)}</td><td>${num(baseline.totals.r)}</td><td>${margin(twoPartyMargin(baseline.totals.d, baseline.totals.r))}</td><td>${num(model.d)}</td><td>${num(model.r)}</td><td>${num(model.other)}</td><td>${pct(100 * model.counted / model.baselineTotal)}</td><td>${margin(model.margin)}</td><td>${signed(model.matchedSwing)} *</td><td>${num(model.remaining)}</td><td>${model.fresh ? signed(model.finalD - model.finalR - model.d + model.r, 0) : '—'}</td><td>${pct(model.impliedTurnout)}</td><td>Applied model</td></tr>`;
      root.querySelector('[data-mi-row-count]').textContent = `${rows.length} of 83 counties shown. Totals always cover all counties. * State swing uses matched county weights. † Turnout assumption already exceeded.`;
    }
    function update() {
      const live = getLive(), result = live?.countyResult;
      model = miCountyModel(baseline, result, options);
      const summary = root.querySelector('[data-mi-summary]');
      const parent = root.closest('dialog'), top = parent?.scrollTop;
      summary.innerHTML = `<p class="muted">Applied model: ${options.volume === 'supplier' ? 'CNN county estimates with' : 'Every county uses'} ${options.turnout}% of 2024 D+R${options.volume === 'supplier' ? ' as fallback' : ''}. Additional-vote shares use 2024${options.swing ? ' plus the observed matched-county change' : ' without a share shift'}.</p>` + renderMiSummary(model, result, baseline);
      if (model && live?.totalVotes !== result.totalVotes) summary.insertAdjacentHTML('afterbegin', `<p class="county-source-note">Statewide headline: ${num(live?.totalVotes)} all-candidate votes, verified ${esc(time(live?.lastSuccessAt))}. County snapshot: ${num(result.totalVotes)}, verified ${esc(time(result.lastSuccessAt))}. These feeds update separately; the table and model use only the county snapshot.</p>`);
      renderRows();
      root.querySelector('[data-mi-csv]').disabled = !model;
      if (parent) parent.scrollTop = top;
    }
    form.addEventListener('submit', event => {
      event.preventDefault();
      const next = { turnout: Number(form.elements.turnout.value), volume: form.elements.volume.value, swing: form.elements.swing.checked };
      try { miCountyModel(baseline, getLive()?.countyResult, next); options = next; root.querySelector('[data-mi-error]').textContent = ''; update(); }
      catch (e) { root.querySelector('[data-mi-error]').textContent = e.message; }
    });
    root.querySelector('[data-mi-sort]').addEventListener('change', renderRows);
    root.querySelector('[data-mi-search]').addEventListener('input', renderRows);
    root.querySelector('[data-mi-csv]').addEventListener('click', () => {
      if (!model) return;
      const url = URL.createObjectURL(new Blob([miCsv(model, options, getLive().countyResult, baseline)], { type: 'text/csv;charset=utf-8' }));
      const a = document.createElement('a'); a.href = url; a.download = 'mi-sen-2024-2026-county-model.csv'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
    updates.set(root, update); update();
  } catch (e) {
    if (!root.isConnected) return;
    root.innerHTML = '<p class="error" role="alert">Michigan’s county comparison could not load.</p><button class="button quiet" data-mi-retry>Retry</button>';
    root.querySelector('[data-mi-retry]').addEventListener('click', () => mountMiSen(root, getLive));
  }
}

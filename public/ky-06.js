import { countyTotal, countyMargin, countyScenario, countyCoverage, scenarioRemaining, countyForecast } from './ky-06-model.js';

const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const number = value => Math.round(value).toLocaleString('en-US');
const percent = value => `${value.toFixed(1)}%`;
const marginLabel = value => Math.abs(value) < .05 ? 'Even' : `${value > 0 ? 'D' : 'R'} +${Math.abs(value).toFixed(1)}`;
const partyClass = value => Math.abs(value) < .05 ? '' : value > 0 ? 'county-blue' : 'county-red';
const signed = value => `${value > 0 ? '+' : value < 0 ? '−' : ''}${number(Math.abs(value))}`;
let baselineRequest;
const updates = new WeakMap();
export const updateKy06 = root => updates.get(root)?.();
const dateLabel = value => value && Number.isFinite(Date.parse(value)) ? new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' }).format(new Date(value)) : 'Not yet verified';
// CNN extraction clocks omit an offset. Preserve the publisher's literal
// clock rather than interpreting it in each visitor's local timezone.
const sourceDateLabel = value => /(?:Z|[+-]\d{2}:\d{2})$/i.test(value) ? dateLabel(value) : `${value} (publisher timezone unspecified)`;
const fresh = result => ['setup', 'reporting'].includes(result?.status) && Date.now() - Date.parse(result.lastSuccessAt) >= -60_000 && Date.now() - Date.parse(result.lastSuccessAt) <= 15 * 60_000;

export function renderKy06Forecast(counties, result, now = Date.now()) {
  const estimate = countyForecast(counties, result, now);
  if (estimate.status !== 'estimate') return `<section class="county-outstanding"><h4>KY-06 live prediction · waiting</h4><p>${escape(estimate.reason)}</p></section>`;
  const fallback = estimate.counties.filter(c => c.volumeSource === 'historical-weight').map(c => c.name);
  return `<section class="county-outstanding" aria-labelledby="county-prediction-heading"><p class="eyebrow">LIVE PREDICTION · EXPERIMENTAL</p><h3 id="county-prediction-heading">County-adjusted estimate: <span class="${partyClass(estimate.margin)}">${marginLabel(estimate.margin)}</span></h3>
    <p>Estimated final <strong>two-party</strong> margin, fitted to reported county returns. This is an uncalibrated extrapolation; no win probability or race call.</p>
    <div class="county-stats"><article><span>Estimated final R / D votes</span><strong>${number(estimate.r)} / ${number(estimate.d)}</strong><small>${number(estimate.total)} two-party votes; ${number(estimate.countedOther)} published other-candidate votes excluded.</small></article><article><span>Sensitivity range</span><strong>${marginLabel(estimate.low)} to ${marginLabel(estimate.high)}</strong><small>Change modeled remaining volume ±20% and remaining D share ±5 points. This is not a confidence interval.</small></article><article><span>Modeled additional D+R votes</span><strong>${number(estimate.remaining)}</strong><small>Based on CNN expected-vote estimates and historical geography; actual ballots remaining are unknown.</small></article></div>
    <p>${estimate.reportingCount} / 16 counties have two-party returns (${percent(estimate.reportingWeight)} of the 2024 district vote by geography). Matched-county D share shift: ${estimate.shift >= 0 ? '+' : '−'}${Math.abs(estimate.shift).toFixed(2)} points vs. 2024. Snapshot verified ${escape(dateLabel(estimate.verifiedAt))}.</p>
    <details><summary>Prediction assumptions and county estimates</summary><p>Published R and D votes stay fixed. We fit a common D share shift, weighted by published two-party votes, against the same counties’ certified 2024 House shares. Each county’s additional votes follow its 2024 share plus that shift, bounded to 0–100%. Early returns may have a different voting-method or precinct mix from later returns.</p><p>Reporting counties use their own CNN expected-vote percentage to estimate additional two-party volume. Other counties use their 2024 House volume scaled to ${percent(100 * estimate.turnoutScale)} by CNN’s district expected-vote estimate, assuming the current district two-party fraction persists. County estimates can differ from the district estimate. No published vote is removed when a turnout estimate is exceeded.</p><p>${fallback.length ? `Historical volume weights used for: ${fallback.map(escape).join(', ')}.` : 'Every county has a usable local expected-vote estimate.'} Anderson and Bath include only KY-06. Supplier estimates, including 100%, do not establish completion. The manual scenarios below do not control this prediction.</p>
    <div class="table-wrap county-table-scroll" tabindex="0" role="region" aria-label="County prediction estimates"><table class="county-table"><caption>Modeled two-party outcome; counted votes held fixed.</caption><thead><tr><th>County</th><th>Additional D+R estimate</th><th>Estimated final R</th><th>Estimated final D</th></tr></thead><tbody>${estimate.counties.map(c => `<tr><th scope="row">${escape(c.name)}</th><td>${number(c.remaining)}</td><td>${number(c.r)}</td><td>${number(c.d)}</td></tr>`).join('')}</tbody></table></div></details>
    <p><a href="${escape(result.sourceUrl)}" target="_blank" rel="noopener noreferrer">${escape(result.sourceName || 'County source')} ↗</a>${(result.sourceSnapshots || []).filter(s => s.url).map(s => ` · <a href="${escape(s.url)}" target="_blank" rel="noopener noreferrer">Saved source response</a>`).join('')}</p></section>`;
}

export async function mountKy06(root, getLive = () => undefined) {
  root.innerHTML = '<p role="status">Loading the certified 2024 county comparison…</p>';
  try {
    baselineRequest ??= fetch('/ky-06-counties.json').then(response => {
      if (!response.ok) throw new Error('County baseline could not load.');
      return response.json();
    }).catch(error => { baselineRequest = undefined; throw error; });
    const baseline = await baselineRequest;
    if (!root.isConnected) return;
    renderTracker(root, baseline, getLive);
  } catch {
    if (!root.isConnected) return;
    root.innerHTML = '<p class="error" role="alert">The county comparison could not load.</p><button type="button" class="button quiet" data-county-retry>Retry county comparison</button>';
    root.querySelector('[data-county-retry]').addEventListener('click', () => mountKy06(root, getLive));
  }
}

function renderTracker(root, baseline, getLive) {
  const counties = baseline.counties;
  const total = baseline.totals.r + baseline.totals.d;
  const baselineMargin = countyMargin(baseline.totals);
  const fayette = counties.find(c => c.name === 'Fayette');
  const outside = { r: baseline.totals.r - fayette.r, d: baseline.totals.d - fayette.d };
  let scenario, sort = 'volume';

  function voteSources(party) {
    const ranked = [...counties].sort((a, b) => b[party] - a[party]);
    const rows = ranked.slice(0, 5);
    rows.push({ name: 'Other 11 county portions', [party]: ranked.slice(5).reduce((sum, c) => sum + c[party], 0) });
    return `<article class="county-coalition"><h4 class="county-${party === 'r' ? 'red' : 'blue'}">${party === 'r' ? 'Republican' : 'Democratic'} vote sources</h4><p>${number(baseline.totals[party])} votes · ${escape(baseline.candidates[party])}</p><ol>${rows.map(c => {
      const share = 100 * c[party] / baseline.totals[party];
      return `<li><div><span>${escape(c.name)}</span><strong>${percent(share)}</strong><span>${number(c[party])}</span></div><svg class="county-bar" viewBox="0 0 100 5" preserveAspectRatio="none" aria-hidden="true"><rect class="county-track" width="100" height="5"/><rect class="county-fill-${party}" width="${share}" height="5"/></svg></li>`;
    }).join('')}</ol></article>`;
  }

  root.innerHTML = `<section class="county-tracker" aria-labelledby="county-heading">
    <div class="county-live-banner" data-county-live aria-live="polite"></div>
    <div data-county-prediction aria-live="polite"></div>
    <p class="eyebrow">KY-06 · LIVE COUNTY RETURNS</p><h3 id="county-heading">Where the turnout is still to report.</h3>
    <div data-county-coverage></div>
    <h3>Where the red and blue votes came from in 2024.</h3>
    <p>Compare all 16 counties with the <strong>certified 2024 U.S. House result</strong>: Andy Barr (R) vs. Randy Cravens (D). Anderson and Bath include only the portions in KY-06.</p>
    <p class="county-source-note">Live county returns appear above. The historical figures and conditional scenarios below provide context; actual votes remaining are unknown.</p>
    <div class="county-stats">
      <article><span>2024 district result</span><strong class="county-red">${marginLabel(baselineMargin)}</strong><small>${number(total)} votes · R net +${number(baseline.totals.r - baseline.totals.d)}</small></article>
      <article><span>Fayette / Lexington</span><strong class="county-blue">${percent(100 * fayette.d / baseline.totals.d)} of D votes</strong><small>${marginLabel(countyMargin(fayette))} locally · D net +${number(fayette.d - fayette.r)}</small></article>
      <article><span>Outside Fayette</span><strong class="county-red">R net +${number(outside.r - outside.d)}</strong><small>${marginLabel(countyMargin(outside))} · ${percent(100 * countyTotal(outside) / total)} of district votes</small></article>
    </div>
    <details class="county-sources"><summary>2024: which counties supplied each party’s votes?</summary><p>Percentages below are each county’s share of that party’s district vote. Fayette supplied the largest number of votes for both parties.</p><div class="county-coalitions">${voteSources('r')}${voteSources('d')}</div></details>
    <section class="county-scenario" aria-labelledby="county-scenario-heading"><h4 id="county-scenario-heading">Expected votes under your assumptions</h4><p>Start with 2024, then change the district margin and turnout. These are illustrative two-party scenarios, not a 2026 forecast.</p>
      <div class="county-presets" role="group" aria-label="County scenario presets"><button type="button" class="button quiet" data-county-margin="${baselineMargin}">2024 replay</button><button type="button" class="button quiet" data-county-margin="-10">R +10</button><button type="button" class="button quiet" data-county-margin="0">Tied race</button><button type="button" class="button quiet" data-county-margin="5">D +5</button></div>
      <form class="county-controls"><label>District D − R margin (points)<input name="margin" type="number" min="-100" max="100" step="any" value="${baselineMargin}" required><small>Negative = Republican lead</small></label><label>Turnout as % of 2024 House votes<input name="turnout" type="number" min="10" max="150" step="any" value="100" required><small>100% = ${number(total)} two-party votes</small></label><button type="submit" class="button">Apply scenario</button></form>
      <p class="error" data-county-error role="alert"></p><div data-county-summary role="status" aria-live="polite"></div><div data-county-remaining role="status" aria-live="polite"></div>
    </section>
    <div class="county-table-heading"><h4>All 16 county portions · 2024 vs. scenario</h4><label>Sort counties<select data-county-sort><option value="volume">2024 vote volume</option><option value="r">2024 Republican votes</option><option value="d">2024 Democratic votes</option><option value="net-r">2024 net Republican votes</option><option value="name">County name</option></select></label><button type="button" class="button quiet" data-county-download>Download CSV</button></div>
    <div class="table-wrap county-table-scroll" tabindex="0" role="region" aria-label="Scrollable county vote comparison"><table class="county-table"><caption>2024 certified House votes and expected votes in the selected scenario. Margins are D minus R as a percentage of two-party votes.</caption><thead><tr><th scope="col" rowspan="2">County</th><th scope="colgroup" colspan="4">2024 certified</th><th scope="colgroup" colspan="4">Scenario · conditional</th></tr><tr><th scope="col">R votes</th><th scope="col">D votes</th><th scope="col">Margin</th><th scope="col">District vote share</th><th scope="col">R votes</th><th scope="col">D votes</th><th scope="col">Margin</th><th scope="col">D net change vs. 2024</th></tr></thead><tbody data-county-rows></tbody><tfoot data-county-totals></tfoot></table></div>
    <p class="muted">* Anderson and Bath are split counties; only their KY-06 votes are included. “D net change” is the change in D minus R votes, including your turnout assumption.</p>
    <details class="county-method"><summary>Sources and scenario method</summary><p><a href="${escape(baseline.source.url)}#page=${baseline.source.page}" target="_blank" rel="noopener noreferrer">${escape(baseline.source.title)} ↗</a> · PDF page ${baseline.source.page} · <a href="${escape(baseline.source.archiveUrl)}" target="_blank" rel="noopener noreferrer">Archived original ↗</a> · <a href="${escape(baseline.source.geographyUrl)}" target="_blank" rel="noopener noreferrer">SOS county / district listing ↗</a> · <a href="/ky-06-counties.json" target="_blank" rel="noopener noreferrer">Baseline data</a>.</p><p>The amended certification gives R ${number(baseline.totals.r)} and D ${number(baseline.totals.d)}; all 16 county rows sum to those totals. It contains two candidates for this contest. This compares House elections, not presidential votes.</p><p>The scenario scales every county’s 2024 two-party volume by the same turnout factor and shifts Democratic vote share equally across counties until the selected district margin is reached. Shares stop at 0% and 100%. Whole votes are apportioned so county rows reconcile to the district totals; a requested margin can differ slightly after rounding. Party vote sources above remain the historical 2024 shares.</p><p>The separate county collector checks CNN and civicAPI every minute. CNN is preferred; civicAPI is the fallback. Every candidate’s 16 county counts must sum to the selected feed’s district count. District and county snapshots may arrive at different times and are labeled separately. A zero published count means no votes in that snapshot, not zero turnout. No reporting percentage, including 100%, establishes finality or a vote-completion denominator.</p><p>“Additional D+R to scenario” subtracts published D and R votes from your assumed county two-party turnout. It is conditional headroom, not a measurement of ballots remaining; other candidates are shown separately and excluded from that subtraction. Counts above the assumed turnout or party targets invalidate that allocation and are flagged. These manual scenarios hold the historical turnout mix fixed; the separate live prediction above uses supplier turnout estimates. Actual ballots left to count are unknown.</p></details>
  </section>`;

  const form = root.querySelector('form');
  function update() {
    try {
      scenario = countyScenario(counties, { margin: Number(form.elements.margin.value), turnout: Number(form.elements.turnout.value) });
      root.querySelector('[data-county-error]').textContent = '';
    } catch (error) { root.querySelector('[data-county-error]').textContent = error.message; return; }
    const f = scenario.counties.find(c => c.name === 'Fayette');
    root.querySelector('[data-county-summary]').innerHTML = `<div class="county-scenario-totals"><strong class="county-red">R ${number(scenario.r)}</strong><strong class="county-blue">D ${number(scenario.d)}</strong><strong>${marginLabel(scenario.margin)}</strong><span>${number(scenario.total)} two-party votes</span></div><p>Common D vote-share shift: <strong>${scenario.shareShift >= 0 ? '+' : '−'}${Math.abs(scenario.shareShift).toFixed(2)} points</strong> vs. 2024. Fayette: ${marginLabel(countyMargin(f))} (${percent(100 * f.d / countyTotal(f))} D). County targets below describe this scenario.</p>`;
    root.querySelectorAll('[data-county-margin]').forEach(button => button.setAttribute('aria-pressed', String(Math.abs(Number(button.dataset.countyMargin) - Number(form.elements.margin.value)) < .00001)));
    renderRows();
    renderLive();
  }
  function renderLive() {
    const live = getLive();
    const countyResult = live?.countyResult;
    const prediction = root.querySelector('[data-county-prediction]');
    const predictionOpen = prediction.querySelector('details')?.open;
    const predictionScroll = prediction.querySelector('.county-table-scroll')?.scrollLeft || 0;
    prediction.innerHTML = renderKy06Forecast(counties, countyResult);
    if (predictionOpen && prediction.querySelector('details')) prediction.querySelector('details').open = true;
    const predictionTable = prediction.querySelector('.county-table-scroll');
    if (predictionTable) predictionTable.scrollLeft = predictionScroll;
    const coverage = countyCoverage(counties, countyResult);
    const district = live?.candidates || [];
    const r = district.filter(c => c.party === 'REP'), d = district.filter(c => c.party === 'DEM');
    const districtTotal = district.reduce((sum, c) => sum + c.votes, 0);
    const margin = r.length === 1 && d.length === 1 && districtTotal ? 100 * (d[0].votes - r[0].votes) / districtTotal : null;
    root.querySelector('[data-county-live]').innerHTML = `<div class="county-live-heading"><strong>LIVE NOW · ${fresh(live) ? 'Unofficial district returns' : 'Source unavailable / stale'}</strong><span>Verified ${escape(dateLabel(live?.lastSuccessAt))} · updates every minute</span></div><div class="county-scenario-totals"><strong class="county-red">R ${r.length === 1 ? number(r[0].votes) : '—'}</strong><strong class="county-blue">D ${d.length === 1 ? number(d[0].votes) : '—'}</strong><strong>${margin === null ? 'Awaiting votes' : marginLabel(margin)}</strong><span>${live?.candidates ? `${number(districtTotal)} all-candidate votes` : 'Vote totals unavailable'}${r.length === 1 && d.length === 1 ? ` · other ${number(districtTotal - r[0].votes - d[0].votes)}` : ''}</span></div>`;
    if (!coverage) {
      root.querySelector('[data-county-coverage]').innerHTML = `<div class="county-outstanding"><h4>County reporting has not been verified yet.</h4><p>District counts are shown above. Remaining votes and their location are unknown until a valid county snapshot arrives. The collector retries automatically.</p><p>${escape(countyResult?.message || '')}</p></div>`;
      root.querySelector('[data-county-remaining]').innerHTML = '<p>Live county counts are unavailable; the scenario cannot yet be compared with reported county votes.</p>';
      return;
    }
    const remaining = scenarioRemaining(scenario, coverage);
    const isFresh = fresh(countyResult);
    const ordered = [...coverage.rows].sort((a, b) => (a.published > 0) - (b.published > 0) || countyTotal(b) - countyTotal(a));
    const heavyMissing = ordered.filter(c => !c.published).slice(0, 5);
    const mismatch = districtTotal !== countyResult.totalVotes || ['DEM', 'REP'].some(party => district.filter(c => c.party === party).reduce((sum, c) => sum + c.votes, 0) !== countyResult.candidates.filter(c => c.party === party).reduce((sum, c) => sum + c.votes, 0));
    const previousTable = root.querySelector('[data-county-coverage] .county-table-scroll');
    const previousScroll = previousTable?.scrollLeft || 0;
    const tableFocused = previousTable === document.activeElement;
    root.querySelector('[data-county-coverage]').innerHTML = `<section class="county-outstanding"><div class="county-live-heading"><h4>${isFresh ? 'County reporting picture' : 'Last verified county picture · stale'}</h4><span>County snapshot verified ${escape(dateLabel(countyResult.lastSuccessAt))}${countyResult.sourceUpdated ? ` · provider update ${escape(sourceDateLabel(countyResult.sourceUpdated))}` : ''}</span></div>
      <div class="county-stats"><article><span>No votes published${isFresh ? '' : ' in saved snapshot'}</span><strong>${coverage.missing.length} / 16 counties</strong><small>${percent(coverage.missingWeight)} of the district’s 2024 House vote came from these county portions.</small></article><article><span>County votes published · all candidates</span><strong>${number(countyResult.totalVotes)}</strong><small>${16 - coverage.missing.length} ${16 - coverage.missing.length === 1 ? 'county has' : 'counties have'} positive vote totals. Votes can still be outstanding in those counties.</small></article><article><span>Actual votes remaining</span><strong>Unknown</strong><small>2024 weight and scenario headroom are context, not a count of unreported ballots.</small></article></div>
      ${heavyMissing.length ? `<p><strong>Largest places still without published votes:</strong> ${heavyMissing.map(c => `${escape(c.name)}${c.partial ? ' *' : ''} (${percent(100 * countyTotal(c) / total)} of the 2024 district vote; ${marginLabel(countyMargin(c))})`).join('; ')}.</p>` : '<p>Every county has published votes. The number still to count remains unknown.</p>'}
      ${mismatch ? `<p class="county-source-note"><strong>County and district snapshots differ:</strong> the headline has ${number(districtTotal)} votes; the county snapshot has ${number(countyResult.totalVotes)}. Missing-county labels describe that county snapshot. Scenario subtraction uses its separately verified counts.</p>` : ''}
      ${!isFresh ? '<p class="error">County data is stale or unavailable. These are retained counts; the outstanding geography may have changed.</p>' : ''}
      <div class="table-wrap county-table-scroll" tabindex="0" role="region" aria-label="Live county returns and turnout context"><table class="county-table county-live-table"><caption>2026 county snapshot vs. 2024 weight. Counties without published votes appear first, largest historical vote volume first. “Additional D+R” uses the applied turnout scenario below.</caption><thead><tr><th>County</th><th>2026 R</th><th>2026 D</th><th>2026 other</th><th>Published votes</th><th>County status</th><th>2024 district weight</th><th>2024 margin</th><th>Additional D+R to scenario</th></tr></thead><tbody>${ordered.map(c => {
        const rem = remaining.rows.find(row => row.name === c.name);
        const more = rem.r + rem.d;
        return `<tr><th scope="row">${escape(c.name)}${c.partial ? ' *' : ''}</th><td class="county-red">${number(c.liveR)}</td><td class="county-blue">${number(c.liveD)}</td><td>${number(c.liveOther)}</td><td>${number(c.published)}</td><td>${c.published ? 'Votes reporting' : 'No votes published'}</td><td>${percent(100 * countyTotal(c) / total)}</td><td class="${partyClass(countyMargin(c))}">${marginLabel(countyMargin(c))}</td><td>${more < 0 ? `Exceeds by ${number(-more)}` : number(more)}${rem.r < 0 || rem.d < 0 ? ' †' : ''}</td></tr>`;
      }).join('')}</tbody><tfoot><tr><th scope="row">KY-06 county sum</th><td>${number(coverage.rows.reduce((sum, c) => sum + c.liveR, 0))}</td><td>${number(coverage.rows.reduce((sum, c) => sum + c.liveD, 0))}</td><td>${number(coverage.rows.reduce((sum, c) => sum + c.liveOther, 0))}</td><td>${number(countyResult.totalVotes)}</td><td>${coverage.missing.length} with no votes</td><td>100.0%</td><td>${marginLabel(baselineMargin)}</td><td>${remaining.total < 0 ? `Exceeds by ${number(-remaining.total)}` : number(remaining.total)}</td></tr></tfoot></table></div>
      <p>† Published votes already exceed this scenario’s county turnout or party allocation. A zero difference does not establish that counting is complete. Anderson and Bath (*) cover only KY-06.</p><p><a href="${escape(countyResult.sourceUrl)}" target="_blank" rel="noopener noreferrer">${escape(countyResult.sourceName || 'County source')} ↗</a>${(countyResult.sourceSnapshots || []).filter(s => s.snapshotId).map(s => ` · <a href="${escape(s.url || `/api/monitor/snapshots/${Number(s.snapshotId)}`)}" target="_blank" rel="noopener noreferrer">Saved county response</a>`).join('')}</p></section>`;
    const refreshedTable = root.querySelector('[data-county-coverage] .county-table-scroll');
    refreshedTable.scrollLeft = previousScroll;
    if (tableFocused) refreshedTable.focus({ preventScroll: true });
    root.querySelector('[data-county-remaining]').innerHTML = `<div class="county-live-comparison"><strong>Compared with ${isFresh ? 'live' : 'last verified'} county votes</strong><p>${remaining.total >= 0 ? `${number(remaining.total)} additional D+R votes would reach your assumed district turnout.` : `Published D+R votes already exceed your assumed district turnout by ${number(-remaining.total)}.`} ${remaining.requiredDShare !== null ? `To reach the scenario’s district result, Democrats would need ${percent(remaining.requiredDShare)} of those additional two-party votes.` : ''}</p>${!remaining.feasible ? '<p class="error">This county allocation is already exceeded by reported votes. Revise the turnout or margin assumptions; negative differences have not been converted into remaining votes.</p>' : ''}<p>Conditional arithmetic using the county snapshot; it does not estimate how many ballots actually remain.</p></div>`;
  }
  function renderRows() {
    const sorted = [...scenario.counties].sort((a, b) => {
      if (sort === 'name') return a.name.localeCompare(b.name);
      const value = c => sort === 'r' ? c.baselineR : sort === 'd' ? c.baselineD : sort === 'net-r' ? c.baselineR - c.baselineD : c.baselineR + c.baselineD;
      return value(b) - value(a) || a.name.localeCompare(b.name);
    });
    root.querySelector('[data-county-rows]').innerHTML = sorted.map(c => {
      const historical = { r: c.baselineR, d: c.baselineD };
      const netChange = c.d - c.r - (c.baselineD - c.baselineR);
      return `<tr><th scope="row">${escape(c.name)}${c.partial ? ' *' : ''}</th><td class="county-red">${number(c.baselineR)}</td><td class="county-blue">${number(c.baselineD)}</td><td class="${partyClass(countyMargin(historical))}">${marginLabel(countyMargin(historical))}</td><td>${percent(100 * countyTotal(historical) / total)}</td><td class="county-red">${number(c.r)}</td><td class="county-blue">${number(c.d)}</td><td class="${partyClass(countyMargin(c))}">${marginLabel(countyMargin(c))}</td><td>${signed(netChange)}</td></tr>`;
    }).join('');
    root.querySelector('[data-county-totals]').innerHTML = `<tr><th scope="row">KY-06 total</th><td class="county-red">${number(baseline.totals.r)}</td><td class="county-blue">${number(baseline.totals.d)}</td><td>${marginLabel(baselineMargin)}</td><td>100.0%</td><td class="county-red">${number(scenario.r)}</td><td class="county-blue">${number(scenario.d)}</td><td>${marginLabel(scenario.margin)}</td><td>${signed(scenario.d - scenario.r - (baseline.totals.d - baseline.totals.r))}</td></tr>`;
  }
  form.addEventListener('submit', event => { event.preventDefault(); update(); });
  root.querySelectorAll('[data-county-margin]').forEach(button => button.addEventListener('click', () => { form.elements.margin.value = button.dataset.countyMargin; update(); }));
  root.querySelector('[data-county-sort]').addEventListener('change', event => { sort = event.target.value; renderRows(); });
  root.querySelector('[data-county-download]').addEventListener('click', () => {
    const countyResult = getLive()?.countyResult;
    const coverage = countyCoverage(counties, countyResult);
    const fields = ['county','geography','2024_R','2024_D','2024_D_minus_R_margin_pp','2024_district_vote_share_pct','scenario_R','scenario_D','scenario_D_minus_R_margin_pp','D_net_change','scenario_district_margin_pp','scenario_turnout_pct_of_2024','baseline_source','2026_R_published','2026_D_published','2026_other_published','additional_two_party_to_scenario','county_snapshot_verified_at','county_snapshot_status','county_source'];
    const rows = scenario.counties.map(c => {
      const live = coverage?.rows.find(row => row.name === c.name);
      return [c.name, c.partial ? 'KY-06 portion only' : 'whole county', c.baselineR, c.baselineD, countyMargin({ r: c.baselineR, d: c.baselineD }), 100 * (c.baselineR + c.baselineD) / total, c.r, c.d, countyMargin(c), c.d - c.r - (c.baselineD - c.baselineR), scenario.margin, 100 * scenario.total / total, baseline.source.url, live?.liveR ?? '', live?.liveD ?? '', live?.liveOther ?? '', live ? countyTotal(c) - live.liveR - live.liveD : '', countyResult?.lastSuccessAt ?? '', fresh(countyResult) ? 'current' : 'stale_or_unavailable', countyResult?.sourceUrl ?? ''];
    });
    const csv = [fields, ...rows].map(row => row.map(cell => `"${String(cell).replaceAll('"', '""')}"`).join(',')).join('\r\n') + '\r\n';
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url; link.download = 'ky-06-county-scenario.csv'; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  update();
  updates.set(root, renderLive);
}

import { signalFor, easternMinutes, closeMinutes, timeLabel, marginLabel } from './election-model.js';

const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const dateLabel = value => new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' }).format(new Date(value));
const statusNames = { awaiting: 'Awaiting results', partial: 'Partial returns', projected: 'Projected', unofficial: 'Unofficial', certified: 'Certified', observed: 'Observed', mixed: 'Mixed evidence', 'not-observed': 'Not observed' };

export function createElectionNight({ api, openEditor, isEditor }) {
  const view = document.querySelector('#night-view');
  const dialog = document.querySelector('#watch-dialog');
  let data, chamber = 'senate', query = '', time = '', onlyPending = false, loading = false, selected;
  let requestSequence = 0, pendingEditor = false;
  const items = () => [...data.guide.senate, ...data.guide.house, ...data.guide.cues];
  const observationFor = id => data.observations.find(item => item.target === id);
  const bandName = id => data.guide.bands.find(band => band.id === id)?.name;
  const badge = (item, observation) => {
    const signal = signalFor(item, observation);
    return `<span class="signal ${signal || 'neutral'}">${escape(signal ? bandName(signal) : !observation || observation.status === 'awaiting' ? 'Awaiting' : item.chamber === 'cue' ? statusNames[observation.status] : item.chamber === 'senate' && observation.margin !== null ? 'Between sheet bands' : 'No sheet trigger')}</span>`;
  };
  const result = (item, observation) => {
    if (!observation || observation.status === 'awaiting') return 'No results entered';
    if (item.chamber === 'cue') return statusNames[observation.status];
    return `${item.group ? `${observation.gopSeats} GOP seats` : marginLabel(observation.margin, item.code === 'NE')}${observation.winner ? ` · ${observation.winner} winner` : ''}${observation.reporting !== null ? ` · ${observation.reporting}% estimated votes counted` : ''}`;
  };
  function render() {
    if (!data) return;
    const { guide, observations } = data;
    const active = observations.filter(o => o.status !== 'awaiting');
    view.innerHTML = `<div class="hero night-hero"><div><p class="eyebrow">NOVEMBER 3, 2026 · ELECTION NIGHT</p><h1>The early tells.</h1><p class="intro">Follow the returns. Read the signals. Keep the receipts.</p></div><div class="election-date"><span>EASTERN TIME</span><strong id="night-clock"></strong><span>Shared desk · manual reporting</span></div></div>
      <div class="night-summary"><div><strong>${active.filter(o => o.target.startsWith('senate-')).length} / ${guide.senate.length}</strong><span>Senate races updated</span></div><div><strong>${active.filter(o => o.target.startsWith('house-')).length} / ${guide.house.length}</strong><span>House watch items updated</span></div><div><strong>${active.filter(o => o.target.startsWith('cue-')).length} / ${guide.cues.length}</strong><span>Timing cues assessed</span></div><div><strong>9pm → 11pm</strong><span>The sheet’s wave / long-night checkpoints</span></div></div>
      <p class="coverage-note">Signals compare manually entered returns with your cheat sheet’s judgment brackets. They are not election calls or chamber forecasts. Uncalled races and missing data remain unresolved. <a href="${guide.sourceImage}" target="_blank" rel="noopener">View the original sheet ↗</a></p>
      <div class="night-legend">${guide.bands.map(band => `<div class="${band.id}"><strong>${band.name}</strong><span>${band.house}</span><span>Senate: ${band.senate}</span></div>`).join('')}</div>
      <div class="section-heading"><h2>Tonight’s watchlist</h2><button type="button" id="refresh-night" class="button quiet">Refresh updates</button></div>
      <p id="night-sync" class="muted" role="status">Last synced ${escape(dateLabel(data.fetchedAt))} · checks every 30 seconds. No automatic results feed.</p>
      <div class="night-tabs" role="group" aria-label="Watchlist">${[['senate','Senate margin bands'],['house','House early tells'],['cue','Timed cues']].map(([value,label]) => `<button type="button" class="button ${value === chamber ? '' : 'quiet'}" data-chamber="${value}" aria-pressed="${value === chamber}">${label}</button>`).join('')}</div>
      <div class="filters night-filters"><label class="search-label">Search the watchlist<input id="night-search" type="search" value="${escape(query)}" placeholder="State, district, candidate, or cue…"></label><label>Poll close / checkpoint (ET)<select id="night-time"><option value="">All times</option>${[...new Set(items().map(item => item.close))].sort().map(value => `<option value="${value}" ${time === value ? 'selected' : ''}>${timeLabel(value)} ET</option>`).join('')}</select></label><label class="check-label"><input id="night-pending" type="checkbox" ${onlyPending ? 'checked' : ''}> Awaiting only</label></div>
      <p class="coverage-note" id="night-description"></p><div id="night-list"></div>
      <details class="night-method"><summary>How to read this desk · source notes &amp; counting caveats</summary><ul>${guide.caveats.map(note => `<li>${escape(note)}</li>`).join('')}</ul><p>Updates require editor access, a source link, an observation time, and a note. Corrections keep the previous versions. A “projected” winner is the editor’s sourced entry; a margin band alone never calls a race.</p></details>`;
    view.querySelectorAll('[data-chamber]').forEach(button => button.addEventListener('click', () => { chamber = button.dataset.chamber; render(); }));
    view.querySelector('#night-search').addEventListener('input', event => { query = event.target.value; renderList(); });
    view.querySelector('#night-time').addEventListener('change', event => { time = event.target.value; renderList(); });
    view.querySelector('#night-pending').addEventListener('change', event => { onlyPending = event.target.checked; renderList(); });
    view.querySelector('#refresh-night').addEventListener('click', () => refresh());
    renderList(); tick();
  }
  function renderList() {
    const shown = data.guide[chamber === 'cue' ? 'cues' : chamber].filter(item =>
      (!time || item.close === time) && `${item.code || ''} ${item.name} ${item.republican || ''} ${item.democrat || ''} ${item.body || ''}`.toLowerCase().includes(query.toLowerCase()) &&
      (!onlyPending || !observationFor(item.id) || observationFor(item.id).status === 'awaiting'));
    view.querySelector('#night-description').textContent = chamber === 'senate'
      ? 'Enter D minus R margin points (I minus R in Nebraska). Highlighted bands reflect current returns; fractional gaps stay unclassified. Poll close times are from the sheet; some states close in stages.'
      : chamber === 'house' ? 'Grouped by poll close, then the sheet’s scenario column. Party indicates who holds the seat in the sheet; ★ marks a redraw. A current lead is provisional. Late toss-ups settle the final size.'
      : 'Record evidence for the sheet’s timing cues. A checkpoint becoming due does not establish the cue or predict an outcome.';
    const list = view.querySelector('#night-list');
    if (!shown.length) { list.innerHTML = '<div class="empty-state">No watch items match these filters.</div>'; return; }
    if (chamber === 'senate') {
      list.innerHTML = `<div class="table-wrap"><table class="senate-signals"><caption class="sr-only">Senate early return thresholds from the supplied sheet</caption><thead><tr><th>Race / close ET</th><th>Latest entry</th>${data.guide.bands.map(band => `<th class="${band.id}">${band.name}</th>`).join('')}<th>Details</th></tr></thead><tbody>${shown.map(item => {
        const observation = observationFor(item.id), signal = signalFor(item, observation);
        return `<tr><th scope="row"><a href="#race/${item.slug}">${item.code} · ${item.name}</a><small>${escape(item.republican)} (R) / ${escape(item.democrat)} (${item.code === 'NE' ? 'I' : 'D'})</small><small>Sheet RCP average (Oct 30): ${escape(item.sheetPolling)}</small><small>${timeLabel(item.close)} ET${item.caveat ? ` · ${escape(item.caveat)}` : ''}</small></th><td>${badge(item, observation)}<small>${escape(result(item, observation))}</small>${observation ? `<small>${escape(statusNames[observation.status])} · ${escape(dateLabel(observation.observedAt))}</small>` : ''}</td>${item.ranges.map((range,index) => `<td class="band-cell ${signal === data.guide.bands[index].id ? `matched ${signal}` : ''}">${escape(range.label)}${signal === data.guide.bands[index].id ? '<small>● Current band</small>' : ''}</td>`).join('')}<td><button class="button quiet" data-watch="${item.id}">${isEditor() ? 'Update' : 'View / update'}</button></td></tr>`;
      }).join('')}</tbody></table></div>`;
    } else {
      list.innerHTML = [...new Set(shown.map(item => item.close))].sort().map(close => `<section class="watch-group"><h3>${timeLabel(close)} <span>ET · ${chamber === 'house' ? 'polls close' : 'checkpoint'}</span> <span data-due="${close}"></span></h3><div class="watch-cards">${shown.filter(item => item.close === close).sort((a,b) => (data.guide.bands.findIndex(band => band.id === a.band) - data.guide.bands.findIndex(band => band.id === b.band))).map(item => {
        const observation = observationFor(item.id);
        return `<article class="watch-card"><div class="watch-card-top"><span class="eyebrow">${chamber === 'house' ? `${escape(bandName(item.winBand || item.band) || 'Late toss-up')}${item.group ? ' · group guardrail' : ` · ${item.party}-held`}` : 'TEA-LEAF READING'}</span>${badge(item, observation)}</div><h4>${escape(item.code || item.name)}${item.redrawn ? ' ★' : ''}</h4><p>${escape(chamber === 'house' ? item.name : item.body)}</p>${item.gopBar ? `<p class="muted">Red trigger: GOP ${item.group ? `${item.gopBar}${item.code === 'TX-REDRAW' ? '+' : ''} seats` : `margin ${item.gopBar}+ points`}${item.winBand ? ' · Any D win: Blue wave' : ''}</p>` : ''}<p class="watch-result">${escape(result(item, observation))}</p><div class="watch-card-bottom"><span class="muted">${observation ? `${escape(statusNames[observation.status])} · ${escape(dateLabel(observation.observedAt))}` : 'No observation yet'}</span><button class="button quiet" data-watch="${item.id}">${isEditor() ? 'Update' : 'View / update'}</button></div></article>`;
      }).join('')}</div></section>`).join('');
    }
    list.querySelectorAll('[data-watch]').forEach(button => button.addEventListener('click', () => openItem(button.dataset.watch)));
    tick();
  }
  function tick() {
    const clock = view.querySelector('#night-clock');
    if (clock) clock.textContent = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: 'numeric', minute: '2-digit' }).format(new Date());
    view.querySelectorAll('[data-due]').forEach(node => { node.textContent = easternMinutes() >= closeMinutes(node.dataset.due) ? 'Time reached' : 'Upcoming'; });
  }
  async function refresh() {
    if (loading) return;
    loading = true;
    try {
      data = await api('/api/election-night');
      const focused = view.contains(document.activeElement) && ['INPUT','SELECT'].includes(document.activeElement.tagName);
      if (!focused) render();
      else { renderList(); view.querySelector('#night-sync').textContent = `Last synced ${dateLabel(data.fetchedAt)} · checks every 30 seconds. No automatic results feed.`; }
    } catch (error) {
      const node = view.querySelector('#night-sync');
      if (node) node.textContent = `Refresh failed: ${error.message} Showing the last saved snapshot; retrying in 30 seconds.`;
      else view.innerHTML = '<p class="error">The election desk could not load.</p><button type="button" class="button" id="retry-night">Try again</button>';
      view.querySelector('#retry-night')?.addEventListener('click', refresh);
    } finally { loading = false; }
  }
  async function openItem(id) {
    selected = id;
    const sequence = ++requestSequence;
    const item = items().find(item => item.id === id), observation = observationFor(id);
    dialog.innerHTML = `<h2 id="watch-title">${escape(item.code || item.name)}</h2><p>Loading observation history…</p><button type="button" class="button quiet" data-close>Close</button>`;
    dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
    if (!dialog.open) dialog.showModal();
    let history, historyError = '';
    try { ({ history } = await api(`/api/election-night/${id}/history`)); }
    catch (error) { historyError = error.message; }
    if (sequence !== requestSequence || !dialog.open) return;
    // Capture the newest stored version, so opening an item also catches updates between polls.
    const current = history?.[0] || observation;
    if (history?.[0]) data.observations = [...data.observations.filter(o => o.target !== id), current];
    const cue = item.chamber === 'cue';
    const statuses = cue ? ['awaiting','observed','mixed','not-observed'] : ['awaiting','partial','projected','unofficial','certified'];
    dialog.innerHTML = `<p class="eyebrow">${cue ? 'TIMING CUE' : 'SOURCED RETURNS'} · ${timeLabel(item.close)} ET</p><h2 id="watch-title">${escape(item.code || item.name)}</h2><p>${escape(item.body || `${item.name}${item.chamber === 'senate' ? ` · ${item.republican} (R) / ${item.democrat} (${item.code === 'NE' ? 'I' : 'D'})` : ''}`)}</p>${badge(item,current)}
      ${current ? `<p>${escape(result(item,current))} · ${escape(statusNames[current.status])}</p><p class="note-body">${escape(current.body)}</p><p><a href="${escape(current.sourceUrl)}" target="_blank" rel="noopener noreferrer">Reporting source ↗</a> · observed ${escape(dateLabel(current.observedAt))}</p>` : '<p>No results or observation entered.</p>'}
      ${isEditor() ? `<form id="watch-form"><div class="form-grid"><label class="full-width">Reporting status<select name="status">${statuses.map(status => `<option value="${status}" ${status === (current?.status || (cue ? 'observed' : 'partial')) ? 'selected' : ''}>${statusNames[status]}</option>`).join('')}</select></label>${cue ? '' : item.group ? `<label class="full-width">GOP seats in this group<input type="number" name="gopSeats" min="0" max="${item.code === 'TX-REDRAW' ? 5 : item.code === 'PA-07-10' ? 2 : 4}" step="1" value="${current?.gopSeats ?? ''}"></label>` : `<label>${item.code === 'NE' ? 'Osborn minus Ricketts' : 'D minus R'} margin (points)<input name="margin" type="number" min="-100" max="100" step="any" value="${current?.margin ?? ''}" placeholder="D +5 → 5; R +5 → -5"></label><label>Winner, if sourced<select name="winner"><option value="">Uncalled</option>${[['D','Democrat'],['R','Republican'],['I','Independent'],['other','Other']].map(([value,label]) => `<option value="${value}" ${current?.winner === value ? 'selected' : ''}>${label}</option>`).join('')}</select></label>`}${cue ? '' : '<label>Estimated vote % counted (optional)<input name="reporting" type="number" min="0" max="100" step="any" placeholder="Leave blank for precinct % or unknown" value="' + (current?.reporting ?? '') + '"></label>'}<label>Observation time (your local time)<input name="observedAt" type="datetime-local" required value="${localInput(new Date())}"></label><label class="full-width">Source URL<input name="sourceUrl" type="url" required maxlength="2048" value="${escape(current?.sourceUrl || '')}" placeholder="https://…"></label><label class="full-width">Evidence / counting context<textarea name="body" required maxlength="2000" placeholder="What was reported? Which ballots remain? Explain corrections.">${escape(current?.body || '')}</textarea></label></div><p class="form-hint">Saved updates are public. Margins describe counted votes. Only enter a vote-count estimate; precinct reporting is a different measure. “Projected” records a sourced call. To reset, select Awaiting and clear all result fields; explain why in the note.</p><p id="watch-error" class="error" role="alert"></p><div class="form-actions"><button type="button" class="button quiet" data-close>Close</button><button type="submit" class="button">Save update</button></div></form>` : '<div class="form-actions"><button type="button" class="button quiet" data-close>Close</button><button type="button" class="button" id="watch-unlock">Editor access to update</button></div>'}
      <details class="watch-history"><summary>Update history ${history ? `(${history.length}${history.length === 20 ? ' most recent' : ''})` : ''}</summary>${historyError ? `<p class="error">History unavailable: ${escape(historyError)}</p>` : history?.length ? history.map(entry => `<article><strong>Version ${entry.version} · ${escape(statusNames[entry.status])}</strong><p>${escape(result(item,entry))}</p><p class="note-body">${escape(entry.body)}</p><a href="${escape(entry.sourceUrl)}" target="_blank" rel="noopener noreferrer">Source ↗</a><small>Observed ${escape(dateLabel(entry.observedAt))} · saved ${escape(dateLabel(entry.updatedAt))}</small></article>`).join('') : '<p>No saved updates.</p>'}</details>`;
    dialog.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => dialog.close()));
    dialog.querySelector('#watch-unlock')?.addEventListener('click', () => { pendingEditor = true; dialog.close(); openEditor(); });
    dialog.querySelector('#watch-form')?.addEventListener('submit', async event => {
      event.preventDefault();
      const form = event.currentTarget, button = form.querySelector('[type="submit"]');
      button.disabled = true;
      const values = Object.fromEntries(new FormData(form));
      const numeric = name => values[name] === undefined || values[name] === '' ? null : Number(values[name]);
      try {
        await api(`/api/election-night/${id}`, { method: 'PUT', body: JSON.stringify({
          status: values.status, margin: numeric('margin'), reporting: numeric('reporting'), gopSeats: numeric('gopSeats'), winner: values.winner || null,
          sourceUrl: values.sourceUrl, observedAt: new Date(values.observedAt).toISOString(), body: values.body, expectedVersion: current?.version || 0,
        }) });
        if (selected === id && sequence === requestSequence) dialog.close();
        await refresh();
      } catch (error) { if (form.isConnected) form.querySelector('#watch-error').textContent = error.message; }
      finally { button.disabled = false; }
    });
  }
  function localInput(date) {
    return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0,16);
  }
  setInterval(() => { if (!view.hidden && !document.hidden) refresh(); }, 30000);
  setInterval(() => { if (!view.hidden) tick(); }, 15000);
  document.addEventListener('visibilitychange', () => { if (!document.hidden && !view.hidden) refresh(); });
  return { show: async () => { if (data) render(); await refresh(); }, editorChanged: () => { if (data) render(); if (pendingEditor && isEditor()) { pendingEditor = false; openItem(selected); } } };
}

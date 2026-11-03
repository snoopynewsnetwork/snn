export function createCheckLog({ api, escape }) {
  const view = document.querySelector('#checks-view');
  let loading = false;
  const time = value => value ? new Date(value).toLocaleString() : 'Never';
  const changes = { initial: 'First response', changed: 'Changed', unchanged: 'Unchanged', unknown: 'Unknown' };
  const triggers = { scheduled: 'Scheduled', 'public-refresh': 'Live desk refresh', 'editor-refresh': 'Editor refresh' };
  const sourceLink = (name, url) => `<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(name)} ↗</a>`;

  view.innerHTML = `<div class="hero"><div><p class="eyebrow">COLLECTOR DIAGNOSTICS</p><h1>Source check log.</h1><p class="intro">The latest 200 automatic election telemetry checks across every polled source.</p></div><button type="button" id="refresh-checks" class="button">Refresh log</button></div>
    <p id="checks-sync" class="muted" role="status">Loading check history…</p>
    <p id="checks-error" class="error" role="alert" hidden></p>
    <details class="check-coverage"><summary>Source coverage · <span id="check-source-count">all</span> monitored sources</summary><p class="muted">Scheduled checks run every minute. Failed sources wait before retrying. Reading this page does not run a source check.</p><div class="table-wrap"><table class="check-table"><caption class="sr-only">All automatic election telemetry sources and their latest status</caption><thead><tr><th scope="col">Source</th><th scope="col">Latest check</th><th scope="col">Checked at</th><th scope="col">Next retry</th></tr></thead><tbody id="check-sources"><tr><td colspan="4">Loading sources…</td></tr></tbody></table></div></details>
    <section aria-labelledby="check-history-heading"><h2 id="check-history-heading">Recent checks</h2><p class="muted">Newest first. Change compares response content with the previous complete response, including publication pages and metadata; it does not necessarily mean votes changed. First responses establish a baseline. Unknown means no complete response could be compared. Failures include HTTP errors and reported contest validation failures. Skipped retries and duplicate refreshes are not source attempts.</p>
    <div class="table-wrap"><table class="check-table check-history"><caption class="sr-only">Latest 200 source attempts, including failures and unchanged responses</caption><thead><tr><th scope="col">Time</th><th scope="col">Source</th><th scope="col">Outcome</th><th scope="col">Content</th><th scope="col">Details</th></tr></thead><tbody id="check-history"><tr><td colspan="5">Loading checks…</td></tr></tbody></table></div></section>`;

  async function refresh() {
    if (loading) return;
    loading = true;
    const button = view.querySelector('#refresh-checks');
    button.disabled = true;
    try {
      const data = await api('/api/monitor/checks');
      view.querySelector('#checks-error').hidden = true;
      view.querySelector('#check-source-count').textContent = data.sources.length;
      view.querySelector('#check-sources').innerHTML = data.sources.map(source => {
        const check = source.lastCheck;
        const status = check ? (check.success ? 'Success' : 'Failed')
          : source.status === 'ok' ? 'Success' : source.status === 'error' ? 'Failed' : 'Awaiting first check';
        return `<tr><th scope="row">${sourceLink(source.name, source.url)}<small>${escape(source.official === false ? 'Newsroom supplier' : 'Official source')}</small></th><td>${escape(status)}${check?.error ? `<small>${escape(check.error)}</small>` : ''}</td><td>${escape(time(check?.checkedAt || source.checkedAt))}</td><td>${escape(source.nextAttemptAt ? time(source.nextAttemptAt) : '—')}</td></tr>`;
      }).join('');
      view.querySelector('#check-history').innerHTML = data.checks.length ? data.checks.map(check => `<tr>
        <td><time datetime="${escape(check.checkedAt)}">${escape(time(check.checkedAt))}</time><small>${escape(triggers[check.trigger] || check.trigger)}</small></td>
        <th scope="row">${sourceLink(check.sourceName, check.sourceUrl)}<small>${escape(check.adapter)} · ${escape(check.sourceId)}</small></th>
        <td><span class="signal ${check.success ? 'check-success' : 'check-failure'}">${check.success ? 'Success' : 'Failed'}</span></td>
        <td>${escape(changes[check.change] || check.change)}</td>
        <td>${check.httpStatus === null ? 'No HTTP response' : `HTTP ${Number(check.httpStatus)}`} · ${Number(check.durationMs).toLocaleString()} ms${check.error ? `<p class="error">${escape(check.error)}</p>` : ''}${check.snapshotUrl ? `<small><a href="${escape(check.snapshotUrl)}" target="_blank" rel="noopener noreferrer">Saved response ↗</a></small>` : ''}</td>
      </tr>`).join('') : '<tr><td colspan="5">No source checks recorded yet. History starts with the next collector run.</td></tr>';
      view.querySelector('#checks-sync').textContent = `${data.checks.length} of ${data.limit} retained checks · ${data.sources.length} sources · Updated ${time(data.fetchedAt)} · Refreshes every 30 seconds while visible`;
    } catch (error) {
      const message = view.querySelector('#checks-error');
      message.textContent = `Could not refresh the log: ${error.message} Any displayed history may be out of date. Retrying in 30 seconds, or use Refresh log.`;
      message.hidden = false;
    } finally {
      button.disabled = false;
      loading = false;
    }
  }
  view.querySelector('#refresh-checks').addEventListener('click', refresh);
  setInterval(() => { if (!view.hidden && !document.hidden) void refresh(); }, 30_000);
  document.addEventListener('visibilitychange', () => { if (!view.hidden && !document.hidden) void refresh(); });
  return { show: refresh };
}

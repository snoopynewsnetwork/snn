import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { build } from 'esbuild';
import { Miniflare, convertV4MiniflareOptions } from 'miniflare';
import { completionSources } from '../src/completion.ts';
import { BASIC_MODEL_VERSION } from '../src/basic-forecast.ts';

test('saved-source collection automatically publishes predictions and corrections; ordinary reads never fetch', { timeout: 30000 }, async () => {
  const built = await build({ entryPoints: ['src/index.ts'], bundle: true, write: false, format: 'esm', platform: 'neutral', external: ['cloudflare:workers'] });
  const bodies = new Map(completionSources.map(s => [s.url, readFileSync(new URL(`fixtures/completion/${s.id}.json`, import.meta.url), 'utf8')]));
  const senateUrl = completionSources.find(s => s.id === 'completion-SG').url;
  const houseUrl = completionSources.find(s => s.id === 'completion-HG').url;
  bodies.set(senateUrl, readFileSync(new URL('fixtures/ledger/senate.json', import.meta.url), 'utf8'));
  bodies.set(houseUrl, readFileSync(new URL('fixtures/ledger/house.json', import.meta.url), 'utf8'));
  let d = 8000, requests = 0;
  const editorKey = 'basic-model-integration-editor-key-32-characters';
  const mf = new Miniflare(convertV4MiniflareOptions({ unsafeInspectDurableObjects: true, workers: [{
    name: 'basic-model-storage', modules: true, script: built.outputFiles[0].text, compatibilityDate: '2026-10-17',
    bindings: { ADMIN_TOKEN: editorKey },
    durableObjects: { NEWSROOM: { className: 'Newsroom', useSQLite: true }, LIVE_MONITORS: { className: 'ElectionMonitor', useSQLite: true } },
    outboundService: request => {
      requests++;
      if (!bodies.has(request.url)) return new Response('Other sources intentionally unavailable', { status: 503 });
      if (request.url === senateUrl) {
        const rows = JSON.parse(bodies.get(senateUrl)), row = rows.find(r => r.ecKey === '2026-SG-MI');
        row.candidates.forEach(c => { c.voteNum = c.majorParty === 'DEM' ? d : c.majorParty === 'REP' ? 10000 - d : 0; c.winner = false; });
        row.totalVote = 10000; row.percentReporting = 99; row.extractedAt = new Date().toISOString(); row.raceEmbargo.votesReleased = true;
        return new Response(JSON.stringify(rows));
      }
      return new Response(bodies.get(request.url));
    },
  }] }));
  const api = async (path, method = 'GET') => {
    const response = await mf.dispatchFetch('http://localhost' + path, { method }); assert.equal(response.status, 200); return response.json();
  };
  try {
    const prior = await api('/api/needle/senate-mi');
    assert.equal(prior.status, 'experimental'); assert.equal(prior.modelInput.basis, 'prior'); assert.equal(requests, 0);
    await api('/api/election-night/refresh', 'POST');
    const beforeRead = requests, live = await api('/api/needle/senate-mi');
    assert.equal(live.status, 'experimental'); assert.equal(live.modelInput.basis, 'live');
    assert.equal(live.probabilities.D, 1); assert.equal(live.observed.totalVotes, 10000);
    assert.match(live.observed.sourceUrl, /politics\.api\.cnn\.io/);
    assert.equal(live.version, prior.version + 1);
    const chamber = await api('/api/needle/senate-control');
    assert.equal(chamber.status, 'experimental'); assert.equal(chamber.missingSeats, 0); assert.ok(chamber.modelCoverage.live >= 1);
    assert.equal(requests, beforeRead);
    const newsroom = await mf.unsafeGetDurableObjectStorage('basic-model-storage', 'Newsroom', { name: 'senate-2026' });
    const collector = await mf.unsafeGetDurableObjectStorage('basic-model-storage', 'ElectionMonitor', { name: 'completion-cnn' });
    await newsroom.exec("DELETE FROM metadata WHERE key = 'live_monitor_started'");
    await collector.exec("DELETE FROM metadata WHERE key = 'started'");
    d = 2000;
    await api('/api/election-night/refresh', 'POST');
    const correction = await api('/api/needle/senate-mi');
    assert.equal(correction.probabilities.R, 1); assert.equal(correction.modelInput.totalVotes, 10000);
    assert.equal(correction.version, live.version + 1);
    const imported = { electionDate: '2026-11-03', asOf: new Date().toISOString(), modelVersion: BASIC_MODEL_VERSION,
      releaseStatus: 'experimental', calibrationUrl: null, assumptions: ['Integration fixture.'], senateTieBreaker: 'R',
      fixedSeats: { house: [], senate: [] }, races: [{ id: 'senate-mi', name: 'Michigan', chamber: 'senate', seatId: 'senate-mi-2', outcomes: 'DR' }] };
    const published = await mf.dispatchFetch('http://localhost/api/needle/forecast', { method: 'PUT',
      headers: { Authorization: `Bearer ${editorKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ expectedVersion: correction.version, run: imported }) });
    assert.equal(published.status, 201);
    await newsroom.exec("DELETE FROM metadata WHERE key = 'live_monitor_started'");
    await collector.exec("DELETE FROM metadata WHERE key = 'started'");
    await api('/api/election-night/refresh', 'POST');
    const preserved = await api('/api/needle/senate-mi');
    assert.equal(preserved.modelVersion, BASIC_MODEL_VERSION); assert.equal(preserved.probabilities.D, .5);
    assert.equal(preserved.publicationSource, 'editor');
    assert.equal(preserved.version, correction.version + 1, 'Automatic runs never overwrite an editor-published run');
  } finally { await mf.dispose(); }
});

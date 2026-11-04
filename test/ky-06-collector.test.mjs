import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { test } from 'node:test';
import { build } from 'esbuild';
import { Miniflare, convertV4MiniflareOptions } from 'miniflare';

test('KY-06 county adapter uses the shared collector, evidence, corrections and outage retention', { timeout: 30000 }, async () => {
  const built = await build({
    stdin: { resolveDir: process.cwd(), contents: `
      export { ElectionMonitor } from './src/election-monitor.ts';
      export default { async fetch(request, env) {
        const monitor = env.MONITOR.getByName('counties');
        const path = new URL(request.url).pathname;
        return Response.json(path === '/refresh' ? await monitor.refresh('southeast-ky-counties', true, 'public-refresh')
          : path.startsWith('/snapshot/') ? await monitor.getSnapshot(Number(path.split('/').pop()))
          : await monitor.getResults('southeast-ky-counties'));
      }};` },
    bundle: true, write: false, format: 'esm', platform: 'neutral', external: ['cloudflare:workers'],
  });
  const data = JSON.parse(gunzipSync(readFileSync(new URL('./fixtures/civic-ky06-counties.json.gz', import.meta.url))).toString());
  const cnnCounties = JSON.parse(gunzipSync(readFileSync(new URL('./fixtures/cnn-ky06-counties.json.gz', import.meta.url))).toString());
  const cnnRace = JSON.parse(gunzipSync(readFileSync(new URL('./fixtures/cnn-ky06-race.json.gz', import.meta.url))).toString());
  let requests = 0, failed = false, cnnEnabled = false;
  const mf = new Miniflare(convertV4MiniflareOptions({
    name: 'ky06-collector', modules: true, script: built.outputFiles[0].text, compatibilityDate: '2026-10-17', unsafeInspectDurableObjects: true,
    durableObjects: { MONITOR: { className: 'ElectionMonitor', useSQLite: true } },
    outboundService: request => {
      requests++;
      if (request.url !== 'https://civicapi.org/api/v2/race/87173') return cnnEnabled
        ? new Response(JSON.stringify(request.url.includes('/county-races/') ? cnnCounties : cnnRace))
        : new Response('CNN unavailable', { status: 503 });
      return failed ? new Response('Unavailable', { status: 503 }) : new Response(JSON.stringify(data));
    },
  }));
  const api = async path => (await mf.dispatchFetch('http://localhost' + path)).json();
  try {
    const first = await api('/refresh');
    const result = first.results[0];
    assert.equal(requests, 3);
    assert.equal(result.counties.length, 16);
    assert.equal(result.totalVotes, 4029);
    assert.equal(result.sourceKind, 'supplier');
    assert.equal(first.checks[0].success, true);
    assert.equal(first.checks[0].official, false);
    assert.match(result.sourceSnapshots[0].url, /southeast-ky-counties\/snapshots\/\d+$/);
    const evidence = await api('/snapshot/' + result.sourceSnapshots[0].snapshotId);
    assert.equal(evidence.body, JSON.stringify(data));
    assert.equal((await api('/')).results[0].counties.length, 16);
    assert.equal(requests, 3, 'Reads do not fetch the provider');
    const storage = await mf.unsafeGetDurableObjectStorage('ky06-collector', 'ElectionMonitor', { name: 'counties' });
    const unlock = () => storage.exec("DELETE FROM metadata WHERE key = 'started'");
    await unlock();
    data.candidates.find(c => c.party === 'Republican').votes -= 100;
    data.region_results.anderson.candidates.find(c => c.party === 'Republican').votes -= 100;
    const corrected = (await api('/refresh')).results[0];
    assert.equal(corrected.totalVotes, 3929);
    assert.notEqual(corrected.sourceSnapshots[0].snapshotId, result.sourceSnapshots[0].snapshotId);
    // Reallocate votes geographically while preserving every district candidate total.
    await unlock();
    data.region_results.anderson.candidates.find(c => c.party === 'Democratic').votes -= 100;
    data.region_results.fayette.candidates.find(c => c.party === 'Democratic').votes += 100;
    const moved = (await api('/refresh')).results[0];
    assert.equal(moved.totalVotes, corrected.totalVotes);
    assert.equal(moved.counties.find(c => c.name === 'Fayette').totalVotes, 100);
    assert.notEqual(moved.resultHash, corrected.resultHash, 'County distribution changes count as result changes');
    await unlock(); failed = true;
    const outage = await api('/refresh');
    assert.equal(outage.results[0].status, 'error');
    assert.equal(outage.results[0].totalVotes, 3929);
    assert.deepEqual(outage.results[0].counties, moved.counties);
    assert.deepEqual(outage.results[0].sourceSnapshots, moved.sourceSnapshots);
    assert.equal(outage.checks[0].success, false);
    assert.equal(outage.checks[0].httpStatus, 503);
    await unlock(); failed = false;
    data.region_results.bath.fips = 'wrong';
    const rejected = await api('/refresh');
    assert.equal(rejected.results[0].status, 'error');
    assert.deepEqual(rejected.results[0].counties, moved.counties);
    assert.equal(rejected.checks[0].success, false);
    assert.equal(rejected.checks[0].httpStatus, 200);
    assert.ok(rejected.checks[0].snapshotUrl, 'Rejected source responses retain evidence');
    await unlock(); cnnEnabled = true;
    const cnn = (await api('/refresh')).results[0];
    assert.equal(cnn.sourceId, 'cnn-ky06-counties');
    assert.match(cnn.sourceUrl, /county-races\/2026-HG-KY-6.json$/);
    assert.equal(cnn.totalVotes, 181845);
    assert.equal(cnn.counties.find(c => c.name === 'Fayette').totalVotes, 101751);
    assert.equal(cnn.estimatedVotePercent, 59);
    const source = cnn.sourceSnapshots.find(s => s.source === 'cnn-ky06-counties');
    assert.equal((await api('/snapshot/' + source.snapshotId)).body, JSON.stringify(cnnCounties));
    // A newer county response must not be accepted against older district sums.
    await unlock();
    cnnCounties[0].candidates[0].voteNum -= 100;
    cnnCounties[0].totalVote -= 100;
    const mismatched = await api('/refresh');
    assert.equal(mismatched.results[0].status, 'error');
    assert.equal(mismatched.results[0].totalVotes, 181845);
    assert.deepEqual(mismatched.results[0].counties, cnn.counties);
    assert.equal(mismatched.checks.find(c => c.sourceId === 'cnn-ky06-counties').success, false);
    await unlock();
    cnnRace.candidates.find(c => c.majorParty === 'REP').voteNum -= 100;
    cnnRace.totalVote -= 100;
    const cnnCorrected = (await api('/refresh')).results[0];
    assert.equal(cnnCorrected.status, 'reporting');
    assert.equal(cnnCorrected.totalVotes, 181745);
    assert.notEqual(cnnCorrected.resultHash, cnn.resultHash);
  } finally { await mf.dispose(); }
});

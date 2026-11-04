import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { test } from 'node:test';
import { build } from 'esbuild';
import { Miniflare, convertV4MiniflareOptions } from 'miniflare';

test('Michigan county collector retains source evidence, corrections and geography through failures', { timeout: 30000 }, async () => {
  const built = await build({
    stdin: { resolveDir: process.cwd(), contents: `
      export { ElectionMonitor } from './src/election-monitor.ts';
      export default { async fetch(request, env) {
        const monitor = env.MONITOR.getByName('counties');
        const path = new URL(request.url).pathname;
        return Response.json(path === '/refresh' ? await monitor.refresh('mi-sen-counties', true, 'public-refresh')
          : path.startsWith('/snapshot/') ? await monitor.getSnapshot(Number(path.split('/').pop()))
          : await monitor.getResults('mi-sen-counties'));
      }};` },
    bundle: true, write: false, format: 'esm', platform: 'neutral', external: ['cloudflare:workers'],
  });
  const rows = JSON.parse(gunzipSync(readFileSync(new URL('./fixtures/cnn-mi-counties.json.gz', import.meta.url))).toString());
  let requests = 0, failed = false;
  const mf = new Miniflare(convertV4MiniflareOptions({
    name: 'mi-collector', modules: true, script: built.outputFiles[0].text, compatibilityDate: '2026-10-17', unsafeInspectDurableObjects: true,
    durableObjects: { MONITOR: { className: 'ElectionMonitor', useSQLite: true } },
    outboundService: request => {
      requests++; assert.equal(request.url,'https://politics.api.cnn.io/results/county-races/2026-SG-MI.json');
      return failed ? new Response('Unavailable', { status:503 }) : new Response(JSON.stringify(rows));
    },
  }));
  const api = async path => (await mf.dispatchFetch('http://localhost' + path)).json();
  try {
    const first=await api('/refresh'), r=first.results[0];
    assert.equal(r.counties.length,83);assert.equal(r.totalVotes,818619);assert.equal(first.checks[0].success,true);
    const evidence=await api('/snapshot/'+r.sourceSnapshots[0].snapshotId);
    assert.equal(evidence.body,JSON.stringify(rows));
    await api('/');assert.equal(requests,1,'Read-only access never contacts the supplier');
    await api('/refresh');assert.equal(requests,1,'Repeated refresh shares the lease');
    const storage=await mf.unsafeGetDurableObjectStorage('mi-collector','ElectionMonitor',{name:'counties'});
    const unlock=()=>storage.exec("DELETE FROM metadata WHERE key = 'started'");
    await unlock();
    const c=rows.find(c=>c.countyName==='Oakland');c.candidates[0].voteNum-=100;c.totalVote-=100;
    const corrected=(await api('/refresh')).results[0];
    assert.equal(corrected.totalVotes,818519);assert.notEqual(corrected.resultHash,r.resultHash);
    await unlock();failed=true;
    const outage=await api('/refresh');
    assert.equal(outage.results[0].status,'error');assert.equal(outage.results[0].totalVotes,818519);
    assert.deepEqual(outage.results[0].counties,corrected.counties);
    assert.deepEqual(outage.results[0].sourceSnapshots,corrected.sourceSnapshots);
    assert.equal(outage.checks[0].success,false);
    await unlock();failed=false;rows[0].countyFipsCode='99999';
    const rejected=await api('/refresh');assert.equal(rejected.results[0].status,'error');
    assert.deepEqual(rejected.results[0].counties,corrected.counties);assert.equal(rejected.checks[0].success,false);
  } finally { await mf.dispose(); }
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { build } from 'esbuild';
import { Miniflare, convertV4MiniflareOptions } from 'miniflare';
import { completionSources } from '../src/completion.ts';

test('completion history retains corrections and evidence beyond the rolling state limit; reads do not fetch', { timeout: 30000 }, async () => {
  const bodies = new Map(completionSources.map(source => [source.url, readFileSync(new URL(`fixtures/completion/${source.id}.json`, import.meta.url), 'utf8')]));
  const sgUrl = completionSources[0].url;
  const built = await build({ stdin: { resolveDir: process.cwd(), contents: `
    import { ElectionMonitor } from './src/election-monitor.ts';
    export { ElectionMonitor };
    export default { async fetch(request, env) {
      const object = env.MONITOR.getByName('completion-cnn');
      const url = new URL(request.url);
      const result = url.pathname === '/refresh' ? await object.refresh('completion-cnn', true)
        : url.pathname === '/history' ? await object.getCompletionHistory('senate-mi', Number(url.searchParams.get('after') ?? 0))
        : await object.getSnapshot(Number(url.pathname.slice(1)));
      return Response.json(result);
    }};` }, bundle: true, write: false, format: 'esm', platform: 'neutral', external: ['cloudflare:workers'] });
  let requests = 0;
  const mf = new Miniflare(convertV4MiniflareOptions({ unsafeInspectDurableObjects: true, workers: [{
    name: 'completion-storage', modules: true, script: built.outputFiles[0].text, compatibilityDate: '2026-10-17',
    durableObjects: { MONITOR: { className: 'ElectionMonitor', useSQLite: true } },
    outboundService: request => { requests++; assert.ok(bodies.has(request.url)); return new Response(bodies.get(request.url)); },
  }] }));
  const api = async path => (await mf.dispatchFetch('http://localhost' + path)).json();
  try {
    const initial = await api('/refresh');
    assert.equal(initial.results.length, 74);
    assert.ok(initial.checks.every(check => check.success));
    const originalEvidence = initial.sources.find(source => source.id === 'completion-SG').snapshotId;
    const storage = await mf.unsafeGetDurableObjectStorage('completion-storage', 'ElectionMonitor', { name: 'completion-cnn' });
    for (let i = 0; i < 21; i++) {
      const rows = JSON.parse(bodies.get(sgUrl)), row = rows.find(r => r.ecKey === '2026-SG-MI');
      row.totalVote = 1000 - i; row.percentReporting = 50 + i; row.raceEmbargo.votesReleased = true;
      row.candidates.forEach((c, index) => c.voteNum = index === 0 ? row.totalVote : 0);
      bodies.set(sgUrl, JSON.stringify(rows));
      await storage.exec('DELETE FROM metadata');
      await api('/refresh');
    }
    const beforeRead = requests, history = await api('/history');
    assert.equal(history.observations.length, 22);
    assert.equal(history.observations.at(-1).totalVotes, 980);
    assert.equal(history.observations.at(-2).totalVotes, 981, 'Downward corrections remain replayable');
    assert.deepEqual((await api('/history?after=' + history.nextCursor)).observations, []);
    assert.ok((await api('/' + originalEvidence)).body, 'Initial source bytes survive more than 20 changes');
    assert.equal(requests, beforeRead, 'History and snapshot reads never contact publishers');
  } finally { await mf.dispose(); }
});

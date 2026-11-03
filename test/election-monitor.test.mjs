import assert from 'node:assert/strict';
import { test } from 'node:test';
import { build } from 'esbuild';
import { Miniflare, convertV4MiniflareOptions } from 'miniflare';

test('collector persists chunked evidence, revalidates version feeds, and isolates failures', { timeout: 30000 }, async () => {
  // Only the source catalog is substituted. The production collector, network
  // reader, hashing, Durable Object RPC and SQLite execute in real workerd.
  const catalog = `
    const source = (id, url, extra = {}) => ({ id, url, name: id, authorityUrl: 'https://example.test/official', official: true, ...extra });
    export function electionAdapter(id) {
      if (id !== 'test') throw new Error('bad adapter');
      return { id, version: '1',
        sources: [source('version', 'https://example.test/version'),
          source('summary', 'https://example.test/{version}/summary', { dependsOn: 'version', maxBytes: 400000 }),
          source('other', 'https://example.test/other')],
        targets: [{ id: 'house-aa-01', state: 'AA', name: 'AA-01', chamber: 'house', sourceId: 'summary' },
          { id: 'house-aa-02', state: 'AA', name: 'AA-02', chamber: 'house', sourceId: 'other' }],
        parse(bodies) { return Object.fromEntries(['summary', 'other'].map((id, i) => {
          const data = bodies[id] && JSON.parse(bodies[id]);
          return ['house-aa-0' + (i + 1), data?.election === '2026-11-03' ? { status: 'reporting', message: 'Cumulative returns',
            candidates: [{ name: 'D', party: 'DEM', votes: data.d }, { name: 'R', party: 'REP', votes: data.r }],
            totalVotes: data.d + data.r, coverage: 'complete', sourceUpdated: data.updated } : { status: 'unavailable', message: 'No verified contest' }];
        })); }
      };
    }`;
  const built = await build({
    stdin: { contents: `import { ElectionMonitor } from './src/election-monitor.ts';
      export { ElectionMonitor };
      export default { async fetch(request, env) {
        const object = env.MONITOR.getByName('fixture');
        const path = new URL(request.url).pathname;
        const data = path === '/refresh' ? await object.refresh('test', true)
          : path.startsWith('/snapshot/') ? await object.getSnapshot(Number(path.split('/').pop()))
          : await object.getResults('test');
        return Response.json(data);
      }};`, resolveDir: process.cwd() },
    bundle: true, write: false, format: 'esm', platform: 'neutral', external: ['cloudflare:workers'],
    plugins: [{ name: 'fixture-catalog', setup(build) {
      build.onResolve({ filter: /^\.\/election-adapters$/ }, () => ({ path: 'catalog', namespace: 'test' }));
      build.onLoad({ filter: /.*/, namespace: 'test' }, () => ({ contents: catalog }));
    } }],
  });
  let version = '1', broken = false, summaryVotes = 600;
  const requests = [];
  const body = () => {
    const prefix = JSON.stringify({ election: '2026-11-03', d: summaryVotes, r: 350, padding: '' }).slice(0, -2);
    // Place a surrogate pair exactly across the nominal SQLite chunk boundary.
    return prefix + 'x'.repeat(131071 - prefix.length) + '😀' + 'x'.repeat(140000) + '"}';
  };
  const mf = new Miniflare(convertV4MiniflareOptions({ unsafeInspectDurableObjects: true, workers: [{ name: 'collector-test', modules: true, script: built.outputFiles[0].text,
    compatibilityDate: '2026-10-17', durableObjects: { MONITOR: { className: 'ElectionMonitor', useSQLite: true } },
    outboundService: request => {
      const path = new URL(request.url).pathname;
      requests.push({ path, conditional: request.headers.get('if-none-match') });
      if (path === '/version') return new Response(version);
      if (path.endsWith('/summary')) {
        if (request.headers.get('if-none-match') === '"summary"') return new Response(null, { status: 304 });
        return new Response(body(), { headers: { ETag: '"summary"' } });
      }
      if (path === '/other') return broken ? new Response('upstream failure', { status: 503 })
        : new Response(JSON.stringify({ election: '2026-11-03', d: 200, r: 300, updated: String(requests.length) }));
      throw new Error('Unexpected source request ' + path);
    },
  }] }));
  const api = async path => (await mf.dispatchFetch('http://localhost' + path)).json();
  try {
    const first = await api('/refresh');
    assert.deepEqual(first.results.map(result => result.totalVotes), [950, 500]);
    const source = first.sources.find(source => source.id === 'summary');
    const evidence = await api('/snapshot/' + source.snapshotId);
    assert.equal(evidence.body, body());
    assert.match(evidence.hash, /^[0-9a-f]{64}$/);
    const storage = await mf.unsafeGetDurableObjectStorage('collector-test', 'ElectionMonitor', { name: 'fixture' });
    const chunks = await storage.exec('SELECT COUNT(*) AS n FROM snapshot_chunks WHERE snapshot = ?', source.snapshotId);
    assert.ok(chunks[0].n >= 3, 'Bodies larger than one SQLite chunk retain every byte');
    const requestCount = requests.length;
    await api('/refresh');
    assert.equal(requests.length, requestCount, 'Persisted lease prevents duplicate source fetches');
    await storage.exec('DELETE FROM metadata');
    const second = await api('/refresh');
    assert.equal(second.sources.find(source => source.id === 'summary').snapshotId, source.snapshotId, '304 reuses immutable evidence');
    assert.ok(requests.some(request => request.path === '/1/summary' && request.conditional === '"summary"'));
    assert.notEqual(second.results[1].sourceUpdated, first.results[1].sourceUpdated);
    assert.equal(second.results[1].lastResultChangedAt, first.results[1].lastResultChangedAt, 'Publisher timestamps do not manufacture vote changes');
    // A new version uses a new URL, so old validators must never suppress it.
    version = '2'; summaryVotes = 450; broken = true;
    await storage.exec('DELETE FROM metadata');
    const third = await api('/refresh');
    assert.equal(requests.find(request => request.path === '/2/summary').conditional, null);
    assert.equal(third.results[0].totalVotes, 800, 'Downward correction replaces the previous cumulative total');
    assert.equal(third.results[1].status, 'unavailable');
    assert.equal(third.results[1].totalVotes, 500, 'Failed sibling retains verified counts with stale status');
    assert.equal(third.results[1].lastSuccessAt, second.results[1].lastSuccessAt);
    assert.ok(third.results[0].sourceSnapshots.every(receipt => receipt.source !== 'other'), 'Fresh evidence does not cite a source that failed this cycle');
    assert.match(third.sources.find(source => source.id === 'other').error, /503/);
    // Read-only requests consume saved results rather than hitting publishers.
    const beforeRead = requests.length;
    assert.equal((await api('/')).results[0].totalVotes, 800);
    assert.equal(requests.length, beforeRead);
  } finally { await mf.dispose(); }
});

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { build } from 'esbuild';
import { Miniflare, convertV4MiniflareOptions } from 'miniflare';
import { alaskaAdapter } from '../src/adapters/alaska.ts';

const alaska = readFileSync(new URL('./fixtures/cnn-ak-senate.json', import.meta.url), 'utf8');
const mississippi = readFileSync(new URL('./fixtures/northeast/cnn-2026-SG-MS.json', import.meta.url), 'utf8');

test('Alaska pins the full field and preserves first-choice counts without declaring a winner', async () => {
  const results = await alaskaAdapter.parse({ 'cnn-2026-SG-AK': alaska });
  const result = results['senate-ak'];
  assert.equal(result.status, 'reporting');
  assert.equal(result.candidates.length, 4);
  assert.equal(result.totalVotes, 213180);
  assert.equal(result.winner, undefined);
  assert.match(result.message, /ranked-choice/);
  const invalid = JSON.parse(alaska);
  invalid.candidates[0].fullName = 'Unpinned candidate';
  assert.equal((await alaskaAdapter.parse({ 'cnn-2026-SG-AK': JSON.stringify(invalid) }))['senate-ak'].status, 'review');
});

test('scheduled, public and editor refreshes fetch only MS and AK and preserve paused batches', { timeout: 60000 }, async () => {
  const built = await build({
    stdin: { resolveDir: process.cwd(), contents: `
      import worker from './src/index.ts';
      export { Newsroom, ElectionMonitor } from './src/index.ts';
      export default { ...worker, async fetch(request, env, ctx) {
        if (new URL(request.url).pathname === '/test-scheduled') {
          await worker.scheduled({}, env);
          return Response.json({ ok: true });
        }
        return worker.fetch(request, env, ctx);
      }};` },
    bundle: true, write: false, format: 'esm', platform: 'neutral', external: ['cloudflare:workers'],
  });
  const urls = [];
  const token = 'tracking-scope-editor-token-at-least-32-characters';
  const mf = new Miniflare(convertV4MiniflareOptions({
    name: 'tracking-scope', modules: true, script: built.outputFiles[0].text, compatibilityDate: '2026-10-17',
    bindings: { ADMIN_TOKEN: token }, unsafeInspectDurableObjects: true,
    durableObjects: { NEWSROOM: { className: 'Newsroom', useSQLite: true }, LIVE_MONITORS: { className: 'ElectionMonitor', useSQLite: true } },
    outboundService: request => {
      urls.push(request.url);
      if (request.url.endsWith('/2026-SG-AK.json')) return new Response(alaska);
      if (request.url.endsWith('/2026-SG-MS.json')) return new Response(mississippi);
      throw new Error('Paused source requested: ' + request.url);
    },
  }));
  const fetch = (path, init) => mf.dispatchFetch('http://localhost' + path, init);
  try {
    await fetch('/api/monitor');
    const newsroom = await mf.unsafeGetDurableObjectStorage('tracking-scope', 'Newsroom', { name: 'senate-2026' });
    const paused = JSON.stringify({ adapter: 'northeast-mi-cnn', version: 'retained', sources: [], results: [{
      target: 'senate-mi', race: 'senate-mi', name: 'Michigan', state: 'MI', chamber: 'senate', status: 'reporting',
      message: 'Original evidence', totalVotes: 100, lastSuccessAt: '2026-11-04T01:00:00Z', sourceUrl: 'https://example.org/retained',
    }] });
    await newsroom.exec("INSERT INTO metadata (key, value) VALUES ('live_batch_northeast-mi-cnn', ?)", paused);
    const cases = [
      ['/test-scheduled', {}, 'scheduled'],
      ['/api/election-night/refresh', { method: 'POST' }, 'public-refresh'],
      ['/api/monitor/refresh', { method: 'POST', headers: { Authorization: 'Bearer ' + token } }, 'editor-refresh'],
    ];
    for (const [path, init, trigger] of cases) {
      await newsroom.exec("DELETE FROM metadata WHERE key = 'live_monitor_started'");
      for (const id of ['northeast-ms-cnn', 'west-ak-cnn']) {
        const storage = await mf.unsafeGetDurableObjectStorage('tracking-scope', 'ElectionMonitor', { name: id });
        // A first access can precede constructor initialization; the first run
        // below creates storage, later runs clear only its collection lease.
        try { await storage.exec("DELETE FROM metadata WHERE key = 'started'"); } catch {}
      }
      const before = urls.length;
      assert.equal((await fetch(path, init)).status, 200);
      assert.equal(urls.length - before, 2);
      const monitor = await (await fetch('/api/monitor')).json();
      assert.deepEqual(monitor.activeAdapters, ['northeast-ms-cnn', 'west-ak-cnn']);
      assert.deepEqual(monitor.races.filter(r => r.automaticTracking).map(r => r.state).sort(), ['AK', 'MS']);
      const ak = monitor.races.find(r => r.race === 'alaska');
      assert.equal(ak.totalVotes, 213180);
      assert.equal(ak.sourceKind, 'supplier');
      const mi = monitor.races.find(r => r.target === 'senate-mi');
      assert.equal(mi.automaticTracking, false);
      assert.equal(mi.totalVotes, 100);
      assert.equal(mi.lastSuccessAt, '2026-11-04T01:00:00Z');
      assert.match(mi.message, /paused/);
      assert.equal((await newsroom.exec("SELECT value FROM metadata WHERE key = 'live_batch_northeast-mi-cnn'"))[0].value, paused);
      const log = await (await fetch('/api/monitor/checks')).json();
      assert.ok(log.checks.slice(0, 2).every(c => c.trigger === trigger && c.success));
      assert.deepEqual(log.sources.filter(s => s.automaticTracking).map(s => s.adapter), monitor.activeAdapters);
      assert.equal((await fetch(log.checks[0].snapshotUrl)).status, 200);
    }
    assert.equal(new Set(urls).size, 2);
    assert.equal((await newsroom.exec("SELECT COUNT(*) AS n FROM metadata WHERE key = 'live_batch_completion-cnn'"))[0].n, 0);
  } finally { await mf.dispose(); }
});

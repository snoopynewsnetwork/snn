import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { build } from 'esbuild';
import { Miniflare, convertV4MiniflareOptions } from 'miniflare';
import { electionAdapters } from '../src/election-adapters.ts';

// Exercise every production endpoint configuration through the real collector,
// RPC coordinator and SQLite. Stub parsers here; adapter fixtures separately
// verify source/contest validation, and election-monitor.test verifies receipts
// for rejected results. No public election server is contacted by these tests.
test('all registered sources feed one persistent, globally bounded check log', { timeout: 60000 }, async () => {
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
    plugins: [{ name: 'fixture-parsers', setup(build) {
      build.onResolve({ filter: /^\.\/election-adapters$/ }, () => ({ path: 'catalog', namespace: 'test' }));
      build.onLoad({ filter: /.*/, namespace: 'test' }, () => ({ resolveDir: process.cwd(), contents: `
        import { electionAdapters as registry } from ${JSON.stringify(join(process.cwd(), 'src/election-adapters.ts'))};
        export const electionAdapters = registry.map(adapter => ({ ...adapter,
          parse: () => Object.fromEntries(adapter.targets.map(target => [target.id, {
            status: 'setup', message: 'Fixture setup', candidates: [
              {name:'D',party:'DEM',votes:0}, {name:'R',party:'REP',votes:0}], totalVotes:0
          }])) }));
        export function electionAdapter(id) { return electionAdapters.find(adapter => adapter.id === id); }
      ` }));
    }}],
  });
  const directory = await mkdtemp(join(tmpdir(), 'snn-check-log-'));
  const sourceCount = electionAdapters.reduce((count, adapter) => count + adapter.sources.length, 0);
  const expected = electionAdapters.flatMap(adapter => adapter.sources.map(source => `${adapter.id}:${source.id}`)).sort();
  let requests = 0, notModified = false, content = '1', fail = false;
  const options = convertV4MiniflareOptions({
    name: 'check-log-test', modules: true, script: built.outputFiles[0].text, compatibilityDate: '2026-10-17',
    bindings: { ADMIN_TOKEN: 'test-editor-token-at-least-32-characters' },
    durableObjects: { NEWSROOM: { className: 'Newsroom', useSQLite: true }, LIVE_MONITORS: { className: 'ElectionMonitor', useSQLite: true } },
    resourcePersistencePath: directory, unsafeInspectDurableObjects: true,
    outboundService: request => {
      requests++;
      assert.ok(!request.url.includes('{version}'));
      if (fail) return new Response('Upstream failure', { status: 503 });
      return notModified ? new Response(null, { status: 304 }) : new Response(content, { headers: { ETag: '"fixture"' } });
    },
  });
  let mf = new Miniflare(options);
  const fetch = (path, init) => mf.dispatchFetch(`http://localhost${path}`, init);
  const log = async () => {
    const response = await fetch('/api/monitor/checks');
    assert.equal(response.status, 200);
    assert.equal(response.headers.get('Cache-Control'), 'no-store');
    return response.json();
  };
  const refresh = async (path = '/api/election-night/refresh', headers) => {
    assert.equal((await fetch(path, { method: 'POST', headers })).status, 200);
    return log();
  };
  const unlock = async () => {
    const newsroom = await mf.unsafeGetDurableObjectStorage('check-log-test', 'Newsroom', { name: 'senate-2026' });
    await newsroom.exec("DELETE FROM metadata WHERE key = 'live_monitor_started'");
    await Promise.all(electionAdapters.map(async adapter => {
      const storage = await mf.unsafeGetDurableObjectStorage('check-log-test', 'ElectionMonitor', { name: adapter.id });
      await storage.exec("DELETE FROM metadata WHERE key = 'started'");
    }));
    return newsroom;
  };
  try {
    const empty = await log();
    assert.deepEqual(empty.checks, []);
    assert.deepEqual(empty.sources.map(source => `${source.adapter}:${source.id}`).sort(), expected);
    assert.ok(empty.sources.every(source => source.lastCheck === null));
    assert.equal(requests, 0, 'Reading the log never contacts publishers');
    assert.equal((await fetch('/api/monitor/checks', { method: 'POST' })).status, 405);

    const first = await refresh();
    assert.equal(requests, sourceCount);
    assert.equal(first.checks.length, sourceCount);
    assert.deepEqual(first.checks.map(check => `${check.adapter}:${check.sourceId}`).sort(), expected);
    assert.ok(first.checks.every(check => check.success && check.change === 'initial' && check.trigger === 'public-refresh'));
    assert.ok(first.checks.every(check => check.httpStatus === 200 && check.snapshotId && check.responseHash && !check.error));
    assert.ok(first.sources.every(source => source.lastCheck.success));
    for (const check of first.checks) {
      assert.ok(!check.sourceUrl.includes('{version}'));
      assert.equal((await fetch(check.snapshotUrl)).status, 200, 'Evidence links include the owning adapter');
    }
    assert.deepEqual((await refresh()).checks, first.checks, 'Lease skips do not manufacture receipts');
    assert.equal(requests, sourceCount);

    await unlock(); notModified = true;
    await fetch('/test-scheduled');
    const scheduled = await log();
    assert.equal(scheduled.checks.length, 2 * sourceCount);
    assert.ok(scheduled.checks.slice(0, sourceCount).every(check => check.success && check.httpStatus === 304 && check.change === 'unchanged' && check.trigger === 'scheduled'));

    await unlock(); notModified = false; content = '2';
    const changed = await refresh('/api/monitor/refresh', { Authorization: 'Bearer test-editor-token-at-least-32-characters' });
    assert.ok(changed.checks.slice(0, sourceCount).every(check => check.success && check.change === 'changed' && check.trigger === 'editor-refresh'));

    await unlock(); fail = true;
    const capped = await refresh();
    assert.equal(capped.limit, 200);
    assert.equal(capped.checks.length, 200);
    const recent = capped.checks.slice(0, sourceCount);
    assert.ok(recent.every(check => !check.success && check.error && check.change === 'unknown'));
    assert.ok(recent.some(check => check.httpStatus === null), 'Blocked version prerequisites record a check without fabricating HTTP');
    assert.ok(capped.sources.every(source => source.lastCheck && !source.lastCheck.success));
    const times = capped.checks.map(check => check.checkedAt);
    assert.deepEqual(times, [...times].sort().reverse(), 'Parallel collectors are ordered by check time');
    const storage = await unlock();
    assert.equal((await storage.exec('SELECT COUNT(*) AS count FROM source_checks'))[0].count, 200, 'Old receipts are actually removed');

    const countBeforeBackoff = requests;
    await fetch('/test-scheduled');
    assert.equal(requests, countBeforeBackoff);
    assert.deepEqual((await log()).checks, capped.checks, 'Backoff skips do not add receipts');
    await mf.dispose();
    mf = new Miniflare(options);
    const restored = await log();
    assert.deepEqual(restored.checks, capped.checks);
    assert.deepEqual(restored.sources, capped.sources);
  } finally {
    await mf.dispose();
    await rm(directory, { recursive: true, force: true });
  }
});

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readSourceBody, resolveSourceUrl, sourceLayers } from '../src/election-fetch.ts';

const version = { id: 'version', url: 'https://results.example/current_ver.txt' };
const summary = { id: 'summary', url: 'https://results.example/2026/{version}/summary.json', dependsOn: 'version' };

test('version-scoped feeds use validated numeric prerequisites and dependency order', () => {
  assert.deepEqual(sourceLayers([summary, version]), [[version], [summary]]);
  assert.equal(resolveSourceUrl(summary, { version: '383360\n' }), 'https://results.example/2026/383360/summary.json');
  for (const value of ['', '../2024', 'https://other.example', '1234567890123', 'test'])
    assert.throws(() => resolveSourceUrl(summary, { version: value }));
  assert.throws(() => sourceLayers([summary]));
  assert.throws(() => sourceLayers([{ ...version, dependsOn: 'summary' }, summary]));
  assert.throws(() => sourceLayers([version, version]));
});

test('source bodies enforce byte limits and preserve binary responses as base64', async () => {
  const bytes = Uint8Array.from([0x50, 0x4b, 0xff, 0, 0x80]);
  const encoded = await readSourceBody(new Response(bytes), { ...version, encoding: 'base64' });
  assert.deepEqual(Buffer.from(encoded, 'base64'), Buffer.from(bytes));
  await assert.rejects(readSourceBody(new Response(bytes), { ...version, maxBytes: 4 }), /byte limit/);
  await assert.rejects(readSourceBody(new Response(bytes), version));
  await assert.rejects(readSourceBody(new Response('   '), version), /blank/);
  assert.equal(await readSourceBody(new Response('café'), version), 'café');
});

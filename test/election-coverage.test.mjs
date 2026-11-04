import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { electionAdapters } from '../src/election-adapters.ts';
import { sourceLayers } from '../src/election-fetch.ts';
import { groupMembers } from '../src/live-results.ts';

const guide = JSON.parse(readFileSync(new URL('../public/election-guide.json', import.meta.url)));

test('live registry covers every sheet race and group member with unique, bounded source configurations', () => {
  const targets = electionAdapters.flatMap(adapter => adapter.targets);
  const ids = targets.map(target => target.id);
  assert.equal(new Set(ids).size, ids.length, 'No race is overwritten by a second adapter');
  assert.equal(new Set(electionAdapters.map(adapter => adapter.id)).size, electionAdapters.length);
  assert.equal(new Set(targets.map(target => target.state)).size, 26);
  for (const target of [...guide.senate, ...guide.house]) {
    if (target.group) {
      assert.ok(groupMembers[target.id]?.length);
      for (const id of groupMembers[target.id]) assert.ok(ids.includes(id), `${target.id} member ${id}`);
    } else assert.ok(ids.includes(target.id), target.id);
  }
  // The coordinator fans out one RPC per adapter; each has its own source budget.
  assert.ok(electionAdapters.length < 50);
  for (const adapter of electionAdapters) {
    assert.ok(adapter.sources.length < 50, adapter.id);
    sourceLayers(adapter.sources);
    for (const target of adapter.targets) {
      assert.ok(!groupMembers[target.id], 'Groups are derived from individual member races');
      if (target.sourceId) assert.ok(adapter.sources.some(source => source.id === target.sourceId), `${target.id} provenance`);
    }
    for (const source of adapter.sources) {
      assert.match(source.url, /^https?:\/\//);
      assert.match(source.authorityUrl, /^https?:\/\//);
      assert.equal(typeof source.official, 'boolean');
      assert.ok((source.maxBytes ?? 2_000_000) <= 32_000_000);
    }
  }
});

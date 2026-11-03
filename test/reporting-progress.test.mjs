import test from 'node:test';
import assert from 'node:assert/strict';
import { reportingProgress } from '../public/election-model.js';

const now = Date.parse('2026-11-03T23:40:00Z');
const live = { status: 'reporting', totalVotes: 4029, coverage: 'complete', lastSuccessAt: new Date(now).toISOString() };

test('dashboard shows source estimates before precinct counts, without inferring votes remaining', () => {
  assert.equal(reportingProgress({ ...live, estimatedVotePercent: 1, reportedPrecincts: 2, totalPrecincts: 100 }, now), '1% est. votes counted');
  assert.equal(reportingProgress({ ...live, estimatedVotePercent: 0 }, now), '0% est. votes counted');
  assert.equal(reportingProgress({ ...live, estimatedVotePercent: 100 }, now), '100% est. votes counted');
  assert.equal(reportingProgress({ ...live, estimatedVotePercent: 47.8312 }, now), '47% est. votes counted');
  assert.equal(reportingProgress({ ...live, estimatedVotePercent: 99.9 }, now), '99% est. votes counted');
  assert.equal(reportingProgress({ ...live, estimatedVotePercent: 0.4 }, now), '<1% est. votes counted');
  assert.equal(reportingProgress({ ...live, reportedPrecincts: 1234, totalPrecincts: 2000 }, now), '1,234 / 2,000 precincts reporting');
});

test('dashboard hides unavailable, stale, setup, partial, group and invalid progress', () => {
  for (const patch of [
    { status: 'setup' }, { status: 'error' }, { totalVotes: 0 }, { coverage: 'partial' }, { members: ['a'] },
    { lastSuccessAt: undefined }, { lastSuccessAt: new Date(now - 16 * 60_000).toISOString() },
    { lastSuccessAt: new Date(now + 120_000).toISOString() },
  ]) assert.equal(reportingProgress({ ...live, estimatedVotePercent: 1, ...patch }, now), '');
  for (const estimatedVotePercent of [undefined, null, '1', -1, 101, NaN, Infinity])
    assert.equal(reportingProgress({ ...live, estimatedVotePercent }, now), '');
  for (const [reportedPrecincts, totalPrecincts] of [[1, 0], [3, 2], [-1, 2], [1.5, 2], [1, undefined]])
    assert.equal(reportingProgress({ ...live, reportedPrecincts, totalPrecincts }, now), '');
  assert.equal(reportingProgress(undefined, now), '');
});

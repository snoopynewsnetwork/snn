import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parseCompletion, completionEstimate, completionAdapter } from '../src/completion.ts';
import { electionAdapters } from '../src/election-adapters.ts';
import { hasValidCounts } from '../src/live-results.ts';
import { buildBasicForecast } from '../src/basic-forecast.ts';
import { buildNeedle } from '../src/needles.ts';

const bodies = Object.fromEntries(completionAdapter.sources.map(s => [s.id, readFileSync(new URL(`fixtures/completion/${s.id}.json`, import.meta.url), 'utf8')]));
const read = id => JSON.parse(bodies[id]);
const now = Date.parse('2026-11-04T01:00:00Z');
function reporting(percent = 50, votes = [600, 400]) {
  const rows = read('completion-SG');
  const row = rows.find(r => r.ecKey === '2026-SG-MI');
  row.totalVote = votes.reduce((a, b) => a + b, 0); row.percentReporting = percent; row.raceEmbargo.votesReleased = true;
  row.candidates.forEach((c, i) => c.voteNum = votes[i] ?? 0);
  row.extractedAt = '2026-11-04T01:00:00Z';
  return { ...bodies, 'completion-SG': JSON.stringify(rows) };
}

test('pinned shared feeds cover every tracked target including both local supporting views', () => {
  const parsed = parseCompletion(bodies);
  assert.equal(Object.keys(parsed).length, 74);
  for (const target of electionAdapters.flatMap(a => a.targets).filter(target => target.id !== 'house-ky-06-counties'))
    assert.equal(parsed[target.id].status, 'setup', target.id);
  assert.equal(parsed['house-ky-06-counties'], undefined, 'The county-detail helper uses the KY-06 race completion estimate, not a separate denominator');
  assert.equal(parsed['senate-mi-detroit'].coverage, 'partial');
  assert.equal(parsed['senate-ks-johnson'].coverage, 'partial');
});

test('source-consistent remaining estimates replace downward corrections and never use precincts', () => {
  const value = parseCompletion(reporting())['senate-mi'];
  const live = { ...value, race: 'senate-mi', lastSuccessAt: new Date(now).toISOString(), sourceUrl: 'https://example.org' };
  assert.equal(completionEstimate(live, now).estimatedRemainingVotes, 1000);
  const correction = parseCompletion(reporting(50, [400, 300]))['senate-mi'];
  assert.equal(completionEstimate({ ...live, ...correction }, now).estimatedRemainingVotes, 700);
  assert.deepEqual(completionEstimate({ ...live, ...correction }, now).candidates, correction.candidates);
  for (const p of [0, 100, undefined]) assert.equal(completionEstimate({ ...live, estimatedVotePercent: p, reportedPrecincts: 2, totalPrecincts: 4 }, now).estimatedRemainingVotes, null);
  assert.equal(completionEstimate(live, now + 16 * 60_000).percentCounted, null);
  assert.equal(completionEstimate({ ...live, sourceUpdated: '2026-11-03T20:00:00Z' }, now).status, 'stale');
});

test('invalid identities, missing percentages, pre-embargo counts, and malformed feeds fail closed per target', () => {
  for (const patch of [
    r => r.percentReporting = -1, r => delete r.percentReporting,
    r => r.externalKey = 'test-key', r => r.totalVote--, r => r.stateAbbreviation = 'OH',
    r => r.candidates[0].fullName = 'Wrong candidate', r => r.raceEmbargo.votesReleased = false,
    r => r.raceEmbargo.assignedPollsClose++, r => r.extractedAt = '2024-11-05T01:00:00Z',
  ]) {
    const data = reporting(), rows = JSON.parse(data['completion-SG']); patch(rows.find(r => r.ecKey === '2026-SG-MI'));
    data['completion-SG'] = JSON.stringify(rows); const results = parseCompletion(data);
    assert.equal(results['senate-mi'].status, 'unavailable'); assert.equal(results['house-va-07'].status, 'setup');
  }
  const missing = { ...bodies }; delete missing['completion-local-MI'];
  assert.equal(parseCompletion(missing)['senate-mi-detroit'].status, 'unavailable');
  const locals = read('completion-local-MI'); locals.push(locals[0]);
  assert.equal(parseCompletion({ ...bodies, 'completion-local-MI': JSON.stringify(locals) })['senate-mi-detroit'].status, 'unavailable');
});

test('real CNN Georgia totals retain unallocated votes instead of falling back to a neutral prior', () => {
  const row = JSON.parse(readFileSync(new URL('fixtures/completion/cnn-ga-unallocated.json', import.meta.url)));
  const gg = read('completion-GG').map(r => r.ecKey === row.ecKey ? row : r);
  const result = parseCompletion({ ...bodies, 'completion-GG': JSON.stringify(gg) })['governor-ga'];
  assert.equal(result.status, 'reporting'); assert.equal(result.totalVotes, 3224711); assert.equal(result.unallocatedVotes, 2);
  assert.equal(result.projection, null, 'A lead and released calls are not a winner flag');
  const live = { ...result, target: 'governor-ga', race: 'governor-ga', sourceUrl: 'https://politics.api.cnn.io/results/national-races/2026-GG.json', lastSuccessAt: row.extractedAt + 'Z' };
  assert.equal(hasValidCounts(live), true);
  const inputs = { races: [], completion: [live], ledgerUpdates: [], lastCheckedAt: live.lastSuccessAt };
  const at = Date.parse(live.lastSuccessAt), run = buildBasicForecast(inputs, at);
  const needle = buildNeedle('governor-ga', inputs, run, at);
  assert.equal(needle.modelInput.basis, 'live'); assert.equal(needle.modelInput.unallocatedVotes, 2);
  assert.ok(needle.probabilities.D > .5);
  assert.equal(hasValidCounts({ ...live, unallocatedVotes: -1 }), false);
});

test('CNN governor projections fix the model outcome and fresh retractions clear it, independently of completion', () => {
  const row = JSON.parse(readFileSync(new URL('fixtures/completion/cnn-ga-unallocated.json', import.meta.url)));
  row.candidates[0].winner = true;
  delete row.percentReporting; // A validated call does not depend on a completion estimate.
  const parse = () => parseCompletion({ ...bodies, 'completion-GG': JSON.stringify(read('completion-GG').map(r => r.ecKey === row.ecKey ? row : r)) })['governor-ga'];
  let result = parse(); assert.equal(result.projection.candidate, 'Keisha Lance Bottoms'); assert.equal(result.winner, undefined);
  const at = Date.parse(row.extractedAt + 'Z');
  const predict = result => { const inputs = { races: [], completion: [{ ...result, target: 'governor-ga', race: 'governor-ga', sourceUrl: 'https://politics.api.cnn.io/results/national-races/2026-GG.json', lastSuccessAt: new Date(at).toISOString() }], lastCheckedAt: null };
    return buildNeedle('governor-ga', inputs, buildBasicForecast(inputs, at), at); };
  assert.deepEqual(predict(result).probabilities, { D: 1, R: 0, other: 0 }); assert.equal(predict(result).modelInput.basis, 'declared');
  row.candidates[0].winner = false; result = parse(); assert.equal(result.projection, null); assert.equal(predict(result).modelInput.basis, 'prior');
  row.candidates.forEach(c => c.winner = true); assert.equal(parse().projection, undefined);
  row.candidates[1].winner = false; row.raceEmbargo.callsReleased = false; assert.equal(parse().projection, undefined);
});

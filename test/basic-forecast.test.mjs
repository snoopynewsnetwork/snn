import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildBasicForecast, BASIC_DRAWS } from '../src/basic-forecast.ts';
import { parseLedgerFeed } from '../src/chamber-ledger.ts';
import { buildNeedle, validateForecastRun, needleCatalog } from '../src/needles.ts';

const now = Date.parse('2026-11-04T01:05:00Z');
const monitor = () => ({ races: [{ target: 'senate-mi', name: 'Michigan', chamber: 'senate' }], completion: [], lastCheckedAt: new Date(now).toISOString() });
const row = () => JSON.parse(readFileSync(new URL('fixtures/ledger/senate.json', import.meta.url))).find(r => r.ecKey === '2026-SG-MI');
function withVotes(d, r, percent, patch = {}) {
  const source = row();
  source.candidates.forEach(c => { c.voteNum = c.majorParty === 'DEM' ? d : c.majorParty === 'REP' ? r : 0; c.winner = false; });
  source.totalVote = d + r; source.percentReporting = percent; source.extractedAt = new Date(now).toISOString(); source.raceEmbargo.votesReleased = true;
  Object.assign(source, patch);
  const updates = parseLedgerFeed('senate', JSON.stringify([source]), new Date(now).toISOString());
  // Omitted fixture rows are intentionally under review; only Michigan is changed.
  return { ...monitor(), ledgerUpdates: updates };
}
const probabilities = (run, inputs) => buildNeedle('senate-mi', inputs, run, now).probabilities;

test('basic model produces reproducible complete joint inputs with an explicit experimental status', () => {
  const inputs = monitor(), run = buildBasicForecast(inputs, now);
  validateForecastRun(run, now);
  assert.equal(run.races.length, 473);
  assert.equal(new Set(run.races.map(r => r.seatId)).size, 473);
  assert.ok(run.races.every(r => r.outcomes.length === BASIC_DRAWS && /^[DRO]+$/.test(r.outcomes)));
  assert.deepEqual(run.races, buildBasicForecast(inputs, now + 1000).races, 'Unchanged inputs do not jitter on clock changes');
  assert.equal(run.releaseStatus, 'experimental'); assert.equal(run.calibrationUrl, null);
  assert.equal(needleCatalog(inputs, run).length, 3, 'Default page stays scoped to tracked races and two chambers');
  assert.equal(needleCatalog(inputs, run, true).length, 475);
  const chamber = buildNeedle('house-control', inputs, run, now);
  assert.equal(chamber.status, 'experimental'); assert.equal(chamber.missingSeats, 0);
  assert.ok(chamber.modelCoverage.prior > 0);
  assert.ok(Math.abs(Object.values(chamber.probabilities).reduce((a, b) => a + b, 0) - 1) < 1e-12);
  assert.ok(buildNeedle('house-al-01', inputs, run, now), 'Untracked forecasts retain individual API representations');
});

test('counted votes stay fixed: late strong leads cannot be overturned by the modeled remaining votes; corrections replace them', () => {
  const inputs = withVotes(8000, 2000, 99);
  let run = buildBasicForecast(inputs, now), needle = buildNeedle('senate-mi', inputs, run, now);
  assert.deepEqual(needle.probabilities, { D: 1, R: 0, other: 0 });
  assert.equal(needle.modelInput.basis, 'live'); assert.ok(needle.marginInterval[0] > 58);
  const correction = withVotes(2000, 8000, 99);
  run = buildBasicForecast(correction, now);
  assert.deepEqual(probabilities(run, correction), { D: 0, R: 1, other: 0 });
  assert.equal(buildNeedle('senate-mi', correction, run, now).modelInput.totalVotes, 10000);
});

test('completion determines how much uncertainty remains rather than treating votes as random ballots', () => {
  const early = withVotes(5100, 4900, 5), late = withVotes(5100, 4900, 99);
  const pEarly = probabilities(buildBasicForecast(early, now), early).D;
  const pLate = probabilities(buildBasicForecast(late, now), late).D;
  assert.ok(pEarly > .2 && pEarly < .8); assert.equal(pLate, 1);
  const capped = withVotes(5100, 4900, 100), run = buildBasicForecast(capped, now);
  assert.ok(run.assumptions.some(a => a.includes('99%')));
  assert.ok(buildNeedle('senate-mi', capped, run, now).marginInterval[0] < 2, '100% still retains modeled uncertainty');
});

test('missing completion, stale counts, unallocated votes and invalid sources fall back to the same disclosed neutral prior', () => {
  const base = withVotes(0, 0, 0), expected = buildBasicForecast(base, now).races.find(r => r.id === 'senate-mi').outcomes;
  for (const input of [
    withVotes(9999, 1, undefined), withVotes(9999, 1, 0), withVotes(9999, 1, 101),
    withVotes(9999, 1, 50, { totalVote: 10001 }),
    withVotes(9999, 1, 50, { externalKey: 'test-key' }),
    withVotes(9999, 1, 50, { extractedAt: '2026-11-04T00:00:00Z' }),
  ]) {
    const forecast = buildBasicForecast(input, now).races.find(r => r.id === 'senate-mi');
    assert.equal(forecast.input.basis, 'prior'); assert.equal(forecast.outcomes, expected); assert.equal(forecast.margins, undefined);
  }
  const broken = withVotes(9999, 1, 50); broken.ledgerUpdates.find(u => u.id === 'senate-mi-2').reason = 'Latest fetch failed';
  assert.equal(buildBasicForecast(broken, now).races.find(r => r.id === 'senate-mi').outcomes, expected);
});

test('explicit projections are fixed outcomes, but independent winners are never assigned a caucus', () => {
  const inputs = monitor(), run = buildBasicForecast(inputs, now);
  assert.equal(run.races.find(r => r.id === 'house-fl-05').outcomes, 'R'.repeat(BASIC_DRAWS));
  const ne = run.races.find(r => r.id === 'senate-ne');
  assert.ok(ne.outcomes.includes('O')); assert.ok(!ne.outcomes.includes('D'));
  const neNeedle = buildNeedle('senate-ne', inputs, run, now);
  assert.equal(neNeedle.probabilities.D, 0); assert.ok(neNeedle.probabilities.other > .1);
  assert.equal(buildNeedle('house-control', inputs, run, now + 16 * 60_000).probabilities, null);
});

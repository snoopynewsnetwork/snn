import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { test } from 'node:test';
import { parseKy06Counties } from '../src/adapters/ky06-counties.ts';
import { countyCoverage, countyScenario, scenarioRemaining } from '../public/ky-06-model.js';

const body = gunzipSync(readFileSync(new URL('./fixtures/civic-ky06-counties.json.gz', import.meta.url))).toString();
const baseline = JSON.parse(readFileSync(new URL('../public/ky-06-counties.json', import.meta.url)));
const feed = () => JSON.parse(body);

test('KY-06 county source preserves all candidates, all 16 portions and district reconciliation', () => {
  const parsed = parseKy06Counties(body);
  assert.equal(parsed.counties.length, 16);
  assert.equal(parsed.totalVotes, 4029);
  assert.equal(parsed.counties.find(c => c.name === 'Anderson').totalVotes, 4029);
  assert.equal(parsed.counties.find(c => c.name === 'Fayette').totalVotes, 0);
  assert.equal(parsed.candidates.reduce((sum, c) => sum + c.votes, 0), 4029);
  for (const candidate of parsed.candidates)
    assert.equal(parsed.counties.reduce((sum, county) => sum + county.candidates.find(c => c.name === candidate.name && c.party === candidate.party).votes, 0), candidate.votes);
  assert.equal(parsed.counties.find(c => c.name === 'Anderson').sourceReporting, 33.3);
  assert.equal(parsed.reportedPrecincts, undefined);
  assert.equal(parsed.totalPrecincts, undefined);
});

test('county election, geography, candidates and inconsistent sums fail closed', () => {
  for (const patch of [{ country: 'CA' }, { province: 'US' }, { district: 'KY-05' }, { election_date: '2024-11-05T05:00:00Z' },
    { test_data: true }, { is_disputed: true }, { election_scope: 'Primary' }, { round: 2 }, { election_name: 'Other' }])
    assert.throws(() => parseKy06Counties(JSON.stringify({ ...feed(), ...patch })));
  const invalid = [
    data => delete data.region_results.bath,
    data => data.region_results.bath.fips = '21005',
    data => data.region_results.bath.name = 'Another county',
    data => data.region_results.bath.type = 'Precinct',
    data => data.region_results.bath.candidates.pop(),
    data => data.region_results.bath.candidates[0].votes = 1,
    data => data.region_results.bath.candidates[0].votes = -1,
    data => data.region_results.bath.candidates[0].votes = '0',
    data => data.region_results.bath.candidates[0].votes = 1.1,
    data => data.region_results.bath.candidates[0].party = 'Republican',
    data => data.candidates[0].candidate_id = 12345,
    data => data.candidates.push({ candidate_id: 1, name: 'Other Republican', party: 'Republican', votes: 0 }),
    data => data.region_results.bath.candidates[0] = data.region_results.bath.candidates[1],
  ];
  for (const mutate of invalid) { const data = feed(); mutate(data); assert.throws(() => parseKy06Counties(JSON.stringify(data))); }
});

test('zero county counts retain historical weight without implying zero turnout or completed counting', () => {
  const coverage = countyCoverage(baseline.counties, parseKy06Counties(body));
  assert.equal(coverage.missing.length, 15);
  assert.ok(coverage.missing.some(c => c.name === 'Fayette'));
  assert.equal(coverage.rows.find(c => c.name === 'Anderson').liveOther, 178);
  assert.ok(Math.abs(coverage.missingWeight - 100 * (352638 - 10483) / 352638) < 1e-10);
  assert.equal(countyCoverage(baseline.counties, undefined), null);
  const partial = parseKy06Counties(body); partial.counties.pop();
  assert.equal(countyCoverage(baseline.counties, partial), null);
});

test('conditional remaining votes subtract only D+R, retain negatives and flag infeasible county allocations', () => {
  const coverage = countyCoverage(baseline.counties, parseKy06Counties(body));
  const tie = countyScenario(baseline.counties, { margin: 0 });
  const remaining = scenarioRemaining(tie, coverage);
  assert.equal(remaining.total, 352638 - 2312 - 1539);
  assert.equal(remaining.r, 176319 - 2312);
  assert.equal(remaining.d, 176319 - 1539);
  assert.equal(remaining.feasible, true);
  assert.equal(remaining.requiredDShare, 100 * remaining.d / remaining.total);
  const low = scenarioRemaining(countyScenario(baseline.counties, { margin: 0, turnout: 10 }), coverage);
  assert.equal(low.feasible, false);
  const anderson = low.rows.find(c => c.name === 'Anderson');
  assert.ok(anderson.r < 0 && anderson.d < 0);
  assert.ok(anderson.r + anderson.d < 0, 'Do not silently floor a breached scenario to zero');
  const republicanSweep = scenarioRemaining(countyScenario(baseline.counties, { margin: -100 }), coverage);
  assert.equal(republicanSweep.districtFeasible, false);
  assert.equal(republicanSweep.requiredDShare, null, 'An impossible target cannot display a feasible remaining-vote share');
});

test('100% provider reporting and downward corrections do not manufacture a vote-completion estimate', () => {
  const data = feed();
  Object.values(data.region_results).forEach(c => { c.percent_reporting = 100; });
  data.candidates[0].votes -= 100;
  data.region_results.anderson.candidates.find(c => c.party === 'Republican').votes -= 100;
  const parsed = parseKy06Counties(JSON.stringify(data));
  assert.equal(parsed.totalVotes, 3929);
  assert.equal(countyCoverage(baseline.counties, parsed).missing.length, 15);
  assert.equal(parsed.reporting, undefined);
  assert.equal(parsed.votesRemaining, undefined);
  assert.equal(parsed.winner, undefined);
});

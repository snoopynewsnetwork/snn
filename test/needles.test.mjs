import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import { independentSeatDistribution, chamberDistribution } from '../src/needle-model.ts';
import { buildNeedle, needleCatalog, validateForecastRun } from '../src/needles.ts';
import houseSeats from '../src/data/house-seats.json' with { type: 'json' };
import senateSeats from '../src/data/senate-seats.json' with { type: 'json' };
import { buildChamberLedger } from '../src/chamber-ledger.ts';

const now = Date.parse('2026-11-04T01:00:00Z');
const race = (id, outcomes, chamber = 'senate') => ({ id, name: id, chamber, seatId: `${id}-${id === 'senate-mi' ? 2 : 3}`, outcomes });
const fixed = (id, caucus) => ({ id, caucus, sourceUrl: 'https://example.org/baseline', basis: 'declared' });
const run = () => ({ electionDate: '2026-11-03', asOf: new Date(now).toISOString(), modelVersion: 'test-1',
  calibrationUrl: 'https://example.org/calibration', assumptions: [],
  races: [race('senate-mi', 'DDRR')], fixedSeats: { house: [], senate: [] }, senateTieBreaker: 'R' });
const monitor = { races: [{ target: 'senate-mi', name: 'Michigan', chamber: 'senate', status: 'reporting', sourceUrl: 'https://example.org/results' },
  { target: 'senate-mi-detroit', chamber: 'senate' }, { target: 'senate-ks-johnson', chamber: 'senate' }], completion: [], lastCheckedAt: new Date(now).toISOString() };

const client = readFileSync(new URL('../public/needle.js', import.meta.url), 'utf8');
const renderDetails = data => runInNewContext(client.slice(0, client.indexOf("\n$('#needle-search').addEventListener")) + '\nraceDetails(data)',
  { data, URL, location: { origin: 'https://snn.example' } });
function texasInputs() {
  const snapshot = (sourceUrl, candidates, extra = {}) => ({ target: 'senate-tx', name: 'Texas', chamber: 'senate',
    status: 'reporting', sourceUrl, candidates, totalVotes: candidates.reduce((sum, c) => sum + c.votes, 0),
    lastSuccessAt: new Date(now).toISOString(), sourceUpdated: new Date(now).toISOString(), ...extra });
  return { ...monitor, races: [snapshot('https://sos.example/results', [
    { name: 'Ken Paxton', party: 'REP', votes: 858327 }, { name: 'James Talarico', party: 'DEM', votes: 761214 },
  ], { sourceKind: 'official', sourceName: 'Texas SOS', sourceUpdated: 'Nov 04, 2026 02:19:21 CT' })], completion: [snapshot('https://cnn.example/results', [
    { name: 'James Talarico', party: 'DEM', votes: 2513352 }, { name: 'Ken Paxton', party: 'REP', votes: 1746623 },
    { name: 'Ted Brown', party: 'LIB', votes: 66000 },
  ], { sourceName: 'CNN', estimatedVotePercent: 42 })] };
}

test('Texas needle pairs CNN completion with its own candidates and labels SOS returns separately', () => {
  const inputs = texasInputs();
  const needle = buildNeedle('senate-tx', inputs, null, now);
  assert.deepEqual(needle.completion.candidates, inputs.completion[0].candidates);
  assert.equal(needle.completion.supplierVotes, 4325975);
  assert.equal(needle.completion.percentCounted, 42);
  assert.equal(needle.completion.candidates.reduce((sum, c) => sum + c.votes, 0), needle.completion.supplierVotes);
  assert.deepEqual(needle.observed.candidates, inputs.races[0].candidates, 'Selected source API remains available');
  const html = renderDetails(needle), [primary, separate] = html.split('<details>');
  assert.match(primary, /Live returns · CNN/);
  assert.match(primary, /2,513,352/); assert.match(primary, /1,746,623/);
  assert.match(primary, /42% of expected vote counted for the returns above/);
  assert.doesNotMatch(primary, /858,327|761,214/);
  assert.match(separate, /Separate official returns/); assert.match(separate, /Texas SOS/);
  assert.match(separate, /858,327/); assert.match(separate, /761,214/);
  assert.match(separate, /does not apply to these totals/);
  assert.match(separate, /https:\/\/sos.example\/results/);
  assert.match(separate, /Nov 04, 2026 02:19:21 CT/); assert.doesNotMatch(separate, /Invalid Date/);
});

test('stale or failed completion retains its own counts without attaching a current percentage', () => {
  for (const patch of [{ lastSuccessAt: new Date(now - 16 * 60_000).toISOString() }, { status: 'error' }]) {
    const inputs = texasInputs(); Object.assign(inputs.completion[0], patch);
    const needle = buildNeedle('senate-tx', inputs, null, now);
    assert.equal(needle.completion.percentCounted, null);
    const [primary] = renderDetails(needle).split('<details>');
    assert.match(primary, /2,513,352/); assert.match(primary, /Unknown share/);
    assert.doesNotMatch(primary, /42%|858,327/);
  }
});

test('missing completion counts never attach an orphaned percentage to official or model totals', () => {
  for (const completion of [[], [{ target: 'senate-tx', status: 'unavailable', sourceUrl: 'https://cnn.example/results', estimatedVotePercent: 42 }]]) {
    const inputs = { ...texasInputs(), completion };
    const needle = buildNeedle('senate-tx', inputs, null, now), html = renderDetails(needle);
    assert.match(html, /858,327/); assert.match(html, /Share of expected vote counted is unknown for these returns/);
    assert.doesNotMatch(html, /42%|Separate official returns/);
  }
  const data = run();
  data.races[0].input = { basis: 'live', reason: 'Published model snapshot', sourceUrl: 'https://model.example/results',
    sourceUpdated: new Date(now).toISOString(), checkedAt: new Date(now).toISOString(), totalVotes: 1000, percentCounted: 40,
    candidates: [{ name: 'Model candidate', party: 'DEM', votes: 1000 }] };
  const html = renderDetails(buildNeedle('senate-mi', monitor, data, now));
  assert.match(html, /Model candidate/); assert.match(html, /unknown for these returns/);
  assert.doesNotMatch(html, /40%/);
});

test('pending or failed supporting geographies never become additional race needles', () => {
  const pending = { ...monitor, races: [...monitor.races,
    { target: 'house-ky-06-counties', chamber: 'house', status: 'pending' },
    { target: 'house-aa-01', chamber: 'house', status: 'error' }] };
  assert.deepEqual(needleCatalog(pending, null).map(needle => needle.id), ['house-control', 'senate-control', 'senate-mi']);
  pending.races[0] = { ...pending.races[0], coverage: 'partial' };
  assert.equal(needleCatalog(pending, null).length, 3, 'A real race stays in the catalog when its latest coverage is partial');
});

test('independent seat convolution matches enumerated outcomes, including fixed seats and certainty', () => {
  assert.deepEqual(independentSeatDistribution([.5, .5]), [.25, .5, .25]);
  assert.deepEqual(independentSeatDistribution([0, 1], 2), [0, 0, 0, 1, 0]);
  const ps = [.2, .6, .8], expected = [0, 0, 0, 0];
  for (let mask = 0; mask < 8; mask++) {
    let mass = 1, seats = 0;
    ps.forEach((p, i) => { const win = mask & (1 << i); mass *= win ? p : 1 - p; if (win) seats++; });
    expected[seats] += mass;
  }
  independentSeatDistribution(ps).forEach((p, i) => assert.ok(Math.abs(p - expected[i]) < 1e-12));
  for (const p of [NaN, -1, 2]) assert.throws(() => independentSeatDistribution([p]));
});

test('joint outcomes preserve correlation, other-control mass, and majority thresholds', () => {
  const correlated = [race('senate-mi', 'DDRR'), race('senate-oh', 'DDRR')];
  const result = chamberDistribution(correlated, [], 2, { D: 2, R: 2 });
  assert.deepEqual(result.probabilities, { D: .5, R: .5, other: 0 });
  assert.equal(independentSeatDistribution([.5, .5])[2], .25);
  const split = chamberDistribution([race('senate-mi', 'DDRR'), race('senate-oh', 'DRDR')], [], 2, { D: 2, R: 2 });
  assert.deepEqual(split.probabilities, { D: .25, R: .25, other: .5 });
  const other = chamberDistribution([race('senate-mi', 'DO')], [fixed('senate-oh-1', 'R')], 2, { D: 2, R: 2 });
  assert.deepEqual(other.probabilities, { D: 0, R: 0, other: 1 });
  assert.throws(() => chamberDistribution(correlated, [fixed('senate-mi-2', 'D')], 3, { D: 2, R: 2 }), /duplicated/);
  assert.throws(() => chamberDistribution([race('senate-mi', 'D'), race('senate-oh', 'DD')], [], 2, { D: 2, R: 2 }), /Incoherent/);
});

test('race APIs publish calibrated joint marginals, and hide stale or missing forecasts', () => {
  const data = run(); data.races[0].margins = [-2, 0, 2, 4];
  validateForecastRun(data, now);
  assert.equal(needleCatalog(monitor, null).length, 3, 'Two chamber needles, one race, no supporting views');
  const needle = buildNeedle('senate-mi', monitor, data, now);
  assert.deepEqual(needle.probabilities, { D: .5, R: .5, other: 0 });
  assert.equal(needle.projectedMargin, 1);
  assert.deepEqual(needle.marginInterval, [-2, 4]);
  assert.equal(buildNeedle('senate-mi', monitor, data, now + 16 * 60_000).probabilities, null);
  assert.equal(buildNeedle('senate-mi', monitor, null, now).status, 'uncalibrated');
  assert.equal(buildNeedle('missing', monitor, data, now), null);
  const chamber = buildNeedle('house-control', monitor, data, now);
  assert.equal(chamber.missingSeats, 416); assert.equal(chamber.probabilities, null);
  assert.equal(chamber.ledger.inventoryComplete, true);
});

test('complete chamber model inputs merge sourced holdovers and declarations without overriding them', () => {
  const data = run();
  data.assumptions = ['Synthetic unresolved-seat outcomes for testing only.'];
  data.fixedSeats.senate = buildChamberLedger('senate').seats.filter(seat => seat.status === 'unresolved' && seat.id !== 'senate-mi-2')
    .map((seat, i) => ({ ...fixed(seat.id, i < 14 ? 'D' : 'R'), basis: 'assumption' }));
  validateForecastRun(data, now);
  let needle = buildNeedle('senate-control', monitor, data, now);
  assert.deepEqual(needle.probabilities, { D: .5, R: .5, other: 0 });
  assert.equal(needle.fixedSeats.length, 99);
  const otherTie = structuredClone(data); otherTie.senateTieBreaker = 'D';
  needle = buildNeedle('senate-control', monitor, otherTie, now);
  assert.equal(needle.probabilities, null); assert.equal(needle.conflicts[0].seatId, 'senate-tie-breaker');
  data.fixedSeats.house = buildChamberLedger('house').seats.filter(seat => seat.status === 'unresolved')
    .map((seat, i) => ({ ...fixed(seat.id, i < 205 ? 'D' : 'R'), basis: 'assumption' }));
  validateForecastRun(data, now);
  assert.deepEqual(buildNeedle('house-control', monitor, data, now).probabilities, { D: 1, R: 0, other: 0 });
});

test('publication rejects ambiguous seats, invalid probabilities, unsafe provenance and incoherent runs', () => {
  for (const mutate of [
    r => r.races.push({ ...r.races[0] }),
    r => r.races[0].seatId = 'senate-oh-1',
    r => r.races[0].outcomes = 'DR?D',
    r => r.races[0].margins = [1],
    r => r.fixedSeats.senate.push(fixed('senate-mi-2', 'R')),
    r => r.fixedSeats.house.push({ ...fixed('house-mi-07', 'R'), basis: 'not-up' }),
    r => r.fixedSeats.senate.push({ id: 'senate-oh-1', caucus: 'D' }),
    r => r.fixedSeats.senate.push(...[1, 2, 3].map(n => fixed(`senate-oh-${n}`, 'D'))),
    r => r.calibrationUrl = 'javascript:alert(1)',
    r => r.asOf = new Date(now + 120_000).toISOString(),
    r => r.races[0].chamber = 'house',
  ]) { const data = run(); mutate(data); assert.throws(() => validateForecastRun(data, now)); }
});

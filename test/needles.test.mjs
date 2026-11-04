import test from 'node:test';
import assert from 'node:assert/strict';
import { independentSeatDistribution, chamberDistribution } from '../src/needle-model.ts';
import { buildNeedle, needleCatalog, validateForecastRun } from '../src/needles.ts';
import houseSeats from '../src/data/house-seats.json' with { type: 'json' };
import senateSeats from '../src/data/senate-seats.json' with { type: 'json' };

const now = Date.parse('2026-11-04T01:00:00Z');
const race = (id, outcomes, chamber = 'senate') => ({ id, name: id, chamber, seatId: `${id}-${id === 'senate-mi' ? 2 : 3}`, outcomes });
const fixed = (id, caucus) => ({ id, caucus, sourceUrl: 'https://example.org/baseline', basis: 'declared' });
const run = () => ({ electionDate: '2026-11-03', asOf: new Date(now).toISOString(), modelVersion: 'test-1',
  calibrationUrl: 'https://example.org/calibration', assumptions: [],
  races: [race('senate-mi', 'DDRR')], fixedSeats: { house: [], senate: [] }, senateTieBreaker: 'R' });
const monitor = { races: [{ target: 'senate-mi', name: 'Michigan', chamber: 'senate', status: 'reporting', sourceUrl: 'https://example.org/results' },
  { target: 'senate-mi-detroit', chamber: 'senate' }, { target: 'senate-ks-johnson', chamber: 'senate' }], completion: [], lastCheckedAt: new Date(now).toISOString() };

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
  assert.equal(chamber.missingSeats, 435); assert.equal(chamber.probabilities, null);
});

test('complete chamber ledgers apply Senate tiebreaker to either caucus', () => {
  const data = run();
  data.fixedSeats.senate = senateSeats.filter(id => id !== 'senate-mi-2')
    .map((id, i) => fixed(id, i < 49 ? 'D' : 'R'));
  validateForecastRun(data, now);
  let needle = buildNeedle('senate-control', monitor, data, now);
  assert.deepEqual(needle.probabilities, { D: 0, R: 1, other: 0 }, '49 fixed Democrats plus a win only reaches 50');
  const otherTie = structuredClone(data); otherTie.senateTieBreaker = 'D';
  needle = buildNeedle('senate-control', monitor, otherTie, now);
  assert.deepEqual(needle.probabilities, { D: .5, R: .5, other: 0 });
  data.fixedSeats.house = houseSeats.map((id, i) => fixed(id, i < 218 ? 'D' : 'R'));
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

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { withOfficialResults } from '../src/live-results.ts';
import { signalFor } from '../public/election-model.js';

const now = Date.parse('2026-11-04T02:00:00Z');
const result = (d = 600, r = 350, other = 50) => ({
  race: 'north-carolina', status: 'reporting', message: 'Official returns',
  candidates: [{ name: 'Roy Cooper', party: 'DEM', votes: d }, { name: 'Michael Whatley', party: 'REP', votes: r }, { name: 'Other', party: 'LIB', votes: other }],
  totalVotes: d + r + other, checkedAt: new Date(now).toISOString(), lastSuccessAt: new Date(now).toISOString(),
  sourceUrl: 'https://er.ncsbe.gov/enr/20261103/data/results_0.txt',
});

test('official votes automatically supply the dashboard margin, including other parties in its denominator', () => {
  const manual = [{ target: 'senate-mi', margin: 5 }, { target: 'senate-nc', margin: 99 }];
  const observations = withOfficialResults(manual, [result()], now);
  assert.equal(observations.find(item => item.target === 'senate-mi').margin, 5);
  const live = observations.find(item => item.target === 'senate-nc');
  assert.equal(live.margin, 25);
  assert.equal(live.totalVotes, 1000);
  assert.equal(live.sourceKind, 'official');
  assert.equal(live.winner, null);
  assert.equal(live.reporting, null);
  assert.equal(live.version, 0);
  assert.equal(manual[1].margin, 99, 'Editor history is not mutated');
});

test('zero setup and missing sources do not create margins or revive manual totals for automatic races', () => {
  assert.deepEqual(withOfficialResults([{ target: 'senate-nc', margin: 99 }], [{ ...result(0, 0, 0), status: 'setup' }], now), []);
  assert.deepEqual(withOfficialResults([], [{ race: 'kansas', status: 'error', message: 'HTTP 403', sourceUrl: 'https://ent.sos.ks.gov/kssos_ent.html' }], now), []);
  assert.deepEqual(withOfficialResults([], [{ ...result(), totalVotes: 999 }], now), []);
});

test('a correction replaces cumulative results and stale retained counts cannot highlight a current signal', () => {
  const correction = withOfficialResults([], [result(450, 500, 50)], now)[0];
  assert.equal(correction.margin, -5);
  const failed = withOfficialResults([], [{ ...result(), status: 'error' }], now)[0];
  assert.equal(failed.totalVotes, 1000);
  assert.equal(failed.sourceStatus, 'stale');
  assert.equal(signalFor({ chamber: 'senate', ranges: [{ min: 0, max: null }] }, failed), null);
  assert.equal(withOfficialResults([], [result()], now + 16 * 60_000)[0].sourceStatus, 'stale');
});

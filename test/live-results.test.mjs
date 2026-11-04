import assert from 'node:assert/strict';
import { test } from 'node:test';
import { withOfficialResults, withGroupResults } from '../src/live-results.ts';
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

test('House races and independent Nebraska margins use all votes and isolate partial coverage', () => {
  const house = { ...result(), target: 'house-oh-01', race: 'house-oh-01', chamber: 'house', sourceKind: 'supplier' };
  assert.equal(withOfficialResults([], [house], now)[0].margin, 25);
  assert.equal(withOfficialResults([], [house], now)[0].sourceKind, 'supplier');
  assert.equal(signalFor({ chamber: 'house' }, withOfficialResults([], [{ ...house, status: 'error' }], now)[0]), null);
  const nebraska = { ...house, target: 'senate-ne', candidates: house.candidates.map(candidate => candidate.party === 'DEM' ? { ...candidate, name: 'Dan Osborn', party: 'IND' } : candidate) };
  assert.equal(withOfficialResults([], [nebraska], now)[0].margin, 25);
  assert.deepEqual(withOfficialResults([], [{ ...house, coverage: 'partial' }], now), []);
  assert.deepEqual(withOfficialResults([], [{ ...house, candidates: [{ name: 'Bad', party: 'DEM', votes: -1 }], totalVotes: -1 }], now), []);
});

test('group guardrails count explicit source declarations rather than current leads', () => {
  const ids = ['house-tx-09', 'house-tx-28', 'house-tx-32', 'house-tx-34', 'house-tx-35'];
  const members = ids.map(target => ({ ...result(350, 600, 50), target, race: target }));
  let group = withGroupResults(members, now).find(result => result.target === 'house-tx-redraw');
  assert.equal(group.gopLeadingSeats, 5);
  assert.equal(group.gopSeats, 0);
  assert.equal(signalFor({ chamber: 'house', group: true, gopBar: 4 }, withOfficialResults([], [group], now)[0]), null);
  group = withGroupResults(members.map((result, i) => ({ ...result, winner: i < 4 ? 'R' : undefined })), now).find(result => result.target === 'house-tx-redraw');
  assert.equal(group.gopSeats, 4);
  assert.equal(signalFor({ chamber: 'house', group: true, gopBar: 4 }, withOfficialResults([], [group], now)[0]), 'riptide');
  group = withGroupResults(members.slice(1), now).find(result => result.target === 'house-tx-redraw');
  assert.equal(group.status, 'unavailable');
  assert.deepEqual(withOfficialResults([], [group], now), []);
  group = withGroupResults(members.map(result => ({ ...result, status: 'setup', totalVotes: 0, candidates: result.candidates.map(candidate => ({ ...candidate, votes: 0 })) })), now).find(result => result.target === 'house-tx-redraw');
  assert.equal(group.status, 'setup');
  assert.deepEqual(withOfficialResults([], [group], now), []);
});

test('SNN calls survive live count changes and outages, preserving separate source provenance', () => {
  const call = { target: 'house-ky-06', status: 'projected', winner: 'D', margin: null,
    reporting: null, sourceUrl: 'https://snoopy-news-network.snoopy-news-network.workers.dev/#night',
    observedAt: new Date(now).toISOString(), body: 'SNN calls KY-06 D', version: 1 };
  const live = { ...result(), target: call.target, race: call.target, sourceKind: 'supplier' };
  for (const snapshot of [live, { ...live, ...result(450, 500, 50) }, { ...live, status: 'error' },
    { ...live, coverage: 'partial' }, { ...live, candidates: [], totalVotes: 0, status: 'setup' }]) {
    const observations = withOfficialResults([call], [snapshot], now);
    assert.equal(observations.length, 1);
    assert.equal(observations[0].winner, 'D');
    assert.equal(observations[0].status, 'projected');
    assert.deepEqual(observations[0].deskCall, call);
  }
  const merged = withOfficialResults([call], [live], now)[0];
  assert.equal(merged.margin, 25);
  assert.equal(merged.sourceKind, 'supplier');
  assert.equal(merged.sourceUrl, live.sourceUrl);
  assert.equal(merged.deskCall.sourceUrl, call.sourceUrl);
  assert.equal(call.margin, null);
  const retracted = withOfficialResults([{ ...call, status: 'awaiting', winner: null }], [live], now)[0];
  assert.equal(retracted.winner, null);
  assert.equal(retracted.deskCall, undefined);
});

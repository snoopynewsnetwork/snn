import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildChamberLedger, parseLedgerFeed, chamberInputs } from '../src/chamber-ledger.ts';
import { buildNeedle } from '../src/needles.ts';

const checkedAt = '2026-11-04T01:00:00Z';
const read = chamber => JSON.parse(readFileSync(new URL(`fixtures/ledger/${chamber}.json`, import.meta.url), 'utf8'));
const updates = chamber => parseLedgerFeed(chamber, JSON.stringify(read(chamber)), checkedAt, '/api/live-monitor/completion-cnn/snapshots/1');
const monitor = { races: [{ target: 'house-fl-05', chamber: 'house', name: 'Florida 5' }], completion: [], lastCheckedAt: checkedAt };

test('complete incoming-Congress inventory separates 65 Senate holdovers from 470 elections', () => {
  const house = buildChamberLedger('house'), senate = buildChamberLedger('senate');
  assert.equal(house.seats.length, 435); assert.equal(senate.seats.length, 100);
  assert.equal(new Set([...house.seats, ...senate.seats].map(seat => seat.id)).size, 535);
  assert.equal(house.inventoryComplete, true); assert.equal(senate.inventoryComplete, true);
  assert.equal(house.notUpSeats, 0); assert.equal(senate.notUpSeats, 65);
  assert.deepEqual(senate.seats.filter(seat => seat.status === 'not-up').reduce((counts, seat) => (counts[seat.caucus]++, counts), { D: 0, R: 0 }), { D: 34, R: 31 });
  for (const id of ['senate-me-1', 'senate-vt-1']) {
    const seat = senate.seats.find(seat => seat.id === id);
    assert.equal(seat.party, 'I'); assert.equal(seat.caucus, 'D'); assert.equal(seat.caucusSourceId, 'independent-caucuses');
  }
  assert.equal(senate.seats.find(seat => seat.id === 'senate-fl-3').status, 'unresolved');
  assert.equal(senate.seats.find(seat => seat.id === 'senate-oh-3').status, 'unresolved');
  assert.equal(senate.senateTieBreaker.caucus, 'R');
  assert.equal(house.seats.filter(seat => seat.election?.key === '2026-HQ-TX-18').length, 0);
  assert.equal(house.seats.filter(seat => seat.id === 'house-tx-18').length, 1);
});

test('all 470 pinned election records accept only explicit attributed projections, including an uncontested zero-vote call', () => {
  const house = updates('house'), senate = updates('senate');
  assert.equal(house.length, 435); assert.equal(senate.length, 35);
  assert.ok([...house, ...senate].every(seat => seat.status !== 'review'));
  assert.equal(house.filter(seat => seat.status === 'declared').length, 19);
  assert.equal(senate.filter(seat => seat.status === 'declared').length, 2);
  assert.ok(senate.find(seat => seat.id === 'senate-va-2').unallocatedVotes > 0, 'Explicit call does not turn unallocated votes into candidate votes');
  const uncontested = house.find(seat => seat.id === 'house-fl-10');
  assert.equal(uncontested.winner, 'Maxwell Frost'); assert.equal(uncontested.caucus, 'D');
  assert.equal(read('house').find(row => row.ecKey === '2026-HG-FL-10').totalVote, 0);
  const ledger = buildChamberLedger('house', house);
  const declared = ledger.seats.find(seat => seat.id === 'house-fl-05');
  assert.equal(declared.declarationKind, 'newsroom-projection'); assert.equal(declared.sourceKind, 'supplier');
  assert.equal(declared.evidenceUrl, '/api/live-monitor/completion-cnn/snapshots/1');
  assert.equal(ledger.seats.find(seat => seat.id === 'house-tx-18').status, 'unresolved');
});

test('retractions clear projections; corrections replace outcomes; leads alone never become declarations', () => {
  const rows = read('house'), row = rows.find(row => row.ecKey === '2026-HG-FL-5');
  row.candidates.forEach(candidate => candidate.winner = false);
  const cleared = parseLedgerFeed('house', JSON.stringify(rows), checkedAt);
  let ledger = buildChamberLedger('house', cleared);
  assert.equal(ledger.seats.find(seat => seat.id === 'house-fl-05').status, 'unresolved');
  assert.equal(ledger.seats.find(seat => seat.id === 'house-fl-05').caucus, null);
  row.candidates.find(candidate => candidate.majorParty === 'DEM').winner = true;
  ledger = buildChamberLedger('house', parseLedgerFeed('house', JSON.stringify(rows), checkedAt));
  assert.equal(ledger.seats.find(seat => seat.id === 'house-fl-05').caucus, 'D');
  assert.equal(ledger.seats.find(seat => seat.id === 'house-fl-05').holder, null);
});

test('full-contest validation isolates candidate, identity, embargo, total, and duplicate failures', () => {
  for (const mutate of [
    row => row.candidates[0].fullName = 'Wrong candidate', row => row.totalVote--,
    row => row.externalKey = 'test-key', row => row.raceEmbargo.votesReleased = false,
    row => row.raceEmbargo.assignedPollsClose++, row => row.extractedAt = '2024-11-05T00:00:00Z',
    row => row.extractedAt = '2026-11-05T00:00:00Z', row => row.stateAbbreviation = 'GA',
    row => row.candidates.forEach(candidate => candidate.winner = true),
  ]) {
    const rows = read('house'); mutate(rows.find(row => row.ecKey === '2026-HG-FL-5'));
    const result = parseLedgerFeed('house', JSON.stringify(rows), checkedAt);
    assert.equal(result.find(seat => seat.id === 'house-fl-05').status, 'review');
    assert.equal(result.find(seat => seat.id === 'house-fl-10').status, 'declared');
  }
  const rows = read('senate'); rows.push(rows[0]);
  assert.equal(parseLedgerFeed('senate', JSON.stringify(rows), checkedAt).filter(seat => seat.status === 'review').length, 1);
  assert.ok(parseLedgerFeed('house', 'invalid', checkedAt).every(seat => seat.status === 'review'));
});

test('official declarations can resolve absent prior timestamps and never retain a misleading party/holder', () => {
  const review = { id: 'house-fl-05', status: 'review', caucus: null, winner: null, party: null, sourceUpdated: null,
    checkedAt, sourceUrl: 'https://example.org/failure' };
  const official = { target: 'house-fl-05', status: 'reporting', winner: 'D', coverage: 'complete', sourceKind: 'official',
    sourceUrl: 'https://official.example/results', lastSuccessAt: checkedAt, candidates: [{ name: 'Official winner', party: 'DEM', votes: 1 }] };
  const seat = buildChamberLedger('house', [review], [official]).seats.find(seat => seat.id === 'house-fl-05');
  assert.equal(seat.status, 'declared'); assert.equal(seat.caucus, 'D'); assert.equal(seat.party, 'DEM');
  assert.equal(seat.winner, 'Official winner'); assert.equal(seat.holder, null); assert.equal(seat.sourceKind, 'official');
  const disagreement = buildChamberLedger('house', updates('house'), [official]).seats.find(seat => seat.id === 'house-fl-05');
  assert.equal(disagreement.status, 'review'); assert.equal(disagreement.caucus, null);
});

test('forecast/ledger disagreement blocks odds instead of silently overwriting either source', () => {
  const run = { electionDate: '2026-11-03', modelVersion: 'test', asOf: checkedAt, calibrationUrl: 'https://example.org/calibration',
    assumptions: [], races: [{ id: 'house-fl-05', name: 'Florida 5', chamber: 'house', seatId: 'house-fl-05', outcomes: 'DDRR' }],
    fixedSeats: { house: [], senate: [] }, senateTieBreaker: 'R' };
  const inputs = chamberInputs('house', run);
  assert.equal(inputs.conflicts[0].seatId, 'house-fl-05');
  let needle = buildNeedle('house-fl-05', monitor, run, Date.parse(checkedAt));
  assert.equal(needle.probabilities, null); assert.equal(needle.status, 'unavailable'); assert.ok(needle.ledgerConflict.sourceUrl);
  needle = buildNeedle('house-control', monitor, run, Date.parse(checkedAt));
  assert.equal(needle.probabilities, null); assert.ok(needle.conflicts.length);
  const retractedRows = read('house'); retractedRows.find(row => row.ecKey === '2026-HG-FL-5').candidates.forEach(candidate => candidate.winner = false);
  const next = { ...monitor, ledgerUpdates: parseLedgerFeed('house', JSON.stringify(retractedRows), checkedAt) };
  needle = buildNeedle('house-fl-05', next, run, Date.parse(checkedAt));
  assert.equal(needle.status, 'ready'); assert.deepEqual(needle.probabilities, { D: .5, R: .5, other: 0 });
});

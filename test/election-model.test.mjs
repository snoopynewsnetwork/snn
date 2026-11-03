import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { signalFor, easternMinutes, closeMinutes, timeLabel } from '../public/election-model.js';
const guide = JSON.parse(await readFile(new URL('../public/election-guide.json', import.meta.url), 'utf8'));
const result = (margin, extra = {}) => ({ status: 'partial', margin, winner: null, gopSeats: null, ...extra });
const senate = code => guide.senate.find(item => item.code === code);
const house = code => guide.house.find(item => item.code === code);

test('Senate sheet bands preserve all four scenarios and leave literal gaps unresolved', () => {
  const cases = {
    FL: [-10, -4, 0, .01], GA: [4.99, 5, 11, 15], SC: [-9, 0, 1, 5], NC: [5.99, 6, 13, 17],
    OH: [-2, 6, 7, 11], ME: [-1, 0, 5, 9], NH: [3.99, 4, 12, 16], TX: [-5, 4, 5, 9],
    MI: [-.01, 0, 8, 12], KS: [-7, 3, 4, 8], MS: [-14, -3, 0, 1],
    IA: [-5, 2, 3, 7], NE: [-5, 0, 1, 5], MN: [.99, 1, 13, 17],
  };
  for (const [code, margins] of Object.entries(cases)) {
    margins.forEach((margin, index) => assert.equal(signalFor(senate(code), result(margin)), guide.bands[index].id, `${code} ${margin}`));
    assert.equal(signalFor(senate(code), null), null);
    assert.equal(signalFor(senate(code), result(10, { status: 'awaiting' })), null);
  }
  for (const [code, margin] of [['FL',-9.5],['ME',-.5],['NC',12.5],['MI',7.5],['NE',.5]])
    assert.equal(signalFor(senate(code), result(margin)), null, `${code} gap ${margin}`);
  assert.equal(signalFor(senate('MI'), result(null, { status: 'projected', winner: 'D' })), null, 'A winner alone cannot establish a margin band');
});

test('House margin guardrails and redraw groups do not turn ordinary GOP holds into wave signals', () => {
  assert.equal(signalFor(house('KY-06'), result(-10)), 'riptide');
  assert.equal(signalFor(house('KY-06'), result(-9.99)), null);
  assert.equal(signalFor(house('KY-06'), result(.1)), 'wave');
  assert.equal(signalFor(house('IN-05'), result(-14)), null);
  assert.equal(signalFor(house('IN-05'), result(-15)), 'riptide');
  assert.equal(signalFor(house('VA-07'), result(-.1)), 'riptide');
  assert.equal(signalFor(house('VA-07'), result(4)), null);
  assert.equal(signalFor(house('VA-02'), result(-4)), null);
  assert.equal(signalFor(house('VA-02'), result(4)), 'tide');
  assert.equal(signalFor(house('FL-14'), result(-1)), 'riptide');
  assert.equal(signalFor(house('FL-14'), result(1)), 'tide');
  assert.equal(signalFor(house('VA-05'), result(null, { status: 'projected', winner: 'D' })), 'tsunami');
  assert.equal(signalFor(house('MT-01'), result(10)), null, 'Later toss-ups do not imply a scenario');
  assert.equal(signalFor(house('TX-REDRAW'), result(null, { gopSeats: 3 })), null);
  assert.equal(signalFor(house('TX-REDRAW'), result(null, { gopSeats: 4 })), 'riptide');
  assert.equal(signalFor(house('PA-07-10'), result(null, { gopSeats: 2 })), 'riptide');
});

test('Election date and overnight checkpoints use Eastern time across the local timezone', () => {
  assert.equal(easternMinutes(new Date('2026-11-04T00:00:00Z')), 19 * 60);
  assert.equal(easternMinutes(new Date('2026-11-04T08:00:00Z')), 27 * 60);
  assert.ok(easternMinutes(new Date('2026-11-02T23:00:00Z')) < 0);
  assert.equal(closeMinutes('19:30'), 1170);
  assert.equal(timeLabel('27:00'), '3am Wed');
  assert.equal(timeLabel('19:30'), '7:30pm');
});

test('Guide IDs are unique and sheet coverage is complete', () => {
  const items = [...guide.senate, ...guide.house, ...guide.cues];
  assert.equal(new Set(items.map(item => item.id)).size, items.length);
  assert.equal(guide.senate.length, 14);
  assert.equal(guide.house.length, 51);
  assert.equal(guide.cues.length, 13);
});

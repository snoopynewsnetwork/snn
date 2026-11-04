import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { countyTotal, countyMargin, countyScenario } from '../public/ky-06-model.js';

const baseline = JSON.parse(await readFile(new URL('../public/ky-06-counties.json', import.meta.url), 'utf8'));
const certifiedPage = await readFile(new URL('./fixtures/ky-06-2024-certified.txt', import.meta.url), 'utf8');
const sum = (rows, key) => rows.reduce((total, row) => total + row[key], 0);
const close = (actual, expected, tolerance = 1e-8) => assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} != ${expected}`);

test('all 16 KY-06 county vectors match the amended certification page and district controls', () => {
  assert.match(certifiedPage, /6th Congressional District/);
  assert.match(certifiedPage, /BARR\s+CRAVENS/);
  const source = [...certifiedPage.matchAll(/^\s+([A-Za-z]+)\s+([\d,]+)\s+([\d,]+)\s*$/gm)]
    .map(([, name, r, d]) => ({ name, r: Number(r.replaceAll(',', '')), d: Number(d.replaceAll(',', '')) }));
  assert.equal(source.length, 16);
  assert.deepEqual(baseline.counties.map(({ name, r, d }) => ({ name, r, d })), source);
  assert.equal(new Set(source.map(c => c.name)).size, 16);
  assert.equal(sum(source, 'r'), 222293);
  assert.equal(sum(source, 'd'), 130345);
  assert.deepEqual(baseline.totals, { r: 222293, d: 130345 });
  assert.match(certifiedPage, /Total Votes\s+222,293\s+130,345/);
  assert.deepEqual(baseline.counties.filter(c => c.partial).map(c => c.name), ['Anderson', 'Bath']);
  assert.equal(baseline.counties.find(c => c.name === 'Fayette').d, 73334, 'Use the amended Fayette count, not the original 70,525');
  assert.equal(baseline.source.page, 16);
});

test('2024 replay reproduces every county vote exactly', () => {
  const scenario = countyScenario(baseline.counties, { margin: countyMargin(baseline.totals) });
  assert.equal(scenario.total, 352638);
  assert.equal(scenario.r, 222293);
  assert.equal(scenario.d, 130345);
  for (const [i, row] of scenario.counties.entries()) {
    assert.equal(row.r, baseline.counties[i].r);
    assert.equal(row.d, baseline.counties[i].d);
  }
  close(scenario.shareShift, 0);
});

test('tie needs a 13.04 point D share shift and preserves all county volumes', () => {
  const scenario = countyScenario(baseline.counties, { margin: 0 });
  assert.equal(scenario.r, 176319);
  assert.equal(scenario.d, 176319);
  close(scenario.shareShift, 100 * 45974 / 352638);
  assert.equal(scenario.margin, 0);
  const fayette = scenario.counties.find(c => c.name === 'Fayette');
  close(100 * fayette.d / countyTotal(fayette), 64.26, .01);
  scenario.counties.forEach((c, i) => assert.equal(countyTotal(c), countyTotal(baseline.counties[i])));
});

test('preset and extreme scenarios bound shares, reconcile whole votes and meet the target within one vote', () => {
  for (const margin of [-100, -90, -10, 0, 5, 80, 100]) {
    for (const turnout of [10, 65, 73.7, 100, 150]) {
      const scenario = countyScenario(baseline.counties, { margin, turnout });
      assert.equal(scenario.total, Math.round(352638 * turnout / 100));
      assert.equal(sum(scenario.counties, 'r'), scenario.r);
      assert.equal(sum(scenario.counties, 'd'), scenario.d);
      close(scenario.margin, margin, 100 / scenario.total + 1e-8);
      scenario.counties.forEach(c => {
        assert.ok(Number.isSafeInteger(c.r) && c.r >= 0);
        assert.ok(Number.isSafeInteger(c.d) && c.d >= 0);
      });
    }
  }
});

test('turnout scaling preserves county mix within one vote and does not invent a preference change', () => {
  const scenario = countyScenario(baseline.counties, { margin: countyMargin(baseline.totals), turnout: 65 });
  scenario.counties.forEach((c, i) => close(countyTotal(c), .65 * countyTotal(baseline.counties[i]), 1));
  close(scenario.shareShift, 0, .001);
});

test('unsupported and missing assumptions fail validation', () => {
  for (const input of [{ margin: NaN }, { margin: Infinity }, { margin: 101 }, { margin: -101 }, { margin: 0, turnout: 0 }, { margin: 0, turnout: 151 }, { margin: '0' }])
    assert.throws(() => countyScenario(baseline.counties, input));
  assert.throws(() => countyScenario([], { margin: 0 }));
  assert.throws(() => countyScenario([{ r: 0, d: 0 }], { margin: 0 }));
});

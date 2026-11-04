import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { createHash } from 'node:crypto';
import { test } from 'node:test';
import { parseCnnKy06Counties, ky06CountyAdapter } from '../src/adapters/ky06-counties.ts';
import { countyForecast } from '../public/ky-06-model.js';
import { renderKy06Forecast } from '../public/ky-06.js';

const fixture = name => gunzipSync(readFileSync(new URL(`./fixtures/${name}`, import.meta.url))).toString();
const countyBody = fixture('cnn-ky06-counties.json.gz'), raceBody = fixture('cnn-ky06-race.json.gz');
const baseline = JSON.parse(readFileSync(new URL('../public/ky-06-counties.json', import.meta.url)));
const now = Date.parse('2026-11-04T01:41:00Z');
const snapshot = () => ({ ...parseCnnKy06Counties(countyBody, raceBody), lastSuccessAt: new Date(now).toISOString() });
const sum = (rows, key) => rows.reduce((n, row) => n + row[key], 0);

test('actual CNN county and district originals reconcile every candidate, with Fayette included', () => {
  const result = snapshot();
  assert.equal(result.totalVotes, 181845);
  assert.equal(result.counties.length, 16);
  assert.equal(result.counties.find(c => c.name === 'Fayette').totalVotes, 101751);
  assert.equal(result.counties.find(c => c.name === 'Anderson').estimatedVotePercent, 82);
  assert.equal(result.counties.find(c => c.name === 'Anderson').sourceReporting, null);
  assert.equal(result.estimatedVotePercent, 59);
  assert.equal(result.winner, undefined);
  for (const c of result.candidates)
    assert.equal(result.counties.reduce((n, county) => n + county.candidates.find(x => x.name === c.name && x.party === c.party).votes, 0), c.votes);
  const manifest = JSON.parse(readFileSync(new URL('./fixtures/ky06-prediction-sources.json', import.meta.url)));
  for (const source of manifest.sources)
    assert.equal(createHash('sha256').update(fixture(source.fixture)).digest('hex'), source.sha256);
  assert.match(fixture('ky06-official-blocked.html.gz'), /Acceptable Use Policy/);
  assert.match(fixture('ky06-wkyt.html.gz'), /2026 General Election/);
});

test('CNN rejects changed county/race identity, candidate configuration, early votes and unreconciled snapshots', () => {
  for (const mutate of [
    d => d.pop(), d => d[1] = d[0], d => d[0].countyFipsCode = '21001',
    d => d[0].ecKey = '2024-HG-KY-6', d => d[0].electionType = 'P',
    d => d[0].externalKey = 'test-key', d => d[0].jurisdictionCode = 5,
    d => d[0].resourceType = 'state-races', d => d[0].extractedAt = '2026-11-02T12:00:00Z',
    d => d[0].candidates.pop(), d => d[0].candidates[0].voteNum = -1,
    d => d[0].candidates[0].majorParty = 'DEM', d => d[0].candidates[0].candidateId = 1,
    d => d[0].candidates[1] = d[0].candidates[0], d => d[0].totalVote++,
    d => { d[0].candidates[0].voteNum++; d[0].totalVote++; },
  ]) {
    const data = JSON.parse(countyBody); mutate(data);
    assert.throws(() => parseCnnKy06Counties(JSON.stringify(data), raceBody));
  }
  const early = JSON.parse(raceBody); early.raceEmbargo.votesReleased = false;
  assert.throws(() => parseCnnKy06Counties(countyBody, JSON.stringify(early)));
  assert.throws(() => parseCnnKy06Counties(countyBody, undefined));
});

test('CNN is preferred; civicAPI remains a separately attributed fallback', () => {
  const civic = fixture('civic-ky06-counties.json.gz');
  const inputs = { 'cnn-ky06-counties': countyBody, 'cnn-2026-HG-KY-6': raceBody, 'civic-ky06-counties': civic };
  const preferred = ky06CountyAdapter.parse(inputs)['house-ky-06-counties'];
  assert.equal(preferred.sourceId, 'cnn-ky06-counties');
  assert.equal(preferred.totalVotes, 181845);
  const fallback = ky06CountyAdapter.parse({ ...inputs, 'cnn-ky06-counties': '[]' })['house-ky-06-counties'];
  assert.equal(fallback.sourceId, 'civic-ky06-counties');
  assert.equal(fallback.totalVotes, 4029);
  assert.equal(fallback.estimatedVotePercent, undefined);
  assert.throws(() => ky06CountyAdapter.parse({}));
});

test('live prediction preserves counted votes, estimates only additional votes and reconciles county outcomes', () => {
  const result = snapshot(), estimate = countyForecast(baseline.counties, result, now);
  assert.equal(estimate.status, 'estimate');
  assert.equal(estimate.reportingCount, 9);
  assert.equal(estimate.countedD, 100685);
  assert.equal(estimate.countedR, 74093);
  assert.equal(estimate.countedOther, 7067);
  assert.equal(estimate.r, sum(estimate.counties, 'r'));
  assert.equal(estimate.d, sum(estimate.counties, 'd'));
  assert.equal(estimate.remaining, sum(estimate.counties, 'remaining'));
  assert.equal(estimate.total, estimate.countedR + estimate.countedD + estimate.remaining);
  assert.ok(estimate.low <= estimate.margin && estimate.margin <= estimate.high);
  assert.ok(estimate.shift > 0);
  for (const county of estimate.counties) {
    assert.ok(Number.isSafeInteger(county.r) && county.r >= county.countedR);
    assert.ok(Number.isSafeInteger(county.d) && county.d >= county.countedD);
    assert.equal(county.r + county.d, county.countedR + county.countedD + county.remaining);
  }
  const anderson = estimate.counties.find(c => c.name === 'Anderson');
  assert.equal(anderson.remaining, Math.round((4386 + 2735) / .82) - 4386 - 2735);
  assert.equal(estimate.counties.find(c => c.name === 'Madison').volumeSource, 'historical-weight');
  assert.equal(estimate.probability, undefined);
  assert.equal(estimate.winner, undefined);
});

test('stale, failed, sparse, missing or mismatched inputs withhold the prediction', () => {
  const result = snapshot();
  for (const patch of [{ status: 'unavailable' }, { coverage: 'partial' }, { estimatedVotePercent: 0 },
    { estimatedVotePercent: 101 }, { estimatedVotePercent: null }, { totalVotes: result.totalVotes + 1 },
    { lastSuccessAt: '2026-11-04T00:00:00Z' }, { lastSuccessAt: '2026-11-04T02:00:00Z' },
    { counties: result.counties.slice(1) }])
    assert.equal(countyForecast(baseline.counties, { ...result, ...patch }, now).status, 'unavailable');
  assert.equal(countyForecast(baseline.counties, { ...result, ...ky06CountyAdapter.parse({ 'civic-ky06-counties': fixture('civic-ky06-counties.json.gz') })['house-ky-06-counties'] }, now).status, 'unavailable');
  const missing = structuredClone(result); missing.counties[0].candidates[0].votes = -1;
  assert.equal(countyForecast(baseline.counties, missing, now).status, 'unavailable');
});

test('matched geography removes reporting-mix bias; 100% estimates do not create a call', () => {
  // A synthetic replay: every county reports its historical counts. With zero
  // additional volume, the outcome must be those exact counts, even at 100%.
  const result = { status: 'reporting', coverage: 'complete', estimatedVotePercent: 100, lastSuccessAt: new Date(now).toISOString(),
    totalVotes: 352638, candidates: [{ name: 'R', party: 'REP', votes: 222293 }, { name: 'D', party: 'DEM', votes: 130345 }],
    counties: baseline.counties.map(c => ({ name: c.name, totalVotes: c.r + c.d, estimatedVotePercent: 100,
      candidates: [{ name: 'R', party: 'REP', votes: c.r }, { name: 'D', party: 'DEM', votes: c.d }] })) };
  const estimate = countyForecast(baseline.counties, result, now);
  assert.equal(estimate.shift, 0);
  assert.equal(estimate.remaining, 0);
  assert.equal(estimate.r, 222293);
  assert.equal(estimate.d, 130345);
  assert.equal(estimate.low, estimate.high);
  assert.equal(estimate.winner, undefined);
  // Remove the large Democratic county; a reporting-only aggregate would look
  // much more Republican, but the matched-county share shift must remain zero.
  const f = result.counties.find(c => c.name === 'Fayette');
  result.candidates.forEach(c => c.votes -= f.candidates.find(x => x.party === c.party).votes);
  result.totalVotes -= f.totalVotes; f.totalVotes = 0; f.candidates.forEach(c => { c.votes = 0; }); f.estimatedVotePercent = 0;
  result.estimatedVotePercent = 100 * result.totalVotes / 352638;
  const partial = countyForecast(baseline.counties, result, now);
  assert.equal(partial.shift, 0);
  assert.equal(partial.r, 222293);
  assert.equal(partial.d, 130345);
});

test('prediction markup labels the model, source and assumptions and suppresses stale numbers', () => {
  const result = { ...snapshot(), sourceUrl: 'https://politics.api.cnn.io/results/county-races/2026-HG-KY-6.json', sourceName: 'CNN county returns' };
  const markup = renderKy06Forecast(baseline.counties, result, now);
  assert.match(markup, /County-adjusted estimate/);
  assert.match(markup, /not a confidence interval/);
  assert.match(markup, /CNN county returns/);
  assert.match(markup, /manual scenarios below do not control this prediction/);
  assert.match(markup, /actual ballots remaining are unknown/);
  const stale = renderKy06Forecast(baseline.counties, { ...result, status: 'unavailable' }, now);
  assert.match(stale, /waiting/);
  assert.doesNotMatch(stale, /Estimated final|Sensitivity range/);
});

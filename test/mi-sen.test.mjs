import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { test } from 'node:test';
import { parseMiCounties } from '../src/adapters/mi-counties.ts';
import { miCountyModel, twoPartyMargin } from '../public/mi-sen-model.js';
import { renderMiSummary, miCsv } from '../public/mi-sen.js';

const baseline = JSON.parse(readFileSync(new URL('../public/mi-sen-counties.json', import.meta.url)));
const body = gunzipSync(readFileSync(new URL('./fixtures/cnn-mi-counties.json.gz', import.meta.url))).toString();
const now = Date.parse('2026-11-04T02:34:00Z');
const result = () => ({ ...parseMiCounties(body), lastSuccessAt: new Date(now).toISOString(), sourceUrl: 'https://politics.api.cnn.io/results/county-races/2026-SG-MI.json' });

test('all 83 historical county rows match retained source extract and official statewide totals', () => {
  const rows = readFileSync(new URL('./fixtures/mi-sen-2024-counties.csv', import.meta.url), 'utf8').trim().split(/\r?\n/).slice(1).map(line => {
    const [name,fips,r,d,other] = line.split(','); return { name,fips,r:+r,d:+d,other:+other };
  });
  assert.deepEqual(baseline.counties, rows);
  assert.equal(rows.length, 83);
  assert.equal(new Set(rows.map(c => c.fips)).size, 83);
  for (const key of ['r','d','other']) assert.equal(rows.reduce((sum,c) => sum+c[key],0),baseline.totals[key]);
  assert.deepEqual(baseline.totals, { r:2693680, d:2712686, other:170821 });
  assert.equal(baseline.totals.d-baseline.totals.r,19006);
});

test('CNN county snapshot excludes 43 overlapping Wayne municipalities and preserves every candidate', () => {
  const parsed = result();
  assert.equal(parsed.counties.length,83);
  assert.equal(parsed.totalVotes,818619);
  assert.equal(parsed.counties.find(c=>c.fips==='26163').totalVotes,2699);
  const all = JSON.parse(body);
  assert.equal(all.length,126);
  assert.equal(all.reduce((s,c)=>s+c.totalVote,0)-parsed.totalVotes,2699,'Wayne subcounty sum must not be added twice');
  for (const c of parsed.candidates) assert.equal(parsed.counties.reduce((s,row)=>s+row.candidates.find(v=>v.name===c.name).votes,0),c.votes);
  assert.equal(parsed.winner,undefined);
  assert.equal(parsed.estimatedVotePercent,undefined);
});

test('county parser rejects missing, duplicate, foreign, stale-identity and invalid candidate rows', () => {
  for (const mutate of [
    x=>x.splice(0,1), x=>x.push(x[0]), x=>x[0].countyFipsCode='26099', x=>x[0].countyName='Other',
    x=>x[0].ecKey='2024-SG-MI', x=>x[0].externalKey='test-key', x=>x[0].contestType='HG', x=>x[0].electionType='P',
    x=>x[0].extractedAt='2026-11-02T01:00:00Z', x=>x[0].candidates.pop(), x=>x[0].candidates[0].candidateId=1,
    x=>x[0].candidates[0].majorParty='REP', x=>x[0].candidates[0].voteNum=-1,
    x=>x[0].candidates[0].voteNum=.5, x=>x[0].candidates[0].voteNum='0', x=>x[0].totalVote=12,
    x=>x.find(c=>c.totalVote>0).voteTimestamp='2026-11-03T12:00:00Z',
    x=>x.find(c=>c.countyFipsCode.length===8).countyFipsCode='99999999',
  ]) { const rows=JSON.parse(body); mutate(rows); assert.throws(()=>parseMiCounties(JSON.stringify(rows))); }
});

test('matched county weights remove changing county composition and handle zero returns without invented swings', () => {
  const b={counties:[{name:'A',fips:'1',d:800,r:200},{name:'B',fips:'2',d:200,r:800}]};
  const county=(fips,d,r)=>({fips,candidates:[{party:'DEM',votes:d},{party:'REP',votes:r}],totalVotes:d+r});
  const input={status:'reporting',coverage:'complete',lastSuccessAt:new Date(now).toISOString(),counties:[county('1',8000,2000),county('2',200,800)],totalVotes:11000,candidates:[{party:'DEM',votes:8200},{party:'REP',votes:2800}]};
  const model=miCountyModel(b,input,{},now);
  assert.ok(Math.abs(model.matchedSwing)<1e-12,'A statewide raw margin change comes entirely from county mix');
  assert.ok(model.margin>49);
  const m=miCountyModel(baseline,result(),{},now);
  assert.ok(m.missing.length>0);
  assert.equal(m.missing[0].swing,null);
  assert.equal(m.missing[0].margin26,null);
});

test('supplier estimates and historical fallback reconcile whole votes without subtracting other candidates', () => {
  const m=miCountyModel(baseline,result(),{},now);
  const oakland=m.rows.find(c=>c.name==='Oakland');
  assert.equal(oakland.volumeSource,'CNN county estimate');
  assert.equal(oakland.assumedTotal,Math.round(oakland.counted/(oakland.supplierPercent/100)));
  const missing=m.missing[0];
  assert.equal(missing.assumedTotal,Math.round(missing.baselineTotal*.8));
  assert.equal(m.rows.reduce((sum,c)=>sum+c.remaining,0),m.remaining);
  assert.equal(m.rows.reduce((sum,c)=>sum+c.finalD,0),m.finalD);
  assert.equal(m.rows.reduce((sum,c)=>sum+c.finalR,0),m.finalR);
  assert.equal(m.finalD+m.finalR,m.d+m.r+m.remaining);
  assert.equal(m.finalMargin,twoPartyMargin(m.finalD,m.finalR));
  const low=miCountyModel(baseline,result(),{turnout:10,volume:'historical',swing:false},now);
  assert.ok(low.rows.some(c=>c.exceeded&&c.headroom<0&&c.remaining===0));
  const replay=miCountyModel(baseline,result(),{turnout:100,volume:'historical',swing:false},now);
  assert.ok(replay.remaining>low.remaining);
});

test('stale and rejected sources retain descriptive counts and suppress current remaining estimates', () => {
  const r=result();
  for(const patch of [{status:'error'},{lastSuccessAt:new Date(now-16*60000).toISOString()}]) {
    const m=miCountyModel(baseline,{...r,...patch},{},now);
    assert.equal(m.fresh,false);assert.equal(m.remaining,null);assert.equal(m.finalMargin,null);
    assert.equal(m.rows[0].remaining,null);assert.equal(m.counted,r.totalVotes-m.other);
    assert.match(renderMiSummary(m,{...r,...patch},baseline),/STALE/);
  }
  r.counties.pop();assert.equal(miCountyModel(baseline,r,{},now),null);
  assert.throws(()=>miCountyModel(baseline,result(),{turnout:0},now));
});

test('100% supplier estimates and downward corrections are not completion or calls', () => {
  const r=result(), c=r.counties.find(c=>c.totalVotes>0), candidate=c.candidates.find(c=>c.party==='DEM');
  c.estimatedVotePercent=100;
  candidate.votes--;c.totalVotes--;r.totalVotes--;r.candidates.find(c=>c.party==='DEM').votes--;
  const model=miCountyModel(baseline,r,{},now);
  assert.equal(model.rows.find(row=>row.fips===c.fips).remaining,0);
  assert.ok(model.remaining>0);
  assert.equal(model.winner,undefined);
  assert.match(renderMiSummary(model,r,baseline),/Actual uncounted ballots are unknown/);
  const csv=miCsv(model,{turnout:80,volume:'supplier',swing:true},r,baseline);
  assert.equal(csv.trim().split('\r\n').length,84);
  assert.match(csv,/signed_headroom_to_assumption/);
  assert.match(csv,/"Wayne","26163"/);
});

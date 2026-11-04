import pins from '../data/mi-county-pins.json' with { type: 'json' };
import type { CandidateCount, CountyCount } from '../monitor';
import type { ElectionAdapter, ElectionResult } from './types';
import { CNN_AUTHORITY } from './northeast-cnn.ts';

export const miCountyTarget = 'senate-mi-counties';
export const miCountyAdapter: ElectionAdapter = {
  id: 'mi-sen-counties', version: '2026-11-03.1',
  sources: [{ id: 'cnn-mi-counties', name: 'CNN Michigan Senate county returns (newsroom supplier)',
    url: 'https://politics.api.cnn.io/results/county-races/2026-SG-MI.json', authorityUrl: CNN_AUTHORITY, official: false }],
  targets: [{ id: miCountyTarget, state: 'MI', name: 'Michigan Senate county detail', chamber: 'senate', sourceId: 'cnn-mi-counties' }],
  parse: bodies => ({ [miCountyTarget]: parseMiCounties(bodies['cnn-mi-counties']) }),
};

export function parseMiCounties(body: string | undefined): ElectionResult {
  if (!body) throw new Error('Michigan county response unavailable.');
  const rows = JSON.parse(body);
  if (!Array.isArray(rows)) throw new Error('Michigan county array missing.');
  const seen = new Set<string>(), clocks: string[] = [];
  const counties: CountyCount[] = [];
  const expected = pins.counties as Record<string, string>;
  const excluded = pins.excludedMunicipalities as Record<string, string>;
  const candidates = pins.candidates as Record<string, string[]>;
  for (const row of rows) {
    if (!row || row.ecKey !== '2026-SG-MI' || row.resourceType !== 'county-races' || row.externalKey !== 'production-key' ||
        row.electionType !== 'G' || row.contestType !== 'SG' || row.raceType !== 'S' || row.raceTypeCode !== 'S' ||
        row.stateAbbreviation !== 'MI' || row.stateFipsCode !== '26') throw new Error('Michigan county election identity changed.');
    const fips = row.countyFipsCode;
    if (typeof fips !== 'string' || seen.has(fips) || row.countyName !== (expected[fips] ?? excluded[fips]) || !(expected[fips] || excluded[fips]))
      throw new Error('Unknown, duplicate or renamed Michigan geography.');
    seen.add(fips);
    // Wayne's municipal rows overlap its county total. Only the pinned 83
    // five-digit county FIPS enter this tally; never sum all provider rows.
    if (excluded[fips]) continue;
    if (typeof row.extractedAt !== 'string' || !/^2026-\d{2}-\d{2}T/.test(row.extractedAt) || row.extractedAt.slice(0, 10) < '2026-11-03' || !Number.isFinite(Date.parse(row.extractedAt)))
      throw new Error('Invalid Michigan county source timestamp.');
    clocks.push(row.extractedAt);
    if (!Array.isArray(row.candidates) || row.candidates.length !== Object.keys(candidates).length) throw new Error('Michigan county candidate universe changed.');
    const ids = new Set<number>();
    const counts: CandidateCount[] = row.candidates.map((c: any) => {
      const identity = candidates[c.candidateId];
      if (!identity || !Number.isSafeInteger(c.candidateId) || ids.has(c.candidateId) || c.fullName !== identity[0] || c.majorParty !== identity[1] ||
          !Number.isSafeInteger(c.voteNum) || c.voteNum < 0) throw new Error('Invalid Michigan county candidate or votes.');
      ids.add(c.candidateId);
      return { name: identity[0], party: identity[1] === 'GRN' ? 'GRE' : identity[1], votes: c.voteNum };
    });
    const totalVotes = counts.reduce((sum, c) => sum + c.votes, 0);
    if (!Number.isSafeInteger(totalVotes) || row.totalVote !== totalVotes) throw new Error('Michigan county total does not reconcile.');
    if (totalVotes > 0 && (typeof row.voteTimestamp !== 'string' || !Number.isFinite(Date.parse(row.voteTimestamp)) || Date.parse(row.voteTimestamp) < 1793754000000))
      throw new Error('Michigan county votes predate the November 3 results-release time.');
    const estimate = row.percentReporting;
    counties.push({ name: expected[fips], fips, candidates: counts, totalVotes, sourceReporting: null,
      estimatedVotePercent: typeof estimate === 'number' && Number.isFinite(estimate) && estimate >= 0 && estimate <= 100 ? estimate : undefined });
  }
  if (counties.length !== 83) throw new Error('All 83 Michigan counties are required.');
  counties.sort((a, b) => a.fips.localeCompare(b.fips));
  const totals = counties[0].candidates.map(c => ({ ...c, votes: counties.reduce((sum, county) => sum + county.candidates.find(v => v.name === c.name && v.party === c.party)!.votes, 0) }));
  const totalVotes = totals.reduce((sum, c) => sum + c.votes, 0);
  if (!Number.isSafeInteger(totalVotes)) throw new Error('Michigan county sum exceeds supported range.');
  return { status: totalVotes ? 'reporting' : 'setup', coverage: 'complete', candidates: totals, totalVotes, counties, sourceUpdated: clocks.sort()[0],
    message: 'CNN county returns, unofficial. 83 counties sum to this county snapshot; 43 overlapping Wayne municipal rows are excluded. Statewide and county feeds can update separately. Expected-vote percentages are supplier estimates.' };
}

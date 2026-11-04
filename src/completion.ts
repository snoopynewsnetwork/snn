import pins from './data/completion-pins.json' with { type: 'json' };
import type { ElectionAdapter, ElectionResult } from './adapters/types';
import type { LiveResult } from './live-results';
import { count, json, party, tally } from './adapters/northeast-common.ts';

const base = 'https://politics.api.cnn.io/results';
export const completionSources = ['SG', 'HG', 'GG'].map(list => ({
  id: `completion-${list}`, name: `CNN ${list} expected-vote estimates`,
  url: `${base}/national-races/2026-${list}.json`,
  authorityUrl: 'https://www.cnn.com/election/2026', official: false, maxBytes: 8_000_000,
})).concat(['KS', 'MI'].map(state => ({
  id: `completion-local-${state}`, name: `CNN ${state} local expected-vote estimates`,
  url: `${base}/county-races/2026-SG-${state}.json`,
  authorityUrl: 'https://www.cnn.com/election/2026', official: false, maxBytes: 4_000_000,
})));

export function parseCompletion(bodies: Record<string, string>): Record<string, ElectionResult> {
  const parsed = new Map<string, any[]>();
  const rows = (id: string): any[] => {
    if (!parsed.has(id)) {
      const value = json(bodies[id], id);
      if (!Array.isArray(value)) throw new Error('Expected a race list.');
      parsed.set(id, value);
    }
    return parsed.get(id)!;
  };
  return Object.fromEntries(pins.map(pin => {
    try {
      const sourceId = pin.local ? `completion-local-${pin.state}` : `completion-${pin.list}`;
      const parent = rows(`completion-${pin.list}`).filter(r => r.ecKey === pin.key);
      const matches = rows(sourceId).filter(r => r.ecKey === pin.key && (!pin.local || r.countyName === pin.local && r.countyFipsCode === pin.geographyId));
      if (parent.length !== 1 || matches.length !== 1) throw new Error('Missing or duplicate contest/geography.');
      const race = parent[0], row = matches[0];
      if (race.resourceType !== 'race' || row.resourceType !== (pin.local ? 'county-races' : 'race'))
        throw new Error('Unexpected source resource type.');
      for (const item of [race, row]) {
        if (item.externalKey !== 'production-key' || item.stateAbbreviation !== pin.state ||
            item.electionType !== pin.identity.electionType || item.contestType !== pin.identity.contestType ||
            typeof item.extractedAt !== 'string' || !Number.isFinite(Date.parse(item.extractedAt)) || item.extractedAt.slice(0, 10) < '2026-11-03')
          throw new Error('Election identity or timestamp changed.');
      }
      if (race.raceTitle !== pin.identity.raceTitle || race.raceEmbargo?.assignedPollsClose !== pin.identity.pollsClose)
        throw new Error('Election title or poll-close identity changed.');
      const candidates = row.candidates;
      if (!Array.isArray(candidates) || candidates.length !== pin.candidates.length ||
          new Set(candidates.map((c: any) => c.fullName)).size !== candidates.length ||
          pin.candidates.some(c => !candidates.some((v: any) => v.fullName === c.name && v.majorParty === c.party)))
        throw new Error('Candidate universe changed.');
      const normalized = candidates.map((c: any) => ({ name: String(c.fullName), party: party(String(c.majorParty)), votes: count(c.voteNum) }));
      const total = normalized.reduce((sum, c) => sum + c.votes, 0);
      if (total !== count(row.totalVote) || total > 0 && race.raceEmbargo?.votesReleased !== true)
        throw new Error('Votes do not reconcile or embargo has not lifted.');
      const percent = row.percentReporting;
      if (typeof percent !== 'number' || !Number.isFinite(percent) || percent < 0 || percent > 100)
        throw new Error('Expected-vote percentage is missing or invalid.');
      return [pin.id, tally(normalized, { label: 'CNN expected-vote estimate (independent of selected results)',
        sourceId, sourceUpdated: row.extractedAt, coverage: pin.coverage as 'complete' | 'partial',
        estimatedVotePercent: total ? percent : undefined })];
    } catch (error) {
      return [pin.id, { status: 'unavailable', message: error instanceof Error ? error.message : 'Completion unavailable.' }];
    }
  }));
}

export const completionAdapter: ElectionAdapter = {
  id: 'completion-cnn', version: '2026-11-03.1', sources: completionSources,
  targets: pins.map(pin => ({ id: pin.id, state: pin.state, name: pin.name,
    chamber: pin.chamber as 'house' | 'senate' | 'governor',
    sourceId: pin.local ? `completion-local-${pin.state}` : `completion-${pin.list}` })),
  parse: parseCompletion,
};

export function completionEstimate(result?: LiveResult, now = Date.now()) {
  const percent = result?.estimatedVotePercent;
  const age = now - Date.parse(result?.lastSuccessAt ?? '');
  const sourceAge = now - Date.parse(result?.sourceUpdated ? /(?:Z|[+-]\d\d:\d\d)$/.test(result.sourceUpdated) ? result.sourceUpdated : result.sourceUpdated + 'Z' : '');
  const fresh = Number.isFinite(age) && age >= -60_000 && age <= 15 * 60_000 &&
    Number.isFinite(sourceAge) && sourceAge >= -60_000 && sourceAge <= 15 * 60_000;
  const valid = fresh && result?.status === 'reporting' && typeof percent === 'number' && percent >= 0 && percent <= 100;
  const remaining = valid && percent! > 0 && percent! < 100 && result!.totalVotes! > 0
    ? result!.totalVotes! * (100 / percent! - 1) : null;
  return { status: !result ? 'unavailable' : !fresh && result.lastSuccessAt ? 'stale' : result.status,
    percentCounted: valid ? percent : null, supplierVotes: result?.totalVotes ?? null,
    estimatedRemainingVotes: remaining === null ? null : Math.round(remaining),
    uncertainty: 'Supplier percentage precision and turnout uncertainty are unquantified; this is not an exact ballot inventory.',
    sourceName: result?.sourceName ?? 'CNN', sourceUrl: result?.sourceUrl ?? null,
    sourceUpdated: result?.sourceUpdated ?? null, checkedAt: result?.lastSuccessAt ?? null,
    evidence: result?.sourceSnapshots ?? [], reason: result?.message ?? 'No completion observation collected yet.' };
}

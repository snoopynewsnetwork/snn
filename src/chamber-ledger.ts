import snapshot from './data/chamber-ledger.json' with { type: 'json' };
import type { LiveResult } from './live-results';
import type { ForecastRun, Seat, Caucus } from './needle-model';
import type { CandidateCount } from './monitor';

export type Chamber = 'house' | 'senate';
export interface LedgerUpdate {
  id: string;
  status: 'declared' | 'unresolved' | 'review';
  caucus: 'D' | 'R' | null;
  winner: string | null;
  party: string | null;
  sourceUpdated: string | null;
  checkedAt: string;
  sourceUrl: string;
  evidenceUrl?: string;
  reason?: string;
  unallocatedVotes?: number;
  candidates?: CandidateCount[];
  totalVotes?: number;
  estimatedVotePercent?: number;
}
export interface LedgerSeat {
  id: string; chamber: string; state: string; raceId: string | null;
  status: 'not-up' | 'declared' | 'unresolved' | 'review';
  caucus: 'D' | 'R' | null; holder: string | null; party: string | null;
  winner: string | null; declarationKind: string | null; sourceId: string;
  sourceUpdated: string | null; sourceUrl: string; sourceKind: 'official' | 'supplier';
  checkedAt: string; evidenceUrl: string | null; reason: string | null;
  election?: { key: string; electionType: string; contestType: string; raceTitle: string; pollsClose: number; candidates: { name: string; party: string }[] };
  caucusSourceId?: string;
  unallocatedVotes?: number;
}

const utc = (value: string | null) => value ? Date.parse(/(?:Z|[+-]\d\d:\d\d)$/.test(value) ? value : value + 'Z') : NaN;
const expected = (chamber: Chamber) => snapshot.seats.filter(seat => seat.chamber === chamber && seat.election);
export const ledgerSources = snapshot.sources;
export const ledgerAsOf = snapshot.asOf;
export const ledgerTieBreaker = snapshot.senateTieBreaker;

// The source is already fetched and retained by completion-cnn. A row explicitly
// lacking a winner clears a prior projection; validation failures remain review.
export function parseLedgerFeed(chamber: Chamber, body: string, checkedAt: string, evidenceUrl?: string): LedgerUpdate[] {
  let rows: any[] = [];
  try { const value = JSON.parse(body); if (Array.isArray(value)) rows = value; }
  catch {}
  const sourceUrl = snapshot.sources[chamber === 'house' ? 'house-races' : 'senate-races'].url;
  return expected(chamber).map(seat => {
    const result: LedgerUpdate = { id: seat.id, status: 'review', caucus: null, winner: null, party: null,
      sourceUpdated: null, checkedAt, sourceUrl, evidenceUrl };
    try {
      const pin = seat.election!;
      const matches = rows.filter(row => row?.ecKey === pin.key);
      if (matches.length !== 1) throw new Error('Missing or duplicate contest.');
      const row = matches[0];
      if (row.externalKey !== 'production-key' || row.resourceType !== 'race' || row.stateAbbreviation !== seat.state ||
          row.electionType !== pin.electionType || row.contestType !== pin.contestType || row.raceTitle !== pin.raceTitle ||
          row.raceEmbargo?.assignedPollsClose !== pin.pollsClose || typeof row.extractedAt !== 'string' ||
          row.extractedAt.slice(0, 10) < snapshot.electionDate || !Number.isFinite(utc(row.extractedAt)) ||
          utc(row.extractedAt) > Date.parse(checkedAt) + 60_000)
        throw new Error('Contest identity, production status, or extraction time changed.');
      result.sourceUpdated = row.extractedAt;
      if (!Array.isArray(row.candidates) || row.candidates.length !== pin.candidates.length ||
          new Set(row.candidates.map((c: any) => c.fullName)).size !== pin.candidates.length ||
          pin.candidates.some(candidate => !row.candidates.some((c: any) => c.fullName === candidate.name && c.majorParty === candidate.party)))
        throw new Error('Candidate universe changed.');
      const candidateVotes = row.candidates.reduce((sum: number, c: any) => sum + c.voteNum, 0);
      if (!Number.isSafeInteger(row.totalVote) || row.totalVote < 0 || row.candidates.some((c: any) => !Number.isSafeInteger(c.voteNum) || c.voteNum < 0) ||
          !Number.isSafeInteger(candidateVotes) || candidateVotes > row.totalVote)
        throw new Error('Candidate votes exceed the published total or contain invalid counts.');
      // Some publisher totals include votes not allocated to listed candidates.
      // This adapter reads explicit calls only; it never computes a vote margin.
      result.unallocatedVotes = row.totalVote - candidateVotes;
      result.candidates = row.candidates.map((candidate: any) => ({ name: candidate.fullName,
        party: candidate.majorParty, votes: candidate.voteNum }));
      result.totalVotes = row.totalVote;
      if (typeof row.percentReporting === 'number' && Number.isFinite(row.percentReporting) && row.percentReporting >= 0 && row.percentReporting <= 100)
        result.estimatedVotePercent = row.percentReporting;
      const winners = row.candidates.filter((candidate: any) => candidate.winner === true);
      if (winners.length > 1 || (winners.length || row.totalVote > 0) && row.raceEmbargo?.votesReleased !== true)
        throw new Error('Multiple winners or pre-embargo publication.');
      if (!winners.length) return { ...result, status: 'unresolved' };
      const winner = winners[0];
      // Independent ballot affiliation alone says nothing about future caucusing.
      return { ...result, status: 'declared', winner: winner.fullName, party: winner.majorParty,
        caucus: winner.majorParty === 'DEM' ? 'D' : winner.majorParty === 'REP' ? 'R' : null };
    } catch (error) { return { ...result, reason: error instanceof Error ? error.message : 'Source validation failed.' }; }
  });
}

export function buildChamberLedger(chamber: Chamber, updates: LedgerUpdate[] = [], results: LiveResult[] = []) {
  const seats = snapshot.seats.filter(seat => seat.chamber === chamber).map(base => {
    const source = snapshot.sources[base.sourceId as keyof typeof snapshot.sources];
    const update = updates.find(update => update.id === base.id);
    let seat = { ...base, sourceUrl: source.url, sourceKind: source.official ? 'official' : 'supplier',
      checkedAt: source.retrievedAt, evidenceUrl: null, reason: null } as LedgerSeat;
    if (update && base.status !== 'not-up') seat = { ...seat, ...update, declarationKind: update.status === 'declared' ? 'newsroom-projection' : null,
      sourceKind: 'supplier', evidenceUrl: update.evidenceUrl ?? null, reason: update.reason ?? null } as typeof seat;
    const official = results.find(result => result.target === base.raceId && result.sourceKind === 'official' && result.winner && result.coverage !== 'partial' && result.status === 'reporting');
    if (official?.lastSuccessAt) {
      const caucus = official.winner === 'D' ? 'D' : official.winner === 'R' ? 'R' : null;
      if (seat.status === 'declared' && seat.caucus && caucus && seat.caucus !== caucus) {
        seat = { ...seat, status: 'review', caucus: null, reason: 'Official declaration and newsroom projection disagree.' };
      } else if (!Number.isFinite(utc(seat.sourceUpdated)) || Date.parse(official.lastSuccessAt) >= utc(seat.sourceUpdated)) {
        const party = caucus === 'D' ? 'DEM' : caucus === 'R' ? 'REP' : official.winner === 'I' ? 'IND' : null;
        const candidates = official.candidates?.filter(candidate => candidate.party === party) ?? [];
        seat = { ...seat, status: 'declared', caucus, declarationKind: 'official-declaration', sourceUrl: official.sourceUrl,
          sourceId: official.sourceId ?? 'official-result', holder: null, party,
          sourceKind: 'official', checkedAt: official.lastSuccessAt, sourceUpdated: official.sourceUpdated ?? official.lastSuccessAt,
          winner: candidates.length === 1 ? candidates[0].name : null };
      }
    }
    return seat;
  });
  const resolved = seats.filter(seat => ['not-up', 'declared'].includes(seat.status) && seat.caucus !== null);
  return { schemaVersion: 1, chamber, electionDate: snapshot.electionDate, seatingHorizon: snapshot.seatingHorizon,
    snapshotAsOf: snapshot.asOf, inventoryComplete: seats.length === (chamber === 'house' ? 435 : 100),
    totalSeats: seats.length, resolvedSeats: resolved.length, unresolvedSeats: seats.length - resolved.length,
    notUpSeats: seats.filter(seat => seat.status === 'not-up').length,
    declaredSeats: seats.filter(seat => seat.status === 'declared').length,
    caucusSeats: { D: resolved.filter(seat => seat.caucus === 'D').length, R: resolved.filter(seat => seat.caucus === 'R').length },
    senateTieBreaker: chamber === 'senate' ? { ...snapshot.senateTieBreaker,
      sourceUrl: snapshot.sources['vice-president'].url, ruleSourceUrl: snapshot.sources['tie-rule'].url } : null,
    sources: snapshot.sources, seats };
}

export function chamberInputs(chamber: Chamber, run: ForecastRun | null, updates: LedgerUpdate[] = [], results: LiveResult[] = []) {
  const ledger = buildChamberLedger(chamber, updates, results);
  const races = run?.races.filter(race => race.chamber === chamber) ?? [];
  const fixed = new Map<string, Seat>();
  const conflicts: { seatId: string; reason: string; sourceUrl: string; sourceUpdated: string | null }[] = [];
  for (const seat of ledger.seats) {
    if (!['not-up', 'declared'].includes(seat.status) || !seat.caucus) continue;
    const forecast = races.find(race => race.seatId === seat.id);
    const explicit = run?.fixedSeats[chamber].find(value => value.id === seat.id);
    if (forecast && [...forecast.outcomes].some(outcome => outcome !== seat.caucus) || explicit && explicit.caucus !== seat.caucus) {
      conflicts.push({ seatId: seat.id, reason: 'Published model contradicts the sourced ledger outcome.', sourceUrl: seat.sourceUrl, sourceUpdated: seat.sourceUpdated });
      continue;
    }
    if (!forecast) fixed.set(seat.id, { id: seat.id, caucus: seat.caucus as Caucus,
      basis: seat.status === 'not-up' ? 'not-up' : 'declared', sourceUrl: seat.sourceUrl });
  }
  for (const seat of run?.fixedSeats[chamber] ?? []) if (!fixed.has(seat.id)) fixed.set(seat.id, seat);
  if (chamber === 'senate' && run && run.senateTieBreaker !== snapshot.senateTieBreaker.caucus)
    conflicts.push({ seatId: 'senate-tie-breaker', reason: 'Published model tie-breaking caucus contradicts the sourced vice-presidential baseline.', sourceUrl: snapshot.sources['vice-president'].url, sourceUpdated: snapshot.senateTieBreaker.asOf });
  return { ledger, races, fixed: [...fixed.values()], conflicts, missingSeats: ledger.totalSeats - races.length - fixed.size };
}

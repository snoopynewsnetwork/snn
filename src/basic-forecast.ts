import pins from './data/completion-pins.json' with { type: 'json' };
import { buildChamberLedger, ledgerTieBreaker } from './chamber-ledger.ts';
import type { ForecastRun, ForecastRace } from './needle-model.ts';
import type { NeedleInputs } from './needles.ts';
import type { CandidateCount } from './monitor';
import normalQuantiles from './data/normal-quantiles.json' with { type: 'json' };

export const BASIC_MODEL_VERSION = 'basic-vote-mix-v2';
export const BASIC_DRAWS = 256;
const PRIOR_VOTES = 20;
const RACE_SCORE_SD = 1;
const NATIONAL_LOG_ODDS_SD = .35;
const MAX_COUNTED_FRACTION = .99;

// Fixed per-race streams keep unchanged inputs stable across collection cycles.
// Each column also uses the same national shock across ALL races/chambers.
function random(seed: string) {
  let state = 2166136261;
  for (const char of seed) state = Math.imul(state ^ char.charCodeAt(0), 16777619);
  return () => {
    state += 0x6D2B79F5;
    let value = Math.imul(state ^ state >>> 15, 1 | state);
    value ^= value + Math.imul(value ^ value >>> 7, 61 | value);
    return ((value ^ value >>> 14) >>> 0) / 4294967296;
  };
}
function normal(rng: () => number) {
  return normalQuantiles[Math.floor(rng() * normalQuantiles.length)];
}
const timestamp = (value?: string | null) => value ? Date.parse(/(?:Z|[+-]\d\d:\d\d)$/.test(value) ? value : value + 'Z') : NaN;
const fresh = (value: string | null | undefined, now: number) => { const age = now - timestamp(value); return age >= -60_000 && age <= 15 * 60_000; };
const caucus = (party: string) => ['DEM', 'D'].includes(party) ? 'D' : ['REP', 'R'].includes(party) ? 'R' : 'O';

// Equal D/R priors, with a small third-party share. If one major party is absent,
// listed independents get equal standing as its opponent, without guessing caucus.
function priorShares(candidates: { party: string }[]) {
  const hasD = candidates.some(c => caucus(c.party) === 'D'), hasR = candidates.some(c => caucus(c.party) === 'R');
  const major = candidates.map(c => caucus(c.party) !== 'O' || (!hasD || !hasR) && ['IND', 'I'].includes(c.party));
  const groups = candidates.map(c => caucus(c.party) === 'O' ? 'IND' : caucus(c.party));
  const others = major.filter(value => !value).length;
  const weights = candidates.map((_, i) => major[i] ? 1 / groups.filter((group, j) => major[j] && group === groups[i]).length : .05 / Math.max(1, others));
  const total = weights.reduce((sum, value) => sum + value, 0);
  return weights.map(weight => weight / total);
}

interface RaceInput {
  id: string; name: string; chamber: ForecastRace['chamber']; seatId: string;
  candidates: { name: string; party: string }[];
  observed?: CandidateCount[]; totalVotes?: number; unallocatedVotes?: number; percent?: number;
  sourceUrl: string; sourceUpdated?: string | null; checkedAt?: string | null;
  valid: boolean; declared?: string | null; reason?: string;
}

function simulate(input: RaceInput, national: number[], now: number): ForecastRace {
  const prior = priorShares(input.candidates);
  const votes = input.candidates.map(c => input.observed?.find(row => row.name === c.name && row.party === c.party)?.votes ?? 0);
  const total = votes.reduce((sum, value) => sum + value, 0);
  const unallocated = input.unallocatedVotes ?? 0;
  const published = input.totalVotes ?? 0;
  const reconciled = input.observed?.length === input.candidates.length && votes.every(v => Number.isSafeInteger(v) && v >= 0) &&
    Number.isSafeInteger(published) && Number.isSafeInteger(unallocated) && unallocated >= 0 && total + unallocated === published;
  const live = input.valid && reconciled && total > 0 && typeof input.percent === 'number' && input.percent > 0 && input.percent <= 100 &&
    fresh(input.sourceUpdated, now) && fresh(input.checkedAt, now);
  const counted = live ? Math.min(MAX_COUNTED_FRACTION, input.percent! / 100) : 0;
  const center = prior.map((share, i) => live ? (votes[i] + PRIOR_VOTES * share) / (total + PRIOR_VOTES) : share);
  const observedShare = votes.map(v => published ? v / published : 0);
  const unknownShare = published ? counted * unallocated / published : 0;
  const rng = random(`${BASIC_MODEL_VERSION}:${input.id}`);
  let outcomes = '';
  const margins: number[] = [];
  const hasBothParties = input.candidates.some(c => caucus(c.party) === 'D') && input.candidates.some(c => caucus(c.party) === 'R');
  for (let draw = 0; draw < BASIC_DRAWS; draw++) {
    if (input.declared) { outcomes += input.declared; continue; }
    const remaining = center.map((share, i) => {
      const party = caucus(input.candidates[i].party);
      const loading = party === 'D' ? .5 : party === 'R' ? -.5 : 0;
      return share * Math.exp(RACE_SCORE_SD * normal(rng) + loading * national[draw]);
    });
    const sum = remaining.reduce((a, b) => a + b, 0);
    const final = remaining.map((share, i) => counted * observedShare[i] + (1 - counted) * share / sum);
    let winner = 0;
    final.forEach((share, i) => { if (share > final[winner]) winner = i; });
    const runnerUp = Math.max(0, ...final.filter((_, i) => i !== winner));
    // Unknown counted votes can belong to any candidate, including an unlisted
    // write-in. Keep a draw unresolved if their allocation could change its winner.
    outcomes += final[winner] - runnerUp <= unknownShare ? 'O' : caucus(input.candidates[winner].party);
    if (live && hasBothParties) {
      const share = (party: string) => final.reduce((sum, value, i) => sum + (caucus(input.candidates[i].party) === party ? value : 0), 0);
      margins.push(Math.round((share('D') - share('R')) * 10000) / 100);
    }
  }
  const basis = input.declared ? 'declared' : live ? 'live' : 'prior';
  return { id: input.id, name: input.name, chamber: input.chamber, seatId: input.seatId, outcomes,
    ...(margins.length ? { margins } : {}),
    ...(margins.length && unknownShare ? { unallocatedMarginBound: unknownShare * 100 } : {}),
    input: { basis, reason: input.reason ?? (basis === 'declared' ? 'Explicit sourced declaration used as a fixed outcome; independent caucusing remains unresolved when unknown.'
      : live ? 'Remaining votes simulated around the current candidate mix; reporting-order bias is not modeled.'
      : 'Neutral ballot prior only: fresh reconciled counts and a same-source completion percentage are not both available.'),
      sourceUrl: input.sourceUrl, sourceUpdated: input.sourceUpdated ?? null, checkedAt: input.checkedAt ?? null,
      totalVotes: input.valid ? input.totalVotes ?? null : null, percentCounted: live ? input.percent! : null,
      unallocatedVotes: input.valid ? unallocated : 0,
      candidates: input.valid ? input.observed ?? [] : [] } };
}

export function buildBasicForecast(monitor: NeedleInputs, now = Date.now()): ForecastRun {
  const rng = random(`${BASIC_MODEL_VERSION}:national`);
  const national = Array.from({ length: BASIC_DRAWS }, () => NATIONAL_LOG_ODDS_SD * normal(rng));
  const races: ForecastRace[] = [];
  for (const chamber of ['house', 'senate'] as const) {
    const ledger = buildChamberLedger(chamber, monitor.ledgerUpdates, monitor.races);
    for (const seat of ledger.seats) {
      if (!seat.raceId || !seat.election) continue;
      const observation = monitor.ledgerUpdates?.find(update => update.id === seat.id);
      races.push(simulate({ id: seat.raceId, name: monitor.races.find(race => race.target === seat.raceId)?.name ?? `${seat.state} ${chamber === 'house' ? 'House · ' + seat.raceId.split('-').at(-1) : 'Senate'}`, chamber, seatId: seat.id,
        candidates: seat.election.candidates, observed: observation?.candidates, totalVotes: observation?.totalVotes, unallocatedVotes: observation?.unallocatedVotes,
        percent: observation?.estimatedVotePercent, sourceUrl: observation?.sourceUrl ?? seat.sourceUrl,
        sourceUpdated: observation?.sourceUpdated ?? seat.sourceUpdated, checkedAt: observation?.checkedAt ?? seat.checkedAt,
        valid: !!observation && observation.status !== 'review' && !observation.reason,
        declared: seat.status === 'declared' ? seat.caucus ?? 'O' : null }, national, now));
    }
  }
  for (const pin of pins.filter(pin => pin.chamber === 'governor')) {
    const result = monitor.completion.find(result => result.target === pin.id);
    const official = monitor.races.find(result => result.target === pin.id);
    races.push(simulate({ id: pin.id, name: pin.name, chamber: 'governor', seatId: pin.id,
      candidates: pin.candidates, observed: result?.candidates, totalVotes: result?.totalVotes, unallocatedVotes: result?.unallocatedVotes, percent: result?.estimatedVotePercent,
      sourceUrl: result?.sourceUrl ?? 'https://www.cnn.com/election/2026', sourceUpdated: result?.projection?.sourceUpdated ?? result?.sourceUpdated,
      checkedAt: result?.lastSuccessAt, valid: result?.status === 'reporting',
      declared: official?.status === 'reporting' && official.winner ? official.winner === 'D' ? 'D' : official.winner === 'R' ? 'R' : 'O'
        : result?.projection ? caucus(result.projection.party) : null,
      reason: result?.projection ? `CNN projects ${result.projection.candidate}; this is a supplier projection, not official certification.` : undefined }, national, now));
  }
  return { electionDate: '2026-11-03', modelVersion: BASIC_MODEL_VERSION, releaseStatus: 'experimental',
    asOf: new Date(now).toISOString(), calibrationUrl: null, races, fixedSeats: { house: [], senate: [] }, senateTieBreaker: ledgerTieBreaker.caucus as 'D' | 'R',
    assumptions: [
      'EXPERIMENTAL: this basic model has not been calibrated or backtested. Probabilities are conditional on these assumptions, not race calls.',
      'No polls, incumbency, ratings or external forecasts. Missing/stale/incomplete data uses a neutral D/R ballot prior; listed independents can win without an assumed caucus.',
      'CNN candidate counts plus explicitly unallocated votes reconcile to the published total. Known votes stay fixed. Unallocated votes are never assigned a party: draws whose winner could change are unresolved, and margin intervals include their worst-case allocation.',
      'Remaining shares use independent normal log-score noise with standard deviation 1, plus a shared national D/R log-odds shock with standard deviation 0.35. These uncertainty constants are heuristic.',
      'Completion is capped at 99% in the model, including displayed 100%. Estimated turnout and reporting-order bias are not modeled. No usable completion means prior-only predictions.',
      'The model predicts final plurality from candidate shares. Ranked-choice transfers, runoffs, and later ballot eligibility changes are not modeled.',
      '256 reproducible joint simulations across all 470 congressional elections and three governors, using 1,024 standard-normal quantile bins. Sourced declarations and Senate holdovers are incorporated separately; third-party/unknown caucus wins retain other-control mass.',
    ] };
}

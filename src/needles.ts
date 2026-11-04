import { completionEstimate } from './completion.ts';
import { chamberDistribution, summarizeRace, type ForecastRun, type ForecastRace } from './needle-model.ts';
import houseSeats from './data/house-seats.json' with { type: 'json' };
import senateSeats from './data/senate-seats.json' with { type: 'json' };
import senateElectionSeats from './data/senate-election-seats.json' with { type: 'json' };
import type { LiveResult } from './live-results';
import { chamberInputs, ledgerTieBreaker, type LedgerUpdate } from './chamber-ledger.ts';

const states = new Set(houseSeats.map(id => id.split('-')[1]));
// Runs returned by NeedleStore are immutable publication artifacts. Cache their
// expensive joint summaries; a newly published run has a new object identity.
const summaries = new WeakMap<ForecastRun, Map<string, unknown>>();
function summary<T>(run: ForecastRun, id: string, calculate: () => T): T {
  let cached = summaries.get(run);
  if (!cached) { cached = new Map(); summaries.set(run, cached); }
  if (!cached.has(id)) cached.set(id, calculate());
  return cached.get(id) as T;
}
function validSeat(id: string, chamber: string) {
  if (chamber === 'house') return houseSeats.includes(id);
  return senateSeats.includes(id);
}

export function validateForecastRun(input: unknown, now = Date.now()): ForecastRun {
  const run = input as ForecastRun;
  if (!run || run.electionDate !== '2026-11-03' || typeof run.modelVersion !== 'string' || !run.modelVersion.trim() || run.modelVersion.length > 200 ||
      typeof run.asOf !== 'string' || !/(Z|[+-]\d\d:\d\d)$/.test(run.asOf) || !Number.isFinite(Date.parse(run.asOf)) || Date.parse(run.asOf) > now + 60_000 ||
      !Array.isArray(run.races) || run.races.length > 600 || !Array.isArray(run.assumptions) || run.assumptions.length > 100 ||
      run.assumptions.some(s => typeof s !== 'string' || s.length > 2000) || !['D', 'R'].includes(run.senateTieBreaker))
    throw new Error('Invalid forecast identity, timestamp, assumptions, or race list.');
  if (run.releaseStatus !== undefined && !['experimental', 'calibrated'].includes(run.releaseStatus)) throw new Error('Invalid forecast release status.');
  if (run.releaseStatus !== 'experimental' || run.calibrationUrl !== null) {
    const url = new URL(run.calibrationUrl ?? '');
    if (url.protocol !== 'https:' || url.username || url.password) throw new Error('A public HTTPS calibration report is required.');
  }
  const ids = new Set<string>(), seats = new Set<string>();
  const n = run.races[0]?.outcomes?.length ?? 1;
  if (n < 1 || n > 10_000) throw new Error('Use 1–10,000 joint draws.');
  for (const race of run.races) {
    if (!race || typeof race.id !== 'string' || !/^(house|senate|governor)-[a-z]{2}(?:-\d{2})?$/.test(race.id) ||
        typeof race.name !== 'string' || !race.name.trim() || race.name.length > 200 || !['house', 'senate', 'governor'].includes(race.chamber) ||
        !race.id.startsWith(race.chamber + '-') || !states.has(race.id.split('-')[1]) || typeof race.seatId !== 'string' ||
        (race.chamber === 'governor' ? race.seatId !== race.id : !validSeat(race.seatId, race.chamber)) ||
        race.chamber === 'house' && race.seatId !== race.id || race.chamber === 'senate' && (!race.seatId.startsWith(race.id + '-') || !senateElectionSeats.includes(race.seatId)) ||
        ids.has(race.id) || seats.has(race.seatId) || typeof race.outcomes !== 'string' || race.outcomes.length !== n || !/^[DRO]+$/.test(race.outcomes) ||
        race.margins !== undefined && (!Array.isArray(race.margins) || race.margins.length !== n || race.margins.some(m => !Number.isFinite(m) || Math.abs(m) > 100)) ||
        race.unallocatedMarginBound !== undefined && (!Number.isFinite(race.unallocatedMarginBound) || race.unallocatedMarginBound < 0 || race.unallocatedMarginBound > 100))
      throw new Error('Invalid/duplicate race, seat, outcomes, or margins.');
    ids.add(race.id); seats.add(race.seatId);
    if (race.input !== undefined) {
      const input = race.input;
      if (!input || !['live', 'prior', 'declared'].includes(input.basis) || typeof input.reason !== 'string' || input.reason.length > 2000 ||
          typeof input.sourceUrl !== 'string' || !/^https:\/\//.test(input.sourceUrl) ||
          input.totalVotes !== null && (!Number.isSafeInteger(input.totalVotes) || input.totalVotes < 0) ||
          input.unallocatedVotes !== undefined && (!Number.isSafeInteger(input.unallocatedVotes) || input.unallocatedVotes < 0) ||
          input.percentCounted !== null && (!Number.isFinite(input.percentCounted) || input.percentCounted < 0 || input.percentCounted > 100) ||
          !Array.isArray(input.candidates) || input.candidates.length > 100 || input.candidates.some(c => !c || typeof c.name !== 'string' || typeof c.party !== 'string' || !Number.isSafeInteger(c.votes) || c.votes < 0) ||
          [input.sourceUpdated, input.checkedAt].some(t => t !== null && (typeof t !== 'string' || !Number.isFinite(Date.parse(t)))))
        throw new Error('Invalid forecast input provenance.');
    }
  }
  for (const chamber of ['house', 'senate'] as const) {
    const fixed = run.fixedSeats?.[chamber];
    if (!Array.isArray(fixed) || fixed.length > (chamber === 'house' ? 435 : 100)) throw new Error('Invalid fixed-seat ledger.');
    for (const seat of fixed) {
      if (!seat || !validSeat(seat.id, chamber) || seats.has(seat.id) || !['D', 'R', 'O'].includes(seat.caucus)) throw new Error('Invalid or duplicate fixed seat.');
      const source = new URL(seat.sourceUrl ?? '');
      if (source.protocol !== 'https:' || source.username || source.password || !['not-up', 'declared', 'assumption'].includes(seat.basis ?? ''))
        throw new Error('Every fixed seat needs HTTPS provenance and an explicit basis.');
      if (seat.basis === 'not-up' && (chamber === 'house' || senateElectionSeats.includes(seat.id)))
        throw new Error('A seat up for election cannot use a not-up baseline.');
      if (seat.basis === 'assumption' && run.assumptions.length === 0) throw new Error('Fixed-seat assumptions must be disclosed.');
      seats.add(seat.id);
    }
    // A missing chamber ledger is allowed, but cannot produce control odds.
    const ledger = [...fixed.map(s => s.id), ...run.races.filter(r => r.chamber === chamber).map(r => r.seatId)];
    if (ledger.length > (chamber === 'house' ? 435 : 100)) throw new Error('Too many chamber seats.');
    if (chamber === 'senate' && [...states].some(state => ledger.filter(id => id.startsWith(`senate-${state}-`)).length > 2))
      throw new Error('A state cannot contribute more than two Senate seats.');
  }
  return run;
}

export interface NeedleInputs {
  races: LiveResult[];
  completion: LiveResult[];
  lastCheckedAt: string | null;
  ledgerUpdates?: LedgerUpdate[];
}

export function needleCatalog(monitor: NeedleInputs, run: ForecastRun | null, includeAll = false) {
  const fullRace = (id: string) => houseSeats.includes(id) || /^senate-[a-z]{2}$/.test(id) && senateElectionSeats.some(seat => seat.startsWith(id + '-')) || /^governor-[a-z]{2}$/.test(id) && states.has(id.split('-')[1]);
  // Scope is an identity property, not a reporting-state field: pending local
  // helpers must never become extra needles before coverage metadata arrives.
  const entries = new Map(monitor.races.filter(r => fullRace(r.target ?? '')).map(r => [r.target!, { id: r.target!, name: r.name ?? r.target!, chamber: r.chamber }]));
  for (const race of run?.races ?? []) if (includeAll || entries.has(race.id)) entries.set(race.id, { id: race.id, name: race.name, chamber: race.chamber });
  return [{ id: 'house-control', name: 'House control', chamber: 'house' }, { id: 'senate-control', name: 'Senate control', chamber: 'senate' }, ...entries.values()]
    .map(entry => ({ ...entry, apiUrl: `/api/needle/${entry.id}` }));
}

export function buildNeedle(id: string, monitor: NeedleInputs, run: ForecastRun | null, now = Date.now()) {
  const entry = needleCatalog(monitor, run, true).find(entry => entry.id === id);
  if (!entry) return null;
  const age = now - Date.parse(run?.asOf ?? '');
  const freshRun = !!run && age >= -60_000 && age <= 15 * 60_000;
  const availableStatus = run?.releaseStatus === 'experimental' ? 'experimental' : 'ready';
  const common = { ...entry, schemaVersion: 1, forecastTimestamp: run?.asOf ?? null, modelVersion: run?.modelVersion ?? null,
    releaseStatus: run?.releaseStatus ?? (run ? 'calibrated' : null),
    calibrationUrl: run?.calibrationUrl ?? null, assumptions: run?.assumptions ?? [], lastCheckedAt: monitor.lastCheckedAt,
    probabilities: null as ReturnType<typeof summarizeRace>['probabilities'] | null };
  if (id.endsWith('-control')) {
    const chamber = id === 'house-control' ? 'house' : 'senate';
    const totalSeats = chamber === 'house' ? 435 : 100;
    const { ledger, races, fixed, conflicts, missingSeats } = chamberInputs(chamber, run, monitor.ledgerUpdates, monitor.races);
    const thresholds = chamber === 'house' ? { D: 218, R: 218 } : { D: ledgerTieBreaker.caucus === 'D' ? 50 : 51, R: ledgerTieBreaker.caucus === 'R' ? 50 : 51 };
    const ready = freshRun && missingSeats === 0 && conflicts.length === 0;
    const modeled = { live: 0, prior: 0, declared: 0 };
    for (const race of races) if (race.input) modeled[race.input.basis]++;
    return { ...common, kind: 'chamber', status: ready ? availableStatus : run && !freshRun ? 'stale' : 'unavailable',
      reason: ready ? null : conflicts.length ? 'Published forecast conflicts with sourced ledger outcomes; publish a coherent replacement run.' : missingSeats ? `Seat inventory is complete; ${missingSeats} seats still need a forecast or explicit outcome baseline.` : 'Forecast run is stale.',
      totalSeats, thresholds, senateTieBreaker: chamber === 'senate' ? ledgerTieBreaker.caucus : null,
      ledger: { inventoryComplete: ledger.inventoryComplete, snapshotAsOf: ledger.snapshotAsOf, resolvedSeats: ledger.resolvedSeats,
        unresolvedSeats: ledger.unresolvedSeats, notUpSeats: ledger.notUpSeats, declaredSeats: ledger.declaredSeats,
        caucusSeats: ledger.caucusSeats, apiUrl: `/api/chamber-ledger/${chamber}` }, conflicts,
      fixedSeats: fixed, contributingRaceIds: races.map(r => r.id), missingSeats,
      modelCoverage: modeled,
      method: 'Joint simulation draws; shared race errors are preserved.',
      seatDistribution: null, seatInterval: null, simulationDraws: null, simulationStandardError: null,
      ...(ready ? summary(run!, `${id}:${fixed.map(seat => `${seat.id}=${seat.caucus}`).sort().join(',')}`, () => chamberDistribution(races, fixed, totalSeats, thresholds)) : {}) };
  }
  const result = monitor.races.find(r => r.target === id);
  const forecast: ForecastRace | undefined = run?.races.find(r => r.id === id);
  const conflict = forecast && forecast.chamber !== 'governor'
    ? chamberInputs(forecast.chamber, run, monitor.ledgerUpdates, monitor.races).conflicts.find(conflict => conflict.seatId === forecast.seatId) : undefined;
  const completion = monitor.completion.find(r => r.target === id);
  const hasResultCounts = !!result?.candidates?.length;
  const hasModelCounts = !!forecast?.input?.candidates.length;
  return { ...common, kind: 'race', status: conflict ? 'unavailable' : forecast && freshRun ? availableStatus : forecast ? 'stale' : 'uncalibrated',
    reason: conflict ? conflict.reason : !forecast ? 'No calibrated forecast has been published for this race.' : !freshRun ? 'Forecast run is stale.' : null,
    ledgerConflict: conflict ?? null,
    modelInput: forecast?.input ?? null,
    observed: { candidates: hasResultCounts ? result!.candidates! : forecast?.input?.candidates ?? [],
      totalVotes: hasResultCounts ? result!.totalVotes ?? null : forecast?.input?.totalVotes ?? null,
      unallocatedVotes: hasResultCounts ? result!.unallocatedVotes ?? 0 : forecast?.input?.unallocatedVotes ?? 0,
      status: hasResultCounts ? result!.status : hasModelCounts ? 'supplier' : result?.status ?? 'unavailable',
      sourceName: hasResultCounts ? result!.sourceName ?? 'Selected results source' : hasModelCounts ? 'Published model snapshot' : result?.sourceName ?? null,
      sourceKind: hasResultCounts ? result!.sourceKind ?? null : null,
      sourceUrl: hasResultCounts ? result!.sourceUrl : hasModelCounts ? forecast!.input!.sourceUrl : result?.sourceUrl ?? null,
      sourceUpdated: hasResultCounts ? result!.sourceUpdated ?? null : forecast?.input?.sourceUpdated ?? null,
      checkedAt: hasResultCounts ? result!.lastSuccessAt ?? null : forecast?.input?.checkedAt ?? null },
    completion: completionEstimate(completion, now),
    projectedMargin: null, marginInterval: null, simulationDraws: null, simulationStandardError: null,
    ...(forecast && freshRun && !conflict ? summary(run!, id, () => summarizeRace(forecast)) : {}) };
}

// Published runs are immutable audit artifacts. Store in chunks to respect
// SQLite per-value limits; public reads use the saved run without network I/O.
export class NeedleStore {
  private storage: DurableObjectStorage;
  private cache?: { version: number; run: ForecastRun | null; automatic: boolean };
  constructor(storage: DurableObjectStorage) {
    this.storage = storage;
    storage.sql.exec(`CREATE TABLE IF NOT EXISTS needle_runs (version INTEGER PRIMARY KEY, asOf TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS needle_run_chunks (version INTEGER NOT NULL, position INTEGER NOT NULL, data TEXT NOT NULL, PRIMARY KEY(version, position));`);
    if (!storage.sql.exec<{ name: string }>('PRAGMA table_info(needle_runs)').toArray().some(column => column.name === 'automatic'))
      storage.sql.exec('ALTER TABLE needle_runs ADD COLUMN automatic INTEGER NOT NULL DEFAULT 0');
  }
  latest() {
    const row = this.storage.sql.exec<{ version: number; automatic: number }>('SELECT version, automatic FROM needle_runs ORDER BY version DESC LIMIT 1').toArray()[0];
    if (!row) return { version: 0, run: null as ForecastRun | null, automatic: false };
    if (this.cache?.version === row.version) return this.cache;
    const data = this.storage.sql.exec<{ data: string }>('SELECT data FROM needle_run_chunks WHERE version = ? ORDER BY position', row.version).toArray().map(r => r.data).join('');
    return this.cache = { version: row.version, run: JSON.parse(data) as ForecastRun, automatic: row.automatic === 1 };
  }
  publish(run: ForecastRun, expectedVersion: number, automatic = false) {
    return this.storage.transactionSync(() => {
      const latest = this.latest();
      if (latest.version !== expectedVersion || latest.run && Date.parse(run.asOf) < Date.parse(latest.run.asOf)) return null;
      const version = expectedVersion + 1, data = JSON.stringify(run);
      this.storage.sql.exec('INSERT INTO needle_runs (version, asOf, automatic) VALUES (?, ?, ?)', version, run.asOf, automatic ? 1 : 0);
      let position = 0;
      for (let offset = 0; offset < data.length;) {
        let end = Math.min(data.length, offset + 65536);
        if (end < data.length && /[\uD800-\uDBFF]/.test(data[end - 1])) end--;
        this.storage.sql.exec('INSERT INTO needle_run_chunks (version, position, data) VALUES (?, ?, ?)', version, position++, data.slice(offset, end));
        offset = end;
      }
      return version;
    });
  }
}

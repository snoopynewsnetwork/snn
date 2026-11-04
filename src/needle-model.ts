// Outcome columns across races refer to the SAME simulation draw. This preserves
// shared national/regional errors instead of assuming marginal odds independent.
export type Caucus = 'D' | 'R' | 'O';
export interface ForecastRace {
  id: string;
  name: string;
  chamber: 'house' | 'senate' | 'governor';
  seatId: string;
  outcomes: string; // D/R/O caucus winner per joint draw; O means other/unresolved.
  margins?: number[]; // D-minus-R percentage points of all candidate votes.
}
export interface Seat { id: string; caucus: Caucus; sourceUrl?: string; basis?: 'not-up' | 'declared' | 'assumption' }
export interface ForecastRun {
  electionDate: '2026-11-03';
  modelVersion: string;
  asOf: string;
  calibrationUrl: string;
  assumptions: string[];
  races: ForecastRace[];
  fixedSeats: { house: Seat[]; senate: Seat[] };
  senateTieBreaker: 'D' | 'R';
}

export function independentSeatDistribution(probabilities: number[], fixed = 0): number[] {
  if (!Number.isSafeInteger(fixed) || fixed < 0) throw new Error('Invalid fixed seat count.');
  let distribution = Array(fixed + 1).fill(0); distribution[fixed] = 1;
  for (const p of probabilities) {
    if (!Number.isFinite(p) || p < 0 || p > 1) throw new Error('Invalid race probability.');
    const next = Array(distribution.length + 1).fill(0);
    distribution.forEach((mass, k) => { next[k] += mass * (1 - p); next[k + 1] += mass * p; });
    distribution = next;
  }
  return distribution;
}

export function summarizeRace(race: ForecastRace) {
  const n = race.outcomes.length;
  const probability = (party: string) => [...race.outcomes].filter(outcome => outcome === party).length / n;
  const margins = race.margins ? [...race.margins].sort((a, b) => a - b) : null;
  return { probabilities: { D: probability('D'), R: probability('R'), other: probability('O') },
    projectedMargin: margins ? margins.reduce((a, b) => a + b, 0) / n : null,
    marginInterval: margins ? [margins[Math.floor((n - 1) * .05)], margins[Math.ceil((n - 1) * .95)]] : null,
    simulationDraws: n, simulationStandardError: Math.sqrt(probability('D') * (1 - probability('D')) / n) };
}

export function chamberDistribution(races: ForecastRace[], fixed: Seat[], totalSeats: number, thresholds: { D: number; R: number }) {
  if (!Number.isSafeInteger(totalSeats) || totalSeats < 1 || [thresholds.D, thresholds.R].some(t => !Number.isSafeInteger(t) || t < 1 || t > totalSeats) || thresholds.D + thresholds.R <= totalSeats)
    throw new Error('Invalid or overlapping chamber control thresholds.');
  const n = races[0]?.outcomes.length ?? 1;
  if (fixed.length + races.length !== totalSeats || new Set([...fixed.map(s => s.id), ...races.map(r => r.seatId)]).size !== totalSeats)
    throw new Error('Chamber seat ledger is incomplete or duplicated.');
  if (races.some(r => r.outcomes.length !== n || !/^[DRO]+$/.test(r.outcomes))) throw new Error('Incoherent joint draws.');
  const distribution = { D: Array(totalSeats + 1).fill(0), R: Array(totalSeats + 1).fill(0) };
  const control = { D: 0, R: 0, other: 0 };
  for (let draw = 0; draw < n; draw++) {
    const counts = { D: fixed.filter(s => s.caucus === 'D').length, R: fixed.filter(s => s.caucus === 'R').length };
    for (const race of races) {
      const outcome = race.outcomes[draw];
      if (outcome === 'D' || outcome === 'R') counts[outcome]++;
    }
    distribution.D[counts.D] += 1 / n; distribution.R[counts.R] += 1 / n;
    if (counts.D >= thresholds.D) control.D++;
    else if (counts.R >= thresholds.R) control.R++;
    else control.other++;
  }
  const interval = (mass: number[]) => {
    const quantile = (p: number) => { let sum = 0; return mass.findIndex(value => (sum += value) >= p); };
    return [quantile(.05), quantile(.95)];
  };
  return { probabilities: { D: control.D / n, R: control.R / n, other: control.other / n },
    seatDistribution: distribution, seatInterval: { D: interval(distribution.D), R: interval(distribution.R) }, simulationDraws: n,
    simulationStandardError: Math.sqrt(control.D / n * (1 - control.D / n) / n) };
}

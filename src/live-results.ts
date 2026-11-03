import type { CandidateCount, ParsedMonitor } from "./monitor";

export interface Observation {
  target: string;
  status: string;
  margin: number | null;
  reporting: number | null;
  winner: string | null;
  gopSeats: number | null;
  cueState: string | null;
  sourceUrl: string;
  observedAt: string;
  body: string;
  version: number;
  updatedAt: string;
  sourceKind?: "official";
  sourceStatus?: string;
  totalVotes?: number;
}

export interface LiveResult extends Omit<ParsedMonitor, "status"> {
  race: string;
  status: ParsedMonitor["status"] | "error" | "pending";
  checkedAt?: string;
  lastSuccessAt?: string;
  lastResultChangedAt?: string;
  sourceUrl: string;
  sourceError?: string;
  sourceSnapshots?: { source: string; snapshotId?: number }[];
}

export const liveTargets = { kansas: "senate-ks", "north-carolina": "senate-nc" } as const;

// Project the current cumulative official snapshot into the desk's margin bands.
// This does not write to the versioned editor log or manufacture a race call.
export function withOfficialResults(manual: Observation[], live: LiveResult[], now = Date.now()): Observation[] {
  const automaticTargets = new Set<string>(live.map(result => liveTargets[result.race as keyof typeof liveTargets]).filter(Boolean));
  const observations = manual.filter(observation => !automaticTargets.has(observation.target));
  for (const result of live) {
    const target = liveTargets[result.race as keyof typeof liveTargets];
    const candidates: CandidateCount[] = result.candidates ?? [];
    const total = candidates.reduce((sum, candidate) => sum + candidate.votes, 0);
    const d = candidates.filter(candidate => candidate.party === "DEM"), r = candidates.filter(candidate => candidate.party === "REP");
    if (!target || !total || total !== result.totalVotes || !result.lastSuccessAt || d.length !== 1 || r.length !== 1) continue;
    const stale = result.status !== "reporting" || now - Date.parse(result.lastSuccessAt) > 15 * 60_000;
    observations.push({
      target, status: "unofficial", margin: (d[0].votes - r[0].votes) / total * 100,
      reporting: null, winner: null, gopSeats: null, cueState: null,
      sourceUrl: result.sourceUrl, observedAt: result.lastSuccessAt, updatedAt: result.lastSuccessAt,
      body: `${total.toLocaleString("en-US")} official Senate votes published. Margin is D minus R as a percentage of all candidate votes. ${stale ? "Source unavailable or stale; these are the last verified counts." : "Unofficial cumulative returns; no race call or vote-completion estimate."}`,
      version: 0, sourceKind: "official", sourceStatus: stale ? "stale" : "reporting", totalVotes: total,
    });
  }
  return observations;
}

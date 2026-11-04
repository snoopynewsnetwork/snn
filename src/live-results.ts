import type { CandidateCount, ParsedMonitor } from "./monitor";
import type { ElectionResult } from "./adapters/types";

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
  sourceKind?: "official" | "supplier";
  sourceStatus?: string;
  totalVotes?: number;
}

export interface LiveResult extends Omit<ElectionResult, "status"> {
  race: string;
  target?: string;
  name?: string;
  chamber?: "senate" | "house" | "governor" | "group";
  state?: string;
  status: ElectionResult["status"] | "error" | "pending";
  checkedAt?: string;
  lastSuccessAt?: string;
  lastResultChangedAt?: string;
  sourceUrl: string;
  sourceKind?: "official" | "supplier";
  sourceName?: string;
  authorityUrl?: string;
  sourceError?: string;
  sourceSnapshots?: { source: string; snapshotId?: number; url?: string }[];
  publications?: ParsedMonitor["publications"];
  gopSeats?: number;
  gopLeadingSeats?: number;
  members?: string[];
  countyResult?: LiveResult;
}

export const liveTargets = { kansas: "senate-ks", "north-carolina": "senate-nc" } as const;

export const groupMembers: Record<string, string[]> = {
  "house-fl-redraw": ["house-fl-09", "house-fl-14", "house-fl-22", "house-fl-25"],
  "house-tx-redraw": ["house-tx-09", "house-tx-28", "house-tx-32", "house-tx-34", "house-tx-35"],
  "house-pa-07-10": ["house-pa-07", "house-pa-10"],
};

export const targetFor = (result: LiveResult) => result.target ?? liveTargets[result.race as keyof typeof liveTargets];

export function hasValidCounts(result: LiveResult): boolean {
  const candidates = result.candidates ?? [];
  return candidates.length > 0 && candidates.every(candidate => Number.isSafeInteger(candidate.votes) && candidate.votes >= 0) &&
    Number.isSafeInteger(result.totalVotes) && candidates.reduce((sum, candidate) => sum + candidate.votes, 0) === result.totalVotes;
}

export function isFresh(result: LiveResult, now = Date.now()): boolean {
  const age = now - Date.parse(result.lastSuccessAt ?? "");
  return result.status === "reporting" && Number.isFinite(age) && age >= -60_000 && age <= 15 * 60_000;
}

export function withGroupResults(live: LiveResult[], now = Date.now()): LiveResult[] {
  const results = [...live];
  for (const [target, members] of Object.entries(groupMembers)) {
    const parts = members.map(id => live.find(result => targetFor(result) === id));
    const present = parts.filter((result): result is LiveResult => !!result);
    const available = parts.every(result => {
      const age = now - Date.parse(result?.lastSuccessAt ?? "");
      return result && ["setup", "reporting"].includes(result.status) && result.coverage !== "partial" &&
        Number.isFinite(age) && age >= -60_000 && age <= 15 * 60_000;
    });
    const reporting = available && present.some(result => result.status === "reporting");
    const gopSeats = present.filter(result => isFresh(result, now) && result.coverage !== "partial" && result.winner === "R").length;
    const gopLeadingSeats = present.filter(result => {
      if (!isFresh(result, now) || result.coverage === "partial" || !hasValidCounts(result)) return false;
      const r = result.candidates!.filter(candidate => candidate.party === "REP");
      return r.length === 1 && result.candidates!.every(candidate => candidate === r[0] || candidate.votes < r[0].votes);
    }).length;
    const dates = present.map(result => result.lastSuccessAt).filter((date): date is string => !!date).sort();
    const sources = present.flatMap(result => result.sourceSnapshots ?? []);
    results.push({
      race: target, target, chamber: "group", name: `${target.startsWith("house-fl") ? "Florida" : target.startsWith("house-tx") ? "Texas" : "Pennsylvania"} group`,
      status: available ? reporting ? "reporting" : "setup" : "unavailable", coverage: "complete", members,
      message: `${gopSeats} Republican wins explicitly declared by sources; ${gopLeadingSeats} current Republican leads. Leads do not count as seats won.${available ? reporting ? "" : " All member contests contain zero setup votes." : " Some member results are unavailable or stale."}`,
      gopSeats, gopLeadingSeats, checkedAt: present.map(result => result.checkedAt ?? "").sort().at(-1),
      lastSuccessAt: available && dates.length === members.length ? dates[0] : undefined,
      sourceUrl: present.find(result => result.sourceUrl)?.sourceUrl ?? "",
      sourceKind: present.some(result => result.sourceKind === "supplier") ? "supplier" : "official", sourceSnapshots: sources,
    });
  }
  return results;
}

// Project the current cumulative official snapshot into the desk's margin bands.
// This does not write to the versioned editor log or manufacture a race call.
export function withOfficialResults(manual: Observation[], live: LiveResult[], now = Date.now()): Observation[] {
  const automaticTargets = new Set<string>(live.map(targetFor).filter((target): target is string => !!target));
  const observations = manual.filter(observation => !automaticTargets.has(observation.target));
  for (const result of live) {
    const target = targetFor(result);
    if (!target || result.coverage === "partial") continue;
    const candidates: CandidateCount[] = result.candidates ?? [];
    const total = candidates.reduce((sum, candidate) => sum + candidate.votes, 0);
    const independent = target === "senate-ne";
    const d = candidates.filter(candidate => candidate.party === (independent ? "IND" : "DEM")), r = candidates.filter(candidate => candidate.party === "REP");
    const group = !!result.members;
    if (group && !isFresh(result, now)) continue;
    if (!result.lastSuccessAt || (!group && (!hasValidCounts(result) || !total || d.length !== 1 || r.length !== 1))) continue;
    const stale = !isFresh(result, now);
    const sourceKind = result.sourceKind ?? "official";
    observations.push({
      target, status: result.resultStatus ?? "unofficial", margin: group ? null : (d[0].votes - r[0].votes) / total * 100,
      reporting: null, winner: result.winner ?? null, gopSeats: group ? result.gopSeats ?? null : null, cueState: null,
      sourceUrl: result.sourceUrl, observedAt: result.lastSuccessAt, updatedAt: result.lastSuccessAt,
      body: group ? result.message : `${total.toLocaleString("en-US")} votes published by ${result.sourceName ?? (sourceKind === "official" ? "the official source" : "the live supplier")}. Margin is ${independent ? "I" : "D"} minus R as a percentage of all candidate votes. ${stale ? "Source unavailable or stale; these are the last verified counts." : "Cumulative returns; no vote-completion estimate. A lead alone is not a race call."}`,
      version: 0, sourceKind, sourceStatus: stale ? "stale" : "reporting", totalVotes: group ? undefined : total,
    });
  }
  return observations;
}

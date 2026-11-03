import type { CandidateCount } from "../monitor";
import type { ElectionResult, ElectionTarget } from "./types";

// Shared helpers for the northeast region adapters (OH MI PA NJ NY ME NH MS).
// Every snapshot is cumulative: parsers replace, never add, successive responses.

export const ELECTION_DAY = "2026-11-03";

export function count(value: unknown): number {
  if (typeof value === "number") {
    if (!Number.isSafeInteger(value) || value < 0) throw new Error("Invalid vote or precinct count.");
    return value;
  }
  const text = String(value ?? "").trim();
  if (!/^(?:0|[1-9]\d*|[1-9]\d{0,2}(?:,\d{3})+)$/.test(text)) throw new Error(`Invalid count ${JSON.stringify(text).slice(0, 40)}.`);
  const n = Number(text.replace(/,/g, ""));
  if (!Number.isSafeInteger(n)) throw new Error("Count exceeds supported range.");
  return n;
}

export class MissingSource extends Error {}

// Some publishers (PA) return a JSON string that itself contains JSON.
export function json(body: string | undefined, label: string): any {
  if (body === undefined) throw new MissingSource(`${label} response unavailable this cycle.`);
  if (/^\s*</.test(body)) throw new Error(`${label} returned HTML (access challenge or error page), not JSON.`);
  let data: unknown = JSON.parse(body);
  if (typeof data === "string") data = JSON.parse(data);
  if (data === null || typeof data !== "object") throw new Error(`${label} is not a JSON object.`);
  return data;
}

const parties: Record<string, string> = {
  D: "DEM", DEM: "DEM", DEMOCRATIC: "DEM", R: "REP", REP: "REP", REPUBLICAN: "REP",
  L: "LIB", LIB: "LIB", LBT: "LIB", LIBERTARIAN: "LIB", G: "GRE", GRE: "GRE", GRN: "GRE", GREEN: "GRE",
  I: "IND", IND: "IND", INDEPENDENT: "IND", WI: "WRITE-IN", "WRITE-IN": "WRITE-IN",
};
// Unknown publisher codes are kept literally rather than guessed.
export function party(code: string): string {
  const key = code.trim().toUpperCase();
  return parties[key] ?? (key || "NONE");
}

export function tally(
  candidates: CandidateCount[],
  extra: Omit<ElectionResult, "status" | "message" | "candidates" | "totalVotes"> & { label: string; partialNote?: string },
): ElectionResult {
  const { label, partialNote, ...rest } = extra;
  const totalVotes = candidates.reduce((sum, candidate) => sum + candidate.votes, 0);
  if (!totalVotes) return { ...rest, status: "setup", message: `Zero setup: ${label} has published no votes yet.`, candidates, totalVotes };
  const coverage = rest.coverage === "partial" ? ` Partial geography only — ${partialNote ?? "not a full-district total"}; do not read as the full-race margin.` : "";
  return {
    ...rest, status: "reporting", candidates, totalVotes,
    message: `${label}. Unofficial cumulative returns; may be revised. No race call.${coverage}`,
  };
}

export function unavailable(message: string): ElectionResult {
  return { status: "unavailable", message };
}

export function review(message: string, sourceUpdated?: string): ElectionResult {
  return { status: "review", message, sourceUpdated };
}

// Compute each target independently so one malformed contest cannot blank its siblings.
export function perTarget(
  targets: ElectionTarget[],
  fn: (target: ElectionTarget) => ElectionResult,
): Record<string, ElectionResult> {
  const out: Record<string, ElectionResult> = {};
  for (const target of targets) {
    try {
      out[target.id] = fn(target);
    } catch (error) {
      if (error instanceof MissingSource) { out[target.id] = unavailable(error.message); continue; }
      out[target.id] = review(`Source changed or failed validation; review required: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  return out;
}

// Exact candidate universe check: same names, each once, nothing extra.
export function requireUniverse(actual: string[], expected: string[], label: string): void {
  const a = [...actual].sort(), e = [...expected].sort();
  if (a.length !== e.length || a.some((name, i) => name !== e[i]))
    throw new Error(`${label} candidate universe changed (got ${a.join("; ")}).`);
}

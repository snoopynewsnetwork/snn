import type { CandidateCount } from "../monitor";
import type { ElectionResult, ElectionTarget } from "./types";

// Shared helpers for the southeast region adapters (FL GA SC NC VA KY IN).
// Every response is a cumulative snapshot: parsers replace, never add, successive responses.

export function count(value: unknown): number {
  if (typeof value === "number") {
    if (!Number.isSafeInteger(value) || value < 0) throw new Error("Invalid vote or precinct count.");
    return value;
  }
  const text = String(value ?? "").trim();
  if (!/^(?:0|[1-9]\d*)$/.test(text)) throw new Error(`Invalid count ${JSON.stringify(text).slice(0, 40)}.`);
  const n = Number(text);
  if (!Number.isSafeInteger(n)) throw new Error("Count exceeds supported range.");
  return n;
}

export function body(bodies: Record<string, string>, id: string): string {
  const text = bodies[id];
  if (text === undefined || text === "") throw new Error(`${id} response missing.`);
  if (/^\s*</.test(text)) throw new Error(`${id} returned HTML (access challenge or error page), not data.`);
  return text.replace(/^﻿/, "");
}

export function json(bodies: Record<string, string>, id: string): any {
  const data: unknown = JSON.parse(body(bodies, id));
  if (data === null || typeof data !== "object") throw new Error(`${id} is not a JSON object.`);
  return data;
}

const parties: Record<string, string> = {
  D: "DEM", DEM: "DEM", DEMOCRATIC: "DEM", R: "REP", REP: "REP", REPUBLICAN: "REP",
  L: "LIB", LIB: "LIB", LPF: "LIB", LIBERTARIAN: "LIB", G: "GRE", GRE: "GRE", GRN: "GRE", GREEN: "GRE",
  I: "IND", IND: "IND", INDEPENDENT: "IND", NPA: "NPA", WRI: "WRITE-IN", "WRITE-IN": "WRITE-IN",
};
// Unknown publisher codes are kept literally rather than guessed.
export function party(code: unknown): string {
  const key = String(code ?? "").trim().toUpperCase();
  return parties[key] ?? (key || "NONE");
}

export interface Expected { name: string; party: string }

// The published candidate universe must be exactly the pinned November ballot:
// a renamed, dropped or added choice means the contest changed and needs review.
// `optional` lists choices verified as certified write-ins that a publisher may add later.
export function exactUniverse(candidates: CandidateCount[], expected: Expected[], label: string, optional: Expected[] = []): void {
  const seen = new Set<string>();
  for (const candidate of candidates) {
    const key = `${candidate.name}|${candidate.party}`;
    if (seen.has(key)) throw new Error(`${label}: duplicate candidate ${candidate.name}.`);
    seen.add(key);
  }
  const want = new Set(expected.map(item => `${item.name}|${item.party}`));
  const allowed = new Set(optional.map(item => `${item.name}|${item.party}`));
  if ([...want].some(key => !seen.has(key)) || [...seen].some(key => !want.has(key) && !allowed.has(key)))
    throw new Error(`${label}: candidate configuration changed; review required.`);
}

export function tally(
  candidates: CandidateCount[],
  label: string,
  extra: Omit<ElectionResult, "status" | "message" | "candidates" | "totalVotes"> & { note?: string } = {},
): ElectionResult {
  const { note, ...rest } = extra;
  const totalVotes = candidates.reduce((sum, candidate) => sum + candidate.votes, 0);
  const suffix = note ? ` ${note}` : "";
  if (!totalVotes)
    return { ...rest, status: "setup", message: `Zero setup: ${label} has published no votes yet.${suffix}`, candidates, totalVotes };
  const stage = rest.resultStatus === "certified" ? "Certified results." : "Unofficial cumulative returns; may be revised. No race call.";
  return { ...rest, status: "reporting", message: `${label}. ${stage}${suffix}`, candidates, totalVotes };
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
      out[target.id] = {
        status: "review",
        message: `Source changed or failed validation; review required: ${error instanceof Error ? error.message : String(error)}`,
      };
    }
  }
  return out;
}

// Whole-feed identity failures (wrong election, test data, access challenge) apply to every target.
export function allTargets(targets: ElectionTarget[], result: ElectionResult): Record<string, ElectionResult> {
  return Object.fromEntries(targets.map(target => [target.id, result]));
}

export function guarded(
  targets: ElectionTarget[],
  identity: () => void,
  fn: (target: ElectionTarget) => ElectionResult,
): Record<string, ElectionResult> {
  try {
    identity();
  } catch (error) {
    return allTargets(targets, {
      status: "review",
      message: `Election identity check failed; no counts admitted: ${error instanceof Error ? error.message : String(error)}`,
    });
  }
  return perTarget(targets, fn);
}

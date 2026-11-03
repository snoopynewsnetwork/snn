import type { CandidateCount } from "../monitor";
import type { ElectionResult, ElectionTarget } from "./types";

// Shared helpers for the west region adapters (KS TX IA NE MN AZ CO WI MT CA).
// Every response is a cumulative snapshot: parsers replace, never add, successive responses.

// Some vendor CDNs (Clarity's CloudFront) reject requests without a User-Agent.
export const HEADERS = { "User-Agent": "Mozilla/5.0 (compatible; SNN-election-monitor/1.0)" };

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

export function text(bodies: Record<string, string>, id: string): string {
  const body = bodies[id];
  if (body === undefined || body === "") throw new Error(`${id} response missing.`);
  return body.replace(/^﻿/, "");
}

export function json(bodies: Record<string, string>, id: string): any {
  const body = text(bodies, id);
  if (/^\s*</.test(body)) throw new Error(`${id} returned HTML (access challenge or error page), not JSON.`);
  const data: unknown = JSON.parse(body);
  if (data === null || typeof data !== "object") throw new Error(`${id} is not JSON.`);
  return data;
}

export function base64Json(value: unknown, label: string): any {
  if (typeof value !== "string" || !/^[A-Za-z0-9+/]+=*$/.test(value)) throw new Error(`${label} is not base64.`);
  const bytes = Uint8Array.from(atob(value), char => char.charCodeAt(0));
  return JSON.parse(new TextDecoder().decode(bytes));
}

// Publisher party codes. DFL is Minnesota's Democratic party; Nebraska/Colorado
// petition and unaffiliated candidates appear on the ballot without a party.
// Unknown codes (FWD, UNI, LMN, AFP, ...) are kept literally rather than guessed.
const parties: Record<string, string> = {
  D: "DEM", DEM: "DEM", DFL: "DEM", R: "REP", REP: "REP",
  L: "LIB", LIB: "LIB", LBR: "LIB", LBT: "LIB", G: "GRE", GRE: "GRE", GRN: "GRE",
  I: "IND", IND: "IND", PET: "IND", UAF: "IND",
  W: "WRITE-IN", WI: "WRITE-IN", "WRITE-IN": "WRITE-IN",
};
export function party(code: unknown): string {
  const key = String(code ?? "").trim().toUpperCase();
  return parties[key] ?? (key || "NONE");
}

export function cleanName(name: unknown): string {
  return String(name ?? "").replace(/\s*\(I\)\s*$/, "").replace(/\s+/g, " ").trim();
}

export type Universe = [name: string, party: string][];

// The published candidate universe must be exactly the pinned November ballot:
// a renamed, dropped or added choice means the contest changed and needs review.
export function exactUniverse(candidates: CandidateCount[], expected: Universe, label: string): void {
  const got = candidates.map(c => `${c.name}|${c.party}`).sort();
  const want = expected.map(([name, p]) => `${name}|${p}`).sort();
  if (new Set(got).size !== got.length) throw new Error(`${label}: duplicate candidate rows.`);
  if (got.length !== want.length || got.some((key, i) => key !== want[i]))
    throw new Error(`${label}: candidate universe changed (got ${got.join("; ")}).`);
}

export function tally(
  candidates: CandidateCount[],
  extra: Omit<ElectionResult, "status" | "message" | "candidates" | "totalVotes"> & { label: string; note?: string },
): ElectionResult {
  const { label, note, ...rest } = extra;
  const totalVotes = candidates.reduce((sum, c) => sum + c.votes, 0);
  const suffix = note ? ` ${note}` : "";
  if (!totalVotes)
    return { ...rest, status: "setup", message: `Zero setup: ${label} has published no votes yet.${suffix}`, candidates, totalVotes };
  const partial = rest.coverage === "partial" ? " Partial geography only; do not read as the full-race margin." : "";
  return {
    ...rest, status: "reporting", resultStatus: "unofficial", candidates, totalVotes,
    message: `${label}. Unofficial cumulative returns; may be revised. No race call.${partial}${suffix}`,
  };
}

export function unavailable(message: string): ElectionResult {
  return { status: "unavailable", message };
}

function reason(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

// Whole-feed identity failures (wrong election, test data, access challenge) apply to
// every target of that adapter; contest failures are isolated per target.
export function guarded(
  targets: ElectionTarget[],
  identity: () => void,
  fn: (target: ElectionTarget) => ElectionResult,
): Record<string, ElectionResult> {
  try {
    identity();
  } catch (error) {
    const result: ElectionResult = { status: "review", message: `Election identity check failed; no counts admitted: ${reason(error)}` };
    return Object.fromEntries(targets.map(target => [target.id, result]));
  }
  const out: Record<string, ElectionResult> = {};
  for (const target of targets) {
    try {
      out[target.id] = fn(target);
    } catch (error) {
      out[target.id] = { status: "review", message: `Source changed or failed validation; review required: ${reason(error)}` };
    }
  }
  return out;
}

// Minimal RFC 4180 CSV reader (quoted fields, doubled quotes, CRLF).
export function csv(body: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [], field = "", quoted = false;
  for (let i = 0; i < body.length; i++) {
    const ch = body[i];
    if (quoted) {
      if (ch === '"' && body[i + 1] === '"') { field += '"'; i++; }
      else if (ch === '"') quoted = false;
      else field += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ",") { row.push(field); field = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && body[i + 1] === "\n") i++;
      row.push(field); field = "";
      if (row.some(cell => cell !== "")) rows.push(row);
      row = [];
    } else field += ch;
  }
  row.push(field);
  if (row.some(cell => cell !== "")) rows.push(row);
  return rows;
}

import type { CandidateCount } from "../monitor";

export interface ElectionSource {
  id: string;
  name: string;
  url: string;
  // Official authority page that publishes/links the endpoint.
  authorityUrl: string;
  official: boolean;
  maxBytes?: number;
  encoding?: "utf8" | "base64"; // Binary ZIP responses are supplied to parse as base64.
  method?: "GET" | "POST";
  body?: string;
  headers?: Record<string, string>;
  // Fetch this prerequisite first. {version} in url is replaced only by its
  // trimmed 1–12 digit response (Clarity's current_ver.txt feeds).
  dependsOn?: string;
}

export interface ElectionTarget {
  id: string; // Existing guide id, e.g. senate-fl or house-fl-14; extra group members may use house-tx-09.
  state: string; // Two-letter USPS code.
  name: string;
  chamber: "senate" | "house" | "governor";
  district?: string;
  // Source used for displayed provenance. Must exist in adapter.sources.
  sourceId?: string;
}

export interface ElectionResult {
  // Optional winning source when a parser selects a fallback. Must be one of
  // this adapter's source ids; provenance follows the selected source.
  sourceId?: string;
  status: "waiting" | "setup" | "reporting" | "review" | "unavailable";
  message: string;
  candidates?: CandidateCount[]; // DEM / REP / LIB / GRE / IND / other literal parties normalized where known.
  totalVotes?: number;
  reportedPrecincts?: number;
  totalPrecincts?: number;
  sourceUpdated?: string;
  sourceSubmitted?: string;
  // Only explicit source declarations of a winner may set this. A lead/100% precincts is not a call.
  winner?: "D" | "R" | "I" | "other";
  resultStatus?: "unofficial" | "certified";
  coverage?: "complete" | "partial";
}

export interface ElectionAdapter {
  id: string;
  version: string;
  sources: ElectionSource[];
  targets: ElectionTarget[];
  // Parse pinned November 3, 2026 source responses; never fetch from inside parse.
  // May be async for decompression. Missing/invalid contest data must throw or return an explicit unavailable result.
  parse: (bodies: Record<string, string>) => Record<string, ElectionResult> | Promise<Record<string, ElectionResult>>;
}

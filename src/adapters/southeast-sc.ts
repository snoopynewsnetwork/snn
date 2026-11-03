import type { CandidateCount } from "../monitor";
import type { ElectionAdapter, ElectionResult, ElectionTarget } from "./types";
import { body, count, exactUniverse, guarded, json, party, type Expected } from "./southeast-common.ts";

// South Carolina State Election Commission ENR (Clarity on enr-scvotes.org).
// scvotes.gov/elections-statistics/election-results/ links "Statewide General Election"
// to election 127300. current_ver.txt names the live version; summary.json is the
// cumulative statewide contest snapshot for that version.
const ELECTION = "127300";
const BASE = `https://www.enr-scvotes.org/SC/${ELECTION}`;
const AUTHORITY = "https://scvotes.gov/elections-statistics/election-results/";

// Contest keys and ballots observed in the live November 3, 2026 setup summary
// (version 382659), matching the SEC candidate tracker's active candidates.
interface Contest { key: string; name: string; candidates: Expected[] }

export const scContests: Record<string, Contest> = {
  "senate-sc": { key: "26000", name: "U.S. Senate", candidates: [
    { name: "Darline Graham", party: "REP" }, { name: "Kasie Whitener", party: "LIB" }, { name: "Annie Andrews", party: "DEM" },
    { name: "Mark Hackett", party: "CON" }, { name: "Write-In", party: "WRITE-IN" }] },
  "house-sc-01": { key: "27002", name: "U.S. House of Representatives, District 1", candidates: [
    { name: "Jenny Costa Honeycutt", party: "REP" }, { name: "Bill Reeside", party: "LIB" }, { name: "Nancy Lacore", party: "DEM" },
    { name: "Write-In", party: "WRITE-IN" }] },
  "house-sc-02": { key: "27004", name: "U.S. House of Representatives, District 2", candidates: [
    { name: "Joe Wilson", party: "REP" }, { name: "Zyon Khalifa", party: "DEM" }, { name: "Dayna Alane Smith", party: "WRK" },
    { name: "Write-In", party: "WRITE-IN" }] },
};

const squash = (text: unknown) => String(text ?? "").replace(/\s+/g, " ").trim();

export function scContest(summary: any[], spec: Contest): ElectionResult {
  const matched = summary.filter(item => item?.K === spec.key);
  if (matched.length !== 1) throw new Error(`${spec.name} (${spec.key}) missing or duplicated.`);
  const item = matched[0];
  if (squash(item.C) !== spec.name || item.VF !== 1 || !Array.isArray(item.CH) || !Array.isArray(item.P) || !Array.isArray(item.V) ||
      item.CH.length !== item.P.length || item.CH.length !== item.V.length || item.IsRCV)
    throw new Error(`${spec.name} identity or layout changed.`);
  const candidates: CandidateCount[] = item.CH.map((choice: unknown, i: number) => {
    const code = squash(item.P[i]), literal = squash(choice);
    return {
      // General-election choices are printed "REP Jane Doe"; drop the duplicated party prefix.
      name: literal.startsWith(`${code} `) ? literal.slice(code.length + 1) : literal,
      party: /^write-?ins?$/i.test(literal) ? "WRITE-IN" : party(code),
      votes: count(item.V[i]),
    };
  });
  exactUniverse(candidates, spec.candidates, spec.name);
  const totalVotes = candidates.reduce((sum, candidate) => sum + candidate.votes, 0);
  const base = { candidates, totalVotes, coverage: "complete" as const, resultStatus: "unofficial" as const };
  // Clarity's statewide TP/PR count counties, not precincts, and are not a vote-completion measure.
  const units = Number.isSafeInteger(item.TP) && Number.isSafeInteger(item.PR) ? ` ${item.PR} of ${item.TP} counties marked complete.` : "";
  return totalVotes
    ? { ...base, status: "reporting", message: `SC Election Commission statewide contest totals. Unofficial cumulative returns; may be revised. No race call.${units}` }
    : { ...base, status: "setup", message: `Zero setup: SC Election Commission has published no votes for this contest yet.${units}` };
}

const targets: ElectionTarget[] = [
  { id: "senate-sc", state: "SC", name: "South Carolina U.S. Senate", chamber: "senate", sourceId: "sc-summary" },
  { id: "house-sc-01", state: "SC", name: "SC-01", chamber: "house", district: "01", sourceId: "sc-summary" },
  { id: "house-sc-02", state: "SC", name: "SC-02", chamber: "house", district: "02", sourceId: "sc-summary" },
];

export const southCarolina: ElectionAdapter = {
  id: "southeast-sc",
  version: "2026-11-03.1",
  sources: [
    { id: "sc-version", name: "SC ENR current version", url: `${BASE}/current_ver.txt`, authorityUrl: AUTHORITY, official: true, maxBytes: 64 },
    { id: "sc-settings", name: "SC ENR election settings", url: `${BASE}/{version}/json/en/electionsettings.json`, authorityUrl: AUTHORITY, official: true, dependsOn: "sc-version", maxBytes: 2_000_000 },
    { id: "sc-summary", name: "SC ENR statewide summary", url: `${BASE}/{version}/json/en/summary.json`, authorityUrl: AUTHORITY, official: true, dependsOn: "sc-version", maxBytes: 4_000_000 },
  ],
  targets,
  parse(bodies) {
    let summary: any[] = [], updated: string | undefined;
    return guarded(targets, () => {
      if (!/^\d{1,12}$/.test(body(bodies, "sc-version").trim())) throw new Error("Version pointer invalid.");
      const settings = json(bodies, "sc-settings");
      const details = settings.settings?.electiondetails;
      if (details?.electionid !== ELECTION || details.electiondate !== "11/3/2026")
        throw new Error("Not the November 3, 2026 statewide general election.");
      // Clarity has emitted this flag both as a boolean and as a string.
      if (String(details.istestmode) !== "false" || details.showtestdatawatermark !== "0") throw new Error("Publisher is in test mode.");
      updated = typeof settings.websiteupdatedat === "string" ? settings.websiteupdatedat : undefined;
      const data = json(bodies, "sc-summary");
      if (!Array.isArray(data) || !data.length) throw new Error("Summary is not a nonempty contest array.");
      summary = data;
    }, target => ({ ...scContest(summary, scContests[target.id]), sourceUpdated: updated }));
  },
};

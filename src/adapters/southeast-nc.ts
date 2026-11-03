import type { CandidateCount } from "../monitor";
import type { ElectionAdapter, ElectionResult, ElectionTarget } from "./types";
import { count, exactUniverse, guarded, json, type Expected } from "./southeast-common.ts";

// NCSBE election-night reporting. One statewide results file carries the Senate
// and every US House contest with contest-level precinct status, so a single
// cumulative snapshot serves all North Carolina targets without any summing.
const AUTHORITY = "https://www.ncsbe.gov/results-data/election-results";

interface Contest { gid: string; name: string; candidates: Expected[] }

// Contest group IDs and ballots observed in the live November 3, 2026 setup file.
export const ncContests: Record<string, Contest> = {
  "senate-nc": { gid: "1383", name: "US SENATE (VOTE FOR 1)", candidates: [
    { name: "Michael Dublin", party: "GRE" }, { name: "Roy Cooper", party: "DEM" },
    { name: "Shannon W. Bray", party: "LIB" }, { name: "Michael Whatley", party: "REP" }] },
  "house-nc-01": { gid: "1369", name: "US HOUSE OF REPRESENTATIVES DISTRICT 01 (VOTE FOR 1)", candidates: [
    { name: "Don Davis", party: "DEM" }, { name: "Laurie Buckhout", party: "REP" }, { name: "Tom Bailey", party: "LIB" }] },
  "house-nc-05": { gid: "1373", name: "US HOUSE OF REPRESENTATIVES DISTRICT 05 (VOTE FOR 1)", candidates: [
    { name: "Virginia Foxx", party: "REP" }, { name: "Robert B. Luffman", party: "LIB" }, { name: "Chuck Hubbard", party: "DEM" }] },
  "house-nc-09": { gid: "1377", name: "US HOUSE OF REPRESENTATIVES DISTRICT 09 (VOTE FOR 1)", candidates: [
    { name: "Richard N. Ojeda II", party: "DEM" }, { name: "Richard Hudson", party: "REP" }] },
  "house-nc-11": { gid: "1379", name: "US HOUSE OF REPRESENTATIVES DISTRICT 11 (VOTE FOR 1)", candidates: [
    { name: "Jennifer Capps Balkcom", party: "REP" }, { name: "Jamie Ager", party: "DEM" }, { name: "Travis Groo", party: "LIB" }] },
};

const rows = (data: unknown, label: string): Record<string, unknown>[] => {
  if (!Array.isArray(data) || !data.length || data.some(row => !row || typeof row !== "object"))
    throw new Error(`${label}: expected a nonempty JSON array.`);
  return data;
};

const targets: ElectionTarget[] = [
  { id: "senate-nc", state: "NC", name: "North Carolina U.S. Senate", chamber: "senate", sourceId: "nc-results" },
  ...["01", "05", "09", "11"].map(district => ({
    id: `house-nc-${district}`, state: "NC", name: `NC-${district}`, chamber: "house" as const, district, sourceId: "nc-results",
  })),
];

function contest(all: Record<string, unknown>[], spec: Contest): ElectionResult {
  const matched = all.filter(row => row.gid === spec.gid);
  if (!matched.length) throw new Error(`Contest ${spec.gid} missing.`);
  if (matched.some(row => row.cnm !== spec.name || row.cid !== "0" || row.lid !== spec.gid || row.vfr !== "1"))
    throw new Error(`Contest ${spec.gid} identity changed.`);
  const writeIns = matched.filter(row => /write.?in/i.test(String(row.bnm)));
  const candidates: CandidateCount[] = matched.map(row => {
    const candidate = {
      name: String(row.bnm), party: /write.?in/i.test(String(row.bnm)) ? "WRITE-IN" : String(row.pty),
      votes: count(row.vct), electionDay: count(row.evc), early: count(row.ovc), mail: count(row.avc), provisional: count(row.pvc),
    };
    if (candidate.votes !== candidate.electionDay + candidate.early + candidate.mail + candidate.provisional)
      throw new Error(`${candidate.name}: voting-method counts do not reconcile.`);
    return candidate;
  });
  // Aggregate write-ins are a legitimate added row on election night; named ballot choices must not change.
  exactUniverse(candidates.filter(candidate => candidate.party !== "WRITE-IN"), spec.candidates, spec.name);
  if (writeIns.length > 1) throw new Error("Multiple write-in rows; review required.");
  const reported = new Set(matched.map(row => `${row.prt}/${row.ptl}`));
  if (reported.size !== 1) throw new Error("Inconsistent contest precinct status.");
  const reportedPrecincts = count(matched[0].prt), totalPrecincts = count(matched[0].ptl);
  if (!totalPrecincts || reportedPrecincts > totalPrecincts) throw new Error("Invalid precinct reporting status.");
  const totalVotes = candidates.reduce((sum, candidate) => sum + candidate.votes, 0);
  const base = { candidates, totalVotes, reportedPrecincts, totalPrecincts, coverage: "complete" as const, resultStatus: "unofficial" as const };
  return totalVotes
    ? { ...base, status: "reporting", message: "NCSBE contest totals across all counties. Unofficial election-night counts; may be revised. No race call. Precincts reporting is not a vote-completion estimate." }
    : { ...base, status: "setup", message: "Zero setup: NCSBE has published no votes for this contest yet." };
}

export const northCarolina: ElectionAdapter = {
  id: "southeast-nc",
  version: "2026-11-03.1",
  sources: [
    { id: "nc-elections", name: "NCSBE election catalog", url: "https://er.ncsbe.gov/enr/elections.txt", authorityUrl: AUTHORITY, official: true },
    { id: "nc-counties", name: "NCSBE county status", url: "https://er.ncsbe.gov/enr/20261103/data/county.txt", authorityUrl: AUTHORITY, official: true },
    { id: "nc-results", name: "NCSBE statewide contest results", url: "https://er.ncsbe.gov/enr/20261103/data/results_0.txt", authorityUrl: AUTHORITY, official: true, maxBytes: 2_000_000 },
  ],
  targets,
  parse(bodies) {
    let counties: Record<string, unknown>[] = [], all: Record<string, unknown>[] = [];
    let state: Record<string, unknown> | undefined;
    return guarded(targets, () => {
      if (!rows(json(bodies, "nc-elections"), "catalog").some(row => row.edt === "11/03/2026" && row.con === "1"))
        throw new Error("November 3, 2026 election missing from the official catalog.");
      counties = rows(json(bodies, "nc-counties"), "county status");
      if (counties.length !== 101 || new Set(counties.map(row => row.cid)).size !== 101 ||
          counties.some(row => !String(row.tle).startsWith("11/03/2026 ") || !/GENERAL ELECTION/.test(String(row.tle)) || /TEST|MOCK/i.test(String(row.tle))))
        throw new Error("County coverage or election identity changed.");
      state = counties.find(row => row.cid === "0" && row.cnm === "STATE");
      if (!state) throw new Error("Statewide status record missing.");
      all = rows(json(bodies, "nc-results"), "results");
    }, target => ({
      ...contest(all, ncContests[target.id]),
      sourceUpdated: String(state!.imp), sourceSubmitted: String(state!.sub),
    }));
  },
};

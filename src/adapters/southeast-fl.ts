import type { CandidateCount } from "../monitor";
import type { ElectionAdapter, ElectionResult, ElectionTarget } from "./types";
import { body, count, exactUniverse, guarded, party, type Expected } from "./southeast-common.ts";

// Florida Division of Elections election-night results file, linked from
// floridaelectionwatch.gov/Downloads. One tab-delimited row per county x candidate;
// each county row is that county's cumulative contest total, so a district or state
// total is the sum across distinct counties within this one snapshot only.
const HEADER = "ElectionDate\tPartyCode\tPartyName\tRaceCode\tRaceName\tCountyCode\tCountyName\tJuris1num\tJuris2num\tPrecincts\tPrecinctsReporting\tCanNameLast\tCanNameFirst\tCanNameMiddle\tCanVotes";
const ALL_COUNTIES = ["ALA", "BAK", "BAY", "BRA", "BRE", "BRO", "CAL", "CHA", "CIT", "CLA", "CLL", "CLM", "DAD", "DES", "DIX", "DUV", "ESC",
  "FLA", "FRA", "GAD", "GIL", "GLA", "GUL", "HAM", "HAR", "HEN", "HER", "HIG", "HIL", "HOL", "IND", "JAC", "JEF", "LAF", "LAK", "LEE",
  "LEO", "LEV", "LIB", "MAD", "MAN", "MON", "MRN", "MRT", "NAS", "OKA", "OKE", "ORA", "OSC", "PAL", "PAS", "PIN", "POL", "PUT", "SAN",
  "SAR", "SEM", "STJ", "STL", "SUM", "SUW", "TAY", "UNI", "VOL", "WAK", "WAL", "WAS"];

interface Contest { race: string; district: string; name: string; counties: string[]; candidates: Expected[] }

// Contest, county scope and ballot observed in the November 3, 2026 setup file.
export const flContests: Record<string, Contest> = {
  "senate-fl": { race: "USS", district: "", name: "United States Senator", counties: ALL_COUNTIES, candidates: [
    { name: "Ashley Moody", party: "REP" }, { name: "Angie Nixon", party: "DEM" }, { name: "Neil J. Gillespie", party: "NPA" }] },
  "governor-fl": { race: "GOV", district: "", name: "Governor and Lieutenant Governor", counties: ALL_COUNTIES, candidates: [
    { name: "Donalds / Avila", party: "REP" }, { name: "Jolly / Graham", party: "DEM" }, { name: "Jewett / Skelly", party: "LIB" },
    { name: "Abrams / Van Vactor", party: "NPA" }, { name: "Burkett / Coto", party: "NPA" }, { name: "Datto / Santana", party: "NPA" },
    { name: "Dimanche / Rojas", party: "NPA" }, { name: "Russo / Rodriguez", party: "NPA" },
    { name: "Anderson / Nokovich", party: "WRITE-IN" }, { name: "Morris / Alaways", party: "WRITE-IN" }] },
  "house-fl-07": { race: "USR", district: "007", name: "Representative in Congress, District 7", counties: ["SEM", "VOL"], candidates: [
    { name: "Bale Dalton", party: "DEM" }, { name: "Christopher Dennison", party: "LIB" }, { name: "Ryan Elijah", party: "REP" }] },
  "house-fl-09": { race: "USR", district: "009", name: "Representative in Congress, District 9", counties: ["GLA", "HIG", "IND", "OKE", "ORA", "OSC", "POL"], candidates: [
    { name: "Darren Soto", party: "DEM" }, { name: "Dan Green", party: "REP" }] },
  "house-fl-14": { race: "USR", district: "014", name: "Representative in Congress, District 14", counties: ["HIL"], candidates: [
    { name: "Kathy Castor", party: "DEM" }, { name: "Brian Lambert", party: "LIB" }, { name: "Mike Beltran", party: "REP" },
    { name: "Keith Varian", party: "WRITE-IN" }, { name: "Salomon Hernandez", party: "WRITE-IN" }] },
  "house-fl-22": { race: "USR", district: "022", name: "Representative in Congress, District 22", counties: ["BRO", "CLL", "HEN", "PAL"], candidates: [
    { name: "Pia Dandiya", party: "DEM" }, { name: "Casey Askar", party: "REP" }] },
  "house-fl-25": { race: "USR", district: "025", name: "Representative in Congress, District 25", counties: ["BRO", "DAD", "PAL"], candidates: [
    { name: "Jared Moskowitz", party: "DEM" }, { name: "Peter Jassenoff", party: "LIB" }, { name: "Scott Singer", party: "REP" },
    { name: "Michaelangelo Hamilton", party: "WRITE-IN" }] },
  "house-fl-27": { race: "USR", district: "027", name: "Representative in Congress, District 27", counties: ["DAD"], candidates: [
    { name: "Eliott Rodriguez", party: "DEM" }, { name: "Maria Elvira Salazar", party: "REP" }] },
};

type Row = Record<string, string>;

export function flRows(text: string, electionDate: string): Row[] {
  const lines = text.replace(/\r/g, "").split("\n").filter(line => line.length);
  if (lines[0] !== HEADER) throw new Error("Results file layout changed.");
  const columns = HEADER.split("\t");
  const rows = lines.slice(1).map(line => {
    const cells = line.split("\t");
    if (cells.length !== columns.length) throw new Error("Malformed results row.");
    return Object.fromEntries(columns.map((column, i) => [column, cells[i]]));
  });
  if (!rows.length || rows.some(row => row.ElectionDate !== electionDate)) throw new Error(`File is not the ${electionDate} election.`);
  return rows;
}

// Gubernatorial tickets put the governor in First and the running mate in Last with a "/" middle.
const displayName = (row: Row) => row.CanNameMiddle.trim() === "/"
  ? `${row.CanNameFirst.trim()} / ${row.CanNameLast.trim()}`
  : [row.CanNameFirst, row.CanNameMiddle, row.CanNameLast].map(part => part.trim()).filter(Boolean).join(" ");

export function flContest(rows: Row[], spec: Contest): ElectionResult {
  const matched = rows.filter(row => row.RaceCode === spec.race && row.Juris1num.trim() === spec.district);
  if (!matched.length) throw new Error(`${spec.name} missing.`);
  if (matched.some(row => row.RaceName !== spec.name)) throw new Error(`${spec.race} ${spec.district} contest name changed.`);
  const byCounty = new Map<string, Row[]>();
  for (const row of matched) byCounty.set(row.CountyCode, [...(byCounty.get(row.CountyCode) ?? []), row]);
  const counties = [...byCounty.keys()].sort();
  if (counties.join() !== [...spec.counties].sort().join()) throw new Error(`${spec.name} county scope changed.`);
  const totals = new Map<string, CandidateCount>();
  let reportedPrecincts = 0, totalPrecincts = 0;
  for (const [county, countyRows] of byCounty) {
    const status = new Set(countyRows.map(row => `${row.PrecinctsReporting}/${row.Precincts}`));
    if (status.size !== 1) throw new Error(`${county}: inconsistent precinct status.`);
    const reported = count(countyRows[0].PrecinctsReporting), total = count(countyRows[0].Precincts);
    if (!total || reported > total) throw new Error(`${county}: invalid precinct status.`);
    reportedPrecincts += reported; totalPrecincts += total;
    const names = new Set<string>();
    for (const row of countyRows) {
      const name = displayName(row), key = `${name}|${party(row.PartyCode)}`;
      if (names.has(key)) throw new Error(`${county}: duplicate candidate row.`);
      names.add(key);
      const entry = totals.get(key) ?? { name, party: party(row.PartyCode), votes: 0 };
      entry.votes += count(row.CanVotes);
      totals.set(key, entry);
    }
    if (names.size !== spec.candidates.length) throw new Error(`${county}: candidate rows incomplete.`);
  }
  const candidates = [...totals.values()];
  exactUniverse(candidates, spec.candidates, spec.name);
  const totalVotes = candidates.reduce((sum, candidate) => sum + candidate.votes, 0);
  const base = { candidates, totalVotes, reportedPrecincts, totalPrecincts, coverage: "complete" as const, resultStatus: "unofficial" as const };
  const scope = `${counties.length} ${counties.length === 1 ? "county" : "counties"}`;
  return totalVotes
    ? { ...base, status: "reporting", message: `Florida Division of Elections county returns (${scope}, compiled in one statewide file). Unofficial election-night counts; may be revised. No race call. Precincts reporting is not a vote-completion estimate.` }
    : { ...base, status: "setup", message: `Zero setup: Florida Division of Elections has published no votes for this contest yet (${scope}).` };
}

const targets: ElectionTarget[] = [
  { id: "senate-fl", state: "FL", name: "Florida U.S. Senate (special)", chamber: "senate", sourceId: "fl-results" },
  { id: "governor-fl", state: "FL", name: "Florida Governor", chamber: "governor", sourceId: "fl-results" },
  ...["07", "09", "14", "22", "25", "27"].map(district => ({
    id: `house-fl-${district}`, state: "FL", name: `FL-${district}`, chamber: "house" as const, district, sourceId: "fl-results",
  })),
];

export const florida: ElectionAdapter = {
  id: "southeast-fl",
  version: "2026-11-03.1",
  sources: [{
    id: "fl-results", name: "Florida Division of Elections election-night results file",
    url: "https://flelectionfiles.floridados.gov/enightfilespublic/20261103_ElecResultsFL.txt",
    authorityUrl: "https://floridaelectionwatch.gov/Downloads", official: true, maxBytes: 4_000_000,
  }],
  targets,
  parse(bodies) {
    let rows: Row[] = [];
    return guarded(targets, () => { rows = flRows(body(bodies, "fl-results"), "11/03/2026"); },
      target => flContest(rows, flContests[target.id]));
  },
};

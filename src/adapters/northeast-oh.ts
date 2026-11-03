import type { CandidateCount } from "../monitor";
import type { ElectionAdapter, ElectionResult, ElectionTarget } from "./types";
import { count, json, party, perTarget, requireUniverse, review, tally, unavailable } from "./northeast-common.ts";
import { CNN_SENATE_LIST, cnnSource, withCnnFallback, type CnnRace } from "./northeast-cnn.ts";

// Ohio Secretary of State "Ohio Decides" election-night API. The live page
// (https://liveresults.ohiosos.gov/) calls these JSON routes; the NIST 1500-100
// XML download carries the election identity and the IsTest flag.
const API = "https://liveresults.ohiosos.gov/Api/v1";
const AUTHORITY = "https://liveresults.ohiosos.gov/";

const SENATE_ID = "_55A742EA56A709A3E0633390EE0AE290";
const SENATE = ["Sherrod Brown", "Jon Husted", "Greg Levy", "William B. Redpath", "Stephen Faris", "Anthony Holliman", "Timothy Telymonde"];

// Contest object IDs and full ballot universes (incl. certified write-ins) from the
// November 3, 2026 contest catalog and district summary observed 2026-11-03.
// `cnn` is CNN's universe for the same race: ballot candidates only, without Ohio's certified write-ins.
const HOUSE: Record<string, { id: string; candidates: string[]; cnn: string[] }> = {
  "01": { id: "_55A742EA574909A3E0633390EE0AE290", candidates: ["Eric Conroy", "Greg Landsman", "Nathan Weise"], cnn: ["Greg Landsman", "Eric Conroy", "Nathan Weise"] },
  "07": { id: "_55A742EA571A09A3E0633390EE0AE290", candidates: ["Thahbia Asad", "Andrey Joseph Martinichin", "Max Miller", "Brian Poindexter"], cnn: ["Brian Poindexter", "Max Miller"] },
  "09": { id: "_55A742EA577809A3E0633390EE0AE290", candidates: ["Marcy Kaptur", "Kathy McKinstry", "Derek Merrin"], cnn: ["Marcy Kaptur", "Derek Merrin"] },
  "10": { id: "_55A742EA571009A3E0633390EE0AE290", candidates: ["Kristina Knickerbocker", "Thomas F. McMasters", "Mike Turner"], cnn: ["Kristina Knickerbocker", "Mike Turner", "Thomas McMasters"] },
  "13": { id: "_55A742EA572F09A3E0633390EE0AE290", candidates: ["Carey Coleman", "Sandeep Dixit", "Emilia Sykes"], cnn: ["Emilia Sykes", "Carey Coleman", "Sandeep Dixit"] },
};
const SENATE_CNN = ["Sherrod Brown", "Jon Husted", "Greg Levy", "William Redpath"];
// CNN 2026-SP-OH, observed 2026-11-03: polls open 12:00Z Nov 3, close 00:30Z Nov 4 (7:30 p.m. ET).
const SENATE_SPECIAL = {
  raceTitle: "Senate Special Election", pollsOpen: 1793707200000, pollsClose: 1793752200000, listSource: CNN_SENATE_LIST.id,
  parties: { "Sherrod Brown": "DEM", "Jon Husted": "REP", "Greg Levy": "IND", "William Redpath": "LIB" },
};
const cnnKey = (target: ElectionTarget) => target.chamber === "senate" ? "2026-SP-OH" : `2026-HG-OH-${Number(target.district)}`;

const targets: ElectionTarget[] = [
  { id: "senate-oh", state: "OH", name: "Ohio U.S. Senate (unexpired term)", chamber: "senate", sourceId: "oh-senate" },
  ...Object.keys(HOUSE).map(district => ({
    id: `house-oh-${district}`, state: "OH", name: `Ohio Congressional District ${district}`, chamber: "house" as const, district, sourceId: "oh-house",
  })),
];

interface Gate { isTest: boolean; generated?: string }

// Election identity comes from the XML root; only the opening tags are inspected.
export function ohioGate(xml: string | undefined): Gate {
  if (xml === undefined) throw new Error("Ohio XML identity file missing; cannot verify non-test status.");
  const root = xml.match(/<ElectionReport\b[^>]*>/)?.[0];
  const election = xml.match(/<Election\b[^>]*\bDate="([^"]+)"[^>]*\bType="([^"]+)"/);
  if (!root || !/IssuerAbbreviation="OH"/.test(root)) throw new Error("Ohio XML is not an Ohio ElectionReport.");
  if (!election || election[1] !== "2026-11-03" || election[2] !== "General") throw new Error("Ohio XML is not the November 3, 2026 general election.");
  const isTest = root.match(/\bIsTest="(true|false)"/)?.[1];
  if (!isTest) throw new Error("Ohio XML test flag missing.");
  return { isTest: isTest === "true", generated: root.match(/\bGeneratedDate="([^"]+)"/)?.[1] };
}

function candidates(rows: any[], expected: string[], label: string): CandidateCount[] {
  if (!Array.isArray(rows)) throw new Error(`${label} candidate list missing.`);
  requireUniverse(rows.map(row => String(row.primaryCandidate)), expected, label);
  return rows.map(row => {
    const votes = count(row.voteCount);
    if (count(row.vCount) !== votes) throw new Error(`${label} vote fields disagree.`);
    return { name: String(row.primaryCandidate), party: row.isWriteIn === true ? "WRITE-IN" : party(String(row.candidateParty)), votes };
  });
}

function stat(stats: any[], name: string): string | undefined {
  return stats.find(item => item?.name === name)?.value;
}

function withGate(gate: Gate, result: ElectionResult): ElectionResult {
  if (!gate.isTest) return { ...result, resultStatus: result.status === "reporting" ? "unofficial" : undefined };
  // Ohio's XML still carried IsTest=true on Election Day morning. Zero setup may be shown;
  // nonzero counts under a test flag are rejected outright.
  if (result.status === "reporting")
    return review("Ohio XML still flags IsTest=true while the JSON shows votes; test returns rejected until the publisher clears the flag.", gate.generated);
  return { ...result, message: `${result.message} Publisher XML still flags this file as a test (IsTest=true).` };
}

function parseOfficial(bodies: Record<string, string>): Record<string, ElectionResult> {
  let gate: Gate;
  try {
    gate = ohioGate(bodies["oh-xml"]);
  } catch (error) {
    const message = `Ohio identity gate failed: ${error instanceof Error ? error.message : String(error)}`;
    return Object.fromEntries(targets.map(target => [target.id, unavailable(message)]));
  }
  return perTarget(targets, target => {
    if (target.chamber === "senate") {
      const data = json(bodies["oh-senate"], "Ohio Senate");
      if (data.isPrimaryElection !== false || !Array.isArray(data.contestList) || data.contestList.length !== 1) throw new Error("Ohio Senate contest shape changed.");
      const contest = data.contestList[0];
      if (contest.objectId !== SENATE_ID || contest.linkText !== "U.S. Senator - Unexpired Term Ending 01/03/2029") throw new Error("Ohio Senate contest identity changed.");
      const stats = data.contestStatistics?.allStatistics ?? [];
      const reported = stat(stats, "Election Day Precincts Reporting")?.match(/^([\d,]+) \(/)?.[1];
      const total = stat(stats, "Total Number of Election Day Precincts");
      const result = tally(candidates(contest.candidatesRunning, SENATE, "Ohio Senate"), {
        label: "Ohio SOS statewide U.S. Senate totals (election-night write-ins may be unavailable)",
        reportedPrecincts: reported ? count(reported) : undefined, totalPrecincts: total ? count(total) : undefined,
        coverage: "complete",
      });
      return { ...withGate(gate, result), sourceId: "oh-senate" };
    }
    const spec = HOUSE[target.district!];
    const data = json(bodies["oh-house"], "Ohio Congress");
    if (data.isPrimaryElection !== false || !Array.isArray(data.contestList)) throw new Error("Ohio Congress summary shape changed.");
    const label = `Representative to Congress - District ${target.district}`;
    const rows = data.contestList.filter((row: any) => row.name === label);
    if (rows.length !== 1 || rows[0].objectId !== spec.id) throw new Error(`${label} missing, duplicated or re-identified.`);
    const list = candidates(rows[0].candidatesRunning, spec.candidates, label);
    if (count(rows[0].totalContestVotes) !== list.reduce((sum, row) => sum + row.votes, 0)) throw new Error(`${label} total does not reconcile.`);
    return { ...withGate(gate, tally(list, { label: `Ohio SOS district-wide totals, ${label}`, coverage: "complete" })), sourceId: "oh-house" };
  });
}

// Official Ohio results are preferred. CNN replaces a target only when the official
// result is unavailable (e.g. HTTP 429) or under review (e.g. counts under IsTest=true).
export function parseOhio(bodies: Record<string, string>): Record<string, ElectionResult> {
  const official = parseOfficial(bodies);
  return Object.fromEntries(targets.map(target => {
    const why = "official Ohio SOS feed unavailable or under review; CNN omits certified write-ins";
    const race: CnnRace = target.chamber === "senate"
      ? { target, key: cnnKey(target), candidates: SENATE_CNN, why, special: SENATE_SPECIAL }
      : { target, key: cnnKey(target), candidates: HOUSE[target.district!].cnn, why };
    return [target.id, withCnnFallback(official[target.id], race, bodies)];
  }));
}

export const ohioAdapter: ElectionAdapter = {
  id: "northeast-oh",
  version: "2026-11-03.2",
  sources: [
    { id: "oh-xml", name: "Ohio SOS NIST results XML (identity/test gate)", url: `${API}/download?filename=VSSC1622XmlFileBlob`, authorityUrl: AUTHORITY, official: true, maxBytes: 6_000_000 },
    { id: "oh-senate", name: "Ohio SOS U.S. Senate statewide JSON", url: `${API}/Contest/GetContestDetailsObject?contestName=U.S.+Senator&contestObjectId=&resultsLevel=&countyId=`, authorityUrl: AUTHORITY, official: true },
    { id: "oh-house", name: "Ohio SOS Representative to Congress district summary JSON", url: `${API}/Contest/GetContestDetailsObject?contestName=Representative+to+Congress&contestObjectId=&resultsLevel=&countyId=`, authorityUrl: AUTHORITY, official: true },
    ...targets.map(target => cnnSource(cnnKey(target))),
    CNN_SENATE_LIST,
  ],
  targets,
  parse: parseOhio,
};

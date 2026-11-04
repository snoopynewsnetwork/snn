import type { CandidateCount } from "../monitor";
import type { ElectionAdapter, ElectionResult, ElectionTarget } from "./types";
import { count, exactUniverse, guarded, json, party, type Expected } from "./southeast-common.ts";
import { cnnSource, withCnnFallback, type CnnRace } from "./northeast-cnn.ts";

// Indiana Election Division ENR (enr.indianavoters.in.gov). settings.json names the
// live buffer (VersionType A or B); the site reads data/<file>_<VersionType>.json.
// Both buffers are fetched and only the one settings selects is admitted.
const BASE = "https://enr.indianavoters.in.gov/site/data";
const AUTHORITY = "https://www.in.gov/sos/elections/";

interface Contest { officeId: string; district: string; title: string; candidates: Expected[] }

export const inContests: Record<string, Contest> = {
  "house-in-01": { officeId: "4912", district: "1", title: "United States Representative, First District", candidates: [
    { name: "Frank J. Mrvan", party: "DEM" }, { name: "Barb Regnitz", party: "REP" },
    { name: "Alexander R (Alex) Degman (W/I)", party: "IND" }, { name: "Prescription Dope Deaths Johnson, Jr (W/I)", party: "O" }] },
  "house-in-05": { officeId: "5256", district: "5", title: "United States Representative, Fifth District", candidates: [
    { name: "J.D. Ford", party: "DEM" }, { name: "Victoria Spartz", party: "REP" }] },
};

const list = <T>(value: T | T[] | undefined): T[] => value === undefined ? [] : Array.isArray(value) ? value : [value];

export function inContest(office: any, settings: any, spec: Contest): ElectionResult {
  const races = list<any>(office.StatewideSummary?.Race).filter(race => race.OFFICEID === spec.officeId);
  if (races.length !== 1 || races[0].OFFICE_TITLE !== spec.title || races[0].NumofSeats !== "1")
    throw new Error(`${spec.title} identity changed.`);
  const certified = settings.Certified === "T";
  let winner: ElectionResult["winner"];
  const candidates: CandidateCount[] = list<any>(races[0].Candidates?.Candidate).map(candidate => {
    const result = { name: String(candidate.NAME_ON_BALLOT).trim(), party: party(candidate.PARTY), votes: count(candidate.TOTAL) };
    // The publisher's own winner flag is only honored once the state marks the election certified.
    if (certified && candidate.isWinner === "T")
      winner = result.party === "DEM" ? "D" : result.party === "REP" ? "R" : result.party === "IND" ? "I" : "other";
    return result;
  });
  exactUniverse(candidates, spec.candidates, spec.title);
  // District totals must equal the per-county rows published in the same snapshot.
  const regions = list<any>(office.OfficeCategory?.Regions?.Region).filter(region => region.MAP_JURISDICTION_NAME === spec.district);
  if (regions.length !== 1) throw new Error(`District ${spec.district} county breakdown missing.`);
  const countyRaces = list<any>(regions[0].Races?.Race);
  if (!countyRaces.length || countyRaces.some(race => race.OFFICEID !== spec.officeId)) throw new Error("County breakdown identity changed.");
  for (const candidate of candidates) {
    const sum = countyRaces.reduce((total, race) => total + list<any>(race.Candidates?.Candidate)
      .filter(row => String(row.NAME_ON_BALLOT).trim() === candidate.name)
      .reduce((n, row) => n + count(row.TOTAL_VOTES), 0), 0);
    if (sum !== candidate.votes) throw new Error(`${candidate.name}: county rows do not reconcile with district total.`);
  }
  const totalVotes = candidates.reduce((sum, candidate) => sum + candidate.votes, 0);
  const base = {
    candidates, totalVotes, coverage: "complete" as const, sourceUpdated: String(office.WriteTime ?? settings.WriteTime),
    resultStatus: certified ? "certified" as const : "unofficial" as const, winner,
  };
  const counties = `${countyRaces.length} counties`;
  if (!totalVotes) return { ...base, winner: undefined, status: "setup", message: `Zero setup: Indiana Election Division has published no votes for this contest yet (${counties}).` };
  return {
    ...base, status: "reporting",
    message: certified
      ? `Indiana Election Division certified district totals (${counties}).`
      : `Indiana Election Division district totals (${counties}). Unofficial cumulative returns; may be revised. No race call.`,
  };
}

const targets: ElectionTarget[] = ["01", "05"].map(district => ({
  id: `house-in-${district}`, state: "IN", name: `IN-${district}`, chamber: "house", district, sourceId: "in-settings",
}));

// Observed 2026-11-04 00:10 UTC: the official feed still carried zero IN-05
// totals while CNN had 89,826 votes. Keep polling the state and use attributed
// newsroom returns until positive official counts arrive.
const in05Fallback: CnnRace = {
  target: targets.find(target => target.id === "house-in-05")!,
  key: "2026-HG-IN-5",
  candidates: inContests["house-in-05"].candidates.map(candidate => candidate.name),
  why: "Indiana's official feed has not supplied usable positive IN-05 returns",
};

export const indiana: ElectionAdapter = {
  id: "southeast-in",
  version: "2026-11-03.2",
  sources: [
    { id: "in-settings", name: "Indiana ENR settings", url: `${BASE}/settings.json`, authorityUrl: AUTHORITY, official: true },
    { id: "in-house-A", name: "Indiana ENR US Representative results (buffer A)", url: `${BASE}/OffCatC_1005_A.json`, authorityUrl: AUTHORITY, official: true, maxBytes: 2_000_000 },
    { id: "in-house-B", name: "Indiana ENR US Representative results (buffer B)", url: `${BASE}/OffCatC_1005_B.json`, authorityUrl: AUTHORITY, official: true, maxBytes: 2_000_000 },
    cnnSource(in05Fallback.key),
  ],
  targets,
  parse(bodies) {
    let settings: any, office: any;
    const official = guarded(targets, () => {
      settings = json(bodies, "in-settings").Root;
      if (settings?.CurrentElection !== "11/03/2026" || settings.ElectionType !== "G") throw new Error("Not the November 3, 2026 general election.");
      if (!/^[AB]$/.test(settings.VersionType)) throw new Error("Unknown live data buffer.");
      office = json(bodies, `in-house-${settings.VersionType}`).Root;
      if (office?.OfficeCategory?.OFFICECATEGORYID !== "1005" || office.OfficeCategory.OFFICE_CATEGORY_NAME !== "US Representative")
        throw new Error("US Representative office category changed.");
    }, target => inContest(office, settings, inContests[target.id]));
    const fallback = withCnnFallback(official["house-in-05"], in05Fallback, bodies, { allowSetup: true });
    if (fallback.sourceId) {
      try { exactUniverse(fallback.candidates ?? [], inContests["house-in-05"].candidates, "CNN IN-05"); }
      catch (error) {
        return { ...official, "house-in-05": { ...official["house-in-05"],
          message: `${official["house-in-05"].message} CNN fallback rejected: ${error instanceof Error ? error.message : String(error)}` } };
      }
    }
    return { ...official, "house-in-05": fallback };
  },
};

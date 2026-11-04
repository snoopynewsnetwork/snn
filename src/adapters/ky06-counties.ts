import type { CandidateCount, CountyCount } from "../monitor";
import type { ElectionAdapter, ElectionResult } from "./types";

type ObjectData = Record<string, unknown>;
function object(value: unknown): ObjectData {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Invalid KY-06 source object.");
  return value as ObjectData;
}
function party(value: unknown): string {
  if (typeof value !== "string" || !value.trim()) throw new Error("Missing KY-06 candidate party.");
  const label = value.trim();
  return ({ Democratic: "DEM", Republican: "REP", Independent: "IND", Libertarian: "LIB", Green: "GRE" } as Record<string, string>)[label] ?? label;
}

export const ky06CountyTarget = "house-ky-06-counties";
export const ky06CountyAdapter: ElectionAdapter = {
  id: "southeast-ky-counties", version: "2026-11-03-v1",
  sources: [{ id: "civic-ky06-counties", name: "civicAPI KY-06 county returns", url: "https://civicapi.org/api/v2/race/87173",
    authorityUrl: "https://civicapi.org/", official: false }],
  targets: [{ id: ky06CountyTarget, state: "KY", name: "KY-06 county detail", chamber: "house", district: "06", sourceId: "civic-ky06-counties" }],
  parse(bodies) {
    try { return { [ky06CountyTarget]: parseKy06Counties(bodies["civic-ky06-counties"]) }; }
    catch (error) { return { [ky06CountyTarget]: { status: "unavailable", message: error instanceof Error ? error.message : "KY-06 county validation failed." } }; }
  },
};

const ky06Counties = new Map([
  ["anderson", "21005"], ["bath", "21011"], ["bourbon", "21017"], ["clark", "21049"],
  ["estill", "21065"], ["fayette", "21067"], ["fleming", "21069"], ["garrard", "21079"],
  ["jessamine", "21113"], ["madison", "21151"], ["mercer", "21167"], ["montgomery", "21173"],
  ["nicholas", "21181"], ["powell", "21197"], ["scott", "21209"], ["woodford", "21239"],
]);

export function parseKy06Counties(body: string): ElectionResult {
  const data = object(JSON.parse(body));
  if (data.country !== "US" || data.province !== "KY" || data.district !== "KY-06" || data.municipality !== null ||
      data.election_name !== "Kentucky US House 6" || data.election_type !== "House of Representatives" || data.election_scope !== "General" ||
      typeof data.election_date !== "string" || !/^2026-11-03T/.test(data.election_date) || !Number.isFinite(Date.parse(data.election_date)) ||
      data.test_data !== false || data.is_disputed !== false || data.round !== 1)
    throw new Error("KY-06 county feed election identity or test/dispute flags changed; review required.");
  if (!Array.isArray(data.candidates) || !data.candidates.length) throw new Error("Missing KY-06 candidate list.");
  const ids = new Set<number>();
  const candidates: CandidateCount[] = data.candidates.map(value => {
    const c = object(value);
    if (typeof c.candidate_id !== "number" || !Number.isSafeInteger(c.candidate_id) || c.candidate_id <= 0 || ids.has(c.candidate_id) ||
        typeof c.name !== "string" || !c.name.trim() || typeof c.votes !== "number" || !Number.isSafeInteger(c.votes) || c.votes < 0)
      throw new Error("Invalid or duplicate KY-06 candidate or vote count.");
    ids.add(c.candidate_id);
    return { name: c.name.trim().replace(/\s+/g, " "), party: party(c.party), votes: c.votes };
  });
  const totalVotes = candidates.reduce((sum, c) => sum + c.votes, 0);
  if (!Number.isSafeInteger(totalVotes)) throw new Error("KY-06 total exceeds supported range.");
  if (candidates.filter(c => c.party === "DEM").length !== 1 || candidates.filter(c => c.party === "REP").length !== 1)
    throw new Error("KY-06 major-party matchup is ambiguous.");
  const expected = new Map<number, [string, string]>([[220411, ["Ralph Alvarado", "REP"]], [220412, ["Zach Dembo", "DEM"]],
    [220413, ["Pete Lynch", "Kentucky Party"]], [220414, ["Jay J. Bowman", "IND"]]]);
  const rawCandidates = data.candidates as ObjectData[];
  for (const [id, [name, candidateParty]] of expected) {
    const index = rawCandidates.findIndex(c => c.candidate_id === id);
    if (index < 0 || candidates[index].name !== name || candidates[index].party !== candidateParty)
      throw new Error("KY-06 county feed candidate identity changed; review required.");
  }
  const identity = (candidate: CandidateCount) => `${candidate.name}\u0000${candidate.party}`;
  if (new Set(candidates.map(identity)).size !== candidates.length) throw new Error("Ambiguous KY-06 candidate identities.");
  const byIdentity = new Map(candidates.map(c => [identity(c), c]));
  const regions = object(data.region_results);
  if (Object.keys(regions).length !== ky06Counties.size || Object.keys(regions).some(key => !ky06Counties.has(key)))
    throw new Error("KY-06 county coverage changed; all 16 county portions are required.");
  const counties: CountyCount[] = [...ky06Counties].map(([key, fips]) => {
    const region = object(regions[key]);
    if (region.type !== "County" || region.fips !== fips || region.name !== key[0].toUpperCase() + key.slice(1) ||
        !Array.isArray(region.candidates) || region.candidates.length !== candidates.length)
      throw new Error("KY-06 county geography or candidate coverage changed.");
    const seen = new Set<string>();
    const countyCandidates = region.candidates.map(value => {
      const c = object(value);
      if (typeof c.name !== "string" || typeof c.votes !== "number" || !Number.isSafeInteger(c.votes) || c.votes < 0)
        throw new Error("Invalid KY-06 county vote count.");
      const candidate = { name: c.name.trim().replace(/\s+/g, " "), party: party(c.party), votes: c.votes };
      const id = identity(candidate);
      if (!byIdentity.has(id) || seen.has(id)) throw new Error("Unknown or duplicate KY-06 county candidate.");
      seen.add(id);
      return candidate;
    });
    return { name: String(region.name), fips, candidates: countyCandidates, totalVotes: countyCandidates.reduce((sum, c) => sum + c.votes, 0),
      sourceReporting: typeof region.percent_reporting === "number" && Number.isFinite(region.percent_reporting) && region.percent_reporting >= 0 && region.percent_reporting <= 100 ? region.percent_reporting : null };
  });
  for (const candidate of candidates) {
    const sum = counties.reduce((total, county) => total + county.candidates.find(c => identity(c) === identity(candidate))!.votes, 0);
    if (!Number.isSafeInteger(sum) || sum !== candidate.votes) throw new Error("KY-06 county votes do not reconcile to the district candidate total.");
  }
  return { status: totalVotes ? "reporting" : "setup", candidates, totalVotes, counties, coverage: "complete",
    ...(typeof data.last_updated === "string" && Number.isFinite(Date.parse(data.last_updated)) ? { sourceUpdated: data.last_updated } : {}), message: "civicAPI KY-06 county returns (third-party). All 16 county portions reconcile to this feed's district totals; reporting percentages do not estimate votes remaining." };
}

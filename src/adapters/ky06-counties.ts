import type { CandidateCount, CountyCount } from "../monitor";
import type { ElectionAdapter, ElectionResult } from "./types";
import { CNN_AUTHORITY, cnnSource, parseCnnRace } from "./northeast-cnn.ts";
import { ky06CnnRace } from "./southeast-ky.ts";

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
  id: "southeast-ky-counties", version: "2026-11-03-v2",
  sources: [{ id: "civic-ky06-counties", name: "civicAPI KY-06 county returns", url: "https://civicapi.org/api/v2/race/87173",
    authorityUrl: "https://civicapi.org/", official: false },
    cnnSource(ky06CnnRace.key, "KY-06 county reconciliation"),
    { id: "cnn-ky06-counties", name: "CNN KY-06 county returns and expected-vote estimates", url: "https://politics.api.cnn.io/results/county-races/2026-HG-KY-6.json",
      authorityUrl: CNN_AUTHORITY, official: false }],
  targets: [{ id: ky06CountyTarget, state: "KY", name: "KY-06 county detail", chamber: "house", district: "06", sourceId: "cnn-ky06-counties" }],
  parse(bodies) {
    let cnnError: string;
    try { return { [ky06CountyTarget]: { ...parseCnnKy06Counties(bodies["cnn-ky06-counties"], bodies[`cnn-${ky06CnnRace.key}`]), sourceId: "cnn-ky06-counties" } }; }
    catch (error) { cnnError = error instanceof Error ? error.message : "CNN county validation failed."; }
    try {
      const result = parseKy06Counties(bodies["civic-ky06-counties"]);
      return { [ky06CountyTarget]: { ...result, sourceId: "civic-ky06-counties", message: `${result.message} CNN county feed unavailable: ${cnnError}` } };
    } catch (error) {
      // No source was admitted. Throw so the shared recorder marks every
      // attempted response as rejected, including a malformed civic fallback.
      throw new Error(`CNN: ${cnnError} civicAPI: ${bodies["civic-ky06-counties"] === undefined ? "Response unavailable this cycle." : error instanceof Error ? error.message : "County validation failed."}`);
    }
  },
};

const ky06Counties = new Map([
  ["anderson", "21005"], ["bath", "21011"], ["bourbon", "21017"], ["clark", "21049"],
  ["estill", "21065"], ["fayette", "21067"], ["fleming", "21069"], ["garrard", "21079"],
  ["jessamine", "21113"], ["madison", "21151"], ["mercer", "21167"], ["montgomery", "21173"],
  ["nicholas", "21181"], ["powell", "21197"], ["scott", "21209"], ["woodford", "21239"],
]);

// A district-specific county feed: split Anderson/Bath are House portions.
// Never use statewide/whole-county totals. Both CNN responses must reconcile;
// a refresh between requests can fail this check and be retried next minute.
export function parseCnnKy06Counties(body: string | undefined, raceBody: string | undefined): ElectionResult {
  const race = parseCnnRace(raceBody, ky06CnnRace);
  if (!["setup", "reporting"].includes(race.status)) throw new Error(race.message);
  if (body === undefined) throw new Error("CNN county response unavailable this cycle.");
  const data: unknown = JSON.parse(body);
  if (!Array.isArray(data) || data.length !== ky06Counties.size) throw new Error("CNN must supply all 16 KY-06 county portions.");
  const expected = new Map([[115622, ["Ralph Alvarado", "REP"]], [169796, ["Zach Dembo", "DEM"]],
    [175051, ["Jay Bowman", "IND"]], [175072, ["Pete Lynch", "KYP"]]]);
  const seen = new Set<string>();
  const clocks: string[] = [];
  const counties: CountyCount[] = data.map(value => {
    const row = object(value);
    const name = String(row.countyName), key = name.toLowerCase();
    if (!ky06Counties.has(key) || seen.has(key) || row.countyFipsCode !== ky06Counties.get(key) || name !== key[0].toUpperCase() + key.slice(1) ||
        row.ecKey !== ky06CnnRace.key || row.externalKey !== "production-key" || row.electionType !== "G" ||
        row.contestType !== "HG" || row.resourceType !== "county-races" || row.raceType !== "H" || row.jurisdictionCode !== 6 ||
        row.stateAbbreviation !== "KY" || row.stateFipsCode !== "21") throw new Error("CNN KY-06 county election identity or geography changed.");
    seen.add(key);
    if (typeof row.extractedAt !== "string" || !/^\d{4}-\d{2}-\d{2}T/.test(row.extractedAt) || row.extractedAt.slice(0, 10) < "2026-11-03" || !Number.isFinite(Date.parse(row.extractedAt)))
      throw new Error("Invalid CNN KY-06 county source timestamp.");
    clocks.push(row.extractedAt);
    if (!Array.isArray(row.candidates) || row.candidates.length !== expected.size) throw new Error("CNN county candidate coverage changed.");
    const candidateIds = new Set<number>();
    const candidates: CandidateCount[] = row.candidates.map(value => {
      const c = object(value), id = c.candidateId as number, identity = expected.get(id);
      if (!identity || candidateIds.has(id) || c.fullName !== identity[0] || c.majorParty !== identity[1] ||
          typeof c.voteNum !== "number" || !Number.isSafeInteger(c.voteNum) || c.voteNum < 0) throw new Error("Invalid CNN county candidate or votes.");
      candidateIds.add(id);
      return { name: identity[0], party: identity[1], votes: c.voteNum };
    });
    const totalVotes = candidates.reduce((sum, c) => sum + c.votes, 0);
    if (!Number.isSafeInteger(totalVotes) || row.totalVote !== totalVotes) throw new Error("CNN county candidate total does not reconcile.");
    const estimate = typeof row.percentReporting === "number" && Number.isFinite(row.percentReporting) && row.percentReporting >= 0 && row.percentReporting <= 100 ? row.percentReporting : undefined;
    return { name, fips: String(row.countyFipsCode), candidates, totalVotes, sourceReporting: null, estimatedVotePercent: estimate };
  });
  for (const candidate of race.candidates!) {
    if (counties.reduce((sum, county) => sum + county.candidates.find(c => c.name === candidate.name && c.party === candidate.party)!.votes, 0) !== candidate.votes)
      throw new Error("CNN county counts do not reconcile to the CNN district snapshot; retry next cycle.");
  }
  return { ...race, counties, sourceUpdated: clocks.sort()[0],
    message: "CNN newsroom county returns (not official). All 16 KY-06 portions reconcile to CNN's district snapshot. Expected-vote percentages are supplier estimates, not actual remaining ballots or race calls." };
}

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

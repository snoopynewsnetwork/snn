import type { CandidateCount } from "../monitor";
import type { ElectionAdapter, ElectionResult, ElectionSource, ElectionTarget } from "./types";
import { count, json, party, perTarget, requireUniverse, review, tally, unavailable } from "./northeast-common.ts";

// Newsroom fallback: CNN's public election-results race API, the JSON behind CNN's
// 2026 results pages. NOT an official publisher. Used only where no official live
// statewide/district feed was reachable (see docs/live-sources-northeast.md).
// CNN projections ("winner") are surfaced as text only; they never set winner.
const API = "https://politics.api.cnn.io/results/race";
export const CNN_AUTHORITY = "https://www.cnn.com/election/2026";

export interface CnnRace {
  target: ElectionTarget;
  key: string; // CNN ecKey, e.g. 2026-SG-ME, 2026-HG-ME-2.
  candidates: string[]; // Full universe incl. listed write-ins, observed 2026-11-03.
  why: string; // Why official sources could not serve this target.
  note?: string;
  // CNN files Senate specials as electionType "P" / contestType "SP" with an empty title.
  // Such a race is admitted only if every pinned November 3 general-election fact matches:
  // its listing in CNN's 2026 Senate general list, the Nov 3 poll embargo times and the
  // exact cross-party field (a party primary cannot have D, R, I and LIB nominees together).
  special?: {
    raceTitle: string; pollsOpen: number; pollsClose: number;
    parties: Record<string, string>; // fullName -> majorParty
    listSource: string; // source id of politics.api.cnn.io/results/national-races/2026-SG.json
  };
}

const majors: Record<string, string> = { DEM: "DEM", REP: "REP", LIB: "LIB", GRN: "GRE", IND: "IND" };

function requireSpecialGeneral(data: any, race: CnnRace, listBody: string | undefined): void {
  const special = race.special!;
  if (data.electionType !== "P" || data.electionTitle !== "" || data.contestType !== "SP" || data.raceType !== "S" || data.raceTypeCode !== "S" || data.raceTitle !== special.raceTitle)
    throw new Error(`CNN ${race.key} special-election identity changed.`);
  const embargo = data.raceEmbargo ?? {};
  if (embargo.pollsOpen !== special.pollsOpen || embargo.assignedPollsClose !== special.pollsClose || embargo.votesRelease !== special.pollsClose)
    throw new Error(`CNN ${race.key} is not embargoed to the November 3, 2026 poll times.`);
  for (const row of data.candidates ?? [])
    if (special.parties[String(row.fullName)] !== String(row.majorParty)) throw new Error(`CNN ${race.key} candidate party field changed.`);
  const list = json(listBody, "CNN 2026 Senate general list");
  if (!Array.isArray(list) || !list.some((item: any) => item?.ecKey === race.key && item?.stateAbbreviation === race.target.state && item?.electionType === "P"))
    throw new Error(`CNN ${race.key} is not listed in CNN's 2026 Senate general-election races.`);
}

export function parseCnnRace(body: string | undefined, race: CnnRace, listBody?: string): ElectionResult {
  const data = json(body, `CNN ${race.key}`);
  if (data.ecKey !== race.key || data.resourceType !== "race") throw new Error(`CNN race identity changed (expected ${race.key}).`);
  if (data.externalKey !== "production-key") throw new Error(`CNN ${race.key} is not production data (${String(data.externalKey)}).`);
  if (data.stateAbbreviation !== race.target.state) throw new Error(`CNN ${race.key} is not a ${race.target.state} race.`);
  if (race.special) requireSpecialGeneral(data, race, listBody);
  else if (data.electionType !== "G" || data.electionTitle !== "General Election")
    throw new Error(`CNN ${race.key} is not the ${race.target.state} general election.`);
  const extracted = String(data.extractedAt ?? "");
  if (!/^\d{4}-\d{2}-\d{2}T/.test(extracted) || extracted.slice(0, 10) < "2026-11-03") throw new Error(`CNN ${race.key} snapshot predates November 3, 2026.`);
  const rows: any[] = data.candidates;
  if (!Array.isArray(rows)) throw new Error(`CNN ${race.key} candidate list missing.`);
  requireUniverse(rows.map(row => String(row.fullName)), race.candidates, `CNN ${race.key}`);
  const candidates: CandidateCount[] = rows.map(row => ({
    name: String(row.fullName),
    party: /\(write-in\)/i.test(String(row.fullName)) ? "WRITE-IN" : majors[String(row.majorParty)] ?? party(String(row.majorParty ?? row.candidatePartyCode)),
    votes: count(row.voteNum),
  }));
  const sum = candidates.reduce((total, candidate) => total + candidate.votes, 0);
  if (count(data.totalVote) !== sum) throw new Error(`CNN ${race.key} candidate votes do not reconcile with totalVote.`);
  if (sum && data.raceEmbargo?.votesReleased !== true) return review(`CNN ${race.key} shows votes before its vote embargo lifted; rejected as test data.`, extracted);
  const projected = rows.filter(row => row.winner === true).map(row => String(row.fullName));
  const estimatedVotePercent = typeof data.percentReporting === "number" && Number.isFinite(data.percentReporting) && data.percentReporting >= 0 && data.percentReporting <= 100
    ? data.percentReporting : undefined;
  const reporting = estimatedVotePercent !== undefined ? ` CNN estimates ${estimatedVotePercent}% of expected vote counted (supplier estimate, not precincts).` : "";
  const result = tally(candidates, {
    label: `CNN newsroom results (not official; ${race.why})`,
    sourceUpdated: extracted, coverage: "complete",
  });
  const extra = [result.status === "reporting" ? reporting.trim() : "", projected.length ? `CNN projects ${projected.join(", ")} — newsroom projection, not an official call.` : "", race.note ?? ""].filter(Boolean).join(" ");
  return { ...result, estimatedVotePercent: result.status === "reporting" ? estimatedVotePercent : undefined,
    message: extra ? `${result.message} ${extra}` : result.message };
}

// Official result first; the CNN race only replaces an official result that is
// unavailable or under review, and never replaces verified official setup or counts.
export function withCnnFallback(primary: ElectionResult, race: CnnRace, bodies: Record<string, string>): ElectionResult {
  if (primary.status !== "unavailable" && primary.status !== "review") return primary;
  const body = bodies[`cnn-${race.key}`];
  if (body === undefined) return { ...primary, message: `${primary.message} CNN fallback also unavailable this cycle.` };
  try {
    const fallback = parseCnnRace(body, race, race.special ? bodies[race.special.listSource] : undefined);
    if (fallback.status === "unavailable" || fallback.status === "review")
      return { ...primary, message: `${primary.message} CNN fallback rejected: ${fallback.message}` };
    return { ...fallback, sourceId: `cnn-${race.key}`, message: `Official feed: ${primary.message} Using fallback — ${fallback.message}` };
  } catch (error) {
    return { ...primary, message: `${primary.message} CNN fallback rejected: ${error instanceof Error ? error.message : String(error)}` };
  }
}

export const CNN_SENATE_LIST: ElectionSource = {
  id: "cnn-2026-SG-list", name: "CNN 2026 Senate general-election race list (identity check, not official)",
  url: "https://politics.api.cnn.io/results/national-races/2026-SG.json", authorityUrl: CNN_AUTHORITY, official: false,
};

export function cnnSource(key: string, role = "newsroom fallback"): ElectionSource {
  return { id: `cnn-${key}`, name: `CNN results API ${key} (${role}, not official)`, url: `${API}/${key}.json`, authorityUrl: CNN_AUTHORITY, official: false };
}

export function cnnAdapter(id: string, races: CnnRace[]): ElectionAdapter {
  const sources: ElectionSource[] = races.map(race => cnnSource(race.key, "newsroom supplier"));
  const byTarget = new Map(races.map(race => [race.target.id, race]));
  return {
    id, version: "2026-11-03.1", sources,
    targets: races.map(race => ({ ...race.target, sourceId: `cnn-${race.key}` })),
    parse: bodies => perTarget(races.map(race => race.target), target => {
      const race = byTarget.get(target.id)!;
      const body = bodies[`cnn-${race.key}`];
      return body === undefined ? unavailable(`CNN ${race.key} response unavailable this cycle.`) : parseCnnRace(body, race);
    }),
  };
}

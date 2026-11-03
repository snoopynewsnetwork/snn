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
}

const majors: Record<string, string> = { DEM: "DEM", REP: "REP", LIB: "LIB", GRN: "GRE", IND: "IND" };

export function parseCnnRace(body: string | undefined, race: CnnRace): ElectionResult {
  const data = json(body, `CNN ${race.key}`);
  if (data.ecKey !== race.key || data.resourceType !== "race") throw new Error(`CNN race identity changed (expected ${race.key}).`);
  if (data.externalKey !== "production-key") throw new Error(`CNN ${race.key} is not production data (${String(data.externalKey)}).`);
  if (data.electionType !== "G" || data.electionTitle !== "General Election" || data.stateAbbreviation !== race.target.state)
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
  const reporting = typeof data.percentReporting === "number" ? ` CNN estimates ${data.percentReporting}% of expected vote counted (supplier estimate, not precincts).` : "";
  const result = tally(candidates, {
    label: `CNN newsroom results (not official; ${race.why})`,
    sourceUpdated: extracted, coverage: "complete",
  });
  const extra = [result.status === "reporting" ? reporting.trim() : "", projected.length ? `CNN projects ${projected.join(", ")} — newsroom projection, not an official call.` : "", race.note ?? ""].filter(Boolean).join(" ");
  return extra ? { ...result, message: `${result.message} ${extra}` } : result;
}

export function cnnAdapter(id: string, races: CnnRace[]): ElectionAdapter {
  const sources: ElectionSource[] = races.map(race => ({
    id: `cnn-${race.key}`, name: `CNN results API ${race.key} (newsroom supplier, not official)`,
    url: `${API}/${race.key}.json`, authorityUrl: CNN_AUTHORITY, official: false,
  }));
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

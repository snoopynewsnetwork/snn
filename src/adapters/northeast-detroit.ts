import type { CandidateCount } from "../monitor";
import type { ElectionAdapter, ElectionResult, ElectionTarget } from "./types";
import { count, json, party, perTarget, requireUniverse, review, tally } from "./northeast-common.ts";

// City of Detroit Department of Elections results, published through its Enhanced Voting
// vendor site and linked from https://detroitmi.gov/departments/elections/election-results-maps.
// City geography only (not Wayne County): supports the cue-detroit editor assessment.
const ELECTION = "_20261027152933";
const AUTHORITY = "https://detroitmi.gov/departments/elections/election-results-maps";
const DETROIT = ["Abdul El-Sayed", "Mike Rogers", "Lydia Christensen", "Tim Long", "Douglas P. Marsh", "Walter P. Kristy", "Write-in"];

const target: ElectionTarget = {
  id: "senate-mi-detroit", state: "MI", name: "Michigan U.S. Senate — City of Detroit only", chamber: "senate", district: "Detroit city", sourceId: "detroit-ev",
};

const text = (value: any): string => (Array.isArray(value) ? value.find(item => item?.languageId === "en" || item?.languageId === null)?.text : undefined) ?? "";

export function parseDetroit(body: string | undefined): ElectionResult {
  const data = json(body, "Detroit Enhanced Voting");
  const election = data.election;
  if (!election || election.electionDate !== "2026-11-03" || text(election.name) !== "City of Detroit, General Election - November 3, 2026")
    throw new Error("Detroit feed is not the November 3, 2026 general election.");
  if (election.isProduction !== true) {
    const anyVotes = JSON.stringify(data.ballotItems ?? []).match(/"voteCount":\s*[1-9]/);
    if (anyVotes) return review("Detroit feed is flagged non-production while showing votes; rejected as test data.");
  }
  const items = (data.ballotItems ?? []).filter((item: any) => text(item.name) === "United States Senator");
  if (items.length !== 1 || items[0].publishPublicElectionId !== ELECTION) throw new Error("Detroit U.S. Senator contest missing or duplicated.");
  const options: any[] = items[0].summaryResults?.ballotOptions;
  if (!Array.isArray(options)) throw new Error("Detroit Senate ballot options missing.");
  requireUniverse(options.map(option => text(option.name)), DETROIT, "Detroit Senate");
  const candidates: CandidateCount[] = options.map(option => {
    const votes = count(option.voteCount);
    const groups: any[] = option.groupResults ?? [];
    const byGroup = (name: string) => groups.filter(group => text(group.groupName) === name).reduce((sum, group) => sum + count(group.voteCount), 0);
    const early = byGroup("Early Voting"), electionDay = byGroup("Election Day"), mail = byGroup("Absentee") + byGroup("Pre-Process Absentee");
    if (groups.length && early + electionDay + mail !== votes) throw new Error("Detroit voting-method counts do not reconcile.");
    return { name: text(option.name), party: option.isWriteIn ? "WRITE-IN" : party(String(option.party?.abbreviation ?? "")), votes, early, electionDay, mail };
  });
  const status = items[0].reportingStatus;
  const result = tally(candidates, {
    label: "City of Detroit official unofficial returns, U.S. Senate (city only)",
    partialNote: "City of Detroit only; compare with Detroit-city 2024 baselines, never Wayne County or statewide",
    coverage: "partial",
    reportedPrecincts: status ? count(status.reportingUnits) : undefined, totalPrecincts: status ? count(status.totalUnits) : undefined,
    sourceUpdated: typeof election.lastUpdated === "string" ? election.lastUpdated : undefined,
  });
  return {
    ...result,
    message: result.status === "setup" ? `${result.message} City of Detroit only (partial geography).` : result.message,
    // The city vendor flag is not a state certification; keep these unofficial.
    resultStatus: result.status === "reporting" ? "unofficial" : undefined,
  };
}

export const detroitAdapter: ElectionAdapter = {
  id: "northeast-mi-detroit",
  version: "2026-11-03.1",
  sources: [{
    id: "detroit-ev", name: "City of Detroit Enhanced Voting results (official city vendor feed)",
    url: `https://app.enhancedvoting.com/results/public/api/elections/city-detroit-mi/${ELECTION}/data`,
    authorityUrl: AUTHORITY, official: true, maxBytes: 6_000_000,
  }],
  targets: [target],
  parse: bodies => perTarget([target], () => parseDetroit(bodies["detroit-ev"])),
};

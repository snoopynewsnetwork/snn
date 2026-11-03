import type { CandidateCount } from "../monitor";
import type { ElectionAdapter, ElectionResult, ElectionTarget } from "./types";
import { count, exactUniverse, guarded, json, party, type Expected } from "./southeast-common.ts";

// Enhanced Voting public results API, used by Georgia SOS and Virginia ELECT.
// The election-scoped /data response is one cumulative snapshot containing every
// state-level ballot item; it is replaced on each poll, never summed.

export interface EnhancedSpec {
  label: string;       // Publisher name used in messages.
  sourceId: string;
  election: { id: string; date: string; name: string };
  unitNoun: string;    // Reporting units are counties/localities, not precincts.
  contests: Record<string, { ballotItemId: string; name: string; candidates: Expected[]; optional?: Expected[] }>;
}

const en = (texts: unknown): string => {
  if (!Array.isArray(texts)) throw new Error("Localized text missing.");
  const text = texts.find(item => item?.languageId === "en")?.text;
  if (typeof text !== "string") throw new Error("English text missing.");
  return text.trim();
};

// Georgia prints party and incumbency into the ballot name: "Jon Ossoff (I) (Dem)".
// "(I)" means incumbent there, not Independent, so both markers are removed from the display name.
export const cleanName = (name: string): string =>
  name.replace(/\s*\((?:I|Rep|Dem|Lib|Grn|Ind)\)/g, "").replace(/\s+/g, " ").trim();

function contest(data: any, spec: EnhancedSpec, targetId: string): ElectionResult {
  const want = spec.contests[targetId];
  const items = (data.ballotItems as any[]).filter(item => item?.id === want.ballotItemId);
  if (items.length !== 1) throw new Error(`Ballot item ${want.ballotItemId} missing or duplicated.`);
  const item = items[0];
  if (en(item.name) !== want.name || item.contestType !== "Candidate" || item.parentId)
    throw new Error(`Ballot item ${want.ballotItemId} identity changed.`);
  const options = item.summaryResults?.ballotOptions;
  if (!Array.isArray(options) || !options.length) throw new Error("Ballot options missing.");
  const candidates: CandidateCount[] = options.map((option: any) => {
    const literal = en(option.name);
    const abbreviation = option.party?.abbreviation;
    const candidate: CandidateCount = {
      name: cleanName(literal),
      party: /^write-?in$/i.test(literal) && !abbreviation ? "WRITE-IN" : party(abbreviation),
      votes: count(option.voteCount),
    };
    const groups: any[] = option.groupResults ?? [];
    if (groups.length && groups.reduce((sum, group) => sum + count(group.voteCount), 0) !== candidate.votes)
      throw new Error(`${candidate.name}: vote-method groups do not reconcile.`);
    for (const group of groups) {
      const name = en(group.groupName), votes = count(group.voteCount);
      if (/^election day$/i.test(name)) candidate.electionDay = votes;
      else if (/^(early voting|advanced? voting)$/i.test(name)) candidate.early = votes;
      else if (/absentee/i.test(name)) candidate.mail = votes;
      else if (/^provisional$/i.test(name)) candidate.provisional = votes;
    }
    return candidate;
  });
  exactUniverse(candidates, want.candidates, want.name, want.optional);
  const totalVotes = candidates.reduce((sum, candidate) => sum + candidate.votes, 0);
  if (count(item.voteTotal) !== totalVotes) throw new Error("Contest total does not equal candidate sum.");
  const status = item.reportingStatus;
  const units = count(status?.reportingUnits), totalUnits = count(status?.totalUnits);
  if (!totalUnits || units > totalUnits) throw new Error("Invalid reporting-unit status.");
  const labeled = data.election.isOfficialResults === true;
  const stage = labeled
    ? `${spec.label} labels these results official; that label is not treated as certification or a race call.`
    : "Unofficial cumulative returns; may be revised. No race call.";
  const unitsNote = `${units} of ${totalUnits} ${spec.unitNoun} fully reporting (a unit count, not a vote-completion estimate).`;
  return {
    status: totalVotes ? "reporting" : "setup",
    message: totalVotes
      ? `${spec.label} contest totals. ${stage} ${unitsNote}`
      : `Zero setup: ${spec.label} has published no votes for this contest yet. ${unitsNote}`,
    candidates, totalVotes, coverage: "complete",
    resultStatus: labeled ? undefined : "unofficial",
    sourceUpdated: String(status.asOf ?? data.election.asOf),
  };
}

export function parseEnhanced(text: Record<string, string>, spec: EnhancedSpec, targets: ElectionTarget[]): Record<string, ElectionResult> {
  let data: any;
  return guarded(targets, () => {
    data = json(text, spec.sourceId);
    const election = data.election;
    if (!election || election.id !== spec.election.id || election.electionDate !== spec.election.date ||
        en(election.name) !== spec.election.name || election.isProduction !== true || election.isPrimary !== false)
      throw new Error(`Not the production ${spec.election.date} general election.`);
    if (!Array.isArray(data.ballotItems)) throw new Error("Ballot items missing.");
  }, target => contest(data, spec, target.id));
}

export function enhancedAdapter(
  id: string, spec: EnhancedSpec, targets: ElectionTarget[], source: ElectionAdapter["sources"][number],
): ElectionAdapter {
  return { id, version: "2026-11-03.1", sources: [source], targets, parse: bodies => parseEnhanced(bodies, spec, targets) };
}

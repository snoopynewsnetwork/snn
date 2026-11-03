import type { CandidateCount } from "../monitor";
import type { ElectionAdapter, ElectionResult, ElectionSource, ElectionTarget } from "./types";
import { HEADERS, count, exactUniverse, guarded, json, party, tally, text, type Universe } from "./west-common.ts";

// Scytl/Clarity ENR (state-run instances for Iowa and Colorado). Data lives only at
// version-scoped paths, so current_ver.txt is fetched first and substituted into the
// summary URL by the collector (dependsOn/{version}).

export interface ClarityContest {
  target: ElectionTarget;
  contest: string; // Exact Clarity contest title ("C").
  universe: Universe;
}

export interface ClarityElection {
  adapterId: string;
  base: string; // e.g. https://electionresults.iowa.gov/IA/127077
  root: string; // elections.json listing that names the EID
  eid: string;
  electionName: RegExp;
  authorityUrl: string;
  label: string;
  contests: ClarityContest[];
}

export function clarityCandidates(row: any, label: string): CandidateCount[] {
  const names = row.CH, codes = row.P, votes = row.V;
  if (!Array.isArray(names) || !Array.isArray(codes) || !Array.isArray(votes) || names.length !== codes.length || names.length !== votes.length || !names.length)
    throw new Error(`${label}: candidate arrays malformed.`);
  return names.map((name: unknown, i: number) => ({
    name: String(name).trim(),
    party: /^write-?ins?$/i.test(String(name).trim()) ? "WRITE-IN" : party(codes[i]),
    votes: count(votes[i]),
  }));
}

export function parseClarityContest(summary: any[], contest: ClarityContest, label: string): ElectionResult {
  const rows = summary.filter(row => row?.C === contest.contest);
  if (rows.length !== 1) throw new Error(`${contest.contest} missing or duplicated.`);
  const row = rows[0];
  if (row.VF !== 1) throw new Error(`${contest.contest} vote-for changed.`);
  if (row.IsRCV === true || row.IsCumulative === true) throw new Error(`${contest.contest} tabulation type changed.`);
  const candidates = clarityCandidates(row, contest.contest);
  exactUniverse(candidates, contest.universe, contest.contest);
  const total = candidates.reduce((sum, c) => sum + c.votes, 0);
  if (row.TV !== undefined && count(row.TV) !== total) throw new Error(`${contest.contest} candidate votes do not reconcile with TV.`);
  const units = count(row.TP), reporting = count(row.PR);
  if (!units || reporting > units) throw new Error(`${contest.contest} reporting-unit status invalid.`);
  // TP/PR count Clarity reporting units (counties on these state sites), not precincts,
  // and not a vote-completion estimate.
  return tally(candidates, {
    label, coverage: "complete",
    note: `${reporting} of ${units} reporting units (counties) have uploaded; this is not a share of votes counted.`,
  });
}

export function clarityAdapter(election: ClarityElection): ElectionAdapter {
  const id = (suffix: string) => `${election.adapterId}-${suffix}`;
  const sources: ElectionSource[] = [
    { id: id("elections"), name: `${election.label} election list`, url: election.root, authorityUrl: election.authorityUrl, official: true, headers: HEADERS },
    { id: id("ver"), name: `${election.label} current version`, url: `${election.base}/current_ver.txt`, authorityUrl: election.authorityUrl, official: true, headers: HEADERS },
    {
      id: id("summary"), name: `${election.label} summary results`, url: `${election.base}/{version}/json/en/summary.json`,
      authorityUrl: election.authorityUrl, official: true, headers: HEADERS, dependsOn: id("ver"), maxBytes: 4_000_000,
    },
  ];
  const targets = election.contests.map(contest => ({ ...contest.target, sourceId: id("summary") }));
  const byTarget = new Map(election.contests.map(contest => [contest.target.id, contest]));
  return {
    id: election.adapterId, version: "2026-11-03.1", sources, targets,
    parse: bodies => {
      let summary: any[] = [];
      return guarded(targets, () => {
        const listing = json(bodies, id("elections"));
        const match = Array.isArray(listing) ? listing.filter(row => row?.EID === election.eid) : [];
        if (match.length !== 1 || !election.electionName.test(String(match[0].ElectionName)) || !/^11\/3\/2026\b/.test(String(match[0].Date)))
          throw new Error(`Clarity EID ${election.eid} is not the November 3, 2026 general election.`);
        if (/test|mock|primary/i.test(String(match[0].ElectionName))) throw new Error("Clarity election is a test or primary.");
        if (!/^\d{1,12}$/.test(text(bodies, id("ver")).trim())) throw new Error("Clarity version marker invalid.");
        const data = json(bodies, id("summary"));
        if (!Array.isArray(data) || !data.length) throw new Error("Clarity summary is not a nonempty array.");
        summary = data;
      }, target => parseClarityContest(summary, byTarget.get(target.id)!, election.label));
    },
  };
}

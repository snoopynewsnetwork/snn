import type { CandidateCount } from "../monitor";
import { parseKansasResults } from "../monitor.ts";
import type { ElectionAdapter, ElectionResult, ElectionTarget } from "./types";
import { CNN_AUTHORITY, parseCnnRace, type CnnRace } from "./northeast-cnn.ts";
import { HEADERS, count, exactUniverse, guarded, json, tally, text } from "./west-common.ts";

// Kansas. The Secretary of State's election-night page (ent.sos.ks.gov) is the official
// statewide source, but it sits behind a Cloudflare managed challenge (HTTP 403,
// cf-mitigated: challenge) for server clients, including Cloudflare Workers. It is still
// polled first; when it fails, CNN's public results API (newsroom supplier, not official)
// is used and labelled as such. Johnson County's own office publishes PDFs only.
const SOS_URL = "https://ent.sos.ks.gov/kssos_ent.html";
const SOS_AUTHORITY = "https://www.sos.ks.gov/elections/election-results.html";
const JOCO_URL = "https://www.jocoelection.org/events-elections/november-3-2026-general-election";
const CNN = "https://politics.api.cnn.io/results";

const senate: ElectionTarget = { id: "senate-ks", state: "KS", chamber: "senate", name: "Kansas U.S. Senate" };
const johnson: ElectionTarget = { id: "senate-ks-johnson", state: "KS", chamber: "senate", district: "Johnson County", name: "Kansas U.S. Senate — Johnson County (supporting cue)" };

const cnnSenate: CnnRace = {
  target: senate, key: "2026-SG-KS", candidates: ["Adam Hamilton", "Roger Marshall", "David Graham"],
  why: "Kansas SOS election-night page returns a Cloudflare challenge to server clients",
};

function reason(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

export function kansasSenate(bodies: Record<string, string>): ElectionResult {
  let official: string;
  try {
    const parsed = parseKansasResults(text(bodies, "ks-sos"));
    const { status, message, candidates, totalVotes, reportedPrecincts, totalPrecincts, sourceUpdated } = parsed;
    if (status !== "reporting" && status !== "setup") throw new Error(`unexpected status ${status}`);
    return {
      status, message, candidates, totalVotes, reportedPrecincts, totalPrecincts, sourceUpdated, coverage: "complete", sourceId: "ks-sos",
      ...(status === "reporting" ? { resultStatus: "unofficial" as const } : {}),
    };
  } catch (error) {
    official = reason(error);
  }
  const fallback = parseCnnRace(text(bodies, `cnn-${cnnSenate.key}`), cnnSenate);
  return { ...fallback, sourceId: `cnn-${cnnSenate.key}`, message: `${fallback.message} Official Kansas SOS page not admitted this cycle: ${official}` };
}

// CNN county-level record for Johnson County (FIPS 20091). One county of 105: partial
// coverage, never a statewide margin. Votes are admitted only after CNN's race-level
// vote embargo has lifted, matching parseCnnRace's test-data guard.
export function johnsonCounty(bodies: Record<string, string>): ElectionResult {
  const race = json(bodies, `cnn-${cnnSenate.key}`);
  const rows = json(bodies, "cnn-ks-counties");
  if (!Array.isArray(rows)) throw new Error("CNN Kansas county list is not an array.");
  const matches = rows.filter(row => row?.countyFipsCode === "20091");
  if (matches.length !== 1) throw new Error("CNN Johnson County record missing or duplicated.");
  const row = matches[0];
  if (row.ecKey !== cnnSenate.key || row.externalKey !== "production-key" || row.electionType !== "G" || row.stateAbbreviation !== "KS" || row.countyName !== "Johnson")
    throw new Error("CNN county record is not the Kansas Senate general election in Johnson County.");
  const extracted = String(row.extractedAt ?? "");
  if (!/^\d{4}-\d{2}-\d{2}T/.test(extracted) || extracted.slice(0, 10) < "2026-11-03") throw new Error("CNN county snapshot predates November 3, 2026.");
  if (!Array.isArray(row.candidates)) throw new Error("CNN county candidates missing.");
  const candidates: CandidateCount[] = row.candidates.map((c: any) => ({ name: String(c.fullName), party: String(c.majorParty), votes: count(c.voteNum) }));
  exactUniverse(candidates, [["Adam Hamilton", "DEM"], ["Roger Marshall", "REP"], ["David Graham", "LIB"]], "CNN Johnson County");
  const sum = candidates.reduce((total, c) => total + c.votes, 0);
  if (count(row.totalVote) !== sum) throw new Error("CNN Johnson County votes do not reconcile with totalVote.");
  if (sum && race.raceEmbargo?.votesReleased !== true) throw new Error("CNN county shows votes before the race vote embargo lifted; rejected as test data.");
  // Watch the county office's own page for official result documents (PDF only).
  const page = bodies["joco-page"] ?? "";
  const docs = [...page.matchAll(/href="([^"]*\/2026-1[12]\/[^"]*(?:GN2026|Result)[^"]*\.(?:pdf|csv))"/gi)].map(m => new URL(m[1].replace(/&amp;/g, "&"), JOCO_URL).href);
  const note = docs.length ? `Johnson County Election Office has posted official documents for manual cross-check: ${[...new Set(docs)].slice(0, 3).join(" ")}` : undefined;
  return tally(candidates, {
    label: "CNN newsroom county results for Johnson County (not official; Kansas SOS county pages are behind a Cloudflare challenge)",
    coverage: "partial", sourceUpdated: extracted, note, sourceId: "cnn-ks-counties",
  });
}

export const kansas: ElectionAdapter = {
  id: "west-ks", version: "2026-11-03.1",
  sources: [
    { id: "ks-sos", name: "Kansas SOS election-night results", url: SOS_URL, authorityUrl: SOS_AUTHORITY, official: true, headers: HEADERS, maxBytes: 3_000_000 },
    { id: `cnn-${cnnSenate.key}`, name: "CNN results API 2026-SG-KS (newsroom supplier, not official)", url: `${CNN}/race/${cnnSenate.key}.json`, authorityUrl: CNN_AUTHORITY, official: false },
    { id: "cnn-ks-counties", name: "CNN county results API 2026-SG-KS (newsroom supplier, not official)", url: `${CNN}/county-races/${cnnSenate.key}.json`, authorityUrl: CNN_AUTHORITY, official: false },
    { id: "joco-page", name: "Johnson County Election Office November 3, 2026 page", url: JOCO_URL, authorityUrl: JOCO_URL, official: true, headers: HEADERS },
  ],
  targets: [{ ...senate, sourceId: "ks-sos" }, { ...johnson, sourceId: "cnn-ks-counties" }],
  parse: bodies => guarded([senate, johnson], () => {}, target => target.id === senate.id ? kansasSenate(bodies) : johnsonCounty(bodies)),
};

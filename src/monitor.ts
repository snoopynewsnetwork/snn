// Official-source adapters. Counts are cumulative snapshots, never additive updates.
export const monitorSources = [
  { id: "nc-elections", race: "north-carolina", name: "NCSBE election catalog", url: "https://er.ncsbe.gov/enr/elections.txt" },
  { id: "nc-counties", race: "north-carolina", name: "NCSBE county status", url: "https://er.ncsbe.gov/enr/20261103/data/county.txt" },
  { id: "nc-results", race: "north-carolina", name: "NCSBE statewide results", url: "https://er.ncsbe.gov/enr/20261103/data/results_0.txt" },
  { id: "ks-home", race: "kansas", name: "Kansas Secretary of State", url: "https://www.sos.ks.gov/" },
  { id: "ks-results", race: "kansas", name: "Kansas official results index", url: "https://www.sos.ks.gov/elections/election-results.html" },
  { id: "ks-live", race: "kansas", name: "Kansas SOS election-night page", url: "https://ent.sos.ks.gov/kssos_ent.html" },
  { id: "ks-johnson", race: "kansas", name: "Johnson County November election", url: "https://www.jocoelection.org/events-elections/november-3-2026-general-election" },
] as const;

export type SourceId = (typeof monitorSources)[number]["id"];
export interface CandidateCount { name: string; party: string; votes: number; electionDay: number; early: number; mail: number; provisional: number }
export interface Publication { title: string; url: string }
export interface ParsedMonitor {
  status: "waiting" | "setup" | "reporting" | "review";
  message: string;
  candidates?: CandidateCount[];
  totalVotes?: number;
  reportedPrecincts?: number;
  totalPrecincts?: number;
  sourceUpdated?: string;
  sourceSubmitted?: string;
  publications?: Publication[];
}

function rows(body: string): Record<string, unknown>[] {
  const data: unknown = JSON.parse(body);
  if (!Array.isArray(data) || !data.length || data.some(row => !row || typeof row !== "object"))
    throw new Error("Expected a nonempty official JSON array.");
  return data;
}
function count(value: unknown): number {
  if (!/^(0|[1-9]\d*)$/.test(String(value))) throw new Error("Invalid vote or precinct count.");
  const n = Number(value);
  if (!Number.isSafeInteger(n)) throw new Error("Count exceeds supported range.");
  return n;
}

export function parseNorthCarolina(catalog: string, countiesBody: string, resultsBody: string): ParsedMonitor {
  if (!rows(catalog).some(row => row.edt === "11/03/2026" && row.con === "1"))
    throw new Error("November 3, 2026 election missing from the official catalog.");
  const counties = rows(countiesBody);
  if (counties.length !== 101 || new Set(counties.map(row => row.cid)).size !== 101 ||
      counties.some(row => !/^(0|[1-9]\d?|100)$/.test(String(row.cid)) ||
        !String(row.tle).startsWith("11/03/2026 ") || !String(row.tle).includes("GENERAL ELECTION") ||
        /TEST|MOCK/i.test(String(row.tle))))
    throw new Error("County coverage or election identity changed; review required.");
  const state = counties.find(row => row.cid === "0");
  if (!state || state.cnm !== "STATE") throw new Error("Statewide status record missing.");
  const all = rows(resultsBody);
  const senate = all.filter(row => /^US SENATE \(VOTE FOR 1\)$/.test(String(row.cnm)));
  if (senate.length < 4 || senate.some(row => row.cid !== "0" || row.gid !== "1383" || row.lid !== "1383" || row.vfr !== "1"))
    throw new Error("November Senate contest identity changed; review required.");
  const required = new Map([["Michael Dublin", "GRE"], ["Roy Cooper", "DEM"], ["Shannon W. Bray", "LIB"], ["Michael Whatley", "REP"]]);
  if ([...required].some(([name, party]) => !senate.some(row => row.bnm === name && row.pty === party)) ||
      senate.some(row => !required.has(String(row.bnm)) && !/write.in/i.test(String(row.bnm))) ||
      new Set(senate.map(row => row.bnm)).size !== senate.length)
    throw new Error("Senate candidate configuration changed; review required.");
  const candidates = senate.map(row => {
    const candidate = { name: String(row.bnm), party: String(row.pty), votes: count(row.vct), electionDay: count(row.evc), early: count(row.ovc), mail: count(row.avc), provisional: count(row.pvc) };
    if (candidate.votes !== candidate.electionDay + candidate.early + candidate.mail + candidate.provisional)
      throw new Error("Candidate voting-method counts do not reconcile.");
    return candidate;
  });
  const totalVotes = candidates.reduce((sum, candidate) => sum + candidate.votes, 0);
  const reportedPrecincts = count(state.prt), totalPrecincts = count(state.ptl);
  if (!totalPrecincts || reportedPrecincts > totalPrecincts) throw new Error("Invalid precinct reporting status.");
  return {
    status: totalVotes ? "reporting" : "setup",
    message: totalVotes ? "Officially published statewide Senate totals. Election-night counts are unofficial and may be revised." : "Zero setup votes published; no Senate votes reported yet.",
    candidates, totalVotes, reportedPrecincts, totalPrecincts,
    sourceUpdated: String(state.imp), sourceSubmitted: String(state.sub),
  };
}

export function parseKansas(body: string, sourceUrl: string): ParsedMonitor {
  const text = body.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ");
  if (!/Kansas|Johnson County/i.test(text) || !/election/i.test(text) || /just a moment|verify you are human/i.test(text))
    throw new Error("Official publication page unavailable or returned an access challenge.");
  const publications: Publication[] = [];
  for (const match of body.matchAll(/<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi)) {
    const title = match[2].replace(/<[^>]*>/g, " ").replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();
    const context = `${title} ${match[1]} ${match[0]}`;
    if (!/result|election.night|\benr\b|\bent\b/i.test(context) || /primary|\b(?:19\d{2}|20(?:0\d|1\d|2[0-5]))\b|mock|kids|test/i.test(context)) continue;
    // This is a publication watch, not permission to admit or follow an unverified feed.
    const url = new URL(match[1].replace(/&amp;/g, "&"), sourceUrl);
    if (url.protocol !== "https:") continue;
    if (url.pathname === "/elections/election-results.html" || url.pathname.startsWith("/forms/")) continue;
    if (!publications.some(item => item.url === url.href)) publications.push({ title: title || "Results publication", url: url.href });
  }
  return {
    status: publications.some(item => /2026|20261103|26elec|general|election.night|\bent\b/i.test(`${item.title} ${item.url}`)) ? "review" : "waiting",
    message: "Watching official publications. A statewide November Senate count feed has not been admitted; Kansas vote totals are unavailable. New result links require election and schema verification.",
    publications,
  };
}

export async function bodyHash(body: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(body));
  return [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, "0")).join("");
}

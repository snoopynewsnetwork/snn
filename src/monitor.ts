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
export interface CandidateCount { name: string; party: string; votes: number; electionDay?: number; early?: number; mail?: number; provisional?: number }
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
    if (url.href.startsWith(sourceUrl + "#") || match[1].startsWith("#")) continue;
    if (url.pathname === "/elections/election-results.html" || url.pathname.startsWith("/forms/")) continue;
    if (!publications.some(item => item.url === url.href)) publications.push({ title: title || "Results publication", url: url.href });
  }
  return {
    status: publications.some(item => /2026|20261103|26elec|general|election.night|\bent\b/i.test(`${item.title} ${item.url}`)) ? "review" : "waiting",
    message: "Watching official publications. A statewide November Senate count feed has not been admitted; Kansas vote totals are unavailable. New result links require election and schema verification.",
    publications,
  };
}

export function parseKansasResults(body: string): ParsedMonitor {
  const metadata = body.match(/<meta\b[^>]*name=["']Keywords["'][^>]*content=["']([^"']+)["']/i)?.[1];
  if (!metadata || !/2026 General Election Results/i.test(metadata) || /primary|test|mock/i.test(metadata))
    throw new Error("Kansas page is not the 2026 general election; review required.");
  const sourceUpdated = body.match(/<span\b[^>]*id\s*=\s*["']time-stamp["'][^>]*>([^<]+)<\/span>/i)?.[1].trim();
  const clock = sourceUpdated?.match(/^(\d{2})\/(\d{2})\/(\d{4})\s+(\d{1,2}):(\d{2})\s+[AP]M$/);
  const sourceDay = clock ? `${clock[3]}-${clock[1]}-${clock[2]}` : "";
  const parsedDay = new Date(`${sourceDay}T00:00:00Z`);
  if (!clock || !Number.isFinite(parsedDay.getTime()) || parsedDay.toISOString().slice(0, 10) !== sourceDay || sourceDay < "2026-11-03" || Number(clock[4]) < 1 || Number(clock[4]) > 12 || Number(clock[5]) > 59)
    throw new Error("Kansas election-date timestamp changed; review required.");
  const countySelect = body.match(/<select\b[^>]*name=["']county-ddl["'][^>]*>([\s\S]*?)<\/select>/i)?.[1];
  const countyLinks = [...(countySelect ?? "").matchAll(/<option\b[^>]*value=["']([a-z-]+\.html)["']/gi)].map(match => match[1]);
  if (countyLinks.length !== 105 || new Set(countyLinks).size !== 105)
    throw new Error("Kansas all-county publication scope changed; review required.");
  const headings = [...body.matchAll(/<h3>United States Senate<\/h3>/g)];
  if (headings.length !== 1) throw new Error("Kansas Senate contest missing or duplicated.");
  const section = body.slice(headings[0].index).split("<!-- end of .race-candidate-list -->")[0];
  if (!/id=["']1001["']/.test(section)) throw new Error("Kansas Senate contest ID changed.");
  const reporting = section.match(/Precincts Reporting:\s*([\d,]+) of ([\d,]+)/);
  const displayedCount = (value: string) => {
    if (!/^(?:0|[1-9]\d*|[1-9]\d{0,2}(?:,\d{3})+)$/.test(value)) throw new Error("Invalid Kansas numeric display.");
    return count(value.replace(/,/g, ""));
  };
  if (!reporting) throw new Error("Kansas precinct status missing.");
  const reportedPrecincts = displayedCount(reporting[1]), totalPrecincts = displayedCount(reporting[2]);
  if (!totalPrecincts || reportedPrecincts > totalPrecincts) throw new Error("Invalid Kansas precinct reporting status.");
  const list = section.split(/<div class=["']race-candidate-list["']>/)[1];
  if (!list) throw new Error("Kansas Senate candidate list missing.");
  const values = [...list.matchAll(/<p>([\s\S]*?)<\/p>/g)].map(match => match[1].replace(/<[^>]*>/g, "").trim());
  const expected = [["D-Adam Hamilton", "Adam Hamilton", "DEM"], ["R-Roger Marshall", "Roger Marshall", "REP"], ["L-David C Graham", "David C Graham", "LIB"]];
  if (values.length !== 12 || values[9] !== "Total Votes") throw new Error("Kansas Senate row layout changed; review required.");
  const candidates = expected.map(([label, name, party], i) => {
    if (values[i * 3] !== label) throw new Error("Kansas Senate candidate configuration changed; review required.");
    return { name, party, votes: displayedCount(values[i * 3 + 1]) };
  });
  const totalVotes = displayedCount(values[10]);
  if (totalVotes !== candidates.reduce((sum, candidate) => sum + candidate.votes, 0))
    throw new Error("Kansas Senate candidate totals do not reconcile.");
  return {
    status: totalVotes ? "reporting" : "setup",
    message: totalVotes ? "Official Kansas SOS statewide Senate totals. Counts are unofficial and may be revised." : "Zero setup votes published; no Kansas Senate votes reported yet.",
    candidates, totalVotes, reportedPrecincts, totalPrecincts, sourceUpdated,
  };
}

export async function bodyHash(body: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(body));
  return [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, "0")).join("");
}

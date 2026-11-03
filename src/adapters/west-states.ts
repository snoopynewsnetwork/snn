import type { CandidateCount } from "../monitor";
import type { ElectionAdapter, ElectionResult, ElectionTarget } from "./types";
import { cnnSource, withCnnFallback, type CnnRace } from "./northeast-cnn.ts";
import { HEADERS, cleanName, count, csv, exactUniverse, guarded, json, party, tally, text, type Universe } from "./west-common.ts";

// Nebraska, Minnesota and California official statewide feeds.

function precincts(reported: number, total: number, label: string) {
  if (!total || reported > total) throw new Error(`${label} precinct status invalid.`);
  return { reportedPrecincts: reported, totalPrecincts: total };
}

// ---------------------------------------------------------------- Nebraska
// Nebraska SOS results site media CSVs (ResultsMedia.aspx). Dan Osborn is a petition
// (independent) candidate; the desk compares Osborn with Ricketts, not a Democrat.
const NE = "https://electionresults.nebraska.gov";
interface NeContest { target: ElectionTarget; source: string; race: string; area: string; universe: Universe }
export const neContests: NeContest[] = [
  {
    target: { id: "senate-ne", state: "NE", chamber: "senate", name: "Nebraska U.S. Senate (Osborn I vs. Ricketts R)" },
    source: "ne-statewide", race: "For United States Senator - 6 Year Term", area: "",
    universe: [["Pete Ricketts", "REP"], ["Dan Osborn", "IND"], ["Mike Marvin", "LMN"], ["Robin Richards", "NWP"], ["Chuck Conboy", "AFP"]],
  },
  {
    target: { id: "house-ne-02", state: "NE", chamber: "house", district: "2", name: "NE-02" },
    source: "ne-congress", race: "For Representative in Congress - 2 Year Term", area: "District 02",
    universe: [["Brinker Harding", "REP"], ["Denise Powell", "DEM"], ["Eric Michael Foreman", "LIB"]],
  },
];

const NE_HEADER = "RaceID,RaceName,PartyCode,AreaType,AreaNum,OfficeSeqNo,BallotOrder,CandidateID,CandidateName,CurrentDateTime,VoteFor,CandidateVotes,CandidatePercentage,PrecinctsReporting";

export function parseNebraska(body: string, spec: NeContest): ElectionResult {
  const rows = csv(body);
  if (!rows.length || rows[0].slice(0, 14).join(",") !== NE_HEADER) throw new Error("Nebraska CSV layout changed.");
  const mine = rows.slice(1).filter(row => row[1].replace(/\s+/g, " ").trim() === spec.race && row[4].trim() === spec.area);
  if (!mine.length || new Set(mine.map(row => row[0])).size !== 1) throw new Error(`${spec.race} ${spec.area} missing or duplicated.`);
  const stamps = new Set(mine.map(row => row[9].trim()));
  const status = new Set(mine.map(row => row[13].replace(/^=/, "").trim()));
  if (stamps.size !== 1 || status.size !== 1) throw new Error("Nebraska contest rows are from mixed snapshots.");
  const stamp = [...stamps][0];
  if (!/^1[12]\/\d{1,2}\/2026 \d{1,2}:\d{2}:\d{2} [AP]M$/.test(stamp)) throw new Error("Nebraska results timestamp is not November/December 2026.");
  const ratio = [...status][0].match(/^(\d+)\/(\d+)$/);
  if (!ratio) throw new Error("Nebraska precinct status missing.");
  if (mine.some(row => row[10].trim() !== "1")) throw new Error("Nebraska vote-for changed.");
  const candidates: CandidateCount[] = mine.map(row => ({ name: cleanName(row[8]), party: party(row[2]), votes: count(row[11]) }));
  exactUniverse(candidates, spec.universe, spec.race);
  return tally(candidates, {
    label: "Nebraska Secretary of State official results", coverage: "complete", sourceUpdated: `${stamp} CT`,
    ...precincts(count(ratio[1]), count(ratio[2]), "Nebraska"),
  });
}

export const nebraska: ElectionAdapter = {
  id: "west-ne-sos", version: "2026-11-03.1",
  sources: [
    { id: "ne-home", name: "Nebraska SOS results home", url: `${NE}/default.aspx`, authorityUrl: `${NE}/ResultsMedia.aspx`, official: true, headers: HEADERS },
    { id: "ne-statewide", name: "Nebraska SOS statewide results CSV", url: `${NE}/resultsCSV.aspx?text=All&type=SW&map=CTY`, authorityUrl: `${NE}/ResultsMedia.aspx`, official: true, headers: HEADERS },
    { id: "ne-congress", name: "Nebraska SOS congressional results CSV", url: `${NE}/resultsCSV.aspx?text=All&type=CG&map=DIST`, authorityUrl: `${NE}/ResultsMedia.aspx`, official: true, headers: HEADERS },
  ],
  targets: neContests.map(spec => ({ ...spec.target, sourceId: spec.source })),
  parse: bodies => guarded(neContests.map(spec => spec.target), () => {
    const home = text(bodies, "ne-home").replace(/<[^>]*>/g, " ").replace(/\s+/g, " ");
    if (!/General Election November 3, 2026/i.test(home) || /test|mock/i.test(home.match(/Unofficial Results[^.]{0,80}/)?.[0] ?? ""))
      throw new Error("Nebraska results site is not the November 3, 2026 general election.");
  }, target => {
    const spec = neContests.find(item => item.target.id === target.id)!;
    return parseNebraska(text(bodies, spec.source), spec);
  }),
};

// ---------------------------------------------------------------- Minnesota
// Minnesota SOS election-results media files (electionresults.sos.mn.gov media file
// layout): State;County;Precinct;OfficeID;Office;District;CandidateID;Name;Suffix;
// Incumbent;Party;PrecinctsReporting;TotalPrecincts;Votes;Percent;TotalVotes.
const MN_AUTHORITY = "https://electionresults.sos.mn.gov/";
const mnSenate: ElectionTarget = { id: "senate-mn", state: "MN", chamber: "senate", name: "Minnesota U.S. Senate" };
const mnUniverse: Universe = [["Peggy Flanagan", "DEM"], ["Michele Tafoya", "REP"], ["Marisa Simonetti", "IND"], ["Rebecca Whiting", "LIB"], ["WRITE-IN", "WRITE-IN"]];

export function parseMinnesotaSenate(body: string): ElectionResult {
  const rows = body.split(/\r?\n/).filter(line => line.trim()).map(line => line.split(";"));
  if (!rows.length || rows.some(row => row.length !== 16 || row[0] !== "MN")) throw new Error("Minnesota media file layout changed.");
  if (rows.some(row => row[3] !== "0102" || row[4] !== "U.S. Senator" || row[1] || row[2])) throw new Error("Minnesota file is not the statewide U.S. Senate contest.");
  const reported = new Set(rows.map(row => row[11])), total = new Set(rows.map(row => row[12])), sums = new Set(rows.map(row => row[15]));
  if (reported.size !== 1 || total.size !== 1 || sums.size !== 1) throw new Error("Minnesota rows are from mixed snapshots.");
  const candidates: CandidateCount[] = rows.map(row => ({ name: cleanName(row[7]), party: party(row[10]), votes: count(row[13]) }));
  exactUniverse(candidates, mnUniverse, "Minnesota U.S. Senator");
  if (count([...sums][0]) !== candidates.reduce((sum, c) => sum + c.votes, 0)) throw new Error("Minnesota candidate votes do not reconcile with the contest total.");
  return tally(candidates, {
    label: "Minnesota Secretary of State official results", coverage: "complete",
    ...precincts(count([...reported][0]), count([...total][0]), "Minnesota"),
  });
}

// The SOS file host timed out from Cloudflare's network in production (200 locally), so
// CNN's race API backs it up. CNN replaces only a missing or rejected official result.
const mnCnn: CnnRace = {
  target: mnSenate, key: "2026-SG-MN",
  candidates: ["Peggy Flanagan", "Michele Tafoya", "Marisa Simonetti", "Rebecca Whiting", "Total Write-ins"],
  why: "Minnesota SOS results file host timed out from the hosted collector",
};

export const minnesota: ElectionAdapter = {
  id: "west-mn-sos", version: "2026-11-03.2",
  sources: [{
    id: "mn-senate", name: "Minnesota SOS U.S. Senate statewide media file",
    url: "https://electionresultsfiles.sos.mn.gov/20261103/ussenate.txt", authorityUrl: MN_AUTHORITY, official: true, headers: HEADERS,
  }, cnnSource(mnCnn.key)],
  targets: [{ ...mnSenate, sourceId: "mn-senate" }],
  // The dated 20261103 path is the election identity; the pinned ballot guards the contest.
  parse: bodies => {
    const official: ElectionResult = bodies["mn-senate"] === undefined
      ? { status: "unavailable", message: "Minnesota SOS results file not fetched this cycle." }
      : { ...guarded([mnSenate], () => {}, () => parseMinnesotaSenate(text(bodies, "mn-senate")))[mnSenate.id], sourceId: "mn-senate" };
    return { [mnSenate.id]: withCnnFallback(official, mnCnn, bodies) };
  },
};

// ---------------------------------------------------------------- California
// California SOS results API (JSON service of electionresults.sos.ca.gov; the HTML site
// itself sits behind an Incapsula challenge, the API does not).
const CA_AUTHORITY = "https://electionresults.sos.ca.gov/";
interface CaContest { target: ElectionTarget; district: number; universe: Universe }
export const caContests: CaContest[] = [
  { target: { id: "house-ca-22", state: "CA", chamber: "house", district: "22", name: "CA-22" }, district: 22, universe: [["David G. Valadao", "REP"], ["Randy Villegas", "DEM"]] },
  { target: { id: "house-ca-48", state: "CA", chamber: "house", district: "48", name: "CA-48" }, district: 48, universe: [["Jim Desmond", "REP"], ["Marni von Wilpert", "DEM"]] },
];

export function parseCalifornia(body: Record<string, string>, spec: CaContest): ElectionResult {
  const data = json(body, `ca-${spec.district}`);
  if (data.raceTitle !== `U.S. House of Representatives District ${spec.district} - Districtwide Results`) throw new Error("California race title changed.");
  const time = String(data.ReportingTime ?? "");
  if (!/^(November|December) \d{1,2}, 2026, /.test(time)) throw new Error("California report is not from the November 2026 general election.");
  const reporting = String(data.Reporting ?? "").match(/\(([\d,]+) of ([\d,]+)\) precincts reporting/);
  if (!reporting) throw new Error("California precinct status missing.");
  if (!Array.isArray(data.candidates)) throw new Error("California candidates missing.");
  const candidates: CandidateCount[] = data.candidates.map((row: any) => ({ name: cleanName(row.Name), party: party(row.Party), votes: count(row.Votes) }));
  exactUniverse(candidates, spec.universe, `CA-${spec.district}`);
  return tally(candidates, {
    label: "California Secretary of State official results", coverage: "complete", sourceUpdated: `${time} PT`,
    ...precincts(count(reporting[1]), count(reporting[2]), "California"),
    note: "California counts mail ballots for weeks; precincts reporting is not vote completion.",
  });
}

export const california: ElectionAdapter = {
  id: "west-ca-sos", version: "2026-11-03.1",
  sources: caContests.map(spec => ({
    id: `ca-${spec.district}`, name: `California SOS U.S. House District ${spec.district}`,
    url: `https://api.sos.ca.gov/returns/us-rep/district/${spec.district}`, authorityUrl: CA_AUTHORITY, official: true, headers: HEADERS,
  })),
  targets: caContests.map(spec => ({ ...spec.target, sourceId: `ca-${spec.district}` })),
  parse: bodies => guarded(caContests.map(spec => spec.target), () => {}, target => parseCalifornia(bodies, caContests.find(spec => spec.target.id === target.id)!)),
};

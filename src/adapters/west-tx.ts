import type { CandidateCount } from "../monitor";
import type { ElectionAdapter, ElectionResult, ElectionTarget } from "./types";
import { HEADERS, base64Json, cleanName, count, exactUniverse, guarded, json, party, tally, type Universe } from "./west-common.ts";

// Texas Secretary of State election-night reporting (Civix "IVIS" ENR, linked from
// sos.state.tx.us). One statewide JSON document per election; its sections are base64 JSON.
const API = "https://goelect.txelections.civixapps.com/api-ivis-system/api/s3/enr";
const AUTHORITY = "https://www.sos.state.tx.us/elections/index.shtml";
const EID = "53815";

interface TxRace { target: ElectionTarget; section: "Federal" | "StateWide"; race: string; universe: Universe }

const house = (district: number, universe: Universe, name: string): TxRace => ({
  target: { id: `house-tx-${String(district).padStart(2, "0")}`, state: "TX", chamber: "house", district: String(district), name },
  section: "Federal", race: `U. S. REPRESENTATIVE DISTRICT ${district}`, universe,
});

export const txRaces: TxRace[] = [
  {
    target: { id: "senate-tx", state: "TX", chamber: "senate", name: "Texas U.S. Senate" },
    section: "Federal", race: "U. S. SENATOR",
    universe: [["KEN PAXTON", "REP"], ["JAMES TALARICO", "DEM"], ["TED BROWN", "LIB"], ["AVERY AYERS", "WRITE-IN"],
      ['BRADFORD "BRAD" HALL', "WRITE-IN"], ["ZUL MOHAMED", "WRITE-IN"], ["JADE SIMMONS", "WRITE-IN"]],
  },
  {
    target: { id: "governor-tx", state: "TX", chamber: "governor", name: "Texas governor (Abbott cue)" },
    section: "StateWide", race: "GOVERNOR",
    universe: [["GREG ABBOTT", "REP"], ["GINA HINOJOSA", "DEM"], ["PAT DIXON", "LIB"], ["EDWARD EARL GILES", "WRITE-IN"],
      ["JENN MACK", "WRITE-IN"], ["JINGHPAW MAJOISHINGRA", "WRITE-IN"], ["MIKE MILLER", "WRITE-IN"]],
  },
  house(15, [["MONICA DE LA CRUZ", "REP"], ["BOBBY PULIDO", "DEM"]], "TX-15"),
  house(9, [["ALEX MEALER", "REP"], ["LETICIA GUTIERREZ", "DEM"]], "TX-09 (redraw group)"),
  house(28, [["TANO E. TIJERINA", "REP"], ["HENRY CUELLAR", "DEM"], ["MARLÓN DURÁN", "GRE"]], "TX-28 (redraw group)"),
  house(32, [["JACE YARBROUGH", "REP"], ["DAN BARRIOS", "DEM"]], "TX-32 (redraw group)"),
  house(34, [["ERIC FLORES", "REP"], ["VICENTE GONZALEZ", "DEM"], ["CHRIS ROYAL", "LIB"], ["EDDIE ESPINOZA", "GRE"]], "TX-34 (redraw group)"),
  house(35, [["CARLOS DE LA CRUZ", "REP"], ["JOHNNY C. GARCIA", "DEM"]], "TX-35 (redraw group)"),
];

export function parseTexasRace(sections: Record<string, any>, spec: TxRace): ElectionResult {
  const races = sections[spec.section]?.Races;
  if (!Array.isArray(races)) throw new Error(`${spec.section} races missing.`);
  const matches = races.filter(race => String(race?.N).trim() === spec.race);
  if (matches.length !== 1) throw new Error(`${spec.race} missing or duplicated.`);
  const rows = matches[0].Candidates;
  if (!Array.isArray(rows) || !rows.length) throw new Error(`${spec.race} candidates missing.`);
  const candidates: CandidateCount[] = rows.map((row: any) => {
    const votes = count(row.V), early = count(row.EV);
    if (early > votes) throw new Error(`${spec.race} early votes exceed total votes.`);
    return { name: cleanName(row.N), party: party(row.P), votes, early };
  });
  exactUniverse(candidates, spec.universe, spec.race);
  const home = sections.Home;
  const reporting = home?.CountiesReporting;
  const note = reporting ? `${count(reporting.CR)} of ${count(reporting.CT)} Texas counties have reported statewide (not race-specific, not a vote-completion share).` : undefined;
  return tally(candidates, {
    label: "Texas Secretary of State official election-night results", coverage: "complete",
    sourceUpdated: home?.LastUpdatedTime ? `${home.LastUpdatedTime} CT` : undefined, note,
  });
}

export const texas: ElectionAdapter = {
  id: "west-tx-sos", version: "2026-11-03.1",
  sources: [
    { id: "tx-constants", name: "Texas SOS ENR election catalog", url: `${API}/electionConstants`, authorityUrl: AUTHORITY, official: true, headers: HEADERS },
    { id: "tx-election", name: "Texas SOS ENR November general election", url: `${API}/election/${EID}`, authorityUrl: AUTHORITY, official: true, headers: HEADERS, maxBytes: 6_000_000 },
  ],
  targets: txRaces.map(spec => ({ ...spec.target, sourceId: "tx-election" })),
  parse: bodies => {
    const sections: Record<string, any> = {};
    return guarded(txRaces.map(spec => spec.target), () => {
      const catalog = base64Json(json(bodies, "tx-constants").upload, "Texas catalog");
      const entry = catalog?.electionInfo?.["2026"]?.GE?.[EID];
      if (!entry || entry.N !== "2026 NOVEMBER GENERAL ELECTION" || entry.ET !== "GE") throw new Error(`Texas election ${EID} is not the 2026 November general election.`);
      const election = json(bodies, "tx-election");
      if (!String(election.Version).startsWith(`enr/${EID}/`)) throw new Error("Texas ENR document is for a different election.");
      for (const key of ["Home", "Federal", "StateWide"]) sections[key] = base64Json(election[key], `Texas ${key}`);
      if (sections.Home.ElecDate !== "11032026") throw new Error("Texas ENR election date is not 11/03/2026.");
    }, target => parseTexasRace(sections, txRaces.find(spec => spec.target.id === target.id)!));
  },
};

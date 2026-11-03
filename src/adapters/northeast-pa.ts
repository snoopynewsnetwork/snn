import type { CandidateCount } from "../monitor";
import type { ElectionAdapter, ElectionResult, ElectionTarget } from "./types";
import { count, json, party, perTarget, requireUniverse, review, tally, unavailable } from "./northeast-common.ts";
import { CNN_AUTHORITY, parseCnnRace, type CnnRace } from "./northeast-cnn.ts";

// Pennsylvania Department of State election returns (https://www.electionreturns.pa.gov/).
// The public Angular app calls these routes; election 117/G is the 2026 General Election.
const API = "https://www.electionreturns.pa.gov/api/ElectionReturn";
const AUTHORITY = "https://www.electionreturns.pa.gov/";
const QUERY = "electionid=117&electiontype=G&isactive=1";

// Full ballot universe per district as published by the Department of State on 2026-11-03.
// The CNN universes are the same people, spelled the way CNN publishes them.
const HOUSE: Record<string, { label: string; candidates: string[]; cnn: string[] }> = {
  "01": { label: "1st Congressional District", candidates: ["BOB HARVIE", "BRIAN FITZPATRICK"], cnn: ["Bob Harvie", "Brian Fitzpatrick"] },
  "07": { label: "7th Congressional District", candidates: ["BOB BROOKS", "RYAN MACKENZIE"], cnn: ["Bob Brooks", "Ryan Mackenzie"] },
  "08": { label: "8th Congressional District", candidates: ["PAIGE COGNETTI", "ROB BRESNAHAN JR"], cnn: ["Paige Cognetti", "Rob Bresnahan"] },
  "10": { label: "10th Congressional District", candidates: ["JANELLE STELSON", "SCOTT PERRY"], cnn: ["Janelle Stelson", "Scott Perry"] },
};
const cnnKey = (district: string) => `2026-HG-PA-${Number(district)}`;

// PA-07 and PA-10 are the two members of the guide's house-pa-07-10 group.
const targets: ElectionTarget[] = Object.keys(HOUSE).map(district => ({
  id: `house-pa-${district}`, state: "PA", name: `Pennsylvania Congressional District ${Number(district)}`, chamber: "house", district, sourceId: "pa-congress",
}));

interface Gate { isTesting: boolean }

export function pennsylvaniaGate(body: string | undefined): Gate {
  const data = json(body, "Pennsylvania election status");
  const rows = Array.isArray(data) ? data : [];
  if (rows.length !== 1) throw new Error("Pennsylvania election status shape changed.");
  const row = rows[0];
  if (row.ElectionID !== 117 || row.ElectionType !== "G" || row.ElectionDate !== "2026-11-03T00:00:00" || !/^2026 General Election\b/.test(String(row.ElectionName)))
    throw new Error("Pennsylvania election identity is not the November 3, 2026 general election.");
  if (typeof row.IsTesting !== "boolean") throw new Error("Pennsylvania testing flag missing.");
  return { isTesting: row.IsTesting };
}

function district(data: any, spec: { label: string; candidates: string[] }): CandidateCount[] {
  const groups = data?.Election?.["Representative in Congress"];
  if (!Array.isArray(groups) || groups.length !== 1) throw new Error("Pennsylvania Congress office shape changed.");
  const matches = Object.entries(groups[0]).filter(([key]) => key.split("$$")[0] === spec.label);
  if (matches.length !== 1) throw new Error(`${spec.label} missing or duplicated.`);
  const entries = matches[0][1] as any[];
  if (!Array.isArray(entries) || entries.length !== 1 || entries[0].District !== spec.label) throw new Error(`${spec.label} identity changed.`);
  const rows: any[] = entries[0].Candidates;
  if (!Array.isArray(rows) || rows.some(row => row.ElectionYear !== "2026" || row.OfficeName !== "Representative in Congress"))
    throw new Error(`${spec.label} is not the 2026 Representative in Congress contest.`);
  requireUniverse(rows.map(row => String(row.CandidateName)), spec.candidates, spec.label);
  return rows.map(row => {
    const candidate = {
      name: String(row.CandidateName), party: party(String(row.PartyName)), votes: count(row.Votes),
      electionDay: count(row.ElectionDayVotes), mail: count(row.MailInVotes), provisional: count(row.ProvisionalVotes),
    };
    if (candidate.votes !== candidate.electionDay + candidate.mail + candidate.provisional)
      throw new Error(`${spec.label} voting-method counts do not reconcile.`);
    return candidate;
  });
}

function parseOfficial(bodies: Record<string, string>): Record<string, ElectionResult> {
  let gate: Gate;
  try {
    gate = pennsylvaniaGate(bodies["pa-status"]);
  } catch (error) {
    const message = `Pennsylvania identity gate failed: ${error instanceof Error ? error.message : String(error)}`;
    return Object.fromEntries(targets.map(target => [target.id, unavailable(message)]));
  }
  return perTarget(targets, target => {
    const spec = HOUSE[target.district!];
    const result = tally(district(json(bodies["pa-congress"], "Pennsylvania Congress"), spec), {
      label: `Pennsylvania Department of State district-wide totals, ${spec.label}`, coverage: "complete",
    });
    if (!gate.isTesting) return { ...result, sourceId: "pa-congress", resultStatus: result.status === "reporting" ? "unofficial" : undefined };
    if (result.status === "reporting")
      return review("Pennsylvania election returns are still in TESTING MODE; test counts rejected.");
    return { ...result, sourceId: "pa-congress", message: `${result.message} Site is in TESTING MODE until polls close at 8 p.m. ET.` };
  });
}

// The official PA DOS result is preferred. CNN is used only when the official
// result for that district is unavailable or under review (blocked, test data or schema drift).
export function parsePennsylvania(bodies: Record<string, string>): Record<string, ElectionResult> {
  const official = parseOfficial(bodies);
  return Object.fromEntries(targets.map(target => {
    const primary = official[target.id];
    if (primary.status !== "unavailable" && primary.status !== "review") return [target.id, primary];
    const spec = HOUSE[target.district!];
    const race: CnnRace = { target, key: cnnKey(target.district!), candidates: spec.cnn, why: "official PA DOS feed unavailable or under review" };
    const body = bodies[`cnn-${race.key}`];
    if (body === undefined) return [target.id, { ...primary, message: `${primary.message} CNN fallback also unavailable this cycle.` }];
    try {
      const fallback = parseCnnRace(body, race);
      if (fallback.status === "unavailable" || fallback.status === "review")
        return [target.id, { ...primary, message: `${primary.message} CNN fallback rejected: ${fallback.message}` }];
      return [target.id, { ...fallback, sourceId: `cnn-${race.key}`, message: `Official PA feed: ${primary.message} Using fallback — ${fallback.message}` }];
    } catch (error) {
      return [target.id, { ...primary, message: `${primary.message} CNN fallback rejected: ${error instanceof Error ? error.message : String(error)}` }];
    }
  }));
}

export const pennsylvaniaAdapter: ElectionAdapter = {
  id: "northeast-pa",
  version: "2026-11-03.2",
  sources: [
    { id: "pa-status", name: "PA DOS election status / testing flag", url: `${API}/GetElectionTesting?methodName=GetElectionTesting&${QUERY}`, authorityUrl: AUTHORITY, official: true },
    { id: "pa-congress", name: "PA DOS Representative in Congress district totals", url: `${API}/GetOfficeData?officeId=11&methodName=GetOfficeDetails&${QUERY}`, authorityUrl: AUTHORITY, official: true },
    ...Object.keys(HOUSE).map(district => ({
      id: `cnn-${cnnKey(district)}`, name: `CNN results API ${cnnKey(district)} (newsroom fallback, not official)`,
      url: `https://politics.api.cnn.io/results/race/${cnnKey(district)}.json`, authorityUrl: CNN_AUTHORITY, official: false,
    })),
  ],
  targets,
  parse: parsePennsylvania,
};

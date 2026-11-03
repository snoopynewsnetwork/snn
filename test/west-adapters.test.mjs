import assert from "node:assert/strict";
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { adapters } from "../src/adapters/west.ts";

// Fixtures are real November 3, 2026 setup responses (see test/fixtures/west/manifest.json
// and docs/live-sources-west.md). Reporting snapshots are derived by editing only counts.
const fx = name => readFileSync(new URL(`./fixtures/west/${name}`, import.meta.url), "utf8");
const guide = JSON.parse(readFileSync(new URL("../public/election-guide.json", import.meta.url), "utf8"));
const byId = id => adapters.find(adapter => adapter.id === id);
const b64 = value => Buffer.from(JSON.stringify(value), "utf8").toString("base64");
const unb64 = value => JSON.parse(Buffer.from(value, "base64").toString("utf8"));

const REGION = new Set(["KS", "TX", "IA", "NE", "MN", "AZ", "CO", "WI", "MT", "CA"]);
const EXTRAS = ["governor-tx", "senate-ks-johnson", "house-tx-09", "house-tx-28", "house-tx-32", "house-tx-34", "house-tx-35"];

const setup = {
  "west-tx-sos": () => ({ "tx-constants": fx("tx-constants.json"), "tx-election": fx("tx-election.json") }),
  "west-ia-sos": () => ({ "west-ia-sos-elections": fx("ia-elections.json"), "west-ia-sos-ver": fx("ia-ver.txt"), "west-ia-sos-summary": fx("ia-summary.json") }),
  "west-co-sos": () => ({ "west-co-sos-elections": fx("co-elections.json"), "west-co-sos-ver": fx("co-ver.txt"), "west-co-sos-summary": fx("co-summary.json") }),
  "west-ne-sos": () => ({ "ne-home": fx("ne-home.html"), "ne-statewide": fx("ne-statewide.csv"), "ne-congress": fx("ne-congress.csv") }),
  "west-mn-sos": () => ({ "mn-senate": fx("mn-senate.txt") }),
  "west-ca-sos": () => ({ "ca-22": fx("ca-22.json"), "ca-48": fx("ca-48.json") }),
  "west-ks": () => ({ "cnn-2026-SG-KS": fx("cnn-2026-SG-KS.json"), "cnn-ks-counties": fx("cnn-ks-counties.json") }),
  "west-az-cnn": () => ({ "cnn-2026-HG-AZ-1": fx("cnn-2026-HG-AZ-1.json"), "cnn-2026-HG-AZ-6": fx("cnn-2026-HG-AZ-6.json") }),
  "west-mt-cnn": () => ({ "cnn-2026-HG-MT-1": fx("cnn-2026-HG-MT-1.json") }),
  "west-wi-cnn": () => ({ "cnn-2026-HG-WI-3": fx("cnn-2026-HG-WI-3.json") }),
};
const run = async (id, bodies = setup[id]()) => byId(id).parse(bodies);

// Texas: rewrite one race's candidate votes inside the base64 Federal/StateWide section.
function texas(section, race, votes, mutate = () => {}) {
  const election = JSON.parse(fx("tx-election.json"));
  const data = unb64(election[section]);
  const row = data.Races.find(item => item.N.trim() === race);
  for (const candidate of row.Candidates) if (candidate.LN in votes) { candidate.V = votes[candidate.LN]; candidate.EV = Math.floor(votes[candidate.LN] / 2); }
  mutate(data, election);
  election[section] = b64(data);
  return { ...setup["west-tx-sos"](), "tx-election": JSON.stringify(election) };
}

function clarity(prefix, file, contest, votes) {
  const rows = JSON.parse(fx(file));
  const row = rows.find(item => item.C === contest);
  row.V = votes; row.TV = votes.reduce((a, b) => a + b, 0); row.PR = 1;
  return { ...setup[`west-${prefix}-sos`](), [`west-${prefix}-sos-summary`]: JSON.stringify(rows) };
}

const cnnVotes = (body, votes, released = true) => {
  const data = JSON.parse(body);
  for (const candidate of data.candidates) if (candidate.fullName in votes) candidate.voteNum = votes[candidate.fullName];
  data.totalVote = data.candidates.reduce((sum, candidate) => sum + candidate.voteNum, 0);
  if (data.raceEmbargo) data.raceEmbargo.votesReleased = released;
  return JSON.stringify(data);
};

test("every assigned guide race and extra target is covered exactly once with declared sources", () => {
  const assigned = [...guide.senate, ...guide.house].filter(item => REGION.has(item.code.slice(0, 2)) && !item.group).map(item => item.id);
  const ids = adapters.flatMap(adapter => adapter.targets.map(target => target.id));
  assert.equal(new Set(ids).size, ids.length, "target ids must be unique");
  assert.deepEqual([...ids].sort(), [...assigned, ...EXTRAS].sort());
  assert.ok(!ids.includes("house-tx-redraw"), "group aggregate is computed by the coordinator");
  for (const adapter of adapters) {
    const sources = new Map(adapter.sources.map(source => [source.id, source]));
    for (const target of adapter.targets) assert.ok(sources.has(target.sourceId), `${target.id} provenance source`);
    for (const source of adapter.sources) {
      assert.match(source.url, /^https:\/\//);
      if (/cnn\.io/.test(source.url)) assert.equal(source.official, false, `${source.id} is a newsroom supplier`);
      if (source.dependsOn) { assert.ok(sources.has(source.dependsOn)); assert.match(source.url, /\{version\}/); }
    }
  }
});

test("real November 3 setup responses parse as zero setup with the full candidate universe", async () => {
  const expectedCandidates = { "senate-tx": 7, "governor-tx": 7, "house-tx-34": 4, "senate-ia": 4, "house-ia-02": 5, "senate-ne": 5, "senate-mn": 5, "house-co-05": 4, "house-az-01": 5, "house-wi-03": 4 };
  for (const adapter of adapters) {
    const results = await run(adapter.id);
    for (const target of adapter.targets) {
      const result = results[target.id];
      assert.equal(result.status, "setup", `${target.id}: ${result.message}`);
      assert.equal(result.totalVotes, 0);
      assert.ok(!result.winner && !result.resultStatus, `${target.id} zero setup is not a result`);
      if (expectedCandidates[target.id]) assert.equal(result.candidates.length, expectedCandidates[target.id], target.id);
    }
  }
  const ne = (await run("west-ne-sos"))["senate-ne"];
  assert.deepEqual(ne.candidates.filter(c => ["IND", "REP"].includes(c.party)).map(c => `${c.name}:${c.party}`), ["Pete Ricketts:REP", "Dan Osborn:IND"]);
  assert.ok(!ne.candidates.some(c => c.party === "DEM"), "Nebraska Senate has no Democrat");
  assert.equal(ne.totalPrecincts, 1322);
  assert.equal((await run("west-mn-sos"))["senate-mn"].candidates.find(c => c.name === "Peggy Flanagan").party, "DEM");
});

test("Texas reports cumulative official counts; a later lower snapshot replaces, never sums", async () => {
  const first = (await run("west-tx-sos", texas("Federal", "U. S. SENATOR", { PAXTON: 1000, TALARICO: 900, BROWN: 30 })))["senate-tx"];
  assert.equal(first.status, "reporting");
  assert.equal(first.totalVotes, 1930);
  assert.equal(first.resultStatus, "unofficial");
  assert.equal(first.coverage, "complete");
  assert.equal(first.winner, undefined);
  assert.equal(first.candidates.find(c => c.name === "KEN PAXTON").early, 500);
  const corrected = (await run("west-tx-sos", texas("Federal", "U. S. SENATOR", { PAXTON: 990, TALARICO: 900, BROWN: 30 })))["senate-tx"];
  assert.equal(corrected.totalVotes, 1920);
  assert.equal(corrected.candidates.find(c => c.name === "KEN PAXTON").votes, 990);
  const governor = (await run("west-tx-sos", texas("StateWide", "GOVERNOR", { ABBOTT: 50, HINOJOSA: 40 })))["governor-tx"];
  assert.equal(governor.totalVotes, 90);
});

test("Texas rejects wrong elections for every target and isolates a changed contest", async () => {
  const constants = JSON.parse(fx("tx-constants.json"));
  const catalog = unb64(constants.upload);
  catalog.electionInfo["2026"].GE["53815"].N = "2026 TEST ELECTION";
  const wrong = await run("west-tx-sos", { ...setup["west-tx-sos"](), "tx-constants": JSON.stringify({ upload: b64(catalog) }) });
  for (const result of Object.values(wrong)) assert.equal(result.status, "review");
  const changed = await run("west-tx-sos", texas("Federal", "U. S. REPRESENTATIVE DISTRICT 15", {}, data => {
    data.Races.find(race => race.N === "U. S. REPRESENTATIVE DISTRICT 15").Candidates.push({ ID: 1, N: "NEW PERSON", P: "IND", V: 0, EV: 0 });
  }));
  assert.equal(changed["house-tx-15"].status, "review");
  assert.match(changed["house-tx-15"].message, /candidate universe changed/);
  assert.equal(changed["senate-tx"].status, "setup", "sibling contests keep parsing");
  const early = await run("west-tx-sos", texas("Federal", "U. S. SENATOR", {}, data => { data.Races[0].Candidates[0].EV = 5; }));
  assert.equal(early["senate-tx"].status, "review");
});

test("Clarity (Iowa/Colorado) validates EID identity, version marker and contest totals", async () => {
  const ia = (await run("west-ia-sos", clarity("ia", "ia-summary.json", "United States Senator", [600, 500, 20, 3])))["senate-ia"];
  assert.equal(ia.status, "reporting");
  assert.equal(ia.totalVotes, 1123);
  assert.match(ia.message, /reporting units \(counties\)/);
  assert.equal(ia.reportedPrecincts, undefined, "county upload counts are not precincts");
  const co = (await run("west-co-sos", clarity("co", "co-summary.json", "Representative to the 120th United States Congress - District 8", [300, 310, 9])))["house-co-08"];
  assert.equal(co.totalVotes, 619);
  const listing = JSON.parse(fx("ia-elections.json")).map(row => row.EID === "127077" ? { ...row, ElectionName: "2026 Primary Election", Date: "6/2/2026 12:00:00 AM" } : row);
  const wrong = await run("west-ia-sos", { ...setup["west-ia-sos"](), "west-ia-sos-elections": JSON.stringify(listing) });
  for (const result of Object.values(wrong)) assert.equal(result.status, "review");
  const badVersion = await run("west-co-sos", { ...setup["west-co-sos"](), "west-co-sos-ver": "<html>" });
  assert.equal(badVersion["house-co-05"].status, "review");
  const rows = JSON.parse(fx("ia-summary.json"));
  rows.find(row => row.C === "United States Representative District 3").TV = 7;
  const mismatch = await run("west-ia-sos", { ...setup["west-ia-sos"](), "west-ia-sos-summary": JSON.stringify(rows) });
  assert.equal(mismatch["house-ia-03"].status, "review");
  assert.equal(mismatch["house-ia-01"].status, "setup");
});

test("Nebraska, Minnesota and California parse counts and reject other elections", async () => {
  const neCsv = fx("ne-statewide.csv").replace(/(,"Dan  Osborn ",[^,]+,1,)0,/, "$11200,").replace(/(,"Pete  Ricketts ",[^,]+,1,)0,/, "$11100,");
  const ne = (await run("west-ne-sos", { ...setup["west-ne-sos"](), "ne-statewide": neCsv }))["senate-ne"];
  assert.equal(ne.status, "reporting");
  assert.equal(ne.candidates.find(c => c.name === "Dan Osborn").votes, 1200);
  assert.equal(ne.totalVotes, 2300);
  const nePrimary = await run("west-ne-sos", { ...setup["west-ne-sos"](), "ne-home": fx("ne-home.html").replace("General Election November 3, 2026", "Primary Election May 12, 2026") });
  assert.equal(nePrimary["senate-ne"].status, "review");
  const mixed = fx("ne-congress.csv").replace(/("Denise  Powell ",)[^,]+/, "$111/3/2026 11:59:59 PM");
  assert.equal((await run("west-ne-sos", { ...setup["west-ne-sos"](), "ne-congress": mixed }))["house-ne-02"].status, "review");

  const mn = fx("mn-senate.txt").split("\n").filter(Boolean).map(line => line.split(";"));
  const votes = { "Peggy Flanagan": 700, "Michele Tafoya": 650, "Marisa Simonetti": 5, "Rebecca Whiting": 4, "WRITE-IN": 1 };
  const mnBody = mn.map(row => { row[11] = "12"; row[13] = String(votes[row[7]]); row[15] = "1360"; return row.join(";"); }).join("\n");
  const mnResult = (await run("west-mn-sos", { "mn-senate": mnBody }))["senate-mn"];
  assert.equal(mnResult.totalVotes, 1360);
  assert.equal(mnResult.reportedPrecincts, 12);
  assert.equal((await run("west-mn-sos", { "mn-senate": mnBody.replace(/;1360$/m, ";1361") }))["senate-mn"].status, "review");

  const ca = JSON.parse(fx("ca-22.json"));
  ca.candidates[0].Votes = "12,345"; ca.candidates[1].Votes = "11,000"; ca.Reporting = "5.0% (29 of 575) precincts reporting"; ca.ReportingTime = "November 3, 2026, 9:10 p.m.";
  const caResult = (await run("west-ca-sos", { ...setup["west-ca-sos"](), "ca-22": JSON.stringify(ca) }))["house-ca-22"];
  assert.equal(caResult.totalVotes, 23345);
  assert.equal(caResult.reportedPrecincts, 29);
  const ca2024 = (await run("west-ca-sos", { ...setup["west-ca-sos"](), "ca-48": fx("ca-48.json").replace("November 2, 2026", "November 5, 2024") }));
  assert.equal(ca2024["house-ca-48"].status, "review");
  assert.equal(ca2024["house-ca-22"].status, "setup");
});

test("Kansas prefers the official SOS page and labels the CNN fallback as not official", async () => {
  const official = (await run("west-ks", { ...setup["west-ks"](), "ks-sos": readFileSync(new URL("./fixtures/kansas-general-setup.html", import.meta.url), "utf8") }))["senate-ks"];
  assert.equal(official.status, "setup");
  assert.doesNotMatch(official.message, /CNN/);
  const fallback = (await run("west-ks"))["senate-ks"];
  assert.match(fallback.message, /CNN newsroom results \(not official/);
  assert.match(fallback.message, /Official Kansas SOS page not admitted/);
  const counted = (await run("west-ks", { ...setup["west-ks"](), "cnn-2026-SG-KS": cnnVotes(fx("cnn-2026-SG-KS.json"), { "Adam Hamilton": 400, "Roger Marshall": 500 }) }))["senate-ks"];
  assert.equal(counted.status, "reporting");
  assert.equal(counted.totalVotes, 900);
  const embargoed = (await run("west-ks", { ...setup["west-ks"](), "cnn-2026-SG-KS": cnnVotes(fx("cnn-2026-SG-KS.json"), { "Adam Hamilton": 400 }, false) }))["senate-ks"];
  assert.equal(embargoed.status, "review");
});

test("Johnson County support target is partial coverage, never a statewide total", async () => {
  const county = JSON.parse(fx("cnn-ks-counties.json"));
  for (const candidate of county[0].candidates) candidate.voteNum = { "Adam Hamilton": 6000, "Roger Marshall": 4000, "David Graham": 100 }[candidate.fullName];
  county[0].totalVote = 10100;
  const race = cnnVotes(fx("cnn-2026-SG-KS.json"), { "Adam Hamilton": 6000, "Roger Marshall": 4000, "David Graham": 100 });
  const results = await run("west-ks", { ...setup["west-ks"](), "cnn-ks-counties": JSON.stringify(county), "cnn-2026-SG-KS": race });
  const johnson = results["senate-ks-johnson"];
  assert.equal(johnson.status, "reporting");
  assert.equal(johnson.coverage, "partial");
  assert.match(johnson.message, /Partial geography only/);
  assert.equal(results["senate-ks"].coverage, "complete");
  // Overlapping county and statewide totals are separate targets; nothing is added together.
  assert.equal(results["senate-ks"].totalVotes, 10100);
  const early = await run("west-ks", { ...setup["west-ks"](), "cnn-ks-counties": JSON.stringify(county) });
  assert.equal(early["senate-ks-johnson"].status, "review", "county votes before embargo are rejected");
  const missing = await run("west-ks", { ...setup["west-ks"](), "cnn-ks-counties": "[]" });
  assert.equal(missing["senate-ks-johnson"].status, "review");
  assert.equal(missing["senate-ks"].status, "setup", "county failure does not break the statewide target");
});

test("AZ, MT and WI newsroom fallbacks reject non-production data", async () => {
  const az = JSON.parse(fx("cnn-2026-HG-AZ-6.json"));
  az.externalKey = "test-key";
  const results = await run("west-az-cnn", { ...setup["west-az-cnn"](), "cnn-2026-HG-AZ-6": JSON.stringify(az) });
  assert.equal(results["house-az-06"].status, "review");
  assert.equal(results["house-az-01"].status, "setup");
  const wi = (await run("west-wi-cnn", { "cnn-2026-HG-WI-3": cnnVotes(fx("cnn-2026-HG-WI-3.json"), { "Rebecca Cooke": 10, "Derrick Van Orden": 12 }) }))["house-wi-03"];
  assert.equal(wi.totalVotes, 22);
  assert.match(wi.message, /not official/);
});

test("Minnesota keeps the official SOS file first and falls back to CNN only when it fails", async () => {
  const cnnSetup = fx("cnn-2026-SG-MN.json");
  const cnnCounted = cnnVotes(cnnSetup, { "Peggy Flanagan": 5200, "Michele Tafoya": 4800, "Marisa Simonetti": 40 });
  // Verified official zero setup is never replaced by newsroom counts.
  const official = (await run("west-mn-sos", { "mn-senate": fx("mn-senate.txt"), "cnn-2026-SG-MN": cnnCounted }))["senate-mn"];
  assert.equal(official.status, "setup");
  assert.equal(official.sourceId, "mn-senate");
  assert.equal(official.totalVotes, 0);
  // Hosted fetch timed out: the SOS body is absent, so the labelled CNN race is used.
  const timedOut = (await run("west-mn-sos", { "cnn-2026-SG-MN": cnnCounted }))["senate-mn"];
  assert.equal(timedOut.status, "reporting");
  assert.equal(timedOut.sourceId, "cnn-2026-SG-MN");
  assert.equal(timedOut.totalVotes, 10040);
  assert.equal(timedOut.candidates.find(c => c.name === "Peggy Flanagan").party, "DEM");
  assert.equal(timedOut.winner, undefined);
  assert.match(timedOut.message, /Minnesota SOS results file not fetched/);
  assert.match(timedOut.message, /not official/);
  // A malformed official response (gateway error page) also yields to the fallback.
  assert.equal((await run("west-mn-sos", { "mn-senate": "<html>504 Gateway Timeout</html>", "cnn-2026-SG-MN": cnnSetup }))["senate-mn"].sourceId, "cnn-2026-SG-MN");
  // Fallback data is still validated: test data or a changed field is rejected, not shown.
  const test = JSON.parse(cnnSetup); test.externalKey = "test-key";
  const rejected = (await run("west-mn-sos", { "cnn-2026-SG-MN": JSON.stringify(test) }))["senate-mn"];
  assert.equal(rejected.status, "unavailable");
  assert.match(rejected.message, /CNN fallback rejected/);
  assert.equal((await run("west-mn-sos", {}))["senate-mn"].status, "unavailable");
});

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { adapters } from "../src/adapters/northeast.ts";
import { parseOhio } from "../src/adapters/northeast-oh.ts";
import { parsePennsylvania } from "../src/adapters/northeast-pa.ts";
import { parseDetroit } from "../src/adapters/northeast-detroit.ts";

const fixture = name => readFileSync(new URL(`fixtures/northeast/${name}`, import.meta.url), "utf8");
const guide = JSON.parse(readFileSync(new URL("../public/election-guide.json", import.meta.url), "utf8"));
const REGION = ["OH", "MI", "PA", "NJ", "NY", "ME", "NH", "MS"];
const byId = id => adapters.find(adapter => adapter.id === id);

// Real November 3, 2026 responses captured before polls closed (see docs/live-sources-northeast.md).
const ohio = () => ({ "oh-xml": fixture("oh-xml-head.xml"), "oh-senate": fixture("oh-senate.json"), "oh-house": fixture("oh-house-summary.json") });
const pa = () => ({ "pa-status": fixture("pa-testing.json"), "pa-congress": fixture("pa-office-11.json") });
const live = xml => xml.replace('IsTest="true"', 'IsTest="false"');

function ohioVotes(body, votes) {
  const data = JSON.parse(body);
  for (const contest of data.contestList) {
    let total = 0;
    for (const candidate of contest.candidatesRunning) {
      const n = votes[candidate.primaryCandidate] ?? 0;
      candidate.voteCount = n.toLocaleString("en-US"); candidate.vCount = n; total += n;
    }
    contest.totalContestVotes = total.toLocaleString("en-US");
  }
  return JSON.stringify(data);
}

function paVotes(body, votes) {
  const data = JSON.parse(JSON.parse(body));
  for (const entries of Object.values(data.Election["Representative in Congress"][0]))
    for (const candidate of entries[0].Candidates) {
      const [day, mail, prov] = votes[candidate.CandidateName] ?? [0, 0, 0];
      Object.assign(candidate, { ElectionDayVotes: String(day), MailInVotes: String(mail), ProvisionalVotes: String(prov), Votes: String(day + mail + prov) });
    }
  return JSON.stringify(JSON.stringify(data));
}

function testing(flag, id = 117) {
  const rows = JSON.parse(JSON.parse(fixture("pa-testing.json")));
  rows[0].IsTesting = flag; rows[0].ElectionID = id;
  return JSON.stringify(JSON.stringify(rows));
}

test("every assigned northeast Senate/House target is covered exactly once", () => {
  const assigned = [...guide.senate, ...guide.house]
    .filter(item => REGION.includes((item.code ?? "").slice(0, 2)) && !item.group).map(item => item.id);
  const members = ["house-pa-07", "house-pa-10"]; // house-pa-07-10 group is aggregated by the coordinator.
  const ids = adapters.flatMap(adapter => adapter.targets.map(target => target.id));
  assert.equal(new Set(ids).size, ids.length, "target ids must be unique");
  for (const id of [...assigned, ...members]) assert.ok(ids.includes(id), `missing ${id}`);
  assert.ok(!ids.includes("house-pa-07-10"));
  assert.equal(assigned.length + members.length, 21);
  for (const adapter of adapters) {
    assert.ok(adapter.sources.length <= 10);
    for (const target of adapter.targets) assert.ok(adapter.sources.some(source => source.id === target.sourceId), `${target.id} provenance`);
    for (const source of adapter.sources) {
      assert.match(source.url, /^https:\/\//);
      if (/cnn/.test(source.url)) assert.equal(source.official, false, "newsroom feeds must not claim official status");
    }
  }
});

test("Ohio zero setup is setup, never reporting, and keeps the full ballot universe", () => {
  const out = parseOhio(ohio());
  assert.deepEqual(Object.keys(out).sort(), ["house-oh-01", "house-oh-07", "house-oh-09", "house-oh-10", "house-oh-13", "senate-oh"]);
  for (const result of Object.values(out)) { assert.equal(result.status, "setup"); assert.equal(result.totalVotes, 0); assert.match(result.message, /IsTest=true/); }
  assert.equal(out["senate-oh"].candidates.length, 7);
  assert.equal(out["senate-oh"].totalPrecincts, 8834);
  assert.deepEqual(out["house-oh-07"].candidates.map(c => c.party), ["WRITE-IN", "WRITE-IN", "REP", "DEM"]);
});

test("Ohio counts are reporting only when the XML clears IsTest; test counts are rejected", () => {
  const votes = { "Sherrod Brown": 1200, "Jon Husted": 1100, "Greg Levy": 30, "William B. Redpath": 20, "Emilia Sykes": 500, "Carey Coleman": 450, "Sandeep Dixit": 9 };
  const bodies = { ...ohio(), "oh-senate": ohioVotes(fixture("oh-senate.json"), votes), "oh-house": ohioVotes(fixture("oh-house-summary.json"), votes) };
  const rejected = parseOhio(bodies);
  assert.equal(rejected["senate-oh"].status, "review");
  assert.equal(rejected["senate-oh"].candidates, undefined);
  const out = parseOhio({ ...bodies, "oh-xml": live(bodies["oh-xml"]) });
  const senate = out["senate-oh"];
  assert.equal(senate.status, "reporting");
  assert.equal(senate.totalVotes, 2350);
  assert.equal(senate.resultStatus, "unofficial");
  assert.equal(senate.winner, undefined);
  assert.deepEqual(senate.candidates.filter(c => c.votes).map(c => [c.party, c.votes]), [["DEM", 1200], ["REP", 1100], ["OP", 30], ["LIB", 20]]);
  assert.equal(out["house-oh-13"].totalVotes, 959);
  assert.equal(out["house-oh-01"].status, "setup");
});

test("Ohio cumulative corrections replace prior snapshots rather than summing", () => {
  const first = parseOhio({ ...ohio(), "oh-xml": live(fixture("oh-xml-head.xml")), "oh-senate": ohioVotes(fixture("oh-senate.json"), { "Sherrod Brown": 500, "Jon Husted": 400 }) });
  const corrected = parseOhio({ ...ohio(), "oh-xml": live(fixture("oh-xml-head.xml")), "oh-senate": ohioVotes(fixture("oh-senate.json"), { "Sherrod Brown": 499, "Jon Husted": 400 }) });
  assert.equal(first["senate-oh"].totalVotes, 900);
  assert.equal(corrected["senate-oh"].totalVotes, 899);
  assert.equal(corrected["senate-oh"].candidates[0].votes, 499);
});

test("Ohio wrong election or missing identity file blocks every Ohio target explicitly", () => {
  const wrong = parseOhio({ ...ohio(), "oh-xml": fixture("oh-xml-head.xml").replace('Date="2026-11-03"', 'Date="2026-05-05"') });
  for (const result of Object.values(wrong)) { assert.equal(result.status, "unavailable"); assert.match(result.message, /November 3, 2026/); }
  const missing = parseOhio({ "oh-senate": fixture("oh-senate.json"), "oh-house": fixture("oh-house-summary.json") });
  assert.equal(Object.keys(missing).length, 6);
  assert.ok(Object.values(missing).every(result => result.status === "unavailable"));
});

test("Ohio contest changes are isolated per target", () => {
  const data = JSON.parse(fixture("oh-house-summary.json"));
  data.contestList.find(c => c.name.endsWith("District 09")).candidatesRunning.pop();
  const out = parseOhio({ ...ohio(), "oh-house": JSON.stringify(data) });
  assert.equal(out["house-oh-09"].status, "review");
  assert.match(out["house-oh-09"].message, /candidate universe/);
  assert.equal(out["house-oh-10"].status, "setup");
  assert.equal(out["senate-oh"].status, "setup");
  const html = parseOhio({ ...ohio(), "oh-senate": "<!DOCTYPE html><title>Just a moment...</title>" });
  assert.equal(html["senate-oh"].status, "review");
  assert.equal(html["house-oh-01"].status, "setup");
});

test("Pennsylvania testing mode allows zero setup but rejects test counts", () => {
  const setup = parsePennsylvania(pa());
  assert.deepEqual(Object.keys(setup).sort(), ["house-pa-01", "house-pa-07", "house-pa-08", "house-pa-10"]);
  assert.ok(Object.values(setup).every(result => result.status === "setup" && /TESTING MODE/.test(result.message)));
  const votes = { "BOB BROOKS": [100, 60, 2], "RYAN MACKENZIE": [120, 30, 1] };
  const counted = { ...pa(), "pa-congress": paVotes(fixture("pa-office-11.json"), votes) };
  assert.equal(parsePennsylvania(counted)["house-pa-07"].status, "review");
  const out = parsePennsylvania({ ...counted, "pa-status": testing(false) });
  assert.equal(out["house-pa-07"].status, "reporting");
  assert.equal(out["house-pa-07"].totalVotes, 313);
  assert.deepEqual(out["house-pa-07"].candidates.map(c => [c.party, c.votes, c.mail]), [["DEM", 162, 60], ["REP", 151, 30]]);
  assert.equal(out["house-pa-10"].status, "setup");
});

test("Pennsylvania wrong election and unreconciled methods are rejected", () => {
  assert.ok(Object.values(parsePennsylvania({ ...pa(), "pa-status": testing(false, 116) })).every(result => result.status === "unavailable"));
  const body = JSON.parse(JSON.parse(paVotes(fixture("pa-office-11.json"), { "SCOTT PERRY": [10, 5, 0] })));
  body.Election["Representative in Congress"][0]["10th Congressional District$$11$$"][0].Candidates[1].Votes = "16";
  const out = parsePennsylvania({ "pa-status": testing(false), "pa-congress": JSON.stringify(JSON.stringify(body)) });
  assert.equal(out["house-pa-10"].status, "review");
  assert.equal(out["house-pa-01"].status, "setup");
});

test("CNN fallback is attributed, production-gated and never sets a winner", async () => {
  const me = byId("northeast-me-cnn");
  const bodies = { "cnn-2026-SG-ME": fixture("cnn-2026-SG-ME.json"), "cnn-2026-HG-ME-2": fixture("cnn-2026-HG-ME-2.json") };
  const setup = await me.parse(bodies);
  assert.equal(setup["senate-me"].status, "setup");
  assert.equal(setup["senate-me"].candidates.length, 8);
  assert.match(setup["senate-me"].message, /not official/);

  const data = JSON.parse(fixture("cnn-2026-SG-ME.json"));
  data.candidates[0].voteNum = 5000; data.candidates[1].voteNum = 4800; data.candidates[1].winner = true; data.totalVote = 9800;
  const early = await me.parse({ ...bodies, "cnn-2026-SG-ME": JSON.stringify(data) });
  assert.equal(early["senate-me"].status, "review", "votes before the embargo lifts are test data");
  data.raceEmbargo.votesReleased = true;
  const out = (await me.parse({ ...bodies, "cnn-2026-SG-ME": JSON.stringify(data) }))["senate-me"];
  assert.equal(out.status, "reporting");
  assert.equal(out.totalVotes, 9800);
  assert.equal(out.winner, undefined);
  assert.match(out.message, /CNN projects Susan Collins — newsroom projection/);
  assert.match(out.message, /ranked-choice/);
  assert.equal(out.candidates[2].party, "WRITE-IN");
  assert.equal(early["house-me-02"].status, "setup", "one race failing does not affect the other");

  const test = JSON.parse(fixture("cnn-2026-SG-ME.json")); test.externalKey = "test-key";
  assert.equal((await me.parse({ ...bodies, "cnn-2026-SG-ME": JSON.stringify(test) }))["senate-me"].status, "review");
  const old = JSON.parse(fixture("cnn-2026-SG-ME.json")); old.extractedAt = "2024-11-05T23:00:00";
  assert.equal((await me.parse({ ...bodies, "cnn-2026-SG-ME": JSON.stringify(old) }))["senate-me"].status, "review");
  const mismatch = JSON.parse(JSON.stringify(data)); mismatch.totalVote = 9801;
  assert.equal((await me.parse({ ...bodies, "cnn-2026-SG-ME": JSON.stringify(mismatch) }))["senate-me"].status, "review");
  const primaryShaped = JSON.parse(fixture("cnn-2026-SG-ME.json")); primaryShaped.electionType = "P"; primaryShaped.electionTitle = "";
  assert.equal((await me.parse({ ...bodies, "cnn-2026-SG-ME": JSON.stringify(primaryShaped) }))["senate-me"].status, "review", "shared G/General gate stays strict");
  const missing = await me.parse({ "cnn-2026-HG-ME-2": bodies["cnn-2026-HG-ME-2"] });
  assert.equal(missing["senate-me"].status, "unavailable");
  assert.equal(missing["house-me-02"].status, "setup");
});

test("every CNN fixture parses with its pinned candidate universe", async () => {
  for (const adapter of adapters.filter(a => a.id.endsWith("-cnn"))) {
    const bodies = Object.fromEntries(adapter.sources.map(s => [s.id, fixture(`${s.id}.json`)]));
    const out = await adapter.parse(bodies);
    for (const target of adapter.targets) assert.equal(out[target.id].status, "setup", `${target.id}: ${out[target.id].message}`);
  }
});

test("Detroit city target is official city geography with partial coverage", () => {
  const setup = parseDetroit(fixture("detroit-ev-senate-excerpt.json"));
  assert.equal(setup.status, "setup");
  assert.equal(setup.coverage, "partial");
  assert.equal(setup.totalPrecincts, 452);
  const data = JSON.parse(fixture("detroit-ev-senate-excerpt.json"));
  const senate = data.ballotItems.find(item => item.name[0].text === "United States Senator");
  for (const [i, n] of [[0, 900], [1, 100]]) {
    const option = senate.summaryResults.ballotOptions[i];
    option.voteCount = n; option.groupResults[1].voteCount = n;
  }
  const out = parseDetroit(JSON.stringify(data));
  assert.equal(out.status, "reporting");
  assert.equal(out.coverage, "partial");
  assert.equal(out.totalVotes, 1000);
  assert.match(out.message, /City of Detroit only/);
  senate.summaryResults.ballotOptions[0].groupResults[1].voteCount = 899;
  assert.throws(() => parseDetroit(JSON.stringify(data)), /reconcile/);
  data.election.electionDate = "2026-08-04";
  assert.throws(() => parseDetroit(JSON.stringify(data)), /November 3, 2026/);
});

test("Pennsylvania falls back to CNN only when the official district result is unavailable or under review", () => {
  const cnn = Object.fromEntries(["1", "7", "8", "10"].map(d => [`cnn-2026-HG-PA-${d}`, fixture(`cnn-2026-HG-PA-${d}.json`)]));
  // Official endpoints failing inside workerd: CNN supplies all four districts.
  const blocked = parsePennsylvania(cnn);
  assert.deepEqual(Object.keys(blocked).sort(), ["house-pa-01", "house-pa-07", "house-pa-08", "house-pa-10"]);
  for (const [id, result] of Object.entries(blocked)) {
    assert.equal(result.status, "setup", `${id}: ${result.message}`);
    assert.equal(result.sourceId, `cnn-2026-HG-PA-${Number(id.slice(-2))}`);
    assert.match(result.message, /identity gate failed.*CNN newsroom results \(not official/);
  }
  // Official preferred whenever it verifies, even at zero setup.
  for (const result of Object.values(parsePennsylvania({ ...pa(), ...cnn }))) assert.equal(result.sourceId, "pa-congress");

  // Official test counts are rejected; real CNN counts take over for that district only.
  const data = JSON.parse(cnn["cnn-2026-HG-PA-7"]);
  data.candidates[0].voteNum = 700; data.candidates[1].voteNum = 650; data.totalVote = 1350; data.raceEmbargo.votesReleased = true;
  const counted = { ...pa(), "pa-congress": paVotes(fixture("pa-office-11.json"), { "BOB BROOKS": [1, 0, 0] }), ...cnn, "cnn-2026-HG-PA-7": JSON.stringify(data) };
  const out = parsePennsylvania(counted);
  assert.equal(out["house-pa-07"].status, "reporting");
  assert.equal(out["house-pa-07"].sourceId, "cnn-2026-HG-PA-7");
  assert.deepEqual(out["house-pa-07"].candidates.map(c => [c.party, c.votes]), [["DEM", 700], ["REP", 650]]);
  assert.equal(out["house-pa-07"].winner, undefined);
  assert.equal(out["house-pa-10"].sourceId, "pa-congress");

  // A changed CNN universe or a missing CNN body leaves the explicit official failure in place.
  const changed = JSON.parse(cnn["cnn-2026-HG-PA-8"]); changed.candidates.pop();
  const rejected = parsePennsylvania({ ...cnn, "cnn-2026-HG-PA-8": JSON.stringify(changed) });
  assert.equal(rejected["house-pa-08"].status, "unavailable");
  assert.match(rejected["house-pa-08"].message, /CNN fallback rejected/);
  assert.equal(rejected["house-pa-08"].sourceId, undefined);
  const none = parsePennsylvania({});
  assert.ok(Object.values(none).every(result => result.status === "unavailable" && /CNN fallback also unavailable/.test(result.message)));
  const adapter = byId("northeast-pa");
  assert.equal(adapter.sources.length, 6);
  assert.ok(adapter.sources.filter(s => s.id.startsWith("cnn-")).every(s => s.official === false));
});

test("Ohio falls back per target to verified CNN when official sources are rate-limited or carry test counts", () => {
  const keys = { "senate-oh": "2026-SP-OH", "house-oh-01": "2026-HG-OH-1", "house-oh-07": "2026-HG-OH-7", "house-oh-09": "2026-HG-OH-9", "house-oh-10": "2026-HG-OH-10", "house-oh-13": "2026-HG-OH-13" };
  const cnn = Object.fromEntries([...Object.values(keys), "2026-SG-list"].map(key => [`cnn-${key}`, fixture(`cnn-${key}.json`)]));
  // All three official requests returning HTTP 429 leaves only the CNN bodies.
  const limited = parseOhio(cnn);
  for (const [id, key] of Object.entries(keys)) {
    assert.equal(limited[id].status, "setup", `${id}: ${limited[id].message}`);
    assert.equal(limited[id].sourceId, `cnn-${key}`);
    assert.match(limited[id].message, /Ohio identity gate failed.*CNN newsroom results \(not official/);
  }
  assert.deepEqual(limited["senate-oh"].candidates.map(c => c.party), ["DEM", "REP", "IND", "LIB"]);
  // Verified official setup is preferred over CNN.
  const both = parseOhio({ ...ohio(), ...cnn });
  for (const id of Object.keys(keys)) assert.equal(both[id].sourceId, id === "senate-oh" ? "oh-senate" : "oh-house");

  // Nonzero official counts under IsTest=true are rejected; verified CNN counts replace them.
  const senate = JSON.parse(cnn["cnn-2026-SP-OH"]);
  senate.candidates[0].voteNum = 1000; senate.candidates[1].voteNum = 900; senate.totalVote = 1900; senate.raceEmbargo.votesReleased = true;
  const counted = { ...ohio(), "oh-senate": ohioVotes(fixture("oh-senate.json"), { "Sherrod Brown": 5 }), ...cnn, "cnn-2026-SP-OH": JSON.stringify(senate) };
  const out = parseOhio(counted)["senate-oh"];
  assert.equal(out.status, "reporting");
  assert.equal(out.sourceId, "cnn-2026-SP-OH");
  assert.equal(out.totalVotes, 1900);
  assert.equal(out.winner, undefined);
  assert.match(out.message, /IsTest=true/);

  // CNN files the Ohio special as electionType P / contestType SP. It is admitted only with the
  // Nov 3 embargo times, the exact cross-party field and its listing in CNN's 2026 Senate general list.
  const reject = (mutate, extra = {}) => {
    const data = JSON.parse(cnn["cnn-2026-SP-OH"]); mutate(data);
    const result = parseOhio({ ...cnn, ...extra, "cnn-2026-SP-OH": JSON.stringify(data) })["senate-oh"];
    assert.equal(result.status, "unavailable"); assert.match(result.message, /CNN fallback rejected/);
    return result.message;
  };
  reject(data => { data.contestType = "SG"; });
  assert.match(reject(data => { data.raceEmbargo.assignedPollsClose = Date.parse("2026-05-05T23:30:00Z"); }), /poll times/);
  assert.match(reject(data => { data.candidates[2].majorParty = "DEM"; }), /party field/);
  reject(data => { data.raceType = "H"; data.raceTypeCode = "H"; }); // different office
  reject(data => { data.raceTitle = "Senate"; });
  reject(data => { data.raceEmbargo.votesRelease = Date.parse("2026-05-05T23:30:00Z"); });
  reject(data => { data.candidates = data.candidates.filter(c => c.majorParty === "DEM"); data.totalVote = 0; }); // primary-shaped field
  reject(data => { data.electionType = "G"; data.electionTitle = "General Election"; }); // the SP exception requires CNN's SP filing
  const unlisted = JSON.parse(cnn["cnn-2026-SG-list"]).filter(item => item.ecKey !== "2026-SP-OH");
  assert.match(reject(() => {}, { "cnn-2026-SG-list": JSON.stringify(unlisted) }), /not listed/);
  const noList = { ...cnn }; delete noList["cnn-2026-SG-list"];
  assert.equal(parseOhio(noList)["senate-oh"].status, "unavailable");
  assert.equal(parseOhio(noList)["house-oh-01"].status, "setup", "House fallbacks do not depend on the Senate list");
  const drift = JSON.parse(cnn["cnn-2026-HG-OH-9"]); drift.candidates.push({ ...drift.candidates[0], fullName: "New Person" });
  assert.equal(parseOhio({ ...cnn, "cnn-2026-HG-OH-9": JSON.stringify(drift) })["house-oh-09"].status, "unavailable");
  assert.equal(byId("northeast-oh").sources.length, 10);
});

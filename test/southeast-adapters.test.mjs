import assert from "node:assert/strict";
import { test } from "node:test";
import { readFile } from "node:fs/promises";
import { adapters } from "../src/adapters/southeast.ts";
import { flContests, flContest, flRows } from "../src/adapters/southeast-fl.ts";
import { parseEnhanced } from "../src/adapters/southeast-enhanced.ts";
import { georgiaSpec } from "../src/adapters/southeast-ga-va.ts";
import { scContest } from "../src/adapters/southeast-sc.ts";

// Fixtures are trimmed exact excerpts of real responses; see test/fixtures/southeast/manifest.json.
const fx = name => readFile(new URL(`./fixtures/southeast/${name}`, import.meta.url), "utf8");
const adapter = id => adapters.find(item => item.id === `southeast-${id}`);
const total = result => result.candidates.reduce((sum, candidate) => sum + candidate.votes, 0);
const votes = (result, name) => result.candidates.find(candidate => candidate.name === name).votes;

test("every assigned cheat-sheet target is represented exactly once with declared provenance", async () => {
  const guide = JSON.parse(await readFile(new URL("../public/election-guide.json", import.meta.url), "utf8"));
  const region = new Set(["FL", "GA", "SC", "NC", "VA", "KY", "IN"]);
  const expected = [
    ...guide.senate.filter(race => region.has(race.code)).map(race => race.id),
    ...guide.house.filter(race => !race.group && region.has(race.code.slice(0, 2))).map(race => race.id),
    "governor-fl", "governor-ga",
  ].sort();
  const ids = adapters.flatMap(item => item.targets.map(target => target.id));
  assert.equal(new Set(ids).size, ids.length, "target ids must be unique");
  assert.deepEqual([...ids].sort(), expected);
  assert.equal(ids.length, 27);
  assert.ok(!ids.includes("house-fl-redraw"), "group aggregates belong to the coordinator");
  for (const item of adapters) {
    const sources = new Set(item.sources.map(source => source.id));
    for (const target of item.targets) assert.ok(!target.sourceId || sources.has(target.sourceId), `${target.id} provenance`);
    for (const source of item.sources) {
      assert.ok(source.url.startsWith("https://") && source.authorityUrl.startsWith("https://"));
      if (source.dependsOn) assert.ok(sources.has(source.dependsOn) && source.url.includes("{version}"));
    }
  }
  const newsroom = adapters.flatMap(item => item.sources).filter(source => !source.official);
  assert.deepEqual(newsroom.map(source => source.id), ["cnn-2026-HG-KY-6"]);
});

// ---------- North Carolina ----------
const ncBodies = async (results) => ({
  "nc-elections": await fx("nc-elections.json"), "nc-counties": await fx("nc-county.json"),
  "nc-results": results ?? await fx("nc-results-setup.json"),
});
const ncWithVotes = (rows, gid, table) => JSON.stringify(rows.map(row => {
  if (row.gid !== gid || !(row.bnm in table)) return row;
  const [evc, ovc, avc, pvc, prt] = table[row.bnm];
  return { ...row, evc: String(evc), ovc: String(ovc), avc: String(avc), pvc: String(pvc), vct: String(evc + ovc + avc + pvc), prt: String(prt) };
}).map(row => row.gid === gid ? { ...row, prt: String(Object.values(table)[0][4]) } : row));

test("NC: real November setup is zero setup across Senate and House from one feed", async () => {
  const out = await adapter("nc").parse(await ncBodies());
  assert.deepEqual(Object.keys(out).sort(), ["house-nc-01", "house-nc-05", "house-nc-09", "house-nc-11", "senate-nc"]);
  for (const result of Object.values(out)) {
    assert.equal(result.status, "setup");
    assert.equal(result.totalVotes, 0);
    assert.equal(result.reportedPrecincts, 0);
  }
  assert.equal(out["senate-nc"].totalPrecincts, 2626);
  assert.equal(out["house-nc-01"].totalPrecincts, 290);
  assert.deepEqual(out["house-nc-01"].candidates.map(c => c.party).sort(), ["DEM", "LIB", "REP"]);
  assert.equal(out["senate-nc"].sourceUpdated, "November 3, 2026 3:31 pm");
});

test("NC: cumulative snapshots replace earlier ones, including downward corrections", async () => {
  const rows = JSON.parse(await fx("nc-results-setup.json"));
  const first = await adapter("nc").parse(await ncBodies(ncWithVotes(rows, "1377", {
    "Richard N. Ojeda II": [100, 200, 30, 0, 10], "Richard Hudson": [150, 180, 20, 0, 10] })));
  assert.equal(first["house-nc-09"].status, "reporting");
  assert.equal(first["house-nc-09"].totalVotes, 680);
  assert.equal(first["house-nc-09"].reportedPrecincts, 10);
  assert.equal(first["house-nc-09"].coverage, "complete");
  assert.equal(first["house-nc-09"].winner, undefined);
  assert.equal(first["senate-nc"].status, "setup", "other contests stay independent");
  const corrected = await adapter("nc").parse(await ncBodies(ncWithVotes(rows, "1377", {
    "Richard N. Ojeda II": [90, 200, 30, 0, 12], "Richard Hudson": [150, 170, 20, 0, 12] })));
  assert.equal(corrected["house-nc-09"].totalVotes, 660, "never summed with the prior snapshot");
  assert.equal(votes(corrected["house-nc-09"], "Richard N. Ojeda II"), 320);
});

test("NC: unreconciled methods or changed candidates isolate to the affected contest", async () => {
  const rows = JSON.parse(await fx("nc-results-setup.json"));
  const broken = rows.map(row => row.bnm === "Don Davis" ? { ...row, vct: "5" } : row);
  const out = await adapter("nc").parse(await ncBodies(JSON.stringify(broken)));
  assert.equal(out["house-nc-01"].status, "review");
  assert.equal(out["house-nc-05"].status, "setup");
  const renamed = rows.map(row => row.bnm === "Roy Cooper" ? { ...row, bnm: "Roy A. Cooper" } : row);
  assert.equal((await adapter("nc").parse(await ncBodies(JSON.stringify(renamed))))["senate-nc"].status, "review");
});

test("NC: a 2024 or test county file is rejected for every target", async () => {
  const counties = JSON.parse(await fx("nc-county.json"));
  const old = JSON.stringify(counties.map(row => ({ ...row, tle: row.tle.replace("11/03/2026", "11/05/2024") })));
  const out = await adapter("nc").parse({ ...(await ncBodies()), "nc-counties": old });
  assert.ok(Object.values(out).every(result => result.status === "review"));
  const mock = JSON.stringify(counties.map(row => ({ ...row, tle: `${row.tle} TEST` })));
  assert.ok(Object.values(await adapter("nc").parse({ ...(await ncBodies()), "nc-counties": mock })).every(r => r.status === "review"));
});

// ---------- Florida ----------
test("FL: real November statewide file is zero setup with pinned county scopes", async () => {
  const out = await adapter("fl").parse({ "fl-results": await fx("fl-20261103-setup.txt") });
  assert.equal(Object.keys(out).length, 8);
  for (const result of Object.values(out)) assert.equal(result.status, "setup");
  assert.equal(out["senate-fl"].totalPrecincts, 5626);
  assert.match(out["senate-fl"].message, /67 counties/);
  assert.match(out["house-fl-25"].message, /3 counties/);
  assert.deepEqual(out["governor-fl"].candidates.filter(c => c.party === "REP" || c.party === "DEM").map(c => c.name).sort(),
    ["Donalds / Avila", "Jolly / Graham"]);
});

test("FL: real 2024 counts reconcile and the 2024 file is rejected as the wrong election", async () => {
  const text = await fx("fl-20241105-uss.txt");
  const spec2024 = { ...flContests["senate-fl"], candidates: [
    { name: "Rick Scott", party: "REP" }, { name: "Debbie Mucarsel-Powell", party: "DEM" }, { name: "Ben Everidge", party: "NPA" },
    { name: "Feena Bonoan", party: "LIB" }, { name: "Tuan TQ Nguyen", party: "NPA" }, { name: "Howard Knepper", party: "WRITE-IN" }] };
  const result = flContest(flRows(text, "11/05/2024"), spec2024);
  assert.equal(result.status, "reporting");
  assert.equal(result.totalVotes, 10_757_428, "matches the certified 2024 Senate total");
  assert.equal(votes(result, "Rick Scott"), 5_977_706);
  // The final 2024 file still says 5,448 of 5,612 precincts: precinct ratios are not vote completion.
  assert.deepEqual([result.reportedPrecincts, result.totalPrecincts], [5448, 5612]);
  assert.equal(result.winner, undefined, "complete precincts are not a race call");
  const out = await adapter("fl").parse({ "fl-results": text });
  assert.ok(Object.values(out).every(r => r.status === "review"));
});

test("FL: county rows sum within one snapshot; missing county rows or HTML challenges fail closed", async () => {
  const text = await fx("fl-20261103-setup.txt");
  const lines = text.trimEnd().split("\n");
  const voted = lines.map(line => {
    const cells = line.split("\t");
    if (cells[3] === "USR" && cells[7].trim() === "025") {
      cells[10] = cells[5] === "BRO" ? "50" : cells[10];
      cells[14] = { Moskowitz: cells[5] === "BRO" ? "1000" : "200", Singer: "300" }[cells[11]] ?? "0";
    }
    return cells.join("\t");
  }).join("\n");
  const out = await adapter("fl").parse({ "fl-results": voted });
  assert.equal(out["house-fl-25"].status, "reporting");
  assert.equal(votes(out["house-fl-25"], "Jared Moskowitz"), 1400);
  assert.equal(votes(out["house-fl-25"], "Scott Singer"), 900);
  assert.equal(out["house-fl-25"].reportedPrecincts, 50);
  assert.equal(out["house-fl-22"].status, "setup");
  const missing = lines.filter(line => !(line.includes("\tUSR\t") && line.includes("\tDAD\t") && line.includes("\t027\t"))).join("\n");
  const partial = await adapter("fl").parse({ "fl-results": missing });
  assert.equal(partial["house-fl-27"].status, "review", "lost county coverage is never presented as a full district");
  assert.equal(partial["senate-fl"].status, "setup");
  const challenge = await adapter("fl").parse({ "fl-results": "<!DOCTYPE html><title>Just a moment...</title>" });
  assert.ok(Object.values(challenge).every(r => r.status === "review"));
  assert.ok(Object.values(await adapter("fl").parse({})).every(r => r.status === "review"));
});

// ---------- Georgia / Virginia (Enhanced Voting) ----------
test("GA and VA: real November setup responses are production zero setup", async () => {
  const ga = await adapter("ga").parse({ "ga-results": await fx("ga-20261103-setup.json") });
  assert.deepEqual(Object.keys(ga).sort(), ["governor-ga", "house-ga-01", "house-ga-02", "senate-ga"]);
  for (const result of Object.values(ga)) { assert.equal(result.status, "setup"); assert.equal(result.resultStatus, "unofficial"); }
  assert.deepEqual(ga["senate-ga"].candidates.map(c => `${c.name}/${c.party}`), ["Mike Collins/REP", "Jon Ossoff/DEM"]);
  assert.match(ga["senate-ga"].message, /0 of 159 counties/);
  assert.equal(ga["senate-ga"].reportedPrecincts, undefined, "counties are not precincts");
  const va = await adapter("va").parse({ "va-results": await fx("va-20261103-setup.json") });
  assert.equal(Object.keys(va).length, 4);
  for (const result of Object.values(va)) assert.equal(result.status, "setup");
  assert.equal(va["house-va-07"].candidates.length, 7, "all third-party and write-in choices preserved");
});

test("GA and VA: real certified historical counts parse; wrong elections are rejected", async () => {
  const ga2024 = await fx("ga-20241105-real.json");
  const targets = [{ id: "house-ga-01", state: "GA", name: "GA-01", chamber: "house" }];
  const spec = { ...georgiaSpec, election: { id: "01000000-7316-ae4b-8b87-08dcda4b828a", date: "2024-11-05", name: "November General Election" },
    contests: { "house-ga-01": { ballotItemId: "01000000-d884-2e72-d102-08dcda4b86d5", name: "US House of Representatives - District 1",
      candidates: [{ name: 'Earl L. "Buddy" Carter', party: "REP" }, { name: "Patti Hewitt", party: "DEM" }] } } };
  const real = parseEnhanced({ "ga-results": ga2024 }, spec, targets)["house-ga-01"];
  assert.equal(real.status, "reporting");
  assert.equal(real.totalVotes, 355_857);
  assert.equal(votes(real, 'Earl L. "Buddy" Carter'), 220_576);
  assert.equal(real.candidates[0].electionDay + real.candidates[0].early + real.candidates[0].mail + real.candidates[0].provisional, 220_576);
  assert.equal(real.resultStatus, undefined, "an 'official' publisher label is not treated as certification");
  assert.equal(real.winner, undefined);
  assert.ok(Object.values(await adapter("ga").parse({ "ga-results": ga2024 })).every(r => r.status === "review"));
  assert.ok(Object.values(await adapter("va").parse({ "va-results": await fx("va-20251104-real.json") })).every(r => r.status === "review"));
});

test("GA: certified write-ins may appear; any other ballot change needs review", async () => {
  const data = JSON.parse(await fx("ga-20261103-setup.json"));
  const senate = data.ballotItems.find(item => item.id === georgiaSpec.contests["senate-ga"].ballotItemId);
  const add = name => ({ ...senate.summaryResults.ballotOptions[0], id: name, party: null, name: [{ languageId: "en", text: name }], voteCount: 0, groupResults: [] });
  senate.summaryResults.ballotOptions.push(add("Christina Clement"));
  assert.equal((await adapter("ga").parse({ "ga-results": JSON.stringify(data) }))["senate-ga"].status, "setup");
  senate.summaryResults.ballotOptions.push(add("Unknown Person"));
  const out = await adapter("ga").parse({ "ga-results": JSON.stringify(data) });
  assert.equal(out["senate-ga"].status, "review");
  assert.equal(out["governor-ga"].status, "setup");
});

test("GA: vote-method groups and contest totals must reconcile", async () => {
  const data = JSON.parse(await fx("ga-20261103-setup.json"));
  const item = data.ballotItems.find(entry => entry.id === georgiaSpec.contests["house-ga-02"].ballotItemId);
  item.summaryResults.ballotOptions[0].voteCount = 10;
  item.voteTotal = 10;
  assert.equal((await adapter("ga").parse({ "ga-results": JSON.stringify(data) }))["house-ga-02"].status, "review");
  item.summaryResults.ballotOptions[0].groupResults[0].voteCount = 10;
  const ok = (await adapter("ga").parse({ "ga-results": JSON.stringify(data) }))["house-ga-02"];
  assert.equal(ok.status, "reporting");
  assert.equal(ok.totalVotes, 10);
});

// ---------- South Carolina (Clarity) ----------
const scBodies = async (overrides = {}) => ({
  "sc-version": await fx("sc-version.txt"), "sc-settings": await fx("sc-settings.json"), "sc-summary": await fx("sc-summary-setup.json"), ...overrides,
});

test("SC: real November Clarity setup is zero setup for Senate, SC-01 and SC-02", async () => {
  const out = await adapter("sc").parse(await scBodies());
  for (const id of ["senate-sc", "house-sc-01", "house-sc-02"]) assert.equal(out[id].status, "setup");
  assert.deepEqual(out["senate-sc"].candidates.map(c => `${c.name}/${c.party}`),
    ["Darline Graham/REP", "Kasie Whitener/LIB", "Annie Andrews/DEM", "Mark Hackett/CON", "Write-In/WRITE-IN"]);
  assert.equal(out["senate-sc"].sourceUpdated, "10/30/2026 10:04:18 AM EDT");
});

test("SC: real 2022 Clarity counts parse; wrong election, test mode and stale versions are rejected", async () => {
  const real = JSON.parse(await fx("sc-2022-summary-real.json"));
  const result = scContest(real, { key: "26000", name: "U.S. Senate", candidates: [
    { name: "Tim Scott", party: "REP" }, { name: "Krystle Matthews", party: "DEM" }, { name: "Write-In", party: "WRITE-IN" }] });
  assert.equal(result.totalVotes, 1_066_274 + 627_616 + 1_812);
  assert.equal(result.winner, undefined, "Clarity winner flags are not admitted as calls");
  const out = await adapter("sc").parse(await scBodies({ "sc-summary": JSON.stringify(real) }));
  assert.ok(Object.values(out).every(r => r.status === "review"), "2022 candidates do not match the November ballot");
  const settings = JSON.parse(await fx("sc-settings.json"));
  const variant = patch => JSON.stringify({ ...settings, settings: { electiondetails: { ...settings.settings.electiondetails, ...patch } } });
  for (const patch of [{ electiondate: "6/9/2026" }, { electionid: "126294" }, { istestmode: true }, { istestmode: "true" }, { showtestdatawatermark: "1" }])
    assert.ok(Object.values(await adapter("sc").parse(await scBodies({ "sc-settings": variant(patch) }))).every(r => r.status === "review"), JSON.stringify(patch));
  assert.ok(Object.values(await adapter("sc").parse(await scBodies({ "sc-version": "<html>" }))).every(r => r.status === "review"));
});

test("SC: a later cumulative version replaces the earlier one", async () => {
  const setup = JSON.parse(await fx("sc-summary-setup.json"));
  const at = values => JSON.stringify(setup.map(c => c.K === "27002" ? { ...c, V: values } : c));
  const first = (await adapter("sc").parse(await scBodies({ "sc-summary": at([500, 20, 400, 3]) })))["house-sc-01"];
  const second = (await adapter("sc").parse(await scBodies({ "sc-summary": at([480, 20, 410, 3]) })))["house-sc-01"];
  assert.equal(first.totalVotes, 923);
  assert.equal(second.totalVotes, 913);
  assert.equal(votes(second, "Nancy Lacore"), 410);
});

// ---------- Indiana ----------
const inBodies = async ({ settings, office, buffer } = {}) => {
  const base = JSON.parse(await fx("in-settings.json"));
  const live = settings ? { Root: { ...base.Root, ...settings } } : base;
  const text = office ?? await fx("in-house-setup.json");
  return { "in-settings": JSON.stringify(live), [`in-house-${buffer ?? live.Root.VersionType}`]: text };
};
const inVotes = async (district, table, flags = {}) => {
  const office = JSON.parse(await fx("in-house-setup.json"));
  const officeId = district === "1" ? "4912" : "5256";
  const race = office.Root.StatewideSummary.Race.find(r => r.OFFICEID === officeId);
  for (const c of race.Candidates.Candidate) { c.TOTAL = table[c.NAME_ON_BALLOT] ?? 0; c.isWinner = flags[c.NAME_ON_BALLOT] ?? "F"; }
  const region = office.Root.OfficeCategory.Regions.Region.find(r => r.MAP_JURISDICTION_NAME === district);
  const county = [region.Races.Race].flat()[0];
  for (const c of county.Candidates.Candidate) c.TOTAL_VOTES = table[c.NAME_ON_BALLOT] ?? 0;
  return JSON.stringify(office);
};

test("IN: real November setup reads the buffer that settings selects", async () => {
  const out = await adapter("in").parse(await inBodies());
  assert.equal(out["house-in-01"].status, "setup");
  assert.equal(out["house-in-05"].status, "setup");
  assert.equal(out["house-in-01"].candidates.length, 4, "write-in candidates preserved");
  const other = JSON.parse(await fx("in-settings.json")).Root.VersionType === "A" ? "B" : "A";
  const wrongBuffer = await adapter("in").parse(await inBodies({ buffer: other }));
  assert.ok(Object.values(wrongBuffer).every(r => r.status === "review"), "the inactive buffer is never admitted");
  const primary = await adapter("in").parse(await inBodies({ settings: { CurrentElection: "05/05/2026", ElectionType: "P" } }));
  assert.ok(Object.values(primary).every(r => r.status === "review"));
});

test("IN: district totals must reconcile with county rows; winners only after certification", async () => {
  const reporting = await adapter("in").parse(await inBodies({ office: await inVotes("5", { "J.D. Ford": 900, "Victoria Spartz": 1100 }) }));
  assert.equal(reporting["house-in-05"].status, "reporting");
  assert.equal(reporting["house-in-05"].totalVotes, 2000);
  assert.equal(reporting["house-in-05"].resultStatus, "unofficial");
  const flagged = await adapter("in").parse(await inBodies({ office: await inVotes("5", { "J.D. Ford": 900, "Victoria Spartz": 1100 }, { "Victoria Spartz": "T" }) }));
  assert.equal(flagged["house-in-05"].winner, undefined, "an uncertified winner flag is ignored");
  const certified = await adapter("in").parse(await inBodies({ settings: { Certified: "T" }, office: await inVotes("5", { "J.D. Ford": 900, "Victoria Spartz": 1100 }, { "Victoria Spartz": "T" }) }));
  assert.equal(certified["house-in-05"].winner, "R");
  assert.equal(certified["house-in-05"].resultStatus, "certified");
  const office = JSON.parse(await inVotes("1", { "Frank J. Mrvan": 70, "Barb Regnitz": 30 }));
  office.Root.StatewideSummary.Race.find(r => r.OFFICEID === "4912").Candidates.Candidate[0].TOTAL = 75;
  const mismatch = await adapter("in").parse(await inBodies({ office: JSON.stringify(office) }));
  assert.equal(mismatch["house-in-01"].status, "review");
  assert.equal(mismatch["house-in-05"].status, "setup");
});

// ---------- Kentucky (newsroom fallback) ----------
test("KY-06: CNN newsroom fallback is labeled unofficial and rejects pre-embargo votes", async () => {
  const ky = adapter("ky");
  assert.equal(ky.sources.length, 1);
  assert.equal(ky.sources[0].official, false);
  const setup = await fx("cnn-ky6-setup.json");
  const out = await ky.parse({ "cnn-2026-HG-KY-6": setup });
  assert.equal(out["house-ky-06"].status, "setup");
  assert.equal(out["house-ky-06"].estimatedVotePercent, undefined);
  assert.match(out["house-ky-06"].message, /not official/);
  const data = JSON.parse(setup);
  data.candidates[0].voteNum = 5; data.totalVote = 5;
  assert.equal((await ky.parse({ "cnn-2026-HG-KY-6": JSON.stringify(data) }))["house-ky-06"].status, "review");
  assert.equal((await ky.parse({}))["house-ky-06"].status, "unavailable");
  data.raceEmbargo = { ...data.raceEmbargo, votesReleased: true };
  for (const percent of [0, 1, 99.5, 100, -1, 101, "1", null]) {
    data.percentReporting = percent;
    const result = (await ky.parse({ "cnn-2026-HG-KY-6": JSON.stringify(data) }))["house-ky-06"];
    assert.equal(result.status, "reporting");
    assert.equal(result.estimatedVotePercent, typeof percent === "number" && percent >= 0 && percent <= 100 ? percent : undefined);
  }
});

import assert from "node:assert/strict";
import { test } from "node:test";
import { parseNorthCarolina, parseKansas } from "../src/monitor.ts";

const catalog = JSON.stringify([{ edt: "11/03/2026", con: "1" }]);
const counties = Array.from({ length: 101 }, (_, cid) => ({
  cid: String(cid), cnm: cid ? `County ${cid}` : "STATE",
  tle: "11/03/2026 UNOFFICIAL GENERAL ELECTION RESULTS - STATEWIDE",
  prt: "0", ptl: "2626", imp: "November 3, 2026 12:25 pm", sub: "November 3, 2026 12:25 pm",
}));
const choices = [["Michael Dublin", "GRE"], ["Roy Cooper", "DEM"], ["Shannon W. Bray", "LIB"], ["Michael Whatley", "REP"]];
const results = choices.map(([bnm, pty]) => ({
  cid: "0", cnm: "US SENATE (VOTE FOR 1)", gid: "1383", lid: "1383", vfr: "1", bnm, pty,
  vct: "0", evc: "0", ovc: "0", avc: "0", pvc: "0",
}));
const parse = (c = counties, r = results, e = catalog) => parseNorthCarolina(e, JSON.stringify(c), JSON.stringify(r));

test("NC distinguishes zero setup, cumulative results and downward corrections", () => {
  assert.equal(parse().status, "setup");
  const next = structuredClone(results);
  next[1].vct = next[1].ovc = "200";
  assert.equal(parse(counties, next).totalVotes, 200);
  next[1].vct = next[1].ovc = "190";
  const correction = parse(counties, next);
  assert.equal(correction.totalVotes, 190);
  assert.equal(correction.candidates[1].early, 190);
  assert.equal(correction.candidates[1].electionDay, 0);
  assert.equal(correction.status, "reporting");
});

test("NC rejects stale elections, test products, missing coverage and unreconciled counts", () => {
  assert.throws(() => parse(counties, results, '[{"edt":"11/05/2024","con":"1"}]'));
  assert.throws(() => parse(counties.slice(1)));
  for (const mutation of [
    row => { row.gid = "other-contest"; },
    row => { row.bnm = "Unknown candidate"; },
    row => { row.vct = "1"; },
    row => { row.vct = row.evc = "-1"; },
    row => { row.vct = row.evc = ""; },
  ]) {
    const bad = structuredClone(results); mutation(bad[0]);
    assert.throws(() => parse(counties, bad));
  }
  const testCounties = structuredClone(counties);
  testCounties[0].tle += " TEST";
  assert.throws(() => parse(testCounties));
  assert.throws(() => parse(counties, [...results, results[0]]));
});

test("NC retains newly published write-in choices without double counting statewide totals", () => {
  const writeIn = { ...results[0], bnm: "Write-In (Miscellaneous)", pty: "", vct: "3", pvc: "3" };
  const parsed = parse(counties, [...results, writeIn]);
  assert.equal(parsed.totalVotes, 3);
  assert.equal(parsed.candidates.length, 5);
});

test("Kansas watches publications without admitting primary, historical or arbitrary counts", () => {
  const html = `<h1>Kansas Election Results</h1>
    <a href="/2026-primary.pdf">2026 Primary Results</a>
    <a href="/2024-general.pdf">2024 General Results</a>
    <a href="/2018-general.pdf">2018 General Results</a>
    <a href="/forms/forms_results.aspx">Forms</a>
    <a href="javascript:alert(1)">2026 General Results</a>`;
  assert.equal(parseKansas(html, "https://www.sos.ks.gov/").status, "waiting");
  const publication = parseKansas(html + '<a href="/26elec/general.pdf">2026 General Election Results</a>', "https://www.sos.ks.gov/");
  assert.equal(publication.status, "review");
  assert.deepEqual(publication.publications, [{ title: "2026 General Election Results", url: "https://www.sos.ks.gov/26elec/general.pdf" }]);
  assert.equal(publication.candidates, undefined);
  assert.throws(() => parseKansas("<h1>Just a moment</h1>", "https://www.sos.ks.gov/"));
});

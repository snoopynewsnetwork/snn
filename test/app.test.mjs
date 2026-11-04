import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { randomBytes } from "node:crypto";
import { once } from "node:events";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { setTimeout as delay } from "node:timers/promises";
import { smoke } from "../scripts/smoke.mjs";

test(
  "Worker API uses real Durable Object storage and survives restart",
  { timeout: 90000 },
  async () => {
    const directory = await mkdtemp(join(tmpdir(), "snn-test-"));
    const key = randomBytes(32).toString("hex");
    const vars = join(directory, ".env");
    await writeFile(vars, `ADMIN_TOKEN=${key}\n`);
    const base = "http://127.0.0.1:8899";
    let worker;
    let output = "";
    async function stop() {
      if (!worker || worker.exitCode !== null) return;
      const exited = once(worker, "exit");
      worker.kill("SIGTERM");
      await exited;
      worker = null;
    }
    async function start() {
      output = "";
      worker = spawn(
        "node",
        [
          "node_modules/wrangler/bin/wrangler.js",
          "dev",
          "--port",
          "8899",
          "--ip",
          "127.0.0.1",
          "--env-file",
          vars,
          "--var",
          `ADMIN_TOKEN:${key}`,
          "--persist-to",
          join(directory, "state"),
        ],
        {
          stdio: ["ignore", "pipe", "pipe"],
          env: { ...process.env, CI: "true", WRANGLER_SEND_METRICS: "false" },
        },
      );
      worker.stdout.on("data", (chunk) => {
        output += chunk;
      });
      worker.stderr.on("data", (chunk) => {
        output += chunk;
      });
      for (let i = 0; i < 150; i++) {
        if (worker.exitCode !== null) throw new Error(output);
        try {
          if ((await fetch(`${base}/api/health`)).ok) return;
        } catch {}
        await delay(200);
      }
      throw new Error(`Worker did not start: ${output}`);
    }
    try {
      await start();
      const intro = await fetch(`${base}/intro`);
      assert.equal(intro.status, 200);
      assert.match(intro.headers.get("content-type"), /text\/html/);
      assert.match(intro.headers.get("content-security-policy"), /script-src 'self'/);
      const introHtml = await intro.text();
      assert.match(introHtml, /id="intro-scene"/);
      assert.equal((introHtml.match(/<button\b/g) ?? []).length, 2);
      for (const asset of ["/intro/film.js", "/intro/style.css"]) {
        const response = await fetch(`${base}${asset}`);
        assert.equal(response.status, 200, `${asset} is deployed with the site`);
        assert.doesNotMatch(response.headers.get("content-type"), /text\/html/);
      }
      await smoke(base, key);
      const monitor = await (await fetch(`${base}/api/monitor`)).json();
      assert.equal(monitor.races.filter(race => /^senate-[a-z]{2}$/.test(race.target)).length, 14);
      assert.ok(monitor.races.some(race => race.target === "house-tx-35"));
      assert.equal(monitor.intervalMinutes, 1);
      assert.ok(monitor.sources.length >= 25);
      assert.equal((await fetch(`${base}/api/monitor/refresh`, { method: "POST" })).status, 401);
      assert.equal((await fetch(`${base}/api/monitor/snapshots/999999`)).status, 404);
      const headers = { Authorization: `Bearer ${key}`, "Content-Type": "application/json" };
      const needlePage = await fetch(`${base}/needle`);
      assert.equal(needlePage.status, 200);
      assert.match(await needlePage.text(), /id="chamber-needles"/);
      const needleCatalog = await (await fetch(`${base}/api/needle`)).json();
      assert.equal(needleCatalog.needles.length, 74, '72 races and two chamber needles');
      assert.equal(new Set(needleCatalog.needles.map(n => n.id)).size, 74);
      assert.equal(needleCatalog.needles.filter(n => n.id.endsWith('-control')).length, 2);
      assert.ok(!needleCatalog.needles.some(n => n.id.includes('detroit') || n.id.includes('johnson')));
      assert.equal((await fetch(`${base}/api/needle/missing`)).status, 404);
      assert.equal((await fetch(`${base}/api/needle/house-control`, { method: 'POST' })).status, 405);
      const emptyChamber = await (await fetch(`${base}/api/needle/house-control`)).json();
      assert.equal(emptyChamber.probabilities, null); assert.equal(emptyChamber.missingSeats, 416);
      assert.equal(emptyChamber.ledger.inventoryComplete, true);
      const senateLedger = await (await fetch(`${base}/api/chamber-ledger/senate`)).json();
      assert.equal(senateLedger.seats.length, 100); assert.equal(senateLedger.notUpSeats, 65);
      assert.equal(senateLedger.senateTieBreaker.caucus, 'R');
      assert.equal((await fetch(`${base}/api/chamber-ledger/house`, { method: 'POST' })).status, 405);
      assert.equal((await fetch(`${base}/api/chamber-ledger/invalid`)).status, 404);
      assert.equal((await fetch(`${base}/api/needle/forecast`, { method: 'PUT' })).status, 401);
      const forecastRun = { electionDate: '2026-11-03', modelVersion: 'integration-fixture', asOf: new Date().toISOString(),
        calibrationUrl: 'https://example.org/fixture-calibration', assumptions: ['Synthetic local integration fixture.', ...Array(40).fill('Chunked persistence fixture ' + 'x'.repeat(1900))],
        races: [{ id: 'senate-mi', name: 'Michigan U.S. Senate', seatId: 'senate-mi-2', chamber: 'senate', outcomes: 'DDDR', margins: [1, 2, 3, -1] }],
        fixedSeats: { house: [], senate: [] }, senateTieBreaker: 'R' };
      const publishForecast = body => fetch(`${base}/api/needle/forecast`, { method: 'PUT', headers, body: JSON.stringify(body) });
      assert.equal((await publishForecast({ expectedVersion: 0, run: { ...forecastRun, calibrationUrl: 'javascript:bad' } })).status, 400);
      assert.equal((await publishForecast({ expectedVersion: 0, run: forecastRun })).status, 201);
      assert.equal((await publishForecast({ expectedVersion: 0, run: forecastRun })).status, 409);
      const raceNeedle = await (await fetch(`${base}/api/needle/senate-mi`)).json();
      assert.equal(raceNeedle.status, 'ready'); assert.equal(raceNeedle.probabilities.D, .75);
      assert.equal(raceNeedle.completion.status, 'pending');
      assert.deepEqual((await (await fetch(`${base}/api/completion/senate-mi/history`)).json()).observations, []);
      assert.equal((await fetch(`${base}/api/completion/senate-mi/history?after=-1`)).status, 400);
      const night = await (await fetch(`${base}/api/election-night`)).json();
      assert.equal(night.guide.senate.length, 14);
      assert.equal(night.guide.house.length, 51);
      assert.deepEqual(night.observations, []);
      assert.equal(night.coverage.configured, 65);
      assert.equal(night.coverage.total, 65);
      assert.ok(night.liveResults.find(result => result.target === 'house-ky-06').countyResult);
      assert.equal(night.sources.find(source => source.id === 'civic-ky06-counties').official, false);
      assert.ok(!night.liveResults.some(result => result.target === 'house-ky-06-counties'), 'County support is nested, not a duplicate watch item');
      assert.equal(new Set(night.liveResults.map(result => result.target)).size, night.liveResults.length);
      for (const item of [...night.guide.senate, ...night.guide.house]) assert.ok(night.liveResults.some(result => result.target === item.id), item.id);
      assert.equal(night.intervalMinutes, 1);
      assert.ok(night.sources.every(source => /^https?:/.test(source.authorityUrl)));
      assert.equal((await fetch(`${base}/api/election-night/refresh`)).status, 405);
      const endpoint = `${base}/api/election-night/senate-mi`;
      const input = {
        status: "partial", margin: 8, reporting: 20, winner: null, gopSeats: null,
        sourceUrl: "https://example.org/results", body: "Partial returns, substantial absentee vote outstanding.",
        observedAt: new Date().toISOString(), expectedVersion: 0,
      };
      const put = (url, body, auth = headers) => fetch(url, { method: "PUT", headers: auth, body: JSON.stringify(body) });
      assert.equal((await put(endpoint, input, { "Content-Type": "application/json" })).status, 401);
      assert.equal((await fetch(`${base}/api/election-night`, { method: "POST" })).status, 405);
      assert.equal((await put(`${base}/api/election-night/missing`, input)).status, 404);
      assert.equal((await fetch(endpoint)).status, 405);
      for (const invalid of [
        { margin: "8" }, { margin: 101 }, { reporting: -1 }, { reporting: 101 },
        { sourceUrl: "javascript:alert(1)" }, { sourceUrl: "https://user:secret@example.org" },
        { observedAt: "2026-02-30T00:00:00Z" }, { observedAt: new Date(Date.now() + 3600000).toISOString() },
        { body: "" }, { body: "x".repeat(2001) }, { expectedVersion: -1 }, { expectedVersion: null },
        { status: "made-up" }, { status: "awaiting" }, { status: "observed" },
        { winner: "D" }, { winner: ["D"] }, { gopSeats: 3 },
        { status: "projected", winner: "R" },
      ]) assert.equal((await put(endpoint, { ...input, ...invalid })).status, 400, JSON.stringify(invalid));
      assert.equal((await fetch(endpoint, { method: "PUT", headers, body: "{" })).status, 400);
      assert.equal((await fetch(endpoint, { method: "PUT", headers, body: JSON.stringify({ ...input, body: "x".repeat(17000) }) })).status, 413);
      assert.equal((await put(endpoint, input, { Authorization: `Bearer ${key}` })).status, 415);
      const saved = await put(endpoint, input);
      assert.equal(saved.status, 200);
      assert.equal((await saved.json()).version, 1);
      assert.equal((await put(endpoint, input)).status, 409, "Stale edits cannot overwrite a newer entry");
      const correction = await put(endpoint, { ...input, status: "unofficial", winner: "D", margin: 7, expectedVersion: 1 });
      assert.equal(correction.status, 200);
      const history = await (await fetch(`${endpoint}/history`)).json();
      assert.deepEqual(history.history.map(entry => entry.version), [2, 1]);
      assert.deepEqual(history.history.map(entry => entry.margin), [7, 8]);
      assert.equal((await put(`${base}/api/election-night/cue-nc`, { ...input, status: "observed", margin: null, reporting: null })).status, 200);
      assert.equal((await put(`${base}/api/election-night/cue-fl`, { ...input, status: "observed" })).status, 400);
      const groupEndpoint = `${base}/api/election-night/house-tx-redraw`;
      assert.equal((await put(groupEndpoint, { ...input, margin: null, gopSeats: 6 })).status, 400);
      assert.equal((await put(groupEndpoint, { ...input, margin: null, gopSeats: 4.5 })).status, 400);
      assert.equal((await put(groupEndpoint, { ...input, margin: null, gopSeats: 4 })).status, 200);
      const reset = await put(endpoint, { ...input, status: "awaiting", margin: null, reporting: null, expectedVersion: 2, body: "Retracting an erroneous entry pending a source correction." });
      assert.equal(reset.status, 200);
      assert.equal((await (await fetch(`${endpoint}/history`)).json()).history.length, 3);
      const concurrent = await Promise.all([
        put(endpoint, { ...input, expectedVersion: 3 }),
        put(endpoint, { ...input, expectedVersion: 3, margin: 9 }),
      ]);
      assert.deepEqual(concurrent.map(response => response.status).sort(), [200, 409]);
      const created = await fetch(`${base}/api/races/ohio/notes`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${key}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          category: "news",
          title: "Restart persistence check",
          body: "Must survive a full local runtime restart.",
          date: "2026-10-17",
          sourceUrl: "https://github.com/snoopynewsnetwork/snn",
        }),
      });
      assert.equal(created.status, 201);
      const note = await created.json();
      await stop();
      await start();
      const restoredNeedle = await (await fetch(`${base}/api/needle/senate-mi`)).json();
      assert.equal(restoredNeedle.version, 1); assert.equal(restoredNeedle.probabilities.D, .75, 'Forecast survives full runtime restart');
      assert.equal(restoredNeedle.assumptions.length, 41, 'Multi-chunk forecast artifacts retain all metadata');
      const race = await (await fetch(`${base}/api/races/ohio`)).json();
      assert.ok(
        race.notes.some((item) => item.id === note.id),
        "Note survives a Worker restart",
      );
      assert.equal(race.election, "Special");
      const restored = await (await fetch(`${base}/api/election-night`)).json();
      assert.ok(!restored.observations.some(entry => entry.target === "senate-mi"), "Automatic races do not revive manual totals while feeds are pending");
      assert.equal((await (await fetch(`${endpoint}/history`)).json()).history[0].version, 4, "Manual history survives the automatic-source overlay");
      assert.equal(restored.observations.find(entry => entry.target === "cue-nc").status, "observed");
      assert.equal((await (await fetch(`${endpoint}/history`)).json()).history.length, 4);
    } finally {
      await stop();
      await rm(directory, { recursive: true, force: true });
    }
  },
);

import assert from "node:assert/strict";
import { setTimeout as delay } from "node:timers/promises";

const base = "https://snoopy-news-network.snoopy-news-network.workers.dev";
// Active Durable Objects defer code updates for up to five minutes by default.
// Allow seven minutes for that delay plus propagation and verification requests.
// https://developers.cloudflare.com/durable-objects/deployments/durable-objects-code-updates/
const attempts = 84;
for (let attempt = 1; attempt <= attempts; attempt++) {
  try {
    const response = await fetch(`${base}/api/health`, { signal: AbortSignal.timeout(10000) });
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), {
      ok: true,
      storage: "durable-object-sqlite",
      races: 35,
    });
    const page = await fetch(base, { signal: AbortSignal.timeout(10000) });
    assert.equal(page.status, 200);
    assert.match(await page.text(), /The 2026 Senate desk/);
    const desk = await fetch(`${base}/api/election-night`, { signal: AbortSignal.timeout(10000) });
    assert.equal(desk.status, 200);
    const live = await desk.json();
    assert.equal(live.intervalMinutes, 1);
    assert.equal(live.coverage?.configured, 65, "Waiting for the deployed live desk schema");
    assert.equal(live.coverage?.total, 65);
    for (const item of [...live.guide.senate, ...live.guide.house]) assert.ok(live.liveResults.some(result => result.target === item.id), item.id);
    assert.ok(live.liveResults.some(result => result.target === "house-tx-35"));
    for (const id of ["cnn-2026-SP-OH", "cnn-2026-SG-MN", "cnn-2026-HG-IN-5"])
      assert.ok(live.sources?.some(source => source.id === id), `Waiting for live fallback source ${id}`);
    assert.ok(live.sources?.some(source => source.id === "civic-ky06-counties"), "Waiting for the KY-06 county collector");
    assert.ok(live.sources?.some(source => source.id === "cnn-ky06-counties"), "Waiting for the KY-06 prediction county source");
    assert.ok(live.liveResults.find(result => result.target === "house-ky-06")?.countyResult, "Waiting for the KY-06 county snapshot schema");
    assert.ok(live.sources?.some(source => source.id === 'cnn-mi-counties'), 'Waiting for the Michigan county collector');
    assert.ok(live.liveResults.find(result => result.target === 'senate-mi')?.countyResult, 'Waiting for the Michigan county snapshot schema');
    for (const asset of ["ky-06.js", "ky-06-model.js", "ky-06-counties.json", "mi-sen.js", "mi-sen-model.js", "mi-sen-counties.json"])
      assert.equal((await fetch(`${base}/${asset}`, { signal: AbortSignal.timeout(10000) })).status, 200);
    assert.match(await (await fetch(`${base}/ky-06-model.js`, { signal: AbortSignal.timeout(10000) })).text(), /export function countyForecast/);
    const client = await fetch(`${base}/election-night.js`, { signal: AbortSignal.timeout(10000) });
    assert.equal(client.status, 200);
    assert.match(await client.text(), /Fetch live results/);
    const checks = await fetch(`${base}/api/monitor/checks`, { signal: AbortSignal.timeout(10000) });
    assert.equal(checks.status, 200);
    const history = await checks.json();
    assert.equal(history.limit, 200);
    assert.ok(history.checks.length <= history.limit);
    assert.deepEqual(history.sources.map(source => `${source.adapter}:${source.id}`).sort(),
      live.sources.map(source => `${source.adapter}:${source.id}`).sort());
    const checkClient = await fetch(`${base}/check-log.js`, { signal: AbortSignal.timeout(10000) });
    assert.equal(checkClient.status, 200);
    assert.match(await checkClient.text(), /\/api\/monitor\/checks/);
    const needles = await fetch(`${base}/api/needle`, { signal: AbortSignal.timeout(10000) });
    assert.equal(needles.status, 200);
    const catalog = await needles.json();
    for (const id of ['house-control', 'senate-control', 'senate-mi', 'house-tx-35'])
      assert.ok(catalog.needles.some(needle => needle.id === id));
    const needle = await fetch(`${base}/api/needle/house-control`, { signal: AbortSignal.timeout(10000) });
    assert.equal(needle.status, 200);
    assert.equal((await needle.json()).schemaVersion, 1);
    const needlePage = await fetch(`${base}/needle`, { signal: AbortSignal.timeout(10000) });
    assert.equal(needlePage.status, 200);
    assert.match(await needlePage.text(), /id="chamber-needles"/);
    assert.ok(live.sources.some(source => source.adapter === 'completion-cnn'), 'Waiting for completion collector deployment');
    const texas = await (await fetch(`${base}/api/needle/senate-tx`, { signal: AbortSignal.timeout(10000) })).json();
    assert.ok(Array.isArray(texas.completion?.candidates), 'Waiting for source-consistent needle candidate tables');
    if (texas.completion.candidates.length)
      assert.equal(texas.completion.candidates.reduce((sum, candidate) => sum + candidate.votes, 0) + (texas.completion.unallocatedVotes ?? 0), texas.completion.supplierVotes);
    const needleClient = await (await fetch(`${base}/needle.js`, { signal: AbortSignal.timeout(10000) })).text();
    assert.match(needleClient, /Separate.*official.*reported.*returns/);
    console.log(`Deployment verified: ${base}`);
    break;
  } catch (error) {
    if (attempt === attempts) throw error;
    console.log(`Waiting for the deployment (${attempt}/${attempts}): ${error.message}`);
    await delay(5000);
  }
}

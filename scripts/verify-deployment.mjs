import assert from "node:assert/strict";
import { setTimeout as delay } from "node:timers/promises";

const base = "https://snoopy-news-network.snoopy-news-network.workers.dev";
for (let attempt = 1; attempt <= 12; attempt++) {
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
    console.log(`Deployment verified: ${base}`);
    break;
  } catch (error) {
    if (attempt === 12) throw error;
    console.log(`Waiting for the deployment (${attempt}/12): ${error.message}`);
    await delay(5000);
  }
}

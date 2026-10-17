import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";

export async function smoke(baseUrl, key) {
  const headers = {
    Authorization: `Bearer ${key}`,
    "Content-Type": "application/json",
  };
  const request = (path, options) => fetch(new URL(path, baseUrl), options);
  const health = await request("/api/health");
  assert.equal(health.status, 200);
  assert.deepEqual(await health.json(), {
    ok: true,
    storage: "durable-object-sqlite",
    races: 35,
  });
  const page = await request("/");
  assert.equal(page.status, 200);
  assert.match(await page.text(), /The 2026 Senate desk/);
  assert.match(
    page.headers.get("Content-Security-Policy"),
    /frame-ancestors 'none'/,
  );
  for (const asset of ["/app.js", "/style.css", "/favicon.svg"])
    assert.equal((await request(asset)).status, 200);
  assert.equal((await request("/api/not-a-route")).status, 404);
  assert.equal((await request("/api/races/not-a-state")).status, 404);
  assert.equal(
    (await request("/api/races/illinois", { method: "PUT" })).status,
    405,
  );
  const { races } = await (await request("/api/races")).json();
  assert.equal(races.length, 35);
  assert.equal(races.filter((race) => race.election === "Special").length, 2);
  assert.equal(
    races.find((race) => race.slug === "illinois").holder,
    "Dick Durbin",
  );
  const detail = await (await request("/api/races/illinois")).json();
  assert.equal(detail.sources.length, 4);
  assert.equal((await request("/api/editor", { method: "POST" })).status, 401);
  assert.equal(
    (await request("/api/editor", { method: "POST", headers })).status,
    200,
  );
  const endpoint = "/api/races/illinois/notes";
  assert.equal((await request(endpoint, { method: "POST" })).status, 401);
  const input = {
    category: "news",
    title: "POC storage verification",
    body: "Temporary deployment test. This note is removed automatically.",
    sourceUrl: "https://github.com/snoopynewsnetwork/snn",
    date: "2026-10-17",
  };
  for (const invalid of [
    { sourceUrl: "javascript:alert(1)" },
    { date: "2026-02-30" },
    { category: "invalid" },
    { title: "" },
  ]) {
    assert.equal(
      (
        await request(endpoint, {
          method: "POST",
          headers,
          body: JSON.stringify({ ...input, ...invalid }),
        })
      ).status,
      400,
    );
  }
  assert.equal(
    (await request(endpoint, { method: "POST", headers, body: "{" })).status,
    400,
  );
  assert.equal(
    (
      await request(endpoint, {
        method: "POST",
        headers,
        body: JSON.stringify({ ...input, body: "x".repeat(17000) }),
      })
    ).status,
    413,
  );
  let note;
  try {
    const created = await request(endpoint, {
      method: "POST",
      headers,
      body: JSON.stringify(input),
    });
    assert.equal(created.status, 201);
    note = await created.json();
    const saved = await (await request("/api/races/illinois")).json();
    assert.ok(
      saved.notes.some(
        (item) => item.id === note.id && item.title === input.title,
      ),
    );
    const refreshed = await (await request("/api/races")).json();
    assert.equal(
      refreshed.races.find((race) => race.slug === "illinois").noteCount,
      detail.notes.length + 1,
    );
    assert.equal(
      (await request(`${endpoint}/${note.id}`, { method: "DELETE" })).status,
      401,
    );
    assert.equal(
      (
        await request(`/api/races/alaska/notes/${note.id}`, {
          method: "DELETE",
          headers,
        })
      ).status,
      404,
    );
  } finally {
    if (note?.id)
      assert.equal(
        (await request(`${endpoint}/${note.id}`, { method: "DELETE", headers }))
          .status,
        200,
      );
  }
  const after = await (await request("/api/races/illinois")).json();
  assert.ok(!after.notes.some((item) => item.id === note.id));
  console.log(
    `Smoke checks passed: ${baseUrl} (35 races, auth, validation, create/read/remove).`,
  );
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const baseUrl = process.argv[2] || "http://localhost:8787";
  const key =
    process.env.ADMIN_TOKEN ||
    (await readFile(new URL("../.dev.vars", import.meta.url), "utf8")).match(
      /^ADMIN_TOKEN="([^"]+)"$/m,
    )?.[1];
  assert.ok(key, "Set ADMIN_TOKEN or configure .dev.vars.");
  await smoke(baseUrl, key);
}

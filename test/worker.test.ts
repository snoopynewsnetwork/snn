import { evictDurableObject, runInDurableObject } from "cloudflare:test";
import { env, exports } from "cloudflare:workers";
import { describe, expect, it } from "vitest";
import seed from "../src/generated/races.json";
import worker from "../src/index";

const auth = { Authorization: `Bearer ${env.ADMIN_TOKEN}` };
const jsonHeaders = { ...auth, "Content-Type": "application/json" };
const validNote = {
  category: "news",
  title: "Vitest note",
  body: "Created by the Vitest worker suite.",
  sourceUrl: "https://github.com/snoopynewsnetwork/snn",
  date: "2026-10-17",
};

function call(path: string, init?: RequestInit) {
  return exports.default.fetch(new Request(`https://snn.test${path}`, init));
}

function postNote(
  slug: string,
  body: unknown,
  headers: HeadersInit = jsonHeaders,
) {
  return call(`/api/races/${slug}/notes`, {
    method: "POST",
    headers,
    body: typeof body === "string" ? body : JSON.stringify(body),
  });
}

describe("seed data", () => {
  it("has 35 races with unique slugs and enough sources", () => {
    expect(seed.races).toHaveLength(35);
    expect(new Set(seed.races.map((race) => race.slug)).size).toBe(35);
    for (const race of seed.races)
      expect(race.sources.length, race.slug).toBeGreaterThanOrEqual(4);
  });
});

describe("routing and headers", () => {
  it("redirects plain HTTP to HTTPS except on localhost", async () => {
    // Call the module directly: the service binding normalises the scheme.
    const remote = await worker.fetch(
      new Request("http://snn.example/api/health"),
      env,
    );
    expect(remote.status).toBe(308);
    expect(remote.headers.get("Location")).toBe(
      "https://snn.example/api/health",
    );
    const local = await worker.fetch(
      new Request("http://localhost/api/health"),
      env,
    );
    expect(local.status).toBe(200);
  });

  it("adds security headers to API and asset responses", async () => {
    for (const path of ["/api/health", "/"]) {
      const response = await call(path);
      expect(response.headers.get("X-Content-Type-Options")).toBe("nosniff");
      expect(response.headers.get("Content-Security-Policy")).toMatch(
        /frame-ancestors 'none'/,
      );
    }
  });

  it("serves static assets", async () => {
    const page = await call("/");
    expect(page.status).toBe(200);
    expect(await page.text()).toMatch(/The 2026 Senate desk/);
    for (const asset of ["/app.js", "/style.css", "/favicon.svg"])
      expect((await call(asset)).status, asset).toBe(200);
  });

  it("reports health from Durable Object storage", async () => {
    const response = await call("/api/health");
    expect(response.headers.get("Cache-Control")).toBe("no-store");
    expect(await response.json()).toEqual({
      ok: true,
      storage: "durable-object-sqlite",
      races: 35,
    });
  });

  it.each([
    ["/api/not-a-route", "GET", 404],
    ["/api", "GET", 404],
    ["/api/races/not-a-state", "GET", 404],
    ["/api/races/Illinois", "GET", 404],
    ["/api/races/illinois", "PUT", 405],
    ["/api/races/illinois/notes", "GET", 405],
    [`/api/races/illinois/notes/${crypto.randomUUID()}`, "POST", 405],
  ])("%s %s returns %i", async (path, method, status) => {
    const response = await call(path, { method });
    expect(response.status).toBe(status);
    expect(await response.json()).toHaveProperty("error");
  });

  it("lists races sorted by state with note counts", async () => {
    const { races } = await (await call("/api/races")).json<{
      races: { state: string; noteCount: number; election: string }[];
    }>();
    expect(races).toHaveLength(35);
    expect(races.map((race) => race.state)).toEqual(
      [...races.map((race) => race.state)].sort(),
    );
    expect(races.every((race) => race.noteCount === 0)).toBe(true);
    expect(races.filter((race) => race.election === "Special")).toHaveLength(2);
  });

  it("returns race detail with sources and notes", async () => {
    const race = await (await call("/api/races/illinois")).json<{
      holder: string;
      sources: unknown[];
      notes: unknown[];
    }>();
    expect(race.holder).toBe("Dick Durbin");
    expect(race.sources).toHaveLength(4);
    expect(race.notes).toEqual([]);
  });
});

describe("editor authorization", () => {
  it("accepts the configured token", async () => {
    const response = await call("/api/editor", { method: "POST", headers: auth });
    expect(response.status).toBe(200);
  });

  it.each([
    ["missing", {}],
    ["wrong", { Authorization: "Bearer nope" }],
    ["unprefixed", { Authorization: env.ADMIN_TOKEN.slice(1) }],
  ])("rejects a %s token", async (_, headers) => {
    const response = await call("/api/editor", { method: "POST", headers });
    expect(response.status).toBe(401);
  });

  it("requires auth before touching notes", async () => {
    expect((await postNote("illinois", validNote, {})).status).toBe(401);
    const id = crypto.randomUUID();
    const response = await call(`/api/races/illinois/notes/${id}`, {
      method: "DELETE",
    });
    expect(response.status).toBe(401);
  });
});

describe("note validation", () => {
  it.each([
    ["javascript URL", { sourceUrl: "javascript:alert(1)" }],
    ["URL with credentials", { sourceUrl: "https://user:pw@example.com" }],
    ["unparseable URL", { sourceUrl: "not a url" }],
    ["impossible date", { date: "2026-02-30" }],
    ["badly formatted date", { date: "10/17/2026" }],
    ["unknown category", { category: "invalid" }],
    ["empty title", { title: "" }],
    ["whitespace body", { body: "   " }],
    ["overlong title", { title: "x".repeat(161) }],
    ["non-string field", { title: 42 }],
  ])("rejects %s", async (_, override) => {
    const response = await postNote("illinois", { ...validNote, ...override });
    expect(response.status).toBe(400);
  });

  it.each([
    ["malformed JSON", "{"],
    ["a JSON array", "[]"],
    ["JSON null", "null"],
  ])("rejects %s", async (_, body) => {
    expect((await postNote("illinois", body)).status).toBe(400);
  });

  it("requires a JSON content type", async () => {
    const response = await postNote("illinois", validNote, {
      ...auth,
      "Content-Type": "text/plain",
    });
    expect(response.status).toBe(415);
  });

  it("rejects bodies over 16 KiB", async () => {
    const response = await postNote("illinois", {
      ...validNote,
      body: "x".repeat(17000),
    });
    expect(response.status).toBe(413);
  });

  it("returns 404 for notes on an unknown race", async () => {
    expect((await postNote("atlantis", validNote)).status).toBe(404);
  });
});

describe("note lifecycle", () => {
  it("creates, lists, counts and soft-deletes a note", async () => {
    const created = await postNote("illinois", {
      ...validNote,
      title: "  Trimmed title  ",
    });
    expect(created.status).toBe(201);
    const note = await created.json<{ id: string; title: string; race: string }>();
    expect(note).toMatchObject({ title: "Trimmed title", race: "illinois" });

    const detail = await (await call("/api/races/illinois")).json<{
      notes: { id: string }[];
    }>();
    expect(detail.notes.map((item) => item.id)).toEqual([note.id]);

    const { races } = await (await call("/api/races")).json<{
      races: { slug: string; noteCount: number }[];
    }>();
    expect(races.find((race) => race.slug === "illinois")?.noteCount).toBe(1);

    const wrongRace = await call(`/api/races/alaska/notes/${note.id}`, {
      method: "DELETE",
      headers: auth,
    });
    expect(wrongRace.status).toBe(404);

    const removed = await call(`/api/races/illinois/notes/${note.id}`, {
      method: "DELETE",
      headers: auth,
    });
    expect(removed.status).toBe(200);
    const again = await call(`/api/races/illinois/notes/${note.id}`, {
      method: "DELETE",
      headers: auth,
    });
    expect(again.status).toBe(404);

    const after = await (await call("/api/races/illinois")).json<{
      notes: unknown[];
    }>();
    expect(after.notes).toEqual([]);
  });

  it("orders notes by date, newest first", async () => {
    for (const date of ["2026-09-01", "2026-10-01", "2026-08-01"])
      await postNote("ohio", { ...validNote, title: date, date });
    const race = await (await call("/api/races/ohio")).json<{
      notes: { date: string }[];
    }>();
    expect(race.notes.map((note) => note.date)).toEqual([
      "2026-10-01",
      "2026-09-01",
      "2026-08-01",
    ]);
  });

  it("keeps notes after the Durable Object is evicted", async () => {
    const note = await (await postNote("ohio", validNote)).json<{ id: string }>();
    const stub = env.NEWSROOM.getByName("senate-2026");
    await evictDurableObject(stub);
    const race = await (await call("/api/races/ohio")).json<{
      notes: { id: string }[];
    }>();
    expect(race.notes.map((item) => item.id)).toContain(note.id);
  });

  it("keeps removed notes in storage with a removedAt timestamp", async () => {
    const note = await (await postNote("ohio", validNote)).json<{ id: string }>();
    await call(`/api/races/ohio/notes/${note.id}`, {
      method: "DELETE",
      headers: auth,
    });
    const stub = env.NEWSROOM.getByName("senate-2026");
    const row = await runInDurableObject(stub, (_, state) =>
      state.storage.sql
        .exec<{ removedAt: string | null }>(
          "SELECT removedAt FROM notes WHERE id = ?",
          note.id,
        )
        .one(),
    );
    expect(row.removedAt).toEqual(expect.any(String));
  });
});

describe("seeding", () => {
  it("records the seed version and reseeds when it changes", async () => {
    const stub = env.NEWSROOM.getByName("senate-2026");
    await stub.listRaces();
    await runInDurableObject(stub, (_, state) => {
      const sql = state.storage.sql;
      expect(
        sql.exec<{ value: string }>(
          "SELECT value FROM metadata WHERE key = 'seed_version'",
        ).one().value,
      ).toBe(seed.version);
      sql.exec("UPDATE metadata SET value = 'stale' WHERE key = 'seed_version'");
      sql.exec("UPDATE races SET data = json_set(data, '$.holder', 'Stale')");
    });
    await evictDurableObject(stub);
    const race = await stub.getRace("illinois");
    expect(race?.holder).toBe("Dick Durbin");
  });
});

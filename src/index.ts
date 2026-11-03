import { DurableObject } from "cloudflare:workers";
import seed from "./generated/races.json";
import { monitorSources, parseKansas, parseKansasResults, parseNorthCarolina, bodyHash, type ParsedMonitor } from "./monitor";

interface Env {
  NEWSROOM: DurableObjectNamespace<Newsroom>;
  ASSETS: Fetcher;
  ADMIN_TOKEN?: string;
}

interface Note {
  id: string;
  race: string;
  category: string;
  title: string;
  body: string;
  sourceUrl: string;
  date: string;
  createdAt: string;
}

type Race = (typeof seed.races)[number];
type RaceSummary = Race & { noteCount: number };
type RaceDetail = Race & { notes: Note[] };

const categories = ["news", "candidates", "polling", "finance", "results"];
const securityHeaders = {
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Content-Security-Policy":
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
};

class HttpError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

function json(data: unknown, status = 200) {
  return Response.json(data, {
    status,
    headers: { "Cache-Control": "no-store" },
  });
}

async function authorize(request: Request, env: Env) {
  if (!env.ADMIN_TOKEN || env.ADMIN_TOKEN.length < 32) {
    throw new HttpError(
      503,
      "Editing is not configured. Set the ADMIN_TOKEN Worker secret.",
    );
  }
  const supplied =
    request.headers.get("Authorization")?.replace(/^Bearer /, "") ?? "";
  const encoder = new TextEncoder();
  const hashes = await Promise.all(
    [supplied, env.ADMIN_TOKEN].map((value) =>
      crypto.subtle.digest("SHA-256", encoder.encode(value)),
    ),
  );
  const a = new Uint8Array(hashes[0]);
  const b = new Uint8Array(hashes[1]);
  let mismatch = 0;
  for (let i = 0; i < a.length; i++) mismatch |= a[i] ^ b[i];
  if (mismatch) throw new HttpError(401, "A valid editor key is required.");
}

async function parseNote(
  request: Request,
): Promise<Omit<Note, "id" | "race" | "createdAt">> {
  if (
    request.headers.get("Content-Type")?.split(";")[0].trim() !==
    "application/json"
  ) {
    throw new HttpError(415, "Use application/json.");
  }
  const reader = request.body?.getReader();
  if (!reader) throw new HttpError(400, "A note is required.");
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 16384) {
        await reader.cancel();
        throw new HttpError(413, "The note is too large.");
      }
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }
  const buffer = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) {
    buffer.set(chunk, offset);
    offset += chunk.length;
  }
  let input: Record<string, unknown>;
  try {
    const parsed: unknown = JSON.parse(new TextDecoder().decode(buffer));
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed))
      throw new Error();
    input = parsed as Record<string, unknown>;
  } catch {
    throw new HttpError(400, "Invalid JSON object.");
  }
  const field = (name: string, max: number) => {
    const value = input[name];
    if (
      typeof value !== "string" ||
      !value.trim() ||
      value.trim().length > max
    ) {
      throw new HttpError(400, `${name} must contain 1–${max} characters.`);
    }
    return value.trim();
  };
  const note = {
    category: field("category", 20),
    title: field("title", 160),
    body: field("body", 6000),
    sourceUrl: field("sourceUrl", 2048),
    date: field("date", 10),
  };
  if (!categories.includes(note.category))
    throw new HttpError(400, "Invalid note category.");
  let source: URL;
  try {
    source = new URL(note.sourceUrl);
  } catch {
    throw new HttpError(400, "A source URL is required.");
  }
  if (
    !["http:", "https:"].includes(source.protocol) ||
    source.username ||
    source.password
  ) {
    throw new HttpError(
      400,
      "Use an HTTP or HTTPS source URL without credentials.",
    );
  }
  const date = new Date(`${note.date}T00:00:00Z`);
  if (
    !/^\d{4}-\d{2}-\d{2}$/.test(note.date) ||
    !Number.isFinite(date.getTime()) ||
    date.toISOString().slice(0, 10) !== note.date
  ) {
    throw new HttpError(400, "Use a valid YYYY-MM-DD date.");
  }
  return note;
}

export class Newsroom extends DurableObject<Env> {
  private monitorRun?: Promise<void>;
  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    const sql = ctx.storage.sql;
    sql.exec(`
      CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS races (slug TEXT PRIMARY KEY, data TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS notes (
        id TEXT PRIMARY KEY, race TEXT NOT NULL, category TEXT NOT NULL,
        title TEXT NOT NULL, body TEXT NOT NULL, sourceUrl TEXT NOT NULL,
        date TEXT NOT NULL, createdAt TEXT NOT NULL, removedAt TEXT
      );
      CREATE INDEX IF NOT EXISTS notes_by_race ON notes(race, removedAt, date DESC, createdAt DESC);
      CREATE TABLE IF NOT EXISTS monitor_sources (id TEXT PRIMARY KEY, data TEXT NOT NULL, body TEXT);
      CREATE TABLE IF NOT EXISTS monitor_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, hash TEXT NOT NULL,
        fetchedAt TEXT NOT NULL, sourceUrl TEXT NOT NULL, headers TEXT NOT NULL, body TEXT NOT NULL,
        UNIQUE(source, hash)
      );
      CREATE TABLE IF NOT EXISTS monitor_races (race TEXT PRIMARY KEY, data TEXT NOT NULL);

    `);
    const version = sql
      .exec<{ value: string }>(
        "SELECT value FROM metadata WHERE key = 'seed_version'",
      )
      .toArray()[0]?.value;
    if (version !== seed.version) {
      ctx.storage.transactionSync(() => {
        for (const race of seed.races) {
          sql.exec(
            "INSERT INTO races (slug, data) VALUES (?, ?) ON CONFLICT(slug) DO UPDATE SET data = excluded.data",
            race.slug,
            JSON.stringify(race),
          );
        }
        sql.exec(
          "INSERT INTO metadata (key, value) VALUES ('seed_version', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
          seed.version,
        );
      });
    }
  }

  getMonitor() {
    const sql = this.ctx.storage.sql;
    const sources = monitorSources.map(source => {
      const row = sql.exec<{ data: string }>("SELECT data FROM monitor_sources WHERE id = ?", source.id).toArray()[0];
      return { ...source, ...(row ? JSON.parse(row.data) : { status: "pending" }) };
    });
    const races = ["kansas", "north-carolina"].map(race => {
      const row = sql.exec<{ data: string }>("SELECT data FROM monitor_races WHERE race = ?", race).toArray()[0];
      return { race, ...(row ? JSON.parse(row.data) : { status: "pending", message: "Waiting for the first automatic source check." }) };
    });
    const snapshots = sql.exec("SELECT id, source, hash, fetchedAt, sourceUrl FROM monitor_snapshots ORDER BY id DESC LIMIT 20").toArray();
    return { intervalMinutes: 5, electionDate: "2026-11-03", parserVersion: "official-senate-v1", sources, races, snapshots };
  }

  getMonitorSnapshot(id: number) {
    return this.ctx.storage.sql.exec("SELECT * FROM monitor_snapshots WHERE id = ?", id).toArray()[0] ?? null;
  }

  runMonitor(): Promise<void> {
    if (!this.monitorRun) {
      this.monitorRun = this.collectMonitor().finally(() => { this.monitorRun = undefined; });
    }
    return this.monitorRun;
  }

  private async collectMonitor() {
    const sql = this.ctx.storage.sql;
    // Persist a short lease so retries/restarts cannot multiply source traffic.
    const last = sql.exec<{ value: string }>("SELECT value FROM metadata WHERE key = 'monitor_started'").toArray()[0];
    if (last && Date.now() - Number(last.value) < 120_000) return;
    sql.exec("INSERT INTO metadata (key, value) VALUES ('monitor_started', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", String(Date.now()));
    const bodies: Record<string, string> = {};
    for (const source of monitorSources) {
      const prior = sql.exec<{ data: string; body: string | null }>("SELECT data, body FROM monitor_sources WHERE id = ?", source.id).toArray()[0];
      const state = prior ? JSON.parse(prior.data) : {};
      if (state.nextAttemptAt && Date.parse(state.nextAttemptAt) > Date.now()) continue;
      const checkedAt = new Date().toISOString();
      try {
        const headers: Record<string, string> = { "User-Agent": "SNN-Official-Results-Monitor/1.0 (+https://github.com/snoopynewsnetwork/snn)", "Cache-Control": "no-cache" };
        if (state.etag) headers["If-None-Match"] = state.etag;
        if (state.lastModified) headers["If-Modified-Since"] = state.lastModified;
        const response = await fetch(source.url, { headers, signal: AbortSignal.timeout(15_000), redirect: "manual" });
        if (response.status !== 200 && response.status !== 304) throw new Error(`Official source returned HTTP ${response.status}.`);
        let body = prior?.body ?? "";
        if (response.status === 200) {
          const reader = response.body!.getReader();
          const chunks: Uint8Array[] = [];
          let size = 0;
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            size += value.byteLength;
            if (size > 2_000_000) { await reader.cancel(); throw new Error("Official response exceeds 2 MB; review required."); }
            chunks.push(value);
          }
          const bytes = new Uint8Array(size);
          let offset = 0;
          for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
          body = new TextDecoder("utf-8", { fatal: true, ignoreBOM: false }).decode(bytes);
        }
        if (!body.trim()) throw new Error("Official source returned an empty response.");
        const hash = await bodyHash(body);
        // Retain original bytes (UTF-8 source text), headers and hash even when a parser rejects the response.
        const receiptHeaders = Object.fromEntries(["content-type", "last-modified", "etag", "date"].map(name => [name, response.headers.get(name)]));
        sql.exec("INSERT OR IGNORE INTO monitor_snapshots (source, hash, fetchedAt, sourceUrl, headers, body) VALUES (?, ?, ?, ?, ?, ?)", source.id, hash, checkedAt, source.url, JSON.stringify(receiptHeaders), body);
        const snapshot = sql.exec<{ id: number }>("SELECT id FROM monitor_snapshots WHERE source = ? AND hash = ?", source.id, hash).toArray()[0];
        const publication = source.race === "kansas" ? parseKansas(body, source.url) : undefined;
        if (source.race === "north-carolina") {
          const data = JSON.parse(body);
          if (!Array.isArray(data) || !data.length) throw new Error("Official JSON array is missing.");
        }
        const next = {
          status: "ok", checkedAt, lastSuccessAt: checkedAt,
          lastChangedAt: state.hash === hash ? state.lastChangedAt : checkedAt,
          hash, snapshotId: snapshot.id, httpStatus: response.status,
          etag: response.headers.get("etag") ?? (response.status === 304 ? state.etag : undefined),
          lastModified: response.headers.get("last-modified") ?? (response.status === 304 ? state.lastModified : undefined),
          consecutiveErrors: 0, publication,
        };
        sql.exec("INSERT INTO monitor_sources (id, data, body) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET data = excluded.data, body = excluded.body", source.id, JSON.stringify(next), body);
        bodies[source.id] = body;
      } catch (error) {
        const consecutiveErrors = (state.consecutiveErrors ?? 0) + 1;
        const nextAttemptAt = new Date(Date.now() + Math.min(60, 5 * 2 ** Math.min(consecutiveErrors - 1, 4)) * 60_000).toISOString();
        const next = { ...state, status: "error", checkedAt, consecutiveErrors, nextAttemptAt, error: error instanceof Error ? error.message : "Source check failed." };
        sql.exec("INSERT INTO monitor_sources (id, data, body) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET data = excluded.data", source.id, JSON.stringify(next), prior?.body ?? null);
      }
    }
    const checkedAt = new Date().toISOString();
    const saveRace = async (race: string, parsed: ParsedMonitor | null, error?: string, verified = true) => {
      const previous = sql.exec<{ data: string }>("SELECT data FROM monitor_races WHERE race = ?", race).toArray()[0];
      const old = previous ? JSON.parse(previous.data) : {};
      const sources = monitorSources.filter(source => source.race === race).map(source => {
        const row = sql.exec<{ data: string }>("SELECT data FROM monitor_sources WHERE id = ?", source.id).toArray()[0];
        return { id: source.id, ...(row ? JSON.parse(row.data) : {}) };
      });
      const hash = parsed ? await bodyHash(JSON.stringify({ status: parsed.status, candidates: parsed.candidates, publications: parsed.publications })) : old.resultHash;
      const next = parsed ? {
        ...parsed, checkedAt, lastSuccessAt: verified ? checkedAt : old.lastSuccessAt, resultHash: hash,
        lastResultChangedAt: old.resultHash === hash ? old.lastResultChangedAt : checkedAt,
        sourceSnapshots: sources.map(source => ({ source: source.id, snapshotId: source.snapshotId })),
      } : { ...old, checkedAt, status: "error", message: error, lastGoodStatus: old.lastGoodStatus ?? old.status };
      sql.exec("INSERT INTO monitor_races (race, data) VALUES (?, ?) ON CONFLICT(race) DO UPDATE SET data = excluded.data", race, JSON.stringify(next));
    };
    try {
      if (!["nc-elections", "nc-counties", "nc-results"].every(id => bodies[id])) throw new Error("Official source check failed or is backing off. Previously verified counts, if present, are retained below.");
      await saveRace("north-carolina", parseNorthCarolina(bodies["nc-elections"], bodies["nc-counties"], bodies["nc-results"]));
    } catch (error) { await saveRace("north-carolina", null, error instanceof Error ? error.message : "Parse failed."); }
    const ks = monitorSources.filter(source => source.race === "kansas");
    const publications = ks.flatMap(source => {
      const row = sql.exec<{ data: string }>("SELECT data FROM monitor_sources WHERE id = ?", source.id).toArray()[0];
      return row ? (JSON.parse(row.data).publication?.publications ?? []) as { title: string; url: string }[] : [];
    });
    try {
      if (!bodies["ks-live"]) throw new Error("Kansas official count page unavailable or backing off. Previously verified counts, if present, are retained below.");
      await saveRace("kansas", { ...parseKansasResults(bodies["ks-live"]), publications: [...new Map(publications.map(item => [item.url, item])).values()] });
    } catch (error) { await saveRace("kansas", null, error instanceof Error ? error.message : "Kansas parse failed."); }
  }

  listRaces(): RaceSummary[] {
    return this.ctx.storage.sql
      .exec<{ data: string; noteCount: number }>(
        `
      SELECT races.data, COUNT(notes.id) AS noteCount FROM races
      LEFT JOIN notes ON notes.race = races.slug AND notes.removedAt IS NULL
      GROUP BY races.slug ORDER BY json_extract(races.data, '$.state')
    `,
      )
      .toArray()
      .map((row) => ({
        ...(JSON.parse(row.data) as Race),
        noteCount: row.noteCount,
      }));
  }

  getRace(slug: string): RaceDetail | null {
    const row = this.ctx.storage.sql
      .exec<{ data: string }>("SELECT data FROM races WHERE slug = ?", slug)
      .toArray()[0];
    if (!row) return null;
    const notes = this.ctx.storage.sql
      .exec<Note & Record<string, SqlStorageValue>>(
        `
      SELECT id, race, category, title, body, sourceUrl, date, createdAt
      FROM notes WHERE race = ? AND removedAt IS NULL ORDER BY date DESC, createdAt DESC
    `,
        slug,
      )
      .toArray();
    return { ...(JSON.parse(row.data) as Race), notes };
  }

  addNote(slug: string, input: Omit<Note, "id" | "race" | "createdAt">) {
    const note: Note = {
      ...input,
      id: crypto.randomUUID(),
      race: slug,
      createdAt: new Date().toISOString(),
    };
    this.ctx.storage.sql.exec(
      `INSERT INTO notes (id, race, category, title, body, sourceUrl, date, createdAt)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      note.id,
      slug,
      note.category,
      note.title,
      note.body,
      note.sourceUrl,
      note.date,
      note.createdAt,
    );
    return note;
  }

  removeNote(slug: string, id: string) {
    return (
      this.ctx.storage.sql
        .exec(
          "UPDATE notes SET removedAt = ? WHERE id = ? AND race = ? AND removedAt IS NULL RETURNING id",
          new Date().toISOString(),
          id,
          slug,
        )
        .toArray().length > 0
    );
  }
}

async function handleRequest(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  if (url.protocol === "http:" && !["localhost", "127.0.0.1", "[::1]"].includes(url.hostname)) {
    url.protocol = "https:";
    return Response.redirect(url.toString(), 308);
  }
  const path = url.pathname;
  if (path !== "/api" && !path.startsWith("/api/"))
    return env.ASSETS.fetch(request);
  const newsroom = env.NEWSROOM.getByName("senate-2026");
  if (path === "/api/monitor" && request.method === "GET") return json(await newsroom.getMonitor());
  if (path === "/api/monitor/refresh" && request.method === "POST") {
    await authorize(request, env);
    await newsroom.runMonitor();
    return json(await newsroom.getMonitor());
  }
  const snapshotMatch = path.match(/^\/api\/monitor\/snapshots\/(\d+)$/);
  if (snapshotMatch && request.method === "GET") {
    const snapshot = await newsroom.getMonitorSnapshot(Number(snapshotMatch[1]));
    if (!snapshot) throw new HttpError(404, "Snapshot not found.");
    return json(snapshot);
  }
  if (path === "/api/health" && request.method === "GET") {
    const races = await newsroom.listRaces();
    return json({
      ok: true,
      storage: "durable-object-sqlite",
      races: races.length,
    });
  }
  if (path === "/api/editor" && request.method === "POST") {
    await authorize(request, env);
    return json({ ok: true });
  }
  if (path === "/api/races" && request.method === "GET")
    return json({ races: await newsroom.listRaces() });
  const match = path.match(
    /^\/api\/races\/([a-z-]+)(?:\/notes(?:\/([a-f0-9-]{36}))?)?$/,
  );
  if (!match) throw new HttpError(404, "API route not found.");
  const [, slug, noteId] = match;
  const isNotes = path.includes("/notes");
  if (
    (!isNotes && request.method !== "GET") ||
    (isNotes && request.method !== (noteId ? "DELETE" : "POST"))
  ) {
    throw new HttpError(405, "Method not allowed.");
  }
  if (isNotes) await authorize(request, env);
  const race = await newsroom.getRace(slug);
  if (!race) throw new HttpError(404, "Race not found.");
  if (!isNotes) return json(race);
  if (!noteId)
    return json(await newsroom.addNote(slug, await parseNote(request)), 201);
  if (!(await newsroom.removeNote(slug, noteId)))
    throw new HttpError(404, "Note not found.");
  return json({ ok: true });
}

export default {
  async scheduled(_controller: ScheduledController, env: Env) {
    await env.NEWSROOM.getByName("senate-2026").runMonitor();
  },

  async fetch(request: Request, env: Env) {
    let response: Response;
    try {
      response = await handleRequest(request, env);
    } catch (error) {
      if (error instanceof HttpError)
        response = json({ error: error.message }, error.status);
      else {
        console.error("Request failed", error);
        response = json(
          { error: "Something went wrong. Please try again." },
          500,
        );
      }
    }
    const secured = new Response(response.body, response);
    for (const [name, value] of Object.entries(securityHeaders))
      secured.headers.set(name, value);
    return secured;
  },
} satisfies ExportedHandler<Env>;

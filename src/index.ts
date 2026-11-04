import { DurableObject } from "cloudflare:workers";
import seed from "./generated/races.json";
import { withGroupResults, withOfficialResults, type Observation, type LiveResult } from "./live-results";
import guide from "../public/election-guide.json";
import { electionAdapters } from "./election-adapters";
import { ElectionMonitor, type ElectionBatch } from "./election-monitor";
import { SourceCheckLog, CHECK_LOG_LIMIT, type CheckTrigger } from "./check-log";
export { ElectionMonitor };

interface Env {
  NEWSROOM: DurableObjectNamespace<Newsroom>;
  LIVE_MONITORS: DurableObjectNamespace<ElectionMonitor>;
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

async function readJson(request: Request): Promise<Record<string, unknown>> {
  if (
    request.headers.get("Content-Type")?.split(";")[0].trim() !==
    "application/json"
  ) {
    throw new HttpError(415, "Use application/json.");
  }
  const reader = request.body?.getReader();
  if (!reader) throw new HttpError(400, "A JSON body is required.");
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 16384) {
        await reader.cancel();
        throw new HttpError(413, "The request is too large.");
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
  return input;
}

async function parseNote(request: Request): Promise<Omit<Note, "id" | "race" | "createdAt">> {
  const input = await readJson(request);
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

const targets = [...guide.senate, ...guide.house, ...guide.cues];
async function parseObservation(request: Request, target: (typeof targets)[number]) {
  const input = await readJson(request);
  const statuses = target.chamber === "cue"
    ? ["awaiting", "observed", "mixed", "not-observed"]
    : ["awaiting", "partial", "projected", "unofficial", "certified"];
  if (typeof input.status !== "string" || !statuses.includes(input.status))
    throw new HttpError(400, "Choose a valid reporting status.");
  const number = (key: string, min: number, max: number, integer = false) => {
    const value = input[key];
    if (value === null || value === undefined) return null;
    if (typeof value !== "number" || !Number.isFinite(value) || value < min || value > max || (integer && !Number.isInteger(value)))
      throw new HttpError(400, `Invalid ${key}.`);
    return value;
  };
  const margin = number("margin", -100, 100);
  const reporting = number("reporting", 0, 100);
  const gopSeats = number("gopSeats", 0, target.id === "house-tx-redraw" ? 5 : target.id === "house-pa-07-10" ? 2 : 4, true);
  const group = "group" in target && target.group;
  const cue = target.chamber === "cue";
  const winner = input.winner ?? null;
  if (winner !== null && (typeof winner !== "string" || !["D", "R", "I", "other"].includes(winner)))
    throw new HttpError(400, "Invalid winner.");
  if (winner !== null && !["projected", "unofficial", "certified"].includes(input.status))
    throw new HttpError(400, "A winner requires a projected, unofficial, or certified status.");
  if (input.status !== "awaiting" && !cue && (group ? gopSeats === null : margin === null && winner === null))
    throw new HttpError(400, "Enter a margin, a winner, or a group seat count.");
  if ((cue && (margin !== null || reporting !== null || winner !== null || gopSeats !== null)) ||
      (!group && gopSeats !== null) || (group && (margin !== null || winner !== null)))
    throw new HttpError(400, "These result fields do not apply to this watch item.");
  if (input.status === "awaiting" && (margin !== null || reporting !== null || winner !== null || gopSeats !== null))
    throw new HttpError(400, "Clear result fields when resetting to awaiting.");
  if (target.chamber === "senate" && winner !== null && margin !== null &&
      ((winner === "R" && margin > 0) || (["D", "I"].includes(String(winner)) && margin < 0)))
    throw new HttpError(400, "Winner and margin disagree.");
  if (typeof input.sourceUrl !== "string" || input.sourceUrl.length > 2048)
    throw new HttpError(400, "A source URL is required.");
  let source: URL;
  try { source = new URL(input.sourceUrl); } catch { throw new HttpError(400, "A source URL is required."); }
  if (!["https:", "http:"].includes(source.protocol) || source.username || source.password)
    throw new HttpError(400, "Use an HTTP or HTTPS source URL without credentials.");
  if (typeof input.body !== "string" || !input.body.trim() || input.body.length > 2000)
    throw new HttpError(400, "Add a reporting note of 1–2000 characters.");
  if (typeof input.observedAt !== "string" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/.test(input.observedAt) || !Number.isFinite(Date.parse(input.observedAt)) || new Date(input.observedAt).toISOString() !== input.observedAt.replace(/Z$/, input.observedAt.includes(".") ? "Z" : ".000Z"))
    throw new HttpError(400, "Use a valid UTC observation timestamp.");
  if (Date.parse(input.observedAt) > Date.now() + 60000)
    throw new HttpError(400, "The observation time cannot be in the future.");
  if (!Number.isInteger(input.expectedVersion) || Number(input.expectedVersion) < 0)
    throw new HttpError(400, "A valid expectedVersion is required.");
  return {
    target: target.id, status: input.status, margin, reporting, winner: winner as string | null,
    gopSeats, cueState: cue ? input.status : null, sourceUrl: source.href,
    observedAt: input.observedAt, body: input.body.trim(), expectedVersion: Number(input.expectedVersion),
  };
}

export class Newsroom extends DurableObject<Env> {
  private monitorRun?: Promise<void>;
  private checkLog: SourceCheckLog;
  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    this.checkLog = new SourceCheckLog(ctx.storage);
    const sql = ctx.storage.sql;
    sql.exec(`
      CREATE TABLE IF NOT EXISTS election_observations (
        target TEXT NOT NULL, version INTEGER NOT NULL, data TEXT NOT NULL,
        PRIMARY KEY (target, version)
      );
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

  async getMonitor() {
    const batches: ElectionBatch[] = electionAdapters.map(adapter => {
      const row = this.ctx.storage.sql.exec<{ value: string }>("SELECT value FROM metadata WHERE key = ?", `live_batch_${adapter.id}`).toArray()[0];
      if (row) return JSON.parse(row.value) as import("./election-monitor").ElectionBatch;
      return { adapter: adapter.id, version: adapter.version,
        sources: adapter.sources.map(source => ({ ...source, status: "pending" as const })),
        results: adapter.targets.map(target => ({
          target: target.id, race: target.id, name: target.name, state: target.state, chamber: target.chamber,
          status: "pending" as const, message: "Awaiting the first automatic source fetch.",
          sourceUrl: adapter.sources.find(source => source.id === target.sourceId)?.authorityUrl ?? adapter.sources[0]?.authorityUrl ?? "",
          sourceKind: (adapter.sources.find(source => source.id === target.sourceId) ?? adapter.sources[0])?.official === false ? "supplier" as const : "official" as const,
        })) };
    });
    const allResults = batches.flatMap(batch => batch.results);
    const countyResult = allResults.find(result => result.target === "house-ky-06-counties");
    const races: LiveResult[] = allResults.filter(result => result.target !== "house-ky-06-counties").map(result => ({ ...result,
      race: guide.senate.find(item => item.id === result.target)?.slug ?? result.race,
      ...(result.target === "house-ky-06" ? { countyResult } : {}) }));
    const sources = batches.flatMap(batch => batch.sources.map(source => ({ ...source, adapter: batch.adapter,
      targets: electionAdapters.find(adapter => adapter.id === batch.adapter)!.targets.map(target => target.id),
      snapshotUrl: source.snapshotId ? `/api/live-monitor/${encodeURIComponent(batch.adapter)}/snapshots/${source.snapshotId}` : undefined,
    })));
    const started = this.ctx.storage.sql.exec<{ value: string }>("SELECT value FROM metadata WHERE key = 'live_monitor_started'").toArray()[0];
    return { intervalMinutes: 1, electionDate: "2026-11-03", parserVersion: "cheat-sheet-live-v2", sources, races,
      lastCheckedAt: started ? new Date(Number(started.value)).toISOString() : null };
  }

  async getCheckLog() {
    const latest = this.checkLog.latestBySource();
    const monitor = await this.getMonitor();
    return { limit: CHECK_LOG_LIMIT, checks: this.checkLog.latest(),
      sources: monitor.sources.map(source => ({ ...source,
        lastCheck: latest[`${source.adapter}:${source.id}`] ?? null })),
      intervalMinutes: monitor.intervalMinutes, fetchedAt: new Date().toISOString() };
  }

  getMonitorSnapshot(id: number) {
    // Old evidence links remain readable after the state collector migration.
    return this.ctx.storage.sql.exec("SELECT * FROM monitor_snapshots WHERE id = ?", id).toArray()[0] ?? null;
  }

  runMonitor(force = false, trigger: CheckTrigger = "scheduled"): Promise<void> {
    if (this.monitorRun) return this.monitorRun;
    const last = this.ctx.storage.sql.exec<{ value: string }>("SELECT value FROM metadata WHERE key = 'live_monitor_started'").toArray()[0];
    if (last && Date.now() - Number(last.value) < 30_000) return Promise.resolve();
    this.ctx.storage.sql.exec("INSERT INTO metadata (key, value) VALUES ('live_monitor_started', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", String(Date.now()));
    if (!this.monitorRun) this.monitorRun = Promise.allSettled(electionAdapters.map(async adapter => {
      const { checks = [], ...batch } = await this.env.LIVE_MONITORS.getByName(adapter.id).refresh(adapter.id, force, trigger);
      for (const check of checks) this.checkLog.record(check);
      this.ctx.storage.sql.exec("INSERT INTO metadata (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", `live_batch_${adapter.id}`, JSON.stringify(batch));
    })).then(results => {
      results.forEach((result, index) => {
        if (result.status !== "rejected") return;
        const id = electionAdapters[index].id;
        console.error(`Monitor failed: ${id}`, result.reason);
        const row = this.ctx.storage.sql.exec<{ value: string }>("SELECT value FROM metadata WHERE key = ?", `live_batch_${id}`).toArray()[0];
        if (row) {
          const batch = JSON.parse(row.value) as import("./election-monitor").ElectionBatch;
          batch.results = batch.results.map(result => ({ ...result, status: "error", message: "State collector is temporarily unavailable; retaining last verified results." }));
          this.ctx.storage.sql.exec("UPDATE metadata SET value = ? WHERE key = ?", JSON.stringify(batch), `live_batch_${id}`);
        }
      });
    }).finally(() => { this.monitorRun = undefined; });
    return this.monitorRun;
  }

  electionObservations(): Observation[] {
    return this.ctx.storage.sql.exec<{ data: string }>(`
      SELECT data FROM election_observations e WHERE version =
      (SELECT MAX(version) FROM election_observations WHERE target = e.target)
      ORDER BY target
    `).toArray().map(row => JSON.parse(row.data) as Observation);
  }

  async getElectionNight() {
    const monitor = await this.getMonitor();
    const liveResults = withGroupResults(monitor.races);
    const guideIds = new Set([...guide.senate, ...guide.house].map(item => item.id));
    const guideResults = liveResults.filter(result => result.target && guideIds.has(result.target));
    return { guide, observations: withOfficialResults(this.electionObservations(), guideResults), liveResults,
      sources: monitor.sources, coverage: { total: guideIds.size, configured: guideResults.length,
        reporting: guideResults.filter(result => result.status === "reporting").length,
        setup: guideResults.filter(result => result.status === "setup").length,
        unavailable: guideResults.filter(result => ["unavailable", "error", "review"].includes(result.status)).length },
      intervalMinutes: monitor.intervalMinutes, lastCheckedAt: monitor.lastCheckedAt, fetchedAt: new Date().toISOString() };
  }

  electionHistory(target: string): Observation[] {
    return this.ctx.storage.sql.exec<{ data: string }>(
      "SELECT data FROM election_observations WHERE target = ? ORDER BY version DESC LIMIT 20", target,
    ).toArray().map(row => JSON.parse(row.data) as Observation);
  }

  saveObservation(input: Awaited<ReturnType<typeof parseObservation>>) {
    return this.ctx.storage.transactionSync(() => {
      const version = this.ctx.storage.sql.exec<{ version: number }>(
        "SELECT MAX(version) AS version FROM election_observations WHERE target = ?", input.target,
      ).toArray()[0]?.version ?? 0;
      if (version !== input.expectedVersion) return { conflict: true as const };
      const { expectedVersion, ...fields } = input;
      const observation: Observation = { ...fields, version: version + 1, updatedAt: new Date().toISOString() };
      this.ctx.storage.sql.exec("INSERT INTO election_observations (target, version, data) VALUES (?, ?, ?)",
        input.target, observation.version, JSON.stringify(observation));
      return { observation };
    });
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
  if (path === "/api/monitor/checks") {
    if (request.method !== "GET") throw new HttpError(405, "Method not allowed.");
    return json(await newsroom.getCheckLog());
  }
  if (path === "/api/monitor/refresh" && request.method === "POST") {
    await authorize(request, env);
    await newsroom.runMonitor(false, "editor-refresh");
    return json(await newsroom.getMonitor());
  }
  const liveSnapshot = path.match(/^\/api\/live-monitor\/([a-z0-9-]+)\/snapshots\/(\d+)$/);
  if (liveSnapshot && request.method === "GET") {
    if (!electionAdapters.some(adapter => adapter.id === liveSnapshot[1])) throw new HttpError(404, "Monitor not found.");
    const snapshot = await env.LIVE_MONITORS.getByName(liveSnapshot[1]).getSnapshot(Number(liveSnapshot[2]));
    if (!snapshot) throw new HttpError(404, "Snapshot expired or not found.");
    return json(snapshot);
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
  if (path === "/api/election-night") {
    if (request.method !== "GET") throw new HttpError(405, "Method not allowed.");
    return json(await newsroom.getElectionNight());
  }
  if (path === "/api/election-night/refresh") {
    if (request.method !== "POST") throw new HttpError(405, "Method not allowed.");
    await newsroom.runMonitor(true, "public-refresh");
    return json(await newsroom.getElectionNight());
  }
  const watchMatch = path.match(/^\/api\/election-night\/([a-z0-9-]+)(\/history)?$/);
  if (watchMatch) {
    const target = targets.find(item => item.id === watchMatch[1]);
    if (!target) throw new HttpError(404, "Watch item not found.");
    if (watchMatch[2]) {
      if (request.method !== "GET") throw new HttpError(405, "Method not allowed.");
      return json({ history: await newsroom.electionHistory(target.id) });
    }
    if (request.method !== "PUT") throw new HttpError(405, "Method not allowed.");
    await authorize(request, env);
    const result = await newsroom.saveObservation(await parseObservation(request, target));
    if ("conflict" in result) throw new HttpError(409, "This item changed. Reopen it to review the latest update before saving.");
    return json(result.observation);
  }
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

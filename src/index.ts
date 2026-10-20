import { DurableObject } from "cloudflare:workers";
import seed from "./generated/races.json";
import { getMarketOdds, hasMarkets } from "./markets";

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
  const markets = path.match(/^\/api\/races\/([a-z-]+)\/markets$/);
  if (markets) {
    if (request.method !== "GET") throw new HttpError(405, "Method not allowed.");
    let odds;
    try {
      odds = await getMarketOdds(markets[1]);
    } catch (error) {
      console.error("Market prices failed", error);
      throw new HttpError(502, "Market prices are unavailable right now.");
    }
    if (!odds) throw new HttpError(404, "No market prices for this race.");
    return json(odds);
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
  if (!isNotes) return json({ ...race, hasMarkets: hasMarkets(slug) });
  if (!noteId)
    return json(await newsroom.addNote(slug, await parseNote(request)), 201);
  if (!(await newsroom.removeNote(slug, noteId)))
    throw new HttpError(404, "Note not found.");
  return json({ ok: true });
}

export default {
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

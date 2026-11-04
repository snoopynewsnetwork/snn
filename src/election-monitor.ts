import { DurableObject } from "cloudflare:workers";
import { electionAdapter } from "./election-adapters";
import type { ElectionAdapter, ElectionResult, ElectionSource, ElectionTarget } from "./adapters/types";
import { bodyHash } from "./monitor";
import { hasValidCounts, type LiveResult } from "./live-results";
import { readSourceBody, resolveSourceUrl, retryAfterTime, sourceLayers } from "./election-fetch";
import type { SourceCheck, CheckTrigger } from "./check-log";
import { parseLedgerFeed, type LedgerUpdate } from './chamber-ledger.ts';

interface SourceState {
  status: "pending" | "ok" | "error";
  checkedAt?: string;
  lastSuccessAt?: string;
  lastChangedAt?: string;
  nextAttemptAt?: string;
  retryAfterAt?: string;
  consecutiveErrors?: number;
  url?: string;
  hash?: string;
  snapshotId?: number;
  etag?: string;
  lastModified?: string;
  httpStatus?: number;
  error?: string;
}

export interface ElectionBatch {
  adapter: string;
  version: string;
  results: LiveResult[];
  sources: (ElectionSource & SourceState)[];
  // Only fresh runs return receipts; the coordinator persists these centrally.
  checks?: SourceCheck[];
  ledgerUpdates?: LedgerUpdate[];
}

// One object per adapter isolates state failures, conditional caches, and source
// request budgets. Cloudflare Cron invokes these objects once each minute.
export class ElectionMonitor extends DurableObject<Record<string, never>> {
  private running?: Promise<ElectionBatch>;

  constructor(ctx: DurableObjectState, env: Record<string, never>) {
    super(ctx, env);
    ctx.storage.sql.exec(`
      CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS sources (id TEXT PRIMARY KEY, data TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS results (id TEXT PRIMARY KEY, data TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS completion_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT NOT NULL, hash TEXT NOT NULL, data TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, hash TEXT NOT NULL,
        url TEXT NOT NULL, encoding TEXT NOT NULL, fetchedAt TEXT NOT NULL,
        headers TEXT NOT NULL, size INTEGER NOT NULL, UNIQUE(source, hash, url)
      );
      CREATE TABLE IF NOT EXISTS snapshot_chunks (
        snapshot INTEGER NOT NULL, position INTEGER NOT NULL, body TEXT NOT NULL,
        PRIMARY KEY(snapshot, position)
      );
    `);
  }

  private sourceState(id: string): SourceState {
    const row = this.ctx.storage.sql.exec<{ data: string }>("SELECT data FROM sources WHERE id = ?", id).toArray()[0];
    return row ? JSON.parse(row.data) : { status: "pending" };
  }

  private sourceBody(snapshot?: number): string {
    if (!snapshot) return "";
    return this.ctx.storage.sql.exec<{ body: string }>("SELECT body FROM snapshot_chunks WHERE snapshot = ? ORDER BY position", snapshot).toArray().map(row => row.body).join("");
  }

  private targetResult(adapter: ElectionAdapter, target: ElectionTarget): LiveResult {
    const row = this.ctx.storage.sql.exec<{ data: string }>("SELECT data FROM results WHERE id = ?", target.id).toArray()[0];
    const data = row ? JSON.parse(row.data) : { status: "pending", message: "Awaiting the first automatic source fetch." };
    const source = adapter.sources.find(source => source.id === (data.sourceId ?? target.sourceId)) ?? adapter.sources[0];
    return { ...data, target: target.id, race: target.id, name: target.name, state: target.state, chamber: target.chamber,
      sourceUrl: data.sourceUrl ?? source?.url ?? "", sourceName: source?.name,
      sourceKind: source?.official === false ? "supplier" : "official", authorityUrl: source?.authorityUrl };
  }

  getResults(id: string): ElectionBatch {
    const adapter = electionAdapter(id);
    return { adapter: id, version: adapter.version, results: adapter.targets.map(target => this.targetResult(adapter, target)),
      sources: adapter.sources.map(source => ({ ...source, ...this.sourceState(source.id) })),
      ...(id === 'completion-cnn' ? { ledgerUpdates: (['house', 'senate'] as const).flatMap(chamber => {
        const state = this.sourceState(chamber === 'house' ? 'completion-HG' : 'completion-SG');
        if (!state.snapshotId) return [];
        const updates = parseLedgerFeed(chamber, this.sourceBody(state.snapshotId), state.checkedAt ?? new Date().toISOString(),
          `/api/live-monitor/completion-cnn/snapshots/${state.snapshotId}`);
        return state.status === 'error' ? updates.map(update => ({ ...update, reason: `Retained source evidence; latest check failed: ${state.error}` })) : updates;
      }) } : {}) };
  }

  getSnapshot(id: number) {
    const snapshot = this.ctx.storage.sql.exec("SELECT * FROM snapshots WHERE id = ?", id).toArray()[0];
    return snapshot ? { ...snapshot, body: this.sourceBody(id) } : null;
  }

  getCompletionHistory(target: string, after = 0) {
    const rows = this.ctx.storage.sql.exec<{ id: number; data: string }>(
      'SELECT id, data FROM completion_history WHERE target = ? AND id > ? ORDER BY id LIMIT 200', target, after).toArray();
    return { observations: rows.map(row => ({ id: row.id, ...JSON.parse(row.data) })), nextCursor: rows.at(-1)?.id ?? after };
  }

  refresh(id: string, force = false, trigger: CheckTrigger = "scheduled"): Promise<ElectionBatch> {
    if (!this.running) this.running = this.collect(electionAdapter(id), force, trigger).finally(() => { this.running = undefined; });
    return this.running;
  }

  private saveSource(id: string, state: SourceState) {
    this.ctx.storage.sql.exec("INSERT INTO sources (id, data) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET data = excluded.data", id, JSON.stringify(state));
  }

  private async fetchSource(adapter: ElectionAdapter, source: ElectionSource, bodies: Record<string, string>, force: boolean, trigger: CheckTrigger, checks: SourceCheck[]) {
    const old = this.sourceState(source.id);
    if ((old.retryAfterAt && Date.parse(old.retryAfterAt) > Date.now()) ||
        (!force && old.nextAttemptAt && Date.parse(old.nextAttemptAt) > Date.now())) return;
    const checkedAt = new Date().toISOString();
    const check: SourceCheck = { adapter: adapter.id, official: source.official,
      sourceId: source.id, sourceName: source.name, sourceUrl: source.url, trigger,
      checkedAt, durationMs: 0, success: false, change: "unknown", httpStatus: null,
      snapshotId: null, snapshotUrl: null, responseHash: null, error: null };
    checks.push(check);
    let retryAfter: number | undefined;
    try {
      const url = resolveSourceUrl(source, bodies);
      check.sourceUrl = url;
      const headers = new Headers({ "User-Agent": "SNN-Live-Results/2.0 (+https://github.com/snoopynewsnetwork/snn)", "Cache-Control": "no-cache", ...source.headers });
      if (old.url === url) {
        if (old.etag) headers.set("If-None-Match", old.etag);
        if (old.lastModified) headers.set("If-Modified-Since", old.lastModified);
      }
      const response = await fetch(url, { method: source.method ?? "GET", body: source.body, headers, redirect: "manual", signal: AbortSignal.timeout(15_000) });
      check.httpStatus = response.status;
      retryAfter = retryAfterTime(response.headers.get("retry-after"));
      if (response.status !== 200 && response.status !== 304) throw new Error(`Source returned HTTP ${response.status}.`);
      const body = response.status === 304 && old.url === url ? this.sourceBody(old.snapshotId) : response.status === 200 ? await readSourceBody(response, source) : "";
      if (!body) throw new Error("Source returned 304 without a matching cached response.");
      const hash = await bodyHash(body);
      check.responseHash = hash;
      check.change = old.hash ? (old.hash === hash && old.url === url ? "unchanged" : "changed") : "initial";
      const receiptHeaders = Object.fromEntries(["content-type", "last-modified", "etag", "date"].map(name => [name, response.headers.get(name)]));
      const sql = this.ctx.storage.sql;
      let snapshot = sql.exec<{ id: number }>("SELECT id FROM snapshots WHERE source = ? AND hash = ? AND url = ?", source.id, hash, url).toArray()[0];
      if (!snapshot) {
        this.ctx.storage.transactionSync(() => {
          const row = sql.exec<{ id: number }>("INSERT INTO snapshots (source, hash, url, encoding, fetchedAt, headers, size) VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id",
            source.id, hash, url, source.encoding ?? "utf8", checkedAt, JSON.stringify(receiptHeaders), new TextEncoder().encode(body).byteLength).toArray()[0];
          snapshot = row;
          let position = 0;
          for (let offset = 0; offset < body.length;) {
            let end = Math.min(body.length, offset + 131072);
            // SQLite encodes each string separately. Keep surrogate pairs in the
            // same chunk so UTF-8 conversion cannot replace half a code point.
            if (end < body.length && /[\uD800-\uDBFF]/.test(body[end - 1])) end--;
            sql.exec("INSERT INTO snapshot_chunks (snapshot, position, body) VALUES (?, ?, ?)", row.id, position++, body.slice(offset, end));
            offset = end;
          }
        });
      }
      this.saveSource(source.id, { status: "ok", url, checkedAt, lastSuccessAt: checkedAt,
        lastChangedAt: old.hash === hash && old.url === url ? old.lastChangedAt : checkedAt,
        hash, snapshotId: snapshot!.id, httpStatus: response.status, consecutiveErrors: 0,
        etag: response.headers.get("etag") ?? (response.status === 304 ? old.etag : undefined),
        lastModified: response.headers.get("last-modified") ?? (response.status === 304 ? old.lastModified : undefined) });
      bodies[source.id] = body;
      check.snapshotId = snapshot!.id;
      check.snapshotUrl = `/api/live-monitor/${encodeURIComponent(adapter.id)}/snapshots/${snapshot!.id}`;
      check.success = true;
    } catch (error) {
      check.error = error instanceof Error ? error.message : "Source fetch failed.";
      const consecutiveErrors = (old.consecutiveErrors ?? 0) + 1;
      this.saveSource(source.id, { ...old, status: "error", checkedAt, consecutiveErrors,
        nextAttemptAt: new Date(Math.max(retryAfter ?? 0, Date.now() + Math.min(15, 2 ** Math.min(consecutiveErrors - 1, 4)) * 60_000)).toISOString(),
        retryAfterAt: retryAfter ? new Date(retryAfter).toISOString() : undefined,
        error: check.error });
    } finally {
      check.durationMs = Math.max(0, Date.now() - Date.parse(checkedAt));
    }
  }

  private async collect(adapter: ElectionAdapter, force: boolean, trigger: CheckTrigger): Promise<ElectionBatch> {
    const sql = this.ctx.storage.sql;
    const started = sql.exec<{ value: string }>("SELECT value FROM metadata WHERE key = 'started'").toArray()[0];
    if (started && Date.now() - Number(started.value) < 30_000) return this.getResults(adapter.id);
    sql.exec("INSERT INTO metadata (key, value) VALUES ('started', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", String(Date.now()));
    const bodies: Record<string, string> = {};
    const checks: SourceCheck[] = [];
    const validationFailed = (sourceId: string | undefined, message: string) => {
      // A result may rely on a version pointer as well as the result response.
      const source = adapter.sources.find(source => source.id === sourceId);
      const check = checks.find(check => check.sourceId === sourceId);
      if (check?.success) { check.success = false; check.error = message; }
      if (source?.dependsOn) validationFailed(source.dependsOn, message);
    };
    // State adapters run independently in parallel. Serialize each publisher's
    // requests to avoid bursts against election servers and version pointers.
    for (const layer of sourceLayers(adapter.sources)) for (const source of layer)
      await this.fetchSource(adapter, source, bodies, force, trigger, checks);
    let parsed: Record<string, ElectionResult> = {};
    let parserError: string | undefined;
    try { parsed = await adapter.parse(bodies); }
    catch (error) { parserError = error instanceof Error ? error.message : "Source parser failed."; }
    if (parserError) for (const source of adapter.sources) validationFailed(source.id, `Adapter validation: ${parserError}`);
    const checkedAt = new Date().toISOString();
    const receipts = adapter.sources.filter(source => bodies[source.id] !== undefined).map(source => ({ source: source.id, snapshotId: this.sourceState(source.id).snapshotId,
      url: `/api/live-monitor/${encodeURIComponent(adapter.id)}/snapshots/${this.sourceState(source.id).snapshotId}` }));
    for (const target of adapter.targets) {
      const old = this.targetResult(adapter, target);
      let result: ElectionResult | undefined = parsed[target.id];
      let error = parserError ?? (!result ? "Adapter returned no result for this contest." : undefined);
      if (result && ((result.status === "reporting" && (!result.candidates || !result.totalVotes)) ||
          (result.candidates && !hasValidCounts({ ...result, race: target.id, sourceUrl: "" })))) {
        error = "Candidate counts do not reconcile to a positive reporting total.";
        result = undefined;
      }
      if (result?.sourceId && !adapter.sources.some(source => source.id === result!.sourceId)) {
        error = "Adapter selected an unknown result source."; result = undefined;
      }
      if (error || (result && ["unavailable", "review"].includes(result.status)))
        validationFailed(target.sourceId ?? adapter.sources[0]?.id, `${target.name}: ${error ?? result?.message}`);
      if (result?.sourceId && target.sourceId && result.sourceId !== target.sourceId)
        validationFailed(target.sourceId, `${target.name}: primary source not admitted. ${result.message}`);
      const selectedId = result?.sourceId ?? (result && ["setup", "reporting"].includes(result.status) ? target.sourceId : old.sourceId ?? target.sourceId);
      const source = adapter.sources.find(source => source.id === selectedId) ?? adapter.sources[0];
      const state = source ? this.sourceState(source.id) : undefined;
      const verified = !!result && ["setup", "reporting"].includes(result.status);
      // Explicit unavailable/review/error retains the last verified cumulative
      // result for display, with stale status suppressing sheet signals.
      const failed = !result || ["unavailable", "review", "waiting"].includes(result.status);
      const content = failed ? { ...old, ...result, candidates: old.candidates, totalVotes: old.totalVotes,
        winner: undefined, status: result?.status ?? "error", message: result?.message ?? error ?? "Source unavailable." } : result;
      const hash = verified ? await bodyHash(JSON.stringify({ status: result!.status,
        candidates: result!.candidates ? [...result!.candidates].sort((a, b) => `${a.party}|${a.name}`.localeCompare(`${b.party}|${b.name}`)) : undefined,
        totalVotes: result!.totalVotes, counties: result!.counties, estimatedVotePercent: result!.estimatedVotePercent,
        reportedPrecincts: result!.reportedPrecincts, totalPrecincts: result!.totalPrecincts,
        winner: result!.winner, resultStatus: result!.resultStatus, coverage: result!.coverage })) : undefined;
      const next = { ...content, checkedAt, lastSuccessAt: verified ? checkedAt : old.lastSuccessAt,
        lastResultChangedAt: hash ? ((old as LiveResult & { resultHash?: string }).resultHash === hash ? old.lastResultChangedAt : checkedAt) : old.lastResultChangedAt,
        resultHash: hash ?? (old as LiveResult & { resultHash?: string }).resultHash,
        sourceId: source?.id,
        sourceUrl: failed && old.candidates ? old.sourceUrl : state?.url ?? source?.authorityUrl ?? source?.url ?? "",
        sourceError: state?.error ?? error, sourceSnapshots: verified ? receipts : old.sourceSnapshots };
      sql.exec("INSERT INTO results (id, data) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET data = excluded.data", target.id, JSON.stringify(next));
      if (adapter.id === 'completion-cnn' && verified && hash && hash !== (old as LiveResult & { resultHash?: string }).resultHash)
        sql.exec('INSERT INTO completion_history (target, hash, data) VALUES (?, ?, ?)', target.id, hash, JSON.stringify(next));
    }
    this.pruneSnapshots();
    return { ...this.getResults(adapter.id), checks };
  }

  private pruneSnapshots() {
    // Preserve completion evidence throughout election night for replay. This
    // adapter has only five bounded feeds; export/archive before a later election.
    if (this.ctx.storage.sql.exec<{ n: number }>('SELECT COUNT(*) AS n FROM completion_history').toArray()[0].n > 0) return;
    const sql = this.ctx.storage.sql;
    const protectedIds = new Set(sql.exec<{ data: string }>("SELECT data FROM sources").toArray().map(row => JSON.parse(row.data).snapshotId));
    for (const row of sql.exec<{ data: string }>("SELECT data FROM results").toArray())
      for (const receipt of JSON.parse(row.data).sourceSnapshots ?? []) protectedIds.add(receipt.snapshotId);
    const snapshots = sql.exec<{ id: number; source: string; size: number }>("SELECT id, source, size FROM snapshots ORDER BY id DESC").toArray();
    const counts = new Map<string, number>();
    let bytes = 0;
    const remove: number[] = [];
    for (const snapshot of snapshots) {
      const count = (counts.get(snapshot.source) ?? 0) + 1;
      counts.set(snapshot.source, count);
      bytes += snapshot.size;
      if ((count > 20 || bytes > 64_000_000) && !protectedIds.has(snapshot.id)) remove.push(snapshot.id);
    }
    this.ctx.storage.transactionSync(() => {
      for (const id of remove) { sql.exec("DELETE FROM snapshot_chunks WHERE snapshot = ?", id); sql.exec("DELETE FROM snapshots WHERE id = ?", id); }
    });
  }
}

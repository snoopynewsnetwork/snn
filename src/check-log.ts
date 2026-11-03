export const CHECK_LOG_LIMIT = 200;

export type CheckTrigger = "scheduled" | "public-refresh" | "editor-refresh";

// Every telemetry adapter records one receipt per attempted source request.
// Success includes validation, not just HTTP delivery. Change compares source
// text with the previous complete response; it does not imply vote totals changed.
export interface SourceCheck {
  adapter: string;
  official: boolean;
  sourceId: string;
  sourceName: string;
  sourceUrl: string;
  trigger: CheckTrigger;
  checkedAt: string;
  // Fetch and initial source validation, excluding waits for other endpoints.
  durationMs: number;
  success: boolean;
  change: "initial" | "changed" | "unchanged" | "unknown";
  httpStatus: number | null;
  snapshotId: number | null;
  snapshotUrl: string | null;
  responseHash: string | null;
  error: string | null;
}

export class SourceCheckLog {
  constructor(private storage: DurableObjectStorage) {
    storage.sql.exec(`CREATE TABLE IF NOT EXISTS source_checks (
      id INTEGER PRIMARY KEY AUTOINCREMENT, checkedAt TEXT NOT NULL, data TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS source_check_status (
      sourceId TEXT PRIMARY KEY, data TEXT NOT NULL
    )`);
  }

  record(check: SourceCheck): void {
    this.storage.transactionSync(() => {
      this.storage.sql.exec("INSERT INTO source_checks (checkedAt, data) VALUES (?, ?)", check.checkedAt, JSON.stringify(check));
      this.storage.sql.exec(`INSERT INTO source_check_status (sourceId, data) VALUES (?, ?)
        ON CONFLICT(sourceId) DO UPDATE SET data = excluded.data`,
        `${check.adapter}:${check.sourceId}`, JSON.stringify(check));
      this.storage.sql.exec(`DELETE FROM source_checks WHERE id NOT IN
        (SELECT id FROM source_checks ORDER BY checkedAt DESC, id DESC LIMIT ${CHECK_LOG_LIMIT})`);
    });
  }

  latestBySource(): Record<string, SourceCheck> {
    return Object.fromEntries(this.storage.sql.exec<{ sourceId: string; data: string }>(
      "SELECT sourceId, data FROM source_check_status",
    ).toArray().map(row => [row.sourceId, JSON.parse(row.data) as SourceCheck]));
  }

  latest(): (SourceCheck & { id: number })[] {
    return this.storage.sql.exec<{ id: number; data: string }>(
      `SELECT id, data FROM source_checks ORDER BY checkedAt DESC, id DESC LIMIT ${CHECK_LOG_LIMIT}`,
    ).toArray().map(row => ({ ...JSON.parse(row.data) as SourceCheck, id: row.id }));
  }
}

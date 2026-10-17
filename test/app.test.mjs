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
      await smoke(base, key);
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
      const race = await (await fetch(`${base}/api/races/ohio`)).json();
      assert.ok(
        race.notes.some((item) => item.id === note.id),
        "Note survives a Worker restart",
      );
      assert.equal(race.election, "Special");
    } finally {
      await stop();
      await rm(directory, { recursive: true, force: true });
    }
  },
);

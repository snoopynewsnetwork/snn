# Snoopy News Network

Versioned reporting notes for U.S. elections.

## Workers proof of concept

The app provides a searchable Senate race index, race details, research links,
and a dated reporting log. It imports the 35 baseline race records directly from
this repository. There is no automated news, candidate, polling, or results feed.

Live POC: https://snoopy-news-network.snoopy-news-network.workers.dev

Pull requests run the Worker checks and a deployment dry run in GitHub Actions.
Every push or merge to `main` runs those checks, deploys the Worker and Durable
Object, and verifies the live app. The workflow uses the repository secrets
`CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. The editor secret is configured
on the Worker and persists across deployments.

The Worker serves the frontend and JSON API. A SQLite-backed `Newsroom` Durable
Object named `senate-2026` stores baseline races and reporting notes. This single
object keeps the POC simple; split objects by race if traffic or scope grows.
Baseline records are refreshed when the generated seed changes. Reporting notes
survive redeployment and are never overwritten by the seed. Removing a note
hides it from the public log while preserving its row for recovery.

### Local development

Requires Node.js 22 or later and npm.

```sh
npm ci
cp .dev.vars.example .dev.vars
# Replace ADMIN_TOKEN in .dev.vars with a random key of at least 32 characters.
npm run dev
```

Open http://localhost:8787. Reading is public. Click **Editor access** and enter
the `ADMIN_TOKEN` value to add or remove notes. The key is kept only in page
memory and is cleared on reload or when you lock editing. Keep `.dev.vars`
private; it is excluded from Git. Local storage lives under `.wrangler/state`
and is separate from production.

```sh
npm run check
npm test
npm run smoke
```

The integration test runs the real local Workers runtime with isolated SQLite
storage, checks authorization and input validation, and verifies that a note
survives a complete runtime restart. Smoke checks create and remove a temporary
reporting note.

### Deploy

`wrangler.jsonc` selects the dedicated SNN Cloudflare account. The npm commands
isolate this project's Cloudflare credentials in `.wrangler/account`, leaving
the machine's existing Wrangler login alone. Always use `npm run cf -- …` for
Cloudflare commands in this project.

```sh
npm run login
npm run deploy
npm run cf -- secret put ADMIN_TOKEN
# At the prompt, enter the same editor key used in .dev.vars.
npm run smoke -- https://YOUR-WORKER.YOUR-SUBDOMAIN.workers.dev
```

For a new account, Cloudflare may require email verification and a workers.dev
subdomain before the first deployment. The configuration uses Workers static
assets and SQLite Durable Objects, compatible with the Workers Free plan and
its usage limits. No custom domain is required.

### API

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/api/health` | Check storage and the race count |
| GET | `/api/races` | List races with reporting-note counts |
| GET | `/api/races/:slug` | Read a race, research sources, and notes |
| GET | `/api/races/:slug/markets` | Read Polymarket and Kalshi prices for a race with mapped markets |
| POST | `/api/editor` | Verify the editor key |
| POST | `/api/races/:slug/notes` | Add a sourced note |
| DELETE | `/api/races/:slug/notes/:id` | Remove a note from the public log |

All POST and DELETE routes require `Authorization: Bearer <ADMIN_TOKEN>`.
Creating a note requires JSON fields `category` (`news`, `candidates`, `polling`,
`finance`, or `results`), `title`, `body`, `date` (`YYYY-MM-DD`), and `sourceUrl`
(HTTP or HTTPS). Editing fails closed if no editor secret is configured.

Market prices come from the public Polymarket and Kalshi APIs, and the Worker
caches them for five minutes. `src/markets.json` pairs each race's outcomes on
the two exchanges by party. Run `npm run check:markets` after editing it, or
when a race changes, to confirm every market is open and names the right state
and party or candidate.

This is a starting point with one shared editor key, public reporting notes,
and no user accounts. App notes are stored in the Durable Object, not written
back to the Markdown files. Keep research changes in the repository and app
notes as separate workflows until a synchronization workflow is added.

## Coverage

- [2026 U.S. Senate races](senate/2026/README.md): one directory per race, covering all 35 seats on the November 3 ballot.
- [Election-night likelihood plan](ELECTION_NIGHT_PLAN.md): county break-even targets, official result ingestion, geographic modeling, and validation; Michigan is the first research pilot.

## Updating a race

Edit the race's `README.md` and add supporting notes in the same directory.
Date each entry with `YYYY-MM-DD`, link the source, and update the relevant
verification date. Keep earlier developments in the news log so changes can be
followed over time.

These are manually maintained trackers. The initial records establish each seat,
its current holder, and official research sources. Candidate lists, polling,
campaign coverage, and results still need research; empty sections mean no
records have been entered.

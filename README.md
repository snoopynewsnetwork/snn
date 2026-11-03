# Snoopy News Network

Versioned reporting notes for U.S. elections.

## Workers proof of concept

The app provides a searchable Senate race index, race details, research links,
and a dated reporting log. It imports the 35 baseline race records directly from
this repository. Kansas and North Carolina have automatic official-source
monitoring; other races and the reporting log are manually maintained.

### Automatic election monitoring

Cloudflare runs the collector every minute, independently of visitors, Paseo,
or an agent session.
The index and both race pages show source health, last check, last verified
snapshot, last count/link change, and links to retained source responses.
Open pages reload monitoring status every minute. A source without a successful
check in 15 minutes is marked stale. Errors back off from five minutes to one
hour and retain the last verified counts.

- **North Carolina:** reads the NCSBE election catalog, all-100-county status
  file and statewide November 3, 2026 results. Validates the election, Senate
  group 1383, candidate configuration and voting-method sums. Zero setup is
  labeled separately from reported votes. Successive cumulative counts replace
  each other, including downward corrections. Precinct reporting does not
  estimate the votes remaining. Counts remain unofficial; certification is
  not inferred from a reporting percentage.
- **Kansas:** parses the SOS statewide election-night HTML, checking the 2026
  general-election metadata, election-day-or-later timestamp, Senate contest
  1001, three printed candidates, all 105 county links and candidate/total
  reconciliation. The state home/results pages and Johnson County's November
  page remain publication backstops. Access errors retain the last verified
  result. The source supplies statewide totals, not a verified county-level
  count crosswalk or voting-method split.

`GET /api/monitor` returns current status. `GET /api/monitor/snapshots/:id`
returns immutable, deduplicated UTF-8 source responses, SHA-256 hashes and HTTP
metadata. `POST /api/monitor/refresh` requires the editor key and runs an initial
check (a 30-second lease prevents duplicate requests without skipping the next
scheduled minute). The one-minute cron
continues without editor credentials. Changed source responses remain in
Durable Object SQLite across deploys. No automatic race calls or forecasts are
generated.

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

### Election-night early tells

The default **Election night** desk tracks the supplied cheat sheet: 14 Senate
margin comparisons, 48 House races plus three redraw/group guardrails, and 13
timed cues. The **Senate research** tab preserves the race index and reporting
logs. The original image is available from the desk; names, polling references,
times and scenario brackets are transcribed from it, rather than asserted as
verified ballot information.

Use **Editor access**, open a watch item, and save its reporting status, signed
D-minus-R margin (I-minus-R in Nebraska), optional estimated vote percentage
counted and sourced winner, or group GOP seat count. Timing cues record an
editor's evidence assessment. Every update requires a source URL, observation time and note.
Entries are public, shared through the existing SQLite Durable Object, and
refresh every 30 seconds while the desk is visible. Kansas and North Carolina
show automatic official vote totals at the top of the desk and derive their
watchlist margins from those counts. Other watch items use editor entries.
Opening the desk or clicking **Fetch live results** asks the server to fetch
the official sources, subject to duplicate-run protection and source backoff.
No editor key or manual result entry is needed for these two states.

Automatic margins divide D minus R votes by all candidate votes. Zero setup
produces no margin or signal; source failures retain verified counts with a
warning and suppress stale signal highlights. These live snapshots do not
overwrite the editor history, declare winners or estimate votes remaining.

A highlighted band describes the sheet's interpretation of the current entry;
it never calls a race or calculates chamber control. Fractional margins between
the sheet's literal rounded bands remain unclassified. Missing results stay
unresolved. Eastern checkpoints continue through 3am Wednesday, with separate
warnings for staggered closings and ranked-choice counting delays.

Corrections append versions and preserve prior entries. Stale editor forms are
rejected with HTTP 409, so two editors cannot silently overwrite one another.
To retract an entry, select **Awaiting results**, clear result fields, and add a
sourced explanation. View the last 20 versions in the item's **Update history**.

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
| GET | `/api/election-night` | Read the guide and latest watch-item observations |
| POST | `/api/election-night/refresh` | Fetch official results and return the live desk; public, rate limited by the collector lease |
| GET | `/api/election-night/:id/history` | Read the last 20 versions of a watch item |
| PUT | `/api/election-night/:id` | Append an editor update with `expectedVersion` concurrency protection |
| POST | `/api/editor` | Verify the editor key |
| POST | `/api/races/:slug/notes` | Add a sourced note |
| DELETE | `/api/races/:slug/notes/:id` | Remove a note from the public log |

Editing routes require `Authorization: Bearer <ADMIN_TOKEN>`; the public
`POST /api/election-night/refresh` only fetches fixed official sources and is
limited by the collector's 30-second lease.
Creating a note requires JSON fields `category` (`news`, `candidates`, `polling`,
`finance`, or `results`), `title`, `body`, `date` (`YYYY-MM-DD`), and `sourceUrl`
(HTTP or HTTPS). Editing fails closed if no editor secret is configured.

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

## Research evidence

Raw research downloads, map originals, extracted data, and review artifacts live in [snoopynewsnetwork/evidence](https://github.com/snoopynewsnetwork/evidence). Normal clones, builds, tests, and deployments of this application do not fetch that archive. Race summaries and application code remain here.

To work with evidence for a particular state, run:

```sh
node scripts/evidence.mjs massachusetts
```

Use state directory names, separated by spaces, or omit the names to fetch all states. The script makes a partial sparse clone into the ignored `evidence/` directory and links the selected states' `data/` and `maps/` directories back to their original locations. Existing research links and scripts then use the same paths. Run it again with more states to add them.

The November 2026 migration removes these directories from every published branch's Git history. Existing clones should be replaced with a fresh clone or have their local work rebased onto the rewritten history; merging an old branch can bring the archive back.

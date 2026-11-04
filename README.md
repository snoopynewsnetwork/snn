# Snoopy News Network

Versioned reporting notes for U.S. elections.

## Workers proof of concept

The app provides a searchable Senate race index, race details, research links,
and a dated reporting log. It imports the 35 baseline race records directly from
this repository. Every Senate and House race on the election cheat sheet has
automatic live monitoring. The reporting log and analytical timing cues are
maintained by editors.

### Automatic election monitoring

Cloudflare Cron runs every minute, independently of visitors, Paseo, agent
sessions or a laptop. The collector covers all 14 Senate races, 48 individual
House races, and the seven additional districts needed for the three group
watch items. Florida, Georgia and Texas governor returns, Detroit city Senate
returns, and Johnson County, Kansas Senate returns support the timing cues.
The cues still require an editor's evidence assessment.

The registry contains 27 adapters across 25 states. Each adapter runs in its own
SQLite-backed `ElectionMonitor` Durable Object, isolating network failures and
request budgets. Shared statewide feeds serve multiple races. The `Newsroom`
object saves the combined result, so browser reads do not hit election servers.
Opening the desk or **Fetch live results** requests a source check; a persisted
30-second lease coalesces concurrent requests. Scheduled failures back off from
one to fifteen minutes; publisher Retry-After delays are honoured even for
explicit fetches. Each adapter fetches its endpoints sequentially to avoid
bursts against election servers.

Official state or officially linked vendor feeds are preferred. CNN's public
results feed is an explicitly attributed newsroom fallback where official
counts cannot be collected. Kansas, Minnesota, Ohio and Pennsylvania select official results
when verified and use CNN when the official feed fails validation or access.
Source attribution follows the selected feed. The desk shows source health,
last check, last verified counts, and retained source responses under **Live
details**. Supporting county/city counts always show partial coverage.

Parsers pin November 3, 2026 election identities, contests and candidate lists,
reconcile totals, and reject nonzero test data. Zero setup is labelled
separately. Cumulative snapshots replace previous counts, including downward
corrections. Partial geography, missing data and stale counts cannot trigger
statewide/district margin bands. Precinct ratios never imply vote completion.
Group guardrails count only explicit publisher-declared wins, with leads shown
separately; they never infer seats won from current margins.

Source responses are conditionally fetched with ETags/Last-Modified where
supported. Versioned Clarity feeds resolve their numeric version pointer before
fetching the corresponding summary. Large responses are stored in SQLite
chunks with deduplicated SHA-256 evidence. Retention keeps up to 20 recent
responses per source within a 64 MB adapter budget, while protecting current
source and verified-result evidence; old unreferenced evidence can expire.
Results and editor history survive deploys.

`GET /api/monitor` returns combined source health and contest snapshots.
`GET /api/live-monitor/:adapter/snapshots/:id` returns saved evidence and HTTP
metadata (binary feeds are base64). Historical `/api/monitor/snapshots/:id`
links remain readable. `POST /api/monitor/refresh` requires the editor key;
`POST /api/election-night/refresh` is public and fetches only configured sources.

The **Source checks** page (`/#checks`) shows the latest 200 checks across
all 66 configured endpoints and an expandable source coverage list. Every
collector returns the shared `SourceCheck` receipt (`src/check-log.ts`), and the
coordinator calls `SourceCheckLog.record()` to persist it in shared SQLite.
Sources are taken directly from the adapter registry, including supporting,
versioned, binary and newsroom fallback endpoints. New adapters automatically
participate through the shared collector; do not add separate adapter logs.

Receipts include the adapter, source name and resolved URL, scheduled/public/
editor trigger, time, HTTP status, duration, success/failure, error and scoped
snapshot link. Failures include transport errors, blocked prerequisites and
reported contest validation failures, including rejected primary sources when
a fallback succeeds. Content is first response, changed, unchanged or unknown,
comparing the response hash and resolved URL with the previous complete fetch;
it does not necessarily mean votes changed. Reading or refreshing the log
never contacts publishers. Lease and backoff skips do not manufacture checks.

`GET /api/monitor/checks` returns this history and the latest receipt per source.
The page refreshes every 30 seconds while visible. History begins with the
first collector run after installation and survives deployments; older entries
are deleted at the global 200-entry limit. Per-source summaries remain visible
when their older receipts fall out of the history. Saved evidence remains
subject to the collector's existing snapshot retention policy.

Source evidence, limitations and exact endpoints:

- [Southeast: FL, GA, SC, NC, VA, KY, IN](docs/live-sources-southeast.md)
- [Northeast/Midwest: OH, MI, PA, NJ, NY, ME, NH, MS](docs/live-sources-northeast.md)
- [West/Plains: KS, TX, IA, NE, MN, AZ, CO, WI, MT, CA](docs/live-sources-west.md)

Live POC: https://snoopy-news-network.snoopy-news-network.workers.dev

Pull requests run the Worker checks and a deployment dry run in GitHub Actions.
Every push or merge to `main` runs those checks, deploys the Worker and Durable
Object, and verifies the live app. The workflow uses the repository secrets
`CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. The editor secret is configured
on the Worker and persists across deployments.

The Worker serves the frontend and JSON API. A SQLite-backed `Newsroom` Durable
Object named `senate-2026` stores baseline races, reporting notes, editor history
and the combined live desk. Per-adapter `ElectionMonitor` objects store source
responses and verified contest snapshots.
Baseline records are refreshed when the generated seed changes. Reporting notes
survive redeployment and are never overwritten by the seed. Removing a note
hides it from the public log while preserving its row for recovery.

### KY-06 county comparison

Open **House early tells → KY-06 → Live + counties** for current district totals,
all 16 county portions, and a comparison with the amended certified 2024 House
result. The live headline stays visible while scrolling through scenarios.
Counties without published votes appear first, ordered by their share of the
2024 district vote; reporting counties may also have votes outstanding.
Anderson and Bath include only their KY-06 portions.

A separate civicAPI county adapter checks election/candidate identities, the
complete county set, and each candidate's county-to-district sum. Its snapshot
has independent freshness and source evidence; CNN remains the district source.
The page flags differences between those snapshots without allocating residuals.

Presets replay 2024 or illustrate R+10, a tie, and D+5. Users can adjust a common
turnout scale and district margin, compare targets with reported D+R votes, and
download the county comparison as CSV. Targets already exceeded by published
votes are flagged. Actual ballots remaining stay unknown; scenario differences
are conditional arithmetic, not measured remaining votes or a forecast.
See [the county methodology](docs/ky-06-counties.md) for sources and calculations.

### Election-night early tells

The default **Election night** desk tracks the supplied cheat sheet: 14 Senate
margin comparisons, 48 House races plus three redraw/group guardrails, and 13
timed cues. The **Senate research** tab preserves the race index and reporting
logs. The original image is available from the desk; names, polling references,
times and scenario brackets are transcribed from it, rather than asserted as
verified ballot information.

Open a race's **Live details** for automatically fetched counts and source
health. No editor key or manual result entry is required. The browser refreshes
the saved desk every 30 seconds while visible. **Fetch live results** requests
fresh source checks and shows the latest collection time; requests within
30 seconds share the same check.

Automatic margins divide D minus R votes (Osborn minus Ricketts in Nebraska)
by all candidate votes. Zero setup produces no margin or signal. Source
failures retain verified counts with a warning and suppress stale highlights.
Automatic snapshots do not overwrite versioned editor history. Only explicit
publisher declarations can populate winners; CNN projections appear as source
notes, and no source's precinct percentage is treated as votes remaining.

Use **Editor access** to record evidence for analytical timing cues. Each update
requires a source URL, observation time and note. Editor history for automatic
races remains available through the history API, but old manual totals do not
replace unavailable live results.

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

The `/intro` page plays the Snoopy-to-Earth film, then holds the final SNN
composition while its rings keep orbiting. It has only Play/Pause and Replay
controls and does not follow scroll position. The renderer is shared with the
[graphics review workspace](graphics/snn-world-intro/README.md). Root `npm ci`
installs that workspace's dependencies, and the normal build and deployment
include the intro. Use `npm run build:intro` to rebuild the intro client alone.

Requires Node.js 22.12 or later and npm.

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
| GET | `/api/monitor/checks` | Read the latest 200 source checks and complete source coverage |
| GET | `/api/races` | List races with reporting-note counts |
| GET | `/api/races/:slug` | Read a race, research sources, and notes |
| GET | `/api/election-night` | Read the guide and latest watch-item observations |
| POST | `/api/election-night/refresh` | Fetch configured live results and return the desk; public, rate limited by the collector lease |
| GET | `/api/election-night/:id/history` | Read the last 20 versions of a watch item |
| PUT | `/api/election-night/:id` | Append an editor update with `expectedVersion` concurrency protection |
| POST | `/api/editor` | Verify the editor key |
| POST | `/api/races/:slug/notes` | Add a sourced note |
| DELETE | `/api/races/:slug/notes/:id` | Remove a note from the public log |

Editing routes require `Authorization: Bearer <ADMIN_TOKEN>`; the public
`POST /api/election-night/refresh` only fetches configured live sources and is
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

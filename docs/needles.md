# Election needles

`/needle` is the only page that renders needles. It lists one per full tracked
race (currently 72), plus House-control and Senate-control needles. Supporting
Detroit/Johnson County views feed completion collection without becoming extra
race needles. Groups reuse member races rather than adding seats.

## Public reads

| Endpoint | Response |
| --- | --- |
| `GET /api/needle` | Catalog of IDs, names, chambers, individual API URLs, and current forecast publication version |
| `GET /api/needle/:raceId` | Individual race forecast, observed counts, independent completion estimate, provenance, freshness, model version, and publication version |
| `GET /api/needle/house-control` | House seat distribution, 90% seat intervals, control probabilities, seat ledger coverage, and assumptions |
| `GET /api/needle/senate-control` | Senate equivalent, including the published vice-presidential tie-breaking caucus |
| `GET /api/completion/:target/history?after=0` | Up to 200 immutable normalized completion changes, ordered by ID; pass `nextCursor` as `after` for the next page |

Reads use saved SQLite observations and forecast runs. They do not refresh
publisher feeds. Unknown needle IDs return 404; unsupported methods return 405.
All JSON reads use `Cache-Control: no-store`. The page refreshes while visible,
limits concurrent individual requests to six, and rejects mixed publication
versions during a refresh. Missing or stale forecasts display no probability
or needle pointer. Forecasts expire after 15 minutes; the browser also hides
retained probabilities after expiry if network reads fail.

## Completion collection

The `completion-cnn` adapter runs alongside the existing state adapters in its
own `ElectionMonitor` Durable Object. Five shared CNN feeds cover the 72 full
contests and two local supporting views. The three national lists share
requests across all races. Every check participates in the shared source-check
log, lease, conditional-fetch, and backoff paths. `/api/monitor` exposes a
separate `completion` array; existing selected results are unchanged.

Pinned identities and candidate universes live in
[`src/data/completion-pins.json`](../src/data/completion-pins.json). Validation
checks contest, production flag, election type, poll-closing identity, candidate
names/parties, reconciled totals, parent vote embargo, extraction date, and the
expected-vote percentage. Local rows are selected explicitly, avoiding overlap
between Michigan counties and their constituent municipalities. The collector
does not sum county rows or substitute whole counties for split districts.
Generalized county/method forecasting inputs beyond the two local views remain
future work; the expected-vote field alone is not a partisan forecast.

Remaining contest votes are approximately `V * (100 / p - 1)` using the CNN
count `V` and percentage `p` from the same snapshot. Official counts remain
separate. Zero setup, zero/missing/invalid percentages, a displayed 100%, and
stale observations return no derived remaining count. The supplier extraction
clock is treated as UTC when its timestamp omits an offset; the original text
is preserved. Both source extraction and successful collection must be within
15 minutes. Unknown rounding precision is disclosed, not converted to a
fabricated confidence interval. These are contest votes, not eligible ballots
or a two-party denominator.

Changed normalized completion observations are append-only; downward
corrections replace latest cumulative counts and append a new observation.
Completion raw evidence bypasses the state adapters' rolling 20-response
retention so it remains replayable throughout election night. Monitor storage
usage and export the completion Durable Object after the election before
reusing it for a future election. Other adapters retain their existing limits.

## Publishing calibrated forecasts

The repository includes a complete sourced chamber ledger; see
[chamber-ledger.md](chamber-ledger.md). There is no calibrated forecast producer
yet. Live counts and completion percentages cannot establish win
probabilities on their own. The default page/API therefore report
`uncalibrated` for races and `unavailable` for chamber control. They become
functional forecasts when an editor publishes a coherent calibrated joint run.
The chamber APIs automatically include sourced holdovers/declarations, expose
complete inventory separately from missing model inputs, and suppress odds when
a model contradicts a ledger outcome.

`PUT /api/needle/forecast` requires the existing editor bearer token and JSON
`{ "expectedVersion": 0, "run": ... }`. Successful publication returns HTTP
201 with the new version. Stale versions and backwards timestamps return 409;
invalid runs return 400. Requests are limited to 8 MB. All runs are retained
as immutable chunked artifacts in Newsroom SQLite and survive redeploys.
The endpoint is a model-output import, not a result-entry form or calibration
procedure. A calibration URL is a publisher attestation; the server validates
its format without fetching or verifying the external report.

The run schema is defined by `ForecastRun` in
[`src/needle-model.ts`](../src/needle-model.ts):

```json
{
  "electionDate": "2026-11-03",
  "asOf": "2026-11-04T01:00:00Z",
  "modelVersion": "your-calibrated-model-version",
  "calibrationUrl": "https://your-newsroom.example/calibration-report",
  "assumptions": ["Document independent caucusing and fixed-seat assumptions."],
  "races": [{
    "id": "senate-mi",
    "name": "Michigan U.S. Senate",
    "chamber": "senate",
    "seatId": "senate-mi-2",
    "outcomes": "DDRR",
    "margins": [2, 1, -1, -2]
  }],
  "fixedSeats": { "house": [], "senate": [] },
  "senateTieBreaker": "R"
}
```

This four-draw example illustrates the wire format; it is not a calibrated
forecast and its chamber ledgers are incomplete. `outcomes` contains one
winning **caucus** code per simulation draw: D, R, or O (other/unresolved).
The same character index across every race is the same joint draw, preserving
national/regional correlations. Declare an independent's caucus assumptions
explicitly, using O when unresolved. Do not label an independent Democrat
merely to obtain complementary probabilities. Optional `margins` are D-minus-R
percentage points of all candidate votes, one per draw. All races use the same
draw count, between 1 and 10,000. Include forecasts for additional relevant
races even if the results desk does not yet monitor them.

House seat IDs equal the existing race ID, such as `house-mi-07`, including
`01` for at-large districts. Senate seat IDs identify state and constitutional
class, such as `senate-mi-2`. Each fixed seat is an object containing `id`,
`caucus`, HTTPS `sourceUrl`, and `basis`: `not-up`, `declared`, or `assumption`.
Assumptions require disclosure in the run. Seat identity validation prevents
duplicates, overlapping fixed/forecast seats, and more than two senators per
state. Model the incoming Congress; a special election for an outgoing term
must not add another seat. The House seat catalog contains 435 regular seats,
excluding the separate TX-18 special-election entry in CNN's list.

Control is evaluated on each joint draw and averaged. House thresholds are
218 caucus seats. Senate thresholds are 50 for the published tie-breaking
caucus and 51 for the other caucus. Missing forecast inputs suppress control odds rather
than counting untracked incumbents as winners. D/R/O probabilities sum to one;
Republican odds are not assumed to complement Democratic odds when other
outcomes exist. The exact independent-race Poisson-binomial convolution is
implemented as a reference calculation, with tests demonstrating why shared
errors change chamber odds. Simulation standard error measures sampling error,
not uncertainty about model calibration or assumptions.

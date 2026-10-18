# State election-night research brief

Authorized 2026-10-17: use Paseo agent stacks for all **35 states with a 2026
Senate race in this repo**, including the Florida and Ohio special elections;
answer the Michigan questions and push directly to main. Michigan is complete;
the [durable queue](research-queue.json) contains the other 34 states. Read the
root [election-night plan](../../ELECTION_NIGHT_PLAN.md) and the
[Michigan package](michigan/README.md) as methodological references.

## Stack and ownership

One batch coordinator owns integration, queue updates, reviews, commits and
pushes. For each queued state, create **four state-specific Paseo agents**, one
per original question. At most **two research workers** may run concurrently;
the coordinator researches newsroom backstops and integrates results meanwhile.
Do not spawn other coordinators or grandchildren. Use asynchronous finish
notifications, not status polling. Reuse agents for repairs when appropriate.

| Worker | Owned paths under `senate/2026/<state>/` | Research |
| --- | --- | --- |
| Turnout | `turnout.md`, `data/county-turnout.csv`, `data/turnout/` | Rank all reporting geographies by recent statewide election volume. Measure top-15 share and the smallest set reaching 80%. Include a recent midterm comparator. Distinguish contest votes, ballots cast and registration. |
| Partisanship | `county-partisanship.md`, `data/county-baselines.csv`, `data/baselines/` | Numerical D/R/mixed baselines from the most relevant recent Senate contest, 2024 president and a recent midterm statewide contest. Compute turnout-weighted tie and cushion scenarios, county contributions and candidate/coalition caveats. |
| Official results | `official-results.md`, `data/official-results-sources.csv`, `data/results-sources/` | Inventory official state/local channels across the whole state. Inspect the priority set deeply: authority chain, linked vendors, public feeds/downloads, bounded samples, timestamps, corrections, completion semantics, access and cadence gaps. |
| Precinct maps | `precinct-maps.md`, `maps/` | Download actual precinct assets for the measured 80% set, with a map index and previews where practical. Preserve source/vintage/retrieval/counts/checksums; distinguish baseline, current and approved November reporting units. |

Dispatch turnout and partisanship first. Reconcile their coverage and priority
set before giving the exact list and data paths to official-results and map
agents. Workers must not edit another assignment, the state README or common
files, and must not change Git state, commit or push. The coordinator is the
sole Git writer. All work uses the shared checkout `/Users/tqbf/codebase/snn`.

## Integrated state package

The coordinator also writes these within each state directory:

- `local-news-results.md`: verified regional scoreboards and counting coverage,
  inspectable embedded channels, upstream suppliers/duplication, and NYT as a
  national cross-check. Verify November availability and access; do not invent
  URLs or count shared AP feeds as independent confirmations.
- `live-polling-strategy.md`: state-specific collection cadence, source
  precedence, raw snapshots/replay, corrections, source health, manual fallback,
  geographic comparison, and uncertain remaining-vote ranges. Mark proposed
  settings separately from demonstrated publication cadence.
- `research-dispatch.md`: actual Paseo question-agent IDs and ownership.
- `research-review.md`: checks, reconciliations, fixes and unresolved gaps;
  distinguish scenario readiness from calibrated live probabilities.
- A research section in the state README linking the package while preserving
  the existing race tracker. Do not fill campaign/polling sections with guesses.

Retain reproducible transformations and meaningful validation scripts, bounded
public samples and provenance. Maps require actual downloaded assets, not just
landing-page links. If blocked, record the attempted source, exact missing
geography/vintage and any clearly labeled alternative.

## Accuracy and geographic exceptions

Browse current sources. Prefer official election offices and linked vendors
for counts/maps; primary newsroom pages for news products. Date observations,
cite direct URLs, preserve retrieval metadata, and distinguish tested feeds
from inspected landing pages. Never guess contest IDs, APIs, guaranteed live
cadence, exact remaining votes or current approval of historical boundaries.
Reject test data and old elections. NYT may require manual observation until
automated access is verified. Separate external calls/forecasts from counts.

Use actual reporting geography: Virginia independent cities, New England towns,
Alaska election reporting units, and native precinct/board IDs. Do not fabricate
county results by aggregating unmatched districts. Explain noncounty schemas
and any compatibility filename using `county-`; retain FIPS where meaningful.

Verify 2026 election rules with official sources, including Alaska/Maine ranked
choice and Louisiana's primary/runoff structure. Separate first-choice,
elimination-round and final counts. A 2024 presidential result is not a 2024
Senate result in a state without that election. Identify election, contest,
candidates, denominator and geography for every baseline. Do not label an
independent as a Democrat or silently combine coalitions. If no Democrat is on
the ballot, show the named opposition candidate scenario separately.

Reconcile all-geography candidate sums to primary statewide totals. Label
derivatives and unexplained discrepancies. For a two-candidate scenario at
fixed turnout weights, a uniform D-share shift `(R-D)/(2*(D+R))` ties. A D+1
margin requires another 0.5 percentage points of D share. Explain share points
versus margin points, turnout sensitivity and already-winning baselines. Do
not force this arithmetic onto unresolved ranked-choice, runoff or substantial
third-candidate outcomes. Keep counted votes fixed; forecast only the remainder.

## Assets and checks

Record source URLs, retrieval times, CRS, feature counts, pagination checks,
geometry defects and hashes. Census VTDs and third-party historical layers are
not automatically current precincts. Compress raw evidence losslessly, subset
large statewide files, avoid duplicates and keep individual Git objects below
40 MB by compression or documented splitting. Never silently simplify original
data; keep preview derivatives separate.

Validate geography uniqueness/coverage, candidate sums, D/R/other balances,
weights totaling one, 80% threshold, scenario tie/cushion arithmetic, source
inventory coverage, map counts/pagination, checksums and relative Markdown
links. Do not call generic link lists a completed substantive investigation.
Document unavoidable gaps honestly rather than inventing values.

## Publication and continuation

Stage only the reviewed state directory and the coordinator's queue/dispatch
updates. Never use `git add .`, reset others' files, switch branches, rebase an
active shared tree or force-push. Inspect staged paths, run whitespace checks,
commit on main, push origin main and verify the remote contains the commit.
Publish each state as it finishes; do not wait for all 34.

Update `research-queue.json` with actual agent IDs, progress, checks, gaps and
published commit IDs; update the root dispatch record at milestones. Resume
from those files after compaction. Continue through **all 34 queued states**,
retaining completed Michigan. Do not finish after launching only the first
wave or after completing one state. A blocked source should not stop other
work; try alternatives and retain specific gaps. Recover launch/provider
failures from the queue. Send concise milestone updates and report completion
only when the batch is actually finished.

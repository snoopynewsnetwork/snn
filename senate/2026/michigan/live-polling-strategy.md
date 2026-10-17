# Michigan election-night live polling strategy

Recorded: **2026-10-17**. [Michigan research index](README.md) ·
[Repo-wide election-night plan](../../../ELECTION_NIGHT_PLAN.md) ·
[Official source inventory](official-results.md)

## Approach

Build a county-first collector that records every changed official snapshot,
with a separate process updating county break-even scenarios and the eventual
forecast. The first milestone is a continuously recording collector, replayable
snapshots, and a trustworthy county coverage board. This document describes the
proposed operation; no continuous poller has been deployed.

The [Michigan Voting Dashboard documentation](https://www.michigan.gov/sos/elections/election-results-and-data/voter-participation-dashboard),
checked 2026-10-17, says the dashboard supplies participation data rather than
official or unofficial election results. Use county publication channels for
candidate returns and state results for reconciliation. Preserve the official
clerk-to-vendor authority chain already recorded in the source inventory.

The [turnout research](turnout.md) identifies 23 priority counties accounting
for 80.4162% of baseline 2024 Senate contest votes. Collect all 83 counties for
statewide arithmetic. As the night progresses, prioritize outstanding votes
and uncertainty as well as historical county volume.

## Proposed polling intervals

These are starting settings, not vendor publication promises. Adjust them to
observed update frequency, source limits, and operational evidence.

| Source | Starting interval |
| --- | --- |
| Working feeds for the 23 priority counties | 60 seconds |
| Other 60 counties | 3 minutes |
| Counties dominating remaining uncertainty late in the count | 30–60 seconds |
| PDF reports | 3–5 minutes |
| State results, for reconciliation | 5 minutes |

Run low-frequency preflight checks before polls close. Increase cadence around
each jurisdiction's local closing time, then continue through the next day and
any unresolved count. Verify election, contest, candidate identities and
publication status before admitting results. An accessible pre-election feed
may contain scaffold or test data.

## Genesee 2026 preflight observation

A bounded public HTTP probe on **2026-10-17** confirmed that the county-linked
November 2026 Clarity election has an accessible version pointer and Senate
summary. The [Genesee clerk's page](https://www.geneseecountymi.gov/departments/county_clerk/election_division.php)
links the actual [November 3, 2026 results destination](https://results.enr.clarityelections.com/MI/Genesee/127354/).

| Observation | Value on the probe date |
| --- | --- |
| Election ID | `127354` |
| [Version pointer](https://results.enr.clarityelections.com/MI/Genesee/127354/current_ver.txt) | `381162` |
| [Versioned Senate summary](https://results.enr.clarityelections.com/MI/Genesee/127354/381162/json/en/summary.json) | Contest `C="United States Senator"`, `K="30"` |
| Candidate labels | Abdul El-Sayed; Mike Rogers; Lydia Christensen; Tim Long; Douglas P. Marsh; Walter P. Kristy; Unassigned write-ins |
| Candidate vote array `V` | Seven zeroes |
| Total `T` | `[0]`, an array in this response |
| Reporting fields | `PR=0`, `TP=142` |

These were zero-vote scaffold observations, not election returns or independent
ballot certification. The version pointer is mutable. The 2024 sample used
Senate contest key `87` and a scalar total; the 2026 probe uses key `30` and an
array total. Resolve identities per election and validate field shapes rather
than copying historical IDs or assuming an unchanged schema. Handle response
compression explicitly.

The working scaffold makes a pre-election adapter rehearsal possible. It does
not establish election-night cadence, remaining-vote counts, voting-method
splits, or the completeness semantics of the reporting fields.

## Collector operation

1. **Build adapters by reporting system.** Start with Clarity and the tested
   Genesee examples. Poll `current_ver.txt`; on a change, pin related summary
   and detail requests to that version. Include occasional full-summary
   consistency checks because version behavior has not been established as
   a guaranteed API contract. Next inspect Enhanced Voting, which
   [Kent officially links for November](https://www.kentcountymi.gov/197/Elections).
   Its actual candidate-data requests still need verification. Keep county
   configuration for election IDs, contests, candidates, and fallback sources.
2. **Archive before interpreting.** Save every changed response with URL,
   retrieval UTC, publisher timestamp when verified, version, body hash and
   parser version. Maintain a fetch log even when content does not change.
   Normalize observations into county/jurisdiction/reporting-unit/method/
   candidate counts, retaining unknown fields as null. Deduplicate retries by
   source, election, version and content identity.
3. **Replace snapshots; derive batches afterward.** Do not add successive
   cumulative totals. Derive differences between compatible snapshots and
   preserve negative corrections with an operator alert. Reconcile precinct
   detail to county totals before accepting a coherent update. Keep the last
   good state when a fetch or parse fails; reject challenge HTML and app shells
   as candidate data even when HTTP status is 200.
4. **Separate health from vote movement.** Display last successful fetch and
   last results change independently. No new votes for an hour can be a
   healthy source. Use jitter, bounded per-host concurrency, conditional
   requests where supported, explicit timeouts, and backoff on failures or
   rate limits. Source limits take precedence over the proposed cadence.
5. **Provide a manual lane immediately.** Wayne's current official outbound
   vendor linkage remains a high-impact gap in the research. Prepare browser
   and PDF capture with sourced, timestamped manual entries. Detroit can help
   explain Wayne's progress, but its votes overlap Wayne. Manual and automated
   observations need explicit precedence and replacement rules. Preserve the
   publication's unofficial/canvassed/certified status.

## Coverage board and live estimate

For every county display source status, last successful fetch, last content
change, counted candidate votes, available precinct/method detail, and remaining
votes as an estimate/range or **unknown**. Source freshness and missing coverage
must be visible alongside the projected statewide result.

Each accepted coherent update should trigger:

- Reconciliation of county and precinct totals, with state and municipal
  overlaps excluded from double counting.
- Comparison with the same geographic and voting-method slice of 2024 where
  a verified crosswalk permits it. Widen uncertainty or use a coarser aggregate
  when comparable slices are unavailable.
- Revised low/base/high outstanding-vote estimates with their evidence and
  assumptions retained.
- Revised county net-vote contributions and conditional break-even shares.

An immediately useful display is: **given these remaining-vote assumptions,
Democrats need X% of what remains; recent comparable returns suggest Y%.**
Keep counted votes fixed and forecast the remainder. Use the conditional
arithmetic in the root plan and show sensitivity to the outstanding-vote range.
“Precincts reporting” is separate from estimated vote completion. Published
win probabilities require the remaining-vote model and calibration gates in
the plan; the existing historical target calculator is a deterministic
scenario tool.

## Fit with the existing Cloudflare app

Start with a one-minute Cron scheduler, per-source due times and polling state,
SQLite observations, and object storage for changed raw snapshots. Keep
collection independent of requests to the user-facing app. Recompute derived
outputs from accepted changes, rather than rerunning the forecast after every
unchanged HTTP response. Isolate source failures so one broken county cannot
halt all collection.

Cloudflare's [Cron documentation](https://developers.cloudflare.com/workers/configuration/cron-triggers/),
checked 2026-10-17, supports minute-level scheduling. If observed update patterns
justify subminute polling, use [Durable Object alarms](https://developers.cloudflare.com/durable-objects/api/alarms/),
whose documented at-least-once execution requires idempotent writes. Durable
Objects allow one scheduled alarm per object; manage multiple due sources
within the scheduler or separate collector objects. This is a proposed
architecture, not an implementation already present in the POC.

## Implementation order

1. Verify this year's county/election/candidate configurations and implement
   the Genesee Clarity collector against the zero-vote scaffold.
2. Store immutable changed snapshots and a fetch/health log; prove deterministic
   replay, duplicate handling, coherent version reads, and correction handling.
3. Verify Enhanced Voting data requests and expand priority-county coverage;
   resolve Wayne and establish the manual lane. Fill out all 83 counties.
4. Add the coverage board and continuously updated break-even scenarios.
5. Complete remaining-vote modeling, historical replay and calibration before
   publishing a live win probability. Synthetic fixtures can test collector
   behavior but do not establish historical forecast calibration.

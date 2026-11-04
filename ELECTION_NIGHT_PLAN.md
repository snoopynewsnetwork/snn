# Election-night likelihood and county break-even plan

Created: 2026-10-17. First research pilot: [Michigan](senate/2026/michigan/README.md).
Updated: 2026-11-03 against `origin/main` at `35c5bbd`.

Implementation status: `/needle`, individual race/chamber APIs, independent
completion collection for all 74 result targets, completion history, and joint
chamber probability arithmetic are implemented. See [the API and model-input
contract](docs/needles.md). An editor can publish an immutable calibrated joint
run. A [complete sourced chamber ledger](docs/chamber-ledger.md) now accounts
for every seat, known holdovers and explicit declarations; unresolved elections
still need model inputs. No calibrated forecast producer has been supplied yet. The default needles therefore show explicit unavailable
states. The [forecast-input acquisition plan](docs/forecast-inputs-plan.md) specifies
the remaining input work. General county/method modeling inputs, geographic maps/scenarios,
historical replay, and calibration remain the modeling milestones below.

## Objective and scope

Estimate the probability of a Democratic Senate win as official results arrive,
using the geography and voting method of counted and outstanding votes. Show
which counties are above or below a stated winning scenario and how much the
Democrat must improve on a historical baseline to win statewide. This is a
research and implementation plan, not a functioning forecast or an election
call. Research artifacts and unresolved gaps must remain visible.

The remaining-vote collection milestone below covers every currently tracked
contest, including House and governor races and the two supporting local
views. The county break-even and calibrated forecast sections retain Michigan
Senate as the first modeling pilot. Completion coverage alone does not establish
a calibrated needle for any contest. Also provide House-control and
Senate-control needles calculated from the relevant race outcome distributions
and the seats outside those elections, as specified below.

There is no unique amount that Democrats must outperform in every county:
gains in one county can offset losses or turnout changes elsewhere. Publish a
uniform-swing benchmark, alternative county turnout scenarios, and conditional
break-even requirements. Distinguish Democratic vote-share points, D-minus-R
margin points, and net votes; they are different quantities.

## Michigan research assignments

Use four Paseo research agents, one per question. Each writes only its assigned
files under `senate/2026/michigan/`, with dated source citations, retrieval
details, explicit gaps, and reproducible calculations where applicable. Agents
must not change branches, commit, push, deploy, or edit one another's files.
The coordinating agent reviews and commits the integrated work to local main.

| Assignment | Questions and required deliverables |
| --- | --- |
| Turnout | Which counties supply the most votes? Rank all 83 using certified 2024 Senate contest votes and, separately, ballots cast where available; add 2022 midterm turnout and 2020 Senate comparisons. Store `turnout.md`, `data/county-turnout.csv`, underlying extracts, and a reproducible calculation script. Identify the top 15 and the smallest county set reaching 80% of baseline contest votes. |
| Partisanship and targets | Which counties are D/R and by how much? Build all-county 2024 Senate and presidential baselines; add 2020 Senate and 2022 statewide context where feasible. Store `county-partisanship.md`, `data/county-baselines.csv`, and reproducible county break-even scenario calculations. Labels are historical election outcomes, not permanent county identities. |
| Official reporting | Where do state, county, and relevant municipal officials publish results? Inspect official landing pages and their linked reporting vendors, downloadable files, update behavior, identifiers, voting-method splits, and outstanding-vote information. Store `official-results.md`, `data/official-results-sources.csv`, and small representative public samples. Inventory all 83 counties; inspect the high-volume counties deeply and state untested coverage honestly. |
| Precinct maps | Download official maps/boundaries for the high-turnout counties, not just links. Start with the likely large counties and reconcile against the turnout ranking. Store `precinct-maps.md`, `maps/manifest.csv`, map assets, and small GIS samples as practical. Include geometry vintage, provenance, checksum, CRS, precinct identifier examples, and gaps between geographic precincts and absentee counting boards. |

“Big turnout” defaults to the union of the top 15 counties and the smallest
set accounting for at least 80% of 2024 Senate contest votes, with Detroit
examined within Wayne County. This is a research priority, not permission to
omit other counties from statewide arithmetic. Until the turnout ranking is
computed, map and source agents should label their initial list provisional.

## Historical baseline and geography

1. Use certified **2024 U.S. Senate** results as the primary recent contest
   baseline, with all candidate votes retained. This is a different seat and
   Democratic candidate from 2026, so do not treat candidate effects as fixed.
2. Keep **2024 president** as a separate comparison, **2020 Senate** as the
   previous election for this Senate seat, and **2022 statewide contests** as
   midterm turnout and geographic context. Do not silently substitute a
   presidential or gubernatorial result for a Senate result.
3. Keep raw candidate counts, party, contest total, ballots cast, undervotes,
   overvotes, registered voters, and source status distinct. “Turnout” can mean
   ballots cast or votes in a contest; every column must say which denominator
   it uses. Do not infer voting-eligible turnout from registration.
4. Use county FIPS plus jurisdiction and source-native precinct/board IDs as
   stable keys. Version boundaries and crosswalk old precincts to 2026 units;
   retain unmatched units for review. Never join on precinct number alone.
5. Treat absentee counting boards, early-vote units, and combined precincts as
   reporting units that may lack a corresponding polygon. County totals must
   reconcile even when a finer geographic allocation is unavailable. A 2020
   Census voting district is a fallback historical layer, not proof of a
   current 2026 precinct boundary.

## County targets before election night

For county `c`, let `D0_c` and `R0_c` be baseline major-party votes,
`s0_c = D0_c / (D0_c + R0_c)`, and `T_c` the scenario's expected final
**major-party Senate votes** in 2026. Keep turnout weights separate from vote
preference. Simulate third-party share separately when converting total ballots
or total contest votes into `T_c`.

```text
M0 = sum_c T_c * (2*s0_c - 1)                 baseline D-minus-R net votes
T  = sum_c T_c
delta_share = -M0 / (2*T)                    additive D-share change for a tie
county_target_share_c = s0_c + delta_share
county_target_margin_c = 2*county_target_share_c - 1
county_target_net_votes_c = T_c * county_target_margin_c

delta_share_for_margin_m = (m*T - M0) / (2*T)  m=0.01 means a D+1 margin
```

Multiply fractional changes by 100 for percentage points. A +1 pp change in
Democratic two-party share means +2 pp in the D-minus-R margin and `0.02*T_c`
additional net votes at fixed turnout. Add a small statewide vote cushion to
define a win rather than a tie. If a target share falls outside [0, 1], solve
with bounded shares and flag the original uniform-shift scenario infeasible.

If the baseline Democrat already won, unchanged shares and turnout may already
produce a Democratic win: the required improvement can be zero or negative.
The point is the statewide threshold, not a presumption that every county must
improve. Round display values only after calculations; preserve raw integers.

Produce these scenario tables for all counties:

- Baseline shares with historical turnout weights; statewide tie and a clearly
  labeled illustrative D+1 margin cushion, expressed in **margin points**.
- A 2022-like county turnout mix, a 2024-like mix, and researched low/base/high
  turnout assumptions. Scale totals explicitly; distinguish composition effects
  from statewide participation changes. These scenarios are sensitivity
  analyses, not assertions about 2026 turnout.
- A user-adjustable scenario that holds all other counties at their expected
  margins and solves for the one selected county's break-even share. Mark
  requirements below 0% as already secured under those assumptions and above
  100% as impossible under those assumptions.

Each row should include county, FIPS, baseline contest/year, D/R votes,
two-party D share, D-minus-R margin, expected turnout, turnout weight,
target share/margin, required change from baseline, target net votes, and the
net-vote value of a +1 pp improvement in D share. The statewide sums must
reproduce the stated tie/cushion. Never present a county's target as a
standalone necessary condition for winning Michigan.

## Live ingestion and official-source provenance

Build adapters only after inspecting the Michigan source inventory. Start with
county-level snapshots and add precinct/voting-method detail where available.
Do not assume a public API, guaranteed real-time service, or future election URL
exists because an old election page does.

For every fetch, save original bytes or a content-addressed reference, URL,
retrieval time in UTC, source update time with its timezone, HTTP metadata,
election/contest ID, parser version, and official status. Distinguish unofficial
election-night results, canvassed results, and certified results. Poll at a
reasonable source-specific interval; respect stated limits and use backoff.
Retain timestamped manual-entry fallbacks when feeds cannot be automated.

For Michigan, supplement official channels with the
[regional newsroom sources and NYT national backstop](senate/2026/michigan/local-news-results.md).
Compare NYT's real-time statewide and available county Senate totals with our
observations, preserving attribution, timestamps and any explicit source
substitution. Verify November coverage and access before automation. Keep
external race calls, completion estimates and Needle forecasts separate from
reported votes; reconcile overlapping sources without adding or averaging them.

Normalize county, jurisdiction, reporting unit, voting method, candidate,
party, vote count, units reported/total, and estimated remaining votes with
provenance and uncertainty. Missing is not zero. Preserve revision history,
including corrections that reduce totals. Replace cumulative snapshots rather
than adding them together. A vendor linked from a clerk's page is an official
publication channel; an unlinked third-party aggregator is not automatically
official. Record state/county overlaps and choose one authoritative observation
per unit/time to avoid double counting.

Do not use “precincts reporting” as “percent of votes counted.” A large absentee
board can contain more votes than many physical precincts, and a reporting
precinct may be incomplete. Determine what completion fields actually mean
for each source. Track already-counted vs outstanding absentee, early in-person,
Election Day, provisional, and other eligible late-processed ballots only to
the granularity supported by official evidence. Record the source and time of
outstanding-vote estimates; do not invent exact counts from percentages.

## Remaining-vote coverage for the current desk

### Implementation baseline, 2026-11-03

The existing collector tracks 72 full contests (14 Senate, 55 House, three
governor) plus Detroit-city and Johnson County Senate views. The three House
group watch items reuse member contests. The 13 analytical timing cues are
editor assessments, not additional contests needing turnout denominators.
The current registry has 26 adapters and 64 source endpoints; derive future
coverage inventories from the registry rather than maintaining these counts
as configuration.

`main` already normalizes CNN `percentReporting` as `estimatedVotePercent`
for admitted reporting results and displays it on dashboard cards. It remains
attached to the selected result source: an official result can take precedence
without receiving an independent CNN completion estimate. Other adapters and
the two supporting local parsers do not yet provide consistent completion
coverage. Do not reimplement the existing percentage display as the next step.

### Source coverage and evidence

Read-only probes on 2026-11-03 matched all 72 full contests to CNN's national
lists. Each matched record contained `totalVote`, `percentReporting`, and
`countyVotesAvailable: true`. These probes observed zero-vote setup records;
they verify identities and fields, not useful post-close estimates or complete
geographic coverage. Capture reproducible fixtures and a dated coverage
manifest before admitting new sources to the collector.

| Tracked scope | Candidate completion source | Required validation |
| --- | --- | --- |
| All 72 full contests | CNN [Senate](https://politics.api.cnn.io/results/national-races/2026-SG.json), [House](https://politics.api.cnn.io/results/national-races/2026-HG.json), and [governor](https://politics.api.cnn.io/results/national-races/2026-GG.json) lists | Pin each target's actual `ecKey`, election identity, candidate universe, production/embargo gates, timestamps, and expected-vote field meaning. Florida and Ohio Senate use `2026-SP-FL` and `2026-SP-OH`; do not construct all keys as regular general elections. |
| Johnson County Senate | CNN [Kansas county results](https://politics.api.cnn.io/results/county-races/2026-SG-KS.json), Johnson FIPS `20091` | Validate the county and contest together; statewide percentages cannot stand in for Johnson County. |
| Detroit city Senate | CNN [Michigan local results](https://politics.api.cnn.io/results/county-races/2026-SG-MI.json), distinct `Wayne County - Detroit` record | Pin the city record and native identifier; do not substitute Wayne County or assume every source geography code is a Census FIPS. |
| Three House group watch items | Existing member contests | Show member completion separately; any combined completion must use compatible expected-vote totals, never an unweighted average of percentages. |

County-result endpoints were spot-checked for Kansas Senate, Michigan Senate,
Florida special Senate, VA-07, CA-22, and TX-32. Every checked endpoint returned
geographic records with percentages and counts. The other endpoints still need
inspection. CNN's Michigan endpoint includes both counties and constituent
municipalities: select one nonoverlapping level for each aggregation. For House
contests, validate county-within-district scope against the current map; never
substitute all votes in a split county. A `countyVotesAvailable` flag is a
discovery hint, not evidence that all expected rows are present.

### Collection and normalized contract

1. Add completion collection independently of result-source selection. Reuse
   already fetched CNN bodies and evaluate the three shared national lists as
   the broad-coverage fetch path. Add local/geographic endpoints as needed.
   Fit this into the existing adapter leases, backoff, evidence storage, and
   shared source-check receipts; browser reads must not contact publishers.
2. Keep the selected official or supplier result intact. Store a separately
   attributed completion observation containing target/contest, geography and
   parent, voting method when available, supplier votes counted, estimated
   percentage counted, source URL/ID, source update and retrieval times,
   snapshot reference, parser version, and validation/freshness status.
   Preserve the existing `estimatedVotePercent` API behavior for consumers.
3. Return an explicit unknown/setup/unavailable/stale state when appropriate.
   Zero-vote setup does not imply an estimated final turnout. Missing methods,
   counties, and percentages remain unknown rather than zero. Independent
   completion failures must not invalidate fresh official result counts.
4. Retain an append-only normalized observation history and enough raw
   evidence to replay the full election night. Current raw retention (20
   recent responses per source within a 64 MB adapter budget, with protected
   current evidence) and the global 200-check log are not a full replay archive.
   Plan storage limits/export and correction handling before increasing feeds.

For supplier contest votes `V` and a validated expected-vote percentage `p`,
the optional derived estimates are:

```text
estimated final contest votes = V * 100 / p
estimated remaining contest votes = V * (100 / p - 1)
```

Calculate only for positive reporting counts and `0 < p < 100`. Use `V` and
`p` from the same source snapshot and geographic scope, never official counts
divided by an asynchronously updated supplier percentage. Keep the supplier
estimate visible beside official counts with both timestamps and any material
disagreement. These are approximate contest votes, not an exact inventory of
uncounted ballots or remaining major-party votes. Do not feed them directly
into the two-party break-even formulas without modeling third-party share.

Validate percentage units, finite range, rounding, and caps. A rounded/capped
percentage does not support an exact remaining count; a displayed 100% alone
must not mark a contest final or force remaining votes to zero. Preserve
revisions to turnout estimates even when percentages decrease. Where source
precision is known, expose the implied range; otherwise label uncertainty as
unquantified rather than inventing a confidence interval. Actual outstanding
ballot reports remain a separate observation with ballot/contest denominator,
eligibility, geography, and time explicitly recorded.

### Supported sources and forecast gates

CNN's public endpoints are an available integration path, not a documented
service guarantee. Evaluate supported AP Elections API access as an alternative:
its [response contract](https://developer.ap.org/ap-elections-api/docs/Elections_Response_Data_Elements.htm)
documents `eevp` and voting-method percentages where available, and its
[terminology](https://developer.ap.org/ap-elections-api/docs/US-Elections_Terminology.htm)
defines expected-vote percentages at state, county, and congressional-district
levels. Confirm access terms, update cadence, exact contest coverage and
Detroit-city support before treating AP as a replacement. No subscription or
purchase is authorized by this plan.

Supplement with official outstanding-ballot reports when published. For
example, California's [unprocessed-ballot report](https://www.sos.ca.gov/administration/news-releases-and-advisories/2026-news-releases-and-advisories/california-secretary-state-shirley-n-weber-phd-issues-unprocessed-ballots-report)
documents county officials' estimates for the June 2026 primary; inspect the
November report and its availability rather than assuming the earlier URL is
the live general-election source. Countywide ballot inventories cannot be
assigned wholesale to one congressional district.

Deliver completion coverage before forecasts. County/municipal remaining-vote
estimates help locate outstanding votes, but partisan projections still require
comparable historical geography, voting-method composition or explicit unknowns,
turnout uncertainty, and the calibration gates below. Ranked-choice contests
also require separate treatment of first-choice counting and later transfers.

## Estimation as results arrive

Keep counted votes fixed. Forecast only remaining votes, with uncertainty in
both their number and partisan composition. Partial results should be compared
with the same geographic/voting-method slice of the baseline, not the whole
county. When comparable slices are unavailable, widen uncertainty and label
the observation as unsuitable for a direct swing estimate.

For reporting unit `u`, model its remaining two-party D share using a bounded
model such as:

```text
logit(q_u) = logit(baseline_share_u)
             + statewide_swing + regional_effect
             + county_effect + voting_method_effect + local_residual
```

Estimate effects from comparable returns, partially pooling sparse units.
Model overdispersion and shared statewide/regional errors; thousands of
precincts are not independent polls. Model turnout and voting-method mix
jointly with shares when evidence supports it. Early-reporting units need not
represent late-reporting units. A new batch is informative about similar
outstanding units, not proof of uniform statewide swing.

Start with an explicit, dated pre-election prior that considers current polls
and historical errors, with a separate historical-only sensitivity run. Do not
reuse the earlier narrative race ranking as a calibrated probability prior.
Keep poll error, turnout error, candidate effects, reporting-order error, and
source-quality uncertainty distinguishable. Choose priors and variance values
through backtesting, not arbitrary confidence constants.

For each simulation, draw remaining turnout and shares with these correlated
effects, add simulated remaining candidate votes to fixed observed candidate
votes, and determine the plurality winner. A two-party simplification is
acceptable only when third-party victory is negligible; otherwise model all
candidates. Report Monte Carlo error and version the random seed/model.

```text
P(D win) = simulations with D plurality / valid simulations
projected D-minus-R margin = final simulated (D-R) / (D+R)
```

Publish a central estimate, an uncertainty interval, and win probability only
after calibration checks pass. Until then show scenarios and “probability not
yet calibrated.” Do not turn a plausible projected margin into a precise win
probability through an untested conversion.

## Live break-even arithmetic

Let `L` be the current statewide counted D-minus-R vote lead, `U_c` expected
remaining major-party votes in county `c`, and `q_c` their D share.

```text
projected final lead = L + sum_c U_c * (2*q_c - 1)
U = sum_c U_c
required D share of all remaining votes = (1 - L/U) / 2

conditional required D share in selected county c =
  (U_c - L - sum_{j != c} U_j*(2*q_j - 1)) / (2*U_c)
```

These are conditional tie thresholds, not probabilities. Apply only for
positive denominators; when no major-party votes remain, use the observed
lead and any unresolved correction/canvass uncertainty. Show requirements
under low/base/high outstanding-vote estimates. Report the selected county's
required share relative to the **comparable baseline for its remaining units**,
not automatically the baseline countywide share. Preserve uncertainty about
which units remain when that information is missing.

## Output and operator workflow

### Needle page and individual APIs

Render needles exclusively on the dedicated `/needle` page, with one needle
per race, keyed by the existing stable race/target ID, plus exactly two chamber
needles: Democratic versus Republican House control and Senate control.
Other site views may
link to `/needle` but must not embed needles. House group watch items and
supporting county/city observations provide inputs or context, not additional
needles for the same race. Each race's needle must show an explicit unavailable
or uncalibrated state when its data or model does not meet the forecast gates.

Provide a public JSON representation of each needle individually at
`GET /api/needle/:raceId` (for example, `/api/needle/senate-mi`). The `/needle`
page must consume these same per-race representations so the UI and API agree.
Each response identifies the race and includes its status, observed counts,
remaining-vote estimate and uncertainty, projected margin and interval, win
probability when calibrated, source provenance/freshness, forecast timestamp,
and model version. Return unavailable forecast fields as null with a reason;
do not manufacture probabilities for unsupported races. Unknown race IDs
return HTTP 404. Reads use persisted data and must not trigger source fetches.

The API representation must be independently fetchable without loading the
page or requesting every race. An aggregate endpoint, if added later, does
not replace the individual needle endpoints.

Each chamber needle also has its own public JSON endpoint:
`GET /api/needle/house-control` and `GET /api/needle/senate-control`.
Reserve these IDs separately from race IDs. Include Democratic and Republican
control probabilities, any unresolved/other-control probability, the seat-count
distribution and interval, majority/tie rules, fixed-seat baseline, contributing
race IDs and forecast versions, coverage gaps, assumptions, and the shared
forecast timestamp/model version. The page consumes these same representations;
the unavailable-state and persisted-read requirements apply to them too.

### Chamber-control probability calculation

Calculate control from the probability distribution of final caucus seats,
not an average of race probabilities or current leads. Build a complete seat
ledger for the incoming Congress: all House voting seats and all Senate seats,
including seats not up for election. Every election that can affect control
must have an outcome distribution, an explicit sourced fixed outcome, or a
visible missing-input state. The desk's currently watched races alone are not
the complete chamber electorate. Add forecasts or explicit, versioned baseline
assumptions for other relevant races; do not silently treat untracked seats as
safe or assign current incumbents as winners. Governors, supporting local
views, and House group watch items must not add seats. Map regular/special
elections to the seat and term being forecast so no seat is counted twice.

Use 218 of 435 voting House seats as the full-chamber majority benchmark
([House membership](https://www.house.gov/the-house-explained)). For a full
100-seat Senate, use 51 caucus seats, or 50 for the caucus with the incoming
vice president's tie-breaking support; record that dated assumption explicitly
([Senate tie-breaking role](https://www.senate.gov/about/officers-staff.htm)).
Record independent candidates' caucus assumptions separately from ballot party.
Handle vacancies, unresolved caucus affiliations, runoffs, and delayed outcomes
explicitly. Define the forecast's seating horizon; keep a full-seat election
majority distinct from temporary membership or a specific leadership vote.

For a binary Democratic/Republican model with `B_D` fixed Democratic caucus
seats, uncertain race indicators `X_i`, and threshold `K_D`, standard probability
math gives:

```text
S_D = B_D + sum_i X_i
P(D control) = P(S_D >= K_D)

If races are independent and P(X_i = 1) = p_i:
f_0(0) = 1; f_0(k != 0) = 0
f_i(k) = (1 - p_i) * f_{i-1}(k) + p_i * f_{i-1}(k-1)
P(D control) = sum_{k: B_D + k >= K_D} f_n(k)
```

This Poisson-binomial recurrence provides an exact independent-race reference
calculation. Marginal race probabilities alone do not specify a correlated
chamber distribution. The production calculation should use the shared
statewide/regional/national effects in the joint race simulations: count final
caucus seats and evaluate each party's control rule in each draw, then divide
each control outcome's draw count by the number of valid draws. A conditional
independence model may instead convolve conditional probabilities per shared
effect draw and average the resulting distributions. Label the independent
reference's assumption; do not present it as accounting for shared errors.

Compute Republican control under its own rule. Use `1 - P(D control)` only
when Democratic and Republican control are mutually exclusive and exhaustive;
otherwise retain unresolved/other-control mass. Include independent winners
and uncertain caucus choices in joint draws when relevant. Both chamber needles
must use a coherent set of race forecasts from the same model run and report
simulation error where applicable. Missing inputs produce an explicit
unavailable state or clearly labeled conditional scenarios, not a complete
unconditional probability. Apply the same calibration gates as race needles.

The `/needle` page should show, within each race's entry or its details:

- Counted vote totals and lead, estimated outstanding votes and uncertainty,
  forecast timestamp, source freshness, and the distinction between observed
  results and forecasts.
- A county table with historical margin, live comparable-unit swing, target
  margin, estimated final turnout, projected net-vote contribution, remaining
  net-vote opportunity, and conditional break-even requirement.
- County/precinct maps using versioned geometry, plus unknown/unmatched-unit
  overlays. Highlight counties driving uncertainty as well as those with the
  most votes. Keep unavailable detail visibly unavailable.
- Scenario controls for turnout composition and county performance, with
  explicit assumptions and the statewide arithmetic updated together.
- A timeline of model changes and source revisions; stale-feed warnings;
  separate official certification and any outside race-call attribution.

Before polls close, verify ballot candidate IDs, official contest URLs,
boundary/crosswalk versions, poll-closing timezones, expected ballot categories,
and source failover paths. Keep Michigan's different local timezones explicit
where relevant, rather than assuming all counties close simultaneously.

## Validation and delivery phases

### Michigan research snapshot, 2026-10-17

The [Michigan research index](senate/2026/michigan/README.md) links all four
completed assignments and the [integration review](senate/2026/michigan/research-review.md).
The 23-county priority set covers 80.4162% of 2024 Senate contest votes; map
assets cover those counties in both selected vintages. County baselines and
eight target scenarios reconcile. The 2024 Senate repeat-performance scenario
already elects the Democrat; a uniform -0.175774 pp D-share shift ties it.
Official live adapter testing, original county-export validation, outstanding
vote estimates, precinct/board crosswalks, geometry review, and probability
calibration remain implementation gates. Research collection is complete with
those gaps documented; a live needle has not been implemented.

### Implementation sequence

The immediate desk-wide prerequisite is the remaining-vote milestone above:
inventory and pin sources for all 74 tracked results, collect independent
completion observations, persist full-night history, and validate geographic
coverage. Acceptance requires fixtures for positive returns, zero setup,
missing/invalid percentages, rounded/capped completion, stale and disagreeing
sources, changed election identities, downward corrections, split counties,
and overlapping county/municipal rows. Validate useful post-close observations
for each target or report an explicit gap; setup-field availability is not a
passing end-to-end coverage check. Surface estimates and unknowns without
changing race calls or enabling uncalibrated probabilities.

Needle delivery also requires `/needle` to render exactly one entry per race
plus the House-control and Senate-control needles, with no needle embeds on
other pages, and an independently readable individual API for every race and
both chambers. Verify page/API agreement,
explicit unavailable states, unknown-ID 404 responses, and that API reads do
not contact publishers.

Validate chamber math against enumerated small examples and the independent
recurrence, including 0/1 race probabilities, already secured/impossible
majorities, Senate ties with either vice-presidential caucus, independent
caucusing, missing races, and duplicate regular/special seats. Check seat-mass
and probability normalization, group/local exclusion, agreement between race
marginals and joint draws, and a correlated-race example where control odds
differ from the independent calculation.

The [Michigan live polling strategy](senate/2026/michigan/live-polling-strategy.md)
specifies starting collection intervals, vendor adapters, versioned snapshots,
manual fallback, source health, and the first collector/replay milestone. It
also records a 2026-10-17 zero-vote probe of Genesee's actual November 2026 feed.

1. **Research now:** collect the four Michigan reports, all-county baseline
   tables, official source inventory, and actual map assets. Review conflicts
   together, link everything from Michigan's README, and commit to main.
2. **Deterministic calculator:** implement the all-county turnout/swing and live
   break-even arithmetic with reconciliation to certified totals and scenario
   sensitivity tables. Verify the factor of two between share and margin.
3. **Source adapters:** replay saved official snapshots, handling cumulative
   updates, duplicates, corrections, incomplete reporting units, and outages.
4. **Calibrated forecast:** replay genuine historical timestamped returns from
   several comparable elections if available. Use final certified outcomes
   only as evaluation targets, never as information available at an earlier
   timestamp. Synthetic reporting orders can stress-test logic but cannot
   establish historical calibration. Hold out entire elections/regions;
   measure probability calibration, interval coverage, Brier/log scores,
   turnout error, and bias by geography/voting method and time of night.
5. **Dress rehearsal:** run a shadow forecast and require human review of data
   freshness and anomalies. Include tests for zero returns, all returns,
   out-of-range targets, missing counties, a late large absentee batch,
   changed precincts, a correction reversing the lead, and source disagreement.

If genuine historical snapshots or remaining-vote evidence are unavailable,
deliver the deterministic scenario tool and keep probabilities experimental.
This task authorizes the plan and research, not deployment of an unvalidated
election-night model.

# Election-night likelihood and county break-even plan

Created: 2026-10-17. First research pilot: [Michigan](senate/2026/michigan/README.md).

## Objective and scope

Estimate the probability of a Democratic Senate win as official results arrive,
using the geography and voting method of counted and outstanding votes. Show
which counties are above or below a stated winning scenario and how much the
Democrat must improve on a historical baseline to win statewide. This is a
research and implementation plan, not a functioning forecast or an election
call. Research artifacts and unresolved gaps must remain visible.

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

The election-night view should show:

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

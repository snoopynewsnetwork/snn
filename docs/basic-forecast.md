# Basic vote-mix model

`basic-vote-mix-v2` is an automatic, **experimental, uncalibrated** model using
only the site's existing feeds and seat ledger. It produces predictions now;
it is not the historically validated forecast described in the longer research
plan. It requires no vendor credentials, paid data, new publisher requests, or
manual forecast uploads.

## Inputs and lifecycle

The existing CNN Senate/House list responses already contain all 470
congressional election records. The ledger parser now retains their candidate
votes and expected-vote percentages alongside declarations. The three watched
governors use existing independent completion observations. Official display
counts remain separate; the model never divides official counts by CNN's
percentage. Unknown independents' caucuses remain other/unresolved.

The first needle read initializes and saves a prior run from persisted inputs.
Every completed collection cycle then publishes a new run from saved source
observations, using the existing minute cron and public refresh. Ordinary reads
reuse the saved run and never contact publishers. Runs and their input metadata
survive restarts. An editor-published run takes precedence; automatic generation
never overwrites it, even if that imported run later becomes stale.

The page continues to show the 72 tracked races plus two chamber needles.
`GET /api/needle?scope=all` discovers all 473 modeled races and both chambers;
every modeled race has its own `/api/needle/:raceId` endpoint. All 470 election
forecasts enter chamber arithmetic, together with the 65 Senate holdovers.

## The calculation

For each race, construct neutral candidate shares `b_i`: Democratic and
Republican party groups receive equal weight, divided among their listed
candidates. Other candidates collectively receive weight 0.05 relative to
each major party's weight of 1. If one major party is absent, listed
independents form an equally weighted opponent group; this does not assign
them to a caucus. If no major group exists, the listed candidates are equal.

A source is usable only when candidate counts plus explicitly unallocated
votes reconcile exactly to its published total, its contest/ballot/embargo validation passes, its expected-vote
percentage is in `(0,100]`, and both extraction and collection are within
15 minutes. Candidate sums exceeding the published total are rejected.
Failure or a missing completion estimate
uses the neutral prior, regardless of the current lead. Prior-only races are
visible in the UI and counted separately in each chamber API.

For usable returns, let `v_i` be counted candidate votes, `A = sum(v_i)`,
`U = published total - A`, `V = A + U`, and
`p` be the supplier's fraction counted. Define:

```text
c = min(p, 0.99)
q_i = (v_i + 20*b_i) / (A + 20)

For each joint simulation j:
  N_j is one shared standard-normal shock across every race
  E_ij is independent standard-normal candidate noise
  loading_i = +0.5 for Democrats, -0.5 for Republicans, 0 otherwise
  w_ij = q_i * exp(E_ij + loading_i * 0.35*N_j)
  remaining_share_ij = w_ij / sum_i(w_ij)
  final_share_ij = c*(v_i/V) + (1-c)*remaining_share_ij
```

This fixes the counted votes conditional on the assumed final turnout `V/c`
and simulates only the remaining vote mix. A displayed 100% is capped at 99%
rather than interpreted as certification. For prior-only races use `c=0` and
`q_i=b_i`. No turnout count or margin interval is invented for these races.

The final plurality winner determines each simulation's D/R/other caucus
outcome. Unallocated counted votes contribute an unknown final share `c*U/V`;
no party or candidate is assigned these votes. If that share could change the
winner, the draw is other/unresolved. Margin intervals expand by its worst-case
D/R allocation. This handles omitted write-ins without inventing their party.
A sourced declaration replaces simulation with its fixed outcome. Governors
honor CNN's explicit candidate `winner` flag once call/vote embargoes have lifted;
a fresh snapshot with no winner clears that projection. Supplier projections
remain separate from official winner fields and do not require a completion
percentage. A lead alone never creates a call;
the 65 Senate holdovers are added by the ledger. The same national shock is
shared across House and Senate, so chamber calculations preserve this simple
dependence rather than assuming all races are independent. No state or regional
factor is included.

The model uses 256 reproducible joint draws. Fixed per-race random streams
keep unchanged inputs stable across refreshes. Normal shocks use 1,024
midpoint quantiles of the standard normal distribution, stored in
`src/data/normal-quantiles.json`; the table is reproducible with Python's
`statistics.NormalDist().inv_cdf((i+0.5)/1024)`, rounded to six decimals.
Simulation standard error is reported separately; near 50% it is about three
percentage points with 256 draws. This is sampling precision, not calibration.

## Limits and presentation

The 20-vote shrinkage, log-score uncertainty of 1, national log-odds shock of
0.35, 99% completion cap, and third-party prior are explicit heuristic choices,
not fitted constants. The model assumes remaining voters resemble counted
voters on average. It has no geographic or voting-method adjustment, polling,
incumbency, district history, turnout-error distribution, ranked-choice
transfers, or runoff model. Races with only neutral priors can dominate chamber
odds. A large lead can reach 100% of simulated outcomes; that is conditional
model arithmetic, not a source race call or a guarantee about corrections.

API responses carry `releaseStatus: "experimental"`, `status: "experimental"`
when usable, a null `calibrationUrl`, assumptions, and per-race `modelInput`
provenance/basis (`live`, `prior`, or `declared`). Chamber responses include
counts of each input basis. Probability fields use the same schema as imported
runs; the page uses a plain "Win probability" label and keeps model limitations
in the assumptions details. A decorative pointer jitter stays within 0.65
degrees of the model angle, uses staggered timings, and never changes displayed
odds or API data. Reduced-motion preferences disable this animation.
Stale runs and source/model conflicts still suppress predictions. The model
does not change official winner fields or the desk's margin-band signals.

Tests verify full seat coverage, repeatability, fixed counted votes, corrections,
completion-dependent uncertainty, neutral fallback, explicit declarations,
unknown independent caucusing, automatic collection-to-prediction publication,
manual-run precedence, and network-free reads. These establish implementation
behavior, not forecast accuracy. Historical validation remains future work.

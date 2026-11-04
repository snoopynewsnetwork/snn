# Obtaining forecast inputs for the needles

Research date: **2026-11-03**. This is an acquisition and implementation plan,
not a forecast or evidence that a provider's forecast has passed our validation.

Implementation update: the [basic vote-mix model](basic-forecast.md) now supplies
automatic experimental predictions from existing data and explicit neutral
priors. This acquisition plan describes replacing that baseline with supported
or historically validated forecasts; it is no longer a prerequisite to rendering
experimental predictions.

## Recommendation

Use a supported **live forecast provider** if the goal is operational needles
for this election. Decision Desk HQ is the first candidate to evaluate: it
describes both a pre-election Forecast and election-night Election Pulse, with
client API documentation. Pulse updates from reported votes and outstanding
ballot characteristics. Exact race coverage, entitlement, pricing, public
redistribution rights, and access to joint simulations still require a sample
and agreement; none was established by this research. No inquiry or purchase
has been made. [DDHQ product description](https://www.decisiondeskhq.com/faq).

In parallel, preserve our live observations and build a transparent model as a
separate project. A model trained, replayed, and reviewed from scratch should
not be represented as calibrated merely because its arithmetic works. If no
supported forecast can be obtained, ship remaining-vote scenarios while the
model is evaluated; keep live win probabilities unavailable.

## What is already available, and what it cannot supply

The branch collects selected official/CNN counts and independent CNN completion
observations for 74 targets. Those are **reported votes and estimated vote
completion**, not a distribution for the partisan composition of outstanding
votes. The separate chamber-ledger work identifies every seat, including
holdovers and unresolved elections. An unresolved ledger entry still needs a
forecast or a sourced declaration before it can contribute to control odds.

Cover all **435 House elections, 35 Senate elections, and the three tracked
governor elections**, not just the desk's 72 full races. Governors do not enter
chamber arithmetic. The 65 Senate holdovers come from the ledger. Actual
declared outcomes may replace uncertain forecasts; “safe” ratings and incumbent
names cannot silently become certain wins.

| Input route | What we can obtain | Decision/gap |
| --- | --- | --- |
| DDHQ Forecast / Election Pulse | A supported candidate source of pre-election and live race probabilities | Obtain sample schema, all-race coverage, forecast timestamps, calibration evidence, and joint-draw/dependence availability before choosing it. Public documentation is not an API entitlement. |
| AP Elections API plus our model | Results, `eevp`, and some voting-method completion fields | These improve observation/turnout inputs; they do not themselves constitute a win-probability feed. Confirm per-race/method availability, pricing, storage and display rights. [AP fields](https://developer.ap.org/ap-elections-api/docs/Elections_Response_Data_Elements.htm). |
| Existing public CNN feeds plus our model | Counts and expected-vote percentages; geographic endpoints for further inspection | No documented forecast probability or joint simulation contract has been verified. Audit geographic scope and service limits before expanding collection. |
| Public forecast CSV benchmark | One inspected publisher offers Senate/House marginal probabilities and margins | Useful as a comparison/prior candidate, not an approved live model. Its methodology says House forecasts are not backtested, some safe House seats are fixed, and independents receive a Democratic control assumption. No joint export or election-night posterior was verified. [Publisher methodology/download links](https://midtermforecast.com/methodology/). |

Cook's ratings measure competitiveness and advertise separate API/licensing
access. Do not assign arbitrary probabilities to “Lean,” “Likely,” or “Solid.”
[Cook ratings definition](https://www.cookpolitical.com/ratings/house-race-ratings).
Prediction-market prices are another signal, with contract-resolution rules,
liquidity and participant effects; they are not automatically calibrated race
probabilities or joint chamber outcomes. If used, record the market's role and
test it separately rather than relabeling prices as our model output. DDHQ's
[2026 methodology](https://votes-docs.decisiondeskhq.com/forecast-methodology/2026-congressional-forecast-methodology)
describes market blending and a shared-factor chamber simulation; that does
not establish that its commercial API exports those simulations.

## First implementation milestone: provider sample to reproducible run

1. Produce a coverage matrix keyed to the chamber ledger and three governor
   race IDs. Record candidate IDs, ballot party, caucus mapping, regular/special
   seat/term, ranked-choice/runoff status, source timestamps and coverage gaps.
2. Evaluate an authorized DDHQ sample against a concrete request: all relevant
   race probabilities and projected-margin distributions; live versus prior
   status; completed race declarations; common model-run ID; joint outcome or
   margin draws with consistent draw IDs; calibration/backtest artifacts;
   update cadence, outage behavior, historical snapshots and public API/display
   rights. If joint draws are unavailable, ask for dependence parameters or
   supported chamber distributions. Do not reverse-engineer a display widget
   into an assumed redistribution license.
3. Build a server-side provider adapter and immutable raw archive. Keep provider
   identity, original forecast time, retrieval time, model version and input
   snapshot IDs distinct. Source failures retain observations with stale flags;
   reading a needle must not fetch the provider. Compare imported race
   marginals and seat distributions with the provider's own published values.
4. Translate only a coherent, accepted run into `ForecastRun`. Every outcome
   column must refer to the same simulated election across races. If only
   marginal probabilities are supplied, do **not** independently sample each
   race and label the result a calibrated joint forecast. Show individual
   provider probabilities through an explicitly attributed marginal schema,
   and keep chamber odds unavailable until their dependence model is supplied
   or fitted and validated. A provider's chamber probability may be displayed
   separately as attributed output, not described as our calculation.
5. Extend the contract before enabling production: add provider/input provenance,
   prior timestamp, calibration scope (pre-election or live), dependence-model
   ID and release status. Require reviewed artifacts, not just a syntactically
   valid `calibrationUrl`. The current publisher endpoint checks format and
   consistency; it does not establish calibration. Respect the 8 MB/10,000-draw
   limits: 10,000 outcome characters for 473 races fit approximately 4.73 MB
   before metadata, but full margin arrays may not. Use a smaller common draw
   set, a larger audited storage contract, or separately versioned summaries.
6. Run shadow imports, verify source/API/page agreement and missing-race behavior,
   then enable one race followed by full chamber runs. Existing freshness rules
   expire forecasts after 15 minutes; preserve the provider's actual as-of time.
   Republishing an old pre-election CSV with a new timestamp is not a live update.

The first gate is **sample and rights availability**, not an assumed delivery
date. No provider access or public price has been verified. Once a usable
sample exists, the adapter and contract work above is an engineering milestone;
no additional statistical model is required if we redistribute an accepted
provider's coherent forecasts under its terms.

## Independent model track: inputs to collect

| Artifact | Acquisition and acceptance |
| --- | --- |
| Frozen race priors | Collect original pollster releases/toplines and field/publication dates, sample/population, sponsor and methodology; combine with map-aligned past votes, incumbency and national environment. Poll-poor races need an explicit fundamentals prior with broad uncertainty. Freeze the election-eve prior to avoid counting live information twice. |
| Historical votes | Start from certified state/county files and the [MIT Election Lab catalog](https://electionlab.mit.edu/data), which provides House district returns through 2024 and 2022/2024 precinct datasets. Record dataset versions and reconcile totals. Final returns are training/evaluation targets, not election-night observations. |
| Current district crosswalks | Pin the actual November 2026 map in each state using official state plans, then crosswalk historical precinct/block votes. [Census 120th Congress products](https://www.census.gov/programs-surveys/decennial-census/about/rdo/congressional-districts.120th_Congress.html) are a starting layer, not sufficient proof a map remained operative after later changes. [Florida's 2026 files](https://www.edr.state.fl.us/Content/redistricting/2026redistricting/index.cfm) and [Texas precinct/district joins](https://data.capitol.texas.gov/dataset/precincts) are concrete state sources. Never join 2024 and 2026 solely by district number. |
| Live comparable slices | Extend ingestion to contest × county/municipality × voting method when supported, with source-native units and overlaps tracked. Preserve candidate counts, timestamps, totals and corrections. Do not mix county totals with constituent cities, or allocate an entire split county to one House race. |
| Outstanding vote | Combine same-snapshot completion estimates with official outstanding-ballot reports and historical reporting patterns. Keep ballot inventories, eligible ballots and contest votes separate; model turnout uncertainty and missing method composition. Polling-place completion alone is insufficient. |
| Genuine replay corpus | Obtain timestamped returns and the remaining-vote estimates available at each timestamp for multiple previous elections. Verify raw corrections and historical map versions. Current-night collection helps future evaluation but cannot validate this election before its outcome exists. |

For live updating, keep reported votes fixed; simulate remaining votes and
their partisan composition using comparable geographic/method slices. Pool
sparse areas and retain national, state/regional, race and method errors, with
third-party, runoff and ranked-choice treatment. Preserve these shared effects
when exporting joint outcomes. This is a proposed modeling approach, not a
claim of calibration. The DDHQ-authored [correlated simulation paper](https://hdsr.mitpress.mit.edu/pub/ftwzgrij/release/4)
provides a concrete national/regional factor reference; its [live modeling
paper](https://hdsr.mitpress.mit.edu/pub/zr6hjsfl/release/1) explains why partially
reported geographic units cannot be treated as random vote samples. Its
primary-election heuristics should not be copied wholesale into this model.

If a chosen provider supplies only marginal probabilities, a concrete fallback
is our own fitted Gaussian factor coupling. For each race, set
`mu_i = inverseNormalCDF(p_i)` and sample
`Z_i = mu_i + a_i*N + b_i*region_i + sqrt(1-a_i^2-b_i^2)*error_i`, with independent
standard-normal factors, shared `N`/regional factors across races, and bounded
loadings. A Democratic win occurs when `Z_i > 0`; the unit total variance
preserves the supplied marginal `p_i` while adding a specified dependence
structure. Fit/load-test a small pooled loading model using genuine archived
forecast snapshots and subsequent outcomes/residuals, with complete election
holdouts. Version it separately from the provider's model, and test chamber
tails as well as race marginals. Without the provider's historical snapshots
or adequate calibration evidence, this is only a dependence sensitivity
scenario, not an approved chamber forecast. Zero loadings give an independent
reference, not a supported correlated forecast. This fallback is a proposed
implementation, not evidence the required historical inputs already exist.

### Replay data has an important trap

DDHQ documents a race vote-history endpoint with cumulative counts and vote
drops, but says downward corrections are applied to earlier values, running
totals never decrease, and its usual window ends 48 hours after poll close
(California excepted). A response fetched later can therefore differ from
what was known then. Confirm an **immutable as-observed archive** or explicitly
model the limitation; do not backtest against revised history as if it were
the original tape. [Exact endpoint contract](https://docs.decisiondeskhq.com/reference/get_api-v4-vote-history-races-race-id).
AP advertises [historical election data](https://www.ap.org/content/formats/data/),
but timestamped revision history, granularity and entitlement still need
verification. MEDSL's [reporting research](https://electionlab.mit.edu/research/election-return-reporting)
is useful context; a paper using time series is not proof its underlying
licensed feed is freely downloadable. If no genuine replay corpus is available,
synthetic reporting orders may test software but cannot validate live odds.

## Validation and release order

1. Freeze data manifests, source artifacts and forecast cutoffs. Fit priors and
   shared errors on earlier cycles; hold out complete later elections and
   regions. Do not tune a variance on the test cycle and report it as held out.
2. Publish race reliability bins, Brier/log scores and margin-interval coverage,
   stratified by race type, reporting fraction and voting-method availability.
   Report sample sizes and uncertainty; many precinct updates from one election
   are not independent calibration trials. Evaluate against a frozen prior and
   a simple historical baseline, including undercoverage and overconfidence.
3. Test chamber seat distributions and control calibration using the same joint
   draws as race needles. Include shared polling misses, unpolled districts,
   corrections, late mail, redrawn geography, stale feeds and missing races.
   Monte Carlo standard error is not evidence that the model is calibrated.
4. Release in order: source coverage and deterministic break-even scenarios;
   accepted pre-election priors labeled as such; shadow live posteriors;
   reviewed live race probabilities; complete chamber runs. Keep a visible
   experimental status until the relevant validation gate is passed.

**Next concrete action:** make the all-race input coverage matrix and evaluate
an authorized DDHQ Forecast/Pulse sample against the six-step contract above.
If access cannot be obtained, implement the replay/baseline manifests and a
Michigan shadow model first. Do not unblock every needle with invented priors,
arbitrary error constants, a ratings-to-probability lookup or synthetic “joint”
draws from unrelated marginal forecasts.

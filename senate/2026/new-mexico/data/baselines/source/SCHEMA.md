# New Mexico baseline source and calculation schema

Version `nm-baselines-1`, original-first pin 2026-10-20. All paths are relative to
`senate/2026/new-mexico/` unless otherwise stated. These are qualified historical
observations and conditional arithmetic, not a current live forecast.

## Ownership and reproduction

Owned outputs are `county-partisanship.md`, `data/county-baselines.csv`, and every
file under `data/baselines/`. All shared source assets, turnout outputs, coordinator
preparation and other reports are read-only. No Git operation or agent delegation
is part of reproduction. The turnout agent was finished at actual baseline launch.

Run `PYTHONDONTWRITEBYTECODE=1 python3 data/baselines/run_offline.py` from the state
directory, or use the repository-relative command in the report. It verifies
original hashes, independently re-extracts original CSV/HTML/PDF sources, rebuilds
controls/scenarios/report, compares the captured peer core, validates, seals assets
and audits that seal. Python3 stdlib, requests (acquisition imports), and Poppler
`pdftotext` are required; no dependency/cache directory is retained. PDF preview
images were rendered with Poppler and visually inspected. Do not regenerate the
original pin with changed extraction bytes; preserve the old pin and disclose a
new version when inputs or extraction semantics change.

`source/acquire.py` without arguments is OFFLINE verification. `--fetch` makes new
public observations from the preserved literal URLs without replacing the pinned
historical inputs. It preserves full redirect response bodies, HTTP status/headers,
request/final URL, UTC retrieval, raw/stored hash/size and lossless gzip. Repeated
`--fetch` is a new observation; later calls archive the prior receipt by SHA256
under `source/fresh-history/` before replacement. The task's
first exploratory network call failed DNS in sandbox; an authorized escalated
download succeeded. A later bounded supplemental fetch replaced the first
supplemental receipt; superseded body entities remain inventoried, but their
individual HTTP headers/retrieval clocks are unavailable. This disclosed receipt
gap concerns supplemental HTML state variants, never the pinned historical
sources or final fresh observation receipts. Entity filesystem mtimes are not
represented as retrieval clocks.

Initial parser-only failures before the original pin: a codec alias typo and the
nested candidate-receipt shape; corrected without changing originals. After the
pin, independent PDF registration extraction required source-aligned numeric
column, county-total and wrapped-label parsing repairs. The peer comparison found
a tied-order convention difference (178 positions) and those registration parsing
errors; all initial source objects remain pinned. No source votes were changed.

## Provenance layers

| Artifact | Meaning |
|---|---|
| `source/original-references.json` | Frozen 75 original-only receipt objects, including parent/discovery chains and individual shared source body references. This is not a dependency on a mutable producer extraction. `asset` points to the exact original gzip; both hashes and both sizes must match. |
| `source/fresh-observations.json` | Own new October20 observations; redirect hops are individual records. Final 200 CSV matches the pinned Senate CSV. Otero final-notice attempt is404/empty, not a recovered document. |
| `source/independent-first-pin.json` | Paths/bytes/SHA256 of independent extraction saved before reading peer derivatives; pin hash `6770ae96313d9f9d2e0964da2470fd903d1f72122e260eece7635370aca014b7`. |
| `original-extract.json` | Every state/county/precinct source row for all four required contests. Original header/party rows, source ID/hash, raw row, complete cell objects, county context, literal identity and administrative flag. |
| `source/*-page-data.json` | Complete embedded `__NEXT_DATA__` payload, including candidate-in-contest ID, person ID, pseudocandidate ID, parties, `nVotes`, `nVotesParty1`, winner/write-in/mask flags, event/office/division IDs, source clocks and file objects. No key deduplication. |
| `legacy-original-rows.json` | Every original row/field for three legacy CSVs, including unrelated offices and trailing empty cells. 2024 header-only remains unavailable. |
| `source/*.txt` | Whole original PDF text extracted with `pdftotext -layout`, including unrelated offices/reference tables; full original bytes remain available by exact receipt reference. |
| `source/turnout-*-div-objects.json.gz` | Complete parsed div/span objects with HTML attributes, source line/column, parent/child indices and text; no truncation. Original HTML is authoritative. |
| `source/*-tables.json` | HTML rows/cells/attributes/source positions, links and inputs. All24general roster header cells and visible/hidden values are retained. Source header `Confidential Public Official` is a source column, not a confidentiality judgment here. |
| `source/peer-freeze/*` | Losslessly compressed exact stable finished turnout core, captured after our original pin. `capture.json` and `sensitivity.capture.json` give raw/stored hashes/bytes and capture UTC; no future-final equality claim. |

Published primary chain: SOS election archive HTML → its literal legacy app links;
SOS archive `rf-table` attributes → linked RealFile JS/public SDK configuration →
GetWidgetFiles literal `sourceURL` → full PublicFiles PDFs. Original receipts retain
failed fallback/widget and document799403 routes too; a recovered archive PDF is
not claimed identical to799. Native CSV chain: SOS-linked ElectionStats contest
page → literal ResultsCSV href →307redirect →200CSV. The source receipts retain
requested/final routes; no current November contest endpoint is guessed.

Every stored artifact is strictly below40,000,000 bytes. Shared originals are
referenced by exact content hashes rather than duplicated. Gzip decompression is
the complete ordered-byte reconstruction; nothing is truncated or simplified.
There are no split artifacts or hidden dependencies.

## Geography and source cells

Native cell objects use one-based `source_row` and `column`. The first two CSV
columns are scope and literal label; candidate/control fields follow. `literal`
retains the exact string, `value` is an integer only when directly printed as
digits, `masked` is true only for `*`. Empty and `*` become null numeric values;
neither becomes zero. `raw_row` plus the header/party rows reproduces parsed
content; full original bytes preserve exact delimiters/newlines/encoding.

`State`, `County`, `Precinct` are source scopes, not disjoint addends. The county
context is carried only within its actual source block. `Voter Privacy` is marked
administrative while preserving its source `Precinct` scope. `native_id` stays
null because the CSV does not publish a numeric ID. The literal label may be a
number, split label or administrative aggregate; no physical precinct/polling
site/vote-center/VTD/municipal-parent equivalence follows. Native county IDs in
legacy HTML/service, ElectionStats person/contest IDs and Census county FIPS are
separate namespaces. County-only Census `Doña Ana`→results `Dona Ana` is the sole
declared name alias. Source strings never change. No cross-year/current precinct
join or geometry is approved.

`candidate-fields.csv` is a long form of all50,179 candidate/control positions:
contest, scope, county, native literal, administrative flag, source row/column,
field label/party/literal/value/mask and source ID. All8558native rows survive
in `native-baselines.csv`. `raw_fields_json` retains every original row field.
Blank/under/over/generic or named valid-write-in controls, native vote methods,
registration and central group identity are unavailable unless an explicit
separate primary publication supplies them; this package never invents them.

Printed `Total Votes Cast`/`Total Ballots Cast` fields are independent lanes.
They can omit protected candidate cells, and the latter matches named-candidate
scope at state/county level rather than whole ballots. `all_candidate_votes`
means the sum of ALL published candidate cells when every cell is numeric;
otherwise null, even when a printed total is0. No residual is allocated. Source
`nVotesParty1` is distinct from `nVotes`; both stay in complete metadata.

## Numerical baseline and scenario tables

`data/county-baselines.csv` has132rows =33counties×4contests. Every row has source
position/ID, FIPS, explicit A/B labels/parties/votes, named other sum, all-candidate
sum, printed total lanes, pair sum/participation/share/margins, source-state
weights, net votes, gain per A-share point, historical winner and closeness band.
`state-baselines.csv` gives corresponding state counts. These tables retain raw
integer observations; scenario rows can be fractional.

| Field family | Definition |
|---|---|
| `pair_votes`, `pair_volume` | A+B historical votes or explicitly modeled pair participation, never all ballots. |
| `A_pair_share` / `baseline_A_pair_share` | A/(A+B), fraction [0,1]; null if pair unavailable or zero. |
| `pair_participation` | (A+B)/all named candidate votes in that county's preference anchor. |
| `pair_margin_pp` |100(A−B)/(A+B), distinct from100(A−B)/all-candidate votes. |
| `pair_weight_state` | Directly printed native/county A+B divided by complete published state A+B. Native weights need not sum1; unknown source values remain missing. |
| `all_candidate_weight_state` | Complete directly printed candidate sum / complete published state candidate total; null if any candidate is masked. |
| `gain_net_per_A_share_pp` |0.02×pair volume: +1share point transfers votes B→A and adds2pair margin points. |
| `net_A_minus_B` / `target_net` | Vote units, separate from share/margin points. |

`settings.json` is the implementation's declared volume/preference contract.
Each low/base/high/context county V_c is the actual all-candidate county volume
of2022governor/2024Senate/2024president/2020Senate, respectively. Four independent
preference anchors supply s_c and p_c. T_c=V_c×p_c; named other candidates keep
their own anchor all-candidate shares. These are historical sensitivities, never
2026 projections. All33counties enter all32state target cases and1056county rows.

For target fractional pair margin g (0 or0.01),
`T=ΣT_c`, `M=ΣT_c(2s_c−1)`, unbounded `δ=(g−M/T)/2`.
The code solves `ΣT_c(2clip(s_c+δ)−1)=gT` with bounded shares. It retains both
unbounded and solved shifts, clipped unit count, target net, gains, full named
other votes and plurality leaders. `A+1` means1pair-margin point, not one vote;
its unbounded A-share shift adds0.5points to the tie shift. A+1all-candidate margin
would use0.01Vnet instead, and is not silently substituted. Already-winning
baselines can have negative required shifts. Targets outside feasible range,
unknown pools and zero/negative pools have explicit statuses.

`county-target-scenarios.csv` contains every county contribution/weight/gain,
pair participation, target share/margin/net, actual change and selected-only
unbounded/feasible share/status. Every other county's assumed share shift is0.
The CLI can explicitly alter this assumption. Selected boundary:
`q_c=(T_c+gT−M_others)/(2T_c)`; q<0 already secured, q>1impossible.

`native-targets.csv` contains every native row for both targets. The directly
known positive A+B universe has its own exact clipped solution/weights/net
contributions in `native-state-scenarios.json`; masked pair rows remain unknown,
zero rows have no positive pool. Whole-state all-native uniform target shares
stay null. For a known selected native row only, the published statewide
historical net minus that directly observed row is the aggregate fixed-rest
assumption. This does not assign protected cells. Unknown selected values stay
null. Cross-year native volume mixes/preferences are unmodeled without a
verified crosswalk; county scenarios do not substitute for native models.

## Orders, controls and peer comparison

`priority-contract.json` includes complete county sensitivity and only explicitly
complete native-candidate observation universes, sorted decreasing votes then
county/literal label/source row. `source-scoped-orders.json` separately uses source
row tie order to match the captured peer contract. Both retain the full remainder.
Minimum80 uses integer `5*cumulative >= 4*denominator`, requiring the preceding
prefix to fail it. Source-known observations, state-denominator comparisons,
nonadministrative rows and certified full geography are different universes.
Certified native order/top15/minimum80 are null; dispatch keys are empty.

`peer-reconciliation.json` compares exact captured source rows, full raw cells and
metadata, all candidate methods/PDF vectors, native ballot/eligible/registration
fields, county FIPS controls, all18source-scoped full orders and80crossings.
It never imports producer code or edits peer outputs. Coordinator acceptance and
future final-byte equality remain false. `source-disagreements.json` keeps2020
ballot and both registration-stock discrepancies, source-lane differences and
the unmatched2024Otero18 context. `coverage-controls.json` keeps every unknown
count and county control-minus-known lane diagnostic, never used to fill cells.

`turnout-controls.json` keeps complete native and county service fields and source
Ballots Cast/Eligible Voters headers. The signed source Eligible Voters −3 stays
signed. `administrative-method-controls.json` preserves separate PDF header
methods, not candidate methods. `state-candidate-methods.json` retains full raw
sections and numeric vectors; the complete source section determines wrapped
labels, not a conveniently adjacent partial line. `registration-controls.json`
and `registration-native-controls.json` retain all county stocks/native
identities/party blanks, page and line positions, literal clocks, row wrapping,
county totals and grand total. Source registration status is unstated; dated
stocks are not substituted for eligible-voter headers.

## Conditional live calculator

CLI input for `calculator.py --live-json INPUT` is a JSON object:

```json
{"counted_A":40,"counted_B":50,"counted_other":{"C":5},"remaining":100,
 "pair_participation":0.8,"remaining_A_pair_share":0.6,
 "remaining_other_mix":{"C":1},"target_pair_margin":0.01}
```

The example is synthetic; replace labels/assumptions explicitly. `remaining` is
ALL-CANDIDATE valid remaining votes, excluding blank/invalid ballots. Other mix
must name opponents and sum1when a nonpair remainder exists; unavailable mix
leaves the full-field scenario unknown. Counted A/B/each named other remain fixed.
U=remaining×p; forecast A=U×clip(q), B=U×(1−clip(q)), others=(remaining−U)×mix.
FINAL pair denominator=counted_A+counted_B+U. FINAL all-candidate denominator
includes counted and forecast others. Target boundary q=(U+g×FINAL_PAIR_DENOM−
counted_A+counted_B)/(2U). Plurality further requires A to exceed each named other.
Equality is a tie boundary. Source correction uncertainty is outside this fixed
count arithmetic. Invalid negative or nonfinite inputs/bad participation are
rejected, unknowns remain unknown, zero-pool results use counted totals, q is
explicitly clipped. Preference is irrelevant when no pair votes remain.

`live-synthetic-scenarios.json` and `bounded-synthetic-scenarios.json` save inputs
and outputs for meaningful edge cases. No forecast probability, calibrated
Needle or candidate/method/remaining-vote effect is inferred.

## Validation and acyclic asset seal

### Bounded calculator-input repair

The original handoff's input validation accepted Python/JSON booleans as numeric
counts/targets/participation and could iterate malformed/null candidate containers
or serialize echoed NaN/Infinity after arithmetic. The actual CLI also failed on
nonfinite parameters and an unknown county. These defects are resolved without
changing source bytes, count/mask/identity scopes or valid historical arithmetic.

Before owned mutations, `repair-history/pre-input-validation-v1/freeze.json`
(SHA256 `b0291453d6b01926e9ea05a6276c863c2fcf59d226890456e4660d377f97af48`)
froze all103priorowned bodies, old manifest and supplied coordinator evidence,
including exact failing calculator `bf8e719605b3e76442c6a8ce08a25ac9a344597e3901b518766cced20810c351`.
The64original body references are verified/read-only, never duplicated as huge
originals. Gzip SHA-addressed history bodies reconstruct every prior byte.
The initial coordinator finding SHA is
`93402ef5d1a99312fc676fd10e3f5389ba62bdb29200dbfe7b4a9e1c30c2d8a4`;
county-parameter finding SHA is
`d910e56046bcd194e64d6dae3d5e16793395c102ae3626a75f30283d51cd11fd`.
Those old artifacts are historical evidence, not reverse pins of the current seal.

`calculator.py` validates complete supplied requests BEFORE arithmetic, including
when another field is unknown. Numeric fields accept finite representable int/
float values only, explicitly excluding booleans. Counted A/B and named-other
values must be present numbers >=0; malformed numeric nulls/text are invalid.
`remaining`, `pair_participation`, and `remaining_A_pair_share` may explicitly be
null for unknown cases; unknowns never hide another malformed field. When the
remaining pool is zero, an unknown participation/preference is irrelevant and the
fixed count still determines the result. Pair participation is bounded [0,1],
live target margin [−1,1], volumes/counts nonnegative. Finite live preference
inputs outside [0,1] retain documented explicit clipping; they are not coerced to
unknown. Invalid values never become zero or a protected-source allocation.

`counted_other` and `remaining_other_mix` must be named-candidate objects, never
null/text/lists; all keys are nonempty strings distinct from reserved A/B keys.
Values are finite nonnegative numbers excluding bool/null/text; mix values lie
in [0,1]. A nonempty mix must sum1within1e-10, without silent normalization.
An absent/empty mix with positive nonpair remainder stays `unknown_other_mix`;
malformed/nonfinite or unnormalized nonempty mix is invalid, even if another
pool/preference is unknown. Duplicate JSON object keys are rejected before they
can silently replace a candidate. Counted votes remain fixed in every valid case.

Uniform input is a list of explicit volume/share objects. Null volume/share is
unknown; malformed/nonfinite/bool/negative volume or share outside [0,1] is
invalid. Optional source `key`, `id` or `county` identities must be nonempty unique
strings within their namespace; no unit identity is invented for anonymous
numeric weight vectors. Actual county CLI input is checked against the complete
source county set and for uniqueness before arithmetic. Unknown county names
are structured errors. Selected pool must be finite/nonnegative or unknown;
other-net may be signed finite or unknown, target-net must be finite numeric.

CLI target margins and other-unit shifts are finite numbers in [−100,+100]
percentage points; malformed, bool-like text or NaN/Infinity arguments are
structured rejections. Target bounds are checked before division into fractions.
The function-level uniform finite out-of-feasible-range margin stress case
remains `impossible`; external CLI targets outside range are invalid. Selected
unbounded requirements below0/above1remain secured/impossible, not malformed.

Overflow, positive-pool underflow and nonfinite/unrepresentable derived results
are checked before strict JSON serialization. Invalid results contain only
`status:invalid_*`, safe `error:{field,reason}`, and `final:null`; they do NOT echo
invalid raw requests. Exact raw invalid requests remain in frozen/generated
fixtures. Unknown/valid results may retain their fully validated input. Structured
invalid responses exit0with one strict JSON object and no stderr/traceback, the
same response convention as ordinary/unknown cases. Unknown/secured/impossible/
no-pool, final denominator and named-opponent plurality semantics remain distinct.

`input_regression.py` executes132fresh subprocess cases (97negative/35positive),
including all21exact supplied fixtures/argv and16actual prior failures, expanded
numeric/container/key/normalization/overflow/unit-identity cases, and legitimate
unknown/no-pool/secured/impossible/clipping/full-plurality/final-denominator
controls. Exact stdout/stderr, exit codes, fixture/output SHA256 and strict JSON
results are in `repair-regressions/results.json`. `repair_check.py` compares the
rebuilt historical core against the entire pre-repair archive and verifies all64
external originals and old witness bytes. The reciprocal peer's immutable
pre-repair source-core audit excludes calculators/scenarios/report/final manifest
and future-byte equality; this repair does not extend its claim.

`validate.py` recomputes source identities/positions/masks/coverage, county/state
candidate balances, denominator/weight identities, every scenario target and
selected-only feasibility, observed orders/integer crossings, unknown bounds,
live final denominators and fixed counted votes, source/hash/size checks, peer
capture equality and local Markdown links. It writes `validation.json` before
`seal.py` hashes all owned deliverables and exact external source references into
`asset-manifest.json`. `final-seal.json` records pre-manifest validation/regression/
history pins, with no reverse current-manifest pin. The manifest includes all
owned artifacts, including histories, fixtures, validation and final-seal metadata;
it excludes ONLY its own current path. No cache is retained. This avoids
a hash cycle. `validate.py --audit` verifies the final inventory/hashes
without rewriting validation, so the seal remains acyclic. Original hashes and
source receipts are separately verified. No retained file may reach40,000,000B.

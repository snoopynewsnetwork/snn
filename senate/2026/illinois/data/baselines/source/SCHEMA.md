# Illinois historical baselines — schema and scopes

This is an offline historical research/calculation package. All paths below are
relative to `data/baselines/` unless stated otherwise. UTF-8 CSV has one header,
standard CSV quoting, decimal integers for historical votes, and unrounded
decimal floats for scenario expectations. Empty derived CSV cells mean null or
unavailable, never an observed zero. JSON null has the same meaning. A literal
source `"0"` remains an observed zero. `schema-inventory.json` lists every CSV's
exact column order and row count, including compressed outputs and the main
`../county-baselines.csv` compatibility filename.

## Original evidence and reconstruction

`source/registry.json.gz` is losslessly compressed complete acquisition metadata,
including original parent/link/form chains, literal requested/final URLs, HTTP
status, headers, redirects, UTC retrieval, source clocks where supplied,
`bytes`/`raw_sha256`, `path`/`stored_sha256`, compression, and reused-original
receipt path/hash. `path` is relative to this package. Decompress each gzip
body exactly once to reconstruct the entire decoded HTTP response entity.
Transfer/content compression is distinct from these reconstructed entity bytes.
No original is truncated, subset, geometrically simplified or split. Shared
originals are referenced read-only by exact hash, including original sources
acquired by turnout; their parsed derivatives are not primary extraction inputs.
Failed DNS/TLS requests retain explicit error receipts, not invented HTTP status
or response bytes. All stored objects must be strictly below40,000,000bytes.

The current registration page explicitly calls its numbers unofficial and
subject to daily fluctuation. Its displayed clock has no timezone. Historical
result pages are official archival publications; their certification status is
not inferred merely from HTTP200 or a Last-Modified header. Federal books are
second publications of state-supplied votes, not independent underlying votes.

## Literal native CSV

`extract/{2020,2022,2024}-raw-rows.csv.gz` retains every source row, its original
12fields and original order. Added fields: `year`, `source_id`,
`csv_record_1based_including_header`. Position2 is the first data record;
positions describe CSV logical records, not physical newline offsets.

The12literal fields, in source order, are `JurisdictionID`, `JurisContainerID`,
`JurisName`, `EISCandidateID`, `CandidateName`, `EISContestID`, `ContestName`,
`PrecinctName`, `Registration`, `EISPartyID`, `PartyName`, `VoteCount`. They all
remain strings. Source IDs are not FIPS or current result IDs. CandidateID0
repeats across different categories: it is never a deduplication key. Generic
Write-In case variants, Under Votes, Over Votes and Blank Ballots are separate
literal categories, not legally named candidates. All fields outside the target
contests in downloaded HTML/PDF originals remain in those complete originals;
unrelated offices are not separately re-extracted.

`extract/{year}-contexts.json.gz` is an array preserving every full
authority/container/name/precinct presentation and source positions. The2024
file has11,535presentations over114authority/container/name presentations.
`presentation_id` is an extraction-order reference, not a physical precinct ID.
`candidate_category_rows` retains every candidate/category record and all its
candidate/party/name/count literals; `registration_literals` preserves presence
and disagreements rather than repeatedly summing registration.

`extract/{year}-units.json` projects to exact `(year,JurisdictionID,
PrecinctName)` arithmetic contexts. `unit_key` is compact JSON of those3literal
strings. It preserves `presentation_contexts`, every `source_positions`,
`literal_category_record_sums` with only present category keys, original
registration literals, named A/B observations and missing-candidate lists.
`printed_other_observed` is the sum of *available* printed-other records, not
an assertion that absent candidates received zero. `generic_writein_marks` is
null when no generic row exists; `generic_writein_recorded_sum` explicitly
defines the empty recorded sum as0, and `generic_writein_source_present`
distinguishes absence. Under/over/blank observed fields are null when absent.
There is no method column; labels are never decoded into methods. This
projection makes no physical precinct, split style, polling-site, vote-center,
municipal-parent, VTD, crossyear or November2026compatibility claim.

## County, authority, candidates and controls

`../county-baselines.csv` has306rows, one per102combined county×3contests.
`county_key` is the historical county selector ID; `FIPS` is independently
joined to the complete Census county-code original by unique literal-name
normalization, with the exact102matches in `county-code-crosswalk.csv`. No
sourceID arithmetic creates FIPS. `authority_members` is a JSON array of the
historical disjoint native authorities contributing to the combined county.
County selector pages already include city commissions: never add city totals
to these combined county totals.

`A`/`B` are exact named Democratic/Republican counts for the stated contest,
with `A_name`,`B_name`,`A_party`,`B_party` explicit. `pair_votes=A+B`.
`other_named=all_named_votes-pair_votes`, preserving separate named source rows
in the candidate ledger; it is never relabeled Democratic. `A_pair_share`,
`A_pair_margin` use A+B; `A_all_share`,`A_all_margin` use all named source
votes. These four fields are fractions; report values in percentage points
multiply by100. `pair_participation=pair_votes/all_named_votes`.
`native_printed_votes`, `native_generic_marks`, `native_raw_mark_universe`,
`named_minus_native_printed`, `generic_minus_additional_named` keep distinct
source scopes and residuals. `historical_Total_Voters` and `ballots_cast` come
from the102county turnout table, not repeated native Registration. The
historical Total Voters label does not itself establish active/inactive/VEP
definitions or a current registration date. `ballots_minus_contest` and
`ballot_contest_participation` remain separate. Historical winner/margin-band
labels apply only to the stated election. Ties remain ties.

County `native_generic_recorded_sum` explicitly names the recorded aggregation;
`native_generic_observed` is null if no source generic category exists and
`native_generic_source_present` preserves that distinction. The compatibility
field `native_generic_marks` is a recorded sum, never an inferred observed zero.
The final peer availability snapshot is separately retained under
`peer-final-availability/` with its independent comparison JSON.

`authority-inventory.csv` retains all108native IDs, six city commissions,
their historical county parents and explicit compatibility qualification.
`extract/authority-candidate-category-totals.csv` preserves all literal category
sums per authority/year; `extract/{year}-authority-contexts.csv` preserves all
container/name presentations. `extract/selector-coverage.csv` retains the
324county/city selector requests, including18empty city pages and3empty
same-default Adams POSTs. The independently verified initial GET is the Adams
county input. City empty responses mean unavailable, not zero.

`extract/statewide-source-rows.csv` and
`extract/county-candidate-source-rows.csv` preserve all source candidate labels,
blank party strings, votes/percentage literals, exact historical detail hrefs,
resolved URLs, source table IDs and1-based table rows including the header.
The2024state table's27source rows are not asserted to be27legal tickets.
`extract/historical-candidate-metadata.json` preserves complete returned label
fields and text, including source Write-In/status/filing labels. No apparent
running mates, aliases or party blanks are silently joined or filled.

`extract/reconciled-controls.json`, `extract/federal-controls.json`,
`extract/denominator-source-reconciliation.csv` and
`extract/native-registration-observations.csv.gz` retain whole-state, every
county, federal publication and native registration comparisons. The2024
federal scattered518aggregate does not authorize individual name/ticket joins.
`extract/current-registration-source-rows.csv` retains literal JID/Name/A/I
fields plus Totals; its separate controls preserve source clock, unofficial
status and undefined-code qualification. No current boundary join is inferred.

## Priority contracts

`priority/contracts.json` retains full orders, denominators, top15share,
minimal integer80crossing, preceding/crossing votes and all selected keys.
`priority/native-2024-printed-observed.csv.gz` is the primary finer **known
printed source-record** order:10,062contexts, denominator5,592,368, minimal
5,540contexts. Kennedy's15absent rows remain null in source units. The4
administrative-only contexts have `printed_observed_sum=null`,
`printed_known_recorded_sum=0`, null `rank`, and full `order_position` after
observed numeric zero. Arithmetic `ranking_value=0` on those rows denotes the
empty recorded aggregation only. No known zero is assigned to an absent
candidate observation.

Tie break: descending exact integer recorded sum; literal authority ID string,
then literal precinct string. Authority orders retain108disjoint native IDs.
The alternative printed-plus-generic-record order is explicitly a different
source scope. Neither order proves legally exhaustive native eligible-vote
80%membership. Combined-county named, printed, marks and ballot orders are
separate sensitivities. Minimality is exactly `5*cumulative>=4*denominator`,
with the preceding value strictly below; displayed rounding never decides it.

## Scenario weights and targets

`scenario-settings.json` is the declared implementation contract. The27county
models cross historical low/base/high all-candidate volumes,2020/2022/2024
county mixes and2020/2022/2024named pair preferences. For volumeV and mixm:
`N_c=V*N_mc/N_m`; `T_c=N_c*(A_mc+B_mc)/N_mc`. The preference anchor is
independent: `s_c=A_pc/(A_pc+B_pc)`. All102counties participate in every model.
Historical volume anchors are sensitivities, never2026projections.

`state-scenarios.csv` has81county and9native state-target rows;
`authority-state-scenarios.json` adds9authority target rows.
`county-target-scenarios.csv.gz` has8,262county rows;
`native-target-scenarios.csv.gz` has90,558rows;
`authority-target-scenarios.csv` has972rows. Native/authority scenarios retain
2024pair weights/preferences and scale to the three source-based historical
state pair totals; no crossyear precinct matching occurs. Four administrative
contexts have no assigned pair pool and remain unavailable observations.
`native-presentation-scenario-index.csv.gz` associates every11,535presentation
with its arithmetic context without giving category-only presentations extra
pair weight.

745additional2024contexts explicitly observeA=B=0; those have undefined pair
preference and no positive observed pair pool, distinct from the4administrative
unavailable candidate pools. Source zeros and missing values remain different.

`volume`/`expected_pair_votes=T_u`; `pair_weight=T_u/T`; county contest weight
usesN. Net votes=`T_u*(2*s_u-1)`. +1share point gains`.02*T_u`net votes at fixed
pair volume. Share points and pair-margin points differ by factor2.
`unbounded_shift=(g-M/T)/2`. Bounded `shift` solves
`sum(T_u*(2*clip(s_u+shift,0,1)-1))=g*T`. They are separate fields; clipped
units are counted. Tieg=0; pair A+1g=.01; all-candidate A+1g=.01*N/T. Thus
pair+1targets`.01*T`net and all-candidate+1targets`.01*N`net.

Each unit row retains baseline/target shares, net contributions, weights and
gains. Selected-unit-only requirement is
`q_u=(T_u+g*T-M_other)/(2*T_u)` with every other unit fixed at that model's
baseline and0additional share shift. Below0=already secured; above1=impossible;
zero pool and unknown source preferences remain explicit. `selected.py`
offers user-adjustable other-unit shifts with clipping, using complete2024
county or native recorded pair weights. Negative tie shifts are preserved;
already-winning A has zero positive improvement requirement.

## Offline live calculator

`calculator.py` reads a JSON object or list. Each case requires distinct
nonempty string `A`,`B`, a `counted` object of nonempty candidate keys and
finite nonnegative numeric votes, and a `remaining` array. Every remaining
pool has a unique nonempty string `unit` key, `votes` (finite nonnegative number
or null=unknown), `pair_participation` (fraction[0,1]or null), `A_pair_share`
(finite fraction, explicitly clipped to[0,1], or null), and `other_shares`
(named-other fractional allocation summing1when other votes remain). Unknown
pool/mix/preference/other allocation is never silently filled. Booleans are
not numbers. Duplicate/missing/empty unit keys are rejected globally, even
without a selected unit. Zero pools still require valid keys/types.

Optional `selected_unit` identifies exactly one pool. Optional
`selected_target_pair_margin` must be a finite numeric fraction within[-1,1];
null, text, booleans, NaN, Infinity and out-of-range values return an explicit
invalid status with standards-compliant JSON, rather than throwing. Parser or
numeric range errors likewise return explicit invalid status. CLI output does
not echo invalid nonfinite input values.

Counted A/B/**every named other** stay fixed. For remaining all-contest pooln,
pair shareρand remaining A pair shareq, add`nρq`toA,`nρ(1-q)`toB and`n(1-ρ)`
to named others using the supplied allocation. Final pair denominator is
countedA+B+remainingpair; final all-candidate denominator is allcounted plus
allremaining. Outputs include these separately, final net/margins, tie/+1pair
thresholds, selected-only thresholds, clipping events and a full-field strict
plurality comparison. Full-field requirement is the maximum of the B-pair
threshold and every named-other threshold; equality is not a guaranteed win.
The outcome is conditional on the supplied candidate set: output explicitly
states that completeness/current ballot mapping has not been independently
verified. It does not turn hypothetical candidate IDs into an actual2026roster.
Illinois's legal highest-vote/lot rule remains separate from illustrative
pair thresholds. No candidate-ID mapping or2026ballot roster is invented.

`live-synthetic-inputs.json`/results contain20arithmetic scenarios. The7bounded
examples include clipping, already winning, impossible/unknown/no-pool cases.
`negative-fixtures/` contains38CLI validation regressions; some intentionally
contain Python-accepted non-standard NaN/Infinity tokens, explicitly invalid.
Every saved result is strict JSON, exit0and empty stderr. The actual initial
coordinator bug evidence is preserved byte-for-byte under
`calculator-review-evidence/`, with its failing script/input/stdout/stderr
finding and a manifest. These fixtures are not probabilities or calibration.

## Reproduction, checks and seal

Use Python3, beautifulsoup4 and Poppler `pdftotext`; no dependency/cache
directories are retained. `reproduce.py` rebuilds offline from pinned original
bytes, then validates/seals. `check_preflight.py` runs the required coordinator
helper with every output redirected here, shared news remaining read-only.
`replay_acquisition.py` optionally fetches observed literal links/events into
new UTC-prefixed sources, without replacing archived baselines. Historical
public GET/POST requests are read-only; all original form payloads remain in
the registry. The reusable acquisition helper uses ordinary browser UA,
verifies selector choices, and preserves same-default clearing behavior.

`peer-capture/` is an immutable reciprocal snapshot taken only after independent
original extraction. `peer-priority-capture/` separately seals final finer
orders with explicit null-admin semantics. Both reconciliation scripts adapt
source positions (peer firstdatarecord1 vs ours header-inclusive2) explicitly;
they never edit peers. Exact copies and manifests survive later peer changes.
`validation.json` records actual source/identity/coverage/denominator/weight/
bounded-target/live-fixture/relative-link checks. `asset-manifest.json` covers
every owned artifact plus exact shared-original references and excludes only
its own recursive hash. `seal.py --check` is the final read-only asset audit.

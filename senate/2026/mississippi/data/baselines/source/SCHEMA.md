# Mississippi historical baselines, schema ms-baselines-1

All paths are relative to `senate/2026/mississippi/` unless stated. Original
integer counts never become modeled fractional votes. Empty/missing is not zero.
Source CSV spellings, whitespace, parties, repeated state-total fields and every
row of every office survive in the original bytes and all-row JSONL extracts.

**Originals.** `references.json` pins original/publication parent IDs, requested
and final URLs, retrieval UTC, HTTP status/headers, original and stored SHA-256,
sizes and exact stored paths. Most originals are reused read-only from `news/`
and `turnout/source/`; no duplicated huge PDF is required. `downloads.json`
records owned acquisitions. `.body.gz`/`.html.gz` are lossless gzip, regardless
of their historical suffix; decompression returns the exact downloaded bytes.
The 104 actual 2020 county links retain every original/amended alternative.
`county-2020-links.json` retains actual parent order and literal route labels.
The request code percent-encodes spaces in literal href URLs; `final_url` and
redirect records retain the HTTP route. Older reused captures can have no
recorded redirect chain; absence of a field is not proof of no redirects.

**County file.** `data/county-baselines.csv` has exactly 82 county rows, with
FIPS independently taken from EAC jurisdiction `FIPSCode[:5]`, not generated
from alphabetical position. Explicit source aliases: `Jeff Davis` maps to
`JEFFERSON DAVIS COUNTY`; `DeSoto` maps to `DESOTO COUNTY`. Rank is descending
2024 Senate two-name votes, then FIPS ascending for ties. Priority is the union
of the first 15 and the minimum integer prefix satisfying `5*cumulative >=
4*state_total`. It is a historical research priority, not geographic approval.

For prefixes `2024-senate`, `2024-president`, `2020-senate`, A means the named
Democrat in that historical contest (Pinkins, Harris, Espy); B means Wicker,
Trump, Hyde-Smith respectively. `other` contains published named candidates
outside that pair; the complete individual names/parties stay in
`candidate-votes.csv`. `pair_votes=A+B`, `named_candidate_votes=A+B+other`,
`A_pair_share=A/(A+B)`, `pair_margin_pp=100*(A-B)/(A+B)`,
`all_candidate_margin_pp=100*(A-B)/(A+B+other)`, `net_A_minus_B=A-B`.
No generic write-in, blank, under/over or missing ballot value is inferred zero
from a named-candidate-only CSV. The CSV's `other=0` for the 2024 Senate means
no third named candidate in that *publication*, not no write-in marks anywhere.

**Candidate observations.** One row per exact historical contest/county/source
candidate identity; `office_literal`, `candidate_literal`, `party_literal`
retain the original key. `votes` is an integer; `source_id` and
`source_position` locate the accepted observation. Original CSV row/count and
state-column value survive beside updated Pike values. No key deduplication,
rescaling or unexplained residual allocation occurs. 2020 uses the CSV whose
three statewide sums match the amended certificate. The original certificate
is a separate vintage, not silently overwritten. `primary-state-readings.json`
records independent complete-page readings and source clocks, with unknown
timezones explicit.

**2018.** November 6 special and November 27 runoff are separate contests and
electorates. Espy versus Hyde-Smith is a *named pair*, not a union of Democratic
or Republican pools. Bartee and McDaniel remain individual candidates. The
county special's blank party fields remain blank; House Clerk supplementary
political identities never overwrite those ballot fields. Its mixed-stage
summary/footnotes must not be summed into one electorate.

**EAC.** Full Mississippi source rows are retained as compressed JSONL, with ZIP
member, original CSV record number and FIPS. The codebooks and survey instruments
are original primary documents. A1a is registered/eligible people for the
specified general election; A1b active; A1c inactive requiring address
verification. A1d, where present, is a separate other category. F1a is voters
whose ballot was counted, including the listed modes, not certified Senate
candidate votes. F1b Election Day, F1c UOCAVA absentee/FWAB, F1d mail,
F1e counted provisional, F1f early/in-person absentee, F1g all-mail jurisdiction,
F1h other; labels/comments survive literally. Source negative sentinels are
never summed as votes: -88 does not apply; -99 data not available; -77 valid
skip where documented. MS comments combine in-person/mail absentee, so no
mail-only split is manufactured. 2024 F1a is below the signed Senate pair in
eight counties; those universes/vintages remain separate. Registration is not
VEP, and neither survey supplies a 2026 projection or current roll timestamp.

**Native machine evidence.** Every original has a document/page inventory.
`extracts/native-v4/<source>/pNNNN.json.gz` retains PDF text, full-page OCR TSV,
render dimensions/rotation/deskew, source hash, detected grid positions, header
and row/cell positions, raw numeric OCR tokens and explicit unresolved cells.
Numbers in OCR montages map by tile ordinal to the original source cell bounds;
montage padding/tile size is recorded. These are reading aids, not authority.
`native-raw-cells.csv.gz` is the lossless concatenation of extracted field cells;
`observation_key=source:p:row:column` is unique. `unit_key=source:p:column` stays
source-specific even when printed labels repeat or look similar across years.
The native inventory distinguishes source TOTAL, blank/unresolved positions
and labeled columns. TOTAL rows/columns must never be added to their components.
Polling sites, precincts, split styles, central/method groups and municipal
parents need explicit source evidence before semantic classification. OCR
labels/route aliases remain qualified. No name/count implies a cross-year or
November 2026 identity or polygon crosswalk.

**Scenarios.** `state-targets.csv` and `county-targets.csv` have identical
scenario/settings definitions in `calculator.py`. Low uses 2022 EAC F1a volumes
with a declared illustrative pair participation of 1 in every county; base
uses actual 2024 named Senate pair volumes; high uses actual 2020 Senate pair
volumes. Alternative normalization to the 2024 total isolates county mix.
Preferences independently anchor to each of 2024 Senate, 2024 president and
2020 Senate pair shares. These are historical sensitivities, not 2026 forecasts.
The conditional all-candidate columns separately hold the preference anchor's
actual named outsiders fixed in every county. Thus the low EAC numeric proxy
is assigned to the *pair* pool, and additional fixed historical outsiders are
outside that pool; its all-candidate denominator is not claimed as 2022 ballots.
Conditional pair participation is `pair/(pair+fixed_named_outsiders)`. Generic
write-in marks remain unresolved. Named outsiders are never silently converted
to Democrats or mapped onto current 2026 candidates.

`target_pair_margin_pp=0` means pair tie; 1 means illustrative A+1 *pair margin*.
Uniform unbounded share shift is `(target_net-baseline_net)/(2*pair_votes)`.
The bounded solve uses `clip(share+shift,0,1)` and monotone bisection. Both
shifts, clipping count, already-winning condition and achieved net are retained.
One share pp transfers `0.01*T` votes from B to A, adding `0.02*T` net votes.
Share points, margin points, integer votes and all-candidate denominators are
different fields. Selected-only rows hold every other county at unchanged
anchor preferences and scenario volumes; raw required share outside [0,1] is
retained and classified, never silently forced feasible.

**Live remainder.** `calculator.py --live-json FILE` takes an explicit named
candidate counted dictionary, A/B pair and remaining units with stated
all-candidate pools and candidate shares. Counted values are fixed. Only
remaining preferences are explicitly clipped; post-clip shares must sum to 1
or the input is rejected. Unknown pools/mixes remain unknown; negative pools
are invalid; no pool returns observed outcome. Final denominator is counted
all-candidate votes plus remaining all-candidate pool, and the pair denominator
includes counted plus remaining pair votes. The illustrative A+1 target uses
1% of the FINAL pair denominator, never 1% of only the remainder. Each selected
remaining unit holds all other remaining units at the input shares and every
counted candidate fixed. Strict plurality checks A against every named rival;
beating B does not establish a win over Pinkins. Arithmetic outputs are not
calibrated probabilities, a collector, a known live cadence or an election call.

**Completed 2018 county stage controls.** `county-2018-readings.json` contains
164 original county/stage observations with all492 candidate fields. Both
complete82-county vectors now equal the signed stage controls exactly.
`record_2018_controls.py` records the independent manual observations and
correction history. Original candidate-label/TOTAL crops and complete-page
repairs are retained; `source/2018-*-control-review-pointers.json` preserves
which original boxes were displayed. A discovery aid's column ordinal is not
assumed the physical printed column; full-page corrections preserve prior
positions in the underlying aids. DeSoto and Leake physical TOTAL columns were
checked independently rather than joined by ordinal. Native unit identities
remain independently gated. County columns for `2018-special` use Espy as A,
Hyde-Smith as B, with Bartee and McDaniel individually retained as well as their
explicitly labeled outside-pair sum. No blank ballot-party field is filled by
supplementary House Clerk affiliation evidence. `2018-runoff` is a different
electorate. `historical-county-controls.json` checks each statewide candidate.

**All-field manual native samples.** `coahoma-updated-readings.json` and
`alcorn-readings.json` preserve complete original-page readings of35 constituent
columns, all11 required2024 candidate fields,22 corresponding TOTAL cells and
77 unused blank cells. Each page records original render size/rotation/deskew,
physical x bounds, literal full native labels, row bounds and source row/column
positions. `summary_TOTAL` is excluded from component sums; `unused` remains
null, never zero. All candidates, including Independent and minor-party
presidential electors, remain separate. Alcorn's correction history preserves
two compensating manual Sonski errors; a correct county sum is insufficient to
establish that each native cell is correct. Hinds's separate108-Senate-unit
reading is in `native-readings.json`, including the omitted row and explicit
TOTAL/unused positions. These are bounded samples, not all-state acceptance.

**Independent machine aids and geometry.** `vision_ocr.swift` uses local Apple
Vision, accurate English recognition with language correction disabled. The
stored word/observation boxes use normalized bottom-left coordinates; conversion
to raster pixels is explicit in `compile_vision_grid.py`. Original raster hash,
source hash, transform and engine settings accompany each page. `vision_native.py`
re-reads original PDF bytes; `extracts/vision-pages/` retains independent OCR and
exact input rasters. `read_layout_hints.py` and `vision_layout_pages.py` import
only source hashes/pages/transforms/physical boxes from the peer's layout aids.
The frozen hint snapshots deliberately exclude every peer vote, label and OCR
literal; original bytes are independently rendered/OCRed. Different snapshots
and failed reading aids remain separately versioned. `extracts/direct-layout/`,
`extracts/vision-layout/`, `extracts/layout-native/` and `extracts/repaired-grid/`
are qualified reading aids. Conflicting, single-engine, blank and unresolved
readings are distinguished. These derivatives do not authorize ordinal/name
joins, fill missing values, or establish current geometry. Raw originals remain
the transcription authority. A widest-gap rule/nearest-line match is a targeting
aid requiring physical review, never geographic proof.

**Summary/statistics controls.** `canvass-readings.json` independently transcribes
14 complete original summary pages, including all candidate/method vectors and
printed generic/under/over/opportunity fields. `canvass-statistics-readings.json`
independently retains12 original statistics panels, ballots, printed registration,
blank fields, reporting rows, source status/date/clock and literal modes. Source
zero registration and0.00% are preserved as printed, not accepted as proof of an
empty register. Null denotes an absent/unresolved field. Quitman scanned/manual
processing columns are not voting-method groups; their2737 Senate/presidential
universe differs from the2739 Absentee/Precinct ballot panel. Original Pike's
12824 ballots and12647 Senate cast marks are not spliced into updated Pike.
Nonprinted opportunity residuals remain unclassified arithmetic differences.
`validate_canvass.py` checks named controls/method sums and only checks under/over
closure where those components are actually printed. F2 EAC source flags and
comments are also retained for all82 counties in both surveys; they do not
reconcile the survey/candidate universe differences.

**Implemented sensitivity settings.** Five preference anchors now include both
separate2018 stages alongside2024 Senate/president and2020 Senate. Five volume
bases comprise2024 Senate pair,2022 EAC counted-ballot numeric proxy assigned
explicitly to a pair pool,2020 Senate pair,2018 special pair,2018 runoff pair.
Each nonbase volume also has a normalized-to-2024 variant. Thus90 state target
rows and7380 county target rows implement exactly the settings shown in the
report. Historical outsiders remain individually named in the candidate file
and fixed in the conditional denominator under the selected preference anchor.
2018's majority threshold is not replaced by any named-pair tie/A+1 scenario.

**Current method source qualification.** `source/current-method-readings.json`
pins independent reads of actual HB859 official history, CURRENT HTML and PDF,
including full original PDF pages1/8/49. History says Law/Chapter385, approved
March19, effectiveJuly1,2026. HTML prints As Sent to Governor while PDFp1 prints
As Passed the House; neither label is silently rewritten. Section26's daily
aggregate in-person absentee ballot report is available on request; this is
not a public endpoint or candidate count. Later statutes/rules/court orders,
actual November result identifiers and operational completion remain separate.

**Rebuild sequence and dependencies.** Existing originals are read-only inputs;
`python reproduce.py` runs offline county/calculator/report validation using
those pinned inputs and fixed manual ledgers. `--acquire` is a separate opt-in
network acquisition stage; future retrieval is not evidence of past chronology.
Python3 with PyMuPDF, Pillow and NumPy, Tesseract for machine aids, and the macOS
Swift/Vision toolchain for independent Vision aids are environment dependencies;
no dependency or compilation cache directory is retained in the package. The
Swift source is reproducible with `swiftc vision_ocr.swift -o qa/vision-ocr`.
`validation.json` deliberately keeps the full-native question incomplete while
native numeric/identity controls remain pending. `asset-manifest.json` covers
all owned files except its self hash and pins read-only original references.


**Frozen independent native replay.** `native-2024-senate-reviewed.json` and its
CSV/controls are the original frozen25-source scope (553 constituents), preserved
unchanged. `native-2024-senate-reviewed-40views.json`/CSV and
`native-2024-senate-reviewed-controls-40views.json` extend it to40 distinct
county sources,111 pages,985 native constituents,40 separate TOTALs and196
unused template columns. Thus2442 source candidate positions comprise1970
native numeric cells,80 TOTALs and392 unused nulls. Each row carries source
hash/FIPS/page/header bounds/candidate bounds, original literal label and
candidate. The unique source-position key is countyFIPS:sourceID:page:column;
identity still requires physical boxes, not an ordinal-only join.

`source/native-reviewed-25view-positions.json.gz` pins the exact coordinator
frozen peer25-view milestone, and `source/native-reviewed-extension-positions.json.gz`
pins a distinct15-source extension reference. The hint payloads deliberately
exclude labels, roles, printed IDs, values and peer OCR. The small lossless
peer reference is retained only for subsequent comparison, never as an
extraction input. `replay_reviewed_native.py` and `replay_extension.py` render
original bytes again; `extracts/reviewed-replay/` retains exact unaltered raster,
source hash/transform and a separately hashed rule-removed OCR derivative.
Per-page independent fields/headers preserve raw literals and all unresolved
or conflicting readings. Original numeric and expanded header crops in
`qa/replay*-original-*.png` were independently visually read for the explicit
repairs in `record_*repairs.py`; no county residual is used to choose a cell.
Own raster rounding can differ by at most1pixel from the targeting raster;
both dimensions and exact raster hashes remain explicit.

Only literal wrapping is ignored after physical-bound agreement; explicit
Smith `Clear Springs-\nPineville` and Jones `SPRINGHILL/\nMAULDIN` representation
aliases remain recorded. Full original labels preserve their codes even where
an optional parsed ID is blank. The original25-view ledger retains104 optional
parsed-ID omissions as a historical witness. Expanded40 parses Pike parenthesized
codes, Sunflower leading hyphen codes, Wilkinson trailing four-digit codes,
Hinds Precinct numbers and Lauderdale leading hyphen-separated codes from own
literal headers. These are historical source-label metadata, not certified
November2026 or cross-year IDs. TOTALs and unused nulls are never additive.
`validate_reviewed_native.py` checks all40 source/county candidate controls,
physical bounds, original/render hashes and unique keys.

**Native conditional targets.** `native_calculator.py` exports lossless
`native-selected-targets.csv.gz`, with exact ordered-byte reconstruction and
original/stored hashes/sizes in `native-calculator-settings.json`. There are
985 units ×90 settings =88650 rows. Native2024 named-pair weight within each
reviewed parent is actual unit pair / actual parent pair. For other historical
county-volume mixes this fraction stays fixed by explicit conditional
assumption; no cross-year native geometry/preference equivalence is asserted.
2024Senate preference is the actual source-native pair share. Other preference
anchors apply that historical county share uniformly to the source2024 unit
pool, explicitly illustrative rather than observed native history.

Each state net and pair denominator includes ALL82 counties. A selected-unit
solve fixes every other geography at the stated anchor and volume. Required
q=(unit_pair+state_target_net-fixed_other_net)/(2*unit_pair); no positive pool
remains distinct. Requirements outside[0,1] remain unbounded and are classified
before a separate clipped display. Local tie shift is(B-A)/(2*(A+B)); local
A+1 requires0.505 A share,0.5 share points above tie. Net votes, share points,
margin points, state weights and fixed historical named-outsider denominator
are separate. The covered-unit weights sum to the covered parents' fraction
of the full state, never silently to1. The complete native statewide bounded
clipping surface is still pending whole-state native review.

**Presidential and historical machine work.** `extract_replay_president.py`
and `read_presidential_cells.py` independently locate/read all nine distinct
presidential fields at original source positions. Two Tesseract segmentation
modes and separate whole-page Vision readings, source boxes and exact rule
removal settings survive; blank OCR is not zero. Versioned older failed aids
remain alongside improved derivatives. Jackson's complete original p2/3/4
candidate labels were separately visually read to repair absent v4 row
detections; `source/native-presidential-row-repairs.json` supplies only own
field-label/row positions and no vote values. `historical_native_v2.py` reads
2020 and2018 original native blocks independently with fresh literal row/header
OCR and complete numeric cells; adjacent-row proposals are not accepted
candidate identities without fresh source agreement/review. These machine
aids are not whole-state native transcription acceptance.

**Complete 2024 named-Senate source inventory, separate universes.**
`native-2024-senate-reviewed-84views.json`/CSV and its controls extend the
immutable earlier25/40/60 witnesses to84 packet views covering all82 counties.
There are1779 native constituents across alternative packet scopes,84 TOTALs,
447 unused blank columns, and11 Kemper `parallel_native_observation` columns:
2321 source columns /4642 two-candidate numeric-or-null positions on211 pages.
Original Pike and Coahoma alternatives remain separate and are never additive
with their explicitly Updated versions. `use_in_preferred82_scope` selects
one historical publication per county,1736 source-native constituents.
Their printed sums are Pinkins451980/Wicker763420, pair1215400. Certified
county sums451981/763420 and pair1215401 stay separate. Tunica SEMS PDF7–8
prints1797/827 while ES&S PDF3 and countyCSV print1798/827; the exact1vote
source disagreement is unallocated, never rescaled or turned into a fake unit.
Kemper PDF6 explicitly says UnOfficial/Page1 and repeats the11 columns on
Official PDF7/Page2; officialPDF8 adds3+TOTAL. All11 observations on PDF6
remain non-additive, without inferring chronology or silently deduplicating.

`replay_checkpoint.py --name 84views` pins the immutable peer snapshot
bcc0237da3b31fda688c533b1d64eb994ddb9657f78f568973e4a1e5fcfea715.
`source/native-reviewed-84views-positions.json.gz` excludes all peer labels,
roles, IDs, values and OCR. Original rasters/raw numeric/header extraction are
saved first; only then is the complete peer snapshot used for comparison.
Final24 original-only review cards require25 numeric and157 header repairs,
recorded by `record_final_checkpoint_repairs.py` and
`record_final_checkpoint_headers.py`. Expanded Walthall original confirms
printed `4th Distrct West`, with initial manual `District` retained in history.
Lincoln prints `Forrestry`; the earlier60 frozen peer typo survives as an
explicit older witness.58 Itawamba candidate-box metadata differences between
old targeting/expanded reading boxes and new physical-grid hints remain
explicit; agreement on4642 values/labels does not claim exact box agreement.
2075 optional-ID empty-string versus null representations are qualified as
missing/unparsed metadata, not positive printed-ID agreement. Parsed nonempty
IDs agree; full labels preserve printed codes even when optional parsing is
blank. None is a2026/cross-year native ID or approved boundary.

`native_state_calculator.py` uses all1736 preferred source-native units and
all82 parents for90 bounded state scenarios,156240 unit target/contribution
rows and7380 county contributions. Outputs are `native-source-state-targets.csv`,
`native-source-unit-targets.csv.gz`, `native-source-county-contributions.csv`
and `native-source-calculator-settings.json`. Base is the separately declared
1215400 source-native pair, not the1215401 certified county universe used by
the earlier county calculator and40-unit-scope output. Native source parent
weights are actual unit named pair / same-source parent named pair. Low2022
EACF1a has expressly illustrative pair participation=1, high uses2020 county
Senate pair, and both2018 stages remain distinct. Four additional mixes use
common statewide scaling to1215400 to isolate county composition. Other-year
county volume applied to this source2024 native pool is conditional, never
an observed historical native allocation or current geography join.2024Senate
uses observed source-native preference; other anchors use county preference
uniformly inside the parent, explicitly assumed. Full native clipping now
solves q=clip(q0+shift,0,1) by monotone bisection. Unbounded shifts, clipped
units, target/gain/weight/all-candidate denominators and selected-only
requirements remain separate. Selected solves fix all other1735 units at
explicit anchor/volume settings. Shares outside[0,1] retain impossible or
already-above statuses before a separately clipped display. Local A+1 is
0.505 share, adding0.5share points above tie; deterministic pair targets do
not replace legal plurality/special-majority rules. All historical named
outsiders remain separately identified in candidate-votes.csv and fixed at
the anchor pool; generic marks remain unresolved. Exact ordered-byte gzip
reconstruction/raw and stored SHA256/bytes are in settings. Each stored
artifact is strictly below40000000bytes. `validate_final_native.py` verifies
every target, source/render hashes, roles, source balances and positions.

**Additional full-field exception readings.**
`native-source-exception-readings.json` independently reads all11 candidate
vectors from complete original Tunica PDF7/8 and Kemper PDF6/7/8, with full
original render hashes, literal headers, row order and source-column roles.
It adds26 disjoint native constituents,2 TOTALs and16 unused columns, plus
11 separately non-additive parallel observations:429 numeric+176 null cells.
Every candidate vector closes its own printed TOTAL. Tunica Harris1836 native
versus1837 ES&S/countyCSV is a second exact primary disagreement alongside
Pinkins1797/1798. Its generic-write-in totals3 Senate/4 president and contest
opportunities2745 remain separate from named and valid/certified candidate
scope. Together with Alcorn/Coahoma Updated, full11-field review covers61
disjoint native constituents in four preferred county sources; full statewide
presidential/method/historical native review is still incomplete.

**All104 2020 county publications, three-candidate TOTAL audit.**
`county-2020-readings.json` preserves55 initial accepted numeric readings and
failed/wrong-block/cropped discovery aids. `county-2020-repair-readings.json`
adds49 complete original block reviews. Hancock discovery PDF3 has no TOTAL;
complete originalPDF4 prints physical TOTALcolumn4 5651/14537/573, with the
rejected proposal retained. `county-2020-publication-controls.json` and
`county-2020-publication-candidate-votes.csv` reconcile all104 actual packets,
82 counties/22 explicit Amended alternatives/312 candidateTOTAL fields.
The earlier county-TOTAL ledger preserves its checkpoint of51 accepted physical ordinals and53 proposals. The later `native-2020-physical-TOTAL-audit.json` independently reviews actual physical TOTAL positions in all104 complete three-candidate native grids; the earlier locator ledger stays unchanged. This scope does not approve other native methods or current geography.
Using explicit Amended where available, otherwise the original, matches all
82 countyCSV vectors and amended statewide578691/709511/23152 exactly.
Original→Amended changes occur in Adams+454/0/0, Coahoma-115/-28/0 and
Prentiss+20/+48/+2. Other19 paired Senate TOTAL vectors agree; that does not
establish no other office/native cell changed. All-original county totals
578332/709491/23150 differ from original statewide578806/709539/23152 by
-474/-48/-2. No common publication/certificate vintage, change chronology or
county residual assignment follows from Coahoma matching the state amendment
vector. `record_coahoma_2020.py` separately closes all18 native constituents
in each of its two vintages:108 native numeric+6TOTAL+18unusednull Senate
cells; complete original page3TOTAL is physical column8 in both. CountyTOTAL
completion does not establish full statewide2020/2018 native completeness.

`reproduce.py` rebuilds the exact offline ledgers, comparisons, calculators,
report and audits from retained originals/manual readings. `--ocr` repeats
the independent original-raster numeric/header replay before comparison.
Original-only QA mosaics/full pages and failed aids are retained; arbitrary
fresh OCR does not replace accepted visual transcription. No peer file is
modified by any reproduction step. `native-final-validation.json` is a
qualified source/target audit, not a claim the complete question is finished.

**Union vendor-native profile partition.**
`extract_union_native_profiles.py` extracts the20 original ES&S profile pages
PDF16,18,…54 from raw hash19a5a0a1138eda18230011669318540099456001a6c1406709743a4dcb384a09.
`union-native-profile-original-extract.json` retains complete raw page text,
19 required numeric-word boxes per source page, raw text-layer literals and
exact full original raster hashes/scale. No peer label/value is an extraction
input. Five original-only panels under `qa/union-independent-profiles/` display
all380 required original field glyphs and20 original printed headers. The
manual literal values in `record_union_native_profiles.py` are independently
read from these originals; printed thousands commas and decimal percentages
are explicit manual literals, never punctuation inferred from text-layer OCR.
`union-native-profile-readings.json` and `union-native-profile-fields.csv`
preserve source profile codes101–504, literal printed headers, fields, both
text/printed literals, values, original PDF-point boxes and reading evidence.
The nine presidential identities, two Senate identities, two generic-mark
fields, two separate contest totals, registration, ballots and blank counts
are18 count fields; printed turnout is the nineteenth, nonadditive rate.
All18 count vectors sum to independently original-read summaryPDF12/statsPDF11.
Numeric original/text-layer differences number7 in this extraction; raw
complete page text also retains label/header extraction failures. Text output
order can put the Union County label after a profile heading: failed raw
header proposals remain verbatim and actual printed headers are independently
read. Profile clock4:58PM and summary4:52PM on11/14/2024 remain separate, no
release chronology. Generic Senate84/President18 marks are not assumed valid
named write-ins. Unprinted under/over fields remain null; Senate186 and
President37 contest-minus-named-plus-generic residuals are arithmetic only.
The profile view is never joined/deduplicated to SEMS/current precincts by
label/count. It adds20 complete all11 vendor-profile observations, separately
from61 complete SEMS constituents in four county views.

`reconcile_union_native_profiles.py` reads peer fields only AFTER independent
original numeric/header readings are saved. It freezes an exact small CSV
reference losslessly at `source/peer-union-profile-fields-reference.csv.gz`.
All380 values, exact raw text-layer literals/PDF-point boxes, labels, IDs,
roles and source hashes agree in `union-native-profile-peer-reconciliation.json`.
Neither this bounded review nor agreement establishes current geography.

**Alternative partitions and repeated observations.**
`native_alternative_calculator.py` adds88 source-native unit observations:
original Pike SEMS25, original Coahoma18, Union vendor profiles20 and original
Pike vendor profiles25. For each
source partition, the ENTIRE selected county partition replaces the preferred
source view and all other81counties stay in the state calculation. This uses
no source-unit crosswalk. There are360 complete-state scenario settings and
7920 selected-unit/local contribution rows, preserving the same nine volume
and mix settings/five historical preference anchors/two pair targets. Base is
actual named pair in that explicit source mixture; originalPike gives1212682,
versus1215400 in the preferred source mixture. Normalized variants use that
mixture's own base. Other-year native weights/preferences remain expressly
conditional over these2024source partitions. `native-alternative-unit-targets.csv`,
`native-alternative-state-targets.csv` and settings retain bounded/unbounded
shifts, state denominators, every-unit contribution/weight/gain and selected
requirements with every other unit fixed explicitly. `native-parallel-observation-local-targets.csv`
contains22 local tie/A+1 targets for11 non-additive Kemper unofficial page
observations. Their selected-state status explicitly declines to infer an
independent disjoint pool for a repeated source observation. Null or impossible
requirements are never silently clipped into feasibility. The supplemental
audit is `native-alternative-validation.json`.

**Continuing presidential row/cell extraction.**
`extract_replay_president.py --ledger native-2024-senate-reviewed-84views.json --tag v4`
and the matching `read_presidential_cells.py --ledger ... --tag v4` independently
read all nine fields at all reviewed Senate-page positions, retaining older
25-view raw artifacts unchanged. The new v4 files are aids, not completed
presidential transcription. Missing row locators, two-mode/whole-page-engine
conflicts and blank OCR remain explicit. Presidential-only/vendor/method pages
require their own inventories; Senate page coverage does not imply their
absence. `locate_presidential_rows.py` uses fresh own-original candidate word
anchors and physically detected table rules to propose row boxes, without any
vote count or peer field input. Missing/ambiguous labels and unresolved rule
bounds survive in `source/native-presidential-fresh-row-proposals.json`; a
nine-row expected order alone is not accepted field identity or a zero.
`source/reviewed-source-scope.json` pins the bounded milestones and explicitly
qualifies the earlier complete named-Senate inventory flag to its reviewed
SEMS partition, with remaining vendor/method/all-candidate/history gates open.

**Primary native order, distinct county sensitivity, immutable v1.**
`build_native_orders.py` independently sorts own reviewed source candidate
counts descending, ties by the literal full source-position key. All84 source
views have separate orders; original Pike/Coahoma alternatives, TOTALs/unused
and Kemper parallel observations do not enter the preferred1736-unit partition.
`native-source-orders.json`, `native-full-order.csv` and
`native-priority-contract.json` declare the preferred native order PRIMARY:
top15native60019/1215400; minimum80 prefix887, preceding886=972157,
crossing887=972656, original LauderdalePDF9c5 `450 - Pickard`119+380=499.
All849 nonpriority units/242744 source votes remain in state calculations.
The887 children occur in77 county parents, with five empty priority-child
lists. All82 parent/all-child and priority-child mappings remain explicit.
The41-county/top15653846 county ranking is a separate parent sensitivity and
never substitutes for primary native dispatch. `data/county-baselines.csv`
retains a legacy `priority` boolean but adds the unambiguous `priority_scope`
and `primary_native_priority_contract_path`; that boolean denotes only county
parent sensitivity. County and native pair denominators remain1215401 and
1215400. Unknown Tunica1 stays unallocated; even top886+1=972158 is below both
integer80% thresholds972320/972321. Its largest published native unit394+1
cannot reach the499 cutoff. This is an upper-bound proof without assigning
the vote, not a unique-all-possible-80%-sets or current-geometry assertion.

`reconcile_native_orders.py` freezes the actual peer source-order bytes and
independently compares84 orders plus the entire1736 preferred native order:
3515 ordered unit positions/7030 candidate fields, full keys/parents/ranks/
cumulatives agree. Four explicit Holmes hyphen-wrap representations survive.
The working peer order adds43 optional parsed ID fields from unchanged literal
headers (Claiborne12/JeffDavis17/Perry14), while frozen84 metadata is unchanged.
These additions appear86 times across individual-source and preferred-order
comparisons and are recorded separately, never called byte-for-byte old-ID
agreement. Names/codes are historical source metadata, not2026IDs/crosswalks.

`freeze_native_priority.py` stores immutable lossless copies of the coherent
contract, full orders, flat file and reciprocal proof under
`source/native-priority-v1/`. Its snapshot pins each original/stored byte size
and SHA256 plus the exact frozen84 input hash. Existing v1 is verified and
never overwritten; later revisions require another explicitly named version.
The status is an independent worker887proposal pending coordinator acceptance,
with original all-candidate/method/history and current2026geometry gates open.
`native-priority-validation.json` checks every key array, all82parent-child
maps, exact integer crossing/unknown1upperbound and all4 immutable pins.

**Versioned13-page presidential row repairs.**
`render_presidential_row_review.py` produces original-only field-label strips
with source-y ticks in the margin. All9 printed candidate labels/order were
independently read on each of13 pages in Itawamba, Scott, Amite, Webster and
Winston. `record_presidential_row_repairs_v5.py` saves117 field-label/position
repairs in `source/native-presidential-row-repairs-v5.json`; earlier Jackson,
v4 raw OCR and v1/v2 fresh-rule proposals remain unchanged. Winston windows
are expressly manually estimated complete-field reading windows on the faint
gray source, not exact printed-rule geometry. v2 rule proposals use vertical
spread to recover slightly skewed faint rules; proposals do not define field
identity. `--tag v5 --only ...` rereads those original presidential cells at
the independently reviewed row positions, without using a peer value or a
county residual to select a row/cell. They remain aids pending numeric review.

**Original Pike vendor profile partition.**
`extract_pike_vendor_originals.py` independently renders and reads every actual
PDF15–56 page, retaining all42 complete original rasters/whole-page OCR and
source hashes. `extract_pike_vendor_fields.py` identifies profiles by each
printed code01–25 and office/candidate/TOTAL labels. Profiles have variable
length; an alternating-page stride is never used. Candidate order also varies,
so labels define candidate fields. `record_pike_native_profiles.py` records
all525 original glyph fields and25 headers in `pike-native-profile-readings.json`
and `pike-native-profile-fields.csv`; source values were read before a peer
field comparison. Twenty COUNT vectors are additive;25 printed turnout
percentages are nonadditive. Nineteen vectors close original county PDF12/13,
including reg24692/ballots12824, Senate5898/6719/generic30/cast12647 and
contest12824. Profile blank1 has no printed county blank control. Unprinted
under/over fields remain null; Senate177/President78 contest-minus-cast
residuals are arithmetic only. Original source says `Peter Sonsk / Lauren Onak`;
the canonical field name preserves candidate identity while raw labels retain
that literal truncation. PDF49 prints1. Profile06 PDF25 raw OCR `Write-in Totais`
failed the initial label locator; the full original visibly prints generic1.
The missing-target initial extract/card are retained in source/qa and repair
history records the original-only reread, without fitting any county residual.
Original profile clock11/15/2024 3:07PM versus county3:05PM is not publication
chronology. Registration active/inactive/status date remains unspecified.

`reconcile_pike_native_profiles.py` separately freezes the exact peer aggregate
CSV after own525 original readings, retaining the earlier Union-only reference
unchanged. All525 field values/pages/codes/literal labels/source hashes agree.
Ownfitz2.4 versus peerfitz3.5 complete reading windows are recorded separately,
never claimed exactly equal. The original vendor partition is an alternative
complete county view, never additive to original/updated SEMS or current units.
Updated Pike has its own named controls; no original profile allocation of its
explicit additional votes is inferred. The offline reproduction and validator
include this bounded audit and the separate alternative targets.

**Background-adaptive presidential cell aids.**
`read_presidential_cells.py --tag v5 --cell-tag v6 --adaptive` retains the old
fixed210-threshold v4/v5 cell outputs. The old rule detector can erase a gray
scan whose paper is darker than210 (Winston); that failure is evidence, not
an absent/zero cell. v6 detects dark rules relative to the original cell's
80th-percentile paper level minus45, capped210, then autocontrasts only the OCR
derivative. Original rasters/complete boxes/two segmentation modes and separate
whole-page readings remain preserved. These outputs are unreviewed aids;
multi-engine agreement or county closure alone never establishes accepted
native transcription.

**Additional complete original candidate vectors and exact field coverage.**
`record_winston_allfield.py` types every original glyph on Winston PDF2/3:
12 native/one TOTAL/nine unused columns;143 numeric+99 null all11candidate
positions. Its two complete original gray-scan rasters are the reading
authority; failed numeric derivatives remain retained, with no zero inference.
`record_native_allfield_batch.py` adds original complete-page all11 readings
with separate per-county controls. Source header positions/roles come from
OWN previously independently original-reviewed historical SEMS header grids;
this is the same exact raw publication/page, not a name/count cross-year join.
Every new numeric vector is typed from the complete original, never a peer
derivative or a county residual. `native-allfield-additional-readings.json`
and its flat CSV keep original hashes/page/physical column/header bounds and
all explicit zeros/TOTALs/unused blanks. Source numeric reading evidence is
the whole original page; experimental numeric crop rectangles are not claimed
accepted exact source field polygons. For Issaquena actual PDFpage1 has the
printed footer Page2; the key is actual PDFpage1. Its unusual printed all-one
small-candidate vectors are retained literally, not normalized to presumed
zeros. Generic/under/over/ballot/registration fields unprinted in a selected
SEMS grid remain unknown, with other vendor/method views separately audited.

`build_allfield_coverage.py` checks each original11candidate native sum against
its printed TOTAL and inventories all82 preferred parents/1736 source units.
`native-allfield-coverage.json` pins every owned original-reading ledger and
counts its exact complete/unreviewed native scope. Unreviewed presidential
fields are not filled with proposals or counted as zero. Tunica's source
Harris1836 versus certified county1837 stays an unallocated source difference.
Kemper's eleven parallel observations stay nonadditive. Union/Pike vendor
profiles remain additional source views, never deduplicated/added by name.

`freeze_allfield_milestone.py --version Nviews` saves eight lossless, immutable
original/stored byte pins under `source/native-allfield-Nviews/`. Versions
10views, 15views, 16views and 25views preserve their actual historical scope;
rerunning an existing version verifies its frozen bytes without replacing
them with a later working aggregate. The 25-view witness covers 431 preferred
native constituents on 53 original pages, 25 separate TOTALs, 116 unused
columns and 11 nonadditive Kemper parallels: 5,137 numeric and 1,276 null
candidate positions. Its additional sources after 16views are Jackson,
Sharkey, Quitman, Sunflower, Adams, Franklin, Jefferson, Carroll and Clay.
Each new nine-candidate presidential vector was typed directly from the
complete original raster. For these sources and Hinds, the two Senate
fields reuse this package's earlier independently original-reviewed values
at the exact same source hash, page and physical header bounds, with that
basis retained per field. This is not a fresh Senate transcription claim.
The remaining 1,305 preferred native constituents in 57 county source views
remain explicitly unreviewed for all nine presidential fields at this
witness. All-field scope counts do not imply historical/method/current
geography or external 887-unit dispatch acceptance.

Later immutable witnesses are 35views (616 preferred native units, 74 pages),
45views (777 units, 94 pages) and 50views (861 units, 104 pages). The 50-view
snapshot preserves 50 TOTALs, 222 unused columns and 11 Kemper parallel
observations, with 10,142 numeric and 2,442 null candidate positions. Its
875 unreviewed native units in 32 preferred county views remain outside the
all-nine-presidential original-reading scope. The same exact-source Senate
reuse qualification applies to each newly typed presidential-only vector.
`record_allfield_corrections.py` reconstructs the complete Stone Kennedy-row
reading enlargements and preserves the initially failed typed vector. Original
glyph rereading corrected adjacent values 4/2 to 0/4 in columns 2/3; no residual
was allocated and the failed attempt never became an accepted Stone ledger.

The immutable 55-view witness adds Harrison49, DeSoto47, Rankin46, Madison44
and Forrest34 native units: 1,081 preferred units on 128 original pages.
The 60-view witness then adds Lee33, Jones38, Hancock26, Pike Updated25 and
Lauderdale37. It covers 1,240 preferred native units on 146 original pages,
60 separate TOTALs, 295 unused columns and 11 Kemper nonadditive parallels:
14,421 numeric and 3,245 null candidate positions. All nine presidential
vectors in these views were directly typed from complete original rasters,
with the two exact-source prior Senate fields explicitly identified as reuse.
At this frozen witness 496 preferred native units in 22 of the 82 preferred
county source views remain unreviewed for all nine presidential fields. The
two earlier Pike/Coahoma alternative packets belong to the separate 84-view
publication universe and are not counted as additional preferred counties.

The immutable 65-, 70-, 75- and 80-view witnesses preserve their exact earlier
scopes. The 82-view witness closes the preferred named-candidate partition:
all 82 preferred county views, 1,736 disjoint native constituents, 206 original
pages, 82 TOTALs, 437 unused columns and 11 nonadditive Kemper parallels;
20,119 numeric and 4,807 null candidate positions. The coverage flag
`complete_statewide_nine_presidential_native` applies only to this preferred
SEMS partition. It does not close all vendor/method/history/peer gates.
The earlier snapshot's broad `complete_statewide_presidential:false` remains
immutable; its narrower complete preferred flag is in the frozen coverage body.
`build_2024_native_candidate_controls.py` compares all 902 county/candidate
vectors with signed controls. Only Tunica Harris1836 versus1837 and
Pinkins1797 versus1798 differ, each -1, unallocated; preferred presidential
source denominator1,228,007 versus signed1,228,008, Senate1,215,400 versus
signed1,215,401. The other nine named vectors balance individually statewide.

`record_native_alternative_allfield.py` directly reads the two earlier
Coahoma/Pike SEMS alternatives into a separate ledger/flat CSV: 43 native,
5 pages,2 TOTALs,10 unused columns,495 numeric+110 null all11candidate
positions. Coahoma's18 and Pike's25 each close their own original TOTALs.
Pike retains the original6091/6504 presidential major pair and5898/6719
Senate pair; the updated publication stays a distinct source. No alternative
observation is added to the preferred82 statewide pool or joined by name.

`reconcile_presidential_batches.py` compares only frozen actual peer original
readings AFTER own complete82source transcription. The through-batch11
Winston-v2 witness checks52source views/12,546 presidential positions:
9,855native,468TOTAL,2,223unused/null. All values/roles/literal labels after
whitespace-only folding agree; original source hashes and PDFpage/physical
column/header are jointly checked. Prior Alcorn/Coahoma all11 agreement stays
a separate proof, giving bounded54preferred/1130native peer coverage, not all82.
Original rasters, numeric crop polygons and parsed IDs are not claimed identical.
The older through-batch11-v1 witness remains immutable; it omitted Winston
and therefore covers51views/12,348positions, not the later52view scope.
The new `through-batch26-v3` snapshot freezes60 exact complete peer derivative
input bodies, captured read-only after own82preferred original transcription.
Its immutable `reconciliation.json` compares73source views/17,991presidential
positions:13,995native,657TOTAL,3,339unused/null, with zero value/role/whitespace-only
label differences. Together with the separately pinned Alcorn/Coahoma all11
proof, the bounded preferred peer scope is75views/1,590native;7views/146native
remain outside it. Original PDF hashes/pages/physical columns/literal headers
are jointly checked; render pixels/numeric polygons/optional parsed IDs are
not asserted identical. Missing OCR aids versus directly read numbers/nulls
remain in the full frozen peer ledgers. No peer numbers enter own source readings.
The `through-batch33-v4` snapshot adds the final seven preferred views using
74 exact complete peer derivative bodies. Its replay checks80source views /
19,872nine-presidential positions:15,309native,720TOTAL,3,744unused/null and
99nonadditive Kemper parallel positions. Together with the separate Alcorn/Coahoma
proof, all82preferred /1,736native named-presidential scope is checked at20,268
nine-presidential positions. All values and roles agree. Eighteen Holmes positions
retain two explicitly listed A-hyphen-line-wrap representation aliases, unequal
under whitespace-only folding; neither literal header is rewritten.
The older Perry/Tunica peer CSVs omit126unused/unprinted positions (45/81),
already null in own direct-original ledger. `own_positions_outside_peer_flat_scope`
lists all126exact source/candidate keys, roles, nulls and raw hashes; peer nulls
are never imputed. No numeric/native/TOTAL/parallel field is missing. Blank-field
scope therefore remains unequal. Kemper peer header boxes are unavailable;
literal labels/roles/ordinals are checked without exact-box equality.
The script defaults to v4 for offline replay; older v1/v2/v3 and the combined
named-v1 witness retain their earlier exact bytes and narrower scopes.
`freeze_2024_named_fields.py` pins alternatives,902controls and bounded peer
proof under `source/native-2024-named-v1/`, referencing the immutable82view
snapshot without duplicating its raw assets. Across84 separate SEMS source
scopes this covers211pages/2321column objects/25,531all11candidate positions:
20,614numeric+4,917null. Alternatives/parallels remain nonadditive; this is
not whole-question, method/history/currentgeo or fullpeer acceptance.

**2020 native publication review.** `render_historical_native_original.py`
also renders the separately scoped2018native originals. The bounded direct
`record_2018_native_original.py` ledger currently reads Issaquena Nov6/Nov27:
five physical named columns per stage, TOTALphysical6 and five unused slots,
36numeric/30null candidate positions. Its164source inventory keeps all other
native counts unknown. Selected special/runoff row party fields are unprinted,
stored null rather than borrowing a party label from a different printed row.
`validate_2018_native.py` checks source/raster/flat identities, literal headers,
all candidate vectors and stage-specific controls. The precise pre-correction
county ledger is losslessly frozen under
`source/2018-physical-column-corrections-v1/`. Working Nov6 physicalTOTAL6
supersedes old machine ordinal4 only through explicit history; original source
position aid, correct target box, four candidate counts and other163 county
readings remain unchanged. The reverse peer check reports a peer still carrying
4 as an explicit original-evidenced metadata difference, never silently as
physical-position agreement. No cross-stage/current ID or geography join.

**2020 native publication review continued.** `render_historical_native_original.py`
reconstructs complete original pages with raw-source/page/render hashes and
explicit transform receipts. `record_2020_native_batch.py` types candidate
glyphs and literal headers from those whole originals; it does not import a
peer,2024native identity, or county residual. Initial additions were Alcorn17,
Benton original5, Benton amended5, Greene13 and Wilkinson9 native constituents. Every three
candidate vector closes its exact publication TOTAL. Alcorn actualPDF3TOTALc7,
Benton actualPDF2TOTALc6, Greene actualPDF3TOTALc3 are independently counted
physical source columns; older county-TOTAL proposal records remain unchanged.
Benton/Greene candidate windows cover the entire Senate band and are explicitly
provisional, not exact row polygons. Physical source ordinal/literal header/
candidate name plus complete page identify the observation. The unused columns
remain null; generic/method/ballot/registration fields unprinted on these
selected grids are unknown. Full originals retain every other office/field.
`build_2020_native_coverage.py` combines prior Coahoma original/amended with
these additions while retaining all104publication statuses:7reviewed source
views/85native across vintages/276numeric/87unusednull. Only5selected county
views/62native belong to its bounded amended-where-linked82county comparison.
Unreviewed native counts are unknown, never borrowed from2024 or filled zero.

`freeze_2020_native_milestone.py --version 7views-v1` preserves the exact
initial seven-publication ledger/flat/coverage bytes under `source/native-2020-7views-v1/`.
Later versions must be new immutable witnesses. Wilkinson literal printed
codes1020/3010/4020/2020/5020/5010/4010/1010/2010 are retained as source-only
metadata, not joined to2024 or current IDs. Its sourceTOTAL is physicalc10.

The `11views-v1` witness additionally preserves Issaquena5, Noxubee8 and both
Sharkey10 publication native views, independently read from their complete
originals:11publication scopes/118native across vintages/387numeric/108null;
selected82comparison only8county publications/85native. All104 source-vintage
statuses remain visible. IssaquenaTOTALc6/NoxubeeTOTALc9/SharkeyTOTALc11
are physical source columns. The original Sharkey machine aid's extra12th
column extended outside the actual printed table to the scanned page edge;
it is retained as a rejected machine proposal, not a native/unused column.
The amended Sharkey form has a distinct original hash/header grid/reading;
matching candidate vectors do not establish native or publication equivalence.

The `22views-v1` witness preserves eleven additional independently read
publication scopes: Calhoun10, Tishomingo14, Smith18, Carroll14, Clay14,
Jefferson12, Claiborne11, and both original/amended Sunflower17 and Choctaw13.
Its combined coverage is22publication views/271native across separate vintages,
22TOTAL columns/103unused columns/879numeric/309unusednull positions.
Only15selected county publications/182native belong to the amended-where-linked
82county comparison. Earlier7/11view frozen witnesses remain unchanged.
Every candidate vector was typed from the complete original page and closes
that publication's printed TOTAL. Physical TOTAL columns are CalhounPDF2c11,
TishomingoPDF3c4, SmithPDF3c8, Carroll/ClayPDF3c4, JeffersonPDF3c2,
ClaibornePDF3c1, both SunflowerPDF3c7 and both ChoctawPDF3c3.
Several machine grids omitted internal rules or treated outer page/fax margins
as extra columns. Fresh physical-grid readings restore actual printed columns;
the failed machine proposals remain unchanged. Broad Senate-band candidate
windows remain explicitly provisional, not accepted exact numeric polygons.
Claiborne's literal County Precinct4-D and Choctaw's Bywy are retained;
source-printed codes in Claiborne/Sunflower are source-only metadata.
No matching vectors establish cross-publication, cross-year or current identity.

The `34views-v1` immutable witness adds twelve original-reviewed publication
scopes beyond22: Perry15, Webster17, both Yalobusha12, Covington15, Prentiss15,
Adams19 and Lawrence24 publication views. Combined34publication scopes contain
473native constituents across separate vintages/34TOTAL/175unused columns,
1,521numeric+525null candidate positions. The selected82comparison contains
only22county publications/299native. Adams originalPDF3/4 and amendedPDF2/3
close7,736/5,416/152 versus8,190/5,416/152; Prentiss original/amendedPDF2/3
close2,694/7,603/227 versus2,714/7,651/229. Neither publication is overwritten,
and no same-header identity/chronology join follows. Lawrence's literalA-Z/91
suffixes retain unresolved split/administrative meaning; all three actual
source pages are retained in each view. Yalobusha amendedPDF3TOTAL is physicalc2,
correcting only the fresh native locator metadata; the earlier unaccepted
county-TOTAL proposal1 remains unchanged. WebsterPDF2 Cumberland/Espy was
initially manually read54; an enlarged complete ORIGINAL Senate-row crop shows64.
The literal correction history, original crop/hash and initial value are retained;
the source glyph supplies the correction, not an allocated residual.

`validate_2020_native.py` independently checks every additional flat CSV row
against source-position/literal-header/party/candidate/role/reading-window fields,
full original/render receipts and source-specific three-candidate controls.
It checks unused nulls and optional-ID absence without claiming positive ID
agreement, reproduces every correction crop from its whole original raster,
and verifies all four lossless pins plus prior-source-object continuity for
every immutable witness. An explicit later source-header glyph correction may
change only the exact recorded old/new literal and add its reproducible source
crop/history. The validator reverses precisely that declared change and requires
all other source semantics, candidate values, raw/render hashes and bounds to
match the prior witness. Older frozen bytes are never changed or silently
normalized. `native-2020-validation.json` reports the
bounded current scope; unreviewed source counts remain unknown and all full
historical/method/current-geography gates stay open.

`reconcile_2020_native_peer.py` freezes14exact peer original-reading derivative
bodies under `source/native-2020-peer-seven-v1/`, read-only after own source
transcription. Own comparison values come from the separately immutable60view
flatCSV, never peer votes or mutable working source rows. All seven publication
views/62native/297positions agree:186native,21TOTALnumeric and90unusednull.
Every source hash/page/physical column/source key/candidate/role and whitespace-
folded literal header is checked. Both full original-page raster hashes are
retained; exact pixels, numeric/header polygons, unavailable peer party or
parsed-ID fields, chronology/current geography and full historical scope are
not asserted equivalent. `native-2020-peer-reconciliation.json` reproduces the
immutable result. Original sources remain independently hash checked.

The `65views-v1` witness adds Jackson32, Hancock25, Lee36, Jones37 and DeSoto41
native constituents across18whole original pages. Combined65publication scopes
contain1,159native across vintages/65TOTAL/338unused,3,672numeric/1,014null
candidate positions; selected82only48publications/905native. LeeEuclatubba
header evidence is an exact whole-raster crop/rotation with reproducible bounds
and hashes. DeSoto's smaller embedded table uses separate fullpage/header/row
windows; a retained header-only dark-column probe keeps unfiltered text-stroke
false rules distinct from physically read table rules. It reads no vote digits
and approves no numeric/geographic polygons. Cumberland/Espy initial1,050 was
corrected to visibly printed1,060 by the complete original three-Senate-row
strip; initial value, exact crop/hash and source-glyph basis retained. Validator
reconstructs both original crop types and checks rule-aid/source hashes.

The `70views-v1` witness adds Washington original/amended19 each, Forrest34,
Madison43 and Harrison53 native constituents across17whole original pages.
Combined70publication scopes contain1,327native/70TOTAL/351unused and one
separate administrative column,4,194numeric/1,053null candidate positions;
selected82only52publications/1,054native. HarrisonPDF4physical4 literally prints
Invalid Addresses9999 and explicit0/0/0, role
`source_administrative_reporting_column`; it is not a precinct or unused blank.
Administrative candidate counts remain separately recorded in coverage, and
source TOTAL reconciliation includes them without allocating their votes to
other units. Washington amended actualTOTALPDF3physical9 replaces only the
unaccepted machine proposal7. KemperPDF2physical9 original header visibly
Lynville, one n, after a fresh complete original and exact upright crop read.
Earlier immutable55/60/65 retain the initial Lynnville reading. The70ledger
retains initial/accepted strings, source/render/crop hashes/bounds and history;
all3candidate values133/180/2, positions and original assets remain unchanged.
The immutable-chain audit identifies this precise metadata transition rather
than claiming byte-identical source objects across it. Full historical/method/
current-geography/priority-dispatch gates remain open.

The `75views-v1` witness adds Copiah19, Holmes16, Leflore18, Montgomery15 and
Lowndes20 native constituents on10complete original pages. MontgomeryPDF2/3
visibly print UnofficialRecapitulation and footerPage1/2, retained explicitly
as `source_status_literal`/`printed_footer_page_literal` rather than borrowing
an official status from the county-index page. Holmes Walden label literally
ends Chapel(A-Z without a closing bracket, and other A-/Z wraps remain printed
label representations; no partition normalization or parsed unique ID claim.
Combined75publication scopes contain1,415native/75TOTAL/368unused plus the
one separately administrative Harrison column,4,473numeric/1,104null candidate
positions; selected82only57publications/1,142native. All candidate vectors
close each exact-publication printedTOTAL; other offices remain original bytes.

The `80views-v1` witness adds Rankin48, Tallahatchie21, Tate20, Union20 and
Walthall20 from13complete original pages. Rankin actualTOTALPDF6physical5 differs
the earlier unaccepted merged-machine proposal4, which remains unchanged in
its original aid. Tallahatchie literal Murphreesbore header final e is supported
by exact unchanged-pixel original crop/rotation; no gazetteer normalization.
Walthall places Senate before President; Union's faint complete originals have
no accepted machine numeric grid, so broad original Senate-band windows and
unfiltered header-only pixel proposals remain qualified separately. Combined
80publication scopes contain1,544native/80TOTAL/377unused plus1administrative,
4,875numeric/1,131null candidate positions; selected82only62publications/
1,271native. These are source publication partitions, not2024/current joins.

The `85views-v1` witness adds Oktibbeha20, Panola21, Grenada13, Bolivar28 and
Itawamba28 from12complete original pages. All3native candidate vectors per
publication close its printedTOTAL. Grenada's literal Box prefixes and
Itawamba's unsuffixed/district-suffixed Friendship/Mantachie columns remain
distinct source observations, no cross-year/current ID or count equivalence.
Grenada uses qualified broad whole-Senate windows after the original machine
row detector stopped above the Senate contest; full original remains authority.
Combined85publication scopes contain1,654native/85TOTAL/394unused plus the one
administrative column,5,220numeric/1,182null candidate positions; selected82
only67publications/1,381native. All remaining native counts stay unknown.

The `90views-v1` witness adds Marion original/amended22 each, Marshall original/
amended24 each and Pike25 from15complete original pages. Each publication is
freshly original-read rather than copied from equal earlier vectors. Marion
has a separateTOTAL-onlyPDF4physical1 and ten unused slots. Marshall's smaller
embedded tables have different page offsets and header-only pixel aids retain
false text-stroke proposals; printed margin fax times/dates are explicit
`source_clock_literal` with zone absent/no established publication or release
clock. Pike's literal01..25 codes are parsed only as printed header substrings,
with no vendor/SEMS2024/current crosswalk. Candidate windows remain qualified
broad source reading windows where machine numeric/row discovery failed.
Combined90publication scopes contain1,771native/90TOTAL/437unused plus1admin,
5,586numeric/1,311null positions; selected82only70publications/1,452native.

The `60views-v1` witness adds Lafayette original/amended18 each, Newton16,
Simpson23 and George22 across12complete original pages. Combined60publication
scopes contain988native across vintages/60TOTAL/316unused columns,3,144numeric/
948null candidate positions. Selected82comparison contains only43publications/
734native. Newton actualTOTALPDF3physical6 differs earlier unaccepted locator5;
right outer paper is not an extra template column. George prints22constituents
and a TOTAL-onlyPDF4physical1 plus ten unprinted slots. Simpson's complete2020
source prints23constituents. All literal source partitions remain publication-
specific without2024/current identity inference; earlier snapshots unchanged.

The `55views-v1` witness adds Kemper14, Leake19, Winston12 and Jasper original/
amended17 each, ten full original pages. All three native vectors independently
close each printedTOTAL. Combined55publication scopes contain891native across
vintages,55TOTAL/286unused,2,838numeric/858null candidate positions. Only39selected
county publications/655native enter the bounded82county comparison. Faint Jasper
windows remain broad entire-Senate reading windows, not exact numeric polygons;
matching publication counts establish no cross-vintage/current identity.

The `50views-v1` witness adds nine publications beyond41: Tunica12, Stone15,
Attala20, Amite21, Clarke23, JeffDavis original/amended17 each and Chickasaw
original/amended15 each. Their19full original pages retain every literal header
and three Senate vectors. Combined50publication scopes contain812native across
alternative vintages,50TOTAL/260unused columns,2,586numeric/780null positions.
Only35selected82publication scopes/593native enter the bounded countyCSV
comparison. Attala actualTOTALPDF3physical10 is accepted in the fresh native
ledger; earlier county-TOTAL proposal4 remains unchanged as an unaccepted aid.
JeffDavis forms literally printPresidential in the form heading while the selected
lower office isUnitedStates-Senate; the original county textJeffDavis and source
printed number substrings remain qualified. Amite's faint source prints21native
constituents, not an imported2024count. Broad reading windows remain provisional.

The `41views-v1` witness additionally reads all ten Hinds original2020Senate
pages2–11,108native constituents, oneTOTAL and oneunused template column.
All three source sums close75,467/23,661/910 at actualPDF11TOTALphysicalc10;
named places and source-printed numbered precinct labels/codes are retained.
No2024same-name/native/current identity equivalence is inferred.
Combined41publication scopes contain657native across alternative vintages,
41TOTAL/215unused,2,094numeric/645null positions. Selected82comparison includes
only28publication scopes/470native; remaining native counts stay unknown.

The `40views-v1` witness adds Quitman10, Franklin14, Jefferson amended12,
Clay amended14 and Humphreys original/amended13 each. Combined scope is
40publication views/549native across vintages/40TOTAL/214unused columns,
1,767numeric+642null candidate positions. Selected82scope is only27county
publications/362native. All five earlier witnesses' lossless bytes and
prior-source-object continuity validate. Jefferson amended uses a smaller
embedded table and independently reviewed original bounds; matching values
do not establish coordinate or publication identity. Humphreys first Belzoni4010
column is restored after the original machine inventory omitted it. Its
Isola suffix glyph transcribed2In remains explicitly font-ambiguous I/l;
the separate clearly printed four-digit2010 source code is retained without
a semantic/current-ID inference. Complete header rasters remain authority.

**Current receipt/method primary scope.** `prepare_current_receipt_sources.py`
verifies exact retained coordinator HTTP receipts and complete original entities,
including the actual FifthCircuit docket-query parent response and linked
September9,2026 two-page Document255-1. `shared-primary-references.json` keeps
requested/final URLs, status, headers, redirect list, UTC capture clocks and
raw/stored hashes/bytes while reusing original bodies read-only without duplication.
Own full2xgrayscale court-page rasters and complete original SOS HTML positions
are in `current-receipt-inputs.json`; `record_current_receipt_readings.py`
pins direct own reading of both court pages and FAQ4/9/10. The courtp2 affirms
the district judgment on Supreme Court remand in light of Watson. Current
ordinary SOS guidance prints November3 postmark / November10 receipt / five
business days, and scanning in-person absentee ballots for counting after
polls close. This scope is a dated primary publication reading, not exhaustive
later mandate/district docket/exception/UOCAVA/cure eligibility review. It
changes no historical candidate/method identity or conditional remaining pool.
MuPDF's two structure-tree warnings are retained as a processing observation;
both complete rasters/text returned and both full original pages were visually
read. No original bytes or PDF structure were repaired.

**Versioned original label and numeric reading aids.**
`extract_presidential_original_labels.py` reads unchanged original candidate
label crops for211 source pages; no line removal or vote/control/peer field.
It locates1871 unique source candidate names;28 missing names have independent
original visual readings. The46 source-label/rule review cards also include18
unresolved rule windows, retained in `presidential-original-label-manual-readings.json`.
`build_presidential_original_row_proposals.py --version v9` and
`build_presidential_row_repairs_v10.py --version v11` preserve earlier failed
outer-bbox projections. `repair_presidential_row_overlap_v12.py` records19
original-source rule repairs and verifies1899 non-overlapping candidate field
windows. A `source_row` in v10 and later is explicitly the presidential
candidate sequence number on that page, not an overall source-table row ID.
Numerical acceptance is separate. The retained v10 outer-glyph-bbox method
overlapped113 neighboring row pairs; v11 center-based proposals still merged
nine pairs where actual printed rules were missed. The original field-label
panels, v5 windows and complete Choctaw/JeffDavis panels supply the recorded
repairs, without any vote residual. These failures remain evidence.

`locate_presidential_party_rows.py` separately finds actual2024 printed party
labels aligned to the numeric line, using original candidate-name identity.
`build_presidential_party_row_repairs_v14.py` leaves39 missing/reused anchors
as explicitly marked full-field v12 fallbacks. It does not assign a candidate
from party alone or map2024parties to2026. Experimental v13/v14 fixed masks
remain unaccepted; a gray scan can still produce cropped/unrecognized glyphs.
`read_presidential_digit_variants.py` saves three declared masks/twoPSMs with
all raw literals, original windows and no-dilation rule-removal parameters.
Multiple masks/PSMs of the same Tesseract model are not independent source
witnesses. `native_tesseract.py` calls the installed primary C API with one
handle per task, clearing image/adaptive state between cells; raw outputs pin
library version and English-model hash. No dependency directory is retained.
The legacy `full_source_cell_box` in experimental outputs is a source reading
window; where `numeric_line_region` is true it is a numeric-line crop, not the
entire multiline candidate field or an approved boundary. Complete original
bytes/rasters remain available. `compile_presidential_workbench.py` inventories
all raw proposals/missing/conflicts without accepting them from county closure.
`review_presidential_ocr_against_manual.py` independently compares the bounded
Winston v15 mask aid with the direct complete-original117presidential numbers
in the exact same source/raster/header frame. It finds10 correct proposals,
one wrong proposal and106 unresolved fields, plus81 explicit original unused
blanks. `presidential-ocr-winston-diagnostic.json` rejects that experimental
consensus for acceptance; it was not run statewide. The original manual
Winston record supplies the accepted values. No failed mask aid is silently
converted to zero or promoted by a county sum. Full v4/v5 earlier artifacts,
v12/v14 locator/whole-page aids and original pages remain separate evidence.

The immutable `95views-v1` witness adds Tippah original/amended24 each, Warren original/amended23 each and Wayne22, with fifteen fresh complete original page readings. It retains 95 publication scopes / 1,887 native observations / 95 TOTALs / 481 unused columns and one separate administrative column; 5,949 numeric and 1,443 unused/null candidate positions. Selected82 subset is 73 publications / 1,521 native. Tippah TOTALphysical3 and Warren TOTALphysical2 are on PDF4; Wayne PDF4 is TOTAL-only. Fax margins outside the printed table are not columns; amendments are separate nonadditive observations. Nine publication-native scopes remain unreviewed.

The immutable `100views-v1` adds Lamar23, Lauderdale38, Lincoln30, Monroe26 and Neshoba27 source-native constituents from16 complete pages. Its100publication/2031native scope remains separately pinned. The later `104views-v1` adds Pearl River26, Pontotoc28, Scott23 and Yazoo23 from12 complete original pages and completes the named three-Senate-candidate grids across all104 actual publications. All2131 native observations across versions /104 TOTALs /536 unused /one administrative column are retained: 6708 numeric and1608 unused/null candidate positions. The selected82 amended-where-linked subset contains1765 native constituents and reproduces578691/709511/23152 exactly; alternative publication observations never add to that selected sum. `complete_all104_native_Senate_three_candidates` and `complete_selected82_native_Senate_three_candidates` express this narrow completion; broad `complete2020_native=false` retains open vendor/method/ballot/registration dimensions. All104 physical TOTAL source positions are separately recorded in `native-2020-physical-TOTAL-audit.json`, preserving earlier51 accepted/53 proposed locator metadata alongside actual fresh positions. Complete source PDFs retain other offices without a second derivative of their numeric fields.

`reconcile_2020_native_peer_v2.py` freezes exactly the announced38-publication peer scope as76 complete JSON/CSV bodies under `source/native-2020-peer-38views-v2/`, against own immutable104-view original-read flat input. It checks2277 positions:1554 native,114 TOTAL numeric and609 unused nulls, covering518 native observations across versions. Raw hashes/sourcekeys/PDFpages/physical ordinals/values/roles/whitespace-folded labels agree, with separate original render hashes and no claim of exact crop polygons or parsed-ID/current-geography equivalence. The original seven-view v1 witness stays unchanged. Capture uses a fixed filename whitelist, never a mutable glob that silently expands to an in-progress peer view.

The separate immutable2018 `2views-v1` witness preserves both Issaquena stage source objects and original flat fields. `record_2018_native_batch.py` extends from those exact pinned bytes, adding original Benton5 and Franklin14 constituents independently in each stage. The `6views-v1` scope contains48 native observations across stages,6 TOTALs,34unused;162numeric+102unused/null candidate positions. Benton actual TOTAL is PDF2physical6; Franklin PDF3physical4. Four special and two runoff candidates stay named/individual; unprinted party labels remain null and simultaneous regular ClassI rows are excluded. Full original pages, raw/raster hashes, source-column/header/candidate reading windows and each printed candidate TOTAL are retained. `validate_2018_native.py` checks variable source-native counts, all candidate vectors against county controls, physical positions/bounds/flat identities, prior witness objects unchanged and the separately retained Issaquena ordinal correction history. Other158 county-stage native scopes remain unknown, never zero-filled.

Immutable2018 `14views-v1` adds independently read distinct Noxubee8/Wilkinson9/Calhoun10/Sharkey10 native columns for each stage; all special4/runoff2 candidate vectors close own source TOTAL. Sharkey runoff actualPDF2 prints footerPage1; its failed empty machine grid and separate header-only original pixel-rule aid retain false text-stroke proposals and accepted physical reading rectangles, without candidate/polygon/current geometry inference. `16views-v1` adds both Greene13-native stages. Current scope16county-stage views/148native observations/16TOTAL/56unused,492numeric+168null positions;148county-stage native scopes remain outside it. All earlier2/6/14 source objects/bytes stay unchanged. Greene special Hyde-Smith1425 versus McDaniel1438 remain separate named candidate fields, never a forced party union or runoff electorate.

The physical2020TOTAL audit separately counts51 prior accepted columns (all agree),53 previously unaccepted locators (ten proposed ordinals differ), and55 nonnull proposals overall (eleven differ). The latter includes two old Coahoma proposals retained beside accepted8; original Coahoma proposed7 supplies the additional difference. These categories are not interchangeable and imply no candidate-vote change.

Immutable2018 `22views-v1` adds both original stages for Clay14, Smith18 and Tishomingo14 constituents. Current22source-stage/240native/22TOTAL/90unused scope has786 numeric+270 null positions on32 original pages. All four special/two runoff named candidate vectors independently close their source TOTAL and earlier county controls. Clay runoff actualPDF3 has UnionStar/Vinton/West-WestPoint then TOTALphysical4; earlier unaccepted machine locator3 remains in the unchanged county ledger and alongside actual native position metadata. No candidate-value repair, stage/source ID join or residual allocation. First2/6/14/16 witness objects/bytes unchanged; other142county-stage native scopes remain unreviewed.

Immutable2018 `28views-v1` adds independently read Carroll14/Choctaw13/Webster17 in each actual stage. Current28source-stage/328native/28TOTAL/128unused scope contains1068numeric+384null candidate positions on44 original pages, leaving136 county-stage native scopes outside it. Webster runoff uses a smaller embedded original grid with eleven physical columns; rejected broad machine geometry and header-only pixel-rule proposals remain distinct from accepted reading windows. Choctaw special PDF3 has Southwest Ackerman/West Weir/TOTALphysical3, with printed Hyde-Smith1550. All candidate vectors close exact-publication county controls; earlier frozen source objects/bytes remain unchanged. These are source-native observations, not cross-stage/current IDs or exact numeric polygons.

Immutable2018 `34views-v1` adds Tunica12/Jefferson12 named native columns in each stage, Claiborne special11 and runoff13:400native/34TOTAL/182unused on56 complete original pages,1296numeric+548unused/null+4literal-mark positions. Claiborne runoff PDF2 CountyPrecinct1-C and4-C print `X` in both Senate candidate cells; the special grid has neither column. The JSON `fields.source_marks` maps physical column to the literal `X`; `values` stays null. Flat CSV `raw_source_mark=X` is distinct from empty `votes`; previous rows have no mark. Both marked named columns remain native source observations, not numeric zeros, blank template slots or inferred administrative/status categories. Validator checks all four raw marks, numerical nulls and known-numeric closure without assigning a value or meaning to `X`. All prior source objects/bytes remain unchanged. Other130county-stage native scopes remain outside this review.

Immutable2018 `40views-v1` adds Quitman10/Stone15/Perry15 independently in both stages. The scope contains480native observations/40TOTAL/206unused on66 original pages;1554numeric+620unused/null+4literalX candidate positions. All vectors close own printed TOTAL and exact-publication county controls. Quitman special Espy1643 is the directly read ten-cell sum as well as printed TOTAL; no allocation. Perry four-digit header codes are parsed source-only substrings; no same-year/other-year/current geography join. Other124county-stage native scopes remain outside this witness; prior versioned source objects and bytes unchanged.

Immutable2018 `46views-v1` adds Montgomery15/Lawrence24/JeffDavis17 in each separate stage. Scope592native/46TOTAL/241unused/oneadministrative column on80 original pages;1910numeric+726unused/null+4literalX positions. Lawrence actualPDF2/3/4 carries24 named columns thenTOTALphysical3 onPDF4, with sourceA-Z/91labels intact. JeffDavis runoff PDF3 starts with administrative `PURGED VOTERS` explicit0/0, followed by six native columns thenTOTALphysical8; specialPDF3 has six native columns thenTOTALphysical7 and no administrative column. Neither native counts nor identity/electorate joins are inferred from another stage/year. Every candidate source vector closes its own printed control; earlier frozen source objects/bytes unchanged. Other118county-stage native scopes remain open.

Immutable2018 `50views-v1` adds Alcorn17/Attala20 perstage;666native/50TOTAL/251unused/oneadmin on88 original pages;2144numeric+756unused/null+4literalX candidate positions. First46 frozen source objects stay unchanged. `record_2018_native_correction_history.py` reproduces an explicit initial original-glance error: Alcorn runoff Pinecrest Espy98 failed native closure; full original row/enlarged actual cell directly prints96. `source/2018-native-correction-history.json` retains the failed17-value input, corrected one glyph, printedTOTAL, full original/render hashes and two derived reading crops with bounds/display scale. This was corrected before publishing50, without assigning a residual or changing any earlier witness. Other114 county-stage native scopes remain open.

Immutable2018 `54views-v1` adds Yalobusha11 andWalthall20 perstage:728native/54TOTAL/273unused/oneadmin on96 original pages;2342numeric+822unused/null+4literalX. Yalobusha actual2018PDF2 has11named columns andPDF3onlyTOTALphysical1; later-year counts are not substituted. `58views-v1` adds Chickasaw15 andCoahoma18 eachstage:794native/58TOTAL/291unused/oneadmin on104 original pages;2552numeric+876unused/null+4literalX. Chickasaw three-digit codes are exact source-header substrings only; Coahoma Bobo/FriarsPoint remain both first physical columns. All candidate vectors close own printed controls and prior frozen source objects remain unchanged. Other106county-stage native scopes remain outside this witness.

`reconcile_2018_native_peer.py` freezes exactly ten peer bodies (JSON+CSV for Issaquena/Benton/Franklin/Smith/Montgomery, each carrying both stages) under `source/native-2018-peer-10views-v1/`, with original/stored lossless pins. Own input is immutable58-view CSV, not peer values. All528candidate positions (342native+30TOTAL numeric,156unused/null) match at rawsource hash/FIPS/PDFpage/physicalcolumn/candidate/value/role and whitespace-folded source header,114native observations across ten separate stages. Peer keys prefix FIPS while own native CSV keys do not; only explicit component identity is compared, not byte-identical source keys/current IDs. Both original-render hashes remain separate; no exact raster/crop-box equivalence. Current Franklin literalMccall agrees; earlier peerMcCall witness remains untouched. These ten stage scopes do not close full2018native/method/geography gates.

`reconcile_2020_native_peer_v3.py` and `source/native-2020-peer-41views-v3/` preserve exact76existing38v2 bodies by reference to their owned lossless hashes, adding only6new bodies for Webster/PrentissOriginal/PrentissAmended after both original readings. The new41-source comparison contains565native/2475candidate positions:1695native+123TOTAL numeric,657unused/null. Own input remains immutable104-source original ledger; all values/roles/rawhashes/physicalpositions/whitespace-folded source headers agree. Prior38 JSON peer-comparison metadata remains its exact earlier captured declaration, not a claim that all41 are newly captured/current bodies. First7/38 frozen witnesses remain unchanged, and no source/year/current identity or raster/numeric-polygon equivalence follows.

`historical_native_calculator.py` reads only the lossless immutable104-publication2020 witness. `native-2020-calculator-settings.json` pins it and31 lossless compressed native target files under `historical-native-targets/`, each strictly below40MB, with both stored and exact decompressed CSV hashes/bytes. Preferred82 selects an actual linked amendment when present:1765native/578691Espy/709511Hyde-Smith/23152Edwards, pair1288202/named1311354. The other22publications each replace their own entire county in a separate82-parent partition, never additive or name-joined;134state groups=90preferred sensitivity+44replacement tie/A+1 cases. `native-2020-state-targets.csv`, `native-2020-county-contributions.csv` and the compressed native files contain134/10988/236510rows. `native-2020-local-targets.csv` has4264rows:2131separate-vintage native observations plus Harrison's one explicitly zero administrative observation, each with tie/A+1 local arithmetic. Unbounded selected-unit requirements, clipped displays/statuses, weights/net gains/contributions are separate. Current 2026 identities/legal thresholds and generic write-ins are not inferred.

Historical2020 low/base/high uses actual2022EACF1a (pair participation1 explicitly illustrative)/2024Senate county pair volumes/observed2020native pair volumes; normalized variants fix1288202 while retaining county mix. Distinct2018special/runoff county volumes and five historical preference anchors remain separate. Source2020native A shares are observed only for2020anchor; all other historical county A shares are explicitly uniform within2020source parents, not native joins/candidate effects/2026projections. JimmyL.Edwards Libertarian remains a named source candidate. Other-anchor named outsiders stay fixed at their actual county/state pools without being allocated to2020native units; generic scope remains unknown. `validate_historical_native_calculator.py` independently reconstructs source identities, all134 complete82-county partitions, allrow/weight/selected/local formulas and hashes. Its saturation-breakpoint slope integration does not import the calculator's bisection;3311140formula checks, maxshift error1.75e-15 and neterror1.03e-10. Broad historical method/geographic acceptance remains open.

Immutable2018 `62views-v1` adds Amite21/Tate20 in each stage:876native/62TOTAL/293unused/oneadmin on112complete original pages;2810numeric+882unused/null+4literalX. Amite outer fax/paper-border machine boxes are excluded, not unused source columns. Tate complete original eleven-column grids restore merged machine proposals; actual final-page TOTALphysical10 is followed by one unused slot. Both stage candidate sets remain separate; all earlier frozen source objects unchanged. Other102county-stage native scopes remain open.

Immutable2018 `66views-v1` adds Kemper14/Newton16 perstage:936native/66TOTAL/317unused/oneadmin on120original pages;3002numeric+954unused/null+4literalX. Kemper original literal Lynville is one n; Newton Duffee/Hickory physical separator restored from complete original header rules. The separate `70views-v1` adds Leake19/Winston12 perstage:998native/70TOTAL/339unused/oneadmin on128pages;3200numeric+1020unused/null+4literalX. Leake runoff Senate rows follow judicial candidate rows, which remain excluded; both complete original final pages show TOTALphysical9. Source four-special/two-runoff candidate vectors close their own printed controls; first66 and all earlier frozen source objects unchanged. Other94county-stage native scopes remain open.

Immutable2018 `78views-v1` adds Jasper17/Adams19/Holmes16/Humphreys13 in each stage:1128native/78TOTAL/377unused/oneadmin on144complete original pages;3614numeric+1134unused/null+4literalX. All four special/two runoff source vectors close own printed county controls and first70 source objects stay unchanged. Holmes merged machine column proposals are replaced by actual complete original eleven-column grids with literal A-Z wraps; Adams district-prefixed source headers are not geographic-ID parsing. Humphreys four-digit codes are literal source substrings; Isola suffix narrow I/l glyph remains explicitly ambiguous, not normalized from another source/year. Other86county-stage native scopes remain open.

`reconcile_2018_native_peer_v2.py` reads immutable own78 and reuses by exact hash all ten bodies from earlier2018peer10v1; only the two explicitly announced Yalobusha JSON/CSV bodies are newly captured under `source/native-2018-peer-12views-v2/`. All660positions (408native+36TOTALnumeric,216unusednull) across12separate stages/136native agree at rawsource hash/FIPS/physicalpage-column/candidate/value/role/whitespace-folded labels. Prior ten metadata declarations are not refreshed; v1 remains exact. Separate raster hashes and FIPS-prefix key representations remain qualified, no crop/current-ID or cross-stage join.

`source/reproduction-1042020-70stage2018.json` pins the successful complete offline rebuild log and exact104/70 original witnesses, earlier10stage2018 and41pub2020 peer witnesses, historical2020 arithmetic settings/independent validation, and reproducer bytes at execution. All26 then-current bounded main checks passed; this dated run predates later78-stage and12-stage reciprocal additions. Later reproducer edits or source scopes do not retroactively widen its proof.

Immutable2018 `82views-v1` adds Copiah19/Sunflower17 in each separate stage:1200native/82TOTAL/389unused/oneadmin on152complete original pages;3842numeric+1170unused/null+4literalX. First78 source objects unchanged. Actual Copiah nineteen-column scope and Sunflower literal two-digit source-header prefixes remain source-specific; extra outer-paper machine boxes excluded, not unused cells. These82stage views span41counties, not all82counties; other82of164stage-native scopes remain open.

Immutable2018 `86views-v1` adds Prentiss15/Union20 perstage:1270native/86TOTAL/403unused/oneadmin on160complete original pages;4064numeric+1212unused/null+4literalX. Prentiss literal slash/hyphen source labels retained. Union machine grid merged multiple columns or failed; all physical headers and four-special/two-runoff candidate rows independently read on complete originals, with header-only pixel-rule proposals retained separately. All candidate vectors close their own printed controls; first82 original objects unchanged. Other78county-stage native scopes remain open.

Immutable2018 `90views-v1` adds Tallahatchie21/Washington19 perstage:1350native/90TOTAL/407unused/oneadmin on168complete original pages;4316numeric+1224unused/null+4literalX. Tallahatchie actual twenty-one-column original scope and TOTALphysical11 are distinct from later-year geography counts. `record_2018_header_evidence.py` retains both original stage-page2 physicalc10 upright unchanged-pixel crops and separately marked3x display enlargements: literal Murphreesbore final e is visibly printed. `source/2018-native-header-evidence.json` pins original/raster/crop hashes/bounds; validator checks corresponding literal header. Washington original nineteen-column scope closes each own control. Prior86 source objects unchanged; other74stage-native scopes remain open.

Immutable2018 `94views-v1` adds Lafayette18/Oktibbeha20 perstage:1426native/94TOTAL/415unused/oneadmin on176complete original pages;4556numeric+1248unused/null+4literalX. Lafayette original header-y/machine-column gaps repaired from complete original grid, including final unused divider and runoff UnionWest4/Yocona boundary; actualTOTALphysical8. Oktibbeha actual twenty native columns and finalTOTALphysical10 remain independent of simultaneous congressional district row scopes/X marks. All six source vectors/county close; first90 source objects unchanged. Other70county-stage native scopes remain open.


Immutable2018 `94views-v2` preserves an explicit original-reading metadata correction: both Greene PDF3physicalc1 print `Mclain` lower-case l. `record_2018_greene_header_case.py` pins exact prior94v1 JSON/CSV/validation, both raw PDFs/full original rasters and unchanged-pixel upright header crops. Only two source header objects and six candidate label fields change; all values/roles/positions/source hashes remain exact. Earlier16/78/94v1 frozen witnesses are unchanged; validator permits only this recorded case transition in the ordered witness chain.

Current immutable2018 `98views-v2` adds Lowndes21/Leflore18 perstage, with184complete original pages:1504native/98TOTAL/421unused/oneadmin,4802numeric+1266unusednull+4literalX positions. Other66of164stage-native scopes remain outside review. Lowndes skewed/failed machine targeting is replaced with the complete original eleven-column physical grid, not another-year count. Leflore Nov6 source raw47d8b6e8606b617d690430c0bf927f3b9aaf0542e25f046ee83d27aa400d6b87 has eighteen Espy native cells summing5853 while printedTOTAL5863; otherthree vectors close185/2199/493. `source/2018-leflore-native-TOTAL-exception-v1.json` pins initial failure and complete original row crops; native-minus-TOTAL -10 remains unallocated. `controls.native_candidate_sums`, `printed_TOTAL`, `native_minus_printed_TOTAL`, `all_vectors_close=false` and `unallocated_source_disagreement` explicitly separate these scopes. No native glyph is changed to force closure.

`source/native-2018-witness-rejections.json` pins an inadvertent stale94-view freeze named98views-v1 after the builder failed Leflore closure. Allthree original/stored gzip pins and exact rejected snapshot are retained and verified, excluded explicitly from accepted witness coverage; no old snapshot is edited. `freeze_2018_native_milestone.py` now requires requested numeric scope, builder counts and validator counts to match before freezing. Valid98views-v2 is separate. `validate_2018_native.py` requires accepted snapshot-name/actual-source/count agreement, checks the exact known exception against original evidence, and reports false for all-reviewed-vectors-close rather than concealing the source disagreement.


Immutable2018 `102views-v1` adds Covington16/George22 perstage on194original pages:1580native/102TOTAL/451unused/oneadmin,5042numeric+1356unusednull+4literalX. George actualPDF4 is TOTAL-only physical1 followed by ten unused source template columns; it is not an extra native page. Covington finalPDF3 has five natives thenTOTALphysical6. The complete original George p3c9 literal Benndale is preserved in source and reproducible unchanged-pixel upright crop by record_2018_header_evidence.py. Existing source objects unchanged, including the pinned Leflore native-TOTAL discrepancy.

Immutable2018 `106views-v1` adds Pontotoc28/Simpson23 perstage on206complete original pages:1682native/106TOTAL/477unused/oneadmin,5360numeric+1434unusednull+4literalX. Pontotoc has eleven+eleven+six source-native columns thenTOTALPDF4physical7/fourunused; actual header suffixes remain literal, no parsed/current IDs asserted. Simpson has eleven+eleven+one native thenTOTALPDF4physical2/nineunused; judicial/constable X marks printed in unrelated contest rows are not imported into Senate cells. All new four-special/two-runoff vectors close own exact-publication controls, one earlier Leflore -10 remains unallocated. First102 source objects stay exact. Other58of164stage-native scopes remain outside this bounded witness.


Immutable2018 `110views-v1` adds Clarke23/Grenada12 perstage:1752native/110TOTAL/513unused/oneadmin on216complete original pages,5582numeric+1542unusednull+4literalX. Clarke special p3 physicalStonewallDist3/Dist1 divider1904 restores eleven printed columns where machine merged them; original literal Souinlovie retained with upright source-header crop. Four special candidates stay individual, including Bartee877 versus Espy1387 as separate fields. Grenada actual twelve native observations perstage endPDF3c1 thenTOTALphysical2/nineunused; machine misidentification of unrelated congressional IrvingHarris as KamalaHarris is diagnostic only, excluded from accepted Senate fields. Earlier106 source objects stay exact; Leflore -10 remains unallocated, other54stage-native scopes remain open.


Immutable2018 `114views-v1` adds Panola22/Marion22 perstage:1840native/114TOTAL/553unused/oneadmin on228complete original pages,5858numeric+1662unusednull+4literalX. Both actualPDF4 pages in both counties are TOTAL-only physical1 with ten unused template columns. Panola runoff machine MikeEspy499..559 office-band target rejected for original candidate rows559..621/621..678; Marion special p3 machineBartee757..812 was regular ClassI O-Hara and rejected for actual special869/870 band. Marion special p4 missing blank dividers restored from original eleven-column physical header, not source-count inference. Every new candidate vector closes exact-publication printedTOTAL/county controls. First110 source objects unchanged; Leflore -10 and rejected stale98v1 remain explicit. Other50of164stage-native scopes remain outside bounded review.


Immutable2018 `118views-v1` adds Marshall24/Neshoba27 perstage:1942native/118TOTAL/579unused/oneadmin on240complete original pages,6176numeric+1740unusednull+4literalX. Marshall several merged machine native/blank columns are restored from original physical header-grid lines with unfiltered header-only pixel probes retained; beat prefixes remain literal, not asserted uniqueIDs. Neshoba original fax/scanner stroke1692..1694 is outside the actual eleven-column source grid and not an extra native/unused column. FinalPDF4 shows five native thenTOTALphysical6/fiveunused; all four-special/two-runoff vectors close original controls. Prior114 source objects unchanged; knownLeflore-10 remains unallocated, other46stage-native scopes open.


Immutable2018 `122views-v1` adds Lamar23/Wayne22 perstage:2032native/122TOTAL/617unused/oneadmin on252original pages,6458numeric+1854unusednull+4literalX. Lamar actualPDF4 has one Sumrall native thenTOTALphysical2/nineunused; WaynePDF4TOTAL-onlyphysical1/tenunused. All six vectors/sourcecounty close their exact-publication controls, no2018-to2024/native ID join. `126views-v1` adds Tippah24/Warren23 perstage:2126native/126TOTAL/651unused/oneadmin on264original pages,6752numeric+1956unusednull+4literalX. TippahTOTALPDF4c3 and WarrenTOTALPDF4c2 retained; Warren allthree runoff machine office-band MikeEspy targets rejected in favor of direct original candidate rows. Every new source vector closes county controls; first122 objects exact. Other38of164stage-native scopes remain open; Leflore-10 still unallocated.

`source/reproduction-1042020-118stage2018/completion.json` pins the successful exit0 full offline rebuild through104actual2020publications/118stage2018 scope and28 then-current bounded checks. Exact execution script saved before launch; eleven output/implementation/validation/manifest bodies retained as complete gzip bytes, plus final38519B log and104/118 input witnesses. Run manifest log entry was recorded before final stdout; final log pin explicitly supersedes that pre-completion entry. New fourth-batch manual code/rasters present as assets at that time were not yet imported into118-stage coverage. Later126-stage additions and new29th receipt-validation check do not retroactively widen the full run.

The immutable `native-2018-130views-v1` witness adds complete original Scott and
Yazoo November 6 and November 27 grids: 130 distinct stage publications, 2,218
native observations, 130 separate TOTALs, 687 unused columns and one
administrative column; 7,040 numeric, 2,064 null and four literal-X candidate
positions. Both counties print 23 native columns per stage; 34 of 164 stage
native scopes remain unreviewed. Scott's original runoff Ludlow glyph is 228:
the initial manual 226 and failed sum are preserved by
`2018-scott-initial-reading-v1.py.gz` and its pin, with source-row evidence and
history in `2018-scott-original-reading-correction.json`. This is an original
glyph correction, not residual allocation. Yazoo machine proposals omit/merge
native columns and have no usable page-3 fields; full original readings and
header-rule proposals establish physical source positions. Scott's literal
truncated `Beat\n3/Cooperville/Springf` is retained without expansion. The
Leflore November 6 Espy native-minus-printed-TOTAL difference remains -10,
unallocated. Older immutable witnesses, including the explicitly rejected
98-view-v1 snapshot, remain unchanged.

`native-2018-134views-v1` adds Lincoln30 and Monroe26 native observations per
stage; `138views-v1` adds Itawamba28 and PearlRiver25; `142views-v1` adds
Hancock25 and Pike25. Each count comes from its actual original grid, not a
2024 count. Each added candidate vector closes its printed stage TOTAL and
county control. Pike's original PDF2c11 Espy glyph is168, superseding initial
manual158; exact initial builder and full original row reread evidence remain
under `source/2018-pike-*`. `142views-v2` separately repairs Tunica's source
header to `Mhoon Landing`: only two PDF2physicalc2 header objects/six flat
candidate labels change. All previous witnesses remain exact. The history
`2018-tunica-header-correction-v1.json` pins prior142v1 and own complete-original
rasters/upright unchanged-pixel crops; no vote/role/position/current-ID change.
The142-view scope has2536 native observations across distinct stages,
142TOTAL/753unused/one administrative column,8030numeric/2262null/four literalX
candidate positions;22 of164 stage-native scopes remain outside original
review. The known Leflore November6 Espy5853 versus printed5863 difference
remains unallocated.

`native-2018-146views-v1` adds original Forrest34 and Jones37 native columns per
stage, each actualPDF2–5. It contains146 stage publications/2678 separate native
observations/146TOTAL/783unused/one administrative column and8468numeric,
2352null and four literal-X candidate positions;18 stage-native scopes remain.
All new vectors close their exact printed source and county controls. Jones
runoff PDF5c2 Espy visibly182 supersedes first manual152; failed builder bytes,
all four complete original Espy row strips and correction history are pinned
under `source/2018-jones-*`, reproduced by `record_2018_jones_evidence.py`.
Jones runoff machine header merges are repaired only from complete original
physical rules, retaining unfiltered header-stroke proposals separately. No
unrelated judicial X mark is transferred into the selected Senate rows.

`native-2018-150views-v1` adds complete original Bolivar28 and Jackson32 native
columns per stage. It preserves150 stage views/2798 native observations,
150TOTAL/791unused/one administrative column,8840numeric/2376null/four literalX
candidate positions. Fourteen of164 stage-native scopes remain. The actual
runoff route/source-ID `sos-2018-runoff-county-jackon` remains literal; the
original PDF header independently prints Jackson County. Jackson special
PDF3c7 Hyde-Smith visibly690 supersedes first manual590; failed first-builder
bytes/all three original row strips/history remain pinned under
`source/2018-jackson-*`. All new candidate vectors close their own printed
TOTAL and county control; no residual allocation, office pooling or cross-year
geographic join.

The immutable `native-2018-164views-v1/snapshot.json` completes the narrow
named-Senate source-native review of all164 actual county-stage publications:
3545 native observations across separate electorates,164 TOTAL,842 unused and
3 administrative columns;11126 numeric,2530 unused/null,6 literalX positions.
Nov6 has1771 native columns; Nov27 has1774 including three X/X columns
(Claiborne two, Rankin Mullins one). LiteralX numerical nulls are unknown,
not zeros or inferred eligible/administrative geography. Harrison Invalid
Addresses9999 is separately administrative in each stage, JeffDavis PURGED
VOTERS administrative in runoff. Their explicit zeros remain source evidence.
Hinds110 perstage differs from2024Hinds108; no crossyear join follows.
`complete2018_named_candidate_native_source_review=true` expresses only this
narrow scope; broad method/ballot/registration coverage stays separately scoped.
Earlier snapshots and rejected stale98v1 remain byte-exact; GreeneMclain and
TunicaMhoonLanding histories change only documented source-label derivatives.

`native_2018_calculator.py` reads that exact immutable164 witness and produces
180 separate state groups,319050 native rows in18 lossless gzip files with
original/stored byte/hash pins,14760 county contributions and7096 local rows.
Every state keeps all82 parents/allpriority and nonpriority native observations.
Three X/X native observations have unmodeled/null arithmetic rows, not imputed
weights; local statuses include6 unknown and6 no-positive-pool target rows.
For known numerical Nov6 cells, Espy386732/Hyde389995 pair776727, separately
Bartee13852/McDaniel154878 named945457; county certification945467 differs by
LefloreEspy10 unallocated. Nov27 known420819/486769 pair/named907588 closes
printed totals without asserting X=0. Denominators explicitly describe the
known numeric source model, not all valid marks or final2026 ballots.

Within each stage, nine volume variants include own observed native pair,
historical low2022EACF1a with illustrative pair participation1/base2024Senate/
high2020Senate county volumes, the other2018stage county mix and explicit
common-volume normalizations. Five preference anchors use observed native
shares only for matching stage; other historical county pair preferences are
uniform within that source2018 parent as explicit conditional assumptions.
No native crossyear join, lower preference, candidate effect or2026projection
is inferred. All outsider candidates remain individually named, with source
party fields unprinted/null on2018recaps. No union of Bartee/McDaniel pools.
Other-anchor outsider county/state pools fixed, not silently native-allocated.

Tie `(B-A)/(2*(A+B))` and A+1pair margin `+0.005` share shift remain distinct
from a legal outcome. Bounded statewide shifts explicitly clip shares[0,1].
Selected-unit-only requirements retain unbounded share/status and clipped
display separately, with every other modeled known source unit fixed at the
explicit scenario/anchor and outsiders fixed. Allnamed majority cushion is
pairnet−namedother; majority requires A pair share>(T+O)/(2T). Strict plurality
also requires beating each individually named rival; Nov6 majority/top-two and
Nov27 separate runoff electorate remain distinct, current2026plurality separate.
Generic/validwritein unknown scope is not a numeric zero. The independent
`validate_native_2018_calculator.py` reconstructs frozen source cells/weights/
local-selected-state-contribution formulas and integrates clipping-breakpoint
slopes without importing the author solver:4462920 formula checks, maximum
shift error2.22e−15 and achievednet error7.28e−11 votes. This arithmetic is not a
calibrated probability or current reporting geography approval.

## Complete retained-packet field scope and later reciprocal versions

`printed-field-source-scope.json` inventories all352 retained county originals /3238 pages. `source/original-page-scope-overviews.json` pins41 complete-original raster overview cards and each page's source hash/layout slot. These cards were inspected for packet structure; they are not numerical transcription authority. Full originals and the source-specific manual ledgers remain authority for candidate/control glyphs. The locator inventory includes allpages but keyword failure is never evidence of absence.

Located required additional views comprise15 county candidate/generic/method summary panels,14 ballot/registration statistics panels,45 ES&S native profiles/905 required numeric fields,3 SEMS E-013 named county presentations, and58 Union BP-009 administrative split-ballot-style rows under20 parentTOTALs. The source-specific availability/nulls are retained. Original2020 ballot-measure under/over rows and unrelated offices remain intact in original bytes without an unnecessary numerical derivative; they are not Senate methods.

`record_lincoln_2024_controls.py` retains exact prior14summary/12statistics bodies, then reads actual LincolnPDF9–11. Its ballots15898 equal both contest totals; registration0 is unusable; residual172Senate/69Pres remains unclassified. `record_montgomery_2024_controls.py` separately retains prior13statistics bytes and actual MontgomeryPDF3 ballots885/registered6291/blank1/turnout14.07%/ED14of14. Its statistics clock10:24AM differs summary10:25AM; namedSen4349/Pres4424 exceed885. No cause, common electorate, residual allocation or repaired ballot volume is inferred. These later bodies do not mutate the older14/12 availability/peer witnesses.

`supplemental-2024-summary-readings.json` preserves direct original BolivarPDF4, GrenadaPDF9, ItawambaPDF12 E-013 named11candidate vectors and each printedTotal. They are repeated county presentations, nonadditive. Missing generic/method/ballot/registration fields remain null.

`union-split-ballot-style-readings.json`/`union-split-ballot-style-fields.csv` preserve every actualPDF8–10 BP-009 split/style/blankParty/TotalVoters row, literal printed codes/names and separate parentTOTALs. NAS is the literal visible label, not silently parsed as NA5. All58 splits sum17058, matching20parentTOTALs and printedGrandTOTAL, separately26 below ES&Sregistration17084. Definition/status equivalence is unavailable. No candidate values are printed by split; pair weights, tie/A+1 targets and selected-only break-even remain unknown_candidate_allocation/null, not0 or no-positive-pool. Source-position keys do not join SEMS/vendor/current2026 geography.

`reconcile_2024_all11_complete_peer.py` uses immutable own82witness and exact read-only peer gzip `data/turnout/source/2024-preferred-all11-source-fields-v1.json.gz`, stored96203B SHA256d066e45bebca7ba66163989165a430164f5b84cef61d9e2cda7e4bc4e1d23b6b; raw2048366B SHAb2a7e234eeb226bd13f35d3a4c32c867f88f7d59a680ec059a7378c036f1fbae. New immutable `source/2024-all11-complete-peer-v1` verifies24926positions:19096native,902TOTAL,4807unusednull,121Kemperparallel. Twenty-two Holmes hyphen-wrap label representations remain explicitly unequal; no crop/raster/currentID equivalence. The126 older Perry/Tunica omitted blanks are now explicit peer null only in this newer body; older through33v4 bytes/scope remain unchanged.

`reconcile_2018_native_peer_v3.py` freezes42 actual peer derivative bodies from the explicitly listed20two-stage counties plusLefloreNov6, after own164original readings. Its separate immutable41-stage witness checks578native/2530candidate-or-null positions:1752native,124TOTAL,654unused. Values/roles/rawhash/FIPS/physical positions/whitespace-folded source labels agree, with separate render hashes. No claim of whole164 independent peer replay. Earlier10/12witnesses retain exact original metadata and body pins. All2018 literalX marks and Leflore−10 remain explicit unmodeled source limits.

Final validation defines complete_owned_question / complete_native_question as completion of these retained available original-source research scopes and conditional arithmetic. Unprinted fields remain unavailable, not invented. Independent historical peer replay remains bounded41/1042020 and41/1642018; unknown future finalballot/feed/geography/legal evidence and coordinator887acceptance remain external qualifications, not silently self-approved or worker-owned completion prerequisites.

## Complete-field primary proposal v2 and final rebuild

`build_native_priority_v2.py` reads the unchanged lossless v1 proposal and own immutable82allfield originals, never peer numeric values, and emits `native-priority-contract-v2.json`, `native-priority-source-fields-v2.csv` and `source/native-priority-v2/snapshot.json`. All2266columns/24926candidate-or-null fields are preserved, including437unused and11Kemperparallel columns. Ordered1736native keys,887priority/849nonpriority arrays,82parent all-child/priority-child maps and77priority authorities exactly preserve v1 arithmetic. All11native totals preserve sourceSen1215400/Pres1228007 versus separately certified1215401/1228008, with unallocated TunicaPinkins1/Harris1. Label/optionalID metadata universes remain distinct; no geometry/currentID inference.

`validate_native_priority_v2.py` does not import the producer. It checks all24926fields/source roles against the separately pinned peer all11 body after both original readings, independently sorts/recomputes every1736rank/prefix/candidate vector and integer887crossing. Holmes source-wrap aliases remain explicit. Coordinator acceptance/current2026approval both false. `freeze_native_priority_v2_fields.py` adds an immutable companion `source/native-priority-v2-field-evidence-v1/snapshot.json` with17 exact derivative bodies for required available controls, source/peer evidence and v2 validators. Both original/stored hashes and sizes are checked; large originals reused by existing exacthash, not duplicated. V1 and all old witnesses unchanged; future revisions require new immutable versions.

`run_final_reproduction.py` executed the complete original offline reconstruction and froze `source/reproduction-complete-original-v1/completion.json`, its exact execution script/log,104/164/82original input witnesses and7output bodies losslessly. It exited0 with35 then-current main checks. Log finalhash supersedes the then-running log entry in that dated run manifest; final outer `validate.py` separately audits current files. The later v2/field-companion integration is a separately validated extension; the frozen earlier rebuild is not rewritten and does not falsely include later executions. Repeating current `reproduce.py` reconstructs the integrated package offline using retained originals/manual ledgers; optional `--ocr` repeats diagnostic original-pixel OCR, not accepted values imported from peers. No acquisition/cache/dependency directories are required for offline reuse.

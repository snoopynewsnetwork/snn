# South Dakota baseline schema and reproduction

This package is historical evidence and conditional arithmetic, observed 2026-10-19 UTC. It contains no 2026 vote observations, turnout prediction, inferred candidate effect, inferred lower preference, calibrated probability, approved geographic crosswalk or demonstrated live cadence. The actual turnout peer is `ad252512-9d56-42ca-adf2-f81a21cbe63e`; comparison is read-only. Coordinator acceptance is external.

## Files and units

| File relative to `data/baselines/` | Grain and meaning |
| --- | --- |
| `../county-baselines.csv` | 198 signed county/contest rows: all 66 counties for 2024 president, 2022 other-seat Senate/midterm, 2020 same-seat Senate. A is historical Harris, Bengs DEM, or Ahlers DEM; B is historical Trump, Thune or Rounds. |
| `county-candidates.csv` | 594 county/candidate rows, complete printed candidate columns, election-specific party, integer votes, source page/line/raw line. No non-Republican aggregate is called Democratic. |
| `native-2024.csv` | All 691 presidential native workbook rows, all 66 worksheet parents, all four original tickets, original order and exact literal labels. Explicitly unofficial, total 428,728. |
| `native-2022-public.csv` | All 687 Senate workbook rows/66 parents, Bengs DEM/Lesnar LIB/Thune REP, 348,020; all 66 footers agree signed state controls. Source still labels itself unofficial. |
| `native-2020-public.csv` | All 693 Senate workbook rows/66 parents, printed Rounds REP then Ahlers DEM; 420,178 versus signed 420,219. |
| `native-2022.csv` | Separate original PDF: 679 rows/65 parents. All available county controls agree. Its 66 Senate pages include Minnehaha continuation and omit Yankton entirely. This is not a second electorate to add to the public workbook. |
| `native-signed-differences.csv` | Every county/candidate public2024-minus-signed difference; no allocation. |
| `public-senate-signed-differences.csv` | All public2020/2022 county/candidate differences, without allocation. |
| `turnout-registration-controls.csv` | 198 county/election book controls: Votes Cast, turnout-table registered, separate active and inactive registration, as-of date, source page/line/literal. |
| `priority-contract.json` | Complete sorted order and constituents for every native year, with 2024 primary contract; signed county concentration is separately labeled sensitivity. Integer minimum80 proofs. No certified native robustness/current geometry approval. |
| `scenario-settings.json`, `state-targets.json` | 21 full-state settings and 42 tie/A+1 targets, historical full candidate totals, all-candidate denominators and separate hypothetical current named pair. |
| `unit-targets.csv.gz` | 17,756 unit/target rows; all 66 county or all native units in every relevant calculation, including units outside priority. |
| `selected-unit-break-even.csv.gz` | 17,756 selected-unit conditional solutions; every other unit fixed at its stated historical share and volume, additive shift zero. |
| `historical-input-example.json`, `live-input-example.json` | Editable offline inputs for historical and remaining-vote calculators. |
| `live-synthetic-scenarios.json`, `bounded-synthetic-scenarios.json` | Saved meaningful input/output cases; arithmetic, not empirical calibration. |
| `peer-reconciliation.json`, `validation.json`, `asset-manifest.json` | Independent read-only peer comparison, substantive checks, complete owned inventory plus read-only original references. |

## Identity, source positions, missingness

County FIPS are five-character strings, from the retained public Census county inventory. South Dakota is state46. Oglala Lakota is46102; historical Shannon46113 is not an extra county or a native geometry join. All county sources used here name Oglala Lakota. The Census name/code change was effective May1,2015: [primary notice](https://www.census.gov/programs-surveys/geography/technical-documentation/county-changes.2010.html).

Native `native_key` is an analyst source locator: `sd:YEAR:pres|senate:46xxx:sheetN:rowN`; it is not an official numeric reporting ID. `sheet` is one-based workbook order, `source_row` the actual Excel row, and `sheet_member` the literal ZIP worksheet member. `source_candidate_cells` lists exact addresses in printed candidate order. PDF keys use page and numeric text-line position. `pdf_page`/`pdf_line` are one-based; full original text and XML remain. No native equivalence across years is inferred. Turnout's 2020/2022 public keys use `public-sheetN`; the exact original hash/member/row/county tuple establishes a source-locator bijection, not a geographic crosswalk. The 2024 key strings agree exactly.

All raw candidate counts and source controls are integers >=0. Blank CSV cells are unavailable/not separately published; they are not zero. In JSON the corresponding unknown calculation results are null. `official_native_id` stays blank. `method_label=literal_absentee_unit` and `method_scope=source_label_absentee_unsplit` mean the source literal contains Absentee; `native_label` separately preserves its complete spelling, whitespace and punctuation, including 2020 Yankton `Absentee `. Other rows have `method_label=not_separately_identified`, `method_scope=unavailable_not_assumed_election_day`. Place-like or VP labels do not prove a polling site, residence precinct, vote center, municipality, VTD or polygon. No numeric method IDs, separate early/mail/provisional split or source counts for missing methods are fabricated.

The worksheets publish candidate votes but not native ballots cast, registration, blank ballots, undervotes, overvotes or generic/valid write-in columns. Those fields remain unavailable. The [2026 official precinct manual](https://sdsos.gov/elections-voting/assets/2026%20Documents/2026PrecinctManual.pdf), PDFp15, excludes ordinary write-in votes from counting; the federal absentee write-in ballot is a distinct ballot mechanism, not evidence of another countable candidate. The original canvasses' printed candidate field is retained without treating absent invalid-mark categories as zero.

`votes_cast_source_label` is the book's Votes Cast, not contest votes. `turnout_table_registered` is the book's active-denominator turnout table. `registration_active` and `registration_inactive` come from separately dated registration tables. Turnout-minus-registration-active is0 in2024, +4 in2022 and -11 in2020 statewide. County differences remain. The Votes Cast-minus-named-contest residual is unclassified, not automatically an undervote, blank or overvote.

## Denominators and calculations

For each historical source row: `pair_votes=A+B`; `all_named_votes=A+B+other_named_votes`; pair participation is `(A+B)/all_named_votes`. Pair share is `A/(A+B)`. Net votes are `A-B`. Pair margin percentage points are `100*(A-B)/(A+B)`; all-candidate margin percentage points use `all_named_votes`. The full named opposition field and parties remain in the candidate and complete cell artifacts. Election-specific party identities never redefine 2026 Bengs IND as D.

County scenarios cross each independent preference anchor2024/2020/2022 with low2022, base2020 and high2024 **observed county all-candidate volumes**. A county's historical pair participation comes from the preference anchor, so its scenario pair volume is selected county all-candidate volume times anchor participation. Each other historical candidate keeps that county's anchor all-candidate share. Native scenarios have their own election's observed native preferences/mix and pair participation. `observed` uses unchanged source votes; low/base/high uniformly scale that source mix to the signed historical statewide all-candidate controls348020/420219/428922. The latter are hypothetical historical-volume sensitivities, not corrected native source counts, certified residual allocations, cross-year native joins or 2026 projections. Scenario weights are explicitly declared and preserved in settings and each target row.

Let T=sum scenario pair volumes and M=sum T_u*(2*s_u-1). The unbounded A-share shift for pair margin m is `(m*T-M)/(2*T)`. Tie m=0; illustrative A+1 margin m=.01. With fixed weights and **no clipping**, A+1 adds0.5 share percentage points. +1 share point changes the pair margin by+2 points and net by `.02*T_u`. A+1 margin is `.01*T` net votes, not one net vote. The full all-candidate margin cushion is `.01*T/all_named_total` times100; it is smaller when other candidates exist.

Shares are clipped to[0,1]. `bounded_shift` solves sum `T_u*(2*clip(s_u+delta)-1)=m*T` by bisection with explicit bounds. We preserve the unbounded result, whether it clips, the feasible bounded result, clipped-unit count, baseline-already-winning flag, and impossible/no-positive-pool statuses. A+1 need not be exactly0.5 additional share points after clipping. Negative tie shifts remain when a baseline already wins; no “improvement needed” floor silently replaces them. Actual legal outcome remains plurality over **every** countable candidate under [SDCL12-20-39](https://sdlegislature.gov/Statutes/12-20-39); a pair tie is not a win and does not replace a multi-candidate legal threshold.

Selected-only threshold is `q=(1+(m*T-other_fixed_net)/selected_pair_volume)/2`. Preserve q outside[0,1], with secured/impossible status and a separately clipped display. Every other unit's baseline contribution, fixed elsewhere shift and total volume are explicit. These county/native targets are sufficient combinations under assumptions, not individually necessary winning conditions.

The separate hypothetical2026 named pair is **Brian L Bengs Independent=A; Mike Rounds Republican=B**. It assumes a repeat of a stated historical pair preference and pair volume, and exactly those two current choices. It carries no historical Oliver/Kennedy/Lesnar votes or effects into Bengs, and gives that named pair its own all-candidate denominator T. Current identities are from the [official county publication ballot](https://www.lincolncountysd.gov/DocumentCenter/View/1989/Sample-Ballot-2026-PDF) linked by its [elections page](https://www.lincolncountysd.gov/159/Elections), primary web inspection2026-10-19, and the retained current SOS general-list status rows. Original county PDF downloads returned404/empty here; the successful parsed primary web observation and failed receipts are retained separately. No current ENR numeric IDs are approved.

For live inputs, `counted` maps every declared candidate to fixed nonnegative votes. `remaining` contains named unit keys, `remaining_total` across all candidates, explicit remaining other-candidate shares, and `a_pair_share` for the remaining pair only. Omitted other shares mean an explicitly assumed zero remaining share. Each other key must be a declared separate candidate. Other shares must be0..1 with sum<=1; out-of-range pair preferences are explicitly clipped. Unknown pools/preferences and negative pools are not coerced to zero. Correct final pair denominator is countedA+countedB+remainingPairPool; final all-candidate denominator includes all fixed counted others and forecast remaining others. Required remaining A share is `(m*FINAL_pair - counted_A_minus_B + remainingPairPool)/(2*remainingPairPool)`. Selected-only live holds all other stated remaining contributions fixed. Final plurality compares all separate named candidates. No probabilities are produced.

## Provenance and reconstruction

Originals remain once, read-only, in `../news/` and `../turnout/source/`, referenced by exact hashes/bytes/receipts; independently acquired additions are here. `shared-news-receipts.json` preserves the full parent/source/public-POST chains, request controls and failed attempts. `peer-original-receipts.json` and `senate-public-original-receipts.json` snapshot exact original receipts. Their referenced parent receipts/bodies remain in turnout/source and are pinned by the asset audit. `original-reference-index.json` links PDF text to exact originals. Raw HTTP entity hashes refer to complete decoded response entities; stored gzip hashes are separate. HTTP cache headers, retrieval UTC, final/requested URLs and redirects remain; publisher/generated download clocks are not inferred source update clocks or live cadence.

`workbooks-complete-cells.json.gz` and `senate-public-workbooks-complete-cells.json.gz` retain full workbook cells, types, raw shared-string indices, resolved literal values, XML, ZIP members/CRCs/member hashes and all worksheets, including unrelated offices in the received originals. `candidate-header-presentation.json` preserves the actual statewide2024 all-race export's incorrect D7 Trump/E7 Trump1 headers, which omit Oliver. They are never silently repaired or mapped by numbers. Native2024 and Aurora exports correctly name all four. Complete original PDFs and extracted text preserve unrelated tables without multiplying unrelated demographic derivatives.

The 149141181-byte2020 county PDF is retained as one exact gzip stream split into four ordered parts below40000000 bytes. `../news/reconstruct_evidence.py sos-2020-general-county-canvass --output /tmp/sd2020.pdf` verifies per-part hashes, whole stored gzip hash/size and the full raw entity hash/size. Do not request a nonexistent standalone asset or truncate a part. The four2024 county PDFs are separately retained lossless gzip; the largest stored object is33160051 bytes. SHA256 checks use exact bytes; no source rescaling, simplification or key deduplication is performed.

The asset manifest inventories every owned file other than itself (self-hash excluded to avoid circularity), plus read-only source/receipt references and strict size bounds. It includes validation.json and this schema. Validation can verify the manifest without rewriting it. Original transport failures have no admitted vote asset; HTTP200 setup/zero is not genuine counts.

## Offline reproduction

Run from repository root with Python3 standard library and installed Poppler `pdftotext`/`pdftoppm`. No retained dependency/cache directories and no network required for reproduction:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/extract.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/controls.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/bbox22.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/public_senate.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/enrich.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/check_preflight.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/render_evidence.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/build.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/compare_peer.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/write_report.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/validate.py --write
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/asset_manifest.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/baselines/scripts/validate.py
```

`check_preflight.py` actually runs retained coordinator preflight logic with only write destinations redirected into this owned directory, then checks full tables/controls against the read-only preflight JSON. Independently authored extractors are separate. `acquire.py` is an optional original-download recipe, not an unattended collector: it records complete responses and transport failures. Its live rerun is not needed to reproduce pinned historical workbooks. The turnout peer's retained `acquire_historical_native.py` reproduces the actual2020/2022 observed history/client/public form-control route; its original form fields and chain are pinned, with no guessed race IDs.

For a customizable historical selected county, run `calculator.py historical-input-example.json --historical --selected 46099 --elsewhere-shift 0` from the baselines directory using `scripts/calculator.py` as the executable path. For live arithmetic run `python3 scripts/calculator.py live-input-example.json`, or add `--selected selected`. Edit only a copy of inputs to change volumes/preferences/remaining pool. Unknown and bounded feasibility statuses are part of the result.

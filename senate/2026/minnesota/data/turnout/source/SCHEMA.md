# Minnesota turnout data and provenance

The analysis is pinned to the original SOS workbooks referenced by [shared-originals.json](shared-originals.json). Paths in its `shared_path` are relative to `senate/2026/minnesota/`; they are read-only shared assets, despite the legacy `.html.gz` suffix. One gzip decompression reconstructs the exact XLSX ZIP or PDF bytes; original and stored hashes and sizes are separate. No original is duplicated here. Each artifact is strictly below 40,000,000 bytes. The source landing → spreadsheet-index → media-file chain is recorded in [source-chain.json](source-chain.json). [acquisition.json](acquisition.json) retains this worker's requested/final URLs, UTC, status, headers, raw/stored hashes and content classification. Earlier shared captures have requested/final URLs rather than a full intermediate redirect trace; that limitation is explicit. A 200 challenge is evidence of an access failure, never an empty election.

## Source scope

`Precinct-Results` is a list of SOS precinct / Vote Tabulation District result rows. `VTDID` is a nine-character source identifier; `PCTCODE` is a four-character code unique within county. The actual `Counties` worksheet supplies the 87 county codes/names and five-character FIPS. All retained rows verify `VTDID == county_fips + PCTCODE`; no sequential-code formula substitutes for that table. [workbook-context.json](workbook-context.json) records exact worksheet ZIP paths, row positions, source column letters, header mapping, all Notes/Fields/Counties cell values/types/formulas, and excluded empty/footer rows. The original workbook retains all sheets, unrelated offices, statistics and source positions. No second derivative of every unrelated table is required or implied.

2020 repeats the literal header `TABMODEL` in G and R. Derived field names `TABMODEL__G` and `TABMODEL__R` preserve both; G is populated in ordinary rows while R can be blank. The original labels and column positions survive. Other source columns retain their original spelling. Missing cells are empty in CSV and null in context JSON; literal `no data` remains literal. A source numeric zero is `0`, never an imputed replacement for missing data.

## Data files

| File | Grain / meaning |
| --- | --- |
| `../county-turnout.csv` | All 87 county parents, ordered by all five 2024 Senate vote fields. Contains every requested candidate field under `{year}_{source_field}`, exact shares/cumulative counts and flags, source-scope D/R/other groups, voter statistics and blank unavailable categories. |
| `native-{year}.csv.gz` | All 4,103 / 4,103 / 4,110 source precinct rows for 2024 / 2022 / 2020, in source order. Retains all native identity/district/equipment/method fields and 2024 Senate + president, 2022 governor, 2020 Senate candidate fields. `source_row` is the original Excel row; each source column is identified in workbook context. |
| `county-controls-{year}.csv` | Native sums by source county, preserving each candidate, total, method and registration count separately. `COUNTYCODE` is the source 1–87 code, distinct from FIPS. |
| `municipal-controls-{year}.csv` | Alternative parent sums by exact `(year, county_fips, MCDNAME)`. `derived_key` is the literal compact JSON tuple, not a source-native or legal municipality ID. Municipalities spanning counties are not merged. |
| `native-2024-ranked.csv.gz` | Complete independent ordering of all 4,103 native precinct rows by reported 2024 Senate votes, including zero rows; includes source fields and exact cumulative integers. |
| `municipal-2024-ranked.csv.gz` | Complete alternative ordering of all 2,761 county-scoped municipal labels; does not imply a statewide legal municipal crosswalk. |
| `candidate-reconciliation.csv` | All 27 candidate/generic-write-in controls for the four requested contests; named identity, source party code/label, explicit analytical group and statewide difference. |
| `sensitivity.json` | Full county orders, state totals, exact integer 80% crossings, top-15 and remainder for all four contests and each year's ballots, REG7AM and EDR. |
| `priority-set.json` | Frozen exact dispatch contract: complete county order, ordered 24 priority keys, all 12,316 historical native constituents grouped by county/year, every exact name/code/ward/source row and unavailable case, plus full 2024 leaf and municipal orders. Only the state-relative external authority path `data/coordinator-priority-acceptance.json` governs accepted historical dispatch; no worker self-acceptance or reverse acceptance hash. |
| `source/extraction-controls.json` | Statewide sums, zero-vote leaves, mail flags and every row where reported method sum differs from TOTVOTING. |
| `source/canvass-2020-reconciliation.json` | Every one of 957 county-field comparisons of 2020 workbook sums against the independent canvass PDF; no differences. |

## Denominators and parties

`USSEN*`, `USPRS*`, and `MNGOV*` are reported contest votes; the suffix `TOTAL` is checked against the complete reported candidate universe on every row. `WI` explicitly includes registered and nonregistered write-ins. It is not a valid-named-write-in allocation. The source supplies no separate blank, undervote, overvote, rejected-vote or valid-named-write-in count for these contests. Null/empty category fields and their status explain this; `TOTVOTING - contest total` is only a denominator gap. No gap is allocated to a candidate or nonvote category.

`DFL` stays `DFL` in raw fields and Democratic-Farmer-Labor in the candidate catalog. Analytical `D` means precisely the DFL candidate; analytical `R` is precisely the Republican candidate. `other` includes every remaining reported candidate and the generic WI field. Source codes such as IA, LIB, LMN and GLC remain distinct. The main CSV's D/R/other fields are redundant arithmetic controls, never a replacement for candidate fields.

The separate 2020 PDF appendix supplies six named-write-in county columns, all 522 explicit cells including zeros. [named-writeins-2020.csv](named-writeins-2020.csv) retains the source candidate label, county label/FIPS, text line and candidate column position; [controls](named-writeins-2020-controls.json) preserve total 32 versus generic WI 2,261 and the unallocated 2,229 scope gap. These tables overlap. They are never added to generic WI or allocated to native precincts. Main CSV `2020_USSEN_named_report_candidate_1` through `_6` correspond, in order, to source labels Josh D. Ondich, John Berman, George A. Dennis Jr, Stephen W Carlson, Jason U. Shaver, Rob Barrett, Jr. Their separate subtotal and generic-minus-named scope gap are explicit. Availability of this named report does not establish a complete validity classification of the generic WI universe; `valid_named_writein` stays unavailable rather than silently treating all generic votes as valid.

The literal source definitions are retained in workbook context:

| Field | Source scope |
| --- | --- |
| `REG7AM` | Voters registered in the precinct at 7 am on that election day (pre-registered); active/inactive status is not separately specified. This is a dated stock, not eligible population. |
| `EDR` | Voters registering when they vote, at the polling place or when voting absentee. Can include re-registration; not a separate participation method or necessarily new voters. |
| `SIGNATURES` | People voting in person, from signatures on polling-place roster. |
| `AB_MB` | Regular and Uniformed/Overseas absentee ballots accepted plus mail ballots accepted. Does not separate early in-person from returned-by-mail absentee ballots. |
| `FEDONLYAB` | Accepted absentee ballots with federal offices only for permanently/indefinitely overseas citizens. |
| `PRESONLYAB` | Accepted president-only absentee ballots for citizens moving out of Minnesota within 30 days. Absent in 2022; absence is not zero. |
| `TOTVOTING` | Number of voters casting ballots, certified by county canvassing boards according to the workbook Notes. |
| `MAILBALLOT` | Source designation that a precinct uses mail balloting, not the method of every individual ballot or a precinct geometry. |

2024 Notes warn SIGNATURES may be too high and AB_MB too low in some mail precincts of Clearwater, Swift and Winona. The warning is attached to every source row in those counties as a conservative county-scoped flag; it does not assert every flagged row is wrong. Reported candidate totals remain untouched. Method sums also fail to equal TOTVOTING in 53 / 41 / 68 source rows, with net excess 22 / 44 / 22 for 2024 / 2022 / 2020. A separate 2022 Waterville Township row reports 378 governor votes versus 377 TOTVOTING. All are retained as discrepancies.

## Hierarchy and dispatch semantics

County keys are `MN:county:{FIPS}`. Native keys are `MN:{year}:VTDID:{VTDID}` to prohibit silent cross-year joins. Source `MCDNAME` is municipality or unorganized territory; `WARD` retains literal source values. Municipal and ward parents overlap their precinct children; county and state summaries overlap both. Only one disjoint level contributes to any statewide sum. The compatibility filename `county-turnout.csv` describes the actual Minnesota county-parent view; the complete native views remain separate and exhaustive.

No standalone central absentee/early candidate rows, polling-place-site identifiers, vote-center identities, ballot-style splits or candidate-by-method splits are present in these result sheets. Their absence is explicitly marked in the contract; no synthetic central unit or polygon is created. A place name containing “Central” is not automatically an administrative absentee board. Geographic/unorganized precinct rows keep their source identity. VTDID here does not establish equivalence to Census VTDs, maps or November 2026 approved reporting units. Historical counts or repeated names do not prove identity or geometry equivalence.

Sorting uses descending integer candidate votes, then ascending exact geography key for ties. Minimum80 uses `5*cumulative >= 4*state_total`, with the previous cumulative strictly below it. Shares are high-precision decimal strings computed from exact integer fractions; display rounding never selects the priority set. Top15 and minimum80 are separate measures; the priority is their union, here the first 24 counties. Native and municipal rankings are alternative analytical views, not additional counties to add to that set.

## Reproduction

Run from the repository root, without network access:

```sh
python3 -B senate/2026/minnesota/data/turnout/extract.py
python3 -B senate/2026/minnesota/data/turnout/reconcile_pdf.py
python3 -B senate/2026/minnesota/data/turnout/build.py
python3 -B senate/2026/minnesota/data/turnout/peer_audit.py
python3 -B senate/2026/minnesota/data/turnout/report.py
python3 -B senate/2026/minnesota/data/turnout/validate.py --refresh-manifest
```

Python standard library and Poppler are sufficient; no dependency/cache directory is retained. `acquire.py` is the optional bounded online evidence acquisition script and leaves existing captures intact. A fresh capture requires a deliberately new evidence ID, not silent overwrite. `asset-manifest.json` inventories every owned artifact except its own self-referential hash, and references shared sources with their separate exact hashes. `validation.json` distinguishes offline arithmetic/source QA from peer agreement and coordinator acceptance.

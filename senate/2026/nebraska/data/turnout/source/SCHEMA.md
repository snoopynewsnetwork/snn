# Nebraska turnout source and data contract

Primary scope is the **2024 Class II two-year Senate special named-canvass
universe**, Ricketts585103 + Love349902 =935005. The primary priority is765
source-native contexts, not20counties. Eligible/generic write-ins are incomplete;
membership robustness is not asserted. Coordinator acceptance and current
geography approval are false. The report and contract carry this qualification.

## Original bytes, acquisition and reconstruction

`acquire.py ID URL [ID URL ...]` retains complete HTTP content bytes in
`source/ID.body.gz` with gzip mtime0. Decompress with Python `gzip.decompress` or
`gzip -dc`; the receipt's `raw_sha256` and `raw_bytes` must match exactly. The
requests transport removes HTTP transfer/content encoding; content is otherwise
unchanged. A transport-decoded entity is not claimed to be a packet/wire capture.
Every receipt retains requested/final URL, UTC retrieval, status, all returned
headers and redirect hops. Source clock, HTTP Last-Modified/Date, archive capture
and retrieval UTC remain separate. A missing redirect history in an inherited
receipt is unknown, never an invented empty history.

Original shared assets are read-only exact-hash references under `data/news/`.
`shared-news-ledger.json` is an immutable retained snapshot of the old233records,
not a dependency on the mutable coordinator ledger. Each original entity is
independently verified by its stored and decompressed SHA256/byte size. Subsequent
newsroom appends do not modify these inputs. Failed receipts and explicitly
truncated archive entities remain evidence. No huge originals are duplicated.
Small fresh current-source observations have their own receipts and exact same
body hash where corroborated. No retained artifact is40,000,000bytes or larger.
No truncation/simplification/splitting is used: every gzip expands in original
byte order. Complete PDFs/workbooks preserve all unrelated offices and source
positions, without a second demographic/unrelated-office extraction.

`peer-primary-original-references.json` references three original historical
final candidate PDFs acquired by the actual peer, with exact original/stored
hashes and primary parent hrefs. Only primary bytes are reused; no peer numerical
allocation is an extraction input. `peer-agreement.json` is the later read-only
independent comparison, never source authority.

`provenance.py` writes `source/source-index.json` with exact receipts, original
paths/hashes/sizes, source-parent chains and source scope. `asset-manifest.json`
pins every owned artifact except itself and `validation.json`, avoiding a hash
cycle. Validation separately pins the manifest; neither self-hash is invented.
All linked raw originals are independently checked. The shared mutable ledger
itself is not pinned as a continuing dependency.

## Reproduction

Use Python3.11+, standard library and external **xlrd2.0.2** for original BIFF.
Set `PYTHONDONTWRITEBYTECODE=1` or use `python -B`. `extract.py` accepts an external
`PYTHONPATH`; its convenience fallback `/tmp/snn-xls-reading-libs` is read-only.
Poppler `pdftotext`, `pdfinfo`, `pdftoppm` are required. Optional original-scan
reading aids require Tesseract5, ImageMagick and Pillow. No dependencies/caches
are retained inside this package.

Run `extract.py`, `local_fields.py`, `scan_transcription.py`, `universe.py`,
`build.py`, `peer_audit.py`, `build.py` again to include the new peer proof,
`report.py`, `provenance.py`, then `validate.py` from this directory. The validator
is offline. Optional `ocr_scans.py` and `ocr_selected.py` rebuild complete/selected
page reading aids. Verified scan transcription is a separate literal table in
`scan_transcription.py`, visually checked against every selected original PNG,
then reconciled to primary candidate and method/volume controls. It is not
residual repair or blind OCR acceptance. Raw images/PDFs remain authoritative.

The original coordinator `preflight_primary_sources.py` was independently run
unchanged with only its shared-output write intercepted into owned
`primary-preflight-reproduction.json`. `primary-preflight-check.json` pins its
script hash and confirms exact original preflight JSON equality. The independent
worker extraction reads original PDFs/HTML/BIFF, not those preflight derivatives.

## County compatibility CSV

`../../county-turnout.csv` is a wide **93county** sensitivity/control table. It
is never the primary geographic dispatch. Each row has literal county,
five-digit `county_fips`, `priority_key=NE:county:FIPS`, separate candidate
columns, source-reported contest sums, registration and Total Voting by year.
Census original codes, not alphabetical enumeration or state-app IDs, supply
FIPS. McPherson31117/Madison31119 are explicitly checked.

Candidate columns are prefixed `2024_senate_special`, `2024_senate_regular`,
`2024_president`, `2022_governor`, `2020_senate`. The full literal identity,
ballot/party and scatterings scope is in `extracts/state-controls.json`.
`*_contest_votes_state_reported` sums exactly those printed candidate columns.
Osborn is By Petition, never Democratic. Love2020 qualified Write-In and
Love2024 Democratic are distinct source identities. No2022Senate exists.
Presidential statewide and congressional-district elector tables are not added.

`YEAR_registered_voters_canvass` is the published `Number of Registered Voters`
snapshot, not voter eligibility or a known finer active/inactive/as-of status.
`YEAR_source_precinct_count` is the source count, not a cross-year ID/geometry
equivalence. All printed party registration columns are separate integers.
`YEAR_total_voting_canvass` is the exact published Total Voting, not contest
votes. The registration/candidate/method tables each preserve all93county rows.

The method suffixes reproduce source categories:

| Year | Printed order before Total Voting |
| --- | --- |
|2024|Polling Place; Early Voting; All Mail Precincts; Provisional Ballot; Military & Overseas; New/Former Resident|
|2022|At Polls; All Mail Precincts; Provisional; Early Voting; Military & Overseas|
|2020|At Polls; All Mail Precincts; Provisional; Early Voting; Military & Overseas; New/Former Resident|

No method is candidate-allocated. Vintages/definitions are not automatically
harmonized. Blank CSV cells are unavailable; literal source zero stays0.
`2024_special_generic_writeins_state_table`, blank/under/over fields are empty
because that state candidate table does not publish them. They are not zero.
`priority_rank`, shares/cumulative/in_top15/in_minimum80 in this compatibility
file describe **county concentration sensitivity only**.

## Primary native contract, hierarchy and keys

`priority-set.json` has schema `NE-turnout-priority-v2`, primary level
`source_native_reporting_unit`. `primary_ranking` is all1326native units at
fixed namedD935005, descending integer votes, exact stable key ascending for
ties. `ordered_priority_keys` is the first765; `ordered_full_keys` is all1326;
`ordered_remainder_keys` is the remaining561. Exact fractions retain numerator
and denominator; decimal percentage strings are presentation. No rounded
percentage determines membership. Minimum condition is `5*cumulative>=4*D` and
the preceding prefix must fail. `top15`, crossing/preceding integers and
remainders are explicit. `county_concentration_sensitivity_only` is a separate
93county comparison, never primary dispatch.

`all93_parents`, `parent_full_child_map`, `parent_priority_child_map` and
`child_parent_map` are complete. Empty priority-child lists remain explicit.
Every child belongs to one county parent in this chosen historical partition.
Count either counties or the selected disjoint children, never add both.

| Chosen source partition | Count | Stable key |
| --- | ---: | --- |
|91complete archived state HTML entities|895|`NE:2024-special:html:SOURCE_COUNTY_ID:NATIVE_ID`|
|Douglas original BIFF|233|`NE:2024-special:douglas-biff:WARD-PRECINCT_LITERAL`|
|Lancaster original final PDF|198|`NE:2024-special:lancaster-pdf:page-ACTUAL_PDF_PAGE`|

HTML county/native IDs preserve leading zeros. The hidden candidate-table1/2
field is **BallotOrder**, not a unique candidate ID. Race12464 is the special,
race12246 the simultaneous regular Senate. Public CSV CandidateID2489/2490
are source-vintage candidate IDs separate from BallotOrder. No key/count/name
match approves another source's precinct, map polygon or current unit.

Douglas's Ward-Precinct field is a literal publication token used in the key;
`native_id_literal` preserves that field, not an inferred hidden machine ID.
Lancaster has no separately published machine ID in this PDF;
`native_id_literal=null` and exact label/page position remain. HTML includes
both exact internal `text_literal` and parsing whitespace text; raw original
HTML/attributes/offsets survive. Exact source labels are not silently rewritten.

`constituents` contains every selected native object: original source/position,
literal ID/label, county/FIPS, candidate vector `[Ricketts,Love]`, source-scoped
generic marks, ballots, registration, blank/under/over, available method vectors,
inclusion/rank and identity qualification. Unknown fields are JSONnull.
`native-turnout.csv` is its flat ranked companion; decimal weights use namedD.

`administrative_and_partial_alternates` contains all329full source objects:
93countywide `_TOT` and236retained partial headers. Their candidate objects
preserve party codes, labels, count/null, BallotOrder, contest ID and completeness.
The complete raw row/position extract is separately linked. They are never added
to chosen children. Additional14Garfield/York PDF Senate contexts are full
alternate source objects, with methods/counts; no HTML identity join is made.
Lancaster/York presidential resident cases have no Senate section and stay
unavailable. Garfield's two school attachments have no Senate context.

## Source position and control extracts

- `state-controls.json`: 11tables, 93county rows each, statewide controls,
  exact candidate identities and original PDF page/line/column/raw line.
- `historical-html-all-positions.jsonl.gz`: every selected source result TR,
  direct cell/attributes/exact text, line and Unicode-character offset, complete
  raw HTML substring. Unclosed EOF rows stay incomplete. Original bytes remain
  authoritative; character offsets are not mislabeled byte offsets.
- `historical-html-native.jsonl.gz` and coverage JSON: every native/admin context
  from all93archive entities, expected/retained headers, source status and clock,
  candidate values and explicit partial completeness. Known partial sums omit
  unknown terms only for a labeled known-sum diagnostic; no missing vote is zero.
- `douglas-original-positions.jsonl.gz`: all1277selected sheet source rows,
  values/types, original dates/footer and95formatted blank2020tail rows. Blank
  formatted rows are not precincts. Full workbooks/sheets remain in original bytes.
- `douglas-native.jsonl.gz`: 1167contexts in five distinct contest tables; all
  candidate/generic/over/under/count fields, combined-method instructions and
  **reconstructed contest volume**, separate from unknown native ballots.
- `lancaster-native-methods.jsonl.gz`: 595contexts, all literal TOTAL/ED/Early/
  Provisional fields; `lancaster-statistics.json`:199statistics contexts with
  ballot/blank methods and registrationTOTAL only. Methods sum toTOTAL, which
  must not be added to them again. `Not Assigned` overlaps write-in parent.
- `additional-summary-*`:12text-layer county contexts and their separate
  statistics; `scan-verified-*`:46visually checked original scan contexts,
  statistics and original source control comparisons. Unprinted fields are null.
- `local-volume-reconciliation.json`:21Douglas summary candidate comparisons,
  source-volume differences−1/−4/−10,03-02within2024 difference, local/state
  registration differences. None are repaired or allocated.
  Lancaster's199native statistics registered sum206570 differs from state206406
  by+164; resident registered0. All199ballots161160 match state Total Voting,
  while198Senate contexts cover161159 and the resident presidential ballot
  remains separate. No registration status/date equivalence is assumed.
- `candidate-universe.json`: complete current five published choices,625setup
  catalog positions (separate full original JSON), historical CSV Senate fields,
  nine-county1117generic vector,431/1078observed vs895unknown native generic,
  conditional233outside/1795inside algebra and coarse30231ballotcapacity.

## Scope, weights and exclusions

Generic marks are not a proven eligible/named write-in total. No statewide
special generic count is printed in the canvass table. The complete later
affidavit/withdrawal/validity roster is not established; missing is not zero.
The partial observed-generic scenario is936083/765/749234 and swaps a native
member; it is not a complete eligible-vote ranking. `universe.py` checks exact
integer conditional bounds without placing unknown votes.

`sensitivity.json` contains full93county orders for the other2024Senate,
2024president, actual2022governor,2020Senate, and each year's separate registration
and Total Voting. Fixed20county comparisons are county concentration only.
No full statewide native ballot/registration sensitivity is fabricated where
895selected HTML contexts lack those fields. No current2026turnout forecast,
live collector, approved boundaries or measured cadence is implied.

All publication statuses, archive capture and source literal clocks retain
their scope. HTML source clocks have no printed timezone. PDFs' footer clocks,
PDF metadata and HTTP clocks are independent. Registration snapshot finer
status/date is unspecified where unprinted. Current final publication is9/11/26,
24pages/page1Senate; the announcement is separate. Catalog148 is a shared
contest/search ID; setupzero is not genuine votes. No2026Democratic Senate row
is invented and Osborn remains named independent/By Petition.

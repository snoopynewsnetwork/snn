# New Hampshire source and calculation schema

Owned scope is `turnout.md`, `data/county-turnout.csv`, and `data/turnout/**`.
All shared originals, coordinator files, and peer outputs are read-only.
No Git or agent creation is part of these scripts.

## Source selection and exact original recovery

The selected 2024 source is `sos-2024-president-archived-original`, the original
BIFF file `2024-ge-president_3.xls`, SHA-256
`fcbdd3810791a4b0988cece58675c41001040b35735f2bbfd61efc73c6527722`.
The actual SOS results index archived 2026-09-17 links this version, ballot
`_14`, and checklist `_7`. Capture recency alone does not supersede the linked
file: the unsuffixed president workbook has different older counts even though
its retained capture is later. The linked `_3` candidate categories agree with
the House Clerk/FEC; its four printed slates agree with NARA. Generic write-ins
are not a demonstrated allocation among named/valid write-in candidates.

The selected 2022 Senate source is the header-mapped `_5` original and separate
remediated PDF, all four candidate fields across all 320 native rows. Its
summary reverses the major-candidate column order used in detail. The House
Clerk still presents the older `_2` split: 297 fewer Hassan and 297 more Bolduc
votes, with the same total. Every retained vintage remains source-scoped.
2020 uses the original Senate PDF, including literal correction asterisks,
blank/dash cells and county sections. See the report for exact counts and URLs.

`shared-originals.json` copies the relevant existing news-manifest metadata and
adds read-only relative content references. Resolve `shared_path` against
`data/turnout/`, not this `source/` directory. Check `stored_sha256` before one
gzip decompression, then check original `raw_sha256`/`bytes`. Shared response
metadata includes requested/final URL, UTC, response headers/status and archive
links. Complete redirect-hop headers were not retained by that earlier
acquisition; this limitation is explicit. Never pretend a saved 403 body is a
result workbook or PDF.
The reference snapshot is pinned once and reused by extraction; subsequent
shared-manifest additions do not silently expand or change this package.
`official-index-links.json` retains the actual three selected link hrefs and
character positions in the recovered official index.

New captures use `<id>.json`, `<id>.headers.txt`, `<id>.body.gz`:

- `requested_url`, `final_url`, `parent_source_id`, `retrieved_utc`, HTTP status,
  complete redirect/response headers, curl diagnostic metadata and errors.
- `stored_sha256` / `stored_bytes`: exact stored `.body.gz` artifact.
- Legacy acquisition keys `original_sha256` / `original_bytes`: response
  entity after undoing the local storage gzip, **before HTTP content decoding**.
- `decoded_original_sha256` / `decoded_original_bytes`: actual source file
  after documented HTTP content decoding. Some Wayback responses returned
  `Content-Encoding: gzip` despite `Accept-Encoding: identity`. In those cases
  `http_content_decoding=gzip`: undo the local gzip and the HTTP gzip, in that
  order, to reconstruct exact source bytes. Otherwise undo only local gzip.
  The compressed HTTP entity is preserved intact too.
- `headers_sha256`: full original response/redirect header bytes. Source
  Last-Modified, archive Memento capture and retrieval UTC are distinct clocks.
  Neither a suffix nor an archive capture proves a correction release cause.

Every stored artifact must be strictly below 40,000,000 bytes. These sources
need no splitting. There is no lossy simplification or truncated original.
Whole originals preserve fields outside the question without making redundant
derivatives of unrelated offices or demographics.

## Extracts and source positions

`extract.py` independently reads original bytes, never the coordinator's count
derivatives. It requires external **xlrd 2.0.2** for BIFF, and Poppler
`pdftotext`; Python's ZIP/XML libraries read OOXML. The available external xlrd
installation is `/tmp/snn-xls-reading-libs`; no dependency/cache tree is stored
in the repository. No spreadsheet or PDF is edited.

`extracts/*-rows.jsonl.gz` preserves every workbook row:

- source ID, sheet name and zero-based sheet index, one-based source row;
- complete literal values, BIFF cell types (0 empty, 1 text, 2 numeric, 3 date,
  4 Boolean, 5 error, 6 formatted blank), or OOXML cell address/type/attributes,
  formula and cached/raw/parsed value;
- original files retain formats, workbook metadata, implicit cells and all ZIP
  parts that are not repeated in the row derivative.

`extracts/*-lines.jsonl.gz` preserves every PDF page and line (one-based), and
`*.txt.gz` preserves complete `pdftotext -layout` output with page breaks.
Original PDF bytes remain authoritative for visual layout. The two retained QA
previews check 2020 Coos dashes/correction marker and the 2022 Lyme blank. The
source's 2022 page itself extends its table to the right edge; the preview is
not a corrected/redesigned document.

`native/<source-id>.jsonl.gz` is one independent source roster per vintage,
each with 320 labels. `fields` contains nonnegative integer counts or JSON null;
`raw_fields` preserves the original blank, dash or number. Missing is never an
invented numeric zero. Candidate universe, method and registration field keys
come from the actual headers. Every record retains source label, county,
source locator and an explicit unavailable numeric-native-ID status.

2020 ballots have side-by-side county tables: the locator also retains
`source_column_start=A` or `G`. An A-column and G-column row are distinct source
records even when sheet/row are identical. Candidate PDF corrections retain
the original starred label, rather than silently stripping asterisks.

`native-fields.jsonl.gz` is a long table of every extracted requested field,
with source scope, raw value, parsed value and position. `controls.json` keeps
summary/footers separately. `reconciliation.json` keeps numeric sums, missing
cells and every detail/footer/summary/state discrepancy. A null control is not
asserted equal to a numeric zero. `vintage-differences.json` compares only exact
county/trimmed-label matches within a source family and records unmatched labels.
This is a textual source comparison, not a boundary or clerk-authority crosswalk.
`contest-candidates.json` retains the source-scoped candidate/ticket names,
party codes, generic write-in versus noncandidate roles, and every actual
header row/position; summary/detail order changes do not discard source keys.

## Geography and dispatch contract

`county-turnout.csv` is a compatibility filename for **320 native town, city,
ward and territory rows**. County and municipal parents are not extra votes.
`geography.json` and `priority-set.json` preserve the disjoint accounting tree.
The selected source has 73 city wards, Berlin as one unexpanded city row, and
246 other labels; 12 explicit warded parents never enter the sum a second time.

- `geography_key`: synthetic `nh-2024-pres:<county FIPS>:<percent-encoded
  whitespace-trimmed literal source label>`, not a publisher's numeric ID.
- `native_label`: original source bytes decoded as text, retaining trailing
  spaces; `display_label` is trimmed. No punctuation/abbreviation correction.
- `county_fips`: Census-verified five-character text, never a ranking unit.
- `ward`: literal ward number from the source's explicit `City Ward N` label;
  always qualified by its city and county. There is no asserted ward FIPS.
- `parent_cousub_geoid_2020`: Census 2020 state+county+subdivision identifier
  only for an exact county-scoped town/city/township name match. Eighteen
  administrative/abbreviated labels remain explicitly unavailable. This is an
  identifier reference, not a legal/current geometry or electoral crosswalk.
- `source_native_id`: null, because no numeric reporting ID is supplied.
  `source_locator` provides a reproducible source identity instead.
- `available_constituents`: each available primary row plus separate 2024
  ballot/checklist row when its county/trimmed literal label agrees; otherwise
  an explicit unavailable case. No name-similarity match.
- `source_native_coverage`: the complete 320-row roster for every retained
  result/administrative vintage, including every unavailable/administrative
  label, positions, null fields and hashed full native-field artifact.
- `finer_constituents_status`: absent polling sites, ballot styles, central
  absentee/early groups or precinct IDs are unavailable, not fabricated.
- `current_2026_equivalence` and clerk-authority status remain unverified.

`reported_candidate_write_in_votes` sums **only reported numeric cells** for
four printed tickets and generic Write-Ins. Twenty rows have missing candidate
fields; sixteen have four blank printed-ticket fields and generic numeric 0.
Their numeric reported subtotal is 0, not a claim that every blank is actual 0.
Every candidate, generic, under and over numeric sum balances at county/state
level in the selected original, so no residual is allocated.

Order is descending reported subtotal, then county FIPS, then trimmed literal
label using Unicode codepoint order. Top-15 and minimum-80 flags use integer
counts. The condition is `5*cumulative >= 4*statewide`, with the preceding
prefix strictly below. Exact numerator/denominator fields govern, not rounded
percentages. The complete ordered list, exact 143 priority keys and full 177-key
remainder are explicit. All units outside priority remain in state arithmetic.

## Administrative fields and sensitivity

Ballot products have `regular`, `absentee`, `ballots_total` exactly as labeled.
They are not candidate-by-method results. No blank/under/over inference fills a
ballot difference. Senate sources do not provide separate under/over fields.

Checklist products retain `republican`, `democratic`, `undeclared`,
`checklist_total`; 2022/2024 additionally retain each party's polling-place
registrations and reported polling-place total. 2020 supplies only the latter
total. No active/inactive status or precise statewide snapshot hour is supplied.
The source header ties the measure to that general election; HTTP/archive
dates do not substitute for an as-of date. Polling-place registrations are kept
separate and never added to the stock. Known source arithmetic defects remain
in `administrative-audit.json`, including Hopkinton's literal 3 versus 296.

`sensitivity.json` independently ranks complete source-specific rosters by
2020/2022 Senate marks, each year's ballots and checklist. It includes the
entire order, top-15, preceding/crossing minimum-80 and remainder for each.
2024 ballots use native Total cells, explicitly 831,468, because the state
summary is 831,467 and method components have another one-vote mismatch.
These sensitivities are volume/denominator comparisons, not a 2026 forecast.

## Offline reproduction and verification

From the repository root, with external xlrd and Poppler available:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-hampshire/data/turnout/extract.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-hampshire/data/turnout/build_turnout.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-hampshire/data/turnout/audit.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-hampshire/data/turnout/report.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-hampshire/data/turnout/validate_turnout.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-hampshire/data/turnout/manifest.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-hampshire/data/turnout/validate_turnout.py
```

Acquisition is separate: `acquire.py ID URL [PARENT_SOURCE_ID]` retains a
capture once; it never silently refreshes an existing ID. Select actual CDX
records or indexed links rather than guessing a future results URL.
`source-inventory.json` provides the request/download/index chains and source
clocks. An unacquired parent label is expressly a discovery description, not
a claim of a retained page; the exact requested/final source URL remains given.

Validation covers raw/stored/decoded original hashes, every source position,
320-row roster uniqueness/coverage, all candidate/method fields and county/state
balances, known source discrepancies, complete order and exact integer crossing,
weight fractions summing to one, parent disjointness, available/unavailable
native constituents, source-scope sensitivity, relative links and strict object
size bounds. `asset-manifest.json` includes every owned file except itself
(a manifest cannot contain its own finite self-hash), with validation included.
Regenerate it after changing the report or peer record, then rerun validation.

Independent peer agreement is recorded only after reading the actual peer's
stable outputs and comparing full fields/order. Until then the contract stays
provisional. Coordinator acceptance remains separate and does not itself
approve 2026 legal geography, a collector, live cadence or calibrated model.

`compare_peer.py` now performs the reciprocal comparison against the actual
peer's stable source/native, county/state, CSV and priority artifacts, retaining
their read-only paths/hashes in `peer-agreement.json`. Its only schema aliases
are peer `ballots_cast` to own `ballots_total`, and peer `label_column` to own
source-column locator. Literal geography labels and candidate identities are
not normalized or guessed. It never writes peer files or uses peer fields as
count/build inputs.

The contract is frozen with external authority path only:
`data/coordinator-priority-acceptance.json`, relative to the state directory.
The coordinator-owned external record is the sole acceptance authority. The
worker provisional/false authority flag is not a rejection or an acceptance;
the reciprocal evidence lives outside the frozen contract. No reverse hash is
embedded, and no current-boundary approval follows. The report and validation
can observe the external record after review without changing contract bytes.
The coordinator has now formally accepted historical dispatch in that external
record. Its pinned reciprocal `peer-agreement.json` is preserved byte-for-byte.
`peer-control-agreement.json` is a separate expanded comparison of all 483
control records; subsequent comparison runs write the supplement rather than
changing the accepted evidence. No acceptance hash is stored in this package.
Validation reads the external authority and verifies its contract/review/peer
pins without adding it to the owned-asset manifest or creating a hash cycle.
The peer later expanded its own `peer-reconciliation.json` with raw/type
verification counters and the frozen contract reference. Validation preserves
the accepted observation hash, explicitly records this later evidence vintage,
and verifies the current supplement's hashes. All original native/count/order
inputs must remain identical; a metadata update is not silently treated as the
same byte artifact.

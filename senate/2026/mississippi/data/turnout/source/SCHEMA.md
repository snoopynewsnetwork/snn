# Mississippi turnout source and schema contract

This package is under active native-field review. County reconciliation does not
authorize current geographic approval or a live collector. See
[validation](../validation.json), [priority contract](../priority-set.json), and
[report](../../../turnout.md).

## Original preservation and provenance

[acquisition.json](acquisition.json) records one observation per source ID.
`url` is the exact requested URL, `final_url` the actual response location,
`retrieved_at_utc` the observation start, `status` the HTTP status, and `headers`
the retained response headers. Owned acquisitions include actual redirect
responses in `redirects`. Reused preparation/peer receipts keep their original
metadata; an absent redirect field means that observation did not record it,
not a reconstructed empty history. `parent_source_id` identifies the inspected
link chain when recorded. Some initial shared preparation receipts lack this
field; their actual linked indexes are retained separately.

`path` is relative to the Mississippi directory. `storage` distinguishes owned
originals from immutable shared-news and independent-peer references. Verify
both `stored_sha256` and `raw_sha256` before use. `.body.gz` and the historical
shared `.html.gz` suffixes contain losslessly compressed original response
entities; the latter can contain a PDF, CSV or HTML according to actual bytes
and HTTP Content-Type. A misleading filename never determines content scope.
Requests/urllib return complete response entity bytes after HTTP transfer/content
decoding. Gzip decompression reconstructs those exact ordered entity bytes.
No truncation, rescaling, simplification or inferred allocation is used.

All stored objects must be strictly below40,000,000 bytes. Original county
packets retain every page, including unrelated offices and process/certification
sheets. No second derivative of unrelated demographic detail is required.
Shared original assets are referenced by exact hashes rather than duplicated.
Original URLs with spaces and their percent-encoded final URLs remain distinct.
HTTP Last-Modified/ETag/retrieval clocks do not establish certification chronology.
Publisher dates/times without a timezone remain literal unknown-timezone fields.

The raw CSV entity is retained in full. `extracts/*-rows.jsonl.gz` preserves every
original CSV row, all literal fields and source row position, including unrelated
offices. Original CSV records are never deduplicated by candidate key.
`source_row=2` means the first record after the header, not a normalized county
identifier. Office/candidate fields retain whitespace and punctuation.

## County and candidate data

[county-turnout.csv](../../county-turnout.csv) contains genuine county parents,
one per all82 counties, in descending2024 Senate named-candidate volume. Its
compatibility filename grants no permission to substitute counties for native
municipal/ward/precinct/central units. `fips` is five-character county FIPS;
EAC2024 `FIPSCode` ten-character source IDs validate the five-character prefix.
Explicit county aliases are `Jeff Davis`→`JEFFERSON DAVIS COUNTY` and
`DeSoto`→`DESOTO COUNTY`; these are county-level source aliases, not native
precinct or boundary crosswalks. SOS monthly county codes01–82 are retained as
separate administrative codes and are not county FIPS.

`2024_senate_*` fields contain certified source-scoped named votes for TyPinkins
and RogerF.Wicker. `2020_senate_*` retains MikeEspy, CindyHyde-Smith and
JimmyL.Edwards separately. `*_candidate_votes` sums the actual source candidate
universe for that election/contest. `2024_president_candidate_votes` includes
all nine names, with every minor/independent candidate retained in
[candidate-votes.csv](../candidate-votes.csv). There is no forced Democratic
coalition or carryover of Pinkins's historical Democratic label into2026.

The original2024 county CSV is a different release from the signed certificate.
Only Pike uses the explicitly linked updated county values: Senate7,130/8,205
and the nine presidential rows on updatedPDFpage4. `prior_csv_votes` and
`prior_csv_source_row` preserve that superseded source observation. The current
candidate record points directly to the updatedPDF's source column. Coahoma
original and updated documents remain separate even when candidate counts agree.

`candidate-votes.csv` keys consist of election, county, office literal, candidate
literal and party literal, with source ID/position retained on each record. The
validation script requires source-row uniqueness rather than silently selecting
one duplicate. Source literal identities are not adjudications of valid write-in
status. Main certified Senate candidate sums include the source's two named2024
candidates. Generic tabulator write-in marks, valid/named write-ins, under/over,
blank, ballots and registration require explicit separate source scopes.

`rank` is1–82. Ties sort by FIPS. `share` and `cumulative_share` are percent
values, not fractions. All arithmetic starts from integers; displayed rounding
does not determine the80% crossing. `priority` is the union of top15 with the
minimum descending80% **county-parent sensitivity** set, not native dispatch.
The integer criterion is `5*cumulative >= 4*state`. Every county outside this
county sensitivity remains in all state sums and comparisons. The actual
source-native priority has887 children in77 county parents; five county parents
have no priority child and still remain in state arithmetic.

The currently empty generic/ballot/registration/blank/under/over compatibility
fields are unavailable uniform statewide certified fields, not zeros or inferred
differences. Do not use them to override source-specific controls below.

## Native identities and hierarchy

Source-position keys use countyFIPS + sourceID + originalPDFpage + original
source column/row. They are provenance keys when no printed precinct ID exists,
not invented official precinct IDs. Keep the source's printed code and full
literal name separately. A label may identify a precinct, split style, municipal
ward, polling site, combined unit or central administrative group. Names and
counts alone do not establish cross-year geometry or November2026 equivalence.

Preserve every source-native position, including source TOTAL/summary and unused
template columns, with an explicit role. County summaries and included native
constituents overlap. Disjoint vote sums exclude summary/TOTAL and verified unused
positions; they include all genuine native administrative and central groups.
Never allocate central ballots to precinct polygons by a county residual.
Repeated physical precinct names across source vintages retain separate keys.

[native-source-orders.json](../native-source-orders.json) preserves all84
published2024 source-view descending orders and the selected disjoint82-view
order. [native-source-order.csv](../native-source-order.csv) is the complete
1,736-row selected order, with exact cumulative named votes and887 priority
flags. [priority-set.json](../priority-set.json) roots `ordered_priority_keys`,
`all_unit_order`, `remainder` and `native_priority_by_parent` in that native
order; `county_parent_sensitivity` retains the separate41-county control.
The preferred native Senate denominator is1,215,400. Tunica SEMS native
Pinkins1,797 differs from the official county/ES&S summary1,798; the single
unassigned vote is explicit in `source_native_unavailable_cases`, never an
invented native unit. The887-unit crossing remains valid for both denominators
under the recorded integer bound. These source keys are not November2026 IDs.

The immutable84-peer replay was pinned before43 later literal printed-ID
parses in Claiborne, Jefferson Davis and Perry. The added IDs are exact
substrings of unchanged source headers and leave votes and roles unchanged;
[native-84-working-metadata-differences.json](../native-84-working-metadata-differences.json)
documents both versions. The frozen comparison does not assert byte-identical
optional ID fields to the later working ledger. Fifty-eight Itawamba candidate
reading boxes also differ between independent replays and remain explicit;
numeric agreement is not geometry agreement.

[native-profile-fields.csv](../native-profile-fields.csv) retains20 Union and25
Pike-original source-vendor profiles, respectively380 and525 numeric fields.
These are alternative nonadditive native views, with all candidate, generic,
registration, ballot, blank and contest-total fields **where printed**.
`native-profile-controls.json` compares every available aggregate to its
own original summary/statistics panel; unavailable fields remain null. Pike's
25 profiles start on variable pages among PDF15–56, not every other page.
Pike original and Pike Updated have distinct publication scopes. A source
profile is not assumed equivalent to a SEMS column or current geography.

`extracts/*-page-probe.json.gz` contains source hash, original page count, every
page's orientation/label probe and selected reading aids. Each selected page
retains original PDF rectangle, render dimensions, rotation/deskew transformation,
OCR TSV token boxes/confidence and preview pointer. Low-resolution OCR absence is
not native absence; compiled packets require per-page orientation reinspection.
`extracts/*-native-grid-*.json.gz` are **unreviewed OCR derivatives** until explicitly
reviewed and reconciled. Version1–4 experiments have known geometry/clipping
failures and are not accepted transcriptions. Raw PDFs remain authority.

[native-readings.json](../native-readings.json) records independent visual cell
readings and corrections with original source/page/column/candidate positions.
No corrected value is derived from a residual. A visually verified source row and
candidate sum does not approve its modern boundary. Native peer agreement and
coordinator acceptance remain distinct gates.

## Participation, methods and registration

[participation-controls.csv](../participation-controls.csv) retains all82 EAC
county jurisdictions in2022v1.1 and2024v2, relevant A1/F1 fields, literal source
strings, archive member and CSV row positions. `value` is an integer only when
the source field explicitly contains a nonnegative integer. Negative sentinel
codes, blank fields and comments retain raw strings, with numeric `value` empty.
`source_missing_code` never contributes an invented zero to a method total.
Summary `reported_sum=0` with `reported_count=0` means no numeric observations,
not a known zero. `A1a/b/c` means total/active/inactive registration in that survey.
`F1a` measures participation, not candidate votes. The short `F1b` labels change
between2022 ElectionDay and2024 physical polling place; both complete original
instruments define counted ballots cast at physical polling places on Election
Day, excluding provisional and dropped-off mail ballots. F2 source-basis fields
remain separate: SEMS in2022 and mixed pollbooks, ballots counted, vote history
and highest-office votes in2024. Combined absentee comments and unallocated method
volume remain explicit. Historical groups do not establish November2026 methods.

[active-registration.csv](../active-registration.csv) retains three distinct
82-county SOS monthly snapshots: November2022, November2024, September2026.
`source_county_code`, `county_literal`, source page and population comparison
literal remain separate. Source policy describes first-Monday monthly active
counts; neither the filename month nor HTTP date is the certified election-day
registration status. Source asterisks and the indicated population vintage remain
part of the source interpretation, not a reason to adjust candidate counts.

[participation-summary.json](../participation-summary.json) preserves relevant
codebook worksheet/member/cell coordinates and per-field reported/missing counts.
[volume-sensitivity.json](../volume-sensitivity.json) independently ranks each
complete source vector and measures both its own minimum80% and the fixed2024
priority share. Source disagreements such as2024 named candidate totals exceeding
EACF1a remain visible and are never treated as participation probabilities.

## Reproduction and gates

Run from any directory with Python3, requests, PyMuPDF, Pillow, NumPy and public
Tesseract installed. No dependency/cache directories are deliverables. Primary
steps: `acquire_sources.py`, `acquire_context.py`, `build_turnout.py`,
`build_participation.py`, native extraction/review scripts, `build_report.py`,
`validate_turnout.py`. Acquisition resumes from pinned receipts; offline builders
read saved entities. Visual manual readings remain explicit, reproducible source
pointers rather than hidden editing. The independent peer owns baselines outputs;
read-only comparisons never mutate them to agree.

Validation checks original/stored hashes, all82 identities and uniqueness,
candidate/state/county sums, explicit Pike replacement, complete descending order,
all-state weights, exact minimum integer80% crossing/remainder, source-scoped
survey codes, relative links and object-size bounds. `validation.json` records
the qualified offline named-candidate and immutable-dependency checks separately
from unavailable broad native fields, current geographic approval and coordinator
acceptance. County rank agreement is not legal geographic approval.

## Reviewed source ledgers and field-level comparison

[historical-county-readings.json](../historical-county-readings.json) records all164
original2018 county-stage TOTAL observations. `build_historical_counties.py`
produces492 candidate records in
[historical-county-candidate-votes.csv](../historical-county-candidate-votes.csv).
All four November6 and both November27 state vectors match the signed certificate.
`reconcile_historical_peer.py` compares all164 raw-source hashes, pages, accepted
TOTAL ordinals and492 named candidate fields read-only. Corrected ordinal histories
retain discovery-aid ordinals and physical bounds separately. Blank special-election
party cells are not pooled party fields.

[native-reviewed-2024.json](../native-reviewed-2024.json) is the manual original
reading ledger for the bounded reviewed scope; it remains incomplete statewide.
`record_native_review.py` and explicit `record_native_*.py` scripts reproduce its
literal labels, printed native codes (null where unestablished), roles, both Senate
counts, header/candidate pixel bounds, render sizes, rotation/deskew and evidence.
Correction histories preserve prior manual readings. Original OCR aids stay
unchanged. Geometry replacements retain prior template bounds and exact reference
hashes, copying no peer numeric or label values. `make_native_review.py` renders own
template mosaics; `make_physical_review.py` renders original cells at detected or
explicitly reviewed physical rules. Missing-rule hypotheses remain explicit.

`build_native_contract.py` emits
[native-candidate-votes-reviewed.csv](../native-candidate-votes-reviewed.csv),
[native-constituents-reviewed.json.gz](../native-constituents-reviewed.json.gz) and
[native-reviewed-controls.json](../native-reviewed-controls.json). Disjoint native
sums exclude each separate source TOTAL and verified unused template cells.
Parallel original/updated/amended source views are alternatives, never additive.
The dispatch contract inventories all84 available2024 originals. All82 preferred
views have complete original-read named Senate and presidential fields, with the
two superseded county publications retained nonadditively. Generic, ballot,
registration and method fields are included only where printed and reviewed.
Every key remains election and source scoped; none grants2026 identity or
boundary approval.

[native-allfield-readings.json](../native-allfield-readings.json) separately records
complete original native vectors for all9 presidential and2 Senate candidates
where independently reviewed. `reconcile_native_allfields_peer.py` compares numeric
AND unused positions with raw-source, row, physical-x, render and rotation/deskew
agreement. Matching county totals cannot excuse compensating cell errors.

The wider presidential workbench is explicitly provisional:
[presidential-original-aid-cells.csv](../presidential-original-aid-cells.csv)
retains18,980 original-image source positions across84 views, each first OCR,
optional second independently cropped OCR, direct original visual reading and
compiler basis separately. The first OCR left2,618 native cells unresolved;
the second read1,696, and all922 remaining original-cell cards were visually
read into [the manual atlas ledger](../presidential-unresolved-original-readings.json).
Thirty-two visibly wrong row targets (Coahoma original, Perry or Tunica) stay
null, rather than silently becoming zeros. The immutable original cards and
physical bounds are under `qa/presidential-unresolved-atlases/`. The two fully
accepted direct original allfield views supersede15 OCR/atlas disagreements.
[The provisional controls](../presidential-original-aid-controls.json) retain
remaining candidate/TOTAL failures; neither OCR agreement nor an observed zero
in an atlas accepts an entire county/source. Row repairs and full candidate,
method and peer reconciliation remain separate statewide gates.

Three later complete direct-original source transcripts remain separate from
that frozen preliminary workbench: [Tunica presidential](../tunica-presidential-original-readings.json)
has12 native columns and one printed TOTAL over pages7–8, with the party strip
explicitly excluded from vote columns; [Perry presidential](../perry-presidential-original-readings.json)
has16 native columns and one TOTAL over pages2–3, including page3 candidate
rows missed by preliminary OCR; [Winston allfield](../winston-allfield-original-readings.json)
has12 native columns, one TOTAL, nine unused columns and all11 candidate
vectors over pages2–3. Direct original source rasters and raw hashes are pinned
in each ledger. [The Tunica/Perry check](../direct-presidential-two-source-reconciliation.json)
retains Tunica's Harris original1836 versus CSV1837 as a source-scoped +1
difference, while Perry's nine printed totals match CSV. The [Winston peer
audit](../winston-original-peer-reconciliation.json) compares143 numeric plus99
unused/null original positions and all11 county controls after extraction.
These readings expand bounded allfield evidence to five complete SEMS source
views (including Alcorn and Coahoma Updated), covering75 preferred native
columns. They do not accept the remaining statewide presidential geography.

[Hinds original presidential reading](../hinds-presidential-original-readings.json)
adds108 native columns across ten original PDF pages, all nine candidates, one
printed TOTAL and one unprinted template position. `make_hinds_presidential_original_review.py`
re-renders the ten pages from the hash-checked PDF; `record_hinds_presidential_original.py`
keeps the prior independent original-pixel OCR values and eight explicit direct
full-page visual corrections. Source candidate sums match all nine printed
TOTAL and county CSV values;990 positions are compared to independent peer
only after extraction. [Five smaller original source readings](../small-presidential-original-readings.json)
add Benton, Greene, Wilkinson, Noxubee and Issaquena,40 native constituents,
594 nine-candidate positions and20 direct full-page visual OCR corrections.
`make_small_presidential_original_review.py` and
`record_small_presidential_original.py` reproduce those bounded ledgers.
Peer literal header line wraps are compared after whitespace folding and each
unmodified literal remains in its own source ledger. Provisional original-pixel
OCR cell boxes are retained as **aids**, not accepted numeric polygons; an
unprinted template position is null rather than an observed zero. Together
these six added views make11 preferred complete presidential source views/223
native constituents. Statewide nine-candidate native review remains open.

[The seven-source original reading](../batch2-presidential-original-readings.json)
adds Adams, Carroll, Clay, Jefferson, Quitman, Sharkey and Sunflower:
96 preferred native columns,1,188 nine-candidate source positions and37
direct full-original corrections to the earlier independent OCR pass.
`make_batch2_presidential_original_review.py` renders the original pages and
`record_batch2_presidential_original.py` records the direct original readings
before comparing all values/roles and whitespace-folded labels with the
independent peer. All nine vectors per source close their own printed TOTAL
and county CSV controls. These make18 preferred complete presidential source
views/319 native constituents in this bounded transcript. The rest of the
state remains outside its accepted original-field scope.

[The four-source original reading](../batch3-presidential-original-readings.json)
adds Calhoun, Claiborne, Smith and Tishomingo:53 preferred native columns,
693 nine-candidate source positions and60 direct full-original corrections
to the independently retained provisional OCR. `make_batch3_presidential_original_review.py`
renders complete hash-checked source pages and exception cards;
`record_batch3_presidential_original.py` records the original glyph readings
before peer comparison. Every named vector closes its own printed TOTAL and
county CSV. All693 values/roles and whitespace-folded literal labels agree
the independent peer after extraction. The complete bounded transcript is
therefore22 preferred source views/372 native constituents. Numeric OCR crop
rectangles are provisional, and statewide presidential native acceptance
remains open.

[The eight-source original reading](../batch4-presidential-original-readings.json)
adds Union, Stone, George, Lowndes, Panola, Monroe, Prentiss and Newton:
155 preferred native columns/1,683 nine-candidate source positions. A fresh
hash-checked complete original-page render supports36 direct visual corrections
to the earlier independent OCR; Prentiss has no OCR disagreement and both
pages were still inspected. `make_batch4_presidential_original_review.py` and
`record_batch4_presidential_original.py` reproduce the bounded ledger and
post-extraction peer comparison. Every nine-candidate source vector closes
the printed TOTAL and county CSV. This makes30 complete preferred 2024
presidential source views/527 native constituents in the bounded transcript.
The other52 preferred views/1,209 native constituents remain outside this
original-field acceptance scope; source PDF positions are not current2026 IDs.

[The four-source original reading](../batch5-presidential-original-readings.json)
adds Walthall, Jasper, Yalobusha and Washington:63 preferred native columns,
792 nine-candidate positions and21 direct full-original corrections to the
earlier independent OCR. `make_batch5_presidential_original_review.py` and
`record_batch5_presidential_original.py` reproduce the hash-checked page
renders, original-reading ledger and post-transcription reciprocal check.
Each candidate's native sum equals the printed source TOTAL and county CSV;
all792 positions/roles and whitespace-folded original labels agree the peer.
The bounded complete presidential scope is now34 preferred views/590 native
constituents. The other48 preferred views/1,146 native constituents remain
outside this original-field scope; the two alternative published PDFs belong
to the separate84-source-view universe.

[The next four-source original reading](../batch6-presidential-original-readings.json)
adds Montgomery, Tallahatchie, Lawrence and Copiah:64 preferred native
columns/792 nine-candidate positions. The independent original-pixel pass has
49 errors resolved by reading complete original source pages, including
Copiah's nine printed TOTAL fields. `make_batch6_presidential_original_review.py`
and `record_batch6_presidential_original.py` preserve original page hashes,
provisional OCR values and direct visual corrections. All nine candidate
vectors per source close its printed TOTAL and county CSV; post-extraction
peer comparison agrees all792 values/roles and whitespace-folded labels.
The bounded complete preferred scope is38 views/654 native constituents;
the other44 preferred views/1,082 native constituents remain outside this
presidential original-field scope. No current2026 geometry inference follows.

[The four-large-county original reading](../batch7-presidential-original-readings.json)
adds Harrison, DeSoto, Rankin and Forrest:176 preferred native source
columns/1,881 nine-candidate positions across19 complete original canvass
pages. `make_batch7_presidential_original_review.py` re-renders those original
PDF pages and preserves46 aid discrepancies with original-only cards;
`record_batch7_presidential_original.py` records each direct whole-page glyph
reading. All nine native vectors in every source close the separately printed
TOTAL and county CSV; only afterward are all1,881 values/roles and
whitespace-folded source labels compared with the independently extracted
peer. Source rasters, source headers, provisional OCR values and hashes remain
separate. The aid crop rectangles are not accepted numeric-cell polygons.
The bounded complete preferred presidential scope is42 views/830 native
constituents;40 preferred views/906 native constituents and two alternative
published views remain outside it. This supplies no current2026 identity
or geometry crosswalk.

[The Lee/Madison original reading](../batch8-presidential-original-readings.json)
adds77 preferred native constituents/891 nine-candidate source positions on
nine complete original PDF pages. `make_batch8_presidential_original_review.py`
retains original rasters and34 OCR exception cards;
`record_batch8_presidential_original.py` records direct full-page readings,
including all nine Madison printed TOTAL cells on PDFpage6 missed by the
original OCR aid. Every nine-candidate native sum agrees the printed source
TOTAL and county CSV, and all891 fields/roles and whitespace-folded literal
labels agree the peer only after transcription. The bounded complete preferred
scope is44 views/907 native constituents, with38 preferred views/829 native
constituents plus two published alternative views still outside original-field
review. Aid crop bounds remain provisional, not certified numeric polygons.

[The Covington/Leake/Attala original reading](../batch9-presidential-original-readings.json)
adds54 preferred native constituents/594 nine-candidate positions from six
complete original canvass pages. `make_batch9_presidential_original_review.py`
preserves the full original rasters and56 discrepancy cards;
`record_batch9_presidential_original.py` records direct visual source glyph
corrections. Each of the nine native vectors per source equals its printed
TOTAL and official county CSV, and all594 fields/roles and whitespace-folded
literal labels agree the peer after independent source reading. The bounded
complete preferred scope is47 views/961 native constituents;35 preferred
views/775 native constituents plus two published alternative views remain
outside original-field review. Provisional OCR bounds are not accepted
numeric polygons or current-geography IDs.

[The Hancock/Chickasaw/Warren/Jones original reading](../batch10-presidential-original-readings.json)
adds102 preferred native constituents/1,188 nine-candidate positions across12
complete original canvass pages. `make_batch10_presidential_original_review.py`
retains source rasters and20 original-only discrepancy cards;
`record_batch10_presidential_original.py` records direct source-glyph readings
before peer comparison. Every nine-candidate native vector closes its printed
TOTAL and county CSV, and all1,188 values/roles and whitespace-folded literal
labels agree the peer after source transcription. The bounded complete preferred
scope is51 views/1,063 native constituents;31 preferred views/673 native
constituents and two published alternative views remain outside original-field
review. OCR crop windows remain provisional and imply no current identity join.

[The Lamar/Neshoba/Oktibbeha original reading](../batch11-presidential-original-readings.json)
adds67 preferred native constituents/792 nine-candidate positions on eight
complete original canvass pages. `make_batch11_presidential_original_review.py`
retains original rasters and17 discrepancy cards;
`record_batch11_presidential_original.py` records the independent source
readings. The script preserves the correction of a first full-page glance at
Neshoba Claudia De la Cruz columns Herbert and Hope after enlarged ORIGINAL
cell rereading (1 and0 respectively), not a fitted residual. All nine native
candidate vectors close printed TOTAL and county CSV, and all792 source
positions/roles/whitespace-folded labels agree the peer only afterward. The
bounded complete preferred scope is54 views/1,130 native constituents;
28 preferred views/606 native constituents and two published alternative
views remain outside original-field review. OCR crop bounds are provisional.

[The Marion/Wayne/Pearl River original reading](../batch12-presidential-original-readings.json)
adds71 preferred native constituents/891 nine-candidate positions on nine
complete original pages. `make_batch12_presidential_original_review.py`
retains whole original source rasters and30 discrepancy cards;
`record_batch12_presidential_original.py` records source glyph values, including
Marion's three printed TOTAL values missed by OCR. Every nine-candidate vector
closes printed TOTAL and county CSV; all891 values/roles/whitespace-folded
source labels agree the independent peer only after source transcription.
The bounded complete preferred scope is57 views/1,201 native constituents;
25 preferred views/535 native constituents and two alternative publications
remain outside it. OCR crop windows do not certify numeric polygons.

[The Pike Updated/Marshall/Simpson original reading](../batch13-presidential-original-readings.json)
adds71 preferred native constituents/891 nine-candidate positions on nine
complete original pages. `make_batch13_presidential_original_review.py`
retains the full rasters and38 discrepancy cards;
`record_batch13_presidential_original.py` independently reads the printed
glyphs before all-position peer comparison. Every nine-candidate native sum
closes the same source publication's TOTAL and official county CSV. Pike
Updated remains distinct from the earlier Pike original publication; the
earlier publication is not added to these preferred counts. The bounded
complete preferred scope is60 views/1,272 native constituents;22 preferred
views/464 native constituents and two alternative published source views remain
outside this original-field review. Numeric crop windows remain provisional.

[The Pontotoc/Tate/Humphreys original reading](../batch14-presidential-original-readings.json)
adds60 preferred native constituents/693 nine-candidate positions on seven
complete original pages. `make_batch14_presidential_original_review.py`
retains original rasters and53 discrepancy cards;
`record_batch14_presidential_original.py` records direct glyph readings before
the all-position independent peer comparison. All nine candidate vectors per
view close printed TOTAL and the county CSV. The bounded complete preferred
scope is63 views/1,332 native constituents;19 preferred views/404 native
constituents and two alternative publications remain outside it. OCR numeric
crop windows remain provisional.

[The Yazoo original reading](../batch15-presidential-original-readings.json)
adds23 preferred native constituents/297 nine-candidate positions on three
complete original PDFpages4–6. `make_batch15_presidential_original_review.py`
retains the page rasters and23 discrepancy cards;
`record_batch15_presidential_original.py` records the visible original glyphs
before the independent peer comparison. All nine candidate vectors close the
printed TOTAL and county CSV. Complete-original preferred scope is64 views/
1,355 native;18 preferred views/381 native and two alternative publications
remain outside it. Numeric crop windows remain provisional.

[The Lafayette original reading](../batch16-presidential-original-readings.json)
adds18 preferred native constituents/198 nine-candidate positions on two
complete original pages. `make_batch16_presidential_original_review.py` retains
both page rasters and26 discrepancy cards;
`record_batch16_presidential_original.py` reads visible glyphs before peer
comparison. All nine vectors close original TOTAL and the county CSV. The
complete-original preferred scope is65 views/1,373 native;17 preferred
views/363 native and two alternative publications remain outside it. Numeric
crop windows remain provisional.

[The Clarke original reading](../batch17-presidential-original-readings.json)
adds23 preferred native constituents/297 nine-candidate positions on three
complete original pages. `make_batch17_presidential_original_review.py` retains
the page rasters and61 discrepancy cards;
`record_batch17_presidential_original.py` records original glyphs before peer
comparison. The initial South Quitman Harris glance 37 was corrected to the
visible 371 by a complete source-row reread. All nine candidate vectors close
the original TOTAL and county CSV. Complete-original preferred scope is66
views/1,396 native;16 preferred views/340 native and two alternative
publications remain outside it. Numeric crop windows remain provisional.

[The Bolivar original reading](../batch18-presidential-original-readings.json)
adds30 preferred native constituents/297 nine-candidate positions on three
complete original PDFpages6–8. `make_batch18_presidential_original_review.py`
retains page rasters and23 discrepancy cards;
`record_batch18_presidential_original.py` records the original glyphs before
peer comparison. All nine candidate vectors close printed TOTAL and county
CSV. Complete-original preferred scope is67 views/1,426 native;15 preferred
views/310 native and two alternative publications remain outside it. Numeric
crop windows remain provisional.

[The Lincoln original reading](../batch19-presidential-original-readings.json)
adds30 preferred native constituents/297 nine-candidate positions on three
complete original PDFpages3–5. `make_batch19_presidential_original_review.py`
retains page rasters and49 discrepancy cards;
`record_batch19_presidential_original.py` reads the printed glyphs before peer
comparison. All nine vectors close source TOTAL and county CSV. The
complete-original preferred scope is68 views/1,456 native;14 preferred
views/280 native and two alternative publications remain outside it. Numeric
crop windows remain provisional.

[The Lauderdale original reading](../batch20-presidential-original-readings.json)
adds37 preferred native constituents/396 nine-candidate positions on four
complete original PDFpages7–10. `make_batch20_presidential_original_review.py`
retains page rasters and61 discrepancy cards;
`record_batch20_presidential_original.py` reads the printed glyphs before peer
comparison. All nine vectors close source TOTAL and county CSV. The
complete-original preferred scope is69 views/1,493 native;13 preferred
views/243 native and two alternative publications remain outside it. Numeric
crop windows remain provisional.

[The Grenada original reading](../batch21-presidential-original-readings.json)
adds13 preferred native constituents/198 nine-candidate positions on two
complete original scanned PDFpages3–4. `make_batch21_presidential_original_review.py`
retains original rasters and30 discrepancy cards;
`record_batch21_presidential_original.py` records direct original glyphs before
peer comparison. The page4 Senate/native header workbench is downsampled,
whereas presidential aid positions refer to a full-size 2.7x original render;
both geometries remain distinct and the candidate crop bounds are provisional.
All nine vectors close source TOTAL and county CSV. Complete-original preferred
scope is70 views/1,506 native;12 preferred views/230 native and two alternative
publications remain outside it.

[The Tippah original reading](../batch22-presidential-original-readings.json)
adds21 preferred native constituents/198 nine-candidate positions on complete
original PDFpages3–4. `make_batch22_presidential_original_review.py` retains
both page rasters and four OCR-discrepancy cards. The aid entirely missed nine
printed presidential TOTAL fields on page4; `record_batch22_presidential_original.py`
records those nine direct whole-page readings separately, with no numeric aid
crop and no inferred zero, as well as four corrected aid cells. All nine
constituent vectors close the printed TOTAL and county CSV and agree the peer
only after the original reading. Candidate crop boxes remain provisional.
Complete-original preferred scope is71 views/1,527 native;11 preferred
views/209 native and two alternative publications remain outside it.

[The Leflore complete-original grid](../batch23-presidential-original-readings.json)
adds18 preferred native constituents/198 nine-candidate positions on original
PDFpages5–6. `make_batch23_presidential_original_review.py` retains source
rasters and106 OCR-discrepancy cards, but
`record_batch23_presidential_original.py` transcribes **every** nine-candidate
cell from the full printed grids. The provisional aid omitted the nine cells
of native Schlater p5c11 and nine unprinted positions p6c11; all three p6
unused template columns are explicit nulls. Each native vector closes the
printed TOTAL and county CSV and only afterward agrees the peer at all198
positions. `record_fullgrid_presidential_original.py` documents this full-page
direct-reading mode. Candidate crop polygons remain provisional. Preferred
complete-original scope is72 views/1,545 native;10 views/191 native and two
alternative publications remain outside it.

[The Webster complete-original grid](../batch24-presidential-original-readings.json)
adds14 preferred native constituents/198 nine-candidate positions on original
PDFpages2–3. `make_batch24_presidential_original_review.py` retains both full
source rasters. No presidential aid cell existed for this source;
`record_batch24_presidential_original.py` directly transcribes all135 printed
candidate cells and63 visibly unprinted template positions. All nine native
candidate vectors close source TOTAL and county CSV, then agree the peer at
all198 positions. No source value was inferred from the peer or a residual.
Preferred complete-original scope is73 views/1,559 native;9 views/177 native
and two alternative publications remain outside it.

[Jeff Davis](../batch25-presidential-original-readings.json) and
[Franklin](../batch26-presidential-original-readings.json) add31 preferred
native constituents/396 positions across four original PDF pages. The full
source grids are directly transcribed by `record_batch25_presidential_original.py`
and `record_batch26_presidential_original.py`, independently of provisional
OCR and peer values. Jeff Davis has19 OCR disagreements/30 missing aid
positions, Franklin one/99. All 18 nine-candidate source vectors close their
printed TOTALs and county CSVs, then agree all peer positions. The complete
preferred original scope is75 views/1,590 native;7 views/146 native and two
alternative publications remain outside it.

[Holmes](../batch27-presidential-original-readings.json) and
[Choctaw](../batch28-presidential-original-readings.json) add28 preferred
native constituents/396 positions across four original PDF pages. Their
direct full-grid scripts preserve all printed values and blank template slots.
The Holmes aid missed99 cells and misread49; Choctaw missed143/misread24. Each
nine-candidate vector closes its printed TOTAL/county CSV and then matches the
peer's values and roles. Two Holmes A-Z headers wrap across lines in the peer
literal; both source-scoped label representations are retained and the
hyphen-line break is folded solely for the comparison. Preferred complete
original scope is77 views/1,618 native;5 views/118 native and two alternative
publications remain outside it.

[Amite](../batch29-presidential-original-readings.json),
[Scott](../batch30-presidential-original-readings.json),
[Itawamba](../batch31-presidential-original-readings.json),
[Jackson](../batch32-presidential-original-readings.json), and
[Kemper](../batch33-presidential-original-readings.json) complete the preferred
82-source/1,736-native 2024 presidential named-candidate partition. Each of
the five full-page scripts directly records all nine original candidate rows,
printed TOTALs, unprinted template cells and source positions before comparing
county controls or peer values. The five views contribute118 native units and
1,485 source positions. Kemper original PDF6 is an **unofficial** parallel
11-column observation, retained with role `parallel_native_observation` and
excluded from additive sums; official PDF7–8 supplies14 native columns and
one TOTAL. The direct original position tables preserve literal headers and
source publication hashes, but OCR aid crop polygons remain provisional.
The old Coahoma and Pike publications remain nonadditive alternative views.
The Tunica Harris and Pinkins source-versus-county CSV differences of one vote
each are unallocated and explicitly bounded by their original source scope.

[canvass-summary-readings.json](../canvass-summary-readings.json) and
[canvass-statistics-readings.json](../canvass-statistics-readings.json) preserve15
summary and14 statistics panels, including all11 named candidates and generic,
method, blank, under/over, ballot and registration fields wherever printed.
`build_canvass_controls.py` emits672 fields and validates30 contest panels;
`reconcile_canvass_peer.py` compares390 shared fields independently:389 agree
literally, while Lincoln PDFpage9's header versus footer clock is retained as
one explicit source-scope difference, not a numeric disagreement. This bounded
coverage is not a uniform statewide generic/ballot/registration universe. Original
Pike statistics remain separate from updated named votes. Processing columns
(scanned/manual) are not voting-method columns (precinct/absentee).

[`record_montgomery_2024_statistics.py`](../record_montgomery_2024_statistics.py)
rerenders the unchanged original Montgomery PDFpages1 and3. Page3 prints
registered6,291, ballots885, blank1, turnout14.07% and clock10:24AM; page1
prints named Senate4,349 and president4,424 and clock10:25AM. The candidate
figures exceed the page3 ballot number, so no candidate-ballot denominator or
method allocation is inferred. The prior13-panel statistics ledger is retained
losslessly in [`canvass-pre-montgomery-statistics-v1/`](canvass-pre-montgomery-statistics-v1/pin.json).

The 2020 same-seat [original publication TOTAL ledger](../2020-publication-original-total-readings.json)
retains all104 actual linked county PDF versions, each original raw hash/page,
three literal candidate values, reading basis, original card/full-band evidence
and qualified TOTAL-column locator. `make_2020_total_original_atlases.py`,
`read_2020_total_original_ocr.py`, `make_2020_total_exception_review.py`,
`make_2020_total_original_exception_strips.py` and
`record_2020_publication_original_totals.py` recreate original-only review
evidence and the312-field ledger. Fifty vectors have two independent OCR-mode
readings of original pixels;54 were read visually from whole original source
bands. Ten direct original ordinal corrections are distinct from the remaining
position hints. [The post-extraction peer comparison](../2020-publication-original-peer-reconciliation.json)
checks all312 candidate cells and source hashes/pages, all82 selected county
CSV controls, the amended state certificate and the separate original-state
discrepancy. It does not certify all historical native or method columns, nor
assert a common release vintage for the original state and county publications.

The [2020 Alcorn complete original native ledger](../2020-native-alcorn-original-readings.json)
is a separately bounded three-candidate,17-constituent reading of PDFpages2–3.
`make_2020_native_position_hints.py` reconstructs vote-free physical positions
from the peer's immutable 40-view source body, verifying its stored and original
hashes before extraction; `extract_2020_native_original_ocr.py` renders the raw SOS original
anew and retains two Tesseract modes as provisional source-pixel aids.
`record_2020_native_alcorn_original.py` records the eight enlarged original
visual readings, literal headers, four unused source columns and all66
candidate positions, then checks own printed TOTAL and peer positions.
The [position hints](2020-native-position-hints-v1.json) contain no peer vote
values or native labels. Cell windows are targeting aids, not approved exact
numeric polygons. This publication does not complete historical statewide
native or method coverage.

`record_2020_native_manual_original.py` takes complete original-page literal
headers and three candidate vectors as direct visual inputs; county and peer
controls run after those inputs are explicit. The separate
[Benton original](../benton-2020-native-original-readings.json),
[Benton amended](../benton-amended-2020-native-original-readings.json),
[Greene](../greene-2020-native-original-readings.json),
[Wilkinson](../wilkinson-2020-native-original-readings.json),
[Issaquena](../issaquena-2020-native-original-readings.json), and
[Noxubee](../noxubee-2020-native-original-readings.json) ledgers add six
publication views to Alcorn. Seven separate2020 publications/62 source-native
columns across versions/297 candidate grid positions close exact-source
printed TOTALs and post-read peer positions. Benton original/amended are
separate source keys despite equal numbers. The provisional independent OCR
attempts for these original PDFs remain retained, including broad-row targeting
failures; they do not supersede the direct whole-page readings.

`record_2020_native_sharkey_originals.py` adds the separately published
[Sharkey original](../sharkey-original-2020-native-original-readings.json) and
[Sharkey amended](../sharkey-amended-2020-native-original-readings.json)
PDFpage2 grids. Each has ten native source columns, physical TOTAL column11,
and33 candidate positions; the visually read values happen to agree across
the two different PDF originals. Nine publications across seven counties now
contain82 source-native columns across versions and363 three-candidate grid
positions. The outer page margin is not an extra source column. These checks
are bounded and leave the remaining 2020 and 2018 native scopes open.

`record_2020_native_calhoun_tishomingo_smith.py` adds complete original
[Calhoun](../calhoun-2020-native-original-readings.json),
[Tishomingo](../tishomingo-2020-native-original-readings.json) and
[Smith](../smith-2020-native-original-readings.json) candidate grids.
Tishomingo and Smith have two actual source pages each, with unused template
columns left null. Smith's source line wrap after `Clear Springs-` is literal.
The bounded direct-original2020 set now has12 publications across ten counties,
124 native columns across vintages and528 three-candidate grid positions.
Original-pixel OCR on Smith page2 had broad repeated candidate bands; those
failed hints are retained, while the accepted values were read from the
complete original page. It is not a statewide historical native partition.

The independent [v2 vote-free physical hints](2020-native-position-hints-v2.json)
are derived only from the peer's immutable 50-publication source body, with
its stored and original bytes verified. V1 remains byte-identical. The
`--hints-version v2` original OCR runs and
`record_2020_native_tunica_stone.py`, `record_2020_native_attala_amite.py`,
and `record_2020_native_clarke.py` reproduce five further complete original
three-candidate publications: [Tunica](../tunica-2020-native-original-readings.json),
[Stone](../stone-2020-native-original-readings.json),
[Attala](../attala-2020-native-original-readings.json),
[Amite](../amite-2020-native-original-readings.json), and
[Clarke](../clarke-2020-native-original-readings.json). Stone's Senate block
precedes president on both original pages. The
[Amite correction history](../2020-native-amite-correction-history.json)
preserves two rejected initial visual readings and expanded same-original
candidate rows. Seventeen separate 2020 publications across15 counties now
contain215 native columns across vintages and891 candidate grid positions.
Original/source controls and post-read peer comparisons pass at each position;
remaining 2020 and both2018 native stages remain outside this bounded set.

The independently frozen [v3 vote-free hints](2020-native-position-hints-v3.json)
target two further county originals using the peer's exact immutable
65-publication source-position body. `record_2020_native_kemper_winston.py`
reproduces [Kemper](../kemper-2020-native-original-readings.json) and
[Winston](../winston-2020-native-original-readings.json) from complete original
PDFpages2–3. They add26 source-native columns and132 three-candidate grid
positions:19 reviewed county publications,241 native across versions and
1,023 candidate positions in total. All three vectors per publication close
their printed TOTAL and own county publication control. Numeric values and
roles agree the peer; the single Kemper page2 column9 literal header differs.
The original prints `Lynville` while the peer derivative has `Lynnville`.
Three candidate rows inherit that one header difference. [The original
header review](../2020-native-kemper-header-review.json) retains the first
visual read, rejected interim edit, full raster and enlarged original crop
with hashes. Literal labels are source-scoped and do not establish a native
ID or a current2026 geography crosswalk. The remaining85 of104 county
publications and both2018 native stages stay outside this direct-original
check.

`record_2020_native_newton.py`, `record_2020_native_jasper_originals.py`
and `record_2020_native_george.py` add four complete-original publications:
[Newton](../newton-2020-native-original-readings.json),
[Jasper original](../jasper-original-2020-native-original-readings.json),
[Jasper amended](../jasper-amended-2020-native-original-readings.json), and
[George](../george-2020-native-original-readings.json). The two Jasper source
publications retain separate original hashes and all physical source positions.
George's PDFpage4 has the sole TOTAL and ten unprinted template columns.
This makes23 direct-original 2020 publications across20 counties,313 native
columns across vintages and1,320 candidate positions. All three native
candidate vectors per publication close their exact printed TOTAL and own
county publication controls. Independent peer vote/role/literal checks agree
apart from the separately documented Kemper literal header. Eighty-one
other2020 actual county publications and the statewide2018 native partitions
still require direct native original reconciliation; no cross-year/current ID or geometry
equivalence follows. An earlier report/SCHEMA draft counted279 by omitting
the two Jasper17-column source versions from its sum. The source rows and votes
did not change; [the arithmetic correction](2020-native-count-correction.json)
retains both numbers and all four added publication counts.

The separate [v4 vote-free hints](2020-native-position-hints-v4.json)
freeze positions from the peer's immutable70-publication original witness.
`record_2020_native_washington_originals.py` independently reads both
[Washington original](../washington-original-2020-native-original-readings.json)
and [Washington amended](../washington-amended-2020-native-original-readings.json)
complete PDFpages2–3. Each version prints19 native columns, a physical
page3 TOTAL and two unprinted template columns. Both three-candidate
vectors close their separately published TOTAL and county controls; all132
source positions, roles and literal headers agree the frozen70 peer after
the original readings. This raises the bounded scope to25 publications,
351 native observations across vintages and1,452 candidate positions for
21 counties. The two Washington publications retain distinct raw hashes,
page receipts and source keys even where their vote vectors are equal.
Seventy-nine published2020 native scopes and the statewide2018 native grids
remain open; physical source columns imply no current precinct crosswalk.

The same immutable70 vote-free positions also target five further separately
original-read publications. `record_2020_native_carroll_original.py`,
`record_2020_native_clay_original.py`,
`record_2020_native_clay_amended_original.py`, and
`record_2020_native_yalobusha_originals.py` reproduce
[Carroll](../carroll-2020-native-original-readings.json),
[Clay original](../clay-2020-native-original-readings.json),
[Clay amended](../clay-amended-2020-native-original-readings.json),
[Yalobusha original](../yalobusha-original-2020-native-original-readings.json),
and [Yalobusha amended](../yalobusha-amended-2020-native-original-readings.json).
Each version has its own original hash, two full-page rasters and physical
source columns. Yalobusha page3 has one native column followed by physical
`TOTAL` column2 and nine unused/null template columns. Their 66 source-native
observations and330 candidate positions bring the bounded2020 direct-original
scope to30 publications,417 native across vintages and1,782 positions in
24 counties. Every source candidate vector closes its printed TOTAL and
county control; all peer values/roles/literal labels agree after original
reading. Seventy-four remaining2020 publication-native scopes, both statewide
2018 native partitions and current geometry remain separate open gates.

`record_2020_native_choctaw_originals.py` and
`record_2020_native_quitman_original.py` read [Choctaw original](../choctaw-original-2020-native-original-readings.json),
[Choctaw amended](../choctaw-amended-2020-native-original-readings.json),
and [Quitman](../quitman-2020-native-original-readings.json) from complete
source PDFs. Choctaw's header literally prints `Bywy`; an upright original
crop is retained alongside the complete page. The two Choctaw versions are
distinct source hashes/roles despite matching candidate vectors. Quitman has
ten native columns and TOTAL on one PDF page. All165 new candidate positions
close exact-source TOTALs/controls and agree peer values/roles/literal labels
only after original readings. The bounded direct-original 2020 scope is now
33 publications,453 native observations across versions and1,947 source
candidate positions in26 counties;71 publication-native scopes remain open.
The later [v5 position-only hint](2020-native-position-hints-v5.json) freezes
83 non-Coahoma source layouts from the peer's immutable85-publication witness.
It contains source hashes, pages, physical header boxes, roles and Senate row
bands only; it imports no vote or literal-header values. The two separately
reviewed Coahoma 2020 publications are outside that additional-layout body.
Unreviewed v5 pages remain unknown until independent original extraction.

The separately frozen [v6 position-only hint](2020-native-position-hints-v6.json)
targets93 non-Coahoma publications from the independent immutable95-view
witness. Its source hashes, pages, physical source-column roles/header boxes
and Senate row bands contain no peer vote or literal-header values. It
extends targeting to the five newest source pairs/variants while retaining
v1–v5 hashes and meanings unchanged; it is not an accepted native transcript.

`record_2020_native_grenada_original.py` reads the complete original
[Grenada Senate grid](../grenada-2020-native-original-readings.json) on
PDFpages2–3. Thirteen native columns and one printed TOTAL close each of
the three source/county candidate controls, including the literal header
`Sweethome Holt#2 Fire Stat`. All66 printed/unused candidate positions,
roles and literal headers agree the separately frozen85-publication peer
only after direct original transcription. The bounded direct-original
2020 scope is34 publications,466 native observations across vintages and
2,013 candidate positions in27 counties. Seventy publication-native
scopes remain unreviewed, and no 2024 or current native identity is inferred.

`record_2020_native_jefferson_original.py` and
`record_2020_native_claiborne_original.py` independently read both complete
PDFpage2–3 Senate grids from original SOS bytes. The [Jefferson](../jefferson-2020-native-original-readings.json)
and [Claiborne](../claiborne-2020-native-original-readings.json) ledgers retain
12 and11 actual native columns respectively, each with one page3 TOTAL and
otherwise unprinted template cells set null. All132 positions close their
own printed source and county controls; the frozen85 peer was compared only
after transcription and agrees in values, roles and source-literal labels.
The bounded direct-original 2020 scope is36 publications,489 native
observations across vintages and2,145 candidate positions in29 counties.
Sixty-eight publication-native scopes remain unreviewed.

`record_2020_native_franklin_original.py` reads all14 Franklin native
columns on complete original PDFpages2–3 and physical page3 TOTAL column4.
The [Franklin source ledger](../franklin-2020-native-original-readings.json)
retains66 candidate-or-null positions, complete source rasters and literal
header/role positions. All three native sums close the printed source and
county controls before comparison with the frozen85 peer; the peer agrees
in all positions and labels. Direct-original 2020 coverage is37 actual
publications,503 native observations across vintages and2,211 candidate
positions in30 counties;67 publication-native scopes remain unreviewed.

`record_2020_native_perry_original.py` reads the complete original
[Perry PDFpage2–3 Senate grid](../perry-2020-native-original-readings.json):
15 native columns, physical page3 TOTAL column5 and six unused/null page3
template columns. Three source-native vectors close the printed publication
and county controls; all66 source candidate positions agree frozen85 peer
after direct original review. The initial page2 column3 header read `1120`
was corrected by an enlarged original-only crop to printed `5120`. Both
readings, original/crop hashes and no-vote-change scope survive in the
[Perry correction history](../2020-native-perry-correction-history.json).
Direct-original 2020 coverage is38 actual publications,518 native
observations across vintages and2,277 candidate positions in31 counties;
66 publication-native scopes remain unreviewed.

`record_2020_native_webster_original.py` reads [Webster's complete PDFpage2–3
Senate grid](../webster-2020-native-original-readings.json):17 native
columns, physical page3 TOTAL column7 and four unprinted/null template
columns. A full-page first read of the Hyde-Smith TOTAL as4,057 failed
native closure. The [correction history](../2020-native-webster-correction-history.json)
retains it beside the source-only enlarged crop that prints4,067; no native
cell was fitted to the ten-vote first-read discrepancy. After correction all
three source/county totals and66 frozen85 peer source positions agree.
Direct-original 2020 coverage is39 publications,535 native observations
across vintages and2,343 candidate positions in32 counties;65
publication-native scopes remain unreviewed.

`record_2020_native_prentiss_originals.py` reads both actual Prentiss
publications independently from their complete original PDFpages2–3. The
[original](../prentiss-original-2020-native-original-readings.json) and
[amended](../prentiss-amended-2020-native-original-readings.json) source
tables each have15 native precinct columns, physical `TOTAL` at page3
column5, and six unused/null template columns. Their printed three-candidate
totals are respectively2,694/7,603/227 and2,714/7,651/229; every native
vector closes its own source, and all132 source cells and literal labels
agree the frozen85 peer only after original transcription. The publications
are nonadditive alternatives. Direct-original 2020 coverage is41
publications/565 native observations across vintages/2,475 candidate
positions in33 counties;63 publication-native scopes remain unreviewed.

`record_2020_native_peer_metadata_history.py` reads, without changing, the
coordinator's lossless earlier12/extension witness archives and the current
owned readings. Its [metadata history](../2020-native-peer-metadata-update-history.json)
records exact compressed/raw byte hashes, paths and earlier/later peer hashes
for all39 archived source-reading bodies. Seventeen differ only in the four
explicit comparison-metadata fields; all39 source-semantic digests (including
rows, votes, labels, positions and source/raster hashes) agree exactly. The
earlier witness/peer comparison and later repeat comparison remain distinct.
The [39-archive input pin](2020-native-peer-metadata-history-inputs-v1.json)
freezes the exact earlier archive paths and raw/stored hashes; later files
added to a coordinator archive directory do not silently expand this first
comparison.

`record_2018_native_issaquena.py` separately reads the complete original
Nov6 and Nov27 Issaquena special-election PDFpage2 grids. Its [stage-native
ledger](../2018-issaquena-two-stage-native-original-readings.json) and
[flat source cells](../2018-issaquena-two-stage-native-original-cells.csv)
retain each candidate, five physically distinct source precinct columns,
physical `TOTAL` column6 and five visibly unprinted template columns. Across
the two stages there are36 printed numeric and30 unprinted/null positions;
all native vectors close their own printed TOTAL and independently checked
county controls. Nov6's simultaneously printed regular ClassI Senate office
remains only in the complete original source and is excluded from the ClassII
special pool. The older Nov6 county-control ledger's `source_TOTAL_column=4`
is a **machine extraction ordinal** caused by merging three header columns;
its pixel bounds point to physical6. The raw ordinal and corrected physical
role remain separate evidence. This one-county native check does not accept
all164 historical stage/county native scopes or any cross-stage/current ID.

`freeze_2018_franklin_header_case_prior.py` losslessly pins the earlier
Franklin two-stage JSON and CSV with literal `McCall` in physical page2
column9. `record_2018_native_franklin.py` now retains the directly re-read
printed `Mccall` in both actual stage publications. The owned
[correction history](../2018-franklin-header-case-correction-history.json)
compares every earlier/current row, records six header-only differences,
preserves both raw/stored prior hashes and the two original-only upright
source crops. No vote, role, physical position, source hash or stage identity
changed; this is a source-literal case correction, not a normalized ID join.

`record_2018_native_manual_original.py` is the source-first builder for further
two-stage original readings. `record_2018_native_clay.py` types every Clay
Nov6 special and Nov27 runoff candidate value from each complete original
PDFpage2–3, retaining the printed labels, 14 native columns per stage,
physical page3 `TOTAL` column4 and seven unprinted/null template columns.
The earlier runoff county-control `TOTAL` locator3 remains an unaccepted
machine ordinal. The [Clay direct reading](../2018-clay-two-stage-native-original-readings.json)
and [flat cells](../2018-clay-two-stage-native-original-cells.csv) close
each stage's separately printed county controls. Only afterward
`reconcile_2018_clay_peer.py` checks all132 source/page/physical-column/
candidate positions against the exact frozen28-view independent peer, with
zero value, role, raw-hash, FIPS or literal-header differences. The
[reciprocal record](../2018-clay-native-peer-reconciliation.json) does not
assert identical source-key wrappers, raster pixels, OCR crop polygons or
current geography.

`record_2018_native_smith.py` independently transcribes both complete Smith
PDFpage2–3 special/runoff grids before consulting the peer. Each stage prints
18 native columns, page3 physical `TOTAL` column8 and three unused/null
template columns. The [source readings](../2018-smith-two-stage-native-original-readings.json)
and [flat cells](../2018-smith-two-stage-native-original-cells.csv) retain
the wrapped `Clear Springs-\nPineville` header literally and all six distinct
candidate-stage vectors, which close printed county controls.
`reconcile_2018_smith_peer.py` compares all132 candidate/source positions to
the exact frozen40-view independent peer only after the source transcription;
the [reciprocal record](../2018-smith-native-peer-reconciliation.json) has
zero source-position, vote, role, raw-hash, FIPS or literal-header differences.
It does not establish cross-stage/current geography or exact raster/crop
equivalence.

`record_2018_native_montgomery.py` independently reads both complete
Montgomery original PDFpage2–3 Senate grids. Each stage has 15 native columns,
page3 physical `TOTAL` column5, and six visibly unused/null template columns.
The [stage readings](../2018-montgomery-two-stage-native-original-readings.json)
and [flat cells](../2018-montgomery-two-stage-native-original-cells.csv)
preserve the literal printed capitalization/wrap and all six candidate-stage
vectors. Only afterward `reconcile_2018_montgomery_peer.py` compares all132
source/page/physical-column/candidate positions with the exact frozen46-view
independent peer; the [reciprocal record](../2018-montgomery-native-peer-reconciliation.json)
has no vote, role, literal header, original hash or FIPS difference. The
regular ClassI office on Nov6 remains outside the special-election pool,
and no same-name cross-stage/current geographic identity is inferred.

`record_2018_native_quitman.py` separately transcribes the actual Nov6 and
Nov27 Quitman original PDFpage2 special/runoff grids: ten native columns and
physical `TOTAL` column11, with no unused template columns. The [stage
readings](../2018-quitman-two-stage-native-original-readings.json) and [flat
cells](../2018-quitman-two-stage-native-original-cells.csv) close all six
candidate-stage vectors against printed county controls. The generic
`reconcile_2018_manual_peer.py` subsequently checks all66 source positions
against the exact frozen50-view independent CSV. The [reciprocal
record](../2018-quitman-native-peer-reconciliation.json) agrees at every
vote, role, literal header, original hash and FIPS; no cross-stage or current
identity is inferred.

`make_2018_vote_free_targets.py` makes a separate [164-source vote-free
locator](2018-vote-free-targets-v1.json) from the independent machine block
aids, retaining only source/page/render/column/candidate row boxes and exact
aid hashes. It excludes candidate values, OCR text, literal native labels,
roles and IDs by schema. `extract_2018_original_numeric_aid.py` freshly
renders exact SOS original PDF bytes and records raw whole-page OCR tokens;
optional per-cell second-pass OCR remains diagnostic. These machine boxes
can omit or misalign columns and crop digits. Missing OCR never becomes zero
and none of its numbers enter an accepted native ledger without direct
original-page review and printed-total/source-position reconciliation.
The full [164-source diagnostic validation](../2018-original-numeric-aid-validation.json)
pins all545 stored diagnostic/TSV assets across381 actual original pages.
Its12,476 tentative target cells yield7,004 single numeric tokens,4,430
empty targets and1,042 ambiguous targets; eight machine source grids have
zero targets. `validate_2018_original_numeric_aid.py` checks every asset,
source/page/target position and count offline. The OCR aids remain unaccepted
even when a token looks numeric; no candidate, role, zero or current native ID
is derived from that count.

The separate [frozen78 value-free position hint](2018-frozen78-vote-free-position-hints-v1.json)
uses the independent immutable 78-view original-source ledger only for page,
header-box and candidate-row coordinates. Its strict schema excludes peer
votes, candidate names, native labels, roles and IDs. `extract_2018_frozen78_original_pixels.py`
freshly renders each hash-verified SOS PDF page at2.7 and records full-page
PNG, upright header OCR and each candidate-cell OCR token without accepting
them as facts. [Original-pixel validation](../2018-frozen78-original-pixels-validation.json)
checks all78 source hashes,144 raster hashes,1,584 header-crop hashes,
4,752 candidate-crop hashes, physical positions and222 stored asset hashes.
Only after extraction does `compare_2018_frozen78_original_ocr.py` load the
frozen independent candidate fields. Its [diagnostic result](../2018-frozen78-original-ocr-peer-diagnostic.json)
records3,184 exact OCR numbers of3,614 reported printed numeric positions,
430 numeric disagreements, one missed original X,12 nonblank OCR tokens in
positions reported unprinted, and767 header OCR disagreements. All remain
review leads. Matching OCR is not accepted original transcription, numeric
polygon, blank/zero, source label or current reporting geography. The 78-view
physical aid is distinct from the broader164-source machine-target aid.

`record_2020_native_coahoma_originals.py` reads the complete actual original
and amended Coahoma PDFpages2–3 separately from their exact source bytes.
The [two-publication ledger](../2020-coahoma-two-publication-native-original-readings.json)
and [flat cells](../2020-coahoma-two-publication-native-original-cells.csv)
retain18 printed native columns per publication, one page3 physical `TOTAL`
column8 and three unused null columns. Each of the six candidate/publication
vectors closes its printed TOTAL and earlier original county control:
original Espy6,452/Hyde-Smith2,161/Edwards46; amended6,337/2,133/46.
`reconcile_2020_coahoma_original_peer.py` then compares all132 values,
roles, physical ordinals, literal headers and source hashes against the
independent frozen104-publication witness; the [comparison](../2020-coahoma-two-publication-native-peer-reconciliation.json)
records zero field differences. The versions remain nonadditive; no native
cross-publication or current geometry identity is inferred.

`record_2018_native_noxubee.py` independently transcribes both actual
Noxubee PDFpage2 Senate stage grids: eight native columns, physical `TOTAL`
column9, two unused/null columns. The [readings](../2018-noxubee-two-stage-native-original-readings.json)
and [flat cells](../2018-noxubee-two-stage-native-original-cells.csv)
close all four Nov6 special and both Nov27 runoff candidate vectors to their
separate printed county controls. Subsequently the generic peer check
compares all66 positions to the exact frozen16-view source CSV; the [peer
record](../2018-noxubee-native-peer-reconciliation.json) has no numeric/null,
role, literal-label, original-hash or FIPS differences. Blank party fields
and cross-stage/current geography remain unassigned.

`record_2018_native_yalobusha.py` reads both complete original Yalobusha
PDFpages2–3 separately:11 printed native columns on each stage's page2,
physical `TOTAL` at page3 column1 and ten page3 unused/null positions.
The [stage ledger](../2018-yalobusha-two-stage-native-original-readings.json)
and [flat cells](../2018-yalobusha-two-stage-native-original-cells.csv)
retain all four November6 special and two November27 runoff vectors plus
literal headers. Only after direct reading, `reconcile_2018_manual_peer.py`
compares all132 source positions against the frozen58-stage independent
CSV; the [result](../2018-yalobusha-native-peer-reconciliation.json)
has zero vote/role/header/source-hash/FIPS differences. The regular ClassI
rows on November6 remain distinct. No cross-stage or current geographic
identity is asserted.

`record_2018_native_greene.py` separately reads both complete original
Greene PDFpages2–3:13 native columns per stage, page3 physical `TOTAL`
column3, eight unprinted template columns. The [direct readings](../2018-greene-two-stage-native-original-readings.json)
and [flat cells](../2018-greene-two-stage-native-original-cells.csv)
close all six candidate-stage vectors to their printed source controls.
`review_2018_greene_peer_literal.py` compares all132 positions only after
those original readings. Votes, roles, hashes and FIPS agree the frozen16
peer. Both original page3 first headers visibly print `Mclain`; the peer
derivative prints `McLain`. The [review](../2018-greene-native-peer-reconciliation.json)
retains six explicit source-literal capitalization differences, exact
enlarged original crop/hash evidence, and the lossless [initial peer
disagreement](2018-greene-initial-peer-differences.json.gz). Neither spelling
is silently substituted for the other; no cross-stage/current ID inference.

`record_2018_native_leflore_original.py` independently transcribes all four
Nov6 special-candidate rows from the complete [Leflore original PDFpages2–3](../2018-leflore-Nov6-native-original-readings.json).
The [flat positions](../2018-leflore-Nov6-native-original-cells.csv) retain18
native columns, PDFpage3 physical `TOTAL` column8 and three unprinted
template columns per candidate. Original page rasters and [complete Espy
source-row strips](../qa/2018-leflore-direct-original/complete-Espy-source-rows-4x.png)
are hash-pinned. The18 visible Espy native integers add to5,853 while
the same PDF prints5,863 as TOTAL; `candidate_checks` preserves the
native-minus-printed difference **-10**, with no fitted column or allocation.
Bartee185, Hyde-Smith2,199 and McDaniel493 each close. County/state control
uses the printed TOTAL with its own scope; regular ClassI rows stay separate.

`record_2018_native_perry.py` independently types both complete original
Perry PDFpages2–3. Each stage prints15 native columns and a page3 physical
`TOTAL` column5; six unused positions per candidate remain null. The
[source-position ledger](../2018-perry-two-stage-native-original-readings.json)
and [flat CSV](../2018-perry-two-stage-native-original-cells.csv) close
all six distinct candidate/stage vectors to original county controls.
`reconcile_2018_manual_peer.py` checks the 132 positions only after the
original readings; the [frozen78 reciprocal result](../2018-perry-native-peer-reconciliation.json)
has zero value/role/literal-header/hash/FIPS differences. Six source
headers per stage wrap across lines. The initial vote-identical, prematurely
folded header derivatives are retained as exact gzip originals under
[the archive manifest](2018-perry-initial-folded-header-archive/archive-manifest.json).
`validate_2018_perry_header_history.py` verifies that the final ledger
changed only those36 candidate-label representations, preserving every
vote, role and source position; see [the history](../2018-perry-header-wrap-correction-history.json).
Neither source column nor matching name authorizes a cross-stage or current
precinct identity.

`record_2018_native_coahoma.py` and `record_2018_native_kemper.py` each type
the two distinct special-election stage grids directly from complete original
PDFpages2–3. Coahoma has18 native columns per stage and a page3 physical
`TOTAL` at column8; Kemper has14 native columns per stage and a page3
physical `TOTAL` at column4. The four November6 and two November27
candidate vectors per county close their own printed/county controls, with
unprinted template cells retained as null. The [Coahoma ledger](../2018-coahoma-two-stage-native-original-readings.json)
and [Kemper ledger](../2018-kemper-two-stage-native-original-readings.json)
retain complete page raster hashes, original source hashes, physical columns,
literal wrapped labels and candidate/party scopes. Only after original
reading, `reconcile_2018_manual_peer.py` compares all132 positions per
county to the immutable78-view peer source. The separate [Coahoma](../2018-coahoma-native-peer-reconciliation.json)
and [Kemper](../2018-kemper-native-peer-reconciliation.json) results report
zero value/null/role/header/source-hash/FIPS differences. No matched name
or column establishes a cross-stage or current reporting identity.

`record_2018_native_tunica.py` reads both complete original Tunica
PDFpages2–3 separately:12 native columns per stage, physical page3 `TOTAL`
column2 and nine unused null columns. All six candidate/stage vectors close
their own printed/county controls in the [direct ledger](../2018-tunica-two-stage-native-original-readings.json)
and [flat positions](../2018-tunica-two-stage-native-original-cells.csv).
`review_2018_tunica_peer_literal.py` compares all132 positions after that
reading, finding complete numeric/null/role/source-hash/FIPS agreement but
six literal p2c2 differences. Both unaltered original source crops visibly
print `Mhoon Landing`; the independent frozen78 derivative prints `Moon
Landing`. The [qualified comparison](../2018-tunica-native-peer-reconciliation.json)
pins both crops, source PDF hashes and a lossless archive of the first
unqualified comparison failure. Neither name is silently normalized, and
no cross-stage/current precinct identity is inferred.

`record_2018_native_calhoun.py` independently reads both actual complete
Calhoun PDFpage2 Senate special-stage grids. Each prints10 native columns,
then physical `TOTAL` column11, with no unused columns. All four Nov6 and
two Nov27 candidate vectors close the source/county controls. The [direct
ledger](../2018-calhoun-two-stage-native-original-readings.json) and [flat
positions](../2018-calhoun-two-stage-native-original-cells.csv) retain both
source hashes, original page rasters, literal headers and roles. The
[subsequent frozen78 peer check](../2018-calhoun-native-peer-reconciliation.json)
agrees all66 values, roles, source hashes, FIPS and headers without implying
any cross-stage or current reporting geography equivalence.

`record_2018_native_sharkey.py` independently types the complete actual
PDFpage2 Sharkey special and runoff Senate blocks. Each stage has10 native
columns and physical `TOTAL` column11; all six separate candidate/stage
vectors close the original county controls. Its [direct ledger](../2018-sharkey-two-stage-native-original-readings.json)
and [flat positions](../2018-sharkey-two-stage-native-original-cells.csv)
keep every original page/source hash and literal multi-line header. The
[post-reading frozen78 comparison](../2018-sharkey-native-peer-reconciliation.json)
agrees all66 candidate positions. The runoff's actual PDFpage2 carries a
printed `Page:1` footer; PDF and printed page identities remain distinct.
The `X` marks in its separate school-board rows are retained by the full
original PDF and are not Senate vote cells.

`record_2018_native_winston.py` reads the two separate complete original
PDFpages2–3 Winston special stages:12 native columns each, physical page3
`TOTAL` column2 and nine unused null columns. All six candidate/stage
vectors close their printed source and earlier county controls. Its [ledger](../2018-winston-two-stage-native-original-readings.json)
and [flat cells](../2018-winston-two-stage-native-original-cells.csv)
preserve original page/source hashes, positions, separate stages and literal
headers. The first full-page reading had `Nann Waiya` at page2 physical
column8; enlarged unaltered original pixel crops visibly print `Nanih
Waiya` in both stages. The [correction history](../2018-winston-header-original-correction-history.json)
and [exact archived initial JSON/CSV bytes](2018-winston-header-correction-v1/prior-ledger-pins.json)
prove that only six candidate-label fields changed. After correction,
`reconcile_2018_manual_peer.py` compares all132 positions to the frozen78
independent witness with zero vote/null/role/literal/source-hash/FIPS
differences. No cross-stage/current precinct identity is inferred.

`finalize_2024_named_contract_coverage.py` updates only the *working*
`priority-set.json` coverage/peer-scope metadata after all 82 preferred
source views have complete original 2024 named Senate and nine presidential
readings. [Its audit](../2024-named-contract-coverage-audit.json) pins every
source reading body and the contract bytes. The frozen887 native proposal
under `data/baselines/source/native-priority-v1/` is untouched. The
contract's broad `native_fields_complete` peer gate remains false because
historical and method/ballot fields and current 2026 geographic identity
have separate unfinished scopes; complete named-field coverage does not
imply coordinator acceptance.

`build_2024_all11_contract_dependency.py` embeds the presidential vector in
every preferred source column of the *working* priority contract and writes
the [complete lossless preferred source-field dependency](2024-preferred-all11-source-fields-v1.json.gz).
The contract pins compressed/raw SHA256 and byte lengths. It contains2,266
original source columns (1,736 native,82 TOTAL,437 unused template,11
nonadditive Kemper parallel) and24,926 candidate field positions for two
Senate plus nine presidential names. Each record retains the native source
key, raw PDF hash, literal header, page, physical column, role, all11 values
and the hash-pinned original-reading ledger. Per-source checks close all nine
presidential native vectors to printed TOTAL and original controls. The
earlier direct Tunica/Perry ledgers omitted126 visibly unprinted template
positions; this dependency adds exactly those as explicit nulls (Tunica81,
Perry45), never zeros. The original Coahoma and Pike alternatives remain
separate and nonadditive. These 2024 field positions are not crosswalked to
2026 precincts, and Senate generic/method/ballot fields remain separately
scoped or unavailable where the original grid does not print them.

`inventory_2024_county_panels.py` and `inventory_2024_all_pdf_pages.py`
retain an [all-page OCR locator](2024-county-panel-full-ocr-inventory.json.gz)
for every page of all82 preferred original county publications. Source hashes,
page counts, render hashes and raw OCR text are retained to find statistics
and method panels. Keyword hits are only leads; absent hits are not proof of
source-field absence and no OCR number becomes an accepted value.

`record_lincoln_2024_panels.py` adds [Lincoln's direct complete-original
panel reading](../2024-lincoln-original-panel-readings.json) from original
PDFpages9–10. It losslessly pins the prior14/12 panel ledgers under
`canvass-pre-lincoln-v1/`, then adds one unofficial summary and one statistics
panel to the working source-scoped controls. Page9 prints15,898 ballots cast
and a literal zero registration/0.00% turnout, unusable as a participation
denominator. Page10 prints Senate4,080/11,599, generic47 and contest15,898;
the unexplained172 remains unallocated. The presidential residual69 and
statistics-versus-contest difference is zero. An initial15,909 glyph read and
its generated outputs are losslessly frozen in
[`2024-lincoln-ballots-original-correction-v1/`](2024-lincoln-ballots-original-correction-v1/correction-history.json),
alongside the enlarged original image supporting the corrected15,898. The original has no
under/over/blank or method split on these pages. Header, footer, clerk-stamp
clocks and Unofficial status are retained separately. Earlier peer agreement
continues to apply only to its first14 summary/12 statistics panels.

`freeze_lincoln_ballots_initial_reading.py` stores exact gzip copies of the
first Lincoln15,909 ballot transcription, source script, controls, validator
and report in [`2024-lincoln-ballots-original-correction-v1/`](2024-lincoln-ballots-original-correction-v1/correction-history.json).
The corrected15,898 comes from an enlarged unaltered-pixel crop of original
PDFpage9. The original source, named candidate fields and contest totals are
unchanged; ballots minus contest is zero. This is a source-glyph correction,
not an adjustment chosen to close the contest residuals.

`record_2020_native_union_original.py` reads all three Senate rows and literal
headers from the complete Union original PDFpages2–3. Its 20 native columns,
page3 physical-column10 TOTAL and one unused template column are retained in
[`union-2020-native-original-readings.json`](../union-2020-native-original-readings.json)
and the flat cell CSV. All66 source positions agree the frozen independent
2020 publication witness after original transcription, and the three native
vectors close 2,660/9,572/424. The fresh original rasters and source PDF hashes
are pinned. Its physical row-band hints are not approved digit polygons or a
cross-year/current precinct identity. This publication extends the separately
bounded direct-original 2020 scope to44 actual source views/621 native
observations across versions; 60 other publications remain outside it.

`audit_2020_full_peer_native_scope.py` verifies the immutable
[`peer104 publication snapshot`](../../../data/baselines/source/native-2020-104views-v1/snapshot.json),
combining its102-publication flat candidate grid with the separately pinned
two-Coahoma original ledger only for source coverage. Its
[`read-only audit`](../2020-full-peer-native-scope-audit.json) compares all312
printed candidate TOTALs to our independently original-read publication
controls, checks248 peer page-render hashes plus both Coahoma source preview
sets, and preserves2,131 native observations across104 alternative-version
views. The82 disjoint amended-where-linked selection sums exactly the signed
amended state vector578,691/709,511/23,152. This introduces **zero** own
direct-original native cells: the separately bounded own subset remains44
views/621 observations. One Harrison administrative column is distinct from
the native partition; neither release chronology nor cross-year/current
precinct identity is inferred.

`record_2018_native_sunflower.py` reads both complete original Sunflower
PDFpages2–3, preserving the November6 four-candidate special and November27
two-candidate runoff as distinct grids. Each has17 native columns, a page3
physical-column7 TOTAL and four visibly unused template columns. The
[`source-position reading`](../2018-sunflower-two-stage-native-original-readings.json)
and [post-transcription reciprocal check](../2018-sunflower-native-peer-reconciliation.json)
retain all132 numeric/null positions and original page/render hashes. The
special closes100/5,090/1,904/374 and the runoff5,301/2,034; the separate
Class I rows are not pooled. This raises the bounded own complete-original
2018 scope to43/164 stage grids across22 counties. The independent peer's
full164-stage original witness remains distinct and does not imply these
remaining121 stage grids were independently transcribed here.

`audit_2018_full_peer_native_scope.py` verifies the immutable
[`peer164 source snapshot`](../../../data/baselines/source/native-2018-164views-v1/snapshot.json),
decompresses every pinned byte exactly, checks all original PDF receipt hashes
and414 independently rendered page hashes, and compares each of its492
printed candidate TOTALs to our separate original-read county controls. Its
[`bounded audit`](../2018-full-peer-native-scope-audit.json) retains all164
stage-source comparisons,3,545 native observations, three administrative
columns,6 literal `X` candidate cells as null, and the Leflore special Espy
native-minus-printed −10. It introduces **zero** own direct-original native
readings; the peer's complete coverage is never substituted for the
separately enumerated43 direct stage grids or for a 2026 geographic crosswalk.

`build_2024_field_availability.py` produces
[`2024-field-availability.json`](../2024-field-availability.json) from the
hash-pinned all803-page original-PDF OCR locator and direct-original panel
ledgers. It inventories every preferred82 source PDF, each actual summary and
statistics page read, printed-field presence, and the two nonadditive original
Coahoma/Pike publications. Fourteen preferred standard summaries and13
preferred statistics were directly transcribed; original Pike adds a separate
one of each. Three additional preferred E-013 county summaries contain only
named candidate aggregates and printed percentages, with no generic,
ballot, registration or voting-method fields on the reviewed pages. A
preferred publication with no separately reviewed panel has status
`not_located_by_allpage_original_OCR_no_numeric_field_accepted`, which means
no ballot, generic, method or registration value is accepted from that source
here. It is not a claim the source has an actual printed zero or a proof that
every OCR keyword was recognized. Printed Lincoln registration0 is retained
as an actual glyph and remains an unusable denominator, distinct from null.
Montgomery's printed885 ballots are a separate incompatible panel, distinct
from a missing or zero ballot value.

[`record_union_ballot_styles_original.py`](../record_union_ballot_styles_original.py)
independently reads the same Union original PDFpages8–10's BP-009 report:
58 ordered split/style rows beneath20 printed parent precinct-code TOTALs,
plus Grand Total Voters17,058. Every Party field is unprinted/null. The
source does not define those voters as candidate votes, ballots or a dated
registration universe; the separate vendor profiles print registration17,084.
[`reconcile_union_ballot_styles_peer.py`](../reconcile_union_ballot_styles_peer.py)
agrees all58 split rows and20 parent rows after original reading. The working
priority contract embeds the complete78-row nonadditive administrative view
with null candidate availability. Its codes, split labels and styles do not
crosswalk to preferred SEMS/native vendor rows or current2026 geography.

[`record_three_e013_summaries.py`](../record_three_e013_summaries.py)
independently reads Bolivar, Grenada and Itawamba's complete original E-013
county summary pages: all33 requested named candidate values, printed office
TOTALs and percentages. They are nonadditive county controls, not native
candidate assignments. They print no generic, ballot, registration or method
field on the reviewed pages; all other offices remain in original PDFs.

[`historical-native-complete-dependencies.json`](../historical-native-complete-dependencies.json)
is built by `build_historical_native_dependencies.py` from immutable,
read-only peer snapshots. Each stored component's exact gzip bytes and full
decompressed bytes are verified; every full source object has a canonical
object digest, and every source field/role/mark in the frozen flat rows is
reconstructed from the frozen original-reading JSON. It retains ordered
2020 all104/selected82/alternative22 publication partitions and2018
all164/Nov6 special82/Nov27 runoff82 stage partitions, plus original PDF
receipts,8,316 and13,662 candidate-or-null positions, and independent
county-control audit hashes. The current mutable 2018 peer validation JSON
has advanced since the frozen snapshot, so its *stored immutable* copy is
canonical; no false current-file byte equality is claimed. This complete
peer-source dependency does not upgrade this worker's bounded44/104 2020
and43/164 2018 direct-original native readings to independent full coverage.

`record_2018_native_neshoba.py` independently transcribes both complete
original Neshoba 2018 special-election stages, preserving six distinct
candidate rows across two stages and all three native pages per source.
Each stage has27 native columns, one page4 TOTAL at physical column6, and
five unprinted template columns. The resulting
[`2018-neshoba-two-stage-native-original-readings.json`](../2018-neshoba-two-stage-native-original-readings.json)
contains198 candidate/source positions; [`validate_2018_neshoba_original.py`](../validate_2018_neshoba_original.py)
checks source bytes, independent original rasters, county balances and
post-transcription peer agreement. Enlarged original PDFpage2 headers in
both sources visibly print `Arlington`; the first `Arrington` reading and
all its derivative bytes are retained in
[`2018-neshoba-original-header-correction-v1/`](2018-neshoba-original-header-correction-v1/correction-history.json).
Candidate values and physical positions did not change; five other wrapped
header differences per stage represent source line breaks. No same-name
cross-stage or current-precinct equivalence is inferred.

The three-pass 2018 diagnostic is reproducible with
`make_2018_peer142_position_hints.py`, `extract_2018_peer142_original_tsv.py`,
`recheck_2018_peer142_ambiguous_original_cells.py`,
`denoise_2018_peer142_original_crops.py` and
`compare_2018_peer142_three_original_aids.py`. The value-free hints contain
only original source/physical targeting metadata from the immutable peer142
witness. Complete-page TSV, widened-crop PSM6 and line-masked PSM11 aids are
saved from our original pixels before peer numbers are read. The
[`diagnostic`](../2018-peer142-three-original-aids-diagnostic.json) records
64 additional source-stage views/5,544 candidate positions; OCR agrees on
3,941 of4,416 numeric source positions, with475 numeric and75 blank-field
leads still requiring original rereading. No OCR-derived vote or geometry is
accepted merely from this diagnostic.

`record_2018_native_george.py` independently transcribes the complete
George November6 and November27 original PDFpages2–4, retaining22 printed
source-native columns, page4 TOTAL physical column1 and ten unprinted
template columns per stage. Its 198 candidate/null positions, all six
printed source TOTALs and original hashes agree the independent immutable
peer142 witness only after original transcription. The
[`direct-original ledger`](../2018-george-two-stage-native-original-readings.json)
and [`reciprocal proof`](../2018-george-native-peer-reconciliation.json)
remain distinct from the diagnostic OCR and from current geography.

`record_2018_native_union.py` independently transcribes the complete Union
November6 and November27 original PDFpages2–3. Both print20 native source
columns, page3 TOTAL physical column10 and one unprinted template column.
All132 candidate/null positions and six source candidate vectors close, then
agree the immutable peer142 witness by exact source positions and literal
headers. The [original reading](../2018-union-two-stage-native-original-readings.json)
and [reciprocal check](../2018-union-native-peer-reconciliation.json) do not
join these2018 source columns to the separate Union2024 vendor profiles or
November2026 reporting identities.

`record_2018_native_benton.py` independently renders and reads both complete
Benton PDFpage2 special-election grids: [stage-native
ledger](../2018-benton-two-stage-native-original-readings.json) and [flat
cells](../2018-benton-two-stage-native-original-cells.csv). Each stage has
five physically distinct printed precinct columns, TOTAL physical6 and five
unused/null template columns. The four Nov6 and two Nov27 candidate vectors
close their own source/county controls. Nov6 separately prints the regular
ClassI Wicker/Baria office above the special pool; the original retains it,
while this comparator excludes it. Together with Issaquena, four of164
county/stage native grids are directly source-read; no labels establish a
cross-stage or current precinct join.

`record_2018_native_franklin.py` separately renders/reads the complete
original PDFpages2–3 for November6 and November27. Its [stage-native
ledger](../2018-franklin-two-stage-native-original-readings.json) and
[flat cells](../2018-franklin-two-stage-native-original-cells.csv) retain
14 printed native columns per stage, physical page3 TOTAL column4 and
seven unprinted page3 template columns. The four Nov6 special-candidate
and two Nov27 runoff vectors close their distinct original/county totals;
90 printed numeric and42 unprinted/null candidate positions are explicit.
Both original page2–3 rasters are hashed per stage. The Nov6 regular ClassI
pool remains only in the full source. Six of164 county/stage native grids
are now directly reviewed, without a cross-stage/current geography join.

[asset-manifest.json](../asset-manifest.json) hashes every owned non-cache artifact
other than itself and lists read-only shared original references. Gzip entries
include exact decompressed hashes and sizes. `validate_turnout.py` writes its
result, then builds the manifest and rechecks every listed stored hash without a
later output mutation. `build_asset_manifest.py` can regenerate it after a change.
The self exclusion avoids an impossible hash cycle and excludes no other owned
deliverable. Frozen bounded milestones under `qa/milestones/` preserve exact bytes
for independent replay without relying on a changing aggregate.

The final `attach_complete_peer_v2.py` verifies the read-only immutable
[independent V2 proposal](../../baselines/source/native-priority-v2/snapshot.json)
and its [17-body field companion](../../baselines/source/native-priority-v2-field-evidence-v1/snapshot.json)
by stored and reconstructed hashes. It checks the exact 887/1,736 key order,
all 2,266 preferred source positions and 24,926 eleven-candidate-or-null
positions against this worker's own original-reading dependency. The 165
line-wrap label representations, including two hyphen wraps, remain literal
variants in the respective source ledgers. This is independent evidence for
the proposed historical reporting order, not coordinator acceptance or a
2026 precinct identity mapping.

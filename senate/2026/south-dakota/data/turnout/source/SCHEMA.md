# South Dakota turnout evidence schema

This package owns only `turnout.md`, `data/county-turnout.csv`, and `data/turnout/**` under the South Dakota state directory. All peer/coordinator/news evidence is read-only. No Git changes or publication operations are performed by the worker.

## Primary geography and priority contract

`../priority-set.json` is the dispatch contract. It contains all 691 primary native leaves in exact descending order, all 66 county ancestors, ordered 304 priority keys, ordered 15 leading keys, complete remainder, crossing and preceding integers, original constituent addresses, explicit administrative/unavailable cases, and separate historical native universes. Ancestors are summaries and never added to the leaves. Priority is the 2024 public presidential workbook's four named ticket votes, denominator 428728, explicitly unofficial. Signed statewide controls are 428922. Minimum cardinality is proven only for the observed public native source; certified minimum/membership robustness remains unproved.

Primary order: descending integer `contest_votes`, county FIPS ascending, numeric worksheet ordinal, numeric source row. All units, including zero-valued source rows, remain. Percentages are decimal presentations of exact integer numerators/denominators; threshold tests use `5*cumulative >= 4*total`, never rounded percentages.

`../../county-turnout.csv` is a compatibility filename containing the 691 native rows in this order. `../native-2024.csv` contains the same fields before extra share/priority columns. Neither is a county-only table. `county`, `native_label`, source member and row preserve publisher identities. `sheet_id` is an actual workbook sheetId, not an election reporting-unit ID. Keys `sd:2024:pres:46xxx:sheetN:rowN` are source locators; `official_native_numeric_id` is null because that ID is not exposed. Numbers embedded in labels remain literal strings. Census FIPS 46xxx identifies county ancestors, not precincts. Oglala Lakota 46102 and historical Shannon naming/code are separate vintages, never additional additive counties or an inferred crosswalk.

The fields `harris_dem`, `oliver_lib`, `trump_rep`, `kennedy_ind` each retain a distinct candidate ticket and historical ballot identity; `contest_votes` is their sum. The exact literal ticket headers and complete row/cell XML remain in `../extracts/native2024-complete-OOXML.json.gz`, including string indices, resolved values, type, styles via original XML, addresses, worksheet rows, source headings, ZIP CRCs and member hashes. Raw original ZIP bytes remain once in shared `data/news`, verified by the news receipt and `source-references.json`.

CSV empty fields and JSON null mean unavailable, never zero. Source numeric zeros remain zero. `ballots_cast`, `registered_voters`, `blank_ballots`, `undervotes`, `overvotes`, `generic_writein_votes`, and `valid_named_writein_votes` are distinct null fields in the primary native workbook. SDCL 12-20-21.2 prohibits counting write-ins; no generic or eligible named write-in observations are invented. A legal prohibition is not a claimed numeric column of zeros.

`method_scope=source_label_absentee_unsplit` applies to explicit source absentee labels. Other rows are `unavailable_not_assumed_election_day`. `CENTRAL` in a place/unit name is not classified as a central absentee board. Physical precincts, combined units, absentee groups, polling sites and vote centers are not presumed interchangeable. No method IDs, physical constituent allocations, polling-site-to-residence joins or 2026 geometry are inferred. Each contract constituent records explicit unavailable physical/method cases.

## Separate source scopes

- `../certified-controls.json`: all 198 county/contest vectors, literal source line, PDF page and page line, printed candidate order and statewide footers. 2024 president: Harris/Oliver/Trump/Kennedy 146859/2778/272081/7204. 2022 Senate, other Class III seat/midterm: Bengs DEM/Lesnar LIB/Thune REP 91007/14697/242316. 2020 Senate, same Class II seat: Rounds REP/Ahlers DEM 276232/143987. No 2024 Senate or substituted governor contest is invented.
- `../native-2024-parent-reconciliation.json`: every native county footer and signed candidate vector, preserving differences across 24 counties totaling -48/-1/-143/-2=-194. No residual allocation.
- `../candidate-header-presentation.json`: separate all-race Statewide workbook's literal D7 Trump / E7 Trump1 conflict; native and Aurora headers retained separately. No repair inferred from counts.
- `../native-2022.csv`: original signed precinct PDF's 679 numeric rows, 65 parents, source PDF pages/table-row/y positions. Complete relevant page bbox XML is retained. All 65 close to signed county vectors. No Yankton pages exist in this PDF; its full statewide county control is retained separately.
- `../native-2022-public.csv`: separately acquired public workbook's 687 rows/66 parents, including eight actual Yankton rows. Every public county/candidate vector matches signed controls; its status remains unofficial. Source-specific keys include `public-sheet` to distinguish workbooks from PDF locators. This is not a retroactive repair of the PDF.
- `../native-2020-public.csv`: separate public workbook's 693 rows/66 parents, Rounds276208/Ahlers143970; -24/-17=-41 across21counties versus signed controls. Complete source rows, labels, cell types and XML retained; no allocation. Yankton's literal `Absentee ` label (trailing space retained) is an explicitly labeled absentee group alongside other `Absentee Precinct` rows.
- `../historical-public-native-reconciliation.json`: all county/footer differences for both historical Senate workbooks. No cross-year join is asserted by names, source counts or matching numeric totals.
- `../source-method-controls.json`: source-specific candidate subtotals for explicit absentee labels and remaining rows. The latter are method-unspecified, never Election Day by complement. No complete statewide early-in-person/mail/ED split is asserted.

## Ballots and registration

`../turnout-registration-controls.json` retains all 66 county rows plus statewide controls separately for each official book's turnout and registration table. Turnout table source label is `Votes Cast`; historical ENR headers call the same statewide volumes `Ballots Cast`. Book dates: November5,2024 / November8,2022 / November3,2020. This label correspondence does not create a native ballot allocation.

`registered_voters_turnout_table` and `registration_table.total_active` are distinct observed values. `inactive` stays separate. No blank party-registration cell is filled with zero; complete source lines and original pages preserve party-specific values and blank cells. Party/demographic derivatives outside the question are not expanded. The 2022 turnout denominator597073 differs from registration active597069; 2020 turnout578655 differs from registration active578666. 2024 ENR registration625192 differs from book624175; 2020 ENR578651 is another source-scoped value. No automatic normalization.

`../county-sensitivities.csv` has198rows (66counties x3contests) and all relevant separate candidate/volume/registration controls. `votes_cast_minus_contest_unclassified` is arithmetic only; it is not measured blank/under/over or an outstanding-vote estimate. `../sensitivities.json` ranks all66 counties separately by signed contest, book Votes Cast, turnout-table registration, registration-table active, and active-plus-inactive stock; it also ranks each separate public native Senate universe. Every sensitivity retains complete order, top15, preceding/crossing, minimum80 and remainder. None substitutes for the primary native priority.

## Current candidate scope

`../current-candidate-scope.json` independently parses the retained current SOS candidate-list page. `complete_source_td_cells` preserves all source table cells, including any hidden markup; it is not a claim that every cell was displayed by the browser. Withdrawn DEM Julian Beaudion, active IND Brian L Bengs and active REP Mike Rounds remain distinct source rows/statuses. Bengs's2022DEM identity is never carried into2026IND. The Lincoln publication-ballot PDF's two Senate choices were independently observed through the web tool; exact original bytes are not retained here because the direct county downloads reported404. The original publication URL and observation limitation are explicit. No statewide all-style ballot certification or live ENR IDs are claimed. Current zero/mock/setup counts are excluded.

## Provenance, reconstruction and reproduction

`*.receipt.json` stores exact requested/final URLs, method, UTC retrieval, status, response headers, redirects where observed, full decoded HTTP entity and stored hashes/sizes, source parent/control and POST fields for public exports. HTTP content decoding is separate from lossless storage gzip. Existing older news receipts sometimes omit redirect arrays; no nonexistent redirect evidence is invented. A publisher `Downloaded at` is a download-generation clock, not source update time or cadence.

`*.failed-request.json` retains initial restricted-network failures. Unarchived returns routes returned404 and are rejected; linked Archive URLs succeeded200. The Census API response is HTTP200 HTML “Missing Key” and rejected; FIPS comes from the successful official code text. Failure/404/HTML objects are retained, not admitted as count controls. Captures have immutable filenames and exact hashes. Acquisition scripts skip already captured entities after checking hashes; a deliberate retry uses a new evidence ID.

`source-references.json` copies relevant shared source receipt entries and pins every referenced stored object. Original large PDFs are reused once, read-only. The2020countyPDF149141181rawbytes is one exact gzip stream split into four ordered parts32000000/32000000/32000000/6882528bytes. Shared `data/news/reconstruct_evidence.py` verifies ordered-part, stored-stream and raw hashes; `extract.shared()` independently does the same. It is not four independently compressed PDFs, a truncation, or a simplified derivative. All stored objects are strictly below40000000bytes.

Offline commands from this state directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python data/turnout/extract.py
PYTHONDONTWRITEBYTECODE=1 python data/turnout/extract_historical_native.py
PYTHONDONTWRITEBYTECODE=1 python data/turnout/reproduce_preflight.py
PYTHONDONTWRITEBYTECODE=1 python data/turnout/build_turnout.py
PYTHONDONTWRITEBYTECODE=1 python data/turnout/compare_peer.py
PYTHONDONTWRITEBYTECODE=1 python data/turnout/validate_turnout.py
```

`extract.py` independently parses original PDFs/ZIPs before comparing coordinator preflights. `reproduce_preflight.py` also executes the supplied scripts with only their write destinations redirected to owned paths; numerical logic and shared reads are unchanged. `compare_peer.py` maps the actual independent peer's separate stable schema without editing it, comparing all named candidate columns, all native universes, methods/nulls, county ballots/registration, complete primary order/priority and exact crossing.

`../validation.json` is substantive offline QA, not a live collector claim. `../asset-manifest.json` pins all owned artifacts except itself, plus reused original stored objects; validation is written before the manifest to avoid a circular hash. `source-references.json` retains full relevant original receipts, including source date/HTTP Last-Modified when available. Peer-agreement records input hashes; a subsequent peer edit requires rerunning comparison. Coordinator acceptance, legal scope and current geometry remain external review gates, not reasons to omit owned historical completion.

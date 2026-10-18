# Kansas turnout source and output contract

Scope: October 18, 2026 research. All writes belong to `turnout.md`,
`data/county-turnout.csv` or `data/turnout/`. Other assignments and shared
sources are read-only. No Git operations, source mutation, delegation or
background research agents are part of these scripts.

## Source chain and original bytes

The Kansas SOS [official index](https://www.sos.ks.gov/elections/election-results.html)
links the 2024 broader presidential workbook, 2024 president precinct workbook,
2022/2020 Senate precinct workbooks, corresponding general canvass PDFs, 2026
primary canvass/precinct workbook, and 2022 turnout workbook. Its current HTML
is retained in `acquisition.json` and `current-results-index.body.gz`; its
earlier coordinator capture remains in the shared manifest. The broader
workbook's intermediate parent is the SOS `election-results-data.html` page.

[shared-references.json](shared-references.json) pins exact read-only shared
paths, original/stored SHA256, original/stored byte counts, URL, retrieval UTC,
HTTP status and headers. Most reused sources live under `../../news/` relative
to this directory. Generic `.html.gz` names are capture filenames: their
decompressed contents are the original XLSX or PDF, not HTML conversions.
No original is duplicated. `gzip.decompress(stored_bytes)` reconstructs the
complete original byte stream; the recorded original hash/size must match.
No split reconstruction is needed; every individual stored object is strictly
below **40,000,000 bytes**.

The shared acquisition recorded requested/final URLs but did not retain every
intermediate redirect; that historical metadata limitation is explicit, not
reconstructed from guesses. New [acquisition.json](acquisition.json) entries
record full observed redirect chains and response headers with UTC retrieval,
requested/final URLs, status, response-body hash/size, content-decoding step,
decoded original hash/size and stored gzip hash/size. HTTP errors retain their
whole response bodies; connection failures retain the exception and URL.
The unsuccessful Johnson/Sumner page probes are not count evidence.

Server `Date`, `Last-Modified` and ETag are response clocks/version hints.
They do not establish election certification dates or a live update cadence.
The PDFs are titled `Official Vote Totals`; precinct filenames/main-sheet
headers and actual party headers remain in the lossless original/row extracts.
The 2024 certification release separately dates the canvass to December 2.

The shared House Clerk PDF is referenced read-only from Michigan by exact
path/hash as corroboration of the four-ticket Kansas table; Kansas SOS files
control the calculations. Its original capture headers remain beside that
original, and this package does not invent missing original retrieval UTC.

The current legal-alert reference is a coordinator factual-observation JSON,
**not** a captured signed court order. It is retained read-only with that
qualification. This worker does not hash the external coordinator acceptance
record: it already pins the worker contract and a reverse digest would cycle.

## Elections and candidate identities

| Prefix | Actual election | Candidate keys | Scope |
| --- | --- | --- | --- |
| `president_2024` | November 5, 2024 general president | `harris`, `trump`, `oliver`, `kennedy` | Four tickets reported in SOS canvass/workbooks; priority basis |
| `senate_2022` | November 8, 2022 general Senate, Class III | `holland`, `moran`, `graham` | Actual midterm, other seat |
| `senate_2020` | November 3, 2020 general Senate, Class II | `bollier`, `marshall`, `buckley` | Prior election for the 2026 seat |
| `senate_primary_2026` | August 4, 2026 Senate primary | `anderson`, `davis`, `hamilton`, `hart`, `latz`, `murray`, `neumann`, `parelkar`, `schmidt`, `soetaert`, `taylor`, `marshall`, `naramore` | Eleven Democratic and two Republican candidates; distinct party electorates |

There is no Kansas 2024 U.S. Senate or governor baseline. Candidate aliases
are explicit, contest-scoped lists in `build_turnout.py`; candidate identity
never comes from party alone. Every original candidate label is retained.
`NON`, `-`, `VOTE FOR 1`, generic write-ins and party affiliations are not
silently recoded as candidate identities. Verified candidate party is separate
from source party/header coding. Supplemental `source_header_context` retains
the preceding header cells at their original row numbers, including nonparty
codes; source candidate-label prefixes remain inspectable. The peer stores
some preceding header codes in a field named `source_party`; raw-header
agreement is therefore verified at original cell level, not by equating that
field with a legal party identity.

Statewide 2024 write-ins, named-valid write-ins, under/overvotes, blank ballots
and candidate-by-method counts are unavailable in these statewide originals.
Blank CSV cells/null JSON values mean unavailable, never zero. Generic 2020
write-ins are available only in three county supplements. Their partial-state
sum is not added to a statewide named-candidate denominator. Source controls
and detail coverage must be checked before aggregating any family.

## County CSV

`../../county-turnout.csv` has one row per actual Kansas county (105 rows),
in descending 2024 four-ticket votes. It is a true county parent table, not a
substitution for municipal/ward units. `county_fips` is a five-character Census
identifier, `county_key` is `US-KS-<FIPS>`, and `county` is the display name.
Original literal `Comanche ` is retained separately and explicitly aliases
to `Comanche` for the FIPS/county join. The 2022 turnout table's uppercase
`<COUNTY> COUNTY` labels are retained beside their explicit county join.

`<prefix>_<candidate>` are nonnegative integer named-candidate votes;
`<prefix>_total` is their sum within that named universe. These are not ballots.
The 2026 primary combined total is a publication-volume sum across separate
party primaries, not a general-election turnout denominator. Raw vote values
are retained, including comma formatting in Wyandotte's 2020 footer.

`rank`, `president_2024_share_exact`, `president_2024_share_pct`,
`president_2024_cumulative_votes`, `president_2024_cumulative_share_pct`,
`top15` and `priority80` derive from all 105 counties. `share_exact` is a reduced
integer fraction. Display percentages use 10 decimal places; ordering and
thresholds use original integers. Flags use 0/1. Ties use ascending county FIPS;
none occur in the primary county ranking.

`ballots_cast_2024_broad` and `registered_voters_2024_broad` use the broad
workbook's `2024 Turnout` sheet, whose registration date/status are unspecified.
`ballots_cast_2022`, `registered_voters_2022` and
`advance_ballots_returned_by_mail_2022` use the 2022 turnout workbook. The four
mail `N/A` cells stay blank in the numeric CSV and remain literal `N/A` in the
administrative extract. Raw 2022 ballot figures have known impossible bounds
and are excluded from clean turnout weights; no county swap is imposed.

`registered_voters_2024_november` is a separate monthly publication, not the
broad turnout-sheet stock. `registered_voters_2026_10_01`,
`inactive_voters_2026_10_01`, and `active_voters_2026_10_01` come from the
October workbooks' internally dated October 1 records. Active + inactive equals
total at each county. Registration affiliations and status are not candidate
votes, voting eligibility or a forecast.

The 2024 generic/named-valid write-in, under/over and blank fields remain empty.
`generic_write_in_2020_published_supplement` is an integer only for Shawnee,
Sedgwick and Wyandotte; other counties remain blank. `candidate_universe` and
`source_id` document the priority denominator.

## Native observations and disjoint source families

`extracts/*-rows.jsonl.gz` preserves every worksheet row, XML worksheet path,
row number and decoded original cell values for each retained workbook. An
explicitly present blank XML cell remains `null`; an absent cell stays absent.
The complete original XML/styles/formulas/ZIP bytes remain authoritative.
These row extracts preserve unrelated office/field values without constructing
an unnecessary second analysis of unrelated offices or demographics.

`extracts/native-units.jsonl.gz` has **22,031** source-scoped identities:
4,567 broad 2024, 4,566 precinct 2024, 4,535 Senate 2022, 3,867 Senate 2020,
and 4,496 Senate primary 2026. These are overlapping families and years.
They must not be concatenated into a single state total or polygon count.

Every precinct workbook has a main101-county sheet and four complementary
county sheets. County `COUNTY TOTALS`/`Totals` rows are controls, not additional
constituents. The broad workbook is a separate complete presentation of all
105 counties; its A:F columns identify district/location/precinct contexts.

`unit_key` is `source_id + ':' + first24hex(SHA256(compact UTF-8 JSON
[source_id, sheet, county_native, native_id_fields]))`. JSON uses preserved
insertion order and `ensure_ascii=False,separators=(',',':')`; the full key
must be unique. This is a generated source identity, **not** an official
physical precinct ID. `native_id_fields` retain the actual literal precinct,
code, VTD or district/location fields and header context. Headerless 2022
Johnson column D is retained as an unlabeled source code. VTD and native
precinct identifiers are separate; leading zeros are preserved in strings.

`source_rows`/`xml_path` locate the original evidence. `named_candidate_total`
is null if any required candidate cell is blank/redacted;
`named_candidate_numeric_sum` sums only actually reported integers.
`unknown_named_cells` counts unavailable candidate cells. `role` identifies
the broad reporting context or a historical native identity with unavailable
counts. No residual is assigned to any such identity. `geometry_status` is
unverified historical identity. The source does not separately identify
central/early/absentee/provisional candidate groups. A locality name containing
`Central` does not establish a method group, polling site or polygon.

`extracts/candidate-observations.jsonl.gz` has **121,053** detail observations:
120,186 named candidate cells, 598 generic write-in cells and 269 Sedgwick
contest-total cells. Each retains source candidate label, canonical candidate
key, category, source party/header context, verified candidate party, literal
raw value, parsed integer/null, value status, row, column and cell coordinate.
No duplicate candidate source key is dropped or combined.

`extracts/county-summary-observations.jsonl.gz` retains the separate footer
observations, including Wyandotte 2020 row 131 comma-formatted counts and the
Sedgwick contest-total footer. `extracts/candidate-controls.csv` reconciles
each named candidate's 105 county controls to independently parsed statewide
PDF totals (23 candidates across the four contest groups). Main-sheet numeric
rows plus four county footers establish complete county candidate controls;
individual blanks remain unknown even where aggregate residual is zero.

`extracts/native-county-reconciliation.csv` retains numeric detail, number of
unavailable cells, source county control and difference for every county and
candidate. Positive differences are 44 Shawnee votes in 2024, eight Wyandotte
votes in 2022, and 22 Shawnee primary votes in 2026. They remain unallocated.
`native-inventory.json` records each family's full unit/blank/redacted/zero
coverage. Native orders put only complete integer units in numerical order;
unknowns remain explicitly unranked, outside that order. Ties use county FIPS,
worksheet and ordered original row numbers, so different key hash schemes do
not change the order.

## Dispatch, rankings and sensitivity

`priority-set.json` contains all105 ordered county objects and all525
county/source-family groups, with each of the 22,031 constituents inline.
It retains ordered top15/priority/remainder keys, full county order, exact
crossing/preceding/remainder arithmetic, source hashes, native IDs, original
positions, unknown-count cases, administrative unavailability and current
crosswalk limits. It has no inferred geometry links or invented zero counts.

The authoritative external coordinator acceptance is
`../../coordinator-priority-acceptance.json` relative to this schema directory,
or `../coordinator-priority-acceptance.json` relative to `priority-set.json`.
The legacy worker-owned `coordinator_acceptance:false` records that the worker
does not self-grant approval. It is not a claim that the coordinator rejected
the package. `coordinator_acceptance_record` is a path-only reference; the
external record is authoritative and no reverse acceptance digest is stored.
Acceptance covers historical research dispatch, not physical/current geography,
operational source collection or forecasting.

`rankings.json` gives full all105 order and exact top15/minimum80/preceding/
crossing/remainder for historical named contests, separate ballot vintages,
and dated registration sensitivities. These are different denominators. The
2022 raw-ballot ranking is preserved as source-inconsistent evidence, not a
recommended weight. `native-ranking-2024.json` gives the alternative complete
4,567-context order and its own top15/minimum80 arithmetic; it is not added to
county totals. All native family orders remain in
`extracts/native-unit-order.csv.gz`.

`administrative-controls.json` preserves source-scoped statewide controls and
the unresolved 2024 release-minus-broad differences (1,127 ballots and 12
registrations). `extracts/county-administration.jsonl.gz` retains each county
administrative field, source row, literal label, source date/status and the
four raw `N/A` mail cells. No denominator is silently rescaled or redistributed.

## Independent peer and offline QA

The coordinator's separate `data/news/sumner-2022-control.json` and original
county-home -> election-office -> archive -> 24-page PDF chain are referenced
read-only in `shared-references.json`. The turnout worker independently read
the original PDF's pages 1–2: 7,932 ballots, four blank ballots, 7,869 named
Senate votes, three generic write-ins, 60 undervotes and zero overvotes. Its
literal six method labels and counts remain in that external supplemental
control. They do not repair the statewide turnout workbook, become a new
statewide native family, or alter the accepted 22,031-identity dispatch.

The actual independent partisanship worker is
`78f9c3c0-062f-41f7-87c0-f0a6443f8877`. `compare_peer.py` reads its stable outputs
without edits. `peer-agreement.json` pins their hashes and compares 105 county
records, all shared named-candidate/administrative counts, 1,365 primary2026
county-candidate values, all 22,031 native components/row sets/counts/missingness,
120,879 shared candidate/generic/footer cells and 94,008 original rows. Raw
party/header/blank contexts are compared directly. The peer raw-row evidence
also retains Sedgwick's contest totals, outside its candidate-only derivative.
The exact native key crosswalk uses source/sheet/county/original row sets,
not names alone or an inferred boundary relationship.

`validate_turnout.py` checks original/stored source hashes, exact cell positions,
identity uniqueness, all-county coverage, candidate and method scopes, footer
exclusion, source field bounds and explicit anomaly identities, integer minimum80,
fractional weights, every order/remainder, native constituent conservation,
peer agreement, relative Markdown links, asset hashes/sizes and dependency/cache
absence. Expected source anomalies are asserted as retained facts, not treated
as clean data. `validation.json` distinguishes successful preservation from
unresolved source quality. `asset-manifest.json` inventories all owned files;
it excludes only its own impossible self-digest and records that exclusion.

Standard-library Python and Poppler `pdftotext`/`pdftoppm` are sufficient. No
dependency/cache directories are retained. The acquisition script is optional;
offline build, peer comparison, report rendering and validation need no network.
After final content changes, rerun validation and `finalize_manifest.py`, then
validate the final pinned assets again. Never run the coordinator's shared
whole-manifest acquisition during this worker task.

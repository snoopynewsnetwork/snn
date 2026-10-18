# South Carolina turnout source and calculation schema

Snapshot: 2026-10-18 UTC. Scope: four actual historical general-election
contests, every returned county/native unit and voting channel; separate VREMS
registration/participation universes. No current boundary crosswalk is approved.

## Originals and authority chain

SC Election Commission results index and election-database page link the legacy
ENR applications and `electionhistory.scvotes.gov`. Legacy 2024/2022/2020 HTTP403
captures remain read-only in `../../news/manifest.json`. The historical app's
actual scripts disclose `/api/graphql_pr`, tenant `sc`, contest route/query and
fragments. `../acquire.py` independently recovers the query from those retained
scripts and repeats the public read-only requests. All eight canonical responses
and all eight `splitParty:true` responses were HTTP200 with no GraphQL errors;
their decoded bytes match the earlier originals exactly. No guessed contest IDs,
private authentication, mutations, or individual ballot/CVR queries were used.
The observed public `FilesForSearchContests` query returned empty file lists for
all three years; it does not provide an original-canvass download route here.

Each `*.meta.json` records requested/final URL, parent, UTC retrieval, HTTP
status, complete response headers/redirect headers, request headers, stored and
original hashes/bytes. POST bodies are exact `*.request.json` files with hashes.
`body_path` is relative to that metadata's directory. It either points to an
owned lossless `.body.gz` or an existing shared original, read-only by exact hash.
`stored_encoding` is `gzip` or `identity`; absent means `gzip`. gzip reconstructs
the entire decoded HTTP response entity, including unused fields. HTTP wire
compression is not claimed. Transport failures retain metadata without a body;
403 bodies are retained whole and never parsed as election returns.

The signed NARA-hosted SC certificate, House Clerk originals, published BCM and
absentee/early-history PDFs, historical calendars, current statute chapters,
Senate class rosters, Census county codes, VREMS parent/JS/type/response bodies
are retained or referenced with independent retrieval metadata. Text files and
page PNGs are inspection derivatives; original PDF bytes remain authoritative.
Source verification times (`verifiedAt`), election dates, document dates, HTTP
Last-Modified, retrieval and certification are separate. The database verification
time is not asserted to be the date the election was certified.

## Contests, candidates and controls

| label | contest ID | event/date | role |
| --- | --- | --- | --- |
| 2024-pres | 7131 | 58 / 2024-11-05 | priority, president; no 2024 SC Senate election |
| 2020-senate | 1975 | 20 / 2020-11-03 | previous Class II seat election |
| 2022-senate | 2321 | 12 / 2022-11-08 | Class III, actual midterm |
| 2022-governor | 2183 | 12 / 2022-11-08 | separate actual midterm ticket |

`../candidate-universe.json` retains complete candidate/party/method/contest
metadata, including source candidate-in-contest IDs, party IDs 1-4, party vote
fields, pseudocandidate type, raw winner/write-in/masking flags and spelling.
The source may label generic Write-In `isWriteIn:false`; its
`ALL_OTHER_CANDIDATES` pseudotype establishes the generic category. No named or
legally valid write-in subset is supplied. There is no presidential write-in
option; SC7-13-360 excludes president/vice-president from the write-in space.
Vice-presidential repeated certificate totals and elector names are not votes.

Candidate IDs with pseudotype null and generic ID6 `ALL_OTHER_CANDIDATES` enter
contest-vote totals. ID4 `TOTAL_VOTES`, ID1 `TOTAL_BALLOTS`, and ID10
`PSEUDOCANDIDATE` labeled Overvotes/Undervotes are overlapping controls. They
never enter candidate sums. Separate blank/under/over fields are unavailable in
these history responses and remain null/empty, not invented zeros. Every raw
candidate/control key is retained, even where metadata has incomplete party
subtotals or flags. Candidate ID, party ID and method ID form the cell key;
candidate names alone are never deduplicated. `splitParty:true` returned identical
bytes in every case; it supplies no additional allocation.

## Disjoint geography and source-native identities

Within a contest, state -> 46 counties -> returned precinct divisions is a
disjoint hierarchy. All parent/child candidate and control combined sums are
exact. Parents overlap descendants: sum one level only. County FIPS uses the
independently downloaded Census 2020 county code list, verified against all 46
official county names. County key `SC:45045` means Greenville, for example.
The compatibility filename `county-turnout.csv` legitimately holds the actual
county parents here; it does not replace finer rows. `extracts/native-units.csv.gz`
and the contract retain all finer identities, including zero-vote units.

Historical native key is `SC:<contest-label>:<county-FIPS>:db:<division-ID>`;
the full source path `1/<county-ID>/<precinct-ID>` and JSON pointer are retained.
The database IDs are not FIPS or VTD codes. Native type `Precinct` is preserved
even for administrative Failsafe, Failsafe Provisional and Provisional rows.
There are 138 such explicitly named administrative contexts per contest.
Names containing Central are flagged as role-unresolved, not automatically
treated as central counting boards. Hampton's Early Branch is not Early Voting.
No polling-place, split-ballot-style, vote-center, polygon or 2026 legal identity
is inferred from names, IDs, row counts, or matching across years.

Combined has method ID0. Methods IDs: 6 Absentee By Mail, 1 Election Day,
2 Provisional, 7 Failsafe, 8 Failsafe Provisional; 5 Early Voting in 2022/2024
and 9 In-Person Absentee in 2020. The source's order is preserved in metadata.
Method cells overlap combined cells. 2024/2022 candidate-method sums match at
every level. In 2020, 95 positive candidate cells across 26 precinct contexts
are unallocated in returned methods (Horry7/Lancaster6/Spartanburg13); statewide
and county own rows remain coherent, but 51 method hierarchy rollup cells fail.
No allocation or zero imputation repairs this. Controls also disagree across
views: `controls.json` retains every difference. Published 2022 absentee ballot
statistics conflict with history mail-channel candidate sums; no relabeling or
cause is inferred. These are historical raw method labels, not approved live
method comparators.

## VREMS printed lists and voter history

The official participation parent links `Statistics/VoterHistoryResults`.
Its actual JS publishes GET routes and its returned year options publish GEN.
All 46 counties have original precinct responses for 2024/2022/2020. VOT view
contains `totalRegistered`, `totalVoting` and `percentVoting`; REG county view
independently corroborates registrations, with `totalVoting:0` structural to
the registered-only display. That zero is retained as `raw_total_voting`; the
interpreted participating value is null. No demographic derivative is built;
all demographic fields remain in complete original response bytes.

Printed-list registration includes all active and some inactive voters, as the
parent page explains. VHM participants come from list markings and absentee
returns and differ from BCM ballots. The summary PDF labels its denominator
Total Registered without specifying the historical active/inactive status;
do not silently replace it with VHM registration. Source report date/status and
2026 current-registration displays are not substitutes for election registration.

VHM key `SC:vhm:<year>:<FIPS>:code:<precinctCode>:row:<ordinal>` preserves
codes/names and original positions. It is separate from history database IDs;
no name-based crosswalk is made. County response keys use FIPS only after exact
county validation. Summary flags are explicit and never counted again. The
2024 unnamed county row has 2 registrations/1 participant and remains outside
all named counties in statewide VHM arithmetic; its REG and VOT observations
overlap. Observed drilldown requires a nonempty county name, so no finer
allocation exists for that row. Native counts exclude county summary rows:
2343/2270/2465 for 2024/2022/2020, all exact county rollups.

## Deliverables and numerical conventions

`../extracts/source-positions.jsonl.gz`: canonical two-view original-position
records, 516586 rows. `raw_ordinal` is zero-based within granularRow;
`source_pointer` addresses the complete response; original flags/row values stay
in `raw_value`. Identical alternate-query responses retain complete originals
and request provenance but are not duplicated into this canonical position set.

`candidate-method-controls.csv.gz`: the same 516586 rows, keys, votes, native
labels, candidate/party names, type and lossless `raw_row_json`.
`native-units.csv.gz`: 9823 nodes across all four state/county/precinct hierarchies,
each combined candidate/control vector and available method IDs. State, county
and native precinct rows overlap and must be filtered by level before summing.
`registration-participation.csv.gz`: 7500 county/native/summary/administrative
observations, original source ordinal/pointer and separate REG/VOT semantics.

`../../county-turnout.csv`: 46 wide county rows, sorted by 2024 presidential
votes. `<label>_candidate_votes`, `_generic_write_in`, `_ballots_control`,
`_combined_under_over` are explicit. `<label>_c<ID>_p<PARTY>` retains every raw
candidate/control combined cell; `_pNone` is source null party. Empty values
are unavailable, not zero. `vhm_YEAR_totalRegistered/totalVoting/percentVoting`
are the separate printed-list/VHM scope. Decimal shares are convenience
displays; original integers and exact numerator/denominator control arithmetic.

`county-rankings.csv` contains every contest/county and combined-ballot order.
`<label>-native-order.csv` contains every native precinct, with stable tie-break
by full `geography_key` ascending after votes descending. `sensitivity.json`
holds full all-unit key orders for each ballot/registration/participation basis,
including the unnamed VHM row. `priority-set.json` includes all 46 county keys,
full descending order/remainder, ordered priority keys, every historical native
constituent for all contests, every VHM constituent, and explicit administrative
and unavailable/current-boundary cases. Native priority order is separately
linked; it is not substituted for the county dispatch priority.

For integer total V, threshold is ceil(4V/5), tested as `5*cumulative >= 4*V`.
The minimum descending prefix is the first that passes; the prior prefix must
fail. The dispatch union is top15 plus that prefix. Ties use full keys, not
an unstable source order. All remainder units stay in denominators and totals.
No scaling, allocation, rounding, deduplication, residual repair, 2026 forecast,
collector cadence, live acceptance or current precinct approval is implied.

## Recovered original ENR publications: final additional source scope

Fresh requests recovered genuine legacy applications after the earlier403
observations. Both vintages remain. Observed app helpers/current version files,
English election settings and literal participating-county roster strings pin
the actual state/county EIDs, versions and original download routes. The county
rosters are not inferred from Census or database IDs. State versions are359624
(2024),313728(2022),277849(2020). Source clocks are preserved verbatim with EDT/EST;
their publication/import dates do not establish the cause of source differences.
`shared-news-provenance.json` and `shared-legacy-provenance.json` snapshot exact
authority/script/download metadata with read-only original paths and hashes.

`extract_legacy.py` independently reads three state XMLs and137 county XML ZIPs,
retaining290542 required source nodes including metadata/turnout scopes,
259722 native candidate-method cells and9579 native method contexts. The source
clock, full ZIP/member hashes and sizes, all raw attributes and text are retained.
`extract_legacy_json.py` independently extracts all138 county combined JSON and
English-summary pairs:368 full required source objects (2022 has two required
contests),9635 native rows and43483 candidate cells. All184 county candidate
vectors reconcile exactly to state controls. Native candidate-vector multisets
equal the database in every county; this numerical check asserts no point/ID
join or physical boundary equivalence. Original JSON keys P/V/T/Eid/Cid and
summary candidate/party/order/winner/recount/runoff fields remain raw. Missing T
or native IDs stay absent; candidate sums are explicitly calculated values.

Original state election turnout fields totalVoters/ballotsCast are separate from
contest and VHM scopes. State2024 totalVoters3343423 differs from published BCM
Total Registered3414652; definition/cause is unresolved. All182 available required
county XML native-ballot rollups are exact, while native registration sums differ
from county VoterTurnout registration controls in151 contexts. Neither side is
replaced or allocated. `legacy-turnout-controls.csv.gz` preserves every available
native raw registration/ballot/reporting attribute, including percentReporting
codes; those codes are not interpreted as votes counted. Separate blank/under/
over counts are not supplied by these XML/JSON scopes. Difference of election
ballots and contest votes is not relabeled as a measured blank or undervote count.

The actual2022 Clarendon pinned version313514 and current319025 XML requests
return404; actual settings explicitly disable XML and enable TXT/XLS. The
original pinned detailtxt.zip and detailxls.zip are retained read-only. Complete
detail.txt is reconstructed from the ZIP and its source line/column positions
are retained. Both required contests have28 native rows;1176 native method cells
and42 overlapping county-summary method cells reconcile exactly. Zero registration
in the pinned original is kept distinct from later current-version registration.
No current field is substituted into the pinned history. All141 original report
archives (3state+137countyXML+1countyTXT) are independently validated, alongside
all276 county JSON originals; enabled XLS is additional original evidence.

Literal Charleston method label Provionsal is retained. A documented comparison
alias maps only that spelling to Provisional. Contest-selection whitespace is
collapsed for identifying the unique requested office, while original titles
remain unchanged. Newberry Write-In has an absent XML party/empty summary party;
only the explicit text Write-In identifies that analysis category, and the raw
absence stays raw. Hampton's source presidential label UNC Cornel Wes/ Melina
Abdullat remains verbatim. Original CON Bledsoe is Constitution, while the
database party274 label is Conservative; neither source is relabeled.

The original finer method rows are complete and independently reconcile parent
to child, including2020. They provide a separate historical source alternative
to the database's26 missing finer method allocations, without manufacturing a
distribution or explaining the import gap. Original combined JSON, method XML,
TXT and voter-turnout rosters remain separate even when names coincide.

`priority-set.json` includes source_observations, legacy_source_observations and
original_combined_json_observations with exact original/stored paths, hashes,
sizes, UTC and source IDs. Historical constituents preserve complete raw division
objects, including displayName; granular flags stay complete in originals and
canonical source positions. Original ENR combined/method constituents are
separate arrays with raw names/ordinals, explicit unavailable IDs and locators.
The contract remains below40000000 bytes. Every raw value is independently
recoverable without embedding all method cells inline. The path-only external
coordinator_acceptance_path is state-relative and does not carry a reverse hash,
self-acceptance or current geometry approval.

XML locators use **zero-based ALL-child ordinals**, matching the original element
order, not the index within findall(tag). For example Choice[1] may be the first
choice when child0 is a contest-level VoteType. Unique metadata tags may omit
the ordinal. `validate_legacy.py` resolves every raw node/cell/contract locator
against the exact original member and checks tag, all attributes and text.
JSON pointers are zero-based actual JSON array positions. TXT locators use
zero-based original line/column fields. No locator convention is a native legal
ID. The full all-native original order and minimum80 proof are retained for
each required contest independently of the database key order.

VHM geographic meaning remains narrower than a physical precinct claim: the
request supplies a county context while returned row county is null. Sparse
labels resembling other counties (including Greenville's Barksdale-Narnie,
Keowee and Monarch Box1) remain unaltered. The available primary explanation
does not resolve election-day physical membership versus later voter-history
or address context. They are source-returned history labels, with no results,
physical or cross-year join. REG/VOT/county/native summary observations overlap.

Peer comparison maps explicitly different derived key/level/scope labels while
comparing every shared raw count, party/candidate/method identity, source field,
flag and original pointer unchanged. It compares all46 county vectors,9823
history hierarchy nodes,7500 VHM rows,516586 history cells,9635 original combined
native rows,260898 original native method cells, and all county/native orders.
Actual peer ID2a77ed30-c478-46c3-8980-817b50d4e679; peer outputs are read-only.

Original2022 election registration also disagrees at the state/county level:
state parent3379089 versus sum of all46 county attributes3379129, a40-registration
difference. Ballots sum exactly1718626. The explicit ledger
`legacy-state-election-reconciliation.json` retains both scopes with no allocation
or inferred cause;2024/2020 state registration parent/child sums are exact.

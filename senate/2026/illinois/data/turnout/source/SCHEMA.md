# Illinois original-source and calculation schema

The primary dispatch scope is **2024 native printed-known votes**, not all legal
write-ins or ballots. `priority-set.json` contains the full 10,062-key order,
ordered 5,540 priority keys, remainder, 108 authorities, parent maps, and every
available native constituent. County named totals and generic marks have
separate orders and denominators. Coordinator acceptance remains false.

`JurisdictionID` is the original election-authority ID. County IDs1–102 and
city IDs104,105,106,107,108,110 are not FIPS. The six city source containers
link respectively to64,16,92,88,48,101. County web totals include their city
commissions; native authority rows are the disjoint arithmetic leaves. County
and city numbers are never added to a combined county total. County FIPS are
independently joined to the original Census2024 counties file by unique
literal-name normalization (case/punctuation/`County` suffix only). A city’s
county FIPS is a parent locator, not a city ID or approved boundary join.

`extract/original-native-records.jsonl.gz` preserves every original12-field CSV
record, in original order within year, including all candidate/category IDs,
names, parties, contest, label, registration and count literals. Positions are
logical CSV records excluding the header, starting1. A peer position including
the header equals this position+1. No record is deduplicated. `EISCandidateID=0`
is reused across noncandidate names; a candidate-ID-only key is invalid.

`extract/source-contexts-YEAR.jsonl.gz` preserves the complete authority,
container, jurisdiction-name and literal precinct presentation key and ordered
source positions. `native-units-YEAR.jsonl.gz` is an explicitly defined
authority+literal-precinct observation projection. It retains every full
context/position and literal category aggregate, not proof of physical units.
Raw row objects are recovered by year/record position from the original-record
artifact. All raw sources themselves remain available by hash.

In2024,59,623rawrecords yield108authorities,114authority presentations,
11,535full source contexts and10,062authority/literal-label projections.
Harris and Trump appear once in10,058projections, Kennedy in10,043.
Fifteen absent Kennedy cells remain null. Lawrence51, Marshall59, Menard65 and
Galesburg108 each have a blank-label administrative-only group: no printed
candidate observations. Their `printed_observed_sum` is null and rank null;
`printed_known_recorded_sum=0` is explicitly the empty recorded aggregate,
not an observed candidate zero. They follow observed numeric zeros in the
primary order and remain in coverage/remainder with no named allocation.

`printed_candidate_votes` values are integer observations or null. Literal
generic variants (`WRITE-IN`, `Write-In`, `Write-in`, `write-in`) remain in
`literal_categories`; `generic_writein_marks` is null without a source row.
Authority generic observations also remain null when no row exists; a separate generic_writein_recorded_sum explicitly preserves an empty aggregate0 and source-present flag. County native_generic_writein_marks is the recorded aggregate (empty sum0); native_generic_writein_observed and its presence flag distinguish source absence. Under/over/blank absence likewise stays absent/null. Summing recorded generic
marks is an alternate source scope, not a valid named-candidate universe.
No16,469residual allocation or legal-native priority robustness is inferred.

`Registration` repeats across candidate/category rows. Each observation group
has one consistent literal in these exports, retained once for a source-field
diagnostic. That diagnostic does not equal the separate102-county turnout
table’s `Total Voters`. Zero registration literals are not interpreted as zero
eligible registered people. Source method fields do not exist: method remains
null, including labels containing `STYLE`, `FED ONLY`, `CENTRAL` or other words.
Split styles, federal-only rows, central/early-looking labels, physical
precincts, polling sites and vote centers are not silently merged.

`county-candidate-source-rows.csv` retains all1462target-contest candidate rows
from306combined county tables, exact table IDs, zero-based table row positions,
raw names/parties/vote/percentage literals and actual detail hrefs. Statewide
source rows preserve all40candidate entries (27/5/8 in2024/2022/2020), including
apparently related names separately. Historical detail metadata is not a
current candidate roster or proof of legal filing date. Contradictory minor
percentages remain literal and are unused in calculations.

`county-turnout.csv` is the compatibility filename for **108 actual authority
rows** ranked by recorded printed+generic marks. Named and ballot fields are
null for the unresolved split authorities, rather than copying combined county
values into every child. Full102-county named/ballot/Total-Voters sensitivities
are separate CSVs. All historical/current identity and geometry remains
unverified. `registration_2026_A/I` preserves the current CSV’s literal headers;
the inspected source does not expand those letters. Source page says unofficial,
daily fluctuations; clock10/19/2026 10:18AM, timezone unspecified.

Ranks use integer values descending, ties by literal authority/county source ID
as a string then literal precinct label. Unavailable observations follow
numeric observations. Fractions retain exact integer numerators/denominators;
`5*cumulative >= 4*N` determines80%, with preceding cumulative strictly below.
Candidate votes are not ballots. Native categories do not exhaust the separate
ballot controls; the2024 difference2,470 remains unallocated.

Acquisition uses actual official parent links and observed option values and
browser-UA selector events. Default Python user-agent omits postback behavior;
normal browser-UA yields the observed onchange. Unchanged-default Adams POST
returns no grids; populated initial GET supplies Adams, while the empty POST
is retained. All18historical city selector pages return no-information bodies;
they are unavailable, not0. Actual turnout Download List postback bodies and
earlier literal-javascript request failures remain evidence, not extra data.

Every successful source body is stored as lossless gzip of the complete
HTTP-client decoded entity; wire Content-Encoding/Content-Length remains in
headers. Gzip reconstruction is exact: `gzip.decompress(stored_bytes)` equals
the raw SHA256/byte length in the receipt. Stored originals are not truncated
or simplified. No artifact is40,000,000bytes or larger. Shared originals are
read-only exact-hash references; `shared-originals.json` freezes selected
original receipts so a mutable newsroom ledger is not a numeric build input.
`external-originals.json` freezes additional official PDF reference metadata.
Original county HTML includes every unrelated office unchanged. Extraction of
unrelated demographic tables is deliberately outside this question’s scope.

`peer-captures/` contains immutable SHA256-named reciprocal snapshots taken
after independent original extraction. The only native-order semantic adapter
moves the four unavailable named pools after observed zeros; both raw orders
are preserved and no counts change. Peer arithmetic agreement never approves
legal geography, current geometry, a valid write-in allocation or live feeds.

Offline sequence: run `build_turnout.py`, `enrich_evidence.py`,
`compare_peer.py`, `write_report.py`, then `validate_turnout.py --seal`.
Python3 needs beautifulsoup4; PDF extraction uses Poppler. Acquisition additionally
needs requests. No dependency/cache directories are retained in this package.
`acquire.py --replay-receipts` reuses successful stored bodies; refresh in a
separate copy if needed, preserving earlier receipts/versions. Failed request
attempts have explicit status/error and retained bodies where returned. Early
sandbox DNS and urllib403 diagnostic probes were not numeric source inputs;
their response bodies were unavailable, and successful recorded requests
supersede access diagnostics without implying universal access.

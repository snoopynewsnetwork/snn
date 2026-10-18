# Florida turnout source contract

This package ranks **67 disjoint county supervisor jurisdictions**, using the
2024 Class I Senate official county table's six named candidates, including the
valid Howard Knepper write-in. The target remains the **2026 Class III special**.
County FIPS are five-character strings, checked against the EAC's county FIPSCode
with its five trailing jurisdiction digits preserved in the original. DOS's
three-letter county codes are a separate identifier system. `Desoto`/`DeSoto`
case and spacing join to the same FIPS; original strings are retained.

## Acquisition and original evidence

`acquire.py ID URL [PARENT_URL]` saves the complete entity body in deterministic
gzip, and a receipt with requested/final URL, parent, UTC retrieval, response
status, all response headers (including duplicates), redirect hops, decoded
entity SHA-256/bytes, stored SHA-256/bytes and exact reconstruction instructions.
HTTP Date/Last-Modified are transport metadata, not an election certification
date or proof of a known update cadence. Failed/404 attempts remain evidence.
Dates and parent links can be inspected in the bodies without network access.

The original 2024/2022/2020 precinct ZIPs are **reused read-only** from `data/news`.
`shared-source-references.json` pins specific entities and their original receipt
records, independent of later coordinator manifest changes. Paths in that file
are relative to this `source` directory. Direct DOS 2024 and 2022 requests later
returned 200 and the exact original entity hashes matched the retained storage
originals. Their receipts reference shared bytes rather than duplicating ZIPs.
`gzip.decompress` restores the whole ZIP byte for byte; its normal ZIP directory
then restores every member, including unrelated offices and recount files.
`original-member-inventory.json` records each member's CRC, SHA-256, bytes and
source row count. **No source body is truncated or simplified.** Every stored
asset must be strictly below 40,000,000 bytes. No dependency/cache directory is
part of the deliverable.

DOS parent → linked original ZIP → member → one-based physical row/byte offset →
raw 19 cells is the native-data chain. The parent explicitly describes the
compiled files as county submissions. Current DOS county table → TR/TD position
→ all named candidates → county/state totals is the certified-result chain.
The 2024 president archived original is independently parsed and matches the
newly recovered current original. NARA's signed certificate is an independent
statewide presidential control, not a county/native allocation.

## Exact 19-field native data

The DOS June 24, 2025 schema defines these **one-based** columns. Their raw string
values, including blanks, whitespace, leading zeros and party codes, are retained.

| Position | Meaning |
| ---: | --- |
| 1–7 | County code; county name; election number; date; name; precinct ID; polling location |
| 8–11 | Total registered; registered Republican; Democratic; all other parties |
| 12–14 | Contest name; district; six-digit contest code |
| 15–18 | Candidate/category label; party; FVRS ID; DOE candidate/category ID |
| 19 | Integer vote total |

DOE 900 is generic write-in marks, 901 overvotes, 902 undervotes. These are not
named valid candidates. IDs are strings; party blank is not a candidate party.
Candidate identity is **all four original fields 15–18**, never just the name.
2024/2020 president uses contest `100000`; Senate uses `120000`. No Florida
Senate contest occurred in 2020. Recount members overlap the base files and are
retained separately; none contains any selected required contest here.

`native-source-rows-{year}.jsonl.gz` retains each selected source row, exact
`fields[0..18]`, member, one-based row, byte offset, line bytes/SHA, encoding,
context and recount flag. Complete original ZIPs retain all other fields and
offices; these are intentionally not re-extracted into extra derivatives.
`native-units.jsonl.gz` groups each exact context/county/election/precinct/polling
label identity, with unchanged registration observations, candidate/category
rows and original row positions. Repeated registration is not added for each
candidate. Compiled registrations have unverified stock/date/status and cannot
replace the separately sourced bookclosing totals.

The native key is a slash-separated context, DOS county, election number,
URL-encoded original precinct ID, URL-encoded original polling label. It is a
**historical source identity**, not a physical polling site, geometry ID, VTD,
ballot style or approved November 2026 precinct. Different contests/years are
disjoint contexts and never summed together or crosswalked on names/counts.
Nine Washington 2022 precinct IDs are blank; three others repeat `1`. Polling
labels plus original member/row distinguish them; missing IDs are not repaired.
Leon `9000` carries an EV label; Osceola president `999` is an explicitly zero
source unit absent from the Senate universe. All are retained.

There is **no method column**. Method hints in labels are kept as hints only:
even all 286 Pinellas 2024 units have the label `Mail Ballot` while their named
votes sum to the whole county contest. No precinct-level candidate method
allocation is made. Unknown administrative/central/split/polygon classifications
are explicit, including noncandidate categories and missing valid-write-in
native allocations.

## County controls, participation and registration

`primary-county-tables.json` preserves complete candidate headers, all 67 vectors,
statewide controls, and table positions for four contexts. The companion long
CSV has source TR/TD positions. `native-primary-candidate-controls.csv` keeps
compiled named counts and generic/under/over universes separate. Exact county
differences appear in `source-discrepancies.json`; no rescaling or residual
allocation is permitted.

`eavs-controls.jsonl.gz` retains 67 Florida county rows in each of EAVS 2024
version 2.0 (released 2026-02-12) and 2022 version 1.1 (released 2023-12-18),
original member/CSV row, F1 participation/methods, F2 derivation flags, A1 stock
counts/comments, E1 provisional dispositions, and C1/C8/B18 mail controls.
Sentinels and blanks remain raw strings: **-88 means does not apply, -99 means
data not available**; these never become zero. Exact field definitions are in
the original codebooks/instrument. F1a is counted participation as reported by
each county; F2 reveals heterogeneous pollbook/ballot-count/vote-history/votes
sources. It is not a uniform tabulator-ballot series. F1b physical Election Day,
F1c UOCAVA, F1d mail, F1e provisional, F1f early, F1g all-mail-jurisdiction,
F1h other are **not automatically disjoint**. County comments disclose overlap
and unresolved discrepancies. No statewide complete method sum is manufactured.

`bookclosing-controls.jsonl.gz` independently retains active registration by
county/party, original worksheet/cell addresses, county totals and precinct
counts. The 2024 bookclosing date is October 7 (generated October 17); 2022 is
October 11 (generated October 20 at 9 PM, timezone unspecified). The stock dates
and definitions differ from election-time EAVS A1a total/A1b active/A1c inactive/
A1d other. Source registration arithmetic exceptions remain visible.

`county-turnout.csv` has one row per FIPS, primary candidate-vote volumes and
valid named write-ins for four contexts, compiled ballot-candidate counts,
generic marks/under/over, historical native counts, separate F1a participation
and registration stocks, descending rank/cumulative fractions/top15/minimum80.
Blank-ballot counts unavailable in these native controls remain empty, not zero.
Votes, ballots/participation and registration are different denominators.

## Priority and review

`priority-set.json` gives the complete 67-county order, exact top15/80% integer
proof and remainder, ordered priority keys, and all available source-native
constituents for every historical context, with method/admin/unavailable cases
and primary/native/participation/registration source objects. The only path to
external acceptance is `data/coordinator-priority-acceptance.json`; worker
`coordinator_accepted` stays false. No acceptance hash is embedded in priority.
After `priority-freeze.json` pins the measured file SHA/bytes, `build_turnout.py`
must reproduce identical priority bytes or refuse to overwrite it.

`compare_peer.py` reads the actual peer's independent original-source outputs;
none is an input to this worker's build. It compares every raw selected field,
primary county candidate, native identity/category/registration/source position,
method absence, full descending order and exact integer crossing. Peer hashes
are pinned in `peer-agreement.json`. `validate_turnout.py` independently checks
all owned assets and source hashes, native rows against original bytes, statewide
controls, complete order/weights/denominators/thresholds, coverage and links.
`asset-manifest.json` includes all owned files, including validation, except the
manifest itself to avoid a self hash. That exclusion is explicit in the validator.
`verify_federal.py` independently parses the original House Clerk PDFs retained
read-only by the actual peer. `federal-original-references.json` pins their exact
raw hashes/bytes and acquisition receipts; no peer-extracted candidate values are
used. The explicit printed-name/party mapping remains in the federal reconciliation.

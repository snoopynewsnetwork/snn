# Arkansas turnout source and calculation schema

The original-first research package is limited to `arkansas/turnout.md`,
`arkansas/data/county-turnout.csv`, and `arkansas/data/turnout/**`. No peer,
coordinator numerical preflight, newsroom aggregate, map layer or other state
derivative is a numerical build input. The bounded reciprocal reads only the
separately captured final peer bodies for verification, never for vote adoption.
Python standard library and the system `pdftotext`
are sufficient. Run with `PYTHONDONTWRITEBYTECODE=1` to avoid cache artifacts.

## Authority and exact original bytes

The Secretary of State's
[historical index](https://sos.arkansas.gov/elections/research/election-results)
links the 2024 precinct XLSX, official PDF and historical Tally elections
1846 (2024 general), 1844 (2022 general), 1841 (2020 general).
The pinned shell's linked public JS client constructs `appConfig.json`,
`Client/GetClientConfig`, `Election/GetElectionInfo`,
`Contest/GetContestSearchList`, `Contest/GetContestResults`,
`Turnout/GetTurnout` and the public `FullDataFile.json` URL. The original
client is retained in full, including the code constructing the optional
`locationId` parameter. No credential, private API, guessed election/contest,
private cell or county ID enumeration is used. County request keys come from
the returned `response.locations` dictionary; selected contest IDs come from
literal target titles in returned metadata. The public client/config is
route-discovery evidence; electoral authority comes from the SOS link chain
and actual returned election/candidate/status records.

`original-pins.json` contains immutable individual source receipts copied from
the read-only preparation manifest before extraction. Each pins exact bytes
of an individual original, not the mutable aggregate or numerical preflight.
`shared_original_path` is relative to the repository root. Original SHA-256,
stored SHA-256, raw byte size, stored size, requested/final URL, UTC retrieval,
status and original headers are retained. The shared originals stay in their
original read-only paths. They must hash-match before every read. They include
all unrelated offices and source metadata; no truncation is authorized.

`acquired/<id>.receipt.json` records each original public acquisition. Fields:

- `url`: exact requested URL; `parent`: observed authority/config route.
- `retrieved_at_utc`/`finished_at_utc`: request clocks, independent of publisher clocks.
- `curl_returncode`, `curl_stderr`, and `http`: curl's complete JSON response
  metadata, including status, effective URL, redirect count, timing and sizes.
- `headers_raw`: ordered response-header blocks, including redirects where returned.
- `raw_sha256`, `raw_bytes`: whole reconstructed original response bytes.
- `asset`, `stored_sha256`, `stored_bytes`: gzip body metadata. When an original
  exactly matches a shared pin, `asset=null`, with `shared_original_path` and
  `original_receipt` instead; this prevents duplicating large originals.

One gzip decompression reconstructs each exact original body; no ordered split
is needed. Every retained object is strictly below 40,000,000 stored bytes.
The failed four 2020 turnout acquisitions remain in `history/acquisition-timeout/`
with their original status-zero receipts, empty compressed bodies, scripts and
failing extraction output. Successful retries replace no original evidence.
There is no election-value substitution for failed responses.

The House Clerk PDFs are separate federal candidate controls. The 2024 SOS
PDF says Official Results. Tally responses say `isOfficial=true`; that does
not independently identify a signed certification instrument or establish a
revision chronology. API `lastUpdated`, FullData HTTP `Last-Modified`, election
date, retrieval UTC and certification/legal status are separate fields.

## Extraction and source positions

`build.py` reads complete original OOXML ZIP members, JSON and PDFs directly.
`2024-xlsx-president-raw-rows.json.gz` preserves literal ten-column headers,
all 19,887 relevant rows, OOXML row numbers, original cell references, `t`
attributes, raw `v` values and resolved strings. The workbook has 69,355 data
rows across 669 literal contest titles; the original workbook preserves the
other offices. No unrelated demographic derivative is required.

Each `<year>-api-original-relevant-records.json.gz` preserves full selected
state, county and native contest objects, raw choice IDs/party IDs, both
write-in key spellings, nulls and returned raw geography descriptors. JSON
pointers identify exact raw source positions. Metadata contains candidate
names, order, party, isWriteIn and the original party dictionary. No source
candidate key is dropped or deduplicated. Uniqueness assertions fail rather
than silently merging ambiguous identities. The whole original JSON includes
unrelated offices, so extraction need not duplicate them.

Each `<year>-full-original-relevant-records.json.gz` preserves the full selected
contest, state candidates, original county wrappers/precincts, wrapper/precinct
array positions, election and turnout objects. The repeated county wrappers
are not disjoint county footers. Only their native leaf votes are used once
in that lane; no county/state/leaf overlap is added. There are no duplicate
literal county/native name pairs in the selected FullData contest arrays.
FullData contains no native IDs. Counts disagree with API and remain separate.

`<year>-turnout-original-records.json.gz` retains exact parsed state/all75 county
responses. Native `locations={}` and `hasLocationTurnout=true` both survive.
The raw original bodies independently retain whitespace, key order and bytes.
`2024-pdf-controls.json` stores all 75 county rows and the statewide row, candidate
header identities/order and extracted line positions. Each of the 525 cells
is checked. `clerk-controls.json` matches each 2020/2022 candidate by a literal
name token, and each 2024 presidential ticket by the independently supplied
ballot-party identity. It retains matched source lines, not merely a sorted
bag of candidate totals.

## Geographic keys, hierarchy and empty fields

The state key is AR / 05. Returned five-character county identifiers are kept
as strings, with leading zeros, and associated with their literal returned
county names. Source/year-scoped keys are constructed as:

`AR:<year>-xlsx:<county FIPS>:<percent-encoded literal precinct>`

`AR:<year>-api:<county FIPS>:<returned native ID>`

`AR:<year>-full:<county FIPS>:<wrapper index>/<precinct index>`

These constructed keys are not official precinct IDs. A primary XLSX row's
`native_id=null` is intentional. `matched_api_native_id` is separate, populated
only for a unique exact same-year county/name and candidate-vector match. Five
XLSX units remain unmatched; source names are never silently normalized. The
two API numerical combinations are evidence, not an approved legal crosswalk.
All source-native IDs, positions and literal names survive even when unmatched.
API and FullData publication vintages have distinct keys and orders.

The primary disjoint arithmetic is one literal XLSX county/precinct leaf with
seven reported candidate rows. County/state summaries are controls. Four method
columns partition candidate votes on each row; methods are not extra geographic
leaves. Unit type, municipal/ward/polling-site/vote-center/central status and
polygon eligibility remain unknown unless explicitly supplied. Central names
are not automatically central counting groups. No 2020/2022/2024/2026 boundary
or native-ID equivalence is inferred from matching names/counts.

Missing ballot, registration, blank, under/over and eligible-write-in fields
are JSON null / empty CSV cells, never inferred zero. Published zero candidate
votes remain zero. API `voteTypeID=1` is literally `All`. PartyID1 or a blank
party name remains source-unknown; the raw Nevada party literals are preserved.
The Clerk's Libertarian identity for Harrington/Cates is a separate ballot
identity, not an edit to raw metadata. A Democratic 2020 Senate scenario is
unavailable: Harrington is the named Libertarian opponent.

## Orders, denominators and dispatch

`county-turnout.csv` is a compatibility filename containing **2,841 native
primary rows**. It is identical to `orders/2024-xlsx.csv`. Each row retains
county/native names, explicit source key, candidate vector, literal ballot
party labels, four method totals, source row positions, nullable optional
controls, rank, integer denominator and cumulative votes. CSV JSON cells encode
structured fields losslessly; consumers must parse them rather than split on
commas. Weights are exact numerator/denominator pairs; decimal percentages are
display-only. There is no rescaling or allocation of an unexplained residual.

All orders use descending integer volume then exact source key ascending.
Minimum crossing is the first rank satisfying `5*cumulative >= 4*denominator`;
the preceding rank must fail. `ceil(4*denominator/5)` is the integer threshold.
The complete remainder stays in the denominator. `orders/statistics.json`
retains exact preceding/crossing/full/remainder counts and votes for every
source-scoped native, county ballot/registration/contest, and available method
sensitivity. Native ballot and registration rankings are unavailable, not
replaced by county rankings. FullData disagreements are not combined into the
chosen primary denominator.

`priority-set.json` contains the full primary order, top15 and ordered minimum80
keys, full remainder, 75 parents with every available source-native constituent
array (all three API and FullData years plus 2024 XLSX), exact native source
positions/IDs, source-scoped county controls and explicit unavailable/current/
administrative cases. Counts/keys refer to the historical reported-candidate
source universe. Eligible-write-in-complete, November2026 and legal geometry
contracts remain null/empty. The bounded captured-final source/field/order peer
comparison passes; coordinator acceptance remains pending.

## Reproduction, validation and sealing

Run `acquire.py` only for public acquisition; successful exact receipts replay
without network replacement. `build.py` and `report.py` rebuild owned outputs
offline. `validate.py --write` records meaningful independent calculations in
`validation.json`; without `--write` it is read-only. The checker independently
parses original OOXML and JSON, checks source/native/candidate/method/turnout
controls, all rankings and crossing proofs, source/pinned hashes, links and bounds.
History retains the original failed native-match assertion/fixture and error
before the narrow change to record source disagreements instead of assuming
identity. That is a checker/model assumption correction, not a source repair.

`seal.py` writes final-seal.json and **then asset-manifest.json last**, including
every owned artifact except the manifest itself. Neither seal nor validation
contains a manifest digest or self-hash cycle. `validate.py --sealed` performs a
read-only exact-membership/hash/source/link/bounds/no-cache audit; it must not
write after the manifest. Immutable core/final snapshot member hashes allow
later same-ID independent peer review without rewriting the frozen evidence.
The original no-peer phase remains reconstructable in the whole-body capture.
The bounded captured-final reciprocal below establishes only its explicit
source/field/order scope; it is not coordinator acceptance.

## Same-ID captured-final reciprocal

The same actual worker 43866295-c1c8-4f15-8933-67a99b3454c0 resumed under the
fresh Verification/medium profile. Before edits/comparison it verified every
old 1,027 manifest target plus manifest, complete 1,028-file membership and
all 19 individually pinned shared originals. `history/captured-final-reciprocal/`
then froze every old whole body or individually pinned immutable original/archive
reference, followed by all 314 final baseline bodies from finished peer
302e0938-9d85-4b49-99c1-87bbb564364d. The old MF/report/scripts/raw/control/null/
admin/hierarchy/order/validation/seal/history are reconstructable by original
path and SHA from those captures. Old MF pins are never compared to rewritten
current bodies. Capture whole-body preservation does not itself imply equality.

`reciprocal.py` reads only these captures and the fixed original bytes. It
independently derives an explicit typed witness schema from original OOXML and
JSON and compares each complete peer row/object, including keys/types/nulls,
raw-v/shared-string/cell/header/method/candidate/party fields, full receipts and
their whole-byte hashes, original pointers, metadata and native descriptors.
Candidate/cell addresses are expanded explicitly from contest-node/worksheet
companions. For a raw node witness only source child `locations`, `Counties`
or `Precincts` subtrees are omitted, with exact child pointer/set/order coverage
checked separately; complete original bytes preserve the whole source. There
is no silent object projection, source normalization, deduplication or zero fill.

The comparison covers all 490 shared originals/receipts, 19,887 workbook rows,
198,870 cells, 198,525 required candidate/method/party positional CSV records,
24,096 complete required raw contest control nodes, 10,454 descriptor records
with explicit contest context, four whole metadata witnesses, 225 complete
county turnout envelopes, all 20 full rankings/integer crossings/denominators,
and all 75 parent/full2841/1056 priority/1785 remainder arrays. Explicit five
match gaps, 2,836 exact matches and all 19 required county/candidate source
differences remain. Complete contextual 2020 identity metadata/shared raw source
bytes are checked; its extra presidential numerical derivatives/scenarios and
all baseline calculator/target/outcome/pool/future/current equality are excluded.

`reciprocal.json` qualifies the captured final reverse proof of 162,714 checks,
zero errors. The complete peer capture retains the earlier 120,916 proof and
old checker/report/schema/actual failing expanded-header adapter history. Only
the actual final captured source/native/field/order/array proof is cited; no
later/future peer or scenario/calculator equality is asserted. One independent
checker state-document cache lookup failed locally; its whole script, actual
error and complete first-parent input with raw receipt/whole-contract pins were
saved under `history/reciprocal-state-document-adapter/` before the narrow cache
lookup fix. No source or calculator count was altered.

`replay_original_scopes.py --check` executes the **captured original builder** in
a temporary tree, with individual immutable original-body symlinks/receipts and
no derived input. Audit hooks deny network, non-pdftotext subprocesses, mutable
helper/discovery reads and writes outside that isolated tree. All 49 generated
bodies match their old whole captured bodies by bytes/path/SHA. The saved
`isolated-replay.json` records exact inputs, output hashes, guard and commands;
`--check` is read-only on owned files. `test_reciprocal.py` reconstructs actual
source-derived complete packets and verifies 24 whole saved negative gzip inputs
reject missing native/candidate/method/null/admin/header/source/companion/control/
metadata, wrong IDs/order/80%, duplicate keys, county substitution, residual
allocation, party/All normalization and current/geography/feed admission.

Only `acceptance_status` changes in the canonical contract. `reciprocal_status.py`
compares every other whole field/object/null/admin/key/source/order to the frozen
old contract and the native CSV to its old whole bytes. Other canonical source,
count, order and original-only acquisition/build/extraction script bodies remain
exact. Report/SCHEMA, explicit
bounded peer status, necessary verification scripts, capture metadata, validation,
seal and manifest are the authorized changes/additions. Coordinator, geographic/
legal/current/November feed/collector/forecast/probability approvals remain false
or unknown. No peer/source writer or mutable peer dependency is introduced.

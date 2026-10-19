# Retained source and investigation schema

All paths in JSON pins are relative to `senate/2026/mississippi/`, unless expressly
marked otherwise. JSON pointers are RFC6901-style paths into the complete decoded
JSON body. A gzip path points to the gzip's exact stored bytes; decompress before
resolving its pointer. Hashes always say whether they cover stored, wire entity,
or content-decoded bytes. No entity is truncated; every stored file is strictly
less than 40,000,000 bytes.

## Complete historical objects

`scope-reference.json` is a reference to entire bodies, not a reduced replacement
contract. The final 13,065,430-byte contract and immutable v2/17-body/historical
components stay read-only at their original paths. External acceptance is path
only. `frozen_scope.py` verifies acceptance-listed final pins, all canonical
104/164 component bytes, complete source objects and ordered source partitions,
all 352 original publication hashes, preferred24,926 candidate/null positions,
physical columns/pages/roles and independent native sorting/prefix arithmetic.
It imports no producer calculator/validator. Canonical source-object digests do
not replace loading the complete source objects. Stored hashes preserve lexical
bytes; recursive ordered comparisons preserve types, object fields and arrays.

All complete source objects remain available, including source/page/physical
column, literal headers, printed codes, bounds/render/original hashes, candidates,
party literal, votes, source marks, administrative/unused/TOTAL roles, alternatives,
registration, ballots, generic marks and explicit unknowns. Sources differ in
what they print; an absent field, explicit null, literal blank, printed zero and
protected/masked value are distinct states. Six 2018 literal X marks remain
numeric nulls. No mask or missing table becomes zero. The complete original
PDFs retain even fields not extracted in a bounded transcript.

`frozen-scope-validation.json` compares v2 and turnout all-eleven candidate
positions with exact source hash/page/physical-column/role controls. It retains
both literal strings for165 representation differences; it does not normalize
them into aliases. Unknown Union style candidate weights/pools, incompatible
Montgomery885ballots and corrected Lincoln15898 remain in their original bodies.
The17-body companion's complete contents, all104/164historical bodies and their
original sources stay dependencies, not independent rediscoveries.

## Parent and child records

`parent-investigations.json` has82 records in frozen v2 parent order. Each stores:

| Field group | Meaning |
| --- | --- |
| `county_fips`, historical counts/arrays | Frozen administrative parent and exact original array references. Neither FIPS nor directory ordinal approves a native join. |
| `state_directory_pointer` | Pointer into the82-record original-derived county authority payload. Original directory names, addresses, clerks, commissioner arrays and empty cells are retained. |
| `preferred_historical_publication` | Actual fresh SOS parent/iframe/index/href chain plus original stored/raw hash. Older alternatives remain in the complete frozen contract. |
| full preferred/historical references | Entire all11/historical bodies remain reachable, not just selected columns. |
| current observations / note / depth | Source-specific actual requests, retained HTTP outcomes, primary/secondary discovery limits and honest current scope. A successful website is not necessarily a successful election source. |
| current IDs/method/remainder/cadence | Null until proved; no current admission in this package. |

`priority-investigations.json` has exactly887 records in accepted rank order.
`remainder-inventory.json` has exactly849 in the original suffix order. Each
record points to its **complete** ranked object, complete constituent object,
complete all11 source column and shared parent inspection. No new copy of the
frozen object is substituted, and no887 independent-feed claim follows.

`official-results-sources.csv` is the83-row state+82county administrative inventory.
Blank current-ID/outstanding fields mean unverified/unavailable, not zero. The
five nonpriority county parents remain present. Native counts are historical
source-native constituents, not current approved physical precincts.

## HTTP evidence and replay

`receipts/*.json` is the complete request record for each actual observation.
It retains requested and encoded request URLs, method, exact source relation,
request headers, POST JSON where used, start/end UTC, status, final URL, ordered
response headers, redirects, content encoding, complete wire entity hash/bytes,
decoded raw hash/bytes where decoded, stored path/hash/bytes or ordered parts,
and transport/error outcomes. HTTP errors retain their complete bodies; DNS/TLS/
timeout failures have no invented HTTP entity/status. The one read-only POST is
the public SOS administrative-rule constructor recovered from actual JS; its
agency54 selection comes from the retained page, not a guessed private endpoint.

Storage is deterministic lossless gzip or an exact shared original reference.
If a compressed entity ever exceeds the limit, ordered32,000,000-byte parts plus
full original/stored hashes and reconstruction instructions are required.
`Accept-Encoding: identity` is requested; servers may still return gzip/Brotli.
Node's built-in Brotli decoder reads retained wire bytes where needed. Chunked
HTTP framing is not a content encoding; the complete dechunked entity is saved.
Transport traces do not pretend to preserve TLS packets or chunk framing.

`source-ledger.json`/`.csv` index all receipts, including setup/error/incidental
captures. `navigation-index.json` and `*.links.json` preserve parsed literal
href/src/form values, attributes, link text, BASE-aware resolved URLs and parent
relations. Page/script existence is not a deployed result API. Current county
parent sources with HTTP200 can still be shell/placeholder/old/vague scope.
`decoding-controls.json` independently verifies every stored entity and decoded
hash; it also records unsupported/absent rather than inventing decoded content.

The acquisition job files are replay descriptions. `acquisition-replay.json`
pins all28 job files, their complete ordered IDs and observed stage order; all487
jobs match exactly one retained outcome. Existing IDs are immutable;
new observations require new IDs and retained old receipts. Replay of a dynamic
URL can produce different bytes. `consolidate_storage.py` can replace duplicate
owned storage only after exact entity equality with a shared read-only original,
and records storage-only changes; it never edits a shared source. No running
collector, cadence promise, authentication, paid docket access or voter lookup.

## Original sample positions and controls

`sample-controls.json` contains original-based independent Pike25-precinct and
DW summary Senate controls, Rankin ordered methods/rows and their full raw lines.
Duplicate Write-ins rows retain ordinal positions, and blank party cells remain
blank. Numeric calculations are integers; current unknowns stay null. Pike and
Rankin named county sums are compared to the accepted source-native county sums
without matching native IDs or methods. This is aggregate control agreement.

`pdf-evidence/` holds complete Poppler layout text, lossless complete word/bbox
XML where available, full relevant-page preview images, and explicit failed bbox
stdout/stderr/exit controls. Bbox crashes on Rankin leave coordinates unavailable;
complete original PDFs and layout-text page/line/column order remain authoritative.
`visual-review.json` records only actually viewed full relevant pages. Source,
election date, status, report clocks, HTTP clocks and retrieval UTC remain separate.
Do not infer zeros from empty pdftotext of a scan. The anomalous Republican County
index PDF has a visually read Walthall certificate, not an inferred adjacent-county
assignment. Its original link/label remain exact.

`current-primary-index-inventory.json` retains both complete76-link lists, their
literal labels, unknown label and missing county labels. These are March primary
indexes, not November feeds. `legal-observations.json` separately records current
source instructions, document-label/vintage differences and unresolved legal
coverage. Newsroom setup IDs remain outside official current-ID fields.

## Freeze

`reproduce.py` is offline and read-only by default. It verifies all frozen
dependencies and full objects, raw entities, calculations, exact887/849/82/77
coverage/order/pointers, administrative controls, links, sizes, Python syntax,
absence of caches and exact owned manifest membership. `--write-validation`
writes the validation before the final manifest is sealed. The manifest covers
only `official-results.md`, `data/official-results-sources.csv` and all
`data/results-sources/**`, excluding only `asset-manifest.json` itself.
No cache, dependency tree or other assignment is part of this worker's output.

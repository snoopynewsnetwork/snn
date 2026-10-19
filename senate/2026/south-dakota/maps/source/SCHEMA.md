# South Dakota precinct-map source and reconstruction schema

Snapshot: 2026-10-19 UTC. All paths in JSON pins are relative to the South Dakota
directory. This package owns only `precinct-maps.md` and `maps/**`. No producer,
peer or coordinator file is modified. No election-night collector is implemented.

## Authority and complete frozen objects

External historical dispatch authority is **path only**:
[`../../data/coordinator-priority-acceptance.json`](../../data/coordinator-priority-acceptance.json).
It is not reverse-pinned or self-approved in these assets. Its complete parsed
object drives recursive verification of every nested listed pin and all66 parent
objects. Frozen worker acceptance and certified-robustness flags remain false.

The exact original contract is referenced once by its path, byte length2,955,655
and SHA256`a1c97454c68c1f30bdb6b7755cd826326e7380318eae74b6452465ee23e9c275`.
No huge original is copied here. A `full_frozen_native_object` or
`full_parent_object` reference has:

| Field | Meaning |
| --- | --- |
| `contract` | Exact original `path`, `bytes`, `sha256` triplet |
| `JSON_pointer` | RFC6901 pointer, array order preserved |
| `recursive_semantic_sha256` | SHA256 of the **entire** object, JSON sorted object keys, UTF8, compact separators; arrays retain order, all nulls/strings/numbers/booleans and nested fields participate |

`inventory-691.json` preserves all691 ranks/order; `priority-index-304.json` is
exactly its first304 full entries and `remainder-387.json` exactly its last387.
Each entry resolves its complete original unit and full parent, including every
candidate, original source heading, source-native constituent, method,
unavailable, null and administrative field. Display fields are conveniences,
never replacements for complete objects. No vote-only projection is a contract.

`county-parents.json` preserves all66 full-object references and both complete
ordered child lists. It also retains all original SOS authority row/cell fields
and HTML, including public contact links and literal unprinted/masked fields.
These are retained read-only; no messages were sent. Names/FIPS select the
county-level historical fallback only; they do not join a reporting observation
to a physical precinct or current entity.

`source/full-contract-references.json` resolves the whole contract, all691 units,
all66 parents, all explicit unavailable cases, full687/693 alternative historical
universes, and all679 rows of the separately byte-pinned2022 PDF companion CSV.
The exact companion CSV is preserved by file reference, with its entire schema;
it is not merged into the687-row public-workbook universe. The recursive graph
also includes signed198 county vectors/594 candidate fields, distinct archive
ballot/registration tables, proofs, reviews, receipts, scripts and manifests.
`qa/dependencies.json` records every independently verified pin and complete
recursive semantic hash. Corrected coordinator PDF-family selection is distinct
from the unchanged correct worker locators.

All seven directly accepted CSV files also retain their complete ordered header
schemas and every full-field ordered row semantic hash in that audit. Empty CSV
strings remain literal source values. Signed controls independently recompute
all198 county vectors/594 candidate fields, with election-specific parties.

## Original acquisition envelopes

`source/reused-receipts.json` is a frozen copy of small, complete original
receipt envelopes, pointing read-only to exact original bodies. It does not
depend on a mutable coordinator acquisition aggregate. Preparation originals
are independently decompressed/hashed, including all four native ID pages,
pre/post counts/IDs/metadata, two full mapbooks, errors, directory chain and
Census ZIP. `source/preparation-individual-pins.json` pins only individual
immutable review/discovery companions. `freeze_references.py` is a one-time
initializer and refuses to replace an existing frozen receipt list.

Worker GETs have one `raw/<id>.receipt.json` each. Their full envelopes survive
in `source/source-inventory.json`. Fields include exact requested URL, parent ID,
literal href or actual client expression, anchor, method, requested county,
retrieval/completion UTC, final URL, redirects with complete headers, status,
complete headers, error, raw length/SHA256, representation, ordered stored pins,
and source clock/timezone. Null clocks are unknown, not generated vote clocks.
HTTP Date/Last-Modified, URL upload year and client cache-busting timestamps are
not election-effective or vote-update times. A transport error's original is
the complete exception text; it is never represented as an HTTP response body.

Bodies are complete requests-decoded HTTP entities. Their original content
encoding/length remains in headers. Stored bodies are deterministic lossless
gzip, split into ordered32,000,000-byte pieces when necessary. Every stored
object is strictly below40,000,000 bytes. Error bodies, empty bodies, and wrong
initial routes survive unchanged alongside later successful observations.

`source/link-inventory.json` preserves all literal links from captured HTML
and the narrower map-related selection. Original `<base href>` is honored.
The initial Hutchinson relative-link resolution mistakenly doubled a directory;
those404 attempts are retained, and source-correct base resolution has separate
successful receipts. Primary search discovery leads are explicitly named as
such; actual official-domain originals are separately fetched and retained.
Minnehaha raw403 parent versus web-reader href discovery is likewise separate.

`source/jobs-*.json` are bounded one-time public acquisition inputs. They never
guess numeric app/service IDs. The Beadle client actually names a settings POST
with runtime IP/login/access variables. Its full HTML and two scripts are
retained; no unobserved variable values or API response are invented. No
authenticated settings or precinct layer from that client is claimed.

## Geometry and binary originals

`source/asset-catalog.json` and `manifest.csv` distinguish29 complete county/map
PDF originals, two complete county native snapshots and one whole-state Census
fallback ZIP. District/administrative supplements and failed map requests stay
in the source inventory, not as successful precinct polygons. PDF feature count
and native CRS are null; raster/paper maps do not establish vector precision.
Every county/entry carries acquisition, access, vintage and finer-geometry gaps.

The two actual county app→configuration→webmap→layer chains are independently
replayed. Esri source pages retain every attribute and exact native `rings` or
`curveRings`, XY/CRS/Z/M, including all curve control objects. Queries request
`outFields=*`, native geometry, `returnTrueCurves=true`, Z/M, with≤50 returned
IDs per page. No output CRS, max offset, rounding, geometry precision,
quantization, simplification or repair is requested. Counts, all ID sets, edit
metadata/full metadata match pre/post; errors and transfer-limit flags checked.
Service-side preexisting generalization remains unknown.

Minnehaha's complete custom WKT describes NAD1983 UTM14N **US survey feet**;
no assumed EPSG or display Mercator is substituted. Pennington's103150/6574
native CRS is also US survey feet. The seven curve features remain in originals
and are excluded from **linear-only** previews/topology, explicitly labeled.
No curve is silently replaced by a chord. Source feature IDs are retrieval
identifiers, not accepted historical/current keys.

`qa/Census-binary-geometry.json.gz` independently verifies every ZIP member's
CRC/SHA/size, SHP/SHX offsets/record lengths/types/bboxes/parts, all785 DBF records
and fields, and **all505,985 native XY positions** including repeated positions
and ring closure. Shape5 has no Z/M, recorded unavailable. Complete PRJ and
DBF schema remain. Every coordinate double is compared by binary bytes with
PyShp3.1.6 before an adapter. The installed constructor signature/source is
checked: `Shape(shapeType=..., points=..., parts=...)` preserves positions;
its `lines=` path implicitly closes polygon rings and is deliberately avoided.
Neither orphan holes nor unclosed rings are rewritten. Invalid/empty/null/curve
cases are diagnosed and retained. Polygon adapters are diagnostic derivatives,
never substitute originals.

Native projected overlap areas are square US survey feet; Census angular XY
overlap areas are square degrees and are not land-area estimates. Invalid
linear features/curves are excluded from intersection calculations, with exact
IDs and reasons retained. No legal gap/overlap certification is made without a
same-vintage legal outline. No repair, buffering or vote allocation occurs.

## Offline display and verification

The index is static HTML with exact304 ordering, all387 remainder rows and66
county pages. Every entry links actual acquired assets or the full historical
fallback with finer-entry qualifications. County SVG previews retain all source
linear positions in display transforms (rounded to0.001 display units), separate
from originals. Census county filtering preserves source parts/attributes and
never proposes leaf joins. The atlas is an outline-only display derivative.

Poppler renders all pages of every inventoried PDF into contact sheets, preserves
complete text extractions, and creates selected complete large-page images.
Actual visual-review scope is in `qa/visual-review.json`; it does not assert
that small thumbnails validate fine print. No browser session was used in
this worker's static workflow; HTML/SVG/XML/local-file QA is explicit, with no
claim of browser interaction or visual browser testing. Browser availability was
not independently tested, and no unavailable-browser error is invented.

Offline reproduction from repository root (Python3.11 plus pinned
[`scripts/requirements.txt`](../scripts/requirements.txt), Poppler required):

```sh
python -B senate/2026/south-dakota/maps/scripts/audit_dependencies.py
python -B senate/2026/south-dakota/maps/scripts/geometry.py
python -B senate/2026/south-dakota/maps/scripts/pdf_previews.py
python -B senate/2026/south-dakota/maps/scripts/investigate.py --inventory-only
python -B senate/2026/south-dakota/maps/scripts/build.py
python -B senate/2026/south-dakota/maps/scripts/atlas.py
python -B senate/2026/south-dakota/maps/scripts/replay.py
python -B senate/2026/south-dakota/maps/scripts/validate.py --check
```

Network acquisition is optional and separate: `acquire.py source/jobs-NN.json`
preserves existing receipts and refuses ID/URL collisions. Do not rerun shared
writers or refresh frozen dependencies.

Exact recovery examples from the `maps` directory:

```sh
python -B scripts/reconstruct.py --id minnehaha-county-PDF /private/tmp/sd-map.pdf
python -B scripts/reconstruct.py --pointer /all_units/303 /private/tmp/sd-unit.json
python -B scripts/reconstruct.py --original-2020-county /private/tmp/sd-2020.pdf
```

The149,141,181-byte2020 county PDF is streamed from its four ordered existing
gzip parts (32M/32M/32M/6,882,528 stored bytes); full original SHA256 is checked.
No copy is stored in this package. Reconstruction refuses to overwrite files.

`asset-manifest.json` covers the report and **every** owned file including QA,
scripts, PNGs, CSVs and errors; only its own self-entry is excluded to avoid
circularity. `validate.py --check` reads it without writing. Updating validation
then rebuilding that manifest is an explicit finalization step, not approval
of current geography or a certified priority minimum.

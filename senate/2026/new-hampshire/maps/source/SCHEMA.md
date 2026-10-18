# New Hampshire map evidence schema and reproduction

Snapshot: October 18, 2026. Paths below are relative to `maps/` unless stated otherwise. Only `maps/**` and the state-relative `precinct-maps.md` belong to this assignment.

## Accounting and authority

`inventory.json.units` contains exactly the frozen contract's 320 leaves, in its full descending order. Each `source_unit` is the complete, unchanged contract object, including labels, null numeric reporting IDs, source locators, explicit municipal parents, every candidate/administrative value and original availability qualifications. The outer object adds map references and gap labels; it never grants approval to the percent-encoded historical key. `priority.json` contains exactly the first 143 in accepted order; the other 177 remain in the inventory. Neither ten county controls nor 98 priority municipal parent labels replace these identities. Parent summaries are not added to votes. Berlin remains a single historical city row.

`compatibility/native/*.jsonl.gz` are byte-identical copies of all 23 frozen native rosters, 320 objects each. Every original field, float/integer/string/null, BIFF cell type, PDF line/page, row/sheet and unavailable ID survives. No cross-year join or vote allocation is performed. `compatibility/diagnostics.json` gives independent source-scoped numeric/null subtotals and ten explicit county control subtotals. `compatibility/primary-control-balances.json` contains separately re-read original summary/footer objects and their differences, including known defects; controls add no votes. `audit_native.py` independently opens each original at all 7,360 locators using xlrd, OOXML XML and Poppler, without importing a turnout/baseline parser. It also verifies every retained original control locator, including2,289 summary/footer fields. Numeric subtotals skip unavailable values; they do not impute actual zeros.

`source/shared-originals.json` pins only frozen contracts and finished first-wave artifacts, plus Farmington's immutable original ballot. `source/native-original-references.json` retains each original body's exact stored/decoded hashes, original metadata, requested/final URL, UTC, headers, access status and shared location. These originals are reused read-only. Existing historical metadata may lack redirect-hop headers; that limitation remains in its original record. No mutable official-results report/manifest is pinned. There is no reverse acceptance hash or mutation of the contract.

## Acquisition objects

Each `source/<id>.meta.json` records one actual response: exact `requested_url`, `final_url`, start/completion UTC, request/response headers, all redirect URLs/statuses/headers available to requests, HTTP status, content-decoding policy, full original decoded-entity SHA-256/bytes, parent capture ID, discovery note and ordered `objects`. Each object has path, stored byte size/hash, decoded segment size/hash, encoding and zero-based order. Content-Encoding transport decompression precedes the recorded original entity; wire framing is not represented. Original PDFs/ZIPs stay untouched. Text/JSON is deterministic gzip. Identical stored objects can be shared by multiple capture records, without merging response metadata.

Bodies larger than the limit are partitioned at exact 30,000,000-byte original-stream boundaries, each segment independently gzip-compressed. Concatenate decoded objects in `order`, with no delimiter. No data is truncated. Every stored object, including scripts/derived/index/manifest, must be **strictly less than 40,000,000 bytes**. The Portsmouth 55,167,846-byte PDF is only retained as its two ordered gzip segments; no huge duplicate original is retained. Reconstruct outside this tree:

```sh
python3 senate/2026/new-hampshire/maps/reconstruct.py portsmouth-map --output /tmp/nh-portsmouth-original.pdf
```

The offline [browser helper](../reconstruct.html) accepts the two local parts, decompresses in declared order and checks complete byte count/SHA-256 before offering the original PDF. It makes no upload/network request. Python reconstruction is the portable tested path.

`source/acquisition-plan.json` is the complete exact-request replay recipe, including failed bodies. `acquire.py` is append-only for existing capture IDs. `fetch_plan.py --out /tmp/new-nh-map-capture` replays the actual observed URLs into a separate evidence directory; future network bytes can differ. `fetch_selected.py` records the initial observed source selections; the final acquisition plan is authoritative for the larger request inventory. HTTP200 with a shell/error is never a polygon. Parent capture notes distinguish actual HTML links, observed viewer/webmap/service configuration chains and directly discovered official documents. No guessed endpoint is admitted as successful data.

## Geometry and IDs

The original GRANIT ZIP holds all 16 members, including polygon `pbp` and line `pba` SHP/SHX/DBF/PRJ controls and original metadata. `derived/zip-controls.json` gives every member CRC, size/hash and DBF field definition, deletion flags, SHX offsets/record lengths, original record number, counts, native bounds and CRS. `derived/granit-archive-{pbp,pba}-native.json.gz` preserves every attribute, all original coordinate doubles, parts, bounding boxes, raw record hashes and byte offsets. Z/M are explicitly absent in these source shape types. SHP has no true-curve representation; no unsupplied source geodatabase is claimed.

`derived/*-service-audit.json` records ArcGIS layer native CRS, object-ID field, metadata hasZ/hasM, complete pre/post count and ID sets, bounded batches of at most 100, actual returned IDs, transfer-limit flags and curve presence. Original batches request `outFields=*`, full geometry, Z/M and true curves; omit outSR, rounding, quantization, precision and generalization parameters. All native server fields, IDs, rings and coordinates survive in original JSON. Geometry type and lack of curves/Z/M are observations of the delivered layer, not a promise about unpublished native databases. All seven services (municipal, ward and polling-point layers) are audited. Pre/post ID/count agreement is not a transactional snapshot and cannot by itself exclude an intervening attribute/geometry edit. URLs and IDs are retrieval IDs, not approved election-results IDs.

CRS: GRANIT archive/current service, Merrimack and Hudson polygons use NAD83 New Hampshire State Plane **EPSG:3437**, US survey feet (0.3048006096012192 m); ArcGIS uses native102710/latest3437. Keene polygons use NAD83(2011) New Hampshire State Plane **EPSG:6525**, US survey feet (native103104/latest6525). Point-layer native CRS is recorded independently in its audit. Native area/length attributes are not recomputed or reinterpreted as vote weights. Current service and historic archive are separate snapshots; source dates/catalog edit dates do not imply election approval or a legal correction chronology.

`derived/*-native.geojson.gz` are convenience Polygon/MultiPolygon derivatives explicitly labeled with native CRS. Source JSON/ZIP controls remain authoritative. `derived/municipal/*.geojson` are whole-municipality reference derivatives, one archive and one live-service version for each of 234 explicitly matched incorporated municipal parents. They contain all corresponding vertices and source attributes, transformed without simplification/rounding to longitude/latitude OGC:CRS84 using pyproj. The exact literal parent label and explicit county attribute select a **reference**, never a cross-year electoral crosswalk. The raw source geometry of all259 features remains; 25 administrative/territory identities receive no assigned polygon even when a GRANIT label happens to match. Source-county labels in the accounting inventory remain original controls, not inferred current jurisdiction assignments.

SVGs are native-CRS fitted displays rounded to0.001 viewBox units, even-odd fill, with no basemap or measurement claim. Original native streams have no coordinate rounding. PNGs are actual rasterizations of PDF pages, up to1200px, preserving full uncropped page; original PDFs retain full resolution. None of these previews replaces native geometry/original PDF.

`derived/topology.json` reports GEOS validity, empty geometry, parts/vertices/bounds, positive-area pair overlaps and enclosed union holes in each dataset's native units. No repairs/snapping/buffering take place. Enclosed holes do not establish legal gaps; external-edge/state/municipal-envelope checks and cross-source alignment remain unverified. Multipart boundaries, holes and all records remain intact.

## Scope states and gaps

`actual_ward_reference` means a city primary ward map or linked municipal ward geometry was actually acquired, with its exact vintage qualification. It does not imply current legal/November source-key approval. Historical Claremont2012/Dover2012/Rochester2020 metadata and current-published other city maps are kept distinct. Whole-municipality references never substitute for wards. Remainder wards without ward downloads say `ward_reference_gap_parent_only`.

Derry's four political/voting districts share one linked polling site; Merrimack has two current linked ward polygons/sites and an April14,2026 clerk transition; Hudson has two linked district polygons but a Ward1 location conflict; Berlin has precinct1/3 street ranges and no downloaded finer polygons. These remain supplemental scopes beside whole-town/city historical rows. Polling sites are points, address lists or places, not independent candidate votes. Central groups/method rows and election-specific reporting crosswalks remain unavailable. Generic4073 write-in marks are not a demonstrated named/valid allocation. No source blank, dash or correction asterisk is rewritten.

`current_november_2026_approved=false` and `current_results_source_id=null` are explicit across this package. Manchester's dated ordinance/effective ward descriptions establish the limited ward authority they actually state; they do not approve a synthetic source key. Source 2010 VTD attributes in the clerk-linked Keene layer remain literal and do not grant general approval to Census VTDs. No county or Census geometry is substituted for approved precincts.

## Offline build and validation

Requires Python3, requests (network capture only), pyshp, Shapely, pyproj, PyMuPDF, Pillow, xlrd2.0.2 and Poppler `pdftotext`. Dependencies live outside the repository; no environment/cache trees are retained. The existing external xlrd path is `/tmp/snn-xls-reading-libs`; install xlrd in an external environment or adjust the path when reproducing elsewhere. Runtime versions are in [environment.json](../environment.json).

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-hampshire/maps/build.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-hampshire/maps/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-hampshire/maps/owned_manifest.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-hampshire/maps/validate.py --check-manifest
```

`build.py` is network-free and touches only owned paths. It verifies primary locators, regenerates native geometry diagnostics, actual PDF previews and the self-contained HTML inventory. `derived/visual-review.json` is the human-readable actual-page review keyed to original hashes; do not invent review status for changed PDFs. `validation.json` is deterministic and records meaningful counters/gaps. `asset-manifest.json` lists every owned file plus `precinct-maps.md`, with state-relative paths/bytes/SHA-256, excluding itself to avoid recursive hashing. Freeze order is build→validate→manifest→read-only manifest check; no mutable peer-report pin is needed. Opening `index.html` directly works without a server, external libraries, remote tiles, fonts or fetch calls.

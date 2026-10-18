# Georgia precinct assets: schema and reproduction

Snapshot: 2026-10-18 UTC. The map collection preserves original public HTTP entities and separates their source vintages. There is no result-to-polygon or cross-year geographic crosswalk. County FIPS only selects rows whose **source FIPS field is explicit**; 27 blank-FIPS shapes remain unassigned. The immutable historical research contract is accepted externally at `../data/coordinator-priority-acceptance.json`; its worker-owned false flag is not the acceptance authority.

## Original bytes and HTTP provenance

`receipts/ID.json` records exact requested/final URL, GET method, parent discovery receipt, start/end UTC, HTTP status, response headers, redirects and headers, any exception, entity SHA256/bytes and ordered storage. An HTTP200 viewer/shell, an empty response, a proposal, or a stale map is never promoted by status alone. Source dates/approval are described separately in `county-research.json`, original documents, source metadata and the report. HTTP Date/Last-Modified, ArcGIS editingInfo, PDF creationDate, printed map date, adoption date and election-effective date are different clocks. Unknown source timezone remains null. Preserve literal clocks rather than guessing a zone.

`storage[]` is ordered by `order`. `encoding:identity` references exact original bytes, while `gzip` references deterministic lossless gzip (mtime0). Recover an entity by decompressing each gzip slice, leaving identity bytes unchanged, then concatenating **in the recorded order**. Compare the complete entity SHA256 and byte count. If an entity cannot be stored below the cap, acquisition splits the **unmodified entity** into consecutive 30,000,000-byte slices, gzips each, and records slice and whole hashes. Every stored file must be strictly below40,000,000 bytes. Current originals fit without splitting. No PDF is truncated or recompressed internally. Identical entities share storage; failed attempts retain their own receipts even when empty entities share one object.

Directly usable PDFs and the original ZIP are stored once in `originals/`; `materialize.py` migrates small PDF/ZIP storage to exact identity bytes and removes unreferenced duplicate representations. `objects/` contains other exact compressed responses, not dependencies or caches. `sources.csv` indexes every request, its parent and receipt; full headers remain in receipts. The original statewide ZIP is SHA256 `4d48e5ba8849cad20809580c3ef56c81c516ef26878a3378be83847394271a8a`,16,477,511 bytes.

## Statewide native geometry

Authority chain: official General Assembly reapportionment page -> its published main JavaScript -> its published anonymous bootstrap algorithm -> `Reapportionment/Page` catalog -> literal `Statewide Voting Precincts (2024)` ZIP link. `scripts/state_catalog.py` reproduces that public chain. No private credentials are involved. The official Geospatial Information Office -> linked data hub was inspected separately; its organization search exposed no precinct layer. This is the General Assembly's precinct publication, not a Census VTD or legislative-district substitution.

The original ZIP retains `.shp`, `.shx`, `.dbf`, `.prj`. `extracts/archive-inspection.json` records every member name, CRC32, uncompressed bytes/SHA256, SHP/SHX/DBF counts, full extent, literal WKT and parsed CRS/axis/unit metadata. All2,724 records remain in the original, including2,697 explicit-FIPS rows across all159 counties and27 blank-FIPS rows. Source shapefile type5 is linear2D polygon, with no Z/M/curve storage. Shapefile coordinate order is literal XY=longitude,latitude; CRS authority axis metadata is retained independently. Native CRS is NAD83, angular degrees, not Web Mercator or county State Plane.

`extracts/state2024-all-attributes.csv` contains all2,724 original row ordinals and every decoded DBF attribute: ID, AREA, DATA, DATA1, DISTRICT, CTYSOSID, FIPS, FIPS2, CTYNAME, CONTY, COUNTY, PRECINCT_I, PRECINCT_N. `row_ordinal` is zero-based, while original SHP record number is one-based. DBF widths/types/padding remain authoritative in the exact ZIP. Numeric parsing and JSON float round-trips do not rewrite the original DBF.

`extracts/FIPS-state2024-native-geometry.json.gz` is a lossless parsed-coordinate/attribute selection for each of the44 priorities. It contains literal WKT, selection rule, all source attributes, row ordinal/record number, shape_type, points, part starts, bbox, z, m, and a secondary GeoJSON interface used for diagnostics. **points/parts and the original SHP are authoritative for original sequence**, including ring orientation and closure; the GeoJSON interface groups rings for consumers and does not replace source sequences. The validator compares every selected point and part to the original. No clipping, simplification, coordinate transformation, repair or allocation is applied. `state2024-unmatched-native-geometry.json.gz` retains all27 blank-FIPS shapes with full source fields. A DISTRICT prefix is not used to assign their county or votes.

## Local GIS services and originals

`service-targets*.json` specifies literal discovered layer URLs and discovery parent receipts. `services/ID.json` records advertised count, OID field, batch receipt IDs, pre/post ID equality, editingInfo comparison and capture status. Original metadata and every response are retained. `scripts/services.py` requests all IDs before and after; fetches bounded100-ID batches with `outFields=*`, geometry, Z, M and true curves requested; applies no outSR, quantization, precision, maxAllowableOffset, clipping or geometry repair. Returned native spatial references/attributes/coordinates are unchanged. Every batch is checked for exact ID coverage, duplicates and exceededTransferLimit. Source changes during acquisition remain a failed/incomplete capture rather than being hidden.

`extracts/ID-service-native.json.gz` assembles the **complete parsed original feature sets**, including their response headers/schema fields within JSON, original geometry objects and native IDs, plus full source metadata/capture index. It is a derivative; exact response bytes remain separately hashed in receipt storage. `service-inspection.json` adds source CRS literal objects, WKT, PROJJSON, axis/unit metadata, actual geometry-key/null/omitted counts and unrepaired diagnostics. Local ID fields, global IDs, null fields, Z/M dimensions and curve objects remain source scoped. No short ID or map count is substituted for a historical app GUID.

Whitfield's265 returned attribute rows omit geometry despite returnGeometry=true. Multiple bounded alternatives retain this omission as `complete_ids_geometry_unavailable`; an omitted geometry is different from a source field explicitly set to null. Those rows do not count as downloaded qualified geometry. The actual2025 precinct PDF and state2024 geometry provide reference assets. Separate election-zone attributes are retained, not dissolved or treated as physical precincts.

PDF originals retain every page, full resolution, media/crop boxes, metadata, scans and annotations. `qa/pdf-inspection.json` records page dimensions/rotation and metadata. `qa/*.txt` is a text derivative; an empty extraction is not an empty map. `qa/*page*.png` and `contact-*.png` render real original pages. Page1 plus selected Cherokee pages have larger previews; contact sheets cover **every page** of every PDF. Dates read from metadata are not legal approval. The report identifies original maps, older references, proposals, notices and wrong-scope materials separately.

## Historical native context and inventory

`input-pins.json` freezes first-wave reports, tables, manifests, contract, acceptance, proofs and controls. `historical-source-pins.json` pins all159 original2024 county JSON bodies and HTTP receipts read-only by exact stored/entity hashes; no duplicates are copied into maps. Other four stages and795 retained county payloads remain accessible through the frozen turnout/baseline manifests; older native rows and raw ballot/registration zero placeholders are unavailable, not zero participation.

`extracts/native-contexts.jsonl.gz` has2,701 records, preserving each complete original contract constituent, native CSV fields, original precinct object and its pointer, original turnout object and pointer, county source election/jurisdiction objects, source body/pointer/hash, priority membership and explicit unapproved geographic status. Original objects remain in the pinned county payloads too, including candidate/method arrays and nulls. Source GUIDs, ordinals, localized labels, administrative/unknown contexts and counts are not deduplicated. Forty candidate nulls and22,416 method nulls remain null. Peer XLSX numerics are distinct source observations and do not replace frozen JSON. `peer-observations.json` retains that exclusion without pinning unfinished peer artifacts. Its concrete read-only Fulton XLSX/HTTP/40-position-ledger references are observations, not build dependencies. The40 app pointers were checked as null against frozen JSON; export numerics totalTrump7/Harris11, while matching labels/counts do not establish a geographic join. The separately reported1,824 known-cell agreement remains attributed to the peer.

`inventory.json` has exactly159 counties and all2,701 constituent keys. Priority rank is **named-four dispatch rank within proved top44 membership**, not full-candidate order. It retains44 priority counties with1,938 native identities and115 others with763 identities. Map-native row indices, map counts, current/local attempts, source findings, documentary status and precise gaps are separate from result identities. `inventory.csv` is a compact overview, not a county-only replacement; `counties/FIPS.html` exposes every native GUID and original map ID/name. No result values are joined to features.

## Diagnostics, previews and scope

`geometry-diagnostics.json` evaluates the whole original state layer and each priority selection for null/empty, nonfinite coordinates, GEOS validity reasons and positive-area pair intersections. State overlap area units are **square angular degrees**; these are planar diagnostics, not ground areas. Local service diagnostics use their actual native metre/US-survey-foot units; Web Mercator areas are projection areas, not ground area estimates. All invalid/null/nonfinite cases and analytic-curve limitations remain explicit. Invalid geometries are excluded from intersection calculations, never repaired. Pair-overlap sums can count triple coverage more than once and are not union area. A zero intersection result does not prove legal boundaries, adjacency gaps, coverage of excluded unknown shapes or historical equivalence.

`previews/*.svg` uses full extent and all linear vertices, rounded only to display pixels. Source data remains exact. Previews are illustrative, uncolored by votes, with deterministic per-feature colors; color does not indicate candidate/party. `index.html` is an offline index with exact44 ordered cards, native-detail/download links, local original previews and all159 inventory. It uses no network tiles, remote libraries or external fonts. `qa/visual-review.json` records actual visual inspections and the lack of an available browser surface for browser-rendered HTML QA; structural/relative-link checks and direct SVG/PDF visual QA remain reproducible offline.

## Reproduce

Python3 with installed `pyshp`, `shapely`, `pyproj`, `PyMuPDF`, `Pillow`; acquisition additionally uses `requests`. No dependency/cache tree is retained. Versions appear in validation. From repo root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/georgia/maps/scripts/render.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/georgia/maps/scripts/build.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/georgia/maps/scripts/report.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/georgia/maps/scripts/validate.py --update-manifest
# Later offline check, without changing the manifest:
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/georgia/maps/scripts/validate.py
```

Acquisition is separate and immutable. `discovery.py targets-initial.json` and other retained targets lists reuse existing receipts; new observations require new IDs. `services.py service-targets.json` likewise reuses frozen responses. To capture fresh source catalog observations without overwriting originals:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/georgia/maps/scripts/state_catalog.py --prefix fresh-20261018-
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/georgia/maps/scripts/acquire.py NEW_ID EXACT_PUBLISHED_URL --parent PARENT_ID
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/georgia/maps/scripts/reconstruct.py state-2024-precinct-zip
```

Reconstruction verifies exact whole bytes by default; optional `--output reconstructed/name` writes below maps. Refresh observations require separate source review; the build remains on the pinned snapshot. `manifest.json` and `manifest.csv` enumerate all owned files (including the report and validation), excluding only the manifests themselves to avoid self-hashes. The validator checks every hash/size, source receipts and storage reconstruction, ZIP member CRC/hash and SHP/SHX/DBF boundaries/counts, all159/all2701 scopes, exact44 order, all native coordinates/parts/attributes, native source objects/nulls/controls, service identity/transfer checks, priority bounds and local relative links. It writes validation before building the manifest, so there is no reverse hash cycle.

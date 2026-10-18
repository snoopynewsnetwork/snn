# Kansas precinct-map package contract

Research date: 2026-10-18 UTC. Writes are limited to `maps/**` and the sibling
`precinct-maps.md`. No Git operations, delegated agents, peer edits, legal-rule
research, result collection or forecast implementation occur in these scripts.

## Geographic and historical scope

`inventory.json` has all 105 counties in the exact frozen 2024 volume order.
`ordered_priority_keys` has the exact 23 coordinator-accepted research keys.
The priority source is four named 2024 presidential tickets, not ballots or
2024 Senate (Kansas had no 2024 Senate election). Votes are 1,067,659 / 1,327,591;
preceding22=1,057,110, crossing Sumner20191 adds10,549; remainder82=259,932.
Unreported statewide write-ins/under/over are unavailable, not zero.

Each `native/<five-digit-FIPS>.json.gz` contains the entire unchanged matching
`all_geography_coverage` county object from the pinned turnout contract. It
retains every constituent object, literal unit key, native ID/name/district/VTD
fields, worksheet/XML path/rows, unknown cells, method/status and overlapping
family relationship. These are detailed native exports, not just county totals.
Five alternative families retain4,567/4,566/4,535/3,867/4,496 identities,22,031 in
all, across525 county-family groups. Unknown-count units remain0/13/12/19/31.
Never sum alternatives or treat county-footer controls as extra precincts.
The complete original candidate-observation and workbook objects remain in the
read-only first-wave assets, pinned by `readonly-pins.json`; no original is
copied. Residuals and blank/redacted cells remain unallocated. Generated native
unit-key hashes identify historical rows, not official physical precinct IDs.

Every `inventory.counties[]` contains county/FIPS/key/rank/priority, native-file
path and five-family counts/unknown counts; complete2022 map FID list and
preview; local assets/scope/vintage/gaps; and `november_2026_boundary_approval:false`.
Every native result remains unmatched. No administrative, unknown, zero-count,
small-enclave or unmatched unit is discarded, assigned a polygon or allocated
votes. A name/ID/count match can support a lexical review candidate only.
County and map feature counts need not agree with results identities.

The2020 Marshall-Bollier Senate contest is ClassII (the2026 seat);2022
Moran-Holland is ClassIII/midterm. The2024 workbook ballot/registration clocks
(1,343,020 /2,031,120) differ from the certification release(1,344,147 /2,031,132).
The2022 ballot workbook is source-inconsistent and is not clean turnout weights;
its county anomalies are not repaired or allocated. The clean named2022 Senate
universe1,004,956 stays separate. Generic2020 write-ins stay outside named
controls; Johnson2020 NON header codes are not candidate identities.

## Original acquisition and storage

`acquisition.json` is an ordered array of immutable request records. `id` is a
local capture identifier, not an official election/precinct ID. Each has exact
`requested_url`, observed `final_url`, retrieval UTC, final HTTP status/headers,
all observed redirects with URL/status/headers, purpose and discovery parent.
A parent capture is a discovery dependency: it is not automatically a verified
HTML hyperlink. Actual authority chains and known missing county-to-vendor
links are distinguished in the report, county notes and source-status inventory.

`original_bytes`/`original_sha256` describe the entire HTTP entity after
requests' Content-Encoding decoding. These are exact original document/JSON
bytes, not the encrypted/compressed wire packets. Errors retain complete bodies;
connection failures retain exception/request URL without invented bytes.
A200HTML viewer, API error, empty search or old/test election is not data.
`source-status.json` labels exclusions; the registry admits only actual PDF,
ZIP or queried native JSON content with explicit scope. Other200 pages are
landing/configuration evidence, not map geometry.

`storage.encoding` is identity for original PDFs below40,000,000bytes and gzip
for other entities. Deterministic gzip usesmtime0. `ordered_parts` lists exact
path/bytes/SHA256 in reconstruction order; stored-stream bytes/hash are also
recorded. All parts are strictly below40,000,000bytes (30,000,000-byte slices
when needed). No asset currently needs split reconstruction. `same_body_as`
shares one stored original for identical bodies while retaining each independent
request/time/status record. Never truncate or simplify an original. `raw/*.body.gz`
may contain a ZIP/JSON/HTML; the suffix is a capture label, not a MIME claim.

`reconstruct.py ID --output desired-file` concatenates exact ordered parts,
checks each part and whole stored stream, decompresses once if needed, and
checks the complete original byte count/hash before writing. With no output
argument, exact bytes go to stdout. It does not overwrite frozen source files.
HTTP Date/Last-Modified/ETag, document printed dates, ArcGIS item/geometry edit
epochs, source field dates and retrieval UTC are distinct clocks. A printed
date without timezone stays date-only. Unknown effective date/timezone/status
remains unavailable. No filemtime/app count/catalog edit establishes election
approval, genuine live cadence or November geography.

## Native geometry and service completeness

`services.json` defines each complete queried layer, county attribution,
URL, native CRS, OID field, advertised count, batch capture IDs and flags.
`services.py` requests count and all object IDs before acquisition, sorted
batches of at most100 IDs, and count/all IDs afterward. Exact batch-ID sets,
unique full ID union, pre/post equality and transfer-limit flags are checked.
`outFields=*`, native output CRS (no outSR), `returnZ=true`, `returnM=true`,
`returnTrueCurves=true` preserve available schema/attributes/coordinates/Z/M/
curves. No geometryPrecision, quantization, envelope, clipping or repair is used.
Root/layer metadata and post-layer snapshot are retained. The native JSON pages
preserve full fields/domains, attributes, geometry parts/vertices and CRS objects.
Full-extent queries are saved separately and checked against actual bounds.

A completed ID inventory does not prove geometry was returned. Wyandotte's153
queried objects omit geometry altogether under both curve settings: they remain
attributes-only evidence, not153 downloaded polygons. Its actual original PDF
is the map reference. Missing geometry is unavailable, not an empty/zero polygon.

The state KLRD/DASC layer is explicitly2022 post-redistricting precinct data.
All4,749 objects and all105 county groups are retained, not just priority
subsets. Its county `CO_CODE` and all literal `VTD_2022_L/S/N`, district/population
fields remain native; they are not a2024/2026 crosswalk. Counties may have
subsequently renamed, recombined or changed those precincts. The data is a
historical reference, never evidence of current physical equivalence.

County service sources are independent snapshots, with overlapping alternatives
such as Montgomery Precincts and Precinct Parts. Do not sum those layers or
compare OID counts to votes/precincts-reporting. County source labels like
precinct part, ward, polling area and voting district retain their own meaning.
Reno/Montgomery/Sumner agency-attributed products have explicit outbound-county
link gaps; their institutional naming does not itself settle authority.

`extracts/archive-checks.json` records every original ZIP member's exact name,
uncompressed/compressed bytes, CRC32 and SHA256; every CRC is tested. SHP/SHX/DBF
record counts, SHP record boundaries, exact SHX offsets/content lengths,
shape-type counts, field definitions, native PRJ WKT/header bounds, and Z/M
ranges/null/sentinel counts are checked without extracting persistent copies.
Sedgwick is PolygonZ: original Z/M arrays remain in its SHP bytes, including
any null/NoData measures. Original DBF encoding/headers remain in the ZIP.

`extracts/<source>-geometry.json.gz` contains all feature attributes, original
native CRS plus interpreted WKT/axes/units, full coordinate extent, native
vertex/ring counts, null/nonfinite/invalid/curve lists and overlap diagnostics.
`extracts/map-feature-attributes.json.gz` retains every downloaded map object's
complete attributes and source/row reference, explicitly unmatched to results.
Coordinates are authoritative only in the untouched raw geometry, not a preview.

GEOS diagnostics operate on an explicitly XY-only copy; they preserve original
Z/M values in raw source pages/SHP. NullM values are not geometry failures.
True curves are enumerated and excluded from GEOS instead of silently
linearizing them. Four Shawnee true-curve IDs2120/2176/2199/2211 remain native;
a separate exact-ID server query with `returnTrueCurves=false` supplies preview
geometry only. The earlier provisional three-ID preview probe is retained and
excluded. Planar positive-area intersections are computed between valid polygons,
without tolerance cutoff; small areas can be numerical slivers, not proven
legal overlaps. Units are source feet², metres² or degree² as recorded. Invalid,
missing and true-curve units are enumerated as omitted from the XY overlap test.
No originals are snapped, buffered, dissolved, made_valid or otherwise repaired.
Diagnostics do not certify absence of legal gaps/overlaps or precise county
boundary agreement. No current-approved county boundary was obtained for that
legal overlay; full native extent is retained and transformed only for broad
Kansas scope checks in validation.

## Previews, PDF inspection and offline index

`build.py` generates105 state-reference SVGs and local geometry SVGs. Every
available part/vertex is traversed; display XY alone is rounded to0.01 image
pixel and fitted to full source extent. The original geometry is neither
simplified nor clipped. Shawnee's four linearized preview objects are separate
from original curves. SVG path tooltips expose native attributes; colors have
no vote/party/turnout meaning. A preview is not an additional source geometry.

All original PDF pages render into `previews/pdf-contact-*.jpg` and page1 into
`previews/<capture>.png`, preserving entire page bounds. Complete originals
stay full-resolution. Text and original PDF metadata/page sizes live under
`extracts/`. Raster scans can have no extracted text; visual inspection is
recorded in `visual-review.md`. OCR/catalog date inference never replaces an
actual printed date. The Pottawatomie legislative PDF, Barton polling-area map
and2018 Cowley mirrored map have their actual limited/reference scopes.

`index.html` works via file:// with no network libraries, basemap or fetch.
Its23 cards are in the exact accepted key order, each with actual informative
preview, original downloads (or clearly labeled historical fallback), vintage
and county-specific gaps. Every105-county inventory row links full native
context and2022 preview. Source originals are stored once; county FID lists
identify each county inside full state pages. No county-only replacement for
historical native detail occurs.

## Reproduce and freeze

From repository root, with existing Python packages requests, PyMuPDF, Pillow,
pyshp, pyproj, Shapely/GEOS (versions in outputs):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/kansas/maps/build.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/kansas/maps/validate.py
# Exact original reconstruction example, writes only the chosen output:
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/kansas/maps/reconstruct.py johnson-shp --output senate/2026/kansas/maps/reconstructed-johnson.zip
# Optional independent new network snapshot, never overwrites frozen originals:
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/kansas/maps/reacquire.py new-snapshot
```

`acquire.py` is the single-source downloader; `reacquire.py` replays every
requested URL in original order into a new child directory. Responses can change;
new retrieval clocks/hashes remain independent. `discover.py` retains bounded
research follow-ups; the full acquisition manifest is the authoritative complete
recipe. `pin_inputs.py` verifies immutable first-wave pins and all127 owned
hashes, retaining full52 shared source metadata objects without copying their
originals. `readonly-pins.json` does not hash coordinator acceptance back into
the worker contract. Acceptance is read externally and checked at validation.

`asset-manifest.json` hashes every owned stored file plus the report, excluding
itself, `validation.json` and `FROZEN.json` to avoid cycles. `FROZEN.json` pins the
manifest/report and read-only input manifest; validation checks those pins.
`validation.json` contains actual offline results and checked UTC. `seal.py`
regenerates the asset manifest and final freeze, then validation must pass.
Rebuilding intentionally does not silently bless modified originals by resealing.
No dependency/cache tree is included. All stored assets are strictly<40MB.

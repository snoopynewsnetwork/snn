# Illinois maps schema

Authority for the frozen historical dispatch is the external PATH
`../data/coordinator-priority-acceptance.json`. Its body and digest are never
copied into this package. It is read in memory at runtime. Producer approval
flags stay false. All original first-pair bodies are reused read-only through
the exact immutable references in that external authority and its producer
seals. The package does not run a producer or an appendable acquisition writer.

`derived/full-inventory.json.gz` is an array of all 10,062 complete observation
objects in the accepted `full_order`. `priority-index.json.gz` is the exact first
5,540 complete objects; `remainder-index.json.gz` is the remaining 4,522 complete
objects. `rank_full` starts at 1. `rank_priority` is null for the remainder.
`source_observation` is the complete, unchanged producer constituent object,
including all literal categories, missing/null cells, containers, names, record
positions and presentation references. It is not a legal/current precinct.
Every entry has specific archive/leaf receipt references, geographic county
fallback and preview references, and access/vintage/finer/current/administrative
gaps. `matched_geometry`, `physical_polygon`, and `source_method` remain null.
Label text alone does not create a method or administrative classification.

`derived/parents.json.gz` contains all 108 complete historical `source_parent`
objects, complete source-order children, complete full-rank children, and
ordered priority/remainder children. Exactly 97 parents have priority children.
The six municipal parents remain distinct: 104 Bloomington, 105 Chicago,
106 Danville, 107 East St. Louis, 108 Galesburg, 110 Rockford. County FIPS in an
entry is only its inherited geographic context locator. It never substitutes
for a source reporting parent. The 102 combined county result selector views
already contain applicable city views; the atlas never sums those overlapping
result products. It does not allocate candidate totals to geography.

`derived/authority-investigations.json` retains all 108 actual archive chains,
all literal linked files across the observed nested hierarchy, selected complete
original receipts and actual leaf access receipts. Complete raw directory HTML
also preserves directory timestamps, file sizes, variants and all unrelated
links. A directory timestamp is a file-publication clock, not a boundary date.
A HEAD response is access evidence, never an acquired map body. An unacquired
oversized original has an explicit access gap. Nested Chicago wards and Will
township/precinct folders are preserved; they are not empty-folder findings.

`source/ID.receipt.json` records method, full requested URL/query/body, actual
parent receipt ID and literal href, discovery basis, request headers, start/end
UTC, final URL/status, all returned headers, redirects and errors. Original
requests use public GET/HEAD only. Redirect bodies, if present, are exact hex
in each redirect record. Complete decoded response entities are losslessly
compressed in `stored_parts`. Concatenate parts in declared order, then gunzip
once; compare raw byte count and SHA256. Stored part pins are state-relative.
Each stored object is strictly below 40,000,000 bytes. Decoded entities are not
wire Content-Encoding bytes; those source headers remain literal. Unknown
display clocks/timezones stay null. HTTP Date/Last-Modified/ETag are separate
publisher metadata and do not establish election-effective geography.

`derived/counties/FIPS.native.json.gz` is an exact-native 2020 Census VTD
geographic slice, covering every original record in that source county, including
null/empty/invalid records if present. All 102 slices are supplied. They contain
native WKT and units, every original DBF field descriptor, every full original
row as hex, padded literal fields, parsed attributes, source record/index
positions, full content hashes, exact bbox/part arrays and every XY binary64
coordinate represented by roundtrippable JSON numbers. The original ZIP remains
the controlling byte source. These JSON slices are not rewritten shapefiles.
No source geometry/header/attribute is repaired. Source record numbers remain
statewide; they are not renumbered within counties. The original is 2D Polygon:
Z/M/truecurves are null, rather than fabricated. The schema supports retaining
source null/empty records; none occurred in this particular Census original.

`derived/census-record-index.json.gz` preserves the exact original SHP offsets,
content bytes/hash, DBF row hash, native GEOID and county fields, point/part
counts for every original record. `county-fallback-index.json` has all 102
complete county record-position arrays, native-slice and preview paths. County
slicing uses only literal STATEFP20/COUNTYFP20; no source observation label,
spatial candidate allocation or historical/current crosswalk enters slicing.

`derived/previews/*.svg` uses the complete native point/part arrays. The sole
coordinate transform is affine `scale(1,-1)` with a fitted viewBox and equal
X/Y scale in native degrees. No geographic reprojection, basemap, rounding or
coordinate reduction occurs. SVG even-odd fill is a display rule, not shell/hole
assignment; geometry remains the raw parts in the native slices. The previews
are not measurements or controlling legal maps. `atlas.html` embeds the exact
5,540 priority sequence, full 10,062 inventory and all 108 complete parent/child
arrays, plus every complete source observation object, visible in row details. It needs no network/CDN/fetch or external JavaScript library. It loads
local SVGs and links local receipts/slices. Gzip download links are compressed
data; use the reconstruction instructions rather than expecting browser GIS.

`derived/original-asset-inventory.json` records complete PDF page counts, boxes,
metadata and full-page text extraction references, ZIP member CRC/hash metadata,
and raster size/format. Original PDF bytes contain every page, including pages
outside the selected visual sample. Automatically extracted vintage text is
uninterpreted; apparent years are not approved boundary-effective dates.
`qa/visual-review.json` alone declares actually viewed pages/previews, separately
from automated extraction/render lists. No unseen browser inspection is claimed.

`qa/census-binary-audit.json` records all-member CRCs, complete SHP/SHX/DBF checks,
all record bboxes/indices/parts/XY bits and unitless individual-ring simplicity.
It performs no whole-feature shell/hole reinterpretation, positive-area,
adjacency, overlap, sliver, gap, legal-boundary or current compatibility
certification. Native coordinate units are degrees. Source ALAND20/AWATER20
attributes remain source integers, not recomputed planar degree areas.

`qa/contract-replay.json` is a result of streaming **all** 554,096 complete
recursive reference records, verifying all 31 root fields, all 116 companion
bodies and every producer-sealed asset/original reference. All 146,370 complete
12-field source records, 11,535 2024 presentations and other historical scopes
remain reconstructable from immutable producer references. This is not a
sampled, selected-only or vote-only ledger. No extra giant original copy is
needed. Exact reference schemas and positions come from the external authority
at runtime; the replay never writes to that authority or producer directories.

`asset-manifest.json` inventories the exact owned membership: this report plus
every file under maps. It excludes only itself to avoid a recursive digest.
`qa/validation.json`, `negative-fixtures.json` and `deterministic-replay.json`
record offline checks. No dependency/cache directories are part of this package.

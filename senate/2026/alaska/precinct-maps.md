# Alaska official precinct map assets

**Downloaded: all 28 priority native House Districts, with 256 individual
physical precinct PDF pages and separate baseline/current GIS snapshots.** Open
the [local map index](maps/index.html) for the original official packets,
all-page contact sheets, 56 district/vintage GeoJSONs and 56 SVG previews. The
official statewide shapefile ZIP and the current DOE locator's complete native
GIS responses each retain **402 physical features across HD1-40**. HD99 is
administrative and has no assumed polygon. The [manifest](maps/manifest.csv)
records exact URLs, official owner, geometry vintage, approval status, UTC
retrieval, native geography, CRS, page/feature counts, bytes, hashes and paths.

Research observations were retrieved **2026-10-18 UTC / 2026-10-17
America/Chicago**. **April 2024 precinct adoption is documented; approved
November 3, 2026 boundaries are not established.** A currently published map,
current locator or September 2026 service edit does not supply that approval.
No verified votes are allocated to polygons, and no live collector or calibrated
forecast is claimed.

The [reconciled turnout dispatch](data/turnout/priority-set.json) fixes the rank
order: **6, 9, 3, 8, 23, 29, 25, 30, 24, 34, 11, 35, 16, 7, 36, 2, 26, 15, 28,
4, 21, 27, 33, 10, 1, 12, 5, 17**. These district groups account for **271,492 /
338,177 = 80.28103626%** of 2024 presidential candidate votes; the largest 27
supply only **263,774 = 77.99879945%**. The total includes district administrative
counts, so it does not mean 80.28% of votes have been geographically assigned.
The [coordinator reconciliation](data/coordinator-baseline-reconciliation.json)
independently verified 533 candidate/HD cells and 82 same-election totals. This
map task uses that completed baseline without changing its arithmetic.

## Primary authority, vintage and acquisition

The modern [Division of Elections district maps page](https://www.elections.alaska.gov/research/district-maps/)
is the primary map authority. Its saved response explicitly identifies precincts
adopted in April 2024 and conforming to the Redistricting Board's May 15, 2023
Final Proclamation. It links all 40 HD packets and the
[official precinct shapefile ZIP](https://www.elections.alaska.gov/doc/maps/AK_Election_Precincts_2023Final.zip).
The individual packets are described as final maps for 2024 and print “May 15,
2023 Redistricting Plan.” The ZIP metadata contains `20240425` metadata creation
and a Web Mercator CRS; internal feature edit dates are not substituted for
election-effective approval dates. This is the published historical baseline,
retrieved in 2026, rather than an independently frozen election-day export.

Each of the 28 dispatch PDF links was required to appear on the newly retrieved
modern primary page, then downloaded sequentially in the exact priority order.
The 28 original PDFs total 256 pages; they are individual named precinct maps,
not 28 district outlines. The statewide combined PDF was not redundantly
downloaded. Original PDF/ZIP bytes, response headers and raw SHA-256s are retained
under `maps/originals/`. The 10,177,631-byte ZIP is directly usable and unmodified;
its six members, CRCs and individual hashes are audited in
[archive-members.json](maps/archive-members.json).

For a distinct current observation, the primary map page/homepage links the
[Division's precinct locator](https://akelections.maps.arcgis.com/apps/webappviewer/index.html?id=579890d66c7e40ae9f7cc227d76669b1).
The saved application has owner **DOEALASKA**, explicitly identifies the State
of Alaska Division of Elections, and names webmap
`6fac55e6f6914c0da0f90e7e444b3626`. That webmap directly includes
[AK Election Geography / Precincts layer 7](https://services3.arcgis.com/AhVzMlCdMxpkPzPE/arcgis/rest/services/AK_Election_Geography/FeatureServer/7?f=pjson).
The matching [service item](https://www.arcgis.com/sharing/rest/content/items/02dec5e7ae604bff951a95bc8a08f9e8?f=pjson)
also has owner DOEALASKA and the exact service URL. This establishes an official
DOE chain rather than relying on an unlinked third-party map or a title alone.
App, webmap, service, layer and owner evidence are retained in `maps/raw/`.

The layer reports `dataLastEditDate=1790700628838`, or **2026-09-29
16:50:28.838 UTC**, while its catalog item was created in June 2022 and last
modified in July 2022. These are different metadata clocks. No source says the
layer is a certified November 2026 boundary set. Its directory is deliberately
named `current-retrieved-2026`, not `approved-2026`.

The service count and full object-ID query both return **402**. All 402 were
downloaded in **9 batches of at most 50** using `objectIds`, `outFields=*` and
`returnGeometry=true`, preserving native EPSG:3857 coordinates. Every batch's IDs
match its request, no `exceededTransferLimit` flag is present, and the complete
returned set equals the count and ID query. There is no spatial filter,
quantization, simplification, geometry-precision parameter or server reprojection.
See [pagination checks](maps/pagination-checks.json). Original EsriJSON response
bytes remain losslessly compressed, separate from derived GeoJSON.

## Exact priority precinct coverage

Each row below has both baseline and current GIS coverage. The page count is
also the count of distinct physical precinct IDs in the 2024 results roster for
that HD. All **256 of 256** native physical IDs have a packet page and a polygon
in each snapshot, with no extra or missing IDs. This is inventory compatibility,
not approval of a geographic vote crosswalk.

| Rank | Native HD | Individual PDF pages / 2024 physical IDs | Baseline GIS features | Current locator features | Original official packet |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 6 | 9 | 9 | 9 | [HD6](maps/originals/HD6_May2023Final_Maps.pdf) |
| 2 | 9 | 9 | 9 | 9 | [HD9](maps/originals/HD9_May2023Final_Maps.pdf) |
| 3 | 3 | 10 | 10 | 10 | [HD3](maps/originals/HD3_May2023Final_Maps.pdf) |
| 4 | 8 | 11 | 11 | 11 | [HD8](maps/originals/HD8_May2023Final_Maps.pdf) |
| 5 | 23 | 6 | 6 | 6 | [HD23](maps/originals/HD23_May2023Final_Maps.pdf) |
| 6 | 29 | 9 | 9 | 9 | [HD29](maps/originals/HD29_May2023Final_Maps.pdf) |
| 7 | 25 | 7 | 7 | 7 | [HD25](maps/originals/HD25_May2023Final_Maps.pdf) |
| 8 | 30 | 12 | 12 | 12 | [HD30](maps/originals/HD30_May2023Final_Maps.pdf) |
| 9 | 24 | 7 | 7 | 7 | [HD24](maps/originals/HD24_May2023Final_Maps.pdf) |
| 10 | 34 | 8 | 8 | 8 | [HD34](maps/originals/HD34_May2023Final_Maps.pdf) |
| 11 | 11 | 7 | 7 | 7 | [HD11](maps/originals/HD11_May2023Final_Maps.pdf) |
| 12 | 35 | 8 | 8 | 8 | [HD35](maps/originals/HD35_May2023Final_Maps.pdf) |
| 13 | 16 | 7 | 7 | 7 | [HD16](maps/originals/HD16_May2023Final_Maps.pdf) |
| 14 | 7 | 6 | 6 | 6 | [HD7](maps/originals/HD7_May2023Final_Maps.pdf) |
| 15 | 36 | 40 | 40 | 40 | [HD36](maps/originals/HD36_May2023Final_Maps.pdf) |
| 16 | 2 | 15 | 15 | 15 | [HD2](maps/originals/HD2_May2023Final_Maps.pdf) |
| 17 | 26 | 7 | 7 | 7 | [HD26](maps/originals/HD26_May2023Final_Maps.pdf) |
| 18 | 15 | 6 | 6 | 6 | [HD15](maps/originals/HD15_May2023Final_Maps.pdf) |
| 19 | 28 | 7 | 7 | 7 | [HD28](maps/originals/HD28_May2023Final_Maps.pdf) |
| 20 | 4 | 8 | 8 | 8 | [HD4](maps/originals/HD4_May2023Final_Maps.pdf) |
| 21 | 21 | 5 | 5 | 5 | [HD21](maps/originals/HD21_May2023Final_Maps.pdf) |
| 22 | 27 | 5 | 5 | 5 | [HD27](maps/originals/HD27_May2023Final_Maps.pdf) |
| 23 | 33 | 6 | 6 | 6 | [HD33](maps/originals/HD33_May2023Final_Maps.pdf) |
| 24 | 10 | 6 | 6 | 6 | [HD10](maps/originals/HD10_May2023Final_Maps.pdf) |
| 25 | 1 | 10 | 10 | 10 | [HD1](maps/originals/HD1_May2023Final_Maps.pdf) |
| 26 | 12 | 6 | 6 | 6 | [HD12](maps/originals/HD12_May2023Final_Maps.pdf) |
| 27 | 5 | 12 | 12 | 12 | [HD5](maps/originals/HD5_May2023Final_Maps.pdf) |
| 28 | 17 | 7 | 7 | 7 | [HD17](maps/originals/HD17_May2023Final_Maps.pdf) |
| **Total** | **28** | **256** | **256** | **256** | **28 original packets** |

[Page inventory](maps/pdf-page-inventory.csv) lists every PDF page, its native
precinct ID, exact source URL and extraction evidence. All pages were extracted
in layout and raw text order and rendered in 28 contact sheets. All contact
sheets were visually inspected; full-page representatives include urban Homer,
rural Allakaket and the two malformed-title pages. PDF headers for **21-725 East
Anchorage No. 5** (HD21 page 5) and **33-183 Plack** (HD33 page 6) actually display
`2 -725` and `3 -183`; their interior map labels give the full IDs. These are
original publication defects, not corrected PDFs. Road labels also interleave
with some extracted headings; raw extraction resolves those cases. The original
map interior, GIS ID and authoritative results roster jointly support the
recorded ID. [Representative renders](maps/derived/representative/HD21-page05.jpg)
preserve the evidence; the original PDFs remain authoritative.

## Complete native inventory and results compatibility

The [41-row native HD inventory](maps/native-hd-inventory.csv) retains HD1-40 and
HD99, including nonpriority units. State FIPS is **02** and `county_fips` is
blank throughout. These are native House Districts, not boroughs, census county
equivalents or artificial county aggregates. Statewide GIS includes all 40
geographic HDs, so the 12 nonpriority HDs have retained polygons even though
their PDF packets were not downloaded. No HD99 polygon or bounding box is
invented.

[Reporting-unit compatibility](maps/reporting-unit-compatibility.csv) retains
every authoritative key, exact source label, native precinct ID/sequence and
unit type from [all 523 actual 2024 units](data/turnout/reporting-units-2024.csv)
and [all 522 actual 2022 units](data/turnout/reporting-units-2022.csv). The 2024
inventory has **402 physical + 120 district administrative + 1 HD99** records;
2022 has **401 + 120 + 1**. All 402 statewide 2024 physical native IDs match both
GIS ID sets. Administrative units have no automatic physical mapping; all 2022
rows remain explicitly un-crosswalked, even when district or precinct numbers
look similar. No 2020-2022 or 2022-2024 boundary crosswalk is established.

The four 2024 units labeled `District 6 - Early Voting`, `District 7 - Early
Voting`, `District 8 - Early Voting` and `District 37 - Early Voting` mix actual
Election Day and Early Voting method columns. Their native keys and mixed-method
status remain visible. Source-label categories and actual counting methods are
different fields; those records, other Absentee/Early/Question administration,
and HD99 cannot be mapped to physical polygons by label alone. No votes,
including the Election Day components of these four records, are assigned to
polygons here.

## CRS, original geometry and defects

Both the ZIP `.prj` and current layer identify **EPSG:3857 / ESRI:102100**, WGS 84
Web Mercator Auxiliary Sphere, in projected meters. Source-native full labels
are `Precinct_N` / `HouseDistr` in the shapefile and `Precinct_Number` /
`HouseDistrict` in the locator, for example `06-200 Anchor Point` and house
district `06`. Full labels, leading zeroes and source attributes remain in
derivatives; short `research_native_precinct_id` is an explicitly derived
six-character inventory key. GlobalIDs and OBJECTIDs are preserved source
attributes, not assumed stable election keys. Source area/length fields remain
source attributes, not recomputed after reprojection.

The 56 GeoJSON derivatives use pyproj EPSG:3857 -> EPSG:4326 with `always_xy=True`,
stored as **OGC:CRS84 longitude/latitude**. All original vertices are retained at
full floating-point precision; whitespace is compacted without simplification,
rounding, clipping or repair. Native original geometry remains separately
available. SVG previews fit native projected coordinates to a display box and
round only display positions to 0.01 units; they have no basemap and are
unsuitable for distance/area measurements.

[Topology diagnostics](maps/topology-checks.json) find **2 invalid features in
each snapshot**, both ring self-intersections: **36-010 Allakaket** (priority)
and **37-732 Manokotak** (outside priority). There are **zero empty features**.
The complete statewide pairwise spatial-index check finds **26 positive-area
overlap pairs in the baseline and 30 in the current snapshot**, ranging from
tiny numerical slivers to larger overlaps. Projected EPSG:3857 area is distorted
and is not geodesic land area. The saved diagnostics list every pair and area;
no arbitrary size threshold silently removes defects. No overlay operation
raised a GEOS error, but that does not validate the self-intersections or legal
boundaries. An independent legal-boundary/land-coverage reference was not
available here, so gap, district-containment and legal-adjacency certification
remain open.

The baseline shapefile also has **eight features whose rings are all
counterclockwise**, violating the normal shapefile shell convention:
`04-130`, `33-155`, `37-756`, `18-556`, `26-380`, `26-350`, `39-942`, `18-555`.
Pyshp warns and emits their rings as exterior shells rather than dropping them.
This is an explicit derivative interpretation, not a repaired original. The
current EsriJSON has no such winding anomaly. Details, native signed areas and
handling are retained in [ring-orientation-checks.json](maps/ring-orientation-checks.json).
Review affected interpretations before any overlay or allocation.

[Snapshot diagnostics](maps/snapshot-comparison.json) retain strict and
tolerance-based comparisons of all 402 common IDs. Binary shapefile coordinates
versus decimal JSON serialization can make strict equality fail; that alone
does not prove a substantive boundary change. Ring ordering/winding also affects
coordinate comparisons. After normalizing order/winding solely for comparison,
**399 of 402** match within `1e-7` projected meter; **04-105, 04-115 and 30-555**
still differ beyond that tolerance. Their effective change dates and legal
explanation are not established. No normalization or tolerance is applied to
the retained originals or exported vertices. Neither common IDs, similar previews nor a comparison
tolerance establish approved November geography or a vote crosswalk. Both
original snapshots are retained separately.

## Access, audit and remaining gaps

System `/usr/bin/curl` with **default certificate validation** successfully
downloaded the modern primary map page, all required PDFs, ZIP, DOE locator
metadata and complete GIS. No TLS validation was disabled. The bounded
[legacy `Core/districtmaps.php` route](https://www.elections.alaska.gov/Core/districtmaps.php)
returned **HTTP 405** with an access-block response; its exact URL, UTC retrieval,
headers, body hash and failure bytes remain in the source evidence. It was not
counted as a map. The working modern route supplied the original links, so the
legacy failure did not leave a physical-asset coverage gap.

The [source evidence manifest](maps/evidence-manifest.json) retains every
successful and failed response's original/stored/header hashes and HTTP
metadata. [Offline validation](maps/validation.json) checks source and asset
bytes/hashes, ZIP members and binary counts, all service IDs/batches, all 41 HDs,
all 1,045 historical unit keys/labels, the exact ordered 28-HD set, the 56
HD/vintage coverage rows, all 256 PDF page/precinct matches, GeoJSON coordinates
and rings, approval labels, relative links, and file sizes below 40 MiB.
Passing these checks means the retained artifacts reconcile; it does not certify
the defective geometry. No runtime cache is retained.

Reproduce with [the package instructions](maps/REPRODUCE.md),
[download scripts](maps/fetch_maps.py), [locator pagination](maps/fetch_locator.py),
[offline build](maps/build_maps.py) and [independent audit](maps/audit_maps.py).
Dependencies and software versions are retained. Original bytes need no
splitting because every source and derivative is below 40 MiB; gzip is lossless.

The substantive unresolved gaps are **November 2026 approval/effective boundary
evidence for all 28 priority HDs; geographic vote/administrative-unit crosswalks;
2020-2022 and 2022-2024 spatial crosswalks; source self-intersections, overlaps
and baseline winding interpretation; and independent legal-boundary/gap review**.
There are **no missing physical 2024 precinct IDs or individual PDF pages within
the priority set**, and both current/baseline native GIS snapshots are fully
downloaded statewide. Keep current and historical vintages separate until those
gaps are resolved.

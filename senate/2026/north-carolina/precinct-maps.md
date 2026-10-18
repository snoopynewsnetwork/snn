# North Carolina precinct maps

Research date: **2026-10-17 America/Chicago**; downloads **2026-10-18 UTC**. **Both selected official boundary snapshots cover all 38 assigned priority counties.** The [map index](maps/index.html) links **76 county GeoJSONs and 76 SVG previews**: **1,833 features** in the July 23, 2024 snapshot and **1,829** in the August 24, 2026 snapshot. These are geographic feature counts, not election reporting-unit counts. **Approval for November 3, 2026 and an election-specific results crosswalk are not established.**

The exact priority order below comes from the reconciled [turnout report](turnout.md) and [100-county CSV](data/county-turnout.csv): **4,576,486 / 5,699,145 = 80.30127326%** of certified **2024 presidential** votes. North Carolina had no 2024 Senate election. The separate 2022 Senate sensitivity adds Haywood; it does not change this assignment's primary 38-county set. All 100 counties remain in the original statewide archives, [source inventory](maps/county-inventory.csv), result-unit diagnostics and statewide denominator checks. Haywood's geometry is retained in those archives, although no separate county GeoJSON is exported for it.

## Official authority, sources and dates

The [NCSBE Voting Maps/Redistricting page](https://www.ncsbe.gov/results-data/voting-maps-redistricting) links its precinct shapefile and KML entries to the same [public precinct folder](https://dl.ncsbe.gov/?prefix=ShapeFiles/Precinct/). The page identifies that folder as containing current and past geospatial files. The folder's actual HTML and JavaScript expose the `dl.ncsbe.gov` S3 bucket. The [inspected object listing](https://s3.amazonaws.com/dl.ncsbe.gov?prefix=ShapeFiles%2FPrecinct%2F&max-keys=1000), retained as [XML](maps/raw/ncsbe-precinct-list.xml), returned **`IsTruncated=false`**. The selected filenames were present in that listing before download; no future URL was inferred.

| Snapshot | Direct official download | Source evidence | Retained bytes / retrieved UTC |
| --- | --- | --- | --- |
| Historical, pre-2024-general | [SBE_PRECINCTS_20240723.zip](https://s3.amazonaws.com/dl.ncsbe.gov/ShapeFiles/Precinct/SBE_PRECINCTS_20240723.zip) | Latest dated 2024 precinct ZIP in the inspected folder; embedded XML `mdDateSt=20240723`; S3 Last-Modified 2024-07-23 18:06:15 UTC | 22,091,618 / 2026-10-18 00:26:04.817694 UTC |
| Current published state archive | [SBE_PRECINCTS_20260824.zip](https://s3.amazonaws.com/dl.ncsbe.gov/ShapeFiles/Precinct/SBE_PRECINCTS_20260824.zip) | Latest dated precinct ZIP in the inspected folder; S3 Last-Modified 2026-08-28 19:06:14 UTC; NC OneMap metadata independently gives publication date 2026-08-24 | 24,357,323 / 2026-10-18 00:26:06.171644 UTC |

The originals are retained once, without repacking, in [maps/raw/](maps/raw/). ZIP CRCs and each member's SHA-256 are checked; county subsets avoid downloading duplicate statewide geometry from another service. The 2024 archive contains **2,656 features across 100 counties**; the current archive contains **2,625 across 100 counties**. Filename dates, publication dates, metadata synchronization dates, HTTP dates and election-effective dates are different concepts. The historical file is a useful pre-election baseline, **not proof of the legally effective November 5, 2024 precinct roster**. No election-day frozen legal-boundary certification was found in these sources.

The official [NC OneMap Voting Precincts layer](https://services.nconemap.gov/secure/rest/services/NC1Map_Boundaries/FeatureServer/0) explicitly attributes its boundaries to NCSBE and credits NCSBE, CGIA and NC OneMap. Its [downloaded XML metadata](maps/raw/onemap-metadata.xml), from the [metadata endpoint](https://services.nconemap.gov/secure/rest/services/NC1Map_Boundaries/FeatureServer/0/metadata), names NCSBE as publisher, gives **publication date 2026-08-24** and **metadata date 2026-09-09**. Those dates corroborate publication, not November approval. Its linked ArcGIS item lookup returned HTTP 200 with JSON error **400, “Item does not exist or is inaccessible.”** That failed catalog lookup is retained in [onemap-item.json](maps/raw/onemap-item.json); the functioning state service and NCSBE archive supply the authority evidence.

NC OneMap was independently queried for count, object IDs and all statewide attributes, without duplicate geometry downloads. Its maximum page size is 2,000. The saved pages contain **2,000 + 625 = 2,625** records; the first page flags a transfer limit, the final page does not. The returned unique object-ID set exactly equals the independent ID query and count. All **county + precinct keys** match the current archive. The tested `id`, `county_id`, `enr_desc` and `of_prec_id` attributes agree after trimming blank padding; 2,624 records differ only in empty-string versus space padding in `of_prec_id`. **Geometry equivalence between the service and ZIP is untested.** Request URLs, timestamps, response headers, original/stored hashes and gzip information are in [evidence-manifest.json](maps/evidence-manifest.json); the pagination and attribute checks are in [checks.json](maps/checks.json).

## Coverage and downloads

Each row links two generated previews; use the [index](maps/index.html) or [manifest](maps/manifest.csv) for the corresponding full-precision county GeoJSON. Counts in parentheses are invalid native geometries, also invalid after export. Every selected county has unique, nonempty native precinct IDs within each snapshot. No feature was dropped or repaired.

| County, in certified volume order | FIPS | NCSBE ID | 2024 features (invalid) | Current features (invalid) | Previews |
| --- | --- | ---: | ---: | ---: | --- |
| Wake | 37183 | 92 | 210 (0) | 216 (0) | [2024](maps/2024-07-23/wake.svg) / [current](maps/2026-08-24/wake.svg) |
| Mecklenburg | 37119 | 60 | 195 (0) | 195 (0) | [2024](maps/2024-07-23/mecklenburg.svg) / [current](maps/2026-08-24/mecklenburg.svg) |
| Guilford | 37081 | 41 | 165 (0) | 165 (0) | [2024](maps/2024-07-23/guilford.svg) / [current](maps/2026-08-24/guilford.svg) |
| Forsyth | 37067 | 34 | 108 (0) | 108 (0) | [2024](maps/2024-07-23/forsyth.svg) / [current](maps/2026-08-24/forsyth.svg) |
| Durham | 37063 | 32 | 60 (0) | 58 (0) | [2024](maps/2024-07-23/durham.svg) / [current](maps/2026-08-24/durham.svg) |
| Buncombe | 37021 | 11 | 80 (0) | 80 (0) | [2024](maps/2024-07-23/buncombe.svg) / [current](maps/2026-08-24/buncombe.svg) |
| Cumberland | 37051 | 26 | 77 (0) | 77 (0) | [2024](maps/2024-07-23/cumberland.svg) / [current](maps/2026-08-24/cumberland.svg) |
| Union | 37179 | 90 | 54 (1) | 54 (0) | [2024](maps/2024-07-23/union.svg) / [current](maps/2026-08-24/union.svg) |
| New Hanover | 37129 | 65 | 41 (0) | 41 (0) | [2024](maps/2024-07-23/new-hanover.svg) / [current](maps/2026-08-24/new-hanover.svg) |
| Johnston | 37101 | 51 | 36 (0) | 34 (0) | [2024](maps/2024-07-23/johnston.svg) / [current](maps/2026-08-24/johnston.svg) |
| Cabarrus | 37025 | 13 | 39 (0) | 38 (0) | [2024](maps/2024-07-23/cabarrus.svg) / [current](maps/2026-08-24/cabarrus.svg) |
| Gaston | 37071 | 36 | 46 (0) | 40 (0) | [2024](maps/2024-07-23/gaston.svg) / [current](maps/2026-08-24/gaston.svg) |
| Iredell | 37097 | 49 | 30 (0) | 30 (0) | [2024](maps/2024-07-23/iredell.svg) / [current](maps/2026-08-24/iredell.svg) |
| Brunswick | 37019 | 10 | 27 (0) | 27 (0) | [2024](maps/2024-07-23/brunswick.svg) / [current](maps/2026-08-24/brunswick.svg) |
| Davidson | 37057 | 29 | 43 (0) | 43 (0) | [2024](maps/2024-07-23/davidson.svg) / [current](maps/2026-08-24/davidson.svg) |
| Alamance | 37001 | 1 | 39 (0) | 39 (0) | [2024](maps/2024-07-23/alamance.svg) / [current](maps/2026-08-24/alamance.svg) |
| Orange | 37135 | 68 | 40 (0) | 40 (0) | [2024](maps/2024-07-23/orange.svg) / [current](maps/2026-08-24/orange.svg) |
| Pitt | 37147 | 74 | 40 (0) | 40 (0) | [2024](maps/2024-07-23/pitt.svg) / [current](maps/2026-08-24/pitt.svg) |
| Catawba | 37035 | 18 | 40 (0) | 40 (0) | [2024](maps/2024-07-23/catawba.svg) / [current](maps/2026-08-24/catawba.svg) |
| Onslow | 37133 | 67 | 24 (0) | 24 (0) | [2024](maps/2024-07-23/onslow.svg) / [current](maps/2026-08-24/onslow.svg) |
| Randolph | 37151 | 76 | 22 (0) | 22 (0) | [2024](maps/2024-07-23/randolph.svg) / [current](maps/2026-08-24/randolph.svg) |
| Rowan | 37159 | 80 | 41 (0) | 41 (0) | [2024](maps/2024-07-23/rowan.svg) / [current](maps/2026-08-24/rowan.svg) |
| Henderson | 37089 | 45 | 34 (0) | 34 (0) | [2024](maps/2024-07-23/henderson.svg) / [current](maps/2026-08-24/henderson.svg) |
| Harnett | 37085 | 43 | 13 (0) | 15 (0) | [2024](maps/2024-07-23/harnett.svg) / [current](maps/2026-08-24/harnett.svg) |
| Moore | 37125 | 63 | 26 (0) | 26 (0) | [2024](maps/2024-07-23/moore.svg) / [current](maps/2026-08-24/moore.svg) |
| Craven | 37049 | 25 | 21 (0) | 21 (0) | [2024](maps/2024-07-23/craven.svg) / [current](maps/2026-08-24/craven.svg) |
| Lincoln | 37109 | 55 | 23 (0) | 23 (0) | [2024](maps/2024-07-23/lincoln.svg) / [current](maps/2026-08-24/lincoln.svg) |
| Wayne | 37191 | 96 | 28 (0) | 28 (0) | [2024](maps/2024-07-23/wayne.svg) / [current](maps/2026-08-24/wayne.svg) |
| Nash | 37127 | 64 | 24 (0) | 24 (0) | [2024](maps/2024-07-23/nash.svg) / [current](maps/2026-08-24/nash.svg) |
| Chatham | 37037 | 19 | 18 (0) | 18 (0) | [2024](maps/2024-07-23/chatham.svg) / [current](maps/2026-08-24/chatham.svg) |
| Cleveland | 37045 | 23 | 21 (0) | 21 (0) | [2024](maps/2024-07-23/cleveland.svg) / [current](maps/2026-08-24/cleveland.svg) |
| Rockingham | 37157 | 79 | 15 (0) | 14 (0) | [2024](maps/2024-07-23/rockingham.svg) / [current](maps/2026-08-24/rockingham.svg) |
| Robeson | 37155 | 78 | 39 (0) | 39 (0) | [2024](maps/2024-07-23/robeson.svg) / [current](maps/2026-08-24/robeson.svg) |
| Burke | 37023 | 12 | 31 (0) | 31 (0) | [2024](maps/2024-07-23/burke.svg) / [current](maps/2026-08-24/burke.svg) |
| Carteret | 37031 | 16 | 26 (0) | 26 (0) | [2024](maps/2024-07-23/carteret.svg) / [current](maps/2026-08-24/carteret.svg) |
| Caldwell | 37027 | 14 | 15 (0) | 15 (0) | [2024](maps/2024-07-23/caldwell.svg) / [current](maps/2026-08-24/caldwell.svg) |
| Franklin | 37069 | 35 | 18 (0) | 18 (0) | [2024](maps/2024-07-23/franklin.svg) / [current](maps/2026-08-24/franklin.svg) |
| Wilson | 37195 | 98 | 24 (0) | 24 (0) | [2024](maps/2024-07-23/wilson.svg) / [current](maps/2026-08-24/wilson.svg) |

The [asset manifest](maps/manifest.csv) records all 152 county assets, original source URL, official owner, source vintage, retrieval time, FIPS, native county ID, CRS, counts, bounds, byte sizes and SHA-256. The [100-county inventory](maps/county-inventory.csv) includes both statewide map counts and historical geographic/administrative result-unit counts for every county; counties outside the deep set are explicitly identified. Neither feature counts nor county coverage establishes the share of land or future votes mapped.

## CRS, precision and identifiers

Both downloaded shapefile `.prj` files identify **EPSG:2264, NAD83 / North Carolina (US survey feet)**. The NC OneMap REST service separately advertises **EPSG:32119, NAD83 / North Carolina (metres)**; its source XML describes feet. These representations must not be assigned the same units merely because their attributes resemble each other. The exported county GeoJSONs use **WGS84 longitude, latitude / OGC:CRS84**, without a legacy GeoJSON CRS object.

The exact PROJ pipeline and software versions are recorded in `checks.json`. The available operation uses the NAD83-to-WGS84 transformation with stated **4 m accuracy**. Preferred regional grid transformations were unavailable in this environment, and their names/warning are retained. No extra decimal rounding is applied to GeoJSON, but numerical precision does not imply survey accuracy. **Every source vertex is retained in the GeoJSON conversion.** Native shapefile coordinates, properties, encoding and sidecars remain unchanged in the ZIPs. Source ring ordering is carried through; no topology repair is applied.

SVGs are separate research previews: longitude is scaled by the cosine of county-midpoint latitude, latitude is reversed for display, and each county is fitted independently. SVG geometry is explicitly simplified at **0.00002 degrees** with topology preservation, then display positions are rounded to 0.01 viewBox units. This affects previews only. They have no basemap or measurement CRS. Two raster checks are retained for [Wake current](maps/previews/wake-current.png) and [Union historical](maps/previews/union-historical.png).

| Field | Meaning and handling | Inspected examples |
| --- | --- | --- |
| `county_id` | Native NCSBE county code, joined exactly to the turnout CSV; not a FIPS suffix | Wake `92` → FIPS `37183`; Mecklenburg `60` → `37119` |
| `county_nam` | Native uppercase county name | `NEW HANOVER`, `GUILFORD` |
| `prec_id` | Geographic precinct code; preserve string formatting and leading zeroes | Wake `01-05`; Mecklenburg `001`; Guilford `CG3A`; Buncombe `01.1`; Cumberland `AL51-1` |
| `id` | Original source numeric record ID; retained but not assumed stable across versions | Wake `01-05` has source `id=105` |
| `enr_desc` | Source label, sometimes a polling location and sometimes an ID | Durham `01`: `BROGDEN MIDDLE SCHOOL`; Union current `0020B`: `0020B` |
| `of_prec_id` | Preserve source value; not by itself an election-approved crosswalk | Mostly blank; Buncombe `prec_id=681` carries `of_prec_id=68.1` in both snapshots |
| `Shape_Area`, `Shape_Leng` | Retained source attributes; not recomputed during conversion | Current first-record ratios to native computed area/length are about `0.092926` and `0.304838`, rather than 1; their units are not established by the field names |
| `_county_fips`, `_source_row`, `_snapshot` | Explicit export enrichment; source properties retain their original names | `_source_row` is the one-based shapefile row, allowing direct lookup in the ZIP |

GeoJSON feature `id` combines FIPS and native `prec_id`, e.g. `37183:01-05`. Join using **county plus election-specific native unit ID**, never a short precinct number alone. GeoJSON county files are ordered by native `prec_id`, so use `_source_row` to recover original archive order. Source area/length fields must not be used for allocation or measurement without resolving their provenance and units; recompute from a documented projected geometry when needed.

## Geometry diagnostics and changes

[geometry-diagnostics.json](maps/geometry-diagnostics.json) records topology reasons and pairwise overlap findings. There are **zero empty selected geometries**, **one invalid 2024 geometry**, and **zero invalid current geometries**. The historical defect is **Union `045`, source id 3030, source row 2602**, a ring self-intersection near **(-80.72012016, 34.96801408)**. It remains in the historical export. The current state geometry for the renamed `0045` is valid, but that does not authorize replacing historical geometry with it.

Valid individual polygons can still overlap. Intersections of valid polygon pairs greater than **1 m²** yield **50 pairs in 2024** and **75 pairs in the current snapshot**. Sum of pair-intersection areas is approximately **3,196,147 m²** and **76,606 m²**, respectively; these are diagnostic pair sums, not unique land-area measurements. Historical Durham accounts for about 3,141,932 m²; current Gaston still has four pairs totaling about 43,149 m². Invalid polygons are excluded from overlap calculations and explicitly counted. Very small overlaps, independent legal county-outline agreement and gaps are untested. No source geometry was altered to make these checks pass.

[vintage-id-comparison.json](maps/vintage-id-comparison.json) records added, removed and shared IDs for **all 100 counties**. Ten priority counties have changed ID sets: Wake, Durham, Union, Johnston, Cabarrus, Gaston, Harnett, Chatham, Cleveland and Rockingham. Examples include Wake's 210→216 features, Durham 60→58, Gaston 46→40 and Harnett 13→15. Union has the same count but changes `020B/044/045` to `0020B/0044/0045`. Same counts or shared IDs do not establish unchanged boundaries. These diagnostics are **not a many-to-many geographic or election crosswalk**; no votes are allocated.

## Results units without matching polygons; attempted alternatives

The read-only result-label comparison uses the **Election Results ZIPs**, contest group **1393 (2024 president)** and **1378 (2022 Senate)** already downloaded by turnout. It does not use NCSBE's separate, statistically noised Precinct Sorted files. [result-unit-diagnostics.csv](maps/result-unit-diagnostics.csv) retains every county/unit literal, real-precinct flag, election/contest, FIPS and literal matches to both map snapshots. The underlying ZIP hashes are recorded as dependencies. These label checks do not override the certified county vote baseline or resolve its documented ZIP discrepancies.

Statewide 2024 president contains **2,658 `Y` geographic result labels and 250 `N` administrative labels**; the 38 counties contain **1,835 and 115**, respectively. For 2022 Senate the statewide counts are **2,655 / 322**, and the priority counts **1,826 / 176**. Administrative examples include Wake `ABSEN`, `EVAB`, `EVBOE`, `PROVI`, `TRANS`; Mecklenburg `ABSENTEE BY MAIL`, `PROVISIONAL`, `TRANSFER`; Guilford `ABSENTEE`, `EARLYVOTE`; and Johnston `EV-ARCHER LODGE`, `ABS-SUPPLEMENTAL`. They are not automatically separate geographic precincts. Their full literal labels are retained; no polygons are invented for them and no votes are replicated across polygons.

Six priority-county `Y` result labels have no literal match in the historical map:

| County / result labels | Inspected alternative and finding | Remaining gap |
| --- | --- | --- |
| Wake: `01-07A`, `07-07A` | [Official July 20, 2021 board minutes](https://s3.us-west-2.amazonaws.com/wakegov.com.if-us-west-2/prod/documents/2021-08/07-20-21%20Board%20Meeting%20Minutes.pdf), [saved PDF](maps/raw/wake-2021-07-20-minutes.pdf), state that the county board approved resolutions for these satellite precincts. The [Wake County Open Data precinct page](https://data.wake.gov/datasets/Wake%3A%3Aprecincts/explore?location=35.797171%2C-78.623247%2C8) identifies the `WakeCountyGovernment` item, credited to Wake County GIS. Its linked [county service](https://services1.arcgis.com/a7CWfuGP5ZnLYE7I/arcgis/rest/services/Precincts/FeatureServer/0) returns 216 precinct attributes and neither satellite code; count and object IDs also equal 216. | Neither state snapshot nor inspected county layer supplies separate polygons for the two labels. Historical satellite evidence is not November 2026 approval or a geometric allocation. |
| Union: `0020B`, `0044`, `0045` | These exact strings exist in the current state archive. The [county elections precinct-map page](https://unioncountyncelections.gov/voting/precinct-maps) labels 20B, 44 and 45. The [official county GIS layer 210](https://gis.unioncountync.gov/server/rest/services/OperationalLayers/MapServer/210) has 54 records but retains `020B`, `044`, `045`, with descriptions Waxhaw Bible Church, Millbridge Clubhouse and New Town Elementary School. Count/ID queries reconcile to all 54 attributes. A [retained three-feature county GeoJSON response](maps/raw/union-alias-alternative.geojson.gz) uses observed object IDs 52, 54 and 50; all three exported geometries are valid, including `045`. | This provides a usable official alternative for the historical defect and supporting alias evidence, but its election-effective vintage and geometric equivalence to the historical/state files remain unverified. It is not merged into either main export or treated as an approved crosswalk. |
| Henderson: `CV` | The [official Carolina Village page](https://www.hendersoncountync.gov/elections/page/carolina-village-cv) confirms the named site. The [August 19, 2025 board packet](https://www.hendersoncountync.gov/sites/default/files/fileattachments/elections/page/135561/8-19-25_board_minutes.pdf), [saved PDF](maps/raw/henderson-2025-08-19-minutes.pdf), page 9, describes Carolina Village as a satellite site within Hendersonville 2 and requests its continuation through the 2026 general elections. The [rendered resolution](maps/previews/henderson-satellite-resolution.png) visibly has the county chair's dated signature and a **blank state executive director approval line**. | No separate `CV` polygon is present in either state snapshot. The packet supports the site's relationship to Hendersonville 2 and county action; it does not establish completed state approval or an election-specific vote crosswalk. |

The county Wake layer's maximum feature edit timestamp is **2025-07-30 23:18:02 UTC**; the catalog item was modified later. These timestamps do not prove election effectiveness. The [Henderson maps/data page](https://www.hendersoncountync.gov/elections/page/maps-data) was also inspected but yielded links to precinct lists/results rather than a downloadable separate `CV` boundary. [Mecklenburg's official data page](https://vote.mecknc.gov/Data) and [map page](https://vote.mecknc.gov/Maps) provide additional county routes; their presence does not certify the state archive's November boundary approval. All inspected alternatives' bytes and metadata are retained. No Census VTD was substituted for a current precinct.

Conversely, four historical priority map IDs have no literal `Y` result-unit match: Durham `48` and Union `020B`, `044`, `045`. Missing result rows are not assigned zero votes. The Union naming evidence explains a likely ID relationship, but exact crosswalk acceptance remains a separate review. Counts alone cannot distinguish an alias, a satellite, an unused result row, a split, a merger or a boundary change.

## Reproduction and validation

From repository root, with Python 3 and the versions in [requirements.txt](maps/requirements.txt) installed:

```sh
# Optional local dependency installation; all explicit installation writes stay in maps/.
python3 -m pip install --no-cache-dir --target senate/2026/north-carolina/maps/.runtime -r senate/2026/north-carolina/maps/requirements.txt

# Offline source verification, full-precision export, SVGs, inventory and diagnostics.
python3 senate/2026/north-carolina/maps/build_maps.py

# Optional retained PNG/text checks; requires Poppler and librsvg.
python3 senate/2026/north-carolina/maps/render_evidence.py

# Supplemental measurement/alternative-source observations.
python3 senate/2026/north-carolina/maps/inspect_sources.py

# Independent standard-library audit; no GIS dependencies or network required.
python3 senate/2026/north-carolina/maps/audit_maps.py
```

[fetch_evidence.py](maps/fetch_evidence.py) optionally refreshes the observed public URLs and their metadata. Preserve this snapshot first: upstream objects and dates can change. The offline build verifies source-byte hashes before parsing; it checks every county/native code, all source and exported vertex counts, ring closure, finite coordinates, geographic bounds, unique IDs and count coverage. Shapely/GEOS validity and pairwise overlap checks leave geometry intact. All writes by these scripts stay under `maps/`; turnout and baseline inputs are read only.

The independent audit checks original HTTP evidence hashes, archive member CRCs/hashes and DBF/SHX record counts, listing completeness, all 100 county identities and statewide arithmetic, all 152 derived-asset hashes, 76 GeoJSON bounds/coordinate/ring/ID checks, state and alternative-county service pagination, historical result-unit uniqueness, local report/index links and the **40,000,000-byte per-file ceiling**. [validation.json](maps/validation.json) records the completed audit; [artifact-manifest.json](maps/artifact-manifest.json) inventories retained files and hashes; [preview-provenance.json](maps/preview-provenance.json) records PDF/SVG rendering commands and input/output hashes. [source-inspection.json](maps/source-inspection.json) retains supplemental measurement examples, alternative geometry validity and manual PDF observations. Representative PNGs and both relevant resolution/minutes pages were visually inspected.

Material open items are **November 2026 approved precinct and reporting-unit rosters; a reviewed 2024→2026 geographic/administrative crosswalk; historical legal-boundary confirmation; source overlap/invalid-geometry review; and separate satellite boundaries or supported aggregate treatment**. County download coverage is complete for both selected published snapshots. This assignment supplies no live publication cadence, current remaining-vote counts, vote allocation or calibrated model. Integration and publication remain with the coordinator; no Git command was run.

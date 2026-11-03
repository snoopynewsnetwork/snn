# Oklahoma precinct maps: 26-county priority set

Research retrieval: **2026-10-18, 17:16:20–17:17:55 UTC** (205 requests, all HTTP 200). **All 26 accepted priority counties have downloaded polygon assets for both the 2024 baseline and the current published geography.** No county is missing. **Approval of these units for the November 3, 2026 count is not established for any county.**

The 26 counties are the exact 25-county 2024-president minimum 80% set from [turnout.md](turnout.md), plus Kay, which belongs to the 80% set of the 2022 special Senate, 2022 regular Senate and 2020 Senate contests. Open the [offline map index](maps/index.html) for county previews. The machine-readable index is [index.csv](maps/index.csv) / [index.json](maps/index.json). The [asset manifest](maps/manifest.csv) lists every owned file with its role, source, vintage, CRS, feature count, SHA-256 and size.

## Bottom line

- **The official source is a statewide layer from the State Election Board's mapping contractor.** The OSEB [District and Precinct Maps page](https://oklahoma.gov/elections/candidates/district-and-precinct-maps.html) says the Board "contracts with the OU Center for Spatial Analysis (CSA) for mapping services" and that GIS maps are downloaded from the [CSA Data Warehouse](https://csagis-uok.opendata.arcgis.com/). There, the hosted layer **"Voter Precincts 2020"** ([item](https://www.arcgis.com/home/item.html?id=8c2c841e2eb54007bd1872c4274d6e07), [layer](https://services.arcgis.com/3xOwF6p0r7IHIjfn/arcgis/rest/services/State_Wide_2020_Precincts/FeatureServer/0)) holds **1,984 precinct polygons** for all 77 counties. Its credits read "Center for Spatial Analysis; Oklahoma State Election Board". Each polygon carries the six-digit OSEB precinct ID `PCT_CEB` (2-digit OSEB county code + 4 digits).
- **The current layer was last edited after the 2024 election.** Its `dataLastEditDate` is **2025-11-05 18:25:45 UTC**, but the item text still says "Last Updated: 06/07/2022". This report labels it **current published geography**: the latest official edit retrieved, not proof of November 2026 approval.
- **The 2024 baseline is a January 2025 copy of the same CSA file.** INCOG (Indian Nations Council of Governments) mirrors it as [PCT_OK_State](https://map11.incog.org/arcgis11wa/rest/services/PCT_OK_State/MapServer). The service text says "File was downloaded from CSA January 2025. Boundaries last updated 2024." Its 1,984 IDs equal the 1,984 geographic precinct IDs in the 2024 OKER results exactly, statewide. It is a government mirror, not the authority's own frozen snapshot, so it is labeled the **2024 baseline mirror**.
- **Current vs 2024: 24 of 26 priority counties are unchanged.** Their IDs match 100% in both directions, and every precinct's geometry is identical: zero symmetric-difference area and zero Hausdorff distance in EPSG:5070. Two counties changed after the 2024 election:
  - **Wagoner (40145)** split two precincts. 730104 became 730104 + **730105**, and 730206 became 730206 + **730211**.
  - **McClain (40087)** merged **440026** into 440010.
  - The pieces conserve area to 0.1 m². See the [area crosswalk](maps/geometry-crosswalk.csv).
- **Two reporting units have no polygon.** 559999 (Oklahoma County) and 729999 (Tulsa County) hold all of each county's absentee-mail and early votes ([reporting-units.json](data/turnout/reporting-units.json)). The geographic precincts there carry Election Day votes only. These two units held **22.7%** of Oklahoma County's and **17.2%** of Tulsa County's 2024 president votes.

## Three geography vintages

| Role | Layer (stored as) | Publisher / provenance | Vintage evidence | Native CRS → stored | Features (state / 26 counties) |
| --- | --- | --- | --- | --- | ---: |
| **Current published** (not a 2026 approval) | CSA `pct_2020`: [REST pages](maps/raw/csa2020/), [Hub shapefile ZIP](maps/raw/csa2020/hub-download-shapefile.zip) | CSA with OSEB (item credits); linked from the OSEB page | `dataLastEditDate` 2025-11-05T18:25:45Z. Hub export `Last-Modified` 2026-06-18. Item text "Last Updated: 06/07/2022" | EPSG:4269 → EPSG:4269 | 1,984 / 1,374 |
| **2024 baseline** | INCOG `PCT_OK_State` [REST pages](maps/raw/incog-state/) | INCOG mirror of the CSA/OSEB file | "File was downloaded from CSA January 2025. Boundaries last updated 2024." IDs = 2024 OKER | EPSG:2267 (ArcGIS 102724, ftUS) → server `outSR=4269` | 1,984 / 1,373 |
| **2020 context** (pre-2022 reprecincting) | CSA `PCT_2010` ([attributes](maps/raw/csa2010/statewide-attributes/) for all counties, [geometry](maps/raw/csa2010/priority-geometry/) for the 26) | CSA | `dataLastEditDate` 2025-11-05 is a republish time, not a boundary date. IDs = 2020 OKER (1,948) | EPSG:4269 → EPSG:4269 | 1,948 / 1,296 |

**The 2022 baseline has no separate layer.** Precincts were redrawn after the 2020 census: only 1,389 of the 1,948 IDs used in 2020 recur in 2022, and the INCOG Tulsa layer says its boundaries "were redrawn based upon the 2020 legislative and county commissioner district boundaries". Between the 2022 and 2024 elections the statewide roster changed by five removed IDs and five added IDs ([geometry-audit.json](maps/geometry-audit.json) `statewide_reconciliation`). In the priority counties:
- **Removed after 2022:** Washington **740031** (710 votes in the 2022 special Senate) and McClain **440007** (315 votes). Neither has a polygon in any retained layer.
- **Added in 2024:** Garfield **240312**, and Wagoner **730110** and **730210**.

**IDs are reused across plans.** For example, 730105 and 730210 both existed in the 2020-era plan, and their 2020-era polygons differ from the current ones (symmetric difference larger than either polygon). Never join across vintages on the precinct number alone.

## Per-county index

"2024 IDs" is matched / 2024 OKER geographic precincts (excluding 559999/729999). "Current→2024" is the share of current polygons whose ID appears in the 2024 results. "2022 IDs" compares the current layer with the 2022 special-Senate export. Each county's GeoJSON files are listed in [index.csv](maps/index.csv).

| # | County | FIPS | OSEB | Current polygons | 2024 baseline | 2024 IDs in current | Current→2024 | 2022 IDs in current | Non-geographic unit | Change since 2024 | Preview |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| 1 | Oklahoma | 40109 | 55 | 290 | 290 | 290/290 (100%) | 100% | 100% | 559999 | none | [png](maps/previews/40109-oklahoma.png) |
| 2 | Tulsa | 40143 | 72 | 251 | 251 | 251/251 (100%) | 100% | 100% | 729999 | none | [png](maps/previews/40143-tulsa.png) |
| 3 | Cleveland | 40027 | 14 | 105 | 105 | 105/105 (100%) | 100% | 100% | — | none | [png](maps/previews/40027-cleveland.png) |
| 4 | Canadian | 40017 | 09 | 60 | 60 | 60/60 (100%) | 100% | 100% | — | none | [png](maps/previews/40017-canadian.png) |
| 5 | Rogers | 40131 | 66 | 38 | 38 | 38/38 (100%) | 100% | 100% | — | none | [png](maps/previews/40131-rogers.png) |
| 6 | **Wagoner** | 40145 | 73 | **31** | 29 | 29/29 (100%) | **93.55%** | 100% | — | **+730105, +730211; 730104 and 730206 reshaped** | [png](maps/previews/40145-wagoner.png) |
| 7 | Comanche | 40031 | 16 | 40 | 40 | 40/40 (100%) | 100% | 100% | — | none | [png](maps/previews/40031-comanche.png) |
| 8 | Creek | 40037 | 19 | 35 | 35 | 35/35 (100%) | 100% | 100% | — | none | [png](maps/previews/40037-creek.png) |
| 9 | Payne | 40119 | 60 | 30 | 30 | 30/30 (100%) | 100% | 100% | — | none | [png](maps/previews/40119-payne.png) |
| 10 | Pottawatomie | 40125 | 63 | 31 | 31 | 31/31 (100%) | 100% | 100% | — | none (PDFs re-issued 2025) | [png](maps/previews/40125-pottawatomie.png) |
| 11 | Grady | 40051 | 26 | 28 | 28 | 28/28 (100%) | 100% | 100% | — | none | [png](maps/previews/40051-grady.png) |
| 12 | Muskogee | 40101 | 51 | 39 | 39 | 39/39 (100%) | 100% | 100% | — | none | [png](maps/previews/40101-muskogee.png) |
| 13 | Logan | 40083 | 42 | 30 | 30 | 30/30 (100%) | 100% | 100% | — | none | [png](maps/previews/40083-logan.png) |
| 14 | Washington | 40147 | 74 | 26 | 26 | 26/26 (100%) | 100% | 96.30% (740031 gone) | — | none | [png](maps/previews/40147-washington.png) |
| 15 | Garfield | 40047 | 24 | 29 | 29 | 29/29 (100%) | 100% | 100% | — | none | [png](maps/previews/40047-garfield.png) |
| 16 | **McClain** | 40087 | 44 | **25** | 26 | **25/26 (96.15%)** | 100% | 92.59% (440007, 440026 gone) | — | **440026 merged into 440010** | [png](maps/previews/40087-mcclain.png) |
| 17 | Osage | 40113 | 57 | 28 | 28 | 28/28 (100%) | 100% | 100% | — | none | [png](maps/previews/40113-osage.png) |
| 18 | Carter | 40019 | 10 | 28 | 28 | 28/28 (100%) | 100% | 100% | — | none | [png](maps/previews/40019-carter.png) |
| 19 | Le Flore | 40079 | 40 | 37 | 37 | 37/37 (100%) | 100% | 100% | — | none (one PDF re-issued 2025) | [png](maps/previews/40079-le-flore.png) |
| 20 | Stephens | 40137 | 69 | 28 | 28 | 28/28 (100%) | 100% | 100% | — | none | [png](maps/previews/40137-stephens.png) |
| 21 | Delaware | 40041 | 21 | 18 | 18 | 18/18 (100%) | 100% | 100% | — | none | [png](maps/previews/40041-delaware.png) |
| 22 | Cherokee | 40021 | 11 | 29 | 29 | 29/29 (100%) | 100% | 100% | — | none | [png](maps/previews/40021-cherokee.png) |
| 23 | Bryan | 40013 | 07 | 25 | 25 | 25/25 (100%) | 100% | 100% | — | none | [png](maps/previews/40013-bryan.png) |
| 24 | Pittsburg | 40121 | 61 | 38 | 38 | 38/38 (100%) | 100% | 100% | — | none | [png](maps/previews/40121-pittsburg.png) |
| 25 | Mayes | 40097 | 49 | 25 | 25 | 25/25 (100%) | 100% | 100% | — | none | [png](maps/previews/40097-mayes.png) |
| 26 | Kay | 40071 | 36 | 30 | 30 | 30/30 (100%) | 100% | 100% | — | none | [png](maps/previews/40071-kay.png) |
| | **Total** | | | **1,374** | **1,373** | **1,372/1,373** | | | 2 units | | [statewide](maps/previews/statewide-priority.png) |

The 2024 baseline mirror matches the 2024 results 100% in every county. The 2020-context layer matches the 2020 OKER export 100% statewide (1,948/1,948) and in every priority county. Per county × layer × election rows, including vote-weighted polygon coverage, are in [id-reconciliation.csv](maps/id-reconciliation.csv). Every ID across every roster, with 2024/2022/2020 votes, is in [precinct-roster.csv](maps/precinct-roster.csv).

**Vote-weighted coverage of the 2024 president vote by current polygons:**
- Oklahoma County: 77.30% (559999 has no polygon).
- Tulsa County: 82.83% (729999 has no polygon).
- McClain: 98.85% (the 247 votes cast in 440026 now fall inside 440010).
- All other priority counties: 100%.

**Zero-vote precincts.** Nine geographic precincts have polygons but zero 2024 president votes: Oklahoma 550001, 550002, 550409, 550412 and 550518; Canadian 090299; Pottawatomie 630039; Cherokee 110030 and 110031. CSA publishes no individual map PDF for 550001 or 550002.

## What changed after the 2024 election

| County | 2024 unit (votes, 2024 president) | Current units | Area evidence |
| --- | --- | --- | --- |
| Wagoner | 730104 (2,004) | 730104 + 730105 | 730104 keeps 30.78% of its 2024 area; 730105 is the other 69.22% |
| Wagoner | 730206 (1,894) | 730206 + 730211 | 70.69% / 29.31% |
| McClain | 440010 (321) + 440026 (247) | 440010 | 2024 areas form 60.76% / 39.24% of current 440010 |

These are **area-only** overlaps of polygons. They are not vote allocations. Use them only for a two-level comparison, such as current 730104 + 730105 against 2024 730104, until address-based or official weights exist. The [change ledger](maps/geometry-changes.csv) lists every compared precinct. A change counts only if it exceeds both 100 m² and 0.01% of the precinct's area; every other compared precinct had exactly zero difference. Previews colour changed polygons, new IDs and removed 2024 polygons.

**The CSA PDF catalogue corroborates the timing.** Wagoner's county-wide map and all 30 individual maps were re-issued 2025-11-07. The individual map for new precinct 211 was created that day and its footer reads "November, 2025". McClain's county-wide map and four individual maps (440003, 440005, 440010, 440022) say "April, 2025".

**One Wagoner date conflict is not resolved.** The re-issued Wagoner county-wide PDF still prints "Map Produced By … November, 2023", yet it labels precincts 105 and 211, which are absent from the 2024 results ([visual review in pdf-audit.json](maps/pdf-audit.json)).

**Some PDF re-issues have no matching GIS change.** Pottawatomie's county-wide map ("August, 2025") and two individual maps were re-issued: 630011 says "March, 2025", while 630041 still says "February, 2022". Le Flore's map book and its individual map 400109 ("February, 2025") were also re-issued. None of these counties shows any ID or geometry change in the GIS layer. No cause is inferred.

## Approved November 2026 reporting units: not established

- **Precinct changes are still allowed by law.** [26 O.S. § 3-118](maps/raw/statute/os26.pdf) (official compiled Title 26, PDF p. 41–42, file `Last-Modified` 2025-12-31) lets the county election board secretary change, abolish or consolidate precincts. Changes are barred only between January 1 of a year ending in 9 and December 31 of a year ending in 0. A change takes effect after notices have been posted and mailed for 30 days. So changes were legal throughout 2025–2026, and an edit after 2025-11-05 would not necessarily appear in the layer retrieved here.
- **No public roster of November 2026 reporting units was found.** OSEB's June 2026 primary results page links only to OKER. The 2026 primary (June 16) and runoff (August 25) precinct exports would show the units in use this year, but they sit behind the app's sign-in, which this assignment does not use. They were not checked.
- **Rows that miss the current layer must stay unmatched.** Until the November 2026 roster is seen, reconcile each 2026 results row to the **current** layer by full six-digit ID. Hold unmatched rows at county level. Keep 559999 and 729999 as non-geographic units.

## Checks and results

[checks.json](maps/checks.json) records 275 build checks, all passing. [validation.json](maps/validation.json) re-checks the package independently with the standard library only (648 checks, all passing).

- **Enumeration and pagination.** Every ArcGIS layer was enumerated with `returnIdsOnly` and fetched in object-ID batches of at most 250. Each layer's maxRecordCount is 2,000. Count = IDs = features for every layer: CSA 2020 1,984; INCOG 1,984; CSA 2010 1,948 attributes and 1,296 priority geometries; INCOG Tulsa 251; McClain 911 27. No page set `exceededTransferLimit`. A `resultOffset` probe returned 1,984 rows at offset 0 and 0 rows at offset 1,984.
- **Hub shapefile = REST layer.** The Hub shapefile download (`pct_2020.zip`, 10,830,200 bytes, ZIP CRCs pass, `.prj` GCS North American 1983) has the same 1,984 `PCT_CEB` IDs as the REST layer. All 20 shared attribute fields are equal. Geometry Hausdorff distance after normalisation is 0.0 degrees.
- **Identifiers.**
  - No duplicate, malformed or empty IDs in the three main layers.
  - Each ID's county prefix equals `COUNTY`.
  - `CO_FIPS` = 2 × OSEB code − 1 for all features.
  - The priority list equals [county-turnout.csv](data/county-turnout.csv) order plus Kay.
  - The read-only inputs are pinned by SHA-256 in [read-only-pins.json](maps/read-only-pins.json): the OKER precinct ZIPs, county CSV, priority contract, reporting-unit ledger and turnout manifest.
- **Geometry** (GEOS 3.11.4 / Shapely 2.0.6; areas in EPSG:5070). Originals are never repaired or simplified.
  - All geometries are Polygon/MultiPolygon with closed, finite rings.
  - The current layer has **0 invalid geometries** statewide.
  - The 2024 mirror has 2 ring self-intersections, in Kay **360403** and **360406**. They are absent from the current layer, and the area difference after `make_valid` is zero.
  - The 2020-context layer has one invalid geometry (Oklahoma 550100).
  - Overlaps and gaps within counties are reported in [geometry-audit.json](maps/geometry-audit.json), identically in the current and 2024 layers:
    - **Wagoner:** 7 overlap pairs of 1,103–6,259 m², and 55 interior gaps totalling 21,531 m² (largest 5,909 m²).
    - **Garfield:** 2 overlaps (9,064 and 1,138 m²) and 1 gap of 2,317 m².
    - **Payne:** 3 overlaps of up to 47 m², and 2 gaps totalling 28 m².
    - **Le Flore:** 3 gaps totalling 35,005 m² (one of 34,992 m²).
    - **Carter:** one 1.4 m² overlap.
  - Every county's polygons union to one part. Sliver residuals of 1 m² or less are only counted.
- **Hashes and sizes.**
  - [source-manifest.json](maps/source-manifest.json) records, for every request: URL, final URL, redirect chain, status, selected headers, UTC times, and SHA-256 and size both as received and as stored.
  - Text is stored gzip-9 with mtime 0. ZIP and PDF files are stored as received.
  - Every file is under 40 MB. The largest is the 10.8 MB shapefile ZIP, and the package totals about 80 MB.

## Official PDFs (catalogue and bounded downloads)

The CSA Hub publishes three PDF forms per county: a county-wide map, a multi-page map book and individual precinct maps. [pdf-inventory.csv](maps/pdf-inventory.csv) records all 1,455 PDF items for the 26 counties with created/modified times and HEAD sizes: 26 county-wide maps, 26 map books, 32 older unlinked map books and 1,371 individual maps. The 84 county-wide maps and map books (including the 32 unlinked older map books) total about 1.3 GB, among them a 115 MB Osage county-wide map, so they were **inventoried, not downloaded**.

Downloaded were the 3 county-wide maps and 8 individual maps that CSA modified after the 2024 general election:
- **County-wide:** Wagoner, Pottawatomie and McClain.
- **Individual:** Wagoner 730211; Pottawatomie 630011 and 630041; McClain 440003, 440005, 440010 and 440022; Le Flore 400109.

Each has a page-1 [preview](maps/previews/pdf/) and printed-date extraction in [pdf-audit.json](maps/pdf-audit.json). The two Wagoner PDFs have no text layer and were read visually. The individual-map rosters match the current layer in every priority county except:
- Oklahoma has no maps for 550001 or 550002.
- Wagoner has no map for 730105.

## Alternatives (clearly labeled, not current precinct authority)

- **Tulsa County, INCOG `PCT_TulsaCo`.** Labeled "Data layer acquired from the Center for Spatial Analysis, April 2022". Its 251 IDs are derived as `72` + zero-padded `PCT`; this is a derived key. They equal Tulsa's 2024 IDs, and all 251 geometries match the current layer within tolerance. This independently corroborates Tulsa.
- **McClain County 911 `VotingPrecincts`.** 27 features. The only edit dates it carries are 2016–2018 (20 of 27 are blank). It has two blank IDs, a duplicate 440016 and 4 invalid geometries. It lacks 440022, 440023, 440027 and 440028, and its shapes differ from the current layer. It is a **stale county-agency copy**, retained only as raw evidence.
- **Not used:** Census 2020 VTDs and VEST/RDH precinct files. An official statewide layer matching the 2024 results exactly made these third-party or historical substitutes unnecessary. They are not current precincts.

## Gaps

1. **November 2026 approval is unverified for all 26 counties.** No public 2026 reporting-unit roster was found, and OKER 2026 exports were not accessed (sign-in). Edits after 2025-11-05 cannot be ruled out.
2. **No 2022-vintage polygons exist for Washington 740031 or McClain 440007.** They were 2022 units removed before 2024. No authority-published 2022 snapshot was found.
3. **The 2024 baseline is a mirror.** The INCOG copy is a government mirror taken in January 2025, not a CSA/OSEB snapshot frozen on election day. Its exact ID match to the 2024 results is the supporting evidence.
4. **Topology defects are retained, not repaired:** Wagoner, Garfield, Payne, Le Flore and Carter (above). The two Kay self-intersections in the mirror are also retained.
5. **One PDF date conflict is unresolved.** The Wagoner county-wide PDF prints a November 2023 date but shows post-2024 precincts.
6. **Most CSA county PDFs were not downloaded** because of size; their metadata and sizes are recorded.

## Files and reproduction

| Path | Contents |
| --- | --- |
| [maps/counties/](maps/counties/) | Per county, three gzip GeoJSON files: `current-csa-pct2020`, `baseline2024-incog-mirror` and `historical2020-csa-pct2010`. Features are unchanged server features (EPSG:4269, lon/lat), filtered by county, with a provenance block. |
| [maps/raw/](maps/raw/) | Original responses: OSEB page, statute PDF, CSA catalogue/groups/HEADs, PDFs, layer metadata/IDs/feature pages, the Hub shapefile, the INCOG mirror and the McClain 911 layer. |
| [maps/previews/](maps/previews/) | 26 county PNGs, a statewide overview and 11 PDF page-1 renders. These are derivatives, not official maps. |
| [maps/manifest.csv](maps/manifest.csv), [maps/index.csv](maps/index.csv), [maps/index.json](maps/index.json) | Asset manifest and map index. |
| [maps/precinct-roster.csv](maps/precinct-roster.csv), [maps/id-reconciliation.csv](maps/id-reconciliation.csv), [maps/geometry-changes.csv](maps/geometry-changes.csv), [maps/geometry-crosswalk.csv](maps/geometry-crosswalk.csv) | Rosters, match rates, change ledger and area crosswalk. |
| [maps/geometry-audit.json](maps/geometry-audit.json), [maps/pdf-audit.json](maps/pdf-audit.json), [maps/checks.json](maps/checks.json), [maps/validation.json](maps/validation.json) | Audits and checks. |
| [maps/acquire.py](maps/acquire.py), [maps/build.py](maps/build.py), [maps/validate.py](maps/validate.py) | Scripts. |

Run from the repository root:

```sh
# Network refresh (replaces maps/raw and source-manifest.json; certifi only supplies a CA bundle for oklegislature.gov)
PYTHONDONTWRITEBYTECODE=1 uv run --with certifi==2024.8.30 python3 -I senate/2026/oklahoma/maps/acquire.py
# Offline build: hash-verifies inputs, writes county files, previews, tables and checks
PYTHONDONTWRITEBYTECODE=1 uv run --with shapely==2.0.6 --with pyproj==3.7.0 --with matplotlib==3.9.2 \
  --with pypdfium2==4.30.0 --with pyshp==2.3.1 python3 -I senate/2026/oklahoma/maps/build.py
# Offline validation (standard library only)
PYTHONDONTWRITEBYTECODE=1 uv run python3 -I senate/2026/oklahoma/maps/validate.py
```

Access notes:
- Every source is public. No sign-in, token or OKER API call was used.
- Requests send `User-Agent: Mozilla/5.0 (compatible; election-research/1.0)`.
- The Hub shapefile route redirects (302) to a cached `hub.arcgis.com` export.
- The OKER precinct results used for matching are the turnout worker's saved exports, read without modification.

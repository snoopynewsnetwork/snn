# Michigan precinct boundaries — research 2026-10-17

**Downloaded coverage: all 23 priority counties, separately for the 2024 baseline and the current 2026-labeled state layer.** Open [the local map index](maps/index.html) for 46 county SVG previews and 46 county-filtered GeoJSON files. The previews are generated research aids, not official published maps. The assets contain **3,220 features for 2024 and 2,789 for 2026**; these are polygon feature counts, not reporting-unit or turnout counts. See the [download manifest](maps/manifest.csv), [structural checks and ID samples](maps/checks.json), and [topology/ID comparison diagnostics](maps/topology-checks.json). Counts are calculated from the official downloads described below, retrieved 2026-10-17.

The [completed turnout research](turnout.md) and [county CSV](data/county-turnout.csv) identify these 23 as the smallest ranked set reaching 80%: **4,484,963 / 5,577,187 = 80.41622058%** of 2024 Senate candidate votes. This inherits the turnout report's county-derivative provenance limitation; no claim of polygon coverage of 80% of land or future votes is made.

## Official source and vintage evidence

All sources in this report were checked **2026-10-17**. Exact URLs, UTC retrieval times, response headers, status/errors and SHA-256 hashes are saved in [evidence-manifest.json](maps/evidence-manifest.json). All GIS request URLs, including county filters and object-ID batches, are in `maps/raw/{2024,2026}/*.retrieval.json`.

- **2024 baseline:** [official state OpenData layer 9](https://gisagocss.state.mi.us/arcgis/rest/services/OpenData/boundaries/MapServer/9) and [ArcGIS item metadata](https://www.arcgis.com/sharing/rest/content/items/02d40893317d46569017beeb14f9c63e?f=pjson), with [full dataset metadata](https://www.arcgis.com/sharing/rest/content/items/02d40893317d46569017beeb14f9c63e/info/metadata/metadata.xml). The description explicitly identifies 2024 election-cycle geography, collected from local election officials and GIS authorities, validated by most but **not all** jurisdictions. This is a 2024-cycle dataset retrieved in 2026, not a frozen election-day 2024 export. Post-election corrections cannot be ruled out; the item modification date is catalog metadata, not an election-effective date. Preserve the saved snapshot for reproducibility.
- **2026 current snapshot:** [officially credited service item](https://www.arcgis.com/sharing/rest/content/items/6a9596d0479c4770b4e943a4a82b14f1?f=pjson), [layer](https://services3.arcgis.com/dxRQUfTDNtfqZ301/arcgis/rest/services/VotingPrecincts2026_051926_gdb/FeatureServer/0), and [Election District Viewer v2 configuration](https://www.arcgis.com/sharing/rest/content/items/a36d3f1069d34ed798659d2efa2b8231/data?f=pjson). The configuration directly includes this service as “2026 Precincts.” The [viewer item](https://www.arcgis.com/sharing/rest/content/items/a36d3f1069d34ed798659d2efa2b8231?f=pjson) and both service catalog items have owner `michigan_admin`, organization `dxRQUfTDNtfqZ301`, and credits identifying Michigan Department of State, Bureau of Elections, and State of Michigan DTMB Center for Shared Solutions. This establishes provenance beyond a service name alone. The 2026 layer reports `dataLastEditDate=1789419271247`, **2026-09-14 20:54:31.247 UTC**. Its filename includes `051926`, but that filename is not evidence of an effective date. **Neither item nor layer establishes approval for November 3, 2026.** Every selected feature has `ElectionYe=2026`; that is a label, not an approval certificate.
- The [DTMB Boundaries and MGF page](https://www.michigan.gov/dtmb/services/maps/mgf-data-hub/boundaries-and-mgf) describes the state geographic framework and links the Michigan GIS Open Data Portal. Direct Python retrieval returned HTTP 403; the web reader successfully exposed its content. The ArcGIS credits and state-hosted 2024 service are the saved primary owner evidence. Both downloaded catalog items state there are no restrictions on use, reproduction or distribution of the **dataset**, while disclaiming accuracy/currency; those terms do not automatically apply to other portal materials.

**Do not conflate the viewer's 2024 hosted service with the baseline downloaded here.** The viewer links `VotingPrecincts2024_100824/FeatureServer/0`, whereas these 2024 assets come from the state OpenData MapServer/9 and its matching item. Their equivalence has not been tested. No features from the viewer's alternate 2024 service were substituted.

## Files, identifiers and CRS

The [manifest](maps/manifest.csv) contains the requested county, five-digit FIPS, sourceURL, official_owner, geometry_vintage, retrieved_utc, local_path, format, CRS, feature_count, SHA-256 and limitations. It inventories the 92 derived county assets plus the Meridian municipal PDF. Original response pages are retained losslessly in gzip under `maps/raw/2024/` and `maps/raw/2026/`; no geometry simplification or coordinate rounding is applied to the GeoJSON. Each retrieval record saves the original decompressed response hash and stored gzip hash. Native coordinate-derived area/length fields are retained as source attributes; they are **not** recomputed in geographic coordinates and should not be treated as square degrees.

| Meaning | 2024 source field | 2026 source field | Handling |
| --- | --- | --- | --- |
| Full precinct identifier | `PRECINCTID` | `PrecinctID` | Preserve as string; e.g. `WP-163-01380-00001` |
| County | `COUNTYFIPS` | `CountyFIPS` | Three-digit source code; prefix `26` for five-digit county FIPS |
| Municipality | `MCDFIPS` | `MCDFIPS` | Five-character source string; preserve leading zeroes |
| Ward / precinct | `WARD`, `PRECINCT` | `Ward`, `Precinct` | Preserve strings, including leading zeroes; field widths differ |
| Human-readable labels | `Precinct_Long_Name`, `Precinct_Short_Name`, `Jurisdiction_Name` | `PrecinctLo`, `PrecinctSh`, `Jurisdicti` | Truncated field names are documented from schema/samples, not used as join keys |
| Election label | `ELECTIONYE` | `ElectionYe` | Inspect feature values, not just layer name |
| Source record identifier | `OBJECTID` | `OBJECTID_1`, `OBJECTID` | Retrieval IDs only; not stable cross-vintage keys |
| Other source codes | `NAME`, `VTDST` | `PrecinctCo`, `VTD` | Retain; do not presume interchangeable with results precinct/board IDs |
| Equipment / registration attributes | `Tabulator_Voter_Assist`, `Registered_Voters`, `Active_Voters` | `TabulatorV`, `Registered`, `ActiveVote` | Not turnout, votes, or a dated voter denominator; not used for forecasts |

Field evidence: saved [2024 schema](maps/raw/2024-layer.json), [2026 schema](maps/raw/2026-layer.json), and per-county sample properties in [checks.json](maps/checks.json), from the linked official services on 2026-10-17. Example 2026 Detroit ID: `WP-163-22000-05120`, with `MCDFIPS=22000`, `Ward=05`, `Precinct=120`; use all components, never precinct 120 alone.

The 2024 native CRS is **EPSG:3078** (ArcGIS 102123); the 2026 native CRS is **EPSG:3857** (ArcGIS 102100). The services perform output transformation with `outSR=4326`; saved GeoJSON uses longitude/latitude, **OGC:CRS84 axis order**, with no legacy CRS object. SVGs use a simple local display transform `x=longitude*cos(43°)`, `y=-latitude`, fitted independently to each county; they have no basemap and are unsuitable for distance/area measurement. SVG display positions are rounded to 0.01 viewBox units, with consecutive duplicate display vertices omitted; geographic source coordinates remain unchanged.

## Coverage and validation

The following table is calculated from the saved official source snapshots (retrieved 2026-10-17); “invalid” means GEOS topology validation of the server-exported GeoJSON, not a determination about the native geodatabase. All files have nonempty Polygon/MultiPolygon geometry, finite geographic coordinates, closed rings with at least four positions, correct county filtering, unique nonmissing precinct IDs **within each county and vintage**, and counts matching the source's object-ID query. Object-ID queries plus batches of at most 200 avoid service transfer-limit truncation. No features were dropped or repaired.

| County | FIPS | 2024 features (invalid) | 2026 features (invalid) | 2024 / 2026 preview |
| --- | --- | ---: | ---: | --- |
| Wayne | 26163 | 847 (0) | 720 (0) | [2024](maps/2024/wayne.svg) / [2026](maps/2026/wayne.svg) |
| Oakland | 26125 | 497 (0) | 404 (0) | [2024](maps/2024/oakland.svg) / [2026](maps/2026/oakland.svg) |
| Macomb | 26099 | 308 (0) | 249 (0) | [2024](maps/2024/macomb.svg) / [2026](maps/2026/macomb.svg) |
| Kent | 26081 | 240 (1) | 202 (4) | [2024](maps/2024/kent.svg) / [2026](maps/2026/kent.svg) |
| Genesee | 26049 | 156 (0) | 142 (0) | [2024](maps/2024/genesee.svg) / [2026](maps/2026/genesee.svg) |
| Washtenaw | 26161 | 120 (4) | 112 (9) | [2024](maps/2024/washtenaw.svg) / [2026](maps/2026/washtenaw.svg) |
| Ottawa | 26139 | 101 (0) | 98 (0) | [2024](maps/2024/ottawa.svg) / [2026](maps/2026/ottawa.svg) |
| Ingham | 26065 | 103 (0) | 81 (2) | [2024](maps/2024/ingham.svg) / [2026](maps/2026/ingham.svg) |
| Kalamazoo | 26077 | 105 (0) | 85 (0) | [2024](maps/2024/kalamazoo.svg) / [2026](maps/2026/kalamazoo.svg) |
| Livingston | 26093 | 73 (0) | 65 (2) | [2024](maps/2024/livingston.svg) / [2026](maps/2026/livingston.svg) |
| Saginaw | 26145 | 76 (0) | 71 (2) | [2024](maps/2024/saginaw.svg) / [2026](maps/2026/saginaw.svg) |
| St. Clair | 26147 | 63 (1) | 61 (1) | [2024](maps/2024/st-clair.svg) / [2026](maps/2026/st-clair.svg) |
| Muskegon | 26121 | 53 (0) | 52 (0) | [2024](maps/2024/muskegon.svg) / [2026](maps/2026/muskegon.svg) |
| Monroe | 26115 | 63 (1) | 63 (2) | [2024](maps/2024/monroe.svg) / [2026](maps/2026/monroe.svg) |
| Berrien | 26021 | 58 (0) | 55 (1) | [2024](maps/2024/berrien.svg) / [2026](maps/2026/berrien.svg) |
| Jackson | 26075 | 59 (0) | 56 (0) | [2024](maps/2024/jackson.svg) / [2026](maps/2026/jackson.svg) |
| Allegan | 26005 | 45 (2) | 44 (3) | [2024](maps/2024/allegan.svg) / [2026](maps/2026/allegan.svg) |
| Calhoun | 26025 | 56 (1) | 47 (3) | [2024](maps/2024/calhoun.svg) / [2026](maps/2026/calhoun.svg) |
| Eaton | 26045 | 44 (0) | 39 (0) | [2024](maps/2024/eaton.svg) / [2026](maps/2026/eaton.svg) |
| Grand Traverse | 26055 | 39 (0) | 36 (0) | [2024](maps/2024/grand-traverse.svg) / [2026](maps/2026/grand-traverse.svg) |
| Bay | 26017 | 40 (0) | 35 (1) | [2024](maps/2024/bay.svg) / [2026](maps/2026/bay.svg) |
| Lapeer | 26087 | 33 (0) | 32 (0) | [2024](maps/2024/lapeer.svg) / [2026](maps/2026/lapeer.svg) |
| Lenawee | 26091 | 41 (1) | 40 (2) | [2024](maps/2024/lenawee.svg) / [2026](maps/2026/lenawee.svg) |

**Topology findings:** 11 invalid geometries in the 2024 exports and 32 in 2026 (43 total), with zero empty geometries. [topology-checks.json](maps/topology-checks.json) lists each source precinct ID, the GEOS reason and coordinates. Ring self-intersections and nested shells are present. These errors can affect clipping, overlay and area-weighted allocation; review the native-source geometry and any repair separately, preserve this raw snapshot, and label any repaired derivative. This check does not establish absence of gaps/overlaps between adjacent valid precincts or agreement with legal boundaries; those checks remain open.

**Mixed attribute warning:** Genesee's 2024 layer has 155 features labeled 2024 and one labeled 2023. The exceptional feature is `WP-049-29020-00002` (Flint Township, Precinct 2). This is a source anomaly; the layer's source-year attribute is retained. See `checks.json` and the Genesee GeoJSON before matching this feature to returns. The rest of the selected 2024 features are labeled 2024; all selected 2026 features are labeled 2026. The file directory expresses the source layer's cycle, not a rewrite of its individual attribute values.

## Changes, crosswalk needs and reporting boards

The counts differ in 22 counties; Monroe has 63 in each vintage, which does not prove unchanged boundaries. [Cross-vintage diagnostics](maps/topology-checks.json) report common, removed and added full precinct IDs by county. Shared IDs do **not** prove unchanged boundaries. The exact topological equality comparison is intentionally strict and is confounded by the two services' different native CRS transformations; tiny coordinate differences alone must not be interpreted as substantive boundary changes. This is an ID inventory and diagnostic, **not a completed geographic or election-results crosswalk**. No votes are allocated by these files.

Before using precinct swing, obtain the 2024 result unit dictionary and the clerk's approved November 2026 precinct/board roster. Match county + municipality + ward + source-native precinct ID, verify the election-specific meaning of each identifier, review splits/mergers, and retain all unmatched units. For actual geographic changes, develop reviewed many-to-many crosswalks using appropriate voter/address or other documented weights; area share alone is not evidence of vote share. Reconcile back to county totals.

The polygon schema identifies geographic precincts and includes equipment fields; it does **not** supply a voting-method roster, absentee counting board coverage, early-vote board coverage, combined precinct reporting definitions, or outstanding ballots. An absentee/early-vote result row may aggregate several polygons or have no polygon of its own. Do not join those rows on a short number, duplicate their votes across polygons, infer votes from registration fields, or equate feature counts with “precincts reporting.” If an approved board-to-geography mapping is unavailable, preserve the result as an unmatched reporting unit and forecast at a supported aggregate. These are interpretation constraints of the downloaded schemas and the [project plan](../../../ELECTION_NIGHT_PLAN.md), not a claim that a particular county's 2026 board configuration has been verified.

## Municipal supplements and access limitations

- **Ingham / Meridian:** [official municipal PDF](https://www.meridian.mi.us/media/nxfeq31d/2026-precinct-and-polling-location-map-update.pdf), saved [locally](maps/raw/meridian-2026.pdf), retrieved 2026-10-17. Its printed title is “Voting Precincts & Polling Locations Map,” and the extracted page says **Last Updated: 05/29/2026**; the initial research lead's April 24 date is not supported by the downloaded copy. The HTTP Last-Modified header is 2026-08-18 15:49:08 GMT, a different kind of date. This covers one municipality, not all Ingham, and does not establish November approval. A [text extraction](maps/raw/meridian-2026.txt) is retained for date verification; the original PDF is authoritative for its appearance.
- **Wayne / Detroit:** both county GeoJSONs include Detroit (400 source features in 2024, 402 in 2026, calculated from the saved downloads); select `MCDFIPS='22000'` within `CountyFIPS='163'` (2026 spelling; 2024 uses uppercase county field). The [city election maps index](https://detroitmi.gov/node/21731) and [official PDF labeled Detroit Election Precincts & 2026 City Council Districts](https://detroitmi.gov/sites/detroitmi.localhost/files/2025-04/Council%20District%20Maps%202025.pdf) were found through the web reader on 2026-10-17. Direct PDF download returned HTTP 403 and is recorded as a failed attempt, **not a saved map**. The 2026 council-district label does not certify precinct currency for the November Senate election. Older city PDFs were not substituted for current precinct geometry. County-level downloads already provide actual Detroit polygon coverage.
- The alternate [BOE precinctmapping layer](https://gisp.mcgi.state.mi.us/maps/rest/services/BOE/precinctmapping/MapServer/0?f=pjson) returned HTTP 403 through Python. Its live vintage and `ConfirmationDate` values were therefore not established or used. Other official statewide layers succeeded, so retries were bounded. Direct DTMB page requests also returned 403; web-reader access worked as described above. These are access-path failures, not assertions that human users cannot reach those sites.

## Reproduction and checks

From repository root:

```sh
# Offline: checks preserved page hashes, rebuilds GeoJSON/previews/manifest/checks/index.
python3 senate/2026/michigan/maps/build_maps.py
# Optional network refresh: replaces the working snapshot; preserve old versions first.
python3 senate/2026/michigan/maps/fetch_evidence.py
python3 senate/2026/michigan/maps/build_maps.py --refresh
# Optional topology diagnostics require Shapely (version recorded in output).
python3 senate/2026/michigan/maps/validate_topology.py
# Recreate the optional municipal PDF text extraction with Poppler.
pdftotext -layout senate/2026/michigan/maps/raw/meridian-2026.pdf senate/2026/michigan/maps/raw/meridian-2026.txt
```

Download/build and metadata retrieval use Python's standard library only. Topology validation uses Shapely/GEOS and does not mutate geometry. The raw original server responses are compressed with deterministic gzip, while county GeoJSON stays directly usable without decompression. Combined raw duplicates were removed; original batch pages and their full retrieval records remain. SVG rounding only affects generated previews. Assets remain below 100 MB combined without sacrificing source coordinate precision.

Validation completed 2026-10-17: all 46 county/vintage feature counts reconcile to object-ID query counts; 46 precinct-ID uniqueness and county/year checks inspected; all raw page and manifest asset hashes verified; 46 files tested for geometry validity; 92 derived map assets plus one PDF inventoried. Remaining material gaps are November 2026 approval, the one Genesee year anomaly, topology repair/adjacency review, an election-results/board crosswalk, and an independently frozen November 2024 legal-boundary snapshot. County coverage itself is complete for both selected layers.

# Kansas precinct maps: downloaded reference package

**All exact 23 priority counties have actual downloaded, full native official
2022 precinct geometry and county-specific previews/download cards.** The
[offline map index](maps/index.html) also retains all 105 counties and every
one of the **22,031 historical native identities** in five overlapping families.
Additional county originals and agency-attributed native services supplement the
2022 reference. **Current local coverage and authority gaps remain; no November
2026 physical boundary approval or results-to-map crosswalk is granted.** This
is a completed source/acquisition/reproduction package with explicit limits,
not a claim of 23 approved current county maps.

Research/retrieval: **2026-10-18 UTC**. Open the index locally; it uses no online
basemap, library or network fetch. [Inventory and exact county gaps](maps/inventory.json),
[original acquisition records](maps/acquisition.json), [schema](maps/SCHEMA.md),
[visual inspection](maps/visual-review.md), [offline checks](maps/validation.json)
and [owned asset manifest](maps/asset-manifest.json) are retained together.

## Scope and immutable historical inputs

The coordinator accepted all 105 counties and the exact ordered 23 below for
research. The named four-ticket 2024 presidential denominator is **1,327,591**;
top15=970,376; minimum23=1,067,659 (**80.4207771821%**); preceding22=1,057,110.
Sumner20191 contributes10,549; the other82 counties retain259,932 votes. Those
are named contest votes, not ballots or geographic area. Unreported statewide
write-ins/under/over remain unavailable. Kansas had no 2024 Senate election;
2020 Marshall-Bollier is the same ClassII seat,2022 Moran-Holland the other
ClassIII/midterm contest. [Accepted contract](data/turnout/priority-set.json),
[external acceptance](data/coordinator-priority-acceptance.json).

The 20,297,853-byte contract SHA256 remains
`dcdc1457a5b08851ef76b5372435d56788f647708da5ff9a6ef35435f92fa6a7`.
[Read-only pins](maps/readonly-pins.json) verify the supplied final first-wave
manifest/CSV/report hashes, all 127 owned first-wave assets and full shared
original metadata without copying original workbooks/PDFs. Coordinator
first-wave/target/native checks stay read-only; no reverse acceptance hash is
introduced. The separate official-results [source scopes](data/results-sources/native-source-scopes.json)
retain old/primary/test/no-results/viewer exclusions; a successful HTTP response
does not establish current data. Legal review remains with that assignment. The final read-only peer scopes retain
Douglas18 as 2024 general (102 literal labels/408 four-named precinct CSV rows,
666 generic write-in votes in summary only); Leavenworth2/Butler3 and Miami126776/Harvey126775
as August2026 primaries; Miami122433/key0004 and Harvey122758/key39 as actual 2024
general. Harvey122159 is August2024 primary despite its local `harvey-2024`
capture prefix and stays excluded as a general baseline. Riley's signed 2024
abstract (document ID24032) matches the accepted four-ticket vector, totaling
24,313 votes; FinalAllGroups (document ID24038) totals23,920 named presidential
votes,393 fewer. The discrepancy remains separate, with no cause inferred. Full source arrays,
IDs and repeats remain in [county inventory](data/results-sources/county-inventory.json)
and [vendor extracts](data/results-sources/vendor-extracts.json). None of these
result identifiers is a physical polygon or November2026 join approval.

Each all-county `maps/native/<FIPS>.json.gz` contains the complete unchanged
source contract object and every constituent: literal IDs/keys/names, district
and VTD fields, sheets/XML paths/rows, unavailable cases and source-family
objects. The five families retain **4,567 /4,566 /4,535 /3,867 /4,496 identities**,
525 county-family groups, and **0 /13 /12 /19 /31 unknown-count units**. They
overlap and are never summed. All native results remain explicitly unmatched;
county footers are controls, not extra precincts. Blank/redacted cells and
residuals remain unallocated. Generic 2020 write-ins are separate from named
controls; Johnson NON raw header codes are not candidate identities. The
source 2024 ballot/registration vintages and inconsistent 2022 turnout workbook
remain untouched; neither supplies map weights. [Turnout](turnout.md),
[baseline methods](county-partisanship.md).

## Official state reference and county source chains

The [SOS election resources](https://sos.ks.gov/elections/election-resources.html)
lead to [district maps](https://sos.ks.gov/elections/district-maps.html) for
Congress/legislature/education; those are not county precinct downloads.
The official [DASC site](https://www.kansasgis.org/) links its
[state GIS hub](https://hub.kansasgis.org/). The hub's preserved embedded catalog
group returns the [Voting Districts item](https://www.arcgis.com/sharing/rest/content/items/bbef57286a754359ace36374d34d6bce?f=json),
whose actual description identifies KLRD **2022 post-redistricting precincts**.
It explicitly says counties can later rename/recombine/change precincts and
KLRD does not maintain them between redistrictings. This establishes a historical
reference scope; a VTD code never proves physical equivalence to2024/2026 units.
The linked [native service](https://services1.arcgis.com/q2CglofYX6ACNEeu/arcgis/rest/services/Voting_Districts/FeatureServer/0)
was downloaded completely: **4,749 polygon objects, 792,805 native vertices,
all 105 county FIPS**. All48 original native JSON batches, counts, complete IDs,
pre/post metadata and full extent are retained once. County cards reference
those originals and give their complete county FID lists.

County chains were inspected through actual returned HTML/configuration/data,
not titles alone. Exact requested/final URLs, redirects, headers, source clocks,
UTC retrieval, original and stored bytes/hashes are in the acquisition records.
Examples include:

- [Johnson election maps](https://www.jocoelection.org/voting-election-info/district-county-maps)
  directly link the actual county precinct PDF. [County AIMS free data](https://aims.jocogov.org/aimsdata/freedata.aspx)
  link its native precinct SHP ZIP. The downloaded PDF prints **10/17/2026**,
  superseding the older cached search date for these retrieved bytes.
- [Sedgwick election maps](https://www.sedgwickcounty.org/elections/maps-and-district-information/)
  link county GIS; its [precinct data page](https://www.sedgwickcounty.org/gis/data-layers/?id=22)
  supplies the actual shapefile ZIP. It contains541 PolygonZ records; the page's
  approximate439-record description is preserved as a separate catalog statement.
- [Shawnee elections](https://www.snco.gov/election/) link ElectionViewer;
  retained configuration/webmap identify the actual native Voting_Precincts
  service, not the overlapping legislative layers. [Crawford maps](https://www.crawfordcountykansas.org/district-maps.html)
  similarly link a precinct app whose webmap identifies its Precincts service.
- [Butler elections](https://www.bucoks.gov/181/Elections) link Elections Hub;
  its full URL-encoded embedded state identifies the actual Voting Precincts
  Experience, then webmap and layer17. Precinct/part/enclave IDs remain distinct.
  [Franklin GIS](https://www.franklincoks.org/555/Maps) follows the same actual
  app→webmap→Voting Precincts layer2 chain; points/commission layers are excluded.
- [Douglas maps](https://www.dgcoks.gov/county-clerk/voting-and-elections/maps)
  link media6038, which links the original county GIS portal PDF. [Riley](https://www.rileycountyks.gov/145/Riley-County-Voting-District-Maps),
  [Miami](https://miamicountyks.gov/254/Elections), [Lyon](https://www.lyoncountyks.gov/240/Election-Office),
  [Finney](https://finneycountyks.gov/447/Polling-Locations-Voting-Districts),
  [Harvey](https://www.hvcoksvote.gov/elected-officials) and
  [Ellis](https://www.ellisco.net/427/Maps) actually link the downloaded PDFs.
  Leavenworth election/GIS indices independently link2025/2026 maps; the vendor
  redirects are preserved. McPherson's county Voter Search Map redirects to its
  actual app/webmap/native district service.

The Saline county primary page's Voting Precincts outbound link was inspected
with the web reader; direct original acquisition returned403. The
[observation](maps/saline-web-observation.json) is labeled separately from actual
HTTP bytes, while linked app/webmap/service originals succeeded. Wyandotte's
actual official GIS PDF supplies county map evidence, while its queried service
returns153 attribute-only objects and its old linked ZIP returns404.
Reno, Montgomery and Sumner native products are **agency-attributed references
with an unresolved county-site outbound-link chain**; their catalog/org naming
is not substituted for proof. Whole originals and precise limits are retained.

## Exact priority assets and coverage

Every row has the complete official 2022 native precinct fallback, shown as a
source polygon count, plus the actual additional asset scope below. Counts in
different columns/families are alternatives, not additive. PDFs are not counted
as polygon features. All current approval/crosswalk fields remain false.

| Priority county | FIPS | Additional downloaded scope | 2022 source polygons | Local review |
| --- | --- | --- | ---: | --- |
| 1. Johnson | 20091 | SHP 693 + PDF | 595 | [card](maps/index.html#20091) / [full native contexts](maps/native/20091.json.gz) |
| 2. Sedgwick | 20173 | PolygonZ SHP 541 | 548 | [card](maps/index.html#20173) / [full native contexts](maps/native/20173.json.gz) |
| 3. Shawnee | 20177 | 247 native objects; 4 curves | 272 | [card](maps/index.html#20177) / [full native contexts](maps/native/20177.json.gz) |
| 4. Douglas | 20045 | County precinct-parts PDF | 182 | [card](maps/index.html#20045) / [full native contexts](maps/native/20045.json.gz) |
| 5. Wyandotte | 20209 | County PDF; 153 attribute-only objects | 155 | [card](maps/index.html#20209) / [full native contexts](maps/native/20209.json.gz) |
| 6. Leavenworth | 20103 | Separate 2026/2025 PDFs | 92 | [card](maps/index.html#20103) / [full native contexts](maps/native/20103.json.gz) |
| 7. Butler | 20015 | 193 native voting-district/part objects | 87 | [card](maps/index.html#20015) / [full native contexts](maps/native/20015.json.gz) |
| 8. Reno | 20155 | 105 agency-attributed polygons | 93 | [card](maps/index.html#20155) / [full native contexts](maps/native/20155.json.gz) |
| 9. Riley | 20161 | County + Manhattan PDFs | 97 | [card](maps/index.html#20161) / [full native contexts](maps/native/20161.json.gz) |
| 10. Saline | 20169 | 75 native objects, Z/M | 89 | [card](maps/index.html#20169) / [full native contexts](maps/native/20169.json.gz) |
| 11. Miami | 20121 | 2026-labeled voting-district PDF | 93 | [card](maps/index.html#20121) / [full native contexts](maps/native/20121.json.gz) |
| 12. Crawford | 20037 | 61 native precinct polygons | 67 | [card](maps/index.html#20037) / [full native contexts](maps/native/20037.json.gz) |
| 13. Harvey | 20079 | 39-page individual-map PDF | 58 | [card](maps/index.html#20079) / [full native contexts](maps/native/20079.json.gz) |
| 14. McPherson | 20113 | 42 native voting-district objects | 38 | [card](maps/index.html#20113) / [full native contexts](maps/native/20113.json.gz) |
| 15. Ellis | 20051 | Rural + Hays precinct PDFs; two city context PDFs | 50 | [card](maps/index.html#20051) / [full native contexts](maps/native/20051.json.gz) |
| 16. Cowley | 20035 | County-produced 2018 PDF via UF archive | 75 | [card](maps/index.html#20035) / [full native contexts](maps/native/20035.json.gz) |
| 17. Pottawatomie | 20149 | 2022 state native reference; local legislative map rejected | 43 | [card](maps/index.html#20149) / [full native contexts](maps/native/20149.json.gz) |
| 18. Lyon | 20111 | City/rural PDFs + polling notice | 58 | [card](maps/index.html#20111) / [full native contexts](maps/native/20111.json.gz) |
| 19. Franklin | 20059 | 25 native precinct objects, Z/M | 27 | [card](maps/index.html#20059) / [full native contexts](maps/native/20059.json.gz) |
| 20. Montgomery | 20125 | 90 precincts / 189 parts, agency-attributed alternatives | 84 | [card](maps/index.html#20125) / [full native contexts](maps/native/20125.json.gz) |
| 21. Finney | 20055 | County + city original PDFs | 71 | [card](maps/index.html#20055) / [full native contexts](maps/native/20055.json.gz) |
| 22. Barton | 20009 | Great Bend precinct PDF; ward/polling context | 50 | [card](maps/index.html#20009) / [full native contexts](maps/native/20009.json.gz) |
| 23. Sumner | 20191 | 53 agency-attributed clerk polygons | 65 | [card](maps/index.html#20191) / [full native contexts](maps/native/20191.json.gz) |

The index cards and [county notes](maps/county-notes.json) give individual
vintages, original downloads, bounded attempts and precise gaps. Important limits:

- **Cowley:** current county election/GIS routes, Beacon403, a candidate county
  PDF URL404 (not observed linked) and bounded catalog searches did not recover a current county precinct
  original. The UF-mirrored county map actually prints **May 8, 2018**, despite the
  archive's2020 category/2024 accession; it stays a secondary historical fallback.
- **Pottawatomie:** current county election, district/GIS maps, actual property
  webmap and county-org catalog did not expose a current precinct layer. The
  downloaded legislative PDF is wrong-scope and explicitly rejected as precincts.
  Entire post2022/current/November precinct geography remains a gap.
- **Barton:** Great Bend has actual precinct/ward detail; Hoisington shows wards.
  Countywide polling-area shading is not full rural/township precinct splits.
  Other current town/rural precinct detail remains missing;2022 state native
  detail supplies a clearly labeled full-county reference.
- **Harvey:** all 39 original individual-map pages are saved; the landing page
  says 41 precincts. Page count does not establish a missing-two-precinct cause or
  prove current unit equivalence; roster-to-map reconciliation remains open.
- **Ellis:** rural and Hays originals show precinct detail. Complementary Ellis/
  Victoria city-limit/polling maps are context, not proved physical precinct
  boundaries. The four maps credit2023; current city/precinct equivalence is open.
- **Reno/Montgomery/Sumner:** full native reference objects succeeded, but actual
  county-site-to-vendor authority links were not recovered. County pages blocked
  or legacy links failed. Their names/counts do not upgrade them to approved
  boundaries. Montgomery90 Precincts and189 Precinct Parts are kept separately.

No county has a documentary November 2026 boundary approval, frozen election-day
2024 boundary equivalence, approved reporting-board/method dictionary or
historical-to-current crosswalk from this work. Administrative/unknown/unmatched
units remain. Polling locations, ballot splits, district maps, city/county
outlines, Census/VTD labels, map counts and ID hashes do not allocate votes.

## Geometry, original bytes and checks

Original ZIPs preserve all SHP/SHX/DBF/PRJ and optional members, native IDs,
attributes, parts, vertices, Z/M and WKT. Every ZIP CRC/member hash and all
SHP/SHX/DBF record counts/offsets pass. Native service queries request all fields,
Z/M/true curves with no reprojection, precision reduction, quantization, clipping,
simplification or repair. Before/after count/all-ID queries and exact bounded
batch unions match for all 12 queried service layers. A service's completed ID
inventory alone is not geometry coverage: Wyandotte's missing153 geometries
remain unavailable and its PDF stays separate.

All original response bytes are stored once, either directly(PDF) or lossless
gzip. Failed/error/test/wrong-scope originals remain separately identified.
Every stored artifact is strictly below 40,000,000bytes; no original needed
splitting. `reconstruct.py` checks part/stream/original hashes and sizes before
reproducing the exact ordered bytes. No truncated PDF or simplified original is
included. [Archive diagnostics](maps/extracts/archive-checks.json),
[build/geometry summary](maps/build-summary.json),
[all map-native attributes](maps/extracts/map-feature-attributes.json.gz).

GEOS XY diagnostics retain invalid originals: Johnson3, Sedgwick4, Shawnee1,
Crawford1, Saline1; the state2022 layer has0 invalid/empty geometries in this
snapshot. Four Shawnee original true-curve objects are retained and explicitly
excluded from GEOS; only a separate preview query linearizes them. Source Z/M
remain intact, including Saline nullM values. Every positive-area intersection
between valid XY polygons is enumerated with original IDs and actual source
units(feet²/metres²/degree²), with no threshold cutoff; small slivers are not
asserted legal overlaps. Invalid/null/curve exclusions are explicit. No repairs,
residual distributions, geometry swaps or invented cause is imposed. Legal
boundary/adjacency agreement remains unproved. Native coordinates are always
available in raw originals; previews use rounded display pixels only.

All **23 PDF originals /61 pages** render into seven contact sheets, including
scans, the polling notice, old/context maps and the rejected legislative map.
Representative pages were visually inspected to establish actual contents and
printed clocks. The local index has exact23 ordered preview/download cards,
105 inventory rows and105 full historical-native context files. Previews and
native originals are separate; colors have no political meaning.

Reproduce offline from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/kansas/maps/build.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/kansas/maps/validate.py
```

For original reconstruction/network recipes, dependency versions, fields,
coordinate/axis units, full schema, exclusions, hash direction and freeze policy,
use [SCHEMA.md](maps/SCHEMA.md). Validation checks exact105/23 order, every 22,031
constituent/source object and unknown case, full state/county FIPS/ID scopes,
original/stored/shared hashes, ZIP controls, service pagination/transfer flags,
native extents/broad Kansas bounds, all relative links, renders, whole owned
manifest coverage and strict per-file cap. It does not claim a current-approved
physical crosswalk, November feed/cadence, outstanding count, collector or
calibrated Needle.

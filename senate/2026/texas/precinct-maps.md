# Texas precinct maps and reporting compatibility

Actual downloads cover **all 34 accepted priority counties**, with four full
county precinct vintages each: 2024 general, 2026 primary, 2022 general and
2020 general. The [offline map index](maps/index.html) includes previews,
136 full-resolution county shapefile downloads, local originals and an all-254
county inventory. Observations were acquired October 17–18, 2026, in UTC as
recorded per response. These are reference boundaries and source diagnostics,
not an approved November reporting crosswalk, a collector or calibration.

The exact accepted county set supplies 9,076,868 / 11,291,854 reported 2024
Senate candidate votes, or 80.384213%. The first 33 supply 9,018,686; Midland's
58,182 crosses 80%. All 254 counties remain in the inventory. The accepted
[ordered keys](data/coordinator-priority-keys.txt) have SHA-256
`a5d39344328ab3c0f76809439c6af42c09a59d81f76b9b756e5b538a63ac5be5`.
The [coordinator reconciliation](data/coordinator-baseline-reconciliation.json)
approves county counts and priority, without accepting finer geography.

## Actual assets

The Texas Legislative Council's [precinct catalog](https://data.capitol.texas.gov/dataset/precincts)
links actual county-collected precinct shapefiles. All four relevant original
ZIPs were downloaded, preserving original bytes and metadata once per vintage:

| Source vintage | Native precinct features | Original vertices | County coverage | Original download provenance |
| --- | ---: | ---: | ---: | --- |
| 2024 general | 9,657 | 4,515,932 | 254 | [Exact URL, bytes, hashes, ordered parts](maps/sources/tlc-24g.json) |
| 2026 primary | 9,614 | 4,514,608 | 254 | [Exact URL, bytes, hashes, ordered parts](maps/sources/tlc-26p.json) |
| 2022 general | 9,586 | 4,504,954 | 254 | [Exact URL, bytes, hashes, ordered parts](maps/sources/tlc-22g.json) |
| 2020 general | 9,014 | 4,514,908 | 254 | [Exact URL, bytes, hashes, ordered parts](maps/sources/tlc-20g.json) |

Every priority-county subset copies the original SHP geometry record bodies and
DBF attribute records byte for byte, with full vertices and no simplification or
repair. Complete statewide originals remain reconstructible. The 68 county
previews display 2024 and 2026 primary independently; 2026 geometry never replaces
the historical election's geometry. All four vintages remain downloadable.

There are also nine fully acquired county GIS layers with 1,864 features:
Bexar 806; Travis 308; Fort Bend's separately named 2025/2022 layers 201/175;
Brazoria's 2024/2026 layers 80/84; Bell's 2022 layer 72; Hays's 2026 layer 88;
Johnson's 2022 layer 50. Original metadata and full-precision query pages retain
all attributes, complete object-ID sets and Z values where returned. The
[county GIS summary](maps/geometry/local-summary.json) and individual
[pagination audits](maps/gis/bexar-voter-audit.json) give the complete accounting.

Two additional original ZIPs retain Harris County Attorney's 1,165 adopted
historical precincts and the City of Galveston's 96-feature, VTD-named voting
reference. These are independently scoped sources, not substitutes for current
county precinct approval. Their [authority chains](maps/authority-chains.json),
[Harris audit](maps/geometry/extra-harris-zip-https.json) and
[Galveston audit](maps/geometry/extra-galveston-city-voting.json) preserve the
distinction.

**37 actual PDF originals, 311 pages**, include countywide maps, individual
mapbooks and adoption/change notices. The complete 121-page Montgomery mapbook,
62-page Bell mapbook and 62-page Webb certified order/mapbook are retained.
County PDFs also cover Travis, Collin, Williamson, El Paso, Hays, Nueces, Comal,
Guadalupe, Johnson, Parker, Randall, Midland, Webb and Rockwall. Hidalgo's older
notice includes a countywide map; Cameron precinct 53, Grayson precinct 101 and
Smith precinct 100 are explicitly partial county PDF coverage. All 34 have
complete countywide TLC reference geometry regardless of local PDF availability.

The [PDF inspection](maps/pdf/inspection.json) records source status/hash/bytes,
page count, metadata, per-page diagnostics, complete text and dated/legal lines.
Poppler and PyMuPDF independently agree on page counts. Sixty-two selected page
previews and six contact sheets were rendered; representative actual maps were
[visually inspected](maps/visual-review.json), including raster Collin and signed
Guadalupe attachments. PDF originals are never replaced by viewer HTML or
screenshots. Previews cover selected pages, while originals retain every page.

## Priority counties

The [all-county CSV](maps/inventory/all-counties.csv) follows the exact accepted
254-county order and links source-native reporting diagnostics. Each county page
below has its own preview/download entries, local acquisitions, exact attempted
routes, HTTP outcomes, reference scope and remaining gaps.

| Rank | County / preview and downloads | FIPS | 2024 general | 2026 primary | Local original coverage |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | [Harris](maps/pages/48201.html) | 48201 | 1172 | 1224 | adopted ZIP |
| 2 | [Dallas](maps/pages/48113.html) | 48113 | 885 | 791 | TLC reference; local export gap |
| 3 | [Tarrant](maps/pages/48439.html) | 48439 | 844 | 707 | 1 PDFs |
| 4 | [Bexar](maps/pages/48029.html) | 48029 | 776 | 806 | 1 GIS layers |
| 5 | [Travis](maps/pages/48453.html) | 48453 | 287 | 308 | 2 PDFs, 1 GIS layers |
| 6 | [Collin](maps/pages/48085.html) | 48085 | 252 | 273 | 1 PDFs |
| 7 | [Denton](maps/pages/48121.html) | 48121 | 240 | 252 | TLC reference; local export gap |
| 8 | [Fort Bend](maps/pages/48157.html) | 48157 | 175 | 201 | 2 GIS layers |
| 9 | [Montgomery](maps/pages/48339.html) | 48339 | 113 | 121 | 2 PDFs |
| 10 | [Williamson](maps/pages/48491.html) | 48491 | 164 | 177 | 1 PDFs |
| 11 | [El Paso](maps/pages/48141.html) | 48141 | 221 | 236 | 2 PDFs |
| 12 | [Hidalgo](maps/pages/48215.html) | 48215 | 259 | 258 | 1 PDFs |
| 13 | [Brazoria](maps/pages/48039.html) | 48039 | 80 | 84 | 2 GIS layers |
| 14 | [Galveston](maps/pages/48167.html) | 48167 | 96 | 96 | city-published VTD-named ZIP |
| 15 | [Bell](maps/pages/48027.html) | 48027 | 65 | 72 | 1 PDFs, 1 GIS layers |
| 16 | [Hays](maps/pages/48209.html) | 48209 | 87 | 88 | 1 PDFs, 1 GIS layers |
| 17 | [Lubbock](maps/pages/48303.html) | 48303 | 99 | 99 | 2 PDFs |
| 18 | [Nueces](maps/pages/48355.html) | 48355 | 129 | 132 | 1 PDFs |
| 19 | [Cameron](maps/pages/48061.html) | 48061 | 101 | 102 | 1 PDFs |
| 20 | [Comal](maps/pages/48091.html) | 48091 | 34 | 41 | 8 PDFs |
| 21 | [Smith](maps/pages/48423.html) | 48423 | 75 | 66 | 1 PDFs |
| 22 | [Mclennan](maps/pages/48309.html) | 48309 | 91 | 95 | TLC reference; local export gap |
| 23 | [Ellis](maps/pages/48139.html) | 48139 | 59 | 61 | TLC reference; local export gap |
| 24 | [Brazos](maps/pages/48041.html) | 48041 | 113 | 77 | TLC reference; local export gap |
| 25 | [Parker](maps/pages/48367.html) | 48367 | 45 | 46 | 1 PDFs |
| 26 | [Jefferson](maps/pages/48245.html) | 48245 | 104 | 104 | TLC reference; local export gap |
| 27 | [Guadalupe](maps/pages/48187.html) | 48187 | 76 | 78 | 2 PDFs |
| 28 | [Johnson](maps/pages/48251.html) | 48251 | 43 | 50 | 1 PDFs, 1 GIS layers |
| 29 | [Kaufman](maps/pages/48257.html) | 48257 | 37 | 37 | TLC reference; local export gap |
| 30 | [Randall](maps/pages/48381.html) | 48381 | 31 | 31 | 1 PDFs |
| 31 | [Grayson](maps/pages/48181.html) | 48181 | 41 | 42 | 2 PDFs |
| 32 | [Webb](maps/pages/48479.html) | 48479 | 78 | 78 | 3 PDFs |
| 33 | [Rockwall](maps/pages/48397.html) | 48397 | 26 | 27 | 1 PDFs |
| 34 | [Midland](maps/pages/48329.html) | 48329 | 46 | 47 | 1 PDFs |

## Reporting identities remain separate

The [reporting compatibility inventory](maps/inventory/reporting-unit-compatibility.csv.gz)
accounts for **48,679 source-scoped identities**: 31,702 historical OE keys,
4,276 original historical vendor units and 12,701 official-results discovery
identities. The independent first-wave identity sets agree and are not counted
twice. The [constituent inventory](maps/inventory/accepted-constituents.csv.gz)
preserves all **45,944 accepted constituent records across 254 groups**, including
county summaries and separately labelled VTD components. Original JSON, unit
labels, county identities, component ordinals and source/file identities remain.

Each available reporting identity is accounted for as ambiguous,
administrative/no-polygon, source conflict or unknown. **Zero geographic matches
are approved.** Exact same-year county ID strings are only lexical candidates:
names, padding, equal counts and map titles do not establish identity or a
historical/current crosswalk. A failed exact string comparison does not prove
that a polygon is absent. Central early/mail groups, ballot styles, polling
locations, county summaries and physical precincts remain distinct. No votes
or preferences are allocated to polygons.

The read-only [official-results native observations](data/results-sources/native-unit-observations.csv.gz)
retain all 170,013 positions/repeats, contests and raw JSON. The corresponding
[identities](data/results-sources/native-unit-identities.csv.gz) and
[schemas](data/results-sources/native-field-schemas.json) preserve observation
classes and occurrence counts. Historical selected OE candidate rows/repeats
remain in the peer originals referenced by exact hash, rather than being copied
or deduplicated. The [compatibility summary](maps/inventory/compatibility-summary.json)
and [read-only references](maps/read-only-references.json) provide the accounting.

Material compatibility defects remain explicit:

- SOS November setup has all 254 county Senate objects. Its MID is an
  alphabetical ordinal offset, **not county FIPS**. County identities come from
  complete published names; no numeric MID/FIPS join is used.
- Harris November embed 1126/Senate 9189 exposes 1,224 literal IDs, whereas SOS
  says 1,225. TLC 2026 primary also has 1,224 polygons; equality is not approval.
  The original 2024 Senate report instead has 1,584 units and reconciles all five
  named candidates to 1,548,914 votes. It does not establish 2026 geography.
- Tarrant Clarity 127297 and El Paso 127348 explicitly have
  `electiondetails.istestmode='1'`, despite no displayed test watermark. Fort
  Bend's setup is also test mode. They remain route/schema/native-discovery
  evidence and are excluded from current counts and approved geography.
- Tarrant's test setup has 2,985 identities; SOS says 708 and TLC 2026 primary
  has 707 polygons. El Paso's test setup and actual boundary PDF have 236 units
  versus SOS 237. These unresolved scopes are not forced into polygon joins.
- Bexar 127291 is non-test but all zero, with 806 native identities. Bell 126390
  is the May 26 primary runoff; Parker's sampled setup is an older election.
  Neither old election is admitted as November counts or geography.
- OE 2024's 184 files contain 182 actual native county labels; `hardin` contains
  Hunt rows and `jeff_davis` contains Grayson rows. Four sources have duplicate
  candidate keys and 22 have nonadditive numeric method fields. OE 2022 contains
  101 counties and 2020 contains 248. Literal/file conflicts and repeats remain
  unchanged. Original Dallas and Travis vendor samples retain different
  candidate vintages/universes despite internal reconciliation.
- Grayson's original March 3, 2026 primary PDF adds 42 labelled precincts and
  546 page-header appearances under source `county-48181-office-follow1-sample`,
  FIPS `48181`, kind `pdf_precinct_label`, class `older_election_excluded`.
  The generic report title is excluded as a unit. Bell's 42 vote-center rows
  are unchanged; no new Bell vote-center-status resource is implied.

The TLC [VTD catalog](https://data.capitol.texas.gov/dataset/vtds) is a different
geography from these precinct originals. Its splits/consolidations and the
known differences between redistricting-derived votes and accepted SOS controls
preclude spatial allocation of those votes here. Hays's county GIS uses a
literal field named `VTD`; Grayson's countywide PDF and Galveston's city ZIP also
use VTD terminology. Those labels are preserved without equating the sources
to TLC VTDs or automatically declaring them current physical precincts.

## Vintage, access and geometry limits

County primary evidence supports specific dated statements: Williamson's page
says October 28, 2025 adoption/effective January 1, 2026; Parker's page describes
the 335/355 split; Guadalupe's original signed May 13, 2025 order and Comal's
effective-2026 notices retain their actual attachments. Tarrant's PDF prints
effective January 1, 2026 and March 17, 2026 print date. These statements do not
transfer approval to later GIS edits or establish a results crosswalk.

Collin's landing-page adoption dates differ from its scanned map's 2023 court
order/January 2024 print text. Bell, Randall, Travis and Webb have retained older
adoption publications alongside later references. Source clock fields, printed
legal statements and retrieval UTC are kept separate in the
[metadata date audit](maps/metadata-dates.json). No upload timestamp or current
link is presented as legal November approval.

Local deep acquisition has precise gaps after bounded repairs. Dallas, Denton,
Galveston, Lubbock, Jefferson and Rockwall election routes returned HTTP 202 empty
responses; Cameron's root/maps routes returned 403. Alternate county routes,
county GIS pages, linked vendors and specific documents were tried. Several
were recovered, including original Smith viewer bytes and partial Cameron map
bytes. Jefferson's exact indexed order URL returned 404. McLennan, Ellis and
Kaufman did not yield a native county export through the acquired routes.
The [county notes](maps/county-notes.json) and per-county pages retain exact URLs,
responses, recovered assets and remaining scope. No empty/challenge body is
classified as a map. Complete downloaded TLC native precincts are clearly
labelled reference fallbacks for local gaps, rather than substituting county
outlines, vote centers, commissioner districts or guessed endpoints.

All 18,050,402 statewide source vertices and every attribute are retained.
The four vintages contain 13 invalid geometry records, all preserved; Tarrant
precinct 1211 is invalid in 2024/2022, and Bexar precinct 4110 in 2026 primary.
Within-county valid-geometry intersection checks find 75 positive-area pairs
across the four sources. Their largest area is approximately 0.052405 square
metres **in the native projected CRS**, consistent with very small slivers;
these are not repaired, rounded to zero or interpreted as legal ground area.
Invalid geometries are excluded only from that intersection calculation, with
the exclusion scope counted. County GIS/ZIP diagnostics use their own native
projected units, preserving their separate invalid/overlap findings. Johnson's
original XYZ is retained; previews show XY only. No curves were returned by the
acquired county services, despite explicit curve-support requests.

## Reproduction and checks

The [schema and commands](maps/SCHEMA.md) explain acquisition, original-byte
reconstruction, county subset construction, CRS/geometry diagnostics, PDF
rendering, native-unit compatibility and offline rebuilding. The
[manifest](maps/manifest.json), [CSV manifest](maps/manifest.csv),
[asset hashes](maps/asset-hashes.json) and [validation](maps/validation.json)
are the machine-readable handoff. Large originals are retained once using
lossless compression or ordered byte parts; every individual saved file is
strictly below 40,000,000 bytes. There are no retained dependency/cache folders.

Validation checks original/stored hashes and byte counts; all-254/priority-34
order and pinned inputs; complete native/constituent coverage and administrative
exceptions; SHP/SHX/DBF counts, every attribute/vertex and byte-identical county
subsets; full ArcGIS pre/post IDs, counts, batches and transfer flags; PDF
original/page previews; native CRS, geometry and Texas bounds; every local HTML
and Markdown link; and static offline operation. The remaining limitations are
source access, source scope/vintage and unapproved geographic compatibility,
not omitted priority counties. Coordinator review/integration remains separate.

The coordinator's independent [binary subset audit](data/coordinator-map-subset-checks.json)
also passed: all four original split streams, ZIP CRCs, all 254 county groups,
18,050,402 original vertices and all 136 county ZIPs. It independently compared
26,922 priority feature records against full original geometry bodies and DBF
rows, in source order, with unchanged PRJ/CPG and exact SHX offsets/lengths.
That audit does not infer topology, approval or a reporting crosswalk.

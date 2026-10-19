"""Write the owned report from measured offline artifacts and explicit findings."""
from common import *
def main():
 s=load('qa/build-summary.json');ps=load('county-parents.json');notes=load('source/county-findings.json');c=json.loads(check(load('qa/dependencies.json')['contract']));pm={p['county_parent_key']:p for p in ps}
 text='''# South Dakota precinct maps — 2026-10-19 research

**The exact304 historical-priority observations have an offline map index with
acquisition, access, vintage and finer-entry qualifications.** Open the
[ordered local index](maps/index.html). All691 observations, all66 full parents
and all387 remainder observations survive by exact full-object reference.
This is a completed qualified map-research package, with **zero approved
reporting-unit-to-polygon or November2026 crosswalks**.

The acquired county resources comprise **29 complete PDF map originals across
17 counties (107 complete pages)** and two native GIS snapshots: Minnehaha81
features and Pennington53. Minnehaha has both paper and native assets, so these
are18 distinct county-map parents. **208 priority entries have qualified county
map resources;96 have Census-only map resources.** Every one of304 also links
the actual complete official Census2020 VTD fallback, county-filtered for display.
The whole original785-feature/66-county ZIP is retained once by hash reference.
A county asset is a shared parent resource, not proof that the individual row
has a physical polygon. The [full691 inventory](maps/inventory-691.json),
[304 entries](maps/priority-index-304.json), [387 remainder](maps/remainder-387.json),
[all66 parents](maps/county-parents.json) and [map catalog](maps/source/asset-catalog.json)
make that distinction inspectable offline.

## Accepted historical order and complete source graph

Authority is solely the external [coordinator acceptance path](data/coordinator-priority-acceptance.json).
The original frozen [contract](data/turnout/priority-set.json) is2,955,655 bytes,
SHA256`a1c97454c68c1f30bdb6b7755cd826326e7380318eae74b6452465ee23e9c275`.
Its worker-acceptance and certified-robustness flags stay false. There is no
reverse acceptance pin or self-approval. The [independent dependency audit](maps/qa/dependencies.json)
checks279 exact pins and2,150 complete recursive object references, including
every source/method/null/unavailable/administrative/candidate field, complete
ordered children, all historical alternatives and original source references.
The originals are reused read-only, not copied into a second large archive.

The primary election is **2024 president; there was no2024 Senate election**.
Correctly headed public-native workbook choices are Harris DEM146,811,
Oliver LIB2,777, Trump REP271,938 and Kennedy IND7,202 =428,728.
The first303 observations contain342,947 votes; observation304 is Hamlin literal
`Precinct-26`, original worksheet32 row14, key
`sd:2024:pres:46057:sheet32:row14`, adding455 to343,402. The source integer80%
target is342,983. Top15=61,003; remainder387=85,326. These are native reporting
observations across39 priority county parents, not a21-county substitution.

Separate signed controls total428,922 (146,859/2,778/272,081/7,204).
The194 missing public votes across24 counties remain **unallocated**. Signed80%
target343,138 is191 above the source303 prefix, versus194 unallocated votes;
unknown native allocation/order prevents a certified minimum or membership
proof. Source304 is not a proved certified/all-eligible minimum. The separate
21-county signed prefix346,205 after20=342,469 is sensitivity only.

The correctly headed native workbook and separately headed Aurora workbook are
independent source presentations. The statewide all-race export's literal
`D7=Trump` / `E7=Trump1` headers remain misleading/contradictory as printed;
neither numerical resemblance nor the native workbook licenses relabeling them.
All raw candidate headings and unavailable method/ballot fields remain.

Complete2022 other-ClassIII Senate retains Thune REP, Bengs DEM and Lesnar LIB:
687 public-native rows/66 parents close exactly to348,020 signed votes
(Bengs91,007/Lesnar14,697/Thune242,316). The separate actual1420-page precinct
PDF has679 numeric observations/65 parents; Yankton pages are not located.
Yankton signed2,462/340/6,051 is county control, not invented native detail.
Complete2020 same-ClassII Rounds REP/Ahlers DEM has693 public rows/66 parents,
420,178 vs signed420,219: Rounds−24/Ahlers−17 across21 counties, unallocated.
All198 signed county vectors/594 candidate fields, distinct archive ballot and
registration tables, +4/−11 registration-source differences, literal contradictory
all-race headers and all unavailable fields remain accessible in the
[full reference graph](maps/source/full-contract-references.json). Historical
candidate labels and source IDs do not become current keys.

The full149,141,181-byte2020 county original SHA256
`a9d55c618d479aaf9e207d0c49a3511206458756d329c42f830ab52c36930e72`
is independently streamed from its existing ordered lossless gzip parts
32M/32M/32M/6,882,528. It is stored once under the existing news `asset_parts`
references, never as an invented standalone asset. All complete2024 county
groups,2022 precinct/recount originals and archive originals are verified by
measured references. Signed candidate canvass page locators and distinct archive
ballot/registration physical-page locators stay separate. The initial coordinator
wrong-PDF-family check was corrected; worker locators were correct and unchanged.

## Actual county native chains and original precision

The original [Minnehaha precinct parent](https://minnehahacounty.gov/dept/au/election/precinct_info/precinct_info.php)
raw GET returned403. Separate primary web-reader discovery exposed its real
mapbook/app hrefs; these are not falsely attributed to the blocked raw HTML.
The two complete originals are county10,937,333 bytes SHA256
`42606ad9270e39c2d8b3b9b453fe2fa122de2e1867bde65242f6232fd708b6aa`
and city19,816,943 bytes SHA256
`ee6cc86fc72141f93f63f643171d149f39fcc0764023d450a7f355f59b0ecab6`.
They have16 and64 pages; actually inspected complete pages show mapdate3/12/2026.
Their80 paper pages and81 GIS features remain distinct observations.

The actual [county-linked app](https://minnehahacounty.maps.arcgis.com/apps/webappviewer/index.html?id=83db20af25c2402a8390082f51baa059)
configuration selects webmap`7cc5bcba864d4d4781b83b229f2b8819`, whose operational
layer is [Election/Redistricting_2022/MapServer4](https://gis.minnehahacounty.gov/minnemap/rest/services/Election/Redistricting_2022/MapServer/4).
All81 features and full attributes/native geometry are retained, including six
`curveRings` features. Native custom NAD1983 UTM14N WKT explicitly uses **US
survey feet**, not the display map's Mercator CRS. No assumed EPSG is substituted.

The [Pennington official district-map parent](https://www.pennco.org/government/board_of_commissioners/district_maps.php)
links Experience`b03eeb32869e421fa0e92864794728f5`. Its actual configured webmap
`fe799037ba7240e1a5f8c16f12c9ecc0` selects
[gis.rcgov.org AGOL/Voting/MapServer13](https://gis.rcgov.org/server/rest/services/AGOL/Voting/MapServer/13):
53 complete native features, one true curve, native103150/latest6574 US survey
feet. An old embedded child URL404 and two linked original PDF403 bodies remain
in the record. The configured successful layer is not a silent replacement
with an asserted equivalent identity.

Both native snapshots have four total bounded pages, at most50 requested IDs
each. Every returned ID set equals its request, and the union equals the exact
pre/post all-ID/count snapshots. Full layer/edit metadata matches pre/post.
All attributes, XY/CRS/Z/M/curve control objects survive in original response
pages. No output CRS, coordinate rounding, geometry precision, quantization,
generalization parameter, simplification or repair was requested. Preexisting
source generalization remains unknown. [Native QA](maps/qa/native-GIS.json)
preserves schemas, IDs, CRS, complete attributes and feature semantic hashes.
Preview SVG/PNG transforms are separate display derivatives; seven curve
features are explicitly omitted from linear displays, retained in originals.

The unchanged linear native geometry has two invalid features: Minnehaha
OBJECTID80 and Pennington OBJECTID40, both ring self-intersections. Valid linear
subsets yield67 and41 positive-area overlaps, respectively, measured in **square
US survey feet**. Curves/invalid features are excluded from these intersections,
so this is incomplete pair coverage. No source defect is repaired or voted away.
There is no same-vintage legal outline comparison and no legal gap/overlap
certification. Tiny overlaps and larger source overlaps are all listed, without
an invented tolerance that silently deletes them.

## Complete official historical fallback

The actual [Census state directory](https://www2.census.gov/geo/tiger/TIGER2020PL/STATE/)
links South Dakota→46→the complete
[tl_2020_46_vtd20.zip](https://www2.census.gov/geo/tiger/TIGER2020PL/STATE/46_SOUTH_DAKOTA/46/tl_2020_46_vtd20.zip).
Original4,315,722 bytes SHA256
`b48632cb589f4b6c45b5a353fd04e3e9426bbb08503440687960a0498ac06edb`
is retained read-only as one lossless gzip reference, all ZIP members intact.
It has785 native features/all66 counties and505,985 native XY positions.
This is a **Census2020 historical VTD** source, not a2024 reporting boundary or
an approved2026 precinct layer. Yankton has only one countywide VTD; it cannot
supply detailed precinct boundaries there.

The [independent full binary audit](maps/qa/Census-binary-geometry.json.gz) checks
every ZIP member CRC/SHA/size, SHP record/SHX offset/length, all DBF attributes,
parts, rings, original position order/multiplicity and every double's original
bits before geometry adaptation. Installed PyShp3.1.6 constructor semantics
are tested: `points=`/`parts=` preserve positions, while `lines=` closes rings
implicitly and is avoided. No orphan-hole rewriting occurs. Complete PRJ and
original native attributes remain; shape5 has no Z/M. All785 diagnostic polygons
are valid, nonempty and closed, with no positive-area within-county overlap in
native angular XY. Angular square degrees are not land area, and this does not
certify legal/current coverage or absence of gaps against a legal outline.
The [all66 atlas](maps/previews/census-atlas.png) and county SVGs are display aids.

## Complete39-parent investigation

Each row links a local investigation containing complete source routes/errors,
all ordered historical children, acquired shared assets, administrative
supplements and the actual Census county fallback. All66 authorities retain full
SOS directory fields; the other27 parents are retained without a claim of deep
current map investigation. Numbers below count historical observations and
source map features, never approved matches. Every finer entry separately
qualifies physical/combined/absentee/CENTRAL scope in the304 index.

| Priority county parent | Priority / full observations | County map assets | Census2020 VTDs | Source/access/vintage finding |
| --- | ---: | ---: | ---: | --- |
'''
 for f in c['ordered_priority_parent_keys']:
  p=pm[f];text+=f'| [{p["county"]} ({f})](maps/counties/{f}.html) | {len(p["ordered_priority_native_keys"])} / {len(p["ordered_all_native_keys"])} | {len(p["acquired_county_map_assets"])} | {p["fallback"]["native_Census_count"]} | {notes[f]} |\n'
 text+='''
## Offline access, original preservation and QA

The [source inventory](maps/source/source-inventory.json) retains244 complete
receipt envelopes:112 read-only reused originals and132 worker GET attempts.
The latter include full sandbox DNS failures, separately network-enabled GETs,
HTTP errors, empty historical bodies, redirects and headers. Successful PDF
map originals are distinguished from district/registration/polling-location
documents and map-only landing pages. Full errors are never called maps.

Useful original-page inspections include Brown's printed10/20/2025 update versus
its effective10/14/25 filename; Brookings' partly clipped original scan footer;
Spink's February2006 map; Yankton's revised1980 highway base with undated overlay;
Stanley's explicit **Proposed Election Precincts** title; Brule's commissioner
district Option1 (a supplement, not precinct geometry); and Lincoln's complete
polling-place roster rather than a map. The newly successful982 roster access
does not erase the original frozen404/empty receipt. The active-voter summary
is registration, not turnout. All blanks remain source blanks/nulls, not zero.

Poppler rendered **43 distinct complete PDFs /193 pages**, including all107
map-PDF pages, into all-page contact sheets with complete text extraction and
selected large full-page renders. Actual visual scope is narrower: ten complete
original pages, two mapbook contact sheets covering80 thumbnails, the all66
fallback atlas and two native display examples were inspected. Fine-print
accuracy of every thumbnail is not claimed. See [visual record](maps/qa/visual-review.json)
and [PDF inspection](maps/qa/PDF-inspection.json). No browser session was used;
browser availability was not independently tested. Static HTML/SVG/XML/local-link
QA is reported explicitly, without an unseen-browser claim.

Use the [schema/reconstruction instructions](maps/source/SCHEMA.md) for complete
originals and frozen-object resolution. [Acquisition](maps/scripts/acquire.py),
[dependency audit](maps/scripts/audit_dependencies.py), [native/binary audit](maps/scripts/geometry.py),
[build](maps/scripts/build.py), [original reconstruction](maps/scripts/reconstruct.py)
and [validation](maps/scripts/validate.py) are retained. Offline checks verify
exact contract/order/full recursive semantics,691/304/387/all66 coverage,
historical alternatives/companion pins, complete gzip streams, all source
originals/errors, GIS pagination/metadata/curves, every SHP position, PDF page
counts/render assets, local links/anchors, static SVGs and exact owned manifest
membership/hashes. The [validation receipt](maps/qa/validation.json) records the
measured result. Every stored owned and referenced artifact is strictly below
40,000,000 bytes; large source originals use existing lossless compression/splits.
[The exact owned manifest](maps/asset-manifest.json) excludes only its own entry.
The [deterministic replay](maps/qa/reproducibility.json) rebuilds derivatives
without network requests and requires identical measured bytes; exact original
PDF and complete nested-object reconstruction are exercised separately.

The remaining qualifications concern real source access, boundary vintage,
complete physical/current reporting identities, legal effectiveness and an
approved crosswalk. They do not block completion of this historical research.
No absentee/CENTRAL votes are spread over polygons; no unknown residual is
allocated. Current candidate parties/ballot keys, ordinary-write-in law, live
feed identities and future/current geography approval remain separate official
research qualifications. No current returns, changing election-night sequence,
cadence/correction lag, exact remaining votes, forecast or calibrated probability
is inferred from these maps.
'''
 (STATE/'precinct-maps.md').write_text(text)
if __name__=='__main__':main()

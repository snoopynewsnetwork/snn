#!/usr/bin/env python3
"""Render the owned report from frozen index/acquisition/geometry observations."""
import json
from acquire import ROOT,STATE

def build():
    idx=json.loads((ROOT/'index.json').read_text());geo=json.loads((ROOT/'geometry-audit.json').read_text());acq=json.loads((ROOT/'acquisition.json').read_text());src={s['id']:s for s in acq['sources']}
    out=['''# Mississippi precinct and native map references

Research observed October19,2026 UTC. **The offline index contains exactly887
ordered historical source-native entries under77 priority county parents,
with the complete1,736 preferred units and all82 parents visible. Every priority
entry has an acquired qualified shared parent/map reference and a specific
unresolved native-boundary/crosswalk gap. There are zero approved entry-level
geometry matches.** This is a completed bounded reference acquisition and
offline inventory, not complete current legal precinct coverage.

Open the [887-entry index](maps/index.html), [full1,736/82 inventory](maps/inventory.html),
[machine index](maps/index.json), [SVG/PNG/PDF preview atlas](maps/previews/map-preview-atlas.pdf),
[native geometry audit](maps/geometry-audit.json), [complete acquisition log](maps/acquisition.json),
[validation](maps/validation.json) and [owned manifest](maps/manifest.json).
All map references are shared and explicitly qualified. Source-native SEMS grid
columns are observations, not certified precinct polygons, stable source IDs or
approved November reporting units. No parent county replaces an index entry;
no votes are assigned by intersection, fuzzy name, printed code or adjacency.

## Exact scope and complete historical preservation

The complete pinned [turnout contract](data/turnout/priority-set.json) is
13,065,430bytes, SHA256
`782ca7899236ba06e53effee549c4e6845f936c9b4ceea3fecc8828dd9a08c32`.
The [compatibility reference](maps/compatibility.json) retains its entire root
object and resolves complete immutable component bodies recursively, rather
than reducing it to keys. It retains all2321 source columns/84source views,
all global/parent/child/candidate/method/admin/null/alternative fields, full
v1/v2 proposal objects and all17 field-companion bodies. The ordered887 and
full1736 arrays, all82 parent priority-child arrays and source-only locators
are checked against that exact original object. Historical dispatch authority
is external launch authority only; historical worker flags remain unchanged.

The primary volume order is the other seat's **2024ClassI Senate** source
observations, not the separate41-county sensitivity. Source named Senate
denominator is1,215,400 versus signed county1,215,401. Tunica's additional
Pinkins1 remains unallocated. The top15native entries total60,019;
886entries total972,157 and fail80%;887total972,656 crosses80% under either
denominator. The crossing is Lauderdale originalPDF9/physical column5,
literal `450 - Pickard`,119Pinkins+380Wicker=499, visible in the
[fresh original-page render](maps/previews/lauderdale-original-p9.png).
The849remainder entries retain242,744votes. All five parents with no priority
children remain in the full index: Issaquena, Jefferson, Quitman, Sharkey, Tunica.
[Turnout report](turnout.md); [official source index](https://www.sos.ms.gov/elections/electionresults_aspx/elections_results_2024_county.aspx).

The compatibility registry verifies all104 actual2020 publications/selected82
same-seat Senate records and all164 actual2018views, keeping the four-candidate
November6special and two-candidate November27runoff separate. All complete
source objects match their canonical hashes; three literal-X native columns/
six candidate marks stay numerical null, and three administrative columns
stay separate. Leflore2018special Espy minus10 and Tunica2024Pinkins/Harris
minus1 each remain unallocated. OldPike/Coahoma,2020 amendments and vendor
Union/Pike profiles remain nonadditive. No2022 statewide Senate or governor
contest is invented; no cross-year/stage native join follows from counts,
FIPS, names, ordinals or printed codes. [Complete historical dependency](data/turnout/historical-native-complete-dependencies.json);
[partisanship report](county-partisanship.md).

Montgomery's incompatible885ballots observation and Lincoln's corrected15,898
stay source-scoped. Union's58split-style rows retain unknown candidate weights,
not zero. Current SAMPLE Colom/Hyde-Smith/Pinkins candidate labels do not approve
current feed IDs or geometry. All unrelated global contract fields survive
unchanged through the complete canonical reference; this work is not a
calculator/source rebuild, collector, forecast or calibrated probability.

## Acquired primary references and date distinctions

The [MARIS political index](https://maris.mississippi.edu/HTML/DATA/Political.html)
actively links [updated precincts](https://maris.mississippi.edu/HTML/DATA/data_Political/UpdatedVotingPrecincts.html)
for13 counties only. All13 actual2023-labeled ZIPs were already downloaded;
their exact raw/stored hashes were verified before read-only reuse. Their220
features retain complete native archives and all attributes/parts/CRS. MARIS
credits Golden Triangle PDD and individual counties. A2023label and March2023
HTTP modification clock are not adoption/effective/November dates. Unrelated
DFIRM template text on the page is not precinct metadata. Exact disabled links
in the raw official HTML yielded68bounded attempts:64HTTP404 and4connection
failures. No extra successful2023archive was silently inferred. Pearl River
has no county archive link in that list. [Exact shared receipts](maps/shared-map-references.json);
[disabled-link discovery](maps/maris-commented-discovery.json).

The [statewide MARIS2020archive](https://maris.mississippi.edu/MARISdata/Political/MS_VotingPrecincts_2020.zip)
contains1,834 actual Census2020VTD features across82 counties. The
[original metadata PDF](https://maris.mississippi.edu/METAdata/METAdata_Political/MS_VotingPrecincts_2020_meta.pdf)
credits Census, prints publication2021-02-01 and explicitly describes
statistical boundaries rather than legal descriptions. Its2022HTTPfile
modification and2026retrieval are separate dates. It is a qualified historical
parent reference for all887entries, not a frozen2024election-day layer or
current approval. Native MSTM coordinates are metres. Original ZIPbytes,
all1,834records and complete DBF fields are retained; no county subset replaces
the original. [82derived county previews](maps/inventory.html).

Stronger bounded county references are distinct from that fallback:

| Parent | Actual acquired reference | Date/scope and remaining gap |
| --- | --- | --- |
| DeSoto | [Official election maps page](https://www.desotocountyms.gov/537/Election-Maps) → linked app → working [county MapServer1](https://gis.desotocountyms.gov/arcgis/rest/services/Election_Info/MapServer/1); complete154features, all154distinct split IDs,47distinct source PRECINCT_ID values. [Original precinct PDF](https://www.desotocountyms.gov/DocumentCenter/View/49), [render](maps/previews/desoto-voting-map-pdf-p1.png). | PDF visibly prints3/7/2025. Service has finer split fields and2true curves; a feature/ID count does not certify physical precincts or November units. The advertised similarly named FeatureServer returns an HTTP200error. A separately acquired county municipal-ward PDF234 is a Hernando ward reference, not county precinct coverage, and is not assigned to any entry. |
| Harrison | County-hosted [precinct FeatureServer0](https://geo.co.harrison.ms.us/server/rest/services/AGO/HarrisonCounty_VotingPrecincts/FeatureServer/0),49features; county Board/Circuit Clerk/GIS copyright retained. | Description ties adjustments to2010Census. Current adoption/effective/November approval unverified; unavailable item/access attempts remain in receipts. County hosting does not make the historical description current. |
| Lamar | [County page](https://lamarcountyms.gov/ms/) → app/webmap with complete25feature embedded precinct collection; [original county PDF](https://lamarcountyms.gov/ms/wp-content/uploads/2022/08/voting_precincts.pdf), [render](maps/previews/lamar-precinct-pdf-p1.png). | PDF visibly prints08/09/2022. Embedded WebMercator/metre collection has an emptyOBJECTID17/Breland feature alongside its other features. Underlying shapefile/native precision, generalization history, independent service count and edit clock unknown. |
| Lafayette | [Official voting page](https://www.lafayettems.com/voting/) → [actual location PDF](https://lafayettems.com/wp-content/uploads/2026/05/WEBSITE-Lafayette-County-Precinct-Locations-and-Addresses.pdf), [render](maps/previews/lafayette-locations-p1.png). |18location entries, no polygons.2026/05in path is not an adoption/effective date. Oxford/source-label variants are not normalized into matches. |
| Pearl River | [Official county quicklinks](https://pearlrivercounty.net/QuickLinks.aspx) → [two-page DP-009PDF](https://pearlrivercounty.net/DocumentCenter/View/154/Precinct-and-Polling-Location-Report-PDF) plus Find My Polling Place app configuration. | PDF prints09/08/2026, with precinct codes, locations and active-voter counts. It supplies no polygons or certified reporting crosswalk. App configuration names a downstream webmap not acquired here and directs verification with Circuit Clerk. Registration is not votes. |

Madison and Rankin official pages link CMPDD apps whose actual portal requests
failed; Madison's alternate ArcGIS sharing response is an HTTP200access/item
error. Jackson County's official pages link Experience Builder, whose portal
data request returned403. Hancock PDF615returned403in two bounded request
forms. Hinds supervisor-map request failed, election commission returned500,
and Jackson municipal map page404. These are specific access/discovery gaps,
not proof that human users cannot obtain maps. No shell/challenge/error body
is called geometry. Complete request/finalURLs, headers, redirects, status,
UTC and raw/stored hashes include those failures in [acquisition](maps/acquisition.json).
The per-parent table below records the exact attempted primary alternatives
and honestly distinguishes statewide discovery from county followup.

## Native fidelity and measured topology

All14ZIPs passed CRC/member magic/hash checks, SHP/SHX offsets and DBF/shape
count alignment. They contain2,054records. Complete archive bytes, DBF fields,
multipart rings, native coordinate values and CRS units are preserved. DeSoto's
archive/service uses EPSG2255/USsurveyfeet; Harrison EPSG2254/USsurveyfeet;
most MARIS archives use MSTM/metres; Lamar's embedded source uses3857/metres.
No reprojection, coordinate rounding, simplification, quantization, repair or
dropped features was applied to originals. [Archive/native feature audit](maps/geometry-audit.json).

Both county services were acquired with pre metadata/count/allIDs, bounded
50-ID batches, allattributes/fullgeometry, Z/M and true-curves requested,
and post metadata/count/allIDs.154DeSoto and49Harrison IDs reconcile exactly,
with no transfer-limit/error payload admitted and equal pre/post metadata.
No outputCRS, offset, geometryPrecision or quantization was requested.
Native DeSotoOBJECTID15and941 retain complete `curveRings`; they are not
densified. All native JSON remains exact raw response bytes. Native-geodatabase
equivalence/server default precision is not independently established; missing
edit clocks mean stable IDs/metadata cannot exclude unclocked coordinate edits.
[DeSoto proof](maps/source/desoto-native.service-proof.json);
[Harrison proof](maps/source/harrison-native.service-proof.json).

The initial diagnostic adapter failed before assigning polygon points in
PyShp3.1.6. Its exact failed code/audit are preserved in
[history](maps/history/adapter-failure-v1/snapshot.json). Its zero-length
invalid/overlap lists did **not** establish zero defects:2,279linear features
had unavailable topology. The corrected adapter passes fullpoints/parts at
construction, avoids automatic ring closure, verifies every entire original
XYring and coordinate with multiplicity, and rejects orphan-hole reinterpretation.
A multipart/two-shell/one-hole control retains all15positions and area89;
open rings are rejected rather than silently closed. Source fingerprints,
attributes, dimensions and roles match the failed audit for every2,282feature.
No source/calculator was rebuilt. [Repair proof](maps/adapter-repair.json).

The final audit actually evaluates2,279linear geometries. Two are invalid
observations of Love's ring self-intersection: MARISDeSoto record42 and county
serviceOBJECTID43, at native coordinate2419964.924925/1912185.21983941. They
remain unrepaired; this is not a cross-version identity approval. Two true-curve
records and one emptyLamar record remain unavailable for linear topology.
Valid linear features yield221positive-area pair observations across separate
source scopes; these cannot be added as a statewide overlap area. No sliver
tolerance is imposed. The invalid/curve/empty records are excluded from
intersection math only, not from originals/inventory. No certified same-vintage
county outline was acquired, so legal gaps/overlaps remain unknown.

| Source scope | Features | XY topology evaluated | Invalid | Unavailable | Positive-area pairs | Native area units |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
''']
    for a in geo['archives_and_native_sources']:
        d=a['diagnostics'];out.append(f"| {a['source_id']} | {d['feature_count']} | {d['topology_evaluated']} | {len(d['invalid'])} | {len(d['topology_unavailable'])} | {len(d['pairwise_positive_area_intersections'])} | {d['area_units']} |\n")
    out+=['''
Repeated labels, source IDs, counts or similar shapes do not establish a
crosswalk. All1,834VTDs and all valid post-2020 linear features were included
in their same-source diagnostics. Tiny positive numerical areas and larger
DeSoto intersections remain exact diagnostics, not certified slivers or legal
overlaps. See per-pair areas and skipped record IDs in the audit.

## Parent-by-parent qualified coverage and specific gaps

Every row retains the actual number of primary entries and full preferred
children. The acquired2020VTD reference is shared, explicitly historical and
unmatched for each source-native entry; its feature count is not a reporting
unit count. All entry-specific original hashes/pages/physical columns/literal
labels/null codes and full object pointers are in the [887index](maps/index.html)
and [machine inventory](maps/index.json). A parent reference is never887unique
boundaries. No county-site exhaustive search is claimed where discovery was
limited to MARIS and Census.

| Parent/FIPS | Priority/full native children | Shared2020VTD features/preview | Actual primary alternatives and remaining gap |
| --- | ---: | --- | --- |
''']
    for p in idx['all82parents']:
        attempts=[]
        for k in p['primary_attempt_ids']:
            s=src[k]
            if k in ['maris-updated-precinct-parent','maris-2020-precinct-parent']:continue
            attempts.append(f"[{k}]({s['requested_url']}) HTTP{s['status']}"+(' '+s.get('error_type','') if not s['status'] else ''))
        out.append(f"| {p['parent_county']} {p['parent_county_fips']} | {p['priority_count']}/{p['full_count']} | [{p['fallback_feature_count']}features]({p['fallback_preview']}) | "+'; '.join(attempts)+'. '+p['gap'].replace('|','&#124;')+' Discovery: '+p['discovery_depth']+'. |\n')
    out+=['''
## Previews, QA and offline reproduction

There are98SVGshared references:82county VTD previews,13MARIS2023archive
previews,2county service previews and1Lamar embedded-collection preview.
Four PNGcontact sheets cover all98. Original PDFs were rendered separately,
including the dense2025DeSoto map,2022Lamar map, Lafayette location list,
two-page Pearl River roster and scannedLauderdalePDF9. Representative maps,
the scanned crossing page and contact sheets were actually visually inspected.
Display coordinates alone round to0.01viewBox units. The two native curves
and empty feature are explicitly omitted from drawings, retained in originals;
no source-image crop becomes legal geometry. The PDFatlas is a display-only
contact/reference derivative. [Actual visual QA](maps/visual-qa.json).

BrowserQA was attempted: no browser surface was exposed, and native Chrome
returned `cgWindowNotFound`. No unseen browser render is claimed. Static
PyMuPDF/Pillow renders and actual visual inspection are the QA basis. The
offline HTML was structurally checked for the exact887order, complete1736/82
coverage, valid relative links and no remote embeds. Source errors and shells
remain distinguishable from native assets.

Run `python -B senate/2026/mississippi/maps/validate.py` from repository root
for read-only verification. [Build instructions](maps/README.md),
[schema](maps/SCHEMA.md), [acquisition](maps/ACQUISITION.md) and
[exact reconstruction](maps/RECONSTRUCTION.md) preserve complete canonical
dependencies without duplicate originals. Every stored owned file is strictly
below40,000,000bytes. The [manifest](maps/manifest.json) inventories every owned
file except itself. The [validation](maps/validation.json) records complete
contract/source/native/parent equality, native archive/service invariants,
geometry/curve/empty qualifications, links and final manifest hashes.

Remaining current-proof gaps are specific: approvedNovember physical/reporting
roster, adoption/effective dates, exact source-native IDs and split/merger
dictionary, administrative/central/absentee coverage, entry-level polygons,
underlying precision where only an embedded collection exists, source
topology anomalies and same-vintage certified outlines. No legal/current-feed
approval, candidate allocation, forecast or calibrated probability follows.
''']
    (STATE/'precinct-maps.md').write_text(''.join(out));print('report bytes',(STATE/'precinct-maps.md').stat().st_size)

if __name__=='__main__':build()

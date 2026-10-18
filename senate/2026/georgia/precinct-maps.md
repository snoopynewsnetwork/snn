# Georgia downloaded precinct maps

Research snapshot **2026-10-18 UTC**. **All exact44 priority counties have actual downloaded full-resolution2024 precinct geometry**, plus local originals and complete native GIS captures where recovered. The [offline library](maps/index.html) contains44 preview/download cards in the exact **named-four dispatch order**, all159 counties and all2,701 historical source identities. The [county/native pages](maps/inventory.json) preserve1,938 priority and763 nonpriority identities. **No votes are assigned to polygons and no historical/current reporting crosswalk is approved.**

## Scope and frozen authority

The [formal coordinator acceptance](data/coordinator-priority-acceptance.json) accepts the immutable [turnout contract](data/turnout/priority-set.json), SHA256 `1f589d2785d985af2eb33de50adad5a398924ab55f9343deaf79ac5c7378d97a`,2,293,339 bytes. Worker `coordinator_accepted:false` is not the authority. [Input pins](maps/input-pins.json) verify the final turnout/partisanship reports, compatibility CSVs and asset manifests against the supplied freeze hashes. All original795 county selected payloads remain read-only through those manifests; maps reuses and pins the159 original2024 county payloads without copying them.

The four named2024 presidential options total5,250,047; complete valid state universe is5,250,905 with858 qualified write-ins lacking county/native/method allocation. [Coordinator proof](data/coordinator-priority-membership-review.json) establishes exact top44 **membership and minimum cardinality**, with dispatch using the named-four order, not full-candidate order. Top15 named votes2,939,795; first43 named4,199,292; named44 votes4,222,572. Even any43 plus all858 is4,200,150, below the complete-universe integer80% threshold4,200,724. Liberty's23,258 ballot ceiling is below Habersham's23,280 named votes; every other outsider is at most22,353+858=23,211. Full-candidate internal/all159 order and exact shares remain unknown; no write-ins are allocated. Priority full-share bounds remain80.41608066–80.43242070%.

Keep election stages separate:2024 president named4=5,250,047;2020 regular ClassII Senate=4,952,175;January2021 same-ClassII runoff=4,484,902;November2022 other-ClassIII Senate=3,935,924;December2022 runoff=3,541,877. House Clerk hybrid recapitulations are not single-stage totals. Original app election/contest IDs and clocks stay in pinned sources/native contexts. Older four elections have no returned native rows and unusable raw zero ballot/registration placeholders; those are unavailable, not zero turnout.

## Actual official statewide original

The [General Assembly reapportionment page](https://www.legis.ga.gov/joint-office/reapportionment) initially returns an Angular shell. Its actual published main client defines the anonymous bootstrap and `Reapportionment/Page` catalog request. The acquired catalog's **Statewide Voting Precincts(2024)** entry links the actual [precinct ZIP](https://www.legis.ga.gov/api/document/docs/default-source/reapportionment-document-library/precincts/gaprec_2024-website-shapefile.zip?sfvrsn=7b38ca99_2). Both the public authority/discovery chain and original download are retained in [receipts](maps/sources.html); the initial401 catalog request is retained separately from the successful authorized anonymous-client request. This is actual precinct data, not a Census VTD, county outline or legislative-district replacement. The [GIO official page](https://gio.ga.gov/) -> linked state data hub route was also inspected; its searched organization exposed no precinct data.

Download [the complete original ZIP](maps/originals/state-2024-precinct-zip.zip): **16,477,511 bytes**, SHA256 `4d48e5ba8849cad20809580c3ef56c81c516ef26878a3378be83847394271a8a`. Its actual contents are SHP/SHX/DBF/PRJ, all CRC-tested and member-hashed in [archive inspection](maps/extracts/archive-inspection.json). SHP, SHX and DBF each contain**2,724 rows**. **2,697 rows have explicit county FIPS spanning all159 counties;27 have blank FIPS, county/precinct IDs/names and remain unassigned.** Their DISTRICT values, source row positions and complete geometries remain in the [unmatched extract](maps/extracts/state2024-unmatched-native-geometry.json.gz) and [preview](maps/previews/state2024-unmatched.svg). Prefixes such as121SC21A,215FTBEN and029FTSTEW are retained without assigning county membership or votes.

Native CRS is literal NAD83 geographic WKT, with XY longitude/latitude in degrees; full extent**[-85.605165,30.355757,-80.78296,35.001303]**. All**1,775,333 vertices and3,436 parts** remain in the original. Source type5 polygons have linear2D geometry without Z/M/curves. Every native field, identifier and attribute remains in the ZIP and [all-row attribute inventory](maps/extracts/state2024-all-attributes.csv). Selected county geometry JSON retains every point/part/attribute and exact original ordinal, with no clipping, simplification, repair or transformed coordinates. Previews are separate derivatives rounded only to display pixels.

The44 selections contain**1,934 explicit-FIPS map rows versus1,938 historical native result identities**. Even matching counts would not establish equivalence. There are also27 unassigned shapes outside those county selections. The catalog's2024 vintage is not independent proof of the exactNovember2024 legal or reporting geometry, and cannot authorize2026 use.

## Exact44 download index

Every county name opens its source-native detail page. Each card in the [offline index](maps/index.html) links its full coordinate/attribute extraction and the one shared statewide original. These are reference maps; local/source vintage findings and all attempted routes are in the [precise gap inventory](maps/gaps.json) and [county research](maps/county-research.json).

| Named-four dispatch rank | County | FIPS |2024 explicit-FIPS map rows |2024 app native identities | Additional actual originals / local snapshots |
|---:|---|---|---:|---:|---|
| 1 | [Fulton County](maps/counties/13121.html) | 13121 | 463 | 466 | [fulton-current](maps/extracts/fulton-current-service-native.json.gz) |
| 2 | [Gwinnett County](maps/counties/13135.html) | 13135 | 156 | 156 | [gwinnett-current](maps/extracts/gwinnett-current-service-native.json.gz) |
| 3 | [Cobb County](maps/counties/13067.html) | 13067 | 148 | 148 | [cobb-precinct-pdf](maps/originals/cobb-precinct-pdf.pdf) |
| 4 | [DeKalb County](maps/counties/13089.html) | 13089 | 191 | 191 | [dekalb-current](maps/extracts/dekalb-current-service-native.json.gz) |
| 5 | [Cherokee County](maps/counties/13057.html) | 13057 | 42 | 43 | [cherokee-current-pdf](maps/originals/cherokee-current-pdf.pdf); [cherokee-precinct-pdf](maps/originals/cherokee-precinct-pdf.pdf) |
| 6 | [Chatham County](maps/counties/13051.html) | 13051 | 87 | 87 | 2024 reference; current/local original gap |
| 7 | [Forsyth County](maps/counties/13117.html) | 13117 | 29 | 29 | [forsyth-current-large-retry](maps/originals/forsyth-current-large-retry.pdf); [forsyth-current-small-retry](maps/originals/forsyth-current-small-retry.pdf); [forsyth-june-notice-retry](maps/originals/forsyth-june-notice-retry.pdf) |
| 8 | [Henry County](maps/counties/13151.html) | 13151 | 37 | 37 | 2024 reference; current/local original gap |
| 9 | [Clayton County](maps/counties/13063.html) | 13063 | 70 | 70 | [clayton-current](maps/extracts/clayton-current-service-native.json.gz) |
| 10 | [Hall County](maps/counties/13139.html) | 13139 | 31 | 31 | [hall-current](maps/extracts/hall-current-service-native.json.gz) |
| 11 | [Paulding County](maps/counties/13223.html) | 13223 | 21 | 21 | [paulding-current-retry](maps/extracts/paulding-current-retry-service-native.json.gz) |
| 12 | [Columbia County](maps/counties/13073.html) | 13073 | 46 | 46 | [columbia-2026-notice-24](maps/originals/columbia-2026-notice-24.pdf); [columbia-2026-notice-100](maps/originals/columbia-2026-notice-100.pdf); [columbia-2026-boundary-text](maps/originals/columbia-2026-boundary-text.pdf); [columbia-2026-map24](maps/originals/columbia-2026-map24.pdf); [columbia-2026-map100](maps/originals/columbia-2026-map100.pdf) |
| 13 | [Coweta County](maps/counties/13077.html) | 13077 | 24 | 24 | [coweta-current](maps/extracts/coweta-current-service-native.json.gz) |
| 14 | [Richmond County](maps/counties/13245.html) | 13245 | 68 | 68 | 2024 reference; current/local original gap |
| 15 | [Houston County](maps/counties/13153.html) | 13153 | 17 | 17 | 2024 reference; current/local original gap |
| 16 | [Muscogee County](maps/counties/13215.html) | 13215 | 25 | 25 | [muscogee-current](maps/extracts/muscogee-current-service-native.json.gz) |
| 17 | [Fayette County](maps/counties/13113.html) | 13113 | 36 | 36 | [fayette-current](maps/extracts/fayette-current-service-native.json.gz) |
| 18 | [Douglas County](maps/counties/13097.html) | 13097 | 25 | 25 | [douglas-precinct-pdf](maps/originals/douglas-precinct-pdf.pdf) |
| 19 | [Bibb County](maps/counties/13021.html) | 13021 | 31 | 31 | 2024 reference; current/local original gap |
| 20 | [Carroll County](maps/counties/13045.html) | 13045 | 28 | 28 | [carroll-2026-pdf](maps/originals/carroll-2026-pdf.pdf); [carroll-2024-pdf](maps/originals/carroll-2024-pdf.pdf) |
| 21 | [Newton County](maps/counties/13217.html) | 13217 | 19 | 19 | 2024 reference; current/local original gap |
| 22 | [Walton County](maps/counties/13297.html) | 13297 | 19 | 19 | [walton-2026-pdf](maps/originals/walton-2026-pdf.pdf) |
| 23 | [Bartow County](maps/counties/13015.html) | 13015 | 17 | 17 | 2024 reference; current/local original gap |
| 24 | [Clarke County](maps/counties/13059.html) | 13059 | 24 | 24 | 2024 reference; current/local original gap |
| 25 | [Lowndes County](maps/counties/13185.html) | 13185 | 18 | 18 | [lowndes-precinct-pdf](maps/originals/lowndes-precinct-pdf.pdf) |
| 26 | [Jackson County](maps/counties/13157.html) | 13157 | 4 | 4 | [jackson-precinct-pdf](maps/originals/jackson-precinct-pdf.pdf); [jackson-consolidated-pdf](maps/originals/jackson-consolidated-pdf.pdf) |
| 27 | [Rockdale County](maps/counties/13247.html) | 13247 | 16 | 16 | [rockdale-2023-pdf](maps/originals/rockdale-2023-pdf.pdf); [rockdale-2019-pdf](maps/originals/rockdale-2019-pdf.pdf) |
| 28 | [Floyd County](maps/counties/13115.html) | 13115 | 19 | 19 | [floyd-legacy-pdf](maps/originals/floyd-legacy-pdf.pdf) |
| 29 | [Barrow County](maps/counties/13013.html) | 13013 | 8 | 8 | [barrow-precinct-pdf](maps/originals/barrow-precinct-pdf.pdf) |
| 30 | [Glynn County](maps/counties/13127.html) | 13127 | 17 | 17 | [glynn-2026-pdf](maps/originals/glynn-2026-pdf.pdf); [glynn-current](maps/extracts/glynn-current-service-native.json.gz) |
| 31 | [Whitfield County](maps/counties/13313.html) | 13313 | 23 | 23 | [whitfield-precinct-pdf](maps/originals/whitfield-precinct-pdf.pdf) |
| 32 | [Effingham County](maps/counties/13103.html) | 13103 | 20 | 20 | 2024 reference; current/local original gap |
| 33 | [Catoosa County](maps/counties/13047.html) | 13047 | 11 | 11 | 2024 reference; current/local original gap |
| 34 | [Dougherty County](maps/counties/13095.html) | 13095 | 25 | 25 | [dougherty-current](maps/extracts/dougherty-current-service-native.json.gz) |
| 35 | [Spalding County](maps/counties/13255.html) | 13255 | 17 | 17 | 2024 reference; current/local original gap |
| 36 | [Bulloch County](maps/counties/13031.html) | 13031 | 16 | 16 | [bulloch-current](maps/extracts/bulloch-current-service-native.json.gz) |
| 37 | [Walker County](maps/counties/13295.html) | 13295 | 11 | 11 | 2024 reference; current/local original gap |
| 38 | [Troup County](maps/counties/13285.html) | 13285 | 13 | 13 | [troup-2026-pdf](maps/originals/troup-2026-pdf.pdf) |
| 39 | [Gordon County](maps/counties/13129.html) | 13129 | 12 | 12 | [gordon-precinct-pdf](maps/originals/gordon-precinct-pdf.pdf) |
| 40 | [Oconee County](maps/counties/13219.html) | 13219 | 8 | 8 | 2024 reference; current/local original gap |
| 41 | [Camden County](maps/counties/13039.html) | 13039 | 11 | 11 | [camden-precinct-pdf](maps/originals/camden-precinct-pdf.pdf); [camden-adoption-pdf](maps/originals/camden-adoption-pdf.pdf) |
| 42 | [Bryan County](maps/counties/13029.html) | 13029 | 10 | 10 | 2024 reference; current/local original gap |
| 43 | [Laurens County](maps/counties/13175.html) | 13175 | 15 | 15 | [laurens-linked-map-pdf](maps/originals/laurens-linked-map-pdf.pdf) |
| 44 | [Habersham County](maps/counties/13137.html) | 13137 | 6 | 6 | 2024 reference; current/local original gap |

## Local originals, approval evidence and exclusions

**Forsyth has actual election-specific documentary evidence.** The [current official precinct page](https://www.forsythco.com/government/departments-a-z/voter-registrations-elections/polling-places-precincts/) says July/August2026 approved changes take effect with theNovember2026 General/Special election: South Forsyth(21) eliminated, boundary changes to Big Creek(01), Johns Creek(35), Daves Creek(38), and29 Election Day precincts. The actual downloaded [large original](maps/originals/forsyth-current-large-retry.pdf) explicitly prints “Precincts and Polling Places effective with the November3,2026 General Election & Special Elections”; its [letter-size original](maps/originals/forsyth-current-small-retry.pdf) is retained too. Initial CDN timeouts and stale Portals404s remain separate; bounded retries recovered complete originals. This establishes the publication/effective-date claim, **not a crosswalk to2024 app GUIDs**. The June notice is a separate earlier proposal, not substituted for the final page/map.

**Glynn:** [official election maps page](https://www.glynncounty.org/government/departments/elections-voter-registration/voting-maps-districts) explicitly says Board adopted mapsJanuary14,2026 and links the acquired [17,270,409-byte high-resolution original](maps/originals/glynn-2026-pdf.pdf). The14-feature service retains mixed2019/2025 descriptive clocks and actual update attributes. Adoption is recorded separately from November reporting equivalence.

**Columbia:** the original January2026 notices say boundary changes *may become finalFebruary24*; acquired partial maps still say Option1/Option2/proposed. No final approval was inferred from the current webpage heading. **Walton:** acquired actual2026 precinct map; the official-results peer reports the official Broken Arrow-to-Walnut Grove merger. **Jackson:** acquired16-old-precinct and four-consolidated-zone PDFs with2017 metadata; peer'sFebruary20,2026 final order concerns polling places, not a geographic/result crosswalk. These older/current contexts remain separate.

**Fayette:** actual contents of the linked Commission Districts app/webmap expose a separate Voter Precincts layer; its full36-feature data was acquired. Commission district polygons themselves are excluded. **Douglas:** actual2025 original contains a distinct25-precinct panel alongside legislative/school panels; only its precinct panel qualifies as precinct reference. **Whitfield:**265 native attribute rows omit geometry in multiple complete-ID captures; they are not counted as downloaded geometry. Its original2025 precinct PDF and state2024 geometry remain explicit fallbacks.

**Scans and vintage:** current Cherokee GIS link is a43-page map book withApril2025 PDF metadata and no extractable text; real pages were rendered and inspected. Its separate42-page2015 book remains historical. Cobb's actual original visually says2026 Voting Precincts. Gordon's linked scan visibly says2014. Lowndes' URL saysJan2018 but the actual original printsMarch2020 and implementedMay18,2009. The county sources do not make these2026 maps by linking them today. Laurens' actual downloaded sheet includes voting-precinct areas/panel alongside roads and municipal insets; retained intact.

All**30 PDFs /152 pages** were rendered into [real-page previews/contact sheets](maps/qa/pdf-inspection.json), including notices and help documents that are not counted as precinct assets. [Visual review](maps/qa/visual-review.json) records the actually inspected originals/scans. No available browser surface was exposed for browser-rendered HTML QA; the index has offline structural/link validation and direct SVG/PDF visual review.

## Complete local native service captures and topology

There are**12 complete local precinct service snapshots, totaling1,044 feature rows** across those separate counties. Actual authority pages -> app/webmap -> literal layer URLs are retained. Each snapshot has advertised count, all IDs before and after,100-ID bounded batches, exact per-batch membership and transfer-limit checks, metadata before/after and original native CRS/attributes/geometries. Omitted geometry and failed connections remain explicit. [Service inspection](maps/service-inspection.json) records raw response batches and detailed diagnostic feature IDs; no service is treated as a November returns feed.

| Native service | Features | Invalid | Positive-area intersection pairs | Largest pair area | Actual native area units |
|---|---:|---:|---:|---:|---|
| [bulloch-current](maps/services/bulloch-current.json) | 16 | 0 | 27 | 16977.642 | square metre; planar native-coordinate diagnostic |
| [clayton-current](maps/services/clayton-current.json) | 69 | 0 | 22 | 56.6088718 | square metre; planar native-coordinate diagnostic |
| [coweta-current](maps/services/coweta-current.json) | 24 | 0 | 2 | 13.9784275 | square US survey foot; planar native-coordinate diagnostic |
| [dekalb-current](maps/services/dekalb-current.json) | 191 | 0 | 39 | 329.955405 | square metre; planar native-coordinate diagnostic |
| [dougherty-current](maps/services/dougherty-current.json) | 25 | 0 | 15 | 33668.1534 | square US survey foot; planar native-coordinate diagnostic |
| [fayette-current](maps/services/fayette-current.json) | 36 | 0 | 0 | 0 | square US survey foot; planar native-coordinate diagnostic |
| [fulton-current](maps/services/fulton-current.json) | 437 | 0 | 247 | 434.390623 | square US survey foot; planar native-coordinate diagnostic |
| [glynn-current](maps/services/glynn-current.json) | 14 | 0 | 17 | 8826.26372 | square metre; planar native-coordinate diagnostic |
| [gwinnett-current](maps/services/gwinnett-current.json) | 156 | 0 | 56 | 0.112333359 | square US survey foot; planar native-coordinate diagnostic |
| [hall-current](maps/services/hall-current.json) | 31 | 0 | 2 | 0.0104750483 | square US survey foot; planar native-coordinate diagnostic |
| [muscogee-current](maps/services/muscogee-current.json) | 25 | 0 | 0 | 0 | square US survey foot; planar native-coordinate diagnostic |
| [paulding-current-retry](maps/services/paulding-current-retry.json) | 20 | 0 | 0 | 0 | square metre; planar native-coordinate diagnostic |

The [whole-state original diagnostics](maps/geometry-diagnostics.json) find**zero null/empty, nonfinite or GEOS-invalid shapes and zero positive-area pair intersections** among all2,724 original state rows. This includes the27 unknown-context shapes. The priority selections likewise have no such defects. Local service snapshots have positive-area intersections as listed, ranging from very small numerical/sliver intersections to material overlaps; originals remain unrepaired. The diagnostics retain exact feature ID pairs and areas. Metre/US-survey-foot values are **native planar projection units**, including Web Mercator where advertised, not automatically ground area. Square-degree state checks are not ground area either. Pair sums can double-count triple coverage. No legal adjacency-gap or cross-vintage coverage proof is asserted.

## Native results and source gaps

The [all2,701 context records](maps/extracts/native-contexts.jsonl.gz) retain complete contract constituents, original precinct and turnout objects/pointers, county election/jurisdiction objects, native GUIDs/ordinals/localized labels, source clocks and original hashes. Administrative/combined/style semantics remain unverified. `isVirtual:false`, `mapFeatureId:null`, label/ID/count agreement, polling points or ballot splits do not establish physical equivalence. Every historical result identity remains unjoined until reviewed documentary mapping exists.

Fulton's40 candidate nulls and130 counties'22,416 method nulls remain missing; no residuals are filled or allocated. JSON candidate/method arrays are retained in read-only originals. Source candidate nativeId/party18 differences remain separate scopes. Dawson's De la Cruz13/West6 void options stay separate from valid named-four votes and858 qualified write-ins; raw county all-options5,250,066 is not valid-state5,250,905.2024 ballots5,297,264 and registration7,219,868 remain source controls with registration status/date unspecified.

The [peer observation record](maps/peer-observations.json) preserves the separately recovered app XLSX scope. The peer's actual [Fulton original bytes](data/results-sources/raw/observed-export-fulton2024-0-0.body.gz) and [HTTP receipt](data/results-sources/raw/observed-export-fulton2024-0-0.http.json) identify a762,229-byte XLSX recovered through the published `/cdn/results/` + jurisdiction GUID + literal blobName route. Original ZIP CRC was checked read-only. Its [40-position alternative-source ledger](data/results-sources/extracts/fulton-alternative-native-nulls.json) retains every app GUID/pointer and XLSX row; all40 positions were checked against the frozen app JSON and remain null there. Separate export values total18 votes (Trump7,Harris11), while the peer reports466 unique exact2024 labels and agreement on all1,824 mutually known cells. Match scope is same2024 county label + English option name, not GUID or geometry equivalence. Transport Last-Modified is2025-01-30T14:00:22Z versus app asOf2025-01-02T19:04:20.416202Z and lastUpdated2024-11-13T14:01:20.0063939Z. These are distinct source vintages. The export does **not** replace frozen JSON nulls or authorize geographic joining. The state export supplies no county write-in allocation. These peer paths are observational read-only references, not newly frozen build dependencies; only final immutable peer artifacts may be pinned. No official-results ledgers were edited.

Every44 county has an actual downloaded2024 reference asset. Remaining gaps are individually named in [gaps.json](maps/gaps.json): current boundary originals where inaccessible or not exposed; exact older/current legal vintage; proposals without final adoption; Whitfield omitted geometry; and historical/result/November reporting crosswalks for **all44 counties and all2,701 native identities**. Chatham dynamic configuration404, Newton403, Bryan GIS connection failure, Catoosa403, Clayton/Dougherty parent challenges, Paulding legacy404 and transient/recovered failures are preserved. County-specific alternatives and successful fallback assets remain distinct. No Census VTD, county outline, polling point, screenshot or viewer shell substitutes for precinct geometry.

## Reproduction and freeze checks

See [full schema/reproduction](maps/SCHEMA.md), [all source receipts](maps/sources.csv), [artifact manifest](maps/manifest.json) and [offline validation](maps/validation.json). Scripts acquire immutable originals, reconstruct exact entities, extract all coordinates/native contexts, render real PDF pages, build44 ordered cards/all159 detail pages, and validate hashes/ZIP structure/full scopes/nulls/bounds/service coverage/relative links. Every stored artifact is strictly below40,000,000 bytes, with no dependency/cache trees or duplicate giant originals. Original files are never clipped, simplified, repaired or truncated.

Offline commands: `PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/georgia/maps/scripts/build.py`; then `report.py` and `validate.py` in the same scripts directory. Rendering uses `render.py`; manifest regeneration after an authorized owned change uses `validate.py --update-manifest`. Acquisition/reconstruction commands are documented separately so refresh observations cannot silently replace this snapshot.

No current results feed, publication cadence, completion denominator, remaining-vote count, collector or calibrated Needle is inferred from these maps. The coordinator owns publication; this worker wrote only this report and `maps/**` and performed no Git operations.

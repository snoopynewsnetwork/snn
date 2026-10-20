from common import *
from build import slug

def report():
 inv=load('maps/inventory.json.gz');geo=load('maps/qa/geography.json.gz');pubs=load('maps/renders/index.json');binary=load('maps/qa/binary-summary.json')
 text='''# Oregon precinct maps — bounded research, 2026-10-20

All **36 parent authority chains**, **510 complete known2024 source contexts** and **31 unavailable native-parent cases** are retained in the [offline atlas](maps/index.html). Actual assets include18 complete native snapshots, three actual SHP layers, a complete107-PDF map archive and other whole county map/legal/election publications. Current legal/result-leaf approval remains unavailable. **Zero inferred current result-leaf polygon joins; no spatial allocation of votes, registration or ballots.** Coordinator alone reviews, accepts and publishes.

The [external source authority](data/coordinator-source-research-acceptance.json) was independently byte-verified and fully consumed in memory; downstream ownership retains its **path only**. The frozen contract was independently byte-verified. Preflight sequencing deviation: the first tool listed candidate paths before verification; the next action verified both whole files before acquired research or owned writes. [History](maps/history/research-history.json) records this candidly.

## Scope and complete source reconstruction

Oregon has no2024 Senate contest.2024 president retains all seven named choices plus genericMisc: **2,244,493** reported votes, including15,026Misc whose eligible named-write-in scope remains unknown. Five known parents retain510 literal source records: Multnomah107, Washington155, Clackamas118, Marion118 and Wasco12. Their1,128,521 votes, known-only top15=112,024 and descriptive known-only213/904,600 after212/902,447 do not establish statewide native80. The unclosed31parents retain **1,115,972** votes and unknown native membership. County11/1,814,630 is a separate sensitivity, never map dispatch. Canonical statewide complete native order/top15/min80/priority/remainder remain **NULL**; null priority did not produce an empty job or synthetic541native units.

[Independent source replay](maps/qa/source-replay.json) checks all23 roots,1994 whole companions,495672 complete recursive objects, four ordered ledgers,5029 fixed whole-file pins and5261 historical records. Its1012011 checks are independent implementation accounting and exclude optional coordinator-review dependencies. [Original reconstruction](maps/qa/original-reconstruction.json) restores113 whole original entities including all72 historical ZIP members, from48 fixed receipts and37 individually reconstructed receipt bodies. Every full original candidate/party/header/null/mask/method/admin/control/raw-position/parent object remains accessible by exact immutable reference through the [resolver](maps/scripts/resolve.py), including old path+hash bodies instead of later current files. No producer writer, mutable newsroom aggregate/current helper/peer directory or optional current map/source/coordinator review is a build input.

2020 Senate is sameClassII;2022 Senate is otherClassIII, and2022 Governor retains its substantial third-candidate field. All36county controls remain. Complete ZIP membership is distinct from partial historical normalization. The separate262-page Benton2020 federal original differs from the115-page ZIP state-office member; separate2022 full189-page original remains. Producer historical closures/differences remain literal, including Douglas's unclosed candidate/control disagreements. Lane's post2023 public redaction/request gap remains without outreach. Washington OCR/source row positions and nonvote301104-vs301105, and Wasco1831-vs1830 scopes remain source evidence, never spatial allocation controls. Clackamas combined115/116 remains one literal source record with two constituents, no allocation; printed119precincts is separate.

## Actual assets, scope and access

[Inventory](maps/inventory.json.gz) links404 map-owned requests plus115 independently hash-verified individual official navigation receipts. All requests/redirects/headers/status/error bodies/timestamps/source clocks and raw/stored size/hash/ordered-part recipes remain. Source observation and reuse times, printed vintage, HTTP clocks, GIS edit times and ZIP dates are separate. Failure bodies are retained; missing metadata is not fabricated. Bodies remain once by content-addressed hash, with each stored part strictly<40,000,000bytes. The largest part is39,000,000bytes. No truncation, login/challenge/TLS bypass, guessed layer IDs or thumbnail-ID stripping occurred.

The [SOS county directory](https://sos.oregon.gov/elections/Pages/countyofficials.aspx) and [Blue Book county chain](https://sos.oregon.gov/blue-book/government/Pages/local-county.aspx) lead to the actual county authorities. Literal map/GIS/app/item/webmap/layer relations are retained in individual receipts. [Multnomah's map page](https://multco.us/info/maps-and-data-multnomah-county-elections) supplies the complete2024 individual-map ZIP and separate2022 split SHP ZIP. Its linked2024 Google Drive page is retained as HTML, **not** an acquired SHP ZIP. [Union Elections](https://unioncountyor.gov/county-clerk/elections/) supplies the actual PDF and SHP ZIP. [Lane's literal2022 map page](https://www.lanecounty.org/cms/One.aspx?portalId=3585881&pageId=18322980) supplies complete county/Eugene/Springfield maps and adjacent-precinct companion.

Baker has TLS issuer failures; Curry and several Jefferson/Linn/Douglas originals have403 access failures; Harney307 lacks a usable exposed Location; Morrow's literal page/PDF and Columbia's countywide PDF fail without acquired complete bodies. Marion's exact public app item/data return JSON errors. Hood River's exact custom app script route404 is retained. These are source-specific access limits, not absence-of-geography findings. Other county publications and their narrower scopes are detailed below and in the atlas. The literal Wheeler Wix image is only a display derivative; no full-size original was invented.

The complete [Census2020 VTD directory](https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/VTD/2020/) has no Oregon county entries. The acquired [Census2010 Oregon county ZIP](https://www2.census.gov/geo/tiger/TIGER2010/COUNTY/2010/tl_2010_41_county10.zip),36 features, is historical **county context**; its full FIPS set independently matches all36 parents. The complete ODOT36-feature native county service is separate state parent context. Neither supplies a current precinct, child/result-ID, physical-site or same-vintage legal outline.

## Complete native snapshots

Each of18 snapshots retains full pre/post service **and layer** metadata/count/allIDs and at-most50-ID all-attribute native geometry pages. All54 requested/returned page sets/counts reconcile across2174 **nonadditive feature records**. All18 full pre/post comparisons, including service extents, were unchanged during their captured intervals; this is not an atomic or November guarantee. No outCRS/outSR, precision, quantization, simplification, generalization, offset paging or source repair was used. Original XY/Z/M/true curves, null/empty/invalid/open/short structures remain intact.

| Snapshot | Features | Native CRS identity | Linear preview exclusions |
| --- | ---: | --- | --- |
'''
 for key,snap in inv['native_snapshots'].items():
  g=next(l for l in geo['layers'] if l['key']==key);sr=snap.get('native_crs') or {};crs='Original WKT' if 'wkt'in sr else str(sr.get('wkid','unknown'))+' / latest '+str(sr.get('latestWkid','unknown'));exc={k:v for k,v in g['counts'].items() if 'excluded'in k};text+=f'| [{key}](maps/native/{key}.json) | {snap.get("feature_count")} | {crs} | {exc or "none"} |\n'
 text+='''
Benton split service returns all66 attribute records but **no geometry**; this is explicit missing geometry, not a completed polygon acquisition.19of21 Benton precincts contain curves. Across overlapping native layers,246 curved feature records,66 missing geometries and four empty/nonpolygon geometries are excluded from linear-only previews/topology.38 nonsimple source rings across native/binary layers are retained diagnostics. [Ring proof](maps/qa/geography.json.gz) tests source closure/shortness/simplicity only. No orphan-hole reinterpretation, source repair or polygon-intersection/legal-gap/overlap/sliver certification was performed. Blank preview areas can reflect excluded curves. [Previews](maps/previews/binary-census-oregon-county2010.svg) are separate stroke-only derivatives; source coordinates remain exact.

GIS precincts/splits, legal precincts, result units, municipality/ward, ballot styles and physical/drop sites are distinct.121Clackamas GIS features do not identify118 historical result rows;282Washington features do not identify155 scanned result records;300Multnomah2024 splits differ from196historical2022 SHP features and107result contexts. Even Wasco's12generalized features matching12source rows does not establish identity;164clerk splits are a separate scope. Every known/unavailable context carries its precise source-specific access/vintage/CRS/physical/legal/finer-ID gaps.

## Binary audit, rendering and actual visual scope

[Independent binary proofs](maps/qa/binary-summary.json) audit every CRC/size/hash of128 members in four actual ZIPs. Three SHP layers contain253 records: Census36, Multnomah196, Union21. Every DBF schema/cell/record, SHP/SHX record index/offset/part/bbox and **416,896 XY IEEE754 values** is independently checked against raw bytes and PyShp;5,183DBF cells are retained in the proof. The installed [PyShp3.1.6 constructor](maps/history/pyshp-constructor.txt) was inspected first: points/parts preserve raw positions/multiplicity while lines can auto-close. No orphan-hole conversion or repair occurs. JSON-only layers make no binary SHP/DBF/SHX claim.

[Complete PDF rendering](maps/renders/index.json) covers135 whole acquired PDFs and **416 pages**, including all107PDF map-archive members. Whole originals, full text, metadata/page dimensions and render pins are retained separately; [browse every page](maps/publications.html). Manual inspection was exactly six selected original map pages—Clatsop countywide, Umatilla page1, Multnomah4501, Benton April2024, Lane countywide, Tillamook—and five geographic previews. [Actual visual scope](maps/qa/visual-review.json) states the limits: remaining pages automatic only, dense labels not all manually transcribed, no browser render claim. Umatilla page1 prints3/20/2026/reference-only; Multnomah4501 prints10/29/2024 and subdivisionsA/B/C; these visual labels do not authorize result joins.

## Every parent remains substantive

The following links expose complete original parent/child/admin arrays, exact immutable references, shared resources and individual access/vintage/CRS/physical/legal/finer-ID findings. A zero in the known-source column means **unavailable native membership**, not zero precincts or zero work.

| Parent | Known source contexts | Bounded map finding |
| --- | ---: | --- |
'''
 for p in inv['parents']:
  short=p['map_findings'].split('. ')[0]+'.';text+=f'| [{p["county"]}](maps/parents/{slug(p["county"])}.html) | {p["known_source_context_count"]} | {short} |\n'
 text+='''
## Offline checks and frozen handoff

The [schema/reconstruction/reproduction document](maps/SCHEMA.md) specifies whole originals, source-format roles, all36/510/31coverage, native/binary checks, static atlas DOM/order/full-object/escaping tests and meaningful corruption fixtures. The static atlas uses **no JavaScript** and requires no server/network; county/known/unavailable navigation provides tested static filters. No browser-specific layout claim is made.

```sh
PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/oregon/maps/scripts/audit.py
```

The command is offline/read-only and independently replays full authority-referenced source bodies, exact historical resolvers, original map receipts/parts, full native/binary/PDF reconstruction, deterministic atlas/previews, relative links and strict size coverage. [Fixtures](maps/qa/fixtures.json), [validation](maps/qa/validation.json), [history](maps/history/research-history.json) and [finalseal](maps/finalseal.json) are included in the [manifest](maps/asset-manifest.json), which excludes **only itself**. No reverse manifest hash cycle exists. After sealing, complete membership/hashes are checked read-only and owned bytes remain frozen.

Bounded map research is complete with explicit external qualifications: current/legal geography, result-leaf/choice/reporting IDs, eligible named write-ins, November returns/live counts, measured cadence, eligible outstanding votes, forecast and calibration approvals remain false or unknown. These are not indefinite research-completion gates. No live collector/probability implementation was authorized or built. Coordinator alone accepts and publishes.
'''
 return text.encode()
if __name__=='__main__':(S/'precinct-maps.md').write_bytes(report())

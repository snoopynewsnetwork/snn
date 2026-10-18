#!/usr/bin/env python3
"""Build the final report, source index, explicit gap inventory and review facts."""
import csv, html, json, pathlib
from acquire import ROOT, STATE, dump, entity,read_record
from build import page

def main():
    inv=json.loads((ROOT/'inventory.json').read_text());priority=sorted([x for x in inv if x['named_four_dispatch_rank']],key=lambda x:x['named_four_dispatch_rank'])
    receipts=[json.loads(p.read_text()) for p in sorted((ROOT/'receipts').glob('*.json'))]
    rr=[];sourcehtml=[]
    for r in receipts:
        rr.append(dict(id=r['id'],parent=r.get('parent'),requested_url=r['requested_url'],final_url=r.get('final_url'),retrieved_start_utc=r['retrieved_start_utc'],retrieved_end_utc=r['retrieved_end_utc'],status=r.get('status'),content_type=r['headers'].get('Content-Type',r['headers'].get('content-type')),http_last_modified=r['headers'].get('Last-Modified',r['headers'].get('last-modified')),entity_bytes=r['entity_bytes'],entity_sha256=r['entity_sha256'],storage_paths=';'.join(s['path'] for s in r['storage']),receipt=f'receipts/{r["id"]}.json'))
        sourcehtml.append(f'<tr><td><a href="receipts/{r["id"]}.json">{r["id"]}</a></td><td>{html.escape(str(r.get("status")))}</td><td>{html.escape(str(r.get("parent")))}</td><td><a href="{html.escape(r["requested_url"])}">{html.escape(r["requested_url"])}</a></td><td>{r["entity_bytes"]}</td><td>{r["retrieved_end_utc"]}</td></tr>')
    with (ROOT/'sources.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rr[0].keys());w.writeheader();w.writerows(rr)
    (ROOT/'sources.html').write_text(page('Georgia map source receipts','<h1>Original source captures</h1><p><a href="index.html">Map library</a>. Failed attempts and original successes remain separate; HTTP status alone does not determine map scope.</p><table><tr><th>Receipt</th><th>HTTP</th><th>Parent</th><th>Requested URL</th><th>Entity bytes</th><th>Retrieved UTC</th></tr>'+''.join(sourcehtml)+'</table>'))
    services=json.loads((ROOT/'service-inspection.json').read_text());ok=[s for s in services if s['status']=='complete' and s['geometry_key_count']>0]
    gaps=[]
    for x in priority:
        local=x['local_research'];gaps.append(dict(county_key=x['county_key'],county_name=x['county_name'],named_four_dispatch_rank=x['named_four_dispatch_rank'],reference_asset=f'extracts/{x["county_fips"]}-state2024-native-geometry.json.gz',reference_rows=x['state_map2024_fips_rows'],historical_native_identities=x['source_native2024_count'],finding=local['finding'],exact_missing_scope=local['exact_gap'],documentary_status=x['documentary_status'],attempt_receipt_ids=local['attempt_receipt_ids'],service_ids=local['service_ids'],original_pdf_assets=local['assets'],result_geography_join_status='all historical identities unmatched to geometry pending approved crosswalk'))
    dump(ROOT/'gaps.json',gaps)
    rows=[]
    for x in priority:
        local=x['local_research'];assets='; '.join(f'[{pathlib.Path(p).stem}](maps/{p})' for p in local['assets'])
        for s in local['service_ids']:assets+=('; ' if assets else '')+f'[{s}](maps/extracts/{s}-service-native.json.gz)'
        if not assets:assets='2024 reference; current/local original gap'
        rows.append(f'| {x["named_four_dispatch_rank"]} | [{x["county_name"]}](maps/counties/{x["county_fips"]}.html) | {x["county_fips"]} | {x["state_map2024_fips_rows"]} | {x["source_native2024_count"]} | {assets} |')
    st=[]
    for s in ok:
        d=s.get('geometry_diagnostics',{});a=[x['area'] for x in d.get('positive_area_overlap_pairs',[])]
        st.append(f'| [{s["id"]}](maps/services/{s["id"]}.json) | {s["captured_count"]} | {len(d.get("invalid_rows",[]))} | {len(a)} | {max(a) if a else 0:.9g} | {d.get("area_units")} |')
    d=json.loads((ROOT/'geometry-diagnostics.json').read_text());w=d['whole_state'];qa=json.loads((ROOT/'qa/pdf-inspection.json').read_text());countpdf=len(qa);pages=sum(x['page_count'] for x in qa)
    report=f'''# Georgia downloaded precinct maps

Research snapshot **2026-10-18 UTC**. **All exact44 priority counties have actual downloaded full-resolution2024 precinct geometry**, plus local originals and complete native GIS captures where recovered. The [offline library](maps/index.html) contains44 preview/download cards in the exact **named-four dispatch order**, all159 counties and all2,701 historical source identities. The [county/native pages](maps/inventory.json) preserve1,938 priority and763 nonpriority identities. **No votes are assigned to polygons and no historical/current reporting crosswalk is approved.**

## Scope and frozen authority

The [formal coordinator acceptance](data/coordinator-priority-acceptance.json) accepts the immutable [turnout contract](data/turnout/priority-set.json), SHA256 `1f589d2785d985af2eb33de50adad5a398924ab55f9343deaf79ac5c7378d97a`,2,293,339 bytes. Worker `coordinator_accepted:false` is not the authority. [Input pins](maps/input-pins.json) verify the final turnout/partisanship reports, compatibility CSVs and asset manifests against the supplied freeze hashes. All original795 county selected payloads remain read-only through those manifests; maps reuses and pins the159 original2024 county payloads without copying them.

The four named2024 presidential options total5,250,047; complete valid state universe is5,250,905 with858 qualified write-ins lacking county/native/method allocation. [Coordinator proof](data/coordinator-priority-membership-review.json) establishes exact top44 **membership and minimum cardinality**, with dispatch using the named-four order, not full-candidate order. Top15 named votes2,939,795; first43 named4,199,292; named44 votes4,222,572. Even any43 plus all858 is4,200,150, below the complete-universe integer80% threshold4,200,724. Liberty's23,258 ballot ceiling is below Habersham's23,280 named votes; every other outsider is at most22,353+858=23,211. Full-candidate internal/all159 order and exact shares remain unknown; no write-ins are allocated. Priority full-share bounds remain80.41608066–80.43242070%.

Keep election stages separate:2024 president named4=5,250,047;2020 regular ClassII Senate=4,952,175;January2021 same-ClassII runoff=4,484,902;November2022 other-ClassIII Senate=3,935,924;December2022 runoff=3,541,877. House Clerk hybrid recapitulations are not single-stage totals. Original app election/contest IDs and clocks stay in pinned sources/native contexts. Older four elections have no returned native rows and unusable raw zero ballot/registration placeholders; those are unavailable, not zero turnout.

## Actual official statewide original

The [General Assembly reapportionment page](https://www.legis.ga.gov/joint-office/reapportionment) initially returns an Angular shell. Its actual published main client defines the anonymous bootstrap and `Reapportionment/Page` catalog request. The acquired catalog's **Statewide Voting Precincts(2024)** entry links the actual [precinct ZIP](https://www.legis.ga.gov/api/document/docs/default-source/reapportionment-document-library/precincts/gaprec_2024-website-shapefile.zip?sfvrsn=7b38ca99_2). Both the public authority/discovery chain and original download are retained in [receipts](maps/sources.html); the initial401 catalog request is retained separately from the successful authorized anonymous-client request. This is actual precinct data, not a Census VTD, county outline or legislative-district replacement. The [GIO official page](https://gio.ga.gov/) -> linked state data hub route was also inspected; its searched organization exposed no precinct data.

Download [the complete original ZIP](maps/originals/state-2024-precinct-zip.zip): **16,477,511 bytes**, SHA256 `4d48e5ba8849cad20809580c3ef56c81c516ef26878a3378be83847394271a8a`. Its actual contents are SHP/SHX/DBF/PRJ, all CRC-tested and member-hashed in [archive inspection](maps/extracts/archive-inspection.json). SHP, SHX and DBF each contain**2,724 rows**. **2,697 rows have explicit county FIPS spanning all159 counties;27 have blank FIPS, county/precinct IDs/names and remain unassigned.** Their DISTRICT values, source row positions and complete geometries remain in the [unmatched extract](maps/extracts/state2024-unmatched-native-geometry.json.gz) and [preview](maps/previews/state2024-unmatched.svg). Prefixes such as121SC21A,215FTBEN and029FTSTEW are retained without assigning county membership or votes.

Native CRS is literal NAD83 geographic WKT, with XY longitude/latitude in degrees; full extent**[-85.605165,30.355757,-80.78296,35.001303]**. All**{w['vertices']:,} vertices and{w['parts']:,} parts** remain in the original. Source type5 polygons have linear2D geometry without Z/M/curves. Every native field, identifier and attribute remains in the ZIP and [all-row attribute inventory](maps/extracts/state2024-all-attributes.csv). Selected county geometry JSON retains every point/part/attribute and exact original ordinal, with no clipping, simplification, repair or transformed coordinates. Previews are separate derivatives rounded only to display pixels.

The44 selections contain**1,934 explicit-FIPS map rows versus1,938 historical native result identities**. Even matching counts would not establish equivalence. There are also27 unassigned shapes outside those county selections. The catalog's2024 vintage is not independent proof of the exactNovember2024 legal or reporting geometry, and cannot authorize2026 use.

## Exact44 download index

Every county name opens its source-native detail page. Each card in the [offline index](maps/index.html) links its full coordinate/attribute extraction and the one shared statewide original. These are reference maps; local/source vintage findings and all attempted routes are in the [precise gap inventory](maps/gaps.json) and [county research](maps/county-research.json).

| Named-four dispatch rank | County | FIPS |2024 explicit-FIPS map rows |2024 app native identities | Additional actual originals / local snapshots |
|---:|---|---|---:|---:|---|
{chr(10).join(rows)}

## Local originals, approval evidence and exclusions

**Forsyth has actual election-specific documentary evidence.** The [current official precinct page](https://www.forsythco.com/government/departments-a-z/voter-registrations-elections/polling-places-precincts/) says July/August2026 approved changes take effect with theNovember2026 General/Special election: South Forsyth(21) eliminated, boundary changes to Big Creek(01), Johns Creek(35), Daves Creek(38), and29 Election Day precincts. The actual downloaded [large original](maps/originals/forsyth-current-large-retry.pdf) explicitly prints “Precincts and Polling Places effective with the November3,2026 General Election & Special Elections”; its [letter-size original](maps/originals/forsyth-current-small-retry.pdf) is retained too. Initial CDN timeouts and stale Portals404s remain separate; bounded retries recovered complete originals. This establishes the publication/effective-date claim, **not a crosswalk to2024 app GUIDs**. The June notice is a separate earlier proposal, not substituted for the final page/map.

**Glynn:** [official election maps page](https://www.glynncounty.org/government/departments/elections-voter-registration/voting-maps-districts) explicitly says Board adopted mapsJanuary14,2026 and links the acquired [17,270,409-byte high-resolution original](maps/originals/glynn-2026-pdf.pdf). The14-feature service retains mixed2019/2025 descriptive clocks and actual update attributes. Adoption is recorded separately from November reporting equivalence.

**Columbia:** the original January2026 notices say boundary changes *may become finalFebruary24*; acquired partial maps still say Option1/Option2/proposed. No final approval was inferred from the current webpage heading. **Walton:** acquired actual2026 precinct map; the official-results peer reports the official Broken Arrow-to-Walnut Grove merger. **Jackson:** acquired16-old-precinct and four-consolidated-zone PDFs with2017 metadata; peer'sFebruary20,2026 final order concerns polling places, not a geographic/result crosswalk. These older/current contexts remain separate.

**Fayette:** actual contents of the linked Commission Districts app/webmap expose a separate Voter Precincts layer; its full36-feature data was acquired. Commission district polygons themselves are excluded. **Douglas:** actual2025 original contains a distinct25-precinct panel alongside legislative/school panels; only its precinct panel qualifies as precinct reference. **Whitfield:**265 native attribute rows omit geometry in multiple complete-ID captures; they are not counted as downloaded geometry. Its original2025 precinct PDF and state2024 geometry remain explicit fallbacks.

**Scans and vintage:** current Cherokee GIS link is a43-page map book withApril2025 PDF metadata and no extractable text; real pages were rendered and inspected. Its separate42-page2015 book remains historical. Cobb's actual original visually says2026 Voting Precincts. Gordon's linked scan visibly says2014. Lowndes' URL saysJan2018 but the actual original printsMarch2020 and implementedMay18,2009. The county sources do not make these2026 maps by linking them today. Laurens' actual downloaded sheet includes voting-precinct areas/panel alongside roads and municipal insets; retained intact.

All**{countpdf} PDFs /{pages} pages** were rendered into [real-page previews/contact sheets](maps/qa/pdf-inspection.json), including notices and help documents that are not counted as precinct assets. [Visual review](maps/qa/visual-review.json) records the actually inspected originals/scans. No available browser surface was exposed for browser-rendered HTML QA; the index has offline structural/link validation and direct SVG/PDF visual review.

## Complete local native service captures and topology

There are**{len(ok)} complete local precinct service snapshots, totaling{sum(s['captured_count'] for s in ok):,} feature rows** across those separate counties. Actual authority pages -> app/webmap -> literal layer URLs are retained. Each snapshot has advertised count, all IDs before and after,100-ID bounded batches, exact per-batch membership and transfer-limit checks, metadata before/after and original native CRS/attributes/geometries. Omitted geometry and failed connections remain explicit. [Service inspection](maps/service-inspection.json) records raw response batches and detailed diagnostic feature IDs; no service is treated as a November returns feed.

| Native service | Features | Invalid | Positive-area intersection pairs | Largest pair area | Actual native area units |
|---|---:|---:|---:|---:|---|
{chr(10).join(st)}

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
'''
    (STATE/'precinct-maps.md').write_text(report)
    print(json.dumps(dict(source_receipts=len(receipts),complete_local_services=len(ok),complete_local_features=sum(s['captured_count'] for s in ok),pdfs=countpdf,pages=pages)))

if __name__=='__main__':main()

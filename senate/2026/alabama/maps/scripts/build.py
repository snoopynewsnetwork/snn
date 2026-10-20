"""Deterministic offline catalogue/atlas/report. No network, producer imports or writers."""
from pathlib import Path
from collections import Counter
import json,gzip,hashlib,html,csv,io,re,sys
ROOT=Path(__file__).resolve().parents[1];S=ROOT.parent
CONTRACT={'path':'data/turnout/priority-set.json','bytes':15257023,'sha256':'a3d53415e3379a512b88a1f5f81506ac337a92f45870dd616038b9e23bf71850'}
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}
def read(p):return json.loads(p.read_bytes())
def body(receipt):
 r=read(ROOT/receipt);e=r.get('entity')
 if not e:return r,b''
 ps=[]
 for p in e['parts']:
  b=(ROOT/p['path']).read_bytes();assert len(b)==p['bytes'] and sha(b)==p['sha256'];ps.append(b)
 b=gzip.decompress(b''.join(ps));assert len(b)==e['bytes'] and sha(b)==e['sha256'];return r,b

def build(out):
 out=Path(out);out.mkdir(exist_ok=True,parents=True)
 inputs=read(ROOT/'build-inputs.json')
 for p in inputs['files']:assert pin(ROOT/p['path'])==p
 cb=(S/CONTRACT['path']).read_bytes();assert len(cb)==CONTRACT['bytes'] and sha(cb)==CONTRACT['sha256'];c=json.loads(cb)
 def put(name,b):
  if isinstance(b,str):b=b.encode()
  assert len(b)<40000000,name
  p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 files={r['path'] for r in inputs['files']};receiptpaths=sorted(p for p in files if p.startswith('source/') and p.endswith('.receipt.json'))
 catalogue=[];raw={}
 for p in receiptpaths:
  r,b=body(p);e=r.get('entity');fmt='PDF' if b.startswith(b'%PDF') else 'ZIP' if b.startswith(b'PK\x03\x04') else 'PNG' if b.startswith(b'\x89PNG') else 'JPEG' if b.startswith(b'\xff\xd8') else 'JSON' if b.lstrip().startswith((b'{',b'[')) else 'other_or_unavailable'
  row={'receipt':p,'requested_url':r['requested_url'],'method':r['method'],'fields':r['fields'],'request_body':r['request_body'],'utc_start':r['utc_start'],'utc_end':r['utc_end'],'final_url':r['final_url'],'status':r['status'],'original_bytes':e['bytes'] if e else None,'original_sha256':e['sha256'] if e else None,'format_by_magic':fmt,'stored_parts':e['parts'] if e else [],'hop_count':len(r['hops']),'metadata_unavailable':r.get('unavailable_metadata'),'role':'Original source observation, including errors and discovery-history bodies. Not an admitted current map or reporting unit.'}
  catalogue.append(row);raw[p]=(r,b)
 put('original-catalogue.json',dump(catalogue))
 output=io.StringIO();w=csv.writer(output);w.writerow(['receipt','method','requested_url','final_url','status','utc_start','utc_end','original_bytes','original_sha256','format_by_magic','stored_parts_json'])
 for r in catalogue:w.writerow([r[k] for k in ['receipt','method','requested_url','final_url','status','utc_start','utc_end','original_bytes','original_sha256','format_by_magic']]+[json.dumps(r['stored_parts'],separators=(',',':'))])
 put('manifest.csv',output.getvalue())
 chains=[(p,read(ROOT/p)) for p in sorted(files) if p.startswith('county-chains/') and p.endswith('.json')]
 dirs={r['county']:r for r in read(ROOT/'directory-observations.json')};assetobs=read(ROOT/'map-asset-observations.json');census=read(ROOT/'census-observations.json');census_by={r['county_fips']:r for r in census}
 statezip=json.loads(gzip.decompress((ROOT/'zip-audit/53b9d0d160451e58df45ec5bfa4ff1cfbb1b452bf617a30ee04c66a2131bfb6b.json.gz').read_bytes()));ds=statezip['datasets'][0];idx=[f['name'] for f in ds['fields']].index('COUNTYFP20');vtdcounts=Counter('01'+r['values'][idx] for r in ds['records']);assert len(vtdcounts)==67
 parents=[];priority=set(c['ordered_priority_keys']);units=c['units'];unitrows=[]
 for p in c['parents']:
  county=p['county'];us=[u for u in units if u['county_fips']==p['county_fips']];cc=[{'path':path,'observations':chain['observations'],'bound':chain.get('bound'),'unfetched_queue':chain.get('unfetched_queue',[])} for path,chain in chains if chain['county']==county]
  aa=[o for o in assetobs if o['county']==county];downloaded=[o for o in aa if o['status']==200 and raw[o['receipt']][1].startswith((b'%PDF',b'PK\x03\x04',b'\x89PNG',b'\xff\xd8'))]
  source_formats=Counter(next(r['format_by_magic'] for r in catalogue if r['receipt']==o['receipt']) for o in downloaded)
  entry={'county':county,'county_fips':p['county_fips'],'complete_original_parent':p,'ordered_source_rank_children':[u['key'] for u in us],'ordered_priority_children':[u['key'] for u in us if u['key'] in priority],'ordered_remainder_children':[u['key'] for u in us if u['key'] not in priority],'directory':dirs[county],'county_investigations':cc,'map_asset_observations':aa,'downloaded_map_asset_count':len(downloaded),'downloaded_formats':dict(source_formats),'historical_tiger2020pl':census_by[p['county_fips']],'statewide_cartographic_vtd2020_count':vtdcounts[p['county_fips']],'statewide_cartographic_role':'Complete67-parent fallback context, source generalization1:500000; never native polygon coverage or current legal approval.','native_service_capture':'native-service-captures.json' if county=='Madison' else None,'historical_result_label_polygon_match':None,'current_2026_ID_crosswalk':None,'administrative_unit_polygon_assumption':False,'qualification':('County chain inspected through exact public anchors; complete bodies, source-native asset names and observed errors retained. ' if cc else 'No county commission website published in the inspected ACCA county links and no bounded source-map anchor established; exact SOS local-office fields and complete native source contexts retained. ')+'Downloaded district/parent/site sources are not automatically precinct boundaries. Source creation/filename/printed vintage does not establish effective/adopted boundaries. No numeric-label alias or spatial allocation.'}
  parents.append(entry)
  for u in us:unitrows.append((u,entry))
 assert len(parents)==67 and sum(bool(p['ordered_priority_children']) for p in parents)==63
 put('county-investigations.json',dump(parents))
 flags={'historical_source_only':True,'current_geography_approved':False,'legal_geography_approved':False,'physical_precinct_identity_approved':False,'current_reporting_choice_IDs_approved':False,'current_leaf_mapping_approved':False,'November_votes_admitted':False,'legal_native80_approved':False,'eligible_named_writein_universe_approved':False,'live_cadence_approved':False,'exact_remaining_pool_approved':False,'collector_approved':False,'forecast_approved':False,'calibration_approved':False,'result_label_polygon_join':None,'remaining_pool':None}
 put('admission.json',dump(flags))
 mask=[];pby={p['county_fips']:p for p in parents}
 output=io.StringIO();w=csv.writer(output);w.writerow(['rank','key','county','county_fips','tier','native_label','method_context','source_member','member_sha256','source_sheet','column_1based','full_contract_context_pointer','county_investigation_pointer','historical_polygon_match','current_ID_crosswalk','reported_candidate_marks'])
 for i,u in enumerate(units):
  parent=pby[u['county_fips']];j=parents.index(parent);tier='priority' if i<887 else 'remainder';ctx='/units/'+str(i);ip='/'+str(j)
  mask.append({'key':u['key'],'tier':tier,'full_contract_context_pointer':ctx,'county_investigation_pointer':ip,'administrative_context':u['key'] in c['administrative_contexts'],'geometry_match':None})
  w.writerow([i+1,u['key'],u['county'],u['county_fips'],tier,u['native_label'],u['method_context'],u['source_member'],u['member_sha256'],u['source_sheet'],u['column_1based'],ctx,ip,'unknown','unknown',u['reported_candidate_votes']])
 put('native-context-index.csv',output.getvalue());put('coverage.json',dump({'contract':CONTRACT,'authority_path':'data/coordinator-priority-acceptance.json','full_order':c['full_order'],'priority_order':c['ordered_priority_keys'],'remainder_order':c['remainder_keys'],'masks':mask,'all67_parent_order':c['parents'],'priority_parent_order':list(dict.fromkeys(u['county_fips'] for u in units[:887])),'coverage':c['coverage'],'admission':flags}))
 pdfindex=read(ROOT/'pdf-index.json');pdfunique={r['original_sha256']:read(ROOT/r['pages_metadata']) for r in pdfindex};pdfpages=sum(len(v['pages']) for v in pdfunique.values())
 texts=[]
 for h,m in sorted(pdfunique.items()):
  text=gzip.decompress((ROOT/m['text_path']).read_bytes()).decode('utf-8')
  lines=[{'line_1based':i+1,'literal':s} for i,s in enumerate(text.splitlines()) if re.search(r'precinct|polling|map produced|map created|effective|adopted|disclaimer|202[0-9]',s,re.I)]
  texts.append({'original_sha256':h,'full_text_path':m['text_path'],'source_pdf_metadata':m['pdf_metadata'],'literal_matching_text_lines':lines,'printed_or_filename_vintage_is_not_adoption':True,'effective_date':None,'adopted_date':None})
 put('map-vintage-observations.json',dump(texts))
 # All unmodified contract contexts appear as escaped text in details, never as executable script.
 e=lambda s:html.escape(str(s),quote=True)
 page=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Alabama historical map research atlas</title><style>body{font:16px system-ui;margin:2rem;color:#173c46;background:#f7faf9}main{max-width:1200px;margin:auto}h1{font-size:2.1rem}label{display:inline-block;margin:.5rem}input,select{font:inherit;padding:.4rem}details{background:white;border:1px solid #ccd9d9;margin:.5rem 0;padding:.65rem}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}summary{cursor:pointer}.badge{font-size:.8rem;color:#455}img{max-width:48%;vertical-align:top}a{color:#075b73}[hidden]{display:none!important}</style><main><h1>Alabama historical map research</h1><p>2,085 original reporting contexts · 887 priority · 1,198 remainder · 67 counties / 63 priority parents.</p><p>No result-label polygon joins, current/legal geography approval or spatial vote allocation. Administrative columns remain literal source contexts.</p><p><a href="../precinct-maps.md">Report</a> · <a href="manifest.csv">Original catalogue CSV</a> · <a href="county-investigations.json">Complete county investigations</a> · <a href="native-service-captures.json">Native service originals</a></p><img src="previews/census-2020-vtd-context.svg" alt="2020 Census VTD historical context, not native coverage"><img src="previews/madison-source-precincts.svg" alt="Madison source-labelled2026 precincts, current/legal compatibility unknown"><p>Separate native-coordinate previews. Census source product is generalized1:500000; no result joins.</p><label>County <select id="county"><option value="">All counties</option>']
 for p in parents:page.append('<option value="'+e(p['county_fips'])+'">'+e(p['county'])+'</option>')
 page.append('</select></label><label>Scope <select id="tier"><option value="">Full universe</option><option value="priority">Priority887</option><option value="remainder">Remainder1198</option></select></label><label>Search <input id="query" type="search"></label><p id="count" aria-live="polite">2085 of2085 contexts</p><section id="units">')
 for i,u in enumerate(units):
  tier='priority' if i<887 else 'remainder';parent=pby[u['county_fips']]
  page.append('<details class="unit" id="unit-'+str(i+1)+'" data-key="'+e(u['key'])+'" data-county="'+u['county_fips']+'" data-tier="'+tier+'" data-search="'+e((u['key']+' '+u['county']+' '+u['native_label']).lower())+'"><summary>'+str(i+1)+'. '+e(u['county'])+' · '+e(u['native_label'])+' <span class="badge">'+tier+' / '+e(u['method_context'])+'</span></summary><p>Full original contract context /units/'+str(i)+'; <a href="#parent-'+u['county_fips']+'">qualified county investigation</a>. Polygon match unknown.</p><pre class="context">'+e(json.dumps(u,ensure_ascii=False,separators=(',',':')) )+'</pre></details>')
 page.append('</section><h2>All county parents and investigations</h2>')
 for p in parents:page.append('<details class="parent" id="parent-'+p['county_fips']+'"><summary>'+e(p['county'])+' · '+str(len(p['ordered_priority_children']))+' priority / '+str(len(p['ordered_remainder_children']))+' remainder</summary><pre class="parent-context">'+e(json.dumps(p,ensure_ascii=False,separators=(',',':')) )+'</pre></details>')
 page.append('<h2>Full remaining original contract context</h2>')
 for k,v in c.items():
  if k in ['units','parents']:continue
  page.append('<details class="root-context" data-root="'+e(k)+'"><summary>'+e(k)+'</summary><pre>'+e(json.dumps(v,ensure_ascii=False,separators=(',',':')) )+'</pre></details>')
 page.append('<h2>Complete native service feature objects</h2>')
 for layer in read(ROOT/'native-service-captures.json'):
  for p in layer['pages']:
   _,b=body(p['receipt']);data=json.loads(b)
   for i,f in enumerate(data['features']):page.append('<details class="native-feature"><summary>'+e(layer['layer_url'].split('/')[-3])+' · '+e(str(f['attributes'].get(layer['pre']['object_id_field'])))+'</summary><p>Exact source page '+e(p['receipt'])+'; no historical label join.</p><pre>'+e(json.dumps(f,ensure_ascii=False,separators=(',',':')) )+'</pre></details>')
 page.append('''<script>
const county=document.getElementById('county'),tier=document.getElementById('tier'),query=document.getElementById('query'),counter=document.getElementById('count');
const rows=Array.from(document.querySelectorAll('details.unit'));
function applyFilters(){let count=0;const q=query.value.toLowerCase();for(const row of rows){const match=(!county.value||row.dataset.county===county.value)&&(!tier.value||row.dataset.tier===tier.value)&&(!q||row.dataset.search.includes(q));row.hidden=!match;if(match)count++;}counter.textContent=`${count} of ${rows.length} contexts`;const url=new URL(location.href);for(const [k,v] of [['county',county.value],['tier',tier.value],['q',query.value]]){if(v)url.searchParams.set(k,v);else url.searchParams.delete(k);}history.replaceState(null,'',url);return count;}
const params=new URL(location.href).searchParams;const selected=params.get('county');if(Array.from(county.options).some(o=>o.value===selected))county.value=selected;const t=params.get('tier');if(['priority','remainder'].includes(t))tier.value=t;query.value=params.get('q')||'';for(const el of [county,tier,query])el.addEventListener('input',applyFilters);applyFilters();
</script></main></html>''')
 put('index.html',''.join(page))
 summary={'receipts':len(catalogue),'response_statuses':dict(Counter(str(r['status']) for r in catalogue)),'unique_original_entities':len(set(r['original_sha256'] for r in catalogue if r['original_sha256'])),'unique_pdfs':len(pdfunique),'all_pdf_pages':pdfpages,'manual_wholepages':3,'source_zip_audits':len({x['audit'] for x in read(ROOT/'zip-audit-index.json')}),'all67_statewide_context':True,'county_asset_observations':len(assetobs),'counties_with_downloaded_map_assets':sum(p['downloaded_map_asset_count']>0 for p in parents),'native_polygon_historical_joins_approved':0,'all_priority_contexts_with_full_source_and_county_investigation':887}
 put('research-summary.json',dump(summary))
 report='''# Alabama precinct maps: bounded original-source research

Observed 2026-10-20 UTC. The [offline atlas](maps/index.html) retains every complete historical native/parent/context object and the exact full, priority and remainder orders. [Original catalogue](maps/manifest.csv), [complete county investigations](maps/county-investigations.json), [schema/reproduction](maps/SCHEMA.md) and [qualifications](maps/admission.json) accompany actual downloaded assets. Sole coordinator review/acceptance/publication remains separate.

The external historical authority is [path-only](data/coordinator-priority-acceptance.json). The exact frozen input is [the turnout contract](data/turnout/priority-set.json), 15,257,023 bytes, SHA-256 `a3d53415e3379a512b88a1f5f81506ac337a92f45870dd616038b9e23bf71850`. Producer flags remain unchanged. [Independent full authority replay](maps/authority-validation.json) checks29 roots,303 whole companions,1,608,035 ordered recursive objects in11 complete partitions,612 fixed files,634 full historical body resolvers/7 archives, all original receipts and every parent array. [Independent workbook replay](maps/xls-source-validation.json) reopens all201 original XLS members and compares6,246,656 complete typed cells and85,129 native source positions over6,270 historical contexts.

## Historical scope and map compatibility

The primary2024 presidential source has2,085 typed native columns and2,265,090 complete six-column named/generic candidate marks. Top15 supplies115,428. The preceding886 contexts total1,811,981 against integer80% threshold1,812,072;887 totals1,812,818, crossing at Calhoun OAK GROVE BAPT, column30,837 marks. All1,198 remainder contexts and452,272 marks remain. The priority spans63 counties; all67 parents retain full/priority/remainder child arrays. [Native context index](maps/native-context-index.csv) binds every entry to its own complete source context and county investigation. Counties never substitute for native columns, and administrative observations are not asserted to be physical precincts.

2022 Senate2,074/1,414,238 and2020 same-ClassII Senate2,111/2,316,445 remain distinct; Alabama had no2024 Senate contest. Candidate marks are not ballots, registration or legally eligible named write-ins. Generic8,738 write-ins do not establish that universe. The baseline's prior statewide label-aggregation error was corrected from its own Jefferson Stein row12(994)/Oliver row13(731); native/county source vectors were already correct, and all earlier scripts/claims remain retained. Three PDF blank/dash candidate cells remain null beside separately observed XLS zeros. Cleburne2024 ballot difference-180, Cullman2022+90, raw registration zero/blanks and missing under/over scopes remain unallocated.

## Actual assets and source vintage

[Madison ArcGIS organization's precinct app](https://madisoncountyal.maps.arcgis.com/apps/webappviewer/index.html?id=f5608d0c95ef41cd83ee34558992dab9) resolves through the inspected client constructor, complete application configuration and returned web-map ID to source-labelled2026 Precincts and2026 Polling Locations. [Complete service captures](maps/native-service-captures.json) retain79 polygons and78 actual published points, both full service/layer pre/post metadata/count/ALL-ID bodies, disjoint pages of at most50 IDs, every attribute/native coordinate and Z/M/true-curve request. Requested/returned ID sets reconcile; service/layer metadata and ordered IDs were unchanged. Native CRS is retained with each body; no outSR, precision reduction, quantization, simplification or generalization parameter was sent. Source-native objects and point locations are shown separately without historical result joins. Source filename/title2026 does not establish an effective/adopted boundary or November/current ID crosswalk. [Publisher-chain qualification](maps/source-authority-qualification.json): the preserved official.gov homepage links the same ArcGIS organization for a different application. The specific precinct app was discovered by public search; its exact current election-office inbound anchor/endorsement remains unestablished. This qualification limits the official-source claim while preserving the complete observed app/service chain.

The [full2020 TIGER/Line VTD index](https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/VTD/2020/) supplied45 complete county ZIPs;22 other requests returned full429 challenge responses, retained without bypass. The separately [published Census cartographic product](https://www.census.gov/geographies/mapping-files/2020/geo/carto-boundary-file.html) supplied the complete Alabama1:500,000 VTD ZIP:1,837 native records covering all67 county identifiers. This product is source-generalized historical context. It is not a full-resolution substitute for missing TIGER files, native reporting-unit polygon coverage or current/legal boundaries. [Full ZIP/member/SHP/SHX/DBF/PRJ/CPG/XML audits](maps/zip-audit-index.json) retain member CRCs/hashes, every field descriptor/token/value/deletion/null, record and SHX offset/length, part/bbox and every XY IEEE754 bit checked against independently inspected installed pyshp3.1.6 constructors before adaptation. Parts, duplicate positions and order survive unchanged.

[Geometry diagnostics](maps/geometry-diagnostics.json.gz) retain invalid/empty/nonpolygon/unclosed/orphan-hole/duplicate/overlap observations unrepaired in native coordinate units. Polygon constructor checks skip unclosed source rings; no buffer/repair, legal coverage, sliver or gap certification occurs. SVGs are separate previews; original geometry remains exact. No votes, ballots or registration are spatially allocated.

[PDF originals and page inventories](maps/pdf-index.json) preserve complete source bodies, all-page Poppler text, exact parser/render warnings and automatic whole-page images. Manual actual whole-page visual inspection was limited to page1 of Etowah's2023 precinct map, Shelby's precincts/voting-centers map and Mobile's voter-precinct map. [Explicit image/detail readings](maps/manual-visual-observations.json) record fullpage and selected dense-label/fineprint scope. Etowah's central00101-00111 labels remain source-scoped. Shelby prints production February25,2026 and an acquired-source accuracy disclaimer; Mobile prints creation3/10/2026 and legal/engineering/survey and accuracy limitations. Printed production/creation dates are distinct from adoption/effectiveness. No unseen-browser or all-page manual visual claim is made. All other pages were automatically rendered and retain full text/originals.

## All67 county investigations

All63 actual priority-parent chains have county-specific bounded official-page/directory/map-source observations. The exact source-native map assets, failed bodies, status, request chain and remaining queues are retained. A count below includes downloaded county map/PDF/image/district/site context, not approved native boundary coverage. Complete statewide fallback and every administrative/remainder case remain even where a county website or precinct download was unavailable.

|County|FIPS|Priority / remainder contexts|Downloaded county map assets|Full TIGER request|Qualified map gap|
|---|---|---:|---:|---|---|
'''
 for p in parents:
  gap='Historical-label/current-ID join unknown; no polygon allocated to administrative columns.'
  if not p['downloaded_map_asset_count']:gap='No actual county map asset established in bounded chain; statewide VTD context retained; native/physical/current match unknown.'
  report+='|'+p['county']+'|'+p['county_fips']+'|'+str(len(p['ordered_priority_children']))+' / '+str(len(p['ordered_remainder_children']))+'|'+str(p['downloaded_map_asset_count'])+'|'+str(p['historical_tiger2020pl']['status'])+'|'+gap+'|\n'
 report+='''
## Offline QA and reproducibility

[Negative fixtures](maps/negative-validation.json) reject30 actual full-input corruptions covering truncation, whole contexts, native/admin/candidate/raw-position/party/null/mask/order/80/parent/county-substitute/residual/key/current-admission and native service IDs/count/CRS/vintage/fields. [Isolated reconstruction](maps/offline-validation.json) denies network and mutable aggregate/helper/peer/writer routes and reproduces10 complete deterministic catalogue/atlas/report outputs byte-for-byte in temporary outputs. [DOM/source/filter/URL checks](maps/dom-validation.json) compare every full native/parent/context object and execute the actual embedded JavaScript over all county/priority/remainder cases. A browser was unavailable through CUA; these are parsed-HTML/Node execution tests, without a browser visual claim. The schema distinguishes acquisition, historical source replay, output regeneration and final read-only audit.

## Preservation, access and completion

Public directory GET selectors used only observed county anchors and local office fields. No personal lookup, outreach, submitted message, authenticated/admin/partner source or challenge bypass was used. Initial sandbox DNS failure has no fabricated body/status/header/hash. Every actual response hop/status/header/body and error remains. Earlier broad discovery GET-only social-share/unrelated probate/ballot responses are retained as excluded source history; no message was submitted and none is admitted as map coverage. Narrow reader/discovery assumptions, exact failed checker versions and errors survive in [history](maps/history/). Missing original metadata remains qualified; fresh controlling map evidence has complete configured/sent headers and actual UTC start/end.

The source catalogue records retrieval clocks separately from source HTTP/cache clocks and filename/printed/adopted/effective distinctions. All stored objects are strictly below40,000,000 bytes, using one lossless gzip stream and ordered parts where needed. Individual original election bodies/receipts are reused by full pins and roles in [original references](maps/original-references.json); exact older bodies resolve from their full historical captures, never a newer file at the same path. No producer writer/import, mutable newsroom aggregate, current helper, unfinished peer or optional coordinator review is a build dependency.

Current/legal/geographic/physical/native80/eligible-write-in/November-vote/reporting-choice/leaf/cadence/exact-pool/collector/forecast/calibration approvals remain false or unknown. These are external qualifications rather than indefinite research gates. The bounded acquisition/report/offline QA completes this question; coordinator alone can review, accept and publish.
'''
 report+='\nMeasured package: '+str(summary['receipts'])+' acquisition receipts, '+str(summary['unique_pdfs'])+' unique full PDFs / '+str(summary['all_pdf_pages'])+' automatically rendered pages; '+str(summary['counties_with_downloaded_map_assets'])+' counties have downloaded map/context assets from their inspected chains.\n'
 put('precinct-maps.md',report)
 return summary
if __name__=='__main__':
 target=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT
 print(json.dumps(build(target)))
 if len(sys.argv)==1:(ROOT/'precinct-maps.md').replace(S/'precinct-maps.md')

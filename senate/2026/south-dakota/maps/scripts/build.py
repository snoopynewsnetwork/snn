"""Deterministic offline source inventory, full-object references, 304 index/691
inventory/66 parent pages. Does not fetch, alter shared sources or infer joins.
"""
from common import *
from investigate import receipts,links
from bs4 import BeautifulSoup
from html import escape as esc
import re,csv,io,collections
MAP_PDFS={
 '46081':['map-46081-42ebaf0a5587','map-46081-f2a5dadfdc64','map-46081-9b9963132dc9'],
 '46013':['map-46013-004-network','map-46013-005-network'],
 '46011':['map-46011-005','map-46011-006'],
 '46135':['map-46135-022-network','map-46135-023-network'],
 '46099':['minnehaha-county-PDF','minnehaha-city-PDF'],
 '46035':['primary-46035-382cbc8ef4'],
 '46117':['map-46117-bd616f1e3d39'],
 '46033':['map-46033-c422daa756e3','map-46033-01fa20e0657e'],
 '46029':['map-46029-2e3d305c75f8'],
 '46079':['map-46079-014-network','map-46079-015-network'],
 '46093':['map-46093-47dbc7cf6656','map-46093-b2fbb800ae41'],
 '46047':['map-46047-009-network','map-46047-010-network','map-46047-011-network'],
 '46027':['map-46027-008-network'],
 '46101':['map-46101-8f3949f46109'],
 '46023':['map-46023-007-network'],
 '46102':['map-46102-017-network','map-46102-018-network'],
 '46115':['map-46115-019-network']}
SUPPLEMENTS={'46015':['map-46015-04a54bfd884a'],'46083':['bounded-final-46083','map-46083-016-network'],'46067':['map-46067-867e0b1c8302'],'46135':['map-46135-021-network'],'46023':['map-46023-006-network'],'46011':['map-46011-007'],'46127':['map-46127-020-network'],'46129':['follow-46129-044']}
STYLE='''body{font:16px/1.45 system-ui,sans-serif;color:#152b40;margin:0;background:#f6f7f9}main{max-width:1250px;margin:auto;padding:28px}h1{font-size:30px}h2{margin-top:34px}a{color:#16599b}table{border-collapse:collapse;width:100%;background:white}th,td{padding:10px;border:1px solid #d5dde5;text-align:left;vertical-align:top}th{background:#e7edf4}code{font-size:12px;overflow-wrap:anywhere}small{color:#46576a}img{max-width:100%;height:auto}.note{padding:18px;background:#fff5d8;border-left:5px solid #d5a53b}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}.card{background:white;padding:15px;border:1px solid #d5dde5}.p{max-width:80ch}input{padding:12px;width:min(90%,600px);font:inherit}summary{cursor:pointer;font-size:20px;padding:14px} .key{max-width:240px}'''
def html(title,body):return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+STYLE+'</style><main>'+body+'</main></html>\n'
def ref(c,ptr,x):return dict(contract=c,JSON_pointer=ptr,recursive_semantic_sha256=semantic(x))
def main():
 dep=load('qa/dependencies.json');cp=dep['contract'];c=json.loads(check(cp));notes=load('source/county-findings.json');es=receipts();ix={e['id']:e for e in es};pdfs=load('qa/PDF-inspection.json');pdfix={e['id']:e for e in pdfs};census=json.loads(gzip.decompress((MAPS/'qa/Census-binary-geometry.json.gz').read_bytes()));native=load('qa/native-GIS.json')
 assert set(notes)==set(c['ordered_priority_parent_keys'])
 # Entire source envelopes and all fields survive, including every complete error.
 dump('source/source-inventory.json',dict(schema='SD-map-source-inventory-v1',originals=es,all_originals_independently_hashed=True,source_clock_note='null means not supplied/verified; no HTTP or generated clock is treated as election update time.'))
 directory=next(e for e in es if e['id']=='peer-county-directory');s=BeautifulSoup(original(directory),'html.parser');rows=s.select('tr.rgRow,tr.rgAltRow');assert len(rows)==66
 authorities={}
 for tr in rows:
  cells=tr.find_all('td',recursive=False);assert len(cells)==9
  authorities[cells[0].get_text(' ',strip=True)]=dict(source_id=directory['id'],source_raw_sha256=directory['raw_sha256'],original_row_id=tr.get('id'),all_row_attributes=tr.attrs,cells=[dict(text=td.get_text(' ',strip=True),HTML=str(td),attributes=td.attrs) for td in cells])
 assets=[]
 for f,ids in MAP_PDFS.items():
  for ident in ids:
   e=ix[ident];p=pdfix[ident];assert original(e).startswith(b'%PDF')
   assets.append(dict(id=ident,county_parent=f,type='official_or_officially_linked_PDF_map',source_url=e['url'],parent_id=e.get('parent_id'),literal_href=e.get('literal_href'),retrieved_utc=e.get('retrieved_at_utc'),raw_bytes=e['raw_bytes'],raw_sha256=e['raw_sha256'],original_reference=e.get('asset_path') or e['stored_objects'],pages=p['pages'],CRS=None,feature_count=None,geometry_vintage_qualification=notes[f],complete_original=True,preview=p['all_pages_contact_sheet'],current_reporting_crosswalk_approved=False))
 for name,f in [('minnehaha','46099'),('pennington','46103')]:
  v=native[name];assets.append(dict(id='native:'+name,county_parent=f,type='complete_native_Esri_snapshot',feature_count=v['feature_count'],true_curve_features=v['true_curve_features'],CRS=v['metadata']['extent']['spatialReference'],source_pages=[e['id'] for e in es if e['id'].startswith(name+'-native-page')],all_attributes_and_geometry_in_original_pages=True,geometry_vintage_qualification=notes[f],preview='maps/previews/'+name+'-native-linear.svg',current_reporting_crosswalk_approved=False))
 ce=ix['census-SD-vtd20-original'];assets.append(dict(id=ce['id'],type='complete_official_Census2020_VTD_fallback',county_parents=list(census['county_counts']),source_url=ce['url'],parent_id=ce['parent_id'],literal_href=ce['literal_href'],retrieved_utc=ce['retrieved_at_utc'],raw_bytes=ce['raw_bytes'],raw_sha256=ce['raw_sha256'],original_reference=ce['asset_path'],feature_count=785,positions=505985,CRS=census['CRS_PRJ'],geometry_vintage_qualification='Census2020 VTD boundaries; no2024 result or current2026 physical/reporting join.',current_reporting_crosswalk_approved=False))
 dump('source/asset-catalog.json',assets)
 bycounty=collections.defaultdict(list)
 for a in assets:
  if a.get('county_parent'):bycounty[a['county_parent']].append(a['id'])
 parents=[]
 for i,p in enumerate(c['county_parents']):
  f=p['parent_key'];assert p['county'] in authorities
  evidence=[e['id'] for e in es if e.get('county_fips')==f or re.search(r'(?<![0-9])'+f+r'(?![0-9])',e['id'])]
  if f=='46099':evidence += [e['id'] for e in es if e['id'].startswith('minnehaha-')]
  if f=='46103':evidence += [e['id'] for e in es if e['id'].startswith(('pennington-','rapid-city-'))]
  if f=='46083':evidence += [e['id'] for e in es if e['id'].startswith('lincoln-')]
  note=notes.get(f,'Outside accepted priority parents. Complete SOS authority record and historical Census2020 fallback retained; no deep current county map investigation or leaf/current join claimed.')
  pe=dict(county=p['county'],county_parent_key=f,priority_parent=f in notes,full_parent_object=ref(cp,'/county_parents/'+str(i),p),ordered_all_native_keys=p['ordered_all_native_keys'],ordered_priority_native_keys=p['ordered_priority_native_keys'],official_authority=authorities[p['county']],source_receipt_ids=sorted(set(evidence)),acquired_county_map_assets=bycounty[f],supplemental_document_ids=SUPPLEMENTS.get(f,[]),fallback=dict(asset_id=ce['id'],native_Census_count=census['county_counts'][f],county_source_selection_fields={'STATEFP20':'46','COUNTYFP20':f[2:]},preview='maps/previews/census-'+f+'.svg',reporting_unit_crosswalk=None),investigation=note,current_geometry_approved=False,historical_to_current_crosswalk=None)
  parents.append(pe)
 dump('county-parents.json',parents);pm={p['county_parent_key']:p for p in parents}
 inv=[]
 for i,u in enumerate(c['all_units']):
  f=u['county_parent_key'];p=pm[f];label=u['native_label_literal'];loc=u['source_native_constituents'][0]
  gap=('Literal absentee reporting group; no physical polygon, countable submethod or geographic allocation is established.' if 'absentee' in label.lower() else 'Literal CENTRAL label; physical board, voting mode and geographic allocation are not established.' if 'central' in label.lower() else 'Source-native observation may be physical, combined or administrative; complete finer constituents and a map correspondence are not established.')
  entry=dict(key=u['key'],rank=u['rank'],county_parent_key=f,county=u['county_literal'],native_label_literal=label,contest_votes=u['contest_votes'],cumulative_votes=u['cumulative_votes'],priority80=u['priority80'],full_frozen_native_object=ref(cp,'/all_units/'+str(i),u),full_frozen_parent_object=p['full_parent_object'],source_locator=dict(worksheet=loc['worksheet_name'],worksheet_ordinal=loc['worksheet_ordinal'],row=loc['row'],candidate_cells=loc['candidate_cell_addresses']),county_map_assets=p['acquired_county_map_assets'],fallback=p['fallback'],qualifications=dict(acquisition='Complete exact county assets where acquired, plus complete official Census2020 fallback original. Scope is shared parent only.',access=p['investigation'],vintage='Distinct published source vintages; no approved November2026 or frozen election-day2024 map is established.',finer_geometry=gap+' No source-native label/number/count is used as a polygon join.',source_specific='Original candidate/source/method/null/unavailable fields resolve in full from the frozen object reference.'),matched_physical_feature_ids=None,current_reporting_crosswalk=None)
  inv.append(entry)
 dump('inventory-691.json',inv);dump('priority-index-304.json',inv[:304]);dump('remainder-387.json',inv[304:])
 dump('source/full-contract-references.json',dict(authority_path_only=ACCEPTANCE,contract=cp,all_complete_objects=dep['complete_semantic_objects'],historical_companions=[p for p in dep['exact_references'] if p['path'] in ['data/baselines/native-2022.csv','data/baselines/native-2022-public.csv','data/baselines/native-2020-public.csv','data/baselines/county-candidates.csv','data/baselines/turnout-registration-controls.csv']],complete_original_reference_graph='qa/dependencies.json',source_only_primary=True,worker_acceptance_and_robustness_flags_unchanged=True))
 # Every read-only original remains one measured reference, not an additional original copy.
 refs={p['path']:p for p in dep['exact_references']}
 for e in es:
  original(e)
  if 'asset_path' in e:refs[e['asset_path']]=dict(path=e['asset_path'],bytes=e['stored_bytes'],sha256=e['stored_sha256'])
  else:
   for p in e['stored_objects']:
    if not p['path'].startswith('maps/'):refs[p['path']]=p
  if e.get('receipt_pin'):refs[e['receipt_pin']['path']]=e['receipt_pin']
 for p in load('source/preparation-individual-pins.json'):check(p);refs[p['path']]=p
 dump('source/read-only-references.json',sorted(refs.values(),key=lambda x:x['path']))
 # Human-readable asset provenance; geometry count stays null for PDFs.
 with (MAPS/'manifest.csv').open('w',newline='') as f:
  fields=['id','county_parent','type','source_url','retrieved_utc','raw_bytes','raw_sha256','feature_count','pages','CRS','preview','geometry_vintage_qualification'];w=csv.DictWriter(f,fields);w.writeheader()
  for a in assets:w.writerow({k:json.dumps(a[k],ensure_ascii=False) if isinstance(a.get(k),(dict,list)) else a.get(k) for k in fields})
 (MAPS/'counties').mkdir(exist_ok=True)
 def source_link(ident):
  e=ix[ident];return '<a href="'+esc(e['url'],quote=True)+'">'+esc(ident)+'</a>'
 def raw_links(ident):
  e=ix[ident];paths=[e['asset_path']] if 'asset_path' in e else [p['path']for p in e['stored_objects']]
  return ' '.join('<a href="../../'+esc(path,quote=True)+'">complete original gzip'+(' part'+str(i+1) if len(paths)>1 else '')+'</a>'for i,path in enumerate(paths))
 def row(e):
  f=e['county_parent_key'];return f'<tr id="rank-{e["rank"]}" data-key="{esc(e["key"])}"><td>{e["rank"]}</td><td><a href="counties/{f}.html">{esc(e["county"])}</a><br>{esc(e["native_label_literal"])}</td><td>{e["contest_votes"]:,}<br><small>cumulative {e["cumulative_votes"]:,}</small></td><td><a href="counties/{f}.html#assets">{len(e["county_map_assets"])} county assets</a>; <a href="previews/census-{f}.svg">Census2020 fallback ({e["fallback"]["native_Census_count"]})</a><br><small>shared parent; no feature match</small></td><td><code>{esc(e["key"])}</code><br><small>worksheet{e["source_locator"]["worksheet_ordinal"]} row{e["source_locator"]["row"]}</small></td><td>{esc(e["qualifications"]["finer_geometry"])}<details><summary>Access / vintage</summary>{esc(e["qualifications"]["access"])}<p>{esc(e["qualifications"]["vintage"])}</p></details></td></tr>'
 header='<tr><th>Frozen rank</th><th>County / literal observation</th><th>2024 source votes</th><th>Acquired maps</th><th>Original locator</th><th>Finer-entry qualification</th></tr>'
 body='<h1>South Dakota precinct-map research</h1><p class="note">304 ordered historical source observations / 39 county parents. All691 observations,387 remainder and66 full parents retained. County maps and Census2020 are shared-parent resources; zero reporting-to-geometry joins are approved. No current returns or vote allocation.</p><p><a href="../precinct-maps.md">Report</a> · <a href="priority-index-304.json">304 full reference entries</a> · <a href="inventory-691.json">691 inventory</a> · <a href="county-parents.json">66 parents</a> · <a href="source/SCHEMA.md">Schema</a> · <a href="source/asset-catalog.json">Asset catalog</a> · <a href="qa/validation.json">Offline QA</a></p><p>Source343,402 /428,728 votes; source303=342,947. Signed428,922 and194 unallocated votes remain separate; certified minimum/membership unproved. This is2024 president, not Senate.</p><p><a href="previews/census-atlas.png">All66 Census fallback atlas</a> · <a href="previews/minnehaha-native-linear.svg">Minnehaha native preview (curves omitted)</a> · <a href="previews/pennington-native-linear.svg">Pennington native preview (curves omitted)</a></p><h2>Exact304 order</h2><table id="priorities">'+header+''.join(row(e) for e in inv[:304])+'</table><details><summary>All387 remainder observations in frozen order</summary><table>'+header+''.join(row(e) for e in inv[304:])+'</table></details><h2>All66 parent resources</h2><div class="grid">'
 for p in parents:
  f=p['county_parent_key'];body+=f'<div class="card"><a href="counties/{f}.html">{esc(p["county"])} ({f})</a><br>{len(p["ordered_all_native_keys"])} historical observations; {len(p["ordered_priority_native_keys"])} priority.<br>Census2020: {p["fallback"]["native_Census_count"]} units. No join.</div>'
 body+='</div>';(MAPS/'index.html').write_text(html('South Dakota | 304 ordered map investigations',body))
 for p in parents:
  f=p['county_parent_key'];b=f'<a href="../index.html">304 ordered index</a><h1>{esc(p["county"])} | {f}</h1><p class="note">{esc(p["investigation"])}</p><p>{len(p["ordered_priority_native_keys"])} priority / {len(p["ordered_all_native_keys"])} full historical observations. Parent is a summary ancestor, not additive to leaves. No physical feature matches or current reporting crosswalk approved.</p><h2 id="assets">Acquired shared-parent assets</h2>'
  for ident in p['acquired_county_map_assets']:
   if ident.startswith('native:'):
    name=ident.split(':')[1];b+=f'<p>{esc(ident)}: {native[name]["feature_count"]} native features, {len(native[name]["true_curve_features"])} true curves. <a href="../qa/native-GIS.json">All attributes/schema/diagnostics</a>. <a href="../previews/{name}-native-linear.svg">Linear display preview</a>. Originals retain curves.</p>'
    for e in es:
     if e['id'].startswith(name+'-native-page'):b+='<p>'+esc(e['id'])+': '+raw_links(e['id'])+'</p>'
    continue
   q=pdfix[ident];b+='<p>'+source_link(ident)+f' | complete{q["pages"]}-page PDF; <a href="../{q["all_pages_contact_sheet"].removeprefix("maps/")}">all-page contact sheet</a>; <a href="../{q["large_complete_page_renders"][0]["path"].removeprefix("maps/")}">complete page1</a>; '+raw_links(ident)+'. Exact reconstruction: <code>python -B scripts/reconstruct.py --id '+esc(ident)+' /private/tmp/map.pdf</code></p>'
  if not p['acquired_county_map_assets']:b+='<p>No complete county precinct-map original acquired from this bounded chain. Use qualified fallback; roster/landing/error bodies are retained as evidence.</p>'
  for ident in p['supplemental_document_ids']:b+='<p>Administrative/district supplement (not a precinct polygon match): '+source_link(ident)+'</p>'
  b+=f'<h2>Census2020 fallback</h2><p>{p["fallback"]["native_Census_count"]} native historical VTD features. Entire785-feature ZIP original retained once, all66 counties. Yankton has one countywide VTD. No current/reporting allocation. '+raw_links(ce['id'])+f'</p><img src="../previews/census-{f}.svg" alt="Historical Census2020 VTD fallback for {esc(p["county"])}"><p><a href="../qa/Census-binary-geometry.json.gz">Full binary/attribute/geometry QA</a></p><h2>Observed authority/acquisition routes</h2><p>Complete SOS authority fields including original blank/masked values: <a href="../county-parents.json">parent inventory</a>. No contacts were sent.</p><ul>'
  for ident in p['source_receipt_ids']:
   e=ix[ident];b+='<li>'+source_link(ident)+' | status '+esc(str(e['status']))+' | complete raw/error bytes '+str(e['raw_bytes'])+'</li>'
  b+='</ul><h2>Ordered full children</h2><ol>'
  for e in inv:
   if e['county_parent_key']==f:b+=f'<li value="{e["rank"]}"><a href="../index.html#rank-{e["rank"]}">{esc(e["native_label_literal"])}</a> | {e["contest_votes"]} source votes | '+('priority' if e['priority80'] else 'remainder')+'</li>'
  b+='</ol>'; (MAPS/f'counties/{f}.html').write_text(html(p['county']+' | qualified parent maps',b))
 summary=dict(priorities=304,full_inventory=691,remainder=387,parents=66,priority_parents=39,county_PDF_map_originals=sum(a['type']=='official_or_officially_linked_PDF_map' for a in assets),county_map_parents=sum(bool(v) for v in bycounty.values()),priority_entries_with_qualified_county_map_assets=sum(bool(e['county_map_assets']) for e in inv[:304]),priority_entries_with_Census_only_map_assets=sum(not e['county_map_assets'] for e in inv[:304]),original_receipts=len(es),owned_GET_receipts=len(list((MAPS/'raw').glob('*.receipt.json'))),native_features=134,true_curve_features=7,Census_features=785,Census_positions=505985,approved_leaf_matches=0)
 dump('qa/build-summary.json',summary);print(summary)
if __name__=='__main__':main()

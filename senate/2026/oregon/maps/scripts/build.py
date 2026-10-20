"""Deterministic static offline atlas. No JavaScript, fetch, result/polygon join or spatial allocation."""
from common import *
from acquire import body_of,links_of
import html,re,collections,urllib.parse,sys

def slug(s):return s.lower().replace(' ','-')
def esc(s):return html.escape(str(s),quote=True)
def link(path,label,base='maps'):
 # All atlas links use the Oregon-relative inventory paths, made relative to each page.
 import os
 return '<a href="'+esc(os.path.relpath(path,base))+'">'+esc(label)+'</a>'
def pre(x,kind,key):return '<pre data-kind="'+esc(kind)+'" data-key="'+esc(key)+'">'+esc(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))+'</pre>'
def shell(title,body):
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+esc(title)+'</title><style>body{font:16px/1.5 system-ui;max-width:1100px;margin:36px auto;padding:0 20px;background:#f7f6f0;color:#17323c}a{color:#075a78}h1,h2{line-height:1.2}nav{display:flex;gap:20px;flex-wrap:wrap}table{border-collapse:collapse;width:100%;background:white}td,th{border:1px solid #c5cdd0;padding:9px;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#fff;padding:18px;border:1px solid #c5cdd0;font-size:12px}details{padding:9px;border-bottom:1px solid #c5cdd0}img{max-width:100%;height:auto}.qualification{border-left:5px solid #bb7821;padding:12px;background:#fff1d5}</style><body>'+body+'</body></html>\n'
def inventory():
 a=load(AUTH);contractref=a['frozen_contract'];c=json.loads(exact(contractref));findings=load('maps/parent-findings.json');parents=c['all_36_county_parents'];requests={};refpaths={};urls={}
 for p in sorted((M/'requests').glob('*.json')):
  r=load(str(p.relative_to(S)));requests[r['key']]=r;refpaths[r['key']]=ref(str(p.relative_to(S)));urls[r['requested_url']]=r['key']
 for name in load('maps/references/navigation-fixed.json'):
  x=load(name);r=x['receipt'];requests[r['key']]=r;refpaths[r['key']]=ref(name);urls[r['requested_url']]=r['key']
 def ancestors(key,seen=None):
  seen=set() if seen is None else seen
  if key in seen or key not in requests:return seen
  seen.add(key);p=requests[key].get('parent');p=p if p in requests else urls.get(p);return ancestors(p,seen) if p else seen
 county_names={slug(p['county']):p['county'] for p in parents}
 resources=[]
 for key,r in requests.items():
  counties=set()
  for ancestor in ancestors(key):
   if ancestor.startswith('county-'):
    for short,name in county_names.items():
     if ancestor.startswith('county-'+short+'-'):counties.add(name)
  if key.startswith('census-') or key.startswith('state-odot') or key=='odot-county-service':counties=set(county_names.values())
  if key.startswith('metro-'):counties={'Clackamas','Multnomah','Washington'}
  b=body_of(r);kind='PDF original' if b.startswith(b'%PDF') else 'ZIP original' if b.startswith(b'PK\x03\x04') else 'JSON original' if b[:1] in [b'{',b'['] else 'HTML/text authority or error body' if b else 'failed attempt: no body'
  resources.append({'key':key,'receipt':refpaths[key],'original_role':r.get('role','independently hash-verified reused official authority navigation'),'parent':r.get('parent'),'ancestor_keys':sorted(ancestors(key)),'counties':sorted(counties),'url':r['requested_url'],'final_url':r.get('final_url'),'statuses':[e['status'] for e in r.get('entities',[])],'access_error':r.get('error'),'format_scope':kind,'raw_bytes':len(b),'raw_sha256':sha(b) if b else None,'acquired_original_body':bool(b),'current_geometry_approved':False})
 native={p.stem:load(str(p.relative_to(S))) for p in sorted((M/'native').glob('*.json'))};geo=load('maps/qa/geography.json.gz');gr={l['key']:l for l in geo['layers']};binary=load('maps/qa/binary-summary.json')
 parentrows=[];contextrows=[];unknown=[]
 for i,p in enumerate(parents):
  name=p['county'];pr={'whole_file':contractref,'pointer':f'/all_36_county_parents/{i}','full_object_semantic_sha256':semantic(p)}
  scope={'vintage':'Resource-specific source publication labels/metadata; historical2010 county context is explicitly separate. No same-vintage result/legal approval.','access':'Every retained attempt/status/error and captured source clock is in linked receipts. '+findings[name], 'CRS':'Per-service complete native spatialReference and per-SHP original PRJ retained. PDF CRS unknown unless explicitly printed; no CRS inferred from appearance.','physical':'No precinct-to-physical-polling-site crosswalk established. Office, drop box, municipality, ward and ballot style are separate scopes.','legal':'No approved November2026 legal precinct outline/crosswalk. County2010 outlines and source ring diagnostics do not establish current legal gaps/overlaps/slivers.','finer_ID':'No source row number/name/count/FIPS/shape used as a finer/current result-ID join. Native GIS IDs are retrieval/attribute evidence only.','native_result_membership':'Known literal source-only constituents retained' if p['source_native_constituents'] else 'Unknown2024native membership retained; unavailable parent is not a synthetic native unit.'}
  ownresources=[r['key'] for r in resources if name in r['counties']];ownnative=[k for k,v in native.items() if any(r['key']==v['parent'] and name in r['counties'] for r in resources) or (k.startswith('metro-') and name in ['Clackamas','Multnomah','Washington']) or k=='state-odot-counties']
  row={'county':name,'county_fips':p['county_fips'],'county_key':p['county_key'],'full_parent_ref':pr,'known_source_context_count':len(p['source_native_constituents']),'unavailable_native_case':p['unknown_native_membership'],'map_findings':findings[name],'gaps':scope,'shared_parent_resource_keys':ownresources,'native_snapshots':ownnative,'fallback_county_context':'census-oregon-county2010','current_result_leaf_polygon_joins':[],'current_geography_approved':False}
  parentrows.append(row)
  for j,obj in enumerate(p['source_native_constituents']):
   contextrows.append({'key':obj['key'],'parent_key':p['county_key'],'source_context_ref':{'whole_file':contractref,'pointer':f'/all_36_county_parents/{i}/source_native_constituents/{j}','full_object_semantic_sha256':semantic(obj)},'full_parent_ref':pr,'gaps':scope,'shared_parent_resources':ownresources,'inferred_leaf_join':None,'allocated_votes_ballots_registration':False})
  if p['unknown_native_membership']:unknown.append({'case_key':p['county_key'],'full_unavailable_parent_ref':pr,'gaps':scope,'shared_parent_resources':ownresources,'native_membership':None})
 order=c['known_source_universe']['full_ordered_keys'];by={x['key']:x for x in contextrows};assert len(contextrows)==len(by)==510 and len(parentrows)==36 and len(unknown)==31
 contextrows=[by[k] for k in order]
 return {'authority_path':AUTH,'frozen_contract':contractref,'schema':'oregon.maps.complete-parent-source-reference-inventory.v1','parents':parentrows,'known_source_contexts':contextrows,'unavailable_native_parent_cases':unknown,'full_original_tree':{'resolver':'maps/scripts/resolve.py','full_source_replay':'maps/qa/source-replay.json','source_ledger_refs':[ref(r['path']) for r in a['complete_source_object_reference_bodies']],'all_companion_and_historical_refs':'resolve through external authority PATH ONLY; full bodies independently replayed without projection'},'resources':resources,'native_snapshots':native,'canonical_statewide_native_order':None,'canonical_top15':None,'canonical_minimum80':None,'canonical_priority':None,'canonical_remainder':None,'current_legal_leaf_resultID_eligible_live_cadence_outstanding_forecast_calibration_approvals':False,'historical_normalization':'partial and producer-specific; complete originals retained by exact immutable source references','inferred_result_leaf_polygon_joins':0,'physical_site_crosswalk':None,'spatial_allocations':False}

def outputs(inv):
 c=json.loads(exact(inv['frozen_contract']));parents=c['all_36_county_parents'];by={p['county_key']:p for p in parents};resources={r['key']:r for r in inv['resources']};geo=load('maps/qa/geography.json.gz');gr={l['key']:l for l in geo['layers']};out={}
 nav='<nav><a href="../precinct-maps.md">Research report</a><a href="index.html">All36 parents</a><a href="known.html">Known510 contexts</a><a href="unavailable.html">31 unavailable cases</a><a href="publications.html">All PDF pages</a><a href="SCHEMA.md">Schema/reproduction</a></nav>'
 warning='<p class="qualification">Canonical statewide native order / top15 / minimum80 / priority / remainder: NULL. All36 parents remain in scope. Geographic assets are qualified evidence; no result-leaf polygon joins or spatial vote, ballot or registration allocation.</p>'
 def table(rows,base='maps'):
  x='<table><thead><tr><th>County</th><th>Known source records</th><th>2024native membership</th><th>Bounded map finding</th></tr></thead><tbody>'
  for p in rows:x+='<tr data-parent="'+esc(p['county_key'])+'"><td>'+link('maps/parents/'+slug(p['county'])+'.html',p['county'],base)+'</td><td>'+str(p['known_source_context_count'])+'</td><td>'+('unavailable' if p['unavailable_native_case'] else 'known source only')+'</td><td>'+esc(p['map_findings'])+'</td></tr>'
  return x+'</tbody></table>'
 out['maps/index.html']=shell('Oregon complete-parent map atlas',nav+'<h1>Oregon precinct map evidence atlas</h1>'+warning+'<p>Static offline navigation filters by county, known-source scope or unavailable parent case. Original parent/source ordering and every full object remain inspectable. Browser Find searches the selected page. No JavaScript or network requests.</p>'+table(inv['parents'])+'<h2>Acquired historical county context</h2><p>Complete Census2010 Oregon county SHP:36 features. Census2020VTD directory has no Oregon entries. Neither is current precinct approval.</p><img alt="2010 county context, not current precincts" src="previews/binary-census-oregon-county2010.svg">')
 out['maps/unavailable.html']=shell('Oregon unavailable native-parent cases',nav+'<h1>31 unavailable native-parent cases</h1>'+warning+table([p for p in inv['parents'] if p['unavailable_native_case']])+pre(inv['unavailable_native_parent_cases'],'all-unavailable','31-parent-cases'))
 x=nav+'<h1>510 complete known source contexts</h1>'+warning+'<p>Preserved qualified known-only source order. This is not statewide priority or a dispatch subset. Each link opens the full original context and source-specific gaps.</p><ol>'
 for row in inv['known_source_contexts']:
  p=by[row['parent_key']];anchor='context-'+sha(row['key'].encode())[:16];x+='<li data-context-key="'+esc(row['key'])+'">'+link('maps/parents/'+slug(p['county'])+'.html#'+anchor,row['key'])+'</li>'
 out['maps/known.html']=shell('Oregon known-only source contexts',x+'</ol>')
 for row in inv['parents']:
  p=by[row['county_key']];base='maps/parents';body='<nav>'+link('maps/index.html','All36 parents',base)+link('maps/known.html','Known510 contexts',base)+link('maps/unavailable.html','31 unavailable cases',base)+'</nav><h1>'+esc(p['county'])+' map/source evidence</h1>'+warning+'<p>'+esc(row['map_findings'])+'</p><h2>Source-specific limitations</h2>'+pre(row['gaps'],'gaps',p['county_key'])+'<details><summary>Complete immutable original parent object, including every constituent/admin/historical array</summary>'+pre(p,'parent',p['county_key'])+'</details><details><summary>Exact full parent reference</summary>'+pre(row['full_parent_ref'],'parent-reference',p['county_key'])+'</details><h2>Acquired native/shared parent resources</h2>'
  for key in row['native_snapshots']:
   snap=inv['native_snapshots'][key];body+='<h3>'+esc(key)+'</h3><p>'+link('maps/native/'+key+'.json','Complete snapshot/metadata/page inventory',base)+'</p>'
   if key in gr:body+='<p>'+esc(gr[key]['counts'])+'</p><img alt="Qualified linear-only native preview" src="'+esc('../previews/'+key+'.svg')+'">'
  body+='<details><summary>Every retained authority/map acquisition and access failure for this parent</summary><ul>'
  for key in row['shared_parent_resource_keys']:
   r=resources[key];body+='<li>'+link(r['receipt']['path'],key,base)+' '+esc(str(r['statuses'])+' '+r['format_scope']+' '+str(r['access_error']))+' <a href="'+esc(r['url'])+'">Original URL</a></li>'
  body+='</ul></details><h2>Complete original source contexts</h2>'
  for j,obj in enumerate(p['source_native_constituents']):
   anchor='context-'+sha(obj['key'].encode())[:16];body+='<details id="'+anchor+'"><summary>'+esc(obj['key'])+'</summary>'+pre(obj,'context',obj['key'])+'<p>Shared-parent map evidence only; finer/current/legal/physical/result-ID gaps above apply to this exact source record. No polygon join inferred.</p></details>'
  if row['unavailable_native_case']:body+='<p data-unavailable="'+esc(p['county_key'])+'">Unknown native membership is retained as one unavailable parent case; it is not a native result row.</p>'
  out['maps/parents/'+slug(p['county'])+'.html']=shell(p['county']+' complete source and map evidence',body)
 gallery=nav+'<h1>Complete acquired PDF publications</h1>'+warning+'<p>Every page below is an automatic full-page Poppler render. Manual scope is recorded separately in qa/visual-review.json. These derivatives do not replace original bytes or certify legal/current/result identity.</p>'
 for pub in load('maps/renders/index.json'):
  gallery+='<section id="pdf-'+pub['source_pdf_sha256']+'"><h2>'+esc(pub['member'] or pub['request'])+'</h2><p>'+link(pub['request'],'Exact request, original body and reconstruction parts')+' '+esc(str(pub['page_count'])+' pages; PDF SHA256 '+pub['source_pdf_sha256'])+'</p>'
  for page in pub['pages']:
   href=page['render']['path'].removeprefix('maps/');gallery+='<a href="'+esc(href)+'"><img loading="lazy" style="width:360px" alt="'+esc('Complete page '+str(page['page']))+'" src="'+esc(href)+'"></a>'
  gallery+='</section>'
 out['maps/publications.html']=shell('Oregon acquired PDF publication atlas',gallery)
 return {k:v.encode() for k,v in out.items()}
if __name__=='__main__':
 inv=inventory();save('maps/inventory.json.gz',inv);inv=load('maps/inventory.json.gz')
 for p,b in outputs(inv).items():(S/p).parent.mkdir(parents=True,exist_ok=True);(S/p).write_bytes(b)
 print(json.dumps({'parents':len(inv['parents']),'complete_known_contexts':len(inv['known_source_contexts']),'unavailable_cases':len(inv['unavailable_native_parent_cases']),'resources':len(inv['resources']),'static_atlas_pages':len(outputs(inv))}))

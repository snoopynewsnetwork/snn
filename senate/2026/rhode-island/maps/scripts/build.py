"""Deterministic static atlas and full source inventory; no JavaScript, external assets or vote allocation."""
from acquire import *
from follow import anchors
from html import escape
from collections import Counter
import csv,re,os

def detail(title,x,cls='object',key=None):
 attr=(' data-key="'+escape(key,quote=True)+'"') if key is not None else ''
 return '<details class="'+cls+'"'+attr+'><summary>'+escape(title)+'</summary><pre>'+escape(json.dumps(x,ensure_ascii=False,indent=2))+'</pre></details>'
def page(title,body):return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+'</title><style>body{max-width:1120px;margin:2em auto;padding:0 1em;font:16px/1.5 system-ui;color:#172d3e;background:#fcfcfa}a{color:#175a87}table{border-collapse:collapse;width:100%}th,td{border:1px solid #b5c6ce;padding:.4em;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.4 monospace;background:#eff3f5;padding:1em}details{margin:.6em 0}summary{cursor:pointer}img{max-width:100%;height:auto}p.note{padding:1em;background:#fff1cd}</style><body><h1>'+escape(title)+'</h1>'+body+'</body></html>\n'
def htmlwrite(path,title,body):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(page(title,body))
def flatrequests():return [parsed(p) for p in sorted((M/'requests').glob('*.json'))]
def ownership(requests):
 byid={r['id']:r for r in requests};roots={}
 special={'cranston-':'cranston','woonsocket-':'woonsocket','warwick-':'warwick','johnston-':'johnston','pawtucket-':'pawtucket','little_compton-':'little_compton','north_providence-':'north_providence'}
 def resolve(r,seen=None):
  seen=seen or set()
  if r['id'] in seen:return None
  seen.add(r['id'])
  if r['id'].startswith('municipal-'):return r['id'][10:]
  for prefix,key in special.items():
   if r['id'].startswith(prefix):return key
  p=r.get('parent');return resolve(byid[p],seen) if p in byid else None
 for r in requests:roots[r['id']]=resolve(r)
 return roots

def run():
 c=parsed(S/'data/turnout/priority-set.json');parents=c['municipal_and_administrative_parent_sensitivity']['full_inventory'];full=c['complete_descending_order'];priority=c['ordered_priority_keys'];inv=c['all_source_native_constituents'];requests=flatrequests();roots=ownership(requests);pr=parsed(M/'source/directory-observation.json')['priority_order'];qa=parsed(M/'qa/native-audit.json');pdfs=parsed(M/'qa/pdf-rendering.json');pd={r['request']:r for r in pdfs['publications'] if 'pages' in r}
 # Whole source contract, including all roots and old peer metadata, stays unchanged as one reconstructible object.
 (M/'derived/full-source-contract.json.gz').write_bytes(gzip.compress((S/'data/turnout/priority-set.json').read_bytes(),mtime=0))
 fullkeys=[x['key'] for x in full];parent_arrays={}
 resources=[];parentrecords=[];observations=[]
 for p in parents:
  key=p['key'];slug=key.split(':')[-1];admin=p['geography_type']!='municipality';ranked=[r for r in full if r['parent_key']==key];const=[x for x in inv if x['key'] in p['native_keys']];member_ranked=[r for r in full if r['native_key'] in p['native_keys']]
  arrays=dict(original_ordered_native_inventory_keys=p['native_keys'],full_source_rank_ordered_children=[r['key'] for r in ranked],ordered_priority_children=[r['key'] for r in ranked if r['key'] in priority],ordered_remainder_children=[r['key'] for r in ranked if r['key'] not in priority]);parent_arrays[key]=arrays
  local=[r for r in requests if roots[r['id']]==slug] if not admin else []
  native={}
  for pre in ['rigis','sos']:
   fs=parsed(M/f'derived/{pre}-native-features.json.gz');matches=[dict(full_array_position=i,objectid=f['attributes'].get('OBJECTID',f['attributes'].get('FID')),attributes=f['attributes']) for i,f in enumerate(fs) if not admin and f['attributes']['TOWN']==p['name']]
   native[pre]=dict(scope='shared municipal TOWN attribute resource only; no child identity/crosswalk',native_crs=qa[pre]['native_crs'],feature_positions=matches,feature_count=len(matches),original_requests=[b['request'] for b in parsed(M/('source/native-batches.json' if pre=='rigis' else 'source/sos-native-batches.json'))['batches']],geometry_vintage=('2021-2022 redistricting-cycle description; later edits/effective November approval unproven' if pre=='rigis' else '2022 layer title and Secretary hub narrative; layer/service descriptions empty, exact effective boundary vintage/November approval unproven'),current_approval=False,legal_approval=False)
  rec=dict(inventory_constituent_ranked_keys=[r['key'] for r in member_ranked],parent_key=key,slug=slug,complete_parent=p,child_arrays=arrays,priority_parent_position=pr.index(slug)+1 if slug in pr else None,municipal_chain_request_ids=[r['id'] for r in local],shared_native_resources=native if not admin else {},physical_geometry_available=False if admin else None,scope='Nonphysical federal administrative counting context; unavailable polygon. Do not assign municipality geometry.' if admin else 'Municipal shared resources; finer source context/current/legal/result-ID/physical match unapproved.',gap='No independently approved November reporting-ID, ballotstyle-to-result, physical-site-to-source-code or legal boundary crosswalk. Historical volume is not land coverage.')
  parentrecords.append(rec)
  for x in const:
   rr=next((r for r in full if r['native_key']==x['key']),None)
   obs=dict(source_inventory_key=x['key'],source_key=rr['key'] if rr else None,source_anchor=rr['source_anchor'] if rr else None,parent_key=x['parent_key'],sensitivity_parent_key=key,priority_rank=priority.index(rr['key'])+1 if rr and rr['key'] in priority else None,shared_parent_resource_key=key if not admin else None,native_resource_positions={pre:[dict(full_array_position=z['full_array_position'],objectid=z['objectid']) for z in v['feature_positions']] for pre,v in native.items()} if not admin else {},physical_geometry_available=False if admin else None,qualified_scope='shared-parent source positions only' if not admin else 'explicit nonphysical/unavailable',gaps=dict(access='; '.join(r['id']+':'+str(last(r).get('status',last(r).get('error'))) for r in local) if local else ('Not dispatched; shared statewide historical geometry only.' if not admin else 'No physical geometry supplied in source.'),vintage='2022-cycle layer, not exact frozen 2024 election map and not approved November 2026.',crs=None if admin else {k:v['native_crs'] for k,v in native.items()},finer='No source-native archive/member/first-Senate-byte to geometry crosswalk.',current='November approval unknown; filename/year and labels do not establish it.',legal='No same-vintage legal outline reconciliation.',physical='No result-context-to-physical-site match approved.',ballotstyle='Sample-ballot publication scope separate; no ballotstyle/result-unit identity inferred.'))
   observations.append(obs)
  body='<p><a href="../index.html">Atlas</a> · <a href="../priority.html">242 ordered priority contexts</a></p><p class="note">'+escape(rec['scope'])+' '+escape(rec['gap'])+'</p>'
  if not admin:
   body+='<p>Each preview groups the native TOWN attribute at shared municipality scope. It supplies no child matching or geographic allocation.</p>'
   for pre in ['rigis','sos']:
    body+=f'<h2>{pre.upper()} native layer: {native[pre]["feature_count"]} features</h2><a href="../previews/{pre}-{slug}.svg"><img src="../previews/{pre}-{slug}.png" alt="{escape(pre+" shared municipality linear-ring preview",quote=True)}"></a>'
  else:body+='<p>No polygon or fabricated polling site. Federal votes stay outside municipal allocations.</p>'
  body+=detail('Complete parent/source-resource record',rec,cls='parent-object',key=key)
  body+='<h2>Acquired local chain and access attempts</h2><ul>'
  for r in local:
   h=last(r);body+='<li><a href="../requests/'+escape(r['id'],quote=True)+'.json">'+escape(r['id'])+'</a>: '+escape(str(h.get('status',h.get('error'))))+' · <a href="'+escape(r['requested_url'],quote=True)+'">publication URL</a>'
   if r['id'] in pd:
    for imagepath in pd[r['id']]['rendered_all_pages']:body+=' · <a href="../'+imagepath+'">page '+imagepath.split('-')[-1].split('.')[0]+'</a>'
   body+='</li>'
  body+='</ul><h2>Full native source constituents in original inventory order</h2>'
  for x in const:body+=detail(x['reporting_name']+' — '+x['key'],x,cls='constituent',key=x['key'])
  body+='<h2>Full ranked Senate contexts in source rank order</h2>'
  for r in member_ranked:
   body+=detail(('Priority ' if r['key'] in priority else 'Remainder ')+str(r['rank'])+' · '+r['name'],r,cls='ranked-object',key=r['key'])
  htmlwrite(M/f'parents/{slug}.html',p['name'],body)
 # Each priority observation has a complete per-source annotation, retaining position and exact shared resource key.
 bynative={x['source_inventory_key']:x for x in observations};ordered_obs=[bynative[r['native_key']] for r in full]
 dump(M/'derived/context-observations.json',dict(authority_path=AUTHORITY,ordered_full_keys=fullkeys,ordered_priority_keys=priority,ordered_remainder_keys=fullkeys[242:],ordered_full_observations=ordered_obs,all_497_inventory_observations=observations,parent_child_arrays=parent_arrays,complete_parent_resource_records=parentrecords,external_complete_historical_objects=dict(native_inventory='data/baselines/extracts/native-inventory.json',all_native_contests='data/baselines/extracts/native-baselines.jsonl.gz',whole_source_contract='data/turnout/priority-set.json'),approvals={k:False for k in ['coordinator','current_geography','legal_boundary','current_reporting_ID','legal_native80','eligible_writein','feed','November_returns','measured_cadence','exact_remainder','collector','forecast','calibration']}))
 for mode,rows in [('priority',full[:242]),('full',full),('remainder',full[242:])]:
  body='<p><a href="index.html">Atlas</a> · <a href="priority.html">Priority</a> · <a href="full.html">All 458</a> · <a href="remainder.html">216 remainder</a></p><p class="note">Historical source observations; no geometry/physical/current/legal identity approved. Expand each complete row and its qualification. Parent pages retain full constituents/candidates/parties/methods/raw-position proofs.</p><ol>'
  for r in rows:
   o=bynative[r['native_key']];slug=o['sensitivity_parent_key'].split(':')[-1]
   body+='<li data-key="'+escape(r['key'],quote=True)+'"><a href="parents/'+slug+'.html">'+escape(str(r['rank'])+' · '+r['name'])+'</a> · '+str(r['votes'])+' reported votes'+detail('Complete original ranked object',r,cls='ranked-object',key=r['key'])+detail('Specific shared-resource and access/position/vintage/CRS/current/legal gaps',o,cls='qualification',key=r['key'])+'</li>'
  body+='</ol>';htmlwrite(M/f'{mode}.html',f'Rhode Island {mode} historical source order ({len(rows)})',body)
 body='<p class="note">242 historical priority observations under 37 municipal parents. All 458 Senate contexts, 216 remainder, all 497 inventory contexts and all 39 municipal + four administrative parents remain available. This atlas does not allocate votes, ballots or registration through geometry.</p><p><a href="priority.html">242 priority in exact order</a> · <a href="full.html">All 458 ordered Senate contexts</a> · <a href="remainder.html">216 remainder</a> · <a href="derived/full-source-contract.json.gz">Whole frozen contract</a> · <a href="derived/context-observations.json">All complete source annotations</a> · <a href="publications.html">All PDF pages</a> · <a href="../precinct-maps.md">Report</a> · <a href="REPRODUCTION.md">Offline reproduction</a></p>'
 body+='<p><a href="../data/baselines/extracts/native-inventory.json">All1459 historical inventory objects</a> · <a href="../data/baselines/extracts/native-baselines.jsonl.gz">All2460 historical native-contest objects</a></p>'
 body+='<h2>37 priority municipal chains in source priority order</h2><ol>'
 for slug in pr:
  p=next(p for p in parents if p['key'].split(':')[-1]==slug);body+='<li data-parent="'+slug+'"><a href="parents/'+slug+'.html">'+escape(p['name'])+'</a></li>'
 body+='</ol><h2>Full 43-parent inventory</h2><table><tr><th>Parent</th><th>Historical inventory</th><th>Senate contexts</th><th>Priority contexts</th><th>Municipal shared geometry</th></tr>'
 for rec in parentrecords:
  p=rec['complete_parent'];ar=rec['child_arrays'];body+='<tr><td><a href="parents/'+rec['slug']+'.html">'+escape(p['name'])+'</a></td><td>'+str(len(ar['original_ordered_native_inventory_keys']))+'</td><td>'+str(len(rec['inventory_constituent_ranked_keys']))+'</td><td>'+str(len(ar['ordered_priority_children']))+'</td><td>'+('RIGIS '+str(rec['shared_native_resources']['rigis']['feature_count'])+' / SOS '+str(rec['shared_native_resources']['sos']['feature_count'])+' (no child match)' if rec['shared_native_resources'] else 'Nonphysical; no polygon')+'</td></tr>'
 body+='</table><p>Static HTML; no JavaScript, external basemap, network dependency, browser permission or simulated filter claim.</p>';htmlwrite(M/'index.html','Rhode Island precinct source atlas',body)
 body='<p><a href="index.html">Atlas</a>. Every acquired PDF page is rendered below; automatic rendering does not mean manual visual inspection. Sample ballots, map PDFs and site rosters remain distinct.</p>'
 for row in pdfs['publications']:
  if 'pages' not in row:continue
  body+='<h2>'+escape(row['request'])+'</h2>'+detail('Complete publication scope, provenance and render record',row,cls='publication-object',key=row['request'])+'<p><a href="requests/'+row['request']+'.json">Original request, full compressed entity parts and provenance</a></p>'
  for path in row['rendered_all_pages']:body+='<a href="'+path+'"><img loading="lazy" src="'+path+'" alt="'+escape(path,quote=True)+'"></a>'
 htmlwrite(M/'publications.html','Complete acquired PDF publications',body)
 # Full request objects persist separately, with every hop/entity. Summary is only an index, not their replacement.
 dump(M/'source/acquisition-index.json',dict(request_ids=[r['id'] for r in requests],requests=[dict(id=r['id'],parent=r.get('parent'),request_path='requests/'+r['id']+'.json',url=r['requested_url'],status=last(r).get('status'),complete_entity=last(r).get('complete_entity',False),actual_access_blocked=blocked(r),municipal_scope=roots[r['id']]) for r in requests],source_roles='Full request objects and complete original parts are controlling. HTML holders/errors/challenges/timeouts are not acquired geometry; rendered sample ballots are ballotstyle context only.'))
 return dict(parent_pages=len(parents),priority_rows=len(priority),full_rows=len(full),remainder_rows=len(full)-len(priority),inventory=len(inv),requests=len(requests),native_source_features={k:qa[k]['feature_count'] for k in ['rigis','sos']},pdfs=pdfs['original_pdf_count'],pages=pdfs['total_pages'])
if __name__=='__main__':print(json.dumps(run()))

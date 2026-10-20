"""Deterministic offline atlas. Source contexts and native GIS remain separate."""
from acquire import *
import json,html,re,collections
S=M.parent

def expand(n):
 for a,b in [('W. ','West '),('E. ','East '),('N. ','North '),('S. ','South ')]:
  if n.startswith(a):return b+n[len(a):]
 return n

def js(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
def native():
 result={}
 for prefix in ['wards','subprecinct']:
  a=json.loads((M/(prefix+'-layer0-acquisition.json')).read_bytes());ff=[]
  for b in a['batches']:
   v=json.loads(load(M/b['receipt'])[0]);ff.extend(dict(feature=f,raw_receipt=b['receipt'],native_spatial_reference=v.get('spatialReference'))for f in v['features'])
  result[prefix]=ff
 return result

def preview(name,features):
 rings=[r for f in features for r in (f['feature'].get('geometry')or{}).get('rings',[])];xy=[p for r in rings for p in r]
 if not xy:return None
 xmin=min(p[0]for p in xy);xmax=max(p[0]for p in xy);ymin=min(p[1]for p in xy);ymax=max(p[1]for p in xy);w=xmax-xmin;h=ymax-ymin;pad=max(w,h)*.025
 out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="'+f'{xmin-pad} {ymin-pad} {w+pad*2} {h+pad*2}'+'"><title>'+html.escape(name)+' native EPSG26986 historical context; no results crosswalk</title><rect x="'+str(xmin-pad)+'" y="'+str(ymin-pad)+'" width="'+str(w+pad*2)+'" height="'+str(h+pad*2)+'" fill="#f3f5f6"/><g transform="matrix(1 0 0 -1 0 '+str(ymin+ymax)+')" fill="#d9e5ec" fill-rule="evenodd" stroke="#244257" stroke-width="'+str(max(w,h)/1800)+'">']
 for wrap in features:
  f=wrap['feature'];g=f.get('geometry')or{}
  if 'curveRings'in g:continue # Curves stay in raw source; no linearized preview.
  d=' '.join('M'+' L'.join(str(p[0])+' '+str(p[1])for p in ring)for ring in g.get('rings',[]))
  out.append('<path d="'+d+'"><title>'+html.escape(json.dumps(f['attributes'],ensure_ascii=False))+'</title></path>')
 out.append('</g></svg>');stem=sha(name.encode())[:12];p=M/'previews'/(stem+'.svg');p.parent.mkdir(exist_ok=True);p.write_text(''.join(out));return str(p.relative_to(M))

def main():
 c=json.loads((S/'data/turnout/priority-set.json').read_bytes());records=c['all_unit_order'];dirs=json.loads((M/'local-requests.json').read_bytes());bydir={x['parent_literal']:x for x in dirs};maps=json.loads((M/'municipal-map-acquisitions.json').read_bytes());local={}
 for p in (M/'parents').glob('*.json'):
  o=json.loads(p.read_bytes());local[o['parent_literal']]=o
 n=native();names=sorted(set(r['literal_tuple'][0]for r in records));par=[];pset=set(c['ordered_priority_keys']);rset=set(c['ordered_remainder_keys'])
 for name in names:
  rr=[r for r in records if r['literal_tuple'][0]==name];town=expand(name).upper();features=[f for f in n['wards']if f['feature']['attributes']['TOWN']==town];subs=[f for f in n['subprecinct']if f['feature']['attributes']['TOWN']==town]
  mp=[x for x in maps if x['parent_literal']==name];loc=local.get(name);pv=preview(name,features)
  full_chain_path='parents/'+sha(name.encode())[:12]+'.json'if loc else None
  loc_summary={k:v for k,v in loc.items()if k!='steps'}|{'steps':[{k:v for k,v in step.items()if k not in ['all_literal_links','complete_text']}for step in loc['steps']],'complete_chain_object_path':full_chain_path}if loc else None
  companions=[x for x in json.loads((M/'companion-acquisitions.json').read_bytes())if x['parent_literal']==name]
  parent=dict(parent_literal=name,directory_authority=bydir[name],authority_role='State CIS directory establishes municipal government channel; individual clerk/election/GIS text retained in steps; officeholder not inferred',municipal_chain=loc_summary,municipal_chain_status='downloaded_bounded_actual_links'if loc else 'directory_link_attempt_or_nonpriority_scope; see web navigation receipts',state_published_maps=mp,linked_map_roster_companions=companions,native_context=dict(association='Municipal display-name search only; NO result-tuple polygon join',searched_TOWN=town,ward_layer_object_ids=[f['feature']['attributes']['OBJECTID']for f in features],subprecinct_layer_object_ids=[f['feature']['attributes']['OBJECTID']for f in subs],ward_layer_receipt='wards-layer0-acquisition.json',subprecinct_layer_receipt='subprecinct-layer0-acquisition.json',preview=pv,preview_transform='affine identity x / reflected y only; native vertices, no projection/rounding/simplification'),original_source_ordered_children=[r['native_key']for r in sorted(rr,key=lambda x:x['csv_record_ordinal'])],canonical_rank_ordered_children=[r['native_key']for r in rr],ordered_priority_children=[r['native_key']for r in rr if r['native_key']in pset],ordered_remainder_children=[r['native_key']for r in rr if r['native_key']in rset],in_priority=any(r['native_key']in pset for r in rr),gaps=dict(vintage='MassGIS 2022 source acquired in 2026; state PDFs printed dates preserved separately; no frozen November2024 operative boundary proof',finer='Result literals may describe subprecinct/reporting contexts. No exhaustive result-label-to-native-ID crosswalk established',physical='Literal labels/counts/polling locations do not establish physical polygon; administrative identity remains source-null/unknown',current='No November2026 legal/current numeric ID or approved reporting boundary match',local_access=[dict(url=s['url'],status=s['status'],challenge_shell=s['challenge_shell'])for s in loc['steps']if s['status']!=200 or s['challenge_shell']]if loc else None))
  par.append(parent)
 inv=[]
 for r in records:
  inv.append(dict(full_source_object=r,parent_literal=r['literal_tuple'][0],parent_index=names.index(r['literal_tuple'][0]),rank=r['rank'],in_priority=r['native_key']in pset,in_remainder=r['native_key']in rset,geometry_match=None,numeric_native_match=None,physical_match=None,current_approved=False,resource_scope='acquired shared state native historical context and parent map/link/access receipt; see parent fullobject'))
 dump(M/'inventory.json',dict(authority_path='data/coordinator-priority-acceptance.json',units=inv,parents=par,original_source_order=[r['native_key']for r in sorted(records,key=lambda x:x['csv_record_ordinal'])],rank_order=[r['native_key']for r in records],priority=c['ordered_priority_keys'],remainder=c['ordered_remainder_keys'],complete_contract_source='data/turnout/priority-set.json',source_parent_objects=c['all_parent_child_maps']))
 (M/'contract.js').write_text('window.CONTRACT='+js(c)+';\n')
 # Complete GIS attributes and response locator, geometry stays once in acquired originals.
 gis={k:[dict(attributes=f['feature']['attributes'],raw_receipt=f['raw_receipt'],native_spatial_reference=f['native_spatial_reference'],geometry_status='complete_native_raw_response_preserved')for f in fs]for k,fs in n.items()}
 (M/'gis-objects.js').write_text('window.GIS='+js(gis)+';\n')
 atlas=json.loads((M/'inventory.json').read_bytes());(M/'atlas-data.js').write_text('window.ATLAS='+js(atlas)+';\n')
 (M/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Massachusetts historical map atlas</title><style>body{font:16px system-ui;margin:24px;max-width:1400px;color:#213747}input,select,button{font:inherit;padding:6px;margin:5px}table{border-collapse:collapse;width:100%}td,th{padding:6px;border-bottom:1px solid #ccd5dc;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f5f7;padding:15px}img{max-width:100%;max-height:650px}a{color:#075c88}.note{border-left:4px solid #d49e27;padding:10px}details{margin:12px 0}</style><h1>Massachusetts historical map atlas</h1><p class="note">2,394 literal 2024 Senate source contexts • 1,470 priority • 924 remainder • 351 municipal parents. Native GIS and published PDFs provide historical geographic context. No source-tuple polygon/current/legal match or vote allocation is approved.</p><label>Search <input id="search" placeholder="Town, ward, precinct, any source text"></label><label>Parent <select id="parent"><option value="">All parents</option></select></label><label>Scope <select id="scope"><option value="all">All 2,394</option><option value="priority">Priority 1,470</option><option value="remainder">Remainder 924</option></select></label><label>Order <select id="order"><option value="rank">Historical named-vote rank</option><option value="source">Original CSV source order</option></select></label><p id="count"></p><div id="parentDetail"></div><details><summary>Complete frozen contract root object (all 25 fields)</summary><pre id="contract"></pre></details><details><summary>Complete 351-parent source objects and all child arrays</summary><pre id="hierarchy"></pre></details><details><summary>Native GIS full attribute objects and raw geometry response locators</summary><pre id="gis"></pre></details><p><a href="SCHEMA.md">Schema / limits</a> · <a href="inventory.json">Full inventory</a> · <a href="pdf-index.json">PDF original reconstruction / page renders</a> · <a href="native-audit.json">Native geometry diagnostics</a> · <a href="reconstruction.json">Complete historical replay</a></p><table><thead><tr><th>Rank</th><th>City/Town</th><th>Ward</th><th>Pct</th><th>Named votes</th><th>Scope / fullobject</th></tr></thead><tbody id="rows"></tbody></table><script src="contract.js"></script><script src="gis-objects.js"></script><script src="atlas-data.js"></script><script src="atlas.js"></script></html>''')
 print('atlas',len(inv),len(par),'priority parents with local receipt',sum(p['in_priority']and p['municipal_chain']is not None for p in par),'native previews',sum(bool(p['native_context']['preview'])for p in par))
if __name__=='__main__':main()

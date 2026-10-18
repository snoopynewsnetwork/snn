#!/usr/bin/env python3
"""Independent final frozen map coverage/requests/manifest and true-curve retention."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import collections,datetime,gzip,hashlib,json,re,sqlite3
R=Path(__file__).resolve().parents[1];D=R/'data';M=R/'maps';sha=lambda b:hashlib.sha256(b).hexdigest();load=lambda p:json.loads(p.read_text())
class Index(HTMLParser):
 def __init__(self):super().__init__();self.cards=[];self.rows=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='article':self.cards.append(a.get('data-county-key'))
  if tag=='tr'and 'data-county-key'in a:self.rows.append(a['data-county-key'])
  self.links.extend(a[k]for k in ['href','src']if k in a)
def entity(key):
 m=load(M/'evidence'/(key+'.request.json'));parts=[];offset=0
 for r in m['ordered_parts']:
  b=(M/r['path']).read_bytes();assert len(b)==r['stored_bytes']<40000000 and sha(b)==r['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==r['entity_bytes']and offset==r['offset'];parts.append(raw);offset+=len(raw)
 b=b''.join(parts);assert len(b)==m['original_entity_bytes']and sha(b)==m['original_entity_sha256'];return m,b

def main():
 mfbytes=(M/'asset-manifest.json').read_bytes();assert sha(mfbytes)=='a5795ffb08c07620102da1f57413b6c14078bdeee6f7e6c5b096161d3ab0ba17';mf=json.loads(mfbytes);assert mf['asset_count']==451
 actual={str(p.relative_to(R))for p in M.rglob('*')if p.is_file()and p.name!='asset-manifest.json'}|{'precinct-maps.md'};listed={x['path']for x in mf['assets']};assert actual==listed and len(listed)==451
 for x in mf['assets']:
  b=(R/x['path']).read_bytes();assert len(b)==x['bytes']<40000000 and sha(b)==x['sha256'],x['path']
 assert not any(p.name in ['__pycache__','.venv','node_modules','.cache']for p in M.rglob('*'))
 contract=load(D/'turnout/priority-set.json');compat=json.loads(gzip.decompress((M/'compatibility.json.gz').read_bytes()));assert compat['complete_frozen_contract']==contract
 assert len(contract['county_order'])==87;assert sum(len(u)for c in contract['county_order']for u in c['native_constituents'].values())==12316
 idx=Index();idx.feed((M/'index.html').read_text());assert idx.cards==contract['ordered_priority_keys']and idx.rows==contract['complete_ordered_county_keys']
 links=0
 for u in idx.links:
  x=urlsplit(u)
  if not x.scheme and x.path:assert(M/unquote(x.path)).exists(),u;links+=1
 for u in re.findall(r'\]\(([^)]+)\)',(R/'precinct-maps.md').read_text()):
  x=urlsplit(u)
  if not x.scheme and x.path:assert(R/unquote(x.path)).exists(),u;links+=1
 requests=[]
 for p in sorted((M/'evidence').glob('*.request.json')):
  m,b=entity(p.name.removesuffix('.request.json'));requests.append(m)
 assert len(requests)==124 and len({m['original_entity_sha256']for m in requests})==115
 pins=load(M/'input-pins.json')['inputs']
 for x in pins:
  b=(R/x['path']).read_bytes();assert len(b)==x['bytes']and sha(b)==x['sha256']
 a,body=entity('waconia-native');w=json.loads(body);b,body=entity('waconia-preview-linearized');lin=json.loads(body);assert len(w['features'])==len(lin['features'])==4
 arcs=0
 for n,l in zip(w['features'],lin['features']):
  assert n['attributes']==l['attributes']and 'curveRings'in n['geometry']and 'rings'in l['geometry']
  for ring in n['geometry']['curveRings']:
   for segment in ring:
    if isinstance(segment,dict):assert set(segment)=={'c'};arcs+=1
 assert arcs==106
 batches=0;attribute_cells=0;precision_differences=0
 for lane,original,table,n in [('current','current-gpkg','bdry_votingdistricts',4105),('results','results-gpkg','general_election_results_by_precinct_2024',4103),('results2022','results-gpkg','general_election_results_by_precinct_2022',4103)]:
  pre=json.loads(entity(lane+'-ids-pre')[1]);post=json.loads(entity(lane+'-ids-post')[1]);ids=pre['objectIds'];assert len(ids)==len(set(ids))==n and sorted(ids)==sorted(post['objectIds'])
  assert json.loads(entity(lane+'-count-pre')[1])['count']==json.loads(entity(lane+'-count-post')[1])['count']==n
  c=sqlite3.connect(':memory:');c.deserialize(entity(original)[1]);names=[r[1]for r in c.execute('PRAGMA table_info('+table+')')];native={r[0]:dict(zip(names,r))for r in c.execute('SELECT * FROM '+table+' ORDER BY OBJECTID')};seen=[]
  for p in sorted((M/'evidence').glob(lane+'-attributes-*.request.json')):
   request,body=entity(p.name.removesuffix('.request.json'));x=json.loads(body);assert x.get('exceededTransferLimit')is not True;requested=[int(v)for v in request['params']['objectIds'].split(',')];received=[]
   for f in x['features']:
    a=f['attributes'];id=a[x['objectIdFieldName']];received.append(id);old=native[id]
    for k,v in a.items():
     field={'Shape__Area':'Shape_Area','Shape__Length':'Shape_Length'}.get(k,k.upper());assert field in old;attribute_cells+=1
     if v!=old[field]:assert field in ['Shape_Area','Shape_Length'];precision_differences+=1
   assert sorted(requested)==sorted(received);seen.extend(received);batches+=1
  assert sorted(seen)==sorted(ids)and len(seen)==len(set(seen));c.close()
 assert batches==51 and precision_differences==3444
 for name in ['coordinator-map-binary-review.json','coordinator-paper-map-review.json']:assert load(D/name)['status'].startswith('pass_')
 out={'status':'pass_final_frozen_map_package','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Independent complete manifest/path-set+124originalrequests+immutableinputpins+contractobject/card/inventory/link checks; rawtruecurve retention and all51serviceID/count/pre-post/rawattribute batches. Independent fullGPKGbinary/subset andfreshPDFmember/page audits are separately linked.','manifest_sha256':sha(mfbytes),'owned_assets':451,'stored_owned_bytes_excluding_manifest':sum(x['bytes']for x in mf['assets']),'max_stored_object_bytes':max(x['bytes']for x in mf['assets']),'all_counties':87,'ordered_priority_cards':24,'complete_historical_objects':12316,'request_observations':124,'unique_original_entities':115,'read_only_input_pins':len(pins),'local_report_HTML_links':links,'Waconia_unflattened_native_circular_arc_segments':arcs,'complete_source_service_batches':batches,'native_vs_service_attribute_cells':attribute_cells,'retained_geometry_measure_precision_differences':precision_differences,'native_binary_review':'coordinator-map-binary-review.json','paper_review':'coordinator-paper-map-review.json','scope':'No current legal approval, reporting/method/result/crossyear mapping, geometry repair or vote allocation. Full native attributes preserve nonidentical labels/no-data contexts.'}
 p=D/'coordinator-map-final-review.json'
 if p.exists():
  old=load(p)
  if {k:v for k,v in old.items()if k!='checked_utc'}=={k:v for k,v in out.items()if k!='checked_utc'}:out['checked_utc']=old['checked_utc']
 p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()

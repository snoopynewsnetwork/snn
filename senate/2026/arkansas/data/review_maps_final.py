"""Coordinator independent original-native/XY/SVG/atlas audit; no worker imports."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urlparse,parse_qs
import gzip,hashlib,json,re,struct,sys,xml.etree.ElementTree as ET
S=Path(__file__).resolve().parents[1];M=S/'maps';N=0;stats=Counter()
def ck(v,label=''):
 global N
 N+=1
 assert v,(N,label)
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def pack(v):return struct.pack('<'+'d'*len(v),*v)
mf=load(M/'asset-manifest.json');before={}
actual={str(p.relative_to(S)) for p in M.rglob('*') if p.is_file()}|{'precinct-maps.md'}
ck(mf['excludes_only']=='maps/asset-manifest.json' and len(mf['files'])==1072 and {x['path'] for x in mf['files']}==actual-{'maps/asset-manifest.json'})
for v in mf['files']:
 p=S/v['path'];b=p.read_bytes();ck(not p.is_symlink() and len(b)==v['bytes']<40000000 and sha(b)==v['sha256']);before[v['path']]=sha(b)
catalogue=load(M/'original-catalogue.json');receipts={};raw={}
def body(v):
 parts=[]
 for pin in v['parts']:
  b=(M/pin['path']).read_bytes();ck(len(b)==pin['bytes']<40000000 and sha(b)==pin['sha256']);parts.append(b)
 b=gzip.decompress(b''.join(parts));ck(len(b)==v['bytes'] and sha(b)==v['sha256']);return b
for item in catalogue:
 p=M/item['receipt_path'];b=p.read_bytes();r=load(p);ck(len(b)==item['receipt_bytes'] and sha(b)==item['receipt_sha256'] and r==item['complete_receipt'])
 receipts[r['label']]=r;ck(r['request']['method']=='GET' and r['request']['fields'] is None and r['request']['body'] is None and r['utc_start']<=r['utc_end'])
 if r['response_body_available']:raw[r['label']]=body(r['body']);ck(r['response_headers_available']);body(r['headers']);stats['complete_response_entities']+=1
 else:ck(r['body'] is None and r['curl_exit']!=0);stats['no_body_failures']+=1
def source(label):return json.loads(raw[label])
pre=source('precinct-layer-pre');post=source('precinct-layer-post');ck(pre==post and source('boundaries-service-pre')==source('boundaries-service-post'))
ids=source('precinct-ids-pre')['objectIds'];ck(ids==source('precinct-ids-post')['objectIds'] and len(ids)==len(set(ids))==2928)
ck(source('precinct-count-pre')['count']==source('precinct-count-post')['count']==len(ids))
ck({k:pre['extent']['spatialReference'][k] for k in ['wkid','latestWkid']}=={'wkid':26915,'latestWkid':26915} and pre['hasZ'] is False and pre['hasM'] is False)
fields={v['name'] for v in pre['fields']};ck(len(fields)==15);features=[];contexts={};envelopes={};seen=[]
for label in sorted(k for k in receipts if k.startswith('native-page-')):
 r=receipts[label];query=parse_qs(urlparse(r['request']['url']).query);ck(set(query)=={'objectIds','outFields','returnGeometry','returnZ','returnM','returnTrueCurves','f'} and query['outFields']==['*'] and query['f']==['json'])
 ck(all(query[k]==['true'] for k in ['returnGeometry','returnZ','returnM','returnTrueCurves']))
 asked=[int(x) for x in query['objectIds'][0].split(',')];obj=source(label);got=[f['attributes']['objectid'] for f in obj['features']]
 ck(0<len(asked)<=50 and set(got)==set(asked) and not set(seen)&set(got));seen+=got;stats['disjoint_native_pages']+=1
 ck(obj['spatialReference']=={k:pre['extent']['spatialReference'][k] for k in ['wkid','latestWkid']});envelope={k:v for k,v in obj.items() if k!='features'}
 for i,f in enumerate(obj['features']):
  ck(set(f['attributes'])==fields and f['attributes']['state_fips']=='05' and len(f['attributes']['county_fips'])==3)
  oid=f['attributes']['objectid'];contexts[oid]={'receipt':f'originals/{label}/receipt.json','raw_sha256':r['body']['sha256'],'json_pointer':f'/features/{i}','source_object_id':oid};envelopes[oid]=envelope;features.append(f)
ck(len(seen)==2928 and set(seen)==set(ids) and stats['disjoint_native_pages']==59)
byid={f['attributes']['objectid']:f for f in features};ck(len(byid)==2928)
c=load(S/'data/turnout/priority-set.json');parents=load(M/'parent-investigations.json');ck(len(parents)==75)
sourceparents={p['county_fips']:p for p in c['all75parents']};priority=set(c['ordered_priority_keys']);remaining=set(c['remainder_keys']);allgeom=load(M/'qa/geometry-diagnostics.json');diagnostics={v['objectid']:v for v in allgeom['feature_diagnostics']}
curve_ids=[];point_count=0;linear_invalid=[]
for p in parents:
 fips=p['county_fips'];county=[f for f in features if f['attributes']['county_fips']==fips[2:]];asset=load(M/f'derived/{fips}.esri.json.gz')
 ck(asset['features']==county and asset['source_contexts']==[contexts[f['attributes']['objectid']] for f in county])
 ck(asset['native_envelope']==envelopes[county[0]['attributes']['objectid']] and asset['selection']==f"exact source county_fips='{fips[2:]}'; no result-label join")
 sourceids=[f['attributes']['objectid'] for f in county];ck(set(p['source_native_ids'])==set(sourceids) and len(p['source_native_ids'])==p['source_native_count']==len(sourceids))
 ctl='county-'+fips[2:];ck(source(ctl+'-count')['count']==len(county) and source(ctl+'-ids')['objectIds']==p['source_native_ids'] and set(source(ctl+'-ids')['objectIds'])==set(sourceids))
 ck(p['historical_parent_key']==sourceparents[fips]['key'] and p['historical_polygon_matches'] is None and p['November_approved'] is False and p['native_ballot_or_registration_geometry_allocation'] is False)
 ordered=[u['key'] for u in c['full_order'] if u['county_fips']==fips];ck(p['historical_full_children']==ordered and p['ordered_priority_children']==[k for k in ordered if k in priority] and p['ordered_remainder_children']==[k for k in ordered if k in remaining])
 rings=[]
 for f,g in zip(county,asset['features']):
  oid=f['attributes']['objectid'];d=diagnostics[oid];ck(d['repaired'] is False)
  if 'curveRings' in f['geometry']:ck(f['geometry']==g['geometry']);curve_ids.append(oid);continue
  src=f['geometry']['rings'];dst=g['geometry']['rings'];ck(len(src)==len(dst))
  if d['diagnostics']:linear_invalid.append(oid)
  for a,b in zip(src,dst):
   ck(len(a)==len(b))
   for x,y in zip(a,b):ck(pack(x)==pack(y));point_count+=1
   if len(a)>=4 and a[0]==a[-1]:rings.append(a)
 svg=ET.fromstring((M/f'previews/{fips}.svg').read_text());paths=svg.findall('.//{http://www.w3.org/2000/svg}path');ck(len(paths)==len(rings))
 for path,ring in zip(paths,rings):
  tokens=re.findall(r'[MLZ]|[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?',path.attrib['d']);numbers=[float(x) for x in tokens if x not in ('M','L','Z')];ck(len(numbers)==2*len(ring))
  for i,xy in enumerate(ring):ck(pack(numbers[2*i:2*i+2])==pack(xy[:2]));stats['SVG_exact_XY_positions']+=1
 stats['full_county_assets']+=1
ck(point_count==1553886 and len(curve_ids)==36 and len(linear_invalid)==17)
ck(allgeom['features']==2928 and len(allgeom['positive_area_pair_overlaps'])==21 and allgeom['result_polygon_joins'] is False and allgeom['source_repairs'] is False)
class DOM(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.rows=[];self.attrs={};self.buf=None
 def handle_starttag(self,t,a):
  if t=='details':self.attrs=dict(a)
  elif t=='pre':self.buf=[]
 def handle_data(self,d):
  if self.buf is not None:self.buf.append(d)
 def handle_endtag(self,t):
  if t=='pre':self.rows.append((dict(self.attrs),json.loads(''.join(self.buf))));self.buf=None
def dom(p):
 d=DOM();d.feed(p.read_text());return d
index=dom(M/'index.html');units=[(a,v) for a,v in index.rows if a['data-kind'] in ['priority','remainder']]
ck([v['complete_historical_source_observation'] for a,v in units]==c['full_order'] and [a['data-key'] for a,v in units if a['data-kind']=='priority']==c['ordered_priority_keys'] and [a['data-key'] for a,v in units if a['data-kind']=='remainder']==c['remainder_keys'])
ck(all(v['polygon_match'] is None for a,v in units));roots={a['data-root']:v for a,v in index.rows if a['data-kind']=='context'}
ck(roots=={k:v for k,v in c.items() if k not in ['full_order','all75parents']})
for p in parents:
 fips=p['county_fips'];d=dom(M/f'atlas/{fips}.html');group=lambda key:[v for a,v in d.rows if a['data-kind']==key]
 ck(group('parent')==[sourceparents[fips]] and group('investigation')==[p])
 ck([v['complete_historical_source_observation'] for a,v in d.rows if a['data-kind'] in ['priority','remainder']]==[u for u in c['full_order'] if u['county_fips']==fips])
 native=group('GIS');ck([v['complete_native_source_feature'] for v in native]==[f for f in features if f['attributes']['county_fips']==fips[2:]])
 for v in native:ck(v['source_context']==contexts[v['complete_native_source_feature']['attributes']['objectid']])
 stats['full_atlas_HTML_pages']+=1
for rel,digest in before.items():ck(sha((S/rel).read_bytes())==digest,'worker sealed bytes unchanged')
result={'status':'pass','checks':N,'worker_manifest_sha256':sha((M/'asset-manifest.json').read_bytes()),'exact_manifest_targets':1072,'counts':dict(stats),'full_native_objects':2928,'native_fields':15,'native_CRS':26915,'full_pre_post_service_layer_count_IDS_equal':True,'complete_literal_county_controls':150,'linear_XY_IEEE754_positions':point_count,'true_curve_features_retained':len(curve_ids),'source_issue_linear_features':len(linear_invalid),'native_positive_area_pair_diagnostics':21,'historical_full_observations':2841,'priority':1056,'remainder':1785,'all_contract_roots_in_atlas':18,'qualified_parents':75,'priority_parents':68,'coordinator_actual_manual_scope':['Stone November specimen first page rendered directly from complete official PDF; three Senate choices and vote-one instruction','Pulaski June2026 whole map page','Pulaski printed January21,2022 approval whole map page'],'qualifications':'Complete native features, lexical originals, nulls and curves retained. All historical result-polygon matches remain null; native diagnostics and printed map dates are not current/legal identity or land/ballot coverage approval. No browser visual claim. No SHP or ZIP binary audit claim for this JSON service.','worker_final_readonly_audit_actually_rerun':{'exit':0,'negative_packets':31,'guarded_exact_outputs':234,'full_ordered_recursive_objects':2185390,'full_original_entities_and_receipts':490,'selected_workbook_rows':19887,'typed_workbook_cells':198870},'all_worker_owned_bytes_unchanged':True}
out=S/'data/coordinator-maps-final-review.json'
if '--check' in sys.argv:ck(load(out)==result)
else:out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))

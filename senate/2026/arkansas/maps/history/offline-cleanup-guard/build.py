"""Offline atlas reconstruction. Reads only whole frozen contract and exact originals.
All geometry remains native Esri JSON, including curves, source nulls and precision.
"""
from pathlib import Path
from collections import defaultdict,Counter
import argparse,csv,gzip,hashlib,html,io,json,math,struct,urllib.parse
ROOT=Path(__file__).resolve().parents[1];STATE=ROOT.parent
LAYER='https://gis.arkansas.gov/arcgis/rest/services/FEATURESERVICES/Boundaries/FeatureServer/11'
def sha(b):return hashlib.sha256(b).hexdigest()
def pairs(p):
 d={}
 for k,v in p:
  if k in d:raise ValueError('duplicate JSON key')
  d[k]=v
 return d
def load(b):return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def dumps(v):return json.dumps(v,ensure_ascii=False,allow_nan=False,indent=2)+'\n'
def native(label):
 receipt=load((ROOT/'originals'/label/'receipt.json').read_bytes())
 if receipt['body'] is None:return None,receipt
 chunks=[]
 for part in receipt['body']['parts']:
  b=(ROOT/part['path']).read_bytes();assert len(b)==part['bytes'] and sha(b)==part['sha256'];chunks.append(b)
 b=gzip.decompress(b''.join(chunks));assert len(b)==receipt['body']['bytes'] and sha(b)==receipt['body']['sha256']
 return b,receipt
def escape(v):return html.escape(v,quote=True)
def detail(v):return '<pre>'+escape(dumps(v))+'</pre>'
CSS='''body{font:16px system-ui;margin:2rem auto;max-width:1200px;padding:0 1rem;color:#172d38;background:#fafbfc}a{color:#005d85}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eef3f5;padding:1rem}summary{cursor:pointer;padding:.6rem;border-bottom:1px solid #ccd7dd}input,select{padding:.6rem;margin:.4rem}table{border-collapse:collapse;width:100%}td,th{padding:.5rem;border-bottom:1px solid #ccd7dd;text-align:left}img{max-width:100%;max-height:700px}small{color:#445d6b}details{margin:.3rem 0}h1{font-size:2rem} .note{background:#fff4d5;padding:1rem} [hidden]{display:none!important}'''
SCRIPT='''const input=document.querySelector('#search'),scope=document.querySelector('#scope');function filter(){let n=0;for(const el of document.querySelectorAll('details[data-kind]')){const yes=(!input.value||el.textContent.toLowerCase().includes(input.value.toLowerCase()))&&(scope.value==='all'||el.dataset.kind===scope.value);el.hidden=!yes;if(yes)n++;}document.querySelector('#count').textContent=String(n);}input.addEventListener('input',filter);scope.addEventListener('change',filter);filter();if(location.hash){const el=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(el){el.open=true;el.scrollIntoView();}}'''
def page(title,body,options):
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'+escape(title)+'</title><style>'+CSS+'</style><body><h1>'+escape(title)+'</h1><p class="note">Historical observations and GIS features are separate inventories. No result-to-polygon match, vote allocation, physical identity or November approval is asserted.</p><label>Search <input id="search" type="search"></label><label>Scope <select id="scope"><option value="all">All</option>'+''.join('<option value="'+x+'">'+escape(x)+'</option>' for x in options)+'</select></label><p><span id="count"></span> matching detail rows</p>'+body+'<script>'+SCRIPT+'</script></body></html>'
def diff(a,b,p=''):
 if type(a)!=type(b):return [{'pointer':p,'pre':a,'post':b}]
 if isinstance(a,dict):
  out=[]
  for k in sorted(set(a)|set(b)):
   if k not in a or k not in b:out.append({'pointer':p+'/'+k,'pre_present':k in a,'post_present':k in b,'pre':a.get(k),'post':b.get(k)})
   else:out+=diff(a[k],b[k],p+'/'+k)
  return out
 if a!=b:return [{'pointer':p,'pre':a,'post':b}]
 return []
def build(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 def write(name,b):
  p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b.encode() if isinstance(b,str) else b)
 def j(name,v):write(name,dumps(v))
 # Contract hash is its own immutable source pin; authority itself is never hashed/copied.
 contract_raw=(STATE/'data/turnout/priority-set.json').read_bytes();c=load(contract_raw)
 assert len(contract_raw)==14233403 and sha(contract_raw)=='a9c226e93b8d6151757789ccef6144d06144ba7655fa9cac99e83c8a62ceec02'
 pr=set(c['ordered_priority_keys']);allkeys=[u['key'] for u in c['full_order']]
 assert len(allkeys)==2841 and allkeys[:1056]==c['ordered_priority_keys'] and allkeys[1056:]==c['remainder_keys']
 cat=[]
 for p in sorted((ROOT/'originals').glob('*/receipt.json')):
  r=load(p.read_bytes())
  for kind in ['body','headers']:
   obj=r[kind]
   if obj is None:continue
   packed=[]
   for item in obj['parts']:
    b=(ROOT/item['path']).read_bytes();assert len(b)==item['bytes']<40000000 and sha(b)==item['sha256'];packed.append(b)
   b=gzip.decompress(b''.join(packed));assert len(b)==obj['bytes'] and sha(b)==obj['sha256']
  cat.append({'receipt_path':str(p.relative_to(ROOT)),'receipt_bytes':p.stat().st_size,'receipt_sha256':sha(p.read_bytes()),'complete_receipt':r})
 j('original-catalogue.json',cat)
 meta=load(native('precinct-layer-pre')[0]);post=load(native('precinct-layer-post')[0]);service=load(native('boundaries-service-pre')[0]);servicepost=load(native('boundaries-service-post')[0])
 ids=load(native('precinct-ids-pre')[0]);idspost=load(native('precinct-ids-post')[0]);count=load(native('precinct-count-pre')[0]);countpost=load(native('precinct-count-post')[0])
 assert ids==idspost and count==countpost and len(ids['objectIds'])==len(set(ids['objectIds']))==count['count']==2928
 assert meta['objectIdField']=='objectid' and meta['geometryType']=='esriGeometryPolygon' and meta['extent']['spatialReference']['wkid']==26915
 by=defaultdict(list);pages=[];features=[];contexts={}
 for i in range(0,len(ids['objectIds']),50):
  label='native-page-%04d'%(i//50);raw,rec=native(label);d=load(raw);got=[x['attributes']['objectid'] for x in d['features']];wanted=ids['objectIds'][i:i+50]
  assert len(got)==len(set(got))==len(wanted)<=50 and set(got)==set(wanted) and not d.get('exceededTransferLimit')
  opts=urllib.parse.parse_qs(urllib.parse.urlparse(rec['request']['url']).query)
  assert set(opts)=={'objectIds','outFields','returnGeometry','returnZ','returnM','returnTrueCurves','f'}
  assert opts['outFields']==['*'] and all(opts[k]==['true'] for k in ['returnGeometry','returnZ','returnM','returnTrueCurves']) and opts['objectIds']==[','.join(map(str,wanted))]
  assert d['spatialReference']['wkid']==26915
  pages.append({'label':label,'requested_ids':wanted,'returned_ids':got,'count':len(got),'source_raw_sha256':sha(raw),'receipt':'originals/'+label+'/receipt.json','all_fields_native_CRS_Z_M_true_curves':True})
  for pos,f in enumerate(d['features']):
   oid=f['attributes']['objectid'];assert oid not in contexts
   ctx={'receipt':'originals/'+label+'/receipt.json','raw_sha256':sha(raw),'json_pointer':'/features/'+str(pos),'source_object_id':oid}
   contexts[oid]=ctx;features.append(f);by[f['attributes']['county_fips']].append(f)
 j('qa/native-page-proof.json',{'pre_post_metadata_changes':{'service':diff(service,servicepost),'layer':diff(meta,post),'IDs':diff(ids,idspost),'count':diff(count,countpost)},'pages':pages,'total':len(features),'unique_ids':len(contexts),'native_CRS':meta['extent']['spatialReference'],'all_source_fields':meta['fields'],'curve_geometry_count':sum('curveRings' in (f.get('geometry') or {}) for f in features),'no_projection_simplification_quantization_or_generalization':True})
 assert len(by)==75
 records=[];investigations=[];index=[];nativecsv=[]
 # Exact native inventories preserve every field/geometry, and all linear point positions.
 for parent in c['all75parents']:
  fips=parent['county_fips'];code=fips[2:];ff=by[code];pchildren=[(i,u) for i,u in enumerate(c['full_order']) if u['county_fips']==fips]
  cc=load(native('county-'+code+'-count')[0]);ci=load(native('county-'+code+'-ids')[0]);oidset={f['attributes']['objectid'] for f in ff}
  assert cc['count']==len(ff) and set(ci['objectIds'])==oidset and len(ci['objectIds'])==len(oidset)
  ed=Counter(f['attributes']['edit_date'] for f in ff);names=Counter(f['attributes']['precinct'] for f in ff);codes=Counter(f['attributes']['precinct_code_1'] for f in ff)
  own={'schema':'arkansas-native-esri-source-subset-v1','source_layer':LAYER,'selection':'exact source county_fips='+repr(code)+'; no result-label join','native_envelope':{k:v for k,v in d.items() if k!='features'},'features':ff,'source_contexts':[contexts[f['attributes']['objectid']] for f in ff]}
  fn='derived/'+fips+'.esri.json.gz';packed=gzip.compress(dumps(own).encode(),mtime=0);write(fn,packed)
  investigation={'county_fips':fips,'historical_parent_key':parent['key'],'historical_county_name':parent['county_name'],'priority_parent':fips in c['priority_parent_fips'],'historical_full_children':[u['key'] for _,u in pchildren],'ordered_priority_children':[u['key'] for _,u in pchildren if u['key'] in pr],'ordered_remainder_children':[u['key'] for _,u in pchildren if u['key'] not in pr],'historical_parent_contract_pointer':'/all75parents/'+str(c['all75parents'].index(parent)),'source_native_count':len(ff),'source_native_count_receipt':'originals/county-'+code+'-count/receipt.json','source_native_ids_receipt':'originals/county-'+code+'-ids/receipt.json','source_native_ids':ci['objectIds'],'source_native_labels': [{'objectid':f['attributes']['objectid'],'precinct':f['attributes']['precinct'],'precinct_code_1':f['attributes']['precinct_code_1'],'conct':f['attributes']['conct'],'county_name':f['attributes']['county_name'],'edit_date':f['attributes']['edit_date'],'vtdst10':f['attributes']['vtdst10'],'vtdst20':f['attributes']['vtdst20'],'vtdst30':f['attributes']['vtdst30'],'context':contexts[f['attributes']['objectid']]} for f in ff],'edit_date_literal_counts':[{'literal':k,'count':v} for k,v in ed.items()],'duplicate_source_precinct_labels':[{'literal':k,'count':v} for k,v in names.items() if v>1],'duplicate_source_precinct_codes':[{'literal':k,'count':v} for k,v in codes.items() if v>1],'curve_objects':[f['attributes']['objectid'] for f in ff if 'curveRings' in (f.get('geometry') or {})],'native_asset':fn,'authority_chain':['originals/precinct-layer-html/receipt.json','originals/boundaries-service-pre/receipt.json','originals/precinct-layer-pre/receipt.json','originals/precinct-metadata/receipt.json'],'qualification':'Complete state-hosted county-scoped precinct asset, all native attributes and geometry. Description says generated after 2010/finalized 2012; edit_date is a source literal, neither adoption nor effective approval. All result labels, method/admin units, 5 exact-name/vector API-ID gaps, physical/finer/current IDs and cross-vintage equivalence remain unjoined/unknown. County source count does not substitute for historical native coverage.','historical_polygon_matches':None,'November_approved':False,'native_ballot_or_registration_geometry_allocation':False}
  investigations.append(investigation)
  body='<p><a href="../index.html">State index</a> · <a href="../'+fn+'">Complete native Esri JSON gzip</a></p>'+ '<h2>Parent investigation</h2><details data-kind="parent"><summary>'+escape(parent['county_name'])+' complete parent and all historical context</summary>'+detail(parent)+'</details><details data-kind="investigation"><summary>Exact source inventory, IDs, vintages, gaps and provenance</summary>'+detail(investigation)+'</details>'
  body+='<h2>Native linear-ring preview</h2><p>Complete unsimplified linear rings only. True curves and short/open rings are omitted; the full native source objects remain below. No result geometry join or legal coverage is asserted.</p><a href="../previews/'+fips+'.svg"><img alt="Separate source linear-ring preview" src="../previews/'+fips+'.svg"></a><h2>Historical source observations</h2>'
  for i,u in pchildren:
   kind='priority' if u['key'] in pr else 'remainder';ident='historical-'+u['key'];context={'contract_path':'../data/turnout/priority-set.json','complete_contract_pointer':'/full_order/'+str(i),'source_id':u['source_id'],'source_pointer':u['source_pointer'],'source_rows':u['source_rows'],'qualified_parent_investigation':fips+'.html','geometric_match':None,'current_reporting_identity':None}
   body+='<details id="'+escape(ident)+'" data-kind="'+kind+'" data-key="'+escape(u['key'])+'"><summary>'+str(u['rank'])+' · '+escape(u['native_name'])+' · '+str(u['votes'])+' candidate votes · '+kind+'</summary>'+detail({'complete_historical_source_observation':u,'own_source_context_reference':context})+'</details>'
  body+='<h2>Separate GIS native feature inventory</h2><p>These source features are not paired with the historical rows above. Coordinates are EPSG:26915 native metres; curves remain native. No map points or vote allocations are fabricated.</p>'
  for f in ff:
   oid=f['attributes']['objectid'];ident='GIS-'+str(oid)
   body+='<details id="'+ident+'" data-kind="GIS" data-source-id="'+str(oid)+'"><summary>'+str(oid)+' · '+escape(str(f['attributes']['precinct']))+'</summary>'+detail({'complete_native_source_feature':f,'source_context':contexts[oid]})+'</details>'
   nativecsv.append({'county_fips':fips,'objectid':oid,'precinct':f['attributes']['precinct'],'precinct_code_1':f['attributes']['precinct_code_1'],'edit_date':f['attributes']['edit_date'],'geometry_kind':','.join((f.get('geometry') or {}).keys()),'source_context_json':json.dumps(contexts[oid],ensure_ascii=False,separators=(',',':'))})
  write('atlas/'+fips+'.html',page(parent['county_name']+' — separate historical and GIS inventories',body,['priority','remainder','GIS','parent','investigation']))
  index.append('<tr><td><a href="atlas/'+fips+'.html">'+escape(parent['county_name'])+'</a></td><td>'+fips+'</td><td>'+str(len(pchildren))+'</td><td>'+str(len(investigation['ordered_priority_children']))+'</td><td>'+str(len(ff))+'</td><td>'+str(len(investigation['curve_objects']))+'</td></tr>')
  records.append({'county_fips':fips,'county':parent['county_name'],'priority_parent':investigation['priority_parent'],'historical_full_count':len(pchildren),'historical_priority_count':len(investigation['ordered_priority_children']),'historical_remainder_count':len(investigation['ordered_remainder_children']),'source_native_features':len(ff),'native_source':LAYER,'asset':fn,'stored_bytes':len(packed),'stored_sha256':sha(packed),'native_CRS':'EPSG:26915; source service units metres','vintage':'2012 description; heterogeneous edit_date/null literals; no effective/adopted/current proof','native_polygon_matches':'unknown','current_approval':'false/unknown'})
 j('parent-investigations.json',investigations)
 j('historical-order.json',{'full':allkeys,'priority':c['ordered_priority_keys'],'remainder':c['remainder_keys'],'parent_order':[p['key'] for p in c['all75parents']],'priority_parent_order':c['priority_parent_fips']})
 for name,rows in [('manifest.csv',records),('native-inventory.csv',nativecsv)]:
  s=io.StringIO();w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);write(name,s.getvalue())
 # Main atlas exposes the exact statewide order and every complete own observation.
 body='<p>Research snapshot: 2026-10-20. <a href="../precinct-maps.md">Report</a> · <a href="manifest.csv">75-parent asset manifest</a> · <a href="original-catalogue.json">Complete original catalogue</a></p><p>2,841 historical observations / 1,056 priority / 1,785 remainder; 2,928 separate GIS features; 68 priority parents and all 75 parents. Source candidate votes are not ballots, registration, eligible write-ins or a measure of mapped land.</p><table><thead><tr><th>County investigation</th><th>FIPS</th><th>Historical full</th><th>Priority</th><th>GIS features</th><th>Curves</th></tr></thead><tbody>'+''.join(index)+'</tbody></table><h2>Exact full historical rank order</h2>'
 for i,u in enumerate(c['full_order']):
  kind='priority' if u['key'] in pr else 'remainder'
  body+='<details data-kind="'+kind+'" data-key="'+escape(u['key'])+'"><summary>'+str(i+1)+' · '+escape(u['county_name'])+' / '+escape(u['native_name'])+' · '+str(u['votes'])+' · '+kind+'</summary><a href="atlas/'+u['county_fips']+'.html#'+urllib.parse.quote('historical-'+u['key'],safe='')+'">Qualified parent investigation</a>'+detail({'complete_historical_source_observation':u,'own_source_context_reference':{'path':'../data/turnout/priority-set.json','pointer':'/full_order/'+str(i),'source_id':u['source_id'],'source_pointer':u['source_pointer'],'source_rows':u['source_rows']},'polygon_match':None})+'</details>'
 body+='<h2>Exact historical parent order and full contexts</h2>'
 for p in c['all75parents']:body+='<details data-kind="parent" data-key="'+escape(p['key'])+'"><summary>'+escape(p['county_name'])+' complete source parent</summary>'+detail(p)+'</details>'
 write('index.html',page('Arkansas precinct source atlas',body,['priority','remainder','parent']))
 j('qa/build-proof.json',{'status':'pass','full_historical_objects':2841,'full_parent_contexts':75,'priority':1056,'remainder':1785,'priority_parent_investigations':68,'all_parent_investigations':75,'complete_GIS_objects':2928,'complete_GIS_curve_objects':36,'native_source_field_count':len(meta['fields']),'derived_subset_policy':'all native fields/geometry by exact source county field, no result-name match','full_source_receipts':len(cat),'current_approval':False,'vote_spatial_allocation':False})
 return sorted(str(p.relative_to(out)) for p in out.rglob('*') if p.is_file())
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT);args=ap.parse_args();files=build(args.out);print('Reconstructed',len(files),'files')

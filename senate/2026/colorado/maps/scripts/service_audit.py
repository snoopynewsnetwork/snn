"""Offline service replay of complete raw pages, full attributes and native geometry."""
import json,collections
import shapefile
from acquire import ROOT,body,sha
from geometry import topology

def run():
 out=[];sets={};top=[]
 for f in sorted((ROOT/'raw').glob('*.service.json')):
  s=json.loads(f.read_text());assert not s.get('failure'),s
  k=s['id'];pre=json.loads(body(k+'-meta-pre'));post=json.loads(body(k+'-meta-post'));assert pre==post
  ids=json.loads(body(k+'-ids-pre'));ids2=json.loads(body(k+'-ids-post'));c=json.loads(body(k+'-count-pre'));c2=json.loads(body(k+'-count-post'))
  assert set(ids['objectIds'])==set(ids2['objectIds']) and c==c2 and len(ids['objectIds'])==c['count'];oid=ids['objectIdFieldName']
  fields=[x['name'] for x in pre['fields']];features=[];seen=[];audit=[];native=[];curves=[]
  for key in s['pages']:
   d=json.loads(body(key));r=json.loads((ROOT/'raw'/f'{key}.receipt.json').read_text());assert not d.get('exceededTransferLimit',False)
   from urllib.parse import urlparse,parse_qs
   params=parse_qs(urlparse(r['url']).query);wanted=list(map(int,params['objectIds'][0].split(',')));assert len(wanted)<=50
   assert not set(params)&{'outSR','geometryPrecision','maxAllowableOffset','quantizationParameters','resultRecordCount'}
   assert params['returnTrueCurves']==['true'] and params['returnZ']==['true'] and params['returnM']==['true'] and params['outFields']==['*']
   pageids=[x['attributes'][oid] for x in d['features']];assert set(pageids)==set(wanted) and len(pageids)==len(wanted);seen+=pageids
   for i,x in enumerate(d['features']):
    assert set(x['attributes'])==set(fields),(k,set(fields)-set(x['attributes']))
    g=x.get('geometry');rows=0;parts=0
    if g and 'curveRings'in g:curves.append(x['attributes'][oid])
    elif g and 'rings'in g:
     rings=g['rings'];parts=len(rings);rows=sum(map(len,rings));pts=[];starts=[]
     for ring in rings:starts.append(len(pts));pts.extend([p[:2] for p in ring])
     shape=shapefile.Shape(shapeType=5,points=pts,parts=starts);native.append((shape,x['attributes']))
    audit.append(dict(page=key,index=i,object_id=x['attributes'][oid],complete_feature_semantic_sha256=sha(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()),native_geometry_sha256=sha(json.dumps(g,sort_keys=True,separators=(',',':'),allow_nan=False).encode()),parts=parts,coordinate_positions=rows))
   features+=d['features']
  assert set(seen)==set(ids['objectIds']) and len(seen)==len(set(seen))==s['count']
  out.append(dict(source=k,county=s['county'],feature_count=len(features),fields=pre['fields'],source_crs=pre.get('sourceSpatialReference',pre.get('extent',{}).get('spatialReference')),hasZ=pre.get('hasZ'),hasM=pre.get('hasM'),editingInfo=pre.get('editingInfo'),true_curve_features=curves,raw_page_references=s['pages'],features=audit,full_attributes_preserved=True,pre_post_metadata_equal=True,pre_post_count_and_ids_equal=True,all_requested_ids_equal=True,query_has_no_precision_transform=True))
  sets[k]=native;top.append(dict(source=k,curve_features_excluded=curves,**topology(native,out[-1]['source_crs'])))
 return out,top,sets
if __name__=='__main__':
 a,t,c=run();(ROOT/'qa/service-audit.json').write_text(json.dumps(a,indent=2)+'\n');(ROOT/'qa/service-topology.json').write_text(json.dumps(t,indent=2)+'\n');print([(x['source'],x['feature_count']) for x in a])

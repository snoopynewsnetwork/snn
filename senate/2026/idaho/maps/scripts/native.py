#!/usr/bin/env python3
"""Verify exact public ArcGIS pages; derive unmodified native-coordinate diagnostics."""
import collections,gzip,hashlib,json,math,struct,sys
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from verify_history import semantic
MAPS=Path(__file__).resolve().parents[1];ROOT=MAPS.parent

def body(r):
 b=(ROOT/r['asset_path']).read_bytes();assert len(b)==r['stored_bytes']<40000000 and hashlib.sha256(b).hexdigest()==r['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==r['raw_bytes'] and hashlib.sha256(raw).hexdigest()==r['raw_sha256'];return raw

def receipts():return [json.loads(p.read_text()) for p in sorted((MAPS/'source').glob('native-*.receipt.json'))]
def verify(records=None):
 records=records or receipts();rs={r['id']:r for r in records};raw={r['id']:body(r) for r in records}
 j={k:json.loads(b) for k,b in raw.items() if k not in ['sos-map-data-parent','state-precinct-Hub-page']}
 hub=rs['state-precinct-Hub-page'];assert hub['url'] in raw['sos-map-data-parent'].decode()
 item=j['state-precinct-item-metadata'];assert item['id']=='0b4fbe4f3104487da8bc5087f9321705' and item['access']=='public'
 assert item['id']+'_0' in hub['url']
 layer=item['url']+'/0';meta=j['state-precinct-layer-metadata'];assert rs['state-precinct-layer-metadata']['url'].split('?')[0]==layer
 assert meta==j['state-precinct-metadata-post']
 assert j['state-precinct-count-pre']==j['state-precinct-count-post']=={'count':976}
 assert j['state-precinct-ids-pre']==j['state-precinct-ids-post'];ids=j['state-precinct-ids-pre']['objectIds'];assert len(ids)==len(set(ids))==976
 assert meta['objectIdField']=='OBJECTID' and meta['spatialReference']=={'wkid':102605,'latestWkid':8826}
 fields=[f['name'] for f in meta['fields']];assert len(fields)==10
 feats=[];page_witness=[]
 for r in sorted((r for r in records if r['id'].startswith('state-precinct-native-page')),key=lambda r:r['id']):
  q=parse_qs(urlsplit(r['url']).query);assert urlsplit(r['url']).path==urlsplit(layer+'/query').path
  assert set(q)=={'f','objectIds','outFields','returnGeometry','returnZ','returnM','returnTrueCurves'}
  assert q['outFields']==['*'] and all(q[k]==['true'] for k in ['returnGeometry','returnZ','returnM','returnTrueCurves'])
  requested=list(map(int,q['objectIds'][0].split(',')));assert requested==r['requested_object_ids'] and 0<len(requested)<=50
  p=j[r['id']];assert not p.get('exceededTransferLimit') and 'error' not in p and p['spatialReference']==meta['spatialReference']
  assert [f['name'] for f in p['fields']]==fields
  fs=p['features'];got=[f['attributes']['OBJECTID'] for f in fs];assert len(set(got))==len(got) and set(got)==set(requested)
  for f in fs:assert set(f['attributes'])==set(fields)
  feats+=fs;page_witness.append(dict(id=r['id'],requested_ids=requested,returned_ids=got,complete_page_semantic_sha256=semantic(p)))
 assert len(page_witness)==20 and len(feats)==976 and {f['attributes']['OBJECTID'] for f in feats}==set(ids)
 counties=collections.Counter(f['attributes']['COUNTY'] for f in feats);assert len(counties)==44
 assert all(f['attributes']['ACTIVE']=='Y' for f in feats)
 details=[];xy=hashlib.sha256();n=0;rings=0
 for f in feats:
  g=f.get('geometry');i=f['attributes']['OBJECTID'];d=dict(object_id=i,attributes=f['attributes'],complete_feature_semantic_sha256=semantic(f),geometry_keys=list(g) if g is not None else None,null=g is None,empty=g=={},true_curves=bool(g and 'curveRings' in g),rings=[])
  if g and 'rings' in g:
   for ring in g['rings']:
    rings+=1;ringhash=hashlib.sha256();n+=len(ring)
    for pos in ring:
     assert all(isinstance(v,(float,int)) and math.isfinite(v) for v in pos)
     for v in pos:packed=struct.pack('>d',v);xy.update(packed);ringhash.update(packed)
    d['rings'].append(dict(positions=len(ring),dimensions=sorted(set(map(len,ring))),closed=bool(ring and ring[0]==ring[-1]),xy_double_sha256=ringhash.hexdigest(),signed_native_area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]))/2))
  details.append(d)
 assert rings==1032 and n==749523
 return feats,dict(status='pass_original_native_acquisition',authority_chain='sos-map-data-parent -> state-precinct-Hub-page -> public item -> configured literal service/layer0',layer_url=layer,feature_count=976,county_counts=dict(sorted(counties.items())),fields=fields,crs=meta['spatialReference'],hasZ=meta['hasZ'],hasM=meta['hasM'],editingInfo=meta['editingInfo'],metadata_clock_not_legal_vintage=True,page_checks=page_witness,rings=rings,original_coordinate_positions=n,ordered_all_native_double_sha256=xy.hexdigest(),null_geometries=sum(d['null'] for d in details),empty_geometries=sum(d['empty'] for d in details),true_curve_features=sum(d['true_curves'] for d in details),open_rings=sum(not r['closed'] for d in details for r in d['rings']),complete_features=details,source_originals_unchanged=True,historical_crosswalk=None,current_legal_approval=None)

def freeze_preparation():
 # Optional preparation used once. Every full individual receipt becomes an immutable owned dependency;
 # subsequent build/validation does not read any preparation manifest or coordinator review.
 prep=json.loads((ROOT/'data/coordinator-map-preparation/acquisition-native-stage-v1.json').read_text())
 for r in prep:
  if r['id']=='sos-current-results-parent':continue
  body(r);p=MAPS/'source'/('native-'+r['id']+'.receipt.json');encoded=(json.dumps(r,indent=2,ensure_ascii=False)+'\n').encode()
  if p.exists():assert p.read_bytes()==encoded
  else:p.write_bytes(encoded)
if __name__=='__main__':
 if '--freeze-preparation' in sys.argv:freeze_preparation()
 feats,qa=verify();b=(json.dumps(qa,indent=2,ensure_ascii=False)+'\n').encode()
 if '--write' in sys.argv:(MAPS/'qa/native-verification.json').write_bytes(b)
 print(json.dumps({k:v for k,v in qa.items() if k not in ['complete_features','page_checks','county_counts']}))

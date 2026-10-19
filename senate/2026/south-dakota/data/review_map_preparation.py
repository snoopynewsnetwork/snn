"""Replay complete native capture proofs without network or geometry repair."""
from pathlib import Path
import hashlib,gzip,json
D=Path(__file__).resolve().parent;S=D.parent;O=D/'coordinator-map-preparation'
def main():
 a=json.loads((O/'acquisition-native-stage-v1.json').read_bytes());r={x['id']:x for x in a};out={}
 def raw(k):
  x=r[k];z=(S/x['asset_path']).read_bytes();b=gzip.decompress(z);assert len(z)==x['stored_bytes']and hashlib.sha256(z).hexdigest()==x['stored_sha256']and len(b)==x['raw_bytes']and hashlib.sha256(b).hexdigest()==x['raw_sha256'];return b
 def obj(k):return json.loads(raw(k))
 for x in a:
  if 'asset_path'in x:raw(x['id'])
 for name in ['minnehaha','pennington']:
  pre=obj(name+'-ids-pre');post=obj(name+'-ids-post');ids=pre['objectIds'];assert ids==post['objectIds']and len(ids)==len(set(ids))==obj(name+'-count-pre')['count']==obj(name+'-count-post')['count']
  meta=obj(name+'-layer-metadata');assert raw(name+'-layer-metadata')==raw(name+'-metadata-post');features=[];pages=[]
  for x in a:
   if x['id'].startswith(name+'-native-page'):
    d=obj(x['id']);assert 'error'not in d and not d.get('exceededTransferLimit');returned=[f['attributes'][pre['objectIdFieldName']]for f in d['features']];assert set(returned)==set(x['requested_object_ids'])and len(returned)==len(set(returned))<=50;features+=d['features'];pages.append(dict(source_id=x['id'],requested_ids=x['requested_object_ids'],returned_ids=returned,spatialReference=d.get('spatialReference')))
  assert len(features)==len(ids)and {f['attributes'][pre['objectIdFieldName']]for f in features}==set(ids)
  out[name]=dict(features=len(features),metadata_exact_pre_post=True,counts_IDs_exact_pre_post=True,pages=pages,metadata_CRS=meta.get('extent',{}).get('spatialReference'),all_field_names=[x['name']for x in meta['fields']],null_geometry=sum(f.get('geometry')is None for f in features),true_curve_features=sum('curveRings'in(f.get('geometry')or{})for f in features),ring_positions=sum(sum(len(ring)for ring in(f.get('geometry')or{}).get('rings',[]))for f in features),source_generalization_unknown=True,geography_crosswalk_approved=False)
 p=D/'coordinator-map-native-preparation-review.json';b=(json.dumps(dict(status='pass_original_native_capture_scope_only',request_observations=len(a),native_layers=out,complete_PDF_originals=['minnehaha-county-PDF','minnehaha-city-PDF'],all_errors_retained=True,mutating_or_repairing_geometry=False,counts_are_current_published_source_not_historical_crosswalk=True),indent=2)+'\n').encode();assert p.read_bytes()==b
 print(json.dumps(dict(path=str(p.relative_to(S)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())))
if __name__=='__main__':main()

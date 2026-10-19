"""Replay exact source batches; preparation, not a reporting/geographic join."""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json
D=Path(__file__).resolve().parent;S=D.parent;O=D/'coordinator-map-preparation'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def freeze(p,b):
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
def main():
 raw=(O/'acquisition.json').read_bytes();freeze(O/'acquisition-native-stage-v1.json',raw);rows=json.loads(raw);mf={r['id']:r for r in rows}
 def read(k):
  r=mf[k];p=S/r['asset_path'];z=p.read_bytes();b=gzip.decompress(z);assert len(z)==r['stored_bytes']and sha(z)==r['stored_sha256']and len(b)==r['raw_bytes']and sha(b)==r['raw_sha256'];assert len(z)<40_000_000;return b
 for r in rows:
  if 'asset_path'in r:read(r['id'])
 result=[]
 for key,expected in [('lancaster-native-layer',222),('douglas-native-layer',234)]:
  get=lambda suffix:json.loads(read(key+suffix));meta=get('-metadata');assert meta==get('-metadata-post');ids=get('-ids-pre')['objectIds'];assert sorted(ids)==sorted(get('-ids-post')['objectIds'])and len(ids)==len(set(ids))==get('-count-pre')['count']==get('-count-post')['count']==expected
  oid=next(f['name']for f in meta['fields']if f['type']=='esriFieldTypeOID');fields={f['name']for f in meta['fields']if f['type']!='esriFieldTypeGeometry'};seen=set();features=[];xy=0;curves=0;empty=0;flags=[];source_pages=[];sr=[]
  for r in rows:
   if not r['id'].startswith(key+'-native-page-'):continue
   x=json.loads(read(r['id']));assert 'error'not in x and not x.get('exceededTransferLimit',False);flags.append(x.get('exceededTransferLimit'));requested=r['requested_object_ids'];assert len(requested)<=50
   assert set(requested)=={f['attributes'][oid]for f in x['features']};assert not seen.intersection(requested);seen.update(requested);sr.append(x['spatialReference'])
   for f in x['features']:
    assert set(f['attributes'])==fields;g=f.get('geometry');empty+=not bool(g);curves+=bool(g and'curveRings'in g)
    if g and'rings'in g:xy+=sum(len(ring)for ring in g['rings'])
    features.append(dict(source_page=r['id'],source_object_ID=f['attributes'][oid],complete_feature_object_sha256=sha(json.dumps(f,sort_keys=True,separators=(',',':')).encode()),complete_attributes_sha256=sha(json.dumps(f['attributes'],sort_keys=True,separators=(',',':')).encode()),geometry_kind=list(g)if g else None))
   source_pages.append(dict(id=r['id'],asset_path=r['asset_path'],raw_bytes=r['raw_bytes'],raw_sha256=r['raw_sha256'],stored_sha256=r['stored_sha256']))
  assert seen==set(ids)and len(features)==expected and all(x==sr[0]for x in sr)
  result.append(dict(layer=key,source_name=meta['name'],native_feature_count=expected,object_ID_field=oid,all_original_attribute_fields=sorted(fields),source_CRS=sr[0],complete_pre_post_metadata_equal=True,complete_pre_post_counts_IDsets_equal=True,bounded_native_pages=len(source_pages),maximum_requested_IDs=50,returned_transfer_limit_flags=flags,native_linear_XY_positions=xy,returned_curve_features=curves,empty_geometries=empty,complete_source_pages=source_pages,complete_feature_fingerprints=features,original_requests_return_all_attrs_geometry_Z_M_truecurves=True,no_output_CRS_or_precision_rounding_quantization_requested=True))
 census=json.loads(gzip.decompress((O/'census-native-structure.json.gz').read_bytes()));assert census['native_features']==1402 and census['county_count']==93
 out=dict(status='pass_bounded_original_map_preparation_not_current_crosswalk',immutable_source_receipts=pin(O/'acquisition-native-stage-v1.json'),observations=len(rows),HTTP_outcomes=dict(Counter(str(r['status'])for r in rows)),native_layers=result,Census_fallback=dict(original_archive=mf['census-nebraska-vtd20'],structure_audit=pin(O/'census-native-structure.json.gz'),features=1402,counties=93,vintage='2020 Census VTD; no2024 or2026 identity approval'),approved_current_or_historical_reporting_matches=0,qualification='Both county layers follow actual official parent/app/config/webmap routes. Raw Lancaster parent/PDF403 and separate web-reader page/PDF evidence stay distinct; no PDF original was obtained through those blocked requests. Source-native geometry/attrs unmodified, CRS distinct. Counts234/222 differ from historical233/198 and establish no crosswalk. Native topology/overlap/precision/current legal scope still for map worker independent review.')
 p=D/'coordinator-map-native-preparation-review.json';freeze(p,(json.dumps(out,indent=2)+'\n').encode());print(json.dumps(pin(p)))
if __name__=='__main__':main()

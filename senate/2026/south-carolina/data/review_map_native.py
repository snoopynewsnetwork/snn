"""Independent read-only native original/subset review; no worker-code imports."""
import gzip,hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parent
MAPS=ROOT.parent/'maps'
def load(path):
 b=path.read_bytes();return gzip.decompress(b) if path.suffix=='.gz' else b
def feature_slices(b):
 s=b.decode('utf8');m=re.search(r'"features"\s*:\s*\[',s);assert m
 decoder=json.JSONDecoder();i=m.end();out=[]
 while True:
  while s[i].isspace() or s[i]==',': i+=1
  if s[i]==']':break
  obj,end=decoder.raw_decode(s,i)
  start_byte=len(s[:i].encode('utf8'));end_byte=len(s[:end].encode('utf8'))
  out.append((obj,b[start_byte:end_byte],start_byte,end_byte));i=end
 return out

def main():
 layer=json.loads(load(MAPS/'raw/rfa-precinct-layer.body.gz'));assert layer['hasZ'] is False and layer['hasM'] is False
 ev=json.loads((MAPS/'evidence-manifest.json').read_text());capt={r['id']:r for r in ev['captures']}
 original={};metadata={};positions=0;pages=0
 aud=json.loads(load(MAPS/'native-audit.json.gz'));aud_by_id={x['OBJECTID']:x for x in aud['features']}
 for path in sorted((MAPS/'raw').glob('native-page-*.body.gz')):
  source_id=path.name.removesuffix('.body.gz');r=capt[source_id];raw=load(path)
  assert hashlib.sha256(raw).hexdigest()==r['original_sha256']
  response=json.loads(raw);assert not response.get('error') and not response.get('exceededTransferLimit') and not response.get('transform')
  assert response.get('hasZ') in [None,False] and response.get('hasM') in [None,False]
  slices=feature_slices(raw);assert len(slices)==len(response['features']);pages+=1
  for ordinal,(feature,lexeme,start,end) in enumerate(slices):
   oid=feature['attributes']['OBJECTID'];assert oid not in original
   rings=feature['geometry']['rings'];assert rings and set(feature['geometry'])=={'rings'}
   positions+=sum(len(ring) for ring in rings)
   assert all(len(coord)==2 for ring in rings for coord in ring)
   ptr=aud_by_id[oid]['original_locator'];assert ptr=={'capture':source_id,'json_pointer':f'/features/{ordinal}','byte_start_inclusive':start,'byte_end_exclusive':end,'feature_original_bytes':len(lexeme),'feature_sha256':hashlib.sha256(lexeme).hexdigest()}
   assert aud_by_id[oid]['complete_attributes']==feature['attributes']
   original[oid]=(feature,lexeme);metadata[oid]=response['spatialReference']
 pre=json.loads(load(MAPS/'raw/native-pre-ids.body.gz'))['objectIds'];post=json.loads(load(MAPS/'raw/native-post-ids.body.gz'))['objectIds']
 assert len(pre)==len(post)==len(original)==2315 and set(pre)==set(post)==set(original)
 inventory=json.loads((MAPS/'county-geometry-inventory.json').read_text());assert len(inventory)==46
 counties={};all_partition=set();subset_count=0;subset_features=0
 for row in inventory:
  fips=row['county_fips'];ids=set(row['native_OBJECTID_set']);assert not (all_partition & ids);all_partition |= ids
  # The published CodeMapNum has a literal county-number component; this validates the worker's declared reference partition, not a reporting-unit crosswalk.
  expected={oid for oid,(f,_) in original.items() if '450'+re.fullmatch(r'P-(\d\d)-.+',f['attributes']['CodeMapNum'])[1]==fips}
  assert ids==expected and len(ids)==row['native_count'];counties[fips]=len(ids)
  if not row['in_priority']:continue
  b=load(MAPS/'derived'/f'{fips}-native.esrijson.gz');j=json.loads(b);slices=feature_slices(b)
  assert len(slices)==len(ids);actual=set()
  for feature,lexeme,_,_ in slices:
   oid=feature['attributes']['OBJECTID'];actual.add(oid);assert feature==original[oid][0] and lexeme==original[oid][1]
   assert j['spatialReference']==layer['spatialReference']
   assert all(j['spatialReference'][key]==value for key,value in metadata[oid].items())
  assert actual==ids;subset_count+=1;subset_features+=len(ids)
 assert all_partition==set(original) and subset_count==17 and subset_features==1639
 alternatives=[]
 for audit in json.loads(load(MAPS/'alternative-native-audit.json.gz')):
  source_id=audit['source_id'];seen=set();coordinate_positions=0
  pre_object=json.loads(load(MAPS/'raw'/(source_id+'-pre-ids.body.gz')));oid_field=pre_object['objectIdFieldName']
  declared={f['original_locator']['feature_sha256']:f for f in audit['features']}
  for path in sorted((MAPS/'raw').glob(source_id+'-page-*.body.gz')):
   capture_id=path.name.removesuffix('.body.gz');raw=load(path);r=capt[capture_id]
   assert hashlib.sha256(raw).hexdigest()==r['original_sha256']
   response=json.loads(raw);assert not response.get('error') and not response.get('exceededTransferLimit') and not response.get('transform')
   for ordinal,(feature,lexeme,start,end) in enumerate(feature_slices(raw)):
    digest=hashlib.sha256(lexeme).hexdigest();witness=declared[digest];ptr=witness['original_locator']
    assert ptr['capture']==capture_id and ptr['json_pointer']==f'/features/{ordinal}' and ptr['byte_start_inclusive']==start and ptr['byte_end_exclusive']==end
    assert ptr['feature_original_bytes']==len(lexeme) and witness['attributes']==feature['attributes']
    oid=feature['attributes'][oid_field];assert oid not in seen;seen.add(oid)
    coordinate_positions+=sum(len(ring) for ring in feature['geometry']['rings'])
  pre=json.loads(load(MAPS/'raw'/(source_id+'-pre-ids.body.gz')))['objectIds']
  post=json.loads(load(MAPS/'raw'/(source_id+'-post-ids.body.gz')))['objectIds']
  assert set(pre)==set(post)==seen==set(audit['all_ids']) and len(seen)==audit['geometry_count']
  alternatives.append({'source_id':source_id,'native_id_field':oid_field,'features':len(seen),'coordinate_positions':coordinate_positions,'scope':'Independent local schema/CRS; no historical or current reporting join.'})
 result={'status':'pass_native_original_bytes_and_exact_subsets','original_pages':pages,'statewide_features':len(original),'all46_partition_features':sum(counties.values()),'priority_counties':subset_count,'priority_features':subset_features,'coordinate_positions':positions,'checks':['Every original decoded-entity hash','Pre/post complete original ID sets','All original attributes and coordinate values','Independent JSON lexeme start/end/full SHA and raw pointer','Every selected subset feature lexeme byte-identical','Native CRS including precision metadata conserved','All46 original CodeMapNum reference partitions unique/complete'],'scope':'Reference-map partition only. No approved reporting-unit/current-November/crossyear join or topology repair inferred.','county_alternative_originals':alternatives,'topology':'Worker GEOS defects remain disclosed separately; this validator preserves their original bytes.'}
 (ROOT/'coordinator-map-native-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()

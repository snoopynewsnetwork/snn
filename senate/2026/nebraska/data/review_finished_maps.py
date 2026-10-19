"""Producer-free map/contract/original-binary audit; never mutate map assets."""
from pathlib import Path
from collections import Counter
import ast,gzip,hashlib,io,json,struct,zipfile
from shapely.geometry import Polygon,MultiPolygon,Point
from shapely.strtree import STRtree
D=Path(__file__).resolve().parent;S=D.parent;M=S/'maps'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def canonical(x):return sha(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
def nodes(x):return 1+sum(nodes(v)for v in(x.values()if isinstance(x,dict)else x))if isinstance(x,(list,dict))else 1
def body(r):
 if 'storage'in r:
  parts=[]
  for x in r['storage']:
   b=(S/x['path']).read_bytes();assert len(b)==x['bytes']and sha(b)==x['sha256'];parts.append(b)
  raw=gzip.decompress(b''.join(parts));assert len(raw)==r['original_bytes']and sha(raw)==r['original_sha256'];return raw
 z=(S/r['asset_path']).read_bytes();raw=gzip.decompress(z);assert len(z)==r['stored_bytes']and sha(z)==r['stored_sha256']and len(raw)==r['raw_bytes']and sha(raw)==r['raw_sha256'];return raw
def main():
 mf=load(M/'asset-manifest.json');owned=mf['owned_artifacts'];refs=mf['external_original_references'];paths=set()
 for r in owned+refs:assert pin(S/r['path'])=={k:r[k]for k in ['path','bytes','sha256']}and r['bytes']<40_000_000
 for r in owned:assert r['path']not in paths;paths.add(r['path'])
 actual={str(p.relative_to(S))for p in M.rglob('*')if p.is_file()}|{'precinct-maps.md'};assert actual==paths|{'maps/asset-manifest.json'}
 assert not any(p.name in ['__pycache__','node_modules','.venv']for p in M.rglob('*'))
 for p in M.rglob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
 c=load(D/'turnout/priority-set.json');f=load(M/'frozen-references.json');assert len(f['files'])==425
 for r in f['files']:assert pin(S/r['path'])=={k:r[k]for k in ['path','bytes','sha256']}
 for r in f['complete_contract_fields']:
  x=c[r['JSON_pointer'][1:]];assert canonical(x)==r['semantic_sha256']and nodes(x)==r['recursive_nodes']
 assert sum(x['recursive_nodes']for x in f['complete_contract_fields'])==101612 and len(f['complete_contract_fields'])==len(c)==32
 idx=load(M/'index.json');parents=load(M/'parents.json');assert len(parents)==93
 for k in ['ordered_priority_keys','ordered_full_keys','ordered_remainder_keys','parent_full_child_map','parent_priority_child_map','child_parent_map']:assert idx[k]==c[k]
 assert len(idx['inventory'])==1326 and len(idx['ordered_priority_keys'])==765 and len(idx['ordered_remainder_keys'])==561
 for i,u in enumerate(idx['inventory']):
  assert u['key']==c['ordered_full_keys'][i]and canonical(c['constituents'][i])==u['complete_frozen_observation']['semantic_sha256'];assert not u['votes_allocated_to_geometry']and all(u[k]is None for k in ['entry_level_legal_match','entry_level_native_match','entry_level_physical_match','entry_level_current_match'])
 coverage=idx['resource_coverage'];assert coverage['priority_entries_with_shared_county_or_municipal_map_resource']==603 and coverage['priority_entries_Census_only']==162
 prep=load(D/'coordinator-map-preparation/acquisition-native-stage-v1.json');receipts=[load(p)for p in sorted((M/'receipts').glob('*.json'))];nativeproof={}
 for name,expected,overlap in [('douglas',234,267),('lancaster',222,132),('sarpy',81,11),('adams',22,8),('scottsbluff',32,11)]:
  rr={r['id']:r for r in(prep if name in ['douglas','lancaster']else receipts)};prefix=name+'-native-layer-';get=lambda tail:json.loads(body(rr[prefix+tail]));meta=get('metadata');assert meta==get('metadata-post');count=get('count-pre')['count'];ids=get('ids-pre');assert count==get('count-post')['count']==len(ids['objectIds'])==expected and ids==get('ids-post');features=[]
  for key,r in rr.items():
   if key.startswith(prefix+'native-page-'):
    d=json.loads(body(r));assert not d.get('error')and not d.get('exceededTransferLimit');asked=r['requested_object_ids'];assert len(asked)<=50 and set(asked)=={x['attributes'][ids['objectIdFieldName']]for x in d['features']}
    for x in d['features']:features.append(dict(source_position=x['attributes'][ids['objectIdFieldName']],**x))
  n=load(M/f'native/{name}.json.gz');assert n['features']==features and n['metadata']==meta and len(features)==expected
  geoms=[];ringcount=0;positions=0
  for x in features:
   rings=x['geometry']['rings'];assert rings;outer=[];holes=[]
   for ring in rings:
    assert len(ring)>=4 and ring[0]==ring[-1];ringcount+=1;positions+=len(ring);signed=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(ring,ring[1:]));(outer if signed<0 else holes).append(ring)
   assigned=[[]for _ in outer]
   for hole in holes:
    candidates=[(Polygon(shell).area,i)for i,shell in enumerate(outer)if Polygon(shell).covers(Point(hole[0]))];assert candidates;assigned[min(candidates)[1]].append(hole)
   ps=[Polygon(shell,assigned[i])for i,shell in enumerate(outer)];g=ps[0]if len(ps)==1 else MultiPolygon(ps);assert g.is_valid and not g.is_empty;geoms.append(g)
  tree=STRtree(geoms);pairs=0
  for i,g in enumerate(geoms):
   for j in tree.query(g):
    if j>i and g.intersection(geoms[j]).area>0:pairs+=1
  assert pairs==overlap
  nativeproof[name]=dict(features=expected,full_original_attributes_geometry_equal=True,pre_post_exact=True,rings=ringcount,positions=positions,individually_invalid=0,positive_area_pairs=pairs,native_CRS=meta['extent']['spatialReference'],reporting_crosswalk_approved=False)
 # Direct binary SHP/SHX/DBF comparison does not use PyShp or producer adapters.
 original=next(x for x in prep if x['id']=='census-nebraska-vtd20');raw=body(original);z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip()is None;files={Path(n).suffix:z.read(n)for n in z.namelist()};shp,shx,dbf=map(files.get,['.shp','.shx','.dbf']);v=load(M/'native/census-vtd20.json.gz');features=v['features'];assert len(features)==1402;pos=100;totalpoints=0;offsets=[];shapes=[]
 for f in features:
  number,length=struct.unpack_from('>II',shp,pos);at=pos+8;typ=struct.unpack_from('<I',shp,at)[0];assert typ==5;bbox=list(struct.unpack_from('<4d',shp,at+4));nparts,npoints=struct.unpack_from('<II',shp,at+36);partstart=at+44;parts=list(struct.unpack_from('<'+str(nparts)+'I',shp,partstart));pointstart=partstart+4*nparts;points=[list(x)for x in struct.iter_unpack('<2d',shp[pointstart:pointstart+16*npoints])];shape=dict(record_number=number,shape_type=typ,parts=parts,points=points,bbox=bbox);assert shape==f['binary_shape'];assert f['geometry']['rings']==[points[a:b]for a,b in zip(parts,parts[1:]+[npoints])];offsets.append((pos//2,length));pos+=8+2*length;totalpoints+=npoints
 assert pos==len(shp)and offsets==list(struct.iter_unpack('>2I',shx[100:]))and totalpoints==383061
 nrows,hsize,rsize=struct.unpack_from('<IHH',dbf,4);assert nrows==1402;fields=[];p=32
 while dbf[p]!=13:
  d=dbf[p:p+32];fields.append((d[:11].split(b'\0')[0].decode(),chr(d[11]),d[16],d[17]));p+=32
 cells=0;counts=Counter()
 for i,f in enumerate(features):
  p=hsize+i*rsize;assert dbf[p]==32;p+=1;attrs={}
  for name,typ,width,decimals in fields:
   literal=dbf[p:p+width].decode('utf8').strip();p+=width;attrs[name]=(float(literal)if decimals else int(literal))if typ=='N'and literal else literal;cells+=1
  assert attrs==f['attributes'];counts['31'+attrs['COUNTYFP20']]+=1
 for p in(M/'counties').glob('*.json.gz'):assert load(p)['features']==[f for f in features if'31'+f['attributes']['COUNTYFP20']==p.name[:5]]
 assert len(counts)==93
 out=dict(status='pass_independent_frozen_map_package_review',manifest=pin(M/'asset-manifest.json'),validation=pin(M/'validation.json'),owned_entries=len(owned),external_entries=len(refs),owned_exact_membership=True,all_stored_strictly_below40MB=True,complete_contract_fields=32,complete_recursive_nodes=101612,frozen_reference_files=425,index_primary_full_remainder=[765,1326,561],parents=93,priority_parents=58,resource_coverage=coverage,native_originals=nativeproof,independent_Census_binary=dict(features=1402,county_slices=93,all_XY_positions=383061,all_DBF_cells=cells,SHP_SHX_DBf_full_source_semantics_equal=True,source_ZIP=original['raw_sha256']),producer_readonly_validation_separate=True,current_geography_or_physical_reporting_crosswalk_approved=False,qualification='Exact source geometry/attributes and native overlap diagnostics are preserved without repair. Native count equality does not prove reporting identity. County/municipal reference resources are shared and may be partial;162 priorities have only Census2020 fallback. No same-vintage legal gap certification or current crosswalk approval.')
 p=D/'coordinator-finished-maps-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()

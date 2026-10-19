"""Producer-free complete map-source, hierarchy and binary-position review."""
from pathlib import Path
from collections import Counter
import ast,gzip,hashlib,io,json,struct,urllib.parse,zipfile
from shapely.geometry import Polygon,MultiPolygon,Point
from shapely.strtree import STRtree

D=Path(__file__).resolve().parent;S=D.parent;M=S/'maps'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def sem(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def pointer(x,p):
 for k in p.split('/')[1:] if p else []:
  k=k.replace('~1','/').replace('~0','~');x=x[int(k)] if isinstance(x,list) else x[k]
 return x
def body(r):
 if 'asset_path' in r:
  p=S/r['asset_path'];b=p.read_bytes();assert len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256'];parts=[b]
 else:
  parts=[]
  for q in r['stored_objects']:
   b=(S/q['path']).read_bytes();assert len(b)==q['bytes'] and sha(b)==q['sha256'];parts.append(b)
 raw=gzip.decompress(b''.join(parts));assert len(raw)==r['raw_bytes'] and sha(raw)==r['raw_sha256'];return raw
def polygon(rings):
 shells=[];holes=[]
 for r in rings:
  assert len(r)>=4 and r[0][:2]==r[-1][:2]
  signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(r,r[1:]))
  (shells if signed<0 else holes).append(r)
 assert shells
 assigned=[[] for _ in shells]
 for h in holes:
  candidates=[(Polygon(s).area,i) for i,s in enumerate(shells) if Polygon(s).covers(Point(h[0][:2]))]
  assert candidates;assigned[min(candidates)[1]].append(h)
 ps=[Polygon(s,assigned[i]) for i,s in enumerate(shells)]
 return ps[0] if len(ps)==1 else MultiPolygon(ps)
def main():
 mf=load(M/'asset-manifest.json');owned=mf['owned_assets'];refs=load(S/mf['read_only_reference_manifest'])
 assert len(owned)==591 and len(refs)==464
 for q in owned+refs:assert pin(S/q['path'])=={k:q[k] for k in ['path','bytes','sha256']} and q['bytes']<40_000_000
 actual={str(p.relative_to(S)) for p in M.rglob('*') if p.is_file()}|{'precinct-maps.md'}
 assert actual=={q['path'] for q in owned}|{'maps/asset-manifest.json'}
 for p in M.rglob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
 assert not any(p.name in ['__pycache__','.venv','node_modules'] for p in M.rglob('*'))
 c=load(D/'turnout/priority-set.json');graph=load(M/'source/full-contract-references.json')
 assert graph['contract']==pin(D/'turnout/priority-set.json')
 for q in graph['all_complete_objects']:assert sem(pointer(c,q['JSON_pointer']))==q['recursive_semantic_sha256']
 assert len(graph['all_complete_objects'])==2150
 inv=load(M/'inventory-691.json');pri=load(M/'priority-index-304.json');rem=load(M/'remainder-387.json');parents=load(M/'county-parents.json')
 assert len(inv)==691 and pri==inv[:304] and rem==inv[304:] and len(parents)==66
 for i,(v,u) in enumerate(zip(inv,c['all_units'])):
  assert v['key']==u['key'] and v['rank']==i+1
  assert v['full_frozen_native_object']['recursive_semantic_sha256']==sem(u)
  assert v['matched_physical_feature_ids'] is None and v['current_reporting_crosswalk'] is None
  assert v['fallback']['reporting_unit_crosswalk'] is None
 for i,(p,u) in enumerate(zip(parents,c['county_parents'])):
  assert p['full_parent_object']['recursive_semantic_sha256']==sem(u)
  assert p['ordered_all_native_keys']==u['ordered_all_native_keys'] and p['ordered_priority_native_keys']==u['ordered_priority_native_keys']
  assert len(p['official_authority']['cells'])==9
 assert sum(bool(v['county_map_assets']) for v in pri)==208
 assert sum(not v['county_map_assets'] for v in pri)==96
 rr=load(M/'source/reused-receipts.json')+[load(p) for p in sorted((M/'raw').glob('*.receipt.json'))];by={r['id']:r for r in rr}
 assert len(rr)==len(by)==244
 for r in rr:body(r)
 proof=load(M/'qa/native-GIS.json');native={}
 for name,count,badid,curves,overlaps in [('minnehaha',81,80,[6,9,62,77,78,79],67),('pennington',53,40,[48],41)]:
  get=lambda suffix:json.loads(body(by[name+'-'+suffix]))
  meta=get('layer-metadata');assert meta==get('metadata-post')
  ids=get('ids-pre');assert ids==get('ids-post')
  assert get('count-pre')==get('count-post')=={'count':count}
  features=[]
  for r in rr:
   if not r['id'].startswith(name+'-native-page'):continue
   q=urllib.parse.parse_qs(urllib.parse.urlsplit(r['url']).query)
   assert not set(k.lower() for k in q)&{'outsr','geometryprecision','quantizationparameters','maxallowableoffset','resultoffset'}
   assert q['returnTrueCurves']==['true'] and q['outFields']==['*']
   p=json.loads(body(r));fs=p['features'];assert not p.get('exceededTransferLimit')
   got=[f['attributes'][ids['objectIdFieldName']] for f in fs]
   assert len(got)==len(set(got))<=50 and set(got)==set(r['requested_object_ids']);features.extend(fs)
  assert len(features)==count and {f['attributes'][ids['objectIdFieldName']] for f in features}==set(ids['objectIds'])
  assert proof[name]['metadata']==meta
  geoms=[];gids=[];bad=[];actualcurves=[];positions=0
  for f,saved in zip(features,proof[name]['records']):
   ident=f['attributes'][ids['objectIdFieldName']];assert saved['id']==ident and saved['attributes']==f['attributes'] and saved['complete_native_feature_semantic_sha256']==sem(f)
   g=f['geometry']
   if 'curveRings' in g:actualcurves.append(ident);continue
   positions+=sum(len(r) for r in g['rings']);v=polygon(g['rings'])
   if not v.is_valid:bad.append(ident);continue
   geoms.append(v);gids.append(ident)
  assert actualcurves==curves and bad==[badid]
  tree=STRtree(geoms);pairs=[]
  for i,g in enumerate(geoms):
   for j in tree.query(g):
    j=int(j)
    if j>i:
     area=g.intersection(geoms[j]).area
     if area>0:pairs.append((gids[i],gids[j],area))
  assert len(pairs)==overlaps
  saved=proof[name]['diagnostics']['positive_area_overlaps']
  assert [(x['a'],x['b'],x['intersection_area']) for x in saved]==pairs
  native[name]=dict(features=count,complete_source_attributes_and_geometry_equal=True,linear_XY_positions=positions,curves_retained=curves,invalid_linear_IDs=bad,positive_area_pairs=len(pairs),source_CRS=meta['extent']['spatialReference'],square_area_units='US survey feet',geometry_repaired=False)
 # Full raw binary source replay; no PyShp/producer geometry adapter is imported.
 raw=body(by['census-SD-vtd20-original']);z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
 files={Path(n).suffix:z.read(n) for n in z.namelist()};shp,shx,dbf=(files[k] for k in ['.shp','.shx','.dbf'])
 cg=load(M/'qa/Census-binary-geometry.json.gz');records=cg['records'];assert len(records)==785
 pos=100;offsets=[];points=0
 for i,r in enumerate(records):
  num,words=struct.unpack_from('>II',shp,pos);b=shp[pos+8:pos+8+2*words]
  typ=struct.unpack_from('<I',b,0)[0];nparts,npoints=struct.unpack_from('<II',b,36)
  parts=list(struct.unpack_from('<'+str(nparts)+'I',b,44));xyoff=44+4*nparts
  assert typ==5 and num==i+1 and xyoff+16*npoints==len(b)
  assert r['record']==num and r['parts']==parts and r['positions']==npoints and r['offset_bytes']==pos
  assert r['original_record_sha256']==sha(shp[pos:pos+8+2*words]) and r['XY_bytes_sha256']==sha(b[xyoff:])
  assert r['bbox']==list(struct.unpack_from('<4d',b,4))
  offsets.append((pos//2,words));points+=npoints;pos+=8+2*words
 assert pos==len(shp) and offsets==list(struct.iter_unpack('>2I',shx[100:])) and points==505985
 nrows,hlen,rlen=struct.unpack_from('<IHH',dbf,4);assert nrows==785
 fields=[];at=32
 while dbf[at]!=13:
  f=dbf[at:at+32];fields.append((f[:11].split(b'\0')[0].decode(),chr(f[11]),f[16],f[17]));at+=32
 county=Counter();cells=0
 for i,r in enumerate(records):
  b=dbf[hlen+i*rlen:hlen+(i+1)*rlen];assert b[0]==32 and sha(b)==r['DBF_record_sha256'];at=1;attrs={}
  for name,typ,width,decimals in fields:
   v=b[at:at+width].decode('utf8').strip().strip('\0');at+=width
   attrs[name]=(float(v) if decimals else int(v)) if typ in ['N','F'] and v else v;cells+=1
  assert attrs==r['attributes'];county[attrs['STATEFP20']+attrs['COUNTYFP20']]+=1
 assert dict(sorted(county.items()))==cg['county_counts'] and len(county)==66
 out=dict(status='pass_independent_complete_frozen_map_source_review',manifest=pin(M/'asset-manifest.json'),validation=pin(M/'qa/validation.json'),owned_exact_membership=591,read_only_reference_pins=464,recursive_complete_contract_objects=2150,full_native=691,priority=304,remainder=387,all_parents=66,qualified_county_map_priorities=208,Census_only_priorities=96,complete_receipts=244,native_source_audit=native,Census_binary=dict(features=785,county_slices=66,all_XY_positions=505985,all_DBF_cells=cells,SHP_record_and_XY_bit_patterns_SHA_equal=True,SHX_offsets_and_lengths_equal=True,source_ZIP_CRCs_pass=True),all_assets_strictly_below40MB=True,source_geometry_repaired=False,current_geography_or_reporting_crosswalk_approved=False,qualification='Full original/membership/hierarchy/attribute/native-position replay. Two invalid linear geometries and seven curves remain source-preserved and excluded from valid-linear overlap diagnostics.108 positive-area pairs are source diagnostics, not legal overlap/gap certification.96 priority entries have only Census2020 fallback; paper/native/current vintages are not joined.')
 p=D/'coordinator-finished-maps-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()

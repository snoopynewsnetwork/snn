"""Independent final full-body, source, hierarchy and geometry audit.
No producer import, writer, network or geographic/result crosswalk.
"""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json,math,struct,zipfile
import shapefile
from shapely.geometry import Polygon,MultiPolygon
from shapely.validation import explain_validity
S=Path(__file__).resolve().parents[1]
CHECKS=0
CACHE={}
def check(v,message=''):
 global CHECKS
 assert v,message;CHECKS+=1
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def read(p):
 p=Path(p);p=p if p.is_absolute()else S/p
 if p not in CACHE:
  b=p.read_bytes();b=gzip.decompress(b)if p.suffix=='.gz'else b
  CACHE[p]=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))if '.csv' in p.name else [json.loads(x)for x in b.splitlines()if x.strip()]if '.jsonl' in p.name else json.loads(b)
 return CACHE[p]
def raw(p):return (S/p).read_bytes()
def pin(p):
 b=raw(p);return dict(path=p,bytes=len(b),sha256=sha(b))
def verify(r):
 b=raw(r['path']);check(len(b)==r['bytes']<40000000,r['path']);check(sha(b)==r['sha256'],r['path']);return b
def pointer(v,p):
 for k in p.split('/')[1:]:
  k=k.replace('~1','/').replace('~0','~');v=v[int(k)]if isinstance(v,list)else v[k]
 return v
def entity(r,official=False):
 if 'asset'in r:
  b=raw('data/results-sources/'+r['asset'])
 elif 'asset_path'in r:b=raw(r['asset_path'])
 else:
  check(bool(r.get('error')));return None
 check(len(b)==r['stored_bytes']<40000000);check(sha(b)==r['stored_sha256'])
 b=gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b
 check(len(b)==r['raw_bytes']);check(sha(b)==r['raw_sha256']);return b

def seal(path,actual_paths):
 d=read(path);rows=d['owned'];check({r['path']for r in rows}==set(actual_paths),'exact owned membership')
 for r in rows:verify(r)
 for r in d.get('external_complete_references',[]):verify(r)
 return dict(manifest=pin(path),owned=len(rows),external=len(d.get('external_complete_references',[])),bytes=sum(r['bytes']for r in rows),maximum=max(r['bytes']for r in rows))

def full_refs(path):
 d=read(path);contract=read(d['contract']['path']);verify(d['contract'])
 check(len(contract)==len(d['root_fields'])==42)
 for r in d['root_fields']:check(sha(canonical(pointer(contract,r['pointer'])))==r['full_recursive_semantic_sha256'])
 companions=d.get('companions',d.get('complete_companions'));objects=d.get('objects',d.get('complete_objects'))
 check(len(companions)==42);check(len(objects)==16388)
 for r in companions:
  b=verify(r);b=gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b
  if 'complete_reconstructed_bytes'in r:
   check(len(b)==r['complete_reconstructed_bytes']);check(sha(b)==r['complete_reconstructed_sha256'])
  check(sha(canonical(read(r['path'])))==r['full_semantic_sha256'])
 for r in objects:
  value=read(r['file'])[r['JSONL_record']-1]if 'JSONL_record'in r else pointer(read(r['file']),r['pointer'])
  check(sha(canonical(value))==r['full_recursive_semantic_sha256'])
 return dict(root_fields=42,complete_companions=42,complete_objects=16388,reference_pin=pin(path))

def census(receipt):
 b=entity(receipt);z=zipfile.ZipFile(io.BytesIO(b));check(z.testzip()is None)
 n=z.namelist();members={name:z.read(name)for name in n}
 for info in z.infolist():check((__import__('zlib').crc32(members[info.filename])&0xffffffff)==info.CRC)
 ext={Path(k).suffix:members[k]for k in n};shp=ext['.shp'];shx=ext['.shx'];dbf=ext['.dbf'];check(shp[:4]==struct.pack('>i',9994));check(struct.unpack('<i',shp[32:36])[0]==5)
 nr=struct.unpack_from('<I',dbf,4)[0];hlen,rlen=struct.unpack_from('<HH',dbf,8);fields=[];offset=1
 for pos in range(32,hlen-1,32):
  v=dbf[pos:pos+32];name=v[:11].split(b'\0')[0].decode();fields.append((name,chr(v[11]),v[16],v[17],offset));offset+=v[16]
 check(offset==rlen);reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf));check(len(reader)==nr)
 audit=read('maps/qa/'+receipt['id']+'-audit.json.gz');check(audit['native_records']==nr);pcount=0;parts_total=0;pos=100
 for i,(shape,record)in enumerate(zip(reader.shapes(),reader.records())):
  number,words=struct.unpack_from('>2i',shp,pos);content=shp[pos+8:pos+8+words*2];a=audit['records'][i]
  check(number==i+1);check(sha(content)==a['content_sha256']);check(struct.unpack_from('>2i',shx,100+i*8)==(pos//2,words))
  typ=struct.unpack_from('<i',content)[0];check(typ==5);box=list(struct.unpack_from('<4d',content,4));np,nxy=struct.unpack_from('<2i',content,36);parts=list(struct.unpack_from('<'+'i'*np,content,44));xy=content[44+np*4:44+np*4+16*nxy]
  check(parts==list(shape.parts)==a['parts']);check(box==list(shape.bbox)==a['bbox']);check(sha(xy)==a['all_xy_raw_sha256'])
  for k,point in enumerate(shape.points):check(struct.pack('<2d',*point)==xy[k*16:k*16+16])
  rawrow=dbf[hlen+i*rlen:hlen+(i+1)*rlen];check(sha(rawrow)==a['dbf_raw_sha256'])
  for (name,kind,length,dec,start),sv,av in zip(fields,record,a['fields']):
   cell=rawrow[start:start+length];check(cell.hex()==av['raw_hex']);check(cell.decode().strip()==av['value'])
   expected=(float(cell.strip())if dec else int(cell.strip()))if kind in 'NF'and cell.strip()else cell.decode().strip()
   check(sv==expected)
  pcount+=nxy;parts_total+=np;pos+=8+len(content)
 check(pos==len(shp));check(pcount==audit['total_positions']);check(parts_total==audit['total_parts'])
 return dict(county=receipt['id'],features=nr,parts=parts_total,exact_XY_positions=pcount,whole_zip_sha256=sha(b))

def main():
 official_manifest='data/results-sources/manifest.json';maps_manifest='maps/asset-manifest.json'
 official_paths=['official-results.md','data/official-results-sources.csv']+[str(p.relative_to(S))for p in (S/'data/results-sources').rglob('*')if p.is_file()and p!=S/official_manifest]
 maps_paths=['precinct-maps.md']+[str(p.relative_to(S))for p in (S/'maps').rglob('*')if p.is_file()and p!=S/maps_manifest]
 seals=[seal(official_manifest,official_paths),seal(maps_manifest,maps_paths)]
 refs=[full_refs('data/results-sources/frozen-references.json.gz'),full_refs('maps/source/frozen-references.json.gz')]
 index=read('data/results-sources/source-index.json');off={}
 for r in index:
  verify(r['receipt']);receipt=read(r['receipt']['path']);off[r['source_id']]=entity(receipt,True)
  check(receipt.get('November_counts_admitted',False)is False)
 csvrows=list(csv.DictReader(io.StringIO(off['primary-csv'].decode('utf-8-sig'))));check(len(csvrows)==829);check(len(csvrows[0])==11)
 dates=collections.Counter(r['electiondate']for r in csvrows);check(len(dates)==12)
 senate=[r for r in csvrows if r['office']=='U.S. Senator'];current=[r for r in senate if r['electiondate'].startswith('2026-09-15')];nov=[r for r in csvrows if r['electiondate'].startswith('2026-11')]
 check(len(senate)==17);check(len(current)==6);check(not nov)
 c=read('data/turnout/priority-set.json');ordered=c['ordered_priority_keys'];full=[r['native_key']for r in c['full_order']]
 for p,n in [('data/results-sources/priority-entry-investigations.json.gz',311),('data/results-sources/remainder-entry-investigations.json.gz',219)]:
  rows=read(p);check(len(rows)==n);check([r['native_key']for r in rows]==(ordered if n==311 else c['ordered_remainder_keys']))
  for r in rows:
   obj=pointer(c,r['frozen_full_observation']['pointer']);check(r['native_key']==obj['native_key']);check(r['native_key']in c['county_native_hierarchy'][r['historical_parent']]['ordered_senate_native_keys'])
   for k,v in r.items():
    if k.startswith('current_'):check(v is None or v is False)
 idx=read('maps/index.json');check([r['native_key']for r in idx['all_senate']]==full);check(idx['full_parent_hierarchies']==c['county_native_hierarchy'])
 for r,old in zip(idx['all_senate'],c['full_order']):
  for k,v in old.items():check(r[k]==v)
  check(r['leaf_feature_ids']is None);check(r['current_geography_approved']is False)
  for p in r['available_geographic_references']:check((S/'maps'/p).is_file())
 receipts=[read(str(p.relative_to(S)))for p in sorted((S/'maps/source').glob('*.receipt.json'))];by={r['id']:r for r in receipts};bodies={r['id']:entity(r)for r in receipts}
 for kind in ['metadata','count','ids']:check(bodies['native-pre-'+kind]==bodies['native-post-'+kind])
 meta=json.loads(bodies['native-pre-metadata']);ids=json.loads(bodies['native-pre-ids'])['objectIds'];fields=[f['name']for f in meta['fields']];features=[]
 for rid in sorted(k for k in by if k.startswith('native-batch-')):
  r=by[rid];req=r['requested_object_ids'];query=r['query_parameters'];check(0<len(req)<=50)
  check(query==dict(f='json',objectIds=','.join(map(str,req)),outFields='*',returnGeometry='true',returnTrueCurves='true',returnZ='true',returnM='true'))
  value=json.loads(bodies[rid]);fs=value['features'];check([f['attributes']['OBJECTID']for f in fs]==req);check(not value.get('exceededTransferLimit',False))
  for f in fs:check(list(f['attributes'])==fields)
  features.extend(fs)
 check([f['attributes']['OBJECTID']for f in features]==ids);check(len(features)==531);check(features==read('maps/native-features.json.gz')['features'])
 topo=read('maps/qa/native-topology.json');geoms=[];ringcount=0;xycount=0
 for f,review in zip(features,topo['features']):
  rings=f['geometry']['rings'];shells=[];holes=[]
  for ring in rings:
   ringcount+=1;xycount+=len(ring);check(ring[0]==ring[-1]);check(all(len(p)==2 and all(math.isfinite(x)for x in p)for p in ring))
   area=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(ring,ring[1:]))/2
   (shells if area<0 else holes).append(ring)
  polys=[]
  for shell in shells:
   base=Polygon(shell);inside=[h for h in holes if base.contains(Polygon(h))];polys.append(Polygon(shell,inside))
  check(all(any(Polygon(s).contains(Polygon(h))for s in shells)for h in holes),'orphan hole')
  g=polys[0]if len(polys)==1 else MultiPolygon(polys);geoms.append(g);check(g.is_valid==review['valid']);check(explain_validity(g)==review['reason']);check(math.isclose(g.area,review['area_native_square_units'],rel_tol=1e-12))
 positive=[];touching=0
 for i,g in enumerate(geoms):
  for j in range(i+1,len(geoms)):
   h=geoms[j]
   if not g.intersects(h):continue
   v=g.intersection(h).area
   if v>0:positive.append((i+1,j+1,v))
   else:touching+=1
 check(not positive);check(touching==topo['touching_pairs']);check(ringcount==533 and xycount==169245)
 census_results=[census(by['census-vtd-'+fips])for fips in ['10001','10003','10005']];check([r['features']for r in census_results]==[67,272,73])
 out=dict(status='pass_independent_full_final_source_and_geometry_review',checks=CHECKS,producer_seals=seals,full_frozen_reference_replays=refs,official_full_request_receipts=len(index),maps_full_request_receipts=len(receipts),current_CSV_rows=len(csvrows),current_CSV_electiondates=dict(dates),current_CSV_Senate_rows=len(senate),actual_current_primary_Senate_rows=len(current),November_rows=0,priority=311,all_native=530,remainder=219,parents=3,map_features=531,native_rings=ringcount,native_XY_positions=xycount,native_individually_invalid=sum(not g.is_valid for g in geoms),positive_area_native_pairs=positive,touching_pairs=touching,census=census_results,source_preservation='Complete raw entities, every referenced full object and all exact source candidate/control fields remain; no producer imports or source allocation.',scope_limit='Historical research only. Native projected topology diagnostics do not certify legal boundaries. No current leaf/geometry/feed/choice/cadence/outstanding pool/collector/probability approval.')
 p=S/'data/coordinator-second-wave-review.json';p.write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+'\n');print(json.dumps({k:out[k]for k in ['status','checks','map_features','native_individually_invalid','touching_pairs']}));print(pin(str(p.relative_to(S))))
if __name__=='__main__':main()

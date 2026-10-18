#!/usr/bin/env python3
"""Independent source/binary/full-coordinate map review; imports no worker code."""
from pathlib import Path
import collections,datetime,gzip,hashlib,io,json,math,struct,subprocess,zipfile
import pyproj
ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/'maps'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def binary_shape(z,stem):
 names={n.lower():n for n in z.namelist()}
 b={e:z.read(names[(stem+e).lower()]) for e in ['.shp','.shx','.dbf','.prj']}
 assert struct.unpack('>i',b['.shp'][:4])[0]==9994
 assert struct.unpack('>i',b['.shp'][24:28])[0]*2==len(b['.shp'])
 assert struct.unpack('<i',b['.shp'][28:32])[0]==1000
 geometry=[];rows=[];pos=100;vertices=parts=zs=ms=nullm=0;types=collections.Counter();digest=hashlib.sha256()
 while pos<len(b['.shp']):
  record,words=struct.unpack_from('>ii',b['.shp'],pos);body=b['.shp'][pos+8:pos+8+words*2]
  assert len(body)==words*2 and record==len(rows)+1
  index=struct.unpack_from('>ii',b['.shx'],100+8*len(rows));assert index==(pos//2,words)
  typ=struct.unpack_from('<i',body)[0];types[typ]+=1
  if typ:
   assert typ in (3,5,13,15,23,25),typ
   np,nv=struct.unpack_from('<ii',body,36); starts=struct.unpack_from('<'+'i'*np,body,44)
   assert starts[0]==0 and list(starts)==sorted(starts) and all(0<=n<nv for n in starts)
   xy=struct.unpack_from('<'+'d'*(2*nv),body,44+4*np)
   assert all(math.isfinite(x) for x in xy)
   off=44+4*np+16*nv;parts+=np;vertices+=nv
   if typ in (13,15):
    zz=struct.unpack_from('<'+'d'*nv,body,off+16);off+=16+8*nv;zs+=len(zz)
    assert all(math.isfinite(x) for x in zz)
   if off<len(body):
    mm=struct.unpack_from('<'+'d'*nv,body,off+16);off+=16+8*nv;ms+=len(mm);nullm+=sum(x< -1e38 for x in mm)
   assert off==len(body),(stem,typ,off,len(body))
  geometry.append({'record_number':record,'shape_type':typ,'parts':list(starts),'points':[list(xy[i:i+2]) for i in range(0,len(xy),2)],'bbox':list(struct.unpack_from('<dddd',body,4))})
  rows.append((pos,words));digest.update(body);pos+=8+words*2
 assert pos==len(b['.shp']) and len(b['.shx'])==100+8*len(rows)
 count,head,width=struct.unpack_from('<IHH',b['.dbf'],4);assert count==len(rows)
 fields=[]
 for n in range(32,head-1,32):
  f=b['.dbf'][n:n+32];name=f[:11].split(b'\0')[0].decode('ascii');fields.append((name,chr(f[11]),f[16],f[17]))
 assert sum(f[2] for f in fields)+1==width
 attrs=[]
 for n in range(count):
  raw=b['.dbf'][head+n*width:head+(n+1)*width];assert raw[:1]==b' '
  p=1;a={}
  for name,typ,length,dec in fields:
   val=raw[p:p+length];p+=length;s=val.decode('utf-8').strip()
   if typ in 'NF':a[name]=None if not s or s.startswith('*') else (float(s) if dec or typ=='F' else int(s))
   else:a[name]=s.rstrip('\0')
  attrs.append(a)
 return dict(records=count,vertices=vertices,parts=parts,Z_values=zs,M_values=ms,M_no_data=nullm,shape_types=dict(types),record_body_sha256=digest.hexdigest(),prj_sha256=sha(b['.prj'])),attrs,geometry

def flat_coordinates(value):
 if isinstance(value,list) and value and isinstance(value[0],(int,float)):
  yield tuple(value)
 else:
  for child in value:
   yield from flat_coordinates(child)

def main():
 mf_bytes=(MAP/'asset-manifest.json').read_bytes();mf=json.loads(mf_bytes)
 assert len(mf['assets'])==1252
 for r in mf['assets']:
  b=(ROOT/r['path']).read_bytes();assert len(b)==r['bytes']<40000000 and sha(b)==r['sha256'],r['path']
 receipts={p.name.removesuffix('.meta.json'):load(p)for p in (MAP/'source').glob('*.meta.json')}
 entities={};objects=set()
 for id,r in receipts.items():
  assert r['requested_url'] and r['requested_utc'] and r['completed_utc']
  segments=[]
  for i,o in enumerate(r['objects']):
   assert o['order']==i
   p=MAP/o['path'];b=p.read_bytes();objects.add(str(p));assert len(b)==o['bytes']<40000000 and sha(b)==o['sha256']
   b=gzip.decompress(b)if o['encoding']=='gzip'else b
   assert len(b)==o['decoded_bytes'] and sha(b)==o['decoded_sha256'];segments.append(b)
  if r['status']is not None:
   b=b''.join(segments);assert len(b)==r['original_bytes'] and sha(b)==r['original_sha256'];entities[id]=b
 assert len(receipts)==145 and len(objects)==119
 z=zipfile.ZipFile(io.BytesIO(entities['granit-pbp']));assert z.testzip()is None
 controls=load(MAP/'derived/zip-controls.json');assert len(z.infolist())==16
 for r in controls['members']:
  b=z.read(r['member']);assert len(b)==r['bytes'] and sha(b)==r['sha256'] and f'{z.getinfo(r["member"]).CRC:08x}'==r['crc32']
 binary={};native={}
 for stem,expected in [('pbp',259),('pba',773)]:
  stats,attrs,geometry=binary_shape(z,stem);assert stats['records']==expected
  derived=json.loads(gzip.decompress((MAP/f'derived/granit-archive-{stem}-native.json.gz').read_bytes()))
  assert len(derived)==expected
  for i,r in enumerate(derived):
   assert r['record_index_zero_based']==i and r['attributes']==attrs[i]
   assert r['shp_record_number']==geometry[i]['record_number']
   assert all(r[k]==geometry[i][k]for k in ['shape_type','parts','points','bbox'])
   b=z.read(stem+'.shp');off=r['shp_byte_offset'];assert sha(b[off:off+8+r['content_bytes']])==r['raw_shp_record_sha256']
  binary[stem]=stats;native[stem]=(attrs,geometry)
 assert binary['pbp']['vertices']==91469
 services={};service_features={}
 for p in sorted((MAP/'derived').glob('*-service-audit.json')):
  a=load(p);id=a['id'];oid=a['object_id_field'];features=[]
  pre=json.loads(entities[id+'-ids-pre'])['objectIds'];post=json.loads(entities[id+'-ids-post'])['objectIds']
  assert sorted(pre)==sorted(post)==sorted(a['pre_ids'])==sorted(a['post_ids'])
  assert json.loads(entities[id+'-count-pre'])['count']==json.loads(entities[id+'-count-post'])['count']==a['count_pre']==a['count_post']==len(pre)
  for batch in a['batches']:
   obj=json.loads(entities[batch['id']]);assert not obj.get('exceededTransferLimit') and not obj.get('transform')
   assert sorted(f['attributes'][oid]for f in obj['features'])==sorted(batch['requested_ids'])
   features.extend(obj['features'])
  ids=[f['attributes'][oid]for f in features];assert len(ids)==len(set(ids))==len(pre) and sorted(ids)==sorted(pre)
  vertices=0
  for f in features:
   g=f['geometry'];assert g is not None and 'curveRings'not in g
   for ring in g.get('rings',[]):
    for pt in ring:assert all(math.isfinite(x)for x in pt);vertices+=1
  services[id]={'features':len(features),'linear_vertices':vertices,'original_attribute_sha256':sha(json.dumps([f['attributes']for f in features],sort_keys=True).encode()),'original_geometry_sha256':sha(json.dumps([f['geometry']for f in features],sort_keys=True).encode())}
  service_features[id]={f['attributes'][oid]:f for f in features}
 assert len(services)==7 and sum(x['features']for x in services.values())==277
 # Verify every output coordinate, including repeated ring endpoints, from original source doubles.
 transform=pyproj.Transformer.from_crs(3437,4326,always_xy=True)
 matches=load(MAP/'derived/municipal-reference-matches.json');derivatives=0;vertices=0
 for r in matches:
  if not r.get('archive_geojson'):continue
  assert not r['current_approval'] and len(r['archive_record_ids'])==len(r['live_object_ids'])==1
  idx=r['archive_record_ids'][0];attrs,geoms=native['pbp'];original=geoms[idx];assert attrs[idx]['NAME']==r['source_parent_label'] and attrs[idx]['COUNTY']==int(r['county_fips'][-3:])
  live=service_features['granit-live'][r['live_object_ids'][0]]
  assert live['attributes']['name']==r['source_parent_label'] and live['attributes']['county']==int(r['county_fips'][-3:])
  for suffix,points,props in [('archive',original['points'],attrs[idx]),('live',[p for ring in live['geometry']['rings']for p in ring],live['attributes'])]:
   fc=load(MAP/r[suffix+'_geojson']);assert len(fc['features'])==1 and fc['features'][0]['properties']==props
   got=list(flat_coordinates(fc['features'][0]['geometry']['coordinates']))
   wanted=[transform.transform(p[0],p[1])for p in points]
   assert collections.Counter(got)==collections.Counter(wanted),(r['source_parent_label'],suffix)
   vertices+=len(got);derivatives+=1
 assert derivatives==468
 contract=load(ROOT/'data/turnout/priority-set.json');inventory=load(MAP/'inventory.json');priority=load(MAP/'priority.json')
 assert [r['geography_key']for r in inventory['units']]==contract['full_ordered_keys']
 assert priority['ordered_priority_keys']==contract['ordered_priority_keys'] and len(priority['units'])==143
 for a,b in zip(inventory['units'],contract['all_units']):
  assert a['source_unit']==b and not a['current_november_2026_approved'] and a['source_to_geometry_crosswalk']=='unverified; no allocation'
 roster_count=0
 for family in contract['source_native_coverage']:
  p=MAP/'compatibility/native'/Path(family['path']).name
  original=ROOT/'data/turnout'/family['path'];assert p.read_bytes()==original.read_bytes()
  roster_count+=len(gzip.decompress(p.read_bytes()).decode().splitlines())
 assert roster_count==7360
 page_count=0
 for r in load(MAP/'derived/pdf-pages.json'):
  b=entities[r['id']];assert b.startswith(b'%PDF-')
  info=subprocess.run(['pdfinfo','-'],input=b,capture_output=True,check=True).stdout.decode()
  import re
  count=int(re.search(r'Pages:\s+(\d+)',info)[1]);assert count==r['page_count']==len(r['pages'])
  assert all((MAP/p['preview']).read_bytes().startswith(b'\x89PNG')for p in r['pages']);page_count+=count
 assert page_count==124
 assert sha(entities['portsmouth-map'])=='789033b8d6eedbc9beb441ac79c516ffcb85638f65dcb69fa0c582478cb8e38e' and len(entities['portsmouth-map'])==55167846
 assert (MAP/'asset-manifest.json').read_bytes()==mf_bytes
 out={'status':'pass_with_unapproved_crosswalks_and_documented_finer_gaps','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independence':'Standalone original ZIP/SHP/SHX/DBF parser, full raw service ID/count checks and every municipal derivative coordinate transformed independently; imports no worker code.','owned_asset_hashes':1252,'http_captures':145,'unique_body_objects':119,'native_archive':binary,'services':services,'municipal_full_coordinate_derivatives':derivatives,'verified_output_vertices':vertices,'source_native_records':7360,'historical_leaves':320,'priority':143,'original_pdf_capture_records':44,'actual_pdf_pages':124,'portsmouth_exact_reconstruction_bytes':55167846,'maps_manifest_sha256':sha(mf_bytes),'scope':'Downloaded map/reference integrity and original conservation; no current legal geometry or result/method crosswalk approval, topology repair or vote allocation.'}
 out=json.loads(json.dumps(out))
 p=ROOT/'data/coordinator-map-review.json'
 if p.exists():
  prev=load(p)
  if {k:v for k,v in prev.items()if k!='reviewed_utc'}=={k:v for k,v in out.items()if k!='reviewed_utc'}:out['reviewed_utc']=prev['reviewed_utc']
 p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['services']},indent=2))

if __name__=='__main__':main()

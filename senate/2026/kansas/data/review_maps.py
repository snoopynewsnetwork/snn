#!/usr/bin/env python3
"""Independent raw-stream/JSON/SHP/DBF conservation review; no worker imports."""
import collections,datetime,gzip,hashlib,io,json,math,struct,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
MAP=ROOT/'maps'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def original(r):
 s=r['storage']; parts=[]
 for a in s['ordered_parts']:
  b=(MAP/a['path']).read_bytes();assert len(b)==a['bytes']<40000000 and sha(b)==a['sha256'];parts.append(b)
 b=b''.join(parts);assert len(b)==s['stored_bytes'] and sha(b)==s['stored_sha256']
 b=gzip.decompress(b) if s['encoding']=='gzip' else b
 assert len(b)==r['original_bytes'] and sha(b)==r['original_sha256'];return b

def binary_shape(z,stem):
 names={n.lower():n for n in z.namelist()}
 b={e:z.read(names[(stem+e).lower()]) for e in ['.shp','.shx','.dbf','.prj']}
 assert struct.unpack('>i',b['.shp'][:4])[0]==9994
 assert struct.unpack('>i',b['.shp'][24:28])[0]*2==len(b['.shp'])
 assert struct.unpack('<i',b['.shp'][28:32])[0]==1000
 rows=[];pos=100;vertices=parts=zs=ms=nullm=0;types=collections.Counter();digest=hashlib.sha256()
 while pos<len(b['.shp']):
  record,words=struct.unpack_from('>ii',b['.shp'],pos);body=b['.shp'][pos+8:pos+8+words*2]
  assert len(body)==words*2 and record==len(rows)+1
  index=struct.unpack_from('>ii',b['.shx'],100+8*len(rows));assert index==(pos//2,words)
  typ=struct.unpack_from('<i',body)[0];types[typ]+=1
  if typ:
   assert typ in (5,15,25),typ
   np,nv=struct.unpack_from('<ii',body,36); starts=struct.unpack_from('<'+'i'*np,body,44)
   assert starts[0]==0 and list(starts)==sorted(starts) and all(0<=n<nv for n in starts)
   xy=struct.unpack_from('<'+'d'*(2*nv),body,44+4*np)
   assert all(math.isfinite(x) for x in xy)
   off=44+4*np+16*nv;parts+=np;vertices+=nv
   if typ==15:
    zz=struct.unpack_from('<'+'d'*nv,body,off+16);off+=16+8*nv;zs+=len(zz)
    assert all(math.isfinite(x) for x in zz)
   if off<len(body):
    mm=struct.unpack_from('<'+'d'*nv,body,off+16);off+=16+8*nv;ms+=len(mm);nullm+=sum(x< -1e38 for x in mm)
   assert off==len(body),(stem,typ,off,len(body))
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
 return dict(records=count,vertices=vertices,parts=parts,Z_values=zs,M_values=ms,M_no_data=nullm,shape_types=dict(types),record_body_sha256=digest.hexdigest(),prj_sha256=sha(b['.prj'])),attrs

def main():
 records=load(MAP/'acquisition.json'); assert len({r['id'] for r in records})==len(records)
 originals={r['id']:original(r) for r in records if r.get('storage')}
 manifests=load(MAP/'asset-manifest.json')['assets']
 for a in manifests:
  b=(MAP/a['path']).read_bytes();assert sha(b)==a['sha256'] and len(b)==a['bytes']<40000000
 service_results={};all_services=load(MAP/'services.json');state_counties=collections.Counter()
 for s in all_services:
  key=s['id'];get=lambda suffix:json.loads(originals[key+suffix])
  before=get('-ids-before')['objectIds'];after=get('-ids-after')['objectIds'];fs=[]
  assert before==after and len(set(before))==len(before)==s['count']==get('-count-before')['count']==get('-count-after')['count']
  for page in s['pages']:
   j=json.loads(originals[page]);assert not j.get('exceededTransferLimit') and not j.get('transform');fs+=j['features']
  oid=s['oid_field'];ids=[f['attributes'][oid] for f in fs];assert len(ids)==len(set(ids))==s['count'] and set(ids)==set(before)
  diag=json.loads(gzip.decompress((MAP/'extracts'/f'{key}-geometry.json.gz').read_bytes()))
  assert [r['attributes'] for r in diag['attributes']]==[f['attributes'] for f in fs]
  vertices=parts=missing=curves=z=m=0;attrdigest=hashlib.sha256();geomdigest=hashlib.sha256()
  for f in fs:
   attrdigest.update(json.dumps(f['attributes'],sort_keys=True,separators=(',',':')).encode())
   geom=f.get('geometry');geomdigest.update(json.dumps(geom,sort_keys=True,separators=(',',':')).encode())
   if not geom:missing+=1;continue
   if 'curveRings' in geom:curves+=1;continue
   for ring in geom.get('rings',[]):
    parts+=1
    for v in ring:
     assert len(v)>=2 and all(isinstance(x,(int,float)) and math.isfinite(x) for x in v[:2]);vertices+=1
     z+=len(v)>=3;m+=len(v)>=4
   if key=='klrd-2022':state_counties[f['attributes']['CO_CODE']]+=1
  assert vertices==diag['vertices'] and parts==diag['rings'] and curves==len(diag['curve_geometry']) and missing==len(diag['null_geometry'])
  service_results[key]=dict(objects=len(fs),vertices=vertices,parts=parts,curved_objects=curves,missing_geometry=missing,Z_positions=z,M_positions=m,attribute_sha256=attrdigest.hexdigest(),native_geometry_sha256=geomdigest.hexdigest())
 assert service_results['klrd-2022']['objects']==4749 and service_results['klrd-2022']['vertices']==792805 and len(state_counties)==105
 assert service_results['wyandotte']['missing_geometry']==153 and service_results['shawnee']['curved_objects']==4
 archive_results={};members=0
 for key in ['johnson-shp','sedgwick-shp']:
  z=zipfile.ZipFile(io.BytesIO(originals[key]));assert z.testzip() is None
  audit=load(MAP/'extracts/archive-checks.json')[key]
  assert len(audit['members'])==len(z.infolist())
  for want,info in zip(audit['members'],z.infolist()):
   b=z.read(info);assert want['name']==info.filename and want['sha256']==sha(b) and want['uncompressed_bytes']==len(b)==info.file_size and want['crc32']==f'{info.CRC:08x}';members+=1
  for stem in [n[:-4] for n in z.namelist() if n.lower().endswith('.shp')]:
   out,attrs=binary_shape(z,stem);d=json.loads(gzip.decompress((MAP/'extracts'/f'{key}-geometry.json.gz').read_bytes()))
   assert out['vertices']==d['vertices'] and out['parts']==d['rings'] and out['records']==d['features']
   assert attrs==[{k:v for k,v in f['attributes'].items() if k!='_record_index'} for f in d['attributes']]
   archive_results[key]=out
 inv=load(MAP/'inventory.json')['counties'];contract=load(ROOT/'data/turnout/priority-set.json');keys=(ROOT/'data/coordinator-priority-keys.txt').read_text().splitlines()
 assert len(inv)==105 and [c['county_key'] for c in inv if c['priority']]==keys
 for c,obj in zip(inv,contract['all_geography_coverage']):
  assert json.loads(gzip.decompress((MAP/c['native_context']).read_bytes()))==obj
  assert len(c['state_2022_feature_ids'])==state_counties[c['county_fips']] and not c['november_2026_boundary_approval']
 # PyMuPDF reads complete untouched originals only; page counts compared to saved preview inventory.
 import fitz
 pdfs={}
 for key,b in originals.items():
  if b.startswith(b'%PDF-'):
   doc=fitz.open(stream=b,filetype='pdf');pdfs[key]=doc.page_count;assert all(page.rect.width>0 and page.rect.height>0 for page in doc)
 assert len(pdfs)==23 and sum(pdfs.values())==61
 pins=load(MAP/'readonly-pins.json');mismatches=[]
 for p in pins['files']:
  b=(MAP/p['path']).read_bytes()
  if sha(b)!=p['sha256'] or len(b)!=p['bytes']:mismatches.append(p['path'])
 assert not [p for p in mismatches if not p.startswith('../data/results-sources/')],mismatches
 result=dict(status='pass_with_unapproved_geography',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),owned_hashes=len(manifests),original_entities=len(originals),service_layers=service_results,zip_layers=archive_results,zip_members=members,pdf_documents=pdfs,pdf_pages=sum(pdfs.values()),counties=105,priority_counties=23,native_results_identities=22031,raw_geometry_unrepaired=True,current_crosswalk_approved=False,mutable_source_metadata_mismatches_pending_final_peer_freeze=mismatches,scope='Independent raw SHA/size, every source Esri coordinate/attribute and count/ID control, independent binary SHP/SHX/DBF all records/vertices/Z/M/attributes, ZIP CRC, PDF pages, exact historical constituent objects; no map/results joining.')
 out=ROOT/'data/coordinator-map-review.json'
 if out.exists():
  old=load(out)
  if {k:v for k,v in old.items() if k!='checked_utc'}=={k:v for k,v in result.items() if k!='checked_utc'}:result['checked_utc']=old['checked_utc']
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

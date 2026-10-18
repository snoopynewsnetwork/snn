#!/usr/bin/env python3
"""Independent binary conservation review; no worker code imported."""
import collections,datetime,gzip,hashlib,html.parser,io,json,math,struct,urllib.parse,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;MAP=ROOT/'maps'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def original(r):
 pieces=[]
 for s in sorted(r['storage'],key=lambda s:s['order']):
  z=(MAP/s['path']).read_bytes();assert len(z)==s['stored_bytes']<40000000 and sha(z)==s['stored_sha256'];b=gzip.decompress(z) if s.get('encoding','gzip')=='gzip' else z;assert len(b)==s['entity_bytes'] and sha(b)==s['entity_sha256'];pieces.append(b)
 b=b''.join(pieces);assert len(b)==r['entity_bytes'] and sha(b)==r['entity_sha256'];return b
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

def main():
 receipts={p.stem:load(p) for p in (MAP/'receipts').glob('*.json')};entities={k:original(r) for k,r in receipts.items()};assert len(entities)==241
 mf=load(MAP/'manifest.json');assert len(mf['artifacts'])==846
 for a in mf['artifacts']:
  b=(ROOT/a['path']).read_bytes();assert len(b)==a['bytes']<40000000 and sha(b)==a['sha256'],a['path']
 z=zipfile.ZipFile(io.BytesIO(entities['state-2024-precinct-zip']));assert z.testzip() is None
 archived=load(MAP/'extracts/archive-inspection.json');assert len(z.infolist())==len(archived['members'])==4
 for a in archived['members']:
  b=z.read(a['name']);assert len(b)==a['bytes'] and sha(b)==a['sha256'] and f'{z.getinfo(a["name"]).CRC:08x}'==a['crc32']
 stem=next(n[:-4] for n in z.namelist() if n.endswith('.shp'));binary,attrs,geometry=binary_shape(z,stem);assert binary['records']==2724 and binary['vertices']==1775333 and binary['parts']==3436 and binary['shape_types']=={5:2724}
 by_fips=collections.defaultdict(list)
 for i,a in enumerate(attrs):by_fips[a['FIPS']].append(i)
 assert len(by_fips)==160 and len(by_fips[''])==27
 contract=load(ROOT/'data/turnout/priority-set.json');inv=load(MAP/'inventory.json');assert len(inv)==159;priority=contract['ordered_priority_keys'];selected=0
 for county in inv:
  f=county['county_fips'];assert county['state_map2024_row_ordinals']==by_fips[f];assert county['map_crosswalk_status'].startswith('unapproved')
  if county['named_four_dispatch_rank']:
   d=json.loads(gzip.decompress((MAP/f'extracts/{f}-state2024-native-geometry.json.gz').read_bytes()));assert d['original_crs_wkt']==z.read(stem+'.prj').decode();assert [r['row_ordinal'] for r in d['features']]==by_fips[f]
   for r in d['features']:
    i=r['row_ordinal'];assert r['attributes']==attrs[i];assert all(r[k]==geometry[i][k] for k in ['record_number','shape_type','parts','points','bbox']);assert r['z'] is None and r['m'] is None
   selected+=len(d['features'])
 assert selected==1934
 unknown=json.loads(gzip.decompress((MAP/'extracts/state2024-unmatched-native-geometry.json.gz').read_bytes()))['features'];assert [r['row_ordinal'] for r in unknown]==by_fips['']
 for r in unknown:
  i=r['row_ordinal'];assert r['attributes']==attrs[i] and all(r[k]==geometry[i][k] for k in ['record_number','shape_type','parts','points','bbox'])
 complete=0;features=0;services={}
 for s in load(MAP/'service-inspection.json'):
  if not s.get('advertised_count'):services[s['id']]={'status':s['status'],'scope':'incomplete capture retained, not accepted geometry'};continue
  sid=s['id'];before=json.loads(entities[sid+'-ids-before'])['objectIds'];after=json.loads(entities[sid+'-ids-after'])['objectIds'];oid=s['oid_field'];sets=[json.loads(entities[p]) for p in s['batches']];assert all(not x.get('exceededTransferLimit',False) and not x.get('transform') for x in sets);fs=[f for x in sets for f in x['features']];ids=[f['attributes'][oid] for f in fs];assert len(ids)==len(set(ids))==s['advertised_count'] and sorted(ids)==sorted(before)==sorted(after)
  d=json.loads(gzip.decompress((MAP/f'extracts/{sid}-service-native.json.gz').read_bytes()));assert d['feature_sets']==sets and d['metadata']==json.loads(entities[sid+'-metadata']);v=p=curves=missing=0;ad=hashlib.sha256();gd=hashlib.sha256()
  for feature in fs:
   ad.update(json.dumps(feature['attributes'],sort_keys=True,separators=(',',':')).encode());g=feature.get('geometry');gd.update(json.dumps(g,sort_keys=True,separators=(',',':')).encode())
   if g is None:missing+=1;continue
   if 'curveRings' in g:curves+=1;continue
   for ring in g.get('rings',[]):
    p+=1
    for point in ring:assert len(point)>=2 and all(isinstance(x,(int,float)) and math.isfinite(x) for x in point[:2]);v+=1
  if s['status']=='complete':
   assert missing==0 and s['metadata_editingInfo_before']==s['metadata_editingInfo_after'];complete+=1;features+=len(fs);assert v==s['geometry_diagnostics']['vertices'] and p==s['geometry_diagnostics']['parts']
  else:assert s['status']=='complete_ids_geometry_unavailable' and missing==len(fs)
  services[sid]={'status':s['status'],'objects':len(fs),'linear_vertices':v,'linear_parts':p,'curved_objects':curves,'missing_geometry':missing,'all_original_attribute_sha256':ad.hexdigest(),'all_original_geometry_sha256':gd.hexdigest()}
 assert complete==12 and features==1044
 # Compare complete historical contract constituents without assigning votes to maps.
 with gzip.open(MAP/'extracts/native-contexts.jsonl.gz','rt') as f:contexts=[json.loads(x) for x in f]
 wanted={u['key']:u for c in contract['coverage'] for u in c['constituents']};assert len(contexts)==len(wanted)==2701
 assert {c['contract_constituent']['key'] for c in contexts}==set(wanted)
 for c in contexts:assert c['contract_constituent']==wanted[c['contract_constituent']['key']] and c['geographic_join_status'].startswith('no approved')
 for p,pin in load(MAP/'input-pins.json').items():
  b=(ROOT/p).read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256'],p
 import fitz
 unique_pdfs={sha(b):b for b in entities.values() if b.startswith(b'%PDF-')};pdf_pages={}
 for h,b in unique_pdfs.items():
  doc=fitz.open(stream=b,filetype='pdf');assert all(p.rect.width>0 and p.rect.height>0 for p in doc);pdf_pages[h]=doc.page_count
 assert len(pdf_pages)==30 and sum(pdf_pages.values())==152
 result={'status':'pass_unapproved_current_crosswalks_explicit','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owned_artifact_hashes':846,'original_entities':len(entities),'binary_archive':binary,'county_fips_groups':159,'unassigned_original_shapes':27,'priority_selected_shapes':1934,'complete_local_services':complete,'complete_local_features':features,'service_details':services,'historical_native_identities':2701,'priority_native_identities':1938,'remainder_native_identities':763,'original_pdf_documents':len(pdf_pages),'original_pdf_pages':sum(pdf_pages.values()),'scope':'Independent raw hashes; ZIP CRC/member hashes; binary SHP/SHX offsets, DBF records/attributes, every selected/unassigned coordinate and part; full original service feature sets, IDs/counts/transfer flags; exact native constituent and frozen-input conservation; PDF pages. No geometry repair or result/map join.'}
 out=ROOT/'data/coordinator-map-review.json'
 if out.exists():
  previous=load(out)
  if {k:v for k,v in previous.items() if k!='checked_utc'}=={k:v for k,v in result.items() if k!='checked_utc'}:result['checked_utc']=previous['checked_utc']
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='service_details'},indent=2))
if __name__=='__main__':main()

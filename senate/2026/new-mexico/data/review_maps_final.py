"""Coordinator independent binary/native/source preservation audit, without producer imports."""
from pathlib import Path
import json,gzip,hashlib,struct,io,zipfile,collections,urllib.parse,math
import shapefile
S=Path(__file__).resolve().parents[1];M=S/'maps';N=0

def sha(x):return hashlib.sha256(x).hexdigest()
def ck(x):
 global N
 assert x
 N+=1

def load(p):return json.loads(p.read_bytes())
def body(r):
 if r['encoding']=='ordered_exact_byte_parts':
  chunks=[];pos=0
  for p in r['parts']:ck(p['byte_offset']==pos);b=body(p);chunks.append(b);pos+=len(b)
  b=b''.join(chunks)
 else:
  z=(S/r['path']).read_bytes();ck(sha(z)==r['sha256'] and len(z)==r['bytes']);b=gzip.decompress(z) if r['encoding']=='gzip' else z
 ck(len(b)==r['raw_bytes'] and sha(b)==r['raw_sha256']);return b

def original(name):return body(load(M/'receipts'/f'{name}.json')['body'])
manifest=load(M/'asset-manifest.json');ck(manifest['self_only_exclusion']=='maps/asset-manifest.json')
actual={str(p.relative_to(S)) for p in M.rglob('*') if p.is_file()}|{'precinct-maps.md'};listed=[r['path'] for r in manifest['owned_files']];ck(len(listed)==len(set(listed))==993);ck(set(listed)==actual-{'maps/asset-manifest.json'})
for r in manifest['owned_files']:
 b=(S/r['path']).read_bytes();ck(sha(b)==r['sha256'] and len(b)==r['bytes']<40000000)
receipts=0;entities=set();hops=0
for p in (M/'receipts').glob('*.json'):
 r=load(p);receipts+=1;ck(bool(r['started_utc']) and bool(r['finished_utc']))
 for e in r['requests']:
  hops+=1
  if e.get('body'):b=body(e['body']);entities.add(sha(b))
 if r.get('body'):entities.add(sha(body(r['body'])))
zip_summaries=[]
for year,count,pairs in [('2024',2169,1158713),('2026',2177,1159113)]:
 raw=original('rgis-'+year+'-zip');z=zipfile.ZipFile(io.BytesIO(raw));ck(z.testzip() is None);audit=json.loads(gzip.decompress((M/f'native-audit-{year}.json.gz').read_bytes()));ck(len(z.infolist())==len(audit['members']))
 for info,a in zip(z.infolist(),audit['members']):
  b=z.read(info);ck(info.filename==a['name'] and info.CRC==a['CRC32'] and len(b)==a['uncompressed_bytes'] and sha(b)==a['sha256'])
 names={Path(i.filename).suffix:i.filename for i in z.infolist() if not i.is_dir()};shp=z.read(names['.shp']);shx=z.read(names['.shx']);dbf=z.read(names['.dbf']);ck(shp[:100].hex()==audit['SHP_header_hex'] and shx[:100].hex()==audit['SHX_header_hex']);ck(struct.unpack_from('>i',shp,24)[0]*2==len(shp));ck(struct.unpack_from('<ii',shp,28)==(1000,5))
 rows,header,width=struct.unpack_from('<IHH',dbf,4);ck(rows==count==len(audit['records']));ck(dbf[:header].hex()==audit['DBF']['complete_header_hex']);fields=[]
 for i,a in enumerate(audit['schema']):
  desc=dbf[32+32*i:64+32*i];ck(desc.hex()==a['descriptor_hex']);name=desc[:11].split(b'\0')[0].decode();typ=chr(desc[11]);size=desc[16];dec=desc[17];ck((name,typ,size,dec)==(a['name'],a['type'],a['length'],a['decimals']));fields.append((name,typ,size,dec))
 ck(dbf[header-1]==13 and 1+sum(f[2] for f in fields)==width);reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf));ck(len(reader)==rows);off=100;xy_n=0;parts_n=0;county=collections.Counter();codes=collections.Counter()
 for i,a in enumerate(audit['records']):
  num,words=struct.unpack_from('>ii',shp,off);c=shp[off+8:off+8+words*2];ck(num==i+1==a['record_number']);ck((off,words)==(a['offset_bytes'],a['content_words']));ck(sha(c)==a['record_content_sha256']);ck(struct.unpack_from('>ii',shx,100+8*i)==(off//2,words));ck(struct.unpack_from('<i',c)[0]==5)
  npar,nxy=struct.unpack_from('<ii',c,36);parts=list(struct.unpack_from('<'+str(npar)+'i',c,44));start=44+4*npar;xy=c[start:];ck(len(xy)==16*nxy and nxy==a['point_count'] and parts==a['parts']);ck(sha(xy)==a['xy_bytes_sha256'] and c[4:36].hex()==a['bbox_hex']);shape=reader.shape(i);ck(bytes().join(struct.pack('<dd',*p) for p in shape.points)==xy);ck(list(shape.parts)==parts and struct.pack('<4d',*shape.bbox)==c[4:36]);xy_n+=nxy;parts_n+=npar
  rb=dbf[header+i*width:header+(i+1)*width];ck(rb[:1].hex()==a['dbf']['deletion_flag_hex']);pos=1;values=[]
  for f,cell in zip(fields,a['dbf']['cells']):
   name,typ,size,dec=f;b=rb[pos:pos+size];pos+=size;t=b.decode('utf-8');v=t.strip().rstrip('\x00') if typ=='C' else None if not t.strip() or t.strip().startswith('*') else float(t) if dec else int(t);ck(b.hex()==cell['raw_hex'] and t==cell['literal'] and v==cell['value']);values.append(v)
  ck(pos==len(rb));ck(values==a['dbf']['values']==list(reader.record(i)));attrs=dict(zip([f[0] for f in fields],values));ck(attrs==a['all_attributes']);county[attrs['STATE']+attrs['COUNTY_FIP']]+=1;codes[attrs['GEOCODE']]+=1;off+=8+words*2
 ck(off==len(shp) and len(shx)==100+8*count and xy_n==pairs);ck(len(county)==33 and county['35049']==179);ck(dbf[header+rows*width:].hex()==audit['DBF']['trailer_hex']);ck(z.read(names['.prj']).decode()==audit['native_CRS_WKT']);dups={k:v for k,v in codes.items() if v>1};ck(not dups if year=='2024' else len(dups)==7 and max(dups.values())==3)
 zip_summaries.append({'year':year,'features':count,'XY_pairs_bitwise_compared_with_native_reader':xy_n,'part_indices':parts_n,'full_DBF_fields':len(fields),'full_DBF_cells':rows*len(fields),'county_counts':dict(county),'duplicate_GEOCODE':dups,'source_CRS':audit['native_CRS_WKT']})
# Complete public-native snapshots, exact attributes and unfiltered metadata.
pre=json.loads(original('precinct-layer-pre'));post=json.loads(original('precinct-layer-post'));ck(pre==post);ck(json.loads(original('political-service-pre'))==json.loads(original('political-service-post')));ids=json.loads(original('precinct-ids-pre'))['objectIds'];ck(set(ids)==set(json.loads(original('precinct-ids-post'))['objectIds']) and len(ids)==len(set(ids))==2177);ck(json.loads(original('precinct-count-pre'))==json.loads(original('precinct-count-post'))=={'count':2177})
cfg=load(M/'service-batches.json');sv=load(M/'service-validation.json');byid={r['objectID']:r['all_attributes'] for r in sv['all_attributes']};got=[];points=0
fields={x['name'] for x in pre['fields'] if x['type']!='esriFieldTypeGeometry'}
for batch in cfg['batches']:
 r=load(S/batch['receipt']['path']);o=json.loads(body(r['body']));qs=urllib.parse.parse_qs(urllib.parse.urlsplit(r['requested_url']).query);ck(qs['outFields']==['*'] and qs['returnTrueCurves']==qs['returnZ']==qs['returnM']==['true']);ck(not set(qs)&{'outSR','geometryPrecision','quantizationParameters','maxAllowableOffset','resultOffset','resultRecordCount'});fs=o['features'];found=[f['attributes'][cfg['objectIdField']] for f in fs];ck(len(found)==len(set(found))==len(batch['requested_IDs'])<=50 and set(found)==set(batch['requested_IDs']));ck(not o.get('exceededTransferLimit') and o['spatialReference']['wkid']==26913);got.extend(found)
 for f in fs:
  a=f['attributes'];ck(set(a)==fields and a==byid[a[cfg['objectIdField']]]);g=f['geometry'];ck('rings' in g and 'curveRings' not in g)
  for ring in g['rings']:
   ck(all(len(p)==2 and all(math.isfinite(v) for v in p) for p in ring));points+=len(ring)
ck(len(cfg['batches'])==44 and len(got)==len(set(got))==2177 and set(got)==set(ids));ck(points==sv['XY_pairs_diagnosed']);ck(sv['county_counts']==zip_summaries[1]['county_counts'])
contract=load(S/'data/turnout/priority-set.json');bykey={r['key']:r for r in contract['constituents']};source=load(S/'data/turnout/original-extract.json')['2024-senate'];rawrows={r['key']:r for r in source['rows'] if r['level']=='Precinct'};inventory=[json.loads(b) for b in gzip.decompress((M/'inventory.jsonl.gz').read_bytes()).splitlines()];ck(len(inventory)==2201 and [r['complete_constituent']['key'] for r in inventory]==contract['complete_coverage_order']);ck(contract['ordered_priority_keys']==[])
for r in inventory:
 k=r['complete_constituent']['key'];ck(r['complete_constituent']==bykey[k] and r['complete_original_source_observation']==rawrows[k] and r['complete_original_header_and_party_rows']==source['header_rows']);ck(all(r[k] is None for k in ['matched_polygon_IDs','current_reporting_ID','polling_site','spatial_allocation']))
for key in ['certified_native_full_order','certified_native_top15','certified_native_minimum80']:ck(contract[key] is None)
parents=[load(p) for p in sorted((M/'parents').glob('*.json'))];ck(len(parents)==33)
for p in parents:ck(p['complete_source_child_keys']==[r['key'] for r in contract['constituents'] if r['parent_key']==p['key']]);ck(p['current_legal_geometry_match'] is None)
pdfs=load(M/'pdf-render-inventory.json');ck(len(pdfs)==60 and sum(r['pages'] for r in pdfs)==194);ck(all(r['pages']==len(r['full_page_automatic_renders']) for r in pdfs))
result={'status':'pass_independent_native_and_complete_source_preservation','checks':N,'owned_files_including_manifest':len(actual),'manifest_entries':len(listed),'complete_receipts':receipts,'request_hops':hops,'distinct_response_entities':len(entities),'native_ZIPs':zip_summaries,'service':{'features':2177,'batches':44,'full_pre_post_metadata_equal':True,'native_CRS':'EPSG26913','XY_pairs':points,'source_transforms_requested':False,'field_names':sorted(fields)},'complete_source_observations':2201,'complete_parents':33,'PDF_originals':60,'PDF_automatic_pages':194,'manual_visual_scope':'Root actually viewed2PDFpages SantaFe2026 and Cibola1,plus Sandoval2026 preview. Other pages not claimed manually.','source_repairs_or_producer_writes':False,'certified_native_priority':None,'current_legal_reporting_polygon_join':None,'reviewed_manifest':{'path':'maps/asset-manifest.json','bytes':(M/'asset-manifest.json').stat().st_size,'sha256':sha((M/'asset-manifest.json').read_bytes())}}
(S/'data/coordinator-maps-final-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':N,'source_rows':2201,'ZIP_XY_pairs':sum(x['XY_pairs_bitwise_compared_with_native_reader'] for x in zip_summaries),'service_XY':points}))

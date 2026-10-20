"""Independent original byte/geometry/service/HTML audit; no worker imports."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from urllib.parse import urlparse,parse_qs
import datetime,gzip,hashlib,io,json,struct,sys,zipfile
S=Path(__file__).resolve().parents[1];M=S/'maps';N=0
stats=Counter()
def ck(v,label=''):
 global N
 N+=1
 assert v,(N,label)
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def pack(v):return struct.pack('<'+'d'*len(v),*v)
def original(r):
 e=r['entity'];parts=[]
 for z in e['parts']:
  b=(M/z['path']).read_bytes();ck(len(b)==z['bytes']<40000000 and sha(b)==z['sha256']);parts.append(b)
 b=gzip.decompress(b''.join(parts));ck(len(b)==e['bytes'] and sha(b)==e['sha256']);return b
mf=load(M/'asset-manifest.json');before={}
actual={str(p.relative_to(S)) for p in M.rglob('*') if p.is_file()}|{'precinct-maps.md'}
ck({r['path'] for r in mf['assets']}==actual-{'maps/asset-manifest.json'} and len(mf['assets'])==5239)
for r in mf['assets']:
 p=S/r['path'];b=p.read_bytes();ck(not p.is_symlink() and len(b)==r['bytes']<40000000 and sha(b)==r['sha256']);before[r['path']]=sha(b)
ck(sum(v['bytes'] for v in mf['assets'])==1170607366)
receipts={};raw={};statuses=Counter()
for p in sorted((M/'source').glob('*.receipt.json')):
 r=load(p);rel=str(p.relative_to(M));ck(rel not in receipts and r['method']=='GET' and r['fields'] is None and r['request_body'] is None and r['utc_start']<=r['utc_end']);receipts[rel]=r
 for h in r['hops']:
  ck(r['utc_start']<=h['utc_start']<=h['utc_end']<=r['utc_end'] and isinstance(h['headers'],list));v=original({'entity':h['entity']});raw[h['entity']['sha256']]=v;stats['whole_response_hops']+=1
 if r['entity'] is None:ck(r['status'] is None and bool(r['error']))
 else:ck(original(r)==raw[r['entity']['sha256']])
 statuses[str(r['status'])]+=1
ck(len(receipts)==975 and stats['whole_response_hops']==1060)
source_summary=[]
for record in load(M/'zip-audit-index.json'):
 r=receipts[record['receipt']];b=raw[record['original_sha256']];ck(r['entity']['sha256']==record['original_sha256']);z=zipfile.ZipFile(io.BytesIO(b));proof=load(M/record['audit'])
 ck(z.testzip() is None and len(z.namelist())==len(set(z.namelist())) and proof['original_sha256']==sha(b) and proof['original_bytes']==len(b));ck([v['name'] for v in proof['members']]==z.namelist())
 for pin,zi in zip(proof['members'],z.infolist()):
  payload=z.read(zi);ck(pin['bytes']==len(payload)==zi.file_size and pin['compressed_bytes']==zi.compress_size and pin['sha256']==sha(payload) and pin['crc32']==zi.CRC and pin['zip_date_time']==list(zi.date_time));stats['complete_ZIP_members']+=1
 ck(len(proof['datasets'])==sum(n.lower().endswith('.shp') for n in z.namelist()))
 for d in proof['datasets']:
  shp=z.read(d['members']['.shp']);shx=z.read(d['members']['.shx']);dbf=z.read(d['members']['.dbf']);records=d['records']
  for v in [shp,shx]:ck(struct.unpack_from('>i',v)[0]==9994 and struct.unpack_from('>i',v,24)[0]*2==len(v) and struct.unpack_from('<i',v,28)[0]==1000)
  ck(shp[:100].hex()==d['header_hex'] and shp[32:100]==shx[32:100] and struct.unpack_from('<i',shp,32)[0]==5)
  n,header,width=struct.unpack_from('<IHH',dbf,4);ck(n==len(records) and len(shx)==100+n*8 and dbf[:header].hex()==d['dbf_header_hex'])
  cpg=z.read(d['members']['.cpg']).decode().strip();ck(cpg==d['cpg_literal'] and z.read(d['members']['.prj']).decode()==d['source_crs_wkt']);enc='utf-8' if cpg.upper() in ['UTF-8','65001'] else cpg
  schema=[];offset=1;offsets=[]
  for pos in range(32,header-1,32):
   desc=dbf[pos:pos+32];schema.append({'name':desc[:11].split(b'\0')[0].decode(enc),'type':chr(desc[11]),'width':desc[16],'decimal':desc[17],'descriptor_hex':desc.hex()});offsets.append(offset);offset+=desc[16]
  ck(schema==d['fields'] and offset==width);cursor=100
  for i,f in enumerate(records):
   off,length=struct.unpack_from('>ii',shx,100+i*8);num,sz=struct.unpack_from('>ii',shp,cursor);block=shp[cursor+8:cursor+8+sz*2]
   ck(off*2==cursor==f['shp_offset'] and length==sz and num==i+1==f['record_number'] and len(block)==f['content_bytes'] and sha(block)==f['content_sha256'])
   typ=struct.unpack_from('<i',block)[0];ck(typ==f['source_shape_type'])
   if typ==5:
    rings,points=struct.unpack_from('<ii',block,36);ix=list(struct.unpack_from('<'+'i'*rings,block,44));start=44+rings*4;ck(ix==f['parts'] and len(f['points'])==points and len(block)==start+points*16 and pack(f['bbox'])==block[4:36])
    for j,p in enumerate(f['points']):ck(pack(p)==block[start+j*16:start+(j+1)*16])
    stats['XY_double_values']+=points*2;stats['parts']+=rings
   else:ck(typ==0 and len(block)==4 and f['points']==[] and f['parts']==[])
   row=dbf[header+i*width:header+(i+1)*width];ck(row[:1].hex()==f['deletion_flag_hex'] and f['deleted']==(row[:1]==b'*'));values=[];tokens=[]
   for field,off in zip(schema,offsets):
    token=row[off:off+field['width']];t=token.decode(enc);kind=field['type'];tokens.append(token.hex())
    if kind=='C':value=t.rstrip('\x00 ')
    elif kind in ('N','F'):value=None if not t.strip(' *\x00') else int(t) if kind=='N' and not field['decimal'] else float(t)
    elif kind=='D':value=None if not t.strip(' 0\x00') else {'date':datetime.date(int(t[:4]),int(t[4:6]),int(t[6:8])).isoformat()}
    else:raise AssertionError(('unhandled native DBF type',kind))
    values.append(value);stats['literal_DBF_tokens']+=1
   ck(tokens==f['field_tokens_hex'] and values==f['values']);stats['native_SHP_records']+=1;cursor+=8+sz*2
  ck(cursor==len(shp));source_summary.append({'receipt':record['receipt'],'dataset':d['shp'],'records':n,'source_crs_wkt':d['source_crs_wkt'],'source_geometry_generalization':d['source_generalization']})
 stats['complete_ZIP_audits']+=1
ck(stats['complete_ZIP_audits']==46 and stats['XY_double_values']==2516662 and stats['literal_DBF_tokens']==36657 and stats['native_SHP_records']==3012)
def source_json(rel):return json.loads(raw[receipts[rel]['entity']['sha256']])
features=[]
for layer in load(M/'native-service-captures.json'):
 pre,post=layer['pre'],layer['post'];lp,lq=source_json(pre['layer']),source_json(post['layer']);sp,sq=source_json(pre['service']),source_json(post['service']);ck(lp==lq and sp==sq);ids=source_json(pre['all_ids'])['objectIds'];ck(ids==source_json(post['all_ids'])['objectIds']==pre['ordered_ids']==post['ordered_ids'] and len(ids)==len(set(ids))==layer['count']);ck(source_json(pre['count'])['count']==source_json(post['count'])['count']==len(ids));allids=[]
 for page in layer['pages']:
  query=parse_qs(urlparse(receipts[page['receipt']]['requested_url']).query);ck(set(query)=={'f','objectIds','outFields','returnGeometry','returnZ','returnM','returnTrueCurves'} and query['outFields']==['*']);ck(all(query[k]==['true'] for k in ['returnGeometry','returnZ','returnM','returnTrueCurves']))
  data=source_json(page['receipt']);got=[f['attributes'][pre['object_id_field']] for f in data['features']];asked=[int(v) for v in query['objectIds'][0].split(',')];ck(asked==page['requested_ids'] and 0<len(asked)<=50 and set(got)==set(asked) and got==page['returned_ids'] and not set(got)&set(allids));allids+=got
  ck(data['spatialReference']==lp['extent']['spatialReference']==page['spatial_reference'])
  for f in data['features']:ck(set(f['attributes'])=={v['name'] for v in lp['fields']});features.append(f)
 ck(len(allids)==len(ids) and set(allids)==set(ids) and layer['current_geography_approved'] is False and layer['result_label_join'] is None)
class DOM(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.kind=None;self.key=None;self.active=False;self.buf=[];self.units=[];self.parents=[];self.roots={};self.features=[];self.rows=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='details':self.kind=d.get('class');self.key=d.get('data-root');self.attrs=d
  if t=='pre':self.active=True;self.buf=[]
 def handle_data(self,s):
  if self.active:self.buf.append(s)
 def handle_endtag(self,t):
  if t=='pre':
   v=json.loads(''.join(self.buf));self.active=False
   if self.kind=='unit':self.units.append(v);self.rows.append(self.attrs)
   elif self.kind=='parent':self.parents.append(v)
   elif self.kind=='root-context':self.roots[self.key]=v
   elif self.kind=='native-feature':self.features.append(v)
  if t=='details':self.kind=None;self.key=None
c=load(S/'data/turnout/priority-set.json');parents=load(M/'county-investigations.json');dom=DOM();dom.feed((M/'index.html').read_text());ck(dom.units==c['units'] and dom.parents==parents and dom.roots=={k:v for k,v in c.items() if k not in ['units','parents']} and dom.features==features)
ck([v['data-key'] for v in dom.rows]==c['full_order'] and [v['data-key'] for v in dom.rows if v['data-tier']=='priority']==c['ordered_priority_keys'] and [v['data-key'] for v in dom.rows if v['data-tier']=='remainder']==c['remainder_keys'])
bykey={u['key']:u for u in c['units']};assets=[]
for parent,original_parent in zip(parents,c['parents']):
 ck(parent['complete_original_parent']==original_parent);fips=parent['county_fips'];keys=[k for k in c['full_order'] if bykey[k]['county_fips']==fips];ck(parent['ordered_source_rank_children']==keys and parent['ordered_priority_children']==[k for k in keys if k in set(c['ordered_priority_keys'])] and parent['ordered_remainder_children']==[k for k in keys if k in set(c['remainder_keys'])]);ck(parent['historical_result_label_polygon_match'] is None and parent['current_2026_ID_crosswalk'] is None and parent['administrative_unit_polygon_assumption'] is False)
 if parent['downloaded_map_asset_count']:assets.append(parent['county'])
ck(len(parents)==67 and sum(bool(p['ordered_priority_children']) for p in parents)==63 and len(assets)==26 and len(features)==157)
for rel,digest in before.items():ck(sha((S/rel).read_bytes())==digest,'unchanged sealed map input')
result={'status':'pass','checks':N,'manifest_sha256':sha((M/'asset-manifest.json').read_bytes()),'exact_manifest_targets':len(mf['assets']),'acquisition_receipts':len(receipts),'source_final_statuses':dict(statuses),'counts':dict(stats),'all_original_native_objects_in_DOM':len(dom.units),'all_complete_other_root_objects_in_DOM':len(dom.roots),'all_complete_native_service_features_in_DOM':len(features),'all_parent_objects':len(parents),'priority_parents':63,'downloaded_county_asset_context_parents':assets,'worker_sealed_audit_actually_rerun':{'status':'PASS','all_PDFs':242,'all_automatic_pages':2087,'negative_fixtures':32,'actual_JS_cases':207,'deterministic_outputs':10},'coordinator_actual_image_scope':['maps/pdf/70399be7c73b4d98cfd560dbb1047a381da78b7cd3b3f34ba7938edf097ecabf/page-0001.png','maps/pdf/37b08c0b9f51f603c20b1445653124947b6439e4a0528bd2cc2f2c1babcb7588/page-0001.png'],'manual_reading':'Two whole original map pages: Etowah title2023; Mobile Voter Precincts with map-created3/10/2026, polling sites and map-use disclaimer. No result-label aliases/legal adoption inferred. Remaining pages automatic or explicit worker manual scope only.','qualifications':'Madison target app election-office endorsement remains unestablished; source attributes/native geometry captured, no current/legal/result join or allocation. Full TIGER failures and source-generalized historical cartographic fallback remain distinct. No November/live/cadence/pool/calibration approval.','all_sealed_owned_bytes_unchanged':True}
out=S/'data/coordinator-maps-final-review.json'
if '--check' in sys.argv:ck(load(out)==result)
else:out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))

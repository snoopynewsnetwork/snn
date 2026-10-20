"""Coordinator independent original/native/binary/DOM audit; no producer imports."""
from pathlib import Path
import collections,gzip,hashlib,io,json,struct,urllib.parse,zipfile,zlib
from html.parser import HTMLParser
import shapefile

S=Path(__file__).resolve().parents[1];M=S/'maps';N=0
def ck(v):
 global N
 N+=1
 assert v, N
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
 b=(S/p).read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def exact(r):
 b=(S/r['path']).read_bytes();ck(len(b)==r['bytes'] and sha(b)==r['sha256']);return b
def raw(r):
 b=b''.join(exact(p) for p in r['parts']);ck(len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256'])
 b=gzip.decompress(b) if 'gzip' in r['encoding'] else b
 ck(len(b)==r['raw_bytes'] and sha(b)==r['raw_sha256']);return b
def entity(path):
 r=load(path);return raw(r['entities'][-1]['body'])
def semantic(x):return sha(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())
def pointer(x,p):
 for k in p.split('/')[1:]:
  k=k.replace('~1','/').replace('~0','~');x=x[int(k)] if isinstance(x,list) else x[k]
 return x
def fullref(r):
 b=exact(r['whole_file']);x=json.loads(b);obj=pointer(x,r['pointer']);ck(semantic(obj)==r['full_object_semantic_sha256']);return obj

manifest=load('maps/asset-manifest.json');ck(manifest['excluded_only']=='maps/asset-manifest.json')
actual={str(p.relative_to(S)) for p in M.rglob('*') if p.is_file()}|{'precinct-maps.md'}
rows=manifest['files'];ck(len(rows)==len({r['path'] for r in rows})==1493);ck(set(r['path'] for r in rows)==actual-{'maps/asset-manifest.json'})
for r in rows:ck(r['bytes']<40000000);exact(r)
authority_sha=sha((S/'data/coordinator-source-research-acceptance.json').read_bytes())
for p in M.rglob('*'):
 ck(not set(p.relative_to(M).parts)&{'__pycache__','node_modules','.pytest_cache','.venv'})
 if p.is_file() and p.suffix in ['.py','.json','.md','.html']:ck(authority_sha.encode() not in p.read_bytes())
seal=load('maps/finalseal.json')
for r in seal['proofs']:exact(r)
for p in ['maps/finalseal.json','maps/qa/validation.json']:ck(sha((M/'asset-manifest.json').read_bytes()).encode() not in (S/p).read_bytes())

requests=hops=0;entities=set();statuses=collections.Counter()
for p in sorted((M/'requests').glob('*.json')):
 r=load(str(p.relative_to(S)));requests+=1;ck(bool(r['started_utc']) and bool(r['finished_utc']) and bool(r['requested_url']) and isinstance(r['request_headers'],dict))
 for e in r['entities']:
  hops+=1;statuses[e['status']]+=1;ck(bool(e['url']) and bool(e['retrieved_utc']) and isinstance(e['headers'],list))
  if e.get('body'):entities.add(sha(raw(e['body'])))
ck(requests==404)

contract=load('data/turnout/priority-set.json');inv=load('maps/inventory.json.gz')
ck(len(inv['parents'])==36 and len(inv['known_source_contexts'])==510 and len(inv['unavailable_native_parent_cases'])==31)
ck(json.loads(exact(inv['frozen_contract']))==contract)
parents=contract['all_36_county_parents'];source={r['key']:r for p in parents for r in p['source_native_constituents']}
ck(len(source)==510 and [p['county_key'] for p in parents]==[p['county_key'] for p in inv['parents']])
for p,r in zip(parents,inv['parents']):
 ck(fullref(r['full_parent_ref'])==p);ck(r['current_result_leaf_polygon_joins']==[] and r['current_geography_approved'] is False)
 ck(set(r['gaps'])=={'vintage','access','CRS','physical','legal','finer_ID','native_result_membership'} and bool(r['shared_parent_resource_keys']))
for r in inv['known_source_contexts']:
 ck(fullref(r['source_context_ref'])==source[r['key']]);ck(fullref(r['full_parent_ref'])['county_key']==r['parent_key'])
 ck(r['inferred_leaf_join'] is None and r['allocated_votes_ballots_registration'] is False)
for r in inv['unavailable_native_parent_cases']:ck(fullref(r['full_unavailable_parent_ref'])['unknown_native_membership'] is True and r['native_membership'] is None)
for k in ['canonical_statewide_native_order','canonical_top15','canonical_minimum80','canonical_priority','canonical_remainder']:ck(inv[k] is None)

# Complete native snapshots and every returned attribute/geometry remain original.
features=pages=curves=missing=empty=positions=0;native=[]
for p in sorted((M/'native').glob('*.json')):
 snap=load(str(p.relative_to(S)));ck(snap['complete'] is True)
 before={k:json.loads(entity(snap['pre_'+k])) for k in ['service','layer','count','ids']}
 after={k:json.loads(entity(snap['post_'+k])) for k in before};ck(before==after)
 ck(snap['pre_post_changes']=={k:[] for k in before})
 ids=before['ids']['objectIds'];oid=before['ids']['objectIdFieldName'];ck(len(ids)==len(set(ids))==before['count']['count']==snap['feature_count'])
 fieldnames={f['name'] for f in before['layer']['fields'] if f['type']!='esriFieldTypeGeometry'};got=[]
 for page in snap['pages']:
  r=load(page['request']);q=urllib.parse.parse_qs(urllib.parse.urlsplit(r['requested_url']).query)
  ck(set(q)=={'f','objectIds','outFields','returnGeometry','returnZ','returnM','returnTrueCurves'})
  ck(q['outFields']==['*'] and all(q[k]==['true'] for k in ['returnGeometry','returnZ','returnM','returnTrueCurves']))
  asked=list(map(int,q['objectIds'][0].split(',')));ck(asked==page['requested_ids'] and len(asked)<=50)
  x=json.loads(entity(page['request']));fs=x['features'];observed=[f['attributes'][oid] for f in fs]
  ck(len(observed)==len(set(observed)) and set(observed)==set(asked) and observed==page['returned_ids']);ck(not x.get('exceededTransferLimit',False));got+=observed;pages+=1
  for f in fs:
   ck(set(f['attributes'])==fieldnames)
   g=f.get('geometry')
   if not g:missing+=1;continue
   ck(x.get('spatialReference') is not None)
   ck(all(before['layer']['extent']['spatialReference'].get(k)==v for k,v in x['spatialReference'].items()))
   if 'curveRings' in g or 'curvePaths' in g:curves+=1
   elif not g.get('rings'):empty+=1
   else:
    for ring in g['rings']:
     positions+=len(ring);ck(all(len(v)>=2 for v in ring))
 ck(len(got)==len(set(got))==len(ids) and set(got)==set(ids));features+=len(got)
 native.append({'key':snap['key'],'features':len(got),'native_CRS':snap['native_crs'],'full_pre_post_equal':True})
ck(len(native)==18 and features==2174 and pages==54 and curves==246 and missing==66 and empty==4)

# Independent struct parsing and every XY bit checked against PyShp points/parts.
zip_members=dbf_cells=xy_values=shape_records=0;binary=[]
for summary in load('maps/qa/binary-summary.json'):
 b=entity(summary['request']);z=zipfile.ZipFile(io.BytesIO(b));a=load(summary['audit']);ck(z.testzip() is None and sha(b)==a['zip_sha256']);ck(len(z.infolist())==len(a['members']))
 for info,am in zip(z.infolist(),a['members']):
  r=z.read(info);ck(info.filename==am['name'] and len(r)==am['bytes'] and sha(r)==am['sha256'] and f'{zlib.crc32(r)&0xffffffff:08x}'==am['crc32']);zip_members+=1
 for layer in a['layers']:
  stem=layer['stem'];shp=z.read(stem+'.shp');shx=z.read(stem+'.shx');dbf=z.read(stem+'.dbf');rd=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf));n,header,width=struct.unpack_from('<IHH',dbf,4)
  ck(n==len(rd)==layer['records'] and len(shx)==100+8*n and struct.unpack_from('>i',shp,24)[0]*2==len(shp));ck(header==layer['dbf_header_bytes'] and width==layer['dbf_record_bytes'])
  for i,f in enumerate(layer['dbf_schema']):
   d=dbf[32+32*i:64+32*i];ck(sha(d)==f['descriptor_sha256']);ck([f['name'],f['type'],f['width'],f['decimals']]==list(rd.fields[i+1]))
  xy_stream=hashlib.sha256();offset=100;xy_layer=0
  for i,(ar,sr) in enumerate(zip(layer['dbf_records'],layer['shp_shx_records'])):
   row=dbf[header+i*width:header+(i+1)*width];ck(sha(row)==ar['sha256'] and ar['offset']==header+i*width);pos=1;record=rd.record(i)
   for j,(f,cell) in enumerate(zip(layer['dbf_schema'],ar['cells'])):
    rawcell=row[pos:pos+f['width']];pos+=f['width'];ck(sha(rawcell)==cell['raw_sha256']);ck(record[j]==cell['value']);dbf_cells+=1
   ck(pos==width);num,words=struct.unpack_from('>ii',shp,offset);content=shp[offset+8:offset+8+words*2]
   ck(num==i+1 and offset==sr['shp_offset'] and words==sr['content_words'] and sha(content)==sr['record_sha256']);ck(struct.unpack_from('>ii',shx,100+i*8)==(offset//2,words))
   typ=struct.unpack_from('<i',content)[0];shape=rd.shape(i);ck(typ==shape.shapeType==sr['shape_type'])
   if typ:
    nr,np=struct.unpack_from('<ii',content,36);parts=list(struct.unpack_from('<'+'i'*nr,content,44));start=44+4*nr;xy=content[start:start+np*16]
    ck(parts==list(shape.parts)==sr['parts'] and np==len(shape.points)==sr['positions']);ck(struct.pack('<4d',*shape.bbox)==content[4:36]);ck(b''.join(struct.pack('<dd',*p[:2]) for p in shape.points)==xy)
    for j,pnt in enumerate(shape.points):ck(struct.pack('<dd',*pnt[:2])==xy[j*16:(j+1)*16])
    xy_stream.update(xy);xy_layer+=np*2
   offset+=8+words*2
  ck(offset==len(shp) and xy_stream.hexdigest()==layer['raw_xy_stream_sha256']==layer['adapter_xy_stream_sha256']);ck(xy_layer==layer['xy_IEEE754_values_checked']);xy_values+=xy_layer;shape_records+=n
  binary.append({'stem':stem,'records':n,'full_DBF_cells':n*len(layer['dbf_schema']),'XY_IEEE754_values':xy_layer,'native_PRJ':layer['prj']})
ck(zip_members==128 and dbf_cells==5183 and xy_values==416896 and shape_records==253)

class DOM(HTMLParser):
 def __init__(self,b):
  super().__init__(convert_charrefs=True);self.objects=[];self.active=None;self.scripts=0;self.links=[];self.ids=[];self.feed(b.decode())
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='pre':self.active=[d,'']
  if t=='script':self.scripts+=1
  if 'id' in d:self.ids.append(d['id'])
  for k in ['src','href']:
   if k in d:self.links.append(d[k])
 def handle_data(self,d):
  if self.active:self.active[1]+=d
 def handle_endtag(self,t):
  if t=='pre' and self.active:self.objects.append(self.active);self.active=None
known={};parentobjs={};link_n=0;htmlpages=list(M.rglob('*.html'))
for p in htmlpages:
 dom=DOM(p.read_bytes());ck(dom.scripts==0 and len(dom.ids)==len(set(dom.ids)))
 for attrs,text in dom.objects:
  if attrs.get('data-kind')=='context':ck(attrs['data-key'] not in known);known[attrs['data-key']]=json.loads(text)
  elif attrs.get('data-kind')=='parent':ck(attrs['data-key'] not in parentobjs);parentobjs[attrs['data-key']]=json.loads(text)
 for u in dom.links:
  url=urllib.parse.urlsplit(u)
  if url.scheme:continue
  target=(p.parent/urllib.parse.unquote(url.path)).resolve() if url.path else p
  ck(target.is_file())
  if url.fragment and target.suffix=='.html':ck(urllib.parse.unquote(url.fragment) in DOM(target.read_bytes()).ids)
  link_n+=1
ck(len(htmlpages)==40 and known==source and parentobjs=={p['county_key']:p for p in parents})
pdfs=load('maps/renders/index.json');ck(len(pdfs)==135 and sum(r['page_count'] for r in pdfs)==416)
for r in pdfs:ck(r['complete_render'] and len(r['pages'])==r['page_count']);[exact(p['render']) for p in r['pages']]
visual=load('maps/qa/visual-review.json');ck(len(visual['manual_pdf_pages'])==6 and len(visual['manual_geographic_previews'])==5)
result={'status':'pass_independent_map_native_binary_complete_source_preservation','checks':N,'owned_manifest_targets':1493,'complete_owned_files':1494,'map_requests':requests,'own_response_hops':hops,'own_unique_response_bodies':len(entities),'own_response_statuses':dict(statuses),'all_parents':36,'complete_known_context_objects':510,'unavailable_parent_cases':31,'native_snapshots':native,'nonadditive_native_features':features,'ID_pages_max50':pages,'full_pre_post_service_layer_count_IDs_equal':True,'curved_feature_records_preserved_excluded_whole':curves,'null_geometry_records':missing,'empty_nonpolygon_records':empty,'binary_layers':binary,'ZIP_members':zip_members,'SHP_records':shape_records,'full_DBF_cells':dbf_cells,'XY_IEEE754_values_bitwise_compared':xy_values,'static_HTML_pages':40,'whole_objects_in_DOM':546,'local_HTML_links':link_n,'whole_PDFs':135,'automatically_rendered_pages':416,'worker_manual_scope':{'PDF_pages':6,'native_previews':5},'coordinator_manual_scope':{'original_PDF_pages':['Multnomah4501 page1','Umatilla2026 page1'],'native_previews':['Benton precinct linear preview'],'other_pages_claimed_manually':False},'canonical_native_order_top15_min80_priority_remainder':None,'inferred_result_polygon_joins':0,'spatial_allocations':False,'source_repairs_or_producer_writes':False,'reviewed_manifest':{'path':'maps/asset-manifest.json','bytes':(M/'asset-manifest.json').stat().st_size,'sha256':sha((M/'asset-manifest.json').read_bytes())}}
(S/'data/coordinator-maps-final-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':N,'native_features':features,'XY_values':xy_values,'HTML_pages':40}))

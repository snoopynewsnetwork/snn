"""Independent stdlib audit of map HTTP entities, native batches and binary archives."""
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
import collections,gzip,hashlib,io,json,math,struct,xml.etree.ElementTree as ET,zipfile
ROOT=Path(__file__).resolve().parents[1];MAP=ROOT/'maps'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_bytes())
canon=lambda o:json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
receipts={p.name.removesuffix('.receipt.json'):load(p) for p in (MAP/'raw').glob('*.receipt.json')}
def raw(sid):
 r=receipts[sid];p=MAP/r['stored_path'];s=p.read_bytes();assert len(s)==r['stored_bytes'] and sha(s)==r['stored_sha256']
 b=gzip.decompress(s) if r.get('compression')=='gzip' else s
 assert len(b)==r['original_bytes'] and sha(b)==r['original_sha256'];return b
def digest_feature(d,attrs,geometry,vertices,rings):
 assert d['attributes']==attrs and d['attributes_sha256']==sha(canon(attrs))
 assert d['geometry_sha256']==sha(canon(geometry))
 assert d['vertex_count']==vertices and d['ring_count']==rings
def shp_audit(key):
 z=zipfile.ZipFile(io.BytesIO(raw(key)));assert z.testzip() is None
 detail=load(MAP/'geometry'/f'{key}.json');metadata=detail['source_metadata']
 for m in metadata['archive_members']:
  info=z.getinfo(m['name']);b=z.read(info);assert sha(b)==m['sha256'] and len(b)==m['bytes'] and f'{info.CRC:08x}'==m['CRC32']
 base=next(n[:-4] for n in z.namelist() if n.endswith('.shp'));shp=z.read(base+'.shp');shx=z.read(base+'.shx');dbf=z.read(base+'.dbf')
 assert struct.unpack_from('>i',shp,0)[0]==9994 and struct.unpack_from('>i',shp,24)[0]*2==len(shp)
 assert struct.unpack_from('>i',shx,24)[0]*2==len(shx)
 count=(len(shx)-100)//8;dbcount,hlen,rlen=struct.unpack_from('<IHH',dbf,4);assert count==dbcount==metadata['SHP_SHX_DBF_record_count']
 fields=[];p=32
 while dbf[p]!=13:
  q=dbf[p:p+32];fields.append((q[:11].split(b'\x00')[0].decode(),chr(q[11]),q[16],q[17]));p+=32
 encoding=z.read(base+'.cpg').decode().strip() if base+'.cpg' in z.namelist() else 'utf-8'
 features={f['source_locator']['record_1based']:f for f in detail['all_features']};points=0;selected=0
 for n in range(count):
  offset,length=struct.unpack_from('>II',shx,100+8*n);record,actual=struct.unpack_from('>II',shp,offset*2)
  assert record==n+1 and actual==length and offset*2+8+length*2<=len(shp)
  body=shp[offset*2+8:offset*2+8+length*2];kind=struct.unpack_from('<I',body)[0];assert kind in [5,15,25],kind
  parts,num=struct.unpack_from('<II',body,36);starts=list(struct.unpack_from('<'+'I'*parts,body,44));start=44+4*parts
  xy=[list(struct.unpack_from('<dd',body,start+16*i)) for i in range(num)];assert all(math.isfinite(v) for pt in xy for v in pt)
  rings=[xy[a:b] for a,b in zip(starts,starts[1:]+[num])]
  extra=start+16*num;zs=None;ms=None
  if kind==15:zs=list(struct.unpack_from('<'+'d'*num,body,extra+16));extra+=16+8*num
  if kind in [15,25] and len(body)>=extra+16+8*num:ms=[v if v>-1e39 else None for v in struct.unpack_from('<'+'d'*num,body,extra+16)]
  row=dbf[hlen+n*rlen:hlen+(n+1)*rlen];assert row[0]==32;attrs={};k=1
  for name,typ,width,dec in fields:
   val=row[k:k+width];k+=width;s=val.decode(encoding).strip('\x00 ')
   if typ in ['N','F']:value=None if not s or '*' in s else (float(s) if dec else int(s))
   elif typ=='L':value=True if s in ['Y','T'] else False if s in ['N','F'] else None
   else:value=s
   attrs[name]=value
  if n+1 not in features:continue
  f=features[n+1];digest_feature(f,attrs,{'rings':rings,'z':zs,'m':ms},num,parts);selected+=1;points+=num
 assert selected==len(features)
 return {'source':key,'original_records':count,'selected_records':selected,'full_XY_positions_compared':points,'CRC_members':len(z.infolist()),'native_Z_M_parsed':True}
def main():
 mfraw=(MAP/'asset-manifest.json').read_bytes();assert sha(mfraw)=='4c5385dffd8b0f375dbd8698a38dd984fbe53bea893d2c3932804c279b84312e'
 mf=json.loads(mfraw);assert len(mf['files'])==733
 expected={p.resolve() for p in MAP.rglob('*') if p.is_file() and p!=MAP/'asset-manifest.json'}|{(ROOT/'precinct-maps.md').resolve()}
 assert expected=={(ROOT/r['path']).resolve() for r in mf['files']}
 for r in mf['files']:
  b=(ROOT/r['path']).read_bytes();assert sha(b)==r['sha256'] and len(b)==r['bytes']<40000000
 c=load(ROOT/'data/turnout/priority-set.json');semantic=json.loads(gzip.decompress((MAP/'frozen-contract.semantic.json.gz').read_bytes()));assert c==semantic
 inventory=load(MAP/'inventory.json');assert [r['frozen_parent'] for r in inventory['full67_inventory']]==c['all_unit_order']
 assert all(r['downloads'] and r['official_reference_acquired'] for r in inventory['full67_inventory'][:22])
 entity_count=0;errors=0
 for sid,r in receipts.items():
  if r.get('stored_path'):raw(sid);entity_count+=1
  errors+=r['status']!=200
 acqs=[];coordinates=0;curves=0;allfeatures=0
 for path in sorted(MAP.glob('*.acquisition.json')):
  a=load(path);pre=json.loads(raw(a['ids_pre_source_id']));post=json.loads(raw(a['ids_post_source_id']));meta=json.loads(raw(a['layer_source_id']));meta2=json.loads(raw(a['key']+'-layer-post'))
  assert set(pre['objectIds'])==set(post['objectIds']) and len(pre['objectIds'])==len(set(pre['objectIds']))==a['source_count']
  assert json.loads(raw(a['key']+'-count'))['count']==a['source_count'];assert meta.get('editingInfo')==meta2.get('editingInfo')==a['pre_editingInfo']==a['post_editingInfo']
  detail=load(MAP/'geometry'/f"{a['key']}.json");di={(x['source_locator']['source_id'],x['source_locator']['feature_index_0based']):x for x in detail['all_features']};seen=set();vertices=0
  for batch in a['batches']:
   sid=batch['source_id'];b=json.loads(raw(sid));q=parse_qs(urlsplit(receipts[sid]['request_url']).query)
   assert q['outFields']==['*'] and all(q[k]==['true'] for k in ['returnGeometry','returnZ','returnM','returnTrueCurves'])
   assert not set(q)&{'outSR','geometryPrecision','quantizationParameters','maxAllowableOffset'}
   assert not b.get('error') and not b.get('exceededTransferLimit');requested=set(map(int,q['objectIds'][0].split(',')));assert requested==set(batch['requested_ids']) and len(requested)<=50
   returned=set()
   for n,f in enumerate(b['features']):
    id=f['attributes'][a['object_id_field']];assert id not in seen;seen.add(id);returned.add(id)
    g=f['geometry'];assert g;rr=g.get('rings',[]);count=sum(len(r) for r in rr)
    digest_feature(di[(sid,n)],f['attributes'],g,count,len(rr));vertices+=count
    curves+=bool(g.get('curveRings'))
   assert returned==requested
  assert seen==set(pre['objectIds']) and len(di)==len(seen);allfeatures+=len(seen);coordinates+=vertices
  acqs.append({'key':a['key'],'features':len(seen),'batches':len(a['batches']),'native_XY_positions_compared':vertices,'all_attributes_and_geometry_hashes':True,'prepost_ID_count_edit_metadata_equal':True})
 assert len(acqs)==11 and allfeatures==3523 and curves==31
 archives=[];ns={'k':'http://www.opengis.net/kml/2.2'}
 for key in ['polk-kml','lee-kml','collier-kml']:
  z=zipfile.ZipFile(io.BytesIO(raw(key)));assert z.testzip() is None;details=load(MAP/'geometry'/f'{key}.json');meta=details['source_metadata'];doc=ET.fromstring(z.read('doc.kml'));target=meta['selected_folder'];di=details['all_features'];index=0;vertices=0
  for folder in doc.findall('.//k:Folder',ns):
   if folder.findtext('k:name',namespaces=ns)!=target:continue
   for pm in folder.findall('k:Placemark',ns):
    rings=[[[float(v) for v in word.split(',')] for word in (coords.text or '').split()] for poly in pm.findall('.//k:Polygon',ns) for coords in poly.findall('.//k:coordinates',ns)]
    attrs={'id':pm.get('id'),'name':pm.findtext('k:name',namespaces=ns),'description':pm.findtext('k:description',namespaces=ns),'extended_data':[ET.tostring(e,encoding='unicode') for e in pm.findall('k:ExtendedData',ns)]}
    pts=sum(map(len,rings));digest_feature(di[index],attrs,{'rings':rings,'z':None,'m':None},pts,len(rings));index+=1;vertices+=pts
  assert index==len(di);archives.append({'source':key,'native_selected_placemarks':index,'all_coordinate_ordinates_compared':vertices,'ZIP_CRC_pass':True})
 archives.extend(shp_audit(k) for k in ['hillsborough-shp-alt','duval-census2020-vtd'])
 geo=json.loads(raw('st-lucie-geojson'));details=load(MAP/'geometry/st-lucie-geojson.json')['all_features'];assert len(geo['features'])==len(details)
 for f,d in zip(geo['features'],details):
  g=f['geometry'];rings=g['coordinates'] if g['type']=='Polygon' else [r for p in g['coordinates'] for r in p];digest_feature(d,f['properties'],g,sum(map(len,rings)),len(rings))
 duval=raw('duval-archived-countywide-pdf');assert len(duval)==2628955 and sha(duval)=='044fdba7b7051901383875a284629d1276d037af73112c8bb68880f09b57043a'
 cdx=json.loads(raw('duval-cdx-1141'));assert cdx[1][0]=='20260106081626' and cdx[1][-1]=='2627790'
 pdf=load(MAP/'pdf-render-validation.json');assert len(pdf['PDFs'])==14 and sum(x['page_count'] for x in pdf['PDFs'])==89
 for p in pdf['PDFs']:
  for page in p['pages']:assert sha((MAP/page['preview_path']).read_bytes())==page['PNG_sha256']
 out={'status':'pass_native_originals_and_complete_frozen_scope','exact_owned_manifest_assets':733,'owned_manifest_sha256':sha(mfraw),'original_error_entities_hashed':entity_count,'retained_error_observations':errors,'complete_frozen_parents':67,'ordered_priority_official_references_including_historical_Duval':22,'full_frozen_contract_semantically_equal':True,'ArcGIS':acqs,'all_ArcGIS_features':allfeatures,'ArcGIS_linear_XY_positions_compared':coordinates,'native_curve_features_preserved':curves,'other_native_archives':archives,'St_Lucie_display_GeoJSON_features':len(details),'PDF_originals':14,'PDF_page_previews_hashed':89,'Duval_archive':{'raw_bytes':len(duval),'raw_sha256':sha(duval),'capture_UTC':'2026-01-06T08:16:26Z','CDX_record_length_not_entity_size':2627790,'scope':'Official historical school-board map with precinct overlay; November2025 footer/metadata, January2026 capture, October2026 retrieval are distinct clocks. Current403s/Census fallback preserved.'},'production_admission':'None. Full source attributes/coordinates/curves retained; no topology repair, cross-year/current result-geometry join, vote allocation, November boundary approval or display-export precision assumption.'}
 (ROOT/'data/coordinator-map-native-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['ArcGIS','other_native_archives']}))
if __name__=='__main__':main()

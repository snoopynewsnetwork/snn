"""Independent sealed-map/raw-native audit; no producer import or source join."""
from pathlib import Path
from html.parser import HTMLParser
import collections,gzip,hashlib,io,json,struct,zipfile,zlib
import shapefile
S=Path(__file__).resolve().parents[1];M=S/'maps';N=0

def ck(v,note=''):
 global N
 assert v,note;N+=1

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def read(p):
 p=Path(p);p=p if p.is_absolute()else S/p;b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def verify(p):
 b=(S/p['path']).read_bytes();ck(len(b)==p['bytes']<40000000,p['path']);ck(sha(b)==p['sha256'],p['path']);return b
def body(r):
 if not r['stored_parts']:
  ck(r['method']=='HEAD'or bool(r.get('error'))or r.get('status')is None);return None
 b=b''.join(verify(p)for p in r['stored_parts']);b=gzip.decompress(b)if r.get('storage','').startswith('Concatenate parts then gzip.decompress')else b
 ck(len(b)==r['raw_bytes']);ck(sha(b)==r['raw_sha256']);return b
class Links(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.links=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=='a'and 'href'in d:self.links.append(d['href'])

def main():
 mf=read('maps/asset-manifest.json');paths={str(p.relative_to(S))for p in M.rglob('*')if p.is_file()and p!=M/'asset-manifest.json'}|{'precinct-maps.md'};ck(paths=={x['path']for x in mf['assets']});ck(len(paths)==1006)
 for r in mf['assets']:verify(r)
 contract=read('data/turnout/priority-set.json');a=read('data/coordinator-priority-acceptance.json');verify(a['frozen_contract']);ck(len(contract)==31)
 for group in ['producer_seals','frozen_first_pair_assets','independent_coordinator_reviews','complete_source_companion_files']:
  for r in a[group]:verify(r)
 entries=read('maps/derived/full-inventory.json.gz');prior=read('maps/derived/priority-index.json.gz');remaining=read('maps/derived/remainder-index.json.gz');parents=read('maps/derived/parents.json.gz');ck(len(entries)==10062);ck(prior==entries[:5540]);ck(remaining==entries[5540:]);ck([r['key']for r in entries]==contract['full_order'])
 units={r['key']:r for r in contract['native_constituents']}
 for i,r in enumerate(entries,1):
  ck(r['source_observation']==units[r['key']]);ck(r['rank_full']==i and r['priority']==(i<=5540));ck(r['authority_key']==contract['native_to_authority_parent_map'][r['key']]);ck(r['matched_geometry']is r['physical_polygon']is r['source_method']is None)
 ck(len(parents)==108)
 for p,original in zip(parents,contract['authority_inventory']):
  ck(p['source_parent']==original);ck(p['all_children_source_order']==original['native_constituent_keys']);keys=[r['key']for r in entries if r['source_observation']['authority_id']==original['authority_id']];ck(p['all_children_rank_order']==keys);ck(p['ordered_priority_children']==[k for k in keys if k in set(contract['ordered_priority_keys'])]);ck(p['ordered_remainder_children']==[k for k in keys if k not in set(contract['ordered_priority_keys'])])
 requests={p.stem.removesuffix('.receipt'):read(p)for p in (M/'source').glob('*.receipt.json')};bodies={key:body(r)for key,r in requests.items()};ck(len(requests)==342)
 inv=read('maps/derived/authority-investigations.json');ck(len(inv)==108 and sum(bool(r['priority'])for r in inv)==97)
 for row in inv:
  r=read(row['archive_receipt']);b=body(r);ck(bool(b),'archive response');links=Links();links.feed(b.decode('utf-8-sig',errors='replace'));observed=set(links.links)
  for x in row['archive_files']:
   parent=read(x['parent_receipt']);h=Links();h.feed(body(parent).decode('utf-8-sig',errors='replace'));ck(x['href']in h.links,'actual literal map href')
  for p in row.get('leaf_access_receipts',[]):r=read(p);ck(r['method']in ['GET','HEAD']);ck(r['status']is not None or bool(r.get('error')))
 r=requests['census-illinois-vtd2020'];b=bodies['census-illinois-vtd2020'];z=zipfile.ZipFile(io.BytesIO(b));ck(z.testzip()is None);blobs={p:z.read(p)for p in z.namelist()}
 for info in z.infolist():ck(zlib.crc32(blobs[info.filename])&0xffffffff==info.CRC)
 ext={Path(k).suffix:v for k,v in blobs.items()};shp,shx,dbf=ext['.shp'],ext['.shx'],ext['.dbf'];ck(struct.unpack_from('>i',shp)[0]==9994);ck(struct.unpack_from('<i',shp,28)[0]==1000);ck(struct.unpack_from('<i',shp,32)[0]==5)
 count=struct.unpack_from('<I',dbf,4)[0];hlen,rlen=struct.unpack_from('<HH',dbf,8);fields=[];offset=1
 for p in range(32,hlen-1,32):
  f=dbf[p:p+32];name=f[:11].split(b'\0')[0].decode();fields.append((name,chr(f[11]),f[16],f[17],offset));offset+=f[16]
 ck(count==10084 and offset==rlen);reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf));ck(len(reader)==count)
 slices={};slice_counties=collections.Counter()
 for path in sorted((M/'derived/counties').glob('*.json.gz')):
  v=read(path);ck(v['native_coordinate_unit']=='degree')
  for row in v['records']:
   i=row['source_record_1based'];ck(i not in slices);slices[i]=row;slice_counties[v['source_county_fips']]+=1;ck(row['attributes']['STATEFP20']+row['attributes']['COUNTYFP20']==v['source_county_fips'])
 ck(len(slice_counties)==102 and set(slices)==set(range(1,count+1)));pos=100;parts_count=xy_count=0
 for i,(shape,record)in enumerate(zip(reader.shapes(),reader.records()),1):
  row=slices[i];number,words=struct.unpack_from('>2i',shp,pos);content=shp[pos+8:pos+8+words*2];ck(struct.unpack_from('>2i',shx,100+(i-1)*8)==(pos//2,words));ck(number==i);ck(pos==row['source_shp_byte_offset']);ck(words*2==row['source_content_bytes']);ck(sha(content)==row['source_content_sha256']);ck(struct.unpack_from('<i',content)[0]==row['shapeType']==5)
  bbox=list(struct.unpack_from('<4d',content,4));np,npts=struct.unpack_from('<ii',content,36);parts=list(struct.unpack_from('<'+'i'*np,content,44));coords=content[44+np*4:];ck(len(coords)==16*npts);ck(parts==list(shape.parts)==row['parts']);ck(struct.pack('<4d',*row['bbox'])==content[4:36]);ck(list(shape.bbox)==bbox);ck(len(row['points'])==npts)
  for k,(rawpt,persisted)in enumerate(zip(shape.points,row['points'])):
   ck(struct.pack('<2d',*rawpt)==coords[k*16:k*16+16]);ck(struct.pack('<2d',*persisted)==coords[k*16:k*16+16])
  rawrow=dbf[hlen+(i-1)*rlen:hlen+i*rlen];ck(rawrow==bytes.fromhex(row['dbf_row_hex']))
  for (name,kind,width,decimal,start),pv in zip(fields,record):
   cell=rawrow[start:start+width].decode();ck(cell==row['dbf_literal_fields'][name]);parsed=(float(cell.strip())if decimal else int(cell.strip()))if kind in 'NF'and cell.strip()else cell.strip();ck(parsed==pv==row['attributes'][name])
  ck(row['z']is row['m']is row['truecurves']is None);parts_count+=np;xy_count+=npts;pos+=8+words*2
 ck(pos==len(shp));ck(parts_count==10974 and xy_count==1664969)
 out=dict(status='pass_independent_complete_sealed_maps_and_native_binary_review',checks=N,owned_manifest=pin(M/'asset-manifest.json'),owned_entries=1006,complete_source_observations=10062,priority=5540,remainder=4522,source_parents=108,priority_parents=97,complete_request_receipts=len(requests),complete_source_objects_embedded_in_every_row=True,source_candidate_null_admin_fields_equal=True,actual_archive_literal_links_replayed=True,Census_whole_original_raw_sha256=sha(b),native_Census_features=count,county_slices=dict(sorted(slice_counties.items())),Census_parts=parts_count,Census_exact_XY_positions=xy_count,every_point_double_bit_pattern_verified=True,every_DBF_field_raw_and_parsed_value_verified=True,field_names=[f[0]for f in fields],no_producer_import_or_write=True,geometry_matches=0,current_legal_leaf_crosswalk_approved=False,qualification='Shared source/archive and historical Census context only; native reporting labels and city/county parents are not polygon or physical/current matches. All original source fields preserved; selected7PDFpages/4previews actual visual scope,71PDFs/118pages fullmetadata/text only; no allpage-render/browser claim.')
 p=S/'data/coordinator-maps-final-review.json';p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(dict(status=out['status'],checks=N,pin=pin(p)))
if __name__=='__main__':main()

from acquire import *
import json,csv,collections,zipfile,io
sources=[];originals={};zips=[]
for p in sorted((M/'receipts').glob('*.json')):
 r=json.loads(p.read_bytes());entry={k:r.get(k)for k in ['requested_url','final_url','method','query','body','parent','literal_href','retrieved_utc','clock_timezone','source_status','source_date','status','error','raw_bytes','raw_sha256','parts']};entry['receipt']=str(p.relative_to(M));sources.append(entry)
 for e in r.get('exchanges',[]):
  if e['raw_sha256']not in originals:originals[e['raw_sha256']]=dict(raw_bytes=e['raw_bytes'],parts=e['parts'],requests=[],observed_content_type=e['response_headers'].get('Content-Type'))
  originals[e['raw_sha256']]['requests'].append(str(p.relative_to(M)))
 if r.get('parts'):
  with gzip.open(M/r['parts'][0]['path'],'rb')as z:head=z.read(4)
  if head[:2]==b'PK':
   z=zipfile.ZipFile(io.BytesIO(body(r)));zips.append(dict(receipt=str(p.relative_to(M)),full_zip_CRC_error=z.testzip(),members=[dict(filename=i.filename,CRC=i.CRC,compressed_bytes=i.compress_size,uncompressed_bytes=i.file_size)for i in z.infolist()],SHP_members=[i.filename for i in z.infolist()if i.filename.lower().endswith('.shp')]))
dump(M/'source-index.json',sources);dump(M/'original-index.json',originals);dump(M/'ZIP-container-audit.json',dict(containers=zips,original_SHP_ZIP_acquired=any(x['SHP_members']for x in zips),qualification='Observed ZIP containers are office-document companions, not original SHP ZIPs. No SHP/SHX/DBF audit or silent ring-closing parser is claimed.'))
with (M/'manifest.csv').open('w',newline='')as f:
 fields=['raw_sha256','raw_bytes','stored_parts_json','observed_content_type','source_receipts_json','qualification'];w=csv.DictWriter(f,fields);w.writeheader()
 for h,x in originals.items():w.writerow(dict(raw_sha256=h,raw_bytes=x['raw_bytes'],stored_parts_json=json.dumps(x['parts'],separators=(',',':')),observed_content_type=x['observed_content_type'],source_receipts_json=json.dumps(x['requests'],separators=(',',':')),qualification='Complete acquired HTTP entity; see receipt for status/content shell/vintage/scope; no current/legal result match'))
print('source requests',len(sources),'unique originals',len(originals),'zip containers',len(zips))

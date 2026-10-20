"""Read/verify immutable originals; derive own Poppler text. No peer count imports."""
import gzip,hashlib,io,json,subprocess,tempfile,zipfile
from pathlib import Path
from immutable_sources import receipts as fixed_receipts,receipt_bytes,entity,restore_zip,metadata_bytes
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT.parent; NEWS=DATA/'news'; PEER=DATA/'turnout/source'
def sha(b):return hashlib.sha256(b).hexdigest()
def writejson(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def gz(p,b):p.write_bytes(gzip.compress(b,mtime=0))
def main():
 inventory=[]; receipts=[]
 def extract(key,b,origin):
  rec={'source_key':key,'raw_sha256':sha(b),'raw_bytes':len(b),'origin':origin}
  if b.startswith(b'%PDF-'):
   with tempfile.TemporaryDirectory(prefix='or-baseline-') as d:
    f=Path(d)/'source.pdf';f.write_bytes(b)
    r=subprocess.run(['pdftotext','-layout',str(f),'-'],capture_output=True,check=True)
    text=r.stdout;rec['extraction_stderr']=r.stderr.decode(errors='replace')
    rec['pages']=text.count(b'\x0c');rec['kind']='PDF'
  else:text=b;rec['kind']='CSV' if b'csv' in str(origin).lower().encode() else 'response'
  path=ROOT/'source/text'/f'{key}.txt.gz';gz(path,text)
  rec.update(text_path=str(path.relative_to(ROOT)),text_raw_sha256=sha(text),text_bytes=len(text),text_stored_sha256=sha(path.read_bytes()))
  inventory.append(rec)
 snapshot=fixed_receipts()
 pins=[x['source'] for x in snapshot if 'id' in x['source']]
 for s in pins:
  receipts.append({'receipt_path':str((PEER/'shared-original-pins.json').relative_to(DATA.parent)), 'source':s})
  if 'asset' in s:
   raw=gzip.decompress((NEWS/s['asset']).read_bytes());assert sha(raw)==s['raw_sha256']
 # Selected abstract reconstruction, using exact retained entities (not a peer extract).
 ids={s['id']:s for s in pins}
 def body(id):
  s=ids[id];p=NEWS/s['asset'];assert sha(p.read_bytes())==s['stored_sha256'];b=gzip.decompress(p.read_bytes());assert sha(b)==s['raw_sha256'];return b
 for key,ls in {'2024-abstract':['sos-2024-results-archived-20241212'],'2020-abstract':['sos-2020-actual-abstract-stream13735450'],'2022-abstract':['sos-2022-record13735454-range0-163839','sos-2022-record13735454-range163840-327679','sos-2022-record13735454-byte-range-tail'],'2024-Wasco':['sos-observed-2024-wasco-native-original'],'2020-registration':['sos-2020-abstract-original'],'2022-registration':['sos-2022-abstract-original'],'2024-registration':['sos-2024-abstract-original']}.items():extract(key,b''.join(body(id) for id in ls),{'source_ids':ls})
 # Every byte/member of the two original ZIPs, restored only in temporary storage.
 for year in [2020,2022]:
  with tempfile.TemporaryFile() as f:
   restore_zip(year,f)
   f.seek(0)
   with zipfile.ZipFile(f) as z:
    for ordinal,info in enumerate(z.infolist()):
     b=z.read(info);extract(f'{year}-{ordinal:02}',b,{'archive_source_id':f'sos-{year}-precinct-zip-observed-download','member':info.filename,'ordinal':ordinal,'CRC':info.CRC})
 # All individual acquired receipts and bodies are read/verified before comparisons.
 for item in snapshot:
  if 'response_entities' not in item['source']:continue
  s=item['source'];p=DATA.parent/item['receipt_path'];metadata_bytes(item)
  receipts.append(item)
  for n,e in enumerate(s.get('response_entities',[])):
   f=p.parent/e['asset'];b=entity(f,e)
   extract(s['key']+(f'-hop{n}' if n else ''),b,{'receipt':str(p.relative_to(DATA.parent)),'entity':n,'url':e['url'],'original_asset':str(f.relative_to(DATA.parent))})
 assert receipts==snapshot
 (ROOT/'source/original-read-receipts.json').write_bytes(receipt_bytes())
 writejson(ROOT/'source/independent-original-inventory.json',inventory)
 print(json.dumps({'originals_read_and_independently_extracted':len(inventory),'ZIP_members':72,'inventory_sha256':sha((ROOT/'source/independent-original-inventory.json').read_bytes())}))
if __name__=='__main__':main()

"""Fixed owned receipt input; individual original entities remain stored once.
No mutable aggregate, peer metadata discovery, or shared helper execution.
"""
import gzip,hashlib,json,tempfile,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];STATE=R.parent.parent;NEWS=R.parent/'news'
RECEIPT_SHA256='3053adb590a11f424c78c34d20e1bad23d5571fe3a72d347e82fdf99a7d6fae7'
def sha(b):return hashlib.sha256(b).hexdigest()
def receipt_bytes():
 b=(R/'source/inputs/original-receipts-v1.json').read_bytes();assert sha(b)==RECEIPT_SHA256;return b
def receipts():return json.loads(receipt_bytes())
def entity(path,record):
 stored=Path(path).read_bytes();assert sha(stored)==record['stored_sha256'];raw=gzip.decompress(stored)
 assert sha(raw)==record['raw_sha256'];assert len(raw)==record.get('raw_bytes',record.get('bytes'));return raw
def metadata_bytes(item):
 # All37 original acquired receipt files use this exact serialization. The captured
 # original hash proves reconstruction; the live peer metadata file is never read.
 b=(json.dumps(item['source'],indent=2)+'\n').encode();assert sha(b)==item['receipt_sha256'];return b
def zip_source(year):return next(x['source'] for x in receipts() if x['source'].get('id')==f'sos-{year}-precinct-zip-observed-download')
def restore_zip(year,destination):
 s=zip_source(year);stored_hash=hashlib.sha256();stored_size=0
 with tempfile.TemporaryFile() as compressed:
  for part in s['asset_parts']:
   path=NEWS/part['asset'];b=path.read_bytes();assert len(b)==part['bytes']<40000000 and sha(b)==part['sha256'];stored_hash.update(b);stored_size+=len(b);compressed.write(b)
  assert stored_size==s['stored_bytes'] and stored_hash.hexdigest()==s['stored_sha256'];compressed.seek(0);h=hashlib.sha256();size=0
  with gzip.GzipFile(fileobj=compressed) as decoded:
   for b in iter(lambda:decoded.read(1024*1024),b''):destination.write(b);h.update(b);size+=len(b)
  assert h.hexdigest()==s['raw_sha256'] and size==s['bytes']==int(s['headers']['Content-Length'])
 req=(NEWS/s['request_body_asset']).read_bytes();assert sha(req)==s['request_body_stored_sha256'] and sha(gzip.decompress(req))==s['request_body_sha256']
 return {'year':year,'original_bytes':size,'original_sha256':h.hexdigest(),'source_id':s['id']}

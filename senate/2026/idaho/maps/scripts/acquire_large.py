#!/usr/bin/env python3
"""One observed Franklin atlas, complete original entity in lossless <=16MB raw chunks."""
import datetime,gzip,hashlib,json
import requests
from acquire import MAPS

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 error=json.loads((MAPS/'source/additional-16041-map-0-3.transport-error.json').read_text());u=error['requested_url'];p=MAPS/'source/franklin-complete-atlas.receipt.json'
 if p.exists():return
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();r=requests.get(u,timeout=(15,120));b=r.content;assert r.status_code==200 and b.startswith(b'%PDF-');parts=[]
 for start in range(0,len(b),16000000):
  raw=b[start:start+16000000];stored=gzip.compress(raw,mtime=0);h=sha(stored);asset=MAPS/'source'/f'{h}.pdf-part.gz';assert len(stored)<40000000
  if not asset.exists():asset.write_bytes(stored)
  parts.append(dict(offset=start,raw_bytes=len(raw),raw_sha256=sha(raw),stored_path=str(asset.relative_to(MAPS.parent)),stored_bytes=len(stored),stored_sha256=h))
 out=dict(id='franklin-complete-atlas',requested_url=u,final_url=r.url,parent=error['parent'],literal_href=error['literal_href'],constructor=None,method='GET',retrieved_utc=now,status=r.status_code,headers=dict(r.headers),redirects=[dict(url=x.url,status=x.status_code,headers=dict(x.headers)) for x in r.history],body_error=None,raw_bytes=len(b),raw_sha256=sha(b),stored_parts=parts,encoding='Ordered gzip parts, exactly reassemble decompressed original bytes; every stored and reconstructed chunk strictly below40MB',purpose='Complete county-published 2026 precinct map and description atlas; original large PDF split losslessly',source_clock=r.headers.get('Last-Modified'),publication_status='County publication, no historical reporting crosswalk or proof of later changes')
 p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(id=out['id'],original_bytes=len(b),parts=len(parts))))
if __name__=='__main__':main()

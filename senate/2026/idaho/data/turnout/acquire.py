#!/usr/bin/env python3
"""Acquire bounded primary evidence; reused originals are pinned, never copied."""
from pathlib import Path
import datetime,gzip,hashlib,json,requests,sys
D=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
def fetch(sid,url,parent=None):
 p=D/'source'/(sid+'.gz'); ledger=D/'source'/'requests.json'; records=json.loads(ledger.read_text()) if ledger.exists() else []
 r=requests.get(url,timeout=90); b=r.content; stored=gzip.compress(b,mtime=0); assert len(stored)<40000000
 p.write_bytes(stored)
 rec=dict(id=sid,requested_url=url,final_url=r.url,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status=r.status_code,headers=dict(r.headers),redirects=[dict(url=x.url,status=x.status_code,headers=dict(x.headers)) for x in r.history],parent=parent,asset=str(p.relative_to(D)),original_bytes=len(b),original_sha256=H(b),stored_bytes=len(stored),stored_sha256=H(stored))
 records=[x for x in records if x['id']!=sid]+[rec];ledger.write_text(json.dumps(records,indent=2)+'\n'); print(sid,r.status_code,len(b),r.url)
 return b
if __name__=='__main__':fetch(*sys.argv[1:])

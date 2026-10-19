"""Immutable original references, acquisitions and hash verification (no peer edits)."""
from pathlib import Path
import datetime,gzip,hashlib,json,urllib.request
BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'data/baselines'
def sha(b): return hashlib.sha256(b).hexdigest()
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def references():
    records={}
    for m in [BASE/'data/news/manifest.json',BASE/'data/turnout/source/acquisition.json']:
        for r in json.loads(m.read_text()):
            r=dict(r)
            if 'path' not in r:r['path']='data/news/'+r['asset']
            r['reference_manifest']=str(m.relative_to(BASE))
            records[r['id']]=r
    own=OUT/'source/downloads.json'
    if own.exists():records.update({r['id']:r for r in json.loads(own.read_text())})
    shared=OUT/'source/shared-primary-references.json'
    if shared.exists():records.update({r['id']:r for r in json.loads(shared.read_text())})
    return records
def original(key):
    r=references()[key];stored=(BASE/r['path']).read_bytes()
    assert sha(stored)==r['stored_sha256'],key
    raw=gzip.decompress(stored) if r['path'].endswith('.gz') else stored
    assert sha(raw)==r['raw_sha256'],key
    return raw
def acquire(key,url,parent):
    dest=OUT/'source/downloads.json';a=json.loads(dest.read_text()) if dest.exists() else []
    if any(r['id']==key for r in a):return
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    req=urllib.request.Request(url,headers={'User-Agent':'Historical election research; public source preservation'})
    with urllib.request.urlopen(req,timeout=90) as response:
        raw=response.read();headers=dict(response.headers);final=response.url;status=response.status
    stored=gzip.compress(raw,mtime=0);p=OUT/'source'/(key+'.body.gz');p.write_bytes(stored)
    assert len(stored)<40000000
    a.append(dict(id=key,url=url,final_url=final,status=status,headers=headers,retrieved_at_utc=start,
                  raw_sha256=sha(raw),raw_bytes=len(raw),stored_sha256=sha(stored),stored_bytes=len(stored),
                  path=str(p.relative_to(BASE)),parent_source_id=parent,storage='owned_lossless_gzip'))
    save(dest,a)
def pin():
    rows=[]
    for r in references().values():
        if r['id'].startswith(('sos-','eac-','fec-','house-','clerk-','hb859-','court-')):
            raw=original(r['id']);r=dict(r);r['verified_original_bytes']=len(raw)
            r['verified_stored_bytes']=(BASE/r['path']).stat().st_size;rows.append(r)
    save(OUT/'source/references.json',rows)
    return rows
if __name__=='__main__':
    acquire('sos-yall-vote-current','https://www.sos.ms.gov/yall-vote',None)
    acquire('sos-2026-sample-ballot','https://sos.ms.gov/content/documents/Elections/2026/Sample%20Ballot%209-9-26.pdf','web-search-discovery; official SOS host')
    pin()

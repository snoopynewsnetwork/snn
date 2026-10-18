"""Acquire bounded primary authority evidence; reuse original news assets read-only.
No peer extraction code is imported. Existing captures are immutable unless --refresh.
"""
from pathlib import Path
import argparse,datetime,gzip,hashlib,json,urllib.request,urllib.error,html,re
H=Path(__file__).resolve().parent; S=H/'source'; N=H.parent/'news'
def sha(b): return hashlib.sha256(b).hexdigest()
def fetch(sid,url,parent=None,data=None):
    req=urllib.request.Request(url,data=data,headers={'User-Agent':'Mozilla/5.0 (historical election research)'})
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try: r=urllib.request.urlopen(req,timeout=45)
    except urllib.error.HTTPError as e:r=e
    b=r.read(); final=r.geturl();headers=dict(r.headers.items()); status=r.status
    p=S/(sid+'.body.gz');p.write_bytes(gzip.compress(b,mtime=0))
    return dict(id=sid,requested_url=url,final_url=final,parent_url=parent,retrieved_utc=now,status=status,headers=headers,redirect_observed=final!=url,redirect_chain_scope='urllib final URL only; intermediate response headers unavailable',raw_bytes=len(b),raw_sha256=sha(b),stored_path=str(p.relative_to(H)),stored_bytes=p.stat().st_size,stored_sha256=sha(p.read_bytes()),content_kind='bot_challenge' if any(t in b.lower() for t in [b'validate.perfdrive.com/?',b'<title>radware',b'captcha']) and b'Precinct' not in b and b'Candidate Filings' not in b else 'inspect_content')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--refresh',action='store_true');args=ap.parse_args();S.mkdir(exist_ok=True)
    old={r['id']:r for r in json.loads((S/'acquisition.json').read_text())} if (S/'acquisition.json').exists() else {}
    urls=[('results-2024','https://www.sos.mn.gov/elections-voting/election-results/2024/2024-general-election-results/'),('results-2022','https://sos.mn.gov/elections-voting/election-results/2022/2022-general-election-results/'),('results-2020','https://www.sos.mn.gov/elections-voting/election-results/2020/2020-general-election-results/'),('class-II','https://www.senate.gov/senators/Class_II.htm'),('class-I','https://www.senate.gov/states/MN/senators.htm'),('plurality','https://www.revisor.mn.gov/statutes/cite/204C.33'),('tie-rule','https://www.revisor.mn.gov/statutes/cite/204C.34'),('candidates-2026','https://candidates.sos.mn.gov/'),('independence-general-2026','https://www.ci.independence.mn.us/government/elections'),('delano-general-ballot-2026','https://www.ci.independence.mn.us/2026%20General%20Election_%20Delano%20Sample%20Ballot.pdf'),('westonka-general-ballot-2026','https://www.ci.independence.mn.us/2026%20General%20Election_%20Westonka%20Sample%20Ballot.pdf'),('candidate-file-layout','https://candidates.sos.mn.gov/Media/MediaFileFormat.txt')]
    for sid,u in urls:
        if sid not in old or args.refresh:
            try:old[sid]=fetch(sid,u)
            except Exception as e:old[sid]=dict(id=sid,requested_url=u,error=repr(e))
    (S/'acquisition.json').write_text(json.dumps(list(old.values()),indent=2)+'\n')
    refs=[]
    manifest=json.loads((N/'manifest.json').read_text())
    for r in manifest:
        if r['id'].startswith('sos-20') and r['id']!='sos-2026-absentee':
            p=N/r['asset'];b=p.read_bytes();assert sha(b)==r['stored_sha256'];raw=gzip.decompress(b);assert sha(raw)==r['raw_sha256'] and len(raw)==r['bytes']
            refs.append(dict(**r,reference_path=str(Path('../news')/r['asset']),reuse='read-only original; no duplicate',parent_manifest='../news/manifest.json'))
    (S/'shared-originals.json').write_text(json.dumps(refs,indent=2)+'\n')
    print(json.dumps([{k:r.get(k) for k in ['id','status','raw_bytes','content_kind']} for r in old.values()],indent=2))

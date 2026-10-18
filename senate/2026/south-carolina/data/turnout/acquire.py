"""Immutable read-only HTTP acquisition. Reuse identical shared originals by hash.

python3 acquire.py get ID URL PARENT
python3 acquire.py history
Saved .body.gz contains the complete decoded HTTP entity, not wire compression.
"""
import datetime, gzip, hashlib, json, os, re, sys
from pathlib import Path
import requests
from urllib.parse import urlencode

H=Path(__file__).resolve().parent
S=H/'source'; S.mkdir(parents=True,exist_ok=True)
D=H.parent
def sha(b): return hashlib.sha256(b).hexdigest()
def shared_index():
    out={}
    for m in json.loads((D/'news/manifest.json').read_text()):
        p=D/'news'/m['asset']
        if p.exists(): out[m['raw_sha256']]=(p,m.get('stored_sha256'),m['url'],'gzip')
    for p in (D/'history-api').glob('*.meta.json'):
        m=json.loads(p.read_text())
        if m.get('original_sha256'):out[m['original_sha256']]=(p.parent/m['body_file'],m['stored_sha256'],m['url'],'gzip')
    other=D.parent.parent/'ohio/data/baselines/raw'
    for name in ['house-2024.pdf','house-2022.pdf']:
        p=other/name
        if p.exists():out[sha(p.read_bytes())]=(p,sha(p.read_bytes()),None,'identity')
    other=D.parent.parent/'new-hampshire/data/turnout/source'
    p=other/'house-clerk-2020.body.gz'
    if p.exists():out[sha(gzip.decompress(p.read_bytes()))]=(p,sha(p.read_bytes()),None,'gzip')
    for p in (D/'baselines/source').glob('*.meta.json'):
        m=json.loads(p.read_text())
        if m.get('original_sha256')and m.get('body_path'):
            q=(p.parent/m['body_path']).resolve()
            if q.exists():out[m['original_sha256']]=(q,m['stored_sha256'],m.get('requested_url'),m.get('stored_encoding','gzip'))
    return out
def capture(sid,url,parent,request=None):
    dest=S/(sid+'.meta.json')
    if dest.exists(): return json.loads(dest.read_text())
    headers={'User-Agent':'South-Carolina historical election research; public read-only acquisition'}
    if request is not None:
        headers.update({'Content-Type':'application/json','X-Elstats-Tenant':'sc'})
        req=json.dumps(request).encode();(S/(sid+'.request.json')).write_bytes(req)
    else:req=None
    m={'id':sid,'requested_url':url,'parent_source':parent,'method':'POST' if req else 'GET',
       'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request_headers':headers}
    if req:m.update(request_file=sid+'.request.json',request_sha256=sha(req))
    try:r=requests.request(m['method'],url,data=req,headers=headers,timeout=50)
    except requests.RequestException as e:
        m.update(transport_error=str(e),http_status=None,body_path=None)
        dest.write_text(json.dumps(m,indent=2)+'\n');return m
    b=r.content; m.update(final_url=r.url,http_status=r.status_code,response_headers=dict(r.headers),
       redirects=[{'url':x.url,'status':x.status_code,'headers':dict(x.headers)}for x in r.history],
       original_bytes=len(b),original_sha256=sha(b),body_encoding='complete decoded HTTP entity; lossless gzip storage')
    shared=shared_index().get(sha(b))
    if shared:
        p,expected,_,encoding=shared; stored=p.read_bytes();assert sha(stored)==expected
        assert (gzip.decompress(stored)if encoding=='gzip'else stored)==b
        m.update(body_path=os.path.relpath(p,S),storage='read-only shared exact-byte reference',stored_encoding=encoding)
    else:
        stored=gzip.compress(b,mtime=0);p=S/(sid+'.body.gz');p.write_bytes(stored)
        m.update(body_path=p.name,storage='owned lossless gzip',stored_encoding='gzip')
    assert len(stored)<40_000_000
    m.update(stored_bytes=len(stored),stored_sha256=sha(stored))
    dest.write_text(json.dumps(m,indent=2)+'\n')
    return m
def body(sid):
    m=json.loads((S/(sid+'.meta.json')).read_text());b=(S/m['body_path']).read_bytes()
    assert sha(b)==m['stored_sha256'];raw=gzip.decompress(b)if m.get('stored_encoding','gzip')=='gzip'else b
    assert sha(raw)==m['original_sha256'];return raw
def app(sid):
    m=next(x for x in json.loads((D/'news/manifest.json').read_text())if x['id']==sid)
    p=D/'news'/m['asset'];b=gzip.decompress(p.read_bytes());assert sha(b)==m['raw_sha256'];return b.decode()
def history():
    # Independently recover query bodies from the retained actual source application.
    q=next(q for q in re.findall(r'\.gql`(.*?)`',app('sos-history-contest-script-27'),re.S)if 'query GetContestGranular(' in q)
    fr=[q for q in re.findall(r'\.gql`(.*?)`',app('sos-history-contest-script-23'),re.S)if any('fragment '+x+' 'in q for x in ['CoreContest','CandidateContestWithParties','granularDivision'])]
    query=re.sub(r'\$\{[^}]+\}','',q+'\n'+'\n'.join(fr))
    for cid,label in [(7131,'2024-pres'),(1975,'2020-senate'),(2321,'2022-senate'),(2183,'2022-governor')]:
        for channel in [False,True]:
            sid=label+'-'+('methods'if channel else'combined')
            req={'operationName':'GetContestGranular','query':query,'variables':{'contestId':cid,'divisionFilter':None,'voteChannelFilter':None,'voteChannels':channel,'singleVoteChannel':None,'splitParty':False}}
            m=capture(sid,'https://electionhistory.scvotes.gov/api/graphql_pr',f'https://electionhistory.scvotes.gov/contest/{cid}; actual scripts sos-history-contest-script-27/-23 in ../news/manifest.json',req)
            d=json.loads(body(sid));assert not d.get('errors');print(sid,m['http_status'],m['original_sha256'],m['storage'],flush=True)
def vhm():
    for year in [2024,2022,2020]:
        counties=json.loads(body(f'vhm-{year}-VOT-county'))['voterHistoryResults']['countyPrecinctResults']
        for i,r in enumerate(counties):
            if r['isSummary'] or r['county'] is None:continue
            sid=f'vhm-{year}-VOT-precinct-{r["county"].lower()}'
            url='https://vrems.scvotes.sc.gov/Statistics/GetVoterHistoryResultsByPrecinct?'+urlencode({'dataType':'VOT','year':year,'electionType':'GEN','county':r['county']})
            m=capture(sid,url,f'voter-history-js GetVoterHistoryByPrecinct; county row {i} in vhm-{year}-VOT-county')
            d=json.loads(body(sid));assert d.get('voterHistoryResults'),sid
            print(sid,m['http_status'],len(d['voterHistoryResults']['countyPrecinctResults']),flush=True)
if __name__=='__main__':
    if sys.argv[1]=='history': history()
    elif sys.argv[1]=='vhm':vhm()
    elif sys.argv[1]=='get':
        m=capture(*sys.argv[2:5]);print(m['id'],m['http_status'],m['original_bytes'],m['original_sha256'])

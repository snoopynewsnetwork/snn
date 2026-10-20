"""Explicit one-time receipt snapshot, and bounded literal-link acquisition.
Usage: python3 -B acquire.py snapshot | fetch ID URL [PARENT_ID] | towns YEAR
No build reads the mutable shared news manifest. No guessed election paths.
"""
import sys, urllib.request, urllib.error, urllib.parse, datetime, json, gzip
from common import *
def snapshot():
    news=STATE/'data/news'; src=json.loads((news/'manifest.json').read_text());out=[]
    for r in src:
        if not r['id'].startswith(('ri-2024-','ri-2020-','ri-2022-','boe-')):continue
        r=dict(r);p=news/r['asset'];b=p.read_bytes();raw=gzip.decompress(b)
        assert sha(raw)==r['raw_sha256'] and sha(b)==r['stored_sha256']
        r.update(stored_path=str(p.relative_to(STATE)),compression='gzip',stored_bytes=len(b),raw_bytes=len(raw))
        r['stored_path']='../../'+r['stored_path']
        out.append(r)
    dump(ROOT/'source/inputs/original-receipts.json',out)
def fetch(key,url,parent=None):
    target=ROOT/'source/acquired';target.mkdir(parents=True,exist_ok=True)
    receipt=target/(key+'.receipt.json')
    if receipt.exists():
        old=json.loads(receipt.read_text())
        if not old.get('error'):return old
        failures=target/'failures';failures.mkdir(exist_ok=True)
        receipt.rename(failures/(key+'.'+sha(receipt.read_bytes())[:12]+'.receipt.json'))
    hops=[]; current=url
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):return None
    opener=urllib.request.build_opener(NoRedirect)
    for _ in range(10):
        now=datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:r=opener.open(urllib.request.Request(current,headers={'User-Agent':'Public election research; source retention','Accept-Encoding':'identity'}),timeout=50)
        except urllib.error.HTTPError as e:r=e
        except Exception as e:
            dump(receipt,dict(id=key,url=url,parent_id=parent,hops=hops,error=repr(e)));return
        b=r.read();packed=gzip.compress(b,mtime=0);name=sha(b)+'.body.gz';p=target/name
        if not p.exists():p.write_bytes(packed)
        h=dict(requested_url=current,final_url=r.geturl(),status=r.code,headers=list(r.headers.items()),retrieved_at_utc=now,raw_sha256=sha(b),raw_bytes=len(b),stored_path=str(p.relative_to(ROOT)),stored_sha256=sha(p.read_bytes()),stored_bytes=p.stat().st_size,compression='gzip')
        hops.append(h)
        if r.code in [301,302,303,307,308] and r.headers.get('Location'):current=urllib.parse.urljoin(current,r.headers['Location']);continue
        break
    result=dict(id=key,url=url,parent_id=parent,hops=hops,**{k:v for k,v in hops[-1].items() if k!='requested_url'})
    dump(receipt,result);return result
def allreceipts():
    return inputs()+[json.loads(p.read_text()) for p in sorted((ROOT/'source/acquired').glob('*.receipt.json'))]
if __name__=='__main__':
    if sys.argv[1]=='snapshot':snapshot()
    elif sys.argv[1]=='fetch':fetch(*sys.argv[2:])
    elif sys.argv[1]=='towns':
        year=sys.argv[2]; rs=inputs(); seed=next(r for r in rs if r['id']=={'2024':'ri-2024-general-old-authority','2020':'ri-2020-observed-state-summary','2022':'ri-2022-observed-historical-seed'}[year])
        ls=links(original(seed)); selected=[(n,urllib.parse.urljoin(seed['url'],u)) for n,u in ls if u.startswith('/election/results/'+year+'/general_election/') and u.endswith('/') and n not in ['Statewide summary','State Senator','State Representative','Data files']]
        assert len(selected)==39
        for n,u in selected:fetch(year+'-town-'+u.rstrip('/').split('/')[-1],u,seed['id'])

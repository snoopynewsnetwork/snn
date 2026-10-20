"""Public original acquisition, one explicit URL per invocation; never overwrites receipts."""
import datetime,gzip,json,sys,urllib.request,urllib.error
from common import *
def fetch(name,url,parent=None):
    p=BASE/'source/acquired';p.mkdir(exist_ok=True)
    dest=p/(name+'.receipt.json')
    if dest.exists(): raise ValueError('Receipt exists; use a new observation name')
    hops=[]
    class Redirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,req,fp,code,msg,headers,newurl):
            hops.append({'url':req.full_url,'status':code,'headers':list(headers.items()),'location':newurl})
            return super().redirect_request(req,fp,code,msg,headers,newurl)
    receipt={'id':name,'requested_url':url,'parent':parent,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'redirects':hops}
    try:
        try:r=urllib.request.build_opener(Redirect).open(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (public election research)'}),timeout=40)
        except urllib.error.HTTPError as e:r=e
        b=r.read();s=gzip.compress(b,mtime=0);target=p/(sha(b)+'.body.gz')
        if not target.exists():target.write_bytes(s)
        receipt.update(final_url=r.geturl(),status=r.status,headers=list(r.headers.items()),raw_sha256=sha(b),raw_bytes=len(b),
            stored_path=str(target.relative_to(BASE)),stored_sha256=sha(target.read_bytes()),stored_bytes=target.stat().st_size,compression='gzip')
    except Exception as e:receipt['error']=repr(e)
    dest.write_text(json.dumps(receipt,indent=2)+'\n');print(name,receipt.get('status'),receipt.get('raw_bytes'),receipt.get('error'))
if __name__=='__main__':fetch(*sys.argv[1:])

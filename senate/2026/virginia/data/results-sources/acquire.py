"""Explicit public GET/directory-selector POST; complete immutable entities.

No discovery, login, personal input, messages or collector. Each call is an observation.
"""
import argparse, datetime, gzip, hashlib, json, urllib.request, urllib.error, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def digest(b): return hashlib.sha256(b).hexdigest()
def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def store(b):
    sha=digest(b); packed=gzip.compress(b, mtime=0)
    if len(packed)>=40000000: raise ValueError('complete entity needs explicit byte parts')
    p=ROOT/'bodies'/ (sha+'.gz'); p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists(): assert gzip.decompress(p.read_bytes())==b
    else: p.write_bytes(packed)
    return {'path':str(p.relative_to(ROOT)), 'raw_bytes':len(b), 'raw_sha256':sha,
            'stored_bytes':len(packed), 'stored_sha256':digest(packed), 'storage':'complete lossless gzip; mtime=0'}
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): return None
def forbidden(url):
    p=urllib.parse.urlsplit(url)
    return p.scheme not in ('https','http') or any(w in p.path.lower().split('/') for w in ('login','signin','account','admin','challenge','captcha','authenticate'))
def fetch(key,url,parent,timeout=35,submitted_fields=None):
    receipt=ROOT/'requests'/(key+'.json')
    if receipt.exists(): raise FileExistsError(receipt)
    headers={'User-Agent':'Virginia-official-source-research/1.0 (bounded public GET)', 'Accept-Encoding':'identity'}
    data=urllib.parse.urlencode(submitted_fields).encode() if submitted_fields is not None else None
    method='POST' if data is not None else 'GET'
    if data is not None:headers['Content-Type']='application/x-www-form-urlencoded'
    r={'key':key,'requested_url':url,'public_parent_edge':parent,'request_method':method,
       'submitted_fields':submitted_fields,'submitted_body':data.decode() if data is not None else None,'request_headers':headers,'started_at_utc':now(),'hops':[],
       'transport_scope':'complete HTTP entities after transfer framing; no network wire capture',
       'publisher_clock':None,'publisher_timezone':None}
    opener=urllib.request.build_opener(NoRedirect())
    for _ in range(8):
        if forbidden(url): r['stopped_reason']='irrelevant or security/account URL';break
        stamp=now()
        try:
            try: response=opener.open(urllib.request.Request(url,data=data,headers=headers,method=method), timeout=timeout)
            except urllib.error.HTTPError as e: response=e
            with response:
                b=response.read(); status=response.status; h=list(response.headers.items()); final=response.geturl()
            hop={'actual_requested_url':url,'response_url':final,'request_method':method,'request_headers':dict(headers),
                 'submitted_body':data.decode() if data is not None else None,'retrieved_at_utc':stamp,'completed_at_utc':now(),
                 'status':status,'response_headers':h,'body':store(b)}
            r['hops'].append(hop);r['final_url']=final;r['final_status']=status
            if status in (301,302,303,307,308):
                location=next((v for k,v in h if k.lower()=='location'),None)
                if not location:break
                url=urllib.parse.urljoin(final,location);hop['redirect_target']=url
                if status in (301,302,303):method='GET';data=None;headers.pop('Content-Type',None)
                continue
            break
        except Exception as e:
            r['failure']={'utc':now(),'url':url,'type':type(e).__name__,'message':str(e),'response_headers':None,'body':None}
            break
    else:r['stopped_reason']='redirect bound reached'
    r['completed_at_utc']=now();dump(receipt,r)
    return r
def body(key):
    r=json.loads((ROOT/'requests'/(key+'.json')).read_bytes())
    return gzip.decompress((ROOT/r['hops'][-1]['body']['path']).read_bytes()) if r['hops'] else b''
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('key');p.add_argument('url');p.add_argument('parent');a=p.parse_args()
    r=fetch(a.key,a.url,a.parent);print(json.dumps({k:r.get(k) for k in ['key','final_status','final_url','failure','stopped_reason']}))

"""Bounded public-source acquisition. No accounts, guessed identifiers or polling."""
from pathlib import Path
import datetime,gzip,hashlib,json,sys,urllib.request,urllib.error,urllib.parse,http.cookiejar,re
from html.parser import HTMLParser

HERE=Path(__file__).resolve().parent
STATE=HERE.parents[1]
LIMIT=40000000
PUBLIC_COOKIES=http.cookiejar.CookieJar()
def sha(b): return hashlib.sha256(b).hexdigest()
def decode_html(b):
    m=re.search(br'charset\s*=\s*["\x27]?([A-Za-z0-9_-]+)',b[:6000],re.I)
    enc='utf-8-sig' if b.startswith(b'\xef\xbb\xbf') else m.group(1).decode() if m else 'utf-8'
    try:return b.decode(enc)
    except (UnicodeDecodeError,LookupError):return b.decode('utf-8',errors='replace')
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def store(b):
    z=gzip.compress(b,mtime=0); h=sha(b)
    if len(z)>=LIMIT: raise ValueError('needs ordered exact-byte splits; not stored or truncated')
    p=HERE/'originals'/f'{h}.gz';p.parent.mkdir(exist_ok=True)
    if not p.exists():p.write_bytes(z)
    return dict(path=str(p.relative_to(STATE)),bytes=len(z),sha256=sha(z),raw_bytes=len(b),raw_sha256=h,compression='gzip')
class Redirects(urllib.request.HTTPRedirectHandler):
    def __init__(self):self.rows=[]
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        b=fp.read()
        self.rows.append(dict(url=req.full_url,request_method=req.get_method(),request_headers=list(req.header_items()),status=code,reason=msg,headers=list(headers.items()),body=store(b),location=newurl))
        return super().redirect_request(req,fp,code,msg,headers,newurl)
class Page(HTMLParser):
    def __init__(self,b,url):
        super().__init__(convert_charrefs=True);self.url=url;self.links=[];self.text=[];self.active=None;self.scripts=[];self.special=[]
        self.feed(decode_html(b));self.close()
    def handle_starttag(self,t,a):
        d=dict(a)
        if t=='a':self.active=dict(href=d.get('href'),label='',attributes=a,position=self.getpos())
        if t in ('script','iframe','form','input','select','option'):
            self.special.append(dict(tag=t,attributes=a,position=self.getpos()))
        if t=='script' and d.get('src'):self.scripts.append(urllib.parse.urljoin(self.url,d['src']))
    def handle_endtag(self,t):
        if t=='a' and self.active:
            self.active['label']=' '.join(self.active['label'].split())
            h=self.active['href'];self.active['url']=urllib.parse.urljoin(self.url,h) if h else None
            self.links.append(self.active);self.active=None
    def handle_data(self,d):
        self.text.append(d)
        if self.active:self.active['label']+=d
def fetch(name,url,parent=None,basis=None,refresh=False,method='GET',data=None):
    path=HERE/'receipts'/f'{name}.json'
    if path.exists() and not refresh:return json.loads(path.read_bytes())
    now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
    wire_url=urllib.parse.quote(url,safe=":/?&=%#@!$'()*+,;~-._")
    headers={'User-Agent':'Public election source research; bounded original retention','Accept-Encoding':'identity'}
    if data is not None:headers['Content-Type']='application/x-www-form-urlencoded'
    req=urllib.request.Request(wire_url,data=data,method=method,headers=headers)
    red=Redirects();opener=urllib.request.build_opener(red,urllib.request.HTTPCookieProcessor(PUBLIC_COOKIES))
    r=dict(id=name,requested_url=url,wire_url=wire_url,parent=parent,discovery_basis=basis,observation_started_utc=now(),request_method=method,request_headers=dict(req.header_items()),request_body=store(data) if data is not None else None,redirects=[],publisher_time=None,publisher_timezone=None,current_count_admitted=False,current_change_admitted=False)
    try:
        try:response=opener.open(req,timeout=35)
        except urllib.error.HTTPError as e:response=e
        b=response.read();r.update(status=response.code,reason=response.reason,final_url=response.geturl(),response_headers=list(response.headers.items()),request_headers=dict(req.header_items()),body=store(b),error=None)
        decoded=b
        if response.headers.get('Content-Encoding','').lower()=='gzip':decoded=gzip.decompress(b)
        r['decoded_body']=store(decoded) if decoded!=b else r['body']
        ct=response.headers.get('Content-Type','')
        if 'html' in ct or decoded.lstrip()[:15].lower().startswith((b'<!doctype html',b'<html')):
            p=Page(decoded,r['final_url']);dump(HERE/'pages'/f'{name}.json',dict(url=r['final_url'],body=r['decoded_body'],links=p.links,scripts=p.scripts,constructors=p.special,text=' '.join(' '.join(p.text).split())))
    except Exception as e:r.update(status=None,error=type(e).__name__+': '+str(e))
    r['redirects']=red.rows;r['observation_finished_utc']=now();dump(path,r)
    print(name,r.get('status'),r.get('body',{}).get('raw_bytes'),r.get('error'),flush=True)
    return r
def page(name):return json.loads((HERE/'pages'/f'{name}.json').read_bytes())
def body(r):
    v=r.get('decoded_body',r['body']);b=(STATE/v['path']).read_bytes();assert sha(b)==v['sha256'];raw=gzip.decompress(b);assert sha(raw)==v['raw_sha256'];return raw
if __name__=='__main__':
    name,url=sys.argv[1:3];fetch(name,url,basis='literal public URL provided/observed in primary research')

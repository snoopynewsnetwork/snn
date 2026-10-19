"""One-shot public GET evidence acquisition. No collector or guessed result IDs.

python3 -B acquire.py jobs.json
jobs: [{id,url,parent?,relation?,scope?}]. Existing receipt IDs are immutable.
Wire entities (including HTTP errors) are preserved losslessly; parsed content is
decoded only after retaining the entity. Large compressed entities use ordered
32,000,000-byte parts. Never use --insecure or discard an error response.
"""
from pathlib import Path
import concurrent.futures, datetime, gzip, hashlib, json, sys, threading
import urllib.request, urllib.error, zlib, subprocess, tempfile
from html.parser import HTMLParser
from urllib.parse import urljoin, quote

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
LOCK = threading.Lock()
def sha(b): return hashlib.sha256(b).hexdigest()
def save(p, x): p.write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n')
def pin(p):
    b=p.read_bytes(); return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))

def shared_index():
    result={}
    for name in ['data/news/manifest.json','data/turnout/source/acquisition.json',
                 'data/baselines/source/references.json',
                 'data/coordinator-legal-preparation/source-ledger.json',
                 'data/coordinator-legal-preparation/supplemental-source-ledger.json']:
        p=ROOT/name
        if not p.exists(): continue
        rows=json.loads(p.read_bytes())
        if isinstance(rows,dict): rows=rows.get('observations',rows.get('sources',rows.get('records',[])))
        for r in rows:
            if isinstance(r.get('body'),dict): r=dict(r,**r['body'])
            path=r.get('path') or r.get('stored_path') or ('data/news/'+r['asset'] if 'asset' in r else None)
            if path and path.startswith('senate/2026/mississippi/'):path=path[len('senate/2026/mississippi/'):]
            if path and r.get('raw_sha256'):
                result.setdefault(r['raw_sha256'],dict(path=path,stored_sha256=r.get('stored_sha256'),reference_manifest=name))
    return result

SHARED=shared_index()
class Redirects(urllib.request.HTTPRedirectHandler):
    def __init__(self): self.history=[]
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.history.append(dict(url=req.full_url,status=code,headers=list(headers.items()),location=newurl))
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def fetch(job):
    receipts=OUT/'receipts'; receipts.mkdir(exist_ok=True)
    p=receipts/(job['id']+'.json')
    if p.exists():
        r=json.loads(p.read_bytes()); assert r['requested_url']==job['url']; return r
    row=dict(id=job['id'],requested_url=job['url'],parent=job.get('parent'),
             relation=job.get('relation'),scope=job.get('scope'),
             method=job.get('method','GET'),request_headers={'User-Agent':'Mozilla/5.0 (public election research)','Accept-Encoding':'identity'},
             started_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    row['request_headers']['Accept-Encoding']=job.get('request_accept_encoding','identity')
    rh=Redirects(); opener=urllib.request.build_opener(rh)
    try:
        row['encoded_request_url']=quote(job['url'],safe=':/?&=%+#@;,!$()*[]')
        data=None
        if row['method']=='POST':
            data=json.dumps(job['json'],separators=(',',':')).encode();row['request_json']=job['json'];row['request_entity_sha256']=sha(data);row['request_headers']['Content-Type']='application/json; charset=utf-8'
        if job.get('transport')=='system_curl_default_certificate_verification':
            assert data is None
            with tempfile.TemporaryDirectory(dir=OUT) as td:
                ep=Path(td)/'entity';hp=Path(td)/'headers'
                cp=subprocess.run(['/usr/bin/curl','--location','--max-time','45','--silent','--show-error','--user-agent',row['request_headers']['User-Agent'],'--header','Accept-Encoding: identity','--dump-header',str(hp),'--output',str(ep),'--write-out','%{json}',row['encoded_request_url']],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                row.update(transport=job['transport'],curl_exit=cp.returncode,curl_stderr=cp.stderr.decode('utf8','replace'))
                row['raw_response_headers']=hp.read_text() if hp.exists() else ''
                meta=json.loads(cp.stdout);row['curl_metadata']=meta
                entity=ep.read_bytes() if ep.exists() else b''
                headerblocks=[h for h in row['raw_response_headers'].split('\n\n') if h.strip()]
                blocks=[]
                for h in headerblocks:
                    lines=h.splitlines();hs=[]
                    for line in lines[1:]:
                        if ':'in line:k,v=line.split(':',1);hs.append((k,v.strip()))
                    blocks.append(dict(status_line=lines[0],headers=hs))
                row.update(status=meta['http_code'],final_url=meta['url_effective'],headers=blocks[-1]['headers'] if blocks else [],redirects=blocks[:-1],entity_bytes=len(entity),entity_sha256=sha(entity),entity_complete=cp.returncode==0)
                if cp.returncode:raise RuntimeError('curl transport failed; see full stderr/metadata')
        else:
            try: response=opener.open(urllib.request.Request(row['encoded_request_url'],headers=row['request_headers'],data=data,method=row['method']),timeout=job.get('timeout',20))
            except urllib.error.HTTPError as e: response=e
            with response:
                entity=response.read()
                row.update(status=response.status,final_url=response.url,headers=list(response.headers.items()),
                           redirects=rh.history,entity_bytes=len(entity),entity_sha256=sha(entity),entity_complete=True)
        encoding=next((v for k,v in row['headers'] if k.lower()=='content-encoding'),'identity')
        row['content_encoding']=encoding
        raw=decode(entity,encoding)
        if raw is not None: row.update(raw_bytes=len(raw),raw_sha256=sha(raw))
        # Reuse only exact entities, never an independently transcribed derivative.
        shared=SHARED.get(sha(entity))
        with LOCK:
            dest=OUT/'entities'; dest.mkdir(exist_ok=True)
            if shared:
                sp=ROOT/shared['path']; sb=sp.read_bytes()
                assert sha(sb)==shared['stored_sha256']
                assert (gzip.decompress(sb) if sp.suffix=='.gz' else sb)==entity
                row.update(storage='external_exact_original_read_only',**shared,stored_bytes=len(sb))
            else:
                stored=gzip.compress(entity,mtime=0)
                ep=dest/(sha(entity)+'.gz')
                if len(stored)<40_000_000:
                    if not ep.exists(): ep.write_bytes(stored)
                    row.update(storage='lossless_gzip_wire_entity',**pin(ep))
                    row['stored_bytes']=row.pop('bytes');row['stored_sha256']=row.pop('sha256')
                else:
                    parts=[]
                    for i,j in enumerate(range(0,len(stored),32_000_000)):
                        pp=dest/(sha(entity)+'.gz.part%04d'%i); pp.write_bytes(stored[j:j+32_000_000]);parts.append(pin(pp))
                    row.update(storage='ordered_parts_of_lossless_gzip_wire_entity',parts=parts,
                               stored_bytes=len(stored),stored_sha256=sha(stored),reconstruction='concatenate parts in listed order, verify stored hash, gzip.decompress, verify entity hash')
    except Exception as e:
        row.update(error_type=type(e).__name__,error=str(e),redirects=rh.history)
        if 'status' not in row: row['status']=None
    row['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    save(p,row); return row

def entity(row):
    if 'parts' in row: b=b''.join((ROOT[p['path']]).read_bytes() for p in row['parts'])
    else: b=(ROOT/row['path']).read_bytes()
    assert sha(b)==row['stored_sha256']
    b=gzip.decompress(b) if row.get('storage')!='uncompressed' else b
    assert sha(b)==row['entity_sha256']
    return b
def body(row):
    return decode(entity(row),row.get('content_encoding','identity'))
def decode(b,encoding):
    e=encoding.lower()
    if e=='gzip':return gzip.decompress(b)
    if e=='deflate':return zlib.decompress(b)
    if e=='br':return subprocess.run(['node','-e',"process.stdout.write(require('zlib').brotliDecompressSync(require('fs').readFileSync(0)))"],input=b,stdout=subprocess.PIPE,check=True).stdout
    if e in ['identity','']:return b
    raise ValueError('Unsupported content encoding '+e)
class Parser(HTMLParser):
    def __init__(self,url): super().__init__(convert_charrefs=True); self.base=url;self.links=[];self.anchor=None;self.text=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='base' and a.get('href'):self.base=urljoin(self.base,a['href'])
        for attr in (['href'] if tag=='a' else ['src'] if tag in ['iframe','script','frame','embed'] else ['action'] if tag=='form' else []):
            if a.get(attr):
                x=dict(tag=tag,attribute=attr,literal=a[attr],text='',attributes=attrs);self.links.append(x)
                if tag=='a':self.anchor=x
    def handle_data(self,d):
        self.text.append(d)
        if self.anchor is not None:self.anchor['text']+=d
    def handle_endtag(self,t):
        if t=='a':self.anchor=None
    def result(self):
        return [dict(x,url=urljoin(self.base,x['literal'])) for x in self.links]
def links(row):
    p=Parser(row['final_url']); p.feed(body(row).decode('utf-8','replace')); return p.result()
def acquire(jobs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for r in pool.map(fetch,jobs): print(r['id'],r.get('status'),r.get('raw_bytes'),r.get('error_type',''),flush=True)
    rows=[json.loads(p.read_bytes()) for p in sorted((OUT/'receipts').glob('*.json'))]
    save(OUT/'source-ledger.json',rows)
    return {r['id']:r for r in rows}
if __name__=='__main__': acquire(json.loads(Path(sys.argv[1]).read_bytes()))

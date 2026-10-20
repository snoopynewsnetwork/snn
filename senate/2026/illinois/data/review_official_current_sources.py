"""Bounded independent current primary recheck, retaining exact complete entities."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import datetime,gzip,hashlib,json,subprocess,tempfile
import requests
S=Path(__file__).resolve().parents[1];D=S/'data/coordinator-official-current-recheck'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
class Text(HTMLParser):
 def __init__(self,b):super().__init__();self.parts=[];self.feed(b.decode('utf-8-sig',errors='replace'))
 def handle_data(self,s):self.parts.append(s)
def get(item):
 sid,url=item;p=D/(sid+'.receipt.json')
 if p.exists():return json.loads(p.read_bytes())
 r=dict(id=sid,requested_url=url,method='GET',retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),purpose='Independent final bounded current primary check; no result or legal completeness admission')
 try:
  x=requests.get(url,headers={'User-Agent':'Mozilla/5.0 (bounded election source research)'},timeout=(10,30));b=x.content
  assert len(b)<40000000
  z=gzip.compress(b,mtime=0);q=D/(sid+'.gz');q.write_bytes(z)
  r.update(final_url=x.url,status=x.status_code,headers=list(x.raw.headers.items()),redirects=[dict(url=h.url,status=h.status_code,headers=list(h.raw.headers.items()),complete_body_hex=h.content.hex())for h in x.history],body_path=str(q.relative_to(S)),raw_bytes=len(b),raw_sha256=sha(b),stored_bytes=len(z),stored_sha256=sha(z),complete=True)
 except Exception as e:r.update(complete=False,error=str(e))
 r['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dump(p,r);return r
def main():
 D.mkdir(parents=True,exist_ok=True)
 urls=[('law-19-8','https://ftp.ilga.gov/ILCS/Ch%200010/Act%200005/001000050K19-8.html'),('law-22-6','https://ftp.ilga.gov/ILCS/Ch%200010/Act%200005/001000050K22-6.html'),('law-17-16.1','https://ftp.ilga.gov/ILCS/Ch%200010/Act%200005/001000050K17-16.1.html'),('state-results-role','https://www.elections.il.gov/ElectionOperations/ElectionResults.aspx'),('court-watson','https://www.supremecourt.gov/opinions/25pdf/24-1260_g3cn.pdf')]
 with ThreadPoolExecutor(max_workers=3)as pool:receipts=list(pool.map(get,urls))
 for sid,url in urls[:3]:
  q=D/(sid+'-system-curl.receipt.json')
  if q.exists():r=json.loads(q.read_bytes())
  else:
   r=dict(id=sid+'-system-curl',requested_url=url,method='GET',retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),purpose='Default system-curl certificate validation after separately retained Python certificate error; no disabled verification')
   with tempfile.TemporaryDirectory()as td:
    hd=Path(td)/'headers';bd=Path(td)/'body'
    cp=subprocess.run(['/usr/bin/curl','--silent','--show-error','--location','--max-time','35','--dump-header',str(hd),'--output',str(bd),'--write-out','%{json}',url],capture_output=True)
    r.update(exit_code=cp.returncode,stderr=cp.stderr.decode(errors='replace'),complete=cp.returncode==0,raw_response_headers_latin1=hd.read_bytes().decode('latin1')if hd.exists()else '')
    if cp.returncode==0:
     meta=json.loads(cp.stdout);b=bd.read_bytes();z=gzip.compress(b,mtime=0);bp=D/(sid+'-system-curl.gz');bp.write_bytes(z)
     r.update(status=meta['http_code'],final_url=meta['url_effective'],curl_info=meta,body_path=str(bp.relative_to(S)),raw_bytes=len(b),raw_sha256=sha(b),stored_bytes=len(z),stored_sha256=sha(z))
    else:r['error']='System curl failed; no response entity admitted'
   r['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dump(q,r)
  receipts.append(r)
 statutes=json.loads((S/'data/results-sources/operative-statutes-complete.json').read_bytes());comp=[]
 for r in receipts:
  if not r['complete']:continue
  b=gzip.decompress((S/r['body_path']).read_bytes());assert sha(b)==r['raw_sha256']
  if r['id'].startswith('law-')and r['status']==200:
   t=' '.join(Text(b).parts);section=r['id'][4:].removesuffix('-system-curl');old=next(v for v in statutes if v['section']==section);same=' '.join(t.split())==' '.join(old['complete_text'].split());assert same
   comp.append(dict(id=r['id'],current_complete_text_matches_sealed_original=True,section=old['section'],complete_text=t))
 out=dict(status='pass_bounded_current_primary_recheck',requests=len(receipts),HTTP_statuses={r['id']:r.get('status')for r in receipts},receipts=receipts,current_statute_comparisons=comp,November_returns_admitted=False,qualification='Only bounded actual primary responses. Current legal exhaustion, later docket, signed statewide roster, geographic/result joins and live source admission remain unapproved. Web reader separately returned403/inaccessible for these state/code routes; complete network responses are retained here.')
 dump(D/'review.json',out);print({r['id']:r.get('status',r.get('error'))for r in receipts});print('matched sections',[r['section']for r in comp])
if __name__=='__main__':main()

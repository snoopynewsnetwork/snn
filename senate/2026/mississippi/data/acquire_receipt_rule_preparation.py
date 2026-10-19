"""Capture bounded public legal-preparation sources; frozen completed-state originals remain read-only."""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,json,requests
ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parents[2]
OUT=ROOT/'data/coordinator-legal-preparation';OUT.mkdir(exist_ok=True)
SOURCES=[
 ('watson-scotus-docket','https://www.supremecourt.gov/docket/docketfiles/html/public/24-1260.html','Official Supreme Court docket, independently refreshed; lower-court completeness not implied'),
 ('sos-current-absentee-information','https://www.sos.ms.gov/yall-vote/absentee-voting-information','Current official FAQ located through primary SOS indexed publication'),
 ('sos-september21-availability','https://www.sos.ms.gov/news/absentee-ballots-now-available-2026-general-election','Actual September21 official election-specific publication, distinct mail and in-person processes'),
 ('watson-bound-opinion','https://www.supremecourt.gov/opinions/25pdf/609us2r65_g314.pdf','Official bound-report version found by primary court indexed search, distinct from retained slip edition'),
 ('fifth-circuit-opinions-september9','https://www.ca5.uscourts.gov/opinions?group=grouped&to=2026-09-09','Public primary opinions index; query date is a lookup bound, not proof of a disposition')]
def sh(b):return hashlib.sha256(b).hexdigest()
def rel(p):return str(p.relative_to(REPO))
def fetch(spec):
 ident,url,chain=spec;receipt=OUT/f'{ident}.receipt.json'
 if receipt.exists():
  j=json.loads(receipt.read_bytes());p=REPO/j['body']['stored_path'];b=p.read_bytes();assert len(b)==j['body']['stored_bytes']and sh(b)==j['body']['stored_sha256'];return j
 started=datetime.datetime.now(datetime.timezone.utc).isoformat();r=None;error=None
 try:r=requests.get(url,timeout=(15,60),headers={'User-Agent':'Election source research; public document retrieval'});body=r.content
 except requests.RequestException as e:body=b'';error=type(e).__name__+': '+str(e)
 ended=datetime.datetime.now(datetime.timezone.utc).isoformat();rawsh=sh(body);shared=None
 for source in (REPO/'senate/2026/florida/data/results-sources/source').glob('watson-*.receipt.json'):
  j=json.loads(source.read_bytes())
  # The completed Florida capture schema is retained independently; only compare exact entity bytes.
  bp=REPO/'senate/2026/florida'/j['body_path'] if isinstance(j.get('body_path'),str) else None
  if bp is not None and bp.exists() and gzip.decompress(bp.read_bytes())==body:shared=bp;break
 if shared is None:
  path=OUT/f'entity-{rawsh}.body.gz';stored=gzip.compress(body,mtime=0)
  if path.exists():assert gzip.decompress(path.read_bytes())==body
  else:path.write_bytes(stored)
 else:path=shared;stored=path.read_bytes()
 j={'id':ident,'method':'GET','requested_url':url,'discovery_scope':chain,'started_at_utc':started,'completed_at_utc':ended,'status':r.status_code if r is not None else 0,'final_url':r.url if r is not None else None,'response_headers':dict(r.headers) if r is not None else {},'redirects':[{'url':x.url,'status':x.status_code,'headers':dict(x.headers)}for x in r.history]if r is not None else [],'error':error,'body':{'raw_bytes':len(body),'raw_sha256':rawsh,'stored_path':rel(path),'stored_bytes':len(stored),'stored_sha256':sh(stored),'encoding':'gzip','exact_existing_entity_reused':shared is not None},'qualification':'Decoded HTTP entity, not a wire capture. HTTP observation and source publication/legal effect clocks are separate. Errors are preserved and do not establish source absence.'}
 receipt.write_text(json.dumps(j,indent=2)+'\n');return j
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5)as pool:observations=list(pool.map(fetch,SOURCES))
 out={'scope':'Bounded coordinator legal-source preparation, not a substitute for later official-results review or complete later-docket audit','observations':observations,'frozen_completed_state_originals_modified':False,'current_rule_admission':False}
 b=(json.dumps(out,indent=2)+'\n').encode();p=OUT/'source-ledger.json'
 if p.exists():assert p.read_bytes()==b,'Existing immutable capture ledger drift'
 else:p.write_bytes(b)
 # Supplemental requests depend on literal form names and a returned PDF link; preserve the initial five-observation ledger.
 from html.parser import HTMLParser
 from urllib.parse import urljoin
 class Links(HTMLParser):
  def __init__(self):super().__init__();self.hrefs=[]
  def handle_starttag(self,tag,attrs):
   d=dict(attrs)
   if tag=='a'and'href'in d:self.hrefs.append(d['href'])
 parent=next(j for j in observations if j['id']=='fifth-circuit-opinions-september9');html=gzip.decompress((REPO/parent['body']['stored_path']).read_bytes()).decode()
 assert 'action="/opinions"'in html and 'name="docket"'in html and 'value="1000"'in html
 for value in ['pord','pub','upord','unpub']:assert ('value="'+value+'"')in html
 query=fetch(('fifth-circuit-published-form-docket-query','https://www.ca5.uscourts.gov/opinions?docket=24-60395&pageSize=1000&type=pord&type=pub&type=upord&type=unpub','Literal GET action /opinions and actual docket/pageSize/type input names and option values observed in retained primary index form; all four source types requested'))
 parser=Links();parser.feed(gzip.decompress((REPO/query['body']['stored_path']).read_bytes()).decode());href='/opinions/unpub/24/24-60395.0.pdf';assert href in parser.hrefs
 child=fetch(('fifth-circuit-september9-remand',urljoin(query['final_url'],href),'Literal PDF href returned by actual official opinions form exact-docket query, September9,2026 unpublished disposition'))
 supplement={'scope':'Two dependent observations using the captured public form and returned literal case-document link','observations':[query,child]};sb=(json.dumps(supplement,indent=2)+'\n').encode();sp=OUT/'supplemental-source-ledger.json'
 if sp.exists():assert sp.read_bytes()==sb,'Supplemental immutable capture drift'
 else:sp.write_bytes(sb)
 print(json.dumps({'observations':len(observations)+2,'status_counts':{str(v):sum(x['status']==v for x in observations+[query,child])for v in sorted({x['status']for x in observations+[query,child]})},'initial_ledger':rel(p),'supplemental_ledger':rel(sp),'initial_bytes':len(b),'initial_sha256':sh(b)}))

"""Bounded MARIS authority/download preparation, never a reporting crosswalk."""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,io,json,urllib.parse,zipfile
from html.parser import HTMLParser
import requests,threading
LOCK=threading.Lock()
D=Path(__file__).resolve().parent;P=D/'coordinator-map-preparation';MF=P/'source-ledger.json'
def sha(b):return hashlib.sha256(b).hexdigest()
class Links(HTMLParser):
 def __init__(self):super().__init__();self.out=[];self.current=None
 def handle_starttag(self,tag,attrs):
  if tag=='a':
   a=dict(attrs)
   if'href'in a:self.current=dict(href=a['href'],text='');self.out.append(self.current)
 def handle_data(self,data):
  if self.current is not None:self.current['text']+=data
 def handle_endtag(self,tag):
  if tag=='a':self.current=None
def fetch(job):
 sid,url,parent=job;row=dict(id=sid,requested_url=url,parent_source_id=parent,request_method='GET',retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:
  r=requests.get(url,timeout=35);b=r.content
  with LOCK:
   candidates=[p for p in P.glob('*.body.gz')if sha(gzip.decompress(p.read_bytes()))==sha(b)]
   p=candidates[0]if candidates else P/(sid+'-'+sha(b)[:12]+'.body.gz')
   if not p.exists():p.write_bytes(gzip.compress(b,mtime=0))
  row.update(status=r.status_code,final_url=r.url,headers=dict(r.headers),redirects=[dict(url=x.url,status=x.status_code,headers=dict(x.headers))for x in r.history],raw_bytes=len(b),raw_sha256=sha(b),path=str(p.relative_to(D.parent)),stored_bytes=p.stat().st_size,stored_sha256=sha(p.read_bytes()));assert p.stat().st_size<40000000
 except requests.RequestException as e:row.update(status=0,error_type=type(e).__name__,error=str(e))
 receipt=P/(sid+'.receipt.json')
 assert not receipt.exists()
 receipt.write_text(json.dumps(row,indent=2)+'\n')
 return row
def body(row):
 b=(D.parent/row['path']).read_bytes();assert sha(b)==row['stored_sha256'];b=gzip.decompress(b);assert sha(b)==row['raw_sha256'];return b
def links(row):
 p=Links();p.feed(body(row).decode('utf-8','replace'));return [dict(**l,url=urllib.parse.urljoin(row['final_url'],l['href']))for l in p.out]
def main():
 P.mkdir(exist_ok=True)
 if MF.exists():rows=json.loads(MF.read_bytes())
 else:rows=[]
 def acquire(jobs):
  nonlocal rows
  old={r['id']:r for r in rows};todo=[]
  for j in jobs:
   if j[0]in old:assert old[j[0]]['requested_url']==j[1]
   else:
    receipt=P/(j[0]+'.receipt.json')
    if receipt.exists():
     recovered=json.loads(receipt.read_bytes());assert recovered['requested_url']==j[1];rows.append(recovered)
    else:todo.append(j)
  if todo:
   with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
    for r in pool.map(fetch,todo):rows.append(r);print(r['id'],r.get('status'),r.get('raw_bytes'),flush=True)
   MF.write_text(json.dumps(rows,indent=2)+'\n')
  if MF.read_bytes()!=(json.dumps(rows,indent=2)+'\n').encode():MF.write_text(json.dumps(rows,indent=2)+'\n')
  return {r['id']:r for r in rows}
 rr=acquire([('maris-political-parent','https://maris.mississippi.edu/HTML/DATA/Political.html',None)])
 assert rr['maris-political-parent']['status']==200
 ls=links(rr['maris-political-parent']);updated=next(l for l in ls if l['url'].endswith('/UpdatedVotingPrecincts.html'));old=next(l for l in ls if l['url'].endswith('/2020VotingPrecincts.html'))
 rr=acquire([('maris-updated-precinct-parent',updated['url'],'maris-political-parent'),('maris-2020-precinct-parent',old['url'],'maris-political-parent')])
 assert all(rr[s]['status']==200 for s in ['maris-updated-precinct-parent','maris-2020-precinct-parent'])
 jobs=[];selected=[]
 for sid in ['maris-updated-precinct-parent','maris-2020-precinct-parent']:
  for l in links(rr[sid]):
   if urllib.parse.urlparse(l['url']).path.lower().endswith(('.zip','.pdf'))and'/MISC/MiscPDF/Location.pdf'not in l['url']:
    if sid=='maris-updated-precinct-parent':key='maris-2023-precinct-'+l['text'].strip().lower().replace(' ','-')
    else:key='maris-2020-precinct-'+('metadata'if urllib.parse.urlparse(l['url']).path.lower().endswith('.pdf')else'zip')
    jobs.append((key,l['url'],sid));selected.append(dict(source_id=key,parent=sid,literal_href=l['href'],literal_link_text=l['text'],resolved_url=l['url']))
 assert len({j[0]for j in jobs})==len(jobs)
 rr=acquire(jobs)
 retries=[]
 for row in list(selected):
  if rr[row['source_id']].get('status')==0:
   sid=row['source_id']+'-retry-1';retries.append((sid,row['resolved_url'],row['parent']));selected.append(dict(row,source_id=sid,retry_of=row['source_id']))
 if retries:rr=acquire(retries)
 audits=[]
 for s in selected:
  r=rr[s['source_id']]
  if r.get('status')!=200:continue
  b=body(r)
  if urllib.parse.urlparse(r['requested_url']).path.lower().endswith('.zip'):
   z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip()is None
   audits.append(dict(source_id=r['id'],members=[dict(member=i.filename,raw_bytes=i.file_size,CRC32=f'{i.CRC:08x}',sha256=sha(z.read(i)))for i in z.infolist()],archive_CRC_pass=True))
 out=dict(status='bounded_official_map_authority_preparation_only',source_ledger_path=str(MF.relative_to(D.parent)),source_observations=len(rows),initial_unsealed_capture_history='data/coordinator-map-preparation/initial-unsealed-entity-inventory.json',observed_parent_links=selected,archive_member_audits=audits,
 qualification='Actual MARIS Political parent calls the updated coverage post2020 and not entirestate. UpdatedPrecincts child saysCurrentData2023 and attributes providers toGoldenTrianglePDD/individualcounties. The separate2020 statewide page explicitly calls its source2020 US Census voting precincts. All titles, literalhrefs, originals and missing/error outcomes survive separately. No assumption that yearlabels/nativecounts/results names establish historic2024 orNovember2026 legal/reporting equivalence. No priority-native match, physical boundary approval, allocation or completed map assignment follows.',priority_accepted=False,current_crosswalk_approved=False)
 p=D/'coordinator-map-authority-preflight.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(report_path=str(p),bytes=p.stat().st_size,sha256=sha(p.read_bytes()),observations=len(rows),CRC_archives=len(audits))))
if __name__=='__main__':main()

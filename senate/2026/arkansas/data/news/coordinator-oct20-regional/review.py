"""Independent bounded newsroom request/body and literal publication audit."""
from pathlib import Path
from html.parser import HTMLParser
import gzip,hashlib,json
H=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
class Text(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.parts=[];self.skip=0;self.title=False;self.t=[]
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.skip+=1
  if t=='title':self.title=True
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip-=1
  if t=='title':self.title=False
 def handle_data(self,x):
  if not self.skip:self.parts.append(x)
  if self.title:self.t.append(x)
def main():
 rows=[];bodies={}
 for p in sorted(H.glob('*.receipt.json')):
  r=json.loads(p.read_text());assert r['requested_UTC'] and r['completed_UTC'] and r['requested_url'].startswith('https://')
  for z in r['hops']:
   b=(H/z['body_path']).read_bytes();raw=gzip.decompress(b);assert sha(b)==z['stored_sha256'] and len(b)==z['stored_bytes']<40000000;assert sha(raw)==z['raw_sha256'] and len(raw)==z['raw_bytes'];assert z['request_headers'] and z['response_headers'];bodies[z['raw_sha256']]=len(raw)
  final=r['hops'][-1];raw=gzip.decompress((H/final['body_path']).read_bytes());p1=Text();p1.feed(raw.decode('utf-8','replace'));text=' '.join(' '.join(p1.parts).split());title=' '.join(p1.t)
  if r['id']=='pinebluff-current-dates':assert 'August 25, 2026' in text and 'Jefferson County Clerk' in text and 'Nov. 3' in text
  if r['id']=='pinebluff-current-candidates':assert 'August 26, 2026' in text and 'UPDATED 4:35 p.m. Aug. 27' in text and 'Jefferson County clerk' in text
  if r['id']=='searktoday-home':assert 'Snapchat' in text and 'Digital Platforms' in text and json.loads((H/'searktoday-home.election-links.json').read_text())==[]
  if r['id']=='ktve-home':assert final['status']==403
  rows.append(dict(id=r['id'],receipt=p.name,requested_url=r['requested_url'],final_url=r.get('final_url'),status=r.get('status'),title_literal=title,complete_raw_sha256=final['raw_sha256'],complete_raw_bytes=final['raw_bytes']))
 assert len(rows)==4 and len(bodies)==4
 out=dict(status='pass_bounded_regional_publication_access_not_November_count_admission',requests=rows,complete_request_count=4,complete_entities=4,HTTP200=3,HTTP403=1,original_news_aggregate_unchanged=True,publication_findings=['PineBluffCommercial actualAugust25 election logistics report attributes information to JeffersonCountyClerk; original dates retained, no verified statewide law/November count feed inferred.','PineBluffCommercial actualAugust26 local candidate report explicitly updatedAugust27 4:35p.m., timezone notprinted; local contested/unopposed offices are not an approved Senate roster.','SearkToday homepage200 now exposes travel/digital-platform material and no literal election links in this bounded response; excluded as a demonstrated election newsroom/count backstop. No claim about all historical publications.','KTVE/myarklamiss homepage403 complete body retained; webreader robots is separate from this actual response.'],search_scope_note='search-scope-note.json',all_original_entities_retained=True,current_counts_ids_supplier_independence_measured_cadence_approved=False)
 (H/'review.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 rows=[]
 for p in sorted(H.iterdir()):
  if p.is_file() and p.name!='asset-manifest.json':
   b=p.read_bytes();assert len(b)<40000000;rows.append(dict(path=p.name,bytes=len(b),sha256=sha(b)))
 (H/'asset-manifest.json').write_text(json.dumps(dict(assets=rows,excludes_only='asset-manifest.json'),indent=2)+'\n')
 print(dict(requests=4,entities=4,assets=len(rows),maximum=max(r['bytes'] for r in rows)))
if __name__=='__main__':main()

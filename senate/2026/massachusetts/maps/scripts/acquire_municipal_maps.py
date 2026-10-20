from acquire import *
import re,json,concurrent.futures
req=json.loads((M/'state-map-requests.json').read_bytes());byid={x['link_id']:x for x in req};found={};errors=[]
for p in sorted((M/'web').glob('map-navigation-*.txt')):
 for block in p.read_text().split('\n--------------------------------------------------------------------------------\n'):
  k=re.search(r'Source: click\(\{"ref_id":"turn1view2","id":(\d+)\}',block);u=re.search(r'^.*?\((https?://[^\n]+)\)\n',block)
  if not u: u=re.search(r'Failed to fetch (https?://[^\s]+?)(?=: |$)',block)
  if k and u and int(k[1])in byid:
   found[int(k[1])]=dict(**byid[int(k[1])],url=u[1],navigation=str(p.relative_to(M)))
  else:errors.append(block[:400])
dump(M/'map-targets.json',list(found.values()));dump(M/'map-navigation-gaps.json',dict(missing=[x for x in req if x['link_id']not in found],unparsed_blocks=errors))
print('actual targets',len(found),'missing',len(req)-len(found),flush=True)
def work(x):
 b,r=fetch('state-map-'+str(x['link_id']),x['url'],parent=x['navigation'],literal_href=None)
 return dict(**x,receipt='receipts/state-map-'+str(x['link_id'])+'.json',format_observed='PDF'if b.startswith(b'%PDF-')else 'HTML/access/error',complete_pdf=b.startswith(b'%PDF-'),raw_bytes=len(b),status=r.get('status'),raw_sha256=r.get('raw_sha256'))
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as ex:out=list(ex.map(work,found.values()))
dump(M/'municipal-map-acquisitions.json',out);print('PDFs',sum(x['complete_pdf']for x in out),'parent coverage',len(set(x['parent_literal']for x in out if x['complete_pdf'])))

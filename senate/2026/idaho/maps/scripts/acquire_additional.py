#!/usr/bin/env python3
"""Precise supplemental published map links; preserves failed literal relative URLs."""
import concurrent.futures,json,re
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
from acquire import fetch,MAPS
DISCOVERED={
 '16011':'https://www.binghamid.gov/departments/elections/ElectionMaps',
 '16031':'https://www.cassia.gov/departments/Elections/Election-Maps',
 '16047':'https://www.goodingcounty.org/212/Elections',
 '16075':'https://www.payettecounty.org/clerk',
 '16085':'https://www.valleycountyid.gov/departments/Elections',
 '16079':'https://shoshonecounty.id.gov/',
}
def get(args):
 try:
  r=fetch(*args);return {k:r.get(k) for k in ['id','status','raw_bytes','stored_path']}
 except Exception as e:
  (MAPS/'source'/f'{args[0]}.transport-error.json').write_text(json.dumps(dict(id=args[0],requested_url=args[1],parent=args[2],literal_href=args[3],transport_error=repr(e),http_status=None),indent=2)+'\n');return dict(id=args[0],error=repr(e))
def main():
 jobs=[('additional-'+k+'-discovery',u,'Primary web search: exact official page located; independent authority domain from SOS directory',None,'Official county map/election/root page discovered by primary-domain search') for k,u in DISCOVERED.items()]
 # Existing published clerk/election links missed by shallow first traversal.
 rs=[json.loads(p.read_text()) for p in (MAPS/'source').glob('county-*.receipt.json')]
 for r in rs:
  if r['id'] in ['county-16073','county-16069','county-16077','county-16019']:
   for l in r.get('links',[]):
    if l['text'].strip().lower() in ['clerk','elections','election','election office','elections office']:
     jobs.append(('additional-'+r['id'].split('-')[1]+'-office-'+str(len(jobs)),l['url'],r['id'],l['href'],'Exact published election/clerk office link'))
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(get,jobs))
 # Two narrowly bounded follow steps; original relative URLs, no speculative path repair.
 for depth in range(2):
  rs=[json.loads(p.read_text()) for p in (MAPS/'source').glob('*.receipt.json') if not p.name.startswith('native-')]
  seen={r['requested_url'] for r in rs};jobs=[]
  for r in rs:
   if not r['id'].startswith(('county-','additional-')):continue
   k=r['id'].split('-')[1]
   if not k.isdigit():continue
   for l in r.get('links',[]):
    u=l['url'];t=(l['text']+' '+l['href']).lower()
    ismap=bool(re.search(r'precinct|polling.?place|polling.?location|where.to.vote',t))
    isoffice=r['id'].startswith('additional-') and (l['text'].strip().lower() in ['elections','election information','precinct maps','election maps','maps'])
    if not (ismap or isoffice) or not u.startswith(('http:','https:')) or u in seen:continue
    if re.search(r'facebook|twitter|linkedin|reddit|mailto|#|login|register|registration|committe|candidate|result|\.aspx\?qid|voteidaho|votertools|sos.idaho|\.js',u+' '+l['text'],re.I):continue
    if any('county-'+k in j[0] for j in jobs) and sum(k in j[0] for j in jobs)>5:continue
    seen.add(u);jobs.append(('additional-'+k+'-map-'+str(depth)+'-'+str(len(jobs)),u,r['id'],l['href'],'Exact county-published precinct/map/roster link; qualified source reference'))
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(get,jobs))
  print(json.dumps(dict(depth=depth,requests=len(out),pdfs=[x for x in out if str(x.get('stored_path')).endswith('.pdf')]),ensure_ascii=False))
if __name__=='__main__':main()

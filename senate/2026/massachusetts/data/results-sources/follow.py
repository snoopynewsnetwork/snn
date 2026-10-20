"""Prepare finite, reviewable requests from actual observed public links.
phase directory: Secretary department links resolved by web click.
phase municipal: up to four relevant HTML/file/vendor links per priority parent.
No requests are issued by this program.
"""
from pathlib import Path
from urllib.parse import urlsplit
import hashlib,json,re,sys
O=Path(__file__).resolve().parent
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def ident(u):return hashlib.sha256(u.encode()).hexdigest()[:16]
def main():
 phase=sys.argv[1];jobs=[]
 if phase=='directory':
  rows=[]
  for p in sorted((O/'source/navigation').glob('*.json')):
   d=json.loads(p.read_text());req={r['id']:r for r in d['requests']}
   for b in d['response'].split('--------------------------------------------------------------------------------'):
    b=b.lstrip()
    m=re.search(r'Source: click\(\{"ref_id":"turn2view1","id":(\d+)\}',b)
    if not m:continue
    r=req[int(m[1])];u=re.search(r'^.*?\((https?://[^\n]+)\)\n',b);u=u[1] if u else None
    if not u:
     bad=re.search(r'Failed to fetch (https?://\S+?): \(',b);u=bad[1]if bad else None
    row=dict(parent_literal=r['name'],requested_directory_link_id=r['id'],web_evidence=str(p.relative_to(O)),web_representation=b,url=u,original_literal_href=None,navigation_kind='homepage fallback'if p.name.startswith('home-')else'department directory')
    rows.append(row)
    if u:jobs.append(dict(id='dept-'+ident(u),url=u,parent=d['parent'],literal_href=None,reason='actual Secretary public department directory link resolved by web click; exact initial href not exposed by web tool'))
  dump(O/'directory-navigation.json',rows)
 else:
  ds=json.loads((O/'municipal-discovery.json').read_text());nav=json.loads((O/'directory-navigation.json').read_text());receipts=[json.loads(p.read_text())for p in (O/'source/http').glob('*.json')];byurl={r['requested_url']:r for r in receipts};seen=set(byurl)
  prior=json.loads((O/'municipal-follow-requests.json').read_text())if (O/'municipal-follow-requests.json').exists()else[]
  def score(x):
   t=(x['text']+' '+x['url']).lower()
   if not x['public_fetch_allowed'] or x['tag']not in ('a','iframe'):return -1
   if re.search('unsubscribe|subscribe|newsletter|notify|calendar.aspx|bidid=|/bids|dog.license|pay|/search|sign.in|emailpage|share|facebook|twitter|instagram|linkedin|google.com/maps',t):return -1
   n=0
   if re.search('election.results|election-results|elections/results|results.*election',t):n+=70
   if re.search('election|voting|registrar|clerk|canvass|recount',t):n+=35
   if re.search('2024|2026|2022|general|state.election|unofficial|official',t):n+=15
   if re.search('clarityelections|enhancedvoting|electionstats|civicweb|electionreporting|electionnight|results.enr',t):n+=70
   if re.search('town.report|annual.report|minutes|agenda|town.meeting',t):n-=25
   return n
  for i,d in enumerate(ds):
   if not d['priority_parent']:continue
   if any(j.get('reason','').startswith('bounded actual link for historical research parent '+d['source_parent_literal']+':')for j in prior):continue
   urls=[x['url']for x in d['selected_sources']]+[x['url']for x in nav if x['parent_literal']==d['source_parent_literal']and x['url']];links=[]
   for u in urls:
    r=byurl.get(u)
    if not r:continue
    ip=O/'source/inspect'/(r['id']+'.json')
    if not ip.exists():continue
    ins=json.loads(ip.read_text())
    for x in ins['links']:
     if score(x)>25:links.append((score(x),x,r))
   links.sort(key=lambda x:-x[0]);n=0
   for s,x,r in links:
    if x['url']in seen:continue
    jobs.append(dict(id='follow-'+ident(x['url']),url=x['url'],parent=r['requested_url'],literal_href=x['literal_href'],reason='bounded actual link for historical research parent '+d['source_parent_literal']+': '+x['text']));seen.add(x['url']);n+=1
    if n>=4:break
 if phase=='municipal':jobs=prior+jobs
 dump(O/(phase+'-follow-requests.json'),jobs);print(dict(phase=phase,requests=len(jobs)))
if __name__=='__main__':main()

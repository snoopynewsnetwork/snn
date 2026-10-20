"""Bounded explicit links only: <=3 result/election links per authority per pass.
No endpoint enumeration, no guessed election IDs. Saved link-selection plan is reviewable.
"""
from common import *
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import sys

def score(a):
 t=(a['text']+' '+a['literal_href']).lower()
 if any(x in t for x in ['facebook','twitter','instagram','mailto:','javascript:','login','admin','calendar','registration','register-to','polling-place','judges','accessib','candidate-filing','apply','board-meeting','minutes']):return -1
 s=0
 if any(x in t for x in ['result','canvass','clarityelections','electionreporting','enhancedvoting','electionnight','enr/']):s+=100
 if any(x in t for x in ['2026','current']):s+=20
 if any(x in t for x in ['november','general']):s+=10
 if any(x in t for x in ['election','voting']):s+=5
 if any(x in t for x in ['2025','2023','2021','primary','2022','2020']):s-=8
 return s

def main():
 level=int(sys.argv[1]) if len(sys.argv)>1 else 1;plan=[]
 rows=json.loads((HERE/'current-authority-directory.json').read_bytes())
 for r in rows:
  id=r['current_directory_selector_value'];parents=[HERE/'receipts'/f'authority-{id}.json'] if level==1 else sorted((HERE/'receipts').glob(f'authority-{id}-L1-*.json'))
  known={}
  for p in (HERE/'receipts').glob(f'authority-{id}*.json'):
   m=json.loads(p.read_bytes());known[m['url']]=1;known[m.get('final_url')]=1
  candidates=[]
  for p in parents:
   if not p.exists():continue
   m=json.loads(p.read_bytes())
   if m.get('status')!=200 or not m.get('complete'):continue
   try:h=HTML(body(m).decode('utf8',errors='replace'))
   except Exception:continue
   for a in h.links:
    if not a['literal_href']:continue
    url=urljoin(m['final_url'],a['literal_href'].replace('\\','/'))
    if score(a)>0 and url.startswith(('http://','https://')) and url.split('#')[0] not in known:
     candidates.append((score(a),a,m,url));known[url.split('#')[0]]=1
  candidates.sort(key=lambda x:-x[0])
  for i,(s,a,m,url) in enumerate(candidates[:3 if level==1 else 2]):
   plan.append(dict(id=f'authority-{id}-L{level}-{i+1}',url=url,parent=m['id'],literal_href=a['literal_href'],link_text=a['text'],selection_score=s,authority_directory_selector=id,basis='actual public link selected by bounded documented result/election relevance; complete source page retained'))
 write(HERE/f'follow-plan-L{level}.json',plan)
 def work(x):
  m=fetch(x['id'],x['url'],x['parent'],x['literal_href'],basis=x['basis']);h=inspect(m);return x['id'],m.get('status'),m.get('raw_bytes'),m.get('error')
 with ThreadPoolExecutor(max_workers=4) as pool:
  for x in pool.map(work,plan):print(x,flush=True)
if __name__=='__main__':main()

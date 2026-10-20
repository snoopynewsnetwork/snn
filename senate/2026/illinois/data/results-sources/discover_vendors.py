from common import *
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

def main():
 plan=[];known={json.loads(p.read_bytes())['url'] for p in (HERE/'receipts').glob('*.json')};per={}
 for p in sorted((HERE/'receipts').glob('authority-*.json')):
  m=json.loads(p.read_bytes())
  if m.get('status')!=200 or not m.get('complete'):continue
  b=body(m)
  if b.startswith((b'%PDF',b'PK')):continue
  s=b.decode('utf8',errors='replace');h=HTML(s);aid=m['id'].split('-')[1];links=[]
  for a in h.links:
   href=a.get('literal_href')
   if href and any(x in href.lower() for x in ['clarityelections.com','enhancedvoting.com','electionreporting.com','livevoterturnout.com','platinumelectionresults.com','electionresults','election-results','election_results','results/']):links.append((href,'published result link',a.get('text')))
  # Public client navigation only; do not interpret IDs or generate endpoints.
  for x in re.finditer(r'(?:window\.)?location(?:\.href)?\s*=\s*[\"\']([^\"\']+)[\"\']',s):links.append((x.group(1),'literal client-side location assignment',None))
  for a in h.scripts:
   href=a.get('src','')
   if href and (any(x in m['final_url'] for x in ['clarityelections.com','dupageresults','livevoterturnout','platinumelectionresults']) or any(x in href.lower() for x in ['election','result','enr'])):
    if not any(x in href.lower() for x in ['jquery','google','analytics','bootstrap','polyfills','runtime.']):links.append((href,'public result app script src',None))
  for href,basis,txt in links:
   u=urljoin(m['final_url'],href).split('#')[0]
   if any(x in u.lower() for x in ['facebook.','twitter.','instagram.','plus.google','reddit.','/security/','myaccount','login','admin','profilecreate','contact-form','mapbox','jquery','cdn.syncfusion','popper.js']):continue
   if not u.startswith(('https://','http://')) or u in known:continue
   if per.get(aid,0)>=5:continue
   per[aid]=per.get(aid,0)+1;known.add(u);id=f'authority-{aid}-vendor-{per[aid]}'
   plan.append(dict(id=id,url=u,parent=m['id'],literal_href=href,discovery_basis=basis,link_text=txt))
 write(HERE/'vendor-follow-plan.json',plan)
 def work(x):
  m=fetch(x['id'],x['url'],x['parent'],x['literal_href'],basis=x['discovery_basis']);inspect(m);return x['id'],m.get('status'),m.get('raw_bytes'),x['url']
 with ThreadPoolExecutor(max_workers=4) as pool:
  for x in pool.map(work,plan):print(x,flush=True)
if __name__=='__main__':main()

from common import *
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

def run_plan(plan,name):
 write(HERE/(name+'-plan.json'),plan)
 def work(x):
  m=fetch(x['id'],x['url'],x.get('parent'),x.get('literal_href'),basis=x['basis']);inspect(m);return x['id'],m.get('status'),m.get('raw_bytes')
 with ThreadPoolExecutor(max_workers=3) as pool:
  for x in pool.map(work,plan):print(x,flush=True)

def main():
 plan=[];known=set();done=set();receipts=[json.loads(p.read_bytes()) for p in sorted((HERE/'receipts').glob('authority-*.json'))]
 for m in receipts:
  u=m.get('final_url','');aid=m['id'].split('-')[1]
  if m.get('status')!=200 or not m.get('complete'):continue
  b=body(m)
  if b.startswith((b'%PDF',b'PK')):continue
  s=b.decode('utf8',errors='replace');h=HTML(s)
  if 'platinumelectionresults.com/turnouts/county/' in u and aid not in done:
   done.add(aid)
   targets=[a for a in h.links if a['text'].strip() in ['FEDERAL','Data','Summary Reports','Precincts Reporting','By Precinct']]
   for i,a in enumerate(targets):plan.append(dict(id=f'authority-{aid}-platinum-{i+1}',url=urljoin(u,a['literal_href']),parent=m['id'],literal_href=a['literal_href'],basis='actual public navigation '+a['text']))
  if 'clarityelections.com' in u and (re.search(r'/\d+/?$',u) or '/web.' in u or '/Web02.' in u):
   if 'versions.txt' in s and (aid,'version') not in known:
    known.add((aid,'version'));base=u if u.endswith('/') else u+'/'
    v=fetch(f'authority-{aid}-versions',urljoin(base,'versions.txt'),m['id'],'versions.txt',basis='literal public XMLHttpRequest versions pointer in root shell');
    # The exact client constructor supplies the public web-build base.
    build=re.search(r"'(web\.[0-9]+)\.?'",s)
    if build and v.get('status') in [200,403,404]:
     txt=body(v).decode().strip() if v.get('status')==200 else ''
     if not txt or re.fullmatch(r'[0-9]+',txt):
      target=base+build.group(1)+('.'+txt if txt else '')+'/'
      plan.append(dict(id=f'authority-{aid}-clarity-web',url=target,parent=m['id'],literal_href=None,basis='observed root constructor + actual versions response; '+v['id']))
  if 'elections.json?v=' in s and 'clarityelections' in u or 'elections.json?v=' in s and 'dupageresults' in u:
   timestamp=str(int(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000));target=urljoin(u,'elections.json?v='+timestamp)
   plan.append(dict(id=f'authority-{aid}-clarity-elections',url=target,parent=m['id'],literal_href='elections.json?v= + (new Date).getTime()',basis='literal complete downloaded app constructor, actual current UTC epoch milliseconds'))
 # primary candidate details and all-active print/download public controls
 m=json.loads((HERE/'receipts/state-senate-candidates-all.json').read_bytes());h=HTML(body(m).decode())
 for i,a in enumerate([a for a in h.links if a['literal_href'] and 'CandidateDetailEO.aspx?' in a['literal_href']],1):plan.append(dict(id=f'state-senate-detail-{i}',url=urljoin(m['final_url'],a['literal_href']),parent=m['id'],literal_href=a['literal_href'],basis='literal all-status November Senate candidate detail hyperlink'))
 a=next(a for a in h.links if a['literal_href'] and 'CandidateList.aspx?' in a['literal_href']);plan.append(dict(id='state-senate-list',url=urljoin(m['final_url'],a['literal_href']),parent=m['id'],literal_href=a['literal_href'],basis='literal November Senate office-list hyperlink'))
 m=json.loads((HERE/'receipts/ag-usps-tro.json').read_bytes());h=HTML(body(m).decode());a=next(a for a in h.links if 'TRO%20order.pdf' in (a['literal_href'] or ''));plan.append(dict(id='court-usps-aug28-order',url=urljoin(m['final_url'],a['literal_href']),parent=m['id'],literal_href=a['literal_href'],basis='actual AG link to complete TRO'))
 run_plan(plan,'deep-public')
if __name__=='__main__':main()

from common import *
from deep_public import run_plan

def main():
 plan=[]
 for p in sorted((HERE/'receipts').glob('*-clarity-web.json')):
  m=json.loads(p.read_bytes());h=HTML(body(m).decode());aid=m['id'].split('-')[1]
  for a in h.scripts:
   if a.get('src','').startswith('main.') or a.get('src')=='main.js':plan.append(dict(id=f'authority-{aid}-clarity-main',url=urljoin(m['final_url'],a['src']),parent=m['id'],literal_href=a['src'],basis='actual public application script src'))
 # Full source public candidate downloads use actual form events.
 m=json.loads((HERE/'receipts/state-candidate-download-options.json').read_bytes());h=HTML(body(m).decode())
 for event,id in [('btnText','state-candidate-file-tsv'),('btnXML','state-candidate-file-xml')]:
  a=next(a for a in h.links if event in (a['literal_href'] or ''));target=re.search(r"__doPostBack\('([^']+)'",a['literal_href']).group(1);d={x['name']:x.get('value','') for x in h.inputs if x.get('type')=='hidden'};d.update(__EVENTTARGET=target,__EVENTARGUMENT='')
  x=fetch(id,m['final_url'],m['id'],a['literal_href'],method='POST',data=d,basis='actual public candidate download event');inspect(x);print(id,x.get('status'),x.get('raw_bytes'),flush=True)
 run_plan(plan,'follow-data')
if __name__=='__main__':main()

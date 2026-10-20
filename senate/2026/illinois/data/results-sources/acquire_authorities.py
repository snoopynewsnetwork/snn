from common import *
from concurrent.futures import ThreadPoolExecutor

def directory():
 d=parsefile(HERE/'parsed/state-directory-all.json.gz');s=parsefile(HERE/'parsed/state-directory.json.gz')['selects'][0]
 options={x['text']:x['attrs']['value'] for x in s['options'] if int(x['attrs']['value'])>0}
 rows=[]
 for i,r in enumerate(d['rows'][1:],1):
  assert len(r['cells'])==7
  name=r['cells'][0]['text'];id=options[name];links=r['cells'][0]['links'];url=links[0]['href'] if links else None
  rows.append(dict(directory_position_1based=i,current_directory_selector_value=id,current_directory_label=name,complete_directory_row=r,columns_in_order=[c['text'] for c in d['rows'][0]['cells']],official_url_literal=url,source_receipt='data/results-sources/receipts/state-directory-all.json',historical_reference_rule='roster identity only; no current result key or boundary join'))
 assert len(rows)==108;write(HERE/'current-authority-directory.json',rows);return rows

def run():
 rows=directory()
 def work(r):
  id=r['current_directory_selector_value'];url=r['official_url_literal']
  if not url:return id,'blank publisher link'
  m=fetch('authority-'+id,url,'state-directory-all',url,basis='actual current state directory jurisdiction hyperlink; no inferred result endpoint');h=inspect(m)
  return id,m.get('status'),m.get('error'),len(h.links)
 with ThreadPoolExecutor(max_workers=4) as pool:
  for x in pool.map(work,rows):print(x,flush=True)
if __name__=='__main__':run()

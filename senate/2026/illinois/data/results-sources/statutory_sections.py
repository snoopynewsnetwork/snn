from common import *
from curl_evidence import fetch_curl
from concurrent.futures import ThreadPoolExecutor
m=parsefile(HERE/'receipts/law-ftp-election-code-files.json');h=HTML(body(m).decode())
sections=['1-6','1-9','1-9.1','1-9.2','1A-19','2A-1.1','17-1','17-16.1','18-9.1','18A-5','18A-15','19-2','19-4','19-8','19A-15','19A-25','20-8','22-1','22-6','22-7','22-8','22-9','22-9.1','23-1.1a','23-2','23-3','23-4','23-5','23-20','23-23.2','24B-15','24C-15']
plan=[]
for section in sections:
 needle='001000050K'+section+'.html';a=next((a for a in h.links if a['text']==needle),None)
 assert a,section
 plan.append(dict(id='law-code-'+section,url=urljoin(m['final_url'],a['literal_href']),parent=m['id'],href=a['literal_href'],section=section))
write(HERE/'statutory-section-request-plan.json',plan)
def work(x):
 r=fetch_curl(x['id'],x['url'],x['parent'],x['href'],basis='literal official source-file link for cited Election Code section '+x['section']);return x['section'],r.get('status'),r.get('raw_bytes')
with ThreadPoolExecutor(max_workers=3) as pool:
 for x in pool.map(work,plan):print(x,flush=True)

#!/usr/bin/env python3
import gzip,re,html,json
from pathlib import Path
from urllib.parse import urljoin
D=Path(__file__).resolve().parent;S=D/'source'
def main():
 out=[]
 for p in S.glob('*.receipt.json'):
  a=json.loads(p.read_text())
  if a.get('status')!=200 or not a.get('asset') or a.get('reference_path'):continue
  b=gzip.decompress((S/a['asset']).read_bytes())
  if b.startswith(b'%PDF'):continue
  s=b.decode(errors='replace')
  for h,l in re.findall(r'<a[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>',s,re.S|re.I):
   h=html.unescape(h);l=html.unescape(re.sub('<[^>]+>',' ',l)).strip()
   out.append({'parent':a['id'],'url':urljoin(a['final_url'],h),'literal_href':h,'label':l})
 (D/'source-link-inventory.json').write_text(json.dumps(out,indent=2)+'\n')
 for a in out:
  if a['parent'] in ['morris-results','essex-results','bergen-prior'] and '2024' in a['url']+' '+a['label']:print(a)
 jobs=[['sussex-2024-archive','https://www.sussexcountyclerk.org/777/General-Election','sussex-elections'],['ocean-archive','https://oceancountyclerk.com/frmElectionServices?page=archives','ocean-elections'],['union-results','https://ucnj.org/boe/election-results/','union-boe'],['bergen-results','https://www.bergencountyclerk.gov/Election','bergen-clerk-0']]
 for a in out:
  if a['parent']=='morris-results' and re.search(r'2024.*general|general.*2024',a['url']+' '+a['label'],re.I) and not 'primary' in (a['url']+' '+a['label']).lower():jobs.append(['morris-2024-'+str(len(jobs)),a['url'],a['parent']])
  if a['parent']=='salem-archive' and any(x in a['url'] for x in ['ESR-w-Write-Ins-2024-General','Official-SOVC-Gen-2024']):jobs.append(['salem-2024-'+str(len(jobs)),a['url'],a['parent']])
 (S/'county-second-follow-jobs.json').write_text(json.dumps(jobs,indent=2)+'\n');print('jobs',len(jobs))
if __name__=='__main__':main()

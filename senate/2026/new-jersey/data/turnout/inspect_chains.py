#!/usr/bin/env python3
"""Discover only literal links in retained public authority pages; no network or shared writes."""
from pathlib import Path
import gzip,re,json,html
from urllib.parse import urljoin
D=Path(__file__).resolve().parent;S=D/'source'
def plain(s):return html.unescape(re.sub('<[^>]+>',' ',s)).strip()
def links(s):return [{'url':html.unescape(h),'label':plain(l)} for h,l in re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',s,re.S|re.I)]
def main():
 s=gzip.decompress((S/'county-officials.body.gz').read_bytes()).decode()
 blocks=re.split(r'<div class="card">',s)[1:];inv=[];jobs=[]
 for block in blocks:
  m=re.search(r'<div class="card-header">.*?<a[^>]*>(.*?)</a>',block,re.S)
  if not m:continue
  county=plain(m[1]).replace(' County','');roles=[]
  for col in re.split(r'<div class="col-sm-4"[^>]*>',block)[1:]:
   col=col.split('</p>',1)[0];role=plain(col).split('Address:',1)[0];ll=links(re.sub(r'<!--.*?-->','',col,flags=re.S));roles.append({'role_and_literal_header':role,'links':ll,'source':'county-officials'})
  clerk=[r for r in roles if 'County Clerk' in r['role_and_literal_header']]
  urls=[l['url'] for r in clerk for l in r['links']]
  slug=county.lower().replace(' ','');inv.append({'county':county,'roles':roles,'clerk_links':urls})
  for i,u in enumerate(urls):jobs.append([f'{slug}-clerk-{i}',u,'county-officials'])
 (D/'county-chains.json').write_text(json.dumps(inv,indent=2)+'\n');(S/'county-clerk-jobs.json').write_text(json.dumps(jobs,indent=2)+'\n')
 print(json.dumps({r['county']:r['clerk_links'] for r in inv},indent=2))
if __name__=='__main__':main()

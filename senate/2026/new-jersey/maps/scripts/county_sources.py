from acquire import *
from html import unescape
from concurrent.futures import ThreadPoolExecutor
import re
s=content('directory').decode();counties=[];jobs=[]
for i in range(1,22):
 pat=rf'<div id="collapse{i}".*?(?=<div class="card">|</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>)'
 start=s.index(f'<div id="collapse{i}"');end=s.find('<div class="card">',start+1);chunk=s[start:end if end!=-1 else len(s)]
 title=re.search(r'href="#collapse'+str(i)+r'">\s*([^<]+)',s).group(1).strip();county=title.replace(' County','');roles=[]
 for j,block in enumerate(re.split(r'<div class="col-sm-4"\s*>',chunk)[1:]):
  block=block.split('</div>')[0]
  plain=unescape(re.sub('<[^>]+>',' ',block));plain=' '.join(plain.split());role={'directory_text':plain,'role_position':j,'links':[]}
  for href in re.findall(r'<a[^>]+href="([^"]+)"',block):
   if href.startswith(('mailto:','tel:')):continue
   u=urllib.parse.urljoin('https://www.nj.gov/state/elections/vote-county-election-officials.shtml?os=v',unescape(href));id=f'county-{i:02d}-role-{j}'
   role['links'].append({'url':u,'literal_href':href,'receipt_id':id});jobs.append((id,u,'directory / '+title+' / '+plain[:70],href))
  roles.append(role)
 counties.append({'county':county,'directory_section':i,'roles':roles,'source':'directory'})
assert len(counties)==21 and all(len(x['roles'])==3 for x in counties)
write(BASE/'authority-directory.json',counties)
with ThreadPoolExecutor(max_workers=6) as e:list(e.map(lambda j:fetch(*j),jobs))

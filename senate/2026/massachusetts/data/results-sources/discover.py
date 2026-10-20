"""Resolve bounded research-parent evidence using observed directory domains.
No current geographical/ID match follows from a name/domain correspondence.
"""
from pathlib import Path
from urllib.parse import urlsplit
import hashlib,json,re
O=Path(__file__).resolve().parent;S=O.parents[1]
def expand(n):
 for a,b in [('N. ','North '),('S. ','South '),('E. ','East '),('W. ','West ')]:
  if n.startswith(a):return b+n[len(a):]
 return n
def norm(n):return re.sub('[^a-z0-9]','',n.lower())
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def main():
 lines={}
 for p in [O/'source/directory-web-initial.json',*sorted((O/'source').glob('government-directory-*.json'))]:
  r=json.loads(p.read_text());v=r if isinstance(r,str) else r['response']
  for m in re.finditer(r'\bL(\d+): ?(.*?)(?=\bL\d+:|$)',v,re.S):lines[int(m[1])]=m[2].rstrip('\n')
 text='\n'.join(lines.get(i,'')for i in range(2638));blocks=[]
 for m in re.finditer(r'^### ([^\n]+)\n(.*?)(?=^### |^## |\Z)',text,re.M|re.S):
  domains=re.findall(r'†((?:www\.)?[A-Za-z0-9.-]+\.[a-z]{2,})',m[2]);blocks.append(dict(name=m[1],raw_web_directory_block=m[0],observed_domains=list(dict.fromkeys(x for x in domains if x!='goo.gl')),raw_original_html_status='403; literal hrefs unavailable in extracted web representation',blank_fields_not_repaired=True))
 write(O/'municipal-government-directory.json',dict(source='https://www.sec.state.ma.us/divisions/cis/contact/town-contact.htm',representation='all available numbered web lines reconstructed; not original HTML',line_count=len(lines),missing_lines=[i for i in range(2638)if i not in lines],entries=blocks))
 candidates=[]
 for p in sorted((O/'source/search').glob('municipal-*.json')):
  v=json.loads(p.read_text())
  for m in re.finditer(r'(?m)^([^\n]+) \((https?://[^\n]+)\)\n(.*?)(?=\n-+\n|\Z)',v['response'],re.S):
   candidates.append(dict(title=m[1],url=m[2],search_block=m[0],search_evidence=str(p.relative_to(O)),queries=v['queries']))
 c=json.loads((S/'data/turnout/priority-set.json').read_text());parents=[json.loads(x['municipal_key'])[0] for x in c['all_parent_child_maps']];out=[];jobs=[]
 for i,n in enumerate(parents):
  full=expand(n);d=next((x for x in blocks if norm(x['name'])==norm(full)),None);domains=d['observed_domains'] if d else []
  def score(x):
   host=urlsplit(x['url']).hostname or '';h=host.removeprefix('www.');direct=any(h==z.removeprefix('www.')for z in domains);related=norm(full)in norm(host) and any(t in host for t in ['ma.','ma-','ma.gov','mass'])
   if not direct and not related:return -1
   if any(t in host for t in ['maine','wikipedia','facebook','instagram','twitter','patch.com']):return -1
   t=x['title'].lower();u=x['url'].lower();s=100 if direct else 50
   s+=45*bool(re.search('election.results|election-results|voting.*elections|elections.*voting',t+' '+u));s+=30*bool(re.search('clerk|election commission|registrar',t+' '+u));s-=30*bool(re.search('town_report|town.report|annual.report|annual-report',t+' '+u));s-=20*bool(re.search('2020|2021|2023|2025',t))
   return s
  choices=sorted((x for x in candidates if score(x)>0),key=lambda x:-score(x));uniq=[]
  for x in choices:
   if x['url']not in [y['url']for y in uniq]:uniq.append(x)
  selected=uniq[:2];pkeys=c['ordered_priority_keys'];priority=any(json.loads(k)[0]==n for k in pkeys)
  row=dict(source_parent_literal=n,research_full_name=full,directory=d,candidate_sources=uniq,selected_sources=selected,priority_parent=priority,research_name_correspondence_only=True,current_identity_approved=False)
  out.append(row)
  for j,x in enumerate(selected):jobs.append(dict(id=f'muni-{i:03d}-'+hashlib.sha256(x['url'].encode()).hexdigest()[:12],url=x['url'],parent=x['search_evidence'],literal_href=None,reason='actual search result URL on observed directory/name-qualified municipal domain; evidence attribution only, not current ID'))
 write(O/'municipal-discovery.json',out);write(O/'municipal-requests.json',jobs)
 print(dict(directory_entries=len(blocks),parents=len(out),selected_requests=len(jobs),no_source=[r['source_parent_literal']for r in out if not r['selected_sources']]))
if __name__=='__main__':main()

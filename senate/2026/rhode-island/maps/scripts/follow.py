from acquire import *
import re,concurrent.futures,urllib.parse
class Anchors(HTMLParser):
 def __init__(self,b):super().__init__();self.rows=[];self.current=None;self.feed(b.decode('utf-8','replace'))
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='a' and d.get('href'):self.current={'href':d['href'],'text':''}
 def handle_data(self,s):
  if self.current is not None:self.current['text']+=s
 def handle_endtag(self,t):
  if t=='a' and self.current is not None:self.rows.append(self.current);self.current=None
def anchors(r):
 seen=set();out=[]
 for i,a in enumerate(Anchors(read(r)).rows):
  a=dict(a,position=i,url=urllib.parse.urljoin(last(r)['url'],a['href'].strip()),text=' '.join(a['text'].split()))
  if a['url'] in seen:continue
  seen.add(a['url']);out.append(a)
 return out
def select(r):
 return [a for a in anchors(r) if a['url'].startswith(('http:','https:')) and '#' not in a['href'] and urllib.parse.urlparse(a['url']).hostname not in ['vote.sos.ri.gov','electionresults.ri.gov','www.elections.ri.gov','elections.ri.gov'] and re.search(r'canvass|\belections?\b|\bvot(?:ing|er|e)\b|precinct|polling|\bward\b',a['text']+' '+a['url'],re.I) and not re.search(r'facebook|twitter|instagram|youtube|login|handbook|candidate|register|registration|survey|electric|budget|ballot.*(track|request)|voteref|turnout',a['url']+' '+a['text'],re.I) and not re.search(r'\.(?:jpg|png|gif|js|css)(?:\?|$)',a['url'],re.I)]
def main():
 import sys
 stage=sys.argv[1]
 jobs=[];edges=[]
 paths=sorted((M/'requests').glob('municipal-*.json')) if stage=='one' else sorted((M/'requests').glob('local-one-*.json'))
 for p in paths:
  r=parsed(p)
  if last(r).get('status')!=200 or last(r).get('challenge_observed'):continue
  candidates=select(r)
  # bounded directory pass: 3 election/roster pages; all direct relevant precinct PDF links.
  picked=[a for a in candidates if re.search(r'\.pdf(?:\?|$)',a['url'],re.I) and re.search(r'precinct|polling|ward|voting.?locations',a['url']+' '+a['text'],re.I)]
  pages=[a for a in candidates if a not in picked and not re.search(r'\.pdf(?:\?|$)',a['url'],re.I)]
  picked+=pages[:3]
  for j,a in enumerate(picked):
   name=f'local-{stage}-{p.stem.removeprefix("municipal-").removeprefix("local-one-")}-{j:02}'
   jobs.append((name,a['url'],r['id']));edges.append(dict(id=name,parent=r['id'],**a))
 dump(M/f'source/follow-{stage}-edges.json',edges)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(lambda args:fetch(*args),jobs):print(r['id'],last(r).get('status'),last(r).get('raw_bytes'),flush=True)
if __name__=='__main__':main()

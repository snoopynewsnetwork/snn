#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
from acquire import *
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.text=[];self.active=None;self.base=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="base":self.base=a.get("href")
  if tag in ["a","iframe"] and ("href" in a or "src" in a):
   self.active={"url":a.get("href",a.get("src")),"label":"","tag":tag};self.links.append(self.active)
 def handle_endtag(self,tag):
  if tag=="a":self.active=None
 def handle_data(self,data):
  self.text.append(data)
  if self.active:self.active["label"]+=data
from urllib.parse import urljoin

def run():
 contract=json.loads((ROOT.parent/'data/turnout/priority-set.json').read_text());priority={x['name'] for x in contract['counties'] if x['in_priority']};rows=json.loads((ROOT/'native-scope-inventory.json').read_text());urls=[(r['county'],r['local_urls'][0]) for r in rows if r['county'] in priority]
 def get(pair):
  county,u=pair;name='county-'+county.lower();d=fetch(name,u,parent='native feature Local_Voter_Reg attribute; see native-scope-inventory.json');s=Links();s.feed(body(name).decode(errors='replace'));links=[]
  for a in s.links:
   url=urljoin(urljoin(d.get('final_url',u),s.base or ''),a['url']);label=a['label'].strip()
   if any(x in (url+' '+label).lower() for x in ['precinct','polling','gis','map','boundary','boundaries','2026']):links.append({'url':url,'label':label,'tag':a['tag']})
  txt=' '.join(s.text);(ROOT/'derived'/f'{name}.txt').write_text(txt+'\n');print(county,d['status'],len(links),flush=True);return {'county':county,'capture':name,'requested_url':u,'status':d['status'],'links':links}
 with ThreadPoolExecutor(max_workers=3) as ex:out=list(ex.map(get,urls))
 (ROOT/'county-observed-links.json').write_text(json.dumps(out,indent=2)+'\n')
 for name,urls in [('Beaufort',[r for r in rows if r['county']=='Beaufort'][0]['bills']),('Lancaster',[r for r in rows if r['county']=='Lancaster'][0]['bills'])]:
  for i,url in enumerate(urls):print(fetch('bill-'+name.lower()+str(i),url,parent='native Bill attribute')['status'])
if __name__=='__main__':run()

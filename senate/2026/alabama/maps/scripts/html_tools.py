from html.parser import HTMLParser
from urllib.parse import urljoin
import gzip,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def entity(receipt):
 r=json.loads((ROOT/receipt).read_text())
 if not r.get('entity'):return r,b''
 return r,gzip.decompress(b''.join((ROOT/p['path']).read_bytes() for p in r['entity']['parts']))
class Links(HTMLParser):
 def __init__(self,base):super().__init__(convert_charrefs=True);self.base=base;self.rows=[];self.current=None
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=='base' and d.get('href'):self.base=urljoin(self.base,d['href'])
  if tag=='a' and d.get('href'):
   self.current={'url':urljoin(self.base,d['href']),'href':d['href'],'text':'','tag':self.get_starttag_text(),'line':self.getpos()[0],'column':self.getpos()[1]};self.rows.append(self.current)
 def handle_data(self,data):
  if self.current is not None:self.current['text']+=data
 def handle_endtag(self,tag):
  if tag=='a':self.current=None
def links(receipt):
 r,b=entity(receipt);p=Links(r['final_url'] or r['requested_url']);p.feed(b.decode('utf-8',errors='replace'));return p.rows

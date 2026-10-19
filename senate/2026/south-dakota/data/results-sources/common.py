import json,gzip,pathlib,hashlib
from html.parser import HTMLParser
from urllib.parse import urljoin
ROOT=pathlib.Path(__file__).resolve().parent
STATE=ROOT.parents[1]
def load(id):
 r=json.loads((ROOT/'raw'/f'{id}.receipt.json').read_text());return r,gzip.decompress(b''.join((ROOT/a['path']).read_bytes() for a in r['stored_parts']))
class HTML(HTMLParser):
 def __init__(self,b):
  super().__init__(convert_charrefs=True);self.links=[];self.scripts=[];self.tags=[];self.text=[];self.anchor=None;self.feed(b.decode('utf-8','replace'))
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);self.tags.append((tag,a))
  if tag=='a':self.anchor={'href':a.get('href',''),'text':''};self.links.append(self.anchor)
  if tag=='script' and a.get('src'):self.scripts.append(a['src'])
 def handle_endtag(self,tag):
  if tag=='a':self.anchor=None
 def handle_data(self,d):
  self.text.append(d)
  if self.anchor is not None:self.anchor['text']+=d
 def resolved(self,url):
  base=next((urljoin(url,a['href']) for t,a in self.tags if t=='base' and 'href' in a),url)
  return [{**a,'url':urljoin(base,a['href'])} for a in self.links]
def dump(name,o):(ROOT/name).write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(STATE)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

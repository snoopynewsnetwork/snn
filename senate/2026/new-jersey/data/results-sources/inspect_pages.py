"""Complete passive HTML link/text/script inventories from saved entity bodies."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import json,gzip,re,html
HERE=Path(__file__).resolve().parent
def plain(s):return html.unescape(re.sub('<[^>]+>',' ',s)).strip()
class Page(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=False);self.links=[];self.scripts=[];self.frames=[];self.link=None;self.script=None;self.text=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=='a':self.link={'attributes':attrs,'literal_href':d.get('href'),'text':''};self.links.append(self.link)
  if t=='script':self.script={'attributes':attrs,'literal_src':d.get('src'),'body':''};self.scripts.append(self.script)
  if t in ['iframe','embed','object']:self.frames.append({'tag':t,'attributes':attrs})
 def handle_endtag(self,t):
  if t=='a':self.link=None
  if t=='script':self.script=None
 def handle_data(self,d):
  self.text.append(d)
  if self.link is not None:self.link['text']+=d
  if self.script is not None:self.script['body']+=d
 def handle_entityref(self,n):self.handle_data('&'+n+';')
 def handle_charref(self,n):self.handle_data('&#'+n+';')
def body(r):
 h=r['hops'][-1]
 if h.get('reference_path'):
  b=(HERE.parents[1]/h['reference_path']).read_bytes()
  return gzip.decompress(b) if h.get('reference_gzip',True) else b
 return gzip.decompress((HERE/h['asset']).read_bytes()) if 'asset' in h else b''.join(gzip.decompress((HERE/p['asset']).read_bytes()) for p in h['ordered_exact_entity_parts'])
def inspect(r):
 if not r.get('hops'):return None
 b=body(r)
 if b.startswith(b'%PDF') or b.startswith(b'PK') or b[:3] in [b'\xff\xd8\xff',b'\x89PN']:return None
 if not any(t in b[:2000].lower() for t in [b'<html',b'<!doctype',b'<head']):return None
 s=b.decode('utf-8','replace');parser=Page();parser.feed(s)
 for l in parser.links:
  if l['literal_href']:l['resolved_url']=urljoin(r['final_url'],html.unescape(l['literal_href']))
 return {'request_id':r['id'],'url':r['final_url'],'status':r['status'],'full_links':parser.links,'full_scripts':parser.scripts,'full_embeds':parser.frames,'full_text':''.join(parser.text)}
def main():
 d=HERE/'inspection';d.mkdir(exist_ok=True)
 for p in sorted((HERE/'requests').glob('*.json')):
  r=json.loads(p.read_bytes());o=inspect(r)
  if not o:
   target=d/(p.stem+'.json.gz')
   if target.exists():target.unlink()
  if o:
   z=gzip.compress((json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode(),mtime=0);(d/(p.stem+'.json.gz')).write_bytes(z)
if __name__=='__main__':main()

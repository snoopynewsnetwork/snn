import html.parser,json,sys,urllib.parse
from acquire import body,ROOT
class P(html.parser.HTMLParser):
 def __init__(self):super().__init__();self.base=None;self.links=[];self.cur=None
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='base':self.base=d.get('href')
  if t=='a' and 'href' in d:self.cur={'tag':t,'url':d['href'],'text':''};self.links.append(self.cur)
  if t in ['iframe','script','img','embed','object'] and (d.get('src') or d.get('data')):self.links.append({'tag':t,'url':d.get('src') or d.get('data'),'text':''})
 def handle_endtag(self,t):
  if t=='a':self.cur=None
 def handle_data(self,d):
  if self.cur:self.cur['text']+=d
for k in sys.argv[1:]:
 r=json.loads((ROOT/'raw'/f'{k}.receipt.json').read_text());p=P();p.feed(body(k).decode(r.get('encoding') or 'utf-8',errors='replace'));base=urllib.parse.urljoin(r.get('final_url') or r['request_url'],p.base or '')
 for l in p.links:l['url']=urllib.parse.urljoin(base,l['url']);l['text']=' '.join(l['text'].split())
 (ROOT/'raw'/f'{k}.links.json').write_text(json.dumps({'base':base,'links':p.links},indent=2)+'\n')
 print('\n',k,r['status'])
 for l in p.links:
  if __import__('re').search(r'map|precinct|gis|\.zip|\.pdf|arcgis',l['url']+' '+l['text'],__import__('re').I):print(l)

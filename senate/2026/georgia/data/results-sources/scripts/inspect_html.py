from common import *
import html.parser,re,urllib.parse
class HTML(html.parser.HTMLParser):
 def __init__(self,url):super().__init__(convert_charrefs=True);self.url=url;self.links=[];self.text=[];self.active=None;self.skip=0
 def handle_starttag(self,tag,at):
  a=dict(at)
  if tag=='base' and a.get('href'):self.url=urllib.parse.urljoin(self.url,a['href'])
  if tag in ['script','style']:self.skip+=1
  if tag in ['a','iframe','script','link','form']:
   key={'a':'href','iframe':'src','script':'src','link':'href','form':'action'}[tag]
   if a.get(key):
    self.links.append({'position':len(self.links),'tag':tag,'url':urllib.parse.urljoin(self.url,a[key]),'literal':a[key],'label':'','attributes':a});self.active=len(self.links)-1 if tag=='a' else None
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip=max(0,self.skip-1)
  if t=='a':self.active=None
 def handle_data(self,s):
  if not self.skip:self.text.append(s)
  if self.active is not None:self.links[self.active]['label']+=s
for mp in sorted((ROOT/'raw').glob('*.http.json')):
 r=js(mp)
 if r.get('status') is None:continue
 b=entity(r)
 if b.lstrip().startswith(b'%PDF'):continue
 if not b.lstrip().startswith((b'<!',b'<html',b'<HTML',b'<')):continue
 h=HTML(r['final_url']);h.feed(b.decode('utf-8','replace'))
 for x in h.links:x['label']=' '.join(x['label'].split())
 save(ROOT/'extracts'/(r['id']+'.links.json'),h.links)
 (ROOT/'extracts'/(r['id']+'.txt')).write_text(' '.join(' '.join(h.text).split())+'\n')
 if r.get('role')=='local_parent':
  hits=[x for x in h.links if re.search('result|enr\.|enhancedvoting|2024.*(summary|vote)|2026.*(summary|vote)|election.*histor|election.*archive',x['label']+' '+x['url'],re.I)]
  print(r['id'],[(x['label'][:90],x['url']) for x in hits[:18]])

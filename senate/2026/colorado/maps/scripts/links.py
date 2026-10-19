from html.parser import HTMLParser
from urllib.parse import urljoin
class Links(HTMLParser):
 def __init__(self,s,base):
  super().__init__();self.links=[];self.active=None;self.base=base;self.feed(s)
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='a' and d.get('href'):self.active=[urljoin(self.base,d['href']),'',d['href']]
 def handle_data(self,s):
  if self.active:self.active[1]+=s
 def handle_endtag(self,t):
  if t=='a' and self.active:self.links.append(self.active);self.active=None

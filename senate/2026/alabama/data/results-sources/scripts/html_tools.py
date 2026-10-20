from html.parser import HTMLParser
from urllib.parse import urljoin
import gzip,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class Node:
    def __init__(self,tag='',attrs=(),pos=None):
        self.tag=tag;self.attrs=dict(attrs);self.children=[];self.pos=pos
    def all(self,tag=None,cls=None):
        stack=list(reversed(self.children))
        while stack:
            c=stack.pop()
            if not isinstance(c,Node):continue
            if (tag is None or c.tag==tag) and (cls is None or cls in c.attrs.get('class','').split()):yield c
            stack.extend(reversed(c.children))
    def text(self):
        parts=[];stack=list(reversed(self.children))
        while stack:
            c=stack.pop()
            if isinstance(c,Node):stack.extend(reversed(c.children))
            else:parts.append(c)
        return ''.join(parts)
class Tree(HTMLParser):
    def __init__(self,b):
        super().__init__(convert_charrefs=True);self.root=Node();self.stack=[self.root];self.feed(b.decode('utf-8',errors='replace'))
    def handle_starttag(self,t,a):
        n=Node(t,a,self.getpos());self.stack[-1].children.append(n)
        if t not in VOID:self.stack.append(n)
    def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t)
    def handle_endtag(self,t):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==t:self.stack=self.stack[:i];return
    def handle_data(self,d):self.stack[-1].children.append(d)
def entity(receipt):
    r=json.loads((ROOT/receipt).read_bytes());v=r['hops'][-1]['body']
    b=gzip.decompress(b''.join((ROOT/p['path']).read_bytes() for p in v['parts']))
    return r,b
def receipts():
    return [(str(p.relative_to(ROOT)),json.loads(p.read_bytes())) for p in sorted((ROOT/'http').glob('*.receipt.json'))]
def latest(url):
    return next((n,r) for n,r in reversed(receipts()) if r['requested_url']==url and r['hops'])
def links(receipt):
    r,b=entity(receipt);tree=Tree(b).root;url=r['hops'][-1]['url']
    return [{'url':urljoin(url,a.attrs['href']),'text':a.text(),'attrs':a.attrs,'position':a.pos,
             'parent_receipt':receipt} for a in tree.all('a') if a.attrs.get('href')]

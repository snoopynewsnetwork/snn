"""Small standard-library helpers; all paths are relative to this package."""
from pathlib import Path
from html.parser import HTMLParser
import gzip, hashlib, json
ROOT = Path(__file__).resolve().parent
STATE = ROOT.parent.parent
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(p, x):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n")
def gzwrite(p,b):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gzip.compress(b,mtime=0))
def inputs(): return json.loads((ROOT/'source/inputs/original-receipts.json').read_text())
def original(r):
    b=(ROOT/r['stored_path']).read_bytes()
    assert sha(b)==r['stored_sha256'], r['id']
    raw=gzip.decompress(b) if r.get('compression')=='gzip' else b
    assert sha(raw)==r['raw_sha256'],r['id']
    return raw
class Node:
    def __init__(self,tag='',attrs=(),parent=None): self.tag=tag;self.attrs=dict(attrs);self.parent=parent;self.children=[]
    def text(self): return ''.join(c.text() if isinstance(c,Node) else c for c in self.children)
    def all(self,tag=None):
        for c in self.children:
            if isinstance(c,Node):
                if tag is None or c.tag==tag: yield c
                yield from c.all(tag)
    def has(self,cls): return cls in self.attrs.get('class','').split()
class Tree(HTMLParser):
    def __init__(self,b):
        super().__init__(convert_charrefs=True);self.root=Node();self.stack=[self.root];self.feed(b.decode('utf-8'));self.close()
    def handle_starttag(self,t,a):
        n=Node(t,a,self.stack[-1]);self.stack[-1].children.append(n)
        if t not in ['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']: self.stack.append(n)
    def handle_endtag(self,t):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==t: self.stack=self.stack[:i];break
    def handle_data(self,s):self.stack[-1].children.append(s)
def clean(s): return ' '.join(s.split())
def links(b): return [(clean(a.text()),a.attrs['href']) for a in Tree(b).root.all('a') if 'href' in a.attrs]

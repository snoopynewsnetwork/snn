"""Small dependency-free HTML tree; source attributes remain literal."""
from html.parser import HTMLParser
from urllib.parse import urljoin
class Node:
    def __init__(self,tag='',attrs=(),parent=None):self.tag=tag;self.attrs=dict(attrs);self.parent=parent;self.children=[]
    def all(self,tag=None):
        todo=[self]
        while todo:
            n=todo.pop()
            if tag is None or n.tag==tag:yield n
            todo.extend(c for c in reversed(n.children)if isinstance(c,Node))
    def text(self):return ' '.join(self.literal_text().split())
    def literal_text(self):
        todo=[self];out=[]
        while todo:
            n=todo.pop()
            if isinstance(n,Node):todo.extend(reversed(n.children))
            elif n.strip():out.append(n.strip())
        return ' '.join(out)
class Tree(HTMLParser):
    def __init__(self,s):
        super().__init__(convert_charrefs=True);self.root=Node();self.stack=[self.root];self.feed(s)
    def handle_starttag(self,tag,attrs):
        n=Node(tag,attrs,self.stack[-1]);self.stack[-1].children.append(n)
        if tag not in ['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']:self.stack.append(n)
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs);self.handle_endtag(tag)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:self.stack=self.stack[:i];break
    def handle_data(self,s):self.stack[-1].children.append(s)
def links(s,url):
    out=[]
    for i,n in enumerate(Tree(s).root.all()):
        key='href' if n.tag in ['a','area','link'] else 'src' if n.tag in ['script','iframe','embed'] else None
        if key and n.attrs.get(key):out.append(dict(position=i,tag=n.tag,text=n.text(),attributes=n.attrs,literal_url=n.attrs[key],url=urljoin(url,n.attrs[key])))
    return out

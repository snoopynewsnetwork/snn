from html.parser import HTMLParser
from urllib.parse import urljoin
class Node:
    def __init__(self,tag='',attrs=(),start=0):self.tag=tag;self.attrs=dict(attrs);self.children=[];self.start=start;self.end=None
    def text(self):return ''.join(x.text() if isinstance(x,Node) else x for x in self.children)
    def find(self,tags):
        for c in self.children:
            if isinstance(c,Node):
                if c.tag in tags:yield c
                yield from c.find(tags)
class Tree(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True);self.source=text;self.lines=[0]
        for i,c in enumerate(text):
            if c=='\n':self.lines.append(i+1)
        self.root=Node();self.stack=[self.root];self.feed(text)
    def charoffset(self):l,c=self.getpos();return self.lines[l-1]+c
    def handle_starttag(self,t,a):
        n=Node(t,a,self.charoffset());self.stack[-1].children.append(n)
        if t not in ['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']:self.stack.append(n)
    def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t)
    def handle_endtag(self,t):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==t:
                self.stack[i].end=self.source.find('>',self.charoffset())+1;self.stack=self.stack[:i];break
    def handle_data(self,d):self.stack[-1].children.append(d)
    def links(self,base):
        return [dict(tag=n.tag,attrs=n.attrs,literal=n.attrs.get('href',n.attrs.get('src')),text=n.text(),url=urljoin(base,n.attrs.get('href',n.attrs.get('src',''))),character_offset=n.start)
            for n in self.root.find(['a','script','iframe','link']) if n.attrs.get('href',n.attrs.get('src'))]

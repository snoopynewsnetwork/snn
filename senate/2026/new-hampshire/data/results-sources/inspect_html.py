#!/usr/bin/env python3
"""Lossless originals remain authoritative. Extract links with character offsets and visible text."""
import gzip, html, json, pathlib, re
from html.parser import HTMLParser
from urllib.parse import urljoin
from acquire import ROOT, SOURCE, dump
class Page(HTMLParser):
    def __init__(self,s):
        super().__init__(convert_charrefs=True); self.s=s; self.links=[]; self.text=[]; self.anchor=None; self.hidden=0; self.base=None
        self.starts=[0]+[m.end() for m in re.finditer('\n',s)]
    def handle_starttag(self,t,a):
        d=dict(a)
        if t=='base' and 'href' in d and self.base is None:self.base=d['href']
        if t in ('script','style'): self.hidden+=1
        if t=='a' and 'href' in d:
            line,col=self.getpos(); self.anchor={'href':d['href'],'text':'','character_position':self.starts[line-1]+col}
        if t in ('br','p','div','li','tr','h1','h2','h3','h4'): self.text.append('\n')
    def handle_endtag(self,t):
        if t in ('script','style'): self.hidden=max(0,self.hidden-1)
        if t=='a' and self.anchor:
            self.anchor['text']=' '.join(self.anchor['text'].split()); self.links.append(self.anchor); self.anchor=None
    def handle_data(self,s):
        if not self.hidden: self.text.append(s+' ')
        if self.anchor: self.anchor['text']+=s+' '
def decode_body(m):
    b=gzip.decompress((ROOT/m['body_path']).read_bytes())
    if b.startswith(b'\x1f\x8b'): b=gzip.decompress(b)
    return b
def inspect(sid):
    m=json.loads((SOURCE/(sid+'.json')).read_text()); b=decode_body(m)
    if b.startswith(b'%PDF'): return None
    s=b.decode('utf-8',errors='replace'); p=Page(s); p.feed(s)
    am=re.match(r'https?://web\.archive\.org/web/\d+(?:id_)?/(https?://.*)',m['final_url'])
    original_document_url=am[1] if am else m['final_url']
    document_base=urljoin(original_document_url,p.base) if p.base is not None else original_document_url
    links=[{**a,'url':urljoin(document_base,a['href'])} for a in p.links]
    x={'source_id':sid,'url':m['final_url'],'http_status':m['http_status'],'links':links,
       'text':re.sub(r'\n\s*\n','\n',''.join(p.text)),'decoded_bytes':len(b),'literal_base_href':p.base,'original_document_url':original_document_url,'document_base_url':document_base,'link_resolver_version':2}
    dump(ROOT/'derived'/(sid+'.json'),x); return x
if __name__=='__main__':
    import sys
    for sid in sys.argv[1:]:
        x=inspect(sid); print(sid, len(x['links']) if x else 'PDF')

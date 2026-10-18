"""Small lossless-cell parser; raw HTML remains authoritative."""
from html.parser import HTMLParser
class Tables(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True);self.rows=[];self.row=None;self.cell=None;self.feed(text)
    def handle_starttag(self,t,a):
        if t=='tr': self.row=[]
        elif t in ('td','th'): self.cell=[]
        elif t=='br' and self.cell is not None: self.cell.append(' ')
    def handle_data(self,d):
        if self.cell is not None:self.cell.append(d)
    def handle_endtag(self,t):
        if t in ('td','th') and self.cell is not None:
            if self.row is not None:self.row.append(' '.join(''.join(self.cell).split()))
            self.cell=None
        elif t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None

import sys,json,re,urllib.parse
from html.parser import HTMLParser
from acquire import ROOT,raw
class HTML(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.text=[];self.current=None;self.label='';self.tables=[];self.rows=[];self.row=None;self.cell=None;self.celltext='';self.headers=[]
    def handle_starttag(self,t,a):
        d=dict(a)
        if t=='a':self.current=d.get('href');self.label=''
        if t=='tr':self.row=[]
        if t in ['th','td']:self.cell=t;self.celltext=''
    def handle_data(self,d):
        self.text.append(d)
        if self.current:self.label+=d
        if self.cell:self.celltext+=d
    def handle_endtag(self,t):
        if t=='a' and self.current:self.links.append({'label':self.label.strip(),'href':self.current});self.current=None
        if t in ['td','th'] and self.cell:
            if self.row is not None:self.row.append(self.celltext.strip())
            self.cell=None
        if t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
def html(label):
    p=HTML();p.feed(raw(label).decode('utf-8',errors='replace'));return p
def main():
    mode=sys.argv[1];jobs=[]
    if mode=='county-homes':
        for f in sorted((ROOT/'requests').glob('aac-*.json')):
            label=f.stem
            if label=='aac-counties':continue
            for link in html(label).links:
                u=link['href']
                if u.startswith(('http://','https://')) and link['label'].startswith(('http://','https://','www.')):
                    jobs.append(dict(label='home-'+label[4:],url=u,parent=label+' actual county website anchor'))
    elif mode=='county-offices':
        for f in sorted((ROOT/'requests').glob('home-*.json')):
            r=json.loads(f.read_bytes())
            if r['hops'][-1]['status']!=200:continue
            base=r['hops'][-1]['url'];seen=set();n=0
            for link in html(f.stem).links:
                if re.search(r'election|county\s*clerk|county-clerk|countyclerk',link['label']+' '+link['href'],re.I):
                    u=urllib.parse.urljoin(base,link['href'])
                    if u in seen or not u.startswith(('https://','http://')) or '/admin' in u:continue
                    seen.add(u);n+=1;jobs.append(dict(label='office-'+f.stem[5:]+'-'+str(n),url=u,parent=f.stem+' '+link['label']))
                    if n==4:break
    elif mode=='county-results':
        for f in sorted((ROOT/'requests').glob('office-*.json')):
            r=json.loads(f.read_bytes())
            if r['hops'][-1]['status']!=200:continue
            base=r['hops'][-1]['url'];seen=set();n=0
            for link in html(f.stem).links:
                if re.search(r'results|sample\s*ballot|current.election|2026.general|tally|clarity',link['label']+' '+link['href'],re.I):
                    u=urllib.parse.urljoin(base,link['href'])
                    if u in seen or not u.startswith(('http://','https://')) or any(k in u for k in ['/admin','Registrant','registration']):continue
                    seen.add(u);n+=1;jobs.append(dict(label='result-'+f.stem[7:]+'-'+str(n),url=u,parent=f.stem+' '+link['label']))
                    if n==4:break
    (ROOT/('batch-'+mode+'.json')).write_text(json.dumps(jobs,indent=2)+'\n');print(mode,len(jobs))
if __name__=='__main__':main()

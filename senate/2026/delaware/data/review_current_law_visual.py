"""Bounded independent retained-primary legal/visual qualification review."""
from pathlib import Path
from html.parser import HTMLParser
import gzip,hashlib,json,re
S=Path(__file__).resolve().parents[1];D=S/'data/results-sources'
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
class Text(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.p=[]
 def handle_data(self,v):self.p.append(v)
def source(key):
 r=json.loads((D/'raw'/f'{key}.receipt.json').read_bytes());p=D/r['asset'];b=gzip.decompress(p.read_bytes());assert hashlib.sha256(b).hexdigest()==r['raw_sha256'];h=Text();h.feed(b.decode('utf-8-sig'));t=' '.join(' '.join(h.p).split());return t,dict(receipt=pin(D/'raw'/f'{key}.receipt.json'),body=pin(p),requested_url=r['requested_url'],final_url=r['final_url'],status=r['status'])
def main():
 laws={};items={}
 for key in ['law-c057','law-c055','hb444','hb444-engrossed','sb266-session','sb329','results','primary']:
  if not (D/'raw'/f'{key}.receipt.json').is_file():continue
  text,row=source(key);items[key]=row;laws[key]=text
 t=laws['law-c057'];assert all(x in t for x in ['Superior Court','5708','5713','1,000','0.5%'] )or all(x in t for x in ['Superior Court','5708','5713','1,000','one half of one percent'])
 assert 'second day after the general election'in t and '10 a.m.'in t and 'President of the Senate'in t
 t=laws['law-c055'];assert 'before the polls close'in t or 'before the polls are closed'in t or 'before the closing of the polls'in t
 assert '30 days'in t and '5509A'in t
 t=laws.get('hb444-engrossed','');assert 'July 1, 2027'in t
 assert 'PR2026.html'in gzip.decompress((D/'raw/results.body.gz').read_bytes()).decode()
 views=[dict(image=pin(D/'previews/calendar-p9.png'),page=9,actual_coordinator_observation='Whole page viewed: Eastern local calendar, November3 7am-8pm, receipt at8pm, November5 SuperiorCourt10am; informational and subject to law changes.'),dict(image=pin(D/'previews/recent-absentee-opinion-p20.png'),page=20,actual_coordinator_observation='Whole conclusion page viewed: permanent-absentee provision upheld and Chancery judgment affirmed; not a holding on every election-law issue.')]
 out=dict(status='pass_bounded_primary_and_selected_original_visual_review',retained_complete_sources=items,independently_rechecked_primary_pages=['https://delcode.delaware.gov/title15/c057/index.html','https://delcode.delaware.gov/title15/c055/index.html','https://legis.delaware.gov/BillDetail?LegislationId=143415','https://elections.delaware.gov/results/index.html'],actual_coordinator_views=views,no_additional_browser_render_claim=True,qualification='Code sections, bill effective dates and bounded holdings only; no exhaustive later signed ballot/law/docket/tie remedy/current ID/feed/geometry approval. Full existing worker originals remain unchanged.')
 p=S/'data/coordinator-current-law-visual-review.json';p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(pin(p))
if __name__=='__main__':main()

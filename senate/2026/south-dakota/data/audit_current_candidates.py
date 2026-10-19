"""Preserve source-scoped current Senate candidate status, not results IDs."""
from pathlib import Path
from html.parser import HTMLParser
import gzip,hashlib,json,re
ROOT=Path(__file__).resolve().parent.parent
D=ROOT/'data/news';m=json.loads((D/'manifest.json').read_text());r=next(x for x in m if x['id']=='sos-general-candidate-list');stored=(D/r['asset']).read_bytes();raw=gzip.decompress(stored)
assert hashlib.sha256(stored).hexdigest()==r['stored_sha256'] and hashlib.sha256(raw).hexdigest()==r['raw_sha256'] and r['status']==200
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t=='tr':self.row=[]
  elif t in ('td','th') and self.row is not None:self.cell=[]
 def handle_data(self,s):
  if self.cell is not None:self.cell.append(s)
 def handle_endtag(self,t):
  if t in ('td','th') and self.cell is not None:
   self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
  elif t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
p=Tables();p.feed(raw.decode());rows=[]
for i,row in enumerate(p.rows,1):
 if row and row[0]=='United States Senator':
  rows.append({'source_TR_ordinal':i,'source_visible_fields':row[:7], 'status':next(x for x in row if x in ['Active','Withdrawn'])})
assert len(rows)==3
names=[x['source_visible_fields'][1] for x in rows]
assert any('Julian Beaudion' in x and 'Withdrawn 08/04/2026' in x for x in names)
assert any('Brian L Bengs'==x for x in names) and any('Mike Rounds'==x for x in names)
assert [x['source_visible_fields'][2] for x in rows]==['DEM','IND','REP']
assert [x['status'] for x in rows]==['Withdrawn','Active','Active']
result={'status':'source_scoped_current_candidate_preflight','source':{'url':r['url'],'raw_sha256':r['raw_sha256'],'stored_sha256':r['stored_sha256'],'asset':'data/news/'+r['asset'],'retrieved_utc':r.get('retrieved_at_utc')},'Senate_rows':rows,'scope':'Captured public general candidate-list first page contains these three Senate rows before House/other offices. Bengs IND and Rounds REP remain active; Beaudion DEM is marked withdrawn August4. Historical Bengs2022 DEM identity is separate. No final physical-ballot/eligible-write-in universe, unique ENR choices, or current count admission inferred.'}
(ROOT/'data/coordinator-candidate-preflight.json').write_text(json.dumps(result,indent=2)+'\n');print('pass: three source-scoped Senate status rows')

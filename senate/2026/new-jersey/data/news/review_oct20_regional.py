"""Independent primary newsroom response/schema audit; no November admission."""
from pathlib import Path
from html.parser import HTMLParser
import gzip,hashlib,json
S=Path(__file__).resolve().parents[2];O=S/'data/news/coordinator-oct20-regional'
def sha(b):return hashlib.sha256(b).hexdigest()
class Page(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.frames=[];self.text=[]
 def handle_starttag(self,t,a):
  if t=='iframe':self.frames.append(dict(a))
 def handle_data(self,s):self.text.append(s)
def main():
 rows=[]
 for p in sorted(O.glob('acquisition-batch*.json')):rows+=json.loads(p.read_bytes())
 assert len(rows)==len({r['id']for r in rows})==8;by={r['id']:r for r in rows};checked=[];parsers={}
 for r in rows:
  for v in r['redirects']+[r]:
   b=(S/v['asset_path']).read_bytes();assert len(b)==v['stored_bytes']<40000000 and sha(b)==v['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==v['raw_bytes']and sha(raw)==v['raw_sha256'];checked.append({k:v[k]for k in ['asset_path','stored_bytes','stored_sha256','raw_bytes','raw_sha256','status']})
  h=Page();h.feed(raw.decode('utf-8-sig',errors='replace'));parsers[r['id']]=h
 r=by['whyy-nj-primary-results'];h=parsers[r['id']];ap=[x for x in h.frames if 'apelections'in x.get('src','')];assert len(ap)==22;assert all(x['title']=='Live election results via the Associated Press'for x in ap);text=' '.join(' '.join(h.text).split());assert '2026 primary'in text and 'June 2, 2026'in text
 assert ap[0]['src']==by['whyy-actual-primary-senate-embed']['url'];assert by['whyy-actual-primary-senate-embed']['status']==403
 assert by['cape-herald-home']['status']==403 and by['press-local-politics']['status']==200 and by['whyy-nj-voter-guide']['status']==200
 out=dict(status='pass_bounded_regional_primary_source_review',complete_requests=len(rows),HTTP200=sum(r['status']==200 for r in rows),HTTP403=sum(r['status']==403 for r in rows),exact_complete_entities=checked,actual_primary_AP_layouts=ap,primary_senate_AP_layout=ap[0]['src'],independent_count_supplier=False,November_count_admitted=False,measured_cadence_established=False,scope='WHYY actual primary-page AP layouts and current voter guide; Press of Atlantic City actual home/politics200; Cape May Herald403. These do not prove November numeric coverage or independent vote supply. No CAPTCHA/challenge bypass, outreach or collector.')
 p=O/'review.json';p.write_text(json.dumps(out,indent=2)+'\n');print(dict(path=str(p.relative_to(S)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()),requests=len(rows)))
 manifest=O/'acquisition-complete-v1.json';body=json.dumps(rows,indent=2)+'\n'
 if manifest.exists():assert manifest.read_text()==body
 else:manifest.write_text(body)
if __name__=='__main__':main()

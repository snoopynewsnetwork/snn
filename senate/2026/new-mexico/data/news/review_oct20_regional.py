"""Independent bounded regional publisher body/redirect audit; not vote admission."""
from pathlib import Path
from html.parser import HTMLParser
import gzip,hashlib,json
S=Path(__file__).resolve().parents[2];O=S/'data/news/coordinator-oct20-regional'
def sha(b):return hashlib.sha256(b).hexdigest()
class Page(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.t=[];self.frames=[];self.times=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='iframe':self.frames.append(d)
  if t=='time':self.times.append(d)
 def handle_data(self,s):self.t.append(s)
def main():
 rows=[]
 for p in sorted(O.glob('acquisition-batch*.json')):rows+=json.loads(p.read_bytes())
 assert len(rows)==len({r['id']for r in rows})==6;by={r['id']:r for r in rows};observations=[]
 for r in rows:
  bodies=[]
  for step in r['redirects']+[r]:
   z=(S/step['asset_path']).read_bytes();raw=gzip.decompress(z);assert len(z)==step['stored_bytes']<40000000 and sha(z)==step['stored_sha256'];assert len(raw)==step['raw_bytes']and sha(raw)==step['raw_sha256'];bodies.append({k:step[k]for k in ['url','status','asset_path','stored_bytes','stored_sha256','raw_bytes','raw_sha256']})
  h=Page();h.feed(raw.decode('utf-8-sig',errors='replace'));text=' '.join(' '.join(h.t).split());observations.append(dict(id=r['id'],url=r['url'],final_url=r['final_url'],status=r['status'],complete_response_entities=bodies,literal_time_attributes=h.times,all_iframe_attributes=h.frames,raw_primary_headline=r.get('title'),article_text_contains_2026_primary='2026 primary'in text.lower()))
 assert by['roswell-record-home']['status']==403;assert by['farmington-times-home']['final_url']=='https://www.tricityrecordnm.com/'and len(by['farmington-times-home']['redirects'])==2
 assert by['abqjournal-primary-results']['status']==200 and '2026 primary'in by['abqjournal-primary-results']['title'].lower();assert by['santafe-election-link']['status']==by['tricity-election-link']['status']==200
 out=dict(status='pass_bounded_regional_primary_response_review',complete_requests=6,complete_response_entities=sum(len(r['redirects'])+1 for r in rows),HTTP200=5,HTTP403=1,observations=observations,November_counts_admitted=False,measured_cadence_established=False,unknown_supplier_not_assumed_independent=True,qualification='Current regional reporting/guide accessibility and one actualJune-primary static results article only. daily-times.com redirects to TriCityRecord; no independent continued FarmingtonDailyTimes publisher or November scoreboard inferred. SantaFe guide/YouTube/Issuu do not establish vote supply. CompleteRoswell403 retained. No actualNovember counts, statewide regional numeric coverage, exactremaining or calibratedprobability admitted.')
 p=O/'review.json';p.write_text(json.dumps(out,indent=2)+'\n');body=json.dumps(rows,indent=2)+'\n';p=O/'acquisition-complete-v1.json'
 if p.exists():assert p.read_text()==body
 else:p.write_text(body)
 print(dict(review_bytes=(O/'review.json').stat().st_size,review_sha256=sha((O/'review.json').read_bytes()),requests=6,response_entities=out['complete_response_entities']))
if __name__=='__main__':main()

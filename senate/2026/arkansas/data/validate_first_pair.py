"""Reviewed original first-pair publication guard; no full-state/current approval."""
from pathlib import Path
import gzip,hashlib,json,re,sys,urllib.parse
S=Path(__file__).resolve().parents[1];D=S/'data'
def read(p):return json.loads(p.read_bytes())
def pin(p):
 b=p.read_bytes();return{'path':str(p.resolve().relative_to(S.resolve())),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main(check):
 seals=[];count=0
 for role,n,extra in [('turnout',1027,['turnout.md','data/county-turnout.csv']),('baselines',313,['county-partisanship.md','data/county-baselines.csv'])]:
  root=D/role;m=read(root/'asset-manifest.json');rows=m['assets'];actual={str(p.relative_to(S))for p in root.rglob('*')if p.is_file()and p!=root/'asset-manifest.json'}|set(extra)
  assert len(rows)==len({r['path']for r in rows})==n and actual=={r['path']for r in rows}
  for r in rows:assert pin(S/r['path'])==r and r['bytes']<40000000;count+=1
  seals.append({'role':role,'manifest':pin(root/'asset-manifest.json'),'targets':n})
 originals=[]
 for r in read(D/'turnout/source/original-pins.json'):
  p=Path(r['shared_original_path']);stored=p.read_bytes();raw=gzip.decompress(stored)
  assert hashlib.sha256(stored).hexdigest()==r['stored_sha256']and hashlib.sha256(raw).hexdigest()==r['raw_sha256']and len(raw)==r['bytes'];originals.append(pin(p))
 c=read(D/'turnout/priority-set.json');assert len(c['full_order'])==2841 and len(c['ordered_priority_keys'])==1056 and len(c['remainder_keys'])==1785 and len(c['all75parents'])==75 and len(c['priority_parent_fips'])==68
 assert c['statistics']['denominator']==1182676 and c['statistics']['integer_threshold']==946141 and c['statistics']['preceding_votes']==946007 and c['statistics']['minimum80_votes']==946377 and c['statistics']['top15_votes']==40031
 reviews=['coordinator-turnout-original-review.json','coordinator-baseline-original-review.json','coordinator-baseline-math-review.json','coordinator-baseline-cli-review.json','coordinator-first-pair-history-review.json']
 for f in reviews:assert read(D/f)['status'].startswith('pass')
 links=0
 for p in [S/'README.md',S/'research-review.md',S/'research-dispatch.md',S/'turnout.md',S/'county-partisanship.md']+list((D/'turnout').rglob('*.md'))+list((D/'baselines').rglob('*.md')):
  for u in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)',p.read_text()):
   u=u.split(' "')[0].strip('<>');x=urllib.parse.urlsplit(u)
   if x.scheme or x.netloc or not x.path:continue
   assert(p.parent/urllib.parse.unquote(x.path)).exists(),(p,u);links+=1
 out={'status':'pass_reviewed_original_first_pair_historical_measurement_and_conditional_scenarios','actual_finished_workers':2,'whole_four_question_state_complete':False,'seals':seals,'exact_producer_targets':count,'complete_shared_originals':originals,'source_turnout_checks':613570,'source_baseline_checks':1212814,'math_checks':1517309,'actual_independent_CLI_cases':73,'expected_invalid':62,'history_checks':178,'native2024':2841,'all_parents':75,'priority_parents':68,'priority':1056,'remainder':1785,'reported_votes':1182676,'top15_votes':40031,'integer80threshold':946141,'prefix_votes':946377,'preceding_votes':946007,'baseline_native_source_contest_rows':23749,'baseline_county_source_contest_rows':675,'source_models':29,'state_targets':58,'unit_targets':83690,'local_Markdown_links':links,'same_turnout_final_peer_reciprocal_pending':True,'producer_flags_untouched':True,'current_geographic_legal_feed_eligible_WI_probability_approved':False,'reviews':[pin(D/f)for f in reviews]}
 body=(json.dumps(out,indent=2)+'\n').encode();p=D/'coordinator-first-pair-validation.json'
 if check:assert p.read_bytes()==body
 else:p.write_bytes(body)
 print(json.dumps({'status':out['status'],'exact_targets':count,'proof':pin(p)}))
if __name__=='__main__':main('--check'in sys.argv)

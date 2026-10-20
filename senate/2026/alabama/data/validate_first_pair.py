"""Validate reviewed original first-pair component, no full-state acceptance."""
from pathlib import Path
import gzip,hashlib,json,re,sys,urllib.parse
S=Path(__file__).resolve().parents[1];D=S/'data'
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(S)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_bytes())
def main(check):
 seals=[];n=0
 for role,count,extra in [('turnout',145,['turnout.md','data/county-turnout.csv']),('baselines',306,['county-partisanship.md','data/county-baselines.csv'])]:
  root=D/role;m=read(root/'asset-manifest.json');actual={str(p.relative_to(S))for p in root.rglob('*')if p.is_file()and p!=root/'asset-manifest.json'}|set(extra)
  assert len(m['assets'])==len({r['path']for r in m['assets']})==count and actual=={r['path']for r in m['assets']}
  for r in m['assets']:assert pin(S/r['path'])==r and r['bytes']<40000000;n+=1
  seals.append({'role':role,'manifest':pin(root/'asset-manifest.json'),'exact_owned_targets':count})
 original=read(D/'turnout/asset-manifest.json')['external_originals'];pins=[]
 for r in original:
  p=S.parents[2]/r['path'];b=p.read_bytes();raw=gzip.decompress(b)
  assert len(b)==r['stored_bytes']and hashlib.sha256(b).hexdigest()==r['stored_sha256']and len(raw)==r['original_bytes']and hashlib.sha256(raw).hexdigest()==r['original_sha256']
  pins.append(pin(p))
 c=read(D/'turnout/priority-set.json');assert len(c['units'])==2085 and len(c['parents'])==67 and len(c['ordered_priority_keys'])==887 and len(c['remainder_keys'])==1198
 assert c['coverage']['denominator']==2265090 and c['coverage']['top15_votes']==115428 and c['coverage']['minimum80_votes']==1812818 and c['coverage']['preceding_votes']==1811981
 assert not c['coordinator_acceptance']and not c['independent_peer_agreement']
 reviews=['coordinator-first-pair-original-review.json','coordinator-baseline-math-review.json','coordinator-baseline-cli-review.json','coordinator-first-pair-history-review.json']
 for name in reviews:assert read(D/name)['status'].startswith('pass')
 links=0
 for p in [S/'README.md',S/'research-review.md',S/'research-dispatch.md',S/'turnout.md',S/'county-partisanship.md']+list((D/'turnout').rglob('*.md'))+list((D/'baselines').rglob('*.md')):
  for u in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)',p.read_text()):
   u=u.split(' "')[0].strip('<>');x=urllib.parse.urlsplit(u)
   if x.scheme or x.netloc or not x.path:continue
   assert(p.parent/urllib.parse.unquote(x.path)).exists(),(p,u);links+=1
 result={'status':'pass_reviewed_original_first_pair_historical_source_and_conditional_scenarios','actual_finished_question_workers':2,'four_question_state_complete':False,'producer_seals':seals,'exact_producer_targets':n,'complete_shared_originals':pins,'original_source_checks':7249699,'math_checks':390250,'history_checks':44474,'actual_independent_CLI_cases':75,'expected_invalid_CLI':65,'all_native_baseline_records':6270,'all_county_year_records':201,'native2024':2085,'parents':67,'native_priority':887,'native_remainder':1198,'reported2024_marks':2265090,'top15':115428,'integer80threshold':1812072,'preceding_marks':1811981,'prefix_marks':1812818,'local_Markdown_links':links,'same_turnout_final_peer_reciprocal_pending_real_slot':True,'source_and_producer_mutation':False,'coordinator_current_legal_geography_feed_eligible_WI_live_probability_approval':False,'review_proofs':[pin(D/name)for name in reviews]}
 body=(json.dumps(result,indent=2)+'\n').encode();p=D/'coordinator-first-pair-validation.json'
 if check:assert p.read_bytes()==body
 else:p.write_bytes(body)
 print(json.dumps({'status':result['status'],'targets':n,'validation':pin(p)}))
if __name__=='__main__':main('--check'in sys.argv)

#!/usr/bin/env python3
"""Read-only comparison against separately extracted partisanship peer outputs."""
from pathlib import Path
import csv,gzip,hashlib,json
from fractions import Fraction
R=Path(__file__).resolve().parents[1];D=R.parent
P={'county':D/'county-baselines.csv','candidate_method':D/'baselines/candidate-methods.csv.gz','native':D/'baselines/native-baselines.csv.gz'}
def rows(p):
 with (gzip.open(p,'rt')if p.suffix=='.gz'else p.open())as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def val(x):return ''if x is None else str(x)
diffs=[];n=0
ours=[]
for fn,method in [('candidate-votes.csv.gz',False),('candidate-method-votes.csv.gz',True)]:
 for r in rows(R/fn):
  row={'election_key':r['election_key'],'county_fips':r['county_fips'],'unit_level':'native_precinct'if r['unit_level']=='precinct'else r['unit_level'],'source_pointer':r['method_pointer']if method else r['source_pointer'],'native_GUID':r['unit_id'],'native_name':r['unit_name'],'candidate_GUID':r['option_id'],'nativeId':r['candidate_native_id'],'candidate_ordinal':r['option_position'],'candidate_name':r['candidate_name'],'party':r['party_abbreviation'],'isWriteIn':r['is_write_in'],'isQualifiedWriteIn':r['is_qualified_write_in'],'group_GUID':r['method_id']if method else '', 'group_name':r['method_name']if method else 'TOTAL','group_ordinal':r['method_position']if method else '-1','votes':r['method_votes']if method else r['votes']}
  ours.append(row)
def key(r):return (r['election_key'],r['county_fips'],r['unit_level'],r['source_pointer'])
op={key(r):r for r in ours};prs=rows(P['candidate_method']);pp={key(r):r for r in prs}
assert len(op)==len(ours) and len(pp)==len(prs)
assert set(op)==set(pp),(len(op),len(pp),len(set(op)-set(pp)),len(set(pp)-set(op)))
fields=['native_GUID','native_name','candidate_GUID','nativeId','candidate_ordinal','candidate_name','party','isWriteIn','isQualifiedWriteIn','group_GUID','group_name','group_ordinal','votes']
for k,a in op.items():
 b=pp[k]
 for f in fields:
  av=a[f];bv=b[f]
  if f.endswith('GUID'):av=av.lower();bv=bv.lower()
  n+=1
  if av!=bv:diffs.append({'key':k,'field':f,'ours':av,'peer':bv})
# Independently compare whole-county volumes, raw counts and available controls.
oc={(r['election_key'],r['county_fips']):r for r in rows(R/'county-controls.csv')};pc={(r['election_key'],r['county_fips']):r for r in rows(P['county'])};assert set(oc)==set(pc)
for k,a in oc.items():
 b=pc[k]
 for of,pf in [('county_source_all_option_votes','source_alloption_votes'),('state_summary_option_votes','named_valid_option_votes'),('additional_county_option_votes','void_option_votes'),('ballots_cast_usable','ballots_cast'),('registration_total_usable','registered_voters'),('under_votes_source','underVoteCount'),('over_votes_source','overVoteCount')]:
  av=a[of];bv=b[pf];n+=1
  if (Fraction(av)if av else None)!=(Fraction(bv)if bv else None):diffs.append({'key':k,'field':of,'ours':av,'peer':bv})
on={(r['election_key'],r['county_fips'],r['native_id']):r for r in rows(R/'native-units.csv')};pn={(r['election_key'],r['county_fips'],r['native_GUID']):r for r in rows(P['native'])};assert set(on)==set(pn)
for k,a in on.items():
 b=pn[k]
 for of,pf in [('source_all_option_votes','source_voteTotal'),('state_summary_option_votes','named_valid_option_votes'),('ballots_cast_source','ballots_cast'),('voter_registration_source','registered_voters'),('under_votes_source','underVoteCount'),('over_votes_source','overVoteCount')]:
  av=a[of];bv=b[pf];n+=1
  if (Fraction(av)if av else None)!=(Fraction(bv)if bv else None):diffs.append({'key':k,'field':of,'ours':av,'peer':bv})
orders={};ranks=json.loads((R/'rankings.json').read_text())
for eid,v in ranks.items():
 rs=[r for r in pc.values()if r['election_key']==eid];rs.sort(key=lambda r:(-int(r['named_valid_option_votes']),r['county_fips']));order=['GA:county:'+r['county_fips']for r in rs];total=sum(int(r['named_valid_option_votes'])for r in rs);cum=0;cross=None
 for i,r in enumerate(rs,1):
  cum+=int(r['named_valid_option_votes'])
  if cross is None and 5*cum>=4*total:cross=i;crossvotes=cum;prior=cum-int(r['named_valid_option_votes'])
 assert order==v['ordered_keys'];assert total==v['denominator'];assert cross==v['minimum_count'];assert crossvotes==v['priority_votes'];assert prior==v['preceding_votes'];assert sum(int(r['named_valid_option_votes'])for r in rs[:15])==v['top15_votes'];n+=165
 orders[eid]={'all159_order_agrees':True,'minimum_count':cross,'priority_votes':crossvotes,'preceding_votes':prior}
# Compare all known native candidate/method lower bounds and null counts by original source positions.
pr=json.loads((D/'baselines/extraction-checks.json').read_text())['native_residuals'];pr={(r['kind'],r['source_id'],r['pointer']):r for r in pr}
for fn,kind in [('native-candidate-controls.csv','native_candidate_sum'),('native-method-controls.csv','native_candidate_method_sum')]:
 for r in rows(R/fn):
  cands=[v for v in ours if v['unit_level']=='county'and v['election_key']==r['election_key']and v['county_fips']==r['county_fips']and v['candidate_name']==r['candidate_name']]
  c=next(v for v in cands if v['group_name']==(r.get('method_name')or'TOTAL'))
  pointer=c['candidate_GUID']+('/'+c['group_GUID']if kind.endswith('method_sum')else'');b=pr[(kind,r['source_id'],pointer)];known=int(r.get('native_known_sum',r.get('native_observed_method_sum')))
  assert known==b['known_sum']and int(r['native_null_cells'])==b['missing_cells']and int(r['county_minus_known_sum'])==b['unallocated_residual'];n+=3
result={'status':'pass'if not diffs else'fail','peer_agent_id':'9081a355-f2cc-4c66-8b2e-dbdf11066aa7','comparison':'independent extraction of same original primary bytes; count agreement is not independent original publication or legal priority acceptance','peer_inputs':{k:{'path':str(p.relative_to(D.parent)),'sha256':sha(p),'bytes':p.stat().st_size}for k,p in P.items()},'source_position_candidate_method_rows_compared':len(op),'field_comparisons':n,'county_rows_compared':len(oc),'native_rows_compared':len(on),'null_candidate_cells':sum(r['votes']==''for r in ours if r['unit_level']=='native_precinct'and r['group_name']=='TOTAL'),'null_method_cells':sum(r['votes']==''for r in ours if r['unit_level']=='native_precinct'and r['group_name']!='TOTAL'),'rankings':orders,'differences':diffs,'full_candidate_priority':'unresolved858qualified-write-inallocation; no acceptance'}
(R/'peer-agreement.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert not diffs

#!/usr/bin/env python3
"""Offline bounded pair arithmetic; plurality remains a separate full-field check."""
import argparse,csv,gzip,json,math
from pathlib import Path
from extract import D,save,csvout
def load(name):
 b=(D/name).read_bytes();return json.loads(gzip.decompress(b)if name.endswith('.gz')else b)
def clip(x):return min(1.,max(0.,x))
def threshold(q,pool):
 if pool<=0:return 'no_positive_pool'
 if q<0:return 'already_secured_under_fixed_assumptions'
 if q>1:return 'impossible_under_fixed_assumptions'
 return 'feasible'
def solve(rows,target_margin):
 if any(r['pair_votes']is None or(r['pair_votes']>0 and r['share']is None)for r in rows):return dict(status='unknown_preference_or_pair_pool',shift=None,unbounded_shift=None)
 T=sum(r['pair_votes']for r in rows)
 if T<=0:return dict(status='no_positive_pool',shift=None,unbounded_shift=None)
 M=sum(r['pair_votes']*(2*r['share']-1)for r in rows if r['pair_votes']>0);target=target_margin*T;unbounded=(target-M)/(2*T)
 if abs(target)>T+1e-8:return dict(status='impossible_bounded_target',shift=None,unbounded_shift=unbounded)
 lo=-1.;hi=1.
 for _ in range(100):
  mid=(lo+hi)/2;net=sum(r['pair_votes']*(2*clip(r['share']+mid)-1)for r in rows if r['pair_votes']>0)
  if net<target:lo=mid
  else:hi=mid
 delta=(lo+hi)/2
 return dict(status='feasible',shift=delta,unbounded_shift=unbounded,total_pair=T,baseline_net=M,target_net=target,achieved_net=sum(r['pair_votes']*(2*clip(r['share']+delta)-1)for r in rows if r['pair_votes']>0),clipped_units=sum(not 0<=r['share']+delta<=1 for r in rows if r['pair_votes']>0),baseline_already_wins=M>0,minimum_nonnegative_improvement=max(0.,delta))
def selected(rows,index,target_margin=0,others_shift=0):
 if any(r['pair_votes']is None or(r['pair_votes']>0 and r['share']is None)for r in rows):return dict(status='unknown_preference_or_pool',required_share=None)
 T=sum(r['pair_votes']for r in rows);r=rows[index];t=r['pair_votes'];other=sum(q['pair_votes']*(2*clip(q['share']+others_shift)-1)for j,q in enumerate(rows)if j!=index and q['pair_votes']>0)
 if t<=0:return dict(status='no_positive_pool',required_share=None,fixed_other_net=other)
 q=(t+target_margin*T-other)/(2*t)
 return dict(status=threshold(q,t),required_share=q,clipped_display_share=clip(q),fixed_other_net=other,other_share_shift_pp=others_shift*100)

PAIRS={
 '2024-president':('Kamala D. Harris','Donald J. Trump'),
 '2020-senate-II':('Paulette Jordan','Jim Risch'),
 '2020-president':('Joseph R. Biden','Donald J. Trump'),
 '2022-senate-III':('David Roth','Mike Crapo'),
 '2022-governor':('Stephen Heidt','Brad Little'),
 '2020-Fleming-Risch':('Natalie M Fleming','Jim Risch'),
 '2022-Cleveland-Crapo':('Scott Oh Cleveland','Mike Crapo'),
 'current-Achilles-Risch':('Todd Achilles','Jim Risch'),
 'current-Fleming-Risch':('Natalie M Fleming','Jim Risch'),
 'current-Loesby-Risch':('Matt Loesby','Jim Risch'),
}
def pair_record(u,pairid):
 an,bn=PAIRS[pairid];by={c['name'].strip():c for c in u['candidates']};current=pairid.startswith('current-')
 anchorA,anchorB=PAIRS['2024-president']if current else(an,bn)
 a=by[anchorA];b=by[anchorB];A=a['votes'];B=b['votes'];complete=all(c['votes']is not None for c in u['candidates']);known=sum(c['votes']for c in u['candidates']if c['votes']is not None);V=known if complete else None;T=None if A is None or B is None else A+B;s=A/T if T else None
 county=u['county']if u['county'].endswith(' County')else u['county']+' County'
 others=({n:.5 for n in ["Todd Achilles","Natalie M Fleming","Matt Loesby"]if n!=an}if current else({c["name"]:c["votes"]/(V-T)for c in u["candidates"]if c["name"].strip()not in [an,bn]}if V is not None and T is not None and V>T else{}if V is not None and T is not None else None))
 return dict(pair_id=pairid,anchor_contest=u['contest'],year=u['year'],scope=u['scope'],unit_id=u['unit_id']+(':'+pairid if pairid!=u['contest']else''),source_unit_id=u['unit_id'],county=county,literal_unit=u['label'],source_id=u['source_id'],archive_member=u['archive_member'],worksheet=u['worksheet'],source_row=u['row'],method_literal=u['method_label_evidence'],candidate_A=an,candidate_B=bn,party_A='IND'if pairid.startswith(('current-Achilles','current-Fleming'))else'LIB'if pairid.startswith('current-Loesby')else a['party'],party_B='REP'if current else b['party'],anchor_A_votes=A,anchor_B_votes=B,pair_votes=T,all_candidate_known_sum=known,all_candidate_votes=V,all_candidate_complete=complete,other_votes=None if V is None or T is None else V-T,pair_participation=None if not V or T is None else T/V,A_share=s,pair_margin_pp=None if s is None else 100*(2*s-1),all_vote_margin_pp=None if not V or A is None or B is None else 100*(A-B)/V,net_A_minus_B=None if A is None or B is None else A-B,net_gain_for_1pp_A_share=None if T is None else .02*T,winner=None if A is None or B is None else(an if A>B else bn if B>A else'tie'),basis='TRANSPORTED historical Harris-Trump preference/participation assumption, NOT current candidate votes/effects'if current else'observed source counts; no null fill',other_candidate_fractions_json=json.dumps(others,sort_keys=True),share=s)

def build():
 units=load('source/native-units.json.gz');controls=[u for u in load('source/controls.json.gz')if u['scope']=='county'];fips=load('source/county-fips.json');rows=[]
 for pairid in PAIRS:
  contest='2024-president'if pairid.startswith('current-')else'2020-senate-II'if pairid=='2020-Fleming-Risch'else'2022-senate-III'if pairid=='2022-Cleveland-Crapo'else pairid
  for u in units+controls:
   if u['contest']==contest:
    r=pair_record(u,pairid);r['county_fips']=fips[r['county']];rows.append(r)
 # Full candidate controls retain actual identities separately from all pair views.
 candidate_rows=[]
 for u in units+controls:
  for c in u['candidates']:
   candidate_rows.append(dict(contest=u['contest'],scope=u['scope'],unit_id=u['unit_id'],county=u['county'],literal_unit=u['label'],candidate_key=c['key'],literal_candidate=c['header_literal'],county_candidate_name=c['name'],literal_party=c['party'],votes=c['votes'],source_id=u['source_id'],archive_member=u['archive_member'],worksheet=u['worksheet'],source_row=c['source_row'],cell=c['cell']))
 csvout('complete-candidate-baselines.csv.gz',candidate_rows)
 csvout('../county-baselines.csv',[{k:v for k,v in r.items()if k!='share'}for r in rows if r['scope']=='county'])
 csvout('native-baselines.csv.gz',[{k:v for k,v in r.items()if k!='share'}for r in rows if r['scope']=='native'])
 # Historical volume/mix settings, all-candidate totals, no 2026 projection.
 settings=[dict(id='priority_repeat_2024',volume_contest='2024-president',label='priority historical repeat'),dict(id='historical_low_2022',volume_contest='2022-senate-III',label='observed low volume and county mix'),dict(id='historical_base_2020',volume_contest='2020-senate-II',label='observed intermediate volume and county mix'),dict(id='historical_high_2024',volume_contest='2024-president',label='observed high volume and county mix')]
 save('scenario-settings.json',dict(volume_basis='county all named candidate votes in declared contest; multiply each county by preference anchor county pair participation',native_mix='2024 native rows within each county retain their 2024 all-candidate proportions; historical county volume replaces parent only. No cross-year precinct join.',settings=settings,current_opposition_anchors='2024 Harris/Trump shares and participation transported as explicit hypothetical proxy to each named opposition/Risch pair; two other printed candidates each receive half of residual candidate volume. This split is arbitrary, not inferred.',anchor_observed_county_repeat='additional setting uses each preference anchors own observed county all-candidate volumes',historical_preferences=list(PAIRS)))
 stateout=[];targets=[]
 for pairid in PAIRS:
  countyrows=[r for r in rows if r['pair_id']==pairid and r['scope']=='county'];nativerows=[r for r in rows if r['pair_id']==pairid and r['scope']=='native']
  for setting in settings+[dict(id='anchor_observed_county_repeat',volume_contest=countyrows[0]['anchor_contest'])]:
   volumes={u['county']if u['county'].endswith(' County')else u['county']+' County':sum(c['votes']for c in u['candidates'])for u in controls if u['contest']==setting['volume_contest']}
   for scope,rr in [('county',countyrows)]+([('native',nativerows)]if pairid=='2024-president'or pairid.startswith('current-')else[]):
    sim=[]
    parents={r['county']:r for r in countyrows}
    for r in rr:
     parent=parents[r['county']];fraction=1 if scope=='county'else r['all_candidate_votes']/parent['all_candidate_votes'];V=volumes[r['county']]*fraction;p=r['pair_participation'];T=None if p is None else V*p
     sim.append(dict(r,valid_volume=V,pair_votes=T,share=r['A_share']))
    append_scenario(pairid,setting['id'],scope,sim,stateout,targets)
  # Every actual native source row also gets its own observed fixed-pair-volume repeat.
  sim=[dict(r,valid_volume=r['all_candidate_known_sum'])for r in nativerows]
  append_scenario(pairid,'native_observed_pair_repeat','native',sim,stateout,targets)
 csvout('state-scenarios.csv',stateout);csvout('unit-targets.csv.gz',targets)
 print('baseline rows',len(rows),'scenarios',len(stateout),'targets',len(targets))
def append_scenario(pairid,setting,scope,sim,stateout,targets):
 for g in [0.,.01]:
  sol=solve(sim,g);T=sum(r['pair_votes']for r in sim if r['pair_votes']is not None);V=sum(r['valid_volume']for r in sim);M=None if any(r['pair_votes']is None or(r['pair_votes']>0 and r['share']is None)for r in sim)else sum(r['pair_votes']*(2*r['share']-1)for r in sim if r['pair_votes']>0)
  scenario=f'{pairid}/{setting}/{scope}/'+('tie'if g==0 else'Aplus1_pair_margin')
  other_totals={};fullfield_known=sol['status']=='feasible'
  for r in sim:
   other=json.loads(r['other_candidate_fractions_json'])
   if other is None or r['pair_votes']is None:fullfield_known=False;continue
   for name,fraction in other.items():other_totals[name]=other_totals.get(name,0)+(r['valid_volume']-r['pair_votes'])*fraction
  targetA=None if sol['status']!='feasible'else(T+sol['target_net'])/2;targetB=None if targetA is None else(T-sol['target_net'])/2
  legal='unknown_full_field'if not fullfield_known else'strict_plurality'if targetA>max([targetB]+list(other_totals.values()))+1e-7 else'shared_highest_tie_coin_rule'if abs(targetA-max([targetB]+list(other_totals.values())))<1e-7 else'not_plurality'
  stateout.append(dict(scenario=scenario,pair_id=pairid,volume_setting=setting,scope=scope,units=len(sim),target_pair_margin_pp=100*g,status=sol['status'],all_candidate_volume_basis=V,pair_volume_known_sum=T,baseline_net=M,baseline_pair_margin_pp=None if not T or M is None else 100*M/T,unbounded_A_share_shift_pp=None if sol['unbounded_shift']is None else 100*sol['unbounded_shift'],bounded_A_share_shift_pp=None if sol['shift']is None else 100*sol['shift'],clipped_units=sol.get('clipped_units'),target_net=sol.get('target_net'),achieved_net=sol.get('achieved_net'),target_all_candidate_margin_pp=None if not V else 100*g*T/V,baseline_already_wins=sol.get('baseline_already_wins'),minimum_nonnegative_improvement_pp=None if sol.get('minimum_nonnegative_improvement')is None else 100*sol['minimum_nonnegative_improvement'],target_A_votes=targetA,target_B_votes=targetB,other_candidate_totals_json=json.dumps(other_totals,sort_keys=True),legal_A_status=legal))
  for i,r in enumerate(sim):
   q=None if sol['shift']is None or r['share']is None else clip(r['share']+sol['shift']);sel=selected(sim,i,g);baseline_net=None if r['pair_votes']is None or r['share']is None else r['pair_votes']*(2*r['share']-1);net=None if q is None else r['pair_votes']*(2*q-1)
   targets.append(dict(scenario=scenario,pair_id=pairid,scope=scope,unit_id=r['unit_id'],source_unit_id=r['source_unit_id'],county=r['county'],literal_unit=r['literal_unit'],source_row=r['source_row'],candidate_A=r['candidate_A'],candidate_B=r['candidate_B'],valid_volume=r['valid_volume'],pair_volume=r['pair_votes'],pair_participation=r['pair_participation'],pair_weight=None if not T or r['pair_votes']is None else r['pair_votes']/T,all_candidate_weight=None if not V else r['valid_volume']/V,baseline_A_share=r['share'],baseline_net=baseline_net,raw_uniform_target_share=None if sol['unbounded_shift']is None or r['share']is None else r['share']+sol['unbounded_shift'],bounded_target_share=q,target_pair_margin_pp=None if q is None else 100*(2*q-1),share_change_pp=None if q is None else 100*(q-r['share']),target_net=net,net_gain=None if net is None or baseline_net is None else net-baseline_net,net_gain_per_1pp_share=None if r['pair_votes']is None else .02*r['pair_votes'],bounded_gain_for_1pp_share=None if r['pair_votes']is None or r['share']is None else 2*r['pair_votes']*(clip(r['share']+.01)-r['share']),selected_only_required_share=sel.get('required_share'),selected_only_status=sel['status'],fixed_other_net=sel.get('fixed_other_net'),fixed_other_assumption='all other units at same scenario volume and unchanged anchor share; other shift=0pp',status=sol['status']))

def main():
 p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');p.add_argument('--pair',default='2024-president',choices=PAIRS);p.add_argument('--unit',help='exact source_unit_id or county name');p.add_argument('--scope',choices=['county','native'],default='county');p.add_argument('--target-margin-pp',type=float,default=0);p.add_argument('--others-shift-pp',type=float,default=0);a=p.parse_args()
 if a.build:build();return
 rr=[]
 with (D.parent/'county-baselines.csv').open()if a.scope=='county'else __import__('contextlib').nullcontext(io_text(gzip.decompress((D/'native-baselines.csv.gz').read_bytes())))as f:
  for r in csv.DictReader(f):
   if r['pair_id']==a.pair:r['share']=float(r['A_share'])if r['A_share']else None;r['pair_votes']=float(r['pair_votes'])if r['pair_votes']else None;rr.append(r)
 if a.unit:
  indices=[i for i,r in enumerate(rr)if r['source_unit_id']==a.unit or(a.scope=='county'and r['county']==a.unit)]
  if len(indices)!=1:raise SystemExit('Select one exact source unit ID or full county name')
  print(json.dumps(selected(rr,indices[0],a.target_margin_pp/100,a.others_shift_pp/100),indent=2))
 else:print(json.dumps(solve(rr,a.target_margin_pp/100),indent=2))
def io_text(b):
 import io
 return io.StringIO(b.decode())
if __name__=='__main__':main()

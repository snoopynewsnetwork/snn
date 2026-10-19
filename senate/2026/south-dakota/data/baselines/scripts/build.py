#!/usr/bin/env python3
"""Build full-geography historical targets and explicit synthetic remainder scenarios."""
import csv,json,gzip,math
from extract import BASE,SRC,csvout,js,gz
from calculator import clip,net,bounded_shift,selected_unit,live,live_selected
def read(name):return list(csv.DictReader((BASE/name).open()))
def rank(rows,key):
 order=sorted(rows,key=lambda r:(-int(r['all_named_votes']),r['county_fips'],int(r.get('sheet',0)),int(r.get('source_row',0))))
 T=sum(int(r['all_named_votes'])for r in order);c=0;cross=None;out=[]
 for i,r in enumerate(order,1):
  c+=int(r['all_named_votes']);out.append(dict(rank=i,key=r[key],county=r['county'],county_fips=r['county_fips'],native_label=r.get('native_label'),volume=int(r['all_named_votes']),cumulative_votes=c,source_id=r['source_id']))
  if cross is None and 5*c>=4*T:cross=i
 return dict(basis='all_named_candidate_contest_votes',sort=['descending all_named_votes','county_fips','numeric sheet ordinal','numeric source row'],denominator=T,minimum_integer80_target=(4*T+4)//5,rows=len(out),top15_votes=sum(r['volume']for r in out[:15]),minimum80_count=cross,before80_votes=out[cross-2]['cumulative_votes'],crossing80_votes=out[cross-1]['cumulative_votes'],crossing_unit=out[cross-1],remaining_votes=T-out[cross-1]['cumulative_votes'],order=out,priority_keys=[r['key']for r in out[:cross]],coordinator_accepted=False,current_geography_approved=False,certified_native_membership_robustness='unproved; no unexplained source residual assigned to native rows')
def main():
 county=read('../county-baselines.csv');native={y:read('native-2024.csv'if y==2024 else f'native-{y}-public.csv')for y in [2024,2022,2020]}
 volumes={y:{r['county']:int(r['all_named_votes'])for r in county if int(r['year'])==y}for y in [2024,2022,2020]}
 totals={y:sum(v.values())for y,v in volumes.items()};alltargets=[];selected=[];states=[];settings=[]
 def scenario(sid,units,metadata):
  T=sum(u['pair_volume']for u in units);allT=sum(u['all_volume']for u in units);base=net(units)
  other_candidates={}
  for u in units:
   for k,v in u.get('other_candidates',{}).items():other_candidates[k]=other_candidates.get(k,0)+v
  settings.append(dict(scenario=sid,**metadata,units=len(units),pair_total=T,all_candidate_total=allT,baseline_net=base,historical_other_candidate_votes=other_candidates))
  for margin,label in [(0.,'tie'),(.01,'A_plus_1_pair_margin')]:
   sol=bounded_shift(units,margin);delta=sol['bounded_shift'];target=margin*T
   historical_final={units[0]['a_historical']:(T+target)/2,units[0]['b_historical']:(T-target)/2,**other_candidates}
   winners=[k for k,v in historical_final.items()if abs(v-max(historical_final.values()))<1e-7]
   states.append(dict(scenario=sid,target=label,**metadata,**sol,all_candidate_total=allT,target_all_candidate_margin_pp=100*target/allT if allT else None,net_gain=target-base,historical_final_candidate_votes=historical_final,historical_plurality_leaders=winners,historical_unique_plurality_winner=winners[0]if len(winners)==1 else None,legal_outcome_rule='strict plurality over every named candidate; tie is not a win',current_named_pair_assumption='Bengs IND=A and Rounds REP=B conditional repeat of historical pair preferences; exactly two current choices, no inferred transfers',current_named_pair_all_candidate_denominator=T,current_named_pair_candidate_votes={'Brian L Bengs Independent':(T+target)/2,'Mike Rounds Republican':(T-target)/2}))
   for u in units:
    q=clip(u['a_share']+delta);baseline=u['pair_volume']*(2*u['a_share']-1);tn=u['pair_volume']*(2*q-1)
    alltargets.append(dict(scenario=sid,target=label,unit_key=u['key'],county=u['county'],native_label=u.get('native_label',''),source_id=u['source_id'],preference_year=metadata['preference_year'],volume_basis=metadata['volume_basis'],a_historical=u['a_historical'],b_historical=u['b_historical'],pair_volume=u['pair_volume'],all_candidate_volume=u['all_volume'],pair_participation=u['pair_volume']/u['all_volume']if u['all_volume']else'',pair_weight=u['pair_volume']/T if T else 0,all_candidate_weight=u['all_volume']/allT if allT else 0,baseline_a_share=u['a_share']if u['pair_volume'] else'',baseline_net=baseline,unbounded_uniform_shift_share_pp=sol['unbounded_shift_share_pp'],bounded_uniform_shift_share_pp=sol['bounded_shift_share_pp'],target_a_share=q if u['pair_volume']else'',clipped=not 0<=u['a_share']+delta<=1,target_pair_margin_pp=100*(2*q-1)if u['pair_volume']else'',target_net=tn,net_gain=tn-baseline,net_gain_per_one_share_pp=.02*u['pair_volume'],target_a_all_candidate_share=q*u['pair_volume']/u['all_volume']if u['all_volume']else'',target_all_candidate_net_margin_pp=100*tn/u['all_volume']if u['all_volume']else'',native_zero_pool='no_positive_pool'if u['pair_volume']==0 else'',state_target_net=target))
    selected.append(dict(scenario=sid,target=label,unit_key=u['key'],county=u['county'],native_label=u.get('native_label',''),a_historical=u['a_historical'],b_historical=u['b_historical'],assumption_elsewhere='all other units fixed at historical anchor shares; zero additive shift; full universe retained',**selected_unit(units,u['key'],margin)))
 # County grid: three real historical county volume mixes by each independent preference anchor.
 for pref in [2024,2020,2022]:
  rr=[r for r in county if int(r['year'])==pref]
  for level,vol in [('low',2022),('base',2020),('high',2024)]:
   units=[]
   for r in rr:
    v=volumes[vol][r['county']];p=int(r['pair_votes'])/int(r['all_named_votes'])
    other={x['candidate']:int(x['votes'])*v/int(r['all_named_votes'])for x in read('county-candidates.csv')if int(x['year'])==pref and x['county']==r['county']and x['candidate']not in[r['a_name'],r['b_name']]}
    units.append(dict(key=r['county_fips'],county=r['county'],a_share=float(r['a_pair_share']),pair_volume=v*p,all_volume=v,source_id=r['source_id'],a_historical=r['a_name'],b_historical=r['b_name'],other_candidates=other))
   scenario(f'county_pref{pref}_{level}_mix{vol}',units,dict(geography='all66_counties',preference_year=pref,volume_basis=f'{vol} actual county all-named contest votes; pair participation from {pref} in each county',historical_volume_level=level,all_candidate_volume_control=totals[vol],mix=f'observed{vol}county_mix'))
   if pref==2024 and vol==2024:js(BASE/'historical-input-example.json',dict(assumption='All66 counties; historical Harris-Trump pair preferences and actual2024 pair volumes. Conditional named Bengs-Rounds substitution is an assumption only.',target_pair_margin=.0,shift_bounds=[-1,1],units=units))
 # Native scenarios: each election's exact original rows and its own preferences/mix.
 # Low/base/high totals are historical controls; scaling is only scenario arithmetic, never source repair.
 for pref,rr in native.items():
  sourceTotal=sum(int(r['all_named_votes'])for r in rr)
  choices=[('observed',None),('low',2022),('base',2020),('high',2024)]
  for level,vol in choices:
   scale=1. if vol is None else totals[vol]/sourceTotal;units=[]
   names={2024:('Kamala D. Harris and Tim Walz','Donald J. Trump and JD Vance'),2022:('Brian L. Bengs','John R. Thune'),2020:('Dan Ahlers','Mike Rounds')}[pref]
   for r in rr:
    other={'Chase Oliver and Mike ter Maat':int(r['oliver_lib'])*scale,'Robert F. Kennedy, Jr. and Nicole Shanahan':int(r['kennedy_ind'])*scale}if pref==2024 else{'Tamara J Lesnar':int(r['other_named_votes'])*scale}if pref==2022 else{}
    pair=int(r['pair_votes']);units.append(dict(key=r['native_key'],county=r['county'],native_label=r['native_label'],a_share=int(r['a_votes'])/pair if pair else.5,pair_volume=pair*scale,all_volume=int(r['all_named_votes'])*scale,source_id=r['source_id'],a_historical=names[0],b_historical=names[1],other_candidates=other))
   scenario(f'native_pref{pref}_{level}',units,dict(geography=f'all{len(rr)}_native_rows_66parents',preference_year=pref,volume_basis='exact observed native candidate votes'if vol is None else f'uniform scale {scale:.17g} of {pref}native rows to historical{vol} all-named statewide control{totals[vol]}; same native mix, no cross-year crosswalk',historical_volume_level=level,all_candidate_volume_control=sourceTotal if vol is None else totals[vol],mix=f'observed{pref}native_mix'))
 js(BASE/'state-targets.json',states);js(BASE/'scenario-settings.json',settings)
 for name,rows in [('unit-targets.csv.gz',alltargets),('selected-unit-break-even.csv.gz',selected)]:
  import io
  f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);(BASE/name).write_bytes(gzip.compress(f.getvalue().encode(),mtime=0))
 contracts={str(y):rank(rr,'native_key')for y,rr in native.items()};contracts['2024_county_separate_sensitivity']=rank([r for r in county if int(r['year'])==2024],'county_fips');js(BASE/'priority-contract.json',contracts)
 # Synthetic executable examples: fixed counts, explicit total remaining and third-candidate shares.
 scenarios=[]
 def example(name,counted,remaining,m=.0,select=None):
  inp=dict(a='Brian L Bengs',b='Mike Rounds',counted=counted,remaining=remaining,target_pair_margin=m)
  scenarios.append(dict(name=name,input=inp,result=live(inp),selected_result=live_selected(inp,select)if select else None))
 A='Brian L Bengs';B='Mike Rounds'
 example('unknown_pool',{A:20,B:30},[dict(key='unknown',remaining_total=None,a_pair_share=.5)])
 example('unknown_preference',{A:20,B:30},[dict(key='unknown',remaining_total=100,a_pair_share=None)])
 example('no_pool_tie',{A:20,B:20},[])
 example('no_pool_secured',{A:21,B:20},[])
 example('no_pool_lost',{A:19,B:20},[])
 example('negative_pool',{A:20,B:30},[dict(key='negative',remaining_total=-1,a_pair_share=.5)])
 example('negative_counted',{A:-1,B:30},[])
 example('impossible',{A:20,B:150},[dict(key='u',remaining_total=100,a_pair_share=.8)],select='u')
 example('secured',{A:150,B:20},[dict(key='u',remaining_total=100,a_pair_share=.2)],select='u')
 example('clip_high',{A:20,B:30},[dict(key='u',remaining_total=100,a_pair_share=1.2)],select='u')
 example('clip_low',{A:20,B:30},[dict(key='u',remaining_total=100,a_pair_share=-.2)],select='u')
 example('FINAL_denominator_Aplus1',{A:400,B:500},[dict(key='u',remaining_total=100,a_pair_share=.9)],m=.01,select='u')
 example('third_candidate_beats_pair_winner',{A:20,B:10,'Illustrative third candidate':200},[dict(key='u',remaining_total=100,a_pair_share=.6,other_shares={'Illustrative third candidate':.2})],select='u')
 example('others_fixed_selected_target',{A:100,B:120},[dict(key='selected',remaining_total=100,a_pair_share=.5),dict(key='elsewhere',remaining_total=200,a_pair_share=.6)],m=.01,select='selected')
 example('zero_pair_pool_positive_other_pool',{A:20,B:30,'Illustrative third candidate':0},[dict(key='u',remaining_total=100,a_pair_share=None,other_shares={'Illustrative third candidate':1})],select='u')
 js(BASE/'live-synthetic-scenarios.json',scenarios)
 # One standalone editable input for command-line use.
 js(BASE/'live-input-example.json',scenarios[-2]['input'])
 edge=[dict(name='no_positive_pool',units=[dict(key='x',pair_volume=0,a_share=.5)]),dict(name='negative_shift_already_winning',units=[dict(key='x',pair_volume=100,a_share=.7)]),dict(name='clipping_requires_bounded_solution',units=[dict(key='x',pair_volume=20,a_share=.95),dict(key='y',pair_volume=80,a_share=.1)]),dict(name='unachievable_limited_shift',units=[dict(key='x',pair_volume=100,a_share=.1)],bounds=[-.1,.1])]
 js(BASE/'bounded-synthetic-scenarios.json',[dict(e,result=bounded_shift(e['units'],bounds=tuple(e.get('bounds',[-1,1]))))for e in edge])
 print(json.dumps(dict(state_targets=len(states),unit_targets=len(alltargets),selected_targets=len(selected),native2024_min80=contracts['2024']['minimum80_count'],scenario_count=len(settings))))
if __name__=='__main__':main()

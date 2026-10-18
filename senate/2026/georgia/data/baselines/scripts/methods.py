#!/usr/bin/env python3
"""Historical native method cells; source group GUIDs/names retained without cross-year joins."""
import collections,json
from calculate import R,csvread,write,save,bounded_uniform,clip,selected
long=csvread(R/'candidate-methods.csv.gz');base=csvread(R.parent/'county-baselines.csv');native=csvread(R/'native-baselines.csv.gz');lookup={(r['election_key'],r['county_fips'],r['native_GUID']):r for r in base+native}
groups=collections.defaultdict(list)
for r in long:
 if r['unit_level'] in ['county','native_precinct'] and r['group_ordinal']!='-1':groups[(r['election_key'],r['county_fips'],r['unit_level'],r['native_GUID'],r['group_GUID'])].append(r)
rows=[]
for (e,f,level,uid,gid),opts in groups.items():
 a=next(x for x in opts if x['candidate_name'].endswith('(Dem)'));b=next(x for x in opts if x['candidate_name'].endswith('(Rep)'));av=int(a['votes']) if a['votes'] else None;bv=int(b['votes']) if b['votes'] else None;pair=av+bv if av is not None and bv is not None else None
 named=[x for x in opts if e!='2024NovGen' or x['candidate_name'] in ['Donald J. Trump (Rep)','Kamala D. Harris (Dem)','Chase Oliver (Lib)','Jill Stein (Grn)']];total=sum(int(x['votes']) for x in named) if all(x['votes'] for x in named) else None
 rows.append({'election_key':e,'county_fips':f,'county_name':a['county_name'],'unit_level':level,'native_GUID':uid,'native_name':a['native_name'],'group_GUID':gid,'group_name':a['group_name'],'group_ordinal':a['group_ordinal'],'source_id':a['source_id'],'A_pointer':a['source_pointer'],'B_pointer':b['source_pointer'],'A_name':a['candidate_name'],'A':av,'B_name':b['candidate_name'],'B':bv,'pair_votes':pair,'named_option_votes':total,'named_other':total-pair if total is not None and pair is not None else None,'A_pair_share':av/pair if pair else None,'pair_net':av-bv if pair is not None else None,'pair_weight_complete_state':pair/sum(int(x['pair_votes']) for x in base if x['election_key']==e) if pair is not None else None,'status':'redacted_partial_or_unknown' if pair is None else 'no_positive_pool' if not pair else 'observed_historical'})
write('method-baselines.csv.gz',rows);targets=[];state=[]
for level in ['county','native_precinct']:
 for e in sorted({x['election_key'] for x in rows if x['unit_level']==level}):
  allrows=[x for x in rows if x['election_key']==e and x['unit_level']==level];known=[x for x in allrows if x['pair_votes'] is not None and x['pair_votes']>0];T=[x['pair_votes'] for x in known];s=[x['A_pair_share'] for x in known];P=sum(int(x['pair_votes']) for x in base if x['election_key']==e);M=sum(int(x['A_minus_B_net']) for x in base if x['election_key']==e);WP=P-sum(T);WM=M-sum(x['pair_net'] for x in known)
  for margin in [0,1]:
   solved=bounded_uniform(T,s,100*(margin*P/100-WM)/sum(T));qs=solved.pop('target_shares');d=solved['bounded_shift_pp']/100;qmap={(x['county_fips'],x['native_GUID'],x['group_GUID']):q for x,q in zip(known,qs)}
   state.append({'unit_level':level,'election_key':e,'target_pair_margin_pp':margin,'complete_state_pair_votes':P,'complete_state_baseline_net':M,'unallocated_redacted_pair_votes_held_fixed':WP,'unallocated_redacted_net_held_fixed':WM,'allstate_target_net':margin*P/100,'allstate_actual_net':sum(t*(2*q-1) for t,q in zip(T,qs))+WM,**solved})
   for x in allrows:
    t=x['pair_votes'];s0=x['A_pair_share'];q=qmap.get((x['county_fips'],x['native_GUID'],x['group_GUID']));raw=(t+margin*P/100-(M-x['pair_net']))/(2*t) if t else None
    targets.append({'unit_level':level,'election_key':e,'county_fips':x['county_fips'],'native_GUID':x['native_GUID'],'native_name':x['native_name'],'group_GUID':x['group_GUID'],'group_name':x['group_name'],'target_pair_margin_pp':margin,'pair_votes':t,'pair_weight_complete_state':t/P if t is not None else None,'baseline_A_pair_share':s0,'target_A_pair_share':q,'target_net':t*(2*q-1) if q is not None else None,'uniform_bounded_shift_pp':solved['bounded_shift_pp'],'unbounded_shift_pp':solved['unbounded_shift_pp'],'actual_shift_pp':100*(q-s0) if q is not None else None,'gain_plus1_share_pp_net':2*t*(clip(s0+.01)-s0) if s0 is not None else None,'selected_raw_required_share':raw,'selected_status':'unknown_redacted' if t is None else 'no_positive_pool' if not t else 'already_secured' if raw<0 else 'impossible' if raw>1 else 'feasible','others_fixed_at_historical':True,'status':x['status']})
write('method-targets.csv.gz',targets);save('method-state-scenarios.json',state)
print(json.dumps({'method_rows':len(rows),'targets':len(targets),'state_scenarios':len(state),'method_levels':dict(collections.Counter(x['unit_level'] for x in rows))}))

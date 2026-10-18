#!/usr/bin/env python3
"""Offline conditional arithmetic. A = named historical Democrat; B = named Republican."""
import argparse,csv,gzip,io,json,math,pathlib
R=pathlib.Path(__file__).resolve().parents[1]
def csvread(p):
 b=p.read_bytes();return list(csv.DictReader(io.StringIO((gzip.decompress(b) if p.suffix=='.gz' else b).decode())))
def write(name,rows):
 rows=list(rows);buf=io.StringIO(newline='');w=csv.DictWriter(buf,list(rows[0]));w.writeheader();w.writerows(rows);b=buf.getvalue().encode();(R/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
def save(name,x):(R/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def clip(x):return max(0,min(1,x))
def bounded_uniform(T,s,margin_pp):
 if any(t<0 for t in T):return {'status':'invalid_negative_volume'}
 total=sum(T)
 if total<=0:return {'status':'no_positive_pool','unbounded_shift_pp':None,'bounded_shift_pp':None}
 M=sum(t*(2*q-1) for t,q in zip(T,s));target=total*margin_pp/100;delta=(target-M)/(2*total)
 out={'baseline_net':M,'pair_total':total,'target_net':target,'unbounded_shift_pp':100*delta,'already_meets_target':M>=target,'minimum_positive_improvement_pp':max(0,100*delta)}
 if abs(margin_pp)>100:return {**out,'status':'impossible','bounded_shift_pp':None}
 lo=-1.;hi=1.
 for _ in range(90):
  mid=(lo+hi)/2;net=sum(t*(2*clip(q+mid)-1) for t,q in zip(T,s))
  if net<target:lo=mid
  else:hi=mid
 shift=(lo+hi)/2; shares=[clip(q+shift) for q in s]
 return {**out,'status':'feasible_clipped' if any(q+delta<0 or q+delta>1 for q in s) else 'feasible','bounded_shift_pp':100*shift,'target_shares':shares,'clipped_unit_count':sum(q+shift<0 or q+shift>1 for q in s),'actual_net':sum(t*(2*q-1) for t,q in zip(T,shares))}
def selected(T,s,index,margin_pp=0,others_shift_pp=0):
 total=sum(T);t=T[index];outside=sum(v*(2*clip(q+others_shift_pp/100)-1) for i,(v,q) in enumerate(zip(T,s)) if i!=index);target=total*margin_pp/100
 if t<=0:return {'selected_status':'no_positive_pool','selected_required_share':None,'outside_fixed_net':outside,'selected_raw_required_share':None}
 q=(t+target-outside)/(2*t)
 return {'selected_status':'already_secured' if q<0 else 'impossible' if q>1 else 'feasible','selected_required_share':clip(q),'selected_raw_required_share':q,'outside_fixed_net':outside}
def live(case):
 """remaining_total is remaining valid contest votes; pair_fraction separates other votes."""
 rows=case['units'];target=case.get('target_pair_margin_pp',0)/100;out={'name':case.get('name'),'interpretation':'conditional arithmetic; no probability; counted values fixed','counted_A':sum(x['counted_A'] for x in rows),'counted_B':sum(x['counted_B'] for x in rows),'counted_other':sum(x['counted_other'] for x in rows)}
 if len({x['id'] for x in rows})!=len(rows):return {**out,'status':'invalid_duplicate_unit'}
 if not rows:return {**out,'status':'no_units'}
 if any(x[k]<0 for x in rows for k in ['counted_A','counted_B','counted_other']):return {**out,'status':'invalid_negative_counted'}
 if any(x.get('remaining_total') is None or x.get('remaining_pair_fraction') is None or x.get('remaining_A_pair_share') is None for x in rows):return {**out,'status':'unknown_remaining_assumptions'}
 if any(x['remaining_total']<0 for x in rows):return {**out,'status':'invalid_negative_remaining'}
 if any(not 0<=x['remaining_pair_fraction']<=1 for x in rows):return {**out,'status':'invalid_pair_fraction'}
 details=[]
 for x in rows:
  u=x['remaining_total']*x['remaining_pair_fraction'];o=x['remaining_total']-u;q=clip(x['remaining_A_pair_share']);details.append({**x,'remaining_pair':u,'remaining_other':o,'clipped_A_pair_share':q,'share_was_clipped':q!=x['remaining_A_pair_share'],'remaining_A':u*q,'remaining_B':u*(1-q)})
 A=out['counted_A']+sum(x['remaining_A'] for x in details);B=out['counted_B']+sum(x['remaining_B'] for x in details);O=out['counted_other']+sum(x['remaining_other'] for x in details);P=A+B;F=P+O;U=sum(x['remaining_pair'] for x in details);L=out['counted_A']-out['counted_B']
 required=(U+target*P-L)/(2*U) if U else None
 majority_required=(F/2-out['counted_A'])/U if U else None
 status='no_positive_pair_pool' if U==0 else 'already_secured' if required<0 else 'impossible' if required>1 else 'conditional_feasible'
 pick=case.get('selected_unit',rows[0]['id']);v=next(x for x in details if x['id']==pick);u=v['remaining_pair'];outside=L+sum(x['remaining_A']-x['remaining_B'] for x in details if x['id']!=pick);sel=(u+target*P-outside)/(2*u) if u else None
 return {**out,'status':status,'units':details,'selected_unit':pick,'final_A':A,'final_B':B,'final_other':O,'FINAL_pair_denominator':P,'FINAL_allcandidate_denominator':F,'pair_net':A-B,'pair_margin_pp':100*(A-B)/P if P else None,'A_allcandidate_share':A/F if F else None,'majority_cushion_votes':A-F/2,'A_strict_majority':A>F/2 if F else None,'required_remaining_A_pair_share_unbounded':required,'required_remaining_A_pair_share_clipped':clip(required) if required is not None else None,'majority_remaining_A_share_boundary_strictly_exceed':majority_required,'majority_requirement_status':'no_positive_pair_pool' if U==0 else 'already_secured' if majority_required<0 else 'impossible' if majority_required>=1 else 'strictly_exceed_boundary','selected_required_share_unbounded':sel,'selected_status':'no_positive_pool' if not u else 'already_secured' if sel<0 else 'impossible' if sel>1 else 'feasible','selected_outside_counted_plus_assumed_remainder_net':outside,'target_pair_margin_pp':100*target}
def build():
 base=csvread(R.parent/'county-baselines.csv');E=sorted({x['election_key'] for x in base});by={e:{x['county_fips']:x for x in base if x['election_key']==e} for e in E};keys=sorted(next(iter(by.values())));assert all(set(v)==set(keys) and len(v)==159 for v in by.values())
 # Low/base/high are actual historical observed pair volumes and county mixes, not forecasts.
 mixes=[('low_historical_Dec2022','2022DecGenRun'),('base_historical_Nov2022','2022NovGen'),('high_historical_Nov2024','2024NovGen'),('same_seat_Nov2020','2020NovGen'),('same_seat_Jan2021','2021JanFedRun')]
 out=[];county=[];rankings={}
 for e in E:
  vals=sorted(by[e].values(),key=lambda r:(-int(r['named_valid_option_votes']),r['county_fips']));total=sum(int(x['named_valid_option_votes']) for x in vals);threshold=(4*total+4)//5;cum=0;rr=[]
  for i,r in enumerate(vals):cum+=int(r['named_valid_option_votes']);rr.append({'rank':i+1,'county_fips':r['county_fips'],'county_name':r['county_name'],'votes':int(r['named_valid_option_votes']),'cumulative_votes':cum,'share':int(r['named_valid_option_votes'])/total,'cumulative_share':cum/total,'priority_named_scope':cum-int(r['named_valid_option_votes'])<threshold})
  crossing=next(x['rank'] for x in rr if x['cumulative_votes']>=threshold);rankings[e]={'basis':'state-published named options;2024 four; excludes separately qualified writeins and void options','denominator':total,'integer_80_threshold':threshold,'minimum_count':crossing,'first_k_minus_1':rr[crossing-2]['cumulative_votes'],'first_k':rr[crossing-1]['cumulative_votes'],'top15':rr[14]['cumulative_votes'],'rows':rr,'accepted_priority':False}
 for pref in E:
  s=[float(by[pref][k]['A_pair_share']) for k in keys]
  for label,mix in mixes:
   T=[int(by[mix][k]['pair_votes']) for k in keys];O=[int(by[mix][k]['other_named_valid_votes']) for k in keys];P=sum(T);other=sum(O);extra=858 if mix=='2024NovGen' else 0
   for margin in [0,1]:
    result=bounded_uniform(T,s,margin);qs=result.pop('target_shares');scenario=f'{pref}__{label}__Aplus{margin}'
    A=sum(t*q for t,q in zip(T,qs));cushion=(margin*P/100-other-extra)/2
    out.append({'scenario':scenario,'preference_anchor':pref,'mix_volume_anchor':mix,'volume_label':label,'pair_votes':P,'named_other_fixed':other,'separate_state_qualified_writeins':extra,'final_allcandidate_denominator':P+other+extra,'target_pair_margin_pp':margin,**result,'majority_cushion_votes':cushion,'A_strict_majority':cushion>0})
    for i,k in enumerate(keys):
     r=by[pref][k];q=qs[i];t=T[i];selected_result=selected(T,s,i,margin)
     county.append({'scenario':scenario,'county_fips':k,'county_name':r['county_name'],'preference_anchor':pref,'mix_volume_anchor':mix,'A_name':r['A_name'],'B_name':r['B_name'],'historical_A':r['A'],'historical_B':r['B'],'baseline_A_pair_share':s[i],'expected_pair_votes':t,'county_pair_participation_in_named_mix':t/(t+O[i]),'named_other_fixed':O[i],'full_county_denominator_status':'unknown_qualified_WI_allocation' if extra else 'published_options','pair_weight':t/P,'baseline_net':t*(2*s[i]-1),'target_A_pair_share':q,'target_pair_margin_pp':100*(2*q-1),'target_net':t*(2*q-1),'actual_shift_share_pp':100*(q-s[i]),'unbounded_shift_pp':result['unbounded_shift_pp'],'bounded_shift_pp':result['bounded_shift_pp'],'gain_for_plus1_share_pp_net':2*t*(clip(s[i]+.01)-s[i]),'linear_gain_for_plus1_share_pp_net':.02*t,'others_fixed_share_shift_pp':0,**selected_result})
 write('state-scenarios.csv',out);write('county-targets.csv.gz',county);save('rankings.json',rankings)
 save('report-settings.json',{'version':1,'A_identity':'named historical Democrat','B_identity':'named historical Republican','preference_anchors':E,'mixes':[{'label':label,'election_key':mix,'volume_basis':'actual county A+B count; no scaling','named_other_basis':'actual county mix named_other count','additional_state_other':858 if mix=='2024NovGen' else 0} for label,mix in mixes],'targets_pair_margin_pp':[0,1],'others_fixed_share_shift_pp':0,'bounded_share_domain':[0,1],'county_pair_participation_basis':'pair/(pair+named_other), excludes unallocated county writeins','historical_not_2026_projection':True})
 # Every observed native identity appears, including withheld and zero-pair entries.
 native=csvread(R/'native-baselines.csv.gz');P=sum(int(x['pair_votes']) for x in by['2024NovGen'].values());M=sum(int(x['A'])-int(x['B']) for x in by['2024NovGen'].values());targets=[];native_state=[]
 proof=json.load(open(R/'source/priority-bounds.json'));priority={x['county_fips'] for x in rankings['2024NovGen']['rows'][:44]}
 save('priority-contract.json',{'status':'membership_proved_dispatch_proposal_not_coordinator_acceptance','coordinator_acceptance':False,'external_coordinator_acceptance_reference':'data/coordinator-priority-acceptance.json','current_geographic_approval':False,'ranking_universe':'named four2024president; full-candidate internalorder unknown','full_state_valid_votes':5250905,'state_qualified_writeins_unallocated':858,'membership_proof':'source/priority-bounds.json','exact_fullcandidate_share':None,'named_four_order_159':rankings['2024NovGen']['rows'],'priority44_membership_fips':sorted(priority),'top15_membership_fips':sorted(x['county_fips'] for x in rankings['2024NovGen']['rows'][:15]),'native_inventory_all159':[{'county_fips':k,'county_name':by['2024NovGen'][k]['county_name'],'priority44':k in priority,'source_id':by['2024NovGen'][k]['source_id'],'native_units':[{'native_GUID':x['native_GUID'],'native_name':x['native_name'],'source_pointer':x['source_pointer'],'candidate_pair_status':x['all_valid_candidate_denominator_status']} for x in native if x['county_fips']==k]} for k in keys]})
 known=[r for r in native if r['pair_votes'] and float(r['pair_votes'])>0];knownT=[float(r['pair_votes']) for r in known];knowns=[float(r['A_pair_share']) for r in known];KP=sum(knownT);KM=sum(float(r['A'])-float(r['B']) for r in known);withheldP=P-KP;withheldM=M-KM
 for margin in [0,1]:
  target=margin*P/100;solution=bounded_uniform(knownT,knowns,100*(target-withheldM)/KP);qs=solution.pop('target_shares');shift=solution['bounded_shift_pp']/100;qmap={(r['county_fips'],r['native_GUID']):q for r,q in zip(known,qs)}
  native_state.append({'target_pair_margin_pp':margin,'complete_county_state_pair_votes':P,'known_native_pair_votes':KP,'unallocated_withheld_pair_votes_held_fixed':withheldP,'unallocated_withheld_net_held_fixed':withheldM,'unallocated_withheld_A_held_fixed':(withheldP+withheldM)/2,'unallocated_withheld_B_held_fixed':(withheldP-withheldM)/2,'unallocated_scope':'Fulton10redactednativeunits; no allocation to any identity','allstate_target_net':target,'known_target_net':sum(t*(2*q-1) for t,q in zip(knownT,qs)),'allstate_actual_net_including_withheld_fixed':sum(t*(2*q-1) for t,q in zip(knownT,qs))+withheldM,**solution})
  for r in native:
   observed=r['pair_votes']!='';t=float(r['pair_votes']) if observed else None;s=float(r['A_pair_share']) if r['A_pair_share'] else None;q=qmap.get((r['county_fips'],r['native_GUID']))
   raw=(t+margin*P/100-(M-(float(r['A'])-float(r['B']))))/(2*t) if t else None
   targets.append({'target_pair_margin_pp':margin,'county_fips':r['county_fips'],'native_GUID':r['native_GUID'],'native_name':r['native_name'],'source_id':r['source_id'],'source_pointer':r['source_pointer'],'pair_votes':t,'pair_weight_in_complete_county_state':t/P if observed else None,'baseline_share':s,'target_share':q,'uniform_shift_share_pp':100*shift,'unbounded_shift_share_pp':solution['unbounded_shift_pp'],'actual_shift_share_pp':100*(q-s) if q is not None else None,'target_net':t*(2*q-1) if q is not None else None,'gain_plus1_share_pp_net':2*t*(clip(s+.01)-s) if s is not None else None,'status':'redacted_unknown_no_allocation' if not observed else 'no_positive_pool' if not t else 'feasible','selected_unbounded_share':raw,'selected_status':'unknown' if not observed else 'no_positive_pool' if not t else 'already_secured' if raw<0 else 'impossible' if raw>1 else 'feasible','outside_fixed_net':M-(float(r['A'])-float(r['B'])) if observed else None})
 write('native-targets.csv.gz',targets)
 save('native-state-scenarios.json',native_state)
 save('calculator-edge-tests.json',[{'case':'clipping_changes_solve','result':bounded_uniform([90,10],[.99,.01],90)},{'case':'already_winning','result':bounded_uniform([100],[.6],0)},{'case':'impossible_margin','result':bounded_uniform([100],[.4],101)},{'case':'no_positive_pool','result':bounded_uniform([0],[.5],0)},{'case':'negative_volume','result':bounded_uniform([-1],[.5],0)}])
 cases=json.load(open(R/'live-scenarios.json'));save('live-results.json',[live(c) for c in cases])
 print(json.dumps({'scenarios':len(out),'county_targets':len(county),'native_targets':len(targets),'rankings':{e:{k:v for k,v in x.items() if k!='rows'} for e,x in rankings.items()}},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--live-json',type=pathlib.Path);p.add_argument('--county-fips');p.add_argument('--preference',default='2024NovGen');p.add_argument('--volume-mix',default='2024NovGen');p.add_argument('--others-shift-pp',type=float,default=0);p.add_argument('--margin-pp',type=float,default=0);a=p.parse_args()
 if a.live_json:print(json.dumps(live(json.load(open(a.live_json))),indent=2,allow_nan=False))
 elif a.county_fips:
  rows=csvread(R.parent/'county-baselines.csv');s=sorted([r for r in rows if r['election_key']==a.preference],key=lambda r:r['county_fips']);mix={r['county_fips']:r for r in rows if r['election_key']==a.volume_mix};i=next(i for i,r in enumerate(s) if r['county_fips']==a.county_fips);print(json.dumps(selected([int(mix[r['county_fips']]['pair_votes']) for r in s],[float(r['A_pair_share']) for r in s],i,a.margin_pp,a.others_shift_pp),indent=2))
 else:build()

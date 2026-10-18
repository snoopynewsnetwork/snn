"""Offline historical and conditional live arithmetic. No probability model.
Shares are fractions internally, pp only in named output fields. Counted votes
are immutable; unknown/negative pools never silently become zero.
"""
import argparse,collections,json,math
from extract import H,readcsv,writecsv,dump

def clip(q):return max(0.,min(1.,q))
def finite(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def requirement(raw,pool,fixed,target):
 if pool==0:return dict(raw_share=None,clipped_share=None,status='no_positive_pool_'+('already_above_target' if fixed>target else 'at_target' if abs(fixed-target)<1e-8 else 'impossible'))
 return dict(raw_share=raw,clipped_share=clip(raw),status='already_secured' if raw<0 else 'impossible' if raw>1 else 'boundary' if raw in [0,1] else 'feasible')
def bounded(shares,weights,target_net):
 if len(shares)!=len(weights) or any(not finite(w) or w<0 for w in weights) or not finite(target_net):return dict(status='invalid_weights_or_target',unbounded_shift=None,bounded_shift=None,shares=None,net=None,clipped_units=None)
 if any(not finite(s) or not 0<=s<=1 for s in shares):return dict(status='unknown_or_invalid_preference',unbounded_shift=None,bounded_shift=None,shares=None,net=None,clipped_units=None)
 t=sum(weights);m=sum(w*(2*s-1) for w,s in zip(weights,shares))
 if not t:return dict(status='no_positive_pool',unbounded_shift=None,bounded_shift=None,shares=shares,net=m,clipped_units=0)
 unbounded=(target_net-m)/(2*t)
 if target_net < -t or target_net > t:return dict(status='impossible',unbounded_shift=unbounded,bounded_shift=None,shares=None,net=None,clipped_units=None)
 lo,hi=-1.,1.
 for _ in range(90):
  mid=(lo+hi)/2;v=sum(w*(2*clip(s+mid)-1) for w,s in zip(weights,shares))
  if v<target_net:lo=mid
  else:hi=mid
 delta=(lo+hi)/2;qs=[clip(s+delta) for s in shares]
 return dict(status='feasible_with_clipping' if any(w>0 and not 0<=s+unbounded<=1 for w,s in zip(weights,shares)) else 'feasible_unclipped',unbounded_shift=unbounded,bounded_shift=delta,shares=qs,net=sum(w*(2*q-1) for w,q in zip(weights,qs)),clipped_units=sum(w>0 and not 0<=s+delta<=1 for w,s in zip(weights,shares)))

def historical(rows,volumes=None,settings='own',others_shift_pp=0):
 ss=[float(r['A_pair_share']) if r['A_pair_share']!='' else .5 for r in rows]
 # Own volumes: exact historical candidate integers. Cross-year county sensitivity:
 # historical all-candidate contest volume * county-specific anchor pair participation.
 allv=[int(r['all_candidate_votes']) if volumes is None else volumes[r['unit_key']] for r in rows]
 weights=[int(r['pair_votes']) if volumes is None else v*float(r['pair_participation']) if r['pair_participation']!='' else 0 for r,v in zip(rows,allv)]
 total=sum(weights);all_total=sum(allv);m=sum(w*(2*s-1) for w,s in zip(weights,ss));out=[];states=[]
 for target,g in [('tie',0.),('Aplus1_pair_margin',.01)]:
  target_net=g*total;sol=bounded(ss,weights,target_net);qs=sol['shares'];assumed=[clip(s+others_shift_pp/100) for s in ss];fixedtotal=sum(w*(2*q-1) for w,q in zip(weights,assumed))
  for i,(r,w,s,v) in enumerate(zip(rows,weights,ss,allv)):
   other_net=fixedtotal-w*(2*assumed[i]-1);req=(w+target_net-other_net)/(2*w) if w else None;sel=requirement(req,w,other_net,target_net);q=qs[i] if qs is not None else None
   out.append(dict(scenario=settings,contest=r['contest'],level=r['level'],unit_key=r['unit_key'],county_fips=r['county_fips'],COUNTYNAME=r['COUNTYNAME'],MCDNAME=r['MCDNAME'],PCTNAME=r['PCTNAME'],target=target,A_name=r['A_name'],B_name=r['B_name'],baseline_A=int(r['A']),baseline_B=int(r['B']),baseline_other=int(r['other']),baseline_all_votes=int(r['all_candidate_votes']),baseline_share=s if int(r['pair_votes']) else '',baseline_pair_participation=r['pair_participation'],scenario_all_votes=v,scenario_pair_votes=w,scenario_other_votes=v-w,pair_weight=w/total if total else '',all_vote_weight=v/all_total if all_total else '',baseline_scenario_net=w*(2*s-1),plus1_share_pp_net_gain=.02*w,plus1_share_pp_feasible_gain=2*w*(clip(s+.01)-s),unbounded_shift_share_pp=100*sol['unbounded_shift'] if sol['unbounded_shift'] is not None else '',bounded_shift_share_pp=100*sol['bounded_shift'] if sol['bounded_shift'] is not None else '',target_share=q if q is not None and w else '',applied_share_change_pp=100*(q-s) if q is not None and w else '',target_pair_margin_pp=100*(2*q-1) if q is not None and w else '',target_net=w*(2*q-1) if q is not None else '',gain_net=2*w*(q-s) if q is not None else '',target_all_margin_pp=100*w*(2*q-1)/v if q is not None and v else '',clipped=bool(w and q is not None and not 0<=s+sol['bounded_shift']<=1),selected_others_shift_share_pp=others_shift_pp,selected_others_net=other_net,selected_required_raw_share=sel['raw_share'] if sel['raw_share'] is not None else '',selected_clipped_share=sel['clipped_share'] if sel['clipped_share'] is not None else '',selected_status=sel['status'],solver_status=sol['status']))
  states.append(dict(scenario=settings,contest=rows[0]['contest'],level=rows[0]['level'],target=target,all_units=len(rows),all_candidate_volume=all_total,pair_volume=total,other_volume=all_total-total,baseline_net=m,baseline_pair_margin_pp=100*m/total if total else None,target_pair_margin_pp=100*g,target_net=target_net,solved_net=sol['net'],target_all_candidate_margin_pp=100*target_net/all_total if all_total else None,unbounded_shift_share_pp=100*sol['unbounded_shift'] if sol['unbounded_shift'] is not None else None,bounded_shift_share_pp=100*sol['bounded_shift'] if sol['bounded_shift'] is not None else None,clipped_units=sol['clipped_units'],status=sol['status'],baseline_already_A_ahead=m>0,others_assumption=f'Each other unit at historical anchor share plus {others_shift_pp} share pp, clipped; all stated volumes fixed.'))
 return out,states

def live(spec):
 result={'id':spec.get('id'),'input':spec,'calibration':'synthetic conditional arithmetic; no probability','counted_held_fixed':True}
 rows=spec['units'];A=spec.get('A','A');B=spec.get('B','B');assert A!=B
 if len({r['key'] for r in rows})!=len(rows):return dict(result,status='invalid_duplicate_units')
 candidate_keys=set(rows[0]['counted']) if rows else set()
 if not rows or A not in candidate_keys or B not in candidate_keys or any(set(r['counted'])!=candidate_keys for r in rows):return dict(result,status='unknown_or_inconsistent_counted_candidate_coverage')
 if any(not finite(v) or v<0 for r in rows for v in r['counted'].values()):return dict(result,status='invalid_counted_votes')
 counted=collections.defaultdict(float)
 for r in rows:
  for k,v in r['counted'].items():counted[k]+=v
 result['counted_totals']=dict(counted)
 if any(r.get('remaining_all') is None for r in rows):return dict(result,status='unknown_remaining_pool',final_denominator=None)
 if any(not finite(r['remaining_all']) or r['remaining_all']<0 for r in rows):return dict(result,status='invalid_negative_or_nonfinite_pool',final_denominator=None)
 finals=dict(counted);unitout=[];u=0;remaining_all=0
 for r in rows:
  v=r['remaining_all'];p=r.get('pair_fraction');q=r.get('A_pair_share')
  if not finite(p) or not 0<=p<=1 or not finite(q):return dict(result,status='invalid_or_unknown_remaining_preferences')
  other=r.get('other_distribution',{})
  if any(not finite(x) or x<0 for x in other.values()) or A in other or B in other or not set(other)<=candidate_keys or (v*(1-p)>1e-9 and abs(sum(other.values())-1)>1e-9):return dict(result,status='invalid_named_other_distribution')
  up=v*p;qc=clip(q);u+=up;remaining_all+=v;add={A:up*qc,B:up*(1-qc)}
  for k,s in other.items():add[k]=v*(1-p)*s
  for k,x in add.items():finals[k]=finals.get(k,0)+x
  unitout.append(dict(key=r['key'],counted=dict(r['counted']),remaining_all=v,remaining_pair=up,raw_preference=q,clipped_preference=qc,preference_clipped=q!=qc,forecast_only_remaining=add,remaining_pair_net=up*(2*qc-1)))
 finalpair=counted.get(A,0)+counted.get(B,0)+u;finalall=sum(counted.values())+remaining_all;lead=counted.get(A,0)-counted.get(B,0);targets={}
 for label,target in [('tie',0),('Aplus1_final_pair_margin',.01*finalpair),('Aplus1_final_all_candidate_margin',.01*finalall)]:
  q=(u+target-lead)/(2*u) if u else None;targets[label]=requirement(q,u,lead,target);targets[label]['target_net']=target
 selected=[]
 for r in unitout:
  pool=r['remaining_pair'];fixed=lead+sum(x['remaining_pair_net'] for x in unitout if x['key']!=r['key']);target=.01*finalpair if spec.get('selected_target')=='Aplus1_final_pair_margin' else 0;q=(pool+target-fixed)/(2*pool) if pool else None
  selected.append(dict(key=r['key'],other_remaining_assumptions='Every other input unit at its explicitly stated clipped preference and remaining pool',fixed_other_net_plus_all_counted_lead=fixed,**requirement(q,pool,fixed,target)))
 net=finals.get(A,0)-finals.get(B,0);others={k:v for k,v in finals.items() if k not in [A,B]};opp=max([finals.get(B,0)]+list(others.values()))
 return dict(result,status='no_positive_pair_pool' if not u else 'calculated',units=unitout,final_candidate_totals=finals,final_pair_denominator=finalpair,final_all_candidate_denominator=finalall,remaining_all_pool=remaining_all,remaining_pair_pool=u,final_pair_net=net,final_pair_margin_pp=100*net/finalpair if finalpair else None,final_all_margin_pp=100*net/finalall if finalall else None,targets=targets,selected_unit_requirements=selected,A_strictly_exceeds_every_supplied_opponent=finals.get(A,0)>opp,legal_scope='Plurality requires exceeding every eligible individual candidate; supplied other buckets and identities are conditional inputs, not validated ballot/write-in eligibility. Pair tie/cushion alone is insufficient.')

def build():
 allout={};states=[];candidate_scenarios=[]
 source_candidates=readcsv(H/'candidate-votes.csv.gz');cvindex=collections.defaultdict(list)
 for r in source_candidates:cvindex[(r['level'],r['contest'],r['unit_key'])].append(r)
 for level,path in [('county',H.parent/'county-baselines.csv'),('native',H/'native-baselines.csv.gz'),('municipal',H/'municipal-baselines.csv.gz')]:
  data=readcsv(path);out=[]
  for cid in dict.fromkeys(r['contest'] for r in data):
   rows=[r for r in data if r['contest']==cid];res,st=historical(rows,settings='own-historical-volume');out+=res;states+=st
   if level=='county':
    for label,anchor in [('low-2022','2022-governor'),('base-2024','2024-senate'),('high-2020','2020-senate')]:
     vv={r['unit_key']:int(r['all_candidate_votes']) for r in data if r['contest']==anchor};res,st=historical(rows,vv,settings=label+'-mix-volume');out+=res;states+=st
    # Isolate volume scaling: keep2024 county mix; totals use actual low/high historical totals.
    basevol={r['unit_key']:int(r['all_candidate_votes']) for r in data if r['contest']=='2024-senate'}
    for label,anchor in [('low','2022-governor'),('high','2020-senate')]:
     scale=sum(int(r['all_candidate_votes']) for r in data if r['contest']==anchor)/sum(basevol.values());vv={k:v*scale for k,v in basevol.items()};res,st=historical(rows,vv,settings=label+'-volume-2024-fixed-mix');out+=res;states+=st
  writecsv(H/(level+'-targets.csv.gz'),out);allout[level]=len(out)
  grouped=collections.defaultdict(float);metadata={}
  for r in out:
   for candidate in cvindex[(level,r['contest'],r['unit_key'])]:
    key=(r['scenario'],r['contest'],level,r['target'],candidate['candidate_key']);metadata[key]=candidate
    if candidate['analytical_group']=='D':v=r['scenario_pair_votes']*r['target_share'] if r['target_share']!='' else 0
    elif candidate['analytical_group']=='R':v=r['scenario_pair_votes']*(1-r['target_share']) if r['target_share']!='' else 0
    else:v=r['scenario_all_votes']*int(candidate['votes'])/r['baseline_all_votes'] if r['baseline_all_votes'] else 0
    grouped[key]+=v
  for key,v in grouped.items():
   c=metadata[key];candidate_scenarios.append(dict(scenario=key[0],contest=key[1],level=key[2],target=key[3],candidate_key=key[4],candidate_name=c['candidate_name'],source_party=c['source_party'],scope=c['writein_scope'],scenario_votes=v))
 writecsv(H/'state-candidate-scenarios.csv',candidate_scenarios)
 dump(H/'state-scenarios.json',states)
 cases=[dict(id='clipping-required',shares=[.01,.9],weights=[10,100],target=0),dict(id='impossible-target',shares=[.5],weights=[100],target=101),dict(id='no-positive-pool',shares=[.5],weights=[0],target=0),dict(id='unknown-preference',shares=[None],weights=[100],target=0),dict(id='negative-weight-rejected',shares=[.5],weights=[-1],target=0),dict(id='already-winning-negative-shift',shares=[.6],weights=[100],target=0)]
 dump(H/'bounded-solver-cases.json',[dict(input=c,output=bounded(c['shares'],c['weights'],c['target'])) for c in cases])
 examples=json.loads((H/'live-scenarios-input.json').read_text());dump(H/'live-scenarios-output.json',[live(s) for s in examples]);print(json.dumps(dict(target_rows=allout,state_scenarios=len(states))))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--build',action='store_true');ap.add_argument('--live');ap.add_argument('--case');ap.add_argument('--contest',default='2024-senate');ap.add_argument('--level',choices=['county','native','municipal'],default='county');ap.add_argument('--unit');ap.add_argument('--others-shift-pp',type=float,default=0);args=ap.parse_args()
 if args.build:build()
 elif args.live:
  spec=json.loads(open(args.live).read())
  if isinstance(spec,list):
   matches=[r for r in spec if r['id']==args.case]
   if len(matches)!=1:ap.error('--case must name one case in a scenario list')
   spec=matches[0]
  print(json.dumps(live(spec),indent=2))
 else:
  path=H.parent/'county-baselines.csv' if args.level=='county' else H/(args.level+'-baselines.csv.gz');rr=[r for r in readcsv(path) if r['contest']==args.contest];res,st=historical(rr,others_shift_pp=args.others_shift_pp);print(json.dumps(dict(state=st,selected=[r for r in res if r['unit_key']==args.unit]),indent=2))

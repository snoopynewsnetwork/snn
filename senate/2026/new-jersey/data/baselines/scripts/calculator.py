#!/usr/bin/env python3
"""Offline deterministic historical and live-remainder arithmetic; no probabilities."""
import json,math,sys,argparse
class InputError(ValueError):pass
def number(x,label,lo=None,hi=None,unknown=False):
 if unknown and x is None:return None
 try:valid=type(x) in (int,float) and math.isfinite(x)
 except OverflowError:valid=False
 if not valid:raise InputError(label+' must be a finite number')
 if lo is not None and x<lo or hi is not None and x>hi:raise InputError(label+' outside allowed range')
 return x
def clip(s):return min(1,max(0,s))
def keys(units,expected=None):
 if not isinstance(units,list) or not units:raise InputError('units must be a nonempty list')
 seen=set()
 for u in units:
  if not isinstance(u,dict):raise InputError('unit must be an object')
  k=u.get('key')
  if not isinstance(k,str) or not k.strip() or k in seen:raise InputError('unit keys must be globally unique nonempty strings')
  seen.add(k)
 if expected is not None:
  if not isinstance(expected,list) or any(not isinstance(k,str) or not k.strip() for k in expected) or len(set(expected))!=len(expected):raise InputError('expected_keys must be unique nonempty strings')
  if seen!=set(expected):raise InputError('units differ from expected_keys: missing or extra units')
 return seen
def state(units,margin=0):
 """Each unit has fixed pair volume and explicit preference. Clipped uniform shift."""
 keys(units);number(margin,'margin',-1,1)
 for u in units:number(u['pair'],'pair',0);number(u['share'],'share',0,1)
 T=sum(u['pair'] for u in units);M=sum(u['pair']*(2*u['share']-1) for u in units)
 if T==0:return {'status':'no-positive-pool','pair_votes':0,'baseline_net':0,'unbounded_share_shift':None,'bounded_share_shift':None,'rows':[]}
 unbounded=(margin*T-M)/(2*T)
 def net(delta):return sum(u['pair']*(2*clip(u['share']+delta)-1) for u in units)
 lo=-1.;hi=1.
 for _ in range(90):
  mid=(lo+hi)/2
  if net(mid)<margin*T:lo=mid
  else:hi=mid
 delta=(lo+hi)/2
 rows=[]
 for u in units:
  share=clip(u['share']+delta);base=u['pair']*(2*u['share']-1);others=M-base
  if u['pair']>0:
   selected=(margin*T-others+u['pair'])/(2*u['pair']);status='already-secured' if selected<0 else 'impossible' if selected>1 else 'feasible'
  else:selected=None;status='no-positive-pool'
  rows.append({'key':u['key'],'pair':u['pair'],'weight':u['pair']/T,'base_share':u['share'],'base_net':base,'share_unbounded_target':u['share']+unbounded,'share_bounded_target':share,'share_change_pp':100*(share-u['share']),'clipped':u['share']+delta<0 or u['share']+delta>1,'target_margin_pp':100*(2*share-1),'target_net':u['pair']*(2*share-1),'net_gain':2*u['pair']*(share-u['share']),'net_gain_per_share_pp':.02*u['pair'],'selected_only_raw_share':selected,'selected_only_status':status,'other_units_fixed_net':others})
 return {'status':'feasible','baseline_already_pair_winning':M>0,'minimum_positive_improvement_pp':max(0,100*delta),'pair_votes':T,'baseline_net':M,'target_pair_margin':margin,'target_net':margin*T,'actual_net':sum(r['target_net'] for r in rows),'unbounded_share_shift':unbounded,'bounded_share_shift':delta,'unbounded_shift_pp':100*unbounded,'bounded_shift_pp':100*delta,'clipped_units':sum(r['clipped'] for r in rows),'rows':rows}
def threshold(raw,pool,fixed,target):
 if pool<=0:return {'raw_share':None,'bounded_share':None,'status':'no-positive-pool','fixed_meets_target':fixed>=target}
 return {'raw_share':raw,'bounded_share':clip(raw),'status':'already-secured' if raw<0 else 'impossible' if raw>1 else 'feasible'}
def live(obj):
 if not isinstance(obj,dict):raise InputError('input must be an object')
 units=obj.get('units');seen=keys(units,obj.get('expected_keys'));m=number(obj.get('target_margin',0),'target_margin',-1,1)
 denom=obj.get('denominator','pair')
 if denom not in ['pair','all']:raise InputError('denominator must be pair or all')
 selected=obj.get('selected_key')
 if selected is not None and (not isinstance(selected,str) or selected not in seen):raise InputError('selected_key is not a supplied unit key')
 A=B=O=0;other_counted={};pools=[];unknown=[]
 for u in units:
  k=u['key'];c=u.get('counted');r=u.get('remaining')
  if not isinstance(c,dict) or not isinstance(r,dict):raise InputError('every unit needs counted and remaining objects')
  for f in ['A','B']:
   x=number(c.get(f),k+' counted '+f,0)
   if type(x) is not int:raise InputError('counted votes must be integers')
  if not isinstance(c.get('others'),dict):raise InputError('counted others must be a candidate-name object')
  for name,x in c['others'].items():
   if not isinstance(name,str) or not name.strip() or name in ['A','B']:raise InputError('other candidate names must be distinct from A/B')
   number(x,'counted other',0)
   if type(x) is not int:raise InputError('counted votes must be integers')
   other_counted[name]=other_counted.get(name,0)+x
  A+=c['A'];B+=c['B'];O+=sum(c['others'].values())
  if 'contest_votes' not in r or 'pair_fraction' not in r or 'a_pair_share' not in r:raise InputError('remaining must explicitly state contest_votes, pair_fraction and a_pair_share; null means unknown')
  U=number(r['contest_votes'],'remaining contest_votes',0,unknown=True);p=number(r['pair_fraction'],'pair_fraction',0,1,unknown=True);q=number(r['a_pair_share'],'a_pair_share',0,1,unknown=True);shift=number(r.get('share_shift',0),'share_shift');mix=r.get('other_mix')
  if not isinstance(mix,dict):raise InputError('remaining other_mix must be a candidate-name object')
  for name,x in mix.items():
   if not isinstance(name,str) or not name.strip() or name in ['A','B']:raise InputError('remaining other names must be distinct from A/B')
   number(x,'other_mix fraction',0,1)
  if mix and not math.isclose(sum(mix.values()),1,abs_tol=1e-12):raise InputError('other_mix must sum to one')
  if U is not None and p is not None and U*(1-p)>0 and not mix:raise InputError('positive other remaining pool requires explicit other_mix')
  if U is None or p is None or (q is None and U*p>0):unknown.append(k)
  R=None if U is None or p is None else U*p;effective=None if q is None else clip(q+shift)
  pools.append({'key':k,'remaining_contest':U,'remaining_pair':R,'base_pair_share':q,'share_shift':shift,'unclipped_pair_share':None if q is None else q+shift,'pair_share':effective,'clipped':q is not None and effective!=q+shift,'other_mix':mix})
 fixed={'A':A,'B':B,'others':other_counted,'all_candidate_votes':A+B+O,'pair_votes':A+B,'net_A_minus_B':A-B}
 if unknown:return {'status':'unknown-assumptions','counted_fixed':fixed,'unknown_units':unknown,'projected_final':None,'conditional_threshold':None,'units':pools,'probability':None}
 U=sum(r['remaining_contest'] for r in pools);R=sum(r['remaining_pair'] for r in pools);finalpair=A+B+R;finalall=A+B+O+U;den=finalpair if denom=='pair' else finalall;target=m*den
 # Counted votes remain fixed; target margin uses the FINAL denominator.
 raw=(target-(A-B)+R)/(2*R) if R>0 else None;req=threshold(raw,R,A-B,target)
 PA=A+sum(r['remaining_pair']*(r['pair_share'] or 0) for r in pools);PB=B+sum(r['remaining_pair']*(1-(r['pair_share'] or 0)) for r in pools);others=dict(other_counted)
 for r in pools:
  for name,v in r['other_mix'].items():others[name]=others.get(name,0)+(r['remaining_contest']-r['remaining_pair'])*v
 cand={'A':PA,'B':PB,**others};largest=max(cand.values());winners=[n for n,v in cand.items() if math.isclose(v,largest,abs_tol=1e-8,rel_tol=0)]
 sel=None
 if selected is not None:
  chosen=next(r for r in pools if r['key']==selected);outside=(A-B)+sum(r['remaining_pair']*(2*(r['pair_share'] or 0)-1) for r in pools if r['key']!=selected);rp=chosen['remaining_pair'];q=(target-outside+rp)/(2*rp) if rp>0 else None;sel={**threshold(q,rp,outside,target),'other_units_fixed_net':outside,'selected_key':selected}
 bounded=None
 if R>0:
  uniform=state([{'key':r['key'],'pair':r['remaining_pair'],'share':r['pair_share'] or 0} for r in pools],margin=(target-(A-B))/R) if abs(target-(A-B))<=R else None
  bounded=None if uniform is None else {'shift':uniform['bounded_share_shift'],'clipped_units':uniform['clipped_units'],'remaining_net':uniform['actual_net']}
 pair_target_A=(A+B+R+target)/2 # meaningful pair A count only where target is attainable
 target_other_max=max(others.values(),default=0)
 return {'status':'conditional-arithmetic','counted_fixed':fixed,'remaining_contest_pool':U,'remaining_pair_pool':R,'final_pair_denominator':finalpair,'final_all_candidate_denominator':finalall,'target_margin':m,'target_denominator':denom,'target_net_A_minus_B':target,'conditional_threshold':req,'selected_only_threshold':sel,'bounded_uniform_remaining_shift':bounded,'projected_final':{'A':PA,'B':PB,'others':others,'net_A_minus_B':PA-PB,'pair_margin':(PA-PB)/finalpair if finalpair else None,'all_candidate_margin':(PA-PB)/finalall if finalall else None,'A_all_candidate_share':PA/finalall if finalall else None,'plurality_leaders':winners,'A_unique_plurality':winners==['A'],'pair_target_A_votes':pair_target_A,'pair_target_beats_largest_other':pair_target_A>target_other_max},'units':pools,'probability':None}
def strict_output(fn):
 def wrapped(*args,**kwargs):
  result=fn(*args,**kwargs)
  def check(x):
   if type(x) is float and not math.isfinite(x):raise InputError('arithmetic exceeded finite output bounds')
   if isinstance(x,dict):
    for v in x.values():check(v)
   if isinstance(x,list):
    for v in x:check(v)
  check(result);return result
 return wrapped
state=strict_output(state)
live=strict_output(live)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('input',nargs='?',default='-');args=ap.parse_args()
 try:
  data=json.load(sys.stdin if args.input=='-' else open(args.input),parse_constant=lambda x:(_ for _ in ()).throw(InputError('nonfinite JSON constant')));result=live(data);print(json.dumps(result,indent=2,allow_nan=False))
 except (InputError,ValueError,KeyError,TypeError,OverflowError) as e:
  print(json.dumps({'error':str(e)},allow_nan=False));return 2
 return 0
if __name__=='__main__':sys.exit(main())

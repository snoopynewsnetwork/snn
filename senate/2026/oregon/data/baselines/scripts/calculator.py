"""Offline deterministic historical and fixed-counted/remainder arithmetic. No probabilities."""
import csv,json,math,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class Invalid(ValueError):pass
def number(x,name,lo=None,hi=None):
 if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x):raise Invalid(name+' must be a finite numeric scalar')
 if lo is not None and x<lo or hi is not None and x>hi:raise Invalid(name+' out of range')
 return x
def mapping(x,name):
 if not isinstance(x,dict):raise Invalid(name+' must be an object')
 return x
def total(xs,name='sum'):
 x=math.fsum(xs);return number(x,name,0)
def units(raw):
 if not isinstance(raw,list):raise Invalid('units must be an array')
 seen=set();out=[]
 for item in raw:
  mapping(item,'unit');key=item.get('key')
  if not isinstance(key,str) or not key.strip() or key in seen:raise Invalid('duplicate, empty or nonstring source-unit key')
  seen.add(key);T=number(item.get('pair_volume'),'pair_volume',0);p=item.get('share')
  if p is not None:p=number(p,'share',0,1)
  out.append({'key':key,'pair_volume':T,'share':p})
 total([r['pair_volume'] for r in out]);return out
def validate_scope(arg,u):
 scope=arg.get('source_scope','synthetic_explicit_units')
 if scope=='synthetic_explicit_units':return
 if scope=='county':
  valid={r['county'] for r in csv.DictReader((R.parent/'county-baselines.csv').open())}
 elif scope=='native':valid={r['unit_key'] for r in json.loads((R/'native-units.json').read_text())}
 else:raise Invalid('unsupported source_scope')
 if any(r['key'] not in valid for r in u):raise Invalid('unknown source-unit key')
 if scope=='county' and {r['key'] for r in u}!=valid:raise Invalid('county source_scope requires all36 units')
def margin_target(arg):
 return number(arg['target_margin'] if 'target_margin' in arg else 0,'target_margin',-1,1)
def solve(arg):
 mapping(arg,'input');u=units(arg.get('units'));validate_scope(arg,u);m=margin_target(arg);T=total([r['pair_volume'] for r in u]);target=m*T
 baseline=None if any(r['share'] is None and r['pair_volume']>0 for r in u) else math.fsum(r['pair_volume']*(2*(r['share'] or 0)-1) for r in u)
 if T==0:return {'status':'no_positive_pool','pair_volume':0,'target_margin':m,'unbounded_share_shift':None,'bounded_share_shift':None,'units':u}
 if baseline is None:return {'status':'unknown_source_preference','pair_volume':T,'target_margin':m,'unbounded_share_shift':None,'bounded_share_shift':None,'units':u}
 d=(target-baseline)/(2*T)
 def net(s):return math.fsum(r['pair_volume']*(2*min(1,max(0,(r['share'] or 0)+s))-1) for r in u)
 lo=-1.;hi=1.
 if target<net(lo)-1e-8 or target>net(hi)+1e-8:return {'status':'impossible_bounded_target','pair_volume':T,'unbounded_share_shift':d}
 for _ in range(100):
  mid=(lo+hi)/2
  if net(mid)<target:lo=mid
  else:hi=mid
 shift=(lo+hi)/2;rows=[]
 for r in u:
  p=r['share'];q=min(1,max(0,(p or 0)+shift));t=r['pair_volume'];base=t*(2*(p or 0)-1)
  rows.append({**r,'weight':t/T,'unbounded_target_share':None if p is None else p+d,'target_share':q if p is not None else None,'clipped':p is not None and not 0<=p+shift<=1,'target_pair_margin':2*q-1 if p is not None else None,'status':'no_positive_pool' if t==0 else 'feasible','baseline_net_votes':base,'target_net_votes':t*(2*q-1),'net_vote_gain':t*2*(q-(p or 0)),'gain_per_A_share_point':.02*t})
 achieved=net(shift)
 return {'status':'already_at_or_above_target' if baseline>=target else 'requires_improvement','target_margin':m,'pair_volume':T,'baseline_net_votes':baseline,'target_net_votes':target,'unbounded_share_shift':d,'unbounded_share_shift_points':100*d,'bounded_share_shift':shift,'bounded_share_shift_points':100*shift,'achieved_net_votes':achieved,'residual_net_votes':achieved-target,'bounded_feasible':abs(achieved-target)<=max(1e-7,T*1e-12),'units':rows}
def selected(arg):
 mapping(arg,'input');u=units(arg.get('units'));validate_scope(arg,u);m=margin_target(arg);key=arg.get('selected')
 if not isinstance(key,str) or not key.strip() or key not in {r['key'] for r in u}:raise Invalid('unknown selected source-unit key')
 s=next(r for r in u if r['key']==key);T=total([r['pair_volume'] for r in u]);others=[r for r in u if r['key']!=key]
 if any(r['share'] is None and r['pair_volume']>0 for r in others):return {'status':'unknown_other_unit_preference','selected':key,'required_share':None}
 other=math.fsum(r['pair_volume']*(2*(r['share'] or 0)-1) for r in others);need=m*T-other;t=s['pair_volume']
 base={'selected':key,'target_margin':m,'pair_volume':T,'selected_pair_volume':t,'other_net_votes_fixed':other,'other_units_fixed':others,'selected_baseline_share':s['share']}
 if t==0:return {**base,'status':'no_positive_pool','required_share':None,'unbounded_required_share':None,'fixed_net_votes_meet_target':other>=m*T}
 q=(need/t+1)/2
 return {**base,'status':'secured_even_at_zero' if q<0 else 'impossible_even_at_one' if q>1 else 'feasible','unbounded_required_share':q,'required_share':min(1,max(0,q)),'required_change_from_source_share':None if s['share'] is None else q-s['share'],'feasible':0<=q<=1,'required_net_votes':need}
def historical(arg):
 mapping(arg,'input');kind=arg.get('mode','county');pref=arg.get('preference','2024-president');m=margin_target(arg)
 if kind not in ['county','native']:raise Invalid('unsupported geography')
 if arg.get('denominator','reported_all_choice')!='reported_all_choice':raise Invalid('unsupported denominator')
 candidates=list(csv.DictReader((R/'county-candidates.csv').open()));known=set(r['contest'] for r in candidates)
 if pref not in known:raise Invalid('unknown preference contest')
 mix=arg.get('mix',{'2024-president':1})
 mapping(mix,'mix')
 if not mix or any(k not in (list(known) if kind=='native' else ['2020-senate','2022-senate','2022-governor','2024-president']) for k in mix):raise Invalid('invalid historical volume mix keys')
 for v in mix.values():number(v,'mix weight',0,1)
 if abs(total(list(mix.values()))-1)>1e-12:raise Invalid('mix weights must sum to one')
 wide=list(csv.DictReader((R.parent/'county-baselines.csv').open()));idx={(r['contest'],r['county']):r for r in wide};counties=sorted({r['county'] for r in wide})
 if 'county' in arg and arg['county'] not in counties:raise Invalid('unknown county')
 if kind=='native':
  if mix!={pref:1}:raise Invalid('native cross-year or cross-contest join unsupported')
  rs=[r for r in json.loads((R/'native-units.json').read_text()) if r['contest']==pref]
  # Only independently column-closed source scopes; select one actual publication per county.
  recon=json.loads((R/'native-reconciliation.json').read_text());closed={r['source_key'] for r in recon if r['contest']==pref and r['column_closed']};chosen={}
  for r in rs:
   if r['source_key'] in closed:chosen.setdefault(r['county'],r['source_key'])
  rs=[r for r in rs if chosen.get(r['county'])==r['source_key']];u=[{'key':r['unit_key'],'pair_volume':r['pair_votes'] or 0,'share':r['A_pair_share']} for r in rs]
  result=solve({'units':u,'target_margin':m});return {'scope':'known column-closed historical native source scope only; other counties unmodeled, never statewide','preference':pref,'mix':mix,'result':result,'statewide_native_dispatch':None}
 u=[];field=[]
 for c in counties:
  r=idx[pref,c];volume=math.fsum(float(idx[k,c]['reported_all_choice_votes'])*w for k,w in mix.items());participation=float(r['pair_participation_in_reported_all_choice']);T=volume*participation;p=float(r['A_pair_share']);u.append({'key':c,'pair_volume':T,'share':p})
  field.append({'county':c,'reported_all_choice_volume':volume,'pair_participation':participation,'other_reported_volume':volume-T,'A':r['A'],'B':r['B'],'other_candidates':{x['candidate']:volume*int(x['votes'])/int(r['reported_all_choice_votes']) for x in candidates if x['contest']==pref and x['county']==c and x['candidate'] not in [r['A'],r['B']]}})
 result=selected({'units':u,'selected':arg['county'],'target_margin':m}) if 'county' in arg else solve({'units':u,'target_margin':m})
 V=total([r['reported_all_choice_volume'] for r in field]);out={'scope':'all36 historical county scenario','preference':pref,'mix':mix,'volume_basis':'reported_all_choice including generic Misc.; no under/over/returned ballots in denominator','denominator':'reported_all_choice','historical_volume':V,'result':result,'county_volume_and_full_field':field,'current_source_accepted':False,'geography_accepted':False}
 if 'county' not in arg and 'target_net_votes' in result:
  a=(result['pair_volume']+result['target_net_votes'])/2;b=result['pair_volume']-a;other={}
  for r in field:
   for name,v in r['other_candidates'].items():other[name]=other.get(name,0)+v
  out.update(A_final=a,B_final=b,A_all_choice_share=a/V if V else None,A_minus_B_all_choice_margin=result['target_net_votes']/V if V else None,other_final=other,A_beats_each_named_other=all(a>v for name,v in other.items() if name!='Misc.'),generic_Misc_eligibility='unknown; arithmetic lane retained, not one legal candidate')
 return out

def live(arg):
 mapping(arg,'input');m=margin_target(arg)
 if arg.get('denominator','final_pair') not in ['final_pair','final_all_choice']:raise Invalid('unsupported denominator')
 denom=arg.get('denominator','final_pair');counted=mapping(arg.get('counted'),'counted');A=number(counted.get('A'),'counted A',0);B=number(counted.get('B'),'counted B',0);other=mapping(counted.get('other',{}),'counted other')
 for k,v in other.items():
  if not isinstance(k,str) or not k.strip() or k in ['A','B']:raise Invalid('invalid other candidate key')
  number(v,'counted other',0)
 if not isinstance(arg.get('remaining'),list):raise Invalid('remaining must be array')
 seen=set();U=[];rother={};unknown=False
 for raw in arg['remaining']:
  r=mapping(raw,'remaining unit');key=r.get('key')
  if not isinstance(key,str) or not key.strip() or key in seen:raise Invalid('duplicate, empty or nonstring source-unit key')
  seen.add(key);v=r.get('volume');p=r.get('pair_participation');q=r.get('share')
  if v is not None:v=number(v,'remaining volume',0)
  if p is not None:p=number(p,'pair_participation',0,1)
  if q is not None:q=number(q,'remaining share',0,1)
  allocation=r.get('other_allocation',{})
  mapping(allocation,'other allocation')
  for k,w in allocation.items():
   if not isinstance(k,str) or not k.strip() or k in ['A','B']:raise Invalid('invalid remaining other key')
   number(w,'other allocation weight',0,1)
  # Allocation is a distribution of NONPAIR remaining votes, not all votes.
  if v is not None and p is not None and v*(1-p)>0 and abs(total(list(allocation.values()))-1)>1e-12:raise Invalid('other allocation must sum to one for positive nonpair pool')
  if allocation and abs(total(list(allocation.values()))-1)>1e-12:raise Invalid('other allocation must sum to one')
  if v is None or p is None:unknown=True;U.append({'key':key,'pair_volume':0,'share':q});continue
  U.append({'key':key,'pair_volume':v*p,'share':q})
  for k,w in allocation.items():rother[k]=rother.get(k,0)+v*(1-p)*w
  if q is None and v*p>0:unknown=True
 if 'selected' in arg:
  key=arg['selected']
  if not isinstance(key,str) or not key.strip() or key not in seen:raise Invalid('unknown selected source-unit key')
 # Type/duplicate validation always precedes unknown propagation.
 upair=total([r['pair_volume'] for r in U]);finalpair=total([A,B,upair]);otherfinal={k:other.get(k,0)+rother.get(k,0) for k in set(other)|set(rother)};finalall=total([finalpair,*otherfinal.values()]);den=finalpair if denom=='final_pair' else finalall
 out={'counted_fixed':{'A':A,'B':B,'other':other},'remaining_units':U,'denominator':denom,'target_margin':m,'probability':None,'scope':'conditional arithmetic; remaining pool/preferences supplied, not inferred'}
 if unknown:return {**out,'status':'unknown_remaining_volume_mix_or_preference','final_denominator':None if any(r.get('volume') is None or r.get('pair_participation') is None for r in arg['remaining']) else den,'required_remaining_A_share':None,'known_partial_remaining_pair_volume':upair}
 target=m*den;lead=A-B;netrem=math.fsum(r['pair_volume']*(2*(r['share'] or 0)-1) for r in U);FA=A+(upair+netrem)/2;FB=B+(upair-netrem)/2
 q=None if upair==0 else (target-lead+upair)/(2*upair)
 status=('no_positive_pool' if upair==0 else 'secured_even_at_zero' if q<0 else 'impossible_even_at_one' if q>1 else 'feasible')
 out.update(status=status,final_denominator=den,final_pair_volume=finalpair,final_all_choice_volume=finalall,remaining_pair_volume=upair,unbounded_required_remaining_A_share=q,required_remaining_A_share=None if q is None else min(1,max(0,q)),required_remaining_share_clipped=q is not None and not 0<=q<=1,final_A=FA,final_B=FB,final_other=otherfinal,final_pair_net_votes=FA-FB,final_margin=(FA-FB)/den if den else None,A_strict_plurality=FA>FB and all(FA>v for v in otherfinal.values()),named_full_field_winner=max({'A':FA,'B':FB,**otherfinal},key={'A':FA,'B':FB,**otherfinal}.get),plurality_tie=len([v for v in [FA,FB,*otherfinal.values()] if v==max([FA,FB,*otherfinal.values()])])>1)
 leaders=[k for k,v in {'A':FA,'B':FB,**otherfinal}.items() if v==max([FA,FB,*otherfinal.values()])]
 out['arithmetic_full_field_leaders']=leaders
 if len(leaders)>1:out['named_full_field_winner']=None
 out['actual2026_ballot_mapping']=None
 if 'selected' in arg:
  key=arg['selected']
  if not isinstance(key,str) or not key.strip() or key not in seen:raise Invalid('unknown selected source-unit key')
  s=next(r for r in U if r['key']==key);othernet=lead+math.fsum(r['pair_volume']*(2*(r['share'] or 0)-1) for r in U if r['key']!=key);t=s['pair_volume'];req=(target-othernet+t)/(2*t) if t>0 else None
  out['selected_only']={'key':key,'other_counted_and_remaining_net_fixed':othernet,'required_share_unbounded':req,'required_share':None if req is None else min(1,max(0,req)),'status':'no_positive_pool' if req is None else 'secured_even_at_zero' if req<0 else 'impossible_even_at_one' if req>1 else 'feasible'}
 return out

def run(arg):
 mapping(arg,'input');mode=arg.get('mode')
 if mode in ['county','native']:return historical(arg)
 if mode=='uniform':return solve(arg)
 if mode=='selected':return selected(arg)
 if mode=='live':return live(arg)
 raise Invalid('unsupported mode')
def main():
 try:
  raw=Path(sys.argv[1]).read_text() if len(sys.argv)==2 and sys.argv[1]!='-' else sys.stdin.read();arg=json.loads(raw,parse_constant=lambda x:(_ for _ in ()).throw(Invalid('nonfinite JSON number')));out={'ok':True,'result':run(arg)}
 except (Invalid,ValueError,TypeError,KeyError,OverflowError,OSError) as e:out={'ok':False,'error':{'type':'invalid_input','message':str(e) if isinstance(e,Invalid) else 'malformed input or unsupported value'}}
 try:print(json.dumps(out,indent=2,allow_nan=False))
 except (ValueError,OverflowError):print('{"ok":false,"error":{"type":"invalid_input","message":"arithmetic overflow"}}')
if __name__=='__main__':main()

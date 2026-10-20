#!/usr/bin/env python3
"""Offline conditional arithmetic; no ingestion, calibration or probabilities."""
import json,math,sys
class Invalid(ValueError):pass
def num(v,name,lo=0,hi=None):
 if type(v) not in (int,float) or not math.isfinite(v) or v<lo or (hi is not None and v>hi):raise Invalid(name+' must be a finite number in bounds')
 return v
def ident(v,name):
 if not isinstance(v,str) or not v.strip():raise Invalid(name+' must be a nonblank string')
 return v
def pairs(items):
 d={}
 for k,v in items:
  if k in d:raise Invalid('duplicate JSON object field: '+k)
  d[k]=v
 return d
def total(xs):
 try:v=math.fsum(xs)
 except (OverflowError,ValueError):raise Invalid('aggregate numeric overflow')
 if not math.isfinite(v):raise Invalid('aggregate numeric overflow')
 return v
def calculate(d):
 if not isinstance(d,dict):raise Invalid('input must be an object')
 if set(d)-{'mode','objective','pair','other_candidates','units','target_margin','selected_unit','assumptions','source_scope'}:raise Invalid('unsupported setting')
 if d.get('mode') not in ['historical','live']:raise Invalid('mode must be historical or live')
 objective=d.get('objective','pair_margin')
 if objective not in ['pair_margin','full_candidate_plurality']:raise Invalid('unsupported objective')
 target=num(d.get('target_margin',0),'target_margin',-1,1)
 pair=d.get('pair');others=d.get('other_candidates')
 if not isinstance(pair,list) or len(pair)!=2 or not isinstance(others,list):raise Invalid('pair and other_candidates must be lists; pair length 2')
 candidates=[ident(c,'candidate') for c in pair+others]
 if len(set(candidates))!=len(candidates):raise Invalid('candidate identities collide')
 units=d.get('units')
 if not isinstance(units,list) or not units:raise Invalid('units must be a nonempty list')
 keys=[];clean=[]
 for u in units:
  if not isinstance(u,dict) or set(u)-{'key','counted','counted_total','remaining','pair_participation','a_share','other_allocation','assumptions'}:raise Invalid('malformed unit')
  key=ident(u.get('key'),'unit key');keys.append(key)
  c=u.get('counted')
  if not isinstance(c,dict) or set(c)!=set(candidates):raise Invalid('counted must explicitly supply every candidate')
  for n,v in c.items():num(v,'counted '+n)
  ct=total(c.values())
  if 'counted_total' in u and num(u['counted_total'],'counted_total')!=ct:raise Invalid('counted_total does not equal complete supplied field')
  r=num(u.get('remaining'),'remaining');p=num(u.get('pair_participation'),'pair_participation',0,1)
  q=u.get('a_share')
  if q is not None:num(q,'a_share',0,1)
  alloc=u.get('other_allocation')
  if not isinstance(alloc,dict) or set(alloc)!=set(others):raise Invalid('other_allocation must supply exactly all other candidates')
  for n,v in alloc.items():num(v,'other_allocation '+n,0,1)
  if others:
   if abs(total(alloc.values())-1)>1e-12:raise Invalid('other allocations must sum to 1')
  elif p!=1:raise Invalid('pair participation must be 1 when no other candidate is supplied')
  clean.append(dict(key=key,counted=c,remaining=r,pair_participation=p,a_share=q,other_allocation=alloc,pair_pool=r*p))
 if len(set(keys))!=len(keys):raise Invalid('globally duplicate unit keys')
 selected=d.get('selected_unit')
 if selected is not None and (ident(selected,'selected_unit') not in keys):raise Invalid('selected unit missing')
 A,B=pair;counted={c:total(u['counted'][c] for u in clean) for c in candidates}
 R=total(u['remaining'] for u in clean);U=total(u['pair_pool'] for u in clean)
 F=total([counted[A],counted[B],U]);full=total([*counted.values(),R]);L=counted[A]-counted[B]
 wanted=target*(F if objective=='pair_margin' else full)
 num(abs(wanted),'derived target');unknown=[u['key'] for u in clean if u['pair_pool']>0 and u['a_share'] is None]
 def final(shares):
  vals={c:counted[c] for c in candidates}
  for u,q in zip(clean,shares):
   pool=u['pair_pool'];vals[A]=total([vals[A],pool*(q or 0)]);vals[B]=total([vals[B],pool*(1-(q or 0))])
   for c in others:vals[c]=total([vals[c],u['remaining']*(1-u['pair_participation'])*u['other_allocation'][c]])
  return vals
 def score(v):return v[A]-v[B] if objective=='pair_margin' else v[A]-max(v[c] for c in candidates if c!=A)
 def describe(v):
  lead=v[A]-v[B];rivals=max(v[c] for c in candidates if c!=A)
  return {'votes':v,'pair_total':F,'all_candidate_total':full,'pair_net_votes':lead,'pair_margin':lead/F if F else None,'all_candidate_pair_margin':lead/full if full else None,'a_full_field_lead':v[A]-rivals,'a_full_field_status':'ahead' if v[A]>rivals else 'tied' if v[A]==rivals else 'behind','objective_residual_net_votes':score(v)-wanted}
 base=[u['a_share'] for u in clean];result={'status':'unknown' if unknown else 'ok','mode':d['mode'],'objective':objective,'named_pair':pair,'other_candidates':others,'source_scope':d.get('source_scope'),'assumptions':d.get('assumptions'),'counted_fixed':counted,'remaining_all_candidates':R,'remaining_pair':U,'final_pair_denominator':F,'final_all_candidate_denominator':full,'target_margin':target,'target_net_votes':wanted,'unknown_positive_pair_pool_units':unknown,'pool_status':'positive' if U>0 else 'no-positive-pool','baseline':None,'uniform':None,'selected':None,'units':[]}
 if not unknown:
  v=final(base);result['baseline']=describe(v)
  unbounded=(target*F-(v[A]-v[B]))/(2*U) if U else None
  if U:
   lo=describe(final([0 for u in clean]));hi=describe(final([1 for u in clean]));minscore=lo['objective_residual_net_votes'];maxscore=hi['objective_residual_net_votes']
   if minscore>0:status='secured';root=None
   elif maxscore<0:status='impossible';root=None
   else:
    status='feasible';left,right=-1.,1.
    for _ in range(80):
     mid=(left+right)/2;val=final([min(1,max(0,(q or 0)+mid)) for q in base])
     if score(val)<wanted:left=mid
     else:right=mid
    root=(left+right)/2
   result['uniform']={'status':status,'unbounded_pair_share_shift':unbounded,'bounded_common_share_shift':root,'at_min':lo,'at_max':hi,'target':describe(final([min(1,max(0,(q or 0)+root)) for q in base])) if root is not None else None,'clipped_units':[u['key'] for u,q in zip(clean,base) if root is not None and u['pair_pool']>0 and ((q or 0)+root<0 or (q or 0)+root>1)]}
  else:result['uniform']={'status':'no-positive-pool','fixed_target_status':'met' if score(v)>=wanted else 'unmet','unbounded_pair_share_shift':None,'bounded_common_share_shift':None}
 if selected is not None:
  i=keys.index(selected);u=clean[i];unknown_other=[k for k in unknown if k!=selected];pool=u['pair_pool']
  if unknown_other:sel={'status':'unknown-other-unit-preferences','unknown_units':unknown_other}
  else:
   q0=list(base);q0[i]=0;v0=final(q0)
   if not pool:sel={'status':'no-positive-pool','required_a_share_raw':None,'fixed_target_status':'met' if score(v0)>=wanted else 'unmet'}
   else:
    pair_req=(target*F-(v0[A]-v0[B]))/(2*pool)
    # Full-field threshold holds every other candidate allocation and all other units fixed.
    full_req=max([(target*full-(v0[A]-v0[B]))/(2*pool)]+[(target*full-(v0[A]-v0[c]))/pool for c in others])
    req=pair_req if objective=='pair_margin' else full_req
    sel={'status':'secured' if req<0 else 'impossible' if req>1 else 'feasible','required_a_share_raw':req,'required_pair_share_raw':pair_req,'required_full_plurality_share_raw':full_req,'required_a_share_clipped':min(1,max(0,req)),'others_fixed_at_supplied_assumptions':True}
  result['selected']={'key':selected,**sel}
 for u,q in zip(clean,base):
  pool=u['pair_pool'];delta=result['uniform'].get('bounded_common_share_shift') if result['uniform'] else None
  tq=min(1,max(0,q+delta)) if q is not None and delta is not None else None
  result['units'].append({'key':u['key'],'pair_pool':pool,'pair_participation':u['pair_participation'],'state_final_pair_weight':pool/F if F else None,'remaining_pool_weight':pool/U if U else None,'baseline_a_share':q if pool else None,'baseline_remaining_net':pool*(2*q-1) if q is not None else (0 if pool==0 else None),'target_a_share':tq if pool else None,'target_remaining_net':pool*(2*tq-1) if tq is not None else (0 if pool==0 else None),'net_gain_per_one_share_point':.02*pool,'counted_fixed':u['counted'],'remaining_other_votes':{c:u['remaining']*(1-u['pair_participation'])*u['other_allocation'][c] for c in others}})
 # Check every derived float, including overflow caused by subtraction/multiplication.
 def check(v):
  if isinstance(v,float) and not math.isfinite(v):raise Invalid('derived numeric overflow')
  if isinstance(v,dict):
   for x in v.values():check(x)
  if isinstance(v,list):
   for x in v:check(x)
 check(result);return result

def main():
 try:
  if len(sys.argv)!=2:raise Invalid('usage: calculator.py INPUT.json (or - for stdin)')
  raw=sys.stdin.read() if sys.argv[1]=='-' else open(sys.argv[1]).read()
  d=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda v:(_ for _ in ()).throw(Invalid('nonfinite JSON token '+v)))
  result=calculate(d);print(json.dumps(result,ensure_ascii=False,allow_nan=False));return 0
 except (Invalid,ValueError,TypeError,KeyError,OverflowError,OSError,ZeroDivisionError) as e:
  print(json.dumps({'status':'invalid-input','error':str(e)},allow_nan=False));return 2
if __name__=='__main__':sys.exit(main())

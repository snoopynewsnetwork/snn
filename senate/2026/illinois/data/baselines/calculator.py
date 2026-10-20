"""Offline deterministic pair and full-field plurality arithmetic; no probabilities.

Amounts may be fractional scenario expectations. Shares are fractions, not pp.
Every counted candidate remains fixed. Unknown and negative pools stay explicit.
"""
import argparse,json,math
from pathlib import Path

def clip(s):return max(0.,min(1.,s))
def number(v):
    if type(v)not in(int,float):return False
    try:return math.isfinite(v)
    except OverflowError:return False
def bounded_shift(units,target_margin=0):
    # All supplied units retained, including zero-volume units.
    if not math.isfinite(target_margin):return {'status':'invalid_target'}
    if any(not math.isfinite(u['volume'])or u['volume']<0 for u in units):return {'status':'invalid_volume'}
    total=sum(u['volume']for u in units)
    if total<=0:return {'status':'no_positive_pool','shift':None,'total':total}
    if any(u['volume']>0 and (u.get('share')is None or not math.isfinite(u['share'])or not 0<=u['share']<=1)for u in units):return {'status':'unknown_preference','shift':None,'total':total}
    if abs(target_margin)>1:return {'status':'impossible','shift':None,'total':total}
    base=sum(u['volume']*(2*u['share']-1)for u in units if u['volume']>0)
    unbounded=(target_margin-base/total)/2
    def net(d):return sum(u['volume']*(2*clip(u['share']+d)-1)for u in units if u['volume']>0)
    lo,hi=-1.,1.
    for _ in range(100):
        mid=(lo+hi)/2
        if net(mid)<target_margin*total:lo=mid
        else:hi=mid
    delta=(lo+hi)/2
    return {'status':'feasible','total':total,'baseline_net':base,'baseline_margin':base/total,'target_margin':target_margin,'target_net':target_margin*total,'unbounded_shift':unbounded,'shift':delta,'achieved_net':net(delta),'clipped_units':sum(u['volume']>0 and not 0<=u['share']+delta<=1 for u in units),'already_A_winning':base>0,'positive_improvement_needed':max(0.,delta)}

def selected_only(volume,other_net,total,target_margin=0):
    if not number(target_margin)or not -1<=target_margin<=1:return {'status':'invalid_target_margin','required_share':None}
    if volume is None:return {'status':'unknown_pool','required_share':None}
    if not math.isfinite(volume)or volume<0:return {'status':'invalid_negative_pool','required_share':None}
    target=target_margin*total
    if volume==0:return {'status':'no_positive_pool_secured' if other_net>target else 'no_positive_pool_tie' if other_net==target else 'no_positive_pool_impossible','required_share':None}
    q=(volume+target-other_net)/(2*volume)
    return {'status':'already_secured' if q<0 else 'impossible' if q>1 else 'feasible','required_share':q,'bounded_share':clip(q),'equality_at_boundary':q in (0,1)}

def live(case):
    if not isinstance(case,dict):return {'status':'invalid_case_object'}
    counted=case.get('counted',{});A=case.get('A','A');B=case.get('B','B')
    if not isinstance(counted,dict):return {'status':'invalid_counted_object'}
    if not all(isinstance(k,str)and k.strip()for k in counted):return {'status':'invalid_counted_candidate_keys'}
    if not isinstance(A,str)or not A.strip()or not isinstance(B,str)or not B.strip()or A==B or A not in counted or B not in counted:return {'status':'invalid_candidate_identities'}
    if any(not number(v)or v<0 for v in counted.values()):return {'status':'invalid_counted_votes'}
    if not number(sum(counted.values())):return {'status':'invalid_counted_total_range'}
    target=case.get('selected_target_pair_margin',0)
    if not number(target)or not -1<=target<=1:return {'status':'invalid_selected_target_pair_margin','expected':'finite numeric fraction within[-1,1]; null, text and nonfinite values rejected'}
    pools=case.get('remaining',[])
    if not isinstance(pools,list)or any(not isinstance(p,dict)for p in pools):return {'status':'invalid_remaining_pool_list'}
    keys=[p.get('unit')for p in pools]
    if any(not isinstance(k,str)or not k.strip()for k in keys):return {'status':'invalid_remaining_unit_key','expected':'nonempty source unit key on every remaining pool, including zero pools'}
    if len(set(keys))!=len(keys):return {'status':'duplicate_remaining_unit_key','expected':'one remaining forecast per exact source unit key; duplicate pools rejected globally'}
    if 'selected_unit'in case and (not isinstance(case['selected_unit'],str)or not case['selected_unit'].strip()):return {'status':'invalid_selected_unit_key'}
    # Validate every provided type before arithmetic, even on zero-volume pools.
    for p in pools:
        n=p.get('votes');rho=p.get('pair_participation');q=p.get('A_pair_share')
        if n is not None and not number(n):return {'status':'invalid_remaining_votes_type','expected':'finite numeric votes or null for unknown'}
        if rho is not None and (not number(rho)or not 0<=rho<=1):return {'status':'invalid_pair_participation','expected':'finite numeric fraction within[0,1] or null for unknown'}
        if q is not None and not number(q):return {'status':'invalid_remaining_share_type','expected':'finite numeric A pair share or null for unknown; finite out-of-range shares explicitly clipped'}
        split=p.get('other_shares',{})
        if not isinstance(split,dict)or any(not isinstance(k,str)or not k.strip()or k in[A,B]or not number(v)or v<0 or v>1 for k,v in split.items()):return {'status':'invalid_other_share_allocation'}
        if split and abs(sum(split.values())-1)>1e-10:return {'status':'invalid_other_share_allocation'}
    if any(p.get('votes')is None for p in pools):return {'status':'unknown_remaining_pool','counted_fixed':counted}
    if any(p['votes']<0 for p in pools):return {'status':'invalid_negative_pool','counted_fixed':counted}
    if not number(sum(p['votes']for p in pools)):return {'status':'invalid_remaining_total_range'}
    final={k:float(v)for k,v in counted.items()};pair_remaining=0.;other_remaining=0.;clip_events=[]
    for p in pools:
        n=p['votes'];rho=p.get('pair_participation')
        if n==0:continue
        if rho is None:return {'status':'unknown_pair_participation','counted_fixed':counted}
        q=p.get('A_pair_share')
        if n*rho>0 and q is None:return {'status':'unknown_remaining_preference','counted_fixed':counted}
        q0=clip(q) if q is not None else 0.
        if q is not None and q0!=q:clip_events.append({'unit':p.get('unit'),'input':q,'clipped':q0})
        u=n*rho;pair_remaining+=u;other_remaining+=n-u
        final[A]+=u*q0;final[B]+=u*(1-q0)
        split=p.get('other_shares',{})
        if n-u>1e-10 and abs(sum(split.values())-1)>1e-10:return {'status':'unknown_or_invalid_other_allocation','counted_fixed':counted}
        for k,s in split.items():final[k]=final.get(k,0.)+(n-u)*s
    total=sum(final.values());pair=final[A]+final[B];lead=final[A]-final[B]
    if not all(number(v)for v in [total,pair,lead,*final.values()]):return {'status':'invalid_final_arithmetic_range'}
    L=counted[A]-counted[B]
    tie=selected_only(pair_remaining,L,pair,0)
    cushion=selected_only(pair_remaining,L,pair,.01)
    competitors={k:v for k,v in final.items()if k!=A};opponent=max(competitors,key=competitors.get) if competitors else None
    legal='A_plurality' if opponent is None or final[A]>competitors[opponent] else 'tie_for_first' if final[A]==competitors[opponent] else 'A_not_plurality'
    # Full-field threshold: named other forecasts fixed, B gets complementary pair votes.
    bounds={B:(pair_remaining+counted[B]-counted[A])/(2*pair_remaining)}if pair_remaining>0 else {}
    if pair_remaining>0:
        bounds.update({k:(v-counted[A])/pair_remaining for k,v in competitors.items()if k!=B})
    full=max(bounds.values()) if bounds else None
    out={'status':'calculated' if pair_remaining>0 else 'no_positive_pair_pool','counted_fixed':counted,'remaining_total_contest_votes':sum(p['votes']for p in pools),'remaining_pair_votes':pair_remaining,'remaining_other_votes':other_remaining,'final':final,'final_all_candidate_denominator':total,'final_pair_denominator':pair,'final_pair_net':lead,'final_pair_margin':lead/pair if pair else None,'final_all_candidate_margin_A_minus_B':lead/total if total else None,'final_A_all_candidate_share':final[A]/total if total else None,'pair_tie_threshold':tie,'pair_A_plus1_threshold':cushion,'full_field_tie_lower_bound_A_remaining_share':full,'full_field_strict_plurality_requires_greater_than_bound':True,'full_field_threshold_status':'no_positive_pool' if full is None else 'already_secured' if full<0 else 'impossible' if full>=1 else 'feasible','legal_plurality_outcome':legal,'largest_competitor':opponent,'clip_events':clip_events}
    out['candidate_universe_scope']='Conditional on supplied candidate IDs and other-vote allocations; completeness and current ballot mapping not independently verified.'
    out['current_ballot_mapping_verified']=False
    # Optional selected remaining pool: all other forecasts held exactly as supplied.
    sel=case.get('selected_unit')
    if sel is not None:
        ps=[p for p in pools if p.get('unit')==sel]
        if len(ps)!=1:out['selected']={'status':'unknown_or_ambiguous_unit'}
        else:
            p=ps[0];u=p['votes']*(p.get('pair_participation')or 0);q=clip(p.get('A_pair_share')or 0)
            out['selected']=selected_only(u,lead-u*(2*q-1),pair,target)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('--output',type=Path);a=ap.parse_args()
    try:
        obj=json.loads(a.input.read_text())
        # Invalid nonfinite inputs are never echoed into standards-compliant result JSON.
        out=[{'id':x.get('id')if isinstance(x,dict)else None,'result':live(x)}for x in obj]if isinstance(obj,list)else live(obj)
    except (OSError,ValueError)as e:out={'status':'invalid_json_input','error':str(e)}
    try:b=json.dumps(out,indent=2,allow_nan=False)+'\n'
    except (TypeError,ValueError):b=json.dumps({'status':'invalid_numeric_result','expected':'All derived numeric outputs must remain finite and JSON serializable'},indent=2)+'\n'
    if a.output:a.output.write_text(b)
    else:print(b)
if __name__=='__main__':main()

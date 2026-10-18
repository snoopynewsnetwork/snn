"""Conditional live-remainder arithmetic, no network and no probability model.
Input: counted A/B/other cumulative votes fixed; remaining contest pools and
other shares supplied by caller. q refers to remaining A+B share, not all votes.
"""
import argparse, json, math
from pathlib import Path
H=Path(__file__).resolve().parent
def clip(x): return max(0.,min(1.,x))
def finite(x): return isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x)
def classification(q):
    return 'secured_under_stated_other_assumptions' if q<0 else ('impossible_under_stated_other_assumptions' if q>1 else 'feasible_boundary_requires_strict_exceedance_for_win')
def calculate(inp):
    counted=inp.get('counted',{}); others=counted.get('other',{}); A=counted.get('A'); B=counted.get('B')
    if not isinstance(others,dict) or not all(finite(x) and x>=0 for x in [A,B]+list(others.values())): return dict(status='invalid_counted_votes')
    rawgoal=inp.get('goal_pair_margin_pp',0)
    if not finite(rawgoal): return dict(status='invalid_goal')
    goal=rawgoal/100
    units=inp.get('remaining_units',[]); ids=[u.get('key') for u in units]
    if len(ids)!=len(set(ids)): return dict(status='duplicate_remaining_keys')
    if any(u.get('remaining_contest_votes') is None for u in units): return dict(status='unknown_remaining_pool',counted_fixed=counted,projection=None)
    parsed=[]; finalOther=dict(others); notes=[]
    for u in units:
        U=u['remaining_contest_votes']; os=u.get('other_shares',{}); q=u.get('A_pair_share')
        if not finite(U) or U<0: return dict(status='invalid_negative_or_nonfinite_pool',unit=u['key'])
        if not isinstance(os,dict) or any(not finite(x) or x<0 or x>1 for x in os.values()) or sum(os.values())>1: return dict(status='invalid_other_shares',unit=u['key'])
        P=U*(1-sum(os.values()))
        if P>0 and q is None: return dict(status='unknown_remaining_preference',unit=u['key'],counted_fixed=counted,projection=None)
        if q is not None and not finite(q): return dict(status='invalid_preference',unit=u['key'])
        q=0. if q is None else q; qc=clip(q)
        if q!=qc:
            if not inp.get('clip_shares',False): return dict(status='invalid_out_of_bounds_preference',unit=u['key'])
            notes.append(dict(unit=u['key'],input_share=q,clipped_share=qc))
        for name,share in os.items(): finalOther[name]=finalOther.get(name,0)+U*share
        parsed.append(dict(key=u['key'],remaining_contest_votes=U,remaining_pair_votes=P,A_pair_share_input=q,A_pair_share_used=qc,A_remaining=P*qc,B_remaining=P*(1-qc),other_remaining={k:U*v for k,v in os.items()}))
    U=sum(u['remaining_contest_votes'] for u in parsed); P=sum(u['remaining_pair_votes'] for u in parsed)
    finalA=A+sum(u['A_remaining'] for u in parsed); finalB=B+sum(u['B_remaining'] for u in parsed)
    finalpair=A+B+P; finaltotal=A+B+sum(others.values())+U
    allvals={'A':finalA,'B':finalB,**{'other:'+k:v for k,v in finalOther.items()}}
    high=max(allvals.values()); winners=[k for k,v in allvals.items() if abs(v-high)<1e-8]
    result=dict(status='calculated',counted_fixed=dict(A=A,B=B,other=others),remaining_contest_votes=U,remaining_pair_votes=P,final_A=finalA,final_B=finalB,final_other=finalOther,final_pair_denominator=finalpair,final_all_candidate_denominator=finaltotal,final_pair_margin_pp=100*(finalA-finalB)/finalpair if finalpair else None,final_all_candidate_margin_pp=100*(finalA-finalB)/finaltotal if finaltotal else None,goal_pair_margin_pp=goal*100,goal_pair_cushion_net_votes=goal*finalpair,pair_goal_met=finalA-finalB>=goal*finalpair,plurality_leaders=winners,A_clear_plurality=winners==['A'],share_clipping=notes,units=parsed,probability=None)
    assert abs(sum(allvals.values())-finaltotal)<1e-7
    if P>0:
        pairq=(P-(A-B)+goal*finalpair)/(2*P)
        legalq=max((P-(A-B))/(2*P),(max(finalOther.values(),default=0)-A)/P)
        result['all_remaining_pair_requirement']=dict(required_A_share_unbounded=pairq,required_A_share_clipped=clip(pairq),status=classification(pairq),plurality_tie_boundary_A_share_unbounded=legalq,plurality_status=classification(legalq),strict_win='A must strictly exceed every other final candidate; pair cushion is an optional separate goal')
    else:
        result['all_remaining_pair_requirement']=dict(required_A_share_unbounded=None,required_A_share_clipped=None,status='no_positive_pair_pool',fixed_result='A_clear_plurality' if winners==['A'] else ('tie' if 'A' in winners else 'A_not_plurality'))
    selected=inp.get('selected_unit')
    if selected:
        if selected not in ids: result['selected_requirement']=dict(status='unknown_selected_key')
        else:
            s=next(x for x in parsed if x['key']==selected); Ps=s['remaining_pair_votes']
            fixedA=finalA-s['A_remaining']; fixedB=finalB-s['B_remaining']
            if Ps<=0: result['selected_requirement']=dict(status='no_positive_pair_pool',required_A_share_unbounded=None)
            else:
                q=(Ps-(fixedA-fixedB)+goal*finalpair)/(2*Ps)
                legal=max((Ps-(fixedA-fixedB))/(2*Ps),(max(finalOther.values(),default=0)-fixedA)/Ps)
                result['selected_requirement']=dict(key=selected,other_units_fixed_to_supplied_shares=True,fixed_A_excluding_selected_remainder=fixedA,fixed_B_excluding_selected_remainder=fixedB,required_A_share_unbounded=q,required_A_share_clipped=clip(q),status=classification(q),plurality_tie_boundary_A_share_unbounded=legal,plurality_status=classification(legal))
    return result
def examples():
    def case(name,A,B,O,U,q=.5,os=None,**kw):
        return dict(name=name,input=dict(counted=dict(A=A,B=B,other=O),remaining_units=[dict(key='selected',remaining_contest_votes=U,A_pair_share=q,other_shares=os or {})],selected_unit='selected',**kw))
    cases=[
      case('unknown_pool',40,50,{'C':10},None),case('unknown_preference',40,50,{},20,None),
      case('no_pool_A_wins',60,50,{'C':1},0),case('no_pool_tie',50,50,{},0),case('no_pool_A_loses',40,50,{},0),
      case('negative_pool',40,50,{},-1),case('impossible',0,100,{},10,.9),case('secured',100,0,{},10,.1),
      case('share_clipped_high',40,50,{'C':10},20,1.2,{'C':.1},clip_shares=True),case('share_clipped_low',40,50,{},20,-.2,clip_shares=True),
      case('unapproved_clipping_rejected',40,50,{},20,1.2),case('pair_goal_is_not_plurality',10,9,{'C':100},10,.6,goal_pair_margin_pp=1),
      case('other_only_pool',20,10,{'C':5},10,None,{'C':1}),case('final_denominator_with_others',40,50,{'C':10},20,.75,{'C':.1},goal_pair_margin_pp=1),
      dict(name='selected_only_others_fixed',input=dict(counted=dict(A=40,B=50,other={'C':10}),remaining_units=[dict(key='selected',remaining_contest_votes=20,A_pair_share=.7,other_shares={'C':.1}),dict(key='other_unit',remaining_contest_votes=30,A_pair_share=.4,other_shares={})],selected_unit='selected'))]
    return [dict(**c,output=calculate(c['input'])) for c in cases]
def main():
    p=argparse.ArgumentParser(); p.add_argument('input',nargs='?'); p.add_argument('--examples',action='store_true'); a=p.parse_args()
    if a.examples:
        (H/'synthetic-live-scenarios.json').write_text(json.dumps(examples(),indent=2,allow_nan=False)+'\n'); print('15 synthetic arithmetic scenarios saved')
    elif a.input: print(json.dumps(calculate(json.loads(Path(a.input).read_text())),indent=2,allow_nan=False))
    else: p.print_help()
if __name__=='__main__': main()

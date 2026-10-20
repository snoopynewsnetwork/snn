#!/usr/bin/env python3
"""Offline deterministic pair arithmetic with typed, finite input boundaries."""
import argparse,functools,json,math
from pathlib import Path
clip=lambda q:max(0.,min(1.,q))

class InputError(ValueError):
    def __init__(self,field,reason,status='invalid_input'):
        self.field,self.reason,self.status=field,reason,status
        super().__init__(reason)

def invalid(field,reason,status='invalid_input'):
    # Never echo an invalid request: it may contain NaN/Infinity or malformed containers.
    return {'status':status,'error':{'field':field,'reason':reason},'final':None}

def number(v,field,unknown=False,low=None,high=None,status='invalid_input'):
    if v is None and unknown:return
    if type(v) not in (int,float):raise InputError(field,'finite_number_required; booleans and null are not numbers')
    try:finite=math.isfinite(v)
    except OverflowError:finite=False
    if not finite:raise InputError(field,'finite_representable_number_required')
    if (low is not None and v<low)or(high is not None and v>high):raise InputError(field,'number_out_of_declared_range',status)

def json_safe(v,field='input'):
    """Check the entire request, including optional metadata, before returning it."""
    if v is None or type(v)in(str,bool):return
    if type(v)in(int,float):number(v,field);return
    if isinstance(v,dict):
        for k,n in v.items():
            if not isinstance(k,str):raise InputError(field,'string_object_keys_required')
            json_safe(n,field+'.'+k)
        return
    if isinstance(v,list):
        for i,n in enumerate(v):json_safe(n,field+'['+str(i)+']')
        return
    raise InputError(field,'JSON_value_required')

def derived(v,field):
    try:number(v,field)
    except InputError:raise InputError(field,'derived_value_not_finite_or_representable','invalid_arithmetic')
    return v

def guarded(fn):
    @functools.wraps(fn)
    def call(*args,**kwargs):
        try:
            out=fn(*args,**kwargs)
            try:json_safe(out,'result')
            except InputError:raise InputError('result','derived_output_not_finite_or_JSON_safe','invalid_arithmetic')
            return out
        except InputError as e:return invalid(e.field,e.reason,e.status)
        except (OverflowError,ZeroDivisionError):return invalid('arithmetic','overflow_or_unrepresentable_denominator','invalid_arithmetic')
        except RecursionError:return invalid('input','input_nesting_exceeds_supported_depth')
    return call

@guarded
def selected(pool,other_net,target_net):
    number(target_net,'target_net')
    number(pool,'pool',unknown=True,low=0,status='invalid_negative_pool')
    number(other_net,'other_net',unknown=True)
    if pool is None or other_net is None:return {'required_share_unbounded':None,'feasible_share':None,'status':'unknown'}
    if pool==0:return {'required_share_unbounded':None,'feasible_share':None,'status':'no_positive_pool','net_minus_target':derived(other_net-target_net,'net_minus_target')}
    q=derived((pool+target_net-other_net)/(2*pool),'required_share_unbounded')
    return {'required_share_unbounded':q,'feasible_share':clip(q)if q<=1 else None,'status':'already_secured'if q<0 else ('impossible'if q>1 else 'feasible')}

@guarded
def uniform(units,margin=0.):
    number(margin,'margin')
    if not isinstance(units,list):raise InputError('units','list_of_unit_objects_required')
    missing=False;seen={k:set()for k in ['key','id','county']}
    for i,u in enumerate(units):
        field='units['+str(i)+']'
        if not isinstance(u,dict):raise InputError(field,'unit_object_required')
        json_safe(u,field)
        if 'volume'not in u or 'share'not in u:raise InputError(field,'explicit_volume_and_share_fields_required')
        number(u['volume'],field+'.volume',unknown=True,low=0)
        number(u['share'],field+'.share',unknown=True,low=0,high=1)
        missing=missing or u['volume']is None or u['share']is None
        for key in seen:
            if key not in u:continue
            ident=u[key]
            if not isinstance(ident,str)or not ident.strip():raise InputError(field+'.'+key,'nonempty_string_unit_identity_required')
            if ident in seen[key]:raise InputError(field+'.'+key,'duplicate_unit_identity')
            seen[key].add(ident)
    # Finite out-of-feasible-range internal targets retain the historical impossible stress case.
    # The external CLI rejects target margins outside [-100,100] percentage points.
    if missing:return {'status':'unknown','shift':None}
    T=derived(sum(u['volume']for u in units),'volume')
    if T<=0:return {'status':'no_positive_pool','shift':None}
    M=derived(sum(u['volume']*(2*u['share']-1)for u in units),'baseline_net');unbounded=derived((margin-M/T)/2,'unbounded_shift')
    if abs(margin)>1:return {'status':'impossible','shift':None,'unbounded_shift':unbounded}
    target=derived(margin*T,'target_net');lo,hi=-1.,1.
    for _ in range(100):
        mid=(lo+hi)/2;net=derived(sum(u['volume']*(2*clip(u['share']+mid)-1)for u in units),'bounded_net')
        if net<target:lo=mid
        else:hi=mid
    d=(lo+hi)/2
    return {'status':'feasible','volume':T,'baseline_net':M,'baseline_margin_pp':100*M/T,'baseline_already_A_winning':M>0,
            'unbounded_shift':unbounded,'unbounded_shift_pp':100*unbounded,'shift':d,'shift_pp':100*d,
            'target_margin_pp':100*margin,'target_net':target,'net_gain':target-M,
            'clipped_units':sum(not 0<=u['share']+unbounded<=1 for u in units),'solved_net':sum(u['volume']*(2*clip(u['share']+d)-1)for u in units)}

def votes_map(obj,field,mix=False):
    if not isinstance(obj,dict):raise InputError(field,'named_candidate_object_required')
    for key,value in obj.items():
        if not isinstance(key,str)or not key.strip()or key in ('A','B'):raise InputError(field,'nonempty_other_candidate_keys_distinct_from_A_and_B_required')
        number(value,field+'.'+key,low=0,high=1 if mix else None,status='invalid_negative_or_bounds')
    if mix and obj:
        total=derived(sum(obj.values()),field+'.sum')
        if abs(total-1)>1e-10:raise InputError(field,'nonempty_mix_must_sum_to_one','invalid_mix')

@guarded
def live(x):
    """Counted A/B/named other fixed; remaining is ALL-CANDIDATE valid votes."""
    if not isinstance(x,dict):raise InputError('input','request_object_required')
    json_safe(x)
    A=x.get('counted_A');B=x.get('counted_B');O=x.get('counted_other',{});R=x.get('remaining');p=x.get('pair_participation');q=x.get('remaining_A_pair_share');g=x.get('target_pair_margin',0);mix=x.get('remaining_other_mix',{})
    number(A,'counted_A',low=0,status='invalid_negative_or_bounds');number(B,'counted_B',low=0,status='invalid_negative_or_bounds')
    number(R,'remaining',unknown=True,low=0,status='invalid_negative_or_bounds')
    number(p,'pair_participation',unknown=True,low=0,high=1,status='invalid_negative_or_bounds')
    number(q,'remaining_A_pair_share',unknown=True) # Documented finite preference clipping is intentional.
    number(g,'target_pair_margin',low=-1,high=1,status='invalid_negative_or_bounds')
    votes_map(O,'counted_other');votes_map(mix,'remaining_other_mix',mix=True)
    # Every supplied field has now been validated, including when another field is unknown.
    if R is None:return {'status':'unknown','input':x,'final':None}
    if p is None:
        if R==0:p=1
        else:return {'status':'unknown','input':x,'final':None}
    U=derived(R*p,'remaining_pair_pool')
    if R>0 and p>0 and U==0:raise InputError('remaining_pair_pool','positive_pool_underflows_representation','invalid_arithmetic')
    if q is None:
        if U==0:q=.5
        else:return {'status':'unknown','input':x,'final':None}
    others=derived(R-U,'remaining_other_pool')
    if others>0 and not mix:return {'status':'unknown_other_mix','input':x,'final':None}
    qq=clip(q);final_other={k:derived(O.get(k,0)+others*mix.get(k,0),'final_other.'+k)for k in sorted(set(O)|set(mix))}
    FA=derived(A+U*qq,'final_A');FB=derived(B+U*(1-qq),'final_B');FP=derived(A+B+U,'final_pair_denominator');F=derived(FP+sum(final_other.values()),'final_all_candidate_denominator');target=derived(g*FP,'target_net')
    if min(FA,FB,FP,F,*final_other.values())<0:raise InputError('final','negative_derived_votes','invalid_arithmetic')
    req=selected(U,A-B,target)
    if req['status'].startswith('invalid'):return req
    legal_req=None if U==0 else derived(max((U+B-A)/(2*U),max(((v-A)/U for v in final_other.values()),default=-math.inf)),'legal_plurality_boundary')
    full={'A':FA,'B':FB,**final_other};high=max(full.values());winners=[k for k,v in full.items()if v==high]
    return {'status':'calculated','input':x,'clipped_preference':q!=qq,'used_remaining_A_pair_share':qq if U else None,'remaining_pair_pool':U,
            'fixed_counted_votes':{'A':A,'B':B,'other':O},'final':{'A':FA,'B':FB,'other':final_other,'pair_denominator':FP,'all_candidate_denominator':F,'pair_net':FA-FB,'pair_margin_pp':None if FP==0 else 100*(FA-FB)/FP,'all_candidate_margin_pp':None if F==0 else 100*(FA-FB)/F,'plurality_leaders':winners,'A_outright_plurality':len(winners)==1 and winners[0]=='A'},
            'pair_target':req,'legal_plurality_tie_boundary_remaining_A_pair_share_unbounded':legal_req,
            'interpretation':'Strictly exceed all opponents for an outright plurality; equality is a tie. Pair cushion is illustrative.'}

class Parser(argparse.ArgumentParser):
    def error(self,message):raise InputError('argv','unrecognized_or_incomplete_arguments')

def cli_number(value,field,low=None,high=None):
    try:value=float(value)
    except (TypeError,ValueError,OverflowError):raise InputError(field,'numeric_command_argument_required')
    number(value,field,low=low,high=high)
    return value

def object_pairs(pairs):
    out={}
    for key,value in pairs:
        if key in out:raise InputError('JSON_object','duplicate_object_key')
        out[key]=value
    return out

@guarded
def command(argv=None):
    ap=Parser();ap.add_argument('--live-json');ap.add_argument('--county');ap.add_argument('--others-shift-pp',default=0);ap.add_argument('--target-margin-pp',default=0);a=ap.parse_args(argv)
    shift=cli_number(a.others_shift_pp,'others_shift_pp',-100,100);margin=cli_number(a.target_margin_pp,'target_margin_pp',-100,100)
    if a.live_json:
        try:x=json.loads(Path(a.live_json).read_text(),object_pairs_hook=object_pairs)
        except (OSError,UnicodeError):raise InputError('live_json','readable_UTF8_input_file_required')
        except (json.JSONDecodeError,RecursionError):raise InputError('live_json','valid_JSON_request_required')
        return live(x)
    import csv
    rows=list(csv.DictReader((Path(__file__).parent.parent/'county-baselines.csv').open()));rs=[r for r in rows if r['contest']=='2024-senate'];names=[r['county']for r in rs]
    if len(names)!=len(set(names)):raise InputError('county_baselines','duplicate_source_county')
    if a.county is not None and a.county not in names:raise InputError('county','unknown_source_county')
    units=[{'county':r['county'],'volume':float(r['pair_votes']),'share':float(r['A_pair_share'])}for r in rs]
    # Validate the actual named unit collection before summing or applying shifts.
    verified=uniform(units,margin/100)
    if verified['status'].startswith('invalid'):return verified
    if a.county is None:return verified
    T=derived(sum(u['volume']for u in units),'pair_total');u=next(u for u in units if u['county']==a.county)
    others=derived(sum(t['volume']*(2*clip(t['share']+shift/100)-1)for t in units if t!=u),'other_net')
    out=selected(u['volume'],others,margin/100*T)
    if out['status'].startswith('invalid'):return out
    out.update({'county':a.county,'others_shift_pp':shift,'pair_total':T,'target_margin_pp':margin})
    return out

def main():
    out=command()
    # Guarded interfaces have already rejected nonfinite/overflowed results.
    print(json.dumps(out,indent=2,allow_nan=False))
if __name__=='__main__':main()

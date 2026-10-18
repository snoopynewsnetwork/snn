"""Conditional arithmetic only: counted votes fixed, forecast stated remainder.

python3 live.py INPUT.json [--selected UNIT_ID] [--target-pair-margin-pp 1]
python3 live.py --historical --contest 2024-pres --unit SC:45045
"""
from calculate import *
def status(q):return 'already_secured' if q<0 else ('impossible' if q>1 else 'feasible_threshold')
def live(x,selected=None,target_pair_margin_pp=0,target_all_margin_pp=None):
    counted=x['counted'];units=x['remaining'];A=counted['A'];B=counted['B'];others=dict(counted.get('others',{}))
    if any(v is not None and (not math.isfinite(v) or v<0) for v in [A,B,*others.values()]):return dict(status='negative_or_nonfinite_counted_invalid')
    if A is None or B is None or any(v is None for v in others.values()):return dict(status='unknown_counted')
    if len({u['id'] for u in units})!=len(units):return dict(status='duplicate_remaining_unit_invalid')
    for u in units:
        if any(v is not None and (not math.isfinite(v) or v<0) for v in [u.get('pair_pool'),*u.get('others',{}).values()]):return dict(status='negative_or_nonfinite_remaining_invalid',unit=u['id'])
    if any(u.get('pair_pool') is None or any(v is None for v in u.get('others',{}).values()) for u in units):return dict(status='unknown_remaining_pool',counted_fixed=counted)
    U=sum(u['pair_pool'] for u in units);finalpair=A+B+U;L=A-B;futureothers={}
    for u in units:
        for k,v in u.get('others',{}).items():futureothers[k]=futureothers.get(k,0)+v
    finalothers={k:others.get(k,0)+futureothers.get(k,0) for k in others.keys()|futureothers.keys()}
    N=finalpair+sum(finalothers.values());target=target_pair_margin_pp/100*finalpair if target_all_margin_pp is None else target_all_margin_pp/100*N
    out=dict(status='conditional',scenario=x.get('name'),scope=x.get('scope'),counted_fixed=counted,counted_pair=A+B,counted_net=L,remaining_pair=U,
             final_pair_denominator=finalpair,final_all_candidate_denominator=N,final_others=finalothers,target_pair_margin_pp=target_pair_margin_pp if target_all_margin_pp is None else None,target_all_margin_pp=target_all_margin_pp,target_net=target,
             probability=None,probability_status='not calibrated; deterministic arithmetic')
    if U==0:
        out.update(status='no_positive_pool',pair_target_status='secured' if L>target else ('at_threshold' if L==target else 'impossible'),
                   strict_plurality_status='secured' if A>max([B,*finalothers.values()]) else ('tied' if A==max([B,*finalothers.values()]) else 'impossible'),projected_A=A,projected_B=B)
        return out
    req=(U+target-L)/(2*U);rival=max(finalothers.values(),default=0)
    plurality_q=max((B+U-A)/(2*U),(rival-A)/U)
    out.update(required_uniform_remaining_A_share=req,required_status=status(req),strict_plurality_remaining_A_share_boundary=plurality_q,
               strict_plurality_status=('impossible_strict_at_or_above_one' if plurality_q>=1 else status(plurality_q)),strict_plurality_condition='A must exceed boundary and every named opponent; equality is not a win')
    projectedA=A;projectedB=B;detail=[];known=True
    for u in units:
        w=u['pair_pool'];s=u.get('A_share');s=0 if w==0 and s is None else s
        if s is None and w>0:known=False;detail.append(dict(id=u['id'],status='unknown_preference',pair_pool=w));continue
        if not math.isfinite(s):return dict(status='nonfinite_preference_invalid',unit=u['id'])
        q=clip(s);projectedA+=w*q;projectedB+=w*(1-q);detail.append(dict(id=u['id'],pair_pool=w,input_share=s,used_share=q,clipped=q!=s,remaining_A=w*q,remaining_B=w*(1-q)))
    out['remaining_details']=detail
    if known:
        out.update(projected_A=projectedA,projected_B=projectedB,projected_net=projectedA-projectedB,
                   projected_pair_margin_pp=100*(projectedA-projectedB)/finalpair if finalpair else None,
                   projected_all_margin_pp=100*(projectedA-projectedB)/N if N else None,
                   strict_plurality_cushion=projectedA-max([projectedB,*finalothers.values()]),
                   all_candidate_vote_sum=projectedA+projectedB+sum(finalothers.values()))
    else:out['status']='known_pool_unknown_preference'
    if selected is not None:
        sel=next((u for u in units if u['id']==selected),None)
        if sel is None:out['selected']={'status':'unknown_selected_unit'}
        elif sel['pair_pool']==0:out['selected']={'status':'no_positive_pool'}
        elif any(u['id']!=selected and u['pair_pool']>0 and u.get('A_share') is None for u in units):out['selected']={'status':'unknown_other_preference'}
        else:
            fixed_other=L+sum(u['pair_pool']*(2*clip(u.get('A_share',0) or 0)-1) for u in units if u['id']!=selected)
            w=sel['pair_pool'];q=(w+target-fixed_other)/(2*w)
            out['selected']=dict(id=selected,pair_pool=w,other_units_fixed_net=fixed_other,required_A_share=q,status=status(q),assumption='all other remaining unit shares fixed at individually listed clipped inputs; counted votes unchanged')
    return out

def fixtures():
    nr=[r for r in readnative() if r['contest_label']=='2024-pres' and r['native_type']=='County']
    # Synthetic 50% counted and 50% historical pair remainder; no reporting-order inference.
    ca=sum(r['A']//2 for r in nr);cb=sum(r['B']//2 for r in nr)
    base=dict(name='all46_historical_synthetic',scope='46 historical counties, arithmetic illustration; remaining pools/preferences not observed2026',counted=dict(A=ca,B=cb,others={'synthetic minor candidate':1000}),remaining=[dict(id=r['geography_key'],pair_pool=r['A']+r['B']-r['A']//2-r['B']//2,A_share=r['A_pair_share'],others={}) for r in nr])
    def case(name,A,B,pool,share=None,other=None):return dict(name=name,scope='synthetic arithmetic test',counted=dict(A=A,B=B,others=other or {}),remaining=[dict(id='synthetic',pair_pool=pool,A_share=share,others={})])
    xs=[base,case('unknown_pool',10,20,None,.6),case('known_pool_unknown_preference',10,20,100),case('no_pool_tie',10,10,0),case('no_pool_secured',21,10,0),
        case('no_pool_impossible',5,10,0),case('negative_remaining',10,20,-1,.5),case('negative_counted',-1,20,10,.5),case('positive_pool_impossible',0,100,20,.8),
        case('positive_pool_secured',100,0,20,.1),case('clip_high',10,20,30,1.3),case('clip_low',10,20,30,-.2),case('other_candidate_blocks_pair_win',20,10,20,.9,{'Named independent':100})]
    dump(BASE/'live-scenarios.json',xs)
    dump(BASE/'live-results.json',[dict(input=x,result=live(x,x['remaining'][0]['id']),Aplus1_result=live(x,x['remaining'][0]['id'],1)) for x in xs])
    print(compact(dict(synthetic_scenarios=len(xs))))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input',nargs='?');ap.add_argument('--fixtures',action='store_true');ap.add_argument('--selected');ap.add_argument('--target-pair-margin-pp',type=float,default=0);ap.add_argument('--target-all-margin-pp',type=float)
    ap.add_argument('--historical',action='store_true');ap.add_argument('--contest',default='2024-pres',choices=LABELS);ap.add_argument('--unit');ap.add_argument('--others-shift-pp',type=float,default=0);args=ap.parse_args()
    if args.fixtures:fixtures()
    elif args.historical:
        ns=readnative();typ='Precinct' if args.unit and ':db:' in args.unit else 'County';rs=[r for r in ns if r['contest_label']==args.contest and r['native_type']==typ]
        sel=next(r for r in rs if r['geography_key']==args.unit);T=sum(r['pair_votes'] for r in rs);net=sum(r['pair_votes']*(2*clip((r['A_pair_share'] or 0)+(0 if r is sel else args.others_shift_pp/100))-1) for r in rs)
        own=sel['A']-sel['B'];print(json.dumps(dict(contest=args.contest,selected=args.unit,all_units=len(rs),total_pair=T,others_shift_pp=args.others_shift_pp,**conditional(sel['pair_votes'],own,net,T,args.target_pair_margin_pp/100)),indent=2))
    else:
        x=json.loads(Path(args.input).read_text());out=[live(y,args.selected,args.target_pair_margin_pp,args.target_all_margin_pp) for y in x] if isinstance(x,list) else live(x,args.selected,args.target_pair_margin_pp,args.target_all_margin_pp);print(json.dumps(out,indent=2))

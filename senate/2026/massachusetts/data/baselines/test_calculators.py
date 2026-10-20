#!/usr/bin/env python3
"""Synthetic arithmetic/edge/rejection cases; never calibrated probabilities."""
import copy,json,math
from calculate import historical,live,strict_json
from extract_originals import ROOT,dump
def main():
    directory=ROOT/'synthetic';directory.mkdir(exist_ok=True);saved=[];checks=[]
    def save(name,mode,x,expect):
        try:
            y=live(x) if mode=='live' else historical(**x)
            expect(y);output=y
        except ValueError as e:
            if expect!='invalid':raise
            output=dict(status='invalid_input',error=str(e))
        else:
            assert expect!='invalid',name
        # All synthetic on-disk inputs remain strict JSON: nonfinite API tests separate below.
        dump(directory/(name+'.input.json'),x);dump(directory/(name+'.output.json'),output);saved.append(dict(name=name,mode=mode,status=output['status']))
    base=dict(candidates=['A','B','C','D'],A='A',B='B',target_margin=0,units=[dict(key='synthetic-unit',counted={'A':40,'B':50,'C':5,'D':0},remaining_pool=dict(status='known',votes=100),allocation={'A':.5,'B':.4,'C':.1,'D':0})])
    save('known-final-denominator','live',base,lambda y:(checks.append('final195_counted95_plus_only_remaining100'),assertion(y['final_denominator']==195 and y['counted']['A']==40 and math.isclose(y['pair_requirement']['raw_share'],100/180))))
    x=copy.deepcopy(base);x['units'][0]['remaining_pool']={'status':'unknown'};save('unknown','live',x,lambda y:assertion(y['final'] is None and y['final_denominator'] is None))
    x=copy.deepcopy(base);x['units'][0]['remaining_pool']['votes']=0;save('no-pool','live',x,lambda y:assertion(y['pair_requirement']['status']=='no_positive_pool' and y['final_denominator']==95))
    x=copy.deepcopy(base);x['units'][0]['remaining_pool']['votes']=-1;save('negative-pool-rejected','live',x,'invalid')
    for name,A,B,status in [('secured',200,0,'already_secured'),('impossible',0,200,'impossible')]:
        x=copy.deepcopy(base);x['units'][0]['counted']['A']=A;x['units'][0]['counted']['B']=B
        save(name,'live',x,lambda y,s=status:assertion(y['pair_requirement']['status']==s))
    x=copy.deepcopy(base);x['target_margin']=.01;x['units'][0].update(counted={'A':50,'B':50,'C':200,'D':0},remaining_pool=dict(status='known',votes=100),allocation={'A':.51,'B':.49,'C':0,'D':0})
    save('Aplus1-pair-loses-fullfield','live',x,lambda y:assertion(math.isclose(y['A_minus_B_final_pair_margin'],.01) and y['leaders']==['C'] and y['final_denominator']==400))
    x=copy.deepcopy(base);x['selected_key']='synthetic-unit';x['units'].append(dict(key='fixed-elsewhere',counted={'A':10,'B':5,'C':1,'D':2},remaining_pool=dict(status='known',votes=200),allocation={'A':.2,'B':.3,'C':.4,'D':.1}))
    save('selected-only-fixed-elsewhere','live',x,lambda y:assertion(y['variable_pair_pool']==90 and y['remaining_pair_pool']==190 and y['counted']['C']==6 and y['final']['C']==96))
    hist=dict(units=[dict(key='left',T=10,share=.05),dict(key='right',T=90,share=.95)],target_margin=-.9)
    save('clipping-bounded-solve','historical',hist,lambda y:assertion(y['clipped_units']==1 and abs(y['achieved_net_votes']+90)<1e-8 and not math.isclose(y['unbounded_share_shift'],y['bounded_share_shift'])))
    save('historical-no-positive-pool','historical',dict(units=[dict(key='zero',T=0,share=.5)],target_margin=0),lambda y:assertion(y['status']=='no_positive_pool'))
    save('already-winning-negative-shift','historical',dict(units=[dict(key='win',T=100,share=.6)],target_margin=0),lambda y:assertion(math.isclose(y['unbounded_share_shift'],-.1) and y['positive_improvement_needed_pp']==0))
    for target in [None,True,'0',-1.01,1.01,float('nan'),float('inf')]:
        for fn,x in [(lambda z:historical([dict(key='u',T=1,share=.5)],z),target),(lambda z:live(dict(base,target_margin=z)),target)]:reject(lambda:fn(x));checks.append('reject_invalid_target_'+repr(target))
    for value in [None,True,'1',-1,float('nan'),float('inf')]:
        reject(lambda:historical([dict(key='u',T=value,share=.5)]));checks.append('reject_invalid_weight_'+repr(value))
        x=copy.deepcopy(base);x['units'][0]['counted']['A']=value;reject(lambda:live(x));checks.append('reject_invalid_counted_'+repr(value))
        x=copy.deepcopy(base);x['units'][0]['remaining_pool']['votes']=value;reject(lambda:live(x));checks.append('reject_invalid_remaining_'+repr(value))
    for value in [None,True,'1',-1,1.01,float('nan'),float('inf')]:
        reject(lambda:historical([dict(key='u',T=1,share=value)]));checks.append('reject_invalid_preference_'+repr(value))
    for ks in [[],[None],[''],[' '],[1],[True],['same','same']]:
        reject(lambda:historical([dict(key=k,T=0,share=.5)for k in ks]));checks.append('global_keys_before_zero_pool_'+repr(ks))
        x=copy.deepcopy(base);x['units']=[dict(x['units'][0],key=k) for k in ks];reject(lambda:live(x));checks.append('live_global_keys_before_arithmetic_'+repr(ks))
    x=copy.deepcopy(base);x['units'][0].pop('key');reject(lambda:live(x));checks.append('missing_global_key')
    x=copy.deepcopy(base);x['units'][0]['counted'].pop('D');reject(lambda:live(x));checks.append('missing_candidate_rejected')
    x=copy.deepcopy(base);x['candidates']=['A','B','C','C'];reject(lambda:live(x));checks.append('duplicate_candidate_rejected')
    x=copy.deepcopy(base);x['units'][0]['allocation']['D']=True;reject(lambda:live(x));checks.append('boolean_allocation_rejected')
    x=copy.deepcopy(base);x['units'][0]['allocation']['A']=.6;reject(lambda:live(x));checks.append('bad_allocation_sum_rejected')
    for s in ['{"x":NaN}','{"x":Infinity}','{"x":1,"x":2}']:reject(lambda:strict_json(s));checks.append('strict_json_'+s)
    reject(lambda:historical([dict(key='a',T=1e308,share=1),dict(key='b',T=1e308,share=1)]));checks.append('finite_input_overflow_safe_error')
    # Exact algebra with FINAL pair denominator: insert required share into variable pool.
    y=live(base);q=y['pair_requirement']['raw_share'];assert math.isclose((40+90*q)-(50+90*(1-q)),0,abs_tol=1e-10)
    checks.append('live_required_share_substitution_ties')
    y=historical([dict(key='a',T=60,share=.7),dict(key='b',T=40,share=.4)],.01)
    z=y['units'][0];q=z['selected_unit_only']['raw_share'];assert math.isclose(60*(2*q-1)+40*(2*.4-1),1,abs_tol=1e-10)
    checks.append('historical_selected_share_substitution_with_every_other_fixed')
    dump(directory/'validation.json',dict(status='pass',synthetic_saved_cases=saved,checks=checks,probability_calibration=False))
    print(len(saved),'saved scenarios;',len(checks),'edge/arithmetic/input checks')
def assertion(test):assert test
def reject(fn):
    try:fn()
    except ValueError:return
    raise AssertionError('invalid input accepted')
if __name__=='__main__':main()

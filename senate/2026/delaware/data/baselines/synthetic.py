#!/usr/bin/env python3
from pathlib import Path
import json
from calculators import live,uniform,selected
P=Path(__file__).resolve().parent

def main():
 def make(name,a,b,U,q=.5,others=None,remaining_other=None,g=0):return dict(name=name,counted={'A':a,'B':b,'other':others or {}},remaining=[dict(unit='selected',remaining_total=U,remaining_other=remaining_other if remaining_other is not None else {},pair_share=q)],target_pair_margin=g,selected_unit='selected')
 xs=[make('ordinary_pair_tie',40,60,100),make('final_denominator_A_plus1',40,60,100,g=.01),make('unknown_remainder',40,60,None),make('no_pool_A_ahead',60,40,0),make('no_pool_tie',50,50,0),make('negative_pool_rejected',40,60,-10),make('negative_counted_rejected',-1,50,100),make('impossible_A_to_tie',0,1000,100),make('secured_even_at_zero_A_remaining',1000,0,100),make('clip_high_preference',40,60,100,1.4),make('clip_low_preference',40,60,100,-.4),make('all_other_remainder_no_pair_pool',40,60,100,others={'Independent C':20},remaining_other={'Independent C':100}),make('third_candidate_defeats_pair_winner',40,60,100,.8,others={'Independent C':250},remaining_other={'Independent C':20}),make('other_exceeds_pool_rejected',40,60,10,remaining_other={'Libertarian C':11}),make('counted_other_final_denominator',40,60,110,.6,others={'Independent C':30,'Libertarian D':10},remaining_other={'Independent C':6,'Libertarian D':4})]
 xs.append(dict(name='selected_only_with_other_unit_fixed',counted={'A':400,'B':450,'other':{'Independent C':25}},remaining=[dict(unit='selected',remaining_total=200,remaining_other={'Independent C':20},pair_share=.55),dict(unit='other',remaining_total=100,remaining_other={'Independent C':10},pair_share=.7)],selected_unit='selected',target_pair_margin=.01))
 xs.append(dict(name='unknown_other_unit_share',counted={'A':10,'B':20,'other':{}},remaining=[dict(unit='selected',remaining_total=30,remaining_other={},pair_share=.5),dict(unit='other',remaining_total=40,remaining_other={},pair_share=None)],selected_unit='selected'))
 xs.append(make('nonnumeric_target_rejected',40,60,100,g='NaN'))
 xs.append(make('null_target_rejected',40,60,100,g=None))
 xs.append(dict(name='duplicate_nonselected_pool_rejected',counted={'A':1,'B':2,'other':{}},remaining=[dict(unit='county|method|one',remaining_total=10,remaining_other={},pair_share=.5),dict(unit='county|method|one',remaining_total=10,remaining_other={},pair_share=.5)]))
 xs.append(make('out_of_bounds_target_rejected',40,60,100,g=1.01))
 tests=[]
 results=[dict(name=x['name'],input=x,result=live(x)) for x in xs]
 rr={r['name']:r['result'] for r in results}
 def test(n,b):assert b,n;tests.append(n)
 test('out of bounds target rejected',rr['out_of_bounds_target_rejected']['status']=='invalid-target-out-of-bounds')
 test('nonnumeric target rejected',rr['nonnumeric_target_rejected']['status']=='invalid-nonfinite-or-nonnumeric-target')
 test('null target rejected',rr['null_target_rejected']['status']=='invalid-nonfinite-or-nonnumeric-target')
 test('duplicate pool rejected without selected unit',rr['duplicate_nonselected_pool_rejected']['status']=='invalid-duplicate-remaining-unit')
 nonfinite=[]
 for tag,value in [('NaN',float('nan')),('positive infinity',float('inf')),('negative infinity',-float('inf'))]:
  item=live(make(tag,40,60,100,g=value));test(tag+' target returns explicit invalid result',item['status']=='invalid-nonfinite-or-nonnumeric-target');nonfinite.append(dict(input_python_expression=repr(value),input_description=tag+' numeric target',result=item))
 (P/'synthetic-invalid-numeric-targets.json').write_text(json.dumps(nonfinite,indent=2,allow_nan=False)+'\n')
 test('final pair denominator is counted100+remaining100=200',rr['final_denominator_A_plus1']['final_pair_denominator']==200)
 test('A+1 requires61percent remainder, not60.5',abs(rr['final_denominator_A_plus1']['required_remaining_A_share_unbounded']-.61)<1e-12)
 test('other votes final denominator includes counted and remaining',rr['counted_other_final_denominator']['final_all_candidate_denominator']==250)
 test('other votes excluded from pair denominator',rr['counted_other_final_denominator']['final_pair_denominator']==200)
 test('unknown remains unknown',rr['unknown_remainder']['status']=='unknown-remainder')
 test('negative rejected',rr['negative_pool_rejected']['status'].startswith('invalid'))
 test('impossible preserved unbounded',rr['impossible_A_to_tie']['required_remaining_A_share_unbounded']==5.5)
 test('secured preserved negative threshold',rr['secured_even_at_zero_A_remaining']['required_remaining_A_share_unbounded']==-4.5)
 test('clipping high documented',rr['clip_high_preference']['share_clipping'][0]['clipped']==1)
 test('clipping low documented',rr['clip_low_preference']['share_clipping'][0]['clipped']==0)
 test('counted A remains fixed',all(r['result'].get('counted_fixed',r['input']['counted'])==r['input']['counted'] for r in results))
 test('third-party plurality separate from pair result',rr['third_candidate_defeats_pair_winner']['final_A']>rr['third_candidate_defeats_pair_winner']['final_B'] and rr['third_candidate_defeats_pair_winner']['plurality_A_secured']==False)
 test('no positive pair pool with remaining others',rr['all_other_remainder_no_pair_pool']['status']=='no-positive-pool')
 u=uniform([(1,0),(100,.9)],0);test('uniform infeasible raw shift solved with clipping',not u['raw_uniform_feasible'] and abs(sum(t*(2*max(0,min(1,s+u['bounded_shift']))-1) for t,s in [(1,0),(100,.9)]))<1e-8)
 testspec=[dict(name='bounded_uniform_clipping',input=[[1,0],[100,.9]],result=u),dict(name='unbounded_full_A_saturation_ray',result=uniform([(5,.4),(6,.8)],1)),dict(name='unbounded_full_B_saturation_ray',result=uniform([(5,.4),(6,.8)],-1)),dict(name='no_pool_uniform',result=uniform([],0)),dict(name='impossible_margin_above100percent',result=uniform([(10,.5)],1.01)),dict(name='selected_zero_pool',result=selected(100,0,30,0))]
 test('unbounded solution ray retained',testspec[1]['result']['solution_interval'][1]=='infinity')
 test('unachievable margin rejected',testspec[4]['result']['status']=='impossible')
 (P/'synthetic-inputs.json').write_text(json.dumps(xs,indent=2)+'\n');(P/'synthetic-results.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n');(P/'synthetic-bounded-cases.json').write_text(json.dumps(testspec,indent=2,allow_nan=False)+'\n');(P/'synthetic-validation.json').write_text(json.dumps(dict(status='pass',checks=tests,count=len(tests)),indent=2)+'\n');print(len(xs),'live scenarios;',len(tests),'checks')
if __name__=='__main__':main()

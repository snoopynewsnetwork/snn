"""Coordinator independent actual-CLI denominator/unknown/bounds/input regressions."""
from pathlib import Path
import copy, json, math, subprocess, sys

S=Path(__file__).resolve().parents[1]
CALC=S/'data/baselines/calculator.py'
records=[]

def invoke(name,d,invalid=False,raw=None,check=None):
    text=raw if raw is not None else json.dumps(d,allow_nan=True)
    p=subprocess.run([sys.executable,'-B',str(CALC)],input=text.encode(),capture_output=True,timeout=15)
    assert p.stderr==b'',(name,p.stderr)
    result=json.loads(p.stdout,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    assert p.returncode==(2 if invalid else 0),(name,p.returncode,result)
    assert result['status']==('invalid-input' if invalid else 'ok'),(name,result)
    if check:check(result)
    records.append(dict(name=name,input_text=text,expected_invalid=invalid,exit_code=p.returncode,stderr='',output=result))
    return result

def close(a,b,tol=1e-10):assert math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tol,(a,b)

base=dict(mode='live',pair=['A','B'],other_candidates=['C'],candidate_universe='full',unallocated_generic=False,assumptions='Coordinator synthetic counted-fixed two-pool arithmetic, no forecast',target_pair_margin=.01,selected_unit='u',units=[dict(key='u',remaining=100,pair_participation=.8,share=.4,other_allocations={'C':1},counted={'A':30,'B':20,'C':10},counted_all_candidate_total=60),dict(key='v',remaining=50,pair_participation=.8,share=.8,other_allocations={'C':1},counted={'A':5,'B':15,'C':0},counted_all_candidate_total=20)])
def check_base(o):
    assert o['counted_fixed']=={'A':35,'B':35,'C':10}
    close(o['final_pair_denominator'],190);close(o['final_all_candidate_denominator'],230)
    close(o['target_pair_net'],1.9);close(o['baseline_pair_net'],8)
    close(o['aggregate_remaining_requirement']['raw_required_share'],121.9/240)
    close(o['selected_unit_requirement']['raw_required_share'],57.9/160)
    for n,v in {'A':99,'B':91,'C':40}.items():close(o['projected_candidates'][n],v)
    close(o['uniform']['unbounded_share_shift'],-6.1/240)
    close(o['uniform']['bounded_net'],1.9,1e-8)
    assert o['plurality']['legal_declaration'] is False
invoke('counted-fixed-final-pair-and-all-denominators',base,check=check_base)

d=copy.deepcopy(base);d['units'][0]['share']=None
o=invoke('unknown-selected-only-solvable-others-known',d)
assert o['uniform']['status']=='unknown-preference' and o['projected_candidates'] is None
close(o['selected_unit_requirement']['raw_required_share'],57.9/160)
d=copy.deepcopy(base);d['units'][1]['share']=None
o=invoke('unknown-positive-other-stays-unknown',d);assert o['selected_unit_requirement']['status']=='unknown-other-preference'
d=copy.deepcopy(base);d['units'][1]['key']=' u ';d['selected_unit']=' u '
o=invoke('literal-space-key-is-distinct-not-trimmed-alias',d);assert len({u['key'] for u in o['units']})==2

hist=dict(mode='historical',pair=['A','B'],other_candidates=['C'],candidate_universe='full',unallocated_generic=False,assumptions='Synthetic endpoint-clipping proof',target_pair_margin=0,units=[dict(key='lo',volume=10,pair_participation=1,share=0,other_allocations={'C':1}),dict(key='hi',volume=90,pair_participation=1,share=.9,other_allocations={'C':1})])
o=invoke('bounded-clipped-root-differs-from-unbounded',hist)
close(o['uniform']['unbounded_share_shift'],-.31);close(o['uniform']['bounded_share_shift'],-31/90)
assert o['uniform']['endpoint_clipped_units']==['lo'];close(o['uniform']['bounded_net'],0,1e-8)
d=copy.deepcopy(hist);d['units']=[dict(key='third',volume=100,pair_participation=.2,share=.6,other_allocations={'C':1})]
o=invoke('pair-leader-loses-supplied-full-field',d);assert o['plurality']['leaders']==['C'] and o['plurality']['pair_A_leads'] is True and o['plurality']['A_leads_every_supplied_other'] is False
d=copy.deepcopy(base)
for u in d['units']:u['remaining']=0;u['share']=None
o=invoke('no-positive-pool-counted-only',d);assert o['uniform']['status']=='no-positive-pool' and o['aggregate_remaining_requirement']['fixed_target_status']=='below'
d=copy.deepcopy(base);d['units'][0]['counted']={'A':1000,'B':0,'C':0};d['units'][0]['counted_all_candidate_total']=1000
o=invoke('negative-required-share-secured-kept-raw',d);assert o['aggregate_remaining_requirement']['status']=='secured' and o['aggregate_remaining_requirement']['raw_required_share']<0
d=copy.deepcopy(base);d['units'][0]['counted']={'A':0,'B':1000,'C':0};d['units'][0]['counted_all_candidate_total']=1000
o=invoke('required-share-above-one-impossible-kept-raw',d);assert o['aggregate_remaining_requirement']['status']=='impossible' and o['aggregate_remaining_requirement']['raw_required_share']>1

# Invalid values are exercised through the real JSON/CLI parser, before every early branch.
for i,value in enumerate([None,True,False,'0',{},[],float('nan'),float('inf'),-float('inf'),-1.00001,1.00001]):
    d=copy.deepcopy(base);d['target_pair_margin']=value;invoke('invalid-target-'+str(i),d,invalid=True)
for branch in ['ordinary','unknown','no-pool']:
    for kind in ['duplicate','missing','empty','whitespace','integer','boolean']:
        d=copy.deepcopy(base);d.pop('selected_unit')
        if branch=='unknown':d['units'][0]['share']=None
        if branch=='no-pool':
            for u in d['units']:u['remaining']=0;u['share']=None
        if kind=='duplicate':d['units'][1]['key']='u'
        elif kind=='missing':d['units'][1].pop('key')
        else:d['units'][1]['key']={'empty':'','whitespace':' \t','integer':3,'boolean':False}[kind]
        invoke('global-key-'+branch+'-'+kind,d,invalid=True)
for field,value in [('remaining',-1),('remaining',True),('remaining',None),('remaining','100'),('remaining',float('inf')),('pair_participation',-.1),('pair_participation',1.1),('pair_participation',True),('share',-1),('share',1.01),('share',True),('share','0.5'),('share',float('nan')),('other_allocations',[]),('other_allocations',{'C':.5}),('other_allocations',{'C':True}),('other_allocations',{'X':1}),('counted',{'A':30,'B':20,'C':-1}),('counted',{'A':30,'B':20}),('counted_all_candidate_total',50),('counted_all_candidate_total',True)]:
    d=copy.deepcopy(base);d['units'][0][field]=value;invoke('invalid-unit-'+field+'-'+str(len(records)),d,invalid=True)
for name,mutate in [('unsupported-mode',lambda d:d.update(mode='runoff')),('candidate-collision',lambda d:d.update(other_candidates=['A'])),('duplicate-pair',lambda d:d.update(pair=['A','A'])),('missing-selection',lambda d:d.update(selected_unit='absent')),('empty-selection',lambda d:d.update(selected_unit=' ')),('aggregate-overflow',lambda d:[u.update(remaining=1e308) for u in d['units']])]:
    d=copy.deepcopy(base);mutate(d);invoke(name,d,invalid=True)
text=json.dumps(base);invoke('duplicate-root-field-rejected',None,invalid=True,raw=text[:-1]+',"mode":"historical"}')

result=dict(status='pass_actual_CLI_independent_counted_fixed_denominator_unknown_clipping_input_review',actual_CLI_cases=len(records),expected_invalid=sum(r['expected_invalid'] for r in records),strict_JSON_exit_stderr=True,producer_import_or_write=False,source_counts_or_model_changed=False,scope='Synthetic arithmetic/input cases only; no forecast, ballot pool, probability or legal declaration.',cases=records)
(S/'data/coordinator-baseline-cli-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='cases'}))

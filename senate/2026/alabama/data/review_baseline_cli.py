"""Coordinator real-CLI tests: fixed counts, full field, finite types, global keys.
No producer implementation imports or source/model/package writes.
"""
from pathlib import Path
import copy,json,math,subprocess,sys
S=Path(__file__).resolve().parents[1];CALC=S/'data/baselines/calculate.py';records=[]
def close(a,b,tol=1e-10):assert math.isfinite(a)and math.isfinite(b)and abs(a-b)<=tol,(a,b)
def invoke(name,d=None,invalid=False,raw=None):
 text=raw if raw is not None else json.dumps(d,allow_nan=True)
 r=subprocess.run([sys.executable,'-B',str(CALC)],input=text.encode(),capture_output=True,timeout=12)
 assert r.stderr==b'',(name,r.stderr)
 o=json.loads(r.stdout,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
 assert r.returncode==(2 if invalid else 0)and o['status']==('invalid-input'if invalid else'ok'),(name,r.returncode,o)
 records.append({'name':name,'input_text':text,'expected_invalid':invalid,'exit_code':r.returncode,'stderr':'','output':o});return o
cs=[{'id':c,'name':c,'party':c+'party','scope':'named'}for c in ['A','B','C']]
base={'mode':'live','scope':'Coordinator synthetic','assumptions':'Counted fixed; explicit synthetic pools, no forecast','candidates':cs,'pair':['A','B'],'target_pair_margin':.01,'selected_unit':'u','units':[{'key':'u','counted':[30,20,10],'remaining':100,'pair_participation':.8,'a_share':.4,'other_allocation':[1]},{'key':'v','counted':[5,15,0],'remaining':50,'pair_participation':.8,'a_share':.8,'other_allocation':[1]}]}
o=invoke('fixed-counted-full-and-pair-denominators',base)
assert[v['votes']for v in o['counted_candidates_fixed']]==[35,35,10]
close(o['final_pair_denominator'],190);close(o['final_full_candidate_denominator'],230);close(o['target_pair_net_votes'],1.9);close(o['baseline_pair_net_votes'],8);close(o['all_remaining_required_a_share']['raw'],121.9/240);close(o['selected_only']['raw'],57.9/160)
for v,e in zip(o['projected_candidates'],[99,91,40]):close(v['votes'],e)
close(o['common_shift']['unbounded_share_shift'],-6.1/240);close(o['common_shift']['bounded_share_shift'],-6.1/240);close(o['common_shift']['residual_net_votes'],0,1e-8)
close(o['same_net_full_candidate_margin_fraction'],1.9/230);assert not o['legal_outcome_declared']and o['probability']is None
for which,status in [(0,'feasible'),(1,'unknown')]:
 d=copy.deepcopy(base);d['units'][which]['a_share']=None;o=invoke('unknown-'+str(which),d);assert o['common_shift']['status']=='unknown'and o['projected_candidates']is None and o['selected_only']['status']==status
 if which==0:close(o['selected_only']['raw'],57.9/160)
d=copy.deepcopy(base);d['units'][1]['key']=' u ';d['selected_unit']=' u ';o=invoke('literal-key-whitespace-preserved',d);assert o['selected_only']['key']==' u 'and len({r['key']for r in o['units']})==2
hist={'mode':'historical','scope':'Synthetic clipping','assumptions':'Endpoint clipping and full-field independent controls','candidates':cs,'pair':['A','B'],'target_pair_margin':0,'units':[{'key':'lo','votes':[0,10,0],'volume':10},{'key':'hi','votes':[81,9,0],'volume':90}]}
o=invoke('clipped-root-differs-from-unbounded',hist);close(o['common_shift']['unbounded_share_shift'],-.31);close(o['common_shift']['bounded_share_shift'],-31/90);assert o['common_shift']['clipping_applied'];close(o['common_shift']['residual_net_votes'],0,1e-8)
d=copy.deepcopy(hist);d['units']=[{'key':'third','votes':[12,8,80]}];o=invoke('pair-leader-and-pair-tie-both-lose-to-C',d);close(o['a_net_over_highest_other_named'],-68);close(o['target_a_net_over_highest_other_named'],-70);assert max(o['projected_candidates'],key=lambda r:r['votes'])['candidate']['id']=='C'
d=copy.deepcopy(hist);d['units']=[{'key':'zero-pair','votes':[0,0,100]}];o=invoke('zero-pair-undefined-source-share',d);assert o['units'][0]['a_share']is None and o['common_shift']['status']=='no-positive-pool';close(o['final_pair_denominator'],0);close(o['final_full_candidate_denominator'],100)
d=copy.deepcopy(base)
for u in d['units']:u['remaining']=0;u['a_share']=None
o=invoke('counted-only-no-positive-pool',d);assert o['common_shift']['status']=='no-positive-pool'and o['all_remaining_required_a_share']['fixed_target_status']=='impossible'
for side,status in [(0,'secured'),(1,'impossible')]:
 d=copy.deepcopy(base);d['units'][0]['counted']=[1000,0,0]if side==0 else[0,1000,0];o=invoke('selected-raw-'+status,d);assert o['all_remaining_required_a_share']['status']==status
 assert o['all_remaining_required_a_share']['raw']<0 if side==0 else o['all_remaining_required_a_share']['raw']>1
for i,v in enumerate([None,True,False,'0',{},[],float('nan'),float('inf'),-float('inf'),-1.000001,1.000001]):
 d=copy.deepcopy(base);d['target_pair_margin']=v;invoke('invalid-target-'+str(i),d,True)
for branch in ['known','unknown','no-pool']:
 for kind in ['duplicate','missing','empty','space','int','bool']:
  d=copy.deepcopy(base);d.pop('selected_unit')
  if branch=='unknown':d['units'][0]['a_share']=None
  if branch=='no-pool':
   for u in d['units']:u['remaining']=0;u['a_share']=None
  if kind=='duplicate':d['units'][1]['key']='u'
  elif kind=='missing':d['units'][1].pop('key')
  else:d['units'][1]['key']={'empty':'','space':' \t','int':3,'bool':True}[kind]
  invoke('global-key-'+branch+'-'+kind,d,True)
for field,v in [('remaining',-1),('remaining',None),('remaining',True),('remaining','2'),('remaining',float('inf')),('pair_participation',-.1),('pair_participation',1.1),('pair_participation',True),('a_share','0.5'),('a_share',False),('a_share',-.1),('a_share',1.1),('a_share',float('nan')),('other_allocation',{}),('other_allocation',[.5]),('other_allocation',[True]),('other_allocation',[2]),('counted',[30,20]),('counted',[30,20,-1]),('counted',[True,20,10]),('counted',[None,20,10])]:
 d=copy.deepcopy(base);d['units'][0][field]=v;invoke('invalid-unit-'+field+'-'+str(len(records)),d,True)
for name,mut in [('unsupported-mode',lambda d:d.update(mode='runoff')),('pair-collision',lambda d:d.update(pair=['A','A'])),('missing-pair-choice',lambda d:d.update(pair=['A','X'])),('missing-selection',lambda d:d.update(selected_unit='absent')),('blank-selection',lambda d:d.update(selected_unit=' ')),('selection-bool',lambda d:d.update(selected_unit=True)),('duplicate-candidate-id',lambda d:d['candidates'][2].update(id='A')),('duplicate-candidate-name',lambda d:d['candidates'][2].update(name='A')),('empty-candidate-name',lambda d:d['candidates'][2].update(name=' ')),('unsupported-scope',lambda d:d['candidates'][2].update(scope='party')),('extra-input-setting',lambda d:d.update(guess=True)),('aggregate-overflow',lambda d:[u.update(remaining=1e308)for u in d['units']])]:
 d=copy.deepcopy(base);mut(d);invoke(name,d,True)
d=copy.deepcopy(hist);d['units'][0]['votes']=[0,0,0];d['units'][0]['volume']=1;invoke('positive-volume-zero-source-total',d,True)
text=json.dumps(base);invoke('duplicate-root-object-field',raw=text[:-1]+',"mode":"historical"}',invalid=True)
text=json.dumps(base).replace('"remaining": 100','"remaining": 100, "remaining": 100');invoke('duplicate-unit-object-field',raw=text,invalid=True)
result={'status':'pass_actual_CLI_independent_counted_fixed_unknown_clipping_and_input_review','actual_CLI_cases':len(records),'expected_invalid':sum(r['expected_invalid']for r in records),'strict_JSON_exit_empty_stderr':True,'producer_import_or_write':False,'source_or_model_changed':False,'scope':'Synthetic arithmetic/input controls only; no remaining estimate, probability or legal declaration','cases':records}
body=(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode();p=S/'data/coordinator-baseline-cli-review.json'
if '--check'in sys.argv:assert p.read_bytes()==body
else:p.write_bytes(body)
print(json.dumps({k:v for k,v in result.items()if k!='cases'}))

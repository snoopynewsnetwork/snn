"""Independent real CLI bounds, counted-fixed, full-field and unknown tests."""
from pathlib import Path
import copy,json,math,subprocess,sys
S=Path(__file__).resolve().parents[1];CALC=S/'data/baselines/calculator.py';records=[]
def close(a,b,tol=1e-10):assert math.isfinite(a)and math.isfinite(b)and abs(a-b)<=tol,(a,b)
def invoke(name,d=None,invalid=False,raw=None):
 text=raw if raw is not None else json.dumps(d,allow_nan=True)
 p=subprocess.run([sys.executable,'-B',str(CALC),'-'],input=text.encode(),capture_output=True,timeout=15)
 assert p.stderr==b'',(name,p.stderr)
 o=json.loads(p.stdout,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
 assert p.returncode==(2 if invalid else 0)and(o['status']=='invalid-input'if invalid else o['status']in ['ok','unknown']),(name,p.returncode,o)
 records.append({'name':name,'input_text':text,'expected_invalid':invalid,'exit':p.returncode,'stderr':'','output':o});return o
base={'mode':'live','objective':'pair_margin','pair':['A','B'],'other_candidates':['C'],'target_margin':.01,'selected_unit':'u','assumptions':'Coordinator synthetic fixed counts and explicit pools; no forecast','source_scope':'Synthetic source scope','units':[{'key':'u','counted':{'A':30,'B':20,'C':10},'remaining':100,'pair_participation':.8,'a_share':.4,'other_allocation':{'C':1}},{'key':'v','counted':{'A':5,'B':15,'C':0},'remaining':50,'pair_participation':.8,'a_share':.8,'other_allocation':{'C':1}}]}
o=invoke('fixed-counted-final-denominators-selected-only',base);assert o['counted_fixed']=={'A':35,'B':35,'C':10};close(o['final_pair_denominator'],190);close(o['final_all_candidate_denominator'],230);close(o['target_net_votes'],1.9);close(o['baseline']['pair_net_votes'],8);close(o['selected']['required_a_share_raw'],57.9/160)
for k,v in {'A':99,'B':91,'C':40}.items():close(o['baseline']['votes'][k],v)
close(o['uniform']['unbounded_pair_share_shift'],-6.1/240);close(o['uniform']['bounded_common_share_shift'],-6.1/240);close(o['uniform']['target']['pair_net_votes'],1.9,1e-8)
for selected_unknown in [True,False]:
 d=copy.deepcopy(base);d['units'][0 if selected_unknown else 1]['a_share']=None;o=invoke('unknown-selected-'+str(selected_unknown),d);assert o['status']=='unknown'and o['baseline']is None and o['uniform']is None
 if selected_unknown:close(o['selected']['required_a_share_raw'],57.9/160)
 else:assert o['selected']['status']=='unknown-other-unit-preferences'
d=copy.deepcopy(base);d['units'][1]['key']=' u ';d['selected_unit']=' u ';o=invoke('exact-literal-key-not-trimmed',d);assert o['selected']['key']==' u '
hist={'mode':'historical','objective':'pair_margin','pair':['A','B'],'other_candidates':['C'],'target_margin':0,'source_scope':'Synthetic clipping','assumptions':'Clipped common shift is distinct from pair algebra','units':[{'key':'lo','counted':{'A':0,'B':0,'C':0},'remaining':10,'pair_participation':1,'a_share':0,'other_allocation':{'C':1}},{'key':'hi','counted':{'A':0,'B':0,'C':0},'remaining':90,'pair_participation':1,'a_share':.9,'other_allocation':{'C':1}}]}
o=invoke('actual-clipped-root-differs-from-unbounded',hist);close(o['uniform']['unbounded_pair_share_shift'],-.31);close(o['uniform']['bounded_common_share_shift'],-31/90);assert o['uniform']['clipped_units']==['lo'];close(o['uniform']['target']['pair_net_votes'],0,1e-8)
d=copy.deepcopy(hist);d['units']=[{'key':'third','counted':{'A':0,'B':0,'C':0},'remaining':100,'pair_participation':.2,'a_share':.6,'other_allocation':{'C':1}}];d['selected_unit']='third';o=invoke('pair-leader-and-pair-tie-both-lose-to-C',d);close(o['baseline']['a_full_field_lead'],-68);close(o['uniform']['target']['a_full_field_lead'],-70);close(o['selected']['required_pair_share_raw'],.5);close(o['selected']['required_full_plurality_share_raw'],4)
d['objective']='full_candidate_plurality';o=invoke('full-field-objective-impossible-when-pair-tie-feasible',d);assert o['uniform']['status']=='impossible'and o['selected']['status']=='impossible';close(o['selected']['required_a_share_raw'],4)
d=copy.deepcopy(base);d['objective']='full_candidate_plurality';o=invoke('full-field-positive-cushion-has-full-denominator',d);close(o['target_net_votes'],2.3);close(o['uniform']['target']['a_full_field_lead'],2.3,1e-8)
d=copy.deepcopy(base)
for u in d['units']:u['remaining']=0;u['a_share']=None
o=invoke('counted-only-zero-pool-no-unknown-inference',d);assert o['uniform']['status']=='no-positive-pool'and o['uniform']['fixed_target_status']=='unmet'
for ahead,status in [(True,'secured'),(False,'impossible')]:
 d=copy.deepcopy(base);d['units'][0]['counted']={'A':1000,'B':0,'C':0}if ahead else{'A':0,'B':1000,'C':0};o=invoke('selected-only-raw-'+status,d);assert o['selected']['status']==status;assert(o['selected']['required_a_share_raw']<0 if ahead else o['selected']['required_a_share_raw']>1)
for i,v in enumerate([None,True,False,'0',{},[],float('nan'),float('inf'),-float('inf'),-1.0001,1.0001]):
 d=copy.deepcopy(base);d['target_margin']=v;invoke('invalid-fractional-target-'+str(i),d,True)
for branch in ['known','unknown','no-pool']:
 for kind in ['duplicate','missing','empty','space','int','bool']:
  d=copy.deepcopy(base);d.pop('selected_unit')
  if branch=='unknown':d['units'][0]['a_share']=None
  if branch=='no-pool':
   for u in d['units']:u['remaining']=0;u['a_share']=None
  if kind=='duplicate':d['units'][1]['key']='u'
  elif kind=='missing':d['units'][1].pop('key')
  else:d['units'][1]['key']={'empty':'','space':' \t','int':7,'bool':False}[kind]
  invoke('global-key-'+branch+'-'+kind,d,True)
for field,v in [('remaining',-1),('remaining',None),('remaining',True),('remaining','3'),('remaining',float('inf')),('pair_participation',-.1),('pair_participation',1.1),('pair_participation',True),('a_share','0.5'),('a_share',False),('a_share',-.1),('a_share',1.1),('a_share',float('nan')),('other_allocation',[]),('other_allocation',{'C':.5}),('other_allocation',{'C':True}),('other_allocation',{'X':1}),('counted',{'A':0,'B':0}),('counted',{'A':0,'B':0,'C':-1}),('counted',{'A':True,'B':0,'C':0}),('counted_total',59),('counted_total',True)]:
 d=copy.deepcopy(base);d['units'][0][field]=v;invoke('invalid-unit-'+field+'-'+str(len(records)),d,True)
for name,fn in [('unsupported-mode',lambda d:d.update(mode='runoff')),('unsupported-objective',lambda d:d.update(objective='forecast')),('duplicate-pair',lambda d:d.update(pair=['A','A'])),('other-collision',lambda d:d.update(other_candidates=['A'])),('missing-selection',lambda d:d.update(selected_unit='absent')),('blank-selection',lambda d:d.update(selected_unit=' ')),('selection-bool',lambda d:d.update(selected_unit=False)),('extra-setting',lambda d:d.update(repair=True)),('overflow',lambda d:[u.update(remaining=1e308)for u in d['units']])]:
 d=copy.deepcopy(base);fn(d);invoke(name,d,True)
invoke('duplicate-root-object-field',raw=json.dumps(base)[:-1]+',"mode":"historical"}',invalid=True)
invoke('duplicate-unit-object-field',raw=json.dumps(base).replace('"remaining": 100','"remaining": 100,"remaining": 100'),invalid=True)
result={'status':'pass_actual_CLI_independent_pair_full_field_counted_fixed_unknown_clipping_and_input_review','actual_CLI_cases':len(records),'expected_invalid':sum(r['expected_invalid']for r in records),'strict_JSON_exit_empty_stderr':True,'producer_import_or_write':False,'no_current_pool_forecast_probability_or_legal_declaration':True,'cases':records}
body=(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode();p=S/'data/coordinator-baseline-cli-review.json'
if '--check'in sys.argv:assert p.read_bytes()==body
else:p.write_bytes(body)
print(json.dumps({k:v for k,v in result.items()if k!='cases'}))

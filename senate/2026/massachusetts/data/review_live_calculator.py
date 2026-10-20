"""Independent CLI fixtures with complete saved inputs and strict JSON output."""
from pathlib import Path
import copy,hashlib,json,math,subprocess,sys
S=Path(__file__).resolve().parents[1];D=S/'data/coordinator-live-input-review';CALC=S/'data/baselines/calculate.py'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def base():return dict(candidates=['A','B','C'],A='A',B='B',units=[dict(key='unit-1',counted=dict(A=60,B=40,C=500),allocation=dict(A=.5,B=.5,C=0),remaining_pool=dict(status='known',votes=100))],target_margin=.01)
def main():
 D.mkdir(exist_ok=True);cases=[]
 for label,v in [('target_null',None),('target_bool',True),('target_text','0'),('target_nan',float('nan')),('target_posinf',float('inf')),('target_neginf',float('-inf')),('target_range',1.01)]:
  x=base();x['target_margin']=v;cases.append((label,x,False))
 for label,v in [('key_null',None),('key_blank',' '),('key_number',1),('key_list',[])]:
  x=base();x['units'][0]['key']=v;cases.append((label,x,False))
 x=base();x['units'].append(copy.deepcopy(x['units'][0]));cases.append(('global_duplicate_no_selected',x,False))
 for field,v,label in [('counted',-1,'negative_counted'),('counted',True,'bool_counted'),('counted',1e308,'overflow_counted'),('allocation',float('nan'),'nonfinite_allocation'),('allocation',1.1,'allocation_range')]:
  x=base();x['units'][0][field]['A']=v
  if label=='overflow_counted':x['units'][0]['counted']['B']=v
  cases.append((label,x,False))
 x=base();x['units'][0]['remaining_pool']['votes']=-1;cases.append(('negative_remaining',x,False))
 x=base();x['units'][0]['remaining_pool']=dict(status='unknown',votes=100);cases.append(('unknown_guessed_count',x,False))
 x=base();del x['units'][0]['counted']['C'];cases.append(('incomplete_counted_field',x,False))
 x=base();x['selected_key']='absent';cases.append(('missing_selected',x,False))
 cases.append(('pair_target_other_candidate_wins',base(),True))
 x=base();x['units'][0]['remaining_pool']=dict(status='unknown');cases.append(('unknown_pool',x,True))
 x=base();x['units'][0]['remaining_pool']['votes']=0;cases.append(('no_pool',x,True))
 x=base();x['units'][0]['counted']=dict(A=1000,B=0,C=0);cases.append(('already_secured',x,True))
 results=[]
 for label,x,valid in cases:
  p=D/(label+'.json');p.write_text(json.dumps(x,indent=2)+'\n');cp=subprocess.run([sys.executable,'-B','-S',str(CALC),'live',str(p)],capture_output=True,text=True);assert not cp.stderr
  out=json.loads(cp.stdout,parse_constant=lambda c:(_ for _ in()).throw(ValueError(c)));assert cp.returncode==(0 if valid else 2),(label,cp.stdout)
  if not valid:assert out['status']=='invalid_input'and out['error']
  elif label=='pair_target_other_candidate_wins':
   assert out['counted']==dict(A=60,B=40,C=500);assert out['final']==dict(A=110,B=90,C=500);assert out['final_denominator']==700;assert math.isclose(out['pair_requirement']['raw_share'],.41);assert out['leaders']==['C'];assert out['full_field_A_strict_plurality_share_threshold']>1
  elif label=='unknown_pool':assert out['status']=='unknown_remaining_pool'and out['final']is None and out['final_denominator']is None
  elif label=='no_pool':assert out['pair_requirement']['status']=='no_positive_pool'
  elif label=='already_secured':assert out['pair_requirement']['status']=='already_secured'
  results.append(dict(label=label,input=pin(p),exit=cp.returncode,stderr=cp.stderr,complete_output=out))
 out=dict(status='pass_actual_strict_CLI_arithmetic_and_negative_input_review',calculator=pin(CALC),case_count=len(cases),positive_cases=4,negative_cases=len(cases)-4,all_original_inputs_outputs=results,qualification='Synthetic arithmetic only; counted full candidate field staysfixed, pair target may lose full-field plurality. No real remaining pool/current source approval.')
 p=D/'review.json';p.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(dict(cases=len(cases),pin=pin(p)))
if __name__=='__main__':main()

"""Actual CLI regressions against a fixed captured calculator version."""
from pathlib import Path
import copy, hashlib, json, subprocess, sys
D=Path(__file__).resolve().parent;B=D/'baselines';H=D/'coordinator-baseline-input-review'

def main():
 H.mkdir(exist_ok=True)
 base={'mode':'live','counted':{'A':120,'B':80,'other':{'Third':75}},'remaining':[{'key':'one','volume':100,'pair_participation':.8,'share':.4,'other_allocation':{'Third':1}},{'key':'two','volume':50,'pair_participation':1,'share':.6,'other_allocation':{}}],'denominator':'final_all_choice','target_margin':.01,'selected':'one'}
 cases=[('ordinary_final_all_choice',base,True),('zero_pool',{'mode':'live','counted':{'A':5,'B':4},'remaining':[]},True),('unknown_pool',{'mode':'live','counted':{'A':5,'B':4},'remaining':[{'key':'u','volume':None,'pair_participation':1,'share':None}]},True),('secured',{'mode':'live','counted':{'A':500,'B':1},'remaining':[{'key':'u','volume':10,'pair_participation':1,'share':.5}]},True),('impossible',{'mode':'live','counted':{'A':1,'B':500},'remaining':[{'key':'u','volume':10,'pair_participation':1,'share':.5}]},True),('bounded_uniform',{'mode':'uniform','units':[{'key':'a','pair_volume':100,'share':.99},{'key':'b','pair_volume':100,'share':.1}],'target_margin':.8},True),('selected_unknown_own_preference',{'mode':'selected','units':[{'key':'a','pair_volume':100,'share':None},{'key':'b','pair_volume':100,'share':.6}],'selected':'a'},True)]
 for i,value in enumerate([True,None,'0.1',float('nan'),float('inf'),float('-inf'),1.01,-1.01]):
  x=copy.deepcopy(base);x['target_margin']=value;cases.append(('invalid_target_'+str(i),x,False))
 for name,path,value in [('boolean_count',['counted','A'],True),('negative_count',['counted','B'],-1),('text_count',['counted','A'],'10'),('infinite_count',['counted','A'],1e309),('null_other',['counted','other'],None),('list_other',['counted','other'],[]),('bool_volume',['remaining',0,'volume'],True),('negative_volume',['remaining',0,'volume'],-1),('text_share',['remaining',0,'share'],'0.4'),('bool_participation',['remaining',0,'pair_participation'],True),('nan_allocation',['remaining',0,'other_allocation'],{'Third':float('nan')}),('null_allocation',['remaining',0,'other_allocation'],None),('wrong_allocation_sum',['remaining',0,'other_allocation'],{'Third':.4})]:
  x=copy.deepcopy(base);dest=x
  for key in path[:-1]:dest=dest[key]
  dest[path[-1]]=value;cases.append((name,x,False))
 x=copy.deepcopy(base);x['remaining'][1]['key']='one';x.pop('selected');cases.append(('global_duplicate_no_selected',x,False))
 x=copy.deepcopy(base);x['remaining'][0]['key']=' ';x.pop('selected');cases.append(('blank_key',x,False))
 x=copy.deepcopy(base);x['remaining'][0]['volume']=None;x['remaining'][0]['share']='unknown';cases.append(('invalid_before_unknown',x,False))
 for mode in ['uniform','selected']:
  x={'mode':mode,'units':[{'key':'a','pair_volume':100,'share':.5}],'target_margin':float('nan'),'selected':'a'};cases.append(('nonfinite_'+mode,x,False))
 for mode,more in [('county',{'county':'UnknownCounty'}),('native',{'mix':{'2020-senate':1}}),('county',{'mix':{'2024-president':float('inf')}}),('county',{'mix':{'2024-president':True}})]:
  cases.append(('historical_'+str(len(cases)),{'mode':mode,**more},False))
 results=[]
 for name,arg,valid in cases:
  raw=(json.dumps(arg,indent=2,allow_nan=True)+'\n').encode();p=H/(name+'.input.json');p.write_bytes(raw)
  proc=subprocess.run([sys.executable,'-B','-S',str(B/'scripts/calculator.py'),str(p)],capture_output=True)
  out=json.loads(proc.stdout,parse_constant=lambda value:(_ for _ in ()).throw(ValueError(value)))
  passed=proc.returncode==0 and proc.stderr==b'' and out.get('ok')is valid
  if name=='ordinary_final_all_choice' and passed:
   z=out['result'];passed=(z['counted_fixed']==base['counted']and z['final_A']==182 and z['final_B']==148 and z['final_other']=={'Third':95}and z['final_all_choice_volume']==425 and abs(z['unbounded_required_remaining_A_share']-.3625)<1e-12 and abs(z['selected_only']['required_share_unbounded']-.2140625)<1e-12)
  for suffix,body in [('stdout.json',proc.stdout),('stderr.txt',proc.stderr)]:
   (H/(name+'.'+suffix)).write_bytes(body)
  results.append({'name':name,'valid_expected':valid,'passed':passed,'exit':proc.returncode,'input_sha256':hashlib.sha256(raw).hexdigest(),'output':out,'stderr':proc.stderr.decode(errors='replace')})
 out={'status':'pass'if all(x['passed']for x in results)else'fail','actual_cases':len(results),'actual_failures':sum(not x['passed']for x in results),'calculator':{'path':'data/baselines/scripts/calculator.py','bytes':(B/'scripts/calculator.py').stat().st_size,'sha256':hashlib.sha256((B/'scripts/calculator.py').read_bytes()).hexdigest()},'fixed_counted_and_final_denominator_analytic_control':True,'cases':results,'producer_files_written':False}
 (H/'review.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='cases'}));assert out['actual_failures']==0

if __name__=='__main__':main()

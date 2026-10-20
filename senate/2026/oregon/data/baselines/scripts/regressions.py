"""Execute real CLI fixtures and independent analytic bounded-root/denominator oracles."""
import copy,hashlib,json,math,random,subprocess,sys
from pathlib import Path
from calculator import R,solve
from county import js

def main():
 fixtures=[]
 def add(name,input,ok=True,status=None):fixtures.append({'name':name,'input':input,'expected_ok':ok,'expected_status':status})
 U=[{'key':'one','pair_volume':900,'share':.99},{'key':'two','pair_volume':100,'share':.01}]
 add('bounded-clipping',{'mode':'uniform','units':U,'target_margin':.99},status='requires_improvement')
 add('negative-shift-already-winning',{'mode':'uniform','units':U},status='already_at_or_above_target')
 add('unknown-preference',{'mode':'uniform','units':[{'key':'unknown','pair_volume':100,'share':None}]},status='unknown_source_preference')
 add('zero-volume',{'mode':'uniform','units':[{'key':'zero','pair_volume':0,'share':None}]},status='no_positive_pool')
 for name,val in [('bool',True),('null',None),('text','0.01'),('object',{}),('range',1.1)]:
  add('uniform-invalid-target-'+name,{'mode':'uniform','units':U,'target_margin':val},False)
  add('selected-invalid-target-'+name,{'mode':'selected','units':U,'selected':'one','target_margin':val},False)
  add('county-invalid-target-'+name,{'mode':'county','target_margin':val},False)
 for name,val in [('bool',True),('negative',-1),('text','10'),('null',None)]:add('uniform-invalid-volume-'+name,{'mode':'uniform','units':[{'key':'u','pair_volume':val,'share':.5}]},False)
 for name,keys in [('duplicates',['a','a']),('blank',['a','']),('nonstring',['a',2])]:add('globally-invalid-keys-'+name,{'mode':'uniform','units':[{'key':k,'pair_volume':1,'share':None} for k in keys]},False)
 add('unknown-county',{'mode':'county','county':'Atlantis'},False)
 for i,mix in enumerate([True,None,[],{}, {'2020-senate':True},{'2020-senate':-1},{'2024-president':.5},{'2024-president':2},{'bad':1},{'2020-senate':1,'2024-president':1}]):add('bad-mix-'+str(i),{'mode':'county','mix':mix},False)
 add('unsupported-denominator',{'mode':'county','denominator':'ballots'},False)
 add('unknown-source-key',{'mode':'uniform','source_scope':'native','units':[{'key':'bad','pair_volume':10,'share':.5}]},False)
 add('selected-impossible',{'mode':'selected','selected':'one','units':[{'key':'one','pair_volume':10,'share':.4},{'key':'two','pair_volume':100,'share':.1}]},status='impossible_even_at_one')
 add('selected-secured',{'mode':'selected','selected':'one','units':[{'key':'one','pair_volume':10,'share':.4},{'key':'two','pair_volume':100,'share':.9}]},status='secured_even_at_zero')
 live={'mode':'live','counted':{'A':40,'B':60,'other':{'Named C':10}},'remaining':[{'key':'r','volume':100,'pair_participation':.8,'share':.6,'other_allocation':{'Named C':1}}],'target_margin':.01,'denominator':'final_pair','selected':'r'}
 add('live-final-pair',live,status='feasible');add('live-final-all-choice',{**live,'denominator':'final_all_choice'},status='feasible')
 add('live-third-candidate-wins',{**live,'counted':{'A':40,'B':60,'other':{'Named C':300}}},status='feasible')
 add('live-unknown-volume',{**live,'remaining':[{**live['remaining'][0],'volume':None}]},status='unknown_remaining_volume_mix_or_preference')
 add('live-unknown-preference',{**live,'remaining':[{**live['remaining'][0],'share':None}]},status='unknown_remaining_volume_mix_or_preference')
 add('live-no-pool',{**live,'remaining':[],'selected':None},False)
 add('live-no-pool-valid',{'mode':'live','counted':live['counted'],'remaining':[]},status='no_positive_pool')
 for name,A,B in [('impossible',0,200),('secured',200,0)]:add('live-'+name,{**live,'counted':{'A':A,'B':B,'other':{}}},status='impossible_even_at_one' if name=='impossible' else 'secured_even_at_zero')
 for name,field,value in [('negative','volume',-1),('bool-volume','volume',True),('bad-share','share',True),('bad-participation','pair_participation',1.1),('bad-other','other_allocation',{'C':.5})]:add('live-invalid-'+name,{**live,'remaining':[{**live['remaining'][0],field:value}]},False)
 add('live-counted-bool',{**live,'counted':{'A':True,'B':1}},False)
 add('live-duplicate-keys',{**live,'remaining':live['remaining']*2},False)
 add('live-unknown-selected-with-unknown-pool',{**live,'selected':'bad','remaining':[{**live['remaining'][0],'volume':None}]},False)
 add('county-positive-historical-mix',{'mode':'county','preference':'2022-governor','mix':{'2020-senate':.2,'2022-senate':.3,'2024-president':.5}},status=None)
 add('county-selected-positive',{'mode':'county','county':'Multnomah','preference':'2024-president'},status=None)
 out=[]
 for f in fixtures:
  p=R/'fixtures'/(f['name']+'.input.json');p.write_text(json.dumps(f['input'],indent=2,allow_nan=False)+'\n')
  result=subprocess.run([sys.executable,'-B',str(R/'scripts/calculator.py'),str(p)],capture_output=True,text=True)
  o=json.loads(result.stdout,parse_constant=lambda v:(_ for _ in ()).throw(AssertionError(v)))
  assert result.returncode==0 and result.stderr=='',(f['name'],result.stderr)
  assert o['ok']==f['expected_ok'],(f['name'],o)
  if f['expected_status']:assert o['result']['status']==f['expected_status'],(f['name'],o)
  if f['name'].startswith('live-final-'):
   rr=o['result'];assert rr['final_A']==88 and rr['final_B']==92 and math.isclose(rr['final_other']['Named C'],30);assert rr['final_pair_volume']==180 and rr['final_all_choice_volume']==210
   denominator=180 if f['name']=='live-final-pair' else 210;assert rr['final_denominator']==denominator
   expected=(.01*denominator-(-20)+80)/(2*80);assert abs(expected-rr['unbounded_required_remaining_A_share'])<1e-12
  if f['name']=='live-third-candidate-wins':assert not o['result']['A_strict_plurality'] and o['result']['named_full_field_winner']=='Named C'
  out.append({**{k:v for k,v in f.items() if k!='input'},'input_path':str(p.relative_to(R)),'returncode':result.returncode,'output':o,'passed':True})
 # Invalid JSON nonfinite literals must fail cleanly; no nonfinite echo.
 for name,token in [('nan','NaN'),('inf','Infinity'),('minusinf','-Infinity')]:
  body='{"mode":"uniform","target_margin":'+token+',"units":[]}';p=R/'fixtures'/(name+'.input.json');p.write_text(body+'\n');q=subprocess.run([sys.executable,'-B',str(R/'scripts/calculator.py'),str(p)],capture_output=True,text=True);o=json.loads(q.stdout);assert not o['ok'] and not q.stderr;out.append({'name':name,'input_path':str(p.relative_to(R)),'output':o,'passed':True})
 # Oracle: solve piecewise-linear clipped sums analytically on all breakpoints.
 random.seed(20261020);oracles=[]
 for i in range(120):
  u=[{'key':str(j),'pair_volume':random.randint(1,500),'share':random.random()} for j in range(random.randint(1,15))];m=random.uniform(-.99,.99);T=sum(r['pair_volume'] for r in u);target=m*T;breaks=sorted({-1.,1.,*[-r['share'] for r in u],*[1-r['share'] for r in u]})
  def net(d):return sum(r['pair_volume']*(2*min(1,max(0,r['share']+d))-1) for r in u)
  truth=None
  for a,b in zip(breaks,breaks[1:]):
   na,nb=net(a),net(b)
   if na<=target<=nb and nb>na:truth=a+(target-na)*(b-a)/(nb-na);break
  assert truth is not None
  got=solve({'units':u,'target_margin':m});assert got['bounded_feasible'];assert abs(got['bounded_share_shift']-truth)<1e-10
  assert abs(sum(r['target_net_votes'] for r in got['units'])-target)<max(1e-7,T*1e-12)
  oracles.append({'case':i,'analytic_root':truth,'bisection_root':got['bounded_share_shift'],'residual_votes':got['residual_net_votes'],'passed':True})
 js('fixtures/results.json',out);js('bounded-root-oracle.json',oracles)
 print(json.dumps({'real_CLI_cases':len(out),'analytic_root_checks':len(oracles),'passed':True}))
if __name__=='__main__':main()

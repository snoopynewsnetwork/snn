#!/usr/bin/env python3
"""Run actual CLI fixtures and independently verify historical piecewise roots."""
import copy,csv,gzip,json,math,os,subprocess,sys,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parent
F=P/'fixtures';F.mkdir(exist_ok=True)
def dump(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def close(a,b,tol=1e-7):assert abs(a-b)<=tol*max(1,abs(b)),(a,b)
def unit(key='u',a=0,b=0,c=0,r=100,p=.8,q=.6):return {'key':key,'counted':{'A':a,'B':b,'C':c},'remaining':r,'pair_participation':p,'a_share':q,'other_allocation':{'C':1}}
def case(us=None,**kw):return {'mode':'live','objective':'pair_margin','pair':['A','B'],'other_candidates':['C'],'units':us if us is not None else [unit()],**kw}
def main():
 cases={
 'counted-final':case([unit(a=40,b=60,c=10,r=100,p=.8,q=.75)],selected_unit='u'),
 'unknown':case([unit(q=None)]),
 'no-pool':case([unit(a=6,b=4,c=3,r=0,q=None)]),
 'zero-pair':case([unit(c=5,r=10,p=0,q=None)]),
 'secured-selected':case([unit('big',a=100,r=0),unit('small',r=10,p=1)],selected_unit='small'),
 'impossible-selected':case([unit('big',b=100,r=0),unit('small',r=10,p=1)],selected_unit='small'),
 'selected-own-unknown':case([unit(q=None)],selected_unit='u'),
 'selected-other-unknown':case([unit('unknown',q=None),unit('chosen')],selected_unit='chosen'),
 'clipping':case([unit('one',r=100,p=1,q=.99),unit('two',r=100,p=1,q=.01)],target_margin=.8),
 'negative-shift':case([unit(r=100,p=1,q=.9)]),
 'pair-leader-loses-field':case([unit(a=60,b=40,c=100,r=0)]),
 'full-field-positive':case([unit(a=60,b=40,c=100,r=100,p=.8,q=.6)],objective='full_candidate_plurality'),
 'full-impossible':case([unit(c=1000,r=100,p=1,q=.6)],objective='full_candidate_plurality'),
 'full-secured':case([unit(a=1000,r=100,p=1,q=.6)],objective='full_candidate_plurality'),
 'target-minus-one':case(target_margin=-1),
 'target-plus-one':case(target_margin=1),
 'literal-key-preserved':case([unit(' u ')] , selected_unit=' u '),
 'historical-cli':{**case([unit(r=100,p=1,q=.3)]),'mode':'historical'},
 }
 invalid={}
 for name,v in [('bool',True),('null',None),('text','0'),('above',1.01),('below',-1.01),('nan',float('nan')),('posinf',float('inf')),('neginf',float('-inf'))]:invalid['target-'+name]=case(target_margin=v)
 for branch,us in [('unknown',[unit(q=None)]),('no-pool',[unit(r=0,q=None)])]:
  for name,key in [('duplicate','u'),('missing','__missing__'),('blank',' \t'),('nonstring',1)]:
   u=unit(key,r=0,q=None)
   if key=='__missing__':del u['key']
   invalid[branch+'-key-'+name]=case(us+[u])
 for name,f,v in [('negative-count','counted',{'A':-1,'B':0,'C':0}),('bool-count','counted',{'A':True,'B':0,'C':0}),('nonfinite-count','counted',{'A':float('inf'),'B':0,'C':0}),('negative-pool','remaining',-1),('null-pool','remaining',None),('negative-share','a_share',-.1),('bool-share','a_share',False),('text-share','a_share','0.5'),('large-share','a_share',1.1),('large-participation','pair_participation',1.1),('bool-participation','pair_participation',True),('missing-other','other_allocation',{}),('unbalanced-other','other_allocation',{'C':.9}),('negative-other','other_allocation',{'C':-1}),('all-small','counted_total',-1),('all-disagrees','counted_total',1)]:
  u=unit();u[f]=v;invalid[name]=case([u])
 invalid.update({'duplicate-candidate':{**case(),'other_candidates':['A']},'same-pair':{**case(),'pair':['A','A']},'unsupported-mode':{**case(),'mode':'probability'},'unsupported-objective':{**case(),'objective':'runoff'},'overflow':case([unit('a',a=1e308),unit('b',a=1e308)]),'selected-not-found':case(selected_unit='missing'),'invalid-shape':[],'empty-units':case([]),'numeric-unit':[1]})
 receipts={};outputs={};failures=[]
 for name,d in {**cases,**invalid}.items():
  raw=json.dumps(d,allow_nan=True)
  (F/(name+'.input.json')).write_text(raw+'\n')
  proc=subprocess.run([sys.executable,str(P/'calculator.py'),str(F/(name+'.input.json'))],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  (F/(name+'.stdout.json')).write_text(proc.stdout);(F/(name+'.stderr.txt')).write_text(proc.stderr)
  try:
   out=json.loads(proc.stdout,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)));assert not proc.stderr
   if name in invalid:assert proc.returncode==2 and out['status']=='invalid-input'
   else:assert proc.returncode==0 and out['status']!='invalid-input';outputs[name]=out
  except Exception as e:failures.append({'case':name,'error':repr(e),'exit':proc.returncode})
  receipts[name]={'exit':proc.returncode,'stderr_bytes':len(proc.stderr.encode()),'expected_invalid':name in invalid}
 # Duplicate object keys must not overwrite even in an unknown/no-pool branch.
 raw=json.dumps(case([unit(r=0,q=None)]));raw=raw.replace('"target_margin": 0','"target_margin":0,"target_margin":0') if 'target_margin' in raw else raw[:-1]+',"target_margin":0,"target_margin":0}'
 (F/'duplicate-json-field.input.json').write_text(raw);proc=subprocess.run([sys.executable,str(P/'calculator.py'),str(F/'duplicate-json-field.input.json')],capture_output=True,text=True);(F/'duplicate-json-field.stdout.json').write_text(proc.stdout);(F/'duplicate-json-field.stderr.txt').write_text(proc.stderr);assert proc.returncode==2 and not proc.stderr;receipts['duplicate-json-field']={'exit':proc.returncode,'stderr_bytes':len(proc.stderr)}
 dump(F/'cli-receipts.json',receipts)
 if failures:
  dump(F/'failures.json',failures);(F/'failing-calculator.py').write_bytes((P/'calculator.py').read_bytes());raise AssertionError(failures)
 r=outputs['counted-final'];close(r['final_pair_denominator'],180);close(r['final_all_candidate_denominator'],210);close(r['baseline']['votes']['A'],100);close(r['baseline']['votes']['B'],80);close(r['baseline']['votes']['C'],30);close(r['selected']['required_a_share_raw'],.625)
 assert r['counted_fixed']=={'A':40.,'B':60.,'C':10.}
 assert outputs['unknown']['status']=='unknown';assert outputs['zero-pair']['baseline']['pair_margin'] is None
 assert outputs['no-pool']['uniform']['fixed_target_status']=='met';assert outputs['selected-other-unknown']['selected']['status']=='unknown-other-unit-preferences'
 close(outputs['selected-own-unknown']['selected']['required_a_share_raw'],.5)
 close(outputs['secured-selected']['selected']['required_a_share_raw'],-4.5);close(outputs['impossible-selected']['selected']['required_a_share_raw'],5.5)
 r=outputs['clipping'];close(r['uniform']['unbounded_pair_share_shift'],.4);close(r['uniform']['bounded_common_share_shift'],.79);close(r['uniform']['target']['pair_net_votes'],160);assert r['uniform']['clipped_units']==['one']
 close(outputs['negative-shift']['uniform']['bounded_common_share_shift'],-.4)
 assert outputs['pair-leader-loses-field']['baseline']['pair_net_votes']==20 and outputs['pair-leader-loses-field']['baseline']['a_full_field_status']=='behind'
 assert outputs['full-impossible']['uniform']['status']=='impossible' and outputs['full-secured']['uniform']['status']=='secured'
 # All historical scenarios: independent piecewise-linear root (no binary search/calc imports).
 states=list(csv.DictReader((P/'state-scenarios.csv').open()));rows=csv.DictReader((P/'unit-targets.csv').open());tables={}
 for r in rows:tables.setdefault((r['scenario'],float(r['target_pair_margin'])),[]).append(r)
 checked=0;maxres=0
 for st in states:
  name=st['scenario'];target=float(st['target_pair_margin']);d=json.loads((P/'scenarios'/f'{name}.input.json').read_text());us=d['units'];ts=[u['remaining']*u['pair_participation'] for u in us];qs=[u['a_share'] for u in us];T=math.fsum(ts);wanted=target*T
  def net(delta):return math.fsum(t*(2*min(1,max(0,(q or 0)+delta))-1) for t,q in zip(ts,qs))
  breaks=sorted({-1.,1.}|{x for q,t in zip(qs,ts) if t>0 for x in [-(q or 0),1-(q or 0)]});root=None
  for l,h in zip(breaks,breaks[1:]):
   nl,nh=net(l),net(h)
   if nl-1e-8<=wanted<=nh+1e-8:
    root=l+(wanted-nl)*(h-l)/(nh-nl) if nh!=nl else l;break
  assert root is not None;close(root,float(st['bounded_share_shift']),1e-9);res=abs(net(root)-wanted);assert res<1e-6;maxres=max(maxres,res)
  tab=tables[(name,target)];assert len(tab)==len(us);close(math.fsum(float(r['state_pair_weight']) for r in tab),1,1e-10);close(math.fsum(float(r['state_all_candidate_weight']) for r in tab),1,1e-10)
  M=net(0)
  for u,t,q,r in zip(us,ts,qs,tab):
   assert u['key']==r['key'];close(float(r['net_per_1_share_pp']),.02*t);close(float(r['baseline_net']),t*(2*(q or 0)-1));close(float(r['target_net']),t*(2*min(1,max(0,(q or 0)+root))-1))
   if t:
    req=(wanted-(M-t*(2*q-1))+t)/(2*t);close(float(r['selected_only_required_raw']),req);close((M-t*(2*q-1))+t*(2*req-1),wanted,1e-6)
   else:assert r['selected_only_status']=='no-positive-pool' and not r['baseline_a_share']
   checked+=1
 dump(P/'calculator-validation.json',{'status':'pass','cli_cases':len(receipts),'invalid_cases':len(invalid)+1,'historical_states':len(states),'unit_contributions_checked':checked,'independent_root_method':'piecewise linear interpolation at every -q and 1-q clipping knot; no calculator import','max_state_net_residual':maxres,'all_counted_fixed_final_denominator_checks':True,'strict_json_exit_stderr':True})
 print('calculator checks pass',len(receipts),len(states),checked,maxres)
if __name__=='__main__':main()

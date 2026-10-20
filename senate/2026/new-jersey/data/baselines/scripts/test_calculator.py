#!/usr/bin/env python3
import copy,json,math,subprocess,sys
from pathlib import Path
from calculator import live,state,InputError
D=Path(__file__).resolve().parents[1];O=D/'synthetic';O.mkdir(exist_ok=True)
def obj(A=40,B=60,C=0,U=100,p=1,q=.6,m=0,den='pair',key='u'):
 return {'target_margin':m,'denominator':den,'expected_keys':[key],'selected_key':key,'units':[{'key':key,'counted':{'A':A,'B':B,'others':{'Named C':C}},'remaining':{'contest_votes':U,'pair_fraction':p,'a_pair_share':q,'other_mix':{'Named C':1}}}]}
CASES={
 'feasible-final-pair-denominator':obj(m=.01),
 'all-candidate-denominator':obj(C=100,U=200,p=.5,m=.01,den='all'),
 'negative-target-margin-valid':obj(m=-.1),
 'unknown-pair-fraction':obj(p=None),
 'unknown-pool':obj(U=None),
 'unknown-preference':obj(q=None),
 'no-remaining-pool':obj(U=0),
 'no-positive-pair-pool':obj(U=50,p=0,q=None),
 'negative-remaining':obj(U=-1),
 'impossible-trailing':obj(A=0,B=500,U=10),
 'secured-counted-lead':obj(A=500,B=0,U=10),
 'pair-Aplus1-still-loses-third':obj(A=10,B=10,C=200,U=100,q=.506,m=.01),
 'clipped-positive-preference':obj(A=0,B=0,U=100,q=.98),
 'clipped-negative-preference':obj(A=0,B=0,U=100,q=.02),
 'counted-units-held-fixed':{'target_margin':.01,'denominator':'pair','selected_key':'one','expected_keys':['one','two'],'units':[obj(A=10,B=30,U=40,q=.7,key='one')['units'][0],obj(A=100,B=80,U=20,q=.4,key='two')['units'][0]]},
}
CASES['clipped-positive-preference']['units'][0]['remaining']['share_shift']=.2
CASES['clipped-negative-preference']['units'][0]['remaining']['share_shift']=-.2
checks=[];results={}
def yes(name,value):
 assert value,name;checks.append({'test':name,'pass':True})
for name,x in CASES.items():
 (O/(name+'.input.json')).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
 try:y=live(x)
 except InputError as e:y={'error':str(e)}
 (O/(name+'.output.json')).write_text(json.dumps(y,indent=2,allow_nan=False)+'\n');results[name]=y
r=results['feasible-final-pair-denominator'];yes('target uses final pair200, threshold.61',abs(r['conditional_threshold']['raw_share']-.61)<1e-12)
r=results['all-candidate-denominator'];yes('finalall400,target4,threshold.62',r['final_all_candidate_denominator']==400 and abs(r['conditional_threshold']['raw_share']-.62)<1e-12)
yes('negative target margin finite and meaningful',abs(results['negative-target-margin-valid']['conditional_threshold']['raw_share']-.5)<1e-12)
yes('unknown pair participation remains unknown',results['unknown-pair-fraction']['projected_final'] is None)
yes('unknown remains unknown',results['unknown-pool']['projected_final'] is None and results['unknown-preference']['projected_final'] is None)
yes('no-pool explicit',results['no-remaining-pool']['conditional_threshold']['status']=='no-positive-pool')
yes('zero-pair with unknown irrelevant preference still computes',results['no-positive-pair-pool']['conditional_threshold']['status']=='no-positive-pool')
yes('negative pool rejected','error' in results['negative-remaining'])
yes('impossible explicit',results['impossible-trailing']['conditional_threshold']['status']=='impossible')
yes('secured explicit',results['secured-counted-lead']['conditional_threshold']['status']=='already-secured')
r=results['pair-Aplus1-still-loses-third'];yes('pair+1 target does not establish legal plurality',not r['projected_final']['A_unique_plurality'] and not r['projected_final']['pair_target_beats_largest_other'] and r['projected_final']['plurality_leaders']==['Named C'])
yes('positive clipping explicit',results['clipped-positive-preference']['units'][0]['clipped'] and results['clipped-positive-preference']['projected_final']['A']==100)
yes('negative clipping explicit',results['clipped-negative-preference']['units'][0]['clipped'] and results['clipped-negative-preference']['projected_final']['A']==0)
r=results['counted-units-held-fixed'];yes('all counted votes fixed across units',r['counted_fixed']['A']==110 and r['counted_fixed']['B']==110 and abs(r['selected_only_threshold']['raw_share']-.585)<1e-12)
# An all-state clipped shift differs from the unbounded shortcut and still hits the target.
r=state([{'key':'edge','pair':80,'share':.99},{'key':'other','pair':20,'share':.01}],.9);yes('bounded clipped uniform solve',r['clipped_units']>0 and abs(r['actual_net']-90)<1e-9 and r['bounded_share_shift']!=r['unbounded_share_shift'])
yes('historical no positive pool preserved',state([{'key':'zero','pair':0,'share':.5}])['status']=='no-positive-pool')
for value in [None,True,'0',float('nan'),float('inf'),-1.1,1.1]:
 x=obj();x['target_margin']=value
 try:live(x);raise AssertionError('target accepted '+str(value))
 except InputError:checks.append({'test':'reject invalid target '+repr(value),'pass':True})
for kind in ['missing','duplicate','empty','null','nonstr','duplicate-no-selected']:
 x=obj()
 if kind=='missing':x['expected_keys'].append('absent')
 elif kind.startswith('duplicate'):x['units'].append(copy.deepcopy(x['units'][0]));x['selected_key']=None
 elif kind=='empty':x['units'][0]['key']=' '
 elif kind=='null':x['units'][0]['key']=None
 else:x['units'][0]['key']=1
 try:live(x);raise AssertionError('invalid units accepted '+kind)
 except InputError:checks.append({'test':'reject units '+kind,'pass':True})
for value in [None,False,'100',float('nan'),float('inf'),-1]:
 if value is None:continue # null remaining is an intentional unknown
 x=obj();x['units'][0]['remaining']['contest_votes']=value
 try:live(x);raise AssertionError('pool accepted '+str(value))
 except InputError:checks.append({'test':'reject invalid pool '+repr(value),'pass':True})
# Public command errors must be safe, finite JSON, with failure exit; no traceback.
p=subprocess.run([sys.executable,str(Path(__file__).with_name('calculator.py'))],input='{"target_margin":NaN,"units":[]}',text=True,capture_output=True)
yes('CLI nonfinite JSON safe error',p.returncode==2 and 'error' in json.loads(p.stdout) and not p.stderr)
(D/'calculator-tests.json').write_text(json.dumps({'tests':len(checks),'passed':len(checks),'checks':checks,'saved_scenarios':list(CASES),'calibration':'arithmetic only, no probabilities'},indent=2)+'\n');print(len(checks))
if __name__=='__main__':pass

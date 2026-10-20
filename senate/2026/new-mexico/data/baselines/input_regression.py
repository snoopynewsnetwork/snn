#!/usr/bin/env python3
"""Actual subprocess CLI regressions, exact frozen coordinator fixtures, no source expansion."""
import base64,copy,gzip,hashlib,json,os,subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent;STATE=D.parents[1];H=D/'repair-history/pre-input-validation-v1';R=D/'repair-regressions';F=R/'fixtures'
sha=lambda b:hashlib.sha256(b).hexdigest()
def strict(b):return json.loads(b,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite_JSON_constant')))
def frozen(path):
    cap=json.loads((H/'freeze.json').read_text());r=next(r for r in cap['files']if r['original_path']==path);z=(STATE/r['stored_path']).read_bytes();assert sha(z)==r['stored_sha256'];b=gzip.decompress(z);assert sha(b)==r['raw_sha256'];return b
def main():
    F.mkdir(parents=True,exist_ok=True);cases=[]
    old=strict(frozen('data/coordinator-live-input-review/initial-finding.json'));params=strict(frozen('data/coordinator-live-input-review/county-parameter-finding.json'))
    for row in old['cases']:
        name='coordinator-'+row['name'];raw=frozen('data/coordinator-live-input-review/'+row['input_path']);p=F/(name+'.json');p.write_bytes(raw)
        cases.append({'name':name,'argv':['--live-json',str(p)],'expected':'invalid'if row['negative']else 'valid','fixture':p,'exact_prior_stdout':row['stdout']if not row['negative']else None})
    for row in params['cases']:cases.append({'name':'coordinator-'+row['name'],'argv':row['argv'],'expected':'invalid'})
    base=dict(counted_A=40,counted_B=50,counted_other={'C':5},remaining=100,pair_participation=.8,remaining_A_pair_share=.6,remaining_other_mix={'C':1})
    variants={
        'null-target':{'target_pair_margin':None},'text-target':{'target_pair_margin':'0'},'bool-false-target':{'target_pair_margin':False},'negative-infinite-target':{'target_pair_margin':-float('inf')},
        'null-count':{'counted_A':None},'text-count':{'counted_B':'50'},'negative-count':{'counted_A':-1},'bool-negative-pool':{'remaining':False},'text-pool':{'remaining':'100'},'negative-pool':{'remaining':-1},
        'unknown-does-not-hide-bool-target':{'remaining':None,'target_pair_margin':True},'unknown-does-not-hide-bad-mix':{'remaining_A_pair_share':None,'remaining_other_mix':{'C':float('inf')}},
        'null-mix-object':{'remaining_other_mix':None},'list-mix-object':{'remaining_other_mix':[1]},'text-mix-object':{'remaining_other_mix':'C'},'negative-mix':{'remaining_other_mix':{'C':-1}},'unnormalized-mix':{'remaining_other_mix':{'C':.6}},'oversized-mix':{'remaining_other_mix':{'C':1.2}},
        'null-mix-value':{'remaining_other_mix':{'C':None}},'empty-mix-key':{'remaining_other_mix':{'':1}},'reserved-mix-key':{'remaining_other_mix':{'A':1}},'reserved-counted-key':{'counted_other':{'B':5}},'blank-counted-key':{'counted_other':{' ':5}},
        'bool-counted-other':{'counted_other':{'C':True}},'text-counted-other':{'counted_other':{'C':'5'}},'null-counted-other-value':{'counted_other':{'C':None}},'negative-counted-other':{'counted_other':{'C':-5}},'infinite-counted-other':{'counted_other':{'C':float('inf')}},
        'nonfinite-participation':{'pair_participation':float('inf')},'negative-participation':{'pair_participation':-.1},'bool-preference':{'remaining_A_pair_share':True},'text-preference':{'remaining_A_pair_share':'.6'},'infinite-preference':{'remaining_A_pair_share':float('inf')},
        'extra-nonfinite-before-unknown':{'remaining':None,'metadata':{'x':float('nan')}},'derived-count-overflow':{'counted_A':1e308,'counted_B':1e308},'derived-other-overflow':{'counted_other':{'C':1e308,'D':1e308}},'derived-tiny-pool':{'remaining':5e-324,'pair_participation':.1},'unrepresentable-integer':{'counted_A':10**400},
    }
    for name,changes in variants.items():
        x=copy.deepcopy(base);x.update(changes);p=F/(name+'.json');p.write_text(json.dumps(x,allow_nan=True)+'\n');cases.append({'name':name,'argv':['--live-json',str(p)],'expected':'invalid','fixture':p})
    for name,raw in [('root-null','null'),('root-list','[]'),('root-bool','true'),('root-text','"request"'),('malformed-json','{'),('duplicate-candidate-key','{"counted_A":40,"counted_B":50,"counted_other":{"C":1,"C":2}}')]:
        p=F/(name+'.json');p.write_text(raw+'\n');cases.append({'name':name,'argv':['--live-json',str(p)],'expected':'invalid','fixture':p})
    for name,argv in [
        ('uniform-null-target',['--target-margin-pp','null']),('uniform-bool-target',['--target-margin-pp','true']),('uniform-negative-infinite',['--target-margin-pp=-inf']),('uniform-out-of-range',['--target-margin-pp','101']),
        ('selected-text-target',['--county','Bernalillo','--target-margin-pp','bad']),('selected-null-target',['--county','Bernalillo','--target-margin-pp','null']),('selected-bool-shift',['--county','Bernalillo','--others-shift-pp','true']),('selected-nan-shift',['--county','Bernalillo','--others-shift-pp','nan']),('selected-overrange-shift',['--county','Bernalillo','--others-shift-pp','101']),('selected-blank-county',['--county','']),('incomplete-argv',['--county']),('unknown-flag',['--bogus'])]:cases.append({'name':name,'argv':argv,'expected':'invalid'})
    # Exact old legitimate synthetic responses must survive unchanged in meaning.
    synthetics=strict(frozen('data/baselines/live-synthetic-scenarios.json'))
    for name,row in synthetics.items():
        if row['status'].startswith('invalid'):continue
        p=F/('positive-'+name+'.json');p.write_text(json.dumps(row['input'],allow_nan=False)+'\n');cases.append({'name':'positive-'+name,'argv':['--live-json',str(p)],'expected':'valid','fixture':p,'expected_object':row})
    for name,x in [('unknown-participation',dict(base,pair_participation=None)),('no-pool-unknown-preference',dict(base,remaining=0,remaining_A_pair_share=None,pair_participation=None)),('fully-zero',dict(base,counted_A=0,counted_B=0,counted_other={},remaining=0)),('two-named-opponents',dict(base,counted_other={'C':5,'D':3},remaining_other_mix={'C':.25,'D':.75}))]:
        p=F/('positive-'+name+'.json');p.write_text(json.dumps(x)+'\n');cases.append({'name':'positive-'+name,'argv':['--live-json',str(p)],'expected':'valid','fixture':p})
    for name,argv in [('valid-uniform',[]),('valid-uniform-cushion',['--target-margin-pp','1']),('valid-selected',['--county','Bernalillo']),('valid-selected-impossible',['--county','Catron','--others-shift-pp','-100']),('valid-selected-secured',['--county','Catron','--others-shift-pp','100']),('valid-selected-boundary',['--county','Bernalillo','--target-margin-pp','-100'])]:cases.append({'name':name,'argv':argv,'expected':'valid'})
    # Function surfaces execute in fresh Python subprocesses, separate from CLI fixture validation.
    functions=[
        ('uniform-bool-margin','uniform',[[{'volume':10,'share':.5}],True],'invalid'),('uniform-null-margin','uniform',[[{'volume':10,'share':.5}],None],'invalid'),('uniform-text-margin','uniform',[[{'volume':10,'share':.5}],'0'],'invalid'),
        ('uniform-infinite-margin','uniform',[[{'volume':10,'share':.5}],float('inf')],'invalid'),('uniform-nan-margin','uniform',[[{'volume':10,'share':.5}],float('nan')],'invalid'),('uniform-not-list','uniform',[{}],'invalid'),('uniform-null-unit','uniform',[[None]],'invalid'),('uniform-bool-volume','uniform',[[{'volume':True,'share':.5}]],'invalid'),('uniform-negative-volume','uniform',[[{'volume':-1,'share':.5}]],'invalid'),('uniform-text-volume','uniform',[[{'volume':'10','share':.5}]],'invalid'),('uniform-infinite-volume','uniform',[[{'volume':float('inf'),'share':.5}]],'invalid'),('uniform-bool-share','uniform',[[{'volume':10,'share':True}]],'invalid'),('uniform-unbounded-share','uniform',[[{'volume':10,'share':1.1}]],'invalid'),
        ('uniform-duplicate-key','uniform',[[{'key':'x','volume':1,'share':.5},{'key':'x','volume':2,'share':.5}]],'invalid'),('uniform-duplicate-county','uniform',[[{'county':'x','volume':1,'share':.5},{'county':'x','volume':2,'share':.5}]],'invalid'),('uniform-bool-id','uniform',[[{'id':True,'volume':1,'share':.5}]],'invalid'),('uniform-overflow','uniform',[[{'volume':1e308,'share':.5},{'volume':1e308,'share':.5}]],'invalid'),
        ('selected-bool-pool','selected',[True,0,0],'invalid'),('selected-negative-pool','selected',[-1,0,0],'invalid'),('selected-nonfinite-net','selected',[1,float('inf'),0],'invalid'),('selected-null-target','selected',[1,0,None],'invalid'),('selected-bool-target','selected',[1,0,True],'invalid'),('selected-unknown-bad-target','selected',[None,None,float('nan')],'invalid'),('selected-overflow','selected',[1e308,-1e308,1e308],'invalid'),
        ('uniform-unknown-volume','uniform',[[{'volume':None,'share':.5}]],'valid'),('uniform-unknown-preference','uniform',[[{'volume':10,'share':None}]],'valid'),('uniform-no-pool','uniform',[[]],'valid'),('uniform-impossible-internal','uniform',[[{'volume':10,'share':.5}],1.1],'valid'),('uniform-clipped','uniform',[[{'volume':10,'share':1},{'volume':90,'share':.4}],.9],'valid'),('selected-unknown','selected',[None,None,0],'valid'),('selected-no-pool','selected',[0,1,0],'valid'),('selected-impossible','selected',[1,-10,0],'valid'),('selected-secured','selected',[1,10,0],'valid')]
    wrapper="import sys,json;sys.path.insert(0,sys.argv[1]);import calculator;c=json.load(open(sys.argv[2]));print(json.dumps(getattr(calculator,c['function'])(*c['args']),allow_nan=False,indent=2))"
    for name,fn,args,expected in functions:
        p=F/(name+'.json');p.write_text(json.dumps({'function':fn,'args':args},allow_nan=True)+'\n');cases.append({'name':name,'function_fixture':p,'expected':expected,'fixture':p})
    out=[]
    for case in cases:
        cmd=[sys.executable,'-B','-c',wrapper,str(D),str(case['function_fixture'])]if 'function_fixture'in case else [sys.executable,'-B',str(D/'calculator.py'),*case['argv']]
        r=subprocess.run(cmd,capture_output=True,timeout=15,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});parsed=None;error=None
        try:parsed=strict(r.stdout)
        except (ValueError,UnicodeError)as e:error=type(e).__name__
        good=r.returncode==0 and r.stderr==b''and isinstance(parsed,dict)
        if good and case['expected']=='invalid':good=parsed.get('status','').startswith('invalid')and parsed.get('final')is None and isinstance(parsed.get('error'),dict)and 'input'not in parsed
        if good and case['expected']=='valid':good=not parsed.get('status','').startswith('invalid')
        if good and case.get('exact_prior_stdout')is not None:good=parsed==strict(case['exact_prior_stdout'])
        if good and 'expected_object'in case:good=parsed==case['expected_object']
        transcript={'name':case['name'],'expected':case['expected'],'argv':cmd[2:],'exit_code':r.returncode,'stdout':r.stdout.decode(),'stdout_sha256':sha(r.stdout),'stderr':r.stderr.decode(),'stderr_sha256':sha(r.stderr),'strict_JSON_error':error,'observed_status':parsed.get('status')if isinstance(parsed,dict)else None,'passed':good}
        if 'fixture'in case:transcript['fixture']={'path':str(case['fixture'].relative_to(STATE)),'bytes':case['fixture'].stat().st_size,'sha256':sha(case['fixture'].read_bytes())}
        out.append(transcript)
    failures=[r['name']for r in out if not r['passed']]
    result={'status':'pass'if not failures else 'fail','calculator_sha256':sha((D/'calculator.py').read_bytes()),'history_freeze_sha256':sha((H/'freeze.json').read_bytes()),'coordinator_initial_finding_sha256':sha(frozen('data/coordinator-live-input-review/initial-finding.json')),'coordinator_county_finding_sha256':sha(frozen('data/coordinator-live-input-review/county-parameter-finding.json')),'case_count':len(out),'coordinator_exact_cases':21,'negative_cases':sum(c['expected']=='invalid'for c in cases),'positive_cases':sum(c['expected']=='valid'for c in cases),'failures':failures,'cases':out,'scope':'Actual current subprocess outputs; prior coordinator and producer bytes preserved separately. No peer/future-final equality claim.'}
    (R/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n');print(json.dumps({k:result[k]for k in ['status','case_count','negative_cases','positive_cases','failures']}));assert not failures
if __name__=='__main__':main()

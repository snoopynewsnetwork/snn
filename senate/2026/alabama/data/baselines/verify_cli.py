#!/usr/bin/env python3
"""Actual process-level fixtures and independent hand/Fraction controls."""
import copy,gzip,json,math,pathlib,subprocess,sys
from fractions import Fraction
BASE=pathlib.Path(__file__).resolve().parent
def decode(t):
    def bad(x):raise AssertionError('nonfinite output '+x)
    return json.loads(t,parse_constant=bad)
CS=[{'id':'A','name':'Synthetic A','party':'D','scope':'named'},{'id':'B','name':'Synthetic B','party':'R','scope':'named'},{'id':'C','name':'Synthetic C','party':'LIB','scope':'named'}]
def live():return {'mode':'live','candidates':CS,'pair':['A','B'],'target_pair_margin':0,'scope':'synthetic; not Alabama returns','assumptions':'stated arithmetic inputs, not calibrated probabilities','units':[{'key':'u','counted':[40,60,10],'remaining':100,'pair_participation':.8,'a_share':.75,'other_allocation':[1]}]}
def close(a,b):assert a is not None and abs(a-b)<=max(1e-8,abs(b)*1e-10),(a,b)
def main():
    fixtures=[]
    def add(name,data,check=None,valid=True,raw=None):fixtures.append((name,data,check,valid,raw))
    def fixed(r):
        close(r['final_full_candidate_denominator'],210);close(r['final_pair_denominator'],180);close(r['all_remaining_required_a_share']['raw'],Fraction(5,8));assert [x['votes'] for x in r['counted_candidates_fixed']]==[40,60,10]
        for actual,expected in zip([x['votes'] for x in r['projected_candidates']],[100,80,30]):close(actual,expected)
    add('counted-fixed-final-denominator',live(),fixed)
    d=live();d['units'][0]['a_share']=None;add('unknown-positive-pool',d,lambda r: (r['common_shift']['status']=='unknown' and r['projected_candidates'] is None) or (_ for _ in ()).throw(AssertionError()))
    d=live();d['units'][0].update(remaining=0,a_share=None);add('no-pool-unknown-preference',d,lambda r:close(r['final_full_candidate_denominator'],110))
    for name,count,status,expected in [('negative-secured',[100,0,0],'secured',-4.5),('impossible',[0,100,0],'impossible',5.5)]:
        d=live();d['selected_unit']='u';d['units'][0].update(counted=count,remaining=10,pair_participation=1)
        def check(r,status=status,expected=expected):assert r['selected_only']['status']==status;close(r['selected_only']['raw'],expected)
        add(name,d,check)
    d=live();d['target_pair_margin']=.5;d['units'][0].update(counted=[0,60,0]);add('target-uses-final-pair-denominator',d,lambda r:close(r['all_remaining_required_a_share']['raw'],1.3125))
    d=live();d['selected_unit']='u';v=copy.deepcopy(d['units'][0]);v['key']='unknown_other';v['a_share']=None;d['units'].append(v);add('selected-only-unknown-other',d,lambda r:assert_status(r['selected_only'],'unknown'))
    d=live();d['units'][0].update(counted=[40,30,100],remaining=0,a_share=None);add('pair-leader-loses-full-field',d,lambda r:close(r['a_net_over_highest_other_named'],-60))
    d={'mode':'historical','candidates':CS[:2],'pair':['A','B'],'target_pair_margin':.8,'scope':'synthetic endpoint test','assumptions':'two units, fixed pair weights ten each','units':[{'key':'high','votes':[9,1]},{'key':'low','votes':[1,9]}]}
    def clipping(r):
        close(r['common_shift']['unbounded_share_shift'],.4);close(r['common_shift']['bounded_share_shift'],.7);assert r['common_shift']['clipping_applied'];close(sum(u['target_remaining_pair_net'] for u in r['units']),16)
    add('clipped-root-distinct-from-unbounded',d,clipping)
    d=copy.deepcopy(d);d['units']=[{'key':'zero','votes':[0,0]}];d['target_pair_margin']=0;add('zero-pair-undefined',d,lambda r: (r['units'][0]['a_share'] is None and r['common_shift']['status']=='no-positive-pool') or (_ for _ in ()).throw(AssertionError()))
    d=live();d['units'][0].update(counted=[100,0,0],remaining=10,pair_participation=1);add('clipped-common-impossible-final-target',d,lambda r:assert_status(r['common_shift'],'secured'))
    # Global unit identity failures must be rejected even in unknown/no-pool paths.
    for branch in ['unknown','no-pool']:
        for defect in ['duplicate','missing','blank','nonstring']:
            d=live();d['units'][0]['a_share']=None
            if branch=='no-pool':d['units'][0]['remaining']=0
            d['units'].append(copy.deepcopy(d['units'][0]))
            if defect=='missing':del d['units'][1]['key']
            elif defect=='blank':d['units'][1]['key']=' \t'
            elif defect=='nonstring':d['units'][1]['key']=3
            add(branch+'-'+defect+'-global-key',d,valid=False)
    for value,label in [(None,'null'),(True,'bool'),('0','text'),(1.01,'high'),(-1.01,'low')]:
        d=live();d['target_pair_margin']=value;add('invalid-target-'+label,d,valid=False)
    for token in ['NaN','Infinity','-Infinity']:
        raw=json.dumps(live()).replace('"target_pair_margin": 0','"target_pair_margin": '+token);add('invalid-target-'+token,None,valid=False,raw=raw)
    for field,bad in [('counted',[-1,0,0]),('counted',[True,0,0]),('remaining',-1),('remaining',None),('remaining','10'),('a_share',1.1),('a_share',False),('pair_participation',-.1),('pair_participation',True),('other_allocation',[.5]),('other_allocation',[True]),('other_allocation',[1,0])]:
        d=live();d['units'][0][field]=bad;add('invalid-'+field+'-'+str(len(fixtures)),d,valid=False)
    for field in ['counted','remaining','a_share','pair_participation','other_allocation']:
        d=live();d['units'][0][field]=[float('nan'),0,0] if field=='counted' else ([float('inf')] if field=='other_allocation' else float('inf'));add('nonfinite-'+field,None,valid=False,raw=json.dumps(d))
    for label,mut in [('candidate-collision',lambda d:d['candidates'].__setitem__(2,copy.deepcopy(d['candidates'][0]))),('selected-absent',lambda d:d.update(selected_unit='absent')),('unsupported-mode',lambda d:d.update(mode='probability')),('aggregate-overflow',lambda d:d['units'][0].update(counted=[1e308,1e308,0])),('unknown-late-invalid',lambda d:(d['units'][0].update(a_share=None),d['units'].append({'key':'late','counted':[0,0,0],'remaining':-2,'pair_participation':1,'a_share':None,'other_allocation':[0]})))]:
        d=copy.deepcopy(live());mut(d);add(label,d,valid=False)
    raw=json.dumps(live()).replace('"target_pair_margin": 0','"target_pair_margin": 0, "target_pair_margin": 0');add('duplicate-object-field',None,valid=False,raw=raw)
    # Source key whitespace is literal identity, not a normalization alias.
    d=live();d['selected_unit']=' u ';d['units'][0]['key']=' u ';add('literal-whitespace-key',d,lambda r: (r['selected_only']['key']==' u ') or (_ for _ in ()).throw(AssertionError()))
    results=[];folder=BASE/'scenarios/cli';folder.mkdir(exist_ok=True)
    for name,d,check,valid,raw in fixtures:
        text=raw if raw is not None else json.dumps(d,allow_nan=False)
        (folder/(name+'.input.txt')).write_text(text+'\n')
        p=subprocess.run([sys.executable,str(BASE/'calculate.py')],input=text,text=True,capture_output=True)
        (folder/(name+'.stdout.json')).write_text(p.stdout);(folder/(name+'.stderr.txt')).write_text(p.stderr)
        result={'fixture':name,'expected_valid':valid,'exit_code':p.returncode,'stderr_empty':not p.stderr,'checks_pass':False}
        try:
            r=decode(p.stdout);assert not p.stderr;assert p.returncode==(0 if valid else 2);assert r['status']==('ok' if valid else 'invalid-input')
            if check:check(r)
            result['checks_pass']=True
        except Exception as e:result['error']=repr(e)
        results.append(result)
    # Execute every saved real statewide scenario via the actual CLI as well.
    for p in sorted((BASE/'scenarios').glob('*.input.json.gz')):
        text=gzip.decompress(p.read_bytes()).decode();r=subprocess.run([sys.executable,str(BASE/'calculate.py')],input=text,text=True,capture_output=True);expected=gzip.decompress(pathlib.Path(str(p).replace('.input.','.result.')).read_bytes()).decode()
        result={'fixture':p.name,'exit_code':r.returncode,'stderr_empty':not r.stderr,'checks_pass':r.returncode==0 and not r.stderr and decode(r.stdout)==decode(expected)};results.append(result)
    output={'actual_cli_cases':len(results),'passed':sum(r['checks_pass'] for r in results),'cases':results,'controls':'hand calculations for fixed/final denominators, raw selected thresholds and analytic endpoint example; statewide independent piecewise proof is in validate.py'}
    (BASE/'cli-validation.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n');print(json.dumps(output,indent=2));return 0 if all(r['checks_pass'] for r in results) else 1
def assert_status(obj,status):assert obj['status']==status,(obj,status)
if __name__=='__main__':sys.exit(main())

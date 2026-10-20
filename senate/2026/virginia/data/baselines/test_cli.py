"""Meaningful actual CLI fixtures; expected results from independently stated arithmetic."""
import copy,json,subprocess,sys
from pathlib import Path
from extract import ROOT,dump
def unit(key='u',A=40,B=60,O=10,remaining=100,p=.8,q=.75):return dict(key=key,counted={'Candidate A':A,'Candidate B':B,'Other':O},counted_all_candidate_total=A+B+O,remaining=remaining,pair_participation=p,share=q,other_allocations={'Other':1})
def live():return dict(mode='live',pair=['Candidate A','Candidate B'],other_candidates=['Other'],candidate_universe='full',unallocated_generic=False,assumptions='Synthetic arithmetic fixture; counted fixed; remaining is uncounted candidate-vote pool, not ballots or a probability.',target_pair_margin=0,units=[unit()])
def main():
    fixtures=[]
    def add(n,d,expect):fixtures.append((n,json.dumps(d,allow_nan=False),expect))
    d=live();add('counted-fixed-final-denominator',d,{'final_all_candidate_denominator':210,'final_pair_denominator':180,'projected_candidates':{'Candidate A':100,'Candidate B':80,'Other':30},'required':.625})
    d=live();d['target_pair_margin']=.01;add('final-denominator-Aplus1',d,{'required':.63625,'target_pair_net':1.8})
    d=live();d['units'][0]['share']=None;add('unknown-positive-pool',d,{'uniform_status':'unknown-preference'})
    d=live();d['units'][0]=unit(remaining=0,q=None);add('no-positive-pool',d,{'uniform_status':'no-positive-pool'})
    d=live();d['units'][0]=unit(A=100,B=0,O=0,remaining=10,p=1,q=.5);add('secured-negative-raw-share',d,{'required':-4.5,'requirement_status':'secured'})
    d=live();d['units'][0]=unit(A=0,B=100,O=0,remaining=10,p=1,q=.5);add('impossible-raw-share',d,{'required':5.5,'requirement_status':'impossible'})
    d=live();d['units']=[unit(),unit(key='unknown',q=None)];d['selected_unit']='u';add('selected-only-unknown-other',d,{'selected_status':'unknown-other-preference'})
    d=live();d['units']=[unit(q=None),unit(key='fixed',q=.75)];d['selected_unit']='u';add('selected-own-preference-unknown',d,{'selected_status':'feasible'})
    d=live();d['units'][0]=unit(A=30,B=20,O=100,remaining=0,q=None);add('pair-leader-loses-full-field',d,{'leaders':['Other'],'pair_A_leads':True})
    d=live();d['candidate_universe']='supplied';add('supplied-universe-only',d,{'plurality_status':'supplied-universe-only'})
    d=live();d['units'][0]=unit(A=0,B=0,O=10,remaining=5,p=0,q=None);add('zero-pair-undefined',d,{'uniform_status':'no-positive-pair-denominator','baseline_pair_margin':None})
    d=dict(mode='historical',pair=['A','B'],other_candidates=[],candidate_universe='supplied',unallocated_generic=False,assumptions='Synthetic unequal-volume clipping example',target_pair_margin=0,units=[dict(key='large',volume=90,pair_participation=1,share=.99,other_allocations={}),dict(key='small',volume=10,pair_participation=1,share=.1,other_allocations={})]);add('clipping-differs-from-unbounded',d,{'clipped':['small'],'bounded_root':5/9-.99,'unbounded_root':-.401})
    for target in (-1,1):
        d=live();d['units'][0]=unit(A=0,B=0,O=0,remaining=10,p=1,q=.3);d['target_pair_margin']=target;add('target-endpoint-'+str(target),d,{'target_pair_net':10*target})
    d=live();d['units'][0]['key']=' u ';d['selected_unit']=' u ';add('literal-key-whitespace-retained',d,{'selected_status':'feasible'})
    for val in [None,True,'0',-1.01,1.01]:
        d=live();d['target_pair_margin']=val;add('invalid-target-'+repr(val),d,{'invalid':True})
    for field,val in [('remaining',-1),('pair_participation',1.01),('share',-.01)]:
        d=live();d['units'][0][field]=val;add('invalid-'+field,d,{'invalid':True})
    for val in [True,None,'4',-1]:
        d=live();d['units'][0]['counted']['Candidate A']=val;add('invalid-count-'+repr(val),d,{'invalid':True})
    d=live();d['units'][0]['counted_all_candidate_total']=50;add('counted-total-smaller-than-pair',d,{'invalid':True})
    d=live();d['units'][0]['other_allocations']={'Other':.9};add('unbalanced-other-allocations',d,{'invalid':True})
    d=live();d['other_candidates']=['Candidate A'];add('candidate-identity-collision',d,{'invalid':True})
    d=live();d['selected_unit']='absent';add('missing-selected-key',d,{'invalid':True})
    d=live();d['mode']='runoff';add('unsupported-mode',d,{'invalid':True})
    for branch in ['unknown','no-pool']:
        for bad in ['duplicate','missing','blank','nonstring']:
            d=live();u=unit(q=None,remaining=100 if branch=='unknown' else 0);v=unit(key='other',q=None,remaining=0)
            if bad=='duplicate':v['key']='u'
            elif bad=='missing':v.pop('key')
            elif bad=='blank':v['key']=' \t'
            else:v['key']=42
            d['units']=[u,v];add('global-key-'+branch+'-'+bad,d,{'invalid':True})
    for token in ['NaN','Infinity','-Infinity','1e999']:
        for field in ['target_pair_margin','remaining','share']:
            d=live();raw=json.dumps(d);old='"'+field+'": '+('0' if field=='target_pair_margin' else '100' if field=='remaining' else '0.75');raw=raw.replace(old,'"'+field+'": '+token,1);fixtures.append(('nonfinite-'+field+'-'+token,raw,{'invalid':True}))
    for token in ['NaN','Infinity','-Infinity','1e999']:
        d=live();raw=json.dumps(d).replace('"Candidate A": 40','"Candidate A": '+token,1);fixtures.append(('nonfinite-count-'+token,raw,{'invalid':True}))
        d=live();raw=json.dumps(d).replace('"other_allocations": {"Other": 1}','"other_allocations": {"Other": '+token+'}',1);fixtures.append(('nonfinite-allocation-'+token,raw,{'invalid':True}))
    d=live();d['units'][0]['share']=None;d['target_pair_margin']=None;add('invalid-target-before-unknown-return',d,{'invalid':True})
    d=live();d['units'][0]['remaining']=0;d['units'][0]['pair_participation']=None;add('invalid-participation-before-no-pool-return',d,{'invalid':True})
    d=live();raw=json.dumps(d).replace('"target_pair_margin": 0','"target_pair_margin": 0, "target_pair_margin": 0.01');fixtures.append(('duplicate-json-field',raw,{'invalid':True}))
    d=live();d['units']=[unit(key='one',A=1e308,B=0,O=0,remaining=0),unit(key='two',A=1e308,B=0,O=0,remaining=0)];add('aggregate-overflow',d,{'invalid':True})
    results=[]
    def near(a,b):
        if isinstance(b,dict):return isinstance(a,dict) and set(a)==set(b) and all(near(a[k],v) for k,v in b.items())
        if isinstance(b,list):return isinstance(a,list) and len(a)==len(b) and all(near(x,y) for x,y in zip(a,b))
        return a==b if a is None or b is None or isinstance(b,(str,bool)) else abs(a-b)<1e-9
    for name,raw,expected in fixtures:
        p=subprocess.run([sys.executable,'-B',str(ROOT/'calculator.py')],input=raw,text=True,capture_output=True);out=json.loads(p.stdout,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)));assert not p.stderr,(name,p.stderr)
        errors=[]
        if expected.get('invalid'):
            if p.returncode!=2 or out.get('status')!='invalid-input':errors.append('expected strict invalid-input/exit2')
        else:
            if p.returncode!=0:errors.append('expected exit0')
            for k,v in expected.items():
                actual=out['aggregate_remaining_requirement']['raw_required_share'] if k=='required' else out['aggregate_remaining_requirement']['status'] if k=='requirement_status' else out['uniform']['status'] if k=='uniform_status' else out['selected_unit_requirement']['status'] if k=='selected_status' else out['plurality']['leaders'] if k=='leaders' else out['plurality']['pair_A_leads'] if k=='pair_A_leads' else out['plurality']['status'] if k=='plurality_status' else out['uniform']['endpoint_clipped_units'] if k=='clipped' else out['uniform']['bounded_share_shift'] if k=='bounded_root' else out['uniform']['unbounded_share_shift'] if k=='unbounded_root' else out[k]
                if not near(actual,v):errors.append(dict(field=k,expected=v,actual=actual))
        dest=ROOT/'scenarios/fixtures';dest.mkdir(parents=True,exist_ok=True);(dest/(name+'.input.json')).write_text(raw+'\n');(dest/(name+'.stdout.json')).write_text(p.stdout);(dest/(name+'.execution.json')).write_text(json.dumps({'exit':p.returncode,'stderr':p.stderr,'expected':expected,'errors':errors},indent=2)+'\n');results.append({'fixture':name,'pass':not errors,'errors':errors})
    # Actual all-native positive CLI: full data input / strict JSON result retained.
    p=subprocess.run([sys.executable,'-B',str(ROOT/'calculator.py'),str(ROOT/'scenarios/actual-2024-native-Aplus1.input.json')],capture_output=True,text=True);assert p.returncode==0 and not p.stderr
    (ROOT/'scenarios/actual-2024-native-Aplus1.stdout.json').write_text(p.stdout);o=json.loads(p.stdout);assert abs(o['uniform']['bounded_net']-.01*4437026)<1e-6
    dump('cli-validation.json',{'actual_cli_runs':len(results)+1,'fixtures':results,'all_passed':all(r['pass'] for r in results),'strict_json_and_no_stderr':True,'actual_full_native_residual':o['uniform']['residual_net']});print('fixtures',len(results),'failed',sum(not r['pass'] for r in results));assert all(r['pass'] for r in results)
if __name__=='__main__':main()

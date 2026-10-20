"""Actual coordinator failure replay plus malformed-type/identity regression cases.
Fixture inputs intentionally include non-standard NaN/Infinity JSON tokens to
exercise Python's accepted input boundary; all result files are strict JSON.
"""
import copy,gzip,json,subprocess,sys
from source_io import ROOT,STATE,dump,sha
def main():
    evidence=STATE/'data/coordinator-live-input-review-v1';dest=ROOT/'calculator-review-evidence';dest.mkdir(exist_ok=True);manifest=[]
    # Exact immutable original evidence, including the failing script and7actual inputs.
    originals=sorted(evidence.iterdir())if not(dest/'manifest.json').exists()else[evidence/(__import__('pathlib').Path(x['capture']).name)for x in json.loads((dest/'manifest.json').read_text())]
    for p in originals:
        if not p.is_file()and not(dest/p.name).is_file():continue
        q=dest/p.name;b=q.read_bytes()if q.exists()else p.read_bytes()
        if not q.exists():q.write_bytes(b)
        manifest.append(dict(original=str(p.relative_to(STATE)),capture=str(q.relative_to(ROOT)),bytes=len(b),sha256=sha(b)))
    dump(dest/'manifest.json',manifest)
    fixture=ROOT/'negative-fixtures';fixture.mkdir(exist_ok=True);cases=[]
    for x in json.loads((dest/'finding.json').read_text())['cases']:
        cases.append((x['case'],json.loads((dest/(x['case']+'.json')).read_text()),'duplicate_remaining_unit_key'if x['case']=='duplicate_pool_unit'else'invalid_selected_target_pair_margin'))
    base={'A':'A','B':'B','counted':{'A':100,'B':120,'C':5},'remaining':[{'unit':'u','votes':50,'pair_participation':.8,'A_pair_share':.6,'other_shares':{'C':1}}]}
    for name,field,val,expected in [('votes-text','votes','50','invalid_remaining_votes_type'),('votes-bool','votes',True,'invalid_remaining_votes_type'),('votes-list','votes',[],'invalid_remaining_votes_type'),('votes-nan','votes',float('nan'),'invalid_remaining_votes_type'),('votes-infinity','votes',float('inf'),'invalid_remaining_votes_type'),('share-text','A_pair_share','0.6','invalid_remaining_share_type'),('share-bool','A_pair_share',False,'invalid_remaining_share_type'),('share-object','A_pair_share',{},'invalid_remaining_share_type'),('share-nan','A_pair_share',float('nan'),'invalid_remaining_share_type'),('participation-text','pair_participation','.8','invalid_pair_participation'),('participation-bool','pair_participation',True,'invalid_pair_participation'),('participation-infinity','pair_participation',float('inf'),'invalid_pair_participation'),('participation-over-one','pair_participation',1.1,'invalid_pair_participation'),('empty-unit','unit','','invalid_remaining_unit_key'),('blank-unit','unit','  ','invalid_remaining_unit_key'),('unit-object','unit',{},'invalid_remaining_unit_key'),('other-string','other_shares','C','invalid_other_share_allocation'),('other-invalid-value','other_shares',{'C':'1'},'invalid_other_share_allocation'),('other-nan','other_shares',{'C':float('nan')},'invalid_other_share_allocation')]:
        c=copy.deepcopy(base);c['remaining'][0][field]=val;cases.append((name,c,expected))
    for name,val in [('selected-target-too-small',-1.1),('selected-target-bool',True),('selected-target-list',[]),('selected-target-object',{})]:
        c=copy.deepcopy(base);c['selected_target_pair_margin']=val;cases.append((name,c,'invalid_selected_target_pair_margin'))
    c=copy.deepcopy(base);c['remaining']*=2;cases.append(('duplicate-without-selected',c,'duplicate_remaining_unit_key'))
    c=copy.deepcopy(base);c['remaining'][0].pop('unit');cases.append(('missing-unit-key',c,'invalid_remaining_unit_key'))
    c=copy.deepcopy(base);c['remaining'][0]['votes']=0;c['remaining'][0]['A_pair_share']='invalid-even-when-zero';cases.append(('zero-pool-invalid-share-type',c,'invalid_remaining_share_type'))
    c=copy.deepcopy(base);c['counted']['A']=True;cases.append(('boolean-counted-votes',c,'invalid_counted_votes'))
    c=copy.deepcopy(base);c['counted']=[100,120];cases.append(('counted-array',c,'invalid_counted_object'))
    c=copy.deepcopy(base);c['remaining']={};cases.append(('remaining-object',c,'invalid_remaining_pool_list'))
    c=copy.deepcopy(base);c['remaining']=[None];cases.append(('null-pool-object',c,'invalid_remaining_pool_list'))
    cases.append(('null-case-object',None,'invalid_case_object'))
    outputs=[]
    for name,c,expected in cases:
        p=fixture/(name+'.json');p.write_text(json.dumps(c,indent=2,allow_nan=True)+'\n')
        r=subprocess.run([sys.executable,str(ROOT/'calculator.py'),str(p)],capture_output=True,text=True)
        result=json.loads(r.stdout);assert r.returncode==0 and not r.stderr and result['status']==expected,(name,r.returncode,r.stdout,r.stderr,expected)
        outputs.append(dict(case=name,input_path=str(p.relative_to(ROOT)),expected_status=expected,actual_exit_code=r.returncode,stdout_json=result,stderr=r.stderr,input_bytes=p.stat().st_size,input_sha256=sha(p.read_bytes())))
    dump(ROOT/'negative-fixture-results.json',dict(status='pass',cases=len(outputs),results=outputs,qualification='Arithmetic input validation; intentional invalid input tokens are fixtures, not accepted source observations or probabilities.'))
    print(json.dumps({'status':'pass','negative_CLI_cases':len(outputs),'actual_coordinator_cases':7}))
if __name__=='__main__':main()

"""Real CLI fixtures, including invalid strict-JSON contracts; independent expected checks."""
import copy,json,math,subprocess,sys
from common import *
def main():
    d=BASE/'scenarios/fixtures';d.mkdir(exist_ok=True)
    standard={'mode':'live','pair':{'A':'Synthetic A','B':'Synthetic B'},'candidate_universe_complete':True,
        'target_margin':0,'is_synthetic_arithmetic':True,'selected_unit':'north','units':[
            {'key':'north','counted':{'A':80,'B':120,'others':{'Synthetic C':10}},'remaining':100,'pair_participation':.8,'a_share':.7,'other_shares':{'Synthetic C':1}},
            {'key':'south','counted':{'A':20,'B':10,'others':{'Synthetic C':5}},'remaining':50,'pair_participation':.6,'a_share':.4,'other_shares':{'Synthetic C':1}}]}
    examples={}
    def add(name,data,code,expect):examples[name]=(data,code,expect)
    add('known-final-denominator',standard,0,{'final_all_candidate_denominator':395.0,'final_pair_denominator':340.0,'forecast_A':168.0,'forecast_B':172.0})
    unknown=copy.deepcopy(standard);unknown['units'][0]['a_share']=None
    add('unknown-preference',unknown,0,{'status':'unknown_preference','forecast_A':None,'final_all_candidate_denominator':395.0})
    no=copy.deepcopy(standard);no.pop('selected_unit');no['units']=no['units'][:1];no['units'][0].update(remaining=0,a_share=None)
    add('no-pool-counted-fixed',no,0,{'status':'no_positive_pool','forecast_A':80.0,'forecast_B':120.0,'final_all_candidate_denominator':210.0})
    for name,A,B in [('secured',1000,0),('impossible',0,1000)]:
        data=copy.deepcopy(standard);data['units']=data['units'][:1];data['units'][0].update(counted={'A':A,'B':B,'others':{}},remaining=10,pair_participation=1,a_share=.5,other_shares={})
        add(name,data,0,{'selected_only.status':name,'pooled_tie_or_margin_requirement.status':name})
    third=copy.deepcopy(no);third['units'][0]['counted']={'A':20,'B':10,'others':{'Synthetic C':100}}
    add('pair-leader-loses-full-field',third,0,{'fullfield.full_field_result':'A_not_strict_plurality','forecast_pair_margin':1/3})
    nonclosed=copy.deepcopy(no);nonclosed['candidate_universe_complete']=False
    add('supplied-universe-only',nonclosed,0,{'fullfield.full_field_result':'unknown_full_field'})
    onlyother=copy.deepcopy(no);onlyother['units'][0].update(remaining=50,pair_participation=0,a_share=None,other_shares={'Synthetic C':1})
    add('no-remaining-pair-other-pool',onlyother,0,{'final_all_candidate_denominator':260.0,'final_pair_denominator':200.0,'status':'no_positive_pool'})
    clipcase={'mode':'historical','pair':{'A':'Synthetic A','B':'Synthetic B'},'target_margin':0,'candidate_universe_complete':True,
        'units':[{'key':'zeroA','pair_volume':1,'all_volume':1,'a_share':0,'others':{}},
                 {'key':'mixed','pair_volume':9,'all_volume':9,'a_share':.8,'others':{}}]}
    add('bounded-clipping-root',clipcase,0,{'uniform_share_shift':-0.24444444444444446,'final_net_votes':0.0})
    zero={'mode':'historical','pair':{'A':'Synthetic A','B':'Synthetic B'},'target_margin':.01,'units':[
        {'key':'onlyC','pair_volume':0,'all_volume':10,'a_share':None,'others':{'Synthetic C':10}}]}
    add('zero-pair-preference-undefined',zero,0,{'status':'no_positive_pool','uniform_share_shift':None,'fullfield.supplied_plurality_leaders':['Synthetic C']})
    for value,name in [(True,'bool'),(None,'null'),('0','text'),(-1.01,'negative-range'),(1.01,'positive-range')]:
        data=copy.deepcopy(unknown);data['target_margin']=value;add('reject-target-'+name,data,2,{'status':'invalid_input'})
    for name,value in [('negative',-1),('bool',True),('text','10'),('null',None)]:
        data=copy.deepcopy(unknown);data['units'][1]['remaining']=value;add('reject-remaining-'+name,data,2,{'status':'invalid_input'})
    for key,name in [('', 'empty'),(42,'nonstring')]:
        data=copy.deepcopy(no);data['units'][0]['key']=key;add('reject-key-'+name+'-no-pool',data,2,{'status':'invalid_input'})
    data=copy.deepcopy(unknown);data.pop('selected_unit');data['units'][1]['key']='north';add('reject-global-duplicate-key',data,2,{'status':'invalid_input'})
    data=copy.deepcopy(standard);data['units'][0]['other_shares']={'Synthetic C':.5};add('reject-unbalanced-other-allocation',data,2,{'status':'invalid_input'})
    data=copy.deepcopy(clipcase);data['units'][0]['all_volume']=0;add('reject-final-denominator-balance',data,2,{'status':'invalid_input'})
    data=copy.deepcopy(unknown);data['units']={};add('reject-container',data,2,{'status':'invalid_input'})
    data=copy.deepcopy(no);data['units'][0]['counted']['A']=True;add('reject-counted-bool',data,2,{'status':'invalid_input'})
    results=[]
    for name,(data,code,expected) in examples.items():
        path=d/(name+'.json');path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
        r=subprocess.run([sys.executable,'-B',str(BASE/'scripts/calculate.py'),str(path)],capture_output=True,text=True)
        output=json.loads(r.stdout);ok=r.returncode==code
        for k,v in expected.items():
            x=output
            for part in k.split('.'):x=x[part]
            ok=ok and (math.isclose(x,v,abs_tol=1e-8,rel_tol=1e-10) if type(v) in [int,float] else x==v)
        (d/(name+'.result.json')).write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
        results.append({'fixture':name,'returncode':r.returncode,'expected_returncode':code,'passed':ok,'expected':expected})
    # Deliberately invalid numeric tokens are retained as text evidence, never as a .json artifact.
    for name,token in [('NaN','NaN'),('Infinity','Infinity'),('negative-Infinity','-Infinity')]:
        path=d/('reject-'+name+'.invalid-json.txt');path.write_text('{"mode":"live","target_margin":'+token+'}\n')
        r=subprocess.run([sys.executable,'-B',str(BASE/'scripts/calculate.py'),str(path)],capture_output=True,text=True)
        output=json.loads(r.stdout);(d/('reject-'+name+'.result.json')).write_text(json.dumps(output,indent=2)+'\n')
        results.append({'fixture':'reject-'+name,'returncode':r.returncode,'passed':r.returncode==2 and output['status']=='invalid_input'})
    # Ordinary valid JSON duplicate property is invalid to this CLI contract.
    path=d/'duplicate-property.invalid-json.txt';path.write_text('{"mode":"live","mode":"historical"}\n')
    r=subprocess.run([sys.executable,'-B',str(BASE/'scripts/calculate.py'),str(path)],capture_output=True,text=True)
    output=json.loads(r.stdout);(d/'duplicate-property.result.json').write_text(json.dumps(output,indent=2)+'\n')
    results.append({'fixture':'duplicate-property','returncode':r.returncode,'passed':r.returncode==2 and output['status']=='invalid_input'})
    write_json('qa/cli-fixtures.json',{'calibrated_probability':None,'synthetic':True,'tests':results,'all_passed':all(x['passed'] for x in results)})
    print('CLI fixtures',len(results),'passed',sum(x['passed'] for x in results))
    if not all(x['passed'] for x in results):raise SystemExit(1)
if __name__=='__main__':main()

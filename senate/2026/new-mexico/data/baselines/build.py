#!/usr/bin/env python3
"""All counties; all original native rows. No suppressed-value reconstruction."""
import csv,gzip,hashlib,json,math
from pathlib import Path
from calculator import uniform,selected,clip,live
D=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def csvout(p,rows):
    with p.open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def order(rows,field):
    rs=sorted(rows,key=lambda r:(-r[field],r['county'],r.get('label',''),r.get('source_row',0)));T=sum(r[field]for r in rs);acc=0;cross=None;out=[]
    for i,r in enumerate(rs,1):
        before=acc;acc+=r[field]
        if cross is None and 5*acc>=4*T:cross=i
        out.append({**r,'rank':i,'weight':r[field]/T if T else None,'cumulative':acc,'cumulative_share':acc/T if T else None})
    return {'denominator':T,'field':field,'ordered':out,'minimum80':cross,'minimum80_before':sum(r[field]for r in rs[:cross-1])if cross else None,'minimum80_at':sum(r[field]for r in rs[:cross])if cross else None,'top15_total':sum(r[field]for r in rs[:15]),'top15_share':sum(r[field]for r in rs[:15])/T if T else None}
def main():
    E=load(D/'original-extract.json');fips={r['cells'][6]['text']:r['cells'][2]['text']for r in load(D/'county-fips-source-rows.json')}
    fips['Dona Ana']=fips['Doña Ana'] if 'Doña Ana'in fips else fips['Dona Ana']
    bases=[];long=[];index={};state=[];native=[];priorities={};scenarios=[];contrib=[];native_targets=[];native_states=[]
    for k,v in E.items():
        cr=[r for r in v['rows']if r['scope']=='County'];index[k]={r['label_literal']:r for r in cr};st=v['rows'][0];nums=[c['value']for c in st['cells'][2:-2]];T=sum(nums[:2]);V=sum(nums)
        state.append({'contest':k,'A_label':v['headers'][2],'B_label':v['headers'][3],'A':nums[0],'B':nums[1],'other':sum(nums[2:]),'all_candidate_votes':V,'pair_votes':T,'A_pair_share':nums[0]/T,'pair_margin_pp':100*(nums[0]-nums[1])/T,'all_candidate_margin_pp':100*(nums[0]-nums[1])/V,'uniform_unbounded_tie_share_pp':100*(nums[1]-nums[0])/(2*T),'uniform_unbounded_Aplus1_share_pp':100*(nums[1]-nums[0])/(2*T)+.5})
        for r in v['rows']:
            vals=[c['value']for c in r['cells'][2:-2]];A,B=vals[:2];pair=None if A is None or B is None else A+B;total=None if any(x is None for x in vals)else sum(vals);known=pair is not None and pair>0
            for j,cell in enumerate(r['cells'][2:],2):long.append({'contest':k,'scope':r['scope'],'county':r['county_literal'],'native_label':r['label_literal'],'administrative':r['administrative'],'source_row':r['source_row'],'source_column':j+1,'field_label':cell['header'],'party_literal':cell['party_literal'],'literal':cell['literal'],'value':cell['value'],'masked':cell['masked'],'source_id':v['source_id']})
            row={'contest':k,'county':r['county_literal']if r['scope']=='Precinct'else r['label_literal'],'fips':fips.get(r['county_literal']if r['scope']=='Precinct'else r['label_literal']),
                'source_row':r['source_row'],'A_label':v['headers'][2],'A_party':v['parties'][2],'B_label':v['headers'][3],'B_party':v['parties'][3],'A':A,'B':B,'other':None if any(x is None for x in vals[2:])else sum(vals[2:]),
                'all_candidate_votes':total,'printed_total_votes':r['cells'][-2]['value'],'printed_total_ballots':r['cells'][-1]['value'],'pair_votes':pair,'pair_participation':pair/total if total else None,
                'A_pair_share':A/pair if known else None,'pair_margin_pp':100*(A-B)/pair if known else None,'all_candidate_margin_pp':100*(A-B)/total if known and total else None,
                'pair_weight_state':pair/T if pair is not None else None,'all_candidate_weight_state':total/V if total is not None else None,'net_A_minus_B':A-B if pair is not None else None,'gain_net_per_A_share_pp':.02*pair if pair is not None else None,
                'historical_pair_winner':('tie'if A==B else (v['headers'][2]if A>B else v['headers'][3]))if pair is not None else None,
                'pair_closeness_band':('<=5pp'if abs(100*(A-B)/pair)<=5 else ('>5to10pp'if abs(100*(A-B)/pair)<=10 else '>10pp'))if known else None,
                'source_id':v['source_id'],'status':'official historical database; county values independently checked original canvass; native privacy limits'}
            if r['scope']=='County':bases.append(row)
            if r['scope']=='Precinct':native.append({**row,'label':r['label_literal'],'administrative':r['administrative'],'native_id':None,'raw_fields_json':json.dumps(r['raw_row'],ensure_ascii=False)})
        nr=[r for r in native if r['contest']==k];knownrows=[r for r in nr if r['pair_votes']is not None and r['pair_votes']>0]
        uu=[{'volume':r['pair_votes'],'share':r['A_pair_share']}for r in knownrows]
        for g in [0.,.01]:
            sol=uniform(uu,g);native_states.append({'contest':k,'universe':'directly printed positive A+B native rows only, including administrative rows; not whole-state native certified electorate','target':g,**sol,'whole_state_native_solution':None,'unknown_pair_rows':sum(r['pair_votes']is None for r in nr),'zero_pair_rows':sum(r['pair_votes']==0 for r in nr)})
            for r in nr:
                known=r['pair_votes']is not None and r['pair_votes']>0;share=clip(r['A_pair_share']+sol['shift'])if known else None
                se=selected(r['pair_votes'],nums[0]-nums[1]-r['net_A_minus_B'] if r['net_A_minus_B']is not None else None,g*T)
                native_targets.append({'contest':k,'county':r['county'],'label':r['label'],'source_row':r['source_row'],'administrative':r['administrative'],'target_pair_margin_pp':g*100,'historical_pair_pool':r['pair_votes'],'observed_universe_pair_weight':r['pair_votes']/sol['volume']if r['pair_votes']is not None else None,'observed_universe_target_share':share,'observed_universe_target_net':r['pair_votes']*(2*share-1)if known else None,'statewide_all_native_uniform_target_share':None,'fullstate_selected_only_unbounded_share':se['required_share_unbounded'],'fullstate_selected_only_feasible_share':se['feasible_share'],'selected_status':se['status'],'others_assumption':'all other source contexts collectively retain published statewide historical A/B net after removing only this directly observed row; no protected allocation','gain_net_per_A_share_pp':r['gain_net_per_A_share_pp']})
        pri_county=order([{'county':r['county'],'all_candidate_votes':r['all_candidate_votes'],'source_row':r['source_row']}for r in bases if r['contest']==k],'all_candidate_votes')
        # All-candidate masks disqualify row from observed full-candidate order; never use printed totals as substitute.
        observed=[{'county':r['county'],'label':r['label'],'source_row':r['source_row'],'administrative':r['administrative'],'all_candidate_votes':r['all_candidate_votes']}for r in nr if r['all_candidate_votes']is not None]
        priorities[k]={'county_sensitivity':pri_county,'observed_complete_candidate_rows_only':order(observed,'all_candidate_votes'),'certified_native_order':None,'certified_native_top15':None,'certified_native_minimum80':None,'canonical_dispatch_keys':[],'complete_source_native_row_count':len(nr),'excluded_unknown_full_candidate_rows':len(nr)-len(observed)}
    csvout(D.parent/'county-baselines.csv',bases);csvout(D/'candidate-fields.csv',long);csvout(D/'native-baselines.csv',native);csvout(D/'native-targets.csv',native_targets);save(D/'native-state-scenarios.json',native_states);save(D/'priority-contract.json',priorities);csvout(D/'state-baselines.csv',state)
    volume_anchors={'low-2022-governor':'2022-governor','base-2024-senate':'2024-senate','high-2024-president':'2024-president','context-2020-same-seat':'2020-senate'}
    settings={'volume_definition':'Each county actual all-candidate valid votes from named historical contest; no actual-ballot conversion','volume_anchors':volume_anchors,'preference_anchors':list(E),'pair_participation':'Each preference anchor county (A+B)/all named candidate votes, held fixed when changing volume mix','other_allocation':'Each non-A/B candidate retains their own anchor county share of all-candidate votes; no transfer/lower preference inference','targets_pair_margin':[0,.01],'other_county_shift_for_selected_only':0,'native_model':'only directly printed positive A+B within each contest; no cross-year/native crosswalk; all-native whole-state uniform solution unavailable','clipping':'clip each A pair share to [0,1] then solve uniform bounded shift by bisection','historical_not_forecast':True}
    save(D/'settings.json',settings)
    for anchor,v in E.items():
        for mix,volume_contest in volume_anchors.items():
            units=[];other_fields={};totalV=0
            for c,r in index[anchor].items():
                vals=[x['value']for x in r['cells'][2:-2]];V=sum(vals);pair=sum(vals[:2]);vol=sum(x['value']for x in index[volume_contest][c]['cells'][2:-2]);totalV+=vol
                u={'county':c,'volume':vol*pair/V,'share':vals[0]/pair,'all_candidate_volume':vol,'pair_participation':pair/V};units.append(u)
                for j,votes in enumerate(vals[2:],4):other_fields[v['headers'][j]]=other_fields.get(v['headers'][j],0)+vol*votes/V
            T=sum(u['volume']for u in units);M=sum(u['volume']*(2*u['share']-1)for u in units)
            for g in [0,.01]:
                sol=uniform(units,g);A=(T+sol['solved_net'])/2;B=T-A;fields={v['headers'][2]:A,v['headers'][3]:B,**other_fields};largest=max(fields.values());leaders=[k for k,n in fields.items()if abs(n-largest)<1e-7]
                scenarios.append({'preference_anchor':anchor,'historical_volume_mix':mix,'volume_contest':volume_contest,'all_candidate_volume':totalV,'pair_participation_state':T/totalV,'all_candidate_target_margin_pp':100*sol['target_net']/totalV,'other_candidate_expected_votes':other_fields,'plurality_leaders_with_held_other':leaders,**sol})
                for u in units:
                    s=clip(u['share']+sol['shift']);net=u['volume']*(2*s-1);ownbase=u['volume']*(2*u['share']-1);sel=selected(u['volume'],M-ownbase,g*T)
                    contrib.append({'preference_anchor':anchor,'historical_volume_mix':mix,'volume_contest':volume_contest,'county':u['county'],'fips':fips[u['county']], 'A_label':v['headers'][2],'B_label':v['headers'][3],'all_candidate_volume':u['all_candidate_volume'],'pair_participation':u['pair_participation'],'pair_volume':u['volume'],'pair_weight':u['volume']/T,'baseline_A_pair_share':u['share'],'target_pair_margin_pp':g*100,'unbounded_state_shift_pp':sol['unbounded_shift_pp'],'bounded_state_shift_pp':sol['shift_pp'],'target_A_pair_share':s,'actual_A_share_shift_pp':100*(s-u['share']),'target_county_pair_margin_pp':100*(2*s-1),'target_net':net,'net_gain':net-ownbase,'gain_net_per_A_share_pp':.02*u['volume'],'selected_only_unbounded_share':sel['required_share_unbounded'],'selected_only_feasible_share':sel['feasible_share'],'selected_only_status':sel['status'],'others_share_shift_pp':0})
    save(D/'state-scenarios.json',scenarios);csvout(D/'county-target-scenarios.csv',contrib)
    # Meaningful synthetic examples, independent of current vote or private geography.
    common={'counted_A':40,'counted_B':50,'counted_other':{'C':5},'remaining':100,'pair_participation':.8,'remaining_A_pair_share':.6,'remaining_other_mix':{'C':1}}
    variations={'ordinary':{},'unknown_remaining':{'remaining':None},'unknown_preference':{'remaining_A_pair_share':None},'negative_pool':{'remaining':-1},'no_pool':{'remaining':0},'secured':{'counted_A':200},'impossible':{'counted_B':300},'clip_high':{'remaining_A_pair_share':1.2},'clip_low':{'remaining_A_pair_share':-.3},'no_pair_pool':{'pair_participation':0},'unknown_other_mix':{'remaining_other_mix':{}},'other_candidate_wins':{'counted_other':{'C':300}},'Aplus1_final_denominator':{'target_pair_margin':.01},'invalid_participation':{'pair_participation':1.1}}
    save(D/'live-synthetic-scenarios.json',{k:live({**common,**x})for k,x in variations.items()})
    save(D/'bounded-synthetic-scenarios.json',{'clipping':uniform([{'volume':10,'share':1},{'volume':90,'share':.4}],.9),'impossible':uniform([{'volume':100,'share':.5}],1.1),'no_pool':uniform([{'volume':0,'share':.5}]),'unknown':uniform([{'volume':None,'share':None}]),'selected_secured':selected(1,10,0),'selected_impossible':selected(1,-10,0)})
    print(json.dumps({'county_rows':len(bases),'native_rows':len(native),'source_candidate_control_cells':len(long),'county_scenario_rows':len(contrib),'native_target_rows':len(native_targets),'state_scenarios':len(scenarios)}))
if __name__=='__main__':main()

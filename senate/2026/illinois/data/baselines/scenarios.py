"""All-county and all-2024-native deterministic targets with historical weights."""
import csv,gzip,io,json,itertools
from source_io import ROOT,dump
from extract import csvwrite
from calculator import clip,bounded_shift,selected_only

def output_rows(path,fields,iterator):
    with gzip.open(path,'wt',encoding='utf-8',newline='')as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(iterator)
def main():
    raw=list(csv.DictReader((ROOT.parent/'county-baselines.csv').open()))
    by={y:{r['county_key']:r for r in raw if r['year']==y}for y in ['2020','2022','2024']}
    nums=['A','B','pair_votes','other_named','all_named_votes','ballots_cast']
    for m in by.values():
        for r in m.values():
            for k in nums:r[k]=int(r[k])
    totals={y:{k:sum(r[k]for r in m.values())for k in nums}for y,m in by.items()}
    settings={'volume_bases':{'low':{'year':'2022','contest':'Senate ClassIII midterm','all_candidate_votes':totals['2022']['all_named_votes']},'base':{'year':'2024','contest':'President','all_candidate_votes':totals['2024']['all_named_votes']},'high':{'year':'2020','contest':'Senate ClassII','all_candidate_votes':totals['2020']['all_named_votes']}},'county_mix_years':['2020','2022','2024'],'county_preference_years':['2020','2022','2024'],'county_volume_formula':'N_c=historical_state_all_candidate_volume * (mix_year_county_all_named / mix_year_state_all_named); T_c=N_c*(mix_year_county_pair / mix_year_county_all_named). Preference independently uses named A/(A+B) of preference year.','native_formula':'Only2024 authority+literal precinct recorded pair weights; low/base/high pair and all-candidate statewide totals from named historical contests, proportionally scaled over original2024pair weights. Historical preference remains2024. Four administrative-only contexts have no assigned pair pool; no absent named vote is relabeled observed0.','native_cross_year_join':False,'target_definitions':{'tie':0,'pair_A_plus1':'.01*T','all_candidate_A_plus1':'.01*N'},'legal_outcome':'Strict plurality of all named candidates; tie/+1 A-B arithmetic alone does not establish an election winner. Other named candidate vote shares held at mix-year statewide totals in county scenarios, and volume-anchor statewide totals in native scenarios, as explicit historical-only assumptions.','others_selected_only_assumption':'Every other unit fixed at that model baseline share and expected volume, zero additional share shift; no priority filter.'}
    dump(ROOT/'scenario-settings.json',settings)
    # Full-field historical other anchors retain literal identity and blank party.
    src=list(csv.DictReader((ROOT/'extract/statewide-source-rows.csv').open()))
    other={}
    for y in by:
        ex=next(iter(by[y].values()));other[y]=[{**r,'votes':int(r['votes'])}for r in src if r['year']==y and r['candidate_literal']not in [ex['A_name'],ex['B_name']]]
    states=[];countyrows=[];fields=None
    for vol,mix,pref in itertools.product(['low','base','high'],['2020','2022','2024'],['2020','2022','2024']):
        V=settings['volume_bases'][vol]['all_candidate_votes'];N=totals[mix]['all_named_votes']
        units=[]
        for key,r in by[mix].items():
            anchor=by[pref][key];n=V*r['all_named_votes']/N;t=n*r['pair_votes']/r['all_named_votes'];s=anchor['A']/anchor['pair_votes']
            units.append(dict(key=key,name=r['county'],volume=t,share=s,contest_volume=n,pair_participation=r['pair_votes']/r['all_named_votes'],preference_A_name=anchor['A_name'],preference_B_name=anchor['B_name']))
        T=sum(u['volume']for u in units);M=sum(u['volume']*(2*u['share']-1)for u in units)
        for target,g in [('tie',0),('pair_A_plus1',.01),('all_candidate_A_plus1',.01*V/T)]:
            sid=f'county-{vol}-mix{mix}-pref{pref}-{target}';sol=bounded_shift(units,g);assert sol['status']=='feasible'
            other_counts=[dict(candidate_literal=r['candidate_literal'],party_literal=r['party_literal'],expected_votes=r['votes']*V/N)for r in other[mix]]
            final_A=(T+sol['achieved_net'])/2;largest=max([x['expected_votes']for x in other_counts],default=0)
            states.append(dict(scenario=sid,level='county',volume_setting=vol,mix_year=mix,preference_year=pref,target=target,units=len(units),all_candidate_denominator=V,pair_denominator=T,other_votes=V-T,**sol,shift_share_pp=100*sol['shift'],unbounded_shift_share_pp=100*sol['unbounded_shift'],achieved_pair_margin_pp=100*sol['achieved_net']/T,achieved_all_candidate_margin_pp=100*sol['achieved_net']/V,final_A=final_A,largest_named_other=largest,A_exceeds_all_named_others=final_A>largest,other_candidate_assumptions=json.dumps(other_counts,ensure_ascii=False),all_other_units_fixed_for_selected='model baseline; additional share shift0'))
            for u in units:
                q=clip(u['share']+sol['shift']);net=u['volume']*(2*u['share']-1);newnet=u['volume']*(2*q-1);sel=selected_only(u['volume'],M-net,T,g)
                countyrows.append(dict(scenario=sid,county_key=u['key'],county=u['name'],volume_setting=vol,mix_year=mix,preference_year=pref,preference_A_name=u['preference_A_name'],preference_B_name=u['preference_B_name'],target=target,expected_all_candidate_votes=u['contest_volume'],expected_pair_votes=u['volume'],pair_participation=u['pair_participation'],pair_weight=u['volume']/T,contest_weight=u['contest_volume']/V,baseline_A_pair_share=u['share'],baseline_pair_margin_pp=100*(2*u['share']-1),baseline_pair_net=net,baseline_state_pair_net_contribution_pp=100*net/T,plus1_share_pp_net_gain=.02*u['volume'],target_A_pair_share=q,target_pair_margin_pp=100*(2*q-1),required_A_share_shift_pp=100*(q-u['share']),bounded_uniform_shift_share_pp=100*sol['shift'],unbounded_uniform_shift_share_pp=100*sol['unbounded_shift'],clipped=q!=u['share']+sol['shift'],target_pair_net=newnet,net_gain=newnet-net,target_all_candidate_margin_pp=100*newnet/u['contest_volume'],selected_only_required_A_share=sel.get('required_share'),selected_only_status=sel['status'],selected_only_bounded_share=sel.get('bounded_share'),selected_only_required_change_pp=100*(sel['required_share']-u['share'])if sel.get('required_share')is not None else None,others_share_shift_pp=0,all_state_units_included=102))
    csvwrite(ROOT/'county-target-scenarios.csv.gz',countyrows)
    # Native model: no inferred methods, geometry or cross-year identity.
    nr=json.loads((ROOT/'extract/2024-units.json').read_text());baseT=totals['2024']['pair_votes'];native_rows=[]
    for vol in ['low','base','high']:
        y=settings['volume_bases'][vol]['year'];T=totals[y]['pair_votes'];V=totals[y]['all_named_votes'];factor=T/baseT
        units=[]
        for r in nr:
            complete=r['A']is not None and r['B']is not None
            t=(r['A']+r['B'])*factor if complete else 0.
            s=r['A']/(r['A']+r['B'])if complete and r['A']+r['B']>0 else None
            units.append({'key':r['unit_key'],'volume':t,'share':s,'raw':r,'status':('complete_printed_pair'if t>0 else'complete_printed_pair_no_positive_observed_pool')if complete else'administrative_only_no_assigned_pair_pool'})
        assert abs(sum(u['volume']for u in units)-T)<1e-6
        for target,g in [('tie',0),('pair_A_plus1',.01),('all_candidate_A_plus1',.01*V/T)]:
            sid=f'native-{vol}-mix2024-pref2024-{target}';sol=bounded_shift(units,g);assert sol['status']=='feasible';M=sol['baseline_net']
            final_A=(T+sol['achieved_net'])/2;largest=max([r['votes']for r in other[y]],default=0)
            states.append(dict(scenario=sid,level='native_recorded_pair',volume_setting=vol,mix_year='2024',preference_year='2024',target=target,units=len(units),all_candidate_denominator=V,pair_denominator=T,other_votes=V-T,**sol,shift_share_pp=100*sol['shift'],unbounded_shift_share_pp=100*sol['unbounded_shift'],achieved_pair_margin_pp=100*sol['achieved_net']/T,achieved_all_candidate_margin_pp=100*sol['achieved_net']/V,final_A=final_A,largest_named_other=largest,A_exceeds_all_named_others=final_A>largest,other_candidate_assumptions=json.dumps(other[y],ensure_ascii=False),all_other_units_fixed_for_selected='2024recorded pair shares; additional shift0; source administrative observations no modeled pair pool'))
            for u in units:
                r=u['raw'];s=u['share'];q=clip(s+sol['shift'])if s is not None else None;net=u['volume']*(2*s-1)if s is not None else 0.;newnet=u['volume']*(2*q-1)if q is not None else 0.;sel=selected_only(u['volume'],M-net,T,g)
                native_rows.append(dict(scenario=sid,unit_key=r['unit_key'],JurisdictionID=r['JurisdictionID'],PrecinctName=r['PrecinctName'],native_pair_status=u['status'],A_observed=r['A'],B_observed=r['B'],expected_pair_votes=u['volume'],pair_weight=u['volume']/T,baseline_A_pair_share=s,baseline_pair_net=net,baseline_state_pair_margin_contribution_pp=100*net/T,plus1_share_pp_net_gain=.02*u['volume'],target_A_pair_share=q,target_pair_margin_pp=100*(2*q-1)if q is not None else None,required_share_change_pp=100*(q-s)if q is not None else None,target_pair_net=newnet,net_gain=newnet-net,clipped=q!=s+sol['shift']if s is not None else False,selected_only_required_A_share=sel.get('required_share'),selected_only_status=sel['status'],others_share_shift_pp=0,source_positions=json.dumps(r['source_positions']),method='unavailable_no_source_column',current_identity='unverified',all_candidate_native_denominator='unavailable_named_writein_allocation',state_all_candidate_denominator=V))
    csvwrite(ROOT/'native-target-scenarios.csv.gz',native_rows)
    csvwrite(ROOT/'state-scenarios.csv',states,sorted(set().union(*(r.keys()for r in states))))
    # Every full native presentation retained; category-only contexts do not create extra pair volume.
    contexts=json.loads(gzip.decompress((ROOT/'extract/2024-contexts.json.gz').read_bytes()))
    presentation=[]
    for c in contexts:
        pairrows=[r for r in c['candidate_category_rows']if r['CandidateName']in ['Kamala D. Harris','Donald J. Trump']]
        presentation.append(dict(presentation_id=c['presentation_id'],JurisdictionID=c['JurisdictionID'],JurisContainerID=c['JurisContainerID'],JurisName=c['JurisName'],PrecinctName=c['PrecinctName'],arithmetic_unit_key=json.dumps(['2024',c['JurisdictionID'],c['PrecinctName']],ensure_ascii=False,separators=(',',':')),source_positions=json.dumps(c['source_positions']),pair_candidate_records=len(pairrows),pair_weight_assignment='recorded_pair_weights_once_per_authority_literalprecinct'if pairrows else 'category_presentation_no_additional_pair_weight',scenario_source='native-target-scenarios.csv.gz',current_identity='unverified'))
    csvwrite(ROOT/'native-presentation-scenario-index.csv.gz',presentation)
    print(json.dumps({'county_models':27,'county_target_rows':len(countyrows),'native_target_rows':len(native_rows),'state_target_rows':len(states),'native_presentations':len(presentation)},indent=2))
if __name__=='__main__':main()

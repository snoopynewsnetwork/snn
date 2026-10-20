"""All108authority targets; disjoint CSV pair slices, not combined county selectors."""
import csv,json,collections
from source_io import ROOT,dump
from extract import csvwrite
from calculator import bounded_shift,clip,selected_only
def main():
    nr=list(csv.DictReader((ROOT/'extract/authority-candidate-category-totals.csv').open()));cats=collections.defaultdict(dict)
    for r in nr:
        if r['year']=='2024':cats[r['JurisdictionID']][r['candidate_or_category_literal']]=int(r['votes'])
    inv={r['JurisdictionID']:r for r in csv.DictReader((ROOT/'authority-inventory.csv').open())};assert len(cats)==108
    settings=json.loads((ROOT/'scenario-settings.json').read_text());county=list(csv.DictReader((ROOT.parent/'county-baselines.csv').open()));totals={y:sum(int(r['pair_votes'])for r in county if r['year']==y)for y in ['2020','2022','2024']};base=totals['2024'];out=[];states=[]
    for volume,setting in settings['volume_bases'].items():
        T=totals[setting['year']];V=setting['all_candidate_votes'];units=[]
        for jid,c in cats.items():
            A=c['Kamala D. Harris'];B=c['Donald J. Trump'];units.append(dict(key=jid,A=A,B=B,volume=(A+B)*T/base,share=A/(A+B)))
        for target,g in [('tie',0),('pair_A_plus1',.01),('all_candidate_A_plus1',.01*V/T)]:
            sol=bounded_shift(units,g);sid=f'authority-{volume}-mix2024-pref2024-{target}';M=sol['baseline_net'];states.append(dict(scenario=sid,volume=volume,target=target,units=108,all_candidate_denominator=V,pair_denominator=T,native_named_denominator='unavailable_authority_named_writein_allocation',**sol))
            for u in units:
                q=clip(u['share']+sol['shift']);net=u['volume']*(2*u['share']-1);newnet=u['volume']*(2*q-1);sel=selected_only(u['volume'],M-net,T,g)
                out.append(dict(scenario=sid,JurisdictionID=u['key'],authority=inv[u['key']]['authority_name_native'],parent_county=inv[u['key']]['historical_parent_county'],A=u['A'],B=u['B'],volume_setting=volume,expected_pair_votes=u['volume'],pair_weight=u['volume']/T,baseline_A_pair_share=u['share'],baseline_net=net,plus1_share_pp_net_gain=.02*u['volume'],target_A_pair_share=q,target_pair_net=newnet,net_gain=newnet-net,shift_share_pp=100*(q-u['share']),selected_only_required_A_share=sel.get('required_share'),selected_only_status=sel['status'],others_share_shift_pp=0,all_state_authorities_included=108,all_named_authority_denominator='unavailable',method='unavailable_no_source_column',current_identity='unverified'))
    csvwrite(ROOT/'authority-target-scenarios.csv',out);dump(ROOT/'authority-state-scenarios.json',states)
    print(json.dumps({'authorities':108,'authority_target_rows':len(out),'state_targets':len(states)}))
if __name__=='__main__':main()

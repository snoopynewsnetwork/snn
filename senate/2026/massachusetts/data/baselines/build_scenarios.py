#!/usr/bin/env python3
import csv,gzip,json
from calculate import historical
from extract_originals import ROOT,TAGS,dump,write_csv
def main():
    controls=json.loads((ROOT/'controls.json').read_text());extracts={tag:json.loads(gzip.decompress((ROOT/'extract'/f'{tag}-original-extraction.json.gz').read_bytes())) for tag in TAGS}
    configs=[]
    for tag in TAGS:
        configs.append((tag+'-own-native',tag,tag,'precinct',1,'Own source native pair volume and own pair preferences; no cross-year native joins'))
    base=controls['2024-senate']['named_pair']
    for label,anchor in [('low','2022-governor'),('high','2020-senate')]:
        configs.append((f'2024-native-fixedmix-{label}', '2024-senate',anchor,'precinct',controls[anchor]['named_pair']/base,'2024 native pair composition scaled to historical statewide pair volume; synthetic fixed mix, not old native allocation'))
    # Matched literal municipal names are explicit administrative comparison assumptions.
    # No boundary/current/native equivalence follows. Never distribute old municipal votes to new precincts.
    for pref in TAGS:
        for mix in ['2022-governor','2024-senate','2020-senate']:
            configs.append((pref+'-municipal-mix-'+mix,pref,mix,'municipal',1,'All351 literal City/Town parents; same-label administrative comparability assumed for sensitivity, no historical native crosswalk'))
    summaries=[];settings=[]
    for name,pref,mix,scope,scale,note in configs:
        ps=extracts[pref]['objects'][scope];mx={u['city_town']:u for u in extracts[mix]['objects']['municipal']}
        units=[];metadata={}
        for u in ps:
            x=u['values'];P=x[0]+x[1]
            if scope=='municipal':
                v=mx[u['city_town']]['values'];T=v[0]+v[1]
            else:T=P*scale
            # Other source votes kept at preference-anchor participation relative to pair pool.
            # This is a declared fullfield sensitivity, not a forecast or legal write-in allocation.
            other=(sum(x[:-2])-P)*(T/P) if P else 0
            units.append(dict(key=u['key'],T=T,share=x[0]/P if P else .5,other_votes=other))
            metadata[u['key']]=dict(city_town=u['city_town'],ward=u['ward'],pct=u['pct'],source_A=x[0],source_B=x[1],pair_participation_reported=P/sum(x[:-2]) if sum(x[:-2]) else None,pair_participation_ballots=P/x[-1] if x[-1] else None,source_record_ordinal=u['record_ordinal'])
        settings.append(dict(name=name,scope=scope,preference_anchor=pref,volume_anchor=mix,scale=scale,note=note,units=len(units),pair_volume=sum(u['T'] for u in units),other_participation='Preference-anchor reported nonpair (named nonpair candidates plus separate AllOthers) / pair ratio per unit held fixed as pair volume changes',other_units_selected_break_even='Every other unit at its own unshifted preference-anchor pair share and the stated scenario T',input_file=f'scenarios/{name}-input.json.gz'))
        dump(ROOT/'scenarios'/f'{name}-input.json.gz',dict(units=units,target_margin=0,settings=settings[-1]))
        for target in [0,.01]:
            result=historical(units,target);out=[]
            for u in result.pop('units'):
                req=u.pop('selected_unit_only')
                out.append(dict(scenario=name,state_target_pair_margin=target,**metadata[u['key']],**u,selected_only_raw_share=req['raw_share'],selected_only_clipped_share=req['clipped_share'],selected_only_status=req['status']))
            result.pop('selected');summaries.append(dict(scenario=name,scope=scope,preference_anchor=pref,volume_anchor=mix,**result))
            write_csv(ROOT/'scenarios'/(name+'-'+('tie' if target==0 else 'Aplus1')+'.csv'),out)
    dump(ROOT/'scenarios/settings.json',settings);write_csv(ROOT/'scenarios/state-targets.csv',summaries)
    p=json.loads((ROOT/'priority-set.json').read_text());rows=list(csv.DictReader((ROOT/'orders/2024-senate-precinct-named_pair.csv').open()))
    native={u['key']:u for u in extracts['2024-senate']['objects']['precinct']};k=p['precinct-named_pair']['minimum80_count'];C=p['precinct-named_pair']['crossing_cumulative'];B=p['precinct-named_pair']['previous_cumulative'];T=p['precinct-named_pair']['total']
    inside=sum(native[r['source_unit_key']]['values'][-3] for r in rows[:k]);outside=sum(native[r['source_unit_key']]['values'][-3] for r in rows[k:])
    impacts={}
    for basis in ['all_named','reported_generic','ballots']:
        alt=list(csv.DictReader((ROOT/'orders'/f'2024-senate-precinct-{basis}.csv').open()));sel={r['source_unit_key'] for r in rows[:k]};alt_sel={r['source_unit_key'] for r in alt if r['minimum80_member']=='True'}
        impacts[basis]=dict(positions_changed=sum(a['source_unit_key']!=b['source_unit_key'] for a,b in zip(rows,alt)),added=sorted(alt_sel-sel),removed=sorted(sel-alt_sel),minimum80_count=len(alt_sel))
    alt=sorted(native.values(),key=lambda x:(-(x['values'][0]+x['values'][1]),x['record_ordinal']))
    impacts['source_record_ties_alternative']=dict(positions_changed=sum(r['source_unit_key']!=s['key'] for r,s in zip(rows,alt)),priority_added=sorted({u['key'] for u in alt[:k]}-{u['source_unit_key'] for u in rows[:k]}),priority_removed=sorted({u['source_unit_key'] for u in rows[:k]}-{u['key'] for u in alt[:k]}),minimum80_count=k,crossing_votes=sum(sum(u['values'][:2]) for u in alt[:k]))
    dump(ROOT/'scenarios/priority-sensitivity.json',dict(impacts=impacts,counterfactual_generic_bounds=dict(AllOthers_inside_fixed1470=inside,AllOthers_outside_fixed1470=outside,minimum_eligible_wholly_outside_to_break_fixed1470=(5*C-4*T)//4+1,minimum_eligible_wholly_inside_fixed1469_to_reach80=4*T-5*B),qualification='Counterfactual eligibility allocations only, not actual valid-writein evidence. Matching named/fullgeneric memberships does not establish legal robustness.'))
    print('Built',len(configs),'settings and',len(summaries),'state/every-unit targets')
if __name__=='__main__':main()

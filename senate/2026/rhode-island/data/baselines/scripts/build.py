"""Whole-state native baselines and declared historical sensitivities; never imports peer counts."""
import collections,json
from common import *
from calculate import historical
CONTESTS=[(2024,'Senator in Congress','2024-senate','other Class I seat'),
          (2024,'Presidential Electors For:','2024-president','separate presidential comparison'),
          (2020,'Senator in Congress','2020-senate','same Class II seat'),
          (2020,'Presidential Electors For:','2020-president','additional historical high-volume comparison'),
          (2022,'Governor','2022-governor','actual midterm')]
def main():
    roots=read_gz('witness/root-selected.jsonl.gz');inventory=json.loads((BASE/'extracts/native-inventory.json').read_text())
    stats=json.loads((BASE/'extracts/native-statistics.json').read_text());rank=json.loads((BASE/'witness/independent-native-priority.json').read_text())
    ri={r['source_code']:r for r in rank};tables=[];parents=[];contests={};flat=[]
    for year,title,cid,role in CONTESTS:
        rr=[r for r in roots if r['year']==year and r['contest_title'].strip()==title]
        universe=[]
        for r in rr:
            c=(r['candidate_code'],r['candidate_name'],r['party'])
            if c not in universe:universe.append(c)
        assert len({x[0] for x in universe})==len(universe),'no deduplication of ambiguous keys permitted'
        a=next(c[1].strip() for c in universe if c[2].strip()=='DEM');b=next(c[1].strip() for c in universe if c[2].strip()=='REP')
        nrows=[]
        for inv in [i for i in inventory if i['year']==year]:
            c=inv['source_code'];cr=[r for r in rr if r['source_code']==c];available=bool(cr)
            candidates=[{'candidate_code':r['candidate_code'],'name_raw':r['candidate_name'],'party_raw':r['party'],
                'votes':r['votes'],'methods':r['methods'],'line':r['line'],'byte_start':r['byte_start'],'byte_end':r['byte_end']} for r in cr]
            ac=sum(r['votes'] for r in cr if r['party'].strip()=='DEM') if available else None
            bc=sum(r['votes'] for r in cr if r['party'].strip()=='REP') if available else None
            allv=sum(r['votes'] for r in cr) if available else None;pair=ac+bc if available else None
            r=cr[0] if available else None
            anchor={'zip_sha256':r['zip_sha256'],'member':r['member'],'first_byte':r['byte_start'],'line':r['line']} if r else None
            key=f"{r['zip_sha256']}#{r['member']}#{r['byte_start']}" if r else None
            st=[s for s in stats if s['year']==year and s['source_code']==c]
            def stat(name):
                v=[s for s in st if s['statistic']==name];assert len(v)<=1
                return v[0]['total'] if v else None
            row={'election':cid,'year':year,'contest':title,'comparison_role':role,'source_unit_key':key,
                'source_code':c,'source_name':inv['source_name'],'parent_key':inv['parent_key'],'parent_kind':inv['parent_kind'],
                'source_anchor':anchor,'observed':available,'A_name':a,'B_name':b,'A_votes':ac,'B_votes':bc,
                'pair_votes':pair,'other_reported_votes':allv-pair if available else None,'all_reported_votes':allv,
                'A_pair_share':ac/pair if pair else None,'pair_margin':(ac-bc)/pair if pair else None,
                'A_all_candidate_share':ac/allv if allv else None,'all_candidate_margin':(ac-bc)/allv if allv else None,
                'pair_participation':pair/allv if allv else None,'candidates':candidates,
                'methods':[sum(r['methods'][i] for r in cr) for i in range(14)] if available else None,
                'registration':stat('REGISTERED VOTERS - TOTAL'),'election_ballots':stat('BALLOTS CAST - TOTAL'),
                'election_blank_ballots':stat('BALLOTS CAST - BLANK'),
                'contest_ballots':None,'contest_undervotes':None,'contest_overvotes':None,'valid_named_writeins':None,
                'rank2024_senate':ri[c]['rank'] if year==2024 and c in ri else None,
                'priority2024_senate':ri[c]['priority'] if year==2024 and c in ri else None,
                'role_literals':inv['roles_literal'],'current_2026_mapping':None}
            nrows.append(row);tables.append(row)
            f={k:v for k,v in row.items() if k not in ['candidates','methods','source_anchor','role_literals']}
            f.update(source_archive_sha256=anchor['zip_sha256'] if anchor else None,source_member=anchor['member'] if anchor else None,
                     first_source_byte=anchor['first_byte'] if anchor else None,source_line=anchor['line'] if anchor else None,
                     candidates_json=json.dumps(candidates,separators=(',',':')),method_slots_json=json.dumps(row['methods']),
                     roles_json=json.dumps(row['role_literals'],sort_keys=True))
            flat.append(f)
        ps=[]
        for p in dict.fromkeys(r['parent_key'] for r in nrows):
            children=[r for r in nrows if r['parent_key']==p and r['observed']]
            if not children:
                invrows=[r for r in nrows if r['parent_key']==p]
                ps.append({'election':cid,'year':year,'parent_key':p,'parent_kind':invrows[0]['parent_kind'],
                    'children':[],'all_child_codes':[r['source_code'] for r in invrows],
                    'A_name':a,'B_name':b,'A_votes':None,'B_votes':None,'pair_votes':None,'all_reported_votes':None,
                    'A_pair_share':None,'candidates':[],'status':'unavailable contest; Board statistic-only administrative contexts'})
                continue
            cand=[]
            for code,name,party in universe:
                cr=[c for r in children for c in r['candidates'] if c['candidate_code']==code]
                cand.append({'candidate_code':code,'name_raw':name,'party_raw':party,'votes':sum(c['votes'] for c in cr),
                             'methods':[sum(c['methods'][i] for c in cr) for i in range(14)]})
            av=sum(r['A_votes'] for r in children);bv=sum(r['B_votes'] for r in children);fv=sum(r['all_reported_votes'] for r in children)
            ps.append({'election':cid,'year':year,'parent_key':p,'parent_kind':children[0]['parent_kind'],
                'children':[r['source_unit_key'] for r in children],'all_child_codes':[r['source_code'] for r in nrows if r['parent_key']==p],
                'A_name':a,'B_name':b,'A_votes':av,'B_votes':bv,'pair_votes':av+bv,'all_reported_votes':fv,
                'A_pair_share':av/(av+bv) if av+bv else None,'candidates':cand})
        parents+=ps
        contests[cid]={'year':year,'contest':title,'role':role,'A_name':a,'B_name':b,'native_rows':len(nrows),
            'observed_units':sum(r['observed'] for r in nrows),'absent_units':[r['source_code'] for r in nrows if not r['observed']],
            'A_votes':sum(r['A_votes'] for r in nrows if r['observed']),'B_votes':sum(r['B_votes'] for r in nrows if r['observed']),
            'all_reported_votes':sum(r['all_reported_votes'] for r in nrows if r['observed']),
            'candidates':[dict(candidate_code=c,name_raw=n,party_raw=p,votes=sum(r['votes'] for r in rr if r['candidate_code']==c),
                    methods=[sum(r['methods'][i] for r in rr if r['candidate_code']==c) for i in range(14)]) for c,n,p in universe]}
    write_gz('extracts/native-baselines.jsonl.gz',tables);write_json('extracts/parent-baselines.json',parents);write_json('extracts/state-baselines.json',contests)
    write_csv('../county-baselines.csv',flat)
    # Priority never uses a coarser parent ranking.
    write_json('native-priority-contract.json',{'schema':'ri-baseline-native-v1','source_contest':'2024-senate','total':sum(x['votes'] for x in rank),
        'minimum80_count':sum(x['priority'] for x in rank),'top15_votes':sum(x['votes'] for x in rank[:15]),
        'priority_votes':sum(x['votes'] for x in rank if x['priority']),'remainder_votes':sum(x['votes'] for x in rank if not x['priority']),
        'ordered_all_keys':[x['key'] for x in rank],'ordered_priority_keys':[x['key'] for x in rank if x['priority']],
        'ordered_remainder_keys':[x['key'] for x in rank if not x['priority']],
        'parents':[{'parent_key':p['parent_key'],'parent_kind':p['parent_kind'],'children':p['children']} for p in parents if p['election']=='2024-senate'],
        'coordinator_acceptance':False,'current_geography_approved':False,'peer_agreement':'see reciprocal/reconciliation.json; captured scope only'})
    settings=[];scenario_inputs=[]
    def units_for(rows):
        return [dict(key=r['source_unit_key'],pair_volume=r['pair_votes'],all_volume=r['all_reported_votes'],
            a_share=r['A_pair_share'],others={c['name_raw'].strip():c['votes'] for c in r['candidates'] if c['party_raw'].strip() not in ['DEM','REP','NON']},
            unallocated_other=sum(c['votes'] for c in r['candidates'] if c['party_raw'].strip()=='NON')) for r in rows]
    for cid,control in contests.items():
        ns=[r for r in tables if r['election']==cid and r['observed']]
        scenario_inputs.append((cid+'-historical',units_for(ns),control['A_name'],control['B_name'],ns))
        settings.append({'id':cid+'-historical','volume_basis':cid+' original reported candidate+generic votes by native context',
            'mix_basis':cid+' own native weights; no cross-year native join','preference_anchor':cid+' A/(A+B); zero pair remains undefined',
            'pair_participation':cid+' native (A+B)/all reported votes','interpretation':'Historical electorate repeat arithmetic, not a 2026 projection'})
    ns=[r for r in tables if r['election']=='2024-senate' and r['observed']]
    base_parent={p['parent_key']:p for p in parents if p['election']=='2024-senate'}
    for label,anchor in [('low','2022-governor'),('base','2024-senate'),('high','2020-president')]:
        ref={p['parent_key']:p for p in parents if p['election']==anchor};units=[]
        for r in ns:
            p=r['parent_key'];original=r['all_reported_votes'];pv=base_parent[p]['all_reported_votes']
            # State-admin federal contexts always retain their own actual 2024 volume; no municipal allocation.
            target=ref[p]['all_reported_votes'] if r['parent_kind']=='municipality' else pv
            factor=target/pv if pv else 1.0
            u=units_for([r])[0]
            u['all_volume']*=factor;u['pair_volume']*=factor
            u['others']={k:v*factor for k,v in u['others'].items()};u['unallocated_other']*=factor
            units.append(u)
        ident='2024-senate-'+label+'-historical-mix'
        scenario_inputs.append((ident,units,contests['2024-senate']['A_name'],contests['2024-senate']['B_name'],ns))
        settings.append({'id':ident,'label':label,'volume_basis':anchor+' municipal reported candidate+generic volumes; all four state-admin federal contexts fixed at actual 2024 Senate',
            'mix_basis':'2024 native all-vote shares within each officially linked municipality; municipal volume from '+anchor,
            'preference_anchor':'2024 Senate native A/(A+B), undefined when pair=0',
            'pair_participation':'2024 Senate native (A+B)/all reported votes held fixed; other proportions fixed',
            'cross_year_mapping':'Municipal parents only, each year original HTML child links; no native/physical precinct crosswalk',
            'interpretation':'Declared historical volume/mix sensitivity. Scaled native scenario volumes are assumptions, not historical allocations or 2026 projections'})
    targetrows=[];staterows=[];parenttargets=[]
    for ident,units,a,b,ns in scenario_inputs:
        for margin,label in [(0,'tie'),(.01,'Aplus1')]:
            data={'mode':'historical','pair':{'A':a,'B':b},'candidate_universe_complete':False,'target_margin':margin,'units':units}
            write_json('scenarios/'+ident+'-'+label+'.input.json',data)
            result=historical(data);write_json('scenarios/'+ident+'-'+label+'.result.json',result)
            lookup={r['source_unit_key']:r for r in ns}
            for r in result['units']:
                original=lookup[r['key']]
                flat={k:v for k,v in r.items() if k!='selected_only'}
                flat.update(scenario=ident,target=label,source_code=original['source_code'],source_name=original['source_name'],
                    parent_key=original['parent_key'],selected_only_raw_share=r['selected_only']['raw_required_share'],
                    selected_only_feasible_share=r['selected_only']['feasible_share'],selected_only_status=r['selected_only']['status'],
                    selected_only_other_net_votes=r['selected_only']['other_units_net_votes'],
                    selected_only_assumption=r['selected_only']['other_units_assumption'])
                targetrows.append(flat)
            staterows.append(dict(scenario=ident,target=label,units=len(units),A_name=a,B_name=b,
                all_volume=result['all_candidate_denominator'],pair_volume=result['pair_denominator'],pair_participation=result['pair_participation'],
                baseline_net_votes=result['baseline_net_votes'],unbounded_A_share_shift_pp=result['unbounded_share_shift_points'],
                bounded_A_share_shift_pp=result['uniform_share_shift_points'],target_pair_margin_pp=margin*100,
                final_net_votes=result['final_net_votes'],final_all_candidate_margin_pp=100*result['final_all_candidate_margin'],
                clipped_units=len(result['clipped_keys']),baseline_target_status=result['baseline_target_status']))
            # Selected-parent break-even, every other native unit fixed at its scenario baseline.
            for p in dict.fromkeys(r['parent_key'] for r in ns):
                keys={r['source_unit_key'] for r in ns if r['parent_key']==p};chosen=[u for u in units if u['key'] in keys]
                t=sum(u['pair_volume'] for u in chosen);own=sum(u['pair_volume']*(2*u['a_share']-1) for u in chosen if u['pair_volume'])
                rest=result['baseline_net_votes']-own;goal=margin*result['pair_denominator'];raw=(goal-rest+t)/(2*t) if t else None
                parenttargets.append(dict(scenario=ident,target=label,parent_key=p,pair_volume=t,all_volume=sum(u['all_volume'] for u in chosen),
                    pair_weight=t/result['pair_denominator'],baseline_net_votes=own,other_units_fixed_net_votes=rest,
                    target_net_votes=goal,raw_required_A_share=raw,feasible_A_share=raw if raw is not None and 0<=raw<=1 else None,
                    status='no_positive_pool' if not t else 'secured' if raw<0 else 'impossible' if raw>1 else 'feasible',
                    plus1_share_point_net_vote_gain=.02*t,assumption='All other native units fixed at scenario baseline preference/volume; within selected parent solve aggregate pair share'))
    write_csv('native-targets.csv',targetrows);write_csv('state-scenarios.csv',staterows);write_csv('parent-selected-targets.csv',parenttargets)
    write_json('scenario-settings.json',settings)
    pr=sorted([p for p in parents if p['election']=='2024-senate'],key=lambda p:(-p['all_reported_votes'],min(p['children'])))
    cum=0;out=[]
    for i,p in enumerate(pr,1):
        old=cum;cum+=p['all_reported_votes'];out.append(dict(rank=i,parent_key=p['parent_key'],parent_kind=p['parent_kind'],votes=p['all_reported_votes'],
            cumulative=cum,priority80_sensitivity=old*5<491948*4))
    write_csv('parent-rank-sensitivity.csv',out)
    print('Baselines',len(tables),'observed candidate records',sum(len(r['candidates']) for r in tables),'target rows',len(targetrows),'scenarios',len(staterows))
if __name__=='__main__':main()

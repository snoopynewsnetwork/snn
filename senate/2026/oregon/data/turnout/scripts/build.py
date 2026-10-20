#!/usr/bin/env python3
"""Exact integer rankings and an explicitly unavailable statewide native contract."""
from pathlib import Path
import csv,gzip,hashlib,json,re
from collections import defaultdict
from decimal import Decimal,localcontext
OUT=Path(__file__).resolve().parents[1]
STATE=OUT.parents[1]

def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def csvout(p,rs):
    with p.open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def fraction(a,b):
    with localcontext()as c:
        c.prec=40
        return dict(numerator=a,denominator=b,percent=str(Decimal(a)*100/Decimal(b)))
def rank(rs,value,key):
    rs=sorted(rs,key=lambda r:(-r[value],r[key]));total=sum(r[value]for r in rs);cum=0
    for i,r in enumerate(rs,1):
        cum+=r[value];r.update(rank=i,cumulative_votes=cum,share_numerator=r[value],share_denominator=total)
    n=next(i for i,r in enumerate(rs,1)if 5*r['cumulative_votes']>=4*total)
    return dict(total=total,unit_count=len(rs),full_order=rs,top15=dict(keys=[r[key]for r in rs[:15]],**fraction(sum(r[value]for r in rs[:15]),total)),
        minimum80=dict(count=n,ordered_keys=[r[key]for r in rs[:n]],preceding_count=n-1,preceding_votes=rs[n-2]['cumulative_votes']if n>1 else 0,
            crossing_key=rs[n-1][key],crossing_votes=rs[n-1][value],cumulative_votes=rs[n-1]['cumulative_votes'],**fraction(rs[n-1]['cumulative_votes'],total)),
        remainder=dict(count=len(rs)-n,keys=[r[key]for r in rs[n:]],votes=total-rs[n-1]['cumulative_votes']))

def main():
    county=json.loads((OUT/'source/county-wide.json').read_bytes())
    controls=list(csv.DictReader((OUT/'county-candidates.csv').open()))
    participation=list(csv.DictReader((OUT/'participation-controls.csv').open()))
    specs=json.loads((OUT/'candidate-universe.json').read_bytes())
    for r in county:
        for year in [2020,2022,2024]:
            p=next(x for x in participation if x['county']==r['county']and int(x['year'])==year)
            for f in ['registration_Number_Eligible','ballots_Returned']:r[f'{year}_statistical_{f}']=int(p[f])
    sensitivities={}
    for contest in ['2024-president','2020-senate','2022-senate','2022-governor']:
        for scope in ['reported_votes','named_votes']:
            value=f'{contest}_{scope}'
            rows=[dict(county=r['county'],key=r['county_fips'],votes=r[value])for r in county]
            sensitivities[value]=rank(rows,'votes','key')
    for year in [2020,2022,2024]:
        for measure in ['ballots_Returned','registration_Number_Eligible']:
            value=f'{year}_statistical_{measure}'
            sensitivities[value]=rank([dict(county=r['county'],key=r['county_fips'],votes=r[value])for r in county],'votes','key')
    primary=sensitivities['2024-president_reported_votes'];byf={r['key']:r for r in primary['full_order']}
    for r in county:
        p=byf[r['county_fips']];r.update(compatibility_file_scope='county_parent_aggregate_sensitivity_not_native_priority',
            rank_2024_president=p['rank'],state_share_2024_president=p['votes']/primary['total'],
            cumulative_votes_2024_president=p['cumulative_votes'],top15_county_sensitivity=p['rank']<=15,
            minimum80_county_sensitivity=p['rank']<=primary['minimum80']['count'],canonical_native_priority_available=False)
    csvout(OUT.parent/'county-turnout.csv',sorted(county,key=lambda r:r['rank_2024_president']))
    save(OUT/'county-sensitivities.json',sensitivities)
    rawunits=json.loads((OUT/'native/units.json').read_bytes())
    # Whole-county candidate closure is checked for every acquired presentation,
    # even those excluded from the disjoint ranking or incompletely extracted.
    bygroup=defaultdict(list)
    for u in rawunits:
        bygroup[(u['source_key'],u['county'],u['contest'])].append(u)
    reconciliations=[]
    for (key,c,contest),group in bygroup.items():
        n=len([x for x in specs if x['contest']==contest]);expected=[int(x['votes'])for x in controls if x['county']==c and x['contest']==contest]
        a=[u for u in group if u['additive']];sums=[sum(u['choices'].get(str(j),0)for u in a)for j in range(n)]
        complete=all(len(u['choices'])==n for u in a)and bool(a)
        delta=[s-e for s,e in zip(sums,expected)]
        reconciliations.append(dict(source_key=key,county=c,contest=contest,observed_additive_rows=len(a),
            rows_with_full_candidate_vector=sum(len(u['choices'])==n for u in a),candidate_sums=sums,
            county_abstract_controls=expected,differences=delta,
            complete_candidate_vectors_and_county_columns_close=complete and delta==[0]*n,
            membership_and_method_completeness='requires independent peer/source review; column closure alone is insufficient',
            nonadditive_presentations=[u['unit_literal']for u in group if not u['additive']]))
    save(OUT/'native/county-reconciliation.json',reconciliations)
    selected={'Multnomah':'multnomah-2024-sovc2','Washington':'washington-2024-precincts',
              'Clackamas':'clackamas-2024-canvass','Marion':'marion-2024-canvass','Wasco':'2024-Wasco'}
    known=[];parents=[]
    inv=json.loads((OUT/'source/original-inventory.json').read_bytes())
    for c in county:
        name=c['county'];fips=c['county_fips'];source=selected.get(name)
        group=[u for u in rawunits if u['source_key']==source and u['additive']]if source else []
        parent=dict(county=name,county_fips=fips,county_key=f'OR:county:{fips}',
            county_presidential_reported_votes=c['2024-president_reported_votes'],
            county_presidential_named_votes=c['2024-president_named_votes'],county_source_Misc=c['2024-president_Misc'],
            native_priority_status='known_original_source_universe_only'if source else 'unavailable_not_acquired_in_bounded_pass',
            native_reporting_unit_count=len(group)if source else None,
            source_native_constituents=[],source_administrative_presentations=[],unknown_native_membership=not bool(source),
            approved_current_election=False,approved_current_geometry=False)
        if name=='Lane':parent['native_priority_status']='unavailable_public_page_says_request_redaction_required_since_2023'
        if name=='Deschutes':parent['native_priority_status']='summary_observed_native_original_not_recovered_in_bounded_pass'
        if source:
            check=next(r for r in reconciliations if r['source_key']==source and r['contest']=='2024-president')
            assert check['complete_candidate_vectors_and_county_columns_close'],check
            for u in group:
                label=u['unit_literal'];native=re.sub(r'^Precinct\s+','',label)
                key=f'OR:2024-11-05:{fips}:president:{native}'
                vector=[u['choices'][str(j)]for j in range(8)]
                fields=u['fields'];presentations=[dict(source_key=source,literal_unit=label,native_contest_id=u.get('native_contest_id'),
                    source_native_id=u.get('source_native_id'),observations_unit_key=u['unit_key'],fields=fields)]
                if name=='Multnomah':
                    other=next(v for v in rawunits if v['source_key']=='multnomah-2024-president'and v['additive']and v['unit_literal']=='Precinct '+native)
                    assert [other['choices'][str(j)]for j in range(8)]==vector
                    fields=other['fields']
                    presentations.append(dict(source_key='multnomah-2024-president',literal_unit=other['unit_literal'],
                        observations_unit_key=other['unit_key'],fields=fields,relationship='overlapping same native precinct vector; nonadditive alternative'))
                constituents=[native]
                if name=='Clackamas'and native=='115/116':constituents=['115','116']
                row=dict(key=key,county=name,county_fips=fips,source_native_unit_literal=label,native_id=native,
                    source_native_constituent_ids=constituents,count_allocation_to_constituents='combined_source_row_no_split'if len(constituents)>1 else 'not_applicable',
                    source_key=source,reported_votes=sum(vector),named_candidate_votes=sum(vector[:-1]),generic_or_Misc=vector[-1],
                    candidate_vector=vector,source_presentations=presentations,
                    geography_class='combined_precinct_reporting_row'if len(constituents)>1 else 'source_precinct_reporting_row',
                    current_result_id=None,current_geometry_id=None,current_approval=False)
                parent['source_native_constituents'].append(row);known.append(row.copy())
            parent['source_administrative_presentations']=[dict(source_key=u['source_key'],literal_unit=u['unit_literal'],
                classification=u['geographic_class'],additive=False)for u in rawunits if u['county']==name and u['contest']=='2024-president'and not u['additive']]
            if name=='Clackamas':parent['reported_precinct_count_vs_source_rows']='119 reported precincts; 118 combined reporting rows; 115/116 remains one disjoint row'
        parent['historical_originals']=[dict(year=r['year'],source_key=r['source_key'],member_name=r['member_name'],
            archive_source_id=r['archive_source_id'],original_sha256=r['original_sha256'],original_bytes=r['original_bytes'],
            candidate_native_extraction_status='see native/county-reconciliation.json; incomplete groups remain explicit')for r in inv if 'member_name'in r and Path(r['member_name']).stem==name]
        parents.append(parent)
    kn=rank(known,'reported_votes','key')
    assert len(kn['full_order'])==510
    unknown=sum(p['county_presidential_reported_votes']for p in parents if p['unknown_native_membership'])
    assert kn['total']+unknown==primary['total']
    for r in kn['full_order']:r['statewide_share']=fraction(r['reported_votes'],primary['total'])
    flat=[]
    for r in kn['full_order']:
        fields=r['source_presentations'][-1]['fields']
        flat.append(dict(rank=r['rank'],key=r['key'],county=r['county'],county_fips=r['county_fips'],native_id=r['native_id'],
            native_literal=r['source_native_unit_literal'],reported_candidate_writein_votes=r['reported_votes'],named_candidate_votes=r['named_candidate_votes'],generic_or_Misc=r['generic_or_Misc'],
            cumulative_votes_known_universe=r['cumulative_votes'],known_universe_denominator=kn['total'],statewide_denominator=primary['total'],
            ballots_source=fields.get('ballots',fields.get('Total Ballots Cast','')),registration_source=fields.get('registered_voters',fields.get('Registered Voters','')),
            overvotes_source=fields.get('overvotes',''),undervotes_source=fields.get('undervotes',''),source_key=r['source_key'],canonical_statewide_rank_available=False))
    csvout(OUT/'known-native-order.csv',flat)
    save(OUT/'known-native-ranking.json',kn)
    contract=dict(schema_version='oregon.turnout.priority-set.v1',state='OR',election_basis='actual 2024-11-05 President',
        candidate_scope='seven named ballot candidates plus source-scoped Misc./generic write-ins; validity of named write-ins unestablished',
        statewide_reported_votes=primary['total'],statewide_named_candidate_votes=sensitivities['2024-president_named_votes']['total'],
        canonical_certified_native_priority_available=False,complete_coverage=False,complete_order=None,ordered_priority_keys=None,
        top15=None,minimum80=None,remainder=None,
        reason='31 county native universes remain unclosed. Complete county controls cannot substitute for finer source reporting geography.',
        all_36_county_parents=parents,known_source_universe=dict(coverage_counties=len(selected),native_unit_count=510,
            reported_votes=kn['total'],statewide_fraction=fraction(kn['total'],primary['total']),unknown_parent_votes=unknown,
            ranking_path='known-native-ranking.json',full_ordered_keys=[r['key']for r in kn['full_order']],
            ordered_priority_keys=kn['minimum80']['ordered_keys'],top15=kn['top15'],minimum80=kn['minimum80'],remainder=kn['remainder'],
            acceptance_status='qualified incomplete-source research only; not authorized geographic dispatch'),
        county_parent_sensitivity=dict(not_native_dispatch=True,path='../county-turnout.csv',ranking_path='county-sensitivities.json',
            ordered_priority_keys=primary['minimum80']['ordered_keys'],top15=primary['top15'],minimum80=primary['minimum80']),
        all_observed_native_presentations=dict(path='native/units.json',observations='native/observations.jsonl.gz',
            reconciliation='native/county-reconciliation.json',qualification='Historical OCR/normalization gaps remain. Unclosed groups and missing fields are unavailable, never zero.'),
        administrative_nonadditive=dict(vice_president_path='nonadditive-vice-president.csv',
            method_scope='Source Total/AB/ED/EV/Vote by Mail/Absentee Voting and summary presentations overlap; do not add.',
            geometry='No vintage/current reporting ID or polygon equivalence established'),
        peer_agreement=dict(peer_agent_id=None,status='pending_not_launched_no_peer_derivatives_read'),
        coordinator_acceptance=dict(status='pending',accepted=False),current_source_accepted=False,current_geographic_approval=False)
    save(OUT/'priority-set.json',contract)
    print(json.dumps(dict(county_top15=primary['top15'],county_min80=primary['minimum80'],known_native_total=kn['total'],known_native_top15=kn['top15'],known_native_min80=kn['minimum80'],unknown_parent_votes=unknown),indent=2))

if __name__=='__main__':main()

"""Final independent original CSV/full native contract/turnout seal replay.

No producer modules are imported or written. Both source-key representations
remain explicit; missing named pools sort after observed zero printed sums.
"""
from collections import defaultdict
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
from urllib.parse import quote
from review_county_originals import OriginalTables

D = Path(__file__).resolve().parent
S = D.parent
T = D/'turnout'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sem(v):
    return sha(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())


def pin(p):
    b=p.read_bytes()
    assert len(b)<40_000_000
    return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))


def main():
    manifest=json.loads((T/'asset-manifest.json').read_bytes())
    expected={r['path'] for r in manifest['assets']}
    actual={str(p.relative_to(S)) for p in T.rglob('*') if p.is_file() and p.name!='asset-manifest.json'}
    actual|={'turnout.md','data/county-turnout.csv'}
    assert actual==expected and len(actual)==937
    for r in manifest['assets']+manifest['external_originals']:
        assert pin(S/r['path'])==r
    cp=T/'priority-set.json'
    assert sha(cp.read_bytes())=='50a21c166dbe14339d3cfa103443c75d7141bf6554f40f5cc96dddf8dfecb78e'
    contract=json.loads(cp.read_bytes())
    assert contract['coordinator_acceptance'] is False and contract['current_geometry_approved'] is False
    source_pins=json.loads((T/'extract/source-pins.json').read_bytes())
    county_originals=json.loads((D/'coordinator-county-original-review.json').read_bytes())['county_objects']
    county_lookup={(int(r['year']),r['county_key']):r for r in county_originals}
    authorities={r['authority_id']:r for r in contract['authority_inventory']}
    assert len(authorities)==108
    county_candidate_checks=0
    derived=[json.loads(line) for line in gzip.decompress((T/'extract/original-native-records.jsonl.gz').read_bytes()).splitlines()]
    by_year=defaultdict(list)
    for r in derived:
        by_year[r['year']].append(r)
    counts={}
    primary_groups=defaultdict(list)
    full_presentations=set()
    checked_fields=0
    original_pins=[]
    for year,source_id,expected_rows in [(2024,'sos-2024-president-csv',59623),
                                         (2022,'sos-observed-2022-senate-native-csv',31797),
                                         (2020,'sos-observed-2020-senate-native-csv',54950)]:
        r=source_pins[source_id]
        z=(S/r['path']).read_bytes();raw=gzip.decompress(z)
        assert len(z)==r['stored_bytes'] and sha(z)==r['stored_sha256']
        assert len(raw)==r['raw_bytes'] and sha(raw)==r['raw_sha256']
        reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
        assert len(reader.fieldnames)==12
        originals=list(reader)
        assert len(originals)==len(by_year[year])==expected_rows
        for position,(a,b) in enumerate(zip(originals,by_year[year]),1):
            assert a==b['fields'] and list(a)==list(b['fields'])
            assert b['source_id']==source_id and b['record_position_1based']==position
            assert b['csv_physical_line_header_offset']==1
            checked_fields+=12
            if year==2024:
                primary_groups[(a['JurisdictionID'],a['PrecinctName'])].append((position,a))
                full_presentations.add(tuple(a[k] for k in ['JurisdictionID','JurisContainerID','JurisName','PrecinctName']))
        county_printed=defaultdict(lambda:defaultdict(int))
        explicit_names={2024:['Kamala D. Harris','Donald J. Trump','Robert F. Kennedy Jr.'],
                        2022:['TAMMY DUCKWORTH','KATHY SALVI','BILL REDPATH'],
                        2020:['RICHARD J. DURBIN','MARK C. CURRAN JR.','DANNY MALOUF','WILLIE L. WILSON','DAVID F. BLACK']}[year]
        for row in originals:
            if row['CandidateName'] in explicit_names:
                county_id=authorities[row['JurisdictionID']]['county_parent_authority_id']
                county_printed[county_id][row['CandidateName']]+=int(row['VoteCount'])
        assert len(county_printed)==102
        for county_id,vector in county_printed.items():
            original={c['candidate']:c['votes'] for c in county_lookup[(year,county_id)]['candidates']}
            for name,value in vector.items():
                assert original[name]==value
                county_candidate_checks+=1
        counts[year]=len(originals)
        original_pins.append(dict(source_id=source_id,**pin(S/r['path']),raw_bytes=len(raw),raw_sha256=sha(raw),complete_original_headers=reader.fieldnames))
    assert len(derived)==146370 and checked_fields==1756440
    assert len(primary_groups)==10062 and len(full_presentations)==11535
    constituent={r['key']:r for r in contract['native_constituents']}
    assert len(constituent)==10062
    own=[]
    names=['Kamala D. Harris','Donald J. Trump','Robert F. Kennedy Jr.']
    all_positions=[]
    for (authority,precinct), rows in primary_groups.items():
        key=f'il:2024:authority:{authority}:label:{quote(precinct,safe="")}'
        item=constituent[key]
        vector={}
        for name in names:
            matches=[a for _,a in rows if a['CandidateName']==name]
            assert len(matches)<=1
            vector[name]=int(matches[0]['VoteCount']) if matches else None
        known=sum(v for v in vector.values() if v is not None)
        missing=[k for k,v in vector.items() if v is None]
        admin=len(missing)==3
        assert item['printed_candidate_votes']==vector and item['administrative_only']==admin
        assert item['printed_known_recorded_sum']==known
        assert item['printed_observed_sum']==(None if admin else known)
        assert set(item['missing_printed_candidate_rows'])==set(missing)
        assert item['authority_id']==authority and item['precinct_name_literal']==precinct
        positions=[p for p,_ in rows]
        assert item['source_records_1based']==positions
        assert item['method'] is None
        assert contract['native_to_authority_parent_map'][key]=='il:authority:'+authority
        all_positions+=positions
        presentation_groups=defaultdict(list)
        for position,a in rows:
            presentation_groups[(a['JurisContainerID'],a['JurisName'])].append(position)
        represented={(c['container_id'],c['juris_name']):c['source_records_1based'] for c in item['source_contexts']}
        assert represented==dict(presentation_groups)
        own.append(dict(key=key,authority=authority,precinct=precinct,known=known,unavailable=admin,
                        complete_original_rows_semantic_sha256=sem([dict(position=p,fields=a) for p,a in rows])))
    assert sorted(all_positions)==list(range(1,59624))
    ordered=sorted(own,key=lambda r:(r['unavailable'],-r['known'],r['authority'],r['precinct']))
    keys=[r['key'] for r in ordered]
    assert keys==contract['full_order']
    assert keys[:5540]==contract['ordered_priority_keys'] and keys[5540:]==contract['remainder_keys']
    assert sum(r['known'] for r in ordered)==5592368
    assert sum(r['known'] for r in ordered[:15])==29572
    assert sum(r['known'] for r in ordered[:5539])==4473789
    assert sum(r['known'] for r in ordered[:5540])==4474312
    assert ordered[5539]['authority']=='88' and ordered[5539]['precinct']=='O FALLON 3' and ordered[5539]['known']==523
    assert sum(r['unavailable'] for r in ordered)==4
    assert len(contract['authority_inventory'])==108
    assert len(contract['native_to_authority_parent_map'])==10062
    for authority,item in authorities.items():
        children=[r['key'] for r in own if r['authority']==authority]
        assert item['native_constituent_keys']==children
    # Three complete original turnout tables, not native Registration sums.
    county_comparison=json.loads((D/'coordinator-county-review-inputs/inputs.json').read_bytes())['county']
    snapshot=gzip.decompress((S/county_comparison['path']).read_bytes())
    comparison={(int(r['year']),r['county']):r for r in csv.DictReader(io.StringIO(snapshot.decode()))}
    turnout_controls=[]
    for year in [2020,2022,2024]:
        r=source_pins['turnout-'+str(year)]
        z=(S/r['path']).read_bytes();raw=gzip.decompress(z)
        assert sha(z)==r['stored_sha256'] and sha(raw)==r['raw_sha256']
        parser=OriginalTables();parser.feed(raw.decode('utf-8-sig'))
        table=parser.tables['ContentPlaceHolder1_gvTurnout']['rows']
        assert [c['text'] for c in table[0]]==['Jurisdiction Name','Total Voters','Total Ballots Cast','Percent']
        assert len(table)==104
        voter_total=ballot_total=0
        for row in table[1:-1]:
            label,voters,ballots,percent=[c['text'] for c in row]
            v=int(voters.replace(',',''));b=int(ballots.replace(',',''))
            source=comparison[(year,label)]
            assert int(source['historical_Total_Voters'])==v and int(source['ballots_cast'])==b
            voter_total+=v;ballot_total+=b
        assert int(table[-1][1]['text'].replace(',',''))==voter_total
        assert int(table[-1][2]['text'].replace(',',''))==ballot_total
        turnout_controls.append(dict(year=year,complete_county_rows=102,Total_Voters=voter_total,
                                     Total_Ballots_Cast=ballot_total,complete_original_source=pin(S/r['path'])))
    assert turnout_controls[-1]['Total_Ballots_Cast']==5705246
    # Current CSV A/I labels retained literally; no new definitions inferred.
    r=source_pins['registration-current-csv']
    z=(S/r['path']).read_bytes();raw=gzip.decompress(z)
    assert sha(z)==r['stored_sha256'] and sha(raw)==r['raw_sha256']
    registration_all=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    assert len(registration_all)==109
    registration=registration_all[:-1]
    registration_footer=registration_all[-1]
    assert registration_footer['JID']=='' and registration_footer['Name']=='Totals'
    assert len(registration)==108
    for row in registration:
        assert row==authorities[row['JID']]['current_registration_row_literal']
    A=sum(int(r['A'].replace(',','')) for r in registration)
    I=sum(int(r['I'].replace(',','')) for r in registration)
    assert (A,I)==(8306489,730052)
    assert (int(registration_footer['A']),int(registration_footer['I']))==(A,I)
    root=[dict(pointer='/'+k,full_recursive_semantic_sha256=sem(v)) for k,v in contract.items()]
    result=dict(status='pass_independent_all_original_fields_native_order_and_turnout_seal',
                source_rows_by_year=counts,raw_source_records=len(derived),literal_field_comparisons=checked_fields,
                complete_original_CSV_pins=original_pins,owned_manifest=pin(T/'asset-manifest.json'),
                owned_entries=937,external_original_entries=len(manifest['external_originals']),
                full_contract=pin(cp),complete_root_fields=root,
                complete_presentations=11535,full_source_groups=10062,source_authorities=108,
                native_printed_to_combined_county_candidate_controls=county_candidate_checks,
                complete_original_turnout_controls=turnout_controls,
                current_literal_registration=dict(rows=108,A=A,I=I,definitions_not_expanded=True,
                                                  separate_printed_footer=registration_footer,
                                                  complete_original_source=pin(S/r['path'])),
                primary_denominator=5592368,minimum80=5540,preceding_votes=4473789,crossing_cumulative=4474312,
                top15_votes=29572,remainder_count=4522,remainder_votes=1118056,
                source_key_schema='Exact original authority ID and literal precinct; turnout percent-encoded keys map by original fields, not normalization or physical/current geography.',
                unavailable_after_observed_zero_order_adapter='Canonical order sorts four unavailable named pools after all observed numeric printed sums including zero. Initial arithmetic known-sum ordering in earlier captured proof treated the empty aggregate as0 but did not impute source cells. Positive order, prefix and all candidate values unchanged.',
                complete_ordered_original_group_digests=ordered,
                coordinator_dispatch_accepted=False,current_geography_approved=False,legal_native_writein_robustness=False)
    p=D/'coordinator-turnout-final-review.json';b=(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode()
    assert len(b)<40_000_000
    p.write_bytes(b)
    print(json.dumps(dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b),original_fields=checked_fields,owned_files=937)))


if __name__=='__main__':
    main()

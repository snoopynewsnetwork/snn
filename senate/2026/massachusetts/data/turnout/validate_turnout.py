#!/usr/bin/env python3
"""Independent offline checks against the full original CSV entities, not summaries."""
import collections,csv,gzip,hashlib,io,json,math,re,runpy,sys
from fractions import Fraction
from pathlib import Path
from urllib.parse import unquote,urlparse
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;STATE=D.parent.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def read(n):return json.loads((D/n).read_bytes())
def key(t):return json.dumps(t,ensure_ascii=False,separators=(',',':'))
def gz(n):return json.loads(gzip.decompress((D/n).read_bytes()))
def count(s):
    assert s!='','Missing numeric source value is not zero.'
    assert re.fullmatch(r'\d{1,3}(?:,\d{3})*|\d+',s)
    return int(s.replace(',',''))
def same_rows(expected,observed):
    assert len(observed)==len(expected)
    assert len({tuple(r[:3])for r in observed})==len(observed)
    assert observed==expected
def main(check_manifest=True,write_result=False):
    checks={};sources={p['id']:p for p in read('source/shared-originals.json')};original={};extractions={};raw_hashes={}
    for sid,p in sources.items():
        z=(STATE/p['immutable_body_path']).read_bytes();b=gzip.decompress(z)
        assert sha(z)==p['stored_sha256']and sha(b)==p['raw_sha256']and len(b)==p['bytes']
        assert len(z)<40_000_000;raw_hashes[sid]=sha(b)
        if sid.endswith('-csv'):original[sid]=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
    checks['immutable_shared_original_entities']=len(sources)
    all_comparisons=all_positions=0;native_counts={};names={};widths={}
    for tag,prefix in [('2024-senate','sos-2024-senate'),('2020-senate','sos-observed-2020-senate'),('2022-governor','sos-observed-2022-governor'),('2024-president','sos-observed-2024-president')]:
        m=original[prefix+'-municipal-csv'];n=original[prefix+'-precinct-csv'];x=gz('extract/'+tag+'-original-extraction.json.gz');extractions[tag]=x
        assert x['all_original_csv_rows']=={'municipal':m,'precinct':n}
        assert m[0][3:]==n[0][3:]and m[1]==n[1]and m[-1]==n[-1]
        assert len(m)==354 and m[-1][0]=='TOTALS'and n[-1][0]=='TOTALS'
        reportcontrol=next(v for v in read('controls.json')if v['contest']==tag)
        assert reportcontrol['columns']==m[0][3:]and reportcontrol['state_control']==[count(v)for v in m[-1][3:]]
        assert reportcontrol['html_candidate_cards']==x['html_candidate_cards']
        assert reportcontrol['named_source_votes']==sum(reportcontrol['state_control'][:-3])and reportcontrol['named_plus_AllOthers_votes']==sum(reportcontrol['state_control'][:-2])
        width=len(m[0])-3;widths[tag]=width
        state=[count(v)for v in m[-1][3:]];parents={};aggregates=collections.defaultdict(lambda:[0]*width);seen=set()
        for r in m[2:-1]:
            assert r[0]not in parents and r[1:3]==['',''];parents[r[0]]=[count(v)for v in r[3:]]
        assert len(parents)==351
        same_rows(n[2:-1],[r['raw_row']for r in x['native_contexts']])
        for o,raw,ordinal in zip(x['native_contexts'],n[2:-1],range(3,len(n))):
            assert o['literal_tuple']==raw[:3]and o['native_key']==key(raw[:3])and o['csv_record_ordinal']==ordinal
            assert o['native_key']not in seen;seen.add(o['native_key']);v=[count(a)for a in raw[3:]]
            assert len(v)==width and sum(v[:-1])==v[-1]and o['values']==v
            assert o['named_source_votes']==sum(v[:-3])and o['named_plus_AllOthers_votes']==sum(v[:-2])
            assert [o['AllOthers'],o['Blanks'],o['TotalVotesCast']]==v[-3:]
            for f in ['method','undervotes','overvotes','registration','municipal_fips','numeric_native_id','administrative_identity']:assert o[f]is None
            for i,a in enumerate(v):aggregates[raw[0]][i]+=a
        assert dict(aggregates)==parents
        assert [sum(v[i]for v in parents.values())for i in range(width)]==state==x['state_control']
        positions=gz('extract/'+tag+'-numeric-positions.json.gz');assert len(positions)==(len(m)-2+len(n)-2)*width
        for v in positions:
            source=original[v['source_id']];r=v['csv_record_ordinal'];col=v['csv_column_ordinal']
            assert source[r-1][col-1]==v['raw_value']and count(v['raw_value'])==v['value']and source[0][col-1]==v['literal_column']
        assert len({(v['source_id'],v['csv_record_ordinal'],v['csv_column_ordinal'])for v in positions})==len(positions)
        footer=next(r for r in x['html_source_table_rows']if 'total'in r['attributes'].get('class','').split())
        assert [count(v)for v in footer['cells'][1:]]==state
        county=[r for r in x['html_source_table_rows']if 'm_item'in r['attributes'].get('class','').split()];assert len(county)==14
        diff=[sum(count(r['cells'][i+1])for r in county)-state[i]for i in range(width)]
        assert diff==x['html_county_sum_minus_state_footer']==([-3189,90,-39,-12,-13,-3163]if tag=='2022-governor'else [0]*width)
        all_comparisons+=351*width;all_positions+=len(positions);native_counts[tag]=len(n)-3;names[tag]=set(parents)
    assert native_counts=={'2024-senate':2394,'2020-senate':2173,'2022-governor':2390,'2024-president':2394}
    assert all(v==names['2024-senate']for v in names.values())
    assert all_comparisons==9828 and all_positions==75566
    checks.update(original_native_counts=native_counts,municipal_native_field_comparisons=all_comparisons,exact_source_numeric_positions=all_positions,all_four_HTML_state_controls=True,county_HTML_2022_conflict_preserved=True)
    unallocated=[o for o in extractions['2022-governor']['native_contexts']if o['literal_tuple'][1:]==['','']];assert len(unallocated)==118
    totals=collections.Counter(o['literal_tuple'][0]for o in extractions['2022-governor']['native_contexts']);assert all(totals[o['literal_tuple'][0]]==1 for o in unallocated)
    checks['unallocated_2022_municipal_contexts']=118
    summaries=read('ranking-summaries.json');expect_orders={};weights={}
    for tag,x in extractions.items():
        for scope,rows in [('native',x['native_contexts']),('municipal',x['municipalities'])]:
            for field in ['named_source_votes','named_plus_AllOthers_votes','TotalVotesCast']:
                label=f'{tag}-{scope}-{field}';sorted_rows=sorted(rows,key=lambda r:(-r[field],tuple(r['literal_tuple']),r['csv_record_ordinal']));expect_orders[label]=sorted_rows
                with (D/'orders'/f'{label}.csv').open(newline='')as f:order=list(csv.DictReader(f))
                assert [r['native_key']for r in order]==[r['native_key']for r in sorted_rows]
                T=sum(r[field]for r in sorted_rows);cum=0;cross=None
                assert sum(Fraction(r[field],T)for r in sorted_rows)==1
                for i,(r,o)in enumerate(zip(sorted_rows,order),1):
                    before=cum;cum+=r[field]
                    assert int(o['rank'])==i and int(o['votes'])==r[field]and int(o['cumulative_votes'])==cum
                    assert o['share_exact']==str(Fraction(r[field],T))and o['cumulative_share_exact']==str(Fraction(cum,T))
                    assert o['in_top15']==str(i<=15)and o['in_minimum80']==str(5*before<4*T)
                    assert math.isclose(float(o['weight']),r[field]/T,rel_tol=1e-15,abs_tol=1e-18)
                    if 5*cum>=4*T and cross is None:cross=i
                z=summaries[label];assert z['units']==len(rows)and z['statewide_votes']==T
                C=sum(r[field]for r in sorted_rows[:cross]);B=sum(r[field]for r in sorted_rows[:cross-1])
                assert z['minimum80_count']==cross and z['minimum80_votes']==C and z['preceding_count']==cross-1 and z['preceding_votes']==B
                assert z['top15_votes']==sum(r[field]for r in sorted_rows[:15])
                assert z['crossing_key']==sorted_rows[cross-1]['native_key']and z['crossing_votes']==sorted_rows[cross-1][field]
                assert z['remainder_count']==len(rows)-cross and z['remainder_votes']==T-C and 5*B<4*T<=5*C
                weights[label]='1 (exact rational sum)'
    checks['complete_orders_checked']=len(expect_orders);checks['weights']=weights
    contract=read('priority-set.json');z=contract['summary'];assert z==summaries['2024-senate-native-named_source_votes']
    expected=expect_orders['2024-senate-native-named_source_votes'];keys=[r['native_key']for r in expected];N=z['minimum80_count'];T=z['statewide_votes']
    assert len(contract['all_unit_order'])==2394 and [r['source_record']for r in contract['all_unit_order']]==expected
    assert [r['native_key']for r in contract['all_unit_order']]==keys
    assert contract['ordered_priority_keys']==keys[:N]and contract['ordered_top15_keys']==keys[:15]and contract['ordered_remainder_keys']==keys[N:]
    assert contract['coordinator_accepted']is False and contract['current_geometry_approved']is False
    assert contract['independent_peer_agreement']is True
    audit=runpy.run_path(str(D/'audit_peer.py'))
    agreement=audit['main'](write_result=False);assert agreement==read('peer-audit/comparison.json')
    assert agreement['status']=='pass_bounded_reciprocal_actual_final_baseline_capture'
    assert contract['bounded_peer_audit']['sha256']==sha((D/'peer-audit/comparison.json').read_bytes())
    old=audit['Capture'](D/'peer-review-freeze/original-first-v1/snapshot-manifest.json').json('data/turnout/priority-set.json')
    projection=dict(contract);projection.pop('bounded_peer_audit');projection['independent_peer_agreement']=False;projection['review_status']=old['review_status'];assert projection==old
    checks['bounded_reciprocal_full_objects_orders_and_metadata_only_contract_changes']=True
    checks['original_first_count_order_CSV_bytes_unchanged']=True
    for row,source in zip(contract['all_unit_order'],expected):
        i=row['rank'];assert row['votes']==source['named_source_votes']and row['cumulative_votes']==sum(r['named_source_votes']for r in expected[:i])
        assert row['in_top15']==(i<=15)and row['in_minimum80']==(i<=N)
    for label,detail in contract['sensitivity_orders'].items():
        assert detail['summary']==summaries[label]
        order=detail['all_unit_order'];field=summaries[label]['field'];ref=expect_orders[label]
        assert [r['native_key']for r in order]==[r['native_key']for r in ref]
        assert [r['votes']for r in order]==[r[field]for r in ref]
    impacts=read('sensitivity-impacts.json')
    for label,impact in impacts.items():
        ref=expect_orders[label];field=summaries[label]['field'];otherkeys=[r['native_key']for r in ref];M=summaries[label]['minimum80_count']
        assert impact['positions_changed']==sum(a!=b for a,b in zip(keys,otherkeys))
        assert impact['priority_added']==[k for k in otherkeys[:M]if k not in set(keys[:N])]
        assert impact['priority_removed']==[k for k in keys[:N]if k not in set(otherkeys[:M])]
        assert impact['primary_priority_votes_under_sensitivity']==sum(r[field]for r in expected[:N])
    maps=contract['all_parent_child_maps'];assert len(maps)==351 and len({m['municipal_key']for m in maps})==351
    used=[]
    for m in maps:
        children=[r for r in extractions['2024-senate']['native_contexts']if r['literal_tuple'][0]==m['literal_city_town']]
        assert m['native_keys_source_order']==[r['native_key']for r in children]
        assert m['native_keys_priority_order']==[k for k in keys if k in set(m['native_keys_source_order'])]
        assert m['values']==[sum(r['values'][i]for r in children)for i in range(5)]and m['native_context_count']==len(children)
        used.extend(m['native_keys_source_order'])
    assert len(used)==len(set(used))==2394 and set(used)==set(keys)
    assert contract['municipal_sensitivity']['summary']==summaries['2024-senate-municipal-named_source_votes']and contract['municipal_sensitivity']['dispatch_substitute']is False
    with (STATE/'data/county-turnout.csv').open(newline='')as f:compat=list(csv.DictReader(f))
    assert len(compat)==2394 and [r['native_key']for r in compat]==keys
    for r,o in zip(compat,expected):
        assert [r['city_town'],r['ward'],r['precinct']]==o['literal_tuple']
        assert [int(r[f])for f in ['Warren','Deaton','AllOthers','Blanks','source_TotalVotesCast']]==o['values']
        assert r['municipal_fips']==r['source_numeric_native_id']==r['separate_ballots_cast']==r['undervotes']==r['overvotes']==r['registered_voters']==r['method']==''
        assert r['source_body_sha256']==contract['source_body_sha256']==raw_hashes['sos-2024-senate-precinct-csv']
    for name,selection in [('ordered-priority-native.csv',compat[:N]),('ordered-remainder-native.csv',compat[N:])]:
        with (D/name).open(newline='')as f:assert list(csv.DictReader(f))==selection
    checks.update(primary_native_order_and_remainder=True,complete_disjoint_parent_child_maps=351,compatibility_CSV_native_rows=2394)
    bounds=read('writein-scope-bounds.json');C=z['minimum80_votes'];B=z['preceding_votes']
    assert bounds['AllOthers_inside_fixed_priority']==sum(r['AllOthers']for r in expected[:N])==4375
    assert bounds['AllOthers_outside_fixed_priority']==sum(r['AllOthers']for r in expected[N:])==1846
    assert bounds['minimum_additional_eligible_wholly_outside_breaks_fixed_priority80']==955 and 5*C>=4*(T+954)and 5*C<4*(T+955)
    assert bounds['minimum_additional_eligible_wholly_inside_fixed_preceding_reaches80']==2277 and 5*(B+2276)<4*(T+2276)and 5*(B+2277)>=4*(T+2277)
    alt=read('alternative-order-presentation.json');a=sorted(expected,key=lambda r:(-r['named_source_votes'],r['csv_record_ordinal']))
    assert alt['full_ordered_keys']==[r['native_key']for r in a]and alt['minimum80_votes']==sum(r['named_source_votes']for r in a[:N])==C
    checks['conditional_writein_bounds_independently_verified']=True;checks['alternative_tie_order_verified']=True
    for scope in ['municipal','native']:
        r=read('source/current-senate-'+scope+'-csv.receipt.json');zipped=(STATE/r['body_path']).read_bytes();raw=gzip.decompress(zipped)
        assert sha(zipped)==r['stored_sha256']and sha(raw)==r['raw_sha256']and len(raw)==r['raw_bytes']
        assert r['raw_sha256']==raw_hashes['sos-2024-senate-'+('municipal'if scope=='municipal'else 'precinct')+'-csv']
    checks['fresh_2024_CSV_entities_match_frozen_originals']=True
    stats=read('statistics-controls.json');assert [(r['year'],r['registration'],r['PD43_minus_turnout_table'],r['PD43_minus_method_index'])for r in stats]==[(2020,4812909,33,33),(2022,4884076,0,0),(2024,5142343,0,64)]
    assert all(r['numeric_method_counts']is None and r['municipal_registration_counts']is None and r['native_registration_counts']is None for r in stats)
    replay=read('preflight-replay/coordinator-primary-preflight.json');assert replay['state_controls']==extractions['2024-senate']['state_control']and replay['municipal_native_control_comparisons']==1755
    checks.update(statewide_statistics_scope_and_differences=True,shared_primary_preflight_replayed_into_owned_path=True)
    build=runpy.run_path(str(D/'build_turnout.py'));tests=[]
    schedule_receipt=read('source/2022-senate-search.receipt.json');assert schedule_receipt['status']==200
    schedule=build['HTML'](gzip.decompress((STATE/schedule_receipt['body_path']).read_bytes())).root
    assert len(list(schedule.descendants('tr',cls='election_item')))==0
    checks['observed_public_form_2022_Senate_General_result_rows']=0
    assert build['number']('')is None and build['number']('0')==0;tests.append('missing numeric versus printed zero remains distinct')
    toy=[dict(native_key=key(['Town','-',v]),literal_tuple=['Town','-',v],csv_record_ordinal=i,named_source_votes=w)for i,(v,w)in enumerate([('2',40),('10',40),('A',20)],3)]
    order,s=build['rank'](toy,'named_source_votes');assert [r['literal_tuple'][2]for r in order]==['10','2','A']and s['minimum80_count']==2 and s['minimum80_votes']==80;tests.append('lexical10-before2, letter retained, exact80 equality')
    zero=[dict(toy[0],named_source_votes=0)]
    try:build['rank'](zero,'named_source_votes')
    except AssertionError:tests.append('zero-denominator rank rejected')
    else:raise AssertionError('zero denominator accepted')
    raw=original['sos-2024-senate-precinct-csv'][2:-1]
    for label,mutation in [('missing native context',raw[:-1]),('duplicate native context',raw+[raw[0]])]:
        try:same_rows(raw,mutation)
        except AssertionError:tests.append(label+' rejected')
        else:raise AssertionError(label)
    altered=[r[:]for r in raw];altered[0][3],altered[1][3]=altered[1][3],altered[0][3]
    assert sum(count(r[3])for r in altered)==sum(count(r[3])for r in raw)
    try:same_rows(raw,altered)
    except AssertionError:tests.append('local candidate swap preserving statewide candidate total rejected')
    else:raise AssertionError('local mutation passed')
    checks['meaningful_calculator_and_input_tests']=tests
    manifest=read('asset-manifest.json');seenpaths=set()
    expectedpaths={p.relative_to(STATE).as_posix()for p in D.rglob('*')if p.is_file()and p!=D/'asset-manifest.json'}|{'turnout.md','data/county-turnout.csv'}
    if check_manifest:
        for asset in manifest['owned_assets']:
            p=STATE/asset['path'];b=p.read_bytes();assert p.is_file()and len(b)==asset['bytes']and len(b)<40_000_000 and sha(b)==asset['sha256'];seenpaths.add(asset['path'])
        assert seenpaths==expectedpaths and len(seenpaths)==len(manifest['owned_assets'])
        assert manifest['hash_cycle_exclusions']==['asset-manifest.json']
        seal=read('final-seal.json')
        assert 'asset-manifest.json'not in seal['sealed_files']and 'asset_manifest_sha256'not in read('validation.json')
        for path,pin in seal['sealed_files'].items():
            b=(D/path).read_bytes();assert len(b)==pin['bytes']and sha(b)==pin['sha256']
    for p in D.rglob('*'):assert p.name not in ['__pycache__','node_modules','.cache'],'No retained cache/dependency directories.'
    for asset in manifest['reused_originals']:
        p=STATE/asset['path'];z=p.read_bytes();raw=gzip.decompress(z)
        assert len(z)==asset['stored_bytes']and sha(z)==asset['stored_sha256']and len(raw)==asset['raw_bytes']and sha(raw)==asset['raw_sha256']
    for r in D.glob('source/*.receipt.json'):
        v=json.loads(r.read_bytes())
        if 'body_path'in v:
            z=(STATE/v['body_path']).read_bytes();raw=gzip.decompress(z)
            assert sha(z)==v['stored_sha256']and len(z)==v['stored_bytes']and sha(raw)==v['raw_sha256']and len(raw)==v['raw_bytes']
    local_links=0
    for p in [STATE/'turnout.md',*D.rglob('*.md')]:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',p.read_text()):
            target=target.split('#',1)[0].strip('<>')
            if not target or urlparse(target).scheme:continue
            assert (p.parent/unquote(target)).resolve().exists(),(str(p),target);local_links+=1
    checks.update(asset_membership_rule='Every owned file except only current asset-manifest.json; seal.py performs final read-only membership/hash verification after writing manifest.',owned_asset_count=len(expectedpaths),reused_original_entities=len(manifest['reused_originals']),strict_asset_byte_limit=40_000_000,relative_links_checked=local_links)
    result=dict(status='pass_original_source_and_bounded_reciprocal_offline_QA_with_explicit_external_gaps',checks=checks,independent_peer_agreement=contract['independent_peer_agreement'],coordinator_accepted=False,limitations=['Reciprocal scope is exact captured final baseline versus own original-first; no later-current peer equality or coordinator acceptance.','Generic AllOthers is not allocated to eligible/named write-ins; conditional bounds only.','Raw statistical XLSX/PDF downloads blocked; local method/registration controls and original bytes unavailable; baseline supplemental browser347 observations not adopted.','Current/native geometry, method/admin splits, live cadence and feed approval remain external.'],primary_contract_sha256=sha((D/'priority-set.json').read_bytes()),peer_comparison_sha256=sha((D/'peer-audit/comparison.json').read_bytes()))
    if write_result:(D/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    else:assert result==read('validation.json'),'Saved validation does not match current complete offline QA.'
    print(json.dumps(dict(status=result['status'],native_counts=native_counts,field_comparisons=all_comparisons,positions=all_positions,orders=24,tests=tests,links=local_links,peer_agreement=result['independent_peer_agreement'])))
    return result
if __name__=='__main__':
    prepare='--prepare-seal'in sys.argv
    main(check_manifest=not prepare,write_result=prepare)

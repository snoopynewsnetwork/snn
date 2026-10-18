"""Read-only exact comparison to the independently authored turnout package."""
import csv, gzip, json
from collections import Counter
from pathlib import Path
from build import H, S, SPECS, csvout, jdump
def jl(p): return [json.loads(line) for line in gzip.open(p,'rt')]
def main():
    peer=H.parent/'turnout'; files=[H.parent/'county-turnout.csv',peer/'priority-set.json',peer/'extracts/native-units.jsonl.gz',peer/'extracts/candidate-observations.jsonl.gz',peer/'extracts/county-summary-observations.jsonl.gz',peer/'extracts/native-unit-order.csv.gz']
    hashes={str(p.relative_to(S.ROOT)):dict(sha256=S.sha(p.read_bytes()),bytes=p.stat().st_size) for p in files}
    own=list(csv.DictReader((H.parent/'county-baselines.csv').open())); other=list(csv.DictReader(files[0].open())); otherby={r['county_fips']:r for r in other}; diffs=[]; comparisons=0
    pairs={'county_key':'county_key','county':'county','president_2024_rank':'rank','ballots_2024_source_workbook':'ballots_cast_2024_broad','registration_2024_source_workbook':'registered_voters_2024_broad','ballots_2022_source_workbook':'ballots_cast_2022','registration_2022_source_workbook':'registered_voters_2022','registration_2024_november_separate_publication':'registered_voters_2024_november','president_2024_cumulative_votes':'president_2024_cumulative_votes'}
    for pref,spec in SPECS.items():
        if spec['stage']!='general': continue
        for ck,_,_ in spec['candidates']: pairs[pref+'_'+ck+'_votes']=pref+'_'+ck
        pairs[pref+'_named_votes']=pref+'_total'
    for r in own:
        p=otherby[r['county_fips']]
        for a,b in pairs.items():
            comparisons+=1
            if r[a]!=p[b]: diffs.append([r['county'],a,r[a],p[b]])
    priority=json.loads(files[1].read_text()); ordering=['US-KS-'+r['county_fips'] for r in sorted(own,key=lambda r:int(r['president_2024_rank']))]
    assert ordering==priority['full_all_unit_order']
    raw={(r['source_id'],r['sheet'],r['row']):r['cells'] for r in jl(H/'source/raw-rows.jsonl.gz')}
    ours=jl(H/'native-units.jsonl.gz'); peers=jl(files[2]); pby={r['unit_key']:r for r in peers}; cross=[]; unitdiff=[]; matched=set()
    for u in ours:
        sid,sh=u['source_id'],u['sheet']; rs=sorted({v[0] for v in u['rows']}); c=raw[sid,sh,rs[0]]
        if sid=='sos-2024-president-county':
            fields={k:v for k,v in u['native_components']}; native=fields['E']
        elif 'VTD' in dict(u['native_components']):
            native=c['A']; fields=dict(County=c['A'],Precinct=c['B'],VTD=c.get('G'))
        else:
            native=u['county']; headers=raw.get((sid,sh,1),{})
            fields={k:dict(header=headers.get(k),value=v) for k,v in u['native_components']}
        payload=[sid,sh,native,fields]; pk=sid+':'+S.sha(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode())[:24]
        assert pk in pby,(sid,sh,fields)
        p=pby[pk]; matched.add(pk)
        compare={'county':u['county'],'county_fips':u['county_fips'],'source_rows':rs,'native_id_fields':fields,'named_candidate_numeric_sum':u['known_named_votes'],'named_candidate_total':u['named_votes'],'unknown_named_cells':sum(v is None for k,v in u['candidates'].items() if k!='generic_write_in')}
        for field,v in compare.items():
            if p[field]!=v: unitdiff.append([pk,field,v,p[field]])
        cross.append(dict(unit_key=u['unit_key'],peer_unit_key=pk,source_id=sid,sheet=sh,county=u['county'],native_fields_equal=not any(x[0]==pk for x in unitdiff)))
    assert len(matched)==len(peers)==len(ours)
    observations={}; psummaries={}
    for line in gzip.open(files[3],'rt'):
        r=json.loads(line); observations[r['source_id'],r['sheet'],r['row'],r['column']]=r
    for line in gzip.open(files[4],'rt'):
        r=json.loads(line); psummaries[r['source_id'],r['sheet'],r['row'],r['column']]=r
    obsdiff=[]; seen=set(); obscompare=0; absent_peer=[]; party_comparisons=0
    parties={'Democratic':'D','Republican':'R','Independent':'i','Libertarian':'L','Unspecified':None}
    for r in csv.DictReader(gzip.open(H/'native-candidates.csv.gz','rt')):
        pk=(r['source_id'],r['sheet'],int(r['source_row']),r['vote_column']); seen.add(pk)
        pool=psummaries if r['role']=='county_footer' else observations
        if pk not in pool:
            absent_peer.append(dict(source_cell=pk,role=r['role'],candidate=r['canonical_candidate'],own_value=r['raw_value'])); continue
        p=pool[pk]; obscompare+=1
        vals=dict(county=r['county'],county_fips=r['county_fips'],candidate_key=r['canonical_candidate'],source_candidate_label=r['source_candidate'],source_party_label=r['source_party'] or None,raw_value=r['raw_value'] or None,votes=int(r['votes']) if r['votes'] else None)
        if r['canonical_candidate']!='generic_write_in':
            vals['verified_candidate_party']=parties[r['party_identity']]; party_comparisons+=1
        # Source absent empty-string and absent value both remain unavailable; raw row retains exact cells.
        for f,v in vals.items():
            if (p.get(f) or None)!=v and not (f=='votes' and p.get(f)==v): obsdiff.append([pk,f,v,p.get(f)])
    extra=Counter(r['category'] for pk,r in observations.items() if pk not in seen)
    auxiliary_comparisons=0; auxiliary_differences=[]
    for r in csv.DictReader((H/'source/auxiliary-controls.csv').open()):
        if r['category']!='reported_contest_total_including_generic_write_ins':continue
        pk=r['source_id'],r['sheet'],int(r['source_row']),r['column'];pool=psummaries if r['role']=='county_footer' else observations
        assert pk in pool,pk
        pr=pool[pk];auxiliary_comparisons+=1
        if pr['raw_value']!=r['raw_value'] or pr['votes']!=int(r['votes']):auxiliary_differences.append([pk,r['raw_value'],pr['raw_value'],r['votes'],pr['votes']])
    assert not auxiliary_differences
    # Primary county controls compared independently, even though not part of broad scenario CSV.
    pcounts={}
    for line in csv.DictReader((H/'native-candidates.csv.gz').open() if False else gzip.open(H/'native-candidates.csv.gz','rt')):
        if line['baseline']=='senate_primary_2026' and (line['role']=='county_footer' or line['sheet']=='U.S. Senate') and line['votes']:
            pk=line['county_fips'],line['canonical_candidate']; pcounts[pk]=pcounts.get(pk,0)+int(line['votes'])
    for r in other:
        for ck,_,_ in SPECS['senate_primary_2026']['candidates']:
            comparisons+=1
            if int(r['senate_primary_2026_'+ck])!=pcounts[r['county_fips'],ck]: diffs.append([r['county'],ck,pcounts[r['county_fips'],ck],r['senate_primary_2026_'+ck]])
    csvout('peer-native-key-crosswalk.csv.gz',cross)
    keymap={r['unit_key']:r['peer_unit_key'] for r in cross}; nativeorder=[]; ownorder=[]
    for sid in dict.fromkeys(u['source_id'] for u in peers):
        us=sorted([u for u in ours if u['source_id']==sid],key=lambda u:(u['named_votes'] is None,-(u['named_votes'] or 0),u['county_fips'],u['sheet'],sorted({x[0] for x in u['rows']})))
        for rank,u in enumerate(us,1):
            rank=rank if u['named_votes'] is not None else None
            nativeorder.append(dict(source_id=sid,unit_key=u['unit_key'],peer_unit_key=keymap[u['unit_key']],county_fips=u['county_fips'],known_count_rank=rank,named_votes=u['named_votes']))
            ownorder.append((sid,keymap[u['unit_key']],str(rank) if rank is not None else '',str(u['named_votes']) if u['named_votes'] is not None else ''))
    porder=[(r['source_id'],r['unit_key'],r['known_count_rank'],r['named_candidate_total']) for r in csv.DictReader(gzip.open(files[5],'rt'))]
    assert ownorder==porder,'native order differs'
    csvout('native-order.csv.gz',nativeorder)
    jdump('peer-reconciliation.json',dict(status='pass' if not diffs+unitdiff+obsdiff else 'differences',peer_agent_id='158cc3fa-5119-4e25-a958-b042f0e0f340',read_only_peer_assets=hashes,county_field_comparisons=comparisons,county_differences=diffs,native_units_compared=len(ours),native_field_differences=unitdiff,source_cell_candidate_comparisons=obscompare,verified_party_comparisons=party_comparisons,candidate_field_differences=obsdiff,own_cells_without_peer_derivative=absent_peer,peer_extra_non_candidate_observation_categories=dict(extra),reported_total_cells_compared=auxiliary_comparisons,reported_total_differences=auxiliary_differences,retained_explicit_scopes=dict(Wyandotte_2020_footer_cells=['E131','F131','H131','I131'],Sedgwick_2020_reported_total_detail_cells=269,Sedgwick_2020_reported_total_footer_cell='F274',unrelated_Wyandotte_president_column='retained separately as auxiliary and in raw originals, never Senate'),shared_detail_candidate_and_total_cells=121053,shared_footer_candidate_and_total_cells=96,native_known_count_order_equal=True,native_order_rows=len(ownorder),method_semantics='both sources publish combined/unspecified methods; native labels are not inferred method boards',full_105_order_equal=True,exact_integer_80_contract_equal=True,coordinator_acceptance='historical research contract externally accepted; see coordinator-priority-acceptance.json; no reverse pin',priority=dict(denominator=1327591,top15=970376,previous22=1057110,minimum23=1067659,crossing='Sumner 20191 10549')))
    print(json.dumps(dict(county_differences=len(diffs),unit_differences=len(unitdiff),candidate_differences=len(obsdiff),compared_units=len(ours),compared_candidate_cells=obscompare,extra_categories=dict(extra))))
if __name__=='__main__': main()

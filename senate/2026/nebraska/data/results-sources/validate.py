#!/usr/bin/env python3
"""Meaningful offline audit; read-only unless --write-validation explicitly set.
No producer parser, mutable news ledger, coordinator aggregate, or network.
"""
import collections,copy,csv,datetime,gzip,json,pathlib,re,sys,urllib.parse
sys.dont_write_bytecode=True
from acquire import D,sha,readj,body,decoded
from build import sem,leaf_count,pin
S=D.parent.parent
def resolve(v,ptr):
    if ptr=='':return v
    for key in ptr.lstrip('/').split('/'):
        key=key.replace('~1','/').replace('~0','~');v=v[int(key)]if isinstance(v,list)else v[key]
    return v
def main(write=False):
    checks=[];frozen=readj(D/'frozen-inputs.json');c=readj(S/frozen['contract']['path']);checkedpins=0;rawentities=0;refcount=0
    def verify_pin(r):
        nonlocal checkedpins
        p=S/r['path'];assert p.is_file(),r['path'];b=p.read_bytes();assert len(b)==r['bytes']and sha(b)==r['sha256'],r['path'];assert len(b)<40000000,r['path'];checkedpins+=1
    verify_pin(frozen['contract']);assert frozen['contract']==dict(path='data/turnout/priority-set.json',bytes=3889923,sha256='125fef1c2e13ff4e0464ac5e75e82ec54c9ea5e675b42da7586c4ccfd90d5891')
    for r in frozen['verified_inputs']:verify_pin(r)
    assert not any(r['path']=='data/news/manifest.json'for r in frozen['verified_inputs'])
    for r in frozen['exact_reconstructed_legacy_aggregate_pins']:
        old=readj(S/'data/turnout/source/shared-news-ledger.json');extra=readj(D/'optional-news-receipts.json')['append6_observations'];b=(json.dumps(old+extra,indent=2)+'\n').encode();assert len(b)==r['bytes']and sha(b)==r['sha256']and not r['mutable_aggregate_file_dependency']
    # Read external authority by path only, never introduce reverse acceptance pin.
    a=readj(S/'data/coordinator-priority-acceptance.json');assert a['status']=='accepted_historical_named_canvass_dispatch_only'
    for k in ['ordered_full_keys','ordered_priority_keys','ordered_remainder_keys','parent_full_child_map','parent_priority_child_map','child_parent_map']:assert c[k]==a[k]
    assert c['all93_parents']==a['all93_parent_objects'];assert not c['coordinator_acceptance']and not c['current_geography_approval']
    checks.append('external_path_authority_and_all_frozen_report_review_manifest_validation_proof_original_pins')
    receipts={p.stem:readj(p)for p in (D/'receipts').glob('*.json')};storedpaths=[]
    for sid,r in receipts.items():
        assert sid==r['id']and r['requested_url'].startswith(('https:','http:'));datetime.datetime.fromisoformat(r['retrieved_utc']);datetime.datetime.fromisoformat(r['finished_utc']);assert r['parent_source_id']is None or r['parent_source_id']in receipts,(sid,r['parent_source_id'])
        if r['stored_parts']:
            assert r['entity_complete']and r['http_status']is not None;chunks=[]
            for part in r['stored_parts']:
                p=D/part['path'];b=p.read_bytes();assert len(b)==part['bytes']<40000000 and sha(b)==part['sha256'];chunks.append(b);storedpaths.append(p.resolve())
            raw=gzip.decompress(b''.join(chunks));assert len(raw)==r['raw_bytes']and sha(raw)==r['raw_sha256'];assert raw==body(sid);rawentities+=1
            assert isinstance(r['headers'],list)and isinstance(r['redirects'],list)
        else:assert not r['entity_complete']and r['http_status']is None and r['error']
    originals={p.resolve()for p in (D/'originals').iterdir()if p.is_file()};assert set(storedpaths)==originals and len(storedpaths)==len(set(storedpaths))
    graph=readj(D/'source-reference-graph.json');assert graph['own_receipt_ids']==sorted(receipts)and not graph['mutable_news_manifest_dependency'];verify_pin(graph['historical_ledger']);ledger=readj(S/graph['historical_ledger']['path']);assert len(ledger)==233
    for i,rr in enumerate(graph['historical_receipts']):
        assert resolve(ledger,rr['receipt_reference']['json_pointer'])==ledger[i]and rr['source_id']==ledger[i]['id']
    for r in ledger+readj(D/'optional-news-receipts.json')['append6_observations']:
        if r.get('asset'):
            z=(S/'data/news'/r['asset']).read_bytes();raw=gzip.decompress(z);assert sha(z)==r['stored_sha256']and len(raw)==r['bytes']and sha(raw)==r['raw_sha256'];rawentities+=1
    checks.append('all_own_and_individual_shared_originals_full_headers_redirects_errors_hashes_sizes_reconstruction')
    p=readj(D/'preservation-index.json')
    def verify_ref(r):
        nonlocal refcount
        assert r['file']==frozen['contract']and r['recursive_all_fields'];v=resolve(c,r['json_pointer']);assert sem(v)==r['semantic_sha256']and leaf_count(v)==r['scalar_leaves'];refcount+=1;return v
    assert verify_ref(p['complete_root_reference'])==c;assert set(p['complete_fields'])==set(c)
    for k,r in p['complete_fields'].items():assert verify_ref(r)==c[k]
    for k,rr in p['arrays'].items():assert [verify_ref(r)for r in rr]==c[k]
    assert [len(c[k])for k in ['constituents','administrative_and_partial_alternates','additional_native_source_contexts','unavailable_cases','additional_administrative_contexts']]==[1326,329,14,2,2]
    # Prove the semantic check detects non-vote-field/null loss, not only key/votes.
    tamper=copy.deepcopy(c['constituents'][0]);tamper['generic_writeins']=0;assert sem(tamper)!=sem(c['constituents'][0])
    checks.append('complete_recursive_object_field_null_preservation_and_nonvote_tamper_detection')
    units=c['constituents'];keys=[r['key']for r in units];assert len(keys)==len(set(keys))==1326;assert keys==c['ordered_full_keys']
    assert keys==[r['key']for r in sorted(units,key=lambda r:(-sum(r['candidate_values']),r['key']))]
    assert c['ordered_priority_keys']==keys[:765]and c['ordered_remainder_keys']==keys[765:];assert [sum(x['candidate_values'][i]for x in units)for i in [0,1]]==[585103,349902]
    assert sum(sum(x['candidate_values'])for x in units[:765])==748190 and sum(sum(x['candidate_values'])for x in units[:764])==747645
    assert 5*748190>=4*935005 and 5*747645<4*935005;assert sum(sum(x['candidate_values'])for x in units[:15])==26773 and sum(sum(x['candidate_values'])for x in units[765:])==186815
    assert 5*748190>=4*(935005+232)and 5*748190<4*(935005+233);assert 5*(747645+1794)<4*(935005+1794)and 5*(747645+1795)>=4*(935005+1795)
    assert len(c['all93_parents'])==93;assert len([r for r in c['all93_parents']if r['priority_child_keys']])==58
    for p0 in c['all93_parents']:
        pk=p0['parent_key'];assert p0['full_child_keys']==c['parent_full_child_map'][pk]and p0['priority_child_keys']==c['parent_priority_child_map'][pk]
        assert p0['full_child_keys']==[r['key']for r in units if c['child_parent_map'][r['key']]==pk]
        assert p0['priority_child_keys']==[k for k in keys[:765]if c['child_parent_map'][k]==pk]
    checks.append('full_order_candidate_controls_integer_crossing_all_parent_child_maps_remainder_and_writein_bounds')
    replay=readj(D/'historical-replay.json');assert replay['status']=='pass_original_replay_named_historical_scope'
    expected=dict(HTML_native=895,Douglas_contexts=1167,Douglas_original_rows=1277,Douglas_raw_values_types=16228,Douglas_numeric_fields=8406,Lancaster_original_pages=1431,Lancaster_contexts=595,Lancaster_method_cells=21428,Lancaster_statistics=199,Lancaster_registration=206570,Lancaster_ballots199=161160,Lancaster_Senate_ballots198=161159,resident_ballots=1)
    for k,v in expected.items():assert replay[k]==v,(k,replay[k])
    transcript=json.loads(gzip.decompress((D/'extracts/original-replayed-native.json.gz').read_bytes()));assert [x['key']for x in transcript]==keys
    for r,u in zip(transcript,units):assert r['values']==u['candidate_values']and r['generic']==u['generic_writeins']
    assert sum(x['generic_writeins']is None for x in units)==895 and replay['observed_generic']==1078 and replay['partial_sensitivity_membership_changed']
    checks.append('independent_original_HTML_BIFF_all1431PDF_pages595contexts199statistics_full_method_and_volume_replay')
    inventory=list(csv.DictReader((S/'data/official-results-sources.csv').open()));assert len(inventory)==94 and len({r['authority_key']for r in inventory})==94
    dirs=readj(D/'directory-records.json');assert len(dirs)==93 and len({r['county_fips']for r in dirs})==93
    dirraw=decoded('sos-directory-retry1').decode();portalraw=decoded('county-portal-retry1').decode()
    assert '2026 Primary Election'in portalraw
    for r in dirs:assert r['directory_fields_original_html']in dirraw
    assert {r['county']:r['county_fips']for r in dirs}['Madison']=='31119'and {r['county']:r['county_fips']for r in dirs}['McPherson']=='31117'
    parents=readj(D/'parent-index.json');assert len(parents)==93 and sum(p['priority_parent']for p in parents)==58;current=json.loads(decoded('state-current-county-json'))['d'];assert len(current)==465
    assert len({r['CountyID']for r in current})==len({r['CountyName']for r in current})==93
    cand=readj(D/'current-candidate-keys.json');assert cand['catalog_rows']==625 and len(cand['catalog_senate_complete_objects'])==5 and all(r['ID']==148 for r in cand['catalog_senate_complete_objects'])
    expectedc=[('3012','REP'),('3249','LMN'),('3434','NWP'),('3429','AFP'),('3365','PET')];assert [(r['CandidateID'],r['PartyCode'])for r in cand['source_scoped_candidate_fields']]==expectedc
    schema=set(current[0]);assert len(schema)==26;totalnative=0;rows=0
    for par in parents:
        q=readj(D/par['path']);assert q['parent_key']==par['parent_key'];verify_ref(q['complete_historical_parent_ref']);assert q['directory_complete_fields']in dirs
        assert not q['current_geography_approved']and q['remaining_Senate_votes']is None and q['measured_cadence']is None
        assert any(x['stage']=='directory-landing'for x in q['local_publication_chain'])
        county=[x for x in current if x['CountyName']==par['county']];assert len(county)==5 and {(x['CandidateID'],x['PartyCode'])for x in county}==set(expectedc)
        for r in county:assert set(r)==schema and r['RaceID']==13224 and r['OfficeSeqNo']=='102'and r['VoteFor']==1 and r['calcCandidateVotes']==0 and not r['IsReported']and r['CurrentDateTime']is None
        nn=q['current_state_source']['current_native']
        if par['priority_parent']:
            assert nn and nn['source_id']=='current-native-'+re.sub('[^a-z0-9]+','-',par['county'].lower()).strip('-');assert receipts[nn['source_id']]['parent_source_id']=='state-current-county-json'
            rr=json.loads(decoded(nn['source_id']))['d'];assert len(rr)==nn['rows'];gg=collections.defaultdict(list)
            for r in rr:
                assert set(r)==schema and r['CountyName']==par['county']and r['CountyID']==county[0]['CountyID'];assert r['RaceID']==13224 and r['OfficeSeqNo']=='102'and r['TotalPrecincts']==1322 and r['calcCandidateVotes']==0 and not r['IsReported']and not r['Winner']and r['CurrentDateTime']is None;gg[r['StatePrecinctID']].append(r)
            assert len(gg)==nn['contexts']and '_TOT'in gg
            for gr in gg.values():assert len(gr)==5 and {(x['CandidateID'],x['PartyCode'])for x in gr}==set(expectedc)
            assert len(gg)-1==nn['nonadministrative_contexts']==county[0]['TotalPrecincts'];totalnative+=len(gg)-1;rows+=len(rr)
        else:assert nn is None
    assert(totalnative,rows)==(1145,6015);assert sum(next(r['TotalPrecincts']for r in current if r['CountyName']==p0['county'])for p0 in parents)==1322
    native=[json.loads(x)for x in gzip.decompress((D/'native-investigations.jsonl.gz').read_bytes()).splitlines()];assert len(native)==1326 and [x['key']for x in native]==keys
    for i,(r,u)in enumerate(zip(native,units)):
        assert r['rank']==i+1 and r['dispatch_status']==('priority'if i<765 else 'remainder');assert verify_ref(r['complete_historical_object_ref'])==u;assert r['parent_key']==c['child_parent_map'][u['key']];assert (D/r['parent_inspection']).is_file()and r['current_reporting_ID']is None and not r['current_geography_approved']and r['remaining_Senate_votes']is None
        if i<765:assert r['current_parent_native_source_id']in receipts
    checks.append('all93directory_original_fields94authorities58individual_current_chains765qualified_records561remainder_no_join')
    vendors=readj(D/'vendor-inspections.json');assert len(vendors)==3 and sum(x['all_contest_schema_balance_checks']for x in vendors)==121
    for v in vendors:
        assert not v['current_November_returns'];assert v['election_identity']['electiondate']in ['5/12/2026','11/5/2024'];assert v['prior_version_comparison']['complete_entity_retained']
        sums=json.loads(decoded(v['config_source_id']+'-sum'))['Contests'];det={x['K']:x for x in json.loads(decoded(v['config_source_id']+'-details'))['Contests']};vt=json.loads(decoded(v['config_source_id']+'-vt'));methods={x['K']:x for x in vt['Contests']}
        for r in sums:
            assert sum(r['V'])==r['T']and len(r['CH'])==len(r['V'])==len(r['P'])==len(r['CHAggId'])
            if r['K']in det:assert [sum(v0[i]for v0 in det[r['K']]['V'])for i in range(len(r['CH']))]==r['V']
            if r['K']in methods:assert [sum(x)for x in methods[r['K']]['Votes']]==r['V']
    assert '11/3/2026'in decoded('state-app-retry1').decode()and '10/6/2026 8:49 AM CT'in decoded('state-1').decode()
    for e in readj(D/'current-export-inspections.json'):
        assert len(e['complete_header'])==14 and e['unheaded_trailing_empty_column_preserved']and len(e['Senate_complete_rows'])==5
        for r in e['Senate_complete_rows']:
            f=r['complete_fields'];assert len(f)==15 and f[0]=='13224'and f[5]=='102'and f[6]==''and f[11]=='0'and f[-1]==''and(f[7],f[2])in expectedc
    law=readj(D/'legal-findings.json');assert 'January1,2027'in law['operative_vintage']['enacted_LB1075'];assert 'third day'in law['operative_vintage']['November_recount_request'];assert 'Tuesday'in law['operative_vintage']['November_ID_cure']
    checks.append('current_election_candidate_identity_zero_setup_rejection_vendor_candidate_method_balances_and_operative_law_limits')
    # Links are checked relative to the actual delivered report/README/schema.
    linkcount=0
    for path in [S/'official-results.md',D/'README.md',D/'SCHEMA.md']:
        for target in re.findall(r'\]\(([^\n)]+)\)',path.read_text()):
            if target.startswith(('https:','http:','mailto:','#')):continue
            target=target.split('#')[0].split(' "')[0].strip('<>');resolved=(path.parent/urllib.parse.unquote(target)).resolve();assert resolved.exists()or(write and resolved in {(D/'validation.json').resolve(),(D/'asset-manifest.json').resolve()}),(str(path),target);linkcount+=1
    checks.append('all_delivered_local_links_and_strict_asset_sizes_no_dependency_cache_directories')
    allowned=[S/'official-results.md',S/'data/official-results-sources.csv']+[p for p in D.rglob('*')if p.is_file()]
    for path in allowned:assert path.stat().st_size<40000000;assert not any(k in path.parts for k in ['__pycache__','node_modules','.venv','venv','.cache'])
    result=dict(schema='NE-official-offline-validation-v1',status='pass_offline_with_explicit_historical_current_legal_limits',checks=checks,frozen_input_file_pins=len(frozen['verified_inputs']),exact_reconstructed_legacy_aggregate_pins=len(frozen['exact_reconstructed_legacy_aggregate_pins']),mutable_news_aggregate_dependency=False,own_receipts=len(receipts),exact_raw_entities_reconstructed=rawentities,recursive_reference_objects_checked=refcount,authorities=94,priority_parents=58,historical_native=1326,priority=765,remainder=561,alternative_admin_partial=329,alternate_PDF=14,resident_unavailable=2,school_attachments=2,current_native_rows=6015,current_nonadmin_contexts=1145,current_votes_admitted=False,current_geography_approved=False,eligible_writein_completeness_approved=False,measured_cadence=False,local_links=linkcount,manifest_exclusion='Manifest self only; validation has no reverse manifest pin')
    data=(json.dumps(result,indent=2)+'\n').encode()
    if write:(D/'validation.json').write_bytes(data)
    else:assert (D/'validation.json').read_bytes()==data,'Saved validation differs'
    mp=D/'asset-manifest.json'
    if mp.exists()and not write:
        manifest=readj(mp);actual={str(p.relative_to(S))for p in allowned if p!=mp};assert actual=={r['path']for r in manifest['owned_artifacts']},'Manifest exact membership'
        for r in manifest['owned_artifacts']+manifest['external_original_references']:verify_pin(r)
        assert manifest['excluded_self_only']=='data/results-sources/asset-manifest.json'and manifest['validation_no_reverse_manifest_pin']
        print('Manifest exact membership and all owned/external pins pass:',len(manifest['owned_artifacts']))
    elif not write:raise AssertionError('Final manifest required for read-only validation')
    print(json.dumps(result))
if __name__=='__main__':main('--write-validation'in sys.argv)

"""Full references and final read-only inventory audit. No source fetch or writes by default."""
import argparse,collections,contextlib,csv,gzip,hashlib,io,json,re,urllib.parse
from pathlib import Path
from acquire import ROOT,body,dump
from inspect_sources import text,xlsx,htmlview
from replay import STATE,AUTHORITY,strict,sha,pointer,semantic,check_pin
import replay,reproduce

MANIFEST=ROOT/'asset-manifest.json'
def owned():
    return sorted([STATE/'official-results.md',STATE/'data/official-results-sources.csv']+[p for p in ROOT.rglob('*') if p.is_file()])
def inventory():
    rows=[]
    for p in owned():
        if p==MANIFEST:continue
        assert not p.is_symlink(),p
        b=p.read_bytes();assert len(b)<40000000,p
        assert not any(s in p.parts for s in ['__pycache__','node_modules']),p
        rows.append({'path':str(p.relative_to(STATE)),'bytes':len(b),'sha256':sha(b)})
    assert len({r['path'] for r in rows})==len(rows)
    return rows
def run(final=False,write=False):
    assert not (final and write)
    before=inventory()
    a_bytes=AUTHORITY.read_bytes();a=strict(a_bytes);a_digest=sha(a_bytes).encode()
    # Read-only external authority. Its digest/body must never be persisted here.
    for p in owned():
        b=p.read_bytes();raw=gzip.decompress(b) if p.suffix=='.gz' else b
        assert a_digest not in raw and raw!=a_bytes,('external authority copied/pinned',p)
    cp=a['frozen_contract'];cb=(STATE/cp['path']).read_bytes();check_pin(cp,cb);contract=strict(cb)
    cache={};receipts={};used=set()
    for p in sorted((ROOT/'requests').glob('*.json')):
        r=strict(p.read_bytes());assert r['key']==p.stem;receipts[p.stem]=r
        for field in ['request_method','submitted_body','request_headers','public_parent_edge','started_at_utc','completed_at_utc']:assert field in r,(p,field)
        if 'submitted_fields' not in r:assert r['request_method']=='GET' and r['submitted_body'] is None
        if r['request_method']=='POST':
            assert r['requested_url']=='https://vote.elections.virginia.gov/VoterInformation/PublicContactLookup'
            assert set(r['submitted_fields'])=={'LocalityUid'}
        for h in r['hops']:
            for f in ['actual_requested_url','request_method','request_headers','submitted_body','response_headers','status','retrieved_at_utc','completed_at_utc']:assert f in h,(p,f)
            e=h['body'];packed=(ROOT/e['path']).read_bytes();assert len(packed)==e['stored_bytes'] and sha(packed)==e['stored_sha256']
            b=gzip.decompress(packed);assert len(b)==e['raw_bytes'] and sha(b)==e['raw_sha256']
            cache[e['raw_sha256']]=b;used.add(e['path'])
    assert used=={str(p.relative_to(ROOT)) for p in (ROOT/'bodies').glob('*')}
    parents=strict((ROOT/'parent-investigations.json').read_bytes());assert len(parents)==133
    assert sum(p['kind']=='independent city' for p in parents)==38
    assert sum(p['priority_parent_rank'] is not None for p in parents)==108
    for p in parents:
        c=p['complete_historical_parent_context'];check_pin({'path':c['path'],'bytes':c['bytes'],'sha256':c['sha256']},cb)
        assert semantic(pointer(contract,c['pointer']))==c['full_recursive_semantic_sha256']
        assert p['hierarchy']==a['all_parent_ordered_child_arrays'][p['historical_parent_key']]
        assert p['current_returns_admitted'] is False
        for f in ['current_leaf_mapping','current_method_crossyear_mapping','current_geometry_mapping','remaining_eligible_vote_pool','measured_vote_publication_cadence']:assert p[f] is None
    def lines(name):return [strict(line) for line in gzip.decompress((ROOT/name).read_bytes()).splitlines()]
    full=lines('full-native-hierarchy.jsonl.gz');priority=lines('priority-investigations.jsonl.gz');rest=lines('remainder-investigations.jsonl.gz')
    assert len(full)==2669 and len(priority)==1538 and len(rest)==1131 and full==priority+rest
    assert [r['source_key'] for r in full]==a['ordered_full_keys']
    assert [r['source_key'] for r in priority]==a['ordered_priority_keys']
    assert [r['source_key'] for r in rest]==a['ordered_remainder_keys']
    references=0
    for i,r in enumerate(full):
        assert r['source_rank']==i+1
        c=r['complete_frozen_native_context'];assert semantic(pointer(contract,c['pointer']))==c['full_recursive_semantic_sha256']
        assert pointer(contract,c['pointer'])['key']==r['source_key'];references+=1
        p=pointer(parents,r['shared_parent_investigation']['pointer']);assert p['historical_parent_key']==contract['ordered_units'][i]['parent_key']
    natives=lines('current-native-inventory.jsonl.gz');assert len(natives)==2528
    def source_ref(ref):
        nonlocal references
        r=receipts[ref['request']];e=r['hops'][-1]['body'];assert e==ref['complete_response_entity']
        x=strict(cache[e['raw_sha256']]);v=pointer(x,ref.get('pointer',''));references+=1;return v
    for r in natives:
        n=source_ref(r['whole_current_native_context']);assert semantic(n)==r['whole_current_native_semantic_sha256']
        assert n['precinct']['id']==r['observed_uuid_setup_only'] and r['votes_admitted'] is False and r['unapproved_historical_match'] is None
    candidate_methods=0
    for p in parents:
        whole=source_ref(p['complete_current_locality_body']);source_ref(p['state_current_parent_context'])
        assert whole['election']['electionDate']=='2026-11-03' and whole['election']['isProduction'] is True and whole['election']['isPrimary'] is False
        ns=whole['ballotItemWithBreakdown']['breakdownResults'];assert len(ns)==p['current_native_objects']
        for n in ns:
            for choice in n['ballotOptions']:
                assert choice['voteCount']==0
                candidate_methods+=len(choice['groupResults'])
                assert all(method['voteCount']==0 for method in choice['groupResults'])
        for v in p['separate_federal_directory_whole_object_references']:
            assert semantic(source_ref(v['source']))==v['whole_object_semantic_sha256']
        for e in p['local_election_link_investigations']:
            rr=receipts[e['request']];assert e['complete_entity']==(rr['hops'][-1]['body'] if rr['hops'] else None)
            assert e['status']==rr.get('final_status')
    assert candidate_methods==37920
    schemas=strict(gzip.decompress((ROOT/'source-schemas.json.gz').read_bytes()))
    for s in schemas:
        assert semantic(strict(cache[s['complete_entity']['raw_sha256']]))==s['full_semantic_sha256']
    # Old inspection products retain exact full text/cells; no excerpt substitutes.
    for key in ['law-full','early-absentee','military-overseas','state-board','board-members','state-about','state-officials']:
        assert gzip.decompress((ROOT/'inspections'/(key+'.txt.gz')).read_bytes())==text(body(key)).encode()
    for key in ['federal-roster-workbook','calendar-workbook']:
        assert strict((ROOT/'inspections'/(key+'.json')).read_bytes())==xlsx(body(key))
    sections=strict((ROOT/'inspections/code-sections.json').read_bytes());law=body('law-full').decode()
    starts=[m.start() for m in re.finditer(r'<b>§ 24\.2-',law)]
    assert len(starts)==len(sections)
    for i,s in enumerate(sections):
        lo,hi=s['character_span'];assert lo==starts[i]
        if i+1<len(starts):assert hi==starts[i+1]
        segment=law[lo:hi].encode();assert s['complete_text']==text(segment)
        assert s['links']==htmlview(segment).links
    with (STATE/'data/official-results-sources.csv').open(newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==133 and [r['parent_key'] for r in rows]==[p['historical_parent_key'] for p in parents]
    assert sum(int(r['priority_native']) for r in rows)==1538 and sum(int(r['remainder_native']) for r in rows)==1131
    assert sum(int(r['current_candidate_methods']) for r in rows)==37920
    # Check every local Markdown file target; archived snapshots are not rewritten.
    checked_links=0
    for md in [STATE/'official-results.md']+sorted(ROOT.rglob('*.md')):
        if 'history' in md.relative_to(STATE).parts:continue
        base=STATE if md.name=='report-template.md' else md.parent
        for target in re.findall(r'\]\(([^\s]+)\)',md.read_text()):
            if urllib.parse.urlsplit(target).scheme or target.startswith('#'):continue
            path=urllib.parse.unquote(target.split('#',1)[0]);resolved=(base/path).resolve()
            assert resolved.exists() or (not final and resolved==MANIFEST.resolve()),(md,target)
            checked_links+=1
    with contextlib.redirect_stdout(io.StringIO()):
        reprod=reproduce.run(False);historical=replay.main(False)
    assert historical==strict((ROOT/'historical-replay.json').read_bytes())
    assert reprod==strict((ROOT/'reproduction.json').read_bytes())
    result={'status':'pass','mode':'final read-only' if final else 'pre-seal validation',
      'external_acceptance_authority_path':str(AUTHORITY.relative_to(STATE)),
      'parents':len(parents),'priority_parents':108,'native_hierarchy':len(full),'priority_in_order':len(priority),'remainder_in_order':len(rest),
      'current_whole_native_setup_objects':len(natives),'current_candidate_method_objects':candidate_methods,
      'complete_reference_resolutions':references,'actual_request_receipts':len(receipts),'distinct_complete_originals':len(cache),
      'json_whole_entity_schemas':len(schemas),'full_code_sections_versions':len(sections),'local_markdown_links_checked':checked_links,
      'historical_recursive_objects':historical['full_recursive_objects'],'offline_byte_identical_products':len(reprod['complete_products_rebuilt_byte_identically']),
      'negative_cases':reprod['negative_cases'],'actual_vote_admission':False,
      'approval_scope':'Bounded source research only; no acceptance/publication/current legality/leaf/geometry/eligible-write-in/cadence/pool/collector/forecast/calibration approval'}
    if final:
        mb=MANIFEST.read_bytes();assert len(mb)<40000000
        mf=strict(mb);assert mf['files']==before
        assert mf['excludes_only']=='data/results-sources/asset-manifest.json'
        seal=strict((ROOT/'final-seal.json').read_bytes())
        assert {p['path'] for p in seal['proofs_and_handoff']}=={'validation.json','reproduction.json','historical-replay.json','negative-fixtures.json','handoff.json'}
        for pin in seal['proofs_and_handoff']:check_pin(pin,(ROOT/pin['path']).read_bytes())
        for p in owned():
            if p==MANIFEST:continue
            b=p.read_bytes();raw=gzip.decompress(b) if p.suffix=='.gz' else b
            assert sha(mb).encode() not in raw,('reverse manifest digest cycle',p)
        assert inventory()==before,'owned files changed during final audit'
        result.update({'exact_manifest_members':len(before),'manifest_sha256':sha(MANIFEST.read_bytes()),'all_owned_files_strictly_under_bytes':40000000,'no_owned_writes':True})
    if write:dump(ROOT/'validation.json',result)
    print(json.dumps(result));return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args();run(a.final,a.write)

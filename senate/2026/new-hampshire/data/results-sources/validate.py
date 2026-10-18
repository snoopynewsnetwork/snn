#!/usr/bin/env python3
"""Meaningful deterministic offline QA, with preserved source disagreements."""
import collections,csv,gzip,json,pathlib,re
from urllib.parse import unquote,urlsplit
from acquire import ROOT,SOURCE,dump,sha,LIMIT
from extract_history import STATE,numeric,read_original
def main():
    c=json.load(open(STATE/'data/turnout/priority-set.json'));assert sha((STATE/'data/turnout/priority-set.json').read_bytes())=='11c042966c67a50e496ad6f839afd8e3c8b28afe6e2761c6cda1aa51f7ce90fc'
    priorities=(STATE/'data/coordinator-priority-keys.txt').read_text().splitlines();assert priorities==c['ordered_priority_keys']
    rows=list(csv.DictReader((STATE/'data/official-results-sources.csv').open()));native=rows[1:];assert rows[0]['record_type']=='state_authority' and len(native)==320
    assert [r['source_geography_key'] for r in native]==c['full_ordered_keys'];assert len({r['source_geography_key'] for r in native})==320
    assert [r['source_geography_key'] for r in native if r['priority']=='true']==priorities
    assert [int(r['full_historical_rank']) for r in native]==list(range(1,321))
    assert all(r[k]=='' for r in native for k in ['source_numeric_native_id','current_numeric_native_id','current_election_id','current_senate_contest_id','verified_live_cadence_seconds','exact_remaining_votes'])
    assert all(r['current_candidate_ids_json']=='null' and r['synthetic_key_current_approval']=='none' for r in native)
    records=[json.loads(l) for l in gzip.open(ROOT/'historical-native-records.jsonl.gz','rt')];by=collections.defaultdict(list)
    blank_fields=0;literal_marks=0
    for r in records:
        by[r['source_id']].append(r);assert r['source_native_id'] is None
        for k,v in r['raw_fields'].items():
            assert r['fields'][k]==numeric(v),(r['source_id'],r['source_locator'],k)
            blank_fields+=v=='';literal_marks+=isinstance(v,str) and bool(re.search(r'[-*]',v))
        assert r['original_position'] and r['schema']
    assert len(by)==23 and len(records)==7360
    for sid,rs in by.items():assert [r['source_roster_position_zero_based'] for r in rs]==list(range(320)),sid
    primary=by[c['basis_source_id']];lookup={(r['county'],r['native_label']):r for r in primary}
    for r in native:assert json.loads(r['historical_raw_fields_json'])==lookup[(r['county'],r['native_label'])]['raw_fields']
    pr=json.load(open(ROOT/'priority-investigations.json'));assert len(pr)==143 and [r['source_geography_key'] for r in pr]==priorities
    assert len({r['explicit_municipal_parent_label'] for r in pr})==98
    assert all(all(v is None for v in r['current_ids_unavailable'].values()) and not r['historical_ward_current_identity_approval'] for r in pr)
    for r in pr:assert r['native_source_record']==lookup[(r['native_source_record']['county'],r['native_source_record']['native_label'])]
    inspections=json.load(open(ROOT/'municipal-inspections.json'));assert len(inspections)==98
    assert all(r['current_election_id'] is None and r['current_feed_test_flags'] is None and r['verified_live_refresh_seconds'] is None and r['exact_remaining_votes'] is None for r in inspections)
    cov=json.load(open(ROOT/'inventory-coverage.json'));assert cov['direct_current_municipal_channels']==79 and len(cov['direct_current_access_gaps'])==19
    hv=json.load(open(ROOT/'history-validation.json'));assert hv['status']=='pass' and hv['fields_checked']==34880 and hv['controls_checked']==483
    assert hv['denominator']==826189 and hv['top15']==185659 and hv['preceding142']==660378 and hv['minimum143']==662624
    assert 5*660378<4*826189<=5*662624 and 662624-660378==2246
    audit=json.load(open(ROOT/'historical-audit.json'));candidate_audits=[a for a in audit if not any(w in a['source_id'] for w in ['ballots-cast','checklist'])]
    for a in candidate_audits:
        assert all(v==0 for v in a['native_minus_state'].values() if v is not None),a['source_id']
        assert all(v==0 for x in a['county_controls'] for d in x['differences'] for v in d.values() if v is not None),a['source_id']
    assert json.load(open(ROOT/'peer-final-verification.json'))['status']=='pass'
    assert json.load(open(ROOT/'independent-controls.json'))['status']=='pass_with_preserved_2022_disagreement'
    http=0;http_status=collections.Counter();parents=collections.Counter()
    for p in SOURCE.glob('*.json'):
        m=json.load(open(p))
        if not isinstance(m,dict) or 'body_path' not in m:continue
        b=(ROOT/m['body_path']).read_bytes();h=(ROOT/m['headers_path']).read_bytes();original=gzip.decompress(b)
        assert len(b)==m['stored_bytes'] and sha(b)==m['stored_sha256']
        assert len(original)==m['original_bytes'] and sha(original)==m['original_sha256']
        assert sha(h)==m['headers_sha256'] and m['requested_url'] and m['final_url'] and m['retrieved_utc']
        assert m['complete_response']==(m['curl_exit']==0);http+=1;http_status[str(m['http_status'])]+=1;parents[str(m.get('parent_source_id'))]+=1
    refchecks=0
    for path in ['history-original-references.json','control-original-references.json','current-ballot-references.json']:
        for r in json.load(open(SOURCE/path)):
            b=(STATE/r['path']).read_bytes();assert len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256'],r['path']
            original=gzip.decompress(b)
            if sha(original)!=r['original_sha256'] and original.startswith(b'\x1f\x8b'):original=gzip.decompress(original)
            assert len(original)==r['original_bytes'] and sha(original)==r['original_sha256'],r['source_id']
            for k in ['metadata_path','headers_path','parent_metadata_path']:
                if r.get(k):
                    q=STATE/r[k];assert q.is_file()
                    expected=r.get(k+'_sha256',r.get('metadata_sha256') if k=='metadata_path' else None)
                    if expected:assert sha(q.read_bytes())==expected,q
            refchecks+=1
    # Every roster and full-original positions path exists and is a valid full JSONL stream.
    for r in json.load(open(ROOT/'historical-rosters.json')):
        assert len([json.loads(l) for l in gzip.open(ROOT/r['path'],'rt')])==320
        original_positions={json.dumps(json.loads(l),sort_keys=True) for l in gzip.open(ROOT/r['original_positions_path'],'rt')}
        # Side-by-side native groups share a physical worksheet row;320leaves need not mean320physicalrows.
        assert all(json.dumps(n['original_position'],sort_keys=True) in original_positions for n in by[r['source_id']])
    links=0
    for p in [STATE/'official-results.md',ROOT/'municipal-inspections.md',SOURCE/'SCHEMA.md']:
        for link in re.findall(r'\]\(([^\n]+?)\)',p.read_text()):
            if link.startswith(('https://','http://','#','mailto:')):continue
            dest=unquote(urlsplit(link).path);q=(p.parent/dest).resolve();assert q.is_file() or q==ROOT/'validation.json',(p,link);links+=1
    from manifest import owned
    files=owned();assert all(p.stat().st_size<LIMIT for p in files)
    assert not list(ROOT.rglob('__pycache__')) and not list(ROOT.rglob('node_modules'))
    assert not any(p.suffix=='.pyc' for p in files)
    ballot=json.load(open(ROOT/'current-ballot-review.json'));assert ballot['vote_limit']==1 and len(ballot['printed_candidates_in_order'])==3 and ballot['write_in_space']
    assert ballot['current_result_candidate_ids'] is None
    hours=json.load(open(ROOT/'poll-hours-evidence.json'));assert hours['utc_offset_seconds']==-18000 and any(h['closing_utc'].startswith('2026-11-04T01:00') for h in hours['local_hours'])
    report=(STATE/'official-results.md').read_text();assert all('`'+key+'`' in report for key in priorities)
    output={'status':'pass_with_explicit_primary_source_disagreements_and_operational_gaps','offline':True,'native_inventory_rows':320,'state_authority_rows':1,'unique_basis_keys':320,'priority_exact_key_records':143,'shared_priority_parent_labels':98,'remainder_records':177,'source_scoped_rosters':23,'source_native_records':7360,'native_fields_independently_checked':34880,'original_county_state_controls':483,'candidate_source_native_county_state_balances':'all independently reconcile; every source vintage retained','historical_denominator':826189,'top15':185659,'first142':660378,'first143':662624,'crossing_leaf':'Tilton2246','integer_minimum_80_percent_prefix':143,'full_order_and_priority_exact':True,'raw_blank_fields_preserved':blank_fields,'raw_dash_or_asterisk_fields_preserved':literal_marks,'source_original_positions':'complete rows/cells/types and PDFpage/line streams retained for all23','direct_current_municipal_channels':79,'direct_current_municipal_access_gaps':cov['direct_current_access_gaps'],'current_general_result_feeds_verified':0,'current_result_ids_filled':0,'owned_http_observations_verified':http,'http_status_counts':dict(sorted(http_status.items())),'read_only_original_reference_checks':refchecks,'relative_markdown_links_verified':links,'object_bound':'all owned files strictly below40000000bytes','cache_dependency_directories':0,'independent_controls':'House2020/2022/2024,FEC2024,NARAvisualcertificate;2022opposing297 preserved','local_checks':'Portsmouth20ward/candidatecells;Londonderry7fields+ballotbalance;Salem55sitecells/11rows/2810primaryballots;writeinadjudicationoverlap','first_wave_final_pins':'both final freezes exact; no mutable maps/news aggregate pin','court_posture':'Oct5narrowinjunction;Oct14staydenial/Dunlapwouldgrant;Oct15SCOTUSapplication/Oct19response/no disposition in capturedOct18docket','known_disagreements':'2022Clerk/earlier_2 versus linked_5/PDF;2024Coos/Somersworth/checklistHopkinton and other administrative vintage differences remain literal','material_gaps':['November result IDs/schema/test flags/completion/cadence','current reporting-unit geometry/clerk/delegated crosswalk','named/valid historical write-in allocation and historical amendment/certification chronology','comprehensive current cure/signature instructions and future court actions','full statewide November local hours; exact outstanding ballots/remaining votes'],'manifest_policy':'complete owned files plus exact read-only dependencies; manifest self excluded to avoid recursive hash; verified separately after build'}
    dump(ROOT/'validation.json',output)
    assert (ROOT/'validation.json').is_file() # Self-link now exists, including on a first clean build.
    print('PASS: all320/23rosters/143keys, original/stored hashes, numeric balances, relative links, unavailable IDs and bounds')
if __name__=='__main__':main()

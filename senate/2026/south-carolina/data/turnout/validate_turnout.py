"""Offline original-row, geography, source, control, threshold and asset audit.

--seal writes deterministic validation.json and a complete owned asset manifest.
Default verifies that seal, including every owned/reused file hash. No network.
"""
import csv,gzip,hashlib,io,json,re,sys
from pathlib import Path
from acquire import H,S,body,sha
from build_turnout import LABELS,walk,cellkey
from validate_legacy import check_legacy

def readcsv(p):
    raw=gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes()
    return list(csv.DictReader(io.StringIO(raw.decode())))
def load(p):return json.loads((H/p).read_text())
def check():
    original_checks=check_legacy()
    metas={p.stem.removesuffix('.meta'):json.loads(p.read_text())for p in sorted(S.glob('*.meta.json'))}
    successful=0;failures=[]
    for sid,m in metas.items():
        if m.get('transport_error'):assert m.get('body_path')is None;failures.append(sid);continue
        b=(S/m['body_path']).read_bytes();assert len(b)==m['stored_bytes']<40_000_000 and sha(b)==m['stored_sha256'],sid
        raw=body(sid);assert len(raw)==m['original_bytes']and sha(raw)==m['original_sha256'],sid
        if m.get('request_file'):assert sha((S/m['request_file']).read_bytes())==m['request_sha256']
        if m['http_status']==200:successful+=1
        else:failures.append(sid)
    u=load('candidate-universe.json');controls=load('controls.json');contract=load('priority-set.json')
    actual=[];expected_native={};candidatechecks={};sources={}
    for label in LABELS:
        candidates=set(u[label]['real_candidate_ids']);statecontrols=[]
        for mode in ['combined','methods']:
            sid=label+'-'+mode;d=json.loads(body(sid));assert not d.get('errors')
            assert metas[sid]['http_status']==200
            assert body(sid)==body(sid+'-split-party')
            assert d['data']['contest']['event']['type']['name']=='General'
            tree=d['data']['contestGranularData']['divisions']
            assert len(tree['children'])==46
            if mode=='combined':
                assert d['data']['contest']==u[label]['contest_metadata']
                assert d['data']['contestGranularData']['candidates']==u[label]['candidate_metadata']
                statecontrols=tree['granularRow'];expected_native[label]=[]
                for county in tree['children']:
                    for c in county['children']:expected_native[label].append((county['division']['name'],c['division']['id'],c['division']['name'],sum(r['votes']for r in c['granularRow']if r['candidateId']in candidates)))
            for n,ptr,parents in walk(tree):
                for i,r in enumerate(n['granularRow']):actual.append(dict(contest_label=label,observation_scope=mode,division_path=list(parents)+[n['division']['id']],division=n['division'],raw_ordinal=i,raw_value=r,source_pointer=ptr+f'/granularRow/{i}'))
        assert not controls[label]['combined_hierarchy_residuals']
        source_total=sum(r['votes']for r in statecontrols if r['candidateId']in candidates)
        assert source_total==controls[label]['state_candidate_votes']==sum(r[3]for r in expected_native[label])
        assert next(r['votes']for r in statecontrols if r['candidateId']==4)==source_total
        nr=readcsv(H/f'extracts/{label}-native-order.csv')
        assert len(nr)==len(expected_native[label])and len({r['geography_key']for r in nr})==len(nr)
        assert {(r['county'],r['native_id'],r['name'],int(r['candidate_votes']))for r in nr}==set(expected_native[label])
        assert nr==sorted(nr,key=lambda r:(-int(r['candidate_votes']),r['geography_key']))
        cumulative=0
        for i,r in enumerate(nr,1):
            cumulative+=int(r['candidate_votes']);assert int(r['rank'])==i and int(r['cumulative_votes'])==cumulative
        st=controls[label]['native_ranking'];n=st['minimum80_count'];assert int(nr[n-1]['cumulative_votes'])*5>=4*source_total>int(nr[n-2]['cumulative_votes'])*5
        candidatechecks[label]={'votes':source_total,'native_precincts':len(nr),'candidate_method_residual_cells':sum(r['kind']=='candidate'for r in controls[label]['combined_minus_method']),'method_hierarchy_residual_cells':len(controls[label]['method_hierarchy_residuals'])}
        sources[label]={mode:metas[label+'-'+mode]['original_sha256']for mode in ['combined','methods']}
    saved=[json.loads(x)for x in gzip.decompress((H/'extracts/source-positions.jsonl.gz').read_bytes()).splitlines()]
    assert saved==actual and len(saved)==516586
    cells=readcsv(H/'extracts/candidate-method-controls.csv.gz');assert len(cells)==len(actual)
    for a,b in zip(actual,cells):
        assert a['contest_label']==b['contest_label']and a['observation_scope']==b['observation_scope']and a['source_pointer']==b['source_pointer']and '/'.join(a['division_path'])==b['division_path']
        assert a['raw_value']==json.loads(b['raw_row_json'])
        r=a['raw_value'];assert str(r['candidateId'])==b['candidate_id']and str(r['voteChannelId'])==b['method_id']and (''if r['partyId']is None else str(r['partyId']))==b['party_id']and (''if r['votes']is None else str(r['votes']))==b['votes']
    county=readcsv(H/'../county-turnout.csv');assert len(county)==46 and len({r['county_fips']for r in county})==46
    assert [r['geography_key']for r in county]==contract['all_county_order']==contract['ordered_keys']
    assert abs(sum(float(r['share_2024_pres'])for r in county)-1)<1e-12
    total=sum(int(r['votes_2024_pres'])for r in county);assert total==2548140==contract['total']
    cumulative=0
    for i,(r,c)in enumerate(zip(county,contract['counties']),1):
        cumulative+=int(r['votes_2024_pres']);assert int(r['rank_2024_pres'])==i and int(r['cumulative_2024_pres'])==cumulative
        assert r['geography_key']==c['geography_key']and int(r['votes_2024_pres'])==c['candidate_votes']
        for label in LABELS:
            raw=json.loads(body(label+'-combined'))['data']['contestGranularData'];node=next(n for n in raw['divisions']['children']if n['division']['name']==r['county'])
            for cell in node['granularRow']:
                col=label.replace('-','_')+f'_c{cell["candidateId"]}_p{cell["partyId"]}'
                assert int(r[col])==cell['votes']
            native=c['historical_constituents'][label]
            assert [(n['native_id'],n['native_name'])for n in native]==[(n['division']['id'],n['division']['name'])for n in node['children']]
            assert sum(n['candidate_votes']for n in native)==int(r[label.replace('-','_')+'_candidate_votes'])
    n=contract['minimum80_count'];assert n==17 and contract['preceding_count']==16 and contract['preceding_votes']==2019337
    assert contract['minimum80_votes']==2061601 and contract['crossing_name']=='Oconee'
    assert 5*contract['preceding_votes']<4*total<=5*contract['minimum80_votes']
    assert contract['ordered_priority_keys']==contract['ordered_keys'][:max(15,n)]
    assert contract['remainder_keys']==contract['ordered_keys'][max(15,n):]
    assert sum(int(r['votes_2024_pres'])for r in county[:15])==1974167==contract['top15_votes']
    assert sum(int(r['votes_2024_pres'])for r in county[n:])==486539==contract['remainder_votes']
    pc=load('primary-controls.json')
    for name,label in [('2024_presidential_signed_certificate','2024-pres'),('2024_house_clerk','2024-pres'),('2020_house_clerk','2020-senate'),('2022_house_clerk','2022-senate')]:
        values={r['candidateId']:r['votes']for r in controls[label]['state_cells']}
        assert sum(pc[name]['candidate_id_votes'].values())==pc[name]['total']
        for k,v in pc[name]['candidate_id_votes'].items():assert values[int(k)]==v
    assert pc['2024_presidential_signed_certificate']['total']-pc['2024_house_clerk']['total']==5352
    assert controls['2020-senate']['state_candidate_votes']-pc['2020_house_clerk']['total']==2294
    ballots=next(r['votes']for r in controls['2020-senate']['state_cells']if r['candidateId']==1)
    assert ballots==2532829 and pc['participation_BCM_summary']['years']['2020']['ballots_BCM']-ballots==181
    reg=readcsv(H/'extracts/registration-participation.csv.gz');assert len(reg)==7500
    for r in reg:
        parts=r['source_pointer'].split('/');raw=json.loads(body(r['source_id']))['voterHistoryResults']['countyPrecinctResults'][int(parts[-1])]
        assert int(r['total_registered'])==raw['totalRegistered']and int(r['raw_total_voting'])==raw['totalVoting']
        assert (r['precinct']or None)==raw['precinct']and (r['precinct_code']or None)==raw['precinctCode']
        if r['data_type']=='REG':assert not r['total_participating']
        else:assert int(r['total_participating'])==raw['totalVoting']
    rc=load('registration-reconciliation.json')
    for y in [2024,2022,2020]:
        assert not rc[str(y)]['precinct_rollup_disagreements']
        for field in ['total_registered','total_participating']:
            rows=[r for r in reg if r['year']==str(y)and r['data_type']=='VOT'and r['level']in ['county','unassigned_administrative']]
            summary=next(r for r in reg if r['year']==str(y)and r['data_type']=='VOT'and r['level']=='state_summary')
            assert sum(int(r[field])for r in rows)==int(summary[field])
        for c in contract['counties']:
            f=c['county_fips'];native=c['voter_history_constituents'][str(y)]
            expected=[r for r in reg if r['year']==str(y)and r['level']=='vhm_native_precinct'and r['geography_key'].split(':')[3]==f]
            assert len(native)==len(expected)and [x['geography_key']for x in native]==[x['geography_key']for x in expected]
    assert len(rc['2024']['unassigned_rows'])==2 and rc['2024']['unassigned_rows'][0]['total_registered']==2 and rc['2024']['unassigned_rows'][0]['total_participating']==1
    assert set(r['geography_key']for r in reg if r['year']=='2024'and r['level']=='unassigned_administrative')=={'SC:vhm:2024:county:unassigned:row0'}
    linkcount=0
    for p in [H/'../../turnout.md',S/'SCHEMA.md']:
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if re.match(r'https?://|#',link):continue
            target=(p.parent/link.split('#')[0]).resolve()
            if '--seal'in sys.argv and target in [(H/'asset-manifest.json').resolve(),(H/'validation.json').resolve()]:pass
            else:assert target.exists(),(str(p),link)
            linkcount+=1
    for p in list(H.rglob('*'))+[H/'../county-turnout.csv',H/'../../turnout.md']:
        if p.is_file():assert p.stat().st_size<40_000_000,p
    return dict(status='pass_with_explicit_source_gaps',checks={'original_response_request_hashes':True,'all516586_original_positions_and_raw_flags':True,'all_candidate_party_method_csv_fields':True,'all46county_candidate_control_vectors':True,'all_native_coverage_and_constituents':True,'whole_state_combined_balances':True,'full_county_and_native_descending_orders':True,'exact_integer_minimum80_and_remainder':True,'county_weights_sum_one':True,'primary_source_controls_and_omissions_scoped':True,'all7500registration_positions_and_native_rollups':True,'unnamed2024admin_retained':True,'relative_links':linkcount,'individual_assets_strictly_below40000000':True},original_legacy_checks=original_checks,canonical_source_hashes=sources,source_successful_captures=successful,source_negative_captures=failures,contests=candidatechecks,priority_summary={k:contract[k]for k in ['total','top15_votes','minimum80_count','minimum80_votes','preceding_votes','crossing_key','remainder_votes']},known_gaps=['2020 DB method allocation absent in26sourceprecinct contexts;95candidate cells and51hierarchy residuals preserved; complete original finer methods separately verified','Method ballot/under-over pseudo-controls disagree with combined views','2022 historical mail-channel candidate votes exceed separately published absentee ballot statistic; source scopes unresolved','2020 Senate ballot control differs electionwide original/BCM summary by181','Clerk2024 omitsTerry5352; Clerk2020Senate omitsgeneric2294','Original native registration sums differ county controls in151of182XMLcontexts; all ballot rollups exact','2022 original state registered3379089 vs all46countyattributes3379129; difference40 retained without allocation','VHM requested-county historic labels do not establish election-day physical membership','No named/valid write-in subset beyond generic source','No current2026 precinct/geometry equivalence or live source approval'],peer_status=load('peer-agreement.json')['status']if(H/'peer-agreement.json').exists()else'pending independent peer package')

def files():
    return sorted([p for p in H.rglob('*')if p.is_file()and p.name!='asset-manifest.json'and '__pycache__'not in p.parts]+[H/'../county-turnout.csv',H/'../../turnout.md'],key=lambda p:str(p))
def seal(result):
    (H/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    entries=[dict(path=str(p.relative_to(H))if p.is_relative_to(H)else __import__('os').path.relpath(p,H),bytes=p.stat().st_size,sha256=sha(p.read_bytes()),ownership='SC turnout exclusive path')for p in files()]
    refs=[]
    for p in sorted(S.glob('*.meta.json')):
        m=json.loads(p.read_text())
        if m.get('body_path'):
            q=(S/m['body_path']).resolve()
            if not q.is_relative_to(H):refs.append(dict(path=__import__('os').path.relpath(q,H),bytes=q.stat().st_size,sha256=sha(q.read_bytes()),original_sha256=m['original_sha256'],original_bytes=m['original_bytes'],encoding=m.get('stored_encoding','gzip'),retrieval_meta=str(p.relative_to(H)),ownership='read-only shared exact-byte original'))
    for name in ['legacy-observations.json','legacy-json-observations.json']:
        for r in load(name).values():
            for field in ['metadata_path','body_path']:
                q=(H/r[field]).resolve()
                if not q.is_relative_to(H):refs.append(dict(path=__import__('os').path.relpath(q,H),bytes=q.stat().st_size,sha256=sha(q.read_bytes()),ownership='read-only original source metadata/body'))
    for name in ['source/shared-news-provenance.json','source/shared-legacy-provenance.json']:
        for r in load(name):
            for field in ['stored_path','metadata_path']:
                if not r.get(field):continue
                q=(H/r[field]).resolve();refs.append(dict(path=__import__('os').path.relpath(q,H),bytes=q.stat().st_size,sha256=sha(q.read_bytes()),ownership='read-only original authority/download chain'))
    (H/'asset-manifest.json').write_text(json.dumps(dict(manifest_scope='All owned files including report,compatibility CSV and validation; manifest itself excluded to avoid self-reference; read-only body references separately listed',owned_assets=entries,read_only_references=refs),indent=2)+'\n')
def verify_manifest():
    m=load('asset-manifest.json');expected={str(p.resolve())for p in files()};actual=set()
    for r in m['owned_assets']+m['read_only_references']:
        p=(H/r['path']).resolve();assert p.exists()and p.stat().st_size==r['bytes']<40_000_000 and sha(p.read_bytes())==r['sha256'],r['path']
    for r in m['owned_assets']:actual.add(str((H/r['path']).resolve()))
    assert actual==expected,'manifest coverage'
if __name__=='__main__':
    r=check()
    if '--seal'in sys.argv:seal(r)
    else:verify_manifest();assert r==load('validation.json')
    print(json.dumps(r,indent=2))

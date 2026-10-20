"""Full source/history/owned membership audit. --sealed is read-only."""
import sys,json,gzip,re,urllib.parse,csv,subprocess,collections
from pathlib import Path
import replay,original_replay,negative_checks
from replay import HERE,STATE,loads,digest
def owned():
    return sorted([STATE/'official-results.md',STATE/'data/official-results-sources.csv']+[p for p in HERE.rglob('*') if p.is_file()],key=lambda p:p.relative_to(STATE).as_posix())
def memberships(sealed=False):
    mf=HERE/'asset-manifest.json';files=owned()
    assert not any(any(c in p.parts for c in ['__pycache__','node_modules','.venv','.cache']) for p in files)
    for p in files:assert p.stat().st_size<40000000,(p,'size')
    if sealed:
        m=loads(mf.read_bytes());actual={p.relative_to(STATE).as_posix():p for p in files if p!=mf}
        assert set(actual)=={x['path'] for x in m['assets']},'exact owned membership'
        for x in m['assets']:
            b=actual[x['path']].read_bytes();assert len(b)==x['bytes'] and digest(b)==x['sha256'],x['path']
    return len(files)
def links(sealed=False):
    n=0
    for p in [STATE/'official-results.md',HERE/'SCHEMA.md']:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('https://','http://','#')):continue
            path=(p.parent/urllib.parse.unquote(target.split('#')[0])).resolve()
            if not sealed and path in [HERE/'asset-manifest.json',HERE/'final-seal.json',HERE/'validation.json',HERE/'offline-proof.json']:continue
            assert path.exists(),('local link',p.name,target);n+=1
    return n
def responses():
    n=collections.Counter()
    for file in sorted((HERE/'requests').glob('*.json')):
        r=loads(file.read_bytes());assert r['started_utc']<=r['finished_utc'];n['requests']+=1
        assert r['request']['method']=='GET' and r['request']['body'] is None
        assert not re.search(r'/wp-admin/|/admin/|previewCode=|[?&]code=',r['request']['url'],re.I)
        for h in r['hops']:
            assert h['started_utc']<=h['finished_utc'];n['response_hops']+=1
            if h['asset']:
                b=(HERE/h['asset']).read_bytes();assert len(b)==h['stored_bytes'] and digest(b)==h['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==h['raw_bytes'] and digest(raw)==h['raw_sha256'];assert h['status'] is not None and h['headers'] is not None;n['whole_response_entities']+=1
            else:
                assert all(h[k] is None for k in ['status','headers','raw_bytes','raw_sha256']);assert h['response_unavailable'];n['explicit_unavailable_hops']+=1
    return dict(n)
def scope():
    p=loads(gzip.decompress((HERE/'historical-context.json.gz').read_bytes()));a=loads((STATE/'data/coordinator-priority-acceptance.json').read_bytes());assert p==loads(replay.checked(a['frozen_contract']))
    idx=loads(gzip.decompress((HERE/'native-context-index.json.gz').read_bytes()));assert len(idx)==2841
    assert [x['key'] for x in idx if x['priority']]==p['ordered_priority_keys'];assert [x['key'] for x in idx if not x['priority']]==p['remainder_keys']
    for x,row in zip(idx,p['full_order']):assert x['complete_historical_source_context']==row and x['current_match'] is None
    countyfiles=sorted((HERE/'counties').glob('*.json'));assert len(countyfiles)==75;n=0
    for f in countyfiles:
        x=loads(f.read_bytes());parent=next(z for z in p['all75parents'] if z['county_fips']==f.stem);assert x['historical_parent_whole']==parent
        rows=[r for r in p['full_order'] if r['county_fips']==f.stem]
        assert x['historical_ordered_full_children']==[r['key'] for r in rows]
        assert x['historical_ordered_priority_children']==[r['key'] for r in rows if r['key'] in set(p['ordered_priority_keys'])]
        n+=x['priority_parent'];o=x['current_source_observation'];assert o['current_historical_matches'] is None and o['current_counts_admitted'] is False
        assert o['exact_remaining_pool'] is None and o['measured_cadence'] is None
        r=loads((HERE/x['publication_chain']['county_results']['receipt']).read_bytes());h=r['hops'][-1];source=loads(gzip.decompress((HERE/h['asset']).read_bytes()));c=source['response']['contests']['eafd140a-9378-43a2-bd6d-f8661524139b'];assert len(c['locations'])==o['native_location_count']
        for ref,(key,value) in zip(o['ordered_native_source_references'],c['locations'].items()):assert ref['key']==key and ref['complete_semantic_sha256']==replay.semantic(value)
    assert n==68
    rows=list(csv.DictReader((STATE/'data/official-results-sources.csv').open()));assert len(rows)==77 and len({r['county_fips'] for r in rows if r['county_fips']})==75
    d=loads((HERE/'disposition.json').read_bytes());assert all(v is False for v in d['approvals'].values()) and d['all_current_historical_matches'] is None
    return {'full_native':2841,'priority':1056,'remainder':1785,'full_parents':75,'priority_parents':68,'inventory_rows':77}
def offline():
    result=subprocess.run([sys.executable,'-B',str(HERE/'offline_replay.py')],capture_output=True)
    if result.returncode:
        raise RuntimeError('offline replay failure: '+result.stderr.decode())
    return loads(result.stdout)
def audit(write=False,sealed=False):
    result={'status':'pass','graph':replay.main(),'originals':original_replay.main()[0],'responses':responses(),'scope':scope(),'negative':negative_checks.run(False),'local_links':links(sealed),'owned_file_count':memberships(sealed)}
    off=offline();result['offline_output_count']=off['count'];result['guard_exercised']=off['guard_exercised']
    if sealed:
        prior=loads((HERE/'offline-proof.json').read_bytes());assert prior==off
        seal=loads((HERE/'final-seal.json').read_bytes());assert seal['status']=='bounded research sealed; coordinator acceptance pending'
    if write:
        (HERE/'offline-proof.json').write_text(json.dumps(off,indent=2)+'\n');(HERE/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':
    result=audit('--write' in sys.argv,'--sealed' in sys.argv);print(json.dumps({k:v for k,v in result.items() if k not in ['negative']},sort_keys=True))

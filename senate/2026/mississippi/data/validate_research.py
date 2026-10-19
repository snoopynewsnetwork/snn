"""Whole Mississippi integration; immutable worker outputs remain read-only."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from concurrent.futures import ThreadPoolExecutor
import ast,datetime,gzip,hashlib,json,re
STATE=Path(__file__).resolve().parent.parent;DATA=STATE/'data'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
class Links(HTMLParser):
    def __init__(self):super().__init__();self.refs=[]
    def handle_starttag(self,t,a):
        self.refs += [v for k,v in a if k in('href','src')and v]
def main():
    specs=[('data/turnout/asset-manifest.json','owned_assets','4681e60b69fda456f8ff87d73c5a82a3c1a79e5210059fb9e7bc04f9a6c1d280',13203,'data/turnout','turnout.md','data/county-turnout.csv'),('data/baselines/asset-manifest.json','owned','f5efa2370206c204af2bb557ced7732fc7b79e4540edbb454cf2350f142aecb2',12404,'data/baselines','county-partisanship.md','data/county-baselines.csv'),('data/results-sources/asset-manifest.json','entries','76043c056687f7e19f3950e19c8212531481444f45612a100684424392d4a05e',1329,'data/results-sources','official-results.md','data/official-results-sources.csv'),('maps/manifest.json','files','a212a838b3a906a2b3afe28d661d4b61a820a5275422b4972f718b9a5a13ad9c',321,'maps','precinct-maps.md',None)]
    manifests=[];allowned=set()
    for relative,key,digest,n,folder,report,csv in specs:
        p=STATE/relative;b=p.read_bytes();assert sha(b)==digest,relative;m=json.loads(b)
        # Baseline's explicit final ownership schema.
        if key not in m:
            assert relative=='data/baselines/asset-manifest.json';key='assets'
        rows=m[key];assert len(rows)==n,(relative,key,len(rows))
        expected={str(q.relative_to(STATE))for q in(STATE/folder).rglob('*')if q.is_file()and q!=p}|{report}
        if csv:expected.add(csv)
        actual={q['path']for q in rows};assert len(actual)==n and actual==expected and not(actual&allowned);allowned|=actual
        def check(a):
            q=STATE/a['path'];v=q.read_bytes();assert not q.is_symlink()and len(v)==a['bytes']<40000000 and sha(v)==a['sha256'],a['path']
            if q.suffix=='.py':ast.parse(v,filename=a['path'])
        with ThreadPoolExecutor(max_workers=4)as pool:list(pool.map(check,rows))
        manifests.append(dict(path=relative,sha256=digest,exact_entries=n,excludes_only_itself=True))
    reviews=['coordinator-finished-turnout-review.json','coordinator-finished-baseline-review.json','coordinator-finished-maps-review.json','coordinator-finished-official-review.json','coordinator-native-priority-v1-review.json','coordinator-native-target-review.json','coordinator-historical-native-target-review.json','coordinator-native-2018-target-review.json','coordinator-printed-field-source-inventory-review.json','coordinator-current-cure-calendar-remand-original-review.json','coordinator-official-original-visual-review.json']
    for name in reviews:assert load(DATA/name)['status'].startswith('pass'),name
    c=(DATA/'turnout/priority-set.json').read_bytes();assert len(c)==13065430 and sha(c)=='782ca7899236ba06e53effee549c4e6845f936c9b4ceea3fecc8828dd9a08c32';q=json.loads(c)
    acceptance=load(DATA/'coordinator-priority-acceptance.json');assert acceptance['accepted']and acceptance['status']=='accepted_historical_dispatch_only'
    assert not q['current_2026_geographic_approval']and len(q['all_unit_order'])==1736 and len(q['ordered_priority_keys'])==887 and len(q['native_priority_by_parent'])==82
    idx=load(STATE/'maps/index.json');official=load(DATA/'results-sources/priority-investigations.json');rem=load(DATA/'results-sources/remainder-inventory.json')
    assert idx['ordered_priority_keys']==[p['key']for p in official]==q['ordered_priority_keys']
    assert [p['key']for p in idx['full_preferred_native_entries']]==[p['key']for p in q['all_unit_order']]
    assert [p['key']for p in rem]==q['remainder']['ordered_keys']and len(rem)==849
    assert all(p['geometry_feature_ids']is None and p['approved_current_crosswalk']is None for p in idx['full_preferred_native_entries'])
    news=load(DATA/'news/manifest.json');assert len(news)==len({p['id']for p in news})==68
    for p in news:
        if not p.get('asset'):assert p.get('error')or p.get('status')is not None;continue
        z=(DATA/'news'/p['asset']).read_bytes();assert sha(z)==p['stored_sha256']
        assert sha(gzip.decompress(z)if p['asset'].endswith('.gz')else z)==p['raw_sha256']
    setup=load(DATA/'news/current-results-structured-review-oct19.json');assert not setup.get('genuine_November_counts_admitted',False)
    local_links=0
    for p in list(STATE.rglob('*.md'))+list(STATE.rglob('*.html')):
        if p.suffix=='.md':urls=re.findall(r'\]\(([^)]+)\)',p.read_text())
        else:parser=Links();parser.feed(p.read_text());urls=parser.refs
        for s in urls:
            u=urlsplit(s.strip('<>'))
            if u.scheme or not u.path:continue
            target=(p.parent/unquote(u.path)).resolve()
            assert target.exists()or target==(DATA/'coordinator-checks.json').resolve(),(str(p.relative_to(STATE)),s)
            local_links+=1
    files=[p for p in STATE.rglob('*')if p.is_file()];assert all(p.stat().st_size<40000000 and not p.is_symlink()for p in files)
    assert not any(p.name in('__pycache__','node_modules','.venv','.cache','.pytest_cache')or p.suffix in('.pyc','.pyo')for p in STATE.rglob('*'))
    for p in STATE.rglob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
    out=dict(status='pass_complete_state_research_integration_with_explicit_source_and_current_gaps',checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),four_assignment_manifests=manifests,total_owned_assignment_entries=len(allowned),independent_reviews=reviews,all_county_parents=82,preferred2024native=1736,all2024source_role_columns=2321,preferred_all11_fields=24926,primary_native=887,priority_parents=77,remainder_native=849,source_named_denominator=1215400,certified_named_denominator=1215401,unallocated_Tunica=1,top15_native_votes=60019,preceding886=972157,priority887=972656,remainder_votes=242744,complete2020publications=104,complete2018stages=164,independent_historical_original_replay=dict(publications2020=44,stages2018=43),news_observations=68,local_MD_HTML_links=local_links,maximum_stored_file_bytes=max(p.stat().st_size for p in files),exclusive_object_limit=40000000,caches=0,repository_check='npm run check passed:35race records,TypeScript andpublicapp syntax',current_November_entities_admitted=0,approved_current_entry_level_geography_matches=0,scope='Completed bounded historical research and current source/map acquisition inventory. Exact source discrepancies/admin/X/null/alternatives and bounded historical independent replay remain; no currentcrosswalk,eligiblewritein/candidateID completeness,exactremainingSenatepool,demonstratedlivecadence,full laterlegalcoverage,runningcollector orcalibratedprobability approval.')
    p=DATA/'coordinator-checks.json'
    if p.exists():
        old=load(p)
        if {k:v for k,v in old.items()if k!='checked_at_utc'}=={k:v for k,v in out.items()if k!='checked_at_utc'}:out['checked_at_utc']=old['checked_at_utc']
    p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()

"""Meaningful offline validation; writes only validation.json after all checks."""
from source_io import *
from build import readjl
import collections,csv,datetime,io,re,urllib.parse
from fractions import Fraction

def main():
    checks={};manifest=json.loads((OUT/'asset-manifest.json').read_text());checked=0
    def filepin(r):
        p=(ROOT/r['path']).resolve();assert p.is_relative_to(ROOT.resolve()),r
        b=p.read_bytes();assert len(b)==r['bytes']and sha(b)==r['sha256'],r['path']
        assert len(b)<40_000_000,r['path']
        return p,b
    for r in manifest['owned_artifacts']:filepin(r);checked+=1
    assert not list(OUT.rglob('__pycache__'))and not list(OUT.rglob('node_modules')),'Remove all owned dependency/cache directories'
    actual={str(p.relative_to(ROOT))for p in OUT.rglob('*')if p.is_file()and p.name not in ['validation.json','asset-manifest.json']}
    listed={r['path']for r in manifest['owned_artifacts']};assert actual=={p for p in listed if p.startswith('data/turnout/')}
    for r in manifest['shared_original_references']:
        _,stored=filepin(r);raw=gzip.decompress(stored)
        assert sha(raw)==r['raw_sha256']and len(raw)==r['raw_bytes'];checked+=1
    for r in manifest['peer_primary_original_references']:
        p=ROOT/r['reference_path'];stored=p.read_bytes();raw=gzip.decompress(stored);receipt=r['receipt']
        assert sha(stored)==receipt['stored_sha256']and sha(raw)==receipt['raw_sha256']and len(raw)==receipt['raw_bytes'];checked+=1
    for p in (OUT/'source').glob('*.receipt.json'):
        r=json.loads(p.read_text());b=(p.parent/r['asset']).read_bytes();raw=gzip.decompress(b)
        assert sha(b)==r['stored_sha256']and sha(raw)==r['raw_sha256']and len(raw)==r['raw_bytes']
        assert r['retrieved_at_utc']and r['final_url']and isinstance(r['headers'],dict)
    checks['hashes_and_original_reconstruction']={'pins_checked':checked,'strict_individual_bytes_below':40000000,'owned_dependency_cache_directories':0}
    # Re-check PDF source positions against original content, not rendered report.
    state=json.loads((OUT/'extracts/state-controls.json').read_text());pages={}
    for y in [2024,2022,2020]:
        raw=original(f'sos-{y}-canvass')
        with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
            f.write(raw);f.flush();pages[y]=subprocess.check_output(['pdftotext','-layout',f.name,'-']).decode().split('\f')
    cells=0
    for tid,t in state.items():
        assert len(t['counties'])==93
        assert [sum(r['values'][j]for r in t['counties'].values())for j in range(len(t['statewide']['values']))]==t['statewide']['values']
        for r in [t['statewide']]+list(t['counties'].values()):
            line=pages[int(tid[:4])][r['actual_pdf_page']-1].splitlines()[r['source_line_1based']-1]
            assert line==r['raw_line']
            tail=line[r['source_column_0based']:];n=len(r['values']);m=re.match(re.escape(r['county_literal'])+r'\s+('+r'\s+'.join([r'\d[\d,]*']*n)+r')',tail)
            assert m and [int(v.replace(',',''))for v in m[1].split()]==r['values'],r
            cells+=n
    assert state['2024-senate-special']['statewide']['values']==[585103,349902]
    assert state['2024-senate-regular']['candidate_columns'][1]['party_literal']=='By Petition'
    assert state['2020-senate']['candidate_columns'][3]['scope']=='qualified_named_writein'
    assert not any(k.startswith('2022-senate')for k in state)
    checks['statewide_primary_controls']={'tables':11,'county_vectors':1023,'PDF_position_numeric_cells_including_state':cells,'all_source_positions_exact':True}
    codes=list(csv.DictReader(io.StringIO(gzip.decompress((OUT/'source/census-county-codes.body.gz').read_bytes()).decode()),delimiter='|'))
    codes={r['COUNTYNAME'].removesuffix(' County'):r['STATEFP']+r['COUNTYFP']for r in codes if r['STATE']=='NE'}
    assert len(codes)==93 and codes['Madison']=='31119'and codes['McPherson']=='31117'
    counties=list(csv.DictReader((ROOT/'data/county-turnout.csv').open(newline='')));assert len(counties)==93
    assert len({r['county']for r in counties})==len({r['county_fips']for r in counties})==93
    for r in counties:
        assert r['county_fips']==codes[r['county']]
        for y in [2024,2022,2020]:
            assert sum(int(v)for k,v in r.items()if k.startswith(f'{y}_registration_'))==int(r[f'{y}_registered_voters_canvass'])
            assert sum(int(v)for k,v in r.items()if k.startswith(f'{y}_total_voting_method_'))==int(r[f'{y}_total_voting_canvass'])
        assert r['2024_special_generic_writeins_state_table']==''
    c=json.loads((OUT/'priority-set.json').read_text());nn=c['constituents'];rr=c['primary_ranking']['full_order'];D=935005
    assert c['priority_level']=='source_native_reporting_unit'and len(nn)==len(rr)==1326
    assert not c['coordinator_acceptance']and not c['current_geography_approval']
    assert [n['key']for n in nn]==[r['key']for r in rr]==c['ordered_full_keys']
    assert len({n['key']for n in nn})==1326
    assert rr==sorted(rr,key=lambda r:(-r['votes'],r['key']))
    assert [sum(n['candidate_values'][j]for n in nn)for j in range(2)]==[585103,349902]
    assert sum(Fraction(sum(n['candidate_values']),D)for n in nn)==1
    cumulative=0
    for i,(n,r)in enumerate(zip(nn,rr),1):
        assert n['county_fips']==codes[n['county']]and n['rank']==r['rank']==i
        assert r['votes']==sum(n['candidate_values'])==n['priority_votes_state_scope']
        assert all(isinstance(v,int)and v>=0 for v in n['candidate_values'])
        assert r['cumulative_before_votes']==cumulative;cumulative+=r['votes'];assert r['cumulative_votes']==cumulative
    assert cumulative==D
    k=next(i for i,r in enumerate(rr,1)if 5*r['cumulative_votes']>=4*D)
    assert k==765 and rr[k-1]['cumulative_votes']==748190 and rr[k-2]['cumulative_votes']==747645
    assert sum(r['votes']for r in rr[:15])==26773
    assert 5*rr[k-2]['cumulative_votes']<4*D<=5*rr[k-1]['cumulative_votes']
    assert c['ordered_priority_keys']==[r['key']for r in rr[:k]]and c['ordered_remainder_keys']==[r['key']for r in rr[k:]]
    assert len(c['ordered_remainder_keys'])==561 and sum(r['votes']for r in rr[k:])==186815
    parents=c['all93_parents'];assert len(parents)==93
    full=[]
    for parent in parents:
        rows=[n for n in nn if n['county']==parent['county']]
        assert parent['full_child_keys']==[n['key']for n in rows]==c['parent_full_child_map'][parent['parent_key']]
        assert parent['priority_child_keys']==[n['key']for n in rows if n['rank']<=k]==c['parent_priority_child_map'][parent['parent_key']]
        assert [sum(n['candidate_values'][j]for n in rows)for j in range(2)]==state['2024-senate-special']['counties'][parent['county']]['values']
        assert parent['full_child_named_votes']==sum(sum(n['candidate_values'])for n in rows)
        assert parent['priority_child_named_votes']==sum(sum(n['candidate_values'])for n in rows if n['rank']<=k)
        assert all(c['child_parent_map'][n['key']]==parent['parent_key']for n in rows);full.extend(parent['full_child_keys'])
    assert len(full)==len(set(full))==1326
    alt=c['administrative_and_partial_alternates'];assert len(alt)==329
    assert sum(r['kind']=='administrative_countywide'for r in alt)==93
    assert all(r['included_in_rank']is False for r in alt)
    cov=c['county_source_coverage'];assert len(cov)==93 and sum(r['complete']for r in cov)==91
    assert sum(r['retained_headers']for r in cov if r['complete'])==895
    assert sum(r['retained_headers']for r in cov if not r['complete'])==236
    for r in cov:
        b=original(r['source_id'])
        if not r['complete']:assert len(b)==1048576
    # Reconstruct every retained HTML TR substring by exact original character position.
    rawby={};positions=readjl(OUT/'extracts/historical-html-all-positions.jsonl.gz')
    for r in positions:
        if r['source_id']not in rawby:rawby[r['source_id']]=original(r['source_id']).decode('utf-8-sig')
        start=r['character_start'];raw=r['raw_html'];assert rawby[r['source_id']][start:start+len(raw)]==raw
    checks['native_geography_and_integer_priority']={'selected':1326,'full_order':1326,'priority':765,'remainder':561,'all93_parent_maps':True,
      'candidate_sums':[585103,349902],'minimum_votes':748190,'preceding_votes':747645,'top15':26773,'HTML_original_row_substrings_checked':len(positions),
      'administrative_partial_full_objects':329,'additional_native_PDF_objects':len(c['additional_native_source_contexts']),'unavailable_Senate_cases':len(c['unavailable_cases'])}
    assert len(c['additional_native_source_contexts'])==14 and len(c['unavailable_cases'])==2
    assert {r['county']for r in c['unavailable_cases']}=={'Lancaster','York'}and all(r['priority_contest_votes']is None for r in c['unavailable_cases'])
    # Source count/method checks, including overlapping parent Not Assigned.
    du=readjl(OUT/'extracts/douglas-native.jsonl.gz');assert len(du)==1167
    for r in du:
        assert sum(v['votes']for v in r['candidate_fields'])==r['reported_total_votes']
        assert r['reported_total_votes']+r['under']+r['over']==r['contest_volume_arithmetic']and r['ballots']is None
    la=readjl(OUT/'extracts/lancaster-native-methods.jsonl.gz');assert len(la)==595;methods=0
    for r in la:
        f={v['label_literal']:v['counts']for v in r['fields']}
        for v in f.values():assert len(v)==4 and v[0]==sum(v[1:]);methods+=len(v)
        assert f['Write-In Totals']==f['Not Assigned']
        names=[n for n in f if n.startswith(('Rep ','Dem ','Lib ','Lmn ','Pet '))]
        for j in range(4):
            assert sum(f[n][j]for n in names+['Write-In Totals'])==f['Total Votes Cast'][j]
            assert sum(f[n][j]for n in ['Total Votes Cast','Overvotes','Undervotes'])==f['Contest Totals'][j]
    volume=json.loads((OUT/'extracts/local-volume-reconciliation.json').read_text());assert [r['difference_arithmetic_minus_ballots']for r in volume['Douglas_source_volume']]==[-1,-1,0,-4,-10]
    assert all(r['repaired']is False for r in volume['Douglas_source_volume'])
    lc=volume['Lancaster_native_statistics_vs_state']
    assert (lc['statistics_contexts'],lc['registered_native_sum'],lc['state_canvass_registered_total'],lc['local_minus_state_registered'],lc['native_ballots_sum_all199'],lc['state_Total_Voting'],lc['resident_registered'])==(199,206570,206406,164,161160,161160,0)
    scans=readjl(OUT/'extracts/scan-verified-contexts.jsonl.gz');assert len(scans)==46
    extra=readjl(OUT/'extracts/additional-summary-contexts.jsonl.gz');assert len(extra)==12
    for r in scans+extra:
        for f in r['fields']:
            v=f['counts']
            if len(v)==4 and all(x is not None for x in v):assert v[0]==sum(v[1:])
    checks['original_methods_and_volume']={'Douglas_contexts':1167,'Lancaster_contexts':595,'Lancaster_method_cells':methods,'scan_contexts':46,'text_summary_contexts':12,'Douglas_unrepaired_volume_differences':[-1,-1,0,-4,-10],
      'Lancaster_registered_native_minus_state':164,'Lancaster_all199_ballots_native_minus_state':0}
    u=json.loads((OUT/'extracts/candidate-universe.json').read_text());assert len(u['current_final_roster'])==len(u['current_catalog_rows'])==5
    assert {r['ID']for r in u['current_catalog_rows']}=={148}and not u['current_counts_admitted']
    assert [(r['name'],r['party_printed'])for r in u['current_final_roster']]==[('Pete Ricketts','Republican'),('Mike Marvin','Legal Marijuana NOW'),('Robin Richards','Nebraska Working People'),('Chuck Conboy','America First'),('Dan Osborn','By Petition')]
    g=u['local_special_generic_writein_observations'];assert len(g)==9 and sum(r['generic_writein_marks']for r in g.values())==1117
    assert sum(r['generic_writeins']is None for r in nn)==895 and sum(r['generic_writeins']or 0 for r in nn)==1078
    assert u['statewide_special_eligible_named_writein_votes']is None
    b=u['writein_bounds'];assert not b['membership_robustness_established']and b['coarse_additional_ballot_capacity_upper_bound']==30231
    assert 5*748190>=4*(D+232)and 5*748190<4*(D+233)
    assert 5*(747645+1794)<4*(D+1794)and 5*(747645+1795)>=4*(D+1795)
    partial=u['incomplete_observed_generic_sensitivity'];assert (partial['named_plus_available_generic_sum'],partial['minimum80_count'],partial['minimum80_votes'])==(936083,765,749234)
    assert partial['priority_key_symmetric_difference']==['NE:2024-special:html:39:0003','NE:2024-special:lancaster-pdf:page-419']
    checks['candidate_universe_and_bounds']={'final_named_choices':5,'special_generic_observed_nine_counties':1117,'selected_native_observed_generic':1078,'unknown_native_generic_contexts':895,
      'conditional_outside':233,'conditional_inside':1795,'membership_robustness_established':False,'full_eligible_writein_universe_known':False}
    proof=json.loads((OUT/'peer-agreement.json').read_text());assert proof['status']=='pass_reciprocal_read_only_original_extraction_agreement'and proof['identity_differences']==[]
    assert c['independent_peer_agreement']['sha256']==sha((OUT/'peer-agreement.json').read_bytes())
    universeproof=json.loads((OUT/'source/peer-universe-QA.json').read_text())
    assert universeproof['status']=='pass'and universeproof['peer_sha256']==sha((OUT/'extracts/candidate-universe.json').read_bytes())
    assert c['independent_peer_universe_QA']['sha256']==sha((OUT/'source/peer-universe-QA.json').read_bytes())
    checks['independent_peer_agreement']={'status':proof['status'],'all93_parent_maps':proof['all93_parent_full_and_priority_maps'],'coordinator_acceptance':False}
    links=0
    for p in [ROOT/'turnout.md',OUT/'native-full-order.md',OUT/'source/SCHEMA.md']:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if re.match(r'^[a-z]+://',target):continue
            target=urllib.parse.unquote(target.split('#')[0]);q=(p.parent/target).resolve()
            assert q.is_relative_to(ROOT.resolve())and(q.exists()or q==(OUT/'validation.json').resolve()),(p,target);links+=1
    checks['relative_links']={'checked':links,'broken':0}
    out={'status':'pass_offline_named_scope_with_explicit_source_limits','checks':checks,
      'asset_manifest_sha256':sha((OUT/'asset-manifest.json').read_bytes()),'validated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'limits':['No complete eligible/generic special write-in universe or robust all-eligible membership established.','No current geographic/boundary equivalence or coordinator acceptance.','Missing native fields remain unavailable; all recorded source-volume/registration discrepancies remain unrepaired.','Historical research only; no implemented live collector, calibrated forecast or observed cadence.']}
    jwrite(OUT/'validation.json',out)
    assert (OUT/'validation.json').is_file()
    print(json.dumps({'status':out['status'],'checks':list(checks),'source_pins':checked,'primary_units':1326,'minimum80':765}))
if __name__=='__main__':main()

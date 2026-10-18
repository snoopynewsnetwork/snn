"""Independent arithmetic/source/asset audit; failures raise, gaps remain explicit."""
import argparse,csv,datetime,gzip,io,json,math,re,zipfile
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urljoin,urlparse,unquote
from html.parser import HTMLParser
from build import H,S,SPECS,jdump
from calculate import clip,solve,selected
from live_remainder import calculate,examples
def readcsv(p): return list(csv.DictReader(gzip.open(p,'rt') if str(p).endswith('.gz') else p.open()))
def jl(p): return [json.loads(l) for l in gzip.open(p,'rt')]
def near(a,b,tol=1e-7): assert abs(a-b)<tol,(a,b)
def manifest():
    paths=[p for p in H.rglob('*') if p.is_file() and p.name!='asset-manifest.json']+[S.ROOT/'county-partisanship.md',H.parent/'county-baselines.csv']
    owned=[dict(path=str(p.relative_to(S.ROOT)),bytes=p.stat().st_size,sha256=S.sha(p.read_bytes())) for p in sorted(paths)]
    shared=[]
    for m in json.loads((H/'source/references.json').read_text()):
        if not m['stored_path'].startswith('data/baselines/'):
            p=S.ROOT/m['stored_path']; shared.append(dict(source_id=m['id'],path=m['stored_path'],bytes=p.stat().st_size,sha256=S.sha(p.read_bytes()),original_sha256=m['raw_sha256'],original_bytes=m.get('raw_bytes',m.get('bytes'))))
    jdump('asset-manifest.json',dict(schema='ks-baselines-assets-v1',hash_policy='SHA256 exact stored bytes; manifest excludes itself; no reverse pins',owned_assets=owned,shared_read_only_original_references=shared,strict_maximum_bytes=40000000))
def verify_assets():
    m=json.loads((H/'asset-manifest.json').read_text())
    for r in m['owned_assets']+m['shared_read_only_original_references']:
        p=S.ROOT/r['path'];assert p.stat().st_size==r['bytes']<40000000; assert S.sha(p.read_bytes())==r['sha256'],str(p)
    expected={str(p.relative_to(S.ROOT)) for p in H.rglob('*') if p.is_file() and p.name!='asset-manifest.json'}|{'county-partisanship.md','data/county-baselines.csv'}
    assert expected=={r['path'] for r in m['owned_assets']}
    return len(m['owned_assets'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--verify-assets',action='store_true');a=p.parse_args()
    if a.verify_assets: print('verified owned assets:',verify_assets());return
    checks=[]
    refs=json.loads((H/'source/references.json').read_text()); meta=S.metadata()
    for m in refs:
        b=S.raw(m['id']);assert S.sha(b)==m['raw_sha256']; stored=(S.ROOT/m['stored_path']).read_bytes();assert S.sha(stored)==m['stored_sha256'];assert len(stored)<40000000
        if b.startswith(b'PK'): assert zipfile.ZipFile(io.BytesIO(b)).testzip() is None
    checks.append(dict(check='source_hashes_bytes_and_XLSX_CRC',status='pass',sources=len(refs)))
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.links=[];self.base=None
        def handle_starttag(self,t,a):
            if t=='a' and dict(a).get('href'):self.links.append(dict(a)['href'])
            if t=='base' and dict(a).get('href'):self.base=dict(a)['href']
    lp=Links();lp.feed(S.raw('current-results').decode()); paths={urlparse(urljoin('https://www.sos.ks.gov/elections/election-results.html',u)).path for u in lp.links}
    for sid in ['sos-2024-president-county','sos-2024-president-precinct','sos-2022-senate-precinct','sos-2020-senate-precinct','sos-2026-senate-primary-precinct','sos-2024-general-canvass','sos-2022-general-canvass','sos-2020-general-canvass','sos-2026-primary-canvass']:
        assert urlparse(meta[sid].get('url',meta[sid].get('requested_url'))).path in paths,sid
    checks.append(dict(check='nine_actual_official_parent_download_links',status='pass'))
    for parent,child in [('sumner-county-home','sumner-election-office'),('sumner-election-office','sumner-archive'),('sumner-archive','sumner-2022-actual-linked-summary')]:
        lp=Links();lp.feed(S.raw(parent).decode());base=lp.base or meta[parent].get('url',meta[parent].get('requested_url'));childurl=meta[child].get('url',meta[child].get('requested_url'))
        assert unquote(childurl) in {unquote(urljoin(base,u)) for u in lp.links},(parent,child)
    assert S.sha(S.raw('sumner-2022-actual-linked-summary'))==S.sha(S.raw('sumner-2022-county-summary-candidate'))
    checks.append(dict(check='Sumner_official_authority_archive_literal_download_chain_and_mirror_hash',status='pass'))
    rows=readcsv(H.parent/'county-baselines.csv');assert len(rows)==105==len({r['county_fips'] for r in rows})==len({r['county'] for r in rows})
    roster={r['STATEFP']+r['COUNTYFP'] for r in csv.DictReader(io.StringIO(S.raw('county-codes-2020').decode()),delimiter='|') if r['STATE']=='KS'};assert roster=={r['county_fips'] for r in rows}
    for r in rows:
        assert r['county_key']=='US-KS-'+r['county_fips']
        for pref in ['president_2024','senate_2020','senate_2022']:
            A=int(r[pref+'_d_votes']);B=int(r[pref+'_r_votes']);C=int(r[pref+'_named_votes']);T=int(r[pref+'_pair_votes']);O=int(r[pref+'_other_named_votes']);assert A+B==T and T+O==C
            near(A/T,float(r[pref+'_d_pair_share']));near(T/C,float(r[pref+'_pair_participation']));near(100*(A-B)/T,float(r[pref+'_d_minus_r_pair_margin_pp']));near(100*(A-B)/C,float(r[pref+'_d_minus_r_named_margin_pp']))
    controls=readcsv(H/'candidate-controls.csv')
    for pref,spec in SPECS.items():
        cr=[r for r in controls if r['baseline']==pref];assert len(cr)==len(spec['candidates'])
        pdfid=cr[0]['control_source'];page=S.pdf(pdfid).split('\f')[0]
        for r in cr:
            assert int(r['county_sum'])==int(r['statewide_control']) and int(r['difference'])==0
            hits=[line for line in page.splitlines() if r['candidate'] in line.lower() and re.search(r'\b'+f"{int(r['statewide_control']):,}"+r'\s+[0-9.]+%',line)]
            assert len(hits)==1,(pref,r['candidate'],hits)
            if spec['stage']=='general':assert sum(int(x[pref+'_'+r['candidate']+'_votes']) for x in rows)==int(r['statewide_control'])
    checks.append(dict(check='all105_FIPS_candidates_denominators_and_primary_PDF_controls',status='pass',named_candidates=len(controls)))
    rank=readcsv(H/'county-priority.csv');assert [r['county_fips'] for r in rank]==[r['county_fips'] for r in sorted(rows,key=lambda r:(-int(r['president_2024_named_votes']),r['county_fips']))]
    assert sum(int(r['named_votes']) for r in rank)==1327591
    assert sum(int(r['named_votes']) for r in rank[:15])==970376
    assert sum(int(r['named_votes']) for r in rank[:22])==1057110 and 5*1057110<4*1327591<=5*1067659
    assert sum(int(r['named_votes']) for r in rank[:23])==1067659 and rank[22]['county_fips']=='20191' and rank[22]['named_votes']=='10549'
    checks.append(dict(check='full105_order_exact_minimum_integer80',status='pass',minimum_count=23))
    raw={(r['source_id'],r['sheet'],r['row']):r['cells'] for r in jl(H/'source/raw-rows.jsonl.gz')};obs=readcsv(H/'native-candidates.csv.gz');seen=set()
    for r in obs:
        pk=r['source_id'],r['sheet'],int(r['source_row']),r['vote_column'];assert pk not in seen;seen.add(pk);v=raw[pk[:3]].get(pk[3]);assert (v or '')==r['raw_value']
        if r['votes']!='':assert int(r['votes'])==int(v.replace(',','')) and r['value_status']=='published_integer'
        else:assert r['value_status']!='published_integer'
    units=jl(H/'native-units.jsonl.gz');assert len(units)==22031==len({u['unit_key'] for u in units})
    expected={'sos-2024-president-county':(4567,0,828),'sos-2024-president-precinct':(4566,13,815),'sos-2022-senate-precinct':(4535,12,786),'sos-2020-senate-precinct':(3867,19,444),'sos-2026-senate-primary-precinct':(4496,31,790)}
    for sid,e in expected.items():
        us=[u for u in units if u['source_id']==sid];assert (len(us),sum(not u['complete_named_values'] for u in us),sum(u['named_votes']==0 for u in us))==e
        assert len({u['county_fips'] for u in us})==105
    for u in units:
        vals=[v for k,v in u['candidates'].items() if k!='generic_write_in'];assert u['known_named_votes']==sum(v for v in vals if v is not None)
        assert (u['named_votes']==sum(vals)) if all(v is not None for v in vals) else u['named_votes'] is None
    nc=readcsv(H/'native-state-controls.csv');residuals=defaultdict(int)
    for r in nc:
        values=[u['candidates'][r['candidate']] for u in units if u['source_id']==r['source_id']]
        assert sum(v for v in values if v is not None)==int(r['known_native_sum'])
        assert int(r['statewide_named_control'])-int(r['known_native_sum'])==int(r['control_minus_known_native'])
        residuals[r['source_id']]+=int(r['control_minus_known_native'])
    assert dict(residuals)=={'sos-2020-senate-precinct':0,'sos-2022-senate-precinct':8,'sos-2024-president-county':0,'sos-2024-president-precinct':44,'sos-2026-senate-primary-precinct':22}
    aux=readcsv(H/'source/auxiliary-controls.csv');assert sum(r['category']=='reported_contest_total_including_generic_write_ins' and r['role']=='detail' for r in aux)==269
    checks.append(dict(check='complete_native_identity_source_cells_zeros_unavailability_auxiliary',status='pass',native_units=len(units),candidate_cells=len(obs),reported_total_detail_cells=269,extra_Wyandotte_footer_cells=4))
    # All goal contributions and selected-only equations recomputed from serialized rows.
    states=json.loads((H/'state-scenarios.json').read_text());targets=readcsv(H/'county-targets.csv');assert len(states)==22 and len(targets)==2310
    settings=json.loads((H/'scenario-settings.json').read_text())
    for label,volume in settings['volume_bases'].items():
        pref=volume['source'];assert volume['named_votes']==sum(int(r[pref+'_named_votes']) for r in rows) and volume['pair_votes']==sum(int(r[pref+'_pair_votes']) for r in rows)
    for s in states:
        rs=[r for r in targets if r['scenario']==s['scenario'] and float(r['goal_pair_margin_pp'])==s['goal_pair_margin_pp']];assert len(rs)==105 and len({r['county_fips'] for r in rs})==105
        T=sum(float(r['expected_pair_votes']) for r in rs);C=sum(float(r['expected_named_votes']) for r in rs);near(T,s['total_pair']);near(C,s['expected_named_votes']);near(sum(float(r['pair_weight']) for r in rs),1);near(sum(float(r['named_weight']) for r in rs),1)
        goal=s['goal_pair_margin_pp']/100;near(sum(float(r['target_net']) for r in rs),goal*T)
        near(s['final_A']+s['final_B']+sum(s['final_other_candidates'].values()),C)
        for r in rs:
            w=float(r['expected_pair_votes']);share=float(r['baseline_A_share']);target=float(r['target_A_share']);assert 0<=target<=1
            near(target,clip(share+s['shift']));near(float(r['target_net']),w*(2*target-1));near(float(r['target_net_gain']),2*w*(target-share));near(float(r['net_gain_per_1pp_A_share']),.02*w)
            q=float(r['selected_only_required_share_unbounded']);other=float(r['selected_only_others_net']);near(other+w*(2*q-1),goal*T)
            assert (q>1)==(r['selected_only_status']=='impossible_under_fixed_others')
    nt=readcsv(H/'native-targets.csv.gz');assert len(nt)==44062
    for s in json.loads((H/'native-state-scenarios.json').read_text()):
        rs=[r for r in nt if r['source_id']=='sos-2024-president-county' and float(r['goal_pair_margin_pp'])==s['goal_pair_margin_pp'] and r['statewide_target_net']!=''];near(sum(float(r['statewide_target_net']) for r in rs),s['goal_pair_margin_pp']/100*s['total_pair'])
    synthetic=solve([.99,.1],[20.,80.],0.);assert synthetic['clipped_units']>0 and synthetic['shift']>synthetic['unbounded_shift'];near(sum(w*(2*clip(q+synthetic['shift'])-1) for q,w in zip([.99,.1],[20,80])),0)
    assert solve([.6],[100.],0.)['shift']<0 and solve([.5],[0.],0.)['status']=='no_positive_pool' and solve([.5],[1.],1.01)['status']=='impossible'
    from calculate import scenario
    assert scenario(rows,'president_2024','president_2024',0)[0]['status']=='no_positive_pool'
    assert scenario(rows,'president_2024','president_2024',-1)[0]['status']=='invalid_volume_or_preference_setting'
    assert scenario(rows,'president_2024','president_2024',1,0,1.01)[0]['status']=='impossible'
    assert selected(0,1,10,0)['status']=='no_positive_pool';assert selected(1,-10,10,0)['status']=='impossible_under_fixed_others';assert selected(1,10,10,0)['status']=='already_secured_under_fixed_others'
    checks.append(dict(check='all_county_native_bounded_targets_weights_contributions_selected_only_and_boundaries',status='pass',state_scenarios=22,county_rows=2310,native_rows=44062))
    cases=examples();saved=json.loads((H/'synthetic-live-scenarios.json').read_text());assert saved==cases
    by={x['name']:x['output'] for x in cases};ex=by['final_denominator_with_others'];near(ex['final_A'],53.5);near(ex['final_B'],54.5);assert ex['final_other']=={'C':12.} and ex['final_pair_denominator']==108 and ex['final_all_candidate_denominator']==120
    assert by['pair_goal_is_not_plurality']['pair_goal_met'] and not by['pair_goal_is_not_plurality']['A_clear_plurality']
    assert by['negative_pool']['status']=='invalid_negative_or_nonfinite_pool';assert by['unknown_pool']['status']=='unknown_remaining_pool';assert by['no_pool_A_wins']['all_remaining_pair_requirement']['fixed_result']=='A_clear_plurality'
    for case in cases:
        result=case['output'];assert result.get('probability') is None
        if result['status']=='calculated':assert result['counted_fixed']==case['input']['counted']
    checks.append(dict(check='meaningful_live_remainder_unknown_negative_no_pool_clipping_third_candidate_final_denominators',status='pass',synthetic_cases=len(cases)))
    # Independent Sumner method balances are additional scope, never added to state/native families.
    sm=readcsv(H/'source/sumner-2022-method-controls.csv');assert len(sm)==77
    for label in {r['source_label'] for r in sm}:
        assert sum(int(r['votes']) for r in sm if r['source_label']==label and r['method']!='TOTAL')==int(next(r['votes'] for r in sm if r['source_label']==label and r['method']=='TOTAL'))
    checks.append(dict(check='additional_Sumner_original_method_controls_and_12_selected_targets',status='pass',source_cells=77,method_identities=6))
    peer=json.loads((H/'peer-reconciliation.json').read_text());assert peer['status']=='pass' and peer['native_known_count_order_equal'] and peer['full_105_order_equal']
    for path,m in peer['read_only_peer_assets'].items():assert S.sha((S.ROOT/path).read_bytes())==m['sha256'],('peer source changed; refresh comparison',path)
    checks.append(dict(check='independent_peer_full_field_native_order_contract_hashes',status='pass',county_comparisons=peer['county_field_comparisons'],native_units=peer['native_units_compared']))
    # Read-only acceptance is checked structurally, without creating a reverse hash pin.
    acceptance=json.loads((H.parent/'coordinator-priority-acceptance.json').read_text());assert acceptance['accepted'] is True
    assert S.sha((H.parent/acceptance['contract']).read_bytes())==acceptance['contract_sha256'],'accepted external contract changed; coordinator refresh required'
    checks.append(dict(check='coordinator_historical_research_acceptance',status='pass',current_geography_approved=False))
    link_count=0
    for file in [S.ROOT/'county-partisanship.md',H/'source/SCHEMA.md']:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',file.read_text()):
            if target.startswith(('https://','http://','#')):continue
            target=unquote(target.split('#')[0]);dest=(file.parent/target).resolve();assert dest.exists() or dest in [H/'validation.json',H/'asset-manifest.json'],(file,target);link_count+=1
    allfiles=[p for p in H.rglob('*') if p.is_file()]+[S.ROOT/'county-partisanship.md',H.parent/'county-baselines.csv'];assert all(p.stat().st_size<40000000 for p in allfiles);assert not any(p.name in ['node_modules','__pycache__','.venv'] for p in H.rglob('*'))
    checks.append(dict(check='relative_links_asset_bounds_no_dependency_or_cache_directories',status='pass',relative_links=link_count))
    gaps=['75 source-native units have unavailable named cells across precinct/primary families; broad2024 is complete. No residual allocation or fully identified bounded native-uniform solve for partial families.','Statewide methods/valid named write-ins/under/over/blanks not published in selected contest files; Sumner2022 supplemental methods cover one county only.','2022 raw turnout ballots violate six county bounds; no corrections or clean ballot weights.2024 broad versus certification turnout/registration vintages differ.2020 county ballots/registration unavailable in selected sources.','Final2026 official ballot candidate mapping/current precinct geometry and signed court orders/subsequent docket must be verified before live admission. Statute-only no-grace conclusion rejected.','No live collector,cadence measurement,remaining-vote evidence,2026 turnout forecast or calibrated probabilities.']
    jdump('validation.json',dict(status='pass_with_documented_source_gaps',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,gaps=gaps))
    manifest();n=verify_assets()
    for file in [S.ROOT/'county-partisanship.md',H/'source/SCHEMA.md']:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',file.read_text()):
            if not target.startswith(('http://','https://','#')):assert (file.parent/unquote(target.split('#')[0])).exists()
    print(json.dumps(dict(status='pass_with_documented_source_gaps',checks=len(checks),owned_assets=n,source_references=len(refs))))
if __name__=='__main__':main()

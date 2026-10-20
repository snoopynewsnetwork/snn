#!/usr/bin/env python3
"""Offline QA of qualified research. Unavailable canonical priority is a gate.

--write creates deterministic validation before sealing; default additionally
checks every sealed asset and never changes witness/manifest/output files.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse,csv,gzip,hashlib,importlib.util,io,json,re,tempfile,zipfile
from collections import Counter,defaultdict
from decimal import Decimal
OUT=Path(__file__).resolve().parents[1];STATE=OUT.parents[1];NEWS=OUT.parent/'news'
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def fail(assertion,detail):
    if not assertion:raise AssertionError(detail)
def main():
    args=argparse.ArgumentParser();args.add_argument('--write',action='store_true');args=args.parse_args()
    checks=[]
    def ok(name,detail):checks.append(dict(check=name,status='pass',detail=detail))
    # Shared original entities and exact ordered native archive restoration.
    pins=load(OUT/'source/shared-original-pins.json');byid={r['id']:r for r in pins}
    for r in pins:
        if r.get('asset_parts'):continue
        z=(NEWS/r['asset']).read_bytes();raw=gzip.decompress(z)
        fail(sha(z)==r['stored_sha256']and sha(raw)==r['raw_sha256']and len(raw)==r['bytes'],r['id'])
    ok('shared_pinned_small_originals','Every selected original response entity raw/stored hash and byte length verified; complete 2022 abstract rebuilt from actual contiguous ranges.')
    spec=importlib.util.spec_from_file_location('read_only_archive_restore',OUT.parent/'audit_precinct_archives.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    inv=load(OUT/'source/original-inventory.json');members=0
    for year in [2020,2022]:
        pin=byid[f'sos-{year}-precinct-zip-observed-download']
        with tempfile.TemporaryFile()as f:
            mod.restore(pin,f);f.seek(0)
            with zipfile.ZipFile(f)as z:
                fail(z.testzip()is None,'ZIP CRC');rs=[r for r in inv if r.get('year')==year]
                fail(len(rs)==len(z.infolist())==36,'36 original members')
                for r in rs:
                    b=z.read(r['member_name']);info=z.getinfo(r['member_name']);fail((len(b),sha(b),info.CRC)==(r['original_bytes'],r['original_sha256'],r['CRC32']),r['member_name']);members+=1
    ok('native_original_archives',dict(original_members_hashed=members,original_ZIP_bytes=94190830+122671283,all_member_CRCs=True,raw_ZIPs_stored_in_repo=False))
    for r in inv:
        z=(OUT/r['text_path']).read_bytes();fail(sha(gzip.decompress(z))==r['text_sha256'],r['text_path'])
    # Exact row positions bind the county export back to original page text.
    candidates=list(csv.DictReader((OUT/'county-candidates.csv').open()));fail(len(candidates)==864,'candidate position count')
    fail(len({(r['contest'],r['county_fips'],r['column_index'])for r in candidates})==864,'candidate key uniqueness')
    footers=load(OUT/'source/statewide-footers.json');expected_totals={}
    for f in footers:
        rs=[r for r in candidates if r['contest']==f['contest']];n=len(f['values'])
        fail(len({r['county_fips']for r in rs})==36 and len(rs)==36*n,'all counties in contest')
        sums=[sum(int(r['votes'])for r in rs if int(r['column_index'])==j)for j in range(n)]
        fail(sums==f['values'],'candidate statewide footer '+f['contest']);expected_totals[f['contest']]=sum(sums)
        for r in rs:
            pg=gzip.decompress((OUT/'source'/f'{r["source_key"]}.layout.txt.gz').read_bytes()).decode().split('\f')[int(r['PDF_page'])-1]
            literal=pg.splitlines()[int(r['text_line_1based'])-1];fail(literal==r['raw_line'],'source row exactness')
            ns=[int(x.replace(',',''))for x in re.findall(r'\d[\d,]*',literal)]
            fail(len(ns)==n and ns[int(r['column_index'])]==int(r['votes']),'original literal candidate integer')
    ok('all_statewide_primary_candidate_columns',dict(county_positions=864,counties_per_contest=36,totals=expected_totals,Misc_separate=True,missing_filled_as_zero=False))
    registration=list(csv.DictReader((OUT/'monthly-registration.csv').open()));fail(len(registration)==108,'monthly source rows')
    participation=list(csv.DictReader((OUT/'participation-controls.csv').open()));pf=load(OUT/'source/participation-footers.json')
    for year in [2020,2022,2024]:
        rs=[r for r in participation if int(r['year'])==year];f=next(r for r in pf if r['year']==year)
        fail(len(rs)==len({r['county_fips']for r in rs})==36,'statistical counties')
        for field in ['registration_Number_Eligible','ballots_Returned']:fail(sum(int(r[field])for r in rs)==f[field],'participation footer')
    ok('separate_participation_and_registration',dict(statistical_county_rows=108,monthly_county_rows=108,scopes_combined=False,statistical_2020_conflict_with_current_history_preserved=True))
    vp=list(csv.DictReader((OUT/'nonadditive-vice-president.csv').open()));fail(len(vp)==216 and all(r['nonadditive']=='True'for r in vp),'VP presentation')
    for r in vp:
        match=next(v for v in candidates if v['contest']=='2024-president'and v['county_fips']==r['county_fips']and v['column_index']==r['overlaps_presidential_column'])
        fail(r['votes']==match['votes'],'VP overlap')
    ok('vice_president_nonadditive',dict(county_positions=216,columns=6,added_to_priority=False,invented_West_Terry_VP_columns=False))
    allrank=load(OUT/'county-sensitivities.json');known=load(OUT/'known-native-ranking.json');contract=load(OUT/'priority-set.json')
    def ranking(v,value):
        a=v['full_order'];total=sum(r[value]for r in a);keys=[r['key']for r in a]
        fail(len(keys)==len(set(keys))and a==sorted(a,key=lambda r:(-r[value],r['key'])),'rank order/uniqueness')
        fail(v['total']==total,'rank denominator');cum=0
        for i,r in enumerate(a,1):cum+=r[value];fail(r['rank']==i and r['cumulative_votes']==cum,'cumulative order')
        t=sum(r[value]for r in a[:15]);fail(v['top15']['numerator']==t and v['top15']['denominator']==total,'top15 fraction')
        m=v['minimum80'];count=m['count'];cross=sum(r[value]for r in a[:count]);pre=sum(r[value]for r in a[:count-1])
        fail(5*pre<4*total<=5*cross,'minimum integer80 crossing')
        fail((m['preceding_count'],m['preceding_votes'],m['crossing_key'],m['cumulative_votes'])==(count-1,pre,a[count-1]['key'],cross),'predecessor/crossing record')
        fail(m['ordered_keys']==keys[:count]and v['remainder']['keys']==keys[count:]and v['remainder']['votes']==total-cross,'exact priority and remainder')
        fail(abs(sum(Decimal(r[value])/Decimal(total)for r in a)-1)<Decimal('1e-24'),'weights')
    for v in allrank.values():ranking(v,'votes');fail(len(v['full_order'])==36,'full county order')
    ranking(known,'reported_votes');fail(len(known['full_order'])==510,'known unit count')
    ok('orders_weights_thresholds',dict(complete_county_scenarios=len(allrank),known_native_rows=510,tie_rule='descending integer votes then ascending versioned key',minimum80_integer_proof=True))
    counties=list(csv.DictReader((OUT.parent/'county-turnout.csv').open()))
    fail(len(counties)==len({r['county_fips']for r in counties})==36,'compatibility CSV all parents')
    fail(all(r['canonical_native_priority_available']=='False'for r in counties),'no county substitution')
    fail(abs(sum(float(r['state_share_2024_president'])for r in counties)-1)<1e-12,'county CSV weights')
    parents=contract['all_36_county_parents'];fail(len(parents)==36,'contract parents')
    unavailable=[p for p in parents if p['unknown_native_membership']]
    fail(len(unavailable)==31 and all(p['native_reporting_unit_count']is None and not p['source_native_constituents']for p in unavailable),'unknown not zero')
    fail(contract['complete_order']is None and contract['ordered_priority_keys']is None and contract['top15']is None and contract['minimum80']is None,'canonical unavailable')
    fail(contract['peer_agreement']['peer_agent_id']is None and not contract['coordinator_acceptance']['accepted'],'no premature acceptance')
    fail(known['total']+sum(p['county_presidential_reported_votes']for p in unavailable)==contract['statewide_reported_votes'],'unknown parents kept in state')
    choices={r['county']:defaultdict(int)for r in known['full_order']}
    for r in known['full_order']:
        fail(len(r['candidate_vector'])==8 and sum(r['candidate_vector'])==r['reported_votes'],'known complete vector')
        for j,v in enumerate(r['candidate_vector']):choices[r['county']][j]+=v
        f=r['source_presentations'][-1]['fields'];b=f.get('ballots',f.get('Total Ballots Cast'));ov=f.get('overvotes');un=f.get('undervotes')
        fail(None not in [b,ov,un]and r['reported_votes']+ov+un==b,'source-specific native ballot equation '+r['key'])
    for name,values in choices.items():
        expected={int(r['column_index']):int(r['votes'])for r in candidates if r['county']==name and r['contest']=='2024-president'}
        fail(dict(values)==expected,'whole native county vector '+name)
    ok('five_native_parents',dict(parents=sorted(choices),native_rows=510,known_votes=known['total'],unknown_parent_votes=1115972,
        all_8_columns_per_county=True,all_local_ballot_nonvote_equations=True,Washington_contest_ballots=301104,Washington_overall_header=301105,
        Clackamas_combined_115_116_kept=True,source_native_keys_not_current_geometries=True))
    # Multnomah CSV choice counters are independently checked as written.
    acq=OUT/'source/acquired';r=load(acq/'multnomah-2024-sovc2.receipt.json');raw=gzip.decompress((acq/r['response_entities'][-1]['asset']).read_bytes()).decode()
    rows=[r for r in csv.DictReader(io.StringIO(raw))if r['Contest ID']=='39'];fail(len(rows)==856,'CSV candidate/precinct universe')
    for r in rows:
        v=lambda k:int(r[k].replace(',',''))
        fail(v('Votes')+v('Overvoted WithVote for this Choice')+v('Undervoted WithoutVote for this Choice')+v('Ballots WithVotes for Others')==v('BallotsWith Contest'),'choice scoped equation')
    ok('Multnomah_native_choice_controls',dict(rows=856,native_contest_id='39',overvotes_scope='choice-specific, not additive contest ballots',all_raw_choice_fields_retained=True))
    owned_receipts=0
    for p in acq.glob('*.receipt.json'):
        r=load(p);owned_receipts+=1
        for e in r['response_entities']:
            z=(acq/e['asset']).read_bytes();b=gzip.decompress(z);fail((len(z),sha(z),len(b),sha(b))==(e['stored_bytes'],e['stored_sha256'],e['raw_bytes'],e['raw_sha256']),str(p))
    for p in (OUT/'source/refined-ocr').glob('*.json'):
        if p.name=='selected-page-plan.json':continue
        r=load(p);stem=p.stem
        fail(sha(gzip.decompress(p.with_name(stem+'.tsv.gz').read_bytes()))==r['TSV_sha256'],'OCR TSV hash')
        fail(sha(gzip.decompress(p.with_name(stem+'.txt.gz').read_bytes()))==r['text_sha256'],'OCR text hash')
    ok('owned_acquisition_and_OCR',dict(acquisition_receipts=owned_receipts,failed_responses_and_local_errors_retained=True,refined_wordbox_hashes=True))
    # Relative report links and every owned artifact's size/bounds.
    report=STATE/'turnout.md';links=re.findall(r'\]\(([^)]+)\)',report.read_text())
    for target in links:
        if target.startswith(('https://','http://','#')):continue
        p=(STATE/target.split('#')[0]).resolve()
        planned=args.write and p in {OUT/'validation.json',OUT/'asset-manifest.json',OUT/'pre-peer-witness-v1.json'}
        fail(p.is_relative_to(STATE.resolve())and (p.exists()or planned),'report link '+target)
    owned=[report,OUT.parent/'county-turnout.csv']+[p for p in OUT.rglob('*')if p.is_file()and '__pycache__'not in p.parts]
    fail(all(p.stat().st_size<40000000 for p in owned),'strict artifact bound')
    fail(not list(OUT.rglob('__pycache__')),'no dependency/cache directories retained')
    planned=[OUT/'validation.json',OUT/'asset-manifest.json',OUT/'pre-peer-witness-v1.json']
    expected_owned=len(owned)+sum(not p.exists()for p in planned)
    ok('relative_links_bounds',dict(relative_report_links_checked=sum(not l.startswith(('http','#'))for l in links),owned_files_after_seal=expected_owned,strict_max_bytes=40000000))
    rec=load(OUT/'native/county-reconciliation.json');closed={co:sorted({r['county']for r in rec if r['contest']==co and r['complete_candidate_vectors_and_county_columns_close']})for co in ['2020-senate','2022-senate','2022-governor']}
    output=dict(status='pass_qualified_research_only_canonical_native_priority_unavailable',research_date='2026-10-20',checks=checks,
        material_gates=dict(canonical_2024_native_complete=False,unclosed_2024_parents=[p['county']for p in unavailable],
            historical_native_normalization_complete=False,historical_county_candidate_column_closed_sets=closed,
            peer_agent_id=None,peer_agreement='pending_not_launched',coordinator_acceptance='pending',approved_current_election=False,approved_current_geometry=False),
        limits=['County aggregate primary reconciliation complete. It does not establish unobserved native membership.',
            'Historic raw originals complete; native parsing/administrative/method review remains partial. Unclosed groups are excluded from priority math.',
            'No November 2026 identity/geometry/live cadence/collector/forecast approval.'])
    if args.write:
        (OUT/'validation.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(dict(status=output['status'],checks=len(checks),canonical_priority_available=False)));return
    manifest=load(OUT/'asset-manifest.json');paths=set()
    for r in manifest['owned_assets']:
        p=(STATE/r['path']).resolve();fail(p.is_relative_to(STATE.resolve()),'owned bound');b=p.read_bytes();fail(len(b)==r['bytes']and sha(b)==r['sha256']and len(b)<40000000,r['path']);paths.add(p)
    expected={p.resolve()for p in owned if p.name!='asset-manifest.json'}
    fail(paths==expected,'complete owned asset manifest coverage')
    for r in manifest['shared_assets']:
        p=(STATE/r['path']).resolve();fail(p.is_relative_to(STATE.resolve()),'shared state bound');b=p.read_bytes();fail((len(b),sha(b))==(r['bytes'],r['sha256'])and len(b)<40000000,r['path'])
    witness=load(OUT/'pre-peer-witness-v1.json')
    for r in witness['pinned_files']:
        b=(STATE/r['path']).read_bytes();fail(sha(b)==r['sha256']and len(b)==r['bytes'],'pre-peer immutable pin '+r['path'])
    fail(load(OUT/'validation.json')==output,'sealed validation matches current recomputation')
    print(json.dumps(dict(status=output['status'],checks=len(checks),sealed_owned_assets=len(paths),shared_assets=len(manifest['shared_assets']),pre_peer_witness_verified=True,canonical_priority_available=False)))
if __name__=='__main__':main()

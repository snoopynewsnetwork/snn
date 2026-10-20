#!/usr/bin/env python3
"""Independent source, exact-rational piecewise, coverage and publication audits.
No producer calculator/extractor imports. --audit is read-only and requires manifest.
"""
import argparse,collections,csv,gzip,hashlib,io,json,math,pathlib,re,sys,tarfile,zipfile
from fractions import Fraction as F
BASE=pathlib.Path(__file__).resolve().parent;STATE=BASE.parent.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def close(a,b,tol=2e-6):assert abs(float(a)-float(b))<=tol,(a,b)
def scope_files():return sorted([STATE/'county-partisanship.md',STATE/'data/county-baselines.csv']+[p for p in BASE.rglob('*') if p.is_file()])
def piecewise(units,ai,bi,target):
    points=collections.defaultdict(F);T=F(0);M=F(0);full=F(0);qs=[]
    for u in units:
        v=u['votes'];pair=v[ai]+v[bi];f=sum(v);volume=F(str(u.get('volume',f)));full+=volume
        w=volume*F(pair,f) if f else F(0);q=F(v[ai],pair) if pair else None;T+=w
        if w:
            M+=w*(2*q-1);points[-q]+=2*w;points[1-q]-=2*w
        qs.append((w,q))
    goal=F(str(target))*T;position=F(-1);value=-T;slope=F(0);root=None
    for x,change in sorted(points.items()):
        next_value=value+slope*(x-position)
        if slope>0 and value<=goal<=next_value:root=position+(goal-value)/slope;break
        value=next_value;position=x;slope+=change
    if root is None and goal==T:root=F(1)
    assert root is not None
    return T,M,full,root,(goal-M)/(2*T),qs
def main(audit=False):
    if audit:
        manifest=read(BASE/'asset-manifest.json');actual={str(p.relative_to(STATE)):p for p in scope_files() if p!=BASE/'asset-manifest.json'}
        assert set(actual)=={x['path'] for x in manifest['assets']},'manifest membership differs'
        for x in manifest['assets']:
            p=actual[x['path']];assert p.stat().st_size==x['bytes'] and sha(p.read_bytes())==x['sha256'] and x['bytes']<40000000
        for p in [STATE/'county-partisanship.md',BASE/'source/SCHEMA.md']:
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                if not re.match(r'https?://|#',target):assert (p.parent/target.split('#')[0]).exists(),target
        print(json.dumps({'read_only_final_audit':'pass','assets':len(actual),'manifest_sha256':sha((BASE/'asset-manifest.json').read_bytes()),'all_stored_files_strictly_below_40000000':True}));return
    import xlrd
    books=read(BASE/'source/typed-workbooks.json.gz');native=read(BASE/'source/native-observations.json.gz');county=read(BASE/'source/county-observations.json');inv=read(BASE/'source/independent-inventory.json');results=[]
    refs=read(BASE/'source/original-references.json')+read(BASE/'source/supplementary-original-references.json');source_bodies={};source_audit=[]
    for r in refs:
        d=r['metadata'];parts=[]
        for part in d['parts']:
            p=BASE.parent/'turnout'/part['path'];b=p.read_bytes();assert sha(b)==part['sha256'] and len(b)==part['bytes'] and len(b)<40000000;parts.append(b)
        raw=gzip.decompress(b''.join(parts));assert sha(raw)==d['original_sha256'] and len(raw)==d['original_bytes'];source_bodies[sha(raw)]=raw;source_audit.append({'sha256':sha(raw),'bytes':len(raw),'stored_parts':len(parts)})
    for d in [read(p) for p in (BASE/'source').glob('*.receipt.json')]:
        if 'asset' in d:
            b=(STATE/'data/news'/d['asset']).read_bytes();assert sha(b)==d['stored_sha256'] and sha(gzip.decompress(b))==d['raw_sha256'] and len(b)<40000000
    for p in (BASE/'source/http').glob('*.receipt.json'):
        d=read(p);b=(BASE/d['stored_path_relative_baselines']).read_bytes();assert sha(b)==d['stored_sha256'] and len(b)==d['stored_bytes'];raw=gzip.decompress(b);assert sha(raw)==d['original_sha256'] and len(raw)==d['original_bytes']
    checked_cells=0;checked_members=0;source_sums={};jefferson={}
    for year in [2024,2022,2020]:
        original=next(r for r in refs if str(year) in r['metadata']['requested_url'] and r['metadata']['requested_url'].endswith('.zip'));z=zipfile.ZipFile(io.BytesIO(source_bodies[original['original_sha256']]))
        assert len(z.infolist())==67 and z.testzip() is None
        year_sums=collections.defaultdict(int)
        for ob in [x for x in books if x['year']==year]:
            raw=z.read(ob['member']);assert sha(raw)==ob['member_sha256'];checked_members+=1;wb=xlrd.open_workbook(file_contents=raw,formatting_info=True)
            for s in ob['sheets']:
                ws=wb.sheet_by_name(s['name']);cols=[c-1 for c in s['native_columns_1based']]
                for row in s['selected_rows']:
                    r=row['row']-1
                    for c,(typ,val) in enumerate(row['cells']):assert (ws.cell_type(r,c),ws.cell_value(r,c))==(typ,val);checked_cells+=1
                    literal=str(ws.cell_value(r,2)).strip();contest=str(ws.cell_value(r,0)).strip()
                    wanted=contest==('PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES' if year==2024 else 'UNITED STATES SENATOR') and literal not in ('Over Votes','Under Votes')
                    if wanted:
                        vals=[ws.cell_value(r,c) for c in cols];assert all(ws.cell_type(r,c)==2 for c in cols);v=sum(int(x) for x in vals);year_sums[literal]+=v
                        if year==2024 and ob['county']=='Jefferson':jefferson[literal]={'row':r+1,'sum':v}
        source_sums[str(year)]=dict(year_sums)
    assert jefferson['Jill Stein']=={'row':12,'sum':994} and jefferson['Chase Oliver']=={'row':13,'sum':731}
    controls=read(BASE/'source/canvass-state-controls.json');pdfrows=read(BASE/'source/canvass-county-cells.json')
    for control in controls:
        year=control['year']
        for c in control['candidate_cells']:
            assert source_sums[str(year)][c['candidate']]==c['value']
            assert sum(r['candidate_cells'][i]['value'] for r in pdfrows if r['year']==year for i in range(len(r['candidate_cells'])) if r['candidate_cells'][i]['candidate']==c['candidate'] and r['candidate_cells'][i]['value'] is not None)==c['value']
    assert len(read(BASE/'source/canvass-xls-disagreements.json'))==3
    for iv in inv:
        year=iv['year'];nr=[u for u in native if u['year']==year];cr=[u for u in county if u['year']==year];assert len(cr)==67 and len({u['county_fips'] for u in nr})==67
        assert len(nr)==iv['native_count'] and len({u['key'] for u in nr})==len(nr)
        for c in cr:
            children=[u for u in nr if u['county_fips']==c['county_fips']]
            for cand in c['candidate_rows']:
                assert cand['votes']==sum(next(x['votes'] for x in u['candidate_rows'] if x['candidate_literal'].strip()==cand['candidate_literal'].strip()) for u in children)
        for level,rows in [('native',nr),('county',cr)]:
            ordered=sorted(rows,key=lambda r:(-r['reported_contest_votes'],r['key']));v=iv[level];assert [x['key'] for x in ordered]==[x['key'] for x in v['full_order']]
            cumulative=0;den=sum(r['reported_contest_votes'] for r in ordered);cross=None
            for i,u in enumerate(ordered,1):
                cumulative+=u['reported_contest_votes'];assert v['full_order'][i-1]['cumulative_votes']==cumulative
                if cross is None and cumulative*5>=den*4:cross=i
            assert cross==v['minimum80_count'];assert v['priority_keys']==[u['key'] for u in ordered[:cross]];assert v['remainder_keys']==[u['key'] for u in ordered[cross:]]
    for p in sorted((BASE/'scenarios').glob('*.input.json.gz')):
        d=read(p);r=read(pathlib.Path(str(p).replace('.input.','.result.')));ids=[c['id'] for c in d['candidates']];ai,bi=[ids.index(n) for n in d['pair']]
        T,M,full,root,unbounded,qs=piecewise(d['units'],ai,bi,d['target_pair_margin'])
        close(T,r['final_pair_denominator']);close(full,r['final_full_candidate_denominator']);close(M,r['baseline_pair_net_votes']);close(root,r['common_shift']['bounded_share_shift'],1e-12);close(unbounded,r['common_shift']['unbounded_share_shift'],1e-12)
        independent_net=F(0)
        for src,out,(w,q) in zip(d['units'],r['units'],qs):
            assert src['key']==out['key']
            close(w,out['pair_pool']);close(F(2,100)*w,out['one_share_point_net_gain']);close(w/T,out['remaining_pair_weight'],1e-12)
            if w:
                share=max(F(0),min(F(1),q+root));net=w*(2*share-1);independent_net+=net;close(share,out['target_a_share'],1e-12);close(net,out['target_remaining_pair_net']);raw=(F(str(d['target_pair_margin']))*T-(M-w*(2*q-1))+w)/(2*w);close(raw,out['selected_only_required_a_share_raw'],1e-9)
            else:assert q is None and out['target_a_share'] is None
        assert independent_net==F(str(d['target_pair_margin']))*T
        close(sum(x['votes'] for x in r['target_candidates']),full)
        results.append({'scenario':p.name,'independent_method':'exact-rational piecewise breakpoint sweep; no producer import','root':float(root),'net_residual_exact':'0','units_checked':len(qs)})
    peer=read(BASE/'peer-reconciliation.json');assert not peer['differences'];assert all(v['same_keys'] and v['full_raw_candidate_order_equal'] for v in peer['checks'].values())
    archive=tarfile.open(BASE/'source/frozen-turnout-peer.tar.gz');contract=json.loads(archive.extractfile('data/turnout/priority-set.json').read());parents=read(BASE/'all67-parent-contract.json')
    for p in parents:
        pp=next(x for x in contract['parents'] if x['county_fips']==p['county_fips']);assert p['full_keys']==pp['constituent_keys'];assert p['priority_keys']==pp['priority_constituent_keys'];assert p['remainder_keys']==pp['remainder_constituent_keys']
    bp=read(BASE/'source/ballot-registration-controls.json');peerbp=json.loads(archive.extractfile('data/turnout/ballot-registration-controls.json').read());other=peerbp['county_rows']+peerbp['statewide'];ballot_diffs=[]
    for row in bp:
        pr=next(x for x in other if x['year']==row['year'] and x['county_fips']==row['county_fips'])
        for a,b in [('registered_voters','registered_voters'),('ballots_cast','ballots_cast'),('democrat_ballots_or_straight_party','democrat_ballots'),('republican_ballots_or_straight_party','republican_ballots'),('absentee_ballots','absentee_ballots')]:
            if row[a]!=pr[b]:ballot_diffs.append({'year':row['year'],'county_fips':row['county_fips'],'field':a,'own':row[a],'peer':pr[b]})
    assert not ballot_diffs
    cli=read(BASE/'cli-validation.json');assert cli['actual_cli_cases']==cli['passed']
    badlinks=[]
    for p in [STATE/'county-partisanship.md',BASE/'source/SCHEMA.md']:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if re.match(r'https?://|#',target):continue
            q=(p.parent/target.split('#')[0]);
            if not q.exists() and q not in (BASE/'final-seal.json',BASE/'asset-manifest.json'):badlinks.append({'file':str(p),'link':target})
    assert not badlinks,badlinks
    files=scope_files();assert all(p.stat().st_size<40000000 for p in files);assert not any('__pycache__' in p.parts or 'node_modules' in p.parts for p in files)
    out={'status':'pass','source_members_reopened':checked_members,'raw_typed_cells_rechecked':checked_cells,'source_sums_by_literal_candidate':source_sums,'jefferson_literal_order_regression':jefferson,'source_original_hash_checks':source_audit,'native_counts':{str(x['year']):x['native_count'] for x in inv},'whole_state_candidate_balances':'all primary known county/native/state cells agree by named literal candidate; three source-null versus explicit zero observations retained','all67_parents_and_full_priority_remainder_peer_equal':True,'ballot_registration_peer_numeric_cells_checked':len(bp)*5,'ballot_registration_peer_differences':ballot_diffs,'scenario_piecewise_proofs':results,'cli_cases_passed':cli['passed'],'relative_links':'pass','strict_stored_file_bound':40000000,'owned_files_observed_before_seal_manifest':len(files),'external_qualifications':{'coordinator_acceptance':False,'current_2026_native_geography_approved':False,'eligible_named_writein_allocation_known':False,'november_live_remainder_known':False,'calibrated_probability':False,'collector_implemented':False}}
    (BASE/'validation.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({'status':'pass','members':checked_members,'typed_cells':checked_cells,'piecewise_scenarios':len(results),'cli_cases':cli['passed']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--audit',action='store_true');args=p.parse_args();main(args.audit)

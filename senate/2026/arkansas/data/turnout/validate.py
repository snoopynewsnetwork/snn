#!/usr/bin/env python3
"""Independent offline source/rank/provenance QA. Default is read-only.

--write records validation.json before sealing. --sealed verifies manifest
membership and hashes and never writes. No build module or peer is imported.
"""
import argparse, collections, csv, decimal, gzip, hashlib, io, json, pathlib, re
import tarfile, urllib.parse, xml.etree.ElementTree as ET, zipfile, subprocess, tempfile
P=pathlib.Path(__file__).resolve().parent;S=P.parents[1];REPO=P.parents[4]
def sha(b):return hashlib.sha256(b).hexdigest()
def owned():return sorted([S/'turnout.md',S/'data/county-turnout.csv']+[f for f in P.rglob('*') if f.is_file()])
def load(path):return json.loads(path.read_text())
def gzload(path):return json.loads(gzip.decompress(path.read_bytes()))
def receipt_body(r,path):
    src=REPO/r['shared_original_path'] if r.get('shared_original_path') else path.parent/r['asset']
    stored=src.read_bytes();assert sha(stored)==r['stored_sha256'],str(src)
    raw=gzip.decompress(stored);assert sha(raw)==r['raw_sha256'],str(path)
    expected=r.get('raw_bytes',r.get('bytes'));assert len(raw)==expected,(path,expected,len(raw))
    assert len(stored)<40000000
    return raw
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--sealed',action='store_true');args=ap.parse_args();assert not(args.write and args.sealed)
    result={'status':'pass','peer_agreement':'unavailable: peer not launched; coordinator acceptance pending','tests':{}}
    tests=result['tests'];receipts={};bodies={}
    for f in sorted((P/'source').glob('*.receipt.json'))+sorted((P/'source/acquired').glob('*.receipt.json')):
        r=load(f);b=receipt_body(r,f);receipts[r['id']]=r;bodies[r['id']]=b
        if 'http' in r:assert r['http']['http_code']==200 and r['curl_returncode']==0
        else:assert r['status']==200
    tests['original_receipt_hash_size_status_checks']=len(receipts)
    failed=list((P/'history/acquisition-timeout').glob('*.receipt.json'));assert len(failed)==4
    for f in failed:
        r=load(f);raw=receipt_body(r,f);assert len(raw)==0 and r['http']['http_code']==0 and r['curl_returncode']==35
    tests['retained_failed_original_receipts_and_empty_body_hashes']=len(failed)
    assert len(list((P/'source/acquired').glob('*.receipt.json')))==471
    # Independent streaming OOXML reader, with source row positions.
    z=zipfile.ZipFile(io.BytesIO(bodies['sos-2024-general-precinct-original']));ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    leaves={};candidate_totals=collections.defaultdict(int);methods=collections.defaultdict(int);raw_positions=[];row_methods=[];allrows=0
    for event,e in ET.iterparse(io.BytesIO(z.read('xl/worksheets/sheet1.xml')),events=('end',)):
        if e.tag!=ns+'row':continue
        vals=[]
        for c in e:
            v=c.find(ns+'v');vals.append(strings[int(v.text)] if c.get('t')=='s' else v.text if v is not None else None)
        if e.get('r')=='1':assert vals==['county','precinct','contest','choice','party','Election Day','Early Vote','Absentee','Provisional','total votes'];continue
        allrows+=1
        if vals[2]=='U.S. President':
            pair=tuple(vals[:2]);leaf=leaves.setdefault(pair,dict(candidates={},methods=[0,0,0,0],positions=[]))
            assert vals[3] not in leaf['candidates'];v=int(vals[9]);ms=list(map(int,vals[5:9]));assert sum(ms)==v
            leaf['candidates'][vals[3]]=v;leaf['positions'].append(int(e.get('r')))
            for i,x in enumerate(ms):leaf['methods'][i]+=x;methods[vals and ['Election Day','Early Vote','Absentee','Provisional'][i]]+=x
            candidate_totals[vals[3]]+=v;raw_positions.append(int(e.get('r')))
        e.clear()
    assert allrows==69355 and len(leaves)==2841 and len(raw_positions)==19887
    assert all(len(v['candidates'])==7 for v in leaves.values())
    contract=load(P/'priority-set.json');rows=contract['full_order'];assert len(rows)==2841
    expected=sorted(rows,key=lambda r:(-sum(leaves[(r['county_name'],r['native_name'])]['candidates'].values()),r['key']))
    assert [r['key'] for r in rows]==[r['key'] for r in expected]
    total=sum(candidate_totals.values());assert total==1182676
    cum=0;cross=None;weights=decimal.Decimal(0)
    for pos,r in enumerate(rows,1):
        leaf=leaves[(r['county_name'],r['native_name'])];votes=sum(leaf['candidates'].values());cum+=votes
        assert r['rank']==pos and r['votes']==votes and r['candidates']==leaf['candidates'] and r['source_rows']==leaf['positions']
        assert r['methods']==dict(zip(['Election Day','Early Vote','Absentee','Provisional'],leaf['methods']))
        assert r['cumulative_votes']==cum and r['share_denominator']==total
        assert r['native_id'] is None
        assert r['key']=='AR:2024-xlsx:'+r['county_fips']+':'+urllib.parse.quote(r['native_name'],safe='')
        if cross is None and cum*5>=total*4:cross=pos
    assert cross==1056 and cum==total
    assert contract['ordered_priority_keys']==[r['key'] for r in rows[:cross]]
    assert contract['top15_keys']==[r['key'] for r in rows[:15]]
    assert contract['remainder_keys']==[r['key'] for r in rows[cross:]]
    assert len(set(r['key'] for r in rows))==len(rows)
    assert len(set(r['county_fips'] for r in rows))==75
    assert len(contract['priority_parent_fips'])==68
    assert len(contract['all75parents'])==75
    assert (S/'data/county-turnout.csv').read_bytes()==(P/'orders/2024-xlsx.csv').read_bytes()
    extracted=gzload(P/'extracted/2024-xlsx-president-raw-rows.json.gz');assert [r['source_row'] for r in extracted['rows']]==raw_positions
    tests['independent_original_xlsx']=dict(all_data_rows=allrows,presidential_candidate_rows=len(raw_positions),native_pairs=len(leaves),parents=75,candidate_totals=dict(candidate_totals),method_totals=dict(methods),minimum80=cross)
    # Check each source-native record set against its original state/county controls.
    native=gzload(P/'extracted/source-native-universes.json.gz');api=load(P/'extracted/api-controls.json');fc=load(P/'extracted/full-controls.json');source_results={}
    for year,eid in [(2024,1846),(2022,1844),(2020,1841)]:
        info=json.loads(bodies[f'{year}-info']);meta=json.loads(bodies[f'{year}-metadata']);state=json.loads(bodies[f'{year}-federal-state']);cid=api[str(year)]['contest_id'];descriptor=meta['response']['contests'][cid];statecontest=state['response']['contests'][cid]
        byname={c['name']:k for k,c in descriptor['choices'].items()};assert len(byname)==len(descriptor['choices'])
        county_sums=collections.Counter();count_native=0
        for fips,loc in info['response']['locations'].items():
            assert re.fullmatch('05\d{3}',fips)
            c=json.loads(bodies[f'{year}-federal-{fips}'])['response']['contests'][cid]
            assert set(c['locations'])==set(loc['locations'])
            counts=collections.Counter()
            for nid,r in c['locations'].items():
                assert sum(v['totalVotes'] for v in r['choices'])==r['totalVotes'];count_native+=1
                assert len({v['choiceID'] for v in r['choices']})==len(r['choices'])
                counts.update({v['choiceID']:v['totalVotes'] for v in r['choices']})
            assert dict(counts)=={v['choiceID']:v['totalVotes'] for v in c['choices']}
            assert c['totalVotes']==statecontest['locations'][fips]['totalVotes']
            county_sums.update(counts)
            turn=json.loads(bodies[f'{year}-turnout-{fips}'])['response'];assert turn['locations']=={}
            ts=json.loads(bodies[f'{year}-turnout-state'])['response']['locations'][fips]
            assert turn['totalBallotsCast']==ts['totalBallotsCast'] and turn['registeredVoters']==ts['registeredVoters']
        assert dict(county_sums)=={v['choiceID']:v['totalVotes'] for v in statecontest['choices']}
        assert count_native==len(native[f'{year}-api'])
        full=json.loads(bodies[f'{year}-full']);fcontest=full['ContestData'][fc[str(year)]['contest_position']]
        fsum=collections.Counter();literal_pairs=[]
        for w in fcontest['Counties']:
            wrapper=collections.Counter()
            for r in w['Precincts']:
                assert len({c['Name'] for c in r['Candidates']})==len(r['Candidates'])
                vector={c['Name']:c['TotalVotes'] for c in r['Candidates']};assert sum(vector.values())==r['TotalVotes'];wrapper.update(vector);literal_pairs.append((w['CountyName'],r['PrecinctName']))
            assert dict(wrapper)=={c['Name']:c['TotalVotes'] for c in w['Candidates']};fsum.update(wrapper)
        assert len(literal_pairs)==len(set(literal_pairs))==len(native[f'{year}-full'])
        assert dict(fsum)=={c['Name']:c['TotalVotes'] for c in fcontest['Candidates']}
        assert sum(fsum.values())==fcontest['TotalVotes']
        for name,v in fsum.items():assert v-api[str(year)]['candidates'][name]==fc[str(year)]['api_difference'][name]
        turn=full['Turnout'];assert len(turn['CountyTurnout'])==75
        assert sum(r['VotesCast'] for r in turn['CountyTurnout'])==turn['VotesCast']
        assert sum(r['RegisteredVoters'] for r in turn['CountyTurnout'])==turn['RegisteredVoters']
        source_results[str(year)]=dict(api_native=count_native,full_native=len(literal_pairs),api_candidates=dict(county_sums),full_candidates=dict(fsum),native_turnout_empty_counties=75)
    tests['all_year_original_api_full_turnout_balances']=source_results
    comparisons=load(P/'extracted/publication-native-comparison.json');changed_counts={}
    for year in ['2024','2022','2020']:
        aa={(r['county_fips'],r['native_name']):r for r in native[year+'-api']};ff={(r['county_fips'],r['native_name']):r for r in native[year+'-full']}
        assert set(aa)==set(ff)
        changed=[pair for pair in aa if aa[pair]['candidates']!=ff[pair]['candidates']]
        assert set(changed)=={(r['county_fips'],r['native_name']) for r in comparisons[year]['changed']}
        for pair in changed:
            assert all(ff[pair]['candidates'][name]==2*v for name,v in aa[pair]['candidates'].items())
        changed_counts[year]=len(changed)
    for county,names,api_name in [('CONWAY',['MENIFEE CITY','MENIFEE RURAL'],'MENIFEE CITY'),('WHITE',['Beebe Ward 3','Beebe Ward 3C'],'Beebe Ward 3')]:
        combined=collections.Counter()
        for name in names:combined.update(leaves[(county,name)]['candidates'])
        actual=[r for r in native['2024-api'] if r['county_name']==county and r['native_name']==api_name];assert len(actual)==1 and combined==actual[0]['candidates']
    tests['retained_native_publication_disagreements_and_two_xlsx_combinations']=changed_counts
    pdf=load(P/'extracted/2024-pdf-controls.json');assert pdf['checked_county_candidate_cells']==525
    def text_pdf(body):
        with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
            f.write(body);f.flush();return subprocess.run(['pdftotext','-layout',f.name,'-'],capture_output=True,check=True).stdout.decode()
    pdf_original=text_pdf(bodies['sos-2024-general-state-original'])
    norm=lambda s:re.sub('[^A-Z]','',s.upper())
    primary_counties=collections.defaultdict(collections.Counter)
    for r in rows:primary_counties[norm(r['county_name'])].update(r['candidates'])
    for r in pdf['rows']:
        assert r['raw_line'] in pdf_original
        vec=candidate_totals if r['county']=='Totals' else primary_counties[norm(r['county'])]
        assert r['values'][:-1]==[vec[name] for name,party in pdf['candidates']]
        assert r['values'][-1]==sum(vec.values())
    clerk=load(P/'extracted/clerk-controls.json')
    for year,c in clerk.items():
        original=text_pdf(bodies['clerk-'+year])
        for name,control in c['candidate_controls'].items():
            assert control['clerk_line'] in original
            assert control['clerk_identity_token'] in control['clerk_line']
            assert int(re.search(r'(\d[\d,]*)\s*$',control['clerk_line'])[1].replace(',',''))==api[year]['candidates'][name]==control['votes']
    tests['independent_original_pdf_and_named_clerk_controls']=dict(pdf_candidate_cells=525,clerk_candidates=12)
    parents={p['county_fips']:p for p in contract['all75parents']}
    for p in parents.values():
        primary=[r for r in rows if r['county_fips']==p['county_fips']];assert p['votes']==sum(r['votes'] for r in primary)
        for lane,rr in p['source_native_constituents'].items():assert [r['key'] for r in rr]==[r['key'] for r in native[lane] if r['county_fips']==p['county_fips']]
    tests['all75_parent_and_source_constituent_coverage']=True
    # Every saved full order: uniqueness, weights, descending order and minimum proof.
    statistics=load(P/'orders/statistics.json');order_results={}
    for lane,st in statistics.items():
        with (P/'orders'/(lane+'.csv')).open(newline='') as f:rr=list(csv.DictReader(f))
        assert len(rr)==st['units'] and len({r['key'] for r in rr})==len(rr)
        assert [(int(r['votes']),r['key']) for r in rr]==sorted([(int(r['votes']),r['key']) for r in rr],key=lambda a:(-a[0],a[1]))
        assert sum(int(r['votes']) for r in rr)==st['denominator']
        assert sum(int(r['votes']) for r in rr[:15])==st['top15_votes']
        cumulative=0;first=None
        for i,r in enumerate(rr,1):
            cumulative+=int(r['votes']);assert int(r['cumulative_votes'])==cumulative and int(r['share_denominator'])==st['denominator']
            if cumulative*5>=st['denominator']*4 and first is None:first=i
        assert first==st['minimum80_count'];assert rr[first-1]['key']==st['crossing_key']
        assert sum(int(r['votes']) for r in rr[:first-1])==st['preceding_votes']
        assert sum(int(r['votes']) for r in rr[:first])==st['minimum80_votes']
        assert st['preceding_votes']*5<st['denominator']*4<=st['minimum80_votes']*5
        assert st['remainder_votes']+st['minimum80_votes']==st['denominator']
        order_results[lane]=dict(units=len(rr),minimum80=first,total=st['denominator'],exact_weights_sum_numerator=cumulative,exact_weights_sum_denominator=st['denominator'])
    tests['complete_orders_and_integer_crossings']=order_results
    # Verify all immutable snapshot members, not merely the archive hash.
    snapshot=load(P/'history/original-first-core/snapshot.json');b=(P/'history/original-first-core/core.tar.gz').read_bytes();assert sha(b)==snapshot['archive_sha256']
    with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz') as tar:
        assert set(tar.getnames())=={r['path'] for r in snapshot['members']}
        for r in snapshot['members']:
            mb=tar.extractfile(r['path']).read();assert len(mb)==r['bytes'] and sha(mb)==r['sha256']
    tests['original_first_frozen_snapshot_members']=len(snapshot['members'])
    files=owned();assert all(not f.is_symlink() for f in files)
    assert all(f.stat().st_size<40000000 for f in files)
    assert not any(any(t in f.parts for t in ['node_modules','__pycache__','.cache']) or f.suffix=='.pyc' for f in files)
    links=[];pending=[]
    for file in files:
        if file.suffix!='.md':continue
        for href in re.findall(r'\]\(([^)]+)\)',file.read_text()):
            href=href.strip('<>')
            if href.startswith(('https:','http:','#','mailto:')):continue
            target=file.parent/urllib.parse.unquote(href.split('#')[0]);links.append(str(target))
            if not target.exists() and not args.sealed and target in [P/'asset-manifest.json',P/'final-seal.json',P/'validation.json']:
                pending.append(str(target.relative_to(S)));continue
            assert target.exists(),(file,href)
    tests['relative_links_checked']=len(links);tests['pending_finalization_links']=sorted(set(pending))
    tests['owned_files_before_validation_write']=len(files);tests['strict_object_limit_bytes']=40000000
    tests['maximum_owned_object_bytes']=max(f.stat().st_size for f in files)
    tests['no_dependency_cache_symlinks']=True
    if args.sealed:
        mf=load(P/'asset-manifest.json');actual={str(f.relative_to(S)):f for f in files if f!=P/'asset-manifest.json'}
        assert set(actual)=={r['path'] for r in mf['assets']}
        for r in mf['assets']:
            f=actual[r['path']];assert f.stat().st_size==r['bytes'] and sha(f.read_bytes())==r['sha256'],r['path']
        tests['sealed_exact_membership_and_hashes']=len(actual)
        assert not pending
    if args.write:(P/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

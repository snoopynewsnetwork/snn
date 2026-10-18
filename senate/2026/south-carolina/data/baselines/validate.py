"""Offline validation, independent bounded-slope solve and complete locator audit."""
from extract import *
from calculate import solve,clip
from live import live
from legacy_extract import xml,candidate,office
import re,math,argparse
def csvread(p):return csv.DictReader(gzip.open(p,'rt') if p.suffix=='.gz' else open(p))
def sweep(W,S,g):
    """Independent piecewise-linear event sweep, not worker bisection."""
    T=sum(W);events=collections.defaultdict(float)
    for w,s in zip(W,S):
        if w:
            events[-s]+=2*w;events[1-s]-=2*w
    keys=sorted(events);x=keys[0];net=-T;slope=0.;target=g*T
    for nxt in keys:
        nxtnet=net+slope*(nxt-x)
        if slope>0 and net-1e-7<=target<=nxtnet+1e-7:return x+(target-net)/slope
        net=nxtnet;x=nxt;slope+=events[nxt]
    assert abs(target-T)<1e-6;return keys[-1]
def resolve(root,pointer):
    assert pointer.startswith('/ElectionResult');n=root
    for tag,idx in re.findall(r'/([^/\[]+)\[(\d+)\]',pointer):
        n=list(n)[int(idx)];assert n.tag==tag,(pointer,tag,n.tag)
    return n
def audit_targets(path):
    groups={};count=0;maxerr=0;selected=collections.Counter()
    for r in csvread(path):
        k=(r['scenario'],r['target']);d=groups.setdefault(k,dict(W=[],S=[],nets=0.,target=float(r['target_pair_margin_pp'])/100,delta=float(r['bounded_shift_pp'])/100))
        w=float(r['pair_pool']);s=float(r['baseline_A_pair_share']) if r['baseline_A_pair_share'] else None;q=float(r['bounded_target_share'])if r['bounded_target_share']else None
        assert w>=0 and (q is None and w==0 or q is not None and 0<=q<=1)
        if w:
            assert abs(q-clip(s+d['delta']))<1e-12
            assert abs(float(r['target_net'])-w*(2*q-1))<1e-7
            assert abs(float(r['net_gain'])-2*w*(q-s))<1e-7
            assert abs(float(r['share_pp1_unbounded_net_gain'])-.02*w)<1e-8
            own=w*(2*s-1);fixed=float(r['other_units_fixed_net']);required=float(r['selected_required_share']);total=w/float(r['weight'])
            assert abs((2*required-1)*w+fixed-d['target']*total)<1e-6
        d['W'].append(w);d['S'].append(s if s is not None else 0);d['nets']+=float(r['target_net']);selected[r['selected_status']]+=1;count+=1
    for d in groups.values():
        T=sum(d['W']);err=abs(d['nets']-d['target']*T);maxerr=max(maxerr,err);assert err<1e-6
        independent=sweep(d['W'],d['S'],d['target']);assert abs(independent-d['delta'])<1e-9
    return dict(rows=count,groups=len(groups),max_target_net_error=maxerr,selected_statuses=dict(selected),independent_solver='event slope sweep agrees with bounded shares')
def main(refresh=False):
    result={'status':'pass_with_documented_source_disagreements','checks':{},'limitations':['Unmatched native spellings/physical/current geography not approved','DB2020 incomplete method allocation preserved; actual original method cells separately complete','Registration/ballot/method source scopes and release differences retained','Final certification PDF and November result IDs/configuration, live cadence/remaining pools/probability calibration not verified']}
    source=0
    for p in SRC.glob('*.meta.json'):
        m=json.loads(p.read_text())
        if 'body_path'in m:loadbody(p);source+=1
    result['checks']['all_owned_capture_entities_hashed']=source
    for ref in json.loads((BASE/'shared-primary-references.json').read_text()):
        assert sha((BASE/ref['meta_path']).read_bytes())==ref['meta_sha256'];p=BASE/ref['body_path'];assert sha(p.read_bytes())==ref['stored_sha256']
    for r in json.loads((BASE/'shared-reference-evidence.json').read_text()):
        if 'body_path'in r:
            b=(BASE/r['body_path']).read_bytes();assert sha(b)==r['metadata']['stored_sha256'];assert sha(gzip.decompress(b))==r['metadata']['raw_sha256']
    positions=0
    it=iter(csvread(BASE/'candidate-method-controls.csv.gz'))
    for lab in LABELS:
        for mode in ['combined','methods']:
            tree=json.loads(loadbody(SRC/(lab+'-'+mode+'.meta.json'))[0])['data']['contestGranularData']['divisions']
            for n,path,ptr,c in walk(tree):
                for ordinal,raw in enumerate(n['granularRow']):
                    row=next(it);assert row['source_pointer']==ptr+f'/granularRow/{ordinal}' and row['contest_label']==lab and row['observation_scope']==mode and json.loads(row['raw_row_json'])==raw
                    positions+=1
    assert next(it,None)is None and positions==516586
    result['checks']['every_history_source_position_and_flag']=positions
    pr=json.loads((BASE/'priority-set.json').read_text());assert pr['total']==2548140 and pr['minimum80_count']==17 and pr['preceding_votes']==2019337 and pr['minimum80_votes']==2061601
    for lab,x in pr['comparisons'].items():
        for lev,r in x.items():
            assert sum(x['votes']for x in r['order'])==r['total'];n=r['minimum80_count'];assert r['order'][n-1]['cumulative']*5>=4*r['total'] and (n==1 or r['order'][n-2]['cumulative']*5<4*r['total'])
            assert r['order']==sorted(r['order'],key=lambda x:(-x['votes'],x['key']))
    result['checks']['full_county_and_native_integer80_order']='all four contours pass; top15 and all nonpriority rows retained'
    un=list(csvread(BASE/'native-units.csv.gz'));assert len(un)==9823 and len({(r['contest_label'],r['native_division_path'])for r in un})==9823
    for lab in LABELS:
        state=next(r for r in un if r['contest_label']==lab and r['native_type']=='State');cs=[r for r in un if r['contest_label']==lab and r['native_type']=='County'];ls=[r for r in un if r['contest_label']==lab and r['native_type']=='Precinct']
        for f in ['A','B','other','candidate_votes','pair_votes']:
            assert sum(int(r[f])for r in cs)==int(state[f])==sum(int(r[f])for r in ls)
        for r in cs+ls:
            assert int(r['A'])+int(r['B'])+int(r['other'])==int(r['candidate_votes'])
            assert abs(float(r['pair_participation'])-int(r['pair_votes'])/int(r['candidate_votes']))<1e-12 if int(r['candidate_votes'])else r['pair_participation']==''
    result['checks']['all_geography_candidate_balances']='all46 counties/all9635 leaves/all four candidate vectors exact'
    # Resolve every original required XML/TXT position, then every method-cell locator.
    cacheid=None;root=None;raw=None;checked=0;cellchecked=0
    def get(sid):
        nonlocal cacheid,root,raw
        if sid!=cacheid:
            b,_=loadbody(SRC/(sid+'.meta.json'))
            import zipfile
            z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip()is None
            if 'detail.xml'in z.namelist():raw=z.read('detail.xml');root=ET.fromstring(raw)
            else:raw=z.read('detail.txt');root=None
            cacheid=sid
        return root,raw
    import xml.etree.ElementTree as ET
    for r in csvread(BASE/'legacy-source-positions.csv.gz'):
        rt,rb=get(r['source_id']);attrs=json.loads(r['raw_attributes'])
        if rt is not None:
            e=resolve(rt,r['source_pointer']);assert e.tag==r['tag'] and e.attrib==attrs and (e.text.strip()if e.text and e.text.strip()else '')==r['text']
        else:
            off=attrs['byte_offset'];line=attrs['raw_line'].encode();assert rb[off:off+len(line)]==line
        checked+=1
    for r in csvread(BASE/'legacy-candidate-methods.csv.gz'):
        rt,rb=get(r['source_id']);attrs=json.loads(r['raw_attributes'])
        if rt is not None:
            e=resolve(rt,r['source_pointer']);assert e.attrib==attrs and int(e.get('votes'))==int(r['votes']) and e.get('name')==r['native_name']
        else:
            off=int(r['source_pointer'].rsplit('/',1)[1]);v=attrs['raw_field'].encode();assert rb[off:off+len(v)]==v and int(v.strip())==int(r['votes'])
        cellchecked+=1
    assert checked==280747 and cellchecked==260898
    result['checks']['every_original_source_locator']=dict(XML_TXT_positions=checked,candidate_method_cells=cellchecked,convention='zero-based ALL-child XML ordinals; exact TXTbyte offsets')
    lo=list(csvread(BASE/'legacy-native-baselines.csv.gz'));assert len(lo)==9635 and len({r['geography_key']for r in lo})==9635
    last=None;j=None
    for r in lo:
        if last!=r['source_id']:
            raw,m=loadbody(SRC/(r['source_id']+'.meta.json'));j=json.loads(raw);last=r['source_id']
        path=r['source_pointer'].strip('/').split('/');n=j
        for step in path:n=n[int(step)]if isinstance(n,list)else n[step]
        assert n==r['name']
        ci=int(path[1]);pi=int(path[-1]);assert j['Contests'][ci]['V'][pi]==json.loads(r['raw_choice_vector'])
    result['checks']['all_original_combined_JSON_locators']=len(lo)
    state_candidates=0;state_methods=0;method_totals=collections.Counter()
    for r in csvread(BASE/'legacy-candidate-methods.csv.gz'):
        method='Provisional'if r['method_name']=='Provionsal'else r['method_name']
        method_totals[(r['contest_label'],int(r['analysis_candidate_id']),method)]+=int(r['votes'])
    original_state_controls=[]
    for year,spec in [(2024,[('2024-pres','President and Vice President')]),(2020,[('2020-senate','U.S. Senate')]),(2022,[('2022-senate','U.S. Senate'),('2022-governor','Governor and Lieutenant Governor')])]:
        root,_=xml(f'legacy{year}-detailxml');ct=root.find('ElectionVoterTurnout');cc=list(ct.find('Counties'));assert len(cc)==46 and len({c.get('name')for c in cc})==46
        original_state_controls.append(dict(year=year,totalVoters=ct.get('totalVoters'),ballotsCast=ct.get('ballotsCast'),county_registration_sum=sum(int(c.get('totalVoters'))for c in cc),county_ballots_sum=sum(int(c.get('ballotsCast'))for c in cc),state_minus_county_registration=int(ct.get('totalVoters'))-sum(int(c.get('totalVoters'))for c in cc),state_minus_county_ballots=int(ct.get('ballotsCast'))-sum(int(c.get('ballotsCast'))for c in cc)))
        for lab,title in spec:
            c=next(c for c in root.findall('Contest')if office(c.get('text'))==title)
            for ch in c.findall('Choice'):
                cid=candidate(lab,ch.get('text'));v=int(ch.get('totalVotes'));state_candidates+=1
                total=sum(dict(zip(json.loads(r['choice_analysis_ids']),json.loads(r['raw_choice_vector'])))[cid]for r in lo if r['contest_label']==lab);assert total==v
                for m in ch.findall('VoteType'):
                    state_methods+=1;mv=int(m.get('votes'));assert sum(int(x.get('votes'))for x in m)==mv==method_totals[(lab,cid,m.get('name'))]
    result['checks']['original_statewide_candidate_and_method_balances']=dict(complete_candidates=state_candidates,method_cells=state_methods,election_controls=original_state_controls)
    ledger=json.loads((BASE/'legacy-database-comparison.json').read_text());assert len(ledger['method_differences'])==180 and len({(r['county'],r['name'])for r in ledger['method_differences']})==19
    assert len(ledger['county_candidate_vector_multisets'])==184 and all(r['multiset_equal']for r in ledger['county_candidate_vector_multisets'])
    result['checks']['all184_original_database_candidate_vector_multisets']='equal; not geographic joins'
    result['checks']['retained_method_disagreements']=dict(cells=180,contexts=19)
    rr=json.loads((BASE/'legacy-registration-reconciliation.json').read_text());assert rr['contexts']==182 and rr['registration_disagreements']==151 and rr['ballots_disagreements']==0
    result['checks']['original_registration_and_ballot_scopes']=dict(contexts=182,registration_disagreements_preserved=151,ballot_rollup_disagreements=0)
    targets={}
    for f in ['county-targets.csv.gz','native-targets.csv.gz','legacy-native-targets.csv.gz','legacy-method-targets.csv.gz']:targets[f]=audit_targets(BASE/f)
    result['checks']['target_tables']=targets
    bounded=json.loads((BASE/'bounded-synthetic.json').read_text())
    for r in bounded:assert solve(r['weights'],r['shares'],r['target'])==r['result']
    byname={r['name']:r for r in bounded};assert byname['clipping_requires_resolve']['result']['status']=='bounded_clipping_solved';assert byname['already_winning']['result']['already_at_or_above_target'];assert byname['zero_pool']['result']['status']=='no_positive_pool';assert byname['negative_pool']['result']['status']=='negative_pool_invalid';assert byname['unknown']['result']['status']=='unknown_preference';assert byname['impossible_target']['result']['status']=='impossible_target_margin'
    result['checks']['bounded_synthetic_cases']=len(bounded)
    for r in csvread(BASE/'all-candidate-cushions.csv'):
        assert abs(float(r['achieved_net'])-.01*float(r['all_candidate_pool']))<1e-6
    fixtures=json.loads((BASE/'live-scenarios.json').read_text());saved=json.loads((BASE/'live-results.json').read_text());assert len(fixtures)==len(saved)==13
    for x,savedrow in zip(fixtures,saved):
        y=live(x,x['remaining'][0]['id']);assert y==savedrow['result']
        if 'projected_net'in y:
            assert y['counted_fixed']==x['counted'];assert abs(y['all_candidate_vote_sum']-y['final_all_candidate_denominator'])<1e-6
        if y.get('required_status')=='feasible_threshold':
            U=y['remaining_pair'];q=y['required_uniform_remaining_A_share'];assert abs(y['counted_net']+U*(2*q-1)-y['target_net'])<1e-6
        yp=live(x,x['remaining'][0]['id'],1);assert yp==savedrow['Aplus1_result']
        if yp.get('required_status')=='feasible_threshold':assert abs(yp['counted_net']+yp['remaining_pair']*(2*yp['required_uniform_remaining_A_share']-1)-.01*yp['final_pair_denominator'])<1e-6
    tests={r['input']['name']:r['result']for r in saved};assert tests['unknown_pool']['status']=='unknown_remaining_pool';assert tests['negative_remaining']['status'].startswith('negative');assert tests['positive_pool_impossible']['required_status']=='impossible';assert tests['positive_pool_secured']['required_status']=='already_secured';assert tests['clip_high']['remaining_details'][0]['used_share']==1;assert tests['clip_low']['remaining_details'][0]['used_share']==0;assert tests['other_candidate_blocks_pair_win']['strict_plurality_status'].startswith('impossible')
    result['checks']['live_synthetic_scenarios']=13
    peer=json.loads((BASE/'peer-reconciliation.json').read_text());assert peer['status']=='pass';result['checks']['independent_peer_history_and_order']='full-field pass'
    peer=json.loads((BASE/'peer-original-reconciliation.json').read_text());assert peer['status']=='pass';result['checks']['independent_peer_originals']='full-field pass'
    links=[]
    for mp in [DATA.parent/'county-partisanship.md',SRC/'SCHEMA.md']:
        for target in re.findall(r'\]\(([^)]+)\)',mp.read_text()):
            if re.match(r'https?://',target):continue
            q=(mp.parent/target.split('#')[0]).resolve()
            if q.name in ['asset-manifest.json','validation.json']and refresh and not q.exists():links.append(str(q));continue
            assert q.exists(),(mp,target);links.append(str(q))
    result['checks']['relative_links']=len(links)
    assets=[p for p in BASE.rglob('*')if p.is_file()and'__pycache__'not in p.parts]+[DATA/'county-baselines.csv',DATA.parent/'county-partisanship.md']
    for p in assets:assert p.stat().st_size<40000000,(p,p.stat().st_size)
    result['checks']['asset_size_limit']='all owned files strictly below40000000bytes'
    dump(BASE/'validation.json',result)
    if refresh:
        assets=[p for p in BASE.rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.name!='asset-manifest.json']+[DATA/'county-baselines.csv',DATA.parent/'county-partisanship.md']
        manifest=dict(scope='all and only owned report/CSV/baselines files; this manifest excluded to avoid recursive self-hash; shared raw bodies separately pinned by source metadata',assets=[dict(path=os.path.relpath(p,DATA.parent),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))for p in sorted(assets)])
        dump(BASE/'asset-manifest.json',manifest)
    else:
        manifest=json.loads((BASE/'asset-manifest.json').read_text())
        for r in manifest['assets']:
            p=DATA.parent/r['path'];assert p.stat().st_size==r['bytes']and sha(p.read_bytes())==r['sha256'],r['path']
    print(compact(dict(status=result['status'],history_positions=positions,original_positions=checked,original_method_cells=cellchecked,target_rows=sum(x['rows']for x in targets.values()),target_groups=sum(x['groups']for x in targets.values()),live_cases=13)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--refresh-manifest',action='store_true');a=p.parse_args();main(a.refresh_manifest)

"""Offline independent source/control/root and calculator validation. No repairs.
Default writes validation.json. --read-only prints checks without writing anything.
"""
import collections,copy,csv,gzip,io,json,math,re,sys,tarfile,zipfile
from decimal import Decimal,getcontext
from common import *
from calculate import calculate,historical
def require(condition,label):
    if not condition:raise AssertionError(label)
def near(a,b,tol=1e-6):return math.isclose(a,b,abs_tol=tol,rel_tol=1e-10)
def native_check(rows,original):
    seen=set()
    for r in rows:
        key=(r['election'],r['source_code']);require(key not in seen,'duplicate native context');seen.add(key)
        expected=original.get(key,[])
        if not expected:
            require(not r['observed'] and r['source_unit_key'] is None,'absent contest is unavailable')
            require(all(r[k] is None for k in ['A_votes','B_votes','pair_votes','all_reported_votes','A_pair_share','methods']),'absent contest fabricated zero')
            continue
        require(r['observed'],'observed context removed');require(len(r['candidates'])==len(expected),'candidate coverage')
        first=expected[0]
        require(r['source_unit_key']==f"{first['zip_sha256']}#{first['member']}#{first['byte_start']}",'source key anchor')
        require(r['source_name']==first['source_name'].strip(),'native source name')
        for candidate,raw in zip(r['candidates'],expected):
            require(candidate['candidate_code']==raw['candidate_code'] and candidate['name_raw']==raw['candidate_name'] and candidate['party_raw']==raw['party'],'candidate raw identity')
            require(candidate['votes']==raw['votes'] and candidate['methods']==raw['methods'] and candidate['byte_start']==raw['byte_start'] and candidate['line']==raw['line'],'candidate votes/methods/positions')
        require(r['all_reported_votes']==sum(x['votes'] for x in expected),'unit total')
        require(r['methods']==[sum(x['methods'][i] for x in expected) for i in range(14)],'14-slot total')
        require(r['A_votes']==sum(x['votes'] for x in expected if x['party'].strip()=='DEM'),'A balance')
        require(r['B_votes']==sum(x['votes'] for x in expected if x['party'].strip()=='REP'),'B balance')
        require(r['pair_votes']==r['A_votes']+r['B_votes'],'pair balance')
        require(r['pair_votes']+r['other_reported_votes']==r['all_reported_votes'],'full-field balance')
        require((r['A_pair_share'] is None) if r['pair_votes']==0 else near(r['A_pair_share'],r['A_votes']/r['pair_votes']),'undefined zero-pair preference')
    require(set(original)<=seen,'missing observed geography')

def main():
    checks=[]
    def check(label,good,detail=None):
        require(good,label);checks.append({'check':label,'passed':True,'detail':detail})
    original_bodies={}
    for r in inputs().values():
        b=body(r['id']);original_bodies[r['id']]=b
        check('original body/stored hash '+r['id'],len(b)==r['raw_bytes'])
    for r in json.loads((BASE/'source/current-inputs.json').read_text()):
        if 'stored_path' in r:
            s=(BASE/r['stored_path']).read_bytes();b=gzip.decompress(s)
            check('current source full response hash '+r['id'],sha(s)==r['stored_sha256'] and sha(b)==r['raw_sha256'] and len(b)==r['raw_bytes'])
    members=json.loads((BASE/'source/zip-members.json').read_text());zips={};member_bodies={}
    for m in members:
        ident=m['input']
        if ident not in zips:zips[ident]=zipfile.ZipFile(io.BytesIO(original_bodies[ident]));require(zips[ident].testzip() is None,'ZIP CRC')
        z=zips[ident];raw=z.read(z.infolist()[m['member_index']]);meta=z.infolist()[m['member_index']]
        member_bodies[ident,m['member']]=raw
        check('ZIP complete member hash '+ident+' '+m['member'],sha(raw)==m['sha256'] and len(raw)==m['bytes'] and meta.CRC==int(m['crc32'],16))
    roots=read_gz('witness/root-selected.jsonl.gz');allviews=read_gz('witness/selected-all-views.jsonl.gz')
    keyset=set()
    for r in allviews:
        key=(r['zip_sha256'],r['member'],r['byte_start']);require(key not in keyset,'duplicate source row');keyset.add(key)
        b=member_bodies[r['input'],r['member']];chunk=b[r['byte_start']:r['byte_end']]
        require(sha(chunk)==r['raw_line_sha256'] and chunk.rstrip(b'\r\n').decode('latin1')==r['raw_record'],'source raw position witness')
        require(sum(r['methods'])==r['votes'] and len(r['methods'])==14,'source method sum')
    check('all selected root/nested/setup raw positions/terminators/14slots',True,len(allviews))
    election={(2024,'Senator in Congress'):'2024-senate',(2024,'Presidential Electors For:'):'2024-president',
        (2020,'Senator in Congress'):'2020-senate',(2020,'Presidential Electors For:'):'2020-president',(2022,'Governor'):'2022-governor'}
    byunit=collections.defaultdict(list)
    for r in roots:byunit[election[r['year'],r['contest_title'].strip()],r['source_code']].append(r)
    rows=read_gz('extracts/native-baselines.jsonl.gz');native_check(rows,byunit)
    check('native baseline complete candidate/native/raw balances',True,{'rows':len(rows),'source_records':len(roots)})
    inv=json.loads((BASE/'extracts/native-inventory.json').read_text())
    check('inventory all native and Board statistic-only contexts',collections.Counter(r['year'] for r in inv)=={2020:504,2022:458,2024:497})
    check('39 absent Senate contexts per presidential year',all(sum(r['election']==cid and not r['observed'] for r in rows)==39 for cid in ['2024-senate','2020-senate']))
    check('four2022 stat-only Governor contexts unavailable',sum(r['election']=='2022-governor' and not r['observed'] for r in rows)==4)
    check('2024 fifteen observed-zero Senate contexts',sum(r['election']=='2024-senate' and r['observed'] and r['all_reported_votes']==0 for r in rows)==15)
    controls=json.loads((BASE/'extracts/state-denominator-controls.json').read_text());pc=json.loads((BASE/'extracts/publication-controls.json').read_text())
    check('Board12997 candidate total+party+first3 method fields',pc['board_candidate_method_checks']==12997 and not pc['board_disagreements'])
    check('all1053 municipal candidate+method fields',pc['html_candidate_method_checks']==1053 and not pc['html_disagreements'])
    balances=[]
    for c in controls:
        cid=election[c['year'],c['contest']];rr=[r for r in rows if r['election']==cid]
        ballots=sum(r['election_ballots'] or 0 for r in rr if r['observed']);excluded=sum(r['election_ballots'] or 0 for r in rr if not r['observed'])
        check('state candidate+over+under=contest ballots '+cid,c['candidate_generic_total']+c['overvotes']['total']+c['undervotes']['total']==c['contest_ballots'])
        check('native electorate ballots=Board contest denominator '+cid,ballots==c['contest_ballots'])
        check('PDF candidate/method controls '+cid,all(x['equal'] for x in c['candidate_checks']))
        balances.append({'election':cid,'candidate_generic':c['candidate_generic_total'],'contest_ballots':c['contest_ballots'],
            'all_election_ballots':ballots+excluded,'excluded_context_ballots':excluded,
            'excluded_context_codes':[r['source_code'] for r in rr if not r['observed']],
            'residual_unallocated':0,'reason':'Exact published Board native election-ballot rows in contexts absent from selected contest; no inferred zeros or residual allocation'})
    if '--read-only' not in sys.argv:write_json('extracts/electorate-ballot-reconciliation.json',balances)
    rank=json.loads((BASE/'witness/independent-native-priority.json').read_text())
    expected=sorted([r for r in rows if r['election']=='2024-senate' and r['observed']],key=lambda r:(-r['all_reported_votes'],r['source_anchor']['first_byte']))
    check('all458 descending exact source-position tie order',[r['key'] for r in rank]==[r['source_unit_key'] for r in expected])
    check('exact integer80 crossing/rank/top15',len(rank)==458 and sum(r['votes'] for r in rank)==491948 and sum(r['votes'] for r in rank[:15])==34697 and rank[240]['cumulative']==393066 and rank[241]['cumulative']==394072 and 393066*5<491948*4<=394072*5 and sum(r['priority'] for r in rank)==242)
    parents=json.loads((BASE/'extracts/parent-baselines.json').read_text());pp=[r for r in parents if r['election']=='2024-senate']
    check('43 disjoint canonical child maps,39 municipal+4 state-admin',len(pp)==43 and sum(p['parent_kind']=='municipality' for p in pp)==39 and collections.Counter(x for p in pp for x in p['children'])==collections.Counter(r['key'] for r in rank))
    check('full parent controls across years',all(sum(p['all_reported_votes'] or 0 for p in parents if p['election']==cid)==sum(r['all_reported_votes'] for r in rows if r['election']==cid and r['observed']) for cid in election.values()))
    independent_roots=[]
    for setting in json.loads((BASE/'scenario-settings.json').read_text()):
        for target in ['tie','Aplus1']:
            name=setting['id']+'-'+target;data=json.loads((BASE/f'scenarios/{name}.input.json').read_text());r=json.loads((BASE/f'scenarios/{name}.result.json').read_text());u=data['units']
            check('scenario every source key unique '+name,len({x['key'] for x in u})==len(u))
            check('scenario denominators source weights '+name,near(sum(x['all_volume'] for x in u),r['all_candidate_denominator']) and near(sum(x['pair_volume'] for x in u),r['pair_denominator']) and near(sum(x['pair_weight'] for x in r['units']),1))
            if setting['id'].startswith('2024-senate-'):check('retain all458/nonpriority units '+name,{x['key'] for x in u}=={x['key'] for x in rank})
            # Independent closed-form piecewise root, using decimal and sorted clipping breakpoints, not the production bisection.
            getcontext().prec=40;D=lambda v:Decimal(str(v));goal=D(data['target_margin'])*sum(D(x['pair_volume']) for x in u)
            points=sorted(set([Decimal(-1),Decimal(1)]+[-D(x['a_share']) for x in u if x['a_share'] is not None]+[1-D(x['a_share']) for x in u if x['a_share'] is not None]))
            def net(d):return sum(D(x['pair_volume'])*(2*min(Decimal(1),max(Decimal(0),D(x['a_share'])+d))-1) for x in u if x['pair_volume']>0)
            exact=None
            for lo,hi in zip(points,points[1:]):
                nl,nh=net(lo),net(hi)
                if nl<=goal<=nh and nh>nl:exact=lo+(goal-nl)*(hi-lo)/(nh-nl);break
            check('independent bounded piecewise root '+name,exact is not None and near(float(exact),r['uniform_share_shift'],1e-11))
            final=sum(x['pair_volume']*(2*x['target_a_share']-1) for x in r['units'] if x['target_a_share'] is not None)
            check('scenario clipping/final target balance '+name,near(final,float(goal)) and all(x['target_a_share'] is None or 0<=x['target_a_share']<=1 for x in r['units']))
            for x in r['units']:
                req=x['selected_only'];q=req['raw_required_share']
                if q is not None and 0<=q<=1:require(near(req['other_units_net_votes']+x['pair_volume']*(2*q-1),float(goal)),'selected unit root')
                if x['pair_volume']==0:require(x['baseline_a_share'] is None,'zero pair neutral fabricated')
            independent_roots.append({'scenario':name,'decimal_piecewise_shift':str(exact),'implemented_shift':r['uniform_share_shift'],'target_net':str(goal),'summed_net':final})
    if '--read-only' not in sys.argv:write_json('qa/independent-bounded-roots.json',independent_roots)
    cli=json.loads((BASE/'qa/cli-fixtures.json').read_text());check('30 actual strict-JSON CLI fixtures',cli['all_passed'] and len(cli['tests'])==30)
    # Corruption probes use production validation boundaries and must fail; no production data is modified.
    corrupt=[]
    def probe(name,fn):
        try:fn();passed=False
        except (AssertionError,ValueError):passed=True
        corrupt.append({'name':name,'corruption_detected':passed});require(passed,name)
    bad=copy.deepcopy(rows);bad[0]['candidates'][0]['votes']+=1;probe('changed candidate vote',lambda:native_check(bad,byunit))
    bad2=copy.deepcopy(rows);bad2[0]['candidates'][0]['party_raw']='REP';probe('changed raw party',lambda:native_check(bad2,byunit))
    bad3=copy.deepcopy(rows);bad3[0]['candidates'][0]['methods'][13]+=1;probe('changed unlabeled14th slot',lambda:native_check(bad3,byunit))
    bad4=copy.deepcopy(rows);bad4.append(copy.deepcopy(bad4[0]));probe('duplicate native source',lambda:native_check(bad4,byunit))
    bad5=copy.deepcopy(rows);bad5.pop(0);probe('missing native source',lambda:native_check(bad5,byunit))
    bad6=copy.deepcopy(rows);absent=next(x for x in bad6 if not x['observed']);absent['A_votes']=0;probe('fabricated absent Senate zero',lambda:native_check(bad6,byunit))
    probe('tampered source bytes hash',lambda:require(sha(original_bodies['ri-2024-layout-zip']+b'x')==inputs()['ri-2024-layout-zip']['raw_sha256'],'source hash'))
    swapped=copy.deepcopy(rank);swapped[0],swapped[1]=swapped[1],swapped[0];probe('wrong full descending priority order',lambda:require([x['key'] for x in swapped]==[x['source_unit_key'] for x in expected],'rank'))
    check('8 independent corruption probes',all(x['corruption_detected'] for x in corrupt))
    reciprocal=json.loads((BASE/'reciprocal/reconciliation.json').read_text());check('captured peer24249 bounded checks',reciprocal['all_passed'] and reciprocal['checks_count']==24249)
    check('raw label whitespace differences retained',len(reciprocal['literal_child_label_representation_differences'])==11)
    wi=json.loads((BASE/'extracts/2024-senate-writein-reconciliation.json').read_text());scope=json.loads((BASE/'extracts/writein-detail-scope-comparison.json').read_text())
    check('writein full literal source and bounded peer scopes both preserved',wi['header_sum']==1239 and wi['detail_sum']==1227 and wi['municipal_generic_sum']==1239 and len(wi['disagreements'])==8 and wi['state_generic']==1244 and scope['row6_onward_sum']==1226 and len(scope['row6_discrepancies'])==9)
    proof=json.loads((BASE/'extracts/writein-row5-source-proof.json').read_text());wb=original_bodies['board2024-writeins-xlsx'];wz=zipfile.ZipFile(io.BytesIO(wb));member=wz.read(proof['member'])
    check('Cranston actual row5 original XML/member proof',sha(wb)==proof['source_raw_sha256'] and sha(member)==proof['member_sha256'] and all(member[c['xml_byte_start']:c['xml_byte_end']].decode()==c['original_cell_xml'] for r in proof['rows'] for c in r['cells'] if c['original_cell_xml'] is not None))
    report=STATE/'county-partisanship.md'
    pending=[]
    for p in [report,BASE/'source/SCHEMA.md',BASE/'REPRODUCTION.md']:
        if p.exists():
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                if target.startswith(('https://','http://','#','mailto:')):continue
                link=p.parent/target.split('#')[0]
                if '--read-only' not in sys.argv and link.name in ['validation.json','final-seal.json','asset-manifest.json'] and not link.exists():
                    pending.append(str(link.relative_to(STATE)));continue
                check('relative link '+str(p.relative_to(STATE))+' '+target,link.exists())
    owned=[p for p in BASE.rglob('*') if p.is_file()]+[STATE/'data/county-baselines.csv']+([report] if report.exists() else [])
    check('every owned artifact strictly below40000000 bytes',all(p.stat().st_size<40000000 for p in owned),max(p.stat().st_size for p in owned))
    check('no retained dependency/cache trees',not any(p.name in ['node_modules','__pycache__','.cache','.venv'] for p in BASE.rglob('*')))
    for p in BASE.rglob('*.json'):
        if p.name in ['validation.json','asset-manifest.json','final-seal.json']:continue
        json.loads(p.read_text(),parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    result={'schema':'ri-baseline-offline-validation-v1','all_passed':True,'checks':checks,'check_count':len(checks),
        'corruption_tests':corrupt,'source_candidate_rows':len(roots),'baseline_native_contest_rows':len(rows),'native_inventory_contexts':len(inv),
        'historical_scenario_runs':16,'cli_fixture_count':30,'peer_captured_checks':24249,'finalization_links_pending_at_preseal_validation':pending,
        'qualifications':{'signed_certification_not_acquired':True,'current_final_ballot_mapping':None,'valid_named_writein_universe':None,
            'current_native_geometry_approved':False,'coordinator_priority_accepted':False,'implemented_live_collector':False,'live_cadence_known':False,
            'known_outstanding_pool':None,'calibrated_probability':None},'manifest_reverse_digest':None}
    if '--read-only' not in sys.argv:write_json('validation.json',result)
    print(json.dumps({'all_passed':True,'check_count':len(checks),'corruption_tests':len(corrupt),'cli_fixtures':30,'peer_captured_checks':24249},indent=2))
if __name__=='__main__':main()

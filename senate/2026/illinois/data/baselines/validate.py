"""Offline source/identity/weight/denominator/scenario audit. No peer/shared writes."""
import collections,csv,gzip,io,json,math,re,sys,subprocess
from pathlib import Path
from source_io import ROOT,STATE,pins,raw,sha,dump
from calculator import live,bounded_shift,selected_only,clip

def readcsv(p):
    b=gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes()
    return list(csv.DictReader(io.StringIO(b.decode())))
def main():
    checks=0;errors=[];counts={}
    def check(ok,context):
        nonlocal checks
        checks+=1
        if not ok:errors.append(context)
    def near(a,b,ctx,tol=1e-5):check(abs(float(a)-float(b))<=tol,ctx)
    sources=pins();check(len({x['id']for x in sources})==len(sources),'source ID uniqueness')
    for x in sources:
        if 'path'not in x:check('error'in x,['failed source receipt explicit',x['id']]);continue
        try:
            b=raw(x['id']);check(len(b)==x['bytes'],['source complete bytes',x['id']])
            check(len((ROOT/x['path']).read_bytes())<40000000,['source stored limit',x['id']])
            if 'receipt_original_path'in x:check(sha((ROOT/x['receipt_original_path']).read_bytes())==x['receipt_original_sha256'],['immutable original receipt',x['id']])
        except Exception as e:check(False,['source hash/bytes',x['id'],str(e)])
    counts['source_receipts']=len(sources)
    control=json.loads((ROOT/'extract/reconciled-controls.json').read_text());allstate=readcsv(ROOT/'extract/statewide-source-rows.csv');county=readcsv(ROOT.parent/'county-baselines.csv');cands=readcsv(ROOT/'extract/county-candidate-source-rows.csv');inv=readcsv(ROOT/'authority-inventory.csv')
    check(len(inv)==108 and len({r['JurisdictionID']for r in inv})==108,'108unique authorities')
    check(len(county)==306 and len({(r['year'],r['county_key'])for r in county})==306,'306unique county-year rows')
    for y,expected_rows in [('2020',54950),('2022',31797),('2024',59623)]:
        sid=control[y]['source_id'];orig=list(csv.DictReader(io.StringIO(raw(sid).decode('utf-8-sig'))));der=readcsv(ROOT/f'extract/{y}-raw-rows.csv.gz');check(len(orig)==len(der)==expected_rows,['raw row coverage',y]);counts[y+'_raw_rows']=len(orig)
        for pos,(o,d)in enumerate(zip(orig,der),2):
            check(int(d['csv_record_1based_including_header'])==pos,['raw position',y,pos])
            for k,v in o.items():check(d[k]==v,['raw exact literal field',y,pos,k])
        expected=collections.Counter()
        for r in orig:expected[r['CandidateName']]+=int(r['VoteCount'])
        check(dict(expected)==control[y]['candidate_categories'],['all raw categories state',y])
        cc=[r for r in county if r['year']==y];check(len(cc)==102,['county coverage102',y]);check(len({r['FIPS']for r in cc})==102,['Census FIPS unique102',y])
        actual=collections.Counter()
        for r in cands:
            if r['year']==y:actual[r['candidate_literal']]+=int(r['votes'])
        target={r['candidate_literal']:int(r['votes'])for r in allstate if r['year']==y};check(dict(actual)==target,['all named county statewide candidates exact',y])
        for r in cc:
            A=int(r['A']);B=int(r['B']);T=int(r['pair_votes']);N=int(r['all_named_votes']);O=int(r['other_named']);check(A+B==T and T+O==N,['county denominators',y,r['county_key']]);near(r['A_pair_share'],A/T,['county pair share',y,r['county_key']]);near(r['pair_participation'],T/N,['county participation',y,r['county_key']]);check(int(r['ballots_minus_contest'])==int(r['ballots_cast'])-N,['ballots distinct',y,r['county_key']])
        check(sum(int(r['all_named_votes'])for r in cc)==control[y]['statewide_HTML_total'],['all-candidate denominator',y]);check(sum(int(r['ballots_cast'])for r in cc)==control[y]['state_ballots'],['state ballots',y])
        units=json.loads((ROOT/f'extract/{y}-units.json').read_text());contexts=json.loads(gzip.decompress((ROOT/f'extract/{y}-contexts.json.gz').read_bytes()));check(len({r['unit_key']for r in units})==len(units),['native uniqueness',y]);check(len(contexts)==control[y]['native_presentations'],['full native presentation coverage',y]);positions=sorted(p for r in contexts for p in r['source_positions']);check(positions==list(range(2,len(orig)+2)),['all source positions exactly once full presentations',y])
        for u in units:
            prs=[orig[p-2]for p in u['source_positions']];cat=collections.Counter()
            for r in prs:cat[r['CandidateName']]+=int(r['VoteCount'])
            check(dict(cat)==u['literal_category_record_sums'],['native category presence and sums',y,u['unit_key']]);check(u['registration_literals']==list(dict.fromkeys(r['Registration']for r in prs)),['native registration literal availability',y,u['unit_key']])
            for k,label in [('under_votes_observed','Under Votes'),('over_votes_observed','Over Votes'),('blank_ballots_observed','Blank Ballots')]:check(u[k]==cat.get(label),['absent category remains null',y,u['unit_key'],k])
            generic_present=any(k.lower()=='write-in'for k in cat);check(u['generic_writein_source_present']==generic_present,['generic source presence',y,u['unit_key']]);check(u['generic_writein_marks']is not None if generic_present else u['generic_writein_marks']is None,['generic observed null',y,u['unit_key']]);check(u['method']=='unavailable_no_source_column',['no inferred method',y,u['unit_key']])
        counts[y+'_native_groups']=len(units);counts[y+'_native_presentations']=len(contexts)
    # Exact entire rankings and integer crossing; unavailable native observations retain null rank.
    contracts=json.loads((ROOT/'priority/contracts.json').read_text())['contracts']
    for key,co in contracts.items():
        p=ROOT/'priority'/(key+'.csv');p=p if p.exists()else p.with_suffix('.csv.gz')
        rr=readcsv(p);keyfield='unit_key'if key.startswith('native-')else'JurisdictionID'if key.startswith('authority-')else'county_key';check(len(rr)==len(co['full_order']),['priority entire coverage',key]);check([r[keyfield]for r in rr]==co['full_order'],['entire source order',key]);cum=0
        for i,r in enumerate(rr,1):
            value=int(r['ranking_value']);cum+=value;check(cum==int(r['cumulative_votes']),['priority cumulative',key,i]);check(int(r['state_denominator'])==co['denominator'],['priority denominator',key,i]);check(int(r['order_position'])==i,['priority full order position',key,i]);near(r['share'],value/co['denominator'],['priority source weight',key,i])
        check(cum==co['denominator'],['priority state balance',key]);k=co['minimum_count'];check(5*co['before_votes']<4*co['denominator']<=5*co['crossing_votes'],['exact minimal integer80',key]);check(int(rr[k-1]['cumulative_votes'])==co['crossing_votes'],['crossing row',key])
    # Scenario checks use source weights and re-evaluate sums independently of solver output.
    states={r['scenario']:r for r in readcsv(ROOT/'state-scenarios.csv')};settings=json.loads((ROOT/'scenario-settings.json').read_text());cb={(r['year'],r['county_key']):r for r in county};native={r['unit_key']:r for r in json.loads((ROOT/'extract/2024-units.json').read_text())}
    for file,level,n in [('county-target-scenarios.csv.gz','county',102),('native-target-scenarios.csv.gz','native',10062)]:
        groups=collections.defaultdict(list)
        for r in readcsv(ROOT/file):groups[r['scenario']].append(r)
        counts[file]=sum(len(r)for r in groups.values())
        for sid,rr in groups.items():
            st=states[sid];T=float(st['pair_denominator']);N=float(st['all_candidate_denominator']);g=float(st['target_margin']);M=float(st['baseline_net']);check(len(rr)==n,['all scenario units retained',sid]);check(len({r['county_key']if level=='county'else r['unit_key']for r in rr})==n,['scenario uniqueness',sid]);near(sum(float(r['expected_pair_votes'])for r in rr),T,['scenario pair sum',sid]);near(sum(float(r['target_pair_net'])for r in rr),g*T,['scenario bounded target achieved',sid]);near(sum(float(r['baseline_pair_net'])for r in rr),M,['scenario baseline source net',sid]);near(sum(float(r['pair_weight'])for r in rr),1,['scenario weights sum1',sid],1e-10);near(float(st['unbounded_shift']),(g-M/T)/2,['unbounded formula factor2',sid],1e-12)
            if level=='county':near(sum(float(r['expected_all_candidate_votes'])for r in rr),N,['all-candidate model volume',sid])
            for r in rr:
                t=float(r['expected_pair_votes']);near(r['plus1_share_pp_net_gain'],.02*t,['share point net gain',sid,r.get('county_key',r.get('unit_key'))]);s=float(r['baseline_A_pair_share'])if r['baseline_A_pair_share']else None;q=float(r['target_A_pair_share'])if r['target_A_pair_share']else None;net=float(r['baseline_pair_net'])
                if s is not None:
                    check(0<=q<=1,['bounded share',sid]);near(float(r['target_pair_net']),t*(2*q-1),['target net vs bounded share',sid]);near(q,clip(s+float(st['shift'])),['share clipping',sid],1e-12)
                else:
                    source=native[r['unit_key']];check(level=='native'and t==0 and ((source['A']is None and source['B']is None)or(source['A']==0 and source['B']==0)),['undefined pair preference: absent administrative pool or explicitly observed A=B=0, never imputed share',sid])
                requirement=r['selected_only_required_A_share']
                if requirement:
                    req=float(requirement);near((M-net)+t*(2*req-1),g*T,['selected only all others fixed',sid]);status=r['selected_only_status'];check((req<0 and status=='already_secured')or(req>1 and status=='impossible')or(0<=req<=1 and status=='feasible'),['selected feasible boundary status',sid])
                if level=='county':
                    mix=st['mix_year'];pref=st['preference_year'];source=cb[mix,r['county_key']];anchor=cb[pref,r['county_key']];mixN=sum(int(c['all_named_votes'])for (y,k),c in cb.items()if y==mix);expectedN=N*int(source['all_named_votes'])/mixN;near(t,expectedN*int(source['pair_votes'])/int(source['all_named_votes']),['actual historical county volume participation',sid,r['county_key']]);near(s,int(anchor['A'])/int(anchor['pair_votes']),['actual historical preference anchor',sid,r['county_key']],1e-12)
                elif t>0:
                    source=native[r['unit_key']];baseT=sum(int(c['pair_votes'])for(y,k),c in cb.items()if y=='2024');near(t,(source['A']+source['B'])*T/baseT,['actual native source weight',sid,r['unit_key']]);near(s,source['A']/(source['A']+source['B']),['actual native preference',sid,r['unit_key']],1e-12)
    ar=readcsv(ROOT/'authority-target-scenarios.csv');ast={r['scenario']:r for r in json.loads((ROOT/'authority-state-scenarios.json').read_text())};ag=collections.defaultdict(list)
    for r in ar:ag[r['scenario']].append(r)
    for sid,rr in ag.items():
        st=ast[sid];check(len(rr)==len({r['JurisdictionID']for r in rr})==108,['108authority model retains cities',sid]);near(sum(float(r['expected_pair_votes'])for r in rr),st['total'],['authority total',sid]);near(sum(float(r['target_pair_net'])for r in rr),st['target_net'],['authority target',sid]);near(sum(float(r['pair_weight'])for r in rr),1,['authority weights',sid],1e-10)
    cases=json.loads((ROOT/'live-synthetic-inputs.json').read_text());saved={r['id']:r['result']for r in json.loads((ROOT/'live-synthetic-results.json').read_text())};results={}
    for case in cases:
        result=live(case);results[case['id']]=result;check(result==saved[case['id']],['saved live reproduction',case['id']]);check('probability'not in result,['no uncalibrated probability',case['id']]);
        if 'final'in result:
            check(result['counted_fixed']==case['counted'],['counted A/B/other fixed',case['id']]);near(result['final_all_candidate_denominator'],sum(case['counted'].values())+sum(p['votes']for p in case['remaining']),['correct FINAL allcandidate denominator',case['id']]);near(result['final_pair_denominator'],case['counted']['A']+case['counted']['B']+result['remaining_pair_votes'],['correct FINAL pair denominator',case['id']]);check(all(result['final'].get(k,0)>=v for k,v in case['counted'].items()),['counted votes never reswung',case['id']])
    for key,status in {'unknown-remainder':'unknown_remaining_pool','negative-remainder':'invalid_negative_pool','no-pool-secured-pair':'no_positive_pair_pool','unknown-preference':'unknown_remaining_preference','unknown-pair-participation':'unknown_pair_participation','unknown-other-allocation':'unknown_or_invalid_other_allocation','invalid-negative-counts':'invalid_counted_votes'}.items():check(results[key]['status']==status,['expected live edge status',key])
    near(results['mixed-final-denominator']['final_all_candidate_denominator'],210,'mixed final denominator210');near(results['mixed-final-denominator']['final_pair_denominator'],180,'mixed final pair180');near(results['mixed-final-denominator']['final_pair_net'],12,'mixed final net12');check(results['pair-win-other-candidate-wins']['legal_plurality_outcome']=='A_not_plurality','pair scenario never substitutes for full-field plurality');check(results['positive-pool-impossible']['pair_tie_threshold']['status']=='impossible','impossible positive pool');check(results['positive-pool-secured']['pair_tie_threshold']['status']=='already_secured','already secured positive pool');check(len(results['clipping-high-share']['clip_events'])==1 and len(results['clipping-low-share']['clip_events'])==1,'both clipping directions explicit')
    for case in json.loads((ROOT/'bounded-synthetic-results.json').read_text()):check(case['result']==bounded_shift(case['units'],case['target_margin']),['bounded synthetic reproduction',case['id']])
    # Native presentation-to-scenario index covers every presentation without adding categories as votes.
    pi=readcsv(ROOT/'native-presentation-scenario-index.csv.gz');check(len(pi)==11535 and len({r['presentation_id']for r in pi})==11535,'all11535native presentation associations');check(all(r['arithmetic_unit_key']in native for r in pi),'all presentation unit references resolve')
    peer=json.loads((ROOT/'peer-reconciliation.json').read_text());check(peer['status']=='pass'and not peer['errors'],'reciprocal original stabilized peer pass')
    np=json.loads((ROOT/'peer-native-priority-reconciliation.json').read_text());check(np['status']=='pass'and not np['errors'],'full finer native and authority order reciprocal pass')
    fp=json.loads((ROOT/'peer-final-availability-reconciliation.json').read_text());check(fp['status']=='pass'and not fp['errors'],'final stable peer null/presence/recorded aggregation comparison')
    for folder in ['peer-priority-capture','peer-final-availability','calculator-review-evidence']:
        for x in json.loads((ROOT/folder/'manifest.json').read_text()):
            p=ROOT/x.get('captured',x.get('capture'));b=p.read_bytes();check(sha(b)==x['sha256']and len(b)==x['bytes'],['immutable final peer/review evidence hash',str(p.relative_to(ROOT))])
    observed_zero=sum(r['A']==0 and r['B']==0 for r in native.values());check(observed_zero==745,'745observed native A=B=0contexts distinguished from4unavailable admin')
    primary=contracts['native-2024-printed-observed'];check(primary['minimum_count']==5540 and primary['denominator']==5592368 and primary['before_votes']==4473789 and primary['crossing_votes']==4474312,'primary5540source-only exact80 contract');check(json.loads(primary['keys'][-1])==['2024','88','O FALLON 3'],'exact primary crossing source identity')
    neg=json.loads((ROOT/'negative-fixture-results.json').read_text());check(neg['status']=='pass'and neg['cases']==38,'38negative CLI fixture coverage')
    for case in neg['results']:
        p=ROOT/case['input_path'];check(sha(p.read_bytes())==case['input_sha256'],['negative input byte seal',case['case']]);r=subprocess.run([sys.executable,str(ROOT/'calculator.py'),str(p)],capture_output=True,text=True);check(r.returncode==0 and not r.stderr,['negative CLI no crash',case['case']]);out=json.loads(r.stdout,parse_constant=lambda x:(_ for _ in()).throw(ValueError('Nonstandard numeric result')));check(out==case['stdout_json']and out['status']==case['expected_status'],['negative CLI exact rejection',case['case']])
    pm=json.loads((ROOT/'peer-capture/manifest.json').read_text())
    for x in pm:check(sha((ROOT/x['captured']).read_bytes())==x['stored_sha256'],['immutable peer capture hash',x['captured']])
    owned=[STATE/'county-partisanship.md',STATE/'data/county-baselines.csv']+[p for p in ROOT.rglob('*')if p.is_file()]
    for p in owned:
        check(p.stat().st_size<40000000,['strict stored asset bound',str(p.relative_to(STATE))]);check('__pycache__'not in p.parts and not p.name.endswith('.pyc'),['no retained caches',str(p)])
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                if '://'in link or link.startswith('#'):continue
                link=link.split('#')[0].strip('<>');dest=(p.parent/link).resolve();check(dest.exists()or dest==ROOT/'validation.json',['relative Markdown link, current validation output may be generated at end of this run',str(p),link])
    counts.update(county_candidate_rows=len(cands),county_year_rows=len(county),authority_rows=len(inv),state_targets=len(states)+len(ast),live_synthetic_cases=len(cases),negative_CLI_cases=neg['cases'],reciprocal_peer_checks=peer['checks'],reciprocal_finer_priority_checks=np['checks'],reciprocal_final_availability_checks=fp['checks'],observed_zero_native_pair_contexts=observed_zero)
    result=dict(status='pass'if not errors else'fail',checks=checks,errors=errors,counts=counts,external_qualifications=['Source-native printed-known80 is an exact arithmetic scope, not legally exhaustive eligible-native vote allocation or current geographic approval.','27presidential source rows are not asserted to be27legal tickets. Named-vs-generic residuals are unallocated.','Historic source labels and IDs do not establish crossyear/current precinct or method compatibility.','No November2026final ballot/result-ID mapping, measured live pools/cadence, forecast or calibrated probability.','Current CSV A/I literals and historical Total Voters remain distinct; parent of current counts calls values unofficial.'],asset_seal='Run seal.py after validation; seal.py --check performs complete read-only final hash/size audit including this validation file.')
    if '--readonly'not in sys.argv:dump(ROOT/'validation.json',result)
    print(json.dumps({**result,'errors':errors[:10],'error_count':len(errors)},indent=2));assert not errors
if __name__=='__main__':main()

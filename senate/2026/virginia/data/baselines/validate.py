"""Independent arithmetic/source/identity audit. Default read-only; --write saves preseal QA."""
import collections,csv,gzip,hashlib,json,math,re,sys,tarfile
from pathlib import Path
from extract import ROOT,STATE,sources
def rows(n):return list(csv.DictReader((ROOT/n).open()))
def close(a,b,tol=1e-6):assert abs(a-b)<=tol,(a,b,a-b)
def piecewise(pools,shares,target):
    # Independent linear breakpoint sweep; calculator uses monotone bisection.
    events=collections.defaultdict(float)
    for w,q in zip(pools,shares):
        if w:events[-q]+=2*w;events[1-q]-=2*w
    current=-math.fsum(pools);previous=-1.;slope=0.
    for x,change in sorted(events.items()):
        nextnet=current+slope*(x-previous)
        if slope>0 and current-1e-7<=target<=nextnet+1e-7:
            return previous+(target-current)/slope
        current=nextnet;previous=x;slope+=change
    raise AssertionError('no piecewise root')
def audit_targets(table,state_table,mode):
    groups=collections.defaultdict(list)
    for r in rows(table):groups[r['scenario']].append(r)
    summaries={r['scenario']:r for r in rows(state_table)};assert set(groups)==set(summaries);maxres=0;count=0
    for name,rs in groups.items():
        s=summaries[name];is_sens=mode=='sensitivity';get=lambda r,f:float(r[f]);pool='pair_volume';q='baseline_share' if is_sens else 'baseline_A_share';net='target_net' if is_sens else 'bounded_target_net';share='target_share' if is_sens else 'bounded_target_share';base='baseline_net';expected_n=133 if is_sens or 'locality-native-aggregate' in name else {'2024-senate':2669,'2024-president':2669,'2020-senate':2846,'2018-senate':2825}[next(k for k in ['2024-senate','2024-president','2020-senate','2018-senate'] if name.startswith(k))];assert len(rs)==expected_n
        weights=[get(r,pool) for r in rs];shares=[get(r,q) if r[q] else 0 for r in rs];T=math.fsum(weights);target=float(s['target_net']);delta=piecewise(weights,shares,target);close(T,float(s['pair_denominator']));close(math.fsum(get(r,'pair_weight') for r in rs),1,1e-12);close(math.fsum(get(r,'all_weight' if is_sens else 'all_candidate_weight') for r in rs),1,1e-12)
        initial=math.fsum(w*(2*q-1) for w,q in zip(weights,shares));close(initial,float(s['baseline_net']));unbound=(target-initial)/(2*T);close(unbound,float(s['unbounded_shift' if is_sens else 'unbounded_share_shift']),1e-12);close(delta,float(s['bounded_shift' if is_sens else 'bounded_share_shift']),1e-10);actual=math.fsum(get(r,net) for r in rs if r[net]);maxres=max(maxres,abs(actual-target));close(actual,target)
        for r,w,q0 in zip(rs,weights,shares):
            count+=1;expected=min(1,max(0,q0+delta))
            if w:
                close(float(r[share]),expected,1e-10);close(float(r[net]),w*(2*expected-1));raw=(w+target-(initial-w*(2*q0-1)))/(2*w);close(raw,float(r['selected_only_raw_share' if is_sens else 'selected_only_required_share']),1e-8);status='secured' if raw<0 else 'impossible' if raw>1 else 'feasible';assert status==r['selected_only_status']
            else:assert not r[share] and r['selected_only_status']=='no-positive-pool'
            close(float(r['gain_net_per_share_pp']),.02*w)
    return {'scenarios':len(groups),'unit_target_rows':count,'maximum_net_residual':maxres,'independent_piecewise_and_selected_only':True}
def main():
    src=sources();summary={};allparents=None
    additional=json.loads((ROOT/'source/additional-pins.json').read_text());f=STATE/additional['receipt_path'];assert hashlib.sha256(f.read_bytes()).hexdigest()==additional['receipt_sha256'];e=additional['entity'];f=STATE/e['path'];raw=gzip.decompress(f.read_bytes());assert hashlib.sha256(f.read_bytes()).hexdigest()==e['sha256'] and hashlib.sha256(raw).hexdigest()==e['raw_sha256']
    for e in json.loads((ROOT/'source/legacy-provenance.json').read_text())['originals']:
        f=STATE/e['path'];assert hashlib.sha256(f.read_bytes()).hexdigest()==e['stored_sha256'] and hashlib.sha256(gzip.decompress(f.read_bytes())).hexdigest()==e['raw_sha256']
    for k in ['2024-senate','2024-president','2020-senate','2018-senate']:
        h=json.loads(gzip.decompress((ROOT/'extracted'/ (k+'.json.gz')).read_bytes()));nat=[r for r in h['rows'] if r['scope']=='Precinct'];par=[r for r in h['rows'] if r['scope']=='Locality'];assert len(par)==133 and len({r['name'] for r in par})==133;assert sum(r['name'].endswith(' County') for r in par)==95;assert sum(r['name'].endswith(' City') for r in par)==38
        for r in h['rows']:assert sum(r['votes'])==r['total']
        for i,v in enumerate(h['state']['votes']):assert sum(r['votes'][i] for r in nat)==v
        if allparents is None:allparents={r['name'] for r in par}
        else:assert allparents=={r['name'] for r in par}
        assert len({r['source_key'] for r in nat})==len(nat);summary[k]={'native':len(nat),'parents':133,'native_candidate_sums':h['native_sums'],'state':h['state']['votes'],'locality_sums':h['locality_sums'],'unallocated_discrepancies':h['discrepancies']}
    priority=json.loads((ROOT/'independent-priority.json').read_text())
    for scope in ['native','locality']:
        p=priority[scope];total=p['total'];n=p['minimum80_count'];order=p['order'];assert 5*sum(r['total'] for r in order[:n-1])<4*total<=5*sum(r['total'] for r in order[:n]);assert [(r['total'],r['record']) for r in order]==sorted([(r['total'],r['record']) for r in order],key=lambda x:(-x[0],x[1]));assert sum(r['total'] for r in order)==4445535
    assert len(rows('../county-baselines.csv'))==532 and len(rows('native-baselines.csv'))==11009
    hist=audit_targets('historical-unit-targets.csv','historical-state-targets.csv','historical');sens=audit_targets('sensitivity-localities.csv','sensitivity-state.csv','sensitivity')
    mt=collections.defaultdict(list)
    for r in rows('native-method-targets.csv'):mt[r['target']].append(r)
    for target,rs in mt.items():
        assert len(rs)==13345;T=math.fsum(float(r['pair']) for r in rs);close(T,4437026);close(math.fsum(float(r['target_net']) for r in rs if r['target_net']),float(target)*T);pool=[float(r['pair']) for r in rs];qs=[float(r['baseline_share']) if r['baseline_share'] else 0 for r in rs];root=piecewise(pool,qs,float(target)*T)
        for r,w,q in zip(rs,pool,qs):
            if w:close(float(r['target_share']),min(1,max(0,q+root)),1e-10)
            else:assert r['selected_status']=='no-positive-pool' and not r['baseline_share']
    # Independently recompute sensitivity source settings, including participation and native aggregate2018 denominator.
    baserows=rows('../county-baselines.csv');base={r['locality']:r for r in baserows if r['contest']=='2024-senate'};anchors={k:{r['locality']:r for r in baserows if r['contest']==k} for k in summary};settings=json.loads((ROOT/'build-settings.json').read_text());scenarios={r['scenario']:r for r in rows('sensitivity-state.csv')}
    for r in rows('sensitivity-localities.csv'):
        s=scenarios[r['scenario']];n=r['locality'];p=base[n];close(float(r['participation']),int(p['pair_votes'])/int(p['native_aggregate_all']),1e-12);mix=anchors[s['mix_anchor']];den=sum(int(v['native_aggregate_all']) for v in mix.values());volume=settings['volume_bases'][s['volume_anchor']];close(float(r['volume']),volume*int(mix[n]['native_aggregate_all'])/den);pref=anchors[s['preference_anchor']][n];close(float(r['baseline_share']),int(pref['A_votes'])/int(pref['pair_votes']),1e-12)
    candgroups=collections.defaultdict(lambda:collections.defaultdict(float))
    for r in rows('sensitivity-localities.csv'):
        votes=json.loads(r['target_candidate_votes_json']);close(math.fsum(votes.values()),float(r['volume']))
        for name,count in votes.items():candgroups[r['scenario']][name]+=count
    for r in rows('sensitivity-state.csv'):
        expected=json.loads(r['target_candidate_votes_json']);close(math.fsum(expected.values()),float(r['all_denominator']))
        assert set(expected)==set(candgroups[r['scenario']])
        for name,count in expected.items():close(count,candgroups[r['scenario']][name])
    for name in ['peer-reconciliation.json','peer-additional-reconciliation.json','peer-all-order-audit.json']:assert not json.loads((ROOT/name).read_text())['differences']
    cli=json.loads((ROOT/'cli-validation.json').read_text());assert cli['all_passed'] and cli['actual_cli_runs']>=55
    w=json.loads((ROOT/'pre-peer-witness.json').read_text());archive=ROOT/w['archive']['path'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==w['archive']['sha256']
    with tarfile.open(archive,'r:gz') as t:
        for f in w['files']:assert hashlib.sha256(t.extractfile(f['path']).read()).hexdigest()==f['sha256']
    capture=json.loads((ROOT/'peer-capture.json').read_text());p=ROOT/capture['archive']['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==capture['archive']['sha256']
    expected_peer={'data/turnout/priority-set.json':'10abc0f647f3b5019baee204757365012c4c235b0dc367db2c865c9567de4a71','data/turnout/asset-manifest.json':'6eafa8cc1a897b40075d8234681b832282d871490043b98ef3c7f5c878fd2b50'}
    with tarfile.open(p,'r:gz') as t:
        for f in capture['files']:assert hashlib.sha256(t.extractfile(f['path']).read()).hexdigest()==f['sha256']
        for name,h in expected_peer.items():assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==h
    owned=[p for p in ROOT.rglob('*') if p.is_file()]+[STATE/'county-partisanship.md',ROOT.parent/'county-baselines.csv'];assert all(p.stat().st_size<40000000 for p in owned);assert not list(ROOT.rglob('__pycache__'));assert not any(p.name in ['node_modules','.venv'] for p in ROOT.rglob('*'))
    for p in owned:
        if p.suffix=='.json':json.loads(p.read_text(),parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s))) if '/fixtures/' not in str(p) or not p.name.endswith('.input.json') else None
    deferred_links=[]
    for p in [STATE/'county-partisanship.md',ROOT/'source/SCHEMA.md']:
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if not re.match(r'^[a-z]+:',link):
                target=p.parent/link.split('#')[0]
                if '--write' in sys.argv and not target.exists() and target.name in ['validation.json','asset-manifest.json','final-seal.json']:deferred_links.append(str(target.relative_to(STATE)))
                else:assert target.exists(),(p,link)
    result={'status':'passed','source_pin_count':len(src),'source_scopes':summary,'priority_native':{k:v for k,v in priority['native'].items() if k not in ('order','priority_keys')},'historical':hist,'sensitivity':sens,'native_method_target_rows':26690,'all133parents_and_nonpriority_retained':True,'cli':{'actual_runs':cli['actual_cli_runs'],'strict_json_no_stderr':cli['strict_json_and_no_stderr']},'peer_order_scopes':17,'pre_peer_frozen_bodies_checked':len(w['files']),'owned_asset_bounds_checked':True,'existing_relative_links_checked':True,'preseal_deferred_links':deferred_links,'scope_qualifications':['Generic marks not eligible named-writein allocation','2018footer36mark discrepancy unallocated','2018/2020 compiled page conflicting-source notes remain','API/CSV/annual/registration scopes differ; not inferred under/over votes','No current geometry or2026 feed ID mapping; no calibrated probability']}
    if '--write' in sys.argv:(ROOT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    if '--sealed' in sys.argv:
        m=json.loads((ROOT/'asset-manifest.json').read_text());actual={str(p.relative_to(STATE)) for p in owned if p!=ROOT/'asset-manifest.json'};assert actual=={r['path'] for r in m['files']}
        for r in m['files']:
            p=STATE/r['path'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
        seal=json.loads((ROOT/'final-seal.json').read_text())
        for r in seal['files']:assert hashlib.sha256((STATE/r['path']).read_bytes()).hexdigest()==r['sha256']
        result['after_seal_read_only_exact_membership_hash_audit']='passed'
    print(json.dumps(result,separators=(',',':')))
if __name__=='__main__':main()

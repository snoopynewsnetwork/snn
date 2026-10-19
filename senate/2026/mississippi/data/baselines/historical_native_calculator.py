"""2020 original-native pair arithmetic; no cross-year native identity join.

Preferred82 uses an actual linked amendment when present. Each of22 other
publications is a separate whole-county replacement sensitivity, never added.
Other-year county mixes/preferences applied to2020native weights are explicit
conditional assumptions, not historical precinct observations or2026 forecasts.
"""
import argparse,csv,gzip,io,json
from collections import defaultdict,Counter
from sources import OUT,BASE,sha,save
from build_counties import writecsv
from calculator import bounded_shift,clip,status
ANCHORS=['2020-senate','2024-senate','2024-president','2018-special','2018-runoff']
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']

def pinned_inputs():
    sp=OUT/'source/native-2020-104views-v1/snapshot.json';snap=json.loads(sp.read_text());bodies={}
    for p in snap['pins']:
        stored=(BASE/p['stored_path']).read_bytes();assert len(stored)==p['stored_bytes'] and sha(stored)==p['stored_sha256'];raw=gzip.decompress(stored);assert len(raw)==p['original_bytes'] and sha(raw)==p['original_sha256'];bodies[p['original_path'].split('/')[-1]]=json.loads(raw) if p['original_path'].endswith('.json') else raw
    coverage=bodies['native-2020-coverage.json'];assert coverage['complete_all104_native_Senate_three_candidates'];selected={s['source_id'] for s in coverage['all104_publication_status'] if s['selected_for_82_county_amended_where_explicit_control']};units=[];admin=[];sources={}
    for name in ['coahoma-2020-amendment-readings.json','native-2020-additional-readings.json']:
        for s in bodies[name]['sources']:
            sid=s['source_id'];assert sid not in sources;sources[sid]=s;fips=s['county_fips']
            for page in s['pages']:
                fields={f['candidate']:f['values'] for f in page['fields']};assert set(fields)==set(NAMES)
                for i,c in enumerate(page['columns']):
                    if c['role'] not in ['source_native_reporting_constituent','source_administrative_reporting_column']:continue
                    a,b,o=[fields[n][i] for n in NAMES];assert all(type(v) is int and v>=0 for v in [a,b,o]);pair=a+b
                    row=dict(source_key=f'{fips}:{sid}:p{page["page"]}:c{c["source_column"]}',county_fips=fips,source_id=sid,source_raw_sha256=s['raw_sha256'],source_page=page['page'],source_column=c['source_column'],label_literal=c['label_literal'],role=c['role'],selected_publication=sid in selected,A_name=NAMES[0],A_party='Democrat',A=a,B_name=NAMES[1],B_party='Republican',B=b,other_name=NAMES[2],other_party='Libertarian',other=o,pair_votes=pair,named_candidate_votes=pair+o,A_pair_share=a/pair if pair else None)
                    (units if c['role']=='source_native_reporting_constituent' else admin).append(row)
    assert len(sources)==104 and len(selected)==82 and len(units)==2131 and len(admin)==1
    preferred=[u for u in units if u['selected_publication']];assert len(preferred)==1765 and Counter({n:sum(u[k] for u in preferred) for n,k in zip(NAMES,['A','B','other'])})==Counter(dict(zip(NAMES,[578691,709511,23152])))
    assert all(u[k]==0 for u in admin for k in ['A','B','other'])
    return sp,units,admin,selected

def volume_scenarios(cc,parents):
    base=sum(p['pair'] for p in parents.values())
    specs=[('high-observed2020-native',None,'Observed2020 same-seat native pair counts'),('low-2022-EAC-ballots','eac_2022_F1a','2022EACF1a county counted ballots; illustrative pair participation1, not Senate participation'),('base-2024-Senate-county-mix','2024-senate_pair_votes','Observed2024other-seat Senate county pair volumes over2020within-parent native weights'),('midterm2018-special-county-mix','2018-special_pair_votes','ObservedNov6Espy/Hyde-Smith county pair volume, separate Bartee/McDaniel identities'),('midterm2018-runoff-county-mix','2018-runoff_pair_votes','ObservedNov27county runoff pair volume, separate electorate')]
    for key,field,basis in specs:
        w={f:float(cc[f][field]) if field else float(parents[f]['pair']) for f in parents};yield key,w,basis
        if field:
            scale=base/sum(w.values());yield key+'-normalized-to-2020-pair',{f:v*scale for f,v in w.items()},basis+'; common statewide scale to1288202 isolates county mix'

def partitions(units):
    preferred=[u for u in units if u['selected_publication']];yield 'preferred82',preferred,True
    for sid in sorted({u['source_id'] for u in units if not u['selected_publication']}):
        replacement=[u for u in units if u['source_id']==sid];f=replacement[0]['county_fips'];assert all(u['county_fips']==f for u in replacement)
        yield 'replace-'+sid,[u for u in preferred if u['county_fips']!=f]+replacement,False

def build():
    sp,units,admin,selected=pinned_inputs();cc={r['fips']:r for r in csv.DictReader((BASE/'data/county-baselines.csv').open())};assert len(cc)==82
    folder=OUT/'historical-native-targets';folder.mkdir(exist_ok=True);states=[];countyrows=[];pins=[];rowcount=0;partition_meta=[];locals=[]
    for u in units+admin:
        n=u['pair_votes'];q=u['A_pair_share'];net=u['A']-u['B']
        for m in [0,.01]:
            locals.append(u|dict(target_pair_margin_pp=100*m,local_target_A_share=(1+m)/2 if n else None,local_share_shift_pp=100*((1+m)/2-q) if n else None,local_net_gain=m*n-net if n else None,local_named_all_candidate_denominator=u['named_candidate_votes'],local_target_A_minus_B_all_candidate_margin_pp=100*m*n/u['named_candidate_votes'] if u['named_candidate_votes'] else None,local_strict_named_plurality_requires_A_pair_share_greater_than=max(.5,u['other']/n) if n else None,local_status='feasible_pair_target' if n else 'no_positive_pool'))
    writecsv(OUT/'native-2020-local-targets.csv',locals)
    for partition,uu,is_preferred in partitions(units):
        parents=defaultdict(lambda:dict(pair=0,other=0))
        for u in uu:p=parents[u['county_fips']];p['pair']+=u['pair_votes'];p['other']+=u['other']
        assert set(parents)==set(cc) and all(p['pair']>0 for p in parents.values());partition_meta.append(dict(partition=partition,native_units=len(uu),state_counties=82,pair_votes=sum(p['pair'] for p in parents.values()),other_name=NAMES[2],other_votes=sum(p['other'] for p in parents.values()),source_ids=sorted({u['source_id'] for u in uu}),qualification='Each source-native partition keeps all82parents; alternative replaces only its actual county source, without native-name joins or shared release-vintage inference.'))
        variants=list(volume_scenarios(cc,parents)) if is_preferred else [('observed2020-source-replacement',{f:float(p['pair']) for f,p in parents.items()},'Actual2020named source pair for all82 counties; one explicitly identified county publication replaces selected version')]
        for scenario,cw,basis in variants:
            buf=io.StringIO();writer=None;file_rows=0
            for anchor in ANCHORS if is_preferred else ['2020-senate']:
                weights=[cw[u['county_fips']]*u['pair_votes']/parents[u['county_fips']]['pair'] for u in uu];T=sum(weights);assert abs(T-sum(cw.values()))<1e-6
                qs=[u['A_pair_share'] if anchor=='2020-senate' else float(cc[u['county_fips']][anchor+'_A_pair_share']) for u in uu];assert all(q is not None for q,w in zip(qs,weights) if w>0);qs=[q if q is not None else .5 for q in qs]
                outsiders={f:p['other'] if anchor=='2020-senate' else int(cc[f][anchor+'_other']) for f,p in parents.items()};O=sum(outsiders.values());D=T+O;base_net=sum(w*(2*q-1) for w,q in zip(weights,qs))
                for margin in [0,.01]:
                    target=margin*T;sol=bounded_shift(weights,qs,target);group=f'{partition}|{scenario}|{anchor}|{100*margin:g}';agg=defaultdict(lambda:dict(pair=0.,baseline_net=0.,target_net=0.,net_gain=0.))
                    states.append(dict(group=group,partition=partition,scenario=scenario,preference_anchor=anchor,target_pair_margin_pp=100*margin,native_units=len(uu),state_counties=82,pair_votes=T,historical_named_other_votes_fixed=O,conditional_named_all_candidate_denominator=D,conditional_A_minus_B_all_candidate_margin_pp=100*target/D,conditional_A_named_share=(T+target)/(2*D),volume_basis=basis,**{k:v for k,v in sol.items() if k!='shares'}))
                    for u,w,q0,q in zip(uu,weights,qs,sol['shares']):
                        old=w*(2*q0-1);fixed=base_net-old;required=(w+target-fixed)/(2*w) if w else None;new=w*(2*q-1);a=agg[u['county_fips']];a['pair']+=w;a['baseline_net']+=old;a['target_net']+=new;a['net_gain']+=new-old
                        row=u|dict(group=group,partition=partition,scenario=scenario,preference_anchor=anchor,target_pair_margin_pp=100*margin,within_parent_historical_pair_weight=u['pair_votes']/parents[u['county_fips']]['pair'],county_conditional_pair_pool=cw[u['county_fips']],expected_pair_votes=w,state_pair_votes=T,state_pair_weight=w/T,baseline_A_share=q0,baseline_net=old,target_A_share=q,target_net=new,net_gain=new-old,net_gain_for_one_A_share_pp=.02*w,state_baseline_net=base_net,state_target_net=target,uniform_unbounded_share_shift_pp=100*sol['unbounded_shift'],uniform_bounded_share_shift_pp=100*sol['bounded_shift'],share_clipped=(q!=q0+sol['bounded_shift']),selected_only_fixed_other_net=fixed,selected_only_required_A_share=required,selected_only_required_shift_pp=100*(required-q0) if w else None,selected_only_status=status(required) if w else 'no_positive_pool',selected_only_clipped_display_share=clip(required) if w else None,conditional_state_named_all_candidate_denominator=D)
                        if writer is None:writer=csv.DictWriter(buf,fieldnames=list(row));writer.writeheader()
                        writer.writerow(row);rowcount+=1;file_rows+=1
                    for f,a in agg.items():countyrows.append(dict(group=group,partition=partition,scenario=scenario,preference_anchor=anchor,target_pair_margin_pp=100*margin,county_fips=f,county=cc[f]['county'],state_pair_weight=a['pair']/T,named_other_votes_fixed=outsiders[f],conditional_named_denominator=a['pair']+outsiders[f],**a))
            raw=buf.getvalue().encode();packed=gzip.compress(raw,mtime=0);path=folder/(partition+'--'+scenario+'.csv.gz');assert len(packed)<40000000;path.write_bytes(packed);pins.append(dict(path=str(path.relative_to(BASE)),bytes=len(packed),sha256=sha(packed),original_csv_bytes=len(raw),original_csv_sha256=sha(raw),rows=file_rows,partition=partition,scenario=scenario,compression='Lossless gzip; exact ordered original CSV bytes by decompression'))
    assert len(states)==134 and len(countyrows)==10988 and len(partition_meta)==23 and len(pins)==31 and len(locals)==4264
    writecsv(OUT/'native-2020-state-targets.csv',states);writecsv(OUT/'native-2020-county-contributions.csv',countyrows)
    save(OUT/'native-2020-calculator-settings.json',dict(input_witness=dict(path=str(sp.relative_to(BASE)),bytes=sp.stat().st_size,sha256=sha(sp.read_bytes())),native_observations_across_alternatives=2131,preferred_native_units=1765,administrative_observations=1,preferred_named_candidates=dict(zip(NAMES,[578691,709511,23152])),preferred_pair_votes=1288202,preferred_named_all_candidate_denominator=1311354,partitions=partition_meta,preference_anchors=ANCHORS,state_groups=len(states),county_contribution_rows=len(countyrows),unit_target_rows=rowcount,source_local_target_rows=len(locals),compressed_unit_outputs=pins,volume='Declared historical low2022EAC/base2024county/highobserved2020 plus distinct2018stage county mixes; within-parent2020source-native pair weights. Pair participation1 is explicit only for illustrativeEACpool; not observed2022Senate or2026participation. Common-volume normalizations isolate composition.',preference='Observed source2020native preference only for2020anchor. Other anchors apply actual historical COUNTY pair share uniformly within its2020source parent; no cross-year native join, candidate effect, lower preferences or2026forecast inferred.',outsiders='JimmyL.Edwards Libertarian stays individually named; actual2020native other counts in local tables and source partition state pool. Other anchors retain actual historical county named outsider pool fixed, without allocating it to2020native units. Generic write-ins remain unresolved, not zero. Special/runoff stages never merged.',selected_only='Every other native unit in all82county parents fixed at its stated scenario volume and anchor share; source-named outsiders held fixed. Required selected share is unbounded, alongside explicit clipped display/status; clipping is not feasibility.',threshold='Pair tie and illustrativeA+1pair-margin targets are arithmetic, not a legal threshold or2026candidate mapping. Current regular Senate plurality requires beating each actual named rival; historical2018special majority/top-two rules remain separate.',formula='Local fixed-pair tie share shift=(B-A)/(2*(A+B)); A+1pair margin adds0.005share=0.5share percentagepoints. Uniform state shifts are bounded with clip(q0+s,0,1). Net gain=2*w*(q-q0); selectedq=(w+targetNet-fixedOtherNet)/(2*w).',complete_historical_method_question=False,current2026_geography_approved=False,calibrated_probability=False,real2026_forecast=False))
    print('2020 original-native targets',len(states),'state',rowcount,'native rows',len(countyrows),'county',len(locals),'source local')

def selected_cli(key,others_shift_pp,target_margin_pp):
    _,units,_,_=pinned_inputs();u=next(u for u in units if u['source_key']==key);partition=[p for _,p,_ in partitions(units) if any(x['source_key']==key for x in p)][0];n=u['pair_votes'];T=sum(x['pair_votes'] for x in partition);fixed=sum(x['pair_votes']*(2*clip((x['A_pair_share'] if x['A_pair_share'] is not None else .5)+others_shift_pp/100)-1) for x in partition if x['source_key']!=key);target=T*target_margin_pp/100;q=(n+target-fixed)/(2*n) if n else None
    print(json.dumps(u|dict(state_counties=82,native_units=len(partition),state_pair_denominator=T,fixed_other_net=fixed,others_shift_share_pp=others_shift_pp,other_assumption='Every other source-native unit at own2020pair preference plus supplied shift explicitly clipped[0,1], actual same-publication2020pair volume; namedEdwards fixed, generic scope unknown',target_state_pair_margin_pp=target_margin_pp,required_A_share=q,status=status(q) if n else 'no_positive_pool',clipped_display_share=clip(q) if n else None),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit');p.add_argument('--others-shift-pp',type=float,default=0);p.add_argument('--target-pair-margin-pp',type=float,default=0);a=p.parse_args()
    if a.unit:selected_cli(a.unit,a.others_shift_pp,a.target_pair_margin_pp)
    else:build()

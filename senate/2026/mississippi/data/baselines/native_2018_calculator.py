"""Conditional arithmetic on all164 actual2018county-stage original native grids.

Unknown literalX fields remain unknown rows, excluded from the explicitly known
numeric modeled pool. Leflore special native−TOTAL10 remains unallocated.
Separate stages, electorates, source denominators and all named outsiders.
"""
import argparse,csv,gzip,io,json
from collections import defaultdict,Counter
from sources import OUT,BASE,sha,save
from build_counties import writecsv
from calculator import bounded_shift,clip,status
ANCHORS=['2018-special','2018-runoff','2020-senate','2024-senate','2024-president']
NAMES={'special':['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],'runoff':['Mike Espy','Cindy Hyde-Smith']}

def load_inputs():
    sp=OUT/'source/native-2018-164views-v1/snapshot.json';snap=json.loads(sp.read_text());docs={}
    for p in snap['pins']:
        z=(BASE/p['stored_path']).read_bytes();r=gzip.decompress(z);assert len(z)==p['stored_bytes'] and sha(z)==p['stored_sha256'] and len(r)==p['original_bytes'] and sha(r)==p['original_sha256'];docs[p['original_path'].split('/')[-1]]=json.loads(r) if p['original_path'].endswith('.json') else r
    ledger=docs['native-2018-original-readings.json'];assert ledger['complete2018_named_candidate_native_source_review'] and len(ledger['sources'])==164
    units=[];admins=[]
    source_fips={r['source_id']:r['county_fips'] for r in csv.DictReader(io.StringIO(docs['native-2018-original-candidate-votes.csv'].decode()))}
    for s in ledger['sources']:
        s=dict(s,county_fips=source_fips[s['source_id']])
        for p in s['pages']:
            fields={f['candidate']:f for f in p['fields']};assert set(fields)==set(NAMES[s['stage']])
            for i,c in enumerate(p['columns']):
                if c['role'] not in ['native','administrative']:continue
                values={n:fields[n]['values'][i] for n in NAMES[s['stage']]};marks={n:fields[n].get('source_marks',{}).get(str(i+1)) for n in values};unknown=any(v is None for v in values.values());assert not unknown or all(v=='X' for v in marks.values())
                a,b=values['Mike Espy'],values['Cindy Hyde-Smith'];o={n:v for n,v in values.items() if n not in ['Mike Espy','Cindy Hyde-Smith']};pair=None if unknown else a+b
                u=dict(source_key=f'{s["county_fips"]}:{s["source_id"]}:p{p["page"]}:c{c["source_column"]}',stage=s['stage'],county_fips=s['county_fips'],source_id=s['source_id'],source_raw_sha256=s['raw_sha256'],source_page=p['page'],source_column=c['source_column'],label_literal=c['label_literal'],role=c['role'],source_mark_status='literal_X_unknown_numeric' if unknown else 'source_numeric',source_marks=json.dumps(marks,sort_keys=True),A_name='Mike Espy',A=a,B_name='Cindy Hyde-Smith',B=b,source_party_fields='unprinted/null; no forced party union',source_named_candidates=json.dumps(values,sort_keys=True),source_named_outsiders=json.dumps(o,sort_keys=True),pair_votes=pair,named_candidate_votes=None if unknown else pair+sum(o.values()),A_pair_share=a/pair if pair else None)
                (units if c['role']=='native' else admins).append(u)
    assert len(units)==3545 and len(admins)==3 and sum(u['pair_votes'] is None for u in units)==3
    return sp,ledger,units,admins

def county_anchors(cc):
    rows=list(csv.DictReader((OUT/'candidate-votes.csv').open()));allfield=defaultdict(list)
    for r in rows:allfield[(r['contest'],r['fips'])].append(r)
    result={}
    for anchor in ANCHORS:
        for f in cc:
            rr=allfield[anchor,f];isA=lambda r: ('Kamala D. Harris' in r['candidate_literal'] if anchor=='2024-president' else 'Ty Pinkins' in r['candidate_literal'] if anchor=='2024-senate' else r['candidate_literal'].strip()=='Mike Espy')
            isB=lambda r: ('Donald J. Trump' in r['candidate_literal'] if anchor=='2024-president' else 'Roger F. Wicker' in r['candidate_literal'] if anchor=='2024-senate' else r['candidate_literal'].strip()=='Cindy Hyde-Smith')
            aa=[r for r in rr if isA(r)];bb=[r for r in rr if isB(r)];assert len(aa)==len(bb)==1,(anchor,f)
            others={r['candidate_literal']:dict(votes=int(r['votes']),party_literal=r['party_literal']) for r in rr if not isA(r) and not isB(r)};assert int(aa[0]['votes'])+int(bb[0]['votes'])==int(cc[f][anchor+'_pair_votes']);assert sum(v['votes'] for v in others.values())==int(cc[f][anchor+'_other'])
            result[anchor,f]=others
    return result

def scenarios(stage,cc,parents):
    native=sum(p['pair'] for p in parents.values());otherstage='2018-runoff' if stage=='special' else '2018-special'
    specs=[('observed2018-'+stage,None,'Observed exact-stage known numerical source pair, excluding literalX unknown fields'),('low-2022-EAC-ballots','eac_2022_F1a','Source2022EACF1a county ballots with illustrative pair participation1, not observed Senate participation'),('base-2024-Senate-county-mix','2024-senate_pair_votes','Actual2024other-seat county pair volumes'),('high-2020-Senate-county-mix','2020-senate_pair_votes','Actual2020same-seat county pair volumes'),('other-midterm-stage-county-mix',otherstage+'_pair_votes','Other actual2018stage county pair volume applied conditionally; not merged electorate')]
    for name,field,basis in specs:
        weights={f:float(cc[f][field]) if field else float(parents[f]['pair']) for f in cc};yield name,weights,basis
        if field:
            ratio=native/sum(weights.values());yield name+'-normalized-to-stage-pair',{f:w*ratio for f,w in weights.items()},basis+'; explicitly common-volume normalized to known numeric source-stage pool, not residual allocation'

def build():
    sp,ledger,units,admins=load_inputs();cc={r['fips']:r for r in csv.DictReader((BASE/'data/county-baselines.csv').open())};anchors=county_anchors(cc);assert len(cc)==82
    states=[];countyrows=[];locals=[];pins=[];totalrows=0;metadata=[];folder=OUT/'native-2018-targets';folder.mkdir(exist_ok=True)
    for u in units+admins:
        n=u['pair_votes'];q=u['A_pair_share'];net=None if n is None else u['A']-u['B'];outs=json.loads(u['source_named_outsiders']);O=sum(outs.values()) if n is not None else None
        for margin in [0.,.01]:
            good=n is not None and n>0
            locals.append(u|dict(target_pair_margin_pp=100*margin,local_target_A_share=(1+margin)/2 if good else None,local_share_shift_pp=100*((1+margin)/2-q) if good else None,local_net_gain=margin*n-net if good else None,local_target_all_named_A_minus_B_margin_pp=100*margin*n/(n+O) if good else None,local_majority_requires_A_pair_share_greater_than=(n+O)/(2*n) if good else None,local_strict_named_plurality_requires_A_pair_share_greater_than=max(.5,max(outs.values(),default=0)/n) if good else None,local_majority_cushion_net=margin*n-O if good else None,local_status='unknown_source_mark' if n is None else 'feasible_pair_target' if n else 'no_positive_pool'))
    writecsv(OUT/'native-2018-local-targets.csv',locals)
    for stage in ['special','runoff']:
        uu=[u for u in units if u['stage']==stage];known=[u for u in uu if u['pair_votes'] is not None];unknown=[u for u in uu if u['pair_votes'] is None];parents=defaultdict(lambda:dict(pair=0,outsiders=Counter()))
        for u in known:parents[u['county_fips']]['pair']+=u['pair_votes'];parents[u['county_fips']]['outsiders'].update(json.loads(u['source_named_outsiders']))
        assert set(parents)==set(cc) and all(p['pair']>0 for p in parents.values());source_totals=Counter()
        for s in ledger['sources']:
            if s['stage']==stage:source_totals.update(s['controls']['printed_TOTAL'])
        actual=Counter()
        for u in known:actual.update(json.loads(u['source_named_candidates']))
        differences={n:actual[n]-source_totals[n] for n in NAMES[stage]};assert differences==({'Tobey Bernard Bartee':0,'Mike Espy':-10,'Cindy Hyde-Smith':0,'Chris McDaniel':0} if stage=='special' else {'Mike Espy':0,'Cindy Hyde-Smith':0})
        T0=sum(p['pair'] for p in parents.values());metadata.append(dict(stage=stage,source_publications=82,native_observations=len(uu),known_numeric_native=len(known),unknown_source_mark_native=len(unknown),known_numeric_pair_votes=T0,native_known_candidate_sums=dict(actual),printed_county_TOTAL_candidate_sums=dict(source_totals),known_native_minus_printed_TOTAL=differences,unknown_unit_keys=[u['source_key'] for u in unknown]))
        for scenario,cw,basis in scenarios(stage,cc,parents):
            buf=io.StringIO();writer=None;nrows=0
            for anchor in ANCHORS:
                weights=[cw[u['county_fips']]*u['pair_votes']/parents[u['county_fips']]['pair'] for u in known];T=sum(weights);assert abs(T-sum(cw.values()))<1e-6
                qs=[(u['A_pair_share'] if u['A_pair_share'] is not None else .5) if anchor=='2018-'+stage else float(cc[u['county_fips']][anchor+'_A_pair_share']) for u in known]
                outside={f:dict(p['outsiders']) if anchor=='2018-'+stage else {n:v['votes'] for n,v in anchors[anchor,f].items()} for f,p in parents.items()};stateother=Counter()
                for o in outside.values():stateother.update(o)
                O=sum(stateother.values());D=T+O;base=sum(w*(2*q-1) for w,q in zip(weights,qs))
                for margin in [0.,.01]:
                    target=T*margin;sol=bounded_shift(weights,qs,target);group=f'{stage}|{scenario}|{anchor}|{100*margin:g}';agg=defaultdict(lambda:dict(pair=0.,baseline_net=0.,target_net=0.,net_gain=0.))
                    states.append(dict(group=group,stage=stage,scenario=scenario,preference_anchor=anchor,target_pair_margin_pp=100*margin,state_counties=82,native_observations=len(uu),known_numeric_native=len(known),unknown_source_mark_native=len(unknown),pair_votes=T,named_outsiders_fixed=json.dumps(dict(stateother),sort_keys=True),named_other_votes_fixed=O,conditional_named_denominator=D,target_A_named_share=(T+target)/(2*D),target_A_minus_B_all_named_margin_pp=100*target/D,majority_cushion_net=target-O,strict_majority_requires_pair_share_greater_than=(T+O)/(2*T),strict_named_plurality_requires_pair_share_greater_than=max(.5,max(stateother.values(),default=0)/T),source_stage_pair_votes=T0,source_stage_certified_pair_votes=source_totals['Mike Espy']+source_totals['Cindy Hyde-Smith'],volume_basis=basis,unknown_and_residual_scope='Known numeric source model only; literalX cells unmodeled/null and Leflore specialEspy10unallocated; no certified denominator identity claim',**{k:v for k,v in sol.items() if k!='shares'}))
                    for u,w,q0,q in zip(known,weights,qs,sol['shares']):
                        old=w*(2*q0-1);new=w*(2*q-1);fixed=base-old;req=(w+target-fixed)/(2*w) if w else None;a=agg[u['county_fips']];a['pair']+=w;a['baseline_net']+=old;a['target_net']+=new;a['net_gain']+=new-old
                        row=u|dict(group=group,scenario=scenario,preference_anchor=anchor,target_pair_margin_pp=100*margin,model_status='known_numeric_source',within_parent_known_pair_weight=u['pair_votes']/parents[u['county_fips']]['pair'],county_conditional_pair_pool=cw[u['county_fips']],expected_pair_votes=w,state_pair_votes=T,state_pair_weight=w/T,baseline_A_share=q0,baseline_net=old,target_A_share=q,target_net=new,net_gain=new-old,net_gain_for_one_A_share_pp=.02*w,state_baseline_net=base,state_target_net=target,uniform_unbounded_share_shift_pp=100*sol['unbounded_shift'],uniform_bounded_share_shift_pp=100*sol['bounded_shift'],share_clipped=q!=q0+sol['bounded_shift'],selected_only_fixed_other_net=fixed,selected_only_required_A_share=req,selected_only_required_shift_pp=100*(req-q0) if w else None,selected_only_status=status(req) if w else 'no_positive_pool',selected_only_clipped_display_share=clip(req) if w else None,conditional_state_named_denominator=D)
                        if writer is None:writer=csv.DictWriter(buf,fieldnames=list(row));writer.writeheader()
                        writer.writerow(row);nrows+=1;totalrows+=1
                    for u in unknown:
                        row={k:None for k in writer.fieldnames};row.update(u);row.update(group=group,scenario=scenario,preference_anchor=anchor,target_pair_margin_pp=100*margin,model_status='unknown_source_mark_unmodeled',state_pair_votes=T,state_baseline_net=base,state_target_net=target,selected_only_status='unknown_source_mark',conditional_state_named_denominator=D);writer.writerow(row);nrows+=1;totalrows+=1
                    for f,a in agg.items():countyrows.append(dict(group=group,stage=stage,scenario=scenario,preference_anchor=anchor,target_pair_margin_pp=100*margin,county_fips=f,county=cc[f]['county'],state_pair_weight=a['pair']/T,named_outsiders_fixed=json.dumps(outside[f],sort_keys=True),conditional_named_denominator=a['pair']+sum(outside[f].values()),**a))
            raw=buf.getvalue().encode();z=gzip.compress(raw,mtime=0);path=folder/(stage+'--'+scenario+'.csv.gz');assert len(z)<40000000;path.write_bytes(z);pins.append(dict(path=str(path.relative_to(BASE)),bytes=len(z),sha256=sha(z),original_csv_bytes=len(raw),original_csv_sha256=sha(raw),rows=nrows,stage=stage,scenario=scenario))
    assert len(states)==180 and len(countyrows)==14760 and len(locals)==7096 and totalrows==319050
    writecsv(OUT/'native-2018-state-targets.csv',states);writecsv(OUT/'native-2018-county-contributions.csv',countyrows)
    save(OUT/'native-2018-calculator-settings.json',dict(input_witness=dict(path=str(sp.relative_to(BASE)),bytes=sp.stat().st_size,sha256=sha(sp.read_bytes())),stage_scopes=metadata,preference_anchors=ANCHORS,state_groups=len(states),unit_target_rows=totalrows,county_contribution_rows=len(countyrows),local_target_rows=len(locals),compressed_unit_outputs=pins,volume='Historical low2022EAC/base2024Senate/high2020Senate county pools plus observed2018native stage and other2018stage mix, each explicitly separate. Within-parent weights use only exact-stage known numerical native pair. LiteralXunknowns carried as unmodeled rows, not zero-weight observations. Common-volume normalization isolates mix only.',preference='Actual stage native share only when anchor matches same stage. Other-year/stage actual county A/B shares applied uniformly within source2018parent as explicit hypothetical assumptions, not native cross-year joins or inferred candidate/lower-preference effects.',other_candidates='All named outsiders retained individually. Nov6Bartee andMcDaniel never forced into Democratic or Republican pools. Historical anchor county outsider pools held fixed with names/parties in candidate-votes.csv; no generic write-in absence/zero inference. Local source-native outsider counts retained.',threshold='Pair tie/A+1margin are illustrative arithmetic. Nov6special legalmajority/all-valid candidate denominator andtop-two runoff remain distinct; majority cushion=pairnet−fixednamedother, requiredAshare>(T+O)/(2T). ActualNov27runoff is a separate electorate. Full validwrite-in/generic scope unavailable; named denominator not all-ballot denominator. Current2026plurality has separate actual3candidate mapping.',selected_only='Every other modeled known-numeric native unit in all82parents fixed at declared scenario/anchor; named outsiders fixed. Unknown literalX and source residual remain unallocated. Each required share unbounded/status separate from clipped display. All nonpriority units retained.',formula='Local tie=(B−A)/(2*(A+B));A+1pairmargin adds0.005share=0.5sharepp. Netgain=2*w*(q−q0),shares clip[0,1]. Bounded uniform solution; selectedq=(w+targetnet−fixedothernet)/(2*w). Shares/marginpoints/netvotes/nameddenominator kept separate.',current2026_geography_approved=False,calibrated_probability=False,real2026_turnout_forecast=False))
    print('2018targets',len(states),'state',totalrows,'unit',len(countyrows),'county',len(locals),'local')

def selected_cli(key,others_shift_pp,target_margin_pp):
    _,ledger,units,admins=load_inputs();u=next(r for r in units+admins if r['source_key']==key);uu=[r for r in units if r['stage']==u['stage']];known=[r for r in uu if r['pair_votes'] is not None];unknown=[r['source_key'] for r in uu if r['pair_votes'] is None];T=sum(r['pair_votes'] for r in known);n=u['pair_votes'];fixed=sum(r['pair_votes']*(2*clip((r['A_pair_share'] if r['A_pair_share'] is not None else .5)+others_shift_pp/100)-1) for r in known if r['source_key']!=key);target=T*target_margin_pp/100;required=(n+target-fixed)/(2*n) if n else None
    print(json.dumps(u|dict(state_counties=82,native_observations=len(uu),known_numeric_state_pair=T,unknown_unit_keys=unknown,unallocated_Leflore_special_Espy=10 if u['stage']=='special' else 0,other_unit_assumption='Each other known native unit uses exact-stage pair volume and observed source preference plus supplied share-point shift clipped[0,1]; named outsiders fixed; literalX units unmodeled, source residual unallocated',others_share_shift_pp=others_shift_pp,target_pair_margin_pp=target_margin_pp,fixed_other_net=fixed,required_A_share=required,clipped_display_share=clip(required) if required is not None else None,status='unknown_source_mark' if n is None else status(required) if n else 'no_positive_pool'),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit');p.add_argument('--others-shift-pp',type=float,default=0);p.add_argument('--target-pair-margin-pp',type=float,default=0);a=p.parse_args()
    if a.unit:selected_cli(a.unit,a.others_shift_pp,a.target_pair_margin_pp)
    else:build()

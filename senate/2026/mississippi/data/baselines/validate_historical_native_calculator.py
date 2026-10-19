"""Independent source/weight/formula audit and piecewise saturation solution.

Does not import the calculator or its bisection solver. Integrates the slope
changes at every native clipping breakpoint to verify each bounded shift.
"""
import csv,gzip,io,json,math
from collections import defaultdict,Counter
from sources import OUT,BASE,sha,save,original

def close(a,b,tol=1e-6):assert abs(float(a)-float(b))<=tol,(a,b)
def clip(q):return max(0.,min(1.,q))
def piecewise(weights,shares,target):
    events=defaultdict(float);total=sum(weights)
    for w,q in zip(weights,shares):
        if w:events[-q]+=2*w;events[1-q]-=2*w
    x=-1.;value=-total;slope=0.
    for end,change in sorted(events.items()):
        after=value+slope*(end-x)
        if slope>0 and value-1e-6<=target<=after+1e-6:return x+(target-value)/slope
        x=end;value=after;slope+=change
    raise AssertionError(('no feasible piecewise root',target,total))

def main():
    settings_path=OUT/'native-2020-calculator-settings.json';settings=json.loads(settings_path.read_text());sp=BASE/settings['input_witness']['path'];assert sp.stat().st_size==settings['input_witness']['bytes'] and sha(sp.read_bytes())==settings['input_witness']['sha256'];snap=json.loads(sp.read_text());docs={}
    for pin in snap['pins']:
        z=(BASE/pin['stored_path']).read_bytes();r=gzip.decompress(z);assert len(z)==pin['stored_bytes'] and sha(z)==pin['stored_sha256'] and len(r)==pin['original_bytes'] and sha(r)==pin['original_sha256']
        if pin['original_path'].endswith('.json'):docs[pin['original_path'].split('/')[-1]]=json.loads(r)
    units={};admins={};source_hashes={}
    for name in ['coahoma-2020-amendment-readings.json','native-2020-additional-readings.json']:
        for s in docs[name]['sources']:
            sid=s['source_id'];assert sha(original(sid))==s['raw_sha256'];source_hashes[sid]=s['raw_sha256']
            for pg in s['pages']:
                fields={f['candidate']:f['values'] for f in pg['fields']}
                for i,c in enumerate(pg['columns']):
                    if c['role'] not in ['source_native_reporting_constituent','source_administrative_reporting_column']:continue
                    key=f'{s["county_fips"]}:{sid}:p{pg["page"]}:c{c["source_column"]}';assert key not in units and key not in admins
                    row=dict(key=key,fips=s['county_fips'],sid=sid,page=pg['page'],column=c['source_column'],label=c['label_literal'],A=fields['Mike Espy'][i],B=fields['Cindy Hyde-Smith'][i],other=fields['Jimmy L. Edwards'][i],role=c['role']);row['pair']=row['A']+row['B'];(units if c['role']=='source_native_reporting_constituent' else admins)[key]=row
    assert len(units)==2131 and len(admins)==1 and len(source_hashes)==104
    cc={r['fips']:r for r in csv.DictReader((BASE/'data/county-baselines.csv').open())};states={r['group']:r for r in csv.DictReader((OUT/'native-2020-state-targets.csv').open())};assert len(states)==134
    partitions={p['partition']:p for p in settings['partitions']};expected={k:{u['key']:u for u in units.values() if u['sid'] in p['source_ids']} for k,p in partitions.items()};assert len(expected)==23
    parents={}
    for name,uu in expected.items():
        pp=defaultdict(lambda:dict(pair=0,other=0))
        for u in uu.values():pp[u['fips']]['pair']+=u['pair'];pp[u['fips']]['other']+=u['other']
        assert set(pp)==set(cc);parents[name]=pp;close(sum(p['pair'] for p in pp.values()),partitions[name]['pair_votes']);assert len(uu)==partitions[name]['native_units']
    accum=defaultdict(lambda:dict(seen=set(),weights=[],shares=[],pair=0.,baseline_net=0.,target_net=0.,gain=0.,clipped=0));countyagg=defaultdict(lambda:dict(pair=0.,baseline_net=0.,target_net=0.,net_gain=0.));formula_checks=rows=0;outpins=[]
    for pin in settings['compressed_unit_outputs']:
        path=BASE/pin['path'];z=path.read_bytes();raw=gzip.decompress(z);assert len(z)==pin['bytes']<40000000 and sha(z)==pin['sha256'] and len(raw)==pin['original_csv_bytes'] and sha(raw)==pin['original_csv_sha256'];nrows=0
        for r in csv.DictReader(io.StringIO(raw.decode())):
            group=r['group'];st=states[group];part=r['partition'];assert part==pin['partition']==st['partition'] and r['scenario']==pin['scenario']==st['scenario'];u=expected[part][r['source_key']];agg=accum[group];assert u['key'] not in agg['seen'];agg['seen'].add(u['key']);f=u['fips'];pp=parents[part];scenario=r['scenario'];anchor=r['preference_anchor'];margin=float(r['target_pair_margin_pp'])/100
            assert r['source_raw_sha256']==source_hashes[u['sid']] and r['label_literal']==u['label'] and r['county_fips']==f and int(r['source_page'])==u['page'] and int(r['source_column'])==u['column']
            assert [int(r[k]) for k in ['A','B','other','pair_votes']]==[u[k] for k in ['A','B','other','pair']]
            if scenario.startswith(('high-observed2020-native','observed2020-source-replacement')):cw={f:float(p['pair']) for f,p in pp.items()}
            else:
                field=next(field for prefix,field in [('low-2022-EAC-ballots','eac_2022_F1a'),('base-2024-Senate-county-mix','2024-senate_pair_votes'),('midterm2018-special-county-mix','2018-special_pair_votes'),('midterm2018-runoff-county-mix','2018-runoff_pair_votes')] if scenario.startswith(prefix));cw={f:float(c[field]) for f,c in cc.items()}
                if scenario.endswith('-normalized-to-2020-pair'):scale=1288202/sum(cw.values());cw={f:w*scale for f,w in cw.items()}
            T=sum(cw.values());w=cw[f]*u['pair']/pp[f]['pair'];q0=u['A']/u['pair'] if anchor=='2020-senate' and u['pair'] else .5 if anchor=='2020-senate' else float(cc[f][anchor+'_A_pair_share']);shift=float(st['bounded_shift']);q=clip(q0+shift);old=w*(2*q0-1);new=w*(2*q-1);target=margin*T;fixed=float(st['baseline_net'])-old;req=(w+target-fixed)/(2*w) if w else None
            O=sum(p['other'] for p in pp.values()) if anchor=='2020-senate' else sum(float(c[anchor+'_other']) for c in cc.values())
            for field,value in [('within_parent_historical_pair_weight',u['pair']/pp[f]['pair']),('county_conditional_pair_pool',cw[f]),('expected_pair_votes',w),('state_pair_votes',T),('state_pair_weight',w/T),('baseline_A_share',q0),('baseline_net',old),('target_A_share',q),('target_net',new),('net_gain',new-old),('net_gain_for_one_A_share_pp',.02*w),('state_target_net',target),('selected_only_fixed_other_net',fixed),('conditional_state_named_all_candidate_denominator',T+O)]:close(r[field],value);formula_checks+=1
            close(float(r['uniform_bounded_share_shift_pp'])/100,shift,1e-12);close(float(r['uniform_unbounded_share_shift_pp'])/100,float(st['unbounded_shift']),1e-12)
            if w:
                close(r['selected_only_required_A_share'],req);close(r['selected_only_required_shift_pp'],100*(req-q0));close(r['selected_only_clipped_display_share'],clip(req));close(fixed+w*(2*req-1),target);assert r['selected_only_status']==('impossible' if req>1 else 'already_above_target_at_zero_share' if req<0 else 'feasible')
            else:assert r['selected_only_status']=='no_positive_pool' and r['selected_only_required_A_share']==r['selected_only_clipped_display_share']==''
            agg['weights'].append(w);agg['shares'].append(q0);agg['pair']+=w;agg['baseline_net']+=old;agg['target_net']+=new;agg['gain']+=new-old;agg['clipped']+=q0+shift<0 or q0+shift>1;c=countyagg[(group,f)];c['pair']+=w;c['baseline_net']+=old;c['target_net']+=new;c['net_gain']+=new-old;rows+=1;nrows+=1
        assert nrows==pin['rows'];outpins.append(dict(path=pin['path'],bytes=len(z),sha256=sha(z),rows=nrows))
    max_shift_error=max_net_error=0.
    for group,agg in accum.items():
        st=states[group];assert agg['seen']==set(expected[st['partition']]);assert len(agg['seen'])==int(st['native_units']);close(agg['pair'],st['pair_votes']);close(agg['baseline_net'],st['baseline_net']);close(agg['target_net'],st['target_net']);close(agg['target_net'],st['achieved_net']);assert agg['clipped']==int(st['clipped_units']);close(agg['gain'],float(st['target_net'])-float(st['baseline_net']));delta=piecewise(agg['weights'],agg['shares'],float(st['target_net']));max_shift_error=max(max_shift_error,abs(delta-float(st['bounded_shift'])));assert abs(delta-float(st['bounded_shift']))<1e-10;max_net_error=max(max_net_error,abs(agg['target_net']-float(st['target_net'])));close(float(st['unbounded_shift']),(float(st['target_net'])-agg['baseline_net'])/(2*agg['pair']),1e-12)
    assert len(accum)==len(states)==settings['state_groups']==134 and rows==settings['unit_target_rows']==236510
    cr=list(csv.DictReader((OUT/'native-2020-county-contributions.csv').open()));assert len(cr)==10988 and len({(r['group'],r['county_fips']) for r in cr})==10988
    for r in cr:
        for k in ['pair','baseline_net','target_net','net_gain']:close(r[k],countyagg[(r['group'],r['county_fips'])][k])
    ll=list(csv.DictReader((OUT/'native-2020-local-targets.csv').open()));assert len(ll)==4264;seen=set()
    for r in ll:
        key=r['source_key'];margin=float(r['target_pair_margin_pp'])/100;assert (key,margin) not in seen;seen.add((key,margin));u=(units|admins)[key];n=u['pair'];assert r['role']==u['role'] and r['label_literal']==u['label'] and [int(r[k]) for k in ['A','B','other']]==[u[k] for k in ['A','B','other']]
        if n:
            q0=u['A']/n;close(r['local_target_A_share'],(1+margin)/2);close(r['local_share_shift_pp'],100*((u['B']-u['A'])/(2*n)+margin/2));close(r['local_net_gain'],margin*n-(u['A']-u['B']));close(r['local_strict_named_plurality_requires_A_pair_share_greater_than'],max(.5,u['other']/n))
        else:assert r['local_status']=='no_positive_pool' and r['local_target_A_share']==r['local_share_shift_pp']==''
    save(OUT/'native-2020-target-validation.json',dict(status='pass_independent_piecewise_and_source_formula_audit',settings=dict(path=str(settings_path.relative_to(BASE)),bytes=settings_path.stat().st_size,sha256=sha(settings_path.read_bytes())),source_publications=104,source_native_observations=2131,preferred_native_units=1765,state_partitions=23,state_groups=134,unit_target_rows=rows,county_contribution_rows=len(cr),source_local_target_rows=len(ll),formula_checks=formula_checks,max_independent_piecewise_shift_error=max_shift_error,max_achieved_net_error=max_net_error,all82_counties_in_every_state=True,all_nonpriority_native_units_retained=True,compressed_outputs=outpins,qualification='Independent clipping-breakpoint slope integration, not imported bisection. Actual source2020native partitions retained; other-year county mixes/preferences conditional, no native identity/candidate-effect/2026projection inferred. Arithmetic does not establish legal outcome/current geography or full vendor-method acceptance.',complete_historical_method_question=False,current2026_geography_approved=False));print('PASS2020native134state/236510unit/10988county/4264local',formula_checks,'formulas; piecewise shift error',max_shift_error,'net error',max_net_error)

if __name__=='__main__':main()

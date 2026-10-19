"""Independent frozen-source/formula and clipping-breakpoint2018target audit.
Does not import the2018calculator or its bisection solver.
"""
import csv,gzip,io,json
from collections import defaultdict,Counter
from sources import OUT,BASE,sha,save
from validate_historical_native_calculator import piecewise,close,clip

def main():
    settingpath=OUT/'native-2018-calculator-settings.json';settings=json.loads(settingpath.read_text());pin=settings['input_witness'];sp=BASE/pin['path'];assert sp.stat().st_size==pin['bytes'] and sha(sp.read_bytes())==pin['sha256'];snap=json.loads(sp.read_text());bodies={}
    for p in snap['pins']:
        z=(BASE/p['stored_path']).read_bytes();r=gzip.decompress(z);assert len(z)==p['stored_bytes']<40000000 and sha(z)==p['stored_sha256'] and len(r)==p['original_bytes'] and sha(r)==p['original_sha256'];bodies[p['original_path'].split('/')[-1]]=json.loads(r) if p['original_path'].endswith('.json') else r
    ledger=bodies['native-2018-original-readings.json'];flat=list(csv.DictReader(io.StringIO(bodies['native-2018-original-candidate-votes.csv'].decode())));fips={r['source_id']:r['county_fips'] for r in flat};units={};admins={};parents={st:defaultdict(lambda:dict(pair=0,outsiders=Counter())) for st in ['special','runoff']}
    for s in ledger['sources']:
        sid=s['source_id'];st=s['stage']
        for p in s['pages']:
            ff={f['candidate']:f for f in p['fields']}
            for i,c in enumerate(p['columns']):
                if c['role'] not in ['native','administrative']:continue
                vals={n:f['values'][i] for n,f in ff.items()};a,b=vals['Mike Espy'],vals['Cindy Hyde-Smith'];unknown=any(v is None for v in vals.values());other={n:v for n,v in vals.items() if n not in ['Mike Espy','Cindy Hyde-Smith']};key=f'{fips[sid]}:{sid}:p{p["page"]}:c{c["source_column"]}';assert key not in units and key not in admins
                marks={n:f.get('source_marks',{}).get(str(i+1)) for n,f in ff.items()};assert not unknown or set(marks.values())=={'X'}
                row=dict(key=key,sid=sid,fips=fips[sid],stage=st,page=p['page'],col=c['source_column'],label=c['label_literal'],role=c['role'],hash=s['raw_sha256'],A=a,B=b,outsiders=other,pair=None if unknown else a+b,named=None if unknown else sum(vals.values()),unknown=unknown,vals=vals,marks=marks);(units if c['role']=='native' else admins)[key]=row
                if c['role']=='native' and not unknown:parents[st][fips[sid]]['pair']+=a+b;parents[st][fips[sid]]['outsiders'].update(other)
    assert len(units)==3545 and len(admins)==3 and len(ledger['sources'])==164
    cc={r['fips']:r for r in csv.DictReader((BASE/'data/county-baselines.csv').open())};states={r['group']:r for r in csv.DictReader((OUT/'native-2018-state-targets.csv').open())};assert len(states)==180
    accum=defaultdict(lambda:dict(seen=set(),weights=[],qs=[],pair=0.,old=0.,new=0.,gain=0.,clipped=0,unknown=0));counties=defaultdict(lambda:dict(pair=0.,baseline_net=0.,target_net=0.,net_gain=0.));rows=checks=0
    for pin in settings['compressed_unit_outputs']:
        z=(BASE/pin['path']).read_bytes();raw=gzip.decompress(z);assert len(z)==pin['bytes']<40000000 and sha(z)==pin['sha256'] and len(raw)==pin['original_csv_bytes'] and sha(raw)==pin['original_csv_sha256'];nrows=0
        for r in csv.DictReader(io.StringIO(raw.decode())):
            u=units[r['source_key']];group=r['group'];st=states[group];stage=r['stage'];assert stage==u['stage']==pin['stage']==st['stage'] and r['scenario']==pin['scenario'];a=accum[group];assert u['key'] not in a['seen'];a['seen'].add(u['key']);nrows+=1;rows+=1
            assert r['source_raw_sha256']==u['hash'] and r['county_fips']==u['fips'] and r['label_literal']==u['label'] and int(r['source_page'])==u['page'] and int(r['source_column'])==u['col'] and json.loads(r['source_named_candidates'])==u['vals'] and json.loads(r['source_named_outsiders'])==u['outsiders'] and json.loads(r['source_marks'])==u['marks']
            if u['unknown']:
                assert r['model_status']=='unknown_source_mark_unmodeled' and r['selected_only_status']=='unknown_source_mark' and all(r[k]=='' for k in ['A','B','pair_votes','named_candidate_votes','expected_pair_votes','state_pair_weight','baseline_A_share','baseline_net','target_A_share','target_net','net_gain','selected_only_fixed_other_net','selected_only_required_A_share']);a['unknown']+=1;continue
            pp=parents[stage];name=r['scenario'];anchor=r['preference_anchor'];margin=float(r['target_pair_margin_pp'])/100
            if name=='observed2018-'+stage:cw={f:float(p['pair']) for f,p in pp.items()}
            else:
                field=next(field for prefix,field in [('low-2022-EAC-ballots','eac_2022_F1a'),('base-2024-Senate-county-mix','2024-senate_pair_votes'),('high-2020-Senate-county-mix','2020-senate_pair_votes'),('other-midterm-stage-county-mix',('2018-runoff' if stage=='special' else '2018-special')+'_pair_votes')] if name.startswith(prefix));cw={f:float(c[field]) for f,c in cc.items()}
                if name.endswith('-normalized-to-stage-pair'):factor=sum(p['pair'] for p in pp.values())/sum(cw.values());cw={f:v*factor for f,v in cw.items()}
            T=sum(cw.values());f=u['fips'];w=cw[f]*u['pair']/pp[f]['pair'];q0=(u['A']/u['pair'] if u['pair'] else .5) if anchor=='2018-'+stage else float(cc[f][anchor+'_A_pair_share']);delta=float(st['bounded_shift']);q=clip(q0+delta);old=w*(2*q0-1);new=w*(2*q-1);target=T*margin;fixed=float(st['baseline_net'])-old;required=(w+target-fixed)/(2*w) if w else None
            O=sum(sum(p['outsiders'].values()) for p in pp.values()) if anchor=='2018-'+stage else sum(int(c[anchor+'_other']) for c in cc.values())
            for field,value in [('within_parent_known_pair_weight',u['pair']/pp[f]['pair']),('county_conditional_pair_pool',cw[f]),('expected_pair_votes',w),('state_pair_votes',T),('state_pair_weight',w/T),('baseline_A_share',q0),('baseline_net',old),('target_A_share',q),('target_net',new),('net_gain',new-old),('net_gain_for_one_A_share_pp',.02*w),('state_target_net',target),('selected_only_fixed_other_net',fixed),('conditional_state_named_denominator',T+O)]:close(r[field],value);checks+=1
            assert r['model_status']=='known_numeric_source';close(float(r['uniform_bounded_share_shift_pp'])/100,delta,1e-12);close(float(r['uniform_unbounded_share_shift_pp'])/100,float(st['unbounded_shift']),1e-12)
            if w:
                close(r['selected_only_required_A_share'],required);close(r['selected_only_required_shift_pp'],100*(required-q0));close(r['selected_only_clipped_display_share'],clip(required));close(fixed+w*(2*required-1),target);assert r['selected_only_status']==('impossible' if required>1 else 'already_above_target_at_zero_share' if required<0 else 'feasible')
            else:assert r['selected_only_status']=='no_positive_pool' and r['selected_only_required_A_share']==''
            a['weights'].append(w);a['qs'].append(q0);a['pair']+=w;a['old']+=old;a['new']+=new;a['gain']+=new-old;a['clipped']+=q0+delta<0 or q0+delta>1;v=counties[group,f];v['pair']+=w;v['baseline_net']+=old;v['target_net']+=new;v['net_gain']+=new-old
        assert nrows==pin['rows']
    maxshift=maxnet=0.
    for group,a in accum.items():
        r=states[group];stage=r['stage'];expected={k for k,u in units.items() if u['stage']==stage};assert a['seen']==expected and len(expected)==int(r['native_observations']);assert a['unknown']==(0 if stage=='special' else 3)==int(r['unknown_source_mark_native']);close(a['pair'],r['pair_votes']);close(a['old'],r['baseline_net']);close(a['new'],r['target_net']);close(a['gain'],float(r['target_net'])-float(r['baseline_net']));assert a['clipped']==int(r['clipped_units']);shift=piecewise(a['weights'],a['qs'],float(r['target_net']));maxshift=max(maxshift,abs(shift-float(r['bounded_shift'])));assert abs(shift-float(r['bounded_shift']))<1e-10;maxnet=max(maxnet,abs(a['new']-float(r['target_net'])));close(float(r['unbounded_shift']),(float(r['target_net'])-a['old'])/(2*a['pair']),1e-12)
        T=a['pair'];other=json.loads(r['named_outsiders_fixed']);O=sum(other.values());D=T+O;close(r['named_other_votes_fixed'],O);close(r['conditional_named_denominator'],D);close(r['target_A_named_share'],(T+float(r['target_net']))/(2*D));close(r['target_A_minus_B_all_named_margin_pp'],100*float(r['target_net'])/D);close(r['majority_cushion_net'],float(r['target_net'])-O);close(r['strict_majority_requires_pair_share_greater_than'],D/(2*T));close(r['strict_named_plurality_requires_pair_share_greater_than'],max(.5,max(other.values(),default=0)/T))
    cr=list(csv.DictReader((OUT/'native-2018-county-contributions.csv').open()));assert len(cr)==14760 and len({(r['group'],r['county_fips']) for r in cr})==len(cr)
    for r in cr:
        for k in ['pair','baseline_net','target_net','net_gain']:close(r[k],counties[r['group'],r['county_fips']][k])
    ll=list(csv.DictReader((OUT/'native-2018-local-targets.csv').open()));assert len(ll)==7096;seen=set();statuses=Counter()
    for r in ll:
        k=r['source_key'];m=float(r['target_pair_margin_pp'])/100;assert (k,m) not in seen;seen.add((k,m));u=(units|admins)[k];n=u['pair'];statuses[r['local_status']]+=1;assert json.loads(r['source_named_candidates'])==u['vals'] and r['label_literal']==u['label'] and r['role']==u['role']
        if n is None:assert r['local_status']=='unknown_source_mark' and r['local_target_A_share']==''
        elif not n:assert r['local_status']=='no_positive_pool' and r['local_target_A_share']==''
        else:
            O=sum(u['outsiders'].values());close(r['local_target_A_share'],(1+m)/2);close(r['local_share_shift_pp'],100*((u['B']-u['A'])/(2*n)+m/2));close(r['local_net_gain'],m*n-u['A']+u['B']);close(r['local_target_all_named_A_minus_B_margin_pp'],100*m*n/(n+O));close(r['local_majority_requires_A_pair_share_greater_than'],(n+O)/(2*n));close(r['local_majority_cushion_net'],m*n-O);close(r['local_strict_named_plurality_requires_A_pair_share_greater_than'],max(.5,max(u['outsiders'].values(),default=0)/n))
    assert rows==settings['unit_target_rows']==319050 and len(accum)==180;assert statuses['unknown_source_mark']==6 and statuses['no_positive_pool']>=6
    save(OUT/'native-2018-target-validation.json',dict(status='pass_independent_source_formula_and_piecewise_clipping_audit',settings=dict(path=str(settingpath.relative_to(BASE)),bytes=settingpath.stat().st_size,sha256=sha(settingpath.read_bytes())),state_groups=180,unit_rows=rows,county_rows=len(cr),local_rows=len(ll),local_status_counts=dict(statuses),formula_checks=checks,max_piecewise_shift_error=maxshift,max_achieved_net_error=maxnet,all82_counties_in_every_state=True,all_nonpriority_units_retained=True,unknown_native_rows_per_runoff_state=3,source_residual_Leflore_special_Espy_unallocated=-10,unknowns_not_zero=True,qualification='Frozen164originalsource fields; independent breakpoint slope integration, not imported author bisection. Eachstage disjoint/all82parents, known-numeric pool explicit, literalXunknowns unmodeled/null, majority/plurality/named-vs-valid denominators distinct. No currentID/geography or2026forecast approval.'))
    print('PASS2018native',len(accum),'state',rows,'unit',len(cr),'county',len(ll),'local',checks,'formulas','maxshift',maxshift,'maxnet',maxnet,'statuses',dict(statuses))
if __name__=='__main__':main()

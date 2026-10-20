#!/usr/bin/env python3
import argparse,csv,gzip,json,math,re
from pathlib import Path
from calculate import strict_json,historical,live
from extract_originals import ROOT,TAGS,originals,sha,dump
STATE=ROOT.parent.parent
def close(a,b):assert math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-7),(a,b)
def owned():return sorted([STATE/'county-partisanship.md',ROOT.parent/'county-baselines.csv']+[p for p in ROOT.rglob('*') if p.is_file()])
def main(sealed=False):
    sources=originals();checks=[];allpositions=0;natives=0
    for tag in TAGS:
        c=strict_json(gzip.decompress((ROOT/'extract'/f'{tag}-original-extraction.json.gz').read_bytes()).decode());m=c['objects']['municipal'];n=c['objects']['precinct'];v=c['controls']['state_values'];w=len(v)
        assert len(m)==351 and len({x['city_town'] for x in m})==351
        assert len({x['key'] for x in n})==len(n)
        for x in n:
            assert json.loads(x['key'])==x['raw_row'][:3] and x['values']==[int(a.replace(',','')) for a in x['raw_row'][3:]]
            assert sum(x['values'][:-1])==x['values'][-1]
            assert all(x[k] is None for k in ['method','registration','undervotes','overvotes','numeric_unit_id'])
        for x in m:
            kids=[k for k in n if k['city_town']==x['city_town']];assert kids
            assert [sum(k['values'][i] for k in kids) for i in range(w)]==x['values']
        assert [sum(x['values'][i] for x in n) for i in range(w)]==v
        assert c['original_rows']['precinct'][-1]==c['original_rows']['municipal'][-1]
        allpositions+=len(c['numeric_positions']);natives+=len(n);checks.append(tag+'_fullfield_native_parent_state_balance')
        for scope in ['municipal','precinct']:
            obs=c['objects'][scope]
            for basis in ['named_pair','all_named','reported_generic','ballots']:
                def votes(x):
                    q=x['values'];return sum(q[:2]) if basis=='named_pair' else sum(q[:-3]) if basis=='all_named' else sum(q[:-2]) if basis=='reported_generic' else q[-1]
                expected=sorted(obs,key=lambda x:(-votes(x),x['city_town'],x['ward'],x['pct'],x['record_ordinal']))
                rows=list(csv.DictReader((ROOT/'orders'/f'{tag}-{scope}-{basis}.csv').open()));assert len(rows)==len(expected)
                total=sum(votes(x) for x in obs);cum=0;chosen=0
                for i,(a,b) in enumerate(zip(rows,expected),1):
                    before=cum;cum+=votes(b);assert a['source_unit_key']==b['key'] and int(a['votes'])==votes(b) and int(a['rank'])==i and int(a['cumulative'])==cum and int(a['total'])==total
                    assert (a['minimum80_member']=='True')==(5*before<4*total)
                    chosen+=(a['minimum80_member']=='True')
                assert 5*int(rows[chosen-2]['cumulative'])<4*total<=5*int(rows[chosen-1]['cumulative'])
    assert natives==9351 and allpositions==75566
    base=list(csv.DictReader((ROOT.parent/'county-baselines.csv').open()));assert len(base)==9351
    assert len({(r['contest'],r['scope'],r['source_unit_key']) for r in base})==9351
    for tag in TAGS:
        subset=[r for r in base if r['contest']==tag];close(sum(float(r['pair_weight']) for r in subset),1)
        for r in subset:
            P=int(r['pair_total']);assert P==int(r['A_votes'])+int(r['B_votes'])
            if P:close(float(r['A_pair_share']),int(r['A_votes'])/P)
            else:assert r['A_pair_share']=='' and r['pair_margin']==''
            vals=json.loads(r['candidate_values_json']);assert sum(vals.values())==int(r['named_candidate_total'])
            assert sum(vals.values())+int(r['All_Others'])==int(r['reported_generic_total'])
            assert int(r['reported_generic_total'])+int(r['Blanks'])==int(r['Total_Votes_Cast'])
            if int(r['reported_generic_total']):close(float(r['pair_participation_reported']),P/int(r['reported_generic_total']))
            else:assert r['pair_participation_reported']==''
            if int(r['Total_Votes_Cast']):close(float(r['pair_participation_ballots']),P/int(r['Total_Votes_Cast']))
            else:assert r['pair_participation_ballots']==''
    settings=strict_json((ROOT/'scenarios/settings.json').read_text());states=list(csv.DictReader((ROOT/'scenarios/state-targets.csv').open()));assert len(settings)==18 and len(states)==36
    unitrows=0
    for s in settings:
        config=strict_json(gzip.decompress((ROOT/s['input_file']).read_bytes()).decode());units=config['units'];assert len(units)==s['units'];close(sum(x['T'] for x in units),s['pair_volume'])
        for target,label in [(0,'tie'),(.01,'Aplus1')]:
            result=historical(units,target);rows=list(csv.DictReader((ROOT/'scenarios'/f"{s['name']}-{label}.csv").open()));assert len(rows)==len(units);unitrows+=len(rows)
            close(sum(float(r['weight']) for r in rows),1);close(sum(float(r['target_net_votes']) for r in rows),target*s['pair_volume'])
            close(sum(float(r['gain_net_votes']) for r in rows),target*s['pair_volume']-result['baseline_net_votes'])
            for row,u,out in zip(rows,units,result['units']):
                assert row['key']==u['key'] and 0<=float(row['target_share'])<=1
                close(float(row['T']),u['T']);close(float(row['share']),u['share']);close(float(row['target_share']),out['target_share'])
                q=float(row['selected_only_raw_share']) if row['selected_only_raw_share'] else None
                if q is not None:close(u['T']*(2*q-1)+float(row['other_units_fixed_net']),target*s['pair_volume'])
                assert row['selected_only_status']==out['selected_unit_only']['status']
    assert unitrows==36702
    for p in (ROOT/'synthetic').glob('*.input.json'):
        name=p.name[:-11];x=strict_json(p.read_text());saved=strict_json((p.parent/(name+'.output.json')).read_text())
        try:result=live(x) if 'candidates' in x else historical(**x)
        except ValueError as e:result=dict(status='invalid_input',error=str(e))
        assert result==saved,p
    fixture=strict_json((ROOT/'synthetic/validation.json').read_text());assert fixture['status']=='pass' and len(fixture['checks'])==65
    checks+=['32_complete_integer_sorted_orders_minimum80','9351_baseline_denominators_weights_and_fullfield','18settings_36state_36702unit_targets_selected_only_substitution','11_saved_synthetic_outputs_65_checks']
    for witness in ['original-first-freeze.json','statistics-original-first-freeze.json']:
        body=json.loads((ROOT/'source'/witness).read_text());entries=body['assets'] if isinstance(body,dict) else body
        for a in entries:
            p=STATE/a['path'] if witness=='original-first-freeze.json' else ROOT/a['path'];assert p.stat().st_size==a['bytes'] and sha(p.read_bytes())==a['sha256'],p
    checks.append('immutable_pre_peer_hash_witnesses_unchanged')
    for p in owned():
        assert p.stat().st_size<40_000_000,p
        assert '__pycache__' not in p.parts and 'node_modules' not in p.parts
        if p.suffix=='.json':strict_json(p.read_text())
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                if link.startswith(('http:','https:','#')):continue
                target=(p.parent/link.split('#')[0]).resolve()
                # Manifest and validation are generated immediately after first validation.
                if not target.exists() and target in [ROOT/'asset-manifest.json',ROOT/'validation.json']:continue
                assert target.exists(),(p,link)
    checks+=['strict_finite_JSON_no_cache_artifacts_all_objects_below40million','all_local_markdown_links_resolve']
    audit=json.loads((ROOT/'peer-audit/comparison.json').read_text());assert audit['exact_priority_agreement'] and len(audit['complete_orders'])==24
    assert json.loads((ROOT/'peer-audit/statistics-comparison.json').read_text())['status'].startswith('pass')
    checks.append('immutable_actual_peer_complete_field_order_native80_and_state_statistics_agree')
    stats=json.loads((ROOT/'statistics-controls.json').read_text());assert stats['registration2024_municipal_coverage']==347 and len(stats['registration2024_county_controls'])==14
    for r in stats['registration2024_county_minus_municipal_disagreements']:assert len(r['sum_minus_county'])==5
    assert stats['source_disagreements']['2020-senate']['PD43_minus_turnout']==33 and stats['source_disagreements']['2024-senate']['PD43_minus_method']==64
    checks.append('registration347_original_access_gaps_and_unallocated_source_disagreements_preserved')
    out=dict(status='pass_qualified_historical_research_and_conditional_arithmetic',native_contest_records=natives,municipal_records=1404,numeric_positions=allpositions,full_orders=32,settings=18,state_targets=36,unit_target_rows=unitrows,saved_synthetic_scenarios=11,calculator_checks=65,checks=checks,asset_integrity={'command':'python validate.py --sealed','rule':'Every owned file except asset-manifest.json is included; validation and final seal included; no reverse manifest digest/cycle'},qualifications=['AllOthers eligible/named allocation unknown','Registration/method original bytes403; supplementary347row browser representation unallocated','2022HTML county conflict,2020+33 and2024method+64 remain','No current geometry/live collector/cadence/ballot-ID approval or calibrated probability','Coordinator final acceptance remains separate'])
    if (ROOT/'validation.json').exists():assert strict_json((ROOT/'validation.json').read_text())==out,'Validation content changed; review explicitly before replacing'
    else:dump(ROOT/'validation.json',out)
    if sealed:
        manifest=strict_json((ROOT/'asset-manifest.json').read_text());actual={str(p.relative_to(STATE)) for p in owned() if p!=ROOT/'asset-manifest.json'};declared={a['path'] for a in manifest['owned_assets']};assert actual==declared,(actual-declared,declared-actual)
        for a in manifest['owned_assets']:
            p=STATE/a['path'];assert p.stat().st_size==a['bytes'] and sha(p.read_bytes())==a['sha256'],p
        for a in manifest['reused_readonly_inputs']:
            p=STATE/a['path'];assert p.stat().st_size==a['bytes'] and sha(p.read_bytes())==a['sha256'],p
        seal=strict_json((ROOT/'final-seal.json').read_text())
        for a in seal['pinned_completed_outputs']:
            p=STATE/a['path'];assert p.stat().st_size==a['bytes'] and sha(p.read_bytes())==a['sha256'],p
        assert 'asset-manifest.json' not in json.dumps(seal), 'No reverse manifest pin allowed'
        print('PASS sealed asset coverage:',len(declared),'owned files; every hash/size checked; only manifest self excluded')
    print('PASS dataset:',natives,'native rows;',allpositions,'positions;',unitrows,'target rows;65 calculator checks')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--sealed',action='store_true');main(ap.parse_args().sealed)

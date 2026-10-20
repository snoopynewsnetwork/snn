"""Independent original-weight and saturation-breakpoint scenario review.

No producer extraction, calculator or solver imports. --output permits a
temporary pre-handoff review; the default is a final coordinator proof.
"""
from collections import defaultdict
from pathlib import Path
import argparse
import csv
import gzip
import hashlib
import io
import json
import math

D = Path(__file__).resolve().parent
B = D / 'baselines'
checks = 0


def near(actual, expected, tolerance=3e-6):
    global checks
    a, b = float(actual), float(expected)
    assert math.isfinite(a) and math.isfinite(b) and abs(a-b) <= tolerance, (a,b)
    checks += 1


def rows(p):
    b = p.read_bytes()
    if p.suffix == '.gz':
        b = gzip.decompress(b)
    return list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(D.parent)), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def clipped(s):
    return min(1.,max(0.,s))


def integrate_breakpoints(units, goal_A):
    events = defaultdict(float)
    for t,s in units:
        if t > 0:
            events[-s] += t
            events[1-s] -= t
    value = slope = 0.
    previous = min(events)
    for edge in sorted(events):
        following = value+slope*(edge-previous)
        if slope > 0 and value-1e-6 <= goal_A <= following+1e-6:
            return previous+(goal_A-value)/slope
        value = following
        slope += events[edge]
        previous = edge
    raise AssertionError(('no feasible saturation interval',goal_A,value))


def main(output):
    global checks
    counties = json.loads((D/'coordinator-county-original-review.json').read_bytes())['county_objects']
    native = json.loads((D/'coordinator-printed-native-priority-review.json').read_bytes())['all_source_groups']
    pairs = {'2020':('RICHARD J. DURBIN','MARK C. CURRAN JR.'),
             '2022':('TAMMY DUCKWORTH','KATHY SALVI'),
             '2024':('Kamala D. Harris','Donald J. Trump')}
    source = {}
    totals = defaultdict(lambda:defaultdict(int))
    other_choices = defaultdict(lambda:defaultdict(int))
    for r in counties:
        y,key = r['year'],r['county_key']
        values = {c['candidate']:c['votes'] for c in r['candidates']}
        A,Bb = pairs[y]
        source[(y,key)] = dict(A=values[A],B=values[Bb],T=values[A]+values[Bb],N=r['all_named'])
        for k,v in source[(y,key)].items():
            totals[y][k] += v
        for c in r['candidates']:
            if c['candidate'] not in [A,Bb]:
                other_choices[y][(c['candidate'],c['party'])] += c['votes']
    assert len(source)==306
    assert sum(c['printed_candidate_cells']['Kamala D. Harris'] or 0 for c in native)==totals['2024']['A']
    assert sum(c['printed_candidate_cells']['Donald J. Trump'] or 0 for c in native)==totals['2024']['B']
    original_native = {c['unit_key']:c for c in native}
    assert len(original_native)==10062
    states = rows(B/'state-scenarios.csv')
    county_targets = rows(B/'county-target-scenarios.csv.gz')
    native_targets = rows(B/'native-target-scenarios.csv.gz')
    groups = defaultdict(list)
    for row in county_targets+native_targets:
        groups[row['scenario']].append(row)
    assert len(states)==len(groups)==90
    assert len(county_targets)==81*102 and len(native_targets)==9*10062
    max_shift_error = max_net_error = 0.
    seen_scenarios = set()
    for state in states:
        sid = state['scenario']
        assert sid not in seen_scenarios
        seen_scenarios.add(sid)
        targets = groups[sid]
        anchor = {'low':'2022','base':'2024','high':'2020'}[state['volume_setting']]
        V = totals[anchor]['N']
        mix,pref = state['mix_year'],state['preference_year']
        is_native = state['level']=='native_recorded_pair'
        assert state['level'] in ['county','native_recorded_pair']
        expected_keys = set(original_native) if is_native else {k for y,k in source if y==mix}
        actual_keys = {r['unit_key'] if is_native else r['county_key'] for r in targets}
        assert actual_keys == expected_keys and len(targets)==len(expected_keys)==int(state['units'])
        units = []
        for row in targets:
            if is_native:
                c = original_native[row['unit_key']]['printed_candidate_cells']
                A,Bb = c['Kamala D. Harris'],c['Donald J. Trump']
                complete = A is not None and Bb is not None
                t = (A+Bb)*totals[anchor]['T']/totals['2024']['T'] if complete else 0.
                s = A/(A+Bb) if complete and A+Bb>0 else None
                assert (row['A_observed']=='') == (A is None)
                assert (row['B_observed']=='') == (Bb is None)
                if complete:
                    near(row['A_observed'],A,0)
                    near(row['B_observed'],Bb,0)
                near(row['expected_pair_votes'],t)
                near(row['state_all_candidate_denominator'],V,0)
                assert row['all_candidate_native_denominator']=='unavailable_named_writein_allocation'
                n = None
            else:
                base = source[(mix,row['county_key'])]
                preference = source[(pref,row['county_key'])]
                n = V*base['N']/totals[mix]['N']
                t = n*base['T']/base['N']
                s = preference['A']/preference['T']
                near(row['expected_all_candidate_votes'],n)
                near(row['expected_pair_votes'],t)
                near(row['pair_participation'],base['T']/base['N'],1e-13)
                near(row['contest_weight'],n/V,1e-13)
                assert row['preference_A_name']==pairs[pref][0] and row['preference_B_name']==pairs[pref][1]
            assert (row['baseline_A_pair_share']=='') == (s is None)
            if s is not None:
                near(row['baseline_A_pair_share'],s,1e-13)
            units.append((row,t,s,n))
        T = math.fsum(u[1] for u in units)
        M = math.fsum(t*(2*s-1) for _,t,s,_ in units if t>0)
        g = {'tie':0.,'pair_A_plus1':.01,'all_candidate_A_plus1':.01*V/T}[state['target']]
        own_shift = integrate_breakpoints([(t,s) for _,t,s,_ in units if t>0],T*(1+g)/2)
        raw_shift = (g*T-M)/(2*T)
        near(state['all_candidate_denominator'],V)
        near(state['pair_denominator'],T)
        near(state['other_votes'],V-T)
        near(state['baseline_net'],M)
        near(state['shift'],own_shift,2e-12)
        near(state['unbounded_shift'],raw_shift,2e-12)
        near(state['target_margin'],g,1e-13)
        max_shift_error = max(max_shift_error,abs(float(state['shift'])-own_shift))
        achieved = []
        for row,t,s,n in units:
            baseline = t*(2*s-1) if t>0 else 0.
            near(row['pair_weight'],t/T,1e-13)
            near(row['baseline_pair_net'],baseline)
            near(row['plus1_share_pp_net_gain'],.02*t)
            q = clipped(s+own_shift) if s is not None else None
            target = t*(2*q-1) if q is not None else 0.
            achieved.append(target)
            near(row['target_pair_net'],target)
            near(row['net_gain'],target-baseline)
            assert (row['target_A_pair_share']=='') == (q is None)
            if q is not None:
                near(row['target_A_pair_share'],q,2e-12)
                near(row['target_pair_margin_pp'],100*(2*q-1))
            share_col = 'selected_only_required_A_share'
            if t>0:
                selected = (t+g*T-(M-baseline))/(2*t)
                near(row[share_col],selected,3e-8)
                expected_status='already_secured' if selected<0 else 'impossible' if selected>1 else 'feasible'
                assert row['selected_only_status']==expected_status
            else:
                assert row[share_col]=='' and row['selected_only_status'].startswith('no_positive_pool')
            if is_native:
                if q is not None:
                    near(row['required_share_change_pp'],100*(q-s))
            else:
                near(row['baseline_pair_margin_pp'],100*(2*s-1))
                near(row['required_A_share_shift_pp'],100*(q-s))
                near(row['target_all_candidate_margin_pp'],100*target/n)
                near(row['selected_only_bounded_share'],clipped(selected))
        achieved_net = math.fsum(achieved)
        near(achieved_net,g*T)
        near(state['achieved_net'],achieved_net)
        near(state['achieved_pair_margin_pp'],100*achieved_net/T)
        near(state['achieved_all_candidate_margin_pp'],100*achieved_net/V)
        near(state['final_A'],(T+achieved_net)/2)
        max_net_error=max(max_net_error,abs(achieved_net-g*T))
        other_year = anchor if is_native else mix
        other_factor = 1 if is_native else V/totals[mix]['N']
        other = json.loads(state['other_candidate_assumptions'])
        observed={(c['candidate_literal'],c['party_literal']):float(c['votes'] if is_native else c['expected_votes']) for c in other}
        assert set(observed)==set(other_choices[other_year])
        for key,count in other_choices[other_year].items():
            near(observed[key],count*other_factor)
        near(state['largest_named_other'],max(observed.values(),default=0))
    # The nine separate disjoint-authority variants aggregate the same original
    # recorded pair cells, never the overlapping county selector products.
    authority_cells=defaultdict(lambda:dict(A=0,B=0))
    for c in native:
        authority_cells[c['authority_ID']]['A']+=c['printed_candidate_cells']['Kamala D. Harris'] or 0
        authority_cells[c['authority_ID']]['B']+=c['printed_candidate_cells']['Donald J. Trump'] or 0
    assert len(authority_cells)==108
    authority_states=json.loads((B/'authority-state-scenarios.json').read_bytes())
    authority_targets=rows(B/'authority-target-scenarios.csv')
    authority_groups=defaultdict(list)
    for r in authority_targets:
        authority_groups[r['scenario']].append(r)
    assert len(authority_states)==len(authority_groups)==9 and len(authority_targets)==972
    for state in authority_states:
        y={'low':'2022','base':'2024','high':'2020'}[state['volume']]
        T,V=totals[y]['T'],totals[y]['N']
        rs=authority_groups[state['scenario']]
        assert {r['JurisdictionID'] for r in rs}==set(authority_cells) and len(rs)==108
        units=[]
        for r in rs:
            c=authority_cells[r['JurisdictionID']]
            t=(c['A']+c['B'])*T/totals['2024']['T']
            s=c['A']/(c['A']+c['B'])
            near(r['A'],c['A'],0);near(r['B'],c['B'],0)
            near(r['expected_pair_votes'],t);near(r['baseline_A_pair_share'],s,1e-13)
            assert r['all_named_authority_denominator']=='unavailable'
            assert r['method']=='unavailable_no_source_column' and r['current_identity']=='unverified'
            units.append((r,t,s))
        M=math.fsum(t*(2*s-1) for _,t,s in units)
        g={'tie':0.,'pair_A_plus1':.01,'all_candidate_A_plus1':.01*V/T}[state['target']]
        d=integrate_breakpoints([(t,s) for _,t,s in units],T*(1+g)/2)
        near(state['all_candidate_denominator'],V);near(state['pair_denominator'],T)
        near(state['baseline_net'],M);near(state['shift'],d,2e-12)
        near(state['unbounded_shift'],(g*T-M)/(2*T),2e-12)
        achieved=[]
        for r,t,s in units:
            net=t*(2*s-1);q=clipped(s+d);target=t*(2*q-1)
            selected=(t+g*T-(M-net))/(2*t)
            near(r['baseline_net'],net);near(r['pair_weight'],t/T,1e-13)
            near(r['plus1_share_pp_net_gain'],.02*t)
            near(r['target_A_pair_share'],q,2e-12);near(r['target_pair_net'],target)
            near(r['net_gain'],target-net);near(r['shift_share_pp'],100*(q-s))
            near(r['selected_only_required_A_share'],selected,3e-8)
            achieved.append(target)
        total_net=math.fsum(achieved)
        near(total_net,g*T);near(state['achieved_net'],total_net)
        max_shift_error=max(max_shift_error,abs(float(state['shift'])-d))
        max_net_error=max(max_net_error,abs(total_net-g*T))
    out=dict(status='pass_independent_original_weight_and_breakpoint_math',checks=checks,
             complete_state_scenarios=len(states)+len(authority_states),county_unit_target_rows=len(county_targets),
             native_unit_target_rows=len(native_targets),all_counties=102,all_source_native_groups=10062,
             authority_unit_target_rows=len(authority_targets),all_source_authorities=108,
             max_shift_error=max_shift_error,max_net_residual=max_net_error,
             source_reviews=[pin(D/'coordinator-county-original-review.json'),pin(D/'coordinator-printed-native-priority-review.json')],
             exact_producer_inputs=[pin(B/p) for p in ['state-scenarios.csv','county-target-scenarios.csv.gz','native-target-scenarios.csv.gz','scenario-settings.json','authority-state-scenarios.json','authority-target-scenarios.csv']],
             independent_solver='Sorted saturation event integration; no producer bisection or extraction imported.',
             qualification='All nonpriority observations retained. Missing named pools stay null. Scenario pair/full-field denominators are explicit historical assumptions, not eligible native write-in allocation, geography, probability or2026 forecast.')
    p=Path(output) if output else D/'coordinator-first-pair-math-review.json'
    b=json.dumps(out,indent=2,allow_nan=False).encode()+b'\n'
    p.write_bytes(b)
    print(json.dumps(dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),checks=checks,max_net_error=max_net_error)))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output')
    main(parser.parse_args().output)

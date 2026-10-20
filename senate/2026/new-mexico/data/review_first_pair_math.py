"""Independent historical arithmetic with saturation-event integration.

No producer solver import, no protected-cell reconstruction or current forecast.
CLI robustness is a separate actual-execution review, not approved here.
"""
from pathlib import Path
import csv
import hashlib
import json
import math

S = Path(__file__).resolve().parents[1]
B = S / 'data/baselines'
N = 0
SHIFT_ERROR = NET_ERROR = 0.


def ck(v, note=''):
    global N
    assert v, note
    N += 1


def close(a, b, tol=1e-8):
    ck(math.isfinite(a) and math.isfinite(b) and abs(a-b) <= tol, (a, b))


def nullable(text):
    return None if text == '' else float(text)


def read(p):
    return json.loads(p.read_bytes())


def rows(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def clip(v):
    return min(1., max(0., v))


def event_shift(units, target):
    total = math.fsum(w for w, s in units)
    events = {}
    for w, s in units:
        events[-s] = events.get(-s, 0.) + 2*w
        events[1-s] = events.get(1-s, 0.) - 2*w
    points = sorted(events)
    value = -total
    previous = points[0]
    slope = events[previous]
    for point in points[1:]:
        end = value + slope*(point-previous)
        if slope > 0 and value - 1e-9 <= target <= end + 1e-9:
            return previous + (target-value)/slope
        value, previous = end, point
        slope += events[point]
    raise AssertionError(('event target not reached', target, value))


def selected(pool, other_net, target):
    if pool is None or other_net is None:
        return None, None, 'unknown'
    if pool == 0:
        return None, None, 'no_positive_pool'
    q = (pool+target-other_net)/(2*pool)
    return q, (clip(q) if q <= 1 else None), ('already_secured' if q < 0 else 'impossible' if q > 1 else 'feasible')


def main():
    global SHIFT_ERROR, NET_ERROR
    original_path = S / 'data/turnout/original-extract.json'
    e = read(original_path)
    source = {k: {r['native_label']: r for r in v['rows'] if r['level'] == 'County'} for k, v in e.items()}
    county = rows(S / 'data/county-baselines.csv')
    native = rows(B / 'native-baselines.csv')
    ck(len(county) == 132 and len(native) == 8558)
    for r in county:
        raw = source[r['contest']][r['county']]
        vals = [x['value'] for x in raw['fields'][:e[r['contest']]['candidate_count']]]
        ck(int(r['A']) == vals[0] and int(r['B']) == vals[1] and int(r['other']) == sum(vals[2:]))
        close(float(r['pair_votes']), vals[0]+vals[1])
        close(float(r['pair_participation']), (vals[0]+vals[1])/sum(vals))
    source_native = {(tag, r['source_row_1based']): r for tag, v in e.items() for r in v['rows'] if r['level'] == 'Precinct'}
    ck(len(source_native) == len(native))
    for r in native:
        raw = source_native[r['contest'], int(r['source_row'])]
        vals = [x['value'] for x in raw['fields'][:e[r['contest']]['candidate_count']]]
        ck(nullable(r['A']) == vals[0] and nullable(r['B']) == vals[1])
        ck(nullable(r['other']) == (sum(vals[2:]) if None not in vals[2:] else None))
        ck(nullable(r['pair_votes']) == (sum(vals[:2]) if None not in vals[:2] else None))
        ck(json.loads(r['raw_fields_json']) == raw['raw_row'])
    state = read(B / 'state-scenarios.json')
    local = rows(B / 'county-target-scenarios.csv')
    ck(len(state) == 32 and len(local) == 1056)
    groups = {}
    for r in local:
        key = (r['preference_anchor'], r['historical_volume_mix'], float(r['target_pair_margin_pp']))
        groups.setdefault(key, {})
        ck(r['county'] not in groups[key])
        groups[key][r['county']] = r
    for z in state:
        anchor, volume = z['preference_anchor'], z['volume_contest']
        target = z['target_margin_pp']/100
        units = {}
        others = {}
        all_volume = 0
        for name, raw in source[anchor].items():
            vals = [x['value'] for x in raw['fields'][:e[anchor]['candidate_count']]]
            original_total = sum(vals)
            v = source[volume][name]['candidate_votes']
            w, s = v*sum(vals[:2])/original_total, vals[0]/sum(vals[:2])
            units[name] = (w, s, v, sum(vals[:2])/original_total)
            all_volume += v
            for cell in raw['fields'][2:e[anchor]['candidate_count']]:
                others[cell['label']] = others.get(cell['label'], 0.) + v*cell['value']/original_total
        total = math.fsum(u[0] for u in units.values())
        net = math.fsum(w*(2*s-1) for w, s, v, p in units.values())
        d = event_shift([(u[0], u[1]) for u in units.values()], target*total)
        SHIFT_ERROR = max(SHIFT_ERROR, abs(d-z['shift']))
        close(d, z['shift'], 1e-12)
        close(total, z['volume'])
        close(net, z['baseline_net'])
        ck(z['all_candidate_volume'] == all_volume)
        close(z['pair_participation_state'], total/all_volume)
        close(z['unbounded_shift'], (target-net/total)/2)
        close(z['all_candidate_target_margin_pp'], 100*target*total/all_volume)
        ck(set(others) == set(z['other_candidate_expected_votes']))
        for name, expected in others.items():
            close(z['other_candidate_expected_votes'][name], expected)
        table = groups[anchor, z['historical_volume_mix'], z['target_margin_pp']]
        ck(set(table) == set(units) and len(table) == 33)
        achieved = []
        for name, (w, s, v, p) in units.items():
            r = table[name]
            share = clip(s+d)
            n = w*(2*share-1)
            achieved.append(n)
            for key, expected in [('pair_volume', w), ('pair_weight', w/total), ('pair_participation', p), ('baseline_A_pair_share', s), ('target_A_pair_share', share), ('target_net', n), ('net_gain', n-w*(2*s-1)), ('gain_net_per_A_share_pp', .02*w)]:
                close(float(r[key]), expected)
            ck(int(r['all_candidate_volume']) == v)
            q, feasible, status = selected(w, net-w*(2*s-1), target*total)
            close(float(r['selected_only_unbounded_share']), q)
            ck((nullable(r['selected_only_feasible_share']) is None) == (feasible is None))
            if feasible is not None:
                close(float(r['selected_only_feasible_share']), feasible)
            ck(r['selected_only_status'] == status and r['others_share_shift_pp'] == '0')
        final_net = math.fsum(achieved)
        NET_ERROR = max(NET_ERROR, abs(final_net-target*total))
        close(final_net, target*total)
    nstate = read(B / 'native-state-scenarios.json')
    ntarget = rows(B / 'native-targets.csv')
    ck(len(nstate) == 8 and len(ntarget) == 17116)
    nd = {(r['contest'], int(r['source_row'])): r for r in native}
    solutions = {}
    for z in nstate:
        tag = z['contest']
        observed = [r for r in native if r['contest'] == tag and nullable(r['pair_votes']) is not None and float(r['pair_votes']) > 0]
        units = [(float(r['pair_votes']), float(r['A_pair_share'])) for r in observed]
        total = math.fsum(w for w, s in units)
        d = event_shift(units, z['target']*total)
        close(d, z['shift'], 1e-12)
        close(total, z['volume'])
        ck(z['whole_state_native_solution'] is None)
        solutions[tag, z['target']*100] = (d, total)
    ck(len(solutions) == 8)
    for r in ntarget:
        tag = r['contest']
        raw = nd[tag, int(r['source_row'])]
        pool = nullable(raw['pair_votes'])
        d, total = solutions[tag, float(r['target_pair_margin_pp'])]
        ck(r['statewide_all_native_uniform_target_share'] == '')
        if pool is None or pool == 0:
            ck(r['observed_universe_target_share'] == '' and r['observed_universe_target_net'] == '')
        else:
            share = clip(float(raw['A_pair_share'])+d)
            close(float(r['observed_universe_target_share']), share)
            close(float(r['observed_universe_target_net']), pool*(2*share-1))
        st = e[tag]['rows'][0]
        A, BB = [x['value'] for x in st['fields'][:2]]
        target = float(r['target_pair_margin_pp'])/100*(A+BB)
        q, feasible, status = selected(pool, None if pool is None else A-BB-float(raw['net_A_minus_B']), target)
        ck((nullable(r['fullstate_selected_only_unbounded_share']) is None) == (q is None))
        if q is not None:
            close(float(r['fullstate_selected_only_unbounded_share']), q)
        if feasible is not None:
            close(float(r['fullstate_selected_only_feasible_share']), feasible)
        else:
            ck(r['fullstate_selected_only_feasible_share'] == '')
        ck(r['selected_status'] == status)
    out = dict(status='pass_independent_historical_formula_review_CLI_input_repair_separate', checks=N,
               method='Independent saturation-event integration; no author solver import or bisection call',
               state_scenarios=32, county_contribution_selected_rows=1056, native_baseline_rows=8558,
               native_source_known_scenarios=8, native_target_rows=17116,
               source_county_rows=132, maximum_shift_difference=SHIFT_ERROR, maximum_net_residual=NET_ERROR,
               all_unknown_native_targets_remain_unmodeled=True, protected_allocations=False,
               canonical_certified_native_order_min80_unavailable=True,
               source_inputs=[pin(original_path), pin(S/'data/county-baselines.csv'), pin(B/'settings.json')],
               output_pins=[pin(B/n) for n in ['state-scenarios.json', 'county-target-scenarios.csv', 'native-baselines.csv', 'native-state-scenarios.json', 'native-targets.csv']],
               CLI_robustness_not_approved='Actual separate input review found11failures; same-worker repair pending real slot. Historical arithmetic equality does not approve malformed input handling or current/legal/feed/geography/probability.')
    p = S / 'data/coordinator-first-pair-math-review.json'
    p.write_text(json.dumps(out, indent=2)+'\n')
    print(dict(checks=N, proof=pin(p), maximum_shift_difference=SHIFT_ERROR, maximum_net_residual=NET_ERROR))


if __name__ == '__main__':
    main()

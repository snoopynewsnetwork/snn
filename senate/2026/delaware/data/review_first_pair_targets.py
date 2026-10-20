"""Independent coordinator source/weight and saturation-breakpoint target audit.

No question-worker extraction, solver or calculator module is imported.
Run after final producer handoff; writes only the coordinator proof.
"""
from pathlib import Path
from collections import defaultdict
import csv
import hashlib
import json
import math
import argparse

D = Path(__file__).resolve().parent
B = D / 'baselines'
checks = 0


def near(a, b, tolerance=2e-7):
    global checks
    assert math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tolerance, (a, b)
    checks += 1


def num(v):
    return None if v == '' else float(v)


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(D.parent)), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def rows(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))


def clipped(v):
    return min(1, max(0, v))


def breakpoint(weights, shares, goal):
    positive = [(t, s) for t, s in zip(weights, shares) if t > 0]
    events = defaultdict(float)
    for t, s in positive:
        events[-s] += t
        events[1 - s] -= t
    points = sorted(events)
    value = slope = 0.0
    at = points[0]
    for edge in points:
        following = value + slope * (edge - at)
        if slope > 0 and value - 1e-8 <= goal <= following + 1e-8:
            return at + (goal - value) / slope
        value = following
        slope += events[edge]
        at = edge
    raise AssertionError(('no feasible breakpoint interval', goal, value))


def main(output_path=None):
    global checks
    base = rows(B / 'native-baselines.csv')
    states = rows(B / 'state-scenarios.csv')
    targets = rows(B / 'unit-targets.csv')
    originals = json.loads((D / 'coordinator-native-original-review.json').read_bytes())['contexts']
    scope = {(2024, 'USSenator'): '2024_SEN', (2024, 'PresidentandVicePresident'): '2024_PRES',
             (2020, 'USSenator'): '2020_SEN', (2020, 'PresidentandVicePresident'): '2020_PRES',
             (2022, 'RepresentativeinCongress'): '2022_HOUSE'}
    lookup = {(int(r['year']), r['office_key'], r['view'], r['geo_key']): r for r in base}
    assert len(lookup) == len(base)
    for (year, office), key in scope.items():
        native = {u['source_key']: u for u in originals[key]['full_native_units']}
        selected = [r for r in base if int(r['year']) == year and r['office_key'] == office and r['view'] == 'byelectiondist']
        assert set(native) == {r['geo_key'] for r in selected}
        for r in selected:
            u = native[r['geo_key']]
            source = {x['candidate']: x for x in u['rows']}
            near(float(r['A']), source[r['A_candidate']]['methods']['Total Votes'], 0)
            near(float(r['B']), source[r['B_candidate']]['methods']['Total Votes'], 0)
            near(float(r['named_total']), u['votes'], 0)
    groups = defaultdict(list)
    for r in targets:
        groups[(r['scenario'], r['target_pair_margin'])].append(r)
    assert len(groups) == len(states) == 80
    settings = {r['scenario']: r for r in json.loads((B / 'scenario-settings.json').read_bytes())}
    county = {(int(r['year']), r['office_key'], r['geo_key']): r for r in base if r['view'] == 'bycounty'}
    scale_anchor = {'low': (2022, 'RepresentativeinCongress'), 'base': (2024, 'USSenator'), 'high': (2024, 'PresidentandVicePresident')}
    maximum_shift_difference = maximum_net_residual = 0.0
    for state in states:
        sid, g = state['scenario'], float(state['target_pair_margin'])
        rs = groups[(sid, state['target_pair_margin'])]
        assert len(rs) == int(state['units'])
        weights, shares, volumes = [], [], []
        for r in rs:
            original = lookup[(int(r['year']), r['office_key'], r['view'], r['geo_key'])]
            if sid in settings:
                setting = settings[sid]
                vy, vo = setting['volume_anchor'].split(' ', 1)
                py, po = setting['preference_anchor'].split(' ', 1)
                vol = float(county[(int(vy), vo, r['geo_key'])]['named_total'])
                primary = county[(2024, 'USSenator', r['geo_key'])]
                weight = vol * float(primary['pair_total']) / float(primary['named_total'])
                pref = county[(int(py), po, r['geo_key'])]
                share = float(pref['A']) / float(pref['pair_total'])
            elif sid.startswith('native-') and sid.endswith('-historical-volume-scale'):
                anchor = scale_anchor[sid.split('-')[1]]
                total = sum(float(v['named_total']) for k, v in county.items() if k[:2] == anchor)
                factor = total / originals['2024_SEN']['named_source_total']
                vol = float(original['named_total']) * factor
                weight = float(original['pair_total']) * factor
                share = None if weight == 0 else float(original['A']) / float(original['pair_total'])
            else:
                assert sid.endswith('-historical')
                vol = float(original['named_total'])
                weight = float(original['pair_total'])
                share = None if weight == 0 else float(original['A']) / weight
            near(float(r['scenario_named_volume']), vol)
            near(float(r['scenario_pair_volume']), weight)
            near(float(r['scenario_named_other']), vol - weight)
            assert (num(r['preference_A_share']) is None) == (share is None)
            if share is not None:
                near(float(r['preference_A_share']), share, 1e-13)
            weights.append(weight)
            shares.append(share)
            volumes.append(vol)
        T = sum(weights)
        V = sum(volumes)
        net = sum(t * (2 * s - 1) for t, s in zip(weights, shares) if t > 0)
        shift = breakpoint(weights, shares, T * (1 + g) / 2)
        raw = (g * T - net) / (2 * T)
        near(float(state['pair_volume']), T)
        near(float(state['named_volume']), V)
        near(float(state['named_other']), V - T)
        near(float(state['baseline_net']), net)
        near(float(state['raw_shift_share_pp']), raw * 100)
        near(float(state['bounded_shift_share_pp']), shift * 100)
        maximum_shift_difference = max(maximum_shift_difference, abs(shift - float(state['bounded_shift_share_pp']) / 100))
        achieved = 0.0
        for r, t, s in zip(rs, weights, shares):
            own = 0 if t == 0 else t * (2 * s - 1)
            fixed = net - own
            near(float(r['baseline_net']), own)
            near(float(r['pair_weight']), t / T)
            near(float(r['selected_other_net_fixed']), fixed)
            if t == 0:
                assert r['target_A_share'] == r['selected_only_required_share'] == ''
                near(float(r['target_net']), 0)
                continue
            q = clipped(s + shift)
            target = t * (2 * q - 1)
            achieved += target
            selected = (t + g * T - fixed) / (2 * t)
            near(float(r['target_A_share']), q, 1e-12)
            near(float(r['target_net']), target)
            near(float(r['net_gain']), target - own)
            near(float(r['share_shift_pp']), 100 * (q - s))
            near(float(r['pair_margin_shift_pp']), 200 * (q - s))
            near(float(r['net_gain_per_1pp_unclipped']), .02 * t)
            near(float(r['net_gain_per_1pp_clipped']), 2 * t * (clipped(s + .01) - s))
            near(float(r['selected_only_required_share']), selected)
            near(float(r['selected_only_clipped_share']), clipped(selected))
        near(achieved, g * T)
        near(float(state['target_net']), achieved)
        near(float(state['target_named_all_candidate_margin_pp']), 100 * achieved / V)
        near(float(state['net_needed_for_1pp_all_candidate_margin']), .01 * V)
        maximum_net_residual = max(maximum_net_residual, abs(achieved - g * T))
    output = dict(status='pass_independent_breakpoint_source_weight_and_target_review', checks=checks,
                  state_scenarios=len(states), complete_unit_targets=len(targets), baseline_units=len(base),
                  original_native_scopes={k: v['native_units'] for k, v in originals.items()},
                  source_original_review=pin(D / 'coordinator-native-original-review.json'),
                  exact_producer_inputs=[pin(B / p) for p in ['native-baselines.csv', 'state-scenarios.csv', 'unit-targets.csv', 'scenario-settings.json']],
                  solver='Independent sorted saturation-breakpoint integration, no producer bisection imported',
                  maximum_shift_difference=maximum_shift_difference, maximum_net_residual=maximum_net_residual,
                  source_county_and_native_volume_mix_and_preference_checked=True,
                  qualifications='Whole-state alternative views remain separate, all nonpriority source units retained. Source unallocated write-ins are not native allocations. Scenario arithmetic is not legal eligibility, current geography, probability or a2026 forecast.')
    p = Path(output_path) if output_path else D / 'coordinator-first-pair-target-review.json'
    b = (json.dumps(output, indent=2) + '\n').encode()
    if p.exists():
        assert p.read_bytes() == b
    else:
        p.write_bytes(b)
    print(json.dumps(dict(path=str(p), bytes=len(b), sha256=hashlib.sha256(b).hexdigest(), checks=checks)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', help='Optional temporary preliminary proof outside sealed producer paths')
    main(parser.parse_args().output)

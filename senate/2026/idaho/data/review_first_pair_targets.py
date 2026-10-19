#!/usr/bin/env python3
"""Producer-independent scenario and fixed-counted arithmetic review.

Reads complete source objects and CSV outputs, never producer Python modules.
The root solver integrates saturation breakpoints rather than using bisection.
"""
from collections import Counter, defaultdict
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import math

D = Path(__file__).resolve().parent
R = D / 'baselines'
PAIRS = {
    '2024-president': ('Kamala D. Harris', 'Donald J. Trump'),
    '2020-senate-II': ('Paulette Jordan', 'Jim Risch'),
    '2020-president': ('Joseph R. Biden', 'Donald J. Trump'),
    '2022-senate-III': ('David Roth', 'Mike Crapo'),
    '2022-governor': ('Stephen Heidt', 'Brad Little'),
    '2020-Fleming-Risch': ('Natalie M Fleming', 'Jim Risch'),
    '2022-Cleveland-Crapo': ('Scott Oh Cleveland', 'Mike Crapo'),
    'current-Achilles-Risch': ('Todd Achilles', 'Jim Risch'),
    'current-Fleming-Risch': ('Natalie M Fleming', 'Jim Risch'),
    'current-Loesby-Risch': ('Matt Loesby', 'Jim Risch'),
}
FILES = ['source/native-units.json.gz', 'source/controls.json.gz',
         'scenario-settings.json', 'state-scenarios.csv', 'unit-targets.csv.gz',
         'live-synthetic-inputs.json', 'live-synthetic-results.json']
BYTES = {n: (R / n).read_bytes() for n in FILES}
checks = Counter()
max_error = defaultdict(float)


def decoded(n):
    b = BYTES[n]
    return gzip.decompress(b) if n.endswith('.gz') else b


def load(n):
    return json.loads(decoded(n))


def table(n):
    return list(csv.DictReader(io.StringIO(decoded(n).decode())))


def check(value, kind, detail=''):
    assert value, (kind, detail)
    checks[kind] += 1


def near(actual, expected, kind, detail='', atol=1e-7):
    if expected is None:
        check(actual in [None, ''], kind, detail)
        return
    error = abs(float(actual) - expected)
    max_error[kind] = max(max_error[kind], error)
    check(math.isfinite(float(actual)) and error <= atol + abs(expected) * 2e-12,
          kind, (detail, actual, expected, error))


def clip(v):
    return max(0., min(1., v))


def county(u):
    return u['county'] if u['county'].endswith(' County') else u['county'] + ' County'


def anchor_contest(pair):
    if pair.startswith('current-'):
        return '2024-president'
    return {'2020-Fleming-Risch': '2020-senate-II',
            '2022-Cleveland-Crapo': '2022-senate-III'}.get(pair, pair)


def source_record(u, pair):
    current = pair.startswith('current-')
    a, b = PAIRS['2024-president' if current else pair]
    fields = {c['name'].strip(): c for c in u['candidates']}
    av, bv = fields[a]['votes'], fields[b]['votes']
    complete = all(c['votes'] is not None for c in u['candidates'])
    known = sum(c['votes'] for c in u['candidates'] if c['votes'] is not None)
    v = known if complete else None
    t = None if av is None or bv is None else av + bv
    s = av / t if t else None
    other = None
    if current:
        other = {name: .5 for name in ['Todd Achilles', 'Natalie M Fleming', 'Matt Loesby']
                 if name != PAIRS[pair][0]}
    elif v is not None and t is not None:
        other = ({c['name']: c['votes'] / (v - t) for c in u['candidates']
                  if c['name'].strip() not in [a, b]} if v > t else {})
    return dict(source=u, t=t, s=s, p=t / v if v and t is not None else None,
                v=v, known=known, other=other)


def independent_root(sim, target):
    total = sum(x['t'] for x in sim)
    events = defaultdict(float)
    for x in sim:
        if x['t']:
            events[-x['s']] += 2 * x['t']
            events[1 - x['s']] -= 2 * x['t']
    previous, value, slope = -1., -total, 0.
    for point in sorted(events):
        next_value = value + slope * (point - previous)
        if slope > 0 and value - 1e-7 <= target <= next_value + 1e-7:
            return previous + (target - value) / slope
        value, previous = next_value, point
        slope += events[point]
    raise AssertionError(('no bounded root', target, total))


def selection_status(q, pool):
    return ('no_positive_pool' if pool <= 0 else
            'already_secured_under_fixed_assumptions' if q < 0 else
            'impossible_under_fixed_assumptions' if q > 1 else 'feasible')


def main():
    units = load('source/native-units.json.gz')
    controls = [u for u in load('source/controls.json.gz') if u['scope'] == 'county']
    check(len(units) == 4931 and len(controls) == 220, 'complete_source_scope')
    check(Counter(u['contest'] for u in units) == Counter({
        '2024-president': 985, '2020-senate-II': 974, '2020-president': 974,
        '2022-senate-III': 999, '2022-governor': 999}), 'separate_native_contests')
    settings = {x['id']: x['volume_contest'] for x in load('scenario-settings.json')['settings']}
    states, targets = table('state-scenarios.csv'), table('unit-targets.csv.gz')
    grouped = defaultdict(list)
    for row in targets:
        grouped[row['scenario']].append(row)
    check(len(states) == 160 and len(targets) == 63518, 'all_scenario_output_rows')
    check(set(grouped) == {s['scenario'] for s in states}, 'complete_state_unit_groups')
    root_differences = []
    for state in states:
        pair, setting, scope = state['pair_id'], state['volume_setting'], state['scope']
        contest = anchor_contest(pair)
        source = [u for u in (units if scope == 'native' else controls) if u['contest'] == contest]
        parents = {county(u): source_record(u, pair) for u in controls if u['contest'] == contest}
        volume_contest = contest if setting == 'anchor_observed_county_repeat' else settings.get(setting)
        volume = {county(u): sum(c['votes'] for c in u['candidates'])
                  for u in controls if u['contest'] == volume_contest}
        sim = []
        for u in source:
            r = source_record(u, pair)
            if setting == 'native_observed_pair_repeat':
                r['volume'] = r['known']
            else:
                parent = parents[county(u)]
                share = 1. if scope == 'county' else r['v'] / parent['v']
                r['volume'] = volume[county(u)] * share
                r['t'] = None if r['p'] is None else r['volume'] * r['p']
            sim.append(r)
        total = sum(r['t'] for r in sim if r['t'] is not None)
        v = sum(r['volume'] for r in sim)
        unknown = any(r['t'] is None or (r['t'] > 0 and r['s'] is None) for r in sim)
        check(state['status'] == ('unknown_preference_or_pair_pool' if unknown else 'feasible'),
              'unknown_pool_status', state['scenario'])
        check(int(state['units']) == len(sim) == len(grouped[state['scenario']]), 'scenario_unit_coverage')
        near(state['all_candidate_volume_basis'], v, 'declared_volume')
        near(state['pair_volume_known_sum'], total, 'declared_pair_volume')
        g = float(state['target_pair_margin_pp']) / 100
        baseline = None if unknown else sum(r['t'] * (2 * r['s'] - 1) for r in sim if r['t'])
        near(state['baseline_net'], baseline, 'source_derived_baseline_net')
        target = g * total
        delta = None if unknown else independent_root(sim, target)
        near(state['bounded_A_share_shift_pp'], None if delta is None else delta * 100,
             'independent_breakpoint_shift', state['scenario'], atol=1e-8)
        if not unknown:
            root_differences.append(abs(delta - float(state['bounded_A_share_shift_pp']) / 100))
            near(state['unbounded_A_share_shift_pp'], 100 * (target - baseline) / (2 * total), 'unbounded_shift')
            near(state['achieved_net'], sum(r['t'] * (2 * clip(r['s'] + delta) - 1)
                                           for r in sim if r['t']), 'achieved_net')
            near(state['target_net'], target, 'target_net')
            check(int(state['clipped_units']) == sum(not 0 <= r['s'] + delta <= 1
                  for r in sim if r['t']), 'clipped_units')
        expected = {r['source']['unit_id']: r for r in sim}
        observed = grouped[state['scenario']]
        check({x['source_unit_id'] for x in observed} == set(expected), 'all_source_units_present')
        for row in observed:
            r = expected[row['source_unit_id']]
            u, t, s = r['source'], r['t'], r['s']
            check(row['literal_unit'] == u['label'] and row['source_row'] == str(u['row'] or ''),
                  'literal_source_positions')
            near(row['valid_volume'], r['volume'], 'unit_volume')
            near(row['pair_volume'], t, 'unit_pair_volume')
            near(row['pair_participation'], r['p'], 'source_pair_participation')
            near(row['baseline_A_share'], s, 'source_preference')
            near(row['pair_weight'], None if not total or t is None else t / total, 'unit_pair_weight')
            near(row['all_candidate_weight'], r['volume'] / v, 'unit_all_weight')
            q = None if delta is None or s is None else clip(s + delta)
            near(row['bounded_target_share'], q, 'bounded_share')
            net = None if q is None else t * (2 * q - 1)
            near(row['target_net'], net, 'unit_net_contribution')
            near(row['net_gain_per_1pp_share'], None if t is None else .02 * t, 'factor_two')
            oldnet = None if t is None or s is None else t * (2 * s - 1)
            near(row['baseline_net'], oldnet, 'unit_baseline_net')
            near(row['net_gain'], None if net is None or oldnet is None else net - oldnet, 'unit_gain')
            if unknown:
                check(row['selected_only_status'] == 'unknown_preference_or_pool', 'selected_unknown')
            elif t <= 0:
                check(row['selected_only_status'] == 'no_positive_pool', 'selected_zero_pool')
            else:
                fixed = baseline - oldnet
                required = (t + target - fixed) / (2 * t)
                near(row['fixed_other_net'], fixed, 'selected_fixed_others')
                near(row['selected_only_required_share'], required, 'selected_conditional_share')
                check(row['selected_only_status'] == selection_status(required, t), 'selected_status')
        if not unknown:
            others = defaultdict(float)
            full = True
            for r in sim:
                if r['other'] is None:
                    full = False
                else:
                    for name, fraction in r['other'].items():
                        others[name] += (r['volume'] - r['t']) * fraction
            observed_others = json.loads(state['other_candidate_totals_json'])
            check(set(others) == set(observed_others), 'other_candidate_identities')
            for name, value in others.items():
                near(observed_others[name], value, 'full_field_other_totals')
            av, bv = (total + target) / 2, (total - target) / 2
            highest_other = max([bv] + list(others.values()))
            status = ('unknown_full_field' if not full else 'strict_plurality' if av > highest_other + 1e-7
                      else 'shared_highest_tie_coin_rule' if abs(av - highest_other) < 1e-7 else 'not_plurality')
            check(state['legal_A_status'] == status, 'full_field_plurality_distinct_from_pair')
    review_live()
    for name, original in BYTES.items():
        check((R / name).read_bytes() == original, 'inputs_unchanged_during_review', name)
    output = dict(status='pass_independent_conditional_arithmetic_review',
                  source_scope='Complete original-derived source objects; original-byte/source-field replay is a separate review.',
                  producer_modules_imported=False, solver='independent saturation breakpoint integration',
                  inputs=[dict(path='data/baselines/' + n, bytes=len(b), sha256=hashlib.sha256(b).hexdigest())
                          for n, b in BYTES.items()],
                  scenarios=len(states), unit_and_selected_targets=len(targets),
                  live_cases=len(load('live-synthetic-inputs.json')),
                  checks=dict(checks), total_checks=sum(checks.values()),
                  maximum_shift_difference=max(root_differences), maximum_errors=dict(max_error),
                  current_geography_approved=False, coordinator_priority_accepted=False,
                  qualification='Arithmetic under explicitly supplied volumes, shares, participation and other-candidate allocations; no probability, current choice certification or measured remainder.')
    p = D / 'coordinator-first-pair-target-review.json'
    p.write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(dict(path=str(p), checks=sum(checks.values()), sha256=hashlib.sha256(p.read_bytes()).hexdigest())))


def review_live():
    cases, outputs = load('live-synthetic-inputs.json'), load('live-synthetic-results.json')
    check(len(cases) == len(outputs) == 14, 'all_live_cases')
    for case, result in zip(cases, outputs):
        counted, a, b = case['counted'], case['A'], case['B']
        check(result['counted_fixed'] == counted and result['probability'] is None, 'counted_fixed_not_probability')
        units = case['remaining_units']
        if any(u['valid_candidate_pool'] is None for u in units):
            check(result['status'] == 'unknown_remaining_pool', 'live_unknown_pool'); continue
        if any(x < 0 for x in counted.values()):
            check(result['status'] == 'invalid_negative_or_nonfinite_counted_votes', 'live_invalid_count'); continue
        if any(u['valid_candidate_pool'] < 0 for u in units):
            check(result['status'] == 'invalid_negative_or_nonfinite_pool', 'live_invalid_pool'); continue
        final = dict(counted)
        rows = []
        for u in units:
            v = u['valid_candidate_pool']; t = v * u['pair_fraction']; q = clip(u['A_share_of_pair'])
            final[a] += t * q; final[b] += t * (1 - q)
            for n, f in u['other_allocation'].items():
                final[n] += (v - t) * f
            rows.append((u['id'], t, q))
        near(result['final_all_candidate_denominator'], sum(final.values()), 'live_all_denominator')
        near(result['final_pair_denominator'], final[a] + final[b], 'live_pair_denominator')
        for name, value in final.items():
            near(result['projected_final'][name], value, 'live_final_candidate')
        chosen = [r for r in rows if r[0] == case['selected_unit']] if case.get('selected_unit') else rows
        pool = sum(r[1] for r in chosen)
        fixed = counted[a] - counted[b] + sum(t * (2 * q - 1) for ident, t, q in rows if (ident, t, q) not in chosen)
        denominator = final[a] + final[b] if case.get('target_denominator', 'pair') == 'pair' else sum(final.values())
        target = case.get('target_margin_pp', 0) * denominator / 100
        out = result['break_even']
        near(out['fixed_A_minus_B'], fixed, 'live_fixed_others')
        near(out['target_net'], target, 'live_target_net')
        if not pool:
            check(out['status'] == 'no_positive_pool', 'live_no_pool'); continue
        required = (pool + target - fixed) / (2 * pool)
        near(out['required_A_share_unbounded'], required, 'live_required_share')
        check(out['status'] == selection_status(required, pool), 'live_required_status')
        fixed_a = counted[a] + sum(t * q for ident, t, q in rows if (ident, t, q) not in chosen)
        legal = max([(pool - fixed) / (2 * pool)] + [(v - fixed_a) / pool for n, v in final.items() if n not in [a, b]])
        near(out['legal_strict_plurality_requires_share_GREATER_THAN'], legal, 'live_full_field_threshold')


if __name__ == '__main__':
    main()

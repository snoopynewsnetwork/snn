#!/usr/bin/env python3
"""Independent source-weighted target arithmetic; no producer imports/solver."""
from collections import Counter, defaultdict
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json

D = Path(__file__).resolve().parent
S = D.parent
B = D / 'baselines'
checks = Counter()
errors = defaultdict(float)
inputs = {}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    b = p.read_bytes()
    inputs[str(p.relative_to(S))] = dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))
    return gzip.decompress(b) if p.suffix == '.gz' else b


def table(p):
    return list(csv.DictReader(io.StringIO(read(p).decode())))


def check(test, kind, detail=''):
    assert test, (kind, detail)
    checks[kind] += 1


def near(actual, expected, kind, detail='', tolerance=1e-7):
    if expected is None:
        check(actual in ['', None], kind, detail)
        return
    error = abs(float(actual) - expected)
    errors[kind] = max(errors[kind], error)
    check(error <= tolerance + abs(expected) * 2e-12, kind, (detail, actual, expected, error))


def clip(x):
    return max(0., min(1., x))


def root(rows, target):
    total = sum(r['weight'] for r in rows)
    changes = defaultdict(float)
    for r in rows:
        if r['weight']:
            changes[-r['share']] += 2 * r['weight']
            changes[1 - r['share']] -= 2 * r['weight']
    x, net, slope = -1., -total, 0.
    for point in sorted(changes):
        next_net = net + slope * (point - x)
        if slope > 0 and net - 1e-7 <= target <= next_net + 1e-7:
            return x + (target - net) / slope
        net, x = next_net, point
        slope += changes[point]
    raise AssertionError(('no feasible root', target, total))


def main():
    proof = json.loads(read(D / 'coordinator-first-pair-source-review.json'))
    original = {}
    for item in proof['complete_originals']:
        receipt = item['receipt']
        if not receipt['id'].endswith('table-csv'):
            continue
        p = S / item['stored_original']['path']
        b = read(p)
        check(sha(b) == receipt['raw_sha256'], 'original_source_hash')
        rawrows = list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
        year = int(receipt['id'].split('-')[3])
        contest = {2024: '26499', 2022: '25990', 2020: '3602'}[year]
        original[year] = dict(county={}, native={})
        county = None
        for fields in rawrows[2:]:
            if fields[0] == 'County':
                county = fields[1]
            if fields[0] not in ['County', 'Precinct']:
                continue
            native = fields[0] == 'Precinct'
            # Baseline county controls retain a final empty native-ID component;
            # turnout controls omit that delimiter. Mapping is source-position
            # scoped and explicit, never a precinct label/current-ID alias.
            key = f'CO|{year}|{contest}|{county}|' + (fields[1] if native else '')
            values = [int(x) for x in fields[2:-2]]
            record = dict(key=key, county=county, a=values[0], b=values[1], other=sum(values[2:]),
                          pair=values[0] + values[1], source_id=receipt['id'])
            original[year]['native' if native else 'county'][key if native else county] = record
    states = table(B / 'state-scenarios.csv')
    target_rows = table(B / 'county-targets.csv') + table(B / 'native-targets.csv.gz')
    settings = json.loads(read(B / 'scenario-settings.json'))
    settings_by_id = {s['scenario']: s for s in settings}
    grouped = defaultdict(list)
    for row in target_rows:
        grouped[row['scenario'], row['target_pair_margin_pp']].append(row)
    check(len(states) == len(grouped), 'all_state_target_groups')
    check(set(s['geography'] for s in states) == {'county', 'native'}, 'both_actual_geographies')
    for state in states:
        pref, vol = int(state['preference_year']), int(state['volume_year'])
        scope = state['geography']
        rows = []
        for key, source in original[pref][scope].items():
            parent = original[pref]['county'][source['county']]
            volume = original[vol]['county'][source['county']]
            if scope == 'county':
                weight, other = volume['pair'], volume['other']
            else:
                weight = source['pair'] / parent['pair'] * volume['pair']
                check(parent['other'] > 0 or volume['other'] == 0, 'other_volume_not_lost_to_zero_parent')
                other = source['other'] / parent['other'] * volume['other'] if parent['other'] else 0.
            share = source['a'] / source['pair'] if source['pair'] else None
            rows.append(dict(source, weight=weight, other_weight=other, share=share))
        rows_by_key = {r['key']: r for r in rows}
        observed = grouped[state['scenario'], state['target_pair_margin_pp']]
        check(len(observed) == len(rows) == int(state['units']) and
              {r['key'] for r in observed} == set(rows_by_key), 'complete_all_units_nonpriority_included')
        total, other = sum(r['weight'] for r in rows), sum(r['other_weight'] for r in rows)
        original_volume_pair = sum(r['pair'] for r in original[vol]['county'].values())
        original_volume_other = sum(r['other'] for r in original[vol]['county'].values())
        near(total, original_volume_pair, 'declared_source_pair_volume')
        near(other, original_volume_other, 'declared_source_other_volume')
        baseline = sum(r['weight'] * (2 * r['share'] - 1) for r in rows if r['weight'])
        g = float(state['target_pair_margin_pp']) / 100
        target = total * g
        shift = root(rows, target)
        near(state['pair_total'], total, 'state_pair_total')
        near(state['other_votes'], other, 'state_other_total')
        near(state['all_candidate_total'], total + other, 'state_all_candidate_total')
        near(state['baseline_net'], baseline, 'source_baseline_net')
        near(state['target_net'], target, 'state_target_net')
        near(state['bounded_share_shift_pp'], 100 * shift, 'independent_breakpoint_shift', state['scenario'], tolerance=1e-8)
        near(state['unbounded_share_shift_pp'], 100 * (target - baseline) / (2 * total), 'unbounded_share_shift')
        a = sum(r['weight'] * clip(r['share'] + shift) for r in rows if r['weight'])
        near(state['target_A'], a, 'state_target_A')
        near(state['target_B'], total - a, 'state_target_B')
        near(state['A_cushion_vs_all_other_combined'], a - other, 'conservative_other_combined_cushion')
        near(state['achieved_net'], target, 'state_achieved_net')
        check(int(state['clipped_units']) == sum(not 0 <= r['share'] + shift <= 1 for r in rows if r['weight']), 'state_clipping')
        setting = settings_by_id[state['scenario']]
        check(setting['geography'] == scope and setting['preference_anchor'] == pref and setting['volume_anchor'] == vol,
              'settings_match_source_weights')
        for row in observed:
            r = rows_by_key[row['key']]
            w, o, s = r['weight'], r['other_weight'], r['share']
            near(row['scenario_pair_votes'], w, 'unit_source_pair_volume')
            near(row['scenario_other_votes'], o, 'unit_source_other_volume')
            near(row['scenario_all_candidate_votes'], w + o, 'unit_all_volume')
            near(row['pair_participation'], w / (w + o) if w + o else None, 'unit_pair_participation')
            near(row['historical_pair_share'], s, 'unit_source_preference')
            near(row['pair_weight'], w / total, 'unit_pair_weight')
            near(row['candidate_weight'], (w + o) / (total + other), 'unit_all_weight')
            near(row['uniform_bounded_shift_pp'], shift * 100, 'unit_uniform_shift')
            target_share = clip(s + shift) if s is not None else None
            near(row['target_share'], target_share, 'bounded_unit_share')
            own_net = w * (2 * s - 1) if s is not None else 0
            net = w * (2 * target_share - 1) if target_share is not None else 0
            near(row['baseline_net'], own_net, 'unit_baseline_net')
            near(row['target_net'], net, 'unit_net_contribution')
            near(row['target_A_votes'], 0 if not w else w * target_share, 'unit_target_A')
            near(row['target_B_votes'], 0 if not w else w * (1 - target_share), 'unit_target_B')
            near(row['target_all_candidate_margin_pp'], 100 * net / (w + o) if w + o else None,
                 'unit_all_candidate_margin')
            near(row['net_gain'], net - own_net, 'unit_net_gain')
            near(row['gain_per_A_share_pp'], .02 * w, 'unit_factor_two_gain')
            fixed = baseline - own_net
            near(row['others_fixed_net'], fixed, 'selected_fixed_others')
            if w:
                required = (w + target - fixed) / (2 * w)
                near(row['selected_only_required_share'], required, 'selected_conditional_share')
                status = 'already_secured' if required < 0 else 'impossible' if required > 1 else 'feasible'
                check(row['selected_only_status'] == status, 'selected_status')
            else:
                near(row['selected_only_required_share'], None, 'selected_no_pool_share')
                check(row['selected_only_status'] == 'no_positive_pool', 'selected_no_pool_status')
    # Fixed-counted synthetic examples are replayed algebraically, not by calling live().
    cases = json.loads(read(B / 'live-scenarios.json'))
    for case in cases:
        x, result = case['input'], case['result']
        check(result.get('probability') is None, 'live_no_probability')
        if 'remaining_units' in x:
            counted = x['counted']
            check(result['counted_fixed'] == counted, 'live_multi_counted_immutable')
            components = []
            for unit in x['remaining_units']:
                u = unit['remaining_votes']
                pair = u * (1 - unit['remaining_other_share']) if u else 0
                share = clip(unit['remaining_A_pair_share']) if pair and unit['remaining_A_pair_share'] is not None else None
                components.append(dict(key=unit['key'], pool=pair,
                                       a=pair * share if pair and share is not None else None if pair else 0,
                                       b=pair * (1 - share) if pair and share is not None else None if pair else 0, volume=u))
            pair = sum(r['pool'] for r in components)
            unknown = [r for r in components if r['a'] is None]
            a = None if unknown else counted['A'] + sum(r['a'] for r in components)
            b = None if unknown else counted['B'] + sum(r['b'] for r in components)
            total = sum([counted['A'], counted['B'], *counted['other_candidates'].values()]) + sum(r['volume'] for r in components)
            final_pair = counted['A'] + counted['B'] + pair
            near(result['final_A'], a, 'live_multi_fixed_counted_A')
            near(result['final_B'], b, 'live_multi_fixed_counted_B')
            near(result['final_pair_denominator'], final_pair, 'live_multi_final_pair_denominator')
            near(result['final_denominator'], total, 'live_multi_final_all_denominator')
            chosen = next(r for r in components if r['key'] == x['selected_key'])
            if unknown:
                check(unknown == [chosen] and result['status'] == 'conditional_only_selected_preference_unknown'
                      and result['pair_net'] is None, 'live_unknown_selected_no_forecast')
            fixed = counted['A'] - counted['B'] + sum(r['a'] - r['b'] for r in components if r is not chosen)
            target = x.get('target_pair_margin_pp', 0) * final_pair / 100
            required = (chosen['pool'] + target - fixed) / (2 * chosen['pool'])
            near(result['selected_unit_requirement']['fixed_others_net'], fixed, 'live_multi_selected_fixed_others')
            near(result['selected_unit_requirement']['required_share'], required, 'live_multi_selected_final_share')
            near(result['selected_unit_requirement']['target_net'], target, 'live_multi_selected_final_target')
            continue
        counted = x['counted']
        check(result['counted_fixed'] == counted, 'live_counted_immutable')
        if result['status'] != 'calculated':
            expected_status = {'unknown_pool': 'unknown_remaining_pool', 'no_pool': 'no_pool',
                               'negative_pool': 'invalid_negative_or_nonfinite_pool',
                               'unknown_other': 'unknown_other_participation',
                               'unknown_preference': 'unknown_remaining_preference'}
            check(result['status'] == expected_status[case['name']], 'live_unknown_invalid_zero_pool_status')
            continue
        u, p, q = x['remaining_votes'], 1 - x['remaining_other_share'], clip(x['remaining_A_pair_share'])
        pair = u * p
        a, b = counted['A'] + pair * q, counted['B'] + pair * (1 - q)
        final_total = sum([counted['A'], counted['B'], *counted['other_candidates'].values()]) + u
        near(result['final_denominator'], final_total, 'live_final_all_denominator')
        near(result['final_pair_denominator'], counted['A'] + counted['B'] + pair, 'live_final_pair_denominator')
        near(result['final_A'], a, 'live_fixed_counted_A')
        near(result['final_B'], b, 'live_fixed_counted_B')
        if pair:
            target = x.get('target_pair_margin_pp', 0) / 100 * (counted['A'] + counted['B'] + pair)
            required = (pair + target - counted['A'] + counted['B']) / (2 * pair)
            near(result['required_A_pair_share'], required, 'live_final_target_share')
    bounded = json.loads(read(B / 'bounded-scenarios.json'))
    for case in bounded:
        total = sum(case['weights'])
        target = case['target']
        result = case['result']
        if not total:
            check(result['status'] == 'no_positive_pool', 'bounded_no_pool')
        elif any(s is None and w > 0 for w, s in zip(case['weights'], case['shares'])):
            check(result['status'] == 'unknown_preference', 'bounded_unknown_share')
        elif abs(target) > total:
            check(result['status'] == 'impossible' and result['bounded_shift'] is None, 'bounded_impossible')
        else:
            rows = [dict(weight=w, share=s) for w, s in zip(case['weights'], case['shares'])]
            shift = root(rows, target)
            near(result['bounded_shift'], shift, 'independent_bounded_fixture')
    for entry in inputs.values():
        b = (S / entry['path']).read_bytes()
        check(sha(b) == entry['sha256'] and len(b) == entry['bytes'], 'review_input_bytes_stable')
    output = dict(status='pass_independent_source_volume_breakpoint_targets_and_bounded_live_examples',
                  producer_modules_imported=False, solver='independent saturation breakpoint integration',
                  complete_input_pins=list(inputs.values()), state_scenarios=len(states),
                  county_targets=sum(r['scenario'].startswith('county-') for r in target_rows),
                  native_targets=sum(r['scenario'].startswith('native-') for r in target_rows),
                  synthetic_cases=len(cases), checks=dict(checks), total_checks=sum(checks.values()), maximum_errors=dict(errors),
                  county_control_key_representation='Baseline keys have an explicit final empty native-ID component; '
                  'turnout controls omit the trailing delimiter. Source year/contest/literal county determine '
                  'this bounded control-only mapping; native keys are unchanged.',
                  conditional_not_probability=True, current_geography_approved=False, coordinator_priority_accepted=False,
                  qualification='Original pair/other volumes and within-county source fractions are explicit assumptions. '
                  'No cross-year native join, current candidate effect, measured outstanding pool or legal win from pair margin.')
    p = D / 'coordinator-first-pair-target-review.json'
    p.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(dict(path=str(p.relative_to(S)), bytes=p.stat().st_size, sha256=sha(p.read_bytes()), checks=sum(checks.values()))))


if __name__ == '__main__':
    main()

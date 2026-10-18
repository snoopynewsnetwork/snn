"""Coordinator read-only audit of serialized historical targets and live cases.

The bounded solution uses piecewise-linear breakpoints, independently of the
worker's bisection. No worker output or pinned original is changed.
"""
import csv
import datetime
import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
H = ROOT / 'data/baselines'


def rows(path):
    with gzip.open(path, 'rt') if str(path).endswith('.gz') else path.open() as f:
        return list(csv.DictReader(f))


def near(a, b, absolute=2e-7):
    assert math.isclose(float(a), float(b), rel_tol=2e-12, abs_tol=absolute), (a, b)


def clipped(value):
    return min(1.0, max(0.0, value))


def bounded_shift(shares, weights, goal):
    """Solve by visiting the exact changes in the linear function's slope."""
    target = goal * sum(weights)
    points = sorted({-1.0, 1.0} | {-s for s in shares} | {1-s for s in shares})
    def net(d):
        return math.fsum(w * (2 * clipped(s+d)-1) for s, w in zip(shares, weights))
    left, left_net = points[0], net(points[0])
    for right in points[1:]:
        right_net = net(right)
        if left_net <= target <= right_net:
            return left + (right-left) * (target-left_net) / (right_net-left_net)
        left, left_net = right, right_net
    raise AssertionError('Target outside bounded range')


def main():
    source = rows(ROOT / 'data/county-baselines.csv')
    by_fips = {r['county_fips']: r for r in source}
    assert len(source) == len(by_fips) == 105
    states = json.loads((H / 'state-scenarios.json').read_text())
    targets = rows(H / 'county-targets.csv')
    assert len(states) == 22 and len(targets) == 2310
    for state in states:
        rs = [r for r in targets if r['scenario'] == state['scenario'] and
              float(r['goal_pair_margin_pp']) == state['goal_pair_margin_pp']]
        assert {r['county_fips'] for r in rs} == set(by_fips) and len(rs) == 105
        anchor, volume, scale = state['preference_anchor'], state['volume_basis'], state['scale']
        weights = [int(by_fips[r['county_fips']][volume+'_pair_votes'])*scale for r in rs]
        shares = [int(by_fips[r['county_fips']][anchor+'_d_votes']) /
                  int(by_fips[r['county_fips']][anchor+'_pair_votes']) for r in rs]
        T = math.fsum(weights)
        M = math.fsum(w*(2*s-1) for w, s in zip(weights, shares))
        g = state['goal_pair_margin_pp']/100
        shift = bounded_shift(shares, weights, g)
        near(shift, state['shift'])
        near((g*T-M)/(2*T), state['unbounded_shift'])
        near(T, state['total_pair'])
        near(M, state['baseline_net'])
        named_total = math.fsum(int(by_fips[r['county_fips']][volume+'_named_votes'])*scale for r in rs)
        near(named_total, state['expected_named_votes'])
        others = {k: math.fsum(int(c[volume+'_'+k+'_votes'])*scale for c in source)
                  for k in state['final_other_candidates']}
        assert all(math.isclose(v, state['final_other_candidates'][k], abs_tol=1e-7) for k, v in others.items())
        final_a = math.fsum(w*clipped(s+shift) for w, s in zip(weights, shares))
        near(final_a, state['final_A'])
        near(T-final_a, state['final_B'])
        near(final_a*2-T, g*T)
        near(T+sum(others.values()), named_total)
        for r, w, s in zip(rs, weights, shares):
            t = clipped(s+shift)
            near(r['expected_pair_votes'], w)
            near(r['baseline_A_share'], s)
            near(r['target_A_share'], t)
            near(r['target_net'], w*(2*t-1))
            near(r['target_net_gain'], 2*w*(t-s))
            near(r['pair_weight'], w/T)
            near(r['net_gain_per_1pp_A_share'], .02*w)
            near(r['bounded_net_gain_from_plus1pp_A_share'], 2*w*(clipped(s+.01)-s))
            other_net = M - w*(2*s-1)
            q = (g*T-other_net+w)/(2*w)
            near(r['selected_only_others_net'], other_net)
            near(r['selected_only_required_share_unbounded'], q)
            near(r['selected_only_required_share_clipped'], clipped(q))
            expected = ('already_secured_under_fixed_others' if q < 0 else
                        'impossible_under_fixed_others' if q > 1 else
                        'feasible_tie_or_cushion_threshold')
            assert r['selected_only_status'] == expected

    with gzip.open(H / 'native-units.jsonl.gz', 'rt') as f:
        units = [json.loads(line) for line in f]
    native = rows(H / 'native-targets.csv.gz')
    assert len(units) == 22031 and len(native) == 44062
    nu = {u['unit_key']: u for u in units}
    assert len(nu) == 22031
    assert Counter(r['unit_key'] for r in native) == Counter({k: 2 for k in nu})
    broad = [u for u in units if u['source_id'] == 'sos-2024-president-county' and u['pair_votes']]
    shifts = {}
    for state in json.loads((H / 'native-state-scenarios.json').read_text()):
        g = state['goal_pair_margin_pp']/100
        shift = bounded_shift([u['A_votes']/u['pair_votes'] for u in broad], [u['pair_votes'] for u in broad], g)
        near(shift, state['shift'])
        assert sum(not 0 <= u['A_votes']/u['pair_votes']+shift <= 1 for u in broad) == state['clipped_units']
        shifts[g] = shift
    statuses = Counter()
    for r in native:
        u = nu[r['unit_key']]
        assert (r['source_id'], r['county_fips'], r['sheet']) == (u['source_id'], u['county_fips'], u['sheet'])
        g = float(r['goal_pair_margin_pp'])/100
        statuses[r['status']] += 1
        if 'primary' in u['baseline']:
            assert r['status'] == 'separate_party_primary_not_a_general_A_B_electorate'
        elif u['pair_votes'] is None:
            assert r['status'] == 'unavailable_native_pair_cells_not_zero'
        elif u['pair_votes'] == 0:
            assert r['status'] == 'no_positive_pair_pool'
        else:
            assert r['status'] == 'published_numeric_pair'
            w = u['pair_votes']; s = u['A_votes']/w
            T = sum(int(c[u['baseline']+'_pair_votes']) for c in source)
            M = sum(int(c[u['baseline']+'_d_votes'])-int(c[u['baseline']+'_r_votes']) for c in source)
            near(r['baseline_A_share'], s)
            near(r['selected_only_required_share_unbounded'], (g*T-(M-(u['A_votes']-u['B_votes']))+w)/(2*w))
            if u['source_id'] == 'sos-2024-president-county':
                t = clipped(s+shifts[g])
                near(r['statewide_uniform_target_share'], t)
                near(r['statewide_target_net'], w*(2*t-1))
            else:
                assert r['statewide_uniform_target_share'] == '' and r['statewide_target_net'] == ''

    methods = rows(H / 'sumner-method-targets.csv')
    assert len(methods) == 12
    M = sum(int(c['senate_2022_d_votes'])-int(c['senate_2022_r_votes']) for c in source)
    T = sum(int(c['senate_2022_pair_votes']) for c in source)
    for r in methods:
        w = int(r['pair_votes']); a = int(r['A_holland']); b = int(r['B_moran'])
        assert a+b == w
        near(r['selected_only_other_net'], M-(a-b))
        near(r['selected_only_required_A_share'], (float(r['goal_pair_margin_pp'])/100*T-(M-(a-b))+w)/(2*w))

    cases = json.loads((H / 'synthetic-live-scenarios.json').read_text())
    assert len(cases) == 15
    for case in cases:
        inp, out = case['input'], case['output']
        if out['status'] != 'calculated':
            assert case['name'] in {'unknown_pool', 'unknown_preference', 'negative_pool', 'unapproved_clipping_rejected'}
            continue
        a, b = inp['counted']['A'], inp['counted']['B']
        other = dict(inp['counted']['other']); P = 0
        for u in inp['remaining_units']:
            pool = u['remaining_contest_votes']
            pair = pool*(1-sum(u['other_shares'].values())); q = clipped(u['A_pair_share'] or 0)
            a += pair*q; b += pair*(1-q); P += pair
            for k, share in u['other_shares'].items():
                other[k] = other.get(k, 0)+pool*share
        near(a, out['final_A']); near(b, out['final_B'])
        assert out['counted_fixed'] == inp['counted'] and out['final_other'] == other
        near(a+b, out['final_pair_denominator'])
        near(a+b+sum(other.values()), out['final_all_candidate_denominator'])
        assert out['A_clear_plurality'] == (a > max([b]+list(other.values())))
        if P:
            target = inp.get('goal_pair_margin_pp', 0)/100*(a+b)
            near(out['all_remaining_pair_requirement']['required_A_share_unbounded'],
                 (P-inp['counted']['A']+inp['counted']['B']+target)/(2*P))
        assert out['probability'] is None

    manifest = json.loads((H / 'asset-manifest.json').read_text())
    for asset in manifest['owned_assets']+manifest['shared_read_only_original_references']:
        data = (ROOT / asset['path']).read_bytes()
        assert len(data) == asset['bytes'] < 40000000
        assert hashlib.sha256(data).hexdigest() == asset['sha256'], asset['path']
    result = dict(status='pass', checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  county_scenarios=22, county_target_rows=2310, native_target_rows=44062,
                  native_statuses=dict(statuses), additional_Sumner_method_targets=12,
                  live_cases=15, owned_asset_hashes=len(manifest['owned_assets']),
                  original_reference_hashes=len(manifest['shared_read_only_original_references']),
                  scope='Historical conditional arithmetic and serialized provenance only; no live source, remaining-vote estimate, current crosswalk or probability calibration.')
    output = ROOT / 'data/coordinator-target-review.json'
    if output.exists():
        previous = json.loads(output.read_text())
        if {k:v for k,v in previous.items() if k != 'checked_utc'} == {k:v for k,v in result.items() if k != 'checked_utc'}:
            result['checked_utc'] = previous['checked_utc']
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

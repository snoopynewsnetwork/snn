"""Independent source-weight and saturation-event math; no producer imports."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import math

S = Path(__file__).resolve().parents[1]
B = S / 'data/baselines'
N = 0


def ck(value, note=''):
    global N
    assert value, note
    N += 1


def close(a, b, atol=2e-8):
    ck(math.isclose(a, b, rel_tol=2e-11, abs_tol=atol), (a, b))


def read(p):
    return json.loads(p.read_bytes())


def pin(p):
    body = p.read_bytes()
    return {'path': str(p.relative_to(S)), 'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}


def event_root(units, wanted):
    """Integrate exact linear segments between all clipping breakpoints."""
    events = collections.defaultdict(float)
    for u in units:
        events[-u['share']] += 2 * u['pair']
        events[1 - u['share']] -= 2 * u['pair']
    position = -1.0
    value = -sum(u['pair'] for u in units)
    slope = 0.0
    for event, change in sorted(events.items()):
        next_value = value + slope * (event - position)
        if slope > 0 and value <= wanted <= next_value:
            return position + (wanted - value) / slope
        position, value = event, next_value
        slope += change
    raise AssertionError('target not bracketed by full source pool')


def main():
    proof = read(S / 'data/coordinator-native-original-review.json')
    ck(proof['status'] == 'pass_independent_complete_four_contest_original_municipal_source_scope')
    # Only source identity/parent metadata is read from turnout; every vote and
    # printed footer below comes from the independent complete-original audit.
    parent_sources = read(S / 'data/turnout/extract/native-rows.json')
    sid_county = {}
    for rows in parent_sources.values():
        for r in rows:
            if r['source_id'] in sid_county:
                ck(sid_county[r['source_id']] == (r['county'], r['county_fips']))
            sid_county[r['source_id']] = (r['county'], r['county_fips'])
    counties = {}
    natives = {}
    for scope, result in proof['source_results'].items():
        counties[scope] = {}
        for footer in result['printed_county_footers']:
            sid = footer['source_id']
            county, fips = sid_county[sid]
            votes = footer['printed_candidate_vector']
            counties[scope][county] = dict(key=scope + ':county:' + fips, county=county, fips=fips, votes=votes)
        natives[scope] = [dict(key=r['key'], county=sid_county[r['source_id']][0], votes=r['values']) for r in proof['all_original_source_rows'][scope]]
        ck(len(counties[scope]) == 21)

    paths = [B / 'scenario-settings.json', B / 'state-scenarios.json', B / 'targets.csv']
    initial_pins = [pin(p) for p in paths]
    settings = read(paths[0])
    states = read(paths[1])
    target_rows = list(csv.DictReader(paths[2].open()))
    ck(len(settings) == 13 and len(states) == 40 and len(target_rows) == 8588)
    groups = collections.defaultdict(list)
    for r in target_rows:
        groups[(r['scenario'], r['level'], float(r['target_pair_margin']))].append(r)
    ck(len(groups) == 40)
    max_shift_error = max_net_residual = 0.0
    row_count = 0
    reviews = []
    for cfg in settings:
        scope = cfg['source_scope']
        for level in cfg['geographies']:
            source = list(counties[scope].values()) if level == 'county' else natives[scope]
            units = []
            for r in source:
                county = r['county']
                own = counties[scope][county]['votes']
                volume = counties[cfg['county_volume_anchor']][county]['votes']
                pref = counties[cfg['preference_anchor']][county]['votes']
                part = counties[cfg['participation_anchor']][county]['votes']
                values = r['votes']
                V0 = sum(v for v in values if v is not None)
                P0 = sum(v or 0 for v in values[:2])
                local_share = values[0] / P0 if P0 else None
                V = V0 * sum(volume) / sum(own)
                participation = (sum(part[:2]) / sum(part)) if cfg['participation_anchor'] != scope else (P0 / V0 if V0 else 0.0)
                share = (pref[0] / sum(pref[:2])) if cfg['preference_anchor'] != scope else local_share
                share = 0.5 if share is None else share
                T = V * participation
                O0 = sum(v or 0 for v in values[2:])
                others = [(V - T) * (v or 0) / O0 if O0 else 0.0 for v in values[2:]]
                close(sum(others), V - T, 1e-6)
                units.append(dict(key=r['key'], pair=T, share=share, V=V, participation=participation,
                                  others=others, local_share=local_share, P0=P0))
            T = sum(u['pair'] for u in units)
            V = sum(u['V'] for u in units)
            M = sum(u['pair'] * (2 * u['share'] - 1) for u in units)
            other_totals = [sum(u['others'][j] for u in units) for j in range(len(units[0]['others']))]
            for target in (0.0, 0.01):
                key = cfg['id'], level, target
                rows = groups[key]
                ck(len(rows) == len(units) and len({r['unit_key'] for r in rows}) == len(units))
                st = next(s for s in states if (s['scenario'], s['level'], s['target_pair_margin']) == key)
                wanted = target * T
                shift = event_root(units, wanted)
                unbounded = (wanted - M) / (2 * T)
                close(st['published_candidate_volume'], V)
                close(st['pair_volume'], T)
                close(st['baseline_net'], M)
                close(st['other_volume'], V - T)
                close(st['target_net'], wanted)
                close(st['unbounded_shift_share_pp'], 100 * unbounded)
                close(st['bounded_shift_share_pp'], 100 * shift)
                max_shift_error = max(max_shift_error, abs(st['bounded_shift_share_pp'] / 100 - shift))
                close(st['target_all_published_margin_pp'], 100 * wanted / V)
                clipped = 0
                A = net = weights = 0.0
                for u, row in zip(units, rows):
                    ck(u['key'] == row['unit_key'])
                    pair, share, vol = u['pair'], u['share'], u['V']
                    x = min(1, max(0, share + shift))
                    fixed = M - pair * (2 * share - 1)
                    selected = (wanted - fixed + pair) / (2 * pair) if pair > 0 else None
                    clipped += share + shift < 0 or share + shift > 1
                    for field, expected in [('pair', pair), ('pair_participation', u['participation']),
                                            ('published_candidate_volume', vol), ('weight', pair / T),
                                            ('base_share', share), ('base_net', pair * (2 * share - 1)),
                                            ('share_unbounded_target', share + unbounded), ('share_bounded_target', x),
                                            ('share_change_pp', 100 * (x - share)), ('target_margin_pp', 100 * (2 * x - 1)),
                                            ('target_net', pair * (2 * x - 1)), ('net_gain', 2 * pair * (x - share)),
                                            ('net_gain_per_share_pp', 0.02 * pair), ('other_units_fixed_net', fixed),
                                            ('local_unit_Aplus1_net_votes', 0.01 * u['P0'])]:
                        close(float(row[field]), expected)
                    if selected is None:
                        ck(row['selected_only_raw_share'] == '' and row['selected_only_status'] == 'no-positive-pool')
                    else:
                        close(float(row['selected_only_raw_share']), selected)
                        ck(row['selected_only_status'] == ('already-secured' if selected < 0 else 'impossible' if selected > 1 else 'feasible'))
                    if vol:
                        close(float(row['target_all_published_margin_pp']), 100 * pair * (2 * x - 1) / vol)
                        close(float(row['A_target_all_published_share']), pair * x / vol)
                    else:
                        ck(row['target_all_published_margin_pp'] == row['A_target_all_published_share'] == '')
                    if u['local_share'] is None:
                        ck(row['local_unit_tie_share_shift_pp'] == row['local_unit_Aplus1_share_shift_pp'] == '')
                    else:
                        close(float(row['local_unit_tie_share_shift_pp']), 100 * (0.5 - u['local_share']))
                        close(float(row['local_unit_Aplus1_share_shift_pp']), 100 * (0.505 - u['local_share']))
                    published_others = json.loads(row['other_candidate_votes_json'])
                    ck(len(published_others) == len(u['others']))
                    for actual, expected in zip(published_others.values(), u['others']):
                        close(actual, expected)
                    A += pair * x
                    net += float(row['target_net'])
                    weights += float(row['weight'])
                    row_count += 1
                close(weights, 1)
                close(net, wanted, 1e-6)
                close(st['A_votes'], A)
                close(st['B_votes'], T - A)
                close(st['A_all_published_share'], A / V)
                ck(st['clipped_units'] == clipped)
                for actual, expected in zip(st['full_other_votes'].values(), other_totals):
                    close(actual, expected)
                max_net_residual = max(max_net_residual, abs(net - wanted))
                reviews.append(dict(scenario=cfg['id'], level=level, target=target, units=len(units),
                                    source_scope=scope, independent_bounded_share_shift=shift, net_residual=net-wanted))
    ck(row_count == 8588)
    ck(initial_pins == [pin(p) for p in paths], 'captured inputs stayed unchanged during audit')
    result = dict(status='pass_independent_complete_original_weight_and_saturation_event_math', checks=N,
                  settings=len(settings), state_scenarios=len(states), every_unit_rows=row_count,
                  maximum_shift_error=max_shift_error, maximum_net_vote_residual=max_net_residual,
                  complete_reviews=reviews, exact_settings_and_outputs=initial_pins,
                  independent_complete_original_audit=pin(S/'data/coordinator-native-original-review.json'),
                  source_parent_mapping=pin(S/'data/turnout/extract/native-rows.json'),
                  solver='Sorted clipping breakpoints and exact segment integration, no producer bisection or extraction import.',
                  qualification='Observed own-contest source units and explicitly conditional county-volume/preference/participation scenarios, with all nonpriority units. No cross-year native join, eligible-writein allocation, current projection, legal plurality inference or probability.')
    out = S/'data/coordinator-first-pair-math-review.json'
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(dict(checks=N, rows=row_count, shift_error=max_shift_error, net_residual=max_net_residual, pin=pin(out)))


if __name__ == '__main__':
    main()

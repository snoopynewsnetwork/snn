"""Independent real CLI arithmetic and invalid-input fixtures; no producer import."""
from pathlib import Path
import copy
from fractions import Fraction
import hashlib
import json
import math
import subprocess
import sys

S = Path(__file__).resolve().parents[1]
D = S / 'data/coordinator-live-input-review'
CALC = S / 'data/baselines/scripts/calculator.py'


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def unit(key='one', A=20, B=80, C=300, pool=100, fraction=1, share=.6):
    return dict(key=key, counted=dict(A=A, B=B, others={'C': C}),
                remaining=dict(contest_votes=pool, pair_fraction=fraction,
                               a_pair_share=share, share_shift=0, other_mix={'C': 1}))


def base():
    return dict(units=[unit()], target_margin=.01, denominator='pair')


def main():
    D.mkdir(exist_ok=True)
    cases = []
    for label, value in [('null', None), ('bool', True), ('text', '0'),
                         ('nan', float('nan')), ('posinf', float('inf')),
                         ('neginf', float('-inf')), ('range', 1.01)]:
        x = base()
        x['target_margin'] = value
        cases.append(('target_' + label, x, False))
    for label, value in [('null', None), ('blank', ' '), ('number', 1), ('list', [])]:
        x = base()
        x['units'][0]['key'] = value
        cases.append(('key_' + label, x, False))
    x = base()
    x['units'].append(copy.deepcopy(x['units'][0]))
    cases.append(('duplicate_key_no_selected', x, False))
    for name, field, value in [('negative_count', 'A', -1), ('bool_count', 'A', True),
                               ('fractional_count', 'A', .5), ('null_count', 'A', None)]:
        x = base()
        x['units'][0]['counted'][field] = value
        cases.append((name, x, False))
    for name, field, value in [('negative_pool', 'contest_votes', -1),
                               ('invalid_fraction', 'pair_fraction', 1.1),
                               ('invalid_share', 'a_pair_share', -.1),
                               ('nonfinite_shift', 'share_shift', float('inf'))]:
        x = base()
        x['units'][0]['remaining'][field] = value
        cases.append((name, x, False))
    x = base()
    x['units'][0]['remaining']['other_mix'] = {'C': .3}
    cases.append(('nonunit_other_mix', x, False))
    x = base()
    x['selected_key'] = 'absent'
    cases.append(('absent_selected', x, False))
    x = base()
    x['expected_keys'] = ['one', 'missing']
    cases.append(('incomplete_global_coverage', x, False))
    x = base()
    x['units'][0]['remaining'].pop('pair_fraction')
    cases.append(('implicit_missing_participation', x, False))
    x = base()
    x['units'] = [unit(A=0, B=0, C=0, pool=1e308), unit('two', A=0, B=0, C=0, pool=1e308)]
    cases.append(('overflow_derived_denominator', x, False))

    cases.append(('pair_Aplus1_can_lose_other_plurality', base(), True))
    x = base()
    x['denominator'] = 'all'
    cases.append(('all_denominator_distinct', x, True))
    x = base()
    x['units'][0]['remaining']['contest_votes'] = None
    cases.append(('explicit_unknown_remaining', x, True))
    x = base()
    x['units'][0]['remaining'].update(contest_votes=0, a_pair_share=None)
    cases.append(('no_positive_pool', x, True))
    x = base()
    x['units'][0]['counted'].update(A=1000, B=0)
    cases.append(('already_secured', x, True))
    x = base()
    x['units'][0]['counted'].update(A=0, B=1000)
    cases.append(('impossible_positive_target', x, True))
    x = base()
    x['units'].append(unit('two', A=10, B=10, C=0, pool=200, fraction=.5, share=.4))
    x['selected_key'] = 'one'
    cases.append(('selected_only_outside_fixed_and_other_pool', x, True))
    x = base()
    x['units'][0]['remaining']['share_shift'] = 1
    cases.append(('clipped_remaining_preference_counted_fixed', x, True))
    results = []
    for label, x, valid in cases:
        path = D / (label + '.json')
        path.write_text(json.dumps(x, indent=2) + '\n')
        cp = subprocess.run([sys.executable, '-B', '-S', str(CALC), str(path)], capture_output=True, text=True)
        assert not cp.stderr, (label, cp.stderr)
        out = json.loads(cp.stdout, parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
        assert cp.returncode == (0 if valid else 2), (label, cp.returncode, cp.stdout)
        if not valid:
            assert out.get('error'), label
        else:
            A = sum(u['counted']['A'] for u in x['units'])
            B = sum(u['counted']['B'] for u in x['units'])
            C = sum(u['counted']['others']['C'] for u in x['units'])
            assert out['counted_fixed']['A'] == A and out['counted_fixed']['B'] == B
            assert out['counted_fixed']['others']['C'] == C
            if label == 'explicit_unknown_remaining':
                assert out['status'] == 'unknown-assumptions' and out['projected_final'] is None
            else:
                remaining = sum(Fraction(str(u['remaining']['contest_votes'])) * Fraction(str(u['remaining']['pair_fraction'])) for u in x['units'])
                final_pair = A + B + remaining
                final_all = A + B + C + sum(u['remaining']['contest_votes'] for u in x['units'])
                denominator = final_pair if x['denominator'] == 'pair' else final_all
                wanted = Fraction(str(x['target_margin'])) * denominator
                assert math.isclose(out['final_pair_denominator'], float(final_pair))
                assert math.isclose(out['final_all_candidate_denominator'], float(final_all))
                if remaining:
                    expected = (wanted - (A-B) + remaining) / (2*remaining)
                    assert math.isclose(out['conditional_threshold']['raw_share'], float(expected), abs_tol=1e-12)
                if label == 'pair_Aplus1_can_lose_other_plurality':
                    assert out['projected_final']['plurality_leaders'] == ['C']
                    assert out['projected_final']['pair_target_beats_largest_other'] is False
                    assert math.isclose(out['conditional_threshold']['raw_share'], .81)
                elif label == 'all_denominator_distinct':
                    assert math.isclose(out['conditional_threshold']['raw_share'], .825)
                elif label == 'no_positive_pool':
                    assert out['conditional_threshold']['status'] == 'no-positive-pool'
                elif label == 'already_secured':
                    assert out['conditional_threshold']['status'] == 'already-secured'
                elif label == 'impossible_positive_target':
                    assert out['conditional_threshold']['status'] == 'impossible'
                elif label == 'selected_only_outside_fixed_and_other_pool':
                    assert math.isclose(out['selected_only_threshold']['raw_share'], .916)
                    assert out['projected_final']['others']['C'] == 400
                elif label == 'clipped_remaining_preference_counted_fixed':
                    assert out['units'][0]['clipped'] and out['units'][0]['pair_share'] == 1
                    assert out['projected_final']['A'] == 120 and out['projected_final']['B'] == 80
        results.append(dict(label=label, input=pin(path), exit=cp.returncode, stderr=cp.stderr, full_output=out))
    result = dict(status='pass_actual_cli_arithmetic_and_negative_input_review', calculator=pin(CALC),
                  cases=len(cases), positive_cases=sum(v for _, _, v in cases),
                  negative_cases=sum(not v for _, _, v in cases), complete_actual_inputs_outputs=results,
                  qualification='Synthetic source-free arithmetic only. Counted full candidate field fixed; final pair and all denominators distinct; unknown pool not zero, pair target not legal plurality or probability.')
    p = D / 'review.json'
    p.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(dict(cases=len(cases), pin=pin(p)))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Coordinator numerical review, independent piecewise-linear clipped solve."""
from pathlib import Path
import collections
import csv
import datetime
import gzip
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / 'data/baselines'
T = ROOT / 'data/turnout'
load = lambda p: json.loads(p.read_text())
csvrows = lambda p: list(csv.DictReader(p.open()))
clip = lambda q: max(0., min(1., q))
def near(a, b):
    assert math.isclose(float(a), float(b), rel_tol=4e-11, abs_tol=5e-7), (a, b)
def solve(weights, shares, goal):
    pairs = [(w, q) for w, q in zip(weights, shares) if w > 0]
    points = sorted({-1., 1.} | {-q for w, q in pairs} | {1-q for w, q in pairs})
    def net(d):
        return math.fsum(w * (2 * clip(q+d)-1) for w, q in pairs)
    left = points[0]
    value = net(left)
    for right in points[1:]:
        following = net(right)
        if value <= goal <= following and following > value:
            return left + (right-left) * (goal-value)/(following-value)
        left, value = right, following
    raise AssertionError('Unreachable bounded goal')
def status(q):
    return 'already_secured_at_all_B' if q < 0 else 'impossible_at_all_A' if q > 1 else 'feasible_boundary_tie_at_all_A' if q == 1 else 'feasible'

sources = {
    'sos-2024-president-archived-original': ('harris_walz', 'trump_vance', ['harris_walz','trump_vance','oliver_ter_maat','stein_ware','generic_write_ins']),
    'sos-archived-2022-ge-us-senator-5-xls': ('hassan','bolduc',['hassan','bolduc','kauffman','scatter']),
    'sos-2020-senate-archived-original': ('shaheen','messner',['shaheen','messner','odonnell','scatter']),
}
rosters = {s: [json.loads(x) for x in gzip.decompress((T/'native'/ (s+'.jsonl.gz')).read_bytes()).decode().splitlines()] for s in sources}
base = csvrows(ROOT/'data/county-baselines.csv')
assert len(base) == 960
bi = {(r['source_id'],r['county'],r['native_label']):r for r in base}
county = collections.defaultdict(lambda: {'A':0, 'B':0, 'C':0})
for s, rs in rosters.items():
    ak, bk, candidates = sources[s]
    for r in rs:
        f = r['fields']
        b = bi[s,r['county'],r['native_label']]
        for k, v in f.items():
            assert b[k] == ('' if v is None else str(v)), (s,r['native_label'],k)
        A, Bv = f[ak], f[bk]
        assert b['A_votes'] == ('' if A is None else str(A))
        assert b['B_votes'] == ('' if Bv is None else str(Bv))
        pool = A+Bv if A is not None and Bv is not None else None
        assert b['pair_votes'] == ('' if pool is None else str(pool))
        C = sum(f[k] for k in candidates if f[k] is not None)
        assert int(b['reported_candidate_generic_total']) == C
        assert json.loads(b['raw_fields_json']) == r['raw_fields']
        # These are observed numeric subtotals; unknown source cells remain null.
        county[s,r['county']]['A'] += A if A is not None else 0
        county[s,r['county']]['B'] += Bv if Bv is not None else 0
        county[s,r['county']]['C'] += C
settings = load(B/'scenario-settings.json')
states = csvrows(B/'state-scenarios.csv')
natives = csvrows(B/'native-targets.csv')
counties = csvrows(B/'county-targets.csv')
assert len(settings['scenarios']) == 8 and len(states) == 16 and len(natives) == 5120 and len(counties) == 160
ni = collections.defaultdict(list)
ci = collections.defaultdict(list)
for r in natives:
    ni[r['scenario'],r['target']].append(r)
for r in counties:
    ci[r['scenario'],r['target']].append(r)
for st in states:
    case = next(x for x in settings['scenarios'] if x['id'] == st['scenario'])
    src = 'sos-2024-president-archived-original' if case.get('hybrid') or case.get('county_preference') else case['preference_source']
    ak,bk,candidates = sources[src]
    weights, shares, totals = [], [], []
    rs = rosters[src]
    for r in rs:
        f = r['fields']
        known = f[ak] is not None and f[bk] is not None
        p = sum(v for v in [f[ak],f[bk]] if v is not None)
        assert not p or known
        q = f[ak]/p if p else None
        C = sum(f[k] for k in candidates if f[k] is not None)
        if case.get('hybrid'):
            mix = county[case['mix_source'],r['county']]
            own = county[src,r['county']]
            scale = (mix['A']+mix['B'])/(own['A']+own['B'])
            p *= scale
            C *= scale
        if case.get('county_preference') and p:
            preference = county[case['preference_source'],r['county']]
            q = preference['A']/(preference['A']+preference['B'])
        weights.append(p); shares.append(q); totals.append(C)
    P = math.fsum(weights)
    M = math.fsum(w*(2*q-1) for w,q in zip(weights,shares) if w)
    C = math.fsum(totals)
    margin = 0 if st['target'] == 'tie' else .01
    shift = solve(weights,shares,margin*P)
    near(st['total_pair_votes'],P); near(st['baseline_net_votes'],M)
    near(st['all_reported_candidate_generic_volume'],C)
    near(st['unbounded_shift_share_pp'],100*(margin*P-M)/(2*P))
    near(st['bounded_shift_share_pp'],100*shift)
    near(st['achieved_net_votes'],margin*P)
    near(st['positive_improvement_share_pp'],max(0,100*(margin*P-M)/(2*P)))
    nr = ni[st['scenario'],st['target']]
    assert len(nr) == 320
    actual_net = collections.Counter()
    original_net = collections.Counter()
    for row,r,w,q,vol in zip(nr,rs,weights,shares,totals):
        assert row['native_label'] == r['native_label'] and row['county'] == r['county']
        near(row['pair_volume'],w); near(row['all_reported_volume'],vol); near(row['pair_weight'],w/P)
        if not w:
            assert row['target_A_pair_share'] == '' and row['selected_only_status'] == 'no_positive_pool'
            continue
        target = clip(q+shift)
        net = w*(2*target-1)
        before = w*(2*q-1)
        outside = M-before
        required = (w+margin*P-outside)/(2*w)
        near(row['baseline_A_pair_share'],q); near(row['target_A_pair_share'],target)
        near(row['target_net_votes'],net); near(row['net_gain_votes'],net-before)
        near(row['required_change_share_pp'],100*(target-q))
        near(row['selected_only_required_share_unbounded'],required)
        near(row['selected_only_required_share_clipped'],clip(required))
        assert row['selected_only_status'] == status(required)
        actual_net[r['county']] += net
        original_net[r['county']] += before
    for row in ci[st['scenario'],st['target']]:
        name = row['county']
        ix = [i for i,r in enumerate(rs) if r['county']==name]
        w = math.fsum(weights[i] for i in ix)
        near(row['pair_volume'],w); near(row['pair_weight'],w/P)
        near(row['all_reported_volume'],math.fsum(totals[i] for i in ix))
        near(row['baseline_net_votes'],original_net[name]); near(row['target_net_votes'],actual_net[name])
        near(row['selected_county_only_required_share_unbounded'],(w+margin*P-(M-original_net[name]))/(2*w))

cases = load(B/'synthetic-inputs.json')
outputs = load(B/'synthetic-results.json')
assert len(cases) == len(outputs) >= 20
for case,out in zip(cases,outputs):
    assert out['label'] == case['label'] and out['counted_fixed'] == case['counted']
    if out['status'] != 'calculated':
        assert out['status'] in ['unknown_remaining_pool','invalid_negative_or_nonfinite_pool','invalid_counted_votes','unknown_remaining_preference','invalid_pair_participation']
        continue
    counted = case['counted']
    pools = case['remaining']
    A0,B0 = counted['A'],counted['B']
    U = sum(p['total_candidate_votes']*p['pair_fraction'] for p in pools)
    O = sum(p['total_candidate_votes']*(1-p['pair_fraction']) for p in pools)
    A = A0+sum(p['total_candidate_votes']*p['pair_fraction']*clip(p['A_pair_share']) for p in pools if p['total_candidate_votes']*p['pair_fraction'])
    Bv = B0+U-(A-A0)
    F = A0+B0+sum(counted['others'].values())+U+O
    near(out['final_A'],A); near(out['final_B'],Bv)
    near(out['final_pair_denominator'],A0+B0+U); near(out['final_candidate_denominator'],F)
    mode = case.get('target_mode','pair_margin')
    goal = case.get('target_fraction',0)*(A0+B0+U if mode=='pair_margin' else F)
    if U:
        near(out['required_remaining_A_pair_share_unbounded'],(U+goal-(A0-B0))/(2*U))
    if not out['unknown_other_allocation']:
        fo = dict(counted['others'])
        for p in pools:
            for name,q in p.get('other_allocation',{}).items():
                fo[name] = fo.get(name,0)+p['total_candidate_votes']*(1-p['pair_fraction'])*q
        assert set(fo) == set(out['final_named_others'])
        for name,value in fo.items():
            near(value,out['final_named_others'][name])
        plural = 'A_leads_every_named_opponent' if A>max([Bv]+list(fo.values())) else 'A_tied_or_behind_a_named_opponent'
        assert out['conditional_plurality_status'] == plural
        if float(U).is_integer():
            needed = max(math.floor((U-(A0-B0))/2)+1,math.floor(max([0]+list(fo.values()))-A0)+1,0)
            assert out['strict_plurality_minimum_integer_A_votes_from_remaining_pair'] == needed
out = {'status':'pass','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'independent_solver':'Piecewise-linear breakpoints; worker uses bisection. Original source rosters conserved separately.',
       'baseline_native_rows':960,'historical_scenarios':8,'state_targets':16,'county_targets':160,
       'native_targets':5120,'synthetic_fixed_counted_cases':len(cases),
       'candidate_pair_anchors':{'2024':814011,'2022':608121,'2020':777007},
       'scope':'Source-scoped numeric subtotals, explicit county-mix/preference assumptions and bounded shifts; no cross-year native equivalence or calibrated2026 probability.'}
path = ROOT/'data/coordinator-target-review.json'
if path.exists():
    previous = load(path)
    if {k:v for k,v in previous.items() if k!='checked_utc'} == {k:v for k,v in out.items() if k!='checked_utc'}:
        out['checked_utc'] = previous['checked_utc']
path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

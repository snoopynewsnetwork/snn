"""Audit all native target rows with an independent piecewise-linear solver."""
from pathlib import Path
from collections import defaultdict
import csv
import gzip
import hashlib
import io
import json
import math
import re

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
DEST = DATA / 'coordinator-qa/native-target-review'
ANCHORS = ['2024-senate','2024-president','2020-senate','2018-special','2018-runoff']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}


def frozen(path):
    dest = DEST / (path.name+'.gz')
    if not dest.exists():
        b = path.read_bytes()
        assert path.read_bytes() == b
        dest.write_bytes(gzip.compress(b,mtime=0))
    return gzip.decompress(dest.read_bytes()),pin(dest)


def clip(q):
    return min(1.,max(0.,q))


def piecewise(weights,shares,target):
    """Integrate exact linear segments between all saturation breakpoints."""
    total = math.fsum(weights)
    assert -total <= target <= total and total > 0
    events = defaultdict(list)
    for w,q in zip(weights,shares):
        events[-q].append(2*w)
        events[1-q].append(-2*w)
    x,net,slope = -1.,-total,0.
    for end,changes in sorted(events.items()):
        next_net = net+slope*(end-x)
        if slope > 0 and net <= target <= next_net:
            result = x+(target-net)/slope
            assert abs(math.fsum(w*(2*clip(q+result)-1) for w,q in zip(weights,shares))-target) < 1e-6
            return result
        x,net = end,next_net
        slope += math.fsum(changes)
    raise AssertionError('Target was not bracketed by piecewise saturation events')


def main():
    DEST.mkdir(exist_ok=True)
    ledger_raw = gzip.decompress((DATA / 'coordinator-qa/native-replay-84views/native-2024-senate-reviewed-84views.json.gz').read_bytes())
    ledger = json.loads(ledger_raw)
    county_raw,county_pin = frozen(DATA / 'county-baselines.csv')
    counties = {r['fips']:r for r in csv.DictReader(io.StringIO(county_raw.decode(),newline=''))}
    settings_raw,settings_pin = frozen(DATA / 'baselines/native-source-calculator-settings.json')
    settings = json.loads(settings_raw)
    assert settings['input_ledger_sha256'] == sha(ledger_raw)
    assert settings['historical_native_pair_votes'] == 1215400 and settings['certified_county_pair_votes'] == 1215401
    assert settings['complete_all_candidate_native_question'] is False and settings['current2026_identity_approved'] is False
    units = {}
    parents = defaultdict(int)
    for source in ledger['sources']:
        if not source['use_in_preferred82_scope']:
            continue
        for p in source['pages']:
            for c in p['columns']:
                if c['role'] != 'source_native_reporting_constituent':
                    continue
                a,b = c['fields']['Ty Pinkins']['value'],c['fields']['Roger F. Wicker']['value']
                key = f'{source["county_fips"]}:{source["source_id"]}:p{p["page"]}:c{c["source_column"]}'
                assert key not in units
                units[key] = {'key':key,'fips':source['county_fips'],'a':a,'b':b,'n':a+b,
                              'q':a/(a+b) if a+b else .5,'label':c['label_literal'],
                              'source_id':source['source_id'],'raw_sha256':source['raw_sha256']}
                parents[source['county_fips']] += a+b
    assert len(units) == 1736 and set(parents) == set(counties) and sum(parents.values()) == 1215400
    mixes = {'base-2024-native-Senate':dict(parents)}
    for name,field in [('low-2022-EAC-counted-ballots','eac_2022_F1a'),
                       ('high-2020-Senate','2020-senate_pair_votes'),
                       ('midterm-2018-special-pair','2018-special_pair_votes'),
                       ('midterm-2018-runoff-pair','2018-runoff_pair_votes')]:
        values = {f:float(r[field]) for f,r in counties.items()}
        assert all(v >= 0 for v in values.values())
        mixes[name] = values
        scale = 1215400/math.fsum(values.values())
        mixes[name+'-normalized-to-native-2024-pair'] = {f:v*scale for f,v in values.items()}
    state_raw,state_pin = frozen(DATA / 'baselines/native-source-state-targets.csv')
    state_rows = list(csv.DictReader(io.StringIO(state_raw.decode(),newline='')))
    assert len(state_rows) == 90
    groups = {}
    max_net_error = max_shift_error = 0.
    for row in state_rows:
        key = (row['scenario'],row['preference_anchor'],float(row['target_pair_margin_pp']))
        assert key not in groups
        mix,anchor,margin = key
        weights = {k:mixes[mix][u['fips']]*u['n']/parents[u['fips']] for k,u in units.items()}
        qs = {k:u['q'] if anchor == '2024-senate' else
              float(counties[u['fips']][anchor+'_A'])/float(counties[u['fips']][anchor+'_pair_votes']) for k,u in units.items()}
        total = math.fsum(weights.values())
        baseline = math.fsum(weights[k]*(2*qs[k]-1) for k in units)
        target = margin*total/100
        shift = piecewise(list(weights.values()),list(qs.values()),target)
        outs = math.fsum(float(r[anchor+'_other']) for r in counties.values())
        achieved = math.fsum(weights[k]*(2*clip(qs[k]+shift)-1) for k in units)
        clipped = sum(q+shift<0 or q+shift>1 for q in qs.values())
        assert abs(float(row['bounded_shift'])-shift) < 1e-12
        assert abs(float(row['pair_votes'])-total) < 1e-6
        assert abs(float(row['baseline_net'])-baseline) < 1e-6
        assert abs(float(row['target_net'])-target) < 1e-6
        assert int(row['clipped_units']) == clipped
        assert abs(float(row['unbounded_shift'])-(target-baseline)/(2*total)) < 1e-12
        assert abs(float(row['historical_named_other_votes_held_fixed'])-outs) < 1e-6
        assert abs(float(row['conditional_named_all_candidate_denominator'])-(total+outs)) < 1e-6
        max_net_error = max(max_net_error,abs(achieved-target))
        max_shift_error = max(max_shift_error,abs(float(row['bounded_shift'])-shift))
        groups[key] = {'weights':weights,'shares':qs,'total':total,'baseline':baseline,'target':target,
                       'shift':shift,'outsiders':outs,'clipped_units':clipped,'county':defaultdict(lambda:[0.,0.,0.,0.])}
    assert len(groups) == 90
    path = DATA / 'baselines/native-source-unit-targets.csv.gz'
    target_pin = pin(path)
    assert target_pin['sha256'] == settings['stored_sha256'] and target_pin['bytes'] == settings['stored_bytes'] < 40000000
    raw_hash = hashlib.sha256()
    size = 0
    with gzip.open(path,'rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            raw_hash.update(block)
            size += len(block)
    assert raw_hash.hexdigest() == settings['original_csv_sha256'] and size == settings['original_csv_bytes']
    seen = set()
    numeric_checks = 0
    with gzip.open(path,'rt',newline='') as stream:
        for r in csv.DictReader(stream):
            group_key = (r['scenario'],r['preference_anchor'],float(r['target_pair_margin_pp']))
            key = (group_key,r['key'])
            assert key not in seen
            seen.add(key)
            u,g = units[r['key']],groups[group_key]
            w,q = g['weights'][u['key']],g['shares'][u['key']]
            shifted = clip(q+g['shift'])
            old_net,new_net = w*(2*q-1),w*(2*shifted-1)
            fixed = g['baseline']-old_net
            req = (w+g['target']-fixed)/(2*w) if w>0 else None
            assert r['source_id'] == u['source_id'] and r['raw_sha256'] == u['raw_sha256']
            assert re.sub(r'\s','',r['label_literal']) == re.sub(r'\s','',u['label'])
            for field,value in {'historical_A':u['a'],'historical_B':u['b'],'historical_pair':u['n'],
                'expected_unit_pair_votes':w,'source_parent_pair_votes':parents[u['fips']],
                'state_pair_votes':g['total'],'state_pair_weight':w/g['total'],
                'baseline_A_share':q,'baseline_unit_net':old_net,'state_baseline_net':g['baseline'],
                'state_target_net':g['target'],'target_A_share':shifted,'target_net':new_net,
                'net_gain':new_net-old_net,'net_gain_for_one_A_share_pp':.02*w,
                'conditional_named_all_candidate_denominator':g['total']+g['outsiders'],
                'historical_named_other_votes_held_fixed':g['outsiders'],
                'selected_only_fixed_other_net':fixed,'local_net_gain_to_tie':-old_net,
                'local_net_gain_to_A_plus_1':.01*w-old_net}.items():
                assert abs(float(r[field])-value) < 1e-6,(field,r[field],value)
                numeric_checks += 1
            if req is None:
                assert r['selected_only_required_A_share'] == '' and r['selected_only_status'] == 'no_positive_pool'
            else:
                assert abs(float(r['selected_only_required_A_share'])-req) < 1e-7
                status = 'impossible' if req>1 else 'already_above_target_at_zero_share' if req<0 else 'feasible'
                assert r['selected_only_status'] == status
                assert abs(fixed+w*(2*req-1)-g['target']) < 1e-6
            agg = g['county'][u['fips']]
            for i,value in enumerate([w,old_net,new_net,new_net-old_net]):
                agg[i] += value
    assert len(seen) == 156240 and pin(path) == target_pin
    county_targets_raw,county_targets_pin = frozen(DATA / 'baselines/native-source-county-contributions.csv')
    county_rows = list(csv.DictReader(io.StringIO(county_targets_raw.decode(),newline='')))
    assert len(county_rows) == 7380
    county_seen = set()
    for r in county_rows:
        group_key = (r['scenario'],r['preference_anchor'],float(r['target_pair_margin_pp']))
        key = (group_key,r['county_fips'])
        assert key not in county_seen
        county_seen.add(key)
        expected = groups[group_key]['county'][r['county_fips']]
        for name,value in zip(['expected_pair_votes','baseline_net','target_net','net_gain'],expected):
            assert abs(float(r[name])-value) < 1e-6
    base = groups['base-2024-native-Senate','2024-senate',0.]
    plus1 = groups['base-2024-native-Senate','2024-senate',1.]
    assert base['clipped_units'] == 133 and plus1['clipped_units'] == 137
    out = {
        'status':'pass_90_piecewise_native_state_solves_156240_unit_rows_7380_county_contributions',
        'settings_snapshot':settings_pin,'county_inputs_snapshot':county_pin,
        'state_targets_snapshot':state_pin,'county_contributions_snapshot':county_targets_pin,
        'unit_target_original_pin':target_pin,'state_groups':90,'native_units':1736,'parent_counties':82,
        'unit_target_rows':156240,'unit_numeric_formula_checks':numeric_checks,'county_contribution_rows':7380,
        'max_piecewise_achieved_net_error_votes':max_net_error,'max_worker_shift_difference':max_shift_error,
        'native_source_denominator':1215400,'certified_county_denominator_not_allocated':1215401,
        'base_tie_share_shift_pp':100*base['shift'],'base_tie_clipped_units':base['clipped_units'],
        'base_A_plus1_share_shift_pp':100*plus1['shift'],'base_A_plus1_clipped_units':plus1['clipped_units'],
        'scope':'The coordinator independently integrates saturation breakpoints, rather than importing the worker bisection solver. All90 groups/156240 native rows and7380 county aggregates close their fixed historical source pool. Other-year county volumes/preferences remain explicit conditional mixes over2024 source units; no historical native geography is inferred. The missing Tunica vote stays outside1215400. Pair arithmetic is not a2026 plurality threshold, current candidate coalition, forecast or calibrated probability; full original-field/native-method gates remain open.'}
    (DATA / 'coordinator-native-target-review.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','unit_numeric_formula_checks','max_piecewise_achieved_net_error_votes',
          'max_worker_shift_difference','base_tie_share_shift_pp','base_A_plus1_share_shift_pp']}))


if __name__ == '__main__':
    main()

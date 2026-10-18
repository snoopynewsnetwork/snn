"""Independent original ENR counts and bounded native/method target equations."""
import collections
import csv
import gzip
import io
import json
import re
from pathlib import Path
from review_legacy import originals, json_pointer
from review_targets import close, clipped, solve

HERE = Path(__file__).resolve().parent
BASE = HERE / 'baselines'


def rows(name):
    with gzip.open(BASE / name, 'rt') as stream:
        return list(csv.DictReader(stream))


def main():
    contract = json.loads((HERE / 'turnout/priority-set.json').read_bytes())
    xml_sources, _ = originals(contract['legacy_source_observations'], True)
    json_sources, _ = originals(contract['original_combined_json_observations'], False)
    native_rows = rows('legacy-native-baselines.csv.gz')
    native = {row['geography_key']: row for row in native_rows}
    assert len(native) == len(native_rows) == 9635
    native_values = {}
    method_values = collections.defaultdict(lambda: [0, 0, 0])
    for row in native_rows:
        source = json_sources[row['source_id']]
        path = row['source_pointer'].split('/P/')[0]
        ordinal = int(row['source_pointer'].rsplit('/', 1)[1])
        details = json_pointer(source, path)
        assert details['P'][ordinal] == row['name']
        vector = details['V'][ordinal]
        summary_id = row['source_id'].removesuffix('-details') + '-summary'
        matches = [s for s in json_sources[summary_id] if s.get('K') == details['K']]
        assert len(matches) == 1
        summary = matches[0]
        parties = summary['P']
        assert len(parties) == len(vector)
        values = [sum(value for value, party in zip(vector, parties) if party == 'DEM'),
                  sum(value for value, party in zip(vector, parties) if party == 'REP')]
        values.append(sum(vector)-sum(values))
        native_values[row['geography_key']] = values
        assert json.loads(row['raw_choice_vector']) == vector
        for field, value in zip(['A', 'B', 'other'], values):
            close(row[field], value)
        source_id = row['source_id'].removesuffix('-details')
        if source_id not in xml_sources:
            assert source_id == 'legacy2022-county-clarendon'
            continue
        root = xml_sources[source_id]
        contests = [c for c in root.findall('Contest') if c.attrib.get('key') == details['K']]
        assert len(contests) == 1
        for choice in contests[0].findall('Choice'):
            party = choice.attrib.get('party')
            bucket = 0 if party == 'DEM' else (1 if party == 'REP' else 2)
            for method in choice.findall('VoteType'):
                matches = [p for p in method if p.attrib['name'] == row['raw_name']]
                assert len(matches) == 1, (source_id, row['name'])
                key = source_id, details['K'], row['raw_name'], method.attrib['name']
                method_values[key][bucket] += int(matches[0].attrib['votes'])

    # Clarendon's actual enabled original TXT has six methods plus a total per choice.
    text = json_sources['legacy2022-clarendon-pinned-detailtxt'].decode('utf-8-sig')
    lines = text.splitlines()
    txt_controls = 0
    for title, label, key in [('U.S. Senate', '2022-senate', '0012'),
                              ('Governor and Lieutenant Governor', '2022-governor', '0005')]:
        index = next(i for i, line in enumerate(lines) if line.strip() == title+' (Vote For 1)')
        candidates_line = lines[index+1]
        header = lines[index+2]
        columns = [header[i:i+30].strip() for i in range(0, len(header), 30)]
        assert columns[:2] == ['County', 'Registered Voters']
        expected = [r for r in native_rows if r['county_fips'] == '45027' and r['contest_label'] == label]
        source_rows = {}
        for line in lines[index+3:]:
            parts = [line[i:i+30].strip() for i in range(0, len(line), 30)]
            if parts and parts[0] in {r['raw_name'] for r in expected}:
                assert len(parts) == len(columns)
                source_rows[parts[0]] = parts
            if len(source_rows) == len(expected):
                break
        assert len(source_rows) == len(expected) == 28
        choice_count = (len(columns)-3)//7
        assert 2+7*choice_count+1 == len(columns)
        for row in expected:
            values = source_rows[row['raw_name']]
            totals = [0, 0, 0]
            for choice in range(choice_count):
                offset = 2+choice*7
                candidate = candidates_line[offset*30:(offset+7)*30].strip()
                bucket = 0 if candidate.startswith('DEM ') else (1 if candidate.startswith('REP ') else 2)
                for method in range(6):
                    method_name = columns[offset+method]
                    value = int(values[offset+method])
                    method_values['legacy2022-clarendon-pinned-detailtxt', key, row['raw_name'], method_name][bucket] += value
                    txt_controls += 1
                total = int(values[offset+6])
                assert total == sum(int(values[offset+m]) for m in range(6))
                totals[bucket] += total
            assert totals == native_values[row['geography_key']]

    methods = rows('legacy-method-baselines.csv.gz')
    assert len(methods) == 57810
    method_by_key = {}
    for row in methods:
        base_key = row['geography_key'].split(':method:', 1)[0]
        parent = native[base_key]
        contest_key = re.search(r':c([^:]+):', base_key).group(1)
        source_key = row['source_id'], contest_key, parent['raw_name'], row['raw_method']
        values = method_values[source_key]
        for field, value in zip(['A', 'B', 'other'], values):
            close(row[field], value)
        method_by_key[row['geography_key']] = values
    assert len(method_by_key) == len(method_values) == 57810

    statewide_controls = []
    for label in ['2024-pres', '2020-senate', '2022-senate', '2022-governor']:
        document = json.loads(gzip.decompress((HERE / 'history-api' / f'history-{label}-granular-combined.body.gz').read_bytes()))['data']['contestGranularData']
        actual_ids = {int(c['candidateId']) for c in document['candidates'] if c['candidate']['pseudocandidate'] in (None, 'ALL_OTHER_CANDIDATES')}
        raw = document['divisions']['granularRow']
        expected = [sum(r['votes'] for r in raw if r['candidateId'] in actual_ids and r['partyId'] == 1),
                    sum(r['votes'] for r in raw if r['candidateId'] in actual_ids and r['partyId'] == 2)]
        expected.append(sum(r['votes'] for r in raw if r['candidateId'] in actual_ids)-sum(expected))
        combined_sum = [sum(native_values[row['geography_key']][i] for row in native_rows if row['contest_label'] == label) for i in range(3)]
        method_sum = [sum(method_by_key[row['geography_key']][i] for row in methods if row['contest_label'] == label) for i in range(3)]
        assert expected == combined_sum == method_sum
        statewide_controls.append({'contest': label, 'D': expected[0], 'R': expected[1], 'other': expected[2]})

    checked = 0
    groups_checked = 0
    maximum_error = 0.0
    for filename, lookup in [('legacy-native-targets.csv.gz', native_values),
                              ('legacy-method-targets.csv.gz', method_by_key)]:
        groups = collections.defaultdict(list)
        for row in rows(filename):
            groups[row['scenario'], row['target']].append(row)
        assert len(groups) == 8
        for (scenario, target_name), group in groups.items():
            values = [lookup[row['geography_key']] for row in group]
            weights = [a+b for a, b, other in values]
            shares = [a/(a+b) if a+b else 0.0 for a, b, other in values]
            total = sum(weights)
            target = 0.0 if target_name == 'tie' else .01*total
            delta = solve(weights, shares, target)
            achieved = 0.0
            for row, (a, b, other), weight, share in zip(group, values, weights, shares):
                for field, value in [('historical_A', a), ('historical_B', b), ('historical_other', other), ('pair_pool', weight), ('other_pool', other), ('weight', weight/total), ('bounded_shift_pp', 100*delta)]:
                    close(row[field], value)
                net = weight*(2*clipped(share+delta)-1)
                close(row['target_net'], net)
                achieved += net
                checked += 1
            maximum_error = max(maximum_error, abs(achieved-target))
            assert abs(achieved-target) < 2e-6
            groups_checked += 1
    result = {'status': 'pass_original_counts_and_independent_piecewise_linear_targets',
              'original_JSON_native_vectors': len(native_values), 'original_native_method_vectors': len(method_by_key),
              'Clarendon_TXT_method_cells': txt_controls, 'bounded_groups': groups_checked,
              'target_rows': checked, 'maximum_target_error_votes': maximum_error,
              'complete_state_controls': statewide_controls,
              'scope': 'Original ENR combined and XML/TXT method scopes; no DB gap filling, physical/current join or forecast.'}
    (HERE / 'coordinator-original-target-review.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

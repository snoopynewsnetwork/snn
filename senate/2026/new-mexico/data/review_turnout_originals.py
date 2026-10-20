"""Coordinator original-byte/whole-field audit; no producer imports or writes.

This reviews the immutable first turnout handoff, not a future reciprocal seal.
Protected observations are checked as unknown, never solved from residuals.
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import csv
import gzip
import hashlib
import io
import json
import re
import subprocess
import tempfile

S = Path(__file__).resolve().parents[1]
T = S / 'data/turnout'
N = 0


def ck(value, label=''):
    global N
    assert value, label
    N += 1


def digest(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    return json.loads(p.read_bytes())


def pin(p):
    z = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(z), sha256=digest(z))


class NextData(HTMLParser):
    def __init__(self, raw):
        super().__init__()
        self.enabled = False
        self.fragments = []
        self.feed(raw.decode('utf-8-sig'))

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.enabled = dict(attrs).get('id') == '__NEXT_DATA__'

    def handle_endtag(self, tag):
        if tag == 'script':
            self.enabled = False

    def handle_data(self, value):
        if self.enabled:
            self.fragments.append(value)


class LiteralText(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.feed(raw)

    def handle_data(self, value):
        self.parts.append(value)

    def text(self):
        return ' '.join(' '.join(self.parts).split())


def numeric(value):
    return int(value.replace(',', '')) if re.fullmatch(r'-?\d[\d,]*', value) else None


def main():
    mf = T / 'asset-manifest.json'
    ck(digest(mf.read_bytes()) == '386c585692491b28b04082d8120e0561771fe6fb2fee200795f98c95e758d88b')
    seal = read(mf)
    expected = {r['path'] for r in seal['owned_assets']}
    actual = {str(p.relative_to(S)) for p in T.rglob('*') if p.is_file() and p != mf}
    actual |= {'turnout.md', 'data/county-turnout.csv'}
    ck(actual == expected and len(expected) == len(seal['owned_assets']) == 91)
    for lane in ['owned_assets', 'source_assets']:
        for row in seal[lane]:
            z = (S / row['path']).read_bytes()
            ck(len(z) == row['bytes'] < 40000000 and digest(z) == row['sha256'], row['path'])
            ck(not any(k in Path(row['path']).parts for k in ['__pycache__', 'node_modules', '.venv']))
    receipts = read(T / 'acquisition.json')
    by_id = {r['id']: r for r in receipts}
    ck(len(by_id) == len(receipts))
    originals = {}
    hops = 0
    for receipt in receipts:
        ck(all(k in receipt for k in ['url', 'final_url', 'retrieved_at_utc', 'status']))
        for row in [receipt, *receipt.get('redirects', [])]:
            if not row.get('asset'):
                continue
            z = (S / row['asset']).read_bytes()
            ck(digest(z) == row['stored_sha256'] and len(z) < 40000000)
            raw = gzip.decompress(z) if row.get('compression') == 'gzip' else z
            ck(digest(raw) == row['raw_sha256'] and len(raw) == row['bytes'])
            if row is receipt:
                originals[receipt['id']] = raw
            else:
                hops += 1
    source = read(T / 'original-extract.json')
    specs = [
        ('2024-senate', 'elstats-2024-senate-linked-csv', 'elstats-2024-senate', 2201),
        ('2020-senate', 'elstats-observed-2020-senate-native-csv', 'elstats-observed-2020-senate-view', 1959),
        ('2022-governor', 'elstats-observed-2022-governor-native-csv', 'elstats-observed-2022-governor-view', 2196),
        ('2024-president', 'elstats-observed-2024-president-native-csv', 'elstats-observed-2024-president-view', 2202),
    ]
    independent = {}
    positions = 0
    for tag, export, view, count in specs:
        parsed = list(csv.reader(io.StringIO(originals[export].decode('utf-8-sig'))))
        saved = source[tag]
        ck(saved['header_rows'] == parsed[:2] and saved['raw_sha256'] == digest(originals[export]))
        js = NextData(originals[view])
        ck(saved['metadata'] == json.loads(''.join(js.fragments))['props']['pageProps'])
        ck([r['raw_row'] for r in saved['rows']] == parsed[2:])
        nc = len(parsed[0]) - 4
        county = None
        records = []
        for number, (raw, row) in enumerate(zip(parsed[2:], saved['rows']), 3):
            if raw[0] == 'County':
                county = raw[1]
            ck(row['source_row_1based'] == number and row['source_id'] == export)
            ck(row['native_label'] == raw[1] and row['level'] == raw[0])
            ck(row['county_literal'] == (None if raw[0] == 'State' else county))
            ck(row['administrative'] == (raw[0] == 'Precinct' and raw[1] == 'Voter Privacy'))
            expected_key = 'nm:elstats:' + saved['contest_id'] + ':' + (county + ':' + raw[1] if raw[0] == 'Precinct' else raw[0] + ':' + raw[1])
            ck(row['key'] == expected_key)
            cells = [numeric(v) for v in raw[2:]]
            for col, (literal, cell) in enumerate(zip(raw[2:], row['fields']), 2):
                ck(cell['column_1based'] == col + 1 and cell['label'] == parsed[0][col])
                ck(cell['party_literal'] == parsed[1][col] and cell['literal'] == literal)
                ck(cell['value'] == numeric(literal))
                ck(cell['kind'] == ('candidate' if col < 2 + nc else 'printed_contest_total' if col == 2 + nc else 'printed_ballot_total'))
                positions += 1
            complete = sum(cells[:nc]) if None not in cells[:nc] else None
            ck(row['candidate_votes'] == complete)
            ck(row['known_candidate_sum'] == sum(v for v in cells[:nc] if v is not None))
            ck(all(row[k] is None for k in ['native_numeric_id', 'method', 'registration', 'blank', 'undervotes', 'overvotes', 'write_in']))
            records.append(dict(key=expected_key, county=county, label=raw[1], level=raw[0], values=cells, complete=complete, source_row=number, administrative=row['administrative']))
        parents = [r for r in records if r['level'] == 'County']
        native = [r for r in records if r['level'] == 'Precinct']
        ck(len(parents) == 33 and len(native) == count and sum(r['administrative'] for r in native) == 33)
        ck(len({r['key'] for r in records}) == len(records))
        ck([sum(r['values'][j] for r in parents) for j in range(nc + 2)] == records[0]['values'])
        for p, reported in zip(parents, saved['reconciliation']):
            kids = [r for r in native if r['county'] == p['label']]
            known = [sum(r['values'][j] for r in kids if r['values'][j] is not None) for j in range(nc + 2)]
            ck(reported['known_sums'] == known)
            ck(reported['county_minus_known'] == [v - k for v, k in zip(p['values'], known)])
        independent[tag] = dict(parents=parents, native=native, state=records[0], candidate_count=nc)
    c = read(T / 'priority-set.json')
    native = independent['2024-senate']['native']
    known = sorted([r for r in native if r['complete'] is not None], key=lambda r: (-r['complete'], r['source_row']))
    masked = [r for r in native if r['complete'] is None]
    ck(len(known) == 2181 and len(masked) == 20 and sum(r['complete'] for r in known) == 902421)
    ck(c['ordered_priority_keys'] == [] and not c['accepted_for_dispatch'])
    ck(all(c[k] is None for k in ['certified_native_top15', 'certified_native_minimum80', 'certified_native_full_order']))
    ck(c['complete_coverage_order'] == [r['key'] for r in known + masked])
    ck(c['known_observation_scope']['order'] == [r['key'] for r in known])
    ck(c['unavailable_order_keys'] == [r['key'] for r in masked])
    ck(len(c['constituents']) == len(native) == 2201 and len(c['county_contexts']) == 33)
    for a, b in zip(native, c['constituents']):
        ck(a['key'] == b['key'] and a['values'][:2] == b['candidate_values'])
        ck(a['complete'] == b['complete_candidate_votes'] and b['current_2026_crosswalk'] is None)
    for parent in c['county_contexts']:
        ck(parent['source_native_constituent_keys'] == [r['key'] for r in native if r['county'] == parent['source_label']])
    sensitivity = read(T / 'sensitivity.json')
    for name, x in sensitivity.items():
        order = x['order']
        ck(order == sorted(order, key=lambda r: (-r['votes'], r['source_order'])), name)
        cum = 0
        for rank, row in enumerate(order, 1):
            cum += row['votes']
            ck(row['rank'] == rank and row['cumulative_votes'] == cum)
        den = x['denominator']
        cutoff = next(i for i, r in enumerate(order, 1) if r['cumulative_votes'] * 5 >= den * 4)
        ck(cutoff == x['minimum80_count'])
        ck(x['minimum80_votes'] == order[cutoff - 1]['cumulative_votes'])
        ck(x['preceding_votes'] == (order[cutoff - 2]['cumulative_votes'] if cutoff > 1 else 0))
        ck(x['top15_votes'] == sum(r['votes'] for r in order[:15]))
        ck(x['ordered_minimum80_keys'] == [r['key'] for r in order[:cutoff]])
    controls = read(T / 'canvass-controls.json')
    text_by_id = {}
    for year, saved in controls['county_controls'].items():
        sid = saved['source_id']
        with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
            f.write(originals[sid]); f.flush()
            out = subprocess.run(['pdftotext', '-layout', f.name, '-'], capture_output=True, check=True).stdout
        ck(out == (T / 'source' / (sid + '.txt')).read_bytes())
        text_by_id[sid] = out.decode()
        lines = out.decode().split('\f')[0].splitlines()
        tag = {'2024': '2024-senate', '2020': '2020-senate', '2022': '2022-governor'}[year]
        for row in saved['candidate_rows'] + saved['whole_ballot_method_rows']:
            i, j = row['line_1based'], row['numeric_line_1based']
            ck(row['raw_lines'] == lines[i-1:j])
            values = [int(v.replace(',', '')) for v in re.findall(r'(?<![\w.])-?\d[\d,]*(?![\w.])', lines[j-1])]
            ck(values == row['county_values'] + [row['state']] and sum(values[:-1]) == values[-1])
            if 'candidate_csv_column_1based' in row:
                col = row['candidate_csv_column_1based'] - 3
                ck(row['county_values'] == [p['values'][col] for p in independent[tag]['parents']])
        ck(saved['pdf_state_ballots'] == sum(r['state'] for r in saved['whole_ballot_method_rows']))
    for row in controls['president_2024_county_controls']:
        line = text_by_id['official-2024-file-2'].split('\f')[0].splitlines()[row['line_1based'] - 1]
        ck(line == row['raw_line'])
        values = [int(v.replace(',', '')) for v in re.findall(r'(?<![\w.])-?\d[\d,]*(?![\w.])', line)]
        ck(values == row['county_values'] + [row['state']])
        ck(values[:-1] == [p['values'][row['csv_column_1based'] - 3] for p in independent['2024-president']['parents']])
    turnout = read(T / 'ballot-registration-extract.json')
    turnout_rows = 0
    for year, saved in turnout.items():
        raw = originals[saved['source_id']]
        html = raw.decode()
        ck(len(re.findall(r'<div class="county-precinct"', html)) == len(saved['native_rows']))
        for row in saved['native_rows']:
            fragment = html[row['source_char_start']:row['source_char_end']]
            ck(fragment.encode() == raw[row['source_byte_start']:row['source_byte_end']])
            text = LiteralText(fragment).text()
            ck(text == ' '.join([row['native_label'], row['ballots_cast_literal'], row['eligible_voters_literal']]))
            ck(row['ballots_cast'] == numeric(row['ballots_cast_literal']))
            ck(row['eligible_voters'] == numeric(row['eligible_voters_literal']))
            ck(row['registration_status'] is None and row['registration_asof'] is None and row['method'] is None)
            ck(row['key'] == 'nm:legacy:' + year + ':cty=' + row['county_id_literal'] + ':' + row['native_label'])
            turnout_rows += 1
        ck(len(saved['counties']) == 33)
        ck(sum(r['ballots_cast'] for r in saved['native_rows']) == saved['native_ballots_sum'] == saved['state_ballots_cast'])
        ck(sum(r['eligible_voters'] for r in saved['native_rows']) == saved['native_eligible_voters_sum'] == saved['state_eligible_voters'])
        service = json.loads(originals['turnout-' + year + '-county-service'])
        ck(service == controls['county_controls'][year]['county_service_raw_rows'])
        for parent in saved['counties']:
            kids = [r for r in saved['native_rows'] if r['county_literal'] == parent['county_literal']]
            published = next(r for r in service if r['CountyName'] == parent['county_literal'])
            ck(sum(r['ballots_cast'] for r in kids) == parent['ballots_cast_native_sum'] == int(published['calcVoterTurnout']))
            ck(sum(r['eligible_voters'] for r in kids) == parent['eligible_voters_native_sum'] == published['Voters'])
    ck(any(r['eligible_voters_literal'] == '-3' and r['eligible_voters'] == -3 for r in turnout['2022']['native_rows']))
    stocks = read(T / 'registration-stocks.json')
    stock_rows = 0
    for month, saved in stocks.items():
        for lane in ['state', 'county']:
            sid = saved[lane]['source_id']
            with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
                f.write(originals[sid]); f.flush()
                out = subprocess.run(['pdftotext', '-layout', f.name, '-'], capture_output=True, check=True).stdout
            ck(out == (T / 'source' / (sid + '.txt')).read_bytes())
            pages = out.decode().split('\f')
            for row in saved[lane]['rows']:
                line = pages[row['page'] - 1].splitlines()[row['line_1based'] - 1]
                ck(line == (row['raw_line'] if lane == 'state' else row['raw_lines'][0]))
                ck(row['registration_status'] is None)
                total = int(re.findall(r'\d[\d,]*', line)[-1 if lane == 'state' else -2].replace(',', ''))
                # County rows finish with an additional literal percentage, sometimes an integer.
                if lane == 'county':
                    header = next(x for x in pages[row['page'] - 1].splitlines() if x.startswith('PRECINCT') and 'DEMOCRATIC' in x)
                    tail = line[header.index('DEMOCRATIC'):]
                    values = [int(v.replace(',', '')) for v in re.findall(r'-?\d[\d,]*', tail)]
                    ck(row['counts'] == values[0:8:2] and row['total'] == values[8])
                    ck(sum(row['counts']) == row['total'])
                else:
                    ck(total == row['total'])
                    literal_counts = [int(v.replace(',', '')) for v in re.findall(r'(\d[\d,]*)\s+[\d.]+\s*%', line)]
                    ck([v for v in row['counts'] if v is not None] == literal_counts)
                stock_rows += 1
        ck(saved['state_report_total'] == next(r['total'] for r in saved['state']['rows'] if r['label_literal'] == 'TOTAL'))
        ck(saved['county_report_county_totals_sum'] == sum(r['total'] for r in saved['county']['rows'] if r['scope'] == 'county_total'))
        ck(saved['county_report_native_sum'] == sum(r['total'] for r in saved['county']['rows'] if r['scope'] == 'native'))
    witness = T / 'original-first-witness-v2.json'
    ck(digest(witness.read_bytes()) == '427ad9e10b16e85cc675f6479796f09813afa5a72845b1199d4dd6b4e8ae7c51')
    for name, row in read(witness)['files'].items():
        z = (T / name).read_bytes()
        ck(len(z) == row['bytes'] and digest(z) == row['sha256'])
    out = dict(status='pass_bounded_original_turnout_review_pending_actual_reciprocal', checks=N,
               handoff_manifest=pin(mf), original_first_witness=pin(witness),
               owned_listed_files=91, immutable_source_assets=63, receipt_objects=len(receipts),
               reconstructed_redirect_hops=hops, candidate_control_positions=positions,
               complete_native_ballot_eligible_rows=turnout_rows, complete_registration_stock_rows=stock_rows,
               complete_contest_native_rows={k: len(v['native']) for k, v in independent.items()},
               full_candidate_and_mask_literals_preserved=True, all_county_PDF_vectors_checked=True,
               independent_complete_candidate_scope=dict(rows=2181, denominator=902421, minimum80=1392,
                                                        cumulative=722113, preceding=721760, crossing='Valencia / 36'),
               canonical_certified_priority_unavailable=True, county_substitution_authorized=False,
               unknowns_allocated=False, producer_imports_or_writes=False,
               future_reciprocal_final_bytes_not_claimed=True,
               qualification='Protected source cells remain unknown; observations, privacy aggregates, county controls and actual ballot/registration publications remain separate. This immutable original-first audit does not admit certified native order, current identities, geometry, cadence, remaining pool or probability.')
    dst = S / 'data/coordinator-turnout-original-review.json'
    dst.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(dict(checks=N, proof=pin(dst))))


if __name__ == '__main__':
    main()

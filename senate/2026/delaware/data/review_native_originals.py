"""Coordinator original HTML/CSV replay, independent of question-worker parsers.

All methods and candidate strings are source observations. No parent inference,
write-in allocation, current geographic join or legal-universe approval.
"""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import csv
import gzip
import hashlib
import io
import json

D = Path(__file__).resolve().parent
S = D.parent
N = D / 'news'


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Tables(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.offsets = [0]
        for line in text.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.header = None
        self.heading = None
        self.table = None
        self.row = None
        self.cell = None
        self.tables = []
        self.feed(text)

    def at(self):
        line, col = self.getpos()
        return self.offsets[line - 1] + col

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ['h3', 'h4']:
            self.heading = dict(tag=tag, attrs=attrs, start=self.at(), text=[])
        if tag == 'table':
            self.table = dict(header=self.header, start=self.at(), attrs=attrs, rows=[])
        if tag == 'tr' and self.table is not None:
            self.row = dict(start=self.at(), cells=[])
        if tag in ['td', 'th'] and self.row is not None:
            self.cell = dict(tag=tag, attrs=attrs, start=self.at(), text=[])

    def handle_data(self, text):
        if self.heading is not None:
            self.heading['text'].append(text)
        if self.cell is not None:
            self.cell['text'].append(text)

    def handle_endtag(self, tag):
        if tag in ['h3', 'h4'] and self.heading is not None:
            self.heading['text'] = ''.join(self.heading['text']).strip()
            self.heading['end'] = self.at() + len(tag) + 3
            self.header = self.heading
            self.heading = None
        if tag in ['td', 'th'] and self.cell is not None:
            self.cell['text'] = ''.join(self.cell['text']).strip()
            self.cell['end'] = self.at() + len(tag) + 3
            self.row['cells'].append(self.cell)
            self.cell = None
        if tag == 'tr' and self.row is not None:
            self.row['end'] = self.at() + len(tag) + 3
            self.table['rows'].append(self.row)
            self.row = None
        if tag == 'table' and self.table is not None:
            self.table['end'] = self.at() + len(tag) + 3
            self.tables.append(self.table)
            self.table = None


def main():
    # Freeze exact individual original receipts; the appendable ledger is discovery only.
    pins_path = D / 'coordinator-original-report-pins.json'
    if pins_path.exists():
        pins = json.loads(pins_path.read_bytes())
    else:
        ledger = {e['id']: e for e in json.loads((N / 'manifest.json').read_bytes())}
        names = ['sos-2024-general-report', 'sos-2024-csv', 'sos-observed-2020-general-report',
                 'sos-observed-2020-state-csv', 'official-2022-report', 'sos-observed-2022-state-csv']
        pins = {key: ledger[key] for key in names}
        pins_path.write_text(json.dumps(pins, indent=2) + '\n')
    originals = {}
    parsed = {}
    for key, e in pins.items():
        stored = (N / e['asset']).read_bytes()
        raw = gzip.decompress(stored)
        assert sha(stored) == e['stored_sha256'] and sha(raw) == e['raw_sha256'] and len(raw) == e['bytes']
        originals[key] = raw
        if 'report' in key:
            parsed[key] = Tables(raw.decode('utf-8-sig')).tables
    contexts = [
        ('2024_SEN', 'sos-2024-general-report', 'sos-2024-csv', 'USSenator', 'U.S. Senator', 530, 500606),
        ('2024_PRES', 'sos-2024-general-report', 'sos-2024-csv', 'PresidentandVicePresident', 'President and Vice President', 533, 511697),
        ('2020_SEN', 'sos-observed-2020-general-report', 'sos-observed-2020-state-csv', 'USSenator', 'U.S. Senator', 436, 490935),
        ('2020_PRES', 'sos-observed-2020-general-report', 'sos-observed-2020-state-csv', 'PresidentandVicePresident', 'President and Vice President', 439, 504010),
        ('2022_HOUSE', 'official-2022-report', 'sos-observed-2022-state-csv', 'RepresentativeinCongress', 'Representative in Congress', 516, 321649),
    ]
    methods = {'Machine Votes': 'machinevotessum', 'Absentee Votes': 'absenteevotessum',
               'Early Voting Votes': 'earlyvotessum', 'Total Votes': 'totalvotessum'}
    output = {}
    checks = 0
    for key, report, source_csv, css, office, count, total in contexts:
        state = [r for r in csv.DictReader(io.StringIO(originals[source_csv].decode('utf-8-sig'))) if r['office'] == office]
        controls = {r['candidatename']: r for r in state}
        tables = [t for t in parsed[report] if t['header'] and css in t['header']['attrs'].get('class', '').split()]
        native = [t for t in tables if 'electiondistrict-title' in t['header']['attrs'].get('class', '').split()]
        assert len(native) == count
        sums, nulls = Counter(), Counter()
        units = []
        for table in native:
            cls = table['header']['attrs']['class'].split()
            source_key = next(x for x in cls if x.startswith('ElectionDistrict'))
            rows = []
            seen = set()
            for row in table['rows']:
                cells = {c['attrs']['data-label']: c for c in row['cells'] if c['tag'] == 'td' and 'data-label' in c['attrs']}
                if not cells:
                    continue
                name = cells['Candidate']['text']
                assert name in controls and name not in seen
                assert cells['Party']['text'] == controls[name]['partyname']
                seen.add(name)
                values = {method: int(cells[method]['text'].replace(',', '')) if method in cells else None for method in methods}
                assert sum(v for method, v in values.items() if method != 'Total Votes' and v is not None) == values['Total Votes']
                for method, v in values.items():
                    if v is None:
                        nulls[method] += 1
                    else:
                        sums[(name, method)] += v
                    checks += 1
                rows.append(dict(candidate=name, party=cells['Party']['text'], methods=values,
                                 literal_cells={k: v['text'] for k, v in cells.items()}, source_row_start=row['start']))
            assert seen == set(controls)
            units.append(dict(source_key=source_key, literal_header=table['header']['text'], table_start=table['start'],
                              table_end=table['end'], rows=rows, votes=sum(r['methods']['Total Votes'] for r in rows)))
        assert len({u['source_key'] for u in units}) == count
        for name, control in controls.items():
            for method, col in methods.items():
                assert sums[(name, method)] == int(control[col])
                checks += 1
        assert sum(u['votes'] for u in units) == total
        order = sorted(units, key=lambda u: (-u['votes'], u['source_key']))
        cumulative = 0
        crossing = None
        for rank, u in enumerate(order, 1):
            previous = cumulative
            cumulative += u['votes']
            if crossing is None and 5 * cumulative >= 4 * total:
                crossing = dict(rank=rank, source_key=u['source_key'], votes=u['votes'], preceding=previous, cumulative=cumulative)
        output[key] = dict(raw_report_source=report, source_raw_sha256=pins[report]['raw_sha256'],
                           state_CSV_complete_rows=state, selected_report_tables=len(tables), native_units=count,
                           methods_unprinted_null=dict(nulls), named_source_total=total, top15=sum(u['votes'] for u in order[:15]),
                           minimum80=crossing, full_source_order=[u['source_key'] for u in order], full_native_units=units)
    x = dict(status='pass_coordinator_original_HTML_parser_and_CSV_controls', original_receipts_path='coordinator-original-report-pins.json',
             candidate_method_and_state_checks=checks, contexts=output,
             source_limits='Complete original source bytes remain referenced once. This audit verifies named source votes/methods only; county/Wilmington/RD overlap is not added, no write-in allocation or county-parent/current identity inference. Unprinted2020early fields remain null.',
             current_geographic_or_legal_candidate_universe_approved=False)
    p = D / 'coordinator-native-original-review.json'
    b = (json.dumps(x, indent=2) + '\n').encode()
    if p.exists():
        assert p.read_bytes() == b
    else:
        p.write_bytes(b)
    print(json.dumps(dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b), checks=checks,
                          native_scopes={k: v['native_units'] for k, v in output.items()}, primary=output['2024_SEN']['minimum80'])))


if __name__ == '__main__':
    main()

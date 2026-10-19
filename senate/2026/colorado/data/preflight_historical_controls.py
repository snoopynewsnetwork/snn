"""Independent county controls from original public HTML and two archived PDFs."""
from pathlib import Path
from html.parser import HTMLParser
import gzip
import hashlib
import json
import re
import subprocess
import tempfile

DATA = Path(__file__).resolve().parent
NEWS = DATA / 'news'


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.level = 0
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.level += 1
        if self.level and tag == 'tr':
            self.row = []
        if self.level and tag in ['td', 'th']:
            self.cell = []

    def handle_data(self, value):
        if self.cell is not None:
            self.cell.append(value)

    def handle_endtag(self, tag):
        if self.level and tag in ['td', 'th'] and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()))
            self.cell = None
        if self.level and tag == 'tr' and self.row is not None:
            self.rows.append(self.row)
            self.row = None
        if tag == 'table':
            self.level -= 1


def main():
    manifest = json.loads((NEWS / 'manifest.json').read_bytes())
    pins = []

    def raw(sid):
        meta = next(x for x in manifest if x['id'] == sid)
        stored = (NEWS / meta['asset']).read_bytes()
        b = gzip.decompress(stored)
        assert hashlib.sha256(stored).hexdigest() == meta['stored_sha256']
        assert hashlib.sha256(b).hexdigest() == meta['raw_sha256'] and len(b) == meta['bytes']
        pins.append(dict(meta))
        return b

    tables = {}
    for sid in ['sos-2022-senate-abstract', 'sos-2022-governor-abstract']:
        p = Tables()
        p.feed(raw(sid).decode())
        header, rows, footer = p.rows[0], p.rows[1:-1], p.rows[-1]
        assert len(rows) == 64 and len({x[0] for x in rows}) == 64 and footer[0] == 'Total'
        records = []
        for ordinal, row in enumerate(rows, 1):
            assert len(row) == len(header)
            values = [int(v.replace(',', '')) for v in row[1:-1]]
            assert sum(values[2:-1]) == values[-1]
            records.append({'source_table_row': ordinal + 1, 'county_literal': row[0], 'raw_cells': row,
                            'registered_voters': values[0], 'ballots_cast': values[1],
                            'candidate_values': values[2:-1], 'candidate_total': values[-1]})
        for col in range(1, len(header) - 1):
            assert sum(int(x[col].replace(',', '')) for x in rows) == int(footer[col].replace(',', ''))
        tables[sid] = {'header_literal': header, 'footer_literal': footer, 'records': records}
    assert tables['sos-2022-senate-abstract']['footer_literal'][3:5] == ['1,397,170', '1,031,693']
    counties = {x['county_literal'] for x in tables['sos-2022-senate-abstract']['records']}

    def pdf_pages(sid):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'original.pdf'
            p.write_bytes(raw(sid))
            return subprocess.check_output(['pdftotext', '-layout', str(p), '-']).decode().split('\f')

    signed = pdf_pages('sos-2020-signed-archive')
    candidate_rows = []
    state = {}
    for page, text in enumerate(signed, 1):
        for line, value in enumerate(text.splitlines(), 1):
            if not value.startswith('United States Senator'):
                continue
            parts = re.split(r'\s{2,}', value.strip())
            if len(parts) == 5 and parts[2] in {c.upper() for c in counties}:
                candidate_rows.append({'page': page, 'line': line, 'raw_line': value, 'party_literal': parts[1],
                                       'county_literal': parts[2], 'candidate_literal': parts[3],
                                       'votes': int(parts[4].replace(',', ''))})
            elif len(parts) == 4 and parts[2].endswith(' Total Votes'):
                state[parts[2].removesuffix(' Total Votes')] = int(parts[3].replace(',', ''))
    assert len(candidate_rows) == 512 and len(state) == 8
    for candidate, votes in state.items():
        rows = [x for x in candidate_rows if x['candidate_literal'] == candidate]
        assert len(rows) == 64 and len({x['county_literal'] for x in rows}) == 64
        assert sum(x['votes'] for x in rows) == votes
    assert state['John W. Hickenlooper'] == 1731114 and state['Cory Gardner'] == 1429492

    booklet = pdf_pages('sos-2020-booklet-archive')
    left, right = {}, {}
    for text, target, width in [(booklet[105], left, 7), (booklet[106], right, 4)]:
        for line, value in enumerate(text.splitlines(), 1):
            parts = re.split(r'\s{2,}', value.strip())
            if parts[0] not in counties | {'Total'}:
                continue
            counts = parts[1:] if width == 7 else parts[1:-1]
            assert len(counts) == width
            target[parts[0]] = {'line': line, 'raw_line': value,
                                'values': [int(n.replace(',', '')) for n in counts]}
    assert set(left) == set(right) == counties | {'Total'}
    names = ['John W. Hickenlooper', 'Cory Gardner', 'Daniel Doyle', 'Stephan "Seku" Evans',
             'Raymon Anthony Doane', 'Danny Skelly', 'Bruce Lohmiller', 'Michael Sanchez']
    signed_lookup = {(x['county_literal'], x['candidate_literal']): x['votes'] for x in candidate_rows}
    for county in counties | {'Total'}:
        values = left[county]['values'][2:] + right[county]['values'][:3]
        assert sum(values) == right[county]['values'][3]
        for name, votes in zip(names, values):
            assert votes == (state[name] if county == 'Total' else signed_lookup[(county.upper(), name)])
    for table in [left, right]:
        for col in range(len(table['Total']['values'])):
            assert sum(table[c]['values'][col] for c in counties) == table['Total']['values'][col]

    index = raw('sos-2020-general-abstract-index').decode()
    assert 'General Election - November 6, 2020' in index
    renders = json.loads((NEWS / 'co-2020-rendered-pages.json').read_bytes())
    for row in renders:
        b = (DATA.parent / row['path']).read_bytes()
        assert hashlib.sha256(b).hexdigest() == row['sha256']
    out = {
        'status': 'pass_original_county_controls_native_and_priority_unaccepted',
        'source_pins': pins, 'HTML2022': tables,
        'signed2020': {'candidate_rows': candidate_rows, 'state_controls': state,
                       'candidate_total': sum(state.values()), 'signed_certificate_face_date': '2020-12-08'},
        'booklet2020': {'PDF_page106': left, 'PDF_page107': right,
                        'full_independent_candidate_comparisons_to_signed_original': 512},
        'complete_pages_independently_rendered_and_read': renders,
        'source_defects_and_limits': [
            '2020 general HTML index literally says November6,2020 and omits President/USSenator links; signed original and booklet say November3.',
            'Current exact2020 PDF URLs returned404; actual CDX-listed complete archived originals were recovered. Capture, PDF metadata and signed date are separate clocks.',
            '2022 named write-in headers and every candidate value remain literal. An unmarked UNA header is not automatically upgraded to legal write-in status.',
            'These are county controls, not complete native candidate/method coverage, an exact accepted priority, a current ballot universe or an approved geographic crosswalk.'
        ]
    }
    (DATA / 'coordinator-historical-controls-preflight.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'status': out['status'], 'counties_each_contest': 64, 'HTML2022_contests': 2,
                      'signed2020_candidate_cells': len(candidate_rows), 'PDF2020_comparisons': 512,
                      'Senate2020_total': sum(state.values())}))


if __name__ == '__main__':
    main()

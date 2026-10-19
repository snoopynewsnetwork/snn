"""Independent replay of the official HTML and linked original candidate XLSX."""
from pathlib import Path
from html.parser import HTMLParser
import gzip
import hashlib
import io
import json
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile

D = Path(__file__).resolve().parent
B = D / 'baselines'
S = D.parent
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def sha(value):
    return hashlib.sha256(value).hexdigest()


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.cell = None
        self.struck = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'tr':
            self.row = []
            self.struck = False
        if self.row is not None and tag in ['td', 'th']:
            self.cell = []
        if self.row is not None and (tag in ['s', 'strike', 'del'] or 'line-through' in attrs.get('style', '')):
            self.struck = True

    def handle_data(self, value):
        if self.cell is not None:
            self.cell.append(value)

    def handle_endtag(self, tag):
        if tag in ['td', 'th'] and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()))
            self.cell = None
        if tag == 'tr' and self.row is not None:
            self.rows.append(dict(fields=self.row, struck=self.struck))
            self.row = None


def main():
    receipts = {r['id']: r for r in json.loads((B / 'source/acquisition.json').read_bytes())}
    bodies = {}
    for name in ['current-candidates', 'current-candidates-xlsx']:
        r = receipts[name]
        stored = (B / r['path']).read_bytes()
        raw = gzip.decompress(stored)
        assert len(stored) == r['stored_bytes'] and sha(stored) == r['stored_sha256']
        assert len(raw) == r['bytes'] and sha(raw) == r['sha256'] and r['status'] == 200
        bodies[name] = raw
    page = Tables()
    page.feed(bodies['current-candidates'].decode())
    official = [row for row in page.rows if len(row['fields']) > 1 and row['fields'][1] == 'US Senate']
    assert len(official) == 9 and sum(x['fields'][4] == 'Y' for x in official) == 3
    assert not any(row['struck'] for row in official)
    archive = zipfile.ZipFile(io.BytesIO(bodies['current-candidates-xlsx']))
    assert archive.testzip() is None
    shared = [''.join(x.itertext()) for x in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('m:si', NS)]
    rels = {x.get('Id'): x.get('Target') for x in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
    senate = []
    for sheet in ET.fromstring(archive.read('xl/workbook.xml')).findall('m:sheets/m:sheet', NS):
        target = rels[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
        member = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        for row in ET.fromstring(archive.read(member)).findall('m:sheetData/m:row', NS):
            cells = []
            values = {}
            for cell in row.findall('m:c', NS):
                v = cell.find('m:v', NS)
                raw = v.text if v is not None else None
                decoded = shared[int(raw)] if cell.get('t') == 's' and raw is not None else raw
                cells.append(dict(attributes=dict(cell.attrib), raw_v=raw, decoded=decoded))
                values[re.sub(r'\d+$', '', cell.get('r'))] = decoded
            if values.get('B') == 'US Senate':
                senate.append(dict(source_row=row.get('r'), cells=cells))
    assert senate == json.loads((B / 'source/current-senate-spreadsheet-rows.json').read_bytes())
    assert [list(x['fields']) for x in official] == [[c['decoded'] for c in r['cells']] for r in senate]
    producer = json.loads((B / 'source/current-senate-roster.json').read_bytes())
    assert official == [{k: r[k] for k in ['fields', 'struck']} for r in producer['rows']]
    result = dict(status='pass_independent_official_candidate_HTML_XLSX_original_replay',
                  source_receipts=[receipts[k] for k in bodies], current_captured_official_Senate_rows=official,
                  independent_original_XLSX_rows=senate, complete_candidate_fields=45,
                  printed_candidates=6, certified_writein_records=3, stricken_rows=0,
                  source_list_clock=producer['source_updated_literal'],
                  current_live_choice_ID_or_generic_writein_allocation_approved=False,
                  limits='Official captured list and source flags, not historical-party aliases or vendor IDs. Generic Write-in setup fields do not allocate votes among the three named certified write-ins. Later signed roster/court changes and genuine November counts remain separate.')
    path = D / 'coordinator-current-roster-original-review.json'
    value = (json.dumps(result, indent=2) + '\n').encode()
    if path.exists():
        assert path.read_bytes() == value
    else:
        path.write_bytes(value)
    print(json.dumps(dict(path=str(path.relative_to(S)), bytes=len(value), sha256=sha(value))))


if __name__ == '__main__':
    main()

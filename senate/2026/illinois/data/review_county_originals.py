"""Independent stdlib original selector replay; complete counties remain sensitivities.

No producer parser or calculated total is imported. All read-only comparison
inputs are frozen once by hash; later producer metadata cannot change this audit.
"""
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json

D = Path(__file__).resolve().parent
B = D / 'baselines'
I = D / 'coordinator-county-review-inputs'


def sha(b):
    return hashlib.sha256(b).hexdigest()


class OriginalTables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = {}
        self.stack = []
        self.select = None
        self.option = None
        self.selected = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'select':
            self.select = a.get('id', '')
        if tag == 'option' and self.select:
            self.option = dict(attrs=a, text=[])
        if tag == 'table':
            table = dict(id=a.get('id'), rows=[], row=None, cell=None)
            self.stack.append(table)
            if table['id']:
                self.tables[table['id']] = table
        if not self.stack:
            return
        t = self.stack[-1]
        if tag == 'tr':
            t['row'] = []
        if tag in ['td', 'th'] and t['row'] is not None:
            t['cell'] = dict(text=[], hrefs=[])
        if tag == 'a' and t['cell'] is not None:
            t['cell']['hrefs'].append(a.get('href'))

    def handle_data(self, value):
        if self.option is not None:
            self.option['text'].append(value)
        if self.stack and self.stack[-1]['cell'] is not None:
            self.stack[-1]['cell']['text'].append(value)

    def handle_endtag(self, tag):
        if tag == 'option' and self.option is not None:
            if 'selected' in self.option['attrs']:
                self.selected[self.select] = dict(value=self.option['attrs']['value'],
                                                 label=' '.join(''.join(self.option['text']).split()))
            self.option = None
        if tag == 'select':
            self.select = None
        if not self.stack:
            return
        t = self.stack[-1]
        if tag in ['td', 'th'] and t['cell'] is not None:
            c = t['cell']
            t['row'].append(dict(text=' '.join(''.join(c['text']).split()), hrefs=c['hrefs']))
            t['cell'] = None
        if tag == 'tr' and t['row'] is not None:
            t['rows'].append(t['row'])
            t['row'] = None
        if tag == 'table':
            self.stack.pop()


def csvrows(b):
    return list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))


def freeze(name, raw):
    I.mkdir(exist_ok=True)
    p = I / (name+'-'+sha(raw)+'.gz')
    z = gzip.compress(raw, mtime=0)
    if p.exists():
        assert p.read_bytes() == z
    else:
        p.write_bytes(z)
    return dict(path=str(p.relative_to(D.parent)), stored_bytes=len(z),
                stored_sha256=sha(z), raw_bytes=len(raw), raw_sha256=sha(raw))


def load(pin):
    z = (D.parent / pin['path']).read_bytes()
    assert sha(z) == pin['stored_sha256'] and len(z) == pin['stored_bytes']
    raw = gzip.decompress(z)
    assert sha(raw) == pin['raw_sha256'] and len(raw) == pin['raw_bytes']
    return raw


def main():
    manifest = I / 'inputs.json'
    if not manifest.exists():
        candidates = (B / 'extract/county-candidate-source-rows.csv').read_bytes()
        county = (D / 'county-baselines.csv').read_bytes()
        source_ids = {r['source_id'] for r in csvrows(candidates)}
        registry = json.loads(gzip.decompress((B / 'source/registry.json.gz').read_bytes()))
        records = {r['id']: r for r in registry if r['id'] in source_ids}
        assert set(records) == source_ids
        input_pins = dict(candidates=freeze('candidate-comparison.csv', candidates),
                          county=freeze('county-comparison.csv', county),
                          complete_source_records=records)
        manifest.write_text(json.dumps(input_pins, indent=2)+'\n')
    inputs = json.loads(manifest.read_bytes())
    candidates = csvrows(load(inputs['candidates']))
    county = csvrows(load(inputs['county']))
    records = inputs['complete_source_records']
    groups = defaultdict(list)
    for row in candidates:
        groups[row['source_id']].append(row)
    original_counties = {}
    checks = 0
    for source_id, rows in groups.items():
        receipt = records[source_id]
        body = (B / receipt['path']).read_bytes()
        assert sha(body) == receipt['stored_sha256']
        raw = gzip.decompress(body)
        assert sha(raw) == receipt['raw_sha256'] and len(raw) == receipt['bytes']
        parser = OriginalTables()
        parser.feed(raw.decode('utf-8-sig'))
        selected = parser.selected['ContentPlaceHolder1_ddlJurisdictions']
        assert len({(r['year'],r['county_key']) for r in rows}) == 1
        year, key = rows[0]['year'], rows[0]['county_key']
        assert selected['value'] == key and selected['label'] == rows[0]['county']
        assert parser.selected['ContentPlaceHolder1_ddlElections']['label'] == year+' GENERAL ELECTION'
        values = []
        for row in rows:
            cells = parser.tables[row['table_id']]['rows'][int(row['table_row'])-1]
            assert len(cells) == 4
            assert [c['text'] for c in cells] == [row['candidate_literal'], row['party_literal'], row['votes_literal'], row['percentage_literal']]
            assert cells[0]['hrefs'] == [row['href_literal']]
            votes = int(cells[2]['text'].replace(',', ''))
            assert votes == int(row['votes'])
            values.append(dict(candidate=cells[0]['text'], party=cells[1]['text'], votes=votes,
                               percentage=cells[3]['text'], href=cells[0]['hrefs'][0],
                               table_id=row['table_id'], table_row=int(row['table_row'])))
            checks += 7
        original_counties[(year,key)] = dict(year=year, county_key=key, county=selected['label'],
                                            source_id=source_id, original_sha256=sha(raw),
                                            candidates=values, all_named=sum(r['votes'] for r in values))
    assert len(original_counties) == 306
    for row in county:
        own = original_counties[(row['year'], row['county_key'])]
        choices = {r['candidate']:r['votes'] for r in own['candidates']}
        assert int(row['A']) == choices[row['A_name']]
        assert int(row['B']) == choices[row['B_name']]
        assert int(row['pair_votes']) == choices[row['A_name']]+choices[row['B_name']]
        assert int(row['all_named_votes']) == own['all_named']
        assert int(row['other_named']) == own['all_named']-int(row['pair_votes'])
        checks += 5
    output = dict(schema='IL-coordinator-original-county-selector-review-v1',
                  status='pass_original_complete_county_candidate_rows', checks=checks,
                  county_views=306, literal_candidate_rows=len(candidates),
                  input_manifest=dict(path=str(manifest.relative_to(D.parent)),
                                      bytes=manifest.stat().st_size, sha256=sha(manifest.read_bytes())),
                  county_objects=list(original_counties.values()),
                  scope='102 combined counties per year are disjoint county sensitivity, not108 independent selector authorities or physical precincts. City selector pages have separate availability limits.',
                  native_writein_allocation_approved=False, geographic_approval=False,
                  final_coordinator_dispatch_acceptance=False)
    p = D / 'coordinator-county-original-review.json'
    b = json.dumps(output, indent=2, ensure_ascii=False).encode()+b'\n'
    p.write_bytes(b)
    print(json.dumps(dict(path=str(p.relative_to(D.parent)), bytes=len(b), sha256=sha(b), checks=checks,
                          county_views=306, original_candidate_rows=len(candidates))))


if __name__ == '__main__':
    main()

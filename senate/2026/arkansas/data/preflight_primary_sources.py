#!/usr/bin/env python3
"""Coordinator preparation: original 2024 workbook/PDF controls, not dispatch acceptance."""
from pathlib import Path
import collections
import datetime
import gzip
import hashlib
import io
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent
manifest = {r['id']: r for r in json.loads((ROOT/'news/manifest.json').read_text())}
def source(id):
    m = manifest[id]
    b = (ROOT/'news'/m['asset']).read_bytes()
    assert hashlib.sha256(b).hexdigest() == m['stored_sha256']
    raw = gzip.decompress(b)
    assert len(raw) == m['bytes'] and hashlib.sha256(raw).hexdigest() == m['raw_sha256']
    return raw

raw = source('sos-2024-general-precinct-original')
z = zipfile.ZipFile(io.BytesIO(raw))
assert z.testzip() is None
ns = {'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
strings = [''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
records = []
for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//s:row', ns):
    cells = {}
    for c in row:
        v = c.find('s:v', ns)
        value = v.text if v is not None else None
        if c.get('t') == 's':
            value = strings[int(value)]
        cells[re.sub(r'\d+$', '', c.get('r'))] = value
    records.append((int(row.get('r')), cells))
assert list(records[0][1].values()) == ['county','precinct','contest','choice','party','Election Day','Early Vote','Absentee','Provisional','total votes']
pres = [(n, r) for n, r in records[1:] if r.get('C') == 'U.S. President']
county_candidates = collections.defaultdict(collections.Counter)
candidate_methods = collections.defaultdict(collections.Counter)
units = set()
nonadditive = []
for n, r in pres:
    values = [int(r[c]) for c in 'FGHIJ']
    if sum(values[:4]) != values[4]:
        nonadditive.append({'source_row':n,'county':r['A'],'precinct':r['B'],'values':values})
    county_candidates[r['A']][r['D']] += values[4]
    candidate_methods[r['D']].update(dict(zip(['election_day','early_vote','absentee','provisional','total'], values)))
    units.add((r['A'],r['B']))
pdf = source('sos-2024-general-state-original')
text = subprocess.run(['pdftotext','-layout','-','-'], input=pdf, capture_output=True, check=True).stdout.decode()
section = text[text.index('U.S. President'):text.index('U.S. Congress District 01')]
columns = ['Peter Sonski/Lauren Onak','Kamala D. Harris/Tim Walz','Jill Stein/Rudolph Ware','Robert F. Kennedy, Jr./Nicole Shanahan','Chase Oliver/Mike ter Maat','Michael Wood/John G. Pietrowski','Donald J. Trump/JD Vance']
pdf_counties = {}
for line in section.splitlines():
    m = re.fullmatch(r'\s*([A-Za-z ]+?)\s+'+r'\s+'.join([r'([\d,]+)']*8)+r'\s*', line)
    if m and m[1].strip().upper() in county_candidates:
        name = m[1].strip().upper()
        values = [int(x.replace(',','')) for x in m.groups()[1:]]
        assert sum(values[:7]) == values[7]
        assert {c:values[i] for i,c in enumerate(columns)} == dict(county_candidates[name]), name
        pdf_counties[name] = values
assert len(pdf_counties) == len(county_candidates) == 75
out = {'status':'pass_preparation_only_not_dispatch_acceptance',
       'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'source_workbook_rows':len(records)-1,'presidential_source_rows':len(pres),
       'literal_counties':75,'source_native_county_precinct_pairs':len(units),
       'county_candidate_primary_pdf_comparisons':75*7,
       'candidate_methods':dict(candidate_methods),'nonadditive_method_rows':nonadditive,
       'zip_crc':'pass','source_votes':sum(sum(x.values()) for x in county_candidates.values()),
       'scope':'Independent 2024 president workbook/PDF cross-check only. No Senate2024 contest exists. Native physical/current approval, ballot controls and current candidates remain research gates. 2020 Senate Cotton versus Libertarian Harrington has no Democratic nominee; do not create one.'}
(ROOT/'coordinator-primary-preflight.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

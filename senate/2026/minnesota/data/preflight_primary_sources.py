"""Independent OOXML preflight; retained originals, no dispatch acceptance."""
import collections
import datetime
import gzip
import hashlib
import io
import json
import re
import subprocess
import xml.etree.ElementTree as E
import zipfile
from pathlib import Path

H = Path(__file__).resolve().parent
N = H / 'news'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
captures = {r['id']: r for r in json.loads((N / 'manifest.json').read_text())}


def raw(sid):
    m = captures[sid]
    b = (N / m['asset']).read_bytes()
    assert hashlib.sha256(b).hexdigest() == m['stored_sha256']
    b = gzip.decompress(b)
    assert len(b) == m['bytes'] and hashlib.sha256(b).hexdigest() == m['raw_sha256']
    return b


def workbook(sid):
    z = zipfile.ZipFile(io.BytesIO(raw(sid)))
    assert z.testzip() is None
    strings = [''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS)]
    rels = {r.attrib['Id']: r.attrib['Target'] for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    sheets = {}
    for sheet in E.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS):
        path = rels[sheet.attrib[R]]
        path = path.lstrip('/') if path.startswith('/') else 'xl/'+path
        rows = []
        for row in E.fromstring(z.read(path)).findall('s:sheetData/s:row', NS):
            cells = {}
            for cell in row:
                v = cell.find('s:v', NS)
                if cell.attrib.get('t') == 'inlineStr':
                    value = ''.join(cell.find('s:is', NS).itertext())
                elif v is None:
                    value = None
                else:
                    value = strings[int(v.text)] if cell.attrib.get('t') == 's' else v.text
                cells[cell.attrib['r']] = dict(value=value, type=cell.attrib.get('t'),
                                               formula=cell.findtext('s:f', namespaces=NS))
            rows.append(dict(source_id=sid, sheet=sheet.attrib['name'], source_row=int(row.attrib['r']), cells=cells))
        sheets[sheet.attrib['name']] = rows
    return sheets


result = {}
all_rows = []
for year, prefix in [(2024, 'USSEN'), (2022, 'MNGOV'), (2020, 'USSEN')]:
    sid = f'sos-{year}-precinct-original'
    sheets = workbook(sid)
    all_rows.extend(r for rs in sheets.values() for r in rs)
    rs = sheets['Precinct-Results']
    labels = [v['value'] for v in rs[0]['cells'].values()]
    duplicated = {x for x, n in collections.Counter(labels).items() if n > 1}
    header = {re.sub(r'\d+$', '', k): v['value']+('__'+re.sub(r'\d+$', '', k) if v['value'] in duplicated else '')
              for k, v in rs[0]['cells'].items()}
    records = []
    for row in rs[1:]:
        values = {header[re.sub(r'\d+$', '', k)]: v['value'] for k, v in row['cells'].items()}
        if values.get('VTDID') in [None, '', 'End of worksheet']:
            continue
        assert re.fullmatch(r'\d{9}', values['VTDID']), values['VTDID']
        values.update(source_row=row['source_row'], source_id=sid)
        records.append(values)
    counties = {r['COUNTYCODE']: r['COUNTYNAME'] for r in records}
    assert len(counties) == 87
    candidate_fields = [v for v in header.values() if v.startswith(prefix) and v != prefix+'TOTAL']
    for row in records:
        assert all(re.fullmatch(r'\d+', row.get(k, '')) for k in candidate_fields+[prefix+'TOTAL'])
        assert sum(int(row[k]) for k in candidate_fields) == int(row[prefix+'TOTAL'])
    counts = {k: sum(int(r[k]) for r in records) for k in candidate_fields}
    total = sum(counts.values())
    assert total == sum(int(r[prefix+'TOTAL']) for r in records)
    county = {name: sum(int(r[prefix+'TOTAL']) for r in records if r['COUNTYNAME'] == name) for name in counties.values()}
    ranked = sorted(county, key=lambda k: (-county[k], k))
    selected = []; cumulative = 0
    while cumulative*5 < total*4:
        selected.append(ranked[len(selected)]); cumulative += county[selected[-1]]
    result[str(year)] = dict(source_id=sid, original_sha256=captures[sid]['raw_sha256'],
                            original_bytes=captures[sid]['bytes'], native_rows=len(records),
                            unique_VTDID=len({r['VTDID'] for r in records}),
                            counties=87, candidate_fields=counts, reported_candidate_total=total,
                            provisional_top15=sum(county[k] for k in ranked[:15]),
                            provisional_min80_count=len(selected), provisional_min80_votes=cumulative,
                            previous_votes=cumulative-county[selected[-1]], crossing=selected[-1],
                            provisional_order=ranked, county_candidate_total=county,
                            duplicate_original_header_labels=sorted(duplicated),
                            column_to_derived_field=header,
                            literal_Notes=[r['cells'] for r in sheets['Notes']])
    (H / f'coordinator-{year}-native-preflight.jsonl.gz').write_bytes(gzip.compress(
        b''.join((json.dumps(r, ensure_ascii=False, separators=(',', ':'))+'\n').encode() for r in records), mtime=0))

assert result['2024']['candidate_fields'] == {'USSENR':1291712, 'USSENDFL':1792441,
                                            'USSENLIB':55215, 'USSENIA':46377, 'USSENWI':3578}
assert result['2022']['candidate_fields'] == {'MNGOVGLC':22599, 'MNGOVLMN':29346, 'MNGOVR':1119941,
                                            'MNGOVDFL':1312349, 'MNGOVIA':18156, 'MNGOVSWP':7241, 'MNGOVWI':1029}
pdf2020 = raw('sos-2020-canvass-original')
assert pdf2020.startswith(b'%PDF')
text2020 = subprocess.run(['pdftotext', '-layout', '-', '-'], input=pdf2020,
                          stdout=subprocess.PIPE, check=True).stdout.decode()
assert re.search(r'TOTAL\s+190,154\s+57,174\s+1,398,145\s+1,566,522', text2020)
assert result['2020']['candidate_fields'] == {'USSENLMN':190154, 'USSENGLC':57174,
                                            'USSENR':1398145, 'USSENDFL':1566522, 'USSENWI':2261}
(N / 'sos-2020-canvass-original.txt').write_text(text2020)
(H / 'coordinator-all-original-workbook-rows.jsonl.gz').write_bytes(gzip.compress(
    b''.join((json.dumps(r, ensure_ascii=False, separators=(',', ':'))+'\n').encode() for r in all_rows), mtime=0))
out = dict(status='pass_primary_preflight_only', checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
           contests=result, limits=['All primary OOXML rows/types/formulas retained; sources not rewritten.',
           'Direct landing200 may be Radware challenge; actual XLSX originals are ZIP/CRC verified.',
           '2024 original warns Signatures/AB_MB splits in Clearwater, Swift, Winona may be incorrect; do not treat as a clean method split.',
           'Generic write-in field is not demonstrated valid named candidate allocation; under/over categories absent remain unknown.',
           'VTDID/precinct code/municipality/ward/ballot statistics remain source fields, not current2026 crosswalk approval.',
           'Independent actual first-wave extraction and full candidate/source/FIPS reconciliation required before priority acceptance.'])
p = H / 'coordinator-primary-preflight.json'
if p.exists():
    previous = json.loads(p.read_text())
    if {k:v for k,v in previous.items() if k != 'checked_utc'} == {k:v for k,v in out.items() if k != 'checked_utc'}:
        out['checked_utc'] = previous['checked_utc']
p.write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps({year:{k:v for k,v in r.items() if k not in ['provisional_order','county_candidate_total','literal_Notes','column_to_derived_field']} for year,r in result.items()}, indent=2))

"""Inspect recovered SOS originals; no research-priority approval.

Requires xlrd 2.0.2 installed outside the repository and pdftotext. Raw BIFF
types and all rows remain available, including blank territory labels.
"""
import datetime
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path
import xlrd

H = Path(__file__).resolve().parent
N = H / 'news'
manifest = {r['id']: r for r in json.loads((N / 'manifest.json').read_text())}


def original(sid):
    m = manifest[sid]
    stored = (N / m['asset']).read_bytes()
    assert hashlib.sha256(stored).hexdigest() == m['stored_sha256']
    b = gzip.decompress(stored)
    assert len(b) == m['bytes'] and hashlib.sha256(b).hexdigest() == m['raw_sha256']
    return b


def identify(label):
    for name in ['Bolduc', 'Hassan', 'Kauffman', 'Scatter']:
        if name.lower() in label.lower():
            return name
    raise ValueError(label)


results = []
all_rows = []
all_native = []
for suffix in ['', '-1', '-2', '-5']:
    sid = 'sos-archived-2022-ge-us-senator'+suffix+'-xls'
    b = original(sid)
    assert b.startswith(bytes.fromhex('d0cf11e0a1b11ae1'))
    book = xlrd.open_workbook(file_contents=b, formatting_info=True)
    summary_sheet = book.sheet_by_index(0)
    summary_names = [identify(str(x)) for x in summary_sheet.row_values(2)[1:5]]
    controls = {str(summary_sheet.cell_value(i, 0)).strip():
                dict(zip(summary_names, summary_sheet.row_values(i)[1:5])) for i in range(3, 14)}
    native = []
    footers = []
    for sheet in book.sheets():
        county = None
        headers = None
        for i in range(sheet.nrows):
            values = sheet.row_values(i)
            types = list(sheet.row_types(i))
            all_rows.append(dict(source_id=sid, sheet=sheet.name, source_row=i+1,
                                 values=values, BIFF_cell_types=types))
            label = str(values[0]).strip()
            if label.endswith(' County'):
                county = label.removesuffix(' County')
                headers = [identify(str(x)) for x in values[1:5]]
                continue
            if county is None or not label:
                continue
            if label == 'TOTALS':
                footers.append(dict(county=county, sheet=sheet.name, source_row=i+1,
                                    candidate_counts=dict(zip(headers, values[1:5]))))
                county = None
                continue
            native.append(dict(source_id=sid, sheet=sheet.name, source_row=i+1,
                               county_label=county, native_label=values[0],
                               candidate_counts=dict(zip(headers, values[1:5])),
                               BIFF_cell_types=dict(zip(headers, types[1:5]))))
    assert len(footers) == 10
    comparisons = []
    for footer in footers:
        ns = [r for r in native if r['county_label'] == footer['county']]
        numeric = {k: sum(r['candidate_counts'][k] for r in ns
                          if isinstance(r['candidate_counts'][k], (int, float)))
                   for k in summary_names}
        comparisons.append(dict(county=footer['county'], numeric_detail_sums=numeric,
                                footer=footer['candidate_counts'], summary=controls[footer['county']],
                                detail_matches_footer=numeric == footer['candidate_counts'],
                                footer_matches_summary=footer['candidate_counts'] == controls[footer['county']]))
    all_native.extend(native)
    results.append(dict(source_id=sid, original_sha256=manifest[sid]['raw_sha256'], original_bytes=len(b),
                        worksheets=book.sheet_names(), native_labeled_rows=len(native),
                        summary_headers=summary_names, summary_state=controls['TOTALS'],
                        county_comparisons=comparisons))

final = results[-1]
assert all(r['detail_matches_footer'] and r['footer_matches_summary'] for r in final['county_comparisons'])
assert final['summary_state'] == {'Hassan': 332490, 'Bolduc': 275631, 'Kauffman': 12390, 'Scatter': 464}
pdfid = 'sos-archived-2022-ge-us-senator-remediated-1-pdf'
text = subprocess.run(['pdftotext', '-layout', '-', '-'], input=original(pdfid),
                      check=True, stdout=subprocess.PIPE).stdout.decode()
(N / 'sos-2022-senate-remediated-archived-original.txt').write_text(text)
first = text.split('Belknap County', 1)[0]
for row in final['county_comparisons']:
    matches = re.findall(r'^'+re.escape(row['county'])+r'\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$', first, re.M)
    assert len(matches) == 1, row['county']
    counts = dict(zip(['Bolduc', 'Hassan', 'Kauffman', 'Scatter'],
                      [int(v.replace(',', '')) for v in matches[0]]))
    assert counts == row['summary']

pdf2020 = original('sos-2020-senate-archived-original')
text2020 = subprocess.run(['pdftotext', '-layout', '-', '-'], input=pdf2020,
                          check=True, stdout=subprocess.PIPE).stdout.decode()
(N / 'sos-2020-senate-archived-original.txt').write_text(text2020)
state2020 = re.search(r'^TOTALS\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)', text2020, re.M)
assert state2020 and [int(x.replace(',', '')) for x in state2020.groups()] == [326229, 450778, 18421, 486]

for filename, records in [('coordinator-2022-all-vintage-raw-rows.jsonl.gz', all_rows),
                          ('coordinator-2022-all-vintage-native-rows.jsonl.gz', all_native)]:
    payload = b''.join((json.dumps(r, ensure_ascii=False, separators=(',', ':'))+'\n').encode() for r in records)
    (H / filename).write_bytes(gzip.compress(payload, mtime=0))
out = dict(status='pass_primary_vintage_preflight_only',
           checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
           source_vintages=results, final_2022_named_plus_scatter=620975,
           final_2022_pdf_all_10_counties_match=True,
           original_2020_senate_state=dict(Messner=326229, Shaheen=450778, ODonnell=18421, Scatter=486),
           limits=['Current direct SOS downloads remain blocked; archived original bytes retained.',
                   '2022 summary _5 candidate columns reverse Bolduc/Hassan compared with older summaries and its own detail headers; map by actual headers.',
                   'Earlier vintages differ in Coos, Grafton and other counties; numeric differences do not prove a correction cause or release chronology.',
                   'Native blanks/types and overlapping summary/footer controls remain separate; no imputed zero, accepted priority or current crosswalk.',
                   '2020 PDF state controls verified here; complete independent native extraction remains assigned to actual first-wave workers.'])
p = H / 'coordinator-senate-vintage-preflight.json'
if p.exists():
    old = json.loads(p.read_text())
    if {k:v for k,v in old.items() if k != 'checked_utc'} == {k:v for k,v in out.items() if k != 'checked_utc'}:
        out['checked_utc'] = old['checked_utc']
p.write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(dict(status=out['status'], native_rows_per_vintage=[r['native_labeled_rows'] for r in results],
                      final_2022_state=final['summary_state'], all_10_county_PDF_controls_match=True)))

#!/usr/bin/env python3
"""Original fixed-width export controls; no research dispatch acceptance."""
from pathlib import Path
import collections
import gzip
import hashlib
import io
import json
import subprocess
import zipfile

D = Path(__file__).resolve().parent
N = D / 'news'
mf = {r['id']: r for r in json.loads((N / 'manifest.json').read_text())}
sha = lambda b: hashlib.sha256(b).hexdigest()
def body(id):
    m = mf[id]
    z = (N / m['asset']).read_bytes()
    b = gzip.decompress(z)
    assert sha(z) == m['stored_sha256'] and sha(b) == m['raw_sha256']
    return b

archives = {}
for id in ['ri-2024-original-data-zip', 'ri-2024-layout-zip']:
    z = zipfile.ZipFile(io.BytesIO(body(id)))
    assert z.testzip() is None
    archives[id] = z
inventories = {id: [{'ordinal': i, 'name': x.filename, 'bytes': x.file_size,
                      'sha256': sha(z.read(x.filename)), 'CRC': x.CRC, 'ZIP_member_timestamp': x.date_time}
                     for i, x in enumerate(z.infolist())] for id, z in archives.items()}
longzip = archives['ri-2024-layout-zip']
shortzip = archives['ri-2024-original-data-zip']
views = {}
all_rows = {}
for label, longname, shortname in [
    ('nested_results', 'rigen2024l/rigen2024l_results.txt', 'rigen2024/rigen2024s_results.txt'),
    ('root_results', 'rigen2024l.txt', 'rigen2024.txt'),
    ('setup', 'rigen2024l/rigen2024l_setup.txt', 'rigen2024/rigen2024s_setup.txt'),
]:
    rows = longzip.read(longname).decode().splitlines()
    shortrows = shortzip.read(shortname).decode().splitlines()
    assert len(rows) == len(shortrows) == 20921
    assert all(len(r) == 263 for r in rows) and all(len(r) == 101 for r in shortrows)
    assert [r[:101] for r in rows] == shortrows
    assert len({r[:11] for r in rows}) == len(rows)
    selected = []
    for i, s in enumerate(rows):
        if s[:4] not in ['0001', '0002']:
            continue
        total = int(s[11:17])
        groups = [int(s[j:j+6]) for j in range(17, 101, 6)]
        assert sum(groups) == total
        selected.append({'source_row': i + 1, 'contest_id': s[:4], 'candidate_id': s[4:7],
                         'native_code': s[7:11], 'total': total, 'groups': groups,
                         'party_literal': s[101:104], 'contest_title': s[111:167],
                         'candidate_name': s[167:205], 'native_name': s[205:235],
                         'district_name': s[235:260], 'votes_allowed': s[260:262], 'referendum_flag': s[262]})
    controls = collections.Counter()
    units = collections.defaultdict(set)
    for r in selected:
        controls[(r['contest_id'], r['candidate_id'], r['candidate_name'].strip())] += r['total']
        units[r['contest_id']].add((r['native_code'], r['native_name']))
    views[label] = {'long_member': longname, 'short_member': shortname, 'all_source_rows': len(rows),
                    'selected_candidate_rows': len(selected), 'native_units': {k: len(v) for k,v in units.items()},
                    'state_candidate_controls': [{'contest': k[0], 'candidate_code': k[1], 'name': k[2], 'votes': v}
                                                 for k,v in controls.items()]}
    all_rows[label] = selected

root = {(r['contest_id'],r['candidate_id'],r['native_code']):r for r in all_rows['root_results']}
old = {(r['contest_id'],r['candidate_id'],r['native_code']):r for r in all_rows['nested_results']}
assert set(root) == set(old)
changes = [{'key': k, 'native_name': r['native_name'], 'candidate_name': r['candidate_name'],
            'root_votes': r['total'], 'nested_votes': old[k]['total'],
            'difference': r['total'] - old[k]['total'], 'root_groups': r['groups'], 'nested_groups': old[k]['groups']}
           for k,r in root.items() if r['total'] != old[k]['total'] or r['groups'] != old[k]['groups']]
units = {c: {(r['native_code'],r['native_name']) for r in all_rows['root_results'] if r['contest_id']==c}
         for c in ['0001', '0002']}
assert len(units['0001']) == 497 and len(units['0002']) == 458
assert len(units['0001'] - units['0002']) == 39 and not units['0002'] - units['0001']
pdf = subprocess.run(['pdftotext','-layout','-','-'], input=body('boe-2024-summary'), capture_output=True, check=True).stdout.decode()
for v in ['285,156','214,406','294,665','196,039','491,948','513,386','507,861','517,231']:
    assert v in pdf
out = {'status': 'primary_preflight_only_with_retained_export_vintages',
       'sources': {k: {'url': mf[k]['url'], 'raw_sha256': mf[k]['raw_sha256'], 'retrieved_at_utc': mf[k]['retrieved_at_utc']}
                   for k in ['ri-2024-original-data-zip','ri-2024-layout-zip','ri-2022-description','boe-2024-summary']},
       'ZIP_member_inventories': inventories, 'views': views, 'root_minus_nested_candidate_changes': changes,
       'presidential_only_native_units_not_in_senate': [{'code': c, 'literal_name': n} for c,n in sorted(units['0001'] - units['0002'])],
       'summary_source_clock': 'Election Summary - 12/03/2024 11:19AM; timezone unspecified',
       'source_scope': ['Root long/short files agree field-for-field and match selected primary December3summary candidate controls; nested _results long/short also agree but have earlier/different counts.',
                        'Setup files are literal zero controls; do not admit them as returns. Complete ZIPs preserve duplicate/nested/member metadata without following embedded quarantine links.',
                        '497president units and458Senate units differ by39sourcecodes; no omitted Senate row is synthesized and no legal reason or physical boundary inferred.',
                        'Presidential contest total517231 vs Senate507861 and different reporting denominators are source-specific; percentages do not measure remaining valid Senate votes.',
                        'Generic write-in categories remain separate from a demonstrated valid named allocation; full native current geometry and39municipal authority relationships require actual question workers.',
                        'First three group labels ElectionDay/Mail/Early come from the actually linked2022formatPDF; additional group IDs remain literal. No2026feed, priority or geography approval.']}
(D/'coordinator-primary-preflight.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'views': views, 'changed_candidate_positions': len(changes),'president_only_units':39},indent=2))

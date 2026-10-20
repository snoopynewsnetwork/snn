"""Independent complete source-envelope/schema and sealed official package audit.

Run only after the actual finish handoff, passing its exact manifest SHA256.
No producer imports/writers, source refresh, feed admission or legal approval.
"""
from pathlib import Path
from collections import Counter
from xml.etree import ElementTree as ET
import csv
import gzip
import hashlib
import io
import json
import subprocess
import sys
import zipfile

S = Path(__file__).resolve().parents[1]
H = S / 'data/results-sources'
N = 0


def ck(v, note=''):
    global N
    assert v, note
    N += 1


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def body(b):
    chunks = []
    for r in b.get('parts', [b]):
        z = (H / r['path']).read_bytes()
        ck(len(z) == r['stored_bytes'] < 40000000 and sha(z) == r['stored_sha256'])
        raw = gzip.decompress(z)
        ck(len(raw) == r['raw_bytes'] and sha(raw) == r['raw_sha256'])
        chunks.append(raw)
    raw = b''.join(chunks)
    ck(len(raw) == b['raw_bytes'] and sha(raw) == b['raw_sha256'])
    if 'parts' in b:
        ck([p['byte_start'] for p in b['parts']] == [sum(x['raw_bytes'] for x in b['parts'][:i]) for i in range(len(b['parts']))])
    return raw


def xtree(e):
    return dict(tag=e.tag, attributes=e.attrib, text=e.text, tail=e.tail, children=[xtree(c) for c in e])


def main():
    ck(len(sys.argv) == 2 and len(sys.argv[1]) == 64, 'actual final handoff manifest digest required')
    mf_path = H / 'asset-manifest.json'
    ck(sha(mf_path.read_bytes()) == sys.argv[1])
    mf = read(mf_path)
    ck(mf['excludes_only'] == 'data/results-sources/asset-manifest.json')
    actual = {str(p.relative_to(S)) for p in H.rglob('*') if p.is_file() and p != mf_path}
    actual |= {'official-results.md', 'data/official-results-sources.csv'}
    ck(actual == {r['path'] for r in mf['owned']} and len(actual) == len(mf['owned']))
    for r in mf['owned']:
        p = S / r['path']
        ck(pin(p) == r, r['path'])
        ck(r['bytes'] < 40000000 and '__pycache__' not in p.parts and p.suffix != '.pyc')
    deps = read(H / 'readonly-inputs.json')
    for r in deps:
        ck(pin(S / r['path']) == r)
    print('complete official seal/dependency pins pass', len(mf['owned']), len(deps), flush=True)
    c = read(S / 'data/turnout/priority-set.json')
    p = read(H / 'priority-investigations.json.gz')
    rem = read(H / 'remainder-investigations.json.gz')
    rows = p + rem
    ck((len(p), len(rem)) == (1470, 924))
    ck([r['complete_frozen_order_object'] for r in rows] == c['all_unit_order'])
    ck([r['complete_original_source_record'] for r in rows] == [r['source_record'] for r in c['all_unit_order']])
    ck([r['historical_native_key'] for r in rows] == c['ordered_priority_keys'] + c['ordered_remainder_keys'])
    hierarchy = read(H / 'all-parent-hierarchy.json.gz')
    ck(len(hierarchy['parents']) == 351 and sum(p['priority_parent'] for p in hierarchy['parents']) == 287)
    ck([p['all_source_child_arrays'] for p in hierarchy['parents']] == c['all_parent_child_maps'])
    for parent in hierarchy['parents']:
        x = read(H / parent['investigation'])
        ck(x['historical_parent_full_object'] == parent['all_source_child_arrays'])
        ck(x['current']['current_admission'] is False and x['current']['eligible_unprocessed_votes'] is None)
        ck(not x['secretary_local_election_directory']['raw_field_completeness'])
        for chain in x['bounded_chain_requests']:
            ck((H / chain['receipt']).is_file())
    for r in rows:
        ck(r['current']['returns_admitted'] is False)
        ck(all(v is None for k, v in r['current'].items() if k != 'returns_admitted'))
    with (S / 'data/official-results-sources.csv').open(newline='') as f:
        directory = list(csv.DictReader(f))
    ck(len(directory) == 355 and sum(r['authority_scope'] == 'municipal research parent' for r in directory) == 351)
    for r in directory:
        ck((H / r['authority_investigation']).is_file())
        ck(r['current_November_returns_admitted'] == 'false' and r['known_eligible_remaining_votes'] == '')
    receipts = [read(p) for p in sorted((H / 'source/http').glob('*.json'))]
    entities = {}
    redirects = 0
    for r in receipts:
        ck(all(k in r for k in ['method', 'query', 'request_body', 'parent', 'literal_href', 'started_utc', 'requested_url', 'final_url', 'status', 'error', 'redirects']))
        for hop in r['redirects']:
            ck(all(k in hop for k in ['requested_url', 'final_url', 'utc', 'status', 'request_headers', 'response_headers', 'body']))
            redirects += 1
        for b in [r.get('body'), *[h.get('body') for h in r['redirects']]]:
            if b and b['raw_sha256'] not in entities:
                raw = body(b)
                entities[b['raw_sha256']] = len(raw)
    print('all official complete response/redirect entities reconstructed', len(entities), flush=True)
    index = read(H / 'structure-index.json')
    formats = Counter()
    workbook_members = 0
    from bs4 import BeautifulSoup
    for r in index['responses']:
        z = read(H / r['structure'])
        raw = body(z['original_body'])
        ck(sha(raw) == r['body_sha256'])
        formats[z['format']] += 1
        if z['format'] == 'JSON':
            ck(z['complete_response'] == json.loads(raw))
        elif z['format'] == 'JavaScript':
            ck(z['complete_text'] == raw.decode('utf-8', 'replace'))
        elif z['format'] == 'PDF':
            ck(z['pages'] == z['text'].split('\f'))
        elif z['format'] == 'XLSX':
            archive = zipfile.ZipFile(io.BytesIO(raw))
            ck(archive.testzip() is None and archive.namelist() == [m['name'] for m in z['members']])
            for m in z['members']:
                b = archive.read(m['name'])
                ck(len(b) == m['bytes'] and sha(b) == m['sha256'])
                if m.get('tree') is not None:
                    ck(xtree(ET.fromstring(b)) == m['tree'])
                workbook_members += 1
        elif z['format'] == 'HTML':
            soup = BeautifulSoup(raw, 'html.parser')
            tables = soup.find_all('table')
            ck(len(tables) == len(z['tables']))
            for table, saved in zip(tables, z['tables']):
                ck(dict(table.attrs) == saved['attributes'])
                ck(saved['caption'] == (table.caption.get_text() if table.caption else None))
                rr = table.find_all('tr')
                ck(len(rr) == len(saved['rows']))
                for tr, sr in zip(rr, saved['rows']):
                    ck(dict(tr.attrs) == sr['attributes'])
                    cells = tr.find_all(['th', 'td'], recursive=False)
                    ck(len(cells) == len(sr['cells']))
                    for cell, sc in zip(cells, sr['cells']):
                        ck(cell.name == sc['tag'] and dict(cell.attrs) == sc['attributes'])
                        ck(cell.get_text() == sc['raw_text'] and cell.get_text(' ', strip=True) == sc['text'])
            scripts = soup.find_all('script')
            ck(len(scripts) == len(z['scripts']))
            for script, saved in zip(scripts, z['scripts']):
                ck(dict(script.attrs) == saved['attributes'] and script.get_text() == saved['inline_text'])
            forms = soup.find_all('form')
            ck(len(forms) == len(z['forms']))
            for form, saved in zip(forms, z['forms']):
                ck(dict(form.attrs) == saved['attributes'])
                fields = form.find_all(['input', 'select', 'option', 'button', 'textarea'])
                ck(len(fields) == len(saved['fields']))
                for field, recorded in zip(fields, saved['fields']):
                    ck(recorded == dict(tag=field.name, attributes=dict(field.attrs), text=field.get_text()))
            ck([dict(m.attrs) for m in soup.find_all('meta')] == z['meta'])
    ck(len(index['historical_csv']) == 8)
    raw_records = 0
    for r in index['historical_csv']:
        raw = gzip.decompress((S / r['body_path']).read_bytes())
        parsed = list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
        z = read(H / r['structure'])
        ck(parsed == z['all_records_including_ragged_headers_party_rows_blanks_and_footer'])
        ck(list(map(len, parsed)) == z['record_lengths'])
        raw_records += len(parsed)
    coverage = read(H / 'coverage.json')
    ck(coverage['priority_parent_HTTP_attempts'] == 287 and coverage['actual_response_receipts'] == len(receipts))
    ck(coverage['response_statuses'] == dict(Counter(str(r['status']) for r in receipts)))
    ck(coverage['complete_structural_samples'] == dict(formats))
    q = read(H / 'current-qualification.json')
    ck(not q['current_returns_admitted'] and all(v is None for v in q['current_native_ids'].values()))
    ck(q['eligible_unprocessed_votes'] is None and q['measured_cadence'] is None)
    ck(read(H / 'validation.json')['status'] == 'pass')
    out = dict(status='pass_independent_complete_official_source_schema_envelope_and_seal_review', checks=N,
               manifest=pin(mf_path), owned_entries=len(mf['owned']), immutable_dependencies=len(deps),
               complete_source_observations=len(rows), priority=1470, remainder=924,
               municipal_inventory=351, priority_parents=287, authority_inventory_rows=len(directory),
               complete_response_receipts=len(receipts), complete_response_hops=redirects,
               complete_distinct_raw_entities=len(entities), raw_entity_bytes=sum(entities.values()),
               source_format_counts=dict(formats), whole_workbook_members=workbook_members,
               full_original_CSVs=8, full_original_CSV_records=raw_records,
               complete_historical_independent_proof=pin(S / 'data/coordinator-acceptance-validation.json'),
               worker_full_historical_reconstruction=pin(H / 'reconstruction.json'),
               current_directory_incomplete_explicit=True, no_producer_import_or_write=True,
               all_current_joins_returns_cadence_remainder_approvals=False,
               qualification='All351 historical municipal inventories retained; actual bounded requests at287priority parents do not establish complete current-directory access, live feeds or current identifiers. Secretary directory403/indexed fragments, wrong-parent negative evidence and all precise legal/roster/docket qualifications survive. PDF fulltext boundaries checked here; selected actual visual scope is separately pinned, with no whole-inventory visual claim.')
    p = S / 'data/coordinator-official-final-review.json'
    p.write_text(json.dumps(out, indent=2)+'\n')
    print(dict(checks=N, proof=pin(p)))


if __name__ == '__main__':
    main()

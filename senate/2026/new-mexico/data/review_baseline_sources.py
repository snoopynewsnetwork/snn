"""Complete original-byte baseline audit, run after actual final seal handoff.

The argument must be the actual final manifest SHA256; no producer imports.
"""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import sys
from review_turnout_originals import NextData, numeric

S = Path(__file__).resolve().parents[1]
B = S/'data/baselines'
N = 0


def ck(value, note=''):
    global N
    assert value, note
    N += 1


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))


def read(p):
    return json.loads(p.read_bytes())


def main():
    ck(len(sys.argv) == 2 and len(sys.argv[1]) == 64)
    mp = B/'asset-manifest.json'
    ck(sha(mp.read_bytes()) == sys.argv[1])
    m = read(mp)
    actual = {str(p.relative_to(S)) for p in B.rglob('*') if p.is_file() and p != mp}
    actual |= {'county-partisanship.md','data/county-baselines.csv'}
    ck(actual == {r['path'] for r in m['owned']} and len(actual) == len(m['owned']))
    for r in m['owned'] + m['external_original_assets']:
        ck(pin(S/r['path']) == {k:r[k] for k in ['path','bytes','sha256']}, r['path'])
        ck(r['bytes'] < 40000000 and not any(k in Path(r['path']).parts for k in ['__pycache__','.venv','node_modules']))
    ip = B/'source/independent-first-pin.json'
    ck(sha(ip.read_bytes()) == '6770ae96313d9f9d2e0964da2470fd903d1f72122e260eece7635370aca014b7')
    for r in read(ip)['files']:
        ck(pin(S/r['path']) == r, r['path'])
    receipts = read(B/'source/original-references.json')
    byid = {r['id']:r for r in receipts}
    ck(len(byid) == len(receipts))
    def body(source):
        r = byid[source]
        z = (S/r['asset']).read_bytes()
        ck(sha(z) == r['stored_sha256'])
        b = gzip.decompress(z)
        ck(len(b) == r['bytes'] and sha(b) == r['raw_sha256'])
        return b
    e = read(B/'original-extract.json')
    full = {}
    native = {}
    for tag,v in e.items():
        b = body(v['source_id'])
        rr = list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
        ck(v['headers'] == rr[0] and v['parties'] == rr[1])
        ck(v['raw_sha256'] == sha(b) and [r['raw_row'] for r in v['rows']] == rr[2:])
        js = NextData(body(v['page_source_id']))
        ck(read(B/'source'/v['page_data_path']) == json.loads(''.join(js.fragments)))
        county = None
        for no,(r,raw) in enumerate(zip(v['rows'],rr[2:]),3):
            ck(r['source_row'] == no and r['scope'] == raw[0] and r['label_literal'] == raw[1])
            if raw[0] == 'County':
                county = raw[1]
            ck(r['county_literal'] == (None if raw[0] == 'State' else county))
            ck(len(r['cells']) == len(raw))
            ck(r['administrative'] == (raw[0] == 'Precinct' and raw[1] == 'Voter Privacy'))
            for col,(cell,literal) in enumerate(zip(r['cells'],raw),1):
                ck(cell == dict(column=col,header=rr[0][col-1],party_literal=rr[1][col-1],literal=literal,value=numeric(literal),masked=literal=='*'))
            full[tag,no] = r
        native[tag] = sum(r['scope'] == 'Precinct' for r in v['rows'])
    ck(native == {'2024-senate':2201,'2020-senate':1959,'2022-governor':2196,'2024-president':2202})
    with (B/'candidate-fields.csv').open(newline='') as f:
        fields = list(csv.DictReader(f))
    ck(len(fields) == 50179)
    ck(len({(r['contest'],r['source_row'],r['source_column']) for r in fields}) == len(fields))
    for row in fields:
        original = full[row['contest'],int(row['source_row'])]
        cell = original['cells'][int(row['source_column'])-1]
        ck(row['scope'] == original['scope'] and row['county'] == (original['county_literal'] or ''))
        ck(row['native_label'] == original['label_literal'] and row['administrative'] == str(original['administrative']))
        ck(row['field_label'] == cell['header'] and row['party_literal'] == cell['party_literal'])
        ck(row['literal'] == cell['literal'] and row['masked'] == str(cell['masked']))
        ck(row['value'] == (str(cell['value']) if cell['value'] is not None else ''))
        ck(row['source_id'] == e[row['contest']]['source_id'])
    pri = read(B/'priority-contract.json')
    ck(set(pri) == set(e))
    for tag,v in pri.items():
        ck(v['canonical_dispatch_keys'] == [] and v['certified_native_order'] is None and v['certified_native_minimum80'] is None and v['certified_native_top15'] is None)
        ck(v['complete_source_native_row_count'] == native[tag])
    out = dict(status='pass_independent_complete_baseline_original_source_fields_and_seal',checks=N,
               final_manifest=pin(mp),owned_entries=len(m['owned']),exact_external_original_assets=len(m['external_original_assets']),
               immutable_original_first_pin=pin(ip),all_original_pin_targets_unchanged=True,
               complete_original_receipts=len(receipts),source_native_rows=native,candidate_control_positions=50179,
               complete_embedded_original_page_JSONs=4,complete_rows_source_party_masks_positions=True,
               canonical_certified_priority_unavailable=True,protected_source_values_allocated=False,
               no_producer_import_or_write=True,
               qualification='Full original source fields only; historical formula and actual CLI repair regression reviews are separate. Superseded supplemental receipt-metadata gaps remain disclosed, not reconstructed into unknown retrieval history. No current/legal/geographic/feed/remaining/probability approval.')
    p=S/'data/coordinator-baseline-source-review.json'
    p.write_text(json.dumps(out,indent=2)+'\n')
    print(dict(checks=N,proof=pin(p)))


if __name__ == '__main__':
    main()

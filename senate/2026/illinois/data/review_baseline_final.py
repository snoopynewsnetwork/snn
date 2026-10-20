"""Independent sealed baseline/original raw-field and missing-cell review."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json

D=Path(__file__).resolve().parent
S=D.parent
B=D/'baselines'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b=p.read_bytes()
    assert len(b)<40_000_000
    return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))


def main():
    mfpath=B/'asset-manifest.json'
    assert sha(mfpath.read_bytes())=='ee08fe5358dd5e97a1667f191d0ac4d43c08fd329d3e62a26fb5bd57a3a0d30b'
    mf=json.loads(mfpath.read_bytes())
    owned={r['path'] for r in mf['owned_assets']}
    actual={str(p.relative_to(S)) for p in B.rglob('*') if p.is_file() and p.name!='asset-manifest.json'}
    actual|={'county-partisanship.md','data/county-baselines.csv'}
    assert owned==actual and len(actual)==248
    for r in mf['owned_assets']:
        assert pin(S/r['path'])==r
    for r in mf['source_references']:
        z=(B/r['path']).read_bytes();raw=gzip.decompress(z)
        assert len(z)==r['bytes']<40_000_000 and sha(z)==r['sha256']
        assert len(raw)==r['raw_bytes'] and sha(raw)==r['raw_sha256']
    sources=json.loads((D/'turnout/extract/source-pins.json').read_bytes())
    fields_checked=0
    raw_rows=0
    for y,sid,count in [(2020,'sos-observed-2020-senate-native-csv',54950),
                        (2022,'sos-observed-2022-senate-native-csv',31797),
                        (2024,'sos-2024-president-csv',59623)]:
        ref=sources[sid];z=(S/ref['path']).read_bytes();raw=gzip.decompress(z)
        assert sha(z)==ref['stored_sha256'] and sha(raw)==ref['raw_sha256']
        reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
        originals=list(reader)
        compared=list(csv.DictReader(io.StringIO(gzip.decompress((B/f'extract/{y}-raw-rows.csv.gz').read_bytes()).decode())))
        assert len(originals)==len(compared)==count
        for index,(a,b) in enumerate(zip(originals,compared),2):
            assert {k:b[k] for k in reader.fieldnames}==a
            assert b['year']==str(y) and b['source_id']==sid
            assert b['csv_record_1based_including_header']==str(index)
            fields_checked+=len(reader.fieldnames)
        raw_rows+=count
    original_groups=json.loads((D/'coordinator-printed-native-priority-review.json').read_bytes())['all_source_groups']
    own={(r['authority_ID'],r['literal_precinct']):r for r in original_groups}
    native=json.loads((B/'extract/2024-units.json').read_bytes())
    assert len(native)==len(own)==10062
    source_missing=source_zero=0
    for r in native:
        source=own[(r['JurisdictionID'],r['PrecinctName'])]
        c=source['printed_candidate_cells']
        assert r['A']==c['Kamala D. Harris'] and r['B']==c['Donald J. Trump']
        other=c['Robert F. Kennedy Jr.']
        # This explicitly documented field aggregates available other records;
        # its empty sum0 is distinct from an observed Kennedy candidate cell.
        assert r['printed_other_observed']==(other if other is not None else 0)
        assert set(r['printed_other_missing_candidates'])=={name for name,value in c.items() if value is None}
        for name,value in c.items():
            if value is None:
                assert name not in r['literal_category_record_sums']
            else:
                assert r['literal_category_record_sums'][name]==value
        assert r['source_positions']==source['original_CSV_positions']
        assert r['method']=='unavailable_no_source_column'
        source_missing+=r['A'] is None and r['B'] is None
        source_zero+=r['A']==0 and r['B']==0
    assert source_missing==4 and source_zero==745
    # Canonical null-last order is compared by explicit source fields, not names.
    contract=json.loads((B/'priority/contracts.json').read_bytes())['contracts']['native-2024-printed-observed']
    turn=json.loads((D/'turnout/priority-set.json').read_bytes())
    source_key={r['key']:(r['authority_id'],r['precinct_name_literal']) for r in turn['native_constituents']}
    decoded=[tuple(json.loads(k)[1:]) for k in contract['full_order']]
    assert decoded==[source_key[k] for k in turn['full_order']]
    assert [tuple(json.loads(k)[1:]) for k in contract['keys']]==[source_key[k] for k in turn['ordered_priority_keys']]
    out=dict(status='pass_independent_baseline_seal_original_fields_and_null_semantics',
             owned_seal=pin(mfpath),owned_assets=248,exact_complete_original_references=len(mf['source_references']),
             raw_records=raw_rows,literal_original_field_comparisons=fields_checked,
             source_known_native_contexts=len(native),observed_pair_zero_contexts=source_zero,
             unavailable_pair_contexts=source_missing,absent_Kennedy_fields=15,
             printed_other_available_record_aggregate_not_a_candidate_cell=True,
             canonical_full_order_and_priority_match=True,
             source_key_mapping='Turnout percent-encoded key and baseline JSON key each resolve to exact original authority ID/literal precinct tuple; this is source-position representation, not a geographic/current crosswalk.',
             paired_seals=[pin(D/'turnout/asset-manifest.json'),pin(mfpath)],
             geographic_approval=False,legal_native_writein_robustness=False,dispatch_acceptance=False)
    p=D/'coordinator-baseline-final-review.json';b=(json.dumps(out,indent=2)+'\n').encode();p.write_bytes(b)
    print(json.dumps(dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b),raw_fields=fields_checked)))


if __name__=='__main__':
    main()

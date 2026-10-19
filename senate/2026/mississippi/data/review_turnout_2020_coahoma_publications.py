"""Recompute the independent two-publication Coahoma comparison from frozen bodies."""
from pathlib import Path
import collections, csv, gzip, hashlib, io, json, struct

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
QA = DATA / 'coordinator-qa/turnout-2020-coahoma-two-publications'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(ROOT)), bytes=len(b), sha256=sha(b))

def freeze(p):
    q = QA / (p.name + '.gz')
    QA.mkdir(parents=True, exist_ok=True)
    if q.exists():
        b = gzip.decompress(q.read_bytes())
    else:
        b = p.read_bytes()
        q.write_bytes(gzip.compress(b, mtime=0))
        assert p.read_bytes() == b
    return b, dict(original=dict(path=str(p.relative_to(ROOT)), bytes=len(b), sha256=sha(b)), lossless_copy=pin(q))

def main():
    prior_path = DATA / 'coordinator-turnout-native-2020-fortyone-review.json'
    prior = json.loads(prior_path.read_bytes())
    assert not prior['formal_native887_dispatch_accepted']
    jb, jp = freeze(DATA / 'turnout/2020-coahoma-two-publication-native-original-readings.json')
    cb, cp = freeze(DATA / 'turnout/2020-coahoma-two-publication-native-original-cells.csv')
    rb, rp = freeze(DATA / 'turnout/2020-coahoma-two-publication-native-peer-reconciliation.json')
    own, rec = json.loads(jb), json.loads(rb)
    assert rec['own_original_reading_sha256'] == sha(jb) and rec['differences'] == []
    snap_path = ROOT / rec['peer_snapshot_path']
    snap_bytes = snap_path.read_bytes()
    assert sha(snap_bytes) == rec['peer_snapshot_sha256'] == '1ff6e98fd18f70ec473ce0b5adac5e082f4f1900a7d03d6090e9181150a71568'
    witness = json.loads(snap_bytes)
    entry = next(p for p in witness['pins'] if p['original_path'] == rec['peer_original_path'])
    stored_path = ROOT / entry['stored_path']
    stored = stored_path.read_bytes()
    peer_bytes = gzip.decompress(stored)
    assert sha(stored) == entry['stored_sha256'] == rec['peer_stored_sha256']
    assert len(stored) == entry['stored_bytes']
    assert sha(peer_bytes) == entry['original_sha256'] == rec['peer_original_sha256']
    assert len(peer_bytes) == entry['original_bytes']
    peer_sources = {s['source_id']: s for s in json.loads(peer_bytes)['sources']}
    flat = list(csv.DictReader(io.StringIO(cb.decode())))
    flat_index = {(r['source_id'], int(r['source_pdf_page']), int(r['physical_source_column']), r['candidate']): r for r in flat}
    assert len(flat_index) == len(flat) == own['total_candidate_positions'] == 132
    old_sources = {s['source_id'] for s in prior['source_findings']}
    counts, findings, rasters, seen = collections.Counter(), [], [], set()
    for s in own['sources']:
        sid = s['source_id']
        assert sid not in old_sources and sid in peer_sources
        peer = peer_sources[sid]
        raw_path = ROOT / s['source_original_path']
        raw = gzip.decompress(raw_path.read_bytes())
        assert raw.startswith(b'%PDF-') and sha(raw) == s['source_raw_sha256'] == peer['raw_sha256']
        peer_fields = {}
        for p in peer['pages']:
            for f in p['fields']:
                for col, value in zip(p['columns'], f['values']):
                    peer_fields[p['page'], col['source_column'], f['candidate']] = col, value
        for p in s['pages']:
            image_path = ROOT / p['original_raster']
            image = image_path.read_bytes()
            assert sha(image) == p['raster_sha256']
            assert image.startswith(b'\x89PNG\r\n\x1a\n')
            assert list(struct.unpack('>II', image[16:24])) == p['render_size']
            rasters.append(pin(image_path))
        sums, totals, units = collections.Counter(), {}, {}
        for row in s['rows']:
            key = sid, row['source_pdf_page'], row['physical_source_column'], row['candidate']
            assert key not in seen
            seen.add(key)
            f = flat_index[key]
            col, value = peer_fields[key[1:]]
            assert row['votes'] == value and row['role'] == col['role']
            assert ' '.join(row['literal_source_header'].split()) == ' '.join(col['label_literal'].split())
            for field in ['source_id', 'county_fips', 'source_raw_sha256', 'literal_source_header', 'role', 'candidate', 'reading_basis', 'original_raster']:
                assert f[field] == row[field]
            assert row['source_raw_sha256'] == s['source_raw_sha256'] and row['county_fips'] == peer['county_fips']
            assert (None if f['votes'] == '' else int(f['votes'])) == row['votes']
            units[key[1:3]] = row['role']
            if row['role'] == 'unused_template_column':
                assert value is None
                counts['unused_null_positions'] += 1
            else:
                assert type(value) is int and value >= 0
                counts['numeric_positions'] += 1
                if row['role'] == 'source_native_reporting_constituent':
                    sums[row['candidate']] += value
                else:
                    assert row['role'] == 'source_TOTAL'
                    assert key[1:3] == (3, 8) and row['candidate'] not in totals
                    totals[row['candidate']] = value
        assert sum(v == 'source_native_reporting_constituent' for v in units.values()) == s['native_constituents'] == 18
        assert sum(v == 'source_TOTAL' for v in units.values()) == 1
        assert sum(v == 'unused_template_column' for v in units.values()) == 3
        assert dict(sums) == totals == {n: c['printed_TOTAL'] for n, c in s['candidate_checks'].items()}
        assert totals == {c['candidate']: c['printed_TOTAL'] for c in peer['checks']}
        assert all(c['native_sum'] == c['printed_TOTAL'] == c['county_control'] and c['passes'] for c in s['candidate_checks'].values())
        findings.append(dict(source_id=sid, raw_original=pin(raw_path), raw_PDF_sha256=sha(raw), native_constituents=18, TOTAL=dict(page=3, physical_column=8), source_candidate_sums_and_TOTAL=totals))
    assert len(seen) == len(flat) == rec['compared_candidate_positions'] == 132
    counts.update(publication_views=2, native_constituents=36, TOTAL_columns=2, unused_columns=6, source_positions=132, selected82_publications=1, selected82_native_constituents=18)
    cumulative = collections.Counter(prior['counts'])
    cumulative.update(counts)
    out = dict(status='pass_bounded_independent_two_publication_original2020_native_comparison', prior_immutable_review=pin(prior_path), frozen_turnout_inputs=[jp, cp, rp], immutable_peer_snapshot=pin(snap_path), immutable_peer_readings=entry, counts=dict(cumulative), new_counts=dict(counts), source_findings=prior['source_findings'] + findings, original_worker_raster_pins=rasters, qualification='Two distinct original publications remain nonadditive alternatives. The 132 source positions recompute from losslessly frozen independent transcripts against immutable104 readings. Exact raw hash/page/physical column/value/role/whitespace-folded literal headers agree. Original raster hashes survive separately; no common raster, numeric polygon, current ID, source chronology or all-historical-method approval is asserted. This is not a fresh coordinator glyph reading of all fields.', formal_native887_dispatch_accepted=False, historical_native_complete=False, current_geography_approved=False)
    p = DATA / 'coordinator-turnout-native-2020-fortythree-review.json'
    body = (json.dumps(out, indent=2) + '\n').encode()
    if p.exists():
        assert p.read_bytes() == body
    else:
        p.write_bytes(body)
    print(json.dumps(dict(output=pin(p), counts=dict(cumulative), new_counts=dict(counts))))

if __name__ == '__main__':
    main()

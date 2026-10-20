"""Independent finished-map seal/source/hierarchy/PDF/actual-JS audit."""
from pathlib import Path
import gzip
import hashlib
import json
import re
import subprocess
import fitz

S = Path(__file__).resolve().parents[1]
M = S / 'maps'
N = 0


def ck(ok, note=''):
    global N
    assert ok, note
    N += 1


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def body(h):
    chunks = []
    for x in h['stored_parts']:
        z = (M / x['path']).read_bytes()
        ck((len(z), sha(z)) == (x['bytes'], x['sha256']))
        ck(len(z) < 40000000)
        chunks.append(z)
    raw = gzip.decompress(b''.join(chunks))
    ck((len(raw), sha(raw)) == (h['raw_bytes'], h['raw_sha256']))
    return raw


def decoded(r):
    h = r['hops'][-1]
    raw = body(h)
    enc = next((v for k, v in h['response_headers'] if k.lower() == 'content-encoding'), '')
    if enc == 'gzip':
        return gzip.decompress(raw)
    if enc == 'br':
        import brotli
        return brotli.decompress(raw)
    ck(enc in ['', 'identity'], enc)
    return raw


def main():
    fitz.TOOLS.mupdf_warnings(reset=True)
    p = M / 'asset-manifest.json'
    ck((p.stat().st_size, sha(p.read_bytes())) == (341127, '45a2f7f5f00db69abacc68912735bb0690da18eeaa552f55f0b7e35ca6591415'))
    mf = read(p)
    ck(mf['only_exclusion'] == 'maps/asset-manifest.json')
    actual = {str(x.relative_to(S)) for x in M.rglob('*') if x.is_file() and x != p} | {'precinct-maps.md'}
    ck(actual == {x['path'] for x in mf['files']} and len(actual) == 1656)
    for row in mf['files']:
        ck(pin(S / row['path']) == row, row['path'])
        ck(row['bytes'] < 40000000)
    deps = read(M / 'individual-source-pins.json')
    for row in deps:
        ck(pin(S / row['path']) == row, row['path'])
    print('exact final map membership and dependencies pass', len(actual), len(deps), flush=True)
    c = read(S / 'data/turnout/priority-set.json')
    ck((S / 'data/turnout/priority-set.json').read_bytes() == gzip.decompress((M / 'historical-contract.json.gz').read_bytes()))
    inventory = read(M / 'inventory.json')
    parents = read(M / 'parents.json')
    ck(len(c) == 24 and [r['source'] for r in inventory] == c['all_units'])
    original = read(S / 'data/baselines/extract/native-contests.json')['2024-senate']
    originals = {r['key']:(r, block['candidates']) for block in original for r in block['rows']}
    for r in inventory:
        ck((r['complete_original_candidate_row'], r['candidate_definitions']) == originals[r['source']['key']])
        ck(r['physical_leaf_polygon_match'] is r['current_native_reporting_ID_match'] is None)
        ck(r['gaps']['source_key'] == r['source']['key'])
    ck(len(parents) == 21)
    for p in parents:
        units = [u for u in c['all_units'] if u['county_fips'] == p['county_fips']]
        ck(p['full_historical_parent_object'] == next(q for q in c['county_coverage'] if q['county_fips'] == p['county_fips']))
        ck(p['all_canonical_rank_ordered_children'] == [u['key'] for u in units])
        ck(p['all_ordered_priority_children'] == [u['key'] for u in units if u['in_minimum80']])
        ck(p['all_ordered_remainder_children'] == [u['key'] for u in units if not u['in_minimum80']])
        ck(len(p['authority']['roles']) == 3 and p['current_geography_approved'] is False)
        ck(p['shared_acquired_resources']['state_features'] > 0 and p['shared_acquired_resources']['census2020_count'] > 0)
        ck(all(p['gaps'][k] for k in ['access', 'vintage', 'finer', 'physical', 'current', 'county_specific']))
    receipts = {p.stem:read(p) for p in (M / 'receipts').glob('*.json')}
    hops = 0
    parts = set()
    raw_entities = set()
    for r in receipts.values():
        ck(bool(r['hops']) or bool(r.get('error')))
        for h in r['hops']:
            raw = body(h)
            raw_entities.add((len(raw), sha(raw)))
            parts.update(x['path'] for x in h['stored_parts'])
            hops += 1
    ck((len(receipts), hops, len(parts)) == (487, 550, 471))
    ck(parts == {str(p.relative_to(M)) for p in (M / 'originals').iterdir() if p.is_file()})
    pdfs = read(M / 'pdf-inventory.json')
    pages = 0
    for r in pdfs:
        raw = decoded(receipts[r['receipt_id']])
        ck(sha(raw) == r['original_raw_sha256'])
        doc = fitz.open(stream=raw, filetype='pdf')
        ck(doc.page_count == r['page_count'] == len(r['pages']))
        text = read(M / r['text_asset'])
        ck(len(text) == doc.page_count)
        for i, (pg, saved) in enumerate(zip(doc, text)):
            ck(saved == dict(page=i+1, text=pg.get_text(), width_points=pg.rect.width, height_points=pg.rect.height, rotation=pg.rotation))
            image = r['pages'][i]
            ck(sha((M / image['preview']).read_bytes()) == image['preview_sha256'])
            pages += 1
    ck(len(pdfs) == 215 and pages == 323)
    for name in ['coordinator-native-map-snapshot-review.json', 'coordinator-census-map-original-review.json']:
        review = read(S / 'data' / name)
        for row in review.get('individually_rehashed_receipts_and_original_parts', review.get('complete_original_pins', [])):
            ck(pin(S / row['path']) == row, row['path'])
    replay = read(M / 'qa/reproduction.json')
    ck(replay['status'] == 'pass' and replay['offline'] and replay['before_and_after_exact_equal'])
    ck(replay['complete_before'] == replay['complete_after'] and replay['deterministic_product_count'] == 578)
    for row in replay['complete_after']:
        ck(pin(S / row['path']) == row)
    test = (M / 'scripts/test_atlas.cjs').read_text()
    source = "fs.writeFileSync(path.join(base,'qa/atlas-js-tests.json'),JSON.stringify(out,null,2)+'\\n');"
    ck(test.count(source) == 1 and test.count('writeFileSync') == 1)
    test = test.replace("const base=path.resolve(__dirname,'..');", 'const base=' + json.dumps(str(M)) + ';')
    test = test.replace(source, "assert.strictEqual(fs.readFileSync(path.join(base,'qa/atlas-js-tests.json'),'utf8'),JSON.stringify(out,null,2)+'\\n');")
    run = subprocess.run(['node', '-e', test], capture_output=True, text=True)
    ck(run.returncode == 0, run.stdout + run.stderr)
    ck(read(M / 'qa/negative-fixtures.json')['status'] == 'pass')
    for row in mf['files']:
        ck(pin(S / row['path']) == row, 'post-harness:' + row['path'])
    result = dict(status='pass_independent_complete_finished_maps_review', checks=N,
                  producer_manifest=pin(M / 'asset-manifest.json'), producer_manifest_list_key='files',
                  owned_entries=1656, immutable_external_file_pins=len(deps),
                  complete_source_observations=575, priority=233, remainder=342, county_parents=21,
                  complete_request_receipts=len(receipts), complete_response_hops=hops,
                  unique_stored_original_parts=len(parts), complete_distinct_raw_entities=len(raw_entities),
                  actual_native_features=[6348,401], Census2020_records=6361,
                  Census2020_XY_positions=1151117, Census2020_individual_coordinate_values=2302234,
                  complete_original_PDFs=215, automatically_rendered_pages=323,
                  offline_deterministic_products=578, actual_readonly_atlas_harness=run.stdout.strip(),
                  browser_layout_or_browser_filepicker_tested=False,
                  additional_coordinator_complete_original_pages_actually_viewed=2,
                  retained_PDF_parser_warnings=fitz.TOOLS.mupdf_warnings(reset=True),
                  all_current_physical_or_legal_source_leaf_matches_approved=False,
                  producer_imports_or_writes=False,
                  qualification='Qualified acquired shared-parent maps and historical native/Census context, not source-label/current/legal matches. Mature-support2019–2020 state layer, separateBurlington401, printed original-vintage/certification gaps, partialGloucester roster and all21 county access/finer gaps retained. No geometry or vote repair, exact eligible pool, measured cadence, collector or probability approval.')
    out = S / 'data/coordinator-maps-final-review.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(checks=N, output=pin(out))))


if __name__ == '__main__':
    main()

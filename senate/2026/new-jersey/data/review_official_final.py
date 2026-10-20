"""Coordinator exact sealed-source/raw-schema review; no producer imports/writes."""
from pathlib import Path
from collections import Counter
from xml.etree import ElementTree as ET
import csv
import gzip
import hashlib
import io
import json
import fitz

S = Path(__file__).resolve().parents[1]
H = S / 'data/results-sources'
N = 0


def ck(v, note=''):
    global N
    assert v, note
    N += 1


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def raw_hop(h):
    if 'ordered_exact_entity_parts' in h:
        raw = b''.join(raw_hop(p) for p in h['ordered_exact_entity_parts'])
    else:
        path = S / h['reference_path'] if 'reference_path' in h else H / h['asset']
        z = path.read_bytes()
        ck(len(z) == h['stored_bytes'] < 40000000 and sha(z) == h['stored_sha256'])
        raw = gzip.decompress(z) if h.get('reference_gzip', True) else z
    ck(len(raw) == h['raw_bytes'] and sha(raw) == h['raw_sha256'])
    return raw


def schema(v, pointer=''):
    yield dict(pointer=pointer, type=type(v).__name__, length=len(v) if isinstance(v,(list,dict,str)) else None, null=v is None)
    if isinstance(v, dict):
        for k, value in v.items():
            yield from schema(value, pointer+'/'+k.replace('~','~0').replace('/','~1'))
    elif isinstance(v, list):
        for i, value in enumerate(v):
            yield from schema(value, pointer+'/'+str(i))


def tree(e):
    return dict(tag=e.tag, attributes=dict(e.attrib), text=e.text, tail=e.tail, children=[tree(c) for c in e])


def main():
    mf_path = H / 'asset-manifest.json'
    ck((mf_path.stat().st_size,sha(mf_path.read_bytes())) == (316761,'29867cc7daa719799f00f71736872ef9ed54c8394bbdccc307f2ed8d998f2da5'))
    mf = read(mf_path)
    ck(mf['excludes_only'] == 'data/results-sources/asset-manifest.json')
    actual = {str(p.relative_to(S)) for p in H.rglob('*') if p.is_file() and p != mf_path}
    actual |= {'official-results.md','data/official-results-sources.csv'}
    ck(actual == {r['path'] for r in mf['files']} and len(actual) == 1443)
    for r in mf['files']:
        ck(pin(S / r['path']) == r, r['path'])
        ck(r['bytes'] < 40000000 and '__pycache__' not in Path(r['path']).parts)
    deps = read(H / 'individual-source-pins.json')
    for r in deps:
        ck(pin(S / r['path']) == {k:r[k] for k in ['path','bytes','sha256']},r['path'])
    print('exact 1443-body seal and all dependency pins pass',len(deps),flush=True)
    c = read(S / 'data/turnout/priority-set.json')
    units = read(H / 'all575-investigations.json.gz')
    parents = read(H / 'county-investigations.json.gz')
    ck(len(units) == 575 and len(parents) == 21)
    ck([r['historical_complete_unit'] for r in units] == c['all_units'])
    ck([r['key'] for r in units] == c['complete_ordered_keys'])
    original = read(S / 'data/baselines/extract/native-contests.json')['2024-senate']
    contexts = {r['key']:dict(original_complete_row=r,full_candidates=p['candidates'],all_page_headers=p['headers'],column_right_edges=p['column_right_edges'],nonadditive_footer=p['footer']) for p in original for r in p['rows']}
    for u in units:
        ck(u['historical_complete_candidate_publication_context'] == contexts[u['key']])
        ck(u['current_leaf_reporting_ID'] is u['current_candidate_choice_IDs'] is u['current_unit_method_crosswalk'] is None)
        ck(u['genuine_November_counts_admitted'] is False)
    for name, expected in [('priority233-investigations.json.gz',units[:233]),('remainder342-investigations.json.gz',units[233:])]:
        rows = read(H / name)
        ck(len(rows) == len(expected))
        for r,u in zip(rows,expected):
            ck({k:v for k,v in r.items() if k != 'complete_shared_parent_investigation'} == u)
            ck(r['complete_shared_parent_investigation'] == next(p for p in parents if p['parent_key'] == u['shared_parent_key']))
    for p in parents:
        keys = [u['key'] for u in units if u['shared_parent_key'] == p['parent_key']]
        ck(p['rank_ordered_children'] == keys)
        ck(p['priority_children'] == [u['key'] for u in units[:233] if u['shared_parent_key'] == p['parent_key']])
        ck(p['remainder_children'] == [u['key'] for u in units[233:] if u['shared_parent_key'] == p['parent_key']])
        ck(p['historical_complete_parent'] == next(r for r in c['county_coverage'] if r['county_fips'] == p['parent_key']))
        ck(len(p['authority_directory']['roles']) == 3 and bool(p['actual_bounded_public_requests']))
        ck(p['measured_candidate_publication_cadence'] is p['November_accepted_unprocessed_eligible_pool'] is None)
        ck(p['current_choice_reporting_or_leaf_match_approved'] is p['genuine_November_counts_admitted'] is False)
    with (S / 'data/official-results-sources.csv').open(newline='') as f:
        csvrows = list(csv.DictReader(f))
    ck(len(csvrows) == 86 and Counter(r['county_fips'] for r in csvrows if r['county_fips']) == {p['parent_key']:4 for p in parents})
    receipts = {}
    entities = {}
    hops = failures = 0
    for p in sorted((H / 'requests').glob('*.json')):
        r = read(p)
        receipts[r['id']] = r
        ck(r['id'] == p.stem and r['admission'] == 'research_only_not_admitted_November_counts')
        failures += not bool(r['hops'])
        for h in r['hops']:
            hops += 1
            ck(h['method'] == 'GET' and h['request_body'] is None and bool(h['actual_requested_url']))
            ck('headers' in h and 'request_headers' in h)
            if h.get('raw_sha256') not in entities:
                raw = raw_hop(h)
                entities[sha(raw)] = len(raw)
    ck((len(receipts),hops,failures,len(entities)) == (485,523,9,415))
    print('every complete source/redirect entity reconstructed',len(entities),flush=True)
    directory_receipt = receipts['state-directory-public']
    directory_raw = raw_hop(directory_receipt['hops'][-1]).decode('utf-8','replace')
    authorities = read(H / 'authorities.json')
    ck(len(authorities) == 21)
    for p in authorities:
        for role in p['roles']:
            ck(role['raw_column_html'] in directory_raw)
            ck(role['blank_name'] == (role['name_literal'] is None))
            ck(role['blank_email'] == (not role['email_tokens']) and role['blank_link'] == (not role['links']))
    formats = Counter()
    schema_fields = pdf_pages = csv_cells = 0
    done = set()
    for r in read(H / 'structure-index.json'):
        if not r['structure_asset'] or r['raw_sha256'] in done:
            continue
        done.add(r['raw_sha256'])
        raw = raw_hop(receipts[r['request_id']]['hops'][-1])
        ck(sha(raw) == r['raw_sha256'])
        z = read(H / r['structure_asset'])
        kind = r['kind']
        formats[kind] += 1
        if kind == 'JSON_complete_recursive_schema':
            expected = list(schema(json.loads(raw)))
            ck(z['schema'] == expected)
            schema_fields += len(expected)
        elif kind == 'CSV_all_rows_all_fields':
            rows = list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
            ck(z['all_rows'] == rows and z['row_lengths'] == list(map(len,rows)))
            csv_cells += sum(map(len,rows))
        elif kind == 'XML_complete_recursive_tree':
            ck(z == tree(ET.fromstring(raw)))
        elif kind == 'PDF_all_pages':
            pdf = fitz.open(stream=raw,filetype='pdf')
            ck(z['page_count'] == len(pdf) == len(z['pages']))
            for pg,saved in zip(pdf,z['pages']):
                ck(saved['rectangle'] == list(pg.rect) and saved['rotation'] == pg.rotation)
                ck(saved['text'] == pg.get_text())
                ck(saved['words'] == [list(w) for w in pg.get_text('words')])
                pdf_pages += 1
    assessments = read(H / 'payload-assessments.json')
    ck(len(assessments) == 12 and sum('2026-06-02 primary' in x['stage_assessment'] for x in assessments) == 11)
    for a in assessments:
        ck(a['genuine_November_counts_admitted'] is False)
        ck(a['measured_publication_cadence'] is a['exact_eligible_remaining_pool'] is None)
    general = next(a for a in assessments if 'November3' in a['stage_assessment'])
    ck(all(not any(r.get('V',[])) for r in general['full_Senate_contest_objects_preview']))
    ck(read(H / 'reproduction.json')['network_run'] is False)
    ck(read(H / 'historical-reconstruction.json')['recursive_objects'] == 724943)
    ck(read(H / 'validation.json')['status'] == 'pass_complete_owned_source_research')
    for r in read(H / 'final-seal.json')['stable_core']:
        ck(pin(S / r['path']) == r)
    out = dict(status='pass_independent_complete_official_seal_source_and_schema_review',checks=N,
               producer_manifest=pin(mf_path),owned_entries=1443,individual_immutable_dependency_pins=len(deps),
               all_complete_source_units=575,priority=233,remainder=342,county_parents=21,authority_rows=86,
               complete_request_observations=485,complete_response_hops=523,client_failures=9,
               complete_distinct_original_entities=415,complete_entity_raw_bytes=sum(entities.values()),
               unique_complete_structure_counts=dict(formats),complete_JSON_schema_fields=schema_fields,
               independent_PDF_pages_text_and_words=pdf_pages,complete_CSV_cells=csv_cells,
               primary_Clarity_payload_sets=11,General_Clarity_zero_template_sets=1,
               earlier_independent_full_historical_graph=pin(S / 'data/coordinator-acceptance-validation.json'),
               full_worker_historical_replay=pin(H / 'historical-reconstruction.json'),
               original_publication_continuity=pin(H / 'original-page-replay.json'),
               no_producer_import_or_write=True,all_current_returns_leaf_joins_or_live_assumptions_approved=False,
               qualification='All21 complete authority/shared-parent investigations and575 complete historical objects preserved. Primary payloads, General zero templates, later law/roster/docket qualifications, nonadditive finer views, all source discrepancies and unallocated/unknown writeins remain distinct. No genuineNovember votes, measured cadence, eligible outstanding pool or current geometry/choice approval.')
    p = S / 'data/coordinator-official-final-review.json'
    p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(checks=N,proof=pin(p))))


if __name__ == '__main__':
    main()
